"""Server-rendered public pages for the free tools, plus sitemap.xml and robots.txt.

Why these exist (DIVASTRO-100): the app is one single-page shell at `/`, so a
search engine sees one URL and a page of buttons. Panchang, Rahu Kaal and
Choghadiya are what people in India search for every morning, and none of it
was indexable. Each page here carries its content in the raw HTML — no script
has to run for a crawler (or a slow phone) to read today's tithi or Rahu Kaal.

DIVASTRO-106 added a full Hindi copy of every page under /hi/ (most of this
audience searches in Hindi), ~100 cities, and /free-kundali. Every page names
its other-language twin with reciprocal hreflang links and a visible switch.
The Hindi pages are written in Hindi, not machine-translated wrappers around
English: the limb names come from the same Hindi tables the app uses.

Everything shown is computed by the same engines the app uses
(`astro.panchang.daily_panchang` for the five limbs and the muhurta windows), so
a page can never disagree with the tool it links to on those numbers. Festival
names are deliberately NOT shown: `daily_panchang` reports the sunrise tithi,
which is the wrong rule for aparahna/pradosh-vyapini festivals (the 1-day-off
bug fixed in DIVASTRO-90 by separate helpers) — only the daily elements, which
the sunrise rule does get right, appear here.

Muhurat-of-the-year pages (vivah/griha pravesh 2026) were considered for
DIVASTRO-106 and deliberately not built: `astro.muhurat.find_muhurat` scores a
day on its sunrise tithi, nakshatra, vara, yoga and Bhadra only. It has no
notion of Chaturmas, Kharmas/Malmas, Pitru Paksha or Guru/Shukra asta, so it
rates ~10 days in every month of 2026 "Auspicious" for marriage — including
August to mid-November and mid-December to mid-January, when no Hindu
almanac lists a vivah muhurat. Fine as an in-app filter; wrong as a public list.

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
# The Hindi limb names: one copy, shared with main.py, muhurat.py and /api/panchang.
from .astro.names_hi import KARANA_HI, NAKSHATRAS_HI, TITHI_HI, VARA_HI, YOGA_HI
from .astro.vargas import DEFAULT_DIVISIONS
from .legal import ADDRESS, BRAND, EMAIL, LEGAL_NAME, PHONE, SITE, registration_inline
from .seo_cities import City

router = APIRouter()

IST = ZoneInfo("Asia/Kolkata")
SITE_URL = SITE.rstrip("/")

# Same publisher as index.html. main.py owns ADSENSE_PUBLISHER for /ads.txt but
# importing main from here would be circular; tests/test_seo_pages.py checks
# the two agree.
ADSENSE_CLIENT = "ca-pub-1593974697916149"

EN, HI = "en", "hi"

# Tool slug -> (display name, Hindi name, the `?open=` key app.js deep-links to).
TOOLS = {
    "panchang": ("Panchang", "पंचांग", "panchang"),
    "rahu-kaal": ("Rahu Kaal", "राहु काल", "panchang"),
    "choghadiya": ("Choghadiya", "चौघड़िया", "choghadiya"),
}

PAKSHA_HI = {"Shukla": "शुक्ल पक्ष", "Krishna": "कृष्ण पक्ष"}

MONTHS_HI = ("जनवरी", "फ़रवरी", "मार्च", "अप्रैल", "मई", "जून", "जुलाई", "अगस्त",
             "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर")


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


@functools.lru_cache(maxsize=2048)
def _panchang(slug: str, day: dt.date) -> dict:
    """One city's almanac for one day. ~10 ms to compute, so this is not about
    a single visitor — it keeps a crawler walking all ~700 URLs, or a burst of
    WhatsApp shares, from recomputing the same day hundreds of times. Keyed on
    the date, so entries simply stop being asked for after midnight and age
    out of the LRU. Sized for every city's 7-day Rahu Kaal week (~114 x 7).
    The English and Hindi pages share an entry. Callers must treat the dict
    as read-only."""
    city = seo_cities.BY_SLUG[slug]
    return panchang_engine.daily_panchang(day, city.latitude, city.longitude, city.timezone)


def _local(iso: str | None) -> dt.datetime | None:
    return dt.datetime.fromisoformat(iso).astimezone(IST) if iso else None


def _clock(moment: dt.datetime, lang: str = EN) -> str:
    """'6:29 AM', or in Hindi 'सुबह 6:29' — the part-of-day word is how times
    are said and printed in Hindi almanacs, and reads better than AM/PM."""
    hm = moment.strftime("%I:%M").lstrip("0")
    if lang == HI:
        h = moment.hour
        part = ("रात" if h < 4 or h >= 20 else "सुबह" if h < 12
                else "दोपहर" if h < 16 else "शाम")
        return f"{part} {hm}"
    return f"{hm} {moment.strftime('%p')}"


def _short_date(day: dt.date, lang: str = EN) -> str:
    return f"{day.day} {MONTHS_HI[day.month - 1] if lang == HI else day.strftime('%b')}"


def _time(iso: str | None, day: dt.date, lang: str = EN) -> str:
    """'6:29 AM', with the date added when it falls on another civil day —
    tithis and moonrise routinely do, and a bare '1:18 AM' would read as this
    morning rather than tonight."""
    moment = _local(iso)
    if moment is None:
        return "—"
    text = _clock(moment, lang)
    if moment.date() != day:
        text += f" ({_short_date(moment.date(), lang)})"
    return text


def _span(window: dict | None, day: dt.date, lang: str = EN) -> str:
    if not window:
        return "—"
    return f"{_time(window['start'], day, lang)} – {_time(window['end'], day, lang)}"


def _long_date(day: dt.date, lang: str = EN) -> str:
    if lang == HI:
        return f"{day.day} {MONTHS_HI[day.month - 1]} {day.year}"
    return f"{day.day} {day.strftime('%B %Y')}"


# --------------------------------------------------------------------------
# Page shell
# --------------------------------------------------------------------------

_STYLE = """
  body { overflow: auto; display: block; }
  .seo { max-width: 820px; margin: 0 auto; padding: 22px 16px 40px; }
  .seo .top { display: flex; justify-content: space-between; align-items: baseline;
              gap: 12px; margin-bottom: 14px; }
  .seo .back { display: inline-block; color: var(--ink-faint);
               font-size: 13px; text-decoration: none; }
  .seo .lang-switch { font-size: 13.5px; padding: 4px 12px; border: 1px solid var(--line);
                      border-radius: 999px; text-decoration: none; white-space: nowrap; }
  .seo .crumbs { font-size: 12.5px; color: var(--ink-faint); margin: 0 0 10px; }
  .seo .crumbs a { color: var(--ink-faint); }
  .seo h1 { font-family: var(--serif); font-weight: 400; font-size: 27px; line-height: 1.25;
            color: var(--gold-soft); margin: 0 0 4px; }
  .seo .hi { font-size: 18px; color: var(--gold); margin: 0 0 6px; }
  .seo .date { font-family: var(--mono); font-size: 13px; color: var(--ink-faint); margin: 0 0 18px; }
  .seo h2 { font-family: var(--serif); font-weight: 400; font-size: 20px; color: var(--gold);
            margin: 28px 0 10px; }
  .seo h3 { font-size: 16px; color: var(--ink); margin: 18px 0 6px; }
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
  .seo .cta.big { font-size: 18px; padding: 18px 20px; }
  .seo .links { display: flex; flex-wrap: wrap; gap: 8px; padding: 0; margin: 0; list-style: none; }
  .seo .links a { display: inline-block; padding: 6px 12px; border: 1px solid var(--line);
                  border-radius: 999px; font-size: 13.5px; text-decoration: none;
                  color: var(--ink-dim); }
  .seo .links a[aria-current] { color: var(--gold); border-color: var(--gold); }
  .seo dl.cities { margin: 0; }
  .seo dl.cities dt { font-size: 12.5px; color: var(--ink-faint); margin: 14px 0 6px;
                      letter-spacing: .03em; }
  .seo dl.cities dd { margin: 0; }
  .seo .faq h3 { margin-top: 20px; }
  .site-footer { margin: 30px auto 0; }
  @media (min-width: 640px) { .seo { padding-top: 40px; } .seo h1 { font-size: 32px; } }
"""

_SHELL = """<!DOCTYPE html>
<html lang="{html_lang}"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{title}</title>
<meta name="description" content="{description}"/>
<link rel="canonical" href="{canonical}"/>
{alternates}<meta property="og:type" content="website"/>
<meta property="og:site_name" content="{brand}"/>
<meta property="og:title" content="{title}"/>
<meta property="og:description" content="{description}"/>
<meta property="og:url" content="{canonical}"/>
<meta property="og:image" content="{site}/static/icon-512.png"/>
<meta property="og:locale" content="{og_locale}"/>
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
  {share}<div class="top"><a class="back" href="{home}">&larr; {brand}</a>{switch}</div>
  <nav class="crumbs" aria-label="{crumb_label}">{crumbs}</nav>
  {body}
