from typing import Any, Dict, Optional, Union, List
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.models import Shipping
from app.schemas.shipping import ShippingCreate, ShippingUpdate

class CRUDShipping(CRUDBase[Shipping, ShippingCreate, ShippingUpdate]):
    def get_by_order_id(self, db: Session, *, order_id: int) -> Optional[Shipping]:
        return db.query(Shipping).filter(Shipping.order_id == order_id).first()

    def update_status(
        self, db: Session, *, db_obj: Shipping, status: str
    ) -> Shipping:
        db_obj.status = status
        db.commit()
        db.refresh(db_obj)
        return db_obj

shipping = CRUDShipping(Shipping) 