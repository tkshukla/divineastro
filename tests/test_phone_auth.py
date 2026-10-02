"""Phone sign-in by SMS code (DIVASTRO-102) — the third account path,
alongside OAuth and username/password. See app/phone_auth.py.

It ships disabled, so the first thing checked is that it really is off
without ASTRO_SMS_PROVIDER. Everything after runs on the `console` sender,
which keeps each code in ConsoleSender.OUTBOX for the test to read back.

No server needed (FastAPI's in-process TestClient).

    ~/.venvs/divineastro/bin/python -u -m tests.test_phone_auth
"""

from __future__ import annotations

import os
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

_tmp = tempfile.mkdtemp(prefix="astro_phoneauth_")
os.environ["ASTRO_DATABASE_URL"] = f"sqlite:///{Path(_tmp).as_posix()}/t.db"
os.environ["ASTRO_DEV_LOGIN"] = "1"
os.environ["ASTRO_COOKIE_SECURE"] = "0"
os.environ["ASTRO_GATEWAY"] = "test"
os.environ["ASTRO_ADMIN_EMAILS"] = "owner@divineastro.org"
os.environ.pop("ASTRO_SMS_PROVIDER", None)
os.environ.pop("ASTRO_SMS_COUNTRIES", None)

from fastapi import HTTPException  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import phone_auth  # noqa: E402
from app.db import User, session as db_session  # noqa: E402
from app.main import app  # noqa: E402

failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def provider_keys() -> list[str]:
    return [p["key"] for p in TestClient(app).get("/api/auth/providers").json()["providers"]]


def last_code(number: str) -> str:
    return next(c for n, c in reversed(phone_auth.ConsoleSender.OUTBOX) if n == number)


def start(client: TestClient, number: str):
    return client.post("/api/auth/phone/start", json={"number": number})


def verify(client: TestClient, number: str, code: str):
    return client.post("/api/auth/phone/verify", json={"number": number, "code": code})


def wrong(code: str) -> str:
    return f"{(int(code) + 1) % 1_000_000:06d}"


