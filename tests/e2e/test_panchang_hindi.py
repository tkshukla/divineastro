"""Hindi selected means Hindi everywhere in the Panchang tools.

Owner's report: "Even though Hindi is selected, Panchang has English words." The
tool printed the limb names, vara, Rahu Kaal / Yamaganda / Gulika / Abhijit and
"until" in English, the Muhurat Finder its yogas, column headings and event
names, and a result already on screen stayed English after the EN / हिं switch.

In Hindi this opens the home Today strip, Panchang, Muhurat Finder and
Choghadiya, and fails on any Latin-script word in their visible text (a picked
place's own label is allowed: GeoNames only has it in English). It also shows a
Panchang in English first and switches to Hindi with it on screen.

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.e2e.test_panchang_hindi
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from playwright.sync_api import sync_playwright  # noqa: E402

from tests.e2e.harness import PHONES, Checker, Page, server  # noqa: E402

check = Checker()

# Brand names a Hindi page still writes in Latin script.
ALLOWED = {"Divine", "Astro", "WhatsApp", "Google"}
# Set E2E_SCREENSHOTS=<dir> to keep phone screenshots of the vrat section and sign-in sheet.
SHOTS = os.environ.get("E2E_SCREENSHOTS", "")
WORD = re.compile(r"[A-Za-z][A-Za-z'’.-]*")

# The visible text of a section, plus what a reader sees in its form controls:
# an empty input's placeholder and each select's chosen option.
VISIBLE = """(sel) => {
  const root = document.querySelector(sel);
  if (!root) return '';
  const extra = [];
  root.querySelectorAll('input[placeholder]').forEach((i) => {
    if (i.offsetParent && !i.value) extra.push(i.placeholder);
  });
  root.querySelectorAll('select').forEach((s) => {
    if (s.offsetParent) extra.push(Array.from(s.options).map((o) => o.text).join(' '));
  });
  return root.innerText + '\\n' + extra.join('\\n');
}"""


def latin_words(pg: Page, sel: str, allow: frozenset = frozenset()) -> list[str]:
    text = pg.page.evaluate(VISIBLE, sel)
    return sorted({w for w in WORD.findall(text) if w not in ALLOWED and w not in allow})


def screenshot(pg: Page, name: str) -> None:
    """For a human to look at; only when E2E_SCREENSHOTS names a directory."""
    if SHOTS and Path(SHOTS).is_dir():
        pg.page.screenshot(path=str(Path(SHOTS) / name))


def open_home_hi(pg: Page) -> None:
    pg.open_home()
    pg.page.click(".lang[data-lang=hi]")
    pg.page.wait_for_function("state.lang === 'hi'")


def today_strip_and_panchang(browser, base: str) -> None:
    print("\n[Hindi: home Today strip, then the Panchang tool]")
    ctx = browser.new_context(**PHONES["iphone_375x812"])
    pg = Page(ctx.new_page(), base)
    open_home_hi(pg)
    pg.page.wait_for_selector("#today-strip:not(.loading)", timeout=15000)
    pg.page.wait_for_function("document.querySelector('#today-city-name').textContent !== 'New Delhi'",
                              timeout=10000)
    words = latin_words(pg, "#today-strip")
    check("Today strip: no Latin-script words", not words, str(words))

    pg.page.click("#today-open")
    pg.page.wait_for_selector("#panchang-result .pa-limbs", timeout=15000)
    words = latin_words(pg, "#stage-panchang")
    check("Panchang: no Latin-script words", not words, str(words))
    head = pg.page.locator("#panchang-result h2").inner_text()
    check("Panchang heading is a Hindi weekday and date", re.search(r"वार · \d+ \S+ 20\d\d$", head) is not None,
          head)
    check("'तक' follows the time, as Hindi says it",
          re.search(r"\d\d:\d\d तक", pg.page.locator("#panchang-result .pa-limbs").inner_text()) is not None)

    # A place picked from the search keeps its own (English) label, but nothing else may be.
    pg.page.fill("#pa-place", "Mumbai")
    pg.page.wait_for_selector("#pa-results li", timeout=10000)
    pg.page.locator("#pa-results li").first.click()
    pg.page.wait_for_function(
        "document.querySelector('#panchang-result .muted-line').textContent.includes('मुंबई')", timeout=15000)
    words = latin_words(pg, "#stage-panchang")
    check("Panchang for a picked SEO city: no Latin-script words (मुंबई)", not words, str(words))

    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    ctx.close()


def muhurat(browser, base: str) -> None:
    print("\n[Hindi: Muhurat Finder]")
    ctx = browser.new_context(**PHONES["iphone_375x812"])
    pg = Page(ctx.new_page(), base)
    open_home_hi(pg)
    pg.page.click("#open-muhurat")
    pg.page.wait_for_selector("#stage-muhurat", state="visible", timeout=10000)
    pg.page.click("#muhurat-go")
    pg.page.wait_for_selector("#muhurat-result tbody tr", state="attached", timeout=60000)
    words = latin_words(pg, "#stage-muhurat")
    check("Muhurat Finder (form, event list, results): no Latin-script words", not words, str(words))
    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    ctx.close()


def choghadiya(browser, base: str) -> None:
    print("\n[Hindi: Choghadiya]")
    ctx = browser.new_context(**PHONES["iphone_375x812"])
    pg = Page(ctx.new_page(), base)
    open_home_hi(pg)
    pg.page.click("#open-choghadiya")
    pg.page.wait_for_selector("#stage-choghadiya", state="visible", timeout=10000)
    pg.page.click("#choghadiya-go")
    pg.page.wait_for_selector("#choghadiya-result tbody tr", state="attached", timeout=15000)
    words = latin_words(pg, "#stage-choghadiya")
    check("Choghadiya: no Latin-script words", not words, str(words))
    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    ctx.close()


def switch_with_results_open(browser, base: str) -> None:
    print("\n[EN -> हिं with results already on screen]")
    ctx = browser.new_context(**PHONES["iphone_375x812"])
    pg = Page(ctx.new_page(), base)
    pg.open_home()
    pg.page.click(".lang[data-lang=en]")
    pg.page.click("#open-panchang")
    pg.page.wait_for_selector("#panchang-result .pa-limbs", timeout=15000)
    check("English first: the Panchang shows English names",
          "Rahu Kaal" in pg.page.locator("#panchang-result").inner_text())
    pg.page.click(".lang[data-lang=hi]")
    pg.page.wait_for_function("!document.querySelector('#panchang-result').innerText.includes('Rahu')",
                              timeout=5000)
    words = latin_words(pg, "#stage-panchang")
    check("after the switch: Panchang has no Latin-script words", not words, str(words))
    pg.page.click(".lang[data-lang=en]")
    pg.page.wait_for_function("document.querySelector('#panchang-result').innerText.includes('Rahu Kaal')",
                              timeout=5000)
    check("and back: English again", "until" in pg.page.locator("#panchang-result").inner_text())

    for opener, go, result, stage in (("#open-choghadiya", "#choghadiya-go", "#choghadiya-result", "#stage-choghadiya"),
                                      ("#open-muhurat", "#muhurat-go", "#muhurat-result", "#stage-muhurat")):
        pg.page.evaluate("document.querySelector('.lang[data-lang=en]').click()")
        pg.page.evaluate("showStage('stage-home')")
        pg.page.click(opener)
        pg.page.click(go)
        pg.page.wait_for_selector(f"{result} tbody tr", state="attached", timeout=60000)
        pg.page.click(".lang[data-lang=hi]")
        try:
            pg.page.wait_for_function(
                f"!/[A-Za-z]{{3,}}/.test(document.querySelector('{result} tbody').innerText)", timeout=60000)
        except Exception:                 # noqa: BLE001 — the assertion below reports it
            pass
        words = latin_words(pg, stage)
        check(f"after the switch: {stage[7:]} result has no Latin-script words", not words, str(words))

    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    ctx.close()


def vrat_section(browser, base: str) -> None:
    """DIVASTRO-111: a festival date's vrat/festivals and their puja muhurat, in Hindi."""
    print("\n[Hindi: the Panchang's vrat/festival section on 8 Nov 2026 (Diwali)]")
    ctx = browser.new_context(**PHONES["iphone_375x812"])
    pg = Page(ctx.new_page(), base)
    open_home_hi(pg)
    pg.page.click("#open-panchang")
    pg.page.wait_for_selector("#panchang-result .pa-limbs", timeout=15000)
    pg.page.fill("#pa-date", "2026-11-08")
    # (Today may well have its own section already: wait for the chosen date's.)
    pg.page.wait_for_function(
        "(document.querySelector('#pa-vrat')||{}).innerText?.includes('8 नवंबर 2026')", timeout=15000)
    vrat = pg.page.locator("#pa-vrat").inner_text()
    check("heading names the chosen date: '8 नवंबर 2026 के व्रत-त्योहार'",
          "8 नवंबर 2026 के व्रत-त्योहार" in vrat, vrat[:200])
    check("दीपावली (लक्ष्मी पूजा) with लक्ष्मी पूजा मुहूर्त 17:54 – 19:50 (New Delhi)",
          "दीपावली (लक्ष्मी पूजा)" in vrat
          and re.search(r"लक्ष्मी पूजा मुहूर्त\s+17:54 – 19:50", vrat) is not None, vrat[:400])
    check("प्रदोष काल and वृषभ काल are listed", "प्रदोष काल" in vrat and "वृषभ काल" in vrat)
    check("Diwali links to the Hindi festival page",
          pg.page.locator("#pa-vrat a[href='/hi/tyohar/diwali-2026']").count() == 1)
    words = latin_words(pg, "#stage-panchang")
    check("Panchang with the vrat section: no Latin-script words", not words, str(words))
    pg.page.locator("#pa-vrat").scroll_into_view_if_needed()
    screenshot(pg, "panchang-vrat-hi.png")

    pg.page.click(".lang[data-lang=en]")
    pg.page.wait_for_function(
        "document.querySelector('#pa-vrat').innerText.includes('Lakshmi puja muhurat')", timeout=5000)
    check("EN switch: the section re-renders in English",
          "Vrat & Festivals on 8 November 2026" in pg.page.locator("#pa-vrat").inner_text()
          and pg.page.locator("#pa-vrat a[href='/tyohar/diwali-2026']").count() == 1)
    pg.page.click(".lang[data-lang=hi]")
    pg.page.wait_for_function(
        "document.querySelector('#pa-vrat').innerText.includes('लक्ष्मी पूजा मुहूर्त')", timeout=5000)
    words = latin_words(pg, "#stage-panchang")
    check("and back to हिं: no Latin-script words", not words, str(words))

    pg.page.fill("#pa-date", "2026-11-20")
    pg.page.wait_for_function(
        "(document.querySelector('#pa-vrat')||{}).innerText?.includes('देवउठनी')", timeout=15000)
    vrat = pg.page.locator("#pa-vrat").inner_text()
    check("20 Nov 2026: देवउठनी एकादशी, पारण का समय 21 नवंबर, 13:10 – 15:18",
          re.search(r"पारण का समय\s+21 नवंबर, 13:10 – 15:18", vrat) is not None, vrat[:300])
    pg.page.fill("#pa-date", "2026-11-12")
    pg.page.wait_for_function(
        "document.querySelector('#panchang-result h2').textContent.includes('12 नवंबर')", timeout=15000)
    check("an ordinary date: no section at all", pg.page.locator("#pa-vrat").count() == 0)
    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    ctx.close()


