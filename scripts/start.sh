#!/bin/bash

# Wait for the database to be ready
echo "Waiting for database to be ready..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done
echo "Database is ready!"

# Run migrations
echo "Running database migrations..."
alembic upgrade head

# Start the application
echo "Starting the application..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload 