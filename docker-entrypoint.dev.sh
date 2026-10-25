#!/bin/sh
set -eu

echo "Running database migrations..."
uv run --no-sync alembic upgrade head

echo "Starting RMS API in development mode..."
exec uv run --no-sync uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
