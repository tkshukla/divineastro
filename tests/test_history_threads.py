"""DIVASTRO-170: My questions as conversations (app/threads.py, GET /api/history and
GET /api/history/thread/<key>).

In process (TestClient, a throwaway SQLite database, the console mail transport, a
FAKE Ollama for the Starter's emailed answers):

  1. Questions on a saved chart are ONE conversation (``c<birth id>``), in the order
     asked; /api/history tags every row with its conversation and item.
  2. A Starter emailed answer joins the same thread: while it is being written it is
     a ``j<job>`` item (pending, with its due time), once written the ``q<row>`` item
     at the time it was ASKED (so before a later instant answer), with
     emailed.status "done"; a failed one says refunded.
  3. Questions on no saved chart: consecutive ones are one conversation, split where
     more than 12 hours apart; marked not available (read-only).
  4. Ownership: another account cannot read the thread (404) and sees nothing in its
     own lists; a birth_id naming another account's chart never shows that chart's
     label; signed out: 401.
  5. Paging: the newest 50, `more`, and `before` for the earlier ones; a saved chart
     with nothing asked is an empty thread.

    ASTRO_SECRET_KEY=ci python -u -m tests.test_history_threads
"""

from __future__ import annotations

import datetime as dt
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

_tmp = tempfile.mkdtemp(prefix="astro_threads_")
os.environ["ASTRO_DATABASE_URL"] = f"sqlite:///{Path(_tmp).as_posix()}/t.db"
os.environ.update({
    "ASTRO_DEV_LOGIN": "1", "ASTRO_COOKIE_SECURE": "0", "ASTRO_GATEWAY": "test",
    "ASTRO_SMTP_HOST": "console", "ASTRO_ADMIN_EMAILS": "owner@example.com",
    "ASTRO_EMAIL_ANSWER_WORKER": "0", "ASTRO_OFFER_ENDS": "2099-01-01T00:00:00+05:30",
    "ASTRO_EMAIL_ANSWER_WRITER": "ollama",
})
for k in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ASTRO_STARTER_ENABLED", "ASTRO_FREE_QUESTIONS"):
    os.environ.pop(k, None)

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import select  # noqa: E402

from tests.fake_ollama import FakeOllama  # noqa: E402

OLLAMA = FakeOllama().start()
os.environ["ASTRO_EMAIL_ANSWER_OLLAMA_URL"] = OLLAMA.url

from app import billing, emailed_answers as ea, mail  # noqa: E402
from app.db import EmailedAnswerJob, QuestionLog, User, grant, session as db_session  # noqa: E402
from app.db import EntryKind  # noqa: E402
from app.main import app  # noqa: E402

failures: list[str] = []
BIRTH = {"name": "Asha", "date": "1990-03-21", "time": "06:15", "place": "Delhi, India",
         "latitude": 28.6519, "longitude": 77.2315, "timezone": "Asia/Kolkata"}
OTHER = {**BIRTH, "name": "Ravi", "date": "1988-11-02", "time": "21:40"}
CHROME = ("Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) "
          "Chrome/126.0 Mobile Safari/537.36")


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def browser(email: str) -> TestClient:
    c = TestClient(app, client=("203.0.113.9", 40000), headers={"User-Agent": CHROME})
    r = c.post("/api/auth/dev", json={"email": email})
    assert r.status_code == 200, r.text
    return c


def uid(c: TestClient) -> int:
    return c.get("/api/me").json()["user"]["id"]


def top_up(c: TestClient, n: int) -> None:
    with db_session() as db:
        grant(db, uid(c), n, EntryKind.admin_adjust, note="test")
        db.commit()


def save(c: TestClient, birth: dict) -> int:
    r = c.post("/api/births", json=birth)
    assert r.status_code == 200, r.text
    return r.json()["birth"]["id"]


def cast(c: TestClient, birth: dict) -> str:
    r = c.post("/api/chart", json=birth)
    assert r.status_code == 200, r.text[:200]
    return r.json()["session_id"]


def ask(c, sid, q, birth_id=None):
    r = c.post("/api/ask/stream", json={"session_id": sid, "question": q, "language": "en",
                                        "provider": "off", "birth_id": birth_id})
    assert r.status_code == 200, r.text[:200]
    return r.text


def thread(c, key, **params):
    return c.get(f"/api/history/thread/{key}", params=params)


