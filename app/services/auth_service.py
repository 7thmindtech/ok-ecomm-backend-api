from typing import Any, Dict, Optional, Union
from sqlalchemy.orm import Session
from app.core.security import get_password_hash, verify_password, create_email_verification_token
from app.models.models import User
from app.schemas.user import UserCreate, UserUpdate
from datetime import datetime, timedelta

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, user_in: UserCreate) -> User:
    # Split full_name into first_name and last_name
    name_parts = user_in.full_name.split(' ', 1)
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else ""
    
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        first_name=first_name,
        last_name=last_name,
        user_type=user_in.user_type,
        is_active=user_in.is_active,
        is_verified=user_in.is_verified,
        phone_number=user_in.phone_number,
        artist_bio=user_in.artist_bio,
        artist_portfolio_url=user_in.artist_portfolio_url,
        business_name=user_in.business_name,
        business_registration_number=user_in.business_registration_number,
        business_address=user_in.business_address,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_user(db: Session, user: User, user_in: UserUpdate) -> User:
    update_data = user_in.dict(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    for field, value in update_data.items():
        setattr(user, field, value)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def verify_email_token(db: Session, token: str) -> Optional[User]:
    """Verify email token - handles both JWT tokens and direct tokens stored in database"""
    print(f"Verifying token: {token}")
    
    # First try to verify as a JWT token
    from app.core.security import verify_email_token as verify_jwt_token
    email = verify_jwt_token(token)
    
    # If JWT verification succeeded, find the user by email
    if email:
        print(f"JWT token valid for email: {email}")
        user = get_user_by_email(db, email=email)
        if user:
            user.is_verified = True
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
    
    # If JWT verification failed, try to find the user with this verification token
    print("JWT verification failed, trying direct token lookup")
    user = db.query(User).filter(
        User.verification_token == token,
        User.verification_token_expires > datetime.utcnow()
    ).first()
    
    if user:
        print(f"Found user with matching verification token: {user.email}")
        user.is_verified = True
        user.verification_token = None  # Clear the token after use
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    print("Token verification failed - no matching user found")
    return None

def send_verification_email(db: Session, *, user: User) -> None:
    from app.services.email_service import send_email
    token = create_email_verification_token(user.email)
    verification_url = f"{settings.FRONTEND_URL}/verify-email/{token}"
    send_email(
        email_to=user.email,
        subject="Verify your email",
        html_content=f"""
            <p>Hi {user.full_name},</p>
            <p>Please verify your email by clicking the link below:</p>
            <p><a href="{verification_url}">Verify Email</a></p>
            <p>This link will expire in 24 hours.</p>
            <p>Best regards,<br>Okyke Team</p>
        """,
    ) 