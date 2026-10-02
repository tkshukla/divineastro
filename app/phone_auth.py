"""Phone-number sign-in by one-time SMS code (DIVASTRO-102).

Ships **disabled**. Nothing here is reachable, and /api/auth/providers does
not advertise "phone", until ASTRO_SMS_PROVIDER names a sender. The env
vars, and India's DLT requirement, are documented in app/auth.py's module
docstring alongside the other sign-in paths.

Identity follows the same scheme as everything else in auth.py:
provider="phone", provider_sub=<E.164 number>, and a session from
auth.issue_session(). A number that verifies once is the same account every
time after.

The flow is two calls:

* ``start(number)`` — normalise and validate the number, check the rate
  limits, generate a 6-digit code, send it, and remember only an HMAC of it.
* ``verify(number, code)`` — check the code against that HMAC, at most
  OTP_MAX_ATTEMPTS times, before OTP_TTL_SECONDS runs out; on success find or
  create the account.

Pending codes live in memory, like the password-login limiter in auth.py:
production is one process (`--workers 1`), so there is nothing to share, and
the worst a restart does is make someone tap "resend". The codes are HMAC'd
with ASTRO_SECRET_KEY all the same, so a memory dump or a stray debug print
never shows one. If this ever scales past one worker, the pending codes and
the limiter stores have to move to the database together.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import os
import re
import secrets
import time
from dataclasses import dataclass

import httpx
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import auth
from .db import CreditEntry, EntryKind, User, grant, utcnow

log = logging.getLogger("astro.phone_auth")

OTP_DIGITS = 6
OTP_TTL_SECONDS = 10 * 60          # Indian SMS can take a minute or two to land
OTP_MAX_ATTEMPTS = 5               # wrong guesses per code, then it is burned
RESEND_COOLDOWN_SECONDS = 30       # the UI counts this down before "Resend"

# Sends are what cost money and what could be used to pester a stranger's
# phone, so they are limited three ways: per number (short and daily
# windows) and per IP. Wrong codes are limited per IP as well as per code, so
# one client cannot spray guesses across many numbers.
SEND_PER_NUMBER = (3, 15 * 60)
SEND_PER_NUMBER_DAILY = (10, 24 * 60 * 60)
SEND_PER_IP = (10, 60 * 60)
VERIFY_FAILS_PER_IP = (20, 15 * 60)

_SENDS_BY_NUMBER: dict[str, list[float]] = {}
_SENDS_BY_NUMBER_DAILY: dict[str, list[float]] = {}
_SENDS_BY_IP: dict[str, list[float]] = {}
_VERIFY_FAILS_BY_IP: dict[str, list[float]] = {}


@dataclass
class _Pending:
    digest: str
    sent_at: float
    expires_at: float
    attempts: int = 0


_PENDING: dict[str, _Pending] = {}


# --------------------------------------------------------------------------
# Numbers
# --------------------------------------------------------------------------

def allowed_countries() -> list[str]:
    """Calling codes we will text, from ASTRO_SMS_COUNTRIES (default India)."""
    raw = os.environ.get("ASTRO_SMS_COUNTRIES", "91")
    codes = [c.strip().lstrip("+") for c in raw.replace(",", " ").split()]
    return [c for c in codes if c.isdigit()] or ["91"]


_INDIAN_MOBILE = re.compile(r"^[6-9]\d{9}$")


def normalise(raw: str) -> str:
    """Turn what a person types into E.164 (+919876543210), or raise 400.

    A bare 10-digit number, or one written 0XXXXXXXXXX / 91XXXXXXXXXX, is
    taken as Indian — that is how almost everyone here writes their own
    number. Anything else must start with "+" and an allowed calling code.
    """
    digits = re.sub(r"[\s\-().]", "", raw or "")
    bad = HTTPException(400, "Please enter a valid mobile number, e.g. 98765 43210.")
    if digits.startswith("+"):
        digits = digits[1:]
    elif len(digits) == 10:
        digits = "91" + digits
    elif len(digits) == 11 and digits.startswith("0"):
        digits = "91" + digits[1:]
    elif not (len(digits) == 12 and digits.startswith("91")):
        raise bad
    if not digits.isdigit():
        raise bad

    cc = next((c for c in allowed_countries() if digits.startswith(c)), None)
    if cc is None:
        raise HTTPException(400, "Sorry — sign-in by SMS is only available for "
                                 "Indian (+91) mobile numbers for now.")
    national = digits[len(cc):]
    if cc == "91":
        if not _INDIAN_MOBILE.match(national):
            raise bad
    elif not (6 <= len(national) <= 14 and len(digits) <= 15):
        raise bad
    return "+" + digits


def mask(number: str) -> str:
    """+919876543210 -> '+91 ••••••3210'. Safe to show and to log."""
    digits = (number or "").lstrip("+")
    if len(digits) < 6:
        return "••••"
    cc = next((c for c in allowed_countries() if digits.startswith(c)), digits[:2])
    national = digits[len(cc):]
    return f"+{cc} {'•' * max(len(national) - 4, 2)}{national[-4:]}"


# --------------------------------------------------------------------------
# Senders
# --------------------------------------------------------------------------

def _production() -> bool:
    """Same test dev-login uses: secure cookies mean a real deployment."""
    return os.environ.get("ASTRO_COOKIE_SECURE", "0") == "1"


class SmsSender:
    """Delivers one code. Returns False on failure; never raises."""

    name = "base"

    def send_code(self, number: str, code: str) -> bool:  # pragma: no cover
        raise NotImplementedError


class ConsoleSender(SmsSender):
    """Tests and local dev only: the code goes to the log, and to OUTBOX so a
    test can read it back. sender() refuses to hand this out in production."""

    name = "console"
    OUTBOX: list[tuple[str, str]] = []

    def send_code(self, number: str, code: str) -> bool:
        self.OUTBOX.append((number, code))
        log.warning("[console SMS — dev only] sign-in code for %s is %s", number, code)
        return True


class Msg91Sender(SmsSender):
    """MSG91's Flow API: the template (linked to a DLT-approved template in the
    MSG91 dashboard) must contain the variable ##otp##.

    Everything goes in the JSON body, never the query string: httpx logs each
    request URL at INFO, and a code in the URL would land in our own logs.
    """

    name = "msg91"
    URL = "https://control.msg91.com/api/v5/flow"

    def __init__(self, authkey: str, template_id: str) -> None:
        self.authkey, self.template_id = authkey, template_id

    def send_code(self, number: str, code: str) -> bool:
        try:
            r = httpx.post(
                self.URL, timeout=10,
                headers={"authkey": self.authkey, "accept": "application/json",
                         "content-type": "application/json"},
                json={"template_id": self.template_id, "short_url": "0",
                      "recipients": [{"mobiles": number.lstrip("+"), "otp": code}]},
            )
            data = r.json()
        except (httpx.HTTPError, ValueError) as exc:
            # The class name only: an exception's text can carry the request.
            log.error("MSG91: sending to %s failed (%s)", mask(number), type(exc).__name__)
            return False
        if r.status_code == 200 and data.get("type") == "success":
            return True
        log.error("MSG91: refused sending to %s: HTTP %s %s", mask(number),
                  r.status_code, str(data.get("message", ""))[:200])
        return False


def sender() -> SmsSender | None:
    """The configured sender, or None (phone sign-in off).

    Read from the environment on every call, like auth.admin_emails(), so a
    restart is all it takes to switch — and so tests can flip it.
    """
    kind = os.environ.get("ASTRO_SMS_PROVIDER", "").strip().lower()
    if not kind:
        return None
    if kind == "console":
        if _production():
            log.error("ASTRO_SMS_PROVIDER=console is refused in production "
                      "(ASTRO_COOKIE_SECURE=1): it would log every code. Phone sign-in is off.")
            return None
        return ConsoleSender()
    if kind == "msg91":
        authkey = os.environ.get("ASTRO_MSG91_AUTHKEY", "").strip()
        template = os.environ.get("ASTRO_MSG91_TEMPLATE_ID", "").strip()
        if not (authkey and template):
            log.error("ASTRO_SMS_PROVIDER=msg91 needs ASTRO_MSG91_AUTHKEY and "
                      "ASTRO_MSG91_TEMPLATE_ID. Phone sign-in is off.")
            return None
        return Msg91Sender(authkey, template)
    log.error("Unknown ASTRO_SMS_PROVIDER=%r. Phone sign-in is off.", kind)
    return None


def enabled() -> bool:
    return sender() is not None


# --------------------------------------------------------------------------
# The flow
# --------------------------------------------------------------------------

def _digest(number: str, code: str) -> str:
    return hmac.new(auth.SECRET.encode(), f"{number}|{code}".encode(),
                    hashlib.sha256).hexdigest()


def _too_many(what: str) -> HTTPException:
    return HTTPException(429, f"Too many {what}. Please wait a few minutes and try again.")


def start(raw_number: str, ip: str) -> dict:
    """Send a fresh code to the number. Replaces any earlier unused code."""
    sms = sender()
    if sms is None:
        raise HTTPException(404, "Not found.")
    number = normalise(raw_number)

    now = time.monotonic()
    pending = _PENDING.get(number)
    if pending and now - pending.sent_at < RESEND_COOLDOWN_SECONDS:
        wait = int(RESEND_COOLDOWN_SECONDS - (now - pending.sent_at)) + 1
        raise HTTPException(429, f"A code was just sent. You can ask for another in {wait} seconds.")
    if auth.throttled(_SENDS_BY_IP, ip, *SEND_PER_IP):
        raise _too_many("codes requested from this connection")
    if (auth.throttled(_SENDS_BY_NUMBER, number, *SEND_PER_NUMBER)
            or auth.throttled(_SENDS_BY_NUMBER_DAILY, number, *SEND_PER_NUMBER_DAILY)):
        raise _too_many("codes sent to this number")

    # Counted before sending, and whether or not it succeeds: a failing
    # gateway must not become an unlimited retry loop at our expense.
    auth.note_hit(_SENDS_BY_IP, ip)
    auth.note_hit(_SENDS_BY_NUMBER, number)
    auth.note_hit(_SENDS_BY_NUMBER_DAILY, number)

    code = f"{secrets.randbelow(10 ** OTP_DIGITS):0{OTP_DIGITS}d}"
    if not sms.send_code(number, code):
        raise HTTPException(502, "We couldn't send the SMS just now. Please try again "
                                 "in a minute, or sign in another way.")
    _PENDING[number] = _Pending(digest=_digest(number, code), sent_at=now,
                                expires_at=now + OTP_TTL_SECONDS)
    return {"ok": True, "number": mask(number), "digits": OTP_DIGITS,
            "expires_in": OTP_TTL_SECONDS, "resend_after": RESEND_COOLDOWN_SECONDS}


def check_code(raw_number: str, raw_code: str, ip: str) -> str:
    """Return the verified E.164 number, or raise. Burns the code on success."""
    if sender() is None:
        raise HTTPException(404, "Not found.")
    number = normalise(raw_number)
    code = re.sub(r"\D", "", raw_code or "")
    if len(code) != OTP_DIGITS:
        # A typo in length is not a guess; it does not use up an attempt.
        raise HTTPException(400, f"Enter the {OTP_DIGITS}-digit code from the SMS.")
    if auth.throttled(_VERIFY_FAILS_BY_IP, ip, *VERIFY_FAILS_PER_IP):
        raise _too_many("wrong codes from this connection")

    pending = _PENDING.get(number)
    if pending is None or time.monotonic() >= pending.expires_at:
        _PENDING.pop(number, None)
        raise HTTPException(400, "That code has expired. Please ask for a new one.")

    if not hmac.compare_digest(pending.digest, _digest(number, code)):
        pending.attempts += 1
        auth.note_hit(_VERIFY_FAILS_BY_IP, ip)
        left = OTP_MAX_ATTEMPTS - pending.attempts
        if left <= 0:
            _PENDING.pop(number, None)
            raise HTTPException(429, "Too many wrong codes. Please ask for a new one.")
        raise HTTPException(400, f"That code is not right. {left} "
                                 f"{'try' if left == 1 else 'tries'} left.")

    _PENDING.pop(number, None)
    return number


def _adopt_manual(db: Session, number: str) -> User | None:
    """An admin-recorded, phone-only customer (see api_account._manual_customer)
    is adopted the first time its owner proves the number, exactly as a manual
    *email* account is adopted by a verified Google sign-in — so a purchase
    recorded by hand is waiting for them. The admin typed the number however
    the customer said it, so every common spelling is tried."""
    digits = number.lstrip("+")
    cc = next((c for c in allowed_countries() if digits.startswith(c)), "")
    national = digits[len(cc):]
    spellings = {number, digits, national, "0" + national}
    user = db.execute(
        select(User).where(User.provider == "manual",
                           User.provider_sub.in_([f"manual:{s}" for s in spellings]))
        .order_by(User.id)
    ).scalars().first()
    if user is None:
        return None
    user.provider, user.provider_sub = "phone", number
    # _manual_customer grants the welcome gift only to email customers, so a
    # phone-only one never had it. Give it now, once.
    had_bonus = db.execute(
        select(CreditEntry.id).where(CreditEntry.user_id == user.id,
                                     CreditEntry.kind == EntryKind.signup_bonus)
    ).first()
    if had_bonus is None:
        from .billing import FREE_QUESTIONS

        grant(db, user.id, FREE_QUESTIONS, EntryKind.signup_bonus,
              note="Welcome — free questions")
    return user


def sign_in(db: Session, number: str) -> tuple[User, bool]:
    """Find or create the account for a number check_code() just verified."""
    user = db.execute(
        select(User).where(User.provider == "phone", User.provider_sub == number)
    ).scalar_one_or_none()
    if user is None:
        user = _adopt_manual(db, number)

    created = user is None
    if created:
        from .billing import FREE_QUESTIONS

        # No name: the header falls back to the masked number (auth.login_label),
        # and the person can add a name later if they want one.
        user = User(email="", name="", provider="phone", provider_sub=number,
                    phone=number)
        db.add(user)
        db.flush()
        grant(db, user.id, FREE_QUESTIONS, EntryKind.signup_bonus,
              note="Welcome — free questions")
    else:
        user.last_seen_at = utcnow()
        if not user.phone:
            user.phone = number

    db.commit()
    if user.blocked:
        raise HTTPException(403, auth.SUSPENDED_MESSAGE)
    return user, created


def reset_for_tests() -> None:
    """Forget every pending code and limiter hit. Tests only."""
    for store in (_PENDING, _SENDS_BY_NUMBER, _SENDS_BY_NUMBER_DAILY, _SENDS_BY_IP,
                  _VERIFY_FAILS_BY_IP):
        store.clear()
    ConsoleSender.OUTBOX.clear()
