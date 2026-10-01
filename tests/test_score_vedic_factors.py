"""Yogas, dasha-lord dignity and Sade Sati folded into the numeric verdict
score, not just the prose (DIVASTRO-92).

Before this, `score_of()` in app/interpret/engine.py was Western-dignity-only
— a chart could score "Strongly supported" while carrying a Raja Yoga or a
badly afflicted dasha lord that would classically shift the reading, and the
number and the prose could tell different stories. `vedic_factor_evidence()`
closes that gap, but only for a factor that touches a planet `gather()`
already treats as relevant to the topic being asked about (a house ruler or
significator) — a generic yoga elsewhere in the chart must not move an
unrelated question's score.

The chart below (1990-03-12 09:30, Delhi, sidereal/Lahiri/Whole Sign) is a
fixed, real chart, not a synthetic fixture — its career-topic evidence is
captured verbatim here. `AS_OF` is pinned explicitly (not "now") so the
dasha-lord assertions stay true regardless of when this test is run; without
that pin, the real antardasha lord changes as years pass and this file would
silently go stale.

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.test_score_vedic_factors
"""

from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.astro import panchang  # noqa: E402
from app.chart_service import BirthData, build  # noqa: E402
from app.interpret.engine import (  # noqa: E402
    Evidence, gather, score_of, vedic_factor_evidence, verdict_of,
)
from app.interpret.topics import TOPICS  # noqa: E402

failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


AS_OF = dt.datetime(2026, 9, 30, 12, 0, tzinfo=dt.timezone.utc)

BIRTH = BirthData(
    name="Fixture", date="1990-03-12", time="09:30",
    latitude=28.6139, longitude=77.2090, timezone="Asia/Kolkata",
    place="Delhi, India", zodiac="sidereal", ayanamsa="lahiri",
    house_system="Whole Sign", time_known=True,
)


def topic(key: str):
    return next(t for t in TOPICS if t.key == key)


def key_planets_for(session, t) -> list[str]:
    planets = [session.house_ruler(h) for h in t.primary_houses]
    planets += list(t.significators[:5])
    return planets


def main() -> int:
    session = build(BIRTH)
    career = topic("career")
    love = topic("love")
    key_planets = key_planets_for(session, career)

    print("1. Real chart: known yogas and the antardasha lord are folded in, "
          "with the right score/weight")
    ev = vedic_factor_evidence(session, career, key_planets, as_of=AS_OF)
    by_factor = {e.factor: e for e in ev}
    check("Gaja Kesari Yoga present at full strength (no strength field -> 1.0x)",
          "Gaja Kesari Yoga" in by_factor
          and by_factor["Gaja Kesari Yoga"].score == 1.0
          and by_factor["Gaja Kesari Yoga"].weight == 0.5)
    check("Antardasha lord dignity present for Mars, exalted in Capricorn",
          "Antardasha lord dignity" in by_factor
          and by_factor["Antardasha lord dignity"].score == 1.5
          and by_factor["Antardasha lord dignity"].weight == 0.7,
          str(by_factor.get("Antardasha lord dignity")))
    raja = [e for e in ev if e.factor == "Raja Yoga"]
    check("at least one Raja Yoga present, each at the 'moderate' strength tier "
          "(2.0 * 0.75 = 1.5 score, 1.0 * 0.75 = 0.75 weight)",
          len(raja) >= 1 and all(e.score == 1.5 and e.weight == 0.75 for e in raja),
          str(raja))
    check("none of these new evidence scores exceed the documented -3..+3 range",
          all(-3.0 <= e.score <= 3.0 for e in ev))

    print("\n2. Relevance scoping: the SAME chart's SAME yogas are silently "
          "dropped when none of their planets are relevant to the topic")
    irrelevant = vedic_factor_evidence(session, career, ["Ketu"], as_of=AS_OF)
    check("zero evidence when key_planets shares nothing with any formed yoga/dasha lord",
          irrelevant == [], str(irrelevant))

    print("\n3. gather() actually wires this in (not just the standalone function)")
    full = gather(session, career, as_of=AS_OF)
    vedic_in_gather = [e for e in full if e.factor in by_factor]
    check("the same vedic-factor evidence appears via the real gather() path",
          len(vedic_in_gather) == len(ev))

    print("\n4. Sade Sati: topic-scoped (career is in scope, love is not), "
          "and phase-scaled — tested with a controlled fake, not real transit "
          "state, so this can't silently rot as Saturn moves")
    real_sade_sati = panchang.sade_sati

    def fake_peak(session, as_of=None, **kw):
        return {"running": True, "phase": {"name": "Peak"}}

    def fake_rising(session, as_of=None, **kw):
        return {"running": True, "phase": {"name": "Rising"}}

    def fake_none(session, as_of=None, **kw):
        return {"running": False, "phase": None}

    try:
        panchang.sade_sati = fake_peak
        in_scope = vedic_factor_evidence(session, career, key_planets, as_of=AS_OF)
        out_of_scope = vedic_factor_evidence(
            session, love, key_planets_for(session, love), as_of=AS_OF)
        check("peak-phase Sade Sati counted for career (in scope)",
              any(e.factor == "Sade Sati (peak)" and e.score == -1.0 and e.weight == 0.5
                  for e in in_scope))
        check("peak-phase Sade Sati NOT counted for love (out of scope)",
              not any("Sade Sati" in e.factor for e in out_of_scope))

        panchang.sade_sati = fake_rising
        rising = vedic_factor_evidence(session, career, key_planets, as_of=AS_OF)
        check("rising-phase Sade Sati is softer than peak (-0.5/0.3, not -1.0/0.5)",
              any(e.factor == "Sade Sati (rising)" and e.score == -0.5 and e.weight == 0.3
                  for e in rising))

        panchang.sade_sati = fake_none
        not_running = vedic_factor_evidence(session, career, key_planets, as_of=AS_OF)
        check("no Sade Sati evidence when not currently running",
              not any("Sade Sati" in e.factor for e in not_running))
    finally:
        panchang.sade_sati = real_sade_sati

    print("\n5. score_of()/verdict_of(): a strong Raja Yoga moves the verdict "
          "band, all else equal (the proposal's own acceptance criterion)")
    base = [Evidence(text="x", score=0.3, weight=1.0, factor="base")]
    with_raja = base + [Evidence(text="y", score=2.0, weight=1.0, factor="Raja Yoga")]
    s_base, s_raja = score_of(base), score_of(with_raja)
    check("adding a strong Raja Yoga raises the score", s_raja > s_base,
          f"{s_base:.3f} -> {s_raja:.3f}")
    check("...enough to flip the verdict band on this constructed case",
          verdict_of(s_base)[0] != verdict_of(s_raja)[0],
          f"{verdict_of(s_base)[0]!r} -> {verdict_of(s_raja)[0]!r}")

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("vedic-factor scoring: all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
