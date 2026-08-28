"""Classical delineation text: dignity, house, career and conjunction lookups.

A pure unit test, in the shape `test_vargas.py` uses: minimal chart bundles,
driven straight against `app.astro.delineation`, finishing against a real
chart built by `chart_service` so the bundle shape is checked against the real
producer.

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.test_delineation
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.astro import delineation as d
from app.astro import vargas as v
from app.chart_service import SIGNS, dms, sign_of

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
    check("Saturn's 1st house depends on the Lagna sign",
          d.planet_house_text("Saturn", 1, "Capricorn") == d._SATURN_HOUSE1_ROYAL
          and d.planet_house_text("Saturn", 1, "Taurus") == d._SATURN_HOUSE1_ORDINARY)
    check("Saturn falls back to the Sun's table for every other house",
          d.planet_house_text("Saturn", 7) == d._BASE_HOUSE_TEXT[7])
    check("an out-of-range house is refused",
          _raises(lambda: d.planet_house_text("Sun", 13), ValueError))
    check("an unknown planet is refused",
          _raises(lambda: d.planet_house_text("Rahu", 1), KeyError))

    print("\n2b. Bhrigu per-Lagna house table — Aries, the first Lagna transcribed")
    check("bhrigu_house_text() returns the Lagna-specific entry directly",
          d.bhrigu_house_text("Aries", "Sun", 1)
          == d.BHRIGU_LAGNA_HOUSE_TEXT["Aries"]["Sun"][1])
    check("planet_house_text() prefers it over the Brihat Jataka fallback "
          "once a lagna_sign is given",
          d.planet_house_text("Sun", 1, "Aries") == d.bhrigu_house_text("Aries", "Sun", 1)
          and d.planet_house_text("Sun", 1, "Aries") != d._BASE_HOUSE_TEXT[1])
    check("without a lagna_sign, the Brihat Jataka fallback is used as before",
          d.planet_house_text("Sun", 1) == d._BASE_HOUSE_TEXT[1])
    check("a Lagna not yet transcribed (e.g. Taurus) falls back cleanly, no KeyError",
          d.planet_house_text("Sun", 1, "Taurus") == d._BASE_HOUSE_TEXT[1])
    check("this table is the only path that can answer for Rahu/Ketu, and it "
          "does, for the Lagna it covers",
          d.planet_house_text("Rahu", 5, "Aries") is not None
          and d.planet_house_text("Ketu", 9, "Aries") is not None)
    check("Rahu/Ketu are still refused without a covering Lagna, not guessed at",
          _raises(lambda: d.planet_house_text("Rahu", 5, "Taurus"), KeyError)
          and _raises(lambda: d.planet_house_text("Rahu", 5), KeyError))
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
    check("for that gap, planet_house_text() still falls back to the Brihat "
          "Jataka table rather than raising",
          d.planet_house_text("Jupiter", 8, "Aries") == d._JUPITER_HOUSE_TEXT[8])
    check("an unknown Lagna name is simply not found, not an error",
          d.bhrigu_house_text("Nonexistent", "Sun", 1) is None)

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
