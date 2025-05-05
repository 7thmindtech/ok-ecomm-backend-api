from datetime import timedelta, datetime
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Body, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core import security
from app.core.config import settings
from app.core.database import get_db
from app.models.models import User, UserType
from app.schemas.auth import Token, LoginResponse
from app.schemas.user import UserCreate, UserResponse
from app.services import auth_service
import secrets
from app.core.email import send_verification_email
from app.crud import crud_user
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.api import deps

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """
    Register a new user.
    """
    # Check if user exists
    user = auth_service.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    # Create user first
    user = auth_service.create_user(db, user_in=user_in)
    
    # Then set verification token
    verification_token = secrets.token_urlsafe(32)
    token_expires = datetime.utcnow() + timedelta(hours=24)
    
    # Update user with verification token
    user.verification_token = verification_token
    user.verification_token_expires = token_expires
    db.commit()
    db.refresh(user)
    
    # Send verification email
    await send_verification_email(user.email, verification_token)
    
    return user

@router.post("/login", response_model=LoginResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    # Use auth_service to get user by email instead of crud_user directly
    user = auth_service.get_user_by_email(db, email=form_data.username)
    
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    return {
        "token": create_access_token(user.id),
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.full_name,
            "role": user.role
        }
    }

@router.post("/logout")
async def logout(current_user = Depends(deps.get_current_user)) -> Any:
    """
    Logout current user
    """
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=dict)
async def read_users_me(current_user = Depends(deps.get_current_user)) -> Any:
    """
    Get current user.
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.full_name,
        "role": current_user.role
    }

@router.post("/refresh-token")
async def refresh_token(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Refresh access token.
    """
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    return {
        "access_token": create_access_token(
            current_user.id, expires_delta=access_token_expires
        ),
        "refresh_token": create_refresh_token(
            current_user.id, expires_delta=refresh_token_expires
        ),
        "token_type": "bearer",
    }

@router.get("/verify-email/{token}")
def verify_email(
    token: str,
    db: Session = Depends(get_db),
) -> Any:
    """
    Verify user email.
    """
    print(f"Verify email endpoint called with token: {token}")
    user = auth_service.verify_email_token(db, token)
    if not user:
        print(f"Token verification failed for: {token}")
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired token",
        )
    print(f"Token verification successful for user: {user.email}")
    return {"message": "Email verified successfully"}

@router.post("/resend-verification")
async def resend_verification(
    data: dict = Body(...),
    db: Session = Depends(get_db)
):
    """
    Resend verification email to user
    """
    email = data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user.is_verified:
            raise HTTPException(status_code=400, detail="Email already verified")
        
        # Generate a new verification token
        verification_token = secrets.token_urlsafe(32)
        token_expires = datetime.utcnow() + timedelta(hours=24)
        
        # Update user with new verification token
        user.verification_token = verification_token
        user.verification_token_expires = token_expires
        db.commit()
        db.refresh(user)
        
        print(f"Generated new verification token for {email}: {verification_token}")
        
        # Send verification email
        await send_verification_email(user.email, verification_token)
        
        return {"message": "Verification email sent successfully"}
    except Exception as e:
        print(f"Error in resend verification: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to resend verification email: {str(e)}")

@router.post("/forgot-password")
async def forgot_password(
    data: dict = Body(...),
    db: Session = Depends(get_db)
):
    """
    Send password reset email with reset token
    """
    email = data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    try:
        user = auth_service.get_user_by_email(db, email=email)
        if not user:
            # Don't reveal that the user doesn't exist
            return {"message": "If the email exists, a password reset link will be sent"}
        
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        token_expires = datetime.utcnow() + timedelta(hours=24)
        
        # Update user with reset token
        user.reset_password_token = reset_token
        user.reset_password_token_expires = token_expires
        db.commit()
        db.refresh(user)
        
        # Send password reset email
        from app.core.email import send_password_reset_email
        await send_password_reset_email(user.email, reset_token)
        
        return {"message": "If the email exists, a password reset link will be sent"}
    except Exception as e:
        print(f"Error in forgot password: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process password reset: {str(e)}")

@router.post("/reset-password")
async def reset_password(
    data: dict = Body(...),
    db: Session = Depends(get_db)
):
    """
    Reset password using token
    """
    token = data.get("token")
    new_password = data.get("password")
    
    if not token or not new_password:
        raise HTTPException(status_code=400, detail="Token and new password are required")
    
    try:
        # Find user with valid reset token
        user = db.query(User).filter(
            User.reset_password_token == token,
            User.reset_password_token_expires > datetime.utcnow()
        ).first()
        
        if not user:
            raise HTTPException(status_code=400, detail="Invalid or expired reset token")
        
        # Update password
        user.hashed_password = security.get_password_hash(new_password)
        user.reset_password_token = None  # Clear the token after use
        user.reset_password_token_expires = None
        db.commit()
        
        return {"message": "Password successfully reset"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in reset password: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to reset password: {str(e)}")

@router.post("/login-alt")
async def login_alt(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
) -> Any:
    """
    Alternative login endpoint for scripts
    """
    # Use auth_service to get user by email instead of crud_user directly
    user = auth_service.get_user_by_email(db, email=username)
    
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer"
    } 