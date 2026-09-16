# Phase 15 Production Readiness Assessment

Per this project's own master prompt: *"Do not claim 'production ready'
merely because Docker works."* This document says plainly what is and
isn't hardened, rather than asserting a blanket status.

## What is genuinely hardened

- **Health check**: `GET /health` (Phase 13), now recorded in metrics.
- **Structured logging**: JSON logs via `src/observability/logging_config.py`,
  verified to produce valid, parseable JSON with exception info when present.
- **Metrics**: `GET /metrics` (Prometheus format) exposes request counts by
  endpoint/status, query latency, rewrite count, and abstention count --
  verified live via the test suite.
- **Security headers**: `X-Content-Type-Options: nosniff`,
  `X-Frame-Options: DENY` on every response, verified in tests.
- **Error handling**: every failure path (generation errors, unexpected
  exceptions, malformed Kafka messages, unreachable broker, missing API
  key) returns a clean, generic client-facing message -- verified that no
  stack trace, provider name, or file path leaks to the client.
- **Bounded failure recovery**: CRAG retries are hard-bounded (verified:
  never exceeds `max_retries`, never loops); Kafka consumer commits
  offsets only after processing so a crash mid-message reprocesses rather
  than silently drops it; a bad ingestion item is dead-lettered, not
  fatal to the batch.
- **Input validation**: Pydantic field length/range limits on every API
  request.
- **Reproducibility**: `requirements.txt` is fully pinned to versions
  actually installed and tested in this session.
- **Configuration**: all secrets/endpoints come from environment
  variables (`.env`, never committed -- gitignored, confirmed throughout
  this session), never hardcoded.

## What is NOT verified, and why

- **Docker / docker-compose**: `Dockerfile`, `docker-compose.yml`, and
  `infrastructure/docker-compose.kafka.yml` are written correctly against
  the standard APIs, but **Docker is unavailable in this development
  sandbox** (confirmed repeatedly across this session). They have not
  been built or run. Verify locally: `docker compose up --build`.
- **Kafka in production**: the streaming producer/consumer (Phase 11) is
  unit-tested (serialization, connection-error handling against a real
  unreachable address) but has never talked to a real broker, for the
  same reason.
- **Load/scale testing**: none performed. All latency numbers in this
  project's benchmark reports (`docs/experiments/`) are single-request,
  single-machine measurements, not throughput-under-load figures.
- **Multi-instance / high availability**: the system runs as a single
  process with a single embedded (not clustered) Qdrant instance. There
  is no failover, no horizontal scaling story, no distributed lock beyond
  Qdrant's own local-mode file lock.
- **Authentication**: deliberately not implemented. This is a local-first,
  single-tenant project by design (see ADR discussions and the project's
  zero-cost requirement) -- adding auth without a real multi-tenant
  requirement would be premature complexity, not hardening. If this is
  ever exposed beyond local use, authentication and rate limiting become
  required, not optional.
- **Clean-environment install**: `requirements.txt` is pinned, but a
  fresh `pip install -r requirements.txt` into an empty virtual
  environment was not performed in this session (all packages were
  already installed incrementally as each phase needed them).

## Known operational gotchas found during this project (worth keeping)

- Two real Windows-specific issues were found and fixed during
  development, both documented in code comments where they were fixed:
  a DLL conflict between scikit-learn and torch when scikit-learn imports
  first (fixed by import ordering), and `kafka-python`'s default timeouts
  not bounding connection failure at all well against an unreachable
  broker (took 26 minutes instead of ~5 seconds before a fix pinning
  `api_version` and short timeouts).
- Free-tier LLM API quotas (Gemini) are real and get exhausted by heavy
  local testing -- the system's own error handling degrades correctly
  when this happens (clean 503, no crash), verified live.

## Honest overall status

**Code-complete and unit/integration-tested for everything that doesn't
require Docker or a live Kafka broker.** Not "production ready" in the
full sense (no load testing, no HA, no live container verification) --
"hardened for a well-tested local-first single-tenant deployment, with
clearly documented gaps for anyone taking it further."
