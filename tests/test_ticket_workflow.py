"""Unit tests for ticket intent detection and wizard steps."""

from __future__ import annotations

import pytest

from app.services import ticket_workflow


@pytest.fixture(autouse=True)
def _clear_state():
    ticket_workflow.reset_ticket_state_for_tests()
    yield
    ticket_workflow.reset_ticket_state_for_tests()


def test_detect_ticket_intent_positive():
    assert ticket_workflow.detect_ticket_intent("Create a ticket")
    assert ticket_workflow.detect_ticket_intent("I found a problem")
    assert ticket_workflow.detect_ticket_intent("raise a bug please")


def test_detect_ticket_intent_negative():
    assert not ticket_workflow.detect_ticket_intent("What is Stupa?")


def test_ticket_flow_collects_title():
    sid = "test-session-1"
    start = ticket_workflow.try_process(sid, "report an issue")
    assert start is not None
    assert start.flow.step == "title"
    assert start.workflow.next_field == "title"

    step2 = ticket_workflow.try_process(sid, "Login broken on mobile")
    assert step2 is not None
    assert step2.flow.step == "description"


def test_ticket_flow_cancel():
    sid = "test-session-2"
    ticket_workflow.try_process(sid, "create ticket")
    cancelled = ticket_workflow.try_process(sid, "cancel")
    assert cancelled is not None
    assert not cancelled.flow.active
