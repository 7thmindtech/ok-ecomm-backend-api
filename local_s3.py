#!/usr/bin/env python3
import os
import shutil
import uuid
import traceback
from pathlib import Path
from fastapi import UploadFile
import logging
import re
import base64
import io
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set to DEBUG for more detailed logs

# Local S3 configuration
LOCAL_STORAGE_DIR = "/Users/bo/Desktop/AI stuff/okyke_ecomm_v4/backend/local_s3_storage"
BASE_URL = "http://127.0.0.1:8888/local_s3"  # Base URL for accessing the files

class LocalS3Client:
    """Simulates AWS S3 client with local file storage"""
    
    def __init__(self, storage_dir=None):
        """Initialize the local S3 client with storage directory"""
        self.storage_dir = storage_dir or LOCAL_STORAGE_DIR
        self._ensure_storage_dir()
    
    def _ensure_storage_dir(self):
        """Ensure the storage directory exists"""
        os.makedirs(self.storage_dir, exist_ok=True)
        logger.info(f"Local S3 storage initialized at: {self.storage_dir}")
    
    async def upload_fileobj(self, file_obj, bucket_name, key, **kwargs):
        """
        Simulates S3's upload_fileobj by copying file to local storage
        
        Args:
            file_obj: The file object to upload
            bucket_name: Simulated bucket name (becomes a subdirectory)
            key: The file key/path within the bucket
            **kwargs: Extra arguments (ignored for compatibility)
        """
        # Create bucket directory if it doesn't exist
        bucket_dir = os.path.join(self.storage_dir, bucket_name)
        os.makedirs(bucket_dir, exist_ok=True)
        
        # Create subdirectories in the key path if necessary
        key_parts = key.split('/')
        key_path = os.path.join(bucket_dir, *key_parts)
        key_dir = os.path.dirname(key_path)
        
        logger.info(f"Ensuring directory exists: {key_dir}")
        os.makedirs(key_dir, exist_ok=True)
        
        # Write the file
        try:
            # Make sure the key directory exists
            os.makedirs(os.path.dirname(key_path), exist_ok=True)
            
            # Check file object type and properties
            logger.debug(f"File object type: {type(file_obj)}")
            logger.debug(f"File object attributes: {dir(file_obj)}")
            
            # Dump file object content for debugging
            if hasattr(file_obj, 'read'):
                try:
                    # Get current position
                    if hasattr(file_obj, 'tell'):
                        current_pos = file_obj.tell()
                        logger.debug(f"Current file position before read: {current_pos}")
                    
                    # Read a small sample for debugging
                    if hasattr(file_obj, 'seek'):
                        file_obj.seek(0)
                        sample = file_obj.read(100)  # Read first 100 bytes for debug
                        logger.debug(f"File sample (first 100 bytes): {sample}")
                        file_obj.seek(0)  # Reset to beginning
                except Exception as e:
                    logger.error(f"Error inspecting file object: {str(e)}")
            
            with open(key_path, "wb") as dest_file:
                # Get current position
                current_pos = 0
                if hasattr(file_obj, 'tell'):
                    try:
                        current_pos = file_obj.tell()
                        logger.debug(f"Current file position: {current_pos}")
                    except Exception as e:
                        logger.error(f"Error getting file position: {str(e)}")
                
                # Seek to the beginning of the file if possible
                if hasattr(file_obj, 'seek'):
                    try:
                        file_obj.seek(0)
                        logger.debug("Successfully seeked to beginning of file")
                    except Exception as e:
                        logger.error(f"Error seeking file: {str(e)}")
                
                # Try different methods of copying based on file_obj type
                try:
                    if hasattr(file_obj, 'read'):
                        # Get file content as bytes
                        content = file_obj.read()
                        logger.debug(f"Read {len(content)} bytes from file")
                        
                        # Write content to destination
                        dest_file.write(content)
                        logger.debug(f"Wrote {len(content)} bytes to {key_path}")
                    else:
                        # Fallback - try copyfileobj
                        logger.debug("Using shutil.copyfileobj for file copy")
                        shutil.copyfileobj(file_obj, dest_file)
                except Exception as e:
                    logger.error(f"Error copying file content: {str(e)}")
                    logger.error(traceback.format_exc())
                    raise e
                
                # Try to return to original position
                if hasattr(file_obj, 'seek'):
                    try:
                        file_obj.seek(current_pos)
                        logger.debug(f"Returned to position {current_pos}")
                    except Exception as e:
                        logger.error(f"Error returning to original position: {str(e)}")
            
            file_size = os.path.getsize(key_path)
            logger.info(f"File uploaded successfully to: {key_path} (size: {file_size} bytes)")
            
            # Print the full URL for debugging
            full_url = f"{BASE_URL}/{bucket_name}/{key}"
            logger.info(f"File accessible at: {full_url}")
            
            # Verify the file was actually written
            if not os.path.exists(key_path):
                logger.error(f"File does not exist after write: {key_path}")
                return False
                
            if os.path.getsize(key_path) == 0:
                logger.error(f"File is empty after write: {key_path}")
                return False
                
            return True
        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            logger.error(traceback.format_exc())
            raise e
    
    async def delete_object(self, bucket_name, key, **kwargs):
        """
        Simulates S3's delete_object by removing file from local storage
        
        Args:
            bucket_name: Simulated bucket name (becomes a subdirectory)
            key: The file key/path within the bucket
            **kwargs: Extra arguments (ignored for compatibility)
        """
        file_path = os.path.join(self.storage_dir, bucket_name, key)
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"File deleted: {file_path}")
            return True
        else:
            logger.warning(f"File not found for deletion: {file_path}")
            return False

