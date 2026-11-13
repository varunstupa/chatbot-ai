"""Documents uploaded from the admin panel: upload, change access, delete, restore at startup.

Every new version is written to the record's ``pending`` field first, then chunked and
embedded through the same path as the guides folder (``service.ingest_guide``). Only after
that succeeds does it become the live version, and the version it replaced is kept as
``previous``. A failed upload leaves the live version answering.

Access (which tenants and roles may read a document) is stored on its MongoDB record and
copied into the registry, which is what every question is checked against.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import PurePath
from threading import Lock
from typing import Any

import yaml

from app.config.settings import get_settings
from app.knowledge import documents, service
from app.knowledge.documents import FAILED, PROCESSING, READY, utcnow
from app.knowledge.extract import DOCX, MARKDOWN, PDF, extract
from app.knowledge.parser import ALL_TENANTS, GuideError, content_hash, normalize_role, parse_guide
from app.knowledge.registry import UPLOAD, is_upload
from app.services.auth import CallerScope, normalize_tenant
from app.utils.logger import get_logger

logger = get_logger(__name__)

CONTENT_TYPES = {
    MARKDOWN: "text/markdown",
    PDF: "application/pdf",
    DOCX: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
# Front matter of an uploaded .md file that is kept (access comes from the upload form).
_KEPT_FRONT_MATTER = ("routes", "aliases", "roles", "sports", "suggested_questions", "overrides")
# The fields that make up one version of a document (live, pending or previous).
_VERSION_FIELDS = (
    "title", "body", "file_name", "kind", "file_id", "size", "file_hash", "content_hash",
    "front_matter", "all_tenants", "tenants", "exclude_tenants", "roles", "chunk_count",
)
_ACCESS_FIELDS = ("all_tenants", "tenants", "exclude_tenants", "roles")

# One change at a time: the local Chroma store and the registry file have a single writer.
_job_lock = Lock()


class ManageError(Exception):
    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status
        self.message = message


def _store() -> documents.KnowledgeDocuments:
    store = documents.store()
    if store is None:
        raise ManageError(503, "Document upload is not available (knowledge_manage is off or MongoDB is down)")
    return store


# ---------- validation ----------


def parse_tenants(value: list[str] | str | None) -> tuple[bool, list[str]] | None:
    """(all_tenants, tenants) from the form; None when nothing was given."""
    if value is None:
        return None
    items = [value] if isinstance(value, str) else list(value)
    names = [n.strip() for item in items for n in str(item).split(",") if n.strip()]
    if not names:
        return None
    if any(n.lower() == ALL_TENANTS for n in names):
        return True, []
    return False, _tenant_names(names)


def _tenant_names(names: list[str]) -> list[str]:
    allowed = {t.lower() for t in get_settings().knowledge_manage.allowed_tenants}
    out = []
    for raw in names:
        name = normalize_tenant(raw)
        if name is None:
            raise ManageError(400, f"'{raw}' is not a valid tenant name")
        if allowed and name not in allowed:
            raise ManageError(400, f"Unknown tenant '{name}'")
        out.append(name)
    return sorted(set(out))


def _list(value: list[str] | str | None) -> list[str] | None:
    if value is None:
        return None
    items = [value] if isinstance(value, str) else list(value)
    return [n.strip() for item in items for n in str(item).split(",") if n.strip()]


def _default_doc_id(file_name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", PurePath(file_name).stem.lower()).strip("-")[:80]
    if not slug:
        raise ManageError(400, "Give a doc_id: the file name has no letters or digits")
    return f"upload.{slug}"


def render(version: dict[str, Any], doc_id: str) -> str:
    """The guide Markdown (front matter and body) the chunker reads."""
    fm: dict[str, Any] = {"doc_id": doc_id, "title": version["title"]}
    fm.update({k: v for k, v in (version.get("front_matter") or {}).items() if k in _KEPT_FRONT_MATTER and v})
    fm["tenants"] = ALL_TENANTS if version["all_tenants"] else list(version["tenants"])
    fm["exclude_tenants"] = list(version.get("exclude_tenants") or [])
    if version.get("roles"):
        fm["roles"] = list(version["roles"])
    return "---\n" + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True) + "---\n" + version["body"].strip() + "\n"


def _validated(version: dict[str, Any], doc_id: str) -> dict[str, Any]:
    """Check the version through the guide parser and fill in its content hash."""
    if not version["all_tenants"] and not version["tenants"]:
        raise ManageError(400, "Choose which tenants can use this document, or all tenants")
    if version["tenants"] and version.get("exclude_tenants"):
        raise ManageError(400, "Excluded tenants can only be given with all tenants")
    try:
        meta, body = parse_guide(render(version, doc_id))
    except GuideError as e:
        raise ManageError(400, str(e)) from e
    skip = frozenset(s.casefold() for s in get_settings().app_chat.index_skip_sections)
    return {**version, "roles": list(meta.roles), "content_hash": content_hash(meta, body, skip)}


def _same_version(a: dict[str, Any], b: dict[str, Any]) -> bool:
    keys = ("file_hash", "title", "file_name", "front_matter") + _ACCESS_FIELDS
    return all(a.get(k) == b.get(k) for k in keys)


# ---------- upload ----------


def upload(
    scope: CallerScope,
    file_name: str,
    data: bytes,
    *,
    tenants: list[str] | str | None = None,
    exclude_tenants: list[str] | str | None = None,
    doc_id: str | None = None,
    title: str | None = None,
    routes: list[str] | str | None = None,
    roles: list[str] | str | None = None,
    sports: list[str] | str | None = None,
) -> dict[str, Any]:
    """Add a document or replace the one with the same doc_id. Blocking: call it in a thread."""
    store = _store()
    file_name = PurePath(file_name or "").name.strip()
    max_bytes = int(get_settings().knowledge_manage.max_file_mb * 1024 * 1024)
    if len(data) > max_bytes:
        raise ManageError(413, f"The file is larger than {get_settings().knowledge_manage.max_file_mb:g} MB")
    try:
        extracted = extract(file_name, data)
    except GuideError as e:
        raise ManageError(400, str(e)) from e

    fm = extracted.front_matter
    doc_id = (doc_id or str(fm.get("doc_id") or "") or _default_doc_id(file_name)).strip().lower()
    access = parse_tenants(tenants)
    if access is None:  # an .md file's own front matter only fills in what the form left out
        raw = fm.get("tenants")
        access = parse_tenants([raw] if isinstance(raw, str) else raw)
    if access is None:
        raise ManageError(400, "Choose which tenants can use this document, or all tenants")
    excluded = _tenant_names(_list(exclude_tenants) or _list(fm.get("exclude_tenants")) or [])
    kept = {k: fm[k] for k in _KEPT_FRONT_MATTER if fm.get(k)}
    for key, value in (("routes", _list(routes)), ("sports", _list(sports))):
        if value is not None:
            kept[key] = value
    role_names = _list(roles)
    if role_names is None:
        role_names = _list(fm.get("roles")) or []
    if any(normalize_role(r) is None for r in role_names):
        raise ManageError(400, "A role name is not valid")
    kept.pop("roles", None)

    version = _validated({
        "title": (title or str(fm.get("title") or "") or extracted.title or PurePath(file_name).stem).strip(),
        "body": extracted.body,
        "file_name": file_name,
        "kind": extracted.kind,
        "size": len(data),
        "file_hash": hashlib.sha256(data).hexdigest(),
        "front_matter": kept,
        "all_tenants": access[0],
        "tenants": access[1],
        "exclude_tenants": excluded,
        "roles": [normalize_role(r) for r in role_names],
    }, doc_id)

    with _job_lock:
        existing = store.get(doc_id)
        _check_conflicts(store, doc_id, version, existing)
        if existing is not None and existing.get("body") is not None and _same_version(existing, version):
            return {"doc_id": doc_id, "result": "unchanged", "document": _public(existing)}
        version["file_id"] = store.put_file(file_name, data, CONTENT_TYPES[extracted.kind], doc_id)
        now = utcnow()
        if existing is None:
            store.insert({
                "doc_id": doc_id, "file_name": file_name, "body": None, "status": PROCESSING,
                "pending": version, "created_by": scope.user_id, "created_at": now,
                "updated_by": scope.user_id, "updated_at": now,
            })
        else:
            store.delete_file((existing.get("pending") or {}).get("file_id"))  # an earlier failed attempt
            store.update(doc_id, {"pending": version, "status": PROCESSING, "updated_by": scope.user_id,
                                  "updated_at": now}, unset=("error",))
        record = _apply_pending(store, doc_id, scope)
    created = existing is None or existing.get("body") is None
    store.audit("upload" if created else "replace", doc_id, scope.user_id, scope.tenant,
                {"file_name": file_name, "kind": extracted.kind, "re_embedded": record.pop("_re_embedded", None)})
    return {"doc_id": doc_id, "result": "created" if created else "replaced", "document": _public(record)}


def _check_conflicts(store: documents.KnowledgeDocuments, doc_id: str, version: dict[str, Any],
                     existing: dict[str, Any] | None) -> None:
    folder = service.list_guides_admin().get(doc_id)
    if existing is None and folder is not None and not is_upload(folder):
        raise ManageError(409, f"'{doc_id}' is a built-in guide; choose another doc_id")
    named = store.by_file_name(version["file_name"])
    if named is not None and named["doc_id"] != doc_id:
        raise ManageError(409, f"A file named '{version['file_name']}' is already uploaded as '{named['doc_id']}'")
    same = store.by_file_hash(version["file_hash"])
    if same is not None and same["doc_id"] != doc_id:
        raise ManageError(409, f"This file is already uploaded as '{same['doc_id']}'")


def _apply_pending(store: documents.KnowledgeDocuments, doc_id: str, scope: CallerScope | None) -> dict[str, Any]:
    """Chunk and embed the pending version, then make it live. Called under _job_lock."""
    record = store.get(doc_id)
    pending = record["pending"]
    try:
        result = service.ingest_guide(render(pending, doc_id), UPLOAD)
        chunks = service.export_document(doc_id)
        store.replace_chunks(doc_id, pending["content_hash"], chunks, get_settings().app_chat.embedding_model)
    except Exception as e:
        message = str(e) if isinstance(e, GuideError) else "Processing failed; the previous version is still live"
        logger.exception("knowledge_upload_failed | doc_id=%s", doc_id)
        store.delete_file(pending.get("file_id"))
        store.update(doc_id, {"status": FAILED, "error": message}, unset=("pending",))
        if record.get("body") is not None:
            # The registry may already carry the new access; put the live version back.
            service.ingest_guide(render(record, doc_id), UPLOAD)
        else:
            service.delete_guide(doc_id)  # never readable without a live version
        raise ManageError(400 if isinstance(e, GuideError) else 500, message) from e

    live = {k: record.get(k) for k in _VERSION_FIELDS} if record.get("body") is not None else None
    old_previous = record.get("previous") or {}
    if old_previous.get("file_id") and old_previous.get("file_id") != (live or {}).get("file_id"):
        store.delete_file(old_previous["file_id"])
    fields = {**{k: pending.get(k) for k in _VERSION_FIELDS}, "chunk_count": result["chunks_indexed"],
              "status": READY, "updated_at": utcnow()}
    if live is not None:
        fields["previous"] = {**live, "replaced_at": utcnow()}
    updated = store.update(doc_id, fields, unset=("pending", "error"))
    service.refresh_caches()
    updated["_re_embedded"] = result["re_embedded"]
    logger.info("knowledge_upload_ready | doc_id=%s chunks=%s re_embedded=%s by=%s", doc_id,
                result["chunks_indexed"], result["re_embedded"], scope.user_id if scope else "startup")
    return updated


# ---------- access, delete, list ----------


def set_access(
    scope: CallerScope,
    doc_id: str,
    *,
    tenants: list[str] | str | None,
    exclude_tenants: list[str] | str | None = None,
    roles: list[str] | str | None = None,
) -> dict[str, Any]:
    """Change who may read a document. Takes effect at once and never re-embeds."""
    store = _store()
    access = parse_tenants(tenants)
    if access is None:
        raise ManageError(400, "Choose which tenants can use this document, or all tenants")
    with _job_lock:
        record = store.get(doc_id)
        if record is None or record.get("body") is None:
            raise ManageError(404, f"No uploaded document '{doc_id}'")
        role_names = (record.get("roles") or []) if roles is None else (_list(roles) or [])
        if any(normalize_role(r) is None for r in role_names):
            raise ManageError(400, "A role name is not valid")
        version = _validated({
            **{k: record.get(k) for k in _VERSION_FIELDS},
            "all_tenants": access[0], "tenants": access[1],
            "exclude_tenants": _tenant_names(_list(exclude_tenants) or []),
            "roles": [normalize_role(r) for r in role_names],
        }, doc_id)
        before = {k: record.get(k) for k in _ACCESS_FIELDS}
        after = {k: version[k] for k in _ACCESS_FIELDS}
        # MongoDB first: if it is down the change is refused, and the registry never runs ahead of it.
        updated = store.update(doc_id, {**after, "updated_by": scope.user_id, "updated_at": utcnow()})
        service.ingest_guide(render(updated, doc_id), UPLOAD)
        service.refresh_caches()
    store.audit("access", doc_id, scope.user_id, scope.tenant, {"before": before, "after": after})
    return _public(updated)


def delete(scope: CallerScope, doc_id: str) -> None:
    store = _store()
    with _job_lock:
        record = store.get(doc_id)
        if record is None:
            raise ManageError(404, f"No uploaded document '{doc_id}'")
        service.delete_guide(doc_id)  # access is revoked before anything else is removed
        store.delete_chunks(doc_id)
        for version in (record, record.get("pending") or {}, record.get("previous") or {}):
            store.delete_file(version.get("file_id"))
        store.delete(doc_id)
        service.refresh_caches()
    store.audit("delete", doc_id, scope.user_id, scope.tenant, {"file_name": record.get("file_name")})


def list_documents() -> list[dict[str, Any]]:
    return [_public(r) for r in _store().all()]


def original_file(doc_id: str) -> tuple[str, str, bytes]:
    """(file name, content type, bytes) of the live version's uploaded file."""
    store = _store()
    record = store.get(doc_id)
    if record is None or not record.get("file_id"):
        raise ManageError(404, f"No uploaded document '{doc_id}'")
    return record["file_name"], CONTENT_TYPES[record["kind"]], store.get_file(record["file_id"])


