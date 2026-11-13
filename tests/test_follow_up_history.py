"""Earlier turns reach the model only with a follow-up question, so an old topic cannot leak in."""

from __future__ import annotations

import pytest
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableLambda

from app.services import app_chat, rag_pipeline
from app.services.chat_memory import get_message_history, reset_chat_memory_for_tests


@pytest.mark.parametrize("question", [
    "How do I create a tournament?",
    "Why can't I publish my event?",
    "golden match kab create hota hai",
    "How are the standings ordered in a group stage?",
])
def test_a_new_topic_is_not_a_follow_up(question):
    assert not app_chat.is_follow_up(question)


@pytest.mark.parametrize("question", [
    "how do I delete it?",
    "what about doubles matches?",
    "and doubles?",
    "isko kaise edit kare",
    "uske baad kya karna hai",
    "Why is that option greyed out?",
])
def test_a_question_about_the_last_answer_is_a_follow_up(question):
    assert app_chat.is_follow_up(question)


@pytest.fixture
def seen(monkeypatch):
    """The messages the model receives, with a fake model."""
    calls: list[list] = []

    def fake_model(prompt_value):
        calls.append(prompt_value.to_messages())
        return AIMessage(content="answer")

    reset_chat_memory_for_tests()
    rag_pipeline.reset_rag_chain_for_tests()
    monkeypatch.setattr(rag_pipeline, "get_llm", lambda: RunnableLambda(fake_model))
    yield calls
    rag_pipeline.reset_rag_chain_for_tests()
    reset_chat_memory_for_tests()


def _ask(question: str, use_history: bool) -> None:
    rag_pipeline.answer_question(
        question, "s1", retriever=lambda q: ("Context about it.", [{"content": "x"}]),
        prompt_template="{context}\n\n{question}", use_history=use_history,
    )


def _human_texts(messages) -> list[str]:
    return [m.content for m in messages if isinstance(m, HumanMessage)]


def test_a_new_topic_is_sent_without_the_earlier_turn(seen):
    _ask("How do I create a tournament?", use_history=False)
    _ask("Why can't I publish my event?", use_history=False)
    assert "How do I create a tournament?" not in _human_texts(seen[1])


def test_a_follow_up_gets_the_earlier_turn(seen):
    _ask("How do I add a player?", use_history=False)
    _ask("how do I delete it?", use_history=True)
    assert "How do I add a player?" in _human_texts(seen[1])


def test_skipped_turns_are_still_remembered(seen):
    _ask("How do I add a player?", use_history=False)
    assert [m.content for m in get_message_history("s1").messages] == ["How do I add a player?", "answer"]
