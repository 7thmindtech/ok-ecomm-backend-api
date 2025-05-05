import { Request, Response } from 'express';
import Category from '../models/Category';
import { generateSlug } from '../utils/slugify';

// Get all categories
export const getAllCategories = async (req: Request, res: Response) => {
  try {
    const categories = await Category.findAll({
      where: {
        is_active: true,
      },
      order: [['name', 'ASC']],
    });
    return res.json(categories);
  } catch (error) {
    console.error('Error fetching categories:', error);
    return res.status(500).json({ error: 'Failed to fetch categories' });
  }
};

// Get a single category by ID
export const getCategoryById = async (req: Request, res: Response) => {
  const { id } = req.params;
  try {
    const category = await Category.findByPk(id);
    if (!category) {
      return res.status(404).json({ error: 'Category not found' });
    }
    return res.json(category);
  } catch (error) {
    console.error(`Error fetching category with ID ${id}:`, error);
    return res.status(500).json({ error: 'Failed to fetch category' });
  }
};

// Create a new category
export const createCategory = async (req: Request, res: Response) => {
  const { name, description, parent_id, is_active } = req.body;
  try {
    // Generate slug from name
    const slug = await generateSlug(name);
    
    const category = await Category.create({
      name,
      description,
      slug,
      parent_id,
      is_active: is_active !== undefined ? is_active : true,
    });
    
    return res.status(201).json(category);
  } catch (error) {
    console.error('Error creating category:', error);
    return res.status(500).json({ error: 'Failed to create category' });
  }
};

// Update a category
export const updateCategory = async (req: Request, res: Response) => {
  const { id } = req.params;
  const { name, description, parent_id, is_active } = req.body;
  
  try {
    const category = await Category.findByPk(id);
    if (!category) {
      return res.status(404).json({ error: 'Category not found' });
    }
    
    // If name is changing, regenerate the slug
    let slug = category.slug;
    if (name && name !== category.name) {
      slug = await generateSlug(name);
    }
    
    await category.update({
      name: name || category.name,
      description: description !== undefined ? description : category.description,
      slug,
      parent_id: parent_id !== undefined ? parent_id : category.parent_id,
      is_active: is_active !== undefined ? is_active : category.is_active,
    });
    
    return res.json(category);
  } catch (error) {
    console.error(`Error updating category with ID ${id}:`, error);
    return res.status(500).json({ error: 'Failed to update category' });
  }
};

// Delete a category
export const deleteCategory = async (req: Request, res: Response) => {
  const { id } = req.params;
  
  try {
    const category = await Category.findByPk(id);
    if (!category) {
      return res.status(404).json({ error: 'Category not found' });
    }
    
    // Check if any products are using this category
    const productsCount = await Category.count({
      where: {
        parent_id: id,
      },
    });
    
    if (productsCount > 0) {
      return res.status(400).json({ 
        error: 'Cannot delete category with associated subcategories',
        count: productsCount 
      });
    }
    
    // Soft delete by setting is_active to false
    await category.update({ is_active: false });
    
    return res.json({ message: 'Category deactivated successfully' });
  } catch (error) {
    console.error(`Error deleting category with ID ${id}:`, error);
    return res.status(500).json({ error: 'Failed to delete category' });
  }
}; 