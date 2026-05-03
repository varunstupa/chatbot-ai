"""Website crawl trigger and per-page ingestion endpoints."""

from __future__ import annotations

import asyncio
import os
import shutil
import subprocess
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.core import constants
from app.models.schemas import (
    CrawlRequest,
    CrawlResponse,
    IngestWebsiteRequest,
    IngestWebsiteResponse,
)
from app.services import ingestion
from app.utils.logger import get_logger

router = APIRouter(tags=["crawl"])
logger = get_logger(__name__)


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def _crawler_script() -> Path:
    return _project_root() / "crawler" / "crawler.js"


def _spawn_crawler_process(domain: str, max_pages: int | None) -> int:
    """Start Node Crawlee in the background. Returns child PID."""
    node = shutil.which("node")
    if not node:
        raise FileNotFoundError("node is not on PATH; install Node.js")
    script = _crawler_script()
    if not script.is_file():
        raise FileNotFoundError(f"Missing crawler script: {script}")

    env = {**os.environ}
    if max_pages is not None:
        env["MAX_PAGES"] = str(max_pages)

    proc = subprocess.Popen(
        [node, str(script), domain],
        cwd=str(script.parent),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    logger.info(
        "crawler_started pid=%s domain=%s max_pages=%s",
        proc.pid,
        domain,
        max_pages,
    )
    return proc.pid


@router.post("/ingest-website", response_model=IngestWebsiteResponse)
async def ingest_website(body: IngestWebsiteRequest) -> IngestWebsiteResponse:
    """Index one crawled page (chunk, embed, Chroma) with ``source`` = URL."""
    url = body.url.strip()
    content = body.content.strip()
    if not url or not content:
        raise HTTPException(
            status_code=400,
            detail="url and content required",
        )
    try:
        n = await asyncio.to_thread(ingestion.ingest_website_page, url, content)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.exception("ingest_website_failed url=%s", url)
        raise HTTPException(
            status_code=500,
            detail=str(e),
        ) from e
    return IngestWebsiteResponse(
        url=url,
        chunks_indexed=n,
        message=f"Indexed {n} chunk(s) from page",
    )


@router.post("/crawl", response_model=CrawlResponse)
async def start_crawl(body: CrawlRequest) -> CrawlResponse:
    """Fire-and-forget Node Crawlee worker for ``body.domain``."""
    try:
        pid = await asyncio.to_thread(
            _spawn_crawler_process,
            body.domain.strip(),
            body.max_pages,
        )
    except FileNotFoundError as e:
        logger.error("crawl_start_failed: %s", e)
        raise HTTPException(
            status_code=503,
            detail=str(e),
            headers={"X-Error-Code": constants.ERROR_CRAWL_START_FAILED},
        ) from e
    except Exception as e:
        logger.exception("crawl_start_failed")
        raise HTTPException(
            status_code=500,
            detail=str(e),
        ) from e
    return CrawlResponse(
        status="started",
        message="Crawler process started (check API and crawler logs)",
        pid=pid,
    )
