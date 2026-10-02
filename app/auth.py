"""Social sign-in (Google / Microsoft / Apple), username/password accounts,
and signed session cookies.

For OAuth: the user picks a provider, we receive a verified email and a
stable subject id, and that is the account — nothing to leak, we never hold
a credential the user could reuse elsewhere. **Identity is the (provider,
sub) pair, not the email.** Emails can be reassigned inside an organisation;
`sub` cannot. We match on `sub` first and fall back to a verified email so a
person who signed up with Google and later uses Microsoft on the same
address lands in the same account.

* **Apple needs a paid Apple Developer account** and a client secret that is a
  signed JWT valid for at most six months. It is wired up but stays hidden
  until APPLE_* is configured, so the other two work without it.

A username/password path (`register_password_user`/`verify_password_login`)
exists alongside OAuth for the opposite reason: a visitor who wants an
account without revealing any identity at all. It reuses the same
(provider, provider_sub) identity scheme — provider="password",
provider_sub=<username> — rather than a parallel users table, so it inherits
uniqueness and the session machinery below for free. There is deliberately
no email on these accounts, which means no password-recovery path either;
that is the cost of anonymity, not a gap to quietly work around.

Phone OTP (`app/phone_auth.py`) is the third path, for the many Indian
visitors who would rather type a mobile number than pick an account or
invent a password. Same scheme again: provider="phone", provider_sub=<the
number in E.164, e.g. +919876543210>, session via issue_session(). It ships
**disabled**: until ASTRO_SMS_PROVIDER is set it is neither advertised by
/api/auth/providers nor reachable.

* ``ASTRO_SMS_PROVIDER`` — ``msg91`` in production; ``console`` only for
  tests/dev (logs the code, and refuses to run when ASTRO_COOKIE_SECURE=1).
  Unset → phone sign-in off.
* ``ASTRO_MSG91_AUTHKEY`` — MSG91 dashboard → Authkey.
* ``ASTRO_MSG91_TEMPLATE_ID`` — the MSG91 OTP template id. **India DLT:**
  TRAI requires every commercial SMS to come from a DLT-registered entity
  (PE ID), a registered sender header and a pre-approved content template.
  Register on a DLT portal (Jio/Airtel/Vi/BSNL), get the OTP template
  approved with a variable for the code, then attach that DLT template id
  to the MSG91 template. Without it operators silently drop the SMS while
  the API still answers "success".
* ``ASTRO_SMS_COUNTRIES`` — calling codes allowed to receive a code,
  default ``91``. Kept narrow on purpose: an open OTP endpoint is a target
  for international SMS-pumping fraud, and we pay for every message.

Email codes (`app/email_auth.py`, DIVASTRO-104) are the fourth: the free
alternative to SMS, a 6-digit code mailed through the same Brevo SMTP as the
admin pings. provider="email", provider_sub=<the address, lowercased>. It is
on whenever mail is configured (``ASTRO_SMTP_HOST``), and
``ASTRO_EMAIL_DAILY_CAP`` (default 250) keeps code sends inside Brevo's free
~300/day. A verified address signs in to an existing Google/Apple account on
the same address rather than creating a duplicate; why that is safe, and why
Microsoft and admin accounts are excluded, is in that module's docstring.

The phone *profile* field (`users.phone`) is still just contact detail — how
Pandit Shukla's team reaches a customer about a hand-written kundali. It is
never used to find an account: it was typed in, not verified, so matching on
it would hand one person's account to whoever owns the number they typed. A
phone sign-in fills it in, since that number *has* been verified.
"""

from __future__ import annotations

import datetime as dt
import logging
import os
import re
import secrets
import time

import bcrypt
from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import HTTPException, Request, Response
from itsdangerous import BadSignature, URLSafeTimedSerializer
from sqlalchemy import select
from sqlalchemy.orm import Session

from .db import EntryKind, User, grant, utcnow

log = logging.getLogger("astro.auth")

SECRET = os.environ.get("ASTRO_SECRET_KEY", "")
if not SECRET:
    SECRET = secrets.token_urlsafe(48)
    log.warning("ASTRO_SECRET_KEY is not set — sessions will not survive a restart.")

