# Roadmap

This roadmap outlines the sequential phases for building the Real-Time Corrective RAG Intelligence Platform. Each phase builds on the previous one, adding incremental capabilities while maintaining a provider‑agnostic, free‑LLM‑first approach.

| Phase | Title | Objective |
|-------|-------|-----------|
| 00 | Foundation | Scaffold repository, define architecture, create planning artifacts. |
| 01 | RAG Baseline | Implement basic Retrieval‑Augmented Generation pipeline. |
| 02 | Document Processing | Add robust loaders, chunking, and preprocessing. |
| 03 | Embeddings & Vector DB | Integrate embedding model and vector store. |
| 04 | Retrieval Engineering | Optimize similarity search, ranking, and grading. |
| 05 | Generation | Connect LLM, prompt engineering, citation injection. |
| 06 | Evaluation | Establish evaluation metrics, test suites, and benchmarking. |
| 07 | Corrective RAG | Implement CRAG loop for query rewriting and answer correction. |
| 08 | LangGraph | Introduce LangGraph orchestration for stateful workflows. |
| 09 | Query Rewriting | Add advanced rewrite strategies and context augmentation. |
| 10 | Real‑time Ingestion | Stream new documents, incremental indexing. |
| 11 | Kafka Integration | Event‑driven pipeline with Kafka for scalability. |
| 12 | Time‑aware Retrieval | Temporal relevance and decay handling. |
| 13 | API | Expose REST/GRPC API for external access. |
| 14 | Frontend | Basic UI for querying and result visualization. |
| 15 | Production | Hardened, monitored, cost‑optimized deployment. |

Each phase has its own detailed implementation plan under `plans/phase-XX-*.md`.
