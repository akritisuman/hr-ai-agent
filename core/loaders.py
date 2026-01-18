"""
Document Loaders for CV Processing
Supports PDF, DOC, and DOCX formats with error handling
"""

import os
from typing import List, Dict, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logger.warning("PyPDF2 not available. PDF support disabled.")

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    logger.warning("python-docx not available. DOCX support disabled.")

try:
    import docx2txt
    DOC_AVAILABLE = True
except ImportError:
    DOC_AVAILABLE = False
    logger.warning("docx2txt not available. DOC support disabled.")


class DocumentLoader:
    """Handles loading and extraction of text from various document formats"""
    
    @staticmethod
    def load_pdf(file_path: str) -> str:
        """Extract text from PDF file"""
        if not PDF_AVAILABLE:
            raise ImportError("PyPDF2 is required for PDF processing")
        
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            logger.error(f"Error reading PDF {file_path}: {str(e)}")
            raise
        return text.strip()
    
    @staticmethod
    def load_docx(file_path: str) -> str:
        """Extract text from DOCX file"""
        if not DOCX_AVAILABLE:
            raise ImportError("python-docx is required for DOCX processing")
        
        try:
            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text.strip()
        except Exception as e:
            logger.error(f"Error reading DOCX {file_path}: {str(e)}")
            raise
    
    @staticmethod
    def load_doc(file_path: str) -> str:
        """Extract text from DOC file"""
        if not DOC_AVAILABLE:
            raise ImportError("docx2txt is required for DOC processing")
        
        try:
            text = docx2txt.process(file_path)
            return text.strip()
        except Exception as e:
            logger.error(f"Error reading DOC {file_path}: {str(e)}")
            raise
    
    @staticmethod
    def load_document(file_path: str) -> str:
        """Auto-detect file type and load document"""
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.pdf':
            return DocumentLoader.load_pdf(file_path)
        elif file_ext == '.docx':
            return DocumentLoader.load_docx(file_path)
        elif file_ext == '.doc':
            return DocumentLoader.load_doc(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
    
    @staticmethod
    def batch_load_documents(file_paths: List[str]) -> Dict[str, str]:
        """
        Load multiple documents in parallel
        Returns dict mapping file_path -> extracted_text
        """
        results = {}
        for file_path in file_paths:
            try:
                results[file_path] = DocumentLoader.load_document(file_path)
                logger.info(f"Successfully loaded: {file_path}")
            except Exception as e:
                logger.error(f"Failed to load {file_path}: {str(e)}")
                results[file_path] = None
        
        return results



















