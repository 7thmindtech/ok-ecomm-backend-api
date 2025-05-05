import { Request, Response } from 'express';
import { User } from '../models/User';
import { Product } from '../models/Product';
import { Order } from '../models/Order';
import { OrderItem } from '../models/OrderItem';
import { Op } from 'sequelize';

export const getAdminDashboard = async (req: Request, res: Response) => {
  try {
    // Get total users by role
    const usersByRole = await User.findAll({
      attributes: ['role', [sequelize.fn('COUNT', sequelize.col('id')), 'count']],
      group: ['role'],
    });

    // Get total products
    const totalProducts = await Product.count();

    // Get total orders and revenue
    const orders = await Order.findAll({
      attributes: [
        [sequelize.fn('COUNT', sequelize.col('id')), 'total_orders'],
        [sequelize.fn('SUM', sequelize.col('total_amount')), 'total_revenue'],
      ],
    });

    // Get recent orders
    const recentOrders = await Order.findAll({
      include: [
        {
          model: User,
          as: 'user',
          attributes: ['id', 'name', 'email'],
        },
        {
          model: OrderItem,
          as: 'items',
          include: [
            {
              model: Product,
              as: 'product',
            },
          ],
        },
      ],
      order: [['created_at', 'DESC']],
      limit: 5,
    });

    res.json({
      metrics: {
        users_by_role: usersByRole,
        total_products: totalProducts,
        total_orders: orders[0].get('total_orders'),
        total_revenue: orders[0].get('total_revenue'),
      },
      recent_orders: recentOrders,
    });
  } catch (error) {
    res.status(500).json({ error: 'Error fetching admin dashboard.' });
  }
};

export const getUsers = async (req: Request, res: Response) => {
  try {
    const { role, search } = req.query;
    const where: any = {};

    if (role) {
      where.role = role;
    }

    if (search) {
      where[Op.or] = [
        { name: { [Op.iLike]: `%${search}%` } },
        { email: { [Op.iLike]: `%${search}%` } },
      ];
    }

    const users = await User.findAll({
      where,
      attributes: { exclude: ['password'] },
      order: [['created_at', 'DESC']],
    });

    res.json(users);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching users.' });
  }
};

export const updateUser = async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const { name, email, role, is_active } = req.body;

    const user = await User.findByPk(id);
    if (!user) {
      return res.status(404).json({ error: 'User not found.' });
    }

    await user.update({ name, email, role, is_active });

    res.json({
      id: user.id,
      name: user.name,
      email: user.email,
      role: user.role,
      is_active: user.is_active,
    });
  } catch (error) {
    res.status(500).json({ error: 'Error updating user.' });
  }
};

export const getProducts = async (req: Request, res: Response) => {
  try {
    const { category, artist_id, search } = req.query;
    const where: any = {};

    if (category) {
      where.category = category;
    }

    if (artist_id) {
      where.artist_id = artist_id;
    }

    if (search) {
      where[Op.or] = [
        { name: { [Op.iLike]: `%${search}%` } },
        { description: { [Op.iLike]: `%${search}%` } },
      ];
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
      order: [['created_at', 'DESC']],
    });

    res.json(products);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching products.' });
  }
};

export const updateProduct = async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const { name, description, price, category, is_active } = req.body;

    const product = await Product.findByPk(id);
    if (!product) {
      return res.status(404).json({ error: 'Product not found.' });
    }

    await product.update({ name, description, price, category, is_active });

    res.json(product);
  } catch (error) {
    res.status(500).json({ error: 'Error updating product.' });
  }
};

export const getOrders = async (req: Request, res: Response) => {
  try {
    const { status, start_date, end_date, search } = req.query;
    const where: any = {};

    if (status) {
      where.status = status;
    }

    if (start_date && end_date) {
      where.created_at = {
        [Op.between]: [start_date, end_date],
      };
    }

    if (search) {
      where[Op.or] = [
        { id: { [Op.iLike]: `%${search}%` } },
        { '$user.name$': { [Op.iLike]: `%${search}%` } },
        { '$user.email$': { [Op.iLike]: `%${search}%` } },
      ];
    }

    const orders = await Order.findAll({
      where,
      include: [
        {
          model: User,
          as: 'user',
          attributes: ['id', 'name', 'email'],
        },
        {
          model: OrderItem,
          as: 'items',
          include: [
            {
              model: Product,
              as: 'product',
            },
          ],
        },
      ],
      order: [['created_at', 'DESC']],
    });

    res.json(orders);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching orders.' });
  }
};

export const updateOrderStatus = async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const { status } = req.body;

    const order = await Order.findByPk(id);
    if (!order) {
      return res.status(404).json({ error: 'Order not found.' });
    }

    await order.update({ status });

    res.json(order);
  } catch (error) {
    res.status(500).json({ error: 'Error updating order status.' });
  }
}; 