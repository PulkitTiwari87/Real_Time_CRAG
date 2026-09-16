"""No live Kafka broker is available in this environment (no Docker).

These tests verify the code paths that don't require a real broker:
connection-error handling (a genuinely unreachable bootstrap server address
is used, so KafkaProducer's own connection attempt fails for real -- this
is not mocked). Should fail within ~5s (see connect_timeout_ms in
IngestionStreamProducer -- kafka-python's own defaults were found to take
26 minutes here before that fix). Publish-time behavior against a real
broker is NOT verified here; see infrastructure/docker-compose.kafka.yml
to verify locally with Docker.
"""
import pytest

from ingestion.producer import RawItem
from streaming.producer import IngestionStreamProducer, StreamingProducerError


def test_producer_raises_clean_error_when_broker_unreachable():
    with pytest.raises(StreamingProducerError):
        producer = IngestionStreamProducer(bootstrap_servers="127.0.0.1:1")
        producer.publish(RawItem(source_id="a", title="t", summary="s", link="l", published_at=None))
