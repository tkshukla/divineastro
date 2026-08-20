"""Panchang, Sade Sati and Kaal Sarp.

A panchang that is subtly wrong is worse than no panchang, so most of this file
is not a unit test in the usual sense — it is a cross-check against numbers
somebody else published. The reference is **Drik Panchang**
(drikpanchang.com/panchang/day-panchang.html), the almanac most Indian users
compare against, read for Delhi (geoname 1273294, 28.65195N 77.23149E) and
Varanasi (geoname 1253405, 25.31668N 82.97684E) with its default Lahiri
ayanamsa. Three dates are checked limb by limb:

    2026-01-15  Delhi      Thursday   Krishna Dwadashi
    2026-08-05  Delhi      Wednesday  Krishna Saptami   (no Abhijit)
    2026-03-21  Varanasi   Saturday   Shukla Tritiya

Names are asserted exactly. Times are allowed two minutes, which is roughly the
width of the disagreement between two published panchangs anyway — Drik prints
whole minutes and rounds, and its stated coordinates for a city are not
necessarily to the metre.

No server, no database, no network. Run it with:

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.test_panchang
"""

from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.astro.panchang import (            # noqa: E402
    GULIKA_SEGMENT, KAAL_SARP_TYPES, MOVABLE_KARANAS, NAKSHATRAS, RAHU_SEGMENT,
    SIGNS, TITHI_NAMES, YAMAGANDA_SEGMENT, YOGA_NAMES,
    daily_panchang, kaal_sarp, kaal_sarp_from_longitudes, panchang_at,
    sade_sati, sade_sati_for_moon_sign,
)

IST = ZoneInfo("Asia/Kolkata")
DELHI = (28.65195, 77.23149, "Asia/Kolkata")
VARANASI = (25.31668, 82.97684, "Asia/Kolkata")
TOLERANCE_S = 120

failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def moment(iso: str | None) -> dt.datetime | None:
    return dt.datetime.fromisoformat(iso) if iso else None


def clock(iso: str | None) -> str:
    return moment(iso).strftime("%H:%M:%S") if iso else "-"


def near(iso: str | None, expected: str, tolerance: int = TOLERANCE_S) -> tuple[bool, str]:
    """Is `iso` within tolerance of the published 'YYYY-MM-DD HH:MM'?"""
    if iso is None:
        return False, "missing"
    got = moment(iso)
    want = dt.datetime.strptime(expected, "%Y-%m-%d %H:%M").replace(tzinfo=IST)
    delta = abs((got - want).total_seconds())
    return delta <= tolerance, f"{got:%Y-%m-%d %H:%M:%S} vs published {expected} ({delta:.0f}s)"


# --------------------------------------------------------------------------
# Published reference data — Drik Panchang, default Lahiri ayanamsa
# --------------------------------------------------------------------------

PUBLISHED = [
    {
        "date": "2026-01-15", "place": DELHI, "label": "Delhi, Thu 15 Jan 2026",
        "sunrise": "2026-01-15 07:15", "sunset": "2026-01-15 17:46",
        "moonrise": "2026-01-16 05:26", "moonset": "2026-01-15 14:29",
        "vara": "Guruvara", "paksha": "Krishna",
        "tithi": [("Dwadashi", "2026-01-15 20:16")],
        "nakshatra": [("Jyeshtha", "2026-01-16 05:47")],
        "yoga": [("Vriddhi", "2026-01-15 20:38")],
        "karana": [("Taitila", "2026-01-15 20:16")],
        "rahu": ("2026-01-15 13:49", "2026-01-15 15:08"),
        "yamaganda": ("2026-01-15 07:15", "2026-01-15 08:34"),
        "gulika": ("2026-01-15 09:53", "2026-01-15 11:12"),
        "abhijit": ("2026-01-15 12:10", "2026-01-15 12:52"),
    },
    {
        "date": "2026-08-05", "place": DELHI, "label": "Delhi, Wed 5 Aug 2026",
        "sunrise": "2026-08-05 05:45", "sunset": "2026-08-05 19:09",
        "moonrise": "2026-08-05 23:04", "moonset": "2026-08-05 11:52",
        "vara": "Budhavara", "paksha": "Krishna",
        "tithi": [("Saptami", "2026-08-05 20:42")],
        "nakshatra": [("Ashwini", "2026-08-05 21:18")],
        "yoga": [("Shula", "2026-08-05 17:29")],
        # Drik prints three karanas on this date; the middle one pins the
        # movable cycle, which is the part most likely to be off by one.
        "karana": [("Vishti", "2026-08-05 09:26"), ("Bava", "2026-08-05 20:42")],
        "rahu": ("2026-08-05 12:27", "2026-08-05 14:07"),
        "yamaganda": ("2026-08-05 07:25", "2026-08-05 09:06"),
        "gulika": ("2026-08-05 10:46", "2026-08-05 12:27"),
        "abhijit": None,                     # suppressed on Wednesday
    },
    {
        "date": "2026-03-21", "place": VARANASI, "label": "Varanasi, Sat 21 Mar 2026",
        "sunrise": "2026-03-21 06:01", "sunset": "2026-03-21 18:09",
        "moonrise": "2026-03-21 07:16", "moonset": "2026-03-21 20:36",
        "vara": "Shanivara", "paksha": "Shukla",
        "tithi": [("Tritiya", "2026-03-21 23:56")],
        "nakshatra": [("Ashwini", "2026-03-22 00:37")],
        "yoga": [("Indra", "2026-03-21 19:01")],
        "karana": [("Taitila", "2026-03-21 13:14"), ("Gara", "2026-03-21 23:56")],
        "rahu": ("2026-03-21 09:03", "2026-03-21 10:34"),
        "yamaganda": ("2026-03-21 13:36", "2026-03-21 15:07"),
        "gulika": ("2026-03-21 06:01", "2026-03-21 07:32"),
        "abhijit": ("2026-03-21 11:41", "2026-03-21 12:30"),
    },
]

