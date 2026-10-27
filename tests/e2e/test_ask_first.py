"""DIVASTRO-167 in a browser: the home screen leads with a question.

24-27 Oct: ~30 visitors a day, 4 charts in 4 days and not one question to the AI.
The first screen is now "Ask your question — free, no sign-in", a field, Ask and five
topic chips; asking keeps the question, takes the birth details only if there is no
chart yet, casts it and sends the question by itself.

  a. The first screen at 390x844 and 360x640, English and Hindi: the heading (the
     guest promise), the field, Ask and all five chips are on screen without
     scrolling; the kundali button is still there under it; nothing scrolls sideways.
  b. A signed-out visitor taps "Marriage": the birth step shows "To answer, we need
     your birth details" and the question; only date, time and place. They fill it
     in: the chart is cast, the chat opens and the answer to THAT question arrives
     (the guest answer), with the sign-up line and the Starter line under it.
     Events: ask_box_shown home, ask_chip marriage, ask_start home, chart_cast, ask_sent.
  c. A festival page's "Have a question about your own chart?" chip opens
     /?ask=...: the question is prefilled, the same flow runs (ask_start page), the
     answer arrives. Hindi page -> Hindi app.
  d. A chart already cast in this tab: the answer comes without the form, from the
     home box and from a /?ask= link in the same tab.
  e. Signed in with a saved chart: asked on the most recent chart, no form.
  f. 320px: no sideways scroll on the home screen, the birth step, a festival page.

Screenshots: $ASTRO_SHOTS_DIR (default tests/e2e/shots/) ask_first_*.png.

    python -m tests.e2e.test_ask_first
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from playwright.sync_api import sync_playwright  # noqa: E402

from tests.e2e.harness import BIRTH, Checker, Page, server, set_lang  # noqa: E402

check = Checker()
SHOTS = Path(os.environ.get("ASTRO_SHOTS_DIR") or Path(__file__).parent / "shots")
# An ordinary phone browser: a headless browser string is a bot to app/guest.py and
# gets no guest answer (nor the "free, no sign-in" promise that goes with it).
PHONE_UA = ("Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/128.0.0.0 Mobile Safari/537.36")
CHIPS = ("marriage", "career", "money", "health", "muhurat")
TITLE_GUEST = {"en": "Ask your question — free, no sign-in",
               "hi": "अपना प्रश्न पूछें — मुफ़्त, साइन-इन की ज़रूरत नहीं"}
Q_MARRIAGE = {"en": "When will I get married?", "hi": "मेरी शादी कब होगी?"}
_n = [0]


def phone(browser, w: int = 390, h: int = 844):
    _n[0] += 1                      # a different visitor to the server's day-scoped hash each time
    return browser.new_context(viewport={"width": w, "height": h}, is_mobile=True, has_touch=True,
                               device_scale_factor=2,
                               user_agent=PHONE_UA.replace("128.0.0.0", f"128.0.7.{_n[0]}"))


def shot(pg: Page, name: str) -> None:
    SHOTS.mkdir(parents=True, exist_ok=True)
    pg.page.screenshot(path=str(SHOTS / f"ask_first_{name}.png"))


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


def sent(events: list[dict], name: str, detail: str | None = None) -> bool:
    return any(e.get("name") == name and (detail is None or e.get("detail") == detail) for e in events)


def no_llm(pg: Page) -> None:
    """No LLM in tests: the rule engine answers. Set before the question goes out (it
    is sent by itself now), after /api/llm has filled the narration picker."""
    pg.page.wait_for_function("typeof state !== 'undefined' && state.providers.length > 0", timeout=10000)
    pg.page.evaluate("state.provider = 'off'")


def hscroll(pg: Page) -> float:
    return pg.page.evaluate("document.documentElement.scrollWidth - window.innerWidth")


def fill_birth(pg: Page) -> None:
    """Date, time and place, the way a person does it."""
    pg.page.fill("#f-date", BIRTH["date"])
    pg.page.fill("#f-time", BIRTH["time"])
    pg.page.fill("#f-place", "Delhi")
    pg.page.wait_for_selector("#place-results li", timeout=15000)
    pg.page.click("#place-results li >> nth=0")
    pg.page.click("#cast")


def answered(pg: Page, question: str, timeout: int = 45000) -> None:
    """The question is in the thread as the visitor's, and an answer follows it."""
    pg.page.wait_for_function(
        """(q) => { const msgs = [...document.querySelectorAll('#thread .msg')];
                    const i = msgs.findIndex(m => m.classList.contains('user') && m.innerText.trim() === q);
                    return i >= 0 && msgs.slice(i + 1).some(m => m.classList.contains('bot')
                           && m.innerText.trim().length > 80) && !state.busy; }""",
        arg=question, timeout=timeout)


