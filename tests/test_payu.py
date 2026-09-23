"""PayU: the hash-signed hosted-checkout flow, end to end.

Why this exists: PayU's classic checkout is unlike every other gateway wired
into app/gateways.py — the browser leaves the site with a real form POST and
PayU brings it back with ANOTHER real POST (not a webhook fetch, not a signed
query string), so /api/payu/return is a route type nothing else here has. The
one thing that must never happen is granting credit on an unsigned or
tampered return; that's what most of this file actually checks.

The hash formula itself (SHA-512, five empty udf slots, six pipes before the
salt) is taken from docs.payu.in's own "Generate Hash — Merchant Hosted"
page, not reproduced from memory. This test hard-codes it independently of
app/gateways.py's implementation, the same way test_matching.py pins the
scoring tables — if the two ever disagree, that is the bug this test exists
to catch, not something to "fix" by making the test match the code.

No server needed (FastAPI's in-process client). Needs its own env, set
BEFORE app.main is imported — PayUGateway reads PAYU_* at construction time,
same as every other gateway adapter here:

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.test_payu
"""

from __future__ import annotations

import hashlib
import os
import random
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

_tmp = tempfile.mkdtemp(prefix="astro_payutest_")
os.environ["ASTRO_DATABASE_URL"] = f"sqlite:///{Path(_tmp).as_posix()}/t.db"
os.environ["ASTRO_DEV_LOGIN"] = "1"
os.environ["ASTRO_COOKIE_SECURE"] = "0"
os.environ["ASTRO_GATEWAY"] = "payu"
os.environ["PAYU_MERCHANT_KEY"] = "gdtestkey"
os.environ["PAYU_SALT"] = "gdtestsalt123456"
os.environ["PAYU_SANDBOX"] = "1"
os.environ["PAYU_SURL"] = "https://divineastro.org/api/payu/return"
os.environ["PAYU_FURL"] = "https://divineastro.org/api/payu/return"

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

MERCHANT_KEY = os.environ["PAYU_MERCHANT_KEY"]
SALT = os.environ["PAYU_SALT"]
failures: list[str] = []
client = TestClient(app, raise_server_exceptions=False)


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def reverse_hash(status: str, productinfo: str, firstname: str, email: str,
                  amount: str, txnid: str, salt: str = SALT, key: str = MERCHANT_KEY) -> str:
    """Transcribed literally from docs.payu.in's reverse-hash sequence:

        SALT|status||||||udf5|udf4|udf3|udf2|udf1|email|firstname|productinfo|amount|txnid|key

    udf1..udf10 are always empty here (create() in gateways.py never
    populates them), but every one of the 10 slots is still spelled out by
    name below so this can't silently drop a field — which is exactly how
    the real bug shipped: gateways.py's first version had 5 empty slots
    instead of 10, this test used the SAME wrong count independently
    (copied the assumption, not just the code), and both sides agreed with
    each other while disagreeing with PayU. It surfaced only when a real
    payment succeeded on PayU's side and still never matched here — the
    scenario check 3 below exists specifically to catch again.
    """
    udf10 = udf9 = udf8 = udf7 = udf6 = udf5 = udf4 = udf3 = udf2 = udf1 = ""
    fields = [salt, status, udf10, udf9, udf8, udf7, udf6, udf5, udf4, udf3, udf2, udf1,
              email, firstname, productinfo, amount, txnid, key]
    return hashlib.sha512("|".join(fields).encode()).hexdigest()


def sign_in() -> tuple[TestClient, str]:
    email = f"payu{random.randint(10000, 99999)}@example.com"
    r = client.post("/api/auth/dev", json={"email": email})
    r.raise_for_status()
    return client, email


def credits() -> int:
    return client.get("/api/me").json()["user"]["credits"]


