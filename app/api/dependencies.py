"""FastAPI dependency providers."""

from __future__ import annotations

from app.services.rag_pipeline import RAGPipeline


def get_rag_pipeline() -> RAGPipeline:
    return RAGPipeline()
