# Admin-app chat knowledge: single collection, document-level access

Status: implemented in `app/knowledge/`, migrated on the dev machine (2026-10-06).
Supersedes the per-tenant collections (`kb_common`, `kb_t_<tenant>`).

Sized for 50–500 tenants, 100–1,000 guides and 10,000–100,000 chunks on one
backend instance.

## 1. Architecture

```
CHATBOT BACKEND REPO (FastAPI)
guides/**/*.md  (source of truth, edited by hand when a screen changes)
        │ loaded at every start (guide_loader), or by hand:
        │ python -m app.knowledge.guide_loader
        ▼
guide_loader ──► parser ──► content_hash changed?
                                              │ yes                 │ no
                                              ▼                     ▼
                                   re-chunk + re-embed       registry update only
                                   ChunkIndex (Chroma)       (access, routes, aliases,
                                   knowledge_chunks           suggestions)
                                              │                     │
                                              └──────► DocumentRegistry
                                                       document_registry.json

Angular widget ─ question + route + JWT ─► POST /api/app-chat
   1. auth.resolve_scope: JWT → tenant, user, role → CallerScope (immutable)
   2. registry.allowed(scope)          → allowed doc_ids
   3. registry routes / aliases         → screen doc_ids (∩ allowed)
   4. ChunkIndex.query(where doc_id $in allowed)  → chunks
   5. guard: drop any chunk whose doc_id ∉ allowed (logged as security event)
   6. prompt + last N messages → Ollama → SSE stream back
```

Rules this design keeps:

| Rule | Where it holds |
|---|---|
| Markdown is the source of truth | Guides live in the frontend repo; the backend never edits them |
| Registry is the runtime access layer | `DocumentRegistry.allowed(scope)` is the only access decision |
| Chroma stores content only | Chunk metadata has no tenant or role |
| No Markdown reads at runtime | Reads use the registry and Chroma only |
| Tenant only from the validated JWT | `auth.resolve_scope`; header must match or 403 |
| Access change = registry only | `ingest_guide` compares `content_hash`; unchanged text is not re-embedded |
| Content change = re-chunk + re-embed | Same function, hash differs |

## 2. Folder structure

```
app/
  knowledge/
    parser.py          GuideMeta, parse_guide, content_hash, build_chunks (pure, no I/O)
    registry.py        DocumentRegistry, entry_allows, entry_from_meta
    index.py           ChunkIndex: the single Chroma collection
    service.py         ingest/delete + scoped reads (search, overview, screen lookup)
    guide_loader.py    loads guides/ at startup; removes guides whose file is gone
    migrate_legacy.py  one-off removal of kb_common / kb_t_* and the v1 registry
  services/
    auth.py            CallerScope, JWT checks, service-key check
    app_chat.py        retrieval strategy (named screen → current screen → fallback)
  api/
    app_chat.py        /app-chat, /knowledge/screen, /knowledge/documents (read-only)
guides/
  README.md            how to write a guide
  tms/event-settings/  create-event.md, registration.md
tests/
  test_app_chat_isolation.py   (also validates every file in guides/)
```

The frontend repo has no knowledge files or tooling; it only sends the route,
token and tenant with each question.

## 3. Python classes

| Class / function | Responsibility |
|---|---|
| `parser.GuideMeta` | Validated front matter: `doc_id`, `title`, `routes`, `aliases`, `tenants` (None = all), `exclude_tenants`, `roles`, `overrides`, `suggested_questions` |
| `parser.parse_guide(text)` | Front matter + body; rejects a guide without `tenants` |
| `parser.content_hash(meta, body)` | sha256 of chunker version + title + body. Decides re-embedding |
| `parser.build_chunks(...)` | `##` sections, FAQ pairs as single chunks, deterministic `chunk_id` |
| `registry.DocumentRegistry` | Load (reload on file change), `upsert`, `remove`, `allowed(scope)` |
| `registry.entry_allows(entry, scope)` | Tenant, exclude list and role check. Malformed entry → deny |
| `index.ChunkIndex` | `replace_document`, `delete_document`, `query(text, doc_ids, k)`, `document_chunks`, `set_route` |
| `service.ingest_guide(text)` | Registry-only update or re-embed, in a safe order |
| `service.search(scope, q, doc_ids)` | Allowed ∩ requested doc_ids → query → guard → rank |
| `auth.CallerScope` | Frozen dataclass: `tenant`, `user_id`, `role` |

Core of the read path (`service.search`):

```python
allowed = registry.allowed(scope)                 # {doc_id: entry}
wanted = [d for d in (doc_ids or allowed) if d in allowed]
rows = index.query(question, wanted, k=top_k)     # where={"doc_id": {"$in": wanted}}
hits = [h for h in rows if h.doc_id in allowed]   # guard; mismatches are logged
```

## 4. Registry design

