"""Orchestrator: the workflow control policy.

`decide` is a pure, deterministic function that selects the next action at every
branching point in the workflow: whether to retry retrieval, proceed to planning,
rewrite a rejected draft, or finish. It is consulted after retrieval validation
and after review — the two places where a real routing decision exists.

This module holds the policy; `graph.py` only wires it in.
"""

from support_agent.config import get_settings
from support_agent.models.enums import NextAction
from support_agent.models.state import WorkflowState

# Each routing action maps to the graph node that performs it.
ACTION_TO_NODE = {
    NextAction.RETRY_RETRIEVAL.value: "refine",
    NextAction.PLAN.value: "plan",
    NextAction.REWRITE.value: "write",
    NextAction.FINISH.value: "finalize",
}

# Distinct destination nodes the orchestrator can route to.
ROUTE_DESTINATIONS = sorted(set(ACTION_TO_NODE.values()))


def decide(state: WorkflowState) -> NextAction:
    """Select the next action from the shared state.

    Reached after validation and after review. The presence of a review result
    distinguishes the two junctions.
    """
    settings = get_settings()

    if state.error:
        return NextAction.FINISH

    if state.review_result is not None:
        rejected = not state.review_result.approved
        if rejected and state.rewrite_attempts < settings.max_rewrite_attempts:
            return NextAction.REWRITE
        return NextAction.FINISH

    if state.needs_retry and state.retrieval_attempts < settings.max_retrieval_attempts:
        return NextAction.RETRY_RETRIEVAL
    return NextAction.PLAN


def orchestrate(state: WorkflowState) -> dict[str, object]:
    """Decision node: record the chosen next action in state and trace."""
    action = decide(state)
    return {
        "next_action": action,
        "trace": state.record("orchestrator", f"next_action={action.value}"),
    }


def route(state: WorkflowState) -> str:
    """Conditional-edge function: the node name to run for the chosen action."""
    return ACTION_TO_NODE[state.next_action.value]
