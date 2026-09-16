"""Phase 10: ties RSS producer -> in-process queue -> consumer together."""
from __future__ import annotations

from embeddings.embedding_service import EmbeddingService
from embeddings.vector_store import VectorStore

from .consumer import IngestionConsumer, IngestStats
from .producer import parse_rss
from .queue import IngestionQueue


def ingest_feed(feed_content_or_url: str, vector_store: VectorStore, embedder: EmbeddingService) -> IngestStats:
    items = parse_rss(feed_content_or_url)
    q = IngestionQueue()
    q.put_many(items)
    consumer = IngestionConsumer(vector_store=vector_store, embedder=embedder)
    return consumer.process(q.get_all())
