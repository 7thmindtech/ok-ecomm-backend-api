#!/usr/bin/env python3
import os
import sys
import psycopg2
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# Database connection parameters
DB_NAME = os.getenv("POSTGRES_DB", "okyke")
DB_USER = os.getenv("POSTGRES_USER", "bo")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

# Path to local storage for product images
STORAGE_PATH = "/Users/bo/Desktop/AI stuff/okyke_ecomm_v4/backend/local_s3_storage/okyke-files/products"

def check_table_exists(cursor, table_name):
    """Check if a table exists in the database"""
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = %s
        )
    """, (table_name,))
    return cursor.fetchone()[0]

def update_products_with_images():
    """
    Check if products have corresponding images in the storage directory.
    Update featured_image_id for products that have images.
    Delete products that don't have any images.
    """
    conn = None
    try:
        # Connect to the database
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()
        
        # First get the column names of the products table to understand its schema
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'products'
        """)
        product_columns = [col[0] for col in cursor.fetchall()]
        print("Product table columns:", product_columns)
        
        # Check which tables exist
        tables_to_check = [
            "product_categories", 
            "product_images", 
            "product_options", 
            "product_variants"
        ]
        existing_tables = {}
        for table in tables_to_check:
            existing_tables[table] = check_table_exists(cursor, table)
            print(f"Table {table} exists: {existing_tables[table]}")
        
        # Get all products
        cursor.execute("SELECT id, name FROM products ORDER BY id")
        products = cursor.fetchall()
        print(f"Found {len(products)} products in database")

        products_to_delete = []
        products_to_update = []

        for product_id, product_name in products:
            product_dir = os.path.join(STORAGE_PATH, str(product_id))
            
            # Check if product directory exists
            if not os.path.exists(product_dir):
                print(f"Product ID {product_id} ({product_name}) has no image directory")
                products_to_delete.append((product_id, product_name))
                continue
            
            # Check if directory has any image files
            image_files = [f for f in os.listdir(product_dir) 
                          if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')) 
                          and not f.startswith('.')]
            
            if not image_files:
                print(f"Product ID {product_id} ({product_name}) has directory but no image files")
                products_to_delete.append((product_id, product_name))
                continue
            
            # For products with images, check if we need to update the featured_image_id
            if "featured_image_id" in product_columns:
                cursor.execute("SELECT featured_image_id FROM products WHERE id = %s", (product_id,))
                featured_image_id = cursor.fetchone()[0]
                
                # If featured_image_id is NULL, check if product has images in the product_images table
                if featured_image_id is None and existing_tables["product_images"]:
                    cursor.execute("SELECT id FROM product_images WHERE product_id = %s AND position = 0 LIMIT 1", (product_id,))
                    primary_image_row = cursor.fetchone()
                    
                    if primary_image_row:
                        # Update the featured_image_id with the primary image found
                        print(f"Product ID {product_id} ({product_name}) will be updated with image ID {primary_image_row[0]}")
                        products_to_update.append((product_id, product_name, primary_image_row[0]))
                    else:
                        # Check for any image
                        cursor.execute("SELECT id FROM product_images WHERE product_id = %s LIMIT 1", (product_id,))
                        any_image_row = cursor.fetchone()
                        
                        if any_image_row:
                            print(f"Product ID {product_id} ({product_name}) will be updated with image ID {any_image_row[0]}")
                            products_to_update.append((product_id, product_name, any_image_row[0]))
                        else:
                            # If no images in product_images table, insert one
                            relative_path = f"/local_s3/okyke-files/products/{product_id}/{image_files[0]}"
                            alt_text = f"{product_name} image"
                            print(f"Will add image {relative_path} to product ID {product_id} ({product_name})")
                            
                            # Insert the image into product_images table
                            cursor.execute(
                                """
                                INSERT INTO product_images (product_id, url, alt_text, position, created_at) 
                                VALUES (%s, %s, %s, %s, NOW()) RETURNING id
                                """,
                                (product_id, relative_path, alt_text, 0)
                            )
                            new_image_id = cursor.fetchone()[0]
                            products_to_update.append((product_id, product_name, new_image_id))
        
        # Process updates and deletes if user confirms
        if products_to_update or products_to_delete:
            print(f"\nSummary:")
            print(f"- {len(products_to_update)} products will have featured_image_id updated")
            print(f"- {len(products_to_delete)} products will be deleted due to missing images")
            
            choice = input("\nDo you want to proceed with these changes? (y/n): ")
            if choice.lower() == 'y':
                # Update products with featured_image_id
                for product_id, product_name, image_id in products_to_update:
                    cursor.execute(
                        "UPDATE products SET featured_image_id = %s WHERE id = %s",
                        (image_id, product_id)
                    )
                    print(f"Updated product ID {product_id} ({product_name}) with featured_image_id = {image_id}")
                
                # Delete products without images
                for product_id, product_name in products_to_delete:
                    # First delete related records from other tables that might have foreign key constraints
                    if existing_tables["product_categories"]:
                        cursor.execute("DELETE FROM product_categories WHERE product_id = %s", (product_id,))
                    
                    if existing_tables["product_images"]:
                        cursor.execute("DELETE FROM product_images WHERE product_id = %s", (product_id,))
                    
                    if existing_tables["product_options"]:
                        cursor.execute("DELETE FROM product_options WHERE product_id = %s", (product_id,))
                    
                    if existing_tables["product_variants"]:
                        cursor.execute("DELETE FROM product_variants WHERE product_id = %s", (product_id,))
                    
                    # Check for other possible tables with product_id foreign keys
                    for table in ["cart_items", "order_items", "wishlist_items"]:
                        if check_table_exists(cursor, table):
                            cursor.execute(f"DELETE FROM {table} WHERE product_id = %s", (product_id,))
                    
                    # Then delete the product
                    cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
                    print(f"Deleted product ID {product_id} ({product_name})")
                
                conn.commit()
                print(f"All changes committed successfully!")
            else:
                print("No changes were made.")
        else:
            print("All products have valid images and featured_image_id values.")
        
    except Exception as e:
        print(f"Error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    update_products_with_images() 