# RAG Backend

Production-style FastAPI service for document ingestion and retrieval-augmented Q&A. Configuration lives in `app/config/config.yaml`; secrets (e.g. `NVIDIA_API_KEY`) load from `.env` / the environment via Pydantic Settings.

## Layout

- **API**: `app/api/routes.py` — `POST /upload`, `POST /query`, `GET /health`
- **Config**: `app/config/config.yaml` + validated `app/config/settings.py`
- **Pipeline**: MarkItDown → LangChain `Document` → chunk → `HuggingFaceEmbeddings` → in-memory Chroma → LLM answer

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

## Edge cases

- Invalid or incomplete YAML: process fails at startup with a clear validation error.
- Empty upload or unreadable binary: `400` with a structured `detail` payload.
- Missing `NVIDIA_API_KEY` when `provider` is `nvidia`: `503` on `/query`.
