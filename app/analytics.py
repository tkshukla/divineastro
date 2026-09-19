"""Privacy-first traffic analytics for the admin Traffic panel.

What is recorded, and what deliberately is not
----------------------------------------------
A visit is one full page load of a public page. We store: when, which page,
where it came from (a classified source such as "google" or "whatsapp", plus any
utm_medium / utm_campaign), a device class, and a `visitor` hash.

We do NOT store the IP address, the user-agent string, or which user it was.
The hash is HMAC(server secret, IST-date | ip | user-agent), truncated. It lets
us count one person once per day, but it changes every day (so nobody can be
followed across days) and the IP cannot be recovered from it. Requests that send
Do-Not-Track / Global-Privacy-Control, bots, link-preview fetchers, prefetches,
and the administrator's own signed-in visits are not recorded at all.

Where a visitor first came from is remembered in ONE small first-party cookie so
it can be stamped on the account if they sign up later ("where do new users come
from"). Nothing else is put in it.

Known limits (also shown in the admin panel): only full page loads are counted,
not navigation inside the single-page app; and because the visitor hash rotates
daily, a multi-day "visitors" total is a sum of daily uniques, not lifetime
uniques.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import hmac
import logging
import os
import random
import re
from collections import Counter, defaultdict
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

from fastapi import Request
from starlette.datastructures import MutableHeaders
from sqlalchemy import delete, func, or_, select
from sqlalchemy.orm import Session

from . import auth
from .db import User, Visit, session as db_session, utcnow

log = logging.getLogger(__name__)

IST = ZoneInfo("Asia/Kolkata")            # the operator's calendar: days roll over at IST midnight
SRC_COOKIE = "astro_src"
SRC_COOKIE_MAX_AGE = 60 * 60 * 24 * 30
RETENTION_DAYS = 400                       # ~13 months, then rows are deleted
PURGE_ONE_IN = 400                         # on average once per 400 recorded visits

_BOT_RE = re.compile(
    r"bot|crawl|spider|slurp|curl/|wget|python-|httpx|aiohttp|okhttp|go-http|"
    r"java/|libwww|scrapy|headless|lighthouse|pingdom|uptime|monitor|"
    r"facebookexternalhit|facebot|whatsapp/|preview|embedly|feedfetcher|"
    r"mediapartners|google-read-aloud|bingpreview", re.IGNORECASE)

# Hosts that mean "the sign-in round trip" or "our own site", never a real source.
_AUTH_HOSTS = ("accounts.google.com", "login.microsoftonline.com", "login.live.com",
               "appleid.apple.com")

_HOST_RULES: list[tuple[re.Pattern, str]] = [(re.compile(p), n) for p, n in [
    (r"(^|\.)gemini\.google\.com$", "gemini"),
    (r"(^|\.)(mail\.google\.com|outlook\.live\.com|outlook\.office\.com|mail\.yahoo\.com)$", "email"),
    (r"(^|\.)google\.[a-z.]{2,}$", "google"),
    (r"(^|\.)bing\.com$", "bing"),
    (r"(^|\.)duckduckgo\.com$", "duckduckgo"),
    (r"(^|\.)yahoo\.[a-z.]{2,}$", "yahoo"),
    (r"(^|\.)yandex\.[a-z.]{2,}$", "yandex"),
    (r"(^|\.)ecosia\.org$", "ecosia"),
    (r"(^|\.)(facebook\.com|fb\.com|fb\.me|messenger\.com)$", "facebook"),
    (r"(^|\.)instagram\.com$", "instagram"),
    (r"(^|\.)(twitter\.com|x\.com|t\.co)$", "x"),
    (r"(^|\.)(youtube\.com|youtu\.be)$", "youtube"),
    (r"(^|\.)(whatsapp\.com|wa\.me)$", "whatsapp"),
    (r"(^|\.)(t\.me|telegram\.org|telegram\.me)$", "telegram"),
    (r"(^|\.)(linkedin\.com|lnkd\.in)$", "linkedin"),
    (r"(^|\.)reddit\.com$", "reddit"),
    (r"(^|\.)pinterest\.[a-z.]{2,}$", "pinterest"),
    (r"(^|\.)quora\.com$", "quora"),
    (r"(^|\.)(chatgpt\.com|openai\.com)$", "chatgpt"),
    (r"(^|\.)perplexity\.ai$", "perplexity"),
]]

_ANDROID_APPS = {
    "com.google.android.googlequicksearchbox": "google", "com.google.android.gm": "email",
    "com.whatsapp": "whatsapp", "com.whatsapp.w4b": "whatsapp",
    "com.facebook.katana": "facebook", "com.facebook.orca": "facebook",
    "com.instagram.android": "instagram", "org.telegram.messenger": "telegram",
    "com.twitter.android": "x", "com.linkedin.android": "linkedin",
}

_CLEAN_RE = re.compile(r"[^a-z0-9._:\-]")


def clean(value: str | None, limit: int = 60) -> str:
    """A label safe to store, put in a cookie and show: lowercase, [a-z0-9._:-] only."""
    return _CLEAN_RE.sub("", (value or "").strip().lower())[:limit]


def is_bot(user_agent: str) -> bool:
    return not user_agent or bool(_BOT_RE.search(user_agent))


def device_class(user_agent: str) -> str:
    u = user_agent.lower()
    if "ipad" in u or "tablet" in u or ("android" in u and "mobile" not in u):
        return "tablet"
    if "mobile" in u or "iphone" in u or "ipod" in u or "android" in u:
        return "mobile"
    return "desktop"


def _strip_host(host: str) -> str:
    host = host.lower().rstrip(".")
    for prefix in ("www.", "m.", "l.", "lm.", "mobile."):
        if host.startswith(prefix):
            host = host[len(prefix):]
    return host


def own_hosts(request_host: str = "") -> set[str]:
    """Hostnames that mean "this site": the one the request arrived on, plus the
    configured public URL — so a referrer of our own domain is recognised even
    when the app is reached by an internal name (a proxy, localhost)."""
    site = urlsplit(os.environ.get("ASTRO_SITE_URL", "https://divineastro.org")).hostname or ""
    return {_strip_host(h) for h in (request_host, site) if h}


def classify_source(referrer: str, query: dict[str, str],
                    own_host: str | set[str]) -> tuple[str, str, str]:
    """(source, medium, campaign) for one landing.

    An explicit utm_source (or ?ref=) wins — the operator tagged the link, so
    trust it — then the referrer's host, then "direct". A referrer that is our
    own site or the sign-in round trip is "internal": it is a page-to-page move,
    not a source, and is left out of the source tables.
    """
    medium, campaign = clean(query.get("utm_medium"), 40), clean(query.get("utm_campaign"), 80)
    tagged = clean(query.get("utm_source") or query.get("ref") or query.get("source"))
    if tagged:
        return tagged, medium, campaign
    if not referrer:
        return "direct", medium, campaign

    parts = urlsplit(referrer)
    if parts.scheme == "android-app":
        pkg = (parts.hostname or parts.netloc or "").lower()
        return _ANDROID_APPS.get(pkg, f"app:{clean(pkg)}"[:60]), medium, campaign
    host = _strip_host(parts.hostname or "")
    if not host:
        return "direct", medium, campaign
    own = {_strip_host(own_host)} if isinstance(own_host, str) else set(own_host)
    if host in own or host in _AUTH_HOSTS:
        return "internal", medium, campaign
    for rx, name in _HOST_RULES:
        if rx.search(host):
            return name, medium, campaign
    return clean(host) or "direct", medium, campaign


def visitor_hash(ip: str, user_agent: str, when: dt.datetime | None = None) -> str:
    """Anonymous, day-scoped visitor id. See the module docstring."""
    day = (when or utcnow()).astimezone(IST).date().isoformat()
    return hmac.new(auth.SECRET.encode(), f"{day}|{ip}|{user_agent}".encode(),
                    hashlib.sha256).hexdigest()[:16]


def _is_admin_session(db: Session, token: str | None) -> bool:
    if not token:
        return False
    try:
        data = auth._signer.loads(token, max_age=auth.MAX_AGE)
    except Exception:
        return False
    user = db.get(User, data.get("uid"))
    return bool(user is not None and user.is_admin)


def _trackable(request: Request) -> tuple[str, str] | None:
    """(user_agent, ip) if this request should be counted, else None."""
    if request.method != "GET":
        return None
    path = request.url.path
    if path.startswith(("/api", "/static", "/admin", "/docs", "/redoc", "/openapi")):
        return None
    h = request.headers
    if h.get("dnt") == "1" or h.get("sec-gpc") == "1":
        return None
    if h.get("sec-purpose", "").startswith("prefetch") or h.get("purpose") == "prefetch":
        return None
    if "welcome" in request.query_params:          # the landing after signing in
        return None
    ua = h.get("user-agent", "")
    if is_bot(ua):
        return None
    ip = request.client.host if request.client else ""
    return ua, ip


class SourceCookieMiddleware:
    """Adds the first-touch cookie to a response when page_visit() asked for one.

    Why this exists: a FastAPI dependency can set a cookie on its `Response`
    parameter, but FastAPI discards that when the route returns its own
    `HTMLResponse` (as every page route here does) — so the cookie silently never
    arrived and every sign-up was attributed to "unknown". The dependency instead
    leaves the header in `scope`, and this adds it to the outgoing response.

    Pure ASGI on purpose (not BaseHTTPMiddleware): it must not sit in the way of
    the streaming chat endpoint, and it does nothing unless a header was asked for.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        scope["astro_cookies"] = []

        async def send_with_cookies(message):
            if message["type"] == "http.response.start" and scope["astro_cookies"]:
                headers = MutableHeaders(scope=message)
                for value in scope["astro_cookies"]:
                    headers.append("set-cookie", value)
            await send(message)

        await self.app(scope, receive, send_with_cookies)


