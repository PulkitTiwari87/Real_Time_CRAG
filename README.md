# Real-Time Corrective RAG Intelligence Platform

**Status:** Implemented through Phase 15 (see `PROJECT.md` for phase tracking). A working FastAPI backend, CRAG loop, embedded vector store, and static frontend exist and are tested; see [Implemented vs. planned](#implemented-vs-planned) below for the honest boundary.

## Overview
A Corrective Retrieval-Augmented Generation (CRAG) system: ingest documents, retrieve and grade relevant chunks, rewrite the query and retry when retrieval quality is poor, and generate a grounded, cited answer.

## Contents
- PROJECT.md — project control document and phase tracker
- ARCHITECTURE.md — high-level architectural description
- DECISIONS.md — Architecture Decision Records (ADRs)
- plans/ — detailed phase plans and roadmap
- docs/ — concept, evaluation, and deployment documentation
- src/ — implementation (API, retrieval, corrective loop, embeddings, streaming, evaluation)
- tests/ — unit and integration test suite
- infrastructure/ — Kafka docker-compose for local development

## Implemented vs. planned

**Implemented:** FastAPI backend (`src/api`) with `/health`, `/metrics`,
`/ingest`, `/query`; embedded (local, file-based) Qdrant vector store;
BM25 + vector retrieval with fallback; the CRAG retrieve/grade/rewrite
loop; Gemini and Ollama LLM providers; a static single-page frontend
served by the API itself; Prometheus metrics and structured logging; a
Dockerfile and `docker-compose.yml` for local containerized runs.

**Planned, not deployed:** Kafka-based real-time ingestion
(`src/streaming/` is unit-tested against a mocked/unreachable broker
only, never a live one); LangGraph-based orchestration
(`src/orchestration/graph.py` exists but isn't wired into the API);
time-aware ranking (`src/time_aware/` is implemented and tested but not
called from the API path); any externally hosted, publicly reachable
deployment.

## CI/CD

```
Developer -> Pull Request -> GitHub Actions (lint, tests, docker build, dependency audit)
                                    |
                              push to main
                                    v
                    GitHub Actions (same checks) -> GHCR image (tagged by commit SHA)
                                    v
                         smoke test (GET /health)
```

- **CI** (`.github/workflows/ci.yml`): runs on every PR and push to `main`
  — `flake8`, the full `pytest` suite, `docker compose config` validation,
  a real `docker build`, and `pip-audit`.
- **CD** (`.github/workflows/cd.yml`): only triggers after CI succeeds on
  `main`, builds the backend image, and pushes it to
  `ghcr.io/pulkittiwari87/real_time_crag` tagged with the commit SHA and
  `latest`, then runs it and polls `/health` as a smoke test.
- No workflow deploys to a persistent external server — see
  [`docs/deployment/ci-cd.md`](docs/deployment/ci-cd.md) for the full
  pipeline, required secrets (none beyond the built-in `GITHUB_TOKEN`
  today), image tags/rollback, and why GitHub Pages isn't used for the
  frontend yet.

## Next Steps
See `PROJECT.md` for open phases and `docs/deployment/production-readiness.md`
for an honest assessment of what is and isn't hardened.
