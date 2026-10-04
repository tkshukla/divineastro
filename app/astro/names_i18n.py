"""One API for panchang / festival / matching names in all site languages (DIVASTRO-123).

    from app.astro.names_i18n import names_for, add_names
    n = names_for("ta")
    n.TITHI["Ashtami"]              # "அஷ்டமி"
    n.tithi_label("Krishna", "Ashtami")   # "தேய்பிறை அஷ்டமி"
    n.festival("ekadashi", "Mohini Ekadashi")
    n.clock(dt.datetime(2026, 1, 1, 6, 14))   # "காலை 6:14"
    add_names(daily_panchang_result, "ta")    # name_ta / label_ta / notes_ta

LANGS: en, hi, kn, te, ta, ml, bn, or. Any other code (or None) gets English.

Every table is keyed by the ENGLISH name the engines emit, so a lookup is
`table.get(english, english)`:

  TITHI          16 names (Pratipada..Chaturdashi, Purnima, Amavasya)
  NAKSHATRAS     27                     VARA        7 (keyed "Sunday"..)
  YOGA           27                     KARANA      11
  PAKSHA         Shukla / Krishna, the bare word that prefixes a tithi
  MASA           12 lunar months, keyed by panchang.LUNAR_MONTHS
  SOLAR_MASA     solar months keyed by the Sun's sidereal sign ("Aries"..) for
                 the languages whose calendar is solar (ta, ml, bn, or); {} else
  RASHI          12 signs keyed by chart_service.SIGNS ("Aries"..)
  GRAHA          9 grahas keyed "Sun".."Saturn", "Rahu", "Ketu"
  CHOGHADIYA     7 slot names; CHOGHADIYA_QUALITY auspicious/neutral/inauspicious
  TIMINGS        rahu_kaal yamaganda gulika abhijit brahma_muhurta pradosh nishita
                 sunrise sunset moonrise moonset parana durmuhurtam varjyam good_time
  FESTIVAL_TIMINGS  festivals.LABELS, key for key
  FESTIVALS      festivals.py observance key -> name (incl. makar_sankranti, lohri,
                 holi, the generic "ekadashi", and the OMITTED keys)
  EKADASHI       each named Ekadashi, keyed by festivals.py's name_en
  REGIONAL_NOTE  optional strong regional framing per festival key (Durga Puja,
                 Bathukamma, Golu, Mysuru Dasara...) - show beside, not instead
  KOOTA          the 8 Ashtakoota labels (matching.KOOTA_LABELS_HI keys)
  GANA NADI VARNA VASHYA YONI TARA  the values matching.py emits
  WEEKDAY        short weekday names     MONTHS   12 Gregorian month names
  CLOCK          morning / afternoon / evening / night (+ optional late_afternoon)
  LIMBS          row labels: tithi nakshatra yoga karana vara paksha masa
                 moon_sign sun_sign panchang
  NOTE_POLAR, NOTE_WEDNESDAY  the two engine notes (see names_hi.add_hindi)

The Hindi and English tables are not copied: they are read from names_hi,
festivals, matching and choghadiya, so those stay the one copy.
"""

from __future__ import annotations

import datetime as dt
import functools
import importlib
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

LANGS = ("en", "hi", "kn", "te", "ta", "ml", "bn", "or")
REGIONAL_LANGS = ("kn", "te", "ta", "ml", "bn", "or")

TABLES = (
    "TITHI", "NAKSHATRAS", "VARA", "YOGA", "KARANA", "PAKSHA", "MASA", "SOLAR_MASA",
    "RASHI", "GRAHA", "CHOGHADIYA", "CHOGHADIYA_QUALITY", "TIMINGS", "FESTIVAL_TIMINGS",
    "FESTIVALS", "EKADASHI", "REGIONAL_NOTE", "KOOTA", "GANA", "NADI", "VARNA", "VASHYA",
    "YONI", "TARA", "WEEKDAY", "MONTHS", "CLOCK", "LIMBS",
)
TEXTS = ("NOTE_POLAR", "NOTE_WEDNESDAY")


