"""MongoDB record of admin-chat conversations: one document per tenant and session.

Collection ``chat_sessions`` (database ``chat_store.database``), one document per
(tenant, session_id): who and when, counts, and ``messages`` - every question in order
with the answer the user saw (the newest ``max_messages_per_session``).

A session's messages are kept in memory and written in one update when the session
has been idle ``idle_minutes``, the widget reports it closed, it holds
``flush_at_messages`` messages, or the chatbot shuts down. Sessions still open are
also written every ``safety_flush_minutes``, so a crash loses at most that much.
MongoDB removes a session itself ``retention_days`` after its last message (TTL index).
Database problems are logged and never reach the chat; unwritten messages are retried.
"""

from __future__ import annotations

import asyncio
from collections import OrderedDict
import uuid
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Callable

from pymongo import ASCENDING, DESCENDING, AsyncMongoClient, UpdateOne
from pymongo.errors import OperationFailure

from app.config.settings import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

ANSWERED = "answered"
NOT_FOUND = "not_found"
ERROR = "error"

SESSIONS = "chat_sessions"
# One document per vote: a user's thumbs up/down on one answer, with a copy of the question and
# answer, so wrong answers can be reviewed and fixed later without searching the sessions.
FEEDBACK = "chat_feedback"
UP, DOWN = "up", "down"
OPEN, FIXED, WONT_FIX = "open", "fixed", "wont_fix"
# Answers kept in memory by message_id so a vote can copy the question and answer (also after the
# session was written). Older answers can no longer be rated.
_RECENT_ANSWERS = 5000
_INDEX_OPTIONS_CONFLICT = 85
# Who and where the session belongs to: stored once on the session, not per message.
_SESSION_FIELDS = ("tenant", "session_id", "user_id", "role")


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class ChatRecord:
    tenant: str
    session_id: str
    question: str
    answer: str
    outcome: str  # ANSWERED | NOT_FOUND | ERROR
    user_id: str | None = None
    role: str | None = None
    route: str | None = None
    screen_title: str | None = None
    sport: str | None = None
    language: str | None = None
    retrieval_mode: str | None = None
    doc_ids: list[str] = field(default_factory=list)
    sources: list[dict] = field(default_factory=list)  # [{"title", "section"}]
    model: str | None = None
    first_token_ms: int | None = None
    total_ms: int | None = None
    streamed: bool = False
    created_at: datetime = field(default_factory=_utcnow)
    # Id the widget sends back with a thumbs up/down vote for this answer.
    message_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    # "up" or "down" once the user voted (copied into the session if it is still unwritten).
    feedback: str | None = None

    def message(self) -> dict:
        """The entry in the session's ``messages`` list."""
        doc = asdict(self)
        for key in _SESSION_FIELDS:
            doc.pop(key)
        return doc


def session_update(items: list[ChatRecord], max_messages: int) -> UpdateOne:
    """One upsert appending ``items`` (same tenant and session, in order) to their session."""
    first, last = items[0], items[-1]
    return UpdateOne(
        {"tenant": first.tenant, "session_id": first.session_id},
        {
            "$setOnInsert": {
                "tenant": first.tenant,
                "session_id": first.session_id,
                "user_id": first.user_id,
                "role": first.role,
                "started_at": first.created_at,
            },
            "$set": {
                "last_message_at": last.created_at,
                "last_route": last.route,
                "last_screen_title": last.screen_title,
            },
            "$inc": {
                "message_count": len(items),
                "not_found_count": sum(i.outcome == NOT_FOUND for i in items),
                "error_count": sum(i.outcome == ERROR for i in items),
            },
            "$push": {
                "messages": {"$each": [i.message() for i in items], "$slice": -max_messages}
            },
        },
        upsert=True,
    )


@dataclass
class _Session:
    """Unwritten messages of one open session."""

    items: list[ChatRecord] = field(default_factory=list)
    last_activity: float = 0.0
    # When the oldest unwritten message arrived; drives the safety write.
    pending_since: float | None = None
    closed: bool = False


