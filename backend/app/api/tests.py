"""Test execution and result endpoints."""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies import get_current_user, get_user_prompt
from app.models import Prompt, PromptVersion, TestResult, User
from app.schemas import (
    TestBulkExecuteRequest,
    TestExecuteRequest,
    TestListResponse,
    TestResultResponse,
)
from app.workers.tasks import execute_test as execute_test_task

router = APIRouter(prefix="/prompts", tags=["Tests"])


@router.post("/{prompt_id}/versions/{version_num}/tests", status_code=status.HTTP_202_ACCEPTED)
async def execute_test(
    prompt_id: UUID,
    version_num: int,
    test_data: TestExecuteRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Execute a test for a specific prompt version.

    Creates a test result record and queues the execution task. Returns task ID for polling.

    Args:
        prompt_id: ID of prompt
        version_num: Version number to test
        test_data: Test input and expected output
        user: Current authenticated user
        db: Database session

    Returns:
        Test result ID for polling status

    Raises:
        HTTPException: If prompt/version not found or user doesn't own prompt
    """
    # Validate ownership and get prompt
    await get_user_prompt(prompt_id, user, db)

    # Get specific version
    stmt = select(PromptVersion).where(
        and_(
            PromptVersion.prompt_id == prompt_id,
            PromptVersion.version == version_num,
        )
    )

    result = await db.execute(stmt)
    version = result.scalar_one_or_none()

    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version {version_num} not found",
        )

    # Create test result record
    test_result = TestResult(
        id=uuid4(),
        version_id=version.id,
        input=test_data.input,
        output=None,  # Will be filled by async task
        expected=test_data.expected,
        latency_ms=0,
        tokens_used=0,
        cost_usd=0.0,
        status="queued",
        error_message=None,
        created_at=datetime.now(timezone.utc),
    )

    db.add(test_result)
    await db.commit()
    await db.refresh(test_result)

    # Queue task with Celery for async execution
    task = execute_test_task.delay(
        test_id=str(test_result.id),
        prompt_content=version.content,
        provider=version.provider,
        model=version.model,
    )

    return {
        "test_id": str(test_result.id),
        "celery_task_id": task.id,
        "status": "queued",
        "message": "Test queued for execution",
    }


@router.post("/{prompt_id}/versions/{version_num}/tests/bulk", status_code=status.HTTP_202_ACCEPTED)
async def execute_bulk_tests(
    prompt_id: UUID,
    version_num: int,
    bulk_data: TestBulkExecuteRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Execute multiple tests for a specific prompt version in bulk.

    Args:
        prompt_id: ID of prompt
        version_num: Version number
        bulk_data: List of inputs
        user: Current authenticated user
        db: Database session

    Returns:
        Summary of queued tests
    """
    # Validate ownership
    await get_user_prompt(prompt_id, user, db)

    # Get version
    stmt = select(PromptVersion).where(
        and_(
            PromptVersion.prompt_id == prompt_id,
            PromptVersion.version == version_num,
        )
    )
    result = await db.execute(stmt)
    version = result.scalar_one_or_none()

    if not version:
        raise HTTPException(status_code=404, detail=f"Version {version_num} not found")

    test_ids = []
    batch_id = uuid4()

    # Create all records first
    for test_input in bulk_data.inputs:
        test_id = uuid4()
        test_result = TestResult(
            id=test_id,
            version_id=version.id,
            batch_id=batch_id,
            input=test_input,
            status="queued",
            expected=bulk_data.expected,
            created_at=datetime.now(timezone.utc),
        )
        db.add(test_result)
        test_ids.append(str(test_id))

    await db.commit()

    # Queue tasks in parallel after commit
    task_ids = []
    for t_id in test_ids:
        task = execute_test_task.delay(
            test_id=t_id,
            prompt_content=version.content,
            provider=version.provider,
            model=version.model,
        )
        task_ids.append(task.id)

    return {
        "test_ids": test_ids,
        "celery_task_ids": task_ids,
        "total_queued": len(test_ids),
        "message": f"Successfully queued {len(test_ids)} tests",
    }


@router.get("/{prompt_id}/versions/{version_num}/tests", response_model=TestListResponse)
async def list_tests(
    prompt_id: UUID,
    version_num: int,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TestListResponse:
    """
    List test results for a specific prompt version with pagination.

    Args:
        prompt_id: ID of prompt
        version_num: Version number
        page: Page number (1-indexed)
        per_page: Items per page
        user: Current authenticated user
        db: Database session

    Returns:
        Paginated test results

    Raises:
        HTTPException: If prompt/version not found or user doesn't own prompt
    """
    # Validate ownership
    await get_user_prompt(prompt_id, user, db)

    # Get version
    stmt = select(PromptVersion).where(
        and_(
            PromptVersion.prompt_id == prompt_id,
            PromptVersion.version == version_num,
        )
    )

    result = await db.execute(stmt)
    version = result.scalar_one_or_none()

    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version {version_num} not found",
        )

    # Count total tests
    count_stmt = (
        select(func.count()).select_from(TestResult).where(TestResult.version_id == version.id)
    )
    count_result = await db.execute(count_stmt)
    total = count_result.scalar() or 0

    # Get test results with pagination
    stmt = (
        select(TestResult)
        .where(TestResult.version_id == version.id)
        .order_by(TestResult.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )

    result = await db.execute(stmt)
    tests = result.scalars().all()

    return TestListResponse(
        total=total,
        page=page,
        per_page=per_page,
        items=[TestResultResponse.from_orm(t) for t in tests],
    )


@router.get("/tests/{test_id}", response_model=TestResultResponse)
async def get_test_result(
    test_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TestResultResponse:
    """
    Get a specific test result by ID.

    Validates that the user owns the prompt that contains this test.

    Args:
        test_id: ID of test result
        user: Current authenticated user
        db: Database session

    Returns:
        Test result details

    Raises:
        HTTPException: If test not found or user doesn't own it
    """
    # Get test result with ownership validation through joins
    stmt = (
        select(TestResult)
        .join(PromptVersion, TestResult.version_id == PromptVersion.id)
        .join(Prompt, PromptVersion.prompt_id == Prompt.id)
        .where(
            and_(
                TestResult.id == test_id,
                Prompt.user_id == user.id,
            )
        )
    )

    result = await db.execute(stmt)
    test_result = result.scalar_one_or_none()

    if not test_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test result not found",
        )

    return TestResultResponse.from_orm(test_result)
