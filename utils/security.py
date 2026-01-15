"""
Security Utilities for Session Isolation and Data Protection
"""

import os
import uuid
import shutil
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manages session isolation and temporary file storage
    Ensures no data leakage between sessions
    """
    
    def __init__(self, base_temp_dir: str = "temp_sessions"):
        """
        Initialize session manager
        
        Args:
            base_temp_dir: Base directory for temporary session storage
        """
        self.base_temp_dir = Path(base_temp_dir)
        self.base_temp_dir.mkdir(exist_ok=True)
    
    def create_session(self) -> str:
        """
        Create a new session and return session ID
        
        Returns:
            Unique session ID
        """
        session_id = str(uuid.uuid4())
        session_dir = self.base_temp_dir / session_id
        session_dir.mkdir(exist_ok=True)
        logger.info(f"Created session: {session_id}")
        return session_id
    
    def get_session_dir(self, session_id: str) -> Path:
        """
        Get directory path for a session
        
        Args:
            session_id: Session identifier
            
        Returns:
            Path to session directory
        """
        return self.base_temp_dir / session_id
    
    def save_file(self, session_id: str, filename: str, file_content: bytes) -> Path:
        """
        Save file to session directory
        
        Args:
            session_id: Session identifier
            filename: Original filename
            file_content: File content as bytes
            
        Returns:
            Path to saved file
        """
        session_dir = self.get_session_dir(session_id)
        file_path = session_dir / filename
        with open(file_path, 'wb') as f:
            f.write(file_content)
        logger.info(f"Saved file {filename} to session {session_id}")
        return file_path
    
    def cleanup_session(self, session_id: str) -> bool:
        """
        Clean up all files for a session
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if cleanup successful
        """
        try:
            session_dir = self.get_session_dir(session_id)
            if session_dir.exists():
                shutil.rmtree(session_dir)
                logger.info(f"Cleaned up session: {session_id}")
                return True
        except Exception as e:
            logger.error(f"Error cleaning up session {session_id}: {str(e)}")
            return False
    
    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """
        Clean up sessions older than specified hours
        
        Args:
            max_age_hours: Maximum age in hours before cleanup
        """
        import time
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        for session_dir in self.base_temp_dir.iterdir():
            if session_dir.is_dir():
                try:
                    # Check modification time
                    mtime = session_dir.stat().st_mtime
                    if current_time - mtime > max_age_seconds:
                        self.cleanup_session(session_dir.name)
                except Exception as e:
                    logger.error(f"Error checking session {session_dir.name}: {str(e)}")


class SecurityValidator:
    """Validates file uploads and prevents security issues"""
    
    ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx'}
    MAX_FILE_SIZE_MB = 10
    
    @staticmethod
    def validate_file_extension(filename: str) -> bool:
        """
        Validate file extension is allowed
        
        Args:
            filename: Name of the file
            
        Returns:
            True if extension is allowed
        """
        ext = Path(filename).suffix.lower()
        return ext in SecurityValidator.ALLOWED_EXTENSIONS
    
    @staticmethod
    def validate_file_size(file_size_bytes: int) -> bool:
        """
        Validate file size is within limits
        
        Args:
            file_size_bytes: File size in bytes
            
        Returns:
            True if file size is acceptable
        """
        max_size_bytes = SecurityValidator.MAX_FILE_SIZE_MB * 1024 * 1024
        return file_size_bytes <= max_size_bytes
    
    @staticmethod
    def validate_file(filename: str, file_size_bytes: int) -> tuple[bool, Optional[str]]:
        """
        Comprehensive file validation
        
        Args:
            filename: Name of the file
            file_size_bytes: File size in bytes
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not SecurityValidator.validate_file_extension(filename):
            return False, f"File type not allowed. Allowed: {SecurityValidator.ALLOWED_EXTENSIONS}"
        
        if not SecurityValidator.validate_file_size(file_size_bytes):
            return False, f"File too large. Max size: {SecurityValidator.MAX_FILE_SIZE_MB}MB"
        
        return True, None









