"""Retrieval and generation evaluation metrics.

Hand-rolled against well-known formulas (verified against known values in
tests/evaluation/test_metrics.py) rather than adding new dependencies for
each one. Faithfulness is a lexical-overlap proxy (fraction of the
answer's content words grounded in the cited context), not an NLI/LLM
factuality classifier -- keeping this a metric, not a new model, per this
phase's own non-scope ("custom metric research beyond listed metrics").
"""
from __future__ import annotations

import math
from collections import Counter

# ---- Retrieval metrics ----


def recall_at_k(retrieved_ids: list[str], relevant_ids: set[str], k: int) -> float:
    if not relevant_ids:
        return 0.0
    top_k = set(retrieved_ids[:k])
    return len(top_k & relevant_ids) / len(relevant_ids)


def precision_at_k(retrieved_ids: list[str], relevant_ids: set[str], k: int) -> float:
    top_k = retrieved_ids[:k]
    if not top_k:
        return 0.0
    hits = sum(1 for doc_id in top_k if doc_id in relevant_ids)
    return hits / len(top_k)


def mrr(retrieved_ids: list[str], relevant_ids: set[str]) -> float:
    for rank, doc_id in enumerate(retrieved_ids, start=1):
        if doc_id in relevant_ids:
            return 1.0 / rank
    return 0.0


def ndcg_at_k(retrieved_ids: list[str], relevant_ids: set[str], k: int) -> float:
    dcg = 0.0
    for i, doc_id in enumerate(retrieved_ids[:k], start=1):
        rel = 1.0 if doc_id in relevant_ids else 0.0
        dcg += rel / math.log2(i + 1)
    ideal_hits = min(len(relevant_ids), k)
    idcg = sum(1.0 / math.log2(i + 1) for i in range(1, ideal_hits + 1))
    return dcg / idcg if idcg > 0 else 0.0


# ---- Generation metrics ----


def _tokenize(text: str) -> list[str]:
    return text.lower().split()


def _ngrams(tokens: list[str], n: int) -> Counter:
    return Counter(tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1))


def bleu(candidate: str, reference: str, max_n: int = 4) -> float:
    """Sentence-level BLEU: equal n-gram weights (1..max_n) + brevity penalty."""
    cand_tokens = _tokenize(candidate)
    ref_tokens = _tokenize(reference)
    if not cand_tokens:
        return 0.0

    precisions = []
    for n in range(1, max_n + 1):
        cand_ngrams = _ngrams(cand_tokens, n)
        ref_ngrams = _ngrams(ref_tokens, n)
        if not cand_ngrams:
            precisions.append(0.0)
            continue
        overlap = sum(min(count, ref_ngrams.get(ng, 0)) for ng, count in cand_ngrams.items())
        precisions.append(overlap / sum(cand_ngrams.values()))

    if any(p == 0 for p in precisions):
        geo_mean = 0.0
    else:
        geo_mean = math.exp(sum(math.log(p) for p in precisions) / len(precisions))

    if len(cand_tokens) > len(ref_tokens):
        bp = 1.0
    elif len(cand_tokens) == 0:
        bp = 0.0
    else:
        bp = math.exp(1 - len(ref_tokens) / len(cand_tokens))
    return bp * geo_mean


def _lcs_length(a: list[str], b: list[str]) -> int:
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[len(a)][len(b)]


def rouge_l(candidate: str, reference: str) -> float:
    """ROUGE-L F1, based on the longest common subsequence."""
    cand_tokens = _tokenize(candidate)
    ref_tokens = _tokenize(reference)
    if not cand_tokens or not ref_tokens:
        return 0.0
    lcs_len = _lcs_length(cand_tokens, ref_tokens)
    precision = lcs_len / len(cand_tokens)
    recall = lcs_len / len(ref_tokens)
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def faithfulness(answer: str, context: str) -> float:
    """Fraction of the answer's distinct content words that appear in the
    cited context -- a lexical-grounding proxy, not a factuality classifier."""
    answer_terms = set(_tokenize(answer))
    if not answer_terms:
        return 0.0
    context_terms = set(_tokenize(context))
    return len(answer_terms & context_terms) / len(answer_terms)


def citation_accuracy(cited_sources: list[str], expected_sources: set[str]) -> float:
    """Fraction of citations that point to an expected/correct source."""
    if not cited_sources:
        return 0.0
    correct = sum(1 for s in cited_sources if s in expected_sources)
    return correct / len(cited_sources)
