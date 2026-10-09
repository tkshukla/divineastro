"""One free answer for a visitor who is not signed in (DIVASTRO-154).

A signed-out visitor who has cast a chart may ask ONE question and get a real
answer (same engine, same narration, same rule-engine fallback as a customer;
nothing is charged and no credit_entries row is written). The next question is
refused with 401 exactly as before, which opens the sign-in sheet. Every answer may
call a paid AI model, so the allowance is guarded several ways at once:

* **A signed, HttpOnly, SameSite=Lax cookie** (`astro_guest`) is set on the answer.
  While it is present and valid the visitor has had their answer.
* **A server-side record** (`guest_answers`, one row per answer) keyed by the
  day-scoped visitor hash analytics already uses (HMAC of IST-date + IP + browser;
  the IP itself is never stored). Clearing cookies on the same connection and
  browser therefore gets nothing more that day. The hash rotates at IST midnight by
  design (it must not follow people across days), so the cookie is what carries the
  limit beyond the day.
* **A per-address ceiling**, in process memory only and never stored (like
  analytics.rate_ok): ASTRO_GUEST_ANSWERS_PER_ADDRESS (default 20) a day from one
  IPv4 address or IPv6 /64. Generous because Indian mobile carriers put many people
  behind one address; it stops one machine rotating browser strings.
* **Global caps**: at most ASTRO_GUEST_ANSWERS_PER_HOUR (60) guest answers in any
  rolling hour and ASTRO_GUEST_ANSWERS_PER_DAY (400) in any rolling 24 hours, for
  everyone together. Beyond them guests get the sign-in sheet.
* **No answer at all** for bots, link-preview fetchers, prefetches and the cloud
  networks analytics.is_cloud_ip knows (the same filters as the visit statistics).

Do-Not-Track / Global-Privacy-Control visitors still get their one answer, but for
them the row holds only the time and the day-scoped hash, which is all the limit
needs: no question, no answer, no language. Nothing else about them is recorded.

ASTRO_GUEST_ANSWER=0 turns the whole path off (every signed-out question is a 401,
as before DIVASTRO-154).
"""

from __future__ import annotations

import datetime as dt
import ipaddress
import logging
import os
import threading
from dataclasses import dataclass

from fastapi import Request
from itsdangerous import BadSignature, URLSafeTimedSerializer
from sqlalchemy import delete, func, select

from . import analytics, auth
from .db import GuestAnswer, session as db_session, utcnow

log = logging.getLogger(__name__)

ENABLED = os.environ.get("ASTRO_GUEST_ANSWER", "1") != "0"
# How many answers a guest gets: one, by the owner's decision. Read by /api/me and
# /pricing so no page ever promises a guest answer while the path is switched off.
GUEST_ANSWERS = 1 if ENABLED else 0
PER_HOUR = int(os.environ.get("ASTRO_GUEST_ANSWERS_PER_HOUR", "60"))
PER_DAY = int(os.environ.get("ASTRO_GUEST_ANSWERS_PER_DAY", "400"))
PER_ADDRESS_DAY = int(os.environ.get("ASTRO_GUEST_ANSWERS_PER_ADDRESS", "20"))

COOKIE = "astro_guest"
COOKIE_MAX_AGE = 60 * 60 * 24 * 400          # as long as the statistics are kept
_signer = URLSafeTimedSerializer(auth.SECRET, salt="astro-guest")
_lock = threading.Lock()                       # check-then-insert must not race
_per_address: dict[str, tuple[str, int]] = {}  # address -> (IST day, answers): memory only
_ADDRESS_KEYS_MAX = 20_000

MAX_QUESTION = 500
MAX_ANSWER = 20_000


@dataclass
class Claim:
    id: int
    private: bool          # DNT / GPC: only ts + visitor are kept
    address: str


def _who(request: Request) -> tuple[str, str] | None:
    """(user_agent, ip) of a browser that may have a guest answer, else None."""
    h = request.headers
    if h.get("sec-purpose", "").startswith("prefetch") or h.get("purpose") == "prefetch":
        return None
    ua = h.get("user-agent", "")
    if analytics.is_bot(ua):
        return None
    ip = request.client.host if request.client else ""
    if not ip or analytics.is_cloud_ip(ip):
        return None
    return ua, ip


def _private(request: Request) -> bool:
    h = request.headers
    return h.get("dnt") == "1" or h.get("sec-gpc") == "1"


def cookie_used(request: Request) -> bool:
    """True while this browser holds a valid guest cookie (its answer is spent)."""
    token = request.cookies.get(COOKIE)
    if not token:
        return False
    try:
        data = _signer.loads(token, max_age=COOKIE_MAX_AGE)
    except BadSignature:
        return False                  # forged or from another secret: ignored, not trusted
    return isinstance(data, dict) and int(data.get("n", 0)) >= GUEST_ANSWERS


