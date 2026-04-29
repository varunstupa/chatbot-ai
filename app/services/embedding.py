"""Singleton HuggingFace embedding model driven by settings."""

from __future__ import annotations

from threading import Lock

from langchain_community.embeddings import HuggingFaceEmbeddings

from app.config.settings import get_settings

_lock = Lock()
_embeddings: HuggingFaceEmbeddings | None = None


def get_embeddings() -> HuggingFaceEmbeddings:
    global _embeddings
    with _lock:
        if _embeddings is None:
            s = get_settings()
            _embeddings = HuggingFaceEmbeddings(
                model_name=s.embedding.model_name,
                model_kwargs=s.embedding.model_kwargs,
                encode_kwargs=s.embedding.encode_kwargs,
            )
        return _embeddings


def reset_embeddings_for_tests() -> None:
    global _embeddings
    with _lock:
        _embeddings = None
