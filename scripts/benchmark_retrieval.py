#!/usr/bin/env python
"""Phase 04: grader calibration benchmark (ROC-AUC, precision-recall).

Two corpora, deliberately of different difficulty:
- SHORT_DOCS: single-topic sentences (easy -- the correct match is the
  whole document).
- LONG_DOCS: multi-sentence paragraphs where the correct answer is one
  fact embedded among several unrelated sentences (hard -- closer to real
  usage, where a chunk covers more than the query asks about, diluting its
  embedding and lowering cosine similarity for genuinely correct matches).

An earlier version of this benchmark used only the easy corpus, scored a
perfect ROC-AUC/PR-AUC of 1.0, and set DEFAULT_CONFIDENCE_THRESHOLD=0.55
from that alone. That threshold then produced a real false negative in
manual testing: a chunk containing the literal answer was graded BAD
because its raw similarity (0.38) was well below what the easy-only
benchmark had implied "good" matches look like. This version benchmarks
both corpora together and picks a threshold via F1-maximization on the
combined precision-recall curve, so it isn't tuned to only the easy case.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

# Import order matters here: torch (pulled in by embedding_service via
# sentence-transformers) must load before scikit-learn, or their bundled
# native libraries conflict on Windows (WinError 1114, reproduced directly).
from embeddings.embedding_service import EmbeddingService
from retrieval.grader import grade_one

from sklearn.metrics import average_precision_score, precision_recall_curve, roc_auc_score

SHORT_DOCS = [
    "The Eiffel Tower is located in Paris, France and was completed in 1889.",
    "Photosynthesis is the process by which plants convert sunlight into chemical energy.",
    "The Great Barrier Reef is the world's largest coral reef system, located off Australia.",
    "Python is a high-level programming language known for its readable syntax.",
    "The mitochondria is the powerhouse of the cell, producing ATP through respiration.",
    "Qdrant is an open-source vector database used for similarity search.",
]
SHORT_QUERIES = [
    ("Where is the Eiffel Tower located?", 0),
    ("How do plants convert sunlight into energy?", 1),
    ("What is the largest coral reef system?", 2),
    ("Which programming language is known for readable syntax?", 3),
    ("What organelle produces ATP in a cell?", 4),
    ("What is a vector database used for similarity search?", 5),
]

LONG_DOCS = [
    "The Aurora Data Pipeline is a fault-tolerant, production-oriented streaming system. "
    "It ingests events from multiple message queues, validates their schema, and writes "
    "them to a columnar data warehouse. When an analyst runs a query, the pipeline "
    "retrieves matching partitions and returns aggregated results within seconds.",
    "Mount Kilimanjaro is the highest mountain in Africa, rising nearly 5,895 meters above "
    "sea level. It is a dormant volcano located in Tanzania near the border with Kenya. "
    "Climbers typically take five to nine days to reach the summit via one of several "
    "established routes.",
    "The human circulatory system consists of the heart, blood vessels, and blood. The "
    "heart pumps oxygenated blood through arteries to tissues throughout the body, while "
    "veins return deoxygenated blood back to the heart and lungs for reoxygenation.",
    "Kubernetes is an open-source container orchestration platform originally developed "
    "by Google. It automates the deployment, scaling, and management of containerized "
    "applications across clusters of machines, using a declarative configuration model.",
    # This exact pairing is the real case that failed in manual pipeline testing
    # (grader.confidence == 0.391 for the actually-correct chunk, threshold 0.55
    # rejected it). Included verbatim so the threshold is validated against a
    # confirmed real failure, not just synthetic approximations of "hard".
    "The Real-Time Corrective RAG Intelligence Platform is a fault-tolerant, "
    "production-oriented Retrieval-Augmented Generation system. It ingests documents, "
    "chunks them, embeds the chunks locally, and stores the vectors in Qdrant. When a "
    "user asks a question, the system retrieves the most relevant chunks and asks a "
    "local language model to answer using only that retrieved context, citing its sources.",
]
LONG_QUERIES = [
    ("What does the Aurora Data Pipeline write validated events to?", 0),
    ("How tall is Mount Kilimanjaro?", 1),
    ("What organ pumps oxygenated blood through arteries?", 2),
    ("Who originally developed Kubernetes?", 3),
    ("What does the system store in Qdrant?", 4),
]

ALL_DOCS = SHORT_DOCS + LONG_DOCS
ALL_QUERIES = SHORT_QUERIES + [(q, idx + len(SHORT_DOCS)) for q, idx in LONG_QUERIES]


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0


def _best_f1_threshold(labels: list[int], confidences: list[float]) -> tuple[float, float]:
    precision, recall, thresholds = precision_recall_curve(labels, confidences)
    best_f1, best_t = 0.0, 0.5
    for p, r, t in zip(precision, recall, thresholds):
        f1 = 2 * p * r / (p + r) if (p + r) else 0.0
        if f1 > best_f1:
            best_f1, best_t = f1, t
    return best_t, best_f1


def main() -> int:
    service = EmbeddingService()
    doc_vectors = service.embed_batch(ALL_DOCS)

    labels = []
    confidences = []
    similarities = []
    for query, correct_idx in ALL_QUERIES:
        qvec = service.embed(query)
        for i, (doc, dvec) in enumerate(zip(ALL_DOCS, doc_vectors)):
            similarity = _cosine(qvec, dvec)
            # Use a neutral threshold here (0.0) purely to compute confidence;
            # the actual GOOD/BAD decision threshold is evaluated separately below.
            graded = grade_one(query, chunk_id=f"doc{i}", content=doc, similarity_score=similarity, threshold=0.0)
            labels.append(1 if i == correct_idx else 0)
            confidences.append(graded.confidence)
            similarities.append(similarity)

    roc_auc = roc_auc_score(labels, confidences)
    pr_auc = average_precision_score(labels, confidences)
    best_threshold, best_f1 = _best_f1_threshold(labels, confidences)

    positive_confidences = [c for c, l in zip(confidences, labels) if l == 1]
    print(f"Pairs evaluated: {len(labels)} ({sum(labels)} positive, {len(labels) - sum(labels)} negative)")
    print(f"ROC-AUC: {roc_auc:.3f}")
    print(f"PR-AUC (average precision): {pr_auc:.3f}")
    print(f"Positive-pair confidence range: {min(positive_confidences):.3f} - {max(positive_confidences):.3f}")
    print(f"Best F1 threshold: {best_threshold:.3f} (F1={best_f1:.3f})")

    predictions_at_threshold = [1 if c >= best_threshold else 0 for c in confidences]
    tp = sum(1 for p, l in zip(predictions_at_threshold, labels) if p == 1 and l == 1)
    fp = sum(1 for p, l in zip(predictions_at_threshold, labels) if p == 1 and l == 0)
    fn = sum(1 for p, l in zip(predictions_at_threshold, labels) if p == 0 and l == 1)
    precision_at_threshold = tp / (tp + fp) if (tp + fp) else 0.0
    recall_at_threshold = tp / (tp + fn) if (tp + fn) else 0.0
    print(f"At best threshold: precision={precision_at_threshold:.3f}, recall={recall_at_threshold:.3f}, "
          f"TP={tp}, FP={fp}, FN={fn}")

    report_path = Path(__file__).resolve().parents[1] / "docs" / "experiments" / "phase04-grader-calibration.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Phase 04 Grader Calibration",
        "",
        "Real measurements (not simulated). Two corpora combined: 6 short single-topic "
        "sentences (easy) + 4 longer multi-sentence paragraphs where the correct answer is "
        "one fact embedded among several unrelated sentences (hard, closer to real chunk "
        "content). 10 queries x 10 documents = 100 (query, doc) pairs, one true positive per query.",
        "",
        "**Revision note:** an earlier version of this benchmark used only the easy corpus, "
        "scored a perfect ROC-AUC/PR-AUC of 1.0, and set the default threshold to 0.55 from "
        "that alone. That threshold produced a real false negative in manual pipeline testing "
        "-- a chunk containing the literal answer was graded BAD because its raw cosine "
        "similarity (0.38) was well below what the easy-only benchmark implied. This version "
        "benchmarks both corpora together and picks a threshold via F1-maximization instead "
        "of an assumed constant.",
        "",
        f"- Pairs evaluated: {len(labels)} ({sum(labels)} positive, {len(labels) - sum(labels)} negative)",
        f"- ROC-AUC: {roc_auc:.3f}",
        f"- PR-AUC (average precision): {pr_auc:.3f}",
        f"- Positive-pair confidence range: {min(positive_confidences):.3f} - {max(positive_confidences):.3f}",
        f"- Best F1 threshold: {best_threshold:.3f} (F1={best_f1:.3f})",
        f"- At best threshold: precision={precision_at_threshold:.3f}, recall={recall_at_threshold:.3f} "
        f"(TP={tp}, FP={fp}, FN={fn})",
        "",
        "## Decision",
        "",
        f"`DEFAULT_CONFIDENCE_THRESHOLD` updated to {best_threshold:.2f} in src/retrieval/grader.py, "
        "chosen by F1-maximization on this combined easy+hard set rather than an assumed value.",
        "",
        "## Notes",
        "",
        "Still a small (100-pair), hand-labeled set -- enough to catch gross miscalibration "
        "and validate the fix for the specific failure mode found, not a substitute for "
        "Phase 06's full evaluation framework on a larger held-out benchmark.",
    ]
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nReport written to {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
