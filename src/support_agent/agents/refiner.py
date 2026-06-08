"""Refiner agent: re-understand the email after retrieval failed.

Used by the retrieval recovery loop. Given the failed attempt and the validator's
reason, it re-classifies the intent (correcting it if it was wrong) and generates
new search queries. It reuses the IntentResult schema so it can update the same
state fields the intent agent set.
"""

from support_agent.agents.base import BaseAgent
from support_agent.llm.prompts import REFINE_PROMPT
from support_agent.models.schemas import IntentResult


class RefinerAgent(BaseAgent[IntentResult]):
    name = "refiner"
    prompt = REFINE_PROMPT
    schema = IntentResult

    def refine(self, email: str, intent: str, queries: list[str], reason: str) -> IntentResult:
        queries_text = ", ".join(queries) or "(none)"
        return self.run(email=email, intent=intent, queries=queries_text, reason=reason)
