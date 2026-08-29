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


def _approx_sun_times(
    date: dt.date,
    latitude: float,
    longitude: float,
    tz_str: str = "Asia/Kolkata",
) -> tuple[dt.datetime, dt.datetime, dt.datetime]:
    """Calculate approximate Sunrise, Sunset, and Next Sunrise for the location.

    Falls back cleanly when high-precision astronomical ephemeris is not required.
    """
    tz = ZoneInfo(tz_str)
    # Default 06:00 to 18:00 localized with solar longitude approximation
    # 4 minutes per degree longitude difference from standard meridian
    std_lon = 82.5 if "Kolkata" in tz_str else 0.0
    offset_mins = (longitude - std_lon) * 4.0

    # Solar declination approximation for day-length variation
    day_of_year = date.timetuple().tm_yday
    # Seasonal variation in minutes
    var_mins = 25.0 * (day_of_year - 80) / 180.0
    if var_mins > 35.0:
        var_mins = 35.0
    elif var_mins < -35.0:
        var_mins = -35.0

    rise_min = int(360 - offset_mins - var_mins)   # Around 06:00
    set_min = int(1080 - offset_mins + var_mins)   # Around 18:00

    sunrise = dt.datetime.combine(date, dt.time(rise_min // 60, rise_min % 60), tzinfo=tz)
    sunset = dt.datetime.combine(date, dt.time(set_min // 60, set_min % 60), tzinfo=tz)
    
    next_date = date + dt.timedelta(days=1)
    next_sunrise = dt.datetime.combine(next_date, dt.time(rise_min // 60, rise_min % 60), tzinfo=tz)

    return sunrise, sunset, next_sunrise


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

    sunrise, sunset, next_sunrise = _approx_sun_times(c_date, latitude, longitude, tz_name)

    # 0 = Monday in Python weekday(), convert to 0 = Sunday (Vedic standard)
    py_weekday = c_date.weekday()
    vedic_weekday = (py_weekday + 1) % 7

    day_slots_names = DAY_SEQUENCE[vedic_weekday]
    night_slots_names = NIGHT_SEQUENCE[vedic_weekday]

    day_duration = (sunset - sunrise).total_seconds()
    slot_day_sec = day_duration / 8.0

    night_duration = (next_sunrise - sunset).total_seconds()
    slot_night_sec = night_duration / 8.0

    day_slots: list[dict[str, Any]] = []
    night_slots: list[dict[str, Any]] = []
    active_slot: dict[str, Any] | None = None

    # Build Day slots
    for i, name in enumerate(day_slots_names):
        s_time = sunrise + dt.timedelta(seconds=i * slot_day_sec)
        e_time = sunrise + dt.timedelta(seconds=(i + 1) * slot_day_sec)
        info = CHOGHADIYA_INFO[name]

        is_current = s_time <= current_time < e_time
        slot_dict = {
            "index": i + 1,
            "period": "day",
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
            "is_current": is_current,
        }
        day_slots.append(slot_dict)
        if is_current:
            active_slot = slot_dict

    # Build Night slots
    for i, name in enumerate(night_slots_names):
        s_time = sunset + dt.timedelta(seconds=i * slot_night_sec)
        e_time = sunset + dt.timedelta(seconds=(i + 1) * slot_night_sec)
        info = CHOGHADIYA_INFO[name]

        is_current = s_time <= current_time < e_time
        slot_dict = {
            "index": i + 9,
            "period": "night",
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
            "is_current": is_current,
        }
        night_slots.append(slot_dict)
        if is_current:
            active_slot = slot_dict

    # If current_time was before sunrise of c_date, active_slot may fall in yesterday's night
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
