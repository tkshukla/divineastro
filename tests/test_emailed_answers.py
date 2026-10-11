"""DIVASTRO-155: the Rs 21 Starter, 3 detailed answers by email.

In process (TestClient, a throwaway SQLite database, the console mail transport),
with a FAKE Ollama (tests/fake_ollama.py, a real HTTP server on localhost) and a
FAKE `anthropic` module, so nothing leaves the machine:

  1. The product: Rs 21 = list = offer (the Diwali offer engine ignores it), sold once
     per account (second order 409), no coupon, off with ASTRO_STARTER_ENABLED=0,
     refused to an account with no email; JSON-LD at 21 with no priceValidUntil.
  2. Separate balances: buying it adds 3 emailed answers and no instant question;
     an instant answer spends only the instant balance.
  3. Enqueue: with 0 instant questions an ask debits one emailed answer and returns
     at once (SSE "queued" / 202), nothing analysed in the request.
  4. The worker: Ollama writes English (en: no translation call; hi: Claude Haiku
     translates); Ollama down -> Claude; projected late -> Claude; Ollama error ->
     Claude; Claude failing too -> the engine's reading with a note. Every path
     emails the answer and saves it to My questions; model_used is recorded.
  5. Failures refund the credit (chart cannot be rebuilt; email cannot be sent);
     a restart puts an interrupted job back in the queue; late delivery alerts;
     alerts are rate-limited to one email an hour.
  6. The admin Traffic tile; the analytics events; the migration up and down.

    ASTRO_SECRET_KEY=ci python -u -m tests.test_emailed_answers
"""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import sys
import tempfile
import time
import types
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

_tmp = tempfile.mkdtemp(prefix="astro_starter_")
os.environ["ASTRO_DATABASE_URL"] = f"sqlite:///{Path(_tmp).as_posix()}/t.db"
os.environ.update({
    "ASTRO_DEV_LOGIN": "1", "ASTRO_COOKIE_SECURE": "0", "ASTRO_GATEWAY": "test",
    "ASTRO_SMTP_HOST": "console", "ASTRO_ADMIN_EMAILS": "owner@example.com",
    "ASTRO_EMAIL_ANSWER_WORKER": "0", "ASTRO_OFFER_ENDS": "2099-01-01T00:00:00+05:30",
})
for k in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ASTRO_STARTER_ENABLED",
          "ASTRO_EMAIL_ANSWER_AVG_MIN", "ASTRO_FREE_QUESTIONS"):
    os.environ.pop(k, None)

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import func, inspect, select  # noqa: E402

from app import analytics, billing, emailed_answers as ea, llm, mail  # noqa: E402
from app.db import (CREDIT_EMAIL, CreditEntry, EmailedAnswerJob, Event, QuestionLog,  # noqa: E402
                    User, balance, email_balance, session as db_session, utcnow)
from app.main import app  # noqa: E402
from tests.fake_ollama import FakeOllama  # noqa: E402

failures: list[str] = []
BIRTH = {"name": "Asha", "date": "1990-03-21", "time": "06:15", "place": "Delhi, India",
         "latitude": 28.6519, "longitude": 77.2315, "timezone": "Asia/Kolkata"}
CHROME = ("Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) "
          "Chrome/126.0 Mobile Safari/537.36")

OLLAMA = FakeOllama().start()
os.environ["ASTRO_EMAIL_ANSWER_OLLAMA_URL"] = OLLAMA.url
# These tests exercise the local-model path and its fallbacks; production defaults to Claude.
os.environ["ASTRO_EMAIL_ANSWER_WRITER"] = "ollama"


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


# ---------------------------------------------------------------- fake Claude
CLAUDE = {"fail": False, "streams": [], "translations": []}
CLAUDE_TEXT = ("**Claude's reading.** The tenth house and its lord show a slow and steady rise; "
               "the running period rewards patience and careful work over sudden moves. "
               "Keep your commitments and the recognition follows.")


