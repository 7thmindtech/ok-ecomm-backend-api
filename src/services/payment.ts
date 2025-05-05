import Stripe from 'stripe';
import { Order } from '../models/Order';
import { Address } from '../models/Address';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2023-10-16',
});

export const createPaymentIntent = async (order: Order, shippingAddress: Address, billingAddress: Address) => {
  try {
    // Create payment intent
    const paymentIntent = await stripe.paymentIntents.create({
      amount: Math.round(order.total_amount * 100), // Convert to cents
      currency: 'usd',
      metadata: {
        order_id: order.id,
        user_id: order.user_id,
      },
    });

    // Create shipping address in Stripe
    const shippingAddressId = await stripe.customers.create({
      email: order.user.email,
      name: shippingAddress.full_name,
      address: {
        line1: shippingAddress.address_line1,
        line2: shippingAddress.address_line2,
        city: shippingAddress.city,
        state: shippingAddress.state,
        postal_code: shippingAddress.postal_code,
        country: shippingAddress.country,
      },
      phone: shippingAddress.phone_number,
    });

    // Create billing address in Stripe
    const billingAddressId = await stripe.customers.create({
      email: order.user.email,
      name: billingAddress.full_name,
      address: {
        line1: billingAddress.address_line1,
        line2: billingAddress.address_line2,
        city: billingAddress.city,
        state: billingAddress.state,
        postal_code: billingAddress.postal_code,
        country: billingAddress.country,
      },
      phone: billingAddress.phone_number,
    });

    return {
      clientSecret: paymentIntent.client_secret,
      shippingAddressId: shippingAddressId.id,
      billingAddressId: billingAddressId.id,
    };
  } catch (error) {
    console.error('Error creating payment intent:', error);
    throw new Error('Error creating payment intent.');
  }
};

export const handleWebhook = async (event: Stripe.Event) => {
  try {
    switch (event.type) {
      case 'payment_intent.succeeded':
        const paymentIntent = event.data.object as Stripe.PaymentIntent;
        const orderId = paymentIntent.metadata.order_id;

        // Update order status
        await Order.update(
          { status: 'processing' },
          { where: { id: orderId } }
        );
        break;

      case 'payment_intent.payment_failed':
        const failedPaymentIntent = event.data.object as Stripe.PaymentIntent;
        const failedOrderId = failedPaymentIntent.metadata.order_id;

        // Update order status
        await Order.update(
          { status: 'cancelled' },
          { where: { id: failedOrderId } }
        );
        break;

      default:
        console.log(`Unhandled event type ${event.type}`);
    }
  } catch (error) {
    console.error('Error handling webhook:', error);
    throw new Error('Error handling webhook.');
  }
};

export const createRefund = async (order: Order) => {
  try {
    const refund = await stripe.refunds.create({
      payment_intent: order.payment_intent_id,
      reason: 'requested_by_customer',
    });

    // Update order status
    await Order.update(
      { status: 'refunded' },
      { where: { id: order.id } }
    );

    return refund;
  } catch (error) {
    console.error('Error creating refund:', error);
    throw new Error('Error creating refund.');
  }
}; 