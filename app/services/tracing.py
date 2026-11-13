"""LangSmith traces of the admin-app chat: one trace per question (app_chat -> retrieve, model calls).

Tracing is switched on per question through a context, never with LANGSMITH_TRACING, so only
/app-chat is sent and the public chat stays out. Traces hold the question, the guide passages and
the answer, but no user id. Failures here are logged and never reach the user.
"""

from __future__ import annotations

import asyncio
import contextvars
import os
import uuid
from typing import Any, AsyncIterator, Coroutine, TypeVar

from langsmith import Client, RunTree, tracing_context

from app.config.settings import get_settings
from app.services import chat_store
from app.utils.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T")
_FEEDBACK_KEY = "user_rating"
_client: Client | None = None


def start() -> None:
    """Connect when langsmith.enabled and LANGSMITH_API_KEY are set; otherwise tracing stays off."""
    global _client
    s = get_settings()
    key = s.langsmith_api_key.get_secret_value().strip() if s.langsmith_api_key else ""
    if not s.langsmith.enabled or not key:
        logger.info("startup | langsmith off")
        return
    # The model calls are traced by LangChain, whose client reads these. .env is not in os.environ.
    os.environ["LANGSMITH_API_KEY"] = key
    os.environ["LANGSMITH_ENDPOINT"] = s.langsmith.endpoint
    _client = Client(api_url=s.langsmith.endpoint, api_key=key)
    logger.info("startup | langsmith project=%s", s.langsmith.project)


def stop() -> None:
    """Send what is still queued."""
    global _client
    client, _client = _client, None
    if client is not None:
        try:
            client.flush()
        except Exception as e:
            logger.warning("langsmith_flush_failed | %s", type(e).__name__)


def _run_id(request_id: str) -> uuid.UUID | None:
    try:
        return uuid.UUID(hex=request_id)
    except (TypeError, ValueError):
        return None


class QuestionTrace:
    """One question's trace. Without a client every method only passes through."""

    def __init__(self, run: RunTree | None = None):
        self._run = run
        self._context: contextvars.Context | None = None
        if run is not None:
            # Own context, so nothing leaks into the response stream between tokens.
            self._context = contextvars.copy_context()
            # Kept alive: its exit would only reset this private context.
            self._manager = tracing_context(enabled=True, parent=run, project_name=run.session_name)
            self._context.run(self._manager.__enter__)

    async def run(self, coro: Coroutine[Any, Any, T]) -> T:
        """Await ``coro`` inside the trace; threads it starts with asyncio.to_thread stay inside."""
        if self._context is None:
            return await coro
        return await asyncio.create_task(coro, context=self._context)

    async def stream(self, items: AsyncIterator[T]) -> AsyncIterator[T]:
        """Iterate ``items`` inside the trace."""
        iterator = items.__aiter__()
        while True:
            try:
                item = await self.run(iterator.__anext__())
            except StopAsyncIteration:
                return
            yield item

    def end(self, answer: str, outcome: str, retrieval: Any = None) -> None:
        """Close the trace with the answer the user saw. Only the first call counts."""
        run, self._run = self._run, None
        if run is None:
            return
        try:
            run.add_metadata({
                "outcome": outcome,
                "retrieval_mode": getattr(retrieval, "mode", None),
                "rewritten_query": getattr(retrieval, "rewritten", None) or None,
                "routed": getattr(retrieval, "routed", None),
            })
            run.end(outputs={"answer": answer}, error=answer if outcome == chat_store.ERROR else None)
            run.patch()
        except Exception as e:
            logger.warning("langsmith_trace_failed | %s", type(e).__name__)


def question(
    question_text: str,
    *,
    request_id: str,
    session_id: str,
    tenant: str,
    role: str | None,
    route: str | None,
    sport: str | None,
    language: str | None,
    streamed: bool,
) -> QuestionTrace:
    """Open the trace of one question. Its id comes from the answer's message id, for the votes."""
    if _client is None:
        return QuestionTrace()
    try:
        run = RunTree(
            name="app_chat",
            run_type="chain",
            id=_run_id(request_id) or uuid.uuid4(),
            inputs={"question": question_text},
            project_name=get_settings().langsmith.project,
            client=_client,
            tags=[f"tenant:{tenant}"],
            extra={"metadata": {
                "tenant": tenant, "role": role, "session_id": session_id, "route": route,
                "sport": sport, "language": language, "streamed": streamed,
                "model": get_settings().llm.local_model_name,
            }},
        )
        run.post()
        return QuestionTrace(run)
    except Exception as e:
        logger.warning("langsmith_trace_failed | %s", type(e).__name__)
        return QuestionTrace()


def feedback(message_id: str, rating: str, comment: str | None) -> None:
    """Add a thumbs up/down to the answer's trace. Voting again replaces the vote."""
    run_id = _run_id(message_id)
    if _client is None or run_id is None:
        return
    try:
        _client.create_feedback(
            run_id,
            key=_FEEDBACK_KEY,
            score=1 if rating == "up" else 0,
            comment=comment,
            trace_id=run_id,  # sent in the background, not during the request
            feedback_id=uuid.uuid5(run_id, _FEEDBACK_KEY),
        )
    except Exception as e:
        logger.warning("langsmith_feedback_failed | %s", type(e).__name__)
