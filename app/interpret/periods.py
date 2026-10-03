"""Date windows named in a question (DIVASTRO-119).

"how is my 10th oct to 20th oct", "kaisa rahega 10 se 20 october", "how will
be my next week", "शादी के लिए अगले महीने" — each names a stretch of the
calendar. Before this module nothing looked for one, so a question with no
subject word fell through to the personality topic and was answered with a
character description (QuestionLog #54).

`parse_period(question, now)` returns a `Period` (a start and end date, both
inclusive, in the asker's civil calendar — IST unless told otherwise) or None.

What is understood
------------------
* explicit dates: "10th oct", "10 October", "oct 10", "10 अक्टूबर",
  "10/10" (day/month, the Indian order), "10/10/2026", "10.10.2026",
  "2026-10-10";
* ranges of those: "10th oct to 20th oct", "10 to 20 october", "10-20 Oct",
  "10 se 20 october (tak)", "between 10 oct and 20 oct", "oct 10 - oct 20",
  "october to december";
* a month on its own, with or without a year: "october", "oct 2026",
  "अक्टूबर"; relative months: "this month" / "is mahine" / "इस महीने",
  "next month" / "agle mahine" / "अगले महीने", "last month" / "pichle mahine";
* weeks: "this week" / "is hafte" (today to Sunday), "next week" /
  "agle hafte" / "coming week" (next Monday to Sunday), "last week",
  "this weekend";
* days: "today" / "aaj", "tomorrow", "day after tomorrow" / "parso",
  "yesterday", "next 10 days" / "agle 10 din".

Decisions (documented because they are judgement calls)
-------------------------------------------------------
* **"kal"** means both yesterday and tomorrow. It is read as *tomorrow*
  unless the question is in the past tense ("kal kaisa tha", "कल कैसा गया"),
  in which case it is yesterday. "aaj kal" / "आजकल" means "these days" and is
  not a date at all.
* **A date or month without a year** is taken in the current year if it has
  not yet passed (or is running now). If it has already passed: a past-tense
  question keeps it in this year (and the window is flagged `past`); any
  other question is moved to the *next* year and flagged `rolled_year`, so
  the answer can say "I have read this as October 2027". A past-tense
  question naming a yearless date still *ahead* this year ("I got married on
  10 oct", asked on 3 Oct) means last year's, which is a look-back: None.
* **An explicit year earlier than the current one** ("March 2015", "10 oct
  2024") returns None: that is a look-back, which the engine's existing review
  path (`engine.extract_when`) already answers, and day-by-day Moon transits
  of a date years ago are not what anyone is asking for.
* **Invalid dates** ("31 feb", "45/13") return None rather than guessing.
* **"may" and "march"** are also ordinary English words, so they count as a
  month only next to a day number or a year, or after a word like
  in/for/during/this/next/of/till/se/tak.
* **Length**: windows up to `DAILY_CAP_DAYS` (92) get day-by-day detail;
  longer ones a month-by-month summary; anything beyond `MAX_DAYS` (366) is
  cut to that length (flagged `truncated`).
"""

from __future__ import annotations

import calendar
import datetime as dt
import re
from dataclasses import dataclass
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
DAILY_CAP_DAYS = 92
MAX_DAYS = 366


@dataclass(frozen=True)
class Period:
    start: dt.date
    end: dt.date                 # inclusive
    kind: str                    # day | range | week | month | days
    matched: str = ""            # the words the window was read from
    assumed_year: bool = False   # no year was given
    rolled_year: bool = False    # moved to next year because it had passed
    past: bool = False           # the whole window is before today
    partly_past: bool = False    # the window started before today
    truncated: bool = False      # cut to MAX_DAYS

    @property
    def days(self) -> int:
        return (self.end - self.start).days + 1

    @property
    def detail(self) -> str:
        """'daily' for a window short enough to read day by day, else 'monthly'."""
        return "daily" if self.days <= DAILY_CAP_DAYS else "monthly"

    @property
    def label(self) -> str:
        if self.start == self.end:
            return fmt_date(self.start)
        return f"{fmt_date(self.start)} – {fmt_date(self.end)}"

    def to_dict(self) -> dict:
        return {
            "start": self.start.isoformat(), "end": self.end.isoformat(),
            "kind": self.kind, "label": self.label, "days": self.days,
            "detail": self.detail, "matched": self.matched,
            "assumed_year": self.assumed_year, "rolled_year": self.rolled_year,
            "past": self.past, "partly_past": self.partly_past,
            "truncated": self.truncated,
        }


