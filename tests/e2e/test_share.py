"""WhatsApp share buttons outside Kundali Milan (DIVASTRO-107).

The home Today strip, the Panchang tool and a server-rendered SEO page, on the
360px phone most of this audience uses. (The Milan button is in test_milan.)

    ~/.venvs/divineastro/bin/python -u -m tests.e2e.test_share
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from playwright.sync_api import sync_playwright  # noqa: E402

from tests.e2e.harness import DESKTOPS, PHONES, Checker, Page, server  # noqa: E402

check = Checker()
SHOT_DIR = os.environ.get("E2E_SHOT_DIR", "/tmp")
ANDROID_UA = ("Mozilla/5.0 (Linux; Android 13; SM-A145F) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36")


def message(href: str) -> tuple[str, str, dict]:
    """(text, shared url, its query) from a wa.me href."""
    if not href.startswith("https://wa.me/?text="):
        return "", "", {}
    text = unquote(href[len("https://wa.me/?text="):])
    url = text.rsplit(" ", 1)[-1]
    return text, url, parse_qs(urlsplit(url).query)


def utm_ok(q: dict, campaign: str) -> bool:
    return q == {"utm_source": ["whatsapp"], "utm_medium": ["share"], "utm_campaign": [campaign]}


def phone(browser):
    ctx = browser.new_context(**PHONES["android_360x640"], user_agent=ANDROID_UA)
    page = ctx.new_page()
    page.add_init_script("window.__shared = []; navigator.share = (d) => { window.__shared.push(d); return Promise.resolve(); };")
    return ctx, page


def today_strip(p, browser, base: str) -> None:
    print("\n[Home Today strip: share today's Rahu Kaal for the city]")
    ctx, page = phone(browser)
    pg = Page(page, base)
    pg.open_home()
    pg.page.wait_for_selector("#today-strip:not(.loading)", timeout=15000)
    pg.page.wait_for_function("document.querySelector('#today-share').href.includes('rahu-kaal')", timeout=10000)
    btn = pg.page.locator("#today-share")
    check("the share button shows once today's values are in", btn.is_visible())
    text, url, q = message(btn.get_attribute("href") or "")
    rahu = pg.page.inner_text("#today-rahu").split("·")[0].strip()
    check("the message names the city and today's Rahu Kaal",
          "Rahu Kaal in New Delhi" in text and rahu in text, text)
    check("Delhi links to the bare /rahu-kaal page (its canonical URL)",
          url.startswith("https://divineastro.org/rahu-kaal?"), url)
    check("tagged utm_campaign=rahukaal", utm_ok(q, "rahukaal"), str(q))
    box = pg.rect("#today-share")
    check("tap target at least 44px", box and box["height"] >= 44, str(box))
    check("fits 360px, no sideways scroll",
          box and box["right"] <= 360 and pg.page.evaluate("document.documentElement.scrollWidth <= innerWidth"),
          str(box))
    head = pg.rect(".today-head")
    check("the strip header stays one row", head and head["height"] <= 52, str(head))
    pg.page.locator("#today-strip").screenshot(path=os.path.join(SHOT_DIR, "today_share_360.png"))

    pg.page.tap("#today-share")
    pg.page.wait_for_timeout(300)
    shared = pg.page.evaluate("window.__shared")
    check("a phone tap opens the share sheet with the same text",
          len(shared) == 1 and shared[0].get("text") == f"{text}", str(shared))
    check("tapping share does not open the Panchang tool", pg.page.is_visible("#stage-home"))

    # A city with its own SEO page links there, in Hindi when the UI is Hindi.
    pg.page.click('button.lang[data-lang="hi"]')
    pg.page.click("#today-city")
    pg.page.fill("#today-place", "Mumbai")
    pg.page.wait_for_selector("#today-results li", timeout=10000)
    pg.page.click("#today-results li >> nth=0")
    pg.page.wait_for_function("document.querySelector('#today-share').href.includes('mumbai')", timeout=15000)
    text, url, q = message(pg.page.get_attribute("#today-share", "href") or "")
    check("Mumbai links to /rahu-kaal/mumbai", url.startswith("https://divineastro.org/rahu-kaal/mumbai?"), url)
    check("Hindi: the message is in Hindi", "राहु काल" in text and "मुंबई" in text, text)
    check("Hindi: the button label is Hindi", pg.page.inner_text("#today-share").strip() == "भेजें")
    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    check("no CSP violations", not pg.csp_violations(), str(pg.csp_violations()[:2]))
    ctx.close()


def panchang_tool(p, browser, base: str) -> None:
    print("\n[Panchang tool: share the day's panchang]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    pg.open_home()
    pg.page.click("#open-panchang")
    pg.page.wait_for_selector("#panchang-share", state="visible", timeout=15000)
    pg.page.fill("#pa-place", "Jaipur")
    pg.page.wait_for_selector("#pa-results li", timeout=10000)
    # dispatch_event: the suggestion list currently renders UNDER the already-loaded
    # result card (a pre-existing stacking issue), so a real click would hit the card.
    pg.page.locator("#pa-results li").first.dispatch_event("click")
    pg.page.wait_for_function("document.querySelector('#panchang-share')?.href.includes('jaipur')", timeout=15000)
    btn = pg.page.locator("#panchang-share")
    text, url, q = message(btn.get_attribute("href") or "")
    check("the message has the city, tithi, nakshatra and Rahu Kaal",
          all(w in text for w in ("Jaipur", "Tithi", "Nakshatra", "Rahu Kaal")), text)
    check("links to /panchang/jaipur", url.startswith("https://divineastro.org/panchang/jaipur?"), url)
    check("tagged utm_campaign=panchang", utm_ok(q, "panchang"), str(q))
    check("desktop: a plain link to wa.me in a new tab (no share sheet)",
          btn.get_attribute("target") == "_blank")
    ctx.route("https://wa.me/**", lambda r: r.fulfill(status=200, body="wa", content_type="text/plain"))
    with ctx.expect_page() as popup:
        btn.click()
    popup.value.wait_for_load_state()
    check("desktop: clicking opens wa.me in a new tab", popup.value.url.startswith("https://wa.me/?text="),
          popup.value.url[:80])
    check("the original tab stays on the tool", pg.page.is_visible("#stage-panchang"))
    popup.value.close()
    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    ctx.close()


def seo_page(p, browser, base: str) -> None:
    print("\n[SEO page /rahu-kaal/mumbai on a 360px phone: plain wa.me link, no script needed]")
    ctx = browser.new_context(**PHONES["android_360x640"], user_agent=ANDROID_UA, java_script_enabled=False)
    page = ctx.new_page()
    page.goto(base + "/rahu-kaal/mumbai", wait_until="domcontentloaded")
    btn = page.locator("a.share-wa")
    check("the share link is visible without JavaScript", btn.is_visible())
    text, url, q = message(btn.get_attribute("href") or "")
    check("links to the page itself, tagged seo-rahu-kaal",
          url.startswith("https://divineastro.org/rahu-kaal/mumbai?") and utm_ok(q, "seo-rahu-kaal"), url)
    box = btn.bounding_box()
    check("tap target at least 44px and on screen", box and box["height"] >= 44 and box["x"] + box["width"] <= 360,
          str(box))
    check("no sideways scroll", page.evaluate("document.documentElement.scrollWidth <= innerWidth"))
    page.screenshot(path=os.path.join(SHOT_DIR, "seo_share_360.png"))
    ctx.close()


def main() -> int:
    with server() as base, sync_playwright() as p:
        browser = p.chromium.launch()
        today_strip(p, browser, base)
        panchang_tool(p, browser, base)
        seo_page(p, browser, base)
        browser.close()
    return check.finish("WhatsApp share buttons")


if __name__ == "__main__":
    raise SystemExit(main())
