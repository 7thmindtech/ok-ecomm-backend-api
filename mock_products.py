#!/usr/bin/env python3
import os
import json
import random
import datetime
import uuid
from pathlib import Path

# Configuration
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../admin_portal/public/mocks")
LOCAL_S3_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "local_s3_storage")
BUCKET_NAME = "okyke-files"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Sample product data
SAMPLE_PRODUCTS = [
    {
        "name": "Classic White T-Shirt",
        "description": "A comfortable, classic white t-shirt made from premium cotton.",
        "price": 29.99,
        "stock": 150,
        "category_id": 1,
        "is_featured": True,
        "status": "published",
        "specifications": {
            "material": "100% Cotton",
            "care": "Machine wash cold"
        },
        "colors": ["White"],
        "image_base": "classic-white-tshirt"
    },
    {
        "name": "Black Hoodie",
        "description": "A warm, comfortable black hoodie perfect for casual wear.",
        "price": 49.99,
        "stock": 100,
        "category_id": 1,
        "is_featured": True,
        "status": "published",
        "specifications": {
            "material": "80% Cotton, 20% Polyester",
            "care": "Machine wash cold"
        },
        "colors": ["Black"],
        "image_base": "black-hoodie"
    },
    {
        "name": "Custom Mug",
        "description": "A personalized ceramic mug, perfect for your morning coffee or tea.",
        "price": 19.99,
        "stock": 75,
        "category_id": 2,
        "is_featured": False,
        "status": "published",
        "specifications": {
            "material": "Ceramic",
            "capacity": "11 oz"
        },
        "is_customizable": True,
        "image_base": "custom-mug"
    },
    {
        "name": "Canvas Tote Bag",
        "description": "A durable canvas tote bag for everyday use.",
        "price": 24.99,
        "stock": 120,
        "category_id": 2,
        "is_featured": False,
        "status": "published",
        "specifications": {
            "material": "100% Cotton Canvas",
            "dimensions": "15\" x 16\" x 4\""
        },
        "image_base": "canvas-tote"
    },
    {
        "name": "Phone Case",
        "description": "A durable, stylish phone case with custom artwork.",
        "price": 29.99,
        "stock": 90,
        "category_id": 2,
        "is_featured": True,
        "status": "published",
        "specifications": {
            "material": "Hard Plastic",
            "compatibility": "iPhone/Android models"
        },
        "is_customizable": True,
        "image_base": "phone-case"
    },
    {
        "name": "Laptop Sleeve",
        "description": "A protective sleeve for laptops with unique artistic designs.",
        "price": 39.99,
        "stock": 60,
        "category_id": 2,
        "is_featured": False,
        "status": "published",
        "specifications": {
            "material": "Neoprene",
            "sizes": ["13\"", "15\"", "17\""]
        },
        "image_base": "laptop-sleeve"
    }
]

# Sample categories
SAMPLE_CATEGORIES = [
    {
        "id": 1,
        "name": "Clothing",
        "description": "Clothing items including t-shirts, hoodies, and more",
        "slug": "clothing",
        "is_active": True,
        "parent_id": None
    },
    {
        "id": 2,
        "name": "Accessories",
        "description": "Various accessories like phone cases, mugs, and bags",
        "slug": "accessories",
        "is_active": True,
        "parent_id": None
    }
]

def generate_mock_products(num_products=6):
    """Generate mock product data based on sample products"""
    products = []
    
    # Use provided samples first
    for i, sample in enumerate(SAMPLE_PRODUCTS[:num_products]):
        product_id = i + 1
        
        # Generate timestamps
        now = datetime.datetime.now()
        created_at = (now - datetime.timedelta(days=random.randint(1, 30))).isoformat()
        updated_at = (now - datetime.timedelta(days=random.randint(0, 5))).isoformat()
        
        # Find any local S3 image for this product
        product_s3_dir = os.path.join(LOCAL_S3_DIR, BUCKET_NAME, "products", str(product_id))
        image_url = None
        if os.path.exists(product_s3_dir):
            image_files = [f for f in os.listdir(product_s3_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
            if image_files:
                relative_path = f"products/{product_id}/{image_files[0]}"
                image_url = f"http://localhost:3001/local_s3/{BUCKET_NAME}/{relative_path}"
        
        # If no S3 image found, use public image
        if not image_url:
            image_url = f"/images/products/{sample['image_base']}.jpg"
        
        # Create product object
        product = {
            "id": product_id,
            "name": sample["name"],
            "description": sample["description"],
            "price": sample["price"],
            "discount_price": sample["price"] * 0.9 if random.random() > 0.7 else None,
            "stock": sample["stock"],
            "category_id": sample["category_id"],
            "artist_id": 1,  # Admin user as artist
            "slug": sample["name"].lower().replace(" ", "-"),
            "status": sample["status"],
            "featured_image_url": image_url,
            "is_featured": sample.get("is_featured", False),
            "is_customizable": sample.get("is_customizable", False),
            "specifications": sample.get("specifications", {}),
            "colors": sample.get("colors", []),
            "created_at": created_at,
            "updated_at": updated_at,
            "sales_count": random.randint(0, 500),
            "low_stock_threshold": 10
        }
        
        products.append(product)
    
    return products

def generate_categories():
    """Generate mock category data"""
    # Add timestamps to categories
    now = datetime.datetime.now()
    
    categories = []
    for category in SAMPLE_CATEGORIES:
        created_at = (now - datetime.timedelta(days=random.randint(30, 60))).isoformat()
        updated_at = created_at
        
        category_copy = category.copy()
        category_copy["created_at"] = created_at
        category_copy["updated_at"] = updated_at
        categories.append(category_copy)
    
    return categories

def save_mock_data(products, categories):
    """Save mock data to JSON files"""
    # Save products
    products_file = os.path.join(OUTPUT_DIR, "products.json")
    with open(products_file, 'w') as f:
        json.dump(products, f, indent=2)
    print(f"Saved {len(products)} mock products to {products_file}")
    
    # Save categories
    categories_file = os.path.join(OUTPUT_DIR, "categories.json")
    with open(categories_file, 'w') as f:
        json.dump(categories, f, indent=2)
    print(f"Saved {len(categories)} mock categories to {categories_file}")

if __name__ == "__main__":
    print("Generating mock product data...")
    
    # Ensure the mocks directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Generate and save mock data
    products = generate_mock_products()
    categories = generate_categories()
    save_mock_data(products, categories)
    
    print("\nMock data generation complete!")
    print(f"Mock data saved to: {OUTPUT_DIR}") 