</main>
{footer}
</body></html>"""


def _share(path: str) -> str:
    """DIVASTRO-107: a plain wa.me "Share on WhatsApp" link, UTM-tagged (see share.py)."""
    from .share import seo_share
    return seo_share(path)


def _footer(lang: str = EN) -> str:
    """The same public footer as index.html — the links AdSense and payment
    underwriters look for, from the same constants the legal pages use. The
    legal pages themselves are English-only, so the Hindi footer translates
    the link text but points at the same pages."""
    reg = registration_inline()
    if lang == HI:
        labels = ("नियम और शर्तें", "गोपनीयता नीति", "रिफ़ंड और रद्दीकरण", "संपर्क करें", "सुझाव")
        disclaimer = ("ज्योतिषीय जानकारी मार्गदर्शन और मनोरंजन के लिए है। यह चिकित्सा, "
                      "कानूनी या वित्तीय सलाह नहीं है।")
    else:
        labels = ("Terms &amp; Conditions", "Privacy Policy", "Refund &amp; Cancellation",
                  "Contact Us", "Feedback")
        disclaimer = ("Astrological readings are provided for guidance and\n    entertainment. "
                      "They are not medical, legal or financial advice.")
    links = "\n    ".join(f'<a href="{href}">{label}</a>' for href, label in zip(
        ("/terms", "/privacy", "/refund", "/contact", "/feedback"), labels))
    return f"""<footer class="site-footer">
  <nav>
    {links}
  </nav>
  <p class="legal-entity">{_e(LEGAL_NAME)} · {_e(ADDRESS)} ·
    <a href="mailto:{_e(EMAIL)}">{_e(EMAIL)}</a> · {_e(PHONE)}</p>
  {f'<p class="legal-entity registrations">{_e(reg)}</p>' if reg else ''}
  <p class="disclaimer">{disclaimer}</p>
</footer>"""


def _alternates(en_path: str, hi_path: str) -> str:
    """Reciprocal hreflang: both copies carry the identical set, which is what
    makes Google treat them as one page in two languages rather than two
    competing pages (a one-way hreflang is ignored)."""
    return "".join(
        f'<link rel="alternate" hreflang="{code}" href="{_e(SITE_URL + p)}"/>\n'
        for code, p in (("en", en_path), ("hi", hi_path), ("x-default", en_path)))


def _render(*, title: str, description: str, path: str, crumbs: list[tuple[str, str]],
            body: str, lang: str = EN, alt: str | None = None, extra_ld: tuple = (),
            status: int = 200, cache: bool = True) -> HTMLResponse:
    """`path` is this page's canonical path; `alt` its other-language twin
    (None for pages with no twin, i.e. the 404s)."""
    hi = lang == HI
    canonical = SITE_URL + path
    trail = [("होम" if hi else "Home", "/")] + crumbs
    crumb_html = " › ".join(
        f'<a href="{_e(href)}">{_e(name)}</a>' if i < len(trail) - 1 else _e(name)
        for i, (name, href) in enumerate(trail))
    graph = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "WebPage", "name": title, "description": description,
             "url": canonical, "inLanguage": "hi-IN" if hi else "en-IN",
             "dateModified": _today().isoformat(),
             "isPartOf": {"@type": "WebSite", "name": BRAND, "url": SITE_URL + "/"}},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": name, "item": SITE_URL + href}
                for i, (name, href) in enumerate(trail)]},
            *extra_ld,
        ],
    }
    # "</" inside a JSON string would close the <script> element early.
    jsonld = json.dumps(graph, ensure_ascii=False).replace("</", "<\\/")
    alternates, switch = "", ""
    if alt:
        en_path, hi_path = (alt, path) if hi else (path, alt)
        alternates = _alternates(en_path, hi_path)
        switch = (f'<a class="lang-switch" href="{_e(alt)}" hreflang="en" lang="en">Read in English</a>'
                  if hi else
                  f'<a class="lang-switch" href="{_e(alt)}" hreflang="hi" lang="hi">हिन्दी में पढ़ें</a>')
    page = _SHELL.format(
        html_lang="hi" if hi else "en-IN", og_locale="hi_IN" if hi else "en_IN",
        title=_e(title), description=_e(description), canonical=_e(canonical),
        alternates=alternates, switch=switch, home="/?lang=hi" if hi else "/",
        crumb_label="ब्रेडक्रंब" if hi else "Breadcrumb",
        brand=_e(BRAND), site=_e(SITE_URL), adsense=ADSENSE_CLIENT, style=_STYLE,
        jsonld=jsonld, crumbs=crumb_html, body=body, footer=_footer(lang),
        share=_share(path) if status == 200 else "")
    headers = _cache_headers() if cache else {"Cache-Control": "no-store"}
    return HTMLResponse(page, status_code=status, headers=headers)


# --------------------------------------------------------------------------
# Shared fragments
# --------------------------------------------------------------------------

def _prefix(lang: str) -> str:
    return "/hi" if lang == HI else ""


def _path(tool: str, city: City, lang: str = EN) -> str:
    """The canonical URL for a tool in a city. The default city's page lives at
    the bare /tool URL, so /tool and /tool/new-delhi are one page to a search
    engine rather than two competing copies. Hindi copies live under /hi/."""
    bare = f"/{tool}" if city == seo_cities.DEFAULT else f"/{tool}/{city.slug}"
    return _prefix(lang) + bare


def _app_link(key: str, lang: str = EN) -> str:
    """A deep link into the app (tools.js handles ?open=, app.js ?lang=)."""
    return f"/?open={key}" + ("&lang=hi" if lang == HI else "")


def _city_links(tool: str, current: City, lang: str = EN) -> str:
    """Every city, grouped by state — ~100 pills in one cloud is unusable."""
    hi = lang == HI
    groups = []
    for state, cities in seo_cities.by_state():
        items = "".join(
            f'<li><a href="{_path(tool, c, lang)}"'
            + (' aria-current="page"' if c == current else "")
            + f'>{_e(c.name_hi if hi else c.name)}</a></li>'
            for c in cities)
        label = seo_cities.STATE_HI[state] if hi else state
        groups.append(f'<dt>{_e(label)}</dt><dd><ul class="links">{items}</ul></dd>')
    heading = f"अन्य शहरों में {TOOLS[tool][1]}" if hi else f"{TOOLS[tool][0]} in other cities"
    return f'<h2>{_e(heading)}</h2><dl class="cities">{"".join(groups)}</dl>'


def _tool_links(city: City, current: str, lang: str = EN) -> str:
    if lang == HI:
        links = [(_path(t, city, HI), f"{city.name_hi} का {TOOLS[t][1]}")
                 for t in TOOLS if t != current]
        if current != "kundali-milan":
            links.append(("/hi/kundali-milan", "कुंडली मिलान (36 गुण)"))
        if current != "free-kundali":
            links.append(("/hi/free-kundali", "मुफ़्त जन्म कुंडली"))
        links.append((_app_link("muhurat", HI), "मुहूर्त खोजें"))
        links.append(("/hi/rashifal", "आज का राशिफल"))
        links.append(("/hi/vrat-tyohar", "आज के व्रत और त्योहार"))
        heading = "और मुफ़्त टूल"
    else:
        links = [(_path(t, city), f"{TOOLS[t][0]} in {city.name}") for t in TOOLS if t != current]
        if current != "kundali-milan":
            links.append(("/kundali-milan", "Kundali Milan (36 guna)"))
        if current != "free-kundali":
            links.append(("/free-kundali", "Free Janam Kundali"))
        links.append(("/?open=muhurat", "Muhurat Finder"))
        links.append(("/rashifal", "Today's Rashifal"))
        links.append(("/vrat-tyohar", "Today's Vrat & Festivals"))
        heading = "More free tools"
    items = "".join(f'<li><a href="{_e(h)}">{_e(t)}</a></li>' for h, t in links)
    return f'<h2>{heading}</h2><ul class="links">{items}</ul>'


def _cta(tool: str, text: str, lang: str = EN, big: bool = False) -> str:
    """A button into the app's own tool stage (the ?open= deep link in tools.js)."""
    key = {"kundali-milan": "milan", "free-kundali": "kundali"}.get(tool) or TOOLS[tool][2]
    cls = "cta big" if big else "cta"
    return f'<a class="{cls}" href="{_e(_app_link(key, lang))}">{_e(text)}</a>'


