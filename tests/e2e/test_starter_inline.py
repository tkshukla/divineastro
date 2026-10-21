"""DIVASTRO-157 in a browser: the Rs 21 Starter line under a free answer, by topic.

  a. A new account (its 3 free questions) on a 390px phone: under the first answer one
     compact line matched to the question ("Want the full picture on your marriage
     timing? ... for ₹21"), reported as starter_inline_shown <topic>; the question box
     stays on screen. The next answer replaces it (one at a time, new topic, no report
     offer beside it). It is still there under the last free answer (0 left). Tapping
     it reports starter_inline_click and opens the store on the Starter. Hindi.
  b. 360x640 and 320x568: with the line on screen the question box is fully visible,
     the page does not scroll, nothing scrolls sideways.
  c. Not shown: a paying account (credits added), an account that bought the Starter.
  d. A signed-out visitor: under the guest answer, below the sign-up line; tapping it
     opens the sign-in sheet (the same entry point as the other Starter offers).

Screenshots: $ASTRO_SHOTS_DIR (default tests/e2e/shots/) starter_inline_*.png.

    python -m tests.e2e.test_starter_inline
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from playwright.sync_api import sync_playwright  # noqa: E402

from tests.e2e.harness import BIRTH, Checker, Page, server, set_lang  # noqa: E402

check = Checker()
SHOTS = Path(os.environ.get("ASTRO_SHOTS_DIR") or Path(__file__).parent / "shots")
SKU = "starter_email3"
LINE = "#thread .starter-inline"
PHONE_UA = ("Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/128.0.0.0 Mobile Safari/537.36")
_n = [0]


def phone(browser, w: int = 390, h: int = 844):
    _n[0] += 1                      # a different visitor to the server's day-scoped hash each time
    return browser.new_context(viewport={"width": w, "height": h}, is_mobile=True, has_touch=True,
                               device_scale_factor=2,
                               user_agent=PHONE_UA.replace("128.0.0.0", f"128.0.1.{_n[0]}"))


def shot(pg: Page, name: str) -> None:
    SHOTS.mkdir(parents=True, exist_ok=True)
    pg.page.screenshot(path=str(SHOTS / f"starter_inline_{name}.png"))


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


def ask(pg: Page, text: str) -> None:
    n = pg.page.locator("#thread .msg.bot").count()
    pg.page.fill("#q", text)
    pg.page.click("#send")
    pg.page.wait_for_function(
        "(n) => document.querySelectorAll('#thread .msg.bot').length > n", arg=n, timeout=30000)
    pg.page.wait_for_function("() => !state.busy", timeout=30000)
    pg.page.wait_for_timeout(500)


def box_visible(pg: Page) -> tuple[bool, str]:
    """The question box (and its send button) inside the screen, the page not scrolled."""
    m = pg.page.evaluate("""() => {
        const f = document.querySelector('#ask-form').getBoundingClientRect();
        const q = document.querySelector('#q').getBoundingClientRect();
        return {vh: window.innerHeight, form_top: f.top, form_bottom: f.bottom, q_top: q.top,
                q_bottom: q.bottom, scrolled: window.scrollY,
                hscroll: document.documentElement.scrollWidth - window.innerWidth}; }""")
    ok = (m["form_top"] >= 0 and m["form_bottom"] <= m["vh"] + 0.5 and m["q_bottom"] <= m["vh"]
          and m["q_top"] >= 0 and m["scrolled"] == 0 and m["hscroll"] <= 1)
    return ok, str(m)


def line_not_over_box(pg: Page) -> bool:
    return pg.page.evaluate("""() => { const l = document.querySelector('#thread .starter-inline');
        if (!l) return true;
        const r = l.getBoundingClientRect(), f = document.querySelector('#ask-form').getBoundingClientRect();
        const t = document.querySelector('#thread').getBoundingClientRect();
        // inside the thread's scroll box: whatever part of it is visible ends above the box
        return l.closest('#thread') !== null && Math.min(r.bottom, t.bottom) <= f.top + 1; }""")


def new_account_chat(pg: Page, email: str, lang: str = "en") -> None:
    pg.sign_in(email=email, name="Inline")
    pg.open_home()
    if lang != "en":
        set_lang(pg.page, lang)
    pg.page.evaluate("async (b) => { await castChart(b); showStage('stage-chat'); }", BIRTH)
    pg.page.wait_for_selector("#thread .msg.bot", timeout=30000)
    pg.page.evaluate("state.provider = 'off'")
    pg.page.wait_for_timeout(400)


def free_answers(browser, base: str) -> None:
    print("\n[a. a new account's free answers carry the topic line, one at a time]")
    ctx = phone(browser)
    pg = Page(ctx.new_page(), base)
    events = track(pg)
    new_account_chat(pg, "inline-en@example.com")
    check("before any answer there is no line", pg.page.locator(LINE).count() == 0)

    ask(pg, "When will I get married?")
    pg.page.wait_for_selector(LINE, timeout=10000)
    line = pg.page.locator(LINE)
    text = " ".join(line.inner_text().split())
    check("under the first free answer: one line about marriage timing, ₹21",
          line.count() == 1 and line.get_attribute("data-topic") == "marriage"
          and "Want the full picture on your marriage timing? Get 3 detailed answers by email for ₹21." in text, text)
    check("it sits right under the answer, inside the thread",
          pg.page.evaluate("document.querySelector('#thread .starter-inline').previousElementSibling.classList.contains('msg')"))
    check("'starter_inline_shown marriage' is reported",
          {"name": "starter_inline_shown", "detail": "marriage"} in events, str(events))
    check("no other offer card beside it", pg.page.locator("#thread .offer-card").count() == 1)
    ok, m = box_visible(pg)
    check("390px: the question box is fully on screen, the page not scrolled", ok, m)
    check("390px: the line never covers the question box", line_not_over_box(pg))
    h = line.evaluate("e => e.getBoundingClientRect().height")
    check(f"it is compact (<= 120px tall at 390px, got {h:.0f})", h <= 120)
    shot(pg, "en_1_marriage")
    line.scroll_into_view_if_needed()            # the reader scrolls down to it
    pg.page.wait_for_timeout(200)
    r, f = line.bounding_box(), pg.rect("#ask-form")
    ok, m = box_visible(pg)
    check("scrolled to the line: it is above the question box, and the box is still on screen",
          ok and r and f and r["y"] + r["height"] <= f["top"] + 1, f"{r} {m}")
    shot(pg, "en_1b_marriage_line")

    ask(pg, "Will I get a promotion in my career this year?")
    pg.page.wait_for_selector(f'{LINE}[data-topic="career"]', timeout=10000)
    check("the next answer replaces it: still exactly one line, now about the career",
          pg.page.locator(LINE).count() == 1 and "your career?" in pg.page.inner_text(LINE))
    check("...under the newest answer",
          pg.page.evaluate("""() => { const bots = document.querySelectorAll('#thread .msg.bot');
              return document.querySelector('#thread .starter-inline').previousElementSibling === bots[bots.length - 1]; }"""))
    ok, m = box_visible(pg)
    check("the question box is still on screen", ok, m)

    ask(pg, "How will my health be?")
    pg.page.wait_for_selector(f'{LINE}[data-topic="health"]', timeout=10000)
    check("the last free answer (0 left) carries it too, about health",
          pg.page.locator(LINE).count() == 1 and pg.page.evaluate("acct.user.credits") == 0)
    ok, m = box_visible(pg)
    check("after three answers the question box is still on screen", ok, m)
    shot(pg, "en_2_health")

    pg.page.click(f"{LINE} .offer-go")
    pg.page.wait_for_selector(".modal.store .pack.focus", timeout=10000)
    check("tapping it opens the store on the Starter",
          pg.page.get_attribute(".modal.store .pack.focus", "data-sku") == SKU)
    check("'starter_inline_click health' is reported",
          {"name": "starter_inline_click", "detail": "health"} in events, str(events))
    check("the line is gone once tapped", pg.page.locator(LINE).count() == 0)
    check("the store's own starter_shown is not double-counted",
          not [e for e in events if e.get("name") == "starter_shown"], str(events))
    pg.page.click(f'.modal.store .pack[data-sku="{SKU}"] .buy-btn')
    pg.page.wait_for_selector(".starter-done", timeout=10000)
    check("buying from it reports starter_click 'inline'",
          {"name": "starter_click", "detail": "inline"} in events, str(events))
    pg.page.click("#starter-ok")
    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    ctx.close()

    print("\n[a2. Hindi]")
    ctx = phone(browser)
    pg = Page(ctx.new_page(), base)
    new_account_chat(pg, "inline-hi@example.com", lang="hi")
    ask(pg, "मेरी शादी कब होगी?")
    pg.page.wait_for_selector(LINE, timeout=10000)
    text = " ".join(pg.page.inner_text(LINE).split())
    check("in Hindi: the marriage line, ₹21, the Hindi button",
          "अपने विवाह के समय की पूरी तस्वीर चाहिए?" in text and "₹21" in text and "स्टार्टर" in text, text)
    ok, m = box_visible(pg)
    check("Hindi: the question box is on screen", ok, m)
    shot(pg, "hi_1_marriage")
    ctx.close()


def small_phones(browser, base: str) -> None:
    print("\n[b. small phones: the question box stays on screen]")
    for w, h in ((360, 640), (320, 568)):
        ctx = phone(browser, w, h)
        pg = Page(ctx.new_page(), base)
        new_account_chat(pg, f"inline-{w}@example.com")
        ask(pg, "Will my finances and wealth improve?")
        pg.page.wait_for_selector(LINE, timeout=10000)
        check(f"{w}x{h}: the money line is there", pg.page.get_attribute(LINE, "data-topic") == "money")
        ok, m = box_visible(pg)
        check(f"{w}x{h}: question box fully on screen, no page scroll, no sideways scroll", ok, m)
        check(f"{w}x{h}: the line does not cover the box", line_not_over_box(pg))
        b = pg.page.locator(f"{LINE} .offer-go").bounding_box()
        check(f"{w}x{h}: its button is a real tap target (>= 44px)", b and b["height"] >= 43.5, str(b))
        # focus the box the way a thumb does: it is still reachable
        pg.page.click("#q")
        pg.page.wait_for_timeout(300)
        q = pg.rect("#q")
        check(f"{w}x{h}: tapping into the box keeps it on screen", q and q["bottom"] <= h and q["top"] >= 0, str(q))
        shot(pg, f"{w}x{h}")
        ctx.close()


def not_for(browser, base: str) -> None:
    print("\n[c. no line for a paying account or after the Starter is bought]")
    ctx = phone(browser)
    pg = Page(ctx.new_page(), base)
    events = track(pg)
    pg.open_chat(email="inline-paying@example.com", name="Paying")        # credits added (10)
    ask(pg, "When will I get married?")
    pg.page.wait_for_timeout(500)
    check("credits beyond the free allowance: no Starter line", pg.page.locator(LINE).count() == 0)
    check("...and no starter_inline_shown", not [e for e in events if e.get("name") == "starter_inline_shown"])
    ctx.close()

    ctx = phone(browser)
    pg = Page(ctx.new_page(), base)
    new_account_chat(pg, "inline-bought@example.com")
    ask(pg, "When will I get married?")
    pg.page.wait_for_selector(LINE, timeout=10000)
    pg.page.click(f"{LINE} .offer-go")
    pg.page.wait_for_selector(f'.modal.store .pack[data-sku="{SKU}"] .buy-btn', timeout=10000)
    pg.page.click(f'.modal.store .pack[data-sku="{SKU}"] .buy-btn')
    pg.page.wait_for_selector(".starter-done", timeout=10000)
    pg.page.click("#starter-ok")
    ask(pg, "Will my career grow?")
    pg.page.wait_for_timeout(500)
    check("after buying the Starter the next free answer has no line", pg.page.locator(LINE).count() == 0)
    ctx.close()


def guest(browser, base: str) -> None:
    print("\n[d. a signed-out visitor: under the guest answer]")
    ctx = phone(browser)
    pg = Page(ctx.new_page(), base)
    events = track(pg)
    pg.open_home()
    pg.page.wait_for_function("typeof acct !== 'undefined' && acct.freeKnown")
    pg.page.evaluate("async (b) => { await castChart(b); await saveBirth(b); showStage('stage-chat'); }", BIRTH)
    pg.page.wait_for_selector("#thread .msg.bot", timeout=30000)
    pg.page.evaluate("state.provider = 'off'")
    pg.page.wait_for_timeout(400)
    ask(pg, "Will I get a new job this year?")
    pg.page.wait_for_selector(".offer-card.guest-cta", timeout=30000)
    pg.page.wait_for_selector(LINE, timeout=10000)
    check("the guest answer: the sign-up line, then one Starter line about the career",
          pg.page.locator(LINE).count() == 1 and pg.page.get_attribute(LINE, "data-topic") == "career"
          and pg.page.evaluate("document.querySelector('#thread .starter-inline').previousElementSibling.classList.contains('guest-cta')"))
    check("'starter_inline_shown career' is reported",
          {"name": "starter_inline_shown", "detail": "career"} in events, str(events))
    ok, m = box_visible(pg)
    check("the question box is on screen with both lines", ok, m)
    shot(pg, "guest")
    pg.page.click(f"{LINE} .offer-go")
    pg.page.wait_for_selector(".modal-backdrop", timeout=10000)
    check("tapping it opens the sign-in sheet first", pg.page.locator(".modal.store").count() == 0
          and pg.page.locator(".modal-backdrop").count() == 1)
    check("'starter_inline_click career' is reported",
          {"name": "starter_inline_click", "detail": "career"} in events, str(events))
    ctx.close()


def main() -> int:
    with server() as base, sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            free_answers(browser, base)
            small_phones(browser, base)
            not_for(browser, base)
            guest(browser, base)
        finally:
            browser.close()
    return check.finish("Starter line under a free answer (e2e)")


if __name__ == "__main__":
    sys.exit(main())
