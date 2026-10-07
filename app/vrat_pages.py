"""Vrat and tyohar (fasts and festivals) pages, English and Hindi (DIVASTRO-111).

    /vrat-tyohar                 today's vrat/festival + the next 30 days (New Delhi)
    /vrat-tyohar/<city>          the same for each of the 114 seo_cities, timings for
                                 that city (DIVASTRO-114; new-delhi = the bare URL)
    /vrat-tyohar/2026, /2027     the whole year, month by month
    /tyohar/<festival>-<year>    one major festival: date, puja muhurat, what/how
    /ekadashi-2026, -2027        every Ekadashi with its parana time
    /hi/...                      a Hindi copy of each
    GET /api/vrat/today          the home Today strip's one-liner (any city)
    GET /api/vrat/day            one date's observances with their timings (Panchang tool)

"aaj kaun sa vrat hai", "ekadashi kab hai", "diwali puja muhurat 2026" are
daily searches; the answer is a date and a time, so both are in the raw HTML.
Every date and time comes from `astro.festivals` for New Delhi, whose rules
were checked against Drik Panchang (tests/test_festivals.py); anything that
could not be validated is switched off there and never reaches a page.

A year is ~0.4 s of ephemeris work, computed once per process per city
(`festivals._year` is an lru_cache) - the first request warms it. The city
pages compute only their 31 days (`festivals.window`, ~40 ms cold), cached per
(city, day) here; nothing is precomputed at startup.

Rich results (DIVASTRO-114): each festival page carries schema.org Event
(startDate/endDate = the puja muhurat window for New Delhi when the festival
has one, else the day itself) and a FAQPage whose answers are printed on the
page; the year and Ekadashi lists carry an ItemList. Only validated values
from astro.festivals are used - nothing OMITTED can reach the markup.

The shell is seo_pages._render: same style, AdSense, visit.js beacon, share
button, hreflang pair and footer(lang) as the other SEO pages.
"""

from __future__ import annotations

import datetime as dt
import functools
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Query
from fastapi.responses import HTMLResponse, JSONResponse

from . import geo, push, seo_cities, seo_pages
from .astro import festivals
from .legal import BRAND
from .seo_cities import City
from .seo_pages import EN, HI, SITE_URL, _e, _long_date, _short_date
from . import i18n
# DIVASTRO-123: every word of these pages is in vrat_text (TEXT, ABOUT, NOTES),
# per language; names of festivals, timings, tithis, weekdays and months come
# from app/astro/names_<code>.py (i18n.names).
from . import vrat_text
from .vrat_text import TEXT

# DIVASTRO-121: the languages these pages are really written in (app/i18n.py).
# /<code>/vrat-tyohar etc. exist for every registry language; one not listed here
# renders the English text with noindex, no hreflang and no sitemap entry. Add a
# code here once vrat_text has that language's text.
TRANSLATED = i18n.BASE_TRANSLATED | {"kn", "te", "ta", "ml", "bn", "or"}  # DIVASTRO-123
i18n.LOCALIZABLE_ROOTS.update({"vrat-tyohar", "tyohar", "ekadashi-"})


def _render(**kw):
    """seo_pages._render with this module's TRANSLATED set."""
    return seo_pages._render(translated=TRANSLATED, **kw)

router = APIRouter()

CITY = seo_cities.DEFAULT                 # New Delhi
YEARS = (2026, 2027)
UPCOMING_DAYS = 30

# What each major festival is, and where traditions differ: slug -> English
# text (the other languages are in vrat_text.ABOUT / vrat_text.NOTES).
ABOUT = vrat_text.ABOUT["en"]
TRADITION_NOTE = vrat_text.NOTES["en"]


def _tx(key: str, lang: str, **values) -> str:
    """This module's text for `key` in `lang` (vrat_text.TEXT), formatted."""
    return i18n.fmt(key, lang, TEXT, **values)



# --------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------

def _pre(lang: str) -> str:
    return i18n.prefix(lang)


def hub_path(lang: str = EN) -> str:
    return _pre(lang) + "/vrat-tyohar"


def year_path(year: int, lang: str = EN) -> str:
    return _pre(lang) + f"/vrat-tyohar/{year}"


def city_path(city: City, lang: str = EN) -> str:
    """The default city's page is the bare hub URL (like /panchang)."""
    return hub_path(lang) + ("" if city == CITY else f"/{city.slug}")


def ekadashi_path(year: int, lang: str = EN) -> str:
    return _pre(lang) + f"/ekadashi-{year}"


def festival_path(slug: str, year: int, lang: str = EN) -> str:
    return _pre(lang) + f"/tyohar/{slug}-{year}"


def _year_obs(year: int) -> tuple[dict, ...]:
    return festivals._year(year, round(CITY.latitude, 4), round(CITY.longitude, 4),
                           CITY.timezone)