def _not_found(tool: str, slug: str, lang: str = EN) -> HTMLResponse:
    """A real 404 status (so the URL never gets indexed) with a usable page,
    because the person who mistyped a city still wants a city."""
    name_en, name_hi, key = TOOLS[tool]
    base = _prefix(lang) + f"/{tool}"
    if lang == HI:
        body = (f"<h1>{_e(name_hi)}: शहर नहीं मिला</h1>"
                f"<p>“{_e(slug)}” के लिए अभी हमारे पास पेज नहीं है। नीचे से अपना शहर चुनें, या "
                f'<a href="{_e(_app_link(key, HI))}">{_e(name_hi)} टूल खोलें</a> — उसमें दुनिया की '
                "कोई भी जगह चुनी जा सकती है।</p>" + _city_links(tool, seo_cities.DEFAULT, HI))
        title, desc = f"शहर नहीं मिला — {BRAND}", f"{name_hi}: यह शहर हमारी सूची में नहीं है।"
        crumbs = [(name_hi, base)]
    else:
        body = (f"<h1>{_e(name_en)}: city not found</h1>"
                f"<p>We don't have a page for “{_e(slug)}” yet. Pick a city below, or "
                f'<a href="/?open={key}">open the {_e(name_en)} tool</a> to use '
                "any place in the world.</p>" + _city_links(tool, seo_cities.DEFAULT))
        title, desc = f"City not found — {BRAND}", f"{name_en} city not found."
        crumbs = [(name_en, base)]
    return _render(title=title, description=desc, path=base, crumbs=crumbs, body=body,
                   lang=lang, status=404, cache=False)


def _limb_rows(entries: list[dict], day: dt.date, hi_names: dict | None = None,
               lang: str = EN) -> str:
    """'Navami until 3:54 AM (5 Oct), then Dashami' — a limb can change during
    the day, and the one that matters for an evening puja may be the second.
    In Hindi the name itself is Hindi: 'नवमी रात 3:54 (5 अक्टूबर) तक, फिर दशमी'."""
    hi = lang == HI
    parts = []
    for i, entry in enumerate(entries):
        if hi:
            name = _e((hi_names or {}).get(entry["name"], entry["name"]))
        else:
            name = _e(entry["name"])
            if hi_names and entry["name"] in hi_names:
                name += f' <span lang="hi">({_e(hi_names[entry["name"]])})</span>'
        if entry.get("pada"):
            name += f" · {'पाद' if hi else 'pada'} {entry['pada']}"
        if i < len(entries) - 1:
            until = _time(entry['ends'], day, lang)
            parts.append(f"{name} {until} तक" if hi else f"{name} until {until}")
        else:
            parts.append((("फिर " if hi else "then ") if i else "") + name)
    return ", ".join(parts) if parts else "—"


def _when_heading(city: City, day: dt.date, p: dict, lang: str = EN) -> str:
    weekday = p["vara"]["weekday"]
    if lang == HI:
        return (f'<p class="date">{_e(VARA_HI.get(weekday, weekday))}, {_e(_long_date(day, HI))} · '
                f'{_e(city.name_hi)}, {_e(seo_cities.STATE_HI.get(city.state, city.state))} · IST</p>')
    return (f'<p class="date">{_e(weekday)}, {_e(_long_date(day))} · '
            f'{_e(city.label)} · IST</p>')


def _tool_crumbs(tool: str, city: City, lang: str = EN) -> list[tuple[str, str]]:
    hi = lang == HI
    name = TOOLS[tool][1 if hi else 0]
    crumbs = [(name, _prefix(lang) + f"/{tool}")]
    if city != seo_cities.DEFAULT:
        crumbs.append((city.name_hi if hi else city.name, _path(tool, city, lang)))
    return crumbs


# --------------------------------------------------------------------------
# /panchang
# --------------------------------------------------------------------------

def _vrat_block(city: City, day: dt.date, lang: str = EN) -> str:
    """Today's vrat/festivals with their puja muhurat, parana etc. for this
    city (DIVASTRO-111); empty on an ordinary day."""
    from . import vrat_pages            # vrat_pages imports this module: import late
    return vrat_pages.panchang_block(day, city.latitude, city.longitude, city.timezone, lang)


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
{_vrat_block(city, day)}
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
                   alt=_path("panchang", city, HI), crumbs=_tool_crumbs("panchang", city),
                   body=body)


def _panchang_page_hi(city: City) -> HTMLResponse:
    day = _today()
    p = _panchang(city.slug, day)
    s, sun, moon, m = p["summary"], p["sun"], p["moon"], p["muhurta"]
    paksha = PAKSHA_HI.get(s["paksha"] or "", s["paksha"] or "")
    vara = VARA_HI.get(p["vara"]["weekday"], p["vara"]["weekday"])
    tithi = TITHI_HI.get(s["tithi"], s["tithi"])
    nak = NAKSHATRAS_HI.get(s["nakshatra"], s["nakshatra"])
    rahu = _span(m["rahu_kaal"], day, HI)
    sunrise = _time(sun["rise"], day, HI)
    rows = [
        ("वार", _e(vara)),
        ("तिथि", _limb_rows(p["tithi"], day, TITHI_HI, HI)),
        ("पक्ष", _e(paksha)),
        ("नक्षत्र", _limb_rows(p["nakshatra"], day, NAKSHATRAS_HI, HI)),
        ("योग", _limb_rows(p["yoga"], day, YOGA_HI, HI)),
        ("करण", _limb_rows(p["karana"], day, KARANA_HI, HI)),
        ("सूर्योदय", sunrise),
        ("सूर्यास्त", _time(sun["set"], day, HI)),
        ("चंद्रोदय", _time(moon["rise"], day, HI) if moon["rise"] else "इस दिन चंद्रोदय नहीं"),
        ("चंद्रास्त", _time(moon["set"], day, HI) if moon["set"] else "इस दिन चंद्रास्त नहीं"),
        ("चंद्र राशि", _e(matching.SIGNS_HI.get(moon["sign"], moon["sign"]))),
        ("राहु काल", rahu),
        ("यमगण्ड", _span(m["yamaganda"], day, HI)),
        ("गुलिक काल", _span(m["gulika_kaal"], day, HI)),
        ("अभिजित मुहूर्त", _span(m["abhijit"], day, HI) if m["abhijit"]
         else "बुधवार को अभिजित मुहूर्त नहीं माना जाता"),
    ]
    table = "".join(f'<tr><th scope="row">{_e(k)}</th><td>{v}</td></tr>' for k, v in rows)
    date_text = _long_date(day, HI)
    title = f"आज का पंचांग {city.name_hi}, {date_text} — तिथि, नक्षत्र, राहु काल | {BRAND}"
    description = (
        f"{city.name_hi} का आज का पंचांग ({vara}, {date_text}): {paksha} {tithi} तिथि, "
        f"{nak} नक्षत्र, सूर्योदय {sunrise}, राहु काल {rahu}। स्विस एफ़िमेरिस से सटीक गणना।")
    body = f"""
<h1>{_e(city.name_hi)} में आज का पंचांग</h1>
<p class="hi" lang="en">Today's Panchang in {_e(city.name)}</p>
{_when_heading(city, day, p, HI)}
<div class="box"><p>आज {_e(city.name_hi)} में <strong>{_e(paksha)} की {_e(tithi)}</strong> तिथि है और
चंद्रमा <strong>{_e(nak)}</strong> नक्षत्र में है। राहु काल <strong>{rahu}</strong> तक रहेगा —
इस समय में कोई नया काम शुरू न करें।</p></div>
{_vrat_block(city, day, HI)}
<div class="scroll"><table>{table}</table></div>
<p>सभी समय {_e(city.name_hi)} ({city.latitude:.4f}°N, {city.longitude:.4f}°E) के लिए भारतीय मानक
समय (IST) में हैं। पंचांग का दिन सूर्योदय से अगले सूर्योदय तक चलता है, इसलिए कोई तिथि या नक्षत्र
आधी रात के बाद भी समाप्त हो सकता है। सूर्योदय भारतीय पंचांगों की तरह सूर्य के ऊपरी किनारे के
दिखने (वायुमंडलीय अपवर्तन सहित) से लिया गया है; नक्षत्र और योग लाहिड़ी अयनांश से हैं।</p>
{_cta("panchang", "पूरा पंचांग खोलें — कोई भी शहर, कोई भी तारीख", HI)}
<h2>पंचांग के पाँच अंग</h2>
<p><strong>तिथि</strong> चंद्र दिवस है — चंद्रमा सूर्य से जितनी बार 12° आगे बढ़ता है, उतनी
तिथियाँ। <strong>नक्षत्र</strong> 27 में से वह नक्षत्र है जिसमें चंद्रमा स्थित है।
<strong>योग</strong> सूर्य और चंद्रमा के भोगांशों के योग से बनता है, और <strong>करण</strong>
आधी तिथि होता है। <strong>वार</strong> सप्ताह का दिन है, जो सूर्योदय से गिना जाता है। ये पाँचों
मिलकर पंचांग (“पाँच अंग”) कहलाते हैं, जिन्हें हर शुभ कार्य से पहले देखा जाता है।</p>
{_city_links("panchang", city, HI)}
{_tool_links(city, "panchang", HI)}"""
    return _render(title=title, description=description, path=_path("panchang", city, HI),
                   alt=_path("panchang", city), crumbs=_tool_crumbs("panchang", city, HI),
                   body=body, lang=HI)


