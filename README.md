# RAG Backend

Production-style FastAPI service for document ingestion and retrieval-augmented Q&A. Configuration lives in `app/config/config.yaml`; secrets (e.g. `NVIDIA_API_KEY`) load from `.env` / the environment via Pydantic Settings.

## Stack (technologies & models)

| Piece | Role in this project |
|--------|----------------------|
| **LangChain** (`langchain`, `langchain-core`, `langchain-community`, `langchain-chroma`, `langchain-openai`, `langchain-text-splitters`) | `Document` types, text splitters, Chroma integration, chat models (Ollama / NVIDIA), prompts, `RunnableWithMessageHistory` for multi-turn RAG. |
| **Chroma** (`chromadb` + `langchain-chroma`) | Persistent vector DB: uploads collection + optional separate website crawl collection (`website_vector_store` in config). |
| **sentence-transformers** (via `HuggingFaceEmbeddings`) | Embedding model configured in `embedding.model_name` — indexes chunks and embeds queries for retrieval. |
| **Crawlee** + **Playwright** (Node, under `crawler/`) | Same-domain web crawl; extracts page text and POSTs to `POST /ingest-website`. See `CRAWLER.md`. |
| **FastAPI** / **Uvicorn** | HTTP API (`/upload`, `/query`, `/stupa-chat`, crawl hooks, etc.). |
| **MarkItDown** | Converts uploads (PDF, Office, …) to text before chunking. |
| **Ollama** (optional) | Local LLM host when `llm.provider` is `local` — model name from `llm.local_model_name`. |
| **NVIDIA NIM** (optional) | Remote chat when `llm.provider` is `nvidia` — model from `llm.model`. |

**ML models in `config.yaml` (typical):**

| Model id | Purpose |
|----------|---------|
| `sentence-transformers/all-mpnet-base-v2` | Embeddings for all Chroma ingestion and similarity search. |
| `llm.local_model_name` (e.g. `llama3.1:8b-instruct-q4_K_M`) | Chat model when using **local** / Ollama. |
| `llm.model` (e.g. NVIDIA Nemotron id) | Chat model when using **nvidia** provider. |

## Layout

- **API**: `app/api/routes.py` — `POST /upload`, `POST /query`, `GET /health`
- **Config**: `app/config/config.yaml` + validated `app/config/settings.py`
- **Pipeline**: MarkItDown → LangChain `Document` → chunk → `HuggingFaceEmbeddings` → Chroma (on disk) → LLM answer

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### NVIDIA API (default)

