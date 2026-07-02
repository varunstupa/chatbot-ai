"""Retrieve context from Chroma and answer with configured LLM."""

from __future__ import annotations

import asyncio
import os
import re
from collections.abc import AsyncIterator
from threading import Lock
from typing import Any

from langchain_core.messages import AIMessage
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
)
from langchain_core.runnables.history import RunnableWithMessageHistory

from app.config.settings import get_settings
from app.services.chat_memory import get_message_history
from app.services.vector_store import CorpusMode, similarity_search
from app.utils.logger import get_logger

logger = get_logger(__name__)


def _is_backend_llm_error(exc: BaseException) -> bool:
    text = str(exc).lower()
    return (
        "ollama" in text
        or "/api/chat" in text
        or "11434" in text
        or "chatopenai" in text
        or "openai" in text
        and "error" in text
    )


def _friendly_llm_error_message(exc: BaseException) -> str:
    """Normalize vague LangChain / aiohttp error strings for operators."""
    raw = str(exc).strip()
    s = get_settings()
    if "bound method" in raw or "clientresponse.text" in raw.lower():
        raw = (
            "LLM HTTP error (response body not included by the client). "
            "Often Ollama HTTP 500: model missing, OOM, or context too long."
        )
    if s.llm.provider in ("local", "ollama"):
        return (
            f"{raw} "
            f"— Ollama: {s.llm.local_base_url}, model `{s.llm.local_model_name}`. "
            "Try: `ollama pull <model>` then `ollama run <model>` and check "
            "`ollama ps` / server logs."
        )
    return f"{raw} — Check NVIDIA_API_KEY and llm.model / base_url."


_llm_lock = Lock()
_llm = None
_chain_lock = Lock()
_chain_with_history: RunnableWithMessageHistory | None = None


def _build_llm():
    s = get_settings()
    if s.llm.provider == "nvidia":
        from langchain_openai import ChatOpenAI

        api_key = None
        if s.nvidia_api_key:
            api_key = s.nvidia_api_key.get_secret_value().strip() or None
        if not api_key:
            api_key = os.environ.get("NVIDIA_API_KEY", "").strip() or None
        if not api_key:
            raise RuntimeError(s.llm.missing_api_key_message)
        kwargs: dict = {
            "model": s.llm.model,
            "temperature": s.llm.temperature,
            "api_key": api_key,
            "base_url": s.llm.base_url.strip(),
            "frequency_penalty": s.llm.frequency_penalty,
            "presence_penalty": s.llm.presence_penalty,
        }
        if s.llm.top_p is not None:
            kwargs["top_p"] = s.llm.top_p
        # NVIDIA chat API rejects max_completion_tokens; LangChain maps max_tokens → that.
        # Omit max_tokens here (NVIDIA uses a server default). See config max_tokens note.
        return ChatOpenAI(**kwargs)
    from langchain_ollama import ChatOllama

    return ChatOllama(
        base_url=s.llm.local_base_url,
        model=s.llm.local_model_name,
        temperature=s.llm.temperature,
    )


def get_llm():
    global _llm
    with _llm_lock:
        if _llm is None:
            _llm = _build_llm()
        return _llm


def _build_chat_prompt() -> ChatPromptTemplate:
    """RAG user turn uses ``rag_turn``; prior Q/A live in ``history``."""
    s = get_settings()
    blocks: list = [
        MessagesPlaceholder("history", optional=True),
        ("human", "{rag_turn}"),
    ]
    sys_msg = (s.llm.system_message or "").strip()
    if sys_msg:
        blocks.insert(0, ("system", "{system_message}"))
    return ChatPromptTemplate.from_messages(blocks)


def get_chain_with_history() -> RunnableWithMessageHistory:
    """
    LangChain runnable: inject ``history``, then ``prompt | llm``.

    History stores short user ``input`` + model replies; ``rag_turn`` holds
    this turn's full RAG prompt (context + question) and is not stored.
    """
    global _chain_with_history
    with _chain_lock:
        if _chain_with_history is None:
            prompt = _build_chat_prompt()
            llm = get_llm()
            # RunnableWithMessageHistory updates history after run (incl. stream end).
            _chain_with_history = RunnableWithMessageHistory(
                prompt | llm,
                get_message_history,
                input_messages_key="input",
                history_messages_key="history",
            )
        return _chain_with_history


def reset_rag_chain_for_tests() -> None:
    global _chain_with_history
    with _chain_lock:
        _chain_with_history = None


