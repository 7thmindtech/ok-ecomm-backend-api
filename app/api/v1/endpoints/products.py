from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Request
from sqlalchemy.orm import Session
from app.api import deps
from app.models.models import Product, ProductStatus, ProductImage
from app.models.models import User, UserRole
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse,
    ProductImageCreate, ProductImageResponse
)
from app.services.storage import upload_file
from app.utils.slugify import slugify
from datetime import datetime
import logging
import os
from app.core.config import settings

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

router = APIRouter()

@router.get("/", response_model=dict)
async def get_products(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 20,
    category_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    status: Optional[ProductStatus] = None,
    is_featured: Optional[bool] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = "created_at",
    sort_order: Optional[str] = "desc",
    current_user: Optional[User] = Depends(deps.get_current_user_optional),
):
    """
    Get products with filtering and sorting.
    If user is admin, include draft products.
    """
    try:
        query = db.query(Product)
        
        # Base filters
        if not current_user or current_user.role != UserRole.ADMIN:
            query = query.filter(Product.status == ProductStatus.PUBLISHED)
        
        # Apply filters
        if category_id:
            query = query.filter(Product.category_id == category_id)
        if min_price is not None:
            query = query.filter(Product.price >= min_price)
        if max_price is not None:
            query = query.filter(Product.price <= max_price)
        if status and current_user and current_user.role == UserRole.ADMIN:
            query = query.filter(Product.status == status)
        if is_featured is not None:
            query = query.filter(Product.is_featured == is_featured)
        if search:
            search = f"%{search}%"
            query = query.filter(
                (Product.name.ilike(search)) |
                (Product.description.ilike(search)) |
                (Product.meta_title.ilike(search)) |
                (Product.meta_description.ilike(search))
            )
        
        # Apply sorting
        sort_column = getattr(Product, sort_by, Product.created_at)
        if sort_order == "desc":
            sort_column = sort_column.desc()
        query = query.order_by(sort_column)
        
        # Get total count for pagination
        total = query.count()
        
        # Apply pagination
        db_products = query.offset(skip).limit(limit).all()
        
        # Convert to simplified dict to avoid relationship issues
        products = []
        for product in db_products:
            # Get the featured image URL if it exists
            featured_image_url = None
            if product.featured_image:
                featured_image_url = product.featured_image.url
            
            # Get product images
            images = []
            for image in product.images:
                images.append({
                    "id": image.id,
                    "url": image.url,
                    "alt_text": image.alt_text,
                    "position": image.position
                })
            
            # Create a simplified product dict
            products.append({
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "stock": product.stock,
                "status": product.status,
                "slug": product.slug,
                "featured_image_url": featured_image_url,
                "created_at": product.created_at.isoformat() if product.created_at else None,
                "updated_at": product.updated_at.isoformat() if product.updated_at else None,
                "published_at": product.published_at.isoformat() if product.published_at else None,
                "category_id": product.category_id,
                "views_count": product.views_count,
                "sales_count": product.sales_count,
                "rating": product.rating,
                "reviews_count": product.reviews_count,
                "is_featured": product.is_featured,
                "is_customizable": product.is_customizable,
                "images": images,
                "low_stock_threshold": product.low_stock_threshold or 10
            })
        
        return {
            "items": products,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Error getting products: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/{product_id_or_slug}")
def get_product(
    product_id_or_slug: str,
    db: Session = Depends(deps.get_db),
):
    """
    Get a specific product by ID or slug.
    """
    try:
        # First try to parse the input as an integer (id)
        try:
            product_id = int(product_id_or_slug)
            product = db.query(Product).filter(Product.id == product_id).first()
        except ValueError:
            # If not an integer, treat as slug
            product = db.query(Product).filter(Product.slug == product_id_or_slug).first()
            
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Get the featured image URL if it exists
        featured_image_url = None
        if product.featured_image:
            featured_image_url = product.featured_image.url
        
        # Get all product images
        images = []
        for image in product.images:
            images.append({
                "id": image.id,
                "url": image.url,
                "alt_text": image.alt_text,
                "position": image.position
            })
            
        # Get category info if available
        category = None
        if product.category:
            category = {
                "id": product.category.id,
                "name": product.category.name,
                "slug": product.category.slug
            }
        
        # Create simplified product response
        return {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "stock": product.stock,
            "status": product.status,
            "slug": product.slug,
            "featured_image_url": featured_image_url,
            "images": images,
            "created_at": product.created_at.isoformat() if product.created_at else None,
            "updated_at": product.updated_at.isoformat() if product.updated_at else None,
            "published_at": product.published_at.isoformat() if product.published_at else None,
            "category": category,
            "specifications": product.specifications,
            "colors": product.colors,
            "dimensions": product.dimensions,
            "weight": product.weight,
            "materials": product.materials,
            "customization_options": product.customization_options,
            "meta_title": product.meta_title,
            "meta_description": product.meta_description,
            "views_count": product.views_count,
            "sales_count": product.sales_count,
            "rating": product.rating,
            "reviews_count": product.reviews_count,
            "is_featured": product.is_featured,
            "is_customizable": product.is_customizable,
            "low_stock_threshold": product.low_stock_threshold
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_product: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/", response_model=ProductResponse)
async def create_product(
    request: Request,
    product: ProductCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Create a new product (admin/manager only).
    """
    logger.debug(f"Create product request received: {product.dict()}")
    
    try:
        # Log request details
        request_body = await request.json()
        logger.debug(f"Request body: {request_body}")
    except Exception as e:
        logger.debug(f"Could not parse request body: {str(e)}")
    
    if current_user.role != UserRole.ADMIN:
        logger.warning(f"User {current_user.id} with role {current_user.role} tried to create a product without permission")
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Generate slug from name if not provided
    if not product.slug:
        base_slug = slugify(product.name)
        slug = base_slug
        counter = 1
        
        # Check for slug uniqueness
        while db.query(Product).filter(Product.slug == slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        logger.debug(f"Generated slug: {slug}")
    else:
        slug = product.slug
        logger.debug(f"Using provided slug: {slug}")
    
    try:
        # Get product data and exclude slug (we handle that separately)
        product_data = product.dict(exclude={'slug'})
        
        # If artist_id is not provided, we can handle it here:
        # 1. Either set it to current_user.id if appropriate
        # 2. Or just let it be None if the database allows it
        if product_data.get('artist_id') is None:
            logger.debug("artist_id not provided, setting to None")
            # If your database schema requires artist_id, you could set it here
            # product_data['artist_id'] = current_user.id
        
        logger.debug(f"Creating product with data: {product_data}")
        
        db_product = Product(
            **product_data,
            slug=slug
        )
        
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        
        logger.info(f"Product created successfully: ID={db_product.id}, Name={db_product.name}")
        return db_product
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating product: {str(e)}", exc_info=True)
        
        # Provide a more detailed error response
        error_message = str(e)
        if "artist_id" in error_message.lower():
            error_message = "Artist ID field error. This field is optional but if provided must reference a valid User ID."
        
        raise HTTPException(
            status_code=500, 
            detail={
                "message": f"Failed to create product: {error_message}",
                "suggestion": "Try using the /products/create-simple endpoint for a simpler way to create products"
            }
        )

@router.post("/{product_id}/images", response_model=ProductImageResponse)
async def upload_product_image(
    request: Request,
    product_id: int,
    file: UploadFile = File(...),
    is_featured: bool = False,
    alt_text: Optional[str] = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Upload a product image (admin only).
    """
    logger.debug(f"Image upload request received for product {product_id}")
    logger.debug(f"File info: name={file.filename}, content_type={file.content_type}, size={file.size if hasattr(file, 'size') else 'unknown'}")
    
    if current_user.role != UserRole.ADMIN:
        logger.warning(f"User {current_user.id} with role {current_user.role} tried to upload image without permission")
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        logger.warning(f"Product with ID {product_id} not found for image upload")
        raise HTTPException(status_code=404, detail="Product not found")
    
    try:
        # Upload file to storage (e.g., S3)
        folder_path = f"products/{product_id}/"
        logger.debug(f"Uploading file to folder: {folder_path}")
        
        # Ensure the correct storage path is used
        storage_dir = os.path.join(settings.LOCAL_STORAGE_PATH, "okyke-files", folder_path)
        os.makedirs(storage_dir, exist_ok=True)
        logger.debug(f"Ensuring storage directory exists: {storage_dir}")
        
        file_url = await upload_file(file, folder_path)
        logger.debug(f"File uploaded successfully, URL: {file_url}")
        
        # Log the expected physical file path
        expected_path = os.path.dirname(file_url.split("/local_s3/")[1])
        logger.debug(f"Expected physical file path: {os.path.join(settings.LOCAL_STORAGE_PATH, expected_path)}")
        
        # Create image record
        image = ProductImage(
            product_id=product_id,
            url=file_url,
            alt_text=alt_text,
            position=len(product.images)
        )
        
        db.add(image)
        
        if is_featured:
            logger.debug(f"Setting image as featured for product {product_id}")
            product.featured_image_id = image.id
        
        db.commit()
        db.refresh(image)
        
        logger.info(f"Image uploaded successfully for product {product_id}: image_id={image.id}, url={file_url}")
        return image
    except Exception as e:
        db.rollback()
        logger.error(f"Error uploading image for product {product_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Update a product (admin/manager only).
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # If status is being changed to published, set published_at
    if (product.status == ProductStatus.PUBLISHED and 
        db_product.status != ProductStatus.PUBLISHED):
        product.published_at = datetime.utcnow()
    
    # Validate featured_image_id if it's being updated
    update_data = product.dict(exclude_unset=True)
    if 'featured_image_id' in update_data:
        image_id = update_data['featured_image_id']
        if image_id is not None:
            # Check if the image exists and belongs to this product
            image = db.query(ProductImage).filter(
                ProductImage.id == image_id,
                ProductImage.product_id == product_id
            ).first()
            if not image:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid featured_image_id. Image must exist and belong to this product."
                )
    
    # Update fields
    for field, value in update_data.items():
        setattr(db_product, field, value)
    
    try:
        db.commit()
        db.refresh(db_product)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
    return db_product

@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Delete a product (admin only).
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(db_product)
    db.commit()
    
    return {"message": "Product deleted successfully"}

@router.post("/{product_id}/publish")
async def publish_product(
    product_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Publish a product (admin/manager only).
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db_product.status = ProductStatus.PUBLISHED
    db_product.published_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Product published successfully"}

@router.post("/{product_id}/archive")
async def archive_product(
    product_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Archive a product (admin/manager only).
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db_product.status = ProductStatus.ARCHIVED
    
    db.commit()
    
    return {"message": "Product archived successfully"}

@router.get("/{product_id_or_slug}/related", response_model=List[dict])
def get_related_products(
    product_id_or_slug: str,
    limit: int = 4,
    db: Session = Depends(deps.get_db),
):
    """
    Get products related to a specific product.
    """
    try:
        # First try to parse the input as an integer (id)
        try:
            product_id = int(product_id_or_slug)
            product = db.query(Product).filter(Product.id == product_id).first()
        except ValueError:
            # If not an integer, treat as slug
            product = db.query(Product).filter(Product.slug == product_id_or_slug).first()
            
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Get products from the same category, excluding the current product
        query = db.query(Product).filter(
            Product.category_id == product.category_id,
            Product.id != product.id,
            Product.status == ProductStatus.PUBLISHED
        )
        
        # Order by views or sales for better recommendations
        query = query.order_by(Product.views_count.desc(), Product.sales_count.desc())
        
        # Apply limit
        related_products = query.limit(limit).all()
        
        # If we don't have enough related products, get products from any category
        if len(related_products) < limit:
            additional_limit = limit - len(related_products)
            additional_products = db.query(Product).filter(
                Product.id != product.id,
                Product.id.notin_([p.id for p in related_products]),
                Product.status == ProductStatus.PUBLISHED
            ).order_by(
                Product.is_featured.desc(),
                Product.views_count.desc()
            ).limit(additional_limit).all()
            
            related_products.extend(additional_products)
        
        # Convert to simplified dict to avoid relationship issues
        result = []
        for prod in related_products:
            # Get the featured image URL if it exists
            featured_image_url = None
            if prod.featured_image:
                featured_image_url = prod.featured_image.url
            
            # Create a simplified product dict
            result.append({
                "id": prod.id,
                "name": prod.name,
                "description": prod.description,
                "price": prod.price,
                "stock": prod.stock,
                "status": prod.status,
                "slug": prod.slug,
                "featured_image_url": featured_image_url,
                "category_id": prod.category_id,
                "rating": prod.rating,
                "reviews_count": prod.reviews_count,
                "is_featured": prod.is_featured,
            })
        
        return result
    except Exception as e:
        logger.error(f"Error getting related products: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/create-simple", response_model=dict)
async def create_simple_product(
    product_data: dict,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Create a new product with simplified data (admin only).
    Used for scripts and testing.
    """
    logger.debug(f"Simple product creation request received: {product_data}")
    
    if current_user.role != UserRole.ADMIN:
        logger.warning(f"User {current_user.id} with role {current_user.role} tried to create a product without permission")
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    required_fields = ["name", "description", "price", "stock", "category_id"]
    for field in required_fields:
        if field not in product_data:
            raise HTTPException(status_code=422, detail=f"Missing required field: {field}")
    
    # Generate slug from name
    base_slug = slugify(product_data["name"])
    slug = base_slug
    counter = 1
    
    # Check for slug uniqueness
    while db.query(Product).filter(Product.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    try:
        # Create product with minimal data
        db_product = Product(
            name=product_data["name"],
            description=product_data["description"],
            price=float(product_data["price"]),
            stock=int(product_data["stock"]),
            category_id=int(product_data["category_id"]),
            status=product_data.get("status", ProductStatus.PUBLISHED),
            is_featured=product_data.get("is_featured", False),
            is_customizable=product_data.get("is_customizable", False),
            artist_id=product_data.get("artist_id"),  # This will be None if not provided
            slug=slug
        )
        
        # Add optional fields if provided
        if "specifications" in product_data:
            db_product.specifications = product_data["specifications"]
        if "colors" in product_data:
            db_product.colors = product_data["colors"]
        if "dimensions" in product_data:
            db_product.dimensions = product_data["dimensions"]
        if "weight" in product_data:
            db_product.weight = product_data["weight"]
        if "materials" in product_data:
            db_product.materials = product_data["materials"]
        
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        
        logger.info(f"Simple product created successfully: ID={db_product.id}, Name={db_product.name}")
        
        # Return a simplified response
        return {
            "id": db_product.id,
            "name": db_product.name,
            "slug": db_product.slug,
            "status": db_product.status,
            "created_at": db_product.created_at.isoformat() if db_product.created_at else None
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating simple product: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create product: {str(e)}") 