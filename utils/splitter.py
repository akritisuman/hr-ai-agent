"""
Text Splitting Utilities for Chunking Documents
Optimized for CV/resume processing
"""

from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
import logging

logger = logging.getLogger(__name__)


class CVTextSplitter:
    """
    Specialized text splitter for CV/resume documents
    Optimized chunk sizes for embedding and semantic search
    """
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: List[str] = None
    ):
        """
        Initialize CV text splitter
        
        Args:
            chunk_size: Maximum size of each chunk
            chunk_overlap: Overlap between chunks for context preservation
            separators: List of separators to use for splitting
        """
        if separators is None:
            separators = ["\n\n", "\n", ". ", " ", ""]
        
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators,
            length_function=len
        )
    
    def split_text(self, text: str) -> List[str]:
        """
        Split text into chunks
        
        Args:
            text: Input text to split
            
        Returns:
            List of text chunks
        """
        if not text or not text.strip():
            logger.warning("Empty text provided to splitter")
            return []
        
        chunks = self.splitter.split_text(text)
        logger.info(f"Split text into {len(chunks)} chunks")
        return chunks
    
    def split_documents(self, documents: List[str]) -> List[List[str]]:
        """
        Split multiple documents into chunks
        
        Args:
            documents: List of document texts
            
        Returns:
            List of lists, where each inner list contains chunks for one document
        """
        return [self.split_text(doc) for doc in documents if doc]







