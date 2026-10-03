"""The daily channel post and its two senders (DIVASTRO-113).

  * app.daily_message — the Hindi/English Panchang post: festivals and their
    timings on known days (Jitiya + Kalashtami 3 Oct 2026, Diwali Lakshmi puja
    17:54 on 8 Nov 2026), an ordinary day, UTM links, Telegram's 4096 limit
    and pure Devanagari in Hindi — checked for every day of 2026.
  * app.telegram_daily — Bot API mocked (httpx.post patched): never prints the
    token, posts once a day, exits non-zero on failure.
  * app.whatsapp_pack — console mail transport (ASTRO_SMTP_HOST=console),
    with the PNG card attached.

Nothing is sent anywhere. A throwaway SQLite database and state directory.

    ~/.venvs/divineastro/bin/python -u -m tests.test_daily_message
"""

from __future__ import annotations

import contextlib
import datetime as dt
import html
import io
import os
import re
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

_tmp = tempfile.mkdtemp(prefix="astro_daily_msg_")
os.environ["ASTRO_DATABASE_URL"] = f"sqlite:///{Path(_tmp).as_posix()}/t.db"
os.environ["ASTRO_DAILY_STATE_DIR"] = str(Path(_tmp) / "state")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import httpx  # noqa: E402
from PIL import Image  # noqa: E402

from app import daily_message as D  # noqa: E402
from app import daily_state, mail, social_card, telegram_daily, whatsapp_pack  # noqa: E402
from app.astro import festivals  # noqa: E402

failures: list[str] = []
URL = re.compile(r"https://\S+")
LATIN = re.compile(r"[A-Za-z]")

JITIYA = dt.date(2026, 10, 3)
DIWALI = dt.date(2026, 11, 8)


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail and not ok else ""))
    if not ok:
        failures.append(label)


def ordinary_day() -> dt.date:
    d = dt.date(2026, 10, 1)
    while festivals.on(d):
        d += dt.timedelta(days=1)
    return d


# --------------------------------------------------------------------------

def test_content() -> None:
    print("\n1. Message content")
    hi = D.channel_message(JITIYA, lang="hi", channel="whatsapp")
    en = D.channel_message(JITIYA, lang="en", channel="whatsapp")
    check("3 Oct (hi): Jivitputrika", "जीवित्पुत्रिका व्रत (जितिया)" in hi, hi)
    check("3 Oct (hi): Kalashtami", "कालाष्टमी" in hi, hi)
    check("3 Oct (en): Jivitputrika + Kalashtami", "Jivitputrika" in en and "Kalashtami" in en)
    check("3 Oct (hi): date + vaar", "3 अक्टूबर 2026, शनिवार" in hi)
    check("3 Oct (hi): tithi with its end time", "तिथि: कृष्ण सप्तमी सुबह 8:00 तक, फिर अष्टमी" in hi)
    check("3 Oct (hi): nakshatra", "नक्षत्र: आर्द्रा" in hi)
    check("3 Oct (hi): sunrise/sunset", "सूर्योदय: सुबह 6:14" in hi and "सूर्यास्त: शाम 6:05" in hi)
    check("3 Oct (hi): Rahu Kaal", "राहु काल: सुबह 9:12 – सुबह 10:41" in hi)
    check("3 Oct (hi): Abhijit", "अभिजित मुहूर्त: सुबह 11:46 – दोपहर 12:33" in hi)
    check("3 Oct (hi): Moon sign for the rashifal line", "चंद्रमा मिथुन राशि में" in hi)
    check("3 Oct (en): Rahu Kaal in AM/PM", "Rahu Kaal: 9:12 AM – 10:41 AM" in en)
    check("vrat without a puja window shows its tithi span",
          "Krishna Ashtami: 8:00 AM to 5:52 AM (4 Oct)" in en, en)

    dhi = D.channel_message(DIWALI, lang="hi", channel="whatsapp")
    den = D.channel_message(DIWALI, lang="en", channel="whatsapp")
    check("8 Nov (hi): Diwali Lakshmi puja 17:54",
          "दीपावली (लक्ष्मी पूजा)" in dhi and "लक्ष्मी पूजा मुहूर्त: शाम 5:54 – शाम 7:50" in dhi, dhi)
    check("8 Nov (en): Lakshmi puja muhurat 5:54 PM",
          "Diwali (Lakshmi Puja)" in den and "Lakshmi puja muhurat: 5:54 PM – 7:50 PM" in den, den)

    day = ordinary_day()
    ohi = D.channel_message(day, lang="hi", channel="whatsapp")
    oen = D.channel_message(day, lang="en", channel="whatsapp")
    check(f"ordinary day ({day}): no festival section",
          "व्रत-त्योहार*" not in ohi and "festivals today" not in oen, ohi)
    check("ordinary day: still has the panchang and links",
          "राहु काल" in ohi and "/hi/panchang?" in ohi and "Rahu Kaal" in oen)

    b = D.build(JITIYA, lang="hi", channel="telegram")
    check("build() -> {title, body, url}", set(b) == {"title", "body", "url"}
          and "आज का पंचांग" in b["title"] and b["url"].startswith("https://divineastro.org/hi/"))


