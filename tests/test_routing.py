"""Tests for the orchestrator routing policy (pure, no network)."""

import pytest

from support_agent.config import get_settings
from support_agent.models.enums import NextAction
from support_agent.models.schemas import ReviewResult
from support_agent.models.state import WorkflowState
from support_agent.workflow.orchestrator import decide

_SETTINGS = get_settings()
_MAX_RETRIEVAL = _SETTINGS.max_retrieval_attempts
_MAX_REWRITE = _SETTINGS.max_rewrite_attempts

_REJECTED = ReviewResult(approved=False, confidence=0.8, feedback=["fix grounding"])
_APPROVED = ReviewResult(approved=True, confidence=0.95, feedback=[])


def _state(**kwargs: object) -> WorkflowState:
    return WorkflowState(email="x", **kwargs)


_CASES = [
    # Post-validation junction
    (_state(needs_retry=True, retrieval_attempts=1), NextAction.RETRY_RETRIEVAL),
    (_state(needs_retry=True, retrieval_attempts=_MAX_RETRIEVAL), NextAction.PLAN),
    (_state(needs_retry=False), NextAction.PLAN),
    # Post-review junction
    (_state(review_result=_REJECTED, rewrite_attempts=0), NextAction.REWRITE),
    (_state(review_result=_REJECTED, rewrite_attempts=_MAX_REWRITE), NextAction.FINISH),
    (_state(review_result=_APPROVED), NextAction.FINISH),
    # Error short-circuit
    (_state(error="boom"), NextAction.FINISH),
]


@pytest.mark.parametrize(("state", "expected"), _CASES)
def test_decide(state: WorkflowState, expected: NextAction) -> None:
    assert decide(state) == expected


def test_error_overrides_any_other_signal() -> None:
    state = _state(error="x", needs_retry=True, retrieval_attempts=0)
    assert decide(state) is NextAction.FINISH