def main() -> int:
    print("\n1. The active gateway is PayU, configured")
    prods = client.get("/api/products").json()
    pay = prods["payment"]
    check("active gateway is payu", pay["gateway"] == "payu", pay["gateway"])
    check("marked live (a real gateway, not the test stub)", pay["live"] is True)

    print("\n2. Buying q10 produces a PayU hosted-checkout form, correctly hashed")
    sign_in()
    start = credits()
    r = client.post("/api/orders", json={"sku": "q10"})
    check("HTTP 200", r.status_code == 200, f"{r.status_code} {r.text[:200]}")
    data = r.json()
    order_id = data["order"]["id"]
    c = data["checkout"]
    check("mode is payu", c.get("mode") == "payu", str(c.get("mode")))
    check("posts to the SANDBOX endpoint (PAYU_SANDBOX=1)",
          c.get("action") == "https://test.payu.in/_payment", str(c.get("action")))
    f = c["fields"]
    check("all required hosted-checkout fields are present",
          all(f.get(k) for k in ("key", "txnid", "amount", "productinfo", "firstname", "email", "hash")),
          str(f))
    check("surl/furl point at our own return route", f.get("surl", "").endswith("/api/payu/return"))

    expected_fwd = hashlib.sha512(
        f"{MERCHANT_KEY}|{f['txnid']}|{f['amount']}|{f['productinfo']}|{f['firstname']}|{f['email']}"
        f"|||||||||||{SALT}".encode()
    ).hexdigest()
    check("the request hash matches PayU's own documented formula, independently recomputed",
          f["hash"] == expected_fwd)

    print("\n3. A validly signed return grants credit exactly once")
    good_hash = reverse_hash("success", f["productinfo"], f["firstname"], f["email"], f["amount"], f["txnid"])
    r1 = client.post("/api/payu/return", data={
        "txnid": f["txnid"], "status": "success", "amount": f["amount"],
        "productinfo": f["productinfo"], "firstname": f["firstname"], "email": f["email"],
        "hash": good_hash, "mihpayid": "test_mihpay_1",
    }, follow_redirects=False)
    check("redirects (303) back to the site", r1.status_code == 303, str(r1.status_code))
    loc = r1.headers.get("location", "")
    check("redirect says payu=ok with the order id", f"payu=ok" in loc and f"order={order_id}" in loc, loc)
    check("10 credits were actually granted", credits() == start + 10, f"{start} -> {credits()}")

    print("\n4. Replaying the same valid return must not grant a second time")
    r2 = client.post("/api/payu/return", data={
        "txnid": f["txnid"], "status": "success", "amount": f["amount"],
        "productinfo": f["productinfo"], "firstname": f["firstname"], "email": f["email"],
        "hash": good_hash, "mihpayid": "test_mihpay_1",
    }, follow_redirects=False)
    check("still redirects cleanly, no 500", r2.status_code == 303, str(r2.status_code))
    check("credits were not granted twice", credits() == start + 10, f"expected {start + 10}, got {credits()}")

    print("\n5. A tampered or unsigned return must never grant credit")
    sign_in()
    start2 = credits()
    r3 = client.post("/api/orders", json={"sku": "q10"})
    f3 = r3.json()["checkout"]["fields"]
    order3_id = r3.json()["order"]["id"]

    tampered = client.post("/api/payu/return", data={
        "txnid": f3["txnid"], "status": "success", "amount": "1.00",   # amount changed after hashing
        "productinfo": f3["productinfo"], "firstname": f3["firstname"], "email": f3["email"],
        "hash": reverse_hash("success", f3["productinfo"], f3["firstname"], f3["email"], f3["amount"], f3["txnid"]),
    }, follow_redirects=False)
    check("a hash computed for a different amount is rejected",
          "payu=failed" in tampered.headers.get("location", ""), tampered.headers.get("location", ""))
    check("no credit granted on the tampered attempt", credits() == start2, f"{start2} -> {credits()}")

    junk = client.post("/api/payu/return", data={
        "txnid": f3["txnid"], "status": "success", "amount": f3["amount"],
        "productinfo": f3["productinfo"], "firstname": f3["firstname"], "email": f3["email"],
        "hash": "0" * 128,
    }, follow_redirects=False)
    check("a plain wrong hash is rejected", "payu=failed" in junk.headers.get("location", ""))
    check("no credit granted on the wrong-hash attempt", credits() == start2, f"{start2} -> {credits()}")

    print("\n6. A genuine failure return (correct hash, status=failure) must not grant")
    fail_hash = reverse_hash("failure", f3["productinfo"], f3["firstname"], f3["email"], f3["amount"], f3["txnid"])
    r4 = client.post("/api/payu/return", data={
        "txnid": f3["txnid"], "status": "failure", "amount": f3["amount"],
        "productinfo": f3["productinfo"], "firstname": f3["firstname"], "email": f3["email"],
        "hash": fail_hash,
    }, follow_redirects=False)
    check("status=failure with a correct hash still does not grant",
          "payu=failed" in r4.headers.get("location", ""))
    check("credits unchanged", credits() == start2)

    print("\n7. A malformed/unknown txnid never 500s")
    r5 = client.post("/api/payu/return", data={"txnid": "no-such-order", "status": "success", "hash": "x"},
                      follow_redirects=False)
    check("unknown order -> clean redirect, not a 500", r5.status_code == 303, str(r5.status_code))

    print("\n8. The webhook path is deliberately inert until its JSON shape is confirmed")
    r6 = client.post("/api/webhooks/payment", content=b'{"status":"success"}',
                      headers={"Content-Type": "application/json"})
    # parse_webhook always returns unverified for PayU (see the gateway class
    # docstring), which the shared webhook handler reports as a bad signature —
    # a clean 400, never a 500, and never a grant.
    check("webhook call is refused cleanly (400), not a 500 and not a grant",
          r6.status_code == 400, f"{r6.status_code} {r6.text[:150]}")

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f_ in failures:
            print("  -", f_)
        return 1
    print("payu: all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
