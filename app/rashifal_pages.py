"""Daily Rashifal pages — /rashifal, /rashifal/<sign>, /hi/rashifal, /hi/rashifal/<sign>.

Why (DIVASTRO-105): "aaj ka rashifal" / "today's horoscope <sign>" are among
the highest-volume daily astrology searches in India. These pages answer them
in the raw HTML, in English and Hindi, the same way seo_pages.py does for the
panchang (and reusing its style, footer and cache rule).

**Computed, not invented.** Every statement on a page is keyed to a real
sidereal (Lahiri) position for today in IST, from the same Swiss Ephemeris
route the panchang engine and the kundali use (`panchang._sidereal`, mean
node, as in `panchang._chart_view`):

  * the house the transiting Moon occupies counted from each rashi (Chandra
    gochar), with the IST time if the Moon changes sign during the day;
  * the houses Saturn, Jupiter and Rahu/Ketu occupy from that rashi — the slow
    transits that set the longer backdrop — and Sade Sati / Dhaiya, which is
    Saturn in the 12th/1st/2nd (4th/8th) from the Moon sign, the same
    sign-ingress rule as `panchang.sade_sati_for_moon_sign`;
  * today's tithi and nakshatra from `daily_panchang` (New Delhi sunrise, the
    same numbers /panchang prints).

Those facts are turned into text through a fixed phrase bank (below), so the
text for a given house is the same for every sign and every day it applies —
nothing is generated, and nothing ("lucky colour", "lucky number") is shown
that does not follow from a documented rule.

**The classical scheme** (gochara phala, results of transits counted from the
janma rashi, i.e. the natal Moon sign):

  * Moon — favourable in the 1st, 3rd, 6th, 7th, 10th and 11th from the
    janma rashi; unfavourable elsewhere. Varahamihira, Brihat Samhita ch. 104
    (Grahagocharadhyaya) and Mantreswara, Phaladeepika ch. 26 (Gocharaphala)
    agree on this set. We grade the unfavourable six in two steps: 4th, 8th
    and 12th (the dusthana/kendra-of-unease positions; the 8th is the widely
    observed *Chandrashtama*) as "take it easy", and 2nd, 5th, 9th as "mixed",
    which is how most published Indian rashifals soften them.
  * Saturn — favourable in the 3rd, 6th and 11th; 12th/1st/2nd is Sade Sati;
    4th and 8th are the two Dhaiyas (Kantaka / Ashtama Shani).
  * Jupiter — favourable in the 2nd, 5th, 7th, 9th and 11th.
  * Rahu and Ketu — favourable in the 3rd, 6th and 11th (Phaladeepika 26
    treats the nodes like Saturn).

Vedha (obstruction of a transit by another planet at its vedha point) and
Ashtakavarga bindus are NOT applied — both refine a transit for an individual
chart, which is exactly what the page says a personal reading adds.

The phrase gist follows those texts (e.g. Moon in the 6th: victory over
opponents and well-being; in the 12th: expense) rewritten in warm, practical
language, never fear-based, with no medical or financial promises.
"""

from __future__ import annotations

import datetime as dt
import functools
import json
from dataclasses import dataclass

from fastapi import APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse

from . import i18n, lang_data, seo_cities
from .astro import panchang as panchang_engine
from .chart_service import SIGNS
from .seo_pages import (
    ADSENSE_CLIENT, BRAND, IST, SITE_URL, _STYLE, _cache_headers, _e,
    _footer, _panchang, _strip, _today, page_language_bits,
)
from .seo_text import TEXT as SEO_TEXT
# DIVASTRO-123: every word of these pages, and the phrase bank, is data in rashifal_text.
from .rashifal_text import (  # noqa: F401  (re-exported: tests read the banks from here)
    CLOCK_LANG, EASY, GOOD, JUPITER_HOUSE, KETU_LINE, MIXED, MOON_HOUSE, MORE_LINKS,
    RAHU_HOUSE, SATURN_HOUSE, TEXT, TONE_LABEL,
)

from .share import seo_share  # noqa: E402  (DIVASTRO-107 share button)

router = APIRouter()


