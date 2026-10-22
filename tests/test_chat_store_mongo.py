"""Chat store against a real MongoDB server.

Uses a local MongoDB (or TEST_MONGODB_URI) and a new throwaway database per test, dropped
afterwards. Skipped when no server is reachable, as in CI.
"""

from __future__ import annotations

import asyncio
import os
import uuid
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from pymongo import MongoClient

from app.api.dependencies import get_rag_pipeline
from app.main import app
from app.services import chat_store
from tests.test_app_chat_isolation import DETAILS_ROUTE, auth, kb  # noqa: F401  (kb is a fixture)
from tests.test_multilingual import GERMAN_QUESTION, NO_ANSWER_DE, ScriptedPipeline

MONGO_URI = os.environ.get("TEST_MONGODB_URI", "mongodb://127.0.0.1:27017")
# conftest.py replaces chat_store.start for every test; keep the real one for the startup tests.
REAL_START = chat_store.start


def _mongo_available() -> bool:
    try:
        MongoClient(MONGO_URI, serverSelectionTimeoutMS=500).admin.command("ping")
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _mongo_available(), reason=f"no MongoDB reachable at {MONGO_URI}")

SESSION_KEYS = {
    "_id", "tenant", "session_id", "user_id", "role", "started_at", "last_message_at",
    "last_route", "last_screen_title", "message_count", "not_found_count", "error_count", "messages",
}
MESSAGE_KEYS = {
    "question", "answer", "outcome", "route", "screen_title", "sport", "language",
    "retrieval_mode", "doc_ids", "sources", "model", "first_token_ms", "total_ms",
    "streamed", "created_at", "message_id", "feedback",
}


class Clock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


def rec(tenant: str, session: str, question: str, outcome: str = "answered", **kw) -> chat_store.ChatRecord:
    return chat_store.ChatRecord(
        tenant=tenant, session_id=session, question=question, answer=f"answer to {question}",
        outcome=outcome, user_id="u1", role="Admin", **kw,
    )


@pytest.fixture()
def db_name():
    name = f"test_chat_store_{uuid.uuid4().hex[:10]}"
    yield name
    client = MongoClient(MONGO_URI)
    client.drop_database(name)
    client.close()


def sessions(db_name: str):
    """Synchronous view of the test database's collection, for assertions."""
    return MongoClient(MONGO_URI, tz_aware=True)[db_name][chat_store.SESSIONS]


def new_store(db_name: str, clock: Clock | None = None, **kw) -> chat_store.ChatStore:
    # A long check interval: the tests decide when to write, not the background task.
    opts = dict(check_seconds=3600, idle_seconds=1800, safety_seconds=600)
    return chat_store.ChatStore(MONGO_URI, db_name, clock=clock or Clock(), **{**opts, **kw})


async def write_all(store: chat_store.ChatStore) -> None:
    """Close every buffered session and write it."""
    for tenant, sid in list(store.sessions):
        store.close_session(tenant, sid)
    await store.flush()


# ---------- startup: collection, indexes, TTL ----------


def test_start_creates_collection_and_indexes(db_name):
    async def run():
        store = new_store(db_name, retention_days=30)
        await store.start()
        await store.stop()

    asyncio.run(run())
    coll = sessions(db_name)
    assert sorted(coll.database.list_collection_names()) == ["chat_feedback", "chat_sessions"]
    idx = coll.index_information()
    assert idx["tenant_session"]["key"] == [("tenant", 1), ("session_id", 1)]
    assert idx["tenant_session"]["unique"] is True
    assert idx["tenant_recent"]["key"] == [("tenant", 1), ("last_message_at", -1)]
    assert idx["tenant_message_outcome"]["key"] == [("tenant", 1), ("messages.outcome", 1)]
    assert idx["ttl_last_message_at"]["expireAfterSeconds"] == 30 * 24 * 3600


def test_start_twice_is_harmless(db_name):
    async def run():
        for _ in range(2):
            store = new_store(db_name)
            await store.start()
            await store.stop()

    asyncio.run(run())
    assert len(sessions(db_name).index_information()) == 5  # _id + 4, no duplicates


