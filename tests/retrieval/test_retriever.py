import pytest

from embeddings.embedding_service import EmbeddingService
from embeddings.vector_store import VectorStore
from retrieval.retriever import BM25Doc, Retriever

SAMPLE_TEXT = "The sky is blue. Grass is green. Cats are mammals."


@pytest.fixture(scope="module")
def embedder():
    return EmbeddingService()


@pytest.fixture
def retriever(tmp_path, embedder):
    store = VectorStore(collection_name="test", vector_size=embedder.dimension, qdrant_path=str(tmp_path / "store"))
    r = Retriever(vector_store=store, embedder=embedder)
    yield r
    store.close()


def test_retrieve_vector_returns_relevant_result(retriever, embedder):
    retriever._store.upsert(
        chunk_id="doc1::0",
        document_id="doc1",
        source="doc1.txt",
        content="the sky is blue",
        vector=embedder.embed("the sky is blue"),
    )
    results = retriever.retrieve_vector("what color is the sky", top_k=1)
    assert len(results) == 1
    assert results[0].method == "vector"
    assert "sky" in results[0].content.lower()


def test_retrieve_bm25_matches_lexical_overlap(retriever):
    # BM25's classic IDF formula is log((N - df + 0.5) / (df + 0.5)): with only
    # 2 docs and a term in exactly 1 of them, idf collapses to log(1) == 0,
    # zeroing every score. Use 3+ docs so the corpus isn't sitting on that
    # small-N degenerate case (verified directly: N=2 -> [0, 0], N=3 -> real scores).
    docs = [
        BM25Doc(chunk_id="a::0", document_id="a", source="a.txt", content="the sky is blue today"),
        BM25Doc(chunk_id="b::0", document_id="b", source="b.txt", content="cats are small mammals"),
        BM25Doc(chunk_id="c::0", document_id="c", source="c.txt", content="python is a programming language"),
    ]
    retriever.index_bm25(docs)
    results = retriever.retrieve_bm25("blue sky", top_k=1)
    assert len(results) == 1
    assert results[0].chunk_id == "a::0"
    assert results[0].method == "bm25"


def test_retrieve_falls_back_to_bm25_when_vector_store_empty(retriever):
    docs = [
        BM25Doc(chunk_id="a::0", document_id="a", source="a.txt", content="mitochondria produce atp"),
        BM25Doc(chunk_id="b::0", document_id="b", source="b.txt", content="cats are small mammals"),
        BM25Doc(chunk_id="c::0", document_id="c", source="c.txt", content="python is a programming language"),
    ]
    retriever.index_bm25(docs)
    # Vector store is empty (nothing upserted), so retrieve() should fall back to BM25.
    results = retriever.retrieve("atp production", top_k=1, use_bm25_fallback=True)
    assert len(results) == 1
    assert results[0].method == "bm25"


def test_retrieve_no_fallback_returns_empty_when_store_empty(retriever):
    results = retriever.retrieve("anything", top_k=1, use_bm25_fallback=False)
    assert results == []
