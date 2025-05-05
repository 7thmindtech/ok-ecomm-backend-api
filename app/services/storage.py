import boto3
from fastapi import UploadFile, HTTPException
from app.core.config import settings
import uuid
from typing import Optional
import os
import sys
import logging

# Add the backend directory to sys.path to import local_s3
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

try:
    from local_s3 import upload_file as local_upload_file, delete_file as local_delete_file
    USE_LOCAL_S3 = True
except ImportError:
    USE_LOCAL_S3 = False

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_s3_client():
    """
    Create and return an S3 client using AWS credentials from settings.
    """
    if USE_LOCAL_S3:
        logger.info("Using local S3 implementation")
        return None  # Not needed when using local S3
    
    if not all([settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY, settings.AWS_REGION]):
        raise HTTPException(
            status_code=500,
            detail="AWS credentials not configured"
        )
    
    return boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )

async def upload_file(file: UploadFile, folder: str = "") -> str:
    """
    Upload a file to S3 or local storage and return its URL.
    
    Args:
        file: The file to upload
        folder: Optional folder path within the bucket
    
    Returns:
        str: The URL of the uploaded file
    """
    if USE_LOCAL_S3:
        logger.info(f"Uploading file {file.filename} to local S3 storage in folder {folder}")
        try:
            url = await local_upload_file(file, folder)
            logger.info(f"File uploaded successfully to local S3: {url}")
            return url
        except Exception as e:
            logger.error(f"Error uploading to local S3: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload file to local storage: {str(e)}"
            )
    
    # Original AWS S3 implementation
    if not settings.S3_BUCKET:
        raise HTTPException(
            status_code=500,
            detail="S3 bucket not configured"
        )
    
    # Generate a unique filename
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else ''
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    
    # Combine folder and filename, ensuring proper path format
    key = f"{folder.rstrip('/')}/{unique_filename}" if folder else unique_filename
    
    try:
        s3_client = get_s3_client()
        
        # Upload the file
        await s3_client.upload_fileobj(
            file.file,
            settings.S3_BUCKET,
            key,
            ExtraArgs={
                "ContentType": file.content_type,
                "ACL": "public-read"
            }
        )
        
        # Generate the URL
        url = f"https://{settings.S3_BUCKET}.s3.{settings.AWS_REGION}.amazonaws.com/{key}"
        return url
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload file: {str(e)}"
        )
    finally:
        file.file.close()

async def delete_file(file_url: str) -> bool:
    """
    Delete a file from S3 or local storage using its URL.
    
    Args:
        file_url: The URL of the file to delete
    
    Returns:
        bool: True if deletion was successful
    """
    if USE_LOCAL_S3:
        logger.info(f"Deleting file from local S3 storage: {file_url}")
        try:
            success = await local_delete_file(file_url)
            if success:
                logger.info(f"File deleted successfully from local S3: {file_url}")
            else:
                logger.warning(f"File not found in local S3: {file_url}")
            return success
        except Exception as e:
            logger.error(f"Error deleting from local S3: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete file from local storage: {str(e)}"
            )
    
    # Original AWS S3 implementation
    if not settings.S3_BUCKET:
        raise HTTPException(
            status_code=500,
            detail="S3 bucket not configured"
        )
    
    try:
        # Extract the key from the URL
        key = file_url.split(f"{settings.S3_BUCKET}.s3.{settings.AWS_REGION}.amazonaws.com/")[-1]
        
        s3_client = get_s3_client()
        await s3_client.delete_object(
            Bucket=settings.S3_BUCKET,
            Key=key
        )
        return True
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete file: {str(e)}"
        ) 