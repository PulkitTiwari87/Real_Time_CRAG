from datetime import datetime, timedelta, timezone

import pytest

from retrieval.retriever import RetrievalResult
from time_aware.ranking import rank_by_recency_and_relevance

NOW = datetime(2024, 6, 1, tzinfo=timezone.utc)


def _result(chunk_id, score, published_at=None):
    return RetrievalResult(
        chunk_id=chunk_id, document_id=chunk_id, source=f"{chunk_id}.txt",
        content="content", score=score, method="vector", published_at=published_at,
    )


def test_highly_relevant_old_doc_beats_barely_relevant_new_doc():
    """The core requirement: do NOT blindly prefer the newest document if
    relevance is poor. With default weights (relevance-dominant), a highly
    relevant 200-day-old doc must still outrank a barely-relevant doc
    published today."""
    old_relevant = _result("old", score=0.95, published_at=(NOW - timedelta(days=200)).isoformat())
    new_irrelevant = _result("new", score=0.15, published_at=NOW.isoformat())

    ranked = rank_by_recency_and_relevance([old_relevant, new_irrelevant], now=NOW)

    assert ranked[0].result.chunk_id == "old"
    assert ranked[0].combined_score > ranked[1].combined_score


def test_high_recency_weight_can_flip_the_ranking():
    """Sanity check that recency_weight is a real, meaningful knob: with
    recency weighted heavily enough, the fresher (but less relevant) doc
    can win -- proving the default result above isn't just a fixed
    ordering the function always produces regardless of input."""
    old_relevant = _result("old", score=0.95, published_at=(NOW - timedelta(days=200)).isoformat())
    new_irrelevant = _result("new", score=0.15, published_at=NOW.isoformat())

    ranked = rank_by_recency_and_relevance([old_relevant, new_irrelevant], recency_weight=0.95, now=NOW)

    assert ranked[0].result.chunk_id == "new"


def test_similar_relevance_breaks_tie_by_recency():
    similar_old = _result("old", score=0.8, published_at=(NOW - timedelta(days=60)).isoformat())
    similar_new = _result("new", score=0.8, published_at=NOW.isoformat())

    ranked = rank_by_recency_and_relevance([similar_old, similar_new], now=NOW)

    assert ranked[0].result.chunk_id == "new"


def test_missing_published_at_gets_neutral_recency_not_penalized_as_stale():
    dated = _result("dated", score=0.5, published_at=(NOW - timedelta(days=500)).isoformat())
    undated = _result("undated", score=0.5, published_at=None)

    ranked = rank_by_recency_and_relevance([dated, undated], now=NOW)
    undated_result = next(r for r in ranked if r.result.chunk_id == "undated")
    dated_result = next(r for r in ranked if r.result.chunk_id == "dated")

    assert undated_result.recency_score == 0.5
    # Same relevance, but the very old dated doc should score at or below neutral.
    assert dated_result.recency_score <= undated_result.recency_score


def test_recency_score_exactly_one_half_life_is_half():
    result = _result("a", score=0.5, published_at=(NOW - timedelta(days=30)).isoformat())
    ranked = rank_by_recency_and_relevance([result], half_life_days=30.0, now=NOW)
    assert ranked[0].recency_score == pytest.approx(0.5, abs=0.01)


def test_invalid_recency_weight_raises():
    with pytest.raises(ValueError):
        rank_by_recency_and_relevance([_result("a", 0.5)], recency_weight=1.5)


def test_empty_results_returns_empty():
    assert rank_by_recency_and_relevance([]) == []