def festival_index(year: int) -> dict[str, dict]:
    """slug -> the observance, for every major festival dated in `year`."""
    out: dict[str, dict] = {}
    for o in _year_obs(year):
        if o["major"] and o["slug"] and o["slug"] not in out:
            out[o["slug"]] = o
    return out


def _festival_slugs(year: int) -> list[str]:
    """Pages that exist for a year, WITHOUT computing the year (used by the
    sitemap and the beacon, which must stay cheap): every major spec not
    switched off, plus Devuthani Ekadashi and Makar Sankranti."""
    keys_off = set(festivals.OMITTED)
    slugs = [s.slug for s in festivals.FESTIVALS if s.key not in keys_off and s.slug]
    slugs += ["devuthani-ekadashi", "makar-sankranti", "lohri"]
    if "holi" not in keys_off:
        slugs.append("holi")
    return slugs


def festival_names() -> dict[str, tuple[str, str]]:
    """slug -> (English, Hindi) name, for the share text. No ephemeris work."""
    out = {s.slug: (s.name_en, s.name_hi) for s in festivals.FESTIVALS if s.slug}
    out["devuthani-ekadashi"] = ("Devuthani Ekadashi", "देवउठनी एकादशी")
    out["makar-sankranti"] = ("Makar Sankranti", "मकर संक्रांति")
    out["lohri"] = ("Lohri", "लोहड़ी")
    out["holi"] = ("Holi", "होली")
    return out


def page_paths() -> list[str]:
    """Every indexable page, every TRANSLATED language - for the sitemap and the beacon."""
    out = []
    for lang in i18n.ordered(TRANSLATED):
        out.append(hub_path(lang))
        for y in YEARS:
            out.append(year_path(y, lang))
            out.append(ekadashi_path(y, lang))
            out += [festival_path(s, y, lang) for s in _festival_slugs(y)]
        out += [city_path(c, lang) for c in seo_cities.CITIES if c != CITY]
    return out


# /vrat-tyohar/new-delhi renders (canonical: the bare URL) but is not in the sitemap.
_PUBLIC = frozenset(page_paths() + [hub_path(lang) + f"/{CITY.slug}"
                                    for lang in i18n.ordered(TRANSLATED)])


def is_public_path(path: str) -> bool:
    if path in _PUBLIC:
        return True
    from . import vrat_city_pages              # lazy: it imports this module (DIVASTRO-140)
    return vrat_city_pages.is_public_path(path)


# --------------------------------------------------------------------------
# Formatting
# --------------------------------------------------------------------------

def _date(o: dict) -> dt.date:
    return dt.date.fromisoformat(o["date"])


def _name(o: dict, lang: str) -> str:
    """The observance's name: the engine's own `name_<lang>` (en, hi), else the
    names_<code>.FESTIVALS / EKADASHI name, else English."""
    return o.get(f"name_{lang}") or i18n.names(lang).festival_name(o)


def _rule(o: dict, lang: str) -> str:
    """How the date is fixed: festivals.py's `rule_<lang>` (en, hi); else composed
    from vrat_text.RULES[lang] with the language's month/paksha/tithi names
    (DIVASTRO-123); English otherwise."""
    if o.get(f"rule_{lang}"):
        return o[f"rule_{lang}"]
    rules = vrat_text.RULES.get(lang, {})
    if rules.get(f"key.{o.get('key')}"):
        return rules[f"key.{o['key']}"]
    t, tail = o.get("tithi"), rules.get(f"rule.{o.get('rule')}")
    if not (t and tail):
        return o["rule_en"]
    n = i18n.names(lang)
    words = rules["tithi"].format(paksha=n.PAKSHA.get(t["paksha"], t["paksha"]),
                                  tithi=n.TITHI.get(t["name"], t["name"]))
    month = o.get("month")
    if month and o["rule_en"].startswith(f"{month['name']} (amanta) "):
        words = rules["head"].format(month=n.MASA.get(month["name"], month["name"])) + words
    return words + tail


def _local_text(table: dict, key: str, lang: str) -> str:
    """vrat_text.ABOUT / NOTES for `lang`, English where it has none."""
    return table.get(lang, {}).get(key) or table["en"].get(key, "")


def _weekday(day: dt.date, lang: str) -> str:
    return i18n.weekday(day, lang)


def _day_label(day: dt.date, lang: str, year: bool = False) -> str:
    text = _long_date(day, lang) if year else _short_date(day, lang)
    return _tx("day_label", lang, date=text, weekday=_weekday(day, lang))


def _clock(iso: str, ref: dt.date, lang: str) -> str:
    return seo_pages._time(iso, ref, lang)


def _city(city: City, lang: str) -> str:
    return seo_cities.city_name(city, lang)


def _city_label(city: City, lang: str) -> str:
    """The date line's place: the city in `lang` ('नई दिल्ली'), or 'New Delhi, Delhi'."""
    return seo_cities.city_name(city, lang) if seo_cities.has_name(city, lang) else city.label


