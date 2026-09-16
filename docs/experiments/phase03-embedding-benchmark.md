# Phase 03 Embedding Model Benchmark

Real measurements on this machine (CPU), not simulated. Corpus: 6 short single-topic documents; 6 queries, each with one known-correct document (top-1 retrieval accuracy). See scripts/benchmark_embeddings.py for the exact corpus.

| Model | Dim | Load time (s) | Avg query latency (ms) | Accuracy@1 |
|---|---|---|---|---|
| all-MiniLM-L6-v2 | 384 | 6.007 | 21.41 | 6/6 (1.0) |
| all-MiniLM-L12-v2 | 384 | 22.771 | 15.27 | 6/6 (1.0) |
| paraphrase-MiniLM-L3-v2 | 384 | 23.266 | 30.25 | 6/6 (1.0) |

## Decision

Default remains `all-MiniLM-L6-v2` (see src/embeddings/embedding_service.py) unless a larger model shows a decisive accuracy improvement that justifies its added latency -- avoiding premature optimization on an unproven benefit.