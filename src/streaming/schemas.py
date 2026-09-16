"""Kafka message schema for ingestion events.

One JSON object per message, matching ingestion.producer.RawItem's fields
-- Kafka transports RawItems between a producer process and a consumer
process, replacing the in-process queue Phase 10 used as a placeholder.
"""
from __future__ import annotations

import json
from dataclasses import asdict

from ingestion.producer import RawItem


def serialize_raw_item(item: RawItem) -> bytes:
    return json.dumps(asdict(item)).encode("utf-8")


def deserialize_raw_item(data: bytes) -> RawItem:
    payload = json.loads(data.decode("utf-8"))
    return RawItem(**payload)