def reset_llm_for_tests() -> None:
    global _llm
    with _llm_lock:
        _llm = None
    reset_rag_chain_for_tests()


def _format_context(docs: list) -> str:
    parts = []
    for i, d in enumerate(docs):
        parts.append(f"[{i + 1}] {d.page_content}")
    return "\n\n".join(parts)


def _sources_from_docs(docs: list) -> list[dict]:
    return [
        {
            "filename": d.metadata.get("filename"),
            "source": d.metadata.get("source"),
            "chunk_index": d.metadata.get("chunk_index"),
            "content": d.page_content or "",
        }
        for d in docs
    ]


def _rag_retrieve(
    question: str,
    corpus: CorpusMode = "merged",
) -> tuple[str, str, list[dict]]:
    q = (question or "").strip()
    if not q:
        raise ValueError("Question must not be empty")
    docs = similarity_search(q, corpus=corpus)
    context = _format_context(docs)
    sources = _sources_from_docs(docs)
    return context, q, sources


def _rag_invoke_payload(
    context: str,
    q: str,
    *,
    prompt_template: str | None = None,
) -> dict[str, Any]:
    s = get_settings()
    tmpl_str = (prompt_template or "").strip() or s.rag.prompt_template
    tmpl = PromptTemplate.from_template(tmpl_str)
    rag_turn = tmpl.format(context=context, question=q)
    sys_msg = (s.llm.system_message or "").strip()
    payload: dict[str, Any] = {"input": q, "rag_turn": rag_turn}
    if sys_msg:
        payload["system_message"] = sys_msg
    return payload


def _invoke_answer_text(response: Any) -> str:
    raw = response.content
    if raw is None:
        return ""
    if isinstance(raw, str):
        return raw.strip()
    if isinstance(raw, list):
        parts = []
        for block in raw:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text") or "")
        return "".join(parts).strip()
    return str(raw).strip()


# Trailing disclaimers models add after a valid answer (end-anchored only).
_TRAILING_IDK = (
    re.compile(
        r"\n*(?:\*\*)?I\s+don'?t\s+know\.?(?:\*\*)?\s*$",
        re.IGNORECASE | re.DOTALL,
    ),
    re.compile(
        r"\n*(?:\*\*)?I\s+do\s+not\s+know\.?(?:\*\*)?\s*$",
        re.IGNORECASE | re.DOTALL,
    ),
    re.compile(
        r"\n*(?:\*\*)?(?:I\s+am\s+not\s+sure|I'?m\s+not\s+sure)\.?(?:\*\*)?\s*$",
        re.IGNORECASE | re.DOTALL,
    ),
    re.compile(
        r"\n+#{1,3}\s*(?:\*\*)?I\s+don'?t\s+know\.?(?:\*\*)?\s*$",
        re.IGNORECASE | re.DOTALL,
    ),
)

# Minimum chars left after strip (avoid gutting short or empty replies).
_MIN_KEPT_AFTER_STRIP = 20


def _strip_spurious_trailing_idk(text: str) -> str:
    """
    Remove a trailing \"I don't know\" (and close variants) when the model
    appends it after already answering. Only matches the response tail.
    """
    raw = (text or "").rstrip()
    if len(raw) < _MIN_KEPT_AFTER_STRIP:
        return raw
    out = raw
    changed = True
    while changed:
        changed = False
        for pat in _TRAILING_IDK:
            candidate = pat.sub("", out).rstrip()
            if candidate != out and len(candidate) >= _MIN_KEPT_AFTER_STRIP:
                out = candidate
                changed = True
                break
    return out


def _ai_message_text(msg: Any) -> str:
    c = getattr(msg, "content", None)
    if c is None:
        return ""
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        parts = []
        for block in c:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text") or "")
        return "".join(parts)
    return str(c)


def _apply_stripped_answer_to_history(session_id: str, stripped: str) -> None:
    """Align last assistant turn with cleaned text (memory matches user-visible)."""
    sid = (session_id or "").strip()
    if not sid or not (stripped and stripped.strip()):
        return
    hist = get_message_history(sid)
    msgs = hist.messages
    if not msgs:
        return
    last = msgs[-1]
    if not isinstance(last, AIMessage):
        return
    if _ai_message_text(last).strip() == stripped.strip():
        return
    msgs[-1] = AIMessage(content=stripped)


def _stream_chunk_text(chunk: Any) -> str:
    raw = getattr(chunk, "content", None)
    if raw is None:
        return ""
    if isinstance(raw, str):
        return raw
    if isinstance(raw, list):
        parts = []
        for block in raw:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text") or "")
        return "".join(parts)
    return str(raw)


