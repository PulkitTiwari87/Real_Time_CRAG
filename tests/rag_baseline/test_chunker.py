import pytest

from rag_baseline.chunker import chunk_document
from rag_baseline.loader import Document


def _doc(content: str) -> Document:
    return Document(document_id="doc1", source="doc1.txt", content=content)


def test_chunk_document_basic_split():
    doc = _doc("x" * 120)
    chunks = chunk_document(doc, chunk_size=50, overlap=0)
    assert len(chunks) == 3
    assert chunks[0].chunk_id == "doc1::0"
    assert all(c.document_id == "doc1" for c in chunks)


def test_chunk_document_overlap_produces_at_least_as_many_chunks():
    doc = _doc("x" * 120)
    no_overlap = chunk_document(doc, chunk_size=50, overlap=0)
    with_overlap = chunk_document(doc, chunk_size=50, overlap=25)
    assert len(with_overlap) >= len(no_overlap)


def test_chunk_document_short_text_single_chunk():
    doc = _doc("short text")
    chunks = chunk_document(doc, chunk_size=500, overlap=50)
    assert len(chunks) == 1
    assert chunks[0].content == "short text"


def test_chunk_document_invalid_chunk_size_raises():
    with pytest.raises(ValueError):
        chunk_document(_doc("text"), chunk_size=0)


def test_chunk_document_invalid_overlap_raises():
    with pytest.raises(ValueError):
        chunk_document(_doc("text"), chunk_size=10, overlap=10)
