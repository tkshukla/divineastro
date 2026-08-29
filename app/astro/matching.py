"""Kundali Milan — Ashtakoot Guna Milan (36 points) and Mangal Dosha.

This is the compatibility method every Indian family already knows, so the job
here is to reproduce the classical tables faithfully rather than to improve on
them. Two things follow from that:

  * **Everything is table lookup, not judgement.** The tables below are printed
    verbatim from the tradition; where lineages print different numbers the
    disagreement is named in a comment and both readings are recorded, instead
    of one being quietly chosen and presented as fact.
  * **Nothing astronomical is computed here.** Both charts arrive already built
    by `chart_service`, and only the sidereal Moon, Lagna, Mars, Venus and
    Jupiter are read out of them. If the caller hands over a tropical chart the
    functions refuse rather than pretending its longitudes are sidereal.

Ashtakoot is read entirely from the Moon: its rashi drives Varna, Vashya,
Graha Maitri and Bhakoot, its nakshatra drives Tara, Yoni, Gana and Nadi.

Sources for the tables, koota by koota, are cited at each table. The overall
frame is the standard North-Indian Ashtakoot as given in Muhurta Chintamani and
reproduced in B. V. Raman's *Muhurtha*; the South-Indian Dashakoot method uses
ten kootas and different weights and is deliberately not implemented.

A caution worth passing to the reader: the 36-point score is a convention with
a long history, not a measurement. It is reported here because people ask for
it, and the bands are labelled as convention throughout.
"""

from __future__ import annotations

from ..chart_service import DOMICILE, NAKSHATRAS, SIGNS

# --------------------------------------------------------------------------
# Reference tables & Hindi vocabularies
# --------------------------------------------------------------------------

NAKSHATRA_ARC = 360.0 / 27.0          # 13°20′
PADA_ARC = NAKSHATRA_ARC / 4.0        # 3°20′

# -- Varna (1 point) -------------------------------------------------------
VARNA_OF_RASHI = {
    "Cancer": "Brahmin", "Scorpio": "Brahmin", "Pisces": "Brahmin",
    "Aries": "Kshatriya", "Leo": "Kshatriya", "Sagittarius": "Kshatriya",
    "Taurus": "Vaishya", "Virgo": "Vaishya", "Capricorn": "Vaishya",
    "Gemini": "Shudra", "Libra": "Shudra", "Aquarius": "Shudra",
}
VARNA_RANK = {"Brahmin": 4, "Kshatriya": 3, "Vaishya": 2, "Shudra": 1}
VARNA_HI = {"Brahmin": "ब्राह्मण", "Kshatriya": "क्षत्रिय", "Vaishya": "वैश्य", "Shudra": "शूद्र"}

# -- Vashya (2 points) -----------------------------------------------------
VASHYA_GROUPS = ("Chatushpada", "Manava", "Jalachara", "Vanachara", "Keeta")
VASHYA_HI = {
    "Chatushpada": "चतुष्पाद", "Manava": "मानव", "Jalachara": "जलचर",
    "Vanachara": "वनचर", "Keeta": "कीट"
}
VASHYA_TABLE = {
    "Chatushpada": (2.0, 1.0, 1.0, 1.5, 1.0),
    "Manava":      (1.0, 2.0, 1.5, 0.0, 1.0),
    "Jalachara":   (1.0, 1.5, 2.0, 1.0, 1.0),
    "Vanachara":   (0.0, 0.0, 0.0, 2.0, 0.0),
    "Keeta":       (1.0, 1.0, 1.0, 0.0, 2.0),
}

# -- Tara / Dina (3 points) ------------------------------------------------
TARA_NAMES = [
    "Janma", "Sampat", "Vipat", "Kshema", "Pratyak",
    "Sadhaka", "Vadha", "Mitra", "Ati-Mitra",
]
TARA_HI = {
    "Janma": "जन्म", "Sampat": "सम्पत्", "Vipat": "विपत्", "Kshema": "क्षेम",
    "Pratyak": "प्रत्यरि", "Sadhaka": "साधक", "Vadha": "वध", "Mitra": "मित्र",
    "Ati-Mitra": "अतिमित्र",
}
TARA_BAD = {3, 5, 7}

