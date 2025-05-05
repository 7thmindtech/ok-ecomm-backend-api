import os
from typing import BinaryIO
from app.core.config import settings

async def upload_file_to_s3(file: BinaryIO, filename: str, folder: str) -> str:
    """Upload a file to local S3-like storage"""
    storage_path = os.path.join(settings.LOCAL_STORAGE_PATH, "okyke-files", folder)
    os.makedirs(storage_path, exist_ok=True)
    
    file_path = os.path.join(storage_path, filename)
    with open(file_path, "wb") as f:
        f.write(file.read())
    
    return f"/storage/{folder}/{filename}"

async def delete_file_from_s3(filename: str, folder: str) -> None:
    """Delete a file from local S3-like storage"""
    file_path = os.path.join(settings.LOCAL_STORAGE_PATH, "okyke-files", folder, filename)
    if os.path.exists(file_path):
        os.remove(file_path) 