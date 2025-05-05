# Import all models here for SQLAlchemy to discover them
from app.db.base_class import Base

# Import all models
from app.models.models import *  # noqa

# Make sure all models are imported
__all__ = [
    "Base",
    "Category",
    "Product",
    "ProductImage",
    "ProductStatus",
    "User",
    "UserType",
    "UserRole",
    "Review",
    "Cart",
    "CartItem",
    "Order",
    "OrderItem",
    "Shipping",
    "Address"
]

# Ensure all models are registered with SQLAlchemy
Base.metadata.tables  # This will trigger model registration 