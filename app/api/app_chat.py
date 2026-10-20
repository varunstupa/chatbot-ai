"""Admin-app chat (JWT, tenant-scoped, screen-aware) and guide management routes."""

from __future__ import annotations

import asyncio
import json
import re
import time
import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Request,
    Response,
)
from fastapi.responses import StreamingResponse

from app.api.dependencies import get_rag_pipeline
from app.api.routes import _attach_session
from app.config.settings import get_settings
from app.core import constants
from app.models.schemas import QueryRequest, QueryResponse, RetrievedChunk
from app.knowledge import service as knowledge
from app.services import app_chat, chat_store
from app.services.auth import CallerScope, require_scope, require_service_key
from app.services.chat_memory import get_message_history
from app.services.language import detect_language
from app.services.rag_pipeline import RAGPipeline
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

_SESSION_RE = re.compile(r"^[A-Za-z0-9_-]{8,64}$")
# Characters of a streamed answer held back, so the guardrail can see an API path
# or code before any part of it is sent.
_HOLD_BACK = 60


def _client_session_id(body_session_id: str | None, request: Request) -> str:
    """Session id as the browser knows it. Anything malformed starts a new one."""
    header = request.headers.get("x-session-id")
    for raw in (body_session_id, header):
        t = (raw or "").strip()
        if _SESSION_RE.match(t):
            return t
    return str(uuid.uuid4())


def _scoped_session_id(scope: CallerScope, session_id: str) -> str:
    """History key. Bound to tenant and user so an id cannot be replayed."""
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
    sport = app_chat.sport_from_id(body.sport_id)

    def run(question: str) -> tuple[str, list[dict]]:
        result = app_chat.retrieve(scope, question, route, url, sport)
        app_chat.audit(scope, route, result)
        holder["result"] = result
        return result.context, result.sources

    return run


def _screen_title(scope: CallerScope, body: QueryRequest) -> str:
    if not body.screen:
        return ""
    info = knowledge.screen_info(
        scope, body.screen.route, body.screen.url, app_chat.sport_from_id(body.sport_id)
    )
    return (info or {}).get("title", "")


def _ms(since: float | None, start: float) -> int | None:
    return None if since is None else int((since - start) * 1000)


