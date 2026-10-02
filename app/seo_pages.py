"""Server-rendered public pages for the free tools, plus sitemap.xml and robots.txt.

Why these exist (DIVASTRO-100): the app is one single-page shell at `/`, so a
search engine sees one URL and a page of buttons. Panchang, Rahu Kaal and
Choghadiya are what people in India search for every morning, and none of it
was indexable. Each page here carries its content in the raw HTML — no script
has to run for a crawler (or a slow phone) to read today's tithi or Rahu Kaal.

Everything shown is computed by the same engines the app uses
(`astro.panchang.daily_panchang` for the five limbs and the muhurta windows), so
a page can never disagree with the tool it links to on those numbers. Festival
names are deliberately NOT shown: `daily_panchang` reports the sunrise tithi,
which is the wrong rule for aparahna/pradosh-vyapini festivals (the 1-day-off
bug fixed in DIVASTRO-90 by separate helpers) — only the daily elements, which
the sunrise rule does get right, appear here.

Rendering follows legal.py: a format-string shell, no template engine (Jinja is
not a dependency and this does not justify one). Every interpolated value goes
through `_e` even though the cities are curated — the habit is cheaper than the
audit.
"""

from __future__ import annotations

import datetime as dt
import functools
import html
import json
import math
from xml.sax.saxutils import escape as xml_escape
from zoneinfo import ZoneInfo

from fastapi import APIRouter
from fastapi.responses import HTMLResponse, PlainTextResponse, Response

from . import seo_cities
from .astro import choghadiya as chog
from .astro import matching
from .astro import panchang as panchang_engine
from .astro.muhurat import NAKSHATRAS_HI, TITHI_HI, VARA_HI
from .legal import ADDRESS, BRAND, EMAIL, LEGAL_NAME, PHONE, SITE, registration_inline
from .seo_cities import City

router = APIRouter()

IST = ZoneInfo("Asia/Kolkata")
SITE_URL = SITE.rstrip("/")

# Same publisher as index.html. main.py owns ADSENSE_PUBLISHER for /ads.txt but
# importing main from here would be circular; tests/test_seo_pages.py checks
# the two agree.
ADSENSE_CLIENT = "ca-pub-1593974697916149"

# Tool slug -> (display name, Hindi name, the `?open=` key app.js deep-links to).
TOOLS = {
    "panchang": ("Panchang", "पंचांग", "panchang"),
    "rahu-kaal": ("Rahu Kaal", "राहु काल", "panchang"),
    "choghadiya": ("Choghadiya", "चौघड़िया", "choghadiya"),
}

PAKSHA_HI = {"Shukla": "शुक्ल पक्ष", "Krishna": "कृष्ण पक्ष"}


def _e(value: object) -> str:
    return html.escape(str(value), quote=True)


# --------------------------------------------------------------------------
# Dates, caching and time formatting
# --------------------------------------------------------------------------

def _today() -> dt.date:
    """Today in India. The container runs UTC; between 00:00 and 05:30 IST a
    server-local "today" would show yesterday's Rahu Kaal (same bug api_tools
    fixed for /api/panchang)."""
    return dt.datetime.now(IST).date()


def _cache_headers() -> dict[str, str]:
    """Cache until the next IST midnight, capped at 30 minutes.

    The content changes once a day, so a short max-age costs nothing — but it
    must never outlive the day it describes, or a cached copy would show
    yesterday's Rahu Kaal after midnight. `private` so a shared cache
    never serves one person's copy to another.
    """
    now = dt.datetime.now(IST)
    midnight = dt.datetime.combine(now.date() + dt.timedelta(days=1), dt.time(), IST)
    max_age = max(60, min(1800, int((midnight - now).total_seconds())))
    return {"Cache-Control": f"private, max-age={max_age}"}


@functools.lru_cache(maxsize=512)
def _panchang(slug: str, day: dt.date) -> dict:
    """One city's almanac for one day. ~10 ms to compute, so this is not about
    a single visitor — it keeps a crawler walking all 90 URLs, or a burst of
    WhatsApp shares, from recomputing the same day hundreds of times. Keyed on
    the date, so entries simply stop being asked for after midnight and age
    out of the LRU. Callers must treat the dict as read-only."""
    city = seo_cities.BY_SLUG[slug]
    return panchang_engine.daily_panchang(day, city.latitude, city.longitude, city.timezone)


def _local(iso: str | None) -> dt.datetime | None:
    return dt.datetime.fromisoformat(iso).astimezone(IST) if iso else None


def _clock(moment: dt.datetime) -> str:
    return moment.strftime("%I:%M %p").lstrip("0")


