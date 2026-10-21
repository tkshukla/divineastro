"""DIVASTRO-158 in a browser: a signed-out visitor buys the Rs 21 Starter without
signing in, types their 3 questions, and gets the answers by email. On a 390px phone,
English and Hindi, on the test gateway, with the real emailed-answer worker (Claude
writes, through the FAKE `anthropic` package in tests/e2e/fake_anthropic) and the
console mail transport, so nothing leaves the machine:

  1. [en] signed out: cast a chart, take the free answer, ask again: the sign-in sheet
     now offers "Pay Rs 21 with UPI / card — no sign-in needed" above the sign-in
     choices (which are all still there);
  2. the guest sheet: email (a bad one is refused in place), optional phone, pay;
     "Sign in instead" stays;
  3. paid on the test gateway: the order page asks for the 3 questions, the question
     the sheet interrupted already in the first box; they are sent and listed as on
     their way; still nobody is signed in;
  4. the worker emails the 3 answers to that address, and the buyer gets the order
     link; the link opens the order page in another browser, with the 3 questions
     marked emailed;
  5. signing in with that address (dev sign-in = Google's path) shows the 3 answers in
     My questions and the Starter as bought;
  6. [hi] an address that already has an account, from openStore's Starter offer
     (what an in-app Starter card calls): the Hindi sheet, paid, credited to that
     account without signing the buyer in.

Screenshots: $ASTRO_SHOTS_DIR (default tests/e2e/shots/) guestpay_*.png.

    python -m tests.e2e.test_guest_checkout
"""

from __future__ import annotations

import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from playwright.sync_api import sync_playwright  # noqa: E402

from tests.e2e.harness import BIRTH, SERVER_LOGS, Checker, Page, server, set_lang  # noqa: E402

check = Checker()
SHOTS = Path(os.environ.get("ASTRO_SHOTS_DIR") or Path(__file__).parent / "shots")
FAKE_ANTHROPIC = Path(__file__).resolve().parent / "fake_anthropic"
PHONE_UA = ("Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/128.0.0.0 Mobile Safari/537.36")
_n = [0]


def phone(browser):
    _n[0] += 1
    return browser.new_context(
        viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True, device_scale_factor=2,
        user_agent=PHONE_UA.replace("128.0.0.0", f"128.0.1.{_n[0]}"))


def shot(pg: Page, name: str) -> None:
    SHOTS.mkdir(parents=True, exist_ok=True)
    pg.page.screenshot(path=str(SHOTS / f"guestpay_{name}.png"))


def no_overflow(pg: Page) -> bool:
    return pg.page.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1")


def me(pg: Page):
    return pg.page.context.request.get(f"{pg.base}/api/me").json()["user"]


def cast_signed_out(pg: Page) -> None:
    pg.page.wait_for_function("typeof acct !== 'undefined' && acct.freeKnown")
    pg.page.evaluate("async (b) => { await castChart(b); await saveBirth(b); showStage('stage-chat'); }", BIRTH)
    pg.page.wait_for_selector("#thread .msg.bot", timeout=30000)
    pg.page.evaluate("state.provider = 'off'")
    pg.page.wait_for_timeout(400)


def ask(pg: Page, q: str) -> None:
    pg.page.fill("#q", q)
    pg.page.click("#send")


def tappable(pg: Page, sel: str) -> bool:
    b = pg.page.locator(sel).first.bounding_box()
    return bool(b and b["height"] >= 40 and b["x"] >= 0 and b["x"] + b["width"] <= 390)


