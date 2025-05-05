#!/usr/bin/env python3
import requests
import json

API_URL = "http://127.0.0.1:8888/api/v1"

PRODUCTS = [
    {
        "name": "Classic White T-Shirt",
        "description": "A comfortable, classic white t-shirt made from premium cotton.",
        "price": 29.99,
        "stock": 150,
        "category_name": "Clothing",
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
        "specifications": {
            "material": "Neoprene",
            "sizes": ["13\"", "15\"", "17\""]
        }
    }
]

def login():
    """Login and get access token"""
    response = requests.post(f"{API_URL}/auth/login-alt", data={
        "username": "admin@okyke.com",
        "password": "Admin123!"
    })
    if response.status_code == 200:
        return response.json()["access_token"]
    print(f"Login failed: {response.text}")
    return None

def create_category(token, name, description=None):
    """Create a category"""
    headers = {"Authorization": f"Bearer {token}"}
    category_data = {
        "name": name,
        "description": description or f"{name} items"
    }
    
    print(f"Creating category: {name}...")
    response = requests.post(f"{API_URL}/categories", headers=headers, json=category_data)
    if response.status_code in (200, 201):
        category = response.json()
        print(f"Created category {name} with ID {category['id']}")
        return category["id"]
    print(f"Failed to create category: {response.text}")
    return None

def create_product(token, product_data, category_id):
    """Create a product"""
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "name": product_data["name"],
        "description": product_data["description"],
        "price": product_data["price"],
        "stock": product_data["stock"],
        "category_id": category_id,
        "artist_id": 1,  # Admin user ID
        "status": "published",
        "specifications": product_data["specifications"],
        "colors": product_data.get("colors", []),
        "is_featured": product_data.get("is_featured", False),
        "is_customizable": product_data.get("is_customizable", False),
        "low_stock_threshold": 10
    }
    
    print(f"Creating product: {data['name']}...")
    response = requests.post(f"{API_URL}/products", headers=headers, json=data)
    print(f"Status Code: {response.status_code}")
    try:
        result = response.json()
        print("Response:", json.dumps(result, indent=2))
        return result
    except:
        print("Response:", response.text)
        return None

def main():
    token = login()
    if not token:
        print("Failed to login")
        return
    
    # Create categories and store their IDs
    categories = {}
    for product in PRODUCTS:
        category_name = product["category_name"]
        if category_name not in categories:
            category_id = create_category(token, category_name)
            if not category_id:
                print(f"Failed to create category {category_name}")
                return
            categories[category_name] = category_id
    
    # Create products
    for product in PRODUCTS:
        category_id = categories[product["category_name"]]
        create_product(token, product, category_id)

if __name__ == "__main__":
    main() 