from typing import Optional
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
from app.core.config import settings
from app.models.models import Order, User
from app.schemas.order import OrderResponse
from pathlib import Path

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)

async def send_order_confirmation(
    order: OrderResponse,
    user: User,
    background_tasks: Optional[list] = None
):
    """
    Send order confirmation email.
    """
    message = MessageSchema(
        subject="Order Confirmation",
        recipients=[user.email],
        body=f"""
        Dear {user.name},

        Thank you for your order! Here are your order details:

        Order ID: {order.id}
        Total Amount: ${order.total_amount:.2f}
        Status: {order.status}

        Order Items:
        {_format_order_items(order.items)}

        Shipping Address:
        {_format_address(order.shipping_address)}

        If you have any questions, please don't hesitate to contact us.

        Best regards,
        Your Store Team
        """,
        subtype="plain"
    )

    fm = FastMail(conf)
    if background_tasks:
        background_tasks.append(fm.send_message(message))
    else:
        await fm.send_message(message)

async def send_password_reset_email(
    email: EmailStr,
    reset_token: str,
    background_tasks: Optional[list] = None
):
    """
    Send password reset email.
    """
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
    
    message = MessageSchema(
        subject="Password Reset Request",
        recipients=[email],
        body=f"""
        You have requested to reset your password. Click the link below to proceed:

        {reset_url}

        If you didn't request this, please ignore this email.

        Best regards,
        Your Store Team
        """,
        subtype="plain"
    )

    fm = FastMail(conf)
    if background_tasks:
        background_tasks.append(fm.send_message(message))
    else:
        await fm.send_message(message)

async def send_welcome_email(
    email: EmailStr,
    name: str,
    background_tasks: Optional[list] = None
):
    """
    Send welcome email to new users.
    """
    message = MessageSchema(
        subject="Welcome to Our Store!",
        recipients=[email],
        body=f"""
        Dear {name},

        Welcome to our store! We're excited to have you as a customer.

        Here are some things you can do:
        - Browse our products
        - Create a wishlist
        - Save your shipping addresses
        - Track your orders

        If you have any questions, please don't hesitate to contact us.

        Best regards,
        Your Store Team
        """,
        subtype="plain"
    )

    fm = FastMail(conf)
    if background_tasks:
        background_tasks.append(fm.send_message(message))
    else:
        await fm.send_message(message)

def _format_order_items(items):
    """
    Format order items for email.
    """
    return "\n".join([
        f"- {item.product.name} x {item.quantity} - ${item.price * item.quantity:.2f}"
        for item in items
    ])

def _format_address(address):
    """
    Format address for email.
    """
    return f"""
    {address.street}
    {address.city}, {address.state} {address.postal_code}
    {address.country}
    """ 