def first_screen(browser, base: str) -> None:
    print("\n[a. the question box is the first screen]")
    for w, h in ((390, 844), (360, 640)):
        for lang in ("en", "hi"):
            ctx = phone(browser, w, h)
            pg = Page(ctx.new_page(), base)
            pg.open_home()
            if lang != "en":
                set_lang(pg.page, lang)
            pg.page.wait_for_function("(t) => document.querySelector('#ask-title').textContent === t",
                                      arg=TITLE_GUEST[lang], timeout=10000)
            tag = f"{w}x{h} {lang}"
            check(f"[{tag}] heading: '{TITLE_GUEST[lang]}'",
                  pg.page.inner_text("#ask-title").strip() == TITLE_GUEST[lang])
            parts = ["#ask-title", "#ask-home-q", "#ask-home-go"] + [f'.ask-chip[data-topic="{c}"]' for c in CHIPS]
            rects = {s: pg.rect(s) for s in parts}
            off = {s: r["bottom"] for s, r in rects.items() if not r or r["bottom"] > h or r["top"] < 0
                   or r["right"] > w or r["left"] < 0}
            check(f"[{tag}] heading, field, Ask and the five chips are all on the first screen",
                  not off, str(off))
            chips = pg.page.eval_on_selector_all(".ask-chip", "els => els.map(e => e.textContent.trim())")
            check(f"[{tag}] five topic chips, all labelled", len(chips) == 5 and all(chips), str(chips))
            ph = pg.page.get_attribute("#ask-home-q", "placeholder")
            check(f"[{tag}] the field's example is '{Q_MARRIAGE[lang]}'", ph == Q_MARRIAGE[lang], ph)
            box, cta = pg.rect("#ask-box"), pg.rect("#home-cta")
            check(f"[{tag}] the question box comes first, the kundali button under it",
                  box["bottom"] <= cta["top"], f"{box['bottom']:.0f} / {cta['top']:.0f}")
            check(f"[{tag}] the kundali button is still on the first screen", cta["bottom"] <= h,
                  f"bottom {cta['bottom']:.0f} of {h}")
            check(f"[{tag}] Ask and the field are big enough for a thumb",
                  rects["#ask-home-go"]["height"] >= 44 and rects["#ask-home-q"]["height"] >= 44)
            check(f"[{tag}] nothing scrolls sideways", hscroll(pg) <= 1, str(hscroll(pg)))
            if lang == "hi":
                check(f"[{tag}] Hindi chips", "विवाह" in chips and pg.page.inner_text("#ask-home-go").strip() == "पूछें",
                      str(chips))
            shot(pg, f"home_{w}x{h}_{lang}")
            check(f"[{tag}] no console errors", not pg.console_errors, "; ".join(pg.console_errors[:2]))
            ctx.close()


