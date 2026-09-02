"""Muhurat (auspicious timing) finder.

No server, no database, no network — pure calculation against real ephemeris
dates via `daily_panchang()`. Verified against a known window (Nov 2026,
Delhi) where a rikta tithi, an Amavasya, and a Tuesday all fall — computed by
hand from the same panchang the module itself calls, not against a second
published source (unlike test_panchang.py — this module's own rule set is
new, not a cross-check of someone else's almanac).

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.test_muhurat
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.astro.muhurat import EVENTS, find_muhurat

failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


DELHI = (28.6139, 77.2090, "Asia/Kolkata")


def main() -> int:
    print("Muhurat finder")

    rows = find_muhurat("marriage", "2026-11-01", "2026-11-14", *DELHI)
    by_date = {r["date"]: r for r in rows}

    check("one entry per day in range", len(rows) == 14, str(len(rows)))
    check("dates are sorted ascending", [r["date"] for r in rows] == sorted(r["date"] for r in rows))

    check("2026-11-08 (Krishna Chaturdashi, a rikta tithi) is avoided",
          by_date["2026-11-08"]["verdict"] == "avoid", str(by_date["2026-11-08"]))
    check("2026-11-09 (Amavasya) is avoided",
          by_date["2026-11-09"]["verdict"] == "avoid", str(by_date["2026-11-09"]))
    check("2026-11-13 (Shukla Chaturthi, a rikta tithi) is avoided",
          by_date["2026-11-13"]["verdict"] == "avoid", str(by_date["2026-11-13"]))
    check("2026-11-06 (an ordinary weekday, no red flags) is good",
          by_date["2026-11-06"]["verdict"] == "good", str(by_date["2026-11-06"]))
    check("every result carries a tithi/nakshatra/vara label",
          all(r["tithi"] and r["nakshatra"] and r["vara"] for r in rows))

    print("\n2. Marriage-specific: Tuesday gets a caution")
    tue = by_date["2026-11-10"]  # Shukla Pratipada, a Tuesday, no other flags
    check("Tuesday is at least a caution for marriage",
          tue["verdict"] in ("avoid", "caution"), str(tue))
    general_tue = find_muhurat("general", "2026-11-10", "2026-11-10", *DELHI)[0]
    check("the same Tuesday is not flagged for a non-marriage event",
          general_tue["verdict"] == "good", str(general_tue))

    print("\n3. Input validation")
    try:
        find_muhurat("not_a_real_event", "2026-11-01", "2026-11-02", *DELHI)
        check("unknown event raises ValueError", False, "did not raise")
    except ValueError:
        check("unknown event raises ValueError", True)

    try:
        find_muhurat("general", "2026-11-10", "2026-11-01", *DELHI)
        check("to_date before from_date raises ValueError", False, "did not raise")
    except ValueError:
        check("to_date before from_date raises ValueError", True)

    try:
        find_muhurat("general", "2026-01-01", "2026-12-31", *DELHI)
        check("a range over 90 days raises ValueError", False, "did not raise")
    except ValueError:
        check("a range over 90 days raises ValueError", True)

    check("every declared event key has a label", all(EVENTS.values()))

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("muhurat finder — all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
