"""Retrieval rules in app.services.app_chat.retrieve.

All guides' passages are ranked together. The current screen gets a small boost and
guides named in the question get a larger one. Nothing gates the other guides.
"""

from __future__ import annotations

from app.knowledge.service import Hit
from app.services import app_chat
from app.services.auth import CallerScope

SCOPE = CallerScope(tenant="denmark", user_id="u1")
ROUTE = "tms/event-settings/game-play/:event_id"


def _hit(doc_id: str, distance: float, tenant_specific: bool = False) -> Hit:
    return Hit(doc_id=doc_id, title=doc_id, section="s", content=doc_id,
               distance=distance, tenant_specific=tenant_specific)


def _fake_knowledge(monkeypatch, everywhere: list[Hit], named: list[str] | None = None) -> None:
    k = app_chat.knowledge
    monkeypatch.setattr(k, "guides_for_screen", lambda *a, **kw: ["game-play"])
    monkeypatch.setattr(k, "screen_info", lambda *a, **kw: {"title": "Game Play"})
    monkeypatch.setattr(k, "guides_named_in", lambda *a, **kw: list(named or []))
    monkeypatch.setattr(k, "search", lambda scope, query, **kw: sorted(everywhere, key=lambda h: h.distance))


def test_clearly_closer_other_guide_wins_over_current_screen(monkeypatch):
    _fake_knowledge(monkeypatch, [_hit("game-play", 0.30), _hit("playing-order", 0.20)])
    result = app_chat.retrieve(SCOPE, "intervals between games", ROUTE, None)
    assert result.mode == "fallback"
    assert result.hits[0].doc_id == "playing-order"


def test_current_screen_wins_a_near_tie(monkeypatch):
    # Adjusted scores: game-play 0.30 - 0.03 = 0.27, playing-order 0.29.
    _fake_knowledge(monkeypatch, [_hit("game-play", 0.30), _hit("playing-order", 0.29)])
    result = app_chat.retrieve(SCOPE, "intervals between games", ROUTE, None)
    assert result.mode == "screen"
    assert result.hits[0].doc_id == "game-play"


def test_named_guide_wins_a_close_call(monkeypatch):
    # Adjusted scores: game-play 0.27, payment 0.26 - 0.05 = 0.21.
    _fake_knowledge(monkeypatch, [_hit("game-play", 0.30), _hit("payment", 0.26)], named=["payment"])
    result = app_chat.retrieve(SCOPE, "error payment settings are required", ROUTE, None)
    assert result.mode == "named"
    assert result.hits[0].doc_id == "payment"


def test_best_current_screen_passage_stays_in_context(monkeypatch):
    own = _hit("game-play", 0.30)
    others = [_hit("referee", 0.25), _hit("umpire", 0.26), _hit("print", 0.27), _hit("draw", 0.275),
              _hit("seeding", 0.28), _hit("results", 0.285)]
    _fake_knowledge(monkeypatch, [*others, own])
    result = app_chat.retrieve(SCOPE, "why is the add button greyed out", ROUTE, None)
    assert "game-play" in [h.doc_id for h in result.hits]
    assert len(result.hits) <= app_chat.get_settings().app_chat.top_k


def test_tenant_specific_passage_goes_first(monkeypatch):
    _fake_knowledge(monkeypatch, [_hit("game-play", 0.25), _hit("game-play.tenant", 0.27, tenant_specific=True)])
    result = app_chat.retrieve(SCOPE, "intervals between games", ROUTE, None)
    assert result.hits[0].doc_id == "game-play.tenant"


def test_single_generic_word_does_not_name_a_guide(monkeypatch):
    from app.knowledge import service

    guides = {
        "tms.event-settings.print-settings": {"title": "Print Settings page", "aliases": ["print"]},
        "tms.printing": {"title": "Printing page", "aliases": ["print queue"]},
    }
    monkeypatch.setattr(service, "visible_guides", lambda *a, **kw: guides)
    assert service.guides_named_in(SCOPE, "print the match sheets") == []
    assert service.guides_named_in(SCOPE, "what is on the print queue") == ["tms.printing"]


def test_most_general_guide_names_the_screen_whatever_the_load_order(monkeypatch):
    from app.knowledge import service

    route = "tms/players/:event_id"
    guides = {
        "tms.players.club-association": {"routes": [route], "title": "Players page – Club columns"},
        "tms.players": {"routes": [route], "title": "Players page"},
        "tms.players.adding": {"routes": [route], "title": "Players page – adding"},
    }
    monkeypatch.setattr(service, "visible_guides", lambda *a, **kw: guides)
    ids = service.guides_for_screen(SCOPE, route)
    assert ids[-1] == "tms.players"
    assert service.screen_info(SCOPE, route)["title"] == "Players page"