def page_visit(request: Request) -> None:
    """FastAPI dependency for the public HTML pages: count the visit and, on the
    first one, ask for the first-touch source cookie (see SourceCookieMiddleware).

    A dependency on those few routes (rather than a global middleware) keeps the
    tracking away from the streaming chat endpoint. It must never break the page,
    so every failure is swallowed and logged.
    """
    try:
        seen = _trackable(request)
        if seen is None:
            return
        ua, ip = seen
        query = dict(request.query_params)
        source, medium, campaign = classify_source(
            request.headers.get("referer", ""), query, own_hosts(request.url.hostname or ""))

        # First-touch: only the first external source is remembered. "internal"
        # (a page-to-page move) never overwrites or seeds it.
        if SRC_COOKIE not in request.cookies and source != "internal":
            cookie = (f"{SRC_COOKIE}={source}|{campaign}; Max-Age={SRC_COOKIE_MAX_AGE}; "
                      "Path=/; HttpOnly; SameSite=lax")
            if request.url.scheme == "https":
                cookie += "; Secure"
            request.scope.setdefault("astro_cookies", []).append(cookie)

        path = request.url.path.rstrip("/") or "/"
        with db_session() as db:
            if _is_admin_session(db, request.cookies.get(auth.COOKIE)):
                return                              # the operator's own visits don't count
            db.add(Visit(
                path=path[:200], source=source, medium=medium, campaign=campaign,
                device=device_class(ua), visitor=visitor_hash(ip, ua)))
            db.commit()
            if random.randrange(PURGE_ONE_IN) == 0:
                purge_old(db)
    except Exception:
        log.warning("visit tracking failed", exc_info=True)


