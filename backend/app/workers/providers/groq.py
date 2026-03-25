"""Groq LLM provider implementation."""

import os
import time
from typing import Optional
from groq import Groq

from app.workers.providers import BaseProvider, ProviderResult


class GroqProvider(BaseProvider):
    """Groq API provider for executing prompts."""

    def __init__(self):
        """Initialize Groq provider."""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
        self.client = Groq(api_key=api_key)

    async def execute(self, prompt: str, model: str, timeout: int) -> ProviderResult:
        """
        Execute prompt using Groq API.

        Args:
            prompt: Prompt text to execute
            model: Model identifier (e.g., "llama-3.3-70b-versatile")
            timeout: Timeout in seconds

        Returns:
            ProviderResult with output and metrics

        Raises:
            TimeoutError: If execution exceeds timeout
            Exception: If API call fails
        """
        start_time = time.time()

        try:
            # Call Groq API
            message = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=1024,
                temperature=0.7,
            )

            # Calculate metrics
            latency_ms = (time.time() - start_time) * 1000
            output = message.choices[0].message.content

            # Extract token usage
            tokens_used = message.usage.total_tokens if message.usage else 0

            # Estimate cost (Groq pricing varies by model)
            # Llama-3.3-70b: ~$0.27 per 1M input, ~$0.81 per 1M output
            input_tokens = message.usage.prompt_tokens if message.usage else 0
            output_tokens = message.usage.completion_tokens if message.usage else 0
            cost_usd = (input_tokens * 0.27 + output_tokens * 0.81) / 1_000_000

            return ProviderResult(
                output=output,
                latency_ms=latency_ms,
                tokens_used=tokens_used,
                cost_usd=cost_usd,
            )

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            raise Exception(f"Groq execution failed: {str(e)}") from e
