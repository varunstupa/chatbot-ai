"""Pydantic models for ticket flow on chat endpoints (``/query``, ``/stupa-chat``)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class TicketWorkflowResponse(BaseModel):
    """Structured hint for the frontend (same shape as SSE ``ticket_workflow``)."""

    action: str = "collect_ticket_information"
    next_field: str | None = None
    active: bool = True
    phase: str = "collecting"
    step: str | None = None
    prompt: str | None = None
    slots: dict[str, Any] = Field(default_factory=dict)


class TicketFlowState(BaseModel):
    """Echoed on chat responses during the Jira ticket wizard (like ``demo_flow``)."""

    active: bool
    phase: str
    step: str | None = None
    next_field: str | None = None
    action: str | None = None
    slots: dict[str, Any] = Field(default_factory=dict)


class TicketAttachmentUploadResponse(BaseModel):
    file_name: str
    file_path: str
    size_bytes: int
    content_type: str | None = None
    session_id: str