def _timing_text(t: dict, day: dt.date, lang: str) -> str:
    label = (t.get(f"label_{lang}") or i18n.names(lang).FESTIVAL_TIMINGS.get(t.get("key"))
             or t["label_en"])
    ref = dt.date.fromisoformat(t["date"]) if t.get("date") else day
    prefix = f"{_short_date(ref, lang)}, " if ref != day else ""
    if t.get("at"):
        value = _clock(t["at"], ref, lang)
    else:
        value = f"{_clock(t['start'], ref, lang)} – {_clock(t['end'], ref, lang)}"
    return _tx("timing", lang, label=label, prefix=prefix, value=value)


def _timings(o: dict, lang: str, first_only: bool = False) -> str:
    day = _date(o)
    items = o["timings"][:1] if first_only else o["timings"]
    return " · ".join(_timing_text(t, day, lang) for t in items)


def _tithi_text(o: dict, lang: str) -> str:
    t = o.get("tithi")
    if not t:
        return ""
    day = _date(o)
    n = i18n.names(lang)
    paksha = _tx("tithi.paksha", lang, paksha=n.PAKSHA.get(t["paksha"], t["paksha"]))
    return _tx("tithi.text", lang, paksha=paksha, name=n.TITHI.get(t["name"], t["name"]),
               start=_clock(t['start'], day, lang), end=_clock(t['end'], day, lang))


def _link_for(o: dict, lang: str) -> str | None:
    if o["major"] and o["slug"]:
        y = _date(o).year
        if y in YEARS and o["slug"] in _festival_slugs(y):
            return festival_path(o["slug"], y, lang)
    if o["key"] == "ekadashi" and _date(o).year in YEARS:
        return ekadashi_path(_date(o).year, lang)
    return None


def _name_html(o: dict, lang: str) -> str:
    href = _link_for(o, lang)
    name = _e(_name(o, lang))
    return f'<a href="{_e(href)}">{name}</a>' if href else name


def _table(rows: list[dict], lang: str, city: City = CITY) -> str:
    th = _tx("table.th", lang, city=_e(_city(city, lang)))
    body = []
    for o in rows:
        day = _date(o)
        body.append(
            f'<tr data-date="{o["date"]}" data-key="{_e(o["key"])}">'
            f"<td>{_e(_day_label(day, lang))}</td>"
            f"<td>{_name_html(o, lang)}</td>"
            f"<td>{_e(_timings(o, lang, first_only=True)) or '—'}</td></tr>")
    return f'<div class="scroll"><table>{th}{"".join(body)}</table></div>'


def _city_note(lang: str, city: City = CITY) -> str:
    return _tx("city_note", lang, city=_e(_city(city, lang)))


def _top_note(city: City, lang: str) -> str:
    """Above the list on the hub and city pages: what changes from city to city."""
    return _tx("top_note", lang, city=_e(_city(city, lang)))


def _city_index(lang: str, current: City | None = None) -> str:
    """Every city's vrat-tyohar page, grouped by state (as on the /panchang pages)."""
    groups = []
    for state, cities in seo_cities.by_state():
        items = "".join(
            f'<li><a href="{_e(city_path(c, lang))}"'
            + (' aria-current="page"' if c == current else "")
            + f">{_e(_city(c, lang))}</a></li>" for c in cities)
        label = seo_cities.state_name(state, lang)
        groups.append(f'<dt>{_e(label)}</dt><dd><ul class="links">{items}</ul></dd>')
    return f'<h2>{_e(_tx("cities.heading", lang))}</h2><dl class="cities">{"".join(groups)}</dl>'


def _city_tools(city: City, lang: str) -> str:
    """The same city's Panchang and Rahu Kaal pages."""
    name = _city(city, lang)
    links = [(seo_pages._path("panchang", city, lang), _tx("tools.panchang", lang, city=name)),
             (seo_pages._path("rahu-kaal", city, lang), _tx("tools.rahu", lang, city=name))]
    items = "".join(f'<li><a href="{_e(h)}">{_e(t)}</a></li>' for h, t in links)
    return f'<h2>{_e(_tx("tools.heading", lang, city=name))}</h2><ul class="links">{items}</ul>'


def _cta(lang: str) -> str:
    # DIVASTRO-112: the opt-in daily push button ("" while push is switched off).
    return (f'<a class="cta" href="{_e(seo_pages._app_link("panchang", lang))}">'
            f'{_e(_tx("cta", lang))}</a>' + push.optin_html(lang))


def _more_links(lang: str, skip: str = "") -> str:
    links = [(hub_path(lang), _tx("more.today", lang))]
    for y in YEARS:
        links.append((year_path(y, lang), _tx("more.year", lang, year=y)))
        links.append((ekadashi_path(y, lang), _tx("more.ekadashi", lang, year=y)))
    links.append((_pre(lang) + "/panchang", _tx("more.panchang", lang)))
    links.append((_pre(lang) + "/rashifal", _tx("more.rashifal", lang)))
    items = "".join(f'<li><a href="{_e(h)}">{_e(t)}</a></li>' for h, t in links if h != skip)
    return f'<h2>{_tx("more.heading", lang)}</h2><ul class="links">{items}</ul>'