def test_changing_retention_updates_the_ttl_index(db_name):
    async def run():
        for days in (30, 90):
            store = new_store(db_name, retention_days=days)
            await store.start()
            await store.stop()

    asyncio.run(run())
    assert sessions(db_name).index_information()["ttl_last_message_at"]["expireAfterSeconds"] == 90 * 24 * 3600


def test_retention_zero_removes_the_ttl_index(db_name):
    async def run():
        for days in (30, 0):
            store = new_store(db_name, retention_days=days)
            await store.start()
            await store.stop()

    asyncio.run(run())
    assert "ttl_last_message_at" not in sessions(db_name).index_information()


# ---------- document shape ----------


def test_session_document_shape_and_types(db_name):
    async def run():
        store = new_store(db_name)
        await store.start()
        store.record(rec(
            "denmark", "s1", "How do I delete a player?", route="tms/players/:event_id",
            screen_title="Players page", sport="table_tennis", language="en", retrieval_mode="screen",
            doc_ids=["tms.players.queue-delete-forfeit"],
            sources=[{"title": "Players page – queue", "section": "Deleting players"}],
            model="qwen3.5:4b-q4_K_M", first_token_ms=900, total_ms=4200, streamed=True,
        ))
        await write_all(store)
        await store.stop()

    asyncio.run(run())
    doc = sessions(db_name).find_one({"tenant": "denmark", "session_id": "s1"})
    assert set(doc) == SESSION_KEYS
    assert (doc["user_id"], doc["role"], doc["message_count"]) == ("u1", "Admin", 1)
    assert isinstance(doc["started_at"], datetime) and doc["started_at"].tzinfo is not None
    assert doc["started_at"] <= doc["last_message_at"]
    [msg] = doc["messages"]
    assert set(msg) == MESSAGE_KEYS  # tenant/session/user are stored once, on the session
    assert msg["doc_ids"] == ["tms.players.queue-delete-forfeit"]
    assert msg["sources"] == [{"title": "Players page – queue", "section": "Deleting players"}]
    assert (msg["first_token_ms"], msg["total_ms"], msg["streamed"]) == (900, 4200, True)
    assert isinstance(msg["created_at"], datetime)


def test_non_english_text_and_long_answers_round_trip(db_name):
    long_answer = "Schritt. " * 20000  # about 180 KB
    async def run():
        store = new_store(db_name)
        await store.start()
        store.record(chat_store.ChatRecord(
            tenant="denmark", session_id="s1", question="मैं खिलाड़ी को कैसे हटाऊँ?",
            answer=long_answer, outcome="answered", language="hi",
        ))
        store.record(rec("denmark", "s1", "Wie füge ich einen Spieler hinzu? ⋮ → Add"))
        await write_all(store)
        await store.stop()

    asyncio.run(run())
    msgs = sessions(db_name).find_one({"tenant": "denmark", "session_id": "s1"})["messages"]
    assert msgs[0]["question"] == "मैं खिलाड़ी को कैसे हटाऊँ?"
    assert msgs[0]["answer"] == long_answer
    assert msgs[1]["question"] == "Wie füge ich einen Spieler hinzu? ⋮ → Add"


# ---------- writing: append, counts, order ----------


def test_writes_append_to_the_same_document_and_counts_add_up(db_name):
    clock = Clock()

    async def run():
        store = new_store(db_name, clock)
        await store.start()
        store.record(rec("denmark", "s1", "q1", route="tms/players/:event_id"))
        await write_all(store)
        clock.now += 60
        store.record(rec("denmark", "s1", "q2", outcome="not_found"))
        store.record(rec("denmark", "s1", "q3", outcome="error", route="tms/event-settings/create-event/:event_id"))
        await write_all(store)
        await store.stop()

    asyncio.run(run())
    coll = sessions(db_name)
    assert coll.count_documents({}) == 1
    doc = coll.find_one()
    assert [m["question"] for m in doc["messages"]] == ["q1", "q2", "q3"]
    assert (doc["message_count"], doc["not_found_count"], doc["error_count"]) == (3, 1, 1)
    assert doc["last_route"] == "tms/event-settings/create-event/:event_id"
    first, last = doc["messages"][0]["created_at"], doc["messages"][-1]["created_at"]
    assert doc["started_at"] == first  # set once, on the first write
    assert doc["last_message_at"] == last


def test_nothing_is_written_while_a_session_is_active(db_name):
    clock = Clock()

    async def run():
        store = new_store(db_name, clock)
        await store.start()
        for n in range(5):
            store.record(rec("denmark", "s1", f"q{n}"))
            clock.now += 100  # a question every 100 s: never idle, under the 10-minute safety write
            assert await store.flush() == 0
        assert sessions(db_name).count_documents({}) == 0
        clock.now += 1800  # now idle
        assert await store.flush() == 5
        await store.stop()

    asyncio.run(run())
    assert sessions(db_name).find_one()["message_count"] == 5


def test_safety_write_keeps_the_session_open(db_name):
    clock = Clock()

    async def run():
        store = new_store(db_name, clock)
        await store.start()
        store.record(rec("denmark", "s1", "q1"))
        clock.now += 600  # oldest unwritten message is 10 minutes old
        store.record(rec("denmark", "s1", "q2"))
        assert await store.flush() == 2
        assert ("denmark", "s1") in store.sessions  # still open, not forgotten
        store.record(rec("denmark", "s1", "q3"))
        await store.stop()  # shutdown writes the rest

    asyncio.run(run())
    doc = sessions(db_name).find_one()
    assert [m["question"] for m in doc["messages"]] == ["q1", "q2", "q3"]


def test_message_cap_keeps_the_newest_across_writes(db_name):
    async def run():
        store = new_store(db_name, max_messages_per_session=3)
        await store.start()
        for batch in (("q1", "q2"), ("q3", "q4")):
            for q in batch:
                store.record(rec("denmark", "s1", q))
            await write_all(store)
        await store.stop()

    asyncio.run(run())
    doc = sessions(db_name).find_one()
    assert [m["question"] for m in doc["messages"]] == ["q2", "q3", "q4"]
    assert doc["message_count"] == 4  # the count still covers the whole session


def test_shutdown_writes_every_open_session(db_name):
    async def run():
        store = new_store(db_name)
        await store.start()
        store.record(rec("denmark", "s1", "q1"))
        store.record(rec("ettu", "s2", "q2"))
        await store.stop()

    asyncio.run(run())
    assert sessions(db_name).count_documents({}) == 2


# ---------- tenants and sessions ----------


def test_same_session_id_in_two_tenants_gives_two_documents(db_name):
    async def run():
        store = new_store(db_name)
        await store.start()
        store.record(rec("denmark", "s1", "denmark question"))
        store.record(rec("ettu", "s1", "ettu question"))
        await write_all(store)
        await store.stop()

    asyncio.run(run())
    coll = sessions(db_name)
    assert coll.count_documents({"session_id": "s1"}) == 2
    assert [m["question"] for m in coll.find_one({"tenant": "ettu"})["messages"]] == ["ettu question"]
    assert [m["question"] for m in coll.find_one({"tenant": "denmark"})["messages"]] == ["denmark question"]


def test_tenant_query_returns_only_that_tenant(db_name):
    async def run():
        store = new_store(db_name)
        await store.start()
        for tenant, sid in (("denmark", "a"), ("denmark", "b"), ("ettu", "c")):
            store.record(rec(tenant, sid, "q"))
        await write_all(store)
        await store.stop()

    asyncio.run(run())
    found = sorted(d["session_id"] for d in sessions(db_name).find({"tenant": "denmark"}))
    assert found == ["a", "b"]


def test_unanswered_query_uses_the_outcome_index(db_name):
    async def run():
        store = new_store(db_name)
        await store.start()
        store.record(rec("denmark", "s1", "q", outcome="not_found"))
        store.record(rec("denmark", "s2", "q"))
        await write_all(store)
        await store.stop()

    asyncio.run(run())
    coll = sessions(db_name)
    query = {"tenant": "denmark", "messages.outcome": "not_found"}
    assert [d["session_id"] for d in coll.find(query)] == ["s1"]
    assert "tenant_message_outcome" in str(coll.find(query).explain()["queryPlanner"]["winningPlan"])


