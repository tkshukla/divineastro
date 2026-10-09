"""End to end: a date-window question through /api/ask and /api/ask/stream
(DIVASTRO-119).

QuestionLog #54 — "how is my 10th oct to 20th oct" — came back as a
personality reading. This drives the real endpoints in-process (FastAPI
TestClient, a throwaway SQLite DB, provider "off" or a mocked rewrite — the
real Anthropic API is never called) and asserts:

  * the answer is a window reading naming 10 and 20 October, not the
    personality heading;
  * Hindi gets the window reading in Devanagari;
  * /api/ask/stream stores the *polished* text in QuestionLog.answer once the
    rewrite finishes, keeps the engine text in answer_engine, and still
    charges exactly one credit;
  * a rewrite that fails leaves the engine text in the log.

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.test_period_answer
"""

from __future__ import annotations

import json
import os
import random
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

_tmp = tempfile.mkdtemp(prefix="astro_period_")
os.environ["ASTRO_DATABASE_URL"] = f"sqlite:///{Path(_tmp).as_posix()}/t.db"
os.environ["ASTRO_DEV_LOGIN"] = "1"
os.environ["ASTRO_COOKIE_SECURE"] = "0"
os.environ["ASTRO_GATEWAY"] = "test"
os.environ.pop("ANTHROPIC_API_KEY", None)        # belt and braces: never the real API

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import select  # noqa: E402

from app import llm  # noqa: E402
from app.db import QuestionLog, session as db_session  # noqa: E402
from app.main import app  # noqa: E402

failures: list[str] = []
NOW = "2026-10-03T10:00:00+05:30"
Q = "how is my 10th oct to 20th oct"
POLISHED = ("Between 10 Oct 2026 and 20 Oct 2026 the Moon moves through friendly signs for "
            "you; 14 Oct 2026 is the strongest day, and Dussehra on 20 Oct 2026 closes the "
            "stretch on a good note. Keep 16 Oct 2026 light.")


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def sse(text: str) -> list[tuple[str, dict]]:
    out = []
    for block in text.strip().split("\n\n"):
        ev = data = None
        for line in block.splitlines():
            if line.startswith("event: "):
                ev = line[7:]
            elif line.startswith("data: "):
                data = json.loads(line[6:])
        if ev:
            out.append((ev, data))
    return out


def latest_log(question: str) -> QuestionLog | None:
    with db_session() as db:
        return db.execute(select(QuestionLog).where(QuestionLog.question == question)
                          .order_by(QuestionLog.id.desc())).scalars().first()


