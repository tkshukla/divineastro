"""The language picker (DIVASTRO-121): eight languages, one clearly visible switch.

The owner's ask: Kannada, Telugu, Tamil, Malayalam, Bengali and Odia "the same
way as Hindi and English", with a significantly visible language switcher on
every page. Translations land later, so until then a new language must show
English — never a blank label or a raw i18n key — and remember the choice.

App (home):
* the picker is in the header, >= 44px, readable, on a 360px phone and a desktop;
* it opens to all eight languages, by their own names;
* choosing Kannada sets <html lang="kn">, keeps every label filled (English
  fallback), loads the Kannada web font (and no font at all for English);
* the choice survives a reload; ?lang=te wins over it;
* a browser set to kn-IN gets a one-time hint in Kannada, which can be dismissed
  and stays dismissed;
* with the production CSP (read from the Caddyfile) enforced, nothing the
  picker or the fonts load is blocked.

Server pages: see seo_pages_section() at the bottom.

    E2E_SCREENSHOTS=<dir> C:\\Astro\\.venv\\Scripts\\python.exe -m tests.e2e.test_language_picker
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from playwright.sync_api import sync_playwright  # noqa: E402

from tests.e2e.harness import DESKTOPS, PHONES, PICKER, Checker, Page, enforce_csp, server  # noqa: E402

check = Checker()
CODES = ["en", "hi", "kn", "te", "ta", "ml", "bn", "or"]
NATIVE = {"en": "English", "hi": "हिन्दी", "kn": "ಕನ್ನಡ", "te": "తెలుగు", "ta": "தமிழ்",
          "ml": "മലയാളം", "bn": "বাংলা", "or": "ଓଡ଼ିଆ"}
SHOTS = os.environ.get("E2E_SCREENSHOTS", "")
FONT_HOST = "fonts.googleapis.com"

# Every visible label on the home screen: none may be empty or look like an i18n key.
HOME_TEXT = """() => {
  const ids = ['home-tagline', 'home-blurb', 'home-cta', 'feat-1', 'feat-2', 'feat-3', 'feat-4',
               'feat-5', 'feat-6', 'tool-milan-name', 'tool-panchang-name', 'tool-muhurat-name',
               'tool-choghadiya-name', 'tool-vrat-name', 'tool-katha-name', 'today-title'];
  return ids.map((id) => { const e = document.getElementById(id);
                           return [id, e ? e.textContent.trim() : null]; });
}"""


def shot(pg: Page, name: str) -> None:
    if SHOTS and Path(SHOTS).is_dir():
        pg.page.screenshot(path=str(Path(SHOTS) / name))


def new_page(browser, base: str, profile: dict, **extra) -> tuple:
    ctx = browser.new_context(**profile, **extra)
    enforce_csp(ctx, base)
    pg = Page(ctx.new_page(), base)
    fonts: list[str] = []
    pg.page.on("request", lambda r: fonts.append(r.url) if FONT_HOST in r.url else None)
    return ctx, pg, fonts


def picker_visible(pg: Page, label: str) -> None:
    btn = pg.rect(f"{PICKER} > summary")
    vw = pg.page.viewport_size["width"]
    check(f"{label}: the picker is in the header and visible",
          bool(btn) and btn["width"] > 0 and pg.page.is_visible(f"{PICKER} > summary"), str(btn))
    if not btn:
        return
    check(f"{label}: the picker is >= 44px tall and inside the screen",
          btn["height"] >= 44 and btn["left"] >= 0 and btn["right"] <= vw, str(btn))
    text = pg.page.inner_text(f"{PICKER} .lp-cur").strip()
    check(f"{label}: it names the current language in its own script", text == NATIVE["en"], text)
    fs = pg.page.evaluate(f"parseFloat(getComputedStyle(document.querySelector('{PICKER} .lp-cur')).fontSize)")
    check(f"{label}: its label is >= 14px", fs >= 14, f"{fs}px")
    over = pg.page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
    check(f"{label}: no sideways scroll with the picker in the header", over <= 1, f"{over}px")


def open_menu(pg: Page, label: str) -> None:
    pg.page.click(f"{PICKER} > summary")
    pg.page.wait_for_selector(f"{PICKER} .lp-menu a[data-lang]", state="visible")
    links = pg.page.eval_on_selector_all(
        f"{PICKER} .lp-menu a[data-lang]",
        "els => els.map(a => [a.dataset.lang, a.querySelector('.lp-native').textContent, "
        "a.getBoundingClientRect().height, a.getBoundingClientRect().left, a.getBoundingClientRect().right])")
    vw = pg.page.viewport_size["width"]
    check(f"{label}: the menu lists all eight languages by their own names",
          [l[0] for l in links] == CODES and all(l[1] == NATIVE[l[0]] for l in links), str([l[:2] for l in links]))
    check(f"{label}: every language is a >= 44px target", all(l[2] >= 44 for l in links),
          str([round(l[2]) for l in links]))
    check(f"{label}: the menu fits on the screen", all(l[3] >= 0 and l[4] <= vw for l in links),
          str([(round(l[3]), round(l[4])) for l in links]))
    focused = pg.page.evaluate("document.activeElement?.dataset?.lang || ''")
    check(f"{label}: opening it moves focus to the current language", focused == "en", focused)


def app_section(browser, base: str) -> None:
    for name, profile in (("android_360x640", PHONES["android_360x640"]),
                          ("small_320x568", PHONES["small_320x568"]),
                          ("desktop_1440x800", DESKTOPS["desktop_1440x800"])):
        print(f"\n[app header picker — {name}]")
        ctx, pg, fonts = new_page(browser, base, profile)
        pg.open_home()
        pg.page.wait_for_timeout(300)
        picker_visible(pg, name)
        shot(pg, f"app_{name}_closed.png")
        open_menu(pg, name)
        shot(pg, f"app_{name}_open.png")
        pg.page.keyboard.press("Escape")
        check(f"{name}: Escape closes the menu",
              pg.page.evaluate(f"!document.querySelector('{PICKER}').open"))
        check(f"{name}: English loads no web font", not fonts, str(fonts))
        if name.startswith("android"):
            # Light theme, closed + open, for a human to look at.
            pg.page.click("#theme-toggle")
            pg.page.wait_for_timeout(300)
            shot(pg, f"app_{name}_light_closed.png")
            pg.page.click(f"{PICKER} > summary")
            pg.page.wait_for_timeout(200)
            shot(pg, f"app_{name}_light_open.png")
            pg.page.keyboard.press("Escape")
            pg.page.click("#theme-toggle")
        ctx.close()

    print("\n[switching to Kannada: English fallback, font, persistence]")
    ctx, pg, fonts = new_page(browser, base, PHONES["android_360x640"])
    pg.open_home()
    en_text = dict(pg.page.evaluate(HOME_TEXT))
    pg.set_lang("kn")
    pg.page.wait_for_timeout(500)
    check("<html lang> is kn", pg.page.evaluate("document.documentElement.lang") == "kn")
    check("the picker now reads ಕನ್ನಡ", pg.page.inner_text(f"{PICKER} .lp-cur").strip() == "ಕನ್ನಡ")
    kn_text = dict(pg.page.evaluate(HOME_TEXT))
    blank = [k for k, v in kn_text.items() if v is not None and not v]
    keyish = [k for k, v in kn_text.items() if v and re.fullmatch(r"[a-z]+[A-Z][A-Za-z0-9]*", v)]
    check("no home label is blank in Kannada", not blank, str(blank))
    check("no home label shows a raw i18n key", not keyish, str({k: kn_text[k] for k in keyish}))
    # kn.json is translated now (DIVASTRO-122): the home labels must be in Kannada
    # script, and none may still be the English text.
    kannada = re.compile(r"[\u0C80-\u0CFF]")
    untranslated = [k for k, v in kn_text.items() if v and v == en_text.get(k) and re.search("[A-Za-z]{3}", v)
                    and not re.fullmatch(r"(Divine Astro|WhatsApp|Google|PDF|UPI)[^A-Za-z]*", v)]
    check("home labels are in Kannada", not untranslated
          and any(kannada.search(v or "") for v in kn_text.values()), str(untranslated[:6]))
    check("the Kannada JSON was fetched on demand",
          pg.page.evaluate("typeof I18N !== 'undefined' && !!I18N.kn"))
    pg.page.wait_for_timeout(800)
    check("the Kannada web font stylesheet is requested", any("Noto+Sans+Kannada" in u for u in fonts), str(fonts))
    check("...and no other script's font", not [u for u in fonts if "Noto+Sans" in u and "Kannada" not in u],
          str(fonts))
    check("the vrat card links to /kn/vrat-tyohar", pg.page.get_attribute("#open-vrat", "href") == "/kn/vrat-tyohar")
    shot(pg, "app_kn_home.png")
    pg.page.reload(wait_until="domcontentloaded")
    pg.page.wait_for_function("typeof showStage === 'function'")
    pg.page.wait_for_timeout(300)
    check("the choice survives a reload", pg.page.evaluate("state.lang") == "kn"
          and pg.page.evaluate("document.documentElement.lang") == "kn"
          and pg.page.inner_text(f"{PICKER} .lp-cur").strip() == "ಕನ್ನಡ")
    pg.page.goto(base + "/?lang=te", wait_until="domcontentloaded")
    pg.page.wait_for_function("typeof showStage === 'function'")
    check("?lang=te wins over the stored choice", pg.page.evaluate("state.lang") == "te"
          and pg.page.inner_text(f"{PICKER} .lp-cur").strip() == "తెలుగు")
    pg.page.goto(base + "/?lang=xx", wait_until="domcontentloaded")
    pg.page.wait_for_function("typeof showStage === 'function'")
    check("an unknown ?lang= falls back to the stored choice", pg.page.evaluate("state.lang") == "te")
    pg.set_lang("hi")
    check("Hindi still works from the picker", pg.page.inner_text("#home-cta").find("निःशुल्क") >= 0)
    pg.set_lang("en")
    check("no CSP violations (fonts, picker)", not pg.csp_violations(), str(pg.csp_violations()))
    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    ctx.close()

    print("\n[first visit with a Kannada browser]")
    ctx, pg, _fonts = new_page(browser, base, PHONES["android_360x640"], locale="kn-IN")
    pg.open_home()
    pg.page.wait_for_selector(".lp-hint", timeout=5000)
    hint = pg.page.inner_text(".lp-hint")
    check("a one-time hint offers Kannada, written in Kannada", "ಕನ್ನಡದಲ್ಲಿ" in hint, hint)
    check("the hint says lang=kn", pg.page.get_attribute(".lp-hint", "lang") == "kn")
    check("the page itself stays English until asked", pg.page.evaluate("state.lang") == "en")
    shot(pg, "app_kn_hint.png")
    pg.page.click(".lp-hint .lp-hint-no")
    check("dismissing removes it", pg.page.locator(".lp-hint").count() == 0)
    pg.page.reload(wait_until="domcontentloaded")
    pg.page.wait_for_function("typeof showStage === 'function'")
    pg.page.wait_for_timeout(500)
    check("...and it does not come back after a reload", pg.page.locator(".lp-hint").count() == 0)
    ctx.close()

    ctx, pg, _fonts = new_page(browser, base, PHONES["android_360x640"], locale="kn-IN")
    pg.open_home()
    pg.page.wait_for_selector(".lp-hint", timeout=5000)
    pg.page.click(".lp-hint .lp-hint-yes")
    pg.page.wait_for_function("state.lang === 'kn'")
    check("accepting the hint switches to Kannada in place",
          pg.page.evaluate("document.documentElement.lang") == "kn" and pg.page.locator(".lp-hint").count() == 0)
    ctx.close()

    ctx, pg, _fonts = new_page(browser, base, PHONES["android_360x640"], locale="en-IN")
    pg.open_home()
    pg.page.wait_for_timeout(600)
    check("an English browser gets no hint", pg.page.locator(".lp-hint").count() == 0)
    ctx.close()


# ---------------------------------------------------------------------------
# SEO pages: the server-rendered picker (app/i18n.py picker()) at the top of
# every page, its links resolve, untranslated copies say so in their script.
# ---------------------------------------------------------------------------
SEO_PICKER = "main.seo details.lang-picker"


def seo_pages_section(browser, base: str) -> None:
    for path in ("/panchang/pune", "/rashifal", "/vrat-tyohar", "/nakshatra/ashwini",
                 "/muhurat/vivah-2026", "/hi/rahu-kaal"):
        print(f"\n[SEO page picker — {path} at 360px]")
        ctx, pg, fonts = new_page(browser, base, PHONES["android_360x640"])
        r = pg.page.goto(base + path, wait_until="domcontentloaded")
        check(f"{path}: 200", r is not None and r.status == 200)
        btn = pg.rect(f"{SEO_PICKER} > summary")
        check(f"{path}: picker visible at the top, >= 44px, on screen",
              bool(btn) and btn["top"] < 120 and btn["height"] >= 44 and btn["right"] <= 360, str(btn))
        pg.page.click(f"{SEO_PICKER} > summary")
        pg.page.wait_for_selector(f"{SEO_PICKER} .lp-menu a[data-lang]", state="visible")
        links = pg.page.eval_on_selector_all(
            f"{SEO_PICKER} .lp-menu a[data-lang]",
            "els => els.map(a => [a.dataset.lang, a.getAttribute('href'), "
            "a.getBoundingClientRect().left, a.getBoundingClientRect().right, "
            "a.getBoundingClientRect().height])")
        check(f"{path}: menu lists all eight", [l[0] for l in links] == CODES, str(links))
        check(f"{path}: menu fits a 360px screen, 44px targets",
              all(l[2] >= 0 and l[3] <= 360 and l[4] >= 44 for l in links),
              str([(round(l[2]), round(l[3]), round(l[4])) for l in links]))
        bad = []
        for code, href, *_ in links:
            resp = pg.page.context.request.get(base + href)
            if resp.status != 200:
                bad.append((code, href, resp.status))
        check(f"{path}: every picker link resolves (200)", not bad, str(bad))
        pg.page.keyboard.press("Escape")
        check(f"{path}: Escape closes the menu",
              pg.page.evaluate(f"!document.querySelector('{SEO_PICKER}').open"))
        check(f"{path}: no web font on an English/Hindi page", not fonts, str(fonts[:2]))
        check(f"{path}: no CSP violations", not pg.csp_violations(), str(pg.csp_violations()))
        ctx.close()

    print("\n[SEO page: choosing Kannada]")
    ctx, pg, fonts = new_page(browser, base, PHONES["android_360x640"])
    pg.page.goto(base + "/panchang/pune", wait_until="domcontentloaded")
    pg.page.click(f"{SEO_PICKER} > summary")
    with pg.page.expect_navigation():
        pg.page.click(f"{SEO_PICKER} .lp-menu a[data-lang='kn']")
    pg.page.wait_for_load_state("networkidle")
    check("lands on /kn/panchang/pune", pg.page.url.endswith("/kn/panchang/pune"), pg.page.url)
    check("<html lang=kn>", pg.page.evaluate("document.documentElement.lang") == "kn")
    # DIVASTRO-123: the SEO pages are translated into Kannada - no note, Kannada body.
    check("no 'translation coming soon' note", pg.page.locator(".lp-notice").count() == 0)
    check("the body is in Kannada", "ಇಂದಿನ ಪಂಚಾಂಗ" in pg.page.inner_text("main.seo")
          and "Today's Panchang in Pune" not in pg.page.inner_text("main.seo"))
    check("the picker now says ಕನ್ನಡ",
          pg.page.inner_text(f"{SEO_PICKER} .lp-cur").strip() == NATIVE["kn"])
    check("indexable (no noindex) now that it is translated",
          pg.page.locator('meta[name="robots"][content^="noindex"]').count() == 0)
    check("the Kannada font, and only it, is requested",
          any("Noto+Sans+Kannada" in u for u in fonts)
          and not any(("Tamil" in u or "Telugu" in u) for u in fonts), str(fonts[:3]))
    check("no CSP violations loading the font", not pg.csp_violations(), str(pg.csp_violations()))
    check("the choice is remembered for the app",
          pg.page.evaluate("localStorage.getItem('astro.lang')") == "kn")
    shot(pg, "seo_kn_panchang_e2e.png")
    pg.page.goto(base + "/", wait_until="domcontentloaded")
    pg.page.wait_for_function("typeof state !== 'undefined'")
    check("...and the app opens in Kannada", pg.page.evaluate("state.lang") == "kn")
    ctx.close()

    print("\n[SEO page: first visit with a Tamil browser]")
    ctx, pg, _fonts = new_page(browser, base, PHONES["android_360x640"], locale="ta-IN")
    pg.page.goto(base + "/rashifal", wait_until="domcontentloaded")
    pg.page.wait_for_selector(".lp-hint", timeout=5000)
    hint = pg.page.inner_text(".lp-hint")
    check("the hint is in Tamil", "தமிழில்" in hint, hint)
    with pg.page.expect_navigation():
        pg.page.click(".lp-hint .lp-hint-yes")
    check("accepting goes to /ta/rashifal", pg.page.url.endswith("/ta/rashifal"), pg.page.url)
    ctx.close()


def main() -> int:
    with server() as base, sync_playwright() as p:
        browser = p.chromium.launch()
        app_section(browser, base)
        seo_pages_section(browser, base)
        browser.close()
    return check.finish("language picker")


if __name__ == "__main__":
    raise SystemExit(main())
