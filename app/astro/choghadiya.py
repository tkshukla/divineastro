"""Classical Vedic Choghadiya engine.

Calculates real-time Day and Night Choghadiya intervals:
- Amrit (अमृत) - Highly Auspicious / Best
- Shubh (शुभ) - Auspicious / Good for religious and important work
- Labh (लाभ) - Auspicious / Commercial gains, business & wealth
- Char (चल) - Neutral / Travel and dynamic activities
- Rog (रोग) - Inauspicious / Avoid new beginnings
- Kaal (काल) - Inauspicious / Saturn ruled, delays & losses
- Udveg (उद्वेग) - Inauspicious / Sun ruled, disputes & unrest
"""

from __future__ import annotations

import datetime as dt
from typing import Any
from zoneinfo import ZoneInfo

from .panchang import sun_times

# Choghadiya properties
CHOGHADIYA_INFO = {
    "Amrit": {
        "name_hi": "अमृत",
        "ruler": "Moon",
        "ruler_hi": "चंद्र",
        "quality": "auspicious",
        "quality_hi": "अति शुभ",
        "score": 95,
        "description": "Best time for all ceremonies, investments, agreements, and starting important endeavors.",
        "description_hi": "सभी प्रकार के मांगलिक कार्य, निवेश, समझौता एवं नवीन शुरुआत हेतु सर्वश्रेष्ठ समय।",
    },
    "Shubh": {
        "name_hi": "शुभ",
        "ruler": "Jupiter",
        "ruler_hi": "गुरु",
        "quality": "auspicious",
        "quality_hi": "शुभ",
        "score": 90,
        "description": "Highly auspicious for ceremonies, religious rituals, education, and purchasing property.",
        "description_hi": "विवाह, धार्मिक अनुष्ठान, शिक्षा आरंभ एवं संपत्ति क्रय हेतु अत्यंत शुभ मुहूर्त।",
    },
    "Labh": {
        "name_hi": "लाभ",
        "ruler": "Mercury",
        "ruler_hi": "बुध",
        "quality": "auspicious",
        "quality_hi": "शुभ / लाभप्रद",
        "score": 85,
        "description": "Favorable for business, trade, financial transactions, launching products, and interviews.",
        "description_hi": "व्यापार, आर्थिक लेनदेन, नवीन उत्पाद शुभारंभ एवं साक्षात्कार हेतु अनुकूल समय।",
    },
    "Char": {
        "name_hi": "चल",
        "ruler": "Venus",
        "ruler_hi": "शुक्र",
        "quality": "neutral",
        "quality_hi": "सामान्य / गतिमान",
        "score": 60,
        "description": "Neutral. Excellent for journeys, travel, vehicle purchases, and shifting places.",
        "description_hi": "सामान्य अनुकूल। यात्रा, वाहन क्रय एवं स्थान परिवर्तन हेतु उत्तम।",
    },
    "Rog": {
        "name_hi": "रोग",
        "ruler": "Mars",
        "ruler_hi": "मंगल",
        "quality": "inauspicious",
        "quality_hi": "अशुभ / रोग",
        "score": 25,
        "description": "Inauspicious. Avoid medical procedures or conflict. Only suitable for competitive sports or defeating rivals.",
        "description_hi": "अशुभ। मांगलिक कार्य वर्जित। प्रतिस्पर्धा व वाद-विवाद निवारण हेतु ही उपयोगी।",
    },
    "Kaal": {
        "name_hi": "काल",
        "ruler": "Saturn",
        "ruler_hi": "शनि",
        "quality": "inauspicious",
        "quality_hi": "अशुभ / काल",
        "score": 20,
        "description": "Inauspicious. Ruled by Saturn; causes delays and setbacks. Avoid new ventures or signing documents.",
        "description_hi": "अशुभ। कार्यों में विलंब व हानि संभव। नए सौदों व अनुबंधों से बचें।",
    },
    "Udveg": {
        "name_hi": "उद्वेग",
        "ruler": "Sun",
        "ruler_hi": "सूर्य",
        "quality": "inauspicious",
        "quality_hi": "अशुभ / उद्वेग",
        "score": 30,
        "description": "Inauspicious. Causes restlessness and anxiety. Favorable only for government filings or official duties.",
        "description_hi": "अशुभ। मानसिक तनाव व अशांति संभव। केवल राजकीय कार्यों व कर आदि हेतु उपयुक्त।",
    },
}

