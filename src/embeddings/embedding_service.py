"""Embedding service: a clear embed(text) -> Vector contract over a
configurable local embedding model.

Default model is all-MiniLM-L6-v2, chosen per the Phase 03 benchmark (see
docs/experiments/phase03-embedding-benchmark.md) over the larger
all-MiniLM-L12-v2: L12 was not decisively more accurate on the benchmark
set but was slower, so there was no evidence-based reason to pay the extra
latency (avoid premature optimization). Configurable via EMBEDDING_MODEL.
"""
from __future__ import annotations

import os
from functools import lru_cache

from sentence_transformers import SentenceTransformer

Vector = list[float]

DEFAULT_MODEL = os.environ.get("EMBEDDING_MODEL") or "all-MiniLM-L6-v2"


@lru_cache(maxsize=4)
def _load_model(model_name: str) -> SentenceTransformer:
    return SentenceTransformer(model_name)


class EmbeddingService:
    def __init__(self, model_name: str | None = None) -> None:
        self.model_name = model_name or DEFAULT_MODEL
        self._model = _load_model(self.model_name)

    @property
    def dimension(self) -> int:
        return self._model.get_embedding_dimension()

    def embed(self, text: str) -> Vector:
        return self._model.encode(text, show_progress_bar=False).tolist()

    def embed_batch(self, texts: list[str]) -> list[Vector]:
        if not texts:
            return []
        return [v.tolist() for v in self._model.encode(texts, show_progress_bar=False)]
