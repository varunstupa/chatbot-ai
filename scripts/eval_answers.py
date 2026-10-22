"""Answer check (needs Ollama): the 50 questions of tests/eval/answer_cases.json, end to end.

Runs each question through the app in-process (signed like the gateway), with a fresh
conversation each time, and scores the answer:
- accuracy: the expected facts are present; off-topic questions get the plain no-answer reply;
  the API question gets "Did you mean"; nothing names an API, says "switch" or "Context";
- behaviour: numbered steps for how-to questions, words per question type, seconds per answer.

    python scripts/eval_answers.py [results.jsonl]

Run it before and after a prompt, model or guide change and compare the two summaries.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("APP_ENV", "development")

from dotenv import dotenv_values  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.config.settings import get_settings  # noqa: E402
from app.main import app  # noqa: E402
from app.services import app_chat  # noqa: E402

CASES = ROOT / "tests" / "eval" / "answer_cases.json"
SECRET = dotenv_values(ROOT / ".env").get("CHATBOT_INTERNAL_SECRET") or os.environ.get("CHATBOT_INTERNAL_SECRET", "")
TENANT, USER, ROLE = "staging", "1", "1"


def _headers() -> dict:
    ts = str(int(time.time()))
    sig = hmac.new(SECRET.encode(), "\n".join(("v1", ts, TENANT, USER, ROLE)).encode(), hashlib.sha256).hexdigest()
    return {"x-chat-tenant": TENANT, "x-chat-user": USER, "x-chat-role": ROLE,
            "x-chat-timestamp": ts, "x-chat-signature": sig}


def grade(case: dict, answer: str, suggestions, no_answer: str) -> tuple[float, list[str]]:
    low = answer.casefold()
    if case["type"] == "refuse":
        ok = answer.strip() == no_answer
        return float(ok), [] if ok else ["should refuse"]
    if case["type"] == "suggest":
        ok = bool(suggestions) and not app_chat.reveals_internal_detail(answer)
        return float(ok), [] if ok else ["no Did-you-mean"]
    if answer.strip() == no_answer or suggestions:
        return 0.0, ["refused an answerable question"]
    groups = case["must"]
    missing = [g[0] for g in groups if not any(x.casefold() in low for x in g)]
    score = 1 - len(missing) / len(groups)
    problems = [f"missing {', '.join(missing)}"] if missing else []
    for pattern, label in ((r"\bswitch", "says switch"), (r"\bcontext\b", "mentions Context")):
        if re.search(pattern, low):
            score -= 0.25
            problems.append(label)
    if app_chat.reveals_internal_detail(answer):
        score, problems = 0.0, problems + ["API detail"]
    return max(score, 0.0), problems


def main() -> int:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    cases = json.loads(CASES.read_text(encoding="utf-8"))
    no_answer = get_settings().app_chat.no_answer_message
    rows = []
    with TestClient(app, raise_server_exceptions=False) as client:
        for case in cases:
            client.cookies.clear()  # a fresh conversation for every question
            body = {"question": case["q"], "screen": {"route": case["route"], "url": None}, "sport_id": case["sport"]}
            started = time.perf_counter()
            r = client.post("/api/app-chat", json=body, headers=_headers())
            secs = round(time.perf_counter() - started, 2)
            data = r.json() if r.status_code == 200 else {}
            answer = data.get("answer") or f"HTTP {r.status_code}"
            score, problems = grade(case, answer, data.get("suggestions"), no_answer)
            rows.append({**case, "answer": answer, "score": score, "problems": problems, "secs": secs})
            print(f'{case["id"]} {secs:5.1f}s score={score:.2f} {problems}', flush=True)
    if out:
        out.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")

    answered = [r for r in rows if r["type"] == "answer"]
    how = [r for r in answered if r.get("kind") == "how-to"]
    numbered = sum(bool(re.search(r"(^|\n)\s*1[.)]", r["answer"])) for r in how)
    print("\n==== SUMMARY ====")
    print(f"accuracy {100 * sum(r['score'] for r in rows) / len(rows):.1f}%   "
          f"fully correct {sum(r['score'] >= 0.999 for r in rows)}/{len(rows)}")
    print(f"how-to with numbered steps {numbered}/{len(how)}   "
          f"mean {sum(r['secs'] for r in rows) / len(rows):.1f}s per answer")
    for kind in ("how-to", "problem", "where-is", "what-is", "list"):
        group = [r for r in answered if r.get("kind") == kind]
        if group:
            print(f"  avg words {kind:8} {sum(len(r['answer'].split()) for r in group) / len(group):.0f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
