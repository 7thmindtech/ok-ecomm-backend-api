from typing import List
from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.db.base_class import Base
from enum import Enum as PyEnum
from app.utils.slugify import slugify

class UserType(str, PyEnum):
    CUSTOMER = "customer"
    ADMIN = "admin"

class UserRole(str, PyEnum):
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

class ProductStatus(str, PyEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class OrderStatus(str, PyEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class ShippingStatus(str, PyEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    FAILED = "failed"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    user_type = Column(Enum(UserType), default=UserType.CUSTOMER)
    role = Column(Enum(UserRole), default=UserRole.USER)
    phone_number = Column(String, nullable=True)
    
    # Verification and reset tokens
    verification_token = Column(String, nullable=True)
    verification_token_expires = Column(DateTime, nullable=True)
    reset_password_token = Column(String, nullable=True)
    reset_password_token_expires = Column(DateTime, nullable=True)
    
    # Optional fields based on user type
    artist_bio = Column(String, nullable=True)
    artist_portfolio_url = Column(String, nullable=True)
    business_name = Column(String, nullable=True)
    business_registration_number = Column(String, nullable=True)
    business_address = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    addresses = relationship("Address", back_populates="user", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")
    cart = relationship("Cart", back_populates="user", uselist=False, cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    
    @property
    def full_name(self) -> str:
        """Return the user's full name by combining first_name and last_name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or ""

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    slug = Column(String(255), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    
    # Relationships
    parent = relationship("Category", remote_side=[id], backref="children")
    products = relationship("Product", back_populates="category", cascade="all, delete-orphan")
    
    def __init__(self, **kwargs):
        if 'name' in kwargs and 'slug' not in kwargs:
            kwargs['slug'] = slugify(kwargs['name'])
        super().__init__(**kwargs)

class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete='CASCADE'), nullable=False)
    url = Column(String, nullable=False)
    alt_text = Column(String)
    position = Column(Integer, nullable=False, server_default='0')
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    product = relationship("Product", back_populates="images", foreign_keys=[product_id])
    featured_in_products = relationship("Product", back_populates="featured_image", foreign_keys="[Product.featured_image_id]")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    artist_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(Enum(ProductStatus), nullable=False, default=ProductStatus.DRAFT)
    
    # Additional fields for detailed product info
    specifications = Column(JSON)  # Store product specs as JSON
    colors = Column(JSON)  # Available colors e.g. [{"name": "Red", "value": "#FF0000"}, ...]
    sizes = Column(JSON) # Available sizes e.g. ["S", "M", "L"]
    dimensions = Column(JSON)  # Product dimensions
    weight = Column(Float)
    materials = Column(JSON)
    customization_options = Column(JSON)  # Available customization options
    
    # SEO and display
    meta_title = Column(String)
    meta_description = Column(String)
    slug = Column(String, unique=True, index=True)
    
    # Media
    images = relationship("ProductImage", back_populates="product", foreign_keys=[ProductImage.product_id], cascade="all, delete-orphan")
    featured_image_id = Column(Integer, ForeignKey("product_images.id"))
    featured_image = relationship("ProductImage", back_populates="featured_in_products", foreign_keys=[featured_image_id])
    
    # Tracking
    views_count = Column(Integer, server_default='0', nullable=False)
    sales_count = Column(Integer, server_default='0', nullable=False)
    rating = Column(Float, server_default='0', nullable=False)
    reviews_count = Column(Integer, server_default='0', nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    category = relationship("Category", back_populates="products")
    artist = relationship("User", foreign_keys=[artist_id])
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")
    
    # Inventory tracking
    low_stock_threshold = Column(Integer, server_default='10', nullable=False)
    is_featured = Column(Boolean, server_default='false', nullable=False)
    is_customizable = Column(Boolean, server_default='false', nullable=False)
    
    # Cart and Order relationships
    cart_items = relationship("CartItem", back_populates="product", cascade="all, delete-orphan")
    order_items = relationship("OrderItem", back_populates="product", cascade="all, delete-orphan")
    
    # Customization relationship
    customizations = relationship("ProductCustomization", back_populates="product", cascade="all, delete-orphan")

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text)
    reviewer_name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="reviews")
    product = relationship("Product", back_populates="reviews")

class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="cart")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")

class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    # Link to the specific customization instead of storing JSON blob here
    product_customization_id = Column(Integer, ForeignKey("product_customizations.id"), nullable=True) 
    # Keep customization JSON for non-saved or simpler cases if needed, or remove later
    # customization = Column(JSON) 
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    cart = relationship("Cart", back_populates="items")
    product = relationship("Product", back_populates="cart_items")
    customization = relationship("ProductCustomization", back_populates="cart_item") # New relationship

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.PENDING)
    payment_status = Column(String, nullable=False, default="pending")
    total_amount = Column(Float, nullable=False)
    shipping_address_id = Column(Integer, ForeignKey("addresses.id"), nullable=False)
    shipping_id = Column(Integer, ForeignKey("shipping.id"), nullable=False)
    billing_address_id = Column(Integer, ForeignKey("addresses.id"), nullable=False)
    subtotal = Column(Float, nullable=True)
    shipping_cost = Column(Float, nullable=True)
    tax = Column(Float, nullable=True)
    payment_intent_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    shipping_address = relationship("Address", foreign_keys=[shipping_address_id])
    billing_address = relationship("Address", foreign_keys=[billing_address_id])
    shipping = relationship("Shipping")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False) # Price at the time of order
    # Link to the specific customization
    product_customization_id = Column(Integer, ForeignKey("product_customizations.id"), nullable=True)
    # Keep customization JSON for non-saved or simpler cases if needed, or remove later
    # customization = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
    customization = relationship("ProductCustomization", back_populates="order_item") # New relationship
    
    @property
    def price(self):
        return self.unit_price

class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    full_name = Column(String, nullable=True)
    address_line1 = Column(String, nullable=False)
    address_line2 = Column(String)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    postal_code = Column(String, nullable=False)
    country = Column(String, nullable=False)
    phone_number = Column(String, nullable=True)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="addresses")

class Shipping(Base):
    __tablename__ = "shipping"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    estimated_days = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# New Table for Product Customizations
class ProductCustomization(Base):
    __tablename__ = "product_customizations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    
    # Store the state of the design tool (e.g., fabric.js JSON)
    canvas_state = Column(JSON, nullable=True) 
    
    # Store the URL/path of the final rendered image (e.g., in S3)
    rendered_image_url = Column(String(512), nullable=False) 
    
    # Store selected product attributes for this customization
    selected_attributes = Column(JSON, nullable=True) # e.g., {"size": "M", "color": "#FF0000"}
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User") # Add back_populates if needed on User model
    product = relationship("Product", back_populates="customizations")
    
    # Relationships back to cart/order items using this customization
    # Using uselist=False because one customization instance should belong to only one cart item or order item
    cart_item = relationship("CartItem", back_populates="customization", uselist=False) 
    order_item = relationship("OrderItem", back_populates="customization", uselist=False) 