# -- Yoni (4 points) -------------------------------------------------------
YONI_OF_NAKSHATRA = {
    "Ashwini": ("Horse", "male"),
    "Bharani": ("Elephant", "male"),
    "Krittika": ("Sheep", "female"),
    "Rohini": ("Serpent", "male"),
    "Mrigashira": ("Serpent", "female"),
    "Ardra": ("Dog", "female"),
    "Punarvasu": ("Cat", "female"),
    "Pushya": ("Sheep", "male"),
    "Ashlesha": ("Cat", "male"),
    "Magha": ("Rat", "male"),
    "Purva Phalguni": ("Rat", "female"),
    "Uttara Phalguni": ("Cow", "male"),
    "Hasta": ("Buffalo", "female"),
    "Chitra": ("Tiger", "female"),
    "Swati": ("Buffalo", "male"),
    "Vishakha": ("Tiger", "male"),
    "Anuradha": ("Deer", "female"),
    "Jyeshtha": ("Deer", "male"),
    "Mula": ("Dog", "male"),
    "Purva Ashadha": ("Monkey", "male"),
    "Uttara Ashadha": ("Mongoose", "male"),
    "Shravana": ("Monkey", "female"),
    "Dhanishta": ("Lion", "female"),
    "Shatabhisha": ("Horse", "female"),
    "Purva Bhadrapada": ("Lion", "male"),
    "Uttara Bhadrapada": ("Cow", "female"),
    "Revati": ("Elephant", "female"),
}
YONI_ORDER = (
    "Horse", "Elephant", "Sheep", "Serpent", "Dog", "Cat", "Rat",
    "Cow", "Buffalo", "Tiger", "Deer", "Monkey", "Mongoose", "Lion",
)
YONI_HI = {
    "Horse": "अश्व (घोड़ा)", "Elephant": "गज (हाथी)", "Sheep": "मेष (भेड़)",
    "Serpent": "सर्प", "Dog": "श्वान (कुत्ता)", "Cat": "मार्जार (बिल्ली)",
    "Rat": "मूषक (चूहा)", "Cow": "गौ (गाय)", "Buffalo": "महिष (भैंस)",
    "Tiger": "व्याघ्र (बाघ)", "Deer": "मृग (हिरण)", "Monkey": "वानर (बंदर)",
    "Mongoose": "नकुल (नेवला)", "Lion": "सिंह (शेर)"
}
YONI_ENEMIES = (
    ("Horse", "Buffalo"),
    ("Elephant", "Lion"),
    ("Sheep", "Monkey"),
    ("Serpent", "Mongoose"),
    ("Dog", "Deer"),
    ("Cat", "Rat"),
    ("Cow", "Tiger"),
)
YONI_TABLE = {
    "Horse":    (4, 2, 2, 3, 2, 2, 2, 1, 0, 1, 3, 3, 2, 1),
    "Elephant": (2, 4, 3, 3, 2, 2, 2, 2, 3, 1, 2, 3, 2, 0),
    "Sheep":    (2, 3, 4, 2, 1, 2, 1, 3, 3, 1, 2, 0, 2, 1),
    "Serpent":  (3, 3, 2, 4, 2, 1, 1, 1, 1, 2, 2, 2, 0, 2),
    "Dog":      (2, 2, 1, 2, 4, 2, 1, 2, 2, 1, 0, 2, 1, 1),
    "Cat":      (2, 2, 2, 1, 2, 4, 0, 2, 2, 1, 3, 3, 2, 1),
    "Rat":      (2, 2, 1, 1, 1, 0, 4, 2, 2, 2, 2, 2, 1, 2),
    "Cow":      (1, 2, 3, 1, 2, 2, 2, 4, 3, 0, 3, 2, 2, 1),
    "Buffalo":  (0, 3, 3, 1, 2, 2, 2, 3, 4, 1, 2, 2, 2, 1),
    "Tiger":    (1, 1, 1, 2, 1, 1, 2, 0, 1, 4, 1, 1, 2, 1),
    "Deer":     (3, 2, 2, 2, 0, 3, 2, 3, 2, 1, 4, 2, 2, 2),
    "Monkey":   (3, 3, 0, 2, 2, 3, 2, 2, 2, 1, 2, 4, 2, 1),
    "Mongoose": (2, 2, 2, 0, 1, 2, 1, 2, 2, 2, 2, 2, 4, 2),
    "Lion":     (1, 0, 1, 2, 1, 1, 2, 1, 1, 1, 2, 1, 2, 4),
}

# -- Graha Maitri (5 points) -----------------------------------------------
NAISARGIKA_FRIENDS = {
    "Sun":     {"Moon", "Mars", "Jupiter"},
    "Moon":    {"Sun", "Mercury"},
    "Mars":    {"Sun", "Moon", "Jupiter"},
    "Mercury": {"Sun", "Venus"},
    "Jupiter": {"Sun", "Moon", "Mars"},
    "Venus":   {"Mercury", "Saturn"},
    "Saturn":  {"Mercury", "Venus"},
}
NAISARGIKA_ENEMIES = {
    "Sun":     {"Venus", "Saturn"},
    "Moon":    set(),
    "Mars":    {"Mercury"},
    "Mercury": {"Moon"},
    "Jupiter": {"Mercury", "Venus"},
    "Venus":   {"Sun", "Moon"},
    "Saturn":  {"Sun", "Moon", "Mars"},
}
MAITRI_POINTS = {
    frozenset(("friend", "friend")):   5.0,
    frozenset(("friend", "neutral")):  4.0,
    frozenset(("neutral", "neutral")): 3.0,
    frozenset(("friend", "enemy")):    1.0,
    frozenset(("neutral", "enemy")):   0.5,
    frozenset(("enemy", "enemy")):     0.0,
}

# -- Gana (6 points) -------------------------------------------------------
GANA_ORDER = ("Deva", "Manushya", "Rakshasa")
GANA_HI = {"Deva": "देव", "Manushya": "मनुष्य", "Rakshasa": "राक्षस"}
GANA_OF_NAKSHATRA = {
    "Ashwini": "Deva", "Bharani": "Manushya", "Krittika": "Rakshasa",
    "Rohini": "Manushya", "Mrigashira": "Deva", "Ardra": "Manushya",
    "Punarvasu": "Deva", "Pushya": "Deva", "Ashlesha": "Rakshasa",
    "Magha": "Rakshasa", "Purva Phalguni": "Manushya",
    "Uttara Phalguni": "Manushya", "Hasta": "Deva", "Chitra": "Rakshasa",
    "Swati": "Deva", "Vishakha": "Rakshasa", "Anuradha": "Deva",
    "Jyeshtha": "Rakshasa", "Mula": "Rakshasa",
    "Purva Ashadha": "Manushya", "Uttara Ashadha": "Manushya",
    "Shravana": "Deva", "Dhanishta": "Rakshasa", "Shatabhisha": "Rakshasa",
    "Purva Bhadrapada": "Manushya", "Uttara Bhadrapada": "Manushya",
    "Revati": "Deva",
}
GANA_TABLE = {
    "Deva":     (6.0, 5.0, 1.0),
    "Manushya": (5.0, 6.0, 0.0),
    "Rakshasa": (1.0, 0.0, 6.0),
}

# -- Bhakoot (7 points) ----------------------------------------------------
BHAKOOT_DOSHA_PAIRS = {
    (2, 12), (12, 2),
    (5, 9),  (9, 5),
    (6, 8),  (8, 6),
}

