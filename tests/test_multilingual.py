"""Answer language, localized no-answer text and the NO_ANSWER marker in JSON and SSE."""

from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_rag_pipeline
from app.config.settings import get_settings
from app.main import app
from app.services import app_chat
from app.services.language import QuestionLanguage, detect_language
from tests.test_app_chat_isolation import DETAILS_ROUTE, auth, kb  # noqa: F401  (kb is a fixture)

GERMAN = QuestionLanguage(code="de", name="German")
NO_ANSWER_DE = get_settings().app_chat.no_answer_messages["de"]


# ---------- language detection ----------


@pytest.mark.parametrize(
    ("question", "code", "name"),
    [
        ("Welche Größe sollte das Vorschaubild der Veranstaltung haben?", "de", "German"),
        ("एक मैच में कितने अंपायर असाइन किए जा सकते हैं?", "hi", "Hindi"),
        ("Hur många domare kan tilldelas en match?", "sv", "Swedish"),
        ("Kolik rozhodčích lze přiřadit k jednomu zápasu?", "cs", "Czech"),
        ("Kan jeg legge til en dommer manuelt?", "no", "Norwegian"),
        ("What size should the event thumbnail be?", "en", "English"),
    ],
)
def test_detects_question_language(question, code, name):
    assert detect_language(question) == QuestionLanguage(code=code, name=name)


def test_short_input_is_left_to_the_model():
    assert detect_language("ok") is None
    assert "the same language as the Question" in app_chat.prompt_for("Event Details page", None)


@pytest.mark.parametrize(
    "question",
    [
        "How do I forfeit a player?",
        "What happens to matches when I forfeit a player?",
        "How do I reset my Gmail password?",
    ],
)
def test_short_english_questions_are_never_another_language(question):
    # Low-accuracy detection alone read these as German, Italian etc.
    result = detect_language(question)
    assert result is None or result.code == "en"


def test_prompt_names_language_and_screen():
    prompt = app_chat.prompt_for("Event Details page", GERMAN)
    assert "Write the entire answer in German" in prompt
    assert "Event Details page" in prompt
    assert "{language}" not in prompt and "{screen}" not in prompt


def test_no_answer_text_falls_back_to_english():
    s = get_settings().app_chat
    assert app_chat.no_answer_text(GERMAN) == NO_ANSWER_DE
    assert app_chat.no_answer_text(QuestionLanguage("xx", "Unknown")) == s.no_answer_message
    assert app_chat.no_answer_text(None) == s.no_answer_message


# ---------- NO_ANSWER marker ----------


@pytest.mark.parametrize("text", ["NO_ANSWER", "  NO_ANSWER\n", "**NO_ANSWER**", "no answer.", "NO_ANSWER The guides…"])
def test_marker_variants_match(text):
    assert app_chat.is_no_answer(text)


@pytest.mark.parametrize("text", ["No, the thumbnail must be 379 x 200 px.", "Notification settings", "None"])
def test_real_answers_are_not_the_marker(text):
    assert not app_chat.is_no_answer(text)


def test_partial_marker_is_held_back():
    assert app_chat.could_become_no_answer("")
    assert app_chat.could_become_no_answer("\n NO_AN")
    assert not app_chat.could_become_no_answer("No,")
    assert not app_chat.could_become_no_answer("Notif")


# ---------- end to end through /api/app-chat ----------


class ScriptedPipeline:
    """Streams fixed tokens, as the LLM would after retrieval."""

    def __init__(self, tokens: list[str]) -> None:
        self.tokens = tokens
        self.prompts: list[str] = []

    async def answer(self, question, session_id, corpus="merged", *, prompt_template=None,
                     retriever=None, no_answer_text=None):
        self.prompts.append(prompt_template)
        return "".join(self.tokens), []

    async def stream(self, question, session_id, corpus="merged", *, prompt_template=None,
                     retriever=None, no_answer_text=None):
        self.prompts.append(prompt_template)
        yield {"type": "session", "session_id": session_id}
        yield {"type": "sources", "chunks": []}
        for t in self.tokens:
            yield {"type": "token", "text": t}
        yield {"type": "done"}


@pytest.fixture()
def scripted(kb):  # noqa: F811
    def make(tokens: list[str]) -> tuple[TestClient, ScriptedPipeline]:
        pipeline = ScriptedPipeline(tokens)
        app.dependency_overrides[get_rag_pipeline] = lambda: pipeline
        return TestClient(app), pipeline

    yield make
    app.dependency_overrides.clear()


