"""Divisional charts (vargas) and the classical chart yogas.

A pure unit test: no server, no database, no network. It builds minimal chart
bundles of the shape `chart_service` produces and drives `app.astro.vargas`
directly, then finishes by running the same functions against a real chart so
the bundle shape is checked against the real producer and not just against this
file's idea of it.

The properties that matter:

* **The D9 Navamsa is asserted against longitudes worked out by hand**, one at
  a time, spanning movable, fixed and dual signs. Each expected value records
  the arithmetic that produced it. Navamsa is the division every marriage
  reading rests on, and an off-by-one in the start sign would be invisible in
  the output and wrong in every chart.
* **A yoga must need every limb of its condition.** The Pancha Mahapurusha
  checks in section 8 are the sharp end of this: a planet with the dignity but
  no kendra, and a planet in a kendra with no dignity, must both form nothing.
  Half a condition silently passing is the failure that would put a fabricated
  yoga in a paid reading.
* **Cancellations fire when they should and stay silent when they should not**,
  for Neecha Bhanga and for Kemadruma alike.

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.test_vargas
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.astro import vargas as v
from app.chart_service import DOMICILE, MODALITY, SIGNS, dms, sign_of

failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


# --------------------------------------------------------------------------
# Chart fixtures — the same keys `chart_service._normalise` emits, and no more
# than `vargas` actually reads.
# --------------------------------------------------------------------------

GRAHAS = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")

# A deliberately quiet arrangement for an Aries Lagna: no Raja yoga, no Dhana
# yoga, no Mahapurusha, no debilitation, and the Moon flanked so Kemadruma
# cannot form either. Found by sweeping placements until nothing at all formed,
# so that every positive test below can move one planet and know that the yoga
# it sees is the one it moved the planet for.
QUIET = {
    "Sun": "Scorpio", "Moon": "Aquarius", "Mars": "Pisces", "Mercury": "Cancer",
    "Jupiter": "Sagittarius", "Venus": "Cancer", "Saturn": "Leo",
}


def lon(sign: str, degree: float = 5.0) -> float:
    return SIGNS.index(sign) * 30.0 + degree


def _obj(name: str, longitude: float, retrograde: bool = False) -> dict:
    longitude %= 360.0
    return {
        "name": name, "kind": "planet", "longitude": longitude,
        "sign": sign_of(longitude), "degree": longitude % 30.0,
        "position": f"{sign_of(longitude)} {dms(longitude % 30.0)}",
        "retrograde": retrograde,
    }


def chart(asc: str | float = "Aries", *, zodiac: str = "sidereal",
          node: str | float | None = None, **where: str | float) -> dict:
    """A bundle with the seven grahas and the Lagna.

    Placements are given as a sign name (taken at 5° of it) or as a raw
    sidereal longitude; anything not named falls back to QUIET.
    """
    placements = dict(QUIET)
    placements.update(where)

    def place(value: str | float) -> float:
        return lon(value) if isinstance(value, str) else float(value)

    objects = {"ASC": _obj("ASC", place(asc))}
    for graha in GRAHAS:
        objects[graha] = _obj(graha, place(placements[graha]))
    if node is not None:
        objects["True Node"] = _obj("True Node", place(node))
    return {
        "meta": {"zodiac": zodiac, "name": "Native", "ayanamsa": "lahiri"},
        "birth": {"name": "Native"},
        "objects": objects,
    }


def formed(c: dict) -> list[str]:
    """The keys of the yogas that actually formed, sorted."""
    return sorted(y["key"] for y in v.yogas(c)["yogas"])


def entry(c: dict, key: str) -> dict | None:
    """One entry out of the full list, formed or not."""
    return next((y for y in v.yogas(c)["all"] if y["key"] == key), None)


def main() -> int:
    print("\n1. The division rules are internally consistent")
    # _check_divisions() already ran at import; its properties are asserted here
    # too so a failure names itself rather than arriving as an ImportError.
    check("six divisions are described and each has a rule function",
          set(v.DIVISIONS) == set(v._DIVISION_RULES) == set(v.DEFAULT_DIVISIONS),
          str(sorted(v.DIVISIONS)))
    check("the part counts are 1/3/7/9/10/12",
          [v.DIVISIONS[d]["parts"] for d in ("D1", "D3", "D7", "D9", "D10", "D12")]
          == [1, 3, 7, 9, 10, 12])
    check("every part arc multiplies back to 30°",
          all(abs(m["arc"] * m["parts"] - 30.0) < 1e-9 for m in v.DIVISIONS.values()))
    check("exaltation and debilitation are seven signs apart for every graha",
          all(_seven_apart(v.EXALTATION[g], v.DEBILITATION[g]) for g in GRAHAS),
          str({g: (v.EXALTATION[g], v.DEBILITATION[g]) for g in GRAHAS
               if not _seven_apart(v.EXALTATION[g], v.DEBILITATION[g])}))
    check("own signs invert chart_service's DOMICILE exactly",
          all(DOMICILE[s] == g for g in GRAHAS for s in v.OWN_SIGNS[g])
          and sum(len(v.OWN_SIGNS[g]) for g in GRAHAS) == 12)
    check("every graha's moolatrikona range is inside one sign and non-empty",
          all(s in SIGNS and 0.0 <= a < b <= 30.0
              for s, a, b in v.MOOLATRIKONA.values()))
    check("the graha drishti table gives Mars 4/7/8, Jupiter 5/7/9, Saturn 3/7/10",
          v.GRAHA_DRISHTI == {"Mars": (4, 7, 8), "Jupiter": (5, 7, 9),
                              "Saturn": (3, 7, 10)})
    check("every planet aspects the 7th",
          all(7 in v.GRAHA_DRISHTI.get(g, v.DEFAULT_DRISHTI) for g in GRAHAS))
    check("the module publishes what it deliberately does not implement",
          len(v.NOT_IMPLEMENTED) >= 8
          and all(len(why) > 30 for _, why in v.NOT_IMPLEMENTED),
          f"{len(v.NOT_IMPLEMENTED)} entries")

    print("\n2. D9 Navamsa, computed by hand from the classical rule")
    # Movable signs count from themselves, fixed from the 9th, dual from the
    # 5th; each navamsa is 3°20′. Every expectation below is that arithmetic
    # carried out longhand, and the source of each is stated.
    navamsa_cases = [
        # Aries 1° — movable, 1st navamsa, counted from Aries itself.
        (1.0, "Aries"),
        # Aries 25° — movable, 25/3°20′ = the 8th navamsa; Aries + 7 = Scorpio.
        (25.0, "Scorpio"),
        # Taurus 10° (lon 40) — fixed, so it counts from the 9th from Taurus,
        # which is Capricorn; 10° is the 4th navamsa; Capricorn + 3 = Aries.
        (40.0, "Aries"),
        # Leo 15° (lon 135) — fixed, counts from the 9th from Leo = Aries; 15°
        # is the 5th navamsa; Aries + 4 = Leo. BPHS names the 5th navamsa of a
        # fixed sign as its vargottama navamsa, and this is it.
        (135.0, "Leo"),
        # Leo 16°40′ (lon 136.67) — the next navamsa along, the 6th;
        # Aries + 5 = Virgo. Chosen to sit just over the boundary above.
        (136.67, "Virgo"),
        # Gemini 5° (lon 65) — dual, counts from the 5th from Gemini = Libra;
        # 5° is the 2nd navamsa; Libra + 1 = Scorpio.
        (65.0, "Scorpio"),
        # Sagittarius 29° (lon 269) — dual, counts from the 5th from Sagittarius
        # = Aries; 29° is the 9th navamsa; Aries + 8 = Sagittarius. The
        # vargottama navamsa of a dual sign is its 9th, and this is it.
        (269.0, "Sagittarius"),
        # Capricorn 3°20′ (lon 273.34) — movable, counts from Capricorn; the
        # 2nd navamsa; Capricorn + 1 = Aquarius.
        (273.34, "Aquarius"),
        # Pisces 27° (lon 357) — dual, counts from the 5th from Pisces = Cancer;
        # the 9th navamsa; Cancer + 8 = Pisces.
        (357.0, "Pisces"),
        # Scorpio 0° (lon 210) — fixed, counts from the 9th from Scorpio =
        # Cancer; the 1st navamsa; Cancer itself.
        (210.0, "Cancer"),
        # Libra 20° (lon 200) — movable, counts from Libra; 20° is the 7th
        # navamsa; Libra + 6 = Aries.
        (200.0, "Aries"),
    ]
    wrong = [(l, v.navamsa_sign(l), e) for l, e in navamsa_cases
             if v.navamsa_sign(l) != e]
    check(f"{len(navamsa_cases)} hand-worked navamsa longitudes",
          not wrong, str(wrong[:3]))
    modalities = {MODALITY[SIGNS[int(l // 30) % 12]] for l, _ in navamsa_cases}
    check("they span movable, fixed and dual signs",
          modalities == {"Cardinal", "Fixed", "Mutable"}, str(sorted(modalities)))
    check("navamsa_sign() and varga_sign(.., 'D9') agree",
          all(v.navamsa_sign(x / 7.0) == v.varga_sign(x / 7.0, "D9")
              for x in range(2521)))

    print("\n3. The other divisions, also worked by hand")
    # D3 Drekkana — 1st third the sign itself, 2nd the 5th from it, 3rd the 9th.
    d3 = [(5.0, "Aries"),          # Aries 5°, 1st drekkana
          (15.0, "Leo"),           # Aries 15°, 2nd drekkana: the 5th from Aries
          (25.0, "Sagittarius"),   # Aries 25°, 3rd drekkana: the 9th from Aries
          (55.0, "Capricorn")]     # Taurus 25°, 3rd: the 9th from Taurus
    # D7 Saptamsa (4°17′08″ each) — odd signs from themselves, even from the 7th.
    d7 = [(2.0, "Aries"),          # Aries 2°, 1st saptamsa
          (29.0, "Libra"),         # Aries 29°, 7th saptamsa: Aries + 6
          (30.0, "Scorpio"),       # Taurus 0°: even sign, the 7th from Taurus
          (59.0, "Taurus"),        # Taurus 29°, 7th saptamsa: Scorpio + 6
          (65.0, "Cancer"),        # Gemini 5°, 2nd saptamsa: Gemini + 1
          (95.0, "Aquarius")]      # Cancer 5°, 2nd: (7th from Cancer) + 1
    # D10 Dasamsa (3° each) — odd signs from themselves, even from the 9th.
    d10 = [(5.0, "Taurus"),        # Aries 5°, 2nd dasamsa: Aries + 1
           (29.0, "Capricorn"),    # Aries 29°, 10th dasamsa: Aries + 9
           (30.0, "Capricorn"),    # Taurus 0°: even sign, the 9th from Taurus
           (59.0, "Libra"),        # Taurus 29°, 10th: Capricorn + 9
           (136.0, "Capricorn"),   # Leo 16°, 6th dasamsa: Leo + 5
           (152.0, "Taurus")]      # Virgo 2°: even sign, the 9th from Virgo
    # D12 Dwadasamsa (2°30′ each) — always counted from the sign itself.
    d12 = [(5.0, "Gemini"),        # Aries 5°, 3rd dwadasamsa: Aries + 2
           (29.0, "Pisces"),       # Aries 29°, 12th: Aries + 11
           (31.0, "Taurus"),       # Taurus 1°, 1st: Taurus itself
           (236.0, "Virgo")]       # Scorpio 26°, 11th: Scorpio + 10
    for division, cases in (("D3", d3), ("D7", d7), ("D10", d10), ("D12", d12)):
        bad = [(l, v.varga_sign(l, division), e) for l, e in cases
               if v.varga_sign(l, division) != e]
        check(f"{len(cases)} hand-worked {division} "
              f"{v.DIVISIONS[division]['name']} longitudes", not bad, str(bad[:2]))

    # D10 and D12 are the two that a naive "continuous walk from Aries"
    # implementation gets wrong, so the difference is asserted rather than
    # trusted: 0° Taurus is Capricorn in D10 and Taurus in D12, and a
    # continuous walk would give Aquarius and Aries.
    check("D10 does not reduce to a continuous walk from Aries",
          v.varga_sign(30.0, "D10") == "Capricorn" != SIGNS[(1 * 10) % 12])
    check("D12 does not reduce to a continuous walk from Aries",
          v.varga_sign(30.0, "D12") == "Taurus" != SIGNS[(1 * 12) % 12])
    check("D3 does not reduce to a continuous walk from Aries",
          v.varga_sign(10.0, "D3") == "Leo" != SIGNS[(0 * 3 + 1) % 12])

    print("\n4. Every division splits every sign the way it says it does")
    for division, meta in v.DIVISIONS.items():
        parts = meta["parts"]
        distinct_ok, valid_ok, cover = True, True, [0] * 12
        for index, sign in enumerate(SIGNS):
            landed = []
            for p in range(parts):
                # A point comfortably inside part p of this sign.
                where = index * 30.0 + (p + 0.5) * (30.0 / parts)
                got = v.varga_sign(where, division)
                valid_ok &= got in SIGNS
                landed.append(got)
                cover[SIGNS.index(got)] += 1
            distinct_ok &= len(set(landed)) == parts
        check(f"{division} gives {parts} distinct sign(s) per rashi",
              distinct_ok and valid_ok)
        check(f"{division} covers all twelve signs evenly",
              len(set(cover)) == 1 and cover[0] == parts, str(cover))

    # A dense sweep of the whole zodiac: nothing may fall outside the twelve
    # signs, and no boundary may throw. 0.01° steps put ~333 samples in the
    # narrowest part (D12's 2°30′) and 36000 samples overall per division.
    escaped = []
    for division in v.DIVISIONS:
        for step in range(36000):
            got = v.varga_sign(step / 100.0, division)
            if got not in SIGNS:
                escaped.append((division, step / 100.0, got))
                break
    check("a 0.01° sweep of the zodiac never leaves the twelve signs",
          not escaped, str(escaped[:3]))
    check("a longitude past 360° wraps rather than escaping",
          v.varga_sign(361.0, "D9") == v.varga_sign(1.0, "D9")
          and v.varga_sign(-359.0, "D9") == v.varga_sign(1.0, "D9"))
    try:
        v.varga_sign(10.0, "D16")
        check("an unimplemented division is refused", False, "no error raised")
    except v.VargaError as exc:
        check("an unimplemented division is refused", "D16" in str(exc), str(exc)[:60])

    print("\n5. A divisional chart off a bundle: signs, houses and the varga Lagna")
    base = chart()
    for division in v.DEFAULT_DIVISIONS:
        d = v.divisional_chart(base, division)
        positions = d["positions"]
        ok_signs = all(p["sign"] in SIGNS for p in positions.values())
        ok_houses = all(1 <= p["house"] <= 12 for p in positions.values())
        check(f"{division}: every body lands in a valid sign and house 1..12",
              ok_signs and ok_houses)
        check(f"{division}: the varga Lagna is present and holds the 1st house",
              d["lagna"]["sign"] in SIGNS
              and positions["Lagna"]["house"] == 1
              and d["houses"][0]["sign"] == d["lagna"]["sign"],
              d["lagna"]["sign"])
        check(f"{division}: twelve houses, consecutive signs from the varga Lagna",
              [h["sign"] for h in d["houses"]]
              == [SIGNS[(SIGNS.index(d["lagna"]["sign"]) + i) % 12] for i in range(12)])
        check(f"{division}: every graha appears in exactly one house's occupants",
              sorted(n for h in d["houses"] for n in h["occupants"])
              == sorted(GRAHAS))
    check("D1 reproduces the rashi chart exactly",
          all(p["sign"] == p["rashi_sign"]
              for p in v.divisional_chart(base, "D1")["positions"].values()))
    check("divisional_charts() returns one entry per requested division",
          set(v.divisional_charts(base)) == set(v.DEFAULT_DIVISIONS))
    with_node = chart(node="Gemini")
    check("Rahu and Ketu ride along when the bundle carries a node, 180° apart",
          {"Rahu", "Ketu"} <= set(v.divisional_chart(with_node, "D9")["positions"])
          and v.divisional_chart(with_node, "D1")["positions"]["Ketu"]["sign"]
          == "Sagittarius")
    check("a bundle with no node simply omits them",
          "Rahu" not in v.divisional_chart(base, "D9")["positions"])

    print("\n6. Vargottama — the positive and the negative case")
    # Sagittarius 29° is the 9th navamsa of a dual sign, which is Sagittarius
    # itself; Aries 25° is the 8th navamsa of a movable sign, which is Scorpio.
    vg = v.vargottama(chart(Sun=269.0, Moon=25.0))
    check("a planet on its own navamsa is reported vargottama",
          "Sun" in vg["planets"] and vg["detail"]["Sun"]["vargottama"]
          and vg["detail"]["Sun"]["navamsa_sign"] == "Sagittarius",
          str(vg["detail"]["Sun"]))
    check("a planet whose navamsa differs is NOT reported vargottama",
          "Moon" not in vg["planets"]
          and vg["detail"]["Moon"]["vargottama"] is False
          and vg["detail"]["Moon"]["rashi_sign"] == "Aries"
          and vg["detail"]["Moon"]["navamsa_sign"] == "Scorpio",
          str(vg["detail"]["Moon"]))
    check("the note names the vargottama planets", "Sun" in vg["note"], vg["note"][:60])
    none = v.vargottama(chart(Sun=25.0, Moon=25.0, Mars=25.0, Mercury=25.0,
                              Jupiter=25.0, Venus=25.0, Saturn=25.0))
    check("a chart with no vargottama planet says so plainly",
          none["planets"] == [] and "No planet" in none["note"])
    # The three navamsas BPHS names vargottama, checked as longitudes rather
    # than through the rule that produced them: 1st of a movable sign, 5th of a
    # fixed sign, 9th of a dual sign.
    named = [(1.0, "Aries"),          # Aries 1°, movable, 1st navamsa
             (44.0, "Taurus"),        # Taurus 14°, fixed, 5th navamsa
             (88.0, "Gemini")]        # Gemini 28°, dual, 9th navamsa
    check("the classical vargottama navamsas are movable-1st, fixed-5th, dual-9th",
          all(v.navamsa_sign(l) == e for l, e in named),
          str([(l, v.navamsa_sign(l)) for l, _ in named]))

    print("\n7. Varga strength is a count, and says so")
    vs = v.varga_strength(chart(Sun="Aries", Saturn="Aquarius"))
    sun = vs["planets"]["Sun"]
    check("an exalted Sun is counted dignified in D1",
          sun["rashi_dignity"] == "exaltation"
          and sun["divisions"][0]["state"] == "exalted", str(sun["divisions"][0]))
    check("the count never exceeds the number of divisions counted",
          all(p["dignified_count"] + p["debilitated_count"] <= p["counted_divisions"]
              for p in vs["planets"].values()))
    check("all seven grahas are counted", set(vs["planets"]) == set(GRAHAS))
    check("it refuses to call itself Vimsopaka Bala",
          "not Vimsopaka" in vs["method_note"] and "not Shadbala" in vs["method_note"])
    deb = v.varga_strength(chart(Sun="Libra"))["planets"]["Sun"]
    check("a debilitated Sun is counted debilitated, not dignified",
          deb["rashi_dignity"] == "debilitation" and deb["debilitated_count"] >= 1,
          f"{deb['dignified_count']}/{deb['debilitated_count']}")

    print("\n8. Pancha Mahapurusha needs BOTH the dignity and the kendra")
    # Mars exalted in Capricorn, which is the 10th from an Aries Lagna.
    ruchaka = entry(chart(Mars="Capricorn"), "ruchaka")
    check("Ruchaka forms on exalted Mars in a kendra",
          ruchaka is not None and ruchaka["planets"] == ["Mars"]
          and ruchaka["strength"] == "exaltation" and ruchaka["house"] == 10,
          ruchaka["condition"] if ruchaka else "absent")
    # The SAME exalted Mars, moved to a Taurus Lagna, where Capricorn is the
    # 9th — a trikona, not a kendra. This is the assertion that matters most.
    check("the dignity alone does NOT form it (exalted Mars in the 9th)",
          entry(chart(asc="Taurus", Mars="Capricorn"), "ruchaka") is None,
          str(formed(chart(asc="Taurus", Mars="Capricorn"))))
    # Mars in Libra is the 7th from an Aries Lagna — a kendra, no dignity.
    check("the kendra alone does NOT form it (Mars in Libra in the 7th)",
          entry(chart(Mars="Libra"), "ruchaka") is None,
          str(formed(chart(Mars="Libra"))))
    check("nor does a debilitated Mars in a kendra (Cancer, the 4th)",
          entry(chart(Mars="Cancer"), "ruchaka") is None)
    # Saturn in its own Aquarius in the 10th from a Taurus Lagna. Below 20° it
    # is also moolatrikona, above it is plain own sign; both form Sasa and the
    # reported strength differs, which is the classical ranking.
    sasa_mt = entry(chart(asc="Taurus", Saturn=lon("Aquarius", 5.0)), "sasa")
    sasa_own = entry(chart(asc="Taurus", Saturn=lon("Aquarius", 25.0)), "sasa")
    check("Sasa forms on own-sign Saturn in a kendra, at either degree",
          sasa_mt is not None and sasa_own is not None,
          f"{sasa_mt and sasa_mt['strength']} / {sasa_own and sasa_own['strength']}")
    check("moolatrikona is reported above plain own sign",
          sasa_mt["strength"] == "moolatrikona" and sasa_own["strength"] == "own sign")
    # Every one of the five, each from its own planet. Mercury needs a Gemini
    # Lagna: its own signs are Gemini and Virgo, which are the 3rd and 6th from
    # an Aries Lagna and neither is a kendra, but Virgo is the 4th from Gemini.
    five = {
        "ruchaka": chart(Mars="Capricorn"),                     # exalted, 10th
        "bhadra": chart(asc="Gemini", Mercury="Virgo"),         # own, 4th
        "hamsa": chart(Jupiter="Cancer", Moon="Leo"),           # exalted, 4th
        "malavya": chart(Venus="Libra"),                        # own, 7th
        "sasa": chart(asc="Taurus", Saturn="Aquarius"),         # own, 10th
    }
    missing = [k for k, c in five.items() if entry(c, k) is None]
    check("all five Mahapurusha yogas can be formed", not missing, str(missing))
    check("each is attributed to its own planet",
          all(entry(five[k], k)["planets"] == [p] for k, p in
              (("ruchaka", "Mars"), ("bhadra", "Mercury"), ("hamsa", "Jupiter"),
               ("malavya", "Venus"), ("sasa", "Saturn"))))
    check("the Lagna is the reference by default, as the constant says",
          v.MAHAPURUSHA_KENDRA_FROM == "Lagna"
          and entry(chart(Mars="Capricorn"), "ruchaka")["kendra_from"] == "the Lagna")

    print("\n9. Gaja Kesari — Jupiter in a kendra from the Moon")
    gk = entry(chart(Moon="Aries", Jupiter="Cancer"), "gaja_kesari")
    check("forms with Jupiter in the 4th from the Moon",
          gk is not None and gk["distance_from_moon"] == 4
          and sorted(gk["planets"]) == ["Jupiter", "Moon"],
          gk["condition"] if gk else "absent")
    check("does NOT form with Jupiter in the 3rd from the Moon",
          entry(chart(Moon="Aries", Jupiter="Gemini"), "gaja_kesari") is None)
    check("does NOT form with Jupiter in the 5th from the Moon",
          entry(chart(Moon="Aries", Jupiter="Leo"), "gaja_kesari") is None)
    check("forms from the Moon, not the Lagna — Aries Lagna, Moon in Leo, "
          "Jupiter in Scorpio is the 8th from the Lagna and the 4th from the Moon",
          entry(chart(Moon="Leo", Jupiter="Scorpio"), "gaja_kesari") is not None)
    conj = entry(chart(Moon="Aries", Jupiter="Aries"), "gaja_kesari")
    check("Jupiter with the Moon counts as the 1st, a kendra",
          conj is not None and conj["distance_from_moon"] == 1)
    weak = entry(chart(Moon="Aries", Jupiter="Capricorn"), "gaja_kesari")
    check("a debilitated Jupiter still forms it but carries the caveat",
          weak is not None and weak["jupiter_dignity"] == "debilitation"
          and any("debilitated" in c for c in weak["caveats"]),
          str(weak["caveats"]) if weak else "absent")

    print("\n10. Neecha Bhanga — cancellation, and the absence of it")
    # Sun debilitated in Libra in the 7th from an Aries Lagna. Venus rules
    # Libra and sits in Cancer, the 4th — a kendra from the Lagna, which is the
    # first classical cancellation condition.
    nb = entry(chart(Sun="Libra", Venus="Cancer"), "neecha_bhanga_raja")
    check("a debilitated Sun with its dispositor in a kendra is cancelled",
          nb is not None and nb["cancelled"] and nb["planets"] == ["Sun"]
          and nb["dispositor"] == "Venus",
          nb["cancellations"][0] if nb else "absent")
    check("and rises to a Raja Yoga because the Sun holds the 7th, a kendra",
          nb["raja_yoga"] and nb["house"] == 7 and nb["formed"])
    # The same debilitated Sun with Venus and Saturn kept out of every kendra
    # from the Lagna and from the Moon, out of aspect to the Sun, and with the
    # Sun's navamsa (Scorpio) not its exaltation.
    plain = entry(chart(Sun="Libra", Venus="Scorpio", Saturn="Aquarius",
                        Moon="Gemini"), "neecha")
    check("with no cancellation available it is reported as a plain debilitation",
          plain is not None and plain["cancelled"] is False
          and plain["formed"] is False and plain["cancellations"] == [],
          plain["note"][:70] if plain else "absent")
    check("the uncancelled case does not reach the formed list",
          "neecha" not in formed(chart(Sun="Libra", Venus="Scorpio",
                                       Saturn="Aquarius", Moon="Gemini")))
    check("a chart with nothing debilitated produces no Neecha entry at all",
          entry(chart(), "neecha") is None and entry(chart(), "neecha_bhanga") is None)
    # The Moon is the one case where conditions 2 and 4 cannot be tested at
    # all: Scorpio is nobody's exaltation sign. That must be reported, not
    # silently skipped.
    moon_deb = entry(chart(Moon="Scorpio"), "neecha") or \
        entry(chart(Moon="Scorpio"), "neecha_bhanga") or \
        entry(chart(Moon="Scorpio"), "neecha_bhanga_raja")
    check("a debilitated Moon reports that Scorpio has no exaltation lord",
          moon_deb is not None and moon_deb["exaltation_lord"] is None
          and moon_deb["exaltation_lord_available"] is False,
          str(moon_deb["debilitation_sign"]) if moon_deb else "absent")
    # Cancellation by exaltation in the navamsa, on its own. Saturn debilitated
    # in Aries; Saturn at Aries 25° takes the 8th navamsa of a movable sign,
    # Aries + 7 = Scorpio... so pick the navamsa that IS Libra: Aries 20°
    # is the 7th navamsa, Aries + 6 = Libra, Saturn's exaltation.
    check("Aries 20° really does take a Libra navamsa",
          v.navamsa_sign(20.0) == "Libra", v.navamsa_sign(20.0))
    nav = entry(chart(Saturn=20.0, Moon="Gemini", Mars="Taurus", Venus="Scorpio"),
                "neecha_bhanga_raja")
    check("exaltation in the navamsa cancels on its own",
          nav is not None and any("navamsa" in c for c in nav["cancellations"]),
          str(nav["cancellations"]) if nav else "absent")
    check("the retrograde and mutual-kendra cancellations are documented as absent",
          any("retrogression" in rule for rule, _ in v.NOT_IMPLEMENTED)
          and any("mutual kendras" in rule for rule, _ in v.NOT_IMPLEMENTED))

    print("\n11. Dhana and Raja yogas — lords in mutual association")
    # Aries Lagna: 2nd Taurus (Venus), 5th Leo (Sun), 9th Sagittarius (Jupiter),
    # 11th Aquarius (Saturn). Venus and the Sun placed together in Gemini.
    dh = [y for y in v.yogas(chart(Sun="Gemini", Venus="Gemini"))["yogas"]
          if y["key"] == "dhana"]
    pair = next((y for y in dh if sorted(y["planets"]) == ["Sun", "Venus"]), None)
    check("the 2nd and 5th lords conjunct form a Dhana yoga",
          pair is not None and pair["association"] == "conjunction"
          and sorted(pair["houses"]) == [2, 5],
          pair["condition"] if pair else "absent")
    check("no Dhana yoga in the quiet chart", not [
        y for y in v.yogas(chart())["yogas"] if y["key"] == "dhana"],
        str(formed(chart())))
    # Aries Lagna: 4th lord is the Moon, 5th lord the Sun; together in Gemini.
    rj = [y for y in v.yogas(chart(Sun="Gemini", Moon="Gemini"))["yogas"]
          if y["key"] == "raja" and sorted(y["planets"]) == ["Moon", "Sun"]]
    check("a kendra lord conjunct a trikona lord forms a Raja yoga",
          len(rj) == 1 and rj[0]["kendra_houses"] == [4]
          and rj[0]["trikona_houses"] == [5],
          rj[0]["condition"] if rj else "absent")
    check("no Raja yoga in the quiet chart", not [
        y for y in v.yogas(chart())["yogas"] if y["key"] == "raja"])
    # Parivartana: Aries Lagna, Moon (4th lord, Cancer) in Leo and the Sun
    # (5th lord, Leo) in Cancer — each in the other's sign.
    ex = [y for y in v.yogas(chart(Moon="Leo", Sun="Cancer"))["yogas"]
          if y["key"] == "raja" and sorted(y["planets"]) == ["Moon", "Sun"]]
    check("an exchange of signs also forms it, and is graded strongest",
          len(ex) == 1 and ex[0]["association"] == "exchange"
          and ex[0]["strength"].startswith("strong"),
          ex[0]["strength"] if ex else "absent")
    check("the Lagna lord cannot form a Raja yoga with itself",
          all(y["planets"][0] != y["planets"][1]
              for y in v.yogas(chart())["all"] if y["key"] == "raja"))
    check("a one-way special aspect is not association by default",
          v.ASSOCIATION_INCLUDES_ONE_WAY_ASPECT is False
          and all(y["association"] != "one-way aspect"
                  for y in v.yogas(chart(Sun="Gemini", Venus="Gemini"))["all"]
                  if "association" in y))
    check("shared lordship of two wealth houses is reported, not counted as a yoga",
          v.yogas(chart(asc="Taurus"))["shared_dhana_lords"]
          == [{"planet": "Mercury", "houses": [2, 5]}],
          str(v.yogas(chart(asc="Taurus"))["shared_dhana_lords"]))

    print("\n12. Kemadruma — the isolated Moon and its cancellations")
    # Aries Lagna, Moon in Sagittarius (the 9th, not a kendra), every other
    # graha placed at 3, 5, 6, 8, 9 or 11 signs from it — so nothing sits in
    # the 2nd, the 12th, the Moon's own sign, or a kendra from the Moon — and
    # Jupiter at the 11th, where its 5th and 9th aspects miss the Moon.
    lonely = chart(Moon="Sagittarius", Sun="Aries", Mars="Aquarius",
                   Mercury="Taurus", Jupiter="Libra", Venus="Cancer", Saturn="Leo")
    km = entry(lonely, "kemadruma")
    check("an isolated Moon with no cancellation forms Kemadruma",
          km is not None and km["formed"] and km["isolated"]
          and km["company"] == [] and km["cancellations"] == [],
          km["condition"] if km else "absent")
    check("and it appears in the formed list", "kemadruma" in formed(lonely))
    # The one planet moved: Jupiter to Aries, the 5th from the Moon, so its 5th
    # aspect reaches the Moon. Still isolated; now cancelled.
    helped = chart(Moon="Sagittarius", Sun="Aries", Mars="Aquarius",
                   Mercury="Taurus", Jupiter="Aries", Venus="Cancer", Saturn="Leo")
    km2 = entry(helped, "kemadruma")
    check("a benefic aspect on the Moon cancels it",
          km2["isolated"] and km2["cancelled"] and not km2["formed"]
          and any("Jupiter" in c for c in km2["cancellations"]),
          str(km2["cancellations"]))
    check("a cancelled Kemadruma stays out of the formed list",
          "kemadruma" not in formed(helped))
    # Mercury moved to Capricorn, the 2nd from the Moon: company, so the yoga
    # never forms in the first place.
    flanked = chart(Moon="Sagittarius", Sun="Aries", Mars="Aquarius",
                    Mercury="Capricorn", Jupiter="Libra", Venus="Cancer",
                    Saturn="Leo")
    km3 = entry(flanked, "kemadruma")
    check("a planet in the 2nd from the Moon prevents it entirely",
          not km3["formed"] and not km3["cancelled"]
          and km3["company"][0]["from_moon"] == 2, str(km3["company"]))
    check("the Sun is not counted as company, by the classical rule",
          "Sun" in v.KEMADRUMA_IGNORED
          and entry(chart(Moon="Sagittarius", Sun="Capricorn", Mars="Aquarius",
                          Mercury="Taurus", Jupiter="Libra", Venus="Cancer",
                          Saturn="Leo"), "kemadruma")["formed"])
    # Moon moved into Cancer, a kendra from the Aries Lagna, with everything
    # else kept away from it.
    kendra_moon = chart(Moon="Cancer", Sun="Virgo", Mars="Scorpio",
                        Mercury="Sagittarius", Jupiter="Capricorn",
                        Venus="Aquarius", Saturn="Pisces")
    km4 = entry(kendra_moon, "kemadruma")
    check("a Moon in a kendra from the Lagna cancels it",
          km4["isolated"] and km4["cancelled"]
          and any("kendra from the Lagna" in c for c in km4["cancellations"]),
          str(km4["cancellations"]))
    check("Kemadruma is always reported, formed or not, so a reading can say so",
          all(entry(c, "kemadruma") is not None
              for c in (lonely, helped, flanked, chart())))
    check("the four cancellations are exposed as a constant",
          set(v.KEMADRUMA_CANCELLATIONS) == {
              "moon_in_kendra", "planet_in_kendra_from_moon",
              "benefic_with_moon", "moon_dignified"})

    print("\n13. Chandra-Mangala and Budha-Aditya")
    cm = entry(chart(Moon="Aquarius", Mars="Aquarius"), "chandra_mangala")
    check("Moon conjunct Mars forms Chandra-Mangala",
          cm is not None and cm["association"] == "conjunction"
          and cm["sign"] == "Aquarius", cm["condition"] if cm else "absent")
    check("Moon opposite Mars does NOT, on the default reading",
          v.CHANDRA_MANGALA_INCLUDES_MUTUAL_ASPECT is False
          and entry(chart(Moon="Aquarius", Mars="Leo"), "chandra_mangala") is None)
    check("and a Moon three signs from Mars does not either",
          entry(chart(Moon="Aquarius", Mars="Aries"), "chandra_mangala") is None)

    # Sun at Scorpio 5°, Mercury at Scorpio 20° — 15° apart, outside the 14°
    # classical combustion arc for a direct Mercury.
    ba = entry(chart(Sun=lon("Scorpio", 5.0), Mercury=lon("Scorpio", 20.0)),
               "budha_aditya")
    check("Sun with Mercury in one sign forms Budha-Aditya",
          ba is not None and ba["sign"] == "Scorpio"
          and abs(ba["separation"] - 15.0) < 0.01,
          ba["condition"] if ba else "absent")
    check("15° from the Sun is outside the 14° combustion arc",
          ba["mercury_combust"] is False and ba["combustion_arc"] == 14.0)
    close = entry(chart(Sun=lon("Scorpio", 5.0), Mercury=lon("Scorpio", 12.0)),
                  "budha_aditya")
    check("a combust Mercury still forms it, and the combustion is disclosed",
          close is not None and close["mercury_combust"] is True
          and "combust" in close["note"], f"{close['separation']}°")
    check("combustion is not enforced, by the documented default",
          v.BUDHA_ADITYA_REQUIRES_NO_COMBUSTION is False)
    check("Sun and Mercury in different signs form nothing",
          entry(chart(Sun="Scorpio", Mercury="Sagittarius"), "budha_aditya") is None)

    print("\n14. Refusals, and the shape of what comes back")
    tropical = chart(zodiac="tropical")
    for name, fn in (("divisional_chart", lambda c: v.divisional_chart(c, "D9")),
                     ("vargottama", v.vargottama),
                     ("varga_strength", v.varga_strength),
                     ("yogas", v.yogas),
                     ("analyse", v.analyse)):
        try:
            fn(tropical)
            check(f"{name}() refuses a tropical chart", False, "no error raised")
        except v.VargaError as exc:
            check(f"{name}() refuses a tropical chart", "sidereal" in str(exc),
                  str(exc)[:60])
    try:
        v.yogas({"nonsense": 1})
        check("a non-chart argument is refused", False, "no error raised")
    except v.VargaError:
        check("a non-chart argument is refused", True)
    try:
        no_asc = chart()
        del no_asc["objects"]["ASC"]
        v.divisional_chart(no_asc, "D9")
        check("a chart with no Lagna is refused", False, "no error raised")
    except v.VargaError as exc:
        check("a chart with no Lagna is refused", "ASC" in str(exc), str(exc)[:60])
    try:
        no_moon = chart()
        del no_moon["objects"]["Moon"]
        v.yogas(no_moon)
        check("a chart with no Moon is refused", False, "no error raised")
    except v.VargaError:
        check("a chart with no Moon is refused", True)

    rich = chart(Sun="Gemini", Moon="Gemini", Mars="Capricorn", Jupiter="Cancer",
                 Venus="Gemini", node="Aries")
    full = v.analyse(rich)
    try:
        blob = json.dumps(full)
        check("analyse() is JSON-serialisable", True, f"{len(blob)} bytes")
    except TypeError as exc:
        check("analyse() is JSON-serialisable", False, str(exc))
    check("it carries the vargas, vargottama, strength, yogas and the caveats",
          {"meta", "rashi_positions", "vargas", "vargottama", "varga_strength",
           "yogas", "not_implemented", "disclaimer"} <= set(full))
    check("every requested division is in the varga block",
          set(full["vargas"]) == set(v.DEFAULT_DIVISIONS))
    check("the D9 sign in rashi_positions agrees with the D9 varga chart",
          all(full["rashi_positions"][n]["navamsa"]
              == full["vargas"]["D9"]["positions"][n]["sign"]
              for n in full["rashi_positions"]))
    check("every formed yoga carries planets, a condition, a note and a source",
          all(y["planets"] and len(y["condition"]) > 15 and len(y["note"]) > 40
              and len(y["source"]) > 10 for y in full["yogas"]["yogas"]),
          f"{len(full['yogas']['yogas'])} formed")
    check("strength is present or explicitly None, never invented as a number",
          all(y["strength"] is None or isinstance(y["strength"], str)
              for y in full["yogas"]["all"]))
    check("the method note states the whole-sign and drishti conventions",
          "whole-sign" in full["yogas"]["method_note"]
          and "Rahu and Ketu take no part" in full["yogas"]["method_note"])
    # Ordinals reach the reader, so sweep every note and condition the engine
    # can emit rather than spot-checking one.
    prose: list[str] = []
    for sign in SIGNS:
        for other in SIGNS:
            c = chart(asc=sign, Sun=other, Moon=other, Mars=other,
                      Mercury=other, Jupiter=other, Venus=other, Saturn=other)
            for y in v.yogas(c)["all"]:
                prose += [y["condition"], y["note"], *y.get("cancellations", []),
                          *y.get("caveats", [])]
    # Every "<number><suffix>" in the prose has to be the suffix _ordinal would
    # have chosen. A naive substring hunt for "1th"/"2th" will not do here:
    # houses run to 12, and "11th" and "12th" are correct and contain both.
    mangled = [m.group(0) for p in prose for m in re.finditer(r"\b(\d+)(st|nd|rd|th)\b", p)
               if m.group(0) != v._ordinal(int(m.group(1)))]
    check("no note misspells an ordinal", not mangled, str(sorted(set(mangled))[:5]))
    check("the disclaimer says a yoga is not a verdict",
          "not a verdict" in full["disclaimer"])
    check("the ChartSession path and the bundle path agree",
          json.dumps(v.analyse(_Session(rich))) == json.dumps(full))

    print("\n15. Against a chart built by chart_service itself")
    try:
        from app.chart_service import BirthData, build

        session = build(BirthData(
            name="Native", date="1986-08-19", time="11:59",
            latitude=26.26, longitude=82.07, timezone="Asia/Kolkata",
            place="Sultanpur, Uttar Pradesh, India", zodiac="sidereal",
            ayanamsa="lahiri", house_system="Whole Sign"))

        live = v.analyse(session)
        check("a real ChartSession is read without adaptation", True,
              f"Lagna {live['meta']['lagna']}, "
              f"{live['yogas']['count']} yoga(s) formed")
        check("the bundle dict works too, and agrees",
              json.dumps(v.analyse(session.bundle)) == json.dumps(live))
        json.dumps(live)
        check("a real chart's analysis is JSON-serialisable", True)
        d9 = live["vargas"]["D9"]
        check("the real chart's navamsa places every graha in a valid sign",
              all(d9["positions"][g]["sign"] in SIGNS for g in GRAHAS)
              and d9["lagna"]["sign"] in SIGNS,
              f"D9 Lagna {d9['lagna']['sign']}")
        # The navamsa this module derives must agree with the navamsa pada that
        # chart_service's Vimshottari code already derives from the same Moon:
        # a nakshatra pada is exactly one navamsa, and the 108 navamsas of the
        # zodiac are the 27 nakshatras' 4 padas. They read the same longitude
        # and must never disagree.
        import datetime as dt

        from app.chart_service import vimshottari

        vim = vimshottari(session, dt.datetime(2026, 1, 1))
        moon_lon = session.bundle["objects"]["Moon"]["longitude"]
        pada_index = int((moon_lon % 360.0) / (360.0 / 108.0))
        check("the Moon's navamsa is the sign of its nakshatra pada",
              SIGNS[pada_index % 12] == v.navamsa_sign(moon_lon),
              f"{SIGNS[pada_index % 12]} vs {v.navamsa_sign(moon_lon)} "
              f"({vim['nakshatra']} pada {vim['pada']})")
        check("Rahu and Ketu ride along on a real chart",
              "Rahu" in d9["positions"] and "Ketu" in d9["positions"],
              str([n for n in d9["positions"] if n in ("Rahu", "Ketu")]))
        check("every real-chart yoga names its source",
              all(y["source"] for y in live["yogas"]["yogas"]))

        # A tropical build of the same birth must be refused, not converted.
        west = build(BirthData(
            name="Native", date="1986-08-19", time="11:59",
            latitude=26.26, longitude=82.07, timezone="Asia/Kolkata",
            place="Sultanpur, Uttar Pradesh, India", zodiac="tropical",
            house_system="Whole Sign"))
        try:
            v.analyse(west)
            check("a real tropical chart is refused", False, "no error raised")
        except v.VargaError:
            check("a real tropical chart is refused", True)
    except Exception as exc:                          # pragma: no cover
        check("real charts build and analyse", False, f"{type(exc).__name__}: {exc}")

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("vargas — divisional charts and classical yogas: all green")
    return 0


class _Session:
    """The one attribute `vargas` needs off a chart_service.ChartSession."""

    def __init__(self, bundle: dict) -> None:
        self.bundle = bundle


def _seven_apart(a: str, b: str) -> bool:
    return (SIGNS.index(b) - SIGNS.index(a)) % 12 == 6


if __name__ == "__main__":
    raise SystemExit(main())
