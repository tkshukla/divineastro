"""Admin access, the kundali work queue, and the Instamojo adapter.

Two properties matter here:

* **Becoming an admin must go through ASTRO_ADMIN_EMAILS**, not through
  anything a visitor can influence. Signing in with an unlisted address must
  never grant rights, however the account is spelled.
* **A payment receipt belongs to exactly one order.** Paying for the cheap pack
  and presenting that receipt against an expensive one must be refused.

Run the server with ASTRO_DEV_LOGIN=1 and ASTRO_ADMIN_EMAILS=owner@divineastro.org:

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.test_admin
"""

from __future__ import annotations

import hashlib
import hmac
import os
import random
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

BASE = "http://127.0.0.1:8600"
ADMIN_EMAIL = "owner@divineastro.org"     # must match the server's env
failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def sign_in(email: str | None = None) -> tuple[requests.Session, str]:
    s = requests.Session()
    email = email or f"adm{random.randint(10000, 99999)}@example.com"
    s.post(f"{BASE}/api/auth/dev", json={"email": email}, timeout=30).raise_for_status()
    return s, email


def main() -> int:
    print("\n1. The admin page is served")
    page = requests.get(f"{BASE}/admin", timeout=20)
    check("/admin returns the shell", page.status_code == 200, str(page.status_code))
    check("it is marked noindex", "noindex" in page.text)
    for asset in ("/static/admin.js", "/static/admin.css"):
        r = requests.get(f"{BASE}{asset}", timeout=20)
        check(f"{asset} loads", r.status_code == 200, str(r.status_code))

    print("\n2. An ordinary account gets nothing")
    plain, plain_email = sign_in()
    me = plain.get(f"{BASE}/api/me", timeout=20).json()["user"]
    check("is_admin is false", me["is_admin"] is False, str(me["is_admin"]))
    for path in ("/api/admin/upi/pending", "/api/admin/coupons", "/api/admin/kundalis"):
        r = plain.get(f"{BASE}{path}", timeout=20)
        check(f"{path} refused", r.status_code == 403, str(r.status_code))

    print("\n3. A near-miss address is not promoted")
    for lookalike in (f" {ADMIN_EMAIL}".replace("@", "@ "), "owner@divineastro.org.evil.com",
                      "owner@divineastro.orgx"):
        s, _ = sign_in(lookalike)
        u = s.get(f"{BASE}/api/me", timeout=20).json()["user"]
        check(f"'{lookalike}' not admin", u["is_admin"] is False, str(u["is_admin"]))

    print("\n4. The listed address IS promoted, on sign-in alone")
    admin_s, _ = sign_in(ADMIN_EMAIL)
    au = admin_s.get(f"{BASE}/api/me", timeout=20).json()["user"]
    check("is_admin is true", au["is_admin"] is True, str(au["is_admin"]))
    check("case-insensitive", sign_in(ADMIN_EMAIL.upper())[0]
          .get(f"{BASE}/api/me", timeout=20).json()["user"]["is_admin"] is True)

    print("\n5. Admin can reach every panel")
    for path in ("/api/admin/upi/pending", "/api/admin/coupons",
                 "/api/admin/kundalis", "/api/admin/kundalis?state=all"):
        r = admin_s.get(f"{BASE}{path}", timeout=20)
        check(f"{path} allowed", r.status_code == 200, str(r.status_code))

    print("\n6. The kundali queue shows only PAID work")
    birth = plain.post(f"{BASE}/api/births", json={
        "label": "self", "name": "Test Person", "date": "1986-08-19", "time": "11:59",
        "time_known": True, "place": "Sultanpur, Uttar Pradesh, India",
        "latitude": 26.26, "longitude": 82.07, "timezone": "Asia/Kolkata",
    }, timeout=30)
    check("birth profile saved", birth.status_code == 200, birth.text[:120])
    birth_id = birth.json().get("birth", {}).get("id")

    order = plain.post(f"{BASE}/api/orders",
                       json={"sku": "k3", "birth_id": birth_id}, timeout=30)
    if order.status_code != 200:                    # sku name may differ
        skus = [p["sku"] for p in
                requests.get(f"{BASE}/api/products?kind=kundali", timeout=20).json()["products"]]
        check("a kundali product exists", bool(skus), str(skus))
        if skus:
            order = plain.post(f"{BASE}/api/orders",
                               json={"sku": skus[0], "birth_id": birth_id}, timeout=30)
    check("kundali order created", order.status_code == 200, order.text[:140])
    oid = order.json()["order"]["id"]

    queue = admin_s.get(f"{BASE}/api/admin/kundalis", timeout=20).json()["kundalis"]
    check("unpaid order is NOT in the queue",
          all(k["id"] != oid for k in queue), f"{len(queue)} queued")

    print("\n7. Once paid it appears, with the birth data attached")
    utr = f"{random.randint(10**11, 10**12 - 1)}"
    plain.post(f"{BASE}/api/orders/upi-claim",
               json={"order_id": oid, "utr": utr}, timeout=20)
    admin_s.post(f"{BASE}/api/admin/upi/verify",
                 json={"order_id": oid, "approve": True}, timeout=20)

    queue = admin_s.get(f"{BASE}/api/admin/kundalis", timeout=20).json()["kundalis"]
    row = next((k for k in queue if k["id"] == oid), None)
    check("paid order is queued", row is not None)
    if row:
        check("fulfilment starts pending", row["fulfilment"] == "pending", row["fulfilment"])
        check("buyer is shown", row["buyer_email"] == plain_email, str(row["buyer_email"]))
        check("birth details travel with it",
              (row.get("birth") or {}).get("date") == "1986-08-19", str(row.get("birth")))

    print("\n8. Fulfilment can be advanced, and only by an admin")
    denied = plain.post(f"{BASE}/api/admin/kundalis/fulfil",
                        json={"order_id": oid, "status": "delivered"}, timeout=20)
    check("customer cannot mark it delivered", denied.status_code == 403, str(denied.status_code))

    bad = admin_s.post(f"{BASE}/api/admin/kundalis/fulfil",
                       json={"order_id": oid, "status": "banana"}, timeout=20)
    check("unknown status refused", bad.status_code == 400, str(bad.status_code))

    ok = admin_s.post(f"{BASE}/api/admin/kundalis/fulfil",
                      json={"order_id": oid, "status": "in_progress", "note": "started"},
                      timeout=20)
    check("admin can advance it", ok.status_code == 200, ok.text[:120])
    open_q = admin_s.get(f"{BASE}/api/admin/kundalis", timeout=20).json()["kundalis"]
    check("still open at in_progress", any(k["id"] == oid for k in open_q))

    admin_s.post(f"{BASE}/api/admin/kundalis/fulfil",
                 json={"order_id": oid, "status": "delivered"}, timeout=20)
    open_q = admin_s.get(f"{BASE}/api/admin/kundalis", timeout=20).json()["kundalis"]
    all_q = admin_s.get(f"{BASE}/api/admin/kundalis?state=all", timeout=20).json()["kundalis"]
    check("delivered leaves the open queue", all(k["id"] != oid for k in open_q))
    check("delivered still visible in state=all", any(k["id"] == oid for k in all_q))

    print("\n9. A receipt cannot be moved between orders")
    a = plain.post(f"{BASE}/api/orders", json={"sku": "q10"}, timeout=30).json()["order"]
    b = plain.post(f"{BASE}/api/orders", json={"sku": "q50"}, timeout=30).json()["order"]
    cross = plain.post(f"{BASE}/api/orders/confirm", json={
        "order_id": b["id"], "payload": {"payment_request_id": f"DA{a['id']:06d}",
                                         "payment_id": "MOJOfake"},
    }, timeout=20)
    check("cross-order receipt refused", cross.status_code == 400, str(cross.status_code))

    print("\n10. Instamojo webhook signing")
    os.environ["INSTAMOJO_SALT"] = "test-salt-value"
    from app.gateways import InstamojoGateway

    gw = InstamojoGateway()
    fields = {"payment_id": "MOJO123", "payment_request_id": "abc123",
              "status": "Credit", "amount": "111.00", "buyer": "x@example.com"}
    message = "|".join(fields[k] for k in sorted(fields, key=str.lower))
    mac = hmac.new(b"test-salt-value", message.encode(), hashlib.sha1).hexdigest()

    body = "&".join(f"{k}={v}" for k, v in {**fields, "mac": mac}.items()).encode()
    ok_sig, req_id, pay_id = gw.parse_webhook(body, {})
    check("a correctly signed webhook verifies", ok_sig is True)
    check("it yields the request id", req_id == "abc123", req_id)
    check("it yields the payment id", pay_id == "MOJO123", pay_id)

    tampered = body.replace(b"amount=111.00", b"amount=99999.00")
    check("a tampered webhook is rejected", gw.parse_webhook(tampered, {})[0] is False)
    check("an unsigned webhook is rejected",
          gw.parse_webhook(b"payment_id=X&status=Credit", {})[0] is False)

    failed = {**fields, "status": "Failed"}
    fmsg = "|".join(failed[k] for k in sorted(failed, key=str.lower))
    fmac = hmac.new(b"test-salt-value", fmsg.encode(), hashlib.sha1).hexdigest()
    fbody = "&".join(f"{k}={v}" for k, v in {**failed, "mac": fmac}.items()).encode()
    check("a signed but FAILED payment grants nothing",
          gw.parse_webhook(fbody, {})[0] is False)

    os.environ["INSTAMOJO_SALT"] = ""
    check("no salt configured -> never trusted",
          InstamojoGateway().parse_webhook(body, {})[0] is False)

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("admin, kundali queue and instamojo: all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