def chip_flow(browser, base: str) -> None:
    print("\n[b. a chip -> birth step with the question -> cast -> the answer arrives by itself]")
    ctx = phone(browser)
    pg = Page(ctx.new_page(), base)
    events = track(pg)
    pg.open_home()
    pg.page.wait_for_function("typeof acct !== 'undefined' && acct.freeKnown && acct.guestLeft > 0")
    no_llm(pg)
    pg.page.wait_for_timeout(600)
    check("ask_box_shown 'home' is reported when the box is on screen", sent(events, "ask_box_shown", "home"),
          str(events))
    pg.page.tap('.ask-chip[data-topic="marriage"]')
    pg.page.wait_for_selector("#stage-birth.active", timeout=10000)
    q = Q_MARRIAGE["en"]
    check("the birth step opens", True)
    check("it says 'To answer, we need your birth details'",
          pg.page.inner_text("#ask-pending-note").strip() == "To answer, we need your birth details")
    check("...with the question above the form", q in pg.page.inner_text("#ask-pending-q"),
          pg.page.inner_text("#ask-pending-q"))
    check("only date, time (with 'don't know') and place: name and gender are folded away",
          pg.page.is_visible("#f-date") and pg.page.is_visible("#f-time") and pg.page.is_visible("#f-unknown")
          and pg.page.is_visible("#f-place") and pg.page.is_hidden("#f-name") and pg.page.is_hidden("#f-gender"))
    pend, form = pg.rect("#ask-pending"), pg.rect("#birth-form")
    check("the question sits above the form", pend["bottom"] <= form["top"] + 1)
    check("the chip reported ask_chip 'marriage' and ask_start 'home'",
          sent(events, "ask_chip", "marriage") and sent(events, "ask_start", "home"), str(events))
    shot(pg, "birth_step_en")

    fill_birth(pg)
    pg.page.wait_for_selector("#stage-chat.active", timeout=30000)
    answered(pg, q)
    check("the chart is cast and the chat opens with the question asked for them", True)
    check("the answer is the guest answer: the sign-up line follows it",
          pg.page.locator(".offer-card.guest-cta").count() == 1)
    pg.page.wait_for_selector("#thread .starter-inline", timeout=10000)
    topic = pg.page.get_attribute("#thread .starter-inline", "data-topic")
    check("the Starter line is under it (DIVASTRO-157), on the marriage topic", topic == "marriage", str(topic))
    check("the chat stays on screen (not the dashboard)", pg.page.is_visible("#stage-chat"))
    check("the question box is on screen and ready", pg.page.is_visible("#q") and pg.page.is_enabled("#q"))
    check("no birth step left behind", pg.page.is_hidden("#ask-pending"))
    check("chart_cast and ask_sent were reported", sent(events, "chart_cast") and sent(events, "ask_sent"),
          str([e["name"] for e in events]))
    check("ask_sent exactly once", sum(1 for e in events if e.get("name") == "ask_sent") == 1)
    shot(pg, "answer_en")
    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:2]))
    check("no CSP violations", not pg.csp_violations())
    ctx.close()


def typed_question(browser, base: str) -> None:
    print("\n[b2. a typed question, Hindi]")
    ctx = phone(browser)
    pg = Page(ctx.new_page(), base)
    events = track(pg)
    pg.open_home()
    set_lang(pg.page, "hi")
    no_llm(pg)
    q = "क्या इस साल नई नौकरी मिलेगी?"
    pg.page.click("#ask-home-go")
    pg.page.wait_for_timeout(300)
    check("an empty field asks nothing (the field gets the focus)",
          pg.page.is_visible("#stage-home") and pg.page.evaluate("document.activeElement.id") == "ask-home-q")
    pg.page.fill("#ask-home-q", q)
    pg.page.press("#ask-home-q", "Enter")
    pg.page.wait_for_selector("#stage-birth.active", timeout=10000)
    check("Hindi: 'उत्तर देने के लिए आपका जन्म विवरण चाहिए'",
          pg.page.inner_text("#ask-pending-note").strip() == "उत्तर देने के लिए आपका जन्म विवरण चाहिए")
    check("Hindi: the typed question is shown", q in pg.page.inner_text("#ask-pending-q"))
    shot(pg, "birth_step_hi")
    fill_birth(pg)
    answered(pg, q)
    check("Hindi: the typed question is answered by itself", True)
    check("ask_start 'home' without a chip", sent(events, "ask_start", "home") and not sent(events, "ask_chip"))
    ctx.close()


