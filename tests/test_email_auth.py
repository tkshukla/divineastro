"""Email sign-in by one-time code (DIVASTRO-104) — the free alternative to
phone OTP. See app/email_auth.py.

It is on only when mail is configured, so the first thing checked is that it
is off without ASTRO_SMTP_HOST. Everything after runs on mail.py's `console`
transport, which keeps each message in mail.OUTBOX for the test to read back.

No server needed (FastAPI's in-process TestClient).

    ~/.venvs/divineastro/bin/python -u -m tests.test_email_auth
"""

from __future__ import annotations

import os
import re
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

_tmp = tempfile.mkdtemp(prefix="astro_emailauth_")
os.environ["ASTRO_DATABASE_URL"] = f"sqlite:///{Path(_tmp).as_posix()}/t.db"
os.environ["ASTRO_DEV_LOGIN"] = "1"
os.environ["ASTRO_COOKIE_SECURE"] = "0"
os.environ["ASTRO_GATEWAY"] = "test"
os.environ["ASTRO_ADMIN_EMAILS"] = "owner@divineastro.org"
for _k in ("ASTRO_SMTP_HOST", "ASTRO_EMAIL_DAILY_CAP", "ASTRO_SMS_PROVIDER"):
    os.environ.pop(_k, None)

from fastapi import HTTPException  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import auth, email_auth, mail  # noqa: E402
from app.db import User, session as db_session  # noqa: E402
from app.main import app  # noqa: E402

failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def providers() -> list[dict]:
    return TestClient(app).get("/api/auth/providers").json()["providers"]


def last_code(addr: str) -> str:
    to, _subject, body, _html = next(m for m in reversed(mail.OUTBOX) if m[0] == [addr])
    return re.search(r"\b(\d{6})\b", body).group(1)


def start(client: TestClient, addr: str, lang: str = "en"):
    return client.post("/api/auth/email/start", json={"email": addr, "lang": lang})


def verify(client: TestClient, addr: str, code: str, lang: str = "en"):
    return client.post("/api/auth/email/verify", json={"email": addr, "code": code, "lang": lang})


def wrong(code: str) -> str:
    return f"{(int(code) + 1) % 1_000_000:06d}"


