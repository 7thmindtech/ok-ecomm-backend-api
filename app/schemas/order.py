from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
from app.models.models import OrderStatus

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"

class OrderItemBase(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)
    customizations: Dict[str, str] = Field(default_factory=dict)

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemUpdate(BaseModel):
    quantity: Optional[int] = Field(None, gt=0)
    customizations: Optional[Dict[str, str]] = None

class OrderItemResponse(OrderItemBase):
    id: int
    order_id: int
    price: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    shipping_address_id: int
    billing_address_id: int
    shipping_id: int
    items: List[OrderItemCreate]
    subtotal: float = Field(gt=0)
    shipping_cost: float = Field(ge=0)
    tax: float = Field(ge=0)
    total_amount: float = Field(gt=0)

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    payment_status: Optional[PaymentStatus] = None

class OrderResponse(OrderBase):
    id: int
    user_id: int
    status: OrderStatus
    payment_status: PaymentStatus
    payment_intent_id: Optional[str] = None
    items: List[OrderItemResponse]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 