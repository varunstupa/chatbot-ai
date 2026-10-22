"""Guide-writing standard (app.knowledge.guide_check) for every guide in guides/.

Known problems are listed in tests/eval/guide_check_baseline.txt. A new or edited guide must
follow the rules: any problem not in that list fails this test. When you fix a known problem,
regenerate the list:

    python -m app.knowledge.guide_check --write-baseline tests/eval/guide_check_baseline.txt
"""

from __future__ import annotations

from pathlib import Path

from app.knowledge.guide_check import check_directory, check_guide, problem_keys

ROOT = Path(__file__).resolve().parents[1]
GUIDES = ROOT / "guides"
BASELINE = ROOT / "tests" / "eval" / "guide_check_baseline.txt"


def _known() -> set[str]:
    return {line.strip() for line in BASELINE.read_text(encoding="utf-8").splitlines() if line.strip()}


def test_every_guide_is_valid():
    invalid = [k for k in problem_keys(check_directory(GUIDES)) if ":: invalid guide:" in k]
    assert invalid == []


def test_no_new_guide_problems():
    new = sorted(set(problem_keys(check_directory(GUIDES))) - _known())
    assert new == [], "guides break the writing rules (see app/knowledge/guide_check.py):\n" + "\n".join(new)


GUIDE = """---
doc_id: tms.example
title: Example page
routes: [tms/example]
tenants: all
suggested_questions:
  - How do I publish the example?
  - Why is the example hidden?
---
## Overview

The Example page.

## Frequently asked questions

**How do I publish the example?** Turn on Publish.
"""


def test_suggested_question_needs_an_faq_answer():
    problems = check_guide(GUIDE).problems
    assert problems == ["suggested question has no FAQ answer: Why is the example hidden?"]


def test_heading_style_faq_counts_as_an_answer():
    text = GUIDE.replace("**How do I publish the example?** Turn on Publish.",
                         "### How do I publish the example?\n\nTurn on Publish.\n\n"
                         "### Why is the example hidden? (not visible)\n\nIt is not published.")
    assert check_guide(text).problems == []


def test_answer_notes_in_the_body_are_reported():
    text = GUIDE.replace("The Example page.", "The Example page.\n\nAnswer direction: be brief.")
    assert any("answer notes in the body" in p for p in check_guide(text).problems)


def test_backend_guides_need_no_faq_for_their_questions():
    text = GUIDE.replace("doc_id: tms.example", "doc_id: tms.example.api")
    assert check_guide(text).problems == []
