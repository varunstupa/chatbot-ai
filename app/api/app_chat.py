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
    Path as FastAPIPath,
    Query,
    Request,
    Response,
)
from fastapi.responses import StreamingResponse

from app.api.dependencies import get_rag_pipeline
from app.api.routes import _attach_session
from app.config.settings import get_settings
from app.core import constants
from app.models.schemas import (
    FeedbackRequest,
    FeedbackStatusRequest,
    QueryRequest,
    QueryResponse,
    RetrievedChunk,
    UsageResetRequest,
)
from app.knowledge import service as knowledge
from app.services import app_chat, chat_limits, chat_store, llm_warmup, tracing
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
NL = chr(10)


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


def _location_prefix(holder: dict) -> str:
    """The code-written opening sentence when the answer is on another screen (dynamic prompt)."""
    result = holder.get("result")
    return result.location_prefix if result is not None else ""


def _screen_title(scope: CallerScope, body: QueryRequest) -> str:
    if not body.screen:
        return ""
    info = knowledge.screen_info(
        scope, body.screen.route, body.screen.url, app_chat.sport_from_id(body.sport_id)
    )
    return (info or {}).get("title", "")


def _ms(since: float | None, start: float) -> int | None:
    return None if since is None else int((since - start) * 1000)


async def _reserve(scope: CallerScope) -> chat_limits.Reservation:
    """Take one question from the caller's daily, weekly and monthly limits, or refuse."""
    try:
        return await chat_limits.limits.reserve(scope)
    except chat_limits.LimitDenied as e:
        logger.info("chat_limit_reached | tenant=%s window=%s", scope.tenant, e.payload.get("window"))
        raise HTTPException(status_code=429, detail=e.payload) from e
    except chat_limits.MissingUser as e:
        raise HTTPException(status_code=401, detail={"code": "chat_user_required"}) from e
    except chat_limits.LimitsUnavailable as e:
        raise HTTPException(status_code=503, detail={"code": "chat_limits_unavailable"}) from e


async def _reservation(scope: CallerScope, request: Request) -> chat_limits.Reservation:
    """The gateway's reservation (X-Chat-Request-Id) when it reserved already, else reserve here."""
    request_id = request.headers.get("x-chat-request-id")
    if not request_id:
        return await _reserve(scope)
    try:
        res = await chat_limits.limits.lookup(scope, request_id)
    except Exception as e:
        logger.error("chat_reservation_lookup_failed | %s", e)
        raise HTTPException(status_code=503, detail={"code": "chat_limits_unavailable"}) from e
    if res is None:
        raise HTTPException(status_code=409, detail={"code": "chat_reservation_invalid"})
    return res


