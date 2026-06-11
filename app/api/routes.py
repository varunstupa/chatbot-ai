"""HTTP routes: upload, query, health."""

from __future__ import annotations

import asyncio
import json
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, Response, UploadFile
from fastapi.responses import StreamingResponse

from app.config.settings import get_settings
from app.api.dependencies import get_rag_pipeline
from app.core import constants
from app.models.schemas import (
    DemoFlowState,
    HealthResponse,
    QueryRequest,
    QueryResponse,
    RetrievedChunk,
    UploadResponse,
)
from app.models.ticket_schemas import (
    TicketAttachmentUploadResponse,
    TicketFlowState,
)
from app.services import demo_booking, ingestion, ticket_workflow
from app.services.rag_pipeline import RAGPipeline
from app.services.ticket_upload import save_ticket_file
from app.services.vector_store import CorpusMode
from app.utils.debug_console import debug_log
from app.utils.logger import get_logger
from app.utils.rate_limit import check_rate_limit

router = APIRouter()
logger = get_logger(__name__)


def _resolve_session_id(body_session_id: str | None, request: Request) -> str:
    """Prefer body, then ``X-Session-Id`` header, then ``session_id`` cookie.

    New UUID only when all are absent so multi-turn clients stay on one thread.
    """
    header = request.headers.get("x-session-id") or request.headers.get("X-Session-Id")
    cookie = request.cookies.get("session_id")
    for raw in (body_session_id, header, cookie):
        t = (raw or "").strip()
        if t:
            return t
    new_id = str(uuid.uuid4())
    logger.info(
        "chat_memory | new session %s (no session in body/header/cookie); "
        "client must echo id on the next request for multi-turn memory",
        new_id,
    )
    return new_id


def _client_key(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


def _query_response_from_ticket(
    session_id: str,
    ticket: ticket_workflow.TicketTurnResult,
    response: Response,
) -> QueryResponse:
    _attach_session(response, session_id)
    return QueryResponse(
        answer=ticket.answer,
        chunks=[],
        session_id=session_id,
        ticket_flow=TicketFlowState(**ticket.flow.as_dict()),
        ticket_workflow=ticket.workflow,
    )


async def _save_ticket_attachment(
    request: Request,
    file: UploadFile,
    session_id: str,
) -> TicketAttachmentUploadResponse:
    try:
        check_rate_limit(
            f"ticket-upload:{_client_key(request)}",
            max_calls=20,
            window_seconds=60,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=429,
            detail={"message": str(e), "code": constants.ERROR_RATE_LIMIT},
        ) from e

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail={
                "message": get_settings().messages.missing_filename,
                "code": constants.ERROR_UPLOAD_EMPTY,
            },
        )
    raw = await file.read()
    try:

        def _run() -> tuple[str, str]:
            return save_ticket_file(file.filename or "file", raw)

        stored_name, rel_path = await asyncio.to_thread(_run)
    except ValueError as e:
        logger.warning("ticket_attachment_validation | %s", e)
        raise HTTPException(
            status_code=400,
            detail={"message": str(e), "code": constants.ERROR_UPLOAD_UNSUPPORTED},
        ) from e

    ticket_workflow.register_session_attachment(
        session_id,
        stored_name,
        rel_path,
    )
    return TicketAttachmentUploadResponse(
        file_name=stored_name,
        file_path=rel_path,
        size_bytes=len(raw),
        content_type=file.content_type,
        session_id=session_id,
    )


def _attach_session(response: Response, session_id: str) -> None:
    response.headers["X-Session-Id"] = session_id
    response.set_cookie(
        key="session_id",
        value=session_id,
        max_age=604800,
        path="/",
        httponly=True,
        samesite="lax",
    )


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


