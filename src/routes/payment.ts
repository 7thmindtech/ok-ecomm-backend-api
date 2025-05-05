import express from 'express';
import { auth } from '../middleware/auth';
import {
  createPayment,
  handleStripeWebhook,
  requestRefund,
} from '../controllers/payment';

const router = express.Router();

// Public routes
router.post('/webhook', express.raw({ type: 'application/json' }), handleStripeWebhook);

// Protected routes
router.post('/create-payment', auth, createPayment);
router.post('/orders/:order_id/refund', auth, requestRefund);

export default router; 