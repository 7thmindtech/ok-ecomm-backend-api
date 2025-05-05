import express from 'express';
import { auth, authorize } from '../middleware/auth';
import {
  getAdminDashboard,
  getUsers,
  updateUser,
  getProducts,
  updateProduct,
  getOrders,
  updateOrderStatus,
} from '../controllers/admin';

const router = express.Router();

// All routes require admin role
router.use(auth, authorize('admin'));

// Dashboard
router.get('/dashboard', getAdminDashboard);

// Users
router.get('/users', getUsers);
router.put('/users/:id', updateUser);

// Products
router.get('/products', getProducts);
router.put('/products/:id', updateProduct);

// Orders
router.get('/orders', getOrders);
router.put('/orders/:id/status', updateOrderStatus);

export default router; 