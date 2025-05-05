#!/usr/bin/env python3
import os
import json
from datetime import datetime
import tabulate
import time
import random

# Mock product definitions
MOCK_PRODUCTS = [
    {
        "id": 1,
        "name": "Classic White T-Shirt",
        "description": "A comfortable, classic white t-shirt made from premium cotton.",
        "price": 29.99,
        "stock": 150,
        "category_id": 1,
        "category_name": "Clothing",
        "status": "published",
        "image_url": "/uploads/products/mock/classic-white-tshirt.jpg",
        "created_at": datetime.now().replace(hour=10, minute=0).isoformat(),
        "sales_count": random.randint(5, 50)
    },
    {
        "id": 2,
        "name": "Black Hoodie",
        "description": "A warm, comfortable black hoodie perfect for casual wear.",
        "price": 49.99,
        "stock": 100,
        "category_id": 1,
        "category_name": "Clothing",
        "status": "published",
        "image_url": "/uploads/products/mock/black-hoodie.jpg",
        "created_at": datetime.now().replace(hour=11, minute=0).isoformat(),
        "sales_count": random.randint(10, 70)
    },
    {
        "id": 3,
        "name": "Custom Mug",
        "description": "A personalized ceramic mug, perfect for your morning coffee or tea.",
        "price": 19.99,
        "stock": 75,
        "category_id": 2,
        "category_name": "Accessories",
        "status": "published",
        "image_url": "/uploads/products/mock/custom-mug.jpg",
        "created_at": datetime.now().replace(hour=12, minute=0).isoformat(),
        "sales_count": random.randint(15, 100) 
    },
    {
        "id": 4,
        "name": "Canvas Tote Bag",
        "description": "A durable canvas tote bag for everyday use.",
        "price": 24.99,
        "stock": 120,
        "category_id": 2,
        "category_name": "Accessories",
        "status": "published",
        "image_url": "/uploads/products/mock/canvas-tote.jpg",
        "created_at": datetime.now().replace(hour=13, minute=0).isoformat(),
        "sales_count": random.randint(8, 45)
    },
    {
        "id": 5,
        "name": "Phone Case",
        "description": "A durable, stylish phone case with custom artwork.",
        "price": 29.99,
        "stock": 90,
        "category_id": 2,
        "category_name": "Accessories",
        "status": "published",
        "image_url": "/uploads/products/mock/phone-case.jpg",
        "created_at": datetime.now().replace(hour=14, minute=0).isoformat(),
        "sales_count": random.randint(20, 80)
    },
    {
        "id": 6,
        "name": "Laptop Sleeve",
        "description": "A protective sleeve for laptops with unique artistic designs.",
        "price": 39.99,
        "stock": 60,
        "category_id": 2,
        "category_name": "Accessories",
        "status": "published",
        "image_url": "/uploads/products/mock/laptop-sleeve.jpg",
        "created_at": datetime.now().replace(hour=15, minute=0).isoformat(),
        "sales_count": random.randint(10, 55)
    }
]

# Mock categories
MOCK_CATEGORIES = {
    1: "Clothing",
    2: "Accessories"
}

def format_date(date_str):
    """Format ISO date string to readable format"""
    if not date_str:
        return "N/A"
    try:
        date_obj = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return date_obj.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return date_str

def format_price(price):
    """Format price with currency symbol"""
    return f"${price:.2f}"

def display_products(products, categories):
    """Display products in a formatted table"""
    if not products:
        print("No products found.")
        return
    
    # Prepare data for tabulation
    table_data = []
    for product in products:
        category_name = categories.get(product.get("category_id"), "Unknown")
        
        # Format the created date
        created_at = format_date(product.get("created_at"))
        
        # Add row to table data
        table_data.append([
            product.get("id"),
            product.get("name"),
            format_price(product.get("price", 0)),
            product.get("stock", 0),
            product.get("status", "unknown"),
            category_name,
            created_at,
            product.get("sales_count", 0)
        ])
    
    # Sort by sales count (most popular first)
    sorted_data = sorted(table_data, key=lambda x: x[7], reverse=True)
    
    # Display table
    headers = ["ID", "Name", "Price", "Stock", "Status", "Category", "Created At", "Sales"]
    print(tabulate.tabulate(sorted_data, headers=headers, tablefmt="grid"))

def display_image_status():
    """Check if the mock product images exist"""
    mock_dir = os.path.join("uploads", "products", "mock")
    if not os.path.exists(mock_dir):
        print("Mock product images directory not found!")
        return False
    
    expected_images = [
        "black-hoodie.jpg",
        "classic-white-tshirt.jpg",
        "custom-mug.jpg",
        "canvas-tote.jpg",
        "phone-case.jpg",
        "laptop-sleeve.jpg"
    ]
    
    missing = []
    for img in expected_images:
        path = os.path.join(mock_dir, img)
        if not os.path.exists(path):
            missing.append(img)
    
    if missing:
        print(f"Missing images: {', '.join(missing)}")
        return False
    
    print("All mock product images are available!")
    return True

def main():
    """Main function to list mock products"""
    print("\n=== Mock Product Image Status ===")
    display_image_status()
    
    # Sort products by different criteria
    by_created = sorted(MOCK_PRODUCTS, key=lambda x: x["created_at"], reverse=True)
    by_sales = sorted(MOCK_PRODUCTS, key=lambda x: x["sales_count"], reverse=True)
    
    # Display latest products
    print(f"\n=== Top {len(by_created)} Latest Products ===\n")
    display_products(by_created, MOCK_CATEGORIES)
    
    # Display best selling products
    print(f"\n=== Top {len(by_sales)} Best Selling Products ===\n")
    display_products(by_sales, MOCK_CATEGORIES)
    
    # Display products by category
    print("\n=== Products by Category ===\n")
    for cat_id, cat_name in MOCK_CATEGORIES.items():
        cat_products = [p for p in MOCK_PRODUCTS if p["category_id"] == cat_id]
        print(f"\n-- {cat_name} ({len(cat_products)} products) --\n")
        display_products(cat_products, MOCK_CATEGORIES)

if __name__ == "__main__":
    main() 