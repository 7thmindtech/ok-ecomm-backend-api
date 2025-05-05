from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.deps import get_current_active_user, get_current_active_superuser, get_db
from app.crud import crud_shipping
from app.schemas.shipping import Shipping, ShippingCreate, ShippingUpdate
from app.schemas.user import UserResponse
from app.models.models import User

router = APIRouter()

@router.get("/", response_model=List[Shipping])
def read_shipping(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Retrieve shipping records.
    """
    shipping = crud_shipping.get_multi(db, skip=skip, limit=limit)
    return shipping

@router.post("/", response_model=Shipping)
def create_shipping(
    *,
    db: Session = Depends(get_db),
    shipping_in: ShippingCreate,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Create new shipping record.
    """
    shipping = crud_shipping.create(db, obj_in=shipping_in)
    return shipping

@router.get("/{shipping_id}", response_model=Shipping)
def read_shipping(
    shipping_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get shipping record by ID.
    """
    shipping = crud_shipping.get(db, id=shipping_id)
    if not shipping:
        raise HTTPException(
            status_code=404,
            detail="Shipping record not found",
        )
    return shipping

@router.put("/{shipping_id}", response_model=Shipping)
def update_shipping(
    *,
    db: Session = Depends(get_db),
    shipping_id: int,
    shipping_in: ShippingUpdate,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Update shipping record.
    """
    shipping = crud_shipping.get(db, id=shipping_id)
    if not shipping:
        raise HTTPException(
            status_code=404,
            detail="Shipping record not found",
        )
    shipping = crud_shipping.update(db, db_obj=shipping, obj_in=shipping_in)
    return shipping

@router.delete("/{shipping_id}", response_model=Shipping)
def delete_shipping(
    *,
    db: Session = Depends(get_db),
    shipping_id: int,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Delete shipping record.
    """
    shipping = crud_shipping.get(db, id=shipping_id)
    if not shipping:
        raise HTTPException(
            status_code=404,
            detail="Shipping record not found",
        )
    shipping = crud_shipping.remove(db, id=shipping_id)
    return shipping 