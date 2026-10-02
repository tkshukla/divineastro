"""Email sign-in by one-time code (DIVASTRO-104).

The free alternative to phone OTP: SMS in India needs paid DLT registration,
while the mail module already sends through Brevo's free SMTP tier. The flow
mirrors app/phone_auth.py call for call, and the code machinery itself
(generation, HMAC storage, rate limits, attempt counting) is the same
app/otp.CodeBook:

* ``start(email, ip, lang)`` — normalise and validate the address, check the
  global daily cap and the rate limits, send a 6-digit code by email, and
  remember only an HMAC of it.
* ``check_code(email, code, ip, lang)`` — check the code, at most
  OTP_MAX_ATTEMPTS times, before OTP_TTL_SECONDS runs out.
* ``sign_in(db, email)`` — find, link or create the account.

It is on whenever mail is (``mail.configured()``, i.e. ASTRO_SMTP_HOST is
set), and off otherwise: neither advertised by /api/auth/providers nor
reachable.

Identity is provider="email", provider_sub=<the address, lowercased>. The
address is also stored in ``users.email``, because unlike a typed-in profile
field it *has* been verified.

**Linking to an existing account.** If someone who signed up with Google
later asks for an email code on the same address, they land in that Google
account rather than a duplicate. A correct code proves control of the
mailbox, which is the same thing Google's ``email_verified`` asserts — and
whoever controls a mailbox can already take over most accounts tied to it by
"forgot password", Google's included for non-Gmail addresses. Linking
therefore grants nothing the code's holder could not already get. The limits
we keep on purpose:

* Only accounts whose email came from a provider that verifies it — Google,
  Apple, and dev sign-in (tests/dev only) — are linked, plus an admin-recorded
  "manual" customer, which is adopted exactly as upsert_user adopts one.
  **Microsoft is excluded**: its ``email`` claim can be set by any tenant
  admin and is not proof of the mailbox (the "nOAuth" problem), so a
  Microsoft account claiming someone's address must not become the place
  their email code signs them in to. Password and phone accounts have no
  email to match.
* The match is exact, on the lowercased address. Gmail ignores dots and
  "+tags", but we do not fold them: folding would let a code sent to one
  literal address open an account registered under another, and a person
  who types their address differently simply gets a separate account.
* **Administrator accounts cannot use email codes.** An admin's Google
  sign-in carries Google's second factor and risk checks; a mailed code is
  one factor, so allowing it would quietly downgrade the most valuable
  accounts on the site. An address listed in ASTRO_ADMIN_EMAILS is refused
  too, even before it has an account, so an email code can never create,
  reach or promote an admin.
* Recycled addresses (a provider re-issuing an abandoned mailbox) are a
  residual risk shared with every email-based login; Google's own sign-in
  is protected by its stable ``sub``, the email-code path is not.

The other direction already works: a later Google sign-in on an address that
first signed up by code finds it through upsert_user's verified-email match.

**The free tier.** Brevo's free plan allows ~300 emails a day, shared with
the admin notification pings. ASTRO_EMAIL_DAILY_CAP (default 250) caps code
sends over any rolling 24 hours, leaving headroom for those pings; once hit,
start() answers 503 and the sign-in sheet points people to Google or a
username instead. The count is in memory like everything else here, so a
restart resets it — the cap is a guard against burning the quota, and Brevo
refusing beyond its limit is the backstop (a failed send is a 502, never a
silent success).
"""

from __future__ import annotations

import logging
import os
import re
import time

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import auth, mail, otp
from .db import CreditEntry, EntryKind, User, grant, utcnow

log = logging.getLogger("astro.email_auth")

OTP_DIGITS = 6
OTP_TTL_SECONDS = 10 * 60          # mail can sit in a queue or a spam folder for a while
OTP_MAX_ATTEMPTS = 5               # wrong guesses per code, then it is burned
RESEND_COOLDOWN_SECONDS = 30       # the UI counts this down before "Resend"

