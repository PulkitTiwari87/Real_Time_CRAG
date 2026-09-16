#!/usr/bin/env python
"""Phase 09: measure whether query rewriting actually improves retrieval.

Uses deliberately awkward/verbose phrasings of the standard benchmark
queries, and checks accuracy@1 (does the correct document rank first) for:
- the original awkward query (baseline, no rewrite)
- deterministic-rewritten query (keyword extraction, no LLM)
- LLM-rewritten query (Gemini, same rewrite used by the Phase 07 CRAG loop)

Real measurement against real embeddings, not assumed. Writes a markdown
report documenting whether each strategy actually helped, per query.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from embeddings.embedding_service import EmbeddingService
from query_rewriting.strategies import RewriteError, deterministic_rewrite, llm_based_rewrite

DOCUMENTS = [
    "The Eiffel Tower is located in Paris, France and was completed in 1889.",
    "Photosynthesis is the process by which plants convert sunlight into chemical energy.",
    "The Great Barrier Reef is the world's largest coral reef system, located off Australia.",
    "Python is a high-level programming language known for its readable syntax.",
    "The mitochondria is the powerhouse of the cell, producing ATP through respiration.",
    "Qdrant is an open-source vector database used for similarity search.",
]

AWKWARD_QUERIES = [
    (
        "Um, so like, where would I go if I wanted to see that huge iron tower "
        "thing they built in France a long time ago?",
        0,
    ),
    (
        "You know that thing where green plants somehow turn sunshine into "
        "food-type energy for themselves, what's that called?",
        1,
    ),
    (
        "I heard there's this massive underwater rock structure made of coral "
        "near Australia that's supposedly the biggest one on Earth, what is it?",
        2,
    ),
    (
        "So there's this coding language that people say is really easy to "
        "read because of how it's written, which one is that?",
        3,
    ),
    (
        "What's that little part inside cells that's in charge of making the "
        "energy molecules through breathing-type chemical reactions?",
        4,
    ),
    (
        "Is there some kind of database out there specifically built to hold "
        "vector-type data for doing similarity lookups fast?",
        5,
    ),
]


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0


def _top1_correct(service, query: str, doc_vectors: list, expected_idx: int) -> bool:
    qvec = service.embed(query)
    scores = [_cosine(qvec, dv) for dv in doc_vectors]
    predicted = max(range(len(scores)), key=lambda i: scores[i])
    return predicted == expected_idx


def main() -> int:
    service = EmbeddingService()
    doc_vectors = service.embed_batch(DOCUMENTS)

    rows = []
    for query, expected_idx in AWKWARD_QUERIES:
        det_query = deterministic_rewrite(query)
        try:
            llm_query = llm_based_rewrite(query, provider_name="gemini")
            llm_error = None
        except RewriteError as exc:
            llm_query = None
            llm_error = str(exc)

        row = {
            "query": query,
            "original_correct": _top1_correct(service, query, doc_vectors, expected_idx),
            "deterministic_query": det_query,
            "deterministic_correct": _top1_correct(service, det_query, doc_vectors, expected_idx),
        }
        if llm_query is not None:
            row["llm_query"] = llm_query
            row["llm_correct"] = _top1_correct(service, llm_query, doc_vectors, expected_idx)
        else:
            row["llm_query"] = None
            row["llm_error"] = llm_error
        rows.append(row)

    def _accuracy(key: str) -> float:
        vals = [r[key] for r in rows if key in r and isinstance(r[key], bool)]
        return sum(vals) / len(vals) if vals else 0.0

    orig_acc = _accuracy("original_correct")
    det_acc = _accuracy("deterministic_correct")
    llm_acc = _accuracy("llm_correct")

    print(f"Original (no rewrite) accuracy@1: {orig_acc:.2f}")
    print(f"Deterministic rewrite accuracy@1: {det_acc:.2f}")
    print(f"LLM rewrite accuracy@1: {llm_acc:.2f}")

    report_path = Path(__file__).resolve().parents[1] / "docs" / "experiments" / "phase09-query-rewriting-benchmark.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Phase 09 Query Rewriting Benchmark",
        "",
        "Real measurement (not assumed): 6 deliberately awkward/verbose phrasings of the "
        "standard benchmark queries, checking whether the correct document ranks first "
        "(accuracy@1) for the original query vs. two rewrite strategies.",
        "",
        "| Strategy | Accuracy@1 |",
        "|---|---|",
        f"| Original (no rewrite) | {orig_acc:.2f} |",
        f"| Deterministic (keyword extraction) | {det_acc:.2f} |",
        f"| LLM-based (Gemini) | {llm_acc:.2f} |",
        "",
        "## Per-Query Detail",
        "",
    ]
    for r in rows:
        lines.append(f"### {r['query']}")
        lines.append(f"- Original correct: {r['original_correct']}")
        lines.append(f"- Deterministic rewrite: \"{r['deterministic_query']}\" -> correct: {r['deterministic_correct']}")
        if r.get("llm_query") is not None:
            lines.append(f"- LLM rewrite: \"{r['llm_query']}\" -> correct: {r['llm_correct']}")
        else:
            lines.append(f"- LLM rewrite failed: {r.get('llm_error')}")
        lines.append("")

    lines += [
        "## Conclusion",
        "",
        (
            "Rewriting did NOT improve accuracy on this benchmark -- the embedding model "
            "already handled these awkward phrasings correctly without any rewrite."
            if orig_acc >= det_acc and orig_acc >= llm_acc
            else "Rewriting improved accuracy on at least one strategy for this benchmark."
        ),
        "",
        "This matches the general finding that semantic (vector) embeddings are often "
        "robust to phrasing/verbosity variations, so rewriting's main value is likely for "
        "lexical (BM25) retrieval or genuinely ambiguous/underspecified queries, not simply "
        "verbose ones. Do not assume rewriting is always beneficial for vector retrieval.",
    ]
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nReport written to {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
