"""Per-user daily, weekly and monthly question limits for the admin chat.

Every accepted question uses one question from each window, including "not found" and
"Did you mean" replies. A denied question uses nothing and never reaches the model. A
qualifying failure (LLM unavailable, pipeline error) is refunded exactly once.

Request path (Redis up):
- One Lua script checks the three counters and, only if every window has room, increments
  all three, records the reservation and adds a "reserve" event to the usage stream: one
  atomic step. Commit and refund are Lua scripts too, keyed by the reservation, so a refund
  happens at most once and never after a commit.
- A counter that is missing (new window, Redis restart, recovery) is seeded from MongoDB
  (``chat_quota``) with SET NX, so a stale value never overwrites a live one.
- app/services/chat_usage_sync.py syncs the stream to MongoDB in the background.

Redis down (circuit breaker open): every question is checked and counted with one atomic
update on the user's ``chat_quota`` document in MongoDB. The users seen during the outage are
remembered; when Redis is back, the stream is drained and their Redis counters are cleared so
they re-seed from MongoDB before Redis is used again. Redis and MongoDB both down: 503.
"""

from __future__ import annotations

import asyncio
import time
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from typing import Any
from urllib.parse import quote
from zoneinfo import ZoneInfo

from pymongo import AsyncMongoClient, ReturnDocument

from app.config.settings import get_settings
from app.services import chat_usage_sync as sync
from app.services.auth import CallerScope
from app.utils.logger import get_logger

logger = get_logger(__name__)

WINDOWS = ("daily", "weekly", "monthly")
_LETTER = {"daily": "d", "weekly": "w", "monthly": "m"}
_REQUEST_TTL = 2 * 86400
_EXPIRY_GRACE = 2 * 86400


class LimitDenied(Exception):
    """A window is used up: HTTP 429 with ``payload``."""

    def __init__(self, payload: dict) -> None:
        super().__init__(payload.get("window"))
        self.payload = payload


class LimitsUnavailable(Exception):
    """Redis and MongoDB are both unreachable: HTTP 503."""


class MissingUser(Exception):
    """Limits are on but the caller has no user id: HTTP 401."""


@dataclass
class Windows:
    keys: dict[str, str]          # daily -> "2026-10-22", weekly -> "2026-W43", monthly -> "2026-10"
    resets_at: dict[str, datetime]

    def expire_at(self, window: str) -> int:
        return int(self.resets_at[window].timestamp()) + _EXPIRY_GRACE


def current_windows(tz_name: str, now: datetime | None = None) -> Windows:
    tz = ZoneInfo(tz_name)
    local = (now or datetime.now(timezone.utc)).astimezone(tz)
    day = local.date()
    iso = local.isocalendar()
    monday = day - timedelta(days=day.weekday())
    first_next_month = date(day.year + (day.month == 12), day.month % 12 + 1, 1)

    def midnight(d: date) -> datetime:
        return datetime(d.year, d.month, d.day, tzinfo=tz)

    return Windows(
        keys={"daily": day.isoformat(), "weekly": f"{iso.year}-W{iso.week:02d}", "monthly": day.strftime("%Y-%m")},
        resets_at={
            "daily": midnight(day + timedelta(days=1)),
            "weekly": midnight(monday + timedelta(days=7)),
            "monthly": midnight(first_next_month),
        },
    )


def limits_for(scope: CallerScope) -> dict[str, int]:
    """Per window: the role override, else the tenant override, else the default. 0 = no limit."""
    cfg = get_settings().chat_limits
    role = cfg.roles.get(scope.role or "")
    tenant = cfg.tenants.get(scope.tenant)
    out = {}
    for window in WINDOWS:
        value = getattr(role, window, None) if role else None
        if value is None and tenant is not None:
            value = getattr(tenant, window, None)
        out[window] = int(getattr(cfg.default, window) if value is None else value)
    return out


def _user_tag(tenant: str, user_id: str) -> str:
    # One hash tag per user, so all of a user's keys share a Redis Cluster slot.
    return "{" + quote(tenant, safe="") + ":" + quote(user_id, safe="") + "}"


def counter_key(tenant: str, user_id: str, window: str, period_key: str) -> str:
    return f"chatq:{_user_tag(tenant, user_id)}:{_LETTER[window]}:{period_key}"


def request_key(tenant: str, user_id: str, request_id: str) -> str:
    return f"chatq:{_user_tag(tenant, user_id)}:req:{request_id}"


