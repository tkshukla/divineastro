"""Year-long Vivah and Griha Pravesh muhurat pages, English and Hindi (DIVASTRO-109).

    /muhurat/vivah-2026            /hi/muhurat/vivah-2026
    /muhurat/griha-pravesh-2026    /hi/muhurat/griha-pravesh-2026
    (and the same for 2027 - the Nov 2026 - Feb 2027 wedding season straddles
    the year boundary, and that is what people search for)

"vivah muhurat 2026" is one of the biggest seasonal searches in India, and the
answer is a list of dates - so the list is in the raw HTML, month by month, for
New Delhi. Every date comes from the same engine the in-app Muhurat Finder uses
(`astro.muhurat.evaluate_day`), including the classical period exclusions added
in DIVASTRO-109, so every date on the page is "Auspicious" in the tool too
(the page shows the stricter subset in the event's own nakshatras - see
`_year_data`). The "no muhurat
during Chaturmas, 25 Jul - 20 Nov" sentences are built from the computed
period runs, never typed.

A year is ~550 panchang days (the year plus padding on both sides, so a period
like Kharmas that crosses 1 January shows its real start and end), about two
seconds of ephemeris work. It is computed once per process per page and kept
(`_year_data` is an lru_cache) - the content of a past or future year's list
does not change.

The shell mirrors seo_pages._render (same style, AdSense, visit.js beacon,
footer) and adds what a bilingual pair needs: <html lang>, hreflang alternates
and a language switch. seo_pages has no share-button helper on main, so there
is none here either.
"""

from __future__ import annotations

import datetime as dt
import functools
import json
from dataclasses import dataclass

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from . import seo_cities, seo_pages
from .astro import muhurat
from .astro import panchang as panchang_engine
from .astro.muhurat import EVENT_PERIODS, NAKSHATRAS_HI, PERIODS, TITHI_HI, VARA_HI
from .legal import BRAND
from .seo_pages import ADSENSE_CLIENT, SITE_URL, _e, _footer

router = APIRouter()

CITY = seo_cities.DEFAULT                 # New Delhi
YEARS = (2026, 2027)
_PAD_DAYS = 90                            # longest period run (Venus asta) is ~75 days


@dataclass(frozen=True)
class Kind:
    slug: str
    event: str                            # astro.muhurat.EVENT_RULES key
    name_en: str
    name_hi: str
    noun_en: str                          # "wedding", "house-warming"


KINDS = {
    "vivah": Kind("vivah", "marriage", "Vivah Muhurat", "विवाह मुहूर्त", "wedding"),
    "griha-pravesh": Kind("griha-pravesh", "griha_pravesh", "Griha Pravesh Muhurat",
                          "गृह प्रवेश मुहूर्त", "house-warming"),
}

MONTHS_HI = ["जनवरी", "फरवरी", "मार्च", "अप्रैल", "मई", "जून", "जुलाई", "अगस्त",
             "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर"]
PAKSHA_HI = {"Shukla": "शुक्ल", "Krishna": "कृष्ण"}


def page_path(kind: str, year: int, lang: str = "en") -> str:
    return ("/hi" if lang == "hi" else "") + f"/muhurat/{kind}-{year}"


def page_paths() -> list[str]:
    """Every muhurat page, both languages - for the sitemap and the beacon."""
    return [page_path(k, y, lang) for y in YEARS for k in KINDS for lang in ("en", "hi")]


# --------------------------------------------------------------------------
# Data (computed once per process)
# --------------------------------------------------------------------------

@functools.lru_cache(maxsize=2048)
def _panchang(day: dt.date) -> dict:
    """New Delhi's almanac for one day, shared by both kinds and both years
    (the padding of one year overlaps the next). Read-only."""
    return panchang_engine.daily_panchang(day, CITY.latitude, CITY.longitude, CITY.timezone)