def _time(iso: str | None, day: dt.date) -> str:
    """'6:29 AM', with the date added when it falls on another civil day —
    tithis and moonrise routinely do, and a bare '1:18 AM' would read as this
    morning rather than tonight."""
    moment = _local(iso)
    if moment is None:
        return "—"
    text = _clock(moment)
    if moment.date() != day:
        text += f" ({moment.day} {moment.strftime('%b')})"
    return text


def _span(window: dict | None, day: dt.date) -> str:
    if not window:
        return "—"
    return f"{_time(window['start'], day)} – {_time(window['end'], day)}"


def _long_date(day: dt.date) -> str:
    return f"{day.day} {day.strftime('%B %Y')}"


# --------------------------------------------------------------------------
# Page shell
# --------------------------------------------------------------------------

_STYLE = """
  body { overflow: auto; display: block; }
  .seo { max-width: 820px; margin: 0 auto; padding: 22px 16px 40px; }
  .seo .back { display: inline-block; margin-bottom: 14px; color: var(--ink-faint);
               font-size: 13px; text-decoration: none; }
  .seo .crumbs { font-size: 12.5px; color: var(--ink-faint); margin: 0 0 10px; }
  .seo .crumbs a { color: var(--ink-faint); }
  .seo h1 { font-family: var(--serif); font-weight: 400; font-size: 27px; line-height: 1.25;
            color: var(--gold-soft); margin: 0 0 4px; }
  .seo .hi { font-size: 18px; color: var(--gold); margin: 0 0 6px; }
  .seo .date { font-family: var(--mono); font-size: 13px; color: var(--ink-faint); margin: 0 0 18px; }
  .seo h2 { font-family: var(--serif); font-weight: 400; font-size: 20px; color: var(--gold);
            margin: 28px 0 10px; }
  .seo p, .seo li { color: var(--ink-dim); font-size: 15px; line-height: 1.7; }
  .seo strong { color: var(--ink); }
  .seo a { color: var(--cyan); }
  .seo .box { border: 1px solid var(--line); border-radius: 14px; padding: 14px 16px;
              background: var(--inset-bg); margin: 16px 0; }
  .seo .scroll { overflow-x: auto; -webkit-overflow-scrolling: touch; }
  .seo table { width: 100%; border-collapse: collapse; font-size: 14.5px; }
  .seo th, .seo td { text-align: left; padding: 9px 8px; border-bottom: 1px solid var(--line);
                     vertical-align: top; }
  .seo th { color: var(--ink-faint); font-weight: 500; white-space: nowrap; }
  .seo td { color: var(--ink); }
  .seo td small { color: var(--ink-faint); display: block; }
  .seo .good { color: var(--green); } .seo .bad { color: var(--rose); }
  .seo .cta { display: block; text-align: center; margin: 24px 0; padding: 14px 18px;
              border-radius: 12px; font-weight: 600; text-decoration: none; color: #fff;
              background: linear-gradient(120deg, var(--primary-a), var(--primary-b)); }
  .seo .links { display: flex; flex-wrap: wrap; gap: 8px; padding: 0; list-style: none; }
  .seo .links a { display: inline-block; padding: 6px 12px; border: 1px solid var(--line);
                  border-radius: 999px; font-size: 13.5px; text-decoration: none;
                  color: var(--ink-dim); }
  .seo .links a[aria-current] { color: var(--gold); border-color: var(--gold); }
  .site-footer { margin: 30px auto 0; }
  @media (min-width: 640px) { .seo { padding-top: 40px; } .seo h1 { font-size: 32px; } }
"""

_SHELL = """<!DOCTYPE html>
<html lang="en-IN"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{title}</title>
<meta name="description" content="{description}"/>
<link rel="canonical" href="{canonical}"/>
<meta property="og:type" content="website"/>
<meta property="og:site_name" content="{brand}"/>
<meta property="og:title" content="{title}"/>
<meta property="og:description" content="{description}"/>
<meta property="og:url" content="{canonical}"/>
<meta property="og:image" content="{site}/static/icon-512.png"/>
<meta property="og:locale" content="en_IN"/>
<meta name="twitter:card" content="summary"/>
<meta name="google-adsense-account" content="{adsense}"/>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={adsense}"
        crossorigin="anonymous"></script>
<script src="/static/visit.js" defer></script>   <!-- counts the page load: see analytics.py -->
<link rel="icon" href="/static/favicon.ico"/>
<link rel="apple-touch-icon" href="/static/apple-touch-icon.png"/>
<link rel="stylesheet" href="/static/styles.css"/>
<style>{style}</style>
<script type="application/ld+json">{jsonld}</script>
</head>
<body class="sacred">
<main class="seo">
  <a class="back" href="/">&larr; {brand}</a>
  <nav class="crumbs" aria-label="Breadcrumb">{crumbs}</nav>
  {body}
</main>
{footer}
</body></html>"""