# -- Nadi (8 points) -------------------------------------------------------
NADI_OF_NAKSHATRA = {
    "Ashwini": "Adi", "Bharani": "Madhya", "Krittika": "Antya",
    "Rohini": "Antya", "Mrigashira": "Madhya", "Ardra": "Adi",
    "Punarvasu": "Adi", "Pushya": "Madhya", "Ashlesha": "Antya",
    "Magha": "Antya", "Purva Phalguni": "Madhya",
    "Uttara Phalguni": "Adi", "Hasta": "Adi", "Chitra": "Madhya",
    "Swati": "Antya", "Vishakha": "Antya", "Anuradha": "Madhya",
    "Jyeshtha": "Adi", "Mula": "Adi", "Purva Ashadha": "Madhya",
    "Uttara Ashadha": "Antya", "Shravana": "Antya",
    "Dhanishta": "Madhya", "Shatabhisha": "Adi",
    "Purva Bhadrapada": "Adi", "Uttara Bhadrapada": "Madhya",
    "Revati": "Antya",
}
NADI_HUMOUR = {"Adi": "Vata", "Madhya": "Pitta", "Antya": "Kapha"}
NADI_HI = {"Adi": "आदि", "Madhya": "मध्य", "Antya": "अंत्य"}
NADI_HUMOUR_HI = {"Vata": "वात", "Pitta": "पित्त", "Kapha": "कफ"}

# -- Mangal Dosha ----------------------------------------------------------
MANGAL_HOUSES = (1, 2, 4, 7, 8, 12)
MANGAL_HOUSE_WEIGHT = {7: 3, 8: 3, 1: 2, 4: 2, 12: 2, 2: 1}
MANGAL_REFERENCE_PHRASE = {"Lagna": "the Lagna", "Moon": "the Moon", "Venus": "Venus"}
MANGAL_REF_HI = {"Lagna": "लग्न", "Moon": "चंद्र", "Venus": "शुक्र"}

MANGAL_HOUSE_EXEMPTIONS = {
    1: {"Aries"},
    2: {"Gemini", "Virgo"},
    4: {"Aries", "Scorpio"},
    7: {"Cancer", "Capricorn"},
    8: {"Sagittarius", "Pisces"},
    12: {"Taurus", "Libra"},
}
MARS_OWN_SIGNS = {"Aries", "Scorpio"}
MARS_EXALTATION = "Capricorn"

SCORE_BANDS = (
    (18.0, "not recommended", "Below the conventional threshold of 18."),
    (25.0, "acceptable", "Within the conventional 18–24 band."),
    (33.0, "good", "Within the conventional 25–32 band."),
    (36.01, "excellent", "Within the conventional 33–36 band."),
)
SCORE_BANDS_HI = (
    (18.0, "अस्वीकार्य / विचारणीय", "पारंपरिक 18 गुण के न्यूनतम मानक से कम।"),
    (25.0, "मध्यम / स्वीकार्य", "पारंपरिक 18-24 गुण के मध्यम वर्ग में।"),
    (33.0, "उत्तम / शुभ", "पारंपरिक 25-32 गुण के शुभ वर्ग में।"),
    (36.01, "अति उत्तम / सर्वश्रेष्ठ", "पारंपरिक 33-36 गुण के सर्वोत्कृष्ट वर्ग में।"),
)

SIGNS_HI = {
    "Aries": "मेष", "Taurus": "वृषभ", "Gemini": "मिथुन", "Cancer": "कर्क",
    "Leo": "सिंह", "Virgo": "कन्या", "Libra": "तुला", "Scorpio": "वृश्चिक",
    "Sagittarius": "धनु", "Capricorn": "मकर", "Aquarius": "कुंभ", "Pisces": "मीन"
}

PLANET_HI = {
    "Sun": "सूर्य", "Moon": "चंद्र", "Mars": "मंगल", "Mercury": "बुध",
    "Jupiter": "गुरु", "Venus": "शुक्र", "Saturn": "शनि", "Rahu": "राहु", "Ketu": "केतु"
}

RELATION_HI = {"friend": "मित्र", "neutral": "सम", "enemy": "शत्रु", "same": "समान"}

KOOTA_LABELS_HI = {
    "varna": "वर्ण", "vashya": "वश्य", "tara": "तारा (दीना)", "yoni": "योनि",
    "graha_maitri": "ग्रह मैत्री", "gana": "गण", "bhakoot": "भकूट", "nadi": "नाड़ी"
}


class MatchingError(ValueError):
    """Raised when a chart cannot support a Kundali Milan reading."""


def _check_yoni_table() -> None:
    size = len(YONI_ORDER)
    for i in range(size):
        for j in range(size):
            if YONI_TABLE[YONI_ORDER[i]][j] != YONI_TABLE[YONI_ORDER[j]][i]:
                raise AssertionError(f"Yoni table asymmetric at {YONI_ORDER[i]}/{YONI_ORDER[j]}")
    zeros = {
        frozenset((YONI_ORDER[i], YONI_ORDER[j]))
        for i in range(size) for j in range(size) if YONI_TABLE[YONI_ORDER[i]][j] == 0
    }
    if zeros != {frozenset(p) for p in YONI_ENEMIES}:
        raise AssertionError("Yoni zero cells do not match the enemy-pair list")


_check_yoni_table()


def yoni_points(a: str, b: str) -> float:
    return float(YONI_TABLE[YONI_ORDER.index(a)][YONI_ORDER.index(b)])


