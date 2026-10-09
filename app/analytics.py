"""Privacy-first traffic analytics for the admin Traffic panel.

What is recorded, and what deliberately is not
----------------------------------------------
A visit is one full page load of a public page, reported by that page's own
JavaScript (see static/visit.js -> POST /api/visit). We store: when, which page,
where it came from (a classified source such as "google" or "whatsapp", plus any
utm_medium / utm_campaign), a device class, and a `visitor` hash.

Why a beacon and not the HTML request: until DIVASTRO-99 a visit was recorded
when the server sent the HTML. Headless scanners with ordinary desktop-Chrome
user-agents, from residential-looking addresses, passed every filter below and
inflated "visitors" about five-fold (117 counted vs ~23 real browsers in the
week to 2 Oct 2026; of 413 addresses that fetched / only 29 ran the page's JS).
Those scanners do not execute JavaScript, so counting from the page's script
removes them without any fingerprinting. The cost is that a person with JS
disabled is not counted; the site does not work without JS anyway.

The beacon carries the page's own path, `document.referrer` and query string.
The beacon request's Referer header is always our own site, so classifying it
would make every visit "internal".

We do NOT store the IP address, the user-agent string, or which user it was.
The hash is HMAC(server secret, IST-date | ip | user-agent), truncated. It lets
us count one person once per day, but it changes every day (so nobody can be
followed across days) and the IP cannot be recovered from it. Requests that send
Do-Not-Track / Global-Privacy-Control, bots, link-preview fetchers, prerenders,
and the administrator's own signed-in visits are not recorded at all.

Where a visitor first came from is remembered in ONE small first-party cookie so
it can be stamped on the account if they sign up later ("where do new users come
from"). Nothing else is put in it. It is set on the beacon's response.

In-app actions (DIVASTRO-128): the single-page app also reports a short list of
named events (screen opened, chart cast, question asked, store opened, checkout
started, ...) to POST /api/event, stored in `events` under the same day-scoped
visitor hash and with the same exclusions. They carry a label from a fixed
vocabulary and nothing the visitor typed: no birth details, no question text.

Questions typed by visitors who are not signed in (DIVASTRO-131) are the one place
free text is kept: the server refuses them (401), and the operator wants to see what
people ask. Only the question text is stored (500 characters at most), under the same
day-scoped hash, with the same exclusions, a per-visitor-day cap, and a line in the
privacy policy. Birth details are never part of it.

Known limits (also shown in the admin panel): a full page load is one visit, and
in-app actions are the fixed event list above, not every click; and because the visitor hash rotates
daily, a multi-day "visitors" total is a sum of daily uniques, not lifetime
uniques.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import hmac
import ipaddress
import logging
import os
import random
import re
import time
from collections import Counter, defaultdict
from urllib.parse import parse_qsl, urlsplit
from zoneinfo import ZoneInfo

from fastapi import Request
from sqlalchemy import delete, func, or_, select
from sqlalchemy.orm import Session

from . import auth, i18n, rashifal_pages, seo_cities
from .db import (BirthProfile, Event, Order, OrderStatus, QuestionLog, UnregQuestion, User,
                 Visit, session as db_session, utcnow)

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


# Automated visitors that dress up as browsers (measured on the live server log,
# 2026-09-27: ~45% of what the Traffic panel showed as "visitors" was these).
#  - "iPhone OS 13_2_3": one fixed, long-obsolete iOS string sent from ~100 cloud
#    IPs. No real iPhone is on iOS 12 or earlier in 2026, and 13.x is vanishingly
#    rare, so any iPhone OS <= 13 is treated as automation.
#  - "(HTML, like Gecko": a typo'd copy of the real "(KHTML, like Gecko" token.
#  - scrapers that announce themselves without the word "bot".
_BOT_UA_EXTRA = re.compile(r"\(HTML, like Gecko|scraper|zeroscraper", re.IGNORECASE)
_OLD_IOS = re.compile(r"(?:iPhone|CPU) OS (\d+)_", re.IGNORECASE)
_MIN_REAL_UA_LEN = 20                     # "XY", "Google Chrome": no real browser is this terse

# Cloud networks nobody browses from. Every range below was seen sending the
# fake-browser traffic above and its owner confirmed by lookup on 2026-09-27
# (Tencent Cloud AS132203, Huawei Cloud AS136907, Google Cloud AS396982). The IP is
# only compared here in memory: it is never stored (see the module docstring).
# More ranges can be added without a code change via ASTRO_BOT_NETS (comma-separated CIDRs).
_CLOUD_NETS_DEFAULT = (
    "43.130.0.0/16", "43.134.0.0/16", "43.135.0.0/16", "43.153.0.0/16", "43.157.0.0/16",
    "43.164.0.0/16", "43.165.0.0/16", "43.166.0.0/16", "49.51.0.0/16", "162.62.0.0/16",
    "170.106.0.0/16",                                  # Tencent Cloud
    "114.119.128.0/17",                                # Huawei Cloud
    "34.96.0.0/16",                                    # Google Cloud
)


def _cloud_networks() -> list:
    raw = list(_CLOUD_NETS_DEFAULT) + [
        c.strip() for c in os.environ.get("ASTRO_BOT_NETS", "").split(",") if c.strip()]
    nets = []
    for cidr in raw:
        try:
            nets.append(ipaddress.ip_network(cidr, strict=False))
        except ValueError:
            log.warning("ignoring bad ASTRO_BOT_NETS entry %r", cidr)
    return nets


_CLOUD_NETS = _cloud_networks()


def is_cloud_ip(ip: str) -> bool:
    """True for an address inside a cloud network no person browses from."""
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return False
    return any(addr in net for net in _CLOUD_NETS if net.version == addr.version)


def is_bot(user_agent: str) -> bool:
    if not user_agent or len(user_agent.strip()) < _MIN_REAL_UA_LEN:
        return True
    if _BOT_RE.search(user_agent) or _BOT_UA_EXTRA.search(user_agent):
        return True
    m = _OLD_IOS.search(user_agent)
    return bool(m and int(m.group(1)) <= 13)


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


# The public pages a beacon may report. Anything else (an /api path, /admin, a
# made-up URL) is garbage or abuse and is ignored, so a forged beacon can at
# worst add a row for a page that really exists.
PUBLIC_PAGES = frozenset({"/", "/feedback", "/terms", "/privacy", "/refund", "/contact"})
# The SEO pages (seo_pages.py): the bare tool path, or tool + a real city slug,
# each also under /hi/ (DIVASTRO-106's Hindi copies).
SEO_TOOLS = frozenset({"/panchang", "/rahu-kaal", "/choghadiya", "/kundali-milan",
                       "/free-kundali", "/sitemap",    # /sitemap: DIVASTRO-133
                       "/pricing"})                   # /pricing: DIVASTRO-149
SEO_CITY_TOOLS = frozenset({"/panchang", "/rahu-kaal", "/choghadiya"})
# The daily rashifal pages (rashifal_pages.py): the 26 canonical URLs, EN + HI.
RASHIFAL_PAGES = rashifal_pages.PUBLIC_PATHS


def is_public_page(path: str) -> bool:
    """A real public page. DIVASTRO-121: /kn/, /te/, /ta/, /ml/, /bn/, /or/ copies
    count too — every SEO page exists in every registry language (untranslated
    ones are noindex but real pages people read) — except the app's home and the
    katha pages, which have no such copies."""
    lang, bare = i18n.strip_prefix(path)
    if lang in i18n.EXTRA_CODES:
        if (bare == "/" or bare in PUBLIC_PAGES or bare.startswith(("/katha", "/en/"))
                or i18n.strip_prefix(bare)[0] != "en"):
            return False
        return _is_public_page(bare)
    return _is_public_page(path)


def _is_public_page(path: str) -> bool:
    if path in PUBLIC_PAGES or path in RASHIFAL_PAGES:
        return True
    from .nakshatra_pages import is_public_path as nakshatra_public   # lazy (DIVASTRO-115)
    if nakshatra_public(path):
        return True
    from .learn_pages import is_public_path as learn_public   # lazy; False unless ASTRO_LEARN_PAGES=1 (DIVASTRO-142)
    if learn_public(path):
        return True
    if path.startswith(("/katha", "/en/katha")):
        from .katha import is_public_path as katha_public   # lazy, like the others
        return katha_public(path)
    if path.startswith("/hi/"):
        path = path[3:]
    if path in SEO_TOOLS:
        return True
    if path.startswith(("/vrat-tyohar", "/tyohar/", "/ekadashi-")):
        from .vrat_pages import is_public_path   # lazy, like muhurat_pages below
        return is_public_path(path)
    if path.startswith(("/muhurat/", "/hi/muhurat/")):
        from .muhurat_pages import page_paths   # lazy: muhurat_pages pulls in the engines
        return path in page_paths()
    from .recurring_pages import is_public_path as recurring_public   # lazy (DIVASTRO-141)
    if recurring_public(path):
        return True
    tool, _, slug = path.rpartition("/")
    return tool in SEO_CITY_TOOLS and seo_cities.get(slug) is not None
MAX_BEACON_BYTES = 2048          # path + referrer + query string; real ones are a few hundred
_MAX_FIELD = 1000                # per string field, before cleaning
_QUERY_KEYS = ("utm_source", "utm_medium", "utm_campaign", "ref", "source", "welcome")

# /api/visit is unauthenticated, so one address may only report so many page
# loads a minute. Generous on purpose: Indian mobile carriers put many people
# behind one CGNAT address. Kept in process memory only (the app runs one
# worker), never stored; like is_cloud_ip, the IP is used and forgotten.
RATE_WINDOW_S = 60.0
RATE_MAX = 60
_rate: dict[str, tuple[float, int]] = {}


_RATE_KEYS_MAX = 10_000


def _rate_key(ip: str) -> str:
    """The address, or for IPv6 its /64: one host is routinely handed a whole /64
    and could otherwise rotate through it to dodge the limit."""
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return ip
    if addr.version == 6:
        return str(ipaddress.ip_network(f"{addr}/64", strict=False))
    return ip


def rate_ok(ip: str, now: float | None = None) -> bool:
    """True if this address may report another page load in the current window.
    Called from the event loop only, so the dict needs no lock."""
    now = time.monotonic() if now is None else now
    key = _rate_key(ip)
    start, n = _rate.get(key, (now, 0))
    if now - start >= RATE_WINDOW_S:
        start, n = now, 0
    if n >= RATE_MAX:
        return False
    _rate[key] = (start, n + 1)
    if len(_rate) > _RATE_KEYS_MAX:               # a scan from many addresses: drop stale entries
        for k in [k for k, (t, _) in _rate.items() if now - t >= RATE_WINDOW_S]:
            del _rate[k]
        if len(_rate) > _RATE_KEYS_MAX // 2:      # still huge: forget it all rather than rescan every request
            _rate.clear()
    return True


def parse_beacon(data: object) -> tuple[str, str, dict[str, str]] | None:
    """(path, referrer, query) from a beacon body, or None if it is not one of ours.

    Only the few query keys classify_source() reads are kept, so a long or
    hostile query string never gets further than this.
    """
    if not isinstance(data, dict):
        return None
    path, ref, q = data.get("path"), data.get("ref", ""), data.get("q", "")
    if not all(isinstance(x, str) and len(x) <= _MAX_FIELD for x in (path, ref, q)):
        return None
    path = path.rstrip("/") or "/"
    if not is_public_page(path):
        return None
    try:
        pairs = parse_qsl(q.lstrip("?"), keep_blank_values=True, max_num_fields=40)
    except ValueError:
        return None
    query: dict[str, str] = {}
    for k, v in pairs:
        if k in _QUERY_KEYS:
            query.setdefault(k, v)
    return path, ref, query


def _countable(request: Request) -> tuple[str, str] | None:
    """(user_agent, ip) if the browser behind this beacon should be counted, else None.

    The beacon is a same-origin request from the page, so DNT / GPC, the
    user-agent, the address and the session cookie are the visitor's own.
    """
    h = request.headers
    if h.get("dnt") == "1" or h.get("sec-gpc") == "1":
        return None
    # A prerendered page runs its scripts before (or without) being seen; visit.js
    # waits for activation, and this catches any browser that does not.
    if h.get("sec-purpose", "").startswith("prefetch") or h.get("purpose") == "prefetch":
        return None
    ua = h.get("user-agent", "")
    if is_bot(ua):
        return None
    ip = request.client.host if request.client else ""
    if is_cloud_ip(ip):
        return None
    return ua, ip


def record_visit(request: Request, path: str, referrer: str,
                 query: dict[str, str]) -> str | None:
    """Count one page load reported by a beacon. Returns the first-touch
    Set-Cookie value to send back, or None.

    Never raises: analytics must not be able to break the page, so every failure
    is swallowed and logged.
    """
    try:
        seen = _countable(request)
        if seen is None or "welcome" in query:     # ?welcome is the landing after signing in
            return None
        ua, ip = seen
        source, medium, campaign = classify_source(
            referrer, query, own_hosts(request.url.hostname or ""))

        with db_session() as db:
            if _is_admin_session(db, request.cookies.get(auth.COOKIE)):
                return None                         # the operator's own visits don't count
            db.add(Visit(
                path=path[:200], source=source, medium=medium, campaign=campaign,
                device=device_class(ua), visitor=visitor_hash(ip, ua)))
            db.commit()
            if random.randrange(PURGE_ONE_IN) == 0:
                purge_old(db)

        # First-touch: only the first external source is remembered. "internal"
        # (a page-to-page move) never overwrites or seeds it.
        if SRC_COOKIE in request.cookies or source == "internal":
            return None
        cookie = (f"{SRC_COOKIE}={source}|{campaign}; Max-Age={SRC_COOKIE_MAX_AGE}; "
                  "Path=/; HttpOnly; SameSite=lax")
        if request.url.scheme == "https":
            cookie += "; Secure"
        return cookie
    except Exception:
        log.warning("visit tracking failed", exc_info=True)
        return None


# --------------------------------------------------------------------------
# In-app events (DIVASTRO-128)
# --------------------------------------------------------------------------

# Event names the app may report. Anything else is ignored, so a forged beacon
# can only add a row that looks like a real one.
EVENT_NAMES = frozenset({
    "screen",          # detail: the screen id (home, birth, chat, ...)
    "chart_cast",      # a chart was built
    "signin_open",     # the sign-in sheet opened
    "signup",          # an account was created (reported by the server)
    "ask_sent",        # a question was sent to the AI
    "store_open",      # the store opened (detail: "credits" when out of questions)
    "checkout_start",  # an order was started (detail: the sku)
    "paid",            # an order was confirmed paid (detail: the sku)
    "lang",            # the language was changed (detail: the code)
    "home_cta",        # the main kundali button on the home screen was tapped
    "strip_push",      # tapped "get daily alert" in the stay-in-touch strip (content pages)
    "strip_channel",   # tapped "join our WhatsApp channel" in that strip
    "strip_share",     # tapped "share this page on WhatsApp" in that strip
    "pricing_view",    # DIVASTRO-149: the home "Plans" section scrolled into view (detail "home"),
                       #   or /pricing opened (detail "page")
    "plans_click",     # tapped a plan card or "See all plans" on the home screen, or "Start free" on /pricing
    "offer_shown",     # an in-app offer appeared (detail: the sku, "low_credits" or "life_book_dashboard")
    "offer_click",     # ...and was tapped (same detail)
})
MAX_EVENT_BYTES = 512


def parse_event(data: object) -> tuple[str, str] | None:
    """(name, detail) from an event body, or None if it is not one of ours."""
    if not isinstance(data, dict):
        return None
    name, detail = data.get("name"), data.get("detail", "")
    if not isinstance(name, str) or not isinstance(detail, str) or len(detail) > 200:
        return None
    if name not in EVENT_NAMES:
        return None
    return name, clean(detail, 40)


def record_event(request: Request, name: str, detail: str = "") -> bool:
    """Store one in-app event if this browser should be counted. Never raises."""
    try:
        seen = _countable(request)
        if seen is None or name not in EVENT_NAMES:
            return False
        ua, ip = seen
        with db_session() as db:
            if _is_admin_session(db, request.cookies.get(auth.COOKIE)):
                return False
            source, _, campaign = request.cookies.get(SRC_COOKIE, "").partition("|")
            db.add(Event(name=name, detail=clean(detail, 40), visitor=visitor_hash(ip, ua),
                         source=clean(source), campaign=clean(campaign, 80)))
            db.commit()
        return True
    except Exception:
        log.warning("event tracking failed", exc_info=True)
        return False


UNREG_PER_VISITOR_DAY = 20


def record_unregistered_question(request: Request, question: str, language: str = "") -> bool:
    """Keep a question a signed-out visitor tried to ask. Never raises."""
    try:
        question = " ".join((question or "").split())[:500]
        seen = _countable(request)
        if not question or seen is None:
            return False
        ua, ip = seen
        visitor = visitor_hash(ip, ua)
        with db_session() as db:
            if _is_admin_session(db, request.cookies.get(auth.COOKIE)):
                return False
            since = utcnow() - dt.timedelta(hours=24)
            if (db.execute(select(func.count(UnregQuestion.id)).where(
                    UnregQuestion.visitor == visitor, UnregQuestion.ts >= since)).scalar_one()
                    >= UNREG_PER_VISITOR_DAY):
                return False
            source, _, campaign = request.cookies.get(SRC_COOKIE, "").partition("|")
            db.add(UnregQuestion(question=question, language=clean(language, 8), visitor=visitor,
                                 source=clean(source), campaign=clean(campaign, 80)))
            db.commit()
        return True
    except Exception:
        log.warning("unregistered-question capture failed", exc_info=True)
        return False


def unregistered_questions(db: Session, start_utc: dt.datetime, limit: int = 60,
                           end_utc: dt.datetime | None = None) -> list[dict]:
    q = select(UnregQuestion.ts, UnregQuestion.question, UnregQuestion.language,
               UnregQuestion.visitor, UnregQuestion.source, UnregQuestion.campaign
               ).where(UnregQuestion.ts >= start_utc)
    if end_utc is not None:
        q = q.where(UnregQuestion.ts < end_utc)
    rows = db.execute(q.order_by(UnregQuestion.ts.desc()).limit(limit)).all()
    return [{"when": ts.astimezone(IST).strftime("%d %b %H:%M"), "question": q, "language": lang,
             "visitor": v[:6], "source": src or "direct", "campaign": camp}
            for ts, q, lang, v, src, camp in rows]


def purge_old(db: Session) -> int:
    """Delete visits past the retention window. Returns how many."""
    cutoff = utcnow() - dt.timedelta(days=RETENTION_DAYS)
    n = db.execute(delete(Visit).where(Visit.ts < cutoff)).rowcount or 0
    db.execute(delete(Event).where(Event.ts < cutoff))
    db.execute(delete(UnregQuestion).where(UnregQuestion.ts < cutoff))
    db.commit()
    return n


def attribute_signup(db: Session, user: User, request: Request) -> None:
    """Stamp the visitor's first-touch source on a freshly created account."""
    raw = request.cookies.get(SRC_COOKIE, "")
    source, _, campaign = raw.partition("|")
    user.signup_source = clean(source) or "unknown"
    user.signup_campaign = clean(campaign, 80) or None
    db.commit()
    if not user.is_admin:
        record_event(request, "signup", user.provider or "")


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


