#!/usr/bin/env python
"""Phase 01 end-to-end demo: load -> chunk -> embed -> index -> retrieve -> generate.

Example:
    python scripts/run_rag_baseline.py --doc data/sample.txt --query "What is this about?"
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rag_baseline.chunker import chunk_document
from rag_baseline.generator import GenerationError, generate_answer
from rag_baseline.loader import load_text_dir, load_text_file
from rag_baseline.retriever import Retriever


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Phase 01 RAG baseline demo.")
    parser.add_argument("--doc", required=True, help="Path to a .txt file or a directory of .txt files")
    parser.add_argument("--query", required=True, help="Question to ask")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--chunk-size", type=int, default=500)
    parser.add_argument("--overlap", type=int, default=50)
    parser.add_argument(
        "--provider",
        default=None,
        help="LLM provider override: 'ollama' or 'gemini' (default: LLM_PROVIDER env var, else 'ollama')",
    )
    args = parser.parse_args()

    doc_path = Path(args.doc)
    documents = load_text_dir(doc_path) if doc_path.is_dir() else [load_text_file(doc_path)]

    chunks = [c for doc in documents for c in chunk_document(doc, args.chunk_size, args.overlap)]
    if not chunks:
        print("No chunks produced from input document(s).", file=sys.stderr)
        return 1

    retriever = Retriever()
    try:
        indexed = retriever.index(chunks)
        print(f"Indexed {indexed} chunks from {len(documents)} document(s).")

        results = retriever.retrieve(args.query, top_k=args.top_k)
        print(f"Retrieved {len(results)} chunk(s) for query: {args.query!r}")

        try:
            result = generate_answer(args.query, results, provider_name=args.provider)
        except GenerationError as exc:
            print(f"Generation failed: {exc}", file=sys.stderr)
            return 1

        print("\nAnswer:")
        print(result.answer)
        print("\nSources:")
        for src in result.citations:
            print(f"- {src}")
        return 0
    finally:
        retriever.close()


if __name__ == "__main__":
    raise SystemExit(main())
