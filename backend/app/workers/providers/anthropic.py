"""Anthropic LLM provider implementation."""

import os
import time

from anthropic import Anthropic

from app.workers.providers import BaseProvider, ProviderResult


class AnthropicProvider(BaseProvider):
    """Anthropic API provider for executing prompts."""

    def __init__(self):
        """Initialize Anthropic provider."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        self.client = Anthropic(api_key=api_key)

    async def execute(self, prompt: str, model: str, timeout: int) -> ProviderResult:
        """
        Execute prompt using Anthropic API.

        Args:
            prompt: Prompt text to execute
            model: Model identifier (e.g., "claude-3-5-sonnet-20240620", "claude-3-opus-20240229")
            timeout: Timeout in seconds

        Returns:
            ProviderResult with output and metrics

        Raises:
            TimeoutError: If execution exceeds timeout
            Exception: If API call fails
        """
        start_time = time.time()

        try:
            # Call Anthropic API
            message = self.client.messages.create(
                model=model,
                max_tokens=2048,
                temperature=0.7,
                system="You are a helpful assistant.",
                messages=[{"role": "user", "content": prompt}],
                timeout=timeout,
            )

            # Calculate metrics
            latency_ms = (time.time() - start_time) * 1000
            output = message.content[0].text

            # Extract token usage
            usage = message.usage
            input_tokens = usage.input_tokens
            output_tokens = usage.output_tokens
            tokens_used = input_tokens + output_tokens

            # Simple cost estimation (Claude 3.5 Sonnet pricing)
            # Input: $3 per 1M tokens | Output: $15 per 1M tokens
            cost_usd = (input_tokens * 3.00 + output_tokens * 15.00) / 1_000_000

            return ProviderResult(
                output=output,
                latency_ms=latency_ms,
                tokens_used=tokens_used,
                cost_usd=cost_usd,
            )

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            raise Exception(f"Anthropic execution failed: {str(e)}") from e