def _public(record: dict[str, Any]) -> dict[str, Any]:
    out = {k: v for k, v in record.items() if k not in ("body", "pending", "file_name_key")}
    if out.get("previous"):
        out["previous"] = {k: record["previous"].get(k) for k in ("file_name", "file_hash", "replaced_at")}
    if record.get("pending"):
        out["pending_file_name"] = record["pending"].get("file_name")
    return out


# ---------- startup ----------


def restore() -> dict[str, int]:
    """Bring the registry and search index in line with MongoDB. Blocking: call it in a thread.

    Live versions are loaded (unchanged ones cost nothing; missing chunks are re-embedded),
    uploads interrupted by a crash are finished, and an uploaded document that MongoDB no
    longer has is removed, so nothing stays readable without a record.
    """
    store = documents.store()
    report = {"loaded": 0, "resumed": 0, "removed": 0, "failed": 0}
    if store is None:
        return report
    with _job_lock:
        records = store.all(with_body=True)
        for record in records:
            doc_id = record["doc_id"]
            try:
                if record.get("body") is not None:
                    service.ingest_guide(render(record, doc_id), UPLOAD)
                    report["loaded"] += 1
                if record.get("pending"):
                    _apply_pending(store, doc_id, None)
                    report["resumed"] += 1
            except Exception:
                logger.exception("knowledge_restore_failed | doc_id=%s", doc_id)
                report["failed"] += 1
        known = {r["doc_id"] for r in records}
        for doc_id, entry in service.list_guides_admin().items():
            if is_upload(entry) and doc_id not in known:
                service.delete_guide(doc_id)
                report["removed"] += 1
    logger.info("startup | uploaded documents restored | %s", report)
    return report
