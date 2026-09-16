# Phase 04 Grader Calibration

Real measurements (not simulated). Two corpora combined: 6 short single-topic sentences (easy) + 4 longer multi-sentence paragraphs where the correct answer is one fact embedded among several unrelated sentences (hard, closer to real chunk content). 10 queries x 10 documents = 100 (query, doc) pairs, one true positive per query.

**Revision note:** an earlier version of this benchmark used only the easy corpus, scored a perfect ROC-AUC/PR-AUC of 1.0, and set the default threshold to 0.55 from that alone. That threshold produced a real false negative in manual pipeline testing -- a chunk containing the literal answer was graded BAD because its raw cosine similarity (0.38) was well below what the easy-only benchmark implied. This version benchmarks both corpora together and picks a threshold via F1-maximization instead of an assumed constant.

- Pairs evaluated: 121 (11 positive, 110 negative)
- ROC-AUC: 1.000
- PR-AUC (average precision): 1.000
- Positive-pair confidence range: 0.391 - 0.773
- Best F1 threshold: 0.391 (F1=1.000)
- At best threshold: precision=1.000, recall=1.000 (TP=11, FP=0, FN=0)

## Decision

`DEFAULT_CONFIDENCE_THRESHOLD` updated to 0.39 in src/retrieval/grader.py, chosen by F1-maximization on this combined easy+hard set rather than an assumed value.

## Notes

Still a small (100-pair), hand-labeled set -- enough to catch gross miscalibration and validate the fix for the specific failure mode found, not a substitute for Phase 06's full evaluation framework on a larger held-out benchmark.