def _ask(client: TestClient, question: str, *, stream: bool):
    body = {"question": question, "screen": {"route": DETAILS_ROUTE}}
    accept = "text/event-stream" if stream else "application/json"
    return client.post("/api/app-chat", json=body, headers={"accept": accept, **auth()})


def _streamed_text(response) -> tuple[str, dict]:
    events = [json.loads(line[6:]) for line in response.text.splitlines() if line.startswith("data: ")]
    text = "".join(e["text"] for e in events if e["type"] == "token")
    return text, next(e for e in events if e["type"] == "done")


GERMAN_QUESTION = "Wie wird das Wetter morgen in Berlin?"


@pytest.mark.parametrize("tokens", [["NO_ANSWER"], ["\n", "NO", "_ANS", "WER"], ["NO_ANSWER", " Die Anleitungen…"]])
def test_marker_is_replaced_in_stream(scripted, tokens):
    client, pipeline = scripted(tokens)
    text, done = _streamed_text(_ask(client, GERMAN_QUESTION, stream=True))
    assert text == NO_ANSWER_DE
    assert done.get("answer") == NO_ANSWER_DE
    assert "Write the entire answer in German" in pipeline.prompts[0]


def test_marker_is_replaced_in_json(scripted):
    client, _ = scripted(["NO_ANSWER"])
    assert _ask(client, GERMAN_QUESTION, stream=False).json()["answer"] == NO_ANSWER_DE


def test_normal_answer_streams_unchanged(scripted):
    tokens = ["No", ", das Vorschaubild", " muss 379 x 200 px groß sein."]
    client, _ = scripted(tokens)
    text, done = _streamed_text(_ask(client, "Welche Größe sollte das Vorschaubild haben?", stream=True))
    assert text == "".join(tokens)
    assert "answer" not in done


# ---------- marker after an explanation (qwen3.5 style) ----------

EXPLAINED = ["Der Kontext enthält keine Informationen", " über das Wetter.", "\n\n", "NO_ANSWER"]


def test_marker_after_text_matches():
    assert app_chat.is_no_answer("The context does not mention it.\n\nNO_ANSWER")
    # Only the exact marker counts later in the text, not prose.
    assert not app_chat.is_no_answer("Players with no answer to the invitation stay in the queue.")


def test_marker_after_text_is_replaced_in_stream(scripted):
    client, _ = scripted(EXPLAINED)
    _, done = _streamed_text(_ask(client, GERMAN_QUESTION, stream=True))
    # The explanation was already streamed; the final answer replaces it.
    assert done.get("answer") == NO_ANSWER_DE


def test_marker_after_text_is_replaced_in_json(scripted):
    client, _ = scripted(EXPLAINED)
    assert _ask(client, GERMAN_QUESTION, stream=False).json()["answer"] == NO_ANSWER_DE


def test_prompt_asks_for_bare_marker_and_same_screen_guides(scripted):
    client, pipeline = scripted(["NO_ANSWER"])
    _ask(client, GERMAN_QUESTION, stream=False)
    assert "NO_ANSWER and nothing else" in pipeline.prompts[0]
    assert "Never tell the user to go to the screen they are on" in pipeline.prompts[0]


# ---------- model settings ----------


def test_local_llm_has_thinking_off():
    from app.services import rag_pipeline

    llm = rag_pipeline._build_llm()
    if type(llm).__name__ == "ChatOllama":
        assert llm.reasoning is False


# ---------- guardrail on the stream ----------


def test_api_path_is_never_streamed(scripted):
    from app.services.language import detect_language

    question = "Which API saves the LED layout?"
    tokens = ["To save the layout the screen calls ", "PUT match", "/v1/update_led_settings", " on the server."]
    client, _ = scripted(tokens)
    text, done = _streamed_text(_ask(client, question, stream=True))
    assert "/v1/" not in text
    assert "PUT match" not in text
    assert done.get("answer") == app_chat.no_answer_text(detect_language(question))


# ---------- "Did you mean" for unanswered module questions ----------

SUGGESTED = ["How do I enable streaming for a match?", "Where do I find streaming?"]
DID_YOU_MEAN = "I couldn't find an exact answer to that. Did you mean:\n\n- " + "\n- ".join(SUGGESTED)