def _festival_links(year: int, lang: str, skip: str = "") -> str:
    idx = festival_index(year)
    items = "".join(
        f'<li><a href="{_e(festival_path(s, year, lang))}">{_e(_name(o, lang))}</a></li>'
        for s, o in sorted(idx.items(), key=lambda kv: kv[1]["date"])
        if s != skip and s in _festival_slugs(year))
    return f'<h2>{_e(_tx("majors.heading", lang, year=year))}</h2><ul class="links">{items}</ul>'


# --------------------------------------------------------------------------
# Structured data: Event, FAQPage, ItemList (DIVASTRO-114)
# --------------------------------------------------------------------------
#
# Google's Event rich result: required name, startDate, location (a Place
# with an address); recommended description, endDate, eventAttendanceMode,
# eventStatus, image, organizer (offers/performer do not apply to a festival
# and are left out rather than invented). Times are ISO 8601 with +05:30; a
# festival with no validated puja window is a date-only, whole-day event.

def _muhurat_window(o: dict) -> dict | None:
    """The festival's main puja window on its own day, if it has one (not a
    moment like moonrise, nor the next morning's parana)."""
    for t in o["timings"]:
        if (t.get("start") and t.get("end") and t["key"] != "parana"
                and t.get("date", o["date"]) == o["date"] and t["start"][:10] == o["date"]):
            return t
    return None


def _event_dates(o: dict) -> tuple[str, str]:
    if o["slug"] == "pitru-paksha":                    # a fortnight: ends on Sarva Pitru Amavasya
        last = festival_index(_date(o).year).get("sarva-pitru-amavasya")
        return o["date"], last["date"] if last and last["date"] >= o["date"] else o["date"]
    w = _muhurat_window(o)
    return (w["start"], w["end"]) if w else (o["date"], o["date"])


def event_ld(o: dict, lang: str) -> dict:
    """schema.org Event for a festival page: an observance kept across India on
    this date, with New Delhi's puja muhurat as its start/end when it has one."""
    year = _date(o).year
    start, end = _event_dates(o)
    about = _local_text(vrat_text.ABOUT, o["slug"], lang)
    return {
        "@type": "Event",
        "name": f"{_name(o, lang)} {year}",
        "startDate": start,
        "endDate": end,
        "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
        "eventStatus": "https://schema.org/EventScheduled",
        "location": {"@type": "Place", "name": _tx("event.place", lang),
                     "address": {"@type": "PostalAddress", "addressCountry": "IN"}},
        "description": about or _rule(o, lang),
        "image": [f"{SITE_URL}/static/icon-512.png"],
        "organizer": {"@type": "Organization", "name": BRAND, "url": SITE_URL + "/"},
        "url": SITE_URL + festival_path(o["slug"], year, lang),
        "inLanguage": i18n.get(lang).bcp47,
    }


# Timings that are moments or the next morning, not a muhurat to do the puja in.
_NOT_MUHURAT = frozenset({"moonrise", "sandhya_arghya", "usha_arghya", "parana"})


def faq_items(o: dict, lang: str) -> tuple[tuple[str, str], ...]:
    """When / muhurat / why, answered only from the validated observance: no
    timing question when the festival has no validated timing (OMITTED ones
    were already stripped by the engine)."""
    day = _date(o)
    v = {"name": _name(o, lang), "year": day.year, "rule": _rule(o, lang),
         "when": _day_label(day, lang, year=True), "weekday": _weekday(day, lang),
         "date": _long_date(day, lang), "short": _short_date(day, lang)}
    timings = "; ".join(_timing_text(t, day, lang) for t in o["timings"])
    has_muhurat = any(t["key"] not in _NOT_MUHURAT for t in o["timings"])
    out = [(_tx("faq.when_q", lang, **v), _tx("faq.when_a", lang, **v))]
    if timings:
        q = _tx("faq.muhurat_q" if has_muhurat else "faq.timings_q", lang, **v)
        out.append((q, _tx("faq.timings_a", lang, timings=timings)))
    out.append((_tx("faq.why_q", lang, **v), _tx("faq.why_a", lang, **v)))
    return tuple(out)


def item_list_ld(name: str, items: list[tuple[str, str | None]]) -> dict:
    """A plain ItemList of (name, page path or None). Google shows Event rich
    results only from each event's own page, so the list pages carry a summary
    list, not Event items."""
    return {"@type": "ItemList", "name": name, "numberOfItems": len(items),
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": n,
                 **({"url": SITE_URL + href} if href else {})}
                for i, (n, href) in enumerate(items)]}


# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------

def _today() -> dt.date:
    return seo_pages._today()


def _obs_range(start: dt.date, end: dt.date) -> list[dict]:
    return festivals.observances(start, end, CITY.latitude, CITY.longitude, CITY.timezone)