# Same shape as phone_auth: every send spends the shared free quota and could
# be used to pester a stranger's inbox, so sends are limited per address (short
# and daily windows) and per IP; wrong codes per IP as well as per code.
SEND_PER_ADDRESS = (3, 15 * 60)
SEND_PER_ADDRESS_DAILY = (10, 24 * 60 * 60)
SEND_PER_IP = (10, 60 * 60)
VERIFY_FAILS_PER_IP = (20, 15 * 60)

DAILY_CAP_DEFAULT = 250
_DAY = 24 * 60 * 60
_ALL_SENDS: dict[str, list[float]] = {}     # one key, "all": every code send
_cap_logged_at = 0.0

_BOOK = otp.CodeBook(
    ttl=OTP_TTL_SECONDS, max_attempts=OTP_MAX_ATTEMPTS, cooldown=RESEND_COOLDOWN_SECONDS,
    per_key=SEND_PER_ADDRESS, per_key_daily=SEND_PER_ADDRESS_DAILY, per_ip=SEND_PER_IP,
    fails_per_ip=VERIFY_FAILS_PER_IP, digits=OTP_DIGITS)
# Address -> pending code. The book's own dict, named here for tests to inspect.
_PENDING = _BOOK.pending

# Providers whose `users.email` is proof of the mailbox — see the docstring.
LINKABLE_PROVIDERS = ("google", "apple", "dev")


def enabled() -> bool:
    return mail.configured()


def daily_cap() -> int:
    """ASTRO_EMAIL_DAILY_CAP, read per call like the other auth switches."""
    try:
        return max(0, int(os.environ.get("ASTRO_EMAIL_DAILY_CAP", DAILY_CAP_DEFAULT)))
    except ValueError:
        return DAILY_CAP_DEFAULT


# --------------------------------------------------------------------------
# Wording (English + Hindi: the API answers in the language the sheet asked in)
# --------------------------------------------------------------------------

_MSG = {
    "en": {
        "bad": "Please enter a valid email address, e.g. name@gmail.com.",
        "typo": "Did you mean {s}? Please check the address.",
        "busy": "Email sign-in is busy right now. Please continue with Google, "
                "or create a username account — it takes a few seconds.",
        "cooldown": "A code was just sent. You can ask for another in {wait} seconds.",
        "ip_sends": "Too many codes requested from this connection. "
                    "Please wait a few minutes and try again.",
        "key_sends": "Too many codes sent to this address. Please wait a few minutes and try again.",
        "send_failed": "We couldn't send the email just now. Please try again "
                       "in a minute, or sign in another way.",
        "length": "Enter the 6-digit code from the email.",
        "ip_fails": "Too many wrong codes from this connection. "
                    "Please wait a few minutes and try again.",
        "expired": "That code has expired. Please ask for a new one.",
        "wrong": "That code is not right. {left} {tries} left.",
        "burned": "Too many wrong codes. Please ask for a new one.",
        "admin": "This is an administrator account. Please sign in with Google.",
    },
    "hi": {
        "bad": "कृपया सही ईमेल पता दर्ज करें, जैसे name@gmail.com",
        "typo": "क्या आपका मतलब {s} था? कृपया पता जाँच लें।",
        "busy": "ईमेल से साइन-इन अभी व्यस्त है। कृपया Google से जारी रखें, "
                "या यूज़रनेम वाला खाता बनाएँ — बस कुछ सेकंड लगते हैं।",
        "cooldown": "कोड अभी-अभी भेजा गया है। {wait} सेकंड बाद दूसरा माँग सकते हैं।",
        "ip_sends": "इस कनेक्शन से बहुत सारे कोड माँगे गए हैं। "
                    "कृपया कुछ मिनट रुककर फिर कोशिश करें।",
        "key_sends": "इस पते पर बहुत सारे कोड भेजे जा चुके हैं। कृपया कुछ मिनट रुककर फिर कोशिश करें।",
        "send_failed": "अभी ईमेल नहीं भेजा जा सका। कृपया एक मिनट बाद फिर कोशिश करें, "
                       "या किसी और तरीके से साइन इन करें।",
        "length": "ईमेल में आया 6 अंकों का कोड दर्ज करें।",
        "ip_fails": "इस कनेक्शन से बहुत सारे गलत कोड डाले गए हैं। "
                    "कृपया कुछ मिनट रुककर फिर कोशिश करें।",
        "expired": "इस कोड की समय-सीमा खत्म हो गई है। कृपया नया कोड माँगें।",
        "wrong": "यह कोड सही नहीं है। {left} {tries} बाकी।",
        "burned": "बहुत सारे गलत कोड। कृपया नया कोड माँगें।",
        "admin": "यह एडमिन खाता है। कृपया Google से साइन इन करें।",
    },
}