File `data/chroma_kb/document_registry.json`, written atomically (temp file +
rename). Every worker re-reads it when its modification time changes, so an
access change applies to all workers without a restart.

```json
{
  "version": 2,
  "documents": {
    "tms.event-settings.registration": {
      "title": "Registration settings page",
      "routes": ["tms/event-settings/registration/:event_id"],
      "aliases": ["registration settings", "registration step"],
      "access": {
        "tenants": "all",
        "exclude_tenants": [],
        "roles": []
      },
      "overrides": null,
      "suggested_questions": ["How do I open registration for a category?"],
      "content_hash": "<sha256 of title + body + chunker version>",
      "chunk_count": 57,
      "updated_at": "2026-10-06T05:58:41+00:00"
    }
  }
}
```

Access semantics:

| Front matter | Readable by |
|---|---|
| `tenants: all` | Every tenant |
| `tenants: all` + `exclude_tenants: [x]` | Every tenant except x |
| `tenants: [a, b]` | Tenants a and b only |
| `roles: [admin]` (with any of the above) | Only callers whose token role is `admin` |
| `roles` empty or absent | Every role |

Roles are matched case-insensitively against the token's `role_name` claim (then
`role_id`), configured in `auth.role_claims`. A caller with no role claim cannot
read a role-restricted guide.

The registry is generated only by the guide loader from `guides/`. It is never
edited by hand.

## 5. Chroma metadata

One collection, `knowledge_chunks` (`app_chat.collection_name`).

```json
{
  "chunk_id": "tms.event-settings.registration::b1d9c897e2e3::0007",
  "doc_id": "tms.event-settings.registration",
  "title": "Registration settings page",
  "section": "Queue Settings card: category capacity and the queue",
  "chunk_index": 7,
  "route": "tms/event-settings/registration/:event_id"
}
```

- `chunk_id` is `doc_id::content_hash[:12]::index`, also used as the Chroma id,
  so re-ingesting the same content is idempotent.
- `title` and `section` are content: they lead the chunk text and appear in
  sources. A title change therefore re-embeds.
- `route` is informational (the first route). The registry is authoritative for
  routing; a route-only change rewrites this field without re-embedding.
- No tenant, role or other access data is ever written to a chunk.

## 6. Retrieval flow

1. `resolve_scope` turns the JWT into `CallerScope(tenant, user_id, role)`.
2. `registry.allowed(scope)` gives the readable documents.
3. Screen documents: registry `routes` match the request's route pattern
   (fallback: match the URL against the patterns). Tenant overlays sort first.
4. Strategy (`services/app_chat.retrieve`):
   - a guide named in the question (title or alias) is searched first;
   - otherwise the current screen's guides (limit `screen_max_distance`);
   - other allowed guides compete with a stricter limit (`max_distance`) and win
     only when closer by `other_screen_margin`;
   - vague questions get the guide's opening chunks;
   - nothing relevant → fixed "couldn't find" reply, no model call.
5. One Chroma query per strategy step with `where doc_id $in [...]`, `k = top_k`.
6. Guard drops anything outside `allowed`; tenant-specific documents rank first.
7. Prompt + last `history_messages` messages → LLM → SSE.

## 7. FastAPI implementation

| Route | Auth | Purpose |
|---|---|---|
| `POST /api/app-chat` (JSON or SSE) | JWT | Ask |
| `POST /api/app-chat/stream` | JWT | Ask, SSE |
| `GET /api/knowledge/screen?route=` | JWT | Screen title + suggested questions |
| `GET /api/knowledge/documents` | `X-Service-Key` | Whole registry (read-only) |

Every chat route depends on `require_scope`. Guides cannot be written over HTTP;
they change only through files in `guides/`.

## 8. Loading guides

When a screen changes, edit its guide in `guides/` by hand (see
`guides/README.md`), run the tests, and restart the backend. The loader runs
before the API starts (`python -m app.main` and `docker/entrypoint.sh`). It can
be run alone only while the backend is stopped (the local Chroma store is not
safe for two processes; a running backend would keep a stale index):

```
python -m app.knowledge.guide_loader
ok       tms.event-settings.create-event  (tms/event-settings/create-event.md)  chunks=54  unchanged content
ok       tms.event-settings.registration  (tms/event-settings/registration.md)  chunks=57  re-embedded
removed  old.guide  (its file no longer exists)
ERROR    broken.md: `tenants` is required: use `all` or a list of tenant names
```

Rules: `README.md` files are skipped; two files with the same `doc_id` are an
error; if any guide has an error nothing is removed; an empty or missing folder
removes nothing. Exit code 1 when there were errors (the container still starts).

Per guide, the backend does:

