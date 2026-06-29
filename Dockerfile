# syntax=docker/dockerfile:1
#
# Backend image = FastAPI (Python) + Node.js crawler (Crawlee/Playwright) in ONE image.
# Why bundled: app/api/crawl.py launches the crawler with subprocess.Popen(["node", ...]),
# inheriting os.environ and cwd=/app/crawler. So `node`, the crawler's node_modules, and the
# Playwright Chromium browser must live in this image for POST /crawl to work. The subprocess
# posts pages to INGEST_URL (default http://localhost:8000/ingest-website) — i.e. back to this
# same container. ChromaDB is embedded (langchain-chroma); no separate DB container.

FROM python:3.13-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    APP_ENV=production \
    HF_HOME=/app/.cache/huggingface \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

WORKDIR /app

# --- System deps + Node.js 20 (NodeSource) ---
# build-essential + libgomp1 are needed by torch / sentence-transformers wheels.
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl ca-certificates gnupg build-essential libgomp1 \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# --- CPU-only PyTorch first ---
# Embeddings (all-mpnet-base-v2) run on CPU here, so avoid the multi-GB CUDA wheel.
# sentence-transformers (below) then sees torch already satisfied.
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# --- Python dependencies (cached layer) ---
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# --- Crawler dependencies + Playwright Chromium (+ its system libs via --with-deps) ---
COPY crawler/package.json crawler/package-lock.json ./crawler/
RUN cd crawler && npm ci
RUN cd crawler && npx playwright install --with-deps chromium \
    && rm -rf /var/lib/apt/lists/*

# --- Application source ---
COPY . .

# --- Non-root user ---
# Required for Playwright Chromium to launch without --no-sandbox (which would mean editing
# crawler.js). Also general best practice. Creating + chowning /app BEFORE the volumes mount
# means fresh named volumes (data/, cache) inherit appuser ownership and stay writable.
RUN useradd --create-home --uid 10001 appuser \
    && mkdir -p /app/data /app/.cache/huggingface /app/crawler/storage \
    && chown -R appuser:appuser /app /home/appuser
USER appuser

# --- Pre-bake the embedding model into the image (as appuser) ---
# Makes the first /query fast and the container self-contained (no runtime model download).
# Must match embedding.model_name in app/config/config.production.yaml.
RUN python -c "from langchain_community.embeddings import HuggingFaceEmbeddings; \
HuggingFaceEmbeddings(model_name='sentence-transformers/all-mpnet-base-v2')"

EXPOSE 8000

# Liveness: uses stdlib urllib (no curl dependency at runtime).
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Single Uvicorn worker: in-memory chat history + LLM/vector singletons are per-process.
# --proxy-headers/--forwarded-allow-ips so client IPs are correct behind a reverse proxy.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", \
     "--proxy-headers", "--forwarded-allow-ips=*"]