def _t(lang: str, key: str, **kw) -> str:
    table = _MSG.get(lang) or _MSG["en"]
    if key == "wrong":
        left = kw.get("left", 0)
        kw["tries"] = ("प्रयास" if lang == "hi"
                       else "try" if left == 1 else "tries")
    return table[key].format(**kw)


def _refusal(r: otp.Refused, lang: str) -> HTTPException:
    return HTTPException(r.status, _t(lang, r.reason, **r.info))


# --------------------------------------------------------------------------
# Addresses
# --------------------------------------------------------------------------

_LOCAL = re.compile(r"^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*$")
_LABEL = re.compile(r"^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$")
_TLD = re.compile(r"^([a-z]{2,63}|xn--[a-z0-9-]{1,59})$")
# Reserved names (RFC 2606/6761) can never receive mail; sending to them only
# spends the quota.
_RESERVED_TLDS = {"test", "example", "invalid", "localhost", "local"}
# Mistypes of the domains most of our visitors use. Each one would burn a
# send on an address that cannot answer, and leave the person waiting for a
# code that never comes — far kinder to ask before sending.
_TYPOS = {
    "gmial.com": "gmail.com", "gmai.com": "gmail.com", "gmal.com": "gmail.com",
    "gamil.com": "gmail.com", "gnail.com": "gmail.com", "gmail.co": "gmail.com",
    "gmail.con": "gmail.com", "gmail.cm": "gmail.com", "gmail.om": "gmail.com",
    "gmail.comm": "gmail.com", "gmaill.com": "gmail.com",
    "yahoo.con": "yahoo.com", "yaho.com": "yahoo.com", "yahooo.com": "yahoo.com",
    "yahoo.co": "yahoo.com", "hotmail.con": "hotmail.com", "hotmial.com": "hotmail.com",
    "hotmal.com": "hotmail.com", "outlook.con": "outlook.com", "outlok.com": "outlook.com",
    "rediffmail.con": "rediffmail.com", "redifmail.com": "rediffmail.com",
    "icloud.con": "icloud.com",
}
# users.provider_sub is 128 characters. Real addresses are far shorter; a
# longer one is junk, not something to truncate into a different identity.
MAX_LEN = 128


def normalise(raw: str, lang: str = "en") -> str:
    """Lowercase and validate an address, or raise 400.

    Deliberately stricter than RFC 5322 (no quoted local parts, no IP-literal
    domains): this is a sign-in field for real inboxes, and anything that
    exotic is far likelier to be a mistake or abuse than a customer.
    """
    addr = (raw or "").strip().lower()
    bad = HTTPException(400, _t(lang, "bad"))
    if not addr or len(addr) > MAX_LEN or addr.count("@") != 1:
        raise bad
    local, domain = addr.split("@")
    if not (1 <= len(local) <= 64) or not _LOCAL.match(local):
        raise bad
    labels = domain.split(".")
    if len(labels) < 2 or not all(_LABEL.match(lb) for lb in labels):
        raise bad
    if not _TLD.match(labels[-1]) or labels[-1] in _RESERVED_TLDS:
        raise bad
    if domain in _TYPOS:
        raise HTTPException(400, _t(lang, "typo", s=f"{local}@{_TYPOS[domain]}"))
    return addr


def mask(addr: str) -> str:
    """'ramesh@gmail.com' -> 'ra•••@gmail.com'. For logs only."""
    local, _, domain = (addr or "").partition("@")
    return f"{local[:2]}•••@{domain}" if domain else "•••"


