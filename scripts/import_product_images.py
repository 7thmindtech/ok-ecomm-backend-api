#!/usr/bin/env python3
import os
import sys
import logging
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from app.db.session import SessionLocal
from app.models.models import Product, ProductImage
from sqlalchemy.orm import Session

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Local S3 storage configuration
LOCAL_STORAGE_DIR = os.path.join(backend_dir, "local_s3_storage")
PRODUCTS_DIR = os.path.join(LOCAL_STORAGE_DIR, "okyke-files", "products")
BASE_URL = "http://localhost:3002/local_s3"  # Base URL for accessing the files

def get_image_files(product_id):
    """Get all image files for a product from local S3 storage"""
    product_dir = os.path.join(PRODUCTS_DIR, str(product_id))
    
    if not os.path.exists(product_dir):
        logger.warning(f"Product directory not found: {product_dir}")
        return []
    
    image_files = []
    for file_name in os.listdir(product_dir):
        if file_name.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')) and not file_name.startswith('.'):
            file_path = os.path.join(product_dir, file_name)
            if os.path.isfile(file_path):
                image_files.append(file_name)
    
    return image_files

def import_images_for_product(db: Session, product_id: int):
    """Import all images for a product into the database"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        logger.error(f"Product ID {product_id} not found in the database")
        return False
    
    # Get image files from storage directory
    image_files = get_image_files(product_id)
    if not image_files:
        logger.warning(f"No image files found for product ID {product_id}")
        return False
    
    logger.info(f"Found {len(image_files)} images for product ID {product_id}")
    
    # Check if product already has images in the database
    existing_images = db.query(ProductImage).filter(ProductImage.product_id == product_id).all()
    if existing_images:
        logger.info(f"Product ID {product_id} already has {len(existing_images)} images in the database")
    
    # Import each image
    position = len(existing_images)
    images_added = 0
    
    for file_name in image_files:
        # Create URL that matches the format expected by the API endpoint
        url = f"{BASE_URL}/okyke-files/products/{product_id}/{file_name}"
        
        # Check if this image already exists in the database
        existing_image = db.query(ProductImage).filter(
            ProductImage.product_id == product_id,
            ProductImage.url == url
        ).first()
        
        if existing_image:
            logger.info(f"Image already exists in database: {url}")
            continue
        
        # Create new ProductImage record
        new_image = ProductImage(
            product_id=product_id,
            url=url,
            alt_text=f"{product.name} image {position + 1}",
            position=position
        )
        
        db.add(new_image)
        position += 1
        images_added += 1
    
    if images_added > 0:
        # Set the first image as featured image if not already set
        if not product.featured_image_id and images_added > 0:
            first_image = db.query(ProductImage).filter(
                ProductImage.product_id == product_id
            ).order_by(ProductImage.position).first()
            
            if first_image:
                product.featured_image_id = first_image.id
                logger.info(f"Set featured image for product ID {product_id} to image ID {first_image.id}")
        
        db.commit()
        logger.info(f"Added {images_added} new images for product ID {product_id}")
        return True
    
    return False

def main():
    """Main function to import all product images"""
    logger.info("Starting product image import")
    
    # Get all product directories from storage
    product_dirs = []
    if os.path.exists(PRODUCTS_DIR):
        product_dirs = [d for d in os.listdir(PRODUCTS_DIR) if os.path.isdir(os.path.join(PRODUCTS_DIR, d))]
    else:
        logger.error(f"Products directory not found: {PRODUCTS_DIR}")
        return
    
    logger.info(f"Found {len(product_dirs)} product directories")
    
    # Create database session
    db = SessionLocal()
    try:
        # Get all products from database
        products = db.query(Product).all()
        logger.info(f"Found {len(products)} products in the database")
        
        products_updated = 0
        
        # Import images for each product
        for product in products:
            product_id = product.id
            logger.info(f"Processing product ID {product_id}: {product.name}")
            
            if str(product_id) in product_dirs:
                if import_images_for_product(db, product_id):
                    products_updated += 1
            else:
                logger.warning(f"No directory found for product ID {product_id}")
        
        logger.info(f"Import complete. Updated {products_updated} products with images.")
        
    except Exception as e:
        logger.error(f"Error during import: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main() 