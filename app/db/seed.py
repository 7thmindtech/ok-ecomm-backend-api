import logging
import json
from app.core.database import get_db
from app.models.models import Product, ProductImage, Category, ProductStatus, User, UserRole
from sqlalchemy.exc import SQLAlchemyError
from app.core.security import get_password_hash

logger = logging.getLogger(__name__)

# Mock data from frontend/src/app/api/products/[slug]/route.ts
mock_products = [
  {
    "id": '1',
    "slug": 'classic-white-tshirt',
    "name": 'Classic White T-Shirt',
    "description": 'Premium cotton t-shirt perfect for customization. Made with high-quality materials that ensure comfort and durability. This shirt is perfect for everyday wear, casual outings, or as a canvas for your creative designs.',
    "price": 29.99,
    "stock": 100,
    "category_id": 2,
    "artist_id": '1',
    "status": ProductStatus.PUBLISHED,
    "specifications": {
      'Material': '100% Cotton',
      'Fit': 'Regular',
      'Care': 'Machine wash cold, tumble dry low',
      'Country of Origin': 'Made in USA',
      'styles': ['Classic', 'Modern', 'Slim'],
      'patterns': ['Solid', 'Striped']
    },
    "colors": [
      { "name": 'White', "value": '#ffffff' },
      { "name": 'Black', "value": '#000000' },
      { "name": 'Gray', "value": '#808080' }
    ],
    "sizes": ['S', 'M', 'L', 'XL', 'XXL'],
    "materials": ['Cotton', 'Organic Cotton', 'Cotton Blend'],
    "dimensions": {
      'S': {"width": 18, "height": 28},
      'M': {"width": 20, "height": 29},
      'L': {"width": 22, "height": 30},
      'XL': {"width": 24, "height": 31}
    },
    "weight": 0.3,
    "is_featured": True,
    "is_customizable": True,
    "low_stock_threshold": 10,
    "featured_image_url": '/local_s3/okyke-files/products/1/671c30a9-f65e-46cf-994d-937292ac7173.jpg',
    "images": [
      { "id": 1, "url": '/local_s3/okyke-files/products/1/671c30a9-f65e-46cf-994d-937292ac7173.jpg', "alt_text": 'Front view', "position": 1, "is_primary": True },
      { "id": 2, "url": '/local_s3/okyke-files/products/1/671c30a9-f65e-46cf-994d-937292ac7173.jpg', "alt_text": 'Back view', "position": 2 },
      { "id": 3, "url": '/local_s3/okyke-files/products/1/671c30a9-f65e-46cf-994d-937292ac7173.jpg', "alt_text": 'Side view', "position": 3 }
    ],
    "views_count": 1240,
    "sales_count": 89,
    "rating": 4.8,
    "reviews_count": 128,
    "stock_status": 'in_stock',
  },
  {
    "id": '2',
    "slug": 'black-hoodie',
    "name": 'Black Hoodie',
    "description": 'Comfortable cotton blend hoodie that keeps you warm and stylish. Features a spacious hood, kangaroo pocket, and ribbed cuffs and hem for a snug fit. Perfect for cooler weather and casual outings.',
    "price": 49.99,
    "stock": 75,
    "category_id": 3,
    "artist_id": '2',
    "status": ProductStatus.PUBLISHED,
    "specifications": {
      'Material': '80% Cotton, 20% Polyester',
      'Fit': 'Regular',
      'Care': 'Machine wash cold, tumble dry low',
      'Country of Origin': 'Made in Canada'
    },
    "colors": [
      { "name": 'Black', "value": '#000000' },
      { "name": 'Navy', "value": '#000080' },
      { "name": 'Charcoal', "value": '#36454F' }
    ],
    "sizes": ['S', 'M', 'L', 'XL'],
    "is_featured": True,
    "is_customizable": True,
    "low_stock_threshold": 10,
    "weight": 0.6,
    "featured_image_url": '/local_s3/okyke-files/products/2/7386f504-b25a-4e12-90a4-6af2be37d094.jpg',
    "images": [
      { "id": 4, "url": '/local_s3/okyke-files/products/2/7386f504-b25a-4e12-90a4-6af2be37d094.jpg', "alt_text": 'Front view', "position": 1, "is_primary": True },
      { "id": 5, "url": '/local_s3/okyke-files/products/2/7386f504-b25a-4e12-90a4-6af2be37d094.jpg', "alt_text": 'Back view', "position": 2 }
    ],
    "views_count": 980,
    "sales_count": 67,
    "rating": 4.9,
    "reviews_count": 95,
    "stock_status": 'in_stock',
  },
  {
    "id": '3',
    "slug": 'custom-mug',
    "name": 'Custom Mug',
    "description": 'Personalized ceramic mug perfect for your morning coffee or tea. Made with high-quality ceramic material that retains heat well. Add your own design or message to make it truly special.',
    "price": 19.99,
    "stock": 150,
    "category_id": 4,
    "artist_id": '3',
    "status": ProductStatus.PUBLISHED,
    "specifications": {
      'Material': 'Ceramic',
      'Capacity': '11 oz',
      'Dishwasher Safe': 'Yes',
      'Microwave Safe': 'Yes'
    },
    "colors": [
      { "name": 'White', "value": '#ffffff' },
      { "name": 'Black', "value": '#000000' },
      { "name": 'Blue', "value": '#0000ff' },
      { "name": 'Red', "value": '#ff0000' }
    ],
    "dimensions": {
      'height': 3.8,
      'diameter': 3.2
    },
    "weight": 0.4,
    "is_featured": True,
    "is_customizable": True,
    "low_stock_threshold": 20,
    "featured_image_url": '/local_s3/okyke-files/products/3/07f6f373-e764-41f9-a7f4-9fe24d38d9b2.jpg',
    "images": [
      { "id": 6, "url": '/local_s3/okyke-files/products/3/07f6f373-e764-41f9-a7f4-9fe24d38d9b2.jpg', "alt_text": 'Front view', "position": 1, "is_primary": True },
      { "id": 7, "url": '/local_s3/okyke-files/products/3/07f6f373-e764-41f9-a7f4-9fe24d38d9b2.jpg', "alt_text": 'Side view', "position": 2 }
    ],
    "views_count": 1420,
    "sales_count": 213,
    "rating": 4.7,
    "reviews_count": 234,
    "stock_status": 'in_stock',
  },
  {
    "id": '4',
    "slug": 'basic-water-bottle',
    "name": 'Basic Water Bottle',
    "description": 'Simple, durable water bottle for everyday use. Keeps your drinks at the right temperature. Made with BPA-free materials that are safe for daily use.',
    "price": 14.99,
    "stock": 200,
    "category_id": 4,
    "artist_id": '3',
    "status": ProductStatus.PUBLISHED,
    # No specifications, colors, sizes or materials - this is a simple product with no variants
    "weight": 0.3,
    "is_featured": False,
    "is_customizable": False,
    "low_stock_threshold": 20,
    "featured_image_url": '/local_s3/okyke-files/products/3/07f6f373-e764-41f9-a7f4-9fe24d38d9b2.jpg',
    "images": [
      { "id": 14, "url": '/local_s3/okyke-files/products/3/07f6f373-e764-41f9-a7f4-9fe24d38d9b2.jpg', "alt_text": 'Front view', "position": 1, "is_primary": True },
    ],
    "views_count": 520,
    "sales_count": 85,
    "rating": 4.3,
    "reviews_count": 42,
    "stock_status": 'in_stock',
  },
  {
    "id": '5',
    "slug": 'plain-notebook',
    "name": 'Plain Notebook',
    "description": 'Simple lined notebook for notes, journaling or sketching. Features quality paper that prevents bleeding and is perfect for daily use.',
    "price": 7.99,
    "stock": 350,
    "category_id": 5,
    "artist_id": '1',
    "status": ProductStatus.PUBLISHED,
    "specifications": None,  # Explicitly set to null to test that case
    "is_featured": False,
    "is_customizable": False,
    "low_stock_threshold": 50,
    "weight": 0.2,
    "featured_image_url": '/local_s3/okyke-files/products/5/69754ff1-b35c-492b-bfd9-99dbbbb74bff.jpg',
    "images": [
      { "id": 15, "url": '/local_s3/okyke-files/products/5/69754ff1-b35c-492b-bfd9-99dbbbb74bff.jpg', "alt_text": 'Front view', "position": 1, "is_primary": True },
    ],
    "views_count": 310,
    "sales_count": 127,
    "rating": 4.5,
    "reviews_count": 78,
    "stock_status": 'in_stock',
  },
  {
    "id": '6',
    "slug": 'canvas-tote-bag',
    "name": 'Canvas Tote Bag',
    "description": 'Spacious and eco-friendly canvas tote bag. Perfect for shopping, beach trips, or everyday use. Durable material with reinforced handles.',
    "price": 29.99,
    "stock": 80,
    "category_id": 6,
    "artist_id": '3',
    "status": ProductStatus.PUBLISHED,
    "specifications": {
      'Material': '100% Cotton Canvas',
      'Dimensions': '15" x 16" x 4"',
      'Capacity': 'Approx. 20 liters',
      'Care': 'Machine washable'
    },
    "colors": [
      { "name": 'Natural', "value": '#f5f5dc' },
      { "name": 'Black', "value": '#000000' },
      { "name": 'Navy', "value": '#000080' }
    ],
    "materials": ['Cotton Canvas', 'Recycled Canvas'],
    "weight": 0.35,
    "is_featured": True,
    "is_customizable": True,
    "low_stock_threshold": 10,
    "featured_image_url": '/local_s3/okyke-files/products/6/8f621dc6-ef1c-4d60-aece-00a35afdd9f6.jpg',
    "images": [
      { "id": 12, "url": '/local_s3/okyke-files/products/6/8f621dc6-ef1c-4d60-aece-00a35afdd9f6.jpg', "alt_text": 'Front view', "position": 1, "is_primary": True },
      { "id": 13, "url": '/local_s3/okyke-files/products/6/8f621dc6-ef1c-4d60-aece-00a35afdd9f6.jpg', "alt_text": 'Side view', "position": 2 }
    ],
    "views_count": 950,
    "sales_count": 68,
    "rating": 4.2,
    "reviews_count": 47,
    "stock_status": 'in_stock',
  },
  {
    "id": '7',
    "slug": 'simple-ceramic-vase',
    "name": 'Simple Ceramic Vase',
    "description": 'Elegant minimalist ceramic vase that complements any home decor style. Hand-crafted by talented artisans with premium quality clay and finished with a smooth glaze. Perfect for displaying flowers or as a standalone decorative piece.',
    "price": 24.99,
    "original_price": 34.99,
    "stock": 12,
    "category_id": 5,
    "status": ProductStatus.PUBLISHED,
    "is_featured": False,
    "is_customizable": False,
    "is_sale": True,
    "is_new": False,
    "low_stock_threshold": 5,
    "featured_image_url": '/local_s3/okyke-files/products/3/ceramic-vase-main.jpg',
    "images": [
      { "id": 16, "url": '/local_s3/okyke-files/products/3/ceramic-vase-main.jpg', "alt_text": 'Ceramic vase', "position": 1, "is_primary": True },
      { "id": 17, "url": '/local_s3/okyke-files/products/3/ceramic-vase-detail.jpg', "alt_text": 'Vase detail', "position": 2 }
    ],
    "views_count": 420,
    "sales_count": 31,
    "rating": 4.6,
    "reviews_count": 18,
    "stock_status": 'low_stock',
    "stock_quantity": 12,
  }
]