def _footer() -> str:
    """The same public footer as index.html — the links AdSense and payment
    underwriters look for, from the same constants the legal pages use."""
    reg = registration_inline()
    return f"""<footer class="site-footer">
  <nav>
    <a href="/terms">Terms &amp; Conditions</a>
    <a href="/privacy">Privacy Policy</a>
    <a href="/refund">Refund &amp; Cancellation</a>
    <a href="/contact">Contact Us</a>
    <a href="/feedback">Feedback</a>
  </nav>
  <p class="legal-entity">{_e(LEGAL_NAME)} · {_e(ADDRESS)} ·
    <a href="mailto:{_e(EMAIL)}">{_e(EMAIL)}</a> · {_e(PHONE)}</p>
  {f'<p class="legal-entity registrations">{_e(reg)}</p>' if reg else ''}
  <p class="disclaimer">Astrological readings are provided for guidance and
    entertainment. They are not medical, legal or financial advice.</p>
</footer>"""


def _render(*, title: str, description: str, path: str, crumbs: list[tuple[str, str]],
            body: str, status: int = 200, cache: bool = True) -> HTMLResponse:
    canonical = SITE_URL + path
    trail = [("Home", "/")] + crumbs
    crumb_html = " › ".join(
        f'<a href="{_e(href)}">{_e(name)}</a>' if i < len(trail) - 1 else _e(name)
        for i, (name, href) in enumerate(trail))
    graph = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "WebPage", "name": title, "description": description,
             "url": canonical, "inLanguage": ["en-IN", "hi-IN"],
             "dateModified": _today().isoformat(),
             "isPartOf": {"@type": "WebSite", "name": BRAND, "url": SITE_URL + "/"}},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": name, "item": SITE_URL + href}
                for i, (name, href) in enumerate(trail)]},
        ],
    }
    # "</" inside a JSON string would close the <script> element early.
    jsonld = json.dumps(graph, ensure_ascii=False).replace("</", "<\\/")
    page = _SHELL.format(
        title=_e(title), description=_e(description), canonical=_e(canonical),
        brand=_e(BRAND), site=_e(SITE_URL), adsense=ADSENSE_CLIENT, style=_STYLE,
        jsonld=jsonld, crumbs=crumb_html, body=body, footer=_footer())
    headers = _cache_headers() if cache else {"Cache-Control": "no-store"}
    return HTMLResponse(page, status_code=status, headers=headers)


# --------------------------------------------------------------------------
# Shared fragments
# --------------------------------------------------------------------------

def _path(tool: str, city: City) -> str:
    """The canonical URL for a tool in a city. The default city's page lives at
    the bare /tool URL, so /tool and /tool/new-delhi are one page to a search
    engine rather than two competing copies."""
    return f"/{tool}" if city == seo_cities.DEFAULT else f"/{tool}/{city.slug}"


def _city_links(tool: str, current: City) -> str:
    name = TOOLS[tool][0]
    items = "".join(
        f'<li><a href="{_path(tool, c)}"'
        + (' aria-current="page"' if c == current else "")
        + f'>{_e(c.name)}</a></li>'
        for c in seo_cities.CITIES)
    return f'<h2>{_e(name)} in other cities</h2><ul class="links">{items}</ul>'


def _tool_links(city: City, current: str) -> str:
    links = [(_path(t, city), f"{TOOLS[t][0]} in {city.name}") for t in TOOLS if t != current]
    if current != "kundali-milan":
        links.append(("/kundali-milan", "Kundali Milan (36 guna)"))
    links += [("/?open=muhurat", "Muhurat Finder"), ("/rashifal", "Today's Rashifal"), ("/", "Your free kundali")]
    items = "".join(f'<li><a href="{_e(h)}">{_e(t)}</a></li>' for h, t in links)
    return f'<h2>More free tools</h2><ul class="links">{items}</ul>'


def _cta(tool: str, text: str) -> str:
    """A button into the app's own tool stage (the ?open= deep link in tools.js)."""
    key = "milan" if tool == "kundali-milan" else TOOLS[tool][2]
    return f'<a class="cta" href="/?open={key}">{_e(text)}</a>'


def _not_found(tool: str, slug: str) -> HTMLResponse:
    """A real 404 status (so the URL never gets indexed) with a usable page,
    because the person who mistyped a city still wants a city."""
    name = TOOLS[tool][0]
    body = (f"<h1>{_e(name)}: city not found</h1>"
            f"<p>We don't have a page for “{_e(slug)}” yet. Pick a city below, or "
            f'<a href="/?open={TOOLS[tool][2]}">open the {_e(name)} tool</a> to use '
            "any place in the world.</p>" + _city_links(tool, seo_cities.DEFAULT))
    return _render(title=f"City not found — {BRAND}", description=f"{name} city not found.",
                   path=f"/{tool}", crumbs=[(name, f"/{tool}")], body=body,
                   status=404, cache=False)


