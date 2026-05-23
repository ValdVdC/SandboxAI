"""Integration tests for the Real-time Multi-Provider Playground endpoint."""

from unittest.mock import patch

import pytest
from httpx import AsyncClient

from app.dependencies import get_current_user
from app.main import app
from app.workers.providers import ProviderResult


class MockProvider:
    """Mock provider for testing playground executions."""

    def __init__(self, should_fail=False):
        self.should_fail = should_fail

    async def execute(self, prompt: str, model: str, timeout: int) -> ProviderResult:
        if self.should_fail or model == "fail-model":
            raise ValueError(f"Simulated execution failure for model {model}")

        return ProviderResult(
            output=f"Mocked output for prompt: '{prompt}' via model: {model}",
            latency_ms=120.0,
            tokens_used=42,
            cost_usd=0.00021,
        )


def get_mock_provider(provider_name: str):
    """Factory for mock providers."""
    if provider_name == "failing":
        return MockProvider(should_fail=True)
    return MockProvider()


@pytest.mark.asyncio
async def test_playground_run_success(client: AsyncClient, sample_user):
    """Test successful parallel execution in playground."""
    # Override authentication
    app.dependency_overrides[get_current_user] = lambda: sample_user

    payload = {
        "prompt_content": "Translate to Spanish: {{text}}",
        "input": '{"text": "Hello World"}',
        "expected": "Hola Mundo",
        "configs": [
            {"provider": "openai", "model": "gpt-4o"},
            {"provider": "groq", "model": "llama-3.3-70b-versatile"},
        ],
    }

    with patch("app.api.playground._get_provider", side_effect=get_mock_provider):
        response = await client.post("/playground/run", json=payload)

    # Cleanup overrides
    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 2

    # Verify first column (OpenAI)
    res_1 = data["results"][0]
    assert res_1["provider"] == "openai"
    assert res_1["model"] == "gpt-4o"
    assert "Mocked output for prompt: 'Translate to Spanish: Hello World'" in res_1["output"]
    assert res_1["status"] == "completed"
    assert res_1["latency_ms"] == 120.0
    assert res_1["tokens_used"] == 42
    assert res_1["cost_usd"] == 0.00021
    # Check that semantic matching has fallback evaluated
    assert res_1["is_correct"] is not None

    # Verify second column (Groq)
    res_2 = data["results"][1]
    assert res_2["provider"] == "groq"
    assert res_2["model"] == "llama-3.3-70b-versatile"
    assert res_2["status"] == "completed"


@pytest.mark.asyncio
async def test_playground_partial_failure_tolerance(client: AsyncClient, sample_user):
    """Test that one failing provider does not break other provider columns in playground."""
    app.dependency_overrides[get_current_user] = lambda: sample_user

    payload = {
        "prompt_content": "Translate: {{text}}",
        "input": '{"text": "Apple"}',
        "configs": [
            {"provider": "openai", "model": "gpt-4o"},
            {
                "provider": "groq",
                "model": "fail-model",
            },  # This one should raise exception
        ],
    }

    with patch("app.api.playground._get_provider", side_effect=get_mock_provider):
        response = await client.post("/playground/run", json=payload)

    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 2

    # Column 1 (Success)
    assert data["results"][0]["status"] == "completed"
    assert data["results"][0]["output"] is not None

    # Column 2 (Gracefully caught error)
    assert data["results"][1]["status"] == "failed"
    assert data["results"][1]["output"] is None
    assert "Simulated execution failure" in data["results"][1]["error_message"]


@pytest.mark.asyncio
async def test_playground_max_columns_limit(client: AsyncClient, sample_user):
    """Test that playground limits execution to max 3 configs."""
    app.dependency_overrides[get_current_user] = lambda: sample_user

    payload = {
        "prompt_content": "Hello",
        "input": "World",
        "configs": [
            {"provider": "openai", "model": "m1"},
            {"provider": "groq", "model": "m2"},
            {"provider": "ollama", "model": "m3"},
            {"provider": "anthropic", "model": "m4"},  # 4 is over the limit of 3
        ],
    }

    response = await client.post("/playground/run", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 400
    assert "allows up to 3 configurations maximum" in response.json()["detail"]


@pytest.mark.asyncio
async def test_playground_empty_configs_rejected(client: AsyncClient, sample_user):
    """Test that playground requires at least 1 config."""
    app.dependency_overrides[get_current_user] = lambda: sample_user

    payload = {
        "prompt_content": "Hello",
        "input": "World",
        "configs": [],
    }

    response = await client.post("/playground/run", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 400
    assert "Specify at least 1 provider configuration" in response.json()["detail"]


@pytest.mark.asyncio
async def test_playground_unauthorized(client: AsyncClient):
    """Test that playground endpoint requires authentication."""
    payload = {
        "prompt_content": "Hello",
        "input": "World",
        "configs": [{"provider": "openai", "model": "gpt-4o"}],
    }

    # No dependency override or authentication headers
    response = await client.post("/playground/run", json=payload)

    assert response.status_code == 401
