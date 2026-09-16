# Phase 03 – Embeddings + Vector DB

## Objective
Establish a provider‑agnostic embedding pipeline and integrate a vector database to store chunk embeddings for retrieval.

## Concepts to Learn
- Open‑source embedding models (e.g., Sentence‑Transformers, Mistral‑Embedding)
- Vector similarity indexes (FAISS, Annoy, Chroma, Qdrant)
- Index persistence and sharding
- Metadata schema for temporal fields

## In‑Scope Work
- Benchmark candidate open‑source embedding models on a representative corpus.
- Select a default local embedding model and define a fallback.
- Implement an embedding service that accepts text chunks and returns dense vectors.
- Provision a vector store (e.g., Chroma) with the temporal metadata fields listed in the architecture.
- Populate the store with sample data from Phase 02.
- Define an interface contract (`embed(text: str) -> Vector`) used by downstream phases.

## Explicit Non‑Scope
- Training custom embeddings.
- Distributed or sharded vector stores beyond a single node.
- Real‑time streaming ingestion (Phase 10).
- Paid or proprietary APIs.

## Implementation Expectations
- Pure‑Python service with a clear API (`/embed`).
- Configurable model path via environment variable.
- Vector DB config abstracted behind a repository pattern.
- Unit tests for deterministic embeddings on a fixed seed.

## Tests / Evaluation
- Accuracy: cosine similarity on a held‑out set vs. baseline.
- Performance: latency < 50 ms per chunk on CPU.
- Persistence test: reload DB and verify vectors unchanged.

## Risks / Failure Cases
- Model loading failures on constrained hardware.
- Embedding drift when model updates.
- Vector DB incompatibilities with future metadata fields.

## Expected Artifacts
- `embedding_service.py` implementing the service.
- `vector_store.py` abstraction.
- Benchmark report (markdown).
- Updated `docs/architecture.md` section.

## Definition of Done
- Embedding service passes all unit tests.
- Vector DB stores and retrieves embeddings with correct metadata.
- Phase 03 documentation approved and linked from the roadmap.

## Dependencies on Previous Phases
- Relies on document chunk schema from Phase 02.
- Uses configuration utilities defined in Phase 00.
