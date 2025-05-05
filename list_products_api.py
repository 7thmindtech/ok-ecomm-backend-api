#!/usr/bin/env python3
import os
import sys
import requests
import json
from datetime import datetime, timedelta
import tabulate
import time
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
API_URL = "http://127.0.0.1:3001/api/v1"
ADMIN_USERNAME = "admin@okyke.com"
ADMIN_PASSWORD = "Admin123!"
TOKEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".api_token")

def save_token(token_data):
    """Save token data to a file for reuse"""
    if not token_data:
        return False
    
    token_info = {
        "access_token": token_data["access_token"],
        "expires_at": (datetime.now() + timedelta(days=6)).isoformat(),  # Conservative expiry
        "user": token_data["user"]
    }
    
    try:
        with open(TOKEN_FILE, "w") as f:
            json.dump(token_info, f)
        return True
    except Exception as e:
        logger.error(f"Failed to save token: {str(e)}")
        return False

def load_token():
    """Load token data from file if available and not expired"""
    if not os.path.exists(TOKEN_FILE):
        return None
    
    try:
        with open(TOKEN_FILE, "r") as f:
            token_info = json.load(f)
        
        # Check token expiry
        expires_at = datetime.fromisoformat(token_info["expires_at"])
        if datetime.now() > expires_at:
            logger.info("Saved token has expired")
            return None
            
        return token_info
    except Exception as e:
        logger.error(f"Failed to load token: {str(e)}")
        return None

def login():
    """Authenticate and get access token with caching"""
    # Try to load cached token first
    token_info = load_token()
    if token_info:
        logger.info("Using cached authentication token")
        return token_info["access_token"]
    
    # Need to authenticate
    logger.info("Authenticating with server...")
    try:
        response = requests.post(
            f"{API_URL}/auth/login-alt",
            data={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}
        )
        
        if response.status_code != 200:
            logger.error(f"Login failed: {response.text}")
            return None
        
        token_data = response.json()
        logger.info("Successfully authenticated.")
        
        # Save token for reuse
        save_token(token_data)
        
        return token_data["access_token"]
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return None

def get_products(limit=20, sort_by="created_at", sort_order="desc", filter_args=None):
    """Fetch products from the API with improved token handling"""
    token = login()
    if not token:
        logger.error("Failed to get authentication token")
        return []
    
    headers = {"Authorization": f"Bearer {token}"}
    
    url = f"{API_URL}/products"
    params = {
        "skip": 0,
        "limit": limit,
        "sort_by": sort_by,
        "sort_order": sort_order
    }
    
    # Add any additional filter parameters
    if filter_args:
        params.update(filter_args)
    
    logger.info(f"Fetching products with parameters: {params}")
    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Retrieved {len(result.get('items', []))} products")
            return result.get("items", [])
        
        # Check for token expired error
        if response.status_code == 401 and "expire" in response.text.lower():
            # Clear token file and retry once
            if os.path.exists(TOKEN_FILE):
                os.remove(TOKEN_FILE)
            
            logger.info("Token expired, retrying with fresh token")
            token = login()
            if not token:
                logger.error("Failed to refresh authentication token")
                return []
                
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Retrieved {len(result.get('items', []))} products after token refresh")
                return result.get("items", [])
            
        logger.error(f"Failed to fetch products: {response.text}")
        return []
    except Exception as e:
        logger.error(f"Error fetching products: {str(e)}")
        return []

def get_categories():
    """Fetch all categories from the API with improved token handling"""
    token = login()
    if not token:
        logger.error("Failed to get authentication token")
        return {}
    
    headers = {"Authorization": f"Bearer {token}"}
    
    logger.info("Fetching categories...")
    try:
        response = requests.get(f"{API_URL}/categories", headers=headers)
        
        if response.status_code == 200:
            categories = {}
            for category in response.json():
                categories[category["id"]] = category["name"]
            logger.info(f"Retrieved {len(categories)} categories")
            return categories
        
        # Check for token expired error
        if response.status_code == 401 and "expire" in response.text.lower():
            # Clear token file and retry once
            if os.path.exists(TOKEN_FILE):
                os.remove(TOKEN_FILE)
            
            logger.info("Token expired, retrying with fresh token")
            token = login()
            if not token:
                logger.error("Failed to refresh authentication token")
                return {}
                
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{API_URL}/categories", headers=headers)
            
            if response.status_code == 200:
                categories = {}
                for category in response.json():
                    categories[category["id"]] = category["name"]
                logger.info(f"Retrieved {len(categories)} categories after token refresh")
                return categories
        
        logger.error(f"Failed to fetch categories: {response.text}")
        return {}
    except Exception as e:
        logger.error(f"Error fetching categories: {str(e)}")
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
    if price is None:
        return "N/A"
    return f"${price:.2f}"