def _today_block(today: dt.date, todays: list[dict], nxt: dict | None, lang: str) -> str:
    if todays:
        parts = []
        for o in todays:
            timing = _timings(o, lang)
            parts.append(
                f'<h3>{_name_html(o, lang)}</h3>'
                + (f"<p>{_e(timing)}</p>" if timing else "")
                + (f"<p><small>{_e(_tithi_text(o, lang))}</small></p>" if o.get("tithi") else "")
                + f'<p><small>{_tx("today.rule", lang)}: {_e(_rule(o, lang))}</small></p>')
        return '<div class="box today">' + "".join(parts) + "</div>"
    text = _tx("today.none", lang)
    if nxt:
        text += _tx("today.next", lang, name=_name_html(nxt, lang),
                    day=_e(_day_label(_date(nxt), lang)))
    return f'<div class="box today"><p>{text}</p></div>'


@functools.lru_cache(maxsize=512)
def _city_upcoming(slug: str, today: dt.date) -> tuple[dict, ...]:
    """A city's today + next 30 days, ~40 ms cold. Keyed on the day, so old
    entries simply stop being asked for after midnight and age out (114 cities
    x a couple of days fits). Read-only, like everything from festivals."""
    c = seo_cities.BY_SLUG[slug]
    return tuple(festivals.window(today, today + dt.timedelta(days=UPCOMING_DAYS),
                                  c.latitude, c.longitude, c.timezone))


def _upcoming(city: City, today: dt.date) -> list[dict]:
    if city == CITY:                                   # the year cache, as before
        return _obs_range(today, today + dt.timedelta(days=UPCOMING_DAYS))
    return list(_city_upcoming(city.slug, today))


def render_hub(lang: str, today: dt.date | None = None, city: City = CITY) -> HTMLResponse:
    """/vrat-tyohar (New Delhi) and /vrat-tyohar/<city>: today + the next 30 days
    with every timing for that city."""
    today = today or _today()
    upcoming = _upcoming(city, today)
    todays = [o for o in upcoming if o["date"] == today.isoformat()]
    later = [o for o in upcoming if o["date"] > today.isoformat()]
    nxt = later[0] if later else None
    default = city == CITY
    path, alt = city_path(city, lang), city_path(city, EN if lang != EN else HI)
    names = ", ".join(_name(o, lang) for o in todays)
    cname = _city(city, lang)
    which = "default" if default else "city"
    title = _tx(f"hub.title_{which}", lang, city=cname, date=_short_date(today, lang))
    h1 = _tx(f"hub.h1_{which}", lang, city=cname)
    long_date = _long_date(today, lang)
    description = ((_tx("hub.desc_today", lang, date=long_date, names=names) if names
                    else _tx("hub.desc_none", lang, date=long_date))
                   + _tx("hub.desc_rest", lang, city=cname))
    body = (f"<h1>{_e(h1)}</h1>{_tx('hub.sub', lang)}"
            f'<p class="date">{_e(_day_label(today, lang, year=True))} · '
            f'{_e(_city_label(city, lang))}</p>'
            + _top_note(city, lang)
            + _today_block(today, todays, nxt, lang)
            + f"<h2>{_e(_tx('hub.upcoming', lang))}</h2>"
            + (_table(later, lang, city) if later else "<p>—</p>")
            + _city_note(lang, city) + _cta(lang) + _city_tools(city, lang)
            + _festival_links(today.year if today.year in YEARS else YEARS[0], lang)
            + _city_index(lang, city)
            + _more_links(lang, skip=path))
    crumbs = [(_tx("crumb", lang), hub_path(lang))]
    if not default:
        crumbs.append((cname, path))
    return _render(title=title, description=description, path=path, alt=alt, crumbs=crumbs,
                   body=body, lang=lang)


def render_year(year: int, lang: str) -> HTMLResponse:
    obs = _year_obs(year)
    path, alt = year_path(year, lang), year_path(year, EN if lang == HI else HI)
    title = _tx("year.title", lang, year=year)
    h1 = _tx("year.h1", lang, year=year)
    description = _tx("year.desc", lang, year=year)
    intro = _tx("year.intro", lang, year=year, count=len(obs))
    sections = []
    for m in range(1, 13):
        rows = [o for o in obs if _date(o).month == m]
        month = _tx("year.month", lang, month=i18n.month_name(m, lang), year=year)
        sections.append(f"<h2>{_e(month)}</h2>" + (_table(rows, lang) if rows else "<p>—</p>"))
    body = (f"<h1>{_e(h1)}</h1>"
            f'<p class="date">{_e(_city_label(CITY, lang))} · IST</p>'
            + intro + _city_note(lang) + "".join(sections) + _cta(lang)
            + _festival_links(year, lang) + _more_links(lang, skip=path))
    crumbs = [(_tx("crumb", lang), hub_path(lang)), (str(year), path)]
    majors = [(f"{_name(o, lang)} - {_long_date(_date(o), lang)}", festival_path(s, year, lang))
              for s, o in sorted(festival_index(year).items(), key=lambda kv: kv[1]["date"])
              if s in _festival_slugs(year)]
    items = item_list_ld(_tx("year.itemlist", lang, year=year), majors)
    return _render(title=title, description=description, path=path, alt=alt, crumbs=crumbs,
                   body=body, lang=lang, extra_ld=(items,))


