# Real-Time Corrective RAG Intelligence Platform

## Project Status

Status: NOT STARTED
Current Phase: Phase 0
Current Milestone: Project Setup

---

# 1. Project Objective

Build a production-oriented Corrective RAG (CRAG) system that:

1. Retrieves relevant information from a knowledge base.
2. Evaluates the quality of retrieved documents.
3. Detects poor retrieval.
4. Rewrites the user's query when retrieval quality is poor.
5. Performs retrieval again.
6. Generates grounded answers.
7. Provides source attribution.
8. Eventually supports real-time document ingestion.
9. Eventually supports time-aware retrieval.

---

# 2. Core Architecture

User
 ↓
Query
 ↓
Retriever
 ↓
Document Grader
 ↓
 ┌───────────────┐
 │               │
Good            Bad
 │               │
 ↓               ↓
Generate      Query Rewrite
                 ↓
              Retrieve
                 ↓
               Grade
                 ↓
              Generate
                 ↓
                END


Future:

News/RSS
 ↓
Kafka
 ↓
Processing
 ↓
Chunking
 ↓
Embeddings
 ↓
Vector Database
 ↓
CRAG
 ↓
Answer + Sources