# Mock categories
mock_categories = [
    {"id": 1, "name": "All Products", "description": "All available products", "slug": "all-products"},
    {"id": 2, "name": "T-Shirts", "description": "Comfortable cotton t-shirts", "slug": "t-shirts"},
    {"id": 3, "name": "Hoodies", "description": "Warm and cozy hoodies", "slug": "hoodies"},
    {"id": 4, "name": "Accessories", "description": "Various accessories", "slug": "accessories"},
    {"id": 5, "name": "Home Decor", "description": "Stylish home decoration items", "slug": "home-decor"},
    {"id": 6, "name": "Bags", "description": "Practical and stylish bags", "slug": "bags"}
]

# Mock admin user for product creation
admin_user = {
    "email": "admin@example.com",
    "password": "admin123",
    "full_name": "Admin User",
    "role": UserRole.ADMIN
}

def seed_db():
    """
    Populate the database with initial data
    """
    try:
        db = next(get_db())
        
        # Create admin user if it doesn't exist
        create_admin_user(db)
        
        # Create categories
        create_categories(db)
        
        # Create products and their images
        create_products(db)
        
        db.commit()
        logger.info("Database seeded successfully!")
        return True
        
    except SQLAlchemyError as e:
        logger.error(f"Error seeding database: {str(e)}")
        db.rollback()
        raise

