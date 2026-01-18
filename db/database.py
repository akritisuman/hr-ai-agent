"""
Database configuration for authentication
SQLAlchemy setup for SQLite database
"""

from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Get absolute path to database file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "auth.db")

# Database URL - use absolute path
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Create engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def init_db():
    """
    Initialize database - create all tables
    If database exists but schema is outdated, recreates it
    """
    # Check if database file exists (using absolute path)
    db_exists = os.path.exists(DATABASE_PATH)
    
    if db_exists:
        # Check if users table exists and has required columns
        inspector = inspect(engine)
        if inspector.has_table("users"):
            columns = [col["name"] for col in inspector.get_columns("users")]
            required_columns = ["reset_token", "reset_token_expiry"]
            
            # If required columns are missing, recreate database
            if not all(col in columns for col in required_columns):
                # Drop all tables and recreate
                Base.metadata.drop_all(bind=engine)
                Base.metadata.create_all(bind=engine)
                return
    
    # Create all tables (will not recreate if they exist with correct schema)
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


