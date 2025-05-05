from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr, SecretStr
from jinja2 import Environment, select_autoescape, PackageLoader
from pathlib import Path
from app.core.config import settings

email_config = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD.get_secret_value(),
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS,
    MAIL_DEBUG=1 if settings.DEBUG else 0  # Set based on application debug mode
)

fastmail = FastMail(email_config)

env = Environment(
    loader=PackageLoader('app', 'templates/email'),
    autoescape=select_autoescape(['html', 'xml'])
)

async def send_verification_email(email: EmailStr, token: str):
    template = env.get_template('verify_email.html')
    verification_url = f"{settings.FRONTEND_URL}/auth/verify-email/{token}?email={email}"
    
    html = template.render(
        verification_url=verification_url
    )
    
    message = MessageSchema(
        subject="Verify your email address",
        recipients=[email],
        body=html,
        subtype="html"
    )
    
    await fastmail.send_message(message)

async def send_password_reset_email(email: EmailStr, token: str):
    template = env.get_template('reset_password.html')
    reset_url = f"{settings.FRONTEND_URL}/auth/reset-password/{token}?email={email}"
    
    html = template.render(
        reset_url=reset_url
    )
    
    message = MessageSchema(
        subject="Reset your password",
        recipients=[email],
        body=html,
        subtype="html"
    )
    
    await fastmail.send_message(message) 