def main() -> int:
    client = TestClient(app)
    email = f"period{random.randint(10000, 99999)}@example.com"
    r = client.post("/api/auth/dev", json={"email": email, "name": "Period Test"})
    check("dev sign-in", r.status_code == 200, r.text[:200])
    # A new account starts with billing.FREE_QUESTIONS (3 since DIVASTRO-154); this suite
    # asks more than that, so top the test account up.
    from app.db import EntryKind, grant, session as db_session
    with db_session() as db:
        grant(db, r.json()["user"]["id"], 20, EntryKind.admin_adjust, note="test top-up")
        db.commit()
    credits0 = client.get("/api/me").json()["user"]["credits"]

    r = client.post("/api/chart", json={
        "name": "Sanskruti", "date": "1999-08-14", "time": "14:07",
        "place": "Pune, Maharashtra, India", "latitude": 18.5204, "longitude": 73.8567,
        "timezone": "Asia/Kolkata"})
    check("chart cast", r.status_code == 200, r.text[:200])
    sid = r.json()["session_id"]

    print("\n1. /api/ask, provider off")
    r = client.post("/api/ask", json={"session_id": sid, "question": Q, "date": NOW,
                                      "provider": "off"})
    check("HTTP 200", r.status_code == 200, r.text[:300])
    a = r.json()
    check("routed to the period topic", a.get("topic") == "period" and a.get("intent") == "period",
          f"{a.get('topic')}/{a.get('intent')}")
    ans = a.get("answer", "")
    check("mentions 10 and 20 October", "10 Oct 2026" in ans and "20 Oct 2026" in ans, ans[:200])
    check("not the personality reading", "Your core signature" not in ans
          and "personality and character" not in ans)
    check("has the Timing section", "### Timing" in ans)
    check("window facts are in the result for clients",
          (a.get("timing") or {}).get("window", {}).get("period", {}).get("start") == "2026-10-10")
    check("one credit charged", a.get("credits") == credits0 - 1, str(a.get("credits")))

    print("\n2. /api/ask in Hindi, provider off")
    r = client.post("/api/ask", json={"session_id": sid, "question": "kaisa rahega 10 se 20 october",
                                      "date": NOW, "provider": "off", "language": "hi"})
    a = r.json()
    check("Hindi window answer", r.status_code == 200 and a.get("topic") == "period"
          and "10 अक्टूबर 2026" in a.get("answer", "") and "20 अक्टूबर 2026" in a.get("answer", ""),
          a.get("answer", "")[:200])

    print("\n3. A question with no window is unchanged")
    r = client.post("/api/ask", json={"session_id": sid, "question": "Describe my personality",
                                      "date": NOW, "provider": "off"})
    a = r.json()
    check("personality question still gets the personality reading",
          a.get("topic") == "self" and "Your core signature" in a.get("answer", ""),
          a.get("topic"))

    print("\n4. /api/ask/stream logs the polished answer (mocked rewrite)")
    real = llm.stream_polish
    seen_prompts: list[str] = []

    def fake_stream(analysis, language, provider, question, history=None, meta=None):
        seen_prompts.append(llm._build_prompt(analysis, language, question, history))
        for i in range(0, len(POLISHED), 40):
            yield POLISHED[i:i + 40]
        llm._audit_dates(meta, seen_prompts[-1], POLISHED)

    llm.stream_polish = fake_stream
    try:
        before = client.get("/api/me").json()["user"]["credits"]
        r = client.post("/api/ask/stream", json={"session_id": sid, "question": Q, "date": NOW,
                                                 "provider": "anthropic"})
        events = sse(r.text)
        kinds = [e for e, _ in events]
        check("stream: analysis, deltas, done", r.status_code == 200 and kinds[0] == "analysis"
              and "delta" in kinds and kinds[-1] == "done" and "error" not in kinds, str(kinds))
        streamed = "".join(d["text"] for e, d in events if e == "delta")
        check("the rewrite streamed whole", streamed == POLISHED)
        analysis = events[0][1]
        check("the analysis event carries the window answer",
              analysis.get("topic") == "period" and "10 Oct 2026" in analysis.get("answer", ""))
        row = latest_log(Q)
        check("QuestionLog.answer is the polished text", row is not None and row.answer == POLISHED,
              (row.answer[:80] if row else "no row"))
        check("QuestionLog.answer_engine keeps the engine text",
              row is not None and row.answer_engine.startswith("**")
              and "10 Oct 2026" in row.answer_engine)
        after = client.get("/api/me").json()["user"]["credits"]
        check("exactly one credit charged for the streamed question", after == before - 1,
              f"{before} -> {after}")
        check("the prompt the model saw carries the window facts",
              seen_prompts and "Date-window evidence" in seen_prompts[-1])

        print("\n5. A failed rewrite leaves the engine text in the log")
        q2 = "how is october for me"

        def broken(*_a, **_k):
            yield "short"
            raise RuntimeError("boom")

        llm.stream_polish = broken
        r = client.post("/api/ask/stream", json={"session_id": sid, "question": q2, "date": NOW,
                                                 "provider": "anthropic"})
        kinds = [e for e, _ in sse(r.text)]
        check("stream reports the error and still finishes", "error" in kinds and kinds[-1] == "done",
              str(kinds))
        row = latest_log(q2)
        check("log keeps the engine answer", row is not None and row.answer == row.answer_engine
              and "1 Oct 2026" in row.answer)
    finally:
        llm.stream_polish = real

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("period answer end to end: all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