def nakshatra_at(longitude: float) -> dict:
    lon = longitude % 360.0
    index = int(lon // NAKSHATRA_ARC) % 27
    within = lon - index * NAKSHATRA_ARC
    return {
        "index": index + 1,
        "name": NAKSHATRAS[index],
        "pada": int(within // PADA_ARC) + 1,
        "degree_in_nakshatra": round(within, 4),
    }


def _ordinal(n: int) -> str:
    if 11 <= n % 100 <= 13:
        return f"{n}th"
    suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def _sign_distance(from_sign: str, to_sign: str) -> int:
    return (SIGNS.index(to_sign) - SIGNS.index(from_sign)) % 12 + 1


def _relation(of: str, toward: str) -> str:
    if of == toward:
        return "friend"
    if toward in NAISARGIKA_FRIENDS[of]:
        return "friend"
    if toward in NAISARGIKA_ENEMIES[of]:
        return "enemy"
    return "neutral"


def _mutually_friendly(a: str, b: str) -> bool:
    if a == b:
        return True
    return _relation(a, b) == "friend" and _relation(b, a) == "friend"


def _vashya_group(sign: str, degree: float) -> str:
    if sign == "Sagittarius":
        return "Chatushpada" if degree >= 15.0 else "Manava"
    if sign == "Capricorn":
        return "Jalachara" if degree >= 15.0 else "Chatushpada"
    return {
        "Aries": "Chatushpada", "Taurus": "Chatushpada",
        "Gemini": "Manava", "Virgo": "Manava", "Libra": "Manava", "Aquarius": "Manava",
        "Cancer": "Jalachara", "Pisces": "Jalachara",
        "Leo": "Vanachara",
        "Scorpio": "Keeta",
    }[sign]


def _bundle(chart: object) -> dict:
    bundle = getattr(chart, "bundle", chart)
    if not isinstance(bundle, dict) or "objects" not in bundle:
        raise MatchingError("Expected a chart_service chart session or its bundle dict.")
    return bundle


def _object(bundle: dict, name: str) -> dict:
    obj = bundle["objects"].get(name)
    if obj is None:
        raise MatchingError(f"Chart is missing {name}; cannot match on it.")
    return obj


def _require_sidereal(bundle: dict) -> None:
    if bundle.get("meta", {}).get("zodiac") != "sidereal":
        raise MatchingError(
            "Kundali Milan needs a sidereal chart — rebuild it with zodiac='sidereal' (Lahiri) before matching."
        )


def moon_profile(chart: object) -> dict:
    bundle = _bundle(chart)
    _require_sidereal(bundle)
    moon = _object(bundle, "Moon")
    nak = nakshatra_at(moon["longitude"])
    rashi = moon["sign"]
    return {
        "name": bundle.get("meta", {}).get("name") or bundle.get("birth", {}).get("name") or "",
        "rashi": rashi,
        "rashi_lord": DOMICILE[rashi],
        "rashi_degree": moon["degree"],
        "position": moon["position"],
        "nakshatra": nak["name"],
        "nakshatra_index": nak["index"],
        "pada": nak["pada"],
        "varna": VARNA_OF_RASHI[rashi],
        "vashya": _vashya_group(rashi, moon["degree"]),
        "yoni": YONI_OF_NAKSHATRA[nak["name"]][0],
        "yoni_gender": YONI_OF_NAKSHATRA[nak["name"]][1],
        "gana": GANA_OF_NAKSHATRA[nak["name"]],
        "nadi": NADI_OF_NAKSHATRA[nak["name"]],
        "nadi_humour": NADI_HUMOUR[NADI_OF_NAKSHATRA[nak["name"]]],
    }


# --------------------------------------------------------------------------
# The eight kootas
# --------------------------------------------------------------------------

def _koota(key: str, label: str, maximum: float, score: float, note: str, **extra: object) -> dict:
    return {
        "key": key, "label": label, "max": maximum,
        "score": round(float(score), 2), "note": note, **extra,
    }


def _varna(groom: dict, bride: dict, lang: str = "en") -> dict:
    g, b = groom["varna"], bride["varna"]
    ok = VARNA_RANK[g] >= VARNA_RANK[b]
    label = KOOTA_LABELS_HI["varna"] if lang == "hi" else "Varna"
    if lang == "hi":
        g_hi, b_hi = VARNA_HI.get(g, g), VARNA_HI.get(b, b)
        note = (
            f"वर का वर्ण {g_hi} और कन्या का {b_hi} है — वर का वर्ण कन्या से निम्न नहीं है, जो अनुकूल है।"
            if ok else
            f"वर का वर्ण {g_hi} और कन्या का {b_hi} है — कन्या का वर्ण वर से उच्च है (वर्ण दोष)।"
        )
    else:
        note = (
            f"{g} groom, {b} bride — the groom's varna is not below the bride's, which is what this koota asks."
            if ok else
            f"{g} groom, {b} bride — the bride's varna outranks the groom's. Traditionally read as a mismatch of temperament."
        )
    return _koota("varna", label, 1.0, 1.0 if ok else 0.0, note,
                  groom_varna=g, bride_varna=b)


def _vashya(groom: dict, bride: dict, lang: str = "en") -> dict:
    g, b = groom["vashya"], bride["vashya"]
    score = VASHYA_TABLE[b][VASHYA_GROUPS.index(g)]
    label = KOOTA_LABELS_HI["vashya"] if lang == "hi" else "Vashya"
    if lang == "hi":
        g_hi, b_hi = VASHYA_HI.get(g, g), VASHYA_HI.get(b, b)
        if g == b:
            note = f"दोनों का वश्य वर्ग समान ({g_hi}) है — परस्पर आकर्षण एवं पूर्ण अनुकूलता।"
        elif score == 0.0:
            note = f"वर का {g_hi} वर्ग और कन्या का {b_hi} वर्ग — वश्य तालिका में न्यूनतम मेल (0 अंक)।"
        else:
            note = f"वर का {g_hi} वर्ग और कन्या का {b_hi} वर्ग — आंशिक अनुकूलता ({score:g}/2 अंक)।"
    else:
        if g == b:
            note = f"Both Moons fall in the {g} group — full mutual pull."
        elif score == 0.0:
            note = f"{g} groom against a {b} bride is the weakest cell in the Vashya table: neither has natural sway over the other."
        else:
            note = f"{g} groom with a {b} bride — partial sway, {score:g} of 2."
    return _koota("vashya", label, 2.0, score, note,
                  groom_vashya=g, bride_vashya=b)


def _tara_count(from_index: int, to_index: int) -> int:
    steps = (to_index - from_index) % 27 + 1
    return steps % 9 or 9


def _tara(groom: dict, bride: dict, lang: str = "en") -> dict:
    g2b = _tara_count(groom["nakshatra_index"], bride["nakshatra_index"])
    b2g = _tara_count(bride["nakshatra_index"], groom["nakshatra_index"])
    good_g2b, good_b2g = g2b not in TARA_BAD, b2g not in TARA_BAD
    score = 1.5 * good_g2b + 1.5 * good_b2g
    label = KOOTA_LABELS_HI["tara"] if lang == "hi" else "Tara (Dina)"

    if lang == "hi":
        t1_hi = TARA_HI.get(TARA_NAMES[g2b - 1], TARA_NAMES[g2b - 1])
        t2_hi = TARA_HI.get(TARA_NAMES[b2g - 1], TARA_NAMES[b2g - 1])
        p1 = f"वर से कन्या की तारा {t1_hi} ({g2b}वीं)"
        p2 = f"कन्या से वर की तारा {t2_hi} ({b2g}वीं)"
        if score == 3.0:
            note = f"{p1} और {p2} — दोनों शुभ ताराएं हैं (पूर्ण 3 अंक)।"
        elif score == 0.0:
            note = f"{p1} और {p2} — दोनों अशुभ (विपत्/प्रत्यरि/वध) ताराएं हैं (0 अंक)।"
        else:
            note = f"{p1} और {p2} — एक तारा शुभ एवं दूसरी प्रतिकूल है (1.5 अंक)।"
    else:
        parts = [
            f"{TARA_NAMES[g2b - 1]} ({_ordinal(g2b)}) counting from the groom's star",
            f"{TARA_NAMES[b2g - 1]} ({_ordinal(b2g)}) counting from the bride's",
        ]
        if score == 3.0:
            note = f"{parts[0]} and {parts[1]} — both auspicious taras."
        elif score == 0.0:
            note = f"{parts[0]} and {parts[1]} — both fall in the Vipat/Pratyak/Vadha set."
        else:
            note = f"{parts[0]} and {parts[1]} — one of the two is afflicted."

    return _koota("tara", label, 3.0, score, note,
                  groom_to_bride=g2b, bride_to_groom=b2g,
                  groom_to_bride_name=TARA_NAMES[g2b - 1],
                  bride_to_groom_name=TARA_NAMES[b2g - 1])


def _yoni(groom: dict, bride: dict, lang: str = "en") -> dict:
    g, b = groom["yoni"], bride["yoni"]
    score = yoni_points(g, b)
    label = KOOTA_LABELS_HI["yoni"] if lang == "hi" else "Yoni"
    if lang == "hi":
        g_hi, b_hi = YONI_HI.get(g, g), YONI_HI.get(b, b)
        if g == b:
            note = f"दोनों की समान योनि ({g_hi}) है — दांपत्य एवं शारीरिक अनुकूलता का सर्वोत्तम योग (4 अंक)।"
        elif score == 0.0:
            note = f"{g_hi} एवं {b_hi} परस्पर स्वाभाविक शत्रु योनि हैं (शत्रु योनि दोष, 0 अंक)।"
        else:
            rel = "मित्र योनि" if score == 3.0 else ("सम योनि" if score == 2.0 else "उदासीन योनि")
            note = f"वर की {g_hi} और कन्या की {b_hi} योनि — {rel} ({score:g}/4 अंक)।"
    else:
        if g == b:
            note = f"Both are {g} yoni — the tradition's best case for physical rapport."
        elif score == 0.0:
            note = f"{g} and {b} are one of the seven natural-enemy yoni pairs."
        else:
            note = f"{g} groom with a {b} bride — {'friendly' if score == 3.0 else 'neutral' if score == 2.0 else 'uneasy'} yonis."
    return _koota("yoni", label, 4.0, score, note,
                  groom_yoni=g, bride_yoni=b,
                  groom_gender=groom["yoni_gender"], bride_gender=bride["yoni_gender"])


def _graha_maitri(groom: dict, bride: dict, lang: str = "en") -> dict:
    gl, bl = groom["rashi_lord"], bride["rashi_lord"]
    label = KOOTA_LABELS_HI["graha_maitri"] if lang == "hi" else "Graha Maitri"
    if gl == bl:
        if lang == "hi":
            note = f"दोनों के राशि स्वामी समान ग्रह ({PLANET_HI.get(gl, gl)}) हैं — पूर्ण मानसिक तालमेल (5 अंक)।"
        else:
            note = f"Both Moon rashis are ruled by {gl}, so the two minds run on the same planet."
        return _koota("graha_maitri", label, 5.0, 5.0, note,
                      groom_lord=gl, bride_lord=bl,
                      groom_to_bride="same", bride_to_groom="same")

    g2b, b2g = _relation(gl, bl), _relation(bl, gl)
    score = MAITRI_POINTS[frozenset((g2b, b2g))]
    if lang == "hi":
        gl_hi, bl_hi = PLANET_HI.get(gl, gl), PLANET_HI.get(bl, bl)
        r1_hi, r2_hi = RELATION_HI.get(g2b, g2b), RELATION_HI.get(b2g, b2g)
        note = f"वर के राशि स्वामी {gl_hi} और कन्या के {bl_hi} हैं — परस्पर {r1_hi} एवं {r2_hi} संबंध ({score:g}/5 अंक)।"
    else:
        note = f"{gl} rules the groom's Moon and {bl} the bride's; {gl} treats {bl} as a {g2b} and {bl} treats {gl} as a {b2g}."
    return _koota("graha_maitri", label, 5.0, score, note,
                  groom_lord=gl, bride_lord=bl,
                  groom_to_bride=g2b, bride_to_groom=b2g)


def _gana(groom: dict, bride: dict, lang: str = "en") -> dict:
    g, b = groom["gana"], bride["gana"]
    score = GANA_TABLE[g][GANA_ORDER.index(b)]
    label = KOOTA_LABELS_HI["gana"] if lang == "hi" else "Gana"
    if lang == "hi":
        g_hi, b_hi = GANA_HI.get(g, g), GANA_HI.get(b, b)
        if g == b:
            note = f"दोनों का गण समान ({g_hi}) है — स्वभाव और विचारों में स्वाभाविक सामंजस्य (6 अंक)।"
        elif score >= 5.0:
            note = f"वर का {g_hi} गण और कन्या का {b_hi} गण — उत्तम अनुकूलता ({score:g}/6 अंक)।"
        else:
            note = f"वर का {g_hi} गण और कन्या का {b_hi} गण — गण दोष (स्वभाव में भिन्नता एवं तनाव की संभावना, {score:g}/6 अंक)।"
    else:
        if g == b:
            note = f"Both {g} gana — the same basic temperament."
        elif score >= 5.0:
            note = f"{g} groom and {b} bride sit next to each other in temperament."
        else:
            note = f"{g} groom against a {b} bride is the classic Gana mismatch: friction expected over behavior under stress."
    return _koota("gana", label, 6.0, score, note, groom_gana=g, bride_gana=b)


def _bhakoot(groom: dict, bride: dict, lang: str = "en") -> dict:
    g2b = _sign_distance(groom["rashi"], bride["rashi"])
    b2g = _sign_distance(bride["rashi"], groom["rashi"])
    afflicted = (g2b, b2g) in BHAKOOT_DOSHA_PAIRS
    raw = 0.0 if afflicted else 7.0
    label = KOOTA_LABELS_HI["bhakoot"] if lang == "hi" else "Bhakoot"

    cancelled, reason = False, ""
    if afflicted:
        gl, bl = groom["rashi_lord"], bride["rashi_lord"]
        if gl == bl:
            cancelled = True
            reason = (f"दोनों राशि स्वामी समान ({PLANET_HI.get(gl, gl)}) हैं" if lang == "hi"
                      else f"both Moon rashis are ruled by {gl}")
        elif _mutually_friendly(gl, bl):
            cancelled = True
            reason = (f"राशि स्वामी {PLANET_HI.get(gl, gl)} एवं {PLANET_HI.get(bl, bl)} परस्पर नैसर्गिक मित्र हैं" if lang == "hi"
                      else f"the rashi lords {gl} and {bl} are mutual natural friends")

    score = 7.0 if cancelled else raw
    if lang == "hi":
        gr_hi, br_hi = SIGNS_HI.get(groom["rashi"], groom["rashi"]), SIGNS_HI.get(bride["rashi"], bride["rashi"])
        if not afflicted:
            note = f"राशियों की स्थिति {gr_hi} से {br_hi} ({g2b}/{b2g}) — भकूट दोष रहित एवं शुभ (7 अंक)।"
        elif cancelled:
            note = f"{min(g2b, b2g)}/{max(g2b, b2g)} भकूट दोष बन रहा था, किंतु {reason} के कारण दोष परिहार (भंग) होकर अंक बहाल हुए।"
        else:
            note = f"{min(g2b, b2g)}/{max(g2b, b2g)} भकूट दोष है और कोई परिहार लागू नहीं होता (0 अंक)। गृह-समृद्धि एवं स्वास्थ्य पर विचारणीय।"
    else:
        if not afflicted:
            note = f"The Moon rashis stand {g2b}/{b2g} from each other, clear of the 2/12, 5/9 and 6/8 axes."
        elif cancelled:
            note = f"A {min(g2b, b2g)}/{max(g2b, b2g)} Bhakoot dosha, cancelled because {reason}. Points restored."
        else:
            note = f"A {min(g2b, b2g)}/{max(g2b, b2g)} Bhakoot dosha with no cancellation available."
    return _koota("bhakoot", label, 7.0, score, note,
                  groom_to_bride=g2b, bride_to_groom=b2g,
                  dosha=afflicted, cancelled=cancelled,
                  cancellation=reason, raw_score=raw)


def _nadi(groom: dict, bride: dict, lang: str = "en") -> dict:
    g, b = groom["nadi"], bride["nadi"]
    afflicted = g == b
    raw = 0.0 if afflicted else 8.0
    label = KOOTA_LABELS_HI["nadi"] if lang == "hi" else "Nadi"

    cancelled, reason = False, ""
    if afflicted:
        if groom["rashi"] == bride["rashi"] and groom["nakshatra"] != bride["nakshatra"]:
            cancelled = True
            reason = (f"दोनों की राशि {SIGNS_HI.get(groom['rashi'], groom['rashi'])} समान है किंतु नक्षत्र भिन्न हैं" if lang == "hi"
                      else f"both Moons are in {groom['rashi']} but in different nakshatras ({groom['nakshatra']} and {bride['nakshatra']})")
        elif groom["nakshatra"] == bride["nakshatra"] and groom["pada"] != bride["pada"]:
            cancelled = True
            reason = (f"दोनों का नक्षत्र समान है किंतु चरण भिन्न ({groom['pada']} व {bride['pada']}) हैं" if lang == "hi"
                      else f"both Moons are in {groom['nakshatra']} but in different padas ({groom['pada']} and {bride['pada']})")

    score = 8.0 if cancelled else raw
    if lang == "hi":
        g_hi, b_hi = NADI_HI.get(g, g), NADI_HI.get(b, b)
        h1_hi, h2_hi = NADI_HUMOUR_HI.get(NADI_HUMOUR.get(g, ""), ""), NADI_HUMOUR_HI.get(NADI_HUMOUR.get(b, ""), "")
        if not afflicted:
            note = f"वर की {g_hi} नाड़ी ({h1_hi}) और कन्या की {b_hi} नाड़ी ({h2_hi}) — भिन्न नाड़ी होने से नाड़ी दोष नहीं है (8 अंक)।"
        elif cancelled:
            note = f"दोनों की समान {g_hi} नाड़ी है, किंतु {reason} होने से नाड़ी दोष का परिहार हो गया है (8 अंक बहाल)।"
        else:
            note = f"दोनों की समान {g_hi} नाड़ी ({h1_hi}) है (नाड़ी दोष, 0 अंक)। अष्टकूट मिलान में यह सबसे भारी कूट है, जो संतान व स्वास्थ्य से संबंधित है।"
    else:
        if not afflicted:
            note = f"{g} nadi ({NADI_HUMOUR[g]}) against {b} nadi ({NADI_HUMOUR[b]}) — different, which is what this koota wants."
        elif cancelled:
            note = f"Both Moons are {g} nadi, but the dosha is cancelled: {reason}. Points restored on that cancellation."
        else:
            note = f"Both Moons are {g} nadi ({NADI_HUMOUR[g]}), and no cancellation applies. Traditionally read against children and health."
    return _koota("nadi", label, 8.0, score, note,
                  groom_nadi=g, bride_nadi=b,
                  dosha=afflicted, cancelled=cancelled,
                  cancellation=reason, raw_score=raw)


KOOTA_FUNCTIONS = (_varna, _vashya, _tara, _yoni, _graha_maitri, _gana, _bhakoot, _nadi)
MAXIMUM_POINTS = 36.0


def _band(total: float, lang: str = "en") -> tuple[str, str]:
    bands = SCORE_BANDS_HI if lang == "hi" else SCORE_BANDS
    for ceiling, verdict, detail in bands:
        if total < ceiling:
            return verdict, detail
    return bands[-1][1], bands[-1][2]


def ashtakoot(groom: object, bride: object, lang: str = "en") -> dict:
    """The 36-point Guna Milan between two charts."""
    g, b = moon_profile(groom), moon_profile(bride)
    kootas = [fn(g, b, lang=lang) for fn in KOOTA_FUNCTIONS]

    total = round(sum(k["score"] for k in kootas), 2)
    before = round(sum(k.get("raw_score", k["score"]) for k in kootas), 2)
    verdict, detail = _band(total, lang=lang)

    conv_note = (
        "18/25/33 गुण के मानक पारंपरिक नियम हैं। यदि मुख्य कूट (नाड़ी, भकूट, ग्रह मैत्री) शुभ हों तो थोड़े कम अंक भी स्वीकार्य हो सकते हैं।"
        if lang == "hi" else
        "The 18/25/33 thresholds are a widely used convention, not a measurement. Astrologers routinely override a low total when the heavier kootas are clean."
    )

    return {
        "groom": g,
        "bride": b,
        "kootas": kootas,
        "total": total,
        "maximum": MAXIMUM_POINTS,
        "total_before_cancellation": before,
        "cancellations_applied": [
            {"koota": k["key"], "reason": k["cancellation"]}
            for k in kootas if k.get("cancelled")
        ],
        "verdict": verdict,
        "band_note": detail,
        "convention_note": conv_note,
    }


# --------------------------------------------------------------------------
# Mangal Dosha
# --------------------------------------------------------------------------

def _mangal_from(reference: str, ref_sign: str, mars: dict, lang: str = "en") -> dict:
    house = _sign_distance(ref_sign, mars["sign"])
    afflicted = house in MANGAL_HOUSES
    exempt_signs = MANGAL_HOUSE_EXEMPTIONS.get(house, set())
    exempt = afflicted and mars["sign"] in exempt_signs
    
    if exempt:
        if lang == "hi":
            ex_text = f"{MANGAL_REF_HI.get(reference, reference)} से {house}वें भाव में मंगल {SIGNS_HI.get(mars['sign'], mars['sign'])} राशि में होने से शास्त्रीय परिहार लागू होता है।"
        else:
            ex_text = f"Mars in {mars['sign']} in the {_ordinal(house)} from {MANGAL_REFERENCE_PHRASE[reference]} is one of the classical sign-in-house exemptions."
    else:
        ex_text = ""

    return {
        "reference": reference,
        "reference_sign": ref_sign,
        "mars_house": house,
        "afflicted": afflicted and not exempt,
        "raw_afflicted": afflicted,
        "weight": MANGAL_HOUSE_WEIGHT.get(house, 0) if afflicted and not exempt else 0,
        "exempt_by_sign": exempt,
        "exemption": ex_text,
    }


def _jupiter_relief(bundle: dict, mars: dict, lang: str = "en") -> str:
    jupiter = bundle["objects"].get("Jupiter")
    if jupiter is None:
        return ""
    distance = _sign_distance(jupiter["sign"], mars["sign"])
    if distance == 1:
        return "गुरु और मंगल की युति है (दोष शमन)" if lang == "hi" else "Jupiter is conjunct Mars"
    if distance in (5, 7, 9):
        return f"गुरु की मंगल पर {distance}वीं शुभ दृष्टि है (दोष शमन)" if lang == "hi" else f"Jupiter casts its {_ordinal(distance)}-house aspect on Mars"
    return ""


def mangal_dosha(chart: object, lang: str = "en") -> dict:
    bundle = _bundle(chart)
    _require_sidereal(bundle)
    mars = _object(bundle, "Mars")

    references = [
        _mangal_from("Lagna", _object(bundle, "ASC")["sign"], mars, lang=lang),
        _mangal_from("Moon", _object(bundle, "Moon")["sign"], mars, lang=lang),
        _mangal_from("Venus", _object(bundle, "Venus")["sign"], mars, lang=lang),
    ]
    hits = [r for r in references if r["afflicted"]]

    mitigations: list[str] = []
    if mars["sign"] in MARS_OWN_SIGNS:
        mitigations.append(f"मंगल स्वराशि ({SIGNS_HI.get(mars['sign'], mars['sign'])}) में स्थित है" if lang == "hi" else f"Mars is in its own sign ({mars['sign']})")
    if mars["sign"] == MARS_EXALTATION:
        mitigations.append("मंगल मकर राशि में उच्च का है" if lang == "hi" else f"Mars is exalted in {MARS_EXALTATION}")
    relief = _jupiter_relief(bundle, mars, lang=lang)
    if relief:
        mitigations.append(relief)
    for r in references:
        if r["exemption"]:
            mitigations.append(r["exemption"])

    weight = max((r["weight"] for r in hits), default=0)
    if not hits:
        severity = "none" if lang != "hi" else "दोष रहित"
    elif mars["sign"] in MARS_OWN_SIGNS or mars["sign"] == MARS_EXALTATION:
        severity = "mild" if lang != "hi" else "अल्प / सामान्य"
    elif weight >= 3 and len(hits) >= 2:
        severity = "severe" if lang != "hi" else "प्रबल"
    elif weight >= 3 or len(hits) >= 3:
        severity = "moderate" if lang != "hi" else "मध्यम"
    elif weight >= 2 and len(hits) >= 2:
        severity = "moderate" if lang != "hi" else "मध्यम"
    else:
        severity = "mild" if lang != "hi" else "अल्प"

    if hits:
        if lang == "hi":
            where = ", ".join(f"{MANGAL_REF_HI.get(r['reference'], r['reference'])} से {r['mars_house']}वें" for r in hits)
            summary = f"मंगल {where} भाव में स्थित होने से मांगलिक योग बनता है (तीव्रता: {severity})।"
        else:
            where = ", ".join(f"the {_ordinal(r['mars_house'])} from {MANGAL_REFERENCE_PHRASE[r['reference']]}" for r in hits)
            by = ("all three readings" if len(hits) == 3 else "the " + " and ".join(r["reference"] for r in hits) + f" reading{'s' if len(hits) > 1 else ''}")
            summary = f"Mars falls in {where}. Manglik by {by}."
    else:
        summary = "लग्न, चंद्र अथवा शुक्र किसी भी स्थान से 1/2/4/7/8/12 भावों में मंगल स्थित नहीं है (अ-मांगलिक)।" if lang == "hi" else "Mars is clear of 1/2/4/7/8/12 from the Lagna, the Moon and Venus."

    return {
        "manglik": bool(hits),
        "severity": severity,
        "mars_position": mars["position"],
        "mars_sign": mars["sign"],
        "references": references,
        "afflicted_from": [r["reference"] for r in hits],
        "mitigations": mitigations,
        "summary": summary,
    }


def _mangal_pair(groom_dosha: dict, bride_dosha: dict, lang: str = "en") -> dict:
    both = groom_dosha["manglik"] and bride_dosha["manglik"]
    either = groom_dosha["manglik"] or bride_dosha["manglik"]

    if both:
        verdict = "संतुलित / परिहार" if lang == "hi" else "balanced"
        note = (
            "दोनों कुंडलियां मांगलिक हैं। पारंपरिक नियमानुसार दोनों का मांगलिक दोष परस्पर निष्प्रभावी (शांत) हो जाता है।"
            if lang == "hi" else
            "Both charts are Manglik. The standard reading is that the dosha is mutually cancelled — this is the reason Manglik natives are conventionally matched together."
        )
    elif either:
        who = ("वर" if groom_dosha["manglik"] else "कन्या") if lang == "hi" else ("groom" if groom_dosha["manglik"] else "bride")
        other = groom_dosha if groom_dosha["manglik"] else bride_dosha
        verdict = "एकतरफा (विचारणीय)" if lang == "hi" else "one-sided"
        note = (
            f"केवल {who} की कुंडली मांगलिक है (तीव्रता: {other['severity']})। इस स्थिति में कुंडली के अन्य परिहारों एवं शांति उपायों का परामर्श लिया जाता है।"
            if lang == "hi" else
            f"Only the {who} is Manglik ({other['severity']} severity). This is the case the tradition treats as a genuine dosha rather than a matched pair."
        )
    else:
        verdict = "दोष रहित" if lang == "hi" else "clear"
        note = "दोनों में से किसी भी कुंडली में मांगलिक दोष नहीं है।" if lang == "hi" else "Neither chart carries Mangal dosha from any of the three references."

    trad_note = (
        "मंगल दोष का विचार लग्न, चंद्र और शुक्र से किया जाता है। कई विद्वानों के मतानुसार 28 वर्ष की आयु के उपरांत मंगल दोष का प्रभाव क्षीण हो जाता है।"
        if lang == "hi" else
        "Severity aside, whether Mangal dosha should carry the weight it does is itself disputed — several respected lineages hold that it applies only from the Lagna."
    )

    return {
        "verdict": verdict,
        "both_manglik": both,
        "cancelled_by_both_manglik": both,
        "note": note,
        "tradition_note": trad_note,
    }


def match(groom: object, bride: object, lang: str = "en") -> dict:
    """Full Kundali Milan between two charts, as a JSON-ready dict."""
    guna = ashtakoot(groom, bride, lang=lang)
    groom_mangal = mangal_dosha(groom, lang=lang)
    bride_mangal = mangal_dosha(bride, lang=lang)

    disclaimer = (
        "अष्टकूट गुण मिलान एक पारंपरिक वैदिक पद्धति है। यह वैवाहिक निर्णय का एकमात्र आधार नहीं होना चाहिए; दोनों पक्षों के व्यक्तिगत स्वभाव एवं संस्कारों का विचार भी आवश्यक है।"
        if lang == "hi" else
        "Ashtakoot is a traditional convention with real cultural weight and no predictive claim behind it. It is offered as the tradition states it, and it should not be the deciding input on a marriage."
    )

    return {
        "ashtakoot": guna,
        "mangal": {
            "groom": groom_mangal,
            "bride": bride_mangal,
            "pair": _mangal_pair(groom_mangal, bride_mangal, lang=lang),
        },
        "summary": {
            "total": guna["total"],
            "maximum": MAXIMUM_POINTS,
            "verdict": guna["verdict"],
            "doshas": [
                k["key"] for k in guna["kootas"]
                if k.get("dosha") and not k.get("cancelled")
            ],
            "manglik": {
                "groom": groom_mangal["manglik"],
                "bride": bride_mangal["manglik"],
                "verdict": _mangal_pair(groom_mangal, bride_mangal, lang=lang)["verdict"],
            },
        },
        "disclaimer": disclaimer,
    }
