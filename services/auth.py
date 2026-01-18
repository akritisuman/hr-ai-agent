"""
Authentication endpoints for FastAPI
Handles signup, login, and password reset
"""

import os
import secrets
import string
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional

from database import get_db, init_db
from models import User
from security import hash_password, verify_password
from email_service import send_reset_email

# Initialize database on import
init_db()

# Create router
auth_router = APIRouter(prefix="/auth", tags=["authentication"])

# Security scheme (not used for session-based auth, but kept for compatibility)
security = HTTPBasic()


# Request/Response models
class SignupRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class AuthResponse(BaseModel):
    success: bool
    message: str
    user_email: Optional[str] = None


def generate_reset_token() -> str:
    """Generate a secure random token for password reset"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(32))


@auth_router.post("/signup", response_model=AuthResponse)
async def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """
    Create a new user account
    
    Args:
        request: Signup request with user details
        db: Database session
        
    Returns:
        Success response with user email
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate password
    if len(request.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters long"
        )
    
    # Hash password
    password_hash = hash_password(request.password)
    
    # Create user
    new_user = User(
        first_name=request.first_name,
        last_name=request.last_name,
        email=request.email,
        password_hash=password_hash
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return AuthResponse(
            success=True,
            message="Account created successfully",
            user_email=request.email
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating account: {str(e)}"
        )


@auth_router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user and return success status
    
    Args:
        request: Login request with email and password
        db: Database session
        
    Returns:
        Success response with user email
    """
    # Find user by email
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    return AuthResponse(
        success=True,
        message="Login successful",
        user_email=user.email
    )


@auth_router.post("/forgot-password", response_model=AuthResponse)
async def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Request password reset - sends reset link via email
    
    Args:
        request: Forgot password request with email
        db: Database session
        
    Returns:
        Generic success message (never reveals if email exists)
    """
    # Find user by email
    user = db.query(User).filter(User.email == request.email).first()
    
    # Always return success message (security: don't reveal if email exists)
    if user:
        # Generate secure reset token
        reset_token = generate_reset_token()
        
        # Set expiry to 15 minutes from now
        reset_token_expiry = datetime.utcnow() + timedelta(minutes=15)
        
        try:
            # Save token and expiry
            user.reset_token = reset_token
            user.reset_token_expiry = reset_token_expiry
            db.commit()
            
            # Send reset email
            send_reset_email(user.email, reset_token)
            
            # Print reset link to console for dev testing
            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:8501")
            reset_link = f"{frontend_url}/?token={reset_token}"
            print(f"[DEV MODE] Password reset link for {user.email}: {reset_link}")
        except Exception as e:
            db.rollback()
            # Still return success message (don't reveal error)
            pass
    
    # Always return the same message regardless of whether email exists
    return AuthResponse(
        success=True,
        message="If the email exists, a reset link has been sent"
    )


@auth_router.post("/reset-password", response_model=AuthResponse)
async def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Reset password using token from email link
    
    Args:
        request: Reset password request with token and new password
        db: Database session
        
    Returns:
        Success response
    """
    # Find user by reset token
    user = db.query(User).filter(User.reset_token == request.token).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Check if token is expired
    if user.reset_token_expiry is None or user.reset_token_expiry < datetime.utcnow():
        # Clear expired token
        user.reset_token = None
        user.reset_token_expiry = None
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Validate password length
    if len(request.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters long"
        )
    
    # Hash new password
    password_hash = hash_password(request.new_password)
    
    try:
        # Update password and clear reset token
        user.password_hash = password_hash
        user.reset_token = None
        user.reset_token_expiry = None
        db.commit()
        
        return AuthResponse(
            success=True,
            message="Password reset successfully",
            user_email=user.email
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resetting password: {str(e)}"
        )

