from typing import Any, Dict, List, Optional
from pydantic import AnyHttpUrl, EmailStr, SecretStr, validator
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv
#from functools import lru_cache

load_dotenv()

class Settings(BaseSettings):
    API_VERSION: str = "v1"
    PROJECT_NAME: str = "OKYKE E-commerce Backend"
    
    # Fix: Use strings instead of AnyHttpUrl for CORS origins
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Server Settings
    PORT: int = 3001
    NODE_ENV: str = "development"
    
    # Database Settings
    POSTGRES_HOST: str = "okyke.crwk2swcs1bq.eu-west-1.rds.amazonaws.com"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "okyke"
    POSTGRES_USER: str = "okyke_admin"
    POSTGRES_PASSWORD: str = "Okykedb!"
    DATABASE_URL: str = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    
    # Storage Settings
    LOCAL_STORAGE_PATH: str = "/Users/bo/Desktop/AI stuff/okyke_ecomm_v4/backend/local_s3_storage"
    
    # JWT Settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-jwt-secret-key-here")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRES_IN: str = "24h"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Rate Limiting
    RATE_LIMIT_WINDOW_MS: int = 900000
    RATE_LIMIT_MAX_REQUESTS: int = 100
    
    # CORS
    CORS_ORIGIN: str = "http://localhost:3000"
    
    # Email Settings
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = 587
    SMTP_HOST: Optional[str] = "smtp.gmail.com"
    SMTP_USERNAME: Optional[str] = "info@gmofoundation.org"
    SMTP_PASSWORD: Optional[str] = "****0648*********"
    EMAILS_FROM_EMAIL: Optional[EmailStr] = "info@gmofoundation.org"
    EMAILS_FROM_NAME: Optional[str] = "OKYKE Support"
    
    # Application Settings
    APP_NAME: str = "Okyke"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:8080",
        "http://127.0.0.1:8080"
    ]
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # Database Configuration
    TEST_DATABASE_URL: str = os.getenv("TEST_DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/okyke_test")
    
    # Redis Configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # AWS Configuration
    AWS_ACCESS_KEY_ID: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION: Optional[str] = os.getenv("AWS_REGION")
    S3_BUCKET: Optional[str] = os.getenv("S3_BUCKET")
    
    # Stripe Configuration
    STRIPE_SECRET_KEY: Optional[str] = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_WEBHOOK_SECRET: Optional[str] = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    # Email Configuration
    EMAIL_FROM_NAME: str = os.getenv("EMAIL_FROM_NAME", "Okyke Support")
    EMAIL_FROM_ADDRESS: str = os.getenv("EMAIL_FROM_ADDRESS", "support@okyke.com")
    
    # Celery Configuration
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")
    
    # FastAPI Mail Configuration
    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME", "info@gmofoundation.org")
    MAIL_PASSWORD: SecretStr = SecretStr(os.getenv("MAIL_PASSWORD", "****706*******")) # Must be wrapped in SecretStr
    #MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD", "*********************")
    #MAIL_PASSWORD: SecretStr = SecretStr("*******************") #first checks env variable, .env or uses default value
    MAIL_FROM: EmailStr = os.getenv("MAIL_FROM", "info@gmofoundation.org")
    MAIL_PORT: int = int(os.getenv("MAIL_PORT", "587"))
    MAIL_SERVER: str = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_FROM_NAME: str = os.getenv("MAIL_FROM_NAME", "Okyke Support")
    MAIL_STARTTLS: bool = os.getenv("MAIL_STARTTLS", "True").lower() == "true"
    MAIL_SSL_TLS: bool = os.getenv("MAIL_SSL_TLS", "False").lower() == "true"
    USE_CREDENTIALS: bool = os.getenv("USE_CREDENTIALS", "True").lower() == "true"
    VALIDATE_CERTS: bool = os.getenv("VALIDATE_CERTS", "True").lower() == "true"
    
    @validator("MAIL_USERNAME", "MAIL_PASSWORD", "MAIL_FROM")
    def validate_mail_credentials(cls, v, values, **kwargs):
        if not v:
            field_name = kwargs.get("field", {}).get("name", "field")
            raise ValueError(f"{field_name} is required for email configuration")
        return v
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    class Config:
        case_sensitive = True
        env_file = ".env"
        validate_assignment = True
        extra = "allow"

settings = Settings()  
# @lru_cache
# def get_settings():
#     return Settings()