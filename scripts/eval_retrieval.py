"""Retrieval regression check: does each test question get its guide? No LLM needed.

Builds a fresh knowledge base from guides/ in a temporary folder (with the real embedding model),
runs every case of tests/eval/retrieval_cases.json through the admin-chat retrieval, and compares
the result with tests/eval/retrieval_thresholds.json. Exit code 1 when a count drops below its
threshold, or when a "routed" case does not get its guide first.

    python scripts/eval_retrieval.py            # check
    python scripts/eval_retrieval.py --update   # record the current counts as the new thresholds

Raise the thresholds (--update) after an improvement; never lower them to make a change pass.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("APP_ENV", "development")

from app.config.settings import get_settings  # noqa: E402

CASES = ROOT / "tests" / "eval" / "retrieval_cases.json"
THRESHOLDS = ROOT / "tests" / "eval" / "retrieval_thresholds.json"
SPORT_ID = 4  # the cases were written for a Badminton organisation


def _matches(doc_id: str, expected: list[str]) -> bool:
    return any(doc_id == e or doc_id.startswith(e + ".") for e in expected)


def main() -> int:
    update = "--update" in sys.argv
    settings = get_settings()
    # ignore_cleanup_errors: on Windows Chroma still holds its files open at the end.
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as kb:
        settings.app_chat.persist_directory = kb  # never touches the local knowledge base
        # No LLM in this check: the weak-question rewrite (a model call) stays off.
        settings.app_chat.rewrite_weak_questions = False

        from app.knowledge import guide_loader
        from app.services import app_chat
        from app.services.auth import CallerScope

        loaded = guide_loader.load_guides()
        if loaded.errors:
            print("guides failed to load:\n  " + "\n  ".join(loaded.errors))
            return 1
        scope = CallerScope(tenant="staging", user_id="1", role="1")
        sport = app_chat.sport_from_id(SPORT_ID)

        found = top1 = 0
        routed_failures: list[str] = []
        misses: list[str] = []
        cases = json.loads(CASES.read_text(encoding="utf-8"))
        for case in cases:
            # The widget sends the route pattern and the URL; cases hold either, so pass both.
            result = app_chat.retrieve(scope, case["q"], case["route"], case["route"], sport)
            docs = [h.doc_id for h in result.hits]
            hit = any(_matches(d, case["expect"]) for d in docs)
            first = bool(docs) and _matches(docs[0], case["expect"])
            found += hit
            top1 += first
            if case.get("kind") == "routed" and not first:
                routed_failures.append(f'{case["id"]} {case["q"]} -> {docs[:1]}')
            if not first:
                misses.append(f'{case["id"]} [{case.get("kind")}] {case["q"]} -> {docs[:3]}')

    total = len(cases)
    print(f"expected guide found: {found}/{total}   right guide first: {top1}/{total}")
    for line in misses:
        print("  not first:", line)
    current = {"found": found, "top1": top1, "total": total, "tolerance": 1}
    if update:
        THRESHOLDS.write_text(json.dumps(current, indent=1) + "\n", encoding="utf-8")
        print(f"thresholds updated: {current}")
        return 0

    limits = json.loads(THRESHOLDS.read_text(encoding="utf-8"))
    # A freshly built vector index can rank one borderline passage differently from run to run,
    # so one case below the recorded best is allowed; real regressions move several cases.
    slack = int(limits.get("tolerance", 1))
    failed = []
    if found < limits["found"] - slack:
        failed.append(f"expected guide found dropped: {found} < {limits['found']} - {slack}")
    if top1 < limits["top1"] - slack:
        failed.append(f"right guide first dropped: {top1} < {limits['top1']} - {slack}")
    failed += [f"routed question lost its answer: {r}" for r in routed_failures]
    for line in failed:
        print("FAIL:", line)
    if not failed and (found > limits["found"] or top1 > limits["top1"]):
        print("Better than the thresholds: run with --update to raise them.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
