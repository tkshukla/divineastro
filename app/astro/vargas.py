"""Divisional charts (vargas) and the classical chart yogas.

Two layers of classical Jyotish that the rest of the app did not have, and that
a kundali reading is thin without:

  * **Vargas** — the divisional charts. A rashi chart says where a planet is;
    a varga says what it is worth in one department of life. D9 Navamsa is the
    one that matters most, because classical practice judges marriage and the
    underlying strength of every planet from it rather than from D1.
  * **Yogas** — the named planetary combinations. These are the sentences the
    tradition actually speaks in: Gaja Kesari, Ruchaka, Neecha Bhanga, and the
    Dhana and Raja yogas built out of house lordships.

Three rules govern everything below, and they are the same three that govern
``matching.py``:

  * **Nothing astronomical is computed here.** The chart arrives already built
    by ``chart_service``; only sidereal longitudes are read out of it. A varga
    is arithmetic on a longitude, and a yoga is a lookup on a sign.
  * **Sidereal only.** A tropical chart's planets sit roughly a whole sign away
    from their sidereal positions, which would move every varga sign and break
    every dignity test. Tropical input is refused rather than converted, since
    the ayanamsa to convert by is the caller's choice.
  * **Where lineages disagree, the disagreement is named and the choice is a
    module constant** so a lineage that reads a rule differently can substitute
    its own rather than fork the file.

**Houses are whole-sign throughout**, counted by rashi from the Lagna, and
inside a varga counted by rashi from the varga Lagna. That is what Jyotish
means by a house; the chart's Placidus cusps, if it has any, are a Western
layer and are deliberately not consulted here.

**On what is deliberately missing.** This module implements five divisions
(D1, D3, D7, D9, D10, D12) out of the classical sixteen, and ten yoga families
(nine plus the 32-yoga Nabhasa group) out of the several hundred the
literature names. Nothing here is a guess: a
rule the sources did not agree on was left out, and the omissions are listed in
:data:`NOT_IMPLEMENTED` so a reader can see the edge of the map. In particular
there is no Vimsopaka Bala and no Ashtakavarga — both need divisions this
module does not compute, and a partial version of either would be a number that
looks authoritative and is not.

Chapter numbering differs between editions and translations of the classical
texts, so sources are cited by text name and by the chapter only where the
citation is stable (BPHS ch. 3 for dignities, which ``matching.py`` already
cites for the same chapter's friendship table).
"""

from __future__ import annotations

from ..chart_service import CLASSICAL, DOMICILE, MODALITY, SIGNS, angular_sep, dms

# --------------------------------------------------------------------------
# Reference tables
# --------------------------------------------------------------------------

# The seven grahas in the traditional weekday order. chart_service.CLASSICAL
# holds the same seven in the Chaldean order it uses elsewhere; the set is
# asserted equal at import so a change there cannot silently drop a planet here.
GRAHAS = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")

# Rahu and Ketu are carried through the vargas because people look for them,
# but they are kept out of every yoga rule below. They own no sign, so they
# cannot be a house lord; their exaltation signs are disputed three ways
# (Taurus/Scorpio, Gemini/Sagittarius, Virgo/Pisces), so they cannot be given a
# dignity; and their aspects are a minority doctrine. See NOT_IMPLEMENTED.
NODE_NAMES = ("True Node", "North Node", "Mean Node")

KENDRAS = (1, 4, 7, 10)          # angles — the houses of action
TRIKONAS = (1, 5, 9)             # trines — the houses of fortune
DHANA_HOUSES = (2, 5, 9, 11)     # wealth, purva punya, fortune, gains

# -- Dignities (BPHS ch. 3) ------------------------------------------------
# Sign-level exaltation and debilitation. The deep-exaltation degrees are kept
# alongside because they are part of the same verse and downstream text likes
# to quote them, but every yoga test below is a SIGN test: classical yoga
# formation asks whether a planet is in its exaltation sign, not whether it is
# within some orb of the exact degree. Deep degrees grade strength, they do not
# form or break a yoga.
EXALTATION = {
    "Sun": "Aries", "Moon": "Taurus", "Mars": "Capricorn", "Mercury": "Virgo",
    "Jupiter": "Cancer", "Venus": "Pisces", "Saturn": "Libra",
}
EXALTATION_DEGREE = {
    "Sun": 10.0, "Moon": 3.0, "Mars": 28.0, "Mercury": 15.0,
    "Jupiter": 5.0, "Venus": 27.0, "Saturn": 20.0,
}
# Debilitation is the seventh sign from exaltation, always. Written out rather
# than derived so a misreading of one line cannot propagate to both tables.
DEBILITATION = {
    "Sun": "Libra", "Moon": "Scorpio", "Mars": "Cancer", "Mercury": "Pisces",
    "Jupiter": "Capricorn", "Venus": "Virgo", "Saturn": "Aries",
}

# Moolatrikona is degree-bound and therefore only meaningful in D1 — a varga
# sign has no degrees of its own. Ranges as given in BPHS ch. 3.
MOOLATRIKONA = {
    "Sun": ("Leo", 0.0, 20.0),
    "Moon": ("Taurus", 4.0, 30.0),
    "Mars": ("Aries", 0.0, 12.0),
    "Mercury": ("Virgo", 16.0, 20.0),
    "Jupiter": ("Sagittarius", 0.0, 10.0),
    "Venus": ("Libra", 0.0, 15.0),
    "Saturn": ("Aquarius", 0.0, 20.0),
}

# Own signs, inverted from chart_service's DOMICILE so the lookup runs the way
# the yoga rules read ("Mars in its own sign").
OWN_SIGNS = {
    planet: tuple(s for s in SIGNS if DOMICILE[s] == planet)
    for planet in GRAHAS
}

# -- Graha drishti ---------------------------------------------------------
# Vedic aspects are whole-sign and asymmetric. Every graha aspects the 7th from
# itself; Mars adds the 4th and 8th, Jupiter the 5th and 9th, Saturn the 3rd
# and 10th. Counts are inclusive, so 1 would be the planet's own sign and never
# appears here. Rahu and Ketu are given no aspect: the 5/7/9 attribution to
# them is a real tradition but a minority one, and including it would silently
# form yogas that most astrologers would not grant.
GRAHA_DRISHTI = {
    "Mars": (4, 7, 8),
    "Jupiter": (5, 7, 9),
    "Saturn": (3, 7, 10),
}
DEFAULT_DRISHTI = (7,)

# Natural benefics for the Kemadruma cancellation. Mercury is deliberately not
# in the set: its benefic status is conditional on the company it keeps, and a
# rule that turns on "Mercury unafflicted" needs a definition of afflicted that
# the sources do not share. The Moon's own benefic status by paksha is the same
# kind of problem and is likewise not used.
NATURAL_BENEFICS = ("Jupiter", "Venus")

# Classical combustion arcs (BPHS): Mercury within 14° of the Sun is combust,
# 12° when retrograde. Used only to annotate Budha-Aditya, never to form or
# break it — see BUDHA_ADITYA_REQUIRES_NO_COMBUSTION.
COMBUSTION_ARC = {"Mercury": 14.0, "Mercury_retrograde": 12.0}


# --------------------------------------------------------------------------
# Disputed rules, exposed so a lineage can swap them
# --------------------------------------------------------------------------

# Pancha Mahapurusha: BPHS and Phaladeepika both put the kendra requirement
# from the LAGNA. A minority reading allows a kendra from the Moon as well,
# which roughly doubles how often the yoga forms — set to "Moon" or "both" to
# adopt it.
MAHAPURUSHA_KENDRA_FROM = "Lagna"          # 'Lagna' | 'Moon' | 'both'

# Chandra-Mangala: BPHS states it as a conjunction. The extension to mutual
# aspect (in practice the 7th, since that is the only aspect Moon and Mars
# share both ways) is common in modern practice and absent from the verse.
CHANDRA_MANGALA_INCLUDES_MUTUAL_ASPECT = False

# Budha-Aditya: the combination is Sun with Mercury in one sign, and Mercury is
# combust in most instances of it because Mercury never strays 28° from the
# Sun. Many practitioners hold the yoga only delivers when Mercury is outside
# the combustion arc. That is a judgement about results, not about formation,
# so combustion is reported and not enforced.
BUDHA_ADITYA_REQUIRES_NO_COMBUSTION = False

# Dhana and Raja yogas: "association" is taken as conjunction in one sign,
# parivartana (exchange of signs), or MUTUAL aspect. A one-way special aspect —
# Saturn throwing its 3rd at a planet that does not throw anything back — is
# accepted as association by some writers and not by others. The strict reading
# is the default.
ASSOCIATION_INCLUDES_ONE_WAY_ASPECT = False

# Neecha Bhanga: cancelling a debilitation is one claim, and turning it into a
# Raja Yoga is a considerably larger one. A substantial tradition holds the
# raja yoga only follows when the debilitated planet itself sits in a kendra or
# a trikona from the Lagna. Cancellation is always reported; the raja yoga
# label is gated on that placement by default.
NEECHA_BHANGA_RAJA_NEEDS_KENDRA_TRIKONA = True

# Kemadruma: which bodies are ignored when looking for company around the Moon.
# The Sun is excluded by the classical rule itself (it is too often beside the
# Moon for its presence to mean anything); the nodes are excluded because they
# are shadows, which is the majority reading but not a unanimous one.
KEMADRUMA_IGNORED = ("Sun", "Rahu", "Ketu")
# Whether a planet sharing the Moon's own sign also breaks the isolation. The
# usual statement is "nothing in the 2nd, nothing in the 12th, and nothing with
# the Moon", so the conjunction case is included.
KEMADRUMA_INCLUDES_CONJUNCTION = True
# Cancellations to apply, in the order they are tested. Every one of these is
# widely printed; sources differ over which are sufficient on their own, and
# 'moon_dignified' is the weakest supported of the four. Drop a key to disable
# it for a lineage that does not accept it.
KEMADRUMA_CANCELLATIONS = (
    "moon_in_kendra",
    "planet_in_kendra_from_moon",
    "benefic_with_moon",
    "moon_dignified",
)

