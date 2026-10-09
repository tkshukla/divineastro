"""DIVASTRO-154: 3 free questions for new accounts, and one answer without signing in.

In process (TestClient, a throwaway SQLite database, no LLM), so it needs no server:

  1. The sign-up grant is billing.FREE_QUESTIONS, 3 by default, ASTRO_FREE_QUESTIONS
     overrides it, and an account that already holds credits keeps every one of them.
  2. A signed-out visitor with a chart gets exactly one real answer (200, the same
     engine path, nothing charged, no credit_entries / question_log row), then 401.
     Clearing the cookie on the same IP + browser is still 401; another visitor gets
     their own one; bots and cloud addresses get none; DNT/GPC still gets one but only
     time + hash are kept; the per-address ceiling and the global hourly/daily caps
     hold; a failed analysis gives the allowance back; someone else's chart is a 404
     that spends nothing.
  3. What is stored: no IP anywhere, the 400-day purge, the admin list, the migration
     up and down.
  4. After the guest signs up: the chart is theirs, 3 credits, asking charges 1.

    ASTRO_SECRET_KEY=ci python -u -m tests.test_guest_answer
"""

from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

_tmp = tempfile.mkdtemp(prefix="astro_guest_")
os.environ["ASTRO_DATABASE_URL"] = f"sqlite:///{Path(_tmp).as_posix()}/t.db"
os.environ["ASTRO_DEV_LOGIN"] = "1"
os.environ["ASTRO_COOKIE_SECURE"] = "0"
os.environ["ASTRO_GATEWAY"] = "test"
os.environ.pop("ASTRO_FREE_QUESTIONS", None)     # the default is what is under test
os.environ.pop("ASTRO_GUEST_ANSWER", None)
os.environ.pop("ANTHROPIC_API_KEY", None)        # never a real model

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import func, inspect, select  # noqa: E402

from app import analytics, billing, guest  # noqa: E402
from app import main as main_mod  # noqa: E402
from app.db import (CreditEntry, EntryKind, GuestAnswer, QuestionLog, UnregQuestion,  # noqa: E402
                    User, balance, engine, grant, session as db_session, utcnow)
from app.main import app  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
failures: list[str] = []

CHROME = ("Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) "
          "Chrome/126.0 Mobile Safari/537.36")
IP = "203.0.113.7"                 # documentation range: not a cloud network
BIRTH = {"name": "Guest", "date": "1990-03-21", "time": "06:15", "place": "Delhi, India",
         "latitude": 28.6519, "longitude": 77.2315, "timezone": "Asia/Kolkata"}


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def browser(ua: str = CHROME, ip: str = IP, **headers) -> TestClient:
    return TestClient(app, client=(ip, 40000), headers={"User-Agent": ua, **headers})


def events(text: str) -> list[tuple[str, dict]]:
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


def cast(c: TestClient) -> str:
    r = c.post("/api/chart", json=BIRTH)
    assert r.status_code == 200, r.text[:200]
    return r.json()["session_id"]


def ask(c: TestClient, sid: str, q: str = "Will I get a new job this year?", lang: str = "en"):
    return c.post("/api/ask/stream", json={"session_id": sid, "question": q,
                                           "language": lang, "provider": "off"})


def count(model, *where) -> int:
    with db_session() as db:
        return db.execute(select(func.count(model.id)).where(*where)).scalar_one()


def reset_guests() -> None:
    with db_session() as db:
        db.query(GuestAnswer).delete()
        db.commit()
    guest._per_address.clear()