async def run_stupa_query(
    body: QueryRequest,
    request: Request,
    response: Response,
    pipeline: RAGPipeline,
) -> QueryResponse:
    """RAG plus book-a-demo wizard when message matches demo intent or session."""
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
    session_id = _resolve_session_id(body.session_id, request)
    ticket = ticket_workflow.try_process(
        session_id,
        q,
        ticket_draft=body.ticket_draft,
    )
    if ticket is not None:
        debug_log(
            "stupa JSON → ticket",
            ticket.flow.phase,
            ticket.flow.step,
        )
        return _query_response_from_ticket(session_id, ticket, response)
    demo = demo_booking.try_process(session_id, q)
    if demo is not None:
        debug_log("stupa JSON → demo", demo.flow.phase, demo.flow.step)
        _attach_session(response, session_id)
        return QueryResponse(
            answer=demo.answer,
            chunks=[],
            session_id=session_id,
            demo_flow=DemoFlowState(**demo.flow.as_dict()),
        )
    rag_corpus = s.stupa_chat.rag_corpus
    rag = await run_query(
        body,
        request,
        response,
        pipeline,
        corpus=rag_corpus,
        prompt_template=s.stupa_chat.prompt_template,
    )
    debug_log("stupa JSON → rag", "chunks=", len(rag.chunks))
    return rag


async def run_query(
    body: QueryRequest,
    request: Request,
    response: Response,
    pipeline: RAGPipeline,
    *,
    corpus: CorpusMode = "merged",
    prompt_template: str | None = None,
) -> QueryResponse:
    """Shared non-streaming RAG (``/query`` merged + default prompt; stupa overrides)."""
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
    session_id = _resolve_session_id(body.session_id, request)
    ticket = ticket_workflow.try_process(
        session_id,
        q,
        ticket_draft=body.ticket_draft,
    )
    if ticket is not None:
        debug_log(
            "query JSON → ticket",
            ticket.flow.phase,
            ticket.flow.step,
        )
        return _query_response_from_ticket(session_id, ticket, response)
    try:
        answer, sources = await pipeline.answer(
            q,
            session_id,
            corpus,
            prompt_template=prompt_template,
        )
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

    _attach_session(response, session_id)
    return QueryResponse(
        answer=answer,
        chunks=[RetrievedChunk(**s) for s in sources],
        session_id=session_id,
    )


def build_query_stream_response(
    body: QueryRequest,
    request: Request,
    pipeline: RAGPipeline,
) -> StreamingResponse:
    """Shared SSE RAG stream (used by ``/query/stream`` and ``/stupa-chat/stream``)."""
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

    session_id = _resolve_session_id(body.session_id, request)

    async def sse_events():
        ticket = ticket_workflow.try_process(
            session_id,
            q,
            ticket_draft=body.ticket_draft,
        )
        if ticket is not None:
            debug_log(
                "query SSE → ticket",
                ticket.flow.phase,
                ticket.flow.step,
            )
            try:
                for line in _ticket_sse_lines(session_id, ticket):
                    yield line
            except Exception:
                logger.exception("query_ticket_stream_failed")
                err = json.dumps(
                    {
                        "type": "error",
                        "message": s.messages.query_processing_failed,
                    },
                    ensure_ascii=False,
                )
                yield f"data: {err}\n\n"
            return
        try:
            async for item in pipeline.stream(q, session_id):
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

    stream = StreamingResponse(
        sse_events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "X-Session-Id": session_id,
        },
    )
    _attach_session(stream, session_id)
    return stream


def _ticket_sse_lines(
    session_id: str,
    ticket: ticket_workflow.TicketTurnResult,
) -> list[str]:
    lines = [
        json.dumps({"type": "session", "session_id": session_id}, ensure_ascii=False),
        json.dumps({"type": "sources", "chunks": []}, ensure_ascii=False),
        json.dumps(
            {"type": "ticket_flow", "session_id": session_id, **ticket.flow.as_dict()},
            ensure_ascii=False,
        ),
        json.dumps(
            {"type": "ticket_workflow", **ticket.workflow.model_dump()},
            ensure_ascii=False,
        ),
        json.dumps({"type": "token", "text": ticket.answer}, ensure_ascii=False),
        json.dumps({"type": "done"}, ensure_ascii=False),
    ]
    return [f"data: {line}\n\n" for line in lines]


