"""Screen-aware retrieval for the admin-app chat."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.config.settings import get_settings
from app.knowledge import service as knowledge
from app.services import query_rewrite, reranker
from app.services.auth import CallerScope
from app.services.language import QuestionLanguage
from app.knowledge.parser import SPORTS_BY_ID
from app.knowledge.service import Hit
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Questions that only make sense as "explain the screen I am looking at".
_VAGUE_RE = re.compile(
    r"\b(this|here|current)\s+(page|screen|step|form|section)\b"
    r"|^\s*(help|what can i do|how does (this|it) work|what is this)\b",
    re.IGNORECASE,
)


def screen_location(doc_id: str) -> str:
    """Where the guide's screen is in the app ("the Players page (open Players from the sidebar)")."""
    locations = get_settings().app_chat.screen_locations
    best = ""
    for prefix in locations:
        if (doc_id == prefix or doc_id.startswith(prefix + ".")) and len(prefix) > len(best):
            best = prefix
    return locations.get(best, "")


@dataclass
class Retrieval:
    hits: list[Hit] = field(default_factory=list)
    screen_title: str = ""
    screen_doc_ids: list[str] = field(default_factory=list)
    # named | screen | fallback | overview | none
    mode: str = "none"
    # The English search query used instead of the question, when the question found too little.
    rewritten: str = ""

    @property
    def context(self) -> str:
        on_screen = set(self.screen_doc_ids)
        blocks = []
        for h in self.hits:
            header = f'Passage from the guide "{h.title}".'
            where = screen_location(h.doc_id)
            if where:
                header += f" Where it is in the app: {where}."
            if h.doc_id in on_screen:
                header += " This is the screen the user is on."
            elif where:
                header += " This is NOT the screen the user is on."
            blocks.append(f"{header}\n{h.content}")
        return "\n\n".join(blocks)

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


def _keep_screen_best(hits: list[Hit], screen_best: Hit, top_k: int) -> list[Hit]:
    """The top_k closest hits, always including the current screen's best passage."""
    ranked = sorted(hits, key=lambda h: h.distance)[:top_k]
    if screen_best not in ranked:
        ranked = sorted(ranked[: top_k - 1] + [screen_best], key=lambda h: h.distance)
    return ranked


def _rank(
    scope: CallerScope,
    question: str,
    on_screen: set[str],
    named: set[str],
    sport: str | None,
) -> list[Hit]:
    """Passages from every guide ranked together, best first, at most top_k."""
    cfg = get_settings().app_chat
    candidates: list[Hit] = []
    for hit in knowledge.search(scope, question, sport=sport, limit=cfg.candidate_pool):
        limit = cfg.screen_max_distance if hit.doc_id in on_screen else cfg.max_distance
        if hit.distance <= limit:
            candidates.append(hit)

    def boosted(base: float, hit: Hit) -> float:
        if hit.doc_id in on_screen:
            base -= cfg.screen_boost
        if hit.doc_id in named:
            base -= cfg.topic_boost
        if hit.keyword_rank is not None:
            base -= cfg.keyword_boost / (1 + hit.keyword_rank)
        return base

    scored = [(boosted(hit.distance, hit), hit) for hit in candidates]
    if cfg.rerank and scored:
        # The cross-encoder reorders the best candidates; its score stands in for the distance.
        scored = sorted(scored, key=lambda item: item[0])[: cfg.rerank_pool]
        relevance = reranker.scores(question, [hit.content for _, hit in scored])
        if relevance is not None:
            scored = [(boosted(-r / cfg.rerank_scale, hit), hit) for r, (_, hit) in zip(relevance, scored)]
    # A relevant tenant-specific passage goes first, as search() orders them; then the boosted score.
    scored.sort(
        key=lambda item: (
            0 if item[1].tenant_specific and item[1].distance <= cfg.screen_max_distance else 1,
            item[0],
        )
    )
    hits = [hit for _, hit in scored[: cfg.top_k]]
    # The best passage from the user's own screen always stays in the context.
    best_on_screen = next((hit for _, hit in scored if hit.doc_id in on_screen), None)
    if hits and best_on_screen is not None and best_on_screen not in hits:
        hits = hits[: max(cfg.top_k - 1, 1)] + [best_on_screen]
    return hits


def _weak(hits: list[Hit]) -> bool:
    return not hits or min(h.distance for h in hits) > get_settings().app_chat.rewrite_above


def retrieve(
    scope: CallerScope,
    question: str,
    route: str | None,
    url: str | None,
    sport: str | None = None,
) -> Retrieval:
    """Rank passages from every guide together; the current screen and named guides get a boost."""
    screen_ids = knowledge.guides_for_screen(scope, route, url, sport)
    info = knowledge.screen_info(scope, route, url, sport)
    result = Retrieval(
        screen_title=(info or {}).get("title", ""),
        screen_doc_ids=screen_ids,
    )
    cfg = get_settings().app_chat
    on_screen = set(screen_ids)
    named = set(knowledge.guides_named_in(scope, question, sport))
    hits = _rank(scope, question, on_screen, named, sport)

    if cfg.rewrite_weak_questions and _weak(hits) and not _VAGUE_RE.search(question or ""):
        query = query_rewrite.rewrite(question)
        if query:
            named_too = named | set(knowledge.guides_named_in(scope, query, sport))
            again = _rank(scope, query, on_screen, named_too, sport)
            if again and (not hits or min(h.distance for h in again) < min(h.distance for h in hits)):
                hits, named, result.rewritten = again, named_too, query
                logger.info("app_chat_rewrite | used | query=%s", query)

    if hits:
        top = hits[0].doc_id
        result.hits = hits
        if top in on_screen:
            result.mode = "screen"
        elif top in named:
            result.mode = "named"
        else:
            result.mode = "fallback"
        return result

    if screen_ids and _VAGUE_RE.search(question or ""):
        overview_hits = knowledge.overview(scope, screen_ids, sport=sport)
        if overview_hits:
            result.hits, result.mode = overview_hits, "overview"
    return result