def fmt_date(d: dt.date) -> str:
    """'10 Oct 2026' — the 'Mon YYYY' tail is what llm._DATE_RE recognises, so
    every window date reaching the polish prompt is on the auditor's allow-list."""
    return f"{d.day} {d:%b %Y}"


# --------------------------------------------------------------------------
# Normalisation: Devanagari -> the Latin/Hinglish vocabulary below
# --------------------------------------------------------------------------

_DEV = "ऀ-ॿ"
_DEV_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")

# Order matters only where one key is a prefix of another; the lookarounds
# stop a key matching inside a longer word ("कल" inside "निकलेगा").
_HI_WORDS = (
    ("आजकल", " aajkal "), ("आज कल", " aajkal "),
    ("जनवरी", " january "), ("फ़रवरी", " february "), ("फरवरी", " february "),
    ("मार्च", " march "), ("अप्रैल", " april "), ("अप्रेल", " april "),
    ("मई", " may "), ("जून", " june "), ("जुलाई", " july "), ("अगस्त", " august "),
    ("सितंबर", " september "), ("सितम्बर", " september "),
    ("अक्टूबर", " october "), ("अक्तूबर", " october "),
    ("नवंबर", " november "), ("नवम्बर", " november "),
    ("दिसंबर", " december "), ("दिसम्बर", " december "),
    ("परसों", " parso "), ("आज", " aaj "), ("कल", " kal "),
    ("अगले", " agle "), ("अगला", " agle "), ("अगली", " agle "), ("आने वाले", " agle "),
    ("पिछले", " pichle "), ("पिछला", " pichle "), ("इस", " is "),
    ("हफ़्ते", " hafte "), ("हफ्ते", " hafte "), ("हफ़्ता", " hafte "), ("हफ्ता", " hafte "),
    ("सप्ताह", " hafte "), ("महीने", " mahine "), ("महीना", " mahine "), ("माह", " mahine "),
    ("दिनों", " din "), ("दिन", " din "), ("से", " se "), ("तक", " tak "),
    ("और", " and "), ("के बीच", " between "),
    ("था", " tha "), ("थी", " tha "), ("थे", " tha "), ("गया", " tha "), ("गई", " tha "),
    ("गयी", " tha "), ("बीता", " tha "),
)
_HI_RES = [(re.compile(rf"(?<![{_DEV}]){re.escape(k)}(?![{_DEV}])"), v) for k, v in _HI_WORDS]


def _normalise(question: str) -> str:
    t = question.translate(_DEV_DIGITS)
    for rx, repl in _HI_RES:
        t = rx.sub(repl, t)
    t = t.lower().replace("’", "'")
    t = re.sub(r"\baaj\s*kal\b", " aajkal ", t)
    return re.sub(r"[ \t]+", " ", t)


# --------------------------------------------------------------------------
# Vocabulary
# --------------------------------------------------------------------------

