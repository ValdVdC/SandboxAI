"""E2E Tests for Models — Test database operations."""

import pytest
import uuid
from sqlalchemy import select
from app.models import User, Prompt, PromptVersion, TestResult


@pytest.mark.asyncio
async def test_create_and_retrieve_user(db_session):
    """Test creating and retrieving a user from database."""
    # Create user
    user_id = uuid.uuid4()
    user = User(
        id=user_id,
        email="newuser@example.com",
        hashed_password="$2b$12$hashed",
        full_name="New User",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()

    # Retrieve user
    stmt = select(User).where(User.email == "newuser@example.com")
    result = await db_session.execute(stmt)
    retrieved_user = result.scalar_one()

    # Validate
    assert retrieved_user.id == user_id
    assert retrieved_user.email == "newuser@example.com"
    assert retrieved_user.full_name == "New User"
    assert retrieved_user.is_active is True


@pytest.mark.asyncio
async def test_user_email_unique_constraint(db_session):
    """Test that user emails are unique."""
    user1 = User(
        id=uuid.uuid4(),
        email="same@example.com",
        hashed_password="hash1",
        is_active=True,
    )
    db_session.add(user1)
    await db_session.commit()

    # Try to add user with same email
    user2 = User(
        id=uuid.uuid4(),
        email="same@example.com",
        hashed_password="hash2",
        is_active=True,
    )
    db_session.add(user2)

    # Should raise integrity error
    with pytest.raises(Exception):  # IntegrityError
        await db_session.commit()


@pytest.mark.asyncio
async def test_create_prompt_for_user(db_session, sample_user):
    """Test creating a prompt linked to a user."""
    prompt = Prompt(
        id=uuid.uuid4(),
        user_id=sample_user.id,
        name="Test Prompt",
        description="A test prompt",
        version_count=0,
    )
    db_session.add(prompt)
    await db_session.commit()

    # Retrieve and validate
    stmt = select(Prompt).where(Prompt.id == prompt.id)
    result = await db_session.execute(stmt)
    retrieved = result.scalar_one()

    assert retrieved.user_id == sample_user.id
    assert retrieved.name == "Test Prompt"


@pytest.mark.asyncio
async def test_prompt_cascade_delete(db_session, sample_user):
    """Test that deleting a user cascades to delete prompts."""
    # Create prompt linked to user
    prompt = Prompt(
        id=uuid.uuid4(),
        user_id=sample_user.id,
        name="Will be deleted",
    )
    db_session.add(prompt)
    await db_session.commit()

    prompt_id = prompt.id

    # Delete user
    await db_session.delete(sample_user)
    await db_session.commit()

    # Verify prompt is also deleted
    stmt = select(Prompt).where(Prompt.id == prompt_id)
    result = await db_session.execute(stmt)
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_create_prompt_version(db_session, sample_prompt):
    """Test creating a version of a prompt."""
    version = PromptVersion(
        id=uuid.uuid4(),
        prompt_id=sample_prompt.id,
        version=1,
        content="You are helpful",
        provider="ollama",
        model="llama2:7b",
    )
    db_session.add(version)
    await db_session.commit()

    # Retrieve
    stmt = select(PromptVersion).where(PromptVersion.id == version.id)
    result = await db_session.execute(stmt)
    retrieved = result.scalar_one()

    assert retrieved.version == 1
    assert retrieved.provider == "ollama"
    assert retrieved.model == "llama2:7b"


@pytest.mark.asyncio
async def test_create_test_result(db_session, sample_version):
    """Test creating a test result."""
    from decimal import Decimal

    result = TestResult(
        id=uuid.uuid4(),
        version_id=sample_version.id,
        input="Help me!",
        output="I'm here to help!",
        expected="Helpful response",
        latency_ms=1250,
        tokens_used=85,
        cost_usd=Decimal("0.001275"),
        status="completed",
    )
    db_session.add(result)
    await db_session.commit()

    # Retrieve
    stmt = select(TestResult).where(TestResult.id == result.id)
    db_result = await db_session.execute(stmt)
    retrieved = db_result.scalar_one()

    assert retrieved.status == "completed"
    assert retrieved.latency_ms == 1250
    assert retrieved.tokens_used == 85


@pytest.mark.asyncio
async def test_full_hierarchy_create_retrieve(db_session):
    """Test creating full hierarchy: User -> Prompt -> Version -> TestResult."""
    from decimal import Decimal

    # 1. Create user
    user = User(
        id=uuid.uuid4(),
        email="hierarchy@example.com",
        hashed_password="hash",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()

    # 2. Create prompt
    prompt = Prompt(
        id=uuid.uuid4(),
        user_id=user.id,
        name="Hierarchy Test",
        version_count=1,
    )
    db_session.add(prompt)
    await db_session.commit()

    # 3. Create version
    version = PromptVersion(
        id=uuid.uuid4(),
        prompt_id=prompt.id,
        version=1,
        content="Test content",
        provider="groq",
        model="mixtral-8x7b",
    )
    db_session.add(version)
    await db_session.commit()

    # 4. Create test result
    test_result = TestResult(
        id=uuid.uuid4(),
        version_id=version.id,
        input="Test input",
        output="Test output",
        latency_ms=500,
        tokens_used=42,
        cost_usd=Decimal("0.0001"),
        status="completed",
    )
    db_session.add(test_result)
    await db_session.commit()

    # 5. Retrieve entire hierarchy
    stmt = select(User).where(User.id == user.id)
    result = await db_session.execute(stmt)
    retrieved_user = result.scalar_one()

    stmt = select(Prompt).where(Prompt.user_id == retrieved_user.id)
    result = await db_session.execute(stmt)
    retrieved_prompt = result.scalar_one()

    stmt = select(PromptVersion).where(PromptVersion.prompt_id == retrieved_prompt.id)
    result = await db_session.execute(stmt)
    retrieved_version = result.scalar_one()

    stmt = select(TestResult).where(TestResult.version_id == retrieved_version.id)
    result = await db_session.execute(stmt)
    retrieved_result = result.scalar_one()

    # 6. Validate entire chain
    assert retrieved_user.email == "hierarchy@example.com"
    assert retrieved_prompt.name == "Hierarchy Test"
    assert retrieved_version.model == "mixtral-8x7b"
    assert retrieved_result.status == "completed"
    assert retrieved_result.latency_ms == 500


@pytest.mark.asyncio
async def test_count_records(db_session, sample_user, sample_prompt, sample_version):
    """Test counting records in database."""
    from sqlalchemy import func

    # Count users
    stmt = select(func.count(User.id))
    result = await db_session.execute(stmt)
    user_count = result.scalar()
    assert user_count == 1

    # Count prompts
    stmt = select(func.count(Prompt.id))
    result = await db_session.execute(stmt)
    prompt_count = result.scalar()
    assert prompt_count == 1

    # Count versions
    stmt = select(func.count(PromptVersion.id))
    result = await db_session.execute(stmt)
    version_count = result.scalar()
    assert version_count == 1
