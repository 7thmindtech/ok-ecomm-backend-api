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
    Mark specific products as customizable
    """
    logger.info("Starting product customization update")
    
    # Create database session
    db = SessionLocal()
    try:
        # Get all products from database
        products = db.query(Product).all()
        logger.info(f"Found {len(products)} products in the database")
        
        # List of products to make customizable (by name)
        customizable_products = [
            "Custom Mug",  # Already has "Custom" in the name
            "T-Shirt",     # Apparel is typically customizable
            "Canvas Tote Bag"  # Good for custom printing
        ]
        
        products_updated = 0
        
        # Process each product
        for product in products:
            should_customize = any(custom_name in product.name for custom_name in customizable_products)
            
            if should_customize and not product.is_customizable:
                product.is_customizable = True
                
                # Add customization options JSON if not already present
                if not product.customization_options:
                    product.customization_options = {
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
                            "enabled": "Mug" not in product.name,  # Only for non-mug products
                            "options": ["S", "M", "L", "XL", "XXL"]
                        },
                        "image_upload": {
                            "enabled": True,
                            "max_size_mb": 5,
                            "formats": ["jpg", "png", "gif"]
                        }
                    }
                
                db.add(product)
                logger.info(f"Marked product '{product.name}' as customizable")
                products_updated += 1
        
        db.commit()
        logger.info(f"Update complete. Made {products_updated} products customizable.")
        
        # Print current state
        for product in db.query(Product).all():
            status = "✓ CUSTOMIZABLE" if product.is_customizable else "STANDARD"
            print(f"Product {product.id}: {product.name} - {status}")
            
    except Exception as e:
        logger.error(f"Error during update: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main() 