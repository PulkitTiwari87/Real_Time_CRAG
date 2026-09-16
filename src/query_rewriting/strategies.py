"""Phase 09: query rewriting strategies -- deterministic and LLM-based.

Phase 07 only needed *a* working rewrite to complete the CRAG loop
(LLM-based, in corrective.rewriter). This phase adds a second, non-LLM
strategy and (see scripts/benchmark_query_rewriting.py) measures whether
either one actually helps retrieval, rather than assuming rewriting is
beneficial by default.
"""
from __future__ import annotations

import re

from corrective.rewriter import RewriteError, rewrite_query as _llm_rewrite

_STOPWORDS = {
    "what", "who", "where", "when", "why", "how", "is", "are", "does", "do",
    "did", "the", "a", "an", "of", "to", "in", "on", "for", "and", "or",
    "this", "that", "these", "those", "was", "were", "be", "been",
}


def deterministic_rewrite(query: str) -> str:
    """Strip question words/stopwords and punctuation, keeping content
    terms only. A simple keyword-extraction rewrite with no LLM call --
    expected to help lexical (BM25) retrieval more than semantic (vector)
    retrieval, which is exactly what the benchmark checks rather than
    assumes."""
    cleaned = re.sub(r"[^\w\s]", "", query.lower())
    terms = [t for t in cleaned.split() if t not in _STOPWORDS]
    return " ".join(terms) if terms else query


def llm_based_rewrite(query: str, provider=None, provider_name: str | None = None) -> str:
    return _llm_rewrite(query, provider=provider, provider_name=provider_name)


STRATEGIES = {
    "deterministic": deterministic_rewrite,
    "llm": llm_based_rewrite,
}

__all__ = ["deterministic_rewrite", "llm_based_rewrite", "STRATEGIES", "RewriteError"]
