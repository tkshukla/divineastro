"""DIVASTRO-157: the Rs 21 Starter offered right under a free answer, matched to its topic.

In process (TestClient, a throwaway SQLite database, no LLM), so it needs no server:

  1. billing.starter_topic: the engine's topic -> the offer line's topic (marriage,
     career, money, health, timing, general); a muhurat question is "timing".
  2. The answer API (/api/ask/stream and /api/ask) returns offer_topic for real
     questions routed by the engine.
  3. Eligibility (result.starter_inline): every answer from a new account's free
     allowance carries it; not once a pack is bought, after an admin top-up, after the
     Starter is bought or while a claim for it is pending, for an account with no email
     (phone), or with the Starter switched off. The guest answer carries it while the
     Starter is on sale.
  4. Analytics: starter_inline_shown / starter_inline_click are accepted, labelled per
     topic and in the in-app funnel; starter_click "inline" is labelled.
  5. i18n: acct.starterInline_<topic> in all 13 languages, with {price}, translated.

    ASTRO_SECRET_KEY=ci python -u -m tests.test_starter_inline
"""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

_tmp = tempfile.mkdtemp(prefix="astro_starter_inline_")
os.environ["ASTRO_DATABASE_URL"] = f"sqlite:///{Path(_tmp).as_posix()}/t.db"
os.environ["ASTRO_DEV_LOGIN"] = "1"
os.environ["ASTRO_COOKIE_SECURE"] = "0"
os.environ["ASTRO_GATEWAY"] = "test"
os.environ.pop("ASTRO_FREE_QUESTIONS", None)
os.environ.pop("ASTRO_GUEST_ANSWER", None)
os.environ.pop("ASTRO_STARTER_ENABLED", None)
os.environ.pop("ANTHROPIC_API_KEY", None)        # never a real model

from fastapi.testclient import TestClient  # noqa: E402

from app import analytics, billing, guest  # noqa: E402
from app.db import (EntryKind, GuestAnswer, Order, OrderStatus, User, grant,  # noqa: E402
                    session as db_session)
from app.main import app  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
failures: list[str] = []

CHROME = ("Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) "
          "Chrome/126.0 Mobile Safari/537.36")
BIRTH = {"name": "Inline", "date": "1990-03-21", "time": "06:15", "place": "Delhi, India",
         "latitude": 28.6519, "longitude": 77.2315, "timezone": "Asia/Kolkata"}
TOPICS = ("marriage", "career", "money", "health", "timing", "general")
LANGS = ("en", "hi", "as", "bn", "gu", "kn", "ml", "mr", "ne", "or", "pa", "ta", "te")
_ip = [10]


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def browser() -> TestClient:
    _ip[0] += 1                                       # a new visitor each time
    return TestClient(app, client=(f"203.0.113.{_ip[0]}", 40000), headers={"User-Agent": CHROME})


def analysis(text: str) -> dict:
    for block in text.strip().split("\n\n"):
        if "event: analysis" in block:
            return json.loads(block.split("data: ", 1)[1])
    return {}


def cast(c: TestClient) -> str:
    r = c.post("/api/chart", json=BIRTH)
    assert r.status_code == 200, r.text[:200]
    return r.json()["session_id"]


def ask(c: TestClient, sid: str, q: str) -> dict:
    r = c.post("/api/ask/stream", json={"session_id": sid, "question": q, "language": "en",
                                        "provider": "off"})
    assert r.status_code == 200, (r.status_code, r.text[:200])
    return analysis(r.text)


def signed_in(email: str) -> tuple[TestClient, str, int]:
    c = browser()
    r = c.post("/api/auth/dev", json={"email": email, "name": "Inline"})
    assert r.status_code == 200, r.text[:200]
    return c, cast(c), r.json()["user"]["id"]