NO_ANSWER = "NO_ANSWER"
_NO_ANSWER_RE = re.compile(r"^\W*no[\s_-]*answer\b", re.IGNORECASE)
# Later in the answer only the exact marker counts, so "no answer" in prose does not.
_NO_ANSWER_ANYWHERE_RE = re.compile(r"\bNO_ANSWER\b")

# Internal detail the admin chat must never show: an HTTP method with a path, API
# paths (.../v1/...), API URLs, code fences and code statements. HTTP methods are
# matched in upper case only, so ordinary words such as "patch" are not caught.
_INTERNAL_DETAIL_RE = re.compile(
    r"\b(?:GET|POST|PUT|PATCH|DELETE)\s+[`'\"]?[a-z0-9_\-{}:.]+/[a-z0-9_\-{}:/.]+"
    r"|/v\d+/"
    r"|\bv\d+/[a-z_\-]+/"
    r"|https?://[^\s)]*/(?:api|v\d+)/"
    r"|```"
    r"|\bcurl\s+-"
    r"|\bdef\s+\w+\s*\("
    r"|^\s*import\s+\w+\s*$"
    r"|\bfunction\s+\w+\s*\("
    r"|\bconsole\.log\b"
    r"|\bapi\s+(?:endpoint|route|path|url)\b",
    re.IGNORECASE | re.MULTILINE,
)


def reveals_internal_detail(text: str) -> bool:
    """True when an answer names an API, endpoint or URL path, or contains code."""
    return bool(_INTERNAL_DETAIL_RE.search(text or ""))


_SPORT_NAMES = {
    "table_tennis": "Table Tennis",
    "padel": "Padel",
    "tennis": "Tennis",
    "badminton": "Badminton",
}


def sport_from_id(sport_id: int | None) -> str | None:
    """The admin app's sport_id as a guide sport code; unknown ids give None."""
    return SPORTS_BY_ID.get(sport_id) if sport_id is not None else None


def prompt_for(
    screen_title: str, language: QuestionLanguage | None = None, sport: str | None = None
) -> str:
    """Prompt template with screen, answer language and sport filled in; {context}/{question} remain."""
    # The screen name only: "Event Details page --- Organiser Guide" -> "Event Details page".
    title = re.split(r"\s+(?:---|–|—)\s+", screen_title or "")[0].strip() or "not documented yet"
    title = title.replace("{", "(").replace("}", ")")
    answer_language = language.name if language else "the same language as the Question"
    return (
        get_settings().app_chat.prompt_template
        .replace("{screen}", title)
        .replace("{language}", answer_language)
        .replace("{sport}", _SPORT_NAMES.get(sport or "", "not specified"))
    )


def did_you_mean(
    scope: CallerScope,
    question: str,
    sport: str | None,
    language: QuestionLanguage | None,
) -> tuple[str, list[str]] | None:
    """For an unanswered question about the modules: a "Did you mean" reply and its questions.

    None for a question that is not about the modules (it gets the plain no-answer message)
    or when no suggested question is close to it.
    """
    cfg = get_settings().app_chat
    if cfg.suggest_count <= 0:
        return None
    english = query_rewrite.module_question(question)
    if not english:
        logger.info("app_chat_suggest | off-topic")
        return None
    items = knowledge.suggest_questions(scope, english, sport, cfg.suggest_count, exclude=question)
    logger.info("app_chat_suggest | query=%s suggestions=%s", english, len(items))
    if not items:
        return None
    intro = cfg.did_you_mean_messages.get(language.code if language else "", cfg.did_you_mean_message)
    return intro + "\n\n" + "\n".join(f"- {q}" for q in items), items


def no_answer_text(language: QuestionLanguage | None) -> str:
    cfg = get_settings().app_chat
    return cfg.no_answer_messages.get(language.code if language else "", cfg.no_answer_message)


def is_no_answer(text: str) -> bool:
    """The model's NO_ANSWER marker, also with stray formatting or text around it.

    Some models explain first ("The context does not mention ...") and put the
    marker last, so the marker anywhere in the answer counts.
    """
    text = text or ""
    return bool(_NO_ANSWER_RE.match(text) or _NO_ANSWER_ANYWHERE_RE.search(text))


def could_become_no_answer(text: str) -> bool:
    """While streaming: the text so far may still turn into the NO_ANSWER marker."""
    t = re.sub(r"^\W+", "", text or "").upper().replace(" ", "_").replace("-", "_")
    return NO_ANSWER.startswith(t[: len(NO_ANSWER)])


def audit(scope: CallerScope, route: str | None, result: Retrieval) -> None:
    logger.info(
        "app_chat_audit | tenant=%s user=%s route=%s mode=%s docs=%s rewritten=%s",
        scope.tenant,
        scope.user_id,
        route or "-",
        result.mode,
        ",".join(sorted({h.doc_id for h in result.hits})) or "-",
        "yes" if result.rewritten else "no",
    )
