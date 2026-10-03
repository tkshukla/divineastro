"""Date-window parsing (DIVASTRO-119).

QuestionLog #54, "how is my 10th oct to 20th oct", was answered with a
personality description because nothing in the engine looked for a date
window. `app.interpret.periods.parse_period` finds one; this is its table of
phrasings (English, Hindi, Hinglish) against a fixed "today" of Saturday
3 Oct 2026, plus the edge cases its docstring documents.

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.test_periods
"""

from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.interpret.periods import DAILY_CAP_DAYS, MAX_DAYS, parse_period  # noqa: E402

TODAY = dt.date(2026, 10, 3)          # a Saturday
failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


D = dt.date
# (question, expected (start, end) or None)
TABLE: list[tuple[str, tuple[dt.date, dt.date] | None]] = [
    # The four from the bug report, plus the timing one.
    ("how is my 10th oct to 20th oct", (D(2026, 10, 10), D(2026, 10, 20))),
    ("how is october for me", (D(2026, 10, 1), D(2026, 10, 31))),
    ("what about 10 to 20 october", (D(2026, 10, 10), D(2026, 10, 20))),
    ("kaisa rahega 10 se 20 october", (D(2026, 10, 10), D(2026, 10, 20))),
    ("how will be my next week", (D(2026, 10, 5), D(2026, 10, 11))),
    # Explicit single dates.
    ("10th oct", (D(2026, 10, 10), D(2026, 10, 10))),
    ("How will 10 October be?", (D(2026, 10, 10), D(2026, 10, 10))),
    ("oct 10th", (D(2026, 10, 10), D(2026, 10, 10))),
    ("is 10/10 a good day", (D(2026, 10, 10), D(2026, 10, 10))),
    ("10/10/2026", (D(2026, 10, 10), D(2026, 10, 10))),
    ("10.10.2026", (D(2026, 10, 10), D(2026, 10, 10))),
    ("2026-10-10", (D(2026, 10, 10), D(2026, 10, 10))),
    ("1st nov", (D(2026, 11, 1), D(2026, 11, 1))),
    ("nov 1st 2026", (D(2026, 11, 1), D(2026, 11, 1))),
    # Ranges.
    ("10-20 Oct", (D(2026, 10, 10), D(2026, 10, 20))),
    ("between 10 oct and 20 oct", (D(2026, 10, 10), D(2026, 10, 20))),
    ("between 10 and 20 october", (D(2026, 10, 10), D(2026, 10, 20))),
    ("oct 10 to oct 20", (D(2026, 10, 10), D(2026, 10, 20))),
    ("october 10-20", (D(2026, 10, 10), D(2026, 10, 20))),
    ("from oct 10 to 20, 2026", (D(2026, 10, 10), D(2026, 10, 20))),
    ("25 dec to 5 jan", (D(2026, 12, 25), D(2027, 1, 5))),
    ("october to december", (D(2026, 10, 1), D(2026, 12, 31))),
    ("10/10 to 20/10", (D(2026, 10, 10), D(2026, 10, 20))),
    # Hindi / Hinglish.
    ("10 अक्टूबर से 20 अक्टूबर तक कैसा रहेगा", (D(2026, 10, 10), D(2026, 10, 20))),
    ("अक्टूबर कैसा रहेगा", (D(2026, 10, 1), D(2026, 10, 31))),
    ("शादी के लिए अगले महीने", (D(2026, 11, 1), D(2026, 11, 30))),
    ("is mahine kaisa rahega", (D(2026, 10, 1), D(2026, 10, 31))),
    ("agle mahine naukri milegi?", (D(2026, 11, 1), D(2026, 11, 30))),
    ("agle hafte kaisa rahega", (D(2026, 10, 5), D(2026, 10, 11))),
    ("is hafte", (D(2026, 10, 3), D(2026, 10, 4))),
    ("अगले हफ्ते", (D(2026, 10, 5), D(2026, 10, 11))),
    ("इस महीने", (D(2026, 10, 1), D(2026, 10, 31))),
    ("aaj ka din kaisa hai", (D(2026, 10, 3), D(2026, 10, 3))),
    ("kal kaisa rahega", (D(2026, 10, 4), D(2026, 10, 4))),        # kal, future -> tomorrow
    ("kal kaisa tha", (D(2026, 10, 2), D(2026, 10, 2))),           # kal, past -> yesterday
    ("कल", (D(2026, 10, 4), D(2026, 10, 4))),
    ("parso", (D(2026, 10, 5), D(2026, 10, 5))),
    ("agle 10 din", (D(2026, 10, 3), D(2026, 10, 12))),
    ("next 10 days", (D(2026, 10, 3), D(2026, 10, 12))),
    # Relative English.
    ("today", (D(2026, 10, 3), D(2026, 10, 3))),
    ("tomorrow", (D(2026, 10, 4), D(2026, 10, 4))),
    ("this week", (D(2026, 10, 3), D(2026, 10, 4))),
    ("this month", (D(2026, 10, 1), D(2026, 10, 31))),
    ("next month", (D(2026, 11, 1), D(2026, 11, 30))),
    ("last week", (D(2026, 9, 21), D(2026, 9, 27))),
    # Year handling.
    ("may 2027", (D(2027, 5, 1), D(2027, 5, 31))),
    ("how is march for me", (D(2027, 3, 1), D(2027, 3, 31))),      # passed -> next year
    ("how is september", (D(2027, 9, 1), D(2027, 9, 30))),         # passed -> next year
    ("how was september", (D(2026, 9, 1), D(2026, 9, 30))),        # past tense -> this year
    # No period at all.
    ("how is my career", None),
    ("Will I get married?", None),
    ("aaj kal kaisa chal raha hai", None),          # "these days", not a date
    ("may I know my future", None),                 # "may" the verb
    ("10 to 20", None),                             # no month: ambiguous
    ("salary 10.5 lakh in", None),
    ("निकलेगा क्या", None),                          # "कल" inside a word
    # Invalid or explicit look-backs.
    ("31 feb", None),
    ("45/13", None),
    ("march 2015", None),                           # explicit past year -> review path
    ("10 oct 2025", None),
    ("I got married on 10 oct", None),              # past tense, date still ahead -> last year's
]


