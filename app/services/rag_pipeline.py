"""Retrieve context from Chroma and answer with configured LLM."""

from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncIterator
from threading import Lock
from typing import Any

from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
)
from langchain_core.runnables.history import RunnableWithMessageHistory

from app.config.settings import get_settings
from app.services.chat_memory import get_message_history
from app.services.vector_store import similarity_search
from app.utils.logger import get_logger

logger = get_logger(__name__)

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
    from langchain_community.chat_models import ChatOllama

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


def _rag_retrieve(question: str) -> tuple[str, str, list[dict]]:
    q = (question or "").strip()
    if not q:
        raise ValueError("Question must not be empty")
    docs = similarity_search(q)
    context = _format_context(docs)
    sources = _sources_from_docs(docs)
    return context, q, sources


def _rag_invoke_payload(context: str, q: str) -> dict[str, Any]:
    s = get_settings()
    tmpl = PromptTemplate.from_template(s.rag.prompt_template)
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


def _strip_spurious_trailing_idk(text: str) -> str:
    """
    Small LMs sometimes append \"I don't know\" after a full answer. Drop that
    suffix only when it is the whole tail and there is already enough content.
    """
    raw = (text or "").strip()
    if len(raw) < 60:
        return raw
    needle = "i don't know"
    idx = raw.lower().rfind(needle)
    if idx < 0:
        return raw
    head = raw[:idx].rstrip()
    tail = raw[idx:].strip()
    if len(head) < 40:
        return raw
    tail_clean = tail.lower().rstrip(".!?: \n\t")
    if tail_clean != needle:
        return raw
    return head


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


def answer_question(question: str, session_id: str) -> tuple[str, list[dict]]:
    if not (session_id or "").strip():
        raise ValueError("session_id must be non-empty")
    context, q, sources = _rag_retrieve(question)
    payload = _rag_invoke_payload(context, q)
    chain = get_chain_with_history()
    cfg = {"configurable": {"session_id": session_id.strip()}}
    sid = session_id.strip()
    response = chain.invoke(payload, config=cfg)
    text = _strip_spurious_trailing_idk(_invoke_answer_text(response))
    logger.info(
        "rag_query_complete",
        extra={"question_len": len(q), "sources": len(sources)},
    )
    return text, sources


async def stream_answer(
    question: str, session_id: str
) -> AsyncIterator[dict[str, Any]]:
    """Yield SSE payloads; history commits when ``astream`` completes.

    First event has type ``session`` and key ``session_id`` so stream clients
    can persist the id without reading response headers.
    """
    if not (session_id or "").strip():
        raise ValueError("session_id must be non-empty")
    sid = session_id.strip()
    # Lets browsers / fetch clients bind multi-turn memory without header/cookie.
    yield {"type": "session", "session_id": sid}

    context, q, sources = await asyncio.to_thread(_rag_retrieve, question)
    yield {"type": "sources", "chunks": sources}

    payload = _rag_invoke_payload(context, q)
    chain = get_chain_with_history()
    cfg = {"configurable": {"session_id": sid}}
    try:
        async for chunk in chain.astream(payload, config=cfg):
            text = _stream_chunk_text(chunk)
            if text:
                yield {"type": "token", "text": text}
    except Exception as e:
        logger.exception("stream_failed", extra={"error": str(e)})
        yield {"type": "error", "message": str(e)}
        return

    logger.info(
        "rag_stream_complete",
        extra={"question_len": len(q), "sources": len(sources)},
    )
    yield {"type": "done"}


class RAGPipeline:
    """Thin wrapper for dependency injection and testing."""

    async def answer(
        self, question: str, session_id: str
    ) -> tuple[str, list[dict]]:
        return await asyncio.to_thread(answer_question, question, session_id)

    async def stream(
        self, question: str, session_id: str
    ) -> AsyncIterator[dict[str, Any]]:
        async for item in stream_answer(question, session_id):
            yield item
