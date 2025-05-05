from typing import Any, Dict, Optional
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr, BaseModel
from app.core.config import settings
import os

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS
)

async def send_email(
    email_to: str,
    subject_template: str,
    html_template: str,
) -> None:
    message = MessageSchema(
        subject=subject_template,
        recipients=[email_to],
        body=html_template,
        subtype="html"
    )
    
    fm = FastMail(conf)
    await fm.send_message(message)

async def send_verification_email(email_to: str, token: str, username: str) -> None:
    verification_url = f"{settings.FRONTEND_URL}/auth/verify-email/{token}"
    subject = "Verify your email"
    html_template = f"""
        <p>Hi {username},</p>
        <p>Welcome to OKYKE! Please click the link below to verify your email address:</p>
        <p><a href="{verification_url}">{verification_url}</a></p>
        <p>If you didn't sign up for OKYKE, you can ignore this email.</p>
        <p>Best regards,<br>The OKYKE Team</p>
    """
    
    await send_email(email_to=email_to, subject_template=subject, html_template=html_template)

async def send_reset_password_email(email_to: str, token: str, username: str) -> None:
    reset_url = f"{settings.FRONTEND_URL}/auth/reset-password/{token}"
    subject = "Reset your password"
    html_template = f"""
        <p>Hi {username},</p>
        <p>We received a request to reset your password. Click the link below to set a new password:</p>
        <p><a href="{reset_url}">{reset_url}</a></p>
        <p>This link will expire in 24 hours.</p>
        <p>If you didn't request a password reset, you can ignore this email.</p>
        <p>Best regards,<br>The OKYKE Team</p>
    """
    
    await send_email(email_to=email_to, subject_template=subject, html_template=html_template) 