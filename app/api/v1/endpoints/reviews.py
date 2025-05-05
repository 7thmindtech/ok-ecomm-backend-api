from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.models.models import User, Review, Product
from app.schemas.review import ReviewCreate, ReviewResponse

router = APIRouter()

@router.get("/{product_slug}/reviews", response_model=List[ReviewResponse])
async def get_product_reviews(
    product_slug: str = Path(..., description="The product slug to get reviews for"),
    skip: int = Query(0, description="Number of reviews to skip"),
    limit: int = Query(20, description="Number of reviews to return"),
    db: Session = Depends(deps.get_db),
    current_user: Optional[User] = Depends(deps.get_current_user_optional),
):
    """
    Get reviews for a specific product by slug
    """
    # First get the product
    product = db.query(Product).filter(Product.slug == product_slug).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Then get the reviews
    reviews = db.query(Review).filter(Review.product_id == product.id).order_by(Review.created_at.desc()).offset(skip).limit(limit).all()
    
    return reviews

@router.post("/{product_slug}/reviews", response_model=ReviewResponse)
async def create_product_review(
    review_in: ReviewCreate,
    product_slug: str = Path(..., description="The product slug to create a review for"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Create a new review for a product
    """
    # First get the product
    product = db.query(Product).filter(Product.slug == product_slug).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if user already reviewed this product
    existing_review = db.query(Review).filter(
        Review.user_id == current_user.id,
        Review.product_id == product.id
    ).first()
    
    if existing_review:
        raise HTTPException(status_code=400, detail="You have already reviewed this product")
    
    # Create the review
    db_review = Review(
        user_id=current_user.id,
        product_id=product.id,
        rating=review_in.rating,
        comment=review_in.comment,
        reviewer_name=current_user.full_name
    )
    
    db.add(db_review)
    
    # Update product rating and reviews count
    product_reviews = db.query(Review).filter(Review.product_id == product.id).all()
    total_rating = sum(review.rating for review in product_reviews) + review_in.rating
    total_reviews = len(product_reviews) + 1
    
    product.rating = round(total_rating / total_reviews, 1)
    product.reviews_count = total_reviews
    
    db.add(product)
    db.commit()
    db.refresh(db_review)
    
    return db_review 