def render_ekadashi(year: int, lang: str) -> HTMLResponse:
    eks = [o for o in _year_obs(year) if o["key"] == "ekadashi"]
    path, alt = ekadashi_path(year, lang), ekadashi_path(year, EN if lang == HI else HI)
    title = _tx("ek.title", lang, year=year)
    h1 = _tx("ek.h1", lang, year=year)
    description = _tx("ek.desc", lang, year=year, count=len(eks))
    rows = []
    for o in eks:
        day = _date(o)
        p = next((t for t in o["timings"] if t["key"] == "parana"), None)
        pday = dt.date.fromisoformat(p["date"]) if p else None
        parana = (f"{_day_label(pday, lang)}, {_clock(p['start'], pday, lang)} – "
                  f"{_clock(p['end'], pday, lang)}") if p else "—"
        rows.append(f'<tr data-date="{o["date"]}"><td><strong>{_e(_name(o, lang))}</strong>'
                    f"<small>{_e(_tithi_text(o, lang))}</small></td>"
                    f"<td>{_e(_day_label(day, lang))}</td><td>{_e(parana)}</td></tr>")
    body = (f"<h1>{_e(h1)}</h1>{_tx('ek.sub', lang, year=year)}"
            f'<p class="date">{_e(_city_label(CITY, lang))} · IST</p>'
            + _tx("ek.rule", lang)
            + f'<div class="scroll"><table>{_tx("ek.th", lang)}{"".join(rows)}</table></div>'
            + _city_note(lang) + _cta(lang) + _more_links(lang, skip=path))
    crumbs = [(_tx("crumb", lang), hub_path(lang)), (_tx("ek.crumb", lang, year=year), path)]
    items = item_list_ld(h1, [(f"{_name(o, lang)} - {_long_date(_date(o), lang)}",
                               _link_for(o, lang) if o.get("slug") else None) for o in eks])
    return _render(title=title, description=description, path=path, alt=alt, crumbs=crumbs,
                   body=body, lang=lang, extra_ld=(items,))


def _city_pills(slug: str, year: int, lang: str) -> str:
    from . import vrat_city_pages              # lazy: it imports this module (DIVASTRO-140)
    return vrat_city_pages.city_pills(slug, year, lang)


def render_festival(slug: str, year: int, lang: str) -> HTMLResponse:
    o = festival_index(year).get(slug)
    if o is None or slug not in _festival_slugs(year):
        return _not_found(lang)
    day = _date(o)
    name = _name(o, lang)
    path, alt = festival_path(slug, year, lang), festival_path(slug, year, EN if lang == HI else HI)
    main = o["timings"][0] if o["timings"] else None
    main_txt = _timing_text(main, day, lang) if main else ""
    v = {"name": name, "year": year, "short": _short_date(day, lang),
         "date": _long_date(day, lang), "weekday": _weekday(day, lang)}
    title = _tx("fest.title", lang, **v)
    h1 = _tx("fest.h1", lang, **v)
    description = _tx("fest.desc", lang, **v,
                      main=_tx("fest.main", lang, text=main_txt) if main_txt else "")
    when = _tx("fest.when", lang, name=_e(name), year=year,
               when=_e(_day_label(day, lang, year=True)))
    items = "".join(f"<li>{_e(_timing_text(t, day, lang))}</li>" for t in o["timings"])
    if o.get("tithi"):
        items += f"<li>{_e(_tithi_text(o, lang))}</li>"
    about = _local_text(vrat_text.ABOUT, slug, lang)
    note = (_local_text(vrat_text.NOTES, slug, lang) if slug in vrat_text.NOTES["en"]
            else _local_text(vrat_text.NOTES, o["key"], lang))
    rule = _rule(o, lang)
    faq_html, faq_ld = seo_pages._faq(faq_items(o, lang))
    sub = _tx("fest.sub", lang, name_en=_e(o["name_en"]), name_hi=_e(o["name_hi"]), year=year)
    body = (f"<h1>{_e(h1)}</h1>{sub}"
            f'<p class="date">{_e(_city_label(CITY, lang))} · IST</p>'
            f'<div class="box"><p>{when}</p>'
            + (f'<ul class="timings">{items}</ul>' if items else "") + "</div>"
            + (f"<h2>{_e(_tx('fest.about_h2', lang))}</h2><p>{_e(about)}</p>" if about else "")
            + f"<h2>{_e(_tx('fest.rule_h2', lang))}</h2><p>{_e(rule)}.</p>"
            + (f"<p><small>{_e(note)}</small></p>" if note else "")
            + f"<h2>{_e(_tx('fest.faq_h2', lang))}</h2>{faq_html}"
            + _city_note(lang) + _city_pills(slug, year, lang) + _cta(lang)
            + _festival_links(year, lang, skip=slug) + _more_links(lang))
    crumbs = [(_tx("crumb", lang), hub_path(lang)), (f"{name} {year}", path)]
    return _render(title=title, description=description, path=path, alt=alt, crumbs=crumbs,
                   body=body, lang=lang, extra_ld=(event_ld(o, lang), faq_ld), cache=True)


