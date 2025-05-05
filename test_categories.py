from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.models.models import Category
from app.utils.slugify import slugify
import logging
from app.crud.crud_category import CRUDCategory

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_categories():
    """Test category functionality."""
    try:
        # Create engine and session
        engine = create_engine(settings.DATABASE_URL)
        logger.info(f"Connected to database: {settings.DATABASE_URL}")
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Create tables if they don't exist
        from app.db.base import Base
        Base.metadata.create_all(bind=engine)
        logger.info("Tables created if they didn't exist")
        
        # Check if any categories exist
        categories = db.query(Category).all()
        logger.info(f"Found {len(categories)} existing categories")
        
        for category in categories:
            logger.info(f"Category: {category.id} - {category.name}")
        
        # If no categories exist, create a test one
        if not categories:
            test_category = Category(
                name="Test Category",
                description="This is a test category",
                slug=slugify("Test Category"),
                is_active=True
            )
            db.add(test_category)
            db.commit()
            logger.info(f"Created test category: {test_category.name}")
        
        # Verify after creation
        categories = db.query(Category).all()
        for category in categories:
            logger.info(f"Category: {category.id} - {category.name}")
        
        db.close()
        print("Category test successful!")
        return True
    except Exception as e:
        logger.error(f"Error in category test: {str(e)}")
        return False

if __name__ == "__main__":
    from create_tables import reset_database
    # First reset the database to ensure clean state
    reset_database()
    # Then test categories
    test_categories() 