# Real-Time Corrective RAG Intelligence Platform

## Project Objective
Build a production‑oriented Corrective Retrieval‑Augmented Generation (CRAG) system capable of ingesting, processing, chunking, embedding, retrieving, grading, query rewriting, and generating grounded answers with source attribution.

## Problem Statement
Current Retrieval‑Augmented Generation pipelines struggle with hallucinations, outdated information, and latency in real‑time contexts. A CRAG system that can detect and correct retrieval errors on‑the‑fly is required for high‑risk domains.

## Target Use Cases
- **Enterprise Knowledge Bases** – accurate, up‑to‑date answers for internal support.
- **Regulatory Compliance** – provide verifiable citations for legal queries.
- **Customer‑Facing Chatbots** – real‑time, trustworthy responses.

## Goals
- End‑to‑end CRAG pipeline with modular phases.
- Comprehensive evaluation framework (retrieval, generation, system metrics).
- Observability and token‑budget monitoring.
- Clear handoff to Claude Code for implementation phases.

## Non‑Goals
- Full UI/UX development (frontend is out of scope for bootstrap).
- Training new embedding models (use existing models).
- Deploying production infrastructure (only scaffolding and design).

## Architecture Summary
The system consists of:
1. **Ingestion & Chunking** – document loaders, text pre‑processing, chunk generation.
2. **Embedding Layer** – external embedding model (e.g., OpenAI, HuggingFace).
3. **Vector Store** – configurable (e.g., Pinecone, Qdrant).
4. **Retriever & Grader** – similarity search + relevance grading.
5. **Corrective Engine** – CRAG logic for query rewriting and answer correction.
6. **Generation Layer** – LLM with prompt templates, citation injection.
7. **Observability** – logging, metrics, token accounting.

## Current Phase & Milestone
- **Current phase:** Phase 00 — Foundation
- **Status:** PLANNED — NOT YET IMPLEMENTED
- **Phase 00 is planned and ready for architecture review.**

## Completed Work
- Directory structure created.
- Initial README, PROJECT, DECISIONS, CHANGELOG, .gitignore, .env.example, requirements.txt.
- Preliminary implementation_plan (now removed).

## Active Work
- Expanding documentation per master bootstrap requirements.
- Populating ADRs, evaluation, token strategy, experiment frameworks.
- Creating detailed phase implementation plans.

## Next Action
Review the repository structure and documentation. Once architecture review is complete, Claude Code may begin Phase 00 implementation.

## Known Issues
- ADR templates not yet defined (pending user clarification).

## Open Questions
- Preferred ADR format?
- Inclusion of CI badges in README?
- Additional top‑level directories (e.g., `examples/`)?

## Project Risks
- Scope creep: adding implementation code prematurely.
- Incomplete ADR decisions may lead to architectural ambiguity.
- Token‑budget oversights could impact cost estimation.

## Architecture Decisions (ADRs)
- ADR‑001 – Language & Framework Selection (PROPOSED)
- ADR‑002 – Vector Store Provider (PROPOSED)
- ADR‑003 – Embedding Model (PROPOSED)
- ADR‑004 – Retrieval Strategy (PROPOSED)
- ADR‑005 – Grading Model (PROPOSED)
- ADR‑006 – CRAG Loop Design (PROPOSED)
- ADR‑007 – Observability Stack (PROPOSED)
- ADR‑008 – Token Budget Monitoring (PROPOSED)
- ADR‑009 – Evaluation Framework (PROPOSED)
- ADR‑010 – Deployment Strategy (PROPOSED)

## Retrieval Metrics
- Recall@K, Precision@K, MRR, NDCG.

## Generation Metrics
- Faithfulness, Answer relevance, Citation correctness, Context relevance.

## System Metrics
- End‑to‑end latency, Token usage per query, Cost per query, Retry rate.

## Token Budget
- Input tokens ≤ 4,000 per request; Output tokens ≤ 1,000; Embedding tokens ≤ 2,000.

