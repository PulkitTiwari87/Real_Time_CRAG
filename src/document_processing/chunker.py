"""Token-based chunking with configurable overlap.

Reuses the Phase 01 embedding model's own tokenizer (via `transformers`,
already a transitive dependency of sentence-transformers) for token
counting/splitting, instead of adding a separate tokenizer dependency
(e.g. tiktoken) purely for this purpose.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from transformers import AutoTokenizer

from .loader import Document

DEFAULT_TOKENIZER_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


@dataclass(frozen=True)
class TokenChunk:
    chunk_id: str
    document_id: str
    source: str
    content: str
    token_count: int


@lru_cache(maxsize=4)
def _get_tokenizer(model_name: str):
    return AutoTokenizer.from_pretrained(model_name)


class Chunker:
    def __init__(
        self,
        chunk_size: int = 200,
        overlap: int = 20,
        tokenizer_model: str = DEFAULT_TOKENIZER_MODEL,
    ) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if overlap < 0 or overlap >= chunk_size:
            raise ValueError("overlap must be >= 0 and < chunk_size")
        self._chunk_size = chunk_size
        self._overlap = overlap
        self._tokenizer = _get_tokenizer(tokenizer_model)

    def chunk(self, document: Document) -> list[TokenChunk]:
        token_ids = self._tokenizer.encode(document.content, add_special_tokens=False)
        step = self._chunk_size - self._overlap
        chunks: list[TokenChunk] = []
        index = 0
        start = 0
        while start < len(token_ids):
            window = token_ids[start : start + self._chunk_size]
            text = self._tokenizer.decode(window, skip_special_tokens=True).strip()
            if text:
                chunks.append(
                    TokenChunk(
                        chunk_id=f"{document.document_id}::{index}",
                        document_id=document.document_id,
                        source=document.source,
                        content=text,
                        token_count=len(window),
                    )
                )
                index += 1
            start += step
        return chunks
