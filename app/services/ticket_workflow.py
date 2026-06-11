"""Conversational Jira ticket wizard for ``/stupa-chat`` (persisted per session)."""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from typing import Any

from app.config.settings import get_settings
from app.models.ticket_schemas import TicketDraftPayload, TicketWorkflowResponse
from app.services.jira_service import JiraService
from app.services.ticket_providers.jira_provider import (
    JiraApiError,
    JiraConfigurationError,
)
from app.services.ticket_upload import resolve_ticket_path
from app.utils.debug_console import debug_log

logger = logging.getLogger(__name__)

_INTENT = re.compile(
    r"\b(report|raise|log|file)\b.*\b(issue|bug|ticket)\b|"
    r"\b(create|open|submit)\b.*\b(ticket|bug)\b|"
    r"\b(ticket|bug)\b.*\b(create|report)\b|"
    r"\bi\s+found\s+a\s+problem\b|"
    r"\bsupport\s+request\b",
    re.IGNORECASE,
)
_CANCEL = re.compile(r"^\s*(cancel|stop|quit|exit)\s*$", re.IGNORECASE)
_YES = re.compile(
    r"^\s*(yes|y|confirm|create\s+ticket|submit|sure)\s*\.?\s*$",
    re.IGNORECASE,
)
_NO = re.compile(r"^\s*(no|n|abort)\s*\.?\s*$", re.IGNORECASE)
_SKIP = re.compile(r"^\s*(skip|none|n/?a|done|-)\s*\.?\s*$", re.IGNORECASE)

_STEPS: tuple[str, ...] = (
    "title",
    "description",
    "expected_vs_actual",
    "attachments",
    "confirm",
)

_PROMPTS: dict[str, str] = {
    "title": "Please provide a **short title** for the issue.",
    "description": (
        "Please **describe the issue** and provide steps to reproduce it."
    ),
    "expected_vs_actual": (
        "What did you **expect** to happen and what **actually** happened?"
    ),
    "attachments": (
        "Please **upload** any screenshots, videos, or supporting files "
        "using the attachment area, then reply **done** or **skip**."
    ),
}

_store: dict[str, "_Session"] = {}
_lock = Lock()


@dataclass
class TicketFlowPayload:
    active: bool
    phase: str
    step: str | None
    next_field: str | None
    action: str | None
    slots: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "active": self.active,
            "phase": self.phase,
            "step": self.step,
            "next_field": self.next_field,
            "action": self.action,
            "slots": dict(self.slots),
        }


@dataclass
class TicketTurnResult:
    answer: str
    flow: TicketFlowPayload
    workflow: TicketWorkflowResponse


class _Session:
    __slots__ = ("phase", "step", "slots")

    def __init__(self) -> None:
        self.phase = "collecting"
        self.step: str = "title"
        self.slots: dict[str, Any] = {
            "title": "",
            "description": "",
            "expected_vs_actual": "",
            "attachments": [],
        }


def _sessions_dir() -> Path:
    base = Path(get_settings().paths.upload_dir).resolve().parent
    root = base / "ticket_sessions"
    root.mkdir(parents=True, exist_ok=True)
    return root


def _session_file(sid: str) -> Path:
    safe = re.sub(r"[^a-zA-Z0-9-]", "", sid)
    return _sessions_dir() / f"{safe}.json"


def _session_to_dict(s: _Session) -> dict[str, Any]:
    return {
        "phase": s.phase,
        "step": s.step,
        "slots": dict(s.slots),
    }


def _session_from_dict(data: dict[str, Any]) -> _Session:
    s = _Session()
    s.phase = str(data.get("phase") or "collecting")
    s.step = str(data.get("step") or "title")
    slots = data.get("slots")
    if isinstance(slots, dict):
        s.slots = {
            "title": str(slots.get("title") or ""),
            "description": str(slots.get("description") or ""),
            "expected_vs_actual": str(slots.get("expected_vs_actual") or ""),
            "attachments": list(slots.get("attachments") or []),
        }
    return s


def _load_session(sid: str) -> _Session | None:
    with _lock:
        cached = _store.get(sid)
    if cached is not None:
        return cached
    path = _session_file(sid)
    if not path.is_file():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            return None
        sess = _session_from_dict(raw)
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        logger.warning("ticket_session_load_failed | sid=%s", sid[:12])
        return None
    with _lock:
        _store[sid] = sess
    logger.info("ticket_session_restored | sid=%s step=%s", sid[:12], sess.step)
    return sess


def _save_session(sid: str, s: _Session) -> None:
    with _lock:
        _store[sid] = s
    path = _session_file(sid)
    path.write_text(
        json.dumps(_session_to_dict(s), ensure_ascii=False),
        encoding="utf-8",
    )