def part1_mapping() -> None:
    print("\n1. The engine's topic -> the offer line's topic")
    cases = {"love": "marriage", "career": "career", "money": "money", "health": "health",
             "timing": "timing", "period": "timing", "self": "general", "family": "general",
             "travel": "general", "": "general", None: "general"}
    bad = {k: billing.starter_topic(k) for k, v in cases.items() if billing.starter_topic(k) != v}
    check("love->marriage, career, money, health, timing/period->timing, everything else general",
          not bad, str(bad))
    check("every result is one of STARTER_INLINE_TOPICS",
          all(billing.starter_topic(k) in billing.STARTER_INLINE_TOPICS for k in cases)
          and billing.STARTER_INLINE_TOPICS == TOPICS)
    check("a muhurat question is timing, whatever it was routed to",
          billing.starter_topic("family", "Best muhurat for griha pravesh?") == "timing"
          and billing.starter_topic("love", "विवाह का शुभ मुहूर्त कब है?") == "timing")


def part2_api_topic() -> None:
    print("\n2. The answer API returns offer_topic")
    c, sid, _uid = signed_in("topics157@example.com")
    with db_session() as db:                       # enough questions for every case
        grant(db, _uid, 10, EntryKind.admin_adjust, note="test")
        db.commit()
    qs = {"When will I get married?": "marriage",
          "Will I get a promotion in my career this year?": "career",
          "Will my finances and wealth improve?": "money",
          "How will my health be?": "health",
          "Is this a good time for me right now?": "timing",
          "What am I like as a person?": "general"}
    got = {}
    for q, want in qs.items():
        a = ask(c, sid, q)
        got[q] = (a.get("topic"), a.get("offer_topic"))
        check(f"'{q}' -> {want}", a.get("offer_topic") == want, str(got[q]))
    r = c.post("/api/ask", json={"session_id": sid, "question": "When will I get married?",
                                 "language": "en", "provider": "off"})
    check("/api/ask carries offer_topic and starter_inline too",
          r.status_code == 200 and r.json().get("offer_topic") == "marriage"
          and "starter_inline" in r.json(), r.text[:120])


def part3_eligibility() -> None:
    print("\n3. Who gets the line")
    c, sid, uid = signed_in("free157@example.com")
    flags = [ask(c, sid, q).get("starter_inline") for q in
             ("Will my career grow?", "When will I marry?", "How is my health?")]
    check("a new account: all 3 free answers carry it (the last one too)", flags == [True] * 3, str(flags))

    c, sid, uid = signed_in("topup157@example.com")
    with db_session() as db:
        grant(db, uid, 5, EntryKind.admin_adjust, note="goodwill")
        db.commit()
    check("credits added by an admin: not a free answer", ask(c, sid, "My career?").get("starter_inline") is False)

    c, sid, uid = signed_in("pack157@example.com")
    with db_session() as db:
        grant(db, uid, 10, EntryKind.purchase, note="q10")
        db.commit()
    check("a bought question pack: no line", ask(c, sid, "My career?").get("starter_inline") is False)

    c, sid, uid = signed_in("bought157@example.com")
    with db_session() as db:
        db.add(Order(user_id=uid, sku=billing.STARTER_SKU, title="Starter", amount_paise=2100,
                     credits=3, status=OrderStatus.paid, provider="test"))
        db.commit()
    a = ask(c, sid, "My career?")
    check("Starter already bought: no line (offer_topic is still there)",
          a.get("starter_inline") is False and a.get("offer_topic") == "career", str(a.get("starter_inline")))

    c, sid, uid = signed_in("pending157@example.com")
    with db_session() as db:
        db.add(Order(user_id=uid, sku=billing.STARTER_SKU, title="Starter", amount_paise=2100,
                     credits=3, status=OrderStatus.awaiting_verification, provider="upi_manual"))
        db.commit()
    check("a Starter UPI claim pending: no line", ask(c, sid, "My career?").get("starter_inline") is False)

    c, sid, uid = signed_in("failed157@example.com")
    with db_session() as db:
        db.add(Order(user_id=uid, sku=billing.STARTER_SKU, title="Starter", amount_paise=2100,
                     credits=3, status=OrderStatus.failed, provider="test"))
        db.commit()
    check("a failed Starter order does not block it", ask(c, sid, "My career?").get("starter_inline") is True)

    with db_session() as db:
        ph = User(email="", name="Phone", provider="phone", provider_sub="phone:+919800000157", phone="+919800000157")
        db.add(ph)
        db.flush()
        grant(db, ph.id, 3, EntryKind.signup_bonus, note="Welcome")
        db.commit()
        check("a phone account (no email to send to): no line", billing.starter_inline(db, ph) is False)
        check("...though its answers are from the free allowance", billing.on_free_allowance(db, ph) is True)

    c, sid, uid = signed_in("off157@example.com")
    os.environ["ASTRO_STARTER_ENABLED"] = "0"
    try:
        check("Starter switched off: no line", ask(c, sid, "My career?").get("starter_inline") is False)
        with db_session() as db:
            db.query(GuestAnswer).delete()
            db.commit()
        guest._per_address.clear()
        g = browser()
        check("...and none under the guest answer either",
              ask(g, cast(g), "When will I marry?").get("starter_inline") is False)
    finally:
        os.environ.pop("ASTRO_STARTER_ENABLED", None)

    with db_session() as db:
        db.query(GuestAnswer).delete()
        db.commit()
    guest._per_address.clear()
    g = browser()
    a = ask(g, cast(g), "When will I get married?")
    check("the guest answer carries the line, with its topic",
          a.get("guest") is True and a.get("starter_inline") is True and a.get("offer_topic") == "marriage",
          str({k: a.get(k) for k in ("guest", "starter_inline", "offer_topic")}))


