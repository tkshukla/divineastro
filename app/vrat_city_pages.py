"""City-specific festival timing pages (DIVASTRO-140).

    /tyohar/<festival>-<year>/<city>        English
    /hi/tyohar/<festival>-<year>/<city>     Hindi (any other language code: the
                                            English text, noindex, so the language
                                            picker's links resolve)

"Karwa Chauth moonrise time in Bangalore", "Diwali Lakshmi puja muhurat in
Mumbai", "Dhanteras puja time in Noida" are the questions people and AI
assistants really ask, and the main /tyohar/<festival>-<year> page answers them
for New Delhi only. Moonrise, sunset and every muhurat shift by minutes from
city to city (and a few observances can fall on another date), so each city
gets its own page, with that city's numbers.

Every time comes from `astro.festivals` for the city's coordinates - the same
engine, the same rules, the same validation as the main page; nothing is
invented here. Only the festivals whose engine timings are location-dependent
are listed in FESTIVALS (a fast with no timing of its own, like Ekadashi's
parana, is not). New Delhi is not in the family: its page IS the main festival
page, so /tyohar/<festival>-<year>/new-delhi redirects there instead of being a
second copy of it.

Each page is built to be its own page, not a template swap: its own title,
description and h1 (festival, year, city and the headline time), a direct
answer, the full fact table, the minute-by-minute difference from New Delhi
computed from the engine, FAQ and Event JSON-LD with the city's numbers, a table
of nearby and major cities' headline times, and links to the main page and the
city's other festivals. Self-canonical, hreflang en/hi only.
"""

from __future__ import annotations

import datetime as dt
import functools
import math

from fastapi import APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse

from . import i18n, seo_cities, seo_pages, vrat_pages as vp
from .astro import festivals
from .seo_cities import City
from .seo_pages import EN, HI, SITE_URL, _e

router = APIRouter()

# Years with city pages. The festival dates are validated for both 2026 and
# 2027 but only the festivals about to happen need the long tail of pages;
# add 2027 here when it is time (nothing else changes).
CITY_YEARS = (2026,)
LANGS = (EN, HI)                                       # indexable languages of this family

# The 25 most-searched cities (New Delhi is the main page, the other 24 get
# pages). Slugs are seo_cities slugs.
CITY_SLUGS = (
    "new-delhi", "noida", "gurugram", "mumbai", "bengaluru", "hyderabad", "chennai",
    "kolkata", "pune", "ahmedabad", "jaipur", "lucknow", "patna", "bhopal", "indore",
    "chandigarh", "nagpur", "surat", "kanpur", "varanasi", "ranchi", "kochi",
    "bhubaneswar", "thiruvananthapuram", "guwahati")
BASE = seo_cities.DEFAULT
CITIES: tuple[City, ...] = tuple(seo_cities.BY_SLUG[s] for s in CITY_SLUGS if s != BASE.slug)
_MAJOR = ("mumbai", "bengaluru", "kolkata", "chennai", "hyderabad", "new-delhi")

