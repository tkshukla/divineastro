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

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from playwright.sync_api import sync_playwright  # noqa: E402

from tests.e2e.harness import PHONES, Checker, Page, server  # noqa: E402

check = Checker()

# Brand names a Hindi page still writes in Latin script.
ALLOWED = {"Divine", "Astro", "WhatsApp"}
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


def latin_words(pg: Page, sel: str) -> list[str]:
    text = pg.page.evaluate(VISIBLE, sel)
    return sorted({w for w in WORD.findall(text) if w not in ALLOWED})


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


def main() -> int:
    with server() as base, sync_playwright() as p:
        browser = p.chromium.launch()
        today_strip_and_panchang(browser, base)
        muhurat(browser, base)
        choghadiya(browser, base)
        switch_with_results_open(browser, base)
        browser.close()
    return check.finish("Hindi Panchang / Muhurat / Choghadiya / Today strip")


if __name__ == "__main__":
    raise SystemExit(main())
