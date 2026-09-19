"""Admin user management: the detail view, grants, and blocking.

Guarantees under test:
  * only an admin can see a user's detail, grant, or block
  * every grant needs a reason, and credits can never be driven negative
  * a complimentary product is a PAID ₹0 order: it delivers (kundali queue,
    ledger) but is NOT counted as a sale
  * a block needs a reason, records who/when/why, cannot hit an admin or
    yourself, and the blocked user gets a clear refusal, not a sign-in loop

    ASTRO_GATEWAY=test ASTRO_DEV_LOGIN=1 uvicorn app.main:app --port 8600
    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.test_admin_users
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

BASE = "http://127.0.0.1:8600"
RUN = random.randint(100000, 999999)
failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def sign_in(email: str) -> requests.Session:
    s = requests.Session()
    s.post(f"{BASE}/api/auth/dev", json={"email": email, "name": email.split("@")[0]},
           timeout=30).raise_for_status()
    return s


def make_admin(email: str) -> None:
    from sqlalchemy import select

    from app.db import User, session as db_session

    with db_session() as db:
        u = db.execute(select(User).where(User.email == email)).scalar_one()
        u.is_admin = True
        db.commit()


def uid(s: requests.Session) -> int:
    return s.get(f"{BASE}/api/me", timeout=20).json()["user"]["id"]


def credits(s: requests.Session) -> int:
    return s.get(f"{BASE}/api/me", timeout=20).json()["user"]["credits"]


def main() -> int:
    admin_email = f"uadmin{RUN}@example.com"
    sign_in(admin_email)
    make_admin(admin_email)
    admin = sign_in(admin_email)
    other_admin_email = f"uadmin2{RUN}@example.com"
    sign_in(other_admin_email)
    make_admin(other_admin_email)
    other_admin = sign_in(other_admin_email)

    target_email = f"target{RUN}@example.com"
    target = sign_in(target_email)
    tid, aid, oid = uid(target), uid(admin), uid(other_admin)
    bystander = sign_in(f"bystander{RUN}@example.com")

    print("\n1. Only an admin may look or act")
    check("detail -> 403 for a user",
          bystander.get(f"{BASE}/api/admin/users/{tid}", timeout=20).status_code == 403)
    check("grant -> 403 for a user",
          bystander.post(f"{BASE}/api/admin/users/{tid}/grant",
                         json={"kind": "credits", "credits": 5, "note": "self-serve"},
                         timeout=20).status_code == 403)
    check("block -> 403 for a user",
          bystander.post(f"{BASE}/api/admin/users/{tid}/block",
                         json={"blocked": True, "reason": "no"}, timeout=20).status_code == 403)
    check("unknown user -> 404",
          admin.get(f"{BASE}/api/admin/users/99999999", timeout=20).status_code == 404)

    print("\n2. The detail view")
    d = admin.get(f"{BASE}/api/admin/users/{tid}", timeout=20).json()
    check("profile, balance and counts", d["user"]["email"] == target_email
          and d["balance"] == credits(target) and d["questions_count"] == 0
          and d["user"]["blocked"] is False, str(d["user"])[:120])
    check("the ledger shows the sign-up gift",
          any(e["kind"] == "signup_bonus" for e in d["ledger"]), str(d["ledger"])[:120])

    print("\n3. Granting credits needs a reason and is bounded")
    grant = f"{BASE}/api/admin/users/{tid}/grant"
    start = credits(target)
    check("no note -> 400", admin.post(grant, json={"kind": "credits", "credits": 5,
                                                    "note": ""}, timeout=20).status_code == 400)
    check("a one-letter note -> 400", admin.post(grant, json={"kind": "credits", "credits": 5,
                                                              "note": "x"}, timeout=20).status_code == 400)
    check("zero credits -> 400", admin.post(grant, json={"kind": "credits", "credits": 0,
                                                         "note": "test grant"}, timeout=20).status_code == 400)
    check("1,001 credits -> 400", admin.post(grant, json={"kind": "credits", "credits": 1001,
                                                          "note": "test grant"}, timeout=20).status_code == 400)
    check("nothing changed by the refused grants", credits(target) == start)
    r = admin.post(grant, json={"kind": "credits", "credits": 7, "note": "Compensation for the frozen chat"},
                   timeout=20)
    check("a valid grant works", r.status_code == 200 and r.json()["new_balance"] == start + 7, r.text[:100])
    check("the user's balance reflects it", credits(target) == start + 7)
    d = admin.get(f"{BASE}/api/admin/users/{tid}", timeout=20).json()
    entry = next(e for e in d["ledger"] if e["delta"] == 7)
    check("the ledger records who granted it and why",
          admin_email in entry["note"] and "frozen chat" in entry["note"], entry["note"])
    check("an unknown kind -> 400", admin.post(grant, json={"kind": "gold", "note": "test grant"},
                                              timeout=20).status_code == 400)

    print("\n4. Deducting can never go below zero")
    adj = f"{BASE}/api/admin/users/{tid}/credits"
    bal = credits(target)
    check("zero adjustment -> 400", admin.post(adj, json={"delta": 0, "note": "n"}, timeout=20).status_code == 400)
    over = admin.post(adj, json={"delta": -(bal + 1), "note": "typo"}, timeout=20)
    check("deducting more than the balance -> 400", over.status_code == 400, over.text[:100])
    check("balance untouched by the refused deduction", credits(target) == bal)
    ok = admin.post(adj, json={"delta": -2, "note": "correcting a double grant"}, timeout=20)
    check("a valid deduction works", ok.status_code == 200 and ok.json()["new_balance"] == bal - 2)

    print("\n5. A complimentary product is a paid ₹0 order that is not a sale")
    m0 = admin.get(f"{BASE}/api/admin/metrics", timeout=20).json()
    check("an unknown product -> 400", admin.post(grant, json={"kind": "product", "sku": "nope",
                                                               "note": "test grant"}, timeout=20).status_code == 400)
    before = credits(target)
    r = admin.post(grant, json={"kind": "product", "sku": "q10", "note": "Goodwill pack"}, timeout=20)
    o = r.json().get("order", {})
    check("a question pack grants its credits",
          r.status_code == 200 and o.get("status") == "paid" and o.get("amount") == 0
          and credits(target) == before + 10, r.text[:140])
    r = admin.post(grant, json={"kind": "product", "sku": "k3", "note": "Free kundali for the first customer"},
                   timeout=20)
    ko = r.json().get("order", {})
    check("a kundali is paid, ₹0 and pending fulfilment",
          ko.get("status") == "paid" and ko.get("amount") == 0 and ko.get("fulfilment") == "pending",
          str(ko)[:140])
    queue = admin.get(f"{BASE}/api/admin/kundalis?state=all", timeout=20).json()["kundalis"]
    check("it enters the astrologer's queue", any(k["id"] == ko.get("id") for k in queue))
    d = admin.get(f"{BASE}/api/admin/users/{tid}", timeout=20).json()
    comp = next((x for x in d["orders"] if x["id"] == ko.get("id")), None)
    check("the detail view labels it a comp, not a purchase",
          comp is not None and comp["provider"] == "comp" and comp["amount"] == 0, str(comp))
    m1 = admin.get(f"{BASE}/api/admin/metrics", timeout=20).json()
    check("it is NOT counted as a sale or as revenue",
          m1["total_paid_orders"] == m0["total_paid_orders"]
          and m1["revenue_all_rupees"] == m0["revenue_all_rupees"],
          f"{m0['total_paid_orders']} -> {m1['total_paid_orders']}")
    listed = admin.get(f"{BASE}/api/admin/orders/manual?limit=100", timeout=20).json()["orders"]
    check("it does not appear among the manual SALES", not any(x["id"] == ko.get("id") for x in listed))
    row = next(u for u in admin.get(f"{BASE}/api/admin/users?q={target_email}", timeout=20).json()["users"]
               if u["id"] == tid)
    check("the user's paid-orders and spend ignore comps",
          row["orders_count"] == 0 and row["spent_rupees"] == 0, str(row["orders_count"]))

    print("\n6. Blocking needs a reason and has guardrails")
    block = f"{BASE}/api/admin/users/{tid}/block"
    check("blocking with no reason -> 400",
          admin.post(block, json={"blocked": True}, timeout=20).status_code == 400)
    check("blocking with a one-letter reason -> 400",
          admin.post(block, json={"blocked": True, "reason": "x"}, timeout=20).status_code == 400)
    check("you cannot block yourself",
          admin.post(f"{BASE}/api/admin/users/{aid}/block", json={"blocked": True, "reason": "oops"},
                     timeout=20).status_code == 400)
    check("you cannot block another administrator",
          admin.post(f"{BASE}/api/admin/users/{oid}/block", json={"blocked": True, "reason": "oops"},
                     timeout=20).status_code == 400)
    check("the target was not blocked by any refused attempt",
          admin.get(f"{BASE}/api/admin/users/{tid}", timeout=20).json()["user"]["blocked"] is False)

    print("\n7. A block is recorded, enforced, and explained")
    live_session = target                                   # signed in BEFORE the block
    r = admin.post(block, json={"blocked": True, "reason": "Abusive messages to support"}, timeout=20)
    check("blocked with a reason", r.status_code == 200 and r.json()["blocked"] is True, r.text[:100])
    u = admin.get(f"{BASE}/api/admin/users/{tid}", timeout=20).json()["user"]
    check("who, when and why are stored",
          u["blocked"] and u["blocked_reason"] == "Abusive messages to support"
          and u["blocked_by"] == admin_email and u["blocked_at"], str(u))
    check("the users list shows the reason",
          next(x for x in admin.get(f"{BASE}/api/admin/users?q={target_email}", timeout=20).json()["users"]
               if x["id"] == tid)["blocked_reason"] == "Abusive messages to support")
    act = live_session.post(f"{BASE}/api/feedback", json={"message": "I would like to write something"},
                            timeout=20)
    check("a blocked user's live session is refused with 403 and a clear message",
          act.status_code == 403 and "suspended" in act.text and "support@" in act.text, act.text[:160])
    retry = requests.post(f"{BASE}/api/auth/dev", json={"email": target_email}, timeout=20)
    check("signing in again is refused with the same message",
          retry.status_code == 403 and "suspended" in retry.text, retry.text[:120])
    check("a granted product still exists on the account (a block is not a wipe)",
          any(x["id"] == ko.get("id") for x in admin.get(f"{BASE}/api/admin/users/{tid}",
                                                         timeout=20).json()["orders"]))

    print("\n8. Unblocking clears the record and restores access")
    r = admin.post(block, json={"blocked": False}, timeout=20)
    check("unblocked", r.status_code == 200 and r.json()["blocked"] is False)
    u = admin.get(f"{BASE}/api/admin/users/{tid}", timeout=20).json()["user"]
    check("the block details are cleared",
          u["blocked"] is False and u["blocked_reason"] == "" and u["blocked_by"] == "", str(u))
    back = sign_in(target_email)
    check("they can sign in and use the site again",
          back.post(f"{BASE}/api/feedback", json={"message": "Thanks for restoring my account"},
                    timeout=20).status_code == 200)

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("admin users: all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
