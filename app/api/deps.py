from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.models import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login", auto_error=False)

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

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
    except JWTError:
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

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

async def get_current_active_superuser(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Get current active user and verify they have admin privileges.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user

async def get_current_user_optional(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme)
) -> Optional[User]:
    """
    Similar to get_current_user but doesn't raise an exception if no token is provided.
    Returns None instead.
    """
    if not token:
        return None
    
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if not user_id:
            return None
    except JWTError:
        return None
    
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
                # If conversion fails, return None
                return None
    except Exception as e:
        print(f"Error retrieving user: {str(e)}")
        return None
        
    if not user:
        return None
    
    return user 