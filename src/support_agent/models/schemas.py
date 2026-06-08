"""Structured I/O models for the agents.

Field descriptions are intentional: they are sent to the LLM as the output schema
when using `with_structured_output`, so they double as instructions.
"""

from pydantic import BaseModel, Field

from support_agent.models.enums import Intent


class RetrievedDoc(BaseModel):
    """A single knowledge base chunk returned by retrieval."""

    content: str
    source: str
    title: str
    score: float = Field(description="Similarity distance from the query (lower is closer).")


class IntentResult(BaseModel):
    """Output of the Intent agent."""

    intent: Intent = Field(description="The single best-matching intent category.")
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Calibrated confidence 0-1; reserve >0.9 for clearly unambiguous emails.",
    )
    summary: str = Field(description="One-sentence summary of what the customer wants.")
    entities: list[str] = Field(
        default_factory=list, description="Key entities (plan, feature, error)."
    )
    queries: list[str] = Field(
        default_factory=list, description="Search queries for retrieval."
    )


class RetrievalAssessment(BaseModel):
    """Output of the Retrieval Validator agent."""

    retrieval_score: float = Field(ge=0.0, le=1.0, description="Relevance of the documents, 0-1.")
    needs_retry: bool = Field(description="True if retrieval is too weak to answer the email.")
    reason: str = Field(description="Brief justification for the score and decision.")


class ResponsePlan(BaseModel):
    """Output of the Planner agent."""

    goal: str = Field(description="What the reply must accomplish for the customer.")
    must_include: list[str] = Field(
        default_factory=list, description="Points the reply must cover."
    )
    key_facts: list[str] = Field(
        default_factory=list, description="Specific facts from the documents to use."
    )


class WriterOutput(BaseModel):
    """Output of the Writer agent."""

    draft_response: str = Field(description="The customer-facing reply.")
    citations: list[str] = Field(
        default_factory=list, description="Document sources supporting the reply."
    )


class ReviewResult(BaseModel):
    """Output of the Reviewer agent."""

    approved: bool = Field(description="True if the draft is grounded, complete, and helpful.")
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Calibrated confidence in the verdict 0-1; reserve >0.9 for clear-cut cases.",
    )
    feedback: list[str] = Field(
        default_factory=list, description="Actionable fixes when not approved."
    )
