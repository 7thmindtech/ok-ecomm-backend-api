from app.core.database import engine
from sqlalchemy import inspect
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_users_table():
    """Check if the users table has the required columns."""
    try:
        inspector = inspect(engine)
        if 'users' in inspector.get_table_names():
            columns = [column['name'] for column in inspector.get_columns('users')]
            logger.info(f"Columns in users table: {columns}")
            
            # Check for our specific columns
            required_columns = [
                'is_verified', 'phone_number', 'verification_token', 
                'verification_token_expires', 'reset_password_token',
                'reset_password_token_expires', 'artist_bio', 
                'artist_portfolio_url', 'business_name',
                'business_registration_number', 'business_address'
            ]
            
            missing = [col for col in required_columns if col not in columns]
            if missing:
                logger.warning(f"Missing columns: {missing}")
            else:
                logger.info("All required columns are present!")
        else:
            logger.error("Users table not found!")
    except Exception as e:
        logger.error(f"Error checking users table: {str(e)}")

if __name__ == "__main__":
    check_users_table() 