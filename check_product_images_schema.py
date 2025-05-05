#!/usr/bin/env python3
import os
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

def check_product_images_schema():
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
        
        # Check the schema of the product_images table
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'product_images'
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        print("product_images table schema:")
        for column in columns:
            print(f"  {column[0]} ({column[1]}, nullable: {column[2]})")
        
        # Get a sample row
        cursor.execute("""
            SELECT * FROM product_images LIMIT 1
        """)
        sample = cursor.fetchone()
        if sample:
            column_names = [desc[0] for desc in cursor.description]
            print("\nSample row:")
            for i, value in enumerate(sample):
                print(f"  {column_names[i]}: {value}")
        else:
            print("\nNo rows in product_images table")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    check_product_images_schema() 