from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import jwt
from app.core.config import settings
from app.core.database import get_db
from app.models.models import User
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Your session has expired. Please log in again.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        raise credentials_exception
    
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.JWTError:
        raise credentials_exception
    
    try:
        # If user_id is an email, try to find user by email
        if '@' in user_id:
            user = db.query(User).filter(User.email == user_id).first()
        else:
            # Try to convert to integer if it's not an email
            try:
                user_id_int = int(user_id)
                user = db.query(User).filter(User.id == user_id_int).first()
            except ValueError:
                # If conversion fails, raise exception
                raise credentials_exception
    except Exception as e:
        print(f"Error retrieving user: {str(e)}")
        raise credentials_exception
    
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return user 