async def upload_file(file: UploadFile, folder: str = "", bucket: str = "okyke-files"):
    """
    Upload a file to local S3-like storage and return its URL
    
    Args:
        file: The file to upload
        folder: Optional folder path within the bucket
        bucket: Simulated bucket name
    
    Returns:
        str: The URL of the uploaded file
    """
    try:
        logger.info(f"Starting upload for file: {file.filename} to folder: {folder}")
        
        # Log all file attributes for debugging
        file_attrs = {attr: getattr(file, attr) for attr in dir(file) 
                     if not attr.startswith('_') and not callable(getattr(file, attr))}
        logger.debug(f"File attributes: {file_attrs}")
        
        # Ensure we have a filename to work with
        if not file.filename:
            file.filename = f"uploaded_file_{uuid.uuid4()}"
            logger.warning(f"No filename provided, using generated name: {file.filename}")

        # Create SEO-friendly filename
        # Format: product-description-short-unique-id.extension
        original_extension = file.filename.split('.')[-1] if '.' in file.filename else ''
        
        # Generate a short unique ID (8 chars from UUID)
        short_id = str(uuid.uuid4()).split('-')[0]
        
        # Extract folder info for better naming
        # For product images, extract product ID and info
        seo_prefix = "image"
        if folder.startswith("products/"):
            parts = folder.split('/')
            if len(parts) >= 2 and parts[0] == "products":
                product_id = parts[1]
                # If this is a product folder, prefix with 'product'
                seo_prefix = f"product-{product_id}"
        
        # Create SEO-friendly base name from original filename
        # Remove extension and any existing unique IDs
        base_name = file.filename
        if '.' in base_name:
            base_name = base_name.rsplit('.', 1)[0]
        
        # Clean up the base name - keep only alphanumeric and replace spaces/underscores with hyphens
        base_name = re.sub(r'[^\w\s-]', '', base_name.lower())
        base_name = re.sub(r'[\s_-]+', '-', base_name)
        
        # Limit to first 3-4 words for better SEO
        base_name_parts = base_name.split('-')
        if len(base_name_parts) > 4:
            base_name = '-'.join(base_name_parts[:4])
        
        # Combine parts into SEO-friendly filename
        seo_filename = f"{seo_prefix}-{base_name}-{short_id}.{original_extension}"
        
        # Final cleanup - ensure no double hyphens and all lowercase
        seo_filename = re.sub(r'-+', '-', seo_filename).lower()
        
        logger.info(f"Generated SEO-friendly filename: {seo_filename}")
        
        # Combine folder and filename, ensuring proper path format
        folder = folder.rstrip('/') if folder else ""
        
        # Ensure the product directory exists first
        if folder.startswith("products/"):
            # Extract product ID
            parts = folder.split('/')
            if len(parts) >= 2 and parts[0] == "products":
                product_id = parts[1]
                logger.info(f"Processing upload for product ID: {product_id}")
                
                # Create the full product directory path - use the specific required path
                product_dir = os.path.join(LOCAL_STORAGE_DIR, bucket, "products", product_id)
                logger.info(f"Ensuring product directory exists: {product_dir}")
                os.makedirs(product_dir, exist_ok=True)
                
                # Create test file to check permissions
                test_file_path = os.path.join(product_dir, "test_write.txt")
                try:
                    with open(test_file_path, "w") as test_file:
                        test_file.write("Test write permission")
                    os.remove(test_file_path)  # Clean up test file
                    logger.debug(f"Write test successful in directory: {product_dir}")
                except Exception as e:
                    logger.error(f"Write permission test failed: {str(e)}")
                    # If permission test fails, log the details
                    logger.error(f"Directory permissions: {os.access(product_dir, os.R_OK)}, {os.access(product_dir, os.W_OK)}, {os.access(product_dir, os.X_OK)}")
        
        # Build the key with proper slashes - use SEO friendly filename
        key = f"{folder}/{seo_filename}" if folder else seo_filename
        key = key.replace('//', '/')  # Fix any double slashes
        
        logger.info(f"Generated key for upload: {key}")
        
        # Create S3 client - use the specific local storage directory
        s3_client = LocalS3Client(storage_dir=LOCAL_STORAGE_DIR)
        
        # Get file content for direct upload
        try:
            # Read file content
            file_content = await file.read()
            logger.debug(f"Read {len(file_content)} bytes from file")
            
            # Reset file position for upload
            await file.seek(0)
            logger.debug("Reset file position for upload")
            
            # Directly upload file content
            file_key_path = os.path.join(bucket, key)
            logger.debug(f"File key path: {file_key_path}")
            
            await s3_client.upload_fileobj(file.file, bucket, key)
            
            # Build the URL to access the file
            url = f"{BASE_URL}/{bucket}/{key}"
            logger.info(f"File uploaded successfully: {url}")
            
            # Verify file exists
            file_path = os.path.join(LOCAL_STORAGE_DIR, bucket, key)
            logger.debug(f"Physical file path: {file_path}")
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                logger.info(f"Verified file exists: {file_path} (size: {file_size} bytes)")
            else:
                logger.error(f"File does not exist after upload: {file_path}")
                
            return url
        except Exception as e:
            logger.error(f"Error reading file content: {str(e)}")
            logger.error(traceback.format_exc())
            raise e
            
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        logger.error(traceback.format_exc())
        raise e

