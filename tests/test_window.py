"""Date-window analysis (DIVASTRO-119).

`app.interpret.window.analyse_window` on the fixture chart used by
test_dashboard / test_api_dashboard (Pune, 14 Aug 1999 14:07), for windows in
Oct 2026. The Moon is checked against an independent Swiss Ephemeris
computation (direct `swe.calc_ut` with Lahiri, sampled every 10 minutes), not
against the module's own helpers.

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.test_window
"""

from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import swisseph as swe  # noqa: E402

from app import rashifal_pages  # noqa: E402
from app.astro import panchang as pe  # noqa: E402
from app.chart_service import SIGNS, BirthData, build, vimshottari  # noqa: E402
from app.interpret import window as W  # noqa: E402
from app.interpret.periods import parse_period  # noqa: E402
from app.interpret.topics import TOPIC_BY_KEY  # noqa: E402

IST = ZoneInfo("Asia/Kolkata")
TODAY = dt.date(2026, 10, 3)
failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def chart():
    return build(BirthData(
        name="Sanskruti", date="1999-08-14", time="14:07",
        latitude=18.5204, longitude=73.8567, timezone="Asia/Kolkata",
        place="Pune, Maharashtra, India", zodiac="sidereal",
        ayanamsa="lahiri", house_system="Whole Sign"))


def moon_lon(moment: dt.datetime) -> float:
    """Independent sidereal Moon: straight Swiss Ephemeris, Lahiri."""
    pe._ephemeris()
    u = moment.astimezone(dt.timezone.utc)
    jd = swe.julday(u.year, u.month, u.day, u.hour + u.minute / 60 + u.second / 3600)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    return swe.calc_ut(jd, swe.MOON, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)[0][0] % 360.0


