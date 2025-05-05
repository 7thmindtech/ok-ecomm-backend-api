from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.crud.crud_product import CRUDProduct
from app.models.models import Product, ProductStatus, ProductImage, Category, User, UserRole, UserType
from app.utils.slugify import slugify
import logging
import random
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_user(db):
    """Create a test user if none exists"""
    user = db.query(User).filter(User.email == "artist@example.com").first()
    if not user:
        test_user = User(
            email="artist@example.com",
            hashed_password="hashed_password_here",  # In real app, would be properly hashed
            full_name="Test Artist",
            user_type=UserType.ARTIST,
            role=UserRole.USER,
            is_active=True,
            is_verified=True,
            artist_bio="This is a test artist bio",
            artist_portfolio_url="https://example.com/portfolio",
            created_at=datetime.utcnow()
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        logger.info(f"Created test user: {test_user.full_name}")
        return test_user
    else:
        logger.info(f"Found existing user: {user.full_name}")
        return user

def create_test_products(db, artist_id, category_id, num_products=5):
    """Create test products if none exist"""
    existing_products = db.query(Product).count()
    
    if existing_products > 0:
        logger.info(f"Found {existing_products} existing products")
        products = db.query(Product).all()
        for product in products[:3]:  # Show first 3 products
            logger.info(f"Product: {product.id} - {product.name} - ${product.price}")
        return
    
    logger.info(f"Creating {num_products} test products")
    
    product_names = [
        "Handcrafted Wooden Bowl", 
        "Silver Pendant Necklace", 
        "Ceramic Plant Pot", 
        "Woven Wall Hanging",
        "Leather Journal", 
        "Macrame Plant Hanger", 
        "Stained Glass Suncatcher", 
        "Hand-Painted Silk Scarf", 
        "Carved Soapstone Figurine",
        "Beaded Bracelet Set"
    ]
    
    descriptions = [
        "Beautifully handcrafted by local artisans using traditional techniques.",
        "Each piece is unique and made with careful attention to detail.",
        "Perfect as a gift or to add an authentic touch to your home.",
        "Made with sustainably sourced materials and eco-friendly processes.",
        "This exclusive piece showcases traditional craftsmanship with a modern twist."
    ]
    
    for i in range(min(num_products, len(product_names))):
        name = product_names[i]
        price = round(random.uniform(20, 200), 2)
        stock = random.randint(5, 50)
        
        # Create product
        product = Product(
            name=name,
            description=random.choice(descriptions),
            price=price,
            stock=stock,
            artist_id=artist_id,
            category_id=category_id,
            status=ProductStatus.PUBLISHED,
            specifications={"material": "Mixed", "dimensions": "Various"},
            colors=["Natural", "Brown", "Black"],
            weight=random.uniform(0.2, 5.0),
            materials=["Wood", "Metal", "Ceramic"],
            meta_title=name,
            meta_description=f"Handcrafted {name} made by local artisans",
            slug=slugify(name),
            views_count=random.randint(10, 500),
            sales_count=random.randint(0, 50),
            rating=round(random.uniform(3.5, 5.0), 1),
            reviews_count=random.randint(0, 20),
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 90)),
            published_at=datetime.utcnow() - timedelta(days=random.randint(1, 60)),
            low_stock_threshold=5,
            is_featured=random.choice([True, False]),
            is_customizable=random.choice([True, False])
        )
        
        db.add(product)
        db.commit()
        db.refresh(product)
        
        # Create a sample image for the product
        image = ProductImage(
            product_id=product.id,
            url=f"https://picsum.photos/id/{random.randint(1, 1000)}/800/600",
            alt_text=f"{name} image",
            position=0
        )
        
        db.add(image)
        
        # Set the image as featured
        product.featured_image_id = image.id
        
        db.commit()
        
        logger.info(f"Created product: {product.name} (ID: {product.id}) - ${product.price}")
    
    logger.info(f"Successfully created {num_products} test products")

def test_products():
    """Test product functionality."""
    try:
        # Create engine and session
        engine = create_engine(settings.DATABASE_URL)
        logger.info(f"Connected to database: {settings.DATABASE_URL}")
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Create a test user
        test_user = create_test_user(db)
        
        # Get a category
        category = db.query(Category).first()
        if not category:
            logger.error("No categories found. Please run test_categories.py first.")
            return False
        
        # Create test products
        create_test_products(db, test_user.id, category.id)
        
        db.close()
        print("Product test successful!")
        return True
    except Exception as e:
        logger.error(f"Error in product test: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_products()
    if not success:
        print("Product test failed. Check the logs for details.") 