# Phase 02 – Document Processing

## Objective
Add robust document ingestion, preprocessing, and chunking capabilities.

## Why
Provides clean, searchable content for the retrieval pipeline and enables handling of various file formats.

## Learning Goals
- File I/O and loader patterns.
- Text normalization, language detection, OCR basics.
- Chunking strategies (fixed size, semantic).

## Prerequisites
- Phase 00 completed.
- No existing loader code.

## Concepts
- Loader abstraction (interface).
- Chunk size, overlap, token estimation.
- Metadata extraction (source ID, timestamps).

## In Scope
- Implement plain‑text and PDF loaders.
- Basic cleaning (whitespace, unicode normalization).
- Fixed‑size token‑based chunker with configurable overlap.
- Store chunk metadata in a JSON manifest.

## Out of Scope
- Complex formats (Word, Excel, images).
- Full‑text search indexing.
- Distributed processing.

## Expected Files
- `src/document_processing/loader.py`
- `src/document_processing/chunker.py`
- `src/document_processing/__init__.py`
- Unit tests under `tests/document_processing/`.

## Implementation Tasks
1. Define `BaseLoader` abstract class.
2. Implement `TextLoader` and `PDFLoader`.
3. Create `Chunker` with token‑based splitting.
4. Add manifest writer.
5. Write CLI entry point `scripts/run_loader.py`.

## Tests
- Verify loader returns raw text for sample files.
- Ensure chunker respects size/overlap limits.
- Confirm manifest JSON schema.

## Evaluation / Metrics
- **Chunk Quality**: average tokens per chunk, overlap percentage.
- **Processing Time**: seconds per MB processed.
- **Error Rate**: files that fail to load.

## Failure Cases
- Corrupted PDF raises exception.
- Tokenizer mismatch leads to oversized chunks.

## Risks
- Dependency on `PyPDF2` may increase bundle size.
- Tokenizer selection impacts chunk boundaries.

## Acceptance Criteria
- All unit tests pass.
- Loader handles provided sample corpus.
- Chunk manifest matches expected schema.

## Definition of Done
- Code committed (by Antigravity) and passes tests.
- Documentation updated in this plan.

## Handoff to Next Phase
- Provide `chunks/` directory with generated chunk files.
- Export embedding configuration for Phase 03.
