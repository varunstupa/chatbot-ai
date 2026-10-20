"""Guide Markdown -> validated metadata + content chunks. No storage, no access checks."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Any

import yaml
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.services.auth import normalize_tenant

ALL_TENANTS = "all"
# Sports a guide can be limited to (front matter `sports`), keyed by the admin app's sport_id.
SPORTS_BY_ID = {1: "table_tennis", 2: "padel", 3: "tennis", 4: "badminton"}
SPORTS = frozenset(SPORTS_BY_ID.values())
# Bump when chunking changes, so unchanged guides are re-embedded on the next sync.
CHUNKER_VERSION = "2"

_DOC_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{1,99}$")
_ROLE_RE = re.compile(r"^[a-z0-9][a-z0-9 _-]{0,59}$")
_FRONT_MATTER_RE = re.compile(r"^﻿?---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)
_QUESTION_RE = re.compile(r"^\*\*[^*\n]+\?\*\*")


class GuideError(ValueError):
    """Guide rejected at ingest (bad or missing front matter)."""


@dataclass(frozen=True)
class GuideMeta:
    doc_id: str
    title: str
    routes: tuple[str, ...]
    aliases: tuple[str, ...]
    tenants: tuple[str, ...] | None  # None means every tenant
    exclude_tenants: tuple[str, ...]
    roles: tuple[str, ...]  # empty means every role
    overrides: str
    suggested_questions: tuple[str, ...]
    sports: tuple[str, ...] = ()  # empty means every sport


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    text: str
    metadata: dict[str, Any]


def normalize_route(route: str) -> str:
    return (route or "").split("?")[0].split("#")[0].strip().strip("/")


def normalize_role(raw: Any) -> str | None:
    role = re.sub(r"\s+", " ", str(raw or "").strip().lower())
    return role if _ROLE_RE.match(role) else None


def _str_list(value: Any, field: str) -> tuple[str, ...]:
    if value in (None, ""):
        return ()
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list):
        raise GuideError(f"`{field}` must be a list")
    return tuple(str(v).strip() for v in value if str(v).strip())


def _tenant_list(value: Any, field: str) -> tuple[str, ...]:
    names = [normalize_tenant(n) for n in _str_list(value, field)]
    if any(n is None for n in names):
        raise GuideError(f"`{field}` contains an invalid tenant name")
    return tuple(sorted(set(names)))  # type: ignore[arg-type]


def parse_guide(text: str) -> tuple[GuideMeta, str]:
    """Split front matter from body and validate it. Fails closed on tenants."""
    match = _FRONT_MATTER_RE.match(text or "")
    if not match:
        raise GuideError("Guide must start with a `---` front matter block")
    try:
        fm = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as e:
        raise GuideError(f"Front matter is not valid YAML: {e}") from e
    if not isinstance(fm, dict):
        raise GuideError("Front matter must be a mapping")
    body = match.group(2).strip()
    if not body:
        raise GuideError("Guide body is empty")

    doc_id = str(fm.get("doc_id") or "").strip().lower()
    if not _DOC_ID_RE.match(doc_id):
        raise GuideError("`doc_id` is required (lowercase letters, digits, . _ -)")
    title = str(fm.get("title") or "").strip()
    if not title:
        raise GuideError("`title` is required")

    raw_tenants = fm.get("tenants")
    if raw_tenants in (None, "", []):
        raise GuideError("`tenants` is required: use `all` or a list of tenant names")
    if isinstance(raw_tenants, str) and raw_tenants.strip().lower() == ALL_TENANTS:
        tenants: tuple[str, ...] | None = None
    else:
        tenants = _tenant_list(raw_tenants, "tenants")
        if not tenants:
            raise GuideError("`tenants` is required: use `all` or a list of tenant names")

    excluded = _tenant_list(fm.get("exclude_tenants"), "exclude_tenants")
    if excluded and tenants is not None:
        raise GuideError("`exclude_tenants` is only valid with `tenants: all`")

    roles = [normalize_role(r) for r in _str_list(fm.get("roles"), "roles")]
    if any(r is None for r in roles):
        raise GuideError("`roles` contains an invalid role name")

    sports = [str(x).strip().lower() for x in _str_list(fm.get("sports"), "sports")]
    unknown = sorted(set(sports) - SPORTS)
    if unknown:
        raise GuideError(f"`sports` has unknown values {unknown}; use {sorted(SPORTS)}")

    meta = GuideMeta(
        doc_id=doc_id,
        title=title,
        routes=tuple(normalize_route(r) for r in _str_list(fm.get("routes"), "routes")),
        aliases=tuple(a.lower() for a in _str_list(fm.get("aliases"), "aliases")),
        tenants=tenants,
        exclude_tenants=excluded,
        roles=tuple(sorted(set(roles))),  # type: ignore[arg-type]
        overrides=str(fm.get("overrides") or "").strip().lower(),
        suggested_questions=_str_list(fm.get("suggested_questions"), "suggested_questions"),
        sports=tuple(sorted(set(sports))),
    )
    return meta, body


def content_hash(meta: GuideMeta, body: str) -> str:
    """Fingerprint of everything that ends up in a chunk's text or embedding."""
    digest = hashlib.sha256()
    for part in (CHUNKER_VERSION, meta.title, body):
        digest.update(part.encode("utf-8"))
        digest.update(b"\0")
    return digest.hexdigest()


