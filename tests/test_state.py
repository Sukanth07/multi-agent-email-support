"""Tests for the shared workflow state."""

from support_agent.models.enums import NextAction
from support_agent.models.state import TraceEntry, WorkflowState


def test_defaults() -> None:
    state = WorkflowState(email="hello")
    assert state.intent is None
    assert state.next_action is NextAction.PLAN
    assert state.entities == [] and state.queries == []
    assert state.retrieval_attempts == 0 and state.rewrite_attempts == 0
    assert state.needs_human_review is False
    assert state.error is None
    assert state.trace == []


def test_record_returns_extended_trace_without_mutating() -> None:
    state = WorkflowState(email="x")
    first = state.record("intent", "classified")

    assert state.trace == []  # original is untouched
    assert len(first) == 1
    assert isinstance(first[0], TraceEntry)
    assert first[0].node == "intent"
    assert first[0].detail == "classified"


def test_record_appends_to_existing_trace() -> None:
    state = WorkflowState(email="x", trace=[TraceEntry(node="intent", detail="a")])
    extended = state.record("retrieve", "b")

    assert [entry.node for entry in extended] == ["intent", "retrieve"]
