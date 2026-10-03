"""Outbound mail over SMTP (Brevo in production).

Two kinds of caller:

* Admin "look at this" pings — `submit_utr()` in `api_account.py` when a
  customer claims a UPI payment, and new feedback in `api_feedback.py`.
* Sign-in codes for email sign-in (`app/email_auth.py`, DIVASTRO-104) — the
  one customer-facing use, which is why `send()` can attach an HTML part.

Deliberately best-effort. `send()` never raises: a broken or unconfigured
mailbox must never turn into a 500 on the endpoint that called it. Leave
`ASTRO_SMTP_HOST` unset and everything still works exactly as before this
module existed — admins just aren't pinged, and email sign-in is not offered
(`configured()` is what /api/auth/providers asks).

`ASTRO_SMTP_HOST=console` is a dev/test transport: nothing is sent, each
message is appended to `OUTBOX` (so an in-process test can read a code back)
and logged in full (so a dev, or an e2e test reading the server log, can).
Because that log would contain every sign-in code, it is refused when
`ASTRO_COOKIE_SECURE=1` — the same production test phone_auth's console SMS
sender and the dev sign-in use — and mail is then simply "not configured".
Attachments (DIVASTRO-113: the daily WhatsApp pack's image card) are kept on
the OUTBOX entry's `.attachments`; only their names and sizes are logged.
"""

from __future__ import annotations

import logging
import os
import smtplib
from email.message import EmailMessage

log = logging.getLogger(__name__)

# (filename, MIME type such as "image/png", bytes)
Attachment = tuple[str, str, bytes]


class Sent(tuple):
    """One console-transport message: unpacks as (to, subject, body, html), the
    shape callers have always read, with `.attachments` alongside."""

    attachments: list[Attachment]

    def __new__(cls, to: list[str], subject: str, body: str, html: str | None,
                attachments: list[Attachment] | None = None) -> "Sent":
        self = super().__new__(cls, (to, subject, body, html))
        self.attachments = list(attachments or [])
        return self


# Console transport only.
OUTBOX: list[Sent] = []


def _console() -> bool:
    return os.environ.get("ASTRO_SMTP_HOST", "").strip().lower() == "console"


def _production() -> bool:
    return os.environ.get("ASTRO_COOKIE_SECURE", "0") == "1"


def configured() -> bool:
    """Whether send() can actually deliver (or, in dev, pretend to)."""
    if not os.environ.get("ASTRO_SMTP_HOST"):
        return False
    if _console() and _production():
        log.error("ASTRO_SMTP_HOST=console is refused in production "
                  "(ASTRO_COOKIE_SECURE=1): it would log every sign-in code. Mail is off.")
        return False
    return True


def send(to: list[str], subject: str, body: str, html: str | None = None,
         attachments: list[Attachment] | None = None) -> bool:
    """Best-effort send. Returns whether it actually went out.

    `body` is the plain-text part every client can show; `html`, if given, is
    attached as the alternative that most clients prefer. `attachments` are
    (filename, "type/subtype", bytes) files added to the message.
    """
    if not to:
        log.warning("mail.send: no recipients (ASTRO_ADMIN_EMAILS empty?), dropping %r", subject)
        return False
    if not configured():
        log.info("mail.send: ASTRO_SMTP_HOST not set, skipping %r", subject)
        return False

    if _console():
        OUTBOX.append(Sent(list(to), subject, body, html, attachments))
        files = "".join(f"\n[attachment {name} {mime} {len(data)} bytes]"
                        for name, mime, data in attachments or [])
        log.warning("[console mail — dev only] to %s: %s\n%s%s", ", ".join(to), subject, body, files)
        return True

    host = os.environ["ASTRO_SMTP_HOST"]
    port = int(os.environ.get("ASTRO_SMTP_PORT", "587"))
    user = os.environ.get("ASTRO_SMTP_USER", "")
    password = os.environ.get("ASTRO_SMTP_PASS", "")
    sender = os.environ.get("ASTRO_MAIL_FROM", user or "no-reply@divineastro.org")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(to)
    msg.set_content(body)
    if html:
        msg.add_alternative(html, subtype="html")
    for name, mime, data in attachments or []:
        maintype, _, subtype = mime.partition("/")
        msg.add_attachment(data, maintype=maintype, subtype=subtype or "octet-stream",
                           filename=name)

    try:
        with smtplib.SMTP(host, port, timeout=10) as smtp:
            smtp.starttls()
            if user:
                smtp.login(user, password)
            smtp.send_message(msg)
        return True
    except Exception as exc:
        # Whatever went wrong — bad creds, host unreachable, TLS refused — the
        # caller's own work already succeeded and must stay that way. This is
        # visibility for the operator, not a condition anything downstream
        # should react to. Only the subject is logged, never the body: a
        # sign-in code lives in the body and must not reach production logs.
        log.warning("mail.send failed for %r: %s: %s", subject, type(exc).__name__, exc)
        return False
