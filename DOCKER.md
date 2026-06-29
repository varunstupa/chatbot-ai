# Docker Deployment Guide

Full containerized deployment of the Stupa RAG chatbot: FastAPI API, embedded ChromaDB,
the Node/Playwright website crawler, and a local Ollama LLM.

---

## 1. What runs where (container map)

| # | Container | Image | Role | Lifetime |
|---|-----------|-------|------|----------|
| 1 | `stupa-ollama` | `ollama/ollama` | Serves the LLM (`llama3.2:3b-instruct-q4_K_M`) on port 11434 | long-running |
| 2 | `stupa-ollama-pull` | `ollama/ollama` | Pulls the model into Ollama, then **exits 0** | one-shot |
| 3 | `stupa-backend` | built from `Dockerfile` | FastAPI API on port 8000 **+ bundled crawler** | long-running |

**Steady state = 2 running containers** (`stupa-ollama` + `stupa-backend`).
`stupa-ollama-pull` runs once at startup and stops.

### Why not more containers?

- **ChromaDB is embedded**, not a server. `langchain-chroma` opens the DB in-process inside
  `backend` and persists files to the `app-data` volume. No separate DB container needed.
- **The crawler is bundled into `backend`**, not its own service. `app/api/crawl.py` launches
  it with `subprocess.Popen(["node", "crawler/crawler.js", ...])`, so Node.js + the Playwright
  Chromium browser must live in the same container as the API. `POST /crawl` works out of the box.

---

## 2. Prerequisites

- Docker Engine 24+ and Docker Compose v2 (`docker compose`, not `docker-compose`).
- **Disk:** ~7 GB (backend image ~2.5 GB incl. baked embedding model, Ollama image ~1.5 GB,
  model weights ~2 GB).
