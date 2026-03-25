"""Test configuration and fixtures."""

import os
import uuid
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from httpx import AsyncClient
from app.main import app
from app.models import Base, User, Prompt, PromptVersion, TestResult
from app.core.database import get_db


# PostgreSQL database for testing
TEST_DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://test:test@postgres:5432/test_sandboxai"
)


@pytest_asyncio.fixture(scope="function")
async def test_db():
    """Create a fresh test database for each test."""
    # Create async engine
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session factory
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    yield async_session

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(test_db):
    """Get a database session."""
    async with test_db() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(test_db):
    """Create test client with dependency override."""

    async def override_get_db():
        async with test_db() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def sample_user(db_session):
    """Create a sample user in the database."""
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        hashed_password="$2b$12$hashedpasswordhere",
        full_name="Test User",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def sample_prompt(db_session, sample_user):
    """Create a sample prompt in the database."""
    prompt = Prompt(
        id=uuid.uuid4(),
        user_id=sample_user.id,
        name="Customer Support Response",
        description="Template for AI-powered support",
        version_count=0,
    )
    db_session.add(prompt)
    await db_session.commit()
    await db_session.refresh(prompt)
    return prompt


@pytest_asyncio.fixture(scope="function")
async def sample_version(db_session, sample_prompt):
    """Create a sample prompt version."""
    version = PromptVersion(
        id=uuid.uuid4(),
        prompt_id=sample_prompt.id,
        version=1,
        content="You are a helpful customer support agent. Answer questions politely.",
        provider="ollama",
        model="llama2:7b",
    )
    db_session.add(version)
    await db_session.commit()
    await db_session.refresh(version)
    return version
