"""MongoDB storage of documents uploaded from the admin panel. No search, no access checks.

Collections (database ``knowledge_manage.database``):

- ``knowledge_documents``: one record per document: the Markdown body the chunks are
  built from, its routes and other front matter, **who may read it** (``all_tenants``,
  ``tenants``, ``exclude_tenants``, ``roles``), hashes, status and the previous version.
- ``knowledge_chunks``: every chunk with its embedding, so the search index can be
  rebuilt without re-embedding.
- ``knowledge_audit``: who uploaded, changed access or deleted what, and when.
- ``knowledge_files``: the original uploaded file (.md, .pdf or .docx), one record per
  file. Files are capped at ``knowledge_manage.max_file_mb`` (at most 15), below MongoDB's
  16 MB document limit, so no GridFS is needed.

MongoDB is the source of truth; the registry and Chroma are rebuilt from it.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from bson import Binary, ObjectId
from pymongo import ASCENDING, DESCENDING, MongoClient, ReturnDocument

from app.config.settings import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

DOCUMENTS = "knowledge_documents"
CHUNKS = "knowledge_chunks"
AUDIT = "knowledge_audit"
FILES = "knowledge_files"

READY, PROCESSING, FAILED = "ready", "processing", "failed"


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class KnowledgeDocuments:
    def __init__(self, db: Any) -> None:
        self.db = db

    def ensure_indexes(self) -> None:
        docs = self.db[DOCUMENTS]
        docs.create_index([("doc_id", ASCENDING)], unique=True, name="doc_id_unique")
        # File names are compared without case, so "Guide.pdf" and "guide.pdf" are the same file.
        docs.create_index([("file_name_key", ASCENDING)], unique=True, name="file_name_unique")
        docs.create_index([("file_hash", ASCENDING)], name="file_hash")
        docs.create_index([("status", ASCENDING)], name="status")
        chunks = self.db[CHUNKS]
        chunks.create_index([("chunk_id", ASCENDING)], unique=True, name="chunk_id_unique")
        chunks.create_index([("doc_id", ASCENDING), ("content_hash", ASCENDING)], name="doc_hash")
        audit = self.db[AUDIT]
        audit.create_index([("doc_id", ASCENDING), ("at", DESCENDING)], name="doc_at")
        audit.create_index([("at", DESCENDING)], name="at")
        self.db[FILES].create_index([("doc_id", ASCENDING)], name="doc_id")

    # ---------- documents ----------

    def get(self, doc_id: str) -> dict[str, Any] | None:
        return self.db[DOCUMENTS].find_one({"doc_id": doc_id}, {"_id": 0})

    def by_file_name(self, file_name: str) -> dict[str, Any] | None:
        return self.db[DOCUMENTS].find_one({"file_name_key": file_name.lower()}, {"_id": 0})

    def by_file_hash(self, file_hash: str) -> dict[str, Any] | None:
        return self.db[DOCUMENTS].find_one({"file_hash": file_hash}, {"_id": 0})

    def all(self, *, with_body: bool = False) -> list[dict[str, Any]]:
        projection = {"_id": 0, "previous.body": 0}
        if not with_body:
            projection.update({"body": 0, "pending": 0})
        return list(self.db[DOCUMENTS].find({}, projection).sort("doc_id", ASCENDING))

    def insert(self, record: dict[str, Any]) -> None:
        self.db[DOCUMENTS].insert_one({**record, "file_name_key": record["file_name"].lower()})

    def update(self, doc_id: str, fields: dict[str, Any], unset: tuple[str, ...] = ()) -> dict[str, Any] | None:
        if "file_name" in fields:
            fields = {**fields, "file_name_key": fields["file_name"].lower()}
        change: dict[str, Any] = {"$set": fields}
        if unset:
            change["$unset"] = {name: "" for name in unset}
        return self.db[DOCUMENTS].find_one_and_update(
            {"doc_id": doc_id}, change, projection={"_id": 0}, return_document=ReturnDocument.AFTER
        )

    def delete(self, doc_id: str) -> dict[str, Any] | None:
        return self.db[DOCUMENTS].find_one_and_delete({"doc_id": doc_id}, projection={"_id": 0})

    # ---------- chunks ----------

    def replace_chunks(self, doc_id: str, content_hash: str, chunks: list[dict[str, Any]], model: str) -> None:
        """Store a document's chunks; chunks of other content hashes of that document are removed."""
        if chunks:
            self.db[CHUNKS].delete_many({"chunk_id": {"$in": [c["chunk_id"] for c in chunks]}})
            self.db[CHUNKS].insert_many(
                [{**c, "doc_id": doc_id, "content_hash": content_hash, "embedding_model": model} for c in chunks]
            )
        self.db[CHUNKS].delete_many({"doc_id": doc_id, "content_hash": {"$ne": content_hash}})

    def delete_chunks(self, doc_id: str) -> None:
        self.db[CHUNKS].delete_many({"doc_id": doc_id})

    def chunk_count(self, doc_id: str) -> int:
        return self.db[CHUNKS].count_documents({"doc_id": doc_id})

    # ---------- original files ----------

    def put_file(self, file_name: str, data: bytes, content_type: str, doc_id: str) -> str:
        result = self.db[FILES].insert_one({
            "doc_id": doc_id, "file_name": file_name, "content_type": content_type,
            "size": len(data), "data": Binary(data), "uploaded_at": utcnow(),
        })
        return str(result.inserted_id)

    def get_file(self, file_id: str) -> bytes:
        found = self.db[FILES].find_one({"_id": ObjectId(file_id)}, {"data": 1})
        if found is None:
            raise KeyError(file_id)
        return bytes(found["data"])

    def delete_file(self, file_id: str | None) -> None:
        if not file_id:
            return
        try:
            self.db[FILES].delete_one({"_id": ObjectId(file_id)})
        except Exception:
            logger.warning("knowledge_file_delete_failed | file_id=%s", file_id)

    # ---------- audit ----------

    def audit(self, action: str, doc_id: str, user_id: str | None, tenant: str | None, details: dict | None = None) -> None:
        self.db[AUDIT].insert_one({
            "action": action, "doc_id": doc_id, "user_id": user_id, "tenant": tenant,
            "details": details or {}, "at": utcnow(),
        })

    def audit_log(self, doc_id: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        query = {"doc_id": doc_id} if doc_id else {}
        cursor = self.db[AUDIT].find(query, {"_id": 0}).sort([("at", DESCENDING), ("_id", DESCENDING)])
        return list(cursor.limit(limit))


_client: MongoClient | None = None
_store: KnowledgeDocuments | None = None


def start() -> KnowledgeDocuments | None:
    """Connect and create the collections' indexes. None when the feature is off."""
    global _client, _store
    s = get_settings()
    cfg = s.knowledge_manage
    if not cfg.enabled:
        return None
    uri = s.chat_store_mongodb_uri.get_secret_value() if s.chat_store_mongodb_uri else s.chat_store.mongodb_uri
    _client = MongoClient(uri, serverSelectionTimeoutMS=3000, tz_aware=True)
    db = _client[cfg.database]
    db.command("ping")
    store = KnowledgeDocuments(db)
    store.ensure_indexes()
    _store = store
    logger.info("startup | knowledge documents on MongoDB database %s", cfg.database)
    return store


def use(store: KnowledgeDocuments | None) -> None:
    """Set the store directly (tests)."""
    global _store
    _store = store


def stop() -> None:
    global _client, _store
    if _client is not None:
        _client.close()
    _client = _store = None


def store() -> KnowledgeDocuments | None:
    return _store
