"""Pluggable LLM provider selection.

Provider-agnostic by design: 'ollama' (local, zero-cost, default) and
'gemini' (development/verification) are both first-class. Selection is via
the LLM_PROVIDER environment variable, defaulting to 'ollama' so the
project's zero-cost local execution path stays the default.
"""
from __future__ import annotations

import os

from ..dotenv import load_dotenv
from .base import LLMConfigError, LLMProvider, LLMProviderError
from .gemini_provider import GeminiProvider
from .ollama_provider import OllamaProvider

load_dotenv()


def get_provider(name: str | None = None) -> LLMProvider:
    provider_name = (name or os.environ.get("LLM_PROVIDER") or "ollama").strip().lower()
    if provider_name == "ollama":
        return OllamaProvider()
    if provider_name == "gemini":
        return GeminiProvider()
    raise LLMConfigError(f"Unknown LLM_PROVIDER: {provider_name!r} (expected 'ollama' or 'gemini')")


__all__ = [
    "LLMProvider",
    "LLMConfigError",
    "LLMProviderError",
    "get_provider",
    "OllamaProvider",
    "GeminiProvider",
]
