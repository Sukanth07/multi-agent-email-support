"""Tests for vector store error handling (no embeddings / network needed)."""

from pathlib import Path

import pytest

from support_agent.config import get_settings
from support_agent.exceptions import VectorStoreError
from support_agent.rag.vector_store import VectorStore, build_index


def test_build_index_rejects_empty_documents() -> None:
    with pytest.raises(VectorStoreError):
        build_index([])


def test_load_missing_index_raises(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    settings = get_settings()
    monkeypatch.setattr(settings, "faiss_index_dir", tmp_path / "does_not_exist")
    with pytest.raises(VectorStoreError):
        VectorStore.load()
