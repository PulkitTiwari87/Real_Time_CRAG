# Phase 01 – RAG Baseline

## Objective
Implement a minimal Retrieval‑Augmented Generation (RAG) pipeline to retrieve relevant documents and generate answers.

## Why it exists
Provide a working baseline that demonstrates end‑to‑end flow before adding corrective logic.

## Prerequisites
- Phase 00 completed.
- Documentation and planning artifacts in place.

## Concepts to learn
- Document loading, chunking, embedding, vector store basics.
- Prompt engineering for LLM answer generation.

## In‑scope work
- Implement document loaders for plain text.
- Create a simple chunking strategy (fixed size).
- Use a free embedding model (e.g., `all-MiniLM-L6-v2`).
- Store embeddings in Qdrant (local Docker).
- Basic retrieval of top‑k chunks.
- Pass retrieved chunks to LLM (free‑tier model) and return answer.

## Explicit non‑scope
- No grading or corrective loop.
- No advanced ranking or reranking.
- No streaming or real‑time ingestion.

## Expected files
- `src/rag_baseline/loader.py`
- `src/rag_baseline/chunker.py`
- `src/rag_baseline/retriever.py`
- `src/rag_baseline/generator.py`
- Unit tests under `tests/rag_baseline/`.

## Implementation tasks
1. Set up package `src/rag_baseline` with `__init__.py`.
2. Implement loader, chunker, retriever, generator modules.
3. Add a simple CLI script in `scripts/run_rag_baseline.py`.
4. Write unit tests for each component.
5. Update `requirements.txt` with needed libraries (e.g., `sentence-transformers`, `qdrant-client`, `openai` or `requests`).

## Tests
- Verify that a sample document can be loaded, chunked, embedded, stored, retrieved, and answered.

## Evaluation / Metrics
- Retrieval: Recall@5, Precision@5, MRR, NDCG.
- Generation: Faithfulness, Answer relevance, Citation correctness.
- System: End‑to‑end latency, token usage per query, cost per query.

## Risks / Failure cases
- Exceeding free‑tier token limits.
- Vector store connectivity issues.
- Inconsistent chunk sizes leading to poor retrieval.

## Acceptance criteria
- All modules compile and pass unit tests.
- End‑to‑end demo script returns an answer with citations.
- Metrics collection hooks are stubbed.

## Definition of Done
- Code implemented, tested, documented.
- No planning files modified.
- All new files listed in Git status as untracked.

## Handoff requirements
- Claude Code may start Phase 02 after confirming Phase 01 passes all acceptance criteria.
