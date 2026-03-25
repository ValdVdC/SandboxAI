"""Celery application configuration."""

import os
from celery import Celery
from kombu import Exchange, Queue

# Create Celery app instance
celery_app = Celery(
    "sandboxai",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/1"),
)

# Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Broker configuration
    broker_connection_retry_on_startup=True,
    # Worker pool settings
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    # Task timeout
    task_soft_time_limit=int(os.getenv("MAX_CONTAINER_TIMEOUT", "60")) - 5,
    task_time_limit=int(os.getenv("MAX_CONTAINER_TIMEOUT", "60")),
    # Concurrency limits
    worker_concurrency=int(os.getenv("MAX_CONCURRENT_TESTS", "10")),
    # Queue configuration
    task_default_queue="default",
    task_queues=(
        Queue("default", Exchange("default"), routing_key="default"),
        Queue("tests", Exchange("tests"), routing_key="test.*"),
        Queue("priority", Exchange("priority"), routing_key="priority"),
    ),
)

# Task routes
celery_app.conf.task_routes = {
    "app.workers.tasks.execute_test": {"queue": "tests"},
    "app.workers.tasks.execute_test_with_priority": {"queue": "priority"},
}

# Import tasks to register them
celery_app.autodiscover_tasks(["app.workers"])
