from ingestion.producer import RawItem
from streaming.schemas import deserialize_raw_item, serialize_raw_item


def test_serialize_deserialize_round_trip():
    item = RawItem(
        source_id="a1", title="Title", summary="Summary text", link="https://x.com/a1",
        published_at="2024-01-01T00:00:00+00:00",
    )
    data = serialize_raw_item(item)
    assert isinstance(data, bytes)
    restored = deserialize_raw_item(data)
    assert restored == item


def test_serialize_deserialize_handles_none_published_at():
    item = RawItem(source_id="a2", title="T", summary="S", link="L", published_at=None)
    restored = deserialize_raw_item(serialize_raw_item(item))
    assert restored.published_at is None
