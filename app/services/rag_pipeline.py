"""Retrieve context from Chroma and answer with configured LLM."""

from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncIterator
from threading import Lock
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate

from app.config.settings import get_settings
from app.services.vector_store import similarity_search
from app.utils.logger import get_logger

logger = get_logger(__name__)

_llm_lock = Lock()
_llm = None


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


def reset_llm_for_tests() -> None:
    global _llm
    with _llm_lock:
        _llm = None


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


def _messages_for_prompt(prompt_text: str, sys_msg: str) -> list:
    messages = []
    if sys_msg:
        messages.append(SystemMessage(content=sys_msg))
    messages.append(HumanMessage(content=prompt_text))
    return messages


def _rag_prepare(question: str) -> tuple[list, list[dict]]:
    s = get_settings()
    q = (question or "").strip()
    if not q:
        raise ValueError("Question must not be empty")

    docs = similarity_search(q)
    context = _format_context(docs)
    template = PromptTemplate.from_template(s.rag.prompt_template)
    prompt_text = template.format(context=context, question=q)
    sys_msg = (s.llm.system_message or "").strip()
    messages = _messages_for_prompt(prompt_text, sys_msg)
    sources = _sources_from_docs(docs)
    return messages, sources


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


def answer_question(question: str) -> tuple[str, list[dict]]:
    messages, sources = _rag_prepare(question)
    llm = get_llm()
    response = llm.invoke(messages)
    text = _invoke_answer_text(response)
    q = (question or "").strip()
    logger.info(
        "rag_query_complete",
        extra={"question_len": len(q), "sources": len(sources)},
    )
    return text, sources


async def stream_answer(question: str) -> AsyncIterator[dict[str, Any]]:
    """Yield SSE-friendly dicts: sources, then token deltas, then done or error."""
    messages, sources = await asyncio.to_thread(_rag_prepare, question)
    yield {"type": "sources", "chunks": sources}

    q = (question or "").strip()
    try:
        llm = get_llm()
        async for chunk in llm.astream(messages):
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

    async def answer(self, question: str) -> tuple[str, list[dict]]:
        return await asyncio.to_thread(answer_question, question)

    async def stream(self, question: str) -> AsyncIterator[dict[str, Any]]:
        async for item in stream_answer(question):
            yield item