@router.get("/panchang", response_class=HTMLResponse)
def panchang_default() -> HTMLResponse:
    return _panchang_page(seo_cities.DEFAULT)


@router.get("/panchang/{slug}", response_class=HTMLResponse)
def panchang_city(slug: str) -> HTMLResponse:
    city = seo_cities.get(slug)
    return _panchang_page(city) if city else _not_found("panchang", slug)


@router.get("/hi/panchang", response_class=HTMLResponse)
def panchang_default_hi() -> HTMLResponse:
    return _panchang_page_hi(seo_cities.DEFAULT)


@router.get("/hi/panchang/{slug}", response_class=HTMLResponse)
def panchang_city_hi(slug: str) -> HTMLResponse:
    city = seo_cities.get(slug)
    return _panchang_page_hi(city) if city else _not_found("panchang", slug, HI)


# --------------------------------------------------------------------------
# /rahu-kaal
# --------------------------------------------------------------------------

def _rahu_week(city: City, day: dt.date, lang: str = EN) -> str:
    """A week ahead: the most-asked follow-up ("what about tomorrow?") answered
    on the page itself. Seven ~10 ms computations, all cached."""
    rows = []
    for offset in range(7):
        d = day + dt.timedelta(days=offset)
        q = _panchang(city.slug, d)
        weekday = q['vara']['weekday']
        label = VARA_HI.get(weekday, weekday) if lang == HI else weekday
        rows.append(f"<tr><td>{_e(label)}<small>{_e(_short_date(d, lang))}</small></td>"
                    f"<td>{_span(q['muhurta']['rahu_kaal'], d, lang)}</td>"
                    f"<td>{_span(q['muhurta']['yamaganda'], d, lang)}</td>"
                    f"<td>{_span(q['muhurta']['gulika_kaal'], d, lang)}</td></tr>")
    return "".join(rows)


def _rahu_page(city: City) -> HTMLResponse:
    day = _today()
    p = _panchang(city.slug, day)
    m, sun = p["muhurta"], p["sun"]
    weekday = p["vara"]["weekday"]
    week = _rahu_week(city, day)

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
{week}
</table></div>
{_city_links("rahu-kaal", city)}
{_tool_links(city, "rahu-kaal")}"""
    return _render(title=title, description=description, path=_path("rahu-kaal", city),
                   alt=_path("rahu-kaal", city, HI), crumbs=_tool_crumbs("rahu-kaal", city),
                   body=body)


def _rahu_page_hi(city: City) -> HTMLResponse:
    day = _today()
    p = _panchang(city.slug, day)
    m, sun = p["muhurta"], p["sun"]
    vara = VARA_HI.get(p["vara"]["weekday"], p["vara"]["weekday"])
    date_text = _long_date(day, HI)
    rahu = _span(m["rahu_kaal"], day, HI)
    title = f"आज का राहु काल {city.name_hi} — {rahu}, {date_text} | {BRAND}"
    description = (
        f"{city.name_hi} में आज ({vara}, {date_text}) राहु काल {rahu} है। साथ में यमगण्ड "
        f"{_span(m['yamaganda'], day, HI)} और गुलिक काल {_span(m['gulika_kaal'], day, HI)}, "
        "पूरे सप्ताह का समय और राहु काल का अर्थ।")
    abhijit = (_span(m['abhijit'], day, HI) if m['abhijit']
               else 'बुधवार को अभिजित मुहूर्त नहीं माना जाता')
    body = f"""
<h1>{_e(city.name_hi)} में आज का राहु काल</h1>
<p class="hi" lang="en">Rahu Kaal Today in {_e(city.name)}</p>
{_when_heading(city, day, p, HI)}
<div class="scroll"><table>
<tr><th scope="row">राहु काल</th><td class="bad"><strong>{rahu}</strong></td></tr>
<tr><th scope="row">यमगण्ड</th><td>{_span(m['yamaganda'], day, HI)}</td></tr>
<tr><th scope="row">गुलिक काल</th><td>{_span(m['gulika_kaal'], day, HI)}</td></tr>
<tr><th scope="row">अभिजित मुहूर्त</th><td class="good">{abhijit}</td></tr>
<tr><th scope="row">सूर्योदय / सूर्यास्त</th><td>{_time(sun['rise'], day, HI)} / {_time(sun['set'], day, HI)}</td></tr>
</table></div>
{_cta("rahu-kaal", "किसी भी शहर या तारीख का राहु काल देखें", HI)}
<h2>राहु काल क्या है?</h2>
<p>राहु काल हर दिन लगभग डेढ़ घंटे की वह अवधि है जिस पर परंपरा से राहु (चंद्रमा का उत्तरी
पात) का प्रभाव माना जाता है। सूर्योदय से सूर्यास्त तक के दिन को आठ बराबर भागों में बाँटा
जाता है और उनमें से एक भाग राहु का होता है। कौन-सा भाग, यह वार पर निर्भर है: रविवार को आठवाँ,
सोमवार को दूसरा, मंगलवार को सातवाँ, बुधवार को पाँचवाँ, गुरुवार को छठा, शुक्रवार को चौथा और
शनिवार को तीसरा।</p>
<p>चूँकि यह वास्तविक सूर्योदय और सूर्यास्त पर आधारित है, इसलिए राहु काल हर शहर में अलग होता है
और साल भर बदलता रहता है — “सोमवार 7:30–9:00” जैसी तय तालिका केवल अनुमान है। परंपरा के अनुसार
राहु काल में नया काम शुरू करना, अनुबंध पर हस्ताक्षर, यात्रा आरंभ या बड़ी ख़रीदारी टाली जाती है;
पहले से चल रहा काम जारी रखा जा सकता है। यमगण्ड और गुलिक काल दिन के दो और आठवें भाग हैं, जिनमें
भी ऐसी ही सावधानी रखी जाती है।</p>
<h2>{_e(city.name_hi)} में इस सप्ताह का राहु काल</h2>
<div class="scroll"><table>
<tr><th>दिन</th><th>राहु काल</th><th>यमगण्ड</th><th>गुलिक</th></tr>
{_rahu_week(city, day, HI)}
</table></div>
{_city_links("rahu-kaal", city, HI)}
{_tool_links(city, "rahu-kaal", HI)}"""
    return _render(title=title, description=description, path=_path("rahu-kaal", city, HI),
                   alt=_path("rahu-kaal", city), crumbs=_tool_crumbs("rahu-kaal", city, HI),
                   body=body, lang=HI)


@router.get("/rahu-kaal", response_class=HTMLResponse)
def rahu_default() -> HTMLResponse:
    return _rahu_page(seo_cities.DEFAULT)


@router.get("/rahu-kaal/{slug}", response_class=HTMLResponse)
def rahu_city(slug: str) -> HTMLResponse:
    city = seo_cities.get(slug)
    return _rahu_page(city) if city else _not_found("rahu-kaal", slug)


@router.get("/hi/rahu-kaal", response_class=HTMLResponse)
def rahu_default_hi() -> HTMLResponse:
    return _rahu_page_hi(seo_cities.DEFAULT)


@router.get("/hi/rahu-kaal/{slug}", response_class=HTMLResponse)
def rahu_city_hi(slug: str) -> HTMLResponse:
    city = seo_cities.get(slug)
    return _rahu_page_hi(city) if city else _not_found("rahu-kaal", slug, HI)


# --------------------------------------------------------------------------
# /choghadiya
# --------------------------------------------------------------------------

def choghadiya_slots(p: dict) -> tuple[list[dict], list[dict]]:
    """Day and night choghadiya from a `daily_panchang` result.

    Slots come from chog.day_night_slots, the same code /api/choghadiya uses,
    cut at the ephemeris sunrise/sunset this page's Panchang prints
    (DIVASTRO-103: both now agree to the second).
    """
    rise, sset, next_rise = (_local(p["sun"][k]) for k in ("rise", "set", "next_rise"))
    if not (rise and sset and next_rise):
        return [], []
    vara = p["vara"]["index"]                          # Sunday = 0, as choghadiya.py uses

    def run(parts: list) -> list[dict]:
        return [{"name": n, "start": s, "end": e, **chog.CHOGHADIYA_INFO[n]} for n, s, e in parts]

    day, night = chog.day_night_slots(vara, rise, sset, next_rise)
    return run(day), run(night)


def _chog_table(slots: list[dict], day: dt.date, lang: str = EN) -> str:
    hi = lang == HI
    rows = []
    for s in slots:
        cls = {"auspicious": "good", "inauspicious": "bad"}.get(s["quality"], "")
        when = (f"{_time(s['start'].isoformat(), day, lang)} – "
                f"{_time(s['end'].isoformat(), day, lang)}")
        if hi:
            rows.append(
                f"<tr><td>{when}</td>"
                f'<td class="{cls}"><strong>{_e(s["name_hi"])}</strong>'
                f'<small>स्वामी: {_e(s["ruler_hi"])}</small></td>'
                f"<td>{_e(s['quality_hi'])}<small>{_e(s['description_hi'])}</small></td></tr>")
        else:
            rows.append(
                f"<tr><td>{when}</td>"
                f'<td class="{cls}"><strong>{_e(s["name"])}</strong> '
                f'<span lang="hi">({_e(s["name_hi"])})</span><small>{_e(s["ruler"])}</small></td>'
                f"<td>{_e(s['quality'].capitalize())}<small>{_e(s['description'])}</small></td></tr>")
    head = ("<tr><th>समय</th><th>चौघड़िया</th><th>स्वभाव</th></tr>" if hi
            else "<tr><th>Time</th><th>Choghadiya</th><th>Nature</th></tr>")
    return '<div class="scroll"><table>' + head + "".join(rows) + "</table></div>"


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
                   alt=_path("choghadiya", city, HI), crumbs=_tool_crumbs("choghadiya", city),
                   body=body)


def _choghadiya_page_hi(city: City) -> HTMLResponse:
    day = _today()
    p = _panchang(city.slug, day)
    day_slots, night_slots = choghadiya_slots(p)
    vara = VARA_HI.get(p["vara"]["weekday"], p["vara"]["weekday"])
    date_text = _long_date(day, HI)
    good = [s for s in day_slots if s["quality"] == "auspicious"]
    first_good = (f"{good[0]['name_hi']} — {_time(good[0]['start'].isoformat(), day, HI)} से"
                  if good else "कोई नहीं")
    sunrise = _time(p['sun']['rise'], day, HI)
    title = f"आज का चौघड़िया {city.name_hi}, {date_text} — दिन और रात का चौघड़िया | {BRAND}"
    description = (
        f"{city.name_hi} का आज का चौघड़िया ({vara}, {date_text}): दिन और रात के सभी 16 मुहूर्त — "
        f"अमृत, शुभ, लाभ, चल, रोग, काल, उद्वेग — सूर्योदय {sunrise} से सटीक आरंभ और समाप्ति समय के साथ।")
    body = f"""