def purge_old(db: Session) -> int:
    """Delete visits past the retention window. Returns how many."""
    cutoff = utcnow() - dt.timedelta(days=RETENTION_DAYS)
    n = db.execute(delete(Visit).where(Visit.ts < cutoff)).rowcount or 0
    db.commit()
    return n


def attribute_signup(db: Session, user: User, request: Request) -> None:
    """Stamp the visitor's first-touch source on a freshly created account."""
    raw = request.cookies.get(SRC_COOKIE, "")
    source, _, campaign = raw.partition("|")
    user.signup_source = clean(source) or "unknown"
    user.signup_campaign = clean(campaign, 80) or None
    db.commit()


# --------------------------------------------------------------------------
# Aggregation for the admin panel
# --------------------------------------------------------------------------

def _local_day(ts: dt.datetime) -> dt.date:
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=dt.timezone.utc)
    return ts.astimezone(IST).date()


def _top(counter: Counter, k: int = 8) -> list[dict]:
    """The k biggest, the rest folded into one "other" row, each with its share."""
    total = sum(counter.values())
    items = counter.most_common()
    head, tail = items[:k], items[k:]
    rows = [{"label": name, "count": n} for name, n in head]
    if tail:
        rows.append({"label": "other", "count": sum(n for _, n in tail)})
    for r in rows:
        r["share"] = round(r["count"] / total, 4) if total else 0
    return rows


def _totals(daily: list[dict]) -> dict:
    v = sum(d["visitors"] for d in daily)
    p = sum(d["pageviews"] for d in daily)
    u = sum(d["new_users"] for d in daily)
    return {"visitors": v, "pageviews": p, "new_users": u,
            "signup_rate": round(u / v, 4) if v else None}