In `config.yaml`, `llm.provider` is `nvidia` with `model` and `base_url` for [NVIDIA NIM / integrate API](https://integrate.api.nvidia.com). Set the key in `.env`:

```bash
NVIDIA_API_KEY=nvapi-...
```

### Local LLM (Ollama)

Set `llm.provider` to `local` and align `llm.local_base_url` / `llm.local_model_name` with your Ollama instance.

## Run

From the project root (so `data/uploads` resolves correctly):

```bash
python -m app.main
```

Or with Uvicorn directly:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Host and port in `config.yaml` under `server` are used when you start via `python -m app.main`.

## Environment overrides

| Variable | Purpose |
|----------|---------|
| `CONFIG_FILE` | Absolute path to an alternate YAML file (full schema, same as `config.yaml`) |
| `APP_ENV` | If `development` or `production`, loads `config.development.yaml` or `config.production.yaml` from `app/config/` when that file exists; otherwise falls back to `config.yaml` |

## Optional config reload

After changing `config.yaml`, you can reset singletons and re-read the file from a shell or admin task:

```python
from app.bootstrap import reload_runtime_configuration
reload_runtime_configuration()
```

This clears the in-memory vector store; re-upload documents afterward.

## API examples

**Health**

```bash
curl http://127.0.0.1:8000/health
```

**Upload**

```bash
curl -X POST http://127.0.0.1:8000/upload -F "file=@./sample.pdf"
```

**Query**

```bash
curl -X POST http://127.0.0.1:8000/query -H "Content-Type: application/json" -d "{\"question\":\"What is this document about?\"}"
```

## Jira tickets (same chat API as RAG)

1. Copy `.env.example` to `.env` in the project root (same folder as `app/`).
2. Fill in Jira Cloud credentials (create an API token at
   https://id.atlassian.com/manage-profile/security/api-tokens):

```bash
JIRA_BASE_URL=https://your-company.atlassian.net
JIRA_EMAIL=you@company.com
JIRA_API_TOKEN=your-api-token
JIRA_PROJECT_KEY=PROJ
JIRA_ISSUE_TYPE=Bug
```

3. **Restart** the API after changing `.env` (values load at startup).

On startup you should see `jira ticket creation configured` in the logs.
If you see `jira not configured`, the `.env` file is missing or incomplete.

Tickets use the **same endpoints** as knowledge-base chat (`POST /query` or `POST /stupa-chat`), not a separate ticket API. Flow matches book-a-demo: send `session_id` on every turn.

**Start ticket wizard**

```bash
curl -X POST http://127.0.0.1:8000/api/stupa-chat \
  -H "Content-Type: application/json" \
  -d "{\"question\":\"report an issue\"}"
```

**Client-driven form (Angular owns the steps):** send the draft with **yes**:

```bash
curl -X POST http://127.0.0.1:8000/api/stupa-chat \
  -H "Content-Type: application/json" \
  -d "{\"question\":\"yes\",\"session_id\":\"<id>\",\"ticket_draft\":{\"title\":\"Login issue\",\"description\":\"Steps...\",\"expected_vs_actual\":\"Expected OK, got error\",\"attachments\":[{\"file_name\":\"a.png\",\"file_path\":\"/uploads/tickets/....png\"}]}}"
```

**Server-driven wizard** — follow-up turns (title, description, expected vs actual, then `done` or `skip` for attachments, then `yes` to create):

```bash
curl -X POST http://127.0.0.1:8000/api/stupa-chat \
  -H "Content-Type: application/json" \
  -d "{\"question\":\"Login fails on mobile\",\"session_id\":\"<from prior response>\"}"
```

**Upload attachment during wizard** (echo same `session_id` via query, header `X-Session-Id`, or cookie):

```bash
curl -X POST "http://127.0.0.1:8000/api/stupa-chat/attachment?session_id=<id>" \
  -F "file=@./screenshot.png"
```

JSON responses include `ticket_flow` and `ticket_workflow`; SSE streams emit `ticket_flow` / `ticket_workflow` events (like `demo_flow`).

## Edge cases

- Invalid or incomplete YAML: process fails at startup with a clear validation error.
- Empty upload or unreadable binary: `400` with a structured `detail` payload.
- Missing `NVIDIA_API_KEY` when `provider` is `nvidia`: `503` on `/query`.

## Admin-app chat (`/app-chat`)

Screen-aware assistant for the admin app. It is separate from `/stupa-chat` and `/query` and uses its own storage (`app_chat.persist_directory`).

- **Through the API gateway (production, `auth.mode: gateway`):** the frontend calls the gateway at `/chatbot/v1/app-chat` (streams when `Accept: text/event-stream`), `/chatbot/v1/app-chat/attachment` and `/chatbot/v1/knowledge/screen`. The gateway verifies the login token (`@auth_decorator`) and forwards to `/api/...` here with `X-Chat-Tenant`, `X-Chat-User`, `X-Chat-Role`, `X-Chat-Timestamp` and an HMAC-SHA256 `X-Chat-Signature` keyed with `CHATBOT_INTERNAL_SECRET` (same value on both sides; gateway also needs `CHATBOT_SERVICE_URL`). In this mode a login token sent directly is refused, so the chatbot must not be reachable except from the gateway.
- **Direct (local development, `auth.mode: jwt`):** every request needs the login JWT in the `auth` (or `Authorization`) header. The tenant is read from the verified token (`auth.tenant_claims`); a `tenant` header that disagrees is rejected. Nothing in the request body can set the tenant.
- **Storage:** every guide's chunks go into one Chroma collection (`knowledge_chunks`) with content-only metadata. Who may read each guide (`tenants`, `exclude_tenants`, `roles`) is kept per document in `document_registry.json`; a request queries only the doc_ids the caller may read and drops anything else. Changing only access updates the registry without re-embedding. Design and migration: `docs/knowledge-architecture.md`.
- **Screen routing:** the client sends `screen: { route, url }`. Each guide lists its `routes`; the current screen's guide is searched first, a guide named in the question wins, and other screens are used only when clearly closer (`app_chat.*_distance`).
- **Guides:** Markdown with front matter in `guides/` (how to write one: `guides/README.md`). They are loaded at every start; after editing one, restart the backend (run `python -m app.knowledge.guide_loader` by hand only while it is stopped). A deleted file removes its guide.

`.env`:

```bash
APP_CHAT_JWT_SECRET=...          # HS256 secret of the main API, or
APP_CHAT_JWT_PUBLIC_KEY=...      # PEM public key (set auth.jwt_algorithms to match)
KNOWLEDGE_SERVICE_KEY=...        # required by the guide listing and /upload
CHATBOT_INTERNAL_SECRET=...      # auth.mode: gateway; must equal the gateway's value
# Local development only, never in production: accept tokens without checking
# the signature and take the tenant from the `tenant` header if the token has none.
# APP_CHAT_ALLOW_UNVERIFIED_DEV_TOKENS=true
```

| Route | Auth | Purpose |
|-------|------|---------|
| `POST /api/app-chat`, `/api/app-chat/stream` | login JWT | Ask a question (JSON or SSE) |
| `POST /api/app-chat/attachment` | login JWT | Ticket attachment |
| `GET /api/knowledge/screen?route=` | login JWT | Screen title and suggested questions |
| `GET /api/knowledge/documents` | `X-Service-Key` | List loaded guides (read-only) |
| `POST /upload` | `X-Service-Key` | Existing upload route, now protected |

Tests: `python -m pytest tests/test_app_chat_isolation.py`.
