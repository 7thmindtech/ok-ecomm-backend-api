from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum
from .user import UserBase, ArtistResponse
from .category import CategoryBase

class ProductStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class ProductImageBase(BaseModel):
    url: str
    alt_text: Optional[str] = None
    position: int = 0

class ProductImageCreate(ProductImageBase):
    product_id: int

class ProductImageResponse(ProductImageBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    category_id: int
    artist_id: Optional[int] = None
    status: ProductStatus = ProductStatus.DRAFT
    specifications: Optional[Dict[str, Any]] = None
    colors: Optional[List[Dict[str, str]]] = None
    sizes: Optional[List[str]] = None
    dimensions: Optional[Dict[str, float]] = None
    weight: Optional[float] = None
    materials: Optional[List[str]] = None
    customization_options: Optional[Dict[str, Any]] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    is_featured: bool = False
    is_customizable: bool = False
    low_stock_threshold: int = Field(default=10, ge=0)

class ProductCreate(ProductBase):
    slug: Optional[str] = None
    
    @validator('artist_id')
    def artist_id_can_be_none(cls, v):
        # Artist ID is optional but if provided must be a positive integer
        if v is not None and v <= 0:
            raise ValueError("If provided, artist_id must be a positive integer")
        return v

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    category_id: Optional[int] = None
    artist_id: Optional[int] = None
    status: Optional[ProductStatus] = None
    specifications: Optional[Dict[str, Any]] = None
    colors: Optional[List[Dict[str, str]]] = None
    sizes: Optional[List[str]] = None
    dimensions: Optional[Dict[str, float]] = None
    weight: Optional[float] = None
    materials: Optional[List[str]] = None
    customization_options: Optional[Dict[str, Any]] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    is_featured: Optional[bool] = None
    is_customizable: Optional[bool] = None
    low_stock_threshold: Optional[int] = Field(None, ge=0)
    featured_image_id: Optional[int] = None
    published_at: Optional[datetime] = None

class ProductResponse(ProductBase):
    id: int
    slug: str
    images: List[ProductImageResponse] = []
    featured_image: Optional[ProductImageResponse] = None
    views_count: int = 0
    sales_count: int = 0
    rating: float = 0.0
    reviews_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    category: Optional[CategoryBase] = None
    artist: Optional[ArtistResponse] = None

    class Config:
        from_attributes = True

class PaginatedProductRead(BaseModel):
    total: int
    page: int
    size: int
    items: List[ProductResponse]

    class Config:
        from_attributes = True