"""Chroma stores: uploads vs crawled website (separate persist dirs)."""

from __future__ import annotations

from pathlib import Path
from threading import Lock
from typing import Literal

from langchain_chroma import Chroma
from langchain_core.documents import Document

from app.config.settings import get_settings
from app.services.embedding import get_embeddings

CorpusMode = Literal["merged", "website", "uploads"]

_lock = Lock()
_store: Chroma | None = None
_website_store: Chroma | None = None


def _persist_path() -> Path:
    s = get_settings()
    path = Path(s.vector_store.persist_directory).resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


def _website_persist_path() -> Path:
    s = get_settings()
    path = Path(s.website_vector_store.persist_directory).resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


def _build_store() -> Chroma:
    return Chroma(
        persist_directory=str(_persist_path()),
        collection_name=get_settings().vector_store.collection_name,
        embedding_function=get_embeddings(),
    )


def _build_website_store() -> Chroma:
    s = get_settings()
    return Chroma(
        persist_directory=str(_website_persist_path()),
        collection_name=s.website_vector_store.collection_name,
        embedding_function=get_embeddings(),
    )


def get_vector_store() -> Chroma:
    """Uploads and other non-crawl ingestion (``vector_store`` in config)."""
    global _store
    with _lock:
        if _store is None:
            _store = _build_store()
        return _store


def get_website_vector_store() -> Chroma:
    """Crawled site pages only (``website_vector_store`` in config)."""
    global _website_store
    with _lock:
        if _website_store is None:
            _website_store = _build_website_store()
        return _website_store


def add_documents(documents: list[Document]) -> None:
    if not documents:
        raise ValueError("No documents to index")
    store = get_vector_store()
    store.add_documents(documents)


def add_website_documents(documents: list[Document]) -> None:
    if not documents:
        raise ValueError("No documents to index")
    store = get_website_vector_store()
    store.add_documents(documents)


def similarity_search(
    query: str,
    *,
    corpus: CorpusMode = "merged",
) -> list[Document]:
    """Retrieve chunks: ``merged`` (uploads + site), ``website`` only, or ``uploads`` only."""
    s = get_settings()
    q = (query or "").strip()
    if not q:
        return []
    if corpus == "website":
        return get_website_vector_store().similarity_search(
            q,
            k=s.website_vector_store.top_k,
        )
    if corpus == "uploads":
        return get_vector_store().similarity_search(
            q,
            k=s.vector_store.top_k,
        )
    if corpus != "merged":
        raise ValueError(f"unknown corpus: {corpus!r}")
    upload_store = get_vector_store()
    web_store = get_website_vector_store()
    docs_up = upload_store.similarity_search(
        q,
        k=s.vector_store.top_k,
    )
    docs_web = web_store.similarity_search(
        q,
        k=s.website_vector_store.top_k,
    )
    return docs_up + docs_web


def reset_vector_store_for_tests() -> None:
    global _store, _website_store
    with _lock:
        _store = None
        _website_store = None
