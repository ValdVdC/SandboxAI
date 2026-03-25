#!/usr/bin/env python
"""
Celery worker entrypoint.

Usage:
    python -m app.workers.worker
    
    Or with options:
    celery -A app.workers.config worker --loglevel=info --concurrency=10 --queues=default,tests,priority
"""

import os
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Validate environment
def validate_environment():
    """Validate required environment variables."""
    required_vars = ["DATABASE_URL", "REDIS_URL"]
    optional_vars = {
        "GROQ_API_KEY": "Groq provider will not work without this",
        "OLLAMA_URL": "Ollama provider will use default http://ollama:11434",
        "MAX_CONTAINER_TIMEOUT": "Default is 60 seconds",
        "MAX_CONCURRENT_TESTS": "Default is 10",
    }

    # Check required
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)

    if missing:
        logger.error(f"Missing required environment variables: {', '.join(missing)}")
        return False

    # Warn about optional
    for var, msg in optional_vars.items():
        if not os.getenv(var):
            logger.warning(f"{var} not set. {msg}")

    return True


def start_worker():
    """Start the Celery worker."""
    from app.workers.config import celery_app

    logger.info("Starting Celery worker...")
    logger.info(f"Database: {os.getenv('DATABASE_URL', 'Not configured')[:30]}...")
    logger.info(f"Redis: {os.getenv('REDIS_URL', 'Not configured')}")

    # Worker configuration from environment
    concurrency = int(os.getenv("MAX_CONCURRENT_TESTS", "10"))

    # Start worker with command-line arguments
    celery_app.worker_main(
        [
            "worker",
            f"--loglevel=info",
            f"--concurrency={concurrency}",
            "--queues=default,tests,priority",
            "--prefetch-multiplier=1",
            "--time-limit=120",  # Hard limit 2 minutes
        ]
    )


if __name__ == "__main__":
    # Validate environment setup
    if not validate_environment():
        logger.error("Environment validation failed. Exiting.")
        sys.exit(1)

    try:
        start_worker()
    except KeyboardInterrupt:
        logger.info("Worker interrupted")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Worker error: {e}", exc_info=True)
        sys.exit(1)
