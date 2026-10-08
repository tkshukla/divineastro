"""Year pages for the observances that come round every month (DIVASTRO-141).

    /purnima-2026            /amavasya-2026          /pradosh-vrat-2026
    /sankashti-chaturthi-2026   /masik-shivratri-2026   /kalashtami-2026
    (and 2027; each also under /hi/, /kn/, /te/, /ta/, /ml/, /bn/, /or/)

"next Amavasya date", "Purnima dates 2026", "Pradosh vrat dates 2026",
"Sankashti Chaturthi dates and moonrise" are searches (and assistant questions)
whose answer is a date and a time. Each page opens with that answer, computed at
render time ("The next Amavasya is on 10 October 2026, Saturday (...)", or "all
dates for 2026" once the year is over), then lists every date of the year with
its weekday, Hindu month, tithi start and end and - where the engine has one -
the observance's own time: Pradosh puja window, Sankashti moonrise, Masik
Shivratri Nishita kaal.

Every date and time is `astro.festivals`' output for New Delhi (its rules were
checked against Drik Panchang, see tests/test_festivals.py); nothing is typed
here. A field the engine does not produce for an observance (Purnima, Amavasya
and Kalashtami have no timing of their own) is left out. The words are in
recurring_text.TEXT, in all eight languages, with a few generic strings reused
from vrat_text.

The shell is seo_pages._render, like /ekadashi-2026: same style, AdSense, visit
beacon, hreflang set, breadcrumbs, footer. Each page is its own canonical;
its copy in another language is a real translation, indexable, and listed in
hreflang (a language missing from TRANSLATED would render English, noindex).
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from . import i18n, lang_data, seo_cities, seo_pages, vrat_pages, vrat_text
from .astro import festivals
from .recurring_text import TEXT
from .seo_pages import EN, HI, SITE_URL, _e, _long_date, _short_date

router = APIRouter()

CITY = seo_cities.DEFAULT                 # New Delhi, like every page of this family
YEARS = (2026, 2027)
TOP_CITIES = 12                           # Panchang links on each page


@dataclass(frozen=True)
class Spec:
    slug: str                             # the URL stem: /<slug>-<year>
    key: str                              # the engine's observance key
    timing: str | None                    # the engine timing that is this observance's own time


SPECS = (
    Spec("purnima", "purnima", None),
    Spec("amavasya", "amavasya", None),
    Spec("pradosh-vrat", "pradosh", "pradosh"),
    Spec("sankashti-chaturthi", "sankashti", "moonrise"),
    Spec("masik-shivratri", "masik_shivratri", "nishita"),
    Spec("kalashtami", "kalashtami", None),
)
BY_SLUG = {s.slug: s for s in SPECS}

# The engine calls it "Purnima Vrat"; the search, and the page, say "Purnima".
_NAME_EN = {"purnima": "Purnima"}

# DIVASTRO-121/123: the languages these pages are really written in. One not
# listed renders English text with noindex, no hreflang and no sitemap entry.
# DIVASTRO-143: the older languages keep this "has its text" rule; a new language is
# translated exactly when app/lang_data/<code>.py READY includes "recurring".
TRANSLATED = i18n.BASE_TRANSLATED | {c for c in lang_data.LEGACY_CODES
                                     if i18n.has("about.purnima", c, TEXT)} | lang_data.ready("recurring")
# localize_links() keys on the first hyphen-separated word of the root.
i18n.LOCALIZABLE_ROOTS.update({f"{s.slug.split('-')[0]}-" for s in SPECS})


def _tx(key: str, lang: str, **values) -> str:
    return i18n.fmt(key, lang, TEXT, **values)


def _has(key: str) -> bool:
    return key in TEXT["en"]


# --------------------------------------------------------------------------
# Paths, and what is public
# --------------------------------------------------------------------------

def path(slug: str, year: int, lang: str = EN) -> str:
    return i18n.prefix(lang) + f"/{slug}-{year}"


def page_paths() -> list[str]:
    """Every indexable page, every TRANSLATED language - for the sitemap."""
    return [path(s.slug, y, lang) for lang in i18n.ordered(TRANSLATED)
            for y in YEARS for s in SPECS]


_BARE = frozenset(path(s.slug, y) for s in SPECS for y in YEARS)


def is_public_path(p: str) -> bool:
    """For the visit beacon: an English, Hindi or regional path of this family."""
    return i18n.strip_prefix(p)[1] in _BARE


def daily_paths(day: dt.date) -> list[str]:
    """The pages whose direct answer changes with `day` (the current year's)."""
    if day.year not in YEARS:
        return []
    return [path(s.slug, day.year, lang) for lang in i18n.ordered(TRANSLATED) for s in SPECS]


def share_text(stem: str) -> str | None:
    """The WhatsApp share message for '<slug>-<year>' (share.seo_share_text)."""
    slug, _, year = stem.rpartition("-")
    spec = BY_SLUG.get(slug)
    if spec is None or not year.isdigit() or int(year) not in YEARS:
        return None
    first = rows(spec, YEARS[0])[0]
    return (f"{_NAME_EN.get(spec.key, first['name_en'])} {year} - all dates · "
            f"{first['name_hi']} {year} की सभी तिथियां:")


def hub_items(lang: str) -> tuple[str, list[tuple[str, str]]]:
    """(heading, [(link text, path)]) for the /sitemap page (site_hub)."""
    items = [(_e(f"{_label(s, lang)} {y}"), path(s.slug, y, lang))
             for y in YEARS for s in SPECS]
    return _e(_tx("hub.h2", lang)), items


# --------------------------------------------------------------------------
# Data: the engine's observances for New Delhi
# --------------------------------------------------------------------------

def _year_obs(year: int) -> tuple[dict, ...]:
    """The engine's whole year (the cache every sibling page shares)."""
    return festivals._year(year, round(CITY.latitude, 4), round(CITY.longitude, 4), CITY.timezone)


def rows(spec: Spec, year: int) -> list[dict]:
    """Every dated occurrence of the observance in `year`, in date order."""
    return [o for o in _year_obs(year) if o["key"] == spec.key]


def _date(o: dict) -> dt.date:
    return dt.date.fromisoformat(o["date"])


def _same_day_festivals(year: int, lang: str) -> dict[str, list[str]]:
    """date -> links to the major festival pages falling on it (Guru Purnima on a
    Purnima, Mauni Amavasya on an Amavasya)."""
    slugs = set(vrat_pages._festival_slugs(year))
    out: dict[str, list[str]] = {}
    for o in _year_obs(year):
        if o["major"] and o["slug"] in slugs:
            out.setdefault(o["date"], []).append(
                f'<a href="{_e(vrat_pages.festival_path(o["slug"], year, lang))}">'
                f"{_e(_obs_name(o, lang))}</a>")
    return out


# --------------------------------------------------------------------------
# Formatting
# --------------------------------------------------------------------------

def _obs_name(o: dict, lang: str) -> str:
    return o.get(f"name_{lang}") or i18n.names(lang).festival_name(o)


def _label(spec: Spec, lang: str) -> str:
    """The observance's name in `lang` (names_<code>.FESTIVALS, English 'Purnima')."""
    if lang == EN and spec.key in _NAME_EN:
        return _NAME_EN[spec.key]
    first = next(iter(rows(spec, YEARS[0])))
    return _obs_name(first, lang)


def _day_label(day: dt.date, lang: str, year: bool = False) -> str:
    text = _long_date(day, lang) if year else _short_date(day, lang)
    return i18n.fmt("day_label", lang, TEXT, date=text, weekday=i18n.weekday(day, lang))


def _clock(iso: str, ref: dt.date, lang: str) -> str:
    return seo_pages._time(iso, ref, lang)


def _tithi_text(o: dict, lang: str) -> str:
    t = o.get("tithi")
    if not t:
        return ""
    day, n = _date(o), i18n.names(lang)
    paksha = _tx("tithi.paksha", lang, paksha=n.PAKSHA.get(t["paksha"], t["paksha"]))
    return _tx("tithi.text", lang, paksha=paksha, name=n.TITHI.get(t["name"], t["name"]),
               start=_clock(t["start"], day, lang), end=_clock(t["end"], day, lang))


def _month_text(o: dict, lang: str) -> str:
    m = o.get("month")
    if not m:
        return "—"
    name = i18n.names(lang).MASA.get(m["name"], m["name"])
    return _tx("adhika", lang, month=name) if m.get("adhika") else name


def _key_timing(o: dict, spec: Spec) -> dict | None:
    if not spec.timing:
        return None
    return next((t for t in o["timings"] if t["key"] == spec.timing), None)


def _key_label(spec: Spec, lang: str, t: dict) -> str:
    return i18n.names(lang).FESTIVAL_TIMINGS.get(spec.timing) or t["label_en"]


def _key_value(t: dict, day: dt.date, lang: str) -> str:
    if t.get("at"):
        return _clock(t["at"], day, lang)
    return f"{_clock(t['start'], day, lang)} – {_clock(t['end'], day, lang)}"


def _details(o: dict, spec: Spec, lang: str) -> str:
    """'Krishna Amavasya: 12:30 AM to ...' plus the observance's own time, if any."""
    text = _tithi_text(o, lang)
    t = _key_timing(o, spec)
    if t:
        text += "; " + _tx("timing", lang, label=_key_label(spec, lang, t), prefix="",
                           value=_key_value(t, _date(o), lang))
    return text


def _rule(o: dict, lang: str) -> str:
    """How the date is fixed: the engine's own rule text (English, Hindi), else
    composed from vrat_text.RULES with the language's tithi/paksha names (the same
    construction the festival pages use)."""
    if o.get(f"rule_{lang}"):
        return o[f"rule_{lang}"]
    rules = vrat_text.RULES.get(lang, {})
    t, tail = o.get("tithi"), rules.get(f"rule.{o.get('rule')}")
    if not (t and tail):
        return o["rule_en"]
    n = i18n.names(lang)
    return rules["tithi"].format(paksha=n.PAKSHA.get(t["paksha"], t["paksha"]),
                                 tithi=n.TITHI.get(t["name"], t["name"])) + tail


def _item_list(name: str, items: list[str]) -> dict:
    return {"@type": "ItemList", "name": name, "numberOfItems": len(items),
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n}
                                for i, n in enumerate(items)]}


