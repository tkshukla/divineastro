"""Classical delineation text: dignity, house, career and conjunction lookups.

A pure unit test, in the shape `test_vargas.py` uses: minimal chart bundles,
driven straight against `app.astro.delineation`, finishing against a real
chart built by `chart_service` so the bundle shape is checked against the real
producer.

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.test_delineation
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.astro import delineation as d
from app.astro import vargas as v
from app.chart_service import DOMICILE, SIGNS, dms, sign_of

failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


GRAHAS = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")

# Same QUIET fixture as test_vargas.py, for the same reason: a known, inert
# baseline that every positive test moves exactly one planet away from.
QUIET = {
    "Sun": "Scorpio", "Moon": "Aquarius", "Mars": "Pisces", "Mercury": "Cancer",
    "Jupiter": "Sagittarius", "Venus": "Cancer", "Saturn": "Leo",
}


def lon(sign: str, degree: float = 5.0) -> float:
    return SIGNS.index(sign) * 30.0 + degree


def _obj(name: str, longitude: float) -> dict:
    longitude %= 360.0
    return {
        "name": name, "kind": "planet", "longitude": longitude,
        "sign": sign_of(longitude), "degree": longitude % 30.0,
        "position": f"{sign_of(longitude)} {dms(longitude % 30.0)}",
        "retrograde": False,
    }


def chart(asc: str | float = "Aries", **where: str | float) -> dict:
    placements = dict(QUIET)
    placements.update(where)

    def place(value: str | float) -> float:
        return lon(value) if isinstance(value, str) else float(value)

    objects = {"ASC": _obj("ASC", place(asc))}
    for graha in GRAHAS:
        objects[graha] = _obj(graha, place(placements[graha]))
    return {
        "meta": {"zodiac": "sidereal", "name": "Native", "ayanamsa": "lahiri"},
        "birth": {"name": "Native"},
        "objects": objects,
    }


# -- Rulership audit of the Bhrigu per-Lagna corpus ---------------------------
# Which sign a graha owns, is exalted in or is debilitated in is astronomically
# fixed, so a corpus entry's dignity claim can be checked against vargas.py's
# tables without consulting any tradition. Friend/enemy claims are deliberately
# NOT audited: those are the source's own and are reported as it states them,
# even where they diverge from the BPHS table (docs/sources/bhrigu_samhita_notes.md).
# Rahu and Ketu are skipped by the dignity check because vargas.py assigns the
# nodes no sign dignity -- and, for the same reason, a node entry must not CLAIM
# one (node_bad below).
_DIGNITY_CLAIM = re.compile(r"\b(own sign|exalted|debilitated)\b", re.IGNORECASE)
_LEADING_BREAK = re.compile(r"\s—\s|;|\.\s")
# A dignity claim in a trailing aspect clause: "its aspect on the 7th (own sign)".
# The parenthetical names the ASPECTED house's sign, judged against the aspecting
# graha (a friendly / enemy sign is the source's own stance and is not audited).
_ASPECT_CLAIM = re.compile(
    r"\baspect on the (Lagna|\d+(?:st|nd|rd|th))\s*\(([^)]*)\)", re.IGNORECASE)

_LORD_CLAIM = re.compile(
    r"\b(Sun|Moon|Mars|Mercury|Jupiter|Venus|Saturn) rules the (\d+)(?:st|nd|rd|th)\b")
_AS_LORD_CLAIM = re.compile(r"\bas (\d+)(?:st|nd|rd|th) lord\b")


def sign_of_house(lagna: str, house: int) -> str:
    """The sign occupying `house` (1-12) in a whole-sign chart with this Lagna."""
    return SIGNS[(SIGNS.index(lagna) + house - 1) % 12]


def leading_clause(text: str) -> str:
    """An entry's opening clause: everything before its first em-dash, semicolon
    or sentence break. That is where the placement's own dignity is stated; the
    aspect clauses after it talk about other houses' signs, so they are not read."""
    return _LEADING_BREAK.split(text, maxsplit=1)[0]


