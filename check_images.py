#!/usr/bin/env python3
import sqlite3
import os

# Connect to the database
db_path = 'app.db'
if not os.path.exists(db_path):
    print(f"Database file {db_path} not found!")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Find products without featured images
    cursor.execute('SELECT id, name, featured_image_url FROM products WHERE featured_image_url IS NULL OR featured_image_url = ""')
    products_without_featured = cursor.fetchall()
    
    # Get all product IDs with images in the product_images table
    cursor.execute('SELECT DISTINCT product_id FROM product_images')
    products_with_images = [row[0] for row in cursor.fetchall()]
    
    # Get all product IDs
    cursor.execute('SELECT id FROM products')
    all_product_ids = [row[0] for row in cursor.fetchall()]
    
    # Find products without any images in the product_images table
    products_without_images = [pid for pid in all_product_ids if pid not in products_with_images]
    
    # Display results
    print(f'Products without featured image: {len(products_without_featured)}')
    for p in products_without_featured:
        print(f"ID: {p[0]}, Name: {p[1]}")
    
    print(f'\nProducts without any images in product_images table: {len(products_without_images)}')
    for pid in products_without_images:
        product = cursor.execute('SELECT id, name FROM products WHERE id = ?', (pid,)).fetchone()
        print(f"ID: {product[0]}, Name: {product[1]}")
    
    # Delete products without images if requested
    problem_product_ids = set([p[0] for p in products_without_featured] + products_without_images)
    
    if problem_product_ids:
        choice = input("\nDo you want to delete all products without images? (y/n): ")
        if choice.lower() == "y":
            for pid in problem_product_ids:
                cursor.execute('DELETE FROM products WHERE id = ?', (pid,))
                print(f'Deleted product {pid}')
            
            conn.commit()
            print(f"{len(problem_product_ids)} products deleted successfully.")
        else:
            print("No products were deleted.")
    else:
        print("All products have images.")

except sqlite3.Error as e:
    print(f"Database error: {e}")

finally:
    conn.close() 