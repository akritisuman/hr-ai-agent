"""
FastAPI Backend for HR AI Agent
Handles CV ranking requests and orchestration
"""

import os
import logging
from typing import List, Optional
from pathlib import Path
import tempfile
import shutil
from dotenv import load_dotenv

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Load environment variables
load_dotenv()

from utils.loaders import DocumentLoader
from utils.security import SessionManager, SecurityValidator
from ingestion import IngestionPipeline
from agent import CVAnalysisAgent
from ranking import RankingEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="HR AI Agent API",
    description="Production-ready HR Operations AI Agent for CV Ranking",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
session_manager = SessionManager()
document_loader = DocumentLoader()

# These will be initialized on startup
ingestion_pipeline = None
analysis_agent = None
ranking_engine = None


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global ingestion_pipeline, analysis_agent, ranking_engine
    
    # Get API keys from environment
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    pinecone_index_name = os.getenv("PINECONE_INDEX_NAME", "hr-agent-cvs")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    pinecone_environment = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
    
    # Ensure index name is hr-agent-cvs
    if pinecone_index_name != "hr-agent-cvs":
        logger.warning(f"Index name is '{pinecone_index_name}', expected 'hr-agent-cvs'. Using configured name.")
    
    if not pinecone_api_key or not openai_api_key:
        logger.warning("API keys not found. Some features may not work.")
        return
    
    try:
        # Initialize ingestion pipeline
        ingestion_pipeline = IngestionPipeline(
            pinecone_api_key=pinecone_api_key,
            pinecone_index_name=pinecone_index_name,
            openai_api_key=openai_api_key,
            environment=pinecone_environment
        )
        
        # Log index dimension for verification
        index_info = ingestion_pipeline.pc.describe_index(pinecone_index_name)
        logger.info(f"📊 Pinecone Index Dimension: {index_info.dimension} (Expected: 1536)")
        if index_info.dimension != 1536:
            logger.error(
                f"❌ CRITICAL: Index dimension is {index_info.dimension}, but embeddings use 1536. "
                f"Please recreate the index with dimension 1536."
            )
        else:
            logger.info("✅ Pinecone index dimension verified: 1536")
        
        # Initialize analysis agent
        analysis_agent = CVAnalysisAgent(openai_api_key=openai_api_key)
        
        # Initialize ranking engine
        ranking_engine = RankingEngine(agent_analyzer=analysis_agent)
        
        logger.info("✅ All services initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing services: {str(e)}")


class RankingResponse(BaseModel):
    """Response model for ranking results"""
    session_id: str
    top_candidates: List[dict]
    total_candidates: int
    processing_time_seconds: float