@dataclass(frozen=True)
class Names:
    code: str
    TITHI: Mapping[str, str]
    NAKSHATRAS: Mapping[str, str]
    VARA: Mapping[str, str]
    YOGA: Mapping[str, str]
    KARANA: Mapping[str, str]
    PAKSHA: Mapping[str, str]
    MASA: Mapping[str, str]
    SOLAR_MASA: Mapping[str, str]
    RASHI: Mapping[str, str]
    GRAHA: Mapping[str, str]
    CHOGHADIYA: Mapping[str, str]
    CHOGHADIYA_QUALITY: Mapping[str, str]
    TIMINGS: Mapping[str, str]
    FESTIVAL_TIMINGS: Mapping[str, str]
    FESTIVALS: Mapping[str, str]
    EKADASHI: Mapping[str, str]
    REGIONAL_NOTE: Mapping[str, str]
    KOOTA: Mapping[str, str]
    GANA: Mapping[str, str]
    NADI: Mapping[str, str]
    VARNA: Mapping[str, str]
    VASHYA: Mapping[str, str]
    YONI: Mapping[str, str]
    TARA: Mapping[str, str]
    WEEKDAY: Mapping[str, str]
    MONTHS: tuple[str, ...]
    CLOCK: Mapping[str, str]
    LIMBS: Mapping[str, str]
    NOTE_POLAR: str
    NOTE_WEDNESDAY: str

    # -- helpers ----------------------------------------------------------
    def tithi_label(self, paksha: str | None, tithi: str) -> str:
        """"Krishna", "Ashtami" -> "कृष्ण अष्टमी" / "தேய்பிறை அஷ்டமி" / "Krishna Ashtami"."""
        name = self.TITHI.get(tithi, tithi)
        word = self.PAKSHA.get(paksha, paksha) if paksha else ""
        return f"{word or ''} {name}".strip()

    def festival(self, key: str | None, name_en: str | None = None) -> str:
        """Name of an observance from festivals.observances(): the named Ekadashi
        when key == "ekadashi", else by key; falls back to name_en."""
        if name_en and name_en in self.EKADASHI and (key in (None, "ekadashi")):
            return self.EKADASHI[name_en]
        if key and key in self.FESTIVALS:
            return self.FESTIVALS[key]
        return name_en or key or ""

    def festival_name(self, o: dict) -> str:
        return self.festival(o.get("key"), o.get("name_en"))

    def clock_word(self, hour: int) -> str:
        """Part-of-day word for an hour 0-23, on the Hindi pages' buckets
        (seo_pages._clock): night <4 or >=20, morning <12, afternoon <16,
        evening <20. A language with `late_afternoon` (bn: বিকেল) uses it 16-17."""
        if hour < 4 or hour >= 20:
            return self.CLOCK["night"]
        if hour < 12:
            return self.CLOCK["morning"]
        if hour < 16:
            return self.CLOCK["afternoon"]
        if hour < 18 and "late_afternoon" in self.CLOCK:
            return self.CLOCK["late_afternoon"]
        return self.CLOCK["evening"]

    def clock(self, moment: dt.datetime) -> str:
        """'6:29 AM' in English, '<part-of-day> 6:29' in every Indian language."""
        hm = moment.strftime("%I:%M").lstrip("0")
        if self.code == "en":
            return f"{hm} {moment.strftime('%p')}"
        return f"{self.clock_word(moment.hour)} {hm}"


def _freeze(table):
    if isinstance(table, (list, tuple)):
        return tuple(table)
    return MappingProxyType(dict(table))


def _build(code: str, values: dict) -> Names:
    kwargs = {name: _freeze(values[name]) for name in TABLES}
    kwargs.update({name: values[name] for name in TEXTS})
    return Names(code=code, **kwargs)


def _regional(code: str) -> Names:
    module = importlib.import_module(f".names_{code}", __package__)
    suffix = code.upper()
    return _build(code, {name: getattr(module, f"{name}_{suffix}") for name in TABLES + TEXTS})


# --------------------------------------------------------------------------
# English and Hindi, read from the modules that own them
# --------------------------------------------------------------------------

_EXTRA_FESTIVALS = {
    # keys festivals.py emits outside RECURRING/FESTIVALS, and the OMITTED ones
    "makar_sankranti": ("Makar Sankranti", "मकर संक्रांति"),
    "lohri": ("Lohri", "लोहड़ी"),
    "holi": ("Holi", "होली"),
    "ekadashi": ("Ekadashi", "एकादशी"),
    "santan_saptami": ("Santan Saptami", "संतान सप्तमी"),
}

_TIMINGS_EN_HI = {
    "rahu_kaal": ("Rahu Kaal", "राहु काल"),
    "yamaganda": ("Yamaganda", "यमगण्ड"),
    "gulika": ("Gulika Kaal", "गुलिक काल"),
    "abhijit": ("Abhijit Muhurta", "अभिजित मुहूर्त"),
    "brahma_muhurta": ("Brahma Muhurta", "ब्रह्म मुहूर्त"),
    "pradosh": ("Pradosh Kaal", "प्रदोष काल"),
    "nishita": ("Nishita Kaal", "निशीथ काल"),
    "sunrise": ("Sunrise", "सूर्योदय"),
    "sunset": ("Sunset", "सूर्यास्त"),
    "moonrise": ("Moonrise", "चंद्रोदय"),
    "moonset": ("Moonset", "चंद्रास्त"),
    "parana": ("Parana time", "पारण का समय"),
    "durmuhurtam": ("Durmuhurtam", "दुर्मुहूर्त"),
    "varjyam": ("Varjyam", "वर्ज्यम्"),
    "good_time": ("Good time", "शुभ समय"),
}

