"""Knowledge service: ingest guides and read them back for one caller.

Write path (service key only): parse -> registry access update -> re-embed only
when the content changed. Read path: registry decides which documents the
caller may read; the single chunk collection is queried for those doc_ids only,
and every hit is checked against that list again.

Every read function takes a ``CallerScope``; none accepts a raw tenant string.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from threading import RLock
from typing import Any

from app.config.settings import get_settings
from app.knowledge.index import ChunkIndex
from app.knowledge.parser import (
    GuideError,
    build_chunks,
    content_hash,
    normalize_route,
    parse_guide,
)
from app.knowledge.registry import DocumentRegistry, entry_from_meta, is_tenant_specific
from app.services.auth import CallerScope
from app.services.embedding import get_embeddings
from app.utils.logger import get_logger

logger = get_logger(__name__)

__all__ = [
    "GuideError",
    "Hit",
    "delete_guide",
    "guides_for_screen",
    "guides_named_in",
    "ingest_guide",
    "list_guides_admin",
    "overview",
    "screen_info",
    "search",
    "visible_guides",
]

_lock = RLock()
_registries: dict[str, DocumentRegistry] = {}
_indexes: dict[str, ChunkIndex] = {}


@dataclass(frozen=True)
class Hit:
    doc_id: str
    title: str
    section: str
    content: str
    distance: float
    tenant_specific: bool


# ---------- wiring ----------


def _kb_dir() -> Path:
    path = Path(get_settings().app_chat.persist_directory).resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


def _registry() -> DocumentRegistry:
    path = _kb_dir() / get_settings().app_chat.registry_file
    with _lock:
        if str(path) not in _registries:
            _registries[str(path)] = DocumentRegistry(path)
        return _registries[str(path)]


def _index() -> ChunkIndex:
    cfg = get_settings().app_chat
    key = f"{_kb_dir()}::{cfg.collection_name}"
    with _lock:
        if key not in _indexes:
            _indexes[key] = ChunkIndex(_kb_dir(), cfg.collection_name, get_embeddings())
        return _indexes[key]


def reset_for_tests() -> None:
    with _lock:
        _registries.clear()
        _indexes.clear()


# ---------- write side (service key only) ----------


def ingest_guide(text: str) -> dict[str, Any]:
    """Insert or update one guide.

    Access, routes, aliases and suggestions are registry data: changing only
    those never re-embeds. Chunks are rebuilt only when the content hash changes
    (or the stored chunks are missing).
    """
    meta, body = parse_guide(text)
    cfg = get_settings().app_chat
    doc_hash = content_hash(meta, body)
    registry, index = _registry(), _index()

    with _lock:
        previous = registry.get(meta.doc_id)
        unchanged = (
            previous is not None
            and previous.get("content_hash") == doc_hash
            and index.count(meta.doc_id) == previous.get("chunk_count")
        )
        if unchanged:
            chunk_count = int(previous["chunk_count"])
            old_routes = previous.get("routes") or []
            new_route = meta.routes[0] if meta.routes else ""
            if (old_routes[0] if old_routes else "") != new_route:
                index.set_route(meta.doc_id, new_route)
        else:
            chunks = build_chunks(
                meta, body, doc_hash,
                chunk_size=cfg.chunk_size, chunk_overlap=cfg.chunk_overlap,
            )
            if not chunks:
                raise GuideError("Guide produced no content")
            if previous is not None:
                # Apply the new access before the content swap, so a narrowed
                # audience never sees the new text under the old rules.
                registry.upsert(
                    meta.doc_id,
                    entry_from_meta(meta, str(previous.get("content_hash") or ""),
                                    int(previous.get("chunk_count") or 0)),
                )
            index.replace_document(meta.doc_id, chunks)
            chunk_count = len(chunks)
        # A new document becomes readable only here, after its chunks exist.
        registry.upsert(meta.doc_id, entry_from_meta(meta, doc_hash, chunk_count))

    logger.info(
        "knowledge_ingested | doc_id=%s tenants=%s roles=%s chunks=%s re_embedded=%s",
        meta.doc_id,
        "all" if meta.tenants is None else ",".join(meta.tenants),
        ",".join(meta.roles) or "-",
        chunk_count,
        not unchanged,
    )
    return {
        "doc_id": meta.doc_id,
        "title": meta.title,
        "tenants": "all" if meta.tenants is None else list(meta.tenants),
        "roles": list(meta.roles),
        "chunks_indexed": chunk_count,
        "re_embedded": not unchanged,
        "replaced": previous is not None,
    }


def delete_guide(doc_id: str) -> bool:
    key = (doc_id or "").strip().lower()
    with _lock:
        # Registry first: access is revoked before any chunk is touched.
        entry = _registry().remove(key)
        if entry is None:
            return False
        _index().delete_document(key)
    logger.info("knowledge_deleted | doc_id=%s", key)
    return True


def list_guides_admin() -> dict[str, dict[str, Any]]:
    """Whole registry. Service-key callers only."""
    return _registry().all()


# ---------- read side (always scoped) ----------


def visible_guides(scope: CallerScope) -> dict[str, dict[str, Any]]:
    return _registry().allowed(scope)


def _pattern_matches(pattern: str, url_path: str) -> bool:
    regex = "^" + re.sub(r":[A-Za-z_][A-Za-z0-9_]*", "[^/]+", re.escape(pattern).replace(r"\:", ":")) + "$"
    return re.match(regex, url_path) is not None


def guides_for_screen(scope: CallerScope, route: str | None, url: str | None = None) -> list[str]:
    """doc_ids documenting the screen: exact route pattern, else URL match."""
    guides = visible_guides(scope)
    pattern = normalize_route(route or "")
    found = [d for d, e in guides.items() if pattern and pattern in (e.get("routes") or [])]
    if not found and url:
        path = normalize_route(url)
        found = [
            d for d, e in guides.items()
            if any(_pattern_matches(r, path) for r in (e.get("routes") or []))
        ]
    # Tenant overlays first so their wording wins.
    return sorted(found, key=lambda d: not is_tenant_specific(guides[d]))


def guides_named_in(scope: CallerScope, question: str) -> list[str]:
    """doc_ids whose title or an alias appears as whole words in the question."""
    q = " " + re.sub(r"[^a-z0-9]+", " ", (question or "").lower()).strip() + " "
    found: list[str] = []
    for doc_id, entry in visible_guides(scope).items():
        names = [str(entry.get("title") or "").lower(), *(entry.get("aliases") or [])]
        for name in names:
            norm = re.sub(r"[^a-z0-9]+", " ", name).strip()
            if len(norm) >= 4 and f" {norm} " in q:
                found.append(doc_id)
                break
    return found


def screen_info(scope: CallerScope, route: str | None, url: str | None = None) -> dict[str, Any] | None:
    ids = guides_for_screen(scope, route, url)
    if not ids:
        return None
    guides = visible_guides(scope)
    questions: list[str] = []
    for doc_id in ids:
        for q in guides[doc_id].get("suggested_questions") or []:
            if q not in questions:
                questions.append(q)
    # The base guide names the screen; overlays only add detail.
    base = ids[-1]
    return {
        "doc_ids": ids,
        "title": guides[base].get("title") or "",
        "suggested_questions": questions[:6],
    }


def _checked_hit(
    text: str,
    metadata: dict,
    distance: float,
    scope: CallerScope,
    allowed: dict[str, dict[str, Any]],
) -> Hit | None:
    """Defence in depth: drop any chunk whose document the caller may not read."""
    doc_id = metadata.get("doc_id")
    if doc_id not in allowed:
        logger.error(
            "security | dropped chunk outside scope | tenant=%s role=%s doc_id=%s",
            scope.tenant, scope.role, doc_id,
        )
        return None
    return Hit(
        doc_id=str(doc_id),
        title=str(metadata.get("title") or ""),
        section=str(metadata.get("section") or ""),
        content=text,
        distance=distance,
        tenant_specific=is_tenant_specific(allowed[doc_id]),
    )


def search(scope: CallerScope, query: str, *, doc_ids: list[str] | None = None) -> list[Hit]:
    """Closest chunks the caller may read, best first. ``doc_ids`` narrows to guides."""
    q = (query or "").strip()
    if not q:
        return []
    allowed = visible_guides(scope)
    wanted = list(allowed) if doc_ids is None else [d for d in doc_ids if d in allowed]
    if not wanted:
        return []

    cfg = get_settings().app_chat
    hits = [
        hit
        for text, metadata, distance in _index().query(q, wanted, cfg.top_k)
        if (hit := _checked_hit(text, metadata, distance, scope, allowed)) is not None
    ]
    # A relevant tenant-specific chunk (overlay or private guide) goes before
    # shared chunks, so the tenant's wording wins over the base guide's.
    hits.sort(
        key=lambda h: (
            0 if h.tenant_specific and h.distance <= cfg.screen_max_distance else 1,
            h.distance,
        )
    )
    return hits


def overview(scope: CallerScope, doc_ids: list[str], limit: int = 2) -> list[Hit]:
    """Opening chunks of the given guides, for vague 'how does this work' questions."""
    allowed = visible_guides(scope)
    hits: list[Hit] = []
    for doc_id in doc_ids:
        if doc_id not in allowed:
            continue
        for text, metadata in _index().document_chunks(doc_id)[:limit]:
            hit = _checked_hit(text or "", metadata or {}, 0.0, scope, allowed)
            if hit is not None:
                hits.append(hit)
    return hits[: max(limit, 1) * 2]