# The classical weekday orderings, restated here independently of the module so
# a typo in the module cannot be validated by itself. 1-based eighth of the
# daylight span, indexed Sunday..Saturday.
CLASSICAL_RAHU = {"Sunday": 8, "Monday": 2, "Tuesday": 7, "Wednesday": 5,
                  "Thursday": 6, "Friday": 4, "Saturday": 3}
CLASSICAL_YAMAGANDA = {"Sunday": 5, "Monday": 4, "Tuesday": 3, "Wednesday": 2,
                       "Thursday": 1, "Friday": 7, "Saturday": 6}
CLASSICAL_GULIKA = {"Sunday": 7, "Monday": 6, "Tuesday": 5, "Wednesday": 4,
                    "Thursday": 3, "Friday": 2, "Saturday": 1}


def main() -> int:
    print("\n1. The limbs are always in range and always end in the future")
    spread = [
        ("2026-01-15", DELHI), ("2026-06-30", DELHI), ("2025-11-02", VARANASI),
        ("2024-02-29", VARANASI), ("2026-08-05", (19.076, 72.8777, "Asia/Kolkata")),
        ("2026-04-11", (51.5074, -0.1278, "Europe/London")),
        ("2026-09-23", (-33.8688, 151.2093, "Australia/Sydney")),
        ("2026-12-25", (40.7128, -74.0060, "America/New_York")),
    ]
    counts = {"tithi": 30, "nakshatra": 27, "yoga": 27, "karana": 60}
    ok_range = ok_order = ok_aware = ok_cover = True
    for date, place in spread:
        p = daily_panchang(date, *place)
        rise = moment(p["vara"]["starts"])
        for limb, total in counts.items():
            entries = p[limb]
            if not entries:
                ok_cover = False
                continue
            for e in entries:
                if not 0 <= e["index"] < total:
                    ok_range = False
                starts, ends = moment(e["starts"]), moment(e["ends"])
                if not (ends > starts):
                    ok_order = False
                if starts.tzinfo is None or ends.tzinfo is None:
                    ok_aware = False
            # The limb running at the reference instant must still be running.
            if not (moment(entries[0]["ends"]) > rise >= moment(entries[0]["starts"])):
                ok_order = False
    check("every index is inside its cycle", ok_range)
    check("every limb ends strictly after it starts, and after sunrise", ok_order)
    check("no naive datetime escapes", ok_aware)
    check("all four limbs are populated everywhere", ok_cover)

    p = daily_panchang("2026-01-15", *DELHI)
    check("names come from the canonical tables",
          p["tithi"][0]["name"] in TITHI_NAMES + ["Amavasya"]
          and p["nakshatra"][0]["name"] in NAKSHATRAS
          and p["yoga"][0]["name"] in YOGA_NAMES
          and p["karana"][0]["name"] in MOVABLE_KARANAS + ["Shakuni", "Chatushpada",
                                                           "Naga", "Kimstughna"])
    check("the offset is stated, not implied",
          p["location"]["utc_offset"] == "+0530", p["location"]["utc_offset"])
    check("nakshatra carries a pada 1-4", p["nakshatra"][0]["pada"] in (1, 2, 3, 4),
          str(p["nakshatra"][0]["pada"]))
    check("the ayanamsa used is reported",
          p["ayanamsa"]["name"] == "Lahiri" and 24.0 < p["ayanamsa"]["degrees"] < 24.5,
          f"{p['ayanamsa']['name']} {p['ayanamsa']['degrees']}")

    print("\n2. Cross-checked against published Drik Panchang values")
    for ref in PUBLISHED:
        print(f"  -- {ref['label']}")
        p = daily_panchang(ref["date"], *ref["place"])

        check("   vara", p["vara"]["name"] == ref["vara"],
              f"{p['vara']['name']} vs {ref['vara']}")
        check("   paksha", p["tithi"][0]["paksha"] == ref["paksha"],
              f"{p['tithi'][0]['paksha']} vs {ref['paksha']}")
        for field, published in (("sun.rise", ref["sunrise"]), ("sun.set", ref["sunset"]),
                                 ("moon.rise", ref["moonrise"]), ("moon.set", ref["moonset"])):
            body, key = field.split(".")
            ok, detail = near(p[body][key], published)
            check(f"   {field}", ok, detail)

        for limb in ("tithi", "nakshatra", "yoga", "karana"):
            for i, (name, ends) in enumerate(ref[limb]):
                entry = p[limb][i] if i < len(p[limb]) else None
                check(f"   {limb}[{i}] name is exactly {name}",
                      entry is not None and entry["name"] == name,
                      entry["name"] if entry else "missing")
                ok, detail = near(entry["ends"] if entry else None, ends)
                check(f"   {limb}[{i}] ends", ok, detail)

    print("\n3. Rahu Kaal, Yamaganda and Gulika Kaal")
    for ref in PUBLISHED:
        p = daily_panchang(ref["date"], *ref["place"])
        rise, sett = moment(p["sun"]["rise"]), moment(p["sun"]["set"])
        span = (sett - rise).total_seconds()
        weekday = p["vara"]["weekday"]

        for key, published, classical in (
            ("rahu_kaal", ref["rahu"], CLASSICAL_RAHU),
            ("yamaganda", ref["yamaganda"], CLASSICAL_YAMAGANDA),
            ("gulika_kaal", ref["gulika"], CLASSICAL_GULIKA),
        ):
            w = p["muhurta"][key]
            start, end = moment(w["start"]), moment(w["end"])
            check(f"  {ref['label'][:8]} {weekday} {key} lies inside daylight",
                  rise <= start < end <= sett,
                  f"{clock(w['start'])}-{clock(w['end'])} in "
                  f"{clock(p['sun']['rise'])}-{clock(p['sun']['set'])}")
            eighth = (end - start).total_seconds()
            check(f"  {ref['label'][:8]} {key} is one eighth of the day",
                  abs(eighth - span / 8.0) < 1.0, f"{eighth:.0f}s vs {span / 8.0:.0f}s")
            check(f"  {ref['label'][:8]} {key} is segment {classical[weekday]} on {weekday}",
                  w["segment"] == classical[weekday],
                  f"got {w['segment']}")
            for label, iso, want in (("start", w["start"], published[0]),
                                     ("end", w["end"], published[1])):
                ok, detail = near(iso, want)
                check(f"  {ref['label'][:8]} {key} {label}", ok, detail)

    # The three published days only cover Thursday, Wednesday and Saturday, so
    # sweep a whole week to prove the tables are right end to end.
    ok_week = True
    detail = ""
    for offset in range(7):
        date = dt.date(2026, 3, 15) + dt.timedelta(days=offset)
        p = daily_panchang(date, *DELHI)
        weekday = p["vara"]["weekday"]
        got = (p["muhurta"]["rahu_kaal"]["segment"],
               p["muhurta"]["yamaganda"]["segment"],
               p["muhurta"]["gulika_kaal"]["segment"])
        want = (CLASSICAL_RAHU[weekday], CLASSICAL_YAMAGANDA[weekday],
                CLASSICAL_GULIKA[weekday])
        if got != want:
            ok_week = False
            detail = f"{weekday}: {got} != {want}"
    check("all seven weekdays match the classical ordering", ok_week, detail)
    check("the module's own tables agree with the classical ones",
          all(RAHU_SEGMENT[i] + 1 == CLASSICAL_RAHU[d] and
              YAMAGANDA_SEGMENT[i] + 1 == CLASSICAL_YAMAGANDA[d] and
              GULIKA_SEGMENT[i] + 1 == CLASSICAL_GULIKA[d]
              for i, d in enumerate(["Sunday", "Monday", "Tuesday", "Wednesday",
                                     "Thursday", "Friday", "Saturday"])))

    print("\n4. Abhijit muhurta straddles local noon, and skips Wednesday")
    p = daily_panchang("2026-03-21", *VARANASI)
    ab = p["muhurta"]["abhijit"]
    rise, sett = moment(p["sun"]["rise"]), moment(p["sun"]["set"])
    midday = rise + (sett - rise) / 2
    centre = moment(ab["start"]) + (moment(ab["end"]) - moment(ab["start"])) / 2
    check("centred on the midpoint of daylight",
          abs((centre - midday).total_seconds()) < 30,
          f"{centre:%H:%M:%S} vs midday {midday:%H:%M:%S}")
    check("one fifteenth of the day long",
          abs(ab["duration_minutes"] - (sett - rise).total_seconds() / 900.0) < 0.1,
          f"{ab['duration_minutes']} min")
    check("absent on Wednesday",
          daily_panchang("2026-08-05", *DELHI)["muhurta"]["abhijit"] is None)
    check("present on the other six days",
          all(daily_panchang(dt.date(2026, 3, 15) + dt.timedelta(days=n),
                             *DELHI)["muhurta"]["abhijit"] is not None
              for n in range(7) if (dt.date(2026, 3, 15) + dt.timedelta(days=n)).weekday() != 2))

    print("\n5. The vara turns over at sunrise, not at midnight")
    # 16 Jan 2026 is a Friday; sunrise at Delhi is 07:14 IST. Anything before
    # that still belongs to Thursday's vedic day, Thursday's Rahu Kaal included.
    before = dt.datetime(2026, 1, 16, 3, 30, tzinfo=IST)
    after = dt.datetime(2026, 1, 16, 9, 30, tzinfo=IST)
    early, late = panchang_at(before, *DELHI), panchang_at(after, *DELHI)
    check("03:30 on Friday morning is still Guruvara",
          early["vara"]["name"] == "Guruvara" and early["vara"]["weekday"] == "Thursday",
          f"{early['vara']['name']} ({early['date']})")
    check("...and reports Thursday's date", early["date"] == "2026-01-15", early["date"])
    check("09:30 the same morning is Shukravara",
          late["vara"]["name"] == "Shukravara" and late["date"] == "2026-01-16",
          f"{late['vara']['name']} ({late['date']})")
    check("the pre-dawn instant sits inside the vedic day it was given",
          moment(early["vara"]["starts"]) <= before < moment(early["vara"]["ends"]),
          f"{early['vara']['starts']} .. {early['vara']['ends']}")
    check("Rahu Kaal before dawn is Thursday's segment, not Friday's",
          early["muhurta"]["rahu_kaal"]["segment"] == CLASSICAL_RAHU["Thursday"]
          and late["muhurta"]["rahu_kaal"]["segment"] == CLASSICAL_RAHU["Friday"],
          f"{early['muhurta']['rahu_kaal']['segment']} then "
          f"{late['muhurta']['rahu_kaal']['segment']}")
    check("a naive midday instant lands on its own civil date",
          panchang_at(dt.datetime(2026, 1, 16, 12, 0), *DELHI)["date"] == "2026-01-16")

    print("\n6. Sade Sati")
    as_of = dt.datetime(2026, 8, 16, 12, 0, tzinfo=IST)
    # Saturn is in Pisces on this date, so Aquarius Moon natives are in the
    # third phase and Leo Moon natives are nowhere near it.
    aq = sade_sati_for_moon_sign("Aquarius", as_of, timezone="Asia/Kolkata")
    leo = sade_sati_for_moon_sign("Leo", as_of, timezone="Asia/Kolkata")
    check("Aquarius Moon is in Sade Sati", aq["running"] is True)
    check("...in the third (Setting) phase over the 2nd from the Moon",
          aq["phase"]["phase"] == 3 and aq["phase"]["house_from_moon"] == 2
          and aq["phase"]["sign"] == "Pisces",
          f"{aq['phase']['phase']} {aq['phase']['name']} {aq['phase']['sign']}")
    check("Leo Moon is not", leo["running"] is False)
    check("Saturn is reported in Pisces for both",
          aq["saturn"]["sign"] == leo["saturn"]["sign"] == "Pisces", aq["saturn"]["sign"])
    check("Leo's Sade Sati is still ahead of it",
          any(p["status"] == "future" for p in leo["periods"]))

    # The phase boundaries must BE Saturn's sign ingresses. Published Saturn
    # transit tables give: enters Pisces 29 Mar 2025, crosses into Aries 3 Jun
    # 2027, retrogrades back to Pisces 20 Oct 2027, leaves Pisces for good
    # 23 Feb 2028. The DATES are asserted exactly; the clock times are given two
    # hours because published tables disagree among themselves by about that
    # much — they are not all using the same Lahiri. The most quoted table puts
    # the Pisces ingress at 23:01 IST, which is exactly Swiss Ephemeris'
    # SE_SIDM_LAHIRI_VP285; plain SE_SIDM_LAHIRI, which is what this app uses
    # and what Drik Panchang's daily pages match, puts it at 21:45 IST.
    for label, iso, published in (
        ("Saturn's ingress into Pisces", aq["phase"]["start"], "2025-03-29 23:01"),
        ("...its ingress into Aries", aq["phase"]["end"], "2027-06-03 05:00"),
    ):
        check(f"{label} falls on the published date",
              moment(iso).date().isoformat() == published[:10],
              f"{moment(iso):%Y-%m-%d %H:%M} vs published {published}")
        ok, detail = near(iso, published, tolerance=7200)
        check(f"{label} is within two hours of the published time", ok, detail)

    tail = aq["current_period"]["phases"][-1]
    check("Saturn's final exit from Pisces matches the published 23 Feb 2028",
          moment(tail["end"]).date() == dt.date(2028, 2, 23),
          f"{moment(tail['end']):%Y-%m-%d %H:%M}")
    check("the retrograde return to Pisces matches the published 20 Oct 2027",
          moment(tail["start"]).date() == dt.date(2027, 10, 20),
          f"{moment(tail['start']):%Y-%m-%d %H:%M}")

    # Independently: re-derive the ingress by asking for the Moon sign whose
    # 1st house Saturn is entering, and confirm the two agree.
    pisces = sade_sati_for_moon_sign("Pisces", as_of, timezone="Asia/Kolkata")
    peak = next(f for f in pisces["current_period"]["phases"]
                if f["house_from_moon"] == 1 and f["status"] == "current")
    check("the same instant is the Peak phase for a Pisces Moon",
          peak["start"] == aq["phase"]["start"],
          f"{peak['start']} vs {aq['phase']['start']}")

    period = aq["current_period"]
    phases = period["phases"]
    check("the running period spans the three signs from the 12th to the 2nd",
          {f["house_from_moon"] for f in phases} == {12, 1, 2},
          str(sorted({f["house_from_moon"] for f in phases})))
    check("it starts when Saturn enters the 12th",
          phases[0]["house_from_moon"] == 12 and period["start"] == phases[0]["start"])
    check("it runs about seven and a half years (longer, given retrogression)",
          7.4 <= period["years"] <= 8.6, str(period["years"]))
    check("phases are contiguous or separated only by retrograde gaps",
          all(moment(phases[i]["end"]) <= moment(phases[i + 1]["start"])
              for i in range(len(phases) - 1)))
    check("past and future periods are both offered",
          any(x["status"] == "past" for x in aq["periods"])
          and any(x["status"] == "future" for x in aq["periods"]),
          str([x["status"] for x in aq["periods"]]))
    check("every timestamp carries the requested zone",
          all(moment(x["start"]).utcoffset() == dt.timedelta(hours=5, minutes=30)
              for x in aq["periods"] if x["start"]))

    print("\n7. Dhaiya / Kantaka Shani rides along")
    check("Leo Moon is under Ashtama Shani (Saturn 8th from the Moon)",
          leo["dhaiya"]["running"] is True
          and leo["dhaiya"]["current"]["phases"][0]["house_from_moon"] == 8,
          str(leo["dhaiya"]["current"]["phases"][0]["name"] if leo["dhaiya"]["current"] else None))
    check("Aquarius Moon is not — Sade Sati and Dhaiya cannot overlap",
          aq["dhaiya"]["running"] is False)
    check("dhaiya only ever names the 4th or the 8th",
          all(f["house_from_moon"] in (4, 8)
              for d in aq["dhaiya"]["periods"] for f in d["phases"]))
    check("Saturn's house from the Moon is consistent with both verdicts",
          leo["saturn"]["house_from_moon"] == 8 and aq["saturn"]["house_from_moon"] == 2,
          f"Leo {leo['saturn']['house_from_moon']}, Aquarius {aq['saturn']['house_from_moon']}")

    print("\n8. Sade Sati straight off a natal chart")
    from app.chart_service import BirthData, build      # noqa: E402  (slow import)

    def chart(zodiac: str = "sidereal") -> object:
        return build(BirthData(
            name="Test", date="1986-08-19", time="11:59", latitude=26.26, longitude=82.07,
            timezone="Asia/Kolkata", place="Sultanpur", zodiac=zodiac, ayanamsa="lahiri",
            house_system="Whole Sign",
        ))

    sidereal_chart, tropical_chart = chart("sidereal"), chart("tropical")
    from_chart = sade_sati(sidereal_chart, dt.date(2026, 8, 16))
    check("the Moon sign is read sidereally",
          from_chart["moon_sign"] == "Capricorn", from_chart["moon_sign"])
    check("it agrees with the sign-only entry point",
          from_chart["running"]
          == sade_sati_for_moon_sign("Capricorn", as_of, timezone="Asia/Kolkata")["running"])
    check("a tropical chart is converted, not judged in the wrong zodiac",
          sade_sati(tropical_chart, dt.date(2026, 8, 16))["moon_sign"]
          == from_chart["moon_sign"],
          sade_sati(tropical_chart, dt.date(2026, 8, 16))["moon_sign"])
    check("it answers in the native's own timezone",
          from_chart["timezone"] == "Asia/Kolkata", from_chart["timezone"])

    print("\n9. Kaal Sarp Dosha")
    whole_sign = [i * 30.0 for i in range(12)]           # Aries rising
    hemmed = {"Sun": 20.0, "Moon": 45.0, "Mars": 70.0, "Mercury": 95.0,
              "Jupiter": 120.0, "Venus": 150.0, "Saturn": 175.0}
    forms = kaal_sarp_from_longitudes(hemmed, rahu=10.0, cusps=whole_sign)
    check("seven planets inside the axis forms the yoga", forms["forms"] is True)
    check("it is complete, not partial", forms["partial"] is False)
    check("direction is anuloma when every planet leads Rahu",
          forms["direction"] == "anuloma", str(forms["direction"]))
    check("Rahu in the 1st names it Anant",
          forms["type"]["name"] == "Anant" and forms["type"]["rahu_house"] == 1,
          str(forms["type"]))
    check("nothing is listed as breaking it", forms["breaking"] == [])

    escaped = {**hemmed, "Saturn": 200.0}               # Saturn crosses Ketu
    broken = kaal_sarp_from_longitudes(escaped, rahu=10.0, cusps=whole_sign)
    check("one planet outside the axis breaks it", broken["forms"] is False)
    check("...and that planet is named", broken["breaking"] == ["Saturn"],
          str(broken["breaking"]))
    check("no type is assigned when it does not form", broken["type"] is None)

    touching = {**hemmed, "Saturn": 189.6}              # 0.4° off the Ketu end
    partial = kaal_sarp_from_longitudes(touching, rahu=10.0, cusps=whole_sign)
    check("a planet sitting on the axis makes it partial",
          partial["forms"] is True and partial["partial"] is True)
    check("...and says which planet and which node",
          partial["conjunct_axis"] == [{"planet": "Saturn", "node": "Ketu", "orb": 0.4}],
          str(partial["conjunct_axis"]))

    mirrored = {k: (v + 180.0) % 360.0 for k, v in hemmed.items()}
    reverse = kaal_sarp_from_longitudes(mirrored, rahu=10.0, cusps=whole_sign)
    check("the mirror image also hems, and is marked vilom",
          reverse["forms"] is True and reverse["direction"] == "vilom",
          str(reverse["direction"]))

    for house in range(1, 13):
        rotated = {k: (v + 30.0 * (house - 1)) % 360.0 for k, v in hemmed.items()}
        r = kaal_sarp_from_longitudes(rotated, rahu=(10.0 + 30.0 * (house - 1)) % 360.0,
                                      cusps=whole_sign)
        if not (r["forms"] and r["type"]["name"] == KAAL_SARP_TYPES[house - 1]
                and r["type"]["rahu_house"] == house):
            check(f"rotating Rahu into house {house} names it "
                  f"{KAAL_SARP_TYPES[house - 1]}", False, str(r["type"]))
            break
    else:
        check("all twelve types are reachable by rotating Rahu through the houses", True)

    timeless = kaal_sarp_from_longitudes(hemmed, rahu=10.0, cusps=None)
    check("with no birth time the geometry still answers", timeless["forms"] is True)
    check("...but the named type is withheld", timeless["type"] is None)
    check("...and the reason is stated",
          any("house Rahu occupies" in n for n in timeless["notes"]))

    from_real = kaal_sarp(sidereal_chart)
    check("a real chart runs through the chart entry point",
          isinstance(from_real["forms"], bool)
          and len(from_real["planets"]) == 7, str(len(from_real["planets"])))
    check("it uses the mean node, as Vedic practice does",
          from_real["rahu"]["node"] == "mean")
    check("Ketu is exactly opposite Rahu",
          abs((from_real["ketu"]["longitude"] - from_real["rahu"]["longitude"]) % 360.0
              - 180.0) < 1e-6)
    check("tropical and sidereal charts give the same Rahu",
          abs(kaal_sarp(tropical_chart)["rahu"]["longitude"]
              - from_real["rahu"]["longitude"]) < 0.05,
          f"{kaal_sarp(tropical_chart)['rahu']['longitude']} vs "
          f"{from_real['rahu']['longitude']}")
    check("the disputed status of the yoga is stated, not hidden",
          any("modern addition" in n for n in from_real["notes"]))

    print("\n10. A polar location degrades instead of raising")
    dark = daily_panchang("2026-12-21", 78.22, 15.63, "Arctic/Longyearbyen")
    check("polar night returns a dict, not an exception", isinstance(dark, dict))
    check("it says the Sun neither rises nor sets",
          dark["sun"]["rises"] is False and dark["sun"]["sets"] is False
          and dark["sun"]["rise"] is None and dark["sun"]["set"] is None)
    check("the three inauspicious windows are None, not guessed",
          dark["muhurta"]["rahu_kaal"] is None
          and dark["muhurta"]["yamaganda"] is None
          and dark["muhurta"]["gulika_kaal"] is None
          and dark["muhurta"]["abhijit"] is None)
    check("it admits it fell back to midnight",
          dark["reckoned_from"] == "midnight" and bool(dark["notes"]),
          dark["reckoned_from"])
    check("the five limbs are still computed", all(dark[k] for k in
          ("tithi", "nakshatra", "yoga", "karana")))
    check("the vara is still named", dark["vara"]["name"] == "Somavara",
          dark["vara"]["name"])

    midnight_sun = daily_panchang("2026-06-21", 78.22, 15.63, "Arctic/Longyearbyen")
    check("midnight sun degrades the same way",
          midnight_sun["sun"]["rises"] is False
          and midnight_sun["muhurta"]["rahu_kaal"] is None)

    edge = daily_panchang("2026-09-22", 78.22, 15.63, "Arctic/Longyearbyen")
    check("a day that does have a sunrise up there still works",
          edge["sun"]["rises"] is True and edge["muhurta"]["rahu_kaal"] is not None,
          str(edge["sun"]["rise"]))
    check("panchang_at survives a polar pre-dawn instant",
          isinstance(panchang_at(dt.datetime(2026, 12, 21, 3, 0,
                                             tzinfo=ZoneInfo("Arctic/Longyearbyen")),
                                 78.22, 15.63, "Arctic/Longyearbyen"), dict))

    print("\n11. The result is JSON-ready")
    import json
    payload = {
        "panchang": daily_panchang("2026-01-15", *DELHI),
        "sade_sati": aq,
        "kaal_sarp": forms,
    }
    try:
        json.dumps(payload)
        check("everything serialises with no custom encoder", True)
    except TypeError as exc:
        check("everything serialises with no custom encoder", False, str(exc))
    check("no bare datetime survives serialisation",
          isinstance(payload["panchang"]["sun"]["rise"], str))
    check("SIGNS is the shared table, not a private copy",
          SIGNS[0] == "Aries" and len(SIGNS) == 12)

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("panchang, sade sati and kaal sarp: all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
