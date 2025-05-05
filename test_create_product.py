import requests
import json

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

def create_product(access_token):
    """Create a new product using the main API endpoint."""
    url = f"{API_URL}/products"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Test data without artist_id
    product_data = {
        "name": "Test Product Without Artist ID",
        "description": "This is a test product created without an artist_id field.",
        "price": 39.99,
        "stock": 50,
        "category_id": 1,
        "status": "published",
        "specifications": {
            "material": "Test Material",
            "care": "Test Care Instructions"
        },
        "colors": ["Red", "Blue"],
        "meta_title": "Test Product",
        "meta_description": "Test product description for SEO",
        "is_featured": False,
        "is_customizable": True
    }
    
    print("\nAttempting to create product with main API endpoint...")
    print("Request data:", json.dumps(product_data, indent=2))
    response = requests.post(url, headers=headers, json=product_data)
    print(f"Response status: {response.status_code}")
    print("Response body:", response.text)
    
    if response.status_code == 200 or response.status_code == 201:
        return True, "Main API"
    
    # If that fails, try the simplified endpoint
    print("\nMain API failed. Trying simplified endpoint...")
    url = f"{API_URL}/products/create-simple"
    response = requests.post(url, headers=headers, json=product_data)
    print(f"Response status: {response.status_code}")
    print("Response body:", response.text)
    
    if response.status_code == 200 or response.status_code == 201:
        return True, "Simple API"
    
    return False, "Both APIs failed"

def main():
    # Get authentication token
    token = login()
    
    # Try to create a product
    success, method = create_product(token)
    
    if success:
        print(f"\nSUCCESS: Product created successfully without artist_id using {method}!")
    else:
        print(f"\nFAILED: {method}")

if __name__ == "__main__":
    main() 