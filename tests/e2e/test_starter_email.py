"""DIVASTRO-155 in a browser: run out of free questions, buy the Rs 21 Starter, ask, get
the answer by email and in My questions. English and Hindi, on a 390px phone.

The test server runs the real worker (app/emailed_answers.py, polling every second)
against a FAKE Ollama (tests/fake_ollama.py, started here) and a FAKE `anthropic`
package (tests/e2e/fake_anthropic, first on the server's PYTHONPATH), with the console
mail transport, so nothing leaves the machine:

  1. a new account asks its 3 free questions; under each free answer the Starter line
     (DIVASTRO-157, in the question's topic) offers it, one at a time;
  2. the 4th question opens the out-of-questions store with the Starter FIRST (Rs 21,
     no strike, no Save badge, once-per-account wording), and the 390px sheet fits;
  3. buying it on the test gateway shows "You have 3 emailed answers ..." and the
     interrupted question is asked: the chat shows the queued-answer card;
  4. the Starter is no longer in the store;
  5. the worker delivers: the email is in the server log, My questions shows the
     answer as emailed, with its text (Hindi for the Hindi customer);
  6. /pricing lists the Starter (en + hi).

Screenshots: $ASTRO_SHOTS_DIR (default tests/e2e/shots/) starter_<lang>_*.png.

    python -m tests.e2e.test_starter_email
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from playwright.sync_api import sync_playwright  # noqa: E402

from tests.e2e.harness import BIRTH, SERVER_LOGS, Checker, Page, server, set_lang  # noqa: E402
from tests.fake_ollama import FakeOllama  # noqa: E402

check = Checker()
SHOTS = Path(os.environ.get("ASTRO_SHOTS_DIR") or Path(__file__).parent / "shots")
FAKE_ANTHROPIC = Path(__file__).resolve().parent / "fake_anthropic"
SKU = "starter_email3"

WORDS = {
    "en": {"title": "Starter: 3 detailed answers by email",
           "sub": "Answers emailed within 30 minutes. One-time offer for new accounts.",
           "bought": "You have 3 emailed answers. Ask your next question as usual — the answer arrives by email within 30 minutes.",
           "queued": "Your detailed answer will be emailed to {email} within 30 minutes. You can also find it in My questions.",
           "nudge": "Get 3 detailed answers by email for ₹21.",
           "subject": "Your detailed answer from Divine Astro",
           "answer_bit": "steady rise through effort",
           "pricing": "/pricing", "once": "Once per account"},
    "hi": {"title": "स्टार्टर: ईमेल पर 3 विस्तृत उत्तर",
           "sub": "उत्तर 30 मिनट के भीतर ईमेल पर। नए खातों के लिए एक बार का ऑफ़र।",
           "bought": "आपके पास 3 ईमेल उत्तर हैं। अगला प्रश्न हमेशा की तरह पूछिए — उत्तर 30 मिनट के भीतर ईमेल पर आएगा।",
           "queued": "आपका विस्तृत उत्तर 30 मिनट के भीतर {email} पर ईमेल किया जाएगा। यह आपको मेरे प्रश्न में भी मिलेगा।",
           "nudge": "₹21 में ईमेल पर 3 विस्तृत उत्तर पाइए।",
           "subject": "डिवाइन एस्ट्रो से आपका विस्तृत उत्तर",
           "answer_bit": "धीरे-धीरे आगे बढ़ने",
           "pricing": "/hi/pricing", "once": "एक खाते पर एक बार"},
}


def phone(browser):
    return browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True,
                               has_touch=True, device_scale_factor=2)


def shot(pg: Page, name: str, full: bool = False) -> None:
    SHOTS.mkdir(parents=True, exist_ok=True)
    pg.page.screenshot(path=str(SHOTS / f"starter_{name}.png"), full_page=full)


def no_overflow(pg: Page) -> bool:
    return pg.page.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1")


def ask(pg: Page, q: str) -> None:
    pg.page.fill("#q", q)
    pg.page.click("#send")
    pg.page.wait_for_function("!state.busy", timeout=30000)
    pg.page.wait_for_timeout(300)


def me(pg: Page) -> dict:
    return pg.page.context.request.get(f"{pg.base}/api/me").json()["user"]


def flow(browser, base: str, lang: str) -> None:
    w = WORDS[lang]
    email = f"starter-{lang}@example.com"
    print(f"\n[{lang}] free questions -> Starter -> emailed answer")
    ctx = phone(browser)
    pg = Page(ctx.new_page(), base)
    pg.sign_in(email=email, name=f"Starter {lang}")
    pg.open_home()
    if lang != "en":
        set_lang(pg.page, lang)
    pg.page.evaluate("async (b) => { await castChart(b); showStage('stage-chat'); }", BIRTH)
    pg.page.wait_for_selector("#thread .msg.bot", timeout=30000)
    pg.page.evaluate("state.provider = 'off'")
    pg.page.wait_for_timeout(400)

    check(f"[{lang}] a new account: 3 free questions, Starter available",
          me(pg)["credits"] == 3 and me(pg)["starter"]["available"])
    ask(pg, "Will my career grow this year?")
    ask(pg, "Is this a good time to change jobs?")
    # DIVASTRO-157: the Starter line under a free answer (it took the 1-left nudge's place).
    nudge = pg.page.locator('#thread .starter-inline')
    check(f"[{lang}] under the free answer (1 left) one Starter line offers it (₹21)",
          nudge.count() == 1 and w["nudge"] in nudge.inner_text() and "₹21" in nudge.inner_text(),
          nudge.inner_text() if nudge.count() else "no card")
    if nudge.count():
        nudge.scroll_into_view_if_needed()
        shot(pg, f"{lang}_1_nudge")
    ask(pg, "What about my health?")
    check(f"[{lang}] the free questions are used up", me(pg)["credits"] == 0)

    # The 4th question: out of questions -> the store, the Starter first.
    pg.page.fill("#q", "When will I get a promotion?")
    pg.page.click("#send")
    pg.page.wait_for_selector(".modal.store", timeout=10000)
    pg.page.wait_for_timeout(500)
    first = pg.page.locator(".modal.store .store-sec").first
    check(f"[{lang}] the out-of-questions store leads with the Starter",
          first.get_attribute("data-sec") == "email_answers" and first.locator(f'.pack[data-sku="{SKU}"]').count() == 1)
    card = pg.page.locator(f'.pack[data-sku="{SKU}"]')
    text = card.inner_text()
    check(f"[{lang}] the card: title, ₹21, the 30-minute promise, one-time wording",
          w["title"] in text and "₹21" in text and w["sub"] in text, text)
    check(f"[{lang}] no strike-through price and no Save badge on it",
          card.locator("s.was").count() == 0 and card.locator(".save-badge").count() == 0)
    box = card.bounding_box()
    check(f"[{lang}] 390px: the card is inside the screen, the sheet has no sideways scroll",
          box and box["x"] >= 0 and box["x"] + box["width"] <= 390 and no_overflow(pg), str(box))
    btn = card.locator(".buy-btn").bounding_box()
    check(f"[{lang}] its Buy button is on screen and tappable (>= 36px)",
          btn and btn["y"] + btn["height"] <= 844 and btn["height"] >= 36, str(btn))
    shot(pg, f"{lang}_2_store_starter_first")

    # Buy it on the test gateway.
    card.locator(".buy-btn").click()
    pg.page.wait_for_selector(".starter-done", timeout=10000)
    pg.page.wait_for_timeout(700)                 # the sheet's slide-in
    msg = pg.page.inner_text(".starter-done")
    check(f"[{lang}] after paying: 'You have 3 emailed answers ...'", w["bought"] in msg, msg)
    shot(pg, f"{lang}_3_bought")
    st = me(pg)
    check(f"[{lang}] 3 emailed answers, still 0 instant questions, Starter no longer available",
          st["email_credits"] == 3 and st["credits"] == 0 and st["starter"]["reason"] == "bought", str(st))
    pg.page.click("#starter-ok")

    # The interrupted question is asked now, and queued.
    pg.page.wait_for_selector(".queued-card", timeout=15000)
    q = pg.page.locator(".queued-card").last
    qt = q.inner_text()
    check(f"[{lang}] the chat shows the queued-answer card with the address and 30 minutes",
          w["queued"].format(email=email) in " ".join(qt.split()), qt)
    qb = q.bounding_box()
    check(f"[{lang}] 390px: the queued card fits the screen, no sideways scroll",
          qb and qb["x"] >= 0 and qb["x"] + qb["width"] <= 390 and no_overflow(pg), str(qb))
    check(f"[{lang}] the header shows the emailed balance (2 left)",
          pg.page.locator("#btn-mail").count() == 1 and "2" in pg.page.inner_text("#btn-mail"))
    check(f"[{lang}] header fits at 390px with the extra pill", no_overflow(pg))
    q.scroll_into_view_if_needed()
    shot(pg, f"{lang}_4_queued_card")

    # The Starter is gone from the store (on a phone the balance pill opens it).
    pg.page.click("#btn-credits")
    pg.page.wait_for_selector(".modal.store", timeout=10000)
    check(f"[{lang}] once bought, the Starter is no longer in the store",
          pg.page.locator(f'.pack[data-sku="{SKU}"]').count() == 0)
    pg.page.click(".modal-x")

    # The worker delivers it.
    deadline = time.time() + 120
    done = None
    while time.time() < deadline:
        hist = pg.page.context.request.get(f"{base}/api/history").json()["questions"]
        done = next((h for h in hist if h.get("emailed") and h["emailed"]["status"] == "done"), None)
        if done:
            break
        time.sleep(1)
    check(f"[{lang}] the worker delivered the emailed answer", done is not None)
    log = SERVER_LOGS[base].read_text(encoding="utf-8")
    check(f"[{lang}] the email went out (console transport) with the answer in {lang}",
          f"to {email}: {w['subject']}" in log and w["answer_bit"] in log)

    # My questions shows it, delivered, with its text.
    pg.page.click("#btn-acct")
    pg.page.click('.acct-drop [data-act="history"]')
    pg.page.wait_for_selector(".hist-row.emailed", timeout=10000)
    row = pg.page.locator('.hist-row.emailed:has(.hist-mail[data-mail="done"])').first
    check(f"[{lang}] My questions: the emailed answer is marked delivered", row.count() == 1)
    row.locator("details.hist-answer > summary").click()
    pg.page.wait_for_timeout(300)
    body = row.locator(".hist-answer-body").inner_text()
    check(f"[{lang}] ...and its text opens in place", w["answer_bit"] in body, body[:160])
    check(f"[{lang}] 390px: My questions has no sideways scroll", no_overflow(pg))
    shot(pg, f"{lang}_5_my_questions")
    # The 402 of the 4th question is the paywall doing its job (the browser logs it).
    errors = [e for e in pg.console_errors if "402" not in e]
    check(f"[{lang}] no console errors (besides the expected 402)", not errors, "; ".join(errors[:3]))
    check(f"[{lang}] no CSP violations", not pg.csp_violations(), str(pg.csp_violations()[:2]))
    ctx.close()

    # /pricing
    ctx = phone(browser)
    pg = Page(ctx.new_page(), base)
    pg.page.goto(base + w["pricing"], wait_until="domcontentloaded")
    row = pg.page.locator(f'tr#{SKU}')
    check(f"[{lang}] /pricing lists the Starter at ₹21 with no strike",
          row.count() == 1 and "₹21" in row.inner_text() and row.locator("s").count() == 0)
    check(f"[{lang}] /pricing says once per account and 30 minutes",
          w["once"] in pg.page.inner_text("body") and "30" in pg.page.inner_text("body"))
    check(f"[{lang}] /pricing at 390px: no sideways scroll", no_overflow(pg))
    pg.page.locator("h2", has_text=w["title"].split(":")[0]).first.scroll_into_view_if_needed()
    shot(pg, f"{lang}_6_pricing")
    ctx.close()


def main() -> int:
    fake = FakeOllama().start()
    env = {
        "ASTRO_SMTP_HOST": "console", "ASTRO_EMAIL_ANSWER_OLLAMA_URL": fake.url, "ASTRO_EMAIL_ANSWER_WRITER": "ollama",
        "ASTRO_EMAIL_ANSWER_POLL_S": "1", "ANTHROPIC_API_KEY": "fake-key-e2e",
        "PYTHONPATH": os.pathsep.join(p for p in (str(FAKE_ANTHROPIC), os.environ.get("PYTHONPATH", "")) if p),
    }
    try:
        with server(env) as base, sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                flow(browser, base, "en")
                flow(browser, base, "hi")
            finally:
                browser.close()
    finally:
        fake.stop()
    return check.finish("Starter emailed answers (e2e)")


if __name__ == "__main__":
    sys.exit(main())
