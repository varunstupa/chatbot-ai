"""Simple in-memory rate limiting per client key (IP)."""

from __future__ import annotations

import time
from collections import defaultdict
from threading import Lock

_store: dict[str, list[float]] = defaultdict(list)
_lock = Lock()


def check_rate_limit(
    key: str,
    *,
    max_calls: int,
    window_seconds: int,
) -> None:
    """
    Raise ValueError if ``key`` exceeded ``max_calls`` in ``window_seconds``.
    """
    now = time.monotonic()
    cutoff = now - window_seconds
    with _lock:
        hits = _store[key]
        hits[:] = [t for t in hits if t > cutoff]
        if len(hits) >= max_calls:
            raise ValueError(
                "Too many requests. Please wait a moment and try again.",
            )
        hits.append(now)


def reset_rate_limits_for_tests() -> None:
    with _lock:
        _store.clear()