# --------------------------------------------------------------------------
# The page
# --------------------------------------------------------------------------

def _today() -> dt.date:
    return seo_pages._today()


def _focus(items: list[dict], year: int, today: dt.date) -> tuple[str, dict]:
    """Which date the answer is about: ('next', the first date >= today) in the
    current year, ('first', the year's first date) for a coming year, and
    ('past', the last date) once the year is over."""
    if year > today.year:
        return "first", items[0]
    later = [o for o in items if _date(o) >= today] if year == today.year else []
    return ("next", later[0]) if later else ("past", items[-1])


def _table(spec: Spec, year: int, items: list[dict], lang: str) -> str:
    same_day = _same_day_festivals(year, lang)
    key_th = ""
    first_t = next((t for o in items if (t := _key_timing(o, spec))), None)
    if first_t:
        key_th = f"<th>{_e(_key_label(spec, lang, first_t))}</th>"
    head = (f"<tr><th>{_e(_tx('th.date', lang))}</th><th>{_e(_tx('th.month', lang))}</th>"
            f"<th>{_e(_tx('th.tithi', lang))}</th>{key_th}</tr>")
    body = []
    for o in items:
        day = _date(o)
        cell = _e(_day_label(day, lang))
        if _has(f"variant.{spec.key}.{day.weekday()}"):
            cell += f"<small>{_e(_tx(f'variant.{spec.key}.{day.weekday()}', lang))}</small>"
        if o["date"] in same_day:
            cell += f"<small>{_e(_tx('also', lang))}{', '.join(same_day[o['date']])}</small>"
        key_td = ""
        if key_th:
            t = _key_timing(o, spec)
            key_td = f"<td>{_e(_key_value(t, day, lang)) if t else '—'}</td>"
        body.append(f'<tr data-date="{o["date"]}"><td>{cell}</td>'
                    f"<td>{_e(_month_text(o, lang))}</td>"
                    f"<td>{_e(_tithi_text(o, lang))}</td>{key_td}</tr>")
    return f'<div class="scroll"><table>{head}{"".join(body)}</table></div>'


