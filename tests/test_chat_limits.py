"""Per-user question limits: Redis counters, sync to MongoDB, MongoDB fallback, recovery.

Uses the local Redis (127.0.0.1:6379, database 15) and the local MongoDB (a throwaway database per
test); each is skipped when it is not reachable. Redis "down" is a client pointed at a closed
port, MongoDB "down" likewise.
"""

from __future__ import annotations

import asyncio
import os
import socket
import uuid
from datetime import datetime, timezone

import pytest
import redis.asyncio as aioredis
from pydantic import ValidationError
from pymongo import AsyncMongoClient, MongoClient

from app.config.settings import ChatLimitsConfig, get_settings
from app.services import chat_limits as cl
from app.services import chat_usage_sync as sync
from app.services.auth import CallerScope
from tests.test_app_chat_isolation import kb  # noqa: F401  (fixture)

MONGO_URI = os.environ.get("TEST_MONGODB_URI", "mongodb://127.0.0.1:27017")
REDIS_URL = os.environ.get("TEST_REDIS_URL", "redis://127.0.0.1:6379/15")
DEAD = "redis://127.0.0.1:1/0"  # nothing listens here


def _port_open(port: int) -> bool:
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


needs_stores = pytest.mark.skipif(
    not (_port_open(27017) and _port_open(6379)), reason="local MongoDB and Redis are needed"
)


# ---------- windows, limits and configuration (no stores) ----------


def test_windows_roll_over_at_local_midnight_monday_and_month_start():
    before = cl.current_windows("Asia/Kolkata", datetime(2026, 10, 31, 18, 29, 59, tzinfo=timezone.utc))
    after = cl.current_windows("Asia/Kolkata", datetime(2026, 10, 31, 18, 30, 0, tzinfo=timezone.utc))
    assert before.keys == {"daily": "2026-10-31", "weekly": "2026-W44", "monthly": "2026-10"}
    assert after.keys == {"daily": "2026-11-01", "weekly": "2026-W44", "monthly": "2026-11"}  # Sunday
    monday = cl.current_windows("Asia/Kolkata", datetime(2026, 11, 1, 18, 30, 0, tzinfo=timezone.utc))
    assert monday.keys["weekly"] == "2026-W45"
    assert before.resets_at["daily"].isoformat() == "2026-11-01T00:00:00+05:30"
    assert before.resets_at["weekly"].isoformat() == "2026-11-02T00:00:00+05:30"
    new_year = cl.current_windows("Asia/Kolkata", datetime(2026, 12, 31, 20, 0, tzinfo=timezone.utc))
    assert new_year.keys == {"daily": "2027-01-01", "weekly": "2026-W53", "monthly": "2027-01"}


def test_daylight_saving_day_resets_at_local_midnight():
    # Europe/Copenhagen moves to summer time on 29 March 2026.
    w = cl.current_windows("Europe/Copenhagen", datetime(2026, 3, 28, 12, tzinfo=timezone.utc))
    assert w.resets_at["daily"].isoformat() == "2026-03-29T00:00:00+01:00"
    after = cl.current_windows("Europe/Copenhagen", datetime(2026, 3, 29, 12, tzinfo=timezone.utc))
    assert after.resets_at["daily"].isoformat() == "2026-03-30T00:00:00+02:00"


def test_limits_resolve_role_then_tenant_then_default(monkeypatch):
    cfg = ChatLimitsConfig(
        default={"daily": 10, "weekly": 50, "monthly": 100},
        tenants={"denmark": {"daily": 20, "weekly": 0}},
        roles={"Admin": {"daily": 30}},
    )
    monkeypatch.setattr(get_settings(), "chat_limits", cfg)
    assert cl.limits_for(CallerScope("staging", "u", "Player")) == {"daily": 10, "weekly": 50, "monthly": 100}
    assert cl.limits_for(CallerScope("denmark", "u", "Player")) == {"daily": 20, "weekly": 0, "monthly": 100}
    assert cl.limits_for(CallerScope("denmark", "u", "Admin")) == {"daily": 30, "weekly": 0, "monthly": 100}


def test_invalid_configuration_is_refused():
    with pytest.raises(ValidationError):
        ChatLimitsConfig(default={"daily": -1})
    with pytest.raises(ValidationError):
        ChatLimitsConfig(timezone="Mars/Olympus")
    with pytest.raises(ValidationError):
        ChatLimitsConfig(retention_days=0)


