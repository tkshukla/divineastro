"""The ₹51 detailed Kundali Milan report (DIVASTRO-156), in a real browser.

  a. under an in-app match result: the card (title, guna by guna / Manglik /
     compatibility, ₹51 with the struck ₹91 while the offer is live, a sample link);
     milan_report_shown is reported
  b. card -> checkout: Buy sends BOTH people on the order, the test gateway confirms,
     the ready sheet downloads a real PDF for that pair; My orders lists it with the
     pair's names and downloads it again
  c. signed out: Buy opens sign-in first
  d. Hindi: the card in Hindi
  e. a 390px phone: the card fits, no sideways scroll
  f. the store: with a match on screen the report is bought for it; with none the
     button opens Kundali Milan
  g. the public /kundali-milan card: price from the catalogue, its button opens the
     app's matching tool, and milan_report_click is reported

    python -u -m tests.e2e.test_milan_report
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from playwright.sync_api import sync_playwright  # noqa: E402

from tests.e2e.harness import DESKTOPS, Checker, Page, server  # noqa: E402

check = Checker()
PHONE = {"viewport": {"width": 390, "height": 844}, "is_mobile": True, "has_touch": True,
         "device_scale_factor": 2}
GROOM = {"name": "Rohan", "date": "1990-03-12", "time": "09:30", "place": "Delhi"}
BRIDE = {"name": "Priya", "date": "1992-07-20", "time": "14:15", "place": "Mumbai"}
CARD = "#milan-result .milan-rpt"


def fill_side(pg: Page, side: str, person: dict) -> None:
    card = f'.milan-card[data-side="{side}"]'
    pg.page.fill(f'{card} [data-f="name"]', person["name"])
    pg.page.fill(f'{card} [data-f="date"]', person["date"])
    pg.page.fill(f'{card} [data-f="time"]', person["time"])
    pg.page.fill(f'{card} [data-f="place"]', person["place"])
    pg.page.wait_for_selector(f'{card} [data-f="results"] li', timeout=10000)
    pg.page.locator(f'{card} [data-f="results"] li').first.click()


def events(pg: Page) -> list:
    """Every analytics beacon the page sends, as (name, detail)."""
    out: list = []

    def seen(req):
        if req.url.endswith("/api/event"):
            try:
                d = json.loads(req.post_data or "{}")
                out.append((d.get("name"), d.get("detail")))
            except ValueError:
                pass
    pg.page.on("request", seen)
    return out


def match(pg: Page, lang: str | None = None) -> None:
    pg.open_home()
    if lang:
        pg.set_lang(lang)
    pg.page.evaluate("showStage('stage-milan')")
    pg.page.wait_for_selector("#stage-milan", state="visible", timeout=10000)
    fill_side(pg, "groom", GROOM)
    fill_side(pg, "bride", BRIDE)
    pg.page.click("#milan-go")
    pg.page.wait_for_selector(CARD, state="visible", timeout=20000)


def card_and_checkout(browser, base: str) -> None:
    print("\n[a/b. The card under the result -> checkout -> the PDF for that pair]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"], accept_downloads=True)
    pg = Page(ctx.new_page(), base)
    pg.sign_in("milan.e2e@example.com", "Milan Buyer")
    sent = events(pg)
    orders: list = []
    pg.page.on("request", lambda r: orders.append(r.post_data or "")
               if r.url.endswith("/api/orders") and r.method == "POST" else None)
    match(pg)
    text = pg.page.locator(CARD).inner_text()
    check("the card sits under the result", pg.page.locator("#milan-result #milan-report-slot .milan-rpt").count() == 1)
    check("its words: detailed report, guna by guna, Manglik dosh, compatibility",
          "Detailed matching report" in text and "Guna by guna, Manglik dosh, compatibility" in text, text[:200])
    check("₹51 with the struck regular ₹91 (offer live)",
          "₹51" in pg.page.locator(f"{CARD} .mr-price").inner_text()
          and pg.page.locator(f"{CARD} .mr-price s.was").inner_text().strip().endswith("₹91"))
    check("a See a sample link to the sample PDF",
          pg.page.locator(f'{CARD} a[data-sample="milan_report"]').get_attribute("href") == "/samples/milan_report.pdf")
    check("it says where the report goes (My orders and the email)",
          "My orders" in text and "milan.e2e@example.com" in text, text[-160:])
    pg.page.wait_for_timeout(300)
    check("milan_report_shown 'app' is reported", ("milan_report_shown", "app") in sent, str(sent))

    with pg.page.expect_download(timeout=120000) as info:
        pg.page.click(f"{CARD} .buy-btn")
        pg.page.wait_for_selector('.rpt-ready[data-sku="milan_report"]', timeout=30000)
        pg.page.click('.rpt-ready .rpt-dl')
    data = Path(info.value.path()).read_bytes()
    body = json.loads(orders[0]) if orders else {}
    check("the order carries both people as the form had them",
          body.get("sku") == "milan_report" and body.get("milan", {}).get("groom", {}).get("name") == "Rohan"
          and body["milan"]["bride"]["name"] == "Priya" and body["milan"]["bride"].get("latitude"), str(body)[:200])
    check("milan_report_click 'app' is reported", ("milan_report_click", "app") in sent, str(sent))
    check("the ready sheet downloads a real PDF named for the pair",
          data.startswith(b"%PDF-") and "Rohan" in info.value.suggested_filename
          and "Priya" in info.value.suggested_filename, info.value.suggested_filename)
    pg.page.wait_for_selector(".rpt-ready .rpt-msg:not([hidden])", timeout=10000)

    pg.page.click(".rpt-orders-link")
    row = pg.page.locator('.ord-row[data-sku="milan_report"]')
    row.wait_for(timeout=10000)
    check("My orders: the report with the pair's names", "Rohan & Priya" in row.inner_text(), row.inner_text())
    with pg.page.expect_download(timeout=120000) as info2:
        row.locator(".ord-milan").click()
    check("My orders downloads it again", Path(info2.value.path()).read_bytes().startswith(b"%PDF-"))
    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    check("no CSP violations", not pg.csp_violations(), str(pg.csp_violations()[:2]))
    ctx.close()


def signed_out(browser, base: str) -> None:
    print("\n[c. Signed out: Buy opens sign-in first]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    sent = events(pg)
    match(pg)
    check("the card shows to a visitor too", pg.page.locator(f"{CARD} .buy-btn").is_visible())
    pg.page.click(f"{CARD} .buy-btn")
    pg.page.wait_for_selector(".modal-backdrop", timeout=10000)
    pg.page.wait_for_timeout(300)
    check("Buy opens the sign-in sheet (no order is started)",
          ("signin_open", "milan_report") in sent and not any(n == "checkout_start" for n, _ in sent), str(sent))
    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    ctx.close()


def hindi_and_phone(browser, base: str) -> None:
    print("\n[d/e. Hindi, and a 390px phone]")
    ctx = browser.new_context(**PHONE)
    pg = Page(ctx.new_page(), base)
    match(pg, "hi")
    text = pg.page.locator(CARD).inner_text()
    check("Hindi: the card in Hindi", "विस्तृत मिलान रिपोर्ट" in text and "मांगलिक दोष" in text, text[:160])
    check("Hindi: the Hindi sample", pg.page.locator(f'{CARD} a[data-sample]').get_attribute("href")
          == "/samples/milan_report.pdf?lang=hi")
    pg.page.locator(CARD).scroll_into_view_if_needed()
    box = pg.rect(CARD)
    check("phone: the card fits 390px", box and box["left"] >= 0 and box["right"] <= 390, str(box))
    check("phone: no sideways scroll", pg.page.evaluate("document.documentElement.scrollWidth <= innerWidth"))
    btn = pg.rect(f"{CARD} .buy-btn")
    check("phone: the button is at least 44px tall", btn and btn["height"] >= 44, str(btn))
    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    ctx.close()


def store(browser, base: str) -> None:
    print("\n[f. The store]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    pg.sign_in("milan.store@example.com", "Store Visitor")
    pg.open_home()
    pg.page.evaluate("openStore()")
    sec = pg.page.locator('.store-sec[data-sec="milan_report"]')
    sec.wait_for(timeout=10000)
    sec.locator("summary").click()
    pack = pg.page.locator('.pack[data-sku="milan_report"]')
    check("the store lists the report next to the others, with its price",
          pack.count() == 1 and "₹51" in pack.inner_text() and "₹91" in pack.inner_text(), pack.inner_text()[:200])
    check("with no match on screen its Buy sends you to Kundali Milan first",
          pack.locator('.buy-btn[data-open="milan"]').count() == 1 and "enter both birth details" in pack.inner_text())
    pack.locator(".buy-btn").click()
    pg.page.wait_for_selector("#stage-milan", state="visible", timeout=10000)
    check("...which opens the matching screen", pg.page.locator("#stage-milan").is_visible())
    fill_side(pg, "groom", GROOM)
    fill_side(pg, "bride", BRIDE)
    pg.page.click("#milan-go")
    pg.page.wait_for_selector(CARD, state="visible", timeout=20000)
    pg.page.evaluate("openStore()")
    pack = pg.page.locator('.pack[data-sku="milan_report"]')
    pack.wait_for(timeout=10000)
    check("after a match: Buy, for the pair on screen",
          pack.locator(".buy-btn:not([data-open])").count() == 1 and "Rohan & Priya" in pack.inner_text(),
          pack.inner_text()[:200])
    pack.locator(".buy-btn").click()
    pg.page.wait_for_selector('.rpt-ready[data-sku="milan_report"]', timeout=30000)
    check("bought from the store: the ready sheet", True)
    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    ctx.close()


def public_page(browser, base: str) -> None:
    print("\n[g. The public /kundali-milan card]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    sent = events(pg)
    pg.page.goto(base + "/kundali-milan", wait_until="domcontentloaded")
    card = pg.page.locator('[data-milan-report="page"]')
    card.wait_for(timeout=10000)
    t = card.inner_text()
    check("the card: words, ₹51, struck ₹91, a sample", "Detailed matching report" in t and "₹51" in t
          and card.locator("s.was").count() == 1 and card.locator('a[data-sample="milan_report"]').count() == 1, t[:200])
    card.scroll_into_view_if_needed()
    pg.page.wait_for_timeout(500)
    check("milan_report_shown 'page' is reported", ("milan_report_shown", "page") in sent, str(sent))
    card.locator("[data-milan-report-go]").click()
    pg.page.wait_for_selector("#stage-milan", state="visible", timeout=15000)
    check("its button opens the app's matching tool", pg.page.locator("#stage-milan").is_visible())
    check("milan_report_click 'page' is reported", ("milan_report_click", "page") in sent, str(sent))
    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    ctx.close()


def main() -> int:
    with server({"ASTRO_OFFER_ENDS": "2099-01-01T00:00:00+05:30"}) as base, sync_playwright() as p:
        browser = p.chromium.launch()
        card_and_checkout(browser, base)
        signed_out(browser, base)
        hindi_and_phone(browser, base)
        store(browser, base)
        public_page(browser, base)
        browser.close()
    return check.finish("Kundali Milan report (DIVASTRO-156)")


if __name__ == "__main__":
    raise SystemExit(main())
