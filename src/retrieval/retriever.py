"""Configurable retriever: vector search (Phase 03's VectorStore) as the
primary path, with an optional BM25 lexical fallback used only when vector
search returns nothing (e.g. an empty/cold store).
"""
from __future__ import annotations

from dataclasses import dataclass

from rank_bm25 import BM25Okapi

from embeddings.embedding_service import EmbeddingService
from embeddings.vector_store import VectorStore


@dataclass(frozen=True)
class RetrievalResult:
    chunk_id: str
    document_id: str
    source: str
    content: str
    score: float
    method: str  # "vector" or "bm25"
    published_at: str | None = None


@dataclass(frozen=True)
class BM25Doc:
    chunk_id: str
    document_id: str
    source: str
    content: str
    published_at: str | None = None


class Retriever:
    def __init__(self, vector_store: VectorStore, embedder: EmbeddingService) -> None:
        self._store = vector_store
        self._embedder = embedder
        self._bm25_docs: list[BM25Doc] = []
        self._bm25: BM25Okapi | None = None

    def index_bm25(self, docs: list[BM25Doc]) -> None:
        """Build a lexical (BM25) index over the given docs.

        A simple, non-persisted, rebuild-from-corpus index -- appropriate
        for the local corpus sizes this project targets; not a distributed
        or incrementally-updated index (explicitly out of scope).
        """
        self._bm25_docs = docs
        tokenized = [d.content.lower().split() for d in docs]
        self._bm25 = BM25Okapi(tokenized) if tokenized else None

    def retrieve_vector(self, query: str, top_k: int = 5) -> list[RetrievalResult]:
        vector = self._embedder.embed(query)
        results = self._store.query(vector, top_k=top_k)
        return [
            RetrievalResult(
                chunk_id=r.record.chunk_id,
                document_id=r.record.document_id,
                source=r.record.source,
                content=r.record.content,
                score=r.score,
                method="vector",
                published_at=r.record.published_at,
            )
            for r in results
        ]

    def retrieve_bm25(self, query: str, top_k: int = 5) -> list[RetrievalResult]:
        """Rank by BM25 score, return top_k candidates.

        Does not filter by score sign/magnitude: classic BM25's IDF term,
        log((N - df + 0.5) / (df + 0.5)), can be exactly zero for small
        corpora (e.g. N=2 docs, term in exactly 1 -> log(1) == 0), which
        would make an ``score > 0`` filter drop genuinely-relevant results
        by mathematical coincidence rather than by relevance. Relevance
        filtering is the grader's job (see grader.py), not the retriever's.
        """
        if not self._bm25:
            return []
        scores = self._bm25.get_scores(query.lower().split())
        ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        return [
            RetrievalResult(
                chunk_id=self._bm25_docs[i].chunk_id,
                document_id=self._bm25_docs[i].document_id,
                source=self._bm25_docs[i].source,
                content=self._bm25_docs[i].content,
                score=float(scores[i]),
                method="bm25",
                published_at=self._bm25_docs[i].published_at,
            )
            for i in ranked
        ]

    def retrieve(self, query: str, top_k: int = 5, use_bm25_fallback: bool = True) -> list[RetrievalResult]:
        results = self.retrieve_vector(query, top_k=top_k)
        if not results and use_bm25_fallback:
            results = self.retrieve_bm25(query, top_k=top_k)
        return results