def test_keys_keep_tenants_apart_and_share_one_slot_per_user():
    a = cl.counter_key("staging", "u:1", "daily", "2026-10-22")
    b = cl.counter_key("staging:u", "1", "daily", "2026-10-22")
    assert a != b
    assert a.startswith("chatq:{staging:u%3A1}:d:")


# ---------- with Redis and MongoDB ----------


@pytest.fixture()
def env(monkeypatch):
    """A ChatLimits on a fresh Redis database and a throwaway MongoDB database, daily limit 10."""
    db_name = f"test_chat_limits_{uuid.uuid4().hex[:10]}"
    tenant = f"t{uuid.uuid4().hex[:8]}"
    cfg = ChatLimitsConfig(mode="enforce", default={"daily": 10, "weekly": 40, "monthly": 100},
                           drain_seconds=0.2, redis_retry_seconds=0.2, claim_idle_seconds=0.2)
    monkeypatch.setattr(get_settings(), "chat_limits", cfg)
    created = []

    async def build(redis_url: str = REDIS_URL, mongo_uri: str = MONGO_URI) -> cl.ChatLimits:
        lim = cl.ChatLimits()
        lim.mongo = AsyncMongoClient(mongo_uri, serverSelectionTimeoutMS=800, connectTimeoutMS=800, tz_aware=True)
        lim.db = lim.mongo[db_name]
        if mongo_uri == MONGO_URI:
            await sync.ensure_indexes(lim.db, 400)
            lim._indexes_ready = True
        client = aioredis.from_url(redis_url, decode_responses=True, socket_timeout=0.5, socket_connect_timeout=0.5)
        lim.attach_redis(client)
        if redis_url == REDIS_URL:
            await client.flushdb()
            await sync.ensure_group(client)
            lim.state = "up"
        created.append(lim)
        return lim

    yield {"build": build, "tenant": tenant, "db": db_name}
    MongoClient(MONGO_URI).drop_database(db_name)


def run(coro):
    return asyncio.run(coro)


def scope(env, user="u1", role="Organiser"):
    return CallerScope(env["tenant"], user, role)


@needs_stores
def test_ten_questions_allowed_then_the_eleventh_is_refused_without_counting(env):
    async def go():
        lim = await env["build"]()
        for _ in range(10):
            res = await lim.reserve(scope(env))
            await lim.commit(res, "answered")
        with pytest.raises(cl.LimitDenied) as denied:
            await lim.reserve(scope(env))
        w = cl.current_windows("Asia/Kolkata")
        value = await lim.redis.get(cl.counter_key(env["tenant"], "u1", "daily", w.keys["daily"]))
        await lim.redis.aclose()
        return denied.value.payload, value

    payload, value = run(go())
    assert payload["code"] == "chat_limit_reached" and payload["window"] == "daily"
    assert payload["used"] == {"daily": 10, "weekly": 10, "monthly": 10}
    assert payload["limits"] == {"daily": 10, "weekly": 40, "monthly": 100}
    assert payload["resets_at"].endswith("+05:30")
    assert value == "10"  # the refused question did not count


@needs_stores
def test_100_concurrent_questions_with_limit_50_allow_exactly_50(env, monkeypatch):
    monkeypatch.setattr(get_settings().chat_limits.default, "daily", 50)
    monkeypatch.setattr(get_settings().chat_limits.default, "weekly", 200)

    async def go():
        lim = await env["build"]()

        async def one():
            try:
                await lim.reserve(scope(env))
                return True
            except cl.LimitDenied:
                return False

        results = await asyncio.gather(*(one() for _ in range(100)))
        await lim.redis.aclose()
        return sum(results)

    assert run(go()) == 50


@needs_stores
def test_refund_once_never_after_commit_and_never_below_zero(env):
    async def go():
        lim = await env["build"]()
        w = cl.current_windows("Asia/Kolkata")
        key = cl.counter_key(env["tenant"], "u1", "daily", w.keys["daily"])
        a = await lim.reserve(scope(env))
        await lim.refund(a)
        a.settled = False
        await lim.refund(a)  # second refund of the same reservation: no change
        after_refunds = await lim.redis.get(key)
        b = await lim.reserve(scope(env))
        await lim.commit(b, "answered")
        b.settled = False
        await lim.refund(b)  # refund after commit: ignored
        after_commit = await lim.redis.get(key)
        await lim.redis.aclose()
        return after_refunds, after_commit

    assert run(go()) == ("0", "1")


