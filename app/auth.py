"""Social sign-in (Google / Microsoft / Apple) and signed session cookies.

No passwords and no OTP: the user picks a provider, we receive a verified email
and a stable subject id, and that is the account. Practical consequences:

* **Nothing to leak.** We never hold a credential the user could reuse elsewhere.
* **Identity is the (provider, sub) pair, not the email.** Emails can be
  reassigned inside an organisation; `sub` cannot. We match on `sub` first and
  fall back to a verified email so a person who signed up with Google and later
  uses Microsoft on the same address lands in the same account.
* **Apple needs a paid Apple Developer account** and a client secret that is a
  signed JWT valid for at most six months. It is wired up but stays hidden
  until APPLE_* is configured, so the other two work without it.

Phone number is kept as an optional profile field — it is how Pandit Shukla's
team reaches a customer about a hand-written kundali, not a login credential.
"""

from __future__ import annotations

import datetime as dt
import logging
import os
import secrets
import time

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
    """What the sign-in screen should offer. Empty until credentials are set."""
    return [{"key": k, "label": v} for k, v in PROVIDERS.items()]


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
        user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
        if user is not None and not user.provider_sub:
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
        raise HTTPException(403, "This account has been suspended.")
    return user, created


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


def require_user(request: Request, db: Session) -> User:
    user = current_user(request, db)
    if user is None:
        raise HTTPException(401, "Please sign in to continue.")
    return user


__all__ = [
    "OAuthError", "PROVIDERS", "clear_session", "client", "current_user",
    "issue_session", "providers", "require_user", "upsert_user",
]
