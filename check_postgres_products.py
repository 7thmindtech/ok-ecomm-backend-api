#!/usr/bin/env python3
import os
import sys
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database connection parameters
DB_NAME = os.getenv("POSTGRES_DB", "okyke")
DB_USER = os.getenv("POSTGRES_USER", "bo")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

def check_table_exists(cursor, table_name):
    """Check if a table exists in the database"""
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = %s
        )
    """, (table_name,))
    return cursor.fetchone()[0]

def check_and_delete_products_without_images():
    """
    Check for products without images in the PostgreSQL database and 
    provide option to delete them
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
        
        # Find products with no images in the product_images table
        if existing_tables["product_images"]:
            cursor.execute("""
                SELECT p.id, p.name
                FROM products p
                LEFT JOIN product_images pi ON p.id = pi.product_id
                WHERE pi.id IS NULL
            """)
            products_without_images = cursor.fetchall()
        else:
            products_without_images = []
        
        # Find products with NULL featured_image_id (if that column exists)
        if 'featured_image_id' in product_columns:
            cursor.execute("""
                SELECT id, name 
                FROM products 
                WHERE featured_image_id IS NULL
            """)
            products_with_null_featured_id = cursor.fetchall()
        else:
            products_with_null_featured_id = []
        
        # Print results
        print(f"\nFound {len(products_without_images)} products with no images in product_images table:")
        for product in products_without_images:
            print(f"ID: {product[0]}, Name: {product[1]}")
        
        if 'featured_image_id' in product_columns:
            print(f"\nFound {len(products_with_null_featured_id)} products with NULL featured_image_id:")
            for product in products_with_null_featured_id:
                print(f"ID: {product[0]}, Name: {product[1]}")
        
        # Combine and remove duplicates
        all_problem_product_ids = set()
        for product in products_without_images:
            all_problem_product_ids.add(product[0])
        for product in products_with_null_featured_id:
            all_problem_product_ids.add(product[0])
        
        if all_problem_product_ids:
            choice = input(f"\nDo you want to delete all {len(all_problem_product_ids)} products without images? (y/n): ")
            if choice.lower() == 'y':
                for product_id in all_problem_product_ids:
                    # First delete related records from other tables that might have foreign key constraints
                    if existing_tables["product_categories"]:
                        cursor.execute("DELETE FROM product_categories WHERE product_id = %s", (product_id,))
                    
                    if existing_tables["product_images"]:
                        cursor.execute("DELETE FROM product_images WHERE product_id = %s", (product_id,))
                    
                    if existing_tables["product_options"]:
                        cursor.execute("DELETE FROM product_options WHERE product_id = %s", (product_id,))
                    
                    if existing_tables["product_variants"]:
                        cursor.execute("DELETE FROM product_variants WHERE product_id = %s", (product_id,))
                    
                    # Check for cart_items table
                    if check_table_exists(cursor, "cart_items"):
                        cursor.execute("DELETE FROM cart_items WHERE product_id = %s", (product_id,))
                    
                    # Check for order_items table
                    if check_table_exists(cursor, "order_items"):
                        cursor.execute("DELETE FROM order_items WHERE product_id = %s", (product_id,))
                    
                    # Then delete the product
                    cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
                    print(f"Deleted product with ID: {product_id}")
                
                conn.commit()
                print(f"Deleted {len(all_problem_product_ids)} products without images.")
            else:
                print("No products were deleted.")
        else:
            print("All products have images.")
        
    except Exception as e:
        print(f"Error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    check_and_delete_products_without_images() 