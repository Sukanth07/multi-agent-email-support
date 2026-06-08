"""Writer agent: draft the customer reply from the plan and documents."""

from support_agent.agents.base import BaseAgent
from support_agent.agents.formatting import format_bullets, format_documents, format_plan
from support_agent.llm.prompts import WRITER_PROMPT
from support_agent.models.schemas import ResponsePlan, RetrievedDoc, WriterOutput


class WriterAgent(BaseAgent[WriterOutput]):
    name = "writer"
    prompt = WRITER_PROMPT
    schema = WriterOutput

    def write(
        self,
        plan: ResponsePlan,
        docs: list[RetrievedDoc],
        feedback: list[str] | None = None,
    ) -> WriterOutput:
        return self.run(
            plan=format_plan(plan),
            documents=format_documents(docs),
            feedback=format_bullets(feedback or []),
        )
