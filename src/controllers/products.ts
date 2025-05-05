import { Request, Response } from 'express';
import { Product } from '../models/Product';
import { User } from '../models/User';

export const createProduct = async (req: Request, res: Response) => {
  try {
    const { name, description, price, category, customization_options } = req.body;
    const artist_id = req.user!.id;

    // Validate customization options
    if (customization_options) {
      for (const option of customization_options) {
        if (!option.type || !option.name || !option.options || !Array.isArray(option.options)) {
          return res.status(400).json({ error: 'Invalid customization option format.' });
        }
      }
    }

    const product = await Product.create({
      name,
      description,
      price,
      category,
      artist_id,
      customization_options: customization_options || [],
    });

    res.status(201).json(product);
  } catch (error) {
    res.status(500).json({ error: 'Error creating product.' });
  }
};

export const getProducts = async (req: Request, res: Response) => {
  try {
    const { category, artist_id } = req.query;
    const where: any = { is_active: true };

    if (category) {
      where.category = category;
    }

    if (artist_id) {
      where.artist_id = artist_id;
    }

    const products = await Product.findAll({
      where,
      include: [
        {
          model: User,
          as: 'artist',
          attributes: ['id', 'name'],
        },
      ],
    });

    res.json(products);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching products.' });
  }
};

export const getProduct = async (req: Request, res: Response) => {
  try {
    const product = await Product.findByPk(req.params.id, {
      include: [
        {
          model: User,
          as: 'artist',
          attributes: ['id', 'name'],
        },
      ],
    });

    if (!product) {
      return res.status(404).json({ error: 'Product not found.' });
    }

    res.json(product);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching product.' });
  }
};

export const updateProduct = async (req: Request, res: Response) => {
  try {
    const { name, description, price, category, customization_options, is_active } = req.body;
    const product = await Product.findByPk(req.params.id);

    if (!product) {
      return res.status(404).json({ error: 'Product not found.' });
    }

    // Check if user is the artist or admin
    if (product.artist_id !== req.user!.id && req.user!.role !== 'admin') {
      return res.status(403).json({ error: 'Not authorized to update this product.' });
    }

    // Validate customization options
    if (customization_options) {
      for (const option of customization_options) {
        if (!option.type || !option.name || !option.options || !Array.isArray(option.options)) {
          return res.status(400).json({ error: 'Invalid customization option format.' });
        }
      }
    }

    await product.update({
      name,
      description,
      price,
      category,
      customization_options,
      is_active,
    });

    res.json(product);
  } catch (error) {
    res.status(500).json({ error: 'Error updating product.' });
  }
};

export const deleteProduct = async (req: Request, res: Response) => {
  try {
    const product = await Product.findByPk(req.params.id);

    if (!product) {
      return res.status(404).json({ error: 'Product not found.' });
    }

    // Check if user is the artist or admin
    if (product.artist_id !== req.user!.id && req.user!.role !== 'admin') {
      return res.status(403).json({ error: 'Not authorized to delete this product.' });
    }

    await product.destroy();

    res.json({ message: 'Product deleted successfully.' });
  } catch (error) {
    res.status(500).json({ error: 'Error deleting product.' });
  }
};

export const validateCustomization = async (req: Request, res: Response) => {
  try {
    const { product_id, customization_data } = req.body;
    const product = await Product.findByPk(product_id);

    if (!product) {
      return res.status(404).json({ error: 'Product not found.' });
    }

    // Validate each customization option
    for (const option of product.customization_options) {
      const value = customization_data[option.name];
      
      if (option.required && !value) {
        return res.status(400).json({
          error: `${option.name} is required.`,
        });
      }

      if (value && !option.options.includes(value)) {
        return res.status(400).json({
          error: `Invalid value for ${option.name}.`,
        });
      }
    }

    res.json({ valid: true });
  } catch (error) {
    res.status(500).json({ error: 'Error validating customization.' });
  }
}; 