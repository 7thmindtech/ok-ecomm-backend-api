
# OKYKE E-commerce Platform

## Overview
OKYKE is a modern e-commerce platform built with NextJS (frontend) and FastAPI (backend). It features a powerful product customization tool that allows users to design personalized products with an interactive canvas.

## Features
- Dynamic product catalog with advanced filtering
- User authentication and profile management
- Shopping cart and checkout functionality
- Product filtering and search
- Admin dashboard for product and order management
- Order processing and tracking
- Reviews and ratings system
- **Interactive Product Customization**:
  - Canvas-based visual editor
  - Text, shapes, and image placement
  - Color and style customizations
  - Save and load designs
- **AI Image Generation**:
  - Integration with OpenAI DALL-E and Stability AI
  - Text-to-image generation for custom designs
  - Direct placement of AI-generated images onto products

## Architecture
The application is split into two main components:
- **Frontend**: NextJS application with Tailwind CSS for styling and Konva.js for canvas interaction
- **Backend**: FastAPI Python API with SQLAlchemy ORM and PostgreSQL database

## Complete Setup Guide

### Prerequisites
- Node.js (v18+)
- Python 3.9+
- PostgreSQL 13+
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/okyke_ecomm_v4.git
cd okyke_ecomm_v4
```

### 2. PostgreSQL Database Setup
1. Install PostgreSQL if not already installed:
   - **macOS**: `brew install postgresql` or download from [PostgreSQL website](https://www.postgresql.org/download/macosx/)
   - **Linux**: `sudo apt install postgresql postgresql-contrib`
   - **Windows**: Download installer from [PostgreSQL website](https://www.postgresql.org/download/windows/)

2. Start PostgreSQL service:
   - **macOS**: `brew services start postgresql`
   - **Linux**: `sudo systemctl start postgresql`
   - **Windows**: Automatic after installation or via Services

3. Create database and user:
```bash
# Login to PostgreSQL as the postgres superuser
sudo -u postgres psql

# Create the database
CREATE DATABASE okyke;

# Create a user with password (change password as needed)
CREATE USER okyke_user WITH PASSWORD 'your_secure_password';

# Grant privileges to the user
GRANT ALL PRIVILEGES ON DATABASE okyke TO okyke_user;

# Exit PostgreSQL
\q
```

### 3. Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create needed directories for local storage:
```bash
mkdir -p local_s3_storage/okyke-files/products
```

5. Create a `.env` file in the backend directory:
```bash
# Database connection
DATABASE_URL=postgresql://okyke_user:your_secure_password@localhost/okyke

# JWT Authentication
SECRET_KEY=your_jwt_secret_key_here_make_it_complex_and_random
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email Settings (if using email features)
MAIL_USERNAME=your_email@example.com
MAIL_PASSWORD=your_email_password
MAIL_FROM=your_email@example.com
MAIL_PORT=587
MAIL_SERVER=smtp.example.com
MAIL_TLS=True
MAIL_SSL=False

# AI Image Generation (if using)
OPENAI_API_KEY=your_openai_api_key
STABILITY_API_KEY=your_stability_ai_key

# Development mode
DEBUG=True
```

6. Set up the database schema:
```bash
# Apply all database migrations
alembic upgrade head
```

7. Seed the database:
```bash
python init_and_seed_db.py
```

### 4. Frontend Setup

1. Navigate to the frontend directory:
```bash
cd ../frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env.local` file with the following contents:
```
NEXT_PUBLIC_API_URL=http://127.0.0.1:8888
NEXT_PUBLIC_SITE_URL=http://localhost:3000

# Optional - for AI features
NEXT_PUBLIC_OPENAI_API_KEY=your_openai_api_key
NEXT_PUBLIC_STABILITY_API_KEY=your_stability_ai_key

# Authentication
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your_secret_key_generate_a_random_one

