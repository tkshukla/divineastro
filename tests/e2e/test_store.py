"""The store: product list, buying on the test gateway, applying a coupon at
checkout, the manual-UPI claim UI, and the PayU hidden-form handoff
(DIVASTRO-72, flow 9). Admin-side coupon CRUD and UPI-queue approval are
already covered in test_feedback_admin.py; this file is the customer side.

PayU's signed/tampered/replayed-return logic is already thoroughly covered
at the API level in tests/test_payu.py (which this file's hash helper is
copied from, not reinvented) — this file's job is the one thing only a
browser can show: does the hidden-form handoff actually reach PayU's domain
with zero CSP violations, the literal regression DIVASTRO-72 exists for
("nothing happens when I click Buy").

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.e2e.test_store
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from playwright.sync_api import sync_playwright  # noqa: E402

from tests.e2e.harness import DESKTOPS, Checker, Page, server  # noqa: E402

check = Checker()

PAYU_KEY = "gdtestkey"
PAYU_SALT = "gdtestsalt123456"


def reverse_hash(status: str, productinfo: str, firstname: str, email: str,
                  amount: str, txnid: str) -> str:
    """Same formula tests/test_payu.py uses — see that file's own docstring
    for why every one of the 10 empty udf slots is spelled out by name."""
    fields = [PAYU_SALT, status, "", "", "", "", "", "", "", "", "", "",
              email, firstname, productinfo, amount, txnid, PAYU_KEY]
    return hashlib.sha512("|".join(fields).encode()).hexdigest()


def store_and_products(p, browser, base: str) -> None:
    print("\n[store entry and the product list]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    pg.sign_in(email="e2e-store@example.com", name="Store Tester")
    pg.open_home()

    products = pg.page.context.request.get(f"{base}/api/products").json()
    check("the product catalogue has real entries", len(products["products"]) > 0,
          str(len(products["products"])))

    pg.page.click("#btn-buy")
    pg.page.wait_for_selector(".pack", timeout=10000)
    check("product cards render in the store modal", pg.page.locator(".pack").count() > 0)
    check("each card has a buy button with a real sku",
          pg.page.locator('.buy-btn[data-sku="q10"]').count() > 0)

    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    check("no CSP violations", not pg.csp_violations(), str(pg.csp_violations()[:2]))
    ctx.close()


def buy_on_test_gateway(p, browser, base: str) -> None:
    print("\n[buying on the test gateway completes instantly, credits update]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    pg.sign_in(email="e2e-buy@example.com", name="Buy Tester")
    pg.open_home()

    before = pg.page.context.request.get(f"{base}/api/me").json()["user"]["credits"]
    pg.page.click("#btn-buy")
    pg.page.wait_for_selector('.buy-btn[data-sku="q10"]', timeout=10000)
    pg.page.click('.buy-btn[data-sku="q10"]')
    pg.page.wait_for_timeout(1500)

    after = pg.page.context.request.get(f"{base}/api/me").json()["user"]["credits"]
    check("credits actually increased after a test-gateway purchase", after > before,
          f"{before} -> {after}")
    pill_text = pg.page.locator("#btn-credits").inner_text()
    check("the credits pill reflects the new balance", str(after) in pill_text, pill_text)

    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    check("no CSP violations", not pg.csp_violations(), str(pg.csp_violations()[:2]))
    ctx.close()


def coupon_at_checkout(p, browser, base: str) -> None:
    print("\n[applying a coupon at checkout changes the price, then the purchase honours it]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    pg.sign_in(email="e2e-coupon@example.com", name="Coupon Tester")
    pg.open_home()

    admin_ctx = browser.new_context()
    admin_pg = Page(admin_ctx.new_page(), base)
    admin_pg.sign_in(email="admin@e2e.test", name="Admin")
    coupon = admin_pg.page.context.request.post(
        f"{base}/api/admin/coupons",
        data={"code": "E2ESTORE10", "kind": "percent", "value": 10,
              "description": "e2e checkout coupon"})
    check("the fixture coupon is created (admin API, setup only)", coupon.ok, coupon.text()[:200])
    admin_ctx.close()

    pg.page.click("#btn-buy")
    # DIVASTRO-149: the coupon box is a collapsed section of the store now.
    pg.page.wait_for_selector('.store-sec[data-sec="coupon"] > summary', timeout=10000)
    check("the coupon box starts folded away",
          not pg.page.locator("#coupon-code").is_visible())
    pg.page.click('.store-sec[data-sec="coupon"] > summary')
    pg.page.wait_for_selector("#coupon-code", state="visible", timeout=10000)
    pg.page.fill("#coupon-code", "E2ESTORE10")
    pg.page.click("#coupon-apply")
    pg.page.wait_for_timeout(1000)
    msg = pg.page.locator(".coupon-msg").inner_text()
    check("the coupon is accepted with a real message", msg.strip() != "", msg)
    check("the price line shows a struck-through original price",
          pg.page.locator('.pack[data-kind="questions"] .pack-price s, '
                          '.pack .pack-price s').count() > 0)

    before = pg.page.context.request.get(f"{base}/api/me").json()["user"]["credits"]
    pg.page.click('.buy-btn[data-sku="q10"]')
    pg.page.wait_for_timeout(1500)
    orders = pg.page.context.request.get(f"{base}/api/orders").json()
    latest = orders["orders"][0] if "orders" in orders else orders[0]
    check("the completed order actually used the discounted amount, not full price",
          latest["amount"] < 11100, str(latest))

    after = pg.page.context.request.get(f"{base}/api/me").json()["user"]["credits"]
    check("credits were still granted with the coupon applied", after > before,
          f"{before} -> {after}")

    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    check("no CSP violations", not pg.csp_violations(), str(pg.csp_violations()[:2]))
    ctx.close()


def upi_manual_claim_ui(p, browser, base: str) -> None:
    print("\n[manual-UPI checkout: VPA/QR shown, then a real UTR claim through the UI]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    pg.sign_in(email="e2e-upi-ui@example.com", name="UPI UI Tester")
    pg.open_home()

    pg.page.click("#btn-buy")
    pg.page.wait_for_selector('.buy-btn[data-sku="q10"]', timeout=10000)
    pg.page.click('.buy-btn[data-sku="q10"]')
    pg.page.wait_for_selector(".upi-vpa code", timeout=10000)
    check("a real VPA is shown", pg.page.locator(".upi-vpa code").inner_text().strip() != "")
    check("a reference code is shown", pg.page.locator(".upi-ref code").inner_text().strip() != "")

    pg.page.fill("#utr-last5", "99999")
    pg.page.click('.upi-claim button[type="submit"]')
    pg.page.wait_for_timeout(1000)
    check("the claim modal closes on success (no .modal-error shown)",
          pg.page.locator(".upi-claim .modal-error:visible").count() == 0)

    pending = pg.page.context.request.get(f"{base}/api/admin/upi/pending")
    check("submitting the claim does not itself grant credit (admin must verify)",
          pg.page.context.request.get(f"{base}/api/me").json()["user"]["credits"] == 3,   # the welcome gift only (DIVASTRO-154: 3)
          "credits moved before admin approval")

    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    check("no CSP violations", not pg.csp_violations(), str(pg.csp_violations()[:2]))
    ctx.close()


def payu_handoff(p, browser, base: str) -> None:
    print("\n[PayU: the hidden-form handoff reaches payu.in, zero CSP violations]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    pg.sign_in(email="e2e-payu@example.com", name="PayU Tester")
    pg.open_home()

    captured = {}

    def stub_payu(route):
        req = route.request
        captured["url"] = req.url
        captured["method"] = req.method
        captured["post_data"] = req.post_data
        route.fulfill(status=200, content_type="text/html", body="<html>payu sandbox stub</html>")

    pg.page.route("https://test.payu.in/**", stub_payu)

    pg.page.click("#btn-buy")
    pg.page.wait_for_selector('.buy-btn[data-sku="q10"]', timeout=10000)
    with pg.page.expect_navigation(timeout=10000):
        pg.page.click('.buy-btn[data-sku="q10"]')

    check("the hidden form really POSTs to PayU's sandbox endpoint",
          captured.get("url") == "https://test.payu.in/_payment", str(captured.get("url")))
    check("it's a real form POST, not a GET/redirect", captured.get("method") == "POST",
          str(captured.get("method")))
    body = captured.get("post_data") or ""
    check("the required hosted-checkout fields are all present in the POST body",
          all(f"name=\"{k}\"" in body for k in ("key", "txnid", "amount", "hash")) or
          all(k in body for k in ("key=", "txnid=", "amount=", "hash=")), body[:300])
    check("no CSP violation was logged during the handoff (the original DIVASTRO-72 bug)",
          not pg.csp_violations(), str(pg.csp_violations()))

    check("no console errors besides the stubbed-page navigation itself",
          not [e for e in pg.console_errors if "404" not in e and "Failed to load" not in e],
          "; ".join(pg.console_errors[:3]))
    ctx.close()


def payu_return_signed_and_tampered(p, browser, base: str) -> None:
    print("\n[a correctly signed PayU return grants once; a tampered one grants nothing]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    pg.sign_in(email="e2e-payu-return@example.com", name="PayU Return Tester")
    pg.open_home()

    start = pg.page.context.request.get(f"{base}/api/me").json()["user"]["credits"]
    order = pg.page.context.request.post(f"{base}/api/orders", data={"sku": "q10"}).json()
    f = order["checkout"]["fields"]

    good_hash = reverse_hash("success", f["productinfo"], f["firstname"], f["email"],
                              f["amount"], f["txnid"])
    r1 = pg.page.context.request.post(
        f"{base}/api/payu/return",
        form={"txnid": f["txnid"], "status": "success", "amount": f["amount"],
              "productinfo": f["productinfo"], "firstname": f["firstname"],
              "email": f["email"], "hash": good_hash, "mihpayid": "e2e_mihpay_1"},
        max_redirects=0)
    check("a correctly signed return redirects back with payu=ok",
          "payu=ok" in (r1.headers.get("location") or ""), str(r1.headers.get("location")))
    after = pg.page.context.request.get(f"{base}/api/me").json()["user"]["credits"]
    check("credit was actually granted", after == start + 10, f"{start} -> {after}")

    replay = pg.page.context.request.post(
        f"{base}/api/payu/return",
        form={"txnid": f["txnid"], "status": "success", "amount": f["amount"],
              "productinfo": f["productinfo"], "firstname": f["firstname"],
              "email": f["email"], "hash": good_hash, "mihpayid": "e2e_mihpay_1"},
        max_redirects=0)
    check("replaying the same valid return doesn't 500", replay.status in (303, 307, 302),
          str(replay.status))
    after_replay = pg.page.context.request.get(f"{base}/api/me").json()["user"]["credits"]
    check("replaying a valid return does not grant a second time", after_replay == after,
          f"{after} -> {after_replay}")

    order2 = pg.page.context.request.post(f"{base}/api/orders", data={"sku": "q10"}).json()
    f2 = order2["checkout"]["fields"]
    tampered = pg.page.context.request.post(
        f"{base}/api/payu/return",
        form={"txnid": f2["txnid"], "status": "success", "amount": "1.00",
              "productinfo": f2["productinfo"], "firstname": f2["firstname"],
              "email": f2["email"],
              "hash": reverse_hash("success", f2["productinfo"], f2["firstname"],
                                    f2["email"], f2["amount"], f2["txnid"]),
              "mihpayid": "e2e_mihpay_2"},
        max_redirects=0)
    check("a hash computed for a tampered amount is rejected",
          "payu=failed" in (tampered.headers.get("location") or ""),
          str(tampered.headers.get("location")))
    after_tampered = pg.page.context.request.get(f"{base}/api/me").json()["user"]["credits"]
    check("no credit was granted on the tampered return", after_tampered == after,
          f"{after} -> {after_tampered}")

    ctx.close()


def main() -> int:
    with server() as base, sync_playwright() as p:
        browser = p.chromium.launch()
        store_and_products(p, browser, base)
        buy_on_test_gateway(p, browser, base)
        coupon_at_checkout(p, browser, base)

    with server(extra_env={"ASTRO_GATEWAY": "upi_manual", "ASTRO_UPI_VPA": "e2e@upi"}) as base, \
         sync_playwright() as p:
        browser = p.chromium.launch()
        upi_manual_claim_ui(p, browser, base)

    with server(extra_env={
        "ASTRO_GATEWAY": "payu", "PAYU_MERCHANT_KEY": PAYU_KEY, "PAYU_SALT": PAYU_SALT,
        "PAYU_SANDBOX": "1",
        "PAYU_SURL": "http://127.0.0.1:1/api/payu/return",
        "PAYU_FURL": "http://127.0.0.1:1/api/payu/return",
    }) as base, sync_playwright() as p:
        browser = p.chromium.launch()
        payu_handoff(p, browser, base)
        payu_return_signed_and_tampered(p, browser, base)

    return check.finish("store (products, test gateway, coupon, UPI UI, PayU handoff)")


if __name__ == "__main__":
    raise SystemExit(main())
