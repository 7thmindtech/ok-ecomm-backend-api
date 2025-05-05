from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.models.models import UserType, UserRole  # Import the enums
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., description="Full name will be split into first_name and last_name")
    user_type: UserType = UserType.CUSTOMER
    is_active: bool = True
    is_verified: bool = False
    phone_number: Optional[str] = None
    
    # Optional fields based on user type
    artist_bio: Optional[str] = None
    artist_portfolio_url: Optional[str] = None
    business_name: Optional[str] = None
    business_registration_number: Optional[str] = None
    business_address: Optional[str] = None

class ArtistResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    artist_bio: Optional[str] = None
    artist_portfolio_url: Optional[str] = None

    class Config:
        from_attributes = True

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserInDBBase(UserBase):
    id: int
    role: UserRole
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserResponse(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: str 