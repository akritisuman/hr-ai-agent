"""
Document Ingestion Pipeline
Handles document loading, chunking, and embedding generation
"""

import os
from typing import List, Dict, Optional
from pathlib import Path
import logging

from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone, ServerlessSpec
from utils.loaders import DocumentLoader
from utils.splitter import CVTextSplitter

logger = logging.getLogger(__name__)


class IngestionPipeline:
    """
    Complete ingestion pipeline for CVs and Job Descriptions
    Handles embedding generation and Pinecone storage
    """
    
    def __init__(
        self,
        pinecone_api_key: str,
        pinecone_index_name: str,
        openai_api_key: str,
        environment: str = "us-east-1"
    ):
        """
        Initialize ingestion pipeline
        
        Args:
            pinecone_api_key: Pinecone API key
            pinecone_index_name: Name of Pinecone index
            openai_api_key: OpenAI API key for embeddings
            environment: Pinecone environment/region
        """
        # Initialize OpenAI embeddings with text-embedding-3-small (1536 dimensions)
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=openai_api_key,
            model="text-embedding-3-small"
        )
        self.embedding_dimension = 1536
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=pinecone_api_key)
        self.index_name = pinecone_index_name
        
        # Get or create index with dimension 1536
        index_dimension = self._ensure_index_exists(environment)
        self.index = self.pc.Index(self.index_name)
        
        # Verify dimension matches
        if index_dimension != 1536:
            logger.error(
                f"Pinecone index dimension mismatch! Index has {index_dimension} dimensions, "
                f"but embeddings use 1536 dimensions. Please recreate the index with dimension 1536."
            )
            raise ValueError(
                f"Index dimension ({index_dimension}) does not match embedding dimension (1536). "
                f"Please delete and recreate the index with dimension 1536."
            )
        
        # Initialize text splitter
        self.splitter = CVTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        logger.info(
            f"✅ Initialized ingestion pipeline - Index: {pinecone_index_name}, "
            f"Model: text-embedding-3-small, Dimension: {index_dimension}"
        )
    
    def _ensure_index_exists(self, environment: str) -> int:
        """
        Ensure Pinecone index exists, create if not
        
        Returns:
            Index dimension (always 1536)
        """
        existing_indexes = [idx.name for idx in self.pc.list_indexes()]
        
        if self.index_name not in existing_indexes:
            # Create new index with dimension 1536 for text-embedding-3-small
            dimension = 1536
            logger.info(f"Creating new Pinecone index: {self.index_name} with dimension {dimension}")
            self.pc.create_index(
                name=self.index_name,
                dimension=dimension,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region=environment
                )
            )
            logger.info(f"✅ Created Pinecone index '{self.index_name}' with dimension {dimension}")
            return dimension
        else:
            # Get existing index dimension
            index_info = self.pc.describe_index(self.index_name)
            dimension = index_info.dimension
            logger.info(f"✅ Using existing Pinecone index '{self.index_name}' with dimension {dimension}")
            return dimension
    
    def ingest_job_description(self, jd_text: str, session_id: str) -> str:
        """
        Ingest job description into vector database
        
        Args:
            jd_text: Job description text
            session_id: Session identifier for isolation
            
        Returns:
            Vector ID for the JD
        """
        # Split JD into chunks
        chunks = self.splitter.split_text(jd_text)
        
        # Generate embeddings (text-embedding-3-small produces 1536 dimensions)
        embeddings_list = self.embeddings.embed_documents(chunks)
        
        # Store in Pinecone
        vectors = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings_list)):
            vector_id = f"jd_{session_id}_{i}"
            vectors.append({
                "id": vector_id,
                "values": embedding,
                "metadata": {
                    "type": "job_description",
                    "session_id": session_id,
                    "chunk_index": i,
                    "text": chunk[:500]  # Store first 500 chars for reference
                }
            })
        
        # Upsert in batch
        self.index.upsert(vectors=vectors)
        logger.info(f"Ingested JD with {len(vectors)} chunks for session {session_id}")
        
        return f"jd_{session_id}"
    
    def ingest_cvs(
        self,
        cv_data: Dict[str, str],
        session_id: str
    ) -> Dict[str, List[str]]:
        """
        Ingest multiple CVs into vector database
        
        Args:
            cv_data: Dict mapping file_path -> extracted_text
            session_id: Session identifier for isolation
            
        Returns:
            Dict mapping file_path -> list of vector IDs
        """
        all_vectors = []
        cv_vector_ids = {}
        
        for file_path, text in cv_data.items():
            if text is None:
                continue
            
            # Extract candidate name from filename or text
            candidate_name = self._extract_candidate_name(file_path, text)
            
            # Split CV into chunks
            chunks = self.splitter.split_text(text)
            
            # Generate embeddings (text-embedding-3-small produces 1536 dimensions)
            embeddings_list = self.embeddings.embed_documents(chunks)
            
            # Prepare vectors
            vector_ids = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings_list)):
                vector_id = f"cv_{session_id}_{Path(file_path).stem}_{i}"
                vector_ids.append(vector_id)
                
                all_vectors.append({
                    "id": vector_id,
                    "values": embedding,
                    "metadata": {
                        "type": "cv",
                        "session_id": session_id,
                        "file_path": file_path,
                        "candidate_name": candidate_name,
                        "chunk_index": i,
                        "text": chunk[:500]  # Store first 500 chars for reference
                    }
                })
            
            cv_vector_ids[file_path] = vector_ids
        
        # Batch upsert all vectors
        if all_vectors:
            # Pinecone supports up to 100 vectors per upsert
            batch_size = 100
            for i in range(0, len(all_vectors), batch_size):
                batch = all_vectors[i:i + batch_size]
                self.index.upsert(vectors=batch)
            
            logger.info(f"Ingested {len(cv_data)} CVs with {len(all_vectors)} total chunks")
        
        return cv_vector_ids
    
    def _extract_candidate_name(self, file_path: str, text: str) -> str:
        """
        Extract candidate name from file path or text
        
        Args:
            file_path: Path to CV file
            text: CV text content
            
        Returns:
            Candidate name
        """
        # Try to extract from filename first
        filename = Path(file_path).stem
        # Remove common prefixes/suffixes
        name = filename.replace("_", " ").replace("-", " ").title()
        
        # If filename looks like a name, use it
        if len(name.split()) <= 3 and name.replace(" ", "").isalpha():
            return name
        
        # Otherwise, try to extract from text (first line or common patterns)
        lines = text.split("\n")[:5]
        for line in lines:
            line = line.strip()
            if line and len(line.split()) <= 3:
                # Check if it looks like a name
                if all(word.replace(".", "").isalpha() for word in line.split()):
                    return line
        
        # Fallback to filename
        return filename
    
    def get_jd_embeddings(self, session_id: str) -> List[List[float]]:
        """
        Retrieve JD embeddings for a session
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of embedding vectors
        """
        # Query all JD vectors for this session (using 1536-dim dummy vector)
        results = self.index.query(
            vector=[0.0] * 1536,  # Dummy vector for metadata filter
            filter={"session_id": {"$eq": session_id}, "type": {"$eq": "job_description"}},
            top_k=100,
            include_metadata=True
        )
        
        # Extract embeddings (would need to fetch by ID)
        # For now, return empty - embeddings are stored, not retrieved this way
        return []
    
    def cleanup_session_vectors(self, session_id: str):
        """
        Clean up all vectors for a session
        
        Args:
            session_id: Session identifier
        """
        # Delete all vectors for this session
        # Note: Pinecone delete by metadata filter requires delete_all with filter
        try:
            self.index.delete(
                filter={
                    "session_id": {"$eq": session_id}
                }
            )
            logger.info(f"Cleaned up vectors for session: {session_id}")
        except Exception as e:
            logger.error(f"Error cleaning up vectors for session {session_id}: {str(e)}")