def _fake_anthropic():
    class Stream:
        def __init__(self, kw):
            self.kw = kw

        def __enter__(self):
            if CLAUDE["fail"]:
                raise RuntimeError("simulated: Your credit balance is too low")
            CLAUDE["streams"].append(self.kw)
            return self

        def __exit__(self, *a):
            return False

        @property
        def text_stream(self):
            yield CLAUDE_TEXT

        def get_final_message(self):
            return types.SimpleNamespace(stop_reason="end_turn")

    class Messages:
        def stream(self, **kw):
            return Stream(kw)

        def create(self, **kw):
            if CLAUDE["fail"]:
                raise RuntimeError("simulated: Your credit balance is too low")
            CLAUDE["translations"].append(kw)
            text = kw["messages"][0]["content"]
            return types.SimpleNamespace(
                stop_reason="end_turn",
                content=[types.SimpleNamespace(text="[अनुवाद] " + text)])

    class Client:
        def __init__(self, **kw):
            self.beta = types.SimpleNamespace(messages=Messages())
            self.messages = Messages()

    return types.SimpleNamespace(Anthropic=Client)


sys.modules["anthropic"] = _fake_anthropic()


def claude_on(on: bool = True) -> None:
    if on:
        os.environ["ANTHROPIC_API_KEY"] = "fake-key"
    else:
        os.environ.pop("ANTHROPIC_API_KEY", None)


def reset_claude(fail: bool = False) -> None:
    CLAUDE.update({"fail": fail, "streams": [], "translations": []})


# ---------------------------------------------------------------- helpers
def browser(email: str) -> TestClient:
    c = TestClient(app, client=("203.0.113.9", 40000), headers={"User-Agent": CHROME})
    r = c.post("/api/auth/dev", json={"email": email})
    assert r.status_code == 200, r.text
    return c


def me(c: TestClient) -> dict:
    return c.get("/api/me").json()["user"]


def buy_starter(c: TestClient):
    r = c.post("/api/orders", json={"sku": billing.STARTER_SKU})
    if r.status_code != 200:
        return r
    return c.post("/api/orders/confirm", json={"order_id": r.json()["order"]["id"], "payload": {}})


def cast(c: TestClient) -> str:
    r = c.post("/api/chart", json=BIRTH)
    assert r.status_code == 200, r.text[:200]
    return r.json()["session_id"]


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


def ask(c, sid, q="Will my career improve this year?", lang="en"):
    return c.post("/api/ask/stream", json={"session_id": sid, "question": q,
                                           "language": lang, "provider": "off"})


def spend_instant(c, sid) -> None:
    while me(c)["credits"] > 0:
        r = ask(c, sid, "Instant question")
        assert r.status_code == 200, r.text[:200]


def job(job_id: int) -> EmailedAnswerJob:
    with db_session() as db:
        return db.get(EmailedAnswerJob, job_id)


def mails_to(addr: str) -> list:
    return [m for m in mail.OUTBOX if addr in m[0]]


def customer_with_starter(email: str, lang: str = "en"):
    """Signed in, Starter bought, instant credits spent: the next ask is emailed."""
    c = browser(email)
    buy_starter(c)
    sid = cast(c)
    spend_instant(c, sid)
    r = ask(c, sid, "What does my chart say about my career this year?", lang)
    ev = events(r.text)
    queued = [d for e, d in ev if e == "queued"]
    assert queued, r.text[:300]
    return c, sid, queued[0]["job_id"]


def fresh_queue() -> None:
    """Earlier parts' leftovers must not change which job run_next picks."""
    with db_session() as db:
        for j in db.execute(select(EmailedAnswerJob).where(
                EmailedAnswerJob.status.in_(("pending", "running")))).scalars():
            j.status = "failed"
        db.commit()


# ---------------------------------------------------------------- 1. product
def part0_writer_default() -> None:
    print("\n0. Writer: Claude by default; every job routed to Claude, never counted as a fallback")
    saved = os.environ.pop("ASTRO_EMAIL_ANSWER_WRITER", None)
    try:
        check("default writer is claude", ea.writer() == "claude")
        class J:  # minimal stand-in for a pending job
            def __init__(self, i): self.id, self.created_at = i, ea.utcnow()
        routes = ea.plan([J(1), J(2)], ea.utcnow(), 240.0, True)
        check("all jobs routed to claude", routes == {1: "claude", 2: "claude"}, str(routes))
        check("'claude' is not a fallback reason", "claude" not in ea.FALLBACK_REASONS)
    finally:
        if saved is not None:
            os.environ["ASTRO_EMAIL_ANSWER_WRITER"] = saved


