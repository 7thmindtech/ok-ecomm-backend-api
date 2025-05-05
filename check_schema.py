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
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print('Tables in the database:')
    for table in tables:
        print(table[0])
        
    # For each table, show schema
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table[0]})")
        columns = cursor.fetchall()
        
        print(f"\nSchema for table '{table[0]}':")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")

except sqlite3.Error as e:
    print(f"Database error: {e}")

finally:
    conn.close() 