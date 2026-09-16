# Evaluation Metrics

## Retrieval Metrics
- **Recall@K**: Fraction of relevant documents retrieved in the top K results.
- **Precision@K**: Ratio of relevant documents among the top K retrieved.
- **MRR (Mean Reciprocal Rank)**: Average reciprocal rank of the first relevant document.
- **NDCG (Normalized Discounted Cumulative Gain)**: Position‑weighted relevance score.

## Generation Metrics
- **Faithfulness**: Degree to which the generated answer is supported by retrieved sources.
- **Answer Relevance**: Relevance of the answer to the user query.
- **Citation Correctness**: Accuracy and completeness of source citations.
- **Context Relevance**: How well the answer utilizes retrieved context.

## System Metrics
- **Latency**: End‑to‑end response time.
- **Token Usage**: Total tokens per request (input + output + embeddings).
- **Retry Rate**: Frequency of CRAG loop retries.
- **Cost**: Approximate monetary cost based on token pricing (free‑tier monitoring).