# slug -> the festival's display names, the topic of its page, the timing keys the
# page leads with and the questions asked about them. Timing keys are the engine's.
# q: (timing key, English question, Hindi question); {name} {year} {city}.
FESTIVALS: dict[str, dict] = {
    "karwa-chauth": dict(
        name=("Karwa Chauth", "करवा चौथ"),
        topic=("Moonrise Time & Puja Muhurat", "moonrise time and puja muhurat",
               "चंद्रोदय का समय और पूजा मुहूर्त"),
        lead=("moonrise", "चंद्रोदय", "moonrise"),
        q=(("moonrise", "What time is moonrise in {city} on {name} {year}?",
            "{city} में {name} {year} पर चांद कब निकलेगा?"),
           ("karwa_puja", "What is the {name} {year} puja muhurat in {city}?",
            "{city} में {name} {year} का पूजा मुहूर्त क्या है?"))),
    "sharad-purnima": dict(
        name=("Sharad Purnima", "शरद पूर्णिमा"),
        topic=("Moonrise Time", "moonrise time", "चंद्रोदय का समय"),
        lead=("moonrise", "चंद्रोदय", "moonrise"),
        q=(("moonrise", "What time is moonrise in {city} on {name} {year}?",
            "{city} में {name} {year} पर चंद्रोदय कब होगा?"),)),
    "ahoi-ashtami": dict(
        name=("Ahoi Ashtami", "अहोई अष्टमी"),
        topic=("Puja Muhurat & Moonrise", "puja muhurat and moonrise",
               "पूजा मुहूर्त और चंद्रोदय"),
        lead=("karwa_puja", "पूजा मुहूर्त", "puja muhurat"),
        q=(("karwa_puja", "What is the {name} {year} puja muhurat in {city}?",
            "{city} में {name} {year} का पूजा मुहूर्त क्या है?"),
           ("moonrise", "When does the moon rise in {city} on {name} {year}?",
            "{city} में {name} {year} पर चंद्रमा कब निकलेगा?"))),
    "dhanteras": dict(
        name=("Dhanteras", "धनतेरस"),
        topic=("Puja Muhurat", "puja muhurat", "पूजा मुहूर्त"),
        lead=("dhanteras_puja", "पूजा मुहूर्त", "puja muhurat"),
        q=(("dhanteras_puja", "What is the {name} {year} puja muhurat in {city}?",
            "{city} में {name} {year} का पूजा मुहूर्त क्या है?"),
           ("pradosh_kaal", "When is Pradosh kaal in {city} on {name} {year}?",
            "{city} में {name} {year} पर प्रदोष काल कब है?"))),
    "diwali": dict(
        name=("Diwali", "दिवाली"),
        topic=("Lakshmi Puja Muhurat", "Lakshmi puja muhurat", "लक्ष्मी पूजा मुहूर्त"),
        lead=("lakshmi_puja", "लक्ष्मी पूजा मुहूर्त", "Lakshmi puja muhurat"),
        q=(("lakshmi_puja", "What is the Lakshmi Puja muhurat in {city} on {name} {year}?",
            "{city} में {name} {year} पर लक्ष्मी पूजा का मुहूर्त क्या है?"),
           ("pradosh_kaal", "When is Pradosh kaal in {city} on {name} {year}?",
            "{city} में {name} {year} पर प्रदोष काल कब है?"))),
    "govardhan-puja": dict(
        name=("Govardhan Puja", "गोवर्धन पूजा"),
        topic=("Puja Muhurat", "puja muhurat", "पूजा मुहूर्त"),
        lead=("pratah", "प्रातःकाल मुहूर्त", "morning (Pratahkala) muhurat"),
        q=(("pratah", "What is the {name} {year} muhurat in {city}?",
            "{city} में {name} {year} का मुहूर्त क्या है?"),)),
    "bhai-dooj": dict(
        name=("Bhai Dooj", "भाई दूज"),
        topic=("Tika Muhurat", "tika muhurat", "तिलक का मुहूर्त"),
        lead=("aparahna", "अपराह्न पूजा का समय", "Aparahna (tika) time"),
        q=(("aparahna", "What is the {name} {year} tika time (Aparahna) in {city}?",
            "{city} में {name} {year} पर तिलक का समय (अपराह्न) क्या है?"),)),
    "chhath-puja": dict(
        name=("Chhath Puja", "छठ पूजा"),
        topic=("Sandhya & Usha Arghya Time", "sandhya and usha arghya time",
               "संध्या और उषा अर्घ्य का समय"),
        lead=("sandhya_arghya", "संध्या अर्घ्य (सूर्यास्त)", "Sandhya arghya (sunset)"),
        q=(("sandhya_arghya", "What time is Sandhya Arghya (sunset) in {city} on {name} {year}?",
            "{city} में {name} {year} पर संध्या अर्घ्य (सूर्यास्त) कब है?"),
           ("usha_arghya", "What time is Usha Arghya (sunrise) in {city} for {name} {year}?",
            "{city} में {name} {year} का उषा अर्घ्य (सूर्योदय) कब है?"))),
    "navratri": dict(
        name=("Sharad Navratri", "शारदीय नवरात्रि"),
        topic=("Ghatasthapana Muhurat", "ghatasthapana muhurat", "घटस्थापना मुहूर्त"),
        lead=("ghatasthapana", "घटस्थापना मुहूर्त", "ghatasthapana muhurat"),
        q=(("ghatasthapana", "What is the Ghatasthapana muhurat in {city} for {name} {year}?",
            "{city} में {name} {year} का घटस्थापना मुहूर्त क्या है?"),
           ("ghatasthapana_abhijit", "What is the Abhijit muhurat for Ghatasthapana in {city} in {year}?",
            "{city} में {year} में घटस्थापना का अभिजित मुहूर्त क्या है?"))),
    "dussehra": dict(
        name=("Dussehra", "दशहरा"),
        topic=("Vijay Muhurat", "Vijay muhurat", "विजय मुहूर्त"),
        lead=("vijay", "विजय मुहूर्त", "Vijay muhurat"),
        q=(("vijay", "What is the Vijay muhurat in {city} on {name} {year}?",
            "{city} में {name} {year} पर विजय मुहूर्त कब है?"),
           ("aparahna", "What is the Aparahna puja time in {city} on {name} {year}?",
            "{city} में {name} {year} पर अपराह्न पूजा का समय क्या है?"))),
}