def part1_product() -> None:
    print("\n1. The Starter product")
    p = billing.PRODUCTS[billing.STARTER_SKU]
    check("Rs 21, 3 credits, kind email_answers, not on the offer",
          p.list_paise == 2100 and p.offer_paise == 2100 and p.credits == 3
          and p.kind == "email_answers" and p.on_offer is False)
    before = dt.datetime(2026, 10, 20, tzinfo=dt.timezone.utc)
    after = dt.datetime(2026, 12, 1, tzinfo=dt.timezone.utc)
    with mock.patch.dict(os.environ, {"ASTRO_OFFER_ENDS": "2026-11-15T23:59:59+05:30"}):
        check("the offer engine ignores it: 21 during and after the Diwali offer",
              billing.effective_price_paise(billing.STARTER_SKU, before) == 2100
              and billing.effective_price_paise(billing.STARTER_SKU, after) == 2100)
        d = p.to_dict(before)
        check("its catalogue entry has no strike price and no offer end while the offer runs",
              d["list_amount_paise"] is None and d["offer"]["active"] is False
              and d["offer"]["ends_at"] is None and d["rupees"] == 21, str(d))
        check("while other products ARE on offer", billing.PRODUCTS["q10"].to_dict(before)["offer"]["active"])

    c = browser("buyer1@example.com")
    st = me(c)
    check("a new account: 3 instant questions, 0 emailed, Starter available",
          st["credits"] == 3 and st["email_credits"] == 0 and st["starter"]["available"], str(st))
    r = c.post("/api/orders", json={"sku": billing.STARTER_SKU, "coupon_code": "ANY10"})
    check("a coupon cannot be used on it", r.status_code == 400 and "Coupon" in r.text, r.text)
    pv = c.post("/api/coupons/preview", json={"sku": billing.STARTER_SKU, "code": "ANY10"}).json()
    check("...and the coupon preview says so", pv["valid"] is False and pv["final"] == 2100, str(pv))
    r = c.post("/api/orders", json={"sku": billing.STARTER_SKU})
    check("the order is created at 2100 paise", r.status_code == 200
          and r.json()["order"]["amount_paise"] == 2100 and r.json()["checkout"]["amount"] == 2100, r.text[:200])
    oid = r.json()["order"]["id"]
    r = c.post("/api/orders", json={"sku": billing.STARTER_SKU})
    check("an unpaid order does not block a new attempt", r.status_code == 200)
    r = c.post("/api/orders/confirm", json={"order_id": oid, "payload": {}})
    check("paid: 3 emailed answers granted, instant balance untouched",
          r.json()["granted"] and r.json()["email_credits"] == 3 and r.json()["credits"] == 3, r.text[:200])
    r = c.post("/api/orders", json={"sku": billing.STARTER_SKU})
    check("a second Starter is refused with 409 and a clear message",
          r.status_code == 409 and "one-time" in r.json()["detail"], r.text)
    check("/api/me: Starter no longer available (bought)", me(c)["starter"] == {"available": False, "reason": "bought"})
    with db_session() as db:
        uid = me(c)["id"]
        rows = db.execute(select(CreditEntry).where(CreditEntry.user_id == uid)).scalars().all()
    check("ledger: the purchase row is credit_type=email, the signup gift question",
          sorted((e.kind.value, e.credit_type, e.delta) for e in rows)
          == [("purchase", "email", 3), ("signup_bonus", "question", 3)], str([(e.kind, e.credit_type) for e in rows]))

    with mock.patch.dict(os.environ, {"ASTRO_STARTER_ENABLED": "0"}):
        skus = [p["sku"] for p in c.get("/api/products").json()["products"]]
        c2 = browser("buyer2@example.com")
        r = c2.post("/api/orders", json={"sku": billing.STARTER_SKU})
        check("ASTRO_STARTER_ENABLED=0: not in /api/products, order refused (409)",
              billing.STARTER_SKU not in skus and r.status_code == 409, r.text)
        check("...and /pricing does not list it", 'id="starter_email3"' not in c.get("/pricing").text)
    check("enabled: /api/products lists it", billing.STARTER_SKU in
          [p["sku"] for p in c.get("/api/products").json()["products"]])

    # An account with no email (phone / username sign-in) cannot buy a promise to email.
    with db_session() as db:
        u = User(email="", name="Phone person", provider="phone", provider_sub="+919999900001")
        db.add(u)
        db.commit()
        st = billing.starter_status(db, u)
        refused = False
        try:
            billing.create_order(db, u, billing.STARTER_SKU)
        except billing.StarterRefused as exc:
            refused = "email" in str(exc)
    check("no email: starter_status = no_email and create_order refuses", st["reason"] == "no_email" and refused, str(st))

    # UPI claim pending blocks a second purchase too.
    c3 = browser("buyer3@example.com")
    oid = c3.post("/api/orders", json={"sku": billing.STARTER_SKU}).json()["order"]["id"]
    from app.db import Order, OrderStatus
    with db_session() as db:
        db.get(Order, oid).status = OrderStatus.awaiting_verification
        db.commit()
    r = c3.post("/api/orders", json={"sku": billing.STARTER_SKU})
    check("a UPI claim awaiting verification blocks a second order (409, 'pending')",
          r.status_code == 409 and me(c3)["starter"]["reason"] == "pending", r.text)

    print("\n   /pricing and JSON-LD")
    for path, words in (("/pricing", "Once per account"), ("/hi/pricing", "एक खाते पर एक बार")):
        h = c.get(path).text
        m = re.search(r'<tr id="starter_email3".*?</tr>', h, re.S)
        row = m.group(0) if m else ""
        check(f"{path}: the Starter row at ₹21, no strike, no Save badge",
              "<b>₹21</b>" in row and 'class="was"' not in row and "pr-save" not in row, row[:300])
        check(f"{path}: the 30-minute promise and '{words}'", "30" in h and words in h)
        ld = []
        for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S):
            data = json.loads(block.replace("<\\/", "</"))
            ld += data.get("@graph", [data]) if isinstance(data, dict) else data
        node = next((n for n in ld if n.get("@type") == "Product" and n.get("sku") == billing.STARTER_SKU), None)
        check(f"{path}: Product/Offer JSON-LD at 21 INR, no priceValidUntil",
              node is not None and node["offers"]["price"] == "21"
              and node["offers"]["priceCurrency"] == "INR" and "priceValidUntil" not in node["offers"], str(node))


