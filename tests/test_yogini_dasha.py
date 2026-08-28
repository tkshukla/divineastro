"""Yogini Dasha: the alternate 8-fold dasha from chart_service.py, and its
result texts in app.astro.delineation.

Pure unit tests against lightweight stand-ins for the two attributes
yogini_dasha() actually touches (session.chart.get_object("Moon").longitude,
session.birth.local_datetime / .timezone), so the date arithmetic can be
checked exactly without going through the ephemeris. Finishes against a real
chart_service.build() session, the same pattern test_delineation.py and
test_vargas.py use.

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.test_yogini_dasha
"""

from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import chart_service as cs
from app.astro import delineation as d

failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


class _StubMoon:
    def __init__(self, longitude: float) -> None:
        self.longitude = longitude


class _StubChart:
    def __init__(self, moon_longitude: float) -> None:
        self._moon = _StubMoon(moon_longitude)

    def get_object(self, name: str):
        assert name == "Moon"
        return self._moon


class _StubBirth:
    def __init__(self, local_datetime: dt.datetime, timezone: str) -> None:
        self.local_datetime = local_datetime
        self.timezone = timezone


class _StubSession:
    """Just enough of a ChartSession for yogini_dasha() to run against."""

    def __init__(self, moon_longitude: float, birth_dt: dt.datetime, timezone: str = "UTC") -> None:
        self.chart = _StubChart(moon_longitude)
        self.birth = _StubBirth(birth_dt, timezone)


def lon_for_nakshatra(nakshatra_index: int, frac: float = 0.0) -> float:
    """Moon longitude that lands `frac` of the way through the nakshatra at
    `nakshatra_index` (0-based, Ashwini=0)."""
    span = 360.0 / 27.0
    return nakshatra_index * span + frac * span


