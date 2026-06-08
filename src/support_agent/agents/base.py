"""Shared base class for LLM-backed agents.

Each agent declares a name, a prompt, and an output schema. The base class builds
the `prompt | structured-model` chain once, runs it, logs, and wraps any failure in
`AgentError`. A second chain bound to the fallback model is built alongside, and
`run` automatically retries on it when the primary call fails (e.g. rate-limited).
This keeps the concrete agents to a few lines and free of duplication.
"""

from typing import Any, Generic, TypeVar, cast

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from support_agent.exceptions import AgentError
from support_agent.llm.client import get_chat_model, get_fallback_chat_model
from support_agent.logger import get_logger

T = TypeVar("T", bound=BaseModel)


class BaseAgent(Generic[T]):
    """Runs a prompt against the chat model and returns a validated schema object."""

    name: str
    prompt: ChatPromptTemplate
    schema: type[T]

    def __init__(self) -> None:
        self._logger = get_logger(f"agents.{self.name}")
        self._chain = self.prompt | get_chat_model().with_structured_output(self.schema)
        self._fallback_chain = (
            self.prompt | get_fallback_chat_model().with_structured_output(self.schema)
        )

    def run(self, **inputs: Any) -> T:
        """Invoke the primary chain; on failure, retry once on the fallback chain."""
        self._logger.info("running")
        try:
            result = self._chain.invoke(inputs)
            self._logger.info("done")
            return cast(T, result)
        except Exception as primary_exc:
            self._logger.warning(
                "primary model failed (%s); retrying on fallback", type(primary_exc).__name__
            )
            try:
                result = self._fallback_chain.invoke(inputs)
            except Exception as fallback_exc:
                raise AgentError(
                    self.name,
                    f"primary and fallback both failed (primary: {primary_exc}; "
                    f"fallback: {fallback_exc})",
                ) from fallback_exc
            self._logger.info("done (via fallback)")
            return cast(T, result)
