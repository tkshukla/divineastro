"""DIVASTRO-158: buying the Starter without signing in.

In process (TestClient, a throwaway SQLite database, the console mail transport, a
FAKE `anthropic` module for the emailed-answer worker), so nothing leaves the machine:

  1. A guest order: email (validated) + optional phone + the chart the guest cast;
     a placeholder account (provider "guest", no session, not a sign-up); the same
     price and once-per-account rule; only allow-listed skus; chart required; a
     signed-in visitor is sent to the store.
  2. An address that already has an account: the order is credited to that account,
     the reply is identical in shape to a new address's, nothing of the account (name,
     phone, questions, charts) reaches the buyer or the gateway, no session is issued,
     and a refusal (Starter already bought, suspended account) is one generic sentence.
  3. Payment: the test gateway's confirm (by token), the webhook, and PayU's signed
     return (amount-checked; the redirect carries the token only when verified) all
     credit the right user once, and email the buyer the link to the order once.
  4. The token: unguessable (signed), bound to one guest order; questions only once
     paid, at most the number bought; each becomes an emailed-answer job to the
     order's address, written without the account's other conversations; the birth
     details leave the order once the questions are in.
  5. Rate limits per IP and per email.
  6. The first sign-in with that address (email code, Google/dev) adopts the
     placeholder: the order and answers are there; Microsoft does not adopt it.
  7. Analytics events, the funnel, the privacy text, the migration up and down.

    ASTRO_SECRET_KEY=ci python -u -m tests.test_guest_checkout
"""

from __future__ import annotations

import json
import re
import os
import sys
import tempfile
import types
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

_tmp = tempfile.mkdtemp(prefix="astro_guestpay_")
os.environ["ASTRO_DATABASE_URL"] = f"sqlite:///{Path(_tmp).as_posix()}/t.db"
os.environ.update({
    "ASTRO_DEV_LOGIN": "1", "ASTRO_COOKIE_SECURE": "0", "ASTRO_GATEWAY": "test",
    "ASTRO_SMTP_HOST": "console", "ASTRO_ADMIN_EMAILS": "owner@example.com",
    "ASTRO_EMAIL_ANSWER_WORKER": "0", "ASTRO_OFFER_ENDS": "2099-01-01T00:00:00+05:30",
    "ANTHROPIC_API_KEY": "fake-key",
})
for k in ("ASTRO_STARTER_ENABLED", "ASTRO_EMAIL_ANSWER_WRITER", "ASTRO_FREE_QUESTIONS",
          "PAYU_MERCHANT_KEY", "PAYU_SALT"):
    os.environ.pop(k, None)

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import inspect, select  # noqa: E402

from app import analytics, auth, billing, email_auth, gateways, guest_checkout as gc  # noqa: E402
from app import emailed_answers as ea, mail  # noqa: E402
from app.db import (EmailedAnswerJob, Event, Order, OrderStatus, QuestionLog, User,  # noqa: E402
                    balance, email_balance, session as db_session)
from app.main import app  # noqa: E402

failures: list[str] = []
BIRTH = {"name": "Asha", "date": "1990-03-21", "time": "06:15", "place": "Delhi, India",
         "latitude": 28.6519, "longitude": 77.2315, "timezone": "Asia/Kolkata"}
CHROME = ("Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) "
          "Chrome/126.0 Mobile Safari/537.36")
SKU = billing.STARTER_SKU


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


# ---------------------------------------------------------------- fake Claude
CLAUDE = {"streams": []}
CLAUDE_TEXT = ("**Claude's reading.** The tenth house and its lord show a slow and steady rise; "
               "the running period rewards patience and careful work over sudden moves. "
               "Keep your commitments and the recognition follows.")


def _fake_anthropic():
    class Stream:
        def __init__(self, kw):
            self.kw = kw

        def __enter__(self):
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
            return types.SimpleNamespace(stop_reason="end_turn",
                                         content=[types.SimpleNamespace(text=kw["messages"][0]["content"])])

    class Client:
        def __init__(self, **kw):
            self.beta = types.SimpleNamespace(messages=Messages())
            self.messages = Messages()

    return types.SimpleNamespace(Anthropic=Client)


sys.modules["anthropic"] = _fake_anthropic()

_ip_n = [10]


