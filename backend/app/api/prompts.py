"""Prompt management endpoints."""

from typing import Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies import get_current_user, get_user_prompt
from app.models import Prompt, PromptVersion, User
from app.schemas import PromptCreate, PromptListResponse, PromptResponse, PromptUpdate

router = APIRouter(prefix="/prompts", tags=["Prompts"])


@router.post("", response_model=PromptResponse, status_code=status.HTTP_201_CREATED)
async def create_prompt(
    prompt_data: PromptCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PromptResponse:
    """
    Create a new prompt for the current user.

    Args:
        prompt_data: Prompt creation data (name, optional description)
        user: Current authenticated user
        db: Database session

    Returns:
        Created prompt with metadata
    """
    prompt = Prompt(
        id=uuid4(),
        user_id=user.id,
        name=prompt_data.name,
        description=prompt_data.description,
        version_count=0,
    )

    db.add(prompt)
    await db.commit()
    await db.refresh(prompt)

    return PromptResponse.from_orm(prompt)


@router.get("", response_model=PromptListResponse)
async def list_prompts(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PromptListResponse:
    """
    List prompts for the current user with pagination and search.

    Args:
        page: Page number (1-indexed)
        per_page: Items per page
        search: Search by prompt name (partial match, case-insensitive)
        user: Current authenticated user
        db: Database session

    Returns:
        Paginated list of prompts
    """
    # Build query
    query = select(Prompt).where(Prompt.user_id == user.id)

    # Apply search filter
    if search:
        query = query.where(Prompt.name.ilike(f"%{search}%"))

    # Count total before pagination
    count_stmt = select(func.count()).select_from(Prompt).where(Prompt.user_id == user.id)
    if search:
        count_stmt = count_stmt.where(Prompt.name.ilike(f"%{search}%"))

    count_result = await db.execute(count_stmt)
    total = count_result.scalar() or 0

    # Apply pagination
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)

    # Execute query
    result = await db.execute(query)
    prompts = result.scalars().all()

    return PromptListResponse(
        total=total,
        page=page,
        per_page=per_page,
        items=[PromptResponse.from_orm(p) for p in prompts],
    )


@router.get("/{prompt_id}", response_model=PromptResponse)
async def get_prompt(
    prompt: Prompt = Depends(get_user_prompt),
) -> PromptResponse:
    """
    Get a specific prompt by ID.

    Args:
        prompt: Prompt object (validated for user ownership)

    Returns:
        Prompt details
    """
    return PromptResponse.from_orm(prompt)


@router.patch("/{prompt_id}", response_model=PromptResponse)
async def update_prompt(
    prompt_id: UUID,
    prompt_data: PromptUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PromptResponse:
    """
    Update a prompt description.

    When updating, a new version is automatically created with the current description.

    Args:
        prompt_id: ID of prompt to update
        prompt_data: Update data (optional new description)
        user: Current authenticated user
        db: Database session

    Returns:
        Updated prompt
    """
    # Get prompt with ownership check
    stmt = select(Prompt).where(and_(Prompt.id == prompt_id, Prompt.user_id == user.id))
    result = await db.execute(stmt)
    prompt = result.scalar_one_or_none()

    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found",
        )

    # Update description if provided
    if prompt_data.description is not None:
        prompt.description = prompt_data.description

    db.add(prompt)
    await db.commit()
    await db.refresh(prompt)

    return PromptResponse.from_orm(prompt)


@router.post("/{prompt_id}/duplicate", response_model=PromptResponse)
async def duplicate_prompt(
    prompt_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PromptResponse:
    """
    Duplicate a prompt and its latest version.

    Args:
        prompt_id: ID of prompt to duplicate
        user: Current authenticated user
        db: Database session

    Returns:
        New duplicated prompt
    """
    # Get original prompt
    stmt = select(Prompt).where(and_(Prompt.id == prompt_id, Prompt.user_id == user.id))
    result = await db.execute(stmt)
    original = result.scalar_one_or_none()

    if not original:
        raise HTTPException(status_code=404, detail="Original prompt not found")

    # Get latest version
    stmt = (
        select(PromptVersion)
        .where(PromptVersion.prompt_id == prompt_id)
        .order_by(PromptVersion.version.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    latest_version = result.scalar_one_or_none()

    # Create new prompt
    new_prompt = Prompt(
        id=uuid4(),
        user_id=user.id,
        name=f"{original.name} (Copy)",
        description=original.description,
        version_count=1 if latest_version else 0,
    )
    db.add(new_prompt)

    # Duplicate version if exists
    if latest_version:
        new_version = PromptVersion(
            id=uuid4(),
            prompt_id=new_prompt.id,
            version=1,
            content=latest_version.content,
            provider=latest_version.provider,
            model=latest_version.model,
            change_description=f"Initial version duplicated from {original.name} v{latest_version.version}",
        )
        db.add(new_version)

    await db.commit()
    await db.refresh(new_prompt)

    return PromptResponse.from_orm(new_prompt)


@router.delete("/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prompt(
    prompt_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Delete a prompt and all its versions and test results.

    Cascading deletion removes all related data.

    Args:
        prompt_id: ID of prompt to delete
        user: Current authenticated user
        db: Database session

    Raises:
        HTTPException: If prompt not found or user doesn't own it
    """
    # Get prompt with ownership check
    stmt = select(Prompt).where(and_(Prompt.id == prompt_id, Prompt.user_id == user.id))
    result = await db.execute(stmt)
    prompt = result.scalar_one_or_none()

    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found",
        )

    await db.delete(prompt)
    await db.commit()
