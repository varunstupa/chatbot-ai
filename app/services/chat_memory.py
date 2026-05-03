"""Session-scoped chat history for RunnableWithMessageHistory (in-memory, Redis-ready)."""

from __future__ import annotations

from collections import OrderedDict
from threading import Lock
from typing import Sequence

from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import BaseMessage

# Swap this dict for Redis-backed histories behind the same factory signature.
_MAX_STORED_SESSIONS = 10_000
_DEFAULT_HISTORY_CAP = 15
_store: OrderedDict[str, InMemoryChatMessageHistory] = OrderedDict()
_lock = Lock()


class TrimmingChatMessageHistory(InMemoryChatMessageHistory):
    """In-memory history that keeps only the last N messages."""

    max_messages: int = _DEFAULT_HISTORY_CAP

    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        super().add_messages(messages)
        m = self.messages
        cap = self.max_messages
        # Keep the most recent exchanges (token safety). Drop oldest, same list
        # identity, for predictable in-memory behavior across turns.
        while len(m) > cap:
            m.pop(0)


def get_message_history(session_id: str) -> InMemoryChatMessageHistory:
    """
    Return history for ``session_id``.

    Replace the body with ``RedisChatMessageHistory`` (or similar) later;
    keep this function name so callers stay stable.
    """
    if not session_id or not session_id.strip():
        raise ValueError("session_id must be non-empty")
    sid = session_id.strip()
    with _lock:
        if sid in _store:
            _store.move_to_end(sid)
            return _store[sid]
        _store[sid] = TrimmingChatMessageHistory()
        while len(_store) > _MAX_STORED_SESSIONS:
            _store.popitem(last=False)
        return _store[sid]


def reset_chat_memory_for_tests() -> None:
    """Clear all in-memory sessions (tests / dev only)."""
    with _lock:
        _store.clear()


def peek_history_len(session_id: str) -> int:
    """Return message count for ``session_id`` (0 if new). Used for debug logs."""
    sid = (session_id or "").strip()
    if not sid:
        return 0
    with _lock:
        h = _store.get(sid)
        return len(h.messages) if h else 0
