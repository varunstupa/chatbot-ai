"""Book-a-demo wizard for `/stupa-chat` (in-memory per session_id).

Flow: intent "book a demo" → collect full name, contact, email, interest,
optional description → confirmation table → user replies **yes**.

On **yes**, POSTs to Stupa send-email (`demo_booking.send_email_url` in
`config.yaml`) with: fullName, contact, email, interests (array), description.
The API response body is shown in the chat on success.

Env: `DEMO_BOOKING_SEND_EMAIL_URL`, `DEMO_BOOKING_SEND_EMAIL_ENABLED` (0/false
to skip HTTP). Stdout: lines prefixed `[demo-booking]` on trigger and status.
"""

from __future__ import annotations

import json
import logging
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from threading import Lock
from typing import Any

from app.config.settings import get_settings
from app.utils.debug_console import debug_log

logger = logging.getLogger(__name__)

INTEREST_OPTIONS: tuple[str, ...] = (
    "Stupa Events AI",
    "Live Cast AI",
    "Value Added Services",
)

_INTENT = re.compile(
    r"\b(book|schedule|request)\b.*\bdemo\b|\bdemo\b.*\b(book|schedule)\b",
    re.IGNORECASE,
)
_EMAIL_OK = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_CANCEL = re.compile(r"^\s*(cancel|stop|quit|exit)\s*$", re.IGNORECASE)
_YES = re.compile(r"^\s*(yes|y|confirm|ok|submit|sure)\s*\.?\s*$", re.IGNORECASE)
_NO = re.compile(r"^\s*(no|n|abort)\s*\.?\s*$", re.IGNORECASE)
_SKIP = re.compile(r"^\s*(skip|none|n/?a|-)\s*\.?\s*$", re.IGNORECASE)
_NAME_LIKE = re.compile(r"^[A-Za-z][A-Za-z\s'.-]{1,120}$")


@dataclass
class DemoFlowPayload:
    """Serializable state for the frontend (buttons, progress)."""

    active: bool
    phase: str
    step: str | None
    interest_options: list[str] | None
    slots: dict[str, str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "active": self.active,
            "phase": self.phase,
            "step": self.step,
            "interest_options": self.interest_options,
            "slots": dict(self.slots),
        }


@dataclass
class DemoTurnResult:
    answer: str
    flow: DemoFlowPayload


class _Session:
    __slots__ = ("phase", "step", "slots")

    def __init__(self) -> None:
        self.phase: str = "collecting"
        self.step: str = "full_name"
        self.slots: dict[str, str] = {
            "full_name": "",
            "contact": "",
            "email": "",
            "interest": "",
            "description": "",
        }


_store: dict[str, _Session] = {}
_lock = Lock()


def _send_email_enabled() -> bool:
    v = (os.environ.get("DEMO_BOOKING_SEND_EMAIL_ENABLED") or "").strip().lower()
    if v in ("0", "false", "no", "off"):
        return False
    return get_settings().demo_booking.enabled


def _send_email_api_url() -> str:
    env_u = (os.environ.get("DEMO_BOOKING_SEND_EMAIL_URL") or "").strip()
    if env_u:
        return env_u
    return (get_settings().demo_booking.send_email_url or "").strip()


def _format_response_snippet(text: str, limit: int = 900) -> str:
    t = (text or "").strip()
    if not t:
        return "_(empty body)_"
    try:
        obj = json.loads(t)
        t = json.dumps(obj, ensure_ascii=False, indent=2)
    except (json.JSONDecodeError, TypeError, ValueError):
        pass
    if len(t) > limit:
        return t[: limit - 3] + "..."
    return t


def _user_facing_booking_success(response_text: str) -> str:
    """Single friendly line for chat — no raw JSON."""
    fallback = (
        "Your demo request was submitted successfully. "
        "Our team will reach out soon."
    )
    t = (response_text or "").strip()
    if not t:
        return fallback
    try:
        obj = json.loads(t)
    except (json.JSONDecodeError, TypeError, ValueError):
        debug_log("demo booking success body (non-JSON)", t[:300])
        return fallback
    if not isinstance(obj, dict):
        return fallback
    msg = obj.get("message")
    if isinstance(msg, str) and msg.strip():
        return msg.strip()
    if obj.get("success") is True:
        return fallback
    return fallback