<h1>{_e(city.name_hi)} में आज का चौघड़िया</h1>
<p class="hi" lang="en">Choghadiya Today in {_e(city.name)}</p>
{_when_heading(city, day, p, HI)}
<div class="box"><p>सूर्योदय <strong>{sunrise}</strong>, सूर्यास्त
<strong>{_time(p['sun']['set'], day, HI)}</strong>। दिन का पहला शुभ चौघड़िया:
<strong>{_e(first_good)}</strong>।</p></div>
<h2>दिन का चौघड़िया</h2>
{_chog_table(day_slots, day, HI)}
<h2>रात का चौघड़िया</h2>
{_chog_table(night_slots, day, HI)}
{_cta("choghadiya", "लाइव चौघड़िया घड़ी खोलें", HI)}
<h2>चौघड़िया कैसे निकाला जाता है</h2>
<p>सूर्योदय से सूर्यास्त तक का दिन, और सूर्यास्त से अगले सूर्योदय तक की रात — दोनों को आठ-आठ
बराबर भागों में बाँटा जाता है, जिन्हें चौघड़िया (“चार घड़ी”) कहते हैं। हर भाग का एक स्वामी ग्रह
होता है और नाम उसके स्वभाव से: <strong>अमृत</strong>, <strong>शुभ</strong> और
<strong>लाभ</strong> शुभ हैं, <strong>चल</strong> (चर) सामान्य है और यात्रा के लिए अच्छा माना जाता है,
जबकि <strong>रोग</strong>, <strong>काल</strong> और <strong>उद्वेग</strong> में नए काम की
शुरुआत टाली जाती है। क्रम वार के स्वामी से शुरू होता है, इसलिए हर दिन बदलता है — और हर भाग की
लंबाई {_e(city.name_hi)} में दिन की वास्तविक लंबाई पर निर्भर करती है।</p>
{_city_links("choghadiya", city, HI)}
{_tool_links(city, "choghadiya", HI)}"""
    return _render(title=title, description=description, path=_path("choghadiya", city, HI),
                   alt=_path("choghadiya", city), crumbs=_tool_crumbs("choghadiya", city, HI),
                   body=body, lang=HI)


@router.get("/choghadiya", response_class=HTMLResponse)
def choghadiya_default() -> HTMLResponse:
    return _choghadiya_page(seo_cities.DEFAULT)


@router.get("/choghadiya/{slug}", response_class=HTMLResponse)
def choghadiya_city(slug: str) -> HTMLResponse:
    city = seo_cities.get(slug)
    return _choghadiya_page(city) if city else _not_found("choghadiya", slug)


@router.get("/hi/choghadiya", response_class=HTMLResponse)
def choghadiya_default_hi() -> HTMLResponse:
    return _choghadiya_page_hi(seo_cities.DEFAULT)


@router.get("/hi/choghadiya/{slug}", response_class=HTMLResponse)
def choghadiya_city_hi(slug: str) -> HTMLResponse:
    city = seo_cities.get(slug)
    return _choghadiya_page_hi(city) if city else _not_found("choghadiya", slug, HI)


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

# The same eight, in Hindi, keyed like KOOTAS (the test checks the keys match).
KOOTAS_HI = {
    "varna": "चंद्र राशि के वर्ण से आध्यात्मिक और कार्य-स्वभाव। वर का वर्ण कन्या के वर्ण से "
             "कम न हो तो पूरा अंक।",
    "vashya": "आपसी आकर्षण और प्रभाव — कौन-सी राशि दूसरी को “वश” में करती है।",
    "tara": "स्वास्थ्य और कल्याण, दोनों जन्म नक्षत्रों के बीच की गिनती से; तीसरी, पाँचवीं और "
            "सातवीं तारा प्रतिकूल मानी जाती है।",
    "yoni": "शारीरिक और दांपत्य अनुकूलता; हर नक्षत्र की एक पशु योनि होती है, और परस्पर शत्रु "
            "योनियों को शून्य अंक मिलता है।",
    "graha_maitri": "दोनों चंद्र राशियों के स्वामियों की मित्रता — दंपति का मानसिक तालमेल।",
    "gana": "स्वभाव: देव, मनुष्य या राक्षस गण।",
    "bhakoot": "दोनों चंद्र राशियों की परस्पर स्थिति। 2/12, 5/9 और 6/8 की स्थिति भकूट दोष "
               "बनाती है, जो दोनों राशियों के स्वामी एक हों या मित्र हों तो निरस्त हो जाता है।",
    "nadi": "सबसे अधिक अंकों वाला कूट, स्वास्थ्य और संतान से जुड़ा। दोनों की एक ही नाड़ी होना "
            "नाड़ी दोष है; राशि एक पर नक्षत्र भिन्न, या नक्षत्र एक पर चरण भिन्न होने पर इसका "
            "शास्त्रीय परिहार माना जाता है।",
}


def _score_bands(lang: str = EN) -> str:
    """The bands are read straight from the engine's table (upper bounds are
    exclusive ceilings, the last one 36.01), so the page and the verdict the
    tool prints can never disagree."""
    total = int(matching.MAXIMUM_POINTS)
    table = matching.SCORE_BANDS_HI if lang == HI else matching.SCORE_BANDS
    bands, low = [], 0
    for ceiling, verdict, _detail in table:
        top = min(math.ceil(ceiling) - 1, total)
        if low == 0:
            rng = f"{top + 1} से कम" if lang == HI else f"Below {top + 1}"
        else:
            rng = f"{low}–{top}"
        text = verdict if lang == HI else verdict.capitalize()
        bands.append(f"<tr><td>{rng}</td><td>{_e(text)}</td></tr>")
        low = top + 1
    return "".join(bands)


@router.get("/kundali-milan", response_class=HTMLResponse)
def kundali_milan() -> HTMLResponse:
    rows = "".join(
        f"<tr><td><strong>{_e(name)}</strong> "
        f'<span lang="hi">({_e(matching.KOOTA_LABELS_HI[key])})</span></td>'
        f"<td>{pts}</td><td>{_e(text)}</td></tr>"
        for key, name, pts, text in KOOTAS)
    total = int(matching.MAXIMUM_POINTS)
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
<div class="scroll"><table><tr><th>Gunas</th><th>Conventional reading</th></tr>{_score_bands()}</table></div>
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
                   alt="/hi/kundali-milan", crumbs=[("Kundali Milan", "/kundali-milan")],
                   body=body)


@router.get("/hi/kundali-milan", response_class=HTMLResponse)
def kundali_milan_hi() -> HTMLResponse:
    rows = "".join(
        f"<tr><td><strong>{_e(matching.KOOTA_LABELS_HI[key])}</strong></td>"
        f"<td>{pts}</td><td>{_e(KOOTAS_HI[key])}</td></tr>"
        for key, _name, pts, _text in KOOTAS)
    total = int(matching.MAXIMUM_POINTS)
    hs = [str(h) for h in matching.MANGAL_HOUSES]
    houses = ", ".join(hs[:-1]) + " या " + hs[-1]
    title = f"कुंडली मिलान — अष्टकूट गुण मिलान ({total} गुण) की पूरी जानकारी | {BRAND}"
    description = (
        f"कुंडली मिलान कैसे होता है: अष्टकूट गुण मिलान के 8 कूट, कुल {total} गुण, विवाह के लिए "
        "कितने गुण अच्छे माने जाते हैं, और मांगलिक दोष की जाँच। हिंदी और अंग्रेज़ी में मुफ़्त "
        "ऑनलाइन कुंडली मिलान।")
    body = f"""
