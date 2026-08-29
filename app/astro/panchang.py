"""Panchang, Sade Sati and Kaal Sarp — the Vedic almanac layer.

Three things live here, and they share one property: they are *time* questions
rather than chart-shape questions, so unlike the rest of ``app/astro`` they do
reach for the ephemeris. They reach for the same one everything else uses —
Swiss Ephemeris, through the copy stellium already unpacked and initialised —
so a longitude computed here and a longitude printed on a kundali page cannot
disagree.

  * :func:`daily_panchang` — the five limbs (tithi, nakshatra, yoga, karana,
    vara) plus sunrise/sunset, moonrise/moonset and the muhurta windows people
    actually look up before booking a train or a wedding.
  * :func:`sade_sati` — Saturn's seven-and-a-half-year pass over the 12th, 1st
    and 2nd signs from the natal Moon, plus the 2.5-year Dhaiya.
  * :func:`kaal_sarp` — the seven classical planets hemmed inside the nodal
    axis.

Two conventions are worth stating up front because almost every disagreement
between two panchang apps traces back to one of them:

**Sunrise defines the day, not midnight.** The vara (weekday), and therefore
Rahu Kaal and everything else keyed to the weekday, belongs to the vedic day
that runs from one sunrise to the next. At 03:00 on a Friday morning the vara
is still Thursday. Getting this wrong shifts Rahu Kaal by a whole segment for
anybody who checks it before dawn.

**Sunrise means the upper limb, with refraction.** Swiss Ephemeris also offers
``SE_BIT_HINDU_RISING`` (disc centre, no refraction), which the Surya Siddhanta
tradition prefers and which lands 4-5 minutes later in the Indian latitudes.
Drik Panchang, the Rashtriya Panchang and every Indian newspaper print the
visible upper-limb sunrise, so that is the default here; see
:data:`HINDU_RISING`.

All times come back as ISO-8601 strings carrying the location's UTC offset.
Nothing in this module is naive, and nothing in it touches the database, the
network or the filesystem beyond the ephemeris stellium already opened.
"""

from __future__ import annotations

import datetime as dt
from zoneinfo import ZoneInfo

try:
    import swisseph as swe
    from stellium.core.ayanamsa import get_ayanamsa, get_ayanamsa_value
    from stellium.data.paths import initialize_ephemeris
except ImportError:  # pragma: no cover - defensive for local environments without compiled wheels
    swe = None
    get_ayanamsa = get_ayanamsa_value = initialize_ephemeris = None

from ..chart_service import NAKSHATRAS, SIGNS, dms, house_of, norm360

# --------------------------------------------------------------------------
# Reference tables
# --------------------------------------------------------------------------

# The 15 tithi names of a paksha. Index 14 is the full/new moon, which is named
# Purnima in the bright fortnight and Amavasya in the dark one.
TITHI_NAMES = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi",
    "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi",
    "Trayodashi", "Chaturdashi", "Purnima",
]

YOGA_NAMES = [
    "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda",
    "Sukarma", "Dhriti", "Shula", "Ganda", "Vriddhi", "Dhruva", "Vyaghata",
    "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyana", "Parigha", "Shiva",
    "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma", "Indra", "Vaidhriti",
]

# The seven movable karanas cycle eight times through the lunar month; four
# fixed karanas bracket them. Half-tithi 1 of the month is Kimstughna, 2..57
# are the movable cycle, and 58..60 are Shakuni, Chatushpada and Naga.
MOVABLE_KARANAS = ["Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti"]
FIXED_KARANAS = ["Shakuni", "Chatushpada", "Naga", "Kimstughna"]

VARA_NAMES = [
    "Ravivara", "Somavara", "Mangalavara", "Budhavara",
    "Guruvara", "Shukravara", "Shanivara",
]
VARA_ENGLISH = [
    "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday",
]
VARA_LORDS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

# Daylight is cut into eight equal parts; each of the three inauspicious
# windows takes one of them, and *which* one is a fixed function of the vara.
# These orderings are the whole feature — the tables below are indexed by vara
# (Sunday = 0) and hold the ZERO-based eighth. Cross-checked against Drik
# Panchang for Delhi and Varanasi on three weekdays (see tests/test_panchang.py):
# Rahu Kaal is the 8th part on Sunday, 2nd on Monday, 7th on Tuesday, 5th on
# Wednesday, 6th on Thursday, 4th on Friday, 3rd on Saturday.
RAHU_SEGMENT = (7, 1, 6, 4, 5, 3, 2)
YAMAGANDA_SEGMENT = (4, 3, 2, 1, 0, 6, 5)
GULIKA_SEGMENT = (6, 5, 4, 3, 2, 1, 0)

# Abhijit is the 8th of the 15 muhurtas of daylight, i.e. the one straddling
# local apparent noon. It is held to be auspicious on every weekday except
# Wednesday, whose lord Mercury is said to spoil it; Drik Panchang and the
# North Indian almanacs both suppress it there, so we do too.
ABHIJIT_MUHURTA = 8
ABHIJIT_EXCLUDED_VARA = 3

