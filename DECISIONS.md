# Architecture Decision Records (ADRs)

This document tracks key architectural decisions. Each ADR follows the template:

## ADR-001: Project Architecture
- **Status:** PROPOSED
- **Context:** Selecting a provider‑agnostic, free‑LLM‑first architecture.
- **Decision:** Use a modular RAG pipeline with interchangeable embedding and vector store components.
- **Alternatives:** Fixed‑provider stack, monolithic design.
- **Consequences:** Enables later swapping of free models; adds integration overhead.

## ADR-002: Vector Store Provider
- **Status:** PROPOSED
- **Context:** Need an open‑source, free‑tier vector store.
- **Decision:** Use Qdrant (self‑hosted) with optional Docker deployment.
- **Alternatives:** Pinecone (paid), FAISS (local file‑based).
- **Consequences:** Self‑hosting adds ops cost but stays free.

## ADR-003: Embedding Model
- **Status:** PROPOSED
- **Context:** Require free embeddings.
- **Decision:** Use OpenAI's `text-embedding-3-small` (free tier) or HuggingFace `sentence-transformers/all-MiniLM-L6-v2`.
- **Alternatives:** Proprietary models, larger transformer models.
- **Consequences:** Limits token usage; easy to replace.

## ADR-004: Retrieval Strategy
- **Status:** PROPOSED
- **Context:** Need efficient top‑K similarity search.
- **Decision:** Use cosine similarity with approximate nearest neighbor (ANN) via Qdrant.
- **Alternatives:** Exact search, BM25.
- **Consequences:** Faster at scale, slight recall trade‑off.

## ADR-005: Grading Model
- **Status:** PROPOSED
- **Context:** Need to assess relevance of retrieved chunks.
- **Decision:** Use a lightweight classification model (e.g., `google/flan-t5-small`) on free tier.
- **Alternatives:** Larger LLM, rule‑based heuristics.
- **Consequences:** Balances accuracy and cost.

## ADR-006: CRAG Loop Design
- **Status:** PROPOSED
- **Context:** Implement corrective feedback loop.
- **Decision:** Introduce a two‑step loop: retrieve → grade → if low confidence, rewrite query and retrieve again.
- **Alternatives:** Single‑pass retrieval, multi‑round iterative.
- **Consequences:** Improves answer correctness at modest latency.

## ADR-007: Observability Stack
- **Status:** PROPOSED
- **Context:** Need monitoring without paid services.
- **Decision:** Use OpenTelemetry with Prometheus + Grafana (self‑hosted).
- **Alternatives:** Datadog, CloudWatch (paid).
- **Consequences:** Requires self‑hosting but remains free.

## ADR-008: Token Budget Monitoring
- **Status:** PROPOSED
- **Context:** Must stay within free LLM token limits.
- **Decision:** Implement a token accounting middleware tracking input, output, embedding, and context tokens.
- **Alternatives:** Manual monitoring, external billing APIs.
- **Consequences:** Enables automated throttling.

## ADR-009: Evaluation Framework
- **Status:** PROPOSED
- **Context:** Need comprehensive metrics for RAG and CRAG.
- **Decision:** Define retrieval (Recall@K, Precision@K, MRR, NDCG), generation (Faithfulness, Answer relevance, Citation correctness, Context relevance), and system (latency, token usage, cost, retry rate).
- **Alternatives:** Ad‑hoc testing, proprietary evaluation services.
- **Consequences:** Standardized, reproducible evaluation.

## ADR-010: Deployment Strategy
- **Status:** PROPOSED
- **Context:** Deploy on free‑tier cloud resources.
- **Decision:** Use Docker Compose for local dev and Fly.io free tier for remote deployment.
- **Alternatives:** Kubernetes (complex), Heroku (paid).
- **Consequences:** Simple, low‑cost, but limited scaling.

*(Add further ADRs as the project evolves.)

This document tracks key architectural decisions. Each ADR follows the template:

## ADR-001: Project Architecture
- **Status:** PROPOSED
- **Context:** ...
- **Decision:** ...
- **Alternatives:** ...
- **Consequences:** ...

*(Add further ADRs as the project evolves.)
