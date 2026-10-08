"""Load the guides folder into the knowledge store.

Runs once per backend start (docker/entrypoint.sh and `python -m app.main`),
before the API serves requests. Can also be run by hand, but only while the
backend is stopped (the local Chroma store is not safe for two processes):

    python -m app.knowledge.guide_loader

Unchanged guides are skipped by content hash; access-only edits update the
registry without re-embedding. A guide whose file was removed is removed from
the store, unless any guide failed to load (then nothing is pruned, so a typo
cannot take a working guide offline).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from app.config.settings import get_settings
from app.knowledge import service
from app.knowledge.parser import GuideError, parse_guide
from app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class LoadReport:
    loaded: list[dict] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def guides_directory() -> Path:
    return Path(get_settings().app_chat.guides_directory).resolve()


def _guide_files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*.md") if p.name.lower() != "readme.md")


def load_guides(root: Path | None = None) -> LoadReport:
    root = root or guides_directory()
    report = LoadReport()
    if not root.is_dir():
        report.errors.append(f"guides folder not found: {root}")
        return report

    seen: dict[str, Path] = {}
    for path in _guide_files(root):
        rel = path.relative_to(root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
            doc_id = parse_guide(text)[0].doc_id
            if doc_id in seen:
                raise GuideError(f"doc_id '{doc_id}' is also used by {seen[doc_id].relative_to(root).as_posix()}")
            seen[doc_id] = path
            report.loaded.append({"file": rel, **service.ingest_guide(text)})
        except (GuideError, OSError, UnicodeDecodeError) as e:
            report.errors.append(f"{rel}: {e}")

    if report.errors:
        logger.error("guides_not_pruned | %s guide(s) failed to load", len(report.errors))
    elif not seen:
        report.errors.append(f"no guides found in {root}; nothing loaded or removed")
    else:
        for doc_id in sorted(set(service.list_guides_admin()) - set(seen)):
            if service.delete_guide(doc_id):
                report.removed.append(doc_id)
    return report


def main() -> int:
    report = load_guides()
    for item in report.loaded:
        work = "re-embedded" if item["re_embedded"] else "unchanged content"
        print(f"ok       {item['doc_id']}  ({item['file']})  chunks={item['chunks_indexed']}  {work}")
    for doc_id in report.removed:
        print(f"removed  {doc_id}  (its file no longer exists)")
    for error in report.errors:
        print(f"ERROR    {error}")
    return 1 if report.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