SessionKey = tuple[str, str]


class ChatStore:
    """Per-session buffers plus one writer task."""

    def __init__(
        self,
        uri: str,
        database: str,
        *,
        idle_seconds: float = 30 * 60,
        safety_seconds: float = 10 * 60,
        flush_at_messages: int = 50,
        check_seconds: float = 30.0,
        max_buffered_messages: int = 10000,
        retention_days: int = 180,
        max_messages_per_session: int = 500,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.uri = uri
        self.database_name = database
        self.idle_seconds = idle_seconds
        self.safety_seconds = safety_seconds
        self.flush_at_messages = flush_at_messages
        self.check_seconds = check_seconds
        self.max_buffered_messages = max_buffered_messages
        self.retention_days = retention_days
        self.max_messages_per_session = max_messages_per_session
        self.clock = clock
        self.client: AsyncMongoClient | None = None
        self.db = None
        self.sessions: dict[SessionKey, _Session] = {}
        self._due: set[SessionKey] = set()  # write at the next check, regardless of timers
        self._wake: asyncio.Event | None = None
        self._task: asyncio.Task | None = None
        self._stopping = False
        self.recent: OrderedDict[str, ChatRecord] = OrderedDict()

    @property
    def buffered(self) -> int:
        return sum(len(s.items) for s in self.sessions.values())

    async def start(self) -> None:
        self.client = AsyncMongoClient(self.uri, serverSelectionTimeoutMS=3000, tz_aware=True)
        self.db = self.client[self.database_name]
        await self.db.command("ping")
        await self._ensure_indexes()
        self._wake = asyncio.Event()
        self._task = asyncio.create_task(self._run(), name="chat_store_writer")

    async def stop(self) -> None:
        """Write every session still in memory, then close the connection."""
        self._stopping = True
        if self._task is not None:
            self._wake.set()
            await self._task
            self._task = None
        if self.db is not None:
            await self.flush(force=True)
        if self.client is not None:
            await self.client.close()
            self.client = self.db = None

    def record(self, item: ChatRecord) -> None:
        """Add a question/answer to its session's buffer (memory only)."""
        self.recent[item.message_id] = item
        while len(self.recent) > _RECENT_ANSWERS:
            self.recent.popitem(last=False)
        now = self.clock()
        key = (item.tenant, item.session_id)
        session = self.sessions.setdefault(key, _Session())
        session.items.append(item)
        session.last_activity = now
        session.closed = False  # a closed session that is used again is open again
        if session.pending_since is None:
            session.pending_since = now
        if len(session.items) >= self.flush_at_messages:
            self._mark_due(key)
        if self.buffered >= self.max_buffered_messages:
            logger.warning("chat_store_memory_limit | buffered=%d | writing all sessions", self.buffered)
            self._due.update(self.sessions)
            self._notify()

    def close_session(self, tenant: str, session_id: str) -> None:
        """The widget was closed: write this session now and forget it."""
        key = (tenant, session_id)
        session = self.sessions.get(key)
        if session is None:
            return
        session.closed = True
        self._mark_due(key)

    def _mark_due(self, key: SessionKey) -> None:
        self._due.add(key)
        self._notify()

    def _notify(self) -> None:
        if self._wake is not None:
            self._wake.set()

    def _sessions_to_write(self, force: bool) -> list[SessionKey]:
        now = self.clock()
        keys = []
        for key, s in self.sessions.items():
            idle = now - s.last_activity >= self.idle_seconds
            overdue = s.pending_since is not None and now - s.pending_since >= self.safety_seconds
            if force or key in self._due or idle or overdue or s.closed:
                keys.append(key)
        return keys

    async def flush(self, force: bool = False) -> int:
        """Write the sessions that are due. Returns how many messages were written."""
        written = 0
        for key in self._sessions_to_write(force):
            self._due.discard(key)
            session = self.sessions.get(key)
            if session is None:
                continue
            items, session.items = session.items, []
            pending_since, session.pending_since = session.pending_since, None
            if items:
                try:
                    await self.db[SESSIONS].bulk_write(
                        [session_update(items, self.max_messages_per_session)], ordered=True
                    )
                    written += len(items)
                except Exception:
                    logger.exception("chat_store_write_failed | tenant=%s | kept=%d", key[0], len(items))
                    session.items = items + session.items  # keep order; retried at the next check
                    session.pending_since = pending_since
                    continue
            # Messages that arrived while writing stay for the next write.
            finished = session.closed or self.clock() - session.last_activity >= self.idle_seconds
            if not session.items and (finished or force):
                self.sessions.pop(key, None)
        return written

    async def _ensure_indexes(self) -> None:
        sessions = self.db[SESSIONS]
        await sessions.create_index(
            [("tenant", ASCENDING), ("session_id", ASCENDING)], name="tenant_session", unique=True
        )
        await sessions.create_index(
            [("tenant", ASCENDING), ("last_message_at", DESCENDING)], name="tenant_recent"
        )
        # Sessions of a tenant that contain an unanswered question.
        await sessions.create_index(
            [("tenant", ASCENDING), ("messages.outcome", ASCENDING)], name="tenant_message_outcome"
        )
        await self._ensure_ttl(sessions, "last_message_at")
        feedback = self.db[FEEDBACK]
        await feedback.create_index(
            [("tenant", ASCENDING), ("message_id", ASCENDING), ("user_id", ASCENDING)],
            name="tenant_message_user", unique=True,
        )
        # The review list: a tenant's open thumbs-down answers, newest first.
        await feedback.create_index(
            [("tenant", ASCENDING), ("rating", ASCENDING), ("status", ASCENDING), ("created_at", DESCENDING)],
            name="tenant_rating_status",
        )
        await self._ensure_ttl(feedback, "created_at")

    async def save_feedback(
        self, tenant: str, user_id: str | None, message_id: str, rating: str, comment: str | None
    ) -> bool:
        """Store (or change) one user's vote on one of their answers. False if the answer is unknown."""
        item = self.recent.get(message_id)
        if item is None or item.tenant != tenant or (item.user_id or None) != (user_id or None):
            return False
        item.feedback = rating
        now = _utcnow()
        await self.db[FEEDBACK].update_one(
            {"tenant": tenant, "message_id": message_id, "user_id": user_id},
            {
                "$set": {
                    "rating": rating,
                    "comment": (comment or "").strip() or None,
                    "updated_at": now,
                    # A changed vote is reviewed again.
                    "status": OPEN,
                },
                "$setOnInsert": {
                    "tenant": tenant,
                    "message_id": message_id,
                    "user_id": user_id,
                    "role": item.role,
                    "session_id": item.session_id,
                    "question": item.question,
                    "answer": item.answer,
                    "outcome": item.outcome,
                    "route": item.route,
                    "screen_title": item.screen_title,
                    "sport": item.sport,
                    "language": item.language,
                    "retrieval_mode": item.retrieval_mode,
                    "doc_ids": item.doc_ids,
                    "sources": item.sources,
                    "model": item.model,
                    "answered_at": item.created_at,
                    "created_at": now,
                },
            },
            upsert=True,
        )
        return True

    async def list_feedback(
        self, tenant: str | None, rating: str | None, status: str | None, limit: int
    ) -> list[dict]:
        query = {k: v for k, v in (("tenant", tenant), ("rating", rating), ("status", status)) if v}
        cursor = self.db[FEEDBACK].find(query, {"_id": 0}).sort("created_at", DESCENDING).limit(limit)
        return [doc async for doc in cursor]

    async def set_feedback_status(self, tenant: str, message_id: str, status: str, note: str | None) -> int:
        result = await self.db[FEEDBACK].update_many(
            {"tenant": tenant, "message_id": message_id},
            {"$set": {"status": status, "review_note": (note or "").strip() or None, "reviewed_at": _utcnow()}},
        )
        return result.modified_count

    async def _ensure_ttl(self, collection, field_name: str) -> None:
        """TTL index on ``field_name``; changes the expiry in place when retention_days changes."""
        name = f"ttl_{field_name}"
        if self.retention_days <= 0:
            try:
                await collection.drop_index(name)
            except OperationFailure:
                pass
            return
        seconds = self.retention_days * 24 * 60 * 60
        try:
            await collection.create_index(field_name, name=name, expireAfterSeconds=seconds)
        except OperationFailure as e:
            if e.code != _INDEX_OPTIONS_CONFLICT:
                raise
            await self.db.command(
                {"collMod": collection.name, "index": {"name": name, "expireAfterSeconds": seconds}}
            )

    async def _run(self) -> None:
        while not self._stopping:
            try:
                await asyncio.wait_for(self._wake.wait(), timeout=self.check_seconds)
            except asyncio.TimeoutError:
                pass
            self._wake.clear()
            if self._stopping:
                break
            try:
                await self.flush()
            except Exception:
                logger.exception("chat_store_flush_failed")


# ---------- process-wide instance (started in app.main lifespan) ----------

_store: ChatStore | None = None


async def start() -> None:
    global _store
    s = get_settings()
    cfg = s.chat_store
    if not cfg.enabled:
        logger.info("startup | chat store disabled")
        return
    env_uri = s.chat_store_mongodb_uri.get_secret_value().strip() if s.chat_store_mongodb_uri else ""
    uri = env_uri or cfg.mongodb_uri
    store = ChatStore(
        uri,
        cfg.database,
        idle_seconds=cfg.idle_minutes * 60,
        safety_seconds=cfg.safety_flush_minutes * 60,
        flush_at_messages=cfg.flush_at_messages,
        check_seconds=cfg.check_seconds,
        max_buffered_messages=cfg.max_buffered_messages,
        retention_days=cfg.retention_days,
        max_messages_per_session=cfg.max_messages_per_session,
    )
    try:
        await store.start()
    except Exception as e:
        logger.warning("startup | chat store unavailable (%s); questions are not recorded", e)
        if store.client is not None:
            await store.client.close()
        return
    _store = store
    logger.info(
        "startup | chat store on MongoDB database %s | written per session: idle %g min, "
        "every %g min while open, at %d messages, on close | retention %d days",
        cfg.database,
        cfg.idle_minutes,
        cfg.safety_flush_minutes,
        cfg.flush_at_messages,
        cfg.retention_days,
    )


async def stop() -> None:
    global _store
    if _store is not None:
        await _store.stop()
        _store = None


def record(item: ChatRecord) -> None:
    """Add one question and answer to its session; returns at once and never raises."""
    if _store is None:
        return
    try:
        _store.record(item)
    except Exception:
        logger.exception("chat_store_record_failed")


async def save_feedback(
    tenant: str, user_id: str | None, message_id: str, rating: str, comment: str | None = None
) -> str:
    """"saved", "unknown" (no such answer for this user) or "unavailable" (no store). Never raises."""
    if _store is None:
        return "unavailable"
    try:
        saved = await _store.save_feedback(tenant, user_id, message_id, rating, comment)
    except Exception:
        logger.exception("chat_feedback_failed")
        return "unavailable"
    return "saved" if saved else "unknown"


async def list_feedback(
    tenant: str | None = None, rating: str | None = None, status: str | None = None, limit: int = 100
) -> list[dict] | None:
    """Votes for review, newest first; None when the store is not running."""
    if _store is None:
        return None
    return await _store.list_feedback(tenant, rating, status, limit)


async def set_feedback_status(tenant: str, message_id: str, status: str, note: str | None = None) -> int | None:
    if _store is None:
        return None
    return await _store.set_feedback_status(tenant, message_id, status, note)


def close_session(tenant: str, session_id: str) -> None:
    """The user closed the chat: write that session now. Never raises."""
    if _store is None:
        return
    try:
        _store.close_session(tenant, session_id)
    except Exception:
        logger.exception("chat_store_close_failed")