def english(browser, base: str) -> None:
    print("\n[en] signed out -> pay Rs 21 with only an email -> 3 questions -> answers by email")
    email = "guest-buyer@e2e-mail.org"
    ctx = phone(browser)
    pg = Page(ctx.new_page(), base)
    pg.open_home()
    cast_signed_out(pg)
    ask(pg, "Will I get a new job this year?")
    pg.page.wait_for_selector(".offer-card.guest-cta", timeout=30000)
    q2 = "When will I marry?"
    ask(pg, q2)
    pg.page.wait_for_selector(".modal .guest-pay-offer", timeout=15000)
    offer = pg.page.inner_text(".guest-pay-offer")
    check("[en] the sign-in sheet offers 'Pay ₹21 with UPI / card — no sign-in needed'",
          "Pay ₹21 with UPI / card — no sign-in needed" in offer
          and "Starter: 3 detailed answers by email" in offer, offer)
    check("[en] ...and keeps every sign-in choice below it",
          pg.page.locator(".modal .oauth-btn").count() >= 2 and pg.page.is_visible("#toggle-password-auth"))
    check("[en] 390px: the offer's button is on screen and tappable", tappable(pg, "#guest-pay-open")
          and no_overflow(pg))
    shot(pg, "en_1_signin_sheet_offer")

    pg.page.click("#guest-pay-open")
    pg.page.wait_for_selector(".modal.guest-pay #gp-email", timeout=10000)
    sheet = pg.page.inner_text(".modal.guest-pay")
    check("[en] the guest sheet: the Starter, ₹21, an email field, an optional phone, Sign in instead",
          "₹21" in sheet and "phone (optional)" in sheet.lower() and "Sign in instead" in sheet
          and pg.page.is_visible("#gp-phone"), sheet[:300])
    check("[en] 390px: the sheet fits, the pay button is tappable", no_overflow(pg) and tappable(pg, "#gp-pay"))
    shot(pg, "en_2_guest_sheet")
    pg.page.fill("#gp-email", "not-an-email")
    pg.page.click("#gp-pay")
    err = pg.page.inner_text(".modal.guest-pay .modal-error")
    check("[en] a bad address is refused in place", "valid email" in err, err)
    pg.page.fill("#gp-email", email)
    pg.page.fill("#gp-phone", "98765 43210")
    pg.page.click("#gp-pay")
    pg.page.wait_for_selector(".modal.guest-order #gq-form", timeout=15000)
    page_text = pg.page.inner_text(".modal.guest-order")
    check("[en] paid: the order page asks for the questions, sent to the typed address",
          "Paid ✓ Now type your questions" in page_text and email in page_text
          and "3 questions" in page_text, page_text[:300])
    first = pg.page.input_value("#gq-0")
    check("[en] the question the sheet interrupted is already in the first box", first == q2, first)
    check("[en] three boxes, 390px fits", pg.page.locator(".gq").count() == 3 and no_overflow(pg))
    check("[en] still not signed in", me(pg) is None)
    shot(pg, "en_3_order_page")
    pg.page.fill("#gq-1", "Is this a good year to buy a house?")
    pg.page.fill("#gq-2", "How is my health this year?")
    pg.page.click("#gq-send")
    pg.page.wait_for_selector(".modal.guest-order .guest-asked", timeout=15000)
    sent = pg.page.inner_text(".modal.guest-order")
    check("[en] sent: 'Your questions are in', the three listed as on their way",
          "Your questions are in" in sent and pg.page.locator(".guest-asked li").count() == 3
          and "on its way" in sent, sent[:400])
    check("[en] and the buyer is told how to keep them: sign in with that address",
          f"sign in with {email}" in sent)
    check("[en] still not signed in after asking", me(pg) is None and no_overflow(pg))
    shot(pg, "en_4_questions_sent")
    errors = [e for e in pg.console_errors if "401" not in e]
    check("[en] no console errors (besides the expected 401)", not errors, "; ".join(errors[:3]))
    check("[en] no CSP violations", not pg.csp_violations(), str(pg.csp_violations()[:2]))
    ctx.close()

    # The worker answers; the emails go out.
    log_path = SERVER_LOGS[base]
    deadline = time.time() + 120
    while time.time() < deadline:
        log = log_path.read_text(encoding="utf-8")
        if log.count(f"to {email}: Your detailed answer from Divine Astro") >= 3:
            break
        time.sleep(1)
    log = log_path.read_text(encoding="utf-8")
    check("[en] the 3 answers are emailed to the typed address",
          log.count(f"to {email}: Your detailed answer from Divine Astro") == 3)
    m = re.search(rf"to {re.escape(email)}: Your Starter is paid.*?(\S*\?gt=\S+)", log, re.S)
    check("[en] and the order link was emailed", m is not None)
    if not m:
        return

    # The emailed link, in another browser.
    ctx = phone(browser)
    pg = Page(ctx.new_page(), base)
    path = m.group(1).replace("https://divineastro.org", "")
    pg.page.goto(base + path, wait_until="domcontentloaded")
    pg.page.wait_for_selector(".modal.guest-order .guest-asked", timeout=15000)
    text = pg.page.inner_text(".modal.guest-order")
    check("[en] the emailed link opens the order page: 3 questions, emailed",
          text.count("Emailed ·") == 3 and "gt=" not in pg.page.url, text[:400])
    check("[en] the page shows no answer text (that goes only to the mailbox)", "A short reading" not in text)
    shot(pg, "en_5_link_order_page")

    # Signing in with that address: everything is there.
    pg.sign_in(email=email, name="Guest Buyer")
    u = me(pg)
    hist = pg.page.context.request.get(f"{base}/api/history").json()["questions"]
    done = [h for h in hist if h.get("emailed") and h["emailed"]["status"] == "done"]
    check("[en] signing in with that address: the 3 answers are in My questions",
          len(done) == 3 and any(h["question"] == q2 for h in done), str(len(done)))
    check("[en] ...the Starter shows as bought, and the welcome questions are there",
          u["starter"]["reason"] == "bought" and u["email_credits"] == 0 and u["credits"] == 3, str(u)[:200])
    ctx.close()