# Optional - for payment integration
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
STRIPE_SECRET_KEY=your_stripe_secret_key
```

## Running the Application

### Option 1: Starting Both Services Together
If you have the convenience script, use it:

```bash
# From the root directory
chmod +x start-services.sh  # Make script executable first time
./start-services.sh
```

This will start both the frontend and backend services in development mode with hot-reloading.

### Option 2: Starting Services Separately

#### Start the Backend
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8888
```

#### Start the Frontend
```bash
cd frontend
npm run dev
```

## Verifying the Setup

1. **Backend API**: Visit http://127.0.0.1:8888/docs to see the Swagger UI documentation. This confirms your backend is running correctly.

2. **Database Seeding**: If the database isn't already seeded, visit http://127.0.0.1:8888/seed in your browser.

3. **Frontend**: Navigate to http://localhost:3000 to view the application.

4. **Login**: Use these demo credentials to test admin functionality:
   - Email: admin@example.com
   - Password: password123

## Database Structure

The main database tables include:

- **users**: User accounts and authentication info
- **products**: Product listings with details
- **categories**: Product categorization
- **orders**: Customer orders
- **order_items**: Items within orders
- **customizations**: Saved product customizations
- **reviews**: Product reviews and ratings
- **cart_items**: Shopping cart contents

You can view the full schema by examining the SQLAlchemy models in `backend/app/models/` or via the Alembic migrations in `backend/alembic/versions/`.

## Troubleshooting

### Database Connection Issues
- Verify PostgreSQL is running: `pg_isready`
- Check connection string in your backend `.env` file
- Ensure your PostgreSQL user has proper permissions

### Backend Service Won't Start
- Check Python version (3.9+ required)
- Verify all dependencies are installed
- Check backend logs for specific errors

### Frontend Build Errors
- Verify Node.js version (18+ recommended)
- Clear npm cache: `npm cache clean --force`
- Remove node_modules and reinstall: `rm -rf node_modules && npm install`

### Image Upload Issues
- Verify the `local_s3_storage` directory exists and has write permissions
- Check storage paths in backend configuration

## Product Customization Features

### Canvas Editor
The product customization tool uses an interactive canvas powered by Konva.js to allow users to:
- Add and style text with different fonts, sizes, and colors
- Insert shapes (rectangles, circles, triangles, stars, etc.)
- Upload and place custom images
- Position and resize elements with drag-and-drop
- Undo/redo operations for design changes

### Responsive Layout
- Resizable sidebar with drag handle and double-click reset
- Collapsible design panels for mobile responsiveness
- Floating toolbar for easy access to design tools

### AI Integration
- Generate custom images directly in the editor using AI models
- Chatbot-style interface for describing desired images
- Multiple AI model support (OpenAI DALL-E, Stability AI)
- Direct placement of generated images onto the product

### Design Management
- Save customized designs to user account
- Add customized products directly to cart
- Download designs as high-quality PNG images
- Apply designs to different product variants (colors, sizes)

## Development Notes

### Data Flow
All data is loaded dynamically from the backend database:

1. The frontend makes API calls to the backend endpoints
2. The backend retrieves data from the PostgreSQL database
3. No mock data is used in production mode

### API Endpoints
Main API endpoints:
- GET /api/v1/products - List all products with filtering options
- GET /api/v1/products/{slug} - Get detailed information about a specific product
- GET /api/v1/products/{slug}/related - Get products related to a specific product
- GET /api/v1/categories - List all product categories
- POST /api/customize/save-customization - Save a customized product design
- POST /api/customize/generate-image - Generate an AI image for customization

## Maintenance Tasks

### Backup the Database
```bash
pg_dump -U okyke_user -d okyke -f okyke_backup.sql
```

### Restore the Database
```bash
psql -U okyke_user -d okyke -f okyke_backup.sql
```

### Update Dependencies
```bash
# Backend
cd backend
source venv/bin/activate
pip install --upgrade -r requirements.txt

# Frontend
cd frontend
npm update
```

## License
MIT 
