"""Unit tests for ticket attachment validation."""

from __future__ import annotations

import pytest

from app.services.ticket_upload import validate_upload


def test_validate_rejects_empty():
    with pytest.raises(ValueError, match="Empty"):
        validate_upload("a.png", b"", None)


def test_validate_rejects_bad_extension():
    with pytest.raises(ValueError, match="Unsupported"):
        validate_upload("virus.exe", b"x", None)


def test_validate_accepts_png():
    ext = validate_upload("shot.png", b"\x89PNG", "image/png")
    assert ext == ".png"
