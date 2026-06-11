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


class TicketAttachmentRef(BaseModel):
    file_name: str = Field(min_length=1, max_length=255)
    file_path: str = Field(min_length=1, max_length=512)


class TicketDraftPayload(BaseModel):
    """Optional on ``POST /stupa-chat`` when the UI confirms with **yes**."""

    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1, max_length=8000)
    expected_vs_actual: str = Field(min_length=1, max_length=4000)
    attachments: list[TicketAttachmentRef] = Field(default_factory=list)


class TicketAttachmentUploadResponse(BaseModel):
    file_name: str
    file_path: str
    size_bytes: int
    content_type: str | None = None
    session_id: str
