"""Screen-aware retrieval for the admin-app chat."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.config.settings import get_settings
from app.knowledge import service as knowledge
from app.services.auth import CallerScope
from app.knowledge.service import Hit
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Questions that only make sense as "explain the screen I am looking at".
_VAGUE_RE = re.compile(
    r"\b(this|here|current)\s+(page|screen|step|form|section)\b"
    r"|^\s*(help|what can i do|how does (this|it) work|what is this)\b",
    re.IGNORECASE,
)


@dataclass
class Retrieval:
    hits: list[Hit] = field(default_factory=list)
    screen_title: str = ""
    screen_doc_ids: list[str] = field(default_factory=list)
    # named | screen | fallback | overview | none
    mode: str = "none"

    @property
    def context(self) -> str:
        return "\n\n".join(
            f'Passage from the guide of the screen "{h.title}":\n{h.content}'
            for h in self.hits
        )

    @property
    def sources(self) -> list[dict]:
        # Guide title and section only: no file paths or tenant names.
        return [
            {
                "filename": h.title,
                "source": h.section,
                "chunk_index": i,
                "content": h.content,
            }
            for i, h in enumerate(self.hits)
        ]


def _within(hits: list[Hit], limit: float) -> list[Hit]:
    return [h for h in hits if h.distance <= limit]


def _if_relevant(hits: list[Hit], limit: float) -> list[Hit]:
    """All hits when the best one is close enough, else none.

    Used for a single screen's guide: once the guide is relevant, its other
    passages are useful context even when they score below the limit.
    """
    return hits if hits and hits[0].distance <= limit else []


def retrieve(
    scope: CallerScope,
    question: str,
    route: str | None,
    url: str | None,
) -> Retrieval:
    """Named screen first, then the current screen, then every guide in scope."""
    screen_ids = knowledge.guides_for_screen(scope, route, url)
    info = knowledge.screen_info(scope, route, url)
    result = Retrieval(
        screen_title=(info or {}).get("title", ""),
        screen_doc_ids=screen_ids,
    )

    cfg = get_settings().app_chat

    named = [d for d in knowledge.guides_named_in(scope, question) if d not in screen_ids]
    if named:
        hits = _if_relevant(knowledge.search(scope, question, doc_ids=named), cfg.screen_max_distance)
        if hits:
            result.hits, result.mode = hits, "named"
            return result

    on_screen = (
        _if_relevant(knowledge.search(scope, question, doc_ids=screen_ids), cfg.screen_max_distance)
        if screen_ids
        else []
    )
    elsewhere = [
        h
        for h in _within(knowledge.search(scope, question), cfg.max_distance)
        if h.doc_id not in screen_ids
    ]
    # The current screen wins unless another screen's guide is clearly closer.
    if on_screen and not (
        elsewhere and elsewhere[0].distance + cfg.other_screen_margin < on_screen[0].distance
    ):
        result.hits, result.mode = on_screen, "screen"
        return result
    if elsewhere:
        result.hits, result.mode = elsewhere, "fallback"
        return result

    if screen_ids and _VAGUE_RE.search(question or ""):
        hits = knowledge.overview(scope, screen_ids)
        if hits:
            result.hits, result.mode = hits, "overview"
    return result


def prompt_for(screen_title: str) -> str:
    """Prompt template with the screen name filled in; {context}/{question} remain."""
    title = (screen_title or "not documented yet").replace("{", "(").replace("}", ")")
    return get_settings().app_chat.prompt_template.replace("{screen}", title)


def audit(scope: CallerScope, route: str | None, result: Retrieval) -> None:
    logger.info(
        "app_chat_audit | tenant=%s user=%s route=%s mode=%s docs=%s",
        scope.tenant,
        scope.user_id,
        route or "-",
        result.mode,
        ",".join(sorted({h.doc_id for h in result.hits})) or "-",
    )
