"""Opt-in daily web push: "today's vrat, else today's Rahu Kaal" (DIVASTRO-112).

    GET  /sw.js                  the service worker (scope /): shows the push,
                                 opens its link on tap
    GET  /api/push/key           the VAPID public key the browser subscribes with
    POST /api/push/subscribe     {subscription, lat, lon, tz, label, lang}
    POST /api/push/unsubscribe   {endpoint}

Standard Web Push with VAPID (RFC 8030/8292) via `pywebpush` — the browser's
own push service (FCM for Chrome, Mozilla's for Firefox, Apple's for Safari)
carries it, so there is no paid service and no SDK on the page.

The whole feature is OFF unless ASTRO_VAPID_PUBLIC_KEY and
ASTRO_VAPID_PRIVATE_KEY are both set: every route above is a 404, the
server-rendered pages leave the opt-in out, the home button never appears
(it asks /api/push/key first), and the sender never starts.
`python -m app.push_keys` prints a fresh key pair.

THE DAILY SENDER — an in-process asyncio loop, not a host cron job
------------------------------------------------------------------
The app already owns everything a send needs (the DB, the VAPID keys in its
env, the ephemeris), and production is ONE uvicorn worker in ONE container
(Dockerfile: chart sessions live in process memory). The only cron on the
host is the watchdog, which must sit outside the app by its nature; a push
cron would instead need `docker compose exec` plumbing on the VM that is not
in the repo, and would silently stop the day someone rebuilds the host. So:
`start_sender()` runs from the app's lifespan, wakes every SENDER_INTERVAL_S,
and sends to each subscriber whose LOCAL time is between SEND_FROM and
SEND_UNTIL and who has had nothing yet on that local date (`last_sent`).
A restart or a deploy mid-morning simply resumes; a day whose whole window
the app was down for is skipped rather than sent stale in the evening.

  * Idempotent within one process: `last_sent` is committed per subscriber
    right after its send succeeds, and a pass never overlaps itself.
  * NOT safe with several workers/replicas: two loops could both see a
    subscriber as due and send twice. Before scaling out, take a lock around
    `run_due` (Postgres `pg_try_advisory_lock`, or `SELECT ... FOR UPDATE SKIP
    LOCKED` per row), or set ASTRO_PUSH_SENDER=0 on all but one instance.
  * ASTRO_PUSH_SENDER=0 turns the loop off without turning the feature off
    (the tests' throwaway servers do this).

A 404/410 from the push service means the subscription is gone (the user
revoked it, cleared the site, or the browser rotated it): the row is deleted.
Anything else counts a failure and closes that day (one attempt per day);
MAX_FAILURES days in a row deletes the row too.
"""

from __future__ import annotations

import asyncio
import base64
import datetime as dt
import ipaddress
import json
import logging
import os
import threading
import time
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from . import auth, push_message
from .db import PushSubscription, aware, session as db_session, utcnow

log = logging.getLogger("astro.push")

router = APIRouter()

SW_FILE = Path(__file__).parent / "static" / "sw.js"

SEND_FROM = dt.time(6, 0)          # local time a subscriber's daily push becomes due
SEND_UNTIL = dt.time(11, 0)        # ...and stops being due (no stale "today" at night)
SENDER_INTERVAL_S = int(os.environ.get("ASTRO_PUSH_INTERVAL_S", "300") or 300)
TTL_S = 6 * 3600                   # the push service may hold it this long for an offline phone
MAX_FAILURES = 10
ICON = "/static/icon-512.png"

# The browser vendors' push services. The server POSTs to whatever endpoint a
# subscriber hands it, so without this list anyone could make us send a daily
# request to an arbitrary (or internal) URL.
PUSH_HOSTS = (
    "fcm.googleapis.com",              # Chrome, Edge (new), Android, Samsung, Opera
    "android.googleapis.com",
    "updates.push.services.mozilla.com",  # Firefox
    "push.services.mozilla.com",
    "notify.windows.com",              # *.notify.windows.com — legacy Edge
    "push.apple.com",                  # web.push.apple.com — Safari 16+
)


def _env(name: str) -> str:
    return (os.environ.get(name) or "").strip()


def public_key() -> str:
    return _env("ASTRO_VAPID_PUBLIC_KEY")


def private_key() -> str:
    return _env("ASTRO_VAPID_PRIVATE_KEY")


def subject() -> str:
    return _env("ASTRO_VAPID_SUBJECT") or "mailto:support@divineastro.org"


def enabled() -> bool:
    return bool(public_key() and private_key())


def _require_enabled() -> None:
    if not enabled():
        raise HTTPException(404, "Not Found")


def optin_html(lang: str = "en") -> str:
    """The opt-in mount point + script for a server-rendered page, or "" while
    the feature is off. push.js fills it in only when the browser can do push
    and notifications are not blocked; otherwise it stays hidden."""
    if not enabled():
        return ""
    return ('<div class="push-optin" id="push-optin" hidden></div>'
            '<script src="/static/push.js" defer></script>')


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------

