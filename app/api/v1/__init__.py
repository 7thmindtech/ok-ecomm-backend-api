from fastapi import APIRouter
from .endpoints.auth import router as auth_router
from .endpoints.products import router as products_router
from .endpoints.users import router as users_router
from .endpoints.shipping import router as shipping_router
from .endpoints.orders import router as orders_router
from .endpoints.cart import router as cart_router
from .endpoints.health import router as health_router
from .endpoints.categories import router as categories_router
from .endpoints.addresses import router as addresses_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(products_router, prefix="/products", tags=["products"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(shipping_router, prefix="/shipping", tags=["shipping"])
api_router.include_router(orders_router, prefix="/orders", tags=["orders"])
api_router.include_router(cart_router, prefix="/cart", tags=["cart"])
api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(categories_router, prefix="/categories", tags=["categories"])
api_router.include_router(addresses_router, prefix="/addresses", tags=["addresses"]) 