# Which divisions are computed by default, and which one defines Vargottama.
DEFAULT_DIVISIONS = ("D1", "D3", "D7", "D9", "D10", "D12")
# Vargottama in its classical sense is same sign in D1 and D9. The word is also
# used loosely for "same sign in D1 and any varga"; that reading is reported
# separately under 'repeats' rather than being called Vargottama.
VARGOTTAMA_DIVISION = "D9"


# Rules considered and deliberately not implemented, with the reason. Kept as
# data so the module can be asked what it does not know.
NOT_IMPLEMENTED = (
    ("Rahu/Ketu exaltation and debilitation",
     "Three incompatible traditions (Taurus/Scorpio, Gemini/Sagittarius, "
     "Virgo/Pisces). No dignity is assigned to the nodes anywhere here."),
    ("Rahu/Ketu graha drishti",
     "The 5/7/9 attribution is a real but minority doctrine; including it "
     "would form Raja and Dhana yogas most astrologers would not grant."),
    ("Vimsopaka Bala",
     "Needs the Shadvarga or larger sets (D2, D30, D16, D20, D24, D27, D40, "
     "D45, D60). Computing it over the six divisions here would produce an "
     "authoritative-looking number that is not the classical one."),
    ("Ashtakavarga",
     "A separate system with its own bindu tables; not attempted."),
    ("Neecha Bhanga by retrogression",
     "The claim that a retrograde debilitated planet is thereby cancelled is "
     "contested at the level of principle, not detail."),
    ("Neecha Bhanga by mutual kendras of the dispositor and exaltation lord",
     "Printed in some sources and absent from others; left out."),
    ("Kendradhipati dosha",
     "The rule that natural benefics owning kendras lose their benefic power "
     "interacts with Raja Yoga judgement and is stated differently by every "
     "text that carries it."),
    ("Vipareeta Raja Yoga, Sunapha/Anapha/Durudhara, Amala, Sakata, and the "
     "remaining named yogas",
     "Not attempted here rather than attempted approximately."),
    ("Divisional charts D2, D4, D6, D8, D16, D20, D24, D27, D30, D40, D45, D60",
     "Only D1, D3, D7, D9, D10 and D12 are computed. D2 Hora and D30 "
     "Trimsamsa in particular have competing schemes."),
    ("Bhava madhya (cusp-based) houses",
     "Every house count here is whole-sign, which is what the yoga rules "
     "assume. A cusp-based reading would give different house lords."),
)


class VargaError(ValueError):
    """Raised when a chart cannot support a varga or yoga reading."""


# --------------------------------------------------------------------------
# The division rules
# --------------------------------------------------------------------------
#
# Each rule answers one question: given the rashi a longitude falls in and
# which part of that rashi it falls in, which sign is the varga sign? They are
# written one per division, in the words of the verse, because the differences
# between them are the whole point and a single clever formula would hide them.
#
# Sign indices are 0-based (Aries = 0) inside these functions; "the 9th from X"
# is an inclusive count, so it adds 8.

def _rule_d1(sign: int, part: int) -> int:
    """D1 Rashi — the sign itself. Present so D1 can go through the same path."""
    return sign


def _rule_d3(sign: int, part: int) -> int:
    """D3 Drekkana — 1st third the sign itself, 2nd the 5th from it, 3rd the 9th.

    The three drekkanas of any sign are its own trine, which is why this rule
    jumps in fours instead of running consecutively like the others.
    """
    return sign + 4 * part


def _rule_d7(sign: int, part: int) -> int:
    """D7 Saptamsa — odd signs count from themselves, even signs from the 7th."""
    odd = sign % 2 == 0                      # Aries is index 0 and is the 1st sign
    return (sign if odd else sign + 6) + part


def _rule_d9(sign: int, part: int) -> int:
    """D9 Navamsa — movable from itself, fixed from the 9th, dual from the 5th.

    This is the rule the whole module turns on. Written as the three modality
    cases the verse gives; _check_divisions() asserts at import that it agrees
    with the continuous 3°20′ walk from 0° Aries, which is the other way the
    same rule is usually stated.
    """
    modality = MODALITY[SIGNS[sign % 12]]
    start = sign + {"Cardinal": 0, "Fixed": 8, "Mutable": 4}[modality]
    return start + part


def _rule_d10(sign: int, part: int) -> int:
    """D10 Dasamsa — odd signs count from themselves, even signs from the 9th.

    Note this does NOT reduce to a continuous walk of 3° arcs from Aries, which
    is a common implementation error: the even-sign start is the 9th, not the
    11th that a continuous walk would land on.
    """
    odd = sign % 2 == 0
    return (sign if odd else sign + 8) + part


def _rule_d12(sign: int, part: int) -> int:
    """D12 Dwadasamsa — always counted from the sign itself, for every sign."""
    return sign + part


# Public description of each division. The rule functions are held separately
# so this table stays JSON-serialisable.
DIVISIONS: dict[str, dict] = {
    "D1": {
        "key": "D1", "name": "Rashi", "parts": 1, "arc": 30.0,
        "signifies": "the body, the life and the chart as a whole",
        "rule": "The sign itself.",
    },
    "D3": {
        "key": "D3", "name": "Drekkana", "parts": 3, "arc": 10.0,
        "signifies": "siblings, courage and the capacity to begin things",
        "rule": "First third the sign itself, second the 5th from it, third the 9th.",
    },
    "D7": {
        "key": "D7", "name": "Saptamsa", "parts": 7, "arc": 30.0 / 7.0,
        "signifies": "children and progeny",
        "rule": "Odd signs counted from themselves, even signs from the 7th.",
    },
    "D9": {
        "key": "D9", "name": "Navamsa", "parts": 9, "arc": 30.0 / 9.0,
        "signifies": "marriage and the spouse, and the underlying strength of "
                     "every planet in the chart",
        "rule": "Movable signs counted from themselves, fixed signs from the 9th, "
                "dual signs from the 5th.",
    },
    "D10": {
        "key": "D10", "name": "Dasamsa", "parts": 10, "arc": 3.0,
        "signifies": "career, standing and action in the world",
        "rule": "Odd signs counted from themselves, even signs from the 9th.",
    },
    "D12": {
        "key": "D12", "name": "Dwadasamsa", "parts": 12, "arc": 2.5,
        "signifies": "parents and ancestry",
        "rule": "Always counted from the sign itself.",
    },
}

_DIVISION_RULES = {
    "D1": _rule_d1, "D3": _rule_d3, "D7": _rule_d7,
    "D9": _rule_d9, "D10": _rule_d10, "D12": _rule_d12,
}


def _check_divisions() -> None:
    """Guard the division rules against the ways they can silently rot.

    Four properties, each of which a mis-typed offset would break:

      * the parts of one sign land in that many *distinct* signs,
      * a full 360° sweep gives every sign equal weight,
      * D9 agrees with the continuous 3°20′ walk from 0° Aries — the same rule
        stated the other way round, and the check that actually pins Navamsa,
      * the three navamsas the tradition names vargottama really are.
    """
    for key, meta in DIVISIONS.items():
        rule, parts = _DIVISION_RULES[key], meta["parts"]
        for sign in range(12):
            landed = {rule(sign, p) % 12 for p in range(parts)}
            if len(landed) != parts:
                raise AssertionError(
                    f"{key} maps the {parts} parts of {SIGNS[sign]} onto "
                    f"{len(landed)} signs")
        coverage = [0] * 12
        for sign in range(12):
            for p in range(parts):
                coverage[rule(sign, p) % 12] += 1
        if len(set(coverage)) != 1:
            raise AssertionError(f"{key} does not cover the zodiac evenly: {coverage}")

    # D9 and D7 are the two divisions that reduce to a continuous walk; D3, D10
    # and D12 provably do not, which is why they are written out.
    for key, arc in (("D9", 30.0 / 9.0), ("D7", 30.0 / 7.0)):
        rule, parts = _DIVISION_RULES[key], DIVISIONS[key]["parts"]
        for sign in range(12):
            for p in range(parts):
                walked = (sign * parts + p) % 12
                if rule(sign, p) % 12 != walked:
                    raise AssertionError(
                        f"{key} disagrees with the continuous {arc:.4f}° walk at "
                        f"{SIGNS[sign]} part {p + 1}")

    # BPHS names the 1st navamsa of a movable sign, the 5th of a fixed sign and
    # the 9th of a dual sign as vargottama. That is a consequence of the rule,
    # not an extra rule, so it is a free consistency check on the rule.
    for sign in range(12):
        part = {"Cardinal": 0, "Fixed": 4, "Mutable": 8}[MODALITY[SIGNS[sign]]]
        if _rule_d9(sign, part) % 12 != sign:
            raise AssertionError(
                f"the vargottama navamsa of {SIGNS[sign]} is not {SIGNS[sign]}")

    if set(GRAHAS) != set(CLASSICAL):
        raise AssertionError("GRAHAS has drifted from chart_service.CLASSICAL")


_check_divisions()


# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------

def _ordinal(n: int) -> str:
    """1 -> '1st'. These land in text a reader sees, so 1th/2th will not do."""
    if 11 <= n % 100 <= 13:
        return f"{n}th"
    suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def _sign_distance(from_sign: str, to_sign: str) -> int:
    """Inclusive count from one rashi to another, 1..12 — whole-sign counting."""
    return (SIGNS.index(to_sign) - SIGNS.index(from_sign)) % 12 + 1


def varga_sign(longitude: float, division: str = "D9") -> str:
    """The varga sign a sidereal longitude falls in, for one division.

    Pure arithmetic on a longitude — no chart needed, which is what makes the
    worked examples in the tests possible.
    """
    if division not in DIVISIONS:
        raise VargaError(
            f"Unknown division {division!r}; this module computes "
            f"{', '.join(DIVISIONS)}.")
    lon = float(longitude) % 360.0
    sign = int(lon // 30.0) % 12
    parts = DIVISIONS[division]["parts"]
    # Clamped because 29.999999999 / (30/9) can round up on the boundary and
    # push the part index one past the end of the sign.
    part = min(int((lon % 30.0) / (30.0 / parts)), parts - 1)
    return SIGNS[_DIVISION_RULES[division](sign, part) % 12]


def navamsa_sign(longitude: float) -> str:
    """The D9 Navamsa sign of a sidereal longitude — the one every reading wants."""
    return varga_sign(longitude, "D9")


def varga_part(longitude: float, division: str = "D9") -> int:
    """Which part of its rashi a longitude falls in, 1-based (1..parts)."""
    if division not in DIVISIONS:
        raise VargaError(f"Unknown division {division!r}.")
    parts = DIVISIONS[division]["parts"]
    lon = float(longitude) % 360.0
    return min(int((lon % 30.0) / (30.0 / parts)), parts - 1) + 1


def _bundle(chart: object) -> dict:
    """Accept either a `chart_service.ChartSession` or the bundle dict it holds."""
    bundle = getattr(chart, "bundle", chart)
    if not isinstance(bundle, dict) or "objects" not in bundle:
        raise VargaError(
            "Expected a chart_service chart session or its bundle dict.")
    return bundle


def _object(bundle: dict, name: str) -> dict:
    obj = bundle["objects"].get(name)
    if obj is None:
        raise VargaError(f"Chart is missing {name}; cannot read vargas from it.")
    return obj


def _require_sidereal(bundle: dict) -> None:
    """Vargas and yogas are sidereal rules, and refuse to run on anything else.

    A tropical chart's longitudes are roughly 24° adrift, which is most of a
    sign — enough to move nearly every planet's rashi, every varga sign derived
    from it, and every dignity test built on those signs. Refuse rather than
    convert silently, because the ayanamsa is the caller's choice to make.
    """
    if bundle.get("meta", {}).get("zodiac") != "sidereal":
        raise VargaError(
            "Vargas and yogas need a sidereal chart — rebuild it with "
            "zodiac='sidereal' (Lahiri) before reading divisional charts.")


def _view(chart: object) -> dict:
    """Everything the rules below read out of a chart, resolved once.

    Whole-sign houses from the Lagna, the twelve house lords, and the sidereal
    longitude of every body that takes part. Rahu and Ketu are carried when the
    bundle has a node, purely so they appear in the varga tables.
    """
    bundle = _bundle(chart)
    _require_sidereal(bundle)

    longitudes: dict[str, float] = {}
    retrograde: dict[str, bool] = {}
    for graha in GRAHAS:
        obj = _object(bundle, graha)
        longitudes[graha] = float(obj["longitude"]) % 360.0
        retrograde[graha] = bool(obj.get("retrograde", False))

    asc = _object(bundle, "ASC")
    longitudes["Lagna"] = float(asc["longitude"]) % 360.0

    node = next((bundle["objects"][n] for n in NODE_NAMES if n in bundle["objects"]), None)
    if node is not None:
        longitudes["Rahu"] = float(node["longitude"]) % 360.0
        longitudes["Ketu"] = (longitudes["Rahu"] + 180.0) % 360.0

    signs = {name: SIGNS[int(lon // 30.0) % 12] for name, lon in longitudes.items()}
    lagna_sign = signs["Lagna"]
    house_signs = [SIGNS[(SIGNS.index(lagna_sign) + i) % 12] for i in range(12)]

    return {
        "meta": bundle.get("meta", {}),
        "bodies": tuple(longitudes),                 # Lagna first, then grahas, then nodes
        "longitudes": longitudes,
        "retrograde": retrograde,
        "signs": signs,
        "degrees": {n: lon % 30.0 for n, lon in longitudes.items()},
        "lagna_sign": lagna_sign,
        "house_signs": house_signs,
        "houses": {n: _sign_distance(lagna_sign, s) for n, s in signs.items()},
        "house_lords": {i + 1: DOMICILE[s] for i, s in enumerate(house_signs)},
    }


def _aspects(view: dict, source: str, target: str) -> bool:
    """Does `source` cast graha drishti on `target`? Whole-sign, one-directional."""
    if source not in GRAHAS or target not in view["signs"]:
        return False
    distance = _sign_distance(view["signs"][source], view["signs"][target])
    return distance in GRAHA_DRISHTI.get(source, DEFAULT_DRISHTI)


def _conjunct(view: dict, a: str, b: str) -> bool:
    """Same rashi. Vedic conjunction is sign-based, not orb-based."""
    return a != b and view["signs"][a] == view["signs"][b]


def _exchange(view: dict, a: str, b: str) -> bool:
    """Parivartana — each planet sits in a sign the other owns."""
    if a == b or a not in GRAHAS or b not in GRAHAS:
        return False
    return DOMICILE[view["signs"][a]] == b and DOMICILE[view["signs"][b]] == a


def _association(view: dict, a: str, b: str) -> str:
    """How two planets are related, as the Dhana and Raja rules mean it.

    Returns "" when they are not associated. Conjunction, exchange and mutual
    aspect are the three the tradition names; one-way special aspects are
    excluded unless ASSOCIATION_INCLUDES_ONE_WAY_ASPECT says otherwise.
    """
    if a == b:
        return ""
    if _conjunct(view, a, b):
        return "conjunction"
    if _exchange(view, a, b):
        return "exchange"
    there, back = _aspects(view, a, b), _aspects(view, b, a)
    if there and back:
        return "mutual aspect"
    if (there or back) and ASSOCIATION_INCLUDES_ONE_WAY_ASPECT:
        return "one-way aspect"
    return ""


def _dignity(view: dict, planet: str) -> str:
    """The strongest essential dignity a graha holds in D1, or "".

    Ordered exaltation > moolatrikona > own sign, which is the order the
    tradition ranks them in. Debilitation is reported separately by
    _is_debilitated() because it is not a weaker dignity, it is the opposite.
    """
    sign = view["signs"][planet]
    if EXALTATION.get(planet) == sign:
        return "exaltation"
    mt_sign, low, high = MOOLATRIKONA[planet]
    if sign == mt_sign and low <= view["degrees"][planet] < high:
        return "moolatrikona"
    if sign in OWN_SIGNS[planet]:
        return "own sign"
    return ""


def _is_debilitated(view: dict, planet: str) -> bool:
    return DEBILITATION.get(planet) == view["signs"][planet]


def _position(view: dict, name: str) -> str:
    return f"{view['signs'][name]} {dms(view['degrees'][name])}"


def chart_view(chart: object) -> dict:
    """Public access to the resolved chart view other astro/ modules can reuse.

    Whole-sign houses, house lords, signs and degrees for the Lagna and every
    graha — the same dict every rule in this module reads from. Exposed so a
    sibling module (delineation.py) does not have to re-derive whole-sign
    houses from a bundle a second time; it is the canonical reading of a
    sidereal chart and there should only be one copy of that logic.
    """
    return _view(chart)


# --------------------------------------------------------------------------
# Divisional charts
# --------------------------------------------------------------------------

def divisional_chart(chart: object, division: str = "D9") -> dict:
    """One divisional chart: every body's varga sign and house, and the varga Lagna.

    Houses inside a varga are whole-sign counted from the varga Lagna, which is
    how a varga is read — the rashi chart's houses have no authority here.
    """
    if division not in DIVISIONS:
        raise VargaError(
            f"Unknown division {division!r}; this module computes "
            f"{', '.join(DIVISIONS)}.")
    view = _view(chart)
    meta = DIVISIONS[division]

    varga_signs = {
        name: varga_sign(lon, division) for name, lon in view["longitudes"].items()
    }
    lagna = varga_signs["Lagna"]
    house_signs = [SIGNS[(SIGNS.index(lagna) + i) % 12] for i in range(12)]

    positions: dict[str, dict] = {}
    for name in view["bodies"]:
        v_sign = varga_signs[name]
        positions[name] = {
            "name": name,
            "sign": v_sign,
            "house": _sign_distance(lagna, v_sign),
            "sign_lord": DOMICILE[v_sign],
            "rashi_sign": view["signs"][name],
            "rashi_position": _position(view, name),
            "part": varga_part(view["longitudes"][name], division),
            # Same sign in D1 and here. In D9 this is Vargottama proper; in the
            # other divisions it is only a repeat, and vargottama() says so.
            "same_as_rashi": v_sign == view["signs"][name],
        }

    houses = [
        {
            "house": i + 1,
            "sign": sign,
            "lord": DOMICILE[sign],
            "occupants": [n for n in view["bodies"]
                          if n != "Lagna" and varga_signs[n] == sign],
        }
        for i, sign in enumerate(house_signs)
    ]

    return {
        "division": division,
        "name": meta["name"],
        "parts": meta["parts"],
        "part_arc": round(meta["arc"], 6),
        "signifies": meta["signifies"],
        "rule": meta["rule"],
        "lagna": {
            "sign": lagna,
            "lord": DOMICILE[lagna],
            "rashi_lagna": view["lagna_sign"],
        },
        "house_signs": house_signs,
        "houses": houses,
        "positions": positions,
    }


def divisional_charts(chart: object, divisions: tuple[str, ...] = DEFAULT_DIVISIONS) -> dict:
    """Several divisional charts at once, keyed by division."""
    return {d: divisional_chart(chart, d) for d in divisions}


def vargottama(chart: object) -> dict:
    """Planets holding the same sign in D1 and D9 — the classical strength marker.

    A vargottama planet is read as acting with full force whatever else the
    chart does to it, on the reasoning that the rashi and the navamsa, the two
    charts every reading rests on, agree about it. The looser use of the word
    for a repeat in any other division is reported under 'repeats' and is not
    called Vargottama here.
    """
    view = _view(chart)
    d9 = {n: varga_sign(lon, VARGOTTAMA_DIVISION)
          for n, lon in view["longitudes"].items()}

    planets: list[str] = []
    detail: dict[str, dict] = {}
    for name in view["bodies"]:
        same = d9[name] == view["signs"][name]
        if same:
            planets.append(name)
        detail[name] = {
            "rashi_sign": view["signs"][name],
            "navamsa_sign": d9[name],
            "vargottama": same,
        }

    repeats: dict[str, list[str]] = {}
    for division in DEFAULT_DIVISIONS:
        if division in ("D1", VARGOTTAMA_DIVISION):
            continue
        hits = [n for n in view["bodies"]
                if varga_sign(view["longitudes"][n], division) == view["signs"][n]]
        if hits:
            repeats[division] = hits

    if planets:
        listed = ", ".join(planets)
        note = (f"{listed} hold the same sign in the rashi and in the navamsa. "
                f"The tradition reads a vargottama planet as acting at full "
                f"strength regardless of the rest of its condition.")
    else:
        note = ("No planet repeats its rashi sign in the navamsa in this chart. "
                "That is the common case and is not a weakness in itself.")

    return {
        "division": VARGOTTAMA_DIVISION,
        "planets": planets,
        "detail": detail,
        "repeats_in_other_divisions": repeats,
        "note": note,
    }


def varga_strength(chart: object, divisions: tuple[str, ...] = DEFAULT_DIVISIONS) -> dict:
    """How many of the computed divisions each graha occupies with dignity.

    A plain count, and nothing more. **This is not Vimsopaka Bala** — that needs
    the Shadvarga or Shodasavarga sets with their own weights, and two of the
    six divisions it requires are not computed here. It is not Shadbala either.
    It is the honest thing the available divisions support: in how many of them
    does this planet sit in its own or its exaltation sign, and in how many does
    it sit in its debilitation sign.

    Dignity inside a varga is judged at sign level only. Moolatrikona is degree
    bound and a varga sign carries no degrees, so it counts in D1 alone.
    """
    view = _view(chart)
    out: dict[str, dict] = {}

    for graha in GRAHAS:
        rows = []
        strong = weak = 0
        for division in divisions:
            v_sign = varga_sign(view["longitudes"][graha], division)
            if EXALTATION[graha] == v_sign:
                state = "exalted"
            elif division == "D1" and _dignity(view, graha) == "moolatrikona":
                state = "moolatrikona"
            elif v_sign in OWN_SIGNS[graha]:
                state = "own sign"
            elif DEBILITATION[graha] == v_sign:
                state = "debilitated"
            else:
                state = "neutral"
            strong += state in ("exalted", "moolatrikona", "own sign")
            weak += state == "debilitated"
            rows.append({"division": division, "sign": v_sign, "state": state})

        vargottama_here = (
            varga_sign(view["longitudes"][graha], VARGOTTAMA_DIVISION)
            == view["signs"][graha]
        )
        out[graha] = {
            "planet": graha,
            "rashi_sign": view["signs"][graha],
            "rashi_dignity": _dignity(view, graha) or (
                "debilitation" if _is_debilitated(view, graha) else "none"),
            "divisions": rows,
            "dignified_count": strong,
            "debilitated_count": weak,
            "counted_divisions": len(divisions),
            "vargottama": vargottama_here,
        }

    return {
        "divisions": list(divisions),
        "planets": out,
        "method_note": (
            "A count of dignified placements across the divisions this module "
            "computes. It is not Vimsopaka Bala and not Shadbala, both of which "
            "need divisions and weights that are not implemented here."
        ),
    }


# --------------------------------------------------------------------------
# Yogas
# --------------------------------------------------------------------------

def _yoga(key: str, name: str, group: str, planets: list[str], condition: str,
          note: str, source: str, strength: str | None = None, **extra: object) -> dict:
    return {
        "key": key, "name": name, "group": group, "planets": planets,
        "condition": condition, "note": note, "source": source,
        "strength": strength, **extra,
    }


# -- Pancha Mahapurusha ----------------------------------------------------

# The five, with the planet each belongs to. The dignity requirement is own
# sign or exaltation sign; the placement requirement is a kendra. Both, always.
MAHAPURUSHA = {
    "Mars": ("ruchaka", "Ruchaka Yoga",
             "a commanding, physically forceful cast of character — the soldier's yoga"),
    "Mercury": ("bhadra", "Bhadra Yoga",
                "quickness of mind, learning and skill with words and numbers"),
    "Jupiter": ("hamsa", "Hamsa Yoga",
                "moral weight, teaching and the respect that follows from it"),
    "Venus": ("malavya", "Malavya Yoga",
              "beauty, comfort, artistic sense and a settled domestic life"),
    "Saturn": ("sasa", "Sasa Yoga",
               "endurance, authority over others and the patience to hold a position"),
}


def pancha_mahapurusha(chart: object) -> list[dict]:
    """The five Mahapurusha yogas — Ruchaka, Bhadra, Hamsa, Malavya, Sasa.

    Both conditions are required and neither substitutes for the other: the
    planet must be in its own or its exaltation sign, AND in a kendra (1, 4, 7,
    10) from the Lagna. An exalted Saturn in the 6th forms nothing, and Saturn
    in the 10th in a sign it does not own forms nothing either.

    Source: Brihat Parashara Hora Shastra and Phaladeepika, which agree on both
    limbs. Saravali carries the same five.
    """
    view = _view(chart)
    formed: list[dict] = []

    for planet, (key, name, meaning) in MAHAPURUSHA.items():
        sign = view["signs"][planet]
        exalted = EXALTATION[planet] == sign
        own = sign in OWN_SIGNS[planet]
        if not (exalted or own):
            continue

        houses = []
        if MAHAPURUSHA_KENDRA_FROM in ("Lagna", "both"):
            houses.append(("the Lagna", view["houses"][planet]))
        if MAHAPURUSHA_KENDRA_FROM in ("Moon", "both"):
            houses.append(("the Moon", _sign_distance(view["signs"]["Moon"], sign)))
        kendra = [(ref, h) for ref, h in houses if h in KENDRAS]
        if not kendra:
            continue

        ref, house = kendra[0]
        dignity = "exaltation" if exalted else (
            "moolatrikona" if _dignity(view, planet) == "moolatrikona" else "own sign")
        formed.append(_yoga(
            key, name, "Pancha Mahapurusha", [planet],
            condition=(f"{planet} in {sign}, its {dignity} sign, and in the "
                       f"{_ordinal(house)} — a kendra from {ref}."),
            note=(f"{name} is the {planet} Mahapurusha yoga: {meaning}. It needs "
                  f"both limbs, dignity and a kendra, and this chart has both."),
            source="BPHS and Phaladeepika; the same five appear in Saravali.",
            # Exaltation outranks own sign in every listing of the five; there
            # is no numeric strength in the tradition, so the dignity is
            # reported as the strength and nothing is invented on top of it.
            strength=dignity,
            house=house, sign=sign, kendra_from=ref,
        ))

    return formed


# -- Gaja Kesari -----------------------------------------------------------

def gaja_kesari(chart: object) -> list[dict]:
    """Jupiter in a kendra from the Moon.

    The condition is exactly that — 1st, 4th, 7th or 10th counted by sign from
    the Moon, Jupiter with the Moon included. Source: BPHS; also Phaladeepika.

    The literature adds riders that are not applied as formation conditions
    because they are stated inconsistently: that Jupiter should not be combust,
    debilitated or in an enemy sign, and that the yoga wants benefic support.
    Jupiter's own condition is reported alongside so a reading can weigh it,
    which is what an astrologer would do rather than declaring the yoga absent.
    """
    view = _view(chart)
    distance = _sign_distance(view["signs"]["Moon"], view["signs"]["Jupiter"])
    if distance not in KENDRAS:
        return []

    debilitated = _is_debilitated(view, "Jupiter")
    dignity = _dignity(view, "Jupiter")
    caveats = []
    if debilitated:
        caveats.append("Jupiter is debilitated in Capricorn, which several sources "
                       "hold weakens the yoga to nothing")
    separation = angular_sep(view["longitudes"]["Jupiter"], view["longitudes"]["Sun"])
    if separation < 11.0:
        caveats.append(f"Jupiter is within {separation:.1f}° of the Sun and so combust")

    note = ("Jupiter stands in a kendra from the Moon — the classical picture of "
            "the elephant and the lion. Read as reputation, the respect of others "
            "and help arriving from people with standing.")
    if caveats:
        note += " " + ("Worth qualifying: " + "; ".join(caveats) + ".")

    return [_yoga(
        "gaja_kesari", "Gaja Kesari Yoga", "Chandra yoga", ["Jupiter", "Moon"],
        condition=(f"Jupiter in {view['signs']['Jupiter']}, the {_ordinal(distance)} "
                   f"from the Moon in {view['signs']['Moon']} — a kendra."),
        note=note,
        source="BPHS; also given in Phaladeepika.",
        strength=None,
        distance_from_moon=distance,
        jupiter_dignity=dignity or ("debilitation" if debilitated else "none"),
        caveats=caveats,
    )]


# -- Neecha Bhanga ---------------------------------------------------------

def neecha_bhanga(chart: object) -> list[dict]:
    """Cancellation of debilitation, and when it rises to a Raja Yoga.

    The mainstream cancellation conditions, any one of which suffices:

      1. The lord of the sign of debilitation is in a kendra from the Lagna or
         from the Moon.
      2. The planet that is exalted in that same sign is in a kendra from the
         Lagna or from the Moon.
      3. The debilitated planet is conjunct or aspected by the lord of its
         debilitation sign.
      4. The debilitated planet is conjunct or aspected by the planet exalted
         in that sign.
      5. The debilitated planet is exalted in the Navamsa.

    Source: BPHS, and the same set as carried by Phaladeepika and Jataka
    Parijata. Note that condition 2 and 4 are simply unavailable when the Moon
    is debilitated: Scorpio is nobody's exaltation sign, so there is no planet
    to test. That is reported rather than skipped silently.

    Two further conditions circulate and are deliberately NOT applied — see
    NOT_IMPLEMENTED: cancellation by the debilitated planet being retrograde,
    and cancellation by the dispositor and the exaltation lord standing in
    mutual kendras. Both are contested at the level of principle.

    Cancellation and Raja Yoga are reported as two separate claims. The larger
    claim — that the cancellation produces a Raja Yoga — is gated on the
    debilitated planet itself occupying a kendra or a trikona, which is the
    reading a substantial part of the tradition insists on. See
    NEECHA_BHANGA_RAJA_NEEDS_KENDRA_TRIKONA.
    """
    view = _view(chart)
    moon_sign = view["signs"]["Moon"]
    formed: list[dict] = []

    for planet in GRAHAS:
        if not _is_debilitated(view, planet):
            continue
        deb_sign = DEBILITATION[planet]
        dispositor = DOMICILE[deb_sign]
        # The planet exalted in the sign of debilitation, if there is one.
        exalt_lord = next((p for p in GRAHAS if EXALTATION[p] == deb_sign), None)

        def in_kendra(other: str) -> str:
            """Kendra from the Lagna or from the Moon, named for the reader."""
            if view["houses"][other] in KENDRAS:
                return f"a kendra from the Lagna (the {_ordinal(view['houses'][other])})"
            distance = _sign_distance(moon_sign, view["signs"][other])
            if distance in KENDRAS:
                return f"a kendra from the Moon (the {_ordinal(distance)})"
            return ""

        reasons: list[str] = []

        where = in_kendra(dispositor)
        if where:
            reasons.append(f"{dispositor}, lord of {deb_sign}, stands in {where}")

        if exalt_lord is not None:
            where = in_kendra(exalt_lord)
            if where:
                reasons.append(
                    f"{exalt_lord}, which is exalted in {deb_sign}, stands in {where}")

        if _conjunct(view, planet, dispositor):
            reasons.append(f"{planet} is conjunct its dispositor {dispositor}")
        elif _aspects(view, dispositor, planet):
            reasons.append(f"{dispositor}, lord of {deb_sign}, aspects {planet}")

        if exalt_lord is not None and exalt_lord != planet:
            if _conjunct(view, planet, exalt_lord):
                reasons.append(f"{planet} is conjunct {exalt_lord}, the planet "
                               f"exalted in {deb_sign}")
            elif _aspects(view, exalt_lord, planet):
                reasons.append(f"{exalt_lord}, exalted in {deb_sign}, aspects {planet}")

        navamsa = varga_sign(view["longitudes"][planet], "D9")
        if EXALTATION[planet] == navamsa:
            reasons.append(f"{planet} is exalted in the navamsa, in {navamsa}")

        house = view["houses"][planet]
        angular = house in KENDRAS or house in TRIKONAS
        cancelled = bool(reasons)
        raja = cancelled and (angular or not NEECHA_BHANGA_RAJA_NEEDS_KENDRA_TRIKONA)

        if cancelled and raja:
            note = (f"{planet} is debilitated in {deb_sign}, but the debilitation is "
                    f"cancelled, and {planet} also holds the {_ordinal(house)} — a "
                    f"{'kendra' if house in KENDRAS else 'trikona'}. The tradition "
                    f"reads this as a planet that starts low and ends high, which is "
                    f"why the cancellation is given the name Raja Yoga.")
        elif cancelled:
            note = (f"{planet} is debilitated in {deb_sign} and the debilitation is "
                    f"cancelled, so the planet is not the liability the placement "
                    f"looks like. It is reported as a cancellation and not as a Raja "
                    f"Yoga, because {planet} sits in the {_ordinal(house)}, neither a "
                    f"kendra nor a trikona.")
        else:
            note = (f"{planet} is debilitated in {deb_sign} and none of the classical "
                    f"cancellation conditions applies. Read as a genuine weakness in "
                    f"whatever {planet} signifies for this chart.")

        formed.append(_yoga(
            "neecha_bhanga_raja" if raja else
            ("neecha_bhanga" if cancelled else "neecha"),
            "Neecha Bhanga Raja Yoga" if raja else
            ("Neecha Bhanga" if cancelled else "Uncancelled debilitation"),
            "Neecha Bhanga", [planet],
            condition=(f"{planet} debilitated in {deb_sign} in the "
                       f"{_ordinal(house)}."),
            note=note,
            source="BPHS; the same conditions in Phaladeepika and Jataka Parijata.",
            # More independent cancellations is the only thing the tradition
            # offers as a gradation, and even that is a practitioners' reading.
            strength=(f"{len(reasons)} cancellation condition"
                      f"{'s' if len(reasons) != 1 else ''} met") if cancelled else None,
            debilitation_sign=deb_sign,
            dispositor=dispositor,
            exaltation_lord=exalt_lord,
            exaltation_lord_available=exalt_lord is not None,
            navamsa_sign=navamsa,
            house=house,
            cancelled=cancelled,
            raja_yoga=raja,
            cancellations=reasons,
            formed=cancelled,
        ))

    return formed


# -- Dhana and Raja yogas --------------------------------------------------

def _lord_pairs(view: dict, houses_a: tuple[int, ...],
                houses_b: tuple[int, ...]) -> list[dict]:
    """Associated pairs of house lords, deduplicated by the pair of planets.

    A planet often lords two houses, so the same pair of planets can arrive
    from several house pairs; they are collapsed into one yoga carrying every
    house pair that produced it, rather than reported as several yogas.
    """
    found: dict[frozenset, dict] = {}
    for ha in houses_a:
        for hb in houses_b:
            if ha == hb:
                continue
            a, b = view["house_lords"][ha], view["house_lords"][hb]
            if a == b:
                continue                      # one planet cannot associate with itself
            how = _association(view, a, b)
            if not how:
                continue
            key = frozenset((a, b))
            entry = found.setdefault(key, {
                "planets": sorted((a, b)), "how": how, "house_pairs": []})
            entry["house_pairs"].append([ha, hb])
    return list(found.values())


def _shared_lords(view: dict, houses: tuple[int, ...]) -> list[dict]:
    """Planets owning more than one of a set of houses.

    Reported, not counted as a yoga. It is often said that a single lord over
    two of the wealth houses is a Dhana yoga in itself, but that is a different
    claim from "two lords in mutual association", which is the rule asked for.
    """
    by_planet: dict[str, list[int]] = {}
    for h in houses:
        by_planet.setdefault(view["house_lords"][h], []).append(h)
    return [{"planet": p, "houses": hs} for p, hs in by_planet.items() if len(hs) > 1]


def _lordship(view: dict, planet: str, houses: list[int],
              labels: dict[int, str] | None = None) -> str:
    """"Mercury (lord of the 9th)" — which houses *this* planet actually owns.

    `_lord_pairs` sorts the planet pair alphabetically, which breaks any
    positional correspondence with the house pair that produced it. A condition
    reading "Mercury and Moon — a lord of the 10th with a lord of the 9th"
    therefore invited exactly the wrong pairing: here Moon owns the 10th and
    Mercury the 9th, but the sentence implies the reverse. Bind each planet to
    its own houses instead of relying on the order of two lists.
    """
    owned = sorted({h for h in houses if view["house_lords"][h] == planet})
    if not owned:
        return planet
    parts = []
    for h in owned:
        label = (labels or {}).get(h)
        parts.append(f"{_ordinal(h)}{f' (a {label})' if label else ''}")
    return f"{planet}, lord of the {' and the '.join(parts)}"


def dhana_yogas(chart: object) -> list[dict]:
    """Lords of the 2nd, 5th, 9th and 11th in mutual association.

    The 2nd is accumulated wealth, the 11th is income and gain, and the 5th and
    9th are the trines of merit and fortune that the tradition holds wealth
    actually rests on. Two of those lords conjunct, exchanging signs, or in
    mutual aspect is a Dhana yoga.

    Source: BPHS, the Dhana Yoga chapter. The single-planet case — one graha
    owning two of the four houses — is reported separately under
    _shared_lords() rather than counted, because it is a different claim.
    """
    view = _view(chart)
    out = []
    for pair in _lord_pairs(view, DHANA_HOUSES, DHANA_HOUSES):
        a, b = pair["planets"]
        houses = sorted({h for hp in pair["house_pairs"] for h in hp})
        listed = " and ".join(_ordinal(h) for h in houses)
        out.append(_yoga(
            "dhana", "Dhana Yoga", "Dhana", [a, b],
            condition=(f"{_lordship(view, a, houses)}, and "
                       f"{_lordship(view, b, houses)}, joined by "
                       f"{pair['how']}."),
            note=(f"A wealth yoga: the lords of the {listed} are linked by "
                  f"{pair['how']}. The tradition reads the houses of earning and "
                  f"the houses of merit as working together rather than "
                  f"separately, which is what this link means."),
            source="BPHS, the Dhana Yoga chapter.",
            # Exchange is the strongest of the three links in every listing,
            # conjunction next, mutual aspect last. That ordering is classical;
            # no number is attached to it here because none is given.
            strength={"exchange": "strong (parivartana)",
                      "conjunction": "moderate (conjunction)",
                      "mutual aspect": "moderate (mutual aspect)",
                      "one-way aspect": "weak (one-way aspect)"}[pair["how"]],
            association=pair["how"],
            houses=houses,
            house_pairs=pair["house_pairs"],
        ))
    return out


def raja_yogas(chart: object) -> list[dict]:
    """A kendra lord associated with a trikona lord.

    Kendras are 1, 4, 7, 10 and trikonas are 1, 5, 9. The 1st is both, which is
    why the two lists overlap; the pair still has to be two different planets,
    so the Lagna lord cannot form a Raja Yoga with itself.

    Source: BPHS, the Raja Yoga chapter. Kendradhipati dosha — the doctrine
    that natural benefics owning kendras lose their power to bless — is not
    applied; see NOT_IMPLEMENTED.
    """
    view = _view(chart)
    out = []
    for pair in _lord_pairs(view, KENDRAS, TRIKONAS):
        a, b = pair["planets"]
        kendra_h = sorted({hp[0] for hp in pair["house_pairs"]})
        trikona_h = sorted({hp[1] for hp in pair["house_pairs"]})
        # The 1st is both, so label it that way rather than picking a side.
        _roles = {h: ("kendra and trikona" if h in KENDRAS and h in TRIKONAS
                      else "kendra" if h in KENDRAS else "trikona")
                  for h in set(kendra_h) | set(trikona_h)}
        out.append(_yoga(
            "raja", "Raja Yoga", "Raja", [a, b],
            condition=(
                f"{_lordship(view, a, kendra_h + trikona_h, labels=_roles)} "
                f"with {_lordship(view, b, kendra_h + trikona_h, labels=_roles)}"
                f" — joined by {pair['how']}."),
            note=(f"The classical Raja Yoga: the houses of action and the houses "
                  f"of fortune are tied together through {a} and {b} by "
                  f"{pair['how']}. Read as capacity meeting opportunity, and "
                  f"traditionally expected to deliver during the periods of the "
                  f"two planets involved."),
            source="BPHS, the Raja Yoga chapter.",
            strength={"exchange": "strong (parivartana)",
                      "conjunction": "moderate (conjunction)",
                      "mutual aspect": "moderate (mutual aspect)",
                      "one-way aspect": "weak (one-way aspect)"}[pair["how"]],
            association=pair["how"],
            kendra_houses=kendra_h,
            trikona_houses=trikona_h,
            house_pairs=pair["house_pairs"],
        ))
    return out


# -- Kemadruma -------------------------------------------------------------

def kemadruma(chart: object) -> list[dict]:
    """The Moon standing alone — and the cancellations that undo it.

    Formed when no planet occupies the 2nd or the 12th from the Moon, and none
    shares the Moon's sign. The Sun is not counted, because it is beside the
    Moon too often for its presence there to say anything; the nodes are not
    counted either, which is the majority reading.

    Source: BPHS, among the Chandra yogas that also give Sunapha, Anapha and
    Durudhara — Kemadruma is the absence of all three.

    The cancellations applied are listed in KEMADRUMA_CANCELLATIONS. All four
    are widely printed and the sources differ over which are sufficient alone;
    'moon_dignified' has the least support of the four and is the first a
    lineage would want to drop.

    Returned even when it does not form, so a reading can say the Moon is not
    isolated — this is the yoga people are most often frightened by.
    """
    view = _view(chart)
    moon_sign = view["signs"]["Moon"]
    considered = [g for g in GRAHAS
                  if g != "Moon" and g not in KEMADRUMA_IGNORED]

    company: list[dict] = []
    for planet in considered:
        distance = _sign_distance(moon_sign, view["signs"][planet])
        if distance in (2, 12) or (distance == 1 and KEMADRUMA_INCLUDES_CONJUNCTION):
            company.append({"planet": planet, "from_moon": distance})

    if company:
        where = ", ".join(f"{c['planet']} in the {_ordinal(c['from_moon'])}"
                          for c in company)
        return [_yoga(
            "kemadruma", "Kemadruma Yoga", "Chandra yoga", ["Moon"],
            condition=f"The Moon has company: {where} from it.",
            note=(f"Kemadruma does not form. The Moon is flanked or joined "
                  f"({where} counted from it), which is the ordinary case and the "
                  f"thing the yoga is defined by the absence of."),
            source="BPHS, the Chandra yogas.",
            strength=None,
            formed=False, cancelled=False, company=company, cancellations=[],
        )]

    # Isolated. Now the cancellations.
    reasons: list[str] = []
    moon_house = view["houses"]["Moon"]

    if "moon_in_kendra" in KEMADRUMA_CANCELLATIONS and moon_house in KENDRAS:
        reasons.append(f"the Moon itself occupies the {_ordinal(moon_house)}, "
                       f"a kendra from the Lagna")

    if "planet_in_kendra_from_moon" in KEMADRUMA_CANCELLATIONS:
        in_kendra = [p for p in considered
                     if _sign_distance(moon_sign, view["signs"][p]) in (4, 7, 10)]
        if in_kendra:
            reasons.append(f"{', '.join(in_kendra)} stand in kendras from the Moon")

    if "benefic_with_moon" in KEMADRUMA_CANCELLATIONS:
        helpers = [b for b in NATURAL_BENEFICS
                   if _conjunct(view, "Moon", b) or _aspects(view, b, "Moon")]
        if helpers:
            reasons.append(f"the Moon is joined or aspected by "
                           f"{' and '.join(helpers)}")

    if "moon_dignified" in KEMADRUMA_CANCELLATIONS:
        dignity = _dignity(view, "Moon")
        if dignity:
            reasons.append(f"the Moon is in its {dignity} ({moon_sign})")

    cancelled = bool(reasons)
    if cancelled:
        note = (f"The Moon has nothing in the 2nd, the 12th or its own sign, which "
                f"is the Kemadruma condition — but the yoga is cancelled: "
                f"{'; '.join(reasons)}. A cancelled Kemadruma is not read as a "
                f"defect.")
    else:
        note = ("Nothing stands in the 2nd or the 12th from the Moon, and nothing "
                "shares its sign. Kemadruma forms and none of the standard "
                "cancellations applies. Traditionally read as a mind that has to "
                "carry itself without support, and as effort that does not "
                "compound. It is also the yoga most often overstated: it is "
                "common, and the classical texts weigh it against the rest of the "
                "chart rather than on its own.")

    return [_yoga(
        "kemadruma", "Kemadruma Yoga", "Chandra yoga", ["Moon"],
        condition=(f"No planet in the 2nd or 12th from the Moon in {moon_sign}, "
                   f"and none with it."),
        note=note,
        source="BPHS, the Chandra yogas.",
        strength=None,
        formed=not cancelled, cancelled=cancelled,
        isolated=True, company=[], cancellations=reasons,
        moon_house=moon_house,
    )]


# -- The two small combinations -------------------------------------------

def chandra_mangala(chart: object) -> list[dict]:
    """Moon with Mars.

    BPHS states this as a conjunction, and conjunction is what forms it here.
    The extension to mutual aspect is common in modern practice and is not in
    the verse; CHANDRA_MANGALA_INCLUDES_MUTUAL_ASPECT switches it on.
    """
    view = _view(chart)
    conjunct = _conjunct(view, "Moon", "Mars")
    mutual = (CHANDRA_MANGALA_INCLUDES_MUTUAL_ASPECT
              and _aspects(view, "Mars", "Moon") and _aspects(view, "Moon", "Mars"))
    if not (conjunct or mutual):
        return []

    how = "conjunct in " + view["signs"]["Moon"] if conjunct else "in mutual aspect"
    return [_yoga(
        "chandra_mangala", "Chandra-Mangala Yoga", "Combination",
        ["Moon", "Mars"],
        condition=f"Moon and Mars {how}.",
        note=("The Moon and Mars together. Classically read as drive attached to "
              "feeling: earning power and enterprise, and a temper that runs hot. "
              "The texts give it a mercenary edge as often as a fortunate one, so "
              "it is not simply a benefic combination."),
        source="BPHS; also in Phaladeepika.",
        strength=None,
        association="conjunction" if conjunct else "mutual aspect",
        sign=view["signs"]["Moon"] if conjunct else None,
        house=view["houses"]["Moon"] if conjunct else None,
    )]


def budha_aditya(chart: object) -> list[dict]:
    """Sun with Mercury in one sign.

    Mercury is never more than about 28° from the Sun, so this is a frequent
    combination and Mercury is combust in most instances of it. Combustion is
    reported, not enforced: whether a combust Mercury voids the yoga is a
    judgement about results rather than about formation, and the sources that
    raise it do not agree. BUDHA_ADITYA_REQUIRES_NO_COMBUSTION enforces it.

    Source: widely carried in the later literature; Phaladeepika gives the same
    Sun-Mercury combination under the name Nipuna Yoga.
    """
    view = _view(chart)
    if not _conjunct(view, "Sun", "Mercury"):
        return []

    separation = angular_sep(view["longitudes"]["Sun"], view["longitudes"]["Mercury"])
    arc = COMBUSTION_ARC["Mercury_retrograde" if view["retrograde"].get("Mercury")
                         else "Mercury"]
    combust = separation < arc
    if combust and BUDHA_ADITYA_REQUIRES_NO_COMBUSTION:
        return []

    note = ("The Sun and Mercury share a sign — intelligence attached to the sense "
            "of self. Read as analytical ability, learning and skill at any work "
            "that is done with the mind.")
    if combust:
        note += (f" Mercury is {separation:.1f}° from the Sun and so combust; many "
                 f"practitioners hold a combust Mercury gives the yoga less than "
                 f"its full result, and it is worth reading as a qualification.")

    return [_yoga(
        "budha_aditya", "Budha-Aditya Yoga", "Combination", ["Sun", "Mercury"],
        condition=(f"Sun and Mercury both in {view['signs']['Sun']}, "
                   f"{separation:.1f}° apart."),
        note=note,
        source="Later classical literature; Phaladeepika carries the same "
               "combination as Nipuna Yoga.",
        strength=None,
        separation=round(separation, 2),
        mercury_combust=combust,
        combustion_arc=arc,
        sign=view["signs"]["Sun"],
        house=view["houses"]["Sun"],
    )]


# -- Nabhasa Yogas -----------------------------------------------------------
#
# A structural family: 32 yogas formed purely from which houses (or how many
# distinct signs) the seven classical grahas occupy, independent of dignity or
# aspect. Four groups:
#
#   * Asraya  (3)  — by the MODALITY of the signs all seven occupy.
#   * Dala    (2)  — by benefics or malefics gathering in the four kendras.
#   * Akriti  (20) — by the HOUSES all seven occupy forming a named shape.
#   * Sankhya (7)  — by how many distinct SIGNS the seven occupy, 1 through 7.
#
# Source: Brihat Jataka ch. 12 (Varaha Mihira, tr. N. Chidambaram Iyer, 1885 —
# public domain; Harvard Widener Library / Google Books scan). The same
# chapter names BPHS as carrying an equivalent list.
#
# Rahu and Ketu take no part, for the reason given throughout this module:
# they own no sign, and the source states this family in terms of the seven
# classical grahas.
#
# Priority, simplified. The source spends several verses adjudicating what
# happens when a chart matches more than one Nabhasa yoga at once — chiefly,
# a Sankhya yoga can coincide with an Akriti or Asraya yoga of the same size.
# Rather than reproduce that adjudication case by case, this module applies
# one rule: Asraya, Dala and Akriti are tested first and are independent of
# each other (they test different things — sign modality, benefic/malefic
# placement, house pattern — so more than one can legitimately form
# together); Sankhya is tested last and reported only if none of the other
# three formed. The one exception the source insists on by name is kept:
# Gola (all seven in a single sign) is always reported even alongside an
# Asraya yoga, because the source specifically says Gola is not to be
# folded into Asraya the way Kedara/Sula/Yuga are.
#
# House-set yogas are matched by EXACT equality: the set of houses the seven
# grahas occupy must equal the named set, not merely be contained in it. A
# subset test would make Gada indistinguishable from Kamala, and Yupa from
# Nau, which the source treats as different yogas precisely because the
# occupied houses differ.
#
# Naming collision, flagged rather than hidden: this module's Sakata (Nabhasa/
# Akriti — all seven confined to the Lagna and 7th) is a different yoga from
# the Chandra-yoga-family Sakata (Moon-Jupiter based) named in NOT_IMPLEMENTED.
# The tradition reuses the name across two unrelated yoga families; this is
# the source's own overlap, not an error here.

NABHASA_BENEFICS = ("Mercury", "Jupiter", "Venus")
NABHASA_MALEFICS = ("Sun", "Mars", "Saturn")
# Distinct from NATURAL_BENEFICS above, which serves Kemadruma and deliberately
# excludes Mercury for a different reason (its benefic status there is
# conditional on the company it keeps). This grouping is the Dala yoga's own,
# attributed by the source to Parasara. Neither grouping opines on the Moon;
# Vajra/Yava below need only place it among the four kendras with the rest,
# not on a particular side of the split — the source does not say where it goes.

PANAPHARA = (2, 5, 8, 11)
APOKLIMA = (3, 6, 9, 12)


def _occupied_houses(view: dict) -> frozenset[int]:
    return frozenset(view["houses"][g] for g in GRAHAS)


def _occupied_signs_count(view: dict) -> int:
    return len({view["signs"][g] for g in GRAHAS})


def _consecutive(start: int, span: int) -> frozenset[int]:
    """`span` houses counted inclusively from `start`, wrapping past the 12th."""
    return frozenset(((start - 1 + k) % 12) + 1 for k in range(span))


_ASRAYA = {
    "Cardinal": ("rajju", "Rajju Yoga",
                 "restless and acquisitive — jealous of others' wealth and "
                 "drawn to foreign travel"),
    "Fixed": ("musala", "Musala Yoga",
              "respectable and prosperous, engaged in many undertakings at once"),
    "Mutable": ("nala", "Nala Yoga",
                "unusual in body but settled in outlook — rich and skilled at "
                "the work chosen"),
}


def _asraya_yoga(view: dict) -> list[dict]:
    modalities = {MODALITY[view["signs"][g]] for g in GRAHAS}
    if len(modalities) != 1:
        return []
    modality = next(iter(modalities))
    key, name, meaning = _ASRAYA[modality]
    return [_yoga(
        key, name, "Nabhasa — Asraya", list(GRAHAS),
        condition=f"All seven grahas stand in {modality.lower()} signs.",
        note=f"{name}: {meaning}.",
        source="Brihat Jataka ch. 12 (Varaha Mihira).",
        strength=None,
        modality=modality,
    )]


def _dala_yoga(view: dict) -> list[dict]:
    formed = []
    for group, key, name, meaning in (
        (NABHASA_BENEFICS, "srik", "Srik Yoga (Mala Yoga)",
         "ease and material comfort — a life lived without much friction"),
        (NABHASA_MALEFICS, "sarpa", "Sarpa Yoga",
         "hardship on several fronts at once, the difficult mirror of Srik"),
    ):
        if all(view["houses"][g] in KENDRAS for g in group):
            formed.append(_yoga(
                key, name, "Nabhasa — Dala", list(group),
                condition=f"{', '.join(group)} all stand in the four kendras.",
                note=f"{name}: {meaning}.",
                source="Brihat Jataka ch. 12, attributed there to Parasara.",
                strength=None,
            ))
    return formed


# name_key, display name, the exact house-set(s) that form it, and the effect.
_AKRITI_GROUPS: tuple[tuple[str, str, tuple[frozenset[int], ...], str], ...] = (
    ("gada", "Gada Yoga",
     (frozenset({1, 4}), frozenset({4, 7}), frozenset({7, 10}), frozenset({10, 1})),
     "performs sacrificial rites, is wealthy, and is forever occupied in "
     "acquiring more"),
    ("sakata", "Sakata Yoga", (frozenset({1, 7}),),
     "makes a living by vehicles or transport, is prone to illness, and has "
     "an unhappy marriage"),
    ("vihaga", "Vihaga Yoga", (frozenset({4, 10}),),
     "lives by carrying messages or communication, is fond of travel, and "
     "tends to stir up quarrels"),
    ("sringataka", "Sringataka Yoga", (frozenset({1, 5, 9}),),
     "finds happiness late in life rather than early"),
    ("hala", "Hala Yoga",
     (frozenset({2, 6, 10}), frozenset({3, 7, 11}), frozenset({4, 8, 12})),
     "works the land — a life built on steady, direct labour"),
    ("vapi", "Vapi Yoga", (frozenset(PANAPHARA), frozenset(APOKLIMA)),
     "lives modestly for a long stretch of life, and hoards rather than spends"),
    ("yupa", "Yupa Yoga", (_consecutive(1, 4),),
     "liberal in giving, and drawn to formal or ceremonial acts of merit"),
    ("ishu", "Ishu Yoga (Bana Yoga)", (_consecutive(4, 4),),
     "severe by temperament — drawn to confinement, punishment, or the making "
     "of weapons"),
    ("sakti", "Sakti Yoga", (_consecutive(7, 4),),
     "takes on work beneath their station, unskilled and without much comfort"),
    ("danda", "Danda Yoga", (_consecutive(10, 4),),
     "separated from those they love, earning a living by the humblest means"),
    ("nau", "Nau Yoga", (_consecutive(1, 7),),
     "widely known, but happy only intermittently, and inclined to be a miser"),
    ("kuta", "Kuta Yoga", (_consecutive(4, 7),),
     "inclined to deception, drawn to work as a guard or gaoler"),
    ("chhatra", "Chhatra Yoga", (_consecutive(7, 7),),
     "brings comfort to their own people, with ease arriving in later life"),
    ("chapa", "Chapa Yoga", (_consecutive(10, 7),),
     "delights in conflict, and is comfortable at both the start and the end "
     "of life"),
    ("ardha_chandra", "Ardha-Chandra Yoga",
     tuple(_consecutive(s, 7) for s in (2, 3, 5, 6, 8, 9, 11, 12)),
     "a general favourite — agreeable, and well regarded by nearly everyone"),
    ("samudra", "Samudra Yoga", (frozenset({2, 4, 6, 8, 10, 12}),),
     "prosperous and comfortable, on a scale the tradition compares to a king"),
    ("chakra", "Chakra Yoga", (frozenset({1, 3, 5, 7, 9, 11}),),
     "commands real deference from others — the tradition's image is of kings "
     "paying respect"),
)

_SANKHYA: dict[int, tuple[str, str, str]] = {
    7: ("vallaki", "Vallaki Yoga", "skilled at work, and delights in music and dance"),
    6: ("damini", "Damini Yoga", "liberal in giving, and delights in helping others"),
    5: ("pasa", "Pasa Yoga",
        "earns wealth by honest means, with the help of family and servants"),
    4: ("kedara", "Kedara Yoga",
        "works the land, and is useful to others through steady good deeds"),
    3: ("sula", "Sula Yoga", "bold in a fight and fond of money, but stays poor"),
    2: ("yuga", "Yuga Yoga", "poor, and inclined to act against convention"),
    1: ("gola", "Gola Yoga", "poor, unclean, unskilled, and forever on the move"),
}


def _sankhya_yoga(view: dict) -> dict:
    count = _occupied_signs_count(view)
    key, name, meaning = _SANKHYA[count]
    return _yoga(
        key, name, "Nabhasa — Sankhya", list(GRAHAS),
        condition=(f"The seven grahas occupy exactly {count} distinct "
                   f"sign{'s' if count != 1 else ''}."),
        note=f"{name}: {meaning}.",
        source="Brihat Jataka ch. 12 (Varaha Mihira).",
        strength=None,
        sign_count=count,
    )


def nabhasa_yogas(chart: object) -> list[dict]:
    """All 32 Nabhasa yogas this module tests, judged against one chart.

    Formed from house and sign PATTERN alone — no dignity, no aspect. See the
    comment block above this function for the priority rule applied when a
    chart could match more than one Nabhasa yoga, and for why the exact house
    SET is required rather than a subset.

    Source: Brihat Jataka ch. 12 (Varaha Mihira, tr. N. Chidambaram Iyer, 1885).
    """
    view = _view(chart)
    occupied = _occupied_houses(view)
    formed: list[dict] = []
    formed += _asraya_yoga(view)
    formed += _dala_yoga(view)

    for key, name, sets, meaning in _AKRITI_GROUPS:
        if occupied in sets:
            formed.append(_yoga(
                key, name, "Nabhasa — Akriti", list(GRAHAS),
                condition=(f"All seven grahas confined to house"
                           f"{'s' if len(occupied) != 1 else ''} "
                           f"{', '.join(_ordinal(h) for h in sorted(occupied))}."),
                note=f"{name}: {meaning}.",
                source="Brihat Jataka ch. 12 (Varaha Mihira).",
                strength=None,
                houses=sorted(occupied),
            ))

    # Kamala, and its two named exceptions Vajra and Yava: same house-set
    # (all four kendras), distinguished by which houses hold the benefics and
    # which hold the malefics.
    if occupied == frozenset(KENDRAS):
        benefic_houses = {view["houses"][g] for g in NABHASA_BENEFICS}
        malefic_houses = {view["houses"][g] for g in NABHASA_MALEFICS}
        if benefic_houses <= {1, 7} and malefic_houses <= {4, 10}:
            formed.append(_yoga(
                "vajra", "Vajra Yoga", "Nabhasa — Akriti", list(GRAHAS),
                condition="Benefics confined to the Lagna and 7th, malefics to "
                          "the 4th and 10th.",
                note="Vajra Yoga: happy at both the start and the end of life, "
                     "a general favourite, and bold in confrontation.",
                source="Brihat Jataka ch. 12 (Varaha Mihira).",
                strength=None, houses=sorted(occupied),
            ))
        elif malefic_houses <= {1, 7} and benefic_houses <= {4, 10}:
            formed.append(_yoga(
                "yava", "Yava Yoga", "Nabhasa — Akriti", list(GRAHAS),
                condition="Malefics confined to the Lagna and 7th, benefics to "
                          "the 4th and 10th.",
                note="Yava Yoga: powerful, with happiness concentrated in the "
                     "middle years of life.",
                source="Brihat Jataka ch. 12 (Varaha Mihira).",
                strength=None, houses=sorted(occupied),
            ))
        else:
            formed.append(_yoga(
                "kamala", "Kamala Yoga", "Nabhasa — Akriti", list(GRAHAS),
                condition="All seven grahas confined to the four kendras.",
                note="Kamala Yoga: widely renowned, deeply content, and "
                     "accomplished across several fields.",
                source="Brihat Jataka ch. 12 (Varaha Mihira).",
                strength=None, houses=sorted(occupied),
            ))

    sankhya = _sankhya_yoga(view)
    if not formed or sankhya["sign_count"] == 1:
        formed.append(sankhya)

    return formed


# --------------------------------------------------------------------------
# Public entry points
# --------------------------------------------------------------------------

YOGA_FUNCTIONS = (
    pancha_mahapurusha, gaja_kesari, neecha_bhanga,
    dhana_yogas, raja_yogas, kemadruma, chandra_mangala, budha_aditya,
    nabhasa_yogas,
)


def yogas(chart: object) -> dict:
    """Every yoga this module knows how to test, judged against one chart.

    The list carries entries that did NOT form as well, where saying so is
    useful: an uncancelled debilitation, and a Kemadruma that does not form.
    Each entry's `formed` flag is the thing to read; `yogas` in the returned
    dict is the filtered list of what actually formed.
    """
    view = _view(chart)
    everything: list[dict] = []
    for fn in YOGA_FUNCTIONS:
        everything.extend(fn(chart))

    formed = [y for y in everything if y.get("formed", True)]
    return {
        "yogas": formed,
        "all": everything,
        "count": len(formed),
        "by_group": sorted({y["group"] for y in formed}),
        "lagna": view["lagna_sign"],
        "house_lords": {str(h): p for h, p in view["house_lords"].items()},
        "shared_dhana_lords": _shared_lords(view, DHANA_HOUSES),
        "method_note": (
            "Houses are whole-sign from the Lagna, aspects are graha drishti "
            "(every planet the 7th; Mars the 4th and 8th, Jupiter the 5th and "
            "9th, Saturn the 3rd and 10th), and Rahu and Ketu take no part in "
            "any yoga rule here."
        ),
    }


def analyse(chart: object, divisions: tuple[str, ...] = DEFAULT_DIVISIONS) -> dict:
    """Divisional charts, Vargottama, varga strength and the yogas, as one dict.

    `chart` is a `chart_service` chart session or the bundle dict it carries,
    built with `zodiac='sidereal'`. Everything returned is JSON-serialisable.
    """
    view = _view(chart)
    return {
        "meta": {
            "name": view["meta"].get("name") or "",
            "zodiac": view["meta"].get("zodiac"),
            "ayanamsa": view["meta"].get("ayanamsa"),
            "lagna": view["lagna_sign"],
            "lagna_lord": DOMICILE[view["lagna_sign"]],
            "house_system": "Whole Sign (vargas and yogas are whole-sign rules)",
        },
        "rashi_positions": {
            name: {
                "sign": view["signs"][name],
                "position": _position(view, name),
                "house": view["houses"][name],
                "navamsa": varga_sign(view["longitudes"][name], "D9"),
            }
            for name in view["bodies"]
        },
        "vargas": divisional_charts(chart, divisions),
        "vargottama": vargottama(chart),
        "varga_strength": varga_strength(chart, divisions),
        "yogas": yogas(chart),
        "not_implemented": [{"rule": r, "why": w} for r, w in NOT_IMPLEMENTED],
        "disclaimer": (
            "Divisional charts and yogas are the classical rules as the texts "
            "state them, applied mechanically. Where lineages disagree the "
            "choice made here is named in the module constants and in each "
            "rule's own note. A yoga is one sentence of a chart, not a verdict "
            "on a life."
        ),
    }


_VARGA_META_HI = {
    "D1": {"name": "Rashi", "name_hi": "लग्न / राशि कुंडली", "purpose": "General Life & Physical Self", "purpose_hi": "समग्र जीवन व शरीर"},
    "D3": {"name": "Drekkana", "name_hi": "द्रेष्काण", "purpose": "Siblings & Courage", "purpose_hi": "सहज, पराक्रम व भाई-बहन"},
    "D7": {"name": "Saptamsha", "name_hi": "सप्तांश", "purpose": "Children & Lineage", "purpose_hi": "संतान व वंश वृद्धि"},
    "D9": {"name": "Navamsha", "name_hi": "नवमांश", "purpose": "Dharma, Spouse & Destiny", "purpose_hi": "धर्म, जीवनसाथी व भाग्य"},
    "D10": {"name": "Dashamsha", "name_hi": "दशमांश", "purpose": "Career, Profession & Status", "purpose_hi": "करियर, पद व आजीविका"},
    "D12": {"name": "Dwadashamsha", "name_hi": "द्वादशांश", "purpose": "Parents & Lineage", "purpose_hi": "माता-पिता व पितृ विचार"},
}

_SIGNS_HI = {
    "Aries": "मेष", "Taurus": "वृषभ", "Gemini": "मिथुन", "Cancer": "कर्क",
    "Leo": "सिंह", "Virgo": "कन्या", "Libra": "तुला", "Scorpio": "वृश्चिक",
    "Sagittarius": "धनु", "Capricorn": "मकर", "Aquarius": "कुंभ", "Pisces": "मीन"
}

_PLANETS_HI = {
    "Sun": "सूर्य", "Moon": "चंद्र", "Mars": "मंगल", "Mercury": "बुध",
    "Jupiter": "गुरु", "Venus": "शुक्र", "Saturn": "शनि", "Rahu": "राहु",
    "Ketu": "केतु", "Lagna": "लग्न", "ASC": "लग्न"
}


def get_shodashvarga_data(chart: object, lang: str = "en") -> dict:
    """Public helper returning structured Shodashvarga chart tables for UI and API."""
    is_hi = lang == "hi"
    v_dict = divisional_charts(chart)
    results = {}
    for code, v_data in v_dict.items():
        meta = _VARGA_META_HI.get(code, {"name": code, "name_hi": code, "purpose": "", "purpose_hi": ""})
        title = meta["name_hi"] if is_hi else meta["name"]
        purpose = meta["purpose_hi"] if is_hi else meta["purpose"]
        asc_sign = v_data["lagna"]
        asc_label = _SIGNS_HI.get(asc_sign, asc_sign) if is_hi else asc_sign

        placements = []
        houses_map = {h: [] for h in range(1, 13)}
        for p_name, p_info in v_data["positions"].items():
            p_sign = p_info["sign"]
            p_house = p_info["house"]
            p_label = _PLANETS_HI.get(p_name, p_name) if is_hi else p_name
            sign_label = _SIGNS_HI.get(p_sign, p_sign) if is_hi else p_sign
            placements.append({
                "planet": p_name,
                "planet_label": p_label,
                "sign": p_sign,
                "sign_label": sign_label,
                "house": p_house,
            })
            houses_map[p_house].append(p_label)

        results[code] = {
            "code": code,
            "title": title,
            "purpose": purpose,
            "ascendant_sign": asc_sign,
            "ascendant_label": asc_label,
            "placements": placements,
            "houses": houses_map,
        }

    return {
        "vargas": results,
        "available_codes": list(results.keys()),
    }
