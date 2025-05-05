from typing import Any, Dict, Optional, Union, List
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.models import Order, OrderItem
from app.schemas.order import OrderCreate, OrderUpdate, OrderItemCreate, OrderItemUpdate

class CRUDOrder(CRUDBase[Order, OrderCreate, OrderUpdate]):
    def get_by_user(self, db: Session, *, user_id: int) -> List[Order]:
        return db.query(Order).filter(Order.user_id == user_id).all()

    def get_by_status(self, db: Session, *, status: str) -> List[Order]:
        return db.query(Order).filter(Order.status == status).all()

    def create_with_items(
        self, db: Session, *, obj_in: OrderCreate, items: List[OrderItemCreate]
    ) -> Order:
        db_obj = Order(
            user_id=obj_in.user_id,
            status=obj_in.status,
            total_amount=obj_in.total_amount,
            shipping_address_id=obj_in.shipping_address_id,
            billing_address_id=obj_in.billing_address_id,
            tracking_number=obj_in.tracking_number,
            payment_intent_id=obj_in.payment_intent_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        # Add order items
        for item in items:
            order_item = OrderItem(
                order_id=db_obj.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.price,
            )
            db.add(order_item)
        db.commit()
        return db_obj

order = CRUDOrder(Order) 