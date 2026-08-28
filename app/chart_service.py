"""Chart construction and normalisation on top of the `stellium` library.

Every astronomical number in this app comes from stellium (which wraps the
Swiss Ephemeris). This module's job is only to:

  * feed stellium unambiguous, timezone-aware birth data,
  * turn its rich objects into plain dicts the UI and the interpreter can use,
  * add the derived layers stellium does not ship (transit-to-natal aspects
    with transit-appropriate orbs, and Vimshottari dasha for sidereal charts).
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from zoneinfo import ZoneInfo

from stellium import ChartBuilder, ReturnBuilder
from stellium.components import ArabicPartsCalculator, DignityComponent
from stellium.engines import (
    AspectPatternAnalyzer,
    PlacidusHouses,
    PorphyryHouses,
    WholeSignHouses,
    ZodiacalReleasingAnalyzer,
)

# --------------------------------------------------------------------------
# Reference tables
# --------------------------------------------------------------------------

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

DOMICILE = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn",
    "Pisces": "Jupiter",
}
MODERN_RULER = {"Scorpio": "Pluto", "Aquarius": "Uranus", "Pisces": "Neptune"}

ELEMENT = {
    "Aries": "Fire", "Leo": "Fire", "Sagittarius": "Fire",
    "Taurus": "Earth", "Virgo": "Earth", "Capricorn": "Earth",
    "Gemini": "Air", "Libra": "Air", "Aquarius": "Air",
    "Cancer": "Water", "Scorpio": "Water", "Pisces": "Water",
}
MODALITY = {
    "Aries": "Cardinal", "Cancer": "Cardinal", "Libra": "Cardinal", "Capricorn": "Cardinal",
    "Taurus": "Fixed", "Leo": "Fixed", "Scorpio": "Fixed", "Aquarius": "Fixed",
    "Gemini": "Mutable", "Virgo": "Mutable", "Sagittarius": "Mutable", "Pisces": "Mutable",
}

CLASSICAL = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
MODERN = ["Uranus", "Neptune", "Pluto"]
ALL_PLANETS = CLASSICAL + MODERN

BENEFICS = {"Venus", "Jupiter"}
MALEFICS = {"Mars", "Saturn"}

ANGULAR, SUCCEDENT, CADENT = {1, 4, 7, 10}, {2, 5, 8, 11}, {3, 6, 9, 12}

# Transits are judged on tighter orbs than natal aspects — a 6° natal square is
# a real feature of the psyche, but a 6° transiting square is not yet an event.
TRANSIT_ORBS = {
    "Moon": 3.0, "Sun": 1.5, "Mercury": 1.5, "Venus": 1.5, "Mars": 1.5,
    "Jupiter": 2.0, "Saturn": 2.0, "Chiron": 1.5,
    "Uranus": 2.0, "Neptune": 2.0, "Pluto": 2.0,
}
TRANSIT_ASPECTS = [
    ("Conjunction", 0.0), ("Sextile", 60.0), ("Square", 90.0),
    ("Trine", 120.0), ("Opposition", 180.0),
]

# Vimshottari dasha — lord order and period length in years (total 120).
VIMSHOTTARI = [
    ("Ketu", 7), ("Venus", 20), ("Sun", 6), ("Moon", 10), ("Mars", 7),
    ("Rahu", 18), ("Jupiter", 16), ("Saturn", 19), ("Mercury", 17),
]
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta",
    "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]
SIDEREAL_YEAR = 365.25


# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------

def dms(degrees: float) -> str:
    """23.4567 -> '23°27′'."""
    d = int(degrees)
    m = int(round((degrees - d) * 60))
    if m == 60:
        d, m = d + 1, 0
    return f"{d}°{m:02d}′"


def sign_of(longitude: float) -> str:
    return SIGNS[int(longitude // 30) % 12]


def norm360(x: float) -> float:
    return x % 360.0


def angular_sep(a: float, b: float) -> float:
    """Shortest separation between two ecliptic longitudes, 0..180."""
    d = abs(norm360(a - b))
    return 360.0 - d if d > 180.0 else d


def house_of(longitude: float, cusps: list[float]) -> int:
    """Which house a longitude falls in, given 12 cusp longitudes."""
    lon = norm360(longitude)
    for i in range(12):
        start = norm360(cusps[i])
        end = norm360(cusps[(i + 1) % 12])
        span = norm360(end - start)
        if norm360(lon - start) < span:
            return i + 1
    return 1


def placement(house: int) -> str:
    if house in ANGULAR:
        return "angular"
    return "succedent" if house in SUCCEDENT else "cadent"


# --------------------------------------------------------------------------
# Birth data
# --------------------------------------------------------------------------

@dataclass
class BirthData:
    name: str
    date: str                 # YYYY-MM-DD
    time: str                 # HH:MM (24h)
    latitude: float
    longitude: float
    timezone: str
    place: str
    # Vedic by default. This app sells kundali readings to an Indian audience;
    # a tropical chart puts most planets a whole sign away from what any
    # astrologer or Indian astrology site would read, and moves the Moon's
    # nakshatra, which is what the entire Vimshottari dasha timeline is built
    # on. Western remains selectable, but it must be an explicit choice.
    zodiac: str = "sidereal"          # 'sidereal' | 'tropical'
    ayanamsa: str = "lahiri"
    house_system: str = "Whole Sign"  # 'Whole Sign' | 'Placidus'
    time_known: bool = True

    @property
    def local_datetime(self) -> dt.datetime:
        naive = dt.datetime.strptime(f"{self.date} {self.time}", "%Y-%m-%d %H:%M")
        return naive.replace(tzinfo=ZoneInfo(self.timezone))

    def to_dict(self) -> dict:
        return {
            "name": self.name, "date": self.date, "time": self.time,
            "latitude": self.latitude, "longitude": self.longitude,
            "timezone": self.timezone, "place": self.place,
            "zodiac": self.zodiac, "ayanamsa": self.ayanamsa,
            "house_system": self.house_system, "time_known": self.time_known,
        }


# --------------------------------------------------------------------------
# Chart session
# --------------------------------------------------------------------------

@dataclass
class ChartSession:
    birth: BirthData
    chart: object                      # stellium CalculatedChart
    bundle: dict = field(default_factory=dict)
    comparison_system: str = "Whole Sign"
    house_note: str = ""

    # -- convenience accessors used heavily by the interpreter --------------

    def obj(self, name: str) -> dict | None:
        return self.bundle["objects"].get(name)

    def house_ruler(self, house: int) -> str:
        """Traditional domicile ruler of the sign on the given house cusp."""
        return DOMICILE[self.bundle["houses"]["signs"][house - 1]]

    def house_sign(self, house: int) -> str:
        return self.bundle["houses"]["signs"][house - 1]

    def planets_in_house(self, house: int) -> list[dict]:
        return [
            o for o in self.bundle["objects"].values()
            if o["kind"] == "planet" and o["house"] == house
        ]

    def aspects_to(self, name: str) -> list[dict]:
        return [a for a in self.bundle["aspects"] if name in (a["a"], a["b"])]


def _cusps(chart, system: str) -> list[float]:
    return list(chart.get_houses(system).cusps)


# Placidus (and Koch) are undefined above the polar circle: the ecliptic
# degree that should hold a cusp never crosses the required house circle.
POLAR_LIMIT = 66.0


def _house_engines(birth: BirthData) -> tuple[list, str, str, str]:
    """Pick house systems that are actually defined at this latitude.

    Returns (engines, chosen_system, comparison_system, note).
    """
    if abs(birth.latitude) < POLAR_LIMIT:
        engines = [PlacidusHouses(), WholeSignHouses()]
        chosen = birth.house_system if birth.house_system in ("Placidus", "Whole Sign") else "Placidus"
        other = "Whole Sign" if chosen == "Placidus" else "Placidus"
        return engines, chosen, other, ""

    engines = [WholeSignHouses(), PorphyryHouses()]
    note = (
        f"Born at {abs(birth.latitude):.1f}° latitude, inside the polar circle, where Placidus "
        f"house cusps are mathematically undefined. Whole Sign houses are used instead "
        f"(Porphyry is also computed for comparison)."
    )
    chosen = "Whole Sign" if birth.house_system != "Porphyry" else "Porphyry"
    other = "Porphyry" if chosen == "Whole Sign" else "Whole Sign"
    return engines, chosen, other, note


def build(birth: BirthData) -> ChartSession:
    """Compute a fully-loaded natal chart."""
    engines, chosen, other, note = _house_engines(birth)
    birth.house_system = chosen

    builder = (
        ChartBuilder.from_details(
            birth.local_datetime,
            {"latitude": birth.latitude, "longitude": birth.longitude, "name": birth.place},
            name=birth.name or "Native",
        )
        .with_aspects()
        .with_orbs()
        .with_house_systems(engines)
        .add_component(DignityComponent())
        .add_component(ArabicPartsCalculator())
        .add_analyzer(AspectPatternAnalyzer())
        .add_analyzer(ZodiacalReleasingAnalyzer(lots=["Part of Fortune", "Part of Spirit"]))
    )
    if birth.zodiac == "sidereal":
        builder = builder.with_sidereal(birth.ayanamsa)
    else:
        builder = builder.with_tropical()

    chart = builder.calculate()
    session = ChartSession(birth=birth, chart=chart, comparison_system=other, house_note=note)
    session.bundle = _normalise(session)
    return session


def _normalise(session: ChartSession) -> dict:
    chart, birth = session.chart, session.birth
    system = birth.house_system
    cusps = _cusps(chart, system)
    other_system = session.comparison_system

    sun = chart.get_object("Sun")
    sect = chart.sect  # 'day' | 'night'

    objects: dict[str, dict] = {}
    positions = list(chart.get_planets()) + list(chart.get_nodes()) + \
        list(chart.get_points()) + list(chart.get_angles())
    chiron = chart.get_object("Chiron")
    if chiron is not None:
        positions.append(chiron)
    parts = chart.get_component_result("Arabic Parts") or []

    for pos in list(positions) + list(parts):
        name = pos.name
        if name in objects or name == "RAMC":
            continue
        kind = (
            "planet" if name in ALL_PLANETS else
            "angle" if name in ("ASC", "MC", "DSC", "IC") else
            "node" if "Node" in name else
            "part" if name.startswith("Part of") else "point"
        )
        house = house_of(pos.longitude, cusps)
        entry = {
            "name": name,
            "kind": kind,
            "longitude": round(pos.longitude, 6),
            "sign": pos.sign,
            "degree": round(pos.sign_degree, 4),
            "dms": dms(pos.sign_degree),
            "position": f"{pos.sign} {dms(pos.sign_degree)}",
            "house": house,
            "house_other": house_of(pos.longitude, _cusps(chart, other_system)),
            "placement": placement(house),
            "retrograde": bool(pos.is_retrograde),
            "speed": round(pos.speed_longitude or 0.0, 5),
            "declination": round(pos.declination, 3) if pos.declination is not None else None,
            "out_of_bounds": bool(getattr(pos, "is_out_of_bounds", False)),
            "element": ELEMENT.get(pos.sign),
            "modality": MODALITY.get(pos.sign),
        }
        if kind == "planet":
            entry.update(_planet_condition(chart, pos, sun, sect))
        objects[name] = entry

    aspects = _natal_aspects(chart)
    for a in aspects:
        for side in ("a", "b"):
            if a[side] in objects:
                objects[a[side]].setdefault("aspect_count", 0)
                objects[a[side]]["aspect_count"] += 1

    return {
        "birth": birth.to_dict(),
        "meta": _meta(chart, birth, sect),
        "objects": objects,
        "houses": _houses(chart, system, cusps),
        "house_note": session.house_note,
        "aspects": aspects,
        "patterns": _patterns(chart),
        "distribution": _distribution(objects),
        "dignities": _dignity_table(chart),
        "receptions": [dict(r) for r in chart.get_mutual_receptions()],
        "sect": _sect_block(sect),
    }


def _meta(chart, birth: BirthData, sect: str) -> dict:
    d = chart.to_dict()
    return {
        "name": birth.name or "Native",
        "local_time": birth.local_datetime.strftime("%d %B %Y, %H:%M"),
        "utc_time": d["datetime"]["utc"],
        "julian_day": d["datetime"]["julian_date"],
        "place": birth.place,
        "latitude": birth.latitude,
        "longitude": birth.longitude,
        "timezone": birth.timezone,
        "utc_offset": birth.local_datetime.strftime("%z"),
        "zodiac": birth.zodiac,
        "ayanamsa": chart.ayanamsa,
        "ayanamsa_value": round(chart.ayanamsa_value, 4) if chart.ayanamsa_value else None,
        "house_system": birth.house_system,
        "sect": sect,
    }


def _houses(chart, system: str, cusps: list[float]) -> dict:
    hc = chart.get_houses(system)
    return {
        "system": system,
        "cusps": [round(c, 4) for c in cusps],
        "signs": list(hc.signs),
        "degrees": [round(x, 4) for x in hc.sign_degrees],
        "labels": [f"{s} {dms(d)}" for s, d in zip(hc.signs, hc.sign_degrees)],
        "rulers": [DOMICILE[s] for s in hc.signs],
    }


def _planet_condition(chart, pos, sun, sect: str) -> dict:
    """Essential/accidental condition — the traditional 'is this planet able to act'."""
    name = pos.name
    dignity = chart.get_planet_dignity(name) or {}
    total = chart.get_planet_total_score(name) or {}

    elongation = angular_sep(pos.longitude, sun.longitude) if name != "Sun" else 0.0
    if name in ("Sun",):
        solar = "n/a"
    elif elongation < 0.283:            # within 17 arc-minutes
        solar = "cazimi"
    elif elongation < 8.5:
        solar = "combust"
    elif elongation < 15.0:
        solar = "under the beams"
    else:
        solar = "free"

    if name == "Sun":
        sect_status = "sect light" if sect == "day" else "contrary to sect"
    elif name == "Moon":
        sect_status = "sect light" if sect == "night" else "contrary to sect"
    elif name in ("Jupiter", "Saturn"):
        sect_status = "of the sect" if sect == "day" else "contrary to sect"
    elif name in ("Venus", "Mars"):
        sect_status = "of the sect" if sect == "night" else "contrary to sect"
    else:
        sect_status = "neutral"

    return {
        "dignities": dignity.get("dignities", []),
        "dignity_score": dignity.get("score", 0),
        "peregrine": bool(dignity.get("is_peregrine")),
        "dignity_note": dignity.get("interpretation", ""),
        "essential_score": total.get("essential_score", 0),
        "accidental_score": total.get("accidental_score", 0),
        "total_score": total.get("total_score", 0),
        "condition": total.get("interpretation", ""),
        "solar_phase": solar,
        "elongation": round(elongation, 2),
        "sect_status": sect_status,
        "benefic": name in BENEFICS,
        "malefic": name in MALEFICS,
        "rules": [s for s, r in DOMICILE.items() if r == name],
    }


def _natal_aspects(chart) -> list[dict]:
    out = []
    for a in chart.aspects:
        out.append({
            "a": a.object1.name,
            "b": a.object2.name,
            "type": a.aspect_name,
            "angle": a.aspect_degree,
            "orb": round(a.orb, 3),
            "applying": bool(a.is_applying),
            "nature": _aspect_nature(a.aspect_name),
            "strength": _aspect_strength(a.aspect_name, a.orb),
            "text": f"{a.object1.name} {a.aspect_name.lower()} {a.object2.name} "
                    f"({dms(a.orb)} orb, {'applying' if a.is_applying else 'separating'})",
        })
    out.sort(key=lambda x: (-x["strength"], x["orb"]))
    return out


def _aspect_nature(name: str) -> str:
    n = name.lower()
    if n in ("trine", "sextile"):
        return "harmonious"
    if n in ("square", "opposition"):
        return "hard"
    if n == "conjunction":
        return "fusing"
    return "minor"


def _aspect_strength(name: str, orb: float) -> float:
    base = {"conjunction": 1.0, "opposition": 0.9, "square": 0.85,
            "trine": 0.8, "sextile": 0.55}.get(name.lower(), 0.3)
    return round(base * max(0.15, 1.0 - orb / 10.0), 3)


def _patterns(chart) -> list[dict]:
    try:
        raw = chart.get_component_result("Aspect Patterns") or []
    except KeyError:
        return []
    return [
        {"name": p.name, "planets": [x.name for x in p.planets]}
        for p in raw
    ]


def _distribution(objects: dict) -> dict:
    elements = {"Fire": 0, "Earth": 0, "Air": 0, "Water": 0}
    modalities = {"Cardinal": 0, "Fixed": 0, "Mutable": 0}
    polarity = {"Yang": 0, "Yin": 0}
    houses = {p: 0 for p in ("angular", "succedent", "cadent")}
    counted = 0
    for o in objects.values():
        if o["kind"] != "planet":
            continue
        counted += 1
        elements[o["element"]] += 1
        modalities[o["modality"]] += 1
        polarity["Yang" if o["element"] in ("Fire", "Air") else "Yin"] += 1
        houses[o["placement"]] += 1
    dominant_el = max(elements, key=elements.get) if counted else None
    lacking = [k for k, v in elements.items() if v == 0]
    return {
        "elements": elements, "modalities": modalities, "polarity": polarity,
        "houses": houses, "dominant_element": dominant_el,
        "dominant_modality": max(modalities, key=modalities.get) if counted else None,
        "missing_elements": lacking,
    }


def _dignity_table(chart) -> dict:
    out = {}
    for p in CLASSICAL:
        d = chart.get_planet_dignity(p)
        if d:
            out[p] = {
                "dignities": d.get("dignities", []),
                "score": d.get("score", 0),
                "note": d.get("interpretation", ""),
            }
    return out


def _sect_block(sect: str) -> dict:
    day = sect == "day"
    return {
        "sect": sect,
        "light": "Sun" if day else "Moon",
        "benefic_of_sect": "Jupiter" if day else "Venus",
        "benefic_contrary": "Venus" if day else "Jupiter",
        "malefic_of_sect": "Saturn" if day else "Mars",
        "malefic_contrary": "Mars" if day else "Saturn",
    }


# --------------------------------------------------------------------------
# Transits
# --------------------------------------------------------------------------

def transit_chart(session: ChartSession, when: dt.datetime):
    """A chart of the sky at `when`, cast for the native's birthplace."""
    b = session.birth
    engines, _, _, _ = _house_engines(b)
    builder = ChartBuilder.from_details(
        when,
        {"latitude": b.latitude, "longitude": b.longitude, "name": b.place},
    ).with_house_systems(engines)
    builder = builder.with_sidereal(b.ayanamsa) if b.zodiac == "sidereal" else builder.with_tropical()
    return builder.calculate()


