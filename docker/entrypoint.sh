#!/bin/sh
# Container entrypoint: one-time DB seeding, then start the API.
#
# 1. Ingest bundled documents (data/uploads) into the uploads corpus — before serving.
# 2. Crawl SEED_CRAWL_DOMAIN into the website corpus — in the background, after the API is up.
# Both are guarded by marker files in the data volume so restarts never repeat them.
# Disable everything with SEED_ON_START=0. Skip only the crawl by leaving SEED_CRAWL_DOMAIN empty.
set -u

DATA_DIR="/app/data"
DOCS_MARKER="$DATA_DIR/.seeded_docs"
WEB_MARKER="$DATA_DIR/.seeded_web"
SEED_ON_START="${SEED_ON_START:-1}"
SEED_CRAWL_DOMAIN="${SEED_CRAWL_DOMAIN:-}"

mkdir -p "$DATA_DIR" 2>/dev/null || true

if [ "$SEED_ON_START" = "1" ]; then
  # (1) Documents → uploads corpus (synchronous, one time).
  if [ ! -f "$DOCS_MARKER" ]; then
    echo "[seed] ingesting bundled documents into the uploads corpus..."
    if python /app/docker/seed_docs.py; then
      touch "$DOCS_MARKER" 2>/dev/null || true
    else
      echo "[seed] document ingest errored — will retry on next start"
    fi
  fi

  # (2) Website → website corpus (background, one time, after the API answers /health).
  if [ -n "$SEED_CRAWL_DOMAIN" ] && [ ! -f "$WEB_MARKER" ]; then
    (
      echo "[seed] will crawl '$SEED_CRAWL_DOMAIN' once the API is ready..."
      i=0
      while [ "$i" -lt 90 ]; do
        if python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" 2>/dev/null; then
          echo "[seed] API ready — crawling '$SEED_CRAWL_DOMAIN' (website corpus)"
          if (cd /app/crawler && node crawler.js "$SEED_CRAWL_DOMAIN"); then
            touch "$WEB_MARKER" 2>/dev/null || true
            echo "[seed] website crawl complete"
          else
            echo "[seed] website crawl errored — will retry on next start"
          fi
          break
        fi
        i=$((i + 1))
        sleep 2
      done
    ) &
  fi
fi

# Hand off to the API server (PID 1).
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips=*
