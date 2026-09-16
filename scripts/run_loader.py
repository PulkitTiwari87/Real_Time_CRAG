#!/usr/bin/env python
"""Phase 02 CLI: load (text or PDF) -> clean -> token-chunk -> write manifest."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from document_processing import Chunker, PDFLoader, TextLoader, write_manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Phase 02 document processing.")
    parser.add_argument("--doc", required=True, help="Path to a file or a directory")
    parser.add_argument("--type", choices=["text", "pdf"], default="text")
    parser.add_argument("--chunk-size", type=int, default=200, help="Chunk size in tokens")
    parser.add_argument("--overlap", type=int, default=20, help="Overlap in tokens")
    parser.add_argument("--out", default="data/chunks/manifest.json")
    args = parser.parse_args()

    loader = TextLoader() if args.type == "text" else PDFLoader()
    doc_path = Path(args.doc)
    pattern = "*.txt" if args.type == "text" else "*.pdf"
    documents = loader.load_dir(doc_path, pattern) if doc_path.is_dir() else [loader.load(doc_path)]

    chunker = Chunker(chunk_size=args.chunk_size, overlap=args.overlap)
    all_chunks = [c for doc in documents for c in chunker.chunk(doc)]
    if not all_chunks:
        print("No chunks produced.", file=sys.stderr)
        return 1

    out_path = write_manifest(all_chunks, args.out, args.chunk_size, args.overlap)
    print(f"Loaded {len(documents)} document(s), wrote {len(all_chunks)} chunk(s) to {out_path}")

    errors = getattr(loader, "errors", [])
    if errors:
        print(f"{len(errors)} file(s) failed to load and were skipped:", file=sys.stderr)
        for e in errors:
            print(f"  - {e.path}: {e.error}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
