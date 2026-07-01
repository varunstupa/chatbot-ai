"""One-time seeding of bundled documents into the uploads Chroma collection.

Called by docker/entrypoint.sh on first container start. Iterates over every file
already present in the configured upload directory (data/uploads) and runs the same
parse -> chunk -> embed -> index path used by POST /upload. Idempotency at the
"run once" level is handled by the caller via the .seeded_docs marker file, so this
script simply ingests whatever is there and reports per-file results.

Exit code 0 as long as the run completed (individual file failures are logged and
skipped) so the caller can safely write the marker. Exit non-zero only on a hard
setup error (e.g. the app package cannot be imported).
"""

from __future__ import annotations

import sys
from pathlib import Path

# Running as `python /app/docker/seed_docs.py` with cwd=/app makes `app` importable.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config.settings import get_settings  # noqa: E402
from app.services import ingestion  # noqa: E402
from app.utils.logger import get_logger  # noqa: E402

logger = get_logger(__name__)

# Extensions MarkItDown can parse into text for ingestion.
SUPPORTED_SUFFIXES = {
    ".docx",
    ".doc",
    ".pdf",
    ".txt",
    ".md",
    ".html",
    ".htm",
    ".pptx",
    ".xlsx",
    ".csv",
}


def _iter_seed_files(upload_dir: Path):
    for path in sorted(upload_dir.iterdir()):
        if not path.is_file():
            continue
        if path.name.startswith("."):  # .gitkeep and friends
            continue
        if path.suffix.lower() not in SUPPORTED_SUFFIXES:
            logger.info("seed_skip_unsupported", extra={"file": path.name})
            continue
        yield path


def main() -> int:
    settings = get_settings()
    upload_dir = Path(settings.paths.upload_dir).resolve()
    if not upload_dir.is_dir():
        logger.info("seed_no_upload_dir", extra={"dir": str(upload_dir)})
        return 0

    files = list(_iter_seed_files(upload_dir))
    if not files:
        logger.info("seed_no_documents", extra={"dir": str(upload_dir)})
        return 0

    total_chunks = 0
    failures = 0
    for path in files:
        try:
            n = ingestion.ingest_path(path)
            total_chunks += n
            logger.info("seed_ingested", extra={"file": path.name, "chunks": n})
        except Exception:
            failures += 1
            logger.exception("seed_ingest_failed", extra={"file": path.name})

    logger.info(
        "seed_complete",
        extra={
            "files": len(files),
            "failures": failures,
            "total_chunks": total_chunks,
        },
    )
    # Completed the run; let the caller mark seeding done even if some files failed.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
