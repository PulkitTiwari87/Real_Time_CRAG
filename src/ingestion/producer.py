"""Phase 10: RSS/API ingestion source.

Fetches raw items (title, link, published date, summary) from an RSS/Atom
feed. Uses feedparser (well-established, purpose-built for real-world feed
format variations) rather than hand-rolling XML parsing.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime, timezone

import feedparser


@dataclass(frozen=True)
class RawItem:
    source_id: str
    title: str
    summary: str
    link: str
    published_at: str | None


def parse_rss(feed_content_or_url: str) -> list[RawItem]:
    """Parse an RSS/Atom feed from a URL or a raw feed content string."""
    parsed = feedparser.parse(feed_content_or_url)
    items = []
    for entry in parsed.entries:
        source_id = entry.get("id") or entry.get("link") or entry.get("title", "")
        published_at = None
        if getattr(entry, "published_parsed", None):
            published_at = datetime.fromtimestamp(
                time.mktime(entry.published_parsed), tz=timezone.utc
            ).isoformat()
        items.append(
            RawItem(
                source_id=source_id,
                title=entry.get("title", ""),
                summary=entry.get("summary", ""),
                link=entry.get("link", ""),
                published_at=published_at,
            )
        )
    return items