@functools.lru_cache(maxsize=8)
def _year_data(kind: str, year: int) -> dict:
    event = KINDS[kind].event
    rule = muhurat.EVENT_RULES[event]
    wanted = EVENT_PERIODS[event]
    first, last = dt.date(year, 1, 1), dt.date(year, 12, 31)

    months: dict[int, list[dict]] = {m: [] for m in range(1, 13)}
    month_periods: dict[int, set[str]] = {m: set() for m in range(1, 13)}
    # key -> list of [start, end] runs over the padded range
    runs: dict[str, list[list[dt.date]]] = {k: [] for k in PERIODS if k in wanted}
    open_run: dict[str, list[dt.date] | None] = dict.fromkeys(runs)

    day = first - dt.timedelta(days=_PAD_DAYS)
    stop = last + dt.timedelta(days=_PAD_DAYS)
    while day <= stop:
        p = _panchang(day)
        if first <= day <= last:
            r = muhurat.evaluate_day(event, day, CITY.latitude, CITY.longitude,
                                     CITY.timezone, p=p)
            keys = [x["key"] for x in r["excluded_periods"]]
            month_periods[day.month].update(keys)
            # A published list only names days in the event's own nakshatras
            # (vivah: Rohini, Mrigashira, Magha, U.Phalguni, Hasta, Swati,
            # Anuradha, Mula, U.Ashadha, U.Bhadrapada, Revati - Muhurta
            # Chintamani). The tool's score can still reach "Auspicious" on a
            # neutral nakshatra through tithi + weekday alone (Pushya, say,
            # which is classically barred for vivah), so the page lists the
            # stricter subset: every date here is "Auspicious" in the tool too.
            if (r["verdict"] == "Auspicious"
                    and p["nakshatra"][0]["name"] in rule.preferred_nakshatras):
                t = p["tithi"][0]
                months[day.month].append({
                    "date": day, "weekday": p["vara"]["weekday"],
                    "tithi": t["name"], "paksha": t["paksha"],
                    "nakshatra": p["nakshatra"][0]["name"],
                })
        else:
            keys = muhurat.day_periods(p, CITY.latitude, wanted=wanted)
        for k in runs:
            if k in keys:
                if open_run[k] is None:
                    open_run[k] = [day, day]
                    runs[k].append(open_run[k])
                else:
                    open_run[k][1] = day
            else:
                open_run[k] = None
        day += dt.timedelta(days=1)

    # Only the runs that touch the year itself are worth explaining.
    spans = sorted(
        ((s, e, k) for k, rs in runs.items() for s, e in rs if s <= last and e >= first),
        key=lambda x: x[0])
    return {"months": months, "month_periods": month_periods, "spans": spans,
            "count": sum(len(v) for v in months.values())}


# --------------------------------------------------------------------------
# Formatting
# --------------------------------------------------------------------------

def _d(day: dt.date, lang: str, with_year: bool = False) -> str:
    month = MONTHS_HI[day.month - 1] if lang == "hi" else day.strftime("%b")
    return f"{day.day} {month}" + (f" {day.year}" if with_year else "")


def _range(s: dt.date, e: dt.date, year: int, lang: str) -> str:
    cross = s.year != year or e.year != year
    if s == e:
        return _d(s, lang, cross)
    return f"{_d(s, lang, cross)} – {_d(e, lang, cross)}"


def _month_name(m: int, year: int, lang: str) -> str:
    return f"{MONTHS_HI[m - 1]} {year}" if lang == "hi" else f"{dt.date(year, m, 1):%B} {year}"


def _period_list(keys: set[str], lang: str) -> str:
    names = [PERIODS[k].name_hi if lang == "hi" else PERIODS[k].name_en
             for k in PERIODS if k in keys]
    return ", ".join(names)


