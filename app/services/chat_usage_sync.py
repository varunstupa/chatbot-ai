"""Sync of question usage from the Redis stream to MongoDB (see app/services/chat_limits.py).

Every reserve, commit and refund in Redis also adds an event to the stream ``chatq:events``.
Each pod reads the stream through one consumer group, writes the events to MongoDB and only
then acknowledges and deletes them. An event that is read but not acknowledged (the pod
crashed, MongoDB failed) stays pending: this pod reads it again, and another pod takes it
over once it has been idle for ``claim_idle_seconds``. An event that keeps failing moves to
``chatq:events:dead`` after ``max_deliveries`` attempts.

MongoDB writes are duplicate-safe: each document keeps the ids of the last 500 events
applied to it, and an update only matches a document that does not hold the event id yet.
A redelivered event therefore never counts twice.

Collections (database of the chat store):
- ``chat_usage``: one document per user and period (day, week, month) with
  count (questions, net of refunds), answered, not_found and refunded: the history.
- ``chat_quota``: one document per user with the current day, week and month counts:
  what the limit check falls back to when Redis is down, and what Redis is seeded from.
"""

from __future__ import annotations

import asyncio
import os
import socket
import time
from datetime import datetime, timezone

from pymongo import ASCENDING, UpdateOne
from pymongo.errors import BulkWriteError, DuplicateKeyError
from redis.exceptions import ResponseError

from app.utils.logger import get_logger

logger = get_logger(__name__)

STREAM = "chatq:events"
DEAD_STREAM = "chatq:events:dead"
GROUP = "chatq-drain"
USAGE = "chat_usage"
QUOTA = "chat_quota"
FALLBACK_REQUESTS = "chat_fallback_requests"
OUTAGE_USERS = "chat_outage_users"
APPLIED_KEEP = 500
_DUPLICATE_KEY = 11000

# Window letter in events -> (period name in chat_usage, field in chat_quota).
PERIODS = (("dk", "day", "d"), ("wk", "week", "w"), ("mk", "month", "m"))


def _now() -> datetime:
    return datetime.now(timezone.utc)


def consumer_name() -> str:
    return f"{socket.gethostname()}-{os.getpid()}"


# ---------- MongoDB: indexes and duplicate-safe writes ----------


async def ensure_indexes(db, retention_days: int) -> None:
    usage = db[USAGE]
    await usage.create_index(
        [("tenant", ASCENDING), ("user_id", ASCENDING), ("period", ASCENDING), ("period_key", ASCENDING)],
        name="tenant_user_period", unique=True,
    )
    await usage.create_index("updated_at", name="ttl_updated_at", expireAfterSeconds=retention_days * 86400)
    await db[QUOTA].create_index(
        [("tenant", ASCENDING), ("user_id", ASCENDING)], name="tenant_user", unique=True
    )
    await db[FALLBACK_REQUESTS].create_index("request_id", name="request_id", unique=True)
    await db[FALLBACK_REQUESTS].create_index("created_at", name="ttl_created_at", expireAfterSeconds=2 * 86400)
    await db[OUTAGE_USERS].create_index(
        [("tenant", ASCENDING), ("user_id", ASCENDING)], name="tenant_user", unique=True
    )


def usage_ops(event: dict) -> list[UpdateOne]:
    """The chat_usage updates for one event: one per period (day, week, month)."""
    kind = event["type"]
    if kind == "reserve":
        inc = {"count": 1}
    elif kind == "refund":
        inc = {"count": -1, "refunded": 1}
    elif kind == "commit":
        inc = {"not_found" if event.get("outcome") == "not_found" else "answered": 1}
    else:
        return []
    at = datetime.fromtimestamp(float(event["ts"]), tz=timezone.utc)
    event_id = event["event_id"]
    ops = []
    for field, period, _ in PERIODS:
        key = event.get(field)
        if not key:
            continue
        ops.append(UpdateOne(
            {"tenant": event["tenant"], "user_id": event["user_id"], "period": period,
             "period_key": key, "applied": {"$ne": event_id}},
            {
                "$inc": inc,
                "$set": {"role": event.get("role") or None, "updated_at": _now()},
                "$min": {"first_at": at},
                "$max": {"last_at": at},
                "$push": {"applied": {"$each": [event_id], "$slice": -APPLIED_KEEP}},
            },
            upsert=True,
        ))
    return ops


