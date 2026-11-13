"""LangSmith traces of the admin-app chat: off without a key, one trace per question, no leaks."""

from __future__ import annotations

import asyncio
import uuid
from unittest.mock import MagicMock

import pytest
from langsmith.utils import tracing_is_enabled
from pydantic import SecretStr

from app.config.settings import get_settings
from app.services import app_chat, chat_store, tracing

REQUEST_ID = uuid.uuid4().hex


def _question(**kw) -> tracing.QuestionTrace:
    args = dict(request_id=REQUEST_ID, session_id="s1", tenant="staging", role="1", route="r",
                sport=None, language="en", streamed=True)
    return tracing.question("How do I delete a player?", **{**args, **kw})


@pytest.fixture
def client(monkeypatch) -> MagicMock:
    fake = MagicMock()
    monkeypatch.setattr(tracing, "_client", fake)
    return fake


def test_without_a_client_everything_passes_through(monkeypatch):
    monkeypatch.setattr(tracing, "_client", None)
    trace = _question()

    async def items():
        yield "a"
        yield "b"

    async def go():
        return [x async for x in trace.stream(items())], await trace.run(asyncio.sleep(0, "done"))

    assert asyncio.run(go()) == (["a", "b"], "done")
    trace.end("answer", chat_store.ANSWERED)
    tracing.feedback(REQUEST_ID, "up", None)


@pytest.mark.parametrize("enabled, key", [(False, "key"), (True, ""), (True, None)])
def test_start_needs_both_the_setting_and_the_key(monkeypatch, enabled, key):
    monkeypatch.undo()  # conftest replaces start() for every other test
    s = get_settings()
    monkeypatch.setattr(s.langsmith, "enabled", enabled)
    monkeypatch.setattr(s, "langsmith_api_key", SecretStr(key) if key is not None else None)
    monkeypatch.setattr(tracing, "_client", None)
    tracing.start()
    assert tracing._client is None


def test_trace_id_is_the_message_id_and_holds_no_user_id(client):
    _question()
    sent = client.create_run.call_args.kwargs
    assert str(sent["id"]) == str(uuid.UUID(hex=REQUEST_ID))
    assert sent["inputs"] == {"question": "How do I delete a player?"}
    assert "user_id" not in str(sent)


def test_tracing_stays_inside_the_question(client):
    trace = _question()
    assert not tracing_is_enabled()

    async def items():
        assert tracing_is_enabled()
        yield 1
        assert await asyncio.to_thread(tracing_is_enabled)
        yield 2

    async def go():
        out = []
        async for item in trace.stream(items()):
            # The response stream and the rest of the app are not traced between tokens.
            assert not tracing_is_enabled()
            out.append(item)
        return out

    assert asyncio.run(go()) == [1, 2]
    assert not tracing_is_enabled()


def test_retrieve_is_a_child_run_and_hides_the_caller(client, monkeypatch):
    from app.services.auth import CallerScope

    trace = _question()
    monkeypatch.setattr(app_chat.knowledge, "guides_for_screen", lambda *a: [])
    monkeypatch.setattr(app_chat.knowledge, "screen_info", lambda *a: None)
    monkeypatch.setattr(app_chat.knowledge, "search", lambda *a, **kw: [])
    scope = CallerScope(tenant="staging", user_id="secret-user-7", role="1")

    async def go():
        return await trace.run(asyncio.to_thread(app_chat.retrieve, scope, "q", None, None))

    asyncio.run(go())
    assert "secret-user-7" not in str(client.mock_calls)


def test_only_the_first_end_counts(client):
    trace = _question()
    trace.end("the answer", chat_store.ANSWERED)
    trace.end("partial", "disconnected")
    update = client.update_run.call_args_list
    assert len(update) == 1
    assert update[0].kwargs["outputs"] == {"answer": "the answer"}
    assert update[0].kwargs["error"] is None


def test_a_failed_answer_is_marked_as_error(client):
    trace = _question()
    trace.end("Something went wrong", chat_store.ERROR)
    assert client.update_run.call_args.kwargs["error"] == "Something went wrong"


def test_tracing_failures_never_reach_the_user(client):
    client.create_run.side_effect = RuntimeError("LangSmith is down")
    trace = _question()
    assert trace._run is None
    client.create_feedback.side_effect = RuntimeError("LangSmith is down")
    tracing.feedback(REQUEST_ID, "up", None)


def test_voting_again_replaces_the_vote(client):
    tracing.feedback(REQUEST_ID, "down", "wrong")
    tracing.feedback(REQUEST_ID, "up", None)
    first, second = client.create_feedback.call_args_list
    assert first.kwargs["score"] == 0 and second.kwargs["score"] == 1
    assert first.kwargs["feedback_id"] == second.kwargs["feedback_id"]
    assert first.kwargs["trace_id"] == uuid.UUID(hex=REQUEST_ID)


def test_an_id_that_is_not_a_run_is_skipped(client):
    tracing.feedback("not-a-uuid", "up", None)
    client.create_feedback.assert_not_called()
