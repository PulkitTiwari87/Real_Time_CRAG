"""Local, zero-cost LLM provider backed by a local Ollama server."""
from __future__ import annotations

import os

import requests

from .base import LLMProviderError

DEFAULT_MODEL = "qwen3:8b"
DEFAULT_HOST = "http://localhost:11434"


class OllamaProvider:
    def __init__(self, model: str | None = None, host: str | None = None, timeout: float = 60.0) -> None:
        self.model_name = model or os.environ.get("LLM_MODEL") or DEFAULT_MODEL
        self._host = host or os.environ.get("OLLAMA_HOST") or DEFAULT_HOST
        self._timeout = timeout

    def generate(self, prompt: str) -> str:
        try:
            response = requests.post(
                f"{self._host}/api/generate",
                json={"model": self.model_name, "prompt": prompt, "stream": False},
                timeout=self._timeout,
            )
        except requests.RequestException as exc:
            raise LLMProviderError(
                f"Could not reach local Ollama at {self._host} (model={self.model_name}): {exc}"
            ) from exc

        if response.status_code != 200:
            raise LLMProviderError(
                f"Ollama returned HTTP {response.status_code} (model={self.model_name}): {response.text[:300]}"
            )
        return response.json().get("response", "")
