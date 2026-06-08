"""Build the FAISS index from internal docs.

Run once before starting the app, and again whenever the documents change:

    python scripts/build_index.py
"""

from support_agent.logger import get_logger
from support_agent.rag.loader import load_documents
from support_agent.rag.vector_store import build_index

logger = get_logger("scripts.build_index")


def main() -> None:
    logger.info("Building knowledge index...")
    chunks = load_documents()
    build_index(chunks)
    logger.info("Index ready.")


if __name__ == "__main__":
    main()
