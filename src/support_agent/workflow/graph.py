"""Workflow graph: wires the agent nodes around the orchestrator (hub-and-spoke).

Every working node returns to the orchestrator, which selects the next step. This
module is topology only; the control policy lives in `orchestrator.py`.
"""

from collections.abc import Iterator
from functools import lru_cache

from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from support_agent.logger import get_logger
from support_agent.models.state import WorkflowState
from support_agent.workflow import nodes
from support_agent.workflow.orchestrator import ROUTE_DESTINATIONS, orchestrate, route

logger = get_logger("workflow.graph")

# Loops add node visits, so allow more than the default before LangGraph aborts.
_CONFIG: RunnableConfig = {"recursion_limit": 50}

_AGENT_NODES = {
    "intent": nodes.intent_node,
    "retrieve": nodes.retrieve_node,
    "validate": nodes.validate_node,
    "refine": nodes.refine_node,
    "plan": nodes.plan_node,
    "write": nodes.write_node,
    "review": nodes.review_node,
    "finalize": nodes.finalize_node,
}


def build_workflow() -> CompiledStateGraph[WorkflowState]:
    """Construct and compile the workflow.

    Linear hand-offs between deterministic steps; the orchestrator is consulted
    only at the two real branching points (after validation and after review).
    """
    graph: StateGraph[WorkflowState] = StateGraph(WorkflowState)

    graph.add_node("orchestrate", orchestrate)
    # LangGraph's add_node stubs type the node input as `Never`, so a typed node
    # Callable doesn't match; the runtime contract is correct.
    for name, fn in _AGENT_NODES.items():
        graph.add_node(name, fn)  # type: ignore[arg-type]

    graph.add_edge(START, "intent")
    graph.add_edge("intent", "retrieve")
    graph.add_edge("retrieve", "validate")
    graph.add_edge("validate", "orchestrate")
    graph.add_edge("refine", "retrieve")
    graph.add_edge("plan", "write")
    graph.add_edge("write", "review")
    graph.add_edge("review", "orchestrate")
    graph.add_conditional_edges("orchestrate", route, ROUTE_DESTINATIONS)
    graph.add_edge("finalize", END)

    return graph.compile()


@lru_cache
def get_workflow() -> CompiledStateGraph[WorkflowState]:
    """Return the cached compiled workflow."""
    return build_workflow()


def run_workflow(email: str) -> WorkflowState:
    """Run the full workflow for one email and return the final state."""
    logger.info("workflow start")
    result = get_workflow().invoke(WorkflowState(email=email), config=_CONFIG)
    logger.info("workflow end")
    return WorkflowState(**result)


def stream_workflow(email: str) -> Iterator[WorkflowState]:
    """Yield the workflow state after each step, for live UI updates."""
    logger.info("workflow stream start")
    for values in get_workflow().stream(
        WorkflowState(email=email), stream_mode="values", config=_CONFIG
    ):
        yield WorkflowState(**values)
    logger.info("workflow stream end")