def _delete_session(sid: str) -> None:
    with _lock:
        _store.pop(sid, None)
    path = _session_file(sid)
    if path.is_file():
        path.unlink(missing_ok=True)


def detect_ticket_intent(message: str) -> bool:
    return bool(_INTENT.search((message or "").strip()))


def _idle_payload() -> TicketFlowPayload:
    return TicketFlowPayload(
        active=False,
        phase="idle",
        step=None,
        next_field=None,
        action=None,
        slots={},
    )


def _workflow_from_session(s: _Session) -> TicketWorkflowResponse:
    nxt = s.step if s.phase == "collecting" else None
    return TicketWorkflowResponse(
        action="collect_ticket_information",
        next_field=nxt,
        active=s.phase != "idle",
        phase=s.phase,
        step=s.step,
        prompt=_PROMPTS.get(s.step or "", None),
        slots=dict(s.slots),
    )


def _payload(sid: str, s: _Session) -> TicketFlowPayload:
    nxt = s.step if s.phase == "collecting" else None
    return TicketFlowPayload(
        active=True,
        phase=s.phase,
        step=s.step,
        next_field=nxt,
        action="collect_ticket_information",
        slots=dict(s.slots),
    )


def register_session_attachment(
    session_id: str,
    file_name: str,
    file_path: str,
) -> None:
    """Called after ``POST /query/attachment`` or ``POST /stupa-chat/attachment``."""
    sid = (session_id or "").strip()
    if not sid:
        return
    sess = _load_session(sid)
    if sess is None:
        sess = _Session()
        sess.step = "attachments"
        logger.info(
            "ticket_session_bootstrapped | sid=%s reason=attachment",
            sid[:12],
        )
    items = sess.slots.setdefault("attachments", [])
    if not isinstance(items, list):
        items = []
        sess.slots["attachments"] = items
    items.append({"file_name": file_name, "file_path": file_path})
    _save_session(sid, sess)
    logger.info(
        "ticket_session_attachment | sid=%s count=%s",
        sid[:10],
        len(items),
    )


def _preview_markdown(s: _Session) -> str:
    att = s.slots.get("attachments") or []
    count = len(att) if isinstance(att, list) else 0
    return "\n".join(
        [
            "## Ticket summary",
            "",
            f"**Title:** {s.slots.get('title', '')}",
            "",
            f"**Description:** {s.slots.get('description', '')}",
            "",
            f"**Expected vs actual:** {s.slots.get('expected_vs_actual', '')}",
            "",
            f"**Attachments:** {count}",
            "",
            "Would you like me to **create the Jira ticket**? "
            "Reply **yes** to create or **no** to cancel.",
        ],
    )


def _is_wizard_only_reply(raw: str) -> bool:
    return bool(
        _YES.match(raw)
        or _NO.match(raw)
        or _SKIP.match(raw)
        or _CANCEL.match(raw),
    )


def _session_from_draft(draft: TicketDraftPayload) -> _Session:
    s = _Session()
    s.phase = "confirming"
    s.step = "confirm"
    s.slots = {
        "title": draft.title.strip(),
        "description": draft.description.strip(),
        "expected_vs_actual": draft.expected_vs_actual.strip(),
        "attachments": [
            {"file_name": a.file_name, "file_path": a.file_path}
            for a in draft.attachments
        ],
    }
    return s


