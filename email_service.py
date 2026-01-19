"""
Email service for password reset
Uses SMTP to send password reset links
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def send_reset_email(email: str, reset_token: str) -> bool:
    """
    Send password reset email with reset link via SMTP
    
    Args:
        email: Recipient email address
        reset_token: Secure reset token to include in link
        
    Returns:
        True if email sent successfully, False otherwise
    """
    # Get SMTP configuration from environment variables
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:8501")
    
    # If SMTP credentials not configured, print to console (dev mode)
    if not smtp_username or not smtp_password:
        reset_link = f"{frontend_url}?token={reset_token}"
        print(f"[DEV MODE] Password reset link for {email}: {reset_link}")
        return True
    
    try:
        # Create email message
        msg = MIMEMultipart()
        msg["From"] = smtp_username
        msg["To"] = email
        msg["Subject"] = "HR AI Agent - Password Reset"
        
        # Create reset link (format: http://localhost:8501/?token=XXXX)
        reset_link = f"{frontend_url}/?token={reset_token}"
        
        # Email body with clear reset link
        body = f"""Hello,

You requested a password reset for your HR AI Agent account.

Click the link below to reset your password (valid for 15 minutes):
{reset_link}

If you did not request this reset, please ignore this email.

Best regards,
HR AI Agent Team
"""
        msg.attach(MIMEText(body, "plain"))
        
        # Send email via SMTP with TLS
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Use TLS encryption
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        
        return True
    except Exception as e:
        # Log error but don't expose to user (security)
        print(f"Error sending password reset email: {str(e)}")
        # Still print link for dev/testing
        reset_link = f"{frontend_url}/?token={reset_token}"
        print(f"[FALLBACK] Password reset link for {email}: {reset_link}")
        return False
