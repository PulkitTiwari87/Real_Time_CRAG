"""Gemini-backed LLM provider.

Used as a development/verification provider alongside the local Ollama
path (see ollama_provider.py) -- not a replacement for it. Requires
GEMINI_API_KEY in the environment (e.g. via a local, gitignored .env file
loaded by dotenv.load_dotenv). The key is sent only as a request header,
never placed in a URL, never logged, and never exposed on this object's
public state.
"""
from __future__ import annotations

import os

import requests

from .base import LLMConfigError, LLMProviderError

DEFAULT_MODEL = "gemini-3.6-flash"
API_URL_TEMPLATE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


class GeminiProvider:
    def __init__(self, model: str | None = None, timeout: float = 60.0) -> None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise LLMConfigError("GEMINI_API_KEY is not set in the environment")
        self._api_key = api_key
        self.model_name = model or os.environ.get("GEMINI_MODEL") or DEFAULT_MODEL
        self._timeout = timeout

    def generate(self, prompt: str) -> str:
        url = API_URL_TEMPLATE.format(model=self.model_name)
        headers = {"x-goog-api-key": self._api_key, "Content-Type": "application/json"}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=self._timeout)
        except requests.RequestException as exc:
            raise LLMProviderError(f"Gemini API request failed (model={self.model_name}): {exc}") from exc

        if response.status_code != 200:
            raise LLMProviderError(
                f"Gemini API returned HTTP {response.status_code} (model={self.model_name}): {response.text[:300]}"
            )

        data = response.json()
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as exc:
            raise LLMProviderError("Gemini API returned an unexpected response shape") from exc
