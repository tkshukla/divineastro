"""DIVASTRO-154 in a real browser: one answer without signing in, then 3 free questions.

  1. A signed-out visitor (an ordinary phone browser) casts a chart and sees "Ask your
     first question free — no sign-in needed" above the question box. They ask, and a
     real answer arrives, with "Sign up to ask 3 more free questions" under it.
  2. Their next question opens the DIVASTRO-129 sign-in sheet, titled "Sign in to keep
     asking — 3 more questions free", and the question is parked.
  3. They sign up in the sheet: the welcome says 3, the guest answer is still on screen,
     and the parked question is asked and answered (3 - 1 = 2 left).
  4. The same after a full-page sign-in (OAuth): the guest answer is put back.
  5. Hindi: the same three screens in Hindi.
  6. A headless browser (a bot to the server) gets no guest answer: straight to the sheet.
  7. Home, Plans, the sign-in sheet, the store, /pricing and /hi/pricing say 3 and the
     guest line, and no rendered page or i18n file says 10 free questions anywhere.

Screenshots (390px wide, en + hi) go to tests/e2e/shots/guest_*.png, or to
$ASTRO_SHOTS_DIR when that is set.

    python -m tests.e2e.test_guest_answer
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from playwright.sync_api import sync_playwright  # noqa: E402

from tests.e2e.harness import BIRTH, ROOT, Checker, Page, server, set_lang  # noqa: E402

check = Checker()
SHOTS = Path(os.environ.get("ASTRO_SHOTS_DIR") or Path(__file__).parent / "shots")
PHONE_UA = ("Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/128.0.0.0 Mobile Safari/537.36")
_n = [0]


def phone(browser, ua: str | None = None):
    """A 390px phone with an ordinary (non-headless) browser string, a new one per call so
    each is a different visitor to the server's day-scoped hash."""
    _n[0] += 1
    return browser.new_context(
        viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True, device_scale_factor=2,
        user_agent=ua or PHONE_UA.replace("128.0.0.0", f"128.0.0.{_n[0]}"))


# "10 free" and its equivalents in the 13 languages (ASCII or native digits).
TEN = r"(?:10|१०|১০|੧੦|૧૦|୧୦|೧೦|౧౦|௧௦|൧൦)"
FREE = (r"(?:free|FREE|मुफ़्त|मुफ्त|फ्री|निःशुल्क|मोफत|ಉಚಿತ|ఉచిత|இலவச|സൗജന്യ|বিনামূল্যে|বিনামূলীয়া|"
        r"ମାଗଣା|ਮੁਫ਼ਤ|મફત)")
STRAY = re.compile(rf"{TEN}[^\n\d]{{0,25}}{FREE}|{FREE}[^\n\d]{{0,25}}(?<![₹\d]){TEN}(?!\d)")


def stray(text: str) -> list[str]:
    return [m.group(0) for m in STRAY.finditer(text)]


def shot(pg: Page, name: str) -> None:
    SHOTS.mkdir(parents=True, exist_ok=True)
    pg.page.screenshot(path=str(SHOTS / f"guest_{name}.png"))


def cast_signed_out(pg: Page) -> None:
    pg.open_home()
    pg.page.wait_for_function("typeof acct !== 'undefined' && acct.freeKnown")
    # What the birth form does for a signed-out visitor: cast, and park the chart.
    pg.page.evaluate("async (b) => { await castChart(b); await saveBirth(b); showStage('stage-chat'); }", BIRTH)
    pg.page.wait_for_selector("#thread .msg.bot", timeout=30000)
    pg.page.evaluate("state.provider = 'off'")        # no LLM here: the rule engine answers
    pg.page.wait_for_timeout(400)


def ask(pg: Page, q: str) -> None:
    pg.page.fill("#q", q)
    pg.page.click("#send")


