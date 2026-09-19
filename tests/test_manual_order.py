"""Admin "manual order" — recording a sale that happened off-site.

What has to hold: the order is a real PAID order that flows through the same
machinery as an online one (credits ledger, revenue metrics, kundali queue),
only an admin can create one, a repeat click cannot double-record, and a
customer signing in later lands on the account that was made for them.

    ASTRO_GATEWAY=test ASTRO_DEV_LOGIN=1 uvicorn app.main:app --port 8600
    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.test_manual_order
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

BASE = "http://127.0.0.1:8600"
failures: list[str] = []

BIRTH = {"name": "Test Customer", "date": "1975-09-19", "time": "06:43",
         "place": "Bengaluru, Karnataka, India", "latitude": 12.9716,
         "longitude": 77.5946, "gender": "male"}


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def sign_in(email: str | None = None) -> tuple[requests.Session, str]:
    s = requests.Session()
    email = email or f"man{random.randint(100000, 999999)}@example.com"
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


def main() -> int:
    admin_s, admin_email = sign_in()
    make_admin(admin_email)
    admin_s, _ = sign_in(admin_email)                 # refresh the admin flag
    url = f"{BASE}/api/admin/orders/manual"

    print("\n1. Only an admin may record one")
    plain, _ = sign_in()
    r = plain.post(url, json={"email": "x@example.com", "sku": "q10"}, timeout=20)
    check("ordinary user gets 403", r.status_code == 403, str(r.status_code))
    check("ordinary user cannot list them", plain.get(url, timeout=20).status_code == 403)
    check("anonymous gets 401/403",
          requests.post(url, json={"email": "x@example.com", "sku": "q10"},
                        timeout=20).status_code in (401, 403))

    print("\n2. Question pack for a brand-new customer")
    email = f"newbie{random.randint(100000, 999999)}@example.com"
    r = admin_s.post(url, json={"email": email, "name": "New Buyer", "sku": "q10",
                                "method": "cash", "reference": "receipt 42",
                                "note": "paid at the shop"}, timeout=30)
    check("recorded", r.status_code == 200, r.text[:200])
    d = r.json()
    o = d["order"]
    check("customer was created", d["customer"]["created"] is True)
    check("order is PAID", o["status"] == "paid", o["status"])
    check("amount defaults to list price", o["amount_paise"] == 11100, str(o["amount_paise"]))
    check("credits come from the pack", o["credits"] == 10, str(o["credits"]))
    check("fulfilment not applicable for questions", o["fulfilment"] == "not_applicable")
    check("welcome gift + pack credits both on the balance",
          d["customer"]["credits"] == 10 + 10,
          str(d["customer"]["credits"]))
    check("note records method and reference",
          "cash" in o["note"] and "receipt 42" in o["note"], o["note"])
    check("recorded_by names the admin", o["recorded_by"] == admin_email)

    print("\n3. The customer signing in later gets that same account and credits")
    cust, _ = sign_in(email)
    check("purchase is waiting on their account", credits(cust) == 20, str(credits(cust)))
    mine = cust.get(f"{BASE}/api/orders", timeout=20).json()["orders"]
    check("it shows in their order history",
          any(x["id"] == o["id"] and x["status"] == "paid" for x in mine))

    print("\n4. A repeat click is caught, an intentional repeat is allowed")
    dup = admin_s.post(url, json={"email": email, "sku": "q10"}, timeout=30)
    check("identical order within 2 minutes -> 409", dup.status_code == 409, dup.text[:160])
    check("balance untouched by the refused duplicate", credits(cust) == 20, str(credits(cust)))
    again = admin_s.post(url, json={"email": email, "sku": "q10", "force": True}, timeout=30)
    check("force records it", again.status_code == 200, again.text[:160])
    check("second sale's credits landed", credits(cust) == 30, str(credits(cust)))
    check("existing customer is not re-created", again.json()["customer"]["created"] is False)

    print("\n5. Kundali with birth details reaches the astrologer's queue")
    kemail = f"kund{random.randint(100000, 999999)}@example.com"
    r = admin_s.post(url, json={"email": kemail, "sku": "k3", "amount_paise": 9900,
                                "method": "upi", "reference": "48213", "birth": BIRTH},
                     timeout=30)
    check("recorded", r.status_code == 200, r.text[:200])
    k = r.json()
    check("kundali is pending fulfilment", k["order"]["fulfilment"] == "pending")
    check("amount override honoured (₹99)", k["order"]["amount_paise"] == 9900)
    check("discount vs list price recorded", k["order"]["discount_paise"] == 1200,
          str(k["order"]["discount_paise"]))
    check("a birth chart was saved", bool(k["birth"]))
    check("no missing-birth warning", not k["warnings"], str(k["warnings"]))
    check("chart is sidereal/Lahiri regardless of input",
          k["birth"]["zodiac"] == "sidereal" and k["birth"]["ayanamsa"] == "lahiri")
    queue = admin_s.get(f"{BASE}/api/admin/kundalis?state=all", timeout=20).json()
    rows = queue.get("orders") or queue.get("kundalis") or []
    check("order appears in /admin/kundalis",
          any(x.get("id") == k["order"]["id"] for x in rows), f"{len(rows)} rows")

    print("\n6. Kundali with NO birth details warns instead of failing")
    r = admin_s.post(url, json={"email": f"nob{random.randint(100000, 999999)}@example.com",
                                "sku": "k3"}, timeout=30)
    check("still recorded", r.status_code == 200, r.text[:160])
    check("warning about missing birth data", bool(r.json()["warnings"]))

    print("\n7. Custom order")
    cemail = f"cust{random.randint(100000, 999999)}@example.com"
    r = admin_s.post(url, json={"email": cemail, "sku": "custom", "title": "Muhurat consultation",
                                "amount_paise": 25100, "credits": 5, "method": "bank"},
                     timeout=30)
    check("recorded", r.status_code == 200, r.text[:200])
    check("takes the given title and credits",
          r.json()["order"]["title"] == "Muhurat consultation"
          and r.json()["order"]["credits"] == 5)
    no_amt = admin_s.post(url, json={"email": cemail, "sku": "custom", "title": "X"}, timeout=30)
    check("custom without an amount -> 400", no_amt.status_code == 400, str(no_amt.status_code))
    no_title = admin_s.post(url, json={"email": cemail, "sku": "custom", "amount_paise": 100},
                            timeout=30)
    check("custom without a title -> 400", no_title.status_code == 400, str(no_title.status_code))

    print("\n8. Bad input is refused and leaves nothing behind")
    ghost = f"ghost{random.randint(100000, 999999)}@example.com"
    for label, payload in [
        ("unknown SKU", {"email": ghost, "sku": "nope"}),
        ("no email or phone", {"sku": "q10"}),
        ("malformed email", {"email": "not-an-email", "sku": "q10"}),
        ("negative amount", {"email": ghost, "sku": "q10", "amount_paise": -5}),
        ("absurd amount", {"email": ghost, "sku": "q10", "amount_paise": 10 ** 12}),
        ("bad method", {"email": ghost, "sku": "q10", "method": "barter"}),
        ("bad birth date", {"email": ghost, "sku": "k3", "birth": {**BIRTH, "date": "19-09-1975"}}),
    ]:
        r = admin_s.post(url, json=payload, timeout=20)
        check(f"{label} -> 400", r.status_code == 400, f"{r.status_code} {r.text[:100]}")
    probe, _ = sign_in(ghost)
    check("a refused order did not leave a customer with credits behind",
          credits(probe) == 10, str(credits(probe)))   # only the ordinary sign-up gift

    print("\n9. Phone-only customer")
    phone = f"9{random.randint(100000000, 999999999)}"
    r = admin_s.post(url, json={"phone": phone, "name": "No Email", "sku": "q10"}, timeout=30)
    check("recorded without an email", r.status_code == 200, r.text[:160])
    check("phone stored", r.json()["order"]["customer_phone"] == phone)

    print("\n10. It shows up everywhere an online order would")
    lst = admin_s.get(f"{url}?limit=50", timeout=20).json()["orders"]
    check("listed under manual orders", any(x["id"] == o["id"] for x in lst))
    check("list row carries customer and note",
          any(x["id"] == o["id"] and x["customer_email"] == email for x in lst))
    m = admin_s.get(f"{BASE}/api/admin/metrics", timeout=20).json()
    recent = m.get("recent_orders", [])
    check("appears in dashboard recent orders", any(x["id"] == o["id"] for x in recent),
          f"{len(recent)} recent")

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("manual orders: all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