def _links(spec: Spec, year: int, lang: str) -> str:
    items = []
    for s in SPECS:
        if s != spec:
            items.append((path(s.slug, year, lang), f"{_label(s, lang)} {year}"))
    for y in YEARS:
        if y != year:
            items.append((path(spec.slug, y, lang), f"{_label(spec, lang)} {y}"))
    items.append((vrat_pages.ekadashi_path(year, lang), _tx("more.ekadashi", lang, year=year)))
    items.append((vrat_pages.year_path(year, lang), _tx("more.year", lang, year=year)))
    items.append((vrat_pages.hub_path(lang), _tx("more.today", lang)))
    lis = "".join(f'<li><a href="{_e(h)}">{_e(t)}</a></li>' for h, t in items)
    return f'<h2>{_e(_tx("related.h2", lang))}</h2><ul class="links">{lis}</ul>'


def _city_links(lang: str) -> str:
    lis = "".join(
        f'<li><a href="{_e(seo_pages._path("panchang", c, lang))}">'
        f'{_e(_tx("tools.panchang", lang, city=seo_cities.city_name(c, lang)))}</a></li>'
        for c in seo_cities.CITIES[:TOP_CITIES])
    return f'<h2>{_e(_tx("city.h2", lang))}</h2><ul class="links">{lis}</ul>'


