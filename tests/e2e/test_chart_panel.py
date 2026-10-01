"""Chart panel: the 8 content tabs, the 3 drawing styles, saving a chart and
reopening it (DIVASTRO-72, flow 5).

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.e2e.test_chart_panel
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from playwright.sync_api import sync_playwright  # noqa: E402

from tests.e2e.harness import BIRTH, DESKTOPS, Checker, Page, server  # noqa: E402

check = Checker()

TABS = ["placements", "houses", "vargas", "ashtakavarga", "jaimini", "sudarshana",
        "aspects", "now"]
STYLES = ["north", "south", "wheel"]


def eight_tabs(p, browser, base: str) -> None:
    print("\n[all 8 chart-panel tabs switch and load real content]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    pg.open_chat()

    for tab in TABS:
        pg.page.click(f'button.tab[data-tab="{tab}"]')
        pg.page.wait_for_function(
            "t => document.querySelector(`button.tab[data-tab=\"${t}\"]`).classList.contains('active')",
            arg=tab, timeout=10000)
        active_pane = pg.page.locator(f"#pane-{tab}").evaluate(
            "e => e.classList.contains('active')")
        check(f"[{tab}] tab becomes active", True)
        check(f"[{tab}] pane becomes active", active_pane)
        pg.page.wait_for_function(
            "t => (document.querySelector(`#pane-${t}`)?.textContent || '').trim().length > 0",
            arg=tab, timeout=10000)
        content = pg.page.locator(f"#pane-{tab}").inner_text().strip()
        check(f"[{tab}] pane actually has content, not an empty shell", len(content) > 0)

    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    check("no CSP violations", not pg.csp_violations(), str(pg.csp_violations()[:2]))
    ctx.close()


def three_chart_styles(p, browser, base: str) -> None:
    print("\n[the 3 chart drawing styles switch and persist to localStorage]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    pg.open_chat()

    for style in STYLES:
        pg.page.click(f'.cstyle[data-style="{style}"]')
        pg.page.wait_for_timeout(200)
        active = pg.page.evaluate("document.querySelector('.cstyle.active')?.dataset.style")
        check(f"[{style}] becomes the active style", active == style, str(active))
        stored = pg.page.evaluate("localStorage.getItem('astro.chartStyle')")
        check(f"[{style}] persisted to localStorage", stored == style, str(stored))

    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    check("no CSP violations", not pg.csp_violations(), str(pg.csp_violations()[:2]))
    ctx.close()


def save_and_reopen(p, browser, base: str) -> None:
    print("\n[save a chart, then reopen it from the home screen]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    pg.open_chat()

    check("the save-chart button is visible once signed in with a cast chart",
          pg.page.is_visible("#save-chart-btn"))
    check("not yet marked as saved", "saved" not in (
        pg.page.get_attribute("#save-chart-btn", "class") or ""))

    pg.page.click("#save-chart-btn")
    pg.page.wait_for_function(
        "document.querySelector('#save-chart-btn').classList.contains('saved')", timeout=10000)
    check("the save button shows saved afterwards", True)

    births = pg.page.context.request.get(f"{base}/api/births").json()
    check("the chart was actually persisted server-side", len(births["births"]) >= 1, str(births))

    # #back intentionally goes to the dashboard, not home, once a session is
    # active (app.js: state.sessionId check) — a fresh navigation is the real
    # way a user reaches "home" with their saved charts freshly loaded.
    pg.open_home()
    pg.page.wait_for_selector("#saved-charts:not([hidden])", timeout=10000)
    rows = pg.page.locator("#saved-charts .saved-row")
    check("the saved chart appears on the home screen", rows.count() >= 1,
          f"{rows.count()} rows")

    pg.page.click('#saved-charts .saved-row .saved-open[data-act="open"]')
    pg.page.wait_for_selector("#stage-dashboard, #stage-chat", state="visible", timeout=15000)
    check("clicking a saved chart reopens it (leaves the home stage)",
          not pg.page.is_visible("#saved-charts") or pg.page.locator("#stage-home").evaluate(
              "e => !e.classList.contains('active')"))

    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    check("no CSP violations", not pg.csp_violations(), str(pg.csp_violations()[:2]))
    ctx.close()


def main() -> int:
    with server() as base, sync_playwright() as p:
        browser = p.chromium.launch()
        eight_tabs(p, browser, base)
        three_chart_styles(p, browser, base)
        save_and_reopen(p, browser, base)
        browser.close()
    return check.finish("chart panel (tabs, styles, save/reopen)")


if __name__ == "__main__":
    raise SystemExit(main())
