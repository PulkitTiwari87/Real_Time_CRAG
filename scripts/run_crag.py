#!/usr/bin/env python
"""Phase 07 end-to-end CRAG demo: load -> chunk -> embed -> index ->
[retrieve -> grade -> rewrite-and-retry (bounded) -> generate/abstain]."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from corrective import run_crag
from document_processing import Chunker, TextLoader
from embeddings import EmbeddingService, VectorStore
from generation import GenerationError
from retrieval import Retriever


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Phase 07 CRAG pipeline.")
    parser.add_argument("--doc", required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--max-retries", type=int, default=2)
    parser.add_argument("--provider", default=None)
    parser.add_argument("--collection", default="crag_demo")
    args = parser.parse_args()

    loader = TextLoader()
    doc_path = Path(args.doc)
    documents = loader.load_dir(doc_path) if doc_path.is_dir() else [loader.load(doc_path)]

    chunker = Chunker()
    chunks = [c for doc in documents for c in chunker.chunk(doc)]
    if not chunks:
        print("No chunks produced.", file=sys.stderr)
        return 1

    embedder = EmbeddingService()
    store = VectorStore(collection_name=args.collection, vector_size=embedder.dimension)
    try:
        for c in chunks:
            store.upsert(
                chunk_id=c.chunk_id, document_id=c.document_id, source=c.source,
                content=c.content, vector=embedder.embed(c.content),
            )
        print(f"Indexed {len(chunks)} chunk(s).")

        retriever = Retriever(vector_store=store, embedder=embedder)
        try:
            result = run_crag(
                args.query, retriever, top_k=args.top_k, max_retries=args.max_retries, provider_name=args.provider
            )
        except GenerationError as exc:
            print(f"Generation failed: {exc}", file=sys.stderr)
            return 1

        print(f"\nOriginal query: {result.original_query}")
        if result.rewrite_count:
            print(f"Final query (after {result.rewrite_count} rewrite(s)): {result.final_query}")
        print(f"Recovered by rewrite: {result.recovered_by_rewrite}")
        print(f"Abstained: {result.abstained}")
        print(f"Total latency: {result.total_latency_ms:.0f} ms")
        print(f"\nAnswer:\n{result.answer.answer}")
        print("\nCitations:")
        for c in result.answer.citations:
            print(f"  [{c.index}] {c.source}")
        return 0
    finally:
        store.close()


if __name__ == "__main__":
    raise SystemExit(main())
