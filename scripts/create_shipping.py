from app.db.session import SessionLocal
from app.models.models import Shipping

def create_shipping_methods():
    db = SessionLocal()
    try:
        # Check if shipping method already exists
        existing = db.query(Shipping).filter(Shipping.id == 1).first()
        
        if not existing:
            # Create a standard shipping method
            standard_shipping = Shipping(
                id=1,
                name='Standard Shipping',
                description='3-5 business days delivery',
                price=5.99,
                estimated_days=5,
                is_active=True
            )
            db.add(standard_shipping)
            
            # Create an express shipping method
            express_shipping = Shipping(
                id=2, 
                name='Express Shipping',
                description='1-2 business days delivery',
                price=14.99,
                estimated_days=2,
                is_active=True
            )
            db.add(express_shipping)
            
            db.commit()
            print('Shipping methods created successfully')
        else:
            print('Shipping methods already exist')
            
    except Exception as e:
        print(f'Error creating shipping methods: {e}')
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_shipping_methods() 