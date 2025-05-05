#!/usr/bin/env python3
import sys
import os

# Add the parent directory to the Python path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import init_db

if __name__ == "__main__":
    print("WARNING: This will delete all data in the database!")
    response = input("Are you sure you want to continue? [y/N] ")
    
    if response.lower() == 'y':
        print("Resetting database...")
        init_db(should_reset=True)
        print("Database reset complete!")
    else:
        print("Database reset cancelled.") 