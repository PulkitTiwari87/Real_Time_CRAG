import pytest

from document_processing.chunker import Chunker
from document_processing.loader import Document


def _doc(content: str) -> Document:
    return Document(document_id="doc1", source="doc1.txt", content=content)


def test_chunk_respects_size_and_overlap():
    chunker = Chunker(chunk_size=10, overlap=2)
    doc = _doc(" ".join(f"word{i}" for i in range(60)))
    chunks = chunker.chunk(doc)
    assert len(chunks) > 1
    assert all(c.token_count <= 10 for c in chunks)
    assert all(c.document_id == "doc1" for c in chunks)
    assert chunks[0].chunk_id == "doc1::0"


def test_chunk_short_document_single_chunk():
    chunker = Chunker(chunk_size=200, overlap=20)
    doc = _doc("just a short sentence")
    chunks = chunker.chunk(doc)
    assert len(chunks) == 1
    assert chunks[0].content.strip() != ""


def test_chunker_invalid_chunk_size_raises():
    with pytest.raises(ValueError):
        Chunker(chunk_size=0)


def test_chunker_invalid_overlap_raises():
    with pytest.raises(ValueError):
        Chunker(chunk_size=10, overlap=10)