def transits(session: ChartSession, when: dt.datetime, movers: list[str] | None = None) -> list[dict]:
    """Transit-to-natal contacts, with transit-appropriate orbs.

    Computed here rather than via stellium's comparison aspects so the orbs are
    explicitly transit orbs and the applying/separating call uses the transiting
    body's own motion against a fixed natal point.
    """
    tchart = transit_chart(session, when)
    movers = movers or ALL_PLANETS
    natal_cusps = session.bundle["houses"]["cusps"]

    targets = [
        o for o in session.bundle["objects"].values()
        if o["kind"] in ("planet", "angle") or o["name"] in ("North Node", "True Node")
    ]

    hits: list[dict] = []
    for tname in movers:
        tp = tchart.get_object(tname)
        if tp is None:
            continue
        orb_limit = TRANSIT_ORBS.get(tname, 1.5)
        t_house = house_of(tp.longitude, natal_cusps)
        for target in targets:
            for aname, angle in TRANSIT_ASPECTS:
                sep = angular_sep(tp.longitude, target["longitude"])
                orb = abs(sep - angle)
                if orb > orb_limit:
                    continue
                # Applying if the gap to exactness is shrinking as the transiting
                # body moves; natal points are fixed, so only its speed matters.
                speed = tp.speed_longitude or 0.0
                future = angular_sep(
                    norm360(tp.longitude + speed * 0.5), target["longitude"]
                )
                applying = abs(future - angle) < orb
                hits.append({
                    "transit": tname,
                    "transit_position": f"{tp.sign} {dms(tp.sign_degree)}",
                    "transit_retrograde": bool(tp.is_retrograde),
                    "transit_house": t_house,
                    "aspect": aname,
                    "natal": target["name"],
                    "natal_position": target["position"],
                    "natal_house": target["house"],
                    "orb": round(orb, 2),
                    "applying": applying,
                    "nature": _aspect_nature(aname),
                    "weight": round(_transit_weight(tname, aname, orb, target["name"]), 3),
                    "text": (
                        f"transiting {tname}{' (Rx)' if tp.is_retrograde else ''} "
                        f"{aname.lower()} natal {target['name']} "
                        f"(orb {orb:.1f}°, {'applying' if applying else 'separating'})"
                    ),
                })
    hits.sort(key=lambda h: -h["weight"])
    return hits


