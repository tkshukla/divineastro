"""DIVASTRO-170 in a browser: My questions opens the whole conversation.

Our first paying customer: "I cannot see the recent conversations as a conversation
history. It only shows a list of conversations, but when I tap one it does not open
the previous questions and answers" and "the emailed answers should also show on
screen in the saved history". On a 390px phone:

  1. ask 3 questions on a saved chart, reload, open My questions: one conversation,
     3 questions; tap it -> the chat for that chart with all 3 questions AND their
     full answers in order (Copy / Share under each), the tapped one in view;
  2. continue with a 4th question in the same thread; reopened, the thread has 4;
  3. a Starter emailed answer (the test gateway's comp grant, a held fake Ollama):
     while it is being written the thread shows "Writing your detailed answer ...",
     and once written (polled) it shows the answer with "Sent to your email";
  4. a question on a chart that was not saved: its conversation opens read-only with
     a note;
  5. 320x568: the thread opens, the question box is on screen, no sideways scroll;
  6. another account sees none of it (list empty, the thread key 404s); signed out,
     401.

Screenshots: $ASTRO_SHOTS_DIR (default tests/e2e/shots/) history_*.png.

    python -m tests.e2e.test_history
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from playwright.sync_api import sync_playwright  # noqa: E402

from tests.e2e.harness import BIRTH, Checker, Page, server  # noqa: E402
from tests.fake_ollama import FakeOllama  # noqa: E402

check = Checker()
SHOTS = Path(os.environ.get("ASTRO_SHOTS_DIR") or Path(__file__).parent / "shots")
FAKE_ANTHROPIC = Path(__file__).resolve().parent / "fake_anthropic"
EMAIL = "history-a@example.com"
QUESTIONS = ["Will my career grow this year?", "Is marriage likely soon?",
             "How will my health be?"]
OTHER_BIRTH = {**BIRTH, "name": "Unsaved Cousin", "date": "1992-02-02", "time": "08:15"}


def ctx_for(browser, w: int, h: int):
    return browser.new_context(viewport={"width": w, "height": h}, is_mobile=True,
                               has_touch=True, device_scale_factor=2)


def shot(pg: Page, name: str) -> None:
    SHOTS.mkdir(parents=True, exist_ok=True)
    pg.page.screenshot(path=str(SHOTS / f"history_{name}.png"))


def no_overflow(pg: Page) -> bool:
    """No sideways scroll: the page, and an open sheet (fixed, so the page's own
    width does not show it) and everything in it."""
    # The phone's width, not innerWidth: on a mobile viewport a page wider than the
    # screen widens the layout viewport (innerWidth) with it and the browser zooms out.
    return pg.page.evaluate("""(w) => {
      if (document.documentElement.scrollWidth > w + 1 || window.innerWidth > w + 1) return false;
      const m = document.querySelector('.modal');
      if (!m) return true;
      const r = m.getBoundingClientRect();
      if (r.left < -1 || r.right > w + 1) return false;
      return [...m.querySelectorAll('*')].every((e) => {
        const b = e.getBoundingClientRect();
        return !b.width || (b.left >= r.left - 1 && b.right <= r.right + 1);
      });
    }""", pg.page.viewport_size["width"])


def ask(pg: Page, q: str) -> None:
    pg.page.fill("#q", q)
    pg.page.click("#send")
    pg.page.wait_for_function("!state.busy", timeout=30000)
    pg.page.wait_for_timeout(300)


def admin_post(pg: Page, path: str, data: dict) -> None:
    ctx = pg.page.context.browser.new_context()
    try:
        r = ctx.request.post(f"{pg.base}/api/auth/dev", data={"email": "admin@e2e.test", "name": "Admin"})
        assert r.ok, r.status
        r = ctx.request.post(f"{pg.base}{path}", data=data)
        assert r.ok, r.text()
    finally:
        ctx.close()


def me(pg: Page) -> dict:
    return pg.page.context.request.get(f"{pg.base}/api/me").json()["user"]


def open_history(pg: Page) -> None:
    pg.page.click("#btn-acct")
    pg.page.click('.acct-drop [data-act="history"]')
    pg.page.wait_for_selector(".modal .hist", timeout=10000)
    pg.page.wait_for_timeout(300)


def thread_questions(pg: Page) -> list[str]:
    return pg.page.eval_on_selector_all(
        "#thread .past-thread .msg.user .bubble", "els => els.map(e => e.textContent.trim())")


def q_box_visible(pg: Page) -> bool:
    r = pg.rect("#q")
    vh = pg.page.viewport_size["height"]
    return bool(r) and r["top"] >= 0 and r["bottom"] <= vh + 1 and r["height"] > 20


def flow(browser, base: str, fake: FakeOllama) -> None:
    print("\n[390px] three questions, reload, open the conversation")
    ctx = ctx_for(browser, 390, 844)
    pg = Page(ctx.new_page(), base)
    pg.sign_in(email=EMAIL, name="History A")
    pg.top_up(10)
    pg.open_home()
    pg.page.wait_for_function("typeof acct !== 'undefined' && !!acct.user", timeout=10000)
    # What the birth form does: cast, then save (every signed-in cast is saved).
    pg.page.evaluate("async (b) => { await castChart(b); await saveBirth(b); showStage('stage-chat'); }", BIRTH)
    pg.page.wait_for_selector("#thread .msg.bot", timeout=30000)
    pg.page.evaluate("state.provider = 'off'")
    birth_id = pg.page.evaluate("state.currentBirthId")
    check("the cast-and-saved chart is the one the questions are asked on (birth id set)",
          isinstance(birth_id, int), str(birth_id))
    for q in QUESTIONS:
        ask(pg, q)
    live = pg.page.eval_on_selector_all("#thread .msg.bot .bubble", "els => els.map(e => e.innerText.trim())")[1:]

    pg.page.reload(wait_until="domcontentloaded")
    pg.page.wait_for_function("typeof acct !== 'undefined' && !!acct.user", timeout=10000)
    open_history(pg)
    convs = pg.page.locator(".modal .hist-conv")
    rows = pg.page.locator(".modal .hist-conv .hist-row")
    check("My questions: one conversation for the chart, with its 3 questions",
          convs.count() == 1 and rows.count() == 3, f"{convs.count()} / {rows.count()}")
    check("390px: My questions has no sideways scroll", no_overflow(pg))
    shot(pg, "1_my_questions_390")
    # Tap the first question asked (the list is newest first).
    rows.nth(2).click()
    pg.page.wait_for_function("document.querySelector('#stage-chat').classList.contains('active') "
                              "&& document.querySelectorAll('#thread .past-thread .msg.user').length >= 3",
                              timeout=30000)
    pg.page.wait_for_timeout(500)
    check("tapping it opens the chat with all 3 questions, in order",
          thread_questions(pg) == QUESTIONS, str(thread_questions(pg)))
    answers = pg.page.eval_on_selector_all("#thread .past-thread .msg.bot .bubble",
                                           "els => els.map(e => e.innerText.trim())")
    check("...each with its full answer (the same text the chat showed)",
          len(answers) == 3 and all(a and a[:80] in l for a, l in zip(answers, live)),
          f"{[a[:40] for a in answers]}")
    acts = pg.page.locator("#thread .past-thread .msg.bot .msg-actions")
    check("...with Copy / Share under every answer", acts.count() == 3)
    first = pg.rect("#thread .past-thread .msg.user")
    th = pg.rect("#thread")
    check("...scrolled to the tapped (first) question",
          first and th and first["top"] >= th["top"] - 2 and first["top"] < th["bottom"], f"{first} {th}")
    check("390px: the question box is on screen", q_box_visible(pg), str(pg.rect("#q")))
    check("390px: no sideways scroll", no_overflow(pg))
    shot(pg, "2_thread_390")

    print("\n[390px] continue the same conversation")
    ask(pg, "When will I buy a house?")
    hist = pg.page.context.request.get(f"{base}/api/history").json()
    check("the 4th question joins the same conversation",
          len(hist["threads"]) == 1 and hist["threads"][0]["count"] == 4, str(hist["threads"]))
    pg.page.reload(wait_until="domcontentloaded")
    pg.page.wait_for_function("typeof acct !== 'undefined' && !!acct.user", timeout=10000)
    open_history(pg)
    pg.page.locator(".modal .hist-conv-head").first.click()
    pg.page.wait_for_function("document.querySelectorAll('#thread .past-thread .msg.user').length >= 4",
                              timeout=30000)
    check("reopened, the thread has all 4 questions in order",
          thread_questions(pg) == QUESTIONS + ["When will I buy a house?"], str(thread_questions(pg)))
    last = pg.rect("#thread .past-thread .msg.bot:last-of-type")
    check("opened from the conversation (not a question): scrolled to the latest",
          pg.page.evaluate("(() => { const t = document.querySelector('#thread');"
                           " return t.scrollHeight - t.scrollTop - t.clientHeight < 80; })()"), str(last))

    print("\n[390px] a Starter emailed answer: writing, then delivered")
    uid = me(pg)["id"]
    admin_post(pg, f"/api/admin/users/{uid}/grant", {"kind": "product", "sku": "starter_email3", "note": "e2e"})
    admin_post(pg, f"/api/admin/users/{uid}/credits", {"delta": -me(pg)["credits"], "note": "e2e: spend"})
    st = me(pg)
    check("the account now has 0 instant questions and 3 emailed answers",
          st["credits"] == 0 and st["email_credits"] == 3, str({k: st[k] for k in ("credits", "email_credits")}))
    fake.gate.clear()                                     # the local model "thinks" until released
    pg.page.evaluate("window.DA_THREAD_POLL_MS = 1000")
    ask(pg, "What does my chart say about my career this year?")
    pg.page.wait_for_selector("#thread .queued-card", timeout=15000)
    # Wait until the worker has picked it up (and is held by the fake model).
    deadline = time.time() + 30
    while time.time() < deadline and not fake.requests:
        time.sleep(0.5)
    pg.page.reload(wait_until="domcontentloaded")
    pg.page.wait_for_function("typeof acct !== 'undefined' && !!acct.user", timeout=10000)
    pg.page.evaluate("window.DA_THREAD_POLL_MS = 1000")
    open_history(pg)
    pend_row = pg.page.locator('.modal .hist-row:has(.hist-mail[data-mail="running"]), '
                               '.modal .hist-row:has(.hist-mail[data-mail="pending"])')
    check("My questions lists the emailed question in the same conversation, on its way",
          pg.page.locator(".modal .hist-conv").count() == 1 and pend_row.count() == 1)
    pend_row.first.click()
    pg.page.wait_for_selector("#thread .past-thread .mail-pending", timeout=30000)
    pg.page.wait_for_timeout(300)
    note = pg.page.inner_text("#thread .past-thread .mail-pending")
    check("the thread shows 'Writing your detailed answer — it'll also arrive by email within 30 minutes'",
          "Writing your detailed answer" in note and "30 minutes" in note, note)
    check("...after the 4 instant answers, in time order",
          thread_questions(pg)[-1] == "What does my chart say about my career this year?"
          and len(thread_questions(pg)) == 5, str(thread_questions(pg)))
    pg.page.locator("#thread .past-thread .mail-pending").scroll_into_view_if_needed()
    shot(pg, "3_emailed_writing_390")
    fake.gate.set()
    try:
        pg.page.wait_for_selector("#thread .past-thread .mail-tag", timeout=60000)
    except Exception:
        pass
    pg.page.wait_for_timeout(400)
    tag = pg.page.locator("#thread .past-thread .mail-tag")
    check("polled: once written, the answer appears in place, tagged 'Sent to your email'",
          tag.count() == 1 and "Sent to your email" in tag.inner_text()
          and pg.page.locator("#thread .past-thread .mail-pending").count() == 0)
    bub = pg.page.locator("#thread .past-thread .msg.bot").last
    check("...with the answer's text and Copy / Share",
          "steady rise through effort" in bub.inner_text() and bub.locator(".msg-actions").count() == 1)
    check("the queued card's poll stopped (nothing pending)",
          pg.page.evaluate("!window.__daThreadPolling"))
    bub.scroll_into_view_if_needed()
    shot(pg, "4_emailed_done_390")

    print("\n[390px] a chart that was not saved: read-only")
    pg.page.evaluate("async (b) => { await castChart(b); showStage('stage-chat'); }", OTHER_BIRTH)
    pg.page.wait_for_function("state.currentBirthId === null", timeout=5000)
    pg.page.evaluate("state.provider = 'off'")
    admin_post(pg, f"/api/admin/users/{uid}/credits", {"delta": 1, "note": "e2e"})
    ask(pg, "Will I travel abroad?")
    pg.page.reload(wait_until="domcontentloaded")
    pg.page.wait_for_function("typeof acct !== 'undefined' && !!acct.user", timeout=10000)
    open_history(pg)
    check("My questions: two conversations now", pg.page.locator(".modal .hist-conv").count() == 2)
    pg.page.locator(".modal .hist-conv").first.locator(".hist-conv-head").click()
    pg.page.wait_for_selector(".modal .thread-view .msg.user", timeout=10000)
    pg.page.wait_for_timeout(300)
    view = pg.page.inner_text(".modal .thread-view")
    check("its conversation opens read-only: the question, its answer, the note",
          "Will I travel abroad?" in view and pg.page.locator(".modal .thread-view .msg.bot .msg-actions").count() == 1
          and pg.page.locator(".modal .thread-readonly-note").count() == 1)
    check("390px: no sideways scroll (read-only view)", no_overflow(pg))
    shot(pg, "5_readonly_390")
    errors = [e for e in pg.console_errors if "402" not in e]
    check("no console errors", not errors, "; ".join(errors[:3]))
    check("no CSP violations", not pg.csp_violations())
    ctx.close()

    print("\n[320x568] the thread on the narrowest phone")
    ctx = ctx_for(browser, 320, 568)
    pg = Page(ctx.new_page(), base)
    pg.sign_in(email=EMAIL, name="History A")
    pg.open_home()
    pg.page.wait_for_function("typeof acct !== 'undefined' && !!acct.user", timeout=10000)
    open_history(pg)
    check("320px: My questions has no sideways scroll", no_overflow(pg))
    shot(pg, "6_my_questions_320")
    pg.page.locator('.modal .hist-conv:has(.hist-conv-head[data-thread^="c"]) .hist-conv-head').click()
    pg.page.wait_for_function("document.querySelectorAll('#thread .past-thread .msg.user').length >= 5",
                              timeout=30000)
    pg.page.wait_for_timeout(500)
    check("320px: the whole thread is there (5 questions)", len(thread_questions(pg)) == 5)
    check("320px: the question box is on screen", q_box_visible(pg), str(pg.rect("#q")))
    check("320px: no sideways scroll", no_overflow(pg))
    shot(pg, "7_thread_320")
    ctx.close()

    print("\n[another account] sees nothing")
    ctx = ctx_for(browser, 390, 844)
    pg = Page(ctx.new_page(), base)
    pg.sign_in(email="history-b@example.com", name="History B")
    h = pg.page.context.request.get(f"{base}/api/history").json()
    check("another account: no questions, no conversations", h["questions"] == [] and h["threads"] == [])
    r = pg.page.context.request.get(f"{base}/api/history/thread/c{birth_id}")
    check("another account: A's conversation key is not found (404)", r.status == 404, str(r.status))
    pg.open_home()
    pg.page.wait_for_function("typeof acct !== 'undefined' && !!acct.user", timeout=10000)
    open_history(pg)
    check("another account: My questions is empty", pg.page.locator(".modal .hist-row").count() == 0)
    ctx.close()
    anon = browser.new_context()
    r = anon.request.get(f"{base}/api/history/thread/c{birth_id}")
    check("signed out: 401", r.status == 401, str(r.status))
    anon.close()


def main() -> int:
    fake = FakeOllama().start()
    env = {
        "ASTRO_SMTP_HOST": "console", "ASTRO_EMAIL_ANSWER_OLLAMA_URL": fake.url,
        "ASTRO_EMAIL_ANSWER_WRITER": "ollama", "ASTRO_EMAIL_ANSWER_POLL_S": "1",
        "ANTHROPIC_API_KEY": "fake-key-e2e",
        "PYTHONPATH": os.pathsep.join(p for p in (str(FAKE_ANTHROPIC), os.environ.get("PYTHONPATH", "")) if p),
    }
    try:
        with server(env) as base, sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                flow(browser, base, fake)
            finally:
                browser.close()
    finally:
        fake.gate.set()
        fake.stop()
    return check.finish("Conversation history (e2e)")


if __name__ == "__main__":
    sys.exit(main())
