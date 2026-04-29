"""Chroma vector store (singleton) with config-driven collection, persist path, and retrieval."""

from __future__ import annotations

from pathlib import Path
from threading import Lock

from langchain_chroma import Chroma
from langchain_core.documents import Document

from app.config.settings import get_settings
from app.services.embedding import get_embeddings

_lock = Lock()
_store: Chroma | None = None


def _persist_path() -> Path:
    s = get_settings()
    path = Path(s.vector_store.persist_directory).resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


def _build_store() -> Chroma:
    return Chroma(
        persist_directory=str(_persist_path()),
        collection_name=get_settings().vector_store.collection_name,
        embedding_function=get_embeddings(),
    )


def get_vector_store() -> Chroma:
    global _store
    with _lock:
        if _store is None:
            _store = _build_store()
        return _store


def add_documents(documents: list[Document]) -> None:
    if not documents:
        raise ValueError("No documents to index")
    store = get_vector_store()
    store.add_documents(documents)


def similarity_search(query: str) -> list[Document]:
    s = get_settings()
    store = get_vector_store()
    return store.similarity_search(query, k=s.vector_store.top_k)


def reset_vector_store_for_tests() -> None:
    global _store
    with _lock:
        _store = None
