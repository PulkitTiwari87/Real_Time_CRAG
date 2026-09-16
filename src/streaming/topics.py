"""Kafka topic definitions for the ingestion pipeline."""
from __future__ import annotations

INGESTION_TOPIC = "rag-ingestion-events"
INGESTION_DLQ_TOPIC = "rag-ingestion-events-dlq"  # failed messages, for inspection/replay

DEFAULT_PARTITIONS = 1
DEFAULT_REPLICATION_FACTOR = 1


def ensure_topics(bootstrap_servers: str, topics: list[str] | None = None) -> None:
    """Create the ingestion topics if they don't already exist (idempotent)."""
    from kafka.admin import KafkaAdminClient, NewTopic
    from kafka.errors import TopicAlreadyExistsError

    topics = topics or [INGESTION_TOPIC, INGESTION_DLQ_TOPIC]
    admin = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
    try:
        new_topics = [
            NewTopic(name=t, num_partitions=DEFAULT_PARTITIONS, replication_factor=DEFAULT_REPLICATION_FACTOR)
            for t in topics
        ]
        try:
            admin.create_topics(new_topics=new_topics, validate_only=False)
        except TopicAlreadyExistsError:
            pass
    finally:
        admin.close()
