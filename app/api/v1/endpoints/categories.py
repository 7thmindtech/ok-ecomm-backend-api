from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query, UploadFile, File, Body
from sqlalchemy.orm import Session
from app.api import deps
from app.models.models import Category, User, UserRole
from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
)
from app.utils.slugify import slugify
from app.core.storage import upload_file_to_s3, delete_file_from_s3
import uuid

router = APIRouter()

@router.get("/", response_model=List[CategoryResponse])
async def get_categories(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    include_inactive: Optional[bool] = False,
    parent_id: Optional[int] = None
):
    """
    Get all categories with optional filtering.
    """
    try:
        query = db.query(Category)
        
        # Filter by active status
        if not include_inactive:
            query = query.filter(Category.is_active == True)
        
        # Filter by parent_id
        if parent_id is not None:
            query = query.filter(Category.parent_id == parent_id)
        
        # Get paginated results
        categories = query.offset(skip).limit(limit).all()
        return categories
    except Exception as e:
        # Log the exception
        print(f"Error fetching categories: {str(e)}")
        # Return empty list instead of raising an exception
        return []

@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int = Path(..., title="The ID of the category to get"),
    db: Session = Depends(deps.get_db)
):
    """
    Get a specific category by ID.
    """
    try:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return category
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching category {category_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/", response_model=CategoryResponse)
async def create_category(
    category_data: dict = Body(None),
    category: CategoryCreate = None,
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Create a new category.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Handle both direct JSON and nested "category" field
    if category is None and category_data:
        # Direct JSON approach (used by upload_products.py)
        if "name" not in category_data:
            raise HTTPException(status_code=422, detail="Name is required")
        
        category_obj = CategoryCreate(
            name=category_data["name"],
            description=category_data.get("description"),
            is_active=category_data.get("is_active", True),
            parent_id=category_data.get("parent_id")
        )
    elif category:
        # Schema validation approach (used by frontend)
        category_obj = category
    else:
        raise HTTPException(status_code=422, detail="Category data is required")

    # Handle image upload if provided
    image_url = None
    if image:
        file_extension = image.filename.split('.')[-1]
        filename = f"{uuid.uuid4()}.{file_extension}"
        image_url = await upload_file_to_s3(image.file, filename, "categories")

    db_category = Category(
        name=category_obj.name,
        description=category_obj.description,
        image_url=image_url,
        parent_id=category_obj.parent_id,
        is_active=category_obj.is_active,
        slug=slugify(category_obj.name)
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category: CategoryUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    image: Optional[UploadFile] = File(None),
):
    """
    Update a category.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Handle image upload if provided
    if image:
        # Delete old image if it exists
        if db_category.image_url:
            old_filename = db_category.image_url.split("/")[-1]
            await delete_file_from_s3(old_filename, "categories")

        # Upload new image
        file_extension = image.filename.split('.')[-1]
        filename = f"{uuid.uuid4()}.{file_extension}"
        image_url = await upload_file_to_s3(image.file, filename, "categories")
        db_category.image_url = image_url

    # Update other fields
    for key, value in category.dict(exclude_unset=True).items():
        setattr(db_category, key, value)

    db.commit()
    db.refresh(db_category)
    return db_category

@router.delete("/{category_id}", response_model=CategoryResponse)
async def delete_category(
    category_id: int = Path(..., title="The ID of the category to delete"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Delete a category.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Delete image from S3 if it exists
    if category.image_url:
        filename = category.image_url.split("/")[-1]
        await delete_file_from_s3(filename, "categories")

    db.delete(category)
    db.commit()
    return {"message": "Category deleted successfully"} 