# ---------------------------------------------------------------- 2/3. balances + enqueue
def part2_enqueue() -> None:
    print("\n2. Separate balances, and asking with only emailed answers left")
    c = browser("asker@example.com")
    buy_starter(c)
    sid = cast(c)
    r = ask(c, sid, "First instant question")
    ev = dict(events(r.text))
    check("with instant questions left, the answer is instant (not queued)",
          "analysis" in ev and "queued" not in ev)
    st = me(c)
    check("the instant answer spent an instant question only", st["credits"] == 2 and st["email_credits"] == 3, str(st))
    spend_instant(c, sid)
    check("instant balance 0, emailed 3", me(c)["credits"] == 0 and me(c)["email_credits"] == 3)

    t0 = time.monotonic()
    r = ask(c, sid, "Will I change jobs this year?")
    took = time.monotonic() - t0
    ev = events(r.text)
    names = [e for e, _ in ev]
    q = dict(ev).get("queued") or {}
    check("the stream answers at once with one 'queued' event and 'done' (nothing analysed)",
          names == ["queued", "done"] and took < 3, f"{names} in {took:.2f}s")
    check("the queued payload: email, minutes = 30, emailed answers left = 2",
          q.get("email") == "asker@example.com" and q.get("minutes") == 30
          and q.get("email_credits") == 2 and q.get("credits") == 0, str(q))
    with db_session() as db:
        j = db.get(EmailedAnswerJob, q["job_id"])
        bj = json.loads(j.birth_json)
    check("a pending job holds the birth payload, language, question",
          j.status == "pending" and bj["date"] == BIRTH["date"] and j.language == "en"
          and j.question == "Will I change jobs this year?" and j.email == "asker@example.com")
    r = c.post("/api/ask", json={"session_id": sid, "question": "Non-stream ask", "provider": "off"})
    check("/api/ask answers 202 queued as well", r.status_code == 202 and r.json()["queued"], r.text[:200])
    ask(c, sid, "Third")
    r = ask(c, sid, "Fourth: nothing left")
    check("with both balances at 0 the paywall (402) is back", r.status_code == 402, r.text[:120])
    h = c.get("/api/history").json()["questions"]
    pend = [x for x in h if x.get("emailed") and x["emailed"]["status"] == "pending"]
    check("My questions lists the 3 waiting answers with their due time",
          len(pend) == 3 and all(x["emailed"]["due"] for x in pend), str(pend[:1]))
    fresh_queue()