# ---------------------------------------------------------------- helpers
def visitor(ip: str | None = None) -> TestClient:
    """A fresh signed-out browser on its own address (rate limits are per IP)."""
    if ip is None:
        _ip_n[0] += 1
        ip = f"198.51.100.{_ip_n[0]}"
    return TestClient(app, client=(ip, 40000), headers={"User-Agent": CHROME})


def signed_in(email: str, name: str = "") -> TestClient:
    c = visitor()
    r = c.post("/api/auth/dev", json={"email": email, "name": name or email.split("@")[0]})
    assert r.status_code == 200, r.text
    return c


def cast(c: TestClient) -> str:
    r = c.post("/api/chart", json=BIRTH)
    assert r.status_code == 200, r.text[:200]
    return r.json()["session_id"]


def checkout(c: TestClient, email: str, sid: str | None = "auto", phone: str = "", sku: str = SKU,
             lang: str = "en"):
    if sid == "auto":
        sid = cast(c)
    return c.post("/api/guest/checkout", json={"sku": sku, "email": email, "phone": phone,
                                               "session_id": sid or "", "lang": lang})


def confirm(c: TestClient, token: str):
    return c.post("/api/guest/confirm", json={"token": token, "payload": {}})


def order(order_id: int) -> Order:
    with db_session() as db:
        return db.get(Order, order_id)


def user_by(email: str) -> list[User]:
    with db_session() as db:
        return list(db.execute(select(User).where(User.email == email).order_by(User.id)).scalars())


def mails_to(addr: str) -> list:
    return [m for m in mail.OUTBOX if addr in m[0]]


def code(r) -> str:
    try:
        return (r.json().get("detail") or {}).get("code", "")
    except Exception:                                   # noqa: BLE001
        return ""


def reset() -> None:
    gc.reset_for_tests()


# ---------------------------------------------------------------- 1. a guest order
def part1_new_address() -> None:
    print("\n1. A guest order for a new address")
    reset()
    c = visitor()
    r = checkout(c, "  Neha.Guest@Example.org ", phone="+91 98765 43210")
    check("guest checkout opens a payment (200)", r.status_code == 200, r.text[:200])
    d = r.json()
    check("the reply carries the order, the gateway session and a token, and the typed address",
          set(d) == {"order", "checkout", "token", "email"} and d["email"] == "neha.guest@example.org"
          and d["order"]["amount_paise"] == billing.PRODUCTS[SKU].amount_paise == 2100, str(d)[:200])
    check("no session cookie is set and /api/me is still signed out",
          auth.COOKIE not in c.cookies and c.get("/api/me").json()["user"] is None)
    o = order(d["order"]["id"])
    users = user_by("neha.guest@example.org")
    check("a placeholder account: provider guest, no password, not a sign-up, no welcome questions",
          len(users) == 1 and users[0].provider == "guest" and users[0].password_hash is None
          and users[0].signup_source == "guest_checkout" and users[0].id == o.user_id
          and balance(db_session(), users[0].id) == 0, str([(u.provider, u.signup_source) for u in users]))
    p = json.loads(o.guest_json)
    check("the order carries the guest's email, phone and the chart's birth details (from the server session)",
          o.guest_email == "neha.guest@example.org" and o.guest_phone == "+919876543210"
          and p["birth"]["date"] == BIRTH["date"] and p["birth"]["latitude"] == BIRTH["latitude"]
          and o.status == OrderStatus.created and o.credits == 3, str(p)[:200])

    with db_session() as db:
        a = gc.account_for(db, "neha.guest@example.org")
        check("a second order for the address reuses the placeholder", a.id == o.user_id)
        db.rollback()

    check("an invalid address is refused (code email)",
          code(checkout(visitor(), "not-an-email")) == "email")
    r = checkout(visitor(), "someone@gmial.com")
    check("a mistyped common domain is caught (code typo, suggestion)",
          code(r) == "typo" and r.json()["detail"].get("s") == "someone@gmail.com", r.text[:200])
    check("a bad phone number is refused (code phone)",
          code(checkout(visitor(), "p1@example.org", phone="12ab")) == "phone")
    check("a product that is not on the guest list is refused (code unavailable)",
          code(checkout(visitor(), "p2@example.org", sku="q10")) == "unavailable")
    check("the Starter needs the guest's chart (code chart)",
          code(checkout(visitor(), "p3@example.org", sid=None)) == "chart")
    owner = signed_in("chartowner@example.com")
    owned_sid = cast(owner)
    check("a chart that belongs to an account cannot be sent by a guest (code chart)",
          code(checkout(visitor(), "p4@example.org", sid=owned_sid)) == "chart")
    check("a signed-in visitor is sent to the store (409 signed_in)",
          code(checkout(owner, "p5@example.org")) == "signed_in")
    os.environ["ASTRO_STARTER_ENABLED"] = "0"
    try:
        check("the Starter switched off: unavailable, and not listed as a guest sku",
              code(checkout(visitor(), "p6@example.org")) == "unavailable"
              and SKU not in visitor().get("/api/products").json()["guest_checkout"])
    finally:
        os.environ.pop("ASTRO_STARTER_ENABLED", None)
    check("/api/products lists the guest skus", visitor().get("/api/products").json()["guest_checkout"]
          == ["starter_email3"])
    check("adding a product is one line: GUEST_CHECKOUT_SKUS is the allow list",
          billing.GUEST_CHECKOUT_SKUS == frozenset({"starter_email3"}))