@app.post("/rank-cvs", response_model=RankingResponse)
async def rank_cvs(
    job_description: str = Form(...),
    files: List[UploadFile] = File(...),
    top_n: int = Form(3)
):
    """
    Rank CVs against Job Description
    
    Args:
        job_description: Job description text
        files: List of uploaded CV files (PDF, DOC, DOCX)
        top_n: Number of top candidates to return (default: 3)
    
    Returns:
        RankingResponse with top candidates and scores
    """
    import time
    start_time = time.time()
    
    # Validate inputs
    if not job_description or not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description is required")
    
    if not files or len(files) < 1:
        raise HTTPException(status_code=400, detail="At least one CV file is required")
    
    if len(files) > 50:  # Reasonable limit
        raise HTTPException(status_code=400, detail="Maximum 50 CVs allowed per request")
    
    # Create session
    session_id = session_manager.create_session()
    
    try:
        # Validate and save files
        cv_file_paths = []
        for file in files:
            # Validate file
            is_valid, error_msg = SecurityValidator.validate_file(
                file.filename,
                file.size
            )
            if not is_valid:
                raise HTTPException(status_code=400, detail=f"Invalid file {file.filename}: {error_msg}")
            
            # Read file content
            file_content = await file.read()
            
            # Save to session directory
            file_path = session_manager.save_file(session_id, file.filename, file_content)
            cv_file_paths.append(str(file_path))
        
        logger.info(f"Processing {len(cv_file_paths)} CVs for session {session_id}")
        
        # Load documents
        cv_data = document_loader.batch_load_documents(cv_file_paths)
        
        # Filter out failed loads
        cv_data = {k: v for k, v in cv_data.items() if v is not None}
        
        if not cv_data:
            raise HTTPException(status_code=500, detail="Failed to load any CV files")
        
        # Check if services are initialized
        if not ingestion_pipeline or not ranking_engine:
            raise HTTPException(
                status_code=500,
                detail="Services not initialized. Check API keys."
            )
        
        # Ingest Job Description
        jd_vector_id = ingestion_pipeline.ingest_job_description(jd_text=job_description, session_id=session_id)
        
        # Ingest CVs
        cv_vector_ids = ingestion_pipeline.ingest_cvs(cv_data=cv_data, session_id=session_id)
        
        # Calculate semantic similarity scores
        semantic_scores = await _calculate_semantic_scores(
            ingestion_pipeline,
            jd_text=job_description,
            cv_data=cv_data,
            session_id=session_id
        )
        
        # Rank candidates
        ranked_candidates = ranking_engine.rank_candidates(
            jd_text=job_description,
            cv_data=cv_data,
            semantic_scores=semantic_scores,
            session_id=session_id
        )
        
        # Get top N candidates
        top_candidates = ranking_engine.get_top_candidates(ranked_candidates, top_n=top_n)
        
        # Convert to dict for JSON response
        top_candidates_dict = [
            {
                "candidate_name": c.candidate_name,
                "file_path": c.file_path,
                "match_score": c.match_score,
                "matched_skills": c.matched_skills,
                "missing_skills": c.missing_skills,
                "explanation": c.explanation,
                "detailed_scores": {
                    "skill_match": c.skill_match_score,
                    "experience": c.experience_score,
                    "tool_tech": c.tool_tech_score,
                    "seniority": c.seniority_score,
                    "semantic": c.semantic_score
                }
            }
            for c in top_candidates
        ]
        
        processing_time = time.time() - start_time
        
        logger.info(f"Ranking completed for session {session_id} in {processing_time:.2f}s")
        
        return RankingResponse(
            session_id=session_id,
            top_candidates=top_candidates_dict,
            total_candidates=len(ranked_candidates),
            processing_time_seconds=round(processing_time, 2)
        )
    
    except HTTPException:
        # Clean up session on error
        session_manager.cleanup_session(session_id)
        raise
    except Exception as e:
        # Clean up session on error
        session_manager.cleanup_session(session_id)
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


async def _calculate_semantic_scores(
    ingestion_pipeline: IngestionPipeline,
    jd_text: str,
    cv_data: dict,
    session_id: str
) -> dict:
    """
    Calculate semantic similarity scores between JD and CVs
    
    Args:
        ingestion_pipeline: Initialized ingestion pipeline
        jd_text: Job description text
        cv_data: Dict of CV texts
        session_id: Session identifier
        
    Returns:
        Dict mapping file_path -> similarity score (0-1)
    """
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    
    # Generate JD embedding (text-embedding-3-small produces 1536 dimensions)
    jd_embedding = ingestion_pipeline.embeddings.embed_query(jd_text[:8000])  # Limit length
    
    scores = {}
    
    # Query Pinecone for each CV
    for file_path, cv_text in cv_data.items():
        if cv_text is None:
            continue
        
        # Generate CV embedding (text-embedding-3-small produces 1536 dimensions)
        cv_embedding = ingestion_pipeline.embeddings.embed_query(cv_text[:8000])
        
        # Calculate cosine similarity
        import numpy as np
        similarity = np.dot(jd_embedding, cv_embedding) / (
            np.linalg.norm(jd_embedding) * np.linalg.norm(cv_embedding)
        )
        
        # Normalize to 0-1 range (cosine similarity is already -1 to 1, but typically 0-1)
        scores[file_path] = max(0.0, similarity)
    
    return scores


@app.get("/download-cv/{session_id}/{filename:path}")
async def download_cv(session_id: str, filename: str):
    """
    Download a CV file from a session
    
    Args:
        session_id: Session identifier
        filename: Name of the file to download
        
    Returns:
        File response
    """
    session_dir = session_manager.get_session_dir(session_id)
    file_path = session_dir / filename
    
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    
    # Security check: ensure file is within session directory
    try:
        file_path.resolve().relative_to(session_dir.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/octet-stream"
    )


@app.delete("/session/{session_id}")
async def cleanup_session(session_id: str):
    """
    Clean up a session and all associated data
    
    Args:
        session_id: Session identifier
        
    Returns:
        Success message
    """
    # Clean up files
    session_manager.cleanup_session(session_id)
    
    # Clean up vectors
    if ingestion_pipeline:
        ingestion_pipeline.cleanup_session_vectors(session_id)
    
    return {"message": f"Session {session_id} cleaned up successfully"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "ingestion": ingestion_pipeline is not None,
            "agent": analysis_agent is not None,
            "ranking": ranking_engine is not None
        }
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

