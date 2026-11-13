"""Uploaded file -> Markdown body that the guide chunker understands.

`.md` is used as written (its front matter is returned separately). `.pdf` gives one
``## Page N`` section per page with text. `.docx` keeps the Word headings as ``##`` and
``###`` sections, lists as ``-`` items and tables as Markdown tables. The old binary
`.doc` format is refused: it has to be saved as `.docx` first.
"""

from __future__ import annotations

import io
import re
from dataclasses import dataclass
from pathlib import PurePath
from typing import Any

import yaml

from app.knowledge.parser import GuideError

MARKDOWN, PDF, DOCX = "md", "pdf", "docx"
KINDS = {".md": MARKDOWN, ".markdown": MARKDOWN, ".pdf": PDF, ".docx": DOCX}
_FRONT_MATTER_RE = re.compile(r"^﻿?---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)
_BLANK_LINES_RE = re.compile(r"\n{3,}")


@dataclass(frozen=True)
class Extracted:
    kind: str
    body: str
    front_matter: dict[str, Any]  # only from a .md file; {} otherwise
    title: str  # suggested by the file itself (PDF or Word title, first # heading); may be ""


def kind_of(file_name: str) -> str:
    suffix = PurePath(file_name or "").suffix.lower()
    if suffix == ".doc":
        raise GuideError("Old Word .doc files are not supported; save the file as .docx and upload it again")
    if suffix not in KINDS:
        raise GuideError("Only .md, .pdf and .docx files can be uploaded")
    return KINDS[suffix]


def extract(file_name: str, data: bytes) -> Extracted:
    kind = kind_of(file_name)
    if not data:
        raise GuideError("The file is empty")
    if kind == MARKDOWN:
        result = _markdown(data)
    elif kind == PDF:
        result = _pdf(data)
    else:
        result = _docx(data)
    body = _BLANK_LINES_RE.sub("\n\n", result.body).strip()
    if not body:
        raise GuideError("No text found in the file" + (" (a scanned PDF has no text to read)" if kind == PDF else ""))
    return Extracted(kind, body, result.front_matter, result.title)


def _markdown(data: bytes) -> Extracted:
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as e:
        raise GuideError("The Markdown file must be UTF-8 text") from e
    front_matter: dict[str, Any] = {}
    match = _FRONT_MATTER_RE.match(text)
    if match:
        try:
            loaded = yaml.safe_load(match.group(1)) or {}
        except yaml.YAMLError as e:
            raise GuideError(f"Front matter is not valid YAML: {e}") from e
        if not isinstance(loaded, dict):
            raise GuideError("Front matter must be a mapping")
        front_matter, text = loaded, match.group(2)
    heading = re.search(r"^# (.+)$", text, re.MULTILINE)
    return Extracted(MARKDOWN, text, front_matter, heading.group(1).strip() if heading else "")


def _pdf(data: bytes) -> Extracted:
    import pdfplumber

    try:
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            title = str((pdf.metadata or {}).get("Title") or "").strip()
            pages = [(n, (page.extract_text() or "").strip()) for n, page in enumerate(pdf.pages, 1)]
    except Exception as e:
        raise GuideError("The PDF could not be read") from e
    body = "\n\n".join(f"## Page {n}\n\n{text}" for n, text in pages if text)
    return Extracted(PDF, body, {}, title)


def _docx(data: bytes) -> Extracted:
    import docx
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    try:
        document = docx.Document(io.BytesIO(data))
    except Exception as e:
        raise GuideError("The Word file could not be read") from e
    title = str(document.core_properties.title or "").strip()
    lines: list[str] = []
    for element in document.element.body.iterchildren():
        tag = element.tag.rsplit("}", 1)[-1]
        if tag == "p":
            line, heading_title = _docx_paragraph(Paragraph(element, document))
            if heading_title and not title:
                title = heading_title
            if line:
                lines.append(line)
        elif tag == "tbl":
            lines.append(_docx_table(Table(element, document)))
    return Extracted(DOCX, "\n\n".join(lines), {}, title)


def _docx_paragraph(paragraph: Any) -> tuple[str, str]:
    """(Markdown line, document title if this paragraph is the Word title)."""
    text = " ".join(paragraph.text.split())
    if not text:
        return "", ""
    style = (paragraph.style.name if paragraph.style is not None else "").lower()
    if style == "title":
        return "", text
    level = re.match(r"heading (\d)", style)
    if level:
        n = int(level.group(1))
        # Heading 1 and 2 start sections and subsections; deeper headings stay bold lines.
        return ("## " if n == 1 else "### " if n == 2 else "**") + text + ("**" if n > 2 else ""), ""
    if style.startswith("list"):
        return f"- {text}", ""
    return text, ""


def _docx_table(table: Any) -> str:
    rows = [[" ".join(cell.text.split()).replace("|", "/") for cell in row.cells] for row in table.rows]
    rows = [r for r in rows if any(r)]
    if not rows:
        return ""
    width = max(len(r) for r in rows)
    rows = [r + [""] * (width - len(r)) for r in rows]
    out = ["| " + " | ".join(rows[0]) + " |", "|" + "---|" * width]
    out += ["| " + " | ".join(r) + " |" for r in rows[1:]]
    return "\n".join(out)
