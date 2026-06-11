"""Unit tests for ticket intent detection and wizard steps."""

from __future__ import annotations

import pytest

from app.models.ticket_schemas import TicketDraftPayload
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


def test_confirm_from_client_draft_without_server_session():
    sid = "test-session-3"
    draft = TicketDraftPayload(
        title="Login issue",
        description="Steps to reproduce the login failure on mobile.",
        expected_vs_actual="Expected login, got error page.",
        attachments=[],
    )
    result = ticket_workflow.try_process(
        sid,
        "yes",
        ticket_draft=draft,
    )
    assert result is not None
    assert result.flow.action in ("ticket_created", "collect_ticket_information")
