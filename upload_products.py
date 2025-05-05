#!/usr/bin/env python3
import os
import sys
import requests
import json
from pathlib import Path
import time
import shutil

# Configuration
API_URL = "http://127.0.0.1:8888/api/v1"
ADMIN_USERNAME = "admin@okyke.com"
ADMIN_PASSWORD = "Admin123!"
IMAGES_DIR = "../frontend/public/images/products"
STORAGE_DIR = "local_s3_storage/okyke-files/products"

# Product definitions
PRODUCTS = [
    {
        "name": "Classic White T-Shirt",
        "description": "A comfortable, classic white t-shirt made from premium cotton.",
        "price": 29.99,
        "stock": 150,
        "category_name": "Clothing",
        "image_file": "classic-white-tshirt-large.jpg",
        "status": "published",
        "specifications": {
            "material": "100% Cotton",
            "care": "Machine wash cold"
        },
        "colors": ["White"],
        "is_featured": True
    },
    {
        "name": "Black Hoodie",
        "description": "A warm, comfortable black hoodie perfect for casual wear.",
        "price": 49.99,
        "stock": 100,
        "category_name": "Clothing",
        "image_file": "sweatshirt.jpg",
        "status": "published",
        "specifications": {
            "material": "80% Cotton, 20% Polyester",
            "care": "Machine wash cold"
        },
        "colors": ["Black"],
        "is_featured": True
    },
    {
        "name": "Custom Mug",
        "description": "A personalized ceramic mug, perfect for your morning coffee or tea.",
        "price": 19.99,
        "stock": 75,
        "category_name": "Accessories",
        "image_file": "custom-mug-large.jpg",
        "status": "published",
        "specifications": {
            "material": "Ceramic",
            "capacity": "11 oz"
        },
        "is_customizable": True
    },
    {
        "name": "Canvas Tote Bag",
        "description": "A durable canvas tote bag for everyday use.",
        "price": 24.99,
        "stock": 120,
        "category_name": "Accessories",
        "image_file": "canvas-tote-large.jpg",
        "status": "published",
        "specifications": {
            "material": "100% Cotton Canvas",
            "dimensions": "15\" x 16\" x 4\""
        }
    },
    {
        "name": "Phone Case",
        "description": "A durable, stylish phone case with custom artwork.",
        "price": 29.99,
        "stock": 90,
        "category_name": "Accessories",
        "image_file": "phone-case-large.jpg",
        "status": "published",
        "specifications": {
            "material": "Hard Plastic",
            "compatibility": "iPhone/Android models"
        },
        "is_customizable": True
    },
    {
        "name": "Laptop Sleeve",
        "description": "A protective sleeve for laptops with unique artistic designs.",
        "price": 39.99,
        "stock": 60,
        "category_name": "Accessories",
        "image_file": "laptop-sleeve-large.jpg",
        "status": "published",
        "specifications": {
            "material": "Neoprene",
            "sizes": ["13\"", "15\"", "17\""]
        }
    }
]

def login():
    """Authenticate and get access token"""
    print("Logging in...")
    response = requests.post(
        f"{API_URL}/auth/login-alt",
        data={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}
    )
    
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        sys.exit(1)
    
    return response.json()["access_token"]

def get_or_create_category(name, description, max_retries=3):
    """Get or create a category with fresh token and retries"""
    for attempt in range(max_retries):
        # Get a fresh token for each attempt
        token = login()
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to find existing category
        try:
            response = requests.get(f"{API_URL}/categories", headers=headers)
            if response.status_code == 200:
                categories = response.json()
                for category in categories:
                    if category["name"].lower() == name.lower():
                        print(f"Found existing category: {name}")
                        return category["id"]
            
            # Create a new category
            print(f"Creating new category: {name}")
            data = {
                "name": name,
                "description": description,
                "is_active": True
            }
            
            response = requests.post(
                f"{API_URL}/categories",
                headers=headers,
                json=data  # Changed from data to json for proper JSON formatting
            )
            
            if response.status_code == 200 or response.status_code == 201:
                new_category = response.json()
                print(f"Created new category: {name} with ID: {new_category['id']}")
                return new_category["id"]
            else:
                print(f"Attempt {attempt+1}/{max_retries} failed: {response.text}")
        except Exception as e:
            print(f"Attempt {attempt+1}/{max_retries} error: {str(e)}")
    
    print(f"Failed to create category after {max_retries} attempts")
    return None