def test_two_chatbot_instances_writing_one_session_share_one_document(db_name):
    """Two instances (or a retry) upserting the same new session at once: one document."""
    async def run():
        a, b = new_store(db_name), new_store(db_name)
        await a.start()
        await b.start()
        a.record(rec("denmark", "s1", "from instance a"))
        b.record(rec("denmark", "s1", "from instance b"))
        await asyncio.gather(write_all(a), write_all(b))
        await a.stop()
        await b.stop()

    asyncio.run(run())
    coll = sessions(db_name)
    assert coll.count_documents({"tenant": "denmark", "session_id": "s1"}) == 1
    doc = coll.find_one()
    assert sorted(m["question"] for m in doc["messages"]) == ["from instance a", "from instance b"]
    assert doc["message_count"] == 2


# ---------- failures ----------


def test_failed_write_keeps_messages_for_retry(db_name):
    async def run():
        store = new_store(db_name)
        await store.start()
        store.record(rec("denmark", "s1", "q1"))
        store.close_session("denmark", "s1")
        real = store.db

        class Down:
            def __getitem__(self, name):
                raise ConnectionError("database down")

        store.db = Down()
        assert await store.flush() == 0
        assert store.buffered == 1  # kept in memory
        store.record(rec("denmark", "s1", "q2"))  # more arrives while MongoDB is down
        store.db = real
        store.close_session("denmark", "s1")
        assert await store.flush() == 2
        await store.stop()

    asyncio.run(run())
    doc = sessions(db_name).find_one()
    assert [m["question"] for m in doc["messages"]] == ["q1", "q2"]  # order kept after the retry


def test_unreachable_server_turns_the_store_off_without_raising(monkeypatch):
    s = chat_store.get_settings()
    monkeypatch.setattr(s.chat_store, "enabled", True)
    monkeypatch.setattr(s.chat_store, "mongodb_uri", "mongodb://127.0.0.1:1")  # nothing listens here
    monkeypatch.setattr(s, "chat_store_mongodb_uri", None)  # ignore CHAT_STORE_MONGODB_URI from .env
    monkeypatch.setattr(chat_store, "_store", None)

    asyncio.run(REAL_START())
    assert chat_store._store is None
    chat_store.record(rec("denmark", "s1", "q"))  # no-op, no exception
    chat_store.close_session("denmark", "s1")


# ---------- end to end: chat API -> buffer -> MongoDB ----------


def test_chat_request_and_close_signal_end_up_in_mongodb(kb, db_name, monkeypatch):  # noqa: F811
    store = new_store(db_name)
    monkeypatch.setattr(chat_store, "_store", store)
    app.dependency_overrides[get_rag_pipeline] = lambda: ScriptedPipeline(["NO_ANSWER"])
    try:
        client = TestClient(app)
        body = {"question": GERMAN_QUESTION, "screen": {"route": DETAILS_ROUTE}, "session_id": "e2e-session-1"}
        r = client.post("/api/app-chat", json=body, headers={"accept": "application/json", **auth("ettu")})
        assert r.status_code == 200
        r = client.post("/api/app-chat/session/close", json={"session_id": "e2e-session-1"}, headers=auth("ettu"))
        assert r.status_code == 204
    finally:
        app.dependency_overrides.clear()

    async def run():
        await store.start()
        assert await store.flush() == 1  # due because of the close signal
        await store.stop()

    asyncio.run(run())
    doc = sessions(db_name).find_one({"tenant": "ettu", "session_id": "e2e-session-1"})
    assert doc is not None and doc["user_id"] == "u1"
    [msg] = doc["messages"]
    assert msg["question"] == GERMAN_QUESTION
    assert (msg["answer"], msg["outcome"], msg["language"]) == (NO_ANSWER_DE, "not_found", "de")
    assert msg["route"] == DETAILS_ROUTE
    assert sessions(db_name).count_documents({"tenant": "denmark"}) == 0


# ---------- thumbs up/down feedback ----------


def feedback_docs(db_name: str) -> list[dict]:
    return list(MongoClient(MONGO_URI, tz_aware=True)[db_name][chat_store.FEEDBACK].find({}, {"_id": 0}))


