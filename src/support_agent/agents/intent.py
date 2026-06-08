"""Intent agent: classify the email and generate retrieval queries."""

from support_agent.agents.base import BaseAgent
from support_agent.llm.prompts import INTENT_PROMPT
from support_agent.models.schemas import IntentResult


class IntentAgent(BaseAgent[IntentResult]):
    name = "intent"
    prompt = INTENT_PROMPT
    schema = IntentResult

    def classify(self, email: str) -> IntentResult:
        return self.run(email=email)
