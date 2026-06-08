"""FAISS vector store backed by local FastEmbed embeddings."""

from functools import lru_cache

from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from support_agent.config import get_settings
from support_agent.exceptions import VectorStoreError
from support_agent.logger import get_logger

logger = get_logger("rag.vector_store")


@lru_cache
def _embeddings() -> FastEmbedEmbeddings:
    """Return the cached embedding model (downloaded once, then reused)."""
    return FastEmbedEmbeddings(model_name=get_settings().embedding_model)


def build_index(documents: list[Document]) -> None:
    """Embed the chunks and persist a FAISS index to disk."""
    if not documents:
        raise VectorStoreError("Cannot build an index from zero documents.")

    settings = get_settings()
    try:
        index = FAISS.from_documents(documents, _embeddings())
        index.save_local(str(settings.faiss_index_dir))
    except Exception as exc:
        raise VectorStoreError(f"Failed to build FAISS index: {exc}") from exc

    logger.info("Built FAISS index (%d chunks) at %s", len(documents), settings.faiss_index_dir)


class VectorStore:
    """Loaded FAISS index exposing similarity search."""

    def __init__(self, index: FAISS) -> None:
        self._index = index

    @classmethod
    def load(cls) -> "VectorStore":
        """Load the persisted index, or fail clearly if it is missing."""
        settings = get_settings()
        if not settings.faiss_index_dir.exists():
            raise VectorStoreError(
                f"FAISS index not found at {settings.faiss_index_dir}. "
                "Run `python scripts/build_index.py` first."
            )
        try:
            index = FAISS.load_local(
                str(settings.faiss_index_dir),
                _embeddings(),
                allow_dangerous_deserialization=True,
            )
        except Exception as exc:
            raise VectorStoreError(f"Failed to load FAISS index: {exc}") from exc

        logger.info("Loaded FAISS index from %s", settings.faiss_index_dir)
        return cls(index)

    def search(self, query: str, k: int | None = None) -> list[tuple[Document, float]]:
        """Return the top matching chunks with their similarity distance."""
        top_k = k or get_settings().retrieval_top_k
        try:
            return self._index.similarity_search_with_score(query, k=top_k)
        except Exception as exc:
            raise VectorStoreError(f"Search failed for query '{query}': {exc}") from exc