# ---------------------------------------------------------------- 2. an existing account
def part2_existing_account() -> None:
    print("\n2. An address that already has an account")
    reset()
    known = signed_in("known@example.com", name="Known Person")
    ksid = cast(known)
    # The account's own history: nothing of it may reach a guest.
    r = known.post("/api/ask/stream", json={"session_id": ksid, "question": "SECRET-QUESTION about me",
                                            "language": "en", "provider": "off"})
    assert r.status_code == 200, r.text[:200]
    with db_session() as db:
        ku = db.execute(select(User).where(User.email == "known@example.com")).scalar_one()
        ku.phone = "+910000011111"
        db.commit()
        kid = ku.id

    new = checkout(visitor(), "fresh-person@example.com").json()
    g = visitor()
    r = checkout(g, "KNOWN@example.com")
    d = r.json()
    check("checkout for a known address succeeds like any other (200)", r.status_code == 200, r.text[:200])
    check("the reply has exactly the same shape as for a new address (no leak)",
          set(d) == set(new) and set(d["order"]) == set(new["order"])
          and set(d["checkout"]) == set(new["checkout"]) and d["email"] == "known@example.com")
    blob = json.dumps(d)
    check("nothing of the account is in the reply (name, phone, user id)",
          "Known Person" not in blob and "0000011111" not in blob and f'"user_id": {kid}' not in blob)
    check("no session is issued: the guest is not signed in to that account",
          auth.COOKIE not in g.cookies and g.get("/api/me").json()["user"] is None)
    o = order(d["order"]["id"])
    check("the order belongs to the existing account (no duplicate account)",
          o.user_id == kid and len(user_by("known@example.com")) == 1)
    r = confirm(g, d["token"])
    s = r.json()
    check("paying credits the existing account's emailed answers",
          r.status_code == 200 and s["paid"] and email_balance(db_session(), kid) == 3, r.text[:200])
    blob = json.dumps(s)
    check("the order page shows this order only: none of the account's questions, name or phone",
          "SECRET-QUESTION" not in blob and "Known Person" not in blob and "0000011111" not in blob
          and s["questions"] == [] and s["email"] == "known@example.com", blob[:300])
    check("the account still sees the order in its own My orders",
          any(x["id"] == o.id and x["status"] == "paid" for x in known.get("/api/orders").json()["orders"]))
    check("the guest still cannot read the account's data (history 401)",
          g.get("/api/history").status_code == 401)

    # Once per account, without saying why.
    r2 = checkout(visitor(), "known@example.com")
    check("a second Starter for that address is refused with the generic sentence (409 refused)",
          r2.status_code == 409 and code(r2) == "refused", r2.text[:200])
    msg = r2.json()["detail"]["message"]
    with db_session() as db:
        b = User(email="blocked@example.com", provider="google", provider_sub="g-blocked", blocked=True)
        db.add(b)
        db.commit()
    r3 = checkout(visitor(), "blocked@example.com")
    check("a suspended account gets the very same reply (no difference to learn from)",
          r3.status_code == 409 and r3.json()["detail"] == r2.json()["detail"], r3.text[:200])
    check("the generic sentence names no account and no purchase status",
          "account" not in msg.lower() and "already" not in msg.lower(), msg)

    # The gateway is never shown the account's name or phone.
    os.environ.update({"ASTRO_GATEWAY": "payu", "PAYU_MERCHANT_KEY": "mk", "PAYU_SALT": "salt",
                       "PAYU_SURL": "http://t/api/payu/return", "PAYU_FURL": "http://t/api/payu/return"})
    gateways._ALL["payu"] = gateways.PayUGateway()
    try:
        with db_session() as db:
            k2 = User(email="named@example.com", name="Real Name Here", phone="+919999988888",
                      provider="google", provider_sub="g-named")
            db.add(k2)
            db.commit()
        r = checkout(visitor(), "named@example.com", phone="")
        f = r.json()["checkout"]["fields"]
        check("PayU sees the typed address, 'Customer' and the typed phone, never the account's",
              f["email"] == "named@example.com" and f["firstname"] == "Customer" and f["phone"] == ""
              and "Real Name" not in json.dumps(r.json()), str(f)[:200])
    finally:
        os.environ["ASTRO_GATEWAY"] = "test"