_SLOW = {"Jupiter": 0.8, "Saturn": 1.0, "Uranus": 0.95, "Neptune": 0.9, "Pluto": 1.0, "Chiron": 0.6}


def _transit_weight(transiting: str, aspect: str, orb: float, natal: str) -> float:
    """Slow planets hitting personal points matter most; the Moon matters least."""
    mover = _SLOW.get(transiting, 0.35 if transiting == "Moon" else 0.5)
    asp = {"Conjunction": 1.0, "Opposition": 0.9, "Square": 0.9,
           "Trine": 0.7, "Sextile": 0.45}[aspect]
    target = 1.0 if natal in ("Sun", "Moon", "ASC", "MC") else 0.75
    tightness = max(0.2, 1.0 - orb / 3.0)
    return mover * asp * target * tightness


# --------------------------------------------------------------------------
# Time-lord systems
# --------------------------------------------------------------------------

def timing_snapshot(session: ChartSession, when: dt.datetime) -> dict:
    """Where the native currently sits in each time-lord system."""
    chart = session.chart
    birth_dt = session.birth.local_datetime
    if when.tzinfo is None:
        when = when.replace(tzinfo=ZoneInfo(session.birth.timezone))
    age_days = (when - birth_dt).total_seconds() / 86400.0
    age = age_days / 365.2425

    out: dict = {"date": when.strftime("%d %B %Y"), "age": round(age, 2)}

    try:
        annual, monthly = chart.profection(date=when.replace(tzinfo=None).isoformat())
        out["profection"] = {
            "house": annual.profected_house,
            "sign": annual.profected_sign,
            "lord_of_year": annual.ruler,
            "lord_house": annual.ruler_house,
            "lord_position": f"{annual.ruler_position.sign} {dms(annual.ruler_position.sign_degree)}",
            "monthly_house": monthly.profected_house,
            "monthly_sign": monthly.profected_sign,
            "monthly_lord": monthly.ruler,
        }
    except Exception as exc:  # pragma: no cover - defensive
        out["profection"] = {"error": str(exc)}

    try:
        zr = chart.zr_at_date(when.astimezone(dt.timezone.utc))
        out["zodiacal_releasing"] = {
            "lot": zr.lot,
            "l1": _zr_period(zr.l1),
            "l2": _zr_period(zr.l2),
            "l3": _zr_period(zr.l3),
            "is_peak": zr.is_peak,
            "is_loosing_bond": zr.is_lb,
        }
    except Exception:
        out["zodiacal_releasing"] = None

    try:
        fd = chart.firdaria()
        current = [p for p in fd.periods if p.start <= when.astimezone(dt.timezone.utc) <= p.end]
        majors = [p for p in current if p.level == 1]
        subs = [p for p in current if p.level == 2]
        if majors:
            out["firdaria"] = {
                "major": majors[0].ruler,
                "sub": subs[0].sub_ruler if subs and subs[0].sub_ruler else (subs[0].ruler if subs else None),
                "major_until": majors[0].end.strftime("%b %Y"),
            }
    except Exception:
        out["firdaria"] = None

    if session.birth.zodiac == "sidereal":
        out["vimshottari"] = vimshottari(session, when)

    return out


