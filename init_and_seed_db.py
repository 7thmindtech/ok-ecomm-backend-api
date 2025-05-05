#!/usr/bin/env python3
"""
Script to initialize and seed the database
"""
import logging
from app.db.init_db import init_db
from app.db.seed import seed_db

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Initializing database...")
    init_db()
    
    logger.info("Seeding database with initial data...")
    try:
        seed_db()
        logger.info("Database seeded successfully!")
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        raise 