@needs_stores
def test_two_tenants_with_the_same_user_id_are_independent(env):
    async def go():
        lim = await env["build"]()
        for _ in range(10):
            await lim.reserve(scope(env, "same"))
        other = await lim.reserve(CallerScope(env["tenant"] + "x", "same", "Organiser"))
        await lim.redis.aclose()
        return other.usage["used"]["daily"]

    assert run(go()) == 1


@needs_stores
def test_counts_reach_mongodb_once_even_when_events_are_delivered_twice(env):
    async def go():
        lim = await env["build"]()
        for i in range(4):
            res = await lim.reserve(scope(env))
            await (lim.commit(res, "answered") if i < 3 else lim.refund(res))
        events = [f for _, f in await lim.redis.xrange(sync.STREAM)]
        await lim.drainer.drain_once()
        await sync.apply_events(lim.db, events)  # the same events again
        w = cl.current_windows("Asia/Kolkata")
        day = await lim.db[sync.USAGE].find_one({"tenant": env["tenant"], "period": "day"})
        quota = await lim.db[sync.QUOTA].find_one({"tenant": env["tenant"]})
        left = await lim.redis.xlen(sync.STREAM)
        await lim.redis.aclose()
        return day, quota, w, left

    day, quota, w, left = run(go())
    assert (day["count"], day["answered"], day["refunded"], day["period_key"]) == (3, 3, 1, w.keys["daily"])
    assert quota["d"] == {"key": w.keys["daily"], "n": 3}
    assert left == 0  # acknowledged and deleted


@needs_stores
def test_events_of_a_crashed_drainer_are_taken_over_and_counted_once(env):
    async def go():
        lim = await env["build"]()
        for _ in range(3):
            await lim.reserve(scope(env))
        # Pod A reads the events and "crashes" before writing or acknowledging them.
        await lim.redis.xreadgroup(sync.GROUP, "pod-a", {sync.STREAM: ">"}, count=100)
        await asyncio.sleep(0.3)  # longer than claim_idle_seconds
        lim.drainer.consumer = "pod-b"
        await lim.drainer.drain_once()
        day = await lim.db[sync.USAGE].find_one({"tenant": env["tenant"], "period": "day"})
        pending = (await lim.redis.xpending(sync.STREAM, sync.GROUP))["pending"]
        await lim.redis.aclose()
        return day["count"], pending

    assert run(go()) == (3, 0)


@needs_stores
def test_missing_redis_counters_are_seeded_from_mongodb(env):
    async def go():
        lim = await env["build"]()
        for _ in range(7):
            await lim.reserve(scope(env))
        await lim.drainer.drain_once()
        await lim.redis.flushdb()  # Redis lost its data
        await sync.ensure_group(lim.redis)
        res = await lim.reserve(scope(env))
        await lim.redis.aclose()
        return res.usage["used"]["daily"]

    assert run(go()) == 8


@needs_stores
def test_redis_down_uses_mongodb_exactly_and_recovery_reseeds(env):
    async def go():
        lim = await env["build"]()
        for _ in range(4):
            await lim.reserve(scope(env))
        # 4 in Redis; only 2 of them synced to MongoDB before Redis fails.
        rows = await lim.redis.xrange(sync.STREAM)
        await sync.apply_events(lim.db, [f for _, f in rows[:2]])
        healthy = lim.redis
        lim.attach_redis(aioredis.from_url(DEAD, decode_responses=True, socket_timeout=0.3,
                                           socket_connect_timeout=0.3))
        lim.state = "up"
        first = await lim.reserve(scope(env))          # trips the breaker, falls back to MongoDB
        assert first.backend == "mongo" and lim.state == "down"
        allowed = 1
        while True:
            try:
                await lim.reserve(scope(env))
                allowed += 1
            except cl.LimitDenied:
                break
        outage = await lim.db[sync.OUTAGE_USERS].count_documents({})
        # Redis is back: sync what it still holds, then re-seed the outage users.
        if lim._retry_task:
            lim._retry_task.cancel()
        lim.attach_redis(healthy)
        lim.state = "recovering"
        await lim.drainer.drain_all()
        reseeded = await lim._clear_outage_users()
        lim.state = "up"
        after = None
        try:
            await lim.reserve(scope(env))
        except cl.LimitDenied as e:
            after = e.payload["used"]["daily"]
        await healthy.aclose()
        return allowed, outage, reseeded, after

    allowed, outage, reseeded, after = run(go())
    # MongoDB knew 2 of the 4 questions: the fallback allowed 10 - 2 = 8 (overshoot of 2, documented).
    assert allowed == 8
    assert outage == 1 and reseeded == 1
    # After recovery the 2 unsynced questions are counted too: 2 + 2 + 8 = 12 >= 10, so refused.
    assert after == 12


