"""Kafka consumer for ingestion events.

Consumes RawItems from the ingestion topic and hands them to Phase 10's
IngestionConsumer (normalize -> chunk -> embed -> index). Malformed or
failed messages are sent to a dead-letter topic rather than crashing the
consumer loop or being silently dropped, so they can be inspected/replayed.
Offsets are committed manually, only after a message is processed or
dead-lettered -- never before, so a crash mid-processing causes at-most a
reprocess on restart, never silent data loss.
"""
from __future__ import annotations

from dataclasses import dataclass

from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError

from embeddings.embedding_service import EmbeddingService
from embeddings.vector_store import VectorStore
from ingestion.consumer import IngestionConsumer

from .schemas import deserialize_raw_item, serialize_raw_item
from .topics import INGESTION_DLQ_TOPIC, INGESTION_TOPIC


class StreamingConsumerError(RuntimeError):
    """Raised when the consumer cannot connect to Kafka."""


@dataclass(frozen=True)
class StreamConsumeStats:
    messages_consumed: int
    chunks_indexed: int
    dead_lettered: int


class IngestionStreamConsumer:
    def __init__(
        self,
        bootstrap_servers: str,
        vector_store: VectorStore,
        embedder: EmbeddingService,
        topic: str = INGESTION_TOPIC,
        group_id: str = "rag-ingestion-consumer",
    ) -> None:
        # api_version pinned and short timeouts throughout: see the matching
        # comment in producer.py -- kafka-python's defaults were found (in
        # live testing) to take 26 minutes to fail against an unreachable
        # broker instead of a few seconds.
        try:
            self._consumer = KafkaConsumer(
                topic,
                bootstrap_servers=bootstrap_servers,
                group_id=group_id,
                value_deserializer=deserialize_raw_item,
                auto_offset_reset="earliest",
                enable_auto_commit=False,
                consumer_timeout_ms=5000,
                api_version=(2, 5, 0),
                request_timeout_ms=5000,
                reconnect_backoff_ms=100,
                reconnect_backoff_max_ms=1000,
            )
            self._dlq_producer = KafkaProducer(
                bootstrap_servers=bootstrap_servers,
                value_serializer=serialize_raw_item,
                api_version=(2, 5, 0),
                request_timeout_ms=5000,
                max_block_ms=5000,
                reconnect_backoff_ms=100,
                reconnect_backoff_max_ms=1000,
            )
        except KafkaError as exc:
            raise StreamingConsumerError(f"Could not connect to Kafka at {bootstrap_servers}: {exc}") from exc
        self._ingestion_consumer = IngestionConsumer(vector_store=vector_store, embedder=embedder)

    def consume_available(self) -> StreamConsumeStats:
        """Consume all currently-available messages (bounded by
        consumer_timeout_ms), process each, and commit offsets only after
        each message is handled (successfully or dead-lettered)."""
        messages_consumed = 0
        chunks_indexed = 0
        dead_lettered = 0

        for message in self._consumer:
            messages_consumed += 1
            try:
                stats = self._ingestion_consumer.process([message.value])
                chunks_indexed += stats.chunks_indexed
                if stats.errors:
                    self._dlq_producer.send(INGESTION_DLQ_TOPIC, value=message.value)
                    dead_lettered += 1
                self._consumer.commit()
            except Exception:
                self._dlq_producer.send(INGESTION_DLQ_TOPIC, value=message.value)
                dead_lettered += 1
                self._consumer.commit()

        return StreamConsumeStats(
            messages_consumed=messages_consumed, chunks_indexed=chunks_indexed, dead_lettered=dead_lettered
        )

    def close(self) -> None:
        self._dlq_producer.close()
        self._consumer.close()
