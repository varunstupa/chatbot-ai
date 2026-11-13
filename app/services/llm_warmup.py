"""Load the local model into Ollama's memory before the first question.

Loading qwen3.5:4b from disk takes about 40 s on CPU, and Ollama only does it on the first request
(or after local_keep_alive without one). The admin widget asks for the screen info as soon as an
event page opens, which calls warm_up_in_background(): the model loads while the user reads the
page. A call while the model is loaded returns at once and only renews keep_alive.
"""

from __future__ import annotations

import threading
import time

import httpx

from app.config.settings import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# At most one warm-up request per this many seconds, however many screens open.
MIN_INTERVAL_SECONDS = 60
_LOAD_TIMEOUT_SECONDS = 300

_lock = threading.Lock()
_last_started = 0.0


def warm_up_in_background() -> None:
    """Ask Ollama to load the model, without waiting. Never raises."""
    global _last_started
    with _lock:
        now = time.monotonic()
        if _last_started and now - _last_started < MIN_INTERVAL_SECONDS:
            return
        _last_started = now
    threading.Thread(target=_load, name="llm-warm-up", daemon=True).start()


def _load() -> None:
    global _last_started
    llm = get_settings().llm
    started = time.monotonic()
    try:
        # An empty prompt only loads the model (Ollama API), and keep_alive keeps it there.
        httpx.post(
            f"{llm.local_base_url.rstrip('/')}/api/generate",
            json={"model": llm.local_model_name, "keep_alive": llm.local_keep_alive},
            timeout=_LOAD_TIMEOUT_SECONDS,
        ).raise_for_status()
        logger.info("llm_warm_up | ready in %.1fs", time.monotonic() - started)
    except Exception as e:
        logger.warning("llm_warm_up_failed | %s", type(e).__name__)
        with _lock:
            _last_started = 0.0  # the next screen tries again