@pytest.fixture()
def suggests(monkeypatch):
    calls: list[str] = []

    def fake(scope, question, sport, language):
        calls.append(question)
        return DID_YOU_MEAN, list(SUGGESTED)

    monkeypatch.setattr(app_chat, "did_you_mean", fake)
    return calls


@pytest.mark.parametrize("tokens", [["NO_ANSWER"], ["I couldn't find that in the guides available to you."]])
def test_module_question_gets_did_you_mean_in_stream(scripted, suggests, tokens):
    client, _ = scripted(tokens)
    text, done = _streamed_text(_ask(client, "streming nhi chal raha", stream=True))
    assert text == DID_YOU_MEAN
    assert done["answer"] == DID_YOU_MEAN
    assert done["suggestions"] == SUGGESTED


def test_module_question_gets_did_you_mean_in_json(scripted, suggests):
    client, _ = scripted(["NO_ANSWER"])
    body = _ask(client, "streming nhi chal raha", stream=False).json()
    assert body["answer"] == DID_YOU_MEAN
    assert body["suggestions"] == SUGGESTED


def test_off_topic_question_keeps_plain_no_answer(scripted):
    # did_you_mean returns None for questions outside the modules (conftest default).
    client, _ = scripted(["NO_ANSWER"])
    text, done = _streamed_text(_ask(client, "tell me a joke", stream=True))
    assert text == done["answer"] == app_chat.get_settings().app_chat.no_answer_message
    assert "suggestions" not in done


def test_blocked_api_answer_gets_did_you_mean_without_the_api(scripted, suggests):
    client, _ = scripted(["Call PUT score/v1/update_score with the sets."])
    text, done = _streamed_text(_ask(client, "which api saves the score", stream=True))
    assert done["answer"] == DID_YOU_MEAN
    assert "update_score" not in text + done["answer"]


def test_did_you_mean_lists_the_suggestions(monkeypatch):
    from app.services.auth import CallerScope

    monkeypatch.undo()  # the real did_you_mean, not the conftest stub
    monkeypatch.setattr(app_chat.query_rewrite, "module_question", lambda q: "How do I fix streaming?")
    monkeypatch.setattr(app_chat.knowledge, "suggest_questions", lambda *a, **kw: list(SUGGESTED))
    text, items = app_chat.did_you_mean(CallerScope(tenant="t", user_id="u"), "streming nhi chal raha", None, None)
    assert text == DID_YOU_MEAN and items == SUGGESTED
    monkeypatch.setattr(app_chat.query_rewrite, "module_question", lambda q: None)
    assert app_chat.did_you_mean(CallerScope(tenant="t", user_id="u"), "tell me a joke", None, None) is None


def test_code_requests_are_off_topic_without_a_model_call(monkeypatch):
    from app.services import query_rewrite, rag_pipeline

    monkeypatch.setattr(rag_pipeline, "get_utility_llm", lambda: (_ for _ in ()).throw(AssertionError("no call")))
    assert query_rewrite.module_question("give me python code for two sum") is None
    assert query_rewrite.module_question("how do I reverse a linked list in java") is None


@pytest.mark.parametrize("question", [
    "Event live nahi ho raha, kya karun?",
    "players ko kaise add karte hai",
    "leaderboard dikh nahi raha sidebar me",
])
def test_hindi_in_english_letters_is_hinglish(question):
    from app.services.language import detect_language

    assert detect_language(question).code == "hi-latn"


@pytest.mark.parametrize("question", [
    "How do I add players to the event?",
    "Show me the schedule of the matches",
    "खिलाड़ियों को कैसे जोड़ें?",
])
def test_other_questions_are_not_hinglish(question):
    from app.services.language import detect_language

    assert getattr(detect_language(question), "code", None) != "hi-latn"


def test_helper_calls_stay_at_temperature_zero(monkeypatch):
    from app.services import rag_pipeline

    monkeypatch.setattr(rag_pipeline.get_settings().llm, "temperature", 0.8)
    rag_pipeline.reset_llm_for_tests()
    try:
        assert rag_pipeline.get_utility_llm().temperature == 0
        assert rag_pipeline.get_llm().temperature == 0.8
    finally:
        rag_pipeline.reset_llm_for_tests()
