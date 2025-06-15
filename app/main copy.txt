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

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.db.base import Base  # noqa: F401
from app.api.v1 import api_router
from app.db.init_db import init_db
from app.db.seed import seed_db
import os
import sys
import logging
import uvicorn

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
    USE_LOCAL_S3 = True
except ImportError:
    USE_LOCAL_S3 = False
    LOCAL_STORAGE_DIR = None

# Ensure we have a storage directory
STORAGE_DIR = settings.LOCAL_STORAGE_PATH if hasattr(settings, 'LOCAL_STORAGE_PATH') else LOCAL_STORAGE_DIR

app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"/api/{settings.API_VERSION}/openapi.json",
    version=settings.API_VERSION,
    description="Okyke E-commerce Platform API",
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    allowed_origins = [str(origin) for origin in settings.BACKEND_CORS_ORIGINS]
    logger.info(f"Configuring CORS with allowed origins: {allowed_origins}")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"], # Allow all methods
        allow_headers=["*"], # Allow all headers
    )
else:
    logger.warning("BACKEND_CORS_ORIGINS not configured. CORS middleware not added.")

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Mount local S3 storage as static files if available
if STORAGE_DIR and os.path.exists(STORAGE_DIR):
    app.mount("/local_s3", StaticFiles(directory=STORAGE_DIR), name="local_s3")
    logger.info(f"Mounted local storage from {STORAGE_DIR} at /local_s3")
else:
    logger.warning(f"Local storage directory not found: {STORAGE_DIR}")

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

@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "healthy"}

# Special endpoint for local S3 file access for compatibility
@app.get("/local_s3/{bucket}/{file_path:path}")
async def get_s3_file(bucket: str, file_path: str):
    if not STORAGE_DIR:
        raise HTTPException(status_code=404, detail="Local S3 storage not configured")
        
    full_path = os.path.join(STORAGE_DIR, bucket, file_path)
    if not os.path.exists(full_path):
        logger.error(f"File not found: {full_path}")
        raise HTTPException(status_code=404, detail=f"File not found: {bucket}/{file_path}")
    
    logger.debug(f"Serving file: {full_path}")
    return FileResponse(full_path)

@app.on_event("startup")
async def startup_event():
    logger.info("Initializing database...")
    init_db()
    
    # Check if we should seed the database with initial data
    if settings.DEBUG and settings.ENVIRONMENT == "development":
        logger.info("Seeding database with initial data...")
        try:
            seed_db()
            logger.info("Database seeded successfully!")
        except Exception as e:
            logger.error(f"Error seeding database: {e}")

@app.get("/seed")
def run_seed_db():
    """Endpoint to manually trigger database seeding (development only)"""
    if not (settings.DEBUG and settings.ENVIRONMENT == "development"):
        raise HTTPException(status_code=403, detail="This endpoint is only available in development mode")
    
    try:
        seed_db()
        return {"message": "Database seeded successfully!"}
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=3002, reload=True) 