def quota_op(event: dict) -> UpdateOne | None:
    """The chat_quota update for a reserve (+1) or refund (-1) event.

    Per window: an event for the stored window changes its count; an event for a newer window
    starts it; an event for an older window is ignored. A refund never goes below 0.
    """
    kind = event["type"]
    if kind not in ("reserve", "refund"):
        return None
    event_id = event["event_id"]
    stages_set: dict = {}
    for field, _, letter in PERIODS:
        key = event.get(field) or ""
        stored_key = {"$ifNull": [f"${letter}.key", ""]}
        stored_n = {"$ifNull": [f"${letter}.n", 0]}
        if kind == "reserve":
            new = {"$cond": [
                {"$eq": [stored_key, key]}, {"key": key, "n": {"$add": [stored_n, 1]}},
                {"$cond": [{"$gt": [key, stored_key]}, {"key": key, "n": 1}, f"${letter}"]},
            ]}
        else:
            new = {"$cond": [
                {"$and": [{"$eq": [stored_key, key]}, {"$gt": [stored_n, 0]}]},
                {"key": key, "n": {"$subtract": [stored_n, 1]}},
                f"${letter}",
            ]}
        stages_set[letter] = new
    stages_set["applied"] = {"$slice": [
        {"$concatArrays": [{"$ifNull": ["$applied", []]}, [event_id]]}, -APPLIED_KEEP,
    ]}
    stages_set["role"] = {"$literal": event.get("role") or None}
    stages_set["updated_at"] = "$$NOW"
    return UpdateOne(
        {"tenant": event["tenant"], "user_id": event["user_id"], "applied": {"$ne": event_id}},
        [{"$set": stages_set}],
        upsert=True,
    )


async def apply_events(db, events: list[dict], quota: bool = True) -> None:
    """Write events to chat_usage and (unless ``quota`` is False) chat_quota; safe to repeat.

    The MongoDB fallback updates chat_quota itself, so it passes ``quota=False``.

    A duplicate-key error means the document already holds the event (or two writers created
    the same new document at once): each such operation is retried alone, and a second
    duplicate-key error means the event was already applied.
    """
    for collection, ops in ((USAGE, [op for e in events for op in usage_ops(e)]),
                            (QUOTA, [op for e in events if quota and (op := quota_op(e)) is not None])):
        if not ops:
            continue
        try:
            await db[collection].bulk_write(ops, ordered=False)
        except BulkWriteError as e:
            errors = e.details.get("writeErrors", [])
            if any(err.get("code") != _DUPLICATE_KEY for err in errors):
                raise
            for err in errors:
                op = ops[err["index"]]
                try:
                    await db[collection].bulk_write([op], ordered=False)
                except BulkWriteError as again:
                    if any(x.get("code") != _DUPLICATE_KEY for x in again.details.get("writeErrors", [])):
                        raise
                except DuplicateKeyError:
                    pass


# ---------- Redis stream: consumer group and drain ----------


async def ensure_group(redis) -> None:
    try:
        await redis.xgroup_create(STREAM, GROUP, id="0", mkstream=True)
    except Exception as e:  # BUSYGROUP: the group exists already
        if "BUSYGROUP" not in str(e):
            raise


