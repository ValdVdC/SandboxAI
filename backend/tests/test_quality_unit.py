"""
Unit tests for AI providers using Mocking.
Focus: Isolation and testing external dependencies without real network calls.
"""

import pytest
from unittest.mock import MagicMock, patch
from app.workers.providers.openai import OpenAIProvider
from app.workers.providers import ProviderResult

@pytest.mark.asyncio
async def test_openai_provider_success():
    """
    Test OpenAI provider success path using mocks.
    Demonstrates: Isolation (Unit Testing).
    """
    # Arrange
    with patch('app.workers.providers.openai.OpenAI') as MockOpenAI:
        # Mocking the client and its nested structure
        mock_client = MockOpenAI.return_value
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="Mocked response content"))
        ]
        mock_response.usage = MagicMock(total_tokens=100, prompt_tokens=40, completion_tokens=60)
        
        # Configure the mock to return the mocked response
        mock_client.chat.completions.create.return_value = mock_response
        
        provider = OpenAIProvider()
        
        # Act
        result = await provider.execute("Hello", "gpt-4o", 10)
        
        # Assert
        assert isinstance(result, ProviderResult)
        assert result.output == "Mocked response content"
        assert result.tokens_used == 100
        assert result.cost_usd > 0
        # Verify that the external API was called with expected parameters
        mock_client.chat.completions.create.assert_called_once()

@pytest.mark.asyncio
async def test_openai_provider_failure():
    """
    Test OpenAI provider failure path.
    Demonstrates: Robustness testing (Error handling).
    """
    # Arrange
    with patch('app.workers.providers.openai.OpenAI') as MockOpenAI:
        mock_client = MockOpenAI.return_value
        # Simulate an API error
        mock_client.chat.completions.create.side_effect = Exception("API Key Invalid")
        
        provider = OpenAIProvider()
        
        # Act & Assert
        with pytest.raises(Exception) as excinfo:
            await provider.execute("Hello", "gpt-4o", 10)
        
        assert "OpenAI execution failed" in str(excinfo.value)
        assert "API Key Invalid" in str(excinfo.value)