_LIMBS_EN_HI = {
    "tithi": ("Tithi", "तिथि"), "nakshatra": ("Nakshatra", "नक्षत्र"),
    "yoga": ("Yoga", "योग"), "karana": ("Karana", "करण"), "vara": ("Vara", "वार"),
    "paksha": ("Paksha", "पक्ष"), "masa": ("Month", "मास"),
    "moon_sign": ("Moon sign", "चंद्र राशि"), "sun_sign": ("Sun sign", "सूर्य राशि"),
    "panchang": ("Panchang", "पंचांग"),
}

_WEEKDAY_EN_HI = {
    "Sunday": ("Sun", "रवि"), "Monday": ("Mon", "सोम"), "Tuesday": ("Tue", "मंगल"),
    "Wednesday": ("Wed", "बुध"), "Thursday": ("Thu", "गुरु"), "Friday": ("Fri", "शुक्र"),
    "Saturday": ("Sat", "शनि"),
}

_MONTHS_EN = ("January", "February", "March", "April", "May", "June", "July", "August",
              "September", "October", "November", "December")
# As seo_pages.MONTHS_HI prints them.
_MONTHS_HI = ("जनवरी", "फ़रवरी", "मार्च", "अप्रैल", "मई", "जून", "जुलाई", "अगस्त",
              "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर")

_CLOCK_EN = {"morning": "morning", "afternoon": "afternoon", "evening": "evening",
             "night": "night"}
_CLOCK_HI = {"morning": "सुबह", "afternoon": "दोपहर", "evening": "शाम", "night": "रात"}

_QUALITY_EN_HI = {"auspicious": ("Auspicious", "शुभ"), "neutral": ("Neutral", "सामान्य"),
                  "inauspicious": ("Inauspicious", "अशुभ")}

_KOOTA_EN = {"varna": "Varna", "vashya": "Vashya", "tara": "Tara (Dina)", "yoni": "Yoni",
             "graha_maitri": "Graha Maitri", "gana": "Gana", "bhakoot": "Bhakoot",
             "nadi": "Nadi"}

_NOTE_POLAR_EN = ("The Sun does not both rise and set on this date at this latitude, so the "
                  "vedic day cannot be bounded by sunrise. The limbs below are reckoned from "
                  "local midnight instead, and the sunrise-based muhurtas are not defined.")
_NOTE_WEDNESDAY_EN = ("Abhijit muhurta is omitted on Wednesday, whose lord Mercury is held to "
                      "spoil it.")


def _festival_specs():
    from . import festivals as F
    seen: dict[str, tuple[str, str]] = {}
    for spec in F.RECURRING + F.FESTIVALS:
        seen.setdefault(spec.key, (spec.name_en, spec.name_hi))
    for key, pair in _EXTRA_FESTIVALS.items():
        seen.setdefault(key, pair)
    ekadashi = {en: hi for en, hi in list(F.EKADASHI_NAMES.values())
                + list(F.ADHIKA_EKADASHI_NAMES.values())}
    return seen, ekadashi, F


def _identity(keys) -> dict:
    return {k: k for k in keys}


def _english() -> Names:
    from . import names_hi as H
    from . import panchang as P
    from . import matching as M
    from .choghadiya import CHOGHADIYA_INFO
    specs, ekadashi, F = _festival_specs()
    return _build("en", {
        "TITHI": _identity(H.TITHI_HI), "NAKSHATRAS": _identity(H.NAKSHATRAS_HI),
        "VARA": _identity(H.VARA_HI), "YOGA": _identity(H.YOGA_HI),
        "KARANA": _identity(H.KARANA_HI), "PAKSHA": _identity(H.PAKSHA_HI),
        "MASA": _identity(P.LUNAR_MONTHS), "SOLAR_MASA": {},
        "RASHI": _identity(M.SIGNS_HI), "GRAHA": _identity(M.PLANET_HI),
        "CHOGHADIYA": _identity(CHOGHADIYA_INFO),
        "CHOGHADIYA_QUALITY": {k: v[0] for k, v in _QUALITY_EN_HI.items()},
        "TIMINGS": {k: v[0] for k, v in _TIMINGS_EN_HI.items()},
        "FESTIVAL_TIMINGS": {k: v[0] for k, v in F.LABELS.items()},
        "FESTIVALS": {k: v[0] for k, v in specs.items()},
        "EKADASHI": _identity(ekadashi), "REGIONAL_NOTE": {},
        "KOOTA": _KOOTA_EN, "GANA": _identity(M.GANA_HI), "NADI": _identity(M.NADI_HI),
        "VARNA": _identity(M.VARNA_HI), "VASHYA": _identity(M.VASHYA_HI),
        "YONI": _identity(M.YONI_HI), "TARA": _identity(M.TARA_HI),
        "WEEKDAY": {k: v[0] for k, v in _WEEKDAY_EN_HI.items()},
        "MONTHS": _MONTHS_EN, "CLOCK": _CLOCK_EN,
        "LIMBS": {k: v[0] for k, v in _LIMBS_EN_HI.items()},
        "NOTE_POLAR": _NOTE_POLAR_EN, "NOTE_WEDNESDAY": _NOTE_WEDNESDAY_EN,
    })


def _hindi() -> Names:
    from . import names_hi as H
    from . import matching as M
    from .choghadiya import CHOGHADIYA_INFO
    from .festivals import MONTHS_HI as LUNAR_HI
    from .panchang import LUNAR_MONTHS
    specs, ekadashi, F = _festival_specs()
    return _build("hi", {
        "TITHI": H.TITHI_HI, "NAKSHATRAS": H.NAKSHATRAS_HI, "VARA": H.VARA_HI,
        "YOGA": H.YOGA_HI, "KARANA": H.KARANA_HI, "PAKSHA": H.PAKSHA_HI,
        "MASA": dict(zip(LUNAR_MONTHS, LUNAR_HI)), "SOLAR_MASA": {},
        "RASHI": M.SIGNS_HI, "GRAHA": M.PLANET_HI,
        "CHOGHADIYA": {k: v["name_hi"] for k, v in CHOGHADIYA_INFO.items()},
        "CHOGHADIYA_QUALITY": {k: v[1] for k, v in _QUALITY_EN_HI.items()},
        "TIMINGS": {k: v[1] for k, v in _TIMINGS_EN_HI.items()},
        "FESTIVAL_TIMINGS": {k: v[1] for k, v in F.LABELS.items()},
        "FESTIVALS": {k: v[1] for k, v in specs.items()},
        "EKADASHI": ekadashi, "REGIONAL_NOTE": {},
        "KOOTA": M.KOOTA_LABELS_HI, "GANA": M.GANA_HI, "NADI": M.NADI_HI,
        "VARNA": M.VARNA_HI, "VASHYA": M.VASHYA_HI, "YONI": M.YONI_HI, "TARA": M.TARA_HI,
        "WEEKDAY": {k: v[1] for k, v in _WEEKDAY_EN_HI.items()},
        "MONTHS": _MONTHS_HI, "CLOCK": _CLOCK_HI,
        "LIMBS": {k: v[1] for k, v in _LIMBS_EN_HI.items()},
        "NOTE_POLAR": H.NOTE_POLAR_HI, "NOTE_WEDNESDAY": H.NOTE_WEDNESDAY_HI,
    })


@functools.lru_cache(maxsize=None)
def _names(code: str) -> Names:
    if code == "en":
        return _english()
    if code == "hi":
        return _hindi()
    return _regional(code)


def names_for(lang: str | None) -> Names:
    """The name tables for `lang` (one of LANGS); anything else gets English."""
    code = (lang or "en").lower()
    return _names(code if code in LANGS else "en")


def add_names(p: dict, lang: str) -> dict:
    """names_hi.add_hindi for any language: adds name_<lang> beside each limb's
    English name (tithis also paksha_<lang> and label_<lang>), the vara's
    name_<lang>, and notes_<lang>. Additive only. "hi" is exactly add_hindi;
    English (or an unknown code) leaves `p` unchanged."""
    code = (lang or "en").lower()
    if code == "hi":
        from .names_hi import add_hindi
        return add_hindi(p)
    if code not in REGIONAL_LANGS:
        return p
    n = names_for(code)
    for row in p.get("tithi") or []:
        row[f"name_{code}"] = n.TITHI.get(row.get("name"), row.get("name"))
        row[f"paksha_{code}"] = n.PAKSHA.get(row.get("paksha"), row.get("paksha"))
        row[f"label_{code}"] = f"{row[f'paksha_{code}'] or ''} {row[f'name_{code}']}".strip()
    for key, table in (("nakshatra", n.NAKSHATRAS), ("yoga", n.YOGA), ("karana", n.KARANA)):
        for row in p.get(key) or []:
            row[f"name_{code}"] = table.get(row.get("name"), row.get("name"))
    vara = p.get("vara")
    if vara:
        vara[f"name_{code}"] = n.VARA.get(vara.get("weekday"), vara.get("name"))
    notes = []
    if p.get("reckoned_from") == "midnight":
        notes.append(n.NOTE_POLAR)
    elif (p.get("muhurta") or {}).get("abhijit") is None and p.get("reckoned_from") == "sunrise":
        notes.append(n.NOTE_WEDNESDAY)
    p[f"notes_{code}"] = notes
    return p