def rulership_audit(corpus: dict) -> dict:
    """Check every classical-graha entry's rulership claims against the fixed facts.

    Two kinds of claim are read: a leading "own sign" / "exalted" / "debilitated"
    (must match where that graha really is in that sign for that Lagna+house),
    and any "X rules the Nth" / "as Nth lord" (must name the true lord of the
    Nth house from that Lagna). Returns the counts checked and the violations.
    """
    dignity_claims = lordship_claims = aspect_claims = 0
    lagnas_with_claims: set[str] = set()
    dignity_bad: list[str] = []
    lordship_bad: list[str] = []
    aspect_bad: list[str] = []
    node_bad: list[str] = []
    for lagna, by_planet in corpus.items():
        for planet, by_house in by_planet.items():
            if planet not in v.GRAHAS:
                if planet in ("Rahu", "Ketu"):
                    for house, text in sorted(by_house.items()):
                        head = leading_clause(text)
                        if _DIGNITY_CLAIM.search(head):
                            node_bad.append(f"{lagna} Lagna, {planet} in {house} "
                                            f"claims sign dignity: {head[:60]!r}")
                continue
            for house, text in sorted(by_house.items()):
                where = f"{lagna} Lagna, {planet} in {house}"
                sign = sign_of_house(lagna, house)
                head = leading_clause(text)
                for claim in {m.group(1).lower() for m in _DIGNITY_CLAIM.finditer(head)}:
                    dignity_claims += 1
                    lagnas_with_claims.add(lagna)
                    if claim == "own sign":
                        ok = sign in v.OWN_SIGNS[planet]
                    elif claim == "exalted":
                        ok = v.EXALTATION[planet] == sign
                    else:
                        ok = v.DEBILITATION[planet] == sign
                    if not ok:
                        dignity_bad.append(
                            f"{where} ({sign}) claims {claim!r}: {head[:60]!r}")
                for m in _ASPECT_CLAIM.finditer(text):
                    ref = m.group(1)
                    n = 1 if ref.lower() == "lagna" else int(re.match(r"\d+", ref).group())
                    aspected = sign_of_house(lagna, n)
                    for claim in {c.group(1).lower()
                                  for c in _DIGNITY_CLAIM.finditer(m.group(2))}:
                        aspect_claims += 1
                        if claim == "own sign":
                            ok = aspected in v.OWN_SIGNS[planet]
                        elif claim == "exalted":
                            ok = v.EXALTATION[planet] == aspected
                        else:
                            ok = v.DEBILITATION[planet] == aspected
                        if not ok:
                            aspect_bad.append(
                                f"{where}: aspect on the {n} ({aspected}) claims "
                                f"{claim!r}, which {planet} does not have there")
                for m in _LORD_CLAIM.finditer(text):
                    lordship_claims += 1
                    named, n = m.group(1), int(m.group(2))
                    if DOMICILE[sign_of_house(lagna, n)] != named:
                        lordship_bad.append(f"{where}: {m.group(0)!r} but the "
                                            f"{n}th is {sign_of_house(lagna, n)}")
                for m in _AS_LORD_CLAIM.finditer(text):
                    lordship_claims += 1
                    n = int(m.group(1))
                    if DOMICILE[sign_of_house(lagna, n)] != planet:
                        lordship_bad.append(f"{where}: {m.group(0)!r} but the "
                                            f"{n}th is {sign_of_house(lagna, n)}")
    return {"dignity_claims": dignity_claims, "lordship_claims": lordship_claims,
            "lagnas": lagnas_with_claims, "dignity_bad": dignity_bad,
            "lordship_bad": lordship_bad,
            "aspect_claims": aspect_claims, "aspect_bad": aspect_bad,
            "node_bad": node_bad,
            "violations": dignity_bad + lordship_bad + aspect_bad + node_bad}