# --------------------------------------------------------------------------
# The message
# --------------------------------------------------------------------------

SUBJECT = "Your Divine Astro sign-in code · आपका साइन-इन कोड"

_TEXT = {
    "en": ("Your Divine Astro sign-in code is:\n\n    {code}\n\n"
           "It is valid for 10 minutes. If you didn't ask for it, you can ignore "
           "this email — nobody can sign in without the code."),
    "hi": ("Divine Astro में साइन इन करने के लिए आपका कोड:\n\n    {code}\n\n"
           "यह 10 मिनट तक मान्य है। अगर आपने यह कोड नहीं माँगा, तो इस ईमेल को "
           "अनदेखा करें — कोड के बिना कोई साइन इन नहीं कर सकता।"),
}
_HTML_LEAD = {
    "en": ("Your sign-in code",
           "Valid for 10 minutes. If you didn't ask for it, ignore this email — "
           "nobody can sign in without the code."),
    "hi": ("आपका साइन-इन कोड",
           "10 मिनट तक मान्य। अगर आपने यह कोड नहीं माँगा, तो इस ईमेल को अनदेखा करें — "
           "कोड के बिना कोई साइन इन नहीं कर सकता।"),
}


def compose(code: str, lang: str = "en") -> tuple[str, str]:
    """(plain text, html) for one code. Both languages are always included,
    the visitor's own first: the person reading it may not be the one who
    chose the sheet's language, and a code is useless if it can't be read."""
    order = ["hi", "en"] if lang == "hi" else ["en", "hi"]
    text = "\n\n—\n\n".join(_TEXT[lg].format(code=code) for lg in order)
    text += "\n\nDivine Astro · https://divineastro.org\n"

    blocks = []
    for lg in order:
        title, note = _HTML_LEAD[lg]
        blocks.append(
            f'<p style="margin:0 0 6px;font-size:15px;color:#444">{title}</p>'
            f'<p style="margin:0 0 10px;font:700 32px/1.2 monospace;letter-spacing:6px;'
            f'color:#5b2a86">{code}</p>'
            f'<p style="margin:0 0 22px;font-size:13px;color:#666">{note}</p>')
    html = (
        '<!doctype html><html><body style="margin:0;padding:24px;background:#faf7f2;'
        'font-family:Arial,Helvetica,sans-serif">'
        '<div style="max-width:460px;margin:0 auto;background:#fff;border-radius:10px;'
        'padding:24px;border:1px solid #eee">'
        '<p style="margin:0 0 18px;font-size:18px;font-weight:700;color:#5b2a86">'
        '&#10022; Divine Astro</p>'
        + "".join(blocks) +
        '<p style="margin:0;font-size:12px;color:#999">'
        '<a href="https://divineastro.org" style="color:#999">divineastro.org</a></p>'
        '</div></body></html>')
    return text, html


# --------------------------------------------------------------------------
# The flow
# --------------------------------------------------------------------------

def _cap_reached() -> bool:
    global _cap_logged_at
    if not auth.throttled(_ALL_SENDS, "all", daily_cap(), _DAY):
        return False
    # Once an hour is enough to notice; every refused visitor would be noise.
    now = time.monotonic()
    if now - _cap_logged_at > 3600 or not _cap_logged_at:
        _cap_logged_at = now
        log.warning("Email sign-in daily cap reached (%s sends in 24h); "
                    "refusing new codes until the window rolls.", daily_cap())
    return True


def start(raw_email: str, ip: str, lang: str = "en") -> dict:
    """Email a fresh code to the address. Replaces any earlier unused code."""
    if not enabled():
        raise HTTPException(404, "Not found.")
    addr = normalise(raw_email, lang)
    if _cap_reached():
        raise HTTPException(503, _t(lang, "busy"))

    def deliver(code: str) -> bool:
        # Counted as soon as we try, success or not: a failed attempt may
        # still have used the provider's quota.
        auth.note_hit(_ALL_SENDS, "all")
        text, html = compose(code, lang)
        ok = mail.send([addr], SUBJECT, text, html)
        if not ok:
            log.error("Email sign-in: sending a code to %s failed", mask(addr))
        return ok

    try:
        _BOOK.issue(addr, ip, deliver)
    except otp.Refused as r:
        raise _refusal(r, lang) from None
    return {"ok": True, "email": addr, "digits": OTP_DIGITS,
            "expires_in": OTP_TTL_SECONDS, "resend_after": RESEND_COOLDOWN_SECONDS}