async def delete_file(file_url: str):
    """
    Delete a file from local S3-like storage using its URL
    
    Args:
        file_url: The URL of the file to delete
    
    Returns:
        bool: True if deletion was successful
    """
    try:
        # Extract the bucket and key from the URL
        path_parts = file_url.replace(f"{BASE_URL}/", "").split("/", 1)
        if len(path_parts) < 2:
            logger.error(f"Invalid file URL format: {file_url}")
            return False
        
        bucket = path_parts[0]
        key = path_parts[1]
        
        # Create S3 client
        s3_client = LocalS3Client()
        
        # Delete the file
        result = await s3_client.delete_object(bucket, key)
        return result
        
    except Exception as e:
        logger.error(f"Failed to delete file: {str(e)}")
        return False

# Setup the directories on module import
def setup_local_s3():
    """Set up the local S3 storage directories"""
    # Create main storage directory
    os.makedirs(LOCAL_STORAGE_DIR, exist_ok=True)
    
    # Create default bucket
    default_bucket = os.path.join(LOCAL_STORAGE_DIR, "okyke-files")
    os.makedirs(default_bucket, exist_ok=True)
    
    # Create common product folders
    products_dir = os.path.join(default_bucket, "products")
    os.makedirs(products_dir, exist_ok=True)
    
    # Create a test product directory to ensure structure is correct
    test_product_dir = os.path.join(products_dir, "test")
    os.makedirs(test_product_dir, exist_ok=True)
    
    # Check permissions by writing a test file
    try:
        test_file_path = os.path.join(test_product_dir, "test_permissions.txt")
        with open(test_file_path, "w") as f:
            f.write("Testing write permissions")
        
        # Read back to verify
        with open(test_file_path, "r") as f:
            content = f.read()
            
        # Clean up
        os.remove(test_file_path)
        logger.info("Storage permissions verified: write/read successful")
    except Exception as e:
        logger.error(f"Storage permission check failed: {str(e)}")
    
    logger.info(f"Local S3 storage set up at: {LOCAL_STORAGE_DIR}")
    logger.info(f"Products directory: {products_dir}")
    return LOCAL_STORAGE_DIR