# Swiss Ephemeris rise/set flavour for the SUN. False = visible sunrise (upper
# limb, with atmospheric refraction), which is what published Indian panchangs
# print. True switches to SE_BIT_HINDU_RISING (disc centre, no refraction, no
# ecliptic latitude), the Surya Siddhanta convention, ~4 min later in India.
HINDU_RISING = False

# The MOON is deliberately not treated the same way. Published panchangs time
# moonrise to the centre of the disc crossing the true (unrefracted) horizon,
# not to the first visible sliver, and the two differ by about five minutes.
# Checked against Drik Panchang for Delhi and Varanasi: with these flags we land
# within half a minute, with the Sun's flags we are five minutes out.
_MOON_RISE_FLAGS = (swe.BIT_DISC_CENTER | swe.BIT_NO_REFRACTION) if swe is not None else 0

# "Lahiri" is not one number. Swiss Ephemeris ships five spellings of it, and
# the spread between them is about 20 arc-seconds — nothing on a chart wheel,
# but enough to move a nakshatra boundary by a minute and a Saturn ingress by
# an hour and a quarter. stellium's "lahiri" is SE_SIDM_LAHIRI, and that is the
# one Drik Panchang's daily pages match (checked to the minute on three dates
# and three limbs). Published Saturn *transit tables* often use the VP285
# variant instead, which is why our ingress instants can sit ~1.3 h earlier than
# a table someone quotes; the date is the same, and Sade Sati does not care.
DEFAULT_AYANAMSA = "lahiri"

# --------------------------------------------------------------------------
# Ephemeris plumbing
# --------------------------------------------------------------------------

# Bisection tolerance for a limb boundary, in days. 1e-6 d is 0.09 s, which is
# far finer than the couple of minutes two published panchangs differ by, and
# costs ~40 ephemeris calls per boundary.
_TOLERANCE_DAYS = 1e-6

# No limb ever takes longer than ~27 h to advance one division (the slowest is
# a nakshatra with the Moon near apogee), so a two-day bracket always contains
# the crossing and the angle can never wrap 360° inside it.
_BRACKET_DAYS = 2.0


def _ephemeris() -> None:
    """Point Swiss Ephemeris at stellium's data directory (idempotent)."""
    initialize_ephemeris()


def _tropical(jd: float, body: int) -> float:
    return swe.calc_ut(jd, body, swe.FLG_SWIEPH)[0][0]


def _sidereal(jd: float, body: int, ayanamsa: str) -> float:
    """Sidereal ecliptic longitude, by the same route stellium takes.

    Subtracting the ayanamsa from a tropical longitude is *almost* the same
    thing, but not quite — Swiss Ephemeris rotates into the sidereal frame
    rather than sliding along the ecliptic of date, and the two disagree by up
    to a thousandth of a degree. That is nothing on a chart wheel and about two
    minutes on a Saturn ingress, but it would mean this module and the kundali
    page quietly printing different longitudes for the same planet. They must
    not, so we call it the way stellium's ephemeris engine does.
    """
    swe.set_sid_mode(get_ayanamsa(ayanamsa).swe_constant)
    return swe.calc_ut(jd, body, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)[0][0] % 360.0


def _ayanamsa_at(jd: float, ayanamsa: str) -> float:
    return get_ayanamsa_value(jd, ayanamsa)


def _to_jd(moment: dt.datetime) -> float:
    """Aware datetime -> Julian Day (UT)."""
    u = moment.astimezone(dt.timezone.utc)
    return swe.julday(u.year, u.month, u.day,
                      u.hour + u.minute / 60.0 + (u.second + u.microsecond / 1e6) / 3600.0)


def _from_jd(jd: float, tz: ZoneInfo) -> dt.datetime:
    """Julian Day (UT) -> aware datetime in `tz`, rounded to the second."""
    year, month, day, hours = swe.revjul(jd)
    utc = dt.datetime(year, month, day, tzinfo=dt.timezone.utc) + dt.timedelta(hours=hours)
    utc += dt.timedelta(microseconds=500000)          # round rather than truncate
    return utc.replace(microsecond=0).astimezone(tz)


def _iso(moment: dt.datetime | None) -> str | None:
    return moment.isoformat() if moment else None


# --------------------------------------------------------------------------
# Rise and set
# --------------------------------------------------------------------------

def _rise_or_set(jd_from: float, body: int, geopos: tuple[float, float, float],
                 rising: bool, limit_days: float) -> float | None:
    """Next rise/set of `body` after `jd_from`, or None if there isn't one.

    Returns None for the two cases that must not raise: a circumpolar Sun
    (retflag -2, midnight sun or polar night) and a body whose next event falls
    outside the window we care about — the Moon legitimately skips a rise or a
    set roughly once a month even at the equator.
    """
    flag = swe.CALC_RISE if rising else swe.CALC_SET
    if body == swe.MOON:
        flag |= _MOON_RISE_FLAGS
    elif HINDU_RISING:
        flag |= swe.BIT_HINDU_RISING
    try:
        retflag, tret = swe.rise_trans(jd_from, body, flag, geopos)
    except Exception:                                 # pragma: no cover - defensive
        return None
    if retflag < 0 or not tret or tret[0] <= 0:
        return None
    return tret[0] if tret[0] - jd_from <= limit_days else None


