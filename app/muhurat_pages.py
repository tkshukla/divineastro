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

from . import i18n, seo_cities, seo_pages
from .astro import muhurat
from .astro import panchang as panchang_engine
from .astro.muhurat import EVENT_PERIODS, PERIODS
from .legal import BRAND
# DIVASTRO-123: every word of these pages is in muhurat_text.TEXT, per language.
from .muhurat_text import MONTHS, TEXT
from .seo_pages import ADSENSE_CLIENT, SITE_URL, _e, _footer
from .share import seo_share

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


# The page text reads the names from muhurat_text ("kind.<slug>", "noun.<slug>");
# name_en/name_hi are kept for callers.
KINDS = {
    slug: Kind(slug, event, TEXT["en"][f"kind.{slug}"], TEXT["hi"][f"kind.{slug}"],
               TEXT["en"][f"noun.{slug}"])
    for slug, event in (("vivah", "marriage"), ("griha-pravesh", "griha_pravesh"))
}

MONTHS_HI = list(MONTHS["hi"])


def _tx(key: str, lang: str, **values) -> str:
    """This module's text for `key` in `lang` (muhurat_text.TEXT), formatted."""
    return i18n.fmt(key, lang, TEXT, **values)


def _kind_vars(kind: Kind, lang: str) -> dict:
    """{name} {name_lower} {noun} {noun_title} in `lang`, plus {name_en} {name_hi}."""
    name, noun = _tx(f"kind.{kind.slug}", lang), _tx(f"noun.{kind.slug}", lang)
    return {"name": name, "name_lower": name.lower(), "noun": noun, "noun_title": noun.title(),
            "name_en": _tx(f"kind.{kind.slug}", "en"), "name_hi": _tx(f"kind.{kind.slug}", "hi")}


# DIVASTRO-121: the languages these pages are really written in (app/i18n.py).
# /<code>/muhurat/... exists for every registry language; an untranslated one
# shows the English text, noindex, outside the sitemap and hreflang.
TRANSLATED = i18n.BASE_TRANSLATED | {"kn", "te", "ta", "ml", "bn", "or"}  # DIVASTRO-123
i18n.LOCALIZABLE_ROOTS.add("muhurat")


def page_path(kind: str, year: int, lang: str = "en") -> str:
    return i18n.prefix(lang) + f"/muhurat/{kind}-{year}"


def page_paths() -> list[str]:
    """Every indexable muhurat page, every TRANSLATED language - for the sitemap
    and the beacon."""
    return [page_path(k, y, lang) for y in YEARS for k in KINDS
            for lang in i18n.ordered(TRANSLATED)]


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
    return (i18n.format_date(day, lang, short=True, months=MONTHS.get(lang))
            + (f" {day.year}" if with_year else ""))


def _range(s: dt.date, e: dt.date, year: int, lang: str) -> str:
    cross = s.year != year or e.year != year
    if s == e:
        return _d(s, lang, cross)
    return f"{_d(s, lang, cross)} – {_d(e, lang, cross)}"


def _month_name(m: int, year: int, lang: str) -> str:
    return f"{i18n.month_name(m, lang, MONTHS.get(lang))} {year}"


def _period_list(keys: set[str], lang: str) -> str:
    return ", ".join(_tx(f"period.{k}", lang) for k in PERIODS if k in keys)


def _month_section(kind: Kind, year: int, m: int, data: dict, lang: str) -> str:
    rows = data["months"][m]
    head = f"<h2>{_e(_month_name(m, year, lang))}</h2>"
    kv = {k: _e(v) for k, v in _kind_vars(kind, lang).items()}
    if not rows:
        why = data["month_periods"][m]
        month = _e(_month_name(m, year, lang))
        text = (_tx("none.periods", lang, **kv, month=month, periods=_e(_period_list(why, lang)))
                if why else _tx("none.plain", lang, **kv, month=month))
        return head + f'<p class="none">{text}</p>'
    n = i18n.names(lang)
    body = []
    for r in rows:
        cells = (_d(r["date"], lang), n.VARA.get(r["weekday"], r["weekday"]),
                 f'{n.PAKSHA.get(r["paksha"], "")} {n.TITHI.get(r["tithi"], r["tithi"])}',
                 n.NAKSHATRAS.get(r["nakshatra"], r["nakshatra"]))
        iso = r["date"].isoformat()
        body.append(f'<tr data-date="{iso}">' + "".join(f"<td>{_e(c)}</td>" for c in cells)
                    + "</tr>")
    return head + f'<div class="scroll"><table>{_tx("th", lang)}{"".join(body)}</table></div>'


def _periods_section(kind: Kind, year: int, data: dict, lang: str) -> str:
    items = [_tx("periods.item", lang, period=_e(_tx(f"period.{k}", lang)),
                 range=_e(_range(s, e, year, lang)), about=_e(_tx(f"period_about.{k}", lang)))
             for s, e, k in data["spans"]]
    kv = _kind_vars(kind, lang)
    title = _tx("periods.h2", lang, **kv, year=year)
    intro = _tx("periods.intro", lang, **{k: _e(v) for k, v in kv.items()})
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
{alternates}{head_extras}<meta property="og:type" content="website"/>
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
  <div class="top"><a class="back" href="{home}">&larr; {brand}</a>{picker}</div>
  <nav class="crumbs" aria-label="Breadcrumb">{crumbs}</nav>
  {notice}
  {body}
