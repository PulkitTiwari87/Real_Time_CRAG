from observability.metrics import QUERY_ABSTENTION_COUNT, QUERY_LATENCY_SECONDS, QUERY_REWRITE_COUNT, REQUEST_COUNT


def test_request_count_increments():
    before = REQUEST_COUNT.labels(endpoint="/test-metric", status="200")._value.get()
    REQUEST_COUNT.labels(endpoint="/test-metric", status="200").inc()
    after = REQUEST_COUNT.labels(endpoint="/test-metric", status="200")._value.get()
    assert after == before + 1


def test_query_latency_histogram_records_observations():
    before = QUERY_LATENCY_SECONDS._sum.get()
    QUERY_LATENCY_SECONDS.observe(0.5)
    after = QUERY_LATENCY_SECONDS._sum.get()
    assert after == before + 0.5


def test_rewrite_and_abstention_counters_are_independent():
    rewrite_before = QUERY_REWRITE_COUNT._value.get()
    abstention_before = QUERY_ABSTENTION_COUNT._value.get()
    QUERY_REWRITE_COUNT.inc()
    assert QUERY_REWRITE_COUNT._value.get() == rewrite_before + 1
    assert QUERY_ABSTENTION_COUNT._value.get() == abstention_before
