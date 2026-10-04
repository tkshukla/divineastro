"""Kundali Milan (matchmaking), English and Hindi (DIVASTRO-72, flow 7).

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.e2e.test_milan
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from playwright.sync_api import sync_playwright  # noqa: E402

from tests.e2e.harness import DESKTOPS, PHONES, Checker, Page, server  # noqa: E402

check = Checker()
# Where the phone screenshot of the share button goes (override with E2E_SHOT_DIR).
SHOT = os.path.join(os.environ.get("E2E_SHOT_DIR", "/tmp"), "milan_share_360.png")

GROOM = {"name": "Rohan", "date": "1990-03-12", "time": "09:30", "place": "Delhi"}
BRIDE = {"name": "Priya", "date": "1992-07-20", "time": "14:15", "place": "Mumbai"}


def fill_side(pg: Page, side: str, person: dict) -> None:
    card = f'.milan-card[data-side="{side}"]'
    pg.page.fill(f'{card} [data-f="name"]', person["name"])
    pg.page.fill(f'{card} [data-f="date"]', person["date"])
    pg.page.fill(f'{card} [data-f="time"]', person["time"])
    pg.page.fill(f'{card} [data-f="place"]', person["place"])
    pg.page.wait_for_selector(f'{card} [data-f="results"] li', timeout=10000)
    pg.page.locator(f'{card} [data-f="results"] li').first.click()


# ---- DIVASTRO-107: the WhatsApp share button after a match --------------------
# Nothing that identifies either person may leave in a share: names, birth dates
# (in any common spelling), times or places.
PERSONAL_BITS = [v for person in (GROOM, BRIDE) for v in person.values()] + [
    "1990", "1992", "12/03", "20/07", "03-12", "07-20", "09:30", "14:15"]


def shared_text(href: str) -> str:
    from urllib.parse import unquote
    assert href.startswith("https://wa.me/?text="), href
    return unquote(href[len("https://wa.me/?text="):])


def check_share(pg: Page, lang: str) -> None:
    btn = pg.page.locator("#milan-share")
    check(f"{lang}: a Share on WhatsApp button appears after the match", btn.is_visible())
    href = btn.get_attribute("href") or ""
    text = shared_text(href) if href.startswith("https://wa.me/?text=") else ""
    check(f"{lang}: it builds a wa.me URL", bool(text), href[:80])
    score = pg.page.locator(".ms-num").inner_text().split("/")[0].strip()
    check(f"{lang}: the message carries the score", f"{score}/36" in text, text)
    check(f"{lang}: the link is UTM-tagged for analytics",
          "https://divineastro.org/kundali-milan?utm_source=whatsapp&utm_medium=share&utm_campaign=milan" in text,
          text)
    leaked = [b for b in PERSONAL_BITS if b.lower() in text.lower()]
    check(f"{lang}: no name, birth date, time or place in it", not leaked, str(leaked))
    if lang == "Hindi":
        check("Hindi: the message is in Hindi", "गुण" in text, text)
    box = pg.rect("#milan-share")
    check(f"{lang}: the button is at least 44px tall", box and box["height"] >= 44, str(box))
    check(f"{lang}: desktop opens wa.me in a new tab", btn.get_attribute("target") == "_blank")


def milan_share_phone(p, browser, base: str) -> None:
    print("\n[Kundali Milan share on a 360px phone: the system share sheet, nothing personal]")
    ctx = browser.new_context(**PHONES["android_360x640"],
                              user_agent="Mozilla/5.0 (Linux; Android 13; SM-A145F) AppleWebKit/537.36 "
                                         "(KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36")
    page = ctx.new_page()
    # Record what the page hands the share sheet instead of opening one.
    page.add_init_script("window.__shared = []; navigator.share = (d) => { window.__shared.push(d); return Promise.resolve(); };")
    pg = Page(page, base)
    open_milan(pg)
    fill_side(pg, "groom", GROOM)
    fill_side(pg, "bride", BRIDE)
    pg.page.click("#milan-go")
    pg.page.wait_for_selector("#milan-share", state="visible", timeout=15000)
    pg.page.locator("#milan-share").scroll_into_view_if_needed()
    pg.page.wait_for_timeout(300)
    pg.page.screenshot(path=SHOT)
    box = pg.rect("#milan-share")
    check("phone: the button fits the 360px screen", box and box["left"] >= 0 and box["right"] <= 360, str(box))
    check("phone: no sideways scroll", pg.page.evaluate("document.documentElement.scrollWidth <= innerWidth"))
    pg.page.tap("#milan-share")
    pg.page.wait_for_timeout(300)
    shared = pg.page.evaluate("window.__shared")
    text = (shared[0] or {}).get("text", "") if shared else ""
    check("phone: tapping uses navigator.share (and stays on the page)",
          len(shared) == 1 and len(ctx.pages) == 1, str(shared))
    leaked = [b for b in PERSONAL_BITS if b.lower() in text.lower()]
    check("phone: the shared text has the score and link, nothing personal",
          "/36" in text and "utm_source=whatsapp" in text and not leaked, f"{text} {leaked}")
    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    ctx.close()


def open_milan(pg: Page) -> None:
    pg.open_home()
    pg.page.click("#open-milan")
    pg.page.wait_for_selector("#stage-milan", state="visible", timeout=10000)


def milan_english(p, browser, base: str) -> None:
    print("\n[Kundali Milan in English: both forms, a real score, a real verdict]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    open_milan(pg)

    fill_side(pg, "groom", GROOM)
    fill_side(pg, "bride", BRIDE)
    check("both places resolved before submitting",
          pg.page.locator('.milan-card[data-side="groom"] [data-f="chosen"]').is_visible()
          and pg.page.locator('.milan-card[data-side="bride"] [data-f="chosen"]').is_visible())

    pg.page.click("#milan-go")
    pg.page.wait_for_selector("#milan-result", state="visible", timeout=15000)

    score_text = pg.page.locator(".ms-num").inner_text()
    check("a real Ashtakoot score renders", "/" in score_text, score_text)
    check("a verdict line renders", pg.page.locator(".ms-verdict").inner_text().strip() != "")
    rows = pg.page.locator("table.koota-table tbody tr")
    check("the koota breakdown table has all 8 kootas", rows.count() == 8, f"{rows.count()} rows")
    check("Mangal Dosha is reported for both people",
          pg.page.locator(".milan-extra").inner_text().strip() != "")
    check_share(pg, "English")

    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    check("no CSP violations", not pg.csp_violations(), str(pg.csp_violations()[:2]))
    ctx.close()


def milan_hindi(p, browser, base: str) -> None:
    print("\n[Kundali Milan in Hindi: the request says hi, the result reads Hindi]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    open_milan(pg)
    pg.set_lang("hi")
    pg.page.evaluate("showStage('stage-milan')")

    fill_side(pg, "groom", GROOM)
    fill_side(pg, "bride", BRIDE)

    bodies: list[str] = []
    pg.page.on("request", lambda r: bodies.append(r.post_data or "")
               if r.url.endswith("/api/match") else None)
    pg.page.click("#milan-go")
    pg.page.wait_for_selector("#milan-result", state="visible", timeout=15000)

    check("the match request declared Hindi", len(bodies) == 1 and '"lang":"hi"' in bodies[0],
          str(bodies))
    check("a score still renders in Hindi mode", "/" in pg.page.locator(".ms-num").inner_text())
    check_share(pg, "Hindi")

    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    check("no CSP violations", not pg.csp_violations(), str(pg.csp_violations()[:2]))
    ctx.close()


def main() -> int:
    with server() as base, sync_playwright() as p:
        browser = p.chromium.launch()
        milan_english(p, browser, base)
        milan_hindi(p, browser, base)
        milan_share_phone(p, browser, base)
        browser.close()
    return check.finish("Kundali Milan (English, Hindi)")


if __name__ == "__main__":
    raise SystemExit(main())
