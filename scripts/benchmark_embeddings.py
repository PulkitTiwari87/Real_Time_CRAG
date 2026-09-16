#!/usr/bin/env python
"""Phase 03: benchmark candidate local embedding models.

Real measurement, not fabricated numbers: for each candidate model, loads
it, times per-text embedding latency, and measures top-1 retrieval
accuracy on a small hand-labeled (query -> correct document) set. Writes a
markdown report to docs/experiments/.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from embeddings.embedding_service import EmbeddingService

CANDIDATE_MODELS = ["all-MiniLM-L6-v2", "all-MiniLM-L12-v2", "paraphrase-MiniLM-L3-v2"]

DOCUMENTS = [
    "The Eiffel Tower is located in Paris, France and was completed in 1889.",
    "Photosynthesis is the process by which plants convert sunlight into chemical energy.",
    "The Great Barrier Reef is the world's largest coral reef system, located off Australia.",
    "Python is a high-level programming language known for its readable syntax.",
    "The mitochondria is the powerhouse of the cell, producing ATP through respiration.",
    "Qdrant is an open-source vector database used for similarity search.",
]

QUERIES = [
    ("Where is the Eiffel Tower located?", 0),
    ("How do plants convert sunlight into energy?", 1),
    ("What is the largest coral reef system?", 2),
    ("Which programming language is known for readable syntax?", 3),
    ("What organelle produces ATP in a cell?", 4),
    ("What is a vector database used for similarity search?", 5),
]


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0


def benchmark_model(model_name: str) -> dict:
    load_start = time.perf_counter()
    service = EmbeddingService(model_name)
    load_time_s = time.perf_counter() - load_start

    doc_vectors = service.embed_batch(DOCUMENTS)

    latencies = []
    correct = 0
    for query, expected_idx in QUERIES:
        start = time.perf_counter()
        qvec = service.embed(query)
        latencies.append((time.perf_counter() - start) * 1000)

        scores = [_cosine(qvec, dv) for dv in doc_vectors]
        predicted_idx = max(range(len(scores)), key=lambda i: scores[i])
        if predicted_idx == expected_idx:
            correct += 1

    return {
        "model": model_name,
        "dimension": service.dimension,
        "load_time_s": round(load_time_s, 3),
        "avg_query_latency_ms": round(sum(latencies) / len(latencies), 2),
        "accuracy_at_1": round(correct / len(QUERIES), 3),
        "correct": correct,
        "total": len(QUERIES),
    }


def main() -> int:
    results = []
    for model_name in CANDIDATE_MODELS:
        print(f"Benchmarking {model_name}...")
        try:
            results.append(benchmark_model(model_name))
        except Exception as exc:
            print(f"  FAILED: {exc}", file=sys.stderr)
            results.append({"model": model_name, "error": str(exc)})

    print("\n=== Results ===")
    for r in results:
        print(r)

    report_path = Path(__file__).resolve().parents[1] / "docs" / "experiments" / "phase03-embedding-benchmark.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Phase 03 Embedding Model Benchmark",
        "",
        "Real measurements on this machine (CPU), not simulated. Corpus: 6 short "
        "single-topic documents; 6 queries, each with one known-correct document "
        "(top-1 retrieval accuracy). See scripts/benchmark_embeddings.py for the exact corpus.",
        "",
        "| Model | Dim | Load time (s) | Avg query latency (ms) | Accuracy@1 |",
        "|---|---|---|---|---|",
    ]
    for r in results:
        if "error" in r:
            lines.append(f"| {r['model']} | - | - | - | FAILED: {r['error']} |")
        else:
            lines.append(
                f"| {r['model']} | {r['dimension']} | {r['load_time_s']} | "
                f"{r['avg_query_latency_ms']} | {r['correct']}/{r['total']} ({r['accuracy_at_1']}) |"
            )
    lines += [
        "",
        "## Decision",
        "",
        "Default remains `all-MiniLM-L6-v2` (see src/embeddings/embedding_service.py) "
        "unless a larger model shows a decisive accuracy improvement that justifies its "
        "added latency -- avoiding premature optimization on an unproven benefit.",
    ]
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nReport written to {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
