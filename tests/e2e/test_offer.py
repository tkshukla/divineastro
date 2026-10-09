"""The Diwali offer on screen (DIVASTRO-152, UI half).

While /api/products says the offer is live, every price in the app shows the REAL regular
price (list_amount_paise from the API) struck through beside the current price, a "Save N%"
badge computed from those two numbers, the label with the real end date, and the one-sentence
banner at the top of the Plans section and the store. When it says the offer is not live (a
server started with ASTRO_OFFER_OFF=1 stands in for "after the end date"), none of it exists
and every price is the regular price.

  a. offer ON: home Plans (signed out, en + hi), store (cards, banner, coupon keeps the strike
     on the regular price), the in-app offer card and the low-credits nudge, the Orders screen
     (what was charged, no strike), layout at 320 / 390 px
  b. the store re-reads /api/products when it opens: a page left open past the end of the offer
     shows the regular prices (simulated by the API turning the offer off between loads)
  c. offer OFF: nothing of it anywhere, prices are the regular ones

    ~/.venvs/divineastro/bin/python -u -m tests.e2e.test_offer
"""

from __future__ import annotations

import datetime as dt
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from playwright.sync_api import sync_playwright  # noqa: E402

from app import billing  # noqa: E402
from tests.e2e.harness import BIRTH, Checker, Page, server  # noqa: E402

check = Checker()

PHONE = {"viewport": {"width": 390, "height": 844}, "is_mobile": True, "has_touch": True, "device_scale_factor": 2}
SMALL = {"viewport": {"width": 320, "height": 640}, "is_mobile": True, "has_touch": True, "device_scale_factor": 2}
DESKTOP = {"viewport": {"width": 1440, "height": 900}}

ENDS_ENV = "2099-01-01T00:00:00+05:30"
PICKS = ["sq_career", "q10", "q50", "life_book"]            # the Plans cards
INK = ("Diwali", "Regular price", "Save ", "दिवाली", "सामान्य कीमत")


def money(paise: int) -> str:
    return f"₹{paise // 100:,}"


def products(pg: Page) -> dict:
    data = pg.page.context.request.get(f"{pg.base}/api/products").json()
    return {p["sku"]: p for p in data["products"]}


def save_pct(p: dict) -> int:
    return round((1 - p["amount_paise"] / p["list_amount_paise"]) * 100)


def no_hscroll(pg: Page) -> bool:
    return pg.page.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1")


def card_text(loc) -> str:
    return " ".join(loc.evaluate("e => e.textContent").split())


