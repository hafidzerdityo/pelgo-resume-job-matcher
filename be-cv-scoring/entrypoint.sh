#!/bin/bash
set -e

export PYTHONPATH=/code

echo "Running Alembic migrations..."
alembic upgrade head

echo "Running seed script..."
python seed.py

echo "Starting API server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
