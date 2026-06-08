"""Shared workflow state.

`WorkflowState` is the single object every node reads and updates. Nodes return
typed partial updates rather than passing strings between agents.
"""

from pydantic import BaseModel, Field

from support_agent.models.enums import Intent, NextAction
from support_agent.models.schemas import (
    ResponsePlan,
    RetrievedDoc,
    ReviewResult,
)


class TraceEntry(BaseModel):
    """One recorded step, surfaced in the UI's workflow trace."""

    node: str
    detail: str


class WorkflowState(BaseModel):
    """End-to-end state for a single customer email."""

    email: str

    intent: Intent | None = None
    intent_confidence: float = 0.0
    summary: str = ""
    entities: list[str] = Field(default_factory=list)
    queries: list[str] = Field(default_factory=list)

    retrieved_docs: list[RetrievedDoc] = Field(default_factory=list)
    retrieval_score: float = 0.0
    needs_retry: bool = False
    retrieval_reason: str = ""
    retrieval_attempts: int = 0

    plan: ResponsePlan | None = None

    draft_response: str = ""
    citations: list[str] = Field(default_factory=list)

    review_result: ReviewResult | None = None
    rewrite_attempts: int = 0

    next_action: NextAction = NextAction.PLAN
    final_response: str = ""
    needs_human_review: bool = False

    trace: list[TraceEntry] = Field(default_factory=list)
    error: str | None = None

    def record(self, node: str, detail: str) -> list[TraceEntry]:
        """Return the trace extended with a new entry (for node updates)."""
        return [*self.trace, TraceEntry(node=node, detail=detail)]