def signup_rate(daily: list[dict], since: str | None) -> float | None:
    """New users ÷ visitors, counted ONLY over days that visit tracking covered.

    New-user counts come from sign-up dates and go back as far as the data does,
    but visitors only exist from the day tracking began. Dividing all of a
    window's new users by the few days of visitors we have gives nonsense (46 new
    users over 30 days ÷ 3 visitors = "1533%"), and it would stay wrong for weeks.
    So both sides are restricted to days on or after `since` (ISO date). None until
    there is at least one tracked visitor.
    """
    if not since:
        return None
    covered = [d for d in daily if d["date"] >= since]
    v = sum(d["visitors"] for d in covered)
    u = sum(d["new_users"] for d in covered)
    return round(u / v, 4) if v else None


def _totals(daily: list[dict], since: str | None = None) -> dict:
    v = sum(d["visitors"] for d in daily)
    p = sum(d["pageviews"] for d in daily)
    u = sum(d["new_users"] for d in daily)
    return {"visitors": v, "pageviews": p, "new_users": u,
            "signup_rate": signup_rate(daily, since)}


def funnel(db: Session, start_utc: dt.datetime, visitors: int, new_users: int) -> dict:
    """Visitors -> sign-ups -> people who saved a chart -> people who asked, for
    the window starting at `start_utc`.

    Saving a chart and asking a question both need an account, so sign-up is the
    step before them. A chart cast without signing in is not stored anywhere, so
    "saved a chart" is the nearest measurable step. The later steps count
    everyone active in the window, not only that window's new users, so they are
    not strictly a subset of the step before. The administrator's own charts and
    questions are left out, like their visits.
    """
    def active(model) -> tuple[int, int]:
        rows, people = db.execute(
            select(func.count(model.id), func.count(func.distinct(model.user_id)))
            .join(User, User.id == model.user_id)
            .where(model.created_at >= start_utc, User.is_admin.is_(False))).one()
        return rows or 0, people or 0

    charts, chart_users = active(BirthProfile)
    questions, question_users = active(QuestionLog)
    return {"visitors": visitors, "new_users": new_users,
            "chart_users": chart_users, "charts": charts,
            "question_users": question_users, "questions": questions}


