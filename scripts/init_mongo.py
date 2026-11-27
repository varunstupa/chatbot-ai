"""Create the admin chatbot's MongoDB collections and indexes ahead of time (idempotent).

The backend creates these itself when a feature is switched on (chat store, question limits,
document upload). Run this once on a new server so the database is ready before any feature is
enabled, or again after an upgrade; running it twice changes nothing.

It uses the backend's own index code, so the script and the app can never disagree.

    python -m scripts.init_mongo                 # every collection
    python -m scripts.init_mongo --only chat     # chat store only (chat, limits, documents)

In Docker:  docker compose -p stupa-chatbot exec backend python -m scripts.init_mongo

Connection: CHAT_STORE_MONGODB_URI from the environment / .env (else chat_store.mongodb_uri);
database: chat_store.database / knowledge_manage.database in the active config (APP_ENV).
The URI is never printed.
"""

from __future__ import annotations

import argparse
import asyncio
import sys

from pymongo import AsyncMongoClient, MongoClient

from app.config.settings import get_settings
from app.knowledge.documents import KnowledgeDocuments
from app.services import chat_usage_sync
from app.services.chat_store import ChatStore

PARTS = ("chat", "limits", "documents")


def _uri() -> str:
    s = get_settings()
    env = s.chat_store_mongodb_uri.get_secret_value().strip() if s.chat_store_mongodb_uri else ""
    return env or s.chat_store.mongodb_uri


async def _async_parts(uri: str, parts: set[str]) -> None:
    s = get_settings()
    client = AsyncMongoClient(uri, serverSelectionTimeoutMS=5000, tz_aware=True)
    try:
        db = client[s.chat_store.database]
        await db.command("ping")
        if "chat" in parts:
            store = ChatStore(uri, s.chat_store.database, retention_days=s.chat_store.retention_days)
            store.client, store.db = client, db  # reuse this connection; the writer loop is not started
            await store._ensure_indexes()
            print(f"chat store      -> {s.chat_store.database}: chat_sessions, chat_feedback")
        if "limits" in parts:
            await chat_usage_sync.ensure_indexes(db, s.chat_limits.retention_days)
            print(
                f"question limits -> {s.chat_store.database}: {chat_usage_sync.USAGE}, {chat_usage_sync.QUOTA}, "
                f"{chat_usage_sync.FALLBACK_REQUESTS}, {chat_usage_sync.OUTAGE_USERS}"
            )
    finally:
        await client.close()


def _documents(uri: str) -> None:
    s = get_settings()
    client = MongoClient(uri, serverSelectionTimeoutMS=5000, tz_aware=True)
    try:
        db = client[s.knowledge_manage.database]
        db.command("ping")
        KnowledgeDocuments(db).ensure_indexes()
        print(
            f"documents       -> {s.knowledge_manage.database}: knowledge_documents, knowledge_chunks, "
            "knowledge_files, knowledge_audit"
        )
    finally:
        client.close()


def _report(uri: str) -> None:
    """Collections and index names now in each database (names only, no data)."""
    s = get_settings()
    client = MongoClient(uri, serverSelectionTimeoutMS=5000, tz_aware=True)
    try:
        for name in sorted({s.chat_store.database, s.knowledge_manage.database}):
            db = client[name]
            print(f"\n{name}:")
            for coll in sorted(db.list_collection_names()):
                indexes = sorted(i["name"] for i in db[coll].list_indexes())
                print(f"  {coll}: {', '.join(indexes)}")
    finally:
        client.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--only", choices=PARTS, action="append", help="limit to one part (repeatable)")
    args = parser.parse_args(argv)
    parts = set(args.only or PARTS)
    uri = _uri()
    try:
        if parts & {"chat", "limits"}:
            asyncio.run(_async_parts(uri, parts))
        if "documents" in parts:
            _documents(uri)
        _report(uri)
    except Exception as e:  # connection or permission problems: say what failed, not the URI
        print(f"init_mongo failed: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    print("\ndone (safe to run again)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
