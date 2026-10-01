"""Kundali Milan (matchmaking), English and Hindi (DIVASTRO-72, flow 7).

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.e2e.test_milan
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from playwright.sync_api import sync_playwright  # noqa: E402

from tests.e2e.harness import DESKTOPS, Checker, Page, server  # noqa: E402

check = Checker()

GROOM = {"name": "Rohan", "date": "1990-03-12", "time": "09:30", "place": "Delhi"}
BRIDE = {"name": "Priya", "date": "1992-07-20", "time": "14:15", "place": "Mumbai"}


def fill_side(pg: Page, side: str, person: dict) -> None:
    card = f'.milan-card[data-side="{side}"]'
    pg.page.fill(f'{card} [data-f="name"]', person["name"])
    pg.page.fill(f'{card} [data-f="date"]', person["date"])
    pg.page.fill(f'{card} [data-f="time"]', person["time"])
    pg.page.fill(f'{card} [data-f="place"]', person["place"])
    pg.page.wait_for_selector(f'{card} [data-f="results"] li', timeout=10000)
    pg.page.locator(f'{card} [data-f="results"] li').first.click()


def open_milan(pg: Page) -> None:
    pg.open_home()
    pg.page.click("#open-milan")
    pg.page.wait_for_selector("#stage-milan", state="visible", timeout=10000)


def milan_english(p, browser, base: str) -> None:
    print("\n[Kundali Milan in English: both forms, a real score, a real verdict]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    open_milan(pg)

    fill_side(pg, "groom", GROOM)
    fill_side(pg, "bride", BRIDE)
    check("both places resolved before submitting",
          pg.page.locator('.milan-card[data-side="groom"] [data-f="chosen"]').is_visible()
          and pg.page.locator('.milan-card[data-side="bride"] [data-f="chosen"]').is_visible())

    pg.page.click("#milan-go")
    pg.page.wait_for_selector("#milan-result", state="visible", timeout=15000)

    score_text = pg.page.locator(".ms-num").inner_text()
    check("a real Ashtakoot score renders", "/" in score_text, score_text)
    check("a verdict line renders", pg.page.locator(".ms-verdict").inner_text().strip() != "")
    rows = pg.page.locator("table.koota-table tbody tr")
    check("the koota breakdown table has all 8 kootas", rows.count() == 8, f"{rows.count()} rows")
    check("Mangal Dosha is reported for both people",
          pg.page.locator(".milan-extra").inner_text().strip() != "")

    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    check("no CSP violations", not pg.csp_violations(), str(pg.csp_violations()[:2]))
    ctx.close()


def milan_hindi(p, browser, base: str) -> None:
    print("\n[Kundali Milan in Hindi: the request says hi, the result reads Hindi]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    open_milan(pg)
    pg.page.click('button.lang[data-lang="hi"]')
    pg.page.evaluate("showStage('stage-milan')")

    fill_side(pg, "groom", GROOM)
    fill_side(pg, "bride", BRIDE)

    bodies: list[str] = []
    pg.page.on("request", lambda r: bodies.append(r.post_data or "")
               if r.url.endswith("/api/match") else None)
    pg.page.click("#milan-go")
    pg.page.wait_for_selector("#milan-result", state="visible", timeout=15000)

    check("the match request declared Hindi", len(bodies) == 1 and '"lang":"hi"' in bodies[0],
          str(bodies))
    check("a score still renders in Hindi mode", "/" in pg.page.locator(".ms-num").inner_text())

    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    check("no CSP violations", not pg.csp_violations(), str(pg.csp_violations()[:2]))
    ctx.close()


def main() -> int:
    with server() as base, sync_playwright() as p:
        browser = p.chromium.launch()
        milan_english(p, browser, base)
        milan_hindi(p, browser, base)
        browser.close()
    return check.finish("Kundali Milan (English, Hindi)")


if __name__ == "__main__":
    raise SystemExit(main())
