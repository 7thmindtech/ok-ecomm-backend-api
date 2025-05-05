#!/bin/bash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Install requirements if needed
pip install -r requirements.txt

# Run migrations
python -m alembic upgrade head

# Start the FastAPI server
uvicorn app.main:app --host 127.0.0.1 --port 3001 --reload 