def _address_key(ip: str) -> str:
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return ip
    if addr.version == 6:
        return str(ipaddress.ip_network(f"{addr}/64", strict=False))
    return ip


def _today() -> str:
    return utcnow().astimezone(analytics.IST).date().isoformat()


def _address_count(key: str) -> int:
    day, n = _per_address.get(key, ("", 0))
    return n if day == _today() else 0


def _refusal(db, request: Request, who: tuple[str, str]) -> str | None:
    """Why this visitor may not have a guest answer now, or None if they may."""
    if not ENABLED:
        return "off"
    if cookie_used(request):
        return "cookie"
    ua, ip = who
    if _address_count(_address_key(ip)) >= PER_ADDRESS_DAY:
        return "address"
    now = utcnow()
    visitor = analytics.visitor_hash(ip, ua)
    if db.execute(select(func.count(GuestAnswer.id)).where(
            GuestAnswer.visitor == visitor)).scalar_one() >= GUEST_ANSWERS:
        return "visitor"
    hour = db.execute(select(func.count(GuestAnswer.id)).where(
        GuestAnswer.ts >= now - dt.timedelta(hours=1))).scalar_one()
    if hour >= PER_HOUR:
        return "hour_cap"
    day = db.execute(select(func.count(GuestAnswer.id)).where(
        GuestAnswer.ts >= now - dt.timedelta(hours=24))).scalar_one()
    if day >= PER_DAY:
        return "day_cap"
    return None


def answers_left(request: Request) -> int:
    """For /api/me: how many guest answers this signed-out browser can still get
    (0 or GUEST_ANSWERS). Read-only. Never raises."""
    try:
        who = _who(request)
        if who is None or not ENABLED:
            return 0
        with db_session() as db:
            return 0 if _refusal(db, request, who) else GUEST_ANSWERS
    except Exception:
        log.warning("guest allowance check failed", exc_info=True)
        return 0


def claim(request: Request, question: str, language: str = "") -> Claim | None:
    """Reserve this visitor's guest answer, or None if they may not have one.

    The row is written BEFORE any work, under a lock, so two simultaneous requests
    from one visitor cannot both pass the check. If the answer then cannot be
    produced, release() gives the allowance back."""
    who = _who(request)
    if who is None or not ENABLED:
        return None
    ua, ip = who
    private = _private(request)
    key = _address_key(ip)
    try:
        with _lock, db_session() as db:
            why = _refusal(db, request, who)
            if why:
                log.info("guest answer refused: %s", why)
                return None
            row = GuestAnswer(
                visitor=analytics.visitor_hash(ip, ua),
                question="" if private else " ".join((question or "").split())[:MAX_QUESTION],
                language="" if private else analytics.clean(language, 8),
                answer="")
            db.add(row)
            db.commit()
            _per_address[key] = (_today(), _address_count(key) + 1)
            if len(_per_address) > _ADDRESS_KEYS_MAX:      # a scan: forget yesterday's
                today = _today()
                for k in [k for k, (d, _) in _per_address.items() if d != today]:
                    del _per_address[k]
            return Claim(id=row.id, private=private, address=key)
    except Exception:
        log.warning("guest answer claim failed", exc_info=True)
        return None


def release(c: Claim | None) -> None:
    """Give the allowance back: the answer could not be produced. Never raises."""
    if c is None:
        return
    try:
        with _lock, db_session() as db:
            db.execute(delete(GuestAnswer).where(GuestAnswer.id == c.id))
            db.commit()
            day, n = _per_address.get(c.address, ("", 0))
            if n > 0:
                _per_address[c.address] = (day, n - 1)
    except Exception:
        log.warning("guest answer release failed", exc_info=True)


def record_answer(c: Claim | None, text: str) -> None:
    """Keep the answer the guest was shown (nothing for a DNT/GPC visitor)."""
    if c is None or c.private or not (text or "").strip():
        return
    try:
        with db_session() as db:
            row = db.get(GuestAnswer, c.id)
            if row is not None:
                row.answer = text.strip()[:MAX_ANSWER]
                db.commit()
    except Exception:
        log.warning("could not store guest answer", exc_info=True)


def set_cookie(response, request: Request) -> None:
    """Mark this browser's guest answer as spent. Signed (so it cannot be forged
    into something else), HttpOnly, SameSite=Lax."""
    secure = (os.environ.get("ASTRO_COOKIE_SECURE", "0") == "1"
              or request.url.scheme == "https")
    response.set_cookie(COOKIE, _signer.dumps({"n": GUEST_ANSWERS}), max_age=COOKIE_MAX_AGE,
                        httponly=True, samesite="lax", secure=secure, path="/")
