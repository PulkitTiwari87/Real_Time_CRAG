"""Plain-text document loading for the RAG baseline pipeline."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Document:
    document_id: str
    source: str
    content: str


def load_text_file(path: str | Path) -> Document:
    """Load a single plain-text document from disk."""
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"Document not found: {p}")
    content = p.read_text(encoding="utf-8")
    if not content.strip():
        raise ValueError(f"Document is empty: {p}")
    return Document(document_id=p.stem, source=str(p), content=content)


def load_text_dir(dir_path: str | Path, pattern: str = "*.txt") -> list[Document]:
    """Load every matching plain-text document from a directory."""
    d = Path(dir_path)
    if not d.is_dir():
        raise FileNotFoundError(f"Directory not found: {d}")
    return [load_text_file(p) for p in sorted(d.glob(pattern))]
