"""Kafka producer for ingestion events.

Publishes RawItems onto the ingestion topic so a separate consumer
process can pick them up.
"""
from __future__ import annotations

from kafka import KafkaProducer
from kafka.errors import KafkaError

from ingestion.producer import RawItem

from .schemas import serialize_raw_item
from .topics import INGESTION_TOPIC


class StreamingProducerError(RuntimeError):
    """Raised when the producer cannot connect to Kafka or publish a message."""


class IngestionStreamProducer:
    def __init__(
        self, bootstrap_servers: str, topic: str = INGESTION_TOPIC, connect_timeout_ms: int = 5000
    ) -> None:
        """connect_timeout_ms bounds connection/API-version-detection setup.

        Found during testing: KafkaProducer's defaults do not fail fast
        against an unreachable broker -- a real test against a bad address
        took 26 minutes to raise instead of the expected ~10s, evidently
        retrying API-version auto-detection well past any per-call timeout.
        Passing an explicit api_version skips that auto-detection
        handshake entirely, and short request_timeout_ms/max_block_ms/
        reconnect_backoff_max_ms bound everything else -- so a genuinely
        unreachable broker fails within a few seconds, not tens of minutes.
        """
        self._topic = topic
        try:
            self._producer = KafkaProducer(
                bootstrap_servers=bootstrap_servers,
                value_serializer=serialize_raw_item,
                key_serializer=lambda k: k.encode("utf-8") if k else None,
                acks="all",
                retries=3,
                api_version=(2, 5, 0),
                request_timeout_ms=connect_timeout_ms,
                max_block_ms=connect_timeout_ms,
                reconnect_backoff_ms=100,
                reconnect_backoff_max_ms=1000,
            )
        except KafkaError as exc:
            raise StreamingProducerError(f"Could not connect to Kafka at {bootstrap_servers}: {exc}") from exc

    def publish(self, item: RawItem) -> None:
        try:
            future = self._producer.send(self._topic, key=item.source_id, value=item)
            future.get(timeout=10)
        except KafkaError as exc:
            raise StreamingProducerError(f"Failed to publish {item.source_id}: {exc}") from exc

    def publish_many(self, items: list[RawItem]) -> None:
        for item in items:
            self.publish(item)

    def close(self) -> None:
        self._producer.flush()
        self._producer.close()
