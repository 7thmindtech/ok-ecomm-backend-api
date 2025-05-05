from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app import models, schemas, crud
from app.api import deps

router = APIRouter()

@router.get("/", response_model=schemas.CartRead)
def get_cart(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Get the current user's cart, creating one if it doesn't exist.
    Includes cart items with product and customization details.
    """
    cart = crud.cart.get_cart_by_user_id(db, user_id=current_user.id)
    if not cart:
        cart = crud.cart.create_cart(db, user_id=current_user.id)
        
    # Ensure items relationship is loaded with necessary details
    # The crud function already handles joinedload, but we can be explicit if needed
    db.refresh(cart) # Refresh to potentially load items if newly created

    # Explicitly load product and customization details for each item
    # This might be redundant if crud.get_cart_by_user_id handles it correctly
    # but ensures the data is present for the response model.
    cart_items = db.query(models.CartItem).options(
        joinedload(models.CartItem.product).joinedload(models.Product.featured_image),
        joinedload(models.CartItem.customization) 
    ).filter(models.CartItem.cart_id == cart.id).all()
    
    # Manually construct the response if necessary to fit CartRead schema
    cart_data = schemas.CartRead.from_orm(cart)
    cart_data.items = [schemas.CartItemRead.from_orm(item) for item in cart_items]

    return cart_data

@router.post("/items", response_model=schemas.CartItemRead)
def add_item_to_cart(
    item: schemas.CartItemCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Add an item (potentially customized) to the user's cart.
    Requires product_id and optionally product_customization_id.
    """
    cart = crud.cart.get_cart_by_user_id(db, user_id=current_user.id)
    if not cart:
        cart = crud.cart.create_cart(db, user_id=current_user.id)
        
    # Validate product exists (optional)
    product = crud.product.get(db, id=item.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    # Validate customization exists if ID is provided
    if item.product_customization_id:
        customization = crud.get_product_customization(db, item.product_customization_id)
        if not customization or customization.user_id != current_user.id:
             raise HTTPException(status_code=404, detail="Customization not found or does not belong to user")
        # Ensure customization matches product
        if customization.product_id != item.product_id:
            raise HTTPException(status_code=400, detail="Customization does not match the specified product")
            
    db_item = crud.cart_item.add_item_to_cart(db=db, cart_id=cart.id, item=item)
    
    # Reload item with relationships for response model
    db_item_loaded = db.query(models.CartItem).options(
        joinedload(models.CartItem.product).joinedload(models.Product.featured_image),
        joinedload(models.CartItem.customization)
    ).filter(models.CartItem.id == db_item.id).first()
        
    return db_item_loaded

@router.put("/items/{item_id}", response_model=schemas.CartItemRead)
def update_cart_item_quantity(
    item_id: int,
    item_update: schemas.CartItemUpdate, # Schema likely only contains quantity now
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Update a cart item's quantity.
    """
    cart = crud.cart.get_cart_by_user_id(db, user_id=current_user.id)
    if not cart:
         raise HTTPException(status_code=404, detail="Cart not found")
         
    db_item = db.query(models.CartItem).filter(
        models.CartItem.id == item_id,
        models.CartItem.cart_id == cart.id # Ensure item belongs to user's cart
    ).first()
    
    if not db_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    # Only update quantity from the schema
    updated_item = crud.cart_item.update_cart_item(db, cart_item_id=item_id, item_update=item_update)

    # Reload item with relationships for response model
    db_item_loaded = db.query(models.CartItem).options(
        joinedload(models.CartItem.product).joinedload(models.Product.featured_image),
        joinedload(models.CartItem.customization)
    ).filter(models.CartItem.id == updated_item.id).first()

    return db_item_loaded

@router.delete("/items/{item_id}", status_code=204) # Return 204 No Content
def remove_item_from_cart(
    item_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Remove an item from the cart.
    """
    cart = crud.cart.get_cart_by_user_id(db, user_id=current_user.id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    # Verify the item belongs to the user's cart before deleting
    db_item = db.query(models.CartItem).filter(
        models.CartItem.id == item_id,
        models.CartItem.cart_id == cart.id
    ).first()

    if not db_item:
        raise HTTPException(status_code=404, detail="Cart item not found in user's cart")
        
    deleted = crud.cart_item.remove_cart_item(db, cart_item_id=item_id)
    if not deleted:
         # This shouldn't happen if the check above passed, but included for safety
        raise HTTPException(status_code=404, detail="Cart item not found for deletion")
        
    return None # Return None for 204 status


@router.delete("/", status_code=204) # Return 204 No Content
def clear_user_cart(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Clear all items from the user's cart.
    """
    cart = crud.cart.get_cart_by_user_id(db, user_id=current_user.id)
    if cart:
        crud.cart_item.clear_cart(db, cart_id=cart.id)
    # No error if cart doesn't exist, just do nothing
    
    return None # Return None for 204 status 