import pytest

from embeddings.embedding_service import EmbeddingService
from embeddings.vector_store import VectorStore
from ingestion.pipeline import ingest_feed

SAMPLE_FEED = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
<title>Test Feed</title>
<item>
<title>Qdrant Overview</title>
<link>https://example.com/qdrant</link>
<description>Qdrant is an open-source vector database used for similarity search.</description>
<pubDate>Mon, 01 Jan 2024 12:00:00 GMT</pubDate>
<guid>https://example.com/qdrant</guid>
</item>
</channel>
</rss>
"""


@pytest.fixture(scope="module")
def embedder():
    return EmbeddingService()


def test_ingest_feed_end_to_end(tmp_path, embedder):
    store = VectorStore(collection_name="pipeline_test", vector_size=embedder.dimension, qdrant_path=str(tmp_path / "s"))
    try:
        stats = ingest_feed(SAMPLE_FEED, store, embedder)
        assert stats.items_processed == 1
        assert stats.chunks_indexed >= 1

        results = store.query(embedder.embed("vector database for similarity search"), top_k=1)
        assert len(results) == 1
        assert "qdrant" in results[0].record.content.lower()
    finally:
        store.close()
