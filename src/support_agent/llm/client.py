"""Single factory for the Groq chat models.

This is the only place chat models are constructed and the only place the Groq API
key is required. A primary model is used by default and a fallback model is exposed
so that agents can transparently retry on the fallback when the primary call fails
(e.g. rate-limited).
"""

from functools import lru_cache

from langchain_groq import ChatGroq

from support_agent.config import get_settings
from support_agent.exceptions import ConfigurationError, LLMError
from support_agent.logger import get_logger

logger = get_logger("llm.client")


@lru_cache(maxsize=2)
def _chat_model(model_name: str) -> ChatGroq:
    """Build a Groq chat model by name (cached per name)."""
    settings = get_settings()
    if settings.groq_api_key is None:
        raise ConfigurationError("GROQ_API_KEY is not set. Add it to your .env file.")

    try:
        model = ChatGroq(
            model=model_name,
            temperature=settings.llm_temperature,
            api_key=settings.groq_api_key,
        )
    except Exception as exc:
        raise LLMError(f"Failed to initialize Groq chat model '{model_name}': {exc}") from exc

    logger.info("Initialized Groq chat model '%s'", model_name)
    return model


def get_chat_model() -> ChatGroq:
    """Return the cached primary chat model."""
    return _chat_model(get_settings().chat_model)


def get_fallback_chat_model() -> ChatGroq:
    """Return the cached fallback chat model, used when the primary call fails."""
    return _chat_model(get_settings().fallback_chat_model)