def sign_in_hindi(browser, base: str) -> None:
    """The header Sign in button, the sign-in sheet and the account menu, in Hindi —
    on load and after a live EN / हिं switch."""
    print("\n[Hindi: header Sign in, the sign-in sheet, the account menu]")
    ctx = browser.new_context(**PHONES["iphone_375x812"])
    pg = Page(ctx.new_page(), base)
    pg.open_home()
    pg.page.click(".lang[data-lang=en]")
    pg.page.wait_for_selector("#btn-signin", timeout=10000)
    check("English: the header says 'Sign in'", pg.page.inner_text("#btn-signin").strip() == "Sign in")
    pg.page.click(".lang[data-lang=hi]")
    check("switch to हिं: the header button turns Hindi at once (साइन इन)",
          pg.page.inner_text("#btn-signin").strip() == "साइन इन", pg.page.inner_text("#btn-signin"))
    words = latin_words(pg, "#account-bar")
    check("header account bar: no Latin-script words", not words, str(words))
    pg.page.click("#btn-signin")
    pg.page.wait_for_selector(".modal-backdrop .modal", timeout=5000)
    words = latin_words(pg, ".modal-backdrop")
    check("sign-in sheet: no Latin-script words", not words, str(words))
    check("the legal line links शर्तें and गोपनीयता नीति",
          pg.page.locator(".legal-line a[href='/terms']").inner_text() == "शर्तें"
          and pg.page.locator(".legal-line a[href='/privacy']").inner_text() == "गोपनीयता नीति")
    check("the close button is labelled in Hindi",
          pg.page.get_attribute(".modal-x", "aria-label") == "बंद करें")
    screenshot(pg, "signin-hi.png")
    pg.page.click("#toggle-password-auth")
    pg.page.fill("#pa-username", "x")
    pg.page.fill("#pa-password", "short")
    pg.page.click("#pa-submit")
    pg.page.wait_for_selector(".modal-error:not([hidden])", timeout=5000)
    words = latin_words(pg, ".modal-backdrop")
    check("username view + a server error: no Latin-script words", not words, str(words))
    pg.page.evaluate("closeModal()")
    pg.page.click(".lang[data-lang=en]")
    check("and back to EN: 'Sign in' again", pg.page.inner_text("#btn-signin").strip() == "Sign in")
    ctx.close()

    # Signed in: the account menu (a Hindi-named user, so the name is not Latin).
    ctx = browser.new_context(**PHONES["iphone_375x812"])
    pg = Page(ctx.new_page(), base)
    pg.sign_in(email="hindi-e2e@example.com", name="परीक्षक")
    pg.open_home()
    pg.page.click(".lang[data-lang=en]")
    pg.page.wait_for_selector("#btn-acct", timeout=10000)
    pg.page.click(".lang[data-lang=hi]")
    pg.page.click("#btn-acct")
    pg.page.wait_for_selector(".acct-drop:not([hidden])", timeout=5000)
    # "English" is the menu's switch *to* English, named in its own language.
    words = latin_words(pg, "#account-bar", frozenset({"English"}))
    check("account bar + menu after a live switch: no Latin-script words", not words, str(words))
    check("menu shows साइन आउट", "साइन आउट" in pg.page.inner_text(".acct-drop"))
    pg.page.click("#btn-acct")
    pg.page.evaluate("openOrders()")
    pg.page.wait_for_selector(".modal-backdrop .modal-title", timeout=5000)
    words = latin_words(pg, ".modal-backdrop")
    check("मेरे ऑर्डर: no Latin-script words", not words, str(words))
    pg.page.evaluate("closeModal()")
    pg.page.click(".lang[data-lang=en]")
    pg.page.click("#btn-acct")
    check("and back to EN: 'Sign out'", "Sign out" in pg.page.inner_text(".acct-drop"))
    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    ctx.close()


def main() -> int:
    with server() as base, sync_playwright() as p:
        browser = p.chromium.launch()
        vrat_section(browser, base)
        sign_in_hindi(browser, base)
        today_strip_and_panchang(browser, base)
        muhurat(browser, base)
        choghadiya(browser, base)
        switch_with_results_open(browser, base)
        browser.close()
    return check.finish("Hindi Panchang / Muhurat / Choghadiya / Today strip")


if __name__ == "__main__":
    raise SystemExit(main())