def main() -> int:
    print("\n1. _yogini_start_index — this source's own (n+3) mod 8 rule")
    # Expected mapping, worked by hand from the rule for nakshatra numbers 1-9
    # (1-based): remainder 0 reads as Sankata (index 7).
    expected = {1: 3, 2: 4, 3: 5, 4: 6, 5: 7, 6: 0, 7: 1, 8: 2, 9: 3}
    check("nakshatra numbers 1-9 map to the expected starting Yogini index",
          all(cs._yogini_start_index(n) == i for n, i in expected.items()),
          str({n: cs._yogini_start_index(n) for n in expected}))
    check("the mapping repeats every 8 nakshatras",
          all(cs._yogini_start_index(n) == cs._yogini_start_index(n + 8)
              for n in range(1, 20)))
    check("every one of the 27 real nakshatra numbers resolves to a valid index",
          all(0 <= cs._yogini_start_index(n) <= 7 for n in range(1, 28)))

    print("\n2. YOGINI_DASHA — the table itself")
    check("eight Yoginis, years 1 through 8 in order",
          [y for _, y, _ in cs.YOGINI_DASHA] == list(range(1, 9)))
    check("the cycle totals 36 years",
          cs.YOGINI_CYCLE_YEARS == 36)
    check("Sankata is last and held to Rahu by the table (Ketu is the "
          "second-half override yogini_dasha() applies, not a table entry)",
          cs.YOGINI_DASHA[-1][0] == "Sankata" and cs.YOGINI_DASHA[-1][2] == "Rahu")

    print("\n3. yogini_dasha() — exact date arithmetic against a stubbed session")
    # Nakshatra index 0 (Ashwini) -> nakshatra_number 1 -> start index 3
    # (Bhramari, 4 years, Mars), from section 1 above. Birth exactly on the
    # nakshatra boundary (frac=0) so the first Bhramari mahadasha runs its
    # full, un-truncated length from the birth instant.
    birth_dt = dt.datetime(2000, 1, 1, tzinfo=ZoneInfo("UTC"))
    session = _StubSession(lon_for_nakshatra(0, frac=0.0), birth_dt)

    at_birth = cs.yogini_dasha(session, birth_dt)
    check("the birth nakshatra is reported correctly",
          at_birth["nakshatra"] == "Ashwini")
    check("the first mahadasha is Bhramari (Mars), per the worked mapping above",
          at_birth["mahadasha"]["name"] == "Bhramari"
          and at_birth["mahadasha"]["graha"] == "Mars",
          str(at_birth["mahadasha"]))
    check("its antardasha starts with itself, matching the Vimshottari "
          "convention this module deliberately mirrors",
          at_birth["antardasha"]["name"] == "Bhramari",
          str(at_birth["antardasha"]))
    check("three upcoming mahadashas are listed, the next three yoginis in order",
          [u["name"] for u in at_birth["upcoming"]] == ["Bhadrika", "Ulka", "Siddha"],
          str(at_birth["upcoming"]))

    print("\n4. Antardasha proportional subdivision — exact, against the stub")
    # Bhramari's own mahadasha is 4 years = 1461.0 days (4 * 365.25). Its
    # first antardasha (Bhramari-in-Bhramari) should be
    # 4 * 4 / 36 * 365.25 days long, checked by walking just past its end.
    bhramari_start = birth_dt
    first_antar_days = 4 * 4 / 36 * cs.SIDEREAL_YEAR
    just_before_end = bhramari_start + dt.timedelta(days=first_antar_days - 1)
    just_after_end = bhramari_start + dt.timedelta(days=first_antar_days + 1)
    before = cs.yogini_dasha(session, just_before_end)
    after = cs.yogini_dasha(session, just_after_end)
    check("a day before the computed antardasha boundary, it's still Bhramari-Bhramari",
          before["antardasha"]["name"] == "Bhramari", str(before["antardasha"]))
    check("a day after, the antardasha has rolled to the next Yogini in the "
          "wheel (Bhadrika, the one after Bhramari)",
          after["antardasha"]["name"] == "Bhadrika", str(after["antardasha"]))

    print("\n5. Sankata's Rahu/Ketu split — first half vs second half of its own mahadasha")
    # Nakshatra number 5 (index 4, Mrigashira) starts on Sankata (section 1).
    sankata_session = _StubSession(lon_for_nakshatra(4, frac=0.0), birth_dt)
    early = cs.yogini_dasha(sankata_session, birth_dt + dt.timedelta(days=30))
    late = cs.yogini_dasha(sankata_session, birth_dt + dt.timedelta(days=7 * cs.SIDEREAL_YEAR))
    check("early in the 8-year Sankata mahadasha, Rahu is reported",
          early["mahadasha"]["name"] == "Sankata" and early["mahadasha"]["graha"] == "Rahu",
          str(early["mahadasha"]))
    check("late in the same mahadasha (past its 4-year midpoint), Ketu is reported",
          late["mahadasha"]["name"] == "Sankata" and late["mahadasha"]["graha"] == "Ketu",
          str(late["mahadasha"]))
    # early's antardasha is Sankata-in-Sankata (the wheel starts with the
    # mahadasha's own name) — confirm its graha is the combined label rather
    # than either single lord, since the source doesn't describe subdividing
    # an antardasha-length slice of Sankata the same way.
    check("a Sankata antardasha reports the combined 'Rahu/Ketu', not one lord",
          early["antardasha"]["name"] == "Sankata"
          and early["antardasha"]["graha"] == "Rahu/Ketu",
          str(early["antardasha"]))

    print("\n6. yogini_dasha_reading() — all eight names, no invented extras")
    check("every one of the eight Yogini names has a reading",
          all(d.yogini_dasha_reading(name) for name, _, _ in cs.YOGINI_DASHA))
    check("an unknown name returns None rather than a guess",
          d.yogini_dasha_reading("Rahu") is None)
    check("readings are non-trivial and distinct from each other",
          len({d.yogini_dasha_reading(n) for n, _, _ in cs.YOGINI_DASHA}) == 8)

    print("\n7. Against a chart built by chart_service itself")
    try:
        from app.chart_service import BirthData, build

        real_session = build(BirthData(
            name="Native", date="1986-08-19", time="11:59",
            latitude=26.26, longitude=82.07, timezone="Asia/Kolkata",
            place="Sultanpur, Uttar Pradesh, India", zodiac="sidereal",
            ayanamsa="lahiri", house_system="Whole Sign"))

        live = cs.yogini_dasha(real_session, dt.datetime(2026, 1, 1, tzinfo=ZoneInfo("UTC")))
        check("a real chart produces a complete result", True,
              f"nakshatra {live['nakshatra']}, mahadasha {live['mahadasha']['name']}")
        check("mahadasha and antardasha both name one of the eight Yoginis",
              live["mahadasha"]["name"] in {n for n, _, _ in cs.YOGINI_DASHA}
              and live["antardasha"]["name"] in {n for n, _, _ in cs.YOGINI_DASHA})
        check("the running mahadasha has a reading available",
              d.yogini_dasha_reading(live["mahadasha"]["name"]) is not None)
        import json
        json.dumps(live)
        check("the result is JSON-serialisable", True)
    except Exception as exc:                          # pragma: no cover
        check("a real chart builds and computes a Yogini Dasha", False,
              f"{type(exc).__name__}: {exc}")

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("yogini dasha — alternate 8-fold dasha: all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