COOKIE = "gd_session"
MAX_AGE = 60 * 60 * 24 * 60          # 60 days
_signer = URLSafeTimedSerializer(SECRET, salt="gd-session")

oauth = OAuth()


# --------------------------------------------------------------------------
# Provider registration
# --------------------------------------------------------------------------

def _apple_client_secret() -> str:
    """Apple's 'client secret' is a short-lived ES256 JWT we must mint ourselves."""
    from authlib.jose import jwt

    key = os.environ.get("APPLE_PRIVATE_KEY", "").replace("\\n", "\n")
    team_id = os.environ.get("APPLE_TEAM_ID", "")
    key_id = os.environ.get("APPLE_KEY_ID", "")
    client_id = os.environ.get("APPLE_CLIENT_ID", "")
    if not all((key, team_id, key_id, client_id)):
        return ""
    now = int(time.time())
    return jwt.encode(
        {"alg": "ES256", "kid": key_id},
        {"iss": team_id, "iat": now, "exp": now + 60 * 60 * 24 * 120,
         "aud": "https://appleid.apple.com", "sub": client_id},
        key,
    ).decode()


def _register() -> dict[str, str]:
    """Register whichever providers are configured. Returns {key: label}."""
    available: dict[str, str] = {}

    if os.environ.get("GOOGLE_CLIENT_ID") and os.environ.get("GOOGLE_CLIENT_SECRET"):
        oauth.register(
            name="google",
            client_id=os.environ["GOOGLE_CLIENT_ID"],
            client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
            client_kwargs={"scope": "openid email profile"},
        )
        available["google"] = "Google"

    if os.environ.get("MICROSOFT_CLIENT_ID") and os.environ.get("MICROSOFT_CLIENT_SECRET"):
        tenant = os.environ.get("MICROSOFT_TENANT", "common")
        oauth.register(
            name="microsoft",
            client_id=os.environ["MICROSOFT_CLIENT_ID"],
            client_secret=os.environ["MICROSOFT_CLIENT_SECRET"],
            server_metadata_url=(
                f"https://login.microsoftonline.com/{tenant}/v2.0/.well-known/"
                "openid-configuration"),
            client_kwargs={"scope": "openid email profile"},
        )
        available["microsoft"] = "Microsoft"

    apple_secret = _apple_client_secret()
    if apple_secret:
        oauth.register(
            name="apple",
            client_id=os.environ["APPLE_CLIENT_ID"],
            client_secret=apple_secret,
            server_metadata_url="https://appleid.apple.com/.well-known/openid-configuration",
            client_kwargs={"scope": "openid email name", "response_mode": "form_post"},
        )
        available["apple"] = "Apple"

    return available


PROVIDERS = _register()


def providers() -> list[dict]:
    """What the sign-in screen should offer.

    Redirect (OAuth) providers appear once their credentials are set. The ones
    that complete inside the page — email codes, when mail is configured;
    phone OTP, only when an SMS sender is configured; and username/password,
    which needs no configuration and is always on — are flagged
    ``inline: true``, so a page that can only render
    "Continue with X" links (admin, feedback) knows to skip them rather than
    link to /api/auth/<key>/start and a 400.
    """
    from . import email_auth, phone_auth

    out = [{"key": k, "label": v} for k, v in PROVIDERS.items()]
    if email_auth.enabled():
        out.append({"key": "email", "label": "Email", "inline": True})
    if phone_auth.enabled():
        out.append({"key": "phone", "label": "Phone", "inline": True})
    out.append({"key": "password", "label": "Username", "inline": True})
    return out


def client(name: str):
    if name not in PROVIDERS:
        raise HTTPException(400, f"{name.title()} sign-in is not configured.")
    return getattr(oauth, name)


# --------------------------------------------------------------------------
# Account resolution
# --------------------------------------------------------------------------

def admin_emails() -> set[str]:
    """Addresses that get administrator rights, from ASTRO_ADMIN_EMAILS.

    Read on every call rather than cached at import, so the operator list can
    be changed with a restart and no code edit. Comma or space separated.
    """
    raw = os.environ.get("ASTRO_ADMIN_EMAILS", "")
    return {p.strip().lower() for p in raw.replace(",", " ").split() if "@" in p}


