"""Phase 06: evaluation framework for retrieval, generation, and (later) CRAG performance."""
from .metrics import (
    bleu,
    citation_accuracy,
    faithfulness,
    mrr,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
    rouge_l,
)

__all__ = [
    "recall_at_k",
    "precision_at_k",
    "mrr",
    "ndcg_at_k",
    "bleu",
    "rouge_l",
    "faithfulness",
    "citation_accuracy",
]
