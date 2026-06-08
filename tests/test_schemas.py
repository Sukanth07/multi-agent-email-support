"""Tests for the agent I/O schemas."""

import pytest
from pydantic import ValidationError

from support_agent.models.enums import Intent
from support_agent.models.schemas import (
    IntentResult,
    RetrievalAssessment,
    ReviewResult,
)


def test_intent_result_defaults_collections() -> None:
    result = IntentResult(intent=Intent.BILLING, confidence=0.8, summary="refund")
    assert result.entities == []
    assert result.queries == []


@pytest.mark.parametrize("bad", [-0.1, 1.1])
def test_confidence_must_be_within_unit_interval(bad: float) -> None:
    with pytest.raises(ValidationError):
        IntentResult(intent=Intent.API, confidence=bad, summary="x")


def test_review_confidence_bounds() -> None:
    with pytest.raises(ValidationError):
        ReviewResult(approved=True, confidence=2.0)


def test_retrieval_assessment_requires_fields() -> None:
    assessment = RetrievalAssessment(retrieval_score=0.5, needs_retry=True, reason="partial")
    assert assessment.needs_retry is True
    with pytest.raises(ValidationError):
        RetrievalAssessment(retrieval_score=0.5, needs_retry=True)  # missing reason
