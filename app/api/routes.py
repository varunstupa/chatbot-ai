"""HTTP routes: upload, query, health."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from app.config.settings import get_settings
from app.api.dependencies import get_rag_pipeline
from app.core import constants
from app.models.schemas import (
    HealthResponse,
    QueryRequest,
    QueryResponse,
    RetrievedChunk,
    UploadResponse,
)
from app.services import ingestion
from app.services.rag_pipeline import RAGPipeline
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    s = get_settings()
    return HealthResponse(
        status=constants.HEALTH_OK,
        app_name=s.app.name,
        version=s.app.version,
    )


@router.post("/upload", response_model=UploadResponse)
async def upload(file: UploadFile = File(...)) -> UploadResponse:
    s = get_settings()
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail=s.messages.missing_filename,
        )
    raw = await file.read()
    if not raw:
        raise HTTPException(
            status_code=400,
            detail={
                "message": s.messages.upload_empty,
                "code": constants.ERROR_UPLOAD_EMPTY,
            },
        )

    def _run() -> tuple[Path, int]:
        path = ingestion.save_upload(file.filename, raw)
        count = ingestion.ingest_path(path)
        return path, count

    try:
        _, chunks = await asyncio.to_thread(_run)
    except ValueError as e:
        msg = str(e)
        code = constants.ERROR_UPLOAD_UNSUPPORTED
        if "Empty" in msg:
            code = constants.ERROR_UPLOAD_EMPTY
        logger.warning("upload_failed", extra={"error": msg, "code": code})
        raise HTTPException(status_code=400, detail={"message": msg, "code": code}) from e
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return UploadResponse(
        filename=file.filename,
        chunks_indexed=chunks,
        message=s.messages.upload_success,
    )


@router.post("/query", response_model=QueryResponse)
async def query(
    body: QueryRequest,
    pipeline: RAGPipeline = Depends(get_rag_pipeline),
) -> QueryResponse:
    s = get_settings()
    q = (body.question or "").strip()
    if not q:
        raise HTTPException(
            status_code=400,
            detail={
                "message": s.messages.query_empty,
                "code": constants.ERROR_QUERY_EMPTY,
            },
        )
    try:
        answer, sources = await pipeline.answer(q)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={"message": str(e), "code": constants.ERROR_QUERY_EMPTY},
        ) from e
    except RuntimeError as e:
        logger.error("llm_unavailable | %s", str(e))
        raise HTTPException(
            status_code=503,
            detail={
                "message": str(e),
                "code": constants.ERROR_LLM_UNAVAILABLE,
            },
        ) from e
    except Exception as e:
        logger.exception("query_failed", extra={"error": str(e)})
        raise HTTPException(
            status_code=500,
            detail=get_settings().messages.query_processing_failed,
        ) from e

    return QueryResponse(
        answer=answer,
        chunks=[RetrievedChunk(**s) for s in sources],
    )


@router.post("/query/stream")
async def query_stream(
    body: QueryRequest,
    pipeline: RAGPipeline = Depends(get_rag_pipeline),
) -> StreamingResponse:
    """Stream RAG answer as SSE: each event is ``data: <json>``.

    JSON object ``type`` is one of:
    ``sources`` (with ``chunks``), ``token`` (with ``text``), ``done``,
    or ``error`` (with ``message``).
    """
    s = get_settings()
    q = (body.question or "").strip()
    if not q:
        raise HTTPException(
            status_code=400,
            detail={
                "message": s.messages.query_empty,
                "code": constants.ERROR_QUERY_EMPTY,
            },
        )

    async def sse_events():
        try:
            async for item in pipeline.stream(q):
                line = json.dumps(item, ensure_ascii=False)
                yield f"data: {line}\n\n"
        except ValueError as e:
            payload = json.dumps(
                {"type": "error", "message": str(e)},
                ensure_ascii=False,
            )
            yield f"data: {payload}\n\n"
        except RuntimeError as e:
            logger.error("llm_unavailable_stream | %s", str(e))
            payload = json.dumps(
                {"type": "error", "message": str(e)},
                ensure_ascii=False,
            )
            yield f"data: {payload}\n\n"
        except Exception:
            logger.exception("query_stream_failed")
            payload = json.dumps(
                {
                    "type": "error",
                    "message": s.messages.query_processing_failed,
                },
                ensure_ascii=False,
            )
            yield f"data: {payload}\n\n"

    return StreamingResponse(
        sse_events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
