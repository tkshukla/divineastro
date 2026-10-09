"""Feedback submission (then appearing in the admin inbox), and the admin
panel: user grant/block, coupon CRUD, the traffic panel, and the UPI verify
queue (DIVASTRO-72, flows 12 and 13).

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.e2e.test_feedback_admin
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from playwright.sync_api import sync_playwright  # noqa: E402

from tests.e2e.harness import DESKTOPS, Checker, Page, server  # noqa: E402

check = Checker()


def open_admin(pg: Page, tab: str) -> None:
    pg.sign_in(email="admin@e2e.test", name="Admin")
    pg.page.goto(pg.base + "/admin", wait_until="domcontentloaded")
    pg.page.wait_for_selector("#panel", state="visible", timeout=10000)
    pg.page.click(f'.atab[data-tab="{tab}"]')
    pg.page.wait_for_selector(f"#pane-{tab}", state="visible", timeout=10000)


def feedback_then_admin_inbox(p, browser, base: str) -> None:
    print("\n[submit feedback, then it shows up in the admin inbox]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    pg.sign_in(email="e2e-feedback@example.com", name="Feedback Tester")
    pg.page.goto(base + "/feedback", wait_until="domcontentloaded")
    pg.page.wait_for_selector("#form-card", state="visible", timeout=10000)

    message = "This is a real end-to-end test message, well over ten characters."
    pg.page.select_option("#category", index=1)
    pg.page.fill("#message", message)
    pg.page.click("#submit")
    pg.page.wait_for_selector("#thanks", state="visible", timeout=10000)
    check("the thank-you panel appears after a real submission", True)

    mine = pg.page.context.request.get(f"{base}/api/feedback/mine").json()
    check("the submission is recorded under the user's own feedback",
          message in str(mine), str(mine)[:300])

    admin_ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    admin_pg = Page(admin_ctx.new_page(), base)
    open_admin(admin_pg, "feedback")
    admin_pg.page.wait_for_selector("#fb-list", timeout=10000)
    check("the same feedback appears in the admin inbox",
          message[:30] in admin_pg.page.locator("#fb-list").inner_text())
    admin_ctx.close()

    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    check("no CSP violations", not pg.csp_violations(), str(pg.csp_violations()[:2]))
    ctx.close()


def user_grant_and_block(p, browser, base: str) -> None:
    print("\n[admin panel: grant credits to a user, then block them]")
    target_ctx = browser.new_context()
    target_pg = Page(target_ctx.new_page(), base)
    target_pg.sign_in(email="e2e-managed@example.com", name="Managed User")
    target_ctx.close()

    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    # Grant and block both go through a native confirm() in admin.js;
    # Playwright auto-dismisses dialogs by default, which silently no-ops
    # the action unless a handler accepts them first.
    pg.page.on("dialog", lambda d: d.accept())
    open_admin(pg, "users")

    pg.page.fill("#pane-users input[type=search], #pane-users input", "e2e-managed@example.com")
    pg.page.wait_for_timeout(500)
    pg.page.click(".btn-manage")
    pg.page.wait_for_selector("#um-grant", state="visible", timeout=10000)

    pg.page.select_option("#um-action", "credits")
    pg.page.fill("#um-amount", "5")
    pg.page.fill("#um-note", "e2e grant")
    pg.page.click("#um-grant")
    pg.page.wait_for_timeout(1000)

    managed = pg.page.context.request.get(f"{base}/api/admin/users?q=e2e-managed").json()
    user_id = managed["users"][0]["id"]
    detail = pg.page.context.request.get(f"{base}/api/admin/users/{user_id}").json()
    check("the grant actually landed server-side (8 = 3 free + 5 granted; DIVASTRO-154)",
          detail["balance"] == 8, str(detail))

    pg.page.fill("#um-reason", "e2e block test")
    pg.page.click("#um-block")
    pg.page.wait_for_timeout(1000)
    detail_after = pg.page.context.request.get(f"{base}/api/admin/users/{user_id}").json()
    check("the block actually landed server-side",
          detail_after["user"]["blocked"] is True, str(detail_after["user"]))

    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    check("no CSP violations", not pg.csp_violations(), str(pg.csp_violations()[:2]))
    ctx.close()


def coupon_crud(p, browser, base: str) -> None:
    print("\n[admin panel: create, toggle and delete a coupon]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    pg.page.on("dialog", lambda d: d.accept())
    open_admin(pg, "coupons")

    pg.page.click("#btn-toggle-coupon-form")
    pg.page.wait_for_selector("#coupon-form", state="visible", timeout=10000)
    pg.page.fill("#c-code", "E2ETEST10")
    pg.page.select_option("#c-kind", index=0)
    pg.page.fill("#c-value", "10")
    pg.page.fill("#c-desc", "e2e test coupon")
    pg.page.click("#coupon-form button[type=submit]")
    pg.page.wait_for_timeout(1000)

    row = pg.page.locator('#coupon-list [data-code="E2ETEST10"], #coupon-list:has-text("E2ETEST10")')
    check("the new coupon appears in the list", row.count() > 0)

    preview = pg.page.context.request.post(
        f"{base}/api/coupons/preview", data={"code": "E2ETEST10", "sku": "q10"}).json()
    check("the coupon is actually usable server-side", preview.get("valid") is True, str(preview))

    pg.page.click('#coupon-list button[data-act="delete"]')
    pg.page.wait_for_timeout(1000)

    preview_after = pg.page.context.request.post(
        f"{base}/api/coupons/preview", data={"code": "E2ETEST10", "sku": "q10"}).json()
    check("the deleted coupon is no longer usable", preview_after.get("valid") is not True,
          str(preview_after))

    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    check("no CSP violations", not pg.csp_violations(), str(pg.csp_violations()[:2]))
    ctx.close()


def traffic_panel(p, browser, base: str) -> None:
    print("\n[admin panel: the traffic panel loads real data]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    open_admin(pg, "traffic")

    pg.page.wait_for_selector("#tr-tiles", timeout=10000)
    tiles_text = pg.page.locator("#tr-tiles").inner_text()
    check("the traffic tiles render with real numbers, not an empty shell",
          tiles_text.strip() != "", tiles_text[:200])

    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    check("no CSP violations", not pg.csp_violations(), str(pg.csp_violations()[:2]))
    ctx.close()


def upi_verify_queue(p, browser, base: str) -> None:
    print("\n[admin panel: the UPI verify queue approves a claim]")
    # A real claim to verify: a buyer puts in a UTR on the upi_manual gateway.
    buyer_ctx = browser.new_context(
        **DESKTOPS["desktop_1440x800"],
        extra_http_headers={})
    buyer_pg = Page(buyer_ctx.new_page(), base)
    buyer_pg.sign_in(email="e2e-upi-buyer@example.com", name="UPI Buyer")
    order = buyer_pg.page.context.request.post(f"{base}/api/orders", data={"sku": "q10"}).json()
    claim = buyer_pg.page.context.request.post(
        f"{base}/api/orders/upi-claim",
        data={"order_id": order["order"]["id"], "utr_last5": "12345"})
    check("the buyer's UPI claim is accepted (queued, not yet granted)", claim.ok,
          claim.text()[:200])
    buyer_ctx.close()

    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    pg.page.on("dialog", lambda d: d.accept())
    open_admin(pg, "upi")
    pg.page.wait_for_selector("#upi-list .row", timeout=10000)
    check("the pending claim appears in the admin queue",
          pg.page.locator("#upi-list .row").count() >= 1)

    pg.page.click('#upi-list .row button[data-act="approve"]')
    pg.page.wait_for_timeout(1000)

    buyer_me = pg.page.context.request.get(
        f"{base}/api/admin/users?q=e2e-upi-buyer").json()
    check("the admin can see the buyer's account", len(buyer_me.get("users", [])) >= 1,
          str(buyer_me))

    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    check("no CSP violations", not pg.csp_violations(), str(pg.csp_violations()[:2]))
    ctx.close()


def main() -> int:
    with server(extra_env={"ASTRO_GATEWAY": "upi_manual", "ASTRO_UPI_VPA": "e2e@upi"}) as base, \
         sync_playwright() as p:
        browser = p.chromium.launch()
        feedback_then_admin_inbox(p, browser, base)
        user_grant_and_block(p, browser, base)
        coupon_crud(p, browser, base)
        traffic_panel(p, browser, base)
        upi_verify_queue(p, browser, base)
        browser.close()
    return check.finish("feedback inbox + admin (users, coupons, traffic, UPI)")


if __name__ == "__main__":
    raise SystemExit(main())