MONTHS = {
    "january": 1, "jan": 1, "february": 2, "feb": 2, "march": 3, "mar": 3,
    "april": 4, "apr": 4, "may": 5, "june": 6, "jun": 6, "july": 7, "jul": 7,
    "august": 8, "aug": 8, "september": 9, "sept": 9, "sep": 9, "october": 10,
    "oct": 10, "november": 11, "nov": 11, "december": 12, "dec": 12,
}
_AMBIGUOUS = {"may", "march", "mar"}
_MON = r"(" + "|".join(sorted(MONTHS, key=len, reverse=True)) + r")\.?"
_DAY = r"(\d{1,2})(?:st|nd|rd|th)?"
_YEAR = r"(?:,?\s*(\d{4}))?"
_SEP = r"\s*(?:-|–|—|to|till|until|upto|up to|through|thru|se|and)\s*"
_PREFIX = r"(?:(?:between|from|bich|beech)\s+)?"
_CONTEXT_BEFORE = re.compile(
    r"\b(in|for|during|this|next|coming|of|from|till|until|to|se|tak|mein|me|by|"
    r"agle|is|month|mahine)\s*$")

_PAST = re.compile(
    r"\b(was|were|went|did|had|got|happened|has been|have been|gone|yesterday|last|tha|thi|"
    r"gaya|gayi|gaye|beeta|bita|guzra|pichle|pichla|rahi thi|raha tha)\b")


def _is_past_question(t: str) -> bool:
    return bool(_PAST.search(t))


def _month_ok(t: str, m: re.Match, word: str, has_day_or_year: bool) -> bool:
    if word not in _AMBIGUOUS or has_day_or_year:
        return True
    return bool(_CONTEXT_BEFORE.search(t[:m.start()]))


def _mk(y: int, mo: int, d: int) -> dt.date | None:
    try:
        return dt.date(y, mo, d)
    except ValueError:
        return None


class _Invalid(Exception):
    """An explicit date that does not exist ("31 feb")."""


# --------------------------------------------------------------------------
# Window construction
# --------------------------------------------------------------------------

def _finish(start: dt.date, end: dt.date, kind: str, matched: str, today: dt.date,
            *, assumed_year: bool = False, rolled: bool = False) -> Period:
    truncated = False
    if (end - start).days + 1 > MAX_DAYS:
        end = start + dt.timedelta(days=MAX_DAYS - 1)
        truncated = True
    return Period(
        start=start, end=end, kind=kind, matched=matched.strip(),
        assumed_year=assumed_year, rolled_year=rolled,
        past=end < today, partly_past=start < today <= end,
        truncated=truncated,
    )


def _resolve_year(make, today: dt.date, past_q: bool, year_given: int | None):
    """`make(year) -> (start, end)`. Picks the year per the module rules."""
    if year_given is not None:
        if year_given < today.year:
            return None                       # explicit look-back: not ours
        s, e = make(year_given)
        return s, e, False, False
    s, e = make(today.year)
    if past_q and s > today:
        return None                           # "I got married on 10 oct": last year's — a look-back
    if e < today and not past_q:
        s, e = make(today.year + 1)
        return s, e, True, True
    return s, e, True, False


def _year_of(s: str | None) -> int | None:
    return int(s) if s else None


