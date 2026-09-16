# Evaluation Methodology

The evaluation process follows a reproducible pipeline:
1. **Dataset Preparation** – curated benchmark queries with ground‑truth citations.
2. **Run Baseline RAG** – execute Phase 01 pipeline on the dataset, collect raw outputs.
3. **Run CRAG** – after Phase 07, re‑run with corrective loop.
4. **Metric Computation** – automatically compute retrieval, generation, and system metrics defined in `metrics.md`.
5. **Statistical Analysis** – compare baseline vs. CRAG using paired t‑tests or bootstrap confidence intervals.
6. **Reporting** – generate a markdown report summarizing results, charts, and observations.

All scripts are located under `scripts/evaluation/` (to be added in later phases). The methodology is provider‑agnostic and uses only free‑tier APIs where possible.