## Context‑Window Strategy
- Truncate and summarize long documents; use hierarchical chunking; prioritize recent data.

## Evaluation Status
- Evaluation plan drafted (see `docs/evaluation/`).

## Definition of Done (DoD)
- All documentation files created and populated.
- Directory structure validated.
- No implementation code present.
- Acceptance criteria for each phase documented.
- Ready for Claude Code to begin Phase 00 implementation.




## Goals
- End‑to‑end CRAG pipeline with modular phases.
- Comprehensive evaluation framework (retrieval, generation, system metrics).
- Observability and token‑budget monitoring.
- Clear handoff to Claude Code for implementation phases.

## Non‑Goals
- Full UI/UX development (frontend is out of scope for bootstrap).
- Training new embedding models (use existing models).
- Deploying production infrastructure (only scaffolding and design).

## Architecture Summary
The system consists of:
1. **Ingestion & Chunking** – document loaders, text pre‑processing, chunk generation.
2. **Embedding Layer** – external embedding model (e.g., OpenAI, HuggingFace).
3. **Vector Store** – configurable (e.g., Pinecone, Qdrant).
4. **Retriever & Grader** – similarity search + relevance grading.
5. **Corrective Engine** – CRAG logic for query rewriting and answer correction.
6. **Generation Layer** – LLM with prompt templates, citation injection.
7. **Observability** – logging, metrics, token accounting.

## Current Phase & Milestone
- **Phase 00 – Foundation** – repository scaffolding, documentation, planning artifacts. **Milestone: Documentation complete, ready for Claude Code handoff.**

## Completed Work
- Directory structure created.
- Initial README, PROJECT, DECISIONS, CHANGELOG, .gitignore, .env.example, requirements.txt.
- Preliminary implementation_plan (now removed).

## Active Work
- Expanding documentation per master bootstrap requirements.
- Populating ADRs, evaluation, token strategy, experiment frameworks.
- Creating detailed phase implementation plans.

## Next Action
Proceed with the creation of canonical documentation files and phase plans as outlined in the approved implementation plan.

## Known Issues
- ADR templates not yet defined (pending user clarification).

## Open Questions
- Preferred ADR format?
- Inclusion of CI badges in README?
- Additional top‑level directories (e.g., `examples/`)?

## Project Risks
- Scope creep: adding implementation code prematurely.
- Incomplete ADR decisions may lead to architectural ambiguity.
- Token‑budget oversights could impact cost estimation.

## Architecture Decisions (ADRs)
- ADR‑001 – Language & Framework Selection (PROPOSED)
- ADR‑002 – Vector Store Provider (PROPOSED)
- ADR‑003 – Embedding Model (PROPOSED)
- ADR‑004 – Retrieval Strategy (PROPOSED)
- ADR‑005 – Grading Model (PROPOSED)
- ADR‑006 – CRAG Loop Design (PROPOSED)
- ADR‑007 – Observability Stack (PROPOSED)
- ADR‑008 – Token Budget Monitoring (PROPOSED)
- ADR‑009 – Evaluation Framework (PROPOSED)
- ADR‑010 – Deployment Strategy (PROPOSED)

## Retrieval Metrics
- Recall@K, Precision@K, MRR, NDCG.

## Generation Metrics
- Faithfulness, Answer relevance, Citation correctness, Context relevance.

## System Metrics
- End‑to‑end latency, Token usage per query, Cost per query, Retry rate.

## Token Budget
- Input tokens ≤ 4,000 per request; Output tokens ≤ 1,000; Embedding tokens ≤ 2,000.

## Context‑Window Strategy
- Truncate and summarize long documents; use hierarchical chunking; prioritize recent data.

## Evaluation Status
- Evaluation plan drafted (see `docs/evaluation/`).

## Definition of Done (DoD)
- All documentation files created and populated.
- Directory structure validated.
- No implementation code present.
- Acceptance criteria for each phase documented.
- Ready for Claude Code to begin Phase 00 implementation.
