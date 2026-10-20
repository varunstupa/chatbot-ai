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
            _embeddings = PrefixedEmbeddings(
                model_name=s.embedding.model_name,
                model_kwargs=s.embedding.model_kwargs,
                encode_kwargs=s.embedding.encode_kwargs,
                query_prefix=s.embedding.query_prefix,
                passage_prefix=s.embedding.passage_prefix,
            )
        return _embeddings


class PrefixedEmbeddings(HuggingFaceEmbeddings):
    """Adds the query/passage prefixes that E5-style models are trained with."""

    query_prefix: str = ""
    passage_prefix: str = ""

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return super().embed_documents([self.passage_prefix + t for t in texts])

    def embed_query(self, text: str) -> list[float]:
        return super().embed_query(self.query_prefix + text)


_knowledge_embeddings: PrefixedEmbeddings | None = None


def get_knowledge_embeddings() -> PrefixedEmbeddings:
    """Multilingual model for the admin-chat guides (``app_chat.embedding_model``).

    Separate from ``get_embeddings()`` so /stupa-chat keeps its own model and collections.
    """
    global _knowledge_embeddings
    with _lock:
        if _knowledge_embeddings is None:
            cfg = get_settings().app_chat
            _knowledge_embeddings = PrefixedEmbeddings(
                model_name=cfg.embedding_model,
                encode_kwargs={"normalize_embeddings": True},
                query_prefix=cfg.embedding_query_prefix,
                passage_prefix=cfg.embedding_passage_prefix,
            )
        return _knowledge_embeddings


def reset_embeddings_for_tests() -> None:
    global _embeddings, _knowledge_embeddings
    with _lock:
        _embeddings = None
        _knowledge_embeddings = None
