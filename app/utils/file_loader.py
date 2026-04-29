"""Parse uploaded files with MarkItDown and emit LangChain Documents."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from langchain_core.documents import Document
from markitdown import MarkItDown

from app.utils.logger import get_logger

logger = get_logger(__name__)


def documents_from_file(file_path: Path) -> list[Document]:
    """
    Convert a file on disk to LangChain Documents with metadata.

    Metadata includes filename and optional fields returned by the converter.
    """
    path = file_path.resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Not a file: {path}")

    md = MarkItDown()
    try:
        result = md.convert(str(path))
    except Exception as e:
        logger.exception("markitdown_convert_failed", extra={"path": str(path)})
        raise ValueError(f"Unsupported or unreadable format: {e}") from e

    text = (result.text_content or "").strip()
    if not text:
        raise ValueError("Parsed content is empty")

    meta: dict[str, Any] = {
        "filename": path.name,
        "source": str(path),
    }
    if getattr(result, "title", None):
        meta["title"] = result.title

    return [Document(page_content=text, metadata=meta)]