def _limb_rows(entries: list[dict], day: dt.date, hi_names: dict | None = None) -> str:
    """'Navami until 3:54 AM (5 Oct), then Dashami' — a limb can change during
    the day, and the one that matters for an evening puja may be the second."""
    parts = []
    for i, entry in enumerate(entries):
        name = _e(entry["name"])
        if hi_names and entry["name"] in hi_names:
            name += f' <span lang="hi">({_e(hi_names[entry["name"]])})</span>'
        if entry.get("pada"):
            name += f" · pada {entry['pada']}"
        if i < len(entries) - 1:
            parts.append(f"{name} until {_time(entry['ends'], day)}")
        else:
            parts.append(("then " if i else "") + name)
    return ", ".join(parts) if parts else "—"


def _when_heading(city: City, day: dt.date, p: dict) -> str:
    vara = p["vara"]
    return (f'<p class="date">{_e(vara["weekday"])}, {_e(_long_date(day))} · '
            f'{_e(city.label)} · IST</p>')


# --------------------------------------------------------------------------
# /panchang
# --------------------------------------------------------------------------

def _panchang_page(city: City) -> HTMLResponse:
    day = _today()
    p = _panchang(city.slug, day)
    s, sun, moon, m = p["summary"], p["sun"], p["moon"], p["muhurta"]
    paksha = s["paksha"] or ""
    weekday = p["vara"]["weekday"]
    abhijit = (_span(m["abhijit"], day) if m["abhijit"]
               else "Not observed on Wednesday (Budhavara)")
    moonrise = _time(moon["rise"], day) if moon["rise"] else "No moonrise this day"
    moonset = _time(moon["set"], day) if moon["set"] else "No moonset this day"

    rows = [
        ("Vaar (weekday)", f'{_e(p["vara"]["name"])} — {_e(weekday)} '
                           f'<span lang="hi">({_e(VARA_HI.get(weekday, ""))})</span>'),
        ("Tithi", _limb_rows(p["tithi"], day, TITHI_HI)),
        ("Paksha", f'{_e(paksha)} <span lang="hi">({_e(PAKSHA_HI.get(paksha, ""))})</span>'),
        ("Nakshatra", _limb_rows(p["nakshatra"], day, NAKSHATRAS_HI)),
        ("Yoga", _limb_rows(p["yoga"], day)),
        ("Karana", _limb_rows(p["karana"], day)),
        ("Sunrise", _time(sun["rise"], day)),
        ("Sunset", _time(sun["set"], day)),
        ("Moonrise", moonrise),
        ("Moonset", moonset),
        ("Moon sign", f'{_e(moon["sign"])}'),
        ("Rahu Kaal", _span(m["rahu_kaal"], day)),
        ("Yamaganda", _span(m["yamaganda"], day)),
        ("Gulika Kaal", _span(m["gulika_kaal"], day)),
        ("Abhijit Muhurat", abhijit),
    ]
    table = "".join(f"<tr><th scope=\"row\">{_e(k)}</th><td>{v}</td></tr>" for k, v in rows)
    date_text = _long_date(day)
    title = f"Today's Panchang in {city.name}, {date_text} — Tithi, Nakshatra, Rahu Kaal | {BRAND}"
    description = (
        f"Aaj ka Panchang for {city.name} on {weekday}, {date_text}: {s['tithi']} tithi "
        f"({paksha} paksha), {s['nakshatra']} nakshatra, sunrise {_time(sun['rise'], day)}, "
        f"Rahu Kaal {_span(m['rahu_kaal'], day)}. Computed with Swiss Ephemeris.")
    body = f"""
<h1>Today's Panchang in {_e(city.name)}</h1>
<p class="hi" lang="hi">आज का पंचांग — {_e(city.name_hi)}</p>
{_when_heading(city, day, p)}
<div class="box"><p>Today in {_e(city.name)} is <strong>{_e(paksha)} {_e(s['tithi'])}</strong>
with the Moon in <strong>{_e(s['nakshatra'])}</strong> nakshatra. Rahu Kaal runs
<strong>{_span(m['rahu_kaal'], day)}</strong> — avoid starting anything new in that window.</p></div>
<div class="scroll"><table>{table}</table></div>
<p>Times are for {_e(city.label)} ({city.latitude:.4f}°N, {city.longitude:.4f}°E) in
Indian Standard Time. The panchang day runs from sunrise to the next sunrise, so a tithi
or nakshatra may end after midnight. Sunrise is the visible upper limb with refraction,
as printed in Indian almanacs; nakshatra and yoga use the Lahiri ayanamsa.</p>
{_cta("panchang", "Open the full Panchang — any city, any date")}
<h2>The five limbs of the Panchang</h2>
<p><strong>Tithi</strong> is the lunar day — each 12° the Moon gains on the Sun.
<strong>Nakshatra</strong> is the Moon's lunar mansion, one of 27. <strong>Yoga</strong> comes
from the combined longitudes of Sun and Moon, and <strong>Karana</strong> is half a tithi.
<strong>Vaar</strong> is the weekday, reckoned from sunrise. Together they are the
<span lang="hi">पंचांग</span> (“five limbs”) consulted before any auspicious work.</p>
{_city_links("panchang", city)}
{_tool_links(city, "panchang")}"""
    return _render(title=title, description=description, path=_path("panchang", city),
                   crumbs=[("Panchang", "/panchang")]
                   + ([(city.name, _path("panchang", city))] if city != seo_cities.DEFAULT else []),
                   body=body)