| Case | Action | Order |
|---|---|---|
| New guide | Chunk, embed, write chunks, then registry | Readable only after the registry entry exists |
| Same content, access/routes/aliases changed | Registry only (route field rewritten if needed) | Immediate |
| Content changed | Registry with new access, replace chunks, registry with new hash | A narrowed audience never sees new text under old rules |
| File deleted | Registry entry removed, then chunks | Access revoked first |

Bumping `CHUNKER_VERSION` in `parser.py` makes the next load re-embed every guide.

## 9. Database schema

None is needed at this size: the registry is a ~1 MB JSON file for 1,000 guides
and Chroma persists to disk.

Move the registry to Postgres when running more than one backend host (the JSON
file is per host). Suggested table, same fields:

```sql
CREATE TABLE knowledge_documents (
    doc_id              TEXT PRIMARY KEY,
    title               TEXT NOT NULL,
    routes              TEXT[] NOT NULL DEFAULT '{}',
    aliases             TEXT[] NOT NULL DEFAULT '{}',
    tenants             TEXT[],              -- NULL means all tenants
    exclude_tenants     TEXT[] NOT NULL DEFAULT '{}',
    roles               TEXT[] NOT NULL DEFAULT '{}',
    overrides           TEXT REFERENCES knowledge_documents(doc_id),
    suggested_questions TEXT[] NOT NULL DEFAULT '{}',
    content_hash        TEXT NOT NULL,
    chunk_count         INTEGER NOT NULL,
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX knowledge_documents_tenants ON knowledge_documents USING GIN (tenants);
CREATE INDEX knowledge_documents_routes  ON knowledge_documents USING GIN (routes);
```

Only `registry.py` changes; `entry_allows` becomes a `WHERE` clause or stays in
Python over a cached result.

## 10. Security considerations

- **Trade-off accepted:** one collection replaces physical per-tenant separation.
  Isolation now rests on two independent checks, both covered by tests:
  1. the Chroma query is restricted to `doc_id $in allowed`;
  2. every returned chunk is checked against `allowed` again and dropped if not
     in it, with a security log line.
- Access fails closed: a guide without `tenants` is rejected at lint and ingest;
  a malformed registry entry denies access; an unreadable registry keeps the
  last good copy instead of opening everything.
- Tenant only from the token; a disagreeing `tenant` header is refused (403);
  `auth.allowed_tenants` limits which tenants a deployment serves.
- **Token signatures:** the staging setup decodes tokens without verifying the
  signature (`APP_CHAT_ALLOW_UNVERIFIED_DEV_TOKENS`). Production must set
  `APP_CHAT_JWT_PUBLIC_KEY` (the user-role service's RS256 public key).
- Writes need `X-Service-Key`, compared in constant time; unset key → 503.
- Chat history keyed by `tenant--user--session`.
- Sources sent to the browser contain guide title and section only.
- `doc_id`, tenant and role names are validated against strict patterns, so they
  cannot inject into Chroma filters.

## 11. Scaling considerations

- **Chroma:** 100,000 chunks × 768 dimensions ≈ 300 MB of vectors; a filtered
  HNSW query on one collection stays in the low tens of milliseconds. The
  `$in` list is at most ~1,000 doc_ids.
- **The model is the bottleneck,** not retrieval: answer time is set by Ollama
  (`OLLAMA_NUM_PARALLEL`, GPU). Retrieval plus embedding the question is ~50 ms
  on CPU.
- **Registry:** in memory per worker, reloaded on change; reads cost a `stat()`.
- **Workers:** 1–2 Uvicorn workers per host. History is in memory per process;
  move it to Redis before scaling out (hook in `chat_memory.get_message_history`).
- **Multiple hosts:** move the registry to Postgres (section 9) and Chroma to a
  Chroma server (`chromadb.HttpClient`) or another vector store; `index.py` is
  the only file that changes.
- **Ingest cost:** about 5–15 ms per chunk to embed on CPU; a full re-embed of
  100,000 chunks is tens of minutes, so routine loads rely on the content hash
  to skip unchanged guides.

## 12. Migration from per-tenant collections

The new code uses a new collection (`knowledge_chunks`) and a new registry file
(`document_registry.json`), so the old data stays untouched until it is removed
explicitly and rollback is a redeploy of the old code.

1. Deploy the new backend.
2. Start it. The guide loader re-embeds every guide into `knowledge_chunks`
   (the new registry has no hashes yet) before the API accepts requests.
3. Check: `GET /api/knowledge/documents` lists every guide; ask a question per
   screen.
4. Dry run: `python -m app.knowledge.migrate_legacy` lists `kb_common`,
   `kb_t_*` and the old `registry.json`.
5. Apply: `python -m app.knowledge.migrate_legacy --apply`. It refuses to run
   while `knowledge_chunks` is empty.

Done on the dev machine on 2026-10-06: 111 chunks moved, `kb_common` and the v1
registry removed, answers verified on the Details and Registration screens.