def create_admin_user(db):
    """Create admin user if it doesn't exist"""
    user = db.query(User).filter(User.email == admin_user["email"]).first()
    if not user:
        # Split full_name into first_name and last_name
        name_parts = admin_user["full_name"].split(" ", 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        
        user = User(
            email=admin_user["email"],
            hashed_password=get_password_hash(admin_user["password"]),
            first_name=first_name,
            last_name=last_name,
            role=admin_user["role"]
        )
        db.add(user)
        db.flush()
        logger.info(f"Created admin user: {user.email}")
    return user

def create_categories(db):
    """Create categories if they don't exist"""
    for category_data in mock_categories:
        category = db.query(Category).filter(Category.id == category_data["id"]).first()
        if not category:
            category = Category(
                id=category_data["id"],
                name=category_data["name"],
                description=category_data["description"],
                slug=category_data["slug"]
            )
            db.add(category)
            db.flush()
            logger.info(f"Created category: {category.name}")

def create_products(db):
    """Create products and their images"""
    for product_data in mock_products:
        # Check if product exists
        product = db.query(Product).filter(Product.slug == product_data["slug"]).first()
        
        if not product:
            # Prepare product data
            product_dict = {
                "name": product_data["name"],
                "slug": product_data["slug"],
                "description": product_data["description"],
                "price": product_data["price"],
                "stock": product_data["stock"],
                "category_id": product_data["category_id"],
                "status": product_data["status"],
                "weight": product_data.get("weight"),
                "is_featured": product_data.get("is_featured", False),
                "is_customizable": product_data.get("is_customizable", False),
                "low_stock_threshold": product_data.get("low_stock_threshold", 10),
                "views_count": product_data.get("views_count", 0),
                "sales_count": product_data.get("sales_count", 0),
                "rating": product_data.get("rating", 0),
                "reviews_count": product_data.get("reviews_count", 0),
            }
            
            # Handle JSON fields separately
            # Add specifications with sizes included if they exist
            specs = product_data.get("specifications", {})
            if specs is not None and product_data.get("sizes"):
                if isinstance(specs, dict):
                    specs["sizes"] = product_data.get("sizes")
                else:
                    specs = {"sizes": product_data.get("sizes")}
                    
            product_dict["specifications"] = specs
            product_dict["colors"] = product_data.get("colors")
            product_dict["dimensions"] = product_data.get("dimensions")
            product_dict["materials"] = product_data.get("materials")
            
            # Create product
            product = Product(**product_dict)
            db.add(product)
            db.flush()
            
            # Create product images
            create_product_images(db, product, product_data)
            
            logger.info(f"Created product: {product.name}")

def create_product_images(db, product, product_data):
    """Create images for a product"""
    featured_image = None
    
    for image_data in product_data.get("images", []):
        image = ProductImage(
            product_id=product.id,
            url=image_data["url"],
            alt_text=image_data.get("alt_text", ""),
            position=image_data.get("position", 0)
        )
        db.add(image)
        db.flush()
        
        # Set as featured image if it's the primary image or the first one
        if image_data.get("is_primary", False) or not featured_image:
            featured_image = image
    
    # Set the featured image
    if featured_image:
        product.featured_image_id = featured_image.id
        db.flush()

if __name__ == "__main__":
    seed_db() 