# Classical Weekday sequences
# Day sequence starts with weekday ruler
DAY_SEQUENCE = {
    0: ["Udveg", "Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg"],      # Sunday
    1: ["Amrit", "Kaal", "Shubh", "Rog", "Udveg", "Char", "Labh", "Amrit"],      # Monday
    2: ["Rog", "Udveg", "Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog"],        # Tuesday
    3: ["Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg", "Char", "Labh"],        # Wednesday
    4: ["Shubh", "Rog", "Udveg", "Char", "Labh", "Amrit", "Kaal", "Shubh"],      # Thursday
    5: ["Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg", "Char"],        # Friday
    6: ["Kaal", "Shubh", "Rog", "Udveg", "Char", "Labh", "Amrit", "Kaal"],        # Saturday
}

# Night sequence starts with 5th weekday ruler from day ruler
NIGHT_SEQUENCE = {
    0: ["Shubh", "Amrit", "Char", "Rog", "Kaal", "Labh", "Udveg", "Shubh"],      # Sunday Night
    1: ["Char", "Rog", "Kaal", "Labh", "Udveg", "Shubh", "Amrit", "Char"],        # Monday Night
    2: ["Kaal", "Labh", "Udveg", "Shubh", "Amrit", "Char", "Rog", "Kaal"],        # Tuesday Night
    3: ["Udveg", "Shubh", "Amrit", "Char", "Rog", "Kaal", "Labh", "Udveg"],      # Wednesday Night
    4: ["Amrit", "Char", "Rog", "Kaal", "Labh", "Udveg", "Shubh", "Amrit"],      # Thursday Night
    5: ["Rog", "Kaal", "Labh", "Udveg", "Shubh", "Amrit", "Char", "Rog"],        # Friday Night
    6: ["Labh", "Udveg", "Shubh", "Amrit", "Char", "Rog", "Kaal", "Labh"],        # Saturday Night
}


def eighths(start: dt.datetime, end: dt.datetime) -> list[tuple[dt.datetime, dt.datetime]]:
    """Cut [start, end) into the eight equal choghadiya parts.

    Each boundary is computed from `start` (not by accumulating steps) so the
    last part ends exactly at `end` and the parts are contiguous.
    """
    step = (end - start) / 8
    return [(start + i * step, end if i == 7 else start + (i + 1) * step) for i in range(8)]


def day_night_slots(
    vara: int,
    sunrise: dt.datetime,
    sunset: dt.datetime,
    next_sunrise: dt.datetime,
) -> tuple[list[tuple[str, dt.datetime, dt.datetime]], list[tuple[str, dt.datetime, dt.datetime]]]:
    """(name, start, end) for the 8 day slots (sunrise -> sunset) and the 8 night
    slots (sunset -> next sunrise) of a vedic weekday (Sunday = 0).

    The single implementation shared by the in-app tool (/api/choghadiya) and
    the server-rendered /choghadiya pages (seo_pages.choghadiya_slots).
    """
    day = [(n, s, e) for n, (s, e) in zip(DAY_SEQUENCE[vara], eighths(sunrise, sunset))]
    night = [(n, s, e) for n, (s, e) in zip(NIGHT_SEQUENCE[vara], eighths(sunset, next_sunrise))]
    return day, night


