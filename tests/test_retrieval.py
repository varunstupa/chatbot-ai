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


# ---------- dynamic prompt ----------

import pytest


@pytest.mark.parametrize("question, kind", [
    ("How can we enable streaming?", "how-to"),
    ("Why can't I publish my event?", "problem"),
    ("Event live nahi ho raha, kya karun?", "problem"),
    ("Where is the players page?", "where-is"),
    ("Which modules are in the sidebar?", "list"),
    ("What are the predefined fixture templates?", "list"),
    ("What does MA mean?", "what-is"),
    ("Thanks", "general"),
])
def test_question_type(question, kind):
    assert app_chat.question_type(question) == kind


def test_location_sentence():
    assert app_chat.location_sentence("tms.fixture.templates") == (
        "This is on the Fixtures/Results page: open Fixtures/Results from the sidebar."
    )
    assert app_chat.location_sentence("unknown.guide") == ""


def test_dynamic_prompt_keeps_the_core_and_only_the_type_rules(monkeypatch):
    _settings(monkeypatch, dynamic_prompt=True)
    prompt = app_chat.prompt_for("Event Details page", None, None, question="Where is the players page?")
    assert "reply with exactly NO_ANSWER" in prompt and "never write code" in prompt
    assert "The user asks where something is." in prompt
    assert "This is a how-to question." not in prompt
    assert "{context}" in prompt and "{question}" in prompt


def test_static_prompt_when_dynamic_is_off(monkeypatch):
    _settings(monkeypatch, dynamic_prompt=False)
    prompt = app_chat.prompt_for("Event Details page", None, None, question="Where is the players page?")
    assert "The user asks where something is." not in prompt


def test_answer_location_line_only_for_another_screen(monkeypatch):
    from app.services.app_chat import Retrieval

    _settings(monkeypatch, dynamic_prompt=True)
    other = Retrieval(hits=[_hit("tms.fixture.templates", 0.3)], screen_doc_ids=["tms.event-settings.create-event"])
    assert other.context.startswith("The user is already told: This is on the Fixtures/Results page")
    assert other.location_prefix == "This is on the Fixtures/Results page: open Fixtures/Results from the sidebar."
    own = Retrieval(hits=[_hit("tms.event-settings.create-event", 0.3)], screen_doc_ids=["tms.event-settings.create-event"])
    assert "already told" not in own.context and own.location_prefix == ""


def test_passage_that_names_another_module_sets_the_location(monkeypatch):
    from app.knowledge.service import Hit
    from app.services.app_chat import Retrieval

    _settings(monkeypatch, dynamic_prompt=True)
    streaming = Hit(doc_id="tms.fixture.scoring", title="Scoring", section="Streaming", distance=0.3,
                    tenant_specific=False,
                    content="To reach it, open **Scoring and Streaming** from the sidebar and click the Streaming tab.")
    r = Retrieval(hits=[streaming], screen_doc_ids=["tms.event-settings.create-event"])
    assert r.location_prefix == "This is on the Scoring and Streaming page: open Scoring and Streaming from the sidebar."


def test_instruction_sections_are_not_indexed():
    from app.knowledge.parser import build_chunks, content_hash, parse_guide

    text = (
        "---\ndoc_id: tms.x\ntitle: X page\nroutes: [tms/x]\ntenants: all\n---\n"
        "## Overview\n\nThe X page.\n\n### Guidance for the assistant\n\nAnswer briefly.\n\n"
        "## When to ask a follow-up question\n\nAsk when unclear.\n\n## Publish\n\nUse the toggle.\n"
    )
    meta, body = parse_guide(text)
    skip = frozenset({"assistant", "when to ask a follow-up question"})
    chunks = build_chunks(meta, body, content_hash(meta, body, skip), chunk_size=1500, chunk_overlap=0,
                          skip_sections=skip)
    texts = " ".join(c.text for c in chunks)
    assert "The X page." in texts and "Use the toggle." in texts
    assert "Answer briefly" not in texts and "Ask when unclear" not in texts
    assert content_hash(meta, body, skip) != content_hash(meta, body)


# ---------- question routing ----------


def test_routed_answer_goes_first(monkeypatch):
    routed = replace(_hit("create-event", 0.31), chunk_id="faq-visible")
    _fake_knowledge(monkeypatch, [_hit("playing-order", 0.27), _hit("players", 0.29)])
    monkeypatch.setattr(app_chat.knowledge, "route_question", lambda *a, **kw: [routed])
    result = app_chat.retrieve(SCOPE, "Why is my event not visible to players?", ROUTE, None)
    assert result.routed and result.hits[0] is routed
    assert len(result.hits) <= app_chat.get_settings().app_chat.top_k


def test_no_route_keeps_the_ranking(monkeypatch):
    _fake_knowledge(monkeypatch, [_hit("game-play", 0.30)])
    monkeypatch.setattr(app_chat.knowledge, "route_question", lambda *a, **kw: [])
    result = app_chat.retrieve(SCOPE, "intervals between games", ROUTE, None)
    assert not result.routed and result.hits[0].doc_id == "game-play"


def test_faq_entry_is_found_for_a_suggested_question():
    from app.knowledge.service import _faq_chunk

    chunks = [
        ("Event page\n\n**Why are all fields greyed out?** Click Edit.", {"chunk_id": "a"}),
        ("Event page\n\n**Why is my event not visible to players?** Publish it.", {"chunk_id": "b"}),
    ]
    assert _faq_chunk("Why is my event not visible to players?", chunks) == "b"
    assert _faq_chunk("How do I add a hotel?", chunks) is None


def test_where_only_guide_is_not_routed_for_a_how_to_question(monkeypatch):
    nav = replace(_hit("tms.navigation", 0.31), chunk_id="nav-payment")
    _fake_knowledge(monkeypatch, [_hit("payment-invoice", 0.30)])
    monkeypatch.setattr(app_chat.knowledge, "route_question", lambda *a, **kw: [nav])
    how_to = app_chat.retrieve(SCOPE, "How do I set up payment methods?", ROUTE, None)
    assert not how_to.routed and how_to.hits[0].doc_id == "payment-invoice"
    where = app_chat.retrieve(SCOPE, "Where do I set up payment and invoices?", ROUTE, None)
    assert where.routed and where.hits[0].doc_id == "tms.navigation"


def test_hindi_in_english_letters_is_always_searched_in_english(monkeypatch):
    k = app_chat.knowledge
    monkeypatch.setattr(k, "guides_for_screen", lambda *a, **kw: ["game-play"])
    monkeypatch.setattr(k, "screen_info", lambda *a, **kw: {"title": "Game Play"})
    monkeypatch.setattr(k, "guides_named_in", lambda *a, **kw: [])
    by_query = {"score sheet print karna hai": [_hit("score-stream", 0.25)],
                "How do I print a score sheet?": [_hit("printing", 0.30)]}
    monkeypatch.setattr(k, "search", lambda scope, query, **kw: by_query.get(query, []))
    monkeypatch.setattr(app_chat.query_rewrite, "rewrite", lambda q: "How do I print a score sheet?")
    _settings(monkeypatch, rewrite_weak_questions=True, rerank=False)
    result = app_chat.retrieve(SCOPE, "score sheet print karna hai", ROUTE, None)
    assert result.rewritten and result.hits[0].doc_id == "printing"
