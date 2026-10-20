"""Sport-specific guides: shown only for their sport, shared guides for every sport."""

from __future__ import annotations

import pytest

from app.api.dependencies import get_rag_pipeline
from app.knowledge import service as knowledge_store
from app.knowledge.parser import GuideError, parse_guide
from app.main import app
from app.services import app_chat
from tests.test_app_chat_isolation import DENMARK, auth, kb  # noqa: F401  (kb is a fixture)
from tests.test_multilingual import ScriptedPipeline

ROUTE = "tms/event-settings/game-play/:event_id"

BASE = f"""---
doc_id: tms.event-settings.game-play
title: Game Play settings page
routes: ["{ROUTE}"]
tenants: all
suggested_questions: ["How do I save game play settings?"]
---
## Game Play settings page: saving

Click Update to save the game play settings of the event.
"""

TABLE_TENNIS = f"""---
doc_id: tms.event-settings.game-play.table-tennis
title: Game Play settings – Table Tennis
routes: ["{ROUTE}"]
tenants: all
sports: [table_tennis, badminton]
suggested_questions: ["What is a sudden death point?"]
---
## Table Tennis scoring: sudden death point

Sudden Death Point ends a prolonged deuce at the Max Point.
"""

PADEL = f"""---
doc_id: tms.event-settings.game-play.padel-tennis
title: Game Play settings – Padel and Tennis
routes: ["{ROUTE}"]
tenants: all
sports: [padel, tennis]
suggested_questions: ["What is a golden point?"]
---
## Padel scoring: golden point

At 40-40 the next point wins the game when Golden Point System is chosen.
"""


@pytest.fixture()
def sport_kb(kb):  # noqa: F811
    for guide in (BASE, TABLE_TENNIS, PADEL):
        knowledge_store.ingest_guide(guide)
    return kb


def test_sport_ids_map_to_codes():
    assert app_chat.sport_from_id(1) == "table_tennis"
    assert app_chat.sport_from_id(2) == "padel"
    assert app_chat.sport_from_id(3) == "tennis"
    assert app_chat.sport_from_id(4) == "badminton"
    assert app_chat.sport_from_id(99) is None
    assert app_chat.sport_from_id(None) is None


def test_unknown_sport_in_front_matter_is_rejected():
    with pytest.raises(GuideError):
        parse_guide(TABLE_TENNIS.replace("badminton", "cricket"))
    meta, _ = parse_guide(PADEL)
    assert meta.sports == ("padel", "tennis")


@pytest.mark.parametrize(
    ("sport", "expected"),
    [
        ("table_tennis", {"tms.event-settings.game-play", "tms.event-settings.game-play.table-tennis"}),
        ("badminton", {"tms.event-settings.game-play", "tms.event-settings.game-play.table-tennis"}),
        ("padel", {"tms.event-settings.game-play", "tms.event-settings.game-play.padel-tennis"}),
        (None, {"tms.event-settings.game-play"}),
    ],
)
def test_screen_guides_follow_the_sport(sport_kb, sport, expected):
    ids = knowledge_store.guides_for_screen(DENMARK, ROUTE, sport=sport)
    assert set(ids) == expected
    # The shared guide names the screen; sport guides come first.
    assert ids[-1] == "tms.event-settings.game-play"


def test_other_sports_chunks_never_retrieved(sport_kb):
    hits = knowledge_store.search(DENMARK, "golden point at 40-40", sport="table_tennis")
    assert all(h.doc_id != "tms.event-settings.game-play.padel-tennis" for h in hits)
    hits = knowledge_store.search(DENMARK, "golden point at 40-40", sport="padel")
    assert any(h.doc_id == "tms.event-settings.game-play.padel-tennis" for h in hits)


def test_screen_info_uses_base_title_and_sport_questions(sport_kb):
    info = knowledge_store.screen_info(DENMARK, ROUTE, sport="padel")
    assert info["title"] == "Game Play settings page"
    assert "What is a golden point?" in info["suggested_questions"]
    assert "What is a sudden death point?" not in info["suggested_questions"]


def test_prompt_names_the_sport():
    assert "The organisation's sport is: Padel." in app_chat.prompt_for("Game Play settings page", None, "padel")
    assert "The organisation's sport is: not specified." in app_chat.prompt_for("x", None, None)


def test_sport_id_reaches_the_prompt_and_screen_endpoint(sport_kb):
    from fastapi.testclient import TestClient

    pipeline = ScriptedPipeline(["Ok."])
    app.dependency_overrides[get_rag_pipeline] = lambda: pipeline
    try:
        client = TestClient(app)
        body = {"question": "What is a golden point?", "screen": {"route": ROUTE}, "sport_id": 2}
        r = client.post("/api/app-chat", json=body, headers={"accept": "application/json", **auth()})
        assert r.status_code == 200
        assert "The organisation's sport is: Padel." in pipeline.prompts[0]

        r = client.get("/api/knowledge/screen", params={"route": ROUTE, "sport_id": 1}, headers=auth())
        assert "What is a sudden death point?" in r.json()["suggested_questions"]
    finally:
        app.dependency_overrides.clear()
