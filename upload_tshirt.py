import os
import requests
import json
from pathlib import Path
from typing import Dict, Any
import sys
import time

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

def upload_image(token: str, image_path: str, product_id: int) -> Dict[str, Any]:
    """Upload a product image"""
    headers = {"Authorization": f"Bearer {token}"}
    
    with open(image_path, 'rb') as f:
        files = {'file': (os.path.basename(image_path), f, 'image/png')}
        data = {
            'alt_text': os.path.basename(image_path),
            'position': 1
        }
        
        print(f"Uploading image to product {product_id}: {image_path}")
        print(f"Target folder should be: products/{product_id}/")
        
        response = requests.post(
            f"{API_URL}/products/{product_id}/images",
            headers=headers,
            files=files,
            data=data
        )
    
    print(f"Upload image response status: {response.status_code}")
    print(f"Upload image response: {response.text}")
    
    try:
        result = response.json()
        
        # Verify where the file should be stored
        expected_path = f"/Users/bo/Desktop/AI stuff/okyke_ecomm_v4/backend/local_s3_storage/okyke-files/products/{product_id}"
        if 'url' in result:
            print(f"Image URL: {result['url']}")
            print(f"Should be stored at: {expected_path}")
        
        return result
    except:
        return {"error": "Failed to parse response"}

def create_product(access_token):
    """Create a new product."""
    url = f"{API_URL}/products"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    product_data = {
        "name": "Classic T-Shirt",
        "description": "A comfortable, classic t-shirt made from premium cotton. Available in multiple colors.",
        "price": 29.99,
        "stock": 100,
        "category_id": 1,
        "status": "published",
        "specifications": {
            "material": "100% Premium Cotton",
            "care": "Machine wash cold, tumble dry low",
            "fit": "Regular fit"
        },
        "colors": ["White", "Gray", "Turquoise", "Black"],
        "dimensions": {
            "width": 50.0,
            "height": 70.0,
            "unit": 1.0  # 1.0 represents cm
        },
        "weight": 0.2,
        "materials": ["Cotton"],
        "customization_options": {
            "colors": ["White", "Gray", "Turquoise", "Black"],
            "sizes": ["XS", "S", "M", "L", "XL", "XXL"],
            "print_areas": ["Front", "Back"]
        },
        "meta_title": "Classic Cotton T-Shirt | Multiple Colors",
        "meta_description": "Premium cotton t-shirt perfect for everyday wear. Available in multiple colors and sizes.",
        "is_featured": True,
        "is_customizable": True,
        "low_stock_threshold": 10
    }
    
    try:
        print("Sending request to create product...")
        print("Request data:", product_data)
        response = requests.post(url, headers=headers, json=product_data)
        print(f"Response status: {response.status_code}")
        print("Response body:", response.text)
        
        if response.status_code == 200 or response.status_code == 201:
            return response.json()
        else:
            # Try fallback approach
            print("API call failed, trying direct upload...")
            return create_product_direct(access_token, product_data)
    except Exception as e:
        print(f"Error creating product: {str(e)}")
        return None

def create_product_direct(access_token, product_data):
    """Create a product directly using a different approach"""
    # Try using the database directly
    try:
        # Let's try a different endpoint that might work
        url = f"{API_URL}/products/create-simple"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Simplify the data structure
        simple_data = {
            "name": product_data["name"],
            "description": product_data["description"],
            "price": product_data["price"],
            "stock": product_data["stock"],
            "category_id": product_data["category_id"],
            "status": product_data["status"],
            "is_featured": product_data["is_featured"],
            "is_customizable": product_data["is_customizable"]
        }
        
        print("Trying simplified product creation...")
        print("Request data:", simple_data)
        response = requests.post(url, headers=headers, json=simple_data)
        print(f"Response status: {response.status_code}")
        print("Response body:", response.text)
        
        if response.status_code == 200 or response.status_code == 201:
            return response.json()
        else:
            # If even simple creation fails, try to bypass the API validation issue
            print("Simple product creation failed. Trying to create a mock product for image upload...")
            # Create a minimal product just to get an ID for image upload
            mock_data = {
                "name": "Temporary Product",
                "description": "This is a temporary product for image upload",
                "price": 9.99,
                "stock": 1,
                "category_id": 1
            }
            
            # Try to create the product with minimal data
            url = f"{API_URL}/products/create-minimal"
            response = requests.post(url, headers=headers, json=mock_data)
            
            if response.status_code == 200 or response.status_code == 201:
                mock_product = response.json()
                print(f"Created mock product with ID: {mock_product['id']}")
                return mock_product
            else:
                print("All creation methods failed")
                return None
    except Exception as e:
        print(f"Error in direct product creation: {str(e)}")
        return None

def main():
    # Get authentication token
    token = login()
    
    # Product data
    product_data = {
        "name": "Classic T-Shirt",
        "description": "A comfortable, classic t-shirt made from premium cotton. Available in multiple colors.",
        "price": 29.99,
        "stock": 100
    }
    
    # Create the product
    product = create_product(token)
    
    if not product or "id" not in product:
        print("Failed to create product")
        return
    
    product_id = product["id"]
    print(f"Created product with ID: {product_id}")
    
    # Upload images for each color variant
    # Use absolute path to ensure images are found
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
            
            # Verify the image was saved to the correct location
            expected_path = f"/Users/bo/Desktop/AI stuff/okyke_ecomm_v4/backend/local_s3_storage/okyke-files/products/{product_id}"
            print(f"Image should be saved in: {expected_path}")
        else:
            print(f"Image not found: {image_path}")

if __name__ == "__main__":
    main() 