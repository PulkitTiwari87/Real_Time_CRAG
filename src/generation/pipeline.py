"""Phase 05: grounded generation, wiring Phase 04's retriever+grader into
Phase 01's LLM provider abstraction (Ollama default / Gemini alternate).

Deliberately does NOT implement query rewriting or retry-on-bad-grade --
that is Phase 07 (Corrective RAG). This phase's job is grounding: only
GOOD-graded chunks are used as context, with numbered citations mapped
back to their real source, and the pipeline abstains (no LLM call at all)
if nothing passes grading.
"""
from __future__ import annotations

import time
from dataclasses import dataclass

from rag_baseline.llm_providers import LLMConfigError, LLMProvider, LLMProviderError, get_provider
from retrieval.grader import Grade, GradedResult

PROMPT_TEMPLATE = """Answer the question using ONLY the numbered context below. \
Cite sources inline as [1], [2], etc. If the context does not contain the answer, say you don't know.

Context:
{context}

Question: {question}

Answer:"""


class GenerationError(RuntimeError):
    """Raised when the configured LLM provider cannot be used or fails."""


@dataclass(frozen=True)
class Citation:
    index: int
    chunk_id: str
    document_id: str
    source: str


@dataclass(frozen=True)
class GroundedAnswer:
    answer: str
    citations: list[Citation]
    model: str
    latency_ms: float
    used_chunk_count: int
    dropped_chunk_count: int


def _build_prompt(question: str, good_chunks: list[GradedResult]) -> str:
    context = "\n".join(f"[{i + 1}] {c.content}" for i, c in enumerate(good_chunks))
    return PROMPT_TEMPLATE.format(context=context, question=question)


def generate_grounded_answer(
    question: str,
    graded_results: list[GradedResult],
    provider: LLMProvider | None = None,
    provider_name: str | None = None,
) -> GroundedAnswer:
    good = [g for g in graded_results if g.grade == Grade.GOOD]
    dropped = len(graded_results) - len(good)

    if not good:
        return GroundedAnswer(
            answer="I don't know. No sufficiently relevant context was retrieved.",
            citations=[],
            model="n/a",
            latency_ms=0.0,
            used_chunk_count=0,
            dropped_chunk_count=dropped,
        )

    prompt = _build_prompt(question, good)
    try:
        llm = provider or get_provider(provider_name)
    except LLMConfigError as exc:
        raise GenerationError(str(exc)) from exc

    start = time.perf_counter()
    try:
        answer_text = llm.generate(prompt)
    except LLMProviderError as exc:
        raise GenerationError(str(exc)) from exc
    latency_ms = (time.perf_counter() - start) * 1000

    citations = [
        Citation(index=i + 1, chunk_id=g.chunk_id, document_id=g.document_id, source=g.source)
        for i, g in enumerate(good)
    ]
    return GroundedAnswer(
        answer=answer_text.strip(),
        citations=citations,
        model=llm.model_name,
        latency_ms=latency_ms,
        used_chunk_count=len(good),
        dropped_chunk_count=dropped,
    )
