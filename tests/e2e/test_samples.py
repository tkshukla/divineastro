"""Sample reports in the UI (DIVASTRO-151).

  a. a signed-out visitor sees a "Sample" link on the home Plans cards for the
     Career report and the Life Book (and on no other card); it opens in a new tab,
     returns a PDF, and a tap reports sample_view with the sku
  b. /pricing at 390px: a "See a sample" link and the fictional-chart note on each
     report and the Life Book, none on the packs or the hand-written kundali
  c. the store: "View sample" on the three reports and the Life Book, none on the
     question packs or the hand-written kundali products
  d. in Hindi the link points at ?lang=hi and the PDF comes back

    ~/.venvs/divineastro/bin/python -u -m tests.e2e.test_samples
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from playwright.sync_api import sync_playwright  # noqa: E402

from tests.e2e.harness import DESKTOPS, Checker, Page, server  # noqa: E402

check = Checker()
PHONE = {"viewport": {"width": 390, "height": 844}, "is_mobile": True, "has_touch": True,
         "device_scale_factor": 2}
SAMPLED = ["sq_career", "sq_marriage_timing", "sq_wealth_business", "life_book"]
HAND_WRITTEN = ["k3", "k5", "k3q3"]
SHOTS = os.environ.get("SAMPLES_SHOT_DIR")


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


def fetch_pdf(pg: Page, href: str, base: str):
    r = pg.page.context.request.get(base + href)
    return r, r.body()


def home_plans(browser, base: str) -> None:
    print("\n[a. signed-out home: Sample link on the Career report and the Life Book cards]")
    for name, args in (("desktop", DESKTOPS["desktop_1440x800"]), ("phone 390", PHONE)):
        ctx = browser.new_context(**args)
        pg = Page(ctx.new_page(), base)
        events = track(pg)
        pg.open_home()
        pg.page.wait_for_selector("#plans:not([hidden]) .plan", timeout=10000)
        links = pg.page.eval_on_selector_all(
            "#plans a[data-sample]",
            "els => els.map(e => ({sku: e.dataset.sample, href: e.getAttribute('href'), target: e.target,"
            " rel: e.rel, text: e.innerText.trim()}))")
        check(f"[{name}] a Sample link on exactly the Career report and the Life Book",
              sorted(l["sku"] for l in links) == ["life_book", "sq_career"], str(links))
        check(f"[{name}] each opens in a new tab with rel noopener",
              all(l["target"] == "_blank" and "noopener" in l["rel"] for l in links), str(links))
        check(f"[{name}] the link says Sample", all(l["text"] == "Sample" for l in links), str(links))
        check(f"[{name}] the plan cards are still there and still link to /pricing",
              pg.page.locator("#plans a.plan").count() == 4
              and all(h.startswith("/pricing#") for h in pg.page.eval_on_selector_all("#plans a.plan", "els => els.map(e => e.getAttribute('href'))")))
        check(f"[{name}] no horizontal scroll",
              pg.page.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1"))
        for l in links:
            r, body = fetch_pdf(pg, l["href"], base)
            check(f"[{name}] {l['href']} returns an inline PDF",
                  r.ok and body.startswith(b"%PDF-") and "inline" in r.headers.get("content-disposition", "")
                  and r.headers["content-type"] == "application/pdf", f"{r.status} {body[:12]!r}")
        pg.page.locator('#plans a[data-sample="sq_career"]').scroll_into_view_if_needed()
        if SHOTS and name.startswith("phone"):
            pg.page.locator("#plans").screenshot(path=os.path.join(SHOTS, "home-plans-390.png"))
        with pg.page.context.expect_page() as popup:
            pg.page.click('#plans a[data-sample="sq_career"]')
        opened = popup.value
        check(f"[{name}] the tap opened a new tab", opened is not pg.page and len(pg.page.context.pages) >= 1)
        opened.close()
        pg.page.wait_for_timeout(600)
        check(f"[{name}] sample_view is reported with the sku",
              any(e.get("name") == "sample_view" and e.get("detail") == "sq_career" for e in events), str(events))
        check(f"[{name}] no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
        ctx.close()


def pricing_page(browser, base: str) -> None:
    print("\n[b. /pricing at 390px]")
    ctx = browser.new_context(**PHONE)
    pg = Page(ctx.new_page(), base)
    events = track(pg)
    pg.page.goto(base + "/pricing")
    pg.page.wait_for_timeout(400)
    for sku in SAMPLED:
        row = pg.page.locator(f'tr[data-sku="{sku}"]')
        link = row.locator("a[data-sample]")
        check(f"{sku}: See a sample + the note",
              link.count() == 1 and link.inner_text() == "See a sample"
              and "fictional chart; yours is cast from your own birth details" in row.inner_text())
    for sku in ["q10", "q50", "q100", *HAND_WRITTEN]:
        check(f"{sku}: no sample link", pg.page.locator(f'tr[data-sku="{sku}"] a[data-sample]').count() == 0)
    check("no horizontal scroll at 390px",
          pg.page.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1"))
    if SHOTS:
        pg.page.screenshot(path=os.path.join(SHOTS, "pricing-390.png"), full_page=True)
    pg.page.click('tr[data-sku="life_book"] a[data-sample]')
    pg.page.wait_for_timeout(600)
    check("a tap reports sample_view life_book",
          any(e.get("name") == "sample_view" and e.get("detail") == "life_book" for e in events), str(events))
    ctx.close()


def store(browser, base: str) -> None:
    print("\n[c. the store]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    pg.sign_in(email="e2e-sample@example.com", name="Sample Tester")
    pg.open_home()
    pg.page.wait_for_timeout(600)
    pg.page.evaluate("openStore()")
    pg.page.wait_for_selector(".modal.store .pack")
    for sku in SAMPLED:
        a = pg.page.locator(f'.modal.store .pack[data-sku="{sku}"] a[data-sample]')
        check(f"{sku}: View sample, new tab, noopener",
              a.count() == 1 and a.text_content().strip() == "View sample" and a.get_attribute("target") == "_blank"
              and "noopener" in a.get_attribute("rel") and a.get_attribute("href") == f"/samples/{sku}.pdf")
    for sku in ["q10", "q50", "q100", *HAND_WRITTEN]:
        check(f"{sku}: no sample link", pg.page.locator(f'.modal.store .pack[data-sku="{sku}"] a[data-sample]').count() == 0)
    check("exactly four sample links in the store", pg.page.locator(".modal.store a[data-sample]").count() == 4)
    r, body = fetch_pdf(pg, "/samples/life_book.pdf", base)
    check("the Life Book sample is a PDF", r.ok and body.startswith(b"%PDF-"), str(r.status))
    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    ctx.close()


def hindi(browser, base: str) -> None:
    print("\n[d. Hindi]")
    ctx = browser.new_context(**PHONE)
    pg = Page(ctx.new_page(), base)
    pg.page.goto(base + "/?lang=hi")
    pg.page.wait_for_selector("#plans:not([hidden]) a[data-sample]", timeout=10000)
    hrefs = pg.page.eval_on_selector_all("#plans a[data-sample]", "els => els.map(e => e.getAttribute('href'))")
    check("the Hindi home links ?lang=hi", sorted(hrefs) == ["/samples/life_book.pdf?lang=hi", "/samples/sq_career.pdf?lang=hi"], str(hrefs))
    check("and the link reads in Hindi", pg.page.locator("#plans a[data-sample]").first.inner_text() == "नमूना")
    r, body = fetch_pdf(pg, hrefs[0], base)
    check("the Hindi sample is a PDF", r.ok and body.startswith(b"%PDF-"), str(r.status))
    ctx.close()


def main() -> int:
    import tempfile
    with server({"ASTRO_SAMPLES_DIR": tempfile.mkdtemp(prefix="astro_e2e_samples_")}) as base, sync_playwright() as p:
        browser = p.chromium.launch()
        home_plans(browser, base)
        pricing_page(browser, base)
        store(browser, base)
        hindi(browser, base)
    return check.finish("sample reports (home Plans, /pricing, store, Hindi)")


if __name__ == "__main__":
    raise SystemExit(main())
