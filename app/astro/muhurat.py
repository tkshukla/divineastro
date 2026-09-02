"""Muhurat (auspicious timing) search over a date range.

Scans a range of civil dates and flags each one's basic panchang quality for
a named event, built entirely on `daily_panchang()` — one real ephemeris
call per candidate day, so the range is capped to bound that cost.

Scope, stated honestly: this encodes only the small set of exclusions that
are essentially universal across classical muhurat practice — a rikta tithi
(4th/9th/14th of either paksha), Amavasya, and Bhadra karana (Vishti) are
avoided for the start of nearly any auspicious undertaking in every
tradition this project has touched (Brihat Jataka, Bhrigu Samhita alike).
It deliberately does NOT attempt event-specific nakshatra allow-lists or
planetary-strength rules (e.g. Guru/Shukra Ast for marriage) — those vary
by regional tradition and school, and asserting one as universal would be
the same overclaiming this project has consistently avoided for its other
classical sources. A "good" verdict here means "no classical red flag was
found," not "guaranteed auspicious" — the notes on every result say so, and
a family priest or the couple's own tradition should still have the final
word for anything that matters (a wedding, first griha pravesh).
"""

from __future__ import annotations

import datetime as dt

from .panchang import DEFAULT_AYANAMSA, daily_panchang

MAX_RANGE_DAYS = 90

EVENTS: dict[str, str] = {
    "marriage": "Marriage / wedding ceremony",
    "griha_pravesh": "Griha Pravesh (house-warming / moving in)",
    "mundan": "Mundan (first hair-cutting)",
    "namkaran": "Namkaran (naming ceremony)",
    "general": "General auspicious beginning",
}

# The day-of-paksha numbers classically avoided for starting anything
# auspicious, in both Shukla and Krishna paksha — "rikta" (empty) tithis.
_RIKTA_NUMBERS = {4, 9, 14}


def _tithi_flags(tithi: dict) -> list[str]:
    flags = []
    if tithi.get("number") in _RIKTA_NUMBERS:
        flags.append(f"{tithi.get('label', tithi.get('name'))} is a rikta (empty) tithi")
    if tithi.get("paksha") == "Krishna" and tithi.get("number") == 15:
        flags.append("Amavasya — the moonless tithi")
    return flags


def _day_quality(panchang: dict, event: str) -> tuple[str, list[str]]:
    """One of 'avoid' | 'caution' | 'good', plus the reasons why."""
    reasons: list[str] = []
    avoid = False
    caution = False

    tithis = panchang.get("tithi") or []
    if tithis:
        flags = _tithi_flags(tithis[0])
        if flags:
            avoid = True
            reasons.extend(flags)

    karanas = panchang.get("karana") or []
    if any(k.get("name") == "Vishti" for k in karanas):
        caution = True
        reasons.append("Bhadra (Vishti karana) falls during part of this day")

    vara = panchang.get("vara") or {}
    if event == "marriage" and vara.get("weekday") == "Tuesday":
        caution = True
        reasons.append("Tuesday (Mangalvar) is avoided for weddings in many traditions")

    if avoid:
        return "avoid", reasons
    if caution:
        return "caution", reasons
    return "good", reasons


def find_muhurat(
    event: str,
    from_date: dt.date | str,
    to_date: dt.date | str,
    latitude: float,
    longitude: float,
    timezone: str,
    *,
    ayanamsa: str = DEFAULT_AYANAMSA,
) -> list[dict]:
    """One entry per day in range: `{date, verdict, tithi, nakshatra, vara, notes}`.

    Raises `ValueError` for an unknown event, an inverted or over-long range
    — the caller (the `/api/muhurat` route) turns that into a 400.
    """
    if event not in EVENTS:
        raise ValueError(f"Unknown event '{event}'. Choose one of: {', '.join(EVENTS)}.")

    if isinstance(from_date, str):
        from_date = dt.date.fromisoformat(from_date)
    if isinstance(to_date, str):
        to_date = dt.date.fromisoformat(to_date)
    if to_date < from_date:
        raise ValueError("to_date must not be before from_date.")
    span = (to_date - from_date).days + 1
    if span > MAX_RANGE_DAYS:
        raise ValueError(f"Range too long — at most {MAX_RANGE_DAYS} days at a time.")

    out: list[dict] = []
    cursor = from_date
    while cursor <= to_date:
        panchang = daily_panchang(
            cursor, latitude, longitude, timezone, ayanamsa=ayanamsa)
        verdict, reasons = _day_quality(panchang, event)
        tithi0 = (panchang.get("tithi") or [{}])[0]
        nak0 = (panchang.get("nakshatra") or [{}])[0]
        out.append({
            "date": cursor.isoformat(),
            "verdict": verdict,
            "tithi": tithi0.get("label") or tithi0.get("name"),
            "nakshatra": nak0.get("name"),
            "vara": (panchang.get("vara") or {}).get("name"),
            "notes": reasons,
        })
        cursor += dt.timedelta(days=1)
    return out
