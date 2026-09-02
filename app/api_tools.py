"""Free Vedic tools: Kundali Milan, Panchang, and the dosha checks.

These are deliberately **not** metered. They cost no LLM tokens — every number
here comes from the deterministic engine — and they are what people search for.
Someone who came for a Guna Milan score and stayed for a reading is the point;
putting a paywall in front of the thing that brings them is not.

Mounted by main.py. Kept out of api_account.py so the money path stays readable
on its own.
"""

from __future__ import annotations

import datetime as dt
from zoneinfo import ZoneInfo

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from . import geo
from .astro import matching
from .astro import muhurat as muhurat_engine
from .astro import panchang as panchang_engine
from .chart_service import BirthData, build

router = APIRouter(prefix="/api")


class PersonIn(BaseModel):
    """One side of a match. Same shape the chart form already posts."""

    name: str = ""
    date: str
    time: str = "12:00"
    time_known: bool = True
    place: str = ""
    latitude: float
    longitude: float
    timezone: str = ""
    gender: str = ""
    zodiac: str = "sidereal"          # matching is a Vedic rule set: sidereal
    ayanamsa: str = "lahiri"
    house_system: str = Field(default="Whole Sign")


class MatchIn(BaseModel):
    groom: PersonIn
    bride: PersonIn
    lang: str = "en"


def _chart(p: PersonIn):
    """Build a chart from one side of the form.

    Guna Milan is defined on the sidereal Moon, so the zodiac is forced rather
    than trusted from the client: a tropical chart would misread every koota by
    roughly a whole nakshatra. matching.py refuses tropical input outright, and
    this makes sure it never has to.
    """
    tz = p.timezone or geo.timezone_for(p.latitude, p.longitude)
    try:
        return build(BirthData(
            name=p.name.strip() or "—",
            date=p.date,
            time=(p.time or "12:00") if p.time_known else "12:00",
            latitude=p.latitude,
            longitude=p.longitude,
            timezone=tz,
            place=p.place or f"{p.latitude:.4f}, {p.longitude:.4f}",
            zodiac="sidereal",
            ayanamsa=p.ayanamsa or "lahiri",
            house_system="Whole Sign",
            time_known=p.time_known,
        ))
    except Exception as exc:
        raise HTTPException(400, f"Could not cast that chart: {exc}") from exc


@router.post("/match")
def kundali_milan(body: MatchIn) -> dict:
    """36-point Ashtakoot Guna Milan plus Mangal Dosha for both people."""
    groom, bride = _chart(body.groom), _chart(body.bride)
    lang = body.lang if body.lang in ("en", "hi") else "en"
    try:
        result = matching.match(groom, bride, lang=lang)
    except matching.MatchingError as exc:
        raise HTTPException(400, str(exc)) from exc

    # Birth time drives Mangal Dosha (it needs the Lagna) but not the ashtakoot,
    # which only needs the Moon. Say so rather than quietly presenting a
    # noon-chart Manglik verdict as if it were solid.
    result["time_known"] = {
        "groom": body.groom.time_known, "bride": body.bride.time_known,
    }
    if not (body.groom.time_known and body.bride.time_known):
        result["caveat"] = (
            "जन्म समय अनुपलब्ध था, इसलिए दोपहर का समय उपयोग किया गया। 36-अंक स्कोर "
            "प्रभावित नहीं है — यह केवल चंद्रमा पर निर्भर करता है — परंतु मांगलिक निर्णय "
            "लग्न पर निर्भर करता है और इस पर भरोसा नहीं करना चाहिए।"
            if lang == "hi" else
            "A birth time is missing, so noon was used. The 36-point score is "
            "unaffected — it depends only on the Moon — but the Manglik verdict "
            "depends on the ascendant and should not be relied on here."
        )
    return result


@router.get("/panchang")
def daily_panchang(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    date: str | None = None,
    timezone: str = "",
) -> dict:
    """The five limbs plus Rahu Kaal for a date and place. Defaults to today."""
    tz = timezone or geo.timezone_for(latitude, longitude)
    # "Today" means today *where the panchang is for*, not on the server. The
    # container runs UTC, so between midnight and 05:30 UTC an Indian visitor
    # was being shown yesterday's panchang.
    when = date or dt.datetime.now(ZoneInfo(tz)).date().isoformat()
    try:
        return panchang_engine.daily_panchang(when, latitude, longitude, tz)
    except ValueError as exc:
        raise HTTPException(400, f"Could not compute the panchang: {exc}") from exc


@router.get("/muhurat")
def find_muhurat(
    event: str,
    from_date: str,
    to_date: str,
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    timezone: str = "",
) -> dict:
    """Auspicious-timing search for one event across a date range (<=90 days)."""
    tz = timezone or geo.timezone_for(latitude, longitude)
    try:
        days = muhurat_engine.find_muhurat(event, from_date, to_date, latitude, longitude, tz)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    return {
        "event": event, "event_label": muhurat_engine.EVENTS[event],
        "from_date": from_date, "to_date": to_date, "timezone": tz,
        "days": days,
    }