def _not_found(lang: str) -> HTMLResponse:
    cities = {city_path(c, lang) for c in seo_cities.CITIES}
    own = [p for p in page_paths() if i18n.strip_prefix(p)[0] == EN]
    links = "".join(f'<li><a href="{_e(i18n.localized_path(p, lang))}">'
                    f'{_e(i18n.localized_path(p, lang))}</a></li>'
                    for p in own if i18n.localized_path(p, lang) not in cities)
    body = (f"<h1>{_tx('nf.h1', lang)}</h1>"
            f'<ul class="links">{links}</ul>' + _city_index(lang))
    return _render(title="Not found", description="", path=hub_path(lang), crumbs=[],
                   body=body, lang=lang, status=404, cache=False)


# --------------------------------------------------------------------------
# Routes
# --------------------------------------------------------------------------

@router.get("/vrat-tyohar", response_class=HTMLResponse)
def hub() -> HTMLResponse:
    return render_hub(EN)


@router.get("/hi/vrat-tyohar", response_class=HTMLResponse)
def hub_hi() -> HTMLResponse:
    return render_hub(HI)


def _year_or_404(year: str, lang: str, fn) -> HTMLResponse:
    if not year.isdigit() or int(year) not in YEARS:
        return _not_found(lang)
    return fn(int(year), lang)


def _year_or_city(key: str, lang: str) -> HTMLResponse:
    """/vrat-tyohar/<year> or /vrat-tyohar/<city> (one route: both are one segment)."""
    if key.isdigit():
        return _year_or_404(key, lang, render_year)
    city = seo_cities.get(key)
    if city is None:
        return _not_found(lang)
    return render_hub(lang, city=city)


@router.get("/vrat-tyohar/{key}", response_class=HTMLResponse)
def year_page(key: str) -> HTMLResponse:
    return _year_or_city(key, EN)


@router.get("/hi/vrat-tyohar/{key}", response_class=HTMLResponse)
def year_page_hi(key: str) -> HTMLResponse:
    return _year_or_city(key, HI)


@router.get("/ekadashi-{year}", response_class=HTMLResponse)
def ekadashi_page(year: str) -> HTMLResponse:
    return _year_or_404(year, EN, render_ekadashi)


@router.get("/hi/ekadashi-{year}", response_class=HTMLResponse)
def ekadashi_page_hi(year: str) -> HTMLResponse:
    return _year_or_404(year, HI, render_ekadashi)


def _festival(slug_year: str, lang: str) -> HTMLResponse:
    slug, _, year = slug_year.rpartition("-")
    if not year.isdigit() or int(year) not in YEARS:
        return _not_found(lang)
    return render_festival(slug, int(year), lang)


@router.get("/tyohar/{slug}", response_class=HTMLResponse)
def festival_page(slug: str) -> HTMLResponse:
    return _festival(slug, EN)


@router.get("/hi/tyohar/{slug}", response_class=HTMLResponse)
def festival_page_hi(slug: str) -> HTMLResponse:
    return _festival(slug, HI)


# DIVASTRO-121: the same pages under /kn/, /te/, ... (i18n.EXTRA_CODES).
@router.get("/{lang:xlang}/vrat-tyohar", response_class=HTMLResponse)
def hub_lang(lang: str) -> HTMLResponse:
    return render_hub(lang)


@router.get("/{lang:xlang}/vrat-tyohar/{key}", response_class=HTMLResponse)
def year_page_lang(lang: str, key: str) -> HTMLResponse:
    return _year_or_city(key, lang)


@router.get("/{lang:xlang}/ekadashi-{year}", response_class=HTMLResponse)
def ekadashi_page_lang(lang: str, year: str) -> HTMLResponse:
    return _year_or_404(year, lang, render_ekadashi)


@router.get("/{lang:xlang}/tyohar/{slug}", response_class=HTMLResponse)
def festival_page_lang(lang: str, slug: str) -> HTMLResponse:
    return _festival(slug, lang)


