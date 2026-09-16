"""Phase 15: structured logging + Prometheus-compatible metrics."""
from .logging_config import configure_logging
from .metrics import QUERY_ABSTENTION_COUNT, QUERY_LATENCY_SECONDS, QUERY_REWRITE_COUNT, REQUEST_COUNT

__all__ = [
    "configure_logging",
    "REQUEST_COUNT",
    "QUERY_LATENCY_SECONDS",
    "QUERY_REWRITE_COUNT",
    "QUERY_ABSTENTION_COUNT",
]
