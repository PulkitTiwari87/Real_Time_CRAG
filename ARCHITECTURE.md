# Architecture

## Status

Architecture v0.1

## Current Architecture

The initial implementation will use a simple offline RAG pipeline.

```text
Documents
    ↓
Document Loader
    ↓
Text Splitter
    ↓
Embedding Model
    ↓
Vector Store
    ↓
Retriever
    ↓
LLM
    ↓
Answer
```

## Target Architecture

```text
                    ┌───────────────┐
                    │   User/API    │
                    └───────┬───────┘
                            ↓
                    ┌───────────────┐
                    │   LangGraph   │
                    └───────┬───────┘
                            ↓
                     ┌────────────┐
                     │ Retriever  │
                     └──────┬─────┘
                            ↓
                     ┌────────────┐
                     │   Grader   │
                     └──────┬─────┘
                            ↓
                   ┌────────┴────────┐
                   │                 │
                 GOOD               BAD
                   │                 │
                   ↓                 ↓
               Generate          Rewrite
                                     ↓
                                  Retrieve
                                     ↓
                                   Grade
                   │                 │
                   └────────┬────────┘
                            ↓
                         Answer
```

The architecture will evolve as each phase is implemented and evaluated.
