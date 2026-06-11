"""API request and response models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

from app.models.ticket_schemas import (
    TicketDraftPayload,
    TicketFlowState,
    TicketWorkflowResponse,
)


class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str


class UploadResponse(BaseModel):
    filename: str
    chunks_indexed: int
    message: str


class IngestWebsiteRequest(BaseModel):
    url: str = Field(min_length=1)
    content: str = Field(min_length=1)


class IngestWebsiteResponse(BaseModel):
    url: str
    chunks_indexed: int
    message: str


class CrawlRequest(BaseModel):
    """Start the Node Crawlee worker for ``domain`` (hostname or full URL)."""

    domain: str = Field(min_length=1, description="e.g. example.com or https://example.com/")
    max_pages: int | None = Field(
        default=None,
        ge=1,
        le=50_000,
        description="Cap crawl depth; default 100 from env",
    )


class CrawlResponse(BaseModel):
    status: str
    message: str
    pid: int | None = None


class QueryRequest(BaseModel):
    question: str = Field(
        min_length=1,
        description="User message. Alias: ``message``.",
    )
    session_id: str | None = Field(default=None)
    ticket_draft: TicketDraftPayload | None = Field(
        default=None,
        description=(
            "When the UI collects the ticket form client-side, send the "
            "filled draft with question **yes** to create the Jira issue."
        ),
    )

    @model_validator(mode="before")
    @classmethod
    def normalize_chat_body(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        out = dict(data)
        raw_q = (
            out.get("question")
            or out.get("message")
            or out.get("text")
            or out.get("content")
            or ""
        )
        out["question"] = str(raw_q).strip()
        draft = out.get("ticket_draft")
        if draft in (None, {}, ""):
            out["ticket_draft"] = None
        elif isinstance(draft, dict):
            title = str(draft.get("title") or "").strip()
            if not title:
                out["ticket_draft"] = None
        return out

    @field_validator("question")
    @classmethod
    def question_not_blank(cls, v: str) -> str:
        t = (v or "").strip()
        if not t:
            raise ValueError("question must not be empty")
        return t


class RetrievedChunk(BaseModel):
    """One retrieved segment: metadata + full chunk text (no truncation)."""

    filename: str | None = None
    source: str | None = None
    chunk_index: int | None = None
    content: str = ""


class DemoFlowState(BaseModel):
    """Book-a-demo wizard state (stupa-chat only)."""

    active: bool
    phase: str
    step: str | None = None
    interest_options: list[str] | None = None
    slots: dict[str, str] = Field(default_factory=dict)


class QueryResponse(BaseModel):
    answer: str
    chunks: list[RetrievedChunk]
    # Echo on every follow-up (body `session_id`, header, or cookie).
    session_id: str | None = None
    # Only set on /stupa-chat during book-a-demo flow.
    demo_flow: DemoFlowState | None = None
    # Only set on /stupa-chat during Jira ticket wizard.
    ticket_flow: TicketFlowState | None = None
    ticket_workflow: TicketWorkflowResponse | None = None


class ErrorResponse(BaseModel):
    detail: str
    code: str | None = None
