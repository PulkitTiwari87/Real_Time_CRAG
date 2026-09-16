"""Minimal .env loader.

Hand-rolled instead of adding a third-party dependency: the format needed
here (KEY=VALUE per line) is small enough not to justify one. Never prints
or logs the values it loads.
"""
from __future__ import annotations

import os
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_ENV_FILE = _REPO_ROOT / ".env"


def load_dotenv(path: str | Path | None = None) -> None:
    """Populate os.environ from a KEY=VALUE .env file.

    Does not override variables already set in the environment. Silently
    does nothing if the file is absent.
    """
    p = Path(path) if path else _DEFAULT_ENV_FILE
    if not p.is_file():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)