def try_process(
    session_id: str,
    message: str,
    *,
    ticket_draft: TicketDraftPayload | None = None,
) -> TicketTurnResult | None:
    """
    If this turn belongs to the ticket flow, return the assistant reply + payload.
    Return None to let demo/RAG handle the message.
    """
    sid = (session_id or "").strip()
    raw = (message or "").strip()
    if not sid or not raw:
        return None

    existing = _load_session(sid)

    if _CANCEL.match(raw):
        if existing is not None:
            _delete_session(sid)
            return TicketTurnResult(
                "Ticket creation cancelled. Ask me anything else anytime.",
                _idle_payload(),
                TicketWorkflowResponse(
                    action="ticket_cancelled",
                    active=False,
                    phase="idle",
                    next_field=None,
                ),
            )
        return None

    if existing is None:
        if _YES.match(raw) and ticket_draft is not None:
            logger.info(
                "ticket_workflow | confirm from client draft | sid=%s",
                sid[:12],
            )
            return _submit_ticket(sid, _session_from_draft(ticket_draft))
        if _is_wizard_only_reply(raw):
            return None
        if not detect_ticket_intent(raw):
            return None
        sess = _Session()
        _save_session(sid, sess)
        debug_log("ticket started", "step=title")
        wf = _workflow_from_session(sess)
        return TicketTurnResult(
            "## Report an issue\n\n" + _PROMPTS["title"],
            _payload(sid, sess),
            wf,
        )

    s = existing

    if s.phase == "confirming":
        if _YES.match(raw):
            return _submit_ticket(sid, s)
        if _NO.match(raw):
            _delete_session(sid)
            return TicketTurnResult(
                "Ticket creation cancelled.",
                _idle_payload(),
                TicketWorkflowResponse(
                    action="ticket_cancelled",
                    active=False,
                    phase="idle",
                ),
            )
        body = _preview_markdown(s) + "\n\nReply **yes** or **no**."
        return TicketTurnResult(
            body,
            _payload(sid, s),
            _workflow_from_session(s),
        )

    step = s.step
    if step == "title":
        if len(raw) < 3:
            return _reply(sid, s, "Please enter a longer **title** (3+ chars).")
        s.slots["title"] = raw
        s.step = "description"
        return _reply(sid, s, _PROMPTS["description"])

    if step == "description":
        if len(raw) < 10:
            return _reply(
                sid,
                s,
                "Please provide a bit more **detail** (10+ characters).",
            )
        s.slots["description"] = raw
        s.step = "expected_vs_actual"
        return _reply(sid, s, _PROMPTS["expected_vs_actual"])

    if step == "expected_vs_actual":
        if len(raw) < 5:
            return _reply(sid, s, "Please describe expected vs actual behavior.")
        s.slots["expected_vs_actual"] = raw
        s.step = "attachments"
        return _reply(sid, s, _PROMPTS["attachments"])

    if step == "attachments":
        if not _SKIP.match(raw):
            att = s.slots.get("attachments") or []
            if not isinstance(att, list) or len(att) == 0:
                return _reply(
                    sid,
                    s,
                    "Upload files in the chat attachment area, then reply "
                    "**done**, or reply **skip** to continue without files.",
                )
        s.phase = "confirming"
        s.step = "confirm"
        _save_session(sid, s)
        return TicketTurnResult(
            _preview_markdown(s),
            _payload(sid, s),
            _workflow_from_session(s),
        )

    return None


def _reply(sid: str, s: _Session, text: str) -> TicketTurnResult:
    _save_session(sid, s)
    return TicketTurnResult(
        text,
        _payload(sid, s),
        _workflow_from_session(s),
    )


def _submit_ticket(sid: str, s: _Session) -> TicketTurnResult:
    svc = JiraService()
    paths: list[tuple] = []
    att = s.slots.get("attachments") or []
    if isinstance(att, list):
        for item in att:
            if not isinstance(item, dict):
                continue
            fp = resolve_ticket_path(str(item.get("file_path", "")))
            fn = str(item.get("file_name", "attachment"))
            if fp is not None:
                paths.append((fp, fn))

    msgs = get_settings().messages
    try:
        created = svc.create_issue(
            title=str(s.slots.get("title", "")),
            description=str(s.slots.get("description", "")),
            expected_vs_actual=str(s.slots.get("expected_vs_actual", "")),
            attachment_paths=paths,
        )
    except JiraConfigurationError:
        logger.error(
            "ticket_submit_failed | sid=%s reason=jira_not_configured",
            sid[:10],
        )
        return TicketTurnResult(
            msgs.ticket_jira_not_configured,
            _payload(sid, s),
            _workflow_from_session(s),
        )
    except JiraApiError:
        logger.exception(
            "ticket_submit_failed | sid=%s reason=jira_api",
            sid[:10],
        )
        return TicketTurnResult(
            msgs.ticket_create_failed,
            _payload(sid, s),
            _workflow_from_session(s),
        )
    except Exception:
        logger.exception("ticket_submit_failed | sid=%s", sid[:10])
        return TicketTurnResult(
            msgs.ticket_create_failed,
            _payload(sid, s),
            _workflow_from_session(s),
        )

    _delete_session(sid)

    done = TicketFlowPayload(
        active=False,
        phase="submitted",
        step=None,
        next_field=None,
        action="ticket_created",
        slots={
            "ticket_id": created.ticket_id,
            "ticket_url": created.ticket_url,
        },
    )
    wf = TicketWorkflowResponse(
        action="ticket_created",
        active=False,
        phase="submitted",
        next_field=None,
        slots=done.slots,
    )
    lines = [
        "## Ticket created successfully",
        "",
        f"**Ticket number:** {created.ticket_id}",
        "",
        f"**Ticket link:** [{created.ticket_url}]({created.ticket_url})",
    ]
    return TicketTurnResult("\n".join(lines), done, wf)


def reset_ticket_state_for_tests() -> None:
    with _lock:
        _store.clear()
    root = _sessions_dir()
    for path in root.glob("*.json"):
        path.unlink(missing_ok=True)
