"""Vector store repository abstraction over Qdrant.

Generalizes retrieval beyond the Phase 01 baseline's Retriever (which is
tightly coupled to rag_baseline's Chunk type), with explicit support for
the temporal metadata fields (ingested_at, published_at) that Phase 12
(time-aware retrieval) will need. Continues using Qdrant per ADR-002 and
the working Phase 01 integration, rather than introducing a second vector
store, even though this plan's text names Chroma as an example.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

DEFAULT_LOCAL_STORAGE_DIR = Path(__file__).resolve().parents[2] / "local_vector_store"


@dataclass(frozen=True)
class VectorRecord:
    id: str
    document_id: str
    chunk_id: str
    source: str
    content: str
    ingested_at: str
    published_at: str | None = None


@dataclass(frozen=True)
class ScoredRecord:
    record: VectorRecord
    score: float


class VectorStore:
    def __init__(
        self,
        collection_name: str,
        vector_size: int,
        qdrant_url: str | None = None,
        qdrant_path: str | None = None,
    ) -> None:
        self._collection_name = collection_name
        self._vector_size = vector_size
        if qdrant_url:
            self._client = QdrantClient(url=qdrant_url)
        else:
            path = Path(qdrant_path) if qdrant_path else DEFAULT_LOCAL_STORAGE_DIR
            path.mkdir(parents=True, exist_ok=True)
            self._client = QdrantClient(path=str(path))
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        existing = [c.name for c in self._client.get_collections().collections]
        if self._collection_name not in existing:
            self._client.create_collection(
                collection_name=self._collection_name,
                vectors_config=qmodels.VectorParams(size=self._vector_size, distance=qmodels.Distance.COSINE),
            )

    def upsert(
        self,
        chunk_id: str,
        document_id: str,
        source: str,
        content: str,
        vector: list[float],
        published_at: str | None = None,
    ) -> str:
        point_id = str(uuid.uuid5(uuid.NAMESPACE_URL, chunk_id))
        payload = {
            "chunk_id": chunk_id,
            "document_id": document_id,
            "source": source,
            "content": content,
            "ingested_at": datetime.now(timezone.utc).isoformat(),
            "published_at": published_at,
        }
        self._client.upsert(
            collection_name=self._collection_name,
            points=[qmodels.PointStruct(id=point_id, vector=vector, payload=payload)],
        )
        return point_id

    def query(self, vector: list[float], top_k: int = 5) -> list[ScoredRecord]:
        response = self._client.query_points(collection_name=self._collection_name, query=vector, limit=top_k)
        return [
            ScoredRecord(
                record=VectorRecord(
                    id=str(r.id),
                    document_id=r.payload["document_id"],
                    chunk_id=r.payload["chunk_id"],
                    source=r.payload["source"],
                    content=r.payload["content"],
                    ingested_at=r.payload["ingested_at"],
                    published_at=r.payload.get("published_at"),
                ),
                score=r.score,
            )
            for r in response.points
        ]

    def count(self) -> int:
        return self._client.count(collection_name=self._collection_name).count

    def close(self) -> None:
        self._client.close()