def _b64url_len(value: str) -> int | None:
    try:
        return len(base64.urlsafe_b64decode(value + "=" * (-len(value) % 4)))
    except (ValueError, TypeError):
        return None


def endpoint_ok(endpoint: str) -> bool:
    try:
        parts = urlsplit(endpoint)
    except ValueError:
        return False
    host = (parts.hostname or "").lower()
    if parts.scheme != "https" or not host or parts.port not in (None, 443):
        return False
    try:
        ipaddress.ip_address(host)
        return False                                   # never a bare IP
    except ValueError:
        pass
    return any(host == h or host.endswith("." + h) for h in PUSH_HOSTS)


def _zone(tz: str) -> ZoneInfo | None:
    try:
        return ZoneInfo(tz) if tz and len(tz) <= 64 else None
    except (ZoneInfoNotFoundError, ValueError):
        return None


class _Keys(BaseModel):
    p256dh: str = Field(..., max_length=200)
    auth: str = Field(..., max_length=64)


class _Subscription(BaseModel):
    endpoint: str = Field(..., max_length=1000)
    keys: _Keys


class SubscribeIn(BaseModel):
    subscription: _Subscription
    lat: float = Field(28.6139, ge=-90, le=90)
    lon: float = Field(77.2090, ge=-180, le=180)
    tz: str = Field("Asia/Kolkata", max_length=64)
    label: str = Field("", max_length=200)
    lang: str = "en"


class UnsubscribeIn(BaseModel):
    endpoint: str = Field(..., max_length=1000)


# A small per-address limit: subscribing is unauthenticated.
_RATE_WINDOW_S, _RATE_MAX = 600, 30
_rate: dict[str, tuple[float, int]] = {}


def _rate_ok(ip: str) -> bool:
    now = time.monotonic()
    start, n = _rate.get(ip, (now, 0))
    if now - start >= _RATE_WINDOW_S:
        start, n = now, 0
    if n >= _RATE_MAX:
        return False
    _rate[ip] = (start, n + 1)
    if len(_rate) > 5000:
        _rate.clear()
    return True


def get_db():
    db = db_session()
    try:
        yield db
    finally:
        db.close()


# --------------------------------------------------------------------------
# Routes
# --------------------------------------------------------------------------

@router.get("/sw.js", include_in_schema=False)
def service_worker() -> Response:
    """Served from the root so its scope can be the whole site. `no-cache` so
    a deploy's new worker is picked up on the next check."""
    _require_enabled()
    return Response(SW_FILE.read_text(encoding="utf-8"),
                    media_type="application/javascript; charset=utf-8",
                    headers={"Cache-Control": "no-cache", "Service-Worker-Allowed": "/"})


@router.get("/api/push/key")
def push_key() -> dict:
    _require_enabled()
    return {"key": public_key()}


@router.post("/api/push/subscribe")
def push_subscribe(body: SubscribeIn, request: Request, db: Session = Depends(get_db)) -> dict:
    _require_enabled()
    if not _rate_ok(request.client.host if request.client else ""):
        raise HTTPException(429, "Too many requests.")
    sub = body.subscription
    if not endpoint_ok(sub.endpoint):
        raise HTTPException(400, "Unsupported push endpoint.")
    p256dh_len = _b64url_len(sub.keys.p256dh)
    if p256dh_len != 65:                               # an uncompressed P-256 point
        raise HTTPException(400, "Invalid subscription keys.")
    if _b64url_len(sub.keys.auth) != 16:
        raise HTTPException(400, "Invalid subscription keys.")
    if _zone(body.tz) is None:
        raise HTTPException(400, "Unknown timezone.")
    lang = "hi" if body.lang == "hi" else "en"
    label = " ".join(body.label.split())[:120]
    user = None
    try:
        user = auth.current_user(request, db)
    except Exception:                                  # pragma: no cover - never block on this
        user = None

    row = db.execute(select(PushSubscription)
                     .where(PushSubscription.endpoint == sub.endpoint)).scalar_one_or_none()
    created = row is None
    if created:
        row = PushSubscription(endpoint=sub.endpoint)
        db.add(row)
    row.p256dh, row.auth = sub.keys.p256dh, sub.keys.auth
    row.lat, row.lon, row.tz = round(body.lat, 4), round(body.lon, 4), body.tz
    row.city, row.lang, row.failures = label, lang, 0
    if user is not None:
        row.user_id = user.id
    db.commit()
    return {"ok": True, "created": created}


@router.post("/api/push/unsubscribe")
def push_unsubscribe(body: UnsubscribeIn, db: Session = Depends(get_db)) -> dict:
    """Knowing the endpoint is the credential: only that browser has it."""
    _require_enabled()
    row = db.execute(select(PushSubscription)
                     .where(PushSubscription.endpoint == body.endpoint)).scalar_one_or_none()
    if row is not None:
        db.delete(row)
        db.commit()
    return {"ok": True, "removed": row is not None}


def subscriber_count(db: Session) -> int:
    return int(db.execute(select(func.count(PushSubscription.id))).scalar_one())