def _store_chat(
    scope: CallerScope,
    body: QueryRequest,
    *,
    session_id: str,
    question: str,
    answer: str,
    outcome: str,
    screen_title: str,
    language,
    holder: dict,
    started: float,
    first_token: float | None,
    streamed: bool,
) -> None:
    """Queue the question and the answer the user saw for the chat store (never raises)."""
    result = holder.get("result")
    llm = get_settings().llm
    chat_store.record(
        chat_store.ChatRecord(
            tenant=scope.tenant,
            session_id=session_id,
            question=question,
            answer=answer,
            outcome=outcome,
            user_id=scope.user_id,
            role=scope.role,
            route=body.screen.route if body.screen else None,
            screen_title=screen_title or None,
            sport=app_chat.sport_from_id(body.sport_id),
            language=language.code if language else None,
            retrieval_mode=result.mode if result else None,
            doc_ids=sorted({h.doc_id for h in result.hits}) if result else [],
            sources=[{"title": h.title, "section": h.section} for h in result.hits] if result else [],
            model=llm.local_model_name,
            first_token_ms=_ms(first_token, started),
            total_ms=_ms(time.monotonic(), started),
            streamed=streamed,
        )
    )


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

    s = get_settings()
    language = detect_language(q)
    no_answer = app_chat.no_answer_text(language)
    started, holder = time.monotonic(), {}
    screen_title = _screen_title(scope, body)

    def store(answer_text: str, outcome: str) -> None:
        _store_chat(
            scope, body, session_id=session_id, question=q, answer=answer_text, outcome=outcome,
            screen_title=screen_title, language=language, holder=holder, started=started,
            first_token=None, streamed=False,
        )

    try:
        answer, sources = await pipeline.answer(
            q,
            scoped,
            prompt_template=app_chat.prompt_for(
                screen_title, language, app_chat.sport_from_id(body.sport_id)
            ),
            retriever=_retriever(scope, body, holder),
            no_answer_text=no_answer,
        )
        if app_chat.is_no_answer(answer):
            answer = no_answer
        elif app_chat.reveals_internal_detail(answer):
            logger.warning("app_chat_guardrail | blocked answer with internal detail")
            answer = no_answer
        suggestions = None
        # A question about the modules gets "Did you mean" (also when the answer was
        # blocked for naming an API): only user questions are suggested, never API details.
        if answer == no_answer:
            found = await asyncio.to_thread(
                app_chat.did_you_mean, scope, q, app_chat.sport_from_id(body.sport_id), language
            )
            if found:
                answer, suggestions = found
    except RuntimeError as e:
        logger.error("llm_unavailable | %s", str(e))
        store(str(e), chat_store.ERROR)
        raise HTTPException(
            status_code=503,
            detail={"message": str(e), "code": constants.ERROR_LLM_UNAVAILABLE},
        ) from e
    except Exception as e:
        logger.exception("app_chat_failed")
        store(s.messages.query_processing_failed, chat_store.ERROR)
        raise HTTPException(status_code=500, detail=s.messages.query_processing_failed) from e

    store(answer, chat_store.NOT_FOUND if answer == no_answer or suggestions else chat_store.ANSWERED)
    _attach_session(response, session_id)
    return QueryResponse(
        answer=answer,
        chunks=[RetrievedChunk(**src) for src in sources],
        session_id=session_id,
        suggestions=suggestions,
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
    language = detect_language(q)
    no_answer = app_chat.no_answer_text(language)
    started, holder = time.monotonic(), {}
    screen_title = _screen_title(scope, body)

    def _line(obj: dict) -> str:
        return f"data: {json.dumps(obj, ensure_ascii=False)}\n\n"

    async def sse_events():
        # Tokens stream as they arrive. Text is held while it could still spell NO_ANSWER,
        # and the last _HOLD_BACK characters are always held, so text naming an API or
        # containing code is caught before it reaches the browser. When that happens the
        # stream stops and the final "done" answer replaces the message.
        sent_upto, decided, is_marker, blocked, full = 0, False, False, False, ""
        first_token: float | None = None
        stored = False

        def store(answer_text: str, outcome: str) -> None:
            nonlocal stored
            if stored:
                return
            stored = True
            _store_chat(
                scope, body, session_id=session_id, question=q, answer=answer_text, outcome=outcome,
                screen_title=screen_title, language=language, holder=holder, started=started,
                first_token=first_token, streamed=True,
            )

        try:
            async for item in pipeline.stream(
                q,
                scoped,
                prompt_template=app_chat.prompt_for(
                    screen_title, language, app_chat.sport_from_id(body.sport_id)
                ),
                retriever=_retriever(scope, body, holder),
                no_answer_text=no_answer,
            ):
                kind = item.get("type")
                if kind == "token":
                    full += item.get("text", "")
                    if first_token is None:
                        first_token = time.monotonic()
                    if not decided:
                        if app_chat.is_no_answer(full):
                            decided = is_marker = True
                        elif app_chat.could_become_no_answer(full):
                            continue
                        else:
                            decided = True
                    if is_marker or blocked or no_answer.startswith(full):
                        continue
                    if app_chat.reveals_internal_detail(full):
                        blocked = True
                        logger.warning("app_chat_guardrail | stopped stream with internal detail")
                        continue
                    safe_end = len(full) - _HOLD_BACK
                    if safe_end > sent_upto:
                        yield _line({"type": "token", "text": full[sent_upto:safe_end]})
                        sent_upto = safe_end
                    continue
                if kind == "done":
                    final = item.get("answer") or full
                    if is_marker or app_chat.is_no_answer(final):
                        final = no_answer
                    elif blocked or app_chat.reveals_internal_detail(final):
                        logger.warning("app_chat_guardrail | blocked answer with internal detail")
                        final = no_answer
                    not_found = final == no_answer
                    if not_found:
                        suggestions = None
                        # A question about the modules gets "Did you mean" instead; the
                        # final "done" answer replaces any text already streamed.
                        found = await asyncio.to_thread(
                            app_chat.did_you_mean, scope, q,
                            app_chat.sport_from_id(body.sport_id), language,
                        )
                        if found:
                            final, suggestions = found
                        if sent_upto == 0:
                            yield _line({"type": "token", "text": final})
                        item = {"type": "done", "answer": final}
                        if suggestions:
                            item["suggestions"] = suggestions
                    elif sent_upto < len(full):
                        yield _line({"type": "token", "text": full[sent_upto:]})
                        sent_upto = len(full)
                    store(final, chat_store.NOT_FOUND if not_found else chat_store.ANSWERED)
                elif kind == "session":
                    # Never hand the tenant-scoped history key to the browser.
                    item = {"type": "session", "session_id": session_id}
                elif kind == "error":
                    # Model/server details stay in the log, not in the browser.
                    logger.error("app_chat_llm_error | %s", item.get("message"))
                    item = {"type": "error", "message": s.messages.query_processing_failed}
                    store(s.messages.query_processing_failed, chat_store.ERROR)
                yield _line(item)
        except Exception:
            logger.exception("app_chat_stream_failed")
            store(s.messages.query_processing_failed, chat_store.ERROR)
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


@router.post("/app-chat/session/close", tags=["app-chat"], status_code=204)
async def app_chat_session_close(
    request: Request,
    scope: CallerScope = Depends(require_scope),
) -> Response:
    """The widget was closed or the page left: store this session's conversation now.

    The session id comes from the JSON body (``session_id``) or the ``X-Session-Id``
    header; the tenant always from the caller's identity. Unknown ids are ignored.
    """
    session_id = request.headers.get("x-session-id") or ""
    try:
        body = await request.json()
        if isinstance(body, dict) and isinstance(body.get("session_id"), str):
            session_id = body["session_id"]
    except Exception:
        pass
    session_id = session_id.strip()
    if _SESSION_RE.match(session_id):
        chat_store.close_session(scope.tenant, session_id)
    return Response(status_code=204)


@router.get("/knowledge/screen", tags=["knowledge"])
async def knowledge_screen(
    route: str | None = Query(default=None, max_length=300),
    url: str | None = Query(default=None, max_length=500),
    sport_id: int | None = Query(default=None),
    scope: CallerScope = Depends(require_scope),
) -> dict:
    """Screen title and suggested questions for the widget."""
    info = knowledge.screen_info(scope, route, url, app_chat.sport_from_id(sport_id))
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
