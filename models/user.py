from sqlalchemy import Boolean, Column, String, Enum, Integer, ForeignKey
from sqlalchemy.orm import relationship
import enum
from .base import Base

class UserType(str, enum.Enum):
    CONSUMER = "consumer"
    ARTIST = "artist"
    BUSINESS = "business"
    ADMIN = "admin"

class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    user_type = Column(Enum(UserType), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    phone_number = Column(String)
    
    # Artist specific fields
    artist_bio = Column(String)
    artist_portfolio_url = Column(String)
    
    # Business specific fields
    business_name = Column(String)
    business_registration_number = Column(String)
    business_address = Column(String)
    
    # Relationships
    products = relationship("Product", back_populates="artist")
    orders = relationship("Order", back_populates="user")
    cart = relationship("Cart", back_populates="user", uselist=False)
    addresses = relationship("Address", back_populates="user")
    reviews = relationship("Review", back_populates="user") 