APP_FUNNEL = (   # (label, event name, detail or None)
    ("Tapped the main kundali button", "home_cta", None),
    ("Opened the birth form", "screen", "birth"),
    ("Cast a chart", "chart_cast", None),
    ("Opened sign-in", "signin_open", None),
    ("Signed up", "signup", None),
    ("Asked the AI a question", "ask_sent", None),
    ("Saw the prices", "pricing_view", None),
    ("Tapped an in-app offer", "offer_click", None),
    ("Opened the store", "store_open", None),
    ("Started checkout", "checkout_start", None),
    ("Paid", "paid", None),
)


def _event_label(name: str, detail: str) -> str:
    return f"{name}: {detail}" if detail else name


def in_app(db: Session, start_utc: dt.datetime, range_days: set, today: dt.date,
           visit_rows: list) -> dict:
    """The in-app funnel for the range, and the latest visitor journeys.

    Both are keyed on (IST day, visitor hash): the hash is day-scoped, so that is
    one person on one day. A journey is that person's page loads and events in
    time order.
    """
    events = db.execute(
        select(Event.ts, Event.name, Event.detail, Event.visitor, Event.source, Event.campaign)
        .where(Event.ts >= start_utc).order_by(Event.ts, Event.id)).all()

    people: dict[tuple, set] = defaultdict(set)      # (name, detail) -> {(day, visitor)}
    for ts, name, detail, visitor, _src, _camp in events:
        day = _local_day(ts)
        if day in range_days and visitor:
            people[(name, detail)].add((day, visitor))
            people[(name, None)].add((day, visitor))
    steps = [{"label": label, "count": len(people.get((name, detail), ()))}
             for label, name, detail in APP_FUNNEL]

    # Journeys: today and yesterday, newest activity first.
    recent = {today, today - dt.timedelta(days=1)}
    journeys: dict[tuple, dict] = {}

    def journey(day, visitor):
        return journeys.setdefault((day, visitor), {
            "day": day.isoformat(), "visitor": visitor[:6], "source": "", "campaign": "",
            "device": "", "steps": [], "last": None})

    for ts, path, source, campaign, device, visitor in visit_rows:
        day = _local_day(ts)
        if day not in recent or not visitor:
            continue
        j = journey(day, visitor)
        if not j["source"] or j["source"] == "internal":
            j["source"], j["campaign"] = source, campaign
        j["device"] = j["device"] or device
        j["steps"].append((ts, "page", path))
    for ts, name, detail, visitor, source, campaign in events:
        day = _local_day(ts)
        if day not in recent or not visitor:
            continue
        j = journey(day, visitor)
        if not j["source"]:
            j["source"], j["campaign"] = source, campaign
        j["steps"].append((ts, "event", _event_label(name, detail)))

    out = []
    for j in journeys.values():
        j["steps"].sort(key=lambda x: x[0])
        compact: list[dict] = []
        for ts, kind, label in j["steps"]:
            if compact and compact[-1]["label"] == label and compact[-1]["kind"] == kind:
                continue                                  # same screen twice in a row
            compact.append({"t": ts.astimezone(IST).strftime("%H:%M"), "kind": kind, "label": label})
        last = j["steps"][-1][0]
        out.append({**j, "steps": compact[:40], "last": last.isoformat(),
                    "source": j["source"] or "direct"})
    out.sort(key=lambda x: x["last"], reverse=True)
    return {"app_funnel": steps, "journeys": out[:40]}


