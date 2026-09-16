import pytest

from corrective.crag import run_crag
from retrieval.retriever import RetrievalResult


def _result(chunk_id="c1", content="the sky is blue", score=0.9):
    return RetrievalResult(
        chunk_id=chunk_id, document_id="doc1", source="doc1.txt", content=content, score=score, method="vector"
    )


class _FakeRetriever:
    """Always returns the same (irrelevant, low-score) result -> always grades BAD."""

    def __init__(self):
        self.retrieve_calls = 0

    def retrieve(self, query, top_k=5):
        self.retrieve_calls += 1
        return [_result(content="completely unrelated content about mitochondria", score=0.01)]


class _RecoveringRetriever:
    """BAD on the first call, GOOD on every call after (simulates a rewrite helping)."""

    def __init__(self):
        self.retrieve_calls = 0

    def retrieve(self, query, top_k=5):
        self.retrieve_calls += 1
        if self.retrieve_calls == 1:
            return [_result(content="completely unrelated content about mitochondria", score=0.01)]
        return [_result(content="the sky is blue and vivid", score=0.95)]


class _FakeProvider:
    model_name = "fake-model"

    def __init__(self):
        self.calls = 0

    def generate(self, prompt: str) -> str:
        self.calls += 1
        if "Rewritten query:" in prompt:
            return "rewritten query text"
        return "The sky is blue."


class _AlwaysFailingProvider:
    model_name = "fake-model"

    def generate(self, prompt: str) -> str:
        from rag_baseline.llm_providers.base import LLMProviderError

        raise LLMProviderError("provider unavailable")


def test_good_first_attempt_never_rewrites():
    class _GoodFirstRetriever:
        def retrieve(self, query, top_k=5):
            return [_result(content="the sky is blue and vivid", score=0.95)]

    provider = _FakeProvider()
    result = run_crag("what color is the sky", _GoodFirstRetriever(), provider=provider, max_retries=2)

    assert result.rewrite_count == 0
    assert result.recovered_by_rewrite is False
    assert result.abstained is False
    assert result.final_query == "what color is the sky"


def test_bounded_retries_never_exceed_max_retries():
    retriever = _FakeRetriever()  # always BAD
    provider = _FakeProvider()
    max_retries = 2

    result = run_crag("what color is the sky", retriever, provider=provider, max_retries=max_retries)

    # attempt 0 (original) + max_retries rewritten attempts = max_retries + 1 retrieve calls, never more.
    assert retriever.retrieve_calls == max_retries + 1
    assert result.rewrite_count == max_retries
    assert result.abstained is True
    assert "don't know" in result.answer.answer.lower()


def test_zero_max_retries_means_no_rewrites():
    retriever = _FakeRetriever()
    provider = _FakeProvider()

    result = run_crag("query", retriever, provider=provider, max_retries=0)

    assert retriever.retrieve_calls == 1
    assert result.rewrite_count == 0
    assert result.abstained is True


def test_recovery_via_rewrite():
    retriever = _RecoveringRetriever()
    provider = _FakeProvider()

    result = run_crag("what color is the sky", retriever, provider=provider, max_retries=2)

    assert retriever.retrieve_calls == 2  # BAD, then GOOD -- stops as soon as it recovers
    assert result.rewrite_count == 1
    assert result.recovered_by_rewrite is True
    assert result.abstained is False
    assert result.answer.answer == "The sky is blue."


def test_negative_max_retries_raises():
    with pytest.raises(ValueError):
        run_crag("q", _FakeRetriever(), provider=_FakeProvider(), max_retries=-1)


def test_rewrite_failure_stops_loop_and_abstains_rather_than_crash():
    retriever = _FakeRetriever()
    provider = _AlwaysFailingProvider()

    result = run_crag("query", retriever, provider=provider, max_retries=3)

    # Rewriting itself fails immediately (provider down) -> loop stops after attempt 1, no retries burned.
    assert retriever.retrieve_calls == 1
    assert result.rewrite_count == 0
    assert result.abstained is True
