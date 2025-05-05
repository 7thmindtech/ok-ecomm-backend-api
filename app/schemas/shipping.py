from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from app.models.models import ShippingStatus

class ShippingRate(BaseModel):
    id: str
    name: str
    description: str
    cost: float
    estimated_days: str

class ShippingCalculationRequest(BaseModel):
    country: str
    postal_code: str

class ShippingBase(BaseModel):
    order_id: int
    tracking_number: Optional[str] = None
    carrier: Optional[str] = None
    status: ShippingStatus = ShippingStatus.PENDING
    estimated_delivery: Optional[datetime] = None
    shipping_cost: Optional[float] = None

class ShippingCreate(ShippingBase):
    pass

class ShippingUpdate(BaseModel):
    tracking_number: Optional[str] = None
    carrier: Optional[str] = None
    status: Optional[ShippingStatus] = None
    estimated_delivery: Optional[datetime] = None
    shipping_cost: Optional[float] = None

class Shipping(ShippingBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True