@dataclass
class Reservation:
    request_id: str
    backend: str                    # "redis" | "mongo" | "none"
    scope: CallerScope | None = None
    window_keys: dict[str, str] = field(default_factory=dict)
    usage: dict | None = None
    settled: bool = False


# ---------- Lua scripts (each one atomic step that also writes its usage event) ----------

_RESERVE_LUA = """
local d = redis.call('GET', KEYS[1])
local w = redis.call('GET', KEYS[2])
local m = redis.call('GET', KEYS[3])
if (not d) or (not w) or (not m) then
  return {'NEED_SEED'}
end
d = tonumber(d); w = tonumber(w); m = tonumber(m)
local ld = tonumber(ARGV[1]); local lw = tonumber(ARGV[2]); local lm = tonumber(ARGV[3])
if ld > 0 and d >= ld then return {'DENIED', 'daily', d, w, m} end
if lw > 0 and w >= lw then return {'DENIED', 'weekly', d, w, m} end
if lm > 0 and m >= lm then return {'DENIED', 'monthly', d, w, m} end
d = redis.call('INCR', KEYS[1]); redis.call('EXPIREAT', KEYS[1], ARGV[4])
w = redis.call('INCR', KEYS[2]); redis.call('EXPIREAT', KEYS[2], ARGV[5])
m = redis.call('INCR', KEYS[3]); redis.call('EXPIREAT', KEYS[3], ARGV[6])
redis.call('HSET', KEYS[4], 'state', 'reserved', 'request_id', ARGV[8], 'tenant', ARGV[9],
  'user_id', ARGV[10], 'role', ARGV[11], 'dk', ARGV[12], 'wk', ARGV[13], 'mk', ARGV[14],
  'dkey', KEYS[1], 'wkey', KEYS[2], 'mkey', KEYS[3])
redis.call('EXPIRE', KEYS[4], ARGV[7])
redis.call('XADD', KEYS[5], '*', 'type', 'reserve', 'event_id', ARGV[8] .. ':reserve',
  'request_id', ARGV[8], 'tenant', ARGV[9], 'user_id', ARGV[10], 'role', ARGV[11],
  'dk', ARGV[12], 'wk', ARGV[13], 'mk', ARGV[14], 'ts', ARGV[15], 'exempt', ARGV[16])
return {'ALLOWED', '', d, w, m}
"""

_COMMIT_LUA = """
if redis.call('HGET', KEYS[1], 'state') ~= 'reserved' then return 0 end
redis.call('HSET', KEYS[1], 'state', 'committed')
local h = redis.call('HMGET', KEYS[1], 'request_id', 'tenant', 'user_id', 'role', 'dk', 'wk', 'mk')
redis.call('XADD', KEYS[2], '*', 'type', 'commit', 'event_id', h[1] .. ':commit', 'request_id', h[1],
  'tenant', h[2], 'user_id', h[3], 'role', h[4], 'dk', h[5], 'wk', h[6], 'mk', h[7],
  'outcome', ARGV[1], 'ts', ARGV[2])
return 1
"""

_REFUND_LUA = """
if redis.call('HGET', KEYS[1], 'state') ~= 'reserved' then return 0 end
redis.call('HSET', KEYS[1], 'state', 'refunded')
local h = redis.call('HMGET', KEYS[1], 'request_id', 'tenant', 'user_id', 'role', 'dk', 'wk', 'mk',
  'dkey', 'wkey', 'mkey')
for i = 8, 10 do
  local v = tonumber(redis.call('GET', h[i]) or '0')
  if v and v > 0 then redis.call('DECR', h[i]) end
end
redis.call('XADD', KEYS[2], '*', 'type', 'refund', 'event_id', h[1] .. ':refund', 'request_id', h[1],
  'tenant', h[2], 'user_id', h[3], 'role', h[4], 'dk', h[5], 'wk', h[6], 'mk', h[7], 'ts', ARGV[1])
return 1
"""