def _sections(body: str) -> list[tuple[str, str]]:
    """Split a guide body on ``## `` headings into (section title, text)."""
    sections: list[tuple[str, str]] = []
    heading = "Overview"
    lines: list[str] = []
    for line in body.splitlines():
        if line.startswith("## "):
            if "".join(lines).strip():
                sections.append((heading, "\n".join(lines).strip()))
            heading = line[3:].strip() or "Section"
            lines = []
        elif line.startswith("# ") and not sections and not "".join(lines).strip():
            continue  # document title; already in front matter
        else:
            lines.append(line)
    if "".join(lines).strip():
        sections.append((heading, "\n".join(lines).strip()))
    return sections


def _question_answer_parts(text: str) -> list[str] | None:
    """One part per `**Question?** answer` paragraph of an FAQ section, else None.

    A user's question is closest to the same question in the guide, so each
    pair is stored alone instead of being diluted in a long FAQ passage.
    """
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    if sum(1 for p in paragraphs if _QUESTION_RE.match(p)) < 2:
        return None
    parts: list[str] = []
    for paragraph in paragraphs:
        if _QUESTION_RE.match(paragraph) or not parts:
            parts.append(paragraph)
        else:
            parts[-1] += "\n\n" + paragraph
    return parts


def build_chunks(
    meta: GuideMeta,
    body: str,
    doc_hash: str,
    *,
    chunk_size: int,
    chunk_overlap: int,
) -> list[Chunk]:
    """Content chunks with content-only metadata. Access rules live in the registry."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    route = meta.routes[0] if meta.routes else ""
    chunks: list[Chunk] = []
    for section, text in _sections(body):
        qa_parts = _question_answer_parts(text)
        if qa_parts:
            parts, lead = qa_parts, meta.title
        else:
            parts = [text] if len(text) <= chunk_size else splitter.split_text(text)
            # Title and section lead the text so the embedding sees them.
            lead = f"{meta.title} – {section}"
        for part in parts:
            index = len(chunks)
            chunk_id = f"{meta.doc_id}::{doc_hash[:12]}::{index:04d}"
            chunks.append(
                Chunk(
                    chunk_id=chunk_id,
                    text=f"{lead}\n\n{part}",
                    metadata={
                        "chunk_id": chunk_id,
                        "doc_id": meta.doc_id,
                        "title": meta.title,
                        "section": section,
                        "chunk_index": index,
                        "route": route,
                    },
                )
            )
    return chunks
