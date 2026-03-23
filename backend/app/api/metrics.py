"""Analytics and metrics endpoints."""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List
from decimal import Decimal

from app.models import User, Prompt, PromptVersion, TestResult
from app.core.database import get_db
from app.dependencies import get_current_user, get_user_prompt
from app.schemas import (
    MetricsResponse,
    ProviderMetricsResponse,
)

router = APIRouter(prefix="/metrics", tags=["Metrics"])


@router.get("", response_model=MetricsResponse)
async def get_metrics(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MetricsResponse:
    """
    Get aggregated metrics for the current user.

    Returns overall statistics including total prompts, versions, tests, and performance metrics.

    Args:
        user: Current authenticated user
        db: Database session

    Returns:
        Aggregated metrics

    """
    # Count total prompts
    prompts_stmt = select(func.count()).select_from(Prompt).where(Prompt.user_id == user.id)
    prompts_result = await db.execute(prompts_stmt)
    total_prompts = prompts_result.scalar() or 0

    # Count total versions
    versions_stmt = (
        select(func.count())
        .select_from(PromptVersion)
        .join(Prompt, PromptVersion.prompt_id == Prompt.id)
        .where(Prompt.user_id == user.id)
    )
    versions_result = await db.execute(versions_stmt)
    total_versions = versions_result.scalar() or 0

    # Count total tests and get metrics for completed tests
    tests_stmt = (
        select(
            func.count(TestResult.id).label("count"),
            func.avg(TestResult.latency_ms).label("avg_latency"),
            func.sum(TestResult.tokens_used).label("total_tokens"),
            func.sum(TestResult.cost_usd).label("total_cost"),
        )
        .select_from(TestResult)
        .join(PromptVersion, TestResult.version_id == PromptVersion.id)
        .join(Prompt, PromptVersion.prompt_id == Prompt.id)
        .where(Prompt.user_id == user.id, TestResult.status == "completed")
    )

    tests_result = await db.execute(tests_stmt)
    tests_data = tests_result.one()

    total_tests_completed = tests_data.count or 0
    avg_latency_ms = float(tests_data.avg_latency) if tests_data.avg_latency else None
    total_tokens = int(tests_data.total_tokens) if tests_data.total_tokens else 0
    total_cost_usd = tests_data.total_cost or 0.0

    # Count tests by status
    pending_stmt = (
        select(func.count())
        .select_from(TestResult)
        .join(PromptVersion, TestResult.version_id == PromptVersion.id)
        .join(Prompt, PromptVersion.prompt_id == Prompt.id)
        .where(Prompt.user_id == user.id, TestResult.status == "queued")
    )
    pending_result = await db.execute(pending_stmt)
    tests_pending = pending_result.scalar() or 0

    failed_stmt = (
        select(func.count())
        .select_from(TestResult)
        .join(PromptVersion, TestResult.version_id == PromptVersion.id)
        .join(Prompt, PromptVersion.prompt_id == Prompt.id)
        .where(Prompt.user_id == user.id, TestResult.status == "failed")
    )
    failed_result = await db.execute(failed_stmt)
    tests_failed = failed_result.scalar() or 0

    return MetricsResponse(
        total_prompts=total_prompts,
        total_versions=total_versions,
        total_tests=total_tests_completed + tests_pending + tests_failed,
        average_latency_ms=avg_latency_ms,
        total_tokens_used=total_tokens,
        total_cost_usd=Decimal(str(total_cost_usd)),
        tests_completed=total_tests_completed,
        tests_failed=tests_failed,
        tests_pending=tests_pending,
    )


@router.get("/providers", response_model=List[ProviderMetricsResponse])
async def get_provider_metrics(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[ProviderMetricsResponse]:
    """
    Get metrics aggregated by provider.

    Returns per-provider statistics including test counts, latency, and costs.

    Args:
        user: Current authenticated user
        db: Database session

    Returns:
        List of provider metrics
    """
    stmt = (
        select(
            PromptVersion.provider.label("provider"),
            func.count(TestResult.id).label("test_count"),
            func.avg(TestResult.latency_ms).label("avg_latency"),
            func.sum(TestResult.tokens_used).label("total_tokens"),
            func.sum(TestResult.cost_usd).label("total_cost"),
        )
        .select_from(TestResult)
        .join(PromptVersion, TestResult.version_id == PromptVersion.id)
        .join(Prompt, PromptVersion.prompt_id == Prompt.id)
        .where(Prompt.user_id == user.id, TestResult.status == "completed")
        .group_by(PromptVersion.provider)
    )

    result = await db.execute(stmt)
    rows = result.all()

    metrics = []
    for row in rows:
        metrics.append(
            ProviderMetricsResponse(
                provider=row.provider,
                test_count=row.test_count or 0,
                avg_latency_ms=float(row.avg_latency) if row.avg_latency else 0.0,
                total_tokens_used=int(row.total_tokens) if row.total_tokens else 0,
                total_cost_usd=float(row.total_cost) if row.total_cost else 0.0,
            )
        )

    return metrics


@router.get("/by-prompt/{prompt_id}", response_model=MetricsResponse)
async def get_prompt_metrics(
    prompt_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MetricsResponse:
    """
    Get metrics for a specific prompt.

    Args:
        prompt_id: ID of prompt
        user: Current authenticated user
        db: Database session

    Returns:
        Metrics for this prompt

    Raises:
        HTTPException: If prompt not found or user doesn't own it
    """
    # Validate ownership
    prompt = await get_user_prompt(prompt_id, user, db)

    # Get versions count
    versions_stmt = select(func.count()).select_from(PromptVersion).where(
        PromptVersion.prompt_id == prompt_id
    )
    versions_result = await db.execute(versions_stmt)
    total_versions = versions_result.scalar() or 0

    # Get test metrics for completed tests
    tests_stmt = (
        select(
            func.count(TestResult.id).label("count"),
            func.avg(TestResult.latency_ms).label("avg_latency"),
            func.sum(TestResult.tokens_used).label("total_tokens"),
            func.sum(TestResult.cost_usd).label("total_cost"),
        )
        .select_from(TestResult)
        .join(PromptVersion, TestResult.version_id == PromptVersion.id)
        .where(PromptVersion.prompt_id == prompt_id, TestResult.status == "completed")
    )

    tests_result = await db.execute(tests_stmt)
    tests_data = tests_result.one()

    total_tests_completed = tests_data.count or 0
    avg_latency_ms = float(tests_data.avg_latency) if tests_data.avg_latency else None
    total_tokens = int(tests_data.total_tokens) if tests_data.total_tokens else 0
    total_cost_usd = tests_data.total_cost or 0.0

    # Count tests by status
    pending_stmt = (
        select(func.count())
        .select_from(TestResult)
        .join(PromptVersion, TestResult.version_id == PromptVersion.id)
        .where(PromptVersion.prompt_id == prompt_id, TestResult.status == "queued")
    )
    pending_result = await db.execute(pending_stmt)
    tests_pending = pending_result.scalar() or 0

    failed_stmt = (
        select(func.count())
        .select_from(TestResult)
        .join(PromptVersion, TestResult.version_id == PromptVersion.id)
        .where(PromptVersion.prompt_id == prompt_id, TestResult.status == "failed")
    )
    failed_result = await db.execute(failed_stmt)
    tests_failed = failed_result.scalar() or 0

    return MetricsResponse(
        total_prompts=1,  # Single prompt
        total_versions=total_versions,
        total_tests=total_tests_completed + tests_pending + tests_failed,
        average_latency_ms=avg_latency_ms,
        total_tokens_used=total_tokens,
        total_cost_usd=Decimal(str(total_cost_usd)),
        tests_completed=total_tests_completed,
        tests_failed=tests_failed,
        tests_pending=tests_pending,
    )
