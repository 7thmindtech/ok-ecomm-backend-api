from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.models import User, UserType, UserRole
import logging
from sqlalchemy.exc import OperationalError, ProgrammingError

logger = logging.getLogger(__name__)

def create_admin_user():
    """Create admin user if it doesn't exist."""
    try:
        db = SessionLocal()
        try:
            # Try to create the admin user directly without checking if it exists
            admin_user = User(
                email="admin@okyke.com",
                hashed_password=get_password_hash("Admin123!"),
                first_name="Admin",
                last_name="User",
                user_type=UserType.ADMIN,
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            logger.info("Successfully created admin user")
        except Exception as e:
            db.rollback()
            if "duplicate key value violates unique constraint" in str(e):
                logger.info("Admin user already exists")
            else:
                logger.error(f"Failed to create admin user: {e}")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error in create_admin_user: {e}")
        raise 