def test_promos() -> None:
    print("\n2b. Promo footer")
    from app import billing
    seen = set()
    for i in range(12):
        day = JITIYA + dt.timedelta(days=i)
        for lang in ("hi", "en"):
            lines = D.promo_lines(day, lang, "whatsapp")
            check(f"{day} {lang}: promo block present", len(lines) >= 4 and lines[2], str(lines)[:120])
            seen.add(lines[2])
    check("promos rotate (6 different texts in 6 days per language)", len(seen) >= 12, str(len(seen)))
    texts = " ".join(t for t, _ in D._promos("en"))
    check("prices come from billing (50 for ₹351, ₹111 kundali)",
          f"₹{billing.PRODUCTS['q50'].rupees}" in texts and f"₹{billing.PRODUCTS['k3'].rupees}" in texts, texts[:200])
    check(f"free-question count from billing ({billing.FREE_QUESTIONS})",
          f"first {billing.FREE_QUESTIONS} questions" in texts)


def test_links() -> None:
    print("\n2. UTM links")
    for channel in ("telegram", "whatsapp"):
        for lang, prefix in (("hi", "/hi"), ("en", "")):
            text = html.unescape(D.channel_message(JITIYA, lang=lang, channel=channel))
            urls = URL.findall(text)
            daily = [u for u in urls if "utm_campaign=daily-" in u]
            promo = [u for u in urls if "utm_campaign=promo-" in u]
            paths = sorted(u.split("?")[0].replace("https://divineastro.org", "") for u in daily)
            want = sorted(f"{prefix}/{p}" for p in ("panchang", "rashifal", "vrat-tyohar"))
            check(f"{channel}/{lang}: links to panchang, vrat-tyohar, rashifal", paths == want,
                  str(paths))
            tag = (f"utm_source={channel}&utm_medium=channel&utm_campaign=daily-2026-10-03")
            check(f"{channel}/{lang}: every daily link tagged", all(u.endswith("?" + tag) for u in daily),
                  str(daily))
            ptag = f"utm_source={channel}&utm_medium=channel&utm_campaign=promo-2026-10-03"
            check(f"{channel}/{lang}: exactly one promo link, tagged promo-<date>",
                  len(promo) == 1 and promo[0].endswith(ptag) and len(urls) == 4, str(urls))
    tg = D.channel_message(JITIYA, lang="hi", channel="telegram")
    check("telegram: & escaped for HTML parse mode", "&amp;utm_medium" in tg and
          "&utm_medium" not in tg.replace("&amp;", ""))


def test_markup() -> None:
    print("\n3. Markup per channel")
    tg = D.channel_message(DIWALI, lang="hi", channel="telegram")
    wa = D.channel_message(DIWALI, lang="hi", channel="whatsapp")
    plain = D.channel_message(DIWALI, lang="hi", channel="plain")
    tags = re.findall(r"</?[a-z]+>", tg)
    check("telegram: only <b> tags, balanced", set(tags) <= {"<b>", "</b>"}
          and tags.count("<b>") == tags.count("</b>") > 0, str(tags))
    check("whatsapp: *bold*, no HTML", "*🪔 आज का पंचांग*" in wa and "<b>" not in wa)
    check("whatsapp: no other markdown (_ ~ ` #)", not re.search(r"[_~`#]", URL.sub("", wa)))
    check("plain: no markup", "*" not in plain and "<b>" not in plain and "\x01" not in plain)
    try:
        D.channel_message(DIWALI, channel="sms")
        check("unknown channel rejected", False)
    except ValueError:
        check("unknown channel rejected", True)


def test_every_day_2026() -> None:
    print("\n4. Every day of 2026: Telegram limit, pure Hindi")
    longest, latin_days = 0, []
    d = dt.date(2026, 1, 1)
    while d.year == 2026:
        hi = D.channel_message(d, lang="hi", channel="telegram")
        en = D.channel_message(d, lang="en", channel="telegram")
        longest = max(longest, len(hi), len(en))
        words = URL.sub("", html.unescape(re.sub(r"</?b>", "", hi)))
        if LATIN.search(words):
            latin_days.append((d.isoformat(), re.findall(r"\S*[A-Za-z]\S*", words)[:5]))
        d += dt.timedelta(days=1)
    check(f"longest message {longest} chars < {D.TELEGRAM_LIMIT}", longest < D.TELEGRAM_LIMIT)
    check("Hindi has no Latin letters outside links (no stray English terms)", not latin_days,
          str(latin_days[:5]))


