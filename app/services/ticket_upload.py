"""Secure ticket attachment storage and validation."""

from __future__ import annotations

import logging
import os
import re
import uuid
from pathlib import Path

from app.config.settings import get_settings

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS: frozenset[str] = frozenset(
    {".png", ".jpg", ".jpeg", ".pdf", ".docx", ".mp4"},
)

ALLOWED_MIME: frozenset[str] = frozenset(
    {
        "image/png",
        "image/jpeg",
        "application/pdf",
        "application/vnd.openxmlformats-officedocument"
        ".wordprocessingml.document",
        "video/mp4",
    },
)

_SAFE_NAME = re.compile(r"[^A-Za-z0-9._-]+")


def _ticket_upload_dir() -> Path:
    env_dir = (os.environ.get("TICKET_UPLOAD_DIR") or "").strip()
    if env_dir:
        root = Path(env_dir)
    else:
        s = get_settings()
        base = Path(s.paths.upload_dir).resolve().parent
        root = base / "ticket_attachments"
    root.mkdir(parents=True, exist_ok=True)
    return root


def max_upload_bytes() -> int:
    raw = (os.environ.get("TICKET_MAX_UPLOAD_BYTES") or "").strip()
    if raw.isdigit():
        return int(raw)
    return 10 * 1024 * 1024


def validate_upload(
    filename: str,
    content: bytes,
    content_type: str | None,
) -> str:
    """
    Validate file; return safe extension (with dot).
    Raises ValueError on rejection.
    """
    if not content:
        raise ValueError("Empty file upload")
    if len(content) > max_upload_bytes():
        mb = max_upload_bytes() // (1024 * 1024)
        raise ValueError(f"File exceeds maximum size ({mb} MB)")

    name = (filename or "").strip()
    if not name:
        raise ValueError("Missing filename")

    ext = Path(name).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(
            "Unsupported file type. Allowed: PNG, JPG, PDF, DOCX, MP4",
        )

    if content_type and content_type not in ALLOWED_MIME:
        logger.warning(
            "ticket_upload_mime_mismatch | name=%s type=%s",
            name,
            content_type,
        )
    return ext


def save_ticket_file(filename: str, content: bytes) -> tuple[str, str]:
    """
    Store upload; return (stored_file_name, relative_api_path).
    """
    ext = validate_upload(filename, content, None)
    safe_stem = _SAFE_NAME.sub(
        "_",
        Path(filename).stem[:80],
    ) or "file"
    unique = f"{uuid.uuid4().hex}_{safe_stem}{ext}"
    dest = _ticket_upload_dir() / unique
    dest.write_bytes(content)
    rel = f"/uploads/tickets/{unique}"
    logger.info(
        "ticket_file_saved | name=%s bytes=%s path=%s",
        unique,
        len(content),
        dest,
    )
    return unique, rel


def resolve_ticket_path(file_path: str) -> Path | None:
    """Map API ``file_path`` to on-disk path."""
    raw = (file_path or "").strip()
    if not raw:
        return None
    name = Path(raw).name
    if ".." in name or "/" in name or "\\" in name:
        logger.warning("ticket_path_traversal_blocked | path=%s", raw)
        return None
    full = _ticket_upload_dir() / name
    if full.is_file():
        return full
    logger.warning("ticket_file_missing | name=%s", name)
    return None