def part1_signup_grant() -> None:
    print("\n1. The sign-up grant")
    check("billing.FREE_QUESTIONS defaults to 3", billing.FREE_QUESTIONS == 3, str(billing.FREE_QUESTIONS))
    out = subprocess.run(
        [sys.executable, "-c", "from app import billing; print(billing.FREE_QUESTIONS)"],
        cwd=ROOT, capture_output=True, text=True,
        env={**os.environ, "ASTRO_FREE_QUESTIONS": "7"})
    check("ASTRO_FREE_QUESTIONS overrides it", out.stdout.strip().endswith("7"), out.stdout[-80:] + out.stderr[-200:])

    c = browser()
    r = c.post("/api/auth/dev", json={"email": "new154@example.com", "name": "New"})
    check("a new account starts with 3 free questions",
          r.status_code == 200 and r.json()["user"]["credits"] == 3, r.text[:160])
    me = c.get("/api/me").json()
    check("/api/me reports free_questions 3", me.get("free_questions") == 3, str(me.get("free_questions")))
    check("/api/products reports free_questions 3",
          c.get("/api/products").json().get("free_questions") == 3)

    # Every grant reads the value at the moment of sign-up (not at import).
    saved = billing.FREE_QUESTIONS
    billing.FREE_QUESTIONS = 5
    try:
        r = browser().post("/api/auth/dev", json={"email": "five154@example.com"})
        check("a changed setting is what the next sign-up gets", r.json()["user"]["credits"] == 5,
              str(r.json()["user"]["credits"]))
    finally:
        billing.FREE_QUESTIONS = saved

    # An account made under the old rule (10 free) keeps every credit it holds.
    with db_session() as db:
        old = User(email="old154@example.com", name="Old", provider="dev", provider_sub="dev:old154@example.com")
        db.add(old)
        db.flush()
        grant(db, old.id, 10, EntryKind.signup_bonus, note="Welcome — free questions")
        grant(db, old.id, -2, EntryKind.question, note="asked")
        db.commit()
        old_id = old.id
        rows_before = db.execute(select(func.count(CreditEntry.id)).where(
            CreditEntry.user_id == old_id)).scalar_one()
    c = browser()
    r = c.post("/api/auth/dev", json={"email": "old154@example.com"})
    check("an existing account signing in again is not re-granted or clawed back",
          r.status_code == 200 and r.json()["created"] is False and r.json()["user"]["credits"] == 8,
          r.text[:160])
    with db_session() as db:
        check("its balance is still 8 (10 granted, 2 used)", balance(db, old_id) == 8)
        check("and no credit_entries row was added or changed",
              db.execute(select(func.count(CreditEntry.id)).where(
                  CreditEntry.user_id == old_id)).scalar_one() == rows_before)