def admin_summary(db: Session) -> dict:
    """For the admin Traffic panel."""
    try:
        n = subscriber_count(db)
    except Exception:                                  # pragma: no cover - table missing
        n = 0
    return {"enabled": enabled(), "subscribers": n}


# --------------------------------------------------------------------------
# The daily sender
# --------------------------------------------------------------------------

def is_due(row: PushSubscription, now: dt.datetime) -> tuple[bool, dt.date | None]:
    """(due, the subscriber's local date). Due between SEND_FROM and SEND_UNTIL
    local time when nothing has been sent on that local date yet."""
    zone = _zone(row.tz) or ZoneInfo("Asia/Kolkata")
    local = now.astimezone(zone)
    if not (SEND_FROM <= local.time() < SEND_UNTIL):
        return False, local.date()
    last = aware(row.last_sent)
    if last is not None and last.astimezone(zone).date() >= local.date():
        return False, local.date()
    return True, local.date()


def payload(msg: dict, lang: str) -> str:
    return json.dumps({"title": msg["title"], "body": msg["body"], "url": msg["path"],
                       "icon": ICON, "badge": ICON, "tag": "daily", "lang": lang},
                      ensure_ascii=False)


def _vapid():
    # py_vapid.Vapid is the RFC 8292 signer ("Authorization: vapid t=..,k=..");
    # Vapid01 is the older draft scheme some push services no longer take.
    from py_vapid import Vapid
    return Vapid.from_string(private_key())


def send_one(row: PushSubscription, data: str, vapid=None) -> int:
    """Send one push. Returns the HTTP status (201 on success); raises nothing.
    0 means no HTTP answer at all (DNS, timeout, refused)."""
    import pywebpush
    try:
        resp = pywebpush.webpush(
            {"endpoint": row.endpoint, "keys": {"p256dh": row.p256dh, "auth": row.auth}},
            data=data,
            vapid_private_key=vapid if vapid is not None else _vapid(),
            vapid_claims={"sub": subject()},           # a fresh dict: webpush() mutates it
            ttl=TTL_S, timeout=10, headers={"Urgency": "normal"})
        return int(getattr(resp, "status_code", 201) or 201)
    except pywebpush.WebPushException as exc:
        status = getattr(exc.response, "status_code", None) if exc.response is not None else None
        return int(status or 0)
    except Exception as exc:                           # network errors and the like
        log.info("push send error: %s", exc.__class__.__name__)
        return 0


_pass_lock = threading.Lock()


def run_due(now: dt.datetime | None = None) -> dict:
    """One pass over every subscriber. Returns counts for logs and tests."""
    stats = {"due": 0, "sent": 0, "removed": 0, "failed": 0}
    if not enabled():
        return stats
    if not _pass_lock.acquire(blocking=False):         # a slow pass must not stack up
        return stats
    try:
        now = now or utcnow()
        vapid = _vapid()
        cache: dict[tuple, dict] = {}
        with db_session() as db:
            rows = db.execute(select(PushSubscription)).scalars().all()
            for row in rows:
                due, day = is_due(row, now)
                if not due:
                    continue
                stats["due"] += 1
                key = (day, round(row.lat, 2), round(row.lon, 2), row.tz, row.lang, row.city)
                try:
                    if key not in cache:
                        cache[key] = push_message.build(day, row.lat, row.lon, row.tz,
                                                         row.lang, city=row.city)
                except Exception:
                    log.exception("daily message failed for %s", key)
                    continue
                status = send_one(row, payload(cache[key], row.lang), vapid)
                if 200 <= status < 300:
                    row.last_sent, row.failures = now, 0
                    stats["sent"] += 1
                elif status in (404, 410):
                    db.delete(row)
                    stats["removed"] += 1
                else:
                    # One attempt a day: a push-service outage must not burn
                    # through MAX_FAILURES in an hour of 5-minute passes, so a
                    # failure also closes today (MAX_FAILURES = that many days).
                    row.last_sent = now
                    row.failures = (row.failures or 0) + 1
                    stats["failed"] += 1
                    if row.failures >= MAX_FAILURES:
                        db.delete(row)
                        stats["removed"] += 1
                db.commit()                            # per subscriber: a crash never re-sends
    finally:
        _pass_lock.release()
    if stats["due"]:
        log.info("daily push: %s", stats)
    return stats


async def _loop() -> None:
    while True:
        try:
            await asyncio.to_thread(run_due)
        except Exception:                              # pragma: no cover - keep the loop alive
            log.exception("daily push pass failed")
        await asyncio.sleep(SENDER_INTERVAL_S)


def start_sender() -> asyncio.Task | None:
    """Called from the app's lifespan. One loop per process — see the module
    docstring before running more than one worker."""
    if not enabled() or _env("ASTRO_PUSH_SENDER") == "0":
        return None
    log.info("daily push sender started (every %ss)", SENDER_INTERVAL_S)
    return asyncio.get_running_loop().create_task(_loop())