@router.get("/api/vrat/today")
def vrat_today(
    lat: float = Query(CITY.latitude, ge=-90, le=90),
    lon: float = Query(CITY.longitude, ge=-180, le=180),
    tz: str = "",
) -> JSONResponse:
    """Today's vrat/festival names for the home Today strip. Never errors: a
    failure is an empty list, and the strip simply shows nothing."""
    items: list[dict] = []
    upcoming = None
    day = None
    try:
        zone = tz or geo.timezone_for(lat, lon)
        day = dt.datetime.now(ZoneInfo(zone)).date()
        items = [{"key": o["key"], "name_en": o["name_en"], "name_hi": o["name_hi"],
                  "major": o["major"]}
                 for o in festivals.on(day, lat, lon, zone)]
        # On an ordinary day the strip says what is coming next instead of
        # nothing, so the vrat-tyohar page is always one tap from home.
        if not items:
            nxt = next(iter(festivals.observances(day + dt.timedelta(days=1),
                                                   day + dt.timedelta(days=30), lat, lon, zone)), None)
            if nxt:
                when = dt.date.fromisoformat(nxt["date"])
                upcoming = {"date": nxt["date"], "name_en": nxt["name_en"],
                            "name_hi": nxt["name_hi"], "day_en": _short_date(when, EN),
                            "day_hi": _short_date(when, HI)}
    except Exception:                                  # pragma: no cover - defensive
        items = []
    body = {"date": day.isoformat() if day else None, "items": items, "next": upcoming,
            "url": hub_path(EN), "url_hi": hub_path(HI)}
    return JSONResponse(body, headers={"Cache-Control": "private, max-age=1800"})


# --------------------------------------------------------------------------
# One day's observances with their timings: the Panchang tool and pages
# --------------------------------------------------------------------------

DAY_RANGE_DAYS = 2 * 366              # /api/vrat/day answers within ~2 years of today


def _timing_json(t: dict, day: dt.date) -> dict:
    """A timing exactly as the engine validated it (nothing added, nothing
    invented), plus the other day's short label in EN/HI when it falls on
    another date (Ekadashi parana is the next morning)."""
    out = {k: t[k] for k in ("key", "label_en", "label_hi", "start", "end", "at", "date")
           if t.get(k)}
    if t.get("date") and t["date"] != day.isoformat():
        ref = dt.date.fromisoformat(t["date"])
        out["day_en"], out["day_hi"] = _short_date(ref, EN), _short_date(ref, HI)
    return out


def day_items(day: dt.date, lat: float, lon: float, tz: str) -> list[dict]:
    """The observances of `day` at a place, each with its timings and the page it
    links to (its festival or Ekadashi page, else the vrat-tyohar hub)."""
    return [{
        "key": o["key"], "name_en": o["name_en"], "name_hi": o["name_hi"], "major": o["major"],
        "url": _link_for(o, EN) or hub_path(EN), "url_hi": _link_for(o, HI) or hub_path(HI),
        "timings": [_timing_json(t, day) for t in o["timings"]],
    } for o in festivals.on(day, lat, lon, tz)]


def panchang_block(day: dt.date, lat: float, lon: float, tz: str, lang: str) -> str:
    """'Vrat & festivals today' for the server-rendered /panchang pages: each
    observance linked to its page, with its timings for this city. Empty on an
    ordinary day, and on any failure (the panchang itself must still render)."""
    try:
        rows = festivals.on(day, lat, lon, tz)
    except Exception:                                  # pragma: no cover - defensive
        return ""
    if not rows:
        return ""
    parts = []
    for o in rows:
        href = _link_for(o, lang) or hub_path(lang)
        times = "".join(f"<li>{_e(_timing_text(t, _date(o), lang))}</li>" for t in o["timings"])
        parts.append(f'<h3><a href="{_e(href)}">{_e(_name(o, lang))}</a></h3>'
                     + (f"<ul>{times}</ul>" if times else ""))
    heading = _tx("block.heading", lang)
    return f'<h2>{heading}</h2><div class="box today vrat-day">{"".join(parts)}</div>'


@router.get("/api/vrat/day")
def vrat_day(
    date: str = "",
    lat: float = Query(CITY.latitude, ge=-90, le=90),
    lon: float = Query(CITY.longitude, ge=-180, le=180),
    tz: str = "",
) -> JSONResponse:
    """One date's vrat/festivals at a place with every validated timing (puja
    muhurat, parana, moonrise, pradosh, nishita...) labelled in English and
    Hindi, for the Panchang tool's "Vrat & festivals" section. Never errors: a
    bad or far-off date, or any failure, is an empty list."""
    body: dict = {"date": None, "items": []}
    try:
        zone = tz or geo.timezone_for(lat, lon)
        today = dt.datetime.now(ZoneInfo(zone)).date()
        day = dt.date.fromisoformat(date) if date else today
        items = (day_items(day, lat, lon, zone)
                 if abs((day - today).days) <= DAY_RANGE_DAYS else [])
        body = {"date": day.isoformat(), "day_en": _long_date(day, EN),
                "day_hi": _long_date(day, HI), "items": items}
    except Exception:
        body = {"date": None, "items": []}
    return JSONResponse(body, headers={"Cache-Control": "private, max-age=1800"})
