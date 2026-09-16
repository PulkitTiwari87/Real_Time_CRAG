"""Phase 10 consumer: normalize -> chunk -> embed -> index each queued item.

A single bad item (empty after cleaning, embedding failure, etc.) is
recorded in IngestStats.errors and skipped -- it does not abort the whole
batch, matching the resilience pattern already used by
document_processing.loader.BaseLoader.load_dir.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from document_processing.chunker import Chunker
from document_processing.loader import Document, clean_text
from embeddings.embedding_service import EmbeddingService
from embeddings.vector_store import VectorStore

from .producer import RawItem


@dataclass(frozen=True)
class IngestStats:
    items_processed: int
    chunks_indexed: int
    errors: list[str] = field(default_factory=list)


class IngestionConsumer:
    def __init__(
        self, vector_store: VectorStore, embedder: EmbeddingService, chunker: Chunker | None = None
    ) -> None:
        self._store = vector_store
        self._embedder = embedder
        self._chunker = chunker or Chunker()

    def process(self, items: list[RawItem]) -> IngestStats:
        chunks_indexed = 0
        errors: list[str] = []
        for item in items:
            try:
                content = clean_text(f"{item.title}\n{item.summary}")
                if not content:
                    errors.append(f"{item.source_id}: empty after cleaning")
                    continue
                doc = Document(document_id=item.source_id, source=item.link or item.source_id, content=content)
                for c in self._chunker.chunk(doc):
                    self._store.upsert(
                        chunk_id=c.chunk_id,
                        document_id=c.document_id,
                        source=c.source,
                        content=c.content,
                        vector=self._embedder.embed(c.content),
                        published_at=item.published_at,
                    )
                    chunks_indexed += 1
            except Exception as exc:
                errors.append(f"{item.source_id}: {exc}")
        return IngestStats(items_processed=len(items), chunks_indexed=chunks_indexed, errors=errors)