def build_stupa_stream_response(
    body: QueryRequest,
    request: Request,
    pipeline: RAGPipeline,
) -> StreamingResponse:
    """SSE for stupa-chat: demo wizard events + standard RAG stream."""
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
    session_id = _resolve_session_id(body.session_id, request)

    async def sse_events():
        ticket = ticket_workflow.try_process(
            session_id,
            q,
            ticket_draft=body.ticket_draft,
        )
        if ticket is not None:
            debug_log(
                "stupa SSE → ticket",
                ticket.flow.phase,
                ticket.flow.step,
            )
            try:
                for line in _ticket_sse_lines(session_id, ticket):
                    yield line
            except Exception:
                logger.exception("stupa_ticket_stream_failed")
                err = json.dumps(
                    {
                        "type": "error",
                        "message": s.messages.query_processing_failed,
                    },
                    ensure_ascii=False,
                )
                yield f"data: {err}\n\n"
            return
        demo = demo_booking.try_process(session_id, q)
        if demo is not None:
            debug_log("stupa SSE → demo", demo.flow.phase, demo.flow.step)
            try:
                sid_line = json.dumps(
                    {"type": "session", "session_id": session_id},
                    ensure_ascii=False,
                )
                yield f"data: {sid_line}\n\n"
                src_line = json.dumps({"type": "sources", "chunks": []}, ensure_ascii=False)
                yield f"data: {src_line}\n\n"
                df = {
                    "type": "demo_flow",
                    "session_id": session_id,
                    **demo.flow.as_dict(),
                }
                yield f"data: {json.dumps(df, ensure_ascii=False)}\n\n"
                tok = json.dumps({"type": "token", "text": demo.answer}, ensure_ascii=False)
                yield f"data: {tok}\n\n"
                dn = json.dumps({"type": "done"}, ensure_ascii=False)
                yield f"data: {dn}\n\n"
            except Exception:
                logger.exception("stupa_demo_stream_failed")
                err = json.dumps(
                    {"type": "error", "message": s.messages.query_processing_failed},
                    ensure_ascii=False,
                )
                yield f"data: {err}\n\n"
            return
        debug_log("stupa SSE → rag", s.stupa_chat.rag_corpus)
        rag_corpus = s.stupa_chat.rag_corpus
        try:
            async for item in pipeline.stream(
                q,
                session_id,
                rag_corpus,
                prompt_template=s.stupa_chat.prompt_template,
            ):
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

    stream = StreamingResponse(
        sse_events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "X-Session-Id": session_id,
        },
    )
    _attach_session(stream, session_id)
    return stream


@router.post("/query", response_model=QueryResponse)
async def query(
    body: QueryRequest,
    request: Request,
    response: Response,
    pipeline: RAGPipeline = Depends(get_rag_pipeline),
) -> QueryResponse:
    return await run_query(body, request, response, pipeline)


@router.post("/query/stream")
async def query_stream(
    body: QueryRequest,
    request: Request,
    pipeline: RAGPipeline = Depends(get_rag_pipeline),
) -> StreamingResponse:
    """Stream RAG answer as SSE: each event is ``data: <json>``.

    JSON object ``type`` is one of:
    ``session`` (with ``session_id`` — send back on the next request),
    ``sources`` (with ``chunks``), ``ticket_flow``, ``ticket_workflow``,
    ``token`` (with ``text``), ``done``, or ``error`` (with ``message``).
    """
    return build_query_stream_response(body, request, pipeline)


