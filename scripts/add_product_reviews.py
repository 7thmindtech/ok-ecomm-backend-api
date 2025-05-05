#!/usr/bin/env python3
import os
import sys
import logging
import random
from datetime import datetime, timedelta

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from app.db.session import SessionLocal
from app.models.models import Product, Review, User
from sqlalchemy.orm import Session

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Sample review texts
REVIEW_TEXTS = [
    "Absolutely love this product! It exceeded all my expectations. Would definitely recommend to friends and family.",
    "Great quality and excellent craftsmanship. This is exactly what I was looking for.",
    "Very happy with my purchase. Fast shipping and the item looks even better in person!",
    "Good product but the color is slightly different from what was shown in the picture.",
    "Decent quality for the price. Not luxury but definitely worth what I paid.",
    "Solid product. Does exactly what it's supposed to do.",
    "Amazing product! I've already ordered two more for gifts.",
    "The customization options really make this special. Everyone asks where I got it!",
    "Love the materials used. Very eco-friendly and sustainable.",
    "Awesome design and great attention to detail. Very pleased with my purchase.",
    "The quality could be better, but it serves its purpose well.",
    "Great value for money. Highly recommended!",
    "This is my second purchase and I'm still impressed with the quality.",
    "Perfect size and the design is beautiful. Very happy customer!",
    "The customization was perfect - exactly what I asked for!"
]

# Sample reviewer names
REVIEWER_NAMES = [
    "John D.",
    "Sarah M.",
    "Robert T.",
    "Emily K.",
    "Michael P.",
    "Jessica H.",
    "David W.",
    "Olivia R.",
    "William S.",
    "Sophia L.",
    "Daniel N.",
    "Emma C.",
    "Matthew B.",
    "Ava G.",
    "James F."
]

def main():
    """
    Add sample reviews and update ratings for products
    """
    logger.info("Starting product review generation")
    
    # Create database session
    db = SessionLocal()
    try:
        # Get all products and users
        products = db.query(Product).all()
        users = db.query(User).all()
        
        if not users:
            logger.error("No users found in the database. Cannot create reviews.")
            return
            
        logger.info(f"Found {len(products)} products and {len(users)} users in the database")
        
        reviews_added = 0
        now = datetime.utcnow()
        
        # Process each product
        for product in products:
            # Determine number of reviews for this product (3-8)
            num_reviews = random.randint(3, 8)
            logger.info(f"Adding {num_reviews} reviews to product '{product.name}'")
            
            product_reviews = []
            
            for i in range(num_reviews):
                # Select random user
                user = random.choice(users)
                
                # Generate random rating (3-5 with more weight toward 4-5)
                rating_weights = [0.1, 0.2, 0.7]  # 10% 3-star, 20% 4-star, 70% 5-star
                rating = random.choices([3, 4, 5], weights=rating_weights)[0]
                
                # Select random review text based on rating
                if rating == 5:
                    # Choose from more positive reviews
                    review_text = random.choice(REVIEW_TEXTS[:4] + REVIEW_TEXTS[6:10] + [REVIEW_TEXTS[14]])
                elif rating == 4:
                    # Choose from neutral to positive reviews
                    review_text = random.choice(REVIEW_TEXTS[4:8] + [REVIEW_TEXTS[9], REVIEW_TEXTS[11], REVIEW_TEXTS[13]])
                else:
                    # Choose from more neutral reviews
                    review_text = random.choice(REVIEW_TEXTS[3:6] + [REVIEW_TEXTS[10]])
                
                # Create random date within last 3 months
                days_ago = random.randint(1, 90)
                review_date = now - timedelta(days=days_ago)
                
                # Get user's name from full_name property or use a random name
                reviewer_name = user.full_name
                if not reviewer_name:
                    reviewer_name = random.choice(REVIEWER_NAMES)
                
                # Create review
                review = Review(
                    product_id=product.id,
                    user_id=user.id,
                    rating=rating,
                    comment=review_text,
                    reviewer_name=reviewer_name,
                    created_at=review_date,
                    updated_at=review_date
                )
                
                db.add(review)
                product_reviews.append(review)
                reviews_added += 1
            
            # Update product rating and reviews count
            average_rating = sum(r.rating for r in product_reviews) / len(product_reviews)
            product.rating = round(average_rating, 1)
            product.reviews_count = len(product_reviews)
            db.add(product)
            
            logger.info(f"Updated product '{product.name}' with rating {product.rating} from {product.reviews_count} reviews")
            
        db.commit()
        logger.info(f"Update complete. Added {reviews_added} reviews to {len(products)} products.")
        
    except Exception as e:
        logger.error(f"Error during update: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main() 