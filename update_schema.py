from app.db.init_db import init_db
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_schema():
    """Update the database schema with new columns."""
    try:
        # This will add any missing columns from the models
        init_db(should_reset=False)
        logger.info("Schema updated successfully")
    except Exception as e:
        logger.error(f"Error updating schema: {str(e)}")

if __name__ == "__main__":
    update_schema() 