# --------------------------------------------------------------------------
# Signs
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Rashi:
    index: int          # 0 = Aries, as chart_service.SIGNS
    slug: str           # the public URL segment — never rename one
    name: str           # Mesh
    name_hi: str        # मेष
    english: str        # Aries

    @property
    def english_slug(self) -> str:
        return self.english.lower()


RASHIS: tuple[Rashi, ...] = tuple(
    Rashi(i, slug, name, hi, SIGNS[i]) for i, (slug, name, hi) in enumerate((
        ("mesh", "Mesh", "मेष"), ("vrishabh", "Vrishabh", "वृषभ"),
        ("mithun", "Mithun", "मिथुन"), ("kark", "Kark", "कर्क"),
        ("simha", "Simha", "सिंह"), ("kanya", "Kanya", "कन्या"),
        ("tula", "Tula", "तुला"), ("vrishchik", "Vrishchik", "वृश्चिक"),
        ("dhanu", "Dhanu", "धनु"), ("makar", "Makar", "मकर"),
        ("kumbh", "Kumbh", "कुंभ"), ("meen", "Meen", "मीन"),
    )))
BY_SLUG = {r.slug: r for r in RASHIS}
BY_ENGLISH = {r.english_slug: r for r in RASHIS}

LANGS = ("en", "hi")
# DIVASTRO-121: the languages these pages are really written in (see app/i18n.py).
# Every registry language gets /<code>/rashifal; one not listed here shows the
# English text with noindex + "translation coming soon", and stays out of the
# sitemap and hreflang. Add a code once its rashifal strings are written.
# DIVASTRO-143: + every new language whose app/lang_data/<code>.py READY includes "rashifal".
TRANSLATED = lang_data.translated("rashifal", i18n.BASE_TRANSLATED, lang_data.LEGACY_CODES)  # DIVASTRO-123/143
i18n.LOCALIZABLE_ROOTS.add("rashifal")



def _ordinal(n: int) -> str:
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def house_from(rashi_index: int, sign_index: int) -> int:
    """The house `sign_index` occupies counted from `rashi_index` (1..12),
    inclusive counting as in every gochar table: the rashi itself is the 1st."""
    return (sign_index - rashi_index) % 12 + 1


def path(rashi: Rashi | None, lang: str) -> str:
    base = i18n.prefix(lang) + "/rashifal"
    return f"{base}/{rashi.slug}" if rashi else base


def sitemap_paths() -> list[str]:
    """All canonical URLs (index + 12 signs) in every TRANSLATED language."""
    return [path(r, lang) for lang in i18n.ordered(TRANSLATED) for r in (None, *RASHIS)]


PUBLIC_PATHS = frozenset(sitemap_paths())


def is_public_path(p: str) -> bool:
    """For analytics.is_public_page: only the canonical URLs count."""
    return p in PUBLIC_PATHS


# --------------------------------------------------------------------------
# The phrase bank — see the module docstring for the classical scheme.
# --------------------------------------------------------------------------

MOON_FAVOURABLE = frozenset({1, 3, 6, 7, 10, 11})
MOON_CHALLENGING = frozenset({4, 8, 12})
SATURN_FAVOURABLE = frozenset({3, 6, 11})
JUPITER_FAVOURABLE = frozenset({2, 5, 7, 9, 11})
NODE_FAVOURABLE = frozenset({3, 6, 11})
SADE_SATI = {12: 1, 1: 2, 2: 3}          # house of Saturn from the Moon sign -> phase
DHAIYA = frozenset({4, 8})
# TONE_LABEL and the phrase bank (MOON_HOUSE, SATURN_HOUSE, JUPITER_HOUSE,
# RAHU_HOUSE, KETU_LINE) live in rashifal_text.py, one entry per language.


def moon_tone(house: int) -> str:
    return GOOD if house in MOON_FAVOURABLE else EASY if house in MOON_CHALLENGING else MIXED


# --------------------------------------------------------------------------
# The sky for one IST day
# --------------------------------------------------------------------------

