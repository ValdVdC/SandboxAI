#!/bin/bash
# Entrypoint script to run migrations and start app

set -e

echo "🚀 Starting SandboxAI Backend..."

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
max_attempts=30
attempt=1
while ! python -c "import asyncpg; import asyncio; asyncio.run(asyncpg.connect('postgresql://sandboxai:change-me-in-production@postgres:5432/sandboxai'))" 2>/dev/null; do
    if [ $attempt -ge $max_attempts ]; then
        echo "❌ Database failed to start after $max_attempts attempts"
        exit 1
    fi
    echo "   Attempt $attempt/$max_attempts..."
    sleep 1
    attempt=$((attempt + 1))
done
echo "✅ Database is ready!"

# Wait for Redis to be ready
echo "⏳ Waiting for Redis to be ready..."
redis_attempt=1
while ! python -c "import redis; redis.Redis(host='redis', port=6379).ping()" 2>/dev/null; do
    if [ $redis_attempt -ge 10 ]; then
        echo "❌ Redis failed to start"
        exit 1
    fi
    echo "   Attempt $redis_attempt/10..."
    sleep 1
    redis_attempt=$((redis_attempt + 1))
done
echo "✅ Redis is ready!"

# Run migrations
echo "🔄 Running database migrations..."
python /app/run_migrations.py

# Seed database with test data (development only)
echo "Seeding database with test data..."
python /app/seed_database.py

# Start the application
echo "✅ Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

