"""A new visitor's first minutes (DIVASTRO-87).

Live data, 2026-09-27: of 44 accounts only 11 (25%) ever made a chart, and 76% of
older sign-ups never did. Two causes are pinned here:

1. Sign-in is a full-page redirect, so a person who typed their first question,
   was asked to sign in, and came back landed on a blank home page: the chart and
   the question were both gone. They must come back to their reading, with the
   question asked for them.
2. The birth form buried the three things a reading needs (date, time, place)
   under name, gender and a long midnight warning.

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.e2e.test_first_run
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from playwright.sync_api import sync_playwright  # noqa: E402

from tests.e2e.harness import BIRTH, Checker, Page, server  # noqa: E402

check = Checker()
QUESTION = "Will I get a promotion this year?"
PLACE = {"label": "Delhi, India", "latitude": 28.6519, "longitude": 77.2315, "timezone": "Asia/Kolkata"}

PHONE = {"viewport": {"width": 412, "height": 915}, "is_mobile": True, "has_touch": True, "device_scale_factor": 2}
SMALL = {"viewport": {"width": 360, "height": 640}, "is_mobile": True, "has_touch": True, "device_scale_factor": 3}
TINY = {"viewport": {"width": 320, "height": 568}, "is_mobile": True, "has_touch": True, "device_scale_factor": 2}


def on_screen(pg: Page, selector: str) -> tuple[bool, str]:
    r = pg.rect(selector)
    vh = pg.page.evaluate("window.innerHeight")
    if r is None or r["height"] <= 0:
        return False, "not rendered"
    return r["top"] >= 0 and r["bottom"] <= vh + 0.5, f"{selector}: {r['top']:.0f}..{r['bottom']:.0f} of {vh}"


def form_checks(browser, base: str, name: str, spec: dict) -> None:
    print(f"\n[the birth form — {name}]")
    ctx = browser.new_context(**spec)
    pg = Page(ctx.new_page(), base)
    pg.open_home()
    pg.page.wait_for_selector("#home-cta")
    pg.page.tap("#home-cta")
    pg.page.wait_for_selector("#stage-birth.active")
    pg.page.wait_for_timeout(300)

    for sel, what in (("#f-date", "date of birth"), ("#f-time", "time of birth"), ("#f-place", "place of birth")):
        ok, d = on_screen(pg, sel)
        check(f"{what} is on screen without scrolling", ok, d)
    order = pg.page.evaluate("""() => ['#f-date','#f-time','#f-unknown','#f-place','#f-name','#f-gender']
        .map(s => document.querySelector(s).getBoundingClientRect().top)""")
    check("order: date and time first, then 'don't know the time', then place, then the optional name and gender",
          order[0] <= order[2] <= order[3] <= order[4] and order[1] <= order[2] and order[4] <= order[5] + 1, str([round(x) for x in order]))
    label = pg.page.inner_text("#cast .label").strip()
    check("the button says what the person gets, not 'cast a chart'", label == "Show my reading", repr(label))

    hint = lambda: pg.page.is_visible("#time-hint")   # noqa: E731
    check("the midnight note is NOT shown for the default time (12:00)", not hint())
    pg.page.fill("#f-time", "02:30")
    check("it appears for an early-morning birth (02:30)", hint())
    pg.page.fill("#f-time", "14:00")
    check("and goes away again for the afternoon", not hint())
    pg.page.fill("#f-time", "02:30")
    pg.page.check("#f-unknown")
    check("and is hidden when the time is unknown", not hint())
    pg.page.uncheck("#f-unknown")

    # The reorder must not have broken the form: it still casts.
    pg.page.fill("#f-date", "1985-06-15")
    pg.page.fill("#f-time", "10:30")
    pg.page.evaluate("(p) => choosePlace(p)", PLACE)
    pg.page.tap("#cast")
    try:
        # A cast ends on the dashboard (existing behaviour); the reading is built either way.
        pg.page.wait_for_function("!!state.sessionId", timeout=30000)
        pg.page.wait_for_selector("#thread .msg.bot", state="attached", timeout=30000)
        cast = pg.page.evaluate("!document.querySelector('#birth-error') || document.querySelector('#birth-error').hidden")
    except Exception:
        cast = False
    check("filling the form and pressing the button still builds the chart and reading", cast)
    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:2]))
    check("no CSP violations", not pg.csp_violations())
    ctx.close()


def answered(pg: Page, timeout: int = 30000) -> bool:
    try:
        pg.page.wait_for_function("document.querySelectorAll('#thread .msg.bot').length >= 2", timeout=timeout)
        return True
    except Exception:
        return False


def resume_checks(browser, base: str) -> None:
    print("\n[sign-in round trip: the chart and the question survive]")
    ctx = browser.new_context(**PHONE)
    pg = Page(ctx.new_page(), base)
    # 1. signed out: cast a chart, then try to ask (the sign-in wall)
    pg.open_home()
    pg.page.evaluate("async (b) => { await castChart(b); await saveBirth(b); showStage('stage-chat'); }", BIRTH)
    pg.page.wait_for_selector("#thread .msg.bot", timeout=30000)
    pg.page.fill("#q", QUESTION)
    pg.page.tap("#send")
    try:
        pg.page.wait_for_selector(".modal .oauth-btn", timeout=10000)
        walled = True
    except Exception:
        walled = False
    check("signed out, asking a question opens the sign-in wall", walled)
    parked = pg.page.evaluate("localStorage.getItem('astro.pendingQuestion')")
    check("the question is parked so the redirect cannot lose it",
          bool(parked) and json.loads(parked)["q"] == QUESTION, str(parked)[:80])
    check("the chart they cast is parked too", bool(pg.page.evaluate("localStorage.getItem('astro.pendingBirth')")))

    # 2. the OAuth return: a brand-new page load carrying ?welcome=1, now signed in
    pg.sign_in("firstrun@example.com", "First Runner")
    pg.page.goto(base + "/?welcome=1", wait_until="domcontentloaded")
    try:
        pg.page.wait_for_selector("#stage-chat.active", timeout=30000)
        landed_chat = True
    except Exception:
        landed_chat = False
    check("back from sign-in they land in their READING, not on a blank home page", landed_chat)
    try:
        pg.page.wait_for_selector("#thread .msg.user", timeout=30000)
        asked = QUESTION in pg.page.inner_text("#thread .msg.user")
    except Exception:
        asked = False
    check("the question they had typed was asked for them", asked)
    check("and it was answered", answered(pg))
    check("the parked question is used once, then gone",
          pg.page.evaluate("localStorage.getItem('astro.pendingQuestion')") is None)
    check("the chart they cast is now saved to their account",
          pg.page.evaluate("state.births.length") == 1)
    pg.page.wait_for_timeout(2000)                      # the balance updates when the stream ends
    credits = pg.page.evaluate("fetch('/api/me').then(r => r.json()).then(d => d.user.credits)")
    check("the question cost exactly one of the free questions", credits == pg.page.evaluate("acct.freeQuestions") - 1, f"{credits} left")
    check("the address bar is clean (?welcome removed)", "welcome" not in pg.page.url, pg.page.url)
    ok, d = on_screen(pg, "#q")
    check("the question box is on screen", ok, d)
    unexpected = [m for m in pg.console_errors if "401" not in m]     # the 401 IS the sign-in wall
    check("no console errors (apart from the expected 401 at the sign-in wall)", not unexpected, "; ".join(unexpected[:2]))
    check("no CSP violations", not pg.csp_violations())
    ctx.close()

    # 3. an old parked question is never asked out of the blue
    print("\n[edge cases]")
    ctx = browser.new_context(**PHONE)
    pg = Page(ctx.new_page(), base)
    pg.sign_in("stale@example.com", "Stale")
    pg.open_home()
    pg.page.evaluate("async (b) => { await castChart(b); await saveBirth(b); }", BIRTH)
    stale = json.dumps({"q": "an old question", "at": int(time.time() * 1000) - 3 * 60 * 60 * 1000})
    pg.page.evaluate("(v) => localStorage.setItem('astro.pendingQuestion', v)", stale)
    pg.page.goto(base + "/?welcome=0", wait_until="domcontentloaded")
    pg.page.wait_for_selector("#stage-chat.active", timeout=30000)
    pg.page.wait_for_timeout(2500)
    check("a returning user with a saved chart lands in the reading", pg.page.is_visible("#stage-chat.active"))
    check("a 3-hour-old parked question is NOT asked", pg.page.locator("#thread .msg.user").count() == 0)
    check("and it is discarded", pg.page.evaluate("localStorage.getItem('astro.pendingQuestion')") is None)
    ctx.close()

    ctx = browser.new_context(**PHONE)
    pg = Page(ctx.new_page(), base)
    pg.sign_in("nochart@example.com", "No Chart")
    pg.page.goto(base + "/?welcome=1", wait_until="domcontentloaded")
    try:
        pg.page.wait_for_selector("#stage-birth.active", timeout=15000)
        form = True
    except Exception:
        form = False
    check("a brand-new user with no chart yet lands on the birth form", form)
    ctx.close()

    ctx = browser.new_context(**PHONE)
    pg = Page(ctx.new_page(), base)
    pg.sign_in("plainvisit@example.com", "Plain")
    pg.open_home()
    pg.page.evaluate("async (b) => { await castChart(b); await saveBirth(b); }", BIRTH)
    pg.page.goto(base + "/", wait_until="domcontentloaded")
    pg.page.wait_for_selector("#stage-home.active", timeout=15000)
    pg.page.wait_for_timeout(2000)
    check("an ordinary visit (no ?welcome) is NOT hijacked: a signed-in user still sees the home page",
          pg.page.is_visible("#stage-home.active") and not pg.page.is_visible("#stage-chat.active"))
    ctx.close()


def main() -> int:
    with server() as base, sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            for name, spec in (("412x915", PHONE), ("360x640", SMALL), ("320x568", TINY)):
                form_checks(browser, base, name, spec)
            resume_checks(browser, base)
        finally:
            browser.close()
    return check.finish("first run")


if __name__ == "__main__":
    raise SystemExit(main())
