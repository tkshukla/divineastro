"""The WhatsApp bar under the answer box, in a real browser (DIVASTRO-164).

On a Hindi city festival page at 390x844 (a common Android size): the bar is on
the first or second screen, both buttons are tap-sized and on one row, a tap
sends strip_share / strip_channel with detail "top" (the strip at the foot
still sends no detail), nothing breaks the production CSP, and at 320px the
page does not scroll sideways (the buttons stack).

    ~/.venvs/divineastro/bin/python -u -m tests.e2e.test_top_bar
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from playwright.sync_api import sync_playwright  # noqa: E402

from tests.e2e.harness import Checker, Page, enforce_csp, server  # noqa: E402

check = Checker()
SHOT_DIR = os.environ.get("E2E_SHOT_DIR", "/tmp")
PATH = "/hi/tyohar/karwa-chauth-2026/lucknow"

# Record every analytics beacon instead of sending it, and keep the WhatsApp
# links from leaving the test (they open wa.me / whatsapp.com in a new tab).
_INIT = """
window.__beacons = [];
navigator.sendBeacon = (url, body) => { window.__beacons.push({url, body: String(body)}); return true; };
document.addEventListener('click', (e) => {
  if (e.target.closest('a[target=_blank]')) e.preventDefault();
}, true);
"""


def events(page) -> list[dict]:
    return [json.loads(b["body"]) for b in page.evaluate("window.__beacons")
            if b["url"].endswith("/api/event")]


def phone_390(browser, base: str) -> None:
    print("\n[390x844, Hindi city festival page]")
    ctx = browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True,
                              has_touch=True, device_scale_factor=2)
    enforce_csp(ctx, base)
    page = ctx.new_page()
    page.add_init_script(_INIT)
    pg = Page(page, base)
    page.goto(base + PATH, wait_until="load")
    page.wait_for_function("typeof window.daTrack === 'function'")

    bar = pg.rect(".wa-top")
    check("the bar is on the page", bar is not None)
    check("on the first or second screen (top < 2 x 844px)", bar and bar["top"] < 2 * 844, str(bar))
    check("right under the answer box",
          page.evaluate("document.querySelector('.box.answer').nextElementSibling"
                        ".classList.contains('wa-top')"))
    links = page.locator(".wa-top a")
    check("two buttons", links.count() == 2, str(links.count()))
    boxes = [links.nth(i).bounding_box() for i in range(links.count())]
    check("each at least 44px tall", all(b and b["height"] >= 44 for b in boxes), str(boxes))
    check("one row at 390px", len(boxes) == 2 and abs(boxes[0]["y"] - boxes[1]["y"]) < 1, str(boxes))
    check("inside the screen", all(b["x"] >= 0 and b["x"] + b["width"] <= 390 for b in boxes), str(boxes))
    check("labels in Hindi", links.nth(0).inner_text().strip() == "परिवार को भेजें"
          and "चैनल" in links.nth(1).inner_text(), links.nth(0).inner_text())

    href = links.nth(0).get_attribute("href") or ""
    text = unquote(href.removeprefix("https://wa.me/?text="))
    url = text.rsplit(" ", 1)[-1]
    answer = page.inner_text(".box.answer")
    check("the message carries the answer's moonrise time", "8:06" in text and "8:06" in answer, text)
    check("tagged utm_campaign=top-share",
          parse_qs(urlsplit(url).query).get("utm_campaign") == ["top-share"], url)
    page.screenshot(path=os.path.join(SHOT_DIR, "topbar_hi_city_390.png"))

    links.nth(0).tap()
    links.nth(1).tap()
    page.wait_for_timeout(300)
    got = [(e["name"], e["detail"]) for e in events(page)]
    check("tapping Forward sends strip_share with detail top", ("strip_share", "top") in got, str(got))
    check("tapping the channel sends strip_channel with detail top",
          ("strip_channel", "top") in got, str(got))

    page.locator("#stay-strip a[data-strip=strip_share]").scroll_into_view_if_needed()
    page.locator("#stay-strip a[data-strip=strip_share]").tap()
    page.wait_for_timeout(300)
    got = [(e["name"], e["detail"]) for e in events(page)]
    check("the foot strip still sends strip_share with no detail", ("strip_share", "") in got, str(got))
    check("no CSP violations", not pg.csp_violations(), str(pg.csp_violations()))
    check("no console errors", not pg.console_errors, str(pg.console_errors[:3]))
    ctx.close()


def phone_320(browser, base: str) -> None:
    print("\n[320x568: no sideways scroll]")
    ctx = browser.new_context(viewport={"width": 320, "height": 568}, is_mobile=True,
                              has_touch=True, device_scale_factor=2)
    page = ctx.new_page()
    for path in (PATH, "/hi/tyohar/diwali-2026", "/ta/panchang/chennai", "/ml/kundali-milan",
                 "/hi/purnima-2026", "/muhurat/vivah-2026"):
        page.goto(base + path, wait_until="load")
        wide = page.evaluate("document.documentElement.scrollWidth")
        boxes = page.evaluate("""[...document.querySelectorAll('.wa-top a')].map((a) => {
            const r = a.getBoundingClientRect(); return {l: r.left, r: r.right, h: r.height}; })""")
        check(f"{path}: no sideways scroll, the bar fits, buttons >= 44px",
              wide <= 320 and len(boxes) == 2
              and all(b["l"] >= 0 and b["r"] <= 320 and b["h"] >= 44 for b in boxes),
              f"scrollWidth {wide}, {boxes}")
        if path == PATH:
            page.screenshot(path=os.path.join(SHOT_DIR, "topbar_hi_city_320.png"))
    ctx.close()


def main() -> int:
    with server() as base, sync_playwright() as p:
        browser = p.chromium.launch()
        phone_390(browser, base)
        phone_320(browser, base)
        browser.close()
    return check.finish("top WhatsApp bar")


if __name__ == "__main__":
    raise SystemExit(main())
