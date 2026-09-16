import pytest

from rag_baseline.chunker import chunk_document
from rag_baseline.loader import Document
from rag_baseline.retriever import Retriever

SAMPLE_TEXT = "The sky is blue. Grass is green. Cats are mammals."


def _sample_chunks():
    doc = Document(document_id="doc1", source="doc1.txt", content=SAMPLE_TEXT)
    return chunk_document(doc, chunk_size=20, overlap=0)


@pytest.fixture(scope="module")
def storage_dir(tmp_path_factory):
    return tmp_path_factory.mktemp("qdrant_local")


@pytest.fixture(scope="module")
def indexed_retriever(storage_dir):
    retriever = Retriever(collection_name="test_collection", qdrant_path=str(storage_dir / "shared"))
    retriever.index(_sample_chunks())
    yield retriever
    retriever.close()


def test_retrieve_returns_relevant_chunk(indexed_retriever):
    results = indexed_retriever.retrieve("What color is the sky?", top_k=1)
    assert len(results) == 1
    assert "blue" in results[0].content.lower() or "sky" in results[0].content.lower()


def test_retrieve_respects_top_k(indexed_retriever):
    results = indexed_retriever.retrieve("animals", top_k=2)
    assert len(results) <= 2


def test_index_empty_chunks_returns_zero(indexed_retriever):
    assert indexed_retriever.index([]) == 0


def test_storage_persists_across_separate_retriever_instances(storage_dir):
    """Indexed data must survive a process restart, not just live in one instance's memory."""
    path = str(storage_dir / "persistence_check")

    writer = Retriever(collection_name="persist_test", qdrant_path=path)
    indexed = writer.index(_sample_chunks())
    assert indexed == len(_sample_chunks())
    writer.close()

    reader = Retriever(collection_name="persist_test", qdrant_path=path)
    try:
        results = reader.retrieve("What color is the sky?", top_k=1)
        assert len(results) == 1
        assert "blue" in results[0].content.lower() or "sky" in results[0].content.lower()
    finally:
        reader.close()