def guest_flow(browser, base: str, lang: str) -> None:
    print(f"\n[{lang}] a signed-out visitor: one answer, then the sign-in sheet, then sign up")
    ctx = phone(browser)
    pg = Page(ctx.new_page(), base)
    pg.open_home()
    if lang != "en":
        set_lang(pg.page, lang)
    cast_signed_out(pg)
    want = {"en": "Ask your first question free — no sign-in needed",
            "hi": "पहला प्रश्न मुफ़्त पूछें — साइन-इन की ज़रूरत नहीं"}[lang]
    check(f"[{lang}] the chat shows the guest line above the question box",
          pg.page.is_visible("#guest-line") and pg.page.inner_text("#guest-line").strip() == want,
          pg.page.inner_text("#guest-line"))
    line, box = pg.rect("#guest-line"), pg.rect("#ask-form")
    check(f"[{lang}] ...right above it, on screen", line and box and line["bottom"] <= box["top"] + 1
          and box["bottom"] <= 844, str((line, box)))
    shot(pg, f"{lang}_1_chat_signed_out")

    q1 = "Will I get a new job this year?" if lang == "en" else "क्या इस साल नई नौकरी मिलेगी?"
    ask(pg, q1)
    pg.page.wait_for_selector(".offer-card.guest-cta", timeout=30000)
    bots = pg.page.locator("#thread .msg.bot").count()
    answer = pg.page.locator("#thread .msg.bot").last.inner_text()
    check(f"[{lang}] the guest question gets a real answer", bots >= 2 and len(answer) > 80, answer[:80])
    cta = pg.page.inner_text(".offer-card.guest-cta .offer-text")
    want_cta = {"en": "Sign up to ask 3 more free questions", "hi": "साइन अप करें और 3 और प्रश्न मुफ़्त पूछें"}[lang]
    check(f"[{lang}] under it: '{want_cta}'", cta.strip() == want_cta, cta)
    check(f"[{lang}] the guest line is gone once the answer is used", not pg.page.is_visible("#guest-line"))
    check(f"[{lang}] no sign-in sheet for the first question", pg.page.locator(".modal").count() == 0)
    pg.page.locator(".offer-card.guest-cta").scroll_into_view_if_needed()
    shot(pg, f"{lang}_2_guest_answer")

    q2 = "And my marriage?" if lang == "en" else "और मेरी शादी?"
    ask(pg, q2)
    pg.page.wait_for_selector(".modal .modal-title", timeout=15000)
    title = pg.page.inner_text(".modal .modal-title")
    want_title = {"en": "Sign in to keep asking — 3 more questions free",
                  "hi": "पूछते रहने के लिए साइन इन करें — 3 और प्रश्न मुफ़्त"}[lang]
    check(f"[{lang}] the second question opens the sign-in sheet: '{want_title}'", title.strip() == want_title, title)
    sheet = pg.page.inner_text(".modal")
    check(f"[{lang}] the sheet never says 10", not stray(sheet), str(stray(sheet)))
    parked = pg.page.evaluate("localStorage.getItem('astro.pendingQuestion')")
    check(f"[{lang}] the second question is parked", bool(parked) and json.loads(parked)["q"] == q2)
    shot(pg, f"{lang}_3_signin_sheet")

    # Sign up inside the sheet (the dev button stands in for email/phone/username here).
    email = f"guest-{lang}@e2e.test"
    pg.page.once("dialog", lambda d: d.accept(email))
    pg.page.click('.oauth-btn.dev[data-provider="dev"]')
    pg.page.wait_for_selector(".toast", timeout=10000)
    toast = pg.page.inner_text(".toast")
    check(f"[{lang}] signing up: the welcome says 3 free questions", " 3 " in f" {toast} " and not stray(toast), toast)
    try:
        pg.page.wait_for_function(
            "(q) => [...document.querySelectorAll('#thread .msg.user')].some(m => m.innerText.trim() === q)"
            " && document.querySelectorAll('#thread .msg.bot').length >= 3", arg=q2, timeout=30000)
        resumed = True
    except Exception:
        resumed = False
    check(f"[{lang}] the parked question is asked and answered", resumed)
    users = pg.page.evaluate("[...document.querySelectorAll('#thread .msg.user')].map(m => m.innerText.trim())")
    check(f"[{lang}] the guest answer is still on screen above it", users[:1] == [q1] and q2 in users, str(users))
    pg.page.wait_for_timeout(1500)
    me = pg.page.context.request.get(f"{base}/api/me").json()
    check(f"[{lang}] the new account got 3 and the parked question used one (2 left)",
          (me.get("user") or {}).get("credits") == 2, str(me.get("user"))[:120])
    unexpected = [m for m in pg.console_errors if "401" not in m]      # the 401 IS the sheet
    check(f"[{lang}] no console errors", not unexpected, "; ".join(unexpected[:2]))
    check(f"[{lang}] no CSP violations", not pg.csp_violations())
    ctx.close()


