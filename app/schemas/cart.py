from typing import Dict, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from .product import ProductResponse  # Corrected: Import ProductResponse instead of ProductRead
from .customization import ProductCustomizationRead # Import the new customization schema

class CartItemBase(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)
    product_customization_id: Optional[int] = None # Link to customization

class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    quantity: Optional[int] = Field(None, gt=0)
    product_customization_id: Optional[int] = None # Allow updating customization link if needed

class CartItemRead(CartItemBase):
    id: int
    product: ProductResponse  # Corrected: Use ProductResponse here
    customization: Optional[ProductCustomizationRead] = None # Include full customization details if present
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True # Renamed from orm_mode

# Add this class for creating a cart
class CartCreate(BaseModel):
    user_id: int
    is_active: bool = True

# Add this class for updating a cart
class CartUpdate(BaseModel):
    is_active: Optional[bool] = None

# Add this class for the Cart response
class CartResponse(BaseModel):
    id: int
    user_id: int
    is_active: bool
    items: List[CartItemRead]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True # Renamed from orm_mode

# Schema for the cart itself
class CartBase(BaseModel):
    user_id: int

class CartRead(CartBase):
    id: int
    items: List[CartItemRead] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True # Renamed from orm_mode 