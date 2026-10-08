"""Admin-app chat (JWT, tenant-scoped, screen-aware) and guide management routes."""

from __future__ import annotations

import asyncio
import json
import re
import uuid

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Query,
    Request,
    Response,
    UploadFile,
)
from fastapi.responses import StreamingResponse

from app.api.dependencies import get_rag_pipeline
from app.api.routes import (
    _attach_session,
    _query_response_from_ticket,
    _save_ticket_attachment,
    _ticket_sse_lines,
)
from app.config.settings import get_settings
from app.core import constants
from app.models.schemas import QueryRequest, QueryResponse, RetrievedChunk
from app.models.ticket_schemas import TicketAttachmentUploadResponse
from app.knowledge import service as knowledge
from app.services import app_chat, ticket_workflow
from app.services.auth import CallerScope, require_scope, require_service_key
from app.services.chat_memory import get_message_history
from app.services.rag_pipeline import RAGPipeline
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

_SESSION_RE = re.compile(r"^[A-Za-z0-9_-]{8,64}$")


def _client_session_id(body_session_id: str | None, request: Request) -> str:
    """Session id as the browser knows it. Anything malformed starts a new one."""
    header = request.headers.get("x-session-id")
    for raw in (body_session_id, header):
        t = (raw or "").strip()
        if _SESSION_RE.match(t):
            return t
    return str(uuid.uuid4())


def _scoped_session_id(scope: CallerScope, session_id: str) -> str:
    """History/ticket key. Bound to tenant and user so an id cannot be replayed."""
    key = f"{scope.tenant}--{scope.user_id}--{session_id}"
    history = get_message_history(key)
    if hasattr(history, "max_messages"):
        history.max_messages = get_settings().app_chat.history_messages
    return key


def _question(body: QueryRequest) -> str:
    q = (body.question or "").strip()
    if not q:
        s = get_settings()
        raise HTTPException(
            status_code=400,
            detail={"message": s.messages.query_empty, "code": constants.ERROR_QUERY_EMPTY},
        )
    return q


def _retriever(scope: CallerScope, body: QueryRequest, holder: dict):
    route = body.screen.route if body.screen else None
    url = body.screen.url if body.screen else None

    def run(question: str) -> tuple[str, list[dict]]:
        result = app_chat.retrieve(scope, question, route, url)
        app_chat.audit(scope, route, result)
        holder["result"] = result
        return result.context, result.sources

    return run


def _screen_title(scope: CallerScope, body: QueryRequest) -> str:
    if not body.screen:
        return ""
    info = knowledge.screen_info(scope, body.screen.route, body.screen.url)
    return (info or {}).get("title", "")


async def _answer_json(
    body: QueryRequest,
    request: Request,
    response: Response,
    pipeline: RAGPipeline,
    scope: CallerScope,
) -> QueryResponse:
    q = _question(body)
    session_id = _client_session_id(body.session_id, request)
    scoped = _scoped_session_id(scope, session_id)

    ticket = ticket_workflow.try_process(scoped, q, ticket_draft=body.ticket_draft)
    if ticket is not None:
        return _query_response_from_ticket(session_id, ticket, response)

    s = get_settings()
    try:
        answer, sources = await pipeline.answer(
            q,
            scoped,
            prompt_template=app_chat.prompt_for(_screen_title(scope, body)),
            retriever=_retriever(scope, body, {}),
            no_answer_text=s.app_chat.no_answer_message,
        )
    except RuntimeError as e:
        logger.error("llm_unavailable | %s", str(e))
        raise HTTPException(
            status_code=503,
            detail={"message": str(e), "code": constants.ERROR_LLM_UNAVAILABLE},
        ) from e
    except Exception as e:
        logger.exception("app_chat_failed")
        raise HTTPException(status_code=500, detail=s.messages.query_processing_failed) from e

    _attach_session(response, session_id)
    return QueryResponse(
        answer=answer,
        chunks=[RetrievedChunk(**src) for src in sources],
        session_id=session_id,
    )