# ---------------------------------------------------------------- 3. payment paths
def _payu_form(gw, o: Order, amount: str, status: str = "success") -> dict:
    productinfo, firstname, email = o.title[:100], "Customer", o.guest_email
    return {"txnid": o.provider_order_id, "amount": amount, "productinfo": productinfo,
            "firstname": firstname, "email": email, "status": status, "mihpayid": f"MIH{o.id}",
            "hash": gw._reverse_hash(status, productinfo, firstname, email, amount, o.provider_order_id)}


def part3_payment_paths() -> None:
    print("\n3. Payment: test confirm, webhook, PayU return")
    reset()
    mail.OUTBOX.clear()
    g = visitor()
    d = checkout(g, "webhook-buyer@example.org", lang="hi").json()
    o = order(d["order"]["id"])
    body = json.dumps({"order_id": o.provider_order_id, "payment_id": "pay_wh_1"}).encode()
    r = visitor().post("/api/webhooks/payment", content=body)
    check("a webhook settles a guest order", r.status_code == 200 and r.json().get("granted"), r.text[:200])
    o = order(o.id)
    check("credited once to the order's account, as emailed answers",
          o.status == OrderStatus.paid and email_balance(db_session(), o.user_id) == 3)
    sent = mails_to("webhook-buyer@example.org")
    check("the buyer is emailed the link to the order page, in their language",
          len(sent) == 1 and "?gt=" in sent[0][2] and "lang=hi" in sent[0][2]
          and "प्रश्न" in sent[0][1], str([m[1] for m in sent]))
    m = re.search(r"\?gt=([^&\s]+)", sent[0][2]) if sent else None
    link_token = m.group(1) if m else ""
    visitor().post("/api/webhooks/payment", content=body)
    check("a replayed webhook grants nothing more and sends no second email",
          email_balance(db_session(), o.user_id) == 3 and len(mails_to("webhook-buyer@example.org")) == 1)
    s = visitor().post("/api/guest/order", json={"token": link_token}).json() if link_token else {}
    check("the emailed link's token opens that order (from any browser)",
          s.get("paid") is True and s.get("questions_left") == 3, str(s)[:200])

    # PayU's signed return
    os.environ.update({"ASTRO_GATEWAY": "payu", "PAYU_MERCHANT_KEY": "mk", "PAYU_SALT": "salt"})
    gateways._ALL["payu"] = gateways.PayUGateway()
    gw = gateways._ALL["payu"]
    try:
        g = visitor()
        d = checkout(g, "payu-buyer@example.org").json()
        o = order(d["order"]["id"])
        check("guest confirm is refused for PayU (its signed return is the only path)",
              code(confirm(g, d["token"])) == "unavailable" and order(o.id).status == OrderStatus.created)
        bad = _payu_form(gw, o, "1.00")
        bad["hash"] = gw._reverse_hash("success", bad["productinfo"], "Customer", o.guest_email,
                                       "1.00", o.provider_order_id)
        r = g.post("/api/payu/return", data=bad, follow_redirects=False)
        loc = r.headers.get("location", "")
        check("a signed return for a different amount grants nothing and carries no token",
              "payu=failed" in loc and "gt=" not in loc and order(o.id).status == OrderStatus.created, loc)
        forged = _payu_form(gw, o, "21.00")
        forged["hash"] = "0" * 128
        r = g.post("/api/payu/return", data=forged, follow_redirects=False)
        loc = r.headers.get("location", "")
        check("a forged hash grants nothing and carries no token",
              "payu=failed" in loc and "gt=" not in loc, loc)
        r = g.post("/api/payu/return", data=_payu_form(gw, o, "21.00"), follow_redirects=False)
        loc = r.headers.get("location", "")
        q = parse_qs(urlparse(loc).query)
        check("PayU's verified return pays the order and redirects with the order's token",
              "payu=ok" in loc and q.get("gt") and order(o.id).status == OrderStatus.paid, loc)
        check("...and that token opens this order", visitor().post(
            "/api/guest/order", json={"token": q["gt"][0]}).json()["order"]["id"] == o.id)
        check("the PayU buyer is emailed the link once", len(mails_to("payu-buyer@example.org")) == 1)
        check("still nobody is signed in", auth.COOKIE not in g.cookies)
    finally:
        os.environ["ASTRO_GATEWAY"] = "test"