def shift(model, row_id: int, hours: float) -> None:
    """Move a row back in time (created_at)."""
    with db_session() as db:
        row = db.get(model, row_id)
        row.created_at = row.created_at - dt.timedelta(hours=hours)
        db.commit()


# ---------------------------------------------------------------- 1 + 2
def part1_saved_chart() -> tuple[TestClient, int]:
    print("\n1-2. One conversation per saved chart, emailed answers in it")
    c = browser("thread-a@example.com")
    top_up(c, 10)
    bid = save(c, BIRTH)
    sid = cast(c, BIRTH)
    for q in ("Will my career grow?", "Is marriage likely soon?"):
        ask(c, sid, q, bid)
    h = c.get("/api/history").json()
    check("/api/history: one conversation for the chart, key c<id>, labelled with the chart",
          len(h["threads"]) == 1 and h["threads"][0]["key"] == f"c{bid}"
          and h["threads"][0]["label"] == "Asha" and h["threads"][0]["available"]
          and h["threads"][0]["count"] == 2, str(h["threads"]))
    check("/api/history: every row names its conversation and item",
          all(q["thread"] == f"c{bid}" and q["item"] == f"q{q['id']}" for q in h["questions"]))
    t = thread(c, f"c{bid}").json()
    check("the thread: both questions with their full answers, oldest first",
          [i["question"] for i in t["items"]] == ["Will my career grow?", "Is marriage likely soon?"]
          and all(len(i["answer"]) > 100 for i in t["items"]) and not t["more"], str(t)[:300])

    # The Starter: buy, spend the instant questions, ask -> queued.
    r = c.post("/api/orders", json={"sku": billing.STARTER_SKU})
    assert r.status_code == 200, r.text
    c.post("/api/orders/confirm", json={"order_id": r.json()["order"]["id"], "payload": {}})
    with db_session() as db:
        u = db.get(User, uid(c))
        from app.db import balance
        left = balance(db, u.id)
        grant(db, u.id, -left, EntryKind.admin_adjust, note="spend")
        db.commit()
    text = ask(c, sid, "What does my chart say about my money this year?", bid)
    job_id = json.loads(text.split("event: queued\ndata: ")[1].split("\n")[0])["job_id"]
    t = thread(c, f"c{bid}").json()
    last = t["items"][-1]
    check("a queued emailed answer is in the same thread, last, as j<job>, pending, with its due time",
          last["key"] == f"j{job_id}" and last["emailed"]["status"] == "pending" and last["emailed"]["due"]
          and last["answer"] == "" and t["pending"] == 1, str(last))
    # An instant answer asked AFTER it (credit back), before the emailed one is written.
    top_up(c, 1)
    ask(c, sid, "And my health?", bid)
    ea.run_next()
    t = thread(c, f"c{bid}").json()
    qs = [i["question"] for i in t["items"]]
    em = next(i for i in t["items"] if i["job_id"] == job_id)
    check("once written: a q<row> item, emailed done, with the answer, in the place it was ASKED",
          qs == ["Will my career grow?", "Is marriage likely soon?",
                 "What does my chart say about my money this year?", "And my health?"]
          and em["key"].startswith("q") and em["emailed"]["status"] == "done"
          and "steady rise through effort" in em["answer"] and t["pending"] == 0, str(qs))
    # A failed one: refunded, no answer (the instant balance is 0 again).
    text = ask(c, sid, "Will I travel?", bid)
    fail_id = json.loads(text.split("event: queued\ndata: ")[1].split("\n")[0])["job_id"]
    with db_session() as db:
        ea._fail(db, db.get(EmailedAnswerJob, fail_id), "test: cannot", notify=False)
        db.commit()
    t = thread(c, f"c{bid}").json()
    f = next(i for i in t["items"] if i["job_id"] == fail_id)
    check("a failed emailed answer: in the thread, failed and refunded, no answer",
          f["emailed"]["status"] == "failed" and f["emailed"]["refunded"] and f["answer"] == "", str(f))
    return c, bid


