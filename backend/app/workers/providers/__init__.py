"""LLM provider implementations for test execution."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class ProviderResult:
    """Result from LLM provider execution."""

    output: str
    latency_ms: float
    tokens_used: int
    cost_usd: float


class BaseProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def execute(self, prompt: str, model: str, timeout: int) -> ProviderResult:
        """
        Execute a prompt with the provider.

        Args:
            prompt: The prompt text to execute
            model: The model identifier
            timeout: Timeout in seconds

        Returns:
            ProviderResult with output and metrics
        """
        pass
