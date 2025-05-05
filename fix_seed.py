#!/usr/bin/env python3
"""
Script to test User creation fix
"""
import logging
from app.core.database import get_db
from app.models.models import User, UserRole
from app.core.security import get_password_hash
from sqlalchemy.exc import SQLAlchemyError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Admin user data
admin_user = {
    "email": "admin@example.com",
    "password": "admin123",
    "full_name": "Admin User",
    "role": UserRole.ADMIN
}

def create_admin_user():
    """Create admin user if it doesn't exist"""
    try:
        db = next(get_db())
        
        user = db.query(User).filter(User.email == admin_user["email"]).first()
        
        if not user:
            # Split full_name into first_name and last_name
            name_parts = admin_user["full_name"].split(" ", 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ""
            
            user = User(
                email=admin_user["email"],
                hashed_password=get_password_hash(admin_user["password"]),
                first_name=first_name,
                last_name=last_name,
                role=admin_user["role"]
            )
            db.add(user)
            db.commit()
            logger.info(f"Created admin user: {user.email}")
        else:
            logger.info(f"Admin user already exists: {user.email}")
            
        return True
    except SQLAlchemyError as e:
        logger.error(f"Error creating admin user: {str(e)}")
        if 'db' in locals():
            db.rollback()
        return False

if __name__ == "__main__":
    logger.info("Creating admin user...")
    if create_admin_user():
        logger.info("Admin user creation successful!")
    else:
        logger.error("Admin user creation failed.") 