EVENT_LABELS = {          # the in-app actions, in plain words, for the day report
    ("screen", "birth"): "Opened the birth form", ("screen", "chat"): "Opened the AI chat",
    ("screen", "dashboard"): "Opened the chart dashboard", ("screen", "panchang"): "Opened Panchang",
    ("screen", "milan"): "Opened Kundali Milan", ("screen", "muhurat"): "Opened Muhurat",
    ("screen", "choghadiya"): "Opened Choghadiya", ("screen", "home"): "Back on the home screen",
    ("home_cta", ""): "Tapped the main kundali button",
    ("chart_cast", ""): "Cast a chart", ("ask_sent", ""): "Sent a question to the AI",
    ("signin_open", ""): "Sign-in sheet opened", ("signup", ""): "Signed up",
    ("store_open", "credits"): "Store opened (out of questions)",
    ("store_open", "browse"): "Store opened (browsing)",
    ("checkout_start", ""): "Started checkout", ("paid", ""): "Paid",
    ("strip_push", ""): "Tapped Get daily alert on a content page",
    ("strip_channel", ""): "Tapped Join WhatsApp channel on a content page",
    ("strip_share", ""): "Tapped Share on WhatsApp on a content page",
    # DIVASTRO-149: the purchase funnel's new steps
    ("pricing_view", "home"): "Saw the Plans section on the home screen",
    ("pricing_view", "page"): "Opened the /pricing page",
    ("plans_click", ""): "Tapped a plan on the home screen or Start free on /pricing",
    ("offer_shown", ""): "An in-app offer was shown",
    ("offer_shown", "low_credits"): "Offer shown: few questions left",
    ("offer_shown", "life_book_dashboard"): "Offer shown: Life Book after the chart",
    ("offer_shown", "sq_career"): "Offer shown: Career report after an answer",
    ("offer_shown", "sq_marriage_timing"): "Offer shown: Marriage report after an answer",
    ("offer_shown", "sq_wealth_business"): "Offer shown: Wealth report after an answer",
    ("offer_shown", "life_book"): "Offer shown: Life Book after an answer",
    ("offer_click", ""): "Tapped an in-app offer",
    ("offer_click", "low_credits"): "Tapped the offer: few questions left",
    ("offer_click", "life_book_dashboard"): "Tapped the offer: Life Book after the chart",
    ("offer_click", "sq_career"): "Tapped the offer: Career report",
    ("offer_click", "sq_marriage_timing"): "Tapped the offer: Marriage report",
    ("offer_click", "sq_wealth_business"): "Tapped the offer: Wealth report",
    ("offer_click", "life_book"): "Tapped the offer: Life Book",
}


