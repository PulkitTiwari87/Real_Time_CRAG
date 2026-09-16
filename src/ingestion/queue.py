"""In-process ingestion queue.

Deliberately NOT a distributed/persistent queue -- that is Phase 11's job
(Kafka). This is the minimal producer/consumer decoupling needed to model
the ingestion architecture (RSS -> Producer -> queue -> Consumer -> ...)
without duplicating Kafka functionality early.
"""
from __future__ import annotations

import queue as _queue
from dataclasses import dataclass

from .producer import RawItem


@dataclass(frozen=True)
class QueueStats:
    enqueued: int
    dequeued: int


class IngestionQueue:
    def __init__(self) -> None:
        self._queue: _queue.Queue = _queue.Queue()
        self._enqueued = 0
        self._dequeued = 0

    def put(self, item: RawItem) -> None:
        self._queue.put(item)
        self._enqueued += 1

    def put_many(self, items: list[RawItem]) -> None:
        for item in items:
            self.put(item)

    def get_all(self) -> list[RawItem]:
        """Drain the queue: the consumer pulls everything currently available."""
        items = []
        while not self._queue.empty():
            items.append(self._queue.get_nowait())
            self._dequeued += 1
        return items

    @property
    def stats(self) -> QueueStats:
        return QueueStats(enqueued=self._enqueued, dequeued=self._dequeued)
