import math

import pytest

from evaluation.metrics import (
    bleu,
    citation_accuracy,
    faithfulness,
    mrr,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
    rouge_l,
)


def test_recall_at_k_known_value():
    # 1 of 2 relevant docs found in top 2 -> 0.5
    assert recall_at_k(["a", "b", "c"], {"b", "d"}, k=2) == 0.5


def test_recall_at_k_no_relevant_returns_zero():
    assert recall_at_k(["a", "b"], set(), k=2) == 0.0


def test_precision_at_k_known_value():
    # 1 of top-2 retrieved is relevant -> 0.5
    assert precision_at_k(["a", "b", "c"], {"b", "d"}, k=2) == 0.5


def test_mrr_known_value():
    # relevant doc "b" is at rank 2 -> 1/2
    assert mrr(["a", "b", "c"], {"b"}) == 0.5


def test_mrr_no_relevant_found_returns_zero():
    assert mrr(["a", "b"], {"z"}) == 0.0


def test_ndcg_at_k_known_value():
    # relevant "b" at rank 2 of 3: dcg = 1/log2(3); ideal (relevant at rank 1): idcg = 1/log2(2) = 1
    expected = (1.0 / math.log2(3)) / 1.0
    assert ndcg_at_k(["a", "b", "c"], {"b"}, k=3) == pytest.approx(expected)


def test_ndcg_at_k_perfect_ranking_is_one():
    assert ndcg_at_k(["a", "b"], {"a"}, k=2) == pytest.approx(1.0)


def test_bleu_identical_sentences_is_one():
    text = "the cat is on the mat"
    assert bleu(text, text) == pytest.approx(1.0)


def test_bleu_completely_different_is_zero():
    assert bleu("apple banana cherry date", "the cat is on the mat") == 0.0


def test_rouge_l_identical_sentences_is_one():
    text = "the cat is on the mat"
    assert rouge_l(text, text) == pytest.approx(1.0)


def test_rouge_l_known_value():
    # LCS("the cat sat", "the cat is on the mat") = ["the", "cat"] -> len 2
    # precision = 2/3, recall = 2/6, F1 = 2*P*R/(P+R)
    p, r = 2 / 3, 2 / 6
    expected = 2 * p * r / (p + r)
    assert rouge_l("the cat sat", "the cat is on the mat") == pytest.approx(expected)


def test_faithfulness_fully_grounded_is_one():
    assert faithfulness("the sky is blue", "the sky is blue and clear") == pytest.approx(1.0)


def test_faithfulness_partially_grounded_known_value():
    # answer terms {paris, is, in, germany}; context has {paris, is}; 2/4 = 0.5
    assert faithfulness("paris is in germany", "paris is the capital of france") == pytest.approx(0.5)


def test_citation_accuracy_known_value():
    assert citation_accuracy(["doc1.txt", "doc2.txt"], {"doc1.txt"}) == 0.5


def test_citation_accuracy_no_citations_is_zero():
    assert citation_accuracy([], {"doc1.txt"}) == 0.0