# ---------- hybrid search, rerank and question rewrite ----------

from dataclasses import replace

from app.knowledge.keyword_index import KeywordIndex, tokens


def _settings(monkeypatch, **values):
    cfg = app_chat.get_settings().app_chat
    for key, value in values.items():
        monkeypatch.setattr(cfg, key, value)


def test_keyword_index_finds_the_exact_label():
    index = KeywordIndex([
        ("c1", "registration", "Registration Fee and refund settings of a category"),
        ("c2", "payment", "Payment & Invoice step: invoice details, payment gateway and tax"),
        ("c3", "scoring", "Streaming tab: Enable Streaming turns streaming on for a match"),
    ])
    found = index.search("how do I set up the payment gateway", {"c1", "registration", "payment", "scoring"}, 5)
    assert found[0].doc_id == "payment"
    assert index.search("enable streaming", {"registration"}, 5) == []  # other guides are not readable
    assert "the" not in tokens("the matches") and "match" in tokens("the matches")


def test_keyword_match_wins_a_near_tie(monkeypatch):
    # Adjusted: game-play 0.30 - 0.03 = 0.27; payment 0.29 - 0.03 (best keyword match) = 0.26.
    payment = replace(_hit("payment", 0.29), keyword_rank=0)
    _fake_knowledge(monkeypatch, [_hit("game-play", 0.30), payment])
    _settings(monkeypatch, keyword_boost=0.03, rerank=False)
    result = app_chat.retrieve(SCOPE, "payment gateway", ROUTE, None)
    assert result.hits[0].doc_id == "payment"


def test_reranker_order_replaces_the_embedding_order(monkeypatch):
    _fake_knowledge(monkeypatch, [_hit("referee", 0.25), _hit("printing", 0.33)])
    _settings(monkeypatch, rerank=True, rerank_scale=10.0)
    monkeypatch.setattr(app_chat.reranker, "scores",
                        lambda q, passages: [-8.0 if p == "referee" else 2.0 for p in passages])
    result = app_chat.retrieve(SCOPE, "print the score sheets", ROUTE, None)
    assert result.hits[0].doc_id == "printing"


def test_unavailable_reranker_keeps_the_embedding_order(monkeypatch):
    _fake_knowledge(monkeypatch, [_hit("referee", 0.25), _hit("printing", 0.33)])
    _settings(monkeypatch, rerank=True)
    monkeypatch.setattr(app_chat.reranker, "scores", lambda q, passages: None)
    result = app_chat.retrieve(SCOPE, "print the score sheets", ROUTE, None)
    assert result.hits[0].doc_id == "referee"


def test_weak_question_is_rewritten_and_searched_again(monkeypatch):
    k = app_chat.knowledge
    monkeypatch.setattr(k, "guides_for_screen", lambda *a, **kw: ["game-play"])
    monkeypatch.setattr(k, "screen_info", lambda *a, **kw: {"title": "Game Play"})
    monkeypatch.setattr(k, "guides_named_in", lambda *a, **kw: [])
    by_query = {"event live nahi ho raha": [], "publish the event": [_hit("create-event", 0.30)]}
    monkeypatch.setattr(k, "search", lambda scope, query, **kw: by_query.get(query, []))
    monkeypatch.setattr(app_chat.query_rewrite, "rewrite", lambda q: "publish the event")
    _settings(monkeypatch, rewrite_weak_questions=True, rerank=False)
    result = app_chat.retrieve(SCOPE, "event live nahi ho raha", ROUTE, None)
    assert result.hits[0].doc_id == "create-event"
    assert result.rewritten == "publish the event"


def test_strong_question_is_not_rewritten(monkeypatch):
    _fake_knowledge(monkeypatch, [_hit("game-play", 0.30)])
    _settings(monkeypatch, rewrite_weak_questions=True, rewrite_above=0.47, rerank=False)
    calls = []
    monkeypatch.setattr(app_chat.query_rewrite, "rewrite", lambda q: calls.append(q) or "x")
    app_chat.retrieve(SCOPE, "intervals between games", ROUTE, None)
    assert calls == []


def test_passages_say_where_their_screen_is():
    from app.services.app_chat import Retrieval

    r = Retrieval(hits=[_hit("tms.event-settings.create-event", 0.3), _hit("tms.fixture.templates", 0.3)],
                  screen_doc_ids=["tms.event-settings.create-event"])
    own, other = r.context.split("\n\n")
    assert "This is the screen the user is on." in own
    assert "open Fixtures/Results from the sidebar" in other
    assert "This is NOT the screen the user is on." in other


def test_prompt_uses_the_screen_name_only():
    prompt = app_chat.prompt_for("Event Details page --- Organiser Guide and Troubleshooting")
    assert "on the screen: Event Details page.\n" in prompt
