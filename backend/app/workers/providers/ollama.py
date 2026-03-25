"""Ollama local LLM provider implementation."""

import os
import time
from typing import Optional

import httpx

from app.workers.providers import BaseProvider, ProviderResult


class OllamaProvider(BaseProvider):
    """Ollama local provider for executing prompts."""

    def __init__(self):
        """Initialize Ollama provider."""
        self.base_url = os.getenv("OLLAMA_URL", "http://ollama:11434")

    async def execute(self, prompt: str, model: str, timeout: int) -> ProviderResult:
        """
        Execute prompt using Ollama local instance.

        Args:
            prompt: Prompt text to execute
            model: Model identifier (e.g., "llama2:7b")
            timeout: Timeout in seconds

        Returns:
            ProviderResult with output and metrics

        Raises:
            TimeoutError: If execution exceeds timeout
            Exception: If API call fails
        """
        start_time = time.time()

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                # Call Ollama API
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "stream": False,
                        "temperature": 0.7,
                    },
                )

                if response.status_code != 200:
                    raise Exception(f"Ollama API error: {response.status_code} - {response.text}")

                data = await response.json()

                # Calculate metrics
                latency_ms = (time.time() - start_time) * 1000
                output = data.get("response", "")

                # Ollama provides metrics in the response
                tokens_used = data.get("eval_count", 0) + data.get("prompt_eval_count", 0)

                # Ollama local is free (cost = 0)
                cost_usd = 0.0

                return ProviderResult(
                    output=output,
                    latency_ms=latency_ms,
                    tokens_used=tokens_used,
                    cost_usd=cost_usd,
                )

        except httpx.TimeoutException:
            latency_ms = (time.time() - start_time) * 1000
            raise TimeoutError(f"Ollama execution timed out after {timeout}s") from None
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            raise Exception(f"Ollama execution failed: {str(e)}") from e