<h1>कुंडली मिलान: अष्टकूट गुण मिलान की पूरी जानकारी</h1>
<p class="hi" lang="en">Kundali Milan — Ashtakoot Guna Milan ({total} points)</p>
<p>कुंडली मिलान विवाह से पहले वर और कन्या की अनुकूलता देखने की पारंपरिक वैदिक विधि है।
उत्तर भारत में सबसे अधिक प्रचलित तरीक़ा <strong>अष्टकूट गुण मिलान</strong> है: दोनों की कुंडलियों
में आठ कूटों की तुलना की जाती है और कुल <strong>{total} गुणों</strong> में से अंक दिए जाते हैं।
ये सभी <strong>चंद्रमा</strong> से देखे जाते हैं — जन्म के समय उसकी राशि और नक्षत्र से — इसलिए
सही जन्म तिथि और स्थान ज़रूरी है, पर जन्म समय का असर बहुत कम पड़ता है।</p>
{_cta("kundali-milan", "अभी दो कुंडलियाँ मिलाएँ — मुफ़्त", HI)}
<h2>आठ कूट और उनके गुण</h2>
<div class="scroll"><table><tr><th>कूट</th><th>गुण</th><th>क्या देखा जाता है</th></tr>
{rows}
<tr><td><strong>कुल</strong></td><td><strong>{total}</strong></td><td></td></tr></table></div>
<h2>कितने गुण मिलना अच्छा है?</h2>
<div class="scroll"><table><tr><th>गुण</th><th>पारंपरिक अर्थ</th></tr>{_score_bands(HI)}</table></div>
<p>18 गुण पारंपरिक न्यूनतम सीमा है। केवल कुल अंक से पूरी बात नहीं कही जा सकती: ऊँचे अंकों के साथ
बिना परिहार का नाड़ी या भकूट दोष हो तो सावधानी से देखा जाता है, और कम अंक होने पर भी अच्छी ग्रह
मैत्री और कोई दोष न हो तो मिलान अक्सर स्वीकार्य माना जाता है। ये सीमाएँ एक पुरानी परंपरा हैं,
कोई माप नहीं — ये मार्गदर्शन हैं, किसी रिश्ते पर अंतिम निर्णय नहीं।</p>
<h2>मांगलिक दोष (मंगल दोष)</h2>
<p>मांगलिक दोष 36 गुणों से अलग देखा जाता है। कुंडली मांगलिक तब होती है जब मंगल
<strong>लग्न</strong>, <strong>चंद्रमा</strong> या <strong>शुक्र</strong> से गिनकर {houses}वें
भाव में हो। शास्त्रों में कुछ राशि-स्थितियों को छूट दी गई है (जैसे पहले भाव में अपनी राशि मेष
में मंगल), और मंगल पर गुरु की दृष्टि से दोष कम माना जाता है। जब वर और कन्या
<strong>दोनों</strong> मांगलिक हों तो परंपरा से दोष आपस में कट जाता है — इसीलिए मांगलिक का
विवाह मांगलिक से किया जाता है। लग्न पर निर्भर होने के कारण मांगलिक दोष के लिए सही जन्म समय
ज़रूरी है।</p>
<h2>हमारा मिलान टूल कैसे काम करता है</h2>
<p>दोनों की जन्म तिथि, समय और स्थान भरें। दोनों कुंडलियाँ स्विस एफ़िमेरिस से निरयण (लाहिड़ी
अयनांश) पद्धति में बनती हैं, और हर कूट के अंक शास्त्रीय तालिकाओं से दिए जाते हैं — हर परिहार
का नाम लेकर। आपको पूरे {total} गुणों का ब्योरा और दोनों का मांगलिक विचार हिंदी या अंग्रेज़ी में,
मुफ़्त और बिना साइन-अप के मिलता है।</p>
{_cta("kundali-milan", "कुंडली मिलान खोलें", HI)}
{_tool_links(seo_cities.DEFAULT, "kundali-milan", HI)}"""
    return _render(title=title, description=description, path="/hi/kundali-milan",
                   alt="/kundali-milan", crumbs=[("कुंडली मिलान", "/hi/kundali-milan")],
                   body=body, lang=HI)


# --------------------------------------------------------------------------
# /free-kundali
# --------------------------------------------------------------------------

# What the free chart actually contains, checked against the app: the varga
# list is the vargas engine's DEFAULT_DIVISIONS (what /api/vargas and the
# Vargas tab show), and the test pins that. Paid extras (the Life Book PDF
# with all sixteen vargas, single-question reports) are deliberately absent.
_VARGA_NAMES = {"D1": ("Rashi", "राशि"), "D3": ("Drekkana", "द्रेष्काण"),
                "D7": ("Saptamsa", "सप्तांश"), "D9": ("Navamsa", "नवांश"),
                "D10": ("Dashamsa", "दशमांश"), "D12": ("Dwadashamsa", "द्वादशांश")}


def _vargas(lang: str) -> str:
    i = 1 if lang == HI else 0
    return ", ".join(f"{code} {_VARGA_NAMES[code][i]}" for code in DEFAULT_DIVISIONS)


FAQ_EN = (
    ("Is the kundali really free?",
     "Yes. Casting the chart, the dashas, the divisional charts and the dosha check cost "
     "nothing, and you do not need to sign in to see them. Only the AI astrologer's answers "
     "beyond your free questions, and in-depth paid reports such as the Life Book, cost money."),
    ("What details do I need?",
     "Your date of birth, time of birth and place of birth. The place sets the latitude, "
     "longitude and time zone, which decide the Lagna (ascendant) and the house positions."),
    ("What if I don't know my exact birth time?",
     "The chart is still cast, at 12:00 noon. The Moon sign and nakshatra are usually still "
     "right (unless the Moon changed sign or nakshatra that day), so Moon-based readings, "
     "Sade Sati and Kundali Milan stay useful — but the Lagna, the houses and Mangal Dosha "
     "need a reliable time. A time from a birth certificate or hospital record is best."),
    ("Which system do you use — Lahiri, KP, tropical?",
     "Every chart is sidereal (Nirayana) with the Lahiri (Chitrapaksha) ayanamsa, whole-sign "
     "houses and Vimshottari dasha — the convention of most Indian almanacs and astrologers. "
     "Planet positions come from the Swiss Ephemeris."),
    ("Can I see my kundali in Hindi?",
     "Yes. Switch the app to हिन्दी and the chart, planet and sign names, dashas and "
     "readings all appear in Hindi; the PDF can be downloaded in Hindi too."),
    ("North Indian or South Indian chart?",
     "Both. The same chart can be shown as the North Indian diamond chart (houses fixed, signs "
     "numbered) or the South Indian square chart (signs fixed), with one tap."),
    ("Is this the same as a horoscope?",
     "A janam kundali is the birth chart itself — the fixed map of the sky at your birth. "
     "A daily horoscope or rashifal is a short general forecast for everyone with the same "
     "Moon sign. Your kundali is personal; a rashifal is not."),
)

FAQ_HI = (
    ("क्या कुंडली सच में मुफ़्त है?",
     "हाँ। कुंडली बनाना, दशाएँ, वर्ग कुंडलियाँ और दोष जाँच पूरी तरह मुफ़्त हैं, और इन्हें देखने के "
     "लिए साइन-इन की ज़रूरत नहीं। केवल मुफ़्त प्रश्नों के बाद एआई ज्योतिषी के उत्तर और लाइफ़ "
     "बुक जैसी विस्तृत रिपोर्ट सशुल्क हैं।"),
    ("कुंडली बनाने के लिए क्या चाहिए?",
     "आपकी जन्म तिथि, जन्म समय और जन्म स्थान। स्थान से अक्षांश, देशांतर और समय क्षेत्र तय होते "
     "हैं, जिनसे लग्न और भावों की स्थिति निकलती है।"),
    ("अगर सही जन्म समय पता न हो तो?",
     "कुंडली फिर भी दोपहर 12:00 बजे के हिसाब से बन जाती है। चंद्र राशि और नक्षत्र आमतौर पर सही "
     "रहते हैं (जब तक उस दिन चंद्रमा ने राशि या नक्षत्र न बदला हो), इसलिए चंद्र-आधारित फल, "
     "साढ़ेसाती और कुंडली मिलान उपयोगी रहते हैं — पर लग्न, भाव और मांगलिक दोष के लिए सही समय "
     "ज़रूरी है। जन्म प्रमाणपत्र या अस्पताल के रिकॉर्ड का समय सबसे अच्छा है।"),
    ("कौन-सी पद्धति इस्तेमाल होती है?",
     "हर कुंडली निरयण (सायन नहीं) पद्धति में लाहिड़ी (चित्रापक्ष) अयनांश, संपूर्ण राशि भाव "
     "(whole sign) और विंशोत्तरी दशा से बनती है — जो अधिकांश भारतीय पंचांगों और ज्योतिषियों की "
     "परंपरा है। ग्रहों की स्थिति स्विस एफ़िमेरिस से ली जाती है।"),
    ("क्या कुंडली हिंदी में मिलेगी?",
     "हाँ। ऐप को हिन्दी में बदलें — कुंडली, ग्रहों और राशियों के नाम, दशाएँ और फलादेश सब हिंदी में "
     "दिखेंगे; PDF भी हिंदी में डाउनलोड की जा सकती है।"),
    ("उत्तर भारतीय या दक्षिण भारतीय कुंडली?",
     "दोनों। एक ही कुंडली को उत्तर भारतीय (भाव स्थिर, राशियों के अंक) या दक्षिण भारतीय (राशियाँ "
     "स्थिर) शैली में एक टैप से देखा जा सकता है।"),
    ("जन्म कुंडली और राशिफल में क्या अंतर है?",
     "जन्म कुंडली आपके जन्म के क्षण के आकाश का स्थायी नक्शा है। दैनिक राशिफल एक ही चंद्र राशि वाले "
     "सभी लोगों के लिए छोटा सामान्य फल है। कुंडली व्यक्तिगत है; राशिफल नहीं।"),
)


def _faq(items: tuple) -> tuple[str, dict]:
    """The FAQ as HTML and as FAQPage JSON-LD, from one list so the two can
    never say different things (Google requires the marked-up Q&A to be
    visible on the page)."""
    html_part = "".join(f"<h3>{_e(q)}</h3><p>{_e(a)}</p>" for q, a in items)
    ld = {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
        for q, a in items]}
    return f'<div class="faq">{html_part}</div>', ld


@router.get("/free-kundali", response_class=HTMLResponse)
def free_kundali() -> HTMLResponse:
    faq_html, faq_ld = _faq(FAQ_EN)
    title = f"Free Kundali Online — Janam Kundali (Birth Chart) in English & Hindi | {BRAND}"
    description = (
        "Make your free janam kundali online: Lagna chart in North or South Indian style, planet "
        "positions, Moon nakshatra, Vimshottari dasha, Navamsa and other divisional charts, "
        "Manglik, Sade Sati and Kaal Sarp check — in English or Hindi, no sign-in needed.")
    body = f"""
