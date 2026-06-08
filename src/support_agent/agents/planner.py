"""Planner agent: turn intent and documents into a response strategy."""

from support_agent.agents.base import BaseAgent
from support_agent.agents.formatting import format_documents
from support_agent.llm.prompts import PLANNER_PROMPT
from support_agent.models.schemas import ResponsePlan, RetrievedDoc


class PlannerAgent(BaseAgent[ResponsePlan]):
    name = "planner"
    prompt = PLANNER_PROMPT
    schema = ResponsePlan

    def plan(self, email: str, intent: str, summary: str, docs: list[RetrievedDoc]) -> ResponsePlan:
        return self.run(
            email=email,
            intent=intent,
            summary=summary,
            documents=format_documents(docs),
        )
