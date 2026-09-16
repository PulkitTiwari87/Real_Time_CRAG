"""Phase 08: LangGraph orchestration of the Phase 07 corrective RAG loop.

Same retrieve -> grade -> (GOOD: generate | BAD: rewrite -> retry) logic as
corrective.crag.run_crag, now expressed as an explicit state graph instead
of a Python for-loop. Bounded transitions and deterministic termination
are enforced by the graph's conditional edge (retry_count >= max_retries
routes unconditionally to "generate"), with LangGraph's own recursion
limit as a second independent safeguard against a runaway graph.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, TypedDict

from langgraph.graph import END, StateGraph

from corrective.rewriter import RewriteError, rewrite_query
from generation.pipeline import GroundedAnswer, generate_grounded_answer
from retrieval.grader import Grade, GradedResult, grade_results
from retrieval.retriever import RetrievalResult

DEFAULT_MAX_RETRIES = 2


class CRAGState(TypedDict):
    original_query: str
    current_query: str
    top_k: int
    max_retries: int
    retry_count: int
    rewrite_count: int
    first_attempt_good: Optional[bool]
    retrieval_results: list[RetrievalResult]
    graded_results: list[GradedResult]
    has_good: bool
    rewrite_failed: bool
    answer: Optional[GroundedAnswer]


@dataclass(frozen=True)
class GraphCRAGResult:
    answer: GroundedAnswer
    original_query: str
    final_query: str
    rewrite_count: int
    recovered_by_rewrite: bool
    abstained: bool


def build_crag_graph(retriever, provider=None, provider_name: str | None = None):
    def retrieve_node(state: CRAGState) -> CRAGState:
        results = retriever.retrieve(state["current_query"], top_k=state["top_k"])
        return {**state, "retrieval_results": results}

    def grade_node(state: CRAGState) -> CRAGState:
        graded = grade_results(state["current_query"], state["retrieval_results"])
        has_good = any(g.grade == Grade.GOOD for g in graded)
        first_attempt_good = state["first_attempt_good"]
        if first_attempt_good is None:
            first_attempt_good = has_good
        return {**state, "graded_results": graded, "has_good": has_good, "first_attempt_good": first_attempt_good}

    def rewrite_node(state: CRAGState) -> CRAGState:
        try:
            new_query = rewrite_query(state["current_query"], provider=provider, provider_name=provider_name)
        except RewriteError:
            return {**state, "rewrite_failed": True}
        return {
            **state,
            "current_query": new_query,
            "retry_count": state["retry_count"] + 1,
            "rewrite_count": state["rewrite_count"] + 1,
        }

    def generate_node(state: CRAGState) -> CRAGState:
        answer = generate_grounded_answer(
            state["current_query"], state["graded_results"], provider=provider, provider_name=provider_name
        )
        return {**state, "answer": answer}

    def route_after_grade(state: CRAGState) -> str:
        if state["has_good"] or state["retry_count"] >= state["max_retries"]:
            return "generate"
        return "rewrite"

    def route_after_rewrite(state: CRAGState) -> str:
        return "generate" if state.get("rewrite_failed") else "retrieve"

    graph = StateGraph(CRAGState)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("grade", grade_node)
    graph.add_node("rewrite", rewrite_node)
    graph.add_node("generate", generate_node)

    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "grade")
    graph.add_conditional_edges("grade", route_after_grade, {"generate": "generate", "rewrite": "rewrite"})
    graph.add_conditional_edges("rewrite", route_after_rewrite, {"retrieve": "retrieve", "generate": "generate"})
    graph.add_edge("generate", END)

    return graph.compile()


def run_crag_graph(
    query: str,
    retriever,
    top_k: int = 5,
    max_retries: int = DEFAULT_MAX_RETRIES,
    provider=None,
    provider_name: str | None = None,
) -> GraphCRAGResult:
    if max_retries < 0:
        raise ValueError("max_retries must be >= 0")

    graph = build_crag_graph(retriever, provider=provider, provider_name=provider_name)
    initial_state: CRAGState = {
        "original_query": query,
        "current_query": query,
        "top_k": top_k,
        "max_retries": max_retries,
        "retry_count": 0,
        "rewrite_count": 0,
        "first_attempt_good": None,
        "retrieval_results": [],
        "graded_results": [],
        "has_good": False,
        "rewrite_failed": False,
        "answer": None,
    }
    final_state = graph.invoke(initial_state)

    return GraphCRAGResult(
        answer=final_state["answer"],
        original_query=final_state["original_query"],
        final_query=final_state["current_query"],
        rewrite_count=final_state["rewrite_count"],
        recovered_by_rewrite=(final_state["first_attempt_good"] is False) and final_state["has_good"],
        abstained=final_state["answer"].used_chunk_count == 0,
    )
