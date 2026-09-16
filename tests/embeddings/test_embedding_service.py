from embeddings.embedding_service import EmbeddingService


def test_embed_returns_vector_of_expected_dimension():
    service = EmbeddingService()
    vector = service.embed("hello world")
    assert isinstance(vector, list)
    assert len(vector) == service.dimension
    assert all(isinstance(x, float) for x in vector)


def test_embed_is_deterministic():
    service = EmbeddingService()
    v1 = service.embed("the sky is blue")
    v2 = service.embed("the sky is blue")
    assert v1 == v2


def test_embed_batch_matches_input_count_and_order():
    service = EmbeddingService()
    texts = ["one", "two", "three"]
    vectors = service.embed_batch(texts)
    assert len(vectors) == 3
    # Batch vs. single-item encoding can differ in the ~6th decimal place due to
    # batched-vs-unbatched floating point paths in the underlying model (padding,
    # kernel selection); they are not bit-identical, only numerically equivalent.
    single = service.embed("one")
    assert all(abs(a - b) < 1e-4 for a, b in zip(vectors[0], single))


def test_embed_batch_empty_returns_empty():
    service = EmbeddingService()
    assert service.embed_batch([]) == []
