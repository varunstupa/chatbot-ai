"""Document registry: the runtime access layer.

One entry per guide, holding who may read it and how its screen is found.
Access is decided here and only here; chunks in the vector index carry no
tenant or role data.

Stored as one JSON file, rewritten atomically. Readers in every worker reload it
when the file changes, so an access change takes effect without a restart.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Any

from app.knowledge.parser import ALL_TENANTS, GuideMeta, normalize_role
from app.services.auth import CallerScope
from app.utils.logger import get_logger

logger = get_logger(__name__)

REGISTRY_VERSION = 2


def entry_from_meta(meta: GuideMeta, doc_hash: str, chunk_count: int) -> dict[str, Any]:
    return {
        "title": meta.title,
        "routes": list(meta.routes),
        "aliases": list(meta.aliases),
        "access": {
            "tenants": ALL_TENANTS if meta.tenants is None else list(meta.tenants),
            "exclude_tenants": list(meta.exclude_tenants),
            "roles": list(meta.roles),
        },
        "overrides": meta.overrides or None,
        "suggested_questions": list(meta.suggested_questions),
        "sports": list(meta.sports),
        "content_hash": doc_hash,
        "chunk_count": chunk_count,
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def is_sport_specific(entry: dict[str, Any]) -> bool:
    return bool(entry.get("sports"))


def entry_matches_sport(entry: dict[str, Any], sport: str | None) -> bool:
    """A guide limited to sports applies only to those; unknown sport sees only shared guides."""
    sports = entry.get("sports") or []
    return not sports or sport in sports


def is_tenant_specific(entry: dict[str, Any]) -> bool:
    return entry.get("access", {}).get("tenants") != ALL_TENANTS


def entry_allows(entry: dict[str, Any], scope: CallerScope) -> bool:
    """Whether the caller may read this document. Fails closed on a malformed entry."""
    access = entry.get("access")
    if not isinstance(access, dict):
        return False
    tenants = access.get("tenants")
    if tenants == ALL_TENANTS:
        if scope.tenant in (access.get("exclude_tenants") or []):
            return False
    elif not isinstance(tenants, list) or scope.tenant not in tenants:
        return False
    roles = access.get("roles") or []
    if roles:
        caller_role = normalize_role(scope.role)
        if caller_role is None or caller_role not in roles:
            return False
    return True


class DocumentRegistry:
    def __init__(self, path: Path):
        self._path = path
        self._lock = RLock()
        self._docs: dict[str, dict[str, Any]] = {}
        self._mtime: float | None = None

    def _reload_if_changed(self) -> None:
        try:
            mtime = os.stat(self._path).st_mtime
        except FileNotFoundError:
            self._docs, self._mtime = {}, None
            return
        if mtime == self._mtime:
            return
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            # Keep serving the last good copy rather than dropping every document.
            logger.exception("knowledge_registry_unreadable")
            return
        if not isinstance(data, dict) or data.get("version") != REGISTRY_VERSION:
            logger.error("knowledge_registry_unexpected_format | path=%s", self._path)
            self._docs, self._mtime = {}, mtime
            return
        docs = data.get("documents")
        self._docs = docs if isinstance(docs, dict) else {}
        self._mtime = mtime

    def _write(self, docs: dict[str, dict[str, Any]]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self._path.with_suffix(".tmp")
        payload = {"version": REGISTRY_VERSION, "documents": docs}
        tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(self._path)
        self._docs = docs
        self._mtime = os.stat(self._path).st_mtime

    def all(self) -> dict[str, dict[str, Any]]:
        with self._lock:
            self._reload_if_changed()
            return dict(self._docs)

    def get(self, doc_id: str) -> dict[str, Any] | None:
        return self.all().get(doc_id)

    def upsert(self, doc_id: str, entry: dict[str, Any]) -> None:
        with self._lock:
            self._reload_if_changed()
            docs = dict(self._docs)
            docs[doc_id] = entry
            self._write(docs)

    def remove(self, doc_id: str) -> dict[str, Any] | None:
        with self._lock:
            self._reload_if_changed()
            docs = dict(self._docs)
            entry = docs.pop(doc_id, None)
            if entry is not None:
                self._write(docs)
            return entry

    def allowed(self, scope: CallerScope) -> dict[str, dict[str, Any]]:
        """Documents this caller may read, keyed by doc_id."""
        return {doc_id: e for doc_id, e in self.all().items() if entry_allows(e, scope)}
