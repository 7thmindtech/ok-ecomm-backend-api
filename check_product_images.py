#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

# Import SQLAlchemy models
from app.db.session import SessionLocal
from app.models.models import Product, ProductImage
from sqlalchemy.orm import Session

def check_products_without_images():
    """Check for products without any images and provide option to delete them"""
    db = SessionLocal()
    
    try:
        # Find products with no images in the ProductImage table
        products_without_images = db.query(Product).filter(
            ~Product.id.in_(db.query(ProductImage.product_id).distinct())
        ).all()
        
        # Also check for products with empty featured_image_url
        products_empty_featured_url = db.query(Product).filter(
            (Product.featured_image_url.is_(None) | 
             (Product.featured_image_url == ""))
        ).all()
        
        print(f"Found {len(products_without_images)} products with no images in ProductImage table:")
        for product in products_without_images:
            print(f"ID: {product.id}, Name: {product.name}, Featured URL: {product.featured_image_url}")
        
        print(f"\nFound {len(products_empty_featured_url)} products with empty featured_image_url:")
        for product in products_empty_featured_url:
            print(f"ID: {product.id}, Name: {product.name}")
        
        # Ask to delete these products
        all_problem_products = list(set(products_without_images + products_empty_featured_url))
        if all_problem_products:
            choice = input("\nDo you want to delete all products without images? (y/n): ")
            if choice.lower() == 'y':
                for product in all_problem_products:
                    print(f"Deleting product: {product.id} - {product.name}")
                    db.delete(product)
                db.commit()
                print(f"Deleted {len(all_problem_products)} products without images.")
            else:
                print("No products were deleted.")
        else:
            print("All products have images.")
    
    finally:
        db.close()

if __name__ == "__main__":
    check_products_without_images() 