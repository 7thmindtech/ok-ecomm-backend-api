import requests
import json
import time
import os
import sys
from pathlib import Path

API_URL = "http://127.0.0.1:8888/api/v1"

def login() -> str:
    """Login to get authentication token"""
    response = requests.post(
        f"{API_URL}/auth/login-alt",
        data={
            "username": "admin@example.com",
            "password": "admin123"
        }
    )
    print(f"Login response status: {response.status_code}")
    print(f"Login response body: {response.text}")
    data = response.json()
    return data["access_token"]

def create_product(token: str, product_data: dict):
    """Create a new product with all details"""
    url = f"{API_URL}/products/create-simple"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("Creating new product...")
    print(f"Request data: {json.dumps(product_data, indent=2)}")
    
    response = requests.post(url, headers=headers, json=product_data)
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 200 or response.status_code == 201:
        print("Product created successfully!")
        return response.json()
    else:
        print(f"Failed to create product: {response.text}")
        return None

def add_product_review(token: str, product_slug: str, review_data: dict):
    """Add a review to a product"""
    url = f"{API_URL}/products/{product_slug}/reviews"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"Adding review to product {product_slug}...")
    print(f"Review data: {json.dumps(review_data, indent=2)}")
    
    response = requests.post(url, headers=headers, json=review_data)
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 200 or response.status_code == 201:
        print("Review added successfully!")
        return response.json()
    else:
        print(f"Failed to add review: {response.text}")
        return None

def upload_image(token: str, image_path: str, product_id: int) -> dict:
    """Upload a product image"""
    headers = {"Authorization": f"Bearer {token}"}
    
    with open(image_path, 'rb') as f:
        files = {'file': (os.path.basename(image_path), f, 'image/png')}
        data = {
            'alt_text': os.path.basename(image_path),
            'position': 1
        }
        
        print(f"Uploading image to product {product_id}: {image_path}")
        
        response = requests.post(
            f"{API_URL}/products/{product_id}/images",
            headers=headers,
            files=files,
            data=data
        )
    
    print(f"Upload image response status: {response.status_code}")
    
    try:
        return response.json()
    except:
        return {"error": "Failed to parse response"}

def main():
    # Get authentication token
    token = login()
    
    # Color specifications
    colors = ["White", "Gray", "Turquoise", "Black"]
    color_hex_codes = {
        "White": "#FFFFFF",
        "Gray": "#808080",
        "Turquoise": "#40E0D0",
        "Black": "#000000"
    }
    
    # Define available sizes
    sizes = ["XS", "S", "M", "L", "XL", "XXL"]
    
    # Create complete product data
    product_data = {
        "name": "Premium Cotton T-Shirt",
        "description": "A high-quality, 100% premium cotton t-shirt available in multiple colors. Features a classic fit with reinforced stitching for durability. Perfect for everyday wear or custom printing.",
        "price": 29.99,
        "stock": 100,
        "category_id": 1,
        "status": "published",
        "is_featured": True,
        "is_customizable": True,
        "colors": colors,
        "specifications": {
            "material": "100% Premium Cotton",
            "care": "Machine wash cold, tumble dry low",
            "fit": "Regular fit",
            "sizes": sizes,
            "neckline": "Crew neck",
            "sleeve": "Short sleeve",
            "fabric_weight": "Medium (5.3 oz/yd²)",
            "color_hex_codes": color_hex_codes
        },
        "customization_options": {
            "colors": colors,
            "sizes": sizes,
            "print_areas": ["Front", "Back", "Left Sleeve", "Right Sleeve"]
        },
        "meta_title": "Premium Cotton T-Shirt | Multiple Colors",
        "meta_description": "High-quality t-shirt made from 100% premium cotton. Available in multiple colors and sizes."
    }
    
    # Create the product
    new_product = create_product(token, product_data)
    
    if not new_product:
        print("Failed to create product. Exiting.")
        return
    
    product_id = new_product["id"]
    product_slug = new_product["slug"]
    
    print(f"Created product with ID: {product_id} and slug: {product_slug}")
    
    # Upload images for each color variant
    image_dir = Path("/Users/bo/Desktop/AI stuff/okyke_ecomm_v4/new_prodcucts")
    color_images = {
        "white": "tshirt_white.png",
        "gray": "tshirt_gray.png",
        "turquoise": "tshirt_turquoise.png",
        "black": "tshirt_black.png"
    }
    
    # Wait a moment to ensure the product is fully created
    print("Waiting for product to be fully created...")
    time.sleep(2)
    
    for color, image_name in color_images.items():
        image_path = image_dir / image_name
        if image_path.exists():
            print(f"Uploading {color} variant image...")
            result = upload_image(token, str(image_path), product_id)
            print(f"Upload result: {result}")
        else:
            print(f"Image not found: {image_path}")
    
    # Add some sample reviews
    reviews = [
        {
            "rating": 5,
            "comment": "Great quality t-shirt! The material is soft and comfortable. I ordered the white one and it's perfect."
        },
        {
            "rating": 4,
            "comment": "Nice fit and good material. I just wish there were more color options available."
        },
        {
            "rating": 5,
            "comment": "The turquoise color is even better in person. Very comfortable and true to size."
        }
    ]
    
    # Wait a moment before adding reviews
    print("Waiting a moment before adding reviews...")
    time.sleep(2)
    
    # Add the reviews
    for review in reviews:
        try:
            added_review = add_product_review(token, product_slug, review)
            if added_review:
                print(f"Added review with rating {review['rating']}")
            time.sleep(1)  # Small delay between reviews
        except Exception as e:
            print(f"Error adding review: {str(e)}")
    
    print("\nProduct creation completed successfully!")

if __name__ == "__main__":
    main() 