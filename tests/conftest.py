"""Shared test setup."""

from __future__ import annotations

import pytest

from app.services import chat_store


@pytest.fixture(autouse=True)
def _no_real_chat_store(monkeypatch):
    """Tests that start the app must never write into a developer's local MongoDB."""

    async def _off() -> None:
        return None

    monkeypatch.setattr(chat_store, "start", _off)


@pytest.fixture(autouse=True)
def _no_real_traces(monkeypatch):
    """Tests that start the app must never send traces, even with a key in .env."""
    from app.services import tracing

    monkeypatch.setattr(tracing, "start", lambda: None)


@pytest.fixture(autouse=True)
def _no_did_you_mean(monkeypatch):
    """"Did you mean" calls the model; tests that need it patch it themselves."""
    from app.services import app_chat

    monkeypatch.setattr(app_chat, "did_you_mean", lambda *a, **kw: None)


@pytest.fixture(autouse=True)
def _no_question_routing(monkeypatch):
    """Routing reads the real index; unit tests patch it themselves when they need it."""
    from app.knowledge import service

    monkeypatch.setattr(service, "route_question", lambda *a, **kw: [])


@pytest.fixture(autouse=True)
def _no_query_rewrite(monkeypatch):
    """The weak-question rewrite calls the model; retrieval tests must not depend on it."""
    from app.services import query_rewrite

    monkeypatch.setattr(query_rewrite, "rewrite", lambda question: None)


@pytest.fixture(autouse=True)
def _limits_off(monkeypatch):
    """Question limits are off unless a test turns them on (tests/test_chat_limits.py)."""
    from app.config.settings import get_settings

    monkeypatch.setattr(get_settings().chat_limits, "mode", "off")


@pytest.fixture(autouse=True)
def _no_real_knowledge_documents(monkeypatch):
    """Tests that start the app must never connect to the MongoDB in .env for uploaded documents."""
    from app.knowledge import documents

    monkeypatch.setattr(documents, "start", lambda: None)
