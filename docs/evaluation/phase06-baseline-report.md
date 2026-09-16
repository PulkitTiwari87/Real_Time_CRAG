# Phase 06 Baseline Evaluation Report

Real end-to-end run of the Phase 05 pipeline over 6 queries against 6 documents (docs/evaluation/benchmark_dataset.json), top_k=3.

## Aggregate Metrics

| Metric | Value |
|---|---|
| retrieval.recall_at_k | 1.000 |
| retrieval.precision_at_k | 0.333 |
| retrieval.mrr | 1.000 |
| retrieval.ndcg_at_k | 1.000 |
| generation.bleu | 0.572 |
| generation.rouge_l | 0.701 |
| generation.faithfulness | 0.713 |
| generation.citation_accuracy | 1.000 |

## Per-Query Results

### Where is the Eiffel Tower located?
- **Answer:** The Eiffel Tower is located in Paris, France [1].
- Retrieval: recall@k=1.00, precision@k=0.33, mrr=1.00, ndcg@k=1.00
- Generation: bleu=0.73, rouge_l=0.82, faithfulness=0.89, citation_accuracy=1.00

### How do plants convert sunlight into energy?
- **Answer:** Plants convert sunlight into chemical energy through the process of photosynthesis [1].
- Retrieval: recall@k=1.00, precision@k=0.33, mrr=1.00, ndcg@k=1.00
- Generation: bleu=0.52, rouge_l=0.70, faithfulness=0.67, citation_accuracy=1.00

### What is the largest coral reef system?
- **Answer:** The largest coral reef system is the Great Barrier Reef [1].
- Retrieval: recall@k=1.00, precision@k=0.33, mrr=1.00, ndcg@k=1.00
- Generation: bleu=0.38, rouge_l=0.45, faithfulness=0.78, citation_accuracy=1.00

### Which programming language is known for readable syntax?
- **Answer:** Python is known for its readable syntax [1].
- Retrieval: recall@k=1.00, precision@k=0.33, mrr=1.00, ndcg@k=1.00
- Generation: bleu=0.68, rouge_l=0.80, faithfulness=0.75, citation_accuracy=1.00

### What organelle produces ATP in a cell?
- **Answer:** The mitochondria produces ATP in a cell [1].
- Retrieval: recall@k=1.00, precision@k=0.33, mrr=1.00, ndcg@k=1.00
- Generation: bleu=0.35, rouge_l=0.57, faithfulness=0.38, citation_accuracy=1.00

### What is a vector database used for similarity search?
- **Answer:** Qdrant is an open-source vector database used for similarity search [1].
- Retrieval: recall@k=1.00, precision@k=0.33, mrr=1.00, ndcg@k=1.00
- Generation: bleu=0.79, rouge_l=0.86, faithfulness=0.82, citation_accuracy=1.00
