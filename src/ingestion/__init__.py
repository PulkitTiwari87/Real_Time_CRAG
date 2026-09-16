"""Phase 10: real-time-style ingestion -- RSS Producer -> queue -> Consumer -> normalize/chunk/embed/Qdrant."""
from .consumer import IngestionConsumer, IngestStats
from .pipeline import ingest_feed
from .producer import RawItem, parse_rss
from .queue import IngestionQueue, QueueStats

__all__ = [
    "parse_rss",
    "RawItem",
    "IngestionQueue",
    "QueueStats",
    "IngestionConsumer",
    "IngestStats",
    "ingest_feed",
]