# ---------------------------------------------------------------- 4. worker
def run(job_id: int) -> EmailedAnswerJob:
    done = ea.run_next()
    assert done == job_id, (done, job_id)
    return job(job_id)


def part4_worker() -> None:
    print("\n4. The worker")
    claude_on(True)

    # English, Ollama up: no translation.
    reset_claude()
    OLLAMA.mode, OLLAMA.requests = "ok", []
    c, sid, jid = customer_with_starter("en-happy@example.com", "en")
    j = run(jid)
    check("en: done by the local model, no translation call",
          j.status == "done" and j.model_used == "ollama:qwen2.5:7b" and j.translator == ""
          and not CLAUDE["translations"] and not CLAUDE["streams"], f"{j.status} {j.model_used} {j.error}")
    req = OLLAMA.requests[-1]
    user_msg = req["messages"][1]["content"]
    check("the local model got the chat's narration prompt in English, no 'keep it short' note, num_predict 1000",
          req["model"] == "qwen2.5:7b" and "Write the answer in English" in user_msg
          and "keep this rewrite tight" not in user_msg and req["options"]["num_predict"] == 1000
          and "Chart evidence behind that verdict" in user_msg)
    m = mails_to("en-happy@example.com")
    check("an email went to the customer with the question, answer, chart and disclaimer",
          len(m) == 1 and "What does my chart say about my career" in m[0][2]
          and "steady rise through effort" in m[0][2] and "Asha" in m[0][2]
          and "not medical, legal or financial advice" in m[0][2] and m[0][3] and "<html" in m[0][3]
          and "Your career question." in m[0][2] and "**" not in m[0][2], (m[0][2][:400] if m else ""))
    check("the email says it was written by the site's AI, not a person",
          m and "Written by Divine Astro's AI" in m[0][2] and "astrologer" not in m[0][2].lower())
    with db_session() as db:
        row = db.get(QuestionLog, j.question_id)
    check("saved to My questions (charged), birth payload cleared",
          row is not None and "steady rise" in row.answer and row.charged and j.birth_json == "")
    h = c.get("/api/history").json()["questions"]
    top = next(x for x in h if x["id"] == j.question_id)
    check("/api/history marks it emailed with the delivery time",
          top["emailed"]["status"] == "done" and top["emailed"]["delivered"], str(top["emailed"]))
    check("1 emailed answer was spent", me(c)["email_credits"] == 2)

    # Hindi, Ollama up: English from the local model, translated by Claude.
    reset_claude()
    OLLAMA.requests = []
    c, sid, jid = customer_with_starter("hi-happy@example.com", "hi")
    j = run(jid)
    tr = CLAUDE["translations"]
    check("hi: written by the local model IN ENGLISH, then translated once by Claude",
          j.model_used == "ollama:qwen2.5:7b" and j.translator.startswith("anthropic:")
          and len(tr) == 1 and "Write the answer in English" in OLLAMA.requests[-1]["messages"][1]["content"]
          and "Hindi" in tr[0]["system"] and "Add nothing" in tr[0]["system"]
          and "Capricorn=मकर" in tr[0]["system"], f"{j.model_used} {j.translator} {len(tr)}")
    m = mails_to("hi-happy@example.com")
    check("hi: the email is in Hindi with the translated answer",
          m and m[0][1] == "डिवाइन एस्ट्रो से आपका विस्तृत उत्तर" and "[अनुवाद]" in m[0][2]
          and "आपका प्रश्न" in m[0][2] and "मार्गदर्शन और मनोरंजन" in m[0][2], (m[0][2][:300] if m else ""))

    # Ollama down -> Claude, written in the customer's language directly.
    reset_claude()
    OLLAMA.mode = "down"
    c, sid, jid = customer_with_starter("down@example.com", "hi")
    j = run(jid)
    check("Ollama down -> Claude writes it (in Hindi, no separate translation)",
          j.status == "done" and j.model_used.startswith("anthropic:") and j.route_reason == "ollama_down"
          and len(CLAUDE["streams"]) == 1 and not CLAUDE["translations"]
          and "Hindi" in CLAUDE["streams"][0]["system"], f"{j.model_used} {j.route_reason}")
    check("...and it is emailed", len(mails_to("down@example.com")) == 1)

    # Ollama errors mid-call -> Claude.
    reset_claude()
    OLLAMA.mode = "error"
    c, sid, jid = customer_with_starter("err@example.com", "en")
    j = run(jid)
    check("Ollama returns an error -> Claude", j.model_used.startswith("anthropic:")
          and j.route_reason == "ollama_error" and "ollama" in j.error, f"{j.route_reason} {j.error}")

    # Projected late -> Claude.
    reset_claude()
    OLLAMA.mode = "ok"
    # The measured average (here: 30 min a job) is what the plan uses once there is one.
    with mock.patch.object(ea, "ollama_avg_s", return_value=1800.0):
        c, sid, jid = customer_with_starter("late@example.com", "en")
        j = run(jid)
    check("projected finish > 25 min -> Claude", j.model_used.startswith("anthropic:")
          and j.route_reason == "projected_late", f"{j.route_reason}")

    # plan(): queue position x average.
    now = utcnow()
    jobs = [types.SimpleNamespace(id=i, created_at=now - dt.timedelta(minutes=1)) for i in range(1, 7)]
    routes = ea.plan(jobs, now, 600, True)
    check("plan: with 10 min per local job, the first two fit in 25 min, the rest go to Claude",
          [routes[i] for i in range(1, 7)] == ["ollama", "ollama", "projected_late", "projected_late",
                                               "projected_late", "projected_late"], str(routes))
    check("plan: Ollama down routes everything to Claude",
          set(ea.plan(jobs, now, 240, False).values()) == {"ollama_down"})

    # Claude fails too -> the engine's reading with an honest note.
    reset_claude(fail=True)
    OLLAMA.mode = "down"
    ea._alert_state.update({"last": 0.0, "pending": []})
    before_admin = len(mails_to("owner@example.com"))
    c, sid, jid = customer_with_starter("engine@example.com", "hi")
    j = run(jid)
    m = mails_to("engine@example.com")
    check("Claude failing too -> the rule engine's reading, model_used=engine, still emailed",
          j.status == "done" and j.model_used == "engine" and len(m) == 1, f"{j.model_used} {j.status}")
    check("...with the one-line note in the customer's language",
          m and "हमारा लेखन मॉडल समय पर उपलब्ध नहीं था" in m[0][2])
    with db_session() as db:
        row = db.get(QuestionLog, j.question_id)
    check("...saved to My questions with the note", row and row.answer.startswith("हमारा लेखन मॉडल"))
    admin_mails = mails_to("owner@example.com")[before_admin:]
    check("the admin is alerted (Claude failed), one email",
          len(admin_mails) == 1 and "[claude_failed]" in admin_mails[0][2] + "".join(ea._alert_state["pending"]),
          str([a[2][:200] for a in admin_mails]))

    # Without any Claude key the engine path is used as well.
    claude_on(False)
    reset_claude()
    c, sid, jid = customer_with_starter("nokey@example.com", "ta")
    j = run(jid)
    m = mails_to("nokey@example.com")
    check("no Claude key + Ollama down (Tamil) -> engine reading, note + 'in English' line, Tamil email",
          j.model_used == "engine" and m and "டிவைன் ஆஸ்ட்ரோ" in m[0][1]
          and "ஆங்கிலத்தில்" in m[0][2], (m[0][2][:200] if m else ""))
    claude_on(True)
    OLLAMA.mode = "ok"


