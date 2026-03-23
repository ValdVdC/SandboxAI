# Database Models Documentation

## Overview

The SandboxAI backend uses SQLAlchemy ORM with async support via `asyncpg`. All database models inherit from `BaseModel` which provides common fields like `created_at` and `updated_at`.

## Database Models

### 1. User

Represents application users.

**Table:** `users`

**Fields:**
- `id` (UUID): Primary key
- `email` (String[255]): Unique email address
- `hashed_password` (String[255]): Bcrypt hashed password
- `full_name` (String[255]): User's full name (optional)
- `is_active` (Boolean): Account status
- `created_at` (DateTime): Timestamp of creation
- `updated_at` (DateTime): Timestamp of last update

**Relationships:**
- `prompts`: One-to-many with Prompt (cascade delete)

**Constraints:**
- Unique constraint on `email`

**Example:**
```python
from app.models import User
from sqlalchemy import select

async with AsyncSessionLocal() as session:
    user = User(
        email="user@example.com",
        hashed_password="$2b$12$...",
        full_name="John Doe",
        is_active=True
    )
    session.add(user)
    await session.commit()
    
    # Query
    stmt = select(User).where(User.email == "user@example.com")
    result = await session.execute(stmt)
    user = result.scalar_one()
```

---

### 2. Prompt

Represents AI prompt templates created by users.

**Table:** `prompts`

**Fields:**
- `id` (UUID): Primary key
- `user_id` (UUID): Foreign key to User
- `name` (String[255]): Prompt name
- `description` (Text): Optional description
- `version_count` (Integer): Number of versions created
- `created_at` (DateTime): Timestamp of creation
- `updated_at` (DateTime): Timestamp of last update

**Relationships:**
- `user`: Many-to-one with User
- `versions`: One-to-many with PromptVersion (cascade delete)

**Example:**
```python
from app.models import Prompt

async with AsyncSessionLocal() as session:
    prompt = Prompt(
        user_id=user.id,
        name="Customer Support Response",
        description="Template for AI-powered support replies",
        version_count=0
    )
    session.add(prompt)
    await session.commit()
```

---

### 3. PromptVersion

Represents different versions of a prompt.

**Table:** `prompt_versions`

**Fields:**
- `id` (UUID): Primary key
- `prompt_id` (UUID): Foreign key to Prompt
- `version` (Integer): Version number (1, 2, 3...)
- `content` (Text): Actual prompt text/template
- `provider` (String[50]): LLM provider ("ollama", "groq", "openai", "anthropic")
- `model` (String[100]): Model name ("llama2:7b", "gpt-4", "claude-3", etc)
- `created_at` (DateTime): Timestamp of creation
- `updated_at` (DateTime): Timestamp of last update

**Relationships:**
- `prompt`: Many-to-one with Prompt
- `test_results`: One-to-many with TestResult (cascade delete)

**Example:**
```python
from app.models import PromptVersion

async with AsyncSessionLocal() as session:
    version = PromptVersion(
        prompt_id=prompt.id,
        version=1,
        content="You are a helpful customer support agent...",
        provider="ollama",
        model="llama2:7b"
    )
    session.add(version)
    await session.commit()
```

---

### 4. TestResult

Represents individual test execution results.

**Table:** `test_results`

**Fields:**
- `id` (UUID): Primary key
- `version_id` (UUID): Foreign key to PromptVersion
- `input` (Text): Input/question provided to the LLM
- `output` (Text): Response from the LLM
- `expected` (Text): Expected output for validation (optional)
- `latency_ms` (Integer): Response time in milliseconds
- `tokens_used` (Integer): Number of tokens consumed
- `cost_usd` (Numeric[10,6]): Cost in USD
- `status` (String[50]): "pending", "completed", or "failed"
- `error_message` (Text): Error details if status is "failed"
- `created_at` (DateTime): Timestamp of creation
- `updated_at` (DateTime): Timestamp of last update

**Relationships:**
- `prompt_version`: Many-to-one with PromptVersion

**Example:**
```python
from app.models import TestResult
from decimal import Decimal

async with AsyncSessionLocal() as session:
    result = TestResult(
        version_id=version.id,
        input="What is your return policy?",
        output="Our return policy allows 30 days...",
        expected="Our 30-day return policy...",
        latency_ms=1250,
        tokens_used=85,
        cost_usd=Decimal("0.001275"),
        status="completed"
    )
    session.add(result)
    await session.commit()
```

---

## Common Queries

### Get all prompts for a user

```python
from sqlalchemy import select
from app.models import User, Prompt

async with AsyncSessionLocal() as session:
    stmt = select(Prompt).where(Prompt.user_id == user_id)
    result = await session.execute(stmt)
    prompts = result.scalars().all()
```

### Get all versions of a prompt

```python
from sqlalchemy import select
from app.models import Prompt

async with AsyncSessionLocal() as session:
    stmt = select(Prompt).where(Prompt.id == prompt_id)
    result = await session.execute(stmt)
    prompt = result.scalar_one()
    versions = prompt.versions  # Lazy load relationship
```

### Get test results for a version

```python
from sqlalchemy import select
from app.models import PromptVersion

async with AsyncSessionLocal() as session:
    stmt = select(PromptVersion).where(PromptVersion.id == version_id)
    result = await session.execute(stmt)
    version = result.scalar_one()
    test_results = version.test_results
```

### Complex query with joins

```python
from sqlalchemy import select
from app.models import User, Prompt, PromptVersion, TestResult

async with AsyncSessionLocal() as session:
    stmt = (
        select(TestResult)
        .join(PromptVersion)
        .join(Prompt)
        .join(User)
        .where(User.id == user_id)
        .where(TestResult.status == "completed")
    )
    result = await session.execute(stmt)
    test_results = result.scalars().all()
```

## Best Practices

1. **Always use async context managers** for session management:
   ```python
   async with AsyncSessionLocal() as session:
       # Your code here
   ```

2. **Use relationships for lazy loading**, but be careful with N+1 queries
3. **Index foreign keys** for query performance (already done in models)
4. **Use Alembic for all schema changes**, never alter tables manually
5. **Don't forget to commit**:
   ```python
   await session.commit()
   ```
6. **Handle transactions properly**:
   ```python
   try:
       # Add/modify objects
       await session.commit()
   except Exception as e:
       await session.rollback()
       raise
   ```

## Type Hints

All model fields are properly typed for IDE autocomplete:

```python
user: User = ...
prompt: Prompt = user.prompts[0]  # Type hint: list[Prompt]
version: PromptVersion = prompt.versions[0]  # Type hint: list[PromptVersion]
result: TestResult = version.test_results[0]  # Type hint: list[TestResult]
```

## Migration Management

See [alembic/README.md](README.md) for migration instructions.
