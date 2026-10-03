"""Muhurat Finder — Classical Electional Astrology Engine.

Evaluates date ranges against classical electional (Muhurta) rules for
major life events (Marriage, Griha Pravesh, Mundan, Namkaran, General Auspicious).
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from zoneinfo import ZoneInfo

from . import panchang
from .panchang import daily_panchang
# The Hindi names live in names_hi.py (the one copy). TITHI_HI, NAKSHATRAS_HI and
# VARA_HI stay importable from here: festivals.py reads them from this module.
from .names_hi import KARANA_HI, NAKSHATRAS_HI, TITHI_HI, VARA_HI, YOGA_HI  # noqa: F401

MAX_SCAN_DAYS = 90

@dataclass(frozen=True)
class EventRule:
    key: str
    name_en: str
    name_hi: str
    preferred_tithis: set[int]
    excluded_tithis: set[int]
    preferred_nakshatras: set[str]
    excluded_nakshatras: set[str]
    preferred_varas: set[str]
    excluded_varas: set[str]
    excluded_yogas: set[str] = field(default_factory=lambda: {"Vyatipata", "Vaidhriti"})


EVENT_RULES: dict[str, EventRule] = {
    "marriage": EventRule(
        key="marriage",
        name_en="Marriage / Vivaha",
        name_hi="विवाह संस्कार",
        preferred_tithis={2, 3, 5, 7, 10, 11, 12, 13, 15},
        excluded_tithis={4, 9, 14, 30},
        preferred_nakshatras={
            "Rohini", "Mrigashira", "Magha", "Uttara Phalguni", "Hasta",
            "Swati", "Anuradha", "Mula", "Uttara Ashadha", "Uttara Bhadrapada", "Revati"
        },
        excluded_nakshatras={"Bharani", "Krittika", "Ardra", "Ashlesha", "Jyeshtha", "Purva Bhadrapada"},
        preferred_varas={"Monday", "Wednesday", "Thursday", "Friday", "Sunday"},
        excluded_varas={"Tuesday"},
        excluded_yogas={"Vyatipata", "Vaidhriti", "Ganda", "Atiganda", "Shula", "Vishkambha"},
    ),
    "griha_pravesh": EventRule(
        key="griha_pravesh",
        name_en="House Warming / Griha Pravesh",
        name_hi="गृह प्रवेश",
        preferred_tithis={2, 3, 5, 7, 10, 11, 12, 13, 15},
        excluded_tithis={4, 9, 14, 30},
        preferred_nakshatras={
            "Rohini", "Mrigashira", "Pushya", "Uttara Phalguni", "Hasta",
            "Chitra", "Anuradha", "Uttara Ashadha", "Shravana", "Dhanishta",
            "Shatabhisha", "Uttara Bhadrapada", "Revati"
        },
        excluded_nakshatras={"Bharani", "Krittika", "Ardra", "Ashlesha", "Magha", "Jyeshtha"},
        preferred_varas={"Monday", "Wednesday", "Thursday", "Friday"},
        excluded_varas={"Tuesday", "Sunday"},
        excluded_yogas={"Vyatipata", "Vaidhriti", "Shula", "Ganda"},
    ),
    "mundan": EventRule(
        key="mundan",
        name_en="Tonsure / Mundan",
        name_hi="चूड़ाकरण / मुंडन",
        preferred_tithis={2, 3, 5, 7, 10, 11, 13},
        excluded_tithis={4, 9, 14, 15, 30},
        preferred_nakshatras={
            "Ashwini", "Rohini", "Mrigashira", "Punarvasu", "Pushya",
            "Hasta", "Chitra", "Swati", "Jyeshtha", "Shravana",
            "Dhanishta", "Shatabhisha", "Revati"
        },
        excluded_nakshatras={"Bharani", "Krittika", "Ardra", "Ashlesha", "Magha", "Purva Phalguni", "Mula", "Purva Ashadha", "Purva Bhadrapada"},
        preferred_varas={"Monday", "Wednesday", "Thursday", "Friday"},
        excluded_varas={"Tuesday", "Saturday"},
        excluded_yogas={"Vyatipata", "Vaidhriti"},
    ),
    "namkaran": EventRule(
        key="namkaran",
        name_en="Naming Ceremony / Namkaran",
        name_hi="नामकरण संस्कार",
        preferred_tithis={1, 2, 3, 5, 6, 7, 10, 11, 12, 13, 15},
        excluded_tithis={4, 9, 14, 30},
        preferred_nakshatras={
            "Ashwini", "Rohini", "Mrigashira", "Punarvasu", "Pushya",
            "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Anuradha",
            "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
            "Uttara Bhadrapada", "Revati"
        },
        excluded_nakshatras={"Bharani", "Krittika", "Ashlesha", "Jyeshtha"},
        preferred_varas={"Monday", "Wednesday", "Thursday", "Friday"},
        excluded_varas=set(),
        excluded_yogas={"Vyatipata", "Vaidhriti"},
    ),
    "general": EventRule(
        key="general",
        name_en="Auspicious Work / General Muhurat",
        name_hi="सामान्य शुभ कार्य",
        preferred_tithis={2, 3, 5, 7, 10, 11, 12, 13, 15},
        excluded_tithis={4, 9, 14, 30},
        preferred_nakshatras={
            "Ashwini", "Rohini", "Mrigashira", "Pushya", "Uttara Phalguni",
            "Hasta", "Chitra", "Swati", "Anuradha", "Uttara Ashadha",
            "Shravana", "Dhanishta", "Shatabhisha", "Uttara Bhadrapada", "Revati"
        },
        excluded_nakshatras={"Bharani", "Krittika", "Ardra", "Ashlesha", "Jyeshtha"},
        preferred_varas={"Monday", "Wednesday", "Thursday", "Friday", "Sunday"},
        excluded_varas={"Tuesday"},
        excluded_yogas={"Vyatipata", "Vaidhriti"},
    ),
}



# --------------------------------------------------------------------------
# Classical period exclusions (DIVASTRO-109)
# --------------------------------------------------------------------------
#
# The five-limb checks above only look at one day. Every published muhurat
# list ALSO bars whole seasons, and before this the engine marked e.g. 5-13
# vivah dates "Auspicious" in every month of 2026, including Chaturmas and
# Kharmas, which no almanac does. Each rule below names its definition and
# source. All of them are computed from the ephemeris (lunar month + sunrise
# tithi, Sun's sidereal sign, planetary kalamsha) - nothing is a hard-coded
# date. The helpers live in panchang.py (`lunar_month_at`, `is_combust`).
#
#   chaturmas    - Devshayani (Ashadha Shukla 11) to Devuthani/Prabodhini
#                  (Kartika Shukla 11) Ekadashi, both days included: Vishnu's
#                  yoga-nidra, when vivah, griha pravesh, chudakarma (mundan)
#                  and upanayana are not performed (Muhurta Chintamani,
#                  vivaha/vastu prakarana: "Harishayana" is barred; Drik
#                  Panchang marks it "Prohibited Chaturmas"). Decided on the
#                  SUNRISE tithi of the amanta month; the observed Ekadashi
#                  can differ by a day when the tithi is kshaya/vriddhi.
#   kharmas      - Sun in sidereal Dhanu or Meena (Dhanu/Meena sankranti to the
#                  next sankranti): the Sun is in Jupiter's signs and
#                  "malina"; North Indian almanacs bar vivah, griha pravesh and
#                  mundan, and new ventures, in this month (Drik's
#                  "Prohibited Solar month" covers both for vivah).
#   adhik_maas   - Adhika (Mal/Purushottam) lunar month: a lunation with no
#                  solar ingress (see panchang.lunar_month_at). All kamya
#                  (optional, desire-driven) rites are barred in it (Muhurta
#                  Chintamani shubhashubha prakarana; Drik "Prohibited
#                  Adhika/Leaped month", 2026: 17 May - 15 Jun).
#   pitru_paksha - Bhadrapada Purnima through the following Amavasya
#                  (Mahalaya / Sarva Pitru Amavasya). That Krishna paksha is
#                  "Bhadrapada Krishna" in amanta and "Ashwin Krishna" in
#                  purnimanta reckoning - the same fortnight. The fortnight is
#                  given to shraddha; shubha karya and new starts are avoided.
#   shukra_asta  - Venus combust: within 10 kalamsha of the Sun (8 when
#   guru_asta      retrograde); Jupiter within 11 (Surya Siddhanta IX.6-9; see
#                  panchang.KALAMSHA for the method and the Drik comparison).
#                  Vivah and the other samskaras need both "witness" planets
#                  visible (Muhurta Chintamani: guru-shukra asta varjya).
#                  Plus ASTA_MARGIN_DAYS = 3 either side: the planet is
#                  "vriddha" (old) for the days before it sets and "bala /
#                  shishu" (infant) for the days after it rises, and is not
#                  yet a fit witness. Days: Drik Panchang's vivah tables mark
#                  exactly 3 days of "Vriddhatva Shukra/Brihaspati" before and
#                  3 of "Shishutva Shukra/Brihaspati" after every Shukra/Guru
#                  asta (e.g. 2022: Vriddhatva Brihaspati 18-20 Feb, Guru asta
#                  21 Feb - 4 May, Shishutva 5-7 May; 2026 New Delhi: Guru asta
#                  from 15 Jul but vivah barred from 12 Jul).
#
# Which events each rule applies to (`EVENT_PERIODS`):
#   marriage, griha_pravesh, mundan - all six. These are the mangal karya
#       the texts name for Chaturmas, Kharmas and guru-shukra asta.
#   general  - kharmas, adhik_maas, pitru_paksha only: these three bar new
#       beginnings generally. Chaturmas restricts samskaras, not ordinary
#       business or purchases (Dhanteras/Diwali shopping falls inside it), and
#       asta is a samskara rule.
#   namkaran - none. The naming ceremony is a time-bound samskara performed
#       on the 10th/11th/12th day after birth (Grihya Sutras); it cannot wait
#       four months for Chaturmas to end, so tradition does not block it by
#       season. Only the daily limbs apply.
#
# Not modelled (documented so nobody assumes they are): Holashtak, Simhastha
# Guru (Jupiter in Leo - a regional vivah bar), Drik's wider vivah solar-month
# rule (Sun in Karka/Simha/Kanya) and the griha pravesh lunar-month rule
# (Magha/Phalguna/Vaishakha/Jyeshtha best). In 2026-27 the solar-month vivah
# rule falls entirely inside Chaturmas/Guru asta, so the open months agree.

@dataclass(frozen=True)
class Period:
    key: str
    name_en: str
    name_hi: str
    about_en: str
    about_hi: str


PERIODS: dict[str, Period] = {
    "chaturmas": Period(
        "chaturmas", "Chaturmas", "चातुर्मास",
        "Devshayani Ekadashi to Devuthani Ekadashi, when Lord Vishnu is in yoga-nidra",
        "देवशयनी एकादशी से देवउठनी एकादशी तक, जब भगवान विष्णु योगनिद्रा में रहते हैं"),
    "kharmas": Period(
        "kharmas", "Kharmas", "खरमास",
        "the Sun in Dhanu (Sagittarius) or Meena (Pisces)",
        "सूर्य धनु या मीन राशि में"),
    "adhik_maas": Period(
        "adhik_maas", "Adhik Maas", "अधिक मास (मलमास)",
        "an intercalary lunar month with no solar ingress",
        "वह चंद्र मास जिसमें सूर्य की कोई संक्रांति नहीं होती"),
    "pitru_paksha": Period(
        "pitru_paksha", "Pitru Paksha", "पितृ पक्ष",
        "Bhadrapada Purnima to Sarva Pitru Amavasya, the fortnight of shraddha",
        "भाद्रपद पूर्णिमा से सर्वपितृ अमावस्या तक, श्राद्ध का पखवाड़ा"),
    "shukra_asta": Period(
        "shukra_asta", "Shukra Asta", "शुक्र अस्त",
        "Venus combust (too close to the Sun to be seen), with 3 days either side",
        "शुक्र ग्रह अस्त (सूर्य के अति निकट), आगे-पीछे 3 दिन सहित"),
    "guru_asta": Period(
        "guru_asta", "Guru Asta", "गुरु अस्त",
        "Jupiter combust (too close to the Sun to be seen), with 3 days either side",
        "गुरु ग्रह अस्त (सूर्य के अति निकट), आगे-पीछे 3 दिन सहित"),
}

_ALL_PERIODS = frozenset(PERIODS)
EVENT_PERIODS: dict[str, frozenset[str]] = {
    "marriage": _ALL_PERIODS,
    "griha_pravesh": _ALL_PERIODS,
    "mundan": _ALL_PERIODS,
    "general": frozenset({"kharmas", "adhik_maas", "pitru_paksha"}),
    "namkaran": frozenset(),
}

_DHANU, _MEENA = 8, 11
_EKADASHI = 10                    # 0-based tithi index of Shukla Ekadashi
_PURNIMA = 14
ASTA_MARGIN_DAYS = 3              # vriddhatva before / shishutva after, see above


def _asta(jd: float, planet: str, latitude: float) -> bool:
    """Combust today, or within ASTA_MARGIN_DAYS of a day that is."""
    offsets = sorted(range(-ASTA_MARGIN_DAYS, ASTA_MARGIN_DAYS + 1), key=abs)
    return any(panchang.is_combust(jd + k, planet, latitude) for k in offsets)


def day_periods(p: dict, latitude: float, ayanamsa: str = "lahiri",
                wanted: frozenset[str] = _ALL_PERIODS) -> list[str]:
    """Keys of the classical periods (above) in force on the vedic day `p`
    (a `daily_panchang` result), restricted to `wanted`, in PERIODS order."""
    if not wanted or not p.get("tithi"):
        return []
    start_iso = p.get("vara", {}).get("starts")
    jd = panchang._to_jd(dt.datetime.fromisoformat(start_iso))
    tithi = p["tithi"][0]["index"]                 # 0..29 at sunrise
    month = panchang.lunar_month_at(jd, ayanamsa)
    name, adhika = month["name"], month["adhika"]
    sun_sign = int(p["sun"]["longitude"] // 30)

    found = set()
    if name == "Ashadha":
        if not adhika and tithi >= _EKADASHI:
            found.add("chaturmas")
    elif name in ("Shravana", "Bhadrapada", "Ashwin"):
        found.add("chaturmas")
    elif name == "Kartika" and (adhika or tithi <= _EKADASHI):
        found.add("chaturmas")
    if sun_sign in (_DHANU, _MEENA):
        found.add("kharmas")
    if adhika:
        found.add("adhik_maas")
    if name == "Bhadrapada" and not adhika and tithi >= _PURNIMA:
        found.add("pitru_paksha")
    if "shukra_asta" in wanted and _asta(jd, "venus", latitude):
        found.add("shukra_asta")
    if "guru_asta" in wanted and _asta(jd, "jupiter", latitude):
        found.add("guru_asta")
    return [k for k in PERIODS if k in found and k in wanted]


def lunar_month_label(p: dict, ayanamsa: str = "lahiri") -> str:
    jd = panchang._to_jd(dt.datetime.fromisoformat(p["vara"]["starts"]))
    m = panchang.lunar_month_at(jd, ayanamsa)
    return ("Adhika " if m["adhika"] else "") + m["name"]


def find_muhurat(
    event: str,
    from_date: dt.date,
    to_date: dt.date,
    latitude: float,
    longitude: float,
    timezone: str,
    *,
    ayanamsa: str = "lahiri",
    language: str = "en"
) -> list[dict]:
    """Scan date range and return scored muhurat days for the event."""
    if event not in EVENT_RULES:
        raise ValueError(f"Unknown event '{event}'. Supported events: {', '.join(EVENT_RULES.keys())}")

    if from_date > to_date:
        raise ValueError("from_date must be before or equal to to_date")

    total_days = (to_date - from_date).days + 1
    if total_days > MAX_SCAN_DAYS:
        raise ValueError(f"Date range exceeds maximum limit of {MAX_SCAN_DAYS} days.")

    return [evaluate_day(event, d, latitude, longitude, timezone,
                         ayanamsa=ayanamsa, language=language)
            for d in (from_date + dt.timedelta(days=i) for i in range(total_days))]


def evaluate_day(
    event: str,
    curr: dt.date,
    latitude: float,
    longitude: float,
    timezone: str,
    *,
    ayanamsa: str = "lahiri",
    language: str = "en",
    p: dict | None = None,
) -> dict:
    """Score one day for one event. `p` lets a caller that already holds the
    day's panchang (the SEO year pages score two events per day) pass it in."""
    rule = EVENT_RULES[event]
    if p is None:
        p = daily_panchang(curr, latitude, longitude, timezone, ayanamsa=ayanamsa)

    tithis = p.get("tithi", [])
    t_info = tithis[0] if tithis else {}
    t_num = t_info.get("number", 1)
    t_name = t_info.get("name", "—")
    # `number` is 1..15 within the paksha, so Amavasya (Krishna 15) used to
    # read as 15 = Purnima and score as a *favourable* tithi. The rule tables
    # spell Amavasya as 30.
    if t_info.get("paksha") == "Krishna" and t_num == 15:
        t_num = 30

    nakshatras = p.get("nakshatra", [])
    n_info = nakshatras[0] if nakshatras else {}
    n_name = n_info.get("name", "—")

    yogas = p.get("yoga", [])
    y_info = yogas[0] if yogas else {}
    y_name = y_info.get("name", "—")

    karanas = p.get("karana", [])
    k_info = karanas[0] if karanas else {}
    k_name = k_info.get("name", "—")

    vara_eng = p.get("vara", {}).get("weekday", curr.strftime("%A"))

    score = 50
    reasons = []
    reasons_hi = []
    is_bad = False

    # 1. Tithi Check
    if t_num in rule.excluded_tithis:
        score -= 30
        is_bad = True
        reasons.append(f"Inauspicious tithi ({t_name})")
        reasons_hi.append(f"अशुभ तिथि ({TITHI_HI.get(t_name, t_name)})")
    elif t_num in rule.preferred_tithis:
        score += 20
        reasons.append(f"Favourable tithi ({t_name})")
        reasons_hi.append(f"शुभ तिथि ({TITHI_HI.get(t_name, t_name)})")

    # 2. Nakshatra Check
    if n_name in rule.excluded_nakshatras:
        score -= 30
        is_bad = True
        reasons.append(f"Restricted nakshatra ({n_name})")
        reasons_hi.append(f"वर्जित नक्षत्र ({NAKSHATRAS_HI.get(n_name, n_name)})")
    elif n_name in rule.preferred_nakshatras:
        score += 25
        reasons.append(f"Auspicious nakshatra ({n_name})")
        reasons_hi.append(f"उत्तम नक्षत्र ({NAKSHATRAS_HI.get(n_name, n_name)})")

    # 3. Vara Check
    if vara_eng in rule.excluded_varas:
        score -= 20
        reasons.append(f"Excluded weekday ({vara_eng})")
        reasons_hi.append(f"वर्जित वार ({VARA_HI.get(vara_eng, vara_eng)})")
    elif vara_eng in rule.preferred_varas:
        score += 15
        reasons.append(f"Auspicious weekday ({vara_eng})")
        reasons_hi.append(f"शुभ वार ({VARA_HI.get(vara_eng, vara_eng)})")

    # 4. Yoga Check
    if y_name in rule.excluded_yogas:
        score -= 25
        is_bad = True
        reasons.append(f"Inauspicious yoga ({y_name})")
        reasons_hi.append(f"अशुभ योग ({YOGA_HI.get(y_name, y_name)})")

    # 5. Vishti Karana (Bhadra)
    if k_name == "Vishti":
        score -= 25
        is_bad = True
        reasons.append("Bhadra (Vishti Karana) active")
        reasons_hi.append("विष्टि (भद्रा) करण सक्रिय")


    # 6. Classical periods (DIVASTRO-109, see the note above PERIODS). Any one
    # of them bars the day outright, whatever the limbs say.
    excluded = day_periods(p, latitude, ayanamsa, EVENT_PERIODS.get(event, frozenset()))
    for key in excluded:
        period = PERIODS[key]
        score -= 40
        is_bad = True
        reasons.append(f"{period.name_en}: {period.about_en}")
        reasons_hi.append(f"{period.name_hi}: {period.about_hi}")

    # Verdict calculation
    score = max(0, min(100, score))
    if is_bad or score < 45:
        verdict = "Inauspicious" if language != "hi" else "अशुभ"
        verdict_badge = "caution"
    elif score >= 75:
        verdict = "Auspicious" if language != "hi" else "शुभ / उत्तम"
        verdict_badge = "excellent"
    else:
        verdict = "Moderate" if language != "hi" else "मध्यम"
        verdict_badge = "neutral"

    abhijit = p.get("muhurta", {}).get("abhijit", {})
    rahu = p.get("muhurta", {}).get("rahu_kaal", {})

    abhijit_str = f"{abhijit['start'][11:16]} - {abhijit['end'][11:16]}" if (abhijit and abhijit.get("start") and abhijit.get("end")) else None
    rahu_str = f"{rahu['start'][11:16]} - {rahu['end'][11:16]}" if (rahu and rahu.get("start") and rahu.get("end")) else None

    hi = language == "hi"
    return {
        "date": curr.isoformat(),
        "vara": VARA_HI.get(vara_eng, vara_eng) if hi else vara_eng,
        "tithi": TITHI_HI.get(t_name, t_name) if hi else t_name,
        "nakshatra": NAKSHATRAS_HI.get(n_name, n_name) if hi else n_name,
        "yoga": YOGA_HI.get(y_name, y_name) if hi else y_name,
        "karana": KARANA_HI.get(k_name, k_name) if hi else k_name,
        "score": score,
        "verdict": verdict,
        "badge": verdict_badge,
        "abhijit": abhijit_str,
        "rahu_kaal": rahu_str,
        "reasons": reasons_hi if hi else reasons,
        "sunrise": p.get("sun", {}).get("rise"),
        "sunset": p.get("sun", {}).get("set"),
        # Added in DIVASTRO-109 (additive; nothing above changed shape):
        # whether a classical period bars the day, and which, so the UI can
        # say "Chaturmas" rather than just "Inauspicious".
        "excluded": bool(excluded),
        "excluded_periods": [
            {"key": k, "name": PERIODS[k].name_hi if hi else PERIODS[k].name_en}
            for k in excluded],
        "paksha": t_info.get("paksha"),
    }
