"""Simple LLM-based query rewriting for the CRAG loop.

Deliberately minimal: Phase 09 (Query Rewriting) is where rewrite
strategies get compared/optimized (deterministic vs. LLM-based). This
just needs *a* working rewrite so the corrective loop in crag.py has
something to retry with.
"""
from __future__ import annotations

from rag_baseline.llm_providers import LLMConfigError, LLMProvider, LLMProviderError, get_provider

REWRITE_PROMPT = """The following search query did not retrieve relevant results:

Query: {query}

Rewrite it as a clearer, more specific, or differently-phrased search query \
that might retrieve better results. Return ONLY the rewritten query, nothing else.

Rewritten query:"""


class RewriteError(RuntimeError):
    """Raised when the query cannot be rewritten (provider unavailable/failed)."""


def rewrite_query(
    query: str,
    provider: LLMProvider | None = None,
    provider_name: str | None = None,
) -> str:
    try:
        llm = provider or get_provider(provider_name)
    except LLMConfigError as exc:
        raise RewriteError(str(exc)) from exc
    try:
        rewritten = llm.generate(REWRITE_PROMPT.format(query=query))
    except LLMProviderError as exc:
        raise RewriteError(str(exc)) from exc
    rewritten = rewritten.strip().strip('"').strip("'")
    return rewritten or query