# ---------------------------------------------------------------- 3
def part3_unsaved(c: TestClient) -> None:
    print("\n3. Questions on no saved chart: split at 12 hours, read-only")
    top_up(c, 3)
    sid = cast(c, OTHER)
    for q in ("Unsaved one", "Unsaved two", "Unsaved three"):
        ask(c, sid, q)
    with db_session() as db:
        rows = db.execute(select(QuestionLog).where(
            QuestionLog.question.like("Unsaved %")).order_by(QuestionLog.id)).scalars().all()
        ids = [r.id for r in rows]
    shift(QuestionLog, ids[0], 30)
    shift(QuestionLog, ids[1], 29)        # 1 h after the first, 29 h before the third
    h = c.get("/api/history").json()
    unsaved = [t for t in h["threads"] if t["key"].startswith("u")]
    check("two unsaved conversations (the 29-hour gap splits them), not available",
          len(unsaved) == 2 and sorted(t["count"] for t in unsaved) == [1, 2]
          and not any(t["available"] for t in unsaved), str(unsaved))
    old = next(t for t in unsaved if t["count"] == 2)
    t = thread(c, old["key"]).json()
    check("the older one reads back both questions in order, birth_id None",
          [i["question"] for i in t["items"]] == ["Unsaved one", "Unsaved two"] and t["birth_id"] is None)
    check("newest conversation first in the list", h["threads"][0]["key"] == next(
        x for x in unsaved if x["count"] == 1)["key"], str([x["key"] for x in h["threads"]]))


# ---------------------------------------------------------------- 4
def part4_ownership(a: TestClient, bid: int) -> None:
    print("\n4. Ownership")
    b = browser("thread-b@example.com")
    h = b.get("/api/history").json()
    check("another account: no questions, no conversations", h["questions"] == [] and h["threads"] == [])
    check("another account: A's chart thread is 404", thread(b, f"c{bid}").status_code == 404)
    a_unsaved = [t["key"] for t in a.get("/api/history").json()["threads"] if t["key"].startswith("u")]
    check("another account: A's unsaved thread key is 404 too",
          all(thread(b, k).status_code == 404 for k in a_unsaved) and a_unsaved)
    # B asks with A's birth_id (the server does not validate it): it must not show A's chart.
    top_up(b, 2)
    sid = cast(b, BIRTH)
    ask(b, sid, "B's question", bid)
    hb = b.get("/api/history").json()
    check("B's question naming A's chart id: B's own unsaved conversation, without A's label",
          len(hb["threads"]) == 1 and hb["threads"][0]["key"].startswith("u")
          and hb["threads"][0]["label"] == "" and not hb["threads"][0]["available"], str(hb["threads"]))
    ta = thread(a, f"c{bid}").json()
    check("...and A's thread does not contain it",
          "B's question" not in [i["question"] for i in ta["items"]])
    anon = TestClient(app, client=("203.0.113.9", 40000), headers={"User-Agent": CHROME})
    check("signed out: /api/history/thread is 401", thread(anon, f"c{bid}").status_code == 401)
    check("signed out: /api/history is 401", anon.get("/api/history").status_code == 401)


# ---------------------------------------------------------------- 5
def part5_paging() -> None:
    print("\n5. Paging; an empty chart")
    c = browser("thread-pages@example.com")
    bid = save(c, BIRTH)
    e = thread(c, f"c{bid}")
    check("a saved chart with nothing asked: an empty thread (200), not 404",
          e.status_code == 200 and e.json()["items"] == [] and e.json()["available"], e.text[:200])
    with db_session() as db:
        base = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=3)
        for n in range(60):
            db.add(QuestionLog(user_id=uid(c), birth_id=bid, question=f"Q{n:02d}", answer=f"A{n:02d}",
                               created_at=base + dt.timedelta(minutes=n)))
        db.commit()
    t = thread(c, f"c{bid}").json()
    check("the newest 50, oldest first, and `more`",
          len(t["items"]) == 50 and t["items"][0]["question"] == "Q10" and t["items"][-1]["question"] == "Q59"
          and t["more"] and t["count"] == 60, f"{len(t['items'])} {t['items'][0]['question']}")
    t2 = thread(c, f"c{bid}", before=t["items"][0]["at"]).json()
    check("`before` the first: the 10 earlier ones, no more",
          [i["question"] for i in t2["items"]] == [f"Q{n:02d}" for n in range(10)] and not t2["more"])


def main() -> int:
    try:
        a, bid = part1_saved_chart()
        part3_unsaved(a)
        part4_ownership(a, bid)
        part5_paging()
    finally:
        OLLAMA.stop()
    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILED:")
        for f in failures:
            print("  -", f)
        return 1
    print("ALL PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