def _place(lang: str) -> str:
    name = (seo_cities.city_name(CITY, lang) if seo_cities.has_name(CITY, lang) else CITY.label)
    return f"{name} · IST"


def _answer(spec: Spec, year: int, items: list[dict], which: str, o: dict, lang: str,
            name: str) -> str:
    when = _e(_day_label(_date(o), lang, year=True))
    v = {"name": _e(name), "year": year, "count": len(items), "when": when,
         "details": _e(_details(o, spec, lang))}
    text = _tx(f"ans.{which}", lang, **v)
    if which == "past" and year + 1 in YEARS:
        link = (f'<a href="{_e(path(spec.slug, year + 1, lang))}">'
                f"{_e(name)} {year + 1}</a>")
        text += _tx("ans.more", lang, year=year + 1, link=link)
    return text


def _faq(spec: Spec, year: int, items: list[dict], which: str, o: dict, lang: str,
         name: str) -> tuple[tuple[str, str], ...]:
    day = _date(o)
    v = {"name": name, "year": year, "count": len(items), "short": _short_date(day, lang),
         "when": _day_label(day, lang, year=True), "details": _details(o, spec, lang)}
    dates = "; ".join(_day_label(_date(x), lang) for x in items)
    out = [(_tx("faq.all_q", lang, **v), _tx("faq.all_a", lang, **v, dates=dates))]
    if which in ("next", "first"):
        out.append((_tx(f"faq.{which}_q", lang, **v), _tx("faq.on_a", lang, **v)))
    t = _key_timing(o, spec)
    q = (_tx("faq.key_q", lang, **v, label=_key_label(spec, lang, t)) if t
         else _tx("faq.tithi_q", lang, **v))
    out.append((q, _tx("faq.timings_a", lang, timings=v["details"])))
    out.append((_tx("faq.why_q", lang, **v), _tx("faq.why_a", lang, **v, rule=_rule(items[0], lang))))
    return tuple(out)