# ---------------------------------------------------------------- 5. failures
def part5_failures() -> None:
    print("\n5. Failures, refunds, restarts, alerts")
    reset_claude()
    OLLAMA.mode = "ok"

    c, sid, jid = customer_with_starter("broken@example.com", "en")
    with db_session() as db:
        db.get(EmailedAnswerJob, jid).birth_json = '{"not": "a birth"}'
        db.commit()
    left = me(c)["email_credits"]
    j = run(jid)
    check("a chart that cannot be rebuilt: failed and refunded",
          j.status == "failed" and j.refunded and me(c)["email_credits"] == left + 1, f"{j.status} {j.error[:80]}")
    m = mails_to("broken@example.com")
    check("...the customer is told, and the credit is back", m and "could not prepare" in m[-1][1].lower())
    h = c.get("/api/history").json()["questions"]
    check("...My questions shows it as failed (refunded)",
          any(x.get("emailed") and x["emailed"]["status"] == "failed" and x["emailed"]["refunded"] for x in h))

    c, sid, jid = customer_with_starter("nomail@example.com", "en")
    left = me(c)["email_credits"]
    with mock.patch.object(mail, "send", return_value=False):
        j = run(jid)
    with db_session() as db:
        row = db.get(QuestionLog, j.question_id) if j.question_id else None
    check("an email that cannot be sent: failed, refunded, answer kept in My questions (charged=False)",
          j.status == "failed" and j.refunded and me(c)["email_credits"] == left + 1
          and row is not None and row.charged is False, f"{j.status} {row and row.charged}")

    # A restart mid-job.
    c, sid, jid = customer_with_starter("restart@example.com", "en")
    with db_session() as db:
        r = db.get(EmailedAnswerJob, jid)
        r.status, r.attempts = "running", 1
        db.commit()
    check("before recovery a 'running' job is not picked", ea.run_next() is None)
    n = ea.recover()
    j = run(jid)
    check("recover() puts it back and the next pass delivers it",
          n == 1 and j.status == "done" and j.attempts == 2, f"{n} {j.status} {j.attempts}")
    with db_session() as db:
        r = db.get(EmailedAnswerJob, jid)
        r.status, r.attempts = "running", 3
        db.commit()
    ea.recover()
    j = job(jid)
    check("a job interrupted MAX_ATTEMPTS times fails and is refunded", j.status == "failed" and j.refunded)

    # Late delivery alert.
    ea._alert_state.update({"last": 0.0, "pending": []})
    before_admin = len(mails_to("owner@example.com"))
    c, sid, jid = customer_with_starter("tardy@example.com", "en")
    with db_session() as db:
        db.get(EmailedAnswerJob, jid).created_at = utcnow() - dt.timedelta(minutes=40)
        db.commit()
    j = run(jid)
    admin_mails = mails_to("owner@example.com")[before_admin:]
    seen = "".join(a[2] for a in admin_mails) + "".join(ea._alert_state["pending"])
    check("a job delivered after 30 minutes alerts the admin (and Claude wrote it: past the safe point)",
          j.status == "done" and j.route_reason == "projected_late"
          and len(admin_mails) == 1 and "[late] job" in seen, seen[:300])

    # Rate limit: one email an hour.
    ea._alert_state.update({"last": 0.0, "pending": []})
    before_admin = len(mails_to("owner@example.com"))
    sent = [ea._alert("test", f"n{i}") for i in range(3)]
    check("alerts: 3 in a row -> one email, the rest held back", sent == [True, False, False]
          and len(mails_to("owner@example.com")) == before_admin + 1, str(sent))
    ea._alert_state["last"] = time.monotonic() - 3601
    check("an hour later the held-back lines go out with the next alert",
          ea._alert("test", "n3") and "n1" in mails_to("owner@example.com")[-1][2])

    # Fallback-rate alert.
    ea._alert_state.update({"last": 0.0, "pending": []})
    with mock.patch.dict(os.environ, {"ASTRO_EMAIL_ANSWER_FALLBACK_ALERT": "1"}):
        OLLAMA.mode = "down"
        before_admin = len(mails_to("owner@example.com"))
        for k in range(2):
            c, sid, jid = customer_with_starter(f"fb{k}@example.com", "en")
            run(jid)
        alerts = "".join(m[2] for m in mails_to("owner@example.com")[before_admin:]) + "".join(ea._alert_state["pending"])
    check("more than N local-model fallbacks in an hour raises the 'fallbacks' alert", "[fallbacks]" in alerts)
    OLLAMA.mode = "ok"


