"""Read internal support documents and split them into retrievable chunks."""

from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from support_agent.config import get_settings
from support_agent.exceptions import KnowledgeBaseError
from support_agent.logger import get_logger

logger = get_logger("rag.loader")


def _read_documents(docs_dir: Path) -> list[Document]:
    """Load each markdown file as a single document with source metadata."""
    files = sorted(docs_dir.glob("*.md"))
    if not files:
        raise KnowledgeBaseError(f"No markdown documents found in {docs_dir}")

    documents: list[Document] = []
    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise KnowledgeBaseError(f"Failed to read {path}: {exc}") from exc
        title = path.stem.replace("_", " ").title()
        metadata = {"source": path.name, "title": title}
        documents.append(Document(page_content=text, metadata=metadata))
    return documents


def load_documents() -> list[Document]:
    """Return the knowledge base split into overlapping chunks."""
    settings = get_settings()
    documents = _read_documents(settings.docs_dir)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    chunks = splitter.split_documents(documents)
    logger.info("Loaded %d documents into %d chunks", len(documents), len(chunks))
    return chunks
