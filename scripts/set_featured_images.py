#!/usr/bin/env python3
import os
import sys
import logging

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

def main():
    """
    Set featured images for all products that don't have one
    """
    logger.info("Starting featured image setter")
    
    # Create database session
    db = SessionLocal()
    try:
        # Get all products from database
        products = db.query(Product).all()
        logger.info(f"Found {len(products)} products in the database")
        
        products_updated = 0
        products_with_featured_image = 0
        
        # Process each product
        for product in products:
            if product.featured_image_id is not None:
                logger.info(f"Product {product.id}: {product.name} already has featured image ID {product.featured_image_id}")
                products_with_featured_image += 1
                continue
                
            # Get first image for this product
            first_image = db.query(ProductImage).filter(
                ProductImage.product_id == product.id
            ).order_by(ProductImage.position).first()
            
            if first_image:
                product.featured_image_id = first_image.id
                db.add(product)
                logger.info(f"Set featured image for product ID {product.id} to image ID {first_image.id}")
                products_updated += 1
            else:
                logger.warning(f"No images found for product ID {product.id}")
        
        db.commit()
        logger.info(f"Update complete. Set featured images for {products_updated} products.")
        logger.info(f"Total products with featured images: {products_with_featured_image + products_updated}")
        
        # Print current state
        for product in db.query(Product).all():
            print(f"Product {product.id}: {product.name}, featured_image_id: {product.featured_image_id}")
            
    except Exception as e:
        logger.error(f"Error during update: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main() 