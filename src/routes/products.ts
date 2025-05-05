import express from 'express';
import { auth, authorize } from '../middleware/auth';
import {
  createProduct,
  getProducts,
  getProduct,
  updateProduct,
  deleteProduct,
  validateCustomization,
} from '../controllers/products';

const router = express.Router();

// Public routes
router.get('/', getProducts);
router.get('/:id', getProduct);
router.post('/validate-customization', validateCustomization);

// Protected routes
router.post('/', auth, authorize('artist', 'admin'), createProduct);
router.put('/:id', auth, authorize('artist', 'admin'), updateProduct);
router.delete('/:id', auth, authorize('artist', 'admin'), deleteProduct);

export default router; 