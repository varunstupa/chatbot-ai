"""API request and response models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str


class UploadResponse(BaseModel):
    filename: str
    chunks_indexed: int
    message: str


class QueryRequest(BaseModel):
    question: str = Field(min_length=1)
    session_id: str | None = Field(default=None)


class RetrievedChunk(BaseModel):
    """One retrieved segment: metadata + full chunk text (no truncation)."""

    filename: str | None = None
    source: str | None = None
    chunk_index: int | None = None
    content: str = ""


class QueryResponse(BaseModel):
    answer: str
    chunks: list[RetrievedChunk]


class ErrorResponse(BaseModel):
    detail: str
    code: str | None = None
