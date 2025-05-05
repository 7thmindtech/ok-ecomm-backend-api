#!/usr/bin/env python3
import os
import sys
import requests
import json
from datetime import datetime
import tabulate
import time

# Configuration
API_URL = "http://127.0.0.1:3001/api/v1"
ADMIN_USERNAME = "admin@okyke.com"
ADMIN_PASSWORD = "Admin123!"

def login():
    """Authenticate and get access token"""
    print("Authenticating...")
    try:
        response = requests.post(
            f"{API_URL}/auth/login-alt",
            data={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}
        )
        
        if response.status_code != 200:
            print(f"Login failed: {response.text}")
            return None
        
        token = response.json()["access_token"]
        print("Successfully authenticated.")
        return token
    except Exception as e:
        print(f"Login error: {str(e)}")
        return None

def get_products(max_retries=3, limit=10, sort_by="created_at", sort_order="desc"):
    """Fetch the latest products from the API with retry mechanism"""
    for attempt in range(max_retries):
        try:
            # Get fresh token for each attempt
            token = login()
            if not token:
                print(f"Failed to get token on attempt {attempt+1}/{max_retries}")
                time.sleep(1)
                continue
                
            headers = {"Authorization": f"Bearer {token}"}
            
            url = f"{API_URL}/products"
            params = {
                "skip": 0,
                "limit": limit,
                "sort_by": sort_by,
                "sort_order": sort_order
            }
            
            print(f"Fetching latest products (attempt {attempt+1}/{max_retries})...")
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                result = response.json()
                return result.get("items", [])
            
            print(f"Failed to fetch products (attempt {attempt+1}/{max_retries}): {response.text}")
            if "token" in response.text.lower() or "expire" in response.text.lower():
                # Token issue, retry with new token
                time.sleep(1)
                continue
                
            # Other error, might be worth stopping
            if response.status_code >= 400 and response.status_code < 500:
                print("Client error, stopping retries")
                return []
        except Exception as e:
            print(f"Error fetching products (attempt {attempt+1}/{max_retries}): {str(e)}")
            time.sleep(1)
    
    print(f"Failed to fetch products after {max_retries} attempts")
    return []

def get_categories(max_retries=3):
    """Fetch all categories to map IDs to names with retry mechanism"""
    for attempt in range(max_retries):
        try:
            # Get fresh token for each attempt
            token = login()
            if not token:
                print(f"Failed to get token on attempt {attempt+1}/{max_retries}")
                time.sleep(1)
                continue
                
            headers = {"Authorization": f"Bearer {token}"}
            
            print(f"Fetching categories (attempt {attempt+1}/{max_retries})...")
            response = requests.get(f"{API_URL}/categories", headers=headers)
            
            if response.status_code == 200:
                categories = {}
                for category in response.json():
                    categories[category["id"]] = category["name"]
                return categories
                
            print(f"Failed to fetch categories (attempt {attempt+1}/{max_retries}): {response.text}")
            if "token" in response.text.lower() or "expire" in response.text.lower():
                # Token issue, retry with new token
                time.sleep(1)
                continue
                
            # Other error, might be worth stopping
            if response.status_code >= 400 and response.status_code < 500:
                print("Client error, stopping retries")
                return {}
        except Exception as e:
            print(f"Error fetching categories (attempt {attempt+1}/{max_retries}): {str(e)}")
            time.sleep(1)
    
    print(f"Failed to fetch categories after {max_retries} attempts")
    return {}

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
            created_at
        ])
    
    # Display table
    headers = ["ID", "Name", "Price", "Stock", "Status", "Category", "Created At"]
    print(tabulate.tabulate(table_data, headers=headers, tablefmt="grid"))

def main():
    """Main function to list latest products"""
    # Get categories for mapping
    categories = get_categories()
    
    # Get latest products
    products = get_products(limit=20)
    
    # Display products
    print(f"\n=== Top {len(products)} Latest Products ===\n")
    display_products(products, categories)

if __name__ == "__main__":
    main() 