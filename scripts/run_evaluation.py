#!/usr/bin/env python
"""Phase 06: end-to-end evaluation benchmark.

Runs the Phase 05 pipeline (index -> retrieve -> grade -> generate) over
docs/evaluation/benchmark_dataset.json, computes retrieval and generation
metrics for each query, and writes a markdown report. Real measurements
against the live-configured LLM provider, not simulated.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

# Import order: torch (via embeddings) before anything that might pull in
# scikit-learn indirectly -- see scripts/benchmark_retrieval.py for the
# reproduced Windows DLL conflict this avoids.
from embeddings import EmbeddingService, VectorStore
from evaluation.metrics import bleu, citation_accuracy, faithfulness, mrr, ndcg_at_k, precision_at_k, recall_at_k, rouge_l
from generation import GenerationError, generate_grounded_answer
from retrieval import Retriever, grade_results


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Run the Phase 06 evaluation benchmark.")
    parser.add_argument("--dataset", default="docs/evaluation/benchmark_dataset.json")
    parser.add_argument("--report", default="docs/evaluation/phase06-baseline-report.md")
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--provider", default=None)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    dataset = json.loads((repo_root / args.dataset).read_text(encoding="utf-8"))

    embedder = EmbeddingService()
    store = VectorStore(collection_name="phase06_eval", vector_size=embedder.dimension)
    retriever = Retriever(vector_store=store, embedder=embedder)

    try:
        for doc in dataset["documents"]:
            store.upsert(
                chunk_id=doc["id"],
                document_id=doc["id"],
                source=doc["id"],
                content=doc["content"],
                vector=embedder.embed(doc["content"]),
            )

        rows = []
        for item in dataset["queries"]:
            query = item["query"]
            relevant_ids = set(item["relevant_doc_ids"])
            reference_answer = item["reference_answer"]

            results = retriever.retrieve(query, top_k=args.top_k)
            retrieved_ids = [r.chunk_id for r in results]

            retrieval_scores = {
                "recall_at_k": recall_at_k(retrieved_ids, relevant_ids, args.top_k),
                "precision_at_k": precision_at_k(retrieved_ids, relevant_ids, args.top_k),
                "mrr": mrr(retrieved_ids, relevant_ids),
                "ndcg_at_k": ndcg_at_k(retrieved_ids, relevant_ids, args.top_k),
            }

            graded = grade_results(query, results)
            try:
                answer = generate_grounded_answer(query, graded, provider_name=args.provider)
                error = None
            except GenerationError as exc:
                answer = None
                error = str(exc)

            if answer is not None and answer.used_chunk_count > 0:
                context_text = " ".join(g.content for g in graded if g.grade.value == "GOOD")
                generation_scores = {
                    "bleu": bleu(answer.answer, reference_answer),
                    "rouge_l": rouge_l(answer.answer, reference_answer),
                    "faithfulness": faithfulness(answer.answer, context_text),
                    "citation_accuracy": citation_accuracy(
                        [c.document_id for c in answer.citations], relevant_ids
                    ),
                }
            else:
                generation_scores = {"bleu": 0.0, "rouge_l": 0.0, "faithfulness": 0.0, "citation_accuracy": 0.0}

            rows.append(
                {
                    "query": query,
                    "retrieval": retrieval_scores,
                    "generation": generation_scores,
                    "answer": answer.answer if answer else None,
                    "error": error,
                }
            )
    finally:
        store.close()

    def _avg(key_path: tuple[str, str]) -> float:
        section, metric = key_path
        values = [r[section][metric] for r in rows]
        return sum(values) / len(values) if values else 0.0

    metric_keys = [
        ("retrieval", "recall_at_k"),
        ("retrieval", "precision_at_k"),
        ("retrieval", "mrr"),
        ("retrieval", "ndcg_at_k"),
        ("generation", "bleu"),
        ("generation", "rouge_l"),
        ("generation", "faithfulness"),
        ("generation", "citation_accuracy"),
    ]
    averages = {f"{s}.{m}": _avg((s, m)) for s, m in metric_keys}

    print("=== Aggregate metrics ===")
    for k, v in averages.items():
        print(f"{k}: {v:.3f}")

    report_path = repo_root / args.report
    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Phase 06 Baseline Evaluation Report",
        "",
        f"Real end-to-end run of the Phase 05 pipeline over {len(dataset['queries'])} queries "
        f"against {len(dataset['documents'])} documents (docs/evaluation/benchmark_dataset.json), top_k={args.top_k}.",
        "",
        "## Aggregate Metrics",
        "",
        "| Metric | Value |",
        "|---|---|",
    ]
    for k, v in averages.items():
        lines.append(f"| {k} | {v:.3f} |")

    lines += ["", "## Per-Query Results", ""]
    for r in rows:
        lines.append(f"### {r['query']}")
        if r["error"]:
            lines.append(f"- **Generation error:** {r['error']}")
        else:
            lines.append(f"- **Answer:** {r['answer']}")
        lines.append(
            f"- Retrieval: recall@k={r['retrieval']['recall_at_k']:.2f}, "
            f"precision@k={r['retrieval']['precision_at_k']:.2f}, "
            f"mrr={r['retrieval']['mrr']:.2f}, ndcg@k={r['retrieval']['ndcg_at_k']:.2f}"
        )
        lines.append(
            f"- Generation: bleu={r['generation']['bleu']:.2f}, rouge_l={r['generation']['rouge_l']:.2f}, "
            f"faithfulness={r['generation']['faithfulness']:.2f}, "
            f"citation_accuracy={r['generation']['citation_accuracy']:.2f}"
        )
        lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nReport written to {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