def main() -> int:
    session = chart()
    natal_moon_sign = SIGNS.index(session.chart.get_object("Moon").sign)
    natal_nak = int(session.chart.get_object("Moon").longitude // (360 / 27))

    print("1. The scheme matches the daily rashifal pages")
    check("Moon favourable/challenging houses agree with rashifal_pages",
          W.MOON_FAVOURABLE == rashifal_pages.MOON_FAVOURABLE
          and W.MOON_CHALLENGING == rashifal_pages.MOON_CHALLENGING)
    check("Saturn / Jupiter / node schemes agree",
          W.SATURN_FAVOURABLE == rashifal_pages.SATURN_FAVOURABLE
          and W.JUPITER_FAVOURABLE == rashifal_pages.JUPITER_FAVOURABLE
          and W.NODE_FAVOURABLE == rashifal_pages.NODE_FAVOURABLE)
    check("moon_tone agrees for all 12 houses",
          all(W.moon_tone(h) == rashifal_pages.moon_tone(h) for h in range(1, 13)))

    print("\n2. Tara bala rule")
    check("own nakshatra is Janma", W.tara_of(4, 4) == "Janma")
    check("next nakshatra is Sampat", W.tara_of(4, 5) == "Sampat")
    check("10th from janma wraps to Janma again", W.tara_of(0, 9) == "Janma")
    check("the 27th is Param-mitra (count wraps the zodiac)", W.tara_of(5, 4) == "Param-mitra")
    check("3rd/5th/7th are the unfavourable three",
          [W.tara_of(0, i) for i in (2, 4, 6)] == ["Vipat", "Pratyak", "Naidhana"]
          and W.TARA_BAD == {"Vipat", "Pratyak", "Naidhana"})

    print("\n3. 10–20 Oct 2026 (the QuestionLog #54 window)")
    p = parse_period("how is my 10th oct to 20th oct", TODAY)
    w = W.analyse_window(session, p, None)
    days = w["days"]
    check("11 days, 10 Oct to 20 Oct", len(days) == 11 and days[0]["date"] == dt.date(2026, 10, 10)
          and days[-1]["date"] == dt.date(2026, 10, 20))

    # Tara: independent nakshatra at that day's sunrise.
    taras_ok = True
    for d in days:
        nak = int(moon_lon(d["sunrise"]) // (360 / 27))
        want = W.TARAS[((nak - natal_nak) % 27) % 9]
        if d["tara"] != want or d["nakshatra"] != nak:
            taras_ok = False
            print(f"     {d['date']}: got {d['tara']}/{d['nakshatra']}, want {want}/{nak}")
    check("tara of each day matches an independent sunrise-nakshatra count", taras_ok)
    check("tara sequence for the window (fixture)",
          [d["tara"] for d in days] == ["Sampat", "Vipat", "Kshema", "Pratyak", "Sadhana",
                                        "Naidhana", "Naidhana", "Mitra", "Param-mitra",
                                        "Janma", "Sampat"],
          str([d["tara"] for d in days]))

    # Dasha agrees with chart_service.vimshottari at month resolution.
    vim = vimshottari(session, dt.datetime(2026, 10, 10, 0, 0, tzinfo=IST))
    ds = w["dasha"]
    check("mahadasha matches chart_service.vimshottari",
          ds["maha"]["lord"] == vim["mahadasha"]["lord"]
          and f"{ds['maha']['start']:%b %Y}" == vim["mahadasha"]["start"]
          and f"{ds['maha']['end']:%b %Y}" == vim["mahadasha"]["end"], str(ds["maha"]))
    check("antardasha matches chart_service.vimshottari",
          ds["antar"]["lord"] == vim["antardasha"]["lord"]
          and f"{ds['antar']['start']:%b %Y}" == vim["antardasha"]["start"]
          and f"{ds['antar']['end']:%b %Y}" == vim["antardasha"]["end"], str(ds["antar"]))
    pd = ds["pratyantar"]
    check("a pratyantardasha is reported and contains the window start",
          pd is not None and pd["start"] <= dt.date(2026, 10, 10) <= pd["end"], str(pd))
    check("pratyantardasha lies inside the antardasha",
          ds["antar"]["start"] <= pd["start"] and pd["end"] <= ds["antar"]["end"])

    obs = {o["key"]: o for o in w["observances"]}
    check("Sharad Navratri begins 11 Oct 2026",
          "navratri" in obs and obs["navratri"]["date"] == dt.date(2026, 10, 11))
    check("Navratri span closes 19 Oct 2026 (eve of Dussehra)",
          obs.get("navratri", {}).get("until") == dt.date(2026, 10, 19))
    check("Dussehra 20 Oct 2026", obs.get("dussehra", {}).get("date") == dt.date(2026, 10, 20))

    inside = all(p.start <= d["date"] <= p.end for d in w["best"] + w["caution"])
    check("best days non-empty", bool(w["best"]), str([d["date"] for d in w["best"]]))
    check("caution days non-empty", bool(w["caution"]), str([d["date"] for d in w["caution"]]))
    check("best and caution days are dated inside the window", inside)
    check("no day is both best and caution",
          not ({d["date"] for d in w["best"]} & {d["date"] for d in w["caution"]}))

    text = W.render(w)
    check("answer names both ends of the window",
          "10 Oct 2026" in text and "20 Oct 2026" in text)
    check("answer has the Timing section with dated bullets",
          "### Timing" in text and "- **10 Oct 2026 (Sat)**" in text)
    check("answer lists Navratri and Dussehra",
          "Sharad Navratri (11 Oct 2026 – 19 Oct 2026)" in text and "Dussehra" in text)
    hi = W.render(w, "hi")
    check("Hindi answer is in Devanagari with Hindi month names",
          "अक्टूबर" in hi and "दशहरा" in hi and "चल रही दशा" in hi and "Oct 2026" not in hi)

    print("\n4. Chandrashtama across October 2026, against an independent Moon")
    p = parse_period("how is october", TODAY)
    w = W.analyse_window(session, p, None)
    eighth = (natal_moon_sign + 7) % 12
    expected = set()
    for i in range(31):
        day = dt.date(2026, 10, 1) + dt.timedelta(days=i)
        start = dt.datetime.combine(day, dt.time(), IST)
        # Every 10 minutes, ignoring the first 5 (the module folds an ingress
        # in the first minutes after midnight into the day's start).
        for m in range(5, 24 * 60, 10):
            if int(moon_lon(start + dt.timedelta(minutes=m)) // 30) == eighth:
                expected.add(day)
                break
    got = {d["date"] for d in w["days"] if d["chandrashtama"]}
    check("Chandrashtama days match the independent scan", got == expected,
          f"got {sorted(got)}, want {sorted(expected)}")
    check("there is at least one Chandrashtama span in October", bool(w["chandrashtama"]))
    spans_ok = True
    for s in w["chandrashtama"]:
        a, b = s["from"], s["until"]
        inside_a = int(moon_lon(a + dt.timedelta(minutes=2)) // 30) == eighth
        before_a = int(moon_lon(a - dt.timedelta(minutes=2)) // 30) != eighth
        inside_b = int(moon_lon(b - dt.timedelta(minutes=2)) // 30) == eighth
        after_b = int(moon_lon(b + dt.timedelta(minutes=2)) // 30) != eighth
        if not (inside_a and before_a and inside_b and after_b):
            spans_ok = False
            print(f"     span {a} – {b} does not bracket the Moon in {SIGNS[eighth]}")
    check("each Chandrashtama span starts and ends on the Moon's ingress (±2 min)", spans_ok)
    every_cs_is_caution = all(d["score"] < 0 for d in w["days"] if d["moon_house"] == 8)
    check("a day with the Moon in the 8th all day scores below zero", every_cs_is_caution)
    moon_ok = all(
        W.house_from(natal_moon_sign, int(moon_lon(
            dt.datetime.combine(d["date"], dt.time(12), IST)) // 30)) in
        {W.house_from(natal_moon_sign, s["sign"]) for s in d["segments"]}
        for d in w["days"])
    check("each day's Moon house agrees with an independent noon position", moon_ok)

    print("\n5. Slow planets and topic weighting (Oct–Dec 2026, career)")
    p = parse_period("career from october to december", TODAY)
    w = W.analyse_window(session, p, TOPIC_BY_KEY["career"])
    jup = next(s for s in w["slow"] if s["planet"] == "Jupiter")
    ingress = [e for e in jup["events"] if e["kind"] == "ingress"]
    check("Jupiter changes sign inside the window", bool(ingress), str(jup["events"]))
    if ingress:
        day = ingress[0]["date"]
        pe._ephemeris()

        def jsign(d: dt.date) -> int:
            m = dt.datetime.combine(d, dt.time(12), IST).astimezone(dt.timezone.utc)
            jd = swe.julday(m.year, m.month, m.day, m.hour + m.minute / 60)
            swe.set_sid_mode(swe.SIDM_LAHIRI)
            return int(swe.calc_ut(jd, swe.JUPITER, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)[0][0] // 30)
        check("the Jupiter ingress date is the day its sign changes (independent check)",
              jsign(day - dt.timedelta(days=1)) != jsign(day + dt.timedelta(days=1))
              and jsign(day + dt.timedelta(days=1)) == ingress[0]["sign"], str(ingress[0]))
    sat = next(s for s in w["slow"] if s["planet"] == "Saturn")
    check("Saturn's station is reported with a date inside the window",
          any(e["kind"] in ("direct", "retrograde") and p.start <= e["date"] <= p.end
              for e in sat["events"]), str(sat["events"]))
    rahu = next(s for s in w["slow"] if s["planet"] == "Rahu")
    ketu = next(s for s in w["slow"] if s["planet"] == "Ketu")
    check("Ketu is opposite Rahu", (rahu["sign"] + 6) % 12 == ketu["sign"])
    check("the window is weighted for career", w["weighted"] and w["topic_houses"] == [10, 6])
    boosted = [d for d in w["days"] if ("moon_topic_house", d["lagna_house"]) in d["boosts"]]
    check("every day with the Moon in the 10th/6th from Lagna carries the career boost",
          all(d["lagna_house"] in (10, 6) for d in boosted)
          and len(boosted) == sum(1 for d in w["days"] if d["lagna_house"] in (10, 6)),
          f"{len(boosted)} boosted")
    text = W.render(w)
    check("the method note says how the topic was weighed",
          "10th, 6th house from the Lagna" in text and "not a guaranteed outcome" in text)
    check("a 92-day window still gets daily detail", w["period"]["detail"] == "daily")

    print("\n6. Flags in the answer")
    p = parse_period("how was september", TODAY)
    text = W.render(W.analyse_window(session, p, None))
    check("a past window says so", "already in the past" in text)
    p = parse_period("how is march for me", TODAY)
    text = W.render(W.analyse_window(session, p, None))
    check("a rolled year says so", "read it as 2027" in text)
    check("a 31-day month gets the day-by-day list", "**Day by day:**" in text)
    p = parse_period("october to march", TODAY)
    text = W.render(W.analyse_window(session, p, None))
    check("a long window gets the month-by-month summary", "**Month by month:**" in text)

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("window analysis: all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
