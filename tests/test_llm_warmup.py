"""The model is loaded in the background when a screen opens, at most once a minute."""

from __future__ import annotations

import threading

import httpx
import pytest

from app.services import llm_warmup


class _InlineThread:
    """Runs the target at start(), so the test sees the request."""

    def __init__(self, target, **kw):
        self._target = target

    def start(self):
        self._target()


@pytest.fixture
def posts(monkeypatch):
    calls = []

    def fake_post(url, json, timeout):
        calls.append((url, json))
        return httpx.Response(200, request=httpx.Request("POST", url))

    monkeypatch.setattr(llm_warmup, "_last_started", 0.0)
    monkeypatch.setattr(llm_warmup.threading, "Thread", _InlineThread)
    monkeypatch.setattr(llm_warmup.httpx, "post", fake_post)
    return calls


def test_loads_the_configured_model_with_keep_alive(posts):
    llm_warmup.warm_up_in_background()
    llm = llm_warmup.get_settings().llm
    assert posts == [(
        f"{llm.local_base_url.rstrip('/')}/api/generate",
        {"model": llm.local_model_name, "keep_alive": llm.local_keep_alive},
    )]


def test_many_screens_send_one_request_per_minute(posts, monkeypatch):
    clock = [1000.0]
    monkeypatch.setattr(llm_warmup.time, "monotonic", lambda: clock[0])
    for _ in range(5):
        llm_warmup.warm_up_in_background()
    clock[0] += llm_warmup.MIN_INTERVAL_SECONDS + 1
    llm_warmup.warm_up_in_background()
    assert len(posts) == 2


def test_a_failure_is_retried_by_the_next_screen(posts, monkeypatch):
    def down(*a, **kw):
        raise httpx.ConnectError("ollama is down")

    monkeypatch.setattr(llm_warmup.httpx, "post", down)
    llm_warmup.warm_up_in_background()  # never raises
    assert llm_warmup._last_started == 0.0


def test_the_screen_route_does_not_wait_for_the_model(monkeypatch):
    started = threading.Event()
    release = threading.Event()

    def slow_post(*a, **kw):
        started.set()
        release.wait(5)
        return httpx.Response(200, request=httpx.Request("POST", "http://x"))

    monkeypatch.setattr(llm_warmup, "_last_started", 0.0)
    monkeypatch.setattr(llm_warmup.httpx, "post", slow_post)
    llm_warmup.warm_up_in_background()
    assert started.wait(5)  # the request is running in the background ...
    release.set()           # ... and the caller already returned