def part2_guest() -> None:
    print("\n2. One answer without signing in")
    reset_guests()
    c = browser()
    me = c.get("/api/me").json()
    check("/api/me offers a signed-out browser one guest answer",
          me.get("user") is None and me.get("guest_answers") == 1, str(me))
    sid = cast(c)
    credits_before, logs_before = count(CreditEntry), count(QuestionLog)
    r = ask(c, sid)
    ev = events(r.text)
    first = ev[0][1] if ev else {}
    check("the first signed-out question is answered (200)", r.status_code == 200, str(r.status_code))
    check("with a real reading from the engine",
          ev and ev[0][0] == "analysis" and len(first.get("answer", "")) > 80
          and first.get("answer") == first.get("answer_engine") and first.get("verdict"), str(first)[:200])
    check("marked as a guest answer, with the sign-up allowance for the app's line",
          first.get("guest") is True and first.get("free_questions") == 3 and "credits" not in first)
    check("the stream finishes", ev and ev[-1][0] == "done")
    check("nothing was charged: no credit_entries row", count(CreditEntry) == credits_before)
    check("no question_log row (there is no account)", count(QuestionLog) == logs_before)
    ck = r.headers.get("set-cookie", "")
    check("a guest cookie is set: HttpOnly, SameSite=Lax, signed",
          ck.startswith(f"{guest.COOKIE}=") and "httponly" in ck.lower() and "samesite=lax" in ck.lower()
          and "." in ck.split(";")[0], ck[:160])
    with db_session() as db:
        row = db.execute(select(GuestAnswer)).scalars().one()
    check("the guest row keeps the question, the answer shown and the language",
          row.question == "Will I get a new job this year?" and len(row.answer) > 80 and row.language == "en")
    check("the guest row has no IP (only the day-scoped hash)",
          IP not in json.dumps([row.visitor, row.question, row.answer, row.language])
          and row.visitor == analytics.visitor_hash(IP, CHROME))
    cols = {col["name"] for col in inspect(engine).get_columns("guest_answers")}
    check("guest_answers has no ip / user / birth column",
          cols == {"id", "ts", "visitor", "question", "answer", "language"}, str(cols))
    check("/api/me now offers no guest answer", c.get("/api/me").json().get("guest_answers") == 0)

    unreg_before = count(UnregQuestion)
    r = ask(c, sid, "And my marriage?")
    check("the second question is 401 (the sign-in sheet)", r.status_code == 401, str(r.status_code))
    check("and is kept in unreg_questions as before (DIVASTRO-131)", count(UnregQuestion) == unreg_before + 1)

    c.cookies.clear()
    r = ask(c, sid, "Third try without the cookie")
    check("clearing the cookie on the same IP + browser is still 401", r.status_code == 401, str(r.status_code))
    check("still exactly one guest answer stored", count(GuestAnswer) == 1)

    forged = browser(ua=CHROME.replace("126.0", "97.0"))
    forged.cookies.set(guest.COOKIE, "eyJuIjoxfQ.forged.signature")
    check("a forged cookie is ignored, not trusted (that visitor is still offered theirs)",
          forged.get("/api/me").json().get("guest_answers") == 1)

    c2 = browser(ua=CHROME.replace("126.0", "125.0"))
    r = ask(c2, cast(c2), "Is this a good year for money?")
    check("a different visitor gets their own one answer", r.status_code == 200
          and events(r.text)[0][1].get("guest") is True, str(r.status_code))
    r = ask(c2, cast(c2), "And health?")
    check("...and only one", r.status_code == 401)

    print("\n   bots, cloud addresses, DNT")
    for label, cl in (("a bot user-agent", browser(ua="Mozilla/5.0 (compatible; Googlebot/2.1)")),
                      ("a headless browser", browser(ua=CHROME.replace("Chrome", "HeadlessChrome"))),
                      ("a cloud address (Tencent)", browser(ip="43.130.10.10")),
                      ("a prefetch", browser(**{"Sec-Purpose": "prefetch"}))):
        n = count(GuestAnswer)
        sid_b = cast(cl)
        r = ask(cl, sid_b, "Bot question")
        check(f"{label}: 401 and no answer", r.status_code == 401 and "analysis" not in r.text
              and count(GuestAnswer) == n, str(r.status_code))
    check("/api/me offers a bot nothing", browser(ua="curl/8.0").get("/api/me").json().get("guest_answers") == 0)

    dnt = browser(ua=CHROME.replace("126.0", "124.0"), DNT="1")
    unreg_before = count(UnregQuestion)
    r = ask(dnt, cast(dnt), "Private question about my career")
    check("a Do-Not-Track visitor still gets their one answer", r.status_code == 200
          and events(r.text)[0][1].get("guest") is True, str(r.status_code))
    with db_session() as db:
        row = db.execute(select(GuestAnswer).order_by(GuestAnswer.id.desc())).scalars().first()
    check("...but only the time and the hash are kept (no question, answer, language)",
          row.question == "" and row.answer == "" and row.language == "" and row.visitor)
    r = ask(dnt, cast(dnt), "Second private question")
    check("...and the DNT visitor's second question is 401 and not stored anywhere",
          r.status_code == 401 and count(UnregQuestion) == unreg_before)
    gpc = browser(ua=CHROME.replace("126.0", "123.0"), **{"Sec-GPC": "1"})
    r = ask(gpc, cast(gpc), "GPC question")
    check("a Global-Privacy-Control visitor gets one answer too", r.status_code == 200)

    print("\n   ownership and failures")
    owner = browser(ua=CHROME.replace("126.0", "122.0"))
    owner.post("/api/auth/dev", json={"email": "owner154@example.com"})
    theirs = cast(owner)
    stranger = browser(ua=CHROME.replace("126.0", "121.0"))
    n = count(GuestAnswer)
    r = ask(stranger, theirs, "Whose chart is this?")
    check("a guest asking about someone else's chart gets 401 as before and spends nothing",
          r.status_code == 401 and count(GuestAnswer) == n and stranger.get("/api/me").json()["guest_answers"] == 1)
    r = ask(stranger, "no-such-session", "Expired chart?")
    check("...as does a chart session that does not exist (expired, or never cast)",
          r.status_code == 401 and count(GuestAnswer) == n)

    real = main_mod.analyse
    main_mod.analyse = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("engine down"))
    try:
        failing = TestClient(app, client=(IP, 40000), raise_server_exceptions=False,
                             headers={"User-Agent": CHROME.replace("126.0", "120.0")})
        sid_f = cast(failing)
        r = ask(failing, sid_f, "Will this fail?")
        check("a failed analysis is an error, not an answer", r.status_code == 500, str(r.status_code))
    finally:
        main_mod.analyse = real
    check("...and gives the allowance back", count(GuestAnswer) == n
          and failing.get("/api/me").json()["guest_answers"] == 1)
    r = ask(failing, sid_f, "Now it works")
    check("...so the same visitor's retry is answered", r.status_code == 200)

    print("\n   caps")
    reset_guests()
    saved = (guest.PER_HOUR, guest.PER_DAY, guest.PER_ADDRESS_DAY)
    try:
        guest.PER_HOUR = 2
        for i in range(2):
            v = browser(ua=CHROME.replace("126.0", f"11{i}.0"))
            check(f"hour cap 2: guest {i + 1} answered", ask(v, cast(v)).status_code == 200)
        v = browser(ua=CHROME.replace("126.0", "112.0"))
        sid_v = cast(v)
        check("hour cap 2: the third guest that hour gets the sign-in sheet (401)",
              ask(v, sid_v).status_code == 401)
        check("/api/me says no guest answer while the cap is reached", v.get("/api/me").json()["guest_answers"] == 0)
        with db_session() as db:                     # move those two answers 2 hours back
            for row in db.execute(select(GuestAnswer)).scalars():
                row.ts = utcnow() - dt.timedelta(hours=2)
            db.commit()
        guest.PER_DAY = 2
        check("day cap 2: still 401 an hour later (2 in the last 24 hours)", ask(v, sid_v).status_code == 401)
        guest.PER_DAY = 400
        check("under both caps again: answered", ask(v, sid_v).status_code == 200)

        reset_guests()
        guest.PER_HOUR, guest.PER_ADDRESS_DAY = 60, 2
        for i in range(2):
            v = browser(ua=CHROME.replace("126.0", f"10{i}.0"), ip="198.51.100.9")
            ask(v, cast(v))
        v = browser(ua=CHROME.replace("126.0", "109.0"), ip="198.51.100.9")
        check("per-address ceiling: a third browser string from one address gets 401",
              ask(v, cast(v)).status_code == 401)
        v = browser(ua=CHROME.replace("126.0", "109.0"), ip="198.51.100.10")
        check("...while another address is unaffected", ask(v, cast(v)).status_code == 200)
    finally:
        guest.PER_HOUR, guest.PER_DAY, guest.PER_ADDRESS_DAY = saved

    saved_on = guest.ENABLED, guest.GUEST_ANSWERS
    guest.ENABLED, guest.GUEST_ANSWERS = False, 0
    try:
        v = browser(ua=CHROME.replace("126.0", "99.0"))
        check("ASTRO_GUEST_ANSWER=0: every signed-out question is 401 as before",
              ask(v, cast(v)).status_code == 401 and v.get("/api/me").json()["guest_answers"] == 0)
    finally:
        guest.ENABLED, guest.GUEST_ANSWERS = saved_on


