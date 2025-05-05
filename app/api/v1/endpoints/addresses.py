from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.models.models import Address, User
from app.schemas.address import AddressCreate, AddressResponse, AddressUpdate

router = APIRouter()

@router.get("/", response_model=List[AddressResponse])
async def get_addresses(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Get all addresses for the current user.
    """
    addresses = db.query(Address).filter(Address.user_id == current_user.id).all()
    return addresses

@router.post("/", response_model=AddressResponse)
async def create_address(
    address: AddressCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Create a new address for the current user.
    """
    # If this is the first address or is_default is True, make sure it's the only default
    if address.is_default:
        # Reset all other default addresses
        db.query(Address).filter(
            Address.user_id == current_user.id,
            Address.is_default == True
        ).update({"is_default": False})
    
    # Convert Pydantic model to dict - we no longer need to remove full_name
    address_data = address.dict()
    
    # Create new address
    db_address = Address(
        user_id=current_user.id,
        **address_data
    )
    
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    
    return db_address

@router.get("/{address_id}", response_model=AddressResponse)
async def get_address(
    address_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Get a specific address by ID.
    """
    address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == current_user.id
    ).first()
    
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    
    return address

@router.put("/{address_id}", response_model=AddressResponse)
async def update_address(
    address_id: int,
    address_data: AddressUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Update an address.
    """
    db_address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == current_user.id
    ).first()
    
    if not db_address:
        raise HTTPException(status_code=404, detail="Address not found")
    
    # Handle setting new default address
    if address_data.is_default:
        # Reset all other default addresses
        db.query(Address).filter(
            Address.user_id == current_user.id,
            Address.is_default == True,
            Address.id != address_id
        ).update({"is_default": False})
    
    # Update address fields - we no longer need to exclude full_name
    update_data = address_data.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_address, key, value)
    
    db.commit()
    db.refresh(db_address)
    
    return db_address

@router.delete("/{address_id}")
async def delete_address(
    address_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Delete an address.
    """
    db_address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == current_user.id
    ).first()
    
    if not db_address:
        raise HTTPException(status_code=404, detail="Address not found")
    
    db.delete(db_address)
    db.commit()
    
    return {"message": "Address deleted successfully"}

@router.post("/{address_id}/set-default", response_model=AddressResponse)
async def set_default_address(
    address_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Set an address as the default.
    """
    # First reset all addresses
    db.query(Address).filter(
        Address.user_id == current_user.id,
        Address.is_default == True
    ).update({"is_default": False})
    
    # Set the specified address as default
    db_address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == current_user.id
    ).first()
    
    if not db_address:
        raise HTTPException(status_code=404, detail="Address not found")
    
    db_address.is_default = True
    db.commit()
    db.refresh(db_address)
    
    return db_address 