# Phase 04 – Retrieval Engineering

## Objective
Design and implement robust retrieval strategies, ranking, and grading to maximize relevance and support the CRAG correction loop.

## Concepts to Learn
- Approximate nearest‑neighbor (ANN) search trade‑offs
- Hybrid retrieval (vector + BM25)
- Relevance grading models and confidence calibration
- Multi‑stage reranking pipelines

## In‑Scope Work
- Implement a configurable retriever that can query the vector store with optional metadata filters.
- Add optional BM25 fallback using pre‑computed inverted index.
- Develop a lightweight grader (binary classifier) that scores retrieved chunks and produces a confidence threshold.
- Expose a retrieval API (`/retrieve`) returning ranked chunks with scores.
- Integrate the grader into the CRAG loop decision point.

## Explicit Non‑Scope
- Training custom ranking models.
- Distributed retrieval across many shards.
- Real‑time incremental indexing (Phase 10).
- Paid retrieval services.

## Implementation Expectations
- Pure‑Python modules with clear interfaces (`Retriever`, `Grader`).
- Configurable parameters via environment or a YAML config file.
- Unit tests covering deterministic ranking on a fixed corpus.
- Documentation of ranking metrics and thresholds.

## Tests / Evaluation
- Retrieval quality: Recall@K, MRR, and NDCG on a held‑out benchmark.
- Grader calibration: ROC‑AUC and precision‑recall at chosen confidence cut‑off.
- Latency: < 100 ms for top‑10 retrieval on CPU.

## Risks / Failure Cases
- Over‑filtering leading to empty result sets.
- Grader mis‑calibration causing excessive rewrites.
- Vector store query incompatibilities with metadata filters.

## Expected Artifacts
- `retriever.py` implementing vector + optional BM25 search.
- `grader.py` with confidence scoring.
- Configuration schema `retrieval_config.yaml`.
- Benchmark report (Markdown).
- Updated `docs/architecture.md` section.

## Definition of Done
- Retrieval service passes all unit tests.
- Grader confidence thresholds are documented and validated.
- Phase 04 documentation reviewed and linked from the roadmap.

## Dependencies on Previous Phases
- Relies on embedding service and vector store from Phase 03.
- Uses document chunk schema defined in Phase 02.
