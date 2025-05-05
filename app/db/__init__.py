from app.core.database import Base, SessionLocal, engine
from app.db.init_db import init_db

# Export the database components
__all__ = ["Base", "SessionLocal", "engine", "init_db"]

# Initialize database tables without resetting
init_db(should_reset=False) 