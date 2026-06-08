"""Application settings, loaded from the environment and `.env`."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Typed configuration for the support agent system."""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    groq_api_key: SecretStr | None = Field(default=None, description="Groq API key.")

    chat_model: str = "llama-3.3-70b-versatile"
    fallback_chat_model: str = "openai/gpt-oss-120b"
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    llm_temperature: float = 0.0

    docs_dir: Path = PROJECT_ROOT / "data" / "internal_docs"
    faiss_index_dir: Path = PROJECT_ROOT / "faiss_index"

    chunk_size: int = 800
    chunk_overlap: int = 120
    retrieval_top_k: int = 4

    max_retrieval_attempts: int = 2
    max_rewrite_attempts: int = 2

    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    """Return the cached settings instance."""
    return Settings()
