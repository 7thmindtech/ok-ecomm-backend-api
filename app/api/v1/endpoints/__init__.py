# Import and export routers
from .auth import router as auth_router
from .products import router as products_router
from .users import router as users_router
from .shipping import router as shipping_router
from .orders import router as orders_router
from .cart import router as cart_router
from .health import router as health_router
from .categories import router as categories_router
from .reviews import router as reviews_router
from .addresses import router as addresses_router

__all__ = [
    "auth_router",
    "products_router",
    "users_router",
    "shipping_router",
    "orders_router",
    "cart_router",
    "health_router",
    "categories_router",
    "reviews_router",
    "addresses_router"
] 