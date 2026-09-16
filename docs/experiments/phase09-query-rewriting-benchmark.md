# Phase 09 Query Rewriting Benchmark

Real measurement (not assumed): 6 deliberately awkward/verbose phrasings of the standard benchmark queries, checking whether the correct document ranks first (accuracy@1) for the original query vs. two rewrite strategies.

| Strategy | Accuracy@1 |
|---|---|
| Original (no rewrite) | 1.00 |
| Deterministic (keyword extraction) | 1.00 |
| LLM-based (Gemini) | 1.00 |

## Per-Query Detail

### Um, so like, where would I go if I wanted to see that huge iron tower thing they built in France a long time ago?
- Original correct: True
- Deterministic rewrite: "um so like would i go if i wanted see huge iron tower thing they built france long time ago" -> correct: True
- LLM rewrite: "Where is the Eiffel Tower located" -> correct: True

### You know that thing where green plants somehow turn sunshine into food-type energy for themselves, what's that called?
- Original correct: True
- Deterministic rewrite: "you know thing green plants somehow turn sunshine into foodtype energy themselves whats called" -> correct: True
- LLM rewrite: "process where plants convert sunlight into food" -> correct: True

### I heard there's this massive underwater rock structure made of coral near Australia that's supposedly the biggest one on Earth, what is it?
- Original correct: True
- Deterministic rewrite: "i heard theres massive underwater rock structure made coral near australia thats supposedly biggest one earth it" -> correct: True
- LLM rewrite: "largest coral reef system in Australia" -> correct: True

### So there's this coding language that people say is really easy to read because of how it's written, which one is that?
- Original correct: True
- Deterministic rewrite: "so theres coding language people say really easy read because its written which one" -> correct: True
- LLM rewrite: "most readable programming language" -> correct: True

### What's that little part inside cells that's in charge of making the energy molecules through breathing-type chemical reactions?
- Original correct: True
- Deterministic rewrite: "whats little part inside cells thats charge making energy molecules through breathingtype chemical reactions" -> correct: True
- LLM rewrite: "Which cell organelle produces ATP through cellular respiration?" -> correct: True

### Is there some kind of database out there specifically built to hold vector-type data for doing similarity lookups fast?
- Original correct: True
- Deterministic rewrite: "there some kind database out there specifically built hold vectortype data doing similarity lookups fast" -> correct: True
- LLM rewrite: "vector database for fast similarity search" -> correct: True

## Conclusion

Rewriting did NOT improve accuracy on this benchmark -- the embedding model already handled these awkward phrasings correctly without any rewrite.

This matches the general finding that semantic (vector) embeddings are often robust to phrasing/verbosity variations, so rewriting's main value is likely for lexical (BM25) retrieval or genuinely ambiguous/underspecified queries, not simply verbose ones. Do not assume rewriting is always beneficial for vector retrieval.