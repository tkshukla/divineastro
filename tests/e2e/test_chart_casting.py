"""Casting a chart: place search, "don't know the time", and validation
errors (DIVASTRO-72, flow 3). Exercises the real birth-entry form, not the
castChart() JS shortcut other tests use to skip straight to a cast chart.

Needs the offline city database (tools/fetch_data.py) since it drives real
place-search autocomplete, unlike every other e2e test so far.

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.e2e.test_chart_casting
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from playwright.sync_api import sync_playwright  # noqa: E402

from tests.e2e.harness import Checker, DESKTOPS, Page, server  # noqa: E402

check = Checker()


def open_birth_form(pg: Page) -> None:
    pg.open_home()
    pg.sign_in()
    pg.page.reload(wait_until="domcontentloaded")
    pg.page.wait_for_function("typeof showStage === 'function'")
    pg.page.click("#home-cta")
    pg.page.wait_for_selector("#birth-form", state="visible")


def validation_without_a_place(p, browser, base: str) -> None:
    print("\n[submitting without picking a place shows an inline error, not a silent no-op]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    open_birth_form(pg)

    pg.page.fill("#f-date", "1990-03-12")
    pg.page.fill("#f-time", "09:30")
    # #f-place has the native `required` attribute, which would block the
    # form's submit event (and a browser-native tooltip, not the app's own
    # #birth-error) before the JS handler ever runs if left empty. Typing
    # text but not picking a suggestion satisfies `required` while still
    # leaving state.place unset — the actual app-level validation case.
    pg.page.fill("#f-place", "Nowhere I Will Pick")
    check("the error line starts hidden", pg.page.locator("#birth-error").is_hidden())
    pg.page.click("#cast")
    pg.page.wait_for_timeout(300)
    check("an inline error appears when no place was chosen",
          pg.page.locator("#birth-error").is_visible())
    check("the page did not navigate away to a chart", pg.page.locator("#birth-form").is_visible())

    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    check("no CSP violations", not pg.csp_violations(), str(pg.csp_violations()[:2]))
    ctx.close()


def place_search_and_cast(p, browser, base: str) -> None:
    print("\n[real place-search autocomplete, then a successful cast]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    open_birth_form(pg)

    pg.page.fill("#f-date", "1990-03-12")
    pg.page.fill("#f-time", "09:30")
    pg.page.fill("#f-place", "Delhi")
    pg.page.wait_for_selector("#place-results li", timeout=10000)
    results = pg.page.locator("#place-results li")
    check("typing a real city returns real suggestions", results.count() > 0,
          f"{results.count()} results")

    results.first.click()
    check("picking a suggestion fills the place field", "Delhi" in pg.page.input_value("#f-place"))
    check("picking a suggestion shows the resolved place line",
          pg.page.locator("#place-chosen").is_visible())

    pg.page.click("#cast")
    pg.page.wait_for_selector("#stage-dashboard, #stage-chat", state="visible", timeout=15000)
    check("a valid submission actually casts the chart (leaves the form)",
          not pg.page.locator("#birth-form").is_visible())

    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    check("no CSP violations", not pg.csp_violations(), str(pg.csp_violations()[:2]))
    ctx.close()


def unknown_birth_time(p, browser, base: str) -> None:
    print("\n[\"don't know the time\" disables the time field and still casts a chart]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    open_birth_form(pg)

    pg.page.fill("#f-date", "1990-03-12")
    pg.page.check("#f-unknown")
    check("checking 'unknown time' disables the time field",
          pg.page.eval_on_selector("#f-time", "e => e.disabled") is True)
    check("the time field is reset to midday when unknown",
          pg.page.input_value("#f-time") == "12:00")

    pg.page.fill("#f-place", "Mumbai")
    pg.page.wait_for_selector("#place-results li", timeout=10000)
    pg.page.locator("#place-results li").first.click()

    requests: list[str] = []
    pg.page.on("request", lambda r: requests.append(r.post_data or "")
               if r.url.endswith("/api/chart") and r.method == "POST" else None)
    pg.page.click("#cast")
    pg.page.wait_for_selector("#stage-dashboard, #stage-chat", state="visible", timeout=15000)
    check("the chart request told the server the time is unknown (time_known: false)",
          len(requests) == 1 and '"time_known":false' in requests[0],
          str(requests))

    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    check("no CSP violations", not pg.csp_violations(), str(pg.csp_violations()[:2]))
    ctx.close()


def name_field_is_optional(p, browser, base: str) -> None:
    print("\n[the Name field is genuinely optional, with a sensible fallback display]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    open_birth_form(pg)

    check("the Name field has no native required attribute",
          pg.page.eval_on_selector("#f-name", "e => e.required") is False)
    check("the label already tells the visitor it's optional",
          "optional" in pg.page.inner_text('label[for="f-name"]').lower())

    pg.page.fill("#f-date", "1990-03-12")
    pg.page.fill("#f-time", "09:30")
    # Deliberately leave #f-name blank.
    pg.page.fill("#f-place", "Kolkata")
    pg.page.wait_for_selector("#place-results li", timeout=10000)
    pg.page.locator("#place-results li").first.click()

    pg.page.click("#cast")
    pg.page.wait_for_selector("#stage-dashboard, #stage-chat", state="visible", timeout=15000)
    check("a chart with no name still casts successfully",
          not pg.page.locator("#birth-form").is_visible())

    who_name = pg.page.inner_text("#who-name").strip()
    check("a real, non-blank fallback displays instead of an empty name",
          who_name not in ("", "—"), repr(who_name))
    # DIVASTRO-162: the neutral "My chart", not the server's "Native" or an empty line.
    check("the chart header says 'My chart' for an unnamed chart",
          (pg.page.text_content("#who-name") or "").strip() == "My chart",
          repr(pg.page.text_content("#who-name")))
    check("the dashboard header says 'My chart' too",
          (pg.page.text_content("#dash-name") or "").strip() == "My chart",
          repr(pg.page.text_content("#dash-name")))
    opening = pg.page.text_content("#thread") or ""
    check("the opening chat message names it 'My chart', never Native/undefined/empty bold",
          "My chart" in opening and "Native" not in opening and "undefined" not in opening
          and "****" not in opening, opening[:120])
    labels = pg.page.evaluate("typeof reportCharts === 'function' ? reportCharts().map(c => c.label) : []")
    check("the reports list labels the open unnamed chart 'This chart', not 'Native'",
          not labels or (labels[0] == "This chart"), str(labels))

    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    check("no CSP violations", not pg.csp_violations(), str(pg.csp_violations()[:2]))
    ctx.close()


NAME_PH_EN = "Optional — a nickname is fine"
NAME_HINT_EN = ("Not needed for the reading — date, time and place are enough. "
                "Leave it blank to stay anonymous.")


def name_hint_on_phones(p, browser, base: str) -> None:
    print("\n[DIVASTRO-162: the name says it is optional and not needed, in English and Hindi, on a phone]")
    hi = json.loads((Path(__file__).resolve().parents[2] / "app" / "static" / "i18n" / "hi.json")
                    .read_text(encoding="utf-8"))

    def form_at(width: int, height: int, lang: str = "en") -> Page:
        ctx = browser.new_context(viewport={"width": width, "height": height}, is_mobile=True,
                                  has_touch=True, device_scale_factor=2)
        pg = Page(ctx.new_page(), base)
        pg.open_home()
        if lang != "en":
            pg.set_lang(lang)
        pg.page.click("#home-cta")
        pg.page.wait_for_selector("#birth-form", state="visible")
        pg.page.evaluate("window.scrollTo(0, 0)")
        return pg

    pg = form_at(390, 844)
    check("EN: the name placeholder says optional, nickname fine",
          pg.page.get_attribute("#f-name", "placeholder") == NAME_PH_EN)
    check("EN: the hint line under the name is visible with the agreed words",
          pg.page.locator("#name-hint").is_visible()
          and pg.page.inner_text("#name-hint").strip() == NAME_HINT_EN,
          pg.page.inner_text("#name-hint"))
    check("the name input points screen readers at the hint",
          pg.page.get_attribute("#f-name", "aria-describedby") == "name-hint")
    hint, name, cast = pg.rect("#name-hint"), pg.rect("#f-name"), pg.rect("#cast")
    check("the hint sits under the name input and above the submit button",
          name["bottom"] <= hint["top"] <= hint["bottom"] <= cast["top"], f"{name} {hint} {cast}")
    check("390x844: the submit button is still fully on the first screen",
          cast["bottom"] <= 844, f"bottom {cast['bottom']:.0f}")
    pg.page.evaluate("showStage('stage-milan')")
    phs = pg.page.eval_on_selector_all(".milan-card [data-f='name']", "els => els.map(e => e.placeholder)")
    check("EN: both Kundali Milan name fields say optional, nickname fine",
          phs == [NAME_PH_EN, NAME_PH_EN], str(phs))
    check("no console errors (EN)", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    pg.page.context.close()

    pg = form_at(360, 640, "hi")
    check("HI: the name placeholder is the Hindi one",
          pg.page.get_attribute("#f-name", "placeholder") == hi["nameOptPh"],
          pg.page.get_attribute("#f-name", "placeholder"))
    check("HI: the hint is the Hindi one",
          pg.page.inner_text("#name-hint").strip() == hi["nameHint"], pg.page.inner_text("#name-hint"))
    lines = pg.rect("#name-hint")["height"] / 16.8
    check("360px: the Hindi hint takes at most two lines", lines <= 2.2, f"{lines:.1f} lines")
    pg.page.evaluate("showStage('stage-milan')")
    phs = pg.page.eval_on_selector_all(".milan-card [data-f='name']", "els => els.map(e => e.placeholder)")
    check("HI: both Kundali Milan name fields use the Hindi placeholder",
          phs == [hi["nameOptPh"]] * 2, str(phs))
    pg.page.context.close()

    pg = form_at(360, 640)
    lines = pg.rect("#name-hint")["height"] / 16.8
    check("360px: the English hint takes at most two lines", lines <= 2.2, f"{lines:.1f} lines")
    pg.page.context.close()

    pg = form_at(320, 568)
    sw = pg.page.evaluate("[document.documentElement.scrollWidth, window.innerWidth]")
    check("320px: the birth form does not scroll sideways", sw[0] <= sw[1], str(sw))
    pg.page.context.close()


def main() -> int:
    with server() as base, sync_playwright() as p:
        browser = p.chromium.launch()
        validation_without_a_place(p, browser, base)
        place_search_and_cast(p, browser, base)
        unknown_birth_time(p, browser, base)
        name_field_is_optional(p, browser, base)
        name_hint_on_phones(p, browser, base)
        browser.close()
    return check.finish("chart casting (place search, unknown time, validation, optional name)")


if __name__ == "__main__":
    raise SystemExit(main())