# ---------------------------------------------------------------- 6. admin, events, migration
def part6_admin() -> None:
    print("\n6. Admin tile, events, migration")
    admin = browser("owner@example.com")
    d = admin.get("/api/admin/traffic?days=7").json()
    t = d.get("email_answers") or {}
    with db_session() as db:
        total = db.execute(select(func.count(EmailedAnswerJob.id))).scalar_one()
    check("Traffic carries today's emailed answers: count, delivered, failed, late, median, model mix",
          t.get("today") == total and t["delivered"] >= 8 and t["failed"] >= 2 and t["late"] >= 1
          and t["median_minutes"] is not None
          and any(k.startswith("ollama:") for k in t["models"]) and "engine" in t["models"], str(t))
    with db_session() as db:
        names = {n for (n,) in db.execute(select(Event.name)).all()}
    check("events recorded: email_answer_queued and email_answer_delivered",
          {"email_answer_queued", "email_answer_delivered"} <= names, str(names))
    check("starter_shown / starter_click accepted from the app",
          analytics.parse_event({"name": "starter_shown", "detail": "store"}) == ("starter_shown", "store")
          and analytics.parse_event({"name": "starter_click", "detail": "paywall"}) is not None)
    day = admin.get("/api/admin/traffic/day").json()
    labels = {a["label"] for a in day["actions"]}
    check("the day report words them", "Asked a question to be answered by email" in labels
          and "An emailed answer was delivered" in labels, str(labels))
    check("every new event has a plain-words label",
          all((n, "") in analytics.EVENT_LABELS for n in
              ("starter_shown", "starter_click", "email_answer_queued", "email_answer_delivered")))

    from alembic import command
    from alembic.config import Config
    from sqlalchemy import create_engine
    root = Path(__file__).resolve().parent.parent
    url = f"sqlite:///{Path(_tmp).as_posix()}/mig.db"
    cfg = Config(str(root / "alembic.ini"))
    cfg.set_main_option("script_location", str(root / "migrations"))
    cfg.set_main_option("sqlalchemy.url", url)
    app_url = os.environ["ASTRO_DATABASE_URL"]
    os.environ["ASTRO_DATABASE_URL"] = url       # migrations/env.py reads the URL from here
    try:
        _migrate(cfg, url, create_engine, command)
    finally:
        os.environ["ASTRO_DATABASE_URL"] = app_url


