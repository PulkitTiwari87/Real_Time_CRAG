"""Embedding + Qdrant-backed retrieval for the RAG baseline pipeline.

Runs against a local, embedded Qdrant instance by default (no Docker/server
required), per the project's zero-cost/local-first requirement. Storage is
persistent on-disk by default (under ``local_vector_store/``, already
covered by .gitignore) so indexed chunks survive process restarts, as
implied by the phase plan's "Store embeddings in Qdrant". Pass
``qdrant_url`` to target a real Qdrant deployment instead, or ``qdrant_path``
to point at a different local directory (tests use an isolated tmp dir).
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from sentence_transformers import SentenceTransformer

from .chunker import Chunk

DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
DEFAULT_COLLECTION = "rag_baseline_chunks"
DEFAULT_LOCAL_STORAGE_DIR = Path(__file__).resolve().parents[2] / "local_vector_store"


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: str
    document_id: str
    source: str
    content: str
    score: float


class Retriever:
    def __init__(
        self,
        collection_name: str = DEFAULT_COLLECTION,
        embedding_model: str = DEFAULT_EMBEDDING_MODEL,
        qdrant_url: str | None = None,
        qdrant_path: str | None = None,
    ) -> None:
        self._model = SentenceTransformer(embedding_model)
        self._vector_size = self._model.get_embedding_dimension()
        self._collection_name = collection_name
        if qdrant_url:
            self._client = QdrantClient(url=qdrant_url)
        else:
            path = Path(qdrant_path) if qdrant_path else DEFAULT_LOCAL_STORAGE_DIR
            path.mkdir(parents=True, exist_ok=True)
            self._client = QdrantClient(path=str(path))
        self._ensure_collection()

    def close(self) -> None:
        """Release the on-disk storage lock so another instance can open it."""
        self._client.close()

    def _ensure_collection(self) -> None:
        existing = [c.name for c in self._client.get_collections().collections]
        if self._collection_name not in existing:
            self._client.create_collection(
                collection_name=self._collection_name,
                vectors_config=qmodels.VectorParams(
                    size=self._vector_size, distance=qmodels.Distance.COSINE
                ),
            )

    def index(self, chunks: list[Chunk]) -> int:
        """Embed and upsert chunks. Returns the number of chunks indexed."""
        if not chunks:
            return 0
        vectors = self._model.encode([c.content for c in chunks], show_progress_bar=False)
        points = [
            qmodels.PointStruct(
                id=str(uuid.uuid5(uuid.NAMESPACE_URL, chunk.chunk_id)),
                vector=vector.tolist(),
                payload={
                    "chunk_id": chunk.chunk_id,
                    "document_id": chunk.document_id,
                    "source": chunk.source,
                    "content": chunk.content,
                },
            )
            for chunk, vector in zip(chunks, vectors)
        ]
        self._client.upsert(collection_name=self._collection_name, points=points)
        return len(points)

    def retrieve(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        """Embed the query and return the top-k most similar chunks."""
        query_vector = self._model.encode(query, show_progress_bar=False).tolist()
        response = self._client.query_points(
            collection_name=self._collection_name,
            query=query_vector,
            limit=top_k,
        )
        return [
            RetrievedChunk(
                chunk_id=r.payload["chunk_id"],
                document_id=r.payload["document_id"],
                source=r.payload["source"],
                content=r.payload["content"],
                score=r.score,
            )
            for r in response.points
        ]
