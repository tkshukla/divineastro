"""Outbound admin notification mail.

Just one caller today: `submit_utr()` in `api_account.py` pings an admin when
a customer claims a UPI payment, so someone doesn't have to remember to keep
checking `/admin/upi/pending`. Nothing here is customer-facing — this is
strictly an internal "look at this" ping.

Deliberately best-effort. `send()` never raises: a broken or unconfigured
mailbox must never turn into a 500 on the customer-facing claim endpoint that
called it. Leave `ASTRO_SMTP_HOST` unset and the claim still works exactly as
before this module existed — it just queues for `/admin` with nobody pinged.
"""

from __future__ import annotations

import logging
import os
import smtplib
from email.message import EmailMessage

log = logging.getLogger(__name__)


def configured() -> bool:
    return bool(os.environ.get("ASTRO_SMTP_HOST"))


def send(to: list[str], subject: str, body: str) -> bool:
    """Best-effort plain-text send. Returns whether it actually went out."""
    if not to:
        log.warning("mail.send: no recipients (ASTRO_ADMIN_EMAILS empty?), dropping %r", subject)
        return False
    if not configured():
        log.info("mail.send: ASTRO_SMTP_HOST not set, skipping %r", subject)
        return False

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

    try:
        with smtplib.SMTP(host, port, timeout=10) as smtp:
            smtp.starttls()
            if user:
                smtp.login(user, password)
            smtp.send_message(msg)
        return True
    except Exception as exc:
        # Whatever went wrong — bad creds, host unreachable, TLS refused — the
        # customer's claim already succeeded and must stay that way. This is
        # visibility for the operator, not a condition anything downstream
        # should react to.
        log.warning("mail.send failed for %r: %s: %s", subject, type(exc).__name__, exc)
        return False
