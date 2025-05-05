from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from datetime import datetime

# Create password hash
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
password_hash = pwd_context.hash('Admin123!')

# Database connection
engine = create_engine('postgresql://bo@localhost:5432/okyke')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

# SQL query to insert admin user
query = text('''
INSERT INTO users (email, hashed_password, first_name, last_name, user_type, role, is_active, is_verified, created_at)
VALUES ('admin@okyke.com', :password, 'Admin', 'User', 'ADMIN', 'ADMIN', true, true, :created_at)
''')

try:
    # Execute the query
    db.execute(query, {'password': password_hash, 'created_at': datetime.utcnow()})
    db.commit()
    print('Admin user created successfully!')
except Exception as e:
    print(f'Error creating admin user: {e}')
finally:
    db.close() 