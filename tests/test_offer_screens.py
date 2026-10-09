"""The Diwali offer on the server-rendered screens (DIVASTRO-152, UI half): /pricing and
/hi/pricing, and the /api/products cache header the app relies on.

What it pins down:
  1. DURING the offer every product row shows the REAL regular price (billing's list price)
     struck through beside the offer price, a "Save N%" badge, the label with the real end date,
     the banner and the explanation section, in English and in Hindi;
  2. AFTER the end instant (clock past ends_at, exactly at it, or ASTRO_OFFER_OFF=1, or an
     unreadable ASTRO_OFFER_ENDS) none of it appears: plain regular prices, no strike, no label,
     no banner, no priceValidUntil, with zero code change;
  3. the JSON-LD keeps ONE Offer per product priced at the effective price (no highPrice);
  4. caching: while the offer is live /pricing may be cached for at most 300 s and never past
     the end instant, /api/products is never cached.

No server needed (in-process client, throwaway SQLite, an injected billing clock).

    ASTRO_SECRET_KEY=ci ~/.venvs/divineastro/bin/python -u -m tests.test_offer_screens
"""

from __future__ import annotations

import datetime as dt
import html as htmllib
import json
import os
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

_tmp = tempfile.mkdtemp(prefix="astro_offer_screens_")
os.environ["ASTRO_DATABASE_URL"] = f"sqlite:///{Path(_tmp).as_posix()}/t.db"
os.environ["ASTRO_GATEWAY"] = "test"
for k in ("ASTRO_OFFER_ENDS", "ASTRO_OFFER_OFF"):
    os.environ.pop(k, None)

from fastapi.testclient import TestClient  # noqa: E402

from app import billing  # noqa: E402
from app.main import app  # noqa: E402

IST = billing.IST
ENDS = dt.datetime(2026, 11, 15, 23, 59, 59, tzinfo=IST)
BEFORE = dt.datetime(2026, 10, 9, 12, 0, tzinfo=IST)
AFTER = ENDS + dt.timedelta(days=3)

client = TestClient(app, raise_server_exceptions=False)
CLOCK = {"now": BEFORE}
billing._now = lambda: CLOCK["now"]
failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def at(when) -> None:
    CLOCK["now"] = when


def money(paise: int) -> str:
    return f"₹{paise // 100:,}"


def graph(h: str) -> list[dict]:
    out = []
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S):
        data = json.loads(block.replace("<\\/", "</"))
        out += data.get("@graph", [data])
    return out


def cell(h: str, sku: str) -> str:
    m = re.search(rf'<tr id="{sku}" data-sku="{sku}">.*?<td class="pr-price">(.*?)</td></tr>', h, re.S)
    return m.group(1) if m else ""


def text(h: str) -> str:
    return htmllib.unescape(re.sub(r"<[^>]+>", "", h))


def max_age(resp) -> int:
    return int(re.search(r"max-age=(\d+)", resp.headers["cache-control"]).group(1))


# What the pages must say, from the owner's wording.
EN = {
    "pill": "Diwali offer · ends 15 Nov",
    "banner": "Diwali offer prices are valid until 15 November 2026, 11:59 PM IST. Regular prices apply after that.",
    "h2": "About the Diwali offer", "was": "Regular price", "path": "/pricing",
}
HI = {
    "pill": "दिवाली ऑफ़र · अंतिम तिथि 15 नवंबर",
    "banner": "दिवाली ऑफ़र की कीमतें 15 नवंबर 2026, रात 11:59 बजे (IST) तक मान्य हैं। उसके बाद सामान्य कीमतें लागू होंगी।",
    "h2": "दिवाली ऑफ़र के बारे में", "was": "सामान्य कीमत", "path": "/hi/pricing",
}
OFFER_MARKERS = ('class="was"', 'class="pr-offer"', 'class="pr-pill"', "diwali-offer", "data-offer-banner", 'class="pr-save"',
                 "priceValidUntil", "Diwali", "दिवाली")