def page_link(browser, base: str) -> None:
    print("\n[c. a festival page's question link -> the same flow]")
    for lang, path in (("en", "/tyohar/diwali-2026"), ("hi", "/hi/vrat-tyohar")):
        ctx = phone(browser)
        pg = Page(ctx.new_page(), base)
        events = track(pg)
        pg.page.goto(base + path, wait_until="domcontentloaded")
        strip = pg.page.locator(".ask-strip")
        check(f"[{lang}] {path} carries the question strip", strip.count() == 1)
        bar, box = pg.rect(".wa-top"), pg.rect(".ask-strip")
        check(f"[{lang}] ...right after the WhatsApp bar", bar and box and box["top"] >= bar["bottom"] - 1)
        links = pg.page.eval_on_selector_all(".ask-strip-chip", "els => els.map(e => e.getAttribute('href'))")
        check(f"[{lang}] two or three question links into the app", 2 <= len(links) <= 3, str(links))
        href = links[0]
        qs = parse_qs(urlsplit(href).query)
        check(f"[{lang}] /?ask=<question>&lang={lang}&utm_medium=ask",
              href.startswith("/?") and qs.get("lang") == [lang] and qs.get("utm_medium") == ["ask"]
              and bool(qs.get("ask")), href)
        question = qs["ask"][0]
        if lang == "en":
            shot(pg, "festival_page_en")
        pg.page.click(".ask-strip-chip >> nth=0")
        pg.page.wait_for_function("typeof showStage === 'function'")
        no_llm(pg)
        pg.page.wait_for_selector("#stage-birth.active", timeout=15000)
        check(f"[{lang}] the app opens on the birth step with that question",
              question in pg.page.inner_text("#ask-pending-q"), pg.page.inner_text("#ask-pending-q"))
        check(f"[{lang}] ...in the page's language", pg.page.evaluate("state.lang") == lang)
        check(f"[{lang}] the question is prefilled in the home box too",
              pg.page.input_value("#ask-home-q") == question)
        check(f"[{lang}] the question is dropped from the address bar", "ask=" not in pg.page.url, pg.page.url)
        check(f"[{lang}] ask_start 'page'", sent(events, "ask_start", "page"), str(events))
        fill_birth(pg)
        answered(pg, question)
        check(f"[{lang}] the answer to that question arrives", True)
        check(f"[{lang}] ask_sent", sent(events, "ask_sent"))
        if lang == "hi":
            shot(pg, "from_page_hi")
        check(f"[{lang}] no console errors", not pg.console_errors, "; ".join(pg.console_errors[:2]))
        ctx.close()

    # Any other /?ask= link (shared by hand): "link".
    ctx = phone(browser)
    pg = Page(ctx.new_page(), base)
    events = track(pg)
    pg.page.goto(base + "/?ask=" + "How%20is%20my%20career%3F", wait_until="domcontentloaded")
    pg.page.wait_for_selector("#stage-birth.active", timeout=15000)
    check("a plain /?ask= link: ask_start 'link'", sent(events, "ask_start", "link"), str(events))
    ctx.close()


def chart_already(browser, base: str) -> None:
    print("\n[d. a chart already cast in this tab: no form]")
    ctx = phone(browser)
    pg = Page(ctx.new_page(), base)
    events = track(pg)
    pg.open_home()
    pg.page.wait_for_function("typeof acct !== 'undefined' && acct.freeKnown")
    no_llm(pg)
    pg.page.evaluate("async (b) => { await castChart(b); showStage('stage-home'); }", BIRTH)
    q = "How will my health be this year?"
    pg.page.tap('.ask-chip[data-topic="health"]')
    pg.page.wait_for_selector("#stage-chat.active", timeout=15000)
    answered(pg, q)
    check("the answer comes straight away, no birth step", not sent(events, "screen", "birth"),
          str([e for e in events if e.get("name") == "screen"]))

    # The same tab, a new page load from a /?ask= link: the chart cast earlier in this
    # session is used again (the guest answer is spent now, so the sign-in sheet may
    # follow; the point is that the question is asked without the form).
    q2 = "When will I get married?"
    pg.page.goto(base + "/?ask=" + "When%20will%20I%20get%20married%3F", wait_until="domcontentloaded")
    pg.page.wait_for_function("typeof showStage === 'function'")
    no_llm(pg)
    pg.page.wait_for_function(
        "(q) => [...document.querySelectorAll('#thread .msg.user')].some(m => m.innerText.trim() === q)",
        arg=q2, timeout=30000)
    check("after a reload in the same tab, a /?ask= question is asked on that chart, no form",
          pg.page.is_hidden("#stage-birth") and pg.page.is_hidden("#ask-pending"))
    ctx.close()


