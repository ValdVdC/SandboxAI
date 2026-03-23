#!/bin/bash
# Entrypoint script to run migrations and start app

set -e

echo "🚀 Starting SandboxAI Backend..."

# Run migrations as root before dropping privileges
echo "🔄 Running database migrations..."
python /app/run_migrations.py

# Start the application
echo "✅ Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
