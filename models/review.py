from sqlalchemy import Column, String, Integer, ForeignKey, Float, Text, Boolean
from sqlalchemy.orm import relationship
from .base import Base

class Review(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    rating = Column(Float, nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    is_verified_purchase = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="reviews")
    product = relationship("Product", back_populates="reviews") 