"""Tests for the document loader (reads real docs, no embeddings)."""

from support_agent.rag.loader import load_documents


def test_load_documents_returns_chunks_with_metadata() -> None:
    chunks = load_documents()
    assert len(chunks) > 0
    for chunk in chunks:
        assert chunk.page_content.strip()
        assert chunk.metadata["source"].endswith(".md")
        assert chunk.metadata["title"]
