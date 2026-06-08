"""LangGraph nodes.

Each node reads the shared state, runs one agent, and returns typed partial updates
plus a `_detail` message. The `_node` decorator turns that into the uniform shape
every node needs: it records the trace entry, and on failure writes the error into
state and short-circuits the rest of the run. Node names are defined once, in the
decorator argument.
"""

from collections.abc import Callable
from functools import lru_cache, wraps
from typing import Any

from support_agent.agents.intent import IntentAgent
from support_agent.agents.planner import PlannerAgent
from support_agent.agents.refiner import RefinerAgent
from support_agent.agents.retrieval import RetrievalAgent
from support_agent.agents.retrieval_validator import RetrievalValidatorAgent
from support_agent.agents.reviewer import ReviewerAgent
from support_agent.agents.writer import WriterAgent
from support_agent.exceptions import AgentError, SupportAgentError
from support_agent.logger import get_logger
from support_agent.models.enums import NextAction
from support_agent.models.state import WorkflowState

logger = get_logger("workflow.nodes")

NodeResult = dict[str, Any]
NodeFn = Callable[[WorkflowState], NodeResult]


# Agents are built lazily and cached so each is constructed once, not per email.
@lru_cache
def _intent_agent() -> IntentAgent:
    return IntentAgent()


@lru_cache
def _retrieval_agent() -> RetrievalAgent:
    return RetrievalAgent()


@lru_cache
def _validator_agent() -> RetrievalValidatorAgent:
    return RetrievalValidatorAgent()


@lru_cache
def _refiner_agent() -> RefinerAgent:
    return RefinerAgent()


@lru_cache
def _planner_agent() -> PlannerAgent:
    return PlannerAgent()


@lru_cache
def _writer_agent() -> WriterAgent:
    return WriterAgent()


@lru_cache
def _reviewer_agent() -> ReviewerAgent:
    return ReviewerAgent()


def _node(name: str) -> Callable[[NodeFn], NodeFn]:
    """Add uniform trace stamping and skip-on-error to a node.

    The wrapped function returns its data plus a `_detail` string; the decorator
    pops `_detail` and records the trace entry. This keeps node names defined once
    (the decorator argument) and away from each node body.
    """

    def decorator(fn: NodeFn) -> NodeFn:
        @wraps(fn)
        def wrapper(state: WorkflowState) -> NodeResult:
            if state.error:
                return {}
            try:
                result = fn(state)
            except SupportAgentError as exc:
                logger.error("node '%s' failed: %s", name, exc)
                return {
                    "error": str(exc),
                    "trace": state.record(name, f"error: {exc}"),
                }
            detail = str(result.pop("_detail", ""))
            result["trace"] = state.record(name, detail)
            return result

        return wrapper

    return decorator


@_node("intent")
def intent_node(state: WorkflowState) -> NodeResult:
    result = _intent_agent().classify(state.email)
    return {
        "intent": result.intent,
        "intent_confidence": result.confidence,
        "summary": result.summary,
        "entities": result.entities,
        "queries": result.queries,
        "_detail": f"{result.intent.value} ({result.confidence:.2f})",
    }


@_node("retrieve")
def retrieve_node(state: WorkflowState) -> NodeResult:
    docs = _retrieval_agent().retrieve(state.queries)
    attempt = state.retrieval_attempts + 1
    return {
        "retrieved_docs": docs,
        "retrieval_attempts": attempt,
        "_detail": f"{len(docs)} docs (attempt {attempt})",
    }


@_node("validate")
def validate_node(state: WorkflowState) -> NodeResult:
    assessment = _validator_agent().validate(state.email, state.queries, state.retrieved_docs)
    return {
        "retrieval_score": assessment.retrieval_score,
        "needs_retry": assessment.needs_retry,
        "retrieval_reason": assessment.reason,
        "_detail": f"score={assessment.retrieval_score:.2f} needs_retry={assessment.needs_retry}",
    }


@_node("refine")
def refine_node(state: WorkflowState) -> NodeResult:
    if state.intent is None:
        raise AgentError("refiner", "no intent available")
    refined = _refiner_agent().refine(
        state.email, state.intent.value, state.queries, state.retrieval_reason
    )
    return {
        "intent": refined.intent,
        "intent_confidence": refined.confidence,
        "summary": refined.summary,
        "entities": refined.entities,
        "queries": refined.queries,
        "_detail": f"intent -> {refined.intent.value}, {len(refined.queries)} new queries",
    }


@_node("plan")
def plan_node(state: WorkflowState) -> NodeResult:
    if state.intent is None:
        raise AgentError("planner", "no intent available")
    plan = _planner_agent().plan(
        state.email, state.intent.value, state.summary, state.retrieved_docs
    )
    return {"plan": plan, "_detail": plan.goal}


@_node("write")
def write_node(state: WorkflowState) -> NodeResult:
    if state.plan is None:
        raise AgentError("writer", "no plan available")

    is_rewrite = state.review_result is not None
    feedback = state.review_result.feedback if state.review_result else None
    output = _writer_agent().write(state.plan, state.retrieved_docs, feedback)

    result: NodeResult = {
        "draft_response": output.draft_response,
        "citations": output.citations,
        "_detail": "rewrote draft" if is_rewrite else "drafted reply",
    }
    if is_rewrite:
        result["rewrite_attempts"] = state.rewrite_attempts + 1
    return result


@_node("review")
def review_node(state: WorkflowState) -> NodeResult:
    if state.plan is None:
        raise AgentError("reviewer", "no plan available")

    review = _reviewer_agent().review(
        state.email, state.plan, state.draft_response, state.retrieved_docs
    )
    return {
        "review_result": review,
        "_detail": f"approved={review.approved} ({review.confidence:.2f})",
    }


ESCALATION_MESSAGE = (
    "Thanks for reaching out. We're reviewing your request and a support "
    "specialist will follow up with you shortly."
)


def finalize_node(state: WorkflowState) -> NodeResult:
    """Terminal node: publish an approved draft, escalate if not, or end on error."""
    if state.error:
        return {
            "next_action": NextAction.FINISH,
            "trace": state.record("finalize", "ended with error"),
        }

    approved = state.review_result is not None and state.review_result.approved
    if approved:
        return {
            "final_response": state.draft_response,
            "next_action": NextAction.FINISH,
            "trace": state.record("finalize", "final response ready"),
        }

    # Rewrites exhausted without approval: never send an unverified reply.
    return {
        "final_response": ESCALATION_MESSAGE,
        "needs_human_review": True,
        "next_action": NextAction.FINISH,
        "trace": state.record("finalize", "not approved after max rewrites; escalated to human"),
    }