def _migrate(cfg, url, create_engine, command) -> None:
    command.upgrade(cfg, "head")
    eng = create_engine(url)
    cols = {c["name"] for c in inspect(eng).get_columns("credit_entries")}
    check("migration up: emailed_answer_jobs + credit_entries.credit_type",
          "emailed_answer_jobs" in inspect(eng).get_table_names() and "credit_type" in cols)
    with eng.begin() as con:
        con.exec_driver_sql("INSERT INTO users (id, email, name, picture, provider, provider_sub, phone, "
                            "language, created_at, last_seen_at, is_admin, blocked) VALUES "
                            "(1,'a@b.c','','','dev','x','','en','2026-10-01','2026-10-01',0,0)")
        con.exec_driver_sql("INSERT INTO credit_entries (user_id, delta, kind, note, created_at) "
                            "VALUES (1, 3, 'signup_bonus', '', '2026-10-01')")
        ct = con.exec_driver_sql("SELECT credit_type FROM credit_entries").scalar()
        con.exec_driver_sql("INSERT INTO credit_entries (user_id, delta, kind, note, created_at, credit_type) "
                            "VALUES (1, 3, 'purchase', '', '2026-10-01', 'email')")
    check("an existing/new row without credit_type defaults to 'question'", ct == "question")
    eng.dispose()
    command.downgrade(cfg, "d1e2f3a4b5c6")
    eng = create_engine(url)
    cols = {c["name"] for c in inspect(eng).get_columns("credit_entries")}
    with eng.begin() as con:
        total = con.exec_driver_sql("SELECT SUM(delta) FROM credit_entries").scalar()
    check("migration down: table and column gone, emailed rows removed (instant balance intact)",
          "emailed_answer_jobs" not in inspect(eng).get_table_names() and "credit_type" not in cols
          and total == 3, f"{cols} {total}")
    eng.dispose()
    command.upgrade(cfg, "head")
    eng = create_engine(url)
    check("and up again", "emailed_answer_jobs" in inspect(eng).get_table_names())
    eng.dispose()


def main() -> int:
    try:
        part0_writer_default()
        part1_product()
        part2_enqueue()
        part4_worker()
        part5_failures()
        part6_admin()
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
