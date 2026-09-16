"""Phase 13: FastAPI interface over the completed CRAG backend.

Error responses are deliberately generic (no stack traces, provider
internals, or file paths in the client-facing detail) -- full details are
logged server-side only. Input is bounded via Pydantic field constraints
(length/range limits) as the appropriate security control for this phase;
this is a local-first, single-tenant service, so auth/rate-limiting would
be security theater here, not a real control -- revisit if/when this is
exposed beyond local use.
"""
from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import FileResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from corrective import run_crag
from document_processing.chunker import Chunker
from document_processing.loader import Document, clean_text
from embeddings import EmbeddingService, VectorStore
from generation import GenerationError
from observability import (
    QUERY_ABSTENTION_COUNT,
    QUERY_LATENCY_SECONDS,
    QUERY_REWRITE_COUNT,
    REQUEST_COUNT,
    configure_logging,
)
from retrieval import Retriever

from .schemas import (
    CitationResponse,
    HealthResponse,
    IngestResponse,
    IngestTextRequest,
    QueryRequest,
    QueryResponse,
)

configure_logging()
logger = logging.getLogger("api")

_state: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    embedder = EmbeddingService()
    # API_VECTOR_DB_PATH lets tests (and alternate deployments) point at an
    # isolated location instead of the shared local_vector_store/ default
    # every CLI script uses -- without it, re-running the test suite
    # accumulates state across runs instead of starting fresh each time.
    store = VectorStore(
        collection_name="api_default",
        vector_size=embedder.dimension,
        qdrant_path=os.environ.get("API_VECTOR_DB_PATH"),
    )
    _state["embedder"] = embedder
    _state["store"] = store
    _state["retriever"] = Retriever(vector_store=store, embedder=embedder)
    _state["chunker"] = Chunker()
    yield
    store.close()
    _state.clear()


app = FastAPI(title="Real-Time Corrective RAG API", version="0.1.0", lifespan=lifespan)


@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    # Minimal, standard headers appropriate for a local-first service with
    # no user-uploaded HTML rendering -- not a substitute for real auth if
    # this is ever exposed beyond local use (see module docstring).
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response


_FRONTEND_PATH = Path(__file__).resolve().parents[2] / "frontend" / "index.html"


@app.get("/")
def frontend() -> FileResponse:
    """Phase 14: the simplest useful interface -- a single static HTML page."""
    return FileResponse(_FRONTEND_PATH)


@app.get("/metrics")
def metrics() -> Response:
    """Phase 15: Prometheus-scrapeable metrics."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    store: VectorStore = _state["store"]
    REQUEST_COUNT.labels(endpoint="/health", status="200").inc()
    return HealthResponse(status="ok", collection_count=store.count())


@app.post("/ingest", response_model=IngestResponse)
def ingest(req: IngestTextRequest) -> IngestResponse:
    content = clean_text(req.content)
    if not content:
        raise HTTPException(status_code=400, detail="content is empty after cleaning")

    doc = Document(document_id=req.document_id, source=req.document_id, content=content)
    chunker: Chunker = _state["chunker"]
    embedder: EmbeddingService = _state["embedder"]
    store: VectorStore = _state["store"]

    chunks = chunker.chunk(doc)
    for c in chunks:
        store.upsert(
            chunk_id=c.chunk_id,
            document_id=c.document_id,
            source=c.source,
            content=c.content,
            vector=embedder.embed(c.content),
            published_at=req.published_at,
        )
    REQUEST_COUNT.labels(endpoint="/ingest", status="200").inc()
    return IngestResponse(chunks_indexed=len(chunks))


@app.post("/query", response_model=QueryResponse)
@QUERY_LATENCY_SECONDS.time()
def query(req: QueryRequest) -> QueryResponse:
    retriever: Retriever = _state["retriever"]
    try:
        result = run_crag(
            req.query, retriever, top_k=req.top_k, max_retries=req.max_retries, provider_name=req.provider
        )
    except GenerationError as exc:
        logger.warning("generation failed: %s", exc)
        REQUEST_COUNT.labels(endpoint="/query", status="503").inc()
        raise HTTPException(
            status_code=503, detail="The language model backend is currently unavailable."
        ) from exc
    except Exception:
        logger.exception("unexpected error handling query")
        REQUEST_COUNT.labels(endpoint="/query", status="500").inc()
        raise HTTPException(status_code=500, detail="Internal error processing the query.")

    REQUEST_COUNT.labels(endpoint="/query", status="200").inc()
    if result.rewrite_count:
        QUERY_REWRITE_COUNT.inc(result.rewrite_count)
    if result.abstained:
        QUERY_ABSTENTION_COUNT.inc()

    return QueryResponse(
        answer=result.answer.answer,
        citations=[CitationResponse(index=c.index, source=c.source) for c in result.answer.citations],
        rewrite_count=result.rewrite_count,
        abstained=result.abstained,
        latency_ms=result.total_latency_ms,
    )
