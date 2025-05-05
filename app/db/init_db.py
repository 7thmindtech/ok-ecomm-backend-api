from app.core.database import engine
import logging
from sqlalchemy import inspect
from app.db.base import Base

logger = logging.getLogger(__name__)

def init_db(should_reset: bool = False):
    """
    Initialize the database.
    
    Args:
        should_reset (bool): If True, drop all tables and recreate them. Use with caution!
    """
    try:
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        
        # Log created tables
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        logger.info(f"Created tables: {', '.join(tables)}")
        
        return True
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise 