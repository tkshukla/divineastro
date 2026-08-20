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
# Reference tables
# --------------------------------------------------------------------------

NAKSHATRA_ARC = 360.0 / 27.0          # 13°20′
PADA_ARC = NAKSHATRA_ARC / 4.0        # 3°20′

# -- Varna (1 point) -------------------------------------------------------
# Varna follows the element of the Moon rashi: water = Brahmin, fire =
# Kshatriya, earth = Vaishya, air = Shudra. The rank ordering below is only
# used to compare the two charts; it carries no claim about people.
VARNA_OF_RASHI = {
    "Cancer": "Brahmin", "Scorpio": "Brahmin", "Pisces": "Brahmin",
    "Aries": "Kshatriya", "Leo": "Kshatriya", "Sagittarius": "Kshatriya",
    "Taurus": "Vaishya", "Virgo": "Vaishya", "Capricorn": "Vaishya",
    "Gemini": "Shudra", "Libra": "Shudra", "Aquarius": "Shudra",
}
VARNA_RANK = {"Brahmin": 4, "Kshatriya": 3, "Vaishya": 2, "Shudra": 1}

# -- Vashya (2 points) -----------------------------------------------------
# Two of the twelve rashis are split at 15°, which is why Vashya needs the
# Moon's degree and not just its sign. Sagittarius is Manava in its first half
# and Chatushpada in its second; Capricorn is Chatushpada then Jalachara.
VASHYA_GROUPS = ("Chatushpada", "Manava", "Jalachara", "Vanachara", "Keeta")

