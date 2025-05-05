from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class AddressBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=100)
    address_line1: str = Field(..., min_length=1, max_length=100)
    address_line2: Optional[str] = Field(None, max_length=100)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=1, max_length=100)
    postal_code: str = Field(..., min_length=1, max_length=20)
    country: str = Field(..., min_length=2, max_length=100)
    phone_number: str = Field(..., min_length=5, max_length=20)
    is_default: bool = False

class AddressCreate(AddressBase):
    pass

class AddressUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    address_line1: Optional[str] = Field(None, min_length=1, max_length=100)
    address_line2: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    state: Optional[str] = Field(None, min_length=1, max_length=100)
    postal_code: Optional[str] = Field(None, min_length=1, max_length=20)
    country: Optional[str] = Field(None, min_length=2, max_length=100)
    phone_number: Optional[str] = Field(None, min_length=5, max_length=20)
    is_default: Optional[bool] = None

class AddressResponse(AddressBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 