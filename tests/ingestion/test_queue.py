from ingestion.producer import RawItem
from ingestion.queue import IngestionQueue


def _item(source_id="a"):
    return RawItem(source_id=source_id, title="t", summary="s", link="l", published_at=None)


def test_put_and_get_all_returns_all_items_in_order():
    q = IngestionQueue()
    q.put(_item("a"))
    q.put(_item("b"))
    items = q.get_all()
    assert [i.source_id for i in items] == ["a", "b"]


def test_get_all_drains_the_queue():
    q = IngestionQueue()
    q.put_many([_item("a"), _item("b")])
    q.get_all()
    assert q.get_all() == []  # already drained


def test_stats_tracks_enqueued_and_dequeued():
    q = IngestionQueue()
    q.put_many([_item("a"), _item("b"), _item("c")])
    q.get_all()
    assert q.stats.enqueued == 3
    assert q.stats.dequeued == 3
