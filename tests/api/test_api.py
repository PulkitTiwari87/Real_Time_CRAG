import pytest
from fastapi.testclient import TestClient

from api.main import app


@pytest.fixture(scope="module")
def client(tmp_path_factory, monkeypatch_module):
    # Isolated storage per test module run, not the shared local_vector_store/
    # every CLI demo uses -- otherwise re-running tests accumulates state.
    monkeypatch_module.setenv("API_VECTOR_DB_PATH", str(tmp_path_factory.mktemp("api_store")))
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def monkeypatch_module():
    from _pytest.monkeypatch import MonkeyPatch

    mp = MonkeyPatch()
    yield mp
    mp.undo()


def test_metrics_endpoint_is_prometheus_scrapeable(client):
    client.get("/health")  # generate at least one data point
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "rag_api_requests_total" in response.text


def test_security_headers_present(client):
    response = client.get("/health")
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"


def test_frontend_served_at_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Real-Time Corrective RAG" in response.text


def test_health_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["collection_count"] == 0


def test_ingest_indexes_content(client):
    response = client.post(
        "/ingest",
        json={"document_id": "doc1", "content": "The sky is blue and the grass is green."},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["chunks_indexed"] >= 1

    health = client.get("/health").json()
    assert health["collection_count"] >= 1


def test_ingest_empty_content_returns_400(client):
    response = client.post("/ingest", json={"document_id": "doc2", "content": "   "})
    assert response.status_code == 400
    # No internal stack trace or implementation detail leaked.
    assert "traceback" not in response.text.lower()


def test_ingest_missing_fields_returns_422_validation_error(client):
    response = client.post("/ingest", json={"document_id": "doc3"})  # missing content
    assert response.status_code == 422


def test_query_too_long_returns_422(client):
    response = client.post("/query", json={"query": "x" * 5000})
    assert response.status_code == 422


def test_query_against_indexed_content_returns_grounded_answer(client, monkeypatch):
    # Mocked provider, not live Gemini: live generation is already proven
    # end-to-end elsewhere (Phases 01/05/07/08/13's own manual verification);
    # this test's job is the API/HTTP wiring, and depending on live external
    # quota here made the permanent suite flaky (hit a real 429 rate limit
    # from the volume of live calls made across this session's testing).
    class _FakeProvider:
        model_name = "fake-model"

        def generate(self, prompt: str) -> str:
            return "Qdrant is a vector database for similarity search [1]."

    monkeypatch.setattr("generation.pipeline.get_provider", lambda name=None: _FakeProvider())
    # Also cover the rewrite path (used only if grading comes back BAD) so
    # this test has zero live-network dependency either way.
    monkeypatch.setattr("corrective.rewriter.get_provider", lambda name=None: _FakeProvider())

    client.post(
        "/ingest",
        json={"document_id": "facts1", "content": "Qdrant is an open-source vector database for similarity search."},
    )
    response = client.post("/query", json={"query": "What is Qdrant?"})
    assert response.status_code == 200
    body = response.json()
    assert "answer" in body
    assert isinstance(body["citations"], list)
    assert isinstance(body["abstained"], bool)


def test_query_with_unknown_provider_name_returns_503_not_stack_trace(client):
    client.post("/ingest", json={"document_id": "d1", "content": "some real content about testing"})
    response = client.post("/query", json={"query": "some real content", "provider": "not-a-real-provider"})
    assert response.status_code == 503
    assert "traceback" not in response.text.lower()
    assert "not-a-real-provider" not in response.text  # error is generic, doesn't echo internals
