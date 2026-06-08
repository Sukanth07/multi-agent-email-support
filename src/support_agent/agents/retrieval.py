"""Retrieval agent: search the vector store with the generated queries.

Unlike the other agents this performs no LLM call; it runs each query against the
FAISS index and returns deduplicated documents, keeping the best score per chunk.
"""

from langchain_core.documents import Document

from support_agent.exceptions import AgentError, VectorStoreError
from support_agent.logger import get_logger
from support_agent.models.schemas import RetrievedDoc
from support_agent.rag.vector_store import VectorStore


class RetrievalAgent:
    name = "retrieval"

    def __init__(self) -> None:
        self._logger = get_logger("agents.retrieval")
        self._store = VectorStore.load()

    def retrieve(self, queries: list[str], k: int | None = None) -> list[RetrievedDoc]:
        """Search every query and return unique documents, closest first."""
        self._logger.info("retrieving for %d queries", len(queries))
        best: dict[str, tuple[Document, float]] = {}
        try:
            for query in queries:
                for doc, score in self._store.search(query, k=k):
                    key = f"{doc.metadata.get('source', '')}|{doc.page_content}"
                    if key not in best or score < best[key][1]:
                        best[key] = (doc, score)
        except VectorStoreError as exc:
            raise AgentError(self.name, str(exc)) from exc

        docs = [
            RetrievedDoc(
                content=doc.page_content,
                source=doc.metadata.get("source", ""),
                title=doc.metadata.get("title", ""),
                score=score,
            )
            for doc, score in best.values()
        ]
        docs.sort(key=lambda d: d.score)
        self._logger.info("retrieved %d unique docs", len(docs))
        return docs