def _explicit(t: str, today: dt.date, past_q: bool) -> Period | None:
    # 1. ISO dates, single or a range.
    iso = r"(\d{4})-(\d{1,2})-(\d{1,2})"
    m = re.search(rf"\b{iso}(?:{_SEP}{iso})?\b", t)
    if m:
        a = _mk(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        if a is None:
            raise _Invalid
        b = a
        if m.group(4):
            b = _mk(int(m.group(4)), int(m.group(5)), int(m.group(6)))
            if b is None:
                raise _Invalid
        if max(a, b) < dt.date(today.year, 1, 1):
            return None
        a, b = min(a, b), max(a, b)
        return _finish(a, b, "range" if a != b else "day", m.group(0), today)

    # 2. Numeric day/month(/year), Indian order. A dash only counts with a
    # year, so "10-20 oct" stays a day range rather than "10th of month 20".
    # "/" may omit the year ("10/10"); "." and "-" need one, so "10.5 lakh"
    # and "10-20 oct" are not misread as dates.
    num = r"(\d{1,2})(?:/(\d{1,2})(?:/(\d{4}|\d{2}))?|\.(\d{1,2})\.(\d{4})|-(\d{1,2})-(\d{4}))"
    nums = list(re.finditer(rf"(?<![\d/.-]){num}(?![\d/.-])", t))
    if nums:
        def one(mm: re.Match) -> tuple[int, int, int | None]:
            d = int(mm.group(1))
            mo = mm.group(2) or mm.group(4) or mm.group(6)
            y = mm.group(3) or mm.group(5) or mm.group(7)
            yi = int(y) if y else None
            if yi is not None and yi < 100:
                yi += 2000
            return d, int(mo), yi
        d1, mo1, y1 = one(nums[0])
        if not (1 <= mo1 <= 12) or _mk(y1 or today.year, mo1, d1) is None:
            raise _Invalid
        second = None
        if len(nums) > 1:
            between = t[nums[0].end():nums[1].start()]
            if re.fullmatch(_SEP, between):
                second = one(nums[1])
                if not (1 <= second[1] <= 12) or _mk(second[2] or today.year,
                                                    second[1], second[0]) is None:
                    raise _Invalid
        matched = t[nums[0].start():(nums[1].end() if second else nums[0].end())]
        year_given = y1 if y1 is not None else (second[2] if second else None)

        def make(y: int):
            a = dt.date(y if y1 is None else y1, mo1, d1)
            if not second:
                return a, a
            d2, mo2, y2 = second
            b = dt.date(y2 if y2 is not None else a.year, mo2, d2)
            if b < a and y2 is None:
                b = dt.date(a.year + 1, mo2, d2)
            return a, b
        r = _resolve_year(make, today, past_q, year_given)
        if r is None:
            return None
        a, b, assumed, rolled = r
        return _finish(a, b, "range" if second else "day", matched, today,
                       assumed_year=assumed, rolled=rolled)

    # 3. Day ranges with month names.
    patterns = (
        # 10th oct 2026 to 20th oct 2026 / 10 to 20 october / 10-20 oct / 10 se 20 october
        rf"{_PREFIX}\b{_DAY}(?:\s*(?:of\s+)?{_MON}{_YEAR})?{_SEP}{_DAY}\s*(?:of\s+)?{_MON}{_YEAR}\b",
        # oct 10 to oct 20 / october 10-20 / oct 10 to 20, 2026
        rf"{_PREFIX}\b{_MON}\s*{_DAY}{_SEP}(?:{_MON}\s*)?{_DAY}{_YEAR}\b",
    )
    m = re.search(patterns[0], t)
    if m:
        d1, mon1, y1, d2, mon2, y2 = (m.group(1), m.group(2), m.group(3), m.group(4),
                                      m.group(5), m.group(6))
        return _day_range(int(d1), MONTHS[mon1] if mon1 else MONTHS[mon2], _year_of(y1),
                          int(d2), MONTHS[mon2], _year_of(y2), m.group(0), today, past_q)
    m = re.search(patterns[1], t)
    if m:
        mon1, d1, mon2, d2, y = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)
        return _day_range(int(d1), MONTHS[mon1], None, int(d2),
                          MONTHS[mon2] if mon2 else MONTHS[mon1], _year_of(y),
                          m.group(0), today, past_q)

    # 4. Month ranges: october to december (2026).
    m = re.search(rf"{_PREFIX}\b{_MON}{_YEAR}{_SEP}{_MON}{_YEAR}\b", t)
    if m and _month_ok(t, m, m.group(1), bool(m.group(2))):
        mo1, y1, mo2, y2 = MONTHS[m.group(1)], _year_of(m.group(2)), MONTHS[m.group(3)], \
            _year_of(m.group(4))
        year_given = y1 if y1 is not None else y2

        def make(y: int):
            if y1 is not None:
                ya = y1
            elif y2 is not None:
                ya = y2 if mo1 <= mo2 else y2 - 1
            else:
                ya = y
            yb = y2 if y2 is not None else (ya if mo2 >= mo1 else ya + 1)
            return (dt.date(ya, mo1, 1),
                    dt.date(yb, mo2, calendar.monthrange(yb, mo2)[1]))
        r = _resolve_year(make, today, past_q, year_given)
        if r is None:
            return None
        a, b, assumed, rolled = r
        return _finish(a, b, "range", m.group(0), today, assumed_year=assumed, rolled=rolled)

    # 5. A single date with a month name.
    for rx, order in ((rf"\b{_DAY}\s*(?:of\s+)?{_MON}{_YEAR}\b", "dm"),
                      (rf"\b{_MON}\s*{_DAY}(?!\d){_YEAR}\b", "md")):
        m = re.search(rx, t)
        if not m:
            continue
        if order == "dm":
            d, mon, y = int(m.group(1)), m.group(2), _year_of(m.group(3))
        else:
            mon, d, y = m.group(1), int(m.group(2)), _year_of(m.group(3))
        if not 1 <= d <= 31:
            continue        # "oct 2026" read as day 20 — leave it to the month rule
        mo = MONTHS[mon]
        if _mk(y or 2024, mo, d) is None:           # 2024: leap, so 29 feb is valid
            raise _Invalid
        r = _resolve_year(lambda yy: (dt.date(yy, mo, d),) * 2, today, past_q, y)
        if r is None:
            return None
        a, b, assumed, rolled = r
        return _finish(a, b, "day", m.group(0), today, assumed_year=assumed, rolled=rolled)

    # 6. A month on its own.
    for m in re.finditer(rf"\b{_MON}{_YEAR}\b", t):
        word, y = m.group(1), _year_of(m.group(2))
        if not _month_ok(t, m, word, y is not None):
            continue
        mo = MONTHS[word]
        r = _resolve_year(
            lambda yy: (dt.date(yy, mo, 1), dt.date(yy, mo, calendar.monthrange(yy, mo)[1])),
            today, past_q, y)
        if r is None:
            return None
        a, b, assumed, rolled = r
        return _finish(a, b, "month", m.group(0), today, assumed_year=assumed, rolled=rolled)
    return None