# --------------------------------------------------------------------------
# Limb boundaries
# --------------------------------------------------------------------------

# Every panchang limb is a monotonically *increasing* angle: the Moon never
# retrogrades, and the Moon-minus-Sun elongation cannot stall because the Moon's
# slowest true motion (~11.8°/day) still beats the Sun's fastest (~1.02°/day).
# That is what makes plain bisection safe here — no need to hunt for turning
# points the way a planetary ingress search has to.

def _advance(angle_at, jd0: float, arc: float) -> float:
    """When the rising angle has gained `arc` degrees on its value at `jd0`."""
    base = angle_at(jd0)

    def gained(jd: float) -> float:
        return (angle_at(jd) - base) % 360.0

    lo, hi = jd0, jd0 + _BRACKET_DAYS
    while gained(hi) < arc and hi - jd0 < 2 * _BRACKET_DAYS:
        hi += _BRACKET_DAYS
    while hi - lo > _TOLERANCE_DAYS:
        mid = (lo + hi) / 2.0
        if gained(mid) < arc:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def _retreat(angle_at, jd0: float, arc: float) -> float:
    """When the rising angle was `arc` degrees short of its value at `jd0`."""
    base = angle_at(jd0)

    def lost(jd: float) -> float:
        return (base - angle_at(jd)) % 360.0

    lo, hi = jd0 - _BRACKET_DAYS, jd0
    while lost(lo) < arc and jd0 - lo < 2 * _BRACKET_DAYS:
        lo -= _BRACKET_DAYS
    while hi - lo > _TOLERANCE_DAYS:
        mid = (lo + hi) / 2.0
        if lost(mid) > arc:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def _limb_run(angle_at, divisions: int, jd_start: float, jd_end: float,
              max_entries: int = 6) -> list[tuple[int, float, float]]:
    """The divisions of one limb covering [jd_start, jd_end).

    Returns ``(index, start_jd, end_jd)`` triples. The first entry is the one
    already running at `jd_start` and its start is its *true* start, found by
    searching backwards — that is what lets the caller say "Vishti began at
    21:04 yesterday", not "Vishti began at sunrise".
    """
    step = 360.0 / divisions
    out: list[tuple[int, float, float]] = []
    cursor = jd_start
    while cursor < jd_end and len(out) < max_entries:
        angle = angle_at(cursor)
        index = int(angle // step) % divisions
        into = angle - index * step                   # degrees already elapsed
        start = _retreat(angle_at, cursor, into) if not out else cursor
        end = _advance(angle_at, cursor, step - into)
        out.append((index, start, end))
        cursor = end + _TOLERANCE_DAYS                # nudge past the boundary
    return out


def _tithi_label(index: int) -> tuple[str, str, int]:
    """0-based tithi index -> (name, paksha, number within the paksha)."""
    paksha = "Shukla" if index < 15 else "Krishna"
    within = index % 15
    name = TITHI_NAMES[within]
    if within == 14:
        name = "Purnima" if paksha == "Shukla" else "Amavasya"
    return name, paksha, within + 1


def _karana_name(index: int) -> str:
    """0-based half-tithi of the lunar month (0..59) -> karana name."""
    if index == 0:
        return "Kimstughna"
    if index >= 57:
        return FIXED_KARANAS[index - 57]
    return MOVABLE_KARANAS[(index - 1) % 7]


# --------------------------------------------------------------------------
# Panchang
# --------------------------------------------------------------------------

def daily_panchang(
    date: dt.date | str,
    latitude: float,
    longitude: float,
    timezone: str,
    *,
    ayanamsa: str = DEFAULT_AYANAMSA,
    elevation: float = 0.0,
) -> dict:
    """The almanac for the vedic day that begins at `date`'s sunrise.

    `date` is a local calendar date at the given location. Everything returned
    is reckoned from that morning's sunrise to the next one, which is why a
    tithi or a moonrise may carry a timestamp on the following civil date.

    Above the polar circles there may be no sunrise at all. That is reported —
    ``sun.rises`` is false and the muhurta windows are None — rather than
    raised, and the five limbs are then reckoned from local midnight, which is
    an admitted fallback and is flagged in ``notes``.
    """
    _ephemeris()
    tz = ZoneInfo(timezone)
    if isinstance(date, str):
        date = dt.date.fromisoformat(date)
    elif isinstance(date, dt.datetime):
        date = date.date()

    geopos = (float(longitude), float(latitude), float(elevation))
    midnight = dt.datetime(date.year, date.month, date.day, tzinfo=tz)
    jd_midnight = _to_jd(midnight)

    notes: list[str] = []
    sunrise = _rise_or_set(jd_midnight, swe.SUN, geopos, True, 1.5)
    sunset = _rise_or_set(sunrise, swe.SUN, geopos, False, 1.5) if sunrise else None
    next_sunrise = _rise_or_set(sunset or jd_midnight + 1.0, swe.SUN, geopos, True, 1.5)

    # A day needs both ends. One without the other happens right at the edge of
    # the polar circle and is just as unusable as neither.
    bounded = sunrise is not None and sunset is not None
    if not bounded:
        notes.append(
            "The Sun does not both rise and set on this date at this latitude, so the "
            "vedic day cannot be bounded by sunrise. The limbs below are reckoned from "
            "local midnight instead, and the sunrise-based muhurtas are not defined."
        )
    day_start = sunrise if bounded else jd_midnight
    day_end = next_sunrise if (bounded and next_sunrise) else jd_midnight + 1.0

    # --- the five limbs ---------------------------------------------------
    def elongation(jd: float) -> float:
        # Tithi and karana are Moon minus Sun, so they are the one part of the
        # panchang that no choice of ayanamsa can move.
        return (_tropical(jd, swe.MOON) - _tropical(jd, swe.SUN)) % 360.0

    def sidereal_moon(jd: float) -> float:
        return _sidereal(jd, swe.MOON, ayanamsa)

    def yoga_angle(jd: float) -> float:
        return (_sidereal(jd, swe.SUN, ayanamsa)
                + _sidereal(jd, swe.MOON, ayanamsa)) % 360.0

    tithis = [
        _tithi_entry(i, s, e, tz)
        for i, s, e in _limb_run(elongation, 30, day_start, day_end)
    ]
    nakshatras = [
        _nakshatra_entry(i, s, e, tz, sidereal_moon, max(s, day_start))
        for i, s, e in _limb_run(sidereal_moon, 27, day_start, day_end)
    ]
    yogas = [
        _named_entry(YOGA_NAMES[i], i, s, e, tz)
        for i, s, e in _limb_run(yoga_angle, 27, day_start, day_end)
    ]
    karanas = [
        _named_entry(_karana_name(i), i, s, e, tz)
        for i, s, e in _limb_run(elongation, 60, day_start, day_end)
    ]

    # --- vara -------------------------------------------------------------
    vara_index = (date.weekday() + 1) % 7             # python Monday=0 -> Sunday=0

    # --- moon rise/set inside the vedic day -------------------------------
    span = day_end - day_start
    moonrise = _rise_or_set(day_start, swe.MOON, geopos, True, span)
    moonset = _rise_or_set(day_start, swe.MOON, geopos, False, span)

    # --- the eighths and the muhurta --------------------------------------
    muhurtas = _day_windows(sunrise, sunset, vara_index, tz) if bounded else {
        "rahu_kaal": None, "yamaganda": None, "gulika_kaal": None, "abhijit": None,
    }
    if bounded and muhurtas["abhijit"] is None:
        notes.append(
            "Abhijit muhurta is omitted on Wednesday, whose lord Mercury is held to "
            "spoil it."
        )

    ayan = _ayanamsa_at(day_start, ayanamsa)
    sun_lon = _sidereal(day_start, swe.SUN, ayanamsa)
    moon_lon = sidereal_moon(day_start)

    return {
        "date": date.isoformat(),
        "location": {
            "latitude": round(float(latitude), 6),
            "longitude": round(float(longitude), 6),
            "elevation": float(elevation),
            "timezone": timezone,
            "utc_offset": midnight.strftime("%z"),
        },
        "reckoned_from": "sunrise" if bounded else "midnight",
        "vara": {
            "index": vara_index,
            "name": VARA_NAMES[vara_index],
            "weekday": VARA_ENGLISH[vara_index],
            "lord": VARA_LORDS[vara_index],
            "starts": _iso(_from_jd(day_start, tz)),
            "ends": _iso(_from_jd(day_end, tz)),
        },
        "sun": {
            "rises": sunrise is not None,
            "sets": sunset is not None,
            "rise": _iso(_from_jd(sunrise, tz)) if sunrise else None,
            "set": _iso(_from_jd(sunset, tz)) if sunset else None,
            "next_rise": _iso(_from_jd(next_sunrise, tz)) if next_sunrise else None,
            "day_length_minutes": round((sunset - sunrise) * 1440.0, 2) if bounded else None,
            "sign": SIGNS[int(sun_lon // 30)],
            "longitude": round(sun_lon, 4),
        },
        "moon": {
            "rise": _iso(_from_jd(moonrise, tz)) if moonrise else None,
            "set": _iso(_from_jd(moonset, tz)) if moonset else None,
            "sign": SIGNS[int(moon_lon // 30)],
            "longitude": round(moon_lon, 4),
            "position": f"{SIGNS[int(moon_lon // 30)]} {dms(moon_lon % 30)}",
        },
        "tithi": tithis,
        "nakshatra": nakshatras,
        "yoga": yogas,
        "karana": karanas,
        "muhurta": muhurtas,
        "ayanamsa": {
            "name": get_ayanamsa(ayanamsa).name,
            "key": ayanamsa,
            "degrees": round(ayan, 6),
            "dms": dms(ayan),
        },
        "summary": {
            "vara": VARA_NAMES[vara_index],
            "paksha": tithis[0]["paksha"] if tithis else None,
            "tithi": tithis[0]["name"] if tithis else None,
            "nakshatra": nakshatras[0]["name"] if nakshatras else None,
            "yoga": yogas[0]["name"] if yogas else None,
            "karana": karanas[0]["name"] if karanas else None,
            "moon_sign": SIGNS[int(moon_lon // 30)],
        },
        "notes": notes,
    }


def panchang_at(
    moment: dt.datetime,
    latitude: float,
    longitude: float,
    timezone: str,
    *,
    elevation: float = 0.0,
    **kwargs,
) -> dict:
    """The almanac for the vedic day *containing* `moment`.

    Between midnight and sunrise this returns the previous civil date's
    panchang, which is the whole point: at 03:00 on a Friday the vara is still
    Thursday and Rahu Kaal is still Thursday's.
    """
    _ephemeris()
    tz = ZoneInfo(timezone)
    local = moment.astimezone(tz) if moment.tzinfo else moment.replace(tzinfo=tz)
    date = local.date()

    geopos = (float(longitude), float(latitude), float(elevation))
    midnight = dt.datetime(date.year, date.month, date.day, tzinfo=tz)
    sunrise = _rise_or_set(_to_jd(midnight), swe.SUN, geopos, True, 1.5)
    if sunrise is not None and _to_jd(local) < sunrise:
        date -= dt.timedelta(days=1)
    return daily_panchang(date, latitude, longitude, timezone,
                          elevation=elevation, **kwargs)


def _tithi_entry(index: int, start: float, end: float, tz: ZoneInfo) -> dict:
    name, paksha, number = _tithi_label(index)
    entry = _named_entry(name, index, start, end, tz)
    entry["paksha"] = paksha
    entry["number"] = number                          # 1..15 within the paksha
    entry["label"] = f"{paksha} {name}"
    return entry


def _nakshatra_entry(index: int, start: float, end: float, tz: ZoneInfo,
                     moon_at, reference: float) -> dict:
    entry = _named_entry(NAKSHATRAS[index], index, start, end, tz)
    span = 360.0 / 27.0
    into = (moon_at(reference) - index * span) % 360.0
    pada = min(4, int(into / (span / 4.0)) + 1)
    entry["pada"] = pada
    entry["pada_ends"] = _iso(_from_jd(
        _advance(moon_at, reference, pada * (span / 4.0) - into), tz))
    entry["lord"] = _NAKSHATRA_LORDS[index % 9]
    return entry


def _named_entry(name: str, index: int, start: float, end: float, tz: ZoneInfo) -> dict:
    start_local, end_local = _from_jd(start, tz), _from_jd(end, tz)
    return {
        "index": index,                               # 0-based, engine-facing
        "name": name,
        "starts": _iso(start_local),
        "ends": _iso(end_local),
        "ends_next_day": end_local.date() > start_local.date(),
        "duration_minutes": round((end - start) * 1440.0, 1),
    }


# Vimshottari lords repeat every nine nakshatras; kept here so a nakshatra entry
# can name its lord without dragging in the dasha machinery.
_NAKSHATRA_LORDS = ["Ketu", "Venus", "Sun", "Moon", "Mars",
                    "Rahu", "Jupiter", "Saturn", "Mercury"]


def _day_windows(sunrise: float, sunset: float, vara: int, tz: ZoneInfo) -> dict:
    """Rahu Kaal, Yamaganda, Gulika Kaal and Abhijit for one daylight span."""
    eighth = (sunset - sunrise) / 8.0

    def part(index: int) -> dict:
        start, end = sunrise + index * eighth, sunrise + (index + 1) * eighth
        return {
            "segment": index + 1,                     # 1..8, as almanacs print it
            "start": _iso(_from_jd(start, tz)),
            "end": _iso(_from_jd(end, tz)),
            "duration_minutes": round(eighth * 1440.0, 1),
        }

    fifteenth = (sunset - sunrise) / 15.0
    abhijit = None
    if vara != ABHIJIT_EXCLUDED_VARA:
        start = sunrise + (ABHIJIT_MUHURTA - 1) * fifteenth
        abhijit = {
            "muhurta": ABHIJIT_MUHURTA,
            "start": _iso(_from_jd(start, tz)),
            "end": _iso(_from_jd(start + fifteenth, tz)),
            "duration_minutes": round(fifteenth * 1440.0, 1),
        }

    return {
        "rahu_kaal": part(RAHU_SEGMENT[vara]),
        "yamaganda": part(YAMAGANDA_SEGMENT[vara]),
        "gulika_kaal": part(GULIKA_SEGMENT[vara]),
        "abhijit": abhijit,
    }


# --------------------------------------------------------------------------
# Reading a chart the rest of the app already built
# --------------------------------------------------------------------------

CLASSICAL_SEVEN = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]


def _chart_view(chart, ayanamsa: str | None = None) -> dict:
    """Sidereal longitudes, houses and metadata out of a chart_service bundle.

    Accepts a ``ChartSession`` or the normalised bundle dict it carries. Vedic
    rules are sidereal rules, so a tropical chart is shifted by the ayanamsa
    here rather than being quietly judged in the wrong zodiac.
    """
    bundle = getattr(chart, "bundle", chart)
    meta = bundle["meta"]
    jd = meta["julian_day"]
    key = ayanamsa or meta.get("ayanamsa") or DEFAULT_AYANAMSA
    _ephemeris()
    ayan = _ayanamsa_at(jd, key)
    # A sidereal bundle already carries sidereal longitudes; a tropical one has
    # to be shifted, cusps included, or the house numbers would not match. That
    # shift is the scalar approximation rather than a reframing, which is worth
    # about a thousandth of a degree — irrelevant to a sign-level rule like
    # Kaal Sarp, and the alternative would be recomputing the whole chart.
    shift = 0.0 if meta.get("zodiac") == "sidereal" else ayan

    longitudes = {
        name: norm360(obj["longitude"] - shift)
        for name, obj in bundle["objects"].items()
    }
    cusps = [norm360(c - shift) for c in bundle["houses"]["cusps"]]

    # Vedic practice reckons Rahu from the *mean* node; stellium's bundle only
    # carries the true node, so the mean one is taken straight from the
    # ephemeris at the same instant.
    rahu = _sidereal(jd, swe.MEAN_NODE, key)

    return {
        "julian_day": jd,
        "ayanamsa": key,
        "ayanamsa_value": ayan,
        "longitudes": longitudes,
        "cusps": cusps,
        "rahu_mean": rahu,
        "rahu_true": longitudes.get("True Node"),
        "timezone": meta.get("timezone") or "UTC",
        "time_known": bundle.get("birth", {}).get("time_known", True),
    }


# --------------------------------------------------------------------------
# Sade Sati
# --------------------------------------------------------------------------

# Saturn's slowest daily motion is about 0.13°, so a two-day scan step can never
# skip a whole sign — but it *can* miss a retrograde dip back across a cusp that
# lasts under two days. Such a dip is under 0.03° deep and is not something any
# almanac reports, so the trade is deliberate.
_SATURN_STEP_DAYS = 2.0

# Saturn's retrograde loop spans about seven degrees and four and a half months.
# Two runs in the Sade Sati signs separated by less than this are the same
# Sade Sati with a retrograde break in the middle, not two Sade Satis.
_RETROGRADE_GAP_DAYS = 170.0

SADE_SATI_PHASES = {
    12: (1, "Rising",
         "Saturn in the 12th from the Moon — traditionally read as loss, "
         "expense and disturbed sleep."),
    1: (2, "Peak",
        "Saturn over the natal Moon — traditionally read as the heaviest of "
        "the three, touching health and state of mind."),
    2: (3, "Setting",
        "Saturn in the 2nd from the Moon — traditionally read as family, "
        "speech and money."),
}

# 4th and 8th from the Moon: two and a half years apiece, hence 'Dhaiya'. Names
# are not settled — 'Kantaka Shani' is applied by some authors to the 4th alone
# and by others to every kendra from the Moon, and the 8th is separately called
# 'Ashtama Shani'. We label the two houses distinctly and leave the umbrella
# term as 'Dhaiya', which is what Indian users search for.
DHAIYA_HOUSES = {4: "Kantaka Shani (4th from Moon)", 8: "Ashtama Shani (8th from Moon)"}


def _saturn_runs(jd_from: float, jd_to: float, ayanamsa: str) -> list[dict]:
    """Contiguous stretches during which Saturn sits in one sidereal sign.

    Retrograde re-entries produce separate runs on purpose — a Sade Sati that
    breaks and resumes is a real thing that people notice, and flattening it
    would hide it.
    """
    def sign_at(jd: float) -> int:
        return int(_sidereal(jd, swe.SATURN, ayanamsa) // 30)

    def boundary(lo: float, hi: float, before: int) -> float:
        while hi - lo > _TOLERANCE_DAYS:
            mid = (lo + hi) / 2.0
            if sign_at(mid) == before:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2.0

    runs: list[dict] = []
    jd = jd_from
    current = sign_at(jd)
    start: float | None = None                        # None = began before the window
    while jd < jd_to:
        nxt = min(jd + _SATURN_STEP_DAYS, jd_to)
        found = sign_at(nxt)
        if found != current:
            edge = boundary(jd, nxt, current)
            runs.append({"sign": current, "start": start, "end": edge})
            current, start = found, edge
        jd = nxt
    runs.append({"sign": current, "start": start, "end": None})
    return runs


def sade_sati_for_moon_sign(
    moon_sign: int | str,
    as_of: dt.datetime | dt.date | None = None,
    *,
    ayanamsa: str = DEFAULT_AYANAMSA,
    timezone: str = "UTC",
    window_years: float = 30.0,
) -> dict:
    """Sade Sati and Dhaiya for a natal Moon sign, without needing a chart."""
    _ephemeris()
    tz = ZoneInfo(timezone)
    moon_index = SIGNS.index(moon_sign) if isinstance(moon_sign, str) else int(moon_sign) % 12

    if as_of is None:
        now = dt.datetime.now(tz)
    elif isinstance(as_of, dt.datetime):
        now = as_of.astimezone(tz) if as_of.tzinfo else as_of.replace(tzinfo=tz)
    else:
        now = dt.datetime(as_of.year, as_of.month, as_of.day, tzinfo=tz)
    jd_now = _to_jd(now)

    half = window_years * 365.25
    runs = _saturn_runs(jd_now - half, jd_now + half, ayanamsa)

    sade_signs = {(moon_index + 11) % 12: 12, moon_index: 1, (moon_index + 1) % 12: 2}
    dhaiya_signs = {(moon_index + 3) % 12: 4, (moon_index + 7) % 12: 8}

    periods = _group(runs, sade_signs, jd_now, tz, SADE_SATI_PHASES)
    dhaiya = _group(runs, dhaiya_signs, jd_now, tz, None)

    current = next((p for p in periods if p["status"] == "current"), None)
    phase = None
    if current:
        phase = next((p for p in current["phases"] if p["status"] == "current"), None)

    saturn_lon = _sidereal(jd_now, swe.SATURN, ayanamsa)
    saturn_speed = swe.calc_ut(jd_now, swe.SATURN, swe.FLG_SWIEPH | swe.FLG_SPEED)[0][3]
    saturn_sign = int(saturn_lon // 30)

    current_dhaiya = next((d for d in dhaiya if d["status"] == "current"), None)

    return {
        "as_of": _iso(now),
        "timezone": timezone,
        "moon_sign": SIGNS[moon_index],
        "moon_sign_index": moon_index,
        "saturn": {
            "longitude": round(saturn_lon, 4),
            "sign": SIGNS[saturn_sign],
            "position": f"{SIGNS[saturn_sign]} {dms(saturn_lon % 30)}",
            "retrograde": saturn_speed < 0,
            "house_from_moon": (saturn_sign - moon_index) % 12 + 1,
        },
        "running": current is not None,
        "phase": phase,
        "current_period": current,
        "periods": periods,
        "dhaiya": {
            "running": current_dhaiya is not None,
            "current": current_dhaiya,
            "periods": dhaiya,
        },
        "ayanamsa": {"key": ayanamsa, "name": get_ayanamsa(ayanamsa).name,
                     "degrees": round(_ayanamsa_at(jd_now, ayanamsa), 6)},
        "window": {
            "from": _iso(_from_jd(jd_now - half, tz)),
            "to": _iso(_from_jd(jd_now + half, tz)),
            "years": window_years,
        },
        "notes": [
            "Sade Sati is judged from the natal Moon sign, not the Sun sign or the "
            "ascendant, and it is a sign-ingress rule: it starts the instant Saturn "
            "enters the 12th from the Moon, whatever degree the Moon holds.",
            "A period broken by a retrograde re-entry is reported as one period with "
            "the gap visible in its phases.",
        ],
    }


def sade_sati(
    chart,
    as_of: dt.datetime | dt.date | None = None,
    *,
    ayanamsa: str | None = None,
    window_years: float = 30.0,
) -> dict:
    """Sade Sati and Dhaiya for a natal chart built by ``chart_service``."""
    view = _chart_view(chart, ayanamsa)
    moon = view["longitudes"]["Moon"]
    return sade_sati_for_moon_sign(
        int(moon // 30),
        as_of,
        ayanamsa=view["ayanamsa"],
        timezone=view["timezone"],
        window_years=window_years,
    )


def _group(runs: list[dict], wanted: dict[int, int], jd_now: float,
           tz: ZoneInfo, phase_table: dict | None) -> list[dict]:
    """Turn sign runs into merged periods, each carrying its phases."""
    hits = [r for r in runs if r["sign"] in wanted]
    if not hits:
        return []

    clusters: list[list[dict]] = [[hits[0]]]
    for run in hits[1:]:
        previous = clusters[-1][-1]
        gap = (run["start"] or jd_now) - (previous["end"] or jd_now)
        # Adjacent signs run back to back (gap 0); a gap only appears when
        # Saturn stepped out and came back, which is the retrograde case.
        if gap <= _RETROGRADE_GAP_DAYS:
            clusters[-1].append(run)
        else:
            clusters.append([run])

    out = []
    for cluster in clusters:
        start, end = cluster[0]["start"], cluster[-1]["end"]
        phases = []
        for run in cluster:
            house = wanted[run["sign"]]
            number, label, gloss = (
                phase_table[house] if phase_table else (house, DHAIYA_HOUSES[house], "")
            )
            phases.append({
                "phase": number,
                "name": label,
                "house_from_moon": house,
                "sign": SIGNS[run["sign"]],
                "start": _iso(_from_jd(run["start"], tz)) if run["start"] else None,
                "end": _iso(_from_jd(run["end"], tz)) if run["end"] else None,
                "status": _status(run["start"], run["end"], jd_now),
                "note": gloss,
            })
        out.append({
            "start": _iso(_from_jd(start, tz)) if start else None,
            "end": _iso(_from_jd(end, tz)) if end else None,
            "start_truncated": start is None,          # began before the window
            "end_truncated": end is None,
            "status": _status(start, end, jd_now),
            "years": round(((end or jd_now) - (start or jd_now)) / 365.25, 2)
            if (start and end) else None,
            "phases": phases,
        })
    return out


def _status(start: float | None, end: float | None, jd_now: float) -> str:
    if end is not None and end <= jd_now:
        return "past"
    if start is not None and start > jd_now:
        return "future"
    return "current"


# --------------------------------------------------------------------------
# Kaal Sarp Dosha
# --------------------------------------------------------------------------

# Worth saying plainly: Kaal Sarp is *not* a classical yoga. It appears in no
# surviving section of Parashara, Varahamihira or Jaimini, and its earliest
# printed descriptions are twentieth-century. Plenty of traditional astrologers
# regard it as a modern invention amplified by the remedial trade, and the
# twelve serpent names below are a modern taxonomy with no textual pedigree.
# We compute it because Indian users expect to see it, and we report exactly
# what the geometry is so the reader can judge it themselves.

KAAL_SARP_TYPES = [
    "Anant", "Kulik", "Vasuki", "Shankhpal", "Padma", "Mahapadma",
    "Takshak", "Karkotak", "Shankhachud", "Ghatak", "Vishdhar", "Sheshnag",
]

# A planet sitting this close to a node is treated as being *on* the axis
# rather than inside it, which by the common rule makes the yoga partial
# (Aanshik) rather than complete.
KAAL_SARP_ORB = 1.0


def kaal_sarp(chart, *, node: str = "mean", orb: float = KAAL_SARP_ORB) -> dict:
    """Whether the seven classical planets are hemmed inside the nodal axis."""
    view = _chart_view(chart)
    rahu = view["rahu_true"] if node == "true" else view["rahu_mean"]
    if rahu is None:
        rahu = view["rahu_mean"]
    return kaal_sarp_from_longitudes(
        view["longitudes"], rahu,
        cusps=view["cusps"] if view["time_known"] else None,
        node=node, orb=orb,
    )


def kaal_sarp_from_longitudes(
    longitudes: dict[str, float],
    rahu: float,
    *,
    cusps: list[float] | None = None,
    node: str = "mean",
    orb: float = KAAL_SARP_ORB,
) -> dict:
    """The geometry alone, for callers that already hold sidereal longitudes.

    Every planet's forward arc from Rahu is measured. If all seven fall in the
    semicircle ahead of Rahu the planets are being 'swallowed' in the
    direction the nodes travel; if all seven fall behind, the same hemming
    exists in mirror image. Both are reported as forming, distinguished by
    ``direction``, because sources split on whether the reversed case is a
    separate Kaal Amrit yoga or simply the same one.
    """
    rahu = norm360(rahu)
    ketu = norm360(rahu + 180.0)

    planets = []
    ahead = behind = 0
    on_axis = []
    for name in CLASSICAL_SEVEN:
        lon = longitudes.get(name)
        if lon is None:
            continue
        arc = norm360(lon - rahu)
        gap_rahu = min(arc, 360.0 - arc)
        gap_ketu = abs(arc - 180.0)
        conjunct = None
        if gap_rahu <= orb:
            conjunct = "Rahu"
        elif gap_ketu <= orb:
            conjunct = "Ketu"
        if conjunct:
            on_axis.append({"planet": name, "node": conjunct,
                            "orb": round(min(gap_rahu, gap_ketu), 3)})
        if arc < 180.0:
            ahead += 1
        elif arc > 180.0:
            behind += 1
        planets.append({
            "name": name,
            "longitude": round(lon, 4),
            "sign": SIGNS[int(lon // 30)],
            "house": house_of(lon, cusps) if cusps else None,
            "arc_from_rahu": round(arc, 3),
            "side": "ahead" if arc < 180.0 else "behind" if arc > 180.0 else "on axis",
        })

    counted = ahead + behind
    forms = counted > 0 and (ahead == 0 or behind == 0)
    direction = None
    if forms:
        direction = "anuloma" if behind == 0 else "vilom"

    rahu_house = house_of(rahu, cusps) if cusps else None
    type_block = None
    if forms and rahu_house:
        type_block = {
            "number": rahu_house,
            "name": KAAL_SARP_TYPES[rahu_house - 1],
            "rahu_house": rahu_house,
        }

    # When it does not form, name the planets that break it — the minority side
    # is the one that spilled out of the axis.
    minority = "behind" if behind <= ahead else "ahead"
    outside = [] if forms else [p["name"] for p in planets if p["side"] == minority]

    notes = [
        "Kaal Sarp Dosha is a modern addition to the Vedic corpus — it is absent "
        "from Parashara and Varahamihira, and many traditional astrologers dispute "
        "it entirely. Treat the result as a geometric fact, not a verdict.",
        f"Computed against the {node} lunar node, which is the Vedic default.",
    ]
    if not cusps:
        notes.append(
            "No usable house cusps, so the twelve named types are not assigned — "
            "they depend on the house Rahu occupies, which needs a known birth time."
        )
    if on_axis:
        notes.append(
            "A planet sits on the nodal axis itself, so the hemming is not complete; "
            "this is what the popular literature calls a partial (Aanshik) Kaal Sarp."
        )

    return {
        "forms": forms,
        "partial": bool(forms and on_axis),
        "direction": direction,
        "type": type_block,
        "rahu": {"longitude": round(rahu, 4), "sign": SIGNS[int(rahu // 30)],
                 "house": rahu_house, "node": node},
        "ketu": {"longitude": round(ketu, 4), "sign": SIGNS[int(ketu // 30)],
                 "house": house_of(ketu, cusps) if cusps else None},
        "planets": planets,
        "ahead_of_rahu": ahead,
        "behind_rahu": behind,
        "breaking": outside,
        "conjunct_axis": on_axis,
        "notes": notes,
    }