def upsert_user(db: Session, provider: str, claims: dict) -> tuple[User, bool]:
    """Find or create the account behind a verified OIDC token."""
    sub = str(claims.get("sub") or "")
    email = (claims.get("email") or "").strip().lower()
    verified = claims.get("email_verified", True)
    name = (claims.get("name") or claims.get("given_name") or "").strip()

    if not sub:
        raise HTTPException(400, "The sign-in provider did not return an account id.")

    user = db.execute(
        select(User).where(User.provider == provider, User.provider_sub == sub)
    ).scalar_one_or_none()

    # Same person, different provider, same verified address → one account.
    if user is None and email and verified:
        # first(), not scalar_one_or_none(): an email-code account and, say, a
        # Microsoft one can legitimately share an address, and two matches
        # must pick the oldest account, not raise a 500 mid-sign-in.
        user = db.execute(
            select(User).where(User.email == email).order_by(User.id)
        ).scalars().first()
        # An admin-created "manual" account (a customer paid off-site and was
        # recorded by hand) is adopted the first time its owner signs in with
        # the same verified address, so their purchase is waiting for them.
        if user is not None and (not user.provider_sub or user.provider == "manual"):
            user.provider, user.provider_sub = provider, sub

    created = user is None
    if created:
        from .billing import FREE_QUESTIONS

        user = User(
            email=email, name=name[:120], provider=provider, provider_sub=sub,
            picture=(claims.get("picture") or "")[:400],
        )
        db.add(user)
        db.flush()
        grant(db, user.id, FREE_QUESTIONS, EntryKind.signup_bonus,
              note="Welcome — free questions")
    else:
        user.last_seen_at = utcnow()
        if name and not user.name:
            user.name = name[:120]
        if email and not user.email:
            user.email = email

    # Operators listed in ASTRO_ADMIN_EMAILS are promoted on sign-in, so the
    # owner can reach the admin panel without touching the database. Promotion
    # only: removing an address here does not demote an existing admin, since
    # is_admin may also have been granted deliberately by hand.
    if email and verified and email in admin_emails():
        user.is_admin = True

    db.commit()
    if user.blocked:
        raise HTTPException(403, SUSPENDED_MESSAGE)
    return user, created


# --------------------------------------------------------------------------
# Username/password accounts
# --------------------------------------------------------------------------
# A deliberately separate pair of functions, not a branch inside
# upsert_user(): that function's email-merge step assumes a *verified OIDC*
# email, which has no equivalent here — these accounts have no email at all.

USERNAME_RE = re.compile(r"^[a-zA-Z0-9_-]{3,30}$")
MIN_PASSWORD_LEN = 8

# In-memory only: a single-process deployment (confirmed — one app
# container, `--workers 1` in the Dockerfile), so this doesn't need to
# survive a restart or be shared across replicas. Keyed by username; a failed
# attempt against a username that doesn't exist is tracked the same way a
# wrong password is, so probing for valid usernames is rate-limited too, not
# just password guessing.
_LOGIN_FAILS: dict[str, list[float]] = {}
LOGIN_MAX_ATTEMPTS = 5
LOGIN_WINDOW_SECONDS = 15 * 60


def throttled(store: dict[str, list[float]], key: str, limit: int, window: float) -> bool:
    """Sliding window: True once `key` has `limit` hits inside the last `window`
    seconds. Shared by password login and phone OTP, each with its own store."""
    now = time.monotonic()
    hits = [t for t in store.get(key, []) if now - t < window]
    if hits:
        store[key] = hits
    else:
        store.pop(key, None)       # one-off keys (IPs, numbers) must not pile up
    return len(hits) >= limit


def note_hit(store: dict[str, list[float]], key: str) -> None:
    store.setdefault(key, []).append(time.monotonic())


def _login_rate_limited(username: str) -> bool:
    return throttled(_LOGIN_FAILS, username, LOGIN_MAX_ATTEMPTS, LOGIN_WINDOW_SECONDS)


def _record_login_failure(username: str) -> None:
    note_hit(_LOGIN_FAILS, username)


