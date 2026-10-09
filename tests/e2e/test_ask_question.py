"""Asking a question end to end: streaming, the stop button, starter chips
hiding, a Hindi answer, the paywall at 0 credits, and the 3 free credits
(DIVASTRO-154; 10 before it) being consumed (DIVASTRO-72, flow 6).

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.e2e.test_ask_question
"""

from __future__ import annotations

import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from playwright.sync_api import sync_playwright  # noqa: E402

from tests.e2e.harness import DESKTOPS, Checker, Page, server  # noqa: E402

check = Checker()

_DEVANAGARI = re.compile(r"[\u0900-\u097F]")


def ask(pg: Page, text: str) -> None:
    pg.page.fill("#q", text)
    pg.page.click("#send")


def streaming_and_starters(p, browser, base: str) -> None:
    print("\n[asking a question streams an answer and hides the starter chips]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    pg.open_chat()

    check("starters are visible before asking anything",
          pg.page.is_visible("#starters"))
    bot_before = pg.page.locator(".msg.bot").count()

    ask(pg, "What does my chart say about career?")
    check("starters hide immediately on send", not pg.page.is_visible("#starters"))
    check("state.busy flips true while the request is in flight",
          pg.page.evaluate("state.busy") is True)

    pg.page.wait_for_function("state.busy === false", timeout=20000)
    pg.page.wait_for_function(
        "n => document.querySelectorAll('.msg.bot').length > n", arg=bot_before, timeout=20000)
    check("a new answer bubble actually arrived",
          pg.page.locator(".msg.bot").count() > bot_before)
    check("#send is usable again once the stream finishes",
          not pg.page.is_disabled("#send"))

    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    check("no CSP violations", not pg.csp_violations(), str(pg.csp_violations()[:2]))
    ctx.close()


def stop_button(p, browser, base: str) -> None:
    print("\n[the stop button aborts an in-flight answer cleanly]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    pg.open_chat()

    # The no-LLM test path answers almost instantly, too fast to reliably
    # click Stop against a real request — delay the request reaching the
    # server instead, which is enough to hold state.busy true for a window.
    # A plain time.sleep(), not a Playwright page call: a route handler runs
    # on the same page, so pg.page.wait_for_timeout() here would block the
    # whole page (and nearly brought the browser down when tried).
    def delay_ask(route):
        time.sleep(2)
        route.continue_()

    pg.page.route("**/api/ask/stream", delay_ask)
    check("the stop button starts hidden", not pg.page.is_visible("#stop"))
    ask(pg, "What does my chart say about money?")
    pg.page.wait_for_selector("#stop", state="visible", timeout=5000)
    check("the stop button appears while a request is in flight", True)

    pg.page.click("#stop")
    pg.page.wait_for_function("state.busy === false", timeout=10000)
    pg.page.unroute("**/api/ask/stream")

    # state.provider === "off" (the test path, no real LLM available here)
    # delivers the whole answer atomically on the first SSE event — there is
    # no delta-streaming phase to interrupt, so a .bubble-incomplete marker
    # needs a real streaming provider this environment doesn't have, and
    # whether the single analysis event wins the race against the artificial
    # delay before Stop is clicked varies run to run (not something to
    # assert on). What's stable and worth checking: the abort leaves the UI
    # clean, not stuck.
    check("#stop hides again once aborted", not pg.page.is_visible("#stop"))
    check("#q is usable again after stopping", not pg.page.is_disabled("#q"))

    bot_before_retry = pg.page.locator(".msg.bot").count()
    ask(pg, "A real question after stopping the previous one.")
    pg.page.wait_for_function("state.busy === false", timeout=20000)
    pg.page.wait_for_function(
        "n => document.querySelectorAll('.msg.bot').length > n",
        arg=bot_before_retry, timeout=20000)
    check("asking again after a stop works normally, nothing left stuck",
          pg.page.locator(".msg.bot").count() > bot_before_retry)

    check("no CSP violations", not pg.csp_violations(), str(pg.csp_violations()[:2]))
    ctx.close()


def hindi_answer(p, browser, base: str) -> None:
    print("\n[a Hindi answer: the request says hi, and the bubble actually reads Hindi]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    pg.open_chat()

    bodies: list[str] = []
    pg.page.on("request", lambda r: bodies.append(r.post_data or "")
               if r.url.endswith("/api/ask/stream") else None)

    pg.set_lang("hi")
    # castChart() kicks off its own background loadAndShowDashboard() call
    # that can resolve after harness.open_chat() already moved to
    # stage-chat, flipping the active stage away from chat under this
    # test's feet. Force it back rather than guess at the exact timing.
    pg.page.evaluate("showStage('stage-chat')")
    pg.page.wait_for_selector("#q", state="visible", timeout=10000)
    bot_before = pg.page.locator(".msg.bot").count()
    ask(pg, "मेरे करियर के बारे में क्या कहता है?")
    pg.page.wait_for_function("state.busy === false", timeout=20000)
    pg.page.wait_for_function(
        "n => document.querySelectorAll('.msg.bot').length > n", arg=bot_before, timeout=20000)

    check("the ask request declared Hindi", len(bodies) == 1 and '"language":"hi"' in bodies[0],
          str(bodies))
    answer_text = pg.page.locator(".msg.bot .bubble").last.inner_text()
    check("the rendered answer actually contains Devanagari text",
          bool(_DEVANAGARI.search(answer_text)), answer_text[:200])

    check("no console errors", not pg.console_errors, "; ".join(pg.console_errors[:3]))
    check("no CSP violations", not pg.csp_violations(), str(pg.csp_violations()[:2]))
    ctx.close()


def paywall_after_free_questions(p, browser, base: str) -> None:
    print("\n[the 3 free questions are actually consumed, then the paywall opens]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    # A dedicated account: the default e2e@example.com is shared by every
    # other sub-test in this file and would already be a few questions into
    # its free balance by the time this one runs.
    pg.open_chat(email="e2e-paywall@example.com", name="Paywall Tester", credits=None)

    me = pg.page.context.request.get(f"{base}/api/me").json()
    # DIVASTRO-154: new accounts get 3 (ASTRO_FREE_QUESTIONS), down from 10.
    check("a fresh sign-up starts with 3 free questions",
          me["user"]["credits"] == 3 and me["free_questions"] == 3, str(me))

    pill_text = pg.page.locator("#btn-credits").inner_text()
    check("the credits pill shows 3 up front", "3" in pill_text and "10" not in pill_text, pill_text)

    for i in range(3):
        bot_before = pg.page.locator(".msg.bot").count()
        ask(pg, f"Question number {i + 1} about my life.")
        pg.page.wait_for_function("state.busy === false", timeout=20000)
        pg.page.wait_for_function(
            "n => document.querySelectorAll('.msg.bot').length > n",
            arg=bot_before, timeout=20000)

    me_after = pg.page.context.request.get(f"{base}/api/me").json()
    check("all 3 free questions were actually consumed",
          me_after["user"]["credits"] == 0, str(me_after["user"]))

    statuses: list[int] = []
    pg.page.on("response", lambda r: statuses.append(r.status)
               if r.url.endswith("/api/ask/stream") else None)
    ask(pg, "One more question, now that I'm out of credits.")
    pg.page.wait_for_timeout(2000)
    check("the 4th question is refused with 402, not silently answered",
          402 in statuses, str(statuses))
    check("the store/paywall modal opens on a 402",
          pg.page.locator(".modal, .modal-backdrop").count() > 0)

    check("no CSP violations", not pg.csp_violations(), str(pg.csp_violations()[:2]))
    ctx.close()


def signin_after_rejected_question(p, browser, base: str) -> None:
    print("\n[a question the server refuses with 401 opens a sign-in sheet that says the question is kept (DIVASTRO-129)]")
    ctx = browser.new_context(**DESKTOPS["desktop_1440x800"])
    pg = Page(ctx.new_page(), base)
    pg.open_chat()
    pg.page.route("**/api/ask/stream", lambda route: route.fulfill(
        status=401, content_type="application/json", body='{"detail":"Sign in to ask."}'))
    ask(pg, "Will I change my job this year?")
    pg.page.wait_for_selector(".modal-title", timeout=10000)
    title = pg.page.locator(".modal-title").first.inner_text()
    sub = pg.page.locator(".modal-sub").first.inner_text()
    check("the sheet is the 'one step to get your answer' version", "get your answer" in title, title)
    check("it says the question is saved", "saved" in sub, sub)
    if pg.page.locator("#email-open").count():
        first = pg.page.evaluate("document.querySelector('#oauth-list').firstElementChild.id")
        check("the email-code route is listed first", first == "email-open", first)
    check("no console errors", not [e for e in pg.console_errors if "401" not in e],
          "; ".join(pg.console_errors[:3]))
    ctx.close()


def main() -> int:
    with server() as base, sync_playwright() as p:
        browser = p.chromium.launch()
        streaming_and_starters(p, browser, base)
        stop_button(p, browser, base)
        hindi_answer(p, browser, base)
        paywall_after_free_questions(p, browser, base)
        signin_after_rejected_question(p, browser, base)
        browser.close()
    return check.finish("ask a question (streaming, stop, Hindi, paywall)")


if __name__ == "__main__":
    raise SystemExit(main())
