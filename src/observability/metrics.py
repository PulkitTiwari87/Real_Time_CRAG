"""Phase 15: Prometheus-compatible metrics for the API.

Small, focused set: request counts by endpoint/status, query latency, and
CRAG-specific signals (rewrite rate, abstention rate) -- the things this
project's own evaluation docs (docs/evaluation/metrics.md) call "System
Metrics", exposed for scraping rather than just printed to logs.
"""
from __future__ import annotations

from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter(
    "rag_api_requests_total", "Total API requests", ["endpoint", "status"]
)
QUERY_LATENCY_SECONDS = Histogram(
    "rag_query_latency_seconds", "End-to-end /query latency in seconds"
)
QUERY_REWRITE_COUNT = Counter(
    "rag_query_rewrites_total", "Total query rewrites performed across all /query calls"
)
QUERY_ABSTENTION_COUNT = Counter(
    "rag_query_abstentions_total", "Total /query calls that abstained (insufficient evidence)"
)