def login_label(user: User) -> str:
    """How an account is recognised on screen when it has no name or email.

    A phone account shows a masked number (+91 ••••••3210): enough for its
    owner to recognise, not enough to read off a shoulder or a screenshot.
    """
    if user.provider == "phone":
        from .phone_auth import mask

        return mask(user.provider_sub)
    if user.provider == "password":
        return user.provider_sub
    # An email-code account is labelled by its address, exactly like a Google
    # one: the header already shows only the part before the "@" (account.js),
    # and the full address is what the owner's admin needs to see.
    if user.provider == "email":
        return user.email or user.provider_sub
    return user.email or ""


def register_password_user(db: Session, username: str, password: str) -> User:
    """Create a username/password account. No email, no real name required."""
    username = username.strip()
    if not USERNAME_RE.match(username):
        raise HTTPException(
            400, "Username must be 3-30 characters: letters, numbers, _ or - only.")
    if len(password) < MIN_PASSWORD_LEN:
        raise HTTPException(400, f"Password must be at least {MIN_PASSWORD_LEN} characters.")

    existing = db.execute(
        select(User).where(User.provider == "password", User.provider_sub == username)
    ).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(409, "That username is already taken.")

    from .billing import FREE_QUESTIONS

    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    user = User(
        email="", name=username, provider="password", provider_sub=username,
        password_hash=password_hash,
    )
    db.add(user)
    db.flush()
    grant(db, user.id, FREE_QUESTIONS, EntryKind.signup_bonus, note="Welcome — free questions")
    db.commit()
    return user


def verify_password_login(db: Session, username: str, password: str) -> User | None:
    """Return the user on a correct username+password, else None.

    Never distinguishes "no such username" from "wrong password" in what it
    returns — the caller must show one generic message either way, or this
    account enumeration protection is pointless.
    """
    username = username.strip()
    if _login_rate_limited(username):
        raise HTTPException(
            429, "Too many attempts. Please wait a few minutes and try again.")

    user = db.execute(
        select(User).where(User.provider == "password", User.provider_sub == username)
    ).scalar_one_or_none()
    if user is None or not user.password_hash:
        _record_login_failure(username)
        return None
    if not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
        _record_login_failure(username)
        return None

    user.last_seen_at = utcnow()
    db.commit()
    if user.blocked:
        raise HTTPException(403, SUSPENDED_MESSAGE)
    return user


# --------------------------------------------------------------------------
# Sessions
# --------------------------------------------------------------------------

def issue_session(response: Response, user: User) -> None:
    token = _signer.dumps({"uid": user.id})
    secure = os.environ.get("ASTRO_COOKIE_SECURE", "0") == "1"
    response.set_cookie(
        COOKIE, token, max_age=MAX_AGE, httponly=True,
        samesite="lax", secure=secure, path="/",
    )


def clear_session(response: Response) -> None:
    response.delete_cookie(COOKIE, path="/")


def current_user(request: Request, db: Session) -> User | None:
    token = request.cookies.get(COOKIE)
    if not token:
        return None
    try:
        data = _signer.loads(token, max_age=MAX_AGE)
    except BadSignature:
        return None
    user = db.get(User, data.get("uid"))
    return None if (user is None or user.blocked) else user


SUSPENDED_MESSAGE = (
    "This account has been suspended. If you think this is a mistake, "
    f"write to {os.environ.get('ASTRO_SUPPORT_EMAIL', 'support@divineastro.org')}.")


def _session_is_blocked(request: Request, db: Session) -> bool:
    """A valid session cookie whose account has since been blocked."""
    token = request.cookies.get(COOKIE)
    if not token:
        return False
    try:
        data = _signer.loads(token, max_age=MAX_AGE)
    except BadSignature:
        return False
    user = db.get(User, data.get("uid"))
    return bool(user is not None and user.blocked)


def require_user(request: Request, db: Session) -> User:
    user = current_user(request, db)
    if user is None:
        # 403, not 401, for a blocked account: "please sign in" would send them
        # round a loop that can never succeed, and tell them nothing.
        if _session_is_blocked(request, db):
            raise HTTPException(403, SUSPENDED_MESSAGE)
        raise HTTPException(401, "Please sign in to continue.")
    return user


__all__ = [
    "OAuthError", "PROVIDERS", "clear_session", "client", "current_user",
    "issue_session", "login_label", "note_hit", "providers", "require_user",
    "throttled", "upsert_user",
]
