"""Phase 07: Corrective RAG loop.

retrieve -> grade -> if BAD, rewrite the query and retry (bounded) ->
abstain if still inadequate after max_retries. Bounded retries are
enforced unconditionally via the loop structure (a fixed range of
max_retries + 1 attempts) -- this must never loop indefinitely.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Protocol

from generation.pipeline import GroundedAnswer, generate_grounded_answer
from retrieval.grader import Grade, grade_results
from retrieval.retriever import RetrievalResult

from .rewriter import RewriteError, rewrite_query

DEFAULT_MAX_RETRIES = 2


class SupportsRetrieve(Protocol):
    def retrieve(self, query: str, top_k: int = 5) -> list[RetrievalResult]: ...


@dataclass(frozen=True)
class CRAGResult:
    answer: GroundedAnswer
    original_query: str
    final_query: str
    rewrite_count: int
    recovered_by_rewrite: bool  # first attempt was BAD, a later one succeeded
    abstained: bool
    total_latency_ms: float


def run_crag(
    query: str,
    retriever: SupportsRetrieve,
    top_k: int = 5,
    max_retries: int = DEFAULT_MAX_RETRIES,
    provider=None,
    provider_name: str | None = None,
) -> CRAGResult:
    if max_retries < 0:
        raise ValueError("max_retries must be >= 0")

    start = time.perf_counter()
    current_query = query
    rewrite_count = 0
    first_attempt_good: bool | None = None

    for attempt in range(max_retries + 1):
        results = retriever.retrieve(current_query, top_k=top_k)
        graded = grade_results(current_query, results)
        has_good = any(g.grade == Grade.GOOD for g in graded)

        if first_attempt_good is None:
            first_attempt_good = has_good

        if has_good or attempt == max_retries:
            answer = generate_grounded_answer(current_query, graded, provider=provider, provider_name=provider_name)
            return CRAGResult(
                answer=answer,
                original_query=query,
                final_query=current_query,
                rewrite_count=rewrite_count,
                recovered_by_rewrite=(not first_attempt_good) and has_good,
                abstained=answer.used_chunk_count == 0,
                total_latency_ms=(time.perf_counter() - start) * 1000,
            )

        try:
            current_query = rewrite_query(current_query, provider=provider, provider_name=provider_name)
        except RewriteError:
            # Can't rewrite (provider unavailable/failed): stop retrying and
            # abstain with what we have, rather than loop or crash.
            answer = generate_grounded_answer(current_query, graded, provider=provider, provider_name=provider_name)
            return CRAGResult(
                answer=answer,
                original_query=query,
                final_query=current_query,
                rewrite_count=rewrite_count,
                recovered_by_rewrite=False,
                abstained=True,
                total_latency_ms=(time.perf_counter() - start) * 1000,
            )
        rewrite_count += 1

    raise RuntimeError("CRAG loop exited without returning a result")  # unreachable
