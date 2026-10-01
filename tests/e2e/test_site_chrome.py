"""Legal pages reachable from the footer, and language/theme persistence
across a reload (DIVASTRO-72, flows 14 and 15).

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.e2e.test_site_chrome
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from playwright.sync_api import sync_playwright  # noqa: E402

from tests.e2e.harness import Checker, DESKTOPS, Page, server  # noqa: E402

check = Checker()

LEGAL_LINKS = [
    ("/terms", "Terms & Conditions"),
    ("/privacy", "Privacy Policy"),
    ("/refund", "Refund & Cancellation"),
    ("/contact", "Contact Us"),
]


def legal_pages(p, browser, base: str) -> None:
    print("\n[legal pages]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    pg.open_home()

    for href, label in LEGAL_LINKS:
        sel = f'a[href="{href}"]'
        check(f"footer link to {href} exists", pg.page.locator(sel).count() > 0, label)

    for href, label in LEGAL_LINKS:
        resp = pg.page.goto(base + href, wait_until="domcontentloaded")
        check(f"{href} loads (200)", resp is not None and resp.status == 200, label)
        body_text = pg.page.locator("body").inner_text()
        check(f"{href} has real content, not a blank/error page",
              len(body_text.strip()) > 100, f"{len(body_text.strip())} chars")

    check("no console errors across the legal pages", not pg.console_errors,
          "; ".join(pg.console_errors[:3]))
    check("no CSP violations across the legal pages", not pg.csp_violations(),
          str(pg.csp_violations()[:2]))
    ctx.close()


def preferences_persist(p, browser, base: str) -> None:
    print("\n[language and theme persist across reload]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    pg.open_home()

    initial_theme = pg.page.evaluate("localStorage.getItem('astro.theme')")
    initial_lang = pg.page.evaluate("localStorage.getItem('astro.lang')")
    check("starts in English", (initial_lang or "en") == "en", str(initial_lang))

    pg.page.click('button.lang[data-lang="hi"]')
    pg.page.click("#theme-toggle")
    lang_after_click = pg.page.evaluate("localStorage.getItem('astro.lang')")
    theme_after_click = pg.page.evaluate("localStorage.getItem('astro.theme')")
    check("clicking the Hindi toggle writes astro.lang=hi to localStorage",
          lang_after_click == "hi", str(lang_after_click))
    check("clicking the theme toggle writes a theme to localStorage",
          theme_after_click in ("light", "dark"), str(theme_after_click))

    pg.page.reload(wait_until="domcontentloaded")
    pg.page.wait_for_function("typeof showStage === 'function'")

    lang_after_reload = pg.page.evaluate("localStorage.getItem('astro.lang')")
    theme_after_reload = pg.page.evaluate("localStorage.getItem('astro.theme')")
    check("language choice survives a reload", lang_after_reload == "hi",
          str(lang_after_reload))
    check("theme choice survives a reload", theme_after_reload == theme_after_click,
          f"{theme_after_click!r} -> {theme_after_reload!r}")

    active_lang_btn = pg.page.evaluate(
        "document.querySelector('button.lang.active')?.dataset.lang")
    check("the Hindi button shows as active after reload (UI matches storage, "
          "not just the storage key)", active_lang_btn == "hi", str(active_lang_btn))

    data_theme = pg.page.evaluate("document.documentElement.getAttribute('data-theme')")
    if theme_after_reload == "light":
        check("data-theme attribute reflects light after reload", data_theme == "light",
              str(data_theme))
    else:
        check("data-theme attribute reflects dark after reload (absent/non-light)",
              data_theme != "light", str(data_theme))

    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    check("no CSP violations", not pg.csp_violations(), str(pg.csp_violations()[:2]))
    ctx.close()


def main() -> int:
    with server() as base, sync_playwright() as p:
        browser = p.chromium.launch()
        legal_pages(p, browser, base)
        preferences_persist(p, browser, base)
        browser.close()
    return check.finish("site chrome (legal pages, language/theme persistence)")


if __name__ == "__main__":
    raise SystemExit(main())
