try:
    # Monkey patch to fix bcrypt/passlib compatibility issue
    import bcrypt
    
    # Add the missing __about__ attribute to bcrypt
    if not hasattr(bcrypt, '__about__'):
        class VersionInfo:
            __version__ = getattr(bcrypt, '__version__', '4.0.1')  # Default version if not found
            
        bcrypt.__about__ = VersionInfo()
        print(f"Added missing __about__ attribute to bcrypt with version {bcrypt.__about__.__version__}")
except Exception as e:
    print("Error applying bcrypt compatibility fix:", e)

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.db.base import Base  # noqa: F401
from app.api.v1 import api_router
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add the backend directory to sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

# Import local S3 configuration
try:
    from local_s3 import LOCAL_STORAGE_DIR
    USE_LOCAL_S3 = False 
except ImportError:
    USE_LOCAL_S3 = False
    LOCAL_STORAGE_DIR = None

app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"/api/{settings.API_VERSION}/openapi.json",
    version=settings.API_VERSION,
    description="Okyke E-commerce Platform API",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],  # Allow frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Mount local S3 storage as static files if available
if USE_LOCAL_S3 and os.path.exists(LOCAL_STORAGE_DIR):
    app.mount("/local_s3", StaticFiles(directory=LOCAL_STORAGE_DIR), name="local_s3")

# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    print(f"ValidationError: {exc.errors()}")
    print(f"Request body: {await request.body()}")
    
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": str(await request.body())},
    )

@app.get("/")
async def root():
    return {
        "message": "Welcome to Okyke E-commerce Platform API",
        "version": settings.API_VERSION,
        "environment": settings.ENVIRONMENT,
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# # Special endpoint for local S3 file access for compatibility
# @app.get("/local_s3/{bucket}/{file_path:path}")
# async def get_s3_file(bucket: str, file_path: str):
#     if not USE_LOCAL_S3:
#         raise HTTPException(status_code=404, detail="Local S3 storage not configured")
        
#     file_path = os.path.join(LOCAL_STORAGE_DIR, bucket, file_path)
#     if not os.path.exists(file_path) or not os.path.isfile(file_path):
#         raise HTTPException(status_code=404, detail="File not found")
        
#     return FileResponse(file_path) 