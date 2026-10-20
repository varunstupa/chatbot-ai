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
def _no_did_you_mean(monkeypatch):
    """"Did you mean" calls the model; tests that need it patch it themselves."""
    from app.services import app_chat

    monkeypatch.setattr(app_chat, "did_you_mean", lambda *a, **kw: None)


@pytest.fixture(autouse=True)
def _no_query_rewrite(monkeypatch):
    """The weak-question rewrite calls the model; retrieval tests must not depend on it."""
    from app.services import query_rewrite

    monkeypatch.setattr(query_rewrite, "rewrite", lambda question: None)
