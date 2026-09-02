"""Kundali Milan — Ashtakoot Guna Milan and Mangal Dosha.

A pure unit test: no server, no database, no network. It builds minimal chart
bundles of the shape `chart_service` produces and drives `app.astro.matching`
directly, then finishes by running the same functions against two real charts
so the bundle shape is checked against the real producer and not just against
this file's idea of it.

The properties that matter:

* **No koota can ever pay out more than its classical maximum**, and the total
  can never exceed 36 — swept over every one of the 729 nakshatra pairs.
* **The worked examples are computed by hand from the classical tables** and
  asserted exactly. If a table is edited, these break loudly. Each one records
  where its expected numbers come from.
* **Both dosha cancellations fire when they should and stay silent when they
  should not.** Restoring points on a cancellation that did not apply is the
  failure mode that would matter most to somebody reading the result.

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.test_matching
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Section 12 prints Hindi (Devanagari) note text as check() detail; Windows
# consoles default to a cp1252 stdout that cannot encode it and crashes the
# whole run before it gets anywhere near a real assertion failure.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.astro import matching as m
from app.chart_service import SIGNS, dms, sign_of

failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


# --------------------------------------------------------------------------
# Chart fixtures — the same keys `chart_service._normalise` emits, and no more
# than `matching` actually reads.
# --------------------------------------------------------------------------

NAK = 360.0 / 27.0


def nak_lon(index: int, pada: int = 1) -> float:
    """Sidereal longitude in the middle of a given nakshatra pada (1-based)."""
    return (index - 1) * NAK + (pada - 1) * (NAK / 4) + NAK / 8


def sign_lon(sign: str, degree: float = 5.0) -> float:
    return SIGNS.index(sign) * 30.0 + degree


def _obj(name: str, longitude: float) -> dict:
    longitude %= 360.0
    return {
        "name": name, "kind": "planet", "longitude": longitude,
        "sign": sign_of(longitude), "degree": longitude % 30.0,
        "position": f"{sign_of(longitude)} {dms(longitude % 30.0)}",
    }


def chart(moon: float, *, asc: str = "Aries", mars: str = "Aries",
          venus: str = "Aries", jupiter: str = "Aries",
          name: str = "Native", zodiac: str = "sidereal") -> dict:
    return {
        "meta": {"zodiac": zodiac, "name": name},
        "birth": {"name": name},
        "objects": {
            "Moon": _obj("Moon", moon),
            "ASC": _obj("ASC", sign_lon(asc)),
            "Mars": _obj("Mars", sign_lon(mars)),
            "Venus": _obj("Venus", sign_lon(venus)),
            "Jupiter": _obj("Jupiter", sign_lon(jupiter)),
        },
    }


def scores(result: dict) -> dict:
    return {k["key"]: k["score"] for k in result["kootas"]}


def main() -> int:
    print("\n1. The reference tables are internally consistent")
    check("27 nakshatras carry a yoni", len(m.YONI_OF_NAKSHATRA) == 27,
          str(len(m.YONI_OF_NAKSHATRA)))
    check("27 nakshatras carry a gana", len(m.GANA_OF_NAKSHATRA) == 27)
    check("27 nakshatras carry a nadi", len(m.NADI_OF_NAKSHATRA) == 27)
    gana_counts = {g: sum(1 for v in m.GANA_OF_NAKSHATRA.values() if v == g)
                   for g in m.GANA_ORDER}
    check("gana splits 9/9/9", set(gana_counts.values()) == {9}, str(gana_counts))
    nadi_counts = {n: sum(1 for v in m.NADI_OF_NAKSHATRA.values() if v == n)
                   for n in ("Adi", "Madhya", "Antya")}
    check("nadi splits 9/9/9", set(nadi_counts.values()) == {9}, str(nadi_counts))
    check("14 distinct yonis", len({y for y, _ in m.YONI_OF_NAKSHATRA.values()}) == 14)
    check("Mongoose holds Uttara Ashadha alone",
          [n for n, (y, _) in m.YONI_OF_NAKSHATRA.items() if y == "Mongoose"]
          == ["Uttara Ashadha"])
    # _check_yoni_table() already ran at import; assert its two properties here
    # too so a failure names itself rather than arriving as an ImportError.
    check("yoni grid is symmetric", all(
        m.YONI_TABLE[i][j] == m.YONI_TABLE[j][i]
        for i in range(14) for j in range(14)))
    check("yoni grid has exactly 7 enemy pairs",
          sum(1 for r in m.YONI_TABLE for c in r if c == 0) == 14)
    check("every rashi has a varna and a vashya group",
          all(s in m.VARNA_OF_RASHI for s in SIGNS)
          and all(m._vashya_group(s, 5.0) in m.VASHYA_GROUPS for s in SIGNS))
    check("the koota maxima sum to 36",
          sum((1, 2, 3, 4, 5, 6, 7, 8)) == int(m.MAXIMUM_POINTS))

    print("\n2. No koota can overpay, and the total never exceeds 36")
    worst_total, worst_pair = 0.0, None
    breaches: list[str] = []
    for gi in range(1, 28):
        for bi in range(1, 28):
            r = m.ashtakoot(chart(nak_lon(gi)), chart(nak_lon(bi)))
            for k in r["kootas"]:
                if not (0.0 <= k["score"] <= k["max"]):
                    breaches.append(f"{k['key']} {k['score']}/{k['max']} at {gi}x{bi}")
            if r["total"] > worst_total:
                worst_total, worst_pair = r["total"], (gi, bi)
            if r["total"] > m.MAXIMUM_POINTS:
                breaches.append(f"total {r['total']} at {gi}x{bi}")
    check("729 nakshatra pairs, every koota inside 0..max",
          not breaches, "; ".join(breaches[:3]))
    check("no total exceeds 36", worst_total <= 36.0,
          f"highest seen {worst_total} at nakshatra pair {worst_pair}")
    check("36 is actually reachable", worst_total == 36.0, str(worst_total))

    print("\n3. Worked examples, computed by hand from the classical tables")

    # (a) Groom Moon in Rohini (Taurus), bride Moon in Hasta (Virgo).
    #   Varna        Taurus and Virgo are both Vaishya; groom not below bride  -> 1
    #   Vashya       Chatushpada groom, Manava bride; VASHYA_TABLE[Manava][0]  -> 1
    #   Tara         4->13 is the 10th star, 10%9=1 Janma; 13->4 is the 19th,
    #                19%9=1 Janma. Neither is Vipat/Pratyak/Vadha             -> 3
    #   Yoni         Rohini is Serpent, Hasta is Buffalo; grid cell            -> 1
    #   Graha Maitri Venus and Mercury count each other friends (BPHS ch.3)    -> 5
    #   Gana         Rohini Manushya, Hasta Deva; GANA_TABLE[Manushya][Deva]   -> 5
    #   Bhakoot      Taurus/Virgo is 5/9, a dosha, but the lords Venus and
    #                Mercury are mutual friends, so it cancels                 -> 7
    #   Nadi         Rohini is Antya, Hasta is Adi — different                 -> 8
    a = m.ashtakoot(chart(nak_lon(4)), chart(nak_lon(13)))
    check("Rohini x Hasta koota by koota",
          scores(a) == {"varna": 1.0, "vashya": 1.0, "tara": 3.0, "yoni": 1.0,
                        "graha_maitri": 5.0, "gana": 5.0, "bhakoot": 7.0, "nadi": 8.0},
          str(scores(a)))
    check("Rohini x Hasta totals 31 and reads 'good'",
          a["total"] == 31.0 and a["verdict"] == "good",
          f"{a['total']} {a['verdict']}")

    # (b) Groom Moon in Ashwini (Aries), bride Moon in Hasta (Virgo) — the
    #     opposite case, chosen because both doshas bite and neither cancels.
    #   Varna        Kshatriya groom over Vaishya bride                        -> 1
    #   Vashya       Chatushpada groom, Manava bride                           -> 1
    #   Tara         1->13 is the 13th star, 13%9=4 Kshema (good); 13->1 is the
    #                16th, 16%9=7 Vadha (bad). One direction only            -> 1.5
    #   Yoni         Horse and Buffalo are a natural-enemy pair                -> 0
    #   Graha Maitri Mars counts Mercury an enemy, Mercury counts Mars
    #                neutral; enemy+neutral                                  -> 0.5
    #   Gana         both Deva                                                 -> 6
    #   Bhakoot      Aries/Virgo is 6/8; lords Mars and Mercury are not
    #                friends, so no cancellation                               -> 0
    #   Nadi         both Adi, different rashi and nakshatra, no cancellation   -> 0
    b = m.ashtakoot(chart(nak_lon(1)), chart(nak_lon(13)))
    check("Ashwini x Hasta koota by koota",
          scores(b) == {"varna": 1.0, "vashya": 1.0, "tara": 1.5, "yoni": 0.0,
                        "graha_maitri": 0.5, "gana": 6.0, "bhakoot": 0.0, "nadi": 0.0},
          str(scores(b)))
    check("Ashwini x Hasta totals 10 and reads 'not recommended'",
          b["total"] == 10.0 and b["verdict"] == "not recommended",
          f"{b['total']} {b['verdict']}")

    # (c) Both Moons in Libra — Swati at 10° Libra, Vishakha at 21° Libra.
    #     Chosen because Swati and Vishakha are adjacent Antya-nadi stars that
    #     share a rashi, which is exactly the Nadi cancellation case.
    #   Varna 1 (both Shudra) · Vashya 2 (both Manava) · Tara 3 (2nd Sampat and
    #   27th -> 9th Ati-Mitra) · Yoni 1 (Buffalo/Tiger) · Graha Maitri 5 (both
    #   Venus) · Gana 0 (Swati Deva against Vishakha Rakshasa) · Bhakoot 7 (1/1)
    #   · Nadi 8 (both Antya, cancelled by same rashi + different nakshatra).
    c = m.ashtakoot(chart(190.0), chart(201.0))
    check("Swati x Vishakha koota by koota",
          scores(c) == {"varna": 1.0, "vashya": 2.0, "tara": 3.0, "yoni": 1.0,
                        "graha_maitri": 5.0, "gana": 0.0, "bhakoot": 7.0, "nadi": 8.0},
          str(scores(c)))
    check("Swati x Vishakha totals 27", c["total"] == 27.0, str(c["total"]))

    # (d) Both Moons in Ashwini, different padas — the only way to score a
    #     perfect 36, since every koota is at its maximum and the Nadi dosha
    #     that identical stars would carry is cancelled by the pada difference.
    d = m.ashtakoot(chart(2.0), chart(9.0))
    check("Ashwini p1 x Ashwini p3 scores a perfect 36",
          d["total"] == 36.0 and d["verdict"] == "excellent",
          f"{d['total']} {d['verdict']}")
    check("every koota is at its maximum there",
          all(k["score"] == k["max"] for k in d["kootas"]), str(scores(d)))

    # (e) Aries and Scorpio Moons — both ruled by Mars. 8/6 is a Bhakoot dosha
    #     and the same-lord cancellation is the one that applies here.
    e = m.ashtakoot(chart(nak_lon(1)), chart(nak_lon(18)))
    check("Aries x Scorpio Bhakoot cancels on the shared lord Mars",
          scores(e)["bhakoot"] == 7.0, str(scores(e)["bhakoot"]))
    check("Varna 0 when the bride outranks the groom (Kshatriya under Brahmin)",
          scores(e)["varna"] == 0.0, str(scores(e)["varna"]))

    print("\n4. Identical charts score sensibly")
    same = m.ashtakoot(chart(2.0), chart(2.0))
    s = scores(same)
    check("seven kootas are at their maximum",
          sum(1 for k in same["kootas"] if k["score"] == k["max"]) == 7, str(s))
    # Identical Moons share a nadi and share a pada, so neither cancellation is
    # available. Classically correct and worth asserting: a horoscope does not
    # match itself perfectly.
    check("Nadi is 0 — identical Moons cannot cancel Nadi", s["nadi"] == 0.0, str(s))
    check("total is 28, not 36", same["total"] == 28.0, str(same["total"]))
    same_nadi = [k for k in same["kootas"] if k["key"] == "nadi"][0]
    check("Nadi is reported as an uncancelled dosha",
          same_nadi["dosha"] is True and same_nadi["cancelled"] is False)

    print("\n5. Nadi dosha — both cancellation paths, and the non-cancelling case")
    nadi_of = lambda r: [k for k in r["kootas"] if k["key"] == "nadi"][0]

    n_rashi = nadi_of(m.ashtakoot(chart(190.0), chart(201.0)))
    check("same rashi + different nakshatra cancels",
          n_rashi["dosha"] and n_rashi["cancelled"] and n_rashi["score"] == 8.0,
          n_rashi["cancellation"])
    n_pada = nadi_of(m.ashtakoot(chart(2.0), chart(9.0)))
    check("same nakshatra + different pada cancels",
          n_pada["dosha"] and n_pada["cancelled"] and n_pada["score"] == 8.0,
          n_pada["cancellation"])
    n_none = nadi_of(m.ashtakoot(chart(nak_lon(1)), chart(nak_lon(13))))
    check("different rashi + different nakshatra does NOT cancel",
          n_none["dosha"] and not n_none["cancelled"] and n_none["score"] == 0.0,
          str(n_none["score"]))
    n_same = nadi_of(m.ashtakoot(chart(2.0), chart(2.0)))
    check("identical Moons do NOT cancel", not n_same["cancelled"], n_same["cancellation"])
    n_clear = nadi_of(m.ashtakoot(chart(nak_lon(4)), chart(nak_lon(13))))
    check("no dosha at all when the nadis differ",
          not n_clear["dosha"] and not n_clear["cancelled"] and n_clear["score"] == 8.0)
    check("raw_score preserves the pre-cancellation value",
          n_rashi["raw_score"] == 0.0 and n_clear["raw_score"] == 8.0)

    print("\n6. Bhakoot dosha — both cancellation paths, and the non-cancelling case")
    bhakoot_of = lambda r: [k for k in r["kootas"] if k["key"] == "bhakoot"][0]

    b_lord = bhakoot_of(m.ashtakoot(chart(nak_lon(1)), chart(nak_lon(18))))
    check("6/8 with a shared lord (Aries/Scorpio, Mars) cancels",
          b_lord["dosha"] and b_lord["cancelled"] and b_lord["score"] == 7.0,
          b_lord["cancellation"])
    b_friend = bhakoot_of(m.ashtakoot(chart(nak_lon(4)), chart(nak_lon(13))))
    check("5/9 with mutually friendly lords (Venus/Mercury) cancels",
          b_friend["dosha"] and b_friend["cancelled"] and b_friend["score"] == 7.0,
          b_friend["cancellation"])
    b_none = bhakoot_of(m.ashtakoot(chart(nak_lon(1)), chart(nak_lon(13))))
    check("6/8 with unfriendly lords (Mars/Mercury) does NOT cancel",
          b_none["dosha"] and not b_none["cancelled"] and b_none["score"] == 0.0,
          f"{b_none['groom_to_bride']}/{b_none['bride_to_groom']}")
    b_clear = bhakoot_of(m.ashtakoot(chart(nak_lon(1)), chart(nak_lon(10))))
    check("Aries/Leo is 5/9 and IS a dosha", b_clear["dosha"] is True,
          f"{b_clear['groom_to_bride']}/{b_clear['bride_to_groom']}")
    b_ok = bhakoot_of(m.ashtakoot(chart(nak_lon(1)), chart(nak_lon(7))))
    check("Aries/Gemini is 3/11 and carries no dosha",
          not b_ok["dosha"] and b_ok["score"] == 7.0,
          f"{b_ok['groom_to_bride']}/{b_ok['bride_to_groom']}")

    print("\n7. Mangal dosha is detected from Lagna, Moon and Venus independently")

    # Mars in Libra: 7th from an Aries Lagna, but 5th from a Gemini Moon and
    # 3rd from a Leo Venus — so only the Lagna reading fires.
    lagna_only = m.mangal_dosha(chart(sign_lon("Gemini"), asc="Aries", mars="Libra",
                                      venus="Leo", jupiter="Taurus"))
    check("Manglik from the Lagna alone",
          lagna_only["manglik"] and lagna_only["afflicted_from"] == ["Lagna"],
          str(lagna_only["afflicted_from"]))

    # Mars in Aquarius: 8th from a Cancer Moon, 11th from an Aries Lagna,
    # 9th from a Gemini Venus.
    moon_only = m.mangal_dosha(chart(sign_lon("Cancer"), asc="Aries", mars="Aquarius",
                                     venus="Gemini", jupiter="Taurus"))
    check("Manglik from the Moon alone",
          moon_only["manglik"] and moon_only["afflicted_from"] == ["Moon"],
          str(moon_only["afflicted_from"]))

    # Mars in Libra: 4th from a Cancer Venus, 6th from a Taurus Lagna,
    # 5th from a Gemini Moon.
    venus_only = m.mangal_dosha(chart(sign_lon("Gemini"), asc="Taurus", mars="Libra",
                                      venus="Cancer", jupiter="Pisces"))
    check("Manglik from Venus alone",
          venus_only["manglik"] and venus_only["afflicted_from"] == ["Venus"],
          str(venus_only["afflicted_from"]))

    clear = m.mangal_dosha(chart(sign_lon("Taurus"), asc="Aries", mars="Virgo",
                                 venus="Scorpio", jupiter="Cancer"))
    check("a clear chart is Manglik from nothing",
          not clear["manglik"] and clear["severity"] == "none"
          and clear["afflicted_from"] == [], str(clear["afflicted_from"]))
    check("all three references are always reported",
          [r["reference"] for r in clear["references"]] == ["Lagna", "Moon", "Venus"])
    check("the 7th from the Lagna is graded above the 4th from Venus",
          lagna_only["severity"] == "moderate" and venus_only["severity"] == "mild",
          f"{lagna_only['severity']} vs {venus_only['severity']}")

    print("\n8. Mangal cancellations and the pair-level reading")

    # Mars in Cancer in the 7th is one of the classical sign-in-house
    # exemptions; Virgo Moon and Scorpio Venus keep the other two clear.
    exempt = m.mangal_dosha(chart(sign_lon("Virgo"), asc="Capricorn", mars="Cancer",
                                  venus="Scorpio", jupiter="Aries"))
    check("Mars in Cancer in the 7th is exempt by sign",
          not exempt["manglik"] and exempt["references"][0]["mars_house"] == 7
          and exempt["references"][0]["exempt_by_sign"],
          str(exempt["afflicted_from"]))
    check("the exemption is spelled out for the reader",
          any("exemption" in x for x in exempt["mitigations"]), str(exempt["mitigations"]))

    # Mars in Scorpio, its own sign, in the 8th from an Aries Moon.
    own = m.mangal_dosha(chart(sign_lon("Aries"), asc="Cancer", mars="Scorpio",
                               venus="Virgo", jupiter="Aries"))
    check("own-sign Mars still registers but caps severity at mild",
          own["manglik"] and own["severity"] == "mild", own["severity"])
    check("own-sign Mars is listed as a mitigation",
          any("own sign" in x for x in own["mitigations"]), str(own["mitigations"]))

    # Jupiter in Aries, Mars in Leo: the 5th from Jupiter, so Jupiter aspects Mars.
    jup = m.mangal_dosha(chart(sign_lon("Taurus"), asc="Leo", mars="Leo",
                               venus="Capricorn", jupiter="Aries"))
    check("Jupiter's aspect on Mars is recorded as a mitigation",
          any("Jupiter" in x for x in jup["mitigations"]), str(jup["mitigations"]))

    manglik_chart = chart(sign_lon("Gemini"), asc="Aries", mars="Libra",
                          venus="Leo", jupiter="Taurus")
    clear_chart = chart(sign_lon("Taurus"), asc="Aries", mars="Virgo",
                        venus="Scorpio", jupiter="Cancer")
    both = m.match(manglik_chart, manglik_chart)["mangal"]["pair"]
    check("two Manglik charts cancel each other",
          both["both_manglik"] and both["cancelled_by_both_manglik"]
          and both["verdict"] == "balanced", both["verdict"])
    one = m.match(manglik_chart, clear_chart)["mangal"]["pair"]
    check("one Manglik and one clear is flagged one-sided",
          one["verdict"] == "one-sided" and not one["cancelled_by_both_manglik"],
          one["verdict"])
    neither = m.match(clear_chart, clear_chart)["mangal"]["pair"]
    check("neither Manglik reads clear", neither["verdict"] == "clear", neither["verdict"])

    print("\n9. Symmetry — and the asymmetries the tradition actually asks for")
    # Tara is counted in both directions here, Graha Maitri is keyed on the
    # unordered pair of relations, and Yoni/Bhakoot/Nadi are symmetric tables.
    # Varna, Vashya and Gana are directional by tradition and must NOT be
    # forced symmetric.
    symmetric_expected = {"tara", "yoni", "graha_maitri", "bhakoot", "nadi"}
    asymmetric_expected = {"varna", "vashya", "gana"}
    observed_asymmetric: set[str] = set()
    for gi in range(1, 28):
        for bi in range(1, 28):
            fwd = scores(m.ashtakoot(chart(nak_lon(gi)), chart(nak_lon(bi))))
            rev = scores(m.ashtakoot(chart(nak_lon(bi)), chart(nak_lon(gi))))
            observed_asymmetric |= {k for k in fwd if fwd[k] != rev[k]}
    check("exactly the five symmetric kootas never change on a swap",
          observed_asymmetric & symmetric_expected == set(),
          str(sorted(observed_asymmetric & symmetric_expected)))
    check("all three directional kootas do change on some swap",
          observed_asymmetric == asymmetric_expected, str(sorted(observed_asymmetric)))

    # The documented asymmetries, asserted deliberately rather than worked
    # around: the groom's varna may equal or exceed the bride's, a Vanachara
    # bride is the weak side of the Vashya table, and Gana favours the groom
    # holding the higher gana.
    gemini, cancer = nak_lon(6), nak_lon(9)          # Ardra -> Gemini, Ashlesha -> Cancer
    check("Varna: Shudra groom under a Brahmin bride scores 0, the reverse 1",
          scores(m.ashtakoot(chart(gemini), chart(cancer)))["varna"] == 0.0
          and scores(m.ashtakoot(chart(cancer), chart(gemini)))["varna"] == 1.0)
    leo, aries = nak_lon(10), nak_lon(1)             # Magha -> Leo, Ashwini -> Aries
    check("Vashya: Chatushpada bride with a Vanachara groom is 1.5, the reverse 0",
          scores(m.ashtakoot(chart(leo), chart(aries)))["vashya"] == 1.5
          and scores(m.ashtakoot(chart(aries), chart(leo)))["vashya"] == 0.0)
    deva, manushya = nak_lon(1), nak_lon(2)          # Ashwini Deva, Bharani Manushya
    check("Gana: Deva groom with a Manushya bride is 6, the reverse 5",
          scores(m.ashtakoot(chart(deva), chart(manushya)))["gana"] == 6.0
          and scores(m.ashtakoot(chart(manushya), chart(deva)))["gana"] == 5.0)
    fwd_total = m.ashtakoot(chart(gemini), chart(cancer))["total"]
    rev_total = m.ashtakoot(chart(cancer), chart(gemini))["total"]
    check("so the total can legitimately differ on a swap",
          fwd_total != rev_total, f"{fwd_total} vs {rev_total}")

    print("\n10. Refusals, and the shape of what comes back")
    try:
        m.ashtakoot(chart(2.0, zodiac="tropical"), chart(9.0))
        check("a tropical chart is refused", False, "no error raised")
    except m.MatchingError as exc:
        check("a tropical chart is refused", "sidereal" in str(exc), str(exc)[:70])
    try:
        m.ashtakoot({"objects": {}}, chart(9.0))
        check("a chart with no Moon is refused", False, "no error raised")
    except m.MatchingError:
        check("a chart with no Moon is refused", True)
    try:
        m.ashtakoot({"nonsense": 1}, chart(9.0))
        check("a non-chart argument is refused", False, "no error raised")
    except m.MatchingError:
        check("a non-chart argument is refused", True)
    try:
        m.mangal_dosha(chart(2.0, zodiac="tropical"))
        check("mangal_dosha refuses a tropical chart too", False, "no error raised")
    except m.MatchingError:
        check("mangal_dosha refuses a tropical chart too", True)

    full = m.match(chart(nak_lon(4), asc="Leo", mars="Libra", venus="Gemini",
                         jupiter="Pisces", name="A"),
                   chart(nak_lon(13), asc="Taurus", mars="Cancer", venus="Leo",
                         jupiter="Virgo", name="B"))
    try:
        blob = json.dumps(full)
        check("match() is JSON-serialisable", True, f"{len(blob)} bytes")
    except TypeError as exc:
        check("match() is JSON-serialisable", False, str(exc))
    check("it carries ashtakoot, mangal and a summary",
          {"ashtakoot", "mangal", "summary", "disclaimer"} <= set(full))
    check("the summary total agrees with the koota total",
          full["summary"]["total"] == full["ashtakoot"]["total"])
    check("uncancelled doshas only are listed in the summary",
          all(d in ("bhakoot", "nadi") for d in full["summary"]["doshas"]),
          str(full["summary"]["doshas"]))
    check("every koota carries a plain-language note",
          all(len(k["note"]) > 20 for k in full["ashtakoot"]["kootas"]))
    # Ordinals reach the reader, so sweep every note the two engines can emit
    # for the '1th'/'2th'/'3th' spellings rather than spot-checking one.
    prose: list[str] = []
    for gi in range(1, 28):
        for bi in range(1, 28):
            r = m.ashtakoot(chart(nak_lon(gi)), chart(nak_lon(bi)))
            prose += [k["note"] for k in r["kootas"]]
    for sign in SIGNS:
        d = m.mangal_dosha(chart(sign_lon(sign), asc=sign, mars=sign,
                                 venus=sign, jupiter=sign))
        prose += [d["summary"], *d["mitigations"]]
    check("no note misspells an ordinal",
          not any(bad in p for p in prose for bad in ("1th", "2th", "3th")),
          next((p for p in prose if any(b in p for b in ("1th", "2th", "3th"))), ""))
    check("no note says 'from the Venus'",
          not any("the Venus" in p for p in prose))
    check("the convention is stated, not asserted as fact",
          "convention" in full["ashtakoot"]["convention_note"].lower())

    bands = [(10.0, "not recommended"), (20.0, "acceptable"),
             (30.0, "good"), (35.0, "excellent"), (17.99, "not recommended"),
             (18.0, "acceptable"), (24.99, "acceptable"), (25.0, "good"),
             (32.5, "good"), (33.0, "excellent"), (36.0, "excellent")]
    check("the 18/25/33 bands land where the convention puts them",
          all(m._band(t)[0] == v for t, v in bands),
          str([(t, m._band(t)[0]) for t, v in bands if m._band(t)[0] != v]))

    print("\n11. Against two charts built by chart_service itself")
    try:
        from app.chart_service import BirthData, build

        groom = build(BirthData(
            name="Groom", date="1986-08-19", time="11:59",
            latitude=26.26, longitude=82.07, timezone="Asia/Kolkata",
            place="Sultanpur, Uttar Pradesh, India", zodiac="sidereal",
            ayanamsa="lahiri", house_system="Whole Sign"))
        bride = build(BirthData(
            name="Bride", date="1990-02-11", time="04:20",
            latitude=28.61, longitude=77.21, timezone="Asia/Kolkata",
            place="New Delhi, India", zodiac="sidereal",
            ayanamsa="lahiri", house_system="Whole Sign"))

        # Passed as ChartSession objects, which is what chart_service hands back.
        live = m.match(groom, bride)
        check("a real ChartSession pair matches without adaptation", True,
              f"{live['ashtakoot']['total']}/36 — {live['ashtakoot']['verdict']}")
        check("total is within range",
              0.0 <= live["ashtakoot"]["total"] <= 36.0,
              str(live["ashtakoot"]["total"]))
        check("the bundle dict works too, and agrees",
              m.match(groom.bundle, bride.bundle)["ashtakoot"]["total"]
              == live["ashtakoot"]["total"])

        # The nakshatra this module derives must be the one chart_service's
        # dasha code already derives from the same Moon — they read the same
        # longitude and must never disagree.
        import datetime as dt

        from app.chart_service import vimshottari

        vim = vimshottari(groom, dt.datetime(2026, 1, 1))
        check("nakshatra agrees with chart_service's vimshottari",
              live["ashtakoot"]["groom"]["nakshatra"] == vim["nakshatra"]
              and live["ashtakoot"]["groom"]["pada"] == vim["pada"],
              f"{live['ashtakoot']['groom']['nakshatra']} p"
              f"{live['ashtakoot']['groom']['pada']} vs {vim['nakshatra']} p{vim['pada']}")
        check("a real chart's Mangal reading covers all three references",
              len(live["mangal"]["groom"]["references"]) == 3,
              live["mangal"]["groom"]["summary"])
    except Exception as exc:                          # pragma: no cover
        check("real charts build and match", False, f"{type(exc).__name__}: {exc}")

    print("\n12. Hindi (lang='hi') — every note carries real content, not just presence")
    import re

    devanagari = re.compile(r"[ऀ-ॿ]")

    g = chart(nak_lon(4), asc="Leo", mars="Libra", venus="Gemini", jupiter="Pisces", name="A")
    b = chart(nak_lon(13), asc="Taurus", mars="Cancer", venus="Leo", jupiter="Virgo", name="B")
    en = m.match(g, b, lang="en")
    hi = m.match(g, b, lang="hi")

    check("every Hindi koota label differs from its English counterpart",
          all(ek["label"] != hk["label"] for ek, hk in
              zip(en["ashtakoot"]["kootas"], hi["ashtakoot"]["kootas"])),
          str([(ek["label"], hk["label"]) for ek, hk in
               zip(en["ashtakoot"]["kootas"], hi["ashtakoot"]["kootas"])
               if ek["label"] == hk["label"]]))
    check("every Hindi koota note is non-empty and carries Devanagari",
          all(hk["note"] and devanagari.search(hk["note"]) for hk in hi["ashtakoot"]["kootas"]),
          str([hk["key"] for hk in hi["ashtakoot"]["kootas"]
               if not (hk["note"] and devanagari.search(hk["note"]))]))
    check("every Hindi koota note differs from its English counterpart",
          all(ek["note"] != hk["note"] for ek, hk in
              zip(en["ashtakoot"]["kootas"], hi["ashtakoot"]["kootas"])))

    check("verdict is localised", hi["ashtakoot"]["verdict"] != en["ashtakoot"]["verdict"]
          and devanagari.search(hi["ashtakoot"]["verdict"]))
    check("band_note is localised", hi["ashtakoot"]["band_note"] != en["ashtakoot"]["band_note"]
          and devanagari.search(hi["ashtakoot"]["band_note"]))
    check("convention_note is localised",
          devanagari.search(hi["ashtakoot"]["convention_note"]) is not None)

    for who in ("groom", "bride"):
        eg, hg = en["mangal"][who], hi["mangal"][who]
        check(f"{who} mangal summary is localised",
              devanagari.search(hg["summary"]) is not None, hg["summary"])
        check(f"{who} severity word is localised",
              hg["severity"] != eg["severity"] and devanagari.search(hg["severity"]),
              hg["severity"])
        check(f"{who} mitigations (if any) are localised",
              all(devanagari.search(x) for x in hg["mitigations"]),
              str(hg["mitigations"]))

    check("pair note is localised", devanagari.search(hi["mangal"]["pair"]["note"]) is not None)
    check("pair tradition_note is localised",
          devanagari.search(hi["mangal"]["pair"]["tradition_note"]) is not None)
    check("disclaimer is localised",
          devanagari.search(hi["disclaimer"]) is not None and hi["disclaimer"] != en["disclaimer"])

    # An unrecognised lang value must degrade to English, not raise or emit
    # a mix of the two.
    fallback = m.match(g, b, lang="fr")
    check("an unknown lang falls back to English content, not an error",
          fallback["disclaimer"] == en["disclaimer"])

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("kundali milan — ashtakoot and mangal dosha: all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
