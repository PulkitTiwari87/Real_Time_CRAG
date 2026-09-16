"""LLM answer generation over retrieved context via a pluggable LLM provider.

Provider-agnostic: the default is the local, zero-cost Ollama path
(llm_providers.ollama_provider), with Gemini available as an alternate
provider (llm_providers.gemini_provider) for development/verification.
Selection is via LLM_PROVIDER (default "ollama") or an injected provider.
"""
from __future__ import annotations

import time
from dataclasses import dataclass

from .llm_providers import LLMConfigError, LLMProvider, LLMProviderError, get_provider
from .retriever import RetrievedChunk

PROMPT_TEMPLATE = """Answer the question using ONLY the numbered context below. \
Cite sources inline as [1], [2], etc. If the context does not contain the answer, say you don't know.

Context:
{context}

Question: {question}

Answer:"""


class GenerationError(RuntimeError):
    """Raised when the configured LLM provider cannot be used or fails."""


@dataclass(frozen=True)
class GeneratedAnswer:
    answer: str
    citations: list[str]
    model: str
    latency_ms: float


def _build_prompt(question: str, chunks: list[RetrievedChunk]) -> str:
    context = "\n".join(f"[{i + 1}] {c.content}" for i, c in enumerate(chunks))
    return PROMPT_TEMPLATE.format(context=context, question=question)


def generate_answer(
    question: str,
    chunks: list[RetrievedChunk],
    provider: LLMProvider | None = None,
    provider_name: str | None = None,
) -> GeneratedAnswer:
    """Generate a grounded answer from retrieved chunks, or abstain if none.

    ``provider`` injects a specific provider instance (used by tests).
    ``provider_name`` selects one by name ("ollama"/"gemini"); if neither
    is given, selection falls back to the LLM_PROVIDER env var.
    """
    if not chunks:
        return GeneratedAnswer(
            answer="I don't know. No relevant context was retrieved.",
            citations=[],
            model="n/a",
            latency_ms=0.0,
        )

    prompt = _build_prompt(question, chunks)
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

    citations = [c.source for c in chunks]
    return GeneratedAnswer(
        answer=answer_text.strip(), citations=citations, model=llm.model_name, latency_ms=latency_ms
    )
