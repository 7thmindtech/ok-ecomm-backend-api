#!/usr/bin/env python3
import requests
import json

def print_response(response):
    print('Status:', response.status_code)
    print('Headers:', dict(response.headers))
    try:
        print('Response:', json.dumps(response.json(), indent=2))
    except:
        print('Response:', response.text)

# Login
try:
    response = requests.post('http://127.0.0.1:3002/api/v1/auth/login-alt', data={'username': 'admin@okyke.com', 'password': 'Admin123!'})
    print('Login response:')
    print_response(response)
    token = response.json()['access_token']
except Exception as e:
    print('Login error:', str(e))
    exit(1)

# Get products to find the ID
try:
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get('http://127.0.0.1:3002/api/v1/products', headers=headers)
    print('\nProducts response:')
    print_response(response)
    products = response.json()['items']
    if not products:
        print('No products found')
        exit(1)
    product_id = products[0]['id']
except Exception as e:
    print('Get products error:', str(e))
    exit(1)

# Upload image
try:
    with open('../frontend/public/images/products/classic-white-tshirt-large.jpg', 'rb') as f:
        files = {'file': ('classic-white-tshirt-large.jpg', f, 'image/jpeg')}
        data = {'is_featured': 'true', 'alt_text': f'Product image for {product_id}'}
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.post(f'http://127.0.0.1:3002/api/v1/products/{product_id}/images', headers=headers, files=files, data=data)
        print('\nUpload response:')
        print_response(response)
except Exception as e:
    print('Upload error:', str(e)) 