# Rows are the *bride's* group, columns the *groom's* — Vashya is asymmetric by
# tradition and the orientation matters (a Vanachara bride scores 0 against
# everyone but a Vanachara groom, while a Chatushpada bride scores 1.5 against
# a Vanachara groom). Reproduced from the Vashya Koota table as printed in
# B. V. Raman's *Muhurtha* and carried by the standard published tables.
VASHYA_TABLE = {
    #                Chatushpada  Manava  Jalachara  Vanachara  Keeta   <- groom
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
# 3rd (Vipat), 5th (Pratyak) and 7th (Vadha) counts are the inauspicious ones.
TARA_BAD = {3, 5, 7}

# -- Yoni (4 points) -------------------------------------------------------
# Fourteen animal yonis over twenty-seven nakshatras: every yoni holds one male
# and one female nakshatra except Mongoose, which holds Uttara Ashadha alone.
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

# The seven natural-enemy pairs, which score 0 and between them account for all
# fourteen yonis. This is the one part of Yoni every source agrees on, so the
# grid below is checked against it at import rather than trusted.
YONI_ENEMIES = (
    ("Horse", "Buffalo"),
    ("Elephant", "Lion"),
    ("Sheep", "Monkey"),
    ("Serpent", "Mongoose"),
    ("Dog", "Deer"),
    ("Cat", "Rat"),
    ("Cow", "Tiger"),
)

# The 14x14 grid, points out of 4: 4 same yoni, 3 friendly, 2 neutral,
# 1 unfriendly, 0 natural enemy. Transcribed from the table PVR Narasimha Rao
# implements in Jagannatha Hora, which is also what saravali.github.io and
# findyourfate print.
#
# A second, systematically more generous grid circulates (many 2s appearing as
# 3s, and Tiger/Lion at 3 rather than 1). It has far less support and is not
# used. Two widely copied pages render Horse/Deer and Buffalo/Lion
# asymmetrically; that is a transcription defect propagating between sites, not
# a directional rule — the table is symmetric, and _check_yoni_table() below
# enforces that so a future edit cannot quietly break it.
#
# One cell stayed genuinely unresolved across sources: Horse/Deer, printed as 1
# here and as 3 elsewhere. It is worth at most two points out of thirty-six.
YONI_TABLE = (
    #  Ho El Sh Se Do Ca Ra Cw Bu Ti De Mo Mg Li
    (4, 2, 2, 3, 2, 2, 2, 1, 0, 1, 1, 3, 2, 1),   # Horse
    (2, 4, 3, 3, 2, 2, 2, 2, 3, 1, 2, 3, 2, 0),   # Elephant
    (2, 3, 4, 2, 1, 2, 1, 3, 3, 1, 2, 0, 3, 1),   # Sheep
    (3, 3, 2, 4, 2, 1, 1, 1, 1, 2, 2, 2, 0, 2),   # Serpent
    (2, 2, 1, 2, 4, 2, 1, 2, 2, 1, 0, 2, 1, 1),   # Dog
    (2, 2, 2, 1, 2, 4, 0, 2, 2, 1, 3, 3, 2, 1),   # Cat
    (2, 2, 1, 1, 1, 0, 4, 2, 2, 2, 2, 2, 1, 2),   # Rat
    (1, 2, 3, 1, 2, 2, 2, 4, 3, 0, 3, 2, 2, 1),   # Cow
    (0, 3, 3, 1, 2, 2, 2, 3, 4, 1, 2, 2, 2, 1),   # Buffalo
    (1, 1, 1, 2, 1, 1, 2, 0, 1, 4, 1, 1, 2, 1),   # Tiger
    (1, 2, 2, 2, 0, 3, 2, 3, 2, 1, 4, 2, 2, 1),   # Deer
    (3, 3, 0, 2, 2, 3, 2, 2, 2, 1, 2, 4, 3, 2),   # Monkey
    (2, 2, 3, 0, 1, 2, 1, 2, 2, 2, 2, 3, 4, 2),   # Mongoose
    (1, 0, 1, 2, 1, 1, 2, 1, 1, 1, 1, 2, 2, 4),   # Lion
)

# -- Graha Maitri (5 points) -----------------------------------------------
# Naisargika (natural) planetary friendship, BPHS ch. 3. Asymmetric on purpose:
# Mercury counts the Sun a friend while the Sun counts Mercury only neutral.
NAISARGIKA_FRIENDS = {
    "Sun": {"Moon", "Mars", "Jupiter"},
    "Moon": {"Sun", "Mercury"},
    "Mars": {"Sun", "Moon", "Jupiter"},
    "Mercury": {"Sun", "Venus"},
    "Jupiter": {"Sun", "Moon", "Mars"},
    "Venus": {"Mercury", "Saturn"},
    "Saturn": {"Mercury", "Venus"},
}
NAISARGIKA_ENEMIES = {
    "Sun": {"Venus", "Saturn"},
    "Moon": set(),
    "Mars": {"Mercury"},
    "Mercury": {"Moon"},
    "Jupiter": {"Mercury", "Venus"},
    "Venus": {"Sun", "Moon"},
    "Saturn": {"Sun", "Moon", "Mars"},
}
# Keyed by the unordered pair of relations, since the classical rule reads
# "friend and enemy" without caring which side is which.
MAITRI_POINTS = {
    frozenset(("friend", "friend")): 5.0,
    frozenset(("friend", "neutral")): 4.0,
    frozenset(("neutral", "neutral")): 3.0,
    frozenset(("friend", "enemy")): 1.0,
    frozenset(("neutral", "enemy")): 0.5,
    frozenset(("enemy", "enemy")): 0.0,
}

# -- Gana (6 points) -------------------------------------------------------
GANA_OF_NAKSHATRA = {
    "Ashwini": "Deva", "Bharani": "Manushya", "Krittika": "Rakshasa",
    "Rohini": "Manushya", "Mrigashira": "Deva", "Ardra": "Manushya",
    "Punarvasu": "Deva", "Pushya": "Deva", "Ashlesha": "Rakshasa",
    "Magha": "Rakshasa", "Purva Phalguni": "Manushya", "Uttara Phalguni": "Manushya",
    "Hasta": "Deva", "Chitra": "Rakshasa", "Swati": "Deva",
    "Vishakha": "Rakshasa", "Anuradha": "Deva", "Jyeshtha": "Rakshasa",
    "Mula": "Rakshasa", "Purva Ashadha": "Manushya", "Uttara Ashadha": "Manushya",
    "Shravana": "Deva", "Dhanishta": "Rakshasa", "Shatabhisha": "Rakshasa",
    "Purva Bhadrapada": "Manushya", "Uttara Bhadrapada": "Manushya", "Revati": "Deva",
}

# Rows the groom's gana, columns the bride's. This is the most contested table
# in the whole method. Every source agrees on the diagonal (6) and that a
# Deva/Rakshasa pairing is the worst; they disagree on two things:
#
#   * Deva–Manushya. Taken here as asymmetric — 6 when the groom is the higher
#     gana, 5 when the bride is — on the same principle Varna runs on. Several
#     published tables print 5 in both directions instead.
#   * Which of Deva–Rakshasa and Manushya–Rakshasa gets the leftover 1 point.
#     Taken here as 0 for Deva–Rakshasa (cosmic opposites) and 1 for
#     Manushya–Rakshasa. A substantial minority of sources swap these.
#
# The disagreement is worth at most one point out of thirty-six, and every
# reading calls both combinations bad; the table is a module constant so a
# lineage that reads it differently can substitute its own.
GANA_TABLE = {
    #            Deva  Manushya  Rakshasa   <- bride
    "Deva":      (6.0, 6.0, 0.0),
    "Manushya":  (5.0, 6.0, 1.0),
    "Rakshasa":  (0.0, 1.0, 6.0),
}
GANA_ORDER = ("Deva", "Manushya", "Rakshasa")

# -- Bhakoot (7 points) ----------------------------------------------------
# The three afflicted mutual placements, by the count each Moon rashi makes
# from the other: 2/12 (dwirdwadasha), 5/9 (nava-pancham), 6/8 (shadashtaka).
BHAKOOT_DOSHA_PAIRS = {(2, 12), (12, 2), (5, 9), (9, 5), (6, 8), (8, 6)}

# -- Nadi (8 points) -------------------------------------------------------
# Adi/Madhya/Antya map onto Vata/Pitta/Kapha. The assignment runs in a fixed
# zig-zag of nine, repeated three times across the twenty-seven nakshatras,
# which is why it is written out rather than derived — the pattern is easy to
# state and easy to get subtly wrong.
NADI_OF_NAKSHATRA = {
    "Ashwini": "Adi", "Bharani": "Madhya", "Krittika": "Antya",
    "Rohini": "Antya", "Mrigashira": "Madhya", "Ardra": "Adi",
    "Punarvasu": "Adi", "Pushya": "Madhya", "Ashlesha": "Antya",
    "Magha": "Antya", "Purva Phalguni": "Madhya", "Uttara Phalguni": "Adi",
    "Hasta": "Adi", "Chitra": "Madhya", "Swati": "Antya",
    "Vishakha": "Antya", "Anuradha": "Madhya", "Jyeshtha": "Adi",
    "Mula": "Adi", "Purva Ashadha": "Madhya", "Uttara Ashadha": "Antya",
    "Shravana": "Antya", "Dhanishta": "Madhya", "Shatabhisha": "Adi",
    "Purva Bhadrapada": "Adi", "Uttara Bhadrapada": "Madhya", "Revati": "Antya",
}
NADI_HUMOUR = {"Adi": "Vata", "Madhya": "Pitta", "Antya": "Kapha"}

# -- Mangal Dosha ----------------------------------------------------------
# Houses 1, 2, 4, 7, 8 and 12 counted from the reference point. The 2nd is a
# South-Indian addition that the North has largely absorbed; the other five are
# common to every lineage. Severity below is ordered by how directly the house
# touches the marriage itself.
MANGAL_HOUSES = (1, 2, 4, 7, 8, 12)
MANGAL_HOUSE_WEIGHT = {7: 3, 8: 3, 1: 2, 4: 2, 12: 2, 2: 1}
# "the Lagna" and "the Moon" take an article, "Venus" does not.
MANGAL_REFERENCE_PHRASE = {"Lagna": "the Lagna", "Moon": "the Moon", "Venus": "Venus"}

# Sign-in-house exemptions from the classical Manglik-bhanga verses. Mars in
# these signs in these houses is held not to afflict.
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

# Conventional interpretation bands for the 36-point total. Convention, not
# measurement — the wording downstream should keep saying so.
SCORE_BANDS = (
    (18.0, "not recommended", "Below the conventional threshold of 18."),
    (25.0, "acceptable", "Within the conventional 18–24 band."),
    (33.0, "good", "Within the conventional 25–32 band."),
    (36.01, "excellent", "Within the conventional 33–36 band."),
)


class MatchingError(ValueError):
    """Raised when a chart cannot support a Kundali Milan reading."""


# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------

def _check_yoni_table() -> None:
    """Guard the transcribed grid against the two ways it can silently rot.

    A mis-keyed digit in a 196-cell table is invisible on review, but it cannot
    stay both symmetric and consistent with the enemy list, so those two
    properties are asserted at import.
    """
    size = len(YONI_ORDER)
    for i in range(size):
        for j in range(size):
            if YONI_TABLE[i][j] != YONI_TABLE[j][i]:
                raise AssertionError(
                    f"Yoni table asymmetric at {YONI_ORDER[i]}/{YONI_ORDER[j]}")
    zeros = {
        frozenset((YONI_ORDER[i], YONI_ORDER[j]))
        for i in range(size) for j in range(size) if YONI_TABLE[i][j] == 0
    }
    if zeros != {frozenset(p) for p in YONI_ENEMIES}:
        raise AssertionError("Yoni zero cells do not match the enemy-pair list")


_check_yoni_table()


def yoni_points(a: str, b: str) -> float:
    """Points out of 4 between two animal yonis.

    Same yoni scores 4 even when both natives hold the male (or female)
    nakshatra of that pair; the gender split within a yoni is a separate
    tradition that some lineages use to drop it to 3, and it is not applied.
    Sources do not even agree on the gender of about a third of the nakshatras,
    which is a further reason to keep it out of the score.
    """
    return float(YONI_TABLE[YONI_ORDER.index(a)][YONI_ORDER.index(b)])


def nakshatra_at(longitude: float) -> dict:
    """Nakshatra name, 1-based index and pada for a sidereal longitude."""
    lon = longitude % 360.0
    index = int(lon // NAKSHATRA_ARC) % 27
    within = lon - index * NAKSHATRA_ARC
    return {
        "index": index + 1,                      # 1-based, as the tradition counts
        "name": NAKSHATRAS[index],
        "pada": int(within // PADA_ARC) + 1,
        "degree_in_nakshatra": round(within, 4),
    }


def _ordinal(n: int) -> str:
    """1 -> '1st'. These land in text a reader sees, so 1th/2th will not do."""
    if 11 <= n % 100 <= 13:
        return f"{n}th"
    suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def _sign_distance(from_sign: str, to_sign: str) -> int:
    """Inclusive count from one rashi to another, 1..12 — whole-sign counting."""
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
    """Both lords count the other a friend (or they are the same planet)."""
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
    """Accept either a `chart_service.ChartSession` or the bundle dict it holds."""
    bundle = getattr(chart, "bundle", chart)
    if not isinstance(bundle, dict) or "objects" not in bundle:
        raise MatchingError(
            "Expected a chart_service chart session or its bundle dict.")
    return bundle


def _object(bundle: dict, name: str) -> dict:
    obj = bundle["objects"].get(name)
    if obj is None:
        raise MatchingError(f"Chart is missing {name}; cannot match on it.")
    return obj


def _require_sidereal(bundle: dict) -> None:
    """Nakshatras only mean anything against a sidereal zodiac.

    A tropical chart's longitudes are roughly 24° adrift of the sidereal ones,
    which is nearly two whole nakshatras — reading Gana or Nadi off them would
    produce confident nonsense. Refuse instead of converting silently, because
    the ayanamsa to convert by is a choice the caller has to make.
    """
    if bundle.get("meta", {}).get("zodiac") != "sidereal":
        raise MatchingError(
            "Kundali Milan needs a sidereal chart — rebuild it with "
            "zodiac='sidereal' (Lahiri) before matching.")


# --------------------------------------------------------------------------
# Chart summaries
# --------------------------------------------------------------------------

def moon_profile(chart: object) -> dict:
    """Everything Ashtakoot reads out of one chart: the Moon, and nothing else."""
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

def _koota(key: str, label: str, maximum: float, score: float, note: str,
           **extra: object) -> dict:
    return {
        "key": key, "label": label, "max": maximum,
        "score": round(float(score), 2), "note": note, **extra,
    }


def _varna(groom: dict, bride: dict) -> dict:
    g, b = groom["varna"], bride["varna"]
    ok = VARNA_RANK[g] >= VARNA_RANK[b]
    note = (
        f"{g} groom, {b} bride — the groom's varna is not below the bride's, "
        f"which is what this koota asks."
        if ok else
        f"{g} groom, {b} bride — the bride's varna outranks the groom's. "
        f"Traditionally read as a mismatch of temperament and work, and it is the "
        f"smallest koota in the scheme."
    )
    return _koota("varna", "Varna", 1.0, 1.0 if ok else 0.0, note,
                  groom_varna=g, bride_varna=b)


def _vashya(groom: dict, bride: dict) -> dict:
    g, b = groom["vashya"], bride["vashya"]
    score = VASHYA_TABLE[b][VASHYA_GROUPS.index(g)]
    if g == b:
        note = f"Both Moons fall in the {g} group — full mutual pull."
    elif score == 0.0:
        note = (f"{g} groom against a {b} bride is the weakest cell in the "
                f"Vashya table: neither has natural sway over the other.")
    else:
        note = (f"{g} groom with a {b} bride — partial sway, "
                f"{score:g} of 2.")
    return _koota("vashya", "Vashya", 2.0, score, note,
                  groom_vashya=g, bride_vashya=b)


def _tara_count(from_index: int, to_index: int) -> int:
    """The 1..9 tara reached by counting inclusively between two nakshatras."""
    steps = (to_index - from_index) % 27 + 1
    return steps % 9 or 9


def _tara(groom: dict, bride: dict) -> dict:
    # Counted in both directions and scored 1.5 each. Some lineages count only
    # from the bride's star to the groom's, which makes Tara asymmetric; the
    # both-ways reading used here is the mainstream North-Indian one and has
    # the side effect of making this koota's score symmetric.
    g2b = _tara_count(groom["nakshatra_index"], bride["nakshatra_index"])
    b2g = _tara_count(bride["nakshatra_index"], groom["nakshatra_index"])
    good_g2b, good_b2g = g2b not in TARA_BAD, b2g not in TARA_BAD
    score = 1.5 * good_g2b + 1.5 * good_b2g

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
    return _koota("tara", "Tara (Dina)", 3.0, score, note,
                  groom_to_bride=g2b, bride_to_groom=b2g,
                  groom_to_bride_name=TARA_NAMES[g2b - 1],
                  bride_to_groom_name=TARA_NAMES[b2g - 1])


def _yoni(groom: dict, bride: dict) -> dict:
    g, b = groom["yoni"], bride["yoni"]
    score = yoni_points(g, b)
    if g == b:
        note = f"Both are {g} yoni — the tradition's best case for physical rapport."
    elif score == 0.0:
        note = f"{g} and {b} are one of the seven natural-enemy yoni pairs."
    else:
        note = (f"{g} groom with a {b} bride — "
                f"{'friendly' if score == 3.0 else 'neutral' if score == 2.0 else 'uneasy'} yonis.")
    return _koota("yoni", "Yoni", 4.0, score, note,
                  groom_yoni=g, bride_yoni=b,
                  groom_gender=groom["yoni_gender"], bride_gender=bride["yoni_gender"])


def _graha_maitri(groom: dict, bride: dict) -> dict:
    gl, bl = groom["rashi_lord"], bride["rashi_lord"]
    if gl == bl:
        return _koota("graha_maitri", "Graha Maitri", 5.0, 5.0,
                      f"Both Moon rashis are ruled by {gl}, so the two minds run on "
                      f"the same planet.",
                      groom_lord=gl, bride_lord=bl,
                      groom_to_bride="same", bride_to_groom="same")
    g2b, b2g = _relation(gl, bl), _relation(bl, gl)
    score = MAITRI_POINTS[frozenset((g2b, b2g))]
    note = (f"{gl} rules the groom's Moon and {bl} the bride's; {gl} treats {bl} as a "
            f"{g2b} and {bl} treats {gl} as a {b2g}.")
    return _koota("graha_maitri", "Graha Maitri", 5.0, score, note,
                  groom_lord=gl, bride_lord=bl,
                  groom_to_bride=g2b, bride_to_groom=b2g)


def _gana(groom: dict, bride: dict) -> dict:
    g, b = groom["gana"], bride["gana"]
    score = GANA_TABLE[g][GANA_ORDER.index(b)]
    if g == b:
        note = f"Both {g} gana — the same basic temperament."
    elif score >= 5.0:
        note = f"{g} groom and {b} bride sit next to each other in temperament."
    else:
        note = (f"{g} groom against a {b} bride is the classic Gana mismatch: "
                f"the tradition expects friction over how each one behaves under stress.")
    return _koota("gana", "Gana", 6.0, score, note, groom_gana=g, bride_gana=b)


def _bhakoot(groom: dict, bride: dict) -> dict:
    g2b = _sign_distance(groom["rashi"], bride["rashi"])
    b2g = _sign_distance(bride["rashi"], groom["rashi"])
    afflicted = (g2b, b2g) in BHAKOOT_DOSHA_PAIRS
    raw = 0.0 if afflicted else 7.0

    cancelled, reason = False, ""
    if afflicted:
        gl, bl = groom["rashi_lord"], bride["rashi_lord"]
        # The two standard cancellations. Same lord covers pairs like Aries and
        # Scorpio (both Mars); mutual friendship covers e.g. Cancer and Leo.
        if gl == bl:
            cancelled = True
            reason = f"both Moon rashis are ruled by {gl}"
        elif _mutually_friendly(gl, bl):
            cancelled = True
            reason = f"the rashi lords {gl} and {bl} are mutual natural friends"

    score = 7.0 if cancelled else raw
    if not afflicted:
        note = (f"The Moon rashis stand {g2b}/{b2g} from each other, clear of the "
                f"2/12, 5/9 and 6/8 axes.")
    elif cancelled:
        note = (f"A {min(g2b, b2g)}/{max(g2b, b2g)} Bhakoot dosha, cancelled because "
                f"{reason}. Points restored on that cancellation.")
    else:
        note = (f"A {min(g2b, b2g)}/{max(g2b, b2g)} Bhakoot dosha with no cancellation "
                f"available. This is the koota traditionally tied to prosperity and "
                f"the health of the household.")
    return _koota("bhakoot", "Bhakoot", 7.0, score, note,
                  groom_to_bride=g2b, bride_to_groom=b2g,
                  dosha=afflicted, cancelled=cancelled,
                  cancellation=reason, raw_score=raw)


def _nadi(groom: dict, bride: dict) -> dict:
    g, b = groom["nadi"], bride["nadi"]
    afflicted = g == b
    raw = 0.0 if afflicted else 8.0

    cancelled, reason = False, ""
    if afflicted:
        # The two cancellations the mainstream agrees on. Both rest on the same
        # idea: identical nadi only bites when the Moons are otherwise identical
        # too, so any separation in rashi, nakshatra or pada relieves it.
        if groom["rashi"] == bride["rashi"] and groom["nakshatra"] != bride["nakshatra"]:
            cancelled = True
            reason = (f"both Moons are in {groom['rashi']} but in different "
                      f"nakshatras ({groom['nakshatra']} and {bride['nakshatra']})")
        elif groom["nakshatra"] == bride["nakshatra"] and groom["pada"] != bride["pada"]:
            cancelled = True
            reason = (f"both Moons are in {groom['nakshatra']} but in different "
                      f"padas ({groom['pada']} and {bride['pada']})")

    score = 8.0 if cancelled else raw
    if not afflicted:
        note = (f"{g} nadi ({NADI_HUMOUR[g]}) against {b} nadi ({NADI_HUMOUR[b]}) — "
                f"different, which is what this koota wants.")
    elif cancelled:
        note = (f"Both Moons are {g} nadi, but the dosha is cancelled: {reason}. "
                f"Points restored on that cancellation.")
    else:
        note = (f"Both Moons are {g} nadi ({NADI_HUMOUR[g]}), and no cancellation "
                f"applies. This is the heaviest koota in the scheme and the one "
                f"traditionally read against children and health.")
    return _koota("nadi", "Nadi", 8.0, score, note,
                  groom_nadi=g, bride_nadi=b,
                  dosha=afflicted, cancelled=cancelled,
                  cancellation=reason, raw_score=raw)


KOOTA_FUNCTIONS = (_varna, _vashya, _tara, _yoni, _graha_maitri, _gana, _bhakoot, _nadi)
MAXIMUM_POINTS = 36.0


def _band(total: float) -> tuple[str, str]:
    for ceiling, verdict, detail in SCORE_BANDS:
        if total < ceiling:
            return verdict, detail
    return SCORE_BANDS[-1][1], SCORE_BANDS[-1][2]


def ashtakoot(groom: object, bride: object) -> dict:
    """The 36-point Guna Milan between two charts.

    `groom` and `bride` are `chart_service` chart sessions (or the bundle dicts
    they carry). Order matters: four of the eight kootas are asymmetric by
    tradition, so swapping the arguments can legitimately change the total.
    """
    g, b = moon_profile(groom), moon_profile(bride)
    kootas = [fn(g, b) for fn in KOOTA_FUNCTIONS]

    total = round(sum(k["score"] for k in kootas), 2)
    before = round(sum(k.get("raw_score", k["score"]) for k in kootas), 2)
    verdict, detail = _band(total)

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
        "convention_note": (
            "The 18/25/33 thresholds are a widely used convention, not a "
            "measurement. Astrologers routinely override a low total when the "
            "heavier kootas are clean, and a high total when Bhakoot or Nadi is not."
        ),
    }


# --------------------------------------------------------------------------
# Mangal Dosha
# --------------------------------------------------------------------------

def _mangal_from(reference: str, ref_sign: str, mars: dict) -> dict:
    """Is Mars in 1/2/4/7/8/12 counted from this reference point?

    Whole-sign counting throughout. Vedic practice counts houses by sign from
    the Lagna, and counting from the Moon or Venus has no cusp to work from at
    all, so using the chart's Placidus houses here would be both inconsistent
    and untraditional.
    """
    house = _sign_distance(ref_sign, mars["sign"])
    afflicted = house in MANGAL_HOUSES
    exempt_signs = MANGAL_HOUSE_EXEMPTIONS.get(house, set())
    exempt = afflicted and mars["sign"] in exempt_signs
    return {
        "reference": reference,
        "reference_sign": ref_sign,
        "mars_house": house,
        "afflicted": afflicted and not exempt,
        "raw_afflicted": afflicted,
        "weight": MANGAL_HOUSE_WEIGHT.get(house, 0) if afflicted and not exempt else 0,
        "exempt_by_sign": exempt,
        "exemption": (
            f"Mars in {mars['sign']} in the {_ordinal(house)} from "
            f"{MANGAL_REFERENCE_PHRASE[reference]} is one of the classical "
            f"sign-in-house exemptions."
            if exempt else ""
        ),
    }


def _jupiter_relief(bundle: dict, mars: dict) -> str:
    """Jupiter's conjunction or graha drishti on Mars, the common relief clause.

    Jupiter's Vedic aspects are the 5th, 7th and 9th signs from itself. Widely
    accepted as mitigating rather than abolishing the dosha, so it is reported
    as a mitigation and never as a cancellation.
    """
    jupiter = bundle["objects"].get("Jupiter")
    if jupiter is None:
        return ""
    distance = _sign_distance(jupiter["sign"], mars["sign"])
    if distance == 1:
        return "Jupiter is conjunct Mars"
    if distance in (5, 7, 9):
        return f"Jupiter casts its {_ordinal(distance)}-house aspect on Mars"
    return ""


def mangal_dosha(chart: object) -> dict:
    """Manglik status of a single chart, read from the Lagna, Moon and Venus.

    All three references are reported rather than collapsed into one verdict,
    because lineages weigh them very differently: the Lagna reading is universal,
    the Moon reading is standard in the North, and the Venus reading is mostly a
    South-Indian refinement. A chart Manglik from one reference and clear from
    the others is a common and genuinely ambiguous case.
    """
    bundle = _bundle(chart)
    # Mangal dosha is read off whole signs, and a tropical chart's signs are a
    # sign adrift for most of the zodiac — checked here and not only in
    # ashtakoot(), because this function is public and callable on its own.
    _require_sidereal(bundle)
    mars = _object(bundle, "Mars")

    references = [
        _mangal_from("Lagna", _object(bundle, "ASC")["sign"], mars),
        _mangal_from("Moon", _object(bundle, "Moon")["sign"], mars),
        _mangal_from("Venus", _object(bundle, "Venus")["sign"], mars),
    ]
    hits = [r for r in references if r["afflicted"]]

    mitigations: list[str] = []
    if mars["sign"] in MARS_OWN_SIGNS:
        mitigations.append(f"Mars is in its own sign ({mars['sign']})")
    if mars["sign"] == MARS_EXALTATION:
        mitigations.append(f"Mars is exalted in {MARS_EXALTATION}")
    relief = _jupiter_relief(bundle, mars)
    if relief:
        mitigations.append(relief)
    for r in references:
        if r["exemption"]:
            mitigations.append(r["exemption"])

    # Severity is the heaviest afflicted house, nudged up when more than one
    # reference agrees. Own-sign and exaltation Mars is held to act with its own
    # dignity rather than as a wrecker, so it caps severity at 'mild' — a
    # mainstream reading, though a minority hold the dosha stands regardless.
    weight = max((r["weight"] for r in hits), default=0)
    if not hits:
        severity = "none"
    elif mars["sign"] in MARS_OWN_SIGNS or mars["sign"] == MARS_EXALTATION:
        severity = "mild"
    elif weight >= 3 and len(hits) >= 2:
        severity = "severe"
    elif weight >= 3 or len(hits) >= 3:
        severity = "moderate"
    elif weight >= 2 and len(hits) >= 2:
        severity = "moderate"
    else:
        severity = "mild"

    if hits:
        where = ", ".join(
            f"the {_ordinal(r['mars_house'])} from {MANGAL_REFERENCE_PHRASE[r['reference']]}"
            for r in hits
        )
        by = ("all three readings" if len(hits) == 3 else
              "the " + " and ".join(r["reference"] for r in hits) +
              f" reading{'s' if len(hits) > 1 else ''}")
        summary = f"Mars falls in {where}. Manglik by {by}."
    else:
        summary = "Mars is clear of 1/2/4/7/8/12 from the Lagna, the Moon and Venus."

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


def _mangal_pair(groom_dosha: dict, bride_dosha: dict) -> dict:
    """The pair-level reading, where the both-Manglik cancellation lives."""
    both = groom_dosha["manglik"] and bride_dosha["manglik"]
    either = groom_dosha["manglik"] or bride_dosha["manglik"]

    if both:
        # The one cancellation almost every lineage accepts: two Manglik charts
        # are held to neutralise each other, which is why Manglik natives are
        # traditionally matched with one another.
        verdict = "balanced"
        note = ("Both charts are Manglik. The standard reading is that the dosha is "
                "mutually cancelled — this is the reason Manglik natives are "
                "conventionally matched together.")
    elif either:
        who = "groom" if groom_dosha["manglik"] else "bride"
        other = groom_dosha if groom_dosha["manglik"] else bride_dosha
        verdict = "one-sided"
        note = (f"Only the {who} is Manglik ({other['severity']} severity). This is the "
                f"case the tradition treats as a genuine dosha rather than a matched "
                f"pair; the mitigations listed on that chart, if any, are what an "
                f"astrologer would weigh next.")
    else:
        verdict = "clear"
        note = "Neither chart carries Mangal dosha from any of the three references."

    return {
        "verdict": verdict,
        "both_manglik": both,
        "cancelled_by_both_manglik": both,
        "note": note,
        "tradition_note": (
            "Severity aside, whether Mangal dosha should carry the weight it does is "
            "itself disputed — several respected lineages hold that it applies only "
            "from the Lagna, and others that it lapses after the native's late twenties."
        ),
    }


# --------------------------------------------------------------------------
# Public entry point
# --------------------------------------------------------------------------

def match(groom: object, bride: object) -> dict:
    """Full Kundali Milan between two charts, as a JSON-ready dict.

    Both arguments are `chart_service` chart sessions (or their bundle dicts)
    built with `zodiac='sidereal'`. The groom's chart goes first: several kootas
    are asymmetric by tradition and the order is part of the reading, not an
    implementation detail.
    """
    guna = ashtakoot(groom, bride)
    groom_mangal = mangal_dosha(groom)
    bride_mangal = mangal_dosha(bride)

    return {
        "ashtakoot": guna,
        "mangal": {
            "groom": groom_mangal,
            "bride": bride_mangal,
            "pair": _mangal_pair(groom_mangal, bride_mangal),
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
                "verdict": _mangal_pair(groom_mangal, bride_mangal)["verdict"],
            },
        },
        "disclaimer": (
            "Ashtakoot is a traditional convention with real cultural weight and no "
            "predictive claim behind it. It is offered as the tradition states it, "
            "and it should not be the deciding input on a marriage."
        ),
    }