class ChatLimits:
    def __init__(self) -> None:
        self.redis = None
        self.mongo: AsyncMongoClient | None = None
        self.db = None
        self.state = "down"            # up | down | recovering
        self._scripts: dict[str, Any] = {}
        self._indexes_ready = False
        self._retry_task: asyncio.Task | None = None
        self.drainer: sync.UsageDrainer | None = None
        # Users already recorded in chat_outage_users during the current Redis outage.
        self._outage_users: set[tuple[str, str]] = set()

    # ---------- lifecycle ----------

    async def start(self) -> None:
        s = get_settings()
        cfg = s.chat_limits
        if cfg.mode == "off":
            logger.info("startup | chat limits off")
            return
        mongo_uri = (s.chat_store_mongodb_uri.get_secret_value().strip() if s.chat_store_mongodb_uri else "") \
            or s.chat_store.mongodb_uri
        ms = int(cfg.mongo_timeout_seconds * 1000)
        self.mongo = AsyncMongoClient(mongo_uri, serverSelectionTimeoutMS=ms, connectTimeoutMS=ms,
                                      socketTimeoutMS=ms * 2, tz_aware=True)
        self.db = self.mongo[s.chat_store.database]
        await self._ensure_indexes()
        redis_url = s.redis_url.get_secret_value().strip() if s.redis_url else ""
        if redis_url:
            import redis.asyncio as aioredis

            self.attach_redis(aioredis.from_url(
                redis_url, decode_responses=True, max_connections=30,
                socket_timeout=cfg.redis_timeout_seconds, socket_connect_timeout=cfg.redis_timeout_seconds,
            ))
            try:
                await self.redis.ping()
                await sync.ensure_group(self.redis)
                self.state = "up"
            except Exception as e:
                self._trip(e)
            self.drainer.start()
        else:
            logger.warning("startup | REDIS_URL not set: question limits use MongoDB only")
        logger.info("startup | chat limits %s | redis %s | timezone %s", cfg.mode, self.state, cfg.timezone)

    async def stop(self) -> None:
        if self._retry_task is not None:
            self._retry_task.cancel()
            self._retry_task = None
        if self.drainer is not None:
            await self.drainer.stop()
        if self.redis is not None:
            await self.redis.aclose()
            self.redis = None
        if self.mongo is not None:
            await self.mongo.close()
            self.mongo = self.db = None
        self.state = "down"

    def attach_redis(self, client) -> None:
        """Use this Redis client (and its scripts and drainer); start() and tests call it."""
        self.redis = client
        self._scripts = {
            "reserve": client.register_script(_RESERVE_LUA),
            "commit": client.register_script(_COMMIT_LUA),
            "refund": client.register_script(_REFUND_LUA),
        }
        self.drainer = sync.UsageDrainer(self._redis_if_usable, lambda: self.db, get_settings().chat_limits)

    def _redis_if_usable(self):
        return self.redis if self.state != "down" else None

    async def _ensure_indexes(self) -> None:
        if self._indexes_ready or self.db is None:
            return
        try:
            await sync.ensure_indexes(self.db, get_settings().chat_limits.retention_days)
            self._indexes_ready = True
        except Exception as e:
            logger.warning("chat_limits_indexes_pending | MongoDB not reachable yet: %s", e)

    # ---------- circuit breaker ----------

    def _trip(self, error: Exception) -> None:
        if self.state != "down":
            logger.error("chat_limits_redis_down | using MongoDB for limits | %s", error)
        self.state = "down"
        if self.redis is not None and (self._retry_task is None or self._retry_task.done()):
            self._retry_task = asyncio.create_task(self._recover_loop(), name="chat_limits_redis_retry")

    async def _recover_loop(self) -> None:
        cfg = get_settings().chat_limits
        while self.state != "up":
            await asyncio.sleep(cfg.redis_retry_seconds)
            try:
                await self.redis.ping()
            except Exception:
                continue
            self.state = "recovering"
            try:
                await sync.ensure_group(self.redis)
                drained = await self.drainer.drain_all() if self.drainer else 0
                reseeded = await self._clear_outage_users()
                self.state = "up"
                logger.warning("chat_limits_redis_recovered | drained=%d reseeded_users=%d", drained, reseeded)
            except Exception as e:
                self.state = "down"
                logger.error("chat_limits_recovery_failed | retrying | %s", e)

    async def _clear_outage_users(self) -> int:
        """Users counted in MongoDB during the outage: drop their Redis counters so they re-seed."""
        w = current_windows(get_settings().chat_limits.timezone)
        users = [d async for d in self.db[sync.OUTAGE_USERS].find({}, {"tenant": 1, "user_id": 1})]
        if users:
            await self.redis.delete(*(counter_key(d["tenant"], d["user_id"], win, w.keys[win])
                                      for d in users for win in WINDOWS))
            await self.db[sync.OUTAGE_USERS].delete_many({"_id": {"$in": [d["_id"] for d in users]}})
        self._outage_users.clear()
        return len(users)

    # ---------- reserve ----------

    async def reserve(self, scope: CallerScope, request_id: str | None = None) -> Reservation:
        cfg = get_settings().chat_limits
        request_id = request_id or uuid.uuid4().hex
        if cfg.mode == "off":
            return Reservation(request_id=request_id, backend="none")
        if not (scope.user_id or "").strip():
            raise MissingUser()
        limits = limits_for(scope)
        exempt = (scope.role or "") in cfg.exempt_roles
        checked = limits if (cfg.mode == "enforce" and not exempt) else {w: 0 for w in WINDOWS}
        windows = current_windows(cfg.timezone)
        if self.state == "up" and self.redis is not None:
            try:
                return await self._reserve_redis(scope, request_id, limits, checked, windows, exempt)
            except LimitDenied:
                raise
            except Exception as e:
                self._trip(e)
        try:
            return await self._reserve_mongo(scope, request_id, limits, checked, windows, exempt)
        except LimitDenied:
            raise
        except Exception as e:
            logger.error("chat_limits_unavailable | redis=%s | mongodb error: %s", self.state, e)
            raise LimitsUnavailable() from e

    async def _reserve_redis(self, scope, request_id, limits, checked, windows, exempt) -> Reservation:
        keys = [counter_key(scope.tenant, scope.user_id, w, windows.keys[w]) for w in WINDOWS]
        req_key = request_key(scope.tenant, scope.user_id, request_id)
        args = [checked["daily"], checked["weekly"], checked["monthly"],
                windows.expire_at("daily"), windows.expire_at("weekly"), windows.expire_at("monthly"),
                _REQUEST_TTL, request_id, scope.tenant, scope.user_id, scope.role or "",
                windows.keys["daily"], windows.keys["weekly"], windows.keys["monthly"],
                f"{time.time():.3f}", "1" if exempt else "0"]
        for _ in range(3):
            result = await self._scripts["reserve"](keys=[*keys, req_key, sync.STREAM], args=args)
            status = result[0]
            if status == "NEED_SEED":
                await self._seed(scope, windows, keys)
                continue
            used = dict(zip(WINDOWS, map(int, result[2:5])))
            if status == "DENIED":
                raise LimitDenied(self._denied_payload(result[1], limits, used, windows))
            return Reservation(request_id, "redis", scope, dict(windows.keys), self._usage(limits, used, windows, exempt))
        raise RuntimeError("chat limit counters could not be seeded")

    async def _seed(self, scope, windows: Windows, keys: list[str]) -> None:
        """Missing counters start from MongoDB's count for the same window (0 for a new one)."""
        counts = {w: 0 for w in WINDOWS}
        try:
            doc = await self.db[sync.QUOTA].find_one({"tenant": scope.tenant, "user_id": scope.user_id})
        except Exception as e:
            doc = None
            logger.warning("chat_limits_seed_without_mongodb | %s", e)
        for window in WINDOWS:
            part = (doc or {}).get(_LETTER[window]) or {}
            if part.get("key") == windows.keys[window]:
                counts[window] = int(part.get("n") or 0)
        async with self.redis.pipeline(transaction=False) as pipe:
            for window, key in zip(WINDOWS, keys):
                pipe.set(key, counts[window], nx=True, exat=windows.expire_at(window))
            await pipe.execute()

    async def _reserve_mongo(self, scope, request_id, limits, checked, windows, exempt) -> Reservation:
        await self._ensure_indexes()
        current = {}
        for window in WINDOWS:
            letter = _LETTER[window]
            current[letter] = {"$cond": [{"$eq": [f"${letter}.key", windows.keys[window]]},
                                         {"$ifNull": [f"${letter}.n", 0]}, 0]}
        ok = {"$and": [
            {"$or": [{"$eq": [checked[w], 0]}, {"$lt": [f"$_c{_LETTER[w]}", checked[w]]}]} for w in WINDOWS
        ]}
        pipeline = [
            {"$set": {f"_c{k}": v for k, v in current.items()}},
            {"$set": {"_ok": ok}},
            {"$set": {
                **{_LETTER[w]: {"$cond": ["$_ok", {"key": windows.keys[w], "n": {"$add": [f"$_c{_LETTER[w]}", 1]}},
                                          f"${_LETTER[w]}"]} for w in WINDOWS},
                "last_request_id": {"$cond": ["$_ok", request_id, "$last_request_id"]},
                "role": {"$literal": scope.role or None},
                "updated_at": "$$NOW",
            }},
            {"$unset": ["_cd", "_cw", "_cm", "_ok"]},
        ]
        doc = await self.db[sync.QUOTA].find_one_and_update(
            {"tenant": scope.tenant, "user_id": scope.user_id}, pipeline,
            upsert=True, return_document=ReturnDocument.AFTER,
        )
        used = {}
        for window in WINDOWS:
            part = doc.get(_LETTER[window]) or {}
            used[window] = int(part.get("n") or 0) if part.get("key") == windows.keys[window] else 0
        if doc.get("last_request_id") != request_id:
            denied = next(w for w in WINDOWS if checked[w] and used[w] >= checked[w])
            raise LimitDenied(self._denied_payload(denied, limits, used, windows))
        res = Reservation(request_id, "mongo", scope, dict(windows.keys), self._usage(limits, used, windows, exempt))
        writes = [
            self.db[sync.FALLBACK_REQUESTS].insert_one(
                {"request_id": request_id, "state": "reserved", "tenant": scope.tenant, "user_id": scope.user_id,
                 "keys": dict(windows.keys), "created_at": datetime.now(timezone.utc)}),
            sync.apply_events(self.db, [self._event(res, "reserve")], quota=False),
        ]
        user = (scope.tenant, scope.user_id)
        if user not in self._outage_users:
            writes.append(self.db[sync.OUTAGE_USERS].update_one(
                {"tenant": scope.tenant, "user_id": scope.user_id}, {"$set": {"at": datetime.now(timezone.utc)}},
                upsert=True))
        await asyncio.gather(*writes)
        self._outage_users.add(user)
        return res

    # ---------- reservations made by the gateway ----------

    async def lookup(self, scope: CallerScope, request_id: str) -> Reservation | None:
        """The caller's own open reservation with this id (made by the gateway), or None.

        Only a reservation still in the reserved state matches, so an id cannot be reused after
        its question was answered or refunded.
        """
        if get_settings().chat_limits.mode == "off":
            return Reservation(request_id, "none")
        if self.state == "up" and self.redis is not None:
            try:
                h = await self.redis.hgetall(request_key(scope.tenant, scope.user_id, request_id))
            except Exception as e:
                self._trip(e)
            else:
                if h.get("state") == "reserved":
                    keys = {"daily": h["dk"], "weekly": h["wk"], "monthly": h["mk"]}
                    return Reservation(request_id, "redis", scope, keys)
        doc = await self.db[sync.FALLBACK_REQUESTS].find_one(
            {"request_id": request_id, "tenant": scope.tenant, "user_id": scope.user_id, "state": "reserved"},
            {"keys": 1},
        )
        return Reservation(request_id, "mongo", scope, doc["keys"]) if doc else None

    async def refund_by_id(self, scope: CallerScope, request_id: str) -> bool:
        """Refund the caller's open reservation (the gateway saw the chatbot fail); False if none."""
        res = await self.lookup(scope, request_id)
        if res is None:
            return False
        await self.refund(res)
        return True

    # ---------- commit and refund ----------

    async def commit(self, res: Reservation, outcome: str) -> None:
        """The answer was delivered: the question stays counted (no refund possible afterwards)."""
        if res.settled or res.backend == "none":
            return
        res.settled = True
        try:
            if res.backend == "redis":
                await self._scripts["commit"](
                    keys=[request_key(res.scope.tenant, res.scope.user_id, res.request_id), sync.STREAM],
                    args=[outcome, f"{time.time():.3f}"],
                )
            else:
                changed = await self.db[sync.FALLBACK_REQUESTS].update_one(
                    {"request_id": res.request_id, "state": "reserved"}, {"$set": {"state": "committed"}})
                if changed.modified_count:
                    await sync.apply_events(self.db, [self._event(res, "commit", outcome=outcome)], quota=False)
        except Exception as e:
            logger.warning("chat_limits_commit_failed | request=%s | %s", res.request_id, e)

    async def refund(self, res: Reservation) -> None:
        """A qualifying failure: give the question back, once."""
        if res.settled or res.backend == "none":
            return
        res.settled = True
        try:
            if res.backend == "redis":
                await self._scripts["refund"](
                    keys=[request_key(res.scope.tenant, res.scope.user_id, res.request_id), sync.STREAM],
                    args=[f"{time.time():.3f}"],
                )
            else:
                changed = await self.db[sync.FALLBACK_REQUESTS].update_one(
                    {"request_id": res.request_id, "state": "reserved"}, {"$set": {"state": "refunded"}})
                if changed.modified_count:
                    await self._mongo_decrement(res)
                    await sync.apply_events(self.db, [self._event(res, "refund")], quota=False)
            logger.info("chat_limits_refunded | request=%s", res.request_id)
        except Exception as e:
            logger.warning("chat_limits_refund_failed | request=%s | %s", res.request_id, e)

    async def _mongo_decrement(self, res: Reservation) -> None:
        updates = {}
        for window in WINDOWS:
            letter, key = _LETTER[window], res.window_keys[window]
            updates[letter] = {"$cond": [
                {"$and": [{"$eq": [f"${letter}.key", key]}, {"$gt": [f"${letter}.n", 0]}]},
                {"key": key, "n": {"$subtract": [f"${letter}.n", 1]}}, f"${letter}",
            ]}
        await self.db[sync.QUOTA].update_one(
            {"tenant": res.scope.tenant, "user_id": res.scope.user_id}, [{"$set": updates}])

    @staticmethod
    def _event(res: Reservation, kind: str, outcome: str = "") -> dict:
        """A usage event of the MongoDB fallback, shaped like the Redis stream events."""
        return {"type": kind, "event_id": f"{res.request_id}:{kind}", "request_id": res.request_id,
                "tenant": res.scope.tenant, "user_id": res.scope.user_id, "role": res.scope.role or "",
                "dk": res.window_keys["daily"], "wk": res.window_keys["weekly"], "mk": res.window_keys["monthly"],
                "outcome": outcome, "ts": f"{time.time():.3f}"}

    # ---------- payloads ----------

    @staticmethod
    def _denied_payload(window: str, limits: dict, used: dict, windows: Windows) -> dict:
        return {"code": "chat_limit_reached", "window": window, "limits": limits, "used": used,
                "resets_at": windows.resets_at[window].isoformat()}

    @staticmethod
    def _usage(limits: dict, used: dict, windows: Windows, exempt: bool) -> dict:
        return {"limits": limits, "used": used, "exempt": exempt,
                "resets_at": {w: windows.resets_at[w].isoformat() for w in WINDOWS}}

    # ---------- support (service key) ----------

    async def usage(self, tenant: str, user_id: str) -> dict:
        cfg = get_settings().chat_limits
        windows = current_windows(cfg.timezone)
        live = None
        if self.state == "up" and self.redis is not None:
            values = await self.redis.mget([counter_key(tenant, user_id, w, windows.keys[w]) for w in WINDOWS])
            live = {w: (int(v) if v is not None else None) for w, v in zip(WINDOWS, values)}
        quota = await self.db[sync.QUOTA].find_one({"tenant": tenant, "user_id": user_id}, {"_id": 0, "applied": 0})
        history = [d async for d in self.db[sync.USAGE].find(
            {"tenant": tenant, "user_id": user_id}, {"_id": 0, "applied": 0}).sort("period_key", -1).limit(60)]
        return {"tenant": tenant, "user_id": user_id, "mode": cfg.mode, "redis_state": self.state,
                "windows": windows.keys, "live_redis": live, "mongodb_quota": quota, "history": history,
                "queue": await self.drainer.health() if self.drainer and self.state == "up" else None}

    async def reset(self, tenant: str, user_id: str, window: str) -> dict:
        cfg = get_settings().chat_limits
        windows = current_windows(cfg.timezone)
        chosen = list(WINDOWS) if window == "all" else [window]
        if self.state == "up" and self.redis is not None:
            async with self.redis.pipeline(transaction=False) as pipe:
                for w in chosen:
                    pipe.set(counter_key(tenant, user_id, w, windows.keys[w]), 0, exat=windows.expire_at(w))
                await pipe.execute()
        await self.db[sync.QUOTA].update_one(
            {"tenant": tenant, "user_id": user_id},
            {"$set": {**{_LETTER[w]: {"key": windows.keys[w], "n": 0} for w in chosen},
                      "updated_at": datetime.now(timezone.utc)}},
            upsert=True,
        )
        logger.warning("chat_limits_reset | tenant=%s user=%s windows=%s", tenant, user_id, ",".join(chosen))
        return {"tenant": tenant, "user_id": user_id, "reset": chosen, "windows": {w: windows.keys[w] for w in chosen}}


limits = ChatLimits()