@router.get("/panchang", response_class=HTMLResponse)
def panchang_default() -> HTMLResponse:
    return _panchang_page(seo_cities.DEFAULT)


@router.get("/panchang/{slug}", response_class=HTMLResponse)
def panchang_city(slug: str) -> HTMLResponse:
    city = seo_cities.get(slug)
    return _panchang_page(city) if city else _not_found("panchang", slug)


# --------------------------------------------------------------------------
# /rahu-kaal
# --------------------------------------------------------------------------

def _rahu_page(city: City) -> HTMLResponse:
    day = _today()
    p = _panchang(city.slug, day)
    m, sun = p["muhurta"], p["sun"]
    weekday = p["vara"]["weekday"]

    # A week ahead: the most-asked follow-up ("what about tomorrow?") answered
    # on the page itself. Seven ~10 ms computations, all cached.
    week = []
    for offset in range(7):
        d = day + dt.timedelta(days=offset)
        q = _panchang(city.slug, d)
        week.append(f"<tr><td>{_e(q['vara']['weekday'])}<small>{d.day} {d.strftime('%b')}</small></td>"
                    f"<td>{_span(q['muhurta']['rahu_kaal'], d)}</td>"
                    f"<td>{_span(q['muhurta']['yamaganda'], d)}</td>"
                    f"<td>{_span(q['muhurta']['gulika_kaal'], d)}</td></tr>")

    date_text = _long_date(day)
    rahu = _span(m["rahu_kaal"], day)
    title = f"Rahu Kaal Today in {city.name} — {rahu}, {date_text} | {BRAND}"
    description = (
        f"Rahu Kaal today in {city.name} ({weekday}, {date_text}) is {rahu}. "
        f"Also Yamaganda {_span(m['yamaganda'], day)} and Gulika {_span(m['gulika_kaal'], day)}, "
        f"with this week's timings and what Rahu Kaal means.")
    body = f"""
<h1>Rahu Kaal Today in {_e(city.name)}</h1>
<p class="hi" lang="hi">आज का राहु काल — {_e(city.name_hi)}</p>
{_when_heading(city, day, p)}
<div class="scroll"><table>
<tr><th scope="row">Rahu Kaal <span lang="hi">(राहु काल)</span></th><td class="bad"><strong>{rahu}</strong></td></tr>
<tr><th scope="row">Yamaganda <span lang="hi">(यमगण्ड)</span></th><td>{_span(m['yamaganda'], day)}</td></tr>
<tr><th scope="row">Gulika Kaal <span lang="hi">(गुलिक काल)</span></th><td>{_span(m['gulika_kaal'], day)}</td></tr>
<tr><th scope="row">Abhijit Muhurat</th><td class="good">{_span(m['abhijit'], day) if m['abhijit'] else 'Not observed on Wednesday'}</td></tr>
<tr><th scope="row">Sunrise / Sunset</th><td>{_time(sun['rise'], day)} / {_time(sun['set'], day)}</td></tr>
</table></div>
{_cta("rahu-kaal", "Check Rahu Kaal for any city or date")}
<h2>What is Rahu Kaal?</h2>
<p>Rahu Kaal (<span lang="hi">राहु काल</span>) is a period of roughly an hour and a half each day
that is traditionally held to be ruled by Rahu, the north lunar node. Daylight — sunrise to
sunset — is divided into eight equal parts, and one of them belongs to Rahu. Which part
depends on the weekday: the 8th on Sunday, 2nd on Monday, 7th on Tuesday, 5th on Wednesday,
6th on Thursday, 4th on Friday and 3rd on Saturday.</p>
<p>Because it follows the real sunrise and sunset, Rahu Kaal is different in every city and
shifts through the year — which is why a fixed “Monday 7:30–9:00” chart is only an
approximation. By custom, people avoid beginning new ventures, signing agreements, starting
journeys or making major purchases during Rahu Kaal; work already under way can continue.
Yamaganda and Gulika Kaal are two further eighths of the day treated with similar caution.</p>
<h2>Rahu Kaal in {_e(city.name)} this week</h2>
<div class="scroll"><table>
<tr><th>Day</th><th>Rahu Kaal</th><th>Yamaganda</th><th>Gulika</th></tr>
{''.join(week)}
</table></div>
{_city_links("rahu-kaal", city)}
{_tool_links(city, "rahu-kaal")}"""
    return _render(title=title, description=description, path=_path("rahu-kaal", city),
                   crumbs=[("Rahu Kaal", "/rahu-kaal")]
                   + ([(city.name, _path("rahu-kaal", city))] if city != seo_cities.DEFAULT else []),
                   body=body)