# ---------------------------------------------------------------- 4. token + questions
def part4_token_and_questions() -> None:
    print("\n4. The order token and the questions")
    reset()
    mail.OUTBOX.clear()
    g = visitor()
    d = checkout(g, "asker@example.org").json()
    token = d["token"]
    oid = d["order"]["id"]
    check("the token is not the order id and cannot be derived from it",
          str(oid) != token and len(token) > 20 and "." in token)
    forged = gc.URLSafeTimedSerializer("another-secret", salt=gc.TOKEN_SALT).dumps({"o": oid})
    check("a token signed with another secret is refused (404 token)",
          visitor().post("/api/guest/order", json={"token": forged}).status_code == 404)
    check("a made-up token is refused", visitor().post(
        "/api/guest/order", json={"token": "abc.def.ghi"}).status_code == 404)
    member = signed_in("member@example.com")
    mo = member.post("/api/orders", json={"sku": "q10"}).json()["order"]["id"]
    with db_session() as db:
        member_order = db.get(Order, mo)
        member_token = gc.token_for(member_order)
    check("a signed token for a signed-in (non-guest) order opens nothing",
          visitor().post("/api/guest/order", json={"token": member_token}).status_code == 404)

    r = g.post("/api/guest/questions", json={"token": token, "questions": ["Will I travel?"]})
    check("questions before payment are refused (409 not_paid)", code(r) == "not_paid", r.text[:200])
    s = confirm(g, token).json()
    check("paid: 3 questions to type", s["paid"] and s["questions_left"] == 3 and s["chart"]["name"] == "Asha")

    # The account behind the order already has a conversation it must not leak into.
    with db_session() as db:
        uid = order(oid).user_id
        db.add(QuestionLog(user_id=uid, question="OTHER-CONVERSATION", answer="OTHER-ANSWER"))
        db.commit()
    r = g.post("/api/guest/questions", json={"token": token, "questions": ["x" * 1001]})
    check("a question over 1000 characters is refused", code(r) == "too_long")
    r = g.post("/api/guest/questions", json={"token": token, "questions": ["  ", ""]})
    check("empty questions are refused", code(r) == "no_questions")
    r = g.post("/api/guest/questions", json={"token": token, "lang": "en", "questions": [
        "When will my career improve?", "Will I marry this year?"]})
    s = r.json()
    check("two questions are queued; one left", r.status_code == 200 and s["questions_left"] == 1
          and [q["status"] for q in s["questions"]] == ["pending", "pending"], r.text[:300])
    with db_session() as db:
        jobs = list(db.execute(select(EmailedAnswerJob).where(EmailedAnswerJob.order_id == oid)).scalars())
    check("each is an emailed-answer job for this order, to the order's address, with the birth details",
          len(jobs) == 2 and all(j.email == "asker@example.org" and j.user_id == uid and j.birth_json
                                 for j in jobs) and email_balance(db_session(), uid) == 1)
    r = g.post("/api/guest/questions", json={"token": token, "questions": ["Third?", "Fourth?"]})
    s = r.json()
    check("the last question fills the order; extra ones are not taken",
          s["questions_left"] == 0 and len(s["questions"]) == 3 and email_balance(db_session(), uid) == 0)
    check("the birth details have left the order once all questions are in",
          "birth" not in json.loads(order(oid).guest_json) and s["chart"]["name"] == "Asha")
    r = g.post("/api/guest/questions", json={"token": token, "questions": ["Fifth?"]})
    check("more questions are refused (409 used)", code(r) == "used")

    CLAUDE["streams"].clear()
    done = [ea.run_next() for _ in range(3)]
    with db_session() as db:
        jobs = list(db.execute(select(EmailedAnswerJob).where(EmailedAnswerJob.order_id == oid)).scalars())
    check("the worker answers all three", all(done) and all(j.status == "done" for j in jobs),
          str([(j.status, j.error[:60]) for j in jobs]))
    prompts = json.dumps([s.get("messages") for s in CLAUDE["streams"]], ensure_ascii=False)
    check("written without the account's other conversations", "OTHER-CONVERSATION" not in prompts
          and len(CLAUDE["streams"]) == 3)
    sent = [m for m in mails_to("asker@example.org") if "Starter is paid" not in m[1]]
    check("each answer is emailed to the order's address", len(sent) == 3, str([m[1] for m in sent]))
    s = visitor().post("/api/guest/order", json={"token": token}).json()
    check("the order page shows each question as emailed, never the answer text",
          all(q["status"] == "done" and q["delivered"] for q in s["questions"])
          and "Claude's reading" not in json.dumps(s))