def main() -> int:
    print("\n1. Dignity state — the seven-way classification")
    check("an exalted planet reads exaltation",
          d.dignity_state("Sun", "Aries", 10.0) == "exaltation")
    check("moolatrikona is distinguished from plain own sign by degree",
          d.dignity_state("Sun", "Leo", 5.0) == "moolatrikona"
          and d.dignity_state("Sun", "Leo", 25.0) == "own_sign")
    check("a debilitated planet reads debilitation, never a dignity",
          d.dignity_state("Sun", "Libra") == "debilitation")
    check("Sun in Mercury's sign (Gemini) reads neutral, not friendly or enemy — "
          "the natural-friendship table (BPHS ch. 3) makes Mercury the Sun's "
          "only neutral",
          d.dignity_state("Sun", "Gemini") == "neutral_sign")
    check("Sun in Jupiter's sign (Sagittarius) reads friendly — Jupiter is a "
          "natural friend of the Sun",
          d.dignity_state("Sun", "Sagittarius") == "friendly_sign")
    check("Sun in Saturn's sign (Capricorn) reads enemy — Saturn is a "
          "natural enemy of the Sun",
          d.dignity_state("Sun", "Capricorn") == "enemy_sign")
    check("every planet has text for every one of the seven states",
          all(state in d.DIGNITY_DELINEATION[p] and d.DIGNITY_DELINEATION[p][state]
              for p in GRAHAS
              for state in ("exaltation", "moolatrikona", "own_sign",
                            "friendly_sign", "neutral_sign", "enemy_sign",
                            "debilitation")))
    check("dignity_delineation() carries the state and the matching text together",
          d.dignity_delineation("Venus", "Pisces", 10.0)["state"] == "exaltation"
          and d.dignity_delineation("Venus", "Pisces", 10.0)["note"]
          == d.DIGNITY_DELINEATION["Venus"]["exaltation"])

    print("\n2. Planet-in-house text — the base table and its named overrides")
    check("the Sun uses its own base table",
          d.planet_house_text("Sun", 10) == d._BASE_HOUSE_TEXT[10])
    check("Mercury overrides house 5 (its own text) but falls back to the "
          "Sun's table for house 10 (not one of its named houses)",
          d.planet_house_text("Mercury", 5) == d._MERCURY_OVERRIDES[5]
          and d.planet_house_text("Mercury", 10) == d._BASE_HOUSE_TEXT[10])
    check("Mars overrides houses 1, 2 and 9 but shares the Sun's table elsewhere",
          d.planet_house_text("Mars", 1) == d._MARS_OVERRIDES[1]
          and d.planet_house_text("Mars", 6) == d._BASE_HOUSE_TEXT[6])
    check("the Moon has a complete table of its own, distinct from the Sun's",
          all(d.planet_house_text("Moon", h) == d._MOON_HOUSE_TEXT[h] for h in range(1, 13))
          and d.planet_house_text("Moon", 1) != d._BASE_HOUSE_TEXT[1])
    check("Jupiter has a complete table of its own",
          all(d.planet_house_text("Jupiter", h) == d._JUPITER_HOUSE_TEXT[h]
              for h in range(1, 13)))
    check("Venus overrides three houses and falls back to JUPITER's table "
          "elsewhere, per the source's own cross-reference — not the Sun's",
          d.planet_house_text("Venus", 1) == d._VENUS_OVERRIDES[1]
          and d.planet_house_text("Venus", 10) == d._JUPITER_HOUSE_TEXT[10]
          and d.planet_house_text("Venus", 10) != d._BASE_HOUSE_TEXT[10])
    check("Saturn's 1st-house royal/ordinary fallback logic is still "
          "correct, though now unreachable via any transcribed Lagna — "
          "all five royal signs are Bhrigu-covered, which is always "
          "checked first",
          d._SATURN_LAGNA_ROYAL_SIGNS ==
          {"Libra", "Sagittarius", "Capricorn", "Aquarius", "Pisces"}
          and all(d.bhrigu_house_text(sign, "Saturn", 1) is not None
                  for sign in d._SATURN_LAGNA_ROYAL_SIGNS)
          and d.planet_house_text("Saturn", 1) == d._SATURN_HOUSE1_ORDINARY)
    check("Saturn falls back to the Sun's table for every other house",
          d.planet_house_text("Saturn", 7) == d._BASE_HOUSE_TEXT[7])
    check("an out-of-range house is refused",
          _raises(lambda: d.planet_house_text("Sun", 13), ValueError))
    check("an unknown planet is refused",
          _raises(lambda: d.planet_house_text("Rahu", 1), KeyError))

    print("\n2b. Bhrigu per-Lagna house table — all twelve Lagnas, Aries "
          "through Pisces")
    check("bhrigu_house_text() returns the Lagna-specific entry directly",
          d.bhrigu_house_text("Aries", "Sun", 1)
          == d.BHRIGU_LAGNA_HOUSE_TEXT["Aries"]["Sun"][1])
    check("planet_house_text() prefers it over the Brihat Jataka fallback "
          "once a lagna_sign is given",
          d.planet_house_text("Sun", 1, "Aries") == d.bhrigu_house_text("Aries", "Sun", 1)
          and d.planet_house_text("Sun", 1, "Aries") != d._BASE_HOUSE_TEXT[1])
    check("without a lagna_sign, the Brihat Jataka fallback is used as before",
          d.planet_house_text("Sun", 1) == d._BASE_HOUSE_TEXT[1])
    check("all twelve Lagnas are now transcribed, so an unrecognised "
          "Lagna name is the only way left to exercise this fallback, "
          "and it still falls back cleanly, no KeyError",
          d.planet_house_text("Sun", 1, "Nonexistent") == d._BASE_HOUSE_TEXT[1])
    check("this table is the only path that can answer for Rahu/Ketu, and it "
          "does, for the Lagnas it covers",
          d.planet_house_text("Rahu", 5, "Aries") is not None
          and d.planet_house_text("Ketu", 9, "Aries") is not None
          and d.planet_house_text("Rahu", 5, "Taurus") is not None
          and d.planet_house_text("Rahu", 5, "Gemini") is not None
          and d.planet_house_text("Rahu", 5, "Cancer") is not None
          and d.planet_house_text("Rahu", 5, "Leo") is not None
          and d.planet_house_text("Rahu", 5, "Virgo") is not None
          and d.planet_house_text("Rahu", 5, "Libra") is not None
          and d.planet_house_text("Rahu", 5, "Scorpio") is not None
          and d.planet_house_text("Rahu", 5, "Sagittarius") is not None
          and d.planet_house_text("Rahu", 5, "Capricorn") is not None
          and d.planet_house_text("Rahu", 5, "Aquarius") is not None
          and d.planet_house_text("Rahu", 5, "Pisces") is not None)
    check("Rahu/Ketu are still refused without any lagna_sign at all, "
          "not guessed at",
          _raises(lambda: d.planet_house_text("Rahu", 5), KeyError))
    check("Ketu's own documented gap for Pisces (houses 2-4, a real "
          "scan-page loss) still raises KeyError rather than guessing, "
          "since Ketu has no non-Bhrigu fallback table to drop to",
          d.bhrigu_house_text("Pisces", "Ketu", 2) is None
          and d.bhrigu_house_text("Pisces", "Ketu", 3) is None
          and d.bhrigu_house_text("Pisces", "Ketu", 4) is None
          and _raises(lambda: d.planet_house_text("Ketu", 2, "Pisces"), KeyError))
    check("all seven classical grahas have all 12 houses for Aries",
          all(len(d.BHRIGU_LAGNA_HOUSE_TEXT["Aries"][p]) == 12
              for p in ("Sun", "Moon", "Mars", "Mercury", "Venus", "Saturn", "Rahu", "Ketu")))
    check("Jupiter is the one documented gap — 9 of 12 houses (8th/9th/10th "
          "missing, a scan-page loss in the source, not a guess)",
          sorted(d.BHRIGU_LAGNA_HOUSE_TEXT["Aries"]["Jupiter"]) == [1, 2, 3, 4, 5, 6, 7, 11, 12])
    check("bhrigu_house_text() returns None rather than guessing for that gap",
          d.bhrigu_house_text("Aries", "Jupiter", 8) is None
          and d.bhrigu_house_text("Aries", "Jupiter", 9) is None
          and d.bhrigu_house_text("Aries", "Jupiter", 10) is None)
    check("Taurus is the second Lagna transcribed, with its own one-entry "
          "gap: Jupiter's 3rd house, where the source's own text is "
          "internally inconsistent (names Sun, not Jupiter)",
          set(d.BHRIGU_LAGNA_HOUSE_TEXT["Taurus"]) ==
          {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"}
          and all(len(d.BHRIGU_LAGNA_HOUSE_TEXT["Taurus"][p]) == 12
                  for p in ("Sun", "Moon", "Mars", "Mercury", "Venus", "Saturn", "Rahu", "Ketu"))
          and sorted(d.BHRIGU_LAGNA_HOUSE_TEXT["Taurus"]["Jupiter"]) == [1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12])
    check("that Jupiter gap returns None, not a guess, and falls back cleanly",
          d.bhrigu_house_text("Taurus", "Jupiter", 3) is None
          and d.planet_house_text("Jupiter", 3, "Taurus") == d._JUPITER_HOUSE_TEXT[3])
    check("for that gap, planet_house_text() still falls back to the Brihat "
          "Jataka table rather than raising",
          d.planet_house_text("Jupiter", 8, "Aries") == d._JUPITER_HOUSE_TEXT[8])
    check("Gemini is the third Lagna transcribed, with no documented gap — "
          "all nine grahas, all 12 houses",
          set(d.BHRIGU_LAGNA_HOUSE_TEXT["Gemini"]) ==
          {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"}
          and all(len(d.BHRIGU_LAGNA_HOUSE_TEXT["Gemini"][p]) == 12
                  for p in d.BHRIGU_LAGNA_HOUSE_TEXT["Gemini"]))
    check("Cancer is the fourth Lagna transcribed, with no documented gap — "
          "all nine grahas, all 12 houses",
          set(d.BHRIGU_LAGNA_HOUSE_TEXT["Cancer"]) ==
          {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"}
          and all(len(d.BHRIGU_LAGNA_HOUSE_TEXT["Cancer"][p]) == 12
                  for p in d.BHRIGU_LAGNA_HOUSE_TEXT["Cancer"]))
    check("Leo is the fifth Lagna transcribed, with no documented gap — "
          "all nine grahas, all 12 houses",
          set(d.BHRIGU_LAGNA_HOUSE_TEXT["Leo"]) ==
          {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"}
          and all(len(d.BHRIGU_LAGNA_HOUSE_TEXT["Leo"][p]) == 12
                  for p in d.BHRIGU_LAGNA_HOUSE_TEXT["Leo"]))
    check("Virgo is the sixth Lagna transcribed, with no documented gap — "
          "all nine grahas, all 12 houses",
          set(d.BHRIGU_LAGNA_HOUSE_TEXT["Virgo"]) ==
          {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"}
          and all(len(d.BHRIGU_LAGNA_HOUSE_TEXT["Virgo"][p]) == 12
                  for p in d.BHRIGU_LAGNA_HOUSE_TEXT["Virgo"]))
    check("Libra is the seventh Lagna transcribed, with no documented gap — "
          "all nine grahas, all 12 houses",
          set(d.BHRIGU_LAGNA_HOUSE_TEXT["Libra"]) ==
          {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"}
          and all(len(d.BHRIGU_LAGNA_HOUSE_TEXT["Libra"][p]) == 12
                  for p in d.BHRIGU_LAGNA_HOUSE_TEXT["Libra"]))
    check("Scorpio is the eighth Lagna transcribed, with no documented gap — "
          "all nine grahas, all 12 houses",
          set(d.BHRIGU_LAGNA_HOUSE_TEXT["Scorpio"]) ==
          {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"}
          and all(len(d.BHRIGU_LAGNA_HOUSE_TEXT["Scorpio"][p]) == 12
                  for p in d.BHRIGU_LAGNA_HOUSE_TEXT["Scorpio"]))
    check("Sagittarius is the ninth Lagna transcribed, with no documented "
          "gap — all nine grahas, all 12 houses",
          set(d.BHRIGU_LAGNA_HOUSE_TEXT["Sagittarius"]) ==
          {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"}
          and all(len(d.BHRIGU_LAGNA_HOUSE_TEXT["Sagittarius"][p]) == 12
                  for p in d.BHRIGU_LAGNA_HOUSE_TEXT["Sagittarius"]))
    check("Capricorn is the tenth Lagna transcribed, with no documented "
          "gap — all nine grahas, all 12 houses",
          set(d.BHRIGU_LAGNA_HOUSE_TEXT["Capricorn"]) ==
          {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"}
          and all(len(d.BHRIGU_LAGNA_HOUSE_TEXT["Capricorn"][p]) == 12
                  for p in d.BHRIGU_LAGNA_HOUSE_TEXT["Capricorn"]))
    check("Aquarius is the eleventh Lagna transcribed, with no documented "
          "gap — all nine grahas, all 12 houses",
          set(d.BHRIGU_LAGNA_HOUSE_TEXT["Aquarius"]) ==
          {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"}
          and all(len(d.BHRIGU_LAGNA_HOUSE_TEXT["Aquarius"][p]) == 12
                  for p in d.BHRIGU_LAGNA_HOUSE_TEXT["Aquarius"]))
    check("Pisces is the twelfth and final Lagna transcribed, completing "
          "the corpus — its one documented gap is Ketu's 2nd/3rd/4th "
          "houses, a real scan-page loss (the source's own printed pages "
          "jump straight from Ketu's 1st house to its 5th)",
          set(d.BHRIGU_LAGNA_HOUSE_TEXT["Pisces"]) ==
          {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"}
          and all(len(d.BHRIGU_LAGNA_HOUSE_TEXT["Pisces"][p]) == 12
                  for p in ("Sun", "Moon", "Mars", "Mercury", "Jupiter",
                            "Venus", "Saturn", "Rahu"))
          and sorted(d.BHRIGU_LAGNA_HOUSE_TEXT["Pisces"]["Ketu"]) ==
          [1, 5, 6, 7, 8, 9, 10, 11, 12])
    check("bhrigu_house_text() returns None rather than guessing for "
          "that Ketu gap",
          d.bhrigu_house_text("Pisces", "Ketu", 2) is None
          and d.bhrigu_house_text("Pisces", "Ketu", 3) is None
          and d.bhrigu_house_text("Pisces", "Ketu", 4) is None)
    check("all twelve Lagnas of the Bhrigu per-Lagna corpus are now present",
          set(d.BHRIGU_LAGNA_HOUSE_TEXT) ==
          {"Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra",
           "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"})
    check("an unknown Lagna name is simply not found, not an error",
          d.bhrigu_house_text("Nonexistent", "Sun", 1) is None)

    print("\n2c. Bhrigu corpus rulership audit — no entry contradicts fixed "
          "rulership facts")
    check("house -> sign mapping is whole-sign and wraps past Pisces",
          sign_of_house("Aries", 11) == "Aquarius"
          and sign_of_house("Virgo", 1) == "Virgo"
          and sign_of_house("Pisces", 1) == "Pisces"
          and sign_of_house("Pisces", 11) == "Capricorn"
          and sign_of_house("Pisces", 12) == "Aquarius")
    # The audit must be able to fail, or a green run proves nothing: feed it
    # the exact contradictions the first audit found, in the exact words used.
    known_bad = {
        "Aries": {"Mars": {11: "Exalted here — grows income"},          # Aquarius
                  "Jupiter": {6: "Own sign here brings success"}},      # Virgo
        "Taurus": {"Venus": {11: "In its own sign here, grows income"}},  # Pisces
        "Leo": {"Saturn": {12: "Debilitated here — brings heavy expense"}},  # Cancer
        "Virgo": {"Sun": {1: "In its own sign and as Lagna-lord's seat here, "
                             "brings a frail build"},                   # Virgo
                  "Jupiter": {6: "Enemy's sign here (Jupiter rules the 6th), "
                                 "brings humility"}},                   # Saturn's
        "Pisces": {"Sun": {11: "Enemy's sign here (Sun rules the 11th), "
                               "brings growth"}},                       # Saturn's
    }
    audit = rulership_audit(known_bad)
    check("the audit flags each of the seven contradictions it was written for",
          len(audit["violations"]) == 7, "; ".join(audit["violations"]))
    known_good = {
        "Aries": {"Mars": {1: "In its own sign here (Mars rules the 8th here), brings vigour",
                           10: "Exalted here — brings standing"},
                  "Sun": {1: "Exalted and vitalised — confident"}},
        "Taurus": {"Venus": {11: "Exalted here — grows income through hard effort"}},
        "Leo": {"Saturn": {12: "Enemy's sign here (the Moon's) brings heavy expense; "
                               "its aspect on the 9th (debilitated) makes fortune harder"}},
        "Virgo": {"Sun": {1: "In Mercury's sign here (the Lagna lord's), brings a frail build"}},
        "Pisces": {"Sun": {11: "In an enemy's sign here (Saturn rules the 11th), brings growth"}},
    }
    audit = rulership_audit(known_good)
    check("the audit passes correct claims, reads only the leading clause "
          "(a later aspect clause naming a debilitated sign is not the "
          "placement's own dignity), and ignores claim-free entries",
          audit["violations"] == [] and audit["dignity_claims"] == 4,
          "; ".join(audit["violations"]) or f"{audit['dignity_claims']} claims")
    check("Rahu and Ketu entries are outside the audit (vargas.py gives the "
          "nodes no sign dignity)",
          rulership_audit({"Aries": {"Rahu": {9: "Debilitated here — brings loss"},
                                     "Ketu": {3: "Exalted here — brings gain"}}})
          ["dignity_claims"] == 0)

    # Trailing aspect-clause claims: the three the source pages contradicted
    # (pp.270, 292, 389 -- the book calls each one a FRIENDLY aspect), in the
    # words the corpus used, plus correct claims that must stay quiet.
    aspect_bad_in = {
        "Leo": {"Venus": {1: "Enemy's sign brings beauty; its aspect on the 7th "
                             "(own sign) brings success"}},              # Aquarius
        "Virgo": {"Sun": {4: "Friend's sign brings a lack; its aspect on the "
                             "10th (own sign) brings dissatisfaction"}},   # Gemini
        "Scorpio": {"Mercury": {7: "Friend's sign brings success; its aspect on "
                                   "the Lagna (own sign) brings strength"}},  # Scorpio
    }
    audit = rulership_audit(aspect_bad_in)
    check("the audit flags each of the three aspect-clause contradictions it "
          "was extended for", len(audit["aspect_bad"]) == 3
          and audit["aspect_claims"] == 3, "; ".join(audit["aspect_bad"]))
    aspect_good_in = {
        "Leo": {"Venus": {4: "Enemy's sign; its aspect on the 10th (own sign) "
                             "brings gain"},                              # Taurus
                "Jupiter": {8: "Own sign; its aspect on the 12th (a friend's "
                               "sign) brings expense"}},                  # not audited
        "Cancer": {"Sun": {4: "x; its aspect on the 10th (exalted) brings fame"}},
        "Scorpio": {"Mercury": {5: "x; its aspect on the 11th (own sign, exalted) "
                                   "brings income"}},                     # Virgo
    }
    audit = rulership_audit(aspect_good_in)
    check("correct aspect-clause claims pass; friend/enemy stances are not audited",
          audit["aspect_bad"] == [] and audit["aspect_claims"] == 4,
          "; ".join(audit["aspect_bad"]) or f"{audit['aspect_claims']} claims")

    # The nodes get no sign dignity (vargas.py), so an entry must not claim one.
    node_in = {"Aries": {"Rahu": {9: "Debilitated here -- brings loss"},
                         "Ketu": {3: "Exalted here -- brings gain",
                                  4: "Brings deficiency in comfort"}},
               "Pisces": {"Ketu": {10: "Exalted in Jupiter's sign, brings comfort"}}}
    audit = rulership_audit(node_in)
    check("the audit flags every node entry that claims sign dignity, and only "
          "those", len(audit["node_bad"]) == 3, "; ".join(audit["node_bad"]))

    real = rulership_audit(d.BHRIGU_LAGNA_HOUSE_TEXT)
    check("every leading own-sign / exalted / debilitated claim in the real "
          "corpus matches the graha's true rulership for that Lagna and house",
          not real["dignity_bad"], "; ".join(real["dignity_bad"]))
    check("every 'X rules the Nth' / 'as Nth lord' claim in the real corpus "
          "names the true lord of that house from that Lagna",
          not real["lordship_bad"], "; ".join(real["lordship_bad"]))
    check("every own-sign / exalted / debilitated claim in a trailing aspect "
          "clause names a sign the aspecting graha really has that dignity in",
          not real["aspect_bad"], "; ".join(real["aspect_bad"]))
    check("no Rahu or Ketu entry claims a sign dignity (vargas.py gives the "
          "nodes none)", not real["node_bad"], "; ".join(real["node_bad"]))
    check("the aspect walk is not vacuous: it read dozens of claims",
          real["aspect_claims"] > 40, f"{real['aspect_claims']} aspect claims")
    check("the real-corpus walk is not vacuous: it read claims from all "
          "twelve Lagnas, and both claim kinds occur many times over",
          len(real["lagnas"]) == 12 and real["dignity_claims"] > 200
          and real["lordship_claims"] > 100,
          f"{real['dignity_claims']} dignity claims, "
          f"{real['lordship_claims']} lordship claims, "
          f"{len(real['lagnas'])} Lagnas")

    print("\n3. Conjunctions — every pair sharing a sign, and only real pairs")
    conj = d.conjunctions_present(v.chart_view(chart(Sun="Aries", Mercury="Aries")))
    check("Sun conjunct Mercury is reported with its text",
          len(conj) == 1 and set(conj[0]["planets"]) == {"Sun", "Mercury"}
          and conj[0]["sign"] == "Aries" and conj[0]["note"],
          str(conj))
    check("every one of the 21 pairwise conjunctions has text",
          len(d.CONJUNCTION_DELINEATION) == 21
          and all(d.CONJUNCTION_DELINEATION[frozenset({a, b})]
                  for i, a in enumerate(GRAHAS) for b in GRAHAS[i + 1:]))
    # QUIET itself has Mercury and Venus sharing Cancer, so isolating "nothing
    # shares a sign" needs every graha given its own distinct sign.
    no_conj = chart(Sun="Aries", Moon="Taurus", Mars="Gemini", Mercury="Cancer",
                    Jupiter="Leo", Venus="Virgo", Saturn="Libra")
    check("no conjunction is reported when nothing shares a sign",
          d.conjunctions_present(v.chart_view(no_conj)) == [])
    triple = d.conjunctions_present(
        v.chart_view(chart(Sun="Aries", Mercury="Aries", Venus="Aries")))
    check("three grahas sharing a sign report all three underlying pairs",
          len(triple) == 3
          and {frozenset(c["planets"]) for c in triple} == {
              frozenset({"Sun", "Mercury"}), frozenset({"Sun", "Venus"}),
              frozenset({"Mercury", "Venus"})})

    print("\n4. Career significators — the 10th house, from the Lagna and the Moon")
    # Aries Lagna: the 10th sign is Capricorn. Put Saturn (Capricorn's own
    # lord) there as an occupant. The Moon sits in Aquarius (QUIET); the 10th
    # sign from Aquarius, counted inclusively, is Scorpio — occupied in QUIET
    # by the Sun — giving a second, independently-derived reading.
    c = chart(Saturn="Capricorn")
    careers = d.career_significators(v.chart_view(c))
    by_ref = {c["from"]: c for c in careers}
    check("the 10th-from-Lagna occupant is reported with its theme",
          by_ref["Lagna"]["planet"] == "Saturn"
          and by_ref["Lagna"]["role"] == "occupant of the 10th"
          and by_ref["Lagna"]["theme"] == d.CAREER_BY_PLANET["Saturn"],
          str(by_ref.get("Lagna")))
    check("the 10th-from-Moon is read separately, off the Moon's own sign",
          by_ref["Moon"]["planet"] == "Sun"
          and by_ref["Moon"]["role"] == "occupant of the 10th",
          str(by_ref.get("Moon")))
    # Now empty that 10th-from-Moon house so the fallback-to-sign-lord path is
    # actually exercised: Sun moved off Scorpio, leaving no occupant, so the
    # lord of Scorpio (Mars) should be reported instead.
    c2 = chart(Saturn="Capricorn", Sun="Aries")
    by_ref2 = {c["from"]: c for c in d.career_significators(v.chart_view(c2))}
    check("with no occupant in the 10th-from-Moon, the sign lord is used instead",
          by_ref2["Moon"]["planet"] == "Mars"
          and by_ref2["Moon"]["role"] == "lord of the 10th",
          str(by_ref2.get("Moon")))
    check("every classical graha has a career theme",
          set(d.CAREER_BY_PLANET) == set(GRAHAS))
    check("the same planet is not reported twice even if it is both "
          "answers (Lagna and Moon 10th coincide)",
          len({c["planet"] for c in careers}) == len(careers))

    print("\n5. Mahadasha readings — benefic and malefic text, Rahu/Ketu excluded")
    check("every classical graha has both a benefic and a malefic reading",
          all(d.mahadasha_reading(p, True) and d.mahadasha_reading(p, False)
              for p in GRAHAS))
    check("the benefic and malefic readings differ",
          all(d.mahadasha_reading(p, True) != d.mahadasha_reading(p, False)
              for p in GRAHAS))
    check("Rahu and Ketu are explicitly not covered, not silently guessed at",
          d.mahadasha_reading("Rahu", True) is None
          and d.mahadasha_reading("Ketu", False) is None)

    print("\n5b. Antardasha readings — one fixed text per graha, all nine covered")
    check("every one of the nine grahas (including Rahu/Ketu) has a reading",
          all(d.antardasha_reading(p) for p in list(GRAHAS) + ["Rahu", "Ketu"]))
    check("an unknown planet returns None rather than a guess",
          d.antardasha_reading("Pluto") is None)

    print("\n6a. Baladi Avastha — five-fold life-stage within a sign's 30 degrees")
    check("0-6 degrees of an odd sign (Aries) is Bala",
          d.baladi_avastha("Aries", 2.0) == {"state": "Bala", "note": d._AVASTHA_TEXT["Bala"]})
    check("24-30 degrees of an odd sign (Aries) is Mrita",
          d.baladi_avastha("Aries", 27.0)["state"] == "Mrita")
    check("12-18 degrees of an odd sign (Leo) is Yuva",
          d.baladi_avastha("Leo", 15.0)["state"] == "Yuva")
    check("the order reverses in an even sign: 0-6 degrees of Taurus is Mrita",
          d.baladi_avastha("Taurus", 2.0)["state"] == "Mrita")
    check("24-30 degrees of an even sign (Taurus) is Bala",
          d.baladi_avastha("Taurus", 27.0)["state"] == "Bala")
    check("the midpoint (12-18) of an even sign is still Yuva either way",
          d.baladi_avastha("Taurus", 15.0)["state"] == "Yuva")
    check("every one of the five stages has explanatory text",
          all(d._AVASTHA_TEXT[s] for s in d._AVASTHA_ORDER))
    check("a degree at or past 30, or negative, is refused",
          _raises(lambda: d.baladi_avastha("Aries", 30.0), ValueError)
          and _raises(lambda: d.baladi_avastha("Aries", -1.0), ValueError))

    print("\n6. delineate() — the one entry point, against a hand-built chart")
    full = d.delineate(chart(Sun="Aries", Mercury="Aries"))
    try:
        blob = json.dumps(full)
        check("delineate() is JSON-serialisable", True, f"{len(blob)} bytes")
    except TypeError as exc:
        check("delineate() is JSON-serialisable", False, str(exc))
    check("it covers all seven classical grahas, no more and no less",
          set(full["planets"]) == set(GRAHAS))
    check("every planet entry carries a sign, house, dignity, house text and avastha",
          all({"sign", "house", "dignity", "house_text", "avastha"} <= set(p)
              for p in full["planets"].values()))
    check("the Sun-Mercury conjunction this chart was built with shows up",
          any(set(c["planets"]) == {"Sun", "Mercury"} for c in full["conjunctions"]))
    check("the career list is non-empty and every entry names a theme",
          bool(full["career"]) and all(c["theme"] for c in full["career"]))
    check("this chart's Lagna is Aries, so the Sun's house text comes from "
          "the Bhrigu per-Lagna table, not the Brihat Jataka fallback",
          full["lagna"] == "Aries"
          and full["planets"]["Sun"]["house_text"]
          == d.BHRIGU_LAGNA_HOUSE_TEXT["Aries"]["Sun"][full["planets"]["Sun"]["house"]])
    tropical = chart()
    tropical["meta"]["zodiac"] = "tropical"
    check("it refuses a tropical chart, the same way vargas.py does",
          _raises(lambda: d.delineate(tropical), v.VargaError))

    print("\n7. Against a chart built by chart_service itself")
    try:
        from app.chart_service import BirthData, build

        session = build(BirthData(
            name="Native", date="1986-08-19", time="11:59",
            latitude=26.26, longitude=82.07, timezone="Asia/Kolkata",
            place="Sultanpur, Uttar Pradesh, India", zodiac="sidereal",
            ayanamsa="lahiri", house_system="Whole Sign"))

        live = d.delineate(session)
        check("a real ChartSession is read without adaptation", True,
              f"Lagna {live['lagna']}, {len(live['career'])} career signal(s)")
        json.dumps(live)
        check("a real chart's delineation is JSON-serialisable", True)
        check("the bundle dict works too, and agrees",
              json.dumps(d.delineate(session.bundle)) == json.dumps(live))
        check("every planet in the real chart resolves to one of the seven "
              "known dignity states",
              all(p["dignity"]["state"] in d.DIGNITY_DELINEATION[name]
                  for name, p in live["planets"].items()))
    except Exception as exc:                          # pragma: no cover
        check("real charts build and delineate", False, f"{type(exc).__name__}: {exc}")

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("delineation — classical delineation text: all green")
    return 0


def _raises(fn, exc_type) -> bool:
    try:
        fn()
        return False
    except exc_type:
        return True
    except Exception:
        return False


if __name__ == "__main__":
    raise SystemExit(main())
