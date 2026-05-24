"""CI/CD integration endpoints."""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies import get_current_user
from app.models import Prompt, PromptVersion, TestResult, User
from app.schemas import CIRunRequest, CIRunResponse, CIJobStatusResponse
from app.workers.tasks import execute_test as execute_test_task

router = APIRouter(prefix="/api/v1/ci", tags=["CI/CD"])


@router.post("/run", response_model=CIRunResponse)
async def trigger_ci_run(
    request: CIRunRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Triggers CI/CD tests for a list of prompts.
    Reads previous test inputs for the latest version of each prompt and re-runs them.
    """
    job_id = uuid.uuid4()
    queued_count = 0

    for prompt_id in request.prompt_ids:
        # Verify ownership
        stmt = select(Prompt).where(
            and_(Prompt.id == prompt_id, Prompt.user_id == user.id)
        )
        result = await db.execute(stmt)
        prompt = result.scalar_one_or_none()
        if not prompt:
            continue

        # Get latest version
        stmt = (
            select(PromptVersion)
            .where(PromptVersion.prompt_id == prompt.id)
            .order_by(PromptVersion.version.desc())
            .limit(1)
        )
        result = await db.execute(stmt)
        latest_version = result.scalar_one_or_none()

        if not latest_version:
            continue

        # Get unique inputs tested before for this prompt
        stmt = (
            select(TestResult.input, TestResult.expected)
            .join(PromptVersion, TestResult.version_id == PromptVersion.id)
            .where(PromptVersion.prompt_id == prompt.id)
            .distinct(TestResult.input)
        )
        result = await db.execute(stmt)
        previous_tests = result.all()

        if not previous_tests:
            continue

        test_ids = []
        for test_input, test_expected in previous_tests:
            test_id = uuid.uuid4()
            test_result = TestResult(
                id=test_id,
                version_id=latest_version.id,
                batch_id=job_id,
                input=test_input,
                status="queued",
                expected=test_expected,
                created_at=datetime.now(timezone.utc),
            )
            db.add(test_result)
            test_ids.append(str(test_id))
            queued_count += 1

        await db.commit()

        # Trigger Celery tasks
        for t_id in test_ids:
            execute_test_task.delay(
                test_id=t_id,
                prompt_content=latest_version.content,
                provider=latest_version.provider,
                model=latest_version.model,
            )

    if queued_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No previous test inputs found for the given prompts.",
        )

    return CIRunResponse(
        job_id=job_id,
        status="RUNNING",
        message=f"Queued {queued_count} tests for CI run.",
    )


@router.get("/run/{job_id}", response_model=CIJobStatusResponse)
async def get_ci_run_status(
    job_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Polling endpoint for CI/CD run.
    When tests are done, evaluates if there's a >20% cost increase or semantic precision drop.
    """
    stmt = select(TestResult).where(TestResult.batch_id == job_id)
    result = await db.execute(stmt)
    current_tests = result.scalars().all()

    if not current_tests:
        raise HTTPException(status_code=404, detail="Job ID not found")

    # Check if still running
    if any(t.status in ["queued", "running"] for t in current_tests):
        return CIJobStatusResponse(job_id=job_id, status="RUNNING")

    # All tests finished (completed or failed)
    total_cost = sum((float(t.cost_usd) if t.cost_usd else 0.0) for t in current_tests)
    scores = [float(t.score) for t in current_tests if t.score is not None]
    avg_score = sum(scores) / len(scores) if scores else 0.0

    # Get previous runs for these prompts to compare
    version_ids = list(set(t.version_id for t in current_tests))

    stmt = select(PromptVersion.prompt_id).where(PromptVersion.id.in_(version_ids))
    result = await db.execute(stmt)
    prompt_ids = result.scalars().all()

    # Find historical tests (excluding current job)
    stmt = (
        select(TestResult)
        .join(PromptVersion, TestResult.version_id == PromptVersion.id)
        .where(
            and_(
                PromptVersion.prompt_id.in_(prompt_ids),
                TestResult.batch_id != job_id,
                TestResult.status == "completed",
            )
        )
    )
    result = await db.execute(stmt)
    hist_tests = result.scalars().all()

    if not hist_tests:
        return CIJobStatusResponse(
            job_id=job_id,
            status="COMPLETED",
            final_status="PASS",
            justification="No historical data to compare. First run passed.",
        )

    hist_cost_per_test = sum(
        (float(t.cost_usd) if t.cost_usd else 0.0) for t in hist_tests
    ) / len(hist_tests)
    hist_scores = [float(t.score) for t in hist_tests if t.score is not None]
    hist_avg_score = sum(hist_scores) / len(hist_scores) if hist_scores else 0.0

    curr_cost_per_test = total_cost / len(current_tests)

    justification_lines = []
    failed = False

    if curr_cost_per_test > hist_cost_per_test * 1.2:
        failed = True
        justification_lines.append(
            f"Cost increased by >20% (Historical avg: ${hist_cost_per_test:.6f}, Current avg: ${curr_cost_per_test:.6f})."
        )
    else:
        justification_lines.append(
            f"Cost is within acceptable limits (Current avg: ${curr_cost_per_test:.6f})."
        )

    if avg_score < hist_avg_score:
        failed = True
        justification_lines.append(
            f"Semantic precision dropped (Historical avg: {hist_avg_score:.2f}, Current avg: {avg_score:.2f})."
        )
    else:
        justification_lines.append(
            f"Semantic precision is stable or improved (Current avg: {avg_score:.2f})."
        )

    final_status = "FAIL" if failed else "PASS"
    justification = " ".join(justification_lines)

    return CIJobStatusResponse(
        job_id=job_id,
        status="COMPLETED",
        final_status=final_status,
        justification=justification,
    )
