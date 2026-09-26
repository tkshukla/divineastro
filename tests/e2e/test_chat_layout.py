"""The reading (chat) screen must be usable on a phone — and stay comfortable on
a laptop.

Written against the numbers measured on production on 2026-09-23 (DIVASTRO-69):
at 375x812 the answer area was 34px tall and the question box sat at y=878,
below the 812px screen. These assertions are the acceptance criteria of
DIVASTRO-73 (Q&A screen space) and the layout half of DIVASTRO-74 (mobile-first),
so the layout cannot quietly regress again.

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.e2e.test_chat_layout
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from playwright.sync_api import sync_playwright  # noqa: E402

from tests.e2e.harness import DESKTOPS, PHONES, Checker, Page, server  # noqa: E402

check = Checker()

# Interactive things a thumb has to hit. (selector, human name)
TOUCH_TARGETS = [
    ("#send", "send button"), ("#back", "back button"), (".vview", "Reading/Chart switch"),
    (".starter", "suggested question"), (".ghost-btn", "header button"),
    (".lang", "language button"), (".theme-toggle", "theme toggle"),
    (".credit-pill", "credits pill"),
]
MIN_TARGET = 44          # px — the common mobile guideline
MIN_META_FONT = 13       # px — chips, secondary text
MIN_BODY_FONT = 15       # px — the answers themselves


def context_args(p, spec: dict) -> dict:
    if "device" in spec:
        return dict(p.devices[spec["device"]])
    return dict(spec)


def visible_boxes(page, selector: str) -> list[dict]:
    return page.page.evaluate(
        """(s) => [...document.querySelectorAll(s)].map(e => {
              const r = e.getBoundingClientRect(), cs = getComputedStyle(e);
              return {w: r.width, h: r.height, fs: parseFloat(cs.fontSize),
                      shown: r.width > 0 && r.height > 0 && cs.visibility !== 'hidden'};
           }).filter(b => b.shown)""", selector)


def measure(pg: Page) -> dict:
    vh = pg.page.evaluate("window.innerHeight")
    vw = pg.page.evaluate("window.innerWidth")
    thread, comp = pg.rect("#thread"), pg.rect("#ask-form")
    return {
        "vh": vh, "vw": vw, "thread": thread, "composer": comp,
        "header": pg.rect(".site-header"), "topbar": pg.rect(".topbar"),
        "page_scroll": pg.page.evaluate(
            "document.scrollingElement.scrollHeight - window.innerHeight"),
        "h_overflow": pg.page.evaluate(
            "document.documentElement.scrollWidth - window.innerWidth"),
    }


def phone_checks(p, browser, base: str, name: str, spec: dict) -> None:
    print(f"\n[{name}]")
    ctx = browser.new_context(**context_args(p, spec))
    pg = Page(ctx.new_page(), base)
    pg.open_chat()
    m = measure(pg)
    vh = m["vh"]

    frac = m["thread"]["height"] / vh
    check(f"answer area is >= 55% of the screen ({m['thread']['height']:.0f}px of {vh}px)",
          frac >= 0.55, f"{frac:.0%}")
    check("question box is fully on screen without scrolling the page",
          m["composer"]["top"] >= 0 and m["composer"]["bottom"] <= vh + 0.5,
          f"top {m['composer']['top']:.0f}, bottom {m['composer']['bottom']:.0f}, screen {vh}")
    check("the page itself does not scroll (only the answers do)",
          m["page_scroll"] <= 1, f"{m['page_scroll']:.0f}px extra")
    screen_w = pg.page.viewport_size["width"]
    check("the page is exactly as wide as the screen (the browser did not zoom it out)",
          abs(m["vw"] - screen_w) <= 1, f"page {m['vw']}px on a {screen_w}px screen")
    check("no sideways scroll", m["h_overflow"] <= 1, f"{m['h_overflow']:.0f}px")
    # The reading stage locks the body, so scrollWidth cannot reveal a column that
    # has grown past the screen (a no-wrap suggestion strip once pushed Send to
    # x=1600). Assert on where the controls actually are.
    send = pg.rect("#send")
    check("the Send button is inside the screen horizontally",
          send is not None and send["left"] >= 0 and send["right"] <= m["vw"] + 0.5,
          f"x {send['left']:.0f}..{send['right']:.0f} of {m['vw']}")
    check("the chat column is no wider than the screen",
          pg.rect(".chat")["width"] <= m["vw"] + 0.5, f"{pg.rect('.chat')['width']:.0f}px")
    check("site header is compact (<= 64px)", m["header"]["height"] <= 64,
          f"{m['header']['height']:.0f}px")

    tag = pg.page.evaluate("document.querySelector('#q').tagName")
    check("the question box is a multi-line textarea", tag == "TEXTAREA", tag)

    # An 8-line question must be readable in full while typing.
    long_q = "\n".join(f"Question line {i + 1}" for i in range(8))     # 8 visual lines
    pg.page.fill("#q", long_q)
    pg.page.wait_for_timeout(200)
    st = pg.page.evaluate("(() => { const q = document.querySelector('#q');"
                          " return {sh: q.scrollHeight, ch: q.clientHeight,"
                          " lines: q.value.split('\\n').length}; })()")
    check("an 8-line question keeps its 8 lines", st["lines"] == 8, f"{st['lines']} lines kept")
    check("an 8-line question is fully visible while typing",
          st["lines"] == 8 and st["sh"] <= st["ch"] + 2,
          f"content {st['sh']}px in a {st['ch']}px box")
    m2 = measure(pg)
    check("with 8 lines typed, the question box is still fully on screen",
          m2["composer"]["bottom"] <= vh + 0.5 and m2["composer"]["top"] >= 0)
    check("with 8 lines typed, answers still get >= 35% of the screen",
          m2["thread"]["height"] / vh >= 0.35, f"{m2['thread']['height'] / vh:.0%}")

    # Touch keyboards: Enter must add a line, not send half a thought.
    pg.page.fill("#q", "")
    pg.page.click("#q")
    pg.page.keyboard.type("first")
    pg.page.keyboard.press("Enter")
    pg.page.keyboard.type("second")
    val = pg.page.input_value("#q")
    check("on a touch device Enter adds a new line instead of sending", "\n" in val, repr(val))
    pg.page.fill("#q", "")

    # Keyboard open: the visible area roughly halves.
    pg.page.set_viewport_size({"width": m["vw"], "height": int(vh * 0.5)})
    pg.page.wait_for_timeout(300)
    mk = measure(pg)
    kvh = mk["vh"]
    check("keyboard open: answers still get >= 35% of the visible area",
          mk["thread"]["height"] / kvh >= 0.35, f"{mk['thread']['height'] / kvh:.0%} of {kvh}px")
    check("keyboard open: the question box is still on screen",
          mk["composer"]["bottom"] <= kvh + 0.5 and mk["composer"]["top"] >= 0,
          f"bottom {mk['composer']['bottom']:.0f} of {kvh}")
    pg.page.set_viewport_size({"width": m["vw"], "height": vh})

    # The real Android keyboard cannot be emulated, but the cause of the "what I
    # type disappears behind the keyboard" bug can be pinned: the browser must be
    # told to resize the page for the keyboard, and the page must NOT also resize
    # itself (that second adjustment moved the box out of the window Chrome had
    # just scrolled to).
    meta = pg.page.evaluate("document.querySelector('meta[name=viewport]').content")
    check("the viewport asks the browser to resize the page for the keyboard",
          "interactive-widget=resizes-content" in meta, meta)
    self_resized = pg.page.evaluate(
        "document.documentElement.style.getPropertyValue('--app-h') "
        "|| document.body.style.height || ''")
    check("the page does not resize itself as well (no double adjustment)", self_resized == "",
          repr(self_resized))

    # Thumb-sized targets and readable text.
    for sel, label in TOUCH_TARGETS:
        boxes = visible_boxes(pg, sel)
        small = [b for b in boxes if min(b["w"], b["h"]) < MIN_TARGET - 0.5]
        if boxes:
            check(f"{label}: every visible one is >= {MIN_TARGET}px to tap", not small,
                  f"smallest {min(min(b['w'], b['h']) for b in boxes):.0f}px")
    for sel, label in [(".chip", "chart chips"), (".starter", "suggested questions"),
                       (".who p", "birth details line")]:
        boxes = visible_boxes(pg, sel)
        if boxes:
            smallest = min(b["fs"] for b in boxes)
            check(f"{label}: text is >= {MIN_META_FONT}px", smallest >= MIN_META_FONT - 0.01,
                  f"{smallest:.1f}px")
    body = visible_boxes(pg, ".msg.bot .bubble > p")
    if body:
        check(f"answer text is >= {MIN_BODY_FONT}px", min(b["fs"] for b in body) >= MIN_BODY_FONT - 0.01,
              f"{min(b['fs'] for b in body):.1f}px")

    # The whole point: with a thumb, ask and get an answer. Last, because sending
    # hides the suggestion chips the checks above measure.
    pg.page.fill("#q", "What does my chart say about career?")
    pg.page.tap("#send")
    try:
        pg.page.wait_for_selector(".msg.user", timeout=15000)
        sent = True
    except Exception:
        sent = False
    check("tapping Send on a phone sends the question", sent)
    if sent:
        pg.page.wait_for_function(
            "document.querySelectorAll('.msg.bot').length >= 2", timeout=30000)
        check("an answer arrives", True)
        check("the answer has Copy and Share buttons",
              pg.page.locator(".msg.bot .msg-actions button").count() >= 2)
        ans = pg.rect(".msg.bot:last-of-type .bubble") or pg.rect(".msg.bot .bubble")
        check("the answer is as wide as the screen allows (no sideways overflow)",
              ans["right"] <= m["vw"] + 0.5, f"right edge {ans['right']:.0f} of {m['vw']}")

    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    check("no CSP violations", not pg.csp_violations(), str(pg.csp_violations()[:2]))
    check("no server errors (5xx)", not pg.failed_requests, "; ".join(pg.failed_requests[:3]))
    ctx.close()


def desktop_checks(p, browser, base: str, name: str, spec: dict) -> None:
    print(f"\n[{name}]")
    ctx = browser.new_context(**context_args(p, spec))
    pg = Page(ctx.new_page(), base)
    pg.open_chat()
    m = measure(pg)
    vh = m["vh"]
    frac = m["thread"]["height"] / vh
    check(f"answer area is >= 60% of the screen ({m['thread']['height']:.0f}px of {vh}px)",
          frac >= 0.60, f"{frac:.0%}")
    check("question box is on screen", m["composer"]["bottom"] <= vh + 0.5)
    check("no sideways scroll", m["h_overflow"] <= 1)
    check("the Send button is inside the screen horizontally",
          pg.rect("#send")["right"] <= m["vw"] + 0.5)

    # Enter sends on a keyboard device, Shift+Enter adds a line.
    pg.page.click("#q")
    pg.page.keyboard.type("line one")
    pg.page.keyboard.press("Shift+Enter")
    pg.page.keyboard.type("line two")
    val = pg.page.input_value("#q")
    check("Shift+Enter adds a new line", "\n" in val, repr(val))
    pg.page.fill("#q", "What does my chart say about career?")
    pg.page.keyboard.press("Enter")
    try:
        pg.page.wait_for_selector(".msg.user", timeout=15000)
        sent = True
    except Exception:
        sent = False
    check("Enter sends the question", sent)
    if sent:
        pg.page.wait_for_selector(".msg.bot:nth-of-type(3), .msg.bot .bubble p", timeout=30000)
        check("the question box is emptied after sending", pg.page.input_value("#q") == "")
        hbox = pg.rect("#q")["height"]
        check("the question box shrinks back to one line after sending", hbox <= 80,
              f"{hbox:.0f}px")

    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    check("no CSP violations", not pg.csp_violations())
    check("no server errors (5xx)", not pg.failed_requests, "; ".join(pg.failed_requests[:3]))
    ctx.close()


def box_on_screen(pg: Page) -> tuple[bool, str]:
    """Is the question box really inside the visible screen? (Not merely 'has a
    size' - a box on the hidden chart side or below the fold both fail this.)"""
    r = pg.rect("#q")
    vh = pg.page.evaluate("window.innerHeight")
    if r is None or r["height"] < 20:
        return False, "not rendered"
    return (r["top"] >= 0 and r["bottom"] <= vh + 0.5), f"top {r['top']:.0f}, bottom {r['bottom']:.0f}, screen {vh}"


def every_way_in(p, browser, base: str) -> None:
    """The question box must be there however the person got to the chat.

    Regression (owner, 2026-09-24): tapping 'Chart & Dashas' once left the phone
    on the chart side for good; the next trip to the chat, including the new
    one-tap route from the home box, showed a screen with NO question box."""
    print("\n[the question box, however you arrive]")
    spec = {"viewport": {"width": 412, "height": 839}, "is_mobile": True,
            "has_touch": True, "device_scale_factor": 2}
    from tests.e2e.harness import BIRTH

    ctx = browser.new_context(**spec)
    pg = Page(ctx.new_page(), base)
    pg.open_chat()
    ok, d = box_on_screen(pg)
    check("fresh chat: the box is on screen", ok, d)

    pg.page.tap('.vview[data-view="chart"]')
    pg.page.wait_for_timeout(200)
    check("(sanity) the chart side has no question box, by design", not box_on_screen(pg)[0])
    pg.page.evaluate("showStage('stage-home')")
    pg.page.wait_for_selector("#free-badge:not([hidden])")
    pg.page.tap("#free-badge")
    pg.page.wait_for_selector("#stage-chat.active")
    pg.page.wait_for_timeout(400)
    ok, d = box_on_screen(pg)
    check("after peeking at the chart, then tapping the home box: the box is on screen", ok, d)
    check("...and the Reading tab is the one highlighted",
          pg.page.evaluate("document.querySelector('.vview.active').dataset.view") == "chat")

    pg.page.tap('.vview[data-view="chart"]')
    pg.page.evaluate("async (b) => { await castChart(b); showStage('stage-chat'); }", BIRTH)
    pg.page.wait_for_selector("#thread .msg.bot", timeout=30000)
    pg.page.wait_for_timeout(400)
    ok, d = box_on_screen(pg)
    check("after peeking at the chart, then opening a chart afresh: the box is on screen", ok, d)
    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    ctx.close()

    # Situations a phone really is in.
    situations = [
        ("landscape phone 800x360", 800, 360, False, 120),
        ("landscape phone 915x412", 915, 412, False, 150),
        ("landscape phone 640x360", 640, 360, False, 120),
        ("portrait, keyboard open 360x330", 360, 330, True, 150),
        ("landscape, keyboard open 800x200", 800, 200, True, 100),
        ("tablet 600x960", 600, 960, False, 400),
    ]
    for label, w, h, kbd, min_thread in situations:
        ctx = browser.new_context(viewport={"width": w, "height": h}, is_mobile=True,
                                  has_touch=True, device_scale_factor=2)
        pg = Page(ctx.new_page(), base)
        pg.open_chat()
        if kbd:
            pg.page.evaluate("document.body.classList.add('kbd')")   # what focusing the box does
            pg.page.wait_for_timeout(200)
        ok, d = box_on_screen(pg)
        th = pg.rect("#thread")["height"]
        check(f"{label}: the box is on screen", ok, d)
        check(f"{label}: the answer still gets >= {min_thread}px", th >= min_thread, f"{th:.0f}px")
        ctx.close()


def main() -> int:
    only = set(sys.argv[1:])         # optional: profile names, for a quick run
    with server() as base, sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            for name, spec in PHONES.items():
                if not only or name in only:
                    phone_checks(p, browser, base, name, spec)
            for name, spec in DESKTOPS.items():
                if not only or name in only:
                    desktop_checks(p, browser, base, name, spec)
            if not only:
                every_way_in(p, browser, base)
        finally:
            browser.close()
    return check.finish("chat layout")


if __name__ == "__main__":
    raise SystemExit(main())