def _month_section(kind: Kind, year: int, m: int, data: dict, lang: str) -> str:
    rows = data["months"][m]
    head = f"<h2>{_e(_month_name(m, year, lang))}</h2>"
    if not rows:
        why = data["month_periods"][m]
        if lang == "hi":
            text = (f"{_e(_month_name(m, year, lang))} में कोई {_e(kind.name_hi)} नहीं"
                    + (f" — {_e(_period_list(why, lang))}।" if why else
                       " — इस माह कोई दिन तिथि, नक्षत्र, वार व योग की शर्तें पूरी नहीं करता।"))
        else:
            text = (f"No {_e(kind.name_en.lower())} in {_e(_month_name(m, year, lang))}"
                    + (f" — {_e(_period_list(why, lang))}." if why else
                       " — no day this month passes the tithi, nakshatra, weekday and yoga checks."))
        return head + f'<p class="none">{text}</p>'
    if lang == "hi":
        th = "<tr><th>तिथि (दिनांक)</th><th>वार</th><th>तिथि</th><th>नक्षत्र</th></tr>"
    else:
        th = "<tr><th>Date</th><th>Day</th><th>Tithi</th><th>Nakshatra</th></tr>"
    body = []
    for r in rows:
        if lang == "hi":
            cells = (_d(r["date"], lang), VARA_HI.get(r["weekday"], r["weekday"]),
                     f'{PAKSHA_HI.get(r["paksha"], "")} {TITHI_HI.get(r["tithi"], r["tithi"])}',
                     NAKSHATRAS_HI.get(r["nakshatra"], r["nakshatra"]))
        else:
            cells = (_d(r["date"], lang), r["weekday"], f'{r["paksha"]} {r["tithi"]}',
                     r["nakshatra"])
        iso = r["date"].isoformat()
        body.append(f'<tr data-date="{iso}">' + "".join(f"<td>{_e(c)}</td>" for c in cells)
                    + "</tr>")
    return head + f'<div class="scroll"><table>{th}{"".join(body)}</table></div>'


def _periods_section(kind: Kind, year: int, data: dict, lang: str) -> str:
    items = []
    for s, e, k in data["spans"]:
        p = PERIODS[k]
        if lang == "hi":
            items.append(f"<li><strong>{_e(p.name_hi)}</strong>, {_e(_range(s, e, year, lang))} "
                         f"— {_e(p.about_hi)}।</li>")
        else:
            items.append(f"<li><strong>{_e(p.name_en)}</strong>, {_e(_range(s, e, year, lang))} "
                         f"— {_e(p.about_en)}.</li>")
    if lang == "hi":
        title = f"{year} में {kind.name_hi} कब नहीं है"
        intro = (f"इन अवधियों में कोई {_e(kind.name_hi)} नहीं होता। ये तिथियां पंचांग से गणना की "
                 "गई हैं (नई दिल्ली, सूर्योदय):")
    else:
        title = f"When there is no {kind.name_en.lower()} in {year}"
        intro = (f"No {_e(kind.name_en.lower())} is given during these periods. The dates are "
                 "computed from the panchang (New Delhi, sunrise):")
    return (f"<h2>{_e(title)}</h2><p>{intro}</p>"
            f'<ul class="periods">{"".join(items)}</ul>')


_EXTRA_STYLE = """
  .seo .lang { float: right; font-size: 13px; }
  .seo .none { color: var(--ink-faint); }
  .seo .periods li { margin-bottom: 4px; }
"""

_SHELL = """<!DOCTYPE html>
<html lang="{html_lang}"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{title}</title>
<meta name="description" content="{description}"/>
<link rel="canonical" href="{canonical}"/>
<link rel="alternate" hreflang="en-IN" href="{href_en}"/>
<link rel="alternate" hreflang="hi-IN" href="{href_hi}"/>
<link rel="alternate" hreflang="x-default" href="{href_en}"/>
<meta property="og:type" content="website"/>
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
  <a class="back" href="/">&larr; {brand}</a>
  <a class="lang" href="{other}" hreflang="{other_lang}">{other_label}</a>
  <nav class="crumbs" aria-label="Breadcrumb">{crumbs}</nav>
  {body}
</main>
{footer}
</body></html>"""


