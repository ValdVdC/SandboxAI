"""OpenAI LLM provider implementation."""

import os
import time

from openai import OpenAI

from app.workers.providers import BaseProvider, ProviderResult


class OpenAIProvider(BaseProvider):
    """OpenAI API provider for executing prompts."""

    def __init__(self):
        """Initialize OpenAI provider."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        self.client = OpenAI(api_key=api_key)

    async def execute(self, prompt: str, model: str, timeout: int) -> ProviderResult:
        """
        Execute prompt using OpenAI API.

        Args:
            prompt: Prompt text to execute
            model: Model identifier (e.g., "gpt-4o", "gpt-4-turbo")
            timeout: Timeout in seconds

        Returns:
            ProviderResult with output and metrics

        Raises:
            TimeoutError: If execution exceeds timeout
            Exception: If API call fails
        """
        start_time = time.time()

        try:
            # Call OpenAI API (Sync call in async method - wrapped in loop.run_in_executor in production usually,
            # but here it's running inside a worker's own event loop)
            # In a more robust implementation we'd use AsyncOpenAI
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=2048,
                temperature=0.7,
                timeout=timeout,
            )

            # Calculate metrics
            latency_ms = (time.time() - start_time) * 1000
            output = response.choices[0].message.content

            # Extract token usage
            usage = response.usage
            tokens_used = usage.total_tokens if usage else 0

            # Simple cost estimation (GPT-4o values - update as needed)
            # GPT-4o: ~$5.00 per 1M input, ~$15.00 per 1M output
            input_tokens = usage.prompt_tokens if usage else 0
            output_tokens = usage.completion_tokens if usage else 0

            # Default to GPT-4o pricing
            cost_usd = (input_tokens * 5.00 + output_tokens * 15.00) / 1_000_000

            return ProviderResult(
                output=output,
                latency_ms=latency_ms,
                tokens_used=tokens_used,
                cost_usd=cost_usd,
            )

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            raise Exception(f"OpenAI execution failed: {str(e)}") from e