<h1>Free Janam Kundali online</h1>
<p class="hi" lang="hi">मुफ़्त जन्म कुंडली — हिंदी और अंग्रेज़ी में</p>
<p>A <strong>janam kundali</strong> (<span lang="hi">जन्म कुंडली</span>, birth chart) is a map of
the sky at the exact moment and place you were born: which of the twelve signs was rising on the
eastern horizon (your <strong>Lagna</strong>), and where the Sun, Moon, Mars, Mercury, Jupiter,
Venus, Saturn, Rahu and Ketu stood among the signs and the 27 nakshatras. Vedic astrology reads
everything else — personality, the twelve areas of life, and above all <em>timing</em> through
the dasha periods — from this one chart. Ours is computed to the minute and is free.</p>
{_cta("free-kundali", "Make my free kundali now", big=True)}
<p>You need your <strong>date</strong>, <strong>time</strong> and <strong>place</strong> of birth.
No sign-in, no card.</p>

<h2>What your free kundali includes</h2>
<ul>
<li><strong>Lagna chart (D1)</strong> in North Indian or South Indian style — switch with one tap.</li>
<li><strong>Planet positions</strong>: sign, degree, house, dignity and retrograde status of all
nine grahas and the ascendant, with your Moon's nakshatra and pada.</li>
<li><strong>The twelve houses (bhavas)</strong> with the planets in each.</li>
<li><strong>Vimshottari dasha</strong>: your current mahadasha and antardasha with their dates,
on a visual timeline.</li>
<li><strong>Divisional charts (vargas)</strong>: {_e(_vargas(EN))}.</li>
<li><strong>Ashtakavarga</strong>: Sarvashtakavarga and Bhinnashtakavarga bindus by house.</li>
<li><strong>Jaimini</strong> chara karakas (Atmakaraka to Darakaraka) and the Arudha padas, and the
<strong>Sudarshana Chakra</strong> reading of the chart from Lagna, Moon and Sun together.</li>
<li><strong>Dosha check</strong>: Mangal Dosha (Manglik), Sade Sati and Kaal Sarp.</li>
<li><strong>Gemstone and remedy</strong> suggestions for your chart and current dasha.</li>
<li>Your <strong>daily forecast</strong> and today's panchang, on your chart's dashboard.</li>
</ul>
<p>Everything is cast in the <strong>sidereal zodiac with the Lahiri ayanamsa</strong>, whole-sign
houses, from the Swiss Ephemeris. With a free account you can also save charts, download the
kundali as a PDF in English or Hindi, and ask the AI astrologer your first questions free.</p>

<h2>How to read your kundali</h2>
<h3>1. Start with the Lagna</h3>
<p>The first house is the sign rising at birth. In the North Indian chart it is the top centre
diamond, and the number written in each house is the <em>sign</em> (1 = Aries … 12 = Pisces), not
the house. In the South Indian chart the signs stay in fixed boxes and the Lagna is marked. The
Lagna and its lord describe the body, temperament and the overall direction of life.</p>
<h3>2. Note your Moon sign and nakshatra</h3>
<p>Your <strong>rashi</strong> in Indian usage is the Moon's sign, not the Sun's. It is the
sign used for rashifal, Sade Sati and Kundali Milan, and the Moon's nakshatra decides where
your Vimshottari dasha begins.</p>
<h3>3. Read the planets by house</h3>
<p>Each house is an area of life: 1st self, 2nd wealth and family, 3rd courage and siblings,
4th home and mother, 5th children and intellect, 6th health and rivals, 7th marriage and
partnership, 8th longevity and sudden change, 9th fortune and dharma, 10th career,
11th gains, 12th expenses and moksha. A planet colours the house it sits in and the houses it
rules; its dignity (exalted, own sign, debilitated) says how well it can deliver.</p>
<h3>4. Check the dasha you are running</h3>
<p>The dasha says <em>when</em>. The mahadasha lord, and within it the antardasha lord, are
the planets whose houses come alive in this period — which is why two people with similar
charts can have very different years.</p>
<h3>5. Treat doshas in context</h3>
<p>A dosha is a pattern to read, not a verdict. Mangal Dosha has classical cancellations;
Sade Sati is a seven-and-a-half-year transit everyone meets two or three times. The dosha
report names the cancellations it found.</p>
{_cta("free-kundali", "Create my janam kundali — free")}

<h2>Frequently asked questions</h2>
{faq_html}
{_tool_links(seo_cities.DEFAULT, "free-kundali")}"""
    return _render(title=title, description=description, path="/free-kundali",
                   alt="/hi/free-kundali", crumbs=[("Free Kundali", "/free-kundali")],
                   body=body, extra_ld=(faq_ld,))


@router.get("/hi/free-kundali", response_class=HTMLResponse)
def free_kundali_hi() -> HTMLResponse:
    faq_html, faq_ld = _faq(FAQ_HI)
    title = f"मुफ़्त जन्म कुंडली ऑनलाइन — हिंदी में फ्री कुंडली बनाएँ | {BRAND}"
    description = (
        "अपनी जन्म कुंडली मुफ़्त बनाएँ: उत्तर या दक्षिण भारतीय शैली में लग्न कुंडली, ग्रह "
        "स्थिति, चंद्र नक्षत्र, विंशोत्तरी दशा, नवांश और अन्य वर्ग कुंडलियाँ, मांगलिक, "
        "साढ़ेसाती और कालसर्प दोष — हिंदी या अंग्रेज़ी में, बिना साइन-इन।")
    body = f"""