def _zr_period(p) -> dict | None:
    if p is None:
        return None
    return {
        "sign": p.sign, "ruler": p.ruler,
        "start": p.start.strftime("%b %Y"), "end": p.end.strftime("%b %Y"),
        "score": p.score, "is_peak": p.is_peak, "is_loosing_bond": p.is_loosing_bond,
    }


YOGINI_DASHA = [
    ("Mangala", 1, "Moon"),
    ("Pingala", 2, "Sun"),
    ("Dhanya", 3, "Jupiter"),
    ("Bhramari", 4, "Mars"),
    ("Bhadrika", 5, "Mercury"),
    ("Ulka", 6, "Saturn"),
    ("Siddha", 7, "Venus"),
    # Rahu rules the first half of Sankata's 8-year span and Ketu the
    # second, per the source's own statement rather than one lord throughout
    # — see yogini_dasha() and docs/sources/ravana_samhita_notes.md.
    ("Sankata", 8, "Rahu"),
]
YOGINI_CYCLE_YEARS = sum(years for _, years, _ in YOGINI_DASHA)   # 36


def _yogini_start_index(nakshatra_number: int) -> int:
    """Which of the 8 Yogini Dashas is running at birth, 1-based nakshatra
    number in.

    This source's own rule: add 3 to the birth nakshatra number and divide
    by 8; the remainder gives the starting Yogini (1=Mangala ... 8=Sankata,
    remainder 0 read as 8). Other traditions state the starting-point rule
    differently — this is the specific rule this source gives, not asserted
    as the one universal method.
    """
    raw = (nakshatra_number + 3) % 8
    return 7 if raw == 0 else raw - 1


