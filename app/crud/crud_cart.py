from typing import Any, Dict, Optional, Union, List
from sqlalchemy.orm import Session, joinedload
from app.crud.base import CRUDBase
from app.models.models import Cart, CartItem
from app.schemas.cart import CartCreate, CartUpdate, CartItemCreate, CartItemUpdate
import logging

logger = logging.getLogger(__name__)

class CRUDCart(CRUDBase[Cart, CartCreate, CartUpdate]):
    def get_by_user(self, db: Session, *, user_id: int) -> Optional[Cart]:
        return db.query(Cart).options(joinedload(Cart.items).joinedload(CartItem.product)).filter(Cart.user_id == user_id).first()

    def create_cart(self, db: Session, user_id: int) -> Cart:
        db_cart = Cart(user_id=user_id)
        db.add(db_cart)
        db.commit()
        db.refresh(db_cart)
        return db_cart

    def remove_cart(self, db: Session, cart_id: int) -> bool:
        db_cart = db.query(Cart).filter(Cart.id == cart_id).first()
        if db_cart:
            db.delete(db_cart)
            db.commit()
            return True
        return False

class CRUDCartItem:
    def get_cart_item(self, db: Session, cart_id: int, product_id: int, product_customization_id: Optional[int] = None) -> Optional[CartItem]:
        """Finds a cart item based on product and optionally customization ID."""
        query = db.query(CartItem).filter(
            CartItem.cart_id == cart_id,
            CartItem.product_id == product_id
        )
        # If a customization ID is provided, match it exactly.
        # If it's None, match items that also have customization ID as None.
        query = query.filter(CartItem.product_customization_id == product_customization_id)
            
        return query.first()

    def add_item_to_cart(self, db: Session, cart_id: int, item: CartItemCreate) -> CartItem:
        """Adds an item to the cart or updates quantity if it exists."""
        # Check if the exact item (product + customization) already exists
        db_item = self.get_cart_item(db, cart_id, item.product_id, item.product_customization_id)

        if db_item:
            # Update quantity
            db_item.quantity += item.quantity
            logger.info(f"Updated quantity for CartItem {db_item.id} to {db_item.quantity}")
        else:
            # Create new cart item
            db_item = CartItem(
                cart_id=cart_id,
                product_id=item.product_id,
                quantity=item.quantity,
                product_customization_id=item.product_customization_id
            )
            db.add(db_item)
            logger.info(f"Added new CartItem for product {item.product_id} (Customization: {item.product_customization_id})")
        
        db.commit()
        db.refresh(db_item)
        return db_item

    def update_cart_item(self, db: Session, cart_item_id: int, item_update: CartItemUpdate) -> Optional[CartItem]:
        """Updates a specific cart item (e.g., quantity)."""
        db_item = db.query(CartItem).filter(CartItem.id == cart_item_id).first()
        if db_item:
            if item_update.quantity is not None:
                db_item.quantity = item_update.quantity
            # Note: Updating product_customization_id might be complex, 
            # usually users would remove and add a new customized item. 
            # If needed, add logic here.
            # if item_update.product_customization_id is not None:
            #     db_item.product_customization_id = item_update.product_customization_id
                
            db.commit()
            db.refresh(db_item)
            logger.info(f"Updated CartItem {db_item.id}")
        return db_item

    def remove_cart_item(self, db: Session, cart_item_id: int) -> bool:
        """Removes an item from the cart by its ID."""
        db_item = db.query(CartItem).filter(CartItem.id == cart_item_id).first()
        if db_item:
            db.delete(db_item)
            db.commit()
            logger.info(f"Removed CartItem {db_item.id}")
            return True
        return False

    def clear_cart(self, db: Session, cart_id: int) -> int:
        """Removes all items from a specific cart. Returns the number of items removed."""
        num_deleted = db.query(CartItem).filter(CartItem.cart_id == cart_id).delete()
        db.commit()
        logger.info(f"Cleared {num_deleted} items from Cart ID {cart_id}")
        return num_deleted

cart = CRUDCart(Cart)
cart_item = CRUDCartItem() 