def offer_on(browser, base: str) -> None:
    print("\n[a. offer ON: Plans, store, offer card, nudge, orders]")
    ctx = browser.new_context(**PHONE)
    pg = Page(ctx.new_page(), base)
    pg.open_home()
    pg.page.wait_for_selector("#plans:not([hidden]) .plan", timeout=10000)
    api = products(pg)
    ends = dt.datetime.fromisoformat(api["q10"]["offer"]["ends_at"])
    short = f"{ends.day} {ends:%b}"
    long = f"{ends.day} {ends:%B %Y}"
    check("the API says the offer is live, with an end date and regular prices",
          all(p["offer"]["active"] and p["list_amount_paise"] > p["amount_paise"] for p in api.values())
          and ends.utcoffset() == dt.timedelta(hours=5, minutes=30), api["q10"]["offer"]["ends_at"])

    banner = pg.page.locator("#plans .offer-banner")
    check("Plans: one banner at the top, above the cards", banner.count() == 1
          and pg.page.evaluate("document.querySelector('#plans .offer-banner').compareDocumentPosition("
                               "document.querySelector('#plans .plans-grid')) & 4") > 0)
    check("Plans: the pill is 'Diwali offer · ends <real date>'",
          f"Diwali offer · ends {short}" in banner.inner_text(), banner.inner_text())
    check("Plans: the sentence carries the real date and the time",
          f"Diwali offer prices are valid until {long}, 11:59 PM IST. Regular prices apply after that." in " ".join(banner.inner_text().split()),
          banner.inner_text())
    bad = []
    for sku in PICKS:
        c = pg.page.locator(f'#plans .plan[data-plans="{sku}"]')
        p = api[sku]
        t = card_text(c)
        was = c.locator("s.was").first.inner_text().replace("Regular price", "").strip()
        if was != money(p["list_amount_paise"]):
            bad.append((sku, "was", was))
        if money(p["amount_paise"]) not in c.locator(".plan-price").inner_text():
            bad.append((sku, "price"))
        if f"Save {save_pct(p)}%" not in t:
            bad.append((sku, "badge", t))
        if f"Regular price {money(p['list_amount_paise'])}, now {money(p['amount_paise'])}" not in t:
            bad.append((sku, "a11y", t))
    check("Plans: each card strikes the API's regular price, shows the current one, Save N%, screen-reader text",
          not bad, str(bad))
    q10 = card_text(pg.page.locator('#plans .plan[data-plans="q10"]'))
    check("Plans: the per-question line strikes the regular per-question price too",
          f"₹{api['q10']['list_per_question']:.2f}" in q10 and f"₹{api['q10']['per_question']:.2f} per question" in q10, q10)
    hw = card_text(pg.page.locator("#plans .plan-hw-head"))
    check("Plans: the hand-written strip shows the strike as well",
          f"Hand-written kundali from Regular price {money(api['k3']['list_amount_paise'])}, now {money(api['k3']['amount_paise'])}" in hw, hw)
    check("Plans: no horizontal scroll at 390px", no_hscroll(pg))
    check("Plans: no countdown or scarcity wording",
          not re.search(r"countdown|left in stock|only \d+ left|hurry", pg.page.inner_text("#plans"), re.I))
    pg.set_lang("hi")
    pg.page.wait_for_timeout(400)
    hb = " ".join(pg.page.locator("#plans .offer-banner").inner_text().split())
    check("Plans in Hindi: label and sentence in Hindi with the real date, ASCII digits",
          "दिवाली ऑफ़र" in hb and f"{ends.day} जनवरी" in hb and f"{ends.day} जनवरी {ends.year}" in hb
          and "(IST)" in hb and "सामान्य कीमतें लागू होंगी" in hb, hb)
    check("Plans in Hindi: the strike is still the API's regular price",
          money(api["q10"]["list_amount_paise"]) in card_text(pg.page.locator('#plans .plan[data-plans="q10"]'))
          and "44% बचत" in card_text(pg.page.locator('#plans .plan[data-plans="q10"]')))
    ctx.close()

    # ---- signed in: store, coupon, offer card, nudge, orders
    ctx = browser.new_context(**PHONE)
    pg = Page(ctx.new_page(), base)
    pg.open_chat(email="e2e-offer-on@example.com", name="Offer On")
    pg.page.evaluate("openStore(false)")
    pg.page.wait_for_selector(".modal.store .pack", timeout=10000)
    check("Store: the banner is the first thing under the title",
          pg.page.evaluate("document.querySelector('.modal.store .modal-body').children[1].id") == "store-offer"
          and pg.page.locator("#store-offer .offer-banner").count() == 1)
    check("Store: the banner states the real date",
          f"valid until {long}, 11:59 PM IST" in " ".join(pg.page.locator("#store-offer").inner_text().split()))
    bad = []
    for sku, p in api.items():
        if p["kind"] in ("kundali_book", "kundali"):
            pg.page.evaluate("document.querySelectorAll('.modal.store details.store-sec').forEach(d => d.open = true)")
        c = pg.page.locator(f'.modal.store .pack[data-sku="{sku}"]')
        t = card_text(c)
        if money(p["list_amount_paise"]) not in c.locator("s.was").first.inner_text():
            bad.append((sku, "was"))
        if f"Save {save_pct(p)}%" not in t:
            bad.append((sku, "badge"))
        if f"Buy {money(p['amount_paise'])}" not in c.locator(".buy-btn").inner_text():
            bad.append((sku, "button", c.locator(".buy-btn").inner_text()))
        if f"Regular price {money(p['list_amount_paise'])}, now {money(p['amount_paise'])}" not in t:
            bad.append((sku, "a11y"))
        if p["kind"] == "questions" and f"₹{p['list_per_question']:.2f}" not in c.locator(".pack-unit").inner_text():
            bad.append((sku, "per-question strike"))
    check("Store: every card strikes the API's regular price, shows Save N%, the Buy button the current price",
          not bad, str(bad))
    check("Store: no horizontal scroll at 390px", no_hscroll(pg))
    small = min(pg.page.evaluate("[...document.querySelectorAll('.modal.store .buy-btn')].map(b => b.getBoundingClientRect().height)"))
    check("Store: every Buy button is at least 44px tall", small >= 43.5, str(small))

    # a coupon works on the effective price and the strike stays on the REGULAR price
    admin = browser.new_context()
    apg = Page(admin.new_page(), base)
    apg.sign_in(email="admin@e2e.test", name="Admin")
    r = apg.page.context.request.post(f"{base}/api/admin/coupons",
                                      data={"code": "DIWALI10", "kind": "percent", "value": 10, "description": "e2e"})
    check("fixture coupon created", r.ok, r.text()[:150])
    admin.close()
    pg.page.evaluate("document.querySelector('.store-sec[data-sec=coupon]').open = true")
    pg.page.fill("#coupon-code", "DIWALI10")
    pg.page.click("#coupon-apply")
    pg.page.wait_for_function("document.querySelector('.pack[data-sku=q10] .pack-unit').textContent.includes('DIWALI10')", timeout=10000)
    c = pg.page.locator('.modal.store .pack[data-sku="q10"]')
    struck = c.locator("s.was").first.inner_text().replace("Regular price", "").strip()
    check("Store + coupon: the strike is the REGULAR price, not the offer price",
          struck == money(api["q10"]["list_amount_paise"]) and "₹99.9" in c.locator(".pack-price").inner_text(),
          c.locator(".pack-price").inner_text())
    check("Store + coupon: the Buy button shows the final price", "₹99.9" in c.locator(".buy-btn").inner_text())
    pg.page.evaluate("document.querySelector('.modal-backdrop')?.remove()")

    # in-app offer card and the low-credits nudge
    pg.page.evaluate("""async () => { offersSeen.clear(); sessionStorage.removeItem('da_offers');
        await maybeOfferAfterAnswer({topic: 'career'}, document.querySelector('#thread .msg.bot')); }""")
    pg.page.wait_for_selector("#thread .offer-card", timeout=5000)
    oc = pg.page.locator("#thread .offer-card").first
    p = api["sq_career"]
    check("Offer card: the button strikes the regular price and shows the current one",
          f"See it for Regular price {money(p['list_amount_paise'])}, now {money(p['amount_paise'])}" in card_text(oc.locator(".offer-go")),
          card_text(oc.locator(".offer-go")))
    check("Offer card: button still >= 44px tall",
          oc.locator(".offer-go").evaluate("e => e.getBoundingClientRect().height") >= 43.5)
    pg.page.evaluate("""async () => { offersSeen.clear(); acct.user.credits = 2;
        document.querySelectorAll('#thread .offer-card').forEach(e => e.remove());
        await maybeOfferAfterAnswer({topic: 'career'}, document.querySelector('#thread .msg.bot')); }""")
    nudge = pg.page.locator('#thread .offer-card[data-offer="low_credits"]')
    nudge.wait_for(timeout=5000)
    q50 = api["q50"]
    nt = card_text(nudge.locator(".offer-text"))
    check("Nudge: '2 left - 50 Questions for <strike regular> <current>'",
          f"2 left — 50 Questions for Regular price {money(q50['list_amount_paise'])}, now {money(q50['amount_paise'])}" in nt, nt)
    check("Nudge: the regular price is struck through (an <s>)", nudge.locator("s.was").count() == 1)
    pg.page.evaluate("acct.user.credits = 10; document.querySelectorAll('#thread .offer-card').forEach(e => e.remove())")

    # Orders: what was charged, no strike
    r = pg.page.context.request.post(f"{base}/api/orders", data={"sku": "q10"})
    check("a test-gateway order is placed at the offer price", r.ok and r.json()["order"]["amount"] == api["q10"]["amount_paise"] // 100,
          r.text()[:150])
    pg.page.evaluate("openOrders()")
    pg.page.wait_for_selector(".ord-row", timeout=10000)
    ot = pg.page.inner_text(".modal")
    check("Orders: shows what was charged, with no strike, label or badge",
          money(api["q10"]["amount_paise"]) in ot and pg.page.locator(".modal s").count() == 0
          and not any(w in ot for w in INK), ot[:200])
    ctx.close()

    # ---- 320 and 390 layouts
    for name, args in (("320px", SMALL), ("390px", PHONE)):
        ctx = browser.new_context(**args)
        pg = Page(ctx.new_page(), base)
        pg.open_chat(email=f"e2e-offer-{name}@example.com", name="Layout")
        pg.page.wait_for_selector("#plans:not([hidden])", state="attached")
        pg.page.evaluate("openStore(false)")
        pg.page.wait_for_selector(".modal.store .pack", timeout=10000)
        pg.page.evaluate("document.querySelectorAll('.modal.store details.store-sec').forEach(d => d.open = true)")
        check(f"[{name}] store: no horizontal scroll", no_hscroll(pg))
        over = pg.page.evaluate("""() => { const m = document.querySelector('.modal.store').getBoundingClientRect();
            return [...document.querySelectorAll('.modal.store .pack *')].filter(e => {
              const r = e.getBoundingClientRect(); return r.width && (r.right > m.right + 0.5 || r.left < m.left - 0.5); }).length; }""")
        check(f"[{name}] store: nothing in a card pokes outside the sheet", over == 0, str(over))
        hs = pg.page.evaluate("[...document.querySelectorAll('.modal.store .buy-btn')].map(b => b.getBoundingClientRect().height)")
        check(f"[{name}] store: all {len(hs)} Buy buttons >= 44px", min(hs) >= 43.5, str(min(hs)))
        clip = pg.page.evaluate("""() => [...document.querySelectorAll('.modal.store .pack-price, .modal.store .pack-price *')]
            .filter(e => !e.closest('.sr-only') && !e.classList.contains('sr-only') && e.scrollWidth > e.clientWidth + 1 && getComputedStyle(e).overflow !== 'visible').length""")
        check(f"[{name}] store: no price is clipped", clip == 0, str(clip))
        pg.page.evaluate("document.querySelector('.modal-backdrop')?.remove()")
        check(f"[{name}] home: no horizontal scroll", no_hscroll(pg))
        ctx.close()
    ctx = browser.new_context(**DESKTOP)
    pg = Page(ctx.new_page(), base)
    pg.open_home()
    pg.page.wait_for_selector("#plans:not([hidden]) .plan", timeout=10000)
    check("[1440px] home Plans: banner and strikes present, no horizontal scroll",
          pg.page.locator("#plans .offer-banner").count() == 1 and pg.page.locator("#plans .plan-price s.was").count() == 4 and no_hscroll(pg))
    ctx.close()


