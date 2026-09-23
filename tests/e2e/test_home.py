"""The home page: the free-questions hook and the feature showcase (DIVASTRO-71).

The rule this exists to enforce: the "First N questions FREE" claim must be the
number the SERVER says (ASTRO_FREE_QUESTIONS), never a number typed into the page,
and it must not appear at all until the server has said it. A wrong or stale
promise on a home page is worse than no promise.

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.e2e.test_home
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from playwright.sync_api import sync_playwright  # noqa: E402

from tests.e2e.harness import Checker, Page, server  # noqa: E402

check = Checker()
FEATURES = 6


def run_profile(p, browser, base: str, name: str, args: dict, expect_n: int) -> None:
    print(f"\n[{name}]")
    ctx = browser.new_context(**args)
    pg = Page(ctx.new_page(), base)
    pg.open_home()
    pg.page.wait_for_selector("#free-badge:not([hidden])", timeout=10000)
    vh = pg.page.viewport_size["height"]

    main = pg.page.inner_text("#free-badge-main")
    check(f"badge says the server's number ({expect_n})", str(expect_n) in main and "FREE" in main, repr(main))
    sub = pg.page.inner_text("#free-badge-sub")
    check("badge says no card is needed", "No card" in sub, repr(sub))
    b, cta = pg.rect("#free-badge"), pg.rect("#home-cta")
    check("badge is visible without scrolling", b["bottom"] <= vh, f"bottom {b['bottom']:.0f} of {vh}")
    check("main button is visible without scrolling", cta["bottom"] <= vh, f"bottom {cta['bottom']:.0f} of {vh}")
    check("badge sits above the main button", b["bottom"] <= cta["top"] + 1)

    feats = pg.page.eval_on_selector_all("#feat-grid .feat span", "els => els.map(e => e.textContent.trim())")
    check(f"{FEATURES} feature tiles, all with text", len(feats) == FEATURES and all(feats), str(feats))
    check("the ornaments are present (toran, mandala, Om)",
          pg.page.locator(".toran").count() == 1 and pg.page.locator(".mandala-bg").count() == 1
          and pg.page.locator(".om").count() == 1)

    # Hindi
    pg.page.click('.lang[data-lang="hi"]')
    pg.page.wait_for_timeout(300)
    hi = pg.page.inner_text("#free-badge-main")
    check("Hindi badge carries the same number", str(expect_n) in hi and "मुफ़्त" in hi, repr(hi))
    check("Hindi button text", "निःशुल्क" in pg.page.inner_text("#home-cta"))
    hi_feats = pg.page.eval_on_selector_all("#feat-grid .feat span", "els => els.map(e => e.textContent.trim())")
    check("Hindi features differ from English and are all filled", all(hi_feats) and hi_feats != feats)
    pg.page.click('.lang[data-lang="en"]')

    # Signed in: the badge shows what the person actually has, not the promotion.
    pg.sign_in()
    pg.open_home()
    pg.page.wait_for_selector("#free-badge:not([hidden])", timeout=10000)
    signed = pg.page.inner_text("#free-badge-main")
    check("signed in, the badge shows the questions they have left", "left" in signed and str(expect_n) in signed, repr(signed))
    check("signed in, the sign-up promise line is gone", not pg.page.is_visible("#free-badge-sub"))

    # Sign out ON THE PAGE, without a reload: the promise must come straight back.
    # (It did not: the server only sent the free-question number to signed-out
    # visitors, so a page that loaded signed in never knew it. Found when the
    # owner signed out on a phone and the box was missing.)
    me = pg.page.evaluate("fetch('/api/me').then(r => r.json())")
    check("/api/me carries the free-question number when signed in too",
          me.get("free_questions") == expect_n, str(me.get("free_questions")))
    pg.page.click("#btn-acct")
    pg.page.click('.acct-drop [data-act="logout"]')
    pg.page.wait_for_function(
        "!document.querySelector('#free-badge').hidden && document.querySelector('#free-badge-main').textContent.includes('FREE')",
        timeout=8000)
    check("after signing out on the page, the FREE badge appears without a reload",
          str(expect_n) in pg.page.inner_text("#free-badge-main"), repr(pg.page.inner_text("#free-badge-main")))

    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:2]))
    check("no CSP violations", not pg.csp_violations())
    ctx.close()


def never_wrong(p, browser, base: str) -> None:
    """The badge must stay hidden until /api/me has answered, and if it never
    answers, must stay hidden — not fall back to a number the page made up."""
    print("\n[the badge never guesses]")
    ctx = browser.new_context(viewport={"width": 412, "height": 915})
    pg = Page(ctx.new_page(), base)

    def slow(route):
        pg.page.wait_for_timeout(1500)
        route.continue_()
    pg.page.route("**/api/me", slow)
    pg.page.goto(base + "/", wait_until="domcontentloaded")
    pg.page.wait_for_function("typeof showStage === 'function'")
    pg.page.wait_for_timeout(300)
    check("hidden while the server has not answered yet", pg.page.is_hidden("#free-badge"))
    pg.page.wait_for_selector("#free-badge:not([hidden])", timeout=10000)
    check("appears once the server has answered", True)
    ctx.close()

    ctx = browser.new_context(viewport={"width": 412, "height": 915})
    pg = Page(ctx.new_page(), base)
    pg.page.route("**/api/me", lambda route: route.fulfill(status=500, body="Internal Server Error"))
    pg.page.goto(base + "/", wait_until="domcontentloaded")
    pg.page.wait_for_function("typeof showStage === 'function'")
    pg.page.wait_for_timeout(1500)
    check("stays hidden when the server errors (no invented number)", pg.page.is_hidden("#free-badge"))
    check("the page still works without the badge (main button present)", pg.page.is_visible("#home-cta"))
    ctx.close()


def main() -> int:
    phones = {
        "pixel7_412x915": {"viewport": {"width": 412, "height": 915}, "is_mobile": True, "has_touch": True},
        "android_360x640": {"viewport": {"width": 360, "height": 640}, "is_mobile": True, "has_touch": True},
        "iphone_375x812": {"viewport": {"width": 375, "height": 812}, "is_mobile": True, "has_touch": True},
        "laptop_1366x768": {"viewport": {"width": 1366, "height": 768}},
    }
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            # Default server: the server says 10.
            with server() as base:
                for name, args in phones.items():
                    run_profile(p, browser, base, name, args, expect_n=10)
                never_wrong(p, browser, base)
            # A server configured for 25: the page must say 25 — proof it is not hard-coded.
            with server({"ASTRO_FREE_QUESTIONS": "25"}) as base:
                run_profile(p, browser, base, "server says 25 (pixel7)", phones["pixel7_412x915"], expect_n=25)
        finally:
            browser.close()
    return check.finish("home page")


if __name__ == "__main__":
    raise SystemExit(main())