def check_code(raw_email: str, raw_code: str, ip: str, lang: str = "en") -> str:
    """Return the verified address, or raise. Burns the code on success."""
    if not enabled():
        raise HTTPException(404, "Not found.")
    addr = normalise(raw_email, lang)
    code = re.sub(r"\D", "", raw_code or "")
    if len(code) != OTP_DIGITS:
        # A typo in length is not a guess; it does not use up an attempt.
        raise HTTPException(400, _t(lang, "length"))
    try:
        _BOOK.check(addr, code, ip)
    except otp.Refused as r:
        raise _refusal(r, lang) from None
    return addr


def _has_bonus(db: Session, user_id: int) -> bool:
    return db.execute(
        select(CreditEntry.id).where(CreditEntry.user_id == user_id,
                                     CreditEntry.kind == EntryKind.signup_bonus)
    ).first() is not None


def _link_existing(db: Session, addr: str) -> User | None:
    """An account this verified address already belongs to — see the
    module docstring for which ones, and why."""
    user = db.execute(
        select(User).where(User.email == addr, User.provider.in_(LINKABLE_PROVIDERS))
        .order_by(User.id)
    ).scalars().first()
    if user is not None:
        return user

    # An admin-recorded customer who paid off-site: adopted on first proof of
    # the address, as upsert_user does for a Google sign-in, so the purchase
    # is waiting for them.
    manual = db.execute(
        select(User).where(User.provider == "manual",
                           (User.email == addr) | (User.provider_sub == f"manual:{addr}"))
        .order_by(User.id)
    ).scalars().first()
    if manual is not None:
        manual.provider, manual.provider_sub = "email", addr
        manual.email = manual.email or addr
        # _manual_customer grants the welcome gift to email customers already;
        # checked rather than assumed, so it is given exactly once either way.
        if not _has_bonus(db, manual.id):
            from .billing import FREE_QUESTIONS

            grant(db, manual.id, FREE_QUESTIONS, EntryKind.signup_bonus,
                  note="Welcome — free questions")
    return manual


def sign_in(db: Session, addr: str, lang: str = "en") -> tuple[User, bool]:
    """Find, link or create the account for an address check_code() verified."""
    user = db.execute(
        select(User).where(User.provider == "email", User.provider_sub == addr)
    ).scalar_one_or_none()
    if user is None:
        user = _link_existing(db, addr)

    if (user is not None and user.is_admin) or addr in auth.admin_emails():
        # Before anything is written: no last_seen bump, no adoption. An
        # ASTRO_ADMIN_EMAILS address is refused even with no account yet, or
        # the email-code account it created would be promoted to admin by
        # that address's first Google sign-in (upsert_user's email match).
        db.rollback()
        raise HTTPException(403, _t(lang, "admin"))

    created = user is None
    if created:
        from .billing import FREE_QUESTIONS

        # No name: the header shows the address's local part, as it does for
        # a Google account, and the person can add a name later.
        user = User(email=addr, name="", provider="email", provider_sub=addr)
        db.add(user)
        db.flush()
        grant(db, user.id, FREE_QUESTIONS, EntryKind.signup_bonus,
              note="Welcome — free questions")
    else:
        user.last_seen_at = utcnow()
        if not user.email:
            user.email = addr

    db.commit()
    if user.blocked:
        raise HTTPException(403, auth.SUSPENDED_MESSAGE)
    return user, created


def reset_for_tests() -> None:
    """Forget every pending code, limiter hit and the daily count. Tests only."""
    global _cap_logged_at
    _BOOK.reset()
    _ALL_SENDS.clear()
    _cap_logged_at = 0.0
    mail.OUTBOX.clear()
