"""Dashboard: forecast, the Panchang widget, the dosha modal, the dasha
timeline, and the Kundali PDF download (DIVASTRO-72, flow 4).

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.e2e.test_dashboard_widgets
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from playwright.sync_api import sync_playwright  # noqa: E402

from tests.e2e.harness import BIRTH, Checker, DESKTOPS, Page, server  # noqa: E402

check = Checker()


def open_dashboard(pg: Page) -> None:
    pg.sign_in()
    pg.open_home()
    pg.page.evaluate("(b) => castChart(b)", BIRTH)
    pg.page.wait_for_selector("#stage-dashboard", state="visible", timeout=15000)
    pg.page.wait_for_selector("#dash-tithi:not(:empty)", timeout=15000)


def forecast_and_panchang(p, browser, base: str) -> None:
    print("\n[forecast card and Panchang widget render real data]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    open_dashboard(pg)

    check("the forecast badge has a real reading, not placeholder text",
          pg.page.locator("#transit-badge").inner_text().strip() != "",
          pg.page.locator("#transit-badge").inner_text())
    check("forecast advice text is present",
          pg.page.locator("#transit-advice").inner_text().strip() != "")

    for sel in ("#dash-tithi", "#dash-nakshatra", "#dash-yoga", "#dash-karana",
                "#dash-rahu-kalam", "#dash-sunrise", "#dash-sunset"):
        text = pg.page.locator(sel).inner_text().strip()
        check(f"Panchang widget {sel} has real content", text != "", repr(text))

    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    check("no CSP violations", not pg.csp_violations(), str(pg.csp_violations()[:2]))
    ctx.close()


def dosha_modal(p, browser, base: str) -> None:
    print("\n[dosha modal: Manglik / Sade Sati / Kaal Sarp]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    open_dashboard(pg)

    check("modal starts closed", not pg.page.is_visible("#doshas-modal"))
    pg.page.click("#dash-nav-doshas")
    pg.page.wait_for_selector("#doshas-modal", state="visible", timeout=10000)
    pg.page.wait_for_function(
        "document.querySelector('#doshas-content').children.length > 0", timeout=10000)
    groups = pg.page.locator("#doshas-content .dosha-group")
    check("the modal lists the dosha groups (Manglik/Sade Sati/Kaal Sarp)",
          groups.count() >= 3, f"{groups.count()} groups")

    pg.page.click("#close-doshas-modal")
    pg.page.wait_for_selector("#doshas-modal", state="hidden", timeout=10000)
    check("closing the modal actually hides it", not pg.page.is_visible("#doshas-modal"))

    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    check("no CSP violations", not pg.csp_violations(), str(pg.csp_violations()[:2]))
    ctx.close()


def dasha_timeline(p, browser, base: str) -> None:
    print("\n[dasha timeline renders periods and a detail view]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    open_dashboard(pg)

    pg.page.wait_for_selector("#timeline-visual .timeline-block", timeout=10000)
    blocks = pg.page.locator("#timeline-visual .timeline-block")
    check("the timeline renders at least one dasha period block", blocks.count() > 0,
          f"{blocks.count()} blocks")

    blocks.first.click()
    pg.page.wait_for_timeout(300)
    detail_text = pg.page.locator("#timeline-detail-box").inner_text().strip()
    check("clicking a period shows its detail", detail_text != "", repr(detail_text))

    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    check("no CSP violations", not pg.csp_violations(), str(pg.csp_violations()[:2]))
    ctx.close()


def kundali_pdf_download(p, browser, base: str) -> None:
    print("\n[Kundali PDF download, English and Hindi]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    open_dashboard(pg)

    pg.page.click("#dash-download-pdf")
    pg.page.wait_for_selector("#kundali-pdf-modal", state="visible", timeout=10000)

    with pg.page.expect_download(timeout=15000) as dl_info:
        pg.page.click("#generate-pdf-en")
    download_en = dl_info.value
    check("the English Kundali PDF actually downloads", download_en.suggested_filename != "",
          download_en.suggested_filename)

    pg.page.click("#dash-download-pdf")
    pg.page.wait_for_selector("#kundali-pdf-modal", state="visible", timeout=10000)
    with pg.page.expect_download(timeout=15000) as dl_info_hi:
        pg.page.click("#generate-pdf-hi")
    download_hi = dl_info_hi.value
    check("the Hindi Kundali PDF also downloads", download_hi.suggested_filename != "",
          download_hi.suggested_filename)

    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    check("no CSP violations", not pg.csp_violations(), str(pg.csp_violations()[:2]))
    ctx.close()


def main() -> int:
    with server() as base, sync_playwright() as p:
        browser = p.chromium.launch()
        forecast_and_panchang(p, browser, base)
        dosha_modal(p, browser, base)
        dasha_timeline(p, browser, base)
        kundali_pdf_download(p, browser, base)
        browser.close()
    return check.finish("dashboard widgets (forecast, panchang, doshas, timeline, PDF)")


if __name__ == "__main__":
    raise SystemExit(main())
