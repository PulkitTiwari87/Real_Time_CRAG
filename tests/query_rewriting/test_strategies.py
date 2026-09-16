from query_rewriting.strategies import deterministic_rewrite


def test_deterministic_rewrite_strips_stopwords_and_question_words():
    result = deterministic_rewrite("What is the capital of France?")
    words = result.split()
    assert "what" not in words
    assert "is" not in words
    assert "the" not in words
    assert "of" not in words
    assert "capital" in words
    assert "france" in words


def test_deterministic_rewrite_strips_punctuation():
    result = deterministic_rewrite("Where's the nearest coffee shop, please?")
    assert "?" not in result
    assert "," not in result
    assert "'" not in result


def test_deterministic_rewrite_falls_back_to_original_if_all_stopwords():
    result = deterministic_rewrite("what is the")
    assert result == "what is the"


def test_deterministic_rewrite_is_deterministic():
    q = "How do plants convert sunlight into energy?"
    assert deterministic_rewrite(q) == deterministic_rewrite(q)