TEXT = {
    "en": {
        "title": "{name} {year} {topic} in {city} - {lead_value}",
        "h1": "{name} {year} in {city}: {topic}",
        "desc": ("{name} {year} in {city} falls on {weekday}, {date}. {lead_sentence} "
                 "{extra}Times computed for {city}; {diff_short}."),
        "fact": "{name} {year} in {city} is on {weekday}, {date}.",
        "lead_s": "The {lead} in {city} is {value}.",
        "diff_short_date": "New Delhi observes it on {base_day}",
        "diff_short_day": "the timings fall on a different calendar day than in New Delhi",
        "answer2": " {label}: {value}.",
        "date_line": "{city}, {state} · IST",
        "table_h2": "{name} {year} timings for {city}",
        "diff_h2": "How {city} differs from New Delhi",
        "diff_short": "{n} minutes {dir} than New Delhi",
        "diff_short0": "the same minute as New Delhi",
        "diff_lead": "The {lead} in {city} is {rel} the New Delhi time ({value} vs {base}).",
        "diff_lead_no": "The {lead} in {city} is {value}; New Delhi's is {base}.",
        "rel": "{n} minutes {dir} than", "rel0": "the same as",
        "later": "later", "earlier": "earlier",
        "diff_at": "{label}: {rel} New Delhi ({value} vs {base}).",
        "diff_win": "{label}: starts {a}, ends {b} than New Delhi ({value} vs {base}).",
        "win_rel": "{n} min {dir}", "win_rel0": "at the same time",
        "diff_note": ("{city} is at a different longitude from New Delhi, so sunset, "
                      "moonrise and the muhurats built on them move with it."),
        "date_diff": ("In {city} the festival is on {city_day}; New Delhi observes it on "
                      "{base_day}. The tithi and the sunrise or sunset it is judged at differ by place."),
        "date_same": "{city} and New Delhi observe {name} {year} on the same day, {day}.",
        "other_h2": "{name} {year}: {lead} in other cities",
        "other_item": "{city} - {value}",
        "faq_when_q": "When is {name} {year} in {city}?",
        "faq_when_a": "{name} {year} in {city} is on {weekday}, {date}.",
        "faq_ans": "In {city}, {timing}. For New Delhi it is {base}.",
        "faq_diff_q": "How is {name} {year} timing in {city} different from Delhi?",
        "main_link": "{name} {year}: date, rule and FAQs (New Delhi)",
        "main_h2": "More on {name} {year}",
        "city_page": "Vrat and tyohar calendar for {city}",
        "fest_h2": "Other festivals in {city}",
        "fest_item": "{name} {year}",
        "pill_h2": "Timings for your city",
        "pill_p": ("{name} {year} times shift by minutes between cities. Pick yours for its own "
                   "moonrise or muhurat. This page shows New Delhi."),
        "event_desc": "{name} {year} in {city}: {sentence}",
        "event_place": "{city}, {state}",
        "crumb": "Vrat & Tyohar",
    },
    "hi": {
        "title": "{name} {year} {topic} {city} में - {lead_value}",
        "h1": "{city} में {name} {year}: {topic}",
        "desc": ("{city} में {name} {year} {date}, {weekday} को है। {lead_sentence} "
                 "{extra}समय {city} के अनुसार; {diff_short}।"),
        "fact": "{city} में {name} {year} {date}, {weekday} को है।",
        "lead_s": "{city} में {lead} {value} है।",
        "diff_short_date": "नई दिल्ली में यह {base_day} को है",
        "diff_short_day": "समय नई दिल्ली से अलग कैलेंडर दिन पर पड़ता है",
        "answer2": " {label}: {value}।",
        "date_line": "{city}, {state} · IST",
        "table_h2": "{city} में {name} {year} के समय",
        "diff_h2": "{city} का समय नई दिल्ली से कैसे अलग है",
        "diff_short": "नई दिल्ली से {n} मिनट {dir}",
        "diff_short0": "नई दिल्ली के समान",
        "diff_lead": "{city} में {lead} नई दिल्ली से {rel} है ({value}, जबकि दिल्ली में {base})।",
        "diff_lead_no": "{city} में {lead} {value} है; नई दिल्ली में {base}।",
        "rel": "{n} मिनट {dir}", "rel0": "बिल्कुल उसी समय",
        "later": "बाद", "earlier": "पहले",
        "diff_at": "{label}: नई दिल्ली से {rel} ({value}, दिल्ली में {base})।",
        "diff_win": "{label}: शुरू {a}, समाप्त {b}, नई दिल्ली की तुलना में ({value}, दिल्ली में {base})।",
        "win_rel": "{n} मिनट {dir}", "win_rel0": "उसी समय",
        "diff_note": ("{city} की देशांतर रेखा नई दिल्ली से अलग है, इसलिए सूर्यास्त, चंद्रोदय "
                      "और उन पर टिके मुहूर्त भी खिसक जाते हैं।"),
        "date_diff": ("{city} में यह पर्व {city_day} को है; नई दिल्ली में {base_day} को। "
                      "तिथि और जिस सूर्योदय या सूर्यास्त पर वह परखी जाती है, वे स्थान के अनुसार बदलते हैं।"),
        "date_same": "{city} और नई दिल्ली में {name} {year} एक ही दिन, {day} को है।",
        "other_h2": "{name} {year}: अन्य शहरों में {lead}",
        "other_item": "{city} - {value}",
        "faq_when_q": "{city} में {name} {year} कब है?",
        "faq_when_a": "{city} में {name} {year} {weekday}, {date} को है।",
        "faq_ans": "{city} में {timing}। नई दिल्ली में यह {base} है।",
        "faq_diff_q": "{city} में {name} {year} का समय दिल्ली से कितना अलग है?",
        "main_link": "{name} {year}: तिथि, नियम और प्रश्न (नई दिल्ली)",
        "main_h2": "{name} {year} के बारे में और",
        "city_page": "{city} का व्रत-त्योहार कैलेंडर",
        "fest_h2": "{city} में अन्य त्योहार",
        "fest_item": "{name} {year}",
        "pill_h2": "अपने शहर का समय",
        "pill_p": ("{name} {year} का समय शहर बदलने पर कुछ मिनट बदल जाता है। अपने शहर का "
                   "चंद्रोदय या मुहूर्त देखें। इस पेज पर नई दिल्ली का समय है।"),
        "event_desc": "{city} में {name} {year}: {sentence}",
        "event_place": "{city}, {state}",
        "crumb": "व्रत और त्योहार",
    },
}