def render(slug: str, year: int, lang: str, today: dt.date | None = None) -> HTMLResponse:
    """/<slug>-<year> in `lang`. `today` is for tests; the routes pass None."""
    spec = BY_SLUG[slug]
    today = today or _today()
    items = rows(spec, year)
    name = _label(spec, lang)
    which, ref = _focus(items, year, today)
    p = path(slug, year, lang)
    v = {"name": name, "year": year, "count": len(items), "what": _tx(f"what.{spec.key}", lang)}

    key_t = next((t for o in items if (t := _key_timing(o, spec))), None)
    next_text = (_tx("desc.next", lang, date=_day_label(_date(ref), lang, year=True))
                 if which in ("next", "first") else "")
    description = _tx("desc", lang, **v, about=_tx(f"desc.about.{spec.key}", lang),
                      keytime=_tx("desc.key", lang, label=_key_label(spec, lang, key_t)) if key_t else "",
                      next=next_text).strip()
    title, h1 = _tx("title", lang, **v), _tx("h1", lang, **v)

    krishna = any(o["tithi"]["paksha"] == "Krishna" for o in items)
    faq_html, faq_ld = seo_pages._faq(_faq(spec, year, items, which, ref, lang, name))
    sub = ""
    if lang == EN:
        sub = f'<p class="hi" lang="hi">{_e(items[0]["name_hi"])} {year}</p>'
    elif lang == HI:
        sub = f'<p class="hi" lang="en">{_e(_NAME_EN.get(spec.key) or items[0]["name_en"])} {year}</p>'
    body = (f"<h1>{_e(h1)}</h1>{sub}"
            f'<p class="date">{_e(_place(lang))}</p>'
            f'<div class="box answer"><p>{_answer(spec, year, items, which, ref, lang, name)}</p></div>'
            f"<h2>{_e(_tx('table.h2', lang, **v))}</h2>"
            + (_tx("months.note", lang) if krishna else "")
            + _table(spec, year, items, lang)
            + _tx("city_note", lang, city=_e(seo_cities.city_name(CITY, lang)))
            + f"<h2>{_e(_tx('about.h2', lang, name=name))}</h2>{_tx(f'about.{spec.key}', lang)}"
            + f"<h2>{_e(_tx('fest.rule_h2', lang))}</h2><p>{_e(_rule(items[0], lang))}.</p>"
            + f"<p>{_e(_tx(f'note.{spec.key}', lang))}</p>"
            + f"<h2>{_e(_tx('fest.faq_h2', lang))}</h2>{faq_html}"
            + f'<a class="cta" href="{_e(seo_pages._app_link("panchang", lang))}">'
              f'{_e(_tx("cta", lang))}</a>'
            + _links(spec, year, lang) + _city_links(lang))
    crumbs = [(_tx("crumb", lang), vrat_pages.hub_path(lang)),
              (_tx("crumb.page", lang, name=name, year=year), p)]
    ld = _item_list(h1, [f"{name} - {_long_date(_date(o), lang)}" for o in items])
    return seo_pages._render(title=title, description=description, path=p, alt="twin",
                             crumbs=crumbs, body=body, lang=lang, extra_ld=(ld, faq_ld),
                             translated=TRANSLATED)


def _not_found(lang: str) -> HTMLResponse:
    links = "".join(f'<li><a href="{_e(p)}">{_e(p)}</a></li>'
                    for p in (path(s.slug, y, lang) for y in YEARS for s in SPECS))
    return seo_pages._render(
        title="Not found", description="", path=path(SPECS[0].slug, YEARS[0], lang), crumbs=[],
        body=f"<h1>{_e(_tx('nf.h1', lang))}</h1><ul class=\"links\">{links}</ul>",
        lang=lang, status=404, cache=False, translated=TRANSLATED)


def _dispatch(spec: Spec, year: str, lang: str) -> HTMLResponse:
    if not year.isdigit() or int(year) not in YEARS:
        return _not_found(lang)
    return render(spec.slug, int(year), lang)


# --------------------------------------------------------------------------
# Routes: one trio (en, hi, any other language) per observance
# --------------------------------------------------------------------------

def _register(spec: Spec) -> None:
    def en(year: str) -> HTMLResponse:
        return _dispatch(spec, year, EN)

    def hi(year: str) -> HTMLResponse:
        return _dispatch(spec, year, HI)

    def other(lang: str, year: str) -> HTMLResponse:
        return _dispatch(spec, year, lang)

    for url, fn, tag in ((f"/{spec.slug}-{{year}}", en, "en"), (f"/hi/{spec.slug}-{{year}}", hi, "hi"),
                         (f"/{{lang:xlang}}/{spec.slug}-{{year}}", other, "lang")):
        router.add_api_route(url, fn, methods=["GET"], response_class=HTMLResponse,
                             name=f"recurring_{spec.key}_{tag}")


for _spec in SPECS:
    _register(_spec)
