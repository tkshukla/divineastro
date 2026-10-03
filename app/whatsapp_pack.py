"""Email the owner today's ready-to-paste WhatsApp Channel post (DIVASTRO-113).

    python -m app.whatsapp_pack [--date YYYY-MM-DD] [--to a@b.c] [--force]
                                [--dry-run [--card-out card.png]]

Meta does not allow automated posting to a WhatsApp Channel, so this is the
half that can be automated: at 06:00 IST (host cron, see
deploy/daily_channels.md) it mails the owner the Hindi and English messages,
formatted with WhatsApp's *bold*, and the English-only image card as a PNG
attachment. The owner opens the mail on the phone, saves the image, and posts.

Recipients: --to, else ASTRO_DAILY_PACK_TO, else ASTRO_SUPPORT_EMAIL (comma
or space separated). Sent through app/mail.py (Brevo SMTP in production).

Once a day, recorded in /srv/data/daily_channels/whatsapp_pack.json
(app/daily_state.py); --force sends again.

Exit codes: 0 sent (or already sent today), 1 mail failed / not configured,
2 bad arguments or no recipient.
"""

from __future__ import annotations

import argparse
import datetime as dt
import io
import os
import sys

from . import daily_message, daily_state, mail, social_card

JOB = "whatsapp_pack"


def recipients(explicit: str | None = None) -> list[str]:
    raw = (explicit or os.environ.get("ASTRO_DAILY_PACK_TO")
           or os.environ.get("ASTRO_SUPPORT_EMAIL") or "")
    return [a for a in raw.replace(",", " ").split() if "@" in a]


def subject(day: dt.date) -> str:
    return f"WhatsApp post for {day.day} {day:%B %Y}"


def card_name(day: dt.date) -> str:
    return f"divineastro-panchang-{day.isoformat()}.png"


def card_png(day: dt.date) -> bytes:
    buf = io.BytesIO()
    social_card.make_card(*daily_message.card_text(day), buf)
    return buf.getvalue()


def body(day: dt.date) -> str:
    hi = daily_message.channel_message(day, lang="hi", channel="whatsapp")
    en = daily_message.channel_message(day, lang="en", channel="whatsapp")
    return "\n".join([
        f"Today's WhatsApp Channel post ({day.isoformat()}).",
        "",
        "How to post: save the attached image, open the Divine Astro channel in",
        "WhatsApp, attach the image, and paste the Hindi text below as its caption",
        "(or as a second message). Post the English one too if you like.",
        "Copy only the text between the lines; *stars* make bold in WhatsApp.",
        "",
        "==================== हिंदी ====================",
        hi,
        "==================== English ====================",
        en,
        "=================================================",
        "",
        f"Image: {card_name(day)} (attached, English only).",
        "Links are tagged utm_source=whatsapp, so visits show in /admin Traffic.",
    ])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m app.whatsapp_pack",
                                 description="Email today's WhatsApp Channel post to the owner.")
    ap.add_argument("--date", help="YYYY-MM-DD (default: today in IST)")
    ap.add_argument("--to", help="recipient(s); default $ASTRO_DAILY_PACK_TO or "
                                 "$ASTRO_SUPPORT_EMAIL")
    ap.add_argument("--force", action="store_true", help="send even if already sent today")
    ap.add_argument("--dry-run", action="store_true", help="print the email, send nothing")
    ap.add_argument("--card-out", help="with --dry-run: also save the card PNG here")
    args = ap.parse_args(argv)

    try:
        day = dt.date.fromisoformat(args.date) if args.date else daily_state.today_ist()
    except ValueError as exc:
        print(f"whatsapp_pack: {exc}", file=sys.stderr)
        return 2

    text = body(day)
    png = card_png(day)
    to = recipients(args.to)

    if args.dry_run:
        print(f"To: {', '.join(to) or '(no recipient configured)'}")
        print(f"Subject: {subject(day)}")
        print(f"Attachment: {card_name(day)} ({len(png)} bytes)")
        print()
        print(text)
        if args.card_out:
            with open(args.card_out, "wb") as f:
                f.write(png)
            print(f"\ncard written to {args.card_out}")
        return 0

    if not to:
        print("whatsapp_pack: no recipient — set ASTRO_DAILY_PACK_TO (or ASTRO_SUPPORT_EMAIL)",
              file=sys.stderr)
        return 2
    if not args.force and daily_state.sent(JOB, day):
        print(f"whatsapp_pack: already sent for {day}; nothing to do")
        return 0
    if not mail.configured():
        print("whatsapp_pack: mail is not configured (ASTRO_SMTP_HOST)", file=sys.stderr)
        return 1
    if not mail.send(to, subject(day), text, attachments=[(card_name(day), "image/png", png)]):
        print(f"whatsapp_pack: FAILED to send for {day} (see the mail.send warning above)",
              file=sys.stderr)
        return 1
    try:
        daily_state.mark(JOB, day, "email")
    except OSError as exc:
        print(f"whatsapp_pack: sent, but could not record it: {exc}", file=sys.stderr)
    print(f"whatsapp_pack: sent {subject(day)!r} to {', '.join(to)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