def store_refetches(browser, base: str) -> None:
    print("\n[b. opening the store re-reads /api/products: a stale page shows the regular price after the end]")
    ctx = browser.new_context(**PHONE)
    pg = Page(ctx.new_page(), base)
    pg.open_chat(email="e2e-offer-refetch@example.com", name="Refetch")
    check("before: Plans show the offer", pg.page.locator("#plans .plan-price s.was").count() == 4)
    state = {"ended": False, "calls": 0}

    def turn_off(route):
        state["calls"] += 1
        resp = route.fetch()
        data = resp.json()
        if state["ended"]:                       # what the server answers after the end instant
            for p in data["products"]:
                p["amount_paise"] = billing.LIST_PRICES_PAISE[p["sku"]]
                p["rupees"] = p["amount_paise"] // 100
                p["per_question"] = round(p["rupees"] / p["credits"], 2) if p["credits"] else None
                p["list_amount_paise"] = None
                p["list_per_question"] = None
                p["offer"] = {"active": False, "name": "Diwali offer", "ends_at": None}
        route.fulfill(response=resp, body=json.dumps(data),
                      headers={**resp.headers, "content-length": str(len(json.dumps(data).encode()))})

    pg.page.route("**/api/products", turn_off)
    state["ended"] = True                        # the offer ended while the page stayed open
    pg.page.evaluate("openStore(false)")
    pg.page.wait_for_selector(".modal.store .pack", timeout=10000)
    pg.page.wait_for_function("!document.querySelector('.modal.store .offer-banner')", timeout=10000)
    check("the store asked the server again when it opened", state["calls"] >= 1, str(state))
    t = pg.page.inner_text(".modal.store")
    check("after: no banner, no strike, no badge in the store", pg.page.locator(".modal.store s").count() == 0
          and pg.page.locator(".modal.store .save-badge").count() == 0 and not any(w in t for w in INK), t[:200])
    check("after: the Career report's button shows the regular price",
          f"Buy {money(billing.LIST_PRICES_PAISE['sq_career'])}" in pg.page.locator('.buy-btn[data-sku="sq_career"]').inner_text())
    check("after: the Plans section behind it dropped the offer too", pg.page.locator("#plans .offer-banner").count() == 0
          and pg.page.locator("#plans s.was").count() == 0)
    ctx.close()


