"""Guide-writing standard, checked when guides load and in CI.

Errors make a guide unusable (it is rejected by the parser already). The checks here are the
writing rules that keep retrieval reliable; they are reported as problems per guide:

- every suggested question has an FAQ answer in the same guide (``**Question?** answer`` or a
  ``### Question?`` entry in a "Frequently asked questions" section), so question routing can
  send that question straight to its answer;
- notes for whoever writes the answers ("Answer direction:", "Guidance for the assistant",
  "When to ask a follow-up question") are not in the body; they belong in ``answer_notes:``
  in the front matter, which is never indexed;
- FAQ sections contain recognisable question entries.

Run: ``python -m app.knowledge.guide_check`` (exit code 1 when a guide breaks a rule).
"""

from __future__ import annotations

import difflib
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from app.config.settings import get_settings
from app.knowledge.parser import GuideError, parse_guide

_FAQ_SECTION_RE = re.compile(r"(?m)^## (Frequently asked[^\n]*)\n(.*?)(?=^## |\Z)", re.DOTALL)
_BOLD_QUESTION_RE = re.compile(r"(?m)^\*\*([^*\n]+\?)\*\*")
_HEADING_QUESTION_RE = re.compile(r"(?m)^### ([^\n]+\?)[^\n]*$")
# A question used as a heading anywhere in the guide ("## How do I give someone access?"):
# the section under it is its answer.
_ANY_HEADING_QUESTION_RE = re.compile(r"(?m)^#{2,3} ([^\n]+\?)\s*$")
# At most this many extra words for a question to count as the same as an answered one
# ("What does Apply to all do in an award?" vs "What does Apply to all do?").
EXTRA_WORDS = 4
_NOTE_RE = re.compile(r"(?m)^(Answer direction\s*:|#{2,3} [^\n]*(assistant|When to ask a follow-up question))",
                      re.IGNORECASE)
# How close a suggested question must be to an FAQ question to count as answered.
MATCH_RATIO = 0.82


def _norm(question: str) -> str:
    q = re.sub(r"\([^)]*\)", " ", question.casefold())
    return " ".join(re.sub(r"[^\w\s]", " ", q).split())


def faq_questions(body: str) -> list[str]:
    """The questions the guide's FAQ sections answer."""
    found: list[str] = []
    for _, text in _FAQ_SECTION_RE.findall(body):
        found += _BOLD_QUESTION_RE.findall(text) + _HEADING_QUESTION_RE.findall(text)
    found += [q for q in _ANY_HEADING_QUESTION_RE.findall(body) if q not in found]
    return found


def _same_question(a: str, b: str) -> bool:
    """One question is the other plus a few words (both with at least four words)."""
    short, long_ = sorted((set(a.split()), set(b.split())), key=len)
    return len(short) >= 4 and short <= long_ and len(long_ - short) <= EXTRA_WORDS


def answered(question: str, faq: list[str]) -> bool:
    target = _norm(question)
    return any(
        _norm(f) == target
        or difflib.SequenceMatcher(None, _norm(f), target).ratio() >= MATCH_RATIO
        or _same_question(_norm(f), target)
        for f in faq
    )


@dataclass
class GuideReport:
    file: str
    doc_id: str = ""
    problems: list[str] = field(default_factory=list)


def check_guide(text: str, file: str = "") -> GuideReport:
    report = GuideReport(file=file)
    try:
        meta, body = parse_guide(text)
    except GuideError as e:
        report.problems.append(f"invalid guide: {e}")
        return report
    report.doc_id = meta.doc_id
    faq = faq_questions(body)
    for section, section_text in _FAQ_SECTION_RE.findall(body):
        if not (_BOLD_QUESTION_RE.search(section_text) or _HEADING_QUESTION_RE.search(section_text)):
            report.problems.append(f"FAQ section '{section}' has no '**Question?**' or '### Question?' entries")
    # Backend (API) guides are references, not routed: their questions need no FAQ entry.
    backend = meta.doc_id.endswith(".api") or ".api-" in meta.doc_id
    for question in () if backend else meta.suggested_questions:
        if not answered(question, faq):
            report.problems.append(f"suggested question has no FAQ answer: {question}")
    notes = sorted({m.group(0).strip()[:60] for m in _NOTE_RE.finditer(body)})
    if notes:
        report.problems.append("answer notes in the body (move them to answer_notes:): " + "; ".join(notes))
    return report


def problem_keys(reports: list[GuideReport]) -> list[str]:
    """Stable "file :: problem" lines, for the baseline of known problems."""
    return sorted(f"{r.file.replace(chr(92), '/')} :: {p}" for r in reports for p in r.problems)


def check_directory(root: Path) -> list[GuideReport]:
    files = sorted(p for p in root.rglob("*.md") if p.name.lower() != "readme.md")
    return [check_guide(p.read_text(encoding="utf-8"), str(p.relative_to(root))) for p in files]


def main() -> int:
    root = Path(get_settings().app_chat.guides_directory)
    reports = check_directory(root)
    bad = [r for r in reports if r.problems]
    for r in bad:
        print(f"{r.file} ({r.doc_id or '?'})")
        for problem in r.problems:
            print(f"   - {problem}")
    print(f"\n{len(reports)} guides checked, {len(bad)} with problems, "
          f"{sum(len(r.problems) for r in bad)} problems in total")
    return 1 if bad else 0


def write_baseline(path: Path) -> int:
    """Record today's problems as known, so only new ones fail the check."""
    keys = problem_keys(check_directory(Path(get_settings().app_chat.guides_directory)))
    path.write_text("\n".join(keys) + "\n", encoding="utf-8")
    print(f"{len(keys)} known problems written to {path}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--write-baseline":
        sys.exit(write_baseline(Path(sys.argv[2])))
    sys.exit(main())
