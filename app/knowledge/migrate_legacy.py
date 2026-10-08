"""Remove the per-tenant collections and registry of the old knowledge store.

Run once, after `npm run kb:sync` has filled the single `knowledge_chunks`
collection and the new document registry:

    python -m app.knowledge.migrate_legacy            # show what would be removed
    python -m app.knowledge.migrate_legacy --apply    # remove it
"""

from __future__ import annotations

import argparse
from pathlib import Path

import chromadb

from app.config.settings import get_settings

LEGACY_REGISTRY = "registry.json"


def _is_legacy(name: str) -> bool:
    return name == "kb_common" or name.startswith("kb_t_")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--apply", action="store_true", help="delete instead of listing")
    args = parser.parse_args()

    cfg = get_settings().app_chat
    kb_dir = Path(cfg.persist_directory).resolve()
    client = chromadb.PersistentClient(path=str(kb_dir))
    names = [c.name for c in client.list_collections()]
    legacy = sorted(n for n in names if _is_legacy(n))

    new_count = client.get_collection(cfg.collection_name).count() if cfg.collection_name in names else 0
    if not legacy and not (kb_dir / LEGACY_REGISTRY).exists():
        print("Nothing to migrate.")
        return 0
    if new_count == 0:
        print(f"Refusing: '{cfg.collection_name}' is empty. Run `npm run kb:sync` first.")
        return 1

    for name in legacy:
        print(f"{'delete' if args.apply else 'would delete'} collection {name} "
              f"({client.get_collection(name).count()} chunks)")
        if args.apply:
            client.delete_collection(name)
    old_registry = kb_dir / LEGACY_REGISTRY
    if old_registry.exists():
        print(f"{'delete' if args.apply else 'would delete'} {old_registry}")
        if args.apply:
            old_registry.unlink()
    if not args.apply:
        print("Dry run. Re-run with --apply to delete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
