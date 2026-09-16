import pytest

from rag_baseline.generator import GenerationError, generate_answer
from rag_baseline.llm_providers.base import LLMProviderError
from rag_baseline.retriever import RetrievedChunk


def _chunk(content="The sky is blue.", source="doc1.txt"):
    return RetrievedChunk(chunk_id="doc1::0", document_id="doc1", source=source, content=content, score=0.9)


class _FakeProvider:
    def __init__(self, response_text="The sky is blue.", model_name="fake-model"):
        self.model_name = model_name
        self._response_text = response_text
        self.last_prompt = None

    def generate(self, prompt: str) -> str:
        self.last_prompt = prompt
        return self._response_text


class _FailingProvider:
    model_name = "fake-model"

    def generate(self, prompt: str) -> str:
        raise LLMProviderError("backend unreachable")


def test_generate_answer_returns_text_and_citations():
    provider = _FakeProvider()
    result = generate_answer("What color is the sky?", [_chunk()], provider=provider)
    assert result.answer == "The sky is blue."
    assert result.citations == ["doc1.txt"]
    assert result.model == "fake-model"
    assert "sky" in provider.last_prompt.lower()
    assert "blue" in provider.last_prompt.lower()  # retrieved context reached the prompt


def test_generate_answer_no_chunks_returns_abstention():
    result = generate_answer("anything", [])
    assert "don't know" in result.answer.lower()
    assert result.citations == []


def test_generate_answer_provider_failure_raises_generation_error():
    with pytest.raises(GenerationError):
        generate_answer("q", [_chunk()], provider=_FailingProvider())


def test_generate_answer_unknown_provider_name_raises_generation_error():
    with pytest.raises(GenerationError):
        generate_answer("q", [_chunk()], provider_name="not-a-real-provider")