def _trace(
    scope: CallerScope, body: QueryRequest, q: str, session_id: str, request_id: str, language, streamed: bool,
) -> tracing.QuestionTrace:
    return tracing.question(
        q, request_id=request_id, session_id=session_id, tenant=scope.tenant, role=scope.role,
        route=body.screen.route if body.screen else None, sport=app_chat.sport_from_id(body.sport_id),
        language=language.code if language else None, streamed=streamed,
    )


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
    message_id: str | None = None,
) -> str:
    """Queue the question and the answer the user saw for the chat store (never raises).

    Returns the answer's message id, which the widget sends back with a thumbs up/down.
    """
    result = holder.get("result")
    llm = get_settings().llm
    record = chat_store.ChatRecord(
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
    if message_id:
        record.message_id = message_id
    chat_store.record(record)
    return record.message_id


async def _answer_json(
    body: QueryRequest,
    request: Request,
    response: Response,
    pipeline: RAGPipeline,
    scope: CallerScope,
    reservation: chat_limits.Reservation,
) -> QueryResponse:
    q = _question(body)
    session_id = _client_session_id(body.session_id, request)
    scoped = _scoped_session_id(scope, session_id)

    s = get_settings()
    language = detect_language(q)
    no_answer = app_chat.no_answer_text(language)
    started, holder = time.monotonic(), {}
    screen_title = _screen_title(scope, body)
    trace = _trace(scope, body, q, session_id, reservation.request_id, language, streamed=False)

    def store(answer_text: str, outcome: str) -> str:
        trace.end(answer_text, outcome, holder.get("result"))
        return _store_chat(
            scope, body, session_id=session_id, question=q, answer=answer_text, outcome=outcome,
            screen_title=screen_title, language=language, holder=holder, started=started,
            first_token=None, streamed=False, message_id=reservation.request_id,
        )

    try:
        answer, sources = await trace.run(pipeline.answer(
            q,
            scoped,
            prompt_template=app_chat.prompt_for(
                screen_title, language, app_chat.sport_from_id(body.sport_id), question=q
            ),
            retriever=_retriever(scope, body, holder),
            no_answer_text=no_answer,
            use_history=app_chat.is_follow_up(q),
        ))
        if app_chat.is_no_answer(answer):
            answer = no_answer
        elif app_chat.reveals_internal_detail(answer):
            logger.warning("app_chat_guardrail | blocked answer with internal detail")
            answer = no_answer
        suggestions = None
        # A question about the modules gets "Did you mean" (also when the answer was
        # blocked for naming an API): only user questions are suggested, never API details.
        if answer == no_answer:
            found = await trace.run(asyncio.to_thread(
                app_chat.did_you_mean, scope, q, app_chat.sport_from_id(body.sport_id), language
            ))
            if found:
                answer, suggestions = found
        elif app_chat.needs_location_prefix(prefix := _location_prefix(holder), answer):
            answer = prefix + NL + NL + answer
    except RuntimeError as e:
        logger.error("llm_unavailable | %s", str(e))
        await chat_limits.limits.refund(reservation)
        store(str(e), chat_store.ERROR)
        raise HTTPException(
            status_code=503,
            detail={"message": str(e), "code": constants.ERROR_LLM_UNAVAILABLE},
        ) from e
    except Exception as e:
        logger.exception("app_chat_failed")
        await chat_limits.limits.refund(reservation)
        store(s.messages.query_processing_failed, chat_store.ERROR)
        raise HTTPException(status_code=500, detail=s.messages.query_processing_failed) from e

    not_found = answer == no_answer or bool(suggestions)
    message_id = store(answer, chat_store.NOT_FOUND if not_found else chat_store.ANSWERED)
    await chat_limits.limits.commit(reservation, "not_found" if not_found else "answered")
    _attach_session(response, session_id)
    return QueryResponse(
        answer=answer,
        chunks=[RetrievedChunk(**src) for src in sources],
        session_id=session_id,
        suggestions=suggestions,
        message_id=message_id,
        usage=reservation.usage,
    )


def _answer_stream(
    body: QueryRequest,
    request: Request,
    pipeline: RAGPipeline,
    scope: CallerScope,
    reservation: chat_limits.Reservation,
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
        # The location sentence goes out once, before the model's first words.
        opening_sent, opening_text = False, ""

        def opening() -> str:
            nonlocal opening_sent, opening_text
            if opening_sent:
                return ""
            opening_sent = True
            prefix = _location_prefix(holder)
            # Decided on the first words held back so far: no duplicate when the model gives the path.
            if app_chat.needs_location_prefix(prefix, full):
                opening_text = prefix + NL + NL
            return opening_text
        first_token: float | None = None
        stored = False
        trace = _trace(scope, body, q, session_id, reservation.request_id, language, streamed=True)

        def store(answer_text: str, outcome: str) -> str | None:
            nonlocal stored
            if stored:
                return None
            stored = True
            trace.end(answer_text, outcome, holder.get("result"))
            return _store_chat(
                scope, body, session_id=session_id, question=q, answer=answer_text, outcome=outcome,
                screen_title=screen_title, language=language, holder=holder, started=started,
                first_token=first_token, streamed=True, message_id=reservation.request_id,
            )

        try:
            async for item in trace.stream(pipeline.stream(
                q,
                scoped,
                prompt_template=app_chat.prompt_for(
                    screen_title, language, app_chat.sport_from_id(body.sport_id), question=q
                ),
                retriever=_retriever(scope, body, holder),
                no_answer_text=no_answer,
                use_history=app_chat.is_follow_up(q),
            )):
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
                        yield _line({"type": "token", "text": opening() + full[sent_upto:safe_end]})
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
                        found = await trace.run(asyncio.to_thread(
                            app_chat.did_you_mean, scope, q,
                            app_chat.sport_from_id(body.sport_id), language,
                        ))
                        if found:
                            final, suggestions = found
                        if sent_upto == 0:
                            yield _line({"type": "token", "text": final})
                        item = {"type": "done", "answer": final}
                        if suggestions:
                            item["suggestions"] = suggestions
                    else:
                        lead = opening() if sent_upto == 0 else ""
                        if sent_upto < len(full) or lead:
                            yield _line({"type": "token", "text": lead + full[sent_upto:]})
                            sent_upto = len(full)
                        if opening_text:
                            final = opening_text + final
                            if item.get("answer"):
                                item = {**item, "answer": final}
                    message_id = store(final, chat_store.NOT_FOUND if not_found else chat_store.ANSWERED)
                    await chat_limits.limits.commit(reservation, "not_found" if not_found else "answered")
                    if message_id:
                        item = {**item, "message_id": message_id}
                    if reservation.usage:
                        item = {**item, "usage": reservation.usage}
                elif kind == "session":
                    # Never hand the tenant-scoped history key to the browser.
                    item = {"type": "session", "session_id": session_id}
                elif kind == "error":
                    # Model/server details stay in the log, not in the browser.
                    logger.error("app_chat_llm_error | %s", item.get("message"))
                    item = {"type": "error", "message": s.messages.query_processing_failed}
                    await chat_limits.limits.refund(reservation)
                    store(s.messages.query_processing_failed, chat_store.ERROR)
                yield _line(item)
        except Exception:
            logger.exception("app_chat_stream_failed")
            await chat_limits.limits.refund(reservation)
            store(s.messages.query_processing_failed, chat_store.ERROR)
            yield _line({"type": "error", "message": s.messages.query_processing_failed})
        finally:
            trace.end(full, "disconnected", holder.get("result"))
            if not reservation.settled:
                # The client left (disconnect or cancel) after the model ran: the question counts.
                asyncio.ensure_future(chat_limits.limits.commit(reservation, "disconnected"))

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
    _question(body)  # an empty question is refused before it can use quota
    reservation = await _reservation(scope, request)
    accept = (request.headers.get("accept") or "").lower()
    if stream or accept.startswith("text/event-stream"):
        return _answer_stream(body, request, pipeline, scope, reservation)
    return await _answer_json(body, request, response, pipeline, scope, reservation)


@router.post("/app-chat/stream", tags=["app-chat"])
async def app_chat_stream(
    body: QueryRequest,
    request: Request,
    pipeline: RAGPipeline = Depends(get_rag_pipeline),
    scope: CallerScope = Depends(require_scope),
) -> StreamingResponse:
    _question(body)
    reservation = await _reservation(scope, request)
    return _answer_stream(body, request, pipeline, scope, reservation)


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


@router.post("/app-chat/feedback", tags=["app-chat"])
async def app_chat_feedback(
    body: FeedbackRequest,
    scope: CallerScope = Depends(require_scope),
) -> dict:
    """Thumbs up/down on one of the caller's own answers; stored with that question and answer.

    Voting again changes the vote. Only the answering user of the same tenant can rate an answer.
    """
    status = await chat_store.save_feedback(scope.tenant, scope.user_id, body.message_id, body.rating, body.comment)
    if status == "unknown":
        raise HTTPException(status_code=404, detail="This answer can no longer be rated.")
    if status == "unavailable":
        raise HTTPException(status_code=503, detail="Feedback cannot be saved right now.")
    tracing.feedback(body.message_id, body.rating, body.comment)
    logger.info("app_chat_feedback | tenant=%s rating=%s", scope.tenant, body.rating)
    return {"saved": True, "rating": body.rating}


@router.get("/app-chat/feedback", tags=["app-chat"], dependencies=[Depends(require_service_key)])
async def app_chat_feedback_list(
    tenant: str | None = Query(default=None, max_length=100),
    rating: str | None = Query(default="down", pattern="^(up|down)$"),
    status: str | None = Query(default="open", pattern="^(open|fixed|wont_fix)$"),
    limit: int = Query(default=100, ge=1, le=1000),
) -> dict:
    """Votes for review (default: open thumbs-down answers), newest first. Service key only."""
    items = await chat_store.list_feedback(tenant, rating, status, limit)
    if items is None:
        raise HTTPException(status_code=503, detail="The chat store is not running.")
    return {"count": len(items), "items": items}


@router.patch(
    "/app-chat/feedback/{tenant}/{message_id}", tags=["app-chat"],
    dependencies=[Depends(require_service_key)],
)
async def app_chat_feedback_status(tenant: str, message_id: str, body: FeedbackStatusRequest) -> dict:
    """Mark a reviewed vote fixed or wont_fix (or open it again). Service key only."""
    changed = await chat_store.set_feedback_status(tenant, message_id, body.status, body.note)
    if changed is None:
        raise HTTPException(status_code=503, detail="The chat store is not running.")
    if changed == 0:
        raise HTTPException(status_code=404, detail="No vote for this answer.")
    return {"updated": changed, "status": body.status}


@router.post("/app-chat/quota/reserve", tags=["app-chat"])
async def app_chat_quota_reserve(scope: CallerScope = Depends(require_scope)) -> dict:
    """Called by the gateway before it forwards a question: take one question from the caller's
    limits (Redis, else MongoDB). 429 when used up, 503 when neither store is reachable."""
    res = await _reserve(scope)
    return {"request_id": res.request_id, "usage": res.usage}


@router.post("/app-chat/quota/{request_id}/refund", tags=["app-chat"])
async def app_chat_quota_refund(
    request_id: str = FastAPIPath(pattern=r"^[0-9a-f]{32}$"),
    scope: CallerScope = Depends(require_scope),
) -> dict:
    """Called by the gateway when the chatbot failed: give the caller's question back (once)."""
    try:
        return {"refunded": await chat_limits.limits.refund_by_id(scope, request_id)}
    except Exception as e:
        logger.error("chat_quota_refund_failed | %s", e)
        raise HTTPException(status_code=503, detail={"code": "chat_limits_unavailable"}) from e


def _require_limits() -> None:
    if get_settings().chat_limits.mode == "off" or chat_limits.limits.db is None:
        raise HTTPException(status_code=503, detail={"code": "chat_limits_off"})


@router.get("/app-chat/usage", tags=["app-chat"], dependencies=[Depends(require_service_key)])
async def app_chat_usage(
    tenant: str = Query(min_length=1, max_length=100),
    user_id: str = Query(min_length=1, max_length=200),
) -> dict:
    """A user's question limits: live Redis counts, MongoDB quota and history, queue health. Service key only."""
    _require_limits()
    return await chat_limits.limits.usage(tenant, user_id)


@router.post("/app-chat/usage/reset", tags=["app-chat"], dependencies=[Depends(require_service_key)])
async def app_chat_usage_reset(body: UsageResetRequest) -> dict:
    """Clear a user's count for the current day, week, month or all three. Service key only."""
    _require_limits()
    return await chat_limits.limits.reset(body.tenant, body.user_id, body.window)


@router.get("/knowledge/screen", tags=["knowledge"])
async def knowledge_screen(
    route: str | None = Query(default=None, max_length=300),
    url: str | None = Query(default=None, max_length=500),
    sport_id: int | None = Query(default=None),
    scope: CallerScope = Depends(require_scope),
) -> dict:
    """Screen title and suggested questions for the widget.

    The widget asks as soon as an event page opens, so the model starts loading here.
    """
    llm_warmup.warm_up_in_background()
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
