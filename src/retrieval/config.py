"""Loader for retrieval_config.yaml."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "retrieval_config.yaml"


def load_retrieval_config(path: str | Path | None = None) -> dict[str, Any]:
    p = Path(path) if path else DEFAULT_CONFIG_PATH
    if not p.is_file():
        raise FileNotFoundError(f"Retrieval config not found: {p}")
    with p.open(encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config or {}