def answer_question(
    question: str,
    session_id: str,
    corpus: CorpusMode = "merged",
    *,
    prompt_template: str | None = None,
) -> tuple[str, list[dict]]:
    if not (session_id or "").strip():
        raise ValueError("session_id must be non-empty")
    sid = session_id.strip()
    context, q, sources = _rag_retrieve(question, corpus)
    if not sources:
        text = "I don't know"
        _apply_stripped_answer_to_history(sid, text)
        logger.info(
            "rag_query_complete",
            extra={
                "question_len": len(q),
                "sources": 0,
                "no_chunks": True,
            },
        )
        return text, sources
    payload = _rag_invoke_payload(
        context,
        q,
        prompt_template=prompt_template,
    )
    chain = get_chain_with_history()
    cfg = {"configurable": {"session_id": sid}}
    try:
        response = chain.invoke(payload, config=cfg)
    except (ValueError, OSError) as e:
        if _is_backend_llm_error(e):
            raise RuntimeError(_friendly_llm_error_message(e)) from e
        raise
    except Exception as e:
        if _is_backend_llm_error(e):
            raise RuntimeError(_friendly_llm_error_message(e)) from e
        raise
    text = _strip_spurious_trailing_idk(_invoke_answer_text(response))
    _apply_stripped_answer_to_history(sid, text)
    logger.info(
        "rag_query_complete",
        extra={"question_len": len(q), "sources": len(sources)},
    )
    return text, sources


async def stream_answer(
    question: str,
    session_id: str,
    corpus: CorpusMode = "merged",
    *,
    prompt_template: str | None = None,
) -> AsyncIterator[dict[str, Any]]:
    """Yield SSE payloads; history commits when ``astream`` completes.

    First event has type ``session`` and key ``session_id`` so stream clients
    can persist the id without reading response headers.

    Final ``done`` may include ``answer`` (canonical text) if trailing disclaimers
    were removed—clients may replace the assembled token buffer with it.
    """
    if not (session_id or "").strip():
        raise ValueError("session_id must be non-empty")
    sid = session_id.strip()
    # Lets browsers / fetch clients bind multi-turn memory without header/cookie.
    yield {"type": "session", "session_id": sid}

    context, q, sources = await asyncio.to_thread(_rag_retrieve, question, corpus)
    yield {"type": "sources", "chunks": sources}

    if not sources:
        yield {"type": "token", "text": "I don't know"}
        _apply_stripped_answer_to_history(sid, "I don't know")
        logger.info(
            "rag_stream_complete",
            extra={"question_len": len(q), "sources": 0, "no_chunks": True},
        )
        yield {"type": "done"}
        return

    payload = _rag_invoke_payload(
        context,
        q,
        prompt_template=prompt_template,
    )
    chain = get_chain_with_history()
    cfg = {"configurable": {"session_id": sid}}
    accumulated: list[str] = []
    try:
        async for chunk in chain.astream(payload, config=cfg):
            text = _stream_chunk_text(chunk)
            if text:
                accumulated.append(text)
                yield {"type": "token", "text": text}
    except Exception as e:
        if _is_backend_llm_error(e):
            logger.exception("stream_failed_llm_backend")
            yield {
                "type": "error",
                "message": _friendly_llm_error_message(e),
            }
        else:
            logger.exception("stream_failed", extra={"error": str(e)})
            yield {"type": "error", "message": str(e)}
        return

    full = "".join(accumulated)
    cleaned = _strip_spurious_trailing_idk(full)
    _apply_stripped_answer_to_history(sid, cleaned)

    logger.info(
        "rag_stream_complete",
        extra={"question_len": len(q), "sources": len(sources)},
    )
    done_payload: dict[str, Any] = {"type": "done"}
    if cleaned != full:
        done_payload["answer"] = cleaned
    yield done_payload


class RAGPipeline:
    """Thin wrapper for dependency injection and testing."""

    async def answer(
        self,
        question: str,
        session_id: str,
        corpus: CorpusMode = "merged",
        *,
        prompt_template: str | None = None,
    ) -> tuple[str, list[dict]]:
        return await asyncio.to_thread(
            answer_question,
            question,
            session_id,
            corpus,
            prompt_template=prompt_template,
        )

    async def stream(
        self,
        question: str,
        session_id: str,
        corpus: CorpusMode = "merged",
        *,
        prompt_template: str | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        async for item in stream_answer(
            question,
            session_id,
            corpus,
            prompt_template=prompt_template,
        ):
            yield item
