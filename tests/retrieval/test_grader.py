from retrieval.grader import DEFAULT_CONFIDENCE_THRESHOLD, Grade, grade_one


def test_high_similarity_and_overlap_grades_good():
    result = grade_one(
        query="what color is the sky",
        chunk_id="c1",
        content="the sky is blue and the color is vivid",
        similarity_score=0.9,
    )
    assert result.grade == Grade.GOOD
    assert result.confidence > DEFAULT_CONFIDENCE_THRESHOLD


def test_low_similarity_and_no_overlap_grades_bad():
    result = grade_one(
        query="what color is the sky",
        chunk_id="c1",
        content="mitochondria produce ATP through respiration",
        similarity_score=0.05,
    )
    assert result.grade == Grade.BAD


def test_confidence_blends_similarity_and_overlap():
    # Same similarity score, different lexical overlap -> different confidence.
    high_overlap = grade_one("blue sky color", "c1", "blue sky color today", similarity_score=0.5)
    low_overlap = grade_one("blue sky color", "c2", "completely unrelated text here", similarity_score=0.5)
    assert high_overlap.confidence > low_overlap.confidence


def test_threshold_is_configurable():
    result_default = grade_one("test query", "c1", "test query match", similarity_score=0.5, threshold=0.9)
    assert result_default.grade == Grade.BAD  # high bar not met

    result_lenient = grade_one("test query", "c1", "test query match", similarity_score=0.5, threshold=0.1)
    assert result_lenient.grade == Grade.GOOD  # low bar easily met


def test_diluted_multi_topic_chunk_still_grades_good():
    """Regression test for a real bug found in manual Phase 05 pipeline testing.

    A chunk covering several sub-topics (loading, chunking, embedding,
    storage, retrieval, generation) has its embedding diluted relative to
    any single fact within it, so real cosine similarity for a genuinely
    correct match came out to only 0.376 -- not the 0.55 threshold this
    project started with (see docs/experiments/phase04-grader-calibration.md).
    Uses the real, observed similarity score, not a synthetic one.
    """
    result = grade_one(
        query="What does the system store in Qdrant?",
        chunk_id="c1",
        content=(
            "the real - time corrective rag intelligence platform is a fault - tolerant, "
            "production - oriented retrieval - augmented generation system. it ingests "
            "documents, chunks them, embeds the chunks locally, and stores the vectors in "
            "qdrant. when a user asks a question, the system retrieves the most relevant "
            "chunks and asks a local language model to answer using only that retrieved "
            "context, citing its sources."
        ),
        similarity_score=0.3755126423777709,  # the real value observed for this exact pair
    )
    assert result.grade == Grade.GOOD
