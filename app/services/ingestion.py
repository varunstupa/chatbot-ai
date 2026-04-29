"""Orchestrate parse → chunk → vector index for uploaded files."""

from __future__ import annotations

from pathlib import Path

from app.config.settings import get_settings
from app.services.chunking import split_documents
from app.services.vector_store import add_documents
from app.utils.file_loader import documents_from_file
from app.utils.logger import get_logger

logger = get_logger(__name__)


def _ensure_upload_dir() -> Path:
    s = get_settings()
    upload_dir = Path(s.paths.upload_dir).resolve()
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


def save_upload(filename: str, data: bytes) -> Path:
    if not data:
        raise ValueError("Empty upload")
    upload_dir = _ensure_upload_dir()
    safe_name = Path(filename).name
    if not safe_name:
        raise ValueError("Invalid filename")
    dest = upload_dir / safe_name
    dest.write_bytes(data)
    logger.info("file_saved", extra={"path": str(dest), "size": len(data)})
    return dest


def ingest_path(file_path: Path) -> int:
    """Parse file, chunk, and add to the vector store. Returns number of chunks indexed."""
    docs = documents_from_file(file_path)
    chunks = split_documents(docs)
    add_documents(chunks)
    logger.info(
        "ingestion_complete",
        extra={"file": file_path.name, "chunks": len(chunks)},
    )
    return len(chunks)
