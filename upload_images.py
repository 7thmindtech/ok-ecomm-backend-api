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

def login():
    """Login and get access token"""
    try:
        response = requests.post(
            f"{API_URL}/auth/login-alt",
            data={
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD
            }
        )
        
        if response.status_code == 200:
            token = response.json()["access_token"]
            print("Successfully logged in")
            return token
        
        print(f"Login failed: {response.text}")
        return None
    except Exception as e:
        print(f"Error during login: {str(e)}")
        return None

def get_product_by_name(name, token):
    """Get product ID by name"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{API_URL}/products",
            headers=headers,
            params={"search": name}
        )
        
        if response.status_code == 200:
            products = response.json()["items"]
            for product in products:
                if product["name"].lower() == name.lower():
                    return product["id"]
        
        print(f"Product not found: {name}")
        return None
    except Exception as e:
        print(f"Error getting product: {str(e)}")
        return None

def upload_product_image(product_id, image_path, token, is_featured=True):
    """Upload a product image"""
    if not os.path.exists(image_path):
        print(f"Image not found: {image_path}")
        return None
    
    print(f"Uploading image for product ID {product_id}: {image_path}")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        with open(image_path, "rb") as img_file:
            files = {
                "file": (os.path.basename(image_path), img_file, "image/jpeg")
            }
            data = {
                "is_featured": str(is_featured).lower(),
                "alt_text": f"Product image for {product_id}"
            }
            
            response = requests.post(
                f"{API_URL}/products/{product_id}/images",
                headers=headers,
                files=files,
                data=data
            )
            
            if response.status_code in (200, 201):
                image_data = response.json()
                print(f"Successfully uploaded image with ID {image_data['id']}")
                return image_data["id"]
            
            print(f"Failed to upload image: {response.text}")
            return None
    except Exception as e:
        print(f"Error uploading image: {str(e)}")
        return None

def main():
    """Main function to upload product images"""
    # Product definitions with their image files
    products = [
        {
            "id": 1,
            "name": "Classic White T-Shirt",
            "image_file": "classic-white-tshirt-large.jpg"
        },
        {
            "id": 2,
            "name": "Black Hoodie",
            "image_file": "sweatshirt.jpg"
        },
        {
            "id": 3,
            "name": "Custom Mug",
            "image_file": "custom-mug-large.jpg"
        },
        {
            "id": 4,
            "name": "Canvas Tote Bag",
            "image_file": "canvas-tote-large.jpg"
        },
        {
            "id": 5,
            "name": "Phone Case",
            "image_file": "phone-case-large.jpg"
        },
        {
            "id": 6,
            "name": "Laptop Sleeve",
            "image_file": "laptop-sleeve-large.jpg"
        }
    ]
    
    # Login
    token = login()
    if not token:
        print("Failed to login")
        sys.exit(1)
    
    # Upload images for each product
    for product_data in products:
        # Upload image
        image_path = os.path.join(IMAGES_DIR, product_data["image_file"])
        image_id = upload_product_image(product_data["id"], image_path, token)
        
        if image_id:
            print(f"Successfully uploaded image for {product_data['name']}")
        else:
            print(f"Failed to upload image for {product_data['name']}")
        
        # Sleep briefly to avoid overwhelming the server
        time.sleep(0.5)
    
    print("Image upload completed!")

if __name__ == "__main__":
    main() 