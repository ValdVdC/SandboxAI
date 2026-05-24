"""Celery tasks for asynchronous test execution."""

import logging
import os
from datetime import datetime, timezone
from uuid import UUID

import numpy as np
from fastembed import TextEmbedding
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.models import TestResult
from app.workers.config import celery_app
from app.workers.providers.anthropic import AnthropicProvider
from app.workers.providers.groq import GroqProvider
from app.workers.providers.ollama import OllamaProvider
from app.workers.providers.openai import OpenAIProvider

# Configure logging
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://user:password@postgres:5432/db"
)
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=5,
    max_overflow=10,
)
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# Global TextEmbedding instance
_embedding_model = None


def get_embedding_model():
    """Lazily load and return the TextEmbedding model."""
    global _embedding_model
    if _embedding_model is None:
        logger.info(
            "Initializing TextEmbedding model (intfloat/multilingual-e5-small)..."
        )
        _embedding_model = TextEmbedding(model_name="intfloat/multilingual-e5-small")
    return _embedding_model


def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors."""
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(dot_product / (norm1 * norm2))


@celery_app.task(bind=True, max_retries=3, default_retry_delay=10)
def execute_test(
    self,
    test_id: str,
    prompt_content: str,
    provider: str,
    model: str,
):
    """
    Execute a test asynchronously.

    Args:
        test_id: UUID of the test result record
        prompt_content: The prompt text to execute
        provider: Provider name ("ollama" or "groq")
        model: Model identifier
    """
    import asyncio

    timeout = int(os.getenv("MAX_CONTAINER_TIMEOUT", "60"))

    # Create a new event loop for this task to avoid "Future attached to a different loop"
    # errors in Celery prefork environments with asyncpg
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        # Run async code in sync Celery context with isolated event loop
        result = loop.run_until_complete(
            _execute_test_async(
                test_id=UUID(test_id),
                prompt_content=prompt_content,
                provider=provider,
                model=model,
                timeout=timeout,
            )
        )
        return result
    except Exception as exc:
        logger.error(f"Task execute_test failed for {test_id}: {exc}")
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=2**self.request.retries)
    finally:
        loop.close()


async def _execute_test_async(
    test_id: UUID,
    prompt_content: str,
    provider: str,
    model: str,
    timeout: int,
) -> dict:
    """
    Execute test asynchronously with database updates.

    Args:
        test_id: UUID of test result
        prompt_content: Prompt template text
        provider: Provider name
        model: Model identifier
        timeout: Timeout in seconds

    Returns:
        Dictionary with execution result
    """
    # Get test input for prompt interpolation
    test_input = None
    async with AsyncSessionLocal() as db:
        try:
            stmt = select(TestResult).where(TestResult.id == test_id)
            result_obj = await db.execute(stmt)
            test_result = result_obj.scalar_one_or_none()

            if test_result:
                test_input = test_result.input

            # Update status to "running"
            stmt = (
                update(TestResult)
                .where(TestResult.id == test_id)
                .values(status="running", updated_at=datetime.now(timezone.utc))
            )
            await db.execute(stmt)
            await db.commit()

        except Exception as e:
            logger.error(f"Failed to update status to running: {e}")
            await db.rollback()
            raise

    # Interpolate prompt with test input
    final_prompt = prompt_content
    if test_input is not None:
        import json

        from jinja2 import Template

        try:
            # Try to parse test_input as JSON to support multiple variables
            input_data = json.loads(test_input)
            if isinstance(input_data, dict):
                template = Template(prompt_content)
                final_prompt = template.render(**input_data)
            else:
                # If it's a JSON but not a dictionary, fallback
                final_prompt = final_prompt.replace("{{input}}", str(test_input))
                final_prompt = final_prompt.replace("{input}", str(test_input))
        except (json.JSONDecodeError, TypeError):
            # Not valid JSON, fallback to simple string replacement
            final_prompt = final_prompt.replace("{{input}}", str(test_input))
            final_prompt = final_prompt.replace("{input}", str(test_input))

    # Execute provider (outside database session to avoid conflicts)
    try:
        provider_instance = _get_provider(provider)
        result = await provider_instance.execute(final_prompt, model, timeout)

    except Exception as e:
        logger.error(f"Provider execution failed for {test_id}: {e}")
        # Update failure in new session
        async with AsyncSessionLocal() as db:
            try:
                stmt = (
                    update(TestResult)
                    .where(TestResult.id == test_id)
                    .values(
                        status="failed",
                        error_message=str(e)[:500],
                        updated_at=datetime.now(timezone.utc),
                    )
                )
                await db.execute(stmt)
                await db.commit()
            except Exception as db_error:
                logger.error(f"Failed to update error status: {db_error}")
                await db.rollback()
        raise

    # Update with results in new session
    async with AsyncSessionLocal() as db:
        try:
            # Basic validation if expected output is provided
            is_correct = None
            score = None

            stmt = select(TestResult).where(TestResult.id == test_id)
            result_obj = await db.execute(stmt)
            test_result = result_obj.scalar_one_or_none()

            if test_result and test_result.expected and result.output:
                expected_norm = test_result.expected.lower().strip()
                output_norm = result.output.lower().strip()

                # Semantic Similarity validation via fastembed
                try:
                    model = get_embedding_model()

                    # Generate embeddings for both texts
                    # embed() returns a generator, so we convert it to a list
                    embeddings = list(model.embed([expected_norm, output_norm]))

                    if len(embeddings) == 2:
                        similarity = cosine_similarity(embeddings[0], embeddings[1])

                        threshold = float(os.getenv("SEMANTIC_THRESHOLD", "0.8"))
                        # Ensure score is bound between 0.0 and 1.0
                        score = max(0.0, min(1.0, similarity))
                        is_correct = score >= threshold

                        logger.info(
                            f"Semantic validation for {test_id}: Score={score:.4f}, Threshold={threshold}, Correct={is_correct}"
                        )
                    else:
                        logger.warning(
                            f"Embedding generation failed for {test_id}. Fallback to exact match."
                        )
                        is_correct = (
                            expected_norm in output_norm or output_norm in expected_norm
                        )
                        score = 1.0 if is_correct else 0.0
                except Exception as eval_err:
                    logger.error(
                        f"Error during semantic validation for {test_id}: {eval_err}"
                    )
                    # Fallback to exact match on error
                    is_correct = (
                        expected_norm in output_norm or output_norm in expected_norm
                    )
                    score = 1.0 if is_correct else 0.0

            stmt = (
                update(TestResult)
                .where(TestResult.id == test_id)
                .values(
                    output=result.output,
                    latency_ms=result.latency_ms,
                    tokens_used=result.tokens_used,
                    cost_usd=result.cost_usd,
                    is_correct=is_correct,
                    score=score,
                    status="completed",
                    error_message=None,
                    updated_at=datetime.now(timezone.utc),
                )
            )
            await db.execute(stmt)
            await db.commit()

            logger.info(f"Test {test_id} completed successfully")
            return {
                "test_id": str(test_id),
                "status": "completed",
                "latency_ms": result.latency_ms,
                "tokens_used": result.tokens_used,
                "cost_usd": result.cost_usd,
            }

        except Exception as e:
            logger.error(f"Failed to update completion status: {e}")
            await db.rollback()
            raise


def _get_provider(provider_name: str):
    """
    Factory function to get the appropriate provider instance.

    Args:
        provider_name: Name of the provider ("groq", "ollama", "openai", "anthropic")

    Returns:
        Provider instance

    Raises:
        ValueError: If provider is not supported
    """
    provider_name = provider_name.lower()
    if provider_name == "groq":
        return GroqProvider()
    elif provider_name == "ollama":
        return OllamaProvider()
    elif provider_name == "openai":
        return OpenAIProvider()
    elif provider_name == "anthropic":
        return AnthropicProvider()
    else:
        raise ValueError(f"Unsupported provider: {provider_name}")


@celery_app.task(bind=True)
def execute_test_with_priority(
    self,
    test_id: str,
    prompt_content: str,
    provider: str,
    model: str,
):
    """
    Execute test with higher priority.

    Same as execute_test but routed to priority queue.
    """
    return execute_test(test_id, prompt_content, provider, model)


@celery_app.task
def cleanup_stale_tests(hours: int = 24):
    """
    Clean up tests stuck in "running" status for too long.

    Args:
        hours: Hours to consider a test stale
    """
    import asyncio

    # Create a new event loop for this task to avoid event loop conflicts
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(_cleanup_stale_tests_async(hours))
    finally:
        loop.close()


async def _cleanup_stale_tests_async(hours: int):
    """Clean up stale tests in database."""
    from datetime import timedelta

    async with AsyncSessionLocal() as db:
        # Find tests stuck in "running" status
        stale_threshold = datetime.now(timezone.utc) - timedelta(hours=hours)

        # Update stale running tests to failed
        await db.execute(
            update(TestResult)
            .where(
                (TestResult.status == "running")
                & (TestResult.created_at < stale_threshold)
            )
            .values(
                status="failed",
                error_message=f"Stale test cleaned up after {hours} hours",
            )
        )
        await db.commit()

        logger.info("Cleaned up stale tests")