class UsageDrainer:
    """One per pod: syncs the usage stream to MongoDB every ``drain_seconds``."""

    def __init__(self, get_redis, get_db, cfg) -> None:
        self._get_redis = get_redis
        self._get_db = get_db
        self.cfg = cfg
        self.consumer = consumer_name()
        self._task: asyncio.Task | None = None
        self._stopping = False
        self._failures = 0
        self.last_error: str | None = None

    def start(self) -> None:
        if self._task is None or self._task.done():
            self._stopping = False
            self._task = asyncio.create_task(self._run(), name="chat_usage_drainer")

    async def stop(self) -> None:
        """Stop reading. Unacknowledged events stay pending for the next run or another pod."""
        self._stopping = True
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except (asyncio.CancelledError, Exception):
                pass
            self._task = None

    async def _run(self) -> None:
        while not self._stopping:
            delay = self.cfg.drain_seconds
            try:
                await self.drain_once()
                self._failures = 0
            except asyncio.CancelledError:
                raise
            except Exception as e:
                self._failures += 1
                self.last_error = str(e)
                delay = min(self.cfg.drain_seconds * (2 ** min(self._failures, 4)), 300)
                logger.warning("chat_usage_drain_failed | attempt=%d retry_in=%.0fs | %s", self._failures, delay, e)
            await asyncio.sleep(delay)

    async def drain_once(self) -> int:
        """One round: take over idle events, read own pending and new events, write, ack."""
        redis, db = self._get_redis(), self._get_db()
        if redis is None or db is None:
            return 0
        if self._failures:  # events only exceed max_deliveries after failed writes
            await self._dead_letter(redis)
        try:
            # Events of crashed pods, idle for claim_idle_seconds.
            claimed = await redis.xautoclaim(
                STREAM, GROUP, self.consumer, min_idle_time=int(self.cfg.claim_idle_seconds * 1000),
                start_id="0-0", count=self.cfg.drain_batch,
            )
        except ResponseError as e:
            if "NOGROUP" not in str(e):
                raise
            await ensure_group(redis)  # Redis lost its data: recreate the group
            return 0
        # Entry id -> event; a dict, because a claimed entry can also be in this pod's pending list.
        events: dict[str, dict] = {i: f for i, f in claimed[1] if f}
        # This pod's own unacknowledged events (a write that failed last round), then new ones.
        for start in ("0", ">"):
            for _, items in await redis.xreadgroup(GROUP, self.consumer, {STREAM: start}, count=self.cfg.drain_batch) or []:
                events.update((i, f) for i, f in items if f)
        if not events:
            return 0
        await apply_events(db, list(events.values()))
        ids = list(events)
        async with redis.pipeline(transaction=False) as pipe:
            pipe.xack(STREAM, GROUP, *ids)
            pipe.xdel(STREAM, *ids)
            await pipe.execute()
        if len(ids) >= self.cfg.drain_batch and await redis.xlen(STREAM) > self.cfg.stream_warn_length:
            logger.warning("chat_usage_stream_long | more than %d events waiting", self.cfg.stream_warn_length)
        logger.info("chat_usage_drained | events=%d", len(ids))
        return len(ids)

    async def drain_all(self, max_rounds: int = 100) -> int:
        """Drain until nothing is waiting (used by the Redis recovery before Redis is trusted)."""
        total = 0
        for _ in range(max_rounds):
            n = await self.drain_once()
            total += n
            if n == 0 and not (await self._get_redis().xpending(STREAM, GROUP))["pending"]:
                break
        return total

    async def _dead_letter(self, redis) -> None:
        pending = await redis.xpending_range(STREAM, GROUP, min="-", max="+", count=100)
        for p in pending or []:
            if int(p.get("times_delivered", 0)) <= self.cfg.max_deliveries:
                continue
            entry_id = p["message_id"]
            rows = await redis.xrange(STREAM, min=entry_id, max=entry_id)
            if rows:
                await redis.xadd(DEAD_STREAM, {**rows[0][1], "failed_entry": entry_id})
            await redis.xack(STREAM, GROUP, entry_id)
            await redis.xdel(STREAM, entry_id)
            logger.error("chat_usage_dead_letter | entry=%s deliveries=%s", entry_id, p.get("times_delivered"))

    async def health(self) -> dict:
        redis = self._get_redis()
        if redis is None:
            return {"redis": "unavailable"}
        summary = await redis.xpending(STREAM, GROUP)
        oldest_age = None
        if summary.get("pending") and summary.get("min"):
            oldest_age = round(time.time() - int(summary["min"].split("-")[0]) / 1000, 1)
        return {
            "stream_length": await redis.xlen(STREAM),
            "pending": summary.get("pending", 0),
            "oldest_pending_seconds": oldest_age,
            "dead_letters": await redis.xlen(DEAD_STREAM),
            "last_drain_error": self.last_error,
        }