def hindi_existing(browser, base: str) -> None:
    print("\n[hi] an address that already has an account, from the Starter offer")
    email = "existing-hi@e2e-mail.org"
    owner = phone(browser)
    opg = Page(owner.new_page(), base)
    opg.sign_in(email=email, name="Pehle Se")
    before = me(opg)

    ctx = phone(browser)
    pg = Page(ctx.new_page(), base)
    pg.open_home()
    set_lang(pg.page, "hi")
    cast_signed_out(pg)
    pg.page.evaluate("openStore(false, STARTER_SKU)")
    pg.page.wait_for_selector(".modal.guest-pay #gp-email", timeout=10000)
    sheet = pg.page.inner_text(".modal.guest-pay")
    check("[hi] openStore's Starter offer opens the guest sheet in Hindi, not the sign-in sheet",
          "UPI / कार्ड से ₹21 चुकाएँ — साइन इन की ज़रूरत नहीं" in sheet and "इसके बजाय साइन इन करें" in sheet,
          sheet[:300])
    check("[hi] 390px fits", no_overflow(pg) and tappable(pg, "#gp-pay"))
    shot(pg, "hi_1_guest_sheet")
    pg.page.fill("#gp-email", email.upper())
    pg.page.click("#gp-pay")
    pg.page.wait_for_selector(".modal.guest-order #gq-form", timeout=15000)
    text = pg.page.inner_text(".modal.guest-order")
    check("[hi] paid: the Hindi order page, the same as for any address",
          "भुगतान हो गया ✓ अब अपने प्रश्न लिखें" in text and email in text, text[:300])
    check("[hi] nothing of the account shows (name)", "Pehle Se" not in text)
    check("[hi] the buyer is not signed in to that account", me(pg) is None)
    shot(pg, "hi_2_order_page")
    after = me(opg)
    check("[hi] the purchase is credited to the existing account",
          after["id"] == before["id"] and after["email_credits"] == 3 and after["starter"]["reason"] == "bought",
          str(after)[:200])
    pg.page.fill("#gq-0", "क्या इस साल नौकरी बदलूँ?")
    pg.page.click("#gq-send")
    pg.page.wait_for_selector(".modal.guest-order .guest-asked", timeout=15000)
    check("[hi] one question sent, 2 boxes left", pg.page.locator(".gq").count() == 2
          and pg.page.locator(".guest-asked li").count() == 1)
    shot(pg, "hi_3_one_sent")
    errors = [e for e in pg.console_errors if "401" not in e]
    check("[hi] no console errors", not errors, "; ".join(errors[:3]))
    ctx.close()
    owner.close()


def main() -> int:
    env = {
        "ASTRO_SMTP_HOST": "console", "ASTRO_EMAIL_ANSWER_POLL_S": "1", "ANTHROPIC_API_KEY": "fake-key-e2e",
        "PYTHONPATH": os.pathsep.join(p for p in (str(FAKE_ANTHROPIC), os.environ.get("PYTHONPATH", "")) if p),
    }
    with server(env) as base, sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            english(browser, base)
            hindi_existing(browser, base)
        finally:
            browser.close()
    return check.finish("Guest checkout (e2e)")


if __name__ == "__main__":
    sys.exit(main())
