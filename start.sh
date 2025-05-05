#!/bin/bash
# Script to start the backend server

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export PYTHONPATH=.
export DEBUG=True
export ENVIRONMENT=development

# Make sure migrations are up to date
echo "Running migrations..."
alembic upgrade head

# Start the FastAPI server
echo "Starting server..."
uvicorn app.main:app --reload --port 8888 --host 0.0.0.0 