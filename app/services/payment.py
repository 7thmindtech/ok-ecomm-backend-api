import stripe
from app.core.config import settings
from typing import Dict, Any

stripe.api_key = settings.STRIPE_SECRET_KEY

async def create_payment_intent(
    amount: float,
    currency: str = "usd",
    metadata: Dict[str, Any] = None
) -> stripe.PaymentIntent:
    """
    Create a Stripe payment intent.
    """
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Convert to cents
            currency=currency,
            metadata=metadata,
            automatic_payment_methods={
                "enabled": True,
            },
        )
        return payment_intent
    except stripe.error.StripeError as e:
        raise Exception(f"Failed to create payment intent: {str(e)}")

async def confirm_payment_intent(
    payment_intent_id: str,
    payment_method_id: str
) -> stripe.PaymentIntent:
    """
    Confirm a Stripe payment intent.
    """
    try:
        payment_intent = stripe.PaymentIntent.confirm(
            payment_intent_id,
            payment_method=payment_method_id,
        )
        return payment_intent
    except stripe.error.StripeError as e:
        raise Exception(f"Failed to confirm payment: {str(e)}")

async def refund_payment(
    payment_intent_id: str,
    amount: float = None
) -> stripe.Refund:
    """
    Refund a payment.
    """
    try:
        refund_params = {
            "payment_intent": payment_intent_id,
        }
        if amount:
            refund_params["amount"] = int(amount * 100)  # Convert to cents
            
        refund = stripe.Refund.create(**refund_params)
        return refund
    except stripe.error.StripeError as e:
        raise Exception(f"Failed to process refund: {str(e)}")

async def get_payment_intent(
    payment_intent_id: str
) -> stripe.PaymentIntent:
    """
    Get a payment intent by ID.
    """
    try:
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        return payment_intent
    except stripe.error.StripeError as e:
        raise Exception(f"Failed to get payment intent: {str(e)}")

async def create_payment_method(
    card_details: Dict[str, Any]
) -> stripe.PaymentMethod:
    """
    Create a payment method from card details.
    """
    try:
        payment_method = stripe.PaymentMethod.create(
            type="card",
            card={
                "number": card_details["number"],
                "exp_month": card_details["exp_month"],
                "exp_year": card_details["exp_year"],
                "cvc": card_details["cvc"],
                "billing_details": card_details.get("billing_details", {}),
            },
        )
        return payment_method
    except stripe.error.StripeError as e:
        raise Exception(f"Failed to create payment method: {str(e)}") 