def offer_off(browser, base: str) -> None:
    print("\n[c. offer OFF (after the end date): nothing of it, regular prices]")
    ctx = browser.new_context(**PHONE)
    pg = Page(ctx.new_page(), base)
    pg.open_home()
    pg.page.wait_for_selector("#plans:not([hidden]) .plan", timeout=10000)
    api = products(pg)
    check("the API: offer inactive, no list price, amount = regular price",
          all(not p["offer"]["active"] and p["list_amount_paise"] is None and p["offer"]["ends_at"] is None
              and p["amount_paise"] == billing.LIST_PRICES_PAISE[p["sku"]] for p in api.values()))
    plans = pg.page.inner_text("#plans")
    check("Plans: no banner, strike, badge or label",
          pg.page.locator("#plans .offer-banner, #plans s, #plans .save-badge, #plans .offer-pill").count() == 0
          and not any(w in plans for w in INK), plans[:200])
    check("Plans: the plain regular prices",
          all(money(billing.LIST_PRICES_PAISE[s]) in pg.page.locator(f'#plans .plan[data-plans="{s}"] .plan-price').inner_text()
              for s in PICKS))
    check("Plans: no sr-only price words either", "Regular price" not in pg.page.locator("#plans").evaluate("e => e.textContent"))
    pg.set_lang("hi")
    pg.page.wait_for_timeout(300)
    check("Plans in Hindi: none either", pg.page.locator("#plans .offer-banner, #plans s, #plans .save-badge").count() == 0)
    ctx.close()

    ctx = browser.new_context(**PHONE)
    pg = Page(ctx.new_page(), base)
    pg.open_chat(email="e2e-offer-off@example.com", name="Offer Off")
    pg.page.evaluate("openStore(false)")
    pg.page.wait_for_selector(".modal.store .pack", timeout=10000)
    pg.page.evaluate("document.querySelectorAll('.modal.store details.store-sec').forEach(d => d.open = true)")
    t = pg.page.locator(".modal.store").evaluate("e => e.textContent")
    check("Store: no banner, strike, badge, label or screen-reader price words",
          pg.page.locator(".modal.store .offer-banner, .modal.store s, .modal.store .save-badge").count() == 0
          and not any(w in t for w in INK), "")
    bad = [s for s in api if f"Buy {money(billing.LIST_PRICES_PAISE[s])}" not in pg.page.locator(f'.buy-btn[data-sku="{s}"]').inner_text()]
    check("Store: every Buy button shows the regular price", not bad, str(bad))
    check("Store: no horizontal scroll", no_hscroll(pg))
    pg.page.evaluate("document.querySelector('.modal-backdrop')?.remove()")
    pg.page.evaluate("""async () => { offersSeen.clear(); sessionStorage.removeItem('da_offers');
        await maybeOfferAfterAnswer({topic: 'career'}, document.querySelector('#thread .msg.bot')); }""")
    pg.page.wait_for_selector("#thread .offer-card", timeout=5000)
    oc = card_text(pg.page.locator("#thread .offer-card").first)
    check("Offer card: 'See it for ₹199', no strike", f"See it for {money(billing.LIST_PRICES_PAISE['sq_career'])}" in oc
          and pg.page.locator("#thread .offer-card s").count() == 0 and "Regular price" not in oc, oc)
    pg.page.evaluate("""async () => { offersSeen.clear(); acct.user.credits = 2;
        document.querySelectorAll('#thread .offer-card').forEach(e => e.remove());
        await maybeOfferAfterAnswer({topic: 'career'}, document.querySelector('#thread .msg.bot')); }""")
    nudge = card_text(pg.page.locator('#thread .offer-card[data-offer="low_credits"] .offer-text'))
    check("Nudge: '2 left — 50 Questions for ₹599', no strike",
          f"2 left — 50 Questions for {money(billing.LIST_PRICES_PAISE['q50'])}" == nudge, nudge)
    pg.page.goto(base + "/pricing")
    check("/pricing: no banner, no strike", pg.page.locator(".pr-offer, .pr-table s, #diwali-offer").count() == 0)
    check("/pricing: regular prices", f"<b>{money(billing.LIST_PRICES_PAISE['q10'])}</b>" in pg.page.content())
    ctx.close()


def main() -> int:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        with server({"ASTRO_OFFER_ENDS": ENDS_ENV}) as base:
            offer_on(browser, base)
            store_refetches(browser, base)
        with server({"ASTRO_OFFER_OFF": "1", "ASTRO_OFFER_ENDS": ENDS_ENV}) as base:
            offer_off(browser, base)
    return check.finish("the Diwali offer on screen (ON, store re-read, OFF)")


if __name__ == "__main__":
    raise SystemExit(main())
