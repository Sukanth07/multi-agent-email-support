"""Retrieval Validator agent: judge whether retrieved docs can answer the email."""

from support_agent.agents.base import BaseAgent
from support_agent.agents.formatting import format_bullets, format_documents
from support_agent.llm.prompts import RETRIEVAL_VALIDATOR_PROMPT
from support_agent.models.schemas import RetrievalAssessment, RetrievedDoc


class RetrievalValidatorAgent(BaseAgent[RetrievalAssessment]):
    name = "retrieval_validator"
    prompt = RETRIEVAL_VALIDATOR_PROMPT
    schema = RetrievalAssessment

    def validate(
        self, email: str, queries: list[str], docs: list[RetrievedDoc]
    ) -> RetrievalAssessment:
        return self.run(
            email=email,
            queries=format_bullets(queries),
            documents=format_documents(docs),
        )