def main() -> int:
    print(f"parse_period table ({len(TABLE)} phrasings, today = {TODAY})\n")
    for q, want in TABLE:
        p = parse_period(q, TODAY)
        got = (p.start, p.end) if p else None
        check(f"{q!r}", got == want, f"got {got}, want {want}")

    print("\nFlags")
    p = parse_period("how is september", TODAY)
    check("a passed yearless month is rolled to next year and flagged",
          p.rolled_year and p.assumed_year and not p.past, str(p))
    p = parse_period("how was september", TODAY)
    check("a past-tense question keeps it and flags it past", p.past and not p.rolled_year, str(p))
    p = parse_period("how is october for me", TODAY)
    check("the running month is flagged partly past", p.partly_past and not p.past, str(p))
    p = parse_period("10th oct to 20th oct", TODAY)
    check("label prints both ends with 'Mon YYYY' for the date auditor",
          p.label == "10 Oct 2026 – 20 Oct 2026", p.label)
    check("an 11-day window gets daily detail", p.detail == "daily" and p.days == 11)
    p = parse_period("october to march", TODAY)
    check(f"a window over {DAILY_CAP_DAYS} days gets the monthly summary",
          p.detail == "monthly" and p.end == D(2027, 3, 31), str(p))
    p = parse_period("2026-10-01 to 2028-10-01", TODAY)
    check(f"a window over {MAX_DAYS} days is cut and flagged",
          p.truncated and p.days == MAX_DAYS, str(p))
    check("an empty question is None", parse_period("", TODAY) is None)
    p = parse_period("how is my day today", dt.datetime(2026, 10, 3, 20, 0, tzinfo=dt.timezone.utc))
    check("an aware 'now' is read in IST (20:00 UTC is already 4 Oct in India)",
          p is not None and p.start == D(2026, 10, 4), str(p))

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("periods: all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