# Setup on import
setup_local_s3()

# --- New function for Customization Images ---
async def upload_customization_image_data(
    image_data: bytes | str, # Can be raw bytes or base64 data URL string
    user_id: int,
    product_id: int,
    image_type: str, # e.g., 'rendered', 'ai_openai', 'ai_stability'
    bucket: str = "okyke-files"
) -> str:
    """
    Uploads image data (bytes or base64 string) for a product customization 
    to a structured path in the local S3 storage.

    Args:
        image_data: The image data as bytes or a base64 data URL string.
        user_id: The ID of the user performing the customization.
        product_id: The ID of the product being customized.
        image_type: A string identifying the type of image (e.g., 'rendered', 'ai_openai').
        bucket: The target bucket name.

    Returns:
        str: The public URL of the uploaded image.
    
    Raises:
        ValueError: If the image data format is invalid.
        Exception: If the upload fails.
    """
    try:
        logger.info(f"Uploading customization image data for user {user_id}, product {product_id}, type {image_type}")
        
        image_bytes: bytes
        file_extension = "png" # Default to png
        
        if isinstance(image_data, str):
            # Handle base64 data URL (e.g., "data:image/png;base64,iVBOR...")
            if image_data.startswith('data:image'):
                try:
                    header, encoded_data = image_data.split(';base64,', 1)
                    # Extract extension from header (e.g., data:image/png -> png)
                    mime_type = header.split(':')[1].split('/')[1]
                    if mime_type in ['png', 'jpeg', 'jpg', 'webp']:
                        file_extension = mime_type if mime_type != 'jpeg' else 'jpg'
                    else:
                         logger.warning(f"Unsupported image format in data URL: {mime_type}. Defaulting to png.")
                         file_extension = "png"
                         
                    image_bytes = base64.b64decode(encoded_data)
                    logger.debug(f"Decoded base64 image data ({len(image_bytes)} bytes), extension: {file_extension}")
                except Exception as e:
                    logger.error(f"Failed to decode base64 image string: {e}")
                    raise ValueError("Invalid base64 image data format") from e
            else:
                 raise ValueError("Invalid image data string format. Expected base64 data URL.")
        elif isinstance(image_data, bytes):
            image_bytes = image_data
            # We might not know the extension for raw bytes, default to png
            # In a real scenario, the AI service might provide the format
            file_extension = "png" 
            logger.debug(f"Received raw image bytes ({len(image_bytes)} bytes)")
        else:
            raise ValueError(f"Unsupported image_data type: {type(image_data)}")

        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        filename = f"{timestamp}-{image_type}.{file_extension}"
        
        # Define structured folder path
        folder = f"products/custom_designs/{user_id}/{product_id}"
        key = f"{folder}/{filename}"
        
        logger.info(f"Generated key for customization upload: {key}")
        
        # Create S3 client
        s3_client = LocalS3Client(storage_dir=LOCAL_STORAGE_DIR)
        
        # Use BytesIO to simulate a file object for upload_fileobj
        file_obj = io.BytesIO(image_bytes)
        
        # Upload the file object
        await s3_client.upload_fileobj(file_obj, bucket, key)
        
        # Build the public URL
        url = f"{BASE_URL}/{bucket}/{key}"
        logger.info(f"Customization image uploaded successfully: {url}")

        # Verify file exists (optional, good for debugging local setup)
        file_path = os.path.join(LOCAL_STORAGE_DIR, bucket, key)
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            logger.info(f"Verified file exists: {file_path} (size: {file_size} bytes)")
        else:
            logger.error(f"File does not exist after upload: {file_path}")
            # Even if verification fails locally, return URL as upload_fileobj didn't raise error

        return url

    except ValueError as ve:
        logger.error(f"Invalid input for customization upload: {ve}")
        raise ve
    except Exception as e:
        logger.error(f"Error uploading customization image data: {str(e)}")
        logger.error(traceback.format_exc())
        raise Exception("Failed to upload customization image.") from e 