def _t(lang: str, key: str, **v) -> str:
    return TEXT.get(lang, TEXT[EN])[key].format(**v)


# --------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------

def city_festival_path(slug: str, year: int, city: City, lang: str = EN) -> str:
    return vp.festival_path(slug, year, lang) + f"/{city.slug}"


def page_paths() -> list[str]:
    """Every indexable city festival page, English and Hindi (sitemap, beacon)."""
    return [city_festival_path(s, y, c, lang)
            for lang in LANGS for y in CITY_YEARS for s in FESTIVALS for c in CITIES
            if s in vp._festival_slugs(y)]


_PUBLIC = frozenset(page_paths())


def is_public_path(path: str) -> bool:
    return path in _PUBLIC


def has_city_pages(slug: str, year: int) -> bool:
    return slug in FESTIVALS and year in CITY_YEARS and slug in vp._festival_slugs(year)


# --------------------------------------------------------------------------
# Data from the engine
# --------------------------------------------------------------------------

@functools.lru_cache(maxsize=96)
def _family_obs(year: int, city_slug: str) -> dict[str, dict]:
    """slug -> the observance, for this family's festivals in one city and year.
    The engine's own year cache holds 16 cities; 25 cities x crawlers would thrash
    it (a year is ~0.5 s), so the few observances needed are kept here (read-only)."""
    c = seo_cities.BY_SLUG[city_slug]
    out: dict[str, dict] = {}
    for o in festivals._year(year, round(c.latitude, 4), round(c.longitude, 4), c.timezone):
        if o["major"] and o["slug"] in FESTIVALS and o["slug"] not in out:
            out[o["slug"]] = o
    return out


