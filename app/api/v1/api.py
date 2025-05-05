from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth_router,
    products_router,
    users_router,
    shipping_router,
    orders_router,
    cart_router,
    health_router,
    categories_router,
    reviews_router,
    addresses_router,
    customize
)

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(products_router, prefix="/products", tags=["products"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(shipping_router, prefix="/shipping", tags=["shipping"])
api_router.include_router(orders_router, prefix="/orders", tags=["orders"])
api_router.include_router(cart_router, prefix="/cart", tags=["cart"])
api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(categories_router, prefix="/categories", tags=["categories"])
api_router.include_router(reviews_router, prefix="/products", tags=["reviews"])
api_router.include_router(addresses_router, prefix="/addresses", tags=["addresses"])
api_router.include_router(customize.router, prefix="/customize", tags=["customize"]) 