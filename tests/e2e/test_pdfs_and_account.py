"""PDF exports beyond the Kundali PDF (already covered in
test_dashboard_widgets.py): remedies, and the PDF routes that need no button of
their own here (questions-history export; the single-question and life-book
routes' 402-before-purchase gate, tested directly against the API — their
download UI after a purchase is tests/e2e/test_report_delivery.py,
DIVASTRO-150). Plus orders,
question history, and the credit ledger (DIVASTRO-72, flows 10 and 11).

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.e2e.test_pdfs_and_account
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from playwright.sync_api import sync_playwright  # noqa: E402

from tests.e2e.harness import BIRTH, DESKTOPS, Checker, Page, server  # noqa: E402

check = Checker()


def remedies_pdf(p, browser, base: str) -> None:
    print("\n[remedies PDF download from the dashboard's remedies modal]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    pg.sign_in()
    pg.open_home()
    pg.page.evaluate("(b) => castChart(b)", BIRTH)
    pg.page.wait_for_selector("#stage-dashboard", state="visible", timeout=15000)

    pg.page.click("#dash-nav-remedies")
    pg.page.wait_for_selector("#remedies-modal", state="visible", timeout=10000)
    with pg.page.expect_download(timeout=15000) as dl_info:
        pg.page.click("#download-remedies-pdf")
    check("the remedies PDF actually downloads", dl_info.value.suggested_filename != "",
          dl_info.value.suggested_filename)

    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    check("no CSP violations", not pg.csp_violations(), str(pg.csp_violations()[:2]))
    ctx.close()


def pdf_routes_gate_correctly(p, browser, base: str) -> None:
    print("\n[questions-export, single-question and life-book PDFs: the routes are "
          "correct before purchase — tested directly. After a purchase the "
          "download UI is covered by test_report_delivery]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    pg.sign_in()
    pg.open_home()
    pg.page.evaluate("(b) => castChart(b)", BIRTH)
    pg.page.wait_for_selector("#stage-dashboard", state="visible", timeout=15000)
    sid = pg.page.evaluate("state.sessionId")

    anon = browser.new_context()
    anon_req = anon.request
    unauth = anon_req.get(f"{base}/api/pdf/questions")
    check("questions-export PDF requires sign-in (401 when anonymous)",
          unauth.status == 401, str(unauth.status))
    anon.close()

    # Signed in, but never asked a question yet in this fresh account — still
    # must not 500.
    q = pg.page.context.request.get(f"{base}/api/pdf/questions")
    check("questions-export with zero history does not 500",
          q.status in (200, 404), str(q.status))

    sq = pg.page.context.request.get(f"{base}/api/pdf/single-question/{sid}?sku=sq_career")
    check("single-question PDF is refused with 402 before purchase",
          sq.status == 402, f"{sq.status} {sq.text()[:200]}")

    lb = pg.page.context.request.get(f"{base}/api/pdf/life-book/{sid}")
    check("life-book PDF is refused with 402 before purchase",
          lb.status == 402, f"{lb.status} {lb.text()[:200]}")

    ctx.close()


def orders_history_and_ledger(p, browser, base: str) -> None:
    print("\n[orders and question history in the UI; the credit ledger via its "
          "API, since it has no customer-facing screen yet]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    pg.open_chat(email="e2e-orders@example.com", name="Orders Tester")

    # One real order via the test gateway, so Orders has something to show.
    order = pg.page.context.request.post(f"{base}/api/orders", data={"sku": "q10"}).json()
    confirm = pg.page.context.request.post(
        f"{base}/api/orders/confirm",
        data={"order_id": order["order"]["id"], "payload": {}})
    check("a test-gateway purchase completes", confirm.ok, confirm.text()[:200])

    # One real question, so History has something to show.
    pg.page.fill("#q", "What does my chart say about career?")
    pg.page.click("#send")
    pg.page.wait_for_function("state.busy === false", timeout=20000)

    pg.page.click("#btn-acct")
    pg.page.click('.acct-drop button[data-act="orders"]')
    pg.page.wait_for_selector(".hist-row", timeout=10000)
    check("the real order appears in the Orders view", pg.page.locator(".hist-row").count() >= 1)
    pg.page.click(".modal-x")
    pg.page.wait_for_selector(".modal-backdrop", state="detached", timeout=5000)

    pg.page.click("#btn-acct")
    pg.page.click('.acct-drop button[data-act="history"]')
    pg.page.wait_for_selector(".hist-row", timeout=10000)
    check("the real question appears in the History view",
          pg.page.locator(".hist-row").count() >= 1)

    ledger = pg.page.context.request.get(f"{base}/api/ledger").json()
    check("the credit ledger API reflects both the purchase and the question spend",
          len(ledger.get("entries", [])) >= 2, str(ledger))

    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    check("no CSP violations", not pg.csp_violations(), str(pg.csp_violations()[:2]))
    ctx.close()


def main() -> int:
    with server() as base, sync_playwright() as p:
        browser = p.chromium.launch()
        remedies_pdf(p, browser, base)
        pdf_routes_gate_correctly(p, browser, base)
        orders_history_and_ledger(p, browser, base)
        browser.close()
    return check.finish("PDFs (remedies + purchase gate), orders/history/ledger")


if __name__ == "__main__":
    raise SystemExit(main())
