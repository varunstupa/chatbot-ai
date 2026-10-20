"""Rewrites a question that found nothing into a short English search query.

Only used when retrieval is weak (no passage within the limits, or only distant ones),
so ordinary questions pay no extra model call. Helps with mixed-language or very casual
wording ("event live nahi ho raha") that the embedding model matches poorly.
"""

from __future__ import annotations

import re

from app.utils.logger import get_logger

logger = get_logger(__name__)

_PROMPT = (
    "Rewrite the user's question as one short English search query for the help guides of "
    "a sports event management system (events, registration, players, fixtures, schedule, "
    "scoring and streaming, printing, rankings, display settings, leaderboard). Use the "
    "names of screens, buttons and settings the user most likely means. Output only the "
    "query, with no explanation and no quotes.\n\nQuestion: {question}\nQuery:"
)


def rewrite(question: str) -> str | None:
    """English search query for the question; None when the model fails or returns nothing useful."""
    from app.services.rag_pipeline import get_utility_llm

    try:
        reply = get_utility_llm().invoke(_PROMPT.format(question=question))
    except Exception:
        logger.exception("query_rewrite_failed")
        return None
    text = getattr(reply, "content", reply)
    if isinstance(text, list):
        text = " ".join(str(part.get("text", "")) if isinstance(part, dict) else str(part) for part in text)
    text = re.sub(r"<think>.*?</think>", "", str(text or ""), flags=re.DOTALL)
    line = next((ln.strip() for ln in text.splitlines() if ln.strip()), "")
    line = line.strip("\"'` ").removeprefix("Query:").strip()
    if not line or len(line) > 200 or line.casefold() == question.strip().casefold():
        return None
    return line


_TOPIC_PROMPT = (
    "You help users of a sports event management system. Its modules are: events and event "
    "settings (registration, payment and invoices, draw settings, game play, umpires, referees, "
    "day planner, accommodation, travel, print settings, access control, documents and sponsors), "
    "players, fixtures and results, schedule, scoring and streaming, awards and standings, "
    "printing, rankings, display settings, leaderboard, export and share results, request "
    "management and notifications.\n"
    "A question about how a feature of this system works inside (its API, endpoint, backend, "
    "database or logic) IS about the system: rewrite it as the user's task on the screen, for "
    "example 'which API creates an event' -> 'How do I create an event?'.\n"
    "If the question is not about this system (general knowledge, programming exercises, "
    "other products, chit-chat), reply exactly OFF_TOPIC.\n"
    "Otherwise rewrite it as one short, correctly spelled English question about the system. "
    "Keep the user's own words for the feature, and do not add phrases such as 'in this system'. "
    "Output only that question.\n\nQuestion: {question}\nReply:"
)
_OFF_TOPIC_RE = re.compile(r"\bOFF[\s_-]*TOPIC\b", re.IGNORECASE)
# Requests for code are never about using the system; no model call is needed for them.
_CODE_REQUEST_RE = re.compile(
    r"\b(python|java(script)?|c\+\+|c#|sql|code|script|program(ming)?|algorithm|function|regex|leetcode)\b",
    re.IGNORECASE,
)


def module_question(question: str) -> str | None:
    """The question as plain English when it is about the system's modules; None when off-topic."""
    if _CODE_REQUEST_RE.search(question or ""):
        return None
    from app.services.rag_pipeline import get_utility_llm

    try:
        reply = get_utility_llm().invoke(_TOPIC_PROMPT.format(question=question))
    except Exception:
        logger.exception("topic_check_failed")
        return None
    text = getattr(reply, "content", reply)
    if isinstance(text, list):
        text = " ".join(str(part.get("text", "")) if isinstance(part, dict) else str(part) for part in text)
    text = re.sub(r"<think>.*?</think>", "", str(text or ""), flags=re.DOTALL)
    if _OFF_TOPIC_RE.search(text):
        return None
    line = next((ln.strip() for ln in text.splitlines() if ln.strip()), "")
    line = line.strip("\"'` ").removeprefix("Reply:").strip()
    return line if 0 < len(line) <= 200 else None
