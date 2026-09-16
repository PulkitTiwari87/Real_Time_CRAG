import pytest

from orchestration.graph import run_crag_graph
from retrieval.retriever import RetrievalResult


def _result(chunk_id="c1", content="the sky is blue", score=0.9):
    return RetrievalResult(
        chunk_id=chunk_id, document_id="doc1", source="doc1.txt", content=content, score=score, method="vector"
    )


class _FakeRetriever:
    def __init__(self):
        self.retrieve_calls = 0

    def retrieve(self, query, top_k=5):
        self.retrieve_calls += 1
        return [_result(content="completely unrelated content about mitochondria", score=0.01)]


class _RecoveringRetriever:
    def __init__(self):
        self.retrieve_calls = 0

    def retrieve(self, query, top_k=5):
        self.retrieve_calls += 1
        if self.retrieve_calls == 1:
            return [_result(content="completely unrelated content about mitochondria", score=0.01)]
        return [_result(content="the sky is blue and vivid", score=0.95)]


class _GoodFirstRetriever:
    def retrieve(self, query, top_k=5):
        return [_result(content="the sky is blue and vivid", score=0.95)]


class _FakeProvider:
    model_name = "fake-model"

    def generate(self, prompt: str) -> str:
        if "Rewritten query:" in prompt:
            return "rewritten query text"
        return "The sky is blue."


class _AlwaysFailingProvider:
    model_name = "fake-model"

    def generate(self, prompt: str) -> str:
        from rag_baseline.llm_providers.base import LLMProviderError

        raise LLMProviderError("provider unavailable")


def test_good_first_attempt_never_rewrites():
    result = run_crag_graph("what color is the sky", _GoodFirstRetriever(), provider=_FakeProvider(), max_retries=2)
    assert result.rewrite_count == 0
    assert result.recovered_by_rewrite is False
    assert result.abstained is False


def test_bounded_retries_never_exceed_max_retries():
    retriever = _FakeRetriever()
    max_retries = 2

    result = run_crag_graph("q", retriever, provider=_FakeProvider(), max_retries=max_retries)

    assert retriever.retrieve_calls == max_retries + 1
    assert result.rewrite_count == max_retries
    assert result.abstained is True
    assert "don't know" in result.answer.answer.lower()


def test_zero_max_retries_means_no_rewrites():
    retriever = _FakeRetriever()
    result = run_crag_graph("q", retriever, provider=_FakeProvider(), max_retries=0)
    assert retriever.retrieve_calls == 1
    assert result.rewrite_count == 0
    assert result.abstained is True


def test_recovery_via_rewrite():
    retriever = _RecoveringRetriever()
    result = run_crag_graph("what color is the sky", retriever, provider=_FakeProvider(), max_retries=2)
    assert retriever.retrieve_calls == 2
    assert result.rewrite_count == 1
    assert result.recovered_by_rewrite is True
    assert result.abstained is False
    assert result.answer.answer == "The sky is blue."


def test_negative_max_retries_raises():
    with pytest.raises(ValueError):
        run_crag_graph("q", _FakeRetriever(), provider=_FakeProvider(), max_retries=-1)


def test_rewrite_failure_stops_loop_and_abstains_rather_than_crash():
    retriever = _FakeRetriever()
    result = run_crag_graph("q", retriever, provider=_AlwaysFailingProvider(), max_retries=3)
    assert retriever.retrieve_calls == 1
    assert result.rewrite_count == 0
    assert result.abstained is True


def test_graph_result_matches_plain_loop_result_for_same_scenario():
    """Sanity check: the graph-based orchestration produces the same
    observable outcome as corrective.crag.run_crag's plain loop for an
    identical scenario -- Phase 08 changes orchestration, not behavior."""
    from corrective.crag import run_crag

    loop_result = run_crag("what color is the sky", _RecoveringRetriever(), provider=_FakeProvider(), max_retries=2)
    graph_result = run_crag_graph(
        "what color is the sky", _RecoveringRetriever(), provider=_FakeProvider(), max_retries=2
    )
    assert loop_result.rewrite_count == graph_result.rewrite_count
    assert loop_result.recovered_by_rewrite == graph_result.recovered_by_rewrite
    assert loop_result.abstained == graph_result.abstained
    assert loop_result.answer.answer == graph_result.answer.answer
