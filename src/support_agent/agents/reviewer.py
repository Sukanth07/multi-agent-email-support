"""Reviewer agent: validate the draft reply before it reaches the customer."""

from support_agent.agents.base import BaseAgent
from support_agent.agents.formatting import format_documents, format_plan
from support_agent.llm.prompts import REVIEWER_PROMPT
from support_agent.models.schemas import ResponsePlan, RetrievedDoc, ReviewResult


class ReviewerAgent(BaseAgent[ReviewResult]):
    name = "reviewer"
    prompt = REVIEWER_PROMPT
    schema = ReviewResult

    def review(
        self,
        email: str,
        plan: ResponsePlan,
        draft: str,
        docs: list[RetrievedDoc],
    ) -> ReviewResult:
        return self.run(
            email=email,
            plan=format_plan(plan),
            draft=draft,
            documents=format_documents(docs),
        )