def _answer_stream(
    body: QueryRequest,
    request: Request,
    pipeline: RAGPipeline,
    scope: CallerScope,
) -> StreamingResponse:
    q = _question(body)
    session_id = _client_session_id(body.session_id, request)
    scoped = _scoped_session_id(scope, session_id)
    s = get_settings()

    def _line(obj: dict) -> str:
        return f"data: {json.dumps(obj, ensure_ascii=False)}\n\n"

    async def sse_events():
        try:
            ticket = ticket_workflow.try_process(scoped, q, ticket_draft=body.ticket_draft)
            if ticket is not None:
                for line in _ticket_sse_lines(session_id, ticket):
                    yield line
                return
            async for item in pipeline.stream(
                q,
                scoped,
                prompt_template=app_chat.prompt_for(_screen_title(scope, body)),
                retriever=_retriever(scope, body, {}),
                no_answer_text=s.app_chat.no_answer_message,
            ):
                if item.get("type") == "session":
                    # Never hand the tenant-scoped history key to the browser.
                    item = {"type": "session", "session_id": session_id}
                elif item.get("type") == "error":
                    # Model/server details stay in the log, not in the browser.
                    logger.error("app_chat_llm_error | %s", item.get("message"))
                    item = {"type": "error", "message": s.messages.query_processing_failed}
                yield _line(item)
        except Exception:
            logger.exception("app_chat_stream_failed")
            yield _line({"type": "error", "message": s.messages.query_processing_failed})

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
    return stream


@router.post("/app-chat", tags=["app-chat"], response_model=None)
async def app_chat_query(
    body: QueryRequest,
    request: Request,
    response: Response,
    pipeline: RAGPipeline = Depends(get_rag_pipeline),
    scope: CallerScope = Depends(require_scope),
    stream: bool = Query(False, description="SSE stream instead of JSON."),
) -> QueryResponse | StreamingResponse:
    """Answer from the guides the caller's tenant may read, current screen first."""
    accept = (request.headers.get("accept") or "").lower()
    if stream or accept.startswith("text/event-stream"):
        return _answer_stream(body, request, pipeline, scope)
    return await _answer_json(body, request, response, pipeline, scope)


@router.post("/app-chat/stream", tags=["app-chat"])
async def app_chat_stream(
    body: QueryRequest,
    request: Request,
    pipeline: RAGPipeline = Depends(get_rag_pipeline),
    scope: CallerScope = Depends(require_scope),
) -> StreamingResponse:
    return _answer_stream(body, request, pipeline, scope)


@router.post(
    "/app-chat/attachment",
    tags=["app-chat"],
    response_model=TicketAttachmentUploadResponse,
)
async def app_chat_attachment(
    request: Request,
    response: Response,
    file: UploadFile = File(...),
    session_id: str | None = Query(default=None),
    scope: CallerScope = Depends(require_scope),
) -> TicketAttachmentUploadResponse:
    client_sid = _client_session_id(session_id, request)
    result = await _save_ticket_attachment(
        request,
        file,
        _scoped_session_id(scope, client_sid),
    )
    result.session_id = client_sid
    _attach_session(response, client_sid)
    return result


@router.get("/knowledge/screen", tags=["knowledge"])
async def knowledge_screen(
    route: str | None = Query(default=None, max_length=300),
    url: str | None = Query(default=None, max_length=500),
    scope: CallerScope = Depends(require_scope),
) -> dict:
    """Screen title and suggested questions for the widget."""
    info = knowledge.screen_info(scope, route, url)
    if info is None:
        return {"documented": False, "title": "", "suggested_questions": []}
    return {
        "documented": True,
        "title": info["title"],
        "suggested_questions": info["suggested_questions"],
    }


@router.get(
    "/knowledge/documents",
    tags=["knowledge"],
    dependencies=[Depends(require_service_key)],
)
async def knowledge_list() -> dict:
    """Registry of loaded guides (access, routes, hashes). Service key only."""
    return {"documents": knowledge.list_guides_admin()}
