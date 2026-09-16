"""Document loaders (plain-text, PDF) behind a common BaseLoader interface.

Uses ``pypdf`` rather than the plan's originally-named ``PyPDF2``: PyPDF2 is
deprecated and merged into pypdf by the same maintainer, so pypdf is the
maintained choice for the same functionality.
"""
from __future__ import annotations

import sys
import unicodedata
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


@dataclass(frozen=True)
class Document:
    document_id: str
    source: str
    content: str


@dataclass(frozen=True)
class LoadError:
    path: str
    error: str


def clean_text(text: str) -> str:
    """Normalize unicode and collapse redundant whitespace per line."""
    text = unicodedata.normalize("NFKC", text)
    lines = [" ".join(line.split()) for line in text.splitlines()]
    return "\n".join(line for line in lines if line).strip()


class BaseLoader(ABC):
    @abstractmethod
    def load(self, path: str | Path) -> Document:
        """Load and clean a single document from disk."""

    def load_dir(self, dir_path: str | Path, pattern: str) -> list[Document]:
        """Load every matching file in a directory.

        A single bad file (corrupted PDF, unreadable encoding, etc.) does
        not abort the whole batch: it's skipped, warned about on stderr,
        and recorded in ``self.errors`` so callers can compute an error
        rate, per the phase's "files that fail to load" metric.
        """
        d = Path(dir_path)
        if not d.is_dir():
            raise FileNotFoundError(f"Directory not found: {d}")

        self.errors: list[LoadError] = []
        documents: list[Document] = []
        for p in sorted(d.glob(pattern)):
            try:
                documents.append(self.load(p))
            except (FileNotFoundError, ValueError) as exc:
                self.errors.append(LoadError(path=str(p), error=str(exc)))
                print(f"Warning: skipping {p}: {exc}", file=sys.stderr)
        return documents


class TextLoader(BaseLoader):
    def load(self, path: str | Path) -> Document:
        p = Path(path)
        if not p.is_file():
            raise FileNotFoundError(f"Document not found: {p}")
        content = clean_text(p.read_text(encoding="utf-8"))
        if not content:
            raise ValueError(f"Document is empty after cleaning: {p}")
        return Document(document_id=p.stem, source=str(p), content=content)

    def load_dir(self, dir_path: str | Path, pattern: str = "*.txt") -> list[Document]:
        return super().load_dir(dir_path, pattern)


class PDFLoader(BaseLoader):
    def load(self, path: str | Path) -> Document:
        p = Path(path)
        if not p.is_file():
            raise FileNotFoundError(f"Document not found: {p}")
        try:
            reader = PdfReader(str(p))
            raw = "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as exc:
            raise ValueError(f"Could not read PDF: {p}: {exc}") from exc
        content = clean_text(raw)
        if not content:
            raise ValueError(f"PDF produced no extractable text: {p}")
        return Document(document_id=p.stem, source=str(p), content=content)

    def load_dir(self, dir_path: str | Path, pattern: str = "*.pdf") -> list[Document]:
        return super().load_dir(dir_path, pattern)
