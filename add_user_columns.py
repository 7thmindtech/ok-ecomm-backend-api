from app.core.database import engine
from sqlalchemy import text
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_user_columns():
    """Add missing columns to the users table."""
    try:
        with engine.connect() as conn:
            # Add is_verified column
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE"))
            
            # Add phone_number column
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS phone_number VARCHAR"))
            
            # Add verification_token columns
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS verification_token VARCHAR"))
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS verification_token_expires TIMESTAMP"))
            
            # Add reset_password_token columns
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_password_token VARCHAR"))
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_password_token_expires TIMESTAMP"))
            
            # Add artist fields
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS artist_bio TEXT"))
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS artist_portfolio_url VARCHAR"))
            
            # Add business fields
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS business_name VARCHAR"))
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS business_registration_number VARCHAR"))
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS business_address VARCHAR"))
            
            conn.commit()
            
        logger.info("Successfully added missing columns to the users table")
    except Exception as e:
        logger.error(f"Error adding columns: {str(e)}")

if __name__ == "__main__":
    add_user_columns() 