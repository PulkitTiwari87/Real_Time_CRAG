"""Phase 11: Kafka-backed ingestion streaming, replacing Phase 10's in-process queue placeholder."""
from .consumer import IngestionStreamConsumer, StreamConsumeStats, StreamingConsumerError
from .producer import IngestionStreamProducer, StreamingProducerError
from .schemas import deserialize_raw_item, serialize_raw_item
from .topics import INGESTION_DLQ_TOPIC, INGESTION_TOPIC, ensure_topics

__all__ = [
    "IngestionStreamProducer",
    "StreamingProducerError",
    "IngestionStreamConsumer",
    "StreamConsumeStats",
    "StreamingConsumerError",
    "serialize_raw_item",
    "deserialize_raw_item",
    "INGESTION_TOPIC",
    "INGESTION_DLQ_TOPIC",
    "ensure_topics",
]
