#!/usr/bin/env python3
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Category

# List of categories to add
categories = [
    {
        "name": "T-Shirts",
        "description": "Comfortable and stylish t-shirts for all occasions"
    },
    {
        "name": "Hoodies",
        "description": "Warm and cozy hoodies perfect for any weather"
    },
    {
        "name": "Phone Cases",
        "description": "Protective and stylish cases for your devices"
    },
    {
        "name": "Mugs",
        "description": "Custom mugs for your favorite beverages"
    },
    {
        "name": "Laptop Accessories",
        "description": "Accessories to enhance your laptop experience"
    },
    {
        "name": "Tote Bags",
        "description": "Durable and eco-friendly bags for everyday use"
    }
]

def add_categories():
    # Get database session
    db = next(get_db())
    
    try:
        # Add each category
        for category_data in categories:
            # Check if category already exists
            existing = db.query(Category).filter(Category.name == category_data["name"]).first()
            if not existing:
                category = Category(**category_data)
                db.add(category)
                print(f"Added category: {category_data['name']}")
            else:
                print(f"Category already exists: {category_data['name']}")
        
        # Commit changes
        db.commit()
        print("Successfully added all categories!")
        
    except Exception as e:
        print(f"Error adding categories: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_categories() 