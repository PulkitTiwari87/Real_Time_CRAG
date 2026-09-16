import pytest
import requests

from rag_baseline.llm_providers import get_provider
from rag_baseline.llm_providers.base import LLMConfigError, LLMProviderError
from rag_baseline.llm_providers.gemini_provider import GeminiProvider
from rag_baseline.llm_providers.ollama_provider import OllamaProvider


def test_get_provider_defaults_to_ollama(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    assert isinstance(get_provider(), OllamaProvider)


def test_get_provider_unknown_name_raises_config_error():
    with pytest.raises(LLMConfigError):
        get_provider("not-a-real-provider")


def test_ollama_provider_defaults(monkeypatch):
    monkeypatch.delenv("LLM_MODEL", raising=False)
    monkeypatch.delenv("OLLAMA_HOST", raising=False)
    provider = OllamaProvider()
    assert provider.model_name == "qwen3:8b"


def test_ollama_provider_wraps_connection_error(monkeypatch):
    provider = OllamaProvider(host="http://fake-host")

    def fake_post(*args, **kwargs):
        raise requests.ConnectionError("refused")

    monkeypatch.setattr("rag_baseline.llm_providers.ollama_provider.requests.post", fake_post)
    with pytest.raises(LLMProviderError):
        provider.generate("hello")


def test_gemini_provider_requires_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(LLMConfigError):
        GeminiProvider()


def test_gemini_provider_reads_config_from_env_without_exposing_key(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key-not-real")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-test-model")
    provider = GeminiProvider()
    assert provider.model_name == "gemini-test-model"
    # The key must never leak onto a public attribute or repr.
    assert "test-key-not-real" not in repr(provider)
    assert not hasattr(provider, "api_key")


def test_gemini_provider_wraps_connection_error(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key-not-real")
    provider = GeminiProvider()

    def fake_post(*args, **kwargs):
        raise requests.ConnectionError("refused")

    monkeypatch.setattr("rag_baseline.llm_providers.gemini_provider.requests.post", fake_post)
    with pytest.raises(LLMProviderError):
        provider.generate("hello")


def test_gemini_provider_wraps_non_200_response(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key-not-real")
    provider = GeminiProvider()

    class FakeResponse:
        status_code = 400
        text = "API key not valid. Please pass a valid API key."

    monkeypatch.setattr(
        "rag_baseline.llm_providers.gemini_provider.requests.post",
        lambda *a, **k: FakeResponse(),
    )
    with pytest.raises(LLMProviderError):
        provider.generate("hello")


def test_gemini_provider_parses_successful_response(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key-not-real")
    provider = GeminiProvider()

    class FakeResponse:
        status_code = 200

        def json(self):
            return {"candidates": [{"content": {"parts": [{"text": "hello back"}]}}]}

    monkeypatch.setattr(
        "rag_baseline.llm_providers.gemini_provider.requests.post",
        lambda *a, **k: FakeResponse(),
    )
    assert provider.generate("hi") == "hello back"


def test_gemini_provider_wraps_unexpected_response_shape(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key-not-real")
    provider = GeminiProvider()

    class FakeResponse:
        status_code = 200

        def json(self):
            return {"unexpected": "shape"}

    monkeypatch.setattr(
        "rag_baseline.llm_providers.gemini_provider.requests.post",
        lambda *a, **k: FakeResponse(),
    )
    with pytest.raises(LLMProviderError):
        provider.generate("hi")
