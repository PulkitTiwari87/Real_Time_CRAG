"""Phase 13: Pydantic request/response schemas for the API."""
from __future__ import annotations

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)
    max_retries: int = Field(default=2, ge=0, le=5)
    provider: str | None = None


class CitationResponse(BaseModel):
    index: int
    source: str


class QueryResponse(BaseModel):
    answer: str
    citations: list[CitationResponse]
    rewrite_count: int
    abstained: bool
    latency_ms: float


class IngestTextRequest(BaseModel):
    document_id: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1, max_length=50000)
    published_at: str | None = None


class IngestResponse(BaseModel):
    chunks_indexed: int


class HealthResponse(BaseModel):
    status: str
    collection_count: int
