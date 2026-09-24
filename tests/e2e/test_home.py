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
    sub = pg.page.inner_text("#free-badge-sub")
    check("signed in, the second line says a tap opens the chat (not 'sign up')",
          "ask" in sub.lower() and "sign up" not in sub.lower(), repr(sub))

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


BADGE_ANIMS = "(() => document.getAnimations({subtree: true}).filter(a => a.effect.target && a.effect.target.closest && a.effect.target.closest('#free-badge'))"


def festival_lights(p, browser, base: str) -> None:
    """The lights must catch the eye without hurting anyone: nothing fast, only the
    sign-up promise gets them, and 'reduce motion' turns them off."""
    print("\n[festival lights]")
    ctx = browser.new_context(viewport={"width": 412, "height": 915})
    pg = Page(ctx.new_page(), base)
    pg.open_home()
    pg.page.wait_for_selector("#free-badge.promo", timeout=8000)
    durs = pg.page.evaluate(BADGE_ANIMS + ".map(a => a.effect.getTiming().duration))()")
    check("the promise is animated (ring, glow, bulbs, shimmer, flame)", len(durs) >= 5, f"{len(durs)} animations")
    fastest = min(durs) if durs else 0
    check("nothing is fast: every animation cycle is >= 1.9s (photosensitivity: < 3 flashes a second)",
          fastest >= 1900, f"fastest cycle {fastest:.0f}ms")
    bulbs = pg.page.evaluate("getComputedStyle(document.querySelector('#free-badge .lights'), '::before').animationName")
    check("the bulb string exists", "bulbs" in bulbs, bulbs)
    ctx.close()

    ctx = browser.new_context(viewport={"width": 412, "height": 915}, reduced_motion="reduce")
    pg = Page(ctx.new_page(), base)
    pg.open_home()
    pg.page.wait_for_selector("#free-badge.promo", timeout=8000)
    n = pg.page.evaluate(BADGE_ANIMS + ".length)()")
    check("with 'reduce motion' on, nothing animates", n == 0, f"{n} running")
    check("...but the badge is still fully visible", pg.page.is_visible("#free-badge-main"))
    ctx.close()

    ctx = browser.new_context(viewport={"width": 412, "height": 915})
    pg = Page(ctx.new_page(), base)
    pg.sign_in()
    pg.open_home()
    pg.page.wait_for_selector("#free-badge:not([hidden])", timeout=8000)
    check("a signed-in person's balance box has no lights", not pg.page.evaluate("document.querySelector('#free-badge').classList.contains('promo')")
          and pg.page.evaluate(BADGE_ANIMS + ".length)()") == 0)
    ctx.close()


def tappable(p, browser, base: str) -> None:
    """The box is a button. Signed out it is the sign-up button; signed in it goes
    straight to the AI chat (owner request)."""
    print("\n[the box is tappable]")
    from tests.e2e.harness import BIRTH

    # signed out -> sign-in
    ctx = browser.new_context(viewport={"width": 412, "height": 915}, is_mobile=True, has_touch=True)
    pg = Page(ctx.new_page(), base)
    pg.open_home()
    pg.page.wait_for_selector("#free-badge:not([hidden])", timeout=10000)
    tag = pg.page.evaluate("document.querySelector('#free-badge').tagName")
    check("the box is a real button (keyboard and screen-reader friendly)", tag == "BUTTON", tag)
    label = pg.page.get_attribute("#free-badge", "aria-label") or ""
    check("a screen reader hears the whole message", "FREE" in label and "sign up" in label, label)
    box = pg.rect("#free-badge")
    check("it is big enough to tap (>= 44px tall)", box["height"] >= 44, f"{box['height']:.0f}px")
    pg.page.tap("#free-badge")
    pg.page.wait_for_selector(".modal .oauth-btn", timeout=5000)
    check("signed out: tapping it opens sign-in", True)
    pg.page.evaluate("closeModal()")
    pg.page.focus("#free-badge")
    pg.page.keyboard.press("Enter")
    pg.page.wait_for_selector(".modal .oauth-btn", timeout=5000)
    check("...and it works from the keyboard (Enter)", True)
    ctx.close()

    # signed in, no chart yet -> the birth form (a reading needs a chart first)
    ctx = browser.new_context(viewport={"width": 412, "height": 915}, is_mobile=True, has_touch=True)
    pg = Page(ctx.new_page(), base)
    pg.sign_in("newcomer@example.com", "New Comer")
    pg.open_home()
    pg.page.wait_for_selector("#free-badge:not([hidden])", timeout=10000)
    pg.page.tap("#free-badge")
    pg.page.wait_for_selector("#stage-birth.active", timeout=5000)
    check("signed in with no chart: tapping it opens the birth form", True)
    ctx.close()

    # signed in with a saved chart -> straight into the chat, and it STAYS there
    ctx = browser.new_context(viewport={"width": 412, "height": 915}, is_mobile=True, has_touch=True)
    pg = Page(ctx.new_page(), base)
    pg.sign_in("regular@example.com", "Regular")
    pg.open_home()
    pg.page.evaluate("async (b) => { await castChart(b); await saveBirth(b); }", BIRTH)
    pg.open_home()                                            # a fresh visit: nothing open
    pg.page.wait_for_selector("#free-badge:not([hidden])", timeout=10000)
    check("the home screen is showing", pg.page.evaluate("document.querySelector('#stage-home').classList.contains('active')"))
    pg.page.tap("#free-badge")
    pg.page.wait_for_selector("#stage-chat.active", timeout=15000)
    pg.page.wait_for_timeout(2500)                            # the dashboard used to take over a moment later
    still = pg.page.evaluate("document.querySelector('#stage-chat').classList.contains('active')")
    check("signed in with a saved chart: tapping it opens the AI chat and it stays there", still)
    check("the question box is ready", pg.page.is_visible("#q") and pg.page.is_enabled("#q"))
    check("the reading is loaded (opening answer is on screen)", pg.page.locator("#thread .msg.bot").count() >= 1)

    # and with a chart already open, straight back to the chat
    pg.page.evaluate("showStage('stage-home')")
    pg.page.tap("#free-badge")
    pg.page.wait_for_selector("#stage-chat.active", timeout=5000)
    check("with a chart already open, one tap returns to the chat", True)
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
                tappable(p, browser, base)
                festival_lights(p, browser, base)
            # A server configured for 25: the page must say 25 — proof it is not hard-coded.
            with server({"ASTRO_FREE_QUESTIONS": "25"}) as base:
                run_profile(p, browser, base, "server says 25 (pixel7)", phones["pixel7_412x915"], expect_n=25)
        finally:
            browser.close()
    return check.finish("home page")


if __name__ == "__main__":
    raise SystemExit(main())
