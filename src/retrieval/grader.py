"""Lightweight, non-trained relevance grader.

Per this phase's own non-scope ("Training custom ranking models"), this
grader does not train a classifier. It blends the retriever's vector
similarity score with a simple lexical-overlap heuristic into a single
confidence score, thresholded into GOOD/BAD -- the signal Phase 07's CRAG
loop will consume to decide whether to rewrite the query and retry.

DEFAULT_CONFIDENCE_THRESHOLD=0.35 (see docs/experiments/phase04-grader-calibration.md):
an earlier value of 0.55 was picked from a benchmark of only short,
single-topic sentences, where correct matches score high. It caused a real
false negative in manual pipeline testing on a realistic longer chunk (a
multi-step description), where the genuinely correct match scored only
0.391 -- diluted by covering several sub-topics, not just the one asked
about. 0.35 sits at the midpoint between the highest observed
incorrect-pair confidence (0.277) and the lowest observed correct-pair
confidence (0.391) on a benchmark that includes that exact real case.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .retriever import RetrievalResult

DEFAULT_CONFIDENCE_THRESHOLD = 0.35
DEFAULT_SIMILARITY_WEIGHT = 0.7


class Grade(str, Enum):
    GOOD = "GOOD"
    BAD = "BAD"


@dataclass(frozen=True)
class GradedResult:
    chunk_id: str
    content: str
    similarity_score: float
    lexical_overlap: float
    confidence: float
    grade: Grade
    document_id: str = ""
    source: str = ""


def _lexical_overlap(query: str, content: str) -> float:
    query_terms = set(query.lower().split())
    if not query_terms:
        return 0.0
    content_terms = set(content.lower().split())
    return len(query_terms & content_terms) / len(query_terms)


def grade_one(
    query: str,
    chunk_id: str,
    content: str,
    similarity_score: float,
    threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
    similarity_weight: float = DEFAULT_SIMILARITY_WEIGHT,
    document_id: str = "",
    source: str = "",
) -> GradedResult:
    overlap = _lexical_overlap(query, content)
    normalized_similarity = max(0.0, min(1.0, similarity_score))
    confidence = similarity_weight * normalized_similarity + (1 - similarity_weight) * overlap
    grade_value = Grade.GOOD if confidence >= threshold else Grade.BAD
    return GradedResult(
        chunk_id=chunk_id,
        content=content,
        similarity_score=similarity_score,
        lexical_overlap=overlap,
        confidence=confidence,
        grade=grade_value,
        document_id=document_id,
        source=source,
    )


def grade_results(
    query: str,
    results: list[RetrievalResult],
    threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
    similarity_weight: float = DEFAULT_SIMILARITY_WEIGHT,
) -> list[GradedResult]:
    return [
        grade_one(
            query,
            r.chunk_id,
            r.content,
            r.score,
            threshold=threshold,
            similarity_weight=similarity_weight,
            document_id=r.document_id,
            source=r.source,
        )
        for r in results
    ]