def signed_in(browser, base: str) -> None:
    print("\n[e. signed in with saved charts: the most recent one]")
    ctx = phone(browser)
    pg = Page(ctx.new_page(), base)
    events = track(pg)
    pg.sign_in("askfirst@example.com", "Ask First")
    pg.open_home()
    older = dict(BIRTH, name="Older", date="1970-01-01")
    pg.page.evaluate("async (b) => { await castChart(b); await saveBirth(b); }", older)
    pg.page.wait_for_timeout(400)
    pg.page.evaluate("async (b) => { await castChart(b); await saveBirth(b); }", BIRTH)
    pg.page.wait_for_timeout(400)
    page2 = ctx.new_page()                     # a fresh visit: nothing open, a new tab session
    pg2 = Page(page2, base)
    ev2 = track(pg2)
    pg2.open_home()
    pg2.page.wait_for_function("typeof acct !== 'undefined' && !!acct.user", timeout=15000)
    no_llm(pg2)
    title = pg2.page.inner_text("#ask-title").strip()
    check("signed in, the heading carries their own balance", "3 questions left" in title, title)
    q = "Will my money situation improve this year?"
    pg2.page.tap('.ask-chip[data-topic="money"]')
    pg2.page.wait_for_selector("#stage-chat.active", timeout=20000)
    answered(pg2, q)
    check("asked and answered without the form", not sent(ev2, "screen", "birth"))
    check("on the most recent saved chart", pg2.page.inner_text("#who-name").strip() == BIRTH["name"],
          pg2.page.inner_text("#who-name"))
    check("no sign-in sheet, no guest line (the normal signed-in path)",
          pg2.page.locator(".modal").count() == 0 and pg2.page.locator(".guest-cta").count() == 0)
    check("no console errors", not pg2.console_errors, "; ".join(pg2.console_errors[:2]))
    ctx.close()


def narrow(browser, base: str) -> None:
    print("\n[f. 320px: nothing scrolls sideways]")
    ctx = phone(browser, 320, 568)
    pg = Page(ctx.new_page(), base)
    pg.open_home()
    pg.page.wait_for_timeout(500)
    check("home at 320px", hscroll(pg) <= 1, str(hscroll(pg)))
    r = pg.rect("#ask-home-go")
    check("Ask fits beside the field at 320px", r["right"] <= 320, str(r))
    shot(pg, "home_320")
    pg.page.tap('.ask-chip[data-topic="muhurat"]')
    pg.page.wait_for_selector("#stage-birth.active", timeout=10000)
    check("the birth step at 320px", hscroll(pg) <= 1, str(hscroll(pg)))
    for path in ("/tyohar/diwali-2026", "/hi/kundali-milan", "/naam-se-kundali-milan?boy=Rahul&girl=Priya"):
        pg.page.goto(base + path, wait_until="domcontentloaded")
        check(f"{path} at 320px", hscroll(pg) <= 1 and pg.page.locator(".ask-strip").count() == 1,
              str(hscroll(pg)))
    ctx.close()


def main() -> int:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            with server() as base:
                first_screen(browser, base)
                chip_flow(browser, base)
                typed_question(browser, base)
                page_link(browser, base)
                chart_already(browser, base)
                signed_in(browser, base)
                narrow(browser, base)
        finally:
            browser.close()
    return check.finish("question first")


if __name__ == "__main__":
    raise SystemExit(main())
