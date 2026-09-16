import pytest

from embeddings.embedding_service import EmbeddingService
from embeddings.vector_store import VectorStore
from ingestion.consumer import IngestionConsumer
from ingestion.producer import RawItem


@pytest.fixture(scope="module")
def embedder():
    return EmbeddingService()


@pytest.fixture
def store(tmp_path, embedder):
    s = VectorStore(collection_name="ingest_test", vector_size=embedder.dimension, qdrant_path=str(tmp_path / "s"))
    yield s
    s.close()


def test_process_indexes_items_with_published_at(store, embedder):
    consumer = IngestionConsumer(vector_store=store, embedder=embedder)
    items = [
        RawItem(
            source_id="a1",
            title="Test Article",
            summary="This article is about testing ingestion pipelines.",
            link="https://example.com/a1",
            published_at="2024-01-01T00:00:00+00:00",
        )
    ]

    stats = consumer.process(items)

    assert stats.items_processed == 1
    assert stats.chunks_indexed >= 1
    assert stats.errors == []

    results = store.query(embedder.embed("testing ingestion pipelines"), top_k=1)
    assert len(results) == 1
    assert results[0].record.published_at == "2024-01-01T00:00:00+00:00"
    assert results[0].record.document_id == "a1"


def test_process_skips_empty_item_without_aborting_batch(store, embedder):
    consumer = IngestionConsumer(vector_store=store, embedder=embedder)
    items = [
        RawItem(source_id="empty", title="", summary="   ", link="l", published_at=None),
        RawItem(source_id="good", title="Real content here", summary="more real content", link="l2", published_at=None),
    ]

    stats = consumer.process(items)

    assert stats.items_processed == 2
    assert stats.chunks_indexed >= 1  # the good item still got indexed
    assert len(stats.errors) == 1
    assert "empty" in stats.errors[0]