# ---------------------------------------------------------------- 5. rate limits
def part5_rate_limits() -> None:
    print("\n5. Rate limits")
    reset()
    ip = "198.51.100.250"
    codes = [code(checkout(visitor(ip), f"ip{i}@example.org")) for i in range(gc.PER_IP[0] + 1)]
    check(f"one address (IP) may open {gc.PER_IP[0]} guest payments an hour, then 429 rate",
          all(c == "" for c in codes[:-1]) and codes[-1] == "rate", str(codes))
    reset()
    codes = [code(checkout(visitor(), "same@example.org")) for _ in range(gc.PER_EMAIL[0] + 1)]
    check(f"one email may be used {gc.PER_EMAIL[0]} times an hour from any address, then 429 rate",
          all(c in ("", "refused") for c in codes[:-1]) and codes[-1] == "rate", str(codes))
    reset()
    v6 = [code(checkout(visitor(f"2001:db8::{i}"), f"v6-{i}@example.org")) for i in range(gc.PER_IP[0] + 1)]
    check("an IPv6 /64 counts as one address", v6[-1] == "rate", str(v6))
    reset()


# ---------------------------------------------------------------- 6. adoption
def part6_adoption() -> None:
    print("\n6. The first sign-in with that address adopts the order")
    reset()
    g = visitor()
    d = checkout(g, "later@example.org").json()
    confirm(g, d["token"])
    g.post("/api/guest/questions", json={"token": d["token"], "questions": ["Will I move abroad?"]})
    placeholder = order(d["order"]["id"]).user_id
    with db_session() as db:
        user, created = email_auth.sign_in(db, "later@example.org")
        check("an email-code sign-in lands in the same account, reported as a sign-up",
              user.id == placeholder and created and user.provider == "email"
              and user.provider_sub == "later@example.org")
        check("...with the welcome questions, once", balance(db, user.id) == billing.FREE_QUESTIONS)
        user2, created2 = email_auth.sign_in(db, "later@example.org")
        check("signing in again is an ordinary sign-in", user2.id == user.id and not created2
              and balance(db, user.id) == billing.FREE_QUESTIONS)

    g2 = visitor()
    d2 = checkout(g2, "googler@example.org").json()
    confirm(g2, d2["token"])
    g2.post("/api/guest/questions", json={"token": d2["token"], "questions": ["Is this a good year?"]})
    pid = order(d2["order"]["id"]).user_id
    c = signed_in("googler@example.org")          # dev sign-in = upsert_user, like Google
    me = c.get("/api/me").json()["user"]
    check("a Google (verified-email) sign-in adopts it: same account, welcome questions, the Starter",
          me["id"] == pid and me["credits"] == billing.FREE_QUESTIONS and me["email_credits"] == 2
          and me["starter"]["reason"] == "bought", str(me)[:300])
    hist = c.get("/api/history").json()["questions"]
    check("My questions shows the question entered on the order page",
          any(q["question"] == "Is this a good year?" and q.get("emailed") for q in hist), str(hist)[:200])
    check("My orders shows the order", any(o["id"] == d2["order"]["id"] for o in c.get("/api/orders").json()["orders"]))
    with db_session() as db:
        u = db.get(User, pid)
        check("the sign-up is recorded at adoption (source stamped, no longer the placeholder's)",
              u.signup_source not in (None, "guest_checkout") and u.provider == "dev")

    g3 = visitor()
    d3 = checkout(g3, "msuser@example.org").json()
    pid3 = order(d3["order"]["id"]).user_id
    with db_session() as db:
        u, _ = auth.upsert_user(db, "microsoft", {"sub": "ms-1", "email": "msuser@example.org",
                                                  "email_verified": True})
        check("a Microsoft sign-in does not adopt it (its email claim is not proof of the mailbox)",
              u.id != pid3 and db.get(User, pid3).provider == "guest")