@router.get("/rahu-kaal", response_class=HTMLResponse)
def rahu_default() -> HTMLResponse:
    return _rahu_page(seo_cities.DEFAULT)


@router.get("/rahu-kaal/{slug}", response_class=HTMLResponse)
def rahu_city(slug: str) -> HTMLResponse:
    city = seo_cities.get(slug)
    return _rahu_page(city) if city else _not_found("rahu-kaal", slug)


# --------------------------------------------------------------------------
# /choghadiya
# --------------------------------------------------------------------------

def choghadiya_slots(p: dict) -> tuple[list[dict], list[dict]]:
    """Day and night choghadiya from a `daily_panchang` result.

    The sequences and meanings come from astro/choghadiya.py; the boundaries
    deliberately do NOT. That engine estimates sunrise from a seasonal formula
    (it was ~35 minutes early for Delhi in October 2026), while this page sits
    one link away from a Panchang page printing the ephemeris sunrise. Cutting
    the day at the same sunrise and sunset keeps the two pages consistent.
    """
    rise, sset, next_rise = (_local(p["sun"][k]) for k in ("rise", "set", "next_rise"))
    if not (rise and sset and next_rise):
        return [], []
    vara = p["vara"]["index"]                          # Sunday = 0, as choghadiya.py uses

    def run(names: list[str], start: dt.datetime, end: dt.datetime) -> list[dict]:
        step = (end - start) / 8
        return [{"name": n, "start": start + i * step, "end": start + (i + 1) * step,
                 **chog.CHOGHADIYA_INFO[n]} for i, n in enumerate(names)]

    return (run(chog.DAY_SEQUENCE[vara], rise, sset),
            run(chog.NIGHT_SEQUENCE[vara], sset, next_rise))


def _chog_table(slots: list[dict], day: dt.date) -> str:
    rows = []
    for s in slots:
        cls = {"auspicious": "good", "inauspicious": "bad"}.get(s["quality"], "")
        when = f"{_time(s['start'].isoformat(), day)} – {_time(s['end'].isoformat(), day)}"
        rows.append(
            f"<tr><td>{when}</td>"
            f'<td class="{cls}"><strong>{_e(s["name"])}</strong> '
            f'<span lang="hi">({_e(s["name_hi"])})</span><small>{_e(s["ruler"])}</small></td>'
            f"<td>{_e(s['quality'].capitalize())}<small>{_e(s['description'])}</small></td></tr>")
    return ('<div class="scroll"><table><tr><th>Time</th><th>Choghadiya</th><th>Nature</th></tr>'
            + "".join(rows) + "</table></div>")


def _choghadiya_page(city: City) -> HTMLResponse:
    day = _today()
    p = _panchang(city.slug, day)
    day_slots, night_slots = choghadiya_slots(p)
    weekday = p["vara"]["weekday"]
    date_text = _long_date(day)
    good = [s for s in day_slots if s["quality"] == "auspicious"]
    first_good = (f"{good[0]['name']} from {_time(good[0]['start'].isoformat(), day)}"
                  if good else "none")
    title = f"Choghadiya Today in {city.name}, {date_text} — Day & Night Timings | {BRAND}"
    description = (
        f"Today's choghadiya for {city.name} ({weekday}, {date_text}): all 16 day and night "
        f"muhurtas — Amrit, Shubh, Labh, Char, Rog, Kaal, Udveg — with exact start and end "
        f"times from sunrise {_time(p['sun']['rise'], day)}.")
    body = f"""
<h1>Choghadiya Today in {_e(city.name)}</h1>
<p class="hi" lang="hi">आज का चौघड़िया — {_e(city.name_hi)}</p>
{_when_heading(city, day, p)}
<div class="box"><p>Sunrise <strong>{_time(p['sun']['rise'], day)}</strong>, sunset
<strong>{_time(p['sun']['set'], day)}</strong>. First auspicious daytime choghadiya:
<strong>{_e(first_good)}</strong>.</p></div>
<h2>Day Choghadiya <span lang="hi">(दिन का चौघड़िया)</span></h2>
{_chog_table(day_slots, day)}
<h2>Night Choghadiya <span lang="hi">(रात का चौघड़िया)</span></h2>
{_chog_table(night_slots, day)}
{_cta("choghadiya", "Open the live Choghadiya clock")}
<h2>How choghadiya works</h2>
<p>The day from sunrise to sunset, and the night from sunset to the next sunrise, are each
divided into eight equal parts called choghadiya (<span lang="hi">चौघड़िया</span>, “four
ghadis”). Each is ruled by a planet and named for its nature: <strong>Amrit</strong>,
<strong>Shubh</strong> and <strong>Labh</strong> are auspicious, <strong>Char</strong> is
neutral and good for travel, while <strong>Rog</strong>, <strong>Kaal</strong> and
<strong>Udveg</strong> are avoided for new beginnings. The order starts from the weekday's
ruler, so it changes every day — and the length of each slot follows the real day length in
{_e(city.name)}.</p>
{_city_links("choghadiya", city)}
{_tool_links(city, "choghadiya")}"""
    return _render(title=title, description=description, path=_path("choghadiya", city),
                   crumbs=[("Choghadiya", "/choghadiya")]
                   + ([(city.name, _path("choghadiya", city))] if city != seo_cities.DEFAULT else []),
                   body=body)


