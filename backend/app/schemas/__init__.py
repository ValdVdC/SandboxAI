"""Request/Response schemas for API validation."""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, computed_field

# ════════════════════════════════════════════════════════════════════════════
# Authentication Schemas
# ════════════════════════════════════════════════════════════════════════════


class UserRegister(BaseModel):
    """Schema for user registration."""

    email: EmailStr
    password: str
    full_name: str


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user response."""

    id: UUID
    email: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Schema for authentication token response."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ════════════════════════════════════════════════════════════════════════════
# Prompt Schemas
# ════════════════════════════════════════════════════════════════════════════


class PromptCreate(BaseModel):
    """Schema for creating a new prompt."""

    name: str
    description: Optional[str] = None


class PromptUpdate(BaseModel):
    """Schema for updating a prompt (creates new version)."""

    description: Optional[str] = None


class PromptResponse(BaseModel):
    """Schema for prompt response."""

    id: UUID
    user_id: UUID
    name: str
    description: Optional[str]
    version_count: int
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def current_version(self) -> int:
        """Return the current version number (same as version_count)."""
        return self.version_count

    class Config:
        from_attributes = True


class PromptListResponse(BaseModel):
    """Schema for listing prompts with pagination."""

    total: int
    page: int
    per_page: int
    items: list[PromptResponse]


# ════════════════════════════════════════════════════════════════════════════
# Prompt Version Schemas
# ════════════════════════════════════════════════════════════════════════════


class VersionCreate(BaseModel):
    """Schema for creating a new prompt version."""

    content: str
    provider: str  # "ollama", "groq", "openai", "anthropic"
    model: str  # "llama2:7b", "gpt-4", etc
    change_description: str | None = None  # Description of changes in this version


class VersionResponse(BaseModel):
    """Schema for prompt version response."""

    id: UUID
    prompt_id: UUID
    version: int
    content: str
    provider: str
    model: str
    change_description: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class VersionListResponse(BaseModel):
    """Schema for listing prompt versions."""

    total: int
    items: list[VersionResponse]


# ════════════════════════════════════════════════════════════════════════════
# Test Execution Schemas
# ════════════════════════════════════════════════════════════════════════════


class TestExecuteRequest(BaseModel):
    """Schema for executing a test."""

    input: str
    expected: Optional[str] = None


class TestResultResponse(BaseModel):
    """Schema for test result response."""

    id: UUID
    version_id: UUID
    input: str
    output: Optional[str]
    expected: Optional[str]
    latency_ms: Optional[int]
    tokens_used: Optional[int]
    cost_usd: Optional[Decimal]
    status: str  # "pending", "completed", "failed"
    error_message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class TestListResponse(BaseModel):
    """Schema for listing test results."""

    total: int
    page: int
    per_page: int
    items: list[TestResultResponse]


# ════════════════════════════════════════════════════════════════════════════
# Metrics Schemas
# ════════════════════════════════════════════════════════════════════════════


class MetricsResponse(BaseModel):
    """Schema for aggregated metrics."""

    total_prompts: int
    total_versions: int
    total_tests: int
    average_latency_ms: Optional[float]
    total_tokens_used: int
    total_cost_usd: Decimal
    tests_completed: int
    tests_failed: int
    tests_pending: int


class ProviderMetricsResponse(BaseModel):
    """Schema for metrics by provider."""

    provider: str
    model: str
    test_count: int
    average_latency_ms: Optional[float]
    average_tokens_per_test: Optional[float]
    average_cost_per_test: Optional[Decimal]


# ════════════════════════════════════════════════════════════════════════════
# Error Response Schemas
# ════════════════════════════════════════════════════════════════════════════


class ErrorResponse(BaseModel):
    """Schema for error responses."""

    detail: str
    error_code: str
    timestamp: datetime