def summary(db: Session, days: int = 30, now: dt.datetime | None = None) -> dict:
    """Everything the Traffic tab shows, for the last `days` IST calendar days."""
    now = now or utcnow()
    today = now.astimezone(IST).date()
    n = max(1, min(int(days), 180))
    span = max(n, 30)                      # the fixed today / 7d / 30d tiles need 30 days
    first_day = today - dt.timedelta(days=span - 1)
    start_utc = dt.datetime.combine(first_day, dt.time.min, IST).astimezone(dt.timezone.utc)

    visits = db.execute(
        select(Visit.ts, Visit.path, Visit.source, Visit.campaign, Visit.device, Visit.visitor)
        .where(Visit.ts >= start_utc).order_by(Visit.ts, Visit.id)).all()
    users = db.execute(
        select(User.created_at, User.signup_source, User.signup_campaign, User.provider)
        .where(User.created_at >= start_utc,
               or_(User.signup_source.is_(None), User.signup_source != "manual"))).all()

    pageviews: Counter = Counter()
    per_day_visitors: dict[dt.date, set] = defaultdict(set)
    first_visit: dict[tuple, tuple] = {}            # (day, visitor) -> (source, campaign, device)
    path_views: Counter = Counter()
    path_visitors: dict[str, set] = defaultdict(set)
    range_days = {today - dt.timedelta(days=i) for i in range(n)}

    for ts, path, source, campaign, device, visitor in visits:
        day = _local_day(ts)
        pageviews[day] += 1
        if visitor:
            per_day_visitors[day].add(visitor)
            first_visit.setdefault((day, visitor), (
                "direct" if source == "internal" else source, campaign, device))
        if day in range_days:
            path_views[path] += 1
            path_visitors[path].add((day, visitor))

    new_by_day: Counter = Counter()
    signup_sources: Counter = Counter()
    signup_campaigns: Counter = Counter()
    providers: Counter = Counter()
    for created_at, src, camp, provider in users:
        day = _local_day(created_at)
        new_by_day[day] += 1
        if day in range_days:
            signup_sources[src or "unknown"] += 1
            if camp:
                signup_campaigns[camp] += 1
            providers[provider or "unknown"] += 1

    daily = []
    for i in range(n):
        day = today - dt.timedelta(days=n - 1 - i)
        daily.append({
            "date": day.isoformat(), "label": f"{day.day} {day.strftime('%b')}",
            "visitors": len(per_day_visitors.get(day, ())),
            "pageviews": pageviews.get(day, 0), "new_users": new_by_day.get(day, 0)})

    def window(k: int) -> dict:
        ds = [today - dt.timedelta(days=i) for i in range(k)]
        v, p, u = (sum(len(per_day_visitors.get(d, ())) for d in ds),
                   sum(pageviews.get(d, 0) for d in ds), sum(new_by_day.get(d, 0) for d in ds))
        return {"visitors": v, "pageviews": p, "new_users": u,
                "signup_rate": round(u / v, 4) if v else None}

    src_counter: Counter = Counter()
    dev_counter: Counter = Counter()
    camp_counter: Counter = Counter()
    for (day, _visitor), (source, campaign, device) in first_visit.items():
        if day in range_days:
            src_counter[source] += 1
            dev_counter[device] += 1
            if campaign:
                camp_counter[campaign] += 1

    live_cut = now - dt.timedelta(minutes=5)
    live_now = db.execute(select(func.count(func.distinct(Visit.visitor)))
                          .where(Visit.ts >= live_cut)).scalar_one() or 0
    since = db.execute(select(func.min(Visit.ts))).scalar_one()
    users_total = db.execute(select(func.count(User.id)).where(
        or_(User.signup_source.is_(None), User.signup_source != "manual"))).scalar_one() or 0

    return {
        "range": {"days": n, "from": daily[0]["date"], "to": daily[-1]["date"], "tz": "Asia/Kolkata"},
        "windows": {"today": window(1), "d7": window(7), "d30": window(30)},
        "totals": _totals(daily),
        "live_now": live_now,
        "daily": daily,
        "sources": _top(src_counter),
        "signup_sources": _top(signup_sources),
        "signup_campaigns": _top(signup_campaigns, 6),
        "providers": _top(providers),
        "devices": _top(dev_counter),
        "campaigns": _top(camp_counter, 6),
        "pages": [{"label": p, "count": c, "visitors": len(path_visitors[p])}
                  for p, c in path_views.most_common(8)],
        "tracking_since": _local_day(since).isoformat() if since else None,
        "users_total": users_total,
    }
