from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.api import deps
from app.models.models import Order, OrderItem, Product, User, Address
from app.schemas.order import OrderCreate, OrderResponse, OrderUpdate
from app.services.payment import create_payment_intent
from app.services.email import send_order_confirmation
from app.core.config import settings
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=List[OrderResponse])
async def get_orders(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Get all orders for the current user.
    """
    orders = db.query(Order).filter(Order.user_id == current_user.id).offset(skip).limit(limit).all()
    return orders

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Get a specific order.
    """
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.post("/", response_model=OrderResponse)
async def create_order(
    order: OrderCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Create a new order.
    
    Accepts all fields from the frontend to ensure we capture all data needed for order fulfillment,
    including subtotal, shipping_cost, and tax.
    """
    try:
        # Extract items from the order
        order_items = order.items
        
        # Create order without items
        order_data = order.dict(exclude={"items"})
        
        # Log order data for debugging
        print(f"Order data received: {order_data}")
        print(f"Order items received: {order_items}")
        
        # Ensure shipping_id is set
        if "shipping_id" not in order_data or order_data["shipping_id"] is None:
            # Default to shipping ID 1 if not provided
            order_data["shipping_id"] = 1
            print(f"Setting default shipping_id to 1")
        
        # Validate all required fields are present
        required_fields = ["shipping_address_id", "billing_address_id", "total_amount"]
        for field in required_fields:
            if field not in order_data or order_data[field] is None:
                print(f"Missing required field: {field}")
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Validate shipping and billing addresses exist
        shipping_address = db.query(Address).filter(Address.id == order_data["shipping_address_id"]).first()
        if not shipping_address:
            print(f"Shipping address with ID {order_data['shipping_address_id']} not found")
            raise HTTPException(status_code=404, detail=f"Shipping address with ID {order_data['shipping_address_id']} not found")
        
        billing_address = db.query(Address).filter(Address.id == order_data["billing_address_id"]).first()
        if not billing_address:
            print(f"Billing address with ID {order_data['billing_address_id']} not found")
            raise HTTPException(status_code=404, detail=f"Billing address with ID {order_data['billing_address_id']} not found")
        
        # Create order with all data from the request
        print(f"Creating order with data: {order_data}")
        current_time = datetime.now()
        db_order = Order(
            **order_data, 
            user_id=current_user.id,
            payment_status="pending",  # Set default payment status
            updated_at=current_time,   # Explicitly set updated_at
            created_at=current_time    # Ensure created_at is also set
        )
        db.add(db_order)
        db.flush()  # Generate the order ID without committing
        print(f"Created order with ID: {db_order.id}")
        
        # Create order items linked to the order
        for item_data in order_items:
            # Get product to get its price
            product_id = int(item_data.product_id) if isinstance(item_data.product_id, str) else item_data.product_id
            product = db.query(Product).filter(Product.id == product_id).first()
            if not product:
                print(f"Product with id {product_id} not found, rolling back transaction")
                db.rollback()
                raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found")
            
            # Create the order item
            print(f"Creating order item for product {product_id}")
            order_item = OrderItem(
                order_id=db_order.id,
                product_id=product_id,
                quantity=item_data.quantity,
                unit_price=product.price,
                customization=item_data.customizations,
                updated_at=current_time  # Explicitly set updated_at for order item
            )
            db.add(order_item)
        
        # Commit all changes
        print("Committing transaction...")
        db.commit()
        db.refresh(db_order)
        print(f"Order {db_order.id} created successfully")
        return db_order
    except Exception as e:
        print(f"Error creating order: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create order: {str(e)}")

@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int,
    order: OrderUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Update an order.
    """
    db_order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    for key, value in order.dict(exclude_unset=True).items():
        setattr(db_order, key, value)
    
    db.commit()
    db.refresh(db_order)
    return db_order

@router.delete("/{order_id}")
async def delete_order(
    order_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Delete an order.
    """
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    db.delete(order)
    db.commit()
    return {"message": "Order deleted successfully"}

@router.post("/{order_id}/cancel")
def cancel_order(
    order_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Cancel an order.
    """
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.status not in ["pending", "processing"]:
        raise HTTPException(
            status_code=400,
            detail="Order cannot be cancelled in its current status"
        )
    
    order.status = "cancelled"
    db.commit()
    return {"message": "Order cancelled successfully"} 