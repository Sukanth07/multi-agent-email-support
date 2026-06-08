"""Tests for node logic that needs no LLM call (finalize / escalation)."""

from support_agent.models.schemas import ReviewResult
from support_agent.models.state import WorkflowState
from support_agent.workflow.nodes import ESCALATION_MESSAGE, finalize_node


def test_finalize_publishes_approved_draft() -> None:
    state = WorkflowState(
        email="x",
        draft_response="the reply",
        review_result=ReviewResult(approved=True, confidence=0.9, feedback=[]),
    )
    result = finalize_node(state)
    assert result["final_response"] == "the reply"
    assert "needs_human_review" not in result


def test_finalize_escalates_unapproved_draft() -> None:
    state = WorkflowState(
        email="x",
        draft_response="shaky reply",
        review_result=ReviewResult(approved=False, confidence=0.7, feedback=["ungrounded"]),
    )
    result = finalize_node(state)
    assert result["needs_human_review"] is True
    assert result["final_response"] == ESCALATION_MESSAGE
    assert result["final_response"] != "shaky reply"  # the draft is not sent


def test_finalize_on_error_does_not_publish() -> None:
    state = WorkflowState(email="x", draft_response="anything", error="boom")
    result = finalize_node(state)
    assert "final_response" not in result