def get_choghadiya_schedule(
    target_date: str | dt.date | None = None,
    latitude: float = 28.6139,
    longitude: float = 77.2090,
    tz_name: str = "Asia/Kolkata",
    now_dt: dt.datetime | None = None,
    lang: str = "en",
) -> dict[str, Any]:
    """Calculate complete 16-slot Day and Night Choghadiya timeline with active slot."""
    hi = lang == "hi"
    tz = ZoneInfo(tz_name)

    if isinstance(target_date, str):
        c_date = dt.date.fromisoformat(target_date)
    elif isinstance(target_date, dt.date):
        c_date = target_date
    else:
        c_date = dt.datetime.now(tz).date()

    if now_dt is None:
        current_time = dt.datetime.now(tz)
    else:
        current_time = now_dt.astimezone(tz) if now_dt.tzinfo else now_dt.replace(tzinfo=tz)

    # The same Swiss Ephemeris sunrise/sunset the Panchang prints (DIVASTRO-103:
    # this used to be a seasonal estimate, ~20-50 min off for Delhi in October).
    sunrise, sunset, next_sunrise = sun_times(c_date, latitude, longitude, tz_name)
    if not (sunrise and sunset and next_sunrise):
        raise ValueError("The Sun does not both rise and set on this date at this "
                         "latitude, so Choghadiya is not defined.")

    # 0 = Monday in Python weekday(), convert to 0 = Sunday (Vedic standard)
    py_weekday = c_date.weekday()
    vedic_weekday = (py_weekday + 1) % 7

    day_parts, night_parts = day_night_slots(vedic_weekday, sunrise, sunset, next_sunrise)

    def slot(index: int, period: str, name: str, s_time: dt.datetime, e_time: dt.datetime) -> dict[str, Any]:
        info = CHOGHADIYA_INFO[name]
        return {
            "index": index,
            "period": period,
            "name": name,
            "name_label": info["name_hi"] if hi else name,
            "ruler": info["ruler"],
            "ruler_label": info["ruler_hi"] if hi else info["ruler"],
            "quality": info["quality"],
            "quality_label": info["quality_hi"] if hi else info["quality"].capitalize(),
            "score": info["score"],
            "start": s_time.strftime("%H:%M"),
            "end": e_time.strftime("%H:%M"),
            "start_iso": s_time.isoformat(),
            "end_iso": e_time.isoformat(),
            "description": info["description_hi"] if hi else info["description"],
            "is_current": s_time <= current_time < e_time,
        }

    day_slots = [slot(i + 1, "day", n, s, e) for i, (n, s, e) in enumerate(day_parts)]
    night_slots = [slot(i + 9, "night", n, s, e) for i, (n, s, e) in enumerate(night_parts)]
    active_slot: dict[str, Any] | None = next(
        (x for x in day_slots + night_slots if x["is_current"]), None)

    # Between midnight and this date's sunrise the running choghadiya belongs to
    # the PREVIOUS vedic day's night (sunset yesterday -> sunrise today), whose
    # sequence follows yesterday's weekday lord.
    if active_slot is None and current_time < sunrise:
        prev = c_date - dt.timedelta(days=1)
        p_rise, p_set, p_next = sun_times(prev, latitude, longitude, tz_name)
        if p_rise and p_set and p_next:
            _, prev_night = day_night_slots((prev.weekday() + 1) % 7, p_rise, p_set, p_next)
            for i, (n, s, e) in enumerate(prev_night):
                if s <= current_time < e:
                    active_slot = slot(i + 9, "night", n, s, e)
                    active_slot["date"] = prev.isoformat()
                    break

    # A date that is neither today nor tomorrow-before-sunrise: keep the old
    # behaviour of pointing at the first slot (not marked current).
    if active_slot is None:
        active_slot = day_slots[0]

    return {
        "date": c_date.isoformat(),
        "weekday": ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"][vedic_weekday],
        "weekday_hi": ["रविवार", "सोमवार", "मंगलवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार"][vedic_weekday],
        "sunrise": sunrise.strftime("%H:%M"),
        "sunset": sunset.strftime("%H:%M"),
        "active_slot": active_slot,
        "day_slots": day_slots,
        "night_slots": night_slots,
    }