def part3_storage() -> None:
    print("\n3. Storage, purge, admin list, migration")
    with db_session() as db:
        db.add(GuestAnswer(visitor="oldvisitor000000", question="old", answer="old answer",
                           ts=utcnow() - dt.timedelta(days=analytics.RETENTION_DAYS + 1)))
        db.add(GuestAnswer(visitor="newvisitor000000", question="Recent guest question", answer="a"))
        db.commit()
        analytics.purge_old(db)
        left = [r.visitor for r in db.execute(select(GuestAnswer)).scalars()]
        check("purge_old deletes guest rows past the 400-day window", "oldvisitor000000" not in left)
        check("...and keeps recent ones", "newvisitor000000" in left)
        listed = analytics.unregistered_questions(db, utcnow() - dt.timedelta(days=1))
        hit = [q for q in listed if q["question"] == "Recent guest question"]
        check("the admin's signed-out questions list shows guest questions, marked answered",
              hit and hit[0]["answered"] is True)
        check("...and never a DNT guest's empty row", all(q["question"] for q in listed))

    from alembic import command
    from alembic.config import Config
    url = f"sqlite:///{Path(_tmp).as_posix()}/mig.db"
    cfg = Config(str(ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(ROOT / "migrations"))
    cfg.set_main_option("sqlalchemy.url", url)
    from sqlalchemy import create_engine
    # migrations/env.py takes the URL from ASTRO_DATABASE_URL: point it at the scratch file.
    app_url = os.environ["ASTRO_DATABASE_URL"]
    os.environ["ASTRO_DATABASE_URL"] = url
    try:
        _migrate(cfg, url, create_engine)
    finally:
        os.environ["ASTRO_DATABASE_URL"] = app_url


def _migrate(cfg, url, create_engine) -> None:
    from alembic import command
    command.upgrade(cfg, "head")
    eng = create_engine(url)
    check("migration up: guest_answers exists", "guest_answers" in inspect(eng).get_table_names())
    command.downgrade(cfg, "c9e3a5b7d1f2")
    eng.dispose()
    eng = create_engine(url)
    tables = inspect(eng).get_table_names()
    check("migration down: guest_answers is gone, unreg_questions stays",
          "guest_answers" not in tables and "unreg_questions" in tables)
    command.upgrade(cfg, "head")
    eng.dispose()
    eng = create_engine(url)
    check("and up again", "guest_answers" in inspect(eng).get_table_names())
    eng.dispose()


def part4_after_signup() -> None:
    print("\n4. The guest signs up")
    reset_guests()
    c = browser(ua=CHROME.replace("126.0", "98.0"))
    sid = cast(c)
    r = ask(c, sid, "Guest question before signing up")
    check("guest answer first", r.status_code == 200)
    check("then 401", ask(c, sid, "Parked question").status_code == 401)
    r = c.post("/api/auth/dev", json={"email": "guest-then-user@example.com"})
    check("signing up gives the new account 3 free questions",
          r.json()["created"] is True and r.json()["user"]["credits"] == 3, r.text[:160])
    r = ask(c, sid, "Parked question")
    ev = events(r.text)
    check("the parked question is answered on the same chart (now theirs)", r.status_code == 200
          and ev[0][1].get("credits") == 2 and not ev[0][1].get("guest"), str(ev[:1])[:200])
    with db_session() as db:
        uid = db.execute(select(User.id).where(User.email == "guest-then-user@example.com")).scalar_one()
        kinds = [k for (k,) in db.execute(select(CreditEntry.kind).where(CreditEntry.user_id == uid))]
    check("their ledger is the welcome grant and one question, nothing for the guest answer",
          sorted(k.value for k in kinds) == sorted([EntryKind.signup_bonus.value, EntryKind.question.value]),
          str(kinds))


def main() -> int:
    part1_signup_grant()
    part2_guest()
    part3_storage()
    part4_after_signup()
    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("guest answer + free allowance: all green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