def oauth_flow(browser, base: str) -> None:
    print("\n[a full-page sign-in (Google) after the guest answer]")
    ctx = phone(browser)
    pg = Page(ctx.new_page(), base)
    cast_signed_out(pg)
    ask(pg, "Is this a good year for money?")
    pg.page.wait_for_selector(".offer-card.guest-cta", timeout=30000)
    ask(pg, "What about my health?")
    pg.page.wait_for_selector(".modal .modal-title", timeout=15000)
    pg.sign_in("guest-oauth@e2e.test", "Guest OAuth")             # the provider round trip
    pg.page.goto(base + "/?welcome=1", wait_until="domcontentloaded")
    try:
        pg.page.wait_for_function(
            "() => { const u = [...document.querySelectorAll('#thread .msg.user')].map(m => m.innerText.trim());"
            " return u.includes('Is this a good year for money?') && u.includes('What about my health?'); }",
            timeout=40000)
        ok = True
    except Exception:
        ok = False
    users = pg.page.evaluate("[...document.querySelectorAll('#thread .msg.user')].map(m => m.innerText.trim())")
    check("back from the provider: the guest question and answer are back on screen, then the parked one",
          ok and users.index("Is this a good year for money?") < users.index("What about my health?"),
          str(users) + " " + "; ".join(pg.console_errors[:3]))
    restored = pg.page.evaluate("""() => { const u = [...document.querySelectorAll('#thread .msg')];
            const i = u.findIndex(m => m.classList.contains('user') && m.innerText.trim() === 'Is this a good year for money?');
            return i >= 0 && !!u[i + 1] && u[i + 1].classList.contains('bot') && u[i + 1].innerText.length > 80; }""")
    check("...with its answer under it", restored)
    unexpected = [m for m in pg.console_errors if "401" not in m]
    check("no console errors on the way back", not unexpected, "; ".join(unexpected[:2]))
    ctx.close()


def bot_flow(browser, base: str) -> None:
    print("\n[a headless browser is a bot to the server: no guest answer]")
    ctx = browser.new_context(viewport={"width": 390, "height": 844})     # Playwright's own HeadlessChrome UA
    pg = Page(ctx.new_page(), base)
    cast_signed_out(pg)
    check("no guest line is offered", not pg.page.is_visible("#guest-line"))
    ask(pg, "Will I get a new job?")
    pg.page.wait_for_selector(".modal .modal-title", timeout=15000)
    check("the first question goes straight to the sign-in sheet (the DIVASTRO-129 one)",
          pg.page.inner_text(".modal .modal-title").strip() == "One step to get your answer",
          pg.page.inner_text(".modal .modal-title"))
    check("and nothing was answered", pg.page.locator(".offer-card.guest-cta").count() == 0)
    ctx.close()