<h1>मुफ़्त जन्म कुंडली ऑनलाइन</h1>
<p class="hi" lang="en">Free Janam Kundali — in Hindi and English</p>
<p><strong>जन्म कुंडली</strong> आपके जन्म के सटीक क्षण और स्थान पर आकाश का नक्शा है: उस समय पूर्वी
क्षितिज पर बारह में से कौन-सी राशि उदित हो रही थी (आपका <strong>लग्न</strong>), और सूर्य, चंद्रमा,
मंगल, बुध, गुरु, शुक्र, शनि, राहु और केतु किस राशि और 27 में से किस नक्षत्र में थे। वैदिक ज्योतिष
स्वभाव, जीवन के बारह क्षेत्र और सबसे बढ़कर <em>समय</em> — दशाओं के माध्यम से — इसी एक कुंडली से
देखता है। हमारी कुंडली मिनट तक सटीक गणना से बनती है और मुफ़्त है।</p>
{_cta("free-kundali", "अभी मेरी मुफ़्त कुंडली बनाएँ", HI, big=True)}
<p>आपको अपनी जन्म <strong>तिथि</strong>, <strong>समय</strong> और <strong>स्थान</strong> चाहिए।
न साइन-इन, न कार्ड।</p>

<h2>मुफ़्त कुंडली में क्या-क्या मिलता है</h2>
<ul>
<li><strong>लग्न कुंडली (D1)</strong> उत्तर भारतीय या दक्षिण भारतीय शैली में — एक टैप से बदलें।</li>
<li><strong>ग्रह स्थिति</strong>: सभी नौ ग्रहों और लग्न की राशि, अंश, भाव, बल (उच्च/स्वराशि/नीच) और
वक्री स्थिति, साथ में चंद्रमा का नक्षत्र और पाद।</li>
<li><strong>बारह भाव</strong> और हर भाव में स्थित ग्रह।</li>
<li><strong>विंशोत्तरी दशा</strong>: वर्तमान महादशा और अंतर्दशा, तिथियों के साथ, समय-रेखा पर।</li>
<li><strong>वर्ग कुंडलियाँ</strong>: {_e(_vargas(HI))}।</li>
<li><strong>अष्टकवर्ग</strong>: हर भाव के सर्वाष्टकवर्ग और भिन्नाष्टकवर्ग बिंदु।</li>
<li><strong>जैमिनी</strong> चर कारक (आत्मकारक से दाराकारक तक) और आरूढ़ पद, तथा लग्न, चंद्र और सूर्य
से एक साथ देखा गया <strong>सुदर्शन चक्र</strong>।</li>
<li><strong>दोष जाँच</strong>: मांगलिक (मंगल दोष), साढ़ेसाती और कालसर्प दोष।</li>
<li>आपकी कुंडली और वर्तमान दशा के अनुसार <strong>रत्न और उपाय</strong>।</li>
<li>कुंडली के डैशबोर्ड पर आपका <strong>दैनिक फल</strong> और आज का पंचांग।</li>
</ul>
<p>सब कुछ <strong>निरयण राशिचक्र और लाहिड़ी अयनांश</strong>, संपूर्ण राशि भाव पद्धति और स्विस
एफ़िमेरिस से बनता है। मुफ़्त अकाउंट से आप कुंडलियाँ सहेज सकते हैं, कुंडली की PDF हिंदी या
अंग्रेज़ी में डाउनलोड कर सकते हैं, और एआई ज्योतिषी से शुरुआती प्रश्न मुफ़्त पूछ सकते हैं।</p>

<h2>अपनी कुंडली कैसे पढ़ें</h2>
<h3>1. लग्न से शुरू करें</h3>
<p>पहला भाव वह राशि है जो जन्म के समय उदित हो रही थी। उत्तर भारतीय कुंडली में यह ऊपर बीच का
चौकोर (हीरे जैसा) खाना है, और हर खाने में लिखा अंक <em>राशि</em> का है (1 = मेष … 12 = मीन), भाव
का नहीं। दक्षिण भारतीय कुंडली में राशियाँ तय खानों में रहती हैं और लग्न अलग से चिह्नित होता है।
लग्न और लग्नेश शरीर, स्वभाव और जीवन की दिशा बताते हैं।</p>
<h3>2. अपनी चंद्र राशि और नक्षत्र देखें</h3>
<p>भारतीय परंपरा में आपकी <strong>राशि</strong> चंद्रमा की राशि है, सूर्य की नहीं। राशिफल,
साढ़ेसाती और कुंडली मिलान इसी से देखे जाते हैं, और चंद्रमा का नक्षत्र तय करता है कि आपकी
विंशोत्तरी दशा कहाँ से शुरू होगी।</p>
<h3>3. भाव के अनुसार ग्रह पढ़ें</h3>
<p>हर भाव जीवन का एक क्षेत्र है: पहला स्वयं, दूसरा धन और कुटुंब, तीसरा पराक्रम और भाई-बहन, चौथा
घर और माता, पाँचवाँ संतान और बुद्धि, छठा रोग और शत्रु, सातवाँ विवाह और साझेदारी, आठवाँ आयु और
अचानक परिवर्तन, नौवाँ भाग्य और धर्म, दसवाँ कर्म और करियर, ग्यारहवाँ लाभ, बारहवाँ व्यय और मोक्ष।
ग्रह जिस भाव में बैठा है और जिन भावों का स्वामी है, उन्हें प्रभावित करता है; उसकी स्थिति
(उच्च, स्वराशि, नीच) बताती है कि वह कितना फल दे पाएगा।</p>
<h3>4. चल रही दशा देखें</h3>
<p>दशा बताती है <em>कब</em>। महादशा का स्वामी, और उसके भीतर अंतर्दशा का स्वामी, वे ग्रह हैं जिनके
भाव इस अवधि में सक्रिय होते हैं — इसीलिए मिलती-जुलती कुंडली वाले दो लोगों के साल बहुत अलग हो
सकते हैं।</p>
<h3>5. दोषों को संदर्भ में देखें</h3>
<p>दोष पढ़ने का एक संकेत है, कोई फ़ैसला नहीं। मंगल दोष के शास्त्रीय परिहार हैं; साढ़ेसाती शनि का
साढ़े सात साल का गोचर है जो हर किसी के जीवन में दो-तीन बार आता है। दोष रिपोर्ट में मिले हुए परिहारों
के नाम भी दिए जाते हैं।</p>
{_cta("free-kundali", "मेरी जन्म कुंडली बनाएँ — मुफ़्त", HI)}

<h2>अक्सर पूछे जाने वाले प्रश्न</h2>
{faq_html}
{_tool_links(seo_cities.DEFAULT, "free-kundali", HI)}"""
    return _render(title=title, description=description, path="/hi/free-kundali",
                   alt="/free-kundali", crumbs=[("मुफ़्त कुंडली", "/hi/free-kundali")],
                   body=body, lang=HI, extra_ld=(faq_ld,))


# --------------------------------------------------------------------------
# sitemap.xml and robots.txt
# --------------------------------------------------------------------------

STATIC_PATHS = ("/", "/kundali-milan", "/terms", "/privacy", "/refund", "/contact")
# Explainer pages that exist in both languages (/x and /hi/x).
BILINGUAL_PATHS = ("/kundali-milan", "/free-kundali")


def sitemap_paths() -> list[str]:
    """Every public URL this module serves that we want indexed, canonical
    form only. Other modules expose their own `sitemap_paths()`; `sitemap()`
    below just concatenates them."""
    paths = list(STATIC_PATHS) + ["/free-kundali"]
    paths += ["/hi" + p for p in BILINGUAL_PATHS]
    for lang in (EN, HI):
        for tool in TOOLS:
            paths += [_path(tool, c, lang) for c in seo_cities.CITIES]
    from .rashifal_pages import sitemap_paths as rashifal_paths  # lazy: it imports this module
    from .muhurat_pages import page_paths as muhurat_paths  # same: imports this module
    from .vrat_pages import page_paths as vrat_paths  # same: imports this module
    return paths + rashifal_paths() + muhurat_paths() + vrat_paths()


@router.get("/sitemap.xml")
def sitemap() -> Response:
    today = _today().isoformat()
    urls = []
    for path in sitemap_paths():
        fields = f"<loc>{xml_escape(SITE_URL + path)}</loc>"
        bare = path.removeprefix("/hi") if path.startswith("/hi/") else path
        # The tool pages genuinely change every day; the legal pages and the
        # explainers do not, and claiming they do only teaches crawlers to
        # ignore our lastmod.
        if bare.split("/")[1] in TOOLS:
            fields += f"<lastmod>{today}</lastmod><changefreq>daily</changefreq>"
        if path == "/":
            fields += "<priority>1.0</priority>"
        elif bare.strip("/") in TOOLS or bare == "/free-kundali":
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