@router.get("/choghadiya", response_class=HTMLResponse)
def choghadiya_default() -> HTMLResponse:
    return _choghadiya_page(seo_cities.DEFAULT)


@router.get("/choghadiya/{slug}", response_class=HTMLResponse)
def choghadiya_city(slug: str) -> HTMLResponse:
    city = seo_cities.get(slug)
    return _choghadiya_page(city) if city else _not_found("choghadiya", slug)


# --------------------------------------------------------------------------
# /kundali-milan
# --------------------------------------------------------------------------

# (key, English name, points, what it measures). Points and Hindi labels are
# checked against astro/matching.py by the test, so this text cannot drift
# from what the matching tool actually scores.
KOOTAS = (
    ("varna", "Varna", 1, "Spiritual and working temperament, from the Moon sign's varna. "
     "Full point when the groom's varna is not below the bride's."),
    ("vashya", "Vashya", 2, "Mutual attraction and influence — which sign “draws” the other."),
    ("tara", "Tara", 3, "Health and wellbeing, from the count between the two birth "
     "nakshatras; the 3rd, 5th and 7th taras are unfavourable."),
    ("yoni", "Yoni", 4, "Physical and intimate compatibility; each nakshatra has an animal yoni, "
     "and sworn-enemy animals score zero."),
    ("graha_maitri", "Graha Maitri", 5, "Friendship between the lords of the two Moon signs — "
     "the mental wavelength of the couple."),
    ("gana", "Gana", 6, "Temperament: Deva (divine), Manushya (human) or Rakshasa (fierce)."),
    ("bhakoot", "Bhakoot", 7, "The relative placement of the two Moon signs. The 2/12, 5/9 and "
     "6/8 positions form Bhakoot dosha, cancelled when the sign lords are the same or friends."),
    ("nadi", "Nadi", 8, "The highest-weighted koota, tied to health and progeny. The same nadi "
     "for both is Nadi dosha, with classical cancellations for the same sign/different "
     "nakshatra or same nakshatra/different pada."),
)


