# Import all the models here so that Base has them before being
# imported by Alembic or any other code
from app.db.base_class import Base
from app.models.models import (
    User,
    Category,
    Product,
    ProductImage,
    Review,
    CartItem,
    OrderItem,
    Order,
    UserType,
    UserRole,
    ProductStatus
)

# Make sure all models are imported before initializing the database
__all__ = [
    "Base",
    "Address",
    "User", 
    "Category",
    "Product", 
    "ProductImage", 
    "Cart", 
    "CartItem", 
    "Order", 
    "OrderItem", 
    "Shipping",
    "Review"
] 