def part4_analytics() -> None:
    print("\n4. Analytics")
    for name in ("starter_inline_shown", "starter_inline_click"):
        check(f"'{name}' is accepted with the topic as detail",
              all(analytics.parse_event({"name": name, "detail": t}) == (name, t) for t in TOPICS))
        check(f"'{name}' has a plain-words label, overall and per topic",
              all((name, t) in analytics.EVENT_LABELS for t in ("",) + TOPICS))
    check("starter_click 'inline' is labelled", ("starter_click", "inline") in analytics.EVENT_LABELS)
    funnel = [n for _l, n, _d in analytics.APP_FUNNEL]
    check("both are steps of the in-app funnel, between asking and the store",
          funnel.index("ask_sent") < funnel.index("starter_inline_shown") < funnel.index("starter_inline_click")
          < funnel.index("store_open"), str(funnel))
    js = (ROOT / "app" / "static" / "account.js").read_text(encoding="utf-8")
    check("account.js reports both through daTrack",
          'daTrack?.("starter_inline_shown"' in js and 'daTrack?.("starter_inline_click"' in js)
    check("...and opens the same store entry point as the other Starter offers",
          'openStore(false, STARTER_SKU, "inline")' in js)


def part5_i18n() -> None:
    print("\n5. The line in all 13 languages")
    files = {c: json.loads((ROOT / "app" / "static" / "i18n" / f"{c}.json").read_text(encoding="utf-8"))
             for c in LANGS}
    en = files["en"]
    check("English: the marriage line is the agreed sentence",
          en.get("acct.starterInline_marriage")
          == "Want the full picture on your marriage timing? Get 3 detailed answers by email for {price}.")
    for code, d in files.items():
        vals = [d.get(f"acct.starterInline_{t}", "") for t in TOPICS]
        check(f"{code}: one line per topic, each with {{price}} and no other placeholder",
              all(v and re.findall(r"\{\w+\}", v) == ["{price}"] for v in vals), str(vals)[:120])
        check(f"{code}: six different lines", len(set(vals)) == 6)
        if code != "en":
            check(f"{code}: translated (no English copy, not Latin script)",
                  all(v != en[f"acct.starterInline_{t}"] and not re.search(r"[A-Za-z]{3,}", v.replace("{price}", ""))
                      for t, v in zip(TOPICS, vals)), str(vals)[:120])


def main() -> int:
    part1_mapping()
    part2_api_topic()
    part3_eligibility()
    part4_analytics()
    part5_i18n()
    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("starter inline (DIVASTRO-157): all green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