@router.get("/kundali-milan", response_class=HTMLResponse)
def kundali_milan() -> HTMLResponse:
    rows = "".join(
        f"<tr><td><strong>{_e(name)}</strong> "
        f'<span lang="hi">({_e(matching.KOOTA_LABELS_HI[key])})</span></td>'
        f"<td>{pts}</td><td>{_e(text)}</td></tr>"
        for key, name, pts, text in KOOTAS)
    total = int(matching.MAXIMUM_POINTS)
    # The bands are read straight from the engine's table (upper bounds are
    # exclusive ceilings, the last one 36.01), so the page and the verdict the
    # tool prints can never disagree.
    bands, low = [], 0
    for ceiling, verdict, _detail in matching.SCORE_BANDS:
        top = min(math.ceil(ceiling) - 1, total)
        rng = f"Below {top + 1}" if low == 0 else f"{low}–{top}"
        bands.append(f"<tr><td>{rng}</td><td>{_e(verdict.capitalize())}</td></tr>")
        low = top + 1
    ordinals = [f"{h}{'st' if h == 1 else 'nd' if h == 2 else 'th'}" for h in matching.MANGAL_HOUSES]
    houses = ", ".join(ordinals[:-1]) + " or " + ordinals[-1]
    title = f"Kundali Milan — Ashtakoot Guna Milan ({total} Gun) Explained | {BRAND}"
    description = (
        f"How Kundali Milan works: the 8 kootas of Ashtakoot Guna Milan, {total} points, what "
        "score is good for marriage, and how Mangal Dosha is checked. Free online matching "
        "in English and Hindi.")
    body = f"""
<h1>Kundali Milan: Ashtakoot Guna Milan explained</h1>
<p class="hi" lang="hi">कुंडली मिलान — अष्टकूट गुण मिलान ({total} गुण)</p>
<p>Kundali Milan (<span lang="hi">कुंडली मिलान</span>) is the traditional Vedic way of checking
marriage compatibility. The most widely used method in North India is <strong>Ashtakoot Guna
Milan</strong>: eight factors (<em>kootas</em>) are compared between the bride's and groom's
charts and scored out of <strong>{total} points (gunas)</strong>. Every one of them is read from
the <strong>Moon</strong> — its sign (rashi) and its nakshatra at birth — which is why
the score needs an accurate birth date and place, but barely depends on the birth time.</p>
{_cta("kundali-milan", "Match two kundalis now — free")}
<h2>The 8 kootas and their points</h2>
<div class="scroll"><table><tr><th>Koota</th><th>Points</th><th>What it measures</th></tr>
{rows}
<tr><td><strong>Total</strong></td><td><strong>{total}</strong></td><td></td></tr></table></div>
<h2>What is a good Guna Milan score?</h2>
<div class="scroll"><table><tr><th>Gunas</th><th>Conventional reading</th></tr>{''.join(bands)}</table></div>
<p>18 is the conventional minimum. The total alone is not the whole story: a high score with an
uncancelled Nadi or Bhakoot dosha is read with caution, and a modest score with strong
Graha Maitri and no doshas is often considered workable. These bands are a convention with a
long history, not a measurement — they are guidance, not a verdict on a relationship.</p>
<h2>Mangal Dosha (Manglik)</h2>
<p>Mangal Dosha is checked separately from the 36 points. A chart is Manglik when Mars sits in
the {houses} house counted from the <strong>Lagna</strong> (ascendant), the
<strong>Moon</strong> or <strong>Venus</strong>. Classical texts exempt certain sign
placements (for example Mars in its own sign Aries in the 1st), and Jupiter's aspect on Mars
is held to soften it. When <strong>both</strong> partners are Manglik the dosha is
conventionally treated as mutually cancelled — which is why Manglik matches are made with
Manglik partners. Because it depends on the Lagna, Mangal Dosha does need a reliable birth
time.</p>
<h2>How our matching tool works</h2>
<p>Enter both people's date, time and place of birth. Both charts are cast with the sidereal
zodiac (Lahiri ayanamsa) from the Swiss Ephemeris, and each koota is scored by table lookup
from the classical tables, with every cancellation named. You get the full {total}-point
breakdown and both partners' Mangal Dosha status, in English or
<span lang="hi">हिन्दी</span>, free and without signing up.</p>
{_cta("kundali-milan", "Open Kundali Milan")}
{_tool_links(seo_cities.DEFAULT, "kundali-milan")}"""
    return _render(title=title, description=description, path="/kundali-milan",
                   crumbs=[("Kundali Milan", "/kundali-milan")], body=body)


# --------------------------------------------------------------------------
# sitemap.xml and robots.txt
# --------------------------------------------------------------------------

STATIC_PATHS = ("/", "/kundali-milan", "/terms", "/privacy", "/refund", "/contact")


def sitemap_paths() -> list[str]:
    """Every public URL we want indexed, canonical form only."""
    paths = list(STATIC_PATHS)
    for tool in TOOLS:
        paths += [_path(tool, c) for c in seo_cities.CITIES]
    from .rashifal_pages import sitemap_paths as rashifal_paths  # lazy: it imports this module
    return paths + rashifal_paths()


@router.get("/sitemap.xml")
def sitemap() -> Response:
    today = _today().isoformat()
    urls = []
    for path in sitemap_paths():
        fields = f"<loc>{xml_escape(SITE_URL + path)}</loc>"
        # The tool pages genuinely change every day; the legal pages and the
        # explainer do not, and claiming they do only teaches crawlers to
        # ignore our lastmod.
        if path.split("/")[1] in TOOLS:
            fields += f"<lastmod>{today}</lastmod><changefreq>daily</changefreq>"
        if path == "/":
            fields += "<priority>1.0</priority>"
        elif path.strip("/") in TOOLS:
            fields += "<priority>0.9</priority>"
        urls.append(f"<url>{fields}</url>")
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + "\n".join(urls) + "\n</urlset>\n")
    return Response(xml, media_type="application/xml",
                    headers={"Cache-Control": "public, max-age=3600"})


@router.get("/robots.txt")
def robots() -> PlainTextResponse:
    """Crawl everything public; keep crawlers out of the JSON API (no value to a
    searcher, real cost to us) and the operator console."""
    body = ("User-agent: *\n"
            "Disallow: /api/\n"
            "Disallow: /admin\n"
            "Allow: /\n\n"
            f"Sitemap: {SITE_URL}/sitemap.xml\n")
    return PlainTextResponse(body, headers={"Cache-Control": "public, max-age=3600"})
