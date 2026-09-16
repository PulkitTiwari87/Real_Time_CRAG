from streaming.topics import INGESTION_DLQ_TOPIC, INGESTION_TOPIC


def test_topic_names_are_distinct_and_nonempty():
    assert INGESTION_TOPIC
    assert INGESTION_DLQ_TOPIC
    assert INGESTION_TOPIC != INGESTION_DLQ_TOPIC
