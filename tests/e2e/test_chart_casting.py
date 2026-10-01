"""Casting a chart: place search, "don't know the time", and validation
errors (DIVASTRO-72, flow 3). Exercises the real birth-entry form, not the
castChart() JS shortcut other tests use to skip straight to a cast chart.

Needs the offline city database (tools/fetch_data.py) since it drives real
place-search autocomplete, unlike every other e2e test so far.

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.e2e.test_chart_casting
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from playwright.sync_api import sync_playwright  # noqa: E402

from tests.e2e.harness import Checker, DESKTOPS, Page, server  # noqa: E402

check = Checker()


def open_birth_form(pg: Page) -> None:
    pg.open_home()
    pg.sign_in()
    pg.page.reload(wait_until="domcontentloaded")
    pg.page.wait_for_function("typeof showStage === 'function'")
    pg.page.click("#home-cta")
    pg.page.wait_for_selector("#birth-form", state="visible")


def validation_without_a_place(p, browser, base: str) -> None:
    print("\n[submitting without picking a place shows an inline error, not a silent no-op]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    open_birth_form(pg)

    pg.page.fill("#f-date", "1990-03-12")
    pg.page.fill("#f-time", "09:30")
    # #f-place has the native `required` attribute, which would block the
    # form's submit event (and a browser-native tooltip, not the app's own
    # #birth-error) before the JS handler ever runs if left empty. Typing
    # text but not picking a suggestion satisfies `required` while still
    # leaving state.place unset — the actual app-level validation case.
    pg.page.fill("#f-place", "Nowhere I Will Pick")
    check("the error line starts hidden", pg.page.locator("#birth-error").is_hidden())
    pg.page.click("#cast")
    pg.page.wait_for_timeout(300)
    check("an inline error appears when no place was chosen",
          pg.page.locator("#birth-error").is_visible())
    check("the page did not navigate away to a chart", pg.page.locator("#birth-form").is_visible())

    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    check("no CSP violations", not pg.csp_violations(), str(pg.csp_violations()[:2]))
    ctx.close()


def place_search_and_cast(p, browser, base: str) -> None:
    print("\n[real place-search autocomplete, then a successful cast]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    open_birth_form(pg)

    pg.page.fill("#f-date", "1990-03-12")
    pg.page.fill("#f-time", "09:30")
    pg.page.fill("#f-place", "Delhi")
    pg.page.wait_for_selector("#place-results li", timeout=10000)
    results = pg.page.locator("#place-results li")
    check("typing a real city returns real suggestions", results.count() > 0,
          f"{results.count()} results")

    results.first.click()
    check("picking a suggestion fills the place field", "Delhi" in pg.page.input_value("#f-place"))
    check("picking a suggestion shows the resolved place line",
          pg.page.locator("#place-chosen").is_visible())

    pg.page.click("#cast")
    pg.page.wait_for_selector("#stage-dashboard, #stage-chat", state="visible", timeout=15000)
    check("a valid submission actually casts the chart (leaves the form)",
          not pg.page.locator("#birth-form").is_visible())

    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    check("no CSP violations", not pg.csp_violations(), str(pg.csp_violations()[:2]))
    ctx.close()


def unknown_birth_time(p, browser, base: str) -> None:
    print("\n[\"don't know the time\" disables the time field and still casts a chart]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    open_birth_form(pg)

    pg.page.fill("#f-date", "1990-03-12")
    pg.page.check("#f-unknown")
    check("checking 'unknown time' disables the time field",
          pg.page.eval_on_selector("#f-time", "e => e.disabled") is True)
    check("the time field is reset to midday when unknown",
          pg.page.input_value("#f-time") == "12:00")

    pg.page.fill("#f-place", "Mumbai")
    pg.page.wait_for_selector("#place-results li", timeout=10000)
    pg.page.locator("#place-results li").first.click()

    requests: list[str] = []
    pg.page.on("request", lambda r: requests.append(r.post_data or "")
               if r.url.endswith("/api/chart") and r.method == "POST" else None)
    pg.page.click("#cast")
    pg.page.wait_for_selector("#stage-dashboard, #stage-chat", state="visible", timeout=15000)
    check("the chart request told the server the time is unknown (time_known: false)",
          len(requests) == 1 and '"time_known":false' in requests[0],
          str(requests))

    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    check("no CSP violations", not pg.csp_violations(), str(pg.csp_violations()[:2]))
    ctx.close()


def main() -> int:
    with server() as base, sync_playwright() as p:
        browser = p.chromium.launch()
        validation_without_a_place(p, browser, base)
        place_search_and_cast(p, browser, base)
        unknown_birth_time(p, browser, base)
        browser.close()
    return check.finish("chart casting (place search, unknown time, validation)")


if __name__ == "__main__":
    raise SystemExit(main())
