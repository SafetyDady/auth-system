#!/bin/bash

# Set environment variables
export PORT=${PORT:-8000}

# Run database migrations
echo "Running database migrations..."
alembic upgrade head || echo "Migration failed or skipped"

# Create initial users if needed
echo "Creating initial users..."
python3 scripts/create_initial_users.py || echo "Initial users creation failed or skipped"

# Start the FastAPI server
echo "Starting FastAPI server on port $PORT..."
uvicorn main:app --host 0.0.0.0 --port $PORT

