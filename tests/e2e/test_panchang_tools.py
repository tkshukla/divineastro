"""Panchang, Muhurat Finder, and Choghadiya — the three free tool pages
(DIVASTRO-72, flow 8).

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.e2e.test_panchang_tools
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from playwright.sync_api import sync_playwright  # noqa: E402

from tests.e2e.harness import DESKTOPS, Checker, Page, server  # noqa: E402

check = Checker()


def pick_place(pg: Page, input_sel: str, results_sel: str, query: str = "Delhi") -> None:
    pg.page.fill(input_sel, query)
    pg.page.wait_for_selector(f"{results_sel} li", timeout=10000)
    pg.page.locator(f"{results_sel} li").first.click()


def panchang(p, browser, base: str) -> None:
    print("\n[Panchang: loads automatically once a place is picked]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    pg.open_home()
    pg.page.click("#open-panchang")
    pg.page.wait_for_selector("#stage-panchang", state="visible", timeout=10000)

    pick_place(pg, "#pa-place", "#pa-results")
    pg.page.wait_for_selector("#panchang-result .pa-limbs", timeout=15000)
    check("the resolved place line shows", pg.page.locator("#pa-chosen").is_visible())
    limbs_text = pg.page.locator("#panchang-result .pa-limbs").inner_text()
    check("tithi/nakshatra/yoga/karana render with real content", limbs_text.strip() != "",
          limbs_text[:200])
    times_text = pg.page.locator("#panchang-result .pa-times").inner_text()
    check("Rahu Kaal / Abhijit Muhurta times render", times_text.strip() != "", times_text[:200])

    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    check("no CSP violations", not pg.csp_violations(), str(pg.csp_violations()[:2]))
    ctx.close()


def muhurat_finder(p, browser, base: str) -> None:
    print("\n[Muhurat Finder: a date-range search returns a verdict table]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    pg.open_home()
    pg.page.click("#open-muhurat")
    pg.page.wait_for_selector("#stage-muhurat", state="visible", timeout=10000)

    check("the date range is pre-seeded (today .. +30 days)",
          pg.page.input_value("#mu-from") != "" and pg.page.input_value("#mu-to") != "")
    pick_place(pg, "#mu-place", "#mu-results", "Mumbai")
    pg.page.click("#muhurat-go")
    pg.page.wait_for_selector("#muhurat-result table, #muhurat-result tr", timeout=15000)

    rows = pg.page.locator("#muhurat-result tr")
    check("the results table has real rows, not just a header", rows.count() > 1,
          f"{rows.count()} rows")

    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    check("no CSP violations", not pg.csp_violations(), str(pg.csp_violations()[:2]))
    ctx.close()


def choghadiya(p, browser, base: str) -> None:
    print("\n[Choghadiya: day/night slot tables for a chosen date]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    pg.open_home()
    pg.page.click("#open-choghadiya")
    pg.page.wait_for_selector("#stage-choghadiya", state="visible", timeout=10000)

    check("the date is pre-seeded with today", pg.page.input_value("#cho-date") != "")
    pick_place(pg, "#cho-place", "#cho-results", "Delhi")
    pg.page.click("#choghadiya-go")
    pg.page.wait_for_selector("#choghadiya-result table, #choghadiya-result tr", timeout=15000)

    rows = pg.page.locator("#choghadiya-result tr")
    check("day/night slot tables render real rows", rows.count() > 1, f"{rows.count()} rows")

    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    check("no CSP violations", not pg.csp_violations(), str(pg.csp_violations()[:2]))
    ctx.close()


def main() -> int:
    with server() as base, sync_playwright() as p:
        browser = p.chromium.launch()
        panchang(p, browser, base)
        muhurat_finder(p, browser, base)
        choghadiya(p, browser, base)
        browser.close()
    return check.finish("Panchang / Muhurat / Choghadiya")


if __name__ == "__main__":
    raise SystemExit(main())
