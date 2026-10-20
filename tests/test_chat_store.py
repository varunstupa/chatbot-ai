"""Chat store: every admin-chat question/answer is recorded per tenant and session."""

from __future__ import annotations

import asyncio
import uuid

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_rag_pipeline
from app.main import app
from app.services import chat_store
from tests.test_app_chat_isolation import DETAILS_ROUTE, auth, kb  # noqa: F401  (kb is a fixture)
from tests.test_multilingual import GERMAN_QUESTION, NO_ANSWER_DE, ScriptedPipeline

SESSION = "sess-12345678"


@pytest.fixture()
def recorded(kb, monkeypatch):  # noqa: F811
    """Captures what the API hands to the chat store; no database needed."""
    items: list[chat_store.ChatRecord] = []
    monkeypatch.setattr(chat_store, "record", items.append)

    def make(tokens: list[str]) -> TestClient:
        app.dependency_overrides[get_rag_pipeline] = lambda: ScriptedPipeline(tokens)
        return TestClient(app)

    yield items, make
    app.dependency_overrides.clear()


def _ask(client: TestClient, question: str, *, stream: bool, tenant: str = "denmark"):
    body = {"question": question, "screen": {"route": DETAILS_ROUTE}, "session_id": SESSION}
    accept = "text/event-stream" if stream else "application/json"
    return client.post("/api/app-chat", json=body, headers={"accept": accept, **auth(tenant)})


# ---------- what the API records ----------


def test_json_answer_is_recorded(recorded):
    items, make = recorded
    r = _ask(make(["The thumbnail must be 379 x 200 px."]), "What size is the thumbnail?", stream=False)
    assert r.status_code == 200
    [rec] = items
    assert (rec.tenant, rec.user_id, rec.session_id) == ("denmark", "u1", SESSION)
    assert rec.question == "What size is the thumbnail?"
    assert rec.answer == "The thumbnail must be 379 x 200 px."
    assert rec.outcome == chat_store.ANSWERED
    assert rec.route == DETAILS_ROUTE
    assert rec.streamed is False and rec.total_ms is not None


def test_streamed_answer_is_recorded_once(recorded):
    items, make = recorded
    _ask(make(["The thumbnail", " must be 379 x 200 px."]), "What size is the thumbnail?", stream=True)
    [rec] = items
    assert rec.answer == "The thumbnail must be 379 x 200 px."
    assert rec.outcome == chat_store.ANSWERED
    assert rec.streamed is True and rec.first_token_ms is not None


@pytest.mark.parametrize("tokens", [["NO_ANSWER"], ["Der Kontext enthält nichts dazu.", "\n\nNO_ANSWER"]])
@pytest.mark.parametrize("stream", [True, False])
def test_not_found_is_recorded_with_the_text_the_user_saw(recorded, tokens, stream):
    items, make = recorded
    _ask(make(tokens), GERMAN_QUESTION, stream=stream)
    [rec] = items
    assert rec.outcome == chat_store.NOT_FOUND
    assert rec.answer == NO_ANSWER_DE
    assert rec.language == "de"


def test_tenant_comes_from_the_signed_identity(recorded):
    items, make = recorded
    client = make(["ok answer"])
    _ask(client, "Question one?", stream=False, tenant="denmark")
    _ask(client, "Question two?", stream=False, tenant="ettu")
    assert [(r.tenant, r.question) for r in items] == [("denmark", "Question one?"), ("ettu", "Question two?")]


def test_a_failing_store_never_breaks_the_chat(kb, monkeypatch):  # noqa: F811
    class Broken:
        def record(self, item):
            raise RuntimeError("database down")

    monkeypatch.setattr(chat_store, "_store", Broken())
    app.dependency_overrides[get_rag_pipeline] = lambda: ScriptedPipeline(["Still answered."])
    try:
        r = _ask(TestClient(app), "What size is the thumbnail?", stream=False)
    finally:
        app.dependency_overrides.clear()
    assert r.status_code == 200 and r.json()["answer"] == "Still answered."