def yogini_dasha(session: ChartSession, when: dt.datetime) -> dict:
    """Yogini Dasha: an alternate 8-fold dasha from the sidereal Moon.

    A modern compilation presented as "Ravana Samhita" (see docs/sources/
    ravana_samhita_notes.md) — a distinct tradition from the Vimshottari
    dasha above, not a competing claim about "the" dasha. Both run off the
    same birth Moon; a caller wanting this system asks for it by name, the
    same way it asks for Vimshottari.

    Shaped like vimshottari()'s return value on purpose (nakshatra,
    mahadasha, antardasha, upcoming) so callers can treat the two similarly,
    though the field names differ (`name` for the Yogini, `graha` for the
    planet held to rule it) since a Yogini dasha is not simply "a planet's
    dasha" the way Vimshottari's is.
    """
    moon = session.chart.get_object("Moon")
    lon = moon.longitude
    span = 360.0 / 27.0
    idx = int(lon // span) % 27
    frac = (lon % span) / span
    nakshatra_number = idx + 1

    start_index = _yogini_start_index(nakshatra_number)
    birth = session.birth.local_datetime
    if when.tzinfo is None:
        when = when.replace(tzinfo=ZoneInfo(session.birth.timezone))

    first_years = YOGINI_DASHA[start_index][1]
    cursor = birth - dt.timedelta(days=frac * first_years * SIDEREAL_YEAR)

    # Four full 36-year turns of the wheel (~144 years) comfortably outlasts
    # any lifetime, the same way vimshottari()'s ten majors outlast its
    # 120-year cycle.
    majors = []
    for i in range(8 * 4):
        name, years, graha = YOGINI_DASHA[(start_index + i) % 8]
        end = cursor + dt.timedelta(days=years * SIDEREAL_YEAR)
        majors.append({"name": name, "graha": graha, "start": cursor, "end": end, "years": years})
        cursor = end

    current = next((m for m in majors if m["start"] <= when < m["end"]), None)
    antar = None
    if current:
        sub_cursor = current["start"]
        start_idx = next(i for i, (n, _, _) in enumerate(YOGINI_DASHA) if n == current["name"])
        for j in range(8):
            sname, syears, sgraha = YOGINI_DASHA[(start_idx + j) % 8]
            length = current["years"] * syears / YOGINI_CYCLE_YEARS * SIDEREAL_YEAR
            sub_end = sub_cursor + dt.timedelta(days=length)
            if sub_cursor <= when < sub_end:
                antar = {"name": sname, "graha": sgraha, "start": sub_cursor, "end": sub_end}
                break
            sub_cursor = sub_end

    def graha_of(period: dict) -> str:
        # Sankata's own Rahu/Ketu split only applies at this, the mahadasha,
        # timescale — the source does not describe subdividing an
        # antardasha-length slice of Sankata the same way.
        if period["name"] != "Sankata":
            return period["graha"]
        midpoint = period["start"] + (period["end"] - period["start"]) / 2
        return "Rahu" if when < midpoint else "Ketu"

    def fmt(d: dt.datetime) -> str:
        return d.strftime("%b %Y")

    return {
        "nakshatra": NAKSHATRAS[idx],
        "mahadasha": {
            "name": current["name"], "graha": graha_of(current),
            "start": fmt(current["start"]), "end": fmt(current["end"]),
        } if current else None,
        "antardasha": {
            "name": antar["name"],
            "graha": "Rahu/Ketu" if antar["name"] == "Sankata" else antar["graha"],
            "start": fmt(antar["start"]), "end": fmt(antar["end"]),
        } if antar else None,
        "upcoming": [
            {"name": m["name"], "graha": graha_of(m), "start": fmt(m["start"]), "end": fmt(m["end"])}
            for m in majors if m["start"] > when
        ][:3],
    }


def vimshottari(session: ChartSession, when: dt.datetime) -> dict:
    """Vimshottari dasha from the sidereal Moon.

    stellium supplies the sidereal Moon longitude (Swiss Ephemeris + the chosen
    ayanamsa); the period arithmetic below is the standard 120-year cycle.
    """
    moon = session.chart.get_object("Moon")
    lon = moon.longitude
    span = 360.0 / 27.0                       # 13°20' per nakshatra
    idx = int(lon // span) % 27
    frac = (lon % span) / span                # how far through the nakshatra
    pada = int(frac * 4) + 1

    start_lord = idx % 9
    birth = session.birth.local_datetime
    if when.tzinfo is None:
        when = when.replace(tzinfo=ZoneInfo(session.birth.timezone))

    # First mahadasha is the remaining fraction of the birth-nakshatra lord.
    cursor = birth - dt.timedelta(days=frac * VIMSHOTTARI[start_lord][1] * SIDEREAL_YEAR)
    majors = []
    for i in range(10):
        lord, years = VIMSHOTTARI[(start_lord + i) % 9]
        end = cursor + dt.timedelta(days=years * SIDEREAL_YEAR)
        majors.append({"lord": lord, "start": cursor, "end": end, "years": years})
        cursor = end

    current = next((m for m in majors if m["start"] <= when < m["end"]), None)
    antar = None
    if current:
        sub_cursor = current["start"]
        lord_idx = next(i for i, (l, _) in enumerate(VIMSHOTTARI) if l == current["lord"])
        for j in range(9):
            slord, syears = VIMSHOTTARI[(lord_idx + j) % 9]
            length = current["years"] * syears / 120.0 * SIDEREAL_YEAR
            sub_end = sub_cursor + dt.timedelta(days=length)
            if sub_cursor <= when < sub_end:
                antar = {"lord": slord, "start": sub_cursor, "end": sub_end}
                break
            sub_cursor = sub_end

    def fmt(d: dt.datetime) -> str:
        return d.strftime("%b %Y")

    return {
        "nakshatra": NAKSHATRAS[idx],
        "pada": pada,
        "moon_position": f"{moon.sign} {dms(moon.sign_degree)}",
        "mahadasha": {
            "lord": current["lord"], "start": fmt(current["start"]), "end": fmt(current["end"]),
        } if current else None,
        "antardasha": {
            "lord": antar["lord"], "start": fmt(antar["start"]), "end": fmt(antar["end"]),
        } if antar else None,
        "upcoming": [
            {"lord": m["lord"], "start": fmt(m["start"]), "end": fmt(m["end"])}
            for m in majors if m["start"] > when
        ][:3],
    }


def solar_return(session: ChartSession, year: int) -> dict:
    """Solar return chart summary for the given calendar year."""
    b = session.birth
    engines, chosen, _, _ = _house_engines(b)
    sr = (
        ReturnBuilder.solar(session.chart, year, location=(b.latitude, b.longitude))
        .with_aspects()
        .with_house_systems(engines)
        .calculate()
    )
    asc = sr.get_object("ASC")
    cusps = list(sr.get_houses(chosen).cusps)
    return {
        "year": year,
        "exact": sr.to_dict()["datetime"]["utc"],
        "ascendant": f"{asc.sign} {dms(asc.sign_degree)}",
        "placements": [
            {
                "name": p.name,
                "position": f"{p.sign} {dms(p.sign_degree)}",
                "house": house_of(p.longitude, cusps),
            }
            for p in sr.get_planets()
        ],
    }


def wheel_svg(session: ChartSession, theme: str = "midnight") -> str:
    """Render the chart wheel as an inline SVG string."""
    import tempfile
    import os

    fd, path = tempfile.mkstemp(suffix=".svg")
    os.close(fd)
    try:
        drawer = session.chart.draw(path).with_theme(theme).with_size(760)
        try:
            drawer = drawer.with_transparent_background()
        except Exception:
            pass
        drawer.save()
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass
