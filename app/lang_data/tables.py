"""The registry of per-language tables (DIVASTRO-143): which constant in
`app/lang_data/<code>.py` feeds which live table, how it is shaped, and where the
English reference comes from.

Used by lang_data.merge (the import-time hooks), the skeleton generator and the
checker. Importing this module is cheap and imports nothing from app.*; the live
tables are looked up lazily (`live()`), only by the skeleton and the checker.

Shapes of the constants in a language file (`shape`):

  dict      {key: str}                    TEXT-like tables, banks keyed by house/slug
  pairs     ((field0, field1), ...)       FAQ (question, answer), MORE_LINKS (href, text)
  tuple     (12 strings,)                 month names
  scalar    "str"                         one value
  variants  {1..12: ("spelling", ...)}    alternative month spellings

and how it lands in the live table (`kind`, lang_data.MERGERS):

  text        table[code]            = {key: str}
  bank        table[key][code]       = str             (MOON_HOUSE[3]["pa"])
  pairs       table[code]            = ((a, b), ...)
  tuple       table[code]            = (12 names)
  scalar      table[code]            = str
  choghadiya  table[name]["description_<code>"] = str
  variants    table[code]            = {1..12: (spellings,)}
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass, field
from typing import Callable


@dataclass(frozen=True)
class Spec:
    id: str                     # the constant's name in app/lang_data/<code>.py
    group: str                  # READY key it belongs to ("seo", "rashifal", ... "app")
    module: str                 # shared module holding the live table
    attr: str                   # ... and its name there
    kind: str                   # how it merges (see above)
    shape: str = "dict"         # what the constant looks like (see above)
    ref: str = "en"             # language whose entries define the key set ("en", or "kn" if no English)
    optional: bool = False      # may stay empty (the English / names_<code> value is used)
    fields: tuple[str, ...] = ()        # names of a pair's parts ("q", "a")
    note: str = ""              # skeleton header: what this table is for
    skip: Callable[[], set] | None = None   # keys not to translate here (filled from elsewhere)


def _recurring_reused() -> set:
    return set(importlib.import_module("app.recurring_text")._REUSED)


def _mundan_keys() -> set:
    return set(importlib.import_module("app.muhurat_text").MUNDAN["en"])


SPECS: dict[str, Spec] = {s.id: s for s in (
    # ---- seo: /panchang /rahu-kaal /choghadiya /kundali-milan /free-kundali + shared chrome
    Spec("SEO_TEXT", "seo", "app.seo_text", "TEXT", "text",
         note="page text of /panchang /rahu-kaal /choghadiya /kundali-milan /free-kundali"),
    Spec("SEO_FAQ", "seo", "app.seo_text", "FAQ", "pairs", "pairs", fields=("q", "a"),
         note="the seven free-kundali FAQ pairs (plain text)"),
    Spec("CHROME", "seo", "app.i18n", "CHROME", "text",
         note="chrome shared by every server page: breadcrumb, footer links, disclaimer (HTML: write &amp;)"),
    Spec("STAY_STRIP", "seo", "app.stay_strip", "TEXT", "text",
         note="the 'Stay in touch' strip at the foot of the pages"),
    Spec("CITY_NAMES", "seo", "app.seo_city_names", "CITIES", "text",
         note="the 114 cities as that language's newspapers spell them (key = URL slug)"),
    Spec("STATE_NAMES", "seo", "app.seo_city_names", "STATES", "text",
         note="the states and union territories (key = English state name)"),
    Spec("CHOGHADIYA_DESC", "seo", "app.astro.choghadiya", "CHOGHADIYA_INFO", "choghadiya",
         note="one-line description of each of the seven choghadiya slots"),
    # ---- rashifal
    Spec("RASHIFAL_TEXT", "rashifal", "app.rashifal_text", "TEXT", "text",
         note="page text of /rashifal and /rashifal/<sign>"),
    Spec("RASHIFAL_MORE_LINKS", "rashifal", "app.rashifal_text", "MORE_LINKS", "pairs", "pairs",
         fields=("href", "text"), note="'More free tools' links: keep every href, translate the text; "
         "the first href is '{twin:en}' (this page in English)"),
    Spec("RASHIFAL_TONE_LABEL", "rashifal", "app.rashifal_text", "TONE_LABEL", "text",
         note="the three day tones (keys good / mixed / easy)"),
    Spec("RASHIFAL_MOON_HOUSE", "rashifal", "app.rashifal_text", "MOON_HOUSE", "bank",
         note="Moon transit through houses 1-12 (key = house number)"),
    Spec("RASHIFAL_SATURN_HOUSE", "rashifal", "app.rashifal_text", "SATURN_HOUSE", "bank",
         note="Saturn transit through houses 1-12"),
    Spec("RASHIFAL_JUPITER_HOUSE", "rashifal", "app.rashifal_text", "JUPITER_HOUSE", "bank",
         note="Jupiter transit through houses 1-12"),
    Spec("RASHIFAL_RAHU_HOUSE", "rashifal", "app.rashifal_text", "RAHU_HOUSE", "bank",
         note="Rahu transit through houses 1-12"),
    Spec("RASHIFAL_KETU_LINE", "rashifal", "app.rashifal_text", "KETU_LINE", "bank",
         note="Ketu line, True = favourable house, False = quiet house; {n} is the house"),
    Spec("RASHIFAL_CLOCK_LANG", "rashifal", "app.rashifal_text", "CLOCK_LANG", "scalar", "scalar",
         optional=True, note="leave '' (the language's own clock words); 'en' prints 6:29 AM as Hindi pages do"),
    # ---- vrat & festivals
    Spec("VRAT_TEXT", "vrat", "app.vrat_text", "TEXT", "text",
         note="page text of /vrat-tyohar, /ekadashi-<year>, /tyohar/<slug>-<year>"),
    Spec("VRAT_ABOUT", "vrat", "app.vrat_text", "ABOUT", "text",
         note="what each of the 47 festivals / vrats is (key = festival slug)"),
    Spec("VRAT_NOTES", "vrat", "app.vrat_text", "NOTES", "text",
         note="tradition notes on dates that differ between almanacs (key = festival slug)"),
    Spec("VRAT_RULES", "vrat", "app.vrat_text", "RULES", "text", ref="kn",
         note="'how the date is fixed' sentences: head {month}, tithi {paksha} {tithi}, rule.<kind>, key.<observance>"),
    # ---- nakshatra, rashi, naam-milan
    Spec("NAKSHATRA_PAGE_TEXT", "nakshatra", "app.nakshatra_page_text", "TEXT", "text",
         note="page text of /nakshatra /rashi (nakshatra_pages.py)"),
    Spec("NAKSHATRA_TRAITS", "nakshatra", "app.nakshatra_text", "NAKSHATRA_TRAITS", "bank",
         note="character paragraph of each of the 27 nakshatras (key = slug)"),
    Spec("RASHI_TRAITS", "nakshatra", "app.nakshatra_text", "RASHI_TRAITS", "bank",
         note="character paragraph of each of the 12 rashis (key = slug)"),
    Spec("NAKSHATRA_FACTS", "nakshatra", "app.nakshatra_text", "FACTS", "text", ref="kn",
         note="deity.<slug> and symbol.<slug> of each nakshatra"),
    Spec("NAAM_MILAN_TEXT", "nakshatra", "app.naam_milan_text", "TEXT", "text",
         note="page text of /naam-se-kundali-milan"),
    Spec("NAAM_MILAN_ENGINE", "nakshatra", "app.naam_milan_text", "ENGINE", "text", ref="kn",
         note="score-band notes and the convention note of a naam-milan result"),
    # ---- muhurat
    Spec("MUHURAT_TEXT", "muhurat", "app.muhurat_text", "TEXT", "text", skip=_mundan_keys,
         note="page text of /muhurat/<kind>-<year> (the mundan-only keys are MUHURAT_MUNDAN)"),
    Spec("MUHURAT_MUNDAN", "muhurat", "app.muhurat_text", "MUNDAN", "text",
         note="the mundan (first haircut) muhurat's own wording"),
    Spec("MUHURAT_MONTHS", "muhurat", "app.muhurat_text", "MONTHS", "tuple", "tuple", optional=True,
         note="only if this page must spell the months differently from names_<code>.MONTHS; else leave ()"),
    # ---- recurring vrat pages (purnima, amavasya, pradosh ...)
    Spec("RECURRING_TEXT", "recurring", "app.recurring_text", "TEXT", "text", skip=_recurring_reused,
         note="page text of /purnima-<year>, /amavasya-<year>, /pradosh-vrat-<year> ... "
              "(the keys it shares with VRAT_TEXT are taken from there)"),
    # ---- /sitemap hub
    Spec("HUB_LABELS", "hub", "app.hub_text", "LABELS", "text",
         note="section names of the crawlable /sitemap page and the footer link block"),
    # ---- app: names_<code>.py and static/i18n/<code>.json are checked beside these
    Spec("ASTRO_TERMS", "app", "app.astro_terms", "TERMS", "text", ref="kn",
         note="house / dasha / sign vocabulary for the AI narration and the chart labels"),
    Spec("ASTRO_MONTHS", "app", "app.astro_terms", "MONTH_VARIANTS", "variants", "variants",
         optional=True, note="other spellings of a Gregorian month the AI may write (month number -> spellings)"),
)}

#: The constants a language file may set that are not text tables.
CONFIG = ("READY", "AKSHAR", "ALLOW_LATIN", "KEEP_ENGLISH")

#: English hints for the tables with no English column (skeleton comments).
RULE_HINTS = {
    "head": "{month} (amanta) ",
    "tithi": "{paksha} {tithi}: ",
    "rule.udaya": "tithi prevailing at sunrise",
    "rule.pratah": "tithi prevailing in Pratahkala (first fifth of the day)",
    "rule.purvahna": "tithi prevailing in the forenoon (purvahna)",
    "rule.madhyahna": "tithi prevailing at Madhyahna (midday fifth of the day)",
    "rule.aparahna": "tithi prevailing at Aparahna (fourth fifth of the day)",
    "rule.dina": "first day on which the tithi is present between sunrise and sunset",
    "rule.sayahna": "tithi prevailing at sunset",
    "rule.pradosh": "tithi prevailing in Pradosh kaal (after sunset)",
    "rule.nishita": "tithi prevailing at Nishita kaal (midnight)",
    "rule.moonrise": "tithi prevailing at moonrise",
    "key.ekadashi": "Smarta: Ekadashi prevailing at sunrise (second day if at two sunrises); parana next "
                    "day after sunrise and after Hari Vasara, within Pratahkala and before Dwadashi ends",
    "key.makar_sankranti": "the Sun's entry into sidereal Makara (Capricorn); punya kaal follows it until sunset",
    "key.lohri": "the day before Makar Sankranti",
    "key.holi": "the day after Holika Dahan",
}
ENGINE_HINTS = {
    "band_note0": "Below the traditional minimum of 18 gunas.",
    "band_note1": "In the traditional 18-24 gunas band.",
    "band_note2": "In the traditional 25-32 gunas band.",
    "band_note3": "In the traditional 33-36 gunas band.",
    "convention_note": "The 18/25/33 guna thresholds are a widely used convention, not a measurement. "
                       "Astrologers often accept a lower total if the heavily weighted kootas are free of dosha.",
}


def live(spec: Spec):
    """The live shared table (imports the shared module, which merges every language)."""
    return getattr(importlib.import_module(spec.module), spec.attr)


# --------------------------------------------------------------------------
# Flat views: {key: str} of a constant in a language file, and of the English
# reference. Pair tuples become "0.q", "0.a" ...; a tuple becomes {0: ..., 11: ...}.
# --------------------------------------------------------------------------

def flatten(table_id: str, data) -> dict:
    spec = SPECS[table_id]
    if data is None:
        return {}
    if spec.shape == "pairs":
        return {f"{i}.{spec.fields[j]}": part
                for i, pair in enumerate(data) for j, part in enumerate(pair)}
    if spec.shape == "tuple":
        return {i: v for i, v in enumerate(data)}
    if spec.shape == "scalar":
        return {"": data} if data else {}
    if spec.shape == "variants":
        return {k: " / ".join(v) for k, v in data.items()}
    return dict(data)


def english(spec: Spec) -> dict:
    """{flat key: English text ('' where there is none)} — the keys a language must
    have. For a table with no English column, the keys come from the `ref` language."""
    table = live(spec)
    skip = spec.skip() if spec.skip else set()
    sid = spec.id
    if sid in ("RASHIFAL_MOON_HOUSE", "RASHIFAL_SATURN_HOUSE", "RASHIFAL_JUPITER_HOUSE",
               "RASHIFAL_RAHU_HOUSE", "RASHIFAL_KETU_LINE", "NAKSHATRA_TRAITS", "RASHI_TRAITS"):
        return {k: v["en"] for k, v in table.items()}
    if sid == "CITY_NAMES":
        cities = importlib.import_module("app.seo_cities").CITIES
        return {c.slug: c.name for c in cities}
    if sid == "STATE_NAMES":
        cities = importlib.import_module("app.seo_cities").CITIES
        return {s: s for s in sorted({c.state for c in cities})}
    if sid == "CHOGHADIYA_DESC":
        return {name: info["description"] for name, info in table.items()}
    if sid == "MUHURAT_MONTHS":
        import calendar
        return {i: calendar.month_name[i + 1] for i in range(12)}
    if sid == "ASTRO_TERMS":
        return {k: k for k in table["kn"]}
    if sid == "ASTRO_MONTHS":
        return {}
    if sid == "RASHIFAL_CLOCK_LANG":
        return {}
    if sid == "MUHURAT_MUNDAN":
        return dict(table["en"])
    if sid == "RASHIFAL_TEXT":
        # A language writes its own words for "4th house" (house.1 .. house.12); English computes the ordinal.
        out = {k: v for k, v in table["en"].items() if k not in skip}
        for n in range(1, 13):
            out[f"house.{n}"] = f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"
        return out
    if sid == "RASHIFAL_MORE_LINKS":
        out = flatten(sid, table["en"])
        out["0.href"], out["0.text"] = "{twin:en}", "Read in English"     # English's own is the Hindi twin
        return out
    if spec.shape == "pairs":
        return flatten(sid, table["en"])
    if spec.ref != "en":
        hints = RULE_HINTS if sid == "VRAT_RULES" else ENGINE_HINTS if sid == "NAAM_MILAN_ENGINE" else {}
        if sid == "NAKSHATRA_FACTS":
            nm = importlib.import_module("app.astro.namakshar")
            for n in nm.NAKSHATRA_LIST:
                hints[f"deity.{n.slug}"], hints[f"symbol.{n.slug}"] = n.deity, n.symbol
        return {k: hints.get(k, "") for k in table[spec.ref]}
    return {k: v for k, v in table["en"].items() if k not in skip}


LEGACY = ("kn", "te", "ta", "ml", "bn", "or")


def placeholder_rules(spec: Spec) -> dict:
    """{key: (core, allowed)} — the {names} a value must keep and may use.

    English is NOT the reference: its templates carry Hindi-twin helpers ({city_hi},
    {name_hi}) and the regional languages' templates legitimately differ from them and
    sometimes from each other (ta/ml drop {date} from a title kn keeps). So:
      core     = the placeholders EVERY complete regional language (kn te ta ml bn or) keeps
      allowed  = the ones ANY of them (or English) uses, plus the astrology labels
                 ({t_rahu_kaal}, {l_tithi} ... — i18n.name_vars)
    A key none of them has falls back to English's own set for both."""
    from .check import placeholders
    if spec.kind not in ("text", "bank"):
        return {}
    table = live(spec)
    rules = {}
    for key in english(spec):
        if spec.kind == "text":
            values = [table.get(code, {}).get(key) for code in LEGACY]
            en = table.get("en", {}).get(key, "")
        else:
            values = [table.get(key, {}).get(code) for code in LEGACY]
            en = table.get(key, {}).get("en", "")
        sets = [placeholders(v) for v in values if v]
        if sets:
            core = frozenset.intersection(*sets)
            allowed = frozenset.union(*sets)
        else:
            core = allowed = placeholders(en)
        rules[key] = (core, allowed)
    return rules


def expected_placeholders(spec: Spec) -> dict:
    return placeholder_rules(spec)


def by_group(group: str) -> list[Spec]:
    return [s for s in SPECS.values() if s.group == group]
