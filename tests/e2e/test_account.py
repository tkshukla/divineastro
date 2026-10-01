"""Sign in (dev login), sign out, and the blocked-user message (DIVASTRO-72,
flow 2). Drives the real sign-in UI (including the native prompt() dialog),
not harness.py's API-level sign_in() shortcut, for at least the sign-in leg.

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.e2e.test_account
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from playwright.sync_api import sync_playwright  # noqa: E402

from tests.e2e.harness import Checker, DESKTOPS, Page, server  # noqa: E402

check = Checker()


def sign_in_and_out(p, browser, base: str) -> None:
    print("\n[sign in via the UI, then sign out]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    pg.open_home()
    pg.page.wait_for_selector("#btn-signin, #btn-credits", timeout=10000)

    check("starts signed out: #btn-signin is shown", pg.page.locator("#btn-signin").count() > 0)
    check("not yet showing the credits pill", pg.page.locator("#btn-credits").count() == 0)

    pg.page.on("dialog", lambda d: d.accept("e2e-ui@example.com"))
    pg.page.click("#btn-signin")
    pg.page.click('.oauth-btn.dev[data-provider="dev"]')
    pg.page.wait_for_selector("#btn-credits", timeout=10000)

    check("signed in: the credits pill appears", pg.page.locator("#btn-credits").count() > 0)
    check("signed in: #btn-signin is gone", pg.page.locator("#btn-signin").count() == 0)
    me = pg.page.context.request.get(f"{base}/api/me").json()
    check("the session really is this account",
          (me.get("user") or {}).get("email") == "e2e-ui@example.com", str(me))

    pg.page.click("#btn-acct")
    pg.page.click('.acct-drop button[data-act="logout"]')
    pg.page.wait_for_selector("#btn-signin", timeout=10000)
    check("signed out: #btn-signin is back", pg.page.locator("#btn-signin").count() > 0)
    check("signed out: the credits pill is gone", pg.page.locator("#btn-credits").count() == 0)
    me_after = pg.page.context.request.get(f"{base}/api/me").json()
    check("the server session is really cleared too", me_after.get("user") is None,
          str(me_after))

    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    check("no CSP violations", not pg.csp_violations(), str(pg.csp_violations()[:2]))
    ctx.close()


def blocked_user_message(p, browser, base: str) -> None:
    print("\n[a blocked user sees why, not a silent failure]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    pg.open_home()
    pg.sign_in(email="e2e-blocked@example.com", name="Blocked Target")
    me = pg.page.context.request.get(f"{base}/api/me").json()
    target_id = me["user"]["id"]

    admin_ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    admin_pg = Page(admin_ctx.new_page(), base)
    # ASTRO_ADMIN_EMAILS=admin@e2e.test is set by harness.server() itself.
    admin_pg.sign_in(email="admin@e2e.test", name="Admin")
    admin_me = admin_pg.page.context.request.get(f"{base}/api/me").json()
    check("the admin account really is flagged admin", admin_me["user"]["is_admin"] is True,
          str(admin_me["user"]))
    block = admin_pg.page.context.request.post(
        f"{base}/api/admin/users/{target_id}/block",
        data={"blocked": True, "reason": "e2e test"})
    check("admin can block the target user", block.ok, f"{block.status} {block.text()[:200]}")
    admin_ctx.close()

    # The blocked user reloads. Blocking doesn't revoke the cookie, but
    # current_user() treats a blocked user as if signed out (auth.py), so the
    # UI genuinely shows #btn-signin again here — not a leftover stale state.
    pg.page.on("dialog", lambda d: d.accept("e2e-blocked@example.com"))
    pg.page.reload(wait_until="domcontentloaded")
    pg.page.wait_for_function("typeof showStage === 'function'")
    pg.page.wait_for_selector("#btn-signin", timeout=10000)
    check("a blocked user looks signed-out after reload, not stuck in a broken state",
          pg.page.locator("#btn-signin").count() > 0)
    pg.page.click("#btn-signin")
    pg.page.click('.oauth-btn.dev[data-provider="dev"]')
    pg.page.wait_for_selector(".modal-error:not([hidden])", timeout=10000)
    error_text = pg.page.locator(".modal-error").inner_text()
    check("the blocked attempt shows an explanation, not a blank/generic failure",
          "suspend" in error_text.lower(), error_text)
    check("still shows signed out (the block was not silently bypassed)",
          pg.page.locator("#btn-credits").count() == 0)

    # This sub-flow deliberately triggers a 403 (the suspension itself), which
    # Chromium legitimately logs as a console error — not asserting "zero
    # console errors" here, only that nothing ELSE broke alongside it.
    unexpected = [e for e in pg.console_errors if "403" not in e]
    check("no OTHER console errors beyond the expected 403", not unexpected,
          "; ".join(unexpected[:3]))
    check("no CSP violations", not pg.csp_violations(), str(pg.csp_violations()[:2]))
    ctx.close()


def username_password_signup_and_login(p, browser, base: str) -> None:
    print("\n[username/password: create an account with no email, sign out, log back in]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    pg.open_home()
    pg.page.wait_for_selector("#btn-signin", timeout=10000)

    pg.page.click("#btn-signin")
    pg.page.wait_for_selector("#toggle-password-auth", timeout=10000)
    pg.page.click("#toggle-password-auth")
    pg.page.wait_for_selector("#password-auth:not([hidden])", timeout=5000)
    check("defaults to 'Create account' mode", "Create" in pg.page.inner_text("#pa-submit"))
    check("the no-recovery trade-off is stated up front, not hidden",
          "recover" in pg.page.inner_text("#pa-note").lower())

    username = "e2e_pw_user"
    pg.page.fill("#pa-username", username)
    pg.page.fill("#pa-password", "correcthorse123")
    pg.page.click("#pa-submit")
    pg.page.wait_for_selector("#btn-credits", timeout=10000)
    check("signed in immediately after creating the account",
          pg.page.locator("#btn-credits").count() > 0)

    me = pg.page.context.request.get(f"{base}/api/me").json()
    check("the account really has no email attached", me["user"]["email"] == "", str(me["user"]))
    check("the account displays by the chosen username",
          me["user"]["name"] == username, me["user"]["name"])

    pg.page.click("#btn-acct")
    acct_label = pg.page.inner_text("#btn-acct")
    check("the account button shows the real username, not a generic 'Account' fallback",
          username in acct_label, acct_label)
    pg.page.click('.acct-drop button[data-act="logout"]')
    pg.page.wait_for_selector("#btn-signin", timeout=10000)

    pg.page.click("#btn-signin")
    pg.page.click("#toggle-password-auth")
    pg.page.wait_for_selector("#password-auth:not([hidden])", timeout=5000)
    pg.page.click("#pa-mode-toggle")
    check("mode toggle switches the submit button to 'Log in'",
          "Log in" in pg.page.inner_text("#pa-submit"))
    pg.page.fill("#pa-username", username)
    pg.page.fill("#pa-password", "correcthorse123")
    pg.page.click("#pa-submit")
    pg.page.wait_for_selector("#btn-credits", timeout=10000)
    check("logging back in with the same credentials works", True)

    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    check("no CSP violations", not pg.csp_violations(), str(pg.csp_violations()[:2]))
    ctx.close()


def main() -> int:
    with server() as base, sync_playwright() as p:
        browser = p.chromium.launch()
        sign_in_and_out(p, browser, base)
        blocked_user_message(p, browser, base)
        username_password_signup_and_login(p, browser, base)
        browser.close()
    return check.finish("account (sign in/out, blocked user, username/password)")


if __name__ == "__main__":
    raise SystemExit(main())
