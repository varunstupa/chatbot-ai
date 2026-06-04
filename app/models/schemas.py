"""API request and response models."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.models.ticket_schemas import TicketFlowState, TicketWorkflowResponse


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
    question: str = Field(min_length=1)
    session_id: str | None = Field(default=None)


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