def display_products(products, categories, show_images=False):
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
        
        # Format image info
        image_info = "Yes" if product.get("featured_image_url") else "No"
        
        # Add row to table data
        table_data.append([
            product.get("id"),
            product.get("name", "Unnamed"),
            format_price(product.get("price")),
            product.get("stock", 0),
            product.get("status", "unknown"),
            category_name,
            created_at,
            image_info,
            product.get("views_count", 0),
            product.get("sales_count", 0),
        ])
    
    # Display table
    headers = ["ID", "Name", "Price", "Stock", "Status", "Category", "Created At", "Has Image", "Views", "Sales"]
    print(tabulate.tabulate(table_data, headers=headers, tablefmt="grid"))
    
    # If requested, show image URLs
    if show_images:
        print("\n=== Product Images ===")
        for product in products:
            if product.get("featured_image_url"):
                print(f"Product ID {product.get('id')} - {product.get('name')}: {product.get('featured_image_url')}")

def filter_by_category(products, category_id):
    """Filter products by category ID"""
    return [p for p in products if p.get("category_id") == category_id]

def main():
    """Main function to list products from the API"""
    parser = argparse.ArgumentParser(description="List products from the Okyke API")
    parser.add_argument("--limit", type=int, default=20, help="Number of products to fetch (default: 20)")
    parser.add_argument("--sort-by", choices=["created_at", "price", "name", "stock", "sales_count"], 
                        default="created_at", help="Field to sort by (default: created_at)")
    parser.add_argument("--sort-order", choices=["asc", "desc"], default="desc", 
                        help="Sort order (default: desc)")
    parser.add_argument("--category", type=int, help="Filter by category ID")
    parser.add_argument("--status", choices=["draft", "published", "archived"], 
                        help="Filter by product status")
    parser.add_argument("--show-images", action="store_true", help="Show product image URLs")
    parser.add_argument("--min-price", type=float, help="Filter by minimum price")
    parser.add_argument("--max-price", type=float, help="Filter by maximum price")
    parser.add_argument("--search", type=str, help="Search term for products")
    
    args = parser.parse_args()
    
    # Build filter arguments
    filter_args = {}
    if args.category:
        filter_args["category_id"] = args.category
    if args.status:
        filter_args["status"] = args.status
    if args.min_price is not None:
        filter_args["min_price"] = args.min_price
    if args.max_price is not None:
        filter_args["max_price"] = args.max_price
    if args.search:
        filter_args["search"] = args.search
    
    # Get categories for mapping
    categories = get_categories()
    
    # Get products with specified parameters
    products = get_products(
        limit=args.limit,
        sort_by=args.sort_by,
        sort_order=args.sort_order,
        filter_args=filter_args
    )
    
    # Display products
    if args.sort_by == "created_at" and args.sort_order == "desc":
        title = f"Top {len(products)} Latest Products"
    elif args.sort_by == "sales_count" and args.sort_order == "desc":
        title = f"Top {len(products)} Best Selling Products"
    elif args.sort_by == "price":
        price_order = "Highest to Lowest" if args.sort_order == "desc" else "Lowest to Highest"
        title = f"Products by Price ({price_order})"
    else:
        title = f"Products Sorted by {args.sort_by.replace('_', ' ').title()} ({args.sort_order})"
    
    if args.category and args.category in categories:
        title += f" in Category '{categories[args.category]}'"
    if args.status:
        title += f" with Status '{args.status.title()}'"
    if args.search:
        title += f" matching '{args.search}'"
    
    print(f"\n=== {title} ===\n")
    display_products(products, categories, args.show_images)

if __name__ == "__main__":
    main() 