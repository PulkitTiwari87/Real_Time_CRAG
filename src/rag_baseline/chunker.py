"""Fixed-size chunking for the RAG baseline pipeline."""
from __future__ import annotations

from dataclasses import dataclass

from .loader import Document


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    document_id: str
    source: str
    content: str


def chunk_document(document: Document, chunk_size: int = 500, overlap: int = 50) -> list[Chunk]:
    """Split a document into fixed-size, optionally overlapping chunks."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and < chunk_size")

    text = document.content
    step = chunk_size - overlap
    chunks: list[Chunk] = []
    start = 0
    index = 0
    while start < len(text):
        piece = text[start : start + chunk_size].strip()
        if piece:
            chunks.append(
                Chunk(
                    chunk_id=f"{document.document_id}::{index}",
                    document_id=document.document_id,
                    source=document.source,
                    content=piece,
                )
            )
            index += 1
        start += step
    return chunks
