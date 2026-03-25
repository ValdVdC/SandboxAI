"""
⚙️ Celery Configuration — SandboxAI

Configuração central do Celery para execução assíncrona de testes.
"""

import os

from celery import Celery

# Criar instância do Celery (convenção: usar 'app' para Celery CLI encontrar)
app = Celery(
    "sandboxai",
    broker=os.getenv("REDIS_URL", "redis://redis:6379"),
    backend=os.getenv("REDIS_URL", "redis://redis:6379"),
)

# Configuração do Celery
app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=int(os.getenv("MAX_CONTAINER_TIMEOUT", "60")) + 60,  # +60s buffer
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Alias para compatibilidade
celery_app = app

__all__ = ["app", "celery_app"]
