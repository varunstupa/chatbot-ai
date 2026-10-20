"""Cross-encoder reranker for the admin-chat passages.

The embedding search compares the question and each passage separately; a cross-encoder
reads them together, so it is better at telling the passage that answers the question
from one that only shares its words. Used on the few candidates left after the limits.
"""

from __future__ import annotations

from threading import Lock
from typing import Any

from app.config.settings import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

_lock = Lock()
_model: Any = None
_failed = False


def _get_model() -> Any:
    """The cross-encoder, loaded on first use; None when it cannot be loaded."""
    global _model, _failed
    with _lock:
        if _model is None and not _failed:
            cfg = get_settings().app_chat
            try:
                from sentence_transformers import CrossEncoder

                _model = CrossEncoder(cfg.rerank_model, max_length=512)
                logger.info("reranker_loaded | model=%s", cfg.rerank_model)
            except Exception:
                # Answers still work without it: the embedding order is kept.
                _failed = True
                logger.exception("reranker_unavailable | model=%s", cfg.rerank_model)
        return _model


def scores(question: str, passages: list[str]) -> list[float] | None:
    """Raw relevance score of each passage (higher is better); None when unavailable."""
    if not passages:
        return []
    model = _get_model()
    if model is None:
        return None
    raw = model.predict([(question, p) for p in passages])
    return [float(x) for x in raw]


def warm_up() -> None:
    if get_settings().app_chat.rerank:
        _get_model()


def reset_for_tests() -> None:
    global _model, _failed
    with _lock:
        _model, _failed = None, False
