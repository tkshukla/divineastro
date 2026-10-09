"""The purchase funnel (DIVASTRO-149): prices on the home screen, offers while a
signed-in user is engaged, and the reordered, shorter store.

  a. a signed-out visitor sees the Plans section with the store's real prices and
     a link to /pricing
  b. after an answer a signed-in user sees the report matching the topic, can
     dismiss it, and tapping it opens the store focused on that product; once per
     product per session
  c. the store lists the reports first, is far shorter than before on a phone,
     and carries the trust line and the refund link
  d. the 'few questions left' nudge appears at 3 left, once
  e. nothing is offered to a signed-out visitor after a blocked question, nor at
     0 questions left

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.e2e.test_purchase_funnel
"""

from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from playwright.sync_api import sync_playwright  # noqa: E402

from tests.e2e.harness import BIRTH, DESKTOPS, Checker, Page, server  # noqa: E402

check = Checker()

PHONE = {"viewport": {"width": 390, "height": 844}, "is_mobile": True, "has_touch": True,
         "device_scale_factor": 2}
# Before this change the store was 3178px tall at 390x844 (first two sections ended at ~1660px).
OLD_STORE_HEIGHT = 3178


def money(r: int) -> str:
    return f"₹{r:,}"


def track(pg: Page) -> list[dict]:
    events: list[dict] = []

    def on_request(req):
        if req.url.endswith("/api/event") and req.post_data:
            try:
                events.append(json.loads(req.post_data))
            except ValueError:
                pass
    pg.page.on("request", on_request)
    return events


def ask(pg: Page, text: str) -> None:
    n = pg.page.locator("#thread .msg.bot").count()
    pg.page.fill("#q", text)
    pg.page.click("#send")
    pg.page.wait_for_function(
        "(n) => document.querySelectorAll('#thread .msg.bot').length > n", arg=n, timeout=30000)
    pg.page.wait_for_function("() => document.querySelector('#stop').hidden", timeout=30000)
    pg.page.wait_for_timeout(500)


def adjust_credits(browser, base: str, uid: int, delta: int) -> None:
    ctx = browser.new_context()
    admin = Page(ctx.new_page(), base)
    admin.sign_in(email="admin@e2e.test", name="Admin")
    r = admin.page.context.request.post(f"{base}/api/admin/users/{uid}/credits",
                                        data={"delta": delta, "note": "e2e"})
    ctx.close()
    assert r.ok, r.text()