def day_report(db: Session, day: dt.date, now: dt.datetime | None = None) -> dict:
    """One IST calendar day in full: the numbers that were quoted by hand in chat.

    Visitors and page views, new users, the same figures for the day before,
    sources (with campaign), the pages, devices, visitors by hour, what people
    did inside the app, questions asked while signed out, orders, and a 7-day trend.
    """
    now = now or utcnow()
    today = now.astimezone(IST).date()
    day = min(day, today)

    def bounds(d: dt.date):
        s = dt.datetime.combine(d, dt.time.min, IST).astimezone(dt.timezone.utc)
        return s, s + dt.timedelta(days=1)

    start, end = bounds(day)
    trend_from = day - dt.timedelta(days=6)
    t_start, _ = bounds(trend_from)

    visits = db.execute(
        select(Visit.ts, Visit.path, Visit.source, Visit.campaign, Visit.device, Visit.visitor)
        .where(Visit.ts >= t_start, Visit.ts < end).order_by(Visit.ts, Visit.id)).all()
    users = db.execute(
        select(User.created_at).where(
            User.created_at >= t_start, User.created_at < end,
            or_(User.signup_source.is_(None), User.signup_source != "manual"))).all()

    per_day_visitors: dict[dt.date, set] = defaultdict(set)
    per_day_views: Counter = Counter()
    for ts, _p, _s, _c, _d, visitor in visits:
        d = _local_day(ts)
        per_day_views[d] += 1
        if visitor:
            per_day_visitors[d].add(visitor)
    new_by_day: Counter = Counter(_local_day(r[0]) for r in users)

    def figures(d: dt.date) -> dict:
        v, p, u = len(per_day_visitors.get(d, ())), per_day_views.get(d, 0), new_by_day.get(d, 0)
        return {"visitors": v, "pageviews": p, "new_users": u}

    first: dict[str, tuple] = {}
    page_views: Counter = Counter()
    page_people: dict[str, set] = defaultdict(set)
    hourly = [set() for _ in range(24)]
    for ts, path, source, campaign, device, visitor in visits:
        if _local_day(ts) != day:
            continue
        page_views[path] += 1
        page_people[path].add(visitor)
        hourly[ts.astimezone(IST).hour].add(visitor)
        first.setdefault(visitor, ("direct" if source == "internal" else source, campaign, device))
    src: Counter = Counter()
    dev: Counter = Counter()
    for source, campaign, device in first.values():
        src[(source, campaign)] += 1
        dev[device] += 1

    ev_people: dict[tuple, set] = defaultdict(set)
    ev_count: Counter = Counter()
    for name, detail, visitor in db.execute(
            select(Event.name, Event.detail, Event.visitor)
            .where(Event.ts >= start, Event.ts < end)).all():
        key = (name, detail if (name, detail) in EVENT_LABELS else "")
        if (name, key[1]) not in EVENT_LABELS:
            continue
        ev_people[key].add(visitor)
        ev_count[key] += 1
    actions = [{"label": EVENT_LABELS[k], "people": len(ev_people[k]), "times": ev_count[k]}
               for k in EVENT_LABELS if k in ev_people]

    paid = db.execute(
        select(func.count(Order.id), func.coalesce(func.sum(Order.amount_paise), 0))
        .where(Order.status == OrderStatus.paid, Order.provider != "comp",
               Order.paid_at >= start, Order.paid_at < end)).one()

    today_f, prev_f = figures(day), figures(day - dt.timedelta(days=1))
    v = today_f["visitors"]
    return {
        "date": day.isoformat(), "label": f"{day.day} {day.strftime('%b %Y')}",
        "weekday": day.strftime("%A"), "is_today": day == today,
        "as_of": now.astimezone(IST).strftime("%H:%M") if day == today else None,
        **today_f,
        "pageviews_per_visitor": round(today_f["pageviews"] / v, 1) if v else None,
        "signup_rate": round(today_f["new_users"] / v, 4) if v else None,
        "previous": prev_f,
        "sources": [{"source": s, "campaign": c, "visitors": n} for (s, c), n in src.most_common(12)],
        "pages": [{"path": p, "views": n, "visitors": len(page_people[p])}
                  for p, n in page_views.most_common(12)],
        "devices": [{"device": d, "visitors": n} for d, n in dev.most_common()],
        "hours": [{"label": f"{h:02d}", "visitors": len(hourly[h])} for h in range(24)],
        "actions": actions,
        "orders": {"paid": paid[0] or 0, "revenue_rupees": round((paid[1] or 0) / 100)},
        "trend": [{"date": d.isoformat(), "label": f"{d.day} {d.strftime('%b')}", **figures(d)}
                  for d in (trend_from + dt.timedelta(days=i) for i in range(7))],
        "questions": unregistered_questions(db, start, 100, end),
    }


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

    since = db.execute(select(func.min(Visit.ts))).scalar_one()
    since_day = _local_day(since) if since else None

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
        # the rate only compares days that tracking covered (see signup_rate)
        tracked = [d for d in ds if since_day and d >= since_day]
        cv = sum(len(per_day_visitors.get(d, ())) for d in tracked)
        cu = sum(new_by_day.get(d, 0) for d in tracked)
        return {"visitors": v, "pageviews": p, "new_users": u,
                "signup_rate": round(cu / cv, 4) if cv else None}

    src_counter: Counter = Counter()
    dev_counter: Counter = Counter()
    camp_counter: Counter = Counter()
    for (day, _visitor), (source, campaign, device) in first_visit.items():
        if day in range_days:
            src_counter[source] += 1
            dev_counter[device] += 1
            if campaign:
                camp_counter[campaign] += 1

    totals = _totals(daily, since_day.isoformat() if since_day else None)
    range_start = dt.datetime.combine(
        today - dt.timedelta(days=n - 1), dt.time.min, IST).astimezone(dt.timezone.utc)

    live_cut = now - dt.timedelta(minutes=5)
    live_now = db.execute(select(func.count(func.distinct(Visit.visitor)))
                          .where(Visit.ts >= live_cut)).scalar_one() or 0
    users_total = db.execute(select(func.count(User.id)).where(
        or_(User.signup_source.is_(None), User.signup_source != "manual"))).scalar_one() or 0

    return {
        "range": {"days": n, "from": daily[0]["date"], "to": daily[-1]["date"], "tz": "Asia/Kolkata"},
        "windows": {"today": window(1), "d7": window(7), "d30": window(30)},
        "totals": totals,
        "funnel": funnel(db, range_start, totals["visitors"], totals["new_users"]),
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
        "tracking_since": since_day.isoformat() if since_day else None,
        "users_total": users_total,
        **in_app(db, start_utc, range_days, today, visits),
        "unreg_questions": unregistered_questions(db, range_start),
    }
