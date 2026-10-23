"""DIVASTRO-160 in a browser: the Rs 21 Starter at the top of the home Plans section.

  a. Signed out on a 390px phone: the strip is in #plans with ₹21 and "no sign-in
     needed"; it is reported once as starter_shown home; tapping it reports
     starter_click home and opens the pay-without-signing-in sheet.
  b. Signed in (a new account that may still buy it): the strip is there; tapping it
     opens the store on the Starter.
  c. 320px: nothing scrolls sideways.

    python -m tests.e2e.test_home_starter
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from playwright.sync_api import sync_playwright  # noqa: E402

from tests.e2e.harness import Checker, Page, server  # noqa: E402

check = Checker()
STRIP = '#plans [data-plans="starter"]'
_n = [0]


def phone(browser, w: int = 390, h: int = 844):
    _n[0] += 1
    return browser.new_context(viewport={"width": w, "height": h}, is_mobile=True, has_touch=True,
                               user_agent=f"Mozilla/5.0 (Linux; Android 14) Mobile e2e-home-starter-{_n[0]}")


def track(pg: Page) -> list[tuple]:
    events: list[tuple] = []

    def on_request(req):
        if req.url.endswith("/api/event") and req.post_data:
            try:
                d = json.loads(req.post_data)
                events.append((d.get("name"), d.get("detail")))
            except ValueError:
                pass
    pg.page.on("request", on_request)
    return events


def signed_out(browser, base: str) -> None:
    print("\n[a. signed out, 390px]")
    ctx = phone(browser)
    pg = Page(ctx.new_page(), base)
    events = track(pg)
    pg.open_home()
    pg.page.wait_for_selector(STRIP, timeout=20000)
    text = pg.page.locator(STRIP).inner_text()
    check("the Starter strip is in the home Plans section with its price", "₹21" in text, text)
    check("...and says no sign-in is needed", "no sign-in needed" in text, text)
    pg.page.locator(STRIP).scroll_into_view_if_needed()
    pg.page.wait_for_timeout(300)
    check("starter_shown home is reported once", events.count(("starter_shown", "home")) == 1, str(events))
    pg.page.locator(STRIP).click()
    pg.page.wait_for_selector("#gp-email, #gp-chart", timeout=10000)
    check("tapping it opens the pay-without-signing-in sheet", pg.page.locator(".modal.store").count() == 0)
    check("starter_click home is reported", ("starter_click", "home") in events, str(events))
    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    ctx.close()


def signed_in(browser, base: str) -> None:
    print("\n[b. signed in, may still buy it]")
    ctx = phone(browser)
    pg = Page(ctx.new_page(), base)
    pg.sign_in("home-starter@example.com", "Home Starter")
    pg.open_home()
    pg.page.wait_for_function("typeof acct !== 'undefined' && acct.user && acct.products && acct.products.length")
    pg.page.wait_for_selector(STRIP, timeout=20000)
    check("a new account sees the strip too", pg.page.locator(STRIP).count() == 1)
    pg.page.locator(STRIP).click()
    pg.page.wait_for_selector('.modal.store .pack[data-sku="starter_email3"]', timeout=10000)
    check("tapping it opens the store on the Starter",
          pg.page.locator('.modal.store .pack[data-sku="starter_email3"]').count() == 1)
    ctx.close()


def narrow(browser, base: str) -> None:
    print("\n[c. 320px]")
    ctx = phone(browser, 320, 568)
    pg = Page(ctx.new_page(), base)
    pg.open_home()
    pg.page.wait_for_selector(STRIP, timeout=20000)
    check("nothing scrolls sideways", pg.page.evaluate("document.documentElement.scrollWidth <= innerWidth"))
    box = pg.page.locator(STRIP).bounding_box()
    check("the strip fits the screen", box and box["x"] >= 0 and box["x"] + box["width"] <= 320, str(box))
    ctx.close()


def main() -> int:
    with server() as base, sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            signed_out(browser, base)
            signed_in(browser, base)
            narrow(browser, base)
        finally:
            browser.close()
    return check.finish("home Starter")


if __name__ == "__main__":
    sys.exit(main())
