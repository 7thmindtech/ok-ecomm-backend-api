#!/usr/bin/env python3
import os
import sys
import logging

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from app.db.session import SessionLocal
from app.models.models import Product
from sqlalchemy.orm import Session

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """
    Make the Black Hoodie customizable
    """
    logger.info("Starting hoodie customization update")
    
    # Create database session
    db = SessionLocal()
    try:
        # Get the Black Hoodie product
        black_hoodie = db.query(Product).filter(Product.name == "Black Hoodie").first()
        
        if not black_hoodie:
            logger.error("Black Hoodie product not found")
            return
            
        logger.info(f"Found Black Hoodie product (ID: {black_hoodie.id})")
        
        # Make the product customizable
        black_hoodie.is_customizable = True
        
        # Add customization options JSON if not already present
        if not black_hoodie.customization_options:
            black_hoodie.customization_options = {
                "text": {
                    "enabled": True,
                    "max_length": 50,
                    "available_fonts": ["Arial", "Helvetica", "Times New Roman", "Roboto", "Comic Sans MS"]
                },
                "color": {
                    "enabled": True,
                    "options": ["Black", "White", "Red", "Blue", "Green", "Purple", "Yellow"]
                },
                "size": {
                    "enabled": True,
                    "options": ["S", "M", "L", "XL", "XXL"]
                },
                "image_upload": {
                    "enabled": True,
                    "max_size_mb": 5,
                    "formats": ["jpg", "png", "gif"]
                }
            }
        
        db.add(black_hoodie)
        db.commit()
        logger.info(f"Updated Black Hoodie (ID: {black_hoodie.id}) to be customizable")
        
        # Print current state
        product = db.query(Product).filter(Product.id == black_hoodie.id).first()
        status = "✓ CUSTOMIZABLE" if product.is_customizable else "STANDARD"
        print(f"Product {product.id}: {product.name} - {status}")
            
    except Exception as e:
        logger.error(f"Error during update: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main() 