def main() -> int:
    print("\n1. Off by default: not advertised, not reachable")
    keys = provider_keys()
    check("'phone' is NOT advertised without ASTRO_SMS_PROVIDER", "phone" not in keys, str(keys))
    provs = TestClient(app).get("/api/auth/providers").json()["providers"]
    pw = next((p for p in provs if p["key"] == "password"), None)
    check("username/password IS advertised, flagged inline (no redirect)",
          bool(pw and pw.get("inline")), str(provs))
    r = start(TestClient(app), "9876543210")
    check("/api/auth/phone/start is a 404 while disabled", r.status_code == 404, str(r.status_code))
    r = verify(TestClient(app), "9876543210", "123456")
    check("/api/auth/phone/verify is a 404 while disabled", r.status_code == 404, str(r.status_code))

    print("\n2. The console sender is refused in production")
    os.environ["ASTRO_SMS_PROVIDER"] = "console"
    os.environ["ASTRO_COOKIE_SECURE"] = "1"
    check("console + ASTRO_COOKIE_SECURE=1 -> phone stays off (it would log codes)",
          "phone" not in provider_keys())
    os.environ["ASTRO_COOKIE_SECURE"] = "0"
    os.environ["ASTRO_SMS_PROVIDER"] = "msg91"
    check("msg91 without its authkey/template -> phone stays off", "phone" not in provider_keys())
    os.environ["ASTRO_SMS_PROVIDER"] = "console"
    keys = provider_keys()
    check("ASTRO_SMS_PROVIDER=console (dev) -> 'phone' is advertised", "phone" in keys, str(keys))

    print("\n3. Number validation and normalisation")
    for raw, want in [("9876543210", "+919876543210"), ("98765 43210", "+919876543210"),
                      ("098765-43210", "+919876543210"), ("919876543210", "+919876543210"),
                      ("+91 (98765) 43210", "+919876543210")]:
        try:
            got = phone_auth.normalise(raw)
        except HTTPException as exc:
            got = f"HTTP {exc.status_code}"
        check(f"{raw!r} -> {want}", got == want, got)
    for raw in ["12345", "5876543210", "98765432101", "abcdefghij", "", "+919876"]:
        r = start(TestClient(app), raw)
        check(f"{raw!r} is rejected with 400", r.status_code == 400, f"{r.status_code} {r.text[:120]}")
    r = start(TestClient(app), "+447700900123")
    check("a non-Indian number is refused (SMS-pumping guard)", r.status_code == 400,
          f"{r.status_code} {r.text[:120]}")
    check("mask() hides all but the last four digits",
          phone_auth.mask("+919876543210") == "+91 ••••••3210", phone_auth.mask("+919876543210"))

    print("\n4. Happy path: start -> verify creates an account and a session")
    phone_auth.reset_for_tests()
    number = "+919812345678"
    client = TestClient(app)
    r = start(client, "98123 45678")
    check("start -> 200", r.status_code == 200, f"{r.status_code} {r.text[:200]}")
    body = r.json()
    code = last_code(number)
    check("the response shows the number masked", body.get("number") == "+91 ••••••5678", str(body))
    check("the code is NOT in the response", code not in r.text)
    check("a cooldown is returned for the resend button", body.get("resend_after") == 30, str(body))
    pending = phone_auth._PENDING[number]
    check("only an HMAC of the code is held, never the code",
          code not in repr(pending) and len(pending.digest) == 64, repr(pending)[:80])
    r = verify(client, "9812345678", code)
    check("verify -> 200", r.status_code == 200, f"{r.status_code} {r.text[:200]}")
    data = r.json()
    check("a new account was created", data.get("created") is True, str(data))
    check("the signup bonus was granted", data["user"]["credits"] == 10, str(data["user"]))
    check("no email is attached", data["user"]["email"] == "", str(data["user"]))
    check("provider is 'phone'", data["user"]["provider"] == "phone", str(data["user"]))
    check("the verified number fills the phone field", data["user"]["phone"] == number, str(data["user"]))
    check("it displays as the masked number", data["user"]["login_label"] == "+91 ••••••5678",
          str(data["user"]))
    check("a session cookie was issued", "gd_session" in client.cookies)
    me = client.get("/api/me").json()
    check("/api/me resolves to this account", me["user"] and me["user"]["id"] == data["user"]["id"], str(me))
    uid = data["user"]["id"]
    r = verify(TestClient(app), number, code)
    check("the same code cannot be used twice", r.status_code == 400, f"{r.status_code} {r.text[:120]}")

    print("\n5. The same number signs in to the SAME account, with no second bonus")
    fresh = TestClient(app)
    start(fresh, "+91 98123 45678")
    r = verify(fresh, number, last_code(number))
    check("second sign-in -> 200", r.status_code == 200, f"{r.status_code} {r.text[:200]}")
    check("same user id", r.json()["user"]["id"] == uid, str(r.json()["user"]))
    check("created is False", r.json()["created"] is False)
    check("credits unchanged (no second bonus)", r.json()["user"]["credits"] == 10)

    print("\n6. A wrong code, then the right one")
    phone_auth.reset_for_tests()
    n2 = "+919700000001"
    c = TestClient(app)
    start(c, n2)
    code = last_code(n2)
    r = verify(c, n2, wrong(code))
    check("wrong code -> 400", r.status_code == 400, f"{r.status_code} {r.text[:120]}")
    check("says how many tries are left", "4 tries left" in r.json()["detail"], r.json()["detail"])
    r = verify(c, n2, "12")
    check("a code of the wrong length -> 400 without using a try", r.status_code == 400
          and phone_auth._PENDING[n2].attempts == 1, f"attempts={phone_auth._PENDING[n2].attempts}")
    r = verify(c, n2, code)
    check("the right code still works after one mistake", r.status_code == 200, f"{r.status_code} {r.text[:120]}")

    print("\n7. An expired code is refused")
    n3 = "+919700000002"
    start(c, n3)
    code = last_code(n3)
    phone_auth._PENDING[n3].expires_at = time.monotonic() - 1
    r = verify(c, n3, code)
    check("expired -> 400", r.status_code == 400, f"{r.status_code} {r.text[:120]}")
    check("the message says to ask for a new one", "expired" in r.json()["detail"].lower(), r.json()["detail"])

    print("\n8. Attempt limit: the code is burned after 5 wrong tries")
    n4 = "+919700000003"
    start(c, n4)
    code = last_code(n4)
    statuses = [verify(c, n4, wrong(code)).status_code for _ in range(phone_auth.OTP_MAX_ATTEMPTS)]
    check("four 400s then a 429", statuses == [400] * 4 + [429], str(statuses))
    r = verify(c, n4, code)
    check("the right code no longer works once burned", r.status_code == 400, f"{r.status_code} {r.text[:120]}")

    print("\n9. Send rate limits: cooldown, per number, per IP")
    phone_auth.reset_for_tests()
    n5 = "+919700000004"
    r1, r2 = start(c, n5), start(c, n5)
    check("an immediate resend is refused (cooldown)", r1.status_code == 200 and r2.status_code == 429,
          f"{r1.status_code} {r2.status_code}")
    statuses = [r1.status_code]
    for _ in range(3):
        phone_auth._PENDING[n5].sent_at -= phone_auth.RESEND_COOLDOWN_SECONDS + 1
        statuses.append(start(c, n5).status_code)
    check("3 sends per number per 15 minutes, then 429", statuses == [200, 200, 200, 429], str(statuses))
    phone_auth.reset_for_tests()
    statuses = [start(c, f"+91970000{i:04d}").status_code for i in range(11)]
    check("10 sends per IP per hour, then 429 — even to different numbers",
          statuses == [200] * 10 + [429], str(statuses))

    print("\n10. Wrong codes are limited per IP too, not only per code")
    phone_auth.reset_for_tests()
    hits = []
    for i in range(5):
        n = f"+91960000{i:04d}"
        start(c, n)
        code = last_code(n)
        hits += [verify(c, n, wrong(code)).status_code for _ in range(4)]
    n = "+919600009999"
    start(c, n)
    r = verify(c, n, last_code(n))
    check("after 20 wrong codes across numbers, even a right one is throttled",
          r.status_code == 429, f"{r.status_code} {r.text[:120]}")

    print("\n11. A blocked phone account is refused")
    phone_auth.reset_for_tests()
    admin = TestClient(app)
    admin.post("/api/auth/dev", json={"email": "owner@divineastro.org"})
    blk = admin.post(f"/api/admin/users/{uid}/block", json={"blocked": True, "reason": "test"})
    check("admin can block a phone user", blk.status_code == 200, f"{blk.status_code} {blk.text[:120]}")
    c2 = TestClient(app)
    start(c2, number)
    r = verify(c2, number, last_code(number))
    check("blocked -> 403", r.status_code == 403, f"{r.status_code} {r.text[:120]}")

    print("\n12. Admin users list shows phone accounts sensibly")
    users = admin.get("/api/admin/users", params={"q": "9812345678"}).json()["users"]
    check("searching by number finds the phone account", any(u["id"] == uid for u in users), str(users)[:200])
    row = next((u for u in users if u["id"] == uid), {})
    check("its label is the masked number", row.get("login_label") == "+91 ••••••5678", str(row)[:200])

    print("\n13. A phone-only customer recorded by an admin is adopted on first phone sign-in")
    db = db_session()
    try:
        manual = User(email="", name="Walk-in", phone="09811122233", provider="manual",
                      provider_sub="manual:09811122233", signup_source="manual")
        db.add(manual)
        db.commit()
        manual_id = manual.id
    finally:
        db.close()
    c3 = TestClient(app)
    n6 = "+919811122233"
    start(c3, "9811122233")
    r = verify(c3, n6, last_code(n6))
    check("verify -> 200", r.status_code == 200, f"{r.status_code} {r.text[:120]}")
    check("lands in the admin-recorded account", r.json()["user"]["id"] == manual_id, str(r.json()["user"]))
    check("it is now a phone account", r.json()["user"]["provider"] == "phone")
    check("the welcome bonus it never had is granted once", r.json()["user"]["credits"] == 10,
          str(r.json()["user"]["credits"]))

    print("\n14. The MSG91 sender puts nothing in the URL (httpx logs URLs)")
    calls = []

    class _Resp:
        status_code = 200

        @staticmethod
        def json():
            return {"type": "success", "message": "req-1"}

    real_post = phone_auth.httpx.post
    phone_auth.httpx.post = lambda url, **kw: calls.append((url, kw)) or _Resp()
    try:
        ok = phone_auth.Msg91Sender("AUTHKEY-PLACEHOLDER", "TEMPLATE-PLACEHOLDER").send_code(
            "+919812345678", "424242")
    finally:
        phone_auth.httpx.post = real_post
    url, kw = calls[0]
    check("success is reported", ok is True)
    check("no query string on the URL", "?" not in url and "424242" not in url, url)
    check("the code and number travel in the JSON body",
          kw["json"]["recipients"] == [{"mobiles": "919812345678", "otp": "424242"}], str(kw["json"]))
    check("authkey is a header", kw["headers"]["authkey"] == "AUTHKEY-PLACEHOLDER")

    os.environ.pop("ASTRO_SMS_PROVIDER", None)
    check("unsetting ASTRO_SMS_PROVIDER turns it straight back off", "phone" not in provider_keys())

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("phone auth: all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