@needs_stores
def test_concurrent_fallback_reserves_never_exceed_the_limit(env, monkeypatch):
    monkeypatch.setattr(get_settings().chat_limits.default, "daily", 50)
    monkeypatch.setattr(get_settings().chat_limits.default, "weekly", 200)

    async def go():
        lim = await env["build"](redis_url=DEAD)
        lim.state = "down"

        async def one():
            try:
                await lim.reserve(scope(env))
                return True
            except cl.LimitDenied:
                return False

        results = await asyncio.gather(*(one() for _ in range(100)))
        quota = await lim.db[sync.QUOTA].find_one({"tenant": env["tenant"]})
        if lim._retry_task:
            lim._retry_task.cancel()
        return sum(results), quota["d"]["n"]

    assert run(go()) == (50, 50)


@needs_stores
def test_fallback_refund_happens_once(env):
    async def go():
        lim = await env["build"](redis_url=DEAD)
        lim.state = "down"
        res = await lim.reserve(scope(env))
        await lim.refund(res)
        res.settled = False
        await lim.refund(res)
        quota = await lim.db[sync.QUOTA].find_one({"tenant": env["tenant"]})
        day = await lim.db[sync.USAGE].find_one({"tenant": env["tenant"], "period": "day"})
        return quota["d"]["n"], day["count"], day["refunded"]

    assert run(go()) == (0, 0, 1)


@needs_stores
def test_redis_and_mongodb_both_down_refuse_with_unavailable(env):
    async def go():
        lim = await env["build"](redis_url=DEAD, mongo_uri="mongodb://127.0.0.1:1")
        lim.state = "down"
        with pytest.raises(cl.LimitsUnavailable):
            await lim.reserve(scope(env))

    run(go())


@needs_stores
def test_observe_mode_counts_but_never_refuses(env, monkeypatch):
    monkeypatch.setattr(get_settings().chat_limits, "mode", "observe")

    async def go():
        lim = await env["build"]()
        for _ in range(12):
            res = await lim.reserve(scope(env))
        await lim.redis.aclose()
        return res.usage["used"]["daily"]

    assert run(go()) == 12


def test_missing_user_is_refused_when_limits_are_on(monkeypatch):
    monkeypatch.setattr(get_settings().chat_limits, "mode", "enforce")
    with pytest.raises(cl.MissingUser):
        run(cl.ChatLimits().reserve(CallerScope("staging", "", "Admin")))


@needs_stores
def test_mongodb_down_while_redis_is_up_keeps_limits_and_syncs_later(env):
    async def go():
        lim = await env["build"]()
        healthy_db = lim.db
        dead = AsyncMongoClient("mongodb://127.0.0.1:1", serverSelectionTimeoutMS=300, connectTimeoutMS=300)
        lim.db = dead["x"]  # MongoDB "down"
        for _ in range(10):
            res = await lim.reserve(scope(env))       # Redis still enforces
            await lim.commit(res, "answered")
        with pytest.raises(cl.LimitDenied):
            await lim.reserve(scope(env))
        with pytest.raises(Exception):
            await lim.drainer.drain_once()            # the sync fails ...
        pending = (await lim.redis.xpending(sync.STREAM, sync.GROUP))["pending"]
        lim.db = healthy_db                          # MongoDB is back
        await lim.drainer.drain_once()               # ... and the same events are synced once
        day = await lim.db[sync.USAGE].find_one({"tenant": env["tenant"], "period": "day"})
        left = (await lim.redis.xpending(sync.STREAM, sync.GROUP))["pending"]
        await lim.redis.aclose()
        return pending, day["count"], day["answered"], left

    pending, count, answered, left = run(go())
    assert pending == 20            # 10 reserve + 10 commit events kept, not lost
    assert (count, answered, left) == (10, 10, 0)


