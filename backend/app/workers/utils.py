"""Utility functions for Celery worker."""

import logging
import os
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.models import PromptVersion, TestResult

logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@postgres:5432/db")
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_test_result(test_id: UUID) -> Optional[TestResult]:
    """
    Get a test result by ID.

    Args:
        test_id: UUID of the test result

    Returns:
        TestResult instance or None if not found
    """
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(TestResult).where(TestResult.id == test_id))
        return result.scalars().first()


async def get_prompt_version(version_id: UUID) -> Optional[PromptVersion]:
    """
    Get a prompt version by ID.

    Args:
        version_id: UUID of the prompt version

    Returns:
        PromptVersion instance or None if not found
    """
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(PromptVersion).where(PromptVersion.id == version_id))
        return result.scalars().first()


def validate_timeout(timeout: int) -> int:
    """
    Validate and adjust timeout based on environment constraints.

    Args:
        timeout: Requested timeout in seconds

    Returns:
        Validated timeout in seconds
    """
    max_timeout = int(os.getenv("MAX_CONTAINER_TIMEOUT", "60"))

    if timeout <= 0:
        return max_timeout

    if timeout > max_timeout:
        logger.warning(f"Timeout {timeout}s exceeds max {max_timeout}s, using max")
        return max_timeout

    return timeout


def validate_provider(provider: str) -> bool:
    """
    Validate provider name.

    Args:
        provider: Provider name to validate

    Returns:
        True if provider is valid, False otherwise
    """
    valid_providers = ["groq", "ollama"]
    return provider.lower() in valid_providers


def validate_model(provider: str, model: str) -> bool:
    """
    Validate model for a given provider.

    Args:
        provider: Provider name
        model: Model identifier

    Returns:
        True if model is valid for provider, False otherwise
    """
    valid_models = {
        "groq": ["llama-3.3-70b-versatile", "gemma2-9b-it", "llama-3.1-8b-instant"],
        "ollama": ["mistral", "llama2", "neural-chat"],  # Common local models
    }

    if provider.lower() not in valid_models:
        return False

    # Ollama accepts any model name (downloaded locally)
    if provider.lower() == "ollama":
        return True

    # Groq has specific models
    return model in valid_models.get(provider.lower(), [])


def format_error_message(exc: Exception) -> str:
    """
    Format an exception into an error message.

    Args:
        exc: Exception instance

    Returns:
        Formatted error message
    """
    error_type = type(exc).__name__
    error_msg = str(exc)
    return f"{error_type}: {error_msg}"


def get_provider_config(provider: str) -> dict:
    """
    Get configuration for a specific provider.

    Args:
        provider: Provider name

    Returns:
        Provider configuration dictionary
    """
    if provider.lower() == "groq":
        return {
            "api_key": os.getenv("GROQ_API_KEY", ""),
            "default_model": "llama-3.3-70b-versatile",
        }
    elif provider.lower() == "ollama":
        return {
            "base_url": os.getenv("OLLAMA_URL", "http://ollama:11434"),
            "default_model": "mistral",
        }
    else:
        return {}


def calculate_retry_delay(attempt: int) -> int:
    """
    Calculate exponential backoff retry delay.

    Args:
        attempt: Current retry attempt (0-based)

    Returns:
        Delay in seconds
    """
    max_delay = 300  # 5 minutes
    delay = min(2**attempt, max_delay)
    return delay


async def get_pending_tests_count() -> int:
    """
    Get count of tests waiting in queue or running.

    Returns:
        Number of pending tests
    """
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(TestResult).where(TestResult.status.in_(["queued", "running"]))
        )
        return len(result.scalars().all())


async def get_test_statistics() -> dict:
    """
    Get overall test execution statistics.

    Returns:
        Dictionary with statistics
    """
    async with AsyncSessionLocal() as db:
        # Count by status
        stats = {}
        for status in ["queued", "running", "completed", "failed"]:
            result = await db.execute(select(TestResult).where(TestResult.status == status))
            stats[status] = len(result.scalars().all())

        return stats
