"""The Diwali offer price engine (DIVASTRO-152, backend).

The honesty rules this pins down:
  1. the amount charged equals the amount shown, always;
  2. the "list" price is a price the site really charges once the offer ends,
     and the switch happens by itself at ends_at;
  3. the only urgency is the real end date (no per-visitor state);
  4. an order keeps the amount quoted at creation, even if paid after the end;
  5. ASTRO_OFFER_OFF=1 ends the offer immediately, never the reverse.

No server needed (in-process client, throwaway SQLite, a controllable clock).

    ASTRO_SECRET_KEY=ci ~/.venvs/divineastro/bin/python -u -m tests.test_offer_pricing
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import random
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

_tmp = tempfile.mkdtemp(prefix="astro_offer_")
os.environ["ASTRO_DATABASE_URL"] = f"sqlite:///{Path(_tmp).as_posix()}/t.db"
os.environ["ASTRO_DEV_LOGIN"] = "1"
os.environ["ASTRO_COOKIE_SECURE"] = "0"
os.environ["PAYU_MERCHANT_KEY"] = "gdtestkey"
os.environ["PAYU_SALT"] = "gdtestsalt123456"
os.environ["PAYU_SANDBOX"] = "1"
os.environ["PAYU_SURL"] = "https://divineastro.org/api/payu/return"
os.environ["PAYU_FURL"] = "https://divineastro.org/api/payu/return"
os.environ["ASTRO_GATEWAY"] = "test"
for k in ("ASTRO_OFFER_ENDS", "ASTRO_OFFER_OFF"):
    os.environ.pop(k, None)

from fastapi.testclient import TestClient  # noqa: E402

from app import billing, coupons, db as database  # noqa: E402
from app.main import app  # noqa: E402

IST = billing.IST
ENDS = dt.datetime(2026, 11, 15, 23, 59, 59, tzinfo=IST)
BEFORE = dt.datetime(2026, 10, 9, 12, 0, tzinfo=IST)
AFTER = ENDS + dt.timedelta(days=3)

OFFER = {"q10": 11100, "q50": 35100, "q100": 65100, "sq_career": 11100,
         "sq_marriage_timing": 11100, "sq_wealth_business": 11100,
         "life_book": 49900, "k3": 11100, "k5": 35100, "k3q3": 110000}
LIST = {"q10": 19900, "q50": 59900, "q100": 119900, "sq_career": 19900,
        "sq_marriage_timing": 19900, "sq_wealth_business": 19900,
        "life_book": 89900, "k3": 19900, "k5": 59900, "k3q3": 199900}

failures: list[str] = []
client = TestClient(app, raise_server_exceptions=False)
CLOCK = {"now": BEFORE}
billing._now = lambda: CLOCK["now"]        # the injected clock


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def at(when) -> None:
    CLOCK["now"] = when


def sign_in() -> str:
    email = f"offer{random.randint(10000, 99999)}{random.randint(0, 999)}@example.com"
    client.post("/api/auth/dev", json={"email": email}).raise_for_status()
    return email


def credits() -> int:
    return client.get("/api/me").json()["user"]["credits"]


def graph(html: str) -> list[dict]:
    out = []
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        data = json.loads(block.replace("<\\/", "</"))
        out += data.get("@graph", [data]) if isinstance(data, dict) else data
    return out


def main() -> int:
    print("\n1. During the offer: effective = offer price, list = the regular price")
    at(BEFORE)
    check("every catalogue SKU is covered by this test", set(billing.PRODUCTS) == set(OFFER))
    check("effective price = offer price for every SKU",
          all(billing.effective_price_paise(s) == OFFER[s] for s in OFFER))
    check("regular (list) prices are the owner's",
          all(billing.PRODUCTS[s].list_paise == LIST[s] for s in LIST))
    st = billing.offer_status()
    check("offer_status: active, named, ends 15 Nov 2026 23:59:59 IST",
          st["active"] and st["name"] == "Diwali offer"
          and st["ends_at_iso"] == "2026-11-15T23:59:59+05:30", str(st))
    check("offer_status carries a human label", "15 November 2026" in st["ends_at_label"], st["ends_at_label"])
    check("the offer is never dearer than the list price",
          all(OFFER[s] < LIST[s] for s in OFFER))

    print("\n2. The boundary")
    check("1 second before ends_at: still the offer",
          billing.effective_price_paise("q10", ENDS - dt.timedelta(seconds=1)) == 11100)
    check("exactly at ends_at: the list price",
          billing.effective_price_paise("q10", ENDS) == 19900
          and not billing.offer_status(ENDS)["active"])
    check("after: list price, status inactive with no end advertised",
          billing.effective_price_paise("q50", AFTER) == 59900
          and billing.offer_status(AFTER) == {"active": False, "name": "Diwali offer",
                                              "ends_at_iso": None, "ends_at_label": None})
    check("the same instant in UTC behaves the same (tz-safe)",
          billing.effective_price_paise("q10", ENDS.astimezone(dt.timezone.utc)) == 19900)
    check("every SKU is list price after the end",
          all(billing.effective_price_paise(s, AFTER) == LIST[s] for s in LIST))

    print("\n3. /api/products: old keys intact, new fields correct")
    r = client.get("/api/products").json()
    q50 = next(p for p in r["products"] if p["sku"] == "q50")
    for key in ("sku", "title", "title_hi", "amount_paise", "credits", "kind", "blurb",
                "blurb_hi", "pages", "highlight", "rupees", "per_question"):
        check(f"old key still present: {key}", key in q50)
    check("amount_paise = the effective (offer) price", q50["amount_paise"] == 35100 and q50["rupees"] == 351)
    check("list_amount_paise = the regular price while active", q50["list_amount_paise"] == 59900)
    check("offer block", q50["offer"] == {"active": True, "name": "Diwali offer",
                                           "ends_at": "2026-11-15T23:59:59+05:30"}, str(q50["offer"]))
    check("price per question uses the effective price", q50["per_question"] == 7.02, str(q50["per_question"]))
    check("list price per question is the regular one", q50["list_per_question"] == 11.98, str(q50["list_per_question"]))
    check("a report has no per-question", next(p for p in r["products"] if p["sku"] == "sq_career")["per_question"] is None)
    at(AFTER)
    r2 = client.get("/api/products").json()
    q50b = next(p for p in r2["products"] if p["sku"] == "q50")
    check("after: amount_paise = list price", q50b["amount_paise"] == 59900 and q50b["rupees"] == 599)
    check("after: list_amount_paise is null, offer inactive with no end",
          q50b["list_amount_paise"] is None and q50b["offer"]["active"] is False
          and q50b["offer"]["ends_at"] is None, str(q50b))
    check("after: per question follows (5.99 each... 11.98 for 50 = 11.98)", q50b["per_question"] == 11.98)
    check("catalogue() and the API agree", [p["amount_paise"] for p in billing.catalogue()]
          == [p["amount_paise"] for p in r2["products"]])
    at(BEFORE)

    print("\n4. Order creation stores the quoted amount")
    sign_in()
    r = client.post("/api/orders", json={"sku": "q100"})
    o = r.json()["order"]
    check("amount = offer price, original = the price in force", o["amount_paise"] == 65100
          and o["original_amount_paise"] == 65100, str(o))
    check("the gateway was asked for exactly that", r.json()["checkout"]["amount"] == 65100)
    at(AFTER)
    r = client.post("/api/orders", json={"sku": "q100"})
    o = r.json()["order"]
    check("after the end a new order is the list price", o["amount_paise"] == 119900, str(o))
    at(BEFORE)

    print("\n5. Coupons apply to the effective price")
    run = random.randint(10000, 99999)
    with database.session() as S:
        S.add_all([
            database.Coupon(code=f"PCT10X{run}", kind=database.CouponKind.percent, value=10, max_per_user=0),
            database.Coupon(code=f"FLAT50X{run}", kind=database.CouponKind.flat, value=5000, max_per_user=0),
            database.Coupon(code=f"BONUS5X{run}", kind=database.CouponKind.extra_credits, value=5, max_per_user=0),
        ])
        S.commit()
    pv = client.post("/api/coupons/preview", json={"sku": "q50", "code": f"PCT10X{run}"}).json()
    check("preview during the offer: 10% of 35100", pv["valid"] and pv["original"] == 35100
          and pv["discount"] == 3510 and pv["final"] == 31590, str(pv))
    o = client.post("/api/orders", json={"sku": "q50", "coupon_code": f"PCT10X{run}"}).json()["order"]
    check("order matches the preview", o["amount_paise"] == 31590 and o["original_amount_paise"] == 35100
          and o["discount_paise"] == 3510, str(o))
    o = client.post("/api/orders", json={"sku": "q50", "coupon_code": f"FLAT50X{run}"}).json()["order"]
    check("flat coupon on the offer price", o["amount_paise"] == 30100 and o["discount_paise"] == 5000)
    o = client.post("/api/orders", json={"sku": "q50", "coupon_code": f"BONUS5X{run}"}).json()["order"]
    check("extra_credits leaves the price alone and adds credits",
          o["amount_paise"] == 35100 and o["credits"] == 55, str(o))
    at(AFTER)
    pv = client.post("/api/coupons/preview", json={"sku": "q50", "code": f"PCT10X{run}"}).json()
    check("preview after the end: 10% of the list price 59900",
          pv["original"] == 59900 and pv["discount"] == 5990 and pv["final"] == 53910, str(pv))
    o = client.post("/api/orders", json={"sku": "q50", "coupon_code": f"PCT10X{run}"}).json()["order"]
    check("order after the end agrees with its preview", o["amount_paise"] == 53910)
    at(BEFORE)

    print("\n6. An order made in the offer, paid after the end (test gateway)")
    email = sign_in()
    start = credits()
    r = client.post("/api/orders", json={"sku": "q10"}).json()
    oid, quoted = r["order"]["id"], r["order"]["amount_paise"]
    at(AFTER)
    pend = client.get("/api/orders").json()
    pend_o = next(x for x in (pend.get("orders") or pend) if x["id"] == oid)
    check("the pending order keeps its quote after the end (no silent repricing)",
          pend_o["amount_paise"] == quoted == 11100, str(pend_o))
    c = client.post("/api/orders/confirm", json={"order_id": oid, "payload": {}}).json()
    check("confirmed after the end: granted what was bought", c.get("granted") is True
          and credits() == start + 10, str(c))
    check("amount stays the quoted one on the paid order", c["order"]["amount_paise"] == 11100)
    at(BEFORE)

    print("\n7. The same through PayU: verification checks the stored amount")
    os.environ["ASTRO_GATEWAY"] = "payu"
    from app import gateways
    salt, key = os.environ["PAYU_SALT"], os.environ["PAYU_MERCHANT_KEY"]

    def rev(status, f, amount=None):
        parts = [salt, status] + [""] * 10 + [f["email"], f["firstname"], f["productinfo"],
                                               amount or f["amount"], f["txnid"], key]
        return hashlib.sha512("|".join(parts).encode()).hexdigest()

    def ret(f, amount=None, status="success"):
        amt = amount or f["amount"]
        return client.post("/api/payu/return", data={
            "txnid": f["txnid"], "status": status, "amount": amt, "productinfo": f["productinfo"],
            "firstname": f["firstname"], "email": f["email"], "hash": rev(status, f, amt),
            "mihpayid": f"mp{random.randint(1, 10**9)}"}, follow_redirects=False)

    check("PayU is the active gateway", gateways.active().key == "payu")
    sign_in()
    start = credits()
    d = client.post("/api/orders", json={"sku": "q50"}).json()
    f = d["checkout"]["fields"]
    check("PayU amount = the offer price", f["amount"] == "351.00", f["amount"])
    at(AFTER)
    loc = ret(f).headers.get("location", "")
    check("a return after the end is verified and granted", "payu=ok" in loc and credits() == start + 50, loc)
    at(BEFORE)

    sign_in()
    start = credits()
    d = client.post("/api/orders", json={"sku": "q10"}).json()
    f = d["checkout"]["fields"]
    at(AFTER)
    loc = ret(f, amount="199.00").headers.get("location", "")
    check("a validly signed return for a DIFFERENT amount (the new list price) is refused",
          "payu=failed" in loc and credits() == start, loc)
    loc = ret(f).headers.get("location", "")
    check("the quoted amount still pays the order", "payu=ok" in loc and credits() == start + 10, loc)
    at(AFTER)
    d = client.post("/api/orders", json={"sku": "q10"}).json()
    check("PayU amount for an order created after the end = list price",
          d["checkout"]["fields"]["amount"] == "199.00", d["checkout"]["fields"]["amount"])
    os.environ["ASTRO_GATEWAY"] = "test"
    at(BEFORE)

    print("\n8. ASTRO_OFFER_ENDS moves the end; ASTRO_OFFER_OFF only ever ends it")
    os.environ["ASTRO_OFFER_ENDS"] = "2027-01-31T18:30:00+00:00"       # = 1 Feb 2027 00:00 IST
    at(AFTER)
    check("end moved later: still the offer past the old date",
          billing.effective_price_paise("q10") == 11100 and billing.offer_status()["active"])
    check("label reflects the new end", "1 February 2027" in billing.offer_status()["ends_at_label"],
          billing.offer_status()["ends_at_label"])
    at(dt.datetime(2027, 1, 31, 18, 30, tzinfo=dt.timezone.utc))
    check("and flips at the new instant", billing.effective_price_paise("q10") == 19900)
    os.environ["ASTRO_OFFER_ENDS"] = "2026-10-01T00:00:00"             # naive -> IST, already past
    at(BEFORE)
    check("moved earlier (and past): list price now", billing.effective_price_paise("q10") == 19900)
    os.environ["ASTRO_OFFER_ENDS"] = "not a date"
    check("an unreadable end date fails SAFE: list prices", billing.effective_price_paise("q10") == 19900
          and not billing.offer_status()["active"])
    os.environ.pop("ASTRO_OFFER_ENDS")
    check("env cleared: default end date again", billing.effective_price_paise("q10") == 11100)
    for val in ("1", "true"):
        os.environ["ASTRO_OFFER_OFF"] = val
        check(f"kill switch ASTRO_OFFER_OFF={val} => list prices immediately",
              all(billing.effective_price_paise(s) == LIST[s] for s in LIST)
              and not billing.offer_status()["active"])
    r = client.get("/api/products").json()["products"][0]
    check("kill switch is reflected in the API (no strike, no offer)",
          r["list_amount_paise"] is None and r["offer"]["active"] is False and r["amount_paise"] == 19900)
    os.environ["ASTRO_OFFER_OFF"] = "0"
    check("OFF=0 does nothing", billing.effective_price_paise("q10") == 11100)
    os.environ["ASTRO_OFFER_OFF"] = "1"
    os.environ["ASTRO_OFFER_ENDS"] = "2099-01-01T00:00:00+05:30"
    check("the kill switch wins over a far-future end date", billing.effective_price_paise("q10") == 19900)
    os.environ.pop("ASTRO_OFFER_OFF")
    os.environ.pop("ASTRO_OFFER_ENDS")
    check("the switch can never create a discount: with no env the default end applies",
          billing.effective_price_paise("q10") == 11100)

    print("\n9. /pricing: effective price, and priceValidUntil only during the offer")
    at(BEFORE)
    h = client.get("/pricing").text
    ld = [n for n in graph(h) if n.get("@type") == "Product"]
    q10 = next(n for n in ld if n["sku"] == "q10")
    check("during: Offer price is the offer price", q10["offers"]["price"] == "111", str(q10["offers"]))
    check("during: priceValidUntil is the real end", q10["offers"].get("priceValidUntil")
          == "2026-11-15T23:59:59+05:30", str(q10["offers"]))
    # DIVASTRO-152 UI half: the regular price now appears too, but only struck through (<s class="was">).
    plain = re.sub(r'<s class="was">.*?</s>', "", h, flags=re.S)
    check("during: page shows the offer price (the regular price only struck through)",
          "<b>₹111</b>" in h and "₹199" not in plain and '<s class="was">' in h)
    at(AFTER)
    h = client.get("/pricing").text
    ld = [n for n in graph(h) if n.get("@type") == "Product"]
    q10 = next(n for n in ld if n["sku"] == "q10")
    check("after: Offer price is the list price", q10["offers"]["price"] == "199", str(q10["offers"]))
    check("after: no priceValidUntil", "priceValidUntil" not in q10["offers"])
    check("after: the page shows list prices", "₹199" in h and "₹599" in h and "₹1,199" in h and "₹111" not in h)
    check("after: price-per-question on the page follows (11.98)", "11.98" in h)
    check("the whole page claims no offer once it is over", "Diwali" not in h)
    at(BEFORE)

    print("\n10. Other readers of the price")
    at(AFTER)
    from app import daily_message
    promo = " ".join(t for t, _ in daily_message._promos("en"))
    check("daily-post promos quote the list price after the end", "₹599" in promo and "₹351" not in promo, promo[:200])
    at(BEFORE)
    promo = " ".join(t for t, _ in daily_message._promos("en"))
    check("and the offer price during it", "₹351" in promo)

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f_ in failures:
            print("  -", f_)
        return 1
    print("ALL PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