def _post_stupa_send_email(api_url: str, body: dict[str, Any]) -> tuple[int, str]:
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        api_url,
        data=data,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Accept": "*/*",
            "Origin": "https://stupasports.ai",
            "Referer": "https://stupasports.ai/demo",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            return resp.getcode(), raw
    except urllib.error.HTTPError as e:
        err_body = ""
        if e.fp is not None:
            err_body = e.read().decode("utf-8", errors="replace")
        return e.code, err_body or (e.reason or str(e))


def _match_interest(text: str) -> str | None:
    t = text.strip().lower()
    if not t:
        return None
    if t == "1":
        return INTEREST_OPTIONS[0]
    if t == "2":
        return INTEREST_OPTIONS[1]
    if t == "3":
        return INTEREST_OPTIONS[2]
    for opt in INTEREST_OPTIONS:
        ol = opt.lower()
        if ol in t or t in ol:
            return opt
    return None


def _payload(session_id: str, s: _Session) -> DemoFlowPayload:
    opts = list(INTEREST_OPTIONS) if s.step == "interest" else None
    return DemoFlowPayload(
        active=True,
        phase=s.phase,
        step=s.step if s.phase == "collecting" else None,
        interest_options=opts,
        slots=dict(s.slots),
    )


def _idle_payload() -> DemoFlowPayload:
    return DemoFlowPayload(
        active=False,
        phase="idle",
        step=None,
        interest_options=None,
        slots={},
    )


def _preview_markdown(s: _Session) -> str:
    d = s.slots
    desc = d.get("description") or "—"
    contact = d.get("contact") or "—"
    lines = [
        "## Demo booking — please confirm",
        "",
        "| Field | Value |",
        "| --- | --- |",
        f"| Full name | {d.get('full_name', '')} |",
        f"| Contact | {contact} |",
        f"| E-mail | {d.get('email', '')} |",
        f"| Interest | {d.get('interest', '')} |",
        f"| Description | {desc} |",
        "",
        "Reply **yes** to submit or **no** to cancel.",
    ]
    return "\n".join(lines)


def try_process(session_id: str, message: str) -> DemoTurnResult | None:
    """
    If this turn belongs to the demo flow, return the assistant reply + payload.
    Return None to let normal RAG handle the message.
    """
    sid = (session_id or "").strip()
    raw = (message or "").strip()
    if not sid or not raw:
        return None

    with _lock:
        existing = _store.get(sid)

    debug_log(
        "demo try_process",
        f"sid={sid[:10]}…",
        f"msg={raw[:72]!r}",
        f"had_session={existing is not None}",
    )

    if _CANCEL.match(raw):
        with _lock:
            _store.pop(sid, None)
        debug_log("demo cancel")
        return DemoTurnResult(
            "Demo booking cancelled. You can ask me anything else anytime.",
            _idle_payload(),
        )

    if existing is None:
        if not _INTENT.search(raw):
            wizard_reply = _YES.match(raw) or _NO.match(raw) or _SKIP.match(raw)
            if (
                _NAME_LIKE.match(raw)
                and not _EMAIL_OK.match(raw)
                and not wizard_reply
            ):
                logger.warning(
                    "demo_booking | no session for this message; "
                    "echo session_id from the 'book a demo' reply (JSON "
                    "session_id, header X-Session-Id, SSE session event, or "
                    "cookie). msg=%r",
                    raw[:80],
                )
            return None
        with _lock:
            _store[sid] = _Session()
        debug_log("demo started", "step=full_name")
        return DemoTurnResult(
            "## Book a demo\n\nWhat is your **full name**?",
            _payload(sid, _store[sid]),
        )

    s = existing

    if s.phase == "confirming":
        if _YES.match(raw):
            fields_only = {
                "full_name": s.slots["full_name"],
                "contact": s.slots["contact"],
                "email": s.slots["email"],
                "interest": s.slots["interest"],
                "description": s.slots["description"],
            }
            api_url = _send_email_api_url()
            enabled = _send_email_enabled()

            if not enabled or not api_url:
                logger.info(
                    "demo_booking_send_email_skipped",
                    extra={"enabled": enabled, "has_url": bool(api_url)},
                )
                print(
                    "[demo-booking] send-email SKIPPED "
                    "(disabled or empty DEMO_BOOKING_SEND_EMAIL_URL)",
                    flush=True,
                )
                with _lock:
                    _store.pop(sid, None)
                done = DemoFlowPayload(
                    active=False,
                    phase="submitted",
                    step=None,
                    interest_options=None,
                    slots=fields_only,
                )
                return DemoTurnResult(
                    "## Thank you\n\n"
                    "Your demo details were saved in chat only: the send-email "
                    "integration is turned off or has no URL.",
                    done,
                )

            stupa_body: dict[str, Any] = {
                "fullName": s.slots["full_name"].strip(),
                "contact": (s.slots["contact"] or "").strip(),
                "email": s.slots["email"].strip(),
                "interests": [s.slots["interest"]] if s.slots.get("interest") else [],
                "description": (s.slots.get("description") or "").strip(),
            }

            print(f"[demo-booking] TRIGGER send-email → {api_url}", flush=True)
            logger.info("demo_booking_send_email_trigger", extra={"url": api_url})
            debug_log("demo send-email payload keys", list(stupa_body.keys()))

            try:
                status, response_text = _post_stupa_send_email(api_url, stupa_body)
            except (urllib.error.URLError, OSError) as e:
                logger.exception("demo_booking_send_email_network_failed")
                print(f"[demo-booking] send-email ERROR: {e!s}", flush=True)
                return DemoTurnResult(
                    f"Submit failed ({e!s}). Check the server or try again. "
                    "Reply **yes** to retry or **no** to cancel.",
                    _payload(sid, s),
                )

            print(f"[demo-booking] send-email response status={status}", flush=True)
            logger.info(
                "demo_booking_send_email_done",
                extra={"status": status, "body_len": len(response_text or "")},
            )

            if status >= 400:
                snippet = _format_response_snippet(response_text, 400)
                return DemoTurnResult(
                    f"## Submit failed (HTTP {status})\n\n"
                    f"```\n{snippet}\n```\n\n"
                    "Reply **yes** to retry or **no** to cancel.",
                    _payload(sid, s),
                )

            with _lock:
                _store.pop(sid, None)
            debug_log("demo submitted ok", (response_text or "")[:400])
            user_line = _user_facing_booking_success(response_text)
            done = DemoFlowPayload(
                active=False,
                phase="submitted",
                step=None,
                interest_options=None,
                slots=fields_only,
            )
            return DemoTurnResult(
                f"## Thank you\n\n{user_line}",
                done,
            )
        if _NO.match(raw):
            with _lock:
                _store.pop(sid, None)
            return DemoTurnResult(
                "Booking cancelled. Let me know if you need anything else.",
                _idle_payload(),
            )
        return DemoTurnResult(
            _preview_markdown(s)
            + "\n\nPlease reply **yes** to confirm or **no** to cancel.",
            _payload(sid, s),
        )

    # collecting
    step = s.step
    if step == "full_name":
        if len(raw) < 2:
            return DemoTurnResult(
                "Please enter your **full name**.",
                _payload(sid, s),
            )
        s.slots["full_name"] = raw
        s.step = "contact"
        return DemoTurnResult(
            "Thanks. What is your **contact** number? "
            "(Say **skip** if you prefer not to share.)",
            _payload(sid, s),
        )

    if step == "contact":
        if _SKIP.match(raw):
            s.slots["contact"] = ""
        else:
            s.slots["contact"] = raw
        s.step = "email"
        return DemoTurnResult(
            "Got it. What is your **e-mail** address?",
            _payload(sid, s),
        )

    if step == "email":
        if not _EMAIL_OK.match(raw):
            return DemoTurnResult(
                "That does not look like a valid e-mail. Please try again.",
                _payload(sid, s),
            )
        s.slots["email"] = raw
        s.step = "interest"
        opts = "\n".join(f"{i}. **{o}**" for i, o in enumerate(INTEREST_OPTIONS, 1))
        return DemoTurnResult(
            "## What are you interested in?\n\n"
            f"{opts}\n\nReply with the **name** or **number** (1–3).",
            _payload(sid, s),
        )

    if step == "interest":
        choice = _match_interest(raw)
        if not choice:
            return DemoTurnResult(
                "Please pick one: **Stupa Events AI**, "
                "**Live Cast AI**, or **Value Added Services** (or 1 / 2 / 3).",
                _payload(sid, s),
            )
        s.slots["interest"] = choice
        s.step = "description"
        return DemoTurnResult(
            "Almost done. Any **description** or notes? "
            "(Optional — say **skip** to leave blank.)",
            _payload(sid, s),
        )

    if step == "description":
        if _SKIP.match(raw):
            s.slots["description"] = ""
        else:
            s.slots["description"] = raw
        s.phase = "confirming"
        s.step = "confirm"
        debug_log("demo → preview confirm")
        return DemoTurnResult(
            _preview_markdown(s),
            _payload(sid, s),
        )

    debug_log("demo → RAG (not handled)")
    return None


def reset_demo_state_for_tests() -> None:
    with _lock:
        _store.clear()