def allowance_screens(browser, base: str) -> None:
    print("\n[home, Plans, sign-in sheet, store and /pricing say 3, never 10]")
    for lang in ("en", "hi"):
        ctx = phone(browser)
        pg = Page(ctx.new_page(), base)
        pg.open_home()
        if lang != "en":
            set_lang(pg.page, lang)
        pg.page.wait_for_function("typeof acct !== 'undefined' && acct.freeKnown")
        pg.page.wait_for_selector("#plans .plans-free", timeout=15000)
        badge = pg.page.inner_text("#free-badge-main")
        check(f"[{lang}] the home badge says 3", "3" in badge and not stray(badge), badge)
        plans = pg.page.inner_text("#plans .plans-free")
        want = {"en": "Your first answer needs no sign-in, and every new account gets 3 free questions.",
                "hi": "पहले उत्तर के लिए साइन-इन ज़रूरी नहीं, और हर नए खाते के साथ 3 प्रश्न मुफ़्त हैं।"}[lang]
        check(f"[{lang}] Plans: the guest line and 3", plans.startswith(want), plans)
        pg.page.locator("#plans").scroll_into_view_if_needed()
        shot(pg, f"{lang}_4_plans")
        body = pg.page.inner_text("body")
        check(f"[{lang}] the home screen never says 10 free", not stray(body), str(stray(body)))
        pg.page.click("#btn-signin")
        pg.page.wait_for_selector(".modal .modal-sub", timeout=10000)
        sub = pg.page.inner_text(".modal .modal-sub")
        check(f"[{lang}] the plain sign-in sheet says the first 3 are free", "3" in sub and not stray(sub), sub)
        ctx.close()

        ctx = phone(browser)
        pg = Page(ctx.new_page(), base)
        pg.page.goto(base + ("/pricing" if lang == "en" else "/hi/pricing"), wait_until="domcontentloaded")
        text = pg.page.inner_text("body")
        want = {"en": ["1 free answer without signing in", "3 free questions with a free account"],
                "hi": ["बिना साइन-इन 1 मुफ़्त उत्तर", "मुफ़्त खाते पर 3 मुफ़्त प्रश्न"]}[lang]
        check(f"[{lang}] /pricing states the guest answer and 3", all(w in text for w in want), text[:200])
        check(f"[{lang}] /pricing never says 10 free", not stray(text), str(stray(text)))
        pg.page.locator("h2").nth(0).scroll_into_view_if_needed()
        pg.page.evaluate("window.scrollTo(0, 0)")
        shot(pg, f"{lang}_5_pricing")
        ctx.close()

    ctx = phone(browser)
    pg = Page(ctx.new_page(), base)
    pg.sign_in("store154@e2e.test", "Store")
    pg.open_home()
    pg.page.wait_for_function("typeof acct !== 'undefined' && !!acct.user")
    check("a new account shows 3 in the header", "3" in pg.page.inner_text("#btn-credits"),
          pg.page.inner_text("#btn-credits"))
    pg.page.evaluate("openStore(false)")
    pg.page.wait_for_selector(".modal.store, .modal .store-sec", timeout=15000)
    store = pg.page.inner_text(".modal")
    check("the store never says 10 free", not stray(store), str(stray(store)))
    ctx.close()


def static_sweep(base: str) -> None:
    print("\n[no rendered page and no i18n file says 10 free]")
    for path in ("/", "/pricing", "/hi/pricing", "/kn/pricing", "/katha", "/free-kundali", "/hi/free-kundali",
                 "/terms", "/privacy"):
        with urllib.request.urlopen(base + path, timeout=30) as r:
            html = r.read().decode("utf-8")
        check(f"{path}: no '10 free' (or an equivalent) in the HTML", not stray(html), str(stray(html)[:3]))
    with urllib.request.urlopen(base + "/", timeout=30) as r:
        home = r.read().decode("utf-8")
    check("/: og:description carries the setting (3), no placeholder left",
          "AI ज्योतिषी से 3 सवाल फ्री" in home and "__FREE_QUESTIONS__" not in home)
    for p in sorted((ROOT / "app" / "static" / "i18n").glob("*.json")):
        table = json.loads(p.read_text(encoding="utf-8"))
        bad = {k: v for k, v in table.items() if isinstance(v, str) and stray(v)}
        check(f"i18n/{p.name}: no '10 free' equivalent", not bad, str(bad)[:200])
        check(f"i18n/{p.name}: the new strings are there with their placeholder",
              all(table.get(k) for k in ("guestAskFree", "acct.guestSignUp"))
              and all("{n}" in table.get(k, "") for k in ("acct.guestMore", "acct.signInKeepTitle", "acct.plansFreeGuest")))


def main() -> int:
    with server() as base, sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            guest_flow(browser, base, "en")
            guest_flow(browser, base, "hi")
            oauth_flow(browser, base)
            bot_flow(browser, base)
            allowance_screens(browser, base)
            static_sweep(base)
        finally:
            browser.close()
    return check.finish("guest answer (e2e)")


if __name__ == "__main__":
    sys.exit(main())