# ---------------------------------------------------------------- 7. analytics, privacy, migration
def part7_events_privacy_migration() -> None:
    print("\n7. Analytics, privacy text, migration")
    with db_session() as db:
        names = [n for (n,) in db.execute(select(Event.name)).all()]
    check("guest_checkout_start and guest_checkout_paid are recorded by the server",
          "guest_checkout_start" in names and "guest_checkout_paid" in names, str(set(names)))
    check("both are known events with plain-words labels and in the app funnel",
          {"guest_checkout_start", "guest_checkout_paid"} <= analytics.EVENT_NAMES
          and all((n, "") in analytics.EVENT_LABELS for n in ("guest_checkout_start", "guest_checkout_paid"))
          and {"guest_checkout_start", "guest_checkout_paid"} <= {n for _l, n, _d in analytics.APP_FUNNEL})
    check("a guest placeholder is not counted as a sign-up", "guest_checkout" in analytics.NOT_SIGNUPS)
    html = visitor().get("/privacy").text
    check("the privacy policy says what a guest purchase keeps",
          "Buying without signing in" in html and "phone" in html)

    from alembic import command
    from alembic.config import Config
    from sqlalchemy import create_engine
    root = Path(__file__).resolve().parent.parent
    url = f"sqlite:///{Path(_tmp).as_posix()}/mig.db"
    cfg = Config(str(root / "alembic.ini"))
    cfg.set_main_option("script_location", str(root / "migrations"))
    cfg.set_main_option("sqlalchemy.url", url)
    app_url = os.environ["ASTRO_DATABASE_URL"]
    os.environ["ASTRO_DATABASE_URL"] = url
    try:
        command.upgrade(cfg, "head")
        eng = create_engine(url)
        ocols = {c["name"] for c in inspect(eng).get_columns("orders")}
        jcols = {c["name"] for c in inspect(eng).get_columns("emailed_answer_jobs")}
        check("migration up: orders.guest_* and emailed_answer_jobs.order_id",
              {"guest_email", "guest_phone", "guest_json"} <= ocols and "order_id" in jcols)
        eng.dispose()
        command.downgrade(cfg, "e7a1c3d5f9b2")
        eng = create_engine(url)
        ocols = {c["name"] for c in inspect(eng).get_columns("orders")}
        jcols = {c["name"] for c in inspect(eng).get_columns("emailed_answer_jobs")}
        check("migration down: the columns are gone", not ({"guest_email", "guest_phone", "guest_json"} & ocols)
              and "order_id" not in jcols)
        eng.dispose()
        command.upgrade(cfg, "head")
        eng = create_engine(url)
        check("and up again", "guest_email" in {c["name"] for c in inspect(eng).get_columns("orders")})
        eng.dispose()
    finally:
        os.environ["ASTRO_DATABASE_URL"] = app_url


def main() -> int:
    part1_new_address()
    part2_existing_account()
    part3_payment_paths()
    part4_token_and_questions()
    part5_rate_limits()
    part6_adoption()
    part7_events_privacy_migration()
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
