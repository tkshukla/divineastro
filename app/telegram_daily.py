"""Post the daily Panchang to the Telegram channel (DIVASTRO-113).

    python -m app.telegram_daily [--date YYYY-MM-DD] [--langs hi,en]
                                 [--with-card] [--force] [--dry-run]

Run from host cron at 06:00 IST inside the app container (see
deploy/daily_channels.md). Fully automatic: the Bot API lets a bot that is an
admin of a channel post to it.

Configuration (environment, i.e. the app's .env):
  ASTRO_TELEGRAM_BOT_TOKEN  the bot's token from @BotFather. Secret: never
                            printed — every error message is passed through
                            _redact() first, because httpx puts the request
                            URL (which contains the token) in its exceptions.
  ASTRO_TELEGRAM_CHAT_ID    the channel: "@divineastro_channel" for a public
                            channel, or its numeric id ("-100…").
  ASTRO_TELEGRAM_LANGS      which posts, in order; default "hi" (Hindi only).
                            "hi,en" also posts the English message.

Once a day: each part (the card, each language) is recorded in
/srv/data/daily_channels/telegram.json (app/daily_state.py) as soon as it is
sent, so a re-run posts only what is missing. --force ignores that.

Exit codes: 0 posted (or already posted today), 1 a send failed, 2 not
configured / bad arguments. --dry-run prints the messages and needs no token.
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import sys

import httpx

from . import daily_message, daily_state

JOB = "telegram"
API = "https://api.telegram.org"
TIMEOUT = 30.0


class TelegramError(RuntimeError):
    pass


def _redact(text: str, token: str) -> str:
    return text.replace(token, "<token>") if token else text


def _call(token: str, method: str, *, data: dict, files: dict | None = None) -> dict:
    """One Bot API call; returns `result` or raises TelegramError (token-free)."""
    url = f"{API}/bot{token}/{method}"
    try:
        if files:
            r = httpx.post(url, data=data, files=files, timeout=TIMEOUT)
        else:
            r = httpx.post(url, json=data, timeout=TIMEOUT)
    except httpx.HTTPError as exc:
        raise TelegramError(_redact(f"{method}: {type(exc).__name__}: {exc}", token)) from None
    try:
        body = r.json()
    except ValueError:
        raise TelegramError(f"{method}: HTTP {r.status_code}, not JSON") from None
    if not body.get("ok"):
        raise TelegramError(_redact(
            f"{method}: HTTP {r.status_code} error {body.get('error_code')}: "
            f"{body.get('description')}", token))
    return body.get("result") or {}


def send_message(token: str, chat_id: str, text: str) -> int | None:
    result = _call(token, "sendMessage", data={
        "chat_id": chat_id, "text": text, "parse_mode": "HTML",
        "link_preview_options": {"is_disabled": True},
    })
    return result.get("message_id")


def send_photo(token: str, chat_id: str, png: bytes, caption: str) -> int | None:
    result = _call(token, "sendPhoto",
                   data={"chat_id": chat_id, "caption": caption, "parse_mode": "HTML"},
                   files={"photo": ("panchang.png", png, "image/png")})
    return result.get("message_id")


card_png = daily_message.card_png


def _langs(raw: str) -> list[str]:
    langs = [x.strip().lower() for x in raw.replace(" ", ",").split(",") if x.strip()]
    bad = [x for x in langs if x not in ("hi", "en")]
    if bad or not langs:
        raise ValueError(f"languages must be hi and/or en, got {raw!r}")
    return langs


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m app.telegram_daily",
                                 description="Post today's Panchang to the Telegram channel.")
    ap.add_argument("--date", help="YYYY-MM-DD (default: today in IST)")
    ap.add_argument("--langs", default=os.environ.get("ASTRO_TELEGRAM_LANGS") or "hi",
                    help='"hi", "en" or "hi,en" (default: $ASTRO_TELEGRAM_LANGS or hi)')
    ap.add_argument("--with-card", action="store_true",
                    help="also post the English image card first")
    ap.add_argument("--force", action="store_true", help="post even if already posted today")
    ap.add_argument("--dry-run", action="store_true", help="print the messages, send nothing")
    args = ap.parse_args(argv)

    try:
        day = dt.date.fromisoformat(args.date) if args.date else daily_state.today_ist()
        langs = _langs(args.langs)
    except ValueError as exc:
        print(f"telegram_daily: {exc}", file=sys.stderr)
        return 2

    messages = {lang: daily_message.channel_message(day, lang=lang, channel="telegram")
                for lang in langs}
    for lang, text in messages.items():
        if len(text) > daily_message.TELEGRAM_LIMIT:
            print(f"telegram_daily: {lang} message is {len(text)} chars, over Telegram's "
                  f"{daily_message.TELEGRAM_LIMIT}", file=sys.stderr)
            return 1

    if args.dry_run:
        for lang, text in messages.items():
            print(f"----- {lang} ({len(text)} chars, Telegram HTML) -----")
            print(text)
        if args.with_card:
            print("----- card -----")
            print(" | ".join(daily_message.card_text(day)))
        return 0

    token = os.environ.get("ASTRO_TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("ASTRO_TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        print("telegram_daily: ASTRO_TELEGRAM_BOT_TOKEN and ASTRO_TELEGRAM_CHAT_ID must both "
              "be set (see deploy/daily_channels.md)", file=sys.stderr)
        return 2

    done = {} if args.force else daily_state.sent(JOB, day)
    parts = (["card"] if args.with_card else []) + langs
    todo = [p for p in parts if p not in done]
    if not todo:
        print(f"telegram_daily: already posted for {day} ({', '.join(parts)}); nothing to do")
        return 0

    try:
        for part in todo:
            if part == "card":
                caption = "🪔 <b>आज का पंचांग</b> · " + daily_message._date_line(day, "hi")
                mid = send_photo(token, chat_id, card_png(day), caption)
            else:
                mid = send_message(token, chat_id, messages[part])
            daily_state.mark(JOB, day, part, mid or True)
            print(f"telegram_daily: posted {part} for {day} (message {mid})")
    except TelegramError as exc:
        print(f"telegram_daily: FAILED for {day}: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:                            # e.g. the state dir is not writable
        print(f"telegram_daily: FAILED for {day}: "
              f"{_redact(f'{type(exc).__name__}: {exc}', token)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