def observance(slug: str, year: int, city: City) -> dict | None:
    """The festival as the engine dates it for `city`."""
    return _family_obs(year, city.slug).get(slug)


def _timing(o: dict, key: str) -> dict | None:
    return next((t for t in o["timings"] if t["key"] == key), None)


def _value(t: dict, day: dt.date, lang: str) -> str:
    """'8:55 PM' or '5:54 PM – 7:08 PM' (a date is added when it is not `day`)."""
    ref = dt.date.fromisoformat(t["date"]) if t.get("date") else day
    if t.get("at"):
        return vp._clock(t["at"], ref, lang)
    return f"{vp._clock(t['start'], ref, lang)} – {vp._clock(t['end'], ref, lang)}"


def _label(t: dict, lang: str) -> str:
    return (t.get(f"label_{lang}") or i18n.names(lang).FESTIVAL_TIMINGS.get(t.get("key"))
            or t["label_en"])


def _minute(iso: str) -> dt.datetime:
    """The moment as the page prints it: to the minute (the clock truncates)."""
    return dt.datetime.fromisoformat(iso).replace(second=0, microsecond=0)


def _delta(city_iso: str, base_iso: str) -> int:
    """Minutes city - base (both as printed, to the minute; a moonrise just past
    midnight in one city and before it in the other still differs by the real gap)."""
    a, b = _minute(city_iso), _minute(base_iso)
    return int((a - b).total_seconds() // 60)


def _word(lang: str, minutes: int) -> tuple[str, int]:
    return _t(lang, "later" if minutes > 0 else "earlier"), abs(minutes)


def _timing_delta(tc: dict, tb: dict) -> tuple[int, int] | None:
    """(start delta, end delta) in minutes for a window, (d, d) for a moment."""
    if tc.get("at"):
        d = _delta(tc["at"], tb["at"]) if tb.get("at") else None
        return (d, d) if d is not None else None
    if not tb.get("start"):
        return None
    return _delta(tc["start"], tb["start"]), _delta(tc["end"], tb["end"])


def _rel(lang: str, n: int) -> str:
    if n == 0:
        return _t(lang, "rel0")
    word, m = _word(lang, n)
    return _t(lang, "rel", n=m, dir=word)


def _win_rel(lang: str, n: int) -> str:
    if n == 0:
        return _t(lang, "win_rel0")
    word, m = _word(lang, n)
    return _t(lang, "win_rel", n=m, dir=word)


def _distance_km(a: City, b: City) -> float:
    p1, p2 = math.radians(a.latitude), math.radians(b.latitude)
    dl = math.radians(b.longitude - a.longitude)
    h = (math.sin((p2 - p1) / 2) ** 2
         + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2)
    return 12742 * math.asin(math.sqrt(h))


def nearby(city: City, n: int = 7) -> list[City]:
    """The city's four nearest family cities (New Delhi included), then the big
    metros, to `n` - a different set for each city."""
    pool = [BASE, *CITIES]
    ranked = sorted((c for c in pool if c != city), key=lambda c: _distance_km(city, c))
    out = ranked[:4]
    for slug in _MAJOR:
        c = seo_cities.BY_SLUG[slug]
        if len(out) < n and c != city and c not in out:
            out.append(c)
    return out


def _city_page(slug: str, year: int, c: City, lang: str) -> str:
    return vp.festival_path(slug, year, lang) if c == BASE else city_festival_path(slug, year, c, lang)


# --------------------------------------------------------------------------
# The page
# --------------------------------------------------------------------------

def _faq(slug: str, year: int, city: City, o: dict, base: dict, lang: str, cname: str,
         name: str, diff_sentence: str) -> tuple[tuple[str, str], ...]:
    day = vp._date(o)
    v = {"name": name, "year": year, "city": cname}
    out = [(_t(lang, "faq_when_q", **v),
            _t(lang, "faq_when_a", **v, weekday=vp._weekday(day, lang),
               date=vp._long_date(day, lang)))]
    for key, q_en, q_hi in FESTIVALS[slug]["q"]:
        t, tb = _timing(o, key), _timing(base, key)
        if not t:
            continue
        timing = vp._timing_text(t, day, lang)
        bval = _value(tb, vp._date(base), lang) if tb else "-"
        q = (q_hi if lang == HI else q_en).format(**v)
        out.append((q, _t(lang, "faq_ans", city=cname, timing=timing, base=bval)))
    out.append((_t(lang, "faq_diff_q", **v), diff_sentence))
    return tuple(out)


def render(slug: str, year: int, city_slug: str, lang: str) -> HTMLResponse:
    city = seo_cities.get(city_slug)
    if not has_city_pages(slug, year) or city is None or city == BASE:
        return vp._not_found(lang)
    o, base = observance(slug, year, city), observance(slug, year, BASE)
    spec = FESTIVALS[slug]
    lead_key, lead_hi, lead_en = spec["lead"]
    if o is None or base is None or not _timing(o, lead_key) or not _timing(base, lead_key):
        return vp._not_found(lang)

    L = lang if lang in (EN, HI) else EN                # the text; other codes: English, noindex
    name = spec["name"][1] if L == HI else spec["name"][0]
    lead = lead_hi if L == HI else lead_en
    cname = seo_cities.city_name(city, L) if seo_cities.has_name(city, L) else city.name
    state = seo_cities.state_name(city.state, L)
    day, bday = vp._date(o), vp._date(base)
    path = city_festival_path(slug, year, city, lang)
    alt = city_festival_path(slug, year, city, EN if lang == HI else HI)

    lead_t, lead_b = _timing(o, lead_key), _timing(base, lead_key)
    lead_value = _value(lead_t, day, L)
    base_value = _value(lead_b, bday, L)

    # --- how this differs from New Delhi, from the engine's own numbers
    items, short = [], ""
    same_day = day == bday
    for t in o["timings"]:
        tb = _timing(base, t["key"])
        d = _timing_delta(t, tb) if (tb and same_day) else None
        if d is None:
            continue
        label, val, bv = _label(t, L), _value(t, day, L), _value(tb, bday, L)
        if t.get("at"):
            items.append(_t(L, "diff_at", label=label, rel=_rel(L, d[0]), value=val, base=bv))
        else:
            items.append(_t(L, "diff_win", label=label, a=_win_rel(L, d[0]),
                            b=_win_rel(L, d[1]), value=val, base=bv))
        if t["key"] == lead_key:
            lead_item = items.pop()
            n = d[0]
            short = (_t(L, "diff_short0") if n == 0 else
                     _t(L, "diff_short", n=abs(n), dir=_word(L, n)[0]))
            lead_diff = lead_item if not t.get("at") else _t(
                L, "diff_lead", lead=lead, city=cname, rel=_rel(L, n),
                value=lead_value, base=base_value)
    if not short:                                       # no like-for-like minutes to state
        short = (_t(L, "diff_short_date", base_day=vp._short_date(bday, L)) if not same_day
                 else _t(L, "diff_short_day"))
        lead_diff = _t(L, "diff_lead_no", lead=lead, city=cname, value=lead_value,
                       base=base_value)
    if same_day:
        date_line = _t(L, "date_same", name=name, year=year, city=cname,
                       day=vp._day_label(day, L, year=True))
    else:
        date_line = _t(L, "date_diff", city=cname, city_day=vp._day_label(day, L, year=True),
                       base_day=vp._day_label(bday, L, year=True))
    diff_sentence = f"{lead_diff} {date_line}"

    # --- headline text
    v = {"name": name, "year": year, "city": cname,
         "weekday": vp._weekday(day, L), "date": vp._long_date(day, L)}
    others = [t for t in o["timings"] if t["key"] != lead_key]
    lead_sentence = _t(L, "lead_s", city=cname, lead=lead, value=lead_value)
    extra_parts = "".join(_t(L, "answer2", label=_label(t, L), value=_value(t, day, L))
                          for t in others[:2])
    answer_html = _t(L, "fact", **v) + " " + lead_sentence + extra_parts
    extra = "".join(_t(L, "answer2", label=_label(t, L), value=_value(t, day, L))
                    for t in others[:1]).strip()
    extra = extra + " " if extra else ""
    topic_title, topic_h1, topic_hi = spec["topic"]
    topic = topic_hi if L == HI else topic_title
    title = _t(L, "title", name=name, year=year, city=cname, topic=topic, lead_value=lead_value)
    h1 = _t(L, "h1", name=name, year=year, city=cname,
            topic=topic_hi if L == HI else topic_h1)
    description = _t(L, "desc", **v, lead_sentence=lead_sentence, extra=extra, diff_short=short)

    timings = "".join(f"<li>{_e(vp._timing_text(t, day, L))}</li>" for t in o["timings"])
    if o.get("tithi"):
        timings += f"<li>{_e(vp._tithi_text(o, L))}</li>"
    faq = _faq(slug, year, city, o, base, L, cname, name, diff_sentence)
    faq_html, faq_ld = seo_pages._faq(faq)

    # --- nearby and major cities: the same headline time
    rows = []
    for c in nearby(city):
        oc = observance(slug, year, c)
        tc = _timing(oc, lead_key) if oc else None
        if not tc:
            continue
        cn = seo_cities.city_name(c, L) if seo_cities.has_name(c, L) else c.name
        txt = _t(L, "other_item", city=cn, value=_value(tc, vp._date(oc), L))
        rows.append(f'<li><a href="{_e(_city_page(slug, year, c, lang))}">{_e(txt)}</a></li>')

    # --- this city's other festivals
    fest = "".join(
        f'<li><a href="{_e(city_festival_path(s, year, city, lang))}">'
        f'{_e(_t(L, "fest_item", name=FESTIVALS[s]["name"][1 if L == HI else 0], year=year))}'
        f'</a></li>'
        for s in FESTIVALS if s != slug and has_city_pages(s, year))

    body = (
        f"<h1>{_e(h1)}</h1>"
        f'<p class="date">{_e(_t(L, "date_line", city=cname, state=state))}</p>'
        f'<div class="box answer"><p><strong>{_e(answer_html)}</strong></p></div>'
        f"<h2>{_e(_t(L, 'table_h2', name=name, year=year, city=cname))}</h2>"
        f'<div class="box"><ul class="timings">{timings}</ul></div>'
        f"<h2>{_e(_t(L, 'diff_h2', city=cname))}</h2>"
        f"<p>{_e(diff_sentence)}</p>"
        + (f'<ul class="timings">{"".join(f"<li>{_e(i)}</li>" for i in items)}</ul>' if items else "")
        + f"<p><small>{_e(_t(L, 'diff_note', city=cname))}</small></p>"
        f"<h2>{_e(_t(L, 'other_h2', name=name, year=year, lead=lead))}</h2>"
        f'<ul class="links">{"".join(rows)}</ul>'
        f"<h2>{_e(vp._tx('fest.faq_h2', L))}</h2>{faq_html}"
        f"<h2>{_e(_t(L, 'main_h2', name=name, year=year))}</h2>"
        f'<ul class="links"><li><a href="{_e(vp.festival_path(slug, year, lang))}">'
        f'{_e(_t(L, "main_link", name=name, year=year))}</a></li>'
        f'<li><a href="{_e(vp.city_path(city, lang))}">'
        f'{_e(_t(L, "city_page", city=cname))}</a></li></ul>'
        f"<h2>{_e(_t(L, 'fest_h2', city=cname))}</h2>"
        f'<ul class="links">{fest}</ul>'
        + vp._cta(lang) + vp._more_links(lang))

    # --- Event: the main page's, with this city's place, dates and numbers
    ev = vp.event_ld(o, L)
    sentence = lead_sentence + extra_parts
    ev.update({
        "name": f"{name} {year} - {cname}",
        "description": _t(L, "event_desc", name=name, year=year, city=cname, sentence=sentence),
        "location": {"@type": "Place", "name": _t(L, "event_place", city=cname, state=state),
                     "address": {"@type": "PostalAddress", "addressLocality": cname,
                                 "addressRegion": state, "addressCountry": "IN"},
                     "geo": {"@type": "GeoCoordinates", "latitude": city.latitude,
                             "longitude": city.longitude}},
        "url": SITE_URL + path,
        "inLanguage": i18n.get(lang).bcp47,
    })
    crumbs = [(_t(L, "crumb"), vp.hub_path(lang)),
              (f"{name} {year}", vp.festival_path(slug, year, lang)),
              (cname, path)]
    return seo_pages._render(translated=frozenset(LANGS), title=title,
                             description=description, path=path, alt=alt, crumbs=crumbs,
                             body=body, lang=lang, extra_ld=(ev, faq_ld), cache=True)


def city_pills(slug: str, year: int, lang: str) -> str:
    """'Timings for your city' on the main festival page ("" where there are no
    city pages: another festival, year or language)."""
    if lang not in LANGS or not has_city_pages(slug, year):
        return ""
    L = lang
    name = FESTIVALS[slug]["name"][1 if L == HI else 0]
    pills = "".join(
        f'<li><a href="{_e(city_festival_path(slug, year, c, lang))}">'
        f'{_e(seo_cities.city_name(c, L) if seo_cities.has_name(c, L) else c.name)}</a></li>'
        for c in CITIES)
    return (f"<h2>{_e(_t(L, 'pill_h2'))}</h2>"
            f"<p>{_e(_t(L, 'pill_p', name=name, year=year))}</p>"
            f'<ul class="links">{pills}</ul>')


# --------------------------------------------------------------------------
# Routes
# --------------------------------------------------------------------------

def _serve(slug: str, city_slug: str, lang: str):
    s, _, y = slug.rpartition("-")
    if not y.isdigit():
        return vp._not_found(lang)
    year = int(y)
    if has_city_pages(s, year) and city_slug == BASE.slug:
        return RedirectResponse(vp.festival_path(s, year, lang), status_code=301)
    return render(s, year, city_slug, lang)


@router.get("/tyohar/{slug}/{city}", response_class=HTMLResponse)
def city_festival(slug: str, city: str):
    return _serve(slug, city, EN)


@router.get("/hi/tyohar/{slug}/{city}", response_class=HTMLResponse)
def city_festival_hi(slug: str, city: str):
    return _serve(slug, city, HI)


@router.get("/{lang:xlang}/tyohar/{slug}/{city}", response_class=HTMLResponse)
def city_festival_lang(lang: str, slug: str, city: str):
    return _serve(slug, city, lang)
