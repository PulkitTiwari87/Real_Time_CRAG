import pytest

from embeddings.embedding_service import EmbeddingService
from embeddings.vector_store import VectorStore


@pytest.fixture(scope="module")
def embedder():
    return EmbeddingService()


@pytest.fixture
def store(tmp_path, embedder):
    s = VectorStore(collection_name="test", vector_size=embedder.dimension, qdrant_path=str(tmp_path / "store"))
    yield s
    s.close()


def test_upsert_and_query_returns_record_with_temporal_fields(store, embedder):
    vector = embedder.embed("the sky is blue")
    store.upsert(chunk_id="doc1::0", document_id="doc1", source="doc1.txt", content="the sky is blue", vector=vector)

    results = store.query(embedder.embed("what color is the sky"), top_k=1)
    assert len(results) == 1
    record = results[0].record
    assert record.chunk_id == "doc1::0"
    assert record.document_id == "doc1"
    assert record.content == "the sky is blue"
    assert record.ingested_at  # auto-populated, non-empty
    assert record.published_at is None  # not provided


def test_upsert_stores_published_at_when_given(store, embedder):
    vector = embedder.embed("published fact")
    store.upsert(
        chunk_id="doc2::0",
        document_id="doc2",
        source="doc2.txt",
        content="published fact",
        vector=vector,
        published_at="2026-01-01T00:00:00+00:00",
    )
    results = store.query(embedder.embed("published fact"), top_k=1)
    assert results[0].record.published_at == "2026-01-01T00:00:00+00:00"


def test_count_reflects_upserts(store, embedder):
    assert store.count() == 0
    store.upsert(
        chunk_id="doc3::0",
        document_id="doc3",
        source="doc3.txt",
        content="something",
        vector=embedder.embed("something"),
    )
    assert store.count() == 1


def test_storage_persists_across_separate_instances(tmp_path, embedder):
    path = str(tmp_path / "persist_check")
    writer = VectorStore(collection_name="persist", vector_size=embedder.dimension, qdrant_path=path)
    writer.upsert(
        chunk_id="doc4::0",
        document_id="doc4",
        source="doc4.txt",
        content="persisted content",
        vector=embedder.embed("persisted content"),
    )
    writer.close()

    reader = VectorStore(collection_name="persist", vector_size=embedder.dimension, qdrant_path=path)
    try:
        results = reader.query(embedder.embed("persisted content"), top_k=1)
        assert results[0].record.content == "persisted content"
    finally:
        reader.close()