def test_close_endpoint_closes_the_callers_session(kb, monkeypatch):  # noqa: F811
    closed: list[tuple[str, str]] = []
    monkeypatch.setattr(chat_store, "close_session", lambda tenant, sid: closed.append((tenant, sid)))
    client = TestClient(app)
    r = client.post("/api/app-chat/session/close", json={"session_id": SESSION}, headers=auth("ettu"))
    assert r.status_code == 204
    # The tenant comes from the identity, so one tenant cannot close another's session.
    assert closed == [("ettu", SESSION)]
    r = client.post("/api/app-chat/session/close", json={"session_id": "bad id!"}, headers=auth("ettu"))
    assert r.status_code == 204 and len(closed) == 1  # malformed ids are ignored


def test_close_endpoint_needs_an_identity(kb):  # noqa: F811
    r = TestClient(app).post("/api/app-chat/session/close", json={"session_id": SESSION})
    assert r.status_code in (401, 403)


# ---------- when a session is written (memory only, no database) ----------


class Clock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


def _rec(tenant: str, session: str, question: str, outcome: str = "answered") -> chat_store.ChatRecord:
    return chat_store.ChatRecord(
        tenant=tenant, session_id=session, question=question, answer="a", outcome=outcome, user_id="u1"
    )


def _store(clock: Clock, **kw) -> chat_store.ChatStore:
    defaults = dict(idle_seconds=1800, safety_seconds=600, flush_at_messages=50)
    return chat_store.ChatStore("mongodb://unused", "unused", clock=clock, **{**defaults, **kw})


def _due(store) -> list[tuple[str, str]]:
    return store._sessions_to_write(force=False)


def test_active_session_is_not_written():
    clock = Clock()
    store = _store(clock)
    store.record(_rec("denmark", "s1", "q1"))
    clock.now += 60
    store.record(_rec("denmark", "s1", "q2"))
    assert _due(store) == []
    assert store.buffered == 2


def test_idle_session_is_written():
    clock = Clock()
    store = _store(clock)
    store.record(_rec("denmark", "s1", "q1"))
    clock.now += 1800
    assert _due(store) == [("denmark", "s1")]


def test_safety_write_for_a_session_still_in_use():
    clock = Clock()
    store = _store(clock)
    store.record(_rec("denmark", "s1", "q1"))
    for _ in range(4):  # a question every 3 minutes: never idle
        clock.now += 180
        store.record(_rec("denmark", "s1", "q"))
    assert clock.now - 1000 == 720 and _due(store) == [("denmark", "s1")]  # oldest unwritten > 10 min


def test_message_limit_and_close_make_a_session_due():
    store = _store(Clock(), flush_at_messages=3)
    for n in range(3):
        store.record(_rec("denmark", "s1", f"q{n}"))
    store.record(_rec("denmark", "s2", "q"))
    store.close_session("denmark", "s2")
    store.close_session("denmark", "unknown")  # ignored
    assert sorted(_due(store)) == [("denmark", "s1"), ("denmark", "s2")]


def test_close_only_affects_the_given_tenant():
    store = _store(Clock())
    store.record(_rec("denmark", "s1", "q"))
    store.record(_rec("ettu", "s1", "q"))
    store.close_session("ettu", "s1")
    assert _due(store) == [("ettu", "s1")]


def test_memory_limit_writes_everything_early():
    store = _store(Clock(), max_buffered_messages=3)
    store.record(_rec("denmark", "s1", "q"))
    store.record(_rec("denmark", "s2", "q"))
    store.record(_rec("ettu", "s3", "q"))
    assert len(_due(store)) == 3


def test_session_update_keeps_order_and_counts():
    items = [_rec("denmark", "s1", "q1"), _rec("denmark", "s1", "q2", "not_found")]
    update = chat_store.session_update(items, max_messages=500)._doc
    assert [m["question"] for m in update["$push"]["messages"]["$each"]] == ["q1", "q2"]
    assert update["$inc"] == {"message_count": 2, "not_found_count": 1, "error_count": 0}
    # Session-level fields are stored once on the session, not repeated per message.
    assert "tenant" not in update["$push"]["messages"]["$each"][0]

# MongoDB itself is tested in tests/test_chat_store_mongo.py.
