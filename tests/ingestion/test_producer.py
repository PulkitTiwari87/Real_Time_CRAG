from ingestion.producer import parse_rss

SAMPLE_FEED = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
<title>Test Feed</title>
<item>
<title>First Article</title>
<link>https://example.com/first</link>
<description>This is the first article about testing RSS feeds.</description>
<pubDate>Mon, 01 Jan 2024 12:00:00 GMT</pubDate>
<guid>https://example.com/first</guid>
</item>
<item>
<title>Second Article</title>
<link>https://example.com/second</link>
<description>This is the second article about something else entirely.</description>
<pubDate>Tue, 02 Jan 2024 12:00:00 GMT</pubDate>
<guid>https://example.com/second</guid>
</item>
</channel>
</rss>
"""


def test_parse_rss_extracts_all_items():
    items = parse_rss(SAMPLE_FEED)
    assert len(items) == 2
    assert items[0].title == "First Article"
    assert items[0].link == "https://example.com/first"
    assert "first article" in items[0].summary.lower()
    assert items[0].source_id == "https://example.com/first"


def test_parse_rss_extracts_published_date_as_iso8601():
    items = parse_rss(SAMPLE_FEED)
    assert items[0].published_at is not None
    assert items[0].published_at.startswith("2024-01-01")


def test_parse_rss_empty_feed_returns_empty_list():
    empty_feed = '<?xml version="1.0"?><rss version="2.0"><channel><title>Empty</title></channel></rss>'
    assert parse_rss(empty_feed) == []


def test_parse_rss_malformed_content_does_not_crash():
    # feedparser is lenient by design; malformed input should yield an empty
    # or partial result, not raise.
    items = parse_rss("this is not xml at all")
    assert isinstance(items, list)
