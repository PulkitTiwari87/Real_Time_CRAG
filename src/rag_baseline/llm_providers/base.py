"""Shared interface and errors for pluggable LLM providers."""
from __future__ import annotations

from typing import Protocol


class LLMProvider(Protocol):
    model_name: str

    def generate(self, prompt: str) -> str:
        """Return raw generated text for the given prompt."""
        ...


class LLMConfigError(RuntimeError):
    """Raised when a provider is misconfigured (e.g. missing credentials)."""


class LLMProviderError(RuntimeError):
    """Raised when a provider's backend call fails."""
