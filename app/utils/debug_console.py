"""Stdout debug lines (like ``console.log``). Enable with ``STUPA_DEBUG=1``."""

from __future__ import annotations

import os


def debug_log(*parts: object) -> None:
    """Print to stderr when ``STUPA_DEBUG`` is 1/true/yes."""
    flag = (os.environ.get("STUPA_DEBUG") or "").strip().lower()
    if flag not in ("1", "true", "yes"):
        return
    msg = " ".join(str(p) for p in parts)
    print(f"[stupa-debug] {msg}", flush=True)