def main() -> int:
    print("\n1. Off without mail: not advertised, not reachable")
    keys = [p["key"] for p in providers()]
    check("'email' is NOT advertised without ASTRO_SMTP_HOST", "email" not in keys, str(keys))
    r = start(TestClient(app), "someone@gmail.com")
    check("/api/auth/email/start is a 404 while disabled", r.status_code == 404, str(r.status_code))
    r = verify(TestClient(app), "someone@gmail.com", "123456")
    check("/api/auth/email/verify is a 404 while disabled", r.status_code == 404, str(r.status_code))

    print("\n2. The console transport is refused in production; SMTP turns it on")
    os.environ["ASTRO_SMTP_HOST"] = "console"
    os.environ["ASTRO_COOKIE_SECURE"] = "1"
    check("console + ASTRO_COOKIE_SECURE=1 -> email stays off (it would log codes)",
          "email" not in [p["key"] for p in providers()])
    check("...and mail.send() refuses to 'send' too",
          mail.send(["x@gmail.com"], "s", "b") is False and not mail.OUTBOX)
    os.environ["ASTRO_COOKIE_SECURE"] = "0"
    os.environ["ASTRO_SMTP_HOST"] = "smtp-relay.brevo.com"
    check("a real SMTP host -> 'email' is advertised", "email" in [p["key"] for p in providers()])
    os.environ["ASTRO_SMTP_HOST"] = "console"
    provs = providers()
    em = next((p for p in provs if p["key"] == "email"), None)
    check("ASTRO_SMTP_HOST=console (dev) -> 'email' advertised, flagged inline",
          bool(em and em.get("inline")), str(provs))

    print("\n3. Address validation")
    for raw, want in [("Ramesh.K@Gmail.com", "ramesh.k@gmail.com"),
                      ("  priya+astro@yahoo.co.in ", "priya+astro@yahoo.co.in"),
                      ("a@b.io", "a@b.io")]:
        try:
            got = email_auth.normalise(raw)
        except HTTPException as exc:
            got = f"HTTP {exc.status_code}"
        check(f"{raw!r} -> {want}", got == want, got)
    for raw in ["", "plainaddress", "@gmail.com", "ram@", "ram@@gmail.com", "ram@gmail",
                "ram@.com", "ram..k@gmail.com", ".ram@gmail.com", "ram @gmail.com",
                "ram@gmail..com", "ram@-gmail.com", "ram@gmail.c", "ram@site.test",
                "ram@localhost", "ram@192.168.0.1", "a" * 120 + "@gmail.com",
                "<ram@gmail.com>", "ram@gmail.com,sita@gmail.com"]:
        r = start(TestClient(app), raw)
        check(f"{raw[:40]!r} is rejected with 400", r.status_code == 400,
              f"{r.status_code} {r.text[:100]}")
    r = start(TestClient(app), "ramesh@gmial.com")
    check("a mistyped Gmail domain is caught before spending a send",
          r.status_code == 400 and "ramesh@gmail.com" in r.json()["detail"], r.text[:160])
    r = start(TestClient(app), "ramesh@gmial.com", lang="hi")
    check("...and the message comes back in Hindi when asked",
          "क्या आपका मतलब" in r.json()["detail"], r.json()["detail"])
    check("nothing was sent for any rejected address", not mail.OUTBOX, str(len(mail.OUTBOX)))

    print("\n4. Happy path: start -> verify creates an account, a session and one bonus")
    email_auth.reset_for_tests()
    addr = "new.person@gmail.com"
    client = TestClient(app)
    r = start(client, "New.Person@Gmail.com ")
    check("start -> 200", r.status_code == 200, f"{r.status_code} {r.text[:200]}")
    body = r.json()
    code = last_code(addr)
    check("the response echoes the normalised address", body.get("email") == addr, str(body))
    check("the code is NOT in the response", code not in r.text)
    check("a cooldown is returned for the resend button", body.get("resend_after") == 30, str(body))
    pending = email_auth._PENDING[addr]
    check("only an HMAC of the code is held, never the code",
          code not in repr(pending) and len(pending.digest) == 64, repr(pending)[:80])
    to, subject, text, html = mail.OUTBOX[-1]
    check("one email, to that address only", to == [addr], str(to))
    check("the subject is bilingual and does not carry the code",
          "sign-in code" in subject and "कोड" in subject and code not in subject, subject)
    check("plain text says 10 minutes and 'ignore', in English and Hindi",
          "10 minutes" in text and "ignore" in text and "10 मिनट" in text, text[:200])
    check("an HTML part shows the code prominently", bool(html) and code in html
          and "32px" in html, (html or "")[:120])
    r = verify(client, "NEW.PERSON@gmail.com", code)
    check("verify -> 200", r.status_code == 200, f"{r.status_code} {r.text[:200]}")
    data = r.json()
    user = data["user"]
    check("a new account was created", data.get("created") is True, str(data))
    check("the signup bonus was granted once", user["credits"] == 10, str(user))
    check("provider is 'email'", user["provider"] == "email", str(user))
    check("the verified address is the account's email", user["email"] == addr, str(user))
    check("it is labelled by its address", user["login_label"] == addr, str(user))
    check("a session cookie was issued", "gd_session" in client.cookies)
    me = client.get("/api/me").json()
    check("/api/me resolves to this account", me["user"] and me["user"]["id"] == user["id"], str(me))
    uid = user["id"]
    r = verify(TestClient(app), addr, code)
    check("the same code cannot be used twice", r.status_code == 400, f"{r.status_code} {r.text[:120]}")

    print("\n5. The same address signs in to the SAME account, with no second bonus")
    fresh = TestClient(app)
    start(fresh, addr)
    r = verify(fresh, addr, last_code(addr))
    check("second sign-in -> 200", r.status_code == 200, f"{r.status_code} {r.text[:200]}")
    check("same user id, created False", r.json()["user"]["id"] == uid and r.json()["created"] is False)
    check("credits unchanged (no second bonus)", r.json()["user"]["credits"] == 10)
    db = db_session()
    try:
        n = db.query(User).filter(User.email == addr).count()
    finally:
        db.close()
    check("exactly one account carries the address", n == 1, str(n))

    print("\n6. Wrong, malformed and expired codes")
    email_auth.reset_for_tests()
    a2 = "wrong.code@gmail.com"
    c = TestClient(app)
    start(c, a2)
    code = last_code(a2)
    r = verify(c, a2, wrong(code))
    check("wrong code -> 400", r.status_code == 400, f"{r.status_code} {r.text[:120]}")
    check("says how many tries are left", "4 tries left" in r.json()["detail"], r.json()["detail"])
    r = verify(c, a2, "12")
    check("a code of the wrong length -> 400 without using a try",
          r.status_code == 400 and email_auth._PENDING[a2].attempts == 1,
          f"attempts={email_auth._PENDING[a2].attempts}")
    r = verify(c, a2, wrong(code), lang="hi")
    check("the wrong-code message is in Hindi when asked", "सही नहीं" in r.json()["detail"],
          r.json()["detail"])
    r = verify(c, a2, code)
    check("the right code still works after mistakes", r.status_code == 200, f"{r.status_code} {r.text[:120]}")
    a3 = "expired.code@gmail.com"
    start(c, a3)
    code = last_code(a3)
    email_auth._PENDING[a3].expires_at = time.monotonic() - 1
    r = verify(c, a3, code)
    check("expired -> 400, 'ask for a new one'", r.status_code == 400
          and "expired" in r.json()["detail"].lower(), f"{r.status_code} {r.text[:120]}")
    r = verify(c, "never.sent@gmail.com", "123456")
    check("a code for an address never sent one -> 400", r.status_code == 400, str(r.status_code))

    print("\n7. Attempt limit: the code is burned after 5 wrong tries")
    a4 = "burn.code@gmail.com"
    start(c, a4)
    code = last_code(a4)
    statuses = [verify(c, a4, wrong(code)).status_code for _ in range(email_auth.OTP_MAX_ATTEMPTS)]
    check("four 400s then a 429", statuses == [400] * 4 + [429], str(statuses))
    r = verify(c, a4, code)
    check("the right code no longer works once burned", r.status_code == 400, f"{r.status_code} {r.text[:120]}")

    print("\n8. Send rate limits: cooldown, per address, per IP")
    email_auth.reset_for_tests()
    a5 = "rate.limit@gmail.com"
    r1, r2 = start(c, a5), start(c, a5)
    check("an immediate resend is refused (cooldown)", r1.status_code == 200 and r2.status_code == 429,
          f"{r1.status_code} {r2.status_code}")
    statuses = [r1.status_code]
    for _ in range(3):
        email_auth._PENDING[a5].sent_at -= email_auth.RESEND_COOLDOWN_SECONDS + 1
        statuses.append(start(c, a5).status_code)
    check("3 sends per address per 15 minutes, then 429", statuses == [200, 200, 200, 429], str(statuses))
    email_auth.reset_for_tests()
    statuses = [start(c, f"ip.limit{i}@gmail.com").status_code for i in range(11)]
    check("10 sends per IP per hour, then 429 — even to different addresses",
          statuses == [200] * 10 + [429], str(statuses))

    print("\n9. Wrong codes are limited per IP too, not only per code")
    email_auth.reset_for_tests()
    for i in range(5):
        a = f"spray{i}@gmail.com"
        start(c, a)
        code = last_code(a)
        for _ in range(4):
            verify(c, a, wrong(code))
    a = "spray.last@gmail.com"
    start(c, a)
    r = verify(c, a, last_code(a))
    check("after 20 wrong codes across addresses, even a right one is throttled",
          r.status_code == 429, f"{r.status_code} {r.text[:120]}")

    print("\n10. The global daily cap protects the free mail quota")
    email_auth.reset_for_tests()
    os.environ["ASTRO_EMAIL_DAILY_CAP"] = "3"
    statuses = []
    for i in range(3):
        # A different IP each time, so only the global cap can be what stops it.
        email_auth._BOOK.sends_by_ip.clear()
        statuses.append(start(c, f"cap{i}@gmail.com").status_code)
    sent_before = len(mail.OUTBOX)
    r = start(c, "cap.over@gmail.com")
    check("3 sends allowed under a cap of 3", statuses == [200] * 3, str(statuses))
    check("the 4th is 503 'busy', pointing to Google / username",
          r.status_code == 503 and "Google" in r.json()["detail"]
          and "username" in r.json()["detail"], f"{r.status_code} {r.text[:160]}")
    check("...and nothing was sent", len(mail.OUTBOX) == sent_before)
    r = start(c, "cap.over@gmail.com", lang="hi")
    check("the busy message is in Hindi when asked", "व्यस्त" in r.json()["detail"], r.json()["detail"])
    os.environ.pop("ASTRO_EMAIL_DAILY_CAP")
    check("the default cap is 250", email_auth.daily_cap() == 250, str(email_auth.daily_cap()))
    os.environ["ASTRO_EMAIL_DAILY_CAP"] = "lots"
    check("a junk cap value falls back to the default", email_auth.daily_cap() == 250)
    os.environ.pop("ASTRO_EMAIL_DAILY_CAP")

    print("\n11. A failing mail transport is a 502, not a silent success")
    email_auth.reset_for_tests()
    real_send = mail.send
    mail.send = lambda *a, **kw: False
    try:
        r = start(c, "smtp.down@gmail.com")
    finally:
        mail.send = real_send
    check("send failure -> 502", r.status_code == 502, f"{r.status_code} {r.text[:120]}")
    check("no pending code is left behind", "smtp.down@gmail.com" not in email_auth._PENDING)

    print("\n12. Linking: an email code on a Google account's address signs in to THAT account")
    email_auth.reset_for_tests()
    gaddr = "google.user@gmail.com"
    db = db_session()
    try:
        guser, created = auth.upsert_user(db, "google", {
            "sub": "google-sub-123", "email": "Google.User@gmail.com", "email_verified": True,
            "name": "Google User"})
        gid = guser.id
    finally:
        db.close()
    check("the Google account exists with its bonus", created)
    gc = TestClient(app)
    start(gc, gaddr)
    r = verify(gc, gaddr, last_code(gaddr))
    check("verify -> 200", r.status_code == 200, f"{r.status_code} {r.text[:120]}")
    u = r.json()["user"]
    check("lands in the Google account, not a new one",
          u["id"] == gid and r.json()["created"] is False, str(u))
    check("no second bonus", u["credits"] == 10, str(u["credits"]))
    check("it is still a Google account (Google sign-in by sub keeps working)",
          u["provider"] == "google", u["provider"])
    db = db_session()
    try:
        g2, created2 = auth.upsert_user(db, "google", {
            "sub": "google-sub-123", "email": gaddr, "email_verified": True})
        same = g2.id == gid and not created2
        n = db.query(User).filter(User.email == gaddr).count()
    finally:
        db.close()
    check("Google sign-in afterwards is the same account", same)
    check("still exactly one account with that address", n == 1, str(n))

    print("\n13. The other direction: email first, Google later -> one account")
    db = db_session()
    try:
        g3, created3 = auth.upsert_user(db, "google", {
            "sub": "google-sub-new-person", "email": addr, "email_verified": True})
        ok = g3.id == uid and not created3
        n = db.query(User).filter(User.email == addr).count()
    finally:
        db.close()
    check("a Google sign-in on the email account's address lands in it", ok)
    check("no duplicate account", n == 1, str(n))

    print("\n14. Not linked: Microsoft (unverifiable email claim) and admin accounts")
    db = db_session()
    try:
        ms, _ = auth.upsert_user(db, "microsoft", {
            "sub": "ms-sub-1", "email": "ms.only@outlook.com", "email_verified": True})
        ms_id = ms.id
    finally:
        db.close()
    mc = TestClient(app)
    start(mc, "ms.only@outlook.com")
    r = verify(mc, "ms.only@outlook.com", last_code("ms.only@outlook.com"))
    check("an email code does NOT open a Microsoft account on the same address",
          r.status_code == 200 and r.json()["user"]["id"] != ms_id
          and r.json()["user"]["provider"] == "email", r.text[:160])
    admin = TestClient(app)
    admin.post("/api/auth/dev", json={"email": "owner@divineastro.org"})
    check("the owner's account is an admin", admin.get("/api/me").json()["user"]["is_admin"])
    start(mc, "owner@divineastro.org")
    r = verify(mc, "owner@divineastro.org", last_code("owner@divineastro.org"))
    check("an admin account cannot be signed in to by email code", r.status_code == 403,
          f"{r.status_code} {r.text[:120]}")
    check("...and no session was issued", "gd_session" not in mc.cookies
          or mc.get("/api/me").json()["user"]["email"] != "owner@divineastro.org")

    print("\n15. An admin-recorded email customer is adopted, bonus exactly once")
    db = db_session()
    try:
        manual = User(email="walkin@gmail.com", name="Walk-in", provider="manual",
                      provider_sub="manual:walkin@gmail.com", signup_source="manual")
        db.add(manual)
        db.commit()
        manual_id = manual.id
    finally:
        db.close()
    wc = TestClient(app)
    start(wc, "walkin@gmail.com")
    r = verify(wc, "walkin@gmail.com", last_code("walkin@gmail.com"))
    check("lands in the admin-recorded account", r.json()["user"]["id"] == manual_id, r.text[:160])
    check("it is now an email account", r.json()["user"]["provider"] == "email")
    check("the welcome bonus is granted once", r.json()["user"]["credits"] == 10,
          str(r.json()["user"]["credits"]))

    print("\n16. Blocked accounts and the admin view")
    blk = admin.post(f"/api/admin/users/{uid}/block", json={"blocked": True, "reason": "test"})
    check("admin can block an email user", blk.status_code == 200, f"{blk.status_code} {blk.text[:120]}")
    bc = TestClient(app)
    start(bc, addr)
    r = verify(bc, addr, last_code(addr))
    check("blocked -> 403", r.status_code == 403, f"{r.status_code} {r.text[:120]}")
    users = admin.get("/api/admin/users", params={"q": "new.person"}).json()["users"]
    row = next((u for u in users if u["id"] == uid), {})
    check("the admin list finds it and shows the full address",
          row.get("login_label") == addr and row.get("email") == addr, str(row)[:200])

    print("\n17. Codes never reach the production log path")
    email_auth.reset_for_tests()
    import logging

    seen: list[str] = []

    class _Grab(logging.Handler):
        def emit(self, record):
            seen.append(record.getMessage())

    grab = _Grab()
    logging.getLogger().addHandler(grab)
    os.environ["ASTRO_SMTP_HOST"] = "smtp.invalid-host.example"
    os.environ["ASTRO_SMTP_PORT"] = "1"
    try:
        r = start(TestClient(app), "log.check@gmail.com")
    finally:
        logging.getLogger().removeHandler(grab)
        os.environ["ASTRO_SMTP_HOST"] = "console"
        os.environ.pop("ASTRO_SMTP_PORT")
    check("a real SMTP failure -> 502", r.status_code == 502, str(r.status_code))
    check("no six-digit number in any log line from the SMTP path",
          not any(re.search(r"\b\d{6}\b", m) for m in seen), str(seen)[:200])

    os.environ.pop("ASTRO_SMTP_HOST", None)
    check("unsetting ASTRO_SMTP_HOST turns it straight back off",
          "email" not in [p["key"] for p in providers()])

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("email auth: all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