@functools.lru_cache(maxsize=16)
def sky(day: dt.date) -> dict:
    """Sidereal (Lahiri) positions for the IST civil day `day`.

    The Moon is checked at 00:00 and just before 24:00 IST; it spends ~2¼ days
    in a sign, so it changes sign at most once a day, and the instant is found
    by bisection to the second. Saturn, Jupiter and the (mean) nodes are read at
    12:00 IST — they move a few arc-minutes a day, and the very rare day one of
    them changes sign is described by its noon position.
    """
    pe = panchang_engine
    pe._ephemeris()
    swe = pe.swe
    aya = pe.DEFAULT_AYANAMSA

    def lon(jd: float, body: int) -> float:
        return pe._sidereal(jd, body, aya)

    start = dt.datetime.combine(day, dt.time(), IST)
    jd0 = pe._to_jd(start)
    jd1 = pe._to_jd(start + dt.timedelta(days=1)) - 1e-7
    first = int(lon(jd0, swe.MOON) // 30)
    last = int(lon(jd1, swe.MOON) // 30)
    segments = [{"sign": first, "from": None, "until": None}]
    if last != first:
        lo, hi = jd0, jd1
        while hi - lo > pe._TOLERANCE_DAYS:
            mid = (lo + hi) / 2
            if int(lon(mid, swe.MOON) // 30) == first:
                lo = mid
            else:
                hi = mid
        change = pe._from_jd(hi, IST)
        segments[0]["until"] = change
        segments.append({"sign": last, "from": change, "until": None})

    noon = pe._to_jd(start + dt.timedelta(hours=12))
    rahu = lon(noon, swe.MEAN_NODE)

    def slow(body: int) -> dict:
        speed = swe.calc_ut(noon, body, swe.FLG_SWIEPH | swe.FLG_SPEED)[0][3]
        return {"sign": int(lon(noon, body) // 30), "retrograde": speed < 0}

    p = _panchang(seo_cities.DEFAULT.slug, day)
    return {
        "day": day,
        "moon": segments,
        "saturn": slow(swe.SATURN),
        "jupiter": slow(swe.JUPITER),
        "rahu": {"sign": int(rahu // 30)},
        "ketu": {"sign": int(((rahu + 180.0) % 360.0) // 30)},
        "panchang": p,
    }


def main_moon(s: dict) -> dict:
    """The Moon segment that covers more of the day (for titles and summaries)."""
    segs = s["moon"]
    if len(segs) == 1:
        return segs[0]
    change = segs[0]["until"]
    return segs[0] if change.hour * 60 + change.minute >= 720 else segs[1]


def reading(rashi: Rashi, day: dt.date) -> dict:
    """Every computed fact the page shows for one rashi, before rendering."""
    s = sky(day)
    moon = [{**seg, "house": house_from(rashi.index, seg["sign"])} for seg in s["moon"]]
    main = house_from(rashi.index, main_moon(s)["sign"])
    sat = house_from(rashi.index, s["saturn"]["sign"])
    return {
        "moon": moon,
        "main_house": main,
        "tone": moon_tone(main),
        "saturn": sat,
        "jupiter": house_from(rashi.index, s["jupiter"]["sign"]),
        "rahu": house_from(rashi.index, s["rahu"]["sign"]),
        "ketu": house_from(rashi.index, s["ketu"]["sign"]),
        "sade_sati_phase": SADE_SATI.get(sat),
        "dhaiya": sat in DHAIYA,
    }


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------

_EXTRA_STYLE = """
  .seo .tone { display: inline-block; padding: 3px 10px; border-radius: 999px; font-size: 13px;
               border: 1px solid var(--line); margin-left: 6px; }
  .seo .tone.good { color: var(--green); border-color: var(--green); }
  .seo .tone.easy { color: var(--rose); border-color: var(--rose); }
  .seo .tone.mixed { color: var(--gold); border-color: var(--gold); }
  .seo .note { font-size: 13.5px; color: var(--ink-faint); }
"""

_SHELL = """<!DOCTYPE html>
<html lang="{html_lang}"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{title}</title>
<meta name="description" content="{description}"/>
<link rel="canonical" href="{canonical}"/>
{alternates}{head_extras}<meta property="og:type" content="article"/>
<meta property="og:site_name" content="{brand}"/>
<meta property="og:title" content="{title}"/>
<meta property="og:description" content="{description}"/>
<meta property="og:url" content="{canonical}"/>
<meta property="og:image" content="{site}/static/og-card.jpg"/>
<meta property="og:image:width" content="1200"/>
<meta property="og:image:height" content="630"/>
<meta property="og:locale" content="{og_locale}"/>
<meta name="twitter:card" content="summary_large_image"/>
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
  {body}{strip}
</main>
{footer}
</body></html>"""

def _tx(key: str, lang: str, **values) -> str:
    """This module's text for `key` in `lang` (rashifal_text.TEXT), formatted."""
    return i18n.fmt(key, lang, TEXT, **values)


def _date_text(day: dt.date, lang: str, short: bool = False) -> str:
    """'4 October 2026' / '4 Oct 2026' (English short form) / '4 अक्टूबर 2026'."""
    return i18n.format_date(day, lang, short=short) + (f" {day.year}" if short else "")


def _weekday(day: dt.date, lang: str) -> str:
    return i18n.weekday(day, lang)


def _local(r: Rashi, lang: str) -> str:
    """The sign in `lang`: मेष, ಮೇಷ — 'Aries' in English (names_<code>.RASHI)."""
    return i18n.names(lang).RASHI.get(r.english, r.english)


def _rashi_vars(r: Rashi, lang: str) -> dict:
    return {"name": r.name, "english": r.english, "name_hi": r.name_hi, "local": _local(r, lang)}


def _house_word(n: int, lang: str) -> str:
    """'4th' / 'चौथे': a language's own "house.<n>" word, else the English ordinal."""
    if i18n.has(f"house.{n}", lang, TEXT):
        return TEXT[lang][f"house.{n}"]
    return _ordinal(n)


def _planet(planet: str, lang: str) -> str:
    if i18n.has(f"planet.{planet}", lang, TEXT):
        return TEXT[lang][f"planet.{planet}"]
    return i18n.names(lang).GRAHA.get(planet, planet)


def _shell(*, lang: str, rashi: Rashi | None, title: str, description: str,
           crumbs: list[tuple[str, str]], body: str, day: dt.date,
           status: int = 200, cache: bool = True) -> HTMLResponse:
    canonical = SITE_URL + path(rashi, lang)
    bits = page_language_bits(lang=lang, path=path(rashi, lang), has_twin=status == 200,
                              translated=TRANSLATED, region=True)
    home = (TEXT[lang]["home"] if i18n.has("home", lang, TEXT) else i18n.chrome("home", lang))
    trail = [(home, "/")] + crumbs
    crumb_html = " › ".join(
        f'<a href="{_e(href)}">{_e(name)}</a>' if i < len(trail) - 1 else _e(name)
        for i, (name, href) in enumerate(trail))
    in_lang = bits["in_language"]
    graph = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "WebPage", "name": title, "description": description, "url": canonical,
             "inLanguage": in_lang, "datePublished": day.isoformat(),
             "dateModified": day.isoformat(),
             "isPartOf": {"@type": "WebSite", "name": BRAND, "url": SITE_URL + "/"}},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": name, "item": SITE_URL + href}
                for i, (name, href) in enumerate(trail)]},
        ],
    }
    jsonld = json.dumps(graph, ensure_ascii=False).replace("</", "<\\/")
    page = _SHELL.format(
        html_lang=in_lang, title=_e(title), description=_e(description),
        canonical=_e(canonical), alternates=bits["alternates"], head_extras=bits["head"],
        og_locale=bits["og_locale"], home=_e(bits["home"]), picker=bits["picker"],
        notice=bits["notice"],
        brand=_e(BRAND), site=_e(SITE_URL), adsense=ADSENSE_CLIENT,
        style=_STYLE + _EXTRA_STYLE, jsonld=jsonld, crumbs=i18n.localize_links(crumb_html, lang),
        body=(seo_share(path(rashi, lang)) if status == 200 else "")
        + i18n.localize_links(body, lang),
        strip=_strip(lang=lang, path=path(rashi, lang), title=title) if status == 200 else "",
        footer=_footer(lang))
    headers = _cache_headers() if cache else {"Cache-Control": "no-store"}
    return HTMLResponse(page, status_code=status, headers=headers)


def _sign_label(index: int, lang: str) -> str:
    return _tx("sign_label", lang, **_rashi_vars(RASHIS[index], lang))


def _sign_links(current: Rashi | None, lang: str) -> str:
    items = "".join(
        f'<li><a href="{path(r, lang)}"' + (' aria-current="page"' if r == current else "")
        + f'>{_e(_tx("sign_link", lang, **_rashi_vars(r, lang)))}</a></li>'
        for r in RASHIS)
    return f'<h2>{_tx("signs.head", lang)}</h2><ul class="links">{items}</ul>'


def _more_links(rashi: Rashi | None, lang: str) -> str:
    links = []
    for href, text in i18n.pick(MORE_LINKS, lang):
        if href.startswith("{twin:"):
            href = path(rashi, href[6:-1])
        links.append((href, text))
    items = "".join(f'<li><a href="{_e(h)}">{_e(t)}</a></li>' for h, t in links)
    return f'<h2>{_tx("more.head", lang)}</h2><ul class="links">{items}</ul>'


def _cta(lang: str) -> str:
    """Into the birth form (tools.js `?open=kundali` clicks the home CTA). A
    question needs a chart first, so the kundali is the one door for both."""
    return f'<a class="cta" href="/?open=kundali">{_e(_tx("cta", lang))}</a>'


def _personal_line(lang: str) -> str:
    return _tx("personal", lang)


def _time(moment: dt.datetime, day: dt.date, lang: str = "en") -> str:
    """The clock time, with the date when it falls on another day. Hindi pages
    print it as English does (rashifal_text.CLOCK_LANG)."""
    lang = CLOCK_LANG.get(lang, lang)
    text = i18n.format_time(moment, lang)
    if moment.date() == day:
        return text
    return f"{text} ({i18n.format_date(moment.date(), lang, short=True)})"


def _moon_section(rashi: Rashi, r: dict, day: dt.date, lang: str) -> str:
    moon = r["moon"]
    parts = []
    for seg in moon:
        h = seg["house"]
        sign = _e(_sign_label(seg["sign"], lang))
        house = _house_word(h, lang)
        if len(moon) == 1:
            lead = _tx("moon.allday", lang, sign=sign, house=house)
        elif seg["until"]:
            lead = _tx("moon.until", lang, sign=sign, house=house, time=_time(seg["until"], day, lang))
        else:
            lead = _tx("moon.from", lang, sign=sign, house=house, time=_time(seg["from"], day, lang))
        tone = moon_tone(h)
        parts.append(f'<p>{lead} <span class="tone {tone}">{_e(i18n.pick(TONE_LABEL, lang)[tone])}</span></p>'
                     f"<p>{_e(i18n.pick(MOON_HOUSE[h], lang))}</p>")
    if len(moon) > 1:
        parts.insert(0, _tx("moon.two", lang))
    return f"<h2>{_tx('moon.head', lang)}</h2>" + "".join(parts)


def _backdrop_section(r: dict, s: dict, lang: str) -> str:
    rows = []

    def row(planet: str, sign_index: int, house: int, text: str, retro: bool = False) -> None:
        where = _tx("back.where", lang, sign=_e(_sign_label(sign_index, lang)),
                    rx=_tx("rx", lang) if retro else "", house=_house_word(house, lang))
        rows.append(f'<tr><th scope="row">{_e(_planet(planet, lang))}<small>{where}</small></th>'
                    f"<td>{_e(text)}</td></tr>")

    row("Saturn", s["saturn"]["sign"], r["saturn"], i18n.pick(SATURN_HOUSE[r["saturn"]], lang),
        s["saturn"]["retrograde"])
    row("Jupiter", s["jupiter"]["sign"], r["jupiter"], i18n.pick(JUPITER_HOUSE[r["jupiter"]], lang),
        s["jupiter"]["retrograde"])
    row("Rahu", s["rahu"]["sign"], r["rahu"], i18n.pick(RAHU_HOUSE[r["rahu"]], lang))
    ketu = i18n.pick(KETU_LINE[r["ketu"] in NODE_FAVOURABLE], lang).format(n=_house_word(r["ketu"], lang))
    row("Ketu", s["ketu"]["sign"], r["ketu"], ketu)

    phase = r["sade_sati_phase"]
    if phase:
        status = _tx("sade.running", lang, phase=_tx(f"phase.{phase}", lang))
    elif r["dhaiya"]:
        status = _tx("sade.dhaiya", lang)
    else:
        status = _tx("sade.none", lang)
    return (f"<h2>{_tx('back.head', lang)}</h2>{_tx('back.intro', lang)}"
            f"<div class=\"scroll\"><table>{''.join(rows)}</table></div>"
            f'<div class="box"><p>{status}</p></div>')


def _panchang_line(s: dict, day: dt.date, lang: str) -> str:
    summ = s["panchang"]["summary"]
    paksha, tithi, nak = summ["paksha"] or "", summ["tithi"] or "", summ["nakshatra"] or ""
    n = i18n.names(lang)
    local_paksha = n.PAKSHA.get(paksha, paksha)
    paksha_full = (i18n.fmt("paksha.full", lang, SEO_TEXT, paksha=local_paksha) if paksha else "")
    return _tx("panchang", lang, paksha=_e(local_paksha), paksha_full=_e(paksha_full),
               tithi=_e(n.TITHI.get(tithi, tithi)), nakshatra=_e(n.NAKSHATRAS.get(nak, nak)))


def _method_note(lang: str) -> str:
    return _tx("method", lang)


@functools.lru_cache(maxsize=128)
def _sign_page(day: dt.date, slug: str, lang: str) -> tuple[str, str, str, str]:
    """(title, description, body, h1-crumb) for one sign — cached per (date, sign, lang)."""
    rashi = BY_SLUG[slug]
    s = sky(day)
    r = reading(rashi, day)
    main = r["main_house"]
    tone = i18n.pick(TONE_LABEL, lang)[r["tone"]]
    rv = _rashi_vars(rashi, lang)
    raw = {**rv, "date": _date_text(day, lang), "date_short": _date_text(day, lang, short=True),
           "weekday": _weekday(day, lang), "house": _house_word(main, lang), "tone": tone,
           "tone_lower": tone.lower(), "brand": BRAND}
    title = _tx("s.title", lang, **raw)
    description = _tx("s.desc", lang, **raw)
    h1 = _tx("s.h1", lang, **rv)
    sub = _tx("s.sub", lang, **rv)
    summary_box = (
        f'<div class="box"><p><strong>{_e(tone)}</strong> — '
        + _tx("s.summary", lang, house=_house_word(main, lang), name=_e(rashi.name))
        + "</p></div>")
    about = _tx("s.about_rashi", lang, **rv)
    body = f"""
<h1>{_e(h1)}</h1>
<p class="hi" lang="{_tx('sub_lang', lang)}">{_e(sub)}</p>
<p class="date">{_e(_weekday(day, lang))}, {_e(_date_text(day, lang))} · IST</p>
{summary_box}
{_moon_section(rashi, r, day, lang)}
{_backdrop_section(r, s, lang)}
{_panchang_line(s, day, lang)}
{_personal_line(lang)}
{_cta(lang)}
<p><a href="{i18n.prefix(lang)}/rashi/{rashi.slug}">{_e(about)}</a></p>
{_sign_links(rashi, lang)}
{_method_note(lang)}
{_more_links(rashi, lang)}"""
    return title, description, body, _tx("sign_crumb", lang, **rv)


@functools.lru_cache(maxsize=8)
def _index_page(day: dt.date, lang: str) -> tuple[str, str, str]:
    s = sky(day)
    rows = []
    for rashi in RASHIS:
        r = reading(rashi, day)
        h = r["main_house"]
        name = _tx("i.name", lang, **{k: _e(v) for k, v in _rashi_vars(rashi, lang).items()})
        where = _tx("house_short", lang, house=_house_word(h, lang))
        sade = _tx("i.sade", lang) if r["sade_sati_phase"] else ""
        rows.append(f'<tr><td><a href="{path(rashi, lang)}">{name}</a></td><td>{where}</td>'
                    f'<td class="{"good" if r["tone"] == GOOD else "bad" if r["tone"] == EASY else ""}">'
                    f'{_e(i18n.pick(TONE_LABEL, lang)[r["tone"]])}{sade}</td></tr>')
    segs = s["moon"]
    moon_now = _sign_label(segs[0]["sign"], lang)
    if len(segs) > 1:
        moon_text = _tx("i.moon_two", lang, now=_e(moon_now), time=_time(segs[0]["until"], day, lang),
                        next=_e(_sign_label(segs[1]["sign"], lang)))
    else:
        moon_text = _tx("i.moon_one", lang, now=_e(moon_now))
    sade_signs = [RASHIS[(s["saturn"]["sign"] + k) % 12] for k in (1, 0, -1)]
    sade_names = ", ".join(_tx("sade_name", lang, **_rashi_vars(x, lang)) for x in sade_signs)
    sat_sign = _sign_label(s["saturn"]["sign"], lang)
    raw = {"date": _date_text(day, lang), "date_short": _date_text(day, lang, short=True),
           "weekday": _weekday(day, lang), "brand": BRAND}
    title = _tx("i.title", lang, **raw)
    description = _tx("i.desc", lang, **raw)
    intro = _tx("i.intro", lang, moon_text=moon_text, sat_sign=_e(sat_sign),
                sade_names=_e(sade_names))
    body = f"""
<h1>{_e(_tx("i.h1", lang))}</h1>
<p class="hi" lang="{_tx('sub_lang', lang)}">{_e(_tx("i.sub", lang))}</p>
<p class="date">{_e(_weekday(day, lang))}, {_e(_date_text(day, lang))} · IST</p>
{intro}
<div class="scroll"><table>{_tx("i.head_row", lang)}{''.join(rows)}</table></div>
{_panchang_line(s, day, lang)}
{_personal_line(lang)}
{_cta(lang)}
{_sign_links(None, lang)}
{_method_note(lang)}
{_more_links(None, lang)}"""
    return title, description, body


def _crumb_root(lang: str) -> tuple[str, str]:
    return _tx("crumb_root", lang), path(None, lang)


def render_index(lang: str, day: dt.date | None = None) -> HTMLResponse:
    day = day or _today()
    title, description, body = _index_page(day, lang)
    return _shell(lang=lang, rashi=None, title=title, description=description,
                  crumbs=[_crumb_root(lang)], body=body, day=day)


def render_sign(slug: str, lang: str, day: dt.date | None = None) -> HTMLResponse:
    day = day or _today()
    rashi = BY_SLUG[slug]
    title, description, body, crumb = _sign_page(day, slug, lang)
    return _shell(lang=lang, rashi=rashi, title=title, description=description,
                  crumbs=[_crumb_root(lang), (crumb, path(rashi, lang))], body=body, day=day)


def _resolve(slug: str, lang: str) -> HTMLResponse | RedirectResponse:
    if slug in BY_SLUG:
        return render_sign(slug, lang)
    key = slug.lower()
    rashi = BY_SLUG.get(key) or BY_ENGLISH.get(key)
    if rashi:
        return RedirectResponse(path(rashi, lang), status_code=301)
    day = _today()
    body = _tx("nf.body", lang, slug=_e(slug)) + _sign_links(None, lang)
    return _shell(lang=lang, rashi=None, title=f"{_tx('nf.title', lang)} — {BRAND}",
                  description="Rashifal sign not found.", crumbs=[_crumb_root(lang)], body=body,
                  day=day, status=404, cache=False)


@router.get("/rashifal", response_class=HTMLResponse)
def rashifal_index() -> HTMLResponse:
    return render_index("en")


@router.get("/rashifal/{slug}", response_class=HTMLResponse)
def rashifal_sign(slug: str):
    return _resolve(slug, "en")


@router.get("/hi/rashifal", response_class=HTMLResponse)
def rashifal_index_hi() -> HTMLResponse:
    return render_index("hi")


@router.get("/hi/rashifal/{slug}", response_class=HTMLResponse)
def rashifal_sign_hi(slug: str):
    return _resolve(slug, "hi")


# DIVASTRO-121: /kn/rashifal, /te/rashifal, ... (i18n.EXTRA_CODES). One builder
# per page, text from rashifal_text (English per key until translated; sign,
# tithi and nakshatra names already in the language's script).
@router.get("/{lang:xlang}/rashifal", response_class=HTMLResponse)
def rashifal_index_lang(lang: str) -> HTMLResponse:
    return render_index(lang)


@router.get("/{lang:xlang}/rashifal/{slug}", response_class=HTMLResponse)
def rashifal_sign_lang(lang: str, slug: str):
    return _resolve(slug, lang)
