"""Prompt version management endpoints."""

from fastapi import APIRouter, HTTPException, Query, Depends, status
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID, uuid4
from typing import Optional

from app.models import User, Prompt, PromptVersion
from app.core.database import get_db
from app.dependencies import get_current_user, get_user_prompt
from app.schemas import (
    VersionCreate,
    VersionResponse,
    VersionListResponse,
)

router = APIRouter(prefix="/prompts", tags=["Versions"])


@router.post(
    "/{prompt_id}/versions",
    response_model=VersionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_version(
    prompt_id: UUID,
    version_data: VersionCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> VersionResponse:
    """
    Create a new version for a prompt.

    Automatically increments version number and associates with the prompt.

    Args:
        prompt_id: ID of prompt to create version for
        version_data: Version data (content, provider, model)
        user: Current authenticated user
        db: Database session

    Returns:
        Created version with metadata
    """
    # Get prompt with ownership check
    prompt = await get_user_prompt(prompt_id, user, db)

    # Get current version count to determine next version number
    stmt = (
        select(func.count()).select_from(PromptVersion).where(PromptVersion.prompt_id == prompt_id)
    )
    result = await db.execute(stmt)
    count = result.scalar() or 0
    next_version = count + 1

    # Create new version
    version = PromptVersion(
        id=uuid4(),
        prompt_id=prompt_id,
        version=next_version,
        content=version_data.content,
        provider=version_data.provider,
        model=version_data.model,
        change_description=version_data.change_description,
    )

    # Update prompt version count
    prompt.version_count = next_version

    db.add(version)
    db.add(prompt)
    await db.commit()
    await db.refresh(version)

    return VersionResponse.from_orm(version)


@router.get("/{prompt_id}/versions", response_model=VersionListResponse)
async def list_versions(
    prompt_id: UUID,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> VersionListResponse:
    """
    List all versions of a prompt with pagination.

    Args:
        prompt_id: ID of prompt to list versions for
        page: Page number (1-indexed)
        per_page: Items per page
        user: Current authenticated user
        db: Database session

    Returns:
        Paginated list of versions
    """
    # Validate ownership
    prompt = await get_user_prompt(prompt_id, user, db)

    # Count total versions
    count_stmt = (
        select(func.count()).select_from(PromptVersion).where(PromptVersion.prompt_id == prompt_id)
    )
    count_result = await db.execute(count_stmt)
    total = count_result.scalar() or 0

    # Get versions with pagination
    stmt = (
        select(PromptVersion)
        .where(PromptVersion.prompt_id == prompt_id)
        .order_by(PromptVersion.version.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )

    result = await db.execute(stmt)
    versions = result.scalars().all()

    return VersionListResponse(
        total=total,
        items=[VersionResponse.from_orm(v) for v in versions],
    )


@router.get("/{prompt_id}/versions/{version_num}", response_model=VersionResponse)
async def get_version(
    prompt_id: UUID,
    version_num: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> VersionResponse:
    """
    Get a specific version of a prompt.

    Args:
        prompt_id: ID of prompt
        version_num: Version number
        user: Current authenticated user
        db: Database session

    Returns:
        Version details

    Raises:
        HTTPException: If prompt not found, user doesn't own it, or version doesn't exist
    """
    # Validate ownership
    prompt = await get_user_prompt(prompt_id, user, db)

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

    return VersionResponse.from_orm(version)
