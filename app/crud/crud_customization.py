from sqlalchemy.orm import Session
from typing import Optional, Dict, Any

from app.models.models import ProductCustomization
from app.schemas.customization import CustomizationSaveRequest # Use this if needed for creation structure
import logging

logger = logging.getLogger(__name__)

def create_product_customization(
    db: Session,
    user_id: int,
    product_id: int,
    rendered_image_url: str,
    canvas_state: Optional[Dict[str, Any]] = None,
    selected_attributes: Optional[Dict[str, Any]] = None
) -> ProductCustomization:
    """Creates a new product customization record."""
    try:
        db_customization = ProductCustomization(
            user_id=user_id,
            product_id=product_id,
            rendered_image_url=rendered_image_url,
            canvas_state=canvas_state,
            selected_attributes=selected_attributes
        )
        db.add(db_customization)
        db.commit()
        db.refresh(db_customization)
        logger.info(f"Created ProductCustomization record with ID: {db_customization.id}")
        return db_customization
    except Exception as e:
        logger.error(f"Error creating ProductCustomization: {e}")
        db.rollback() # Rollback in case of error
        raise

def get_product_customization(db: Session, customization_id: int) -> Optional[ProductCustomization]:
    """Retrieves a product customization by its ID."""
    return db.query(ProductCustomization).filter(ProductCustomization.id == customization_id).first()

def get_user_product_customizations(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> list[ProductCustomization]:
    """Retrieves all customizations for a specific user."""
    return db.query(ProductCustomization)\
             .filter(ProductCustomization.user_id == user_id)\
             .order_by(ProductCustomization.created_at.desc())\
             .offset(skip)\
             .limit(limit)\
             .all()

def update_product_customization(
    db: Session,
    customization_id: int,
    canvas_state: Optional[Dict[str, Any]] = None,
    rendered_image_url: Optional[str] = None,
    selected_attributes: Optional[Dict[str, Any]] = None
) -> Optional[ProductCustomization]:
    """Updates an existing product customization."""
    db_customization = get_product_customization(db, customization_id)
    if not db_customization:
        return None
    
    update_data = {}
    if canvas_state is not None:
        update_data["canvas_state"] = canvas_state
    if rendered_image_url is not None:
        update_data["rendered_image_url"] = rendered_image_url
    if selected_attributes is not None:
        update_data["selected_attributes"] = selected_attributes
        
    if not update_data:
        logger.warning(f"No update data provided for ProductCustomization ID: {customization_id}")
        return db_customization # Return existing object if no changes

    try:
        for key, value in update_data.items():
            setattr(db_customization, key, value)
            
        db.add(db_customization)
        db.commit()
        db.refresh(db_customization)
        logger.info(f"Updated ProductCustomization record with ID: {customization_id}")
        return db_customization
    except Exception as e:
        logger.error(f"Error updating ProductCustomization ID {customization_id}: {e}")
        db.rollback()
        raise

def delete_product_customization(db: Session, customization_id: int) -> bool:
    """Deletes a product customization. Returns True if deleted, False otherwise."""
    db_customization = get_product_customization(db, customization_id)
    if db_customization:
        try:
            db.delete(db_customization)
            db.commit()
            logger.info(f"Deleted ProductCustomization record with ID: {customization_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting ProductCustomization ID {customization_id}: {e}")
            db.rollback()
            raise
    return False 