def _page(kind_slug: str, year: int, lang: str) -> HTMLResponse:
    kind = KINDS[kind_slug]
    data = _year_data(kind_slug, year)
    hi = lang == "hi"
    open_months = [m for m in range(1, 13) if data["months"][m]]
    months_txt = ", ".join(
        (MONTHS_HI[m - 1] if hi else dt.date(year, m, 1).strftime("%B")) for m in open_months)
    path = page_path(kind_slug, year, lang)
    href_en, href_hi = SITE_URL + page_path(kind_slug, year), SITE_URL + page_path(kind_slug, year, "hi")

    if hi:
        title = f"{kind.name_hi} {year}: शुभ तिथियां (नई दिल्ली) | {BRAND}"
        h1 = f"{kind.name_hi} {year}"
        description = (f"{year} के {kind.name_hi} — नई दिल्ली के लिए माहवार शुभ तिथियां, तिथि व "
                       f"नक्षत्र सहित। कुल {data['count']} तिथियां; चातुर्मास, खरमास, अधिक मास, "
                       "पितृ पक्ष और गुरु-शुक्र अस्त की अवधि भी।")
        intro = (f"<p>पंचांग के अनुसार {year} में नई दिल्ली के लिए <strong>{data['count']}</strong> "
                 f"{_e(kind.name_hi)} की तिथियां हैं, इन महीनों में: {_e(months_txt) or '—'}। "
                 "हर तिथि सूर्योदय के तिथि, नक्षत्र, वार, योग और भद्रा के शास्त्रीय नियमों से "
                 "जांची गई है, और चातुर्मास, खरमास, अधिक मास, पितृ पक्ष तथा गुरु-शुक्र अस्त की "
                 "अवधि को छोड़ा गया है।</p>")
        note = ("<p><strong>ध्यान दें:</strong> ये तिथियां नई दिल्ली के सूर्योदय पर आधारित हैं। "
                "दूसरे शहर में तिथि-नक्षत्र का समय बदलता है, और विवाह या गृह प्रवेश का सटीक "
                "मुहूर्त (लग्न) परिवार के पंडित जी से अवश्य दिखवाएं। अपने शहर की तिथियां "
                "मुहूर्त खोजक में देखें।</p>")
        cta = "अपने शहर के लिए शुभ मुहूर्त खोजें"
        crumbs = [("होम", "/"), (f"{kind.name_hi} {year}", path)]
        other, other_lang, other_label = page_path(kind_slug, year), "en", "Read in English"
        more_title = "और मुहूर्त"
    else:
        title = f"{kind.name_en} {year}: Auspicious {kind.noun_en.title()} Dates (New Delhi) | {BRAND}"
        h1 = f"{kind.name_en} {year}: auspicious {kind.noun_en} dates"
        description = (f"{kind.name_en} {year} for New Delhi — month-by-month auspicious "
                       f"{kind.noun_en} dates with tithi and nakshatra. {data['count']} dates; "
                       "Chaturmas, Kharmas, Adhik Maas, Pitru Paksha and Guru/Shukra asta explained.")
        intro = (f"<p>By the panchang there are <strong>{data['count']}</strong> "
                 f"{_e(kind.name_en.lower())} dates in {year} for New Delhi, in "
                 f"{_e(months_txt) or '—'}. Each date passes the classical checks on the sunrise "
                 "tithi, nakshatra, weekday, yoga and Bhadra, and falls outside Chaturmas, "
                 "Kharmas, Adhik Maas, Pitru Paksha and the combustion (asta) of Jupiter and "
                 "Venus.</p>")
        note = ("<p><strong>Timings vary by city.</strong> These dates are reckoned from New "
                "Delhi's sunrise; elsewhere a tithi or nakshatra can change on a different day. "
                "The exact muhurat (lagna) for a wedding or griha pravesh should be fixed by "
                "your family priest. Check your own city in the Muhurat Finder.</p>")
        cta = "Find muhurat for your city — free"
        crumbs = [("Home", "/"), (f"{kind.name_en} {year}", path)]
        other, other_lang, other_label = page_path(kind_slug, year, "hi"), "hi", "हिन्दी में पढ़ें"
        more_title = "More muhurat dates"

    links = []
    for y in YEARS:
        for k, kk in KINDS.items():
            if (k, y) != (kind_slug, year):
                label = f"{kk.name_hi} {y}" if hi else f"{kk.name_en} {y}"
                links.append(f'<li><a href="{page_path(k, y, lang)}">{_e(label)}</a></li>')
    links.append('<li><a href="/panchang">' + ("आज का पंचांग" if hi else "Today's Panchang")
                 + "</a></li>")
    links.append('<li><a href="/kundali-milan">' + ("कुंडली मिलान" if hi else "Kundali Milan")
                 + "</a></li>")

    cta_html = f'<a class="cta" href="/?open=muhurat">{_e(cta)}</a>'
    sub = (f'<p class="hi" lang="en">{_e(kind.name_en)} {year}</p>' if hi
           else f'<p class="hi" lang="hi">{_e(kind.name_hi)} {year}</p>')
    body = (f"<h1>{_e(h1)}</h1>{sub}"
            f'<p class="date">{_e(CITY.name_hi if hi else CITY.label)} · IST</p>'
            f'{intro}<div class="box">{note}</div>{cta_html}'
            + _periods_section(kind, year, data, lang)
            + "".join(_month_section(kind, year, m, data, lang) for m in range(1, 13))
            + cta_html
            + f'<h2>{_e(more_title)}</h2><ul class="links">{"".join(links)}</ul>')

    crumb_html = " › ".join(
        f'<a href="{_e(h)}">{_e(n)}</a>' if i < len(crumbs) - 1 else _e(n)
        for i, (n, h) in enumerate(crumbs))
    graph = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebPage", "name": title, "description": description,
         "url": SITE_URL + path, "inLanguage": "hi-IN" if hi else "en-IN",
         "isPartOf": {"@type": "WebSite", "name": BRAND, "url": SITE_URL + "/"}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE_URL + h}
            for i, (n, h) in enumerate(crumbs)]},
    ]}
    jsonld = json.dumps(graph, ensure_ascii=False).replace("</", "<\\/")
    page = _SHELL.format(
        html_lang="hi-IN" if hi else "en-IN", title=_e(title), description=_e(description),
        canonical=_e(SITE_URL + path), href_en=_e(href_en), href_hi=_e(href_hi),
        brand=_e(BRAND), site=_e(SITE_URL), og_locale="hi_IN" if hi else "en_IN",
        adsense=ADSENSE_CLIENT, style=seo_pages._STYLE + _EXTRA_STYLE, jsonld=jsonld,
        other=_e(other), other_lang=other_lang, other_label=_e(other_label),
        crumbs=crumb_html, body=body, footer=_footer())
    # The list for a whole year does not change day to day.
    return HTMLResponse(page, headers={"Cache-Control": "public, max-age=86400"})


