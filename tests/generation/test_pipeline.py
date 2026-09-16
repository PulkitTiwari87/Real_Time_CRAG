import pytest

from generation.pipeline import GenerationError, generate_grounded_answer
from retrieval.grader import Grade, GradedResult


def _graded(grade: Grade, chunk_id="c1", content="the sky is blue", confidence=0.9, source="doc1.txt"):
    return GradedResult(
        chunk_id=chunk_id,
        content=content,
        similarity_score=0.9,
        lexical_overlap=0.5,
        confidence=confidence,
        grade=grade,
        document_id="doc1",
        source=source,
    )


class _FakeProvider:
    model_name = "fake-model"

    def __init__(self, response_text="The sky is blue."):
        self._response_text = response_text
        self.last_prompt = None

    def generate(self, prompt: str) -> str:
        self.last_prompt = prompt
        return self._response_text


class _FailingProvider:
    model_name = "fake-model"

    def generate(self, prompt: str) -> str:
        from rag_baseline.llm_providers.base import LLMProviderError

        raise LLMProviderError("backend down")


def test_generate_uses_only_good_chunks_and_cites_sources():
    good = _graded(Grade.GOOD, chunk_id="c1", source="doc1.txt")
    bad = _graded(Grade.BAD, chunk_id="c2", content="unrelated", source="doc2.txt")
    provider = _FakeProvider()

    result = generate_grounded_answer("what color is the sky", [good, bad], provider=provider)

    assert result.answer == "The sky is blue."
    assert result.used_chunk_count == 1
    assert result.dropped_chunk_count == 1
    assert len(result.citations) == 1
    assert result.citations[0].source == "doc1.txt"
    assert "sky is blue" in provider.last_prompt.lower()
    assert "unrelated" not in provider.last_prompt.lower()  # BAD chunk excluded from prompt


def test_generate_abstains_when_nothing_graded_good():
    bad = _graded(Grade.BAD)
    result = generate_grounded_answer("anything", [bad], provider=_FakeProvider())
    assert "don't know" in result.answer.lower()
    assert result.citations == []
    assert result.used_chunk_count == 0
    assert result.dropped_chunk_count == 1


def test_generate_abstains_with_no_graded_results_at_all():
    result = generate_grounded_answer("anything", [], provider=_FakeProvider())
    assert "don't know" in result.answer.lower()


def test_generate_provider_failure_raises_generation_error():
    good = _graded(Grade.GOOD)
    with pytest.raises(GenerationError):
        generate_grounded_answer("q", [good], provider=_FailingProvider())
