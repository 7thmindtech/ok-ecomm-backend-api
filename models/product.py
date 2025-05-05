from sqlalchemy import Boolean, Column, String, Integer, Float, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from .base import Base

class Product(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    base_price = Column(Float, nullable=False)
    artist_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("category.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    stock_quantity = Column(Integer, default=0)
    
    # Customization options
    customization_options = Column(JSON, nullable=False)
    # Example structure:
    # {
    #   "colors": ["red", "blue", "green"],
    #   "sizes": ["S", "M", "L", "XL"],
    #   "materials": ["cotton", "polyester"],
    #   "text_options": {
    #     "max_length": 50,
    #     "fonts": ["Arial", "Times New Roman"]
    #   }
    # }
    
    # Relationships
    artist = relationship("User", back_populates="products")
    category = relationship("Category", back_populates="products")
    images = relationship("ProductImage", back_populates="product")
    reviews = relationship("Review", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")
    cart_items = relationship("CartItem", back_populates="product")

class ProductImage(Base):
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    image_url = Column(String, nullable=False)
    is_primary = Column(Boolean, default=False)
    alt_text = Column(String)
    
    # Relationships
    product = relationship("Product", back_populates="images")

class Category(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    parent_id = Column(Integer, ForeignKey("category.id"), nullable=True)
    
    # Relationships
    products = relationship("Product", back_populates="category")
    parent = relationship("Category", remote_side=[id], backref="children") 