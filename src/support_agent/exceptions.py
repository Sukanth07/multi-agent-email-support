"""Custom exception hierarchy.

All recoverable failures inherit from `SupportAgentError` so callers can catch the
base type, while specific subtypes allow targeted handling and clear logging.
"""


class SupportAgentError(Exception):
    """Base class for all application errors."""


class ConfigurationError(SupportAgentError):
    """Raised when settings are missing or invalid."""


class KnowledgeBaseError(SupportAgentError):
    """Raised when knowledge base documents cannot be loaded."""


class VectorStoreError(SupportAgentError):
    """Raised when building, loading, or querying the FAISS index fails."""


class LLMError(SupportAgentError):
    """Raised when an LLM or embeddings call fails."""


class AgentError(SupportAgentError):
    """Raised when an agent fails to produce a valid result.

    Carries the agent's name to make logs and traces unambiguous.
    """

    def __init__(self, agent: str, message: str) -> None:
        self.agent = agent
        super().__init__(f"[{agent}] {message}")