def create_product(product_data, category_id, max_retries=3):
    """Create a product with fresh token and retries"""
    for attempt in range(max_retries):
        # Get a fresh token for each attempt
        token = login()
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            # Prepare product payload
            payload = {
                "name": product_data["name"],
                "description": product_data["description"],
                "price": product_data["price"],
                "stock": product_data["stock"],
                "category_id": category_id,
                "artist_id": 1,  # Assuming admin user is the artist
                "status": product_data.get("status", "draft"),
                "specifications": product_data.get("specifications", {}),
                "colors": product_data.get("colors", []),
                "is_featured": product_data.get("is_featured", False),
                "is_customizable": product_data.get("is_customizable", False),
                "low_stock_threshold": 10
            }
            
            print(f"Creating product: {product_data['name']}")
            response = requests.post(
                f"{API_URL}/products",
                headers=headers,
                json=payload
            )
            
            if response.status_code in (200, 201):
                new_product = response.json()
                print(f"Created product {new_product['name']} with ID {new_product['id']}")
                return new_product["id"]
            
            print(f"Attempt {attempt+1}/{max_retries} failed: {response.text}")
            time.sleep(1)
        except Exception as e:
            print(f"Error in attempt {attempt+1}/{max_retries}: {str(e)}")
            time.sleep(1)
    
    print(f"Failed to create product after {max_retries} attempts")
    return None

def upload_product_image(product_id, image_path, is_featured=True, max_retries=3):
    """Upload a product image to the local S3 storage"""
    if not os.path.exists(image_path):
        print(f"Image not found: {image_path}")
        return None
    
    print(f"Processing image for product ID {product_id}: {image_path}")
    
    # Copy the image to local S3 storage
    image_file = os.path.basename(image_path)
    file_url = copy_image_to_storage(image_file, product_id)
    
    if not file_url:
        print(f"Failed to copy image to storage directory")
        return None
    
    # With real API, we would upload to server with a fresh token:
    for attempt in range(max_retries):
        token = login()
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            # Create a product image record
            payload = {
                "product_id": product_id,
                "image_url": file_url,
                "is_featured": is_featured
            }
            
            response = requests.post(
                f"{API_URL}/products/{product_id}/images",
                headers=headers,
                json=payload
            )
            
            if response.status_code in (200, 201):
                new_image = response.json()
                print(f"Created product image with ID {new_image['id']} at {file_url}")
                return new_image["id"]
            
            print(f"Attempt {attempt+1}/{max_retries} failed: {response.text}")
            time.sleep(1)
        except Exception as e:
            print(f"Error in attempt {attempt+1}/{max_retries}: {str(e)}")
            time.sleep(1)
    
    print(f"Failed to process image after {max_retries} attempts")
    return None

def copy_image_to_storage(image_file, product_id):
    """Copy image to the local S3 storage directory"""
    source_path = os.path.join(IMAGES_DIR, image_file)
    storage_dir = os.path.join(STORAGE_DIR, str(product_id))
    
    if not os.path.exists(source_path):
        print(f"Source image not found: {source_path}")
        return None
    
    # Create storage directory if it doesn't exist
    os.makedirs(storage_dir, exist_ok=True)
    
    # Copy the file
    dest_path = os.path.join(storage_dir, image_file)
    shutil.copy2(source_path, dest_path)
    print(f"Copied image from {source_path} to {dest_path}")
    
    # Return the relative URL
    return f"/local_s3/okyke-files/products/{product_id}/{image_file}"

def main():
    """Main function to upload products"""
    # Create categories
    categories = {
        "Clothing": "Clothing items including t-shirts, hoodies, and more",
        "Accessories": "Various accessories like phone cases, mugs, and bags"
    }
    
    category_ids = {}
    for name, description in categories.items():
        category_ids[name] = get_or_create_category(name, description)
    
    # Create products and upload images
    for product_data in PRODUCTS:
        # Get category ID
        category_name = product_data["category_name"]
        if category_name not in category_ids or not category_ids[category_name]:
            print(f"Category not found: {category_name}")
            continue
        
        # Create product
        product_id = create_product(product_data, category_ids[category_name])
        if not product_id:
            continue
        
        # Upload image
        image_path = os.path.join(IMAGES_DIR, product_data["image_file"])
        upload_product_image(product_id, image_path)
        
        # Sleep briefly to avoid overwhelming the server
        time.sleep(0.5)
    
    print("Product upload completed successfully!")

if __name__ == "__main__":
    main() 