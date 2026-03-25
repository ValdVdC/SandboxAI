"""Tests for Celery worker and provider implementations."""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from uuid import uuid4

from app.workers.providers.groq import GroqProvider
from app.workers.providers.ollama import OllamaProvider
from app.workers.config import celery_app


class TestGroqProvider:
    """Test Groq cloud provider."""

    @pytest.mark.asyncio
    @patch.dict("os.environ", {"GROQ_API_KEY": "test-key"})
    @patch("app.workers.providers.groq.Groq")
    async def test_groq_execute_success(self, mock_groq):
        """Test successful Groq API call."""
        # Mock Groq client response with MagicMock to support subscripting
        from unittest.mock import MagicMock

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test output"
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 5
        mock_response.usage.total_tokens = 15

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_groq.return_value = mock_client

        # Create provider and execute
        provider = GroqProvider()
        result = await provider.execute("test prompt", "test-model", 30)

        # Verify
        assert result.output == "Test output"
        assert result.tokens_used == 15
        assert result.latency_ms > 0
        assert result.cost_usd > 0

    @patch.dict("os.environ", {"GROQ_API_KEY": ""})
    def test_groq_missing_api_key(self):
        """Test Groq provider with missing API key."""
        with pytest.raises(ValueError):
            GroqProvider()


class TestOllamaProvider:
    """Test Ollama local provider."""

    @pytest.fixture
    def provider(self):
        return OllamaProvider()

    @pytest.mark.asyncio
    @patch("app.workers.providers.ollama.httpx.AsyncClient")
    async def test_ollama_execute_success(self, mock_client_class):
        """Test successful Ollama API call."""
        provider = OllamaProvider()

        # Mock HTTP response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = AsyncMock(
            return_value={
                "response": "Test output",
                "eval_count": 5,
                "prompt_eval_count": 10,
            }
        )

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client

        # Execute
        result = await provider.execute("test prompt", "test-model", 30)

        # Verify
        assert result.output == "Test output"
        assert result.tokens_used == 15
        assert result.cost_usd == 0.0


class TestCeleryConfiguration:
    """Test Celery app configuration."""

    def test_celery_app_configured(self):
        """Test that Celery app is properly configured."""
        assert celery_app is not None
        assert celery_app.conf.get("broker_url") is not None
        assert celery_app.conf.get("result_backend") is not None

    def test_task_routes_configured(self):
        """Test that task routes are configured."""
        routes = celery_app.conf.get("task_routes", {})
        assert "app.workers.tasks.execute_test" in routes or len(routes) > 0

    def test_queue_configuration(self):
        """Test that queues are configured."""
        queues = celery_app.conf.get("task_queues", [])
        assert len(queues) > 0


class TestProviderFactory:
    """Test provider factory functions."""

    def test_groq_provider_instantiation(self):
        """Test creating Groq provider."""
        from app.workers.utils import validate_provider

        assert validate_provider("groq") is True
        assert validate_provider("GROQ") is True

    def test_ollama_provider_instantiation(self):
        """Test creating Ollama provider."""
        from app.workers.utils import validate_provider

        assert validate_provider("ollama") is True
        assert validate_provider("OLLAMA") is True

    def test_invalid_provider(self):
        """Test creating invalid provider."""
        from app.workers.utils import validate_provider

        assert validate_provider("invalid") is False


class TestTimeoutHandling:
    """Test timeout validation and handling."""

    @patch.dict("os.environ", {"MAX_CONTAINER_TIMEOUT": "60"})
    def test_timeout_validation(self):
        """Test timeout validation."""
        from app.workers.utils import validate_timeout

        # Valid timeout
        assert validate_timeout(30) == 30

        # Exceeds max
        assert validate_timeout(120) == 60

        # Invalid timeout
        assert validate_timeout(0) == 60

    @patch.dict("os.environ", {"MAX_CONTAINER_TIMEOUT": "120"})
    def test_timeout_with_custom_max(self):
        """Test timeout validation with custom max."""
        from app.workers.utils import validate_timeout

        assert validate_timeout(90) == 90
        assert validate_timeout(150) == 120


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