def test_vote_is_stored_with_its_question_and_answer(db_name):
    async def run():
        store = new_store(db_name)
        await store.start()
        item = rec("denmark", "s1", "How do I publish?", route="tms/x", doc_ids=["tms.a"])
        store.record(item)
        assert await store.save_feedback("denmark", "u1", item.message_id, "down", " wrong page ")
        await store.stop()
        return item

    item = asyncio.run(run())
    [doc] = feedback_docs(db_name)
    assert doc["rating"] == "down" and doc["status"] == "open" and doc["comment"] == "wrong page"
    assert (doc["question"], doc["answer"], doc["route"], doc["doc_ids"]) == (
        "How do I publish?", "answer to How do I publish?", "tms/x", ["tms.a"])
    # The vote is also in the session document, which was still unwritten.
    msg = sessions(db_name).find_one({"session_id": "s1"})["messages"][0]
    assert msg["message_id"] == item.message_id and msg["feedback"] == "down"


def test_voting_again_changes_the_vote(db_name):
    async def run():
        store = new_store(db_name)
        await store.start()
        item = rec("denmark", "s1", "q")
        store.record(item)
        await store.save_feedback("denmark", "u1", item.message_id, "down", None)
        await store.save_feedback("denmark", "u1", item.message_id, "up", None)
        await store.stop()

    asyncio.run(run())
    docs = feedback_docs(db_name)
    assert len(docs) == 1 and docs[0]["rating"] == "up"


def test_only_the_answering_user_of_the_tenant_can_vote(db_name):
    async def run():
        store = new_store(db_name)
        await store.start()
        item = rec("denmark", "s1", "q")
        store.record(item)
        results = [
            await store.save_feedback("norway", "u1", item.message_id, "down", None),
            await store.save_feedback("denmark", "someone-else", item.message_id, "down", None),
            await store.save_feedback("denmark", "u1", "0" * 32, "down", None),
        ]
        await store.stop()
        return results

    assert asyncio.run(run()) == [False, False, False]
    assert feedback_docs(db_name) == []


def test_review_list_and_status(db_name):
    async def run():
        store = new_store(db_name)
        await store.start()
        good, bad = rec("denmark", "s1", "good"), rec("denmark", "s1", "bad")
        store.record(good)
        store.record(bad)
        await store.save_feedback("denmark", "u1", good.message_id, "up", None)
        await store.save_feedback("denmark", "u1", bad.message_id, "down", None)
        open_down = await store.list_feedback("denmark", "down", "open", 10)
        changed = await store.set_feedback_status("denmark", bad.message_id, "fixed", "guide updated")
        still_open = await store.list_feedback("denmark", "down", "open", 10)
        await store.stop()
        return open_down, changed, still_open

    open_down, changed, still_open = asyncio.run(run())
    assert [d["question"] for d in open_down] == ["bad"]
    assert changed == 1 and still_open == []


def test_answers_carry_a_message_id_and_feedback_endpoint_saves_it(db_name, kb, monkeypatch):  # noqa: F811
    store = new_store(db_name)
    monkeypatch.setattr(chat_store, "_store", store)
    votes = []

    async def fake_save(tenant, user_id, message_id, rating, comment=None):
        votes.append((tenant, user_id, message_id, rating, comment))
        return "saved" if message_id in store.recent else "unknown"

    monkeypatch.setattr(chat_store, "save_feedback", fake_save)
    app.dependency_overrides[get_rag_pipeline] = lambda: ScriptedPipeline(["Turn on Publish."])
    try:
        client = TestClient(app)
        body = {"question": "How do I publish?", "screen": {"route": DETAILS_ROUTE}}
        answer = client.post("/api/app-chat", json=body, headers={"accept": "application/json", **auth()}).json()
        message_id = answer["message_id"]
        assert store.recent[message_id].answer == "Turn on Publish."
        stream = client.post("/api/app-chat", json=body, headers={"accept": "text/event-stream", **auth()})
        done = [line for line in stream.text.splitlines() if '"type": "done"' in line][0]
        assert '"message_id"' in done
        vote = {"message_id": message_id, "rating": "down", "comment": "not this page"}
        r = client.post("/api/app-chat/feedback", json=vote, headers=auth())
        assert r.status_code == 200 and r.json() == {"saved": True, "rating": "down"}
        assert votes[-1][2:] == (message_id, "down", "not this page")
        assert client.post("/api/app-chat/feedback", json={**vote, "message_id": "f" * 32},
                           headers=auth()).status_code == 404
        assert client.post("/api/app-chat/feedback", json={**vote, "rating": "maybe"},
                           headers=auth()).status_code == 422
    finally:
        app.dependency_overrides.clear()