- **RAM:** ~8 GB recommended (Ollama 3B model ~4 GB + backend/embeddings ~1.5 GB).
- (Optional) NVIDIA GPU + [nvidia-container-toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
  for fast inference. **CPU-only works without any of this.**

### Build optimizations already applied

- **CPU-only PyTorch** — skips the multi-GB CUDA wheel (embeddings run on CPU).
- **Embedding model pre-baked** into the image — first `/query` is instant and the container
  needs no internet at runtime to embed.
- **Non-root user** (`appuser`) — security best practice *and* what lets the Playwright
  Chromium crawler run without a `--no-sandbox` code change.
- **Healthcheck** built into the image (`/health`).

---

## 3. Deploy (one command, nothing manual)

```bash
docker compose up -d --build
```

That's it. This single command:

1. Builds the backend image (Python deps, Node + Playwright Chromium, **embedding model baked in**).
2. Starts Ollama and **auto-pulls the model** (`ollama-pull`, runs once).
3. Starts the backend only **after** the model is ready (`depends_on` ordering).
4. Creates all data volumes and directories automatically.

No model downloads, no `ollama pull`, no DB setup, no folder creation by hand.

Watch it come up (first model pull takes a few minutes):

```bash
docker compose logs -f
```

### Vector DBs are built automatically on first run

The Chroma databases are **not** in git (they're generated data). The container builds them
itself on first boot, via `docker/entrypoint.sh` — no manual crawl/upload needed:

1. **Uploads corpus** — ingests every file in `data/uploads/` (the bundled `.docx` docs) into
   `data/chroma`.
2. **Website corpus** — crawls `SEED_CRAWL_DOMAIN` (default `stupasports.ai`) in the background
   once the API is up, populating `data/chroma_website`.

Both are guarded by marker files (`.seeded_docs`, `.seeded_web`) in the `app-data` volume, so
**restarts never re-ingest or re-crawl**. Controls (in `docker-compose.yml`):

- `SEED_ON_START=0` — disable all auto-seeding.
- `SEED_CRAWL_DOMAIN=""` — keep doc ingestion but skip the website crawl.
- `SEED_CRAWL_DOMAIN=example.com` — crawl a different site.

To force a fresh rebuild of the DBs: `docker compose down -v` (wipes the volume) then
`docker compose up -d` re-seeds from scratch.

### `.env` is optional

The stack boots **with no `.env` file**. You only need one to turn on **Jira ticketing**
(or to use the NVIDIA cloud LLM instead of Ollama). Without it, the chatbot, RAG, demo
booking, and crawler all work; the ticket wizard just replies "not configured". To enable
Jira: `cp .env.example .env`, fill in the values, then `docker compose up -d`.

Verify:

```bash
curl http://localhost:8000/health
# {"status":"healthy","app_name":"RAG Backend","version":"1.0"}
```

Interactive API docs: <http://localhost:8000/docs>

---

## 4. How the Ollama LLM is deployed

1. The `ollama` service uses the official `ollama/ollama` image, which runs `ollama serve`.
   Pulled models persist in the **`ollama-models`** volume (`/root/.ollama`) — pulled once,
   reused across restarts.
2. The `ollama-pull` one-shot container waits until Ollama is healthy, then runs
   `ollama pull llama3.2:3b-instruct-q4_K_M` against it and exits.
3. The `backend` connects to it at **`http://ollama:11434`** (the compose service name),
   configured in `app/config/config.production.yaml` → `llm.local_base_url`.

### Changing the model

Two places must agree:

```bash
# .env  (drives the ollama-pull container)
OLLAMA_MODEL=llama3.1:8b
```
```yaml
# app/config/config.production.yaml  (drives the backend)
llm:
  local_model_name: "llama3.1:8b"
```
Then `docker compose up -d --build backend ollama-pull`.

### Enabling GPU

Uncomment the `gpus: all` (or the `deploy.resources` block) under the `ollama` service in
`docker-compose.yml`, then `docker compose up -d ollama`.

### Using NVIDIA cloud LLM instead of Ollama

Set `llm.provider: "nvidia"` in `config.production.yaml`, put `NVIDIA_API_KEY=...` in `.env`,
and you can drop the `ollama` / `ollama-pull` services.

---

## 5. Data & persistence (volumes)

| Volume | Mount | Contents |
|--------|-------|----------|
| `app-data` | `/app/data` | Chroma stores (`chroma`, `chroma_website`), uploads, ticket/demo session JSON, attachments |
| `hf-cache` | `/app/.cache/huggingface` | Embedding model `all-mpnet-base-v2` (~420 MB), cached so it isn't re-downloaded |
| `ollama-models` | `/root/.ollama` | Pulled LLM weights |

`docker compose down` keeps volumes. `docker compose down -v` **deletes all data** (vector
index, sessions, models).

---

## 6. Common operations

```bash
# Crawl a site into the website corpus (runs inside the backend container)
curl -X POST http://localhost:8000/crawl \
  -H "Content-Type: application/json" \
  -d '{"domain":"stupasports.ai","max_pages":100}'

# Upload a document to the uploads corpus
curl -X POST http://localhost:8000/upload -F "file=@./mydoc.pdf"

# Ask a question
curl -X POST http://localhost:8000/stupa-chat \
  -H "Content-Type: application/json" \
  -d '{"question":"What does Stupa offer?"}'

# Rebuild after code changes
docker compose up -d --build backend

# Tail logs / shell in
docker compose logs -f backend
docker compose exec backend bash
```

---

## 7. The one thing to know before a browser frontend connects (CORS)

`app/main.py` hardcodes the allowed CORS origins to `localhost:4200/3000`. This is the **only**
deployment concern not covered by config/env. It matters **only for browsers calling the API
from a different origin**. Two zero-code-change ways to handle it:

- **Recommended:** put a reverse proxy in front and serve the frontend and the API on the
  **same origin** (e.g. site at `https://app.example.com`, API proxied under
  `https://app.example.com/api/...` — the app already mirrors every route under `/api`).
  Same origin → no CORS preflight → nothing to change.
- Server-to-server callers, curl, mobile apps, and SSE clients are unaffected by CORS.

(If you must allow a *different* browser origin directly, that single list in `main.py` is the
one line you'd touch.)

## 8. Production notes

- **Single worker per backend container.** Chat history (`chat_memory.py`) and the LLM/vector
  singletons are in-process. To scale horizontally, either run replicas behind a load balancer
  with **sticky sessions** (the `X-Session-Id` cookie/header), or first move `chat_memory.py`
  to Redis (its docstring already anticipates this) and make the Chroma volume shared/external.
- **Logs** are JSON in production (`logging.json_format: true` in `config.production.yaml`) —
  friendly for log shippers.
- **Secrets** come only from `.env` at runtime; `.dockerignore` keeps `.env` out of the image.
- The crawler runs **inside** the backend container (Node + Playwright Chromium are baked in,
  non-root); `POST /crawl` works with no extra setup.
- Put a TLS-terminating reverse proxy (nginx/Caddy/Traefik) in front of `:8000` for public use.
