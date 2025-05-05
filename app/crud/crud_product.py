from typing import Any, Dict, Optional, Union, List
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from app.crud.base import CRUDBase
from app.models.models import Product, ProductImage, Category
from app.schemas.product import ProductCreate, ProductUpdate
from app.schemas.category import CategoryCreate, CategoryUpdate
from datetime import datetime

class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[Product]:
        return db.query(Product).filter(Product.name == name).first()

    def get_by_artist(self, db: Session, *, artist_id: str) -> List[Product]:
        return db.query(Product).filter(Product.artist_id == artist_id).all()

    def get_by_category(self, db: Session, *, category: str) -> List[Product]:
        return db.query(Product).filter(Product.category == category).all()

    def create_with_image(
        self, db: Session, *, obj_in: ProductCreate, image_url: Optional[str] = None
    ) -> Product:
        db_obj = Product(
            name=obj_in.name,
            description=obj_in.description,
            price=obj_in.price,
            category=obj_in.category,
            artist_id=obj_in.artist_id,
            stock=obj_in.stock,
            image_url=image_url,
            customization_options=obj_in.customization_options,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

product = CRUDProduct(Product)

class CRUDCategory(CRUDBase[Category, CategoryCreate, CategoryUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[Category]:
        return db.query(Category).filter(Category.name == name).first()

category = CRUDCategory(Category) 