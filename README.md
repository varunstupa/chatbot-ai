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
| `llm.local_model_name` (e.g. `llama3.2:3b-instruct-q4_K_M`) | Chat model when using **local** / Ollama. |
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
