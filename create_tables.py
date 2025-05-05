from sqlalchemy import create_engine, text
from app.core.config import settings
from app.core.database import Base, engine
from app.db.init_db import init_db
from app.db.admin import create_admin_user
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reset_database():
    """Drop all tables and recreate them."""
    try:
        logger.info(f"Connected to database: {settings.DATABASE_URL}")
        
        # Drop schema with CASCADE
        with engine.connect() as conn:
            conn.execute(text("DROP SCHEMA public CASCADE"))
            conn.execute(text("CREATE SCHEMA public"))
            conn.commit()
        logger.info("Successfully dropped schema and recreated it")
        
        # Initialize database and create tables
        init_db(should_reset=False)
        
        # Create admin user
        create_admin_user()
        
        return True
    except Exception as e:
        logger.error(f"Error resetting database: {str(e)}")
        return False

if __name__ == "__main__":
    success = reset_database()
    if success:
        print("Database reset successful!")
    else:
        print("Database reset failed. Check the logs for details.") 