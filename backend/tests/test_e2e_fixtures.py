"""E2E Tests for Database Fixtures."""

import pytest
import uuid
from sqlalchemy import select
from app.models import User


@pytest.mark.asyncio
async def test_fixtures_create_user(sample_user):
    """Test that sample_user fixture creates a user."""
    assert sample_user is not None
    assert sample_user.email == "test@example.com"
    assert sample_user.is_active is True


@pytest.mark.asyncio
async def test_fixtures_create_prompt(sample_prompt, sample_user):
    """Test that sample_prompt fixture creates a prompt."""
    assert sample_prompt is not None
    assert sample_prompt.name == "Customer Support Response"
    assert sample_prompt.user_id == sample_user.id


@pytest.mark.asyncio
async def test_fixtures_create_version(sample_version, sample_prompt):
    """Test that sample_version fixture creates a version."""
    assert sample_version is not None
    assert sample_version.version == 1
    assert sample_version.prompt_id == sample_prompt.id
    assert sample_version.provider == "ollama"


@pytest.mark.asyncio
async def test_database_isolation(db_session):
    """Test that each test gets a clean database."""
    # Database should be empty at start of test
    stmt = select(User)
    result = await db_session.execute(stmt)
    users = result.scalars().all()
    assert len(users) == 0
    
    # Add a user
    user = User(
        id=uuid.uuid4(),
        email="isolation@test.com",
        hashed_password="hash",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    
    # Now we should have 1 user
    stmt = select(User)
    result = await db_session.execute(stmt)
    users = result.scalars().all()
    assert len(users) == 1