def plans_signed_out(browser, base: str) -> None:
    print("\n[a. signed-out home shows the Plans section with real prices]")
    with urllib.request.urlopen(f"{base}/api/products") as r:
        products = {p["sku"]: p for p in json.loads(r.read())["products"]}
    for name, ctxargs in (("desktop", DESKTOPS["desktop_1440x800"]), ("phone 390", PHONE)):
        ctx = browser.new_context(**ctxargs)
        pg = Page(ctx.new_page(), base)
        events = track(pg)
        pg.open_home()
        pg.page.wait_for_selector("#plans:not([hidden]) .plan", timeout=10000)
        cards = pg.page.eval_on_selector_all(
            "#plans .plan", "els => els.map(e => ({sku: e.dataset.plans, text: e.innerText, href: e.getAttribute('href')}))")
        check(f"[{name}] 3-4 plan cards", 3 <= len(cards) <= 4, str(len(cards)))
        check(f"[{name}] every card shows the catalogue price",
              all(money(products[c["sku"]]["rupees"]) in c["text"] for c in cards),
              str([(c["sku"], c["text"][:40]) for c in cards]))
        check(f"[{name}] includes the ₹111 report, a pack and the Life Book",
              {"sq_career", "q50", "life_book"} <= {c["sku"] for c in cards})
        check(f"[{name}] the 50-question pack carries 'Most popular'",
              "most popular" in pg.page.locator('#plans .plan[data-plans="q50"]').inner_text().lower())
        check(f"[{name}] cards link to /pricing", all(c["href"].startswith("/pricing#") for c in cards))
        check(f"[{name}] a 'See all plans' link to /pricing",
              pg.page.get_attribute("#plans .plans-all", "href") == "/pricing")
        check(f"[{name}] the free note uses the server's number",
              "10 questions are free" in pg.page.locator("#plans .plans-free").inner_text())
        check(f"[{name}] no horizontal scroll",
              pg.page.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1"))
        pg.page.locator("#plans").scroll_into_view_if_needed()
        pg.page.wait_for_timeout(800)
        check(f"[{name}] 'pricing_view home' is reported once the section is on screen",
              any(e.get("name") == "pricing_view" and e.get("detail") == "home" for e in events), str(events))
        low = min(p["rupees"] for p in products.values() if p["kind"] == "kundali")
        hw = pg.page.locator("#plans a.plan-hw")
        hw_text = hw.inner_text()
        check(f"[{name}] hand-written strip shows the lowest k* price ({money(low)})",
              money(low) in hw_text and "Ravan Samhita, Lal Kitab and Jataka Parijata" in hw_text
              and "hand" in hw_text.lower(), hw_text)
        check(f"[{name}] the strip links to /pricing#handwritten",
              hw.get_attribute("href") == "/pricing#handwritten")
        box = hw.bounding_box()
        check(f"[{name}] the strip is a tap target of at least 44px", box and box["height"] >= 44, str(box))
        check(f"[{name}] the strip does not overflow", box and box["x"] >= 0 and box["x"] + box["width"] <= ctxargs["viewport"]["width"] + 1, str(box))
        hw.click()
        pg.page.wait_for_url("**/pricing#handwritten")
        check(f"[{name}] the strip opens the hand-written section of /pricing",
              pg.page.locator("h2#handwritten").count() == 1 and
              "Ravan Samhita" in pg.page.locator("h2#handwritten ~ p").first.inner_text() + pg.page.locator("h2#handwritten ~ p").nth(1).inner_text())
        check(f"[{name}] 'plans_click handwritten' is reported",
              any(e.get("name") == "plans_click" and e.get("detail") == "handwritten" for e in events), str(events))
        pg.page.go_back()
        pg.page.wait_for_selector("#plans:not([hidden]) .plan", timeout=10000)
        pg.page.click("#plans .plans-all")
        pg.page.wait_for_url("**/pricing")
        check(f"[{name}] 'See all plans' opens the pricing page", "Divine Astro prices" in pg.page.inner_text("h1"))
        check(f"[{name}] no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
        ctx.close()

    ctx = browser.new_context(**PHONE)
    pg = Page(ctx.new_page(), base)
    events = track(pg)
    pg.page.goto(base + "/pricing")
    pg.page.wait_for_timeout(500)
    check("/pricing reports pricing_view page",
          any(e.get("name") == "pricing_view" and e.get("detail") == "page" for e in events), str(events))
    check("/pricing has no horizontal scroll at 390px",
          pg.page.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1"))
    pg.page.click("#pricing-cta")
    pg.page.wait_for_timeout(500)
    pg.page.wait_for_selector("#stage-birth.active", timeout=10000)
    check("'Start free' leads into the app's birth form", pg.page.locator("#stage-birth.active").count() == 1,
          pg.page.url)
    ctx.close()


def offers_after_answer(browser, base: str) -> None:
    print("\n[b. the matching report is offered after an answer; dismiss; tap opens the store on it]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    events = track(pg)
    pg.open_chat(email="e2e-offer@example.com", name="Offer Tester")
    price = lambda sku: pg.page.evaluate(f"productBySku('{sku}').rupees")      # noqa: E731

    check("no offer is on screen before any answer", pg.page.locator("#thread .offer-card").count() == 0)
    ask(pg, "Will I get a promotion in my career this year?")
    pg.page.wait_for_selector("#thread .offer-card", timeout=10000)
    card = pg.page.locator("#thread .offer-card").first
    check("a career question gets the Career report", card.get_attribute("data-offer") == "sq_career",
          card.get_attribute("data-offer"))
    check("the card shows the catalogue price", money(price("sq_career")) in card.inner_text(), card.inner_text())
    check("the card names the report", "Career & Profession Report" in card.inner_text())
    check("it sits under the answer, inside the thread",
          pg.page.evaluate("document.querySelector('#thread .offer-card').previousElementSibling.classList.contains('msg')"))
    check("'offer_shown sq_career' is reported",
          {"name": "offer_shown", "detail": "sq_career"} in events, str(events))
    pg.page.click("#thread .offer-x")
    check("it can be dismissed", pg.page.locator("#thread .offer-card").count() == 0)
    ask(pg, "Is my career going to change soon?")
    pg.page.wait_for_timeout(500)
    check("the same report is not offered twice in a session", pg.page.locator("#thread .offer-card").count() == 0)

    ask(pg, "What does my marriage look like?")
    pg.page.wait_for_selector("#thread .offer-card", timeout=10000)
    check("a marriage question gets the Marriage report",
          pg.page.locator("#thread .offer-card").first.get_attribute("data-offer") == "sq_marriage_timing")
    pg.page.click("#thread .offer-go")
    pg.page.wait_for_selector(".modal.store .pack.focus", timeout=10000)
    check("tapping it opens the store focused on that product",
          pg.page.get_attribute(".modal.store .pack.focus", "data-sku") == "sq_marriage_timing")
    check("the focused product is on screen",
          pg.page.evaluate("""() => { const r = document.querySelector('.pack.focus').getBoundingClientRect();
                                      return r.top >= 0 && r.bottom <= window.innerHeight; }"""))
    check("'offer_click sq_marriage_timing' is reported",
          {"name": "offer_click", "detail": "sq_marriage_timing"} in events, str(events))
    pg.page.keyboard.press("Escape")
    pg.page.click(".modal-x")

    ask(pg, "Will I travel abroad for work or settle overseas?")
    pg.page.wait_for_timeout(500)
    check("the Life Book was already offered on the dashboard, so not again (once per product per session)",
          pg.page.locator("#thread .offer-card").count() == 0)
    pg.page.evaluate("offersSeen.delete('life_book'); sessionStorage.removeItem('da_offers')")
    ask(pg, "Will I travel abroad for work or settle overseas?")
    pg.page.wait_for_selector("#thread .offer-card", timeout=10000)
    check("any other topic gets the Life Book",
          pg.page.locator("#thread .offer-card").last.get_attribute("data-offer") == "life_book")
    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    ctx.close()

    print("\n[b2. the Life Book line on the dashboard]")
    ctx = browser.new_context(**PHONE)
    pg = Page(ctx.new_page(), base)
    events = track(pg)
    pg.sign_in(email="e2e-dash@example.com", name="Dash Tester")
    pg.open_home()
    pg.page.evaluate("async (b) => { await castChart(b); }", BIRTH)
    pg.page.wait_for_selector("#dash-offer .offer-card", timeout=15000)
    check("the dashboard offers the Life Book once",
          pg.page.get_attribute("#dash-offer .offer-card", "data-offer") == "life_book_dashboard")
    check("'offer_shown life_book_dashboard' is reported",
          {"name": "offer_shown", "detail": "life_book_dashboard"} in events, str(events))
    pg.page.click("#dash-offer .offer-x")
    check("it dismisses", pg.page.locator("#dash-offer .offer-card").count() == 0)
    pg.page.evaluate("loadAndShowDashboard()")
    pg.page.wait_for_timeout(1200)
    check("and does not come back in the same session", pg.page.locator("#dash-offer .offer-card").count() == 0)
    ctx.close()


def store_layout(browser, base: str) -> None:
    print("\n[c. the store: reports first, much shorter on a phone, trust line and refund link]")
    ctx = browser.new_context(**PHONE)
    pg = Page(ctx.new_page(), base)
    pg.sign_in(email="e2e-layout@example.com", name="Layout Tester")
    pg.open_home()
    pg.page.wait_for_timeout(600)
    pg.page.evaluate("openStore()")
    pg.page.wait_for_selector(".modal.store .pack")
    order = pg.page.eval_on_selector_all(".modal.store .store-sec", "els => els.map(e => e.dataset.sec)")
    check("sections: reports, packs, Life Book, hand-written kundali, coupon",
          order == ["single_question", "questions", "kundali_book", "kundali", "coupon"], str(order))
    first_skus = pg.page.eval_on_selector_all(".modal.store .pack", "els => els.slice(0, 3).map(e => e.dataset.sku)")
    check("the three ₹111 reports come first",
          first_skus == ["sq_career", "sq_marriage_timing", "sq_wealth_business"], str(first_skus))
    state = pg.page.eval_on_selector_all(".modal.store .store-sec", "els => els.map(e => e.open)")
    check("the first two sections are open, the rest folded", state == [True, True, False, False, False], str(state))
    m = pg.page.evaluate("""() => { const modal = document.querySelector('.modal');
        const top = modal.getBoundingClientRect().top;
        const end = (s) => document.querySelector('.store-sec[data-sec=' + s + ']').getBoundingClientRect().bottom - top + modal.scrollTop;
        return {total: modal.scrollHeight, firstTwo: end('questions'), view: window.innerHeight}; }""")
    check(f"the first two sections fit in 1.5 screens ({m['firstTwo']:.0f}px <= {1.5 * m['view']:.0f}px)",
          m["firstTwo"] <= 1.5 * m["view"])
    check(f"the whole store is less than half its old height ({m['total']}px vs {OLD_STORE_HEIGHT}px)",
          m["total"] < OLD_STORE_HEIGHT / 2)
    trust = pg.page.locator(".modal.store .store-trust")
    check("there is a trust line under the title", trust.count() == 1)
    check("with a link to the refund policy", trust.locator('a[href="/refund"]').count() == 1)
    check("and the terms", trust.locator('a[href="/terms"]').count() == 1)
    check("the test-mode banner is still shown (test gateway)", pg.page.locator(".modal.store .test-banner").count() == 1)
    check("every pack card has a concrete 'what you get' line",
          pg.page.evaluate("[...document.querySelectorAll('.modal.store .pack-blurb')].every(e => e.textContent.trim().length > 20)"))
    check("the 50-question pack is the only 'Most popular'",
          pg.page.eval_on_selector_all(".modal.store .pack-flag", "els => els.map(e => e.closest('.pack').dataset.sku)") == ["q50"])
    pg.page.click('.store-sec[data-sec="kundali_book"] > summary')
    check("a folded section opens on tap", pg.page.locator('.pack[data-sku="life_book"] .buy-btn').is_visible())
    check("no horizontal scroll in the sheet",
          pg.page.evaluate("document.querySelector('.modal').scrollWidth <= document.querySelector('.modal').clientWidth + 1"))
    pg.page.click(".modal-x")

    pg.page.evaluate("openStore(false, 'k5')")
    pg.page.wait_for_selector(".modal.store .pack.focus", timeout=5000)
    check("focusSku opens a folded section and highlights the product",
          pg.page.evaluate("document.querySelector('.pack.focus').closest('details').open")
          and pg.page.get_attribute(".pack.focus", "data-sku") == "k5")
    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    ctx.close()


def low_credits(browser, base: str) -> None:
    print("\n[d. the 'few questions left' nudge at 3 left, once]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    events = track(pg)
    pg.open_chat(email="e2e-low@example.com", name="Low Tester")
    uid = pg.page.evaluate("acct.user.id")
    adjust_credits(browser, base, uid, -(pg.page.evaluate("acct.user.credits") - 5))
    pg.page.evaluate("acct.user.credits = 5")
    ask(pg, "Tell me about my health")                      # 4 left: not yet
    check("no nudge at 4 left", pg.page.locator('#thread .offer-card[data-offer="low_credits"]').count() == 0)
    pg.page.evaluate("document.querySelectorAll('#thread .offer-card').forEach(e => e.remove())")
    ask(pg, "And what about my finances?")                  # 3 left
    pg.page.wait_for_selector('#thread .offer-card[data-offer="low_credits"]', timeout=10000)
    text = pg.page.locator('#thread .offer-card[data-offer="low_credits"]').inner_text()
    pack = pg.page.evaluate("productBySku('q50')")
    check("it says 3 left and quotes the 50-question pack at its catalogue price",
          "3 left" in text and "50 Questions" in text and money(pack["rupees"]) in text, text)
    check("'offer_shown low_credits' is reported", {"name": "offer_shown", "detail": "low_credits"} in events)
    pg.page.click('#thread .offer-card[data-offer="low_credits"] .offer-go')
    pg.page.wait_for_selector(".modal.store .pack.focus", timeout=10000)
    check("it opens the store on the 50-question pack", pg.page.get_attribute(".pack.focus", "data-sku") == "q50")
    check("'offer_click low_credits' is reported", {"name": "offer_click", "detail": "low_credits"} in events)
    pg.page.click(".modal-x")
    ask(pg, "Any advice on property?")                      # 2 left
    pg.page.wait_for_timeout(500)
    check("the nudge is not repeated in the same session",
          pg.page.locator('#thread .offer-card[data-offer="low_credits"]').count() == 0)
    ctx.close()


def nothing_when_blocked(browser, base: str) -> None:
    print("\n[e. nothing for a signed-out visitor, nothing at 0 left]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    events = track(pg)
    pg.open_home()
    pg.page.evaluate("async (b) => { await castChart(b); showStage('stage-chat'); }", BIRTH)
    pg.page.wait_for_selector("#thread .msg.bot", timeout=30000)
    pg.page.evaluate("state.provider = 'off'")
    pg.page.fill("#q", "Will I get a promotion in my career?")
    pg.page.click("#send")
    pg.page.wait_for_selector(".modal-backdrop", timeout=10000)
    check("a blocked question opens the sign-in sheet", pg.page.locator(".modal-backdrop").count() == 1)
    check("no offer card anywhere", pg.page.locator(".offer-card").count() == 0)
    check("the sheet shows no price or product",
          "₹" not in pg.page.locator(".modal-backdrop").inner_text())
    check("no offer events were reported",
          not [e for e in events if e.get("name") in ("offer_shown", "offer_click")], str(events))
    ctx.close()

    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    events = track(pg)
    pg.open_chat(email="e2e-zero@example.com", name="Zero Tester")
    uid = pg.page.evaluate("acct.user.id")
    adjust_credits(browser, base, uid, -(pg.page.evaluate("acct.user.credits") - 1))
    pg.page.evaluate("acct.user.credits = 1")
    shown_before = len([e for e in events if e.get("name") == "offer_shown"])
    ask(pg, "Will I get a promotion in my career?")         # the last question: 0 left
    pg.page.wait_for_timeout(800)
    check("at 0 left no offer card is added under the answer", pg.page.locator("#thread .offer-card").count() == 0)
    ask_n = pg.page.locator("#thread .msg.bot").count()
    pg.page.fill("#q", "One more?")
    pg.page.click("#send")
    pg.page.wait_for_selector(".modal.store", timeout=10000)
    check("the paywall still opens the store by itself", pg.page.locator(".modal.store").count() == 1 and ask_n > 0)
    check("and no offer was reported at 0 left",
          len([e for e in events if e.get("name") == "offer_shown"]) == shown_before, str(events))
    ctx.close()


def main() -> int:
    with server() as base, sync_playwright() as p:
        browser = p.chromium.launch()
        plans_signed_out(browser, base)
        offers_after_answer(browser, base)
        store_layout(browser, base)
        low_credits(browser, base)
        nothing_when_blocked(browser, base)
    return check.finish("purchase funnel (plans, offers, store, low credits)")


if __name__ == "__main__":
    raise SystemExit(main())