@router.post(
    "/stupa-chat",
    tags=["stupa-chat"],
    summary="Stupa chat",
    description=(
        "Returns **JSON** by default (waits for full answer). "
        "For **incremental SSE** (same as `/stupa-chat/stream`), send "
        "`stream=true` query param and/or header `Accept: text/event-stream`. "
        "**Book a demo:** say e.g. \"book a demo\" to start the wizard; "
        "send **`session_id` from the response** on every next turn. "
        "`demo_flow` in the JSON (or SSE `demo_flow` event) carries "
        "`interest_options` and `slots` for UI chips. "
        "**Jira tickets:** say e.g. \"report an issue\" on this same endpoint, "
        "or send `ticket_draft` with question **yes** when the UI owns the "
        "form. Use `POST /stupa-chat/attachment` for files. "
        "`ticket_flow` / `ticket_workflow` mirror `demo_flow`. "
        "**RAG context** comes from `stupa_chat.rag_corpus` in config "
        "(default **website** = crawled pages only; `/query` still uses "
        "uploads + website merged). Stupa uses `stupa_chat.prompt_template` "
        "(strict: no evidence → **I don't know**; empty retrieval skips the LLM)."
    ),
    response_model=None,
)
@router.post(
    "/stupa-chat/",
    tags=["stupa-chat"],
    include_in_schema=False,
    response_model=None,
)
async def stupa_chat(
    body: QueryRequest,
    request: Request,
    response: Response,
    pipeline: RAGPipeline = Depends(get_rag_pipeline),
    stream: bool = Query(
        False,
        description="SSE stream (tokens as sent); same format as /stupa-chat/stream.",
    ),
) -> QueryResponse | StreamingResponse:
    accept = (request.headers.get("accept") or "").lower()
    if stream or "text/event-stream" in accept:
        return build_stupa_stream_response(body, request, pipeline)
    return await run_stupa_query(body, request, response, pipeline)


@router.post(
    "/stupa-chat/stream",
    tags=["stupa-chat"],
    summary="Stupa chat (SSE stream)",
)
@router.post(
    "/stupa-chat/stream/",
    tags=["stupa-chat"],
    include_in_schema=False,
)
async def stupa_chat_stream(
    body: QueryRequest,
    request: Request,
    pipeline: RAGPipeline = Depends(get_rag_pipeline),
) -> StreamingResponse:
    return build_stupa_stream_response(body, request, pipeline)


async def _chat_attachment(
    request: Request,
    response: Response,
    file: UploadFile,
    body_session_id: str | None,
) -> TicketAttachmentUploadResponse:
    session_id = _resolve_session_id(body_session_id, request)
    result = await _save_ticket_attachment(request, file, session_id)
    _attach_session(response, session_id)
    return result


@router.post(
    "/query/attachment",
    tags=["query"],
    response_model=TicketAttachmentUploadResponse,
    summary="Upload file during ticket wizard (requires active session)",
)
@router.post(
    "/query/attachment/",
    tags=["query"],
    include_in_schema=False,
    response_model=TicketAttachmentUploadResponse,
)
async def query_ticket_attachment(
    request: Request,
    response: Response,
    file: UploadFile = File(...),
    session_id: str | None = Query(
        default=None,
        description="Chat session id (body field on /query also accepted via cookie/header)",
    ),
) -> TicketAttachmentUploadResponse:
    return await _chat_attachment(request, response, file, session_id)


@router.post(
    "/stupa-chat/attachment",
    tags=["stupa-chat"],
    response_model=TicketAttachmentUploadResponse,
    summary="Upload file during ticket wizard on stupa-chat",
)
@router.post(
    "/stupa-chat/attachment/",
    tags=["stupa-chat"],
    include_in_schema=False,
    response_model=TicketAttachmentUploadResponse,
)
async def stupa_chat_attachment(
    request: Request,
    response: Response,
    file: UploadFile = File(...),
    session_id: str | None = Query(default=None),
) -> TicketAttachmentUploadResponse:
    return await _chat_attachment(request, response, file, session_id)
