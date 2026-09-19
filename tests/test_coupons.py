"""End-to-end test of the coupon system.

Covers the rules that decide how much money actually moves:

  * percent, flat and extra_credits coupons price correctly
  * a discount never takes the charge below the ₹1 gateway floor
  * expired / global-limit / per-user-limit / min-amount / wrong-category
    coupons are refused, each with its own message
  * redeeming the same order twice does not double-count

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.test_coupons
"""

from __future__ import annotations

import datetime as dt
import random
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

BASE = "http://127.0.0.1:8600"
RUN = random.randint(10000, 99999)
ADMIN_EMAIL = f"admin{RUN}@example.com"
USER_EMAIL = f"buyer{RUN}@example.com"
OTHER_EMAIL = f"other{RUN}@example.com"

# Catalogue prices this test reasons about, in paise.
Q10, Q50, K3 = 11100, 35100, 11100

failures: list[str] = []


def check(label: str, condition: bool, detail: str = "") -> None:
    print(f"  {'PASS' if condition else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not condition:
        failures.append(f"{label} {detail}")


def code(name: str) -> str:
    """Namespace codes per run so repeat runs never collide on the unique index."""
    return f"{name}{RUN}"


def signin(email: str) -> requests.Session:
    s = requests.Session()
    s.post(f"{BASE}/api/auth/dev", json={"email": email, "name": email.split("@")[0]})
    return s


def promote(email: str) -> None:
    """Make a user an administrator by writing the database directly."""
    from sqlalchemy import select

    from app.db import User, session

    with session() as db:
        user = db.execute(select(User).where(User.email == email)).scalar_one()
        user.is_admin = True
        db.commit()


def make(s: requests.Session, **fields) -> dict:
    res = s.post(f"{BASE}/api/admin/coupons", json=fields)
    if res.status_code != 200:
        raise AssertionError(f"create {fields.get('code')}: {res.status_code} {res.text[:200]}")
    return res.json()["coupon"]


def preview(s: requests.Session, coupon_code: str, sku: str) -> dict:
    return s.post(f"{BASE}/api/coupons/preview",
                  json={"code": coupon_code, "sku": sku}).json()


def buy(s: requests.Session, sku: str, coupon_code: str | None = None):
    body = {"sku": sku}
    if coupon_code:
        body["coupon_code"] = coupon_code
    return s.post(f"{BASE}/api/orders", json=body)


def main() -> int:
    print("\n1. Admin bootstrap")
    admin = signin(ADMIN_EMAIL)
    promote(ADMIN_EMAIL)
    who = admin.get(f"{BASE}/api/me").json()["user"]
    check("admin flag visible to the client", who.get("is_admin") is True, str(who.get("is_admin")))

    buyer = signin(USER_EMAIL)
    denied = buyer.get(f"{BASE}/api/admin/coupons")
    check("non-admin gets 403 on the admin list", denied.status_code == 403,
          str(denied.status_code))
    check("non-admin cannot create a coupon",
          buyer.post(f"{BASE}/api/admin/coupons",
                     json={"code": code("HACK"), "kind": "flat", "value": 100}
                     ).status_code == 403)

    print("\n2. Create the coupon set")
    past = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=2)).isoformat()
    make(admin, code=code("PCT20"), kind="percent", value=20, applies_to="all",
         max_per_user=5, description="20% off everything")
    make(admin, code=code("FLAT100"), kind="flat", value=10000,
         applies_to="questions", max_per_user=5)
    make(admin, code=code("BONUS5"), kind="extra_credits", value=5,
         applies_to="questions", max_per_user=5)
    make(admin, code=code("CAPPED"), kind="percent", value=50,
         max_discount_paise=5000, applies_to="all", max_per_user=5)
    make(admin, code=code("GONE"), kind="percent", value=50, expires_at=past,
         max_per_user=5)
    make(admin, code=code("ONCE"), kind="percent", value=10, max_per_user=1)
    make(admin, code=code("GLOBAL1"), kind="percent", value=10,
         max_redemptions=1, max_per_user=9)
    make(admin, code=code("BIGMIN"), kind="percent", value=50,
         min_amount_paise=200000, max_per_user=5)
    make(admin, code=code("KUNDALI"), kind="percent", value=10,
         applies_to="kundali", max_per_user=5)
    make(admin, code=code("HUGE"), kind="flat", value=9999999,
         applies_to="all", max_per_user=5)
    listing = admin.get(f"{BASE}/api/admin/coupons").json()["coupons"]
    mine = [c for c in listing if c["code"].endswith(str(RUN))]
    check("all ten coupons listed", len(mine) == 10, f"{len(mine)}")

    print("\n3. Percent discount")
    p = preview(buyer, code("PCT20"), "q10")
    check("percent preview valid", p["valid"] is True, p["message"])
    check("20% of ₹111 is ₹22.20", p["discount"] == Q10 * 20 // 100, str(p["discount"]))
    check("final = original - discount", p["final"] == Q10 - p["discount"], str(p["final"]))
    check("original reported", p["original"] == Q10, str(p["original"]))
    check("no bonus on a percent coupon", p["bonus_credits"] == 0)

    order = buy(buyer, "q10", code("PCT20"))
    check("discounted order created", order.status_code == 200, order.text[:160])
    o = order.json()["order"]
    check("order charges the discounted amount", o["amount_paise"] == Q10 - (Q10 * 20 // 100),
          str(o["amount_paise"]))
    check("original price kept on the order", o["original_amount_paise"] == Q10,
          str(o["original_amount_paise"]))
    check("discount kept on the order", o["discount_paise"] == Q10 * 20 // 100,
          str(o["discount_paise"]))
    before = buyer.get(f"{BASE}/api/me").json()["user"]["credits"]
    conf = buyer.post(f"{BASE}/api/orders/confirm",
                      json={"order_id": o["id"], "payload": {}}).json()
    check("percent order pays out the plain pack credits",
          conf.get("credits") == before + 10, f"{before} -> {conf.get('credits')}")

    print("\n4. Percent discount respects max_discount_paise")
    p = preview(buyer, code("CAPPED"), "q50")
    check("50% of ₹351 capped at ₹50", p["discount"] == 5000, str(p["discount"]))
    check("capped final is ₹301", p["final"] == Q50 - 5000, str(p["final"]))

    print("\n5. Flat discount")
    p = preview(buyer, code("FLAT100"), "q50")
    check("flat preview valid", p["valid"] is True, p["message"])
    check("₹100 off ₹351", p["discount"] == 10000 and p["final"] == Q50 - 10000,
          f"{p['discount']}/{p['final']}")
    o = buy(buyer, "q50", code("FLAT100")).json()["order"]
    check("flat order charges ₹251", o["amount_paise"] == Q50 - 10000, str(o["amount_paise"]))
    before = buyer.get(f"{BASE}/api/me").json()["user"]["credits"]
    conf = buyer.post(f"{BASE}/api/orders/confirm",
                      json={"order_id": o["id"], "payload": {}}).json()
    check("flat order grants 50 credits", conf.get("credits") == before + 50,
          f"{before} -> {conf.get('credits')}")

    print("\n6. extra_credits grants a bonus, not a price cut")
    p = preview(buyer, code("BONUS5"), "q10")
    check("bonus preview valid", p["valid"] is True, p["message"])
    check("price is untouched", p["discount"] == 0 and p["final"] == Q10,
          f"{p['discount']}/{p['final']}")
    check("five bonus credits offered", p["bonus_credits"] == 5, str(p["bonus_credits"]))
    o = buy(buyer, "q10", code("BONUS5")).json()["order"]
    check("bonus order still charges full price", o["amount_paise"] == Q10,
          str(o["amount_paise"]))
    check("order carries 15 credits", o["credits"] == 15, str(o["credits"]))
    before = buyer.get(f"{BASE}/api/me").json()["user"]["credits"]
    conf = buyer.post(f"{BASE}/api/orders/confirm",
                      json={"order_id": o["id"], "payload": {}}).json()
    check("10 + 5 bonus credits granted", conf.get("credits") == before + 15,
          f"{before} -> {conf.get('credits')}")

    print("\n7. Discount clamped so the charge stays at or above ₹1")
    p = preview(buyer, code("HUGE"), "q10")
    check("over-generous coupon still valid", p["valid"] is True, p["message"])
    check("final is exactly ₹1", p["final"] == 100, str(p["final"]))
    check("discount is price minus ₹1", p["discount"] == Q10 - 100, str(p["discount"]))
    check("the clamp is explained to the customer", "minimum" in p["message"].lower(),
          p["message"])
    o = buy(buyer, "q10", code("HUGE")).json()["order"]
    check("clamped order charges ₹1", o["amount_paise"] == 100, str(o["amount_paise"]))
    check("charge never reaches zero", o["amount_paise"] >= 100)

    print("\n8. Expired coupon")
    p = preview(buyer, code("GONE"), "q10")
    check("expired coupon rejected", p["valid"] is False, str(p))
    check("message says expired", "expired" in p["message"].lower(), p["message"])
    check("no discount leaks through", p["discount"] == 0 and p["final"] == Q10)
    rejected = buy(buyer, "q10", code("GONE"))
    check("order with an expired coupon refused", rejected.status_code == 400,
          str(rejected.status_code))

    future = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=30)).isoformat()
    make(admin, code=code("SOON"), kind="percent", value=30, starts_at=future,
         max_per_user=5)
    p = preview(buyer, code("SOON"), "q10")
    check("not-yet-started coupon rejected", p["valid"] is False, p["message"])
    check("message says when it starts", "not valid until" in p["message"].lower(),
          p["message"])

    print("\n9. Unknown and inactive coupons")
    p = preview(buyer, "NOSUCHCODE", "q10")
    check("unknown code rejected", p["valid"] is False and "not found" in p["message"].lower(),
          p["message"])
    dead = make(admin, code=code("OFF"), kind="percent", value=25, active=False)
    p = preview(buyer, dead["code"], "q10")
    check("inactive coupon rejected", p["valid"] is False, p["message"])
    check("message says inactive", "active" in p["message"].lower(), p["message"])

    print("\n10. Minimum order amount")
    p = preview(buyer, code("BIGMIN"), "q10")
    check("below-minimum order rejected", p["valid"] is False, p["message"])
    check("message states the minimum", "2000" in p["message"], p["message"])

    print("\n11. Wrong product category")
    p = preview(buyer, code("KUNDALI"), "q10")
    check("kundali-only coupon refused on a question pack", p["valid"] is False, p["message"])
    check("message says it does not apply", "apply" in p["message"].lower(), p["message"])
    p = preview(buyer, code("KUNDALI"), "k3")
    check("same coupon works on a kundali", p["valid"] is True, p["message"])
    check("10% off ₹111", p["discount"] == K3 * 10 // 100, str(p["discount"]))

    print("\n12. Per-user limit")
    first = buy(buyer, "q10", code("ONCE"))
    check("first use of a once-per-user coupon allowed", first.status_code == 200,
          first.text[:120])
    fid = first.json()["order"]["id"]
    buyer.post(f"{BASE}/api/orders/confirm", json={"order_id": fid, "payload": {}})
    p = preview(buyer, code("ONCE"), "q10")
    check("second use previews as invalid", p["valid"] is False, p["message"])
    check("message says already used", "already" in p["message"].lower(), p["message"])
    second = buy(buyer, "q10", code("ONCE"))
    check("second order refused", second.status_code == 400, str(second.status_code))
    other = signin(OTHER_EMAIL)
    p = preview(other, code("ONCE"), "q10")
    check("a different customer may still use it", p["valid"] is True, p["message"])

    print("\n13. Global redemption limit")
    g = buy(buyer, "q10", code("GLOBAL1"))
    check("first global use allowed", g.status_code == 200, g.text[:120])
    gid = g.json()["order"]["id"]
    buyer.post(f"{BASE}/api/orders/confirm", json={"order_id": gid, "payload": {}})
    p = preview(other, code("GLOBAL1"), "q10")
    check("exhausted coupon refused for everyone", p["valid"] is False, p["message"])
    check("message says usage limit", "limit" in p["message"].lower(), p["message"])
    check("order refused too",
          buy(other, "q10", code("GLOBAL1")).status_code == 400)

    print("\n14. Redeeming twice for the same order does not double-count")
    once = [c for c in admin.get(f"{BASE}/api/admin/coupons").json()["coupons"]
            if c["code"] == code("ONCE")][0]
    check("counter at one after a single purchase", once["times_redeemed"] == 1,
          str(once["times_redeemed"]))

    credits_before = buyer.get(f"{BASE}/api/me").json()["user"]["credits"]
    for _ in range(3):
        buyer.post(f"{BASE}/api/orders/confirm", json={"order_id": fid, "payload": {}})
    credits_after = buyer.get(f"{BASE}/api/me").json()["user"]["credits"]
    check("replayed confirmations grant nothing", credits_before == credits_after,
          f"{credits_before} -> {credits_after}")

    again = [c for c in admin.get(f"{BASE}/api/admin/coupons").json()["coupons"]
             if c["code"] == code("ONCE")][0]
    check("times_redeemed unchanged by replays", again["times_redeemed"] == 1,
          str(again["times_redeemed"]))
    reds = admin.get(f"{BASE}/api/admin/coupons/{once['id']}/redemptions").json()
    check("exactly one redemption row", len(reds["redemptions"]) == 1,
          str(len(reds["redemptions"])))
    check("redemption points at the right order",
          reds["redemptions"][0]["order_id"] == fid, str(reds["redemptions"][0]))

    print("\n15. Webhook replay is also safe")
    hook = {"order_id": f"test_order_{fid}", "payment_id": f"pay_{fid}"}
    for _ in range(2):
        requests.post(f"{BASE}/api/webhooks/payment", json=hook)
    after_hook = admin.get(f"{BASE}/api/admin/coupons/{once['id']}/redemptions").json()
    check("still one redemption after webhook replays",
          len(after_hook["redemptions"]) == 1, str(len(after_hook["redemptions"])))
    check("balance untouched by webhook replays",
          buyer.get(f"{BASE}/api/me").json()["user"]["credits"] == credits_after)

    print("\n16. Admin edit, deactivate and delete")
    target = make(admin, code=code("EDITME"), kind="percent", value=10, max_per_user=5)
    patched = admin.patch(f"{BASE}/api/admin/coupons/{target['id']}",
                          json={"value": 35, "max_redemptions": 7})
    check("patch accepted", patched.status_code == 200, patched.text[:140])
    body = patched.json()["coupon"]
    check("value updated", body["value"] == 35, str(body["value"]))
    check("limit updated", body["max_redemptions"] == 7, str(body["max_redemptions"]))
    p = preview(buyer, code("EDITME"), "q50")
    check("new value takes effect immediately", p["discount"] == Q50 * 35 // 100,
          str(p["discount"]))

    bad = admin.patch(f"{BASE}/api/admin/coupons/{target['id']}", json={"value": 250})
    check("a percent above 100 is refused", bad.status_code == 400, str(bad.status_code))

    admin.patch(f"{BASE}/api/admin/coupons/{target['id']}", json={"active": False})
    p = preview(buyer, code("EDITME"), "q50")
    check("deactivated coupon stops working", p["valid"] is False, p["message"])

    def listed(cid: int) -> dict | None:
        rows = admin.get(f"{BASE}/api/admin/coupons").json()["coupons"]
        return next((c for c in rows if c["id"] == cid), None)

    check("before deleting, the paused coupon reports status 'paused'",
          listed(target["id"])["status"] == "paused", str(listed(target["id"])["status"]))
    gone = admin.delete(f"{BASE}/api/admin/coupons/{target['id']}").json()
    check("delete reports deleted", gone.get("deleted") is True, str(gone)[:120])
    row = listed(target["id"])
    check("a deleted coupon is NOT destroyed — it is still listed, flagged "
          "deleted, with a deletion time (so 'previously created' is visible)",
          row is not None and row["deleted"] is True and row["status"] == "deleted"
          and row["deleted_at"], str(row)[:160])
    check("a deleted coupon is unusable and reads as unknown to a customer",
          preview(buyer, code("EDITME"), "q50")["valid"] is False
          and "not found" in preview(buyer, code("EDITME"), "q50")["message"])
    check("deleting twice is harmless",
          admin.delete(f"{BASE}/api/admin/coupons/{target['id']}").status_code == 200)
    edit_deleted = admin.patch(f"{BASE}/api/admin/coupons/{target['id']}", json={"value": 5})
    check("a deleted coupon cannot be edited until restored (409)",
          edit_deleted.status_code == 409, str(edit_deleted.status_code))
    reuse = admin.post(f"{BASE}/api/admin/coupons",
                       json={"code": code("EDITME"), "kind": "percent", "value": 10})
    check("its code stays reserved: re-creating it is refused and says why",
          reuse.status_code == 409 and "deleted earlier" in reuse.text, reuse.text[:140])
    back = admin.post(f"{BASE}/api/admin/coupons/{target['id']}/restore").json()
    check("restore brings it back PAUSED, not live",
          back["coupon"]["status"] == "paused" and back["coupon"]["deleted"] is False,
          str(back["coupon"]["status"]))
    check("still unusable until resumed on purpose",
          preview(buyer, code("EDITME"), "q50")["valid"] is False)
    admin.patch(f"{BASE}/api/admin/coupons/{target['id']}", json={"active": True})
    p = preview(buyer, code("EDITME"), "q50")
    check("resumed, it works again with the edits it had before",
          p["valid"] is True and p["discount"] == Q50 * 35 // 100, str(p.get("discount")))

    used = admin.delete(f"{BASE}/api/admin/coupons/{once['id']}").json()
    check("a used coupon is deleted the same way", used.get("deleted") is True, str(used)[:120])
    check("its redemption history survives",
          len(admin.get(f"{BASE}/api/admin/coupons/{once['id']}/redemptions"
                        ).json()["redemptions"]) == 1)

    print("\n16b. A coupon limited to several products applies to each of them")
    multi = make(admin, code=code("MULTI"), kind="flat", value=1000,
                 applies_to="q10,k3", max_per_user=9)
    check("it applies to the first listed product",
          preview(buyer, code("MULTI"), "q10")["valid"] is True,
          preview(buyer, code("MULTI"), "q10")["message"])
    check("it applies to the second listed product",
          preview(buyer, code("MULTI"), "k3")["valid"] is True,
          preview(buyer, code("MULTI"), "k3")["message"])
    check("it still refuses a product that is not listed",
          preview(buyer, code("MULTI"), "q50")["valid"] is False)
    kinds = make(admin, code=code("KINDS"), kind="flat", value=1000,
                 applies_to="kundali, q100", max_per_user=9)
    check("a list may mix a product kind and a sku (whitespace tolerated)",
          preview(buyer, code("KINDS"), "k5")["valid"] is True
          and preview(buyer, code("KINDS"), "q100")["valid"] is True
          and preview(buyer, code("KINDS"), "q10")["valid"] is False)

    print("\n16c. The list carries a status the admin UI can filter on")
    past = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=2)).isoformat()
    soon = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=9)).isoformat()
    expired = make(admin, code=code("OLD"), kind="percent", value=5, expires_at=past)
    later = make(admin, code=code("LATER"), kind="percent", value=5, starts_at=soon)
    one_use = make(admin, code=code("ONEUSE"), kind="percent", value=5, max_redemptions=1)
    live = make(admin, code=code("LIVE"), kind="percent", value=5)
    check("live / expired / scheduled report the right status",
          (live["status"], expired["status"], later["status"])
          == ("live", "expired", "scheduled"),
          str((live["status"], expired["status"], later["status"])))
    order = buy(buyer, "q10", code("ONEUSE")).json()["order"]
    from app import billing as _billing
    from app.db import Order, session as _session
    with _session() as _db:
        _billing.mark_paid(_db, _db.get(Order, order["id"]), f"c16c-{RUN}")
    check("a coupon whose total limit is reached reports 'used_up'",
          listed(one_use["id"])["status"] == "used_up", str(listed(one_use["id"])["status"]))

    print("\n17. Buying without a coupon is unaffected")
    plain = buy(buyer, "q10").json()["order"]
    check("full price charged", plain["amount_paise"] == Q10, str(plain["amount_paise"]))
    check("no discount recorded", plain["discount_paise"] == 0, str(plain["discount_paise"]))
    check("no coupon attached", plain["coupon_id"] is None, str(plain["coupon_id"]))

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("coupons: all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
