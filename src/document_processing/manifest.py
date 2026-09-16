"""JSON manifest I/O for processed chunks, handed off to Phase 03."""
from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from .chunker import TokenChunk


def write_manifest(
    chunks: list[TokenChunk], output_path: str | Path, chunk_size: int, overlap: int
) -> Path:
    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "chunk_size": chunk_size,
        "overlap": overlap,
        "chunk_count": len(chunks),
        "chunks": [asdict(c) for c in chunks],
    }
    p.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return p


def read_manifest(path: str | Path) -> dict:
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"Manifest not found: {p}")
    return json.loads(p.read_text(encoding="utf-8"))
