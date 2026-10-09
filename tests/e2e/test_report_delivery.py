"""Delivering what was bought (DIVASTRO-150): a customer who pays for a report or
the Life Book can open the PDF.

  a. buying a report in the store -> a 'ready' state with Download PDF; the click
     downloads a real PDF for the chart that is open; the Life Book likewise
     (it is paid with no report_topic, which the endpoint used to refuse)
  b. the download uses the app language (?lang=hi in Hindi)
  c. failures are said out loud with a Try again: 402 (not paid), 500, no network
  d. My orders: Download PDF on paid report/Life Book orders only; none on an
     unpaid order or a hand-written kundali, whose fulfilment status is shown
  e. no chart open (the page was reloaded after PayU's redirect, or a fresh visit):
     the saved charts are offered; with none saved the person is guided
  f. the dashboard's 'Your reports' row appears only for an account that owns one
  g. 390px screenshots of the ready state, My orders and the reports row

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.e2e.test_report_delivery
    E2E_SHOTS=<dir> keeps the screenshots (otherwise they are not written)
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from playwright.sync_api import sync_playwright  # noqa: E402

from tests.e2e.harness import BIRTH, DESKTOPS, Checker, Page, server  # noqa: E402

check = Checker()
PHONE = {"viewport": {"width": 390, "height": 844}, "is_mobile": True, "has_touch": True,
         "device_scale_factor": 2}
SHOTS = os.environ.get("E2E_SHOTS")
SECOND = {**BIRTH, "name": "Second Chart", "date": "1992-03-04", "time": "06:15"}


def shot(pg: Page, name: str) -> None:
    if SHOTS:
        Path(SHOTS).mkdir(parents=True, exist_ok=True)
        pg.page.screenshot(path=str(Path(SHOTS) / f"{name}.png"))


def api(pg: Page, method: str, path: str, **kw):
    return getattr(pg.page.context.request, method)(f"{pg.base}/api{path}", **kw)


def buy(pg: Page, sku: str, pay: bool = True) -> int:
    """Create an order through the API; pay it through the test gateway."""
    order = api(pg, "post", "/orders", data={"sku": sku}).json()["order"]
    if pay:
        r = api(pg, "post", "/orders/confirm", data={"order_id": order["id"], "payload": {}})
        assert r.ok, r.text()
    return order["id"]


def save_chart(pg: Page, birth: dict) -> None:
    r = api(pg, "post", "/births", data=birth)
    assert r.ok, r.text()


def pdf_pages(data: bytes) -> int:
    m = re.findall(rb"/Count\s+(\d+)", data)
    return int(m[0]) if m else 0


def download(pg: Page, click_selector: str, timeout: int = 90000) -> bytes:
    with pg.page.expect_download(timeout=timeout) as info:
        pg.page.click(click_selector)
    d = info.value
    return Path(d.path()).read_bytes(), d.suggested_filename


def new_user(browser, base: str, email: str, viewport=None):
    ctx = browser.new_context(**(viewport or DESKTOPS["desktop_1440x800"]))
    pg = Page(ctx.new_page(), base)
    pg.sign_in(email=email, name=email.split("@")[0])
    return ctx, pg


def cast_open(pg: Page, birth=BIRTH) -> None:
    pg.open_home()
    pg.page.evaluate("(b) => castChart(b)", birth)
    pg.page.wait_for_selector("#stage-dashboard.active", timeout=20000)


def purchase_then_download(browser, base: str) -> None:
    print("\n[a. buy in the store -> ready state -> a real PDF for the open chart]")
    ctx, pg = new_user(browser, base, "e2e-buyer@example.com")
    cast_open(pg)
    urls: list[str] = []
    pg.page.on("request", lambda r: urls.append(r.url) if "/api/pdf/" in r.url else None)
    sid = pg.page.evaluate("state.sessionId")

    pg.page.evaluate("openStore(false, 'sq_career')")
    pg.page.wait_for_selector('.buy-btn[data-sku="sq_career"]', timeout=10000)
    pg.page.click('.buy-btn[data-sku="sq_career"]')
    pg.page.wait_for_selector(".rpt-ready", timeout=15000)
    title = pg.page.inner_text(".rpt-ready-title")
    check("the ready state names the report that was bought",
          "Career" in title and "ready" in title.lower(), title)
    check("it offers a Download PDF button",
          pg.page.locator(".rpt-ready .rpt-dl").first.inner_text().strip() == "Download PDF")
    check("it names the chart the PDF will be for", "E2E Tester" in pg.page.inner_text(".rpt-ready .rpt-chart"))
    data, name = download(pg, ".rpt-ready .rpt-dl")
    check("the click downloads a PDF file", data.startswith(b"%PDF-") and name.endswith(".pdf"), name)
    check("the career report has at least its 5 pages", pdf_pages(data) >= 5, str(pdf_pages(data)))
    check("it was requested for the open chart, in English",
          any(f"/api/pdf/single-question/{sid}" in u and "sku=sq_career" in u and "lang=en" in u for u in urls),
          str(urls))
    check("a status line confirms the download", "downloading" in pg.page.inner_text(".rpt-ready .rpt-msg").lower())
    pg.page.click(".modal-x")

    print("\n[a2. the Life Book, bought the same way, downloads too]")
    pg.page.evaluate("openStore(false, 'life_book')")
    pg.page.wait_for_selector('.buy-btn[data-sku="life_book"]', timeout=10000)
    pg.page.click('.buy-btn[data-sku="life_book"]')
    pg.page.wait_for_selector(".rpt-ready", timeout=15000)
    check("the Life Book ready state names it", "Life Book" in pg.page.inner_text(".rpt-ready-title"))
    data, name = download(pg, ".rpt-ready .rpt-dl")
    check("the Life Book downloads as a PDF with at least its 8 pages",
          data.startswith(b"%PDF-") and pdf_pages(data) >= 8, f"{name} {pdf_pages(data)} pages")
    check("no server error on the way", not pg.failed_requests, str(pg.failed_requests))
    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    check("no CSP violations", not pg.csp_violations(), str(pg.csp_violations()[:2]))
    ctx.close()


def hindi_download(browser, base: str) -> None:
    print("\n[b. the PDF is requested in the app language]")
    ctx, pg = new_user(browser, base, "e2e-hindi@example.com")
    buy(pg, "sq_marriage_timing")
    cast_open(pg)
    urls: list[str] = []
    pg.page.on("request", lambda r: urls.append(r.url) if "/api/pdf/" in r.url else None)
    pg.set_lang("hi")
    pg.page.wait_for_selector("#dash-reports:not([hidden]) .rpt-chip", timeout=10000)
    chip = pg.page.inner_text("#dash-reports .rpt-chip")
    check("the reports row speaks Hindi", re.search("[\u0900-\u097f]", chip) is not None, chip)
    data, name = download(pg, "#dash-reports .rpt-chip")
    check("a Hindi report downloads", data.startswith(b"%PDF-") and pdf_pages(data) >= 5, name)
    check("with ?lang=hi", any("lang=hi" in u and "sq_marriage_timing" in u for u in urls), str(urls))
    pg.page.evaluate("showReportReady({id: 0, sku: 'sq_marriage_timing', title: 'x', status: 'paid'})")
    pg.page.wait_for_selector(".rpt-ready")
    check("the Hindi ready screen has a Hindi Download button",
          "डाउनलोड" in pg.page.locator(".rpt-ready .rpt-dl").first.inner_text())
    ctx.close()

    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    pg.sign_in(email="e2e-hindi@example.com")
    cast_open(pg)
    pg.set_lang("kn")
    urls.clear()
    pg.page.on("request", lambda r: urls.append(r.url) if "/api/pdf/" in r.url else None)
    pg.page.wait_for_selector("#dash-reports:not([hidden]) .rpt-chip", timeout=10000)
    pg.page.evaluate("showReportReady({id: 0, sku: 'sq_marriage_timing', title: 'x', status: 'paid'})")
    pg.page.wait_for_selector(".rpt-ready .rpt-note")
    check("another app language is told reports come in English or Hindi",
          pg.page.locator(".rpt-ready .rpt-note").inner_text().strip() != "")
    data, _name = download(pg, ".rpt-ready .rpt-dl")
    check("it downloads, in English", data.startswith(b"%PDF-") and any("lang=en" in u for u in urls), str(urls))
    ctx.close()


def failures_are_spoken(browser, base: str) -> None:
    print("\n[c. 402, 500 and a dead network are said out loud, with Try again]")
    ctx, pg = new_user(browser, base, "e2e-fail@example.com")
    buy(pg, "sq_career")
    cast_open(pg)
    text = lambda k: pg.page.evaluate(f"at('{k}')")                                   # noqa: E731

    # 402: this account never bought the wealth report.
    pg.page.evaluate("showReportReady({id: 0, sku: 'sq_wealth_business', title: 'x', status: 'paid'})")
    pg.page.wait_for_selector(".rpt-ready .rpt-dl")
    pg.page.click(".rpt-ready .rpt-dl")
    pg.page.wait_for_selector(".rpt-ready .rpt-msg.rpt-bad", timeout=30000)
    check("402: the person is told it is not paid for",
          pg.page.inner_text(".rpt-ready .rpt-msg") == text("rptNotPaid"), pg.page.inner_text(".rpt-ready .rpt-msg"))
    check("402: the button becomes Try again",
          pg.page.locator(".rpt-ready .rpt-dl").first.inner_text() == text("rptRetry"))
    check("402: the message is announced (aria-live)",
          pg.page.get_attribute(".rpt-ready .rpt-msg", "aria-live") == "polite")
    pg.page.click(".modal-x")

    # 500 then success: Try again works.
    pg.page.evaluate("showReportReady({id: 0, sku: 'sq_career', title: 'x', status: 'paid'})")
    pg.page.wait_for_selector(".rpt-ready .rpt-dl")
    pg.page.route("**/api/pdf/single-question/**",
                  lambda route: route.fulfill(status=500, content_type="application/json",
                                              body='{"detail":"Could not build the PDF: boom"}'))
    pg.page.click(".rpt-ready .rpt-dl")
    pg.page.wait_for_selector(".rpt-ready .rpt-msg.rpt-bad", timeout=30000)
    msg = pg.page.inner_text(".rpt-ready .rpt-msg")
    check("500: a plain message, not the raw server text", msg == text("rptFailed") and "boom" not in msg, msg)
    check("500: nothing was navigated away to a JSON page", pg.page.locator(".rpt-ready").count() == 1)
    pg.page.unroute("**/api/pdf/single-question/**")
    data, _name = download(pg, ".rpt-ready .rpt-dl")
    check("500: Try again then delivers the PDF", data.startswith(b"%PDF-"))

    # dead network
    pg.page.route("**/api/pdf/single-question/**", lambda route: route.abort())
    pg.page.click(".rpt-ready .rpt-dl")
    pg.page.wait_for_function("() => document.querySelector('.rpt-ready .rpt-msg')?.classList.contains('rpt-bad')",
                              timeout=30000)
    check("no network: told to check the connection",
          pg.page.inner_text(".rpt-ready .rpt-msg") == text("rptNetwork"))
    pg.page.unroute("**/api/pdf/single-question/**")

    # chart gone (404): the server restarted, so the session id is stale
    pg.page.evaluate("state.sessionId = 'does-not-exist'")
    pg.page.evaluate("showReportReady({id: 0, sku: 'sq_career', title: 'x', status: 'paid'})")
    pg.page.wait_for_selector(".rpt-ready .rpt-dl")
    pg.page.click(".rpt-ready .rpt-dl")
    pg.page.wait_for_selector(".rpt-ready .rpt-msg.rpt-bad", timeout=30000)
    check("404: asked to open the chart again", pg.page.inner_text(".rpt-ready .rpt-msg") == text("rptChartGone"))
    ctx.close()


def orders_screen(browser, base: str) -> None:
    print("\n[d. My orders: Download PDF only where a PDF exists; hand-written kundali shows its status]")
    ctx, pg = new_user(browser, base, "e2e-orders-dl@example.com", PHONE)
    buy(pg, "sq_career")
    buy(pg, "life_book")
    unpaid = buy(pg, "sq_wealth_business", pay=False)
    buy(pg, "k3")
    cast_open(pg)
    pg.page.wait_for_selector("#dash-reports:not([hidden]) .rpt-chip", timeout=10000)
    pg.page.click("#btn-acct")
    pg.page.click('.acct-drop button[data-act="orders"]')
    pg.page.wait_for_selector(".ord-row", timeout=10000)

    rows = pg.page.eval_on_selector_all(
        ".ord-row", """els => els.map(e => ({sku: e.dataset.sku, status: e.dataset.status,
        dl: e.querySelectorAll('.ord-dl').length, hand: e.querySelector('.ord-hand')?.innerText || '',
        text: e.innerText}))""")
    by = {r["sku"]: r for r in rows}
    check("four orders listed", len(rows) == 4, str(rows))
    check("paid career report has Download PDF", by["sq_career"]["dl"] == 1)
    check("paid Life Book has Download PDF", by["life_book"]["dl"] == 1)
    check("the unpaid report order has none", by["sq_wealth_business"]["dl"] == 0
          and by["sq_wealth_business"]["status"] == "created", str(by["sq_wealth_business"]))
    check("the unpaid order says so", "Not paid" in by["sq_wealth_business"]["text"])
    check("the hand-written kundali has no PDF button", by["k3"]["dl"] == 0)
    check("it shows its fulfilment status in words",
          "astrologer" in by["k3"]["hand"].lower() and "Pending" in by["k3"]["hand"], by["k3"]["hand"])
    shot(pg, "orders-390")
    check("no horizontal scroll on the orders screen",
          pg.page.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1"))

    # chart on screen and only that one: one click, straight to the file.
    data, _ = download(pg, '.ord-row[data-sku="sq_career"] .ord-dl')
    check("Download PDF from My orders delivers the report for the open chart",
          data.startswith(b"%PDF-") and pdf_pages(data) >= 5)
    check("the row confirms it", "downloading" in pg.page.inner_text('.ord-row[data-sku="sq_career"] .rpt-msg').lower())
    pg.page.click(".modal-x")

    # Hindi: the kundali status is in the app's language
    pg.set_lang("hi")
    pg.page.click("#btn-acct")
    pg.page.click('.acct-drop button[data-act="orders"]')
    pg.page.wait_for_selector(".ord-row")
    hand = pg.page.inner_text('.ord-row[data-sku="k3"] .ord-hand')
    pending_hi = pg.page.evaluate("statusText('pending')")
    check("in Hindi the fulfilment line is Hindi and carries the Hindi status",
          re.search("[\u0900-\u097f]", hand) and pending_hi in hand, hand)
    check("the unpaid order is still without a PDF button in Hindi",
          pg.page.locator('.ord-row[data-sku="sq_wealth_business"] .ord-dl').count() == 0)
    _ = unpaid
    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    ctx.close()


def no_chart_open(browser, base: str) -> None:
    print("\n[e. no chart open: saved charts are offered; none saved -> guidance; PayU-style reload]")
    ctx, pg = new_user(browser, base, "e2e-nochart@example.com", PHONE)
    oid = buy(pg, "sq_career")
    save_chart(pg, BIRTH)
    save_chart(pg, SECOND)

    # PayU's redirect: a full page load of /?payu=ok&order=<id>, nothing cast yet
    pg.page.goto(f"{base}/?payu=ok&order={oid}", wait_until="domcontentloaded")
    pg.page.wait_for_selector(".rpt-ready", timeout=15000)
    check("after a PayU return the ready state shows without any chart open",
          pg.page.evaluate("!state.sessionId"))
    check("it asks which chart (none is open)", pg.page.locator(".rpt-ready .rpt-row").count() == 2,
          pg.page.inner_text(".rpt-ready"))
    check("it says there is no chart open",
          pg.page.evaluate("at('rptReadyNoChart')") in pg.page.inner_text(".rpt-ready"))
    check("the ?payu= parameters are cleaned from the URL", "payu=" not in pg.page.url, pg.page.url)
    shot(pg, "ready-nochart-390")
    check("no horizontal scroll on the ready state",
          pg.page.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1"))
    second = pg.page.locator(".rpt-ready .rpt-row", has_text="Second Chart")
    with pg.page.expect_download(timeout=90000) as info:
        second.locator(".rpt-dl").click()
    data = Path(info.value.path()).read_bytes()
    check("choosing a saved chart casts it and downloads the PDF", data.startswith(b"%PDF-"))
    check("that chart is now the open one", pg.page.evaluate("state.chart.meta.name") == "Second Chart")
    ctx.close()

    # more than one candidate while one is open: a picker, open chart marked
    ctx, pg = new_user(browser, base, "e2e-twocharts@example.com")
    buy(pg, "sq_career")
    save_chart(pg, BIRTH)
    save_chart(pg, SECOND)
    pg.open_home()
    pg.page.wait_for_function("state.births.length === 2")
    pg.page.evaluate("(b) => castChart(b)", BIRTH)
    pg.page.wait_for_selector("#stage-dashboard.active")
    pg.page.click("#btn-acct")
    pg.page.click('.acct-drop button[data-act="orders"]')
    pg.page.wait_for_selector('.ord-row[data-sku="sq_career"] .ord-dl')
    pg.page.click('.ord-row[data-sku="sq_career"] .ord-dl')
    pg.page.wait_for_selector(".ord-host .rpt-row")
    check("two charts: a picker with both", pg.page.locator(".ord-host .rpt-row").count() == 2)
    check("the open chart is marked and listed first",
          "open now" in pg.page.locator(".ord-host .rpt-row").first.inner_text())
    ctx.close()

    # nothing saved, nothing open
    ctx, pg = new_user(browser, base, "e2e-emptyacct@example.com")
    buy(pg, "life_book")
    pg.open_home()
    pg.page.wait_for_function("acct.user !== null")
    pg.page.click("#btn-acct")
    pg.page.click('.acct-drop button[data-act="orders"]')
    pg.page.wait_for_selector('.ord-row[data-sku="life_book"] .ord-dl')
    pg.page.click('.ord-row[data-sku="life_book"] .ord-dl')
    pg.page.wait_for_selector(".ord-host .rpt-guide")
    check("no chart at all: the person is told to create one first",
          pg.page.inner_text(".ord-host .rpt-guide") == pg.page.evaluate("at('rptNoChart')"))
    check("and the order stays in the list as paid",
          pg.page.get_attribute('.ord-row[data-sku="life_book"]', "data-status") == "paid")
    pg.page.click(".ord-host .rpt-new")
    pg.page.wait_for_selector("#stage-birth.active", timeout=5000)
    check("the guidance button leads to the birth form", pg.page.locator("#stage-birth.active").count() == 1)
    ctx.close()


def dashboard_row(browser, base: str) -> None:
    print("\n[f. the dashboard's 'Your reports' row]")
    ctx, pg = new_user(browser, base, "e2e-norow@example.com", PHONE)
    cast_open(pg)
    pg.page.wait_for_timeout(1200)
    check("an account that owns nothing sees no reports row",
          pg.page.evaluate("document.getElementById('dash-reports').hidden === true"))
    ctx.close()

    ctx, pg = new_user(browser, base, "e2e-row@example.com", PHONE)
    buy(pg, "sq_career")
    buy(pg, "life_book")
    cast_open(pg)
    pg.page.wait_for_selector("#dash-reports:not([hidden]) .rpt-chip", timeout=10000)
    chips = pg.page.locator("#dash-reports .rpt-chip")
    check("two reports owned, two chips", chips.count() == 2, pg.page.inner_text("#dash-reports"))
    check("each chip says Download PDF",
          all("Download PDF" in chips.nth(i).inner_text() for i in range(2)))
    check("the row is compact on a phone",
          pg.page.evaluate("document.getElementById('dash-reports').getBoundingClientRect().height") < 200)
    pg.page.locator("#dash-reports").scroll_into_view_if_needed()
    shot(pg, "dash-reports-390")
    check("no horizontal scroll with the row",
          pg.page.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1"))
    data, name = download(pg, '#dash-reports .rpt-chip[data-sku="life_book"]')
    check("a chip downloads that report for the open chart", data.startswith(b"%PDF-") and pdf_pages(data) >= 8, name)
    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    ctx.close()


def mobile_ready_shot(browser, base: str) -> None:
    print("\n[g. the ready state on a 390px phone]")
    ctx, pg = new_user(browser, base, "e2e-shot@example.com", PHONE)
    cast_open(pg)
    pg.page.evaluate("openStore(false, 'sq_wealth_business')")
    pg.page.wait_for_selector('.buy-btn[data-sku="sq_wealth_business"]', timeout=10000)
    pg.page.click('.buy-btn[data-sku="sq_wealth_business"]')
    pg.page.wait_for_selector(".rpt-ready .rpt-dl", timeout=15000)
    pg.page.wait_for_timeout(400)
    shot(pg, "ready-390")
    check("the ready state fits a 390px phone",
          pg.page.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1"))
    box = pg.page.locator(".rpt-ready .rpt-dl").first.bounding_box()
    check("the Download PDF button is a comfortable tap target", box and box["height"] >= 44, str(box))
    ctx.close()


def main() -> int:
    with server() as base, sync_playwright() as p:
        browser = p.chromium.launch()
        purchase_then_download(browser, base)
        hindi_download(browser, base)
        failures_are_spoken(browser, base)
        orders_screen(browser, base)
        no_chart_open(browser, base)
        dashboard_row(browser, base)
        mobile_ready_shot(browser, base)
        browser.close()
    return check.finish("report delivery: ready state, Orders, dashboard row, failures")


if __name__ == "__main__":
    raise SystemExit(main())