def _day_range(d1: int, mo1: int, y1: int | None, d2: int, mo2: int, y2: int | None,
               matched: str, today: dt.date, past_q: bool) -> Period | None:
    if _mk(y1 or 2024, mo1, d1) is None or _mk(y2 or 2024, mo2, d2) is None:
        raise _Invalid
    year_given = y1 if y1 is not None else y2

    def make(y: int):
        ya = y1 if y1 is not None else y
        a = dt.date(ya, mo1, d1)
        yb = y2 if y2 is not None else ya
        b = _mk(yb, mo2, d2) or dt.date(yb, mo2, 28)
        if b < a and y2 is None:
            b = dt.date(yb + 1, mo2, d2)
        return a, b
    r = _resolve_year(make, today, past_q, year_given)
    if r is None:
        return None
    a, b, assumed, rolled = r
    if b < a:
        a, b = b, a
    return _finish(a, b, "range" if a != b else "day", matched, today,
                   assumed_year=assumed, rolled=rolled)


_NUM_WORDS = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "ten": 10,
              "fifteen": 15, "few": 3, "do": 2, "teen": 3, "char": 4, "paanch": 5, "das": 10}


def _relative(t: str, today: dt.date, past_q: bool) -> Period | None:
    def day(n: int, words: str) -> Period:
        d = today + dt.timedelta(days=n)
        return _finish(d, d, "day", words, today)

    m = re.search(r"\b(?:next|coming|agle|aane wale|aanewale)\s+(\d{1,3}|"
                  + "|".join(_NUM_WORDS) + r")\s+(days|day|din)\b", t)
    if m:
        n = int(m.group(1)) if m.group(1).isdigit() else _NUM_WORDS[m.group(1)]
        if n <= 0:
            return None
        return _finish(today, today + dt.timedelta(days=n - 1), "days", m.group(0), today)

    m = re.search(r"\b(?:next|coming|agle|aane wale)\s+(\d{1,2}|"
                  + "|".join(_NUM_WORDS) + r")\s+(weeks|hafte|hafton)\b", t)
    if m:
        n = int(m.group(1)) if m.group(1).isdigit() else _NUM_WORDS[m.group(1)]
        return _finish(today, today + dt.timedelta(days=7 * n - 1), "days", m.group(0), today)

    if re.search(r"\bday after tomorrow\b", t):
        return day(2, "day after tomorrow")
    if re.search(r"\bparso\b|\bparson\b", t):
        return day(-2 if past_q else 2, "parso")
    if re.search(r"\btomorrow\b", t):
        return day(1, "tomorrow")
    if re.search(r"\bkal\b", t):
        return day(-1 if past_q else 1, "kal")
    if re.search(r"\byesterday\b", t):
        return day(-1, "yesterday")
    if re.search(r"\b(?:today|aaj|tonight)\b", t):
        return day(0, "today")

    weekday = today.weekday()                          # Monday = 0
    this_mon = today - dt.timedelta(days=weekday)
    if re.search(r"\b(?:this|is)\s+weekend\b", t) or re.search(r"\bweekend\b", t):
        sat = this_mon + dt.timedelta(days=5)
        if today > sat + dt.timedelta(days=1):
            sat += dt.timedelta(days=7)
        return _finish(max(sat, today), sat + dt.timedelta(days=1), "week", "weekend", today)
    m = re.search(r"\b(?:next|coming|agle|agla|aane wale)\s+(?:week|hafte|hafta|saptah)\b", t)
    if m:
        s = this_mon + dt.timedelta(days=7)
        return _finish(s, s + dt.timedelta(days=6), "week", m.group(0), today)
    m = re.search(r"\b(?:last|previous|pichle|pichla)\s+(?:week|hafte|hafta|saptah)\b", t)
    if m:
        s = this_mon - dt.timedelta(days=7)
        return _finish(s, s + dt.timedelta(days=6), "week", m.group(0), today)
    m = re.search(r"\b(?:this|is|current)\s+(?:week|hafte|hafta|saptah)\b", t)
    if m:
        return _finish(today, this_mon + dt.timedelta(days=6), "week", m.group(0), today)

    def month_window(y: int, mo: int, words: str) -> Period:
        return _finish(dt.date(y, mo, 1), dt.date(y, mo, calendar.monthrange(y, mo)[1]),
                       "month", words, today)
    m = re.search(r"\b(?:next|coming|agle|agla|aane wale)\s+(?:month|mahine|mahina|maah)\b", t)
    if m:
        y, mo = (today.year + 1, 1) if today.month == 12 else (today.year, today.month + 1)
        return month_window(y, mo, m.group(0))
    m = re.search(r"\b(?:last|previous|pichle|pichla)\s+(?:month|mahine|mahina|maah)\b", t)
    if m:
        y, mo = (today.year - 1, 12) if today.month == 1 else (today.year, today.month - 1)
        return month_window(y, mo, m.group(0))
    m = re.search(r"\b(?:this|is|current)\s+(?:month|mahine|mahina|maah)\b", t)
    if m:
        return month_window(today.year, today.month, m.group(0))
    return None


def parse_period(question: str, now: dt.datetime | dt.date | None = None,
                 tz: str | ZoneInfo | None = None) -> Period | None:
    """The date window a question names, or None. See the module docstring."""
    zone = ZoneInfo(tz) if isinstance(tz, str) else (tz or IST)
    if now is None:
        today = dt.datetime.now(zone).date()
    elif isinstance(now, dt.datetime):
        today = (now.astimezone(zone) if now.tzinfo else now).date()
    else:
        today = now
    if not question or not question.strip():
        return None
    t = _normalise(question)
    t = t.replace("aajkal", " ")
    past_q = _is_past_question(t)
    try:
        found = _explicit(t, today, past_q)
    except _Invalid:
        return None
    if found is not None:
        return found
    return _relative(t, today, past_q)
