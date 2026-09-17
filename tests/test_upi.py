"""UPI manual collection.

The property that matters most: **claiming a payment must grant nothing.**
Anyone can type five characters; only a human checking the bank statement may
turn an order into credits.

Only the last 5 characters of the UTR are asked for (less to type on a phone),
which means — unlike the old full-UTR flow — two different orders CAN
legitimately end up with the same claimed suffix. That must never crash an
approval or silently misattribute a payment; section 5 below is the actual
regression test for that.

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.test_upi
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

BASE = "http://127.0.0.1:8600"
failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def sign_in(email: str | None = None) -> tuple[requests.Session, str]:
    s = requests.Session()
    email = email or f"upi{random.randint(10000, 99999)}@example.com"
    s.post(f"{BASE}/api/auth/dev", json={"email": email}, timeout=30).raise_for_status()
    return s, email


def make_admin(email: str) -> None:
    from sqlalchemy import select

    from app.db import User, session as db_session

    with db_session() as db:
        u = db.execute(select(User).where(User.email == email)).scalar_one()
        u.is_admin = True
        db.commit()


def credits(s: requests.Session) -> int:
    return s.get(f"{BASE}/api/me", timeout=20).json()["user"]["credits"]


def rand_suffix() -> str:
    return f"{random.randint(10000, 99999)}"


def main() -> int:
    print("\n1. Gateway reports UPI")
    prods = requests.get(f"{BASE}/api/products", timeout=20).json()
    gw = prods["payment"]["gateway"]
    check("active gateway is upi_manual", gw == "upi_manual", gw)

    print("\n2. Buying produces payment instructions")
    buyer, buyer_email = sign_in()
    start = credits(buyer)
    order = buyer.post(f"{BASE}/api/orders", json={"sku": "q10"}, timeout=30)
    check("order created", order.status_code == 200, order.text[:120])
    data = order.json()
    oid = data["order"]["id"]
    co = data["checkout"]
    check("mode is upi_manual", co.get("mode") == "upi_manual", str(co.get("mode")))
    check("a VPA is shown", bool(co.get("vpa")), str(co.get("vpa")))
    check("a QR image is inlined", str(co.get("qr", "")).startswith("data:image/png;base64,"))
    check("upi:// deep link present", str(co.get("link", "")).startswith("upi://pay?"))
    check("reference is quotable", bool(co.get("reference")), str(co.get("reference")))
    check("amount matches the pack", co.get("amount") == 11100, str(co.get("amount")))

    print("\n3. A nonsense suffix is refused")
    bad = buyer.post(f"{BASE}/api/orders/upi-claim",
                     json={"order_id": oid, "utr_last5": "ab"}, timeout=20)
    check("too-short suffix rejected", bad.status_code == 400, str(bad.status_code))
    bad2 = buyer.post(f"{BASE}/api/orders/upi-claim",
                      json={"order_id": oid, "utr_last5": "123456"}, timeout=20)
    check("too-long suffix rejected", bad2.status_code == 400, str(bad2.status_code))

    print("\n4. Claiming grants NOTHING until a human approves")
    suffix = rand_suffix()
    claim = buyer.post(f"{BASE}/api/orders/upi-claim",
                       json={"order_id": oid, "utr_last5": suffix}, timeout=20)
    check("claim accepted", claim.status_code == 200, claim.text[:120])
    check("order awaits verification",
          claim.json()["status"] == "awaiting_verification", claim.json().get("status"))
    check("NO credits granted on claim", credits(buyer) == start,
          f"{start} -> {credits(buyer)}")

    print("\n5. Two orders CAN share a suffix — neither is blocked, and both "
          "approve cleanly (the actual regression risk of shortening the UTR)")
    other_oid = buyer.post(f"{BASE}/api/orders", json={"sku": "q10"}, timeout=30).json()["order"]["id"]
    same_suffix = buyer.post(f"{BASE}/api/orders/upi-claim",
                             json={"order_id": other_oid, "utr_last5": suffix}, timeout=20)
    check("a repeated suffix is NOT rejected (no false 409)",
          same_suffix.status_code == 200, str(same_suffix.status_code))

    admin_s, admin_email = sign_in()
    make_admin(admin_email)
    admin_s, _ = sign_in(admin_email)          # refresh the session's admin flag
    pending_before = admin_s.get(f"{BASE}/api/admin/upi/pending", timeout=20).json()["pending"]
    flagged = {r["id"]: r["utr_ambiguous"] for r in pending_before if r["id"] in (oid, other_oid)}
    check("admin queue flags both as ambiguous",
          flagged.get(oid) is True and flagged.get(other_oid) is True, str(flagged))

    approve_first = admin_s.post(f"{BASE}/api/admin/upi/verify",
                                 json={"order_id": oid, "approve": True, "note": "seen in statement"},
                                 timeout=20)
    check("first colliding order approves without a DB error",
          approve_first.status_code == 200 and approve_first.json().get("granted") is True,
          approve_first.text[:200])
    approve_second = admin_s.post(f"{BASE}/api/admin/upi/verify",
                                  json={"order_id": other_oid, "approve": True, "note": "also seen"},
                                  timeout=20)
    check("second colliding order ALSO approves without a DB error "
          "(this is the exact bug a naive last-5 implementation would hit)",
          approve_second.status_code == 200 and approve_second.json().get("granted") is True,
          approve_second.text[:200])
    check("both orders' credits landed",
          credits(buyer) == start + 20, f"{start} -> {credits(buyer)}")

    print("\n6. Only an admin can see or verify the queue")
    third_oid = buyer.post(f"{BASE}/api/orders", json={"sku": "q10"}, timeout=30).json()["order"]["id"]
    denied = buyer.get(f"{BASE}/api/admin/upi/pending", timeout=20)
    check("ordinary user cannot list pending", denied.status_code == 403, str(denied.status_code))
    sneaky = buyer.post(f"{BASE}/api/admin/upi/verify",
                        json={"order_id": third_oid, "approve": True}, timeout=20)
    check("ordinary user cannot self-approve", sneaky.status_code == 403, str(sneaky.status_code))

    print("\n7. Admin sees a fresh claim and approves")
    fresh_suffix = rand_suffix()
    buyer.post(f"{BASE}/api/orders/upi-claim",
              json={"order_id": third_oid, "utr_last5": fresh_suffix}, timeout=20)
    pending = admin_s.get(f"{BASE}/api/admin/upi/pending", timeout=20)
    check("admin can list pending", pending.status_code == 200, str(pending.status_code))
    rows = pending.json()["pending"]
    mine = [r for r in rows if r["id"] == third_oid]
    check("our order is queued", len(mine) == 1, f"{len(rows)} pending")
    if mine:
        check("queue shows the last-5 suffix and buyer",
              mine[0]["utr_last5"] == fresh_suffix and mine[0]["buyer_email"] == buyer_email,
              str(mine[0].get("buyer_email")))
        check("queue does not flag a unique suffix as ambiguous",
              mine[0]["utr_ambiguous"] is False, str(mine[0].get("utr_ambiguous")))
        check("queue shows expected amount", mine[0]["expected_amount"] == 111,
              str(mine[0].get("expected_amount")))

    before_final = credits(buyer)
    ok = admin_s.post(f"{BASE}/api/admin/upi/verify",
                      json={"order_id": third_oid, "approve": True, "note": "seen in statement"},
                      timeout=20)
    check("approval succeeded", ok.status_code == 200, ok.text[:120])
    check("credits granted on approval", credits(buyer) == before_final + 10,
          f"{before_final} -> {credits(buyer)}")

    print("\n8. Approving twice does not double-grant")
    again = admin_s.post(f"{BASE}/api/admin/upi/verify",
                         json={"order_id": third_oid, "approve": True}, timeout=20)
    check("replay grants nothing", again.json().get("granted") is False,
          str(again.json().get("granted")))
    check("balance unchanged", credits(buyer) == before_final + 10, str(credits(buyer)))

    print("\n9. Rejection does not grant")
    reject_order = buyer.post(f"{BASE}/api/orders", json={"sku": "q10"}, timeout=30).json()["order"]["id"]
    buyer.post(f"{BASE}/api/orders/upi-claim",
              json={"order_id": reject_order, "utr_last5": rand_suffix()},
              timeout=20)
    before = credits(buyer)
    rej = admin_s.post(f"{BASE}/api/admin/upi/verify",
                       json={"order_id": reject_order, "approve": False, "note": "not found"},
                       timeout=20)
    check("rejection accepted", rej.status_code == 200, str(rej.status_code))
    check("no credits for a rejected claim", credits(buyer) == before,
          f"{before} -> {credits(buyer)}")

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("upi manual collection: all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