def main() -> int:
    ends_iso = ENDS.isoformat()

    print("\n1. During the offer: strike, badge, label, banner, explanation (en + hi)")
    at(BEFORE)
    cat = {p["sku"]: p for p in billing.catalogue()}
    for label, tx in (("en", EN), ("hi", HI)):
        r = client.get(tx["path"])
        h = r.text
        t = text(h)
        check(f"[{label}] 200", r.status_code == 200)
        bad = []
        for sku, p in cat.items():
            c = cell(h, sku)
            want_was = (f'<s class="was"><span class="sr-only">{tx["was"]} </span>'
                        f'{money(billing.LIST_PRICES_PAISE[sku])}</s>')
            pct = round((1 - billing.PRODUCTS[sku].offer_paise / billing.LIST_PRICES_PAISE[sku]) * 100)
            if want_was not in c or f"<b>{money(billing.PRODUCTS[sku].offer_paise)}</b>" not in c:
                bad.append((sku, "strike/price"))
            if not re.search(rf'class="pr-save">[^<]*(?<!\d){pct}%', c):
                bad.append((sku, "save badge", pct))
            if f"{money(p['list_amount_paise'])}" not in c:
                bad.append((sku, "api list price"))
        check(f"[{label}] every product row: strike = LIST_PRICES_PAISE, price = offer, Save N% computed", not bad, str(bad))
        check(f"[{label}] per-question line also strikes the regular per-question price",
              "₹19.90</s>" in cell(h, "q10") and "₹11.10" in cell(h, "q10"))
        check(f"[{label}] the label with the real short date", tx["pill"] in t, tx["pill"])
        check(f"[{label}] the banner sentence with the real long date", tx["banner"] in t, tx["banner"])
        check(f"[{label}] the banner is the first thing under the h1",
              re.search(r"</h1>\s*(<style>.*?</style>)?\s*<p class=\"pr-offer\"", h, re.S) is not None)
        check(f"[{label}] the explanation section", f'<h2 id="diwali-offer">{tx["h2"]}</h2>' in h)
        check(f"[{label}] the date is the one in /api/products offer.ends_at (15 Nov 2026 IST)",
              client.get("/api/products").json()["products"][0]["offer"]["ends_at"] == ends_iso
              and "15" in tx["banner"] and "2026" in tx["banner"])
        check(f"[{label}] no countdown, no scarcity wording",
              not re.search(r"countdown|only \d+ left|hurry|last chance|never be this low|कभी नहीं", t, re.I))
    en_text = text(client.get("/pricing").text)
    check("the explanation: all products, regular prices afterwards, order keeps its quoted price",
          "Every product on this page is on our Diwali offer" in en_text
          and "After that the regular prices apply automatically" in en_text
          and "An order you start during the offer keeps the price it was quoted at" in en_text
          and "11:59 PM IST" in en_text)

    print("\n2. JSON-LD: one Offer per product at the effective price, valid until the real end")
    nodes = graph(client.get("/pricing").text)
    products = [n for n in nodes if n.get("@type") == "Product"]
    check("one Product per catalogue entry", len(products) == len(cat), str(len(products)))
    bad = [p["sku"] for p in products
           if p["offers"]["price"] != str(billing.PRODUCTS[p["sku"]].offer_paise // 100)
           or p["offers"].get("priceValidUntil") != ends_iso
           or not isinstance(p["offers"], dict)]
    check("Offer.price = effective price, priceValidUntil = offer.ends_at", not bad, str(bad))
    raw = client.get("/pricing").text
    check("no highPrice / lowPrice / AggregateOffer / second offer",
          not re.search(r"highPrice|lowPrice|AggregateOffer", raw)
          and all(isinstance(p["offers"], dict) for p in products))

    print("\n3. Caching while the offer is live")
    r = client.get("/pricing")
    check("Cache-Control is short (<= 300 s) and private", max_age(r) <= 300 and "private" in r.headers["cache-control"],
          r.headers["cache-control"])
    for secs in (120, 30, 1):
        at(ENDS - dt.timedelta(seconds=secs))
        r1, r2 = client.get("/pricing"), client.get("/hi/pricing")
        check(f"{secs}s before the end: max-age <= {secs} s (a cached copy cannot outlive the offer)",
              max_age(r1) <= secs and max_age(r2) <= secs, f"{r1.headers['cache-control']} / {r2.headers['cache-control']}")
    at(BEFORE)
    r = client.get("/api/products")
    check("/api/products is never cached", r.headers.get("cache-control") == "no-store", str(r.headers.get("cache-control")))

    print("\n4. After the end: nothing of the offer, plain regular prices")
    cases = [("clock past ends_at", lambda: at(AFTER)),
             ("exactly at ends_at", lambda: at(ENDS))]
    for name, setup in cases:
        at(BEFORE)
        setup()
        for label, tx in (("en", EN), ("hi", HI)):
            r = client.get(tx["path"])
            h = r.text
            leftovers = [m for m in OFFER_MARKERS if m in h]
            check(f"[{name}] [{label}] no offer markup, wording, label, banner or explanation", not leftovers, str(leftovers))
            bad = {s: (re.sub(r"<[^>]+>", "", cell(h, s)), money(billing.LIST_PRICES_PAISE[s]))
                   for s in cat if f"<b>{money(billing.LIST_PRICES_PAISE[s])}</b>" not in cell(h, s)
                   or "<s " in cell(h, s)}
            check(f"[{name}] [{label}] every price is the regular price, none struck", not bad, str(bad))
        ld = [n for n in graph(client.get("/pricing").text) if n.get("@type") == "Product"]
        check(f"[{name}] JSON-LD: list price and no priceValidUntil",
              all(p["offers"]["price"] == str(billing.LIST_PRICES_PAISE[p["sku"]] // 100)
                  and "priceValidUntil" not in p["offers"] for p in ld))
        api = client.get("/api/products").json()["products"]
        check(f"[{name}] /api/products: offer inactive, no list price, amount = regular price",
              all(not p["offer"]["active"] and p["list_amount_paise"] is None
                  and p["amount_paise"] == billing.LIST_PRICES_PAISE[p["sku"]] for p in api))
    at(ENDS - dt.timedelta(seconds=1))
    check("1 second before the end the offer is still on the page", 'class="pr-offer"' in client.get("/pricing").text)
    at(ENDS)
    check("at the end instant it is gone", 'class="pr-offer"' not in client.get("/pricing").text)

    print("\n5. The kill switch and an unreadable end date")
    at(BEFORE)
    os.environ["ASTRO_OFFER_OFF"] = "1"
    try:
        for label, tx in (("en", EN), ("hi", HI)):
            h = client.get(tx["path"]).text
            check(f"[OFF] [{label}] no offer markers, regular prices",
                  not [m for m in OFFER_MARKERS if m in h]
                  and all(f"<b>{money(billing.LIST_PRICES_PAISE[s])}</b>" in cell(h, s) for s in cat))
    finally:
        os.environ.pop("ASTRO_OFFER_OFF", None)
    os.environ["ASTRO_OFFER_ENDS"] = "not-a-date"
    try:
        h = client.get("/pricing").text
        check("[bad ASTRO_OFFER_ENDS] treated as over: no offer markers", not [m for m in OFFER_MARKERS if m in h])
    finally:
        os.environ.pop("ASTRO_OFFER_ENDS", None)

    print("\n6. A moved end date is the date shown")
    os.environ["ASTRO_OFFER_ENDS"] = "2026-11-20T23:59:59+05:30"
    try:
        h = client.get("/pricing").text
        check("ASTRO_OFFER_ENDS moves the label and the banner (no date typed in the page code)",
              "ends 20 Nov" in text(h) and "20 November 2026, 11:59 PM IST" in text(h))
    finally:
        os.environ.pop("ASTRO_OFFER_ENDS", None)

    print("\n7. Another registry language shows the English page with its own month name")
    at(BEFORE)
    r = client.get("/kn/pricing")
    check("/kn/pricing renders with the offer banner and stays noindex",
          r.status_code == 200 and 'class="pr-offer"' in r.text and "noindex" in r.text.split("</head>")[0])
    at(AFTER)
    check("/kn/pricing after the end: nothing", 'class="pr-offer"' not in client.get("/kn/pricing").text)

    print("\n8. The app's strings carry the placeholders")
    i18n_dir = Path(__file__).resolve().parent.parent / "app" / "static" / "i18n"
    bad = []
    for f in sorted(i18n_dir.glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        for k, ph in (("acct.offerPill", "{date}"), ("acct.offerBanner", "{date}"), ("acct.savePct", "{n}")):
            if ph not in d.get(k, ""):
                bad.append((f.stem, k))
        for k in ("acct.wasPrice", "acct.nowPrice"):
            if not d.get(k):
                bad.append((f.stem, k))
    check("all 13 languages: label/banner/save strings present with their placeholders", not bad, str(bad))

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("offer screens: all green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
