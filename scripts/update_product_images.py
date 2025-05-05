#!/usr/bin/env python3
import os
import sys
import logging
import glob

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

# Define local S3 storage path
LOCAL_S3_PATH = os.path.join(backend_dir, "local_s3_storage", "okyke-files", "products")

def main():
    """
    Update product images in the database to match what's in local_s3_storage
    """
    logger.info("Starting product image update")
    
    # Create database session
    db = SessionLocal()
    try:
        # Get all products
        products = db.query(Product).all()
        logger.info(f"Found {len(products)} products in the database")
        
        # First, set all featured_image_id to NULL to avoid foreign key constraint violations
        for product in products:
            product.featured_image_id = None
        
        db.commit()
        logger.info("Cleared all featured image references")
        
        products_updated = 0
        
        # Process each product
        for product in products:
            product_id = product.id
            product_image_dir = os.path.join(LOCAL_S3_PATH, str(product_id))
            
            if not os.path.exists(product_image_dir):
                logger.warning(f"No image directory found for product {product_id}")
                continue
                
            # Get image files in the product directory
            image_files = glob.glob(os.path.join(product_image_dir, "*.jpg"))
            image_files.extend(glob.glob(os.path.join(product_image_dir, "*.png")))
            image_files.extend(glob.glob(os.path.join(product_image_dir, "*.jpeg")))
            
            if not image_files:
                logger.warning(f"No image files found for product {product_id}")
                continue
                
            logger.info(f"Found {len(image_files)} images for product {product_id}")
            
            # Clear existing images for this product
            db.query(ProductImage).filter(ProductImage.product_id == product_id).delete()
            
            # Add new images
            for i, image_file in enumerate(image_files):
                # Get just the filename without path
                filename = os.path.basename(image_file)
                
                # Create image URL based on local S3 storage structure
                image_url = f"/local_s3/okyke-files/products/{product_id}/{filename}"
                
                # Create new image
                product_image = ProductImage(
                    product_id=product_id,
                    url=image_url,
                    alt_text=f"{product.name} image {i+1}",
                    position=i
                )
                
                db.add(product_image)
                logger.info(f"Added image {filename} for product {product_id}")
                
            products_updated += 1
            
        # Commit changes to get IDs for new images
        db.commit()
        
        # Update featured images now that we have IDs
        for product in products:
            product_id = product.id
            
            # Get the first image for this product (position 0)
            first_image = db.query(ProductImage).filter(
                ProductImage.product_id == product_id,
                ProductImage.position == 0
            ).first()
            
            if first_image:
                product.featured_image_id = first_image.id
                db.add(product)
                logger.info(f"Updated featured image for product {product_id}")
        
        # Commit the featured image updates
        db.commit()
        
        logger.info(f"Update complete. Updated images for {products_updated} products.")
        
        # Print current state
        for product in db.query(Product).all():
            img_count = db.query(ProductImage).filter(ProductImage.product_id == product.id).count()
            featured_img = "Yes" if product.featured_image_id else "No"
            print(f"Product {product.id}: {product.name} - {img_count} images, Featured image: {featured_img}")
            
    except Exception as e:
        logger.error(f"Error during update: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main() 