def _not_found(lang: str) -> HTMLResponse:
    links = "".join(f'<li><a href="{p}">{_e(p)}</a></li>'
                    for p in page_paths() if p.startswith("/hi") == (lang == "hi"))
    html = (f'<!DOCTYPE html><html lang="en-IN"><head><meta charset="utf-8"/>'
            f'<meta name="viewport" content="width=device-width, initial-scale=1"/>'
            f"<title>Muhurat page not found — {_e(BRAND)}</title>"
            f'<link rel="stylesheet" href="/static/styles.css"/></head>'
            f'<body class="sacred"><main class="seo"><h1>Muhurat page not found</h1>'
            f'<ul>{links}</ul><p><a href="/?open=muhurat">Open the Muhurat Finder</a></p>'
            f"</main></body></html>")
    return HTMLResponse(html, status_code=404, headers={"Cache-Control": "no-store"})


def _dispatch(slug: str, lang: str) -> HTMLResponse:
    kind, _, year = slug.rpartition("-")
    if kind not in KINDS or not year.isdigit() or int(year) not in YEARS:
        return _not_found(lang)
    return _page(kind, int(year), lang)


@router.get("/muhurat/{slug}", response_class=HTMLResponse)
def muhurat_page(slug: str) -> HTMLResponse:
    return _dispatch(slug, "en")


@router.get("/hi/muhurat/{slug}", response_class=HTMLResponse)
def muhurat_page_hi(slug: str) -> HTMLResponse:
    return _dispatch(slug, "hi")
