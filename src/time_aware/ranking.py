"""Phase 12: freshness-aware re-ranking.

Blends relevance score with a recency score (exponential decay based on
published_at) rather than sorting by date alone -- a highly relevant but
older document should still be able to outrank a barely-relevant but
newer one. See scripts/benchmark_time_aware_ranking.py for a genuine test
of relevance-vs-freshness conflicts, not an assumed formula.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from retrieval.retriever import RetrievalResult

DEFAULT_HALF_LIFE_DAYS = 30.0
DEFAULT_RECENCY_WEIGHT = 0.3


@dataclass(frozen=True)
class RankedResult:
    result: RetrievalResult
    relevance_score: float
    recency_score: float
    combined_score: float


def _recency_score(published_at: str | None, half_life_days: float, now: datetime) -> float:
    """Exponential decay: 1.0 for "just published", 0.5 at one half-life,
    0.25 at two half-lives, etc. Missing/unparseable published_at -> a
    neutral 0.5, not 0 -- undated content should not be penalized as if
    it were maximally stale."""
    if not published_at:
        return 0.5
    try:
        published = datetime.fromisoformat(published_at)
    except ValueError:
        return 0.5
    if published.tzinfo is None:
        published = published.replace(tzinfo=timezone.utc)
    age_days = max(0.0, (now - published).total_seconds() / 86400)
    return 0.5 ** (age_days / half_life_days)


def rank_by_recency_and_relevance(
    results: list[RetrievalResult],
    recency_weight: float = DEFAULT_RECENCY_WEIGHT,
    half_life_days: float = DEFAULT_HALF_LIFE_DAYS,
    now: datetime | None = None,
) -> list[RankedResult]:
    if not 0.0 <= recency_weight <= 1.0:
        raise ValueError("recency_weight must be between 0 and 1")
    now = now or datetime.now(timezone.utc)

    # Retrieval scores (cosine similarity or BM25) aren't naturally in
    # [0, 1] -- normalize within this result set so the blend is meaningful.
    raw_scores = [r.score for r in results]
    lo, hi = (min(raw_scores), max(raw_scores)) if raw_scores else (0.0, 1.0)
    span = hi - lo or 1.0

    ranked = []
    for r in results:
        relevance = (r.score - lo) / span
        recency = _recency_score(r.published_at, half_life_days, now)
        combined = (1 - recency_weight) * relevance + recency_weight * recency
        ranked.append(
            RankedResult(result=r, relevance_score=relevance, recency_score=recency, combined_score=combined)
        )
    ranked.sort(key=lambda x: x.combined_score, reverse=True)
    return ranked
