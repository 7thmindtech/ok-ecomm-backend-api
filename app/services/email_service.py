from typing import List, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

def send_email(
    email_to: str,
    subject: str,
    html_content: str,
    from_email: Optional[str] = None,
) -> None:
    if not from_email:
        from_email = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM_ADDRESS}>"
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = email_to
    
    html_part = MIMEText(html_content, "html")
    msg.attach(html_part)
    
    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        # Log the error but don't raise it to prevent the application from crashing
        print(f"Failed to send email: {str(e)}")
        # In production, you might want to use a proper logging system
        # logger.error(f"Failed to send email: {str(e)}")

def send_password_reset_email(email_to: str, token: str) -> None:
    reset_url = f"{settings.FRONTEND_URL}/reset-password/{token}"
    send_email(
        email_to=email_to,
        subject="Reset your password",
        html_content=f"""
            <p>Hi,</p>
            <p>You have requested to reset your password. Click the link below to proceed:</p>
            <p><a href="{reset_url}">Reset Password</a></p>
            <p>This link will expire in 1 hour.</p>
            <p>If you didn't request this, please ignore this email.</p>
            <p>Best regards,<br>Okyke Team</p>
        """,
    )

def send_order_confirmation_email(email_to: str, order_id: str, order_total: float) -> None:
    order_url = f"{settings.FRONTEND_URL}/orders/{order_id}"
    send_email(
        email_to=email_to,
        subject="Order Confirmation",
        html_content=f"""
            <p>Hi,</p>
            <p>Thank you for your order! Your order has been confirmed.</p>
            <p>Order ID: {order_id}</p>
            <p>Total Amount: ${order_total:.2f}</p>
            <p>You can view your order details here: <a href="{order_url}">View Order</a></p>
            <p>We'll send you another email when your order ships.</p>
            <p>Best regards,<br>Okyke Team</p>
        """,
    )

def send_order_shipped_email(email_to: str, order_id: str, tracking_number: str) -> None:
    order_url = f"{settings.FRONTEND_URL}/orders/{order_id}"
    send_email(
        email_to=email_to,
        subject="Your Order Has Shipped!",
        html_content=f"""
            <p>Hi,</p>
            <p>Great news! Your order has been shipped.</p>
            <p>Order ID: {order_id}</p>
            <p>Tracking Number: {tracking_number}</p>
            <p>You can track your order here: <a href="{order_url}">Track Order</a></p>
            <p>Best regards,<br>Okyke Team</p>
        """,
    ) 