# --------------------------------------------------------------------------

TOKEN = "123456789:AAFakeTokenNeverPrinted_xyz"
CHAT = "@divineastro_test"


def _ok(mid: int = 42) -> MagicMock:
    r = MagicMock(status_code=200)
    r.json.return_value = {"ok": True, "result": {"message_id": mid}}
    return r


def _run(mod, argv: list[str]) -> tuple[int, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = mod.main(argv)
    return code, out.getvalue() + err.getvalue()


def test_telegram() -> None:
    print("\n5. Telegram sender (Bot API mocked)")
    env = {"ASTRO_TELEGRAM_BOT_TOKEN": TOKEN, "ASTRO_TELEGRAM_CHAT_ID": CHAT}

    with patch.dict(os.environ, {"ASTRO_TELEGRAM_BOT_TOKEN": "", "ASTRO_TELEGRAM_CHAT_ID": ""}), \
            patch.object(telegram_daily.httpx, "post") as post:
        code, out = _run(telegram_daily, ["--date", "2026-10-03", "--dry-run"])
        check("dry-run: exit 0 without a token, prints the message, sends nothing",
              code == 0 and "जीवित्पुत्रिका" in out and not post.called, out[:200])
        code, out = _run(telegram_daily, ["--date", "2026-10-03"])
        check("unconfigured: exit 2 with a clear message",
              code == 2 and "ASTRO_TELEGRAM_BOT_TOKEN" in out, out)

    with patch.dict(os.environ, env), patch.object(telegram_daily.httpx, "post",
                                                   return_value=_ok()) as post:
        code, out = _run(telegram_daily, ["--date", "2026-10-03"])
        check("posts: exit 0", code == 0, out)
        check("posts: one sendMessage", post.call_count == 1, str(post.call_args_list))
        url = post.call_args.args[0]
        payload = post.call_args.kwargs.get("json") or {}
        check("posts: sendMessage to the configured chat in HTML mode",
              url.endswith("/sendMessage") and payload.get("chat_id") == CHAT
              and payload.get("parse_mode") == "HTML"
              and "जीवित्पुत्रिका" in payload.get("text", ""), str(payload)[:200])
        check("posts: token never printed", TOKEN not in out and "AAFake" not in out, out)
        check("state recorded", daily_state.sent("telegram", JITIYA).get("hi") == 42,
              str(daily_state.load("telegram")))

        post.reset_mock()
        code, out = _run(telegram_daily, ["--date", "2026-10-03"])
        check("idempotent: second run exit 0, nothing sent", code == 0 and not post.called, out)

        code, out = _run(telegram_daily, ["--date", "2026-10-03", "--langs", "hi,en"])
        check("adding English later sends only English", code == 0 and post.call_count == 1
              and "Today's Panchang" in post.call_args.kwargs["json"]["text"], out)

        post.reset_mock()
        code, out = _run(telegram_daily, ["--date", "2026-10-03", "--force"])
        check("--force sends again", code == 0 and post.call_count == 1, out)

        post.reset_mock()
        code, out = _run(telegram_daily, ["--date", "2026-11-08", "--with-card"])
        first = post.call_args_list[0] if post.call_args_list else None
        check("--with-card: sendPhoto with a PNG, then the message",
              code == 0 and post.call_count == 2 and first is not None
              and first.args[0].endswith("/sendPhoto")
              and first.kwargs["files"]["photo"][1][:8] == b"\x89PNG\r\n\x1a\n", out)

    bad = MagicMock(status_code=401)
    bad.json.return_value = {"ok": False, "error_code": 401, "description": "Unauthorized"}
    with patch.dict(os.environ, env), patch.object(telegram_daily.httpx, "post", return_value=bad):
        code, out = _run(telegram_daily, ["--date", "2026-10-05"])
        check("API error: exit 1, Telegram's reason shown",
              code == 1 and "Unauthorized" in out and "FAILED" in out, out)
        check("API error: token never printed", TOKEN not in out, out)
        check("API error: not recorded as sent", not daily_state.sent("telegram", dt.date(2026, 10, 5)))

    boom = httpx.ConnectError(f"cannot reach https://api.telegram.org/bot{TOKEN}/sendMessage")
    with patch.dict(os.environ, env), patch.object(telegram_daily.httpx, "post", side_effect=boom):
        code, out = _run(telegram_daily, ["--date", "2026-10-05"])
        check("network error: exit 1", code == 1, out)
        check("network error: token redacted from the exception text",
              TOKEN not in out and "<token>" in out, out)

    with patch.dict(os.environ, env):
        code, out = _run(telegram_daily, ["--date", "2026-10-05", "--langs", "fr"])
        check("bad --langs: exit 2", code == 2, out)


def test_whatsapp_pack() -> None:
    print("\n6. WhatsApp pack email (console mail transport)")
    env = {"ASTRO_SMTP_HOST": "console", "ASTRO_COOKIE_SECURE": "0",
           "ASTRO_DAILY_PACK_TO": "owner@example.com"}
    with patch.dict(os.environ, env):
        mail.OUTBOX.clear()
        code, out = _run(whatsapp_pack, ["--date", "2026-10-03", "--dry-run"])
        check("dry-run: exit 0, nothing mailed", code == 0 and not mail.OUTBOX
              and "WhatsApp post for 3 October 2026" in out, out[:300])

        code, out = _run(whatsapp_pack, ["--date", "2026-10-03"])
        check("sends: exit 0, one message", code == 0 and len(mail.OUTBOX) == 1, out)
        if mail.OUTBOX:
            sent = mail.OUTBOX[-1]
            to, subject, body, _html = sent
            check("to the pack recipient", to == ["owner@example.com"], str(to))
            check("subject 'WhatsApp post for <date>'", subject == "WhatsApp post for 3 October 2026",
                  subject)
            check("body: Hindi and English, WhatsApp *bold*, whatsapp UTM",
                  "जीवित्पुत्रिका" in body and "Jivitputrika" in body and "*कालाष्टमी*" in body
                  and "utm_source=whatsapp&utm_medium=channel" in body, body[:300])
            att = sent.attachments
            check("one PNG attachment", len(att) == 1 and att[0][1] == "image/png"
                  and att[0][0] == "divineastro-panchang-2026-10-03.png", str([a[:2] for a in att]))
            if att:
                img = Image.open(io.BytesIO(att[0][2]))
                check("attachment is a 1080x1080 PNG", img.format == "PNG" and img.size == (1080, 1080))

        code, out = _run(whatsapp_pack, ["--date", "2026-10-03"])
        check("idempotent: second run sends nothing", code == 0 and len(mail.OUTBOX) == 1, out)
        code, out = _run(whatsapp_pack, ["--date", "2026-10-03", "--force"])
        check("--force sends again", code == 0 and len(mail.OUTBOX) == 2, out)

    with patch.dict(os.environ, {"ASTRO_SMTP_HOST": "", "ASTRO_DAILY_PACK_TO": "o@example.com"}):
        code, out = _run(whatsapp_pack, ["--date", "2026-10-04"])
        check("mail unconfigured: exit 1", code == 1 and "ASTRO_SMTP_HOST" in out, out)
    with patch.dict(os.environ, {"ASTRO_SMTP_HOST": "console", "ASTRO_DAILY_PACK_TO": "",
                                 "ASTRO_SUPPORT_EMAIL": ""}):
        code, out = _run(whatsapp_pack, ["--date", "2026-10-04"])
        check("no recipient: exit 2", code == 2, out)
    with patch.dict(os.environ, {"ASTRO_DAILY_PACK_TO": "", "ASTRO_SUPPORT_EMAIL": "s@x.org"}):
        check("falls back to ASTRO_SUPPORT_EMAIL", whatsapp_pack.recipients() == ["s@x.org"])


def test_card() -> None:
    print("\n7. Image card")
    eyebrow, head, sub = D.card_text(JITIYA)
    check("card text is English (no Devanagari)",
          not re.search(r"[ऀ-ॿ]", eyebrow + head + sub), f"{eyebrow} | {head} | {sub}")
    check("card names today's festivals", "Jivitputrika" in head and "Kalashtami" in head, head)
    check("card headline under ~55 chars", len(head) <= 55, head)
    check("card Rahu Kaal compact", "Rahu Kaal 9:12–10:41 AM" in sub, sub)
    try:
        social_card.make_card("x", "जितिया", "y", io.BytesIO())
        check("social_card refuses Devanagari", False)
    except ValueError:
        check("social_card refuses Devanagari", True)


def main() -> int:
    print("Daily channel message, Telegram sender, WhatsApp pack (DIVASTRO-113)")
    test_content()
    test_promos()
    test_links()
    test_markup()
    test_telegram()
    test_whatsapp_pack()
    test_card()
    test_every_day_2026()
    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("daily message — all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
