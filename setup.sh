#!/bin/bash

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Create app directory if it doesn't exist
mkdir -p app

# Start the FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload 