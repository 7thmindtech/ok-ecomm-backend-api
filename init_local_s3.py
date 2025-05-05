#!/usr/bin/env python3
import os
import sys
import shutil
import logging
import uuid
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
LOCAL_S3_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "local_s3_storage")
IMAGES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../admin_portal/public/images/products")
BUCKET_NAME = "okyke-files"

def setup_local_s3():
    """Create directory structure for local S3 storage"""
    bucket_dir = os.path.join(LOCAL_S3_DIR, BUCKET_NAME)
    products_dir = os.path.join(bucket_dir, "products")
    
    # Ensure directories exist
    os.makedirs(products_dir, exist_ok=True)
    logger.info(f"Created local S3 directory structure: {products_dir}")
    return products_dir

def list_images():
    """List available product images"""
    if not os.path.exists(IMAGES_DIR):
        logger.error(f"Images directory not found: {IMAGES_DIR}")
        return []
    
    images = [f for f in os.listdir(IMAGES_DIR) if f.endswith(('.jpg', '.jpeg', '.png')) and os.path.isfile(os.path.join(IMAGES_DIR, f))]
    images.sort()
    return images

def copy_image_to_local_s3(image_file, product_id=None):
    """Copy a product image to local S3 storage"""
    image_path = os.path.join(IMAGES_DIR, image_file)
    if not os.path.exists(image_path):
        logger.error(f"Image not found: {image_path}")
        return None
    
    # If no product ID is provided, use a dummy ID
    if product_id is None:
        product_id = str(uuid.uuid4())
    
    # Create folder for product
    product_dir = os.path.join(LOCAL_S3_DIR, BUCKET_NAME, "products", str(product_id))
    os.makedirs(product_dir, exist_ok=True)
    
    # Generate a unique filename
    file_extension = os.path.splitext(image_path)[1].lower()
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # Copy the file
    target_path = os.path.join(product_dir, unique_filename)
    try:
        shutil.copy2(image_path, target_path)
        logger.info(f"Image copied to {target_path}")
        
        # Return URL path that would be used in the application
        relative_path = f"products/{product_id}/{unique_filename}"
        url = f"http://localhost:3001/local_s3/{BUCKET_NAME}/{relative_path}"
        return url
    except Exception as e:
        logger.error(f"Failed to copy image: {str(e)}")
        return None

def copy_all_sample_images():
    """Copy all sample images to local S3 storage with different product IDs"""
    products_dir = setup_local_s3()
    images = list_images()
    
    if not images:
        logger.warning("No images found to copy")
        return []
    
    # Sample product base names to use (to avoid using all images)
    sample_base_names = [
        "classic-white-tshirt",
        "black-hoodie",
        "custom-mug",
        "canvas-tote",
        "phone-case",
        "laptop-sleeve"
    ]
    
    results = []
    for i, base_name in enumerate(sample_base_names):
        # Find the actual file that matches this pattern
        matching_files = [img for img in images if img.startswith(base_name) and not '-large-' in img and not '-thumbnail-' in img]
        
        if not matching_files:
            logger.warning(f"No matching files for {base_name}")
            continue
            
        # Use the base image file (without size suffixes)
        base_image = next((img for img in matching_files if img == f"{base_name}.jpg"), matching_files[0])
        
        product_id = i + 1  # Simple numeric IDs
        url = copy_image_to_local_s3(base_image, product_id)
        if url:
            results.append({
                "product_id": product_id,
                "image": base_image,
                "url": url
            })
    
    logger.info(f"Copied {len(results)} images to local S3 storage")
    return results

if __name__ == "__main__":
    logger.info("Starting local S3 initialization")
    setup_local_s3()
    
    results = copy_all_sample_images()
    
    print("\nLocal S3 Initialization Complete")
    print("=================================")
    print(f"Local S3 directory: {LOCAL_S3_DIR}")
    print(f"Bucket name: {BUCKET_NAME}")
    print(f"Copied {len(results)} sample images to local S3")
    
    for result in results:
        print(f"Product ID: {result['product_id']}, Image: {result['image']}, URL: {result['url']}")
    
    print("\nSetup complete!") 