# ---------- reservations made by the gateway (HTTP) ----------


@pytest.fixture()
def gateway_api(env, kb, monkeypatch):  # noqa: F811  (kb comes from test_app_chat_isolation)
    """The app with a ChatLimits on the test stores, daily limit 2, and a scripted answer."""
    import redis as sync_redis
    from fastapi.testclient import TestClient

    from app.api.dependencies import get_rag_pipeline
    from app.main import app
    from tests.test_multilingual import ScriptedPipeline

    monkeypatch.setattr(get_settings().chat_limits.default, "daily", 2)
    sync_redis.Redis.from_url(REDIS_URL).flushdb()
    lim = cl.ChatLimits()  # async clients are created here but first used inside the app's loop
    lim.mongo = AsyncMongoClient(MONGO_URI, tz_aware=True)
    lim.db = lim.mongo[env["db"]]
    lim._indexes_ready = True
    lim.attach_redis(aioredis.from_url(REDIS_URL, decode_responses=True))
    lim.state = "up"
    monkeypatch.setattr(cl, "limits", lim)

    async def keep_test_stores() -> None:  # app startup/shutdown must not swap in the .env stores
        return None

    monkeypatch.setattr(lim, "start", keep_test_stores)
    monkeypatch.setattr(lim, "stop", keep_test_stores)
    app.dependency_overrides[get_rag_pipeline] = lambda: ScriptedPipeline(["Open Players from the sidebar."])
    with TestClient(app) as client:  # one event loop for every request (the async clients bind to it)
        yield client, lim
    app.dependency_overrides.clear()


def _daily(lim_key_tenant="denmark", user="u1") -> str | None:
    import redis as sync_redis

    w = cl.current_windows("Asia/Kolkata")
    return sync_redis.Redis.from_url(REDIS_URL, decode_responses=True).get(
        cl.counter_key(lim_key_tenant, user, "daily", w.keys["daily"]))


@needs_stores
def test_gateway_reserves_then_the_chatbot_uses_that_reservation(gateway_api):
    from tests.test_app_chat_isolation import DETAILS_ROUTE, auth

    client, _ = gateway_api
    reserved = client.post("/api/app-chat/quota/reserve", headers=auth())
    assert reserved.status_code == 200 and reserved.json()["usage"]["used"]["daily"] == 1
    request_id = reserved.json()["request_id"]
    body = {"question": "Where is the players page?", "screen": {"route": DETAILS_ROUTE}}
    answer = client.post("/api/app-chat", json=body,
                         headers={"accept": "application/json", "x-chat-request-id": request_id, **auth()})
    assert answer.status_code == 200 and answer.json()["message_id"] == request_id
    assert _daily() == "1"  # the chatbot did not count the question a second time
    again = client.post("/api/app-chat", json=body,
                        headers={"accept": "application/json", "x-chat-request-id": request_id, **auth()})
    assert again.status_code == 409  # a reservation is used once
    assert client.post("/api/app-chat", json=body, headers={"accept": "application/json",
                       "x-chat-request-id": "f" * 32, **auth()}).status_code == 409


@needs_stores
def test_gateway_reserve_is_refused_at_the_limit_and_refund_gives_it_back(gateway_api):
    from tests.test_app_chat_isolation import auth

    client, _ = gateway_api
    first = client.post("/api/app-chat/quota/reserve", headers=auth()).json()["request_id"]
    client.post("/api/app-chat/quota/reserve", headers=auth())
    refused = client.post("/api/app-chat/quota/reserve", headers=auth())
    assert refused.status_code == 429 and refused.json()["detail"]["code"] == "chat_limit_reached"
    assert client.post(f"/api/app-chat/quota/{first}/refund", headers=auth()).json() == {"refunded": True}
    assert client.post(f"/api/app-chat/quota/{first}/refund", headers=auth()).json() == {"refunded": False}
    assert _daily() == "1"
    other_user = client.post(f"/api/app-chat/quota/{first}/refund", headers=auth("ettu"))
    assert other_user.json() == {"refunded": False}  # only the owner can refund
