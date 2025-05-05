import { Request, Response } from 'express';
import { Order } from '../models/Order';
import { Address } from '../models/Address';
import { createPaymentIntent, handleWebhook, createRefund } from '../services/payment';

export const createPayment = async (req: Request, res: Response) => {
  try {
    const { order_id } = req.body;
    const order = await Order.findByPk(order_id, {
      include: [
        {
          model: Address,
          as: 'shipping_address',
        },
        {
          model: Address,
          as: 'billing_address',
        },
      ],
    });

    if (!order) {
      return res.status(404).json({ error: 'Order not found.' });
    }

    // Check if user owns the order
    if (order.user_id !== req.user!.id) {
      return res.status(403).json({ error: 'Not authorized to pay for this order.' });
    }

    const paymentIntent = await createPaymentIntent(
      order,
      order.shipping_address,
      order.billing_address
    );

    res.json(paymentIntent);
  } catch (error) {
    res.status(500).json({ error: 'Error creating payment.' });
  }
};

export const handleStripeWebhook = async (req: Request, res: Response) => {
  const sig = req.headers['stripe-signature'];

  try {
    const event = stripe.webhooks.constructEvent(
      req.body,
      sig!,
      process.env.STRIPE_WEBHOOK_SECRET!
    );

    await handleWebhook(event);
    res.json({ received: true });
  } catch (error) {
    console.error('Webhook error:', error);
    res.status(400).json({ error: 'Webhook error.' });
  }
};

export const requestRefund = async (req: Request, res: Response) => {
  try {
    const { order_id } = req.params;
    const order = await Order.findByPk(order_id);

    if (!order) {
      return res.status(404).json({ error: 'Order not found.' });
    }

    // Check if user owns the order
    if (order.user_id !== req.user!.id) {
      return res.status(403).json({ error: 'Not authorized to refund this order.' });
    }

    // Check if order is eligible for refund
    if (!['processing', 'shipped', 'delivered'].includes(order.status)) {
      return res.status(400).json({ error: 'Order is not eligible for refund.' });
    }

    const refund = await createRefund(order);

    res.json(refund);
  } catch (error) {
    res.status(500).json({ error: 'Error processing refund.' });
  }
}; 