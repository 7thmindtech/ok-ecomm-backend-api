# Categories API Implementation

This document describes the implementation of the Categories API in the OKYKE e-commerce platform, which provides a hierarchical structure for organizing products.

## Overview

The Categories system provides:

1. A hierarchical structure for products with parent-child relationships
2. URL-friendly slugs for SEO optimization
3. Support for category images and descriptions
4. Integration with product filtering
5. Admin-only management endpoints with proper authentication

## Backend Implementation Details

### Models

- **`Category` Model**: Located in `backend/app/models/category.py`
  - Supports self-referential relationships for parent-child hierarchy
  - Contains fields for name, slug, description, image, and status
  - Includes `parent_id` foreign key for establishing the hierarchy

- **`Product` Model**: Updated in `backend/app/models/product.py`
  - Connects to categories via a foreign key relationship
  - `category_id` column links products to their primary category

### Database Schema

The category system uses the following database structure:

```
categories
├─ id (Primary Key)
├─ name (String, required)
├─ slug (String, unique, required)
├─ description (Text, optional)
├─ image_url (String, optional)
├─ parent_id (Foreign Key to categories.id, optional)
├─ status (String, default='active')
├─ created_at (DateTime)
└─ updated_at (DateTime)
```

Products are linked to categories via:

```
products
├─ ...
├─ category_id (Foreign Key to categories.id)
└─ ...
```

### API Endpoints

The following RESTful endpoints are available:

#### Public Endpoints

- `GET /api/v1/categories` - Get all categories
  - Query parameters:
    - `active_only=true` (optional) - Only return active categories
    - `include_products=true` (optional) - Include product counts per category
    
- `GET /api/v1/categories/tree` - Get categories in a hierarchical tree structure
  - Useful for building navigation menus and category filters
  
- `GET /api/v1/categories/{id_or_slug}` - Get a specific category by ID or slug
  - Returns detailed information about the category and its subcategories
  - Can include products in the category with `include_products=true`

#### Admin-Only Endpoints

- `POST /api/v1/categories` - Create a new category
  - Requires admin authentication
  - Automatically generates a slug from the name if not provided

- `PUT /api/v1/categories/{id}` - Update an existing category
  - Requires admin authentication
  - Can update any category properties including parent relationship

- `DELETE /api/v1/categories/{id}` - Delete a category
  - Requires admin authentication
  - Will not delete categories with products or child categories

### Schemas

The following Pydantic schemas are used:

- `CategoryBase` - Base schema with common fields (name, description, etc.)
- `CategoryCreate` - Schema for creating a category (adds parent_id)
- `CategoryUpdate` - Schema for updating a category (all fields optional)
- `CategoryResponse` - Schema for returning a category to clients
- `CategoryWithChildren` - Enhanced schema for returning a category with its hierarchy

### Utility Functions

- `slugify` utility in `backend/app/utils/slugify.py`:
  - Converts category names to URL-friendly slugs
  - Handles special characters and Unicode
  - Ensures uniqueness by appending a number if needed

## Usage Guide

### Setting Up Categories

When running the application for the first time:

1. The database migration will automatically create the categories table
2. Initial seed categories are created via the database seeding process
3. The API will be available immediately after database initialization

### Managing Categories via API

You can interact with the Categories API using the following methods:

```bash
# Get all categories
curl http://127.0.0.1:8888/api/v1/categories

# Get categories as a hierarchical tree
curl http://127.0.0.1:8888/api/v1/categories/tree

# Get a specific category by ID
curl http://127.0.0.1:8888/api/v1/categories/1

# Get a specific category by slug
curl http://127.0.0.1:8888/api/v1/categories/clothing

# Create a new category (admin authentication required)
curl -X POST http://127.0.0.1:8888/api/v1/categories \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
    -d '{
        "name": "New Category",
        "description": "A new category description",
        "parent_id": 1,
        "image_url": "http://example.com/image.jpg",
        "status": "active"
    }'

# Update an existing category (admin authentication required)
curl -X PUT http://127.0.0.1:8888/api/v1/categories/5 \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
    -d '{
        "name": "Updated Category Name",
        "status": "inactive"
    }'

# Delete a category (admin authentication required)
curl -X DELETE http://127.0.0.1:8888/api/v1/categories/5 \
    -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### Frontend Integration

The frontend integrates with the Categories API in several key areas:

1. **Navigation Menus**: Uses the `/categories/tree` endpoint to build hierarchical menus
2. **Product Filtering**: Uses categories to filter products on listing pages
3. **Product Details**: Shows the category path/breadcrumbs for each product
4. **Admin Panel**: Provides interfaces for managing categories

## Troubleshooting

### Common Issues and Solutions

1. **404 Errors on Category Endpoints**:
   - Verify the API is running on the correct port (8888)
   - Check that all migrations have been applied with `alembic current`
   - Ensure the categories router is properly included in `backend/app/api/v1/api.py`

2. **Category Creation Failures**:
   - Check for unique slug conflicts (try a different name)
   - Ensure the parent category ID exists if specified
   - Verify admin authentication is working correctly

3. **Missing Category Images**:
   - Check file permissions on the image storage directory
   - Verify the image URLs are accessible from the client
   - Ensure the correct base URL is being used for image paths

4. **Hierarchical Structure Issues**:
   - Check for circular references in the parent-child relationships
   - Verify that the `parent_id` points to a valid category
   - Ensure the tree structure is not too deep (maximum depth is 5 levels)

### Debugging Tips

If you encounter persistent issues:

1. Enable DEBUG level logging in `backend/app/core/config.py`
2. Check the database directly to verify category records
3. Use the Swagger documentation at http://127.0.0.1:8888/docs to test endpoints
4. Verify that the frontend is using the correct API base URL (`http://127.0.0.1:8888`)

## Future Enhancements

Planned improvements to the Categories system:

1. Add support for category-specific attributes
2. Implement category-based discounts and promotions
3. Add analytics for category performance
4. Enhance SEO features with category-specific meta tags
5. Implement category-based product recommendations 