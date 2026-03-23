# Celery Worker Module

## Overview

This module implements asynchronous task execution for test execution using Celery and Redis.

## Architecture

```
workers/
├── __init__.py          # Module marker
├── config.py            # Celery app configuration and queue setup
├── worker.py            # Worker entrypoint script
├── tasks.py             # Task definitions (@celery_app.task)
├── utils.py             # Helper functions for task execution
├── providers/
│   ├── __init__.py      # BaseProvider ABC
│   ├── groq.py          # Groq cloud LLM provider
│   └── ollama.py        # Ollama local LLM provider
```

## Components

### config.py
- Celery application instance configured with Redis broker/backend
- Queue definitions: `default`, `tests`, `priority`
- Task routing and timeouts
- Worker concurrency settings from environment

### providers/
Abstract provider pattern with two implementations:

1. **GroqProvider** (`groq.py`)
   - Cloud-based LLM via Groq API
   - Requires `GROQ_API_KEY` environment variable
   - Synchronous execution using Groq Python client
   - Cost calculation: ~$0.24/1M tokens

2. **OllamaProvider** (`ollama.py`)
   - Local LLM execution
   - Requires `OLLAMA_URL` environment variable (default: http://ollama:11434)
   - Asynchronous execution via HTTP API
   - Zero cost (local execution)

### tasks.py
Celery task definitions:

- `execute_test(test_id, prompt_content, provider, model)` - Main task
  - Receives task from queue
  - Executes prompt via selected provider
  - Updates database with results
  - Handles timeouts and errors with retries
  
- `execute_test_with_priority(...)` - Priority queue variant
- `cleanup_stale_tests(hours=24)` - Cleanup stuck tests

### utils.py
Helper functions:
- Database session management
- Provider instantiation
- Timeout validation
- Error formatting
- Statistics and monitoring

## Starting the Worker

### Docker Setup

Add to `docker-compose.yml`:
```yaml
celery-worker:
  build: ./backend
  command: python -m app.workers.worker
  environment:
    - DATABASE_URL=postgresql://user:password@postgres:5432/db
    - REDIS_URL=redis://redis:6379
    - GROQ_API_KEY=YOUR_API_KEY
    - OLLAMA_URL=http://ollama:11434
    - MAX_CONTAINER_TIMEOUT=60
    - MAX_CONCURRENT_TESTS=10
  depends_on:
    - postgres
    - redis
    - ollama
  networks:
    - internal
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL=postgresql://user:password@localhost:5432/db
export REDIS_URL=redis://localhost:6379
export GROQ_API_KEY=your_groq_api_key
export OLLAMA_URL=http://localhost:11434

# Start worker
celery -A app.workers.config worker --loglevel=info --concurrency=10

# Or using the entrypoint script
python -m app.workers.worker
```

## Task Execution Flow

1. **API Endpoint** → `POST /prompts/{id}/versions/{num}/tests`
2. **API Handler** → Creates TestResult record with status="queued"
3. **API Handler** → Enqueues task: `execute_test.delay(test_id, prompt, provider, model)`
4. **Redis Queue** → Stores serialized task
5. **Celery Worker** → Polls Redis queue
6. **Task Executor** → 
   - Gets appropriate provider instance
   - Calls `provider.execute(prompt, model, timeout)`
   - Updates TestResult with output, latency, tokens, cost
   - Sets status="completed" or "failed"
7. **Client** → Can poll `GET /tests/{test_id}` to check status

## Environment Variables

Required:
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis broker URL

Optional:
- `GROQ_API_KEY` - Groq API key for cloud provider
- `OLLAMA_URL` - Ollama API URL (default: http://ollama:11434)
- `MAX_CONTAINER_TIMEOUT` - Max execution time in seconds (default: 60)
- `MAX_CONCURRENT_TESTS` - Worker concurrency (default: 10)

## Monitoring

### Check Task Status
```bash
celery -A app.workers.config inspect active
celery -A app.workers.config inspect stats
```

### Logs
```bash
# Docker
docker logs sandbox-celery-worker

# Development
# Logs output to stdout with format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

### Redis Queue Status
```bash
redis-cli
> LLEN celery  # Length of default queue
> LLEN celery.tests  # Length of tests queue
> LLEN celery.priority  # Length of priority queue
```

## Error Handling

Tasks implement automatic retry with exponential backoff:
- Max retries: 3
- Initial delay: 10 seconds
- Exponential multiplier: 2x

Timeout handling:
- Soft timeout: `MAX_CONTAINER_TIMEOUT - 5` seconds (task.cancel())
- Hard timeout: `MAX_CONTAINER_TIMEOUT` seconds (worker.SIGTERM)

Failed tests:
- Status: "failed"
- Error message: Captured in database
- Manual retry: Re-execute via API endpoint

## Cost Tracking

Each task execution tracks costs:
- **Groq**: Based on input/output tokens at provider rates
- **Ollama**: Zero cost (local execution)

Stored in TestResult:
- `latency_ms` - Execution time
- `tokens_used` - Total tokens (input + output)
- `cost_usd` - Estimated cost

## Scaling

For multiple workers:
```bash
# Terminal 1: Worker 1
celery -A app.workers.config worker -l info -c 5 -n worker1@%h

# Terminal 2: Worker 2
celery -A app.workers.config worker -l info -c 5 -n worker2@%h

# Docker Compose: Multiple replicas
docker-compose up -d --scale celery-worker=3
```

All workers share the same Redis queue and can process tasks in parallel.
