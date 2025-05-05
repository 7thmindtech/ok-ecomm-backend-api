#!/usr/bin/env python3
from app.db.session import SessionLocal
from app.models.models import Category, Product, ProductStatus, ProductImage
from app.utils.slugify import slugify
from datetime import datetime
import os
from pathlib import Path

# Configure database session
db = SessionLocal()

# Define categories
CATEGORIES = [
    {
        "name": "T-Shirts",
        "description": "Comfortable cotton t-shirts in various colors and designs"
    },
    {
        "name": "Hoodies",
        "description": "Warm and stylish hoodies for all seasons"
    },
    {
        "name": "Phone Cases",
        "description": "Protective and attractive phone cases for various models"
    },
    {
        "name": "Mugs",
        "description": "Ceramic mugs for your favorite beverages"
    },
    {
        "name": "Laptop Accessories",
        "description": "Accessories to enhance your laptop experience"
    },
    {
        "name": "Tote Bags",
        "description": "Durable and eco-friendly tote bags"
    }
]

# Define products
PRODUCTS = [
    {
        "name": "Classic White T-Shirt",
        "description": "A comfortable, classic white t-shirt made from premium cotton.",
        "price": 29.99,
        "stock": 150,
        "category_name": "T-Shirts",
        "status": ProductStatus.PUBLISHED,
        "is_featured": True
    },
    {
        "name": "Black Hoodie",
        "description": "A warm, comfortable black hoodie perfect for casual wear.",
        "price": 49.99,
        "stock": 100,
        "category_name": "Hoodies",
        "status": ProductStatus.PUBLISHED,
        "is_featured": True
    },
    {
        "name": "Custom Mug",
        "description": "A personalized ceramic mug, perfect for your morning coffee or tea.",
        "price": 19.99,
        "stock": 200,
        "category_name": "Mugs",
        "status": ProductStatus.PUBLISHED,
        "is_featured": True
    },
    {
        "name": "iPhone Case",
        "description": "A durable, stylish case for your iPhone that offers excellent protection.",
        "price": 24.99,
        "stock": 120,
        "category_name": "Phone Cases",
        "status": ProductStatus.PUBLISHED,
        "is_featured": True
    },
    {
        "name": "Laptop Sleeve",
        "description": "Protect your laptop with this padded sleeve featuring a sleek design.",
        "price": 39.99,
        "stock": 80,
        "category_name": "Laptop Accessories",
        "status": ProductStatus.PUBLISHED,
        "is_featured": True
    },
    {
        "name": "Canvas Tote Bag",
        "description": "A spacious, eco-friendly tote bag perfect for shopping or daily use.",
        "price": 29.99,
        "stock": 100,
        "category_name": "Tote Bags",
        "status": ProductStatus.PUBLISHED,
        "is_featured": True
    }
]

def create_categories():
    """Create categories in the database"""
    print("Creating categories...")
    category_map = {}
    
    for cat_data in CATEGORIES:
        # Check if category exists
        existing_category = db.query(Category).filter(Category.name == cat_data["name"]).first()
        if existing_category:
            print(f"Category '{cat_data['name']}' already exists with ID {existing_category.id}")
            category_map[cat_data["name"]] = existing_category
            continue
        
        # Create new category
        new_category = Category(
            name=cat_data["name"],
            description=cat_data["description"],
            slug=slugify(cat_data["name"]),
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
        
        print(f"Created category '{new_category.name}' with ID {new_category.id}")
        category_map[new_category.name] = new_category
    
    return category_map

def create_products(category_map):
    """Create products in the database"""
    print("\nCreating products...")
    
    for prod_data in PRODUCTS:
        # Check if product exists
        existing_product = db.query(Product).filter(Product.name == prod_data["name"]).first()
        if existing_product:
            print(f"Product '{prod_data['name']}' already exists with ID {existing_product.id}")
            continue
        
        # Get category
        category = category_map.get(prod_data["category_name"])
        if not category:
            print(f"Category '{prod_data['category_name']}' not found, skipping product '{prod_data['name']}'")
            continue
        
        # Create new product
        new_product = Product(
            name=prod_data["name"],
            description=prod_data["description"],
            price=prod_data["price"],
            stock=prod_data["stock"],
            category_id=category.id,
            status=prod_data["status"],
            slug=slugify(prod_data["name"]),
            is_featured=prod_data.get("is_featured", False),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            published_at=datetime.now() if prod_data["status"] == ProductStatus.PUBLISHED else None
        )
        
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        
        print(f"Created product '{new_product.name}' with ID {new_product.id}")

if __name__ == "__main__":
    try:
        # Create categories and get mapping
        category_map = create_categories()
        
        # Create products using the category mapping
        create_products(category_map)
        
        print("\nProduct creation completed successfully!")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        db.close() 