</main>
{footer}
</body></html>"""


def _page(kind_slug: str, year: int, lang: str) -> HTMLResponse:
    kind = KINDS[kind_slug]
    data = _year_data(kind_slug, year)
    open_months = [m for m in range(1, 13) if data["months"][m]]
    months_txt = ", ".join(i18n.month_name(m, lang, MONTHS.get(lang)) for m in open_months)
    path = page_path(kind_slug, year, lang)
    bits = seo_pages.page_language_bits(lang=lang, path=path, has_twin=True,
                                        translated=TRANSLATED, region=True)

    kv = _kind_vars(kind, lang)
    raw = {**kv, "year": year, "count": data["count"], "brand": BRAND}
    title = _tx("title", lang, **raw)
    h1 = _tx("h1", lang, **raw)
    description = _tx("desc", lang, **raw)
    esc = {**{k: _e(v) for k, v in kv.items()}, "year": year, "count": data["count"]}
    intro = _tx("intro", lang, **esc, months=_e(months_txt) or "—")
    note = _tx("note", lang)
    crumbs = [(i18n.chrome("home", lang), "/"), (_tx("crumb", lang, **raw), path)]

    links = []
    for y in YEARS:
        for k, kk in KINDS.items():
            if (k, y) != (kind_slug, year):
                label = _tx("link.kind", lang, **_kind_vars(kk, lang), year=y)
                links.append(f'<li><a href="{page_path(k, y, lang)}">{_e(label)}</a></li>')
    links.append(f'<li><a href="/panchang">{_tx("link.panchang", lang)}</a></li>')
    links.append(f'<li><a href="/kundali-milan">{_tx("link.milan", lang)}</a></li>')

    cta_html = f'<a class="cta" href="/?open=muhurat">{_e(_tx("cta", lang))}</a>'
    place = _tx("place", lang, city=seo_cities.city_name(CITY, lang), label=CITY.label)
    body = (f"<h1>{_e(h1)}</h1>{_tx('sub', lang, **esc)}"
            f'<p class="date">{_e(place)}</p>'
            f'{intro}<div class="box">{note}</div>{cta_html}'
            + _periods_section(kind, year, data, lang)
            + "".join(_month_section(kind, year, m, data, lang) for m in range(1, 13))
            + cta_html
            + f'<h2>{_e(_tx("more", lang))}</h2><ul class="links">{"".join(links)}</ul>')

    crumb_html = " › ".join(
        f'<a href="{_e(h)}">{_e(n)}</a>' if i < len(crumbs) - 1 else _e(n)
        for i, (n, h) in enumerate(crumbs))
    graph = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebPage", "name": title, "description": description,
         "url": SITE_URL + path, "inLanguage": bits["in_language"],
         "isPartOf": {"@type": "WebSite", "name": BRAND, "url": SITE_URL + "/"}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE_URL + h}
            for i, (n, h) in enumerate(crumbs)]},
    ]}
    jsonld = json.dumps(graph, ensure_ascii=False).replace("</", "<\\/")
    page = _SHELL.format(
        html_lang=bits["in_language"], title=_e(title), description=_e(description),
        canonical=_e(SITE_URL + path), alternates=bits["alternates"], head_extras=bits["head"],
        brand=_e(BRAND), site=_e(SITE_URL), og_locale=bits["og_locale"],
        adsense=ADSENSE_CLIENT, style=seo_pages._STYLE + _EXTRA_STYLE, jsonld=jsonld,
        home=_e(bits["home"]), picker=bits["picker"], notice=bits["notice"],
        crumbs=i18n.localize_links(crumb_html, lang),
        body=seo_share(path) + i18n.localize_links(body, lang), footer=_footer(lang))
    # The list for a whole year does not change day to day.
    return HTMLResponse(page, headers={"Cache-Control": "public, max-age=86400"})


def _not_found(lang: str) -> HTMLResponse:
    links = "".join(f'<li><a href="{p}">{_e(p)}</a></li>'
                    for p in (page_path(k, y, lang) for y in YEARS for k in KINDS))
    html = (f'<!DOCTYPE html><html lang="en-IN"><head><meta charset="utf-8"/>'
            f'<meta name="viewport" content="width=device-width, initial-scale=1"/>'
            f"<title>{_e(_tx('nf.title', 'en'))} — {_e(BRAND)}</title>"
            f'<link rel="stylesheet" href="/static/styles.css"/></head>'
            f'<body class="sacred"><main class="seo"><h1>{_e(_tx("nf.title", "en"))}</h1>'
            f'<ul>{links}</ul><p><a href="/?open=muhurat">{_e(_tx("nf.open", "en"))}</a></p>'
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


@router.get("/{lang:xlang}/muhurat/{slug}", response_class=HTMLResponse)
def muhurat_page_lang(lang: str, slug: str) -> HTMLResponse:
    """DIVASTRO-121: /kn/muhurat/vivah-2026 etc. (English text until translated)."""
    return _dispatch(slug, lang)
