#!/usr/bin/env python
"""Phase 05 end-to-end demo using the mature pipeline (Phases 02-05):

load -> chunk -> embed -> index (Qdrant) -> retrieve (vector+BM25) ->
grade -> generate grounded answer with citations.

Supersedes scripts/run_rag_baseline.py's simpler Phase 01 path for actual
use; that script is kept as the original baseline artifact.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from document_processing import Chunker, TextLoader
from embeddings import EmbeddingService, VectorStore
from generation import GenerationError, generate_grounded_answer
from retrieval import Retriever, grade_results


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Phase 05 grounded RAG pipeline.")
    parser.add_argument("--doc", required=True, help="Path to a .txt file or directory")
    parser.add_argument("--query", required=True)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--chunk-size", type=int, default=200, help="Chunk size in tokens")
    parser.add_argument("--overlap", type=int, default=20, help="Overlap in tokens")
    parser.add_argument("--provider", default=None, help="'ollama' or 'gemini' (default: LLM_PROVIDER env var)")
    parser.add_argument("--collection", default="pipeline_demo")
    args = parser.parse_args()

    loader = TextLoader()
    doc_path = Path(args.doc)
    documents = loader.load_dir(doc_path) if doc_path.is_dir() else [loader.load(doc_path)]

    chunker = Chunker(chunk_size=args.chunk_size, overlap=args.overlap)
    chunks = [c for doc in documents for c in chunker.chunk(doc)]
    if not chunks:
        print("No chunks produced.", file=sys.stderr)
        return 1

    embedder = EmbeddingService()
    store = VectorStore(collection_name=args.collection, vector_size=embedder.dimension)
    try:
        for c in chunks:
            store.upsert(
                chunk_id=c.chunk_id,
                document_id=c.document_id,
                source=c.source,
                content=c.content,
                vector=embedder.embed(c.content),
            )
        print(f"Indexed {len(chunks)} chunk(s) from {len(documents)} document(s).")

        retriever = Retriever(vector_store=store, embedder=embedder)
        results = retriever.retrieve(args.query, top_k=args.top_k)
        print(f"Retrieved {len(results)} chunk(s).")

        graded = grade_results(args.query, results)
        good_count = sum(1 for g in graded if g.grade.value == "GOOD")
        print(f"Graded: {good_count}/{len(graded)} GOOD.")

        try:
            answer = generate_grounded_answer(args.query, graded, provider_name=args.provider)
        except GenerationError as exc:
            print(f"Generation failed: {exc}", file=sys.stderr)
            return 1

        print("\nAnswer:")
        print(answer.answer)
        print(f"\n(used {answer.used_chunk_count} chunk(s), dropped {answer.dropped_chunk_count} as low-confidence)")
        print("\nCitations:")
        for c in answer.citations:
            print(f"  [{c.index}] {c.source}")
        return 0
    finally:
        store.close()


if __name__ == "__main__":
    raise SystemExit(main())
