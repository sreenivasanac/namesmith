"""LangGraph definitions for agent workflow."""
from __future__ import annotations

from langgraph.constants import END
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledGraph

from .nodes.availability import build_availability_node
from .nodes.dedupe import dedupe_and_filter
from .nodes.gather import gather_context
from .nodes.generate import build_generate_node
from .nodes.persist import build_persist_node
from .nodes.score import build_score_node
from .providers.base import AvailabilityProvider, GenerationProvider, ScoringProvider
from .state import GenerationStateDict


def build_generation_graph(
    *,
    generation_provider: GenerationProvider,
    scoring_provider: ScoringProvider,
    availability_provider: AvailabilityProvider,
    persist_node,
) -> CompiledGraph:
    graph = StateGraph(GenerationStateDict)
    graph.add_node("gather_context", gather_context)
    graph.add_node("generate", build_generate_node(generation_provider))
    graph.add_node("dedupe", dedupe_and_filter)
    graph.add_node("score", build_score_node(scoring_provider))
    graph.add_node("availability", build_availability_node(availability_provider))
    graph.add_node("persist", persist_node)

    graph.set_entry_point("gather_context")
    graph.add_edge("gather_context", "generate")
    graph.add_edge("generate", "dedupe")
    graph.add_edge("dedupe", "score")
    graph.add_edge("score", "availability")
    graph.add_edge("availability", "persist")
    graph.add_edge("persist", END)

    return graph.compile()
