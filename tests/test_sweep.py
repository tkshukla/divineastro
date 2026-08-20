"""Robustness sweep.

Runs the whole pipeline — chart build, every topic, every intent — across a
spread of dates, latitudes, timezone regimes and settings. This is a crash and
sanity sweep rather than an astrological correctness test: it asserts that no
input in the covered space raises, and that answers stay substantive.

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.test_sweep
"""

from __future__ import annotations

import datetime as dt
import re
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.chart_service import BirthData, build, solar_return, timing_snapshot, transits, wheel_svg
from app.interpret import analyse
from app.interpret.topics import TOPICS

CHARTS = [
    # label, date, time, lat, lon, tz  — chosen for timezone and latitude spread
    ("Delhi 1990",        "1990-05-15", "14:30",  28.6139,  77.2090, "Asia/Kolkata"),
    ("London BST 1955",   "1955-07-04", "03:15",  51.5074,  -0.1278, "Europe/London"),
    ("New York 1975",     "1975-11-22", "23:58",  40.7143, -74.0060, "America/New_York"),
    ("Sydney 2005",       "2005-01-09", "06:05", -33.8679, 151.2073, "Australia/Sydney"),
    ("Berlin 1930",       "1930-02-28", "12:00",  52.5244,  13.4105, "Europe/Berlin"),
    ("Sao Paulo 1988",    "1988-10-31", "19:45", -23.5475, -46.6361, "America/Sao_Paulo"),
    ("Tromso (polar)",    "1994-12-21", "11:11",  69.6496,  18.9560, "Europe/Oslo"),
    ("Leap day 2000",     "2000-02-29", "00:00",   1.2897, 103.8501, "Asia/Singapore"),
    ("Kathmandu +5:45",   "1982-08-17", "05:45",  27.7172,  85.3240, "Asia/Kathmandu"),
    ("Reykjavik 2018",    "2018-06-21", "23:59",  64.1355, -21.8954, "Atlantic/Reykjavik"),
]

SETTINGS = [
    ("tropical", "Placidus"),
    ("tropical", "Whole Sign"),
    ("sidereal", "Whole Sign"),
    ("sidereal", "Placidus"),
]

QUESTIONS = [
    "Tell me about my personality",
    "What are my strengths and blind spots?",
    "How is my career looking?",
    "When will I get a promotion?",
    "Will I ever be rich?",
    "Should I start a business?",
    "When will I get married?",
    "Is my marriage going to last?",
    "Will I have children?",
    "Where are my health vulnerabilities?",
    "Should I move abroad?",
    "Will I clear my exams next year?",
    "Why do I keep facing obstacles?",
    "What is happening in my life right now?",
    "Tell me about my friends and network",
    "Am I spiritually inclined?",
    "When will I buy a house?",
    "How is my relationship with my mother?",
    "I got married in 2012 — what was my chart doing?",
    "I got married a few years ago, what was that year?",
    "Which year did I change jobs?",
    "When did I have my biggest money trouble?",
    "What was happening in March 2015?",
    "What was going on when I was 25?",
    "I lost my job three years ago, why?",
    "How was last year for money?",
    "",                                   # empty-ish input
    "asdfghjkl qwerty zzz",               # nonsense
    "What is the meaning of the number 7?",  # off-topic
]

NOW = dt.datetime(2026, 8, 15, 12, 0)


def main() -> int:
    failures: list[str] = []
    checks = 0

    for label, date, time, lat, lon, tz in CHARTS:
        for zodiac, houses in SETTINGS:
            tag = f"{label} [{zodiac}/{houses}]"
            try:
                birth = BirthData(
                    name=label, date=date, time=time, latitude=lat, longitude=lon,
                    timezone=tz, place=label, zodiac=zodiac, house_system=houses,
                )
                session = build(birth)
            except Exception:
                failures.append(f"BUILD {tag}\n{traceback.format_exc()}")
                continue

            # Structural sanity on the chart itself.
            try:
                b = session.bundle
                assert b["objects"]["ASC"]["sign"], "no ascendant"
                assert len(b["houses"]["cusps"]) == 12, "house cusps missing"
                assert len({o["name"] for o in b["objects"].values()
                            if o["kind"] == "planet"}) >= 10, "planets missing"
                assert b["meta"]["sect"] in ("day", "night")
                for name in ("Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"):
                    assert 1 <= b["objects"][name]["house"] <= 12, f"{name} house out of range"
                assert wheel_svg(session).startswith("<?xml") or "<svg" in wheel_svg(session)
                timing_snapshot(session, NOW)
                transits(session, NOW)
                solar_return(session, 2026)
                checks += 1
            except Exception:
                failures.append(f"CHART {tag}\n{traceback.format_exc()}")

            for q in QUESTIONS:
                try:
                    result = analyse(session, q, NOW)
                    assert result.answer and len(result.answer) > 200, \
                        f"answer too thin ({len(result.answer)} chars)"
                    assert -1.0 <= result.score <= 1.0, "score out of range"
                    assert result.evidence or result.topic == "self", "no evidence gathered"
                    # No unresolved template holes or Python repr should reach
                    # the user. Word-bounded so "maintenance" is not a "nan".
                    leak = re.search(r"\{\w+\}|\bNone\b|\bnan\b|\bNaN\b|CelestialPosition",
                                     result.answer)
                    assert not leak, f"leaked {leak.group(0)!r} into answer"
                    checks += 1
                except Exception:
                    failures.append(f"ASK {tag} :: {q!r}\n{traceback.format_exc()}")

    # Every topic must be reachable from at least one natural question.
    reached = set()
    birth = BirthData(name="R", date="1990-05-15", time="14:30", latitude=28.6139,
                      longitude=77.209, timezone="Asia/Kolkata", place="Delhi")
    session = build(birth)
    for q in QUESTIONS:
        if q.strip():
            reached.add(analyse(session, q, NOW).topic)
    missing = {t.key for t in TOPICS} - reached
    if missing:
        failures.append(f"UNREACHABLE TOPICS: {sorted(missing)}")

    print(f"\n{checks} checks run across {len(CHARTS)} charts x {len(SETTINGS)} settings")
    if failures:
        print(f"\n{len(failures)} FAILURES\n" + "=" * 70)
        for f in failures[:12]:
            print(f + "\n" + "-" * 70)
        return 1
    print("all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
