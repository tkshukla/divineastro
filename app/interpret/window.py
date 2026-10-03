"""Reading a date window for one chart (DIVASTRO-119).

`periods.parse_period` finds the window a question names ("10th oct to 20th
oct", "agle hafte"); this module answers it. Everything is deterministic and
Vedic — sidereal Lahiri, the same Swiss Ephemeris route as the panchang
engine (`panchang._sidereal`) and the kundali — and every date it prints is
computed, never estimated, so the narration layer can be held to them by the
date auditor in llm.py.

What is computed
----------------
1. **Vimshottari dasha** — mahadasha / antardasha / pratyantardasha running on
   the first day, and every change at any of the three levels inside the
   window, to the day. Same arithmetic as `chart_service.vimshottari` (natal
   Moon's nakshatra, 365.25-day year), extended one level down.
2. **Chandra gochar** — for each IST civil day, the sign the Moon occupies
   (the one covering most of the day, with the IST time if it changes) and its
   house counted from the natal Moon sign. Graded with the scheme the daily
   rashifal pages use (`rashifal_pages`: favourable 1, 3, 6, 7, 10, 11;
   mixed 2, 5, 9; take-it-easy 4, 8, 12 — Varahamihira, Brihat Samhita 104 and
   Phaladeepika 26). The 8th from the natal Moon is **Chandrashtama**; those
   stretches are reported with their IST start and end times.
3. **Tara bala** — the nakshatra prevailing at sunrise (New Delhi, the same
   reference the rashifal and panchang pages use) is counted from the janma
   (natal Moon) nakshatra, inclusively, and the count is reduced modulo 9 to
   one of the nine taras: 1 Janma, 2 Sampat, 3 Vipat, 4 Kshema, 5 Pratyak,
   6 Sadhana, 7 Naidhana, 8 Mitra, 9 Param-mitra. Vipat, Pratyak and Naidhana
   are unfavourable (Naidhana the most); Janma is mixed (classically avoided
   for new undertakings but not inauspicious in itself); the other five are
   favourable (Muhurta Chintamani; the standard tara-bala rule).
4. **Slow planets** — Saturn, Jupiter and the mean Rahu/Ketu: sign, house from
   the natal Moon and from the Lagna at the start of the window, and any sign
   ingress or retrograde/direct station inside it (dated). Sade Sati and Dhaiya
   status from `panchang.sade_sati_for_moon_sign`.
5. **Observances** — festivals and vrats dated inside the window by
   `festivals.observances` (New Delhi).
6. **Day scores** — Moon gochar (favourable +2, mixed 0, take-it-easy -2,
   Chandrashtama a further -1) plus tara bala (favourable +1, Janma -0.5,
   Vipat/Pratyak -1.5, Naidhana -2). When the question names a topic, the
   day also gains +1 when the Moon transits one of that topic's primary houses
   counted from the Lagna (e.g. the 10th for career), and +0.5 when the
   weekday's lord is one of the topic's significators. Those two bonuses mark
   *activation* of the topic, not a promise of outcome, and the answer says
   so. The best days are the highest scores; caution days are every
   Chandrashtama day plus the lowest scores.
"""

from __future__ import annotations

import datetime as dt
import functools
from zoneinfo import ZoneInfo

from ..astro import festivals
from ..astro import panchang as pe
from ..astro.names_hi import NAKSHATRAS_HI, VARA_HI
from ..chart_service import NAKSHATRAS, SIDEREAL_YEAR, SIGNS, VIMSHOTTARI, ChartSession
from .periods import Period, fmt_date

IST = ZoneInfo("Asia/Kolkata")
DELHI = (28.6139, 77.2090)

# The rashifal pages' scheme (rashifal_pages.py docstring), restated here
# rather than imported so the interpreter does not pull in a FastAPI router.
# tests/test_window.py asserts the two copies agree.
MOON_FAVOURABLE = frozenset({1, 3, 6, 7, 10, 11})
MOON_CHALLENGING = frozenset({4, 8, 12})
SATURN_FAVOURABLE = frozenset({3, 6, 11})
JUPITER_FAVOURABLE = frozenset({2, 5, 7, 9, 11})
NODE_FAVOURABLE = frozenset({3, 6, 11})
SADE_SATI_HOUSES = {12: 1, 1: 2, 2: 3}
DHAIYA = frozenset({4, 8})

TARAS = ("Janma", "Sampat", "Vipat", "Kshema", "Pratyak", "Sadhana",
         "Naidhana", "Mitra", "Param-mitra")
TARAS_HI = ("जन्म", "संपत", "विपत", "क्षेम", "प्रत्यक", "साधक", "नैधन", "मित्र", "परम मित्र")
TARA_BAD = frozenset({"Vipat", "Pratyak", "Naidhana"})
TARA_SCORE = {"Janma": -0.5, "Sampat": 1.0, "Vipat": -1.5, "Kshema": 1.0, "Pratyak": -1.5,
              "Sadhana": 1.0, "Naidhana": -2.0, "Mitra": 1.0, "Param-mitra": 1.0}
TARA_GLOSS = {
    "Janma": "mixed — the birth star; avoid fresh starts",
    "Sampat": "wealth and gain", "Vipat": "obstacles and loss",
    "Kshema": "well-being", "Pratyak": "opposition and friction",
    "Sadhana": "accomplishment", "Naidhana": "the hardest tara — rest, don't start",
    "Mitra": "friendly support", "Param-mitra": "very friendly support",
}
TARA_GLOSS_HI = {
    "Janma": "मिश्रित — जन्म तारा; नया आरंभ टालें", "Sampat": "धन और लाभ",
    "Vipat": "बाधा और हानि", "Kshema": "कुशल-क्षेम", "Pratyak": "विरोध और टकराव",
    "Sadhana": "कार्य-सिद्धि", "Naidhana": "सबसे कठिन तारा — विश्राम करें, आरंभ नहीं",
    "Mitra": "मित्रवत सहयोग", "Param-mitra": "अत्यंत अनुकूल सहयोग",
}

MOON_GLOSS = {
    1: "comfort and a clear mind", 2: "care with money and words",
    3: "courage; effort pays", 4: "home matters; mood can dip",
    5: "mixed — guard against hasty decisions", 6: "victory over obstacles",
    7: "company and partnerships go well", 8: "Chandrashtama — go slow, avoid risks",
    9: "mixed — plans may stall", 10: "work moves; recognition",
    11: "gains and good news", 12: "expenses and fatigue",
}
MOON_GLOSS_HI = {
    1: "सुख और मन की स्पष्टता", 2: "धन और वाणी में सावधानी", 3: "साहस; प्रयास सफल",
    4: "घर के मामले; मन कुछ भारी", 5: "मिश्रित — जल्दबाज़ी के निर्णय न लें",
    6: "बाधाओं पर विजय", 7: "साथ और साझेदारी अनुकूल", 8: "चंद्राष्टम — धीमे चलें, जोखिम न लें",
    9: "मिश्रित — योजनाएँ अटक सकती हैं", 10: "काम में गति; मान-सम्मान",
    11: "लाभ और शुभ समाचार", 12: "खर्च और थकान",
}

SIGNS_HI = ("मेष", "वृषभ", "मिथुन", "कर्क", "सिंह", "कन्या", "तुला", "वृश्चिक", "धनु",
            "मकर", "कुम्भ", "मीन")
MONTHS_HI = ("जनवरी", "फ़रवरी", "मार्च", "अप्रैल", "मई", "जून", "जुलाई", "अगस्त",
             "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर")
PLANET_HI = {"Sun": "सूर्य", "Moon": "चंद्रमा", "Mars": "मंगल", "Mercury": "बुध",
             "Jupiter": "गुरु", "Venus": "शुक्र", "Saturn": "शनि", "Rahu": "राहु", "Ketu": "केतु"}
HOUSE_HI = {1: "पहले", 2: "दूसरे", 3: "तीसरे", 4: "चौथे", 5: "पाँचवें", 6: "छठे",
            7: "सातवें", 8: "आठवें", 9: "नौवें", 10: "दसवें", 11: "ग्यारहवें", 12: "बारहवें"}
HOUSE_HI_NOM = {1: "पहला", 2: "दूसरा", 3: "तीसरा", 4: "चौथा", 5: "पाँचवाँ", 6: "छठा",
                7: "सातवाँ", 8: "आठवाँ", 9: "नौवाँ", 10: "दसवाँ", 11: "ग्यारहवाँ", 12: "बारहवाँ"}
TOPIC_HI = {
    "career": "करियर", "money": "धन", "love": "प्रेम और विवाह", "family": "घर-परिवार",
    "children": "संतान", "health": "स्वास्थ्य", "education": "शिक्षा",
    "travel": "यात्रा और विदेश", "spirituality": "आध्यात्म", "friends": "मित्र और संपर्क",
    "obstacles": "बाधाएँ और शत्रु",
}
WEEKDAY_LORDS = ("Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Sun")  # Mon..Sun


def _ord(n: int) -> str:
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def moon_tone(house: int) -> str:
    return "good" if house in MOON_FAVOURABLE else "easy" if house in MOON_CHALLENGING else "mixed"


def tara_of(janma_nak: int, day_nak: int) -> str:
    """Tara for a day's nakshatra (0-based indices). Inclusive count from the
    janma nakshatra (janma itself = 1), reduced modulo 9."""
    count = (day_nak - janma_nak) % 27 + 1
    return TARAS[(count - 1) % 9]


def house_from(base_sign: int, sign: int) -> int:
    return (sign - base_sign) % 12 + 1


# --------------------------------------------------------------------------
# Ephemeris helpers
# --------------------------------------------------------------------------

def _lon(jd: float, body: int) -> float:
    return pe._sidereal(jd, body, pe.DEFAULT_AYANAMSA)


def _jd(moment: dt.datetime) -> float:
    return pe._to_jd(moment)


def _when(jd: float) -> dt.datetime:
    return pe._from_jd(jd, IST)


def _bisect(f, lo: float, hi: float) -> float:
    """First jd in (lo, hi] where f changes from f(lo). f must change once."""
    v0 = f(lo)
    while hi - lo > pe._TOLERANCE_DAYS * 10:
        mid = (lo + hi) / 2
        if f(mid) == v0:
            lo = mid
        else:
            hi = mid
    return hi


def _changes(f, jd_from: float, jd_to: float, step: float) -> list[tuple[float, object]]:
    """[(jd, new value)] for every change of f between the two instants."""
    out = []
    a, va = jd_from, f(jd_from)
    while a < jd_to:
        b = min(a + step, jd_to)
        vb = f(b)
        if vb != va:
            t = _bisect(f, a, b)
            out.append((t, f(t)))
            a, va = t, f(t)
            continue
        a, va = b, vb
    return out


# --------------------------------------------------------------------------
# Vimshottari, three levels
# --------------------------------------------------------------------------

def _lord_index(lord: str) -> int:
    return next(i for i, (name, _) in enumerate(VIMSHOTTARI) if name == lord)


def _subperiods(lord: str, start: dt.datetime, years: float) -> list[dict]:
    out, cursor, i0 = [], start, _lord_index(lord)
    for j in range(9):
        sub, syears = VIMSHOTTARI[(i0 + j) % 9]
        length = years * syears / 120.0
        end = cursor + dt.timedelta(days=length * SIDEREAL_YEAR)
        out.append({"lord": sub, "start": cursor, "end": end, "years": length})
        cursor = end
    return out


def dasha_at(session: ChartSession, when: dt.datetime) -> dict | None:
    """{'maha','antar','pratyantar'} -> {lord,start,end} at `when`. Same
    start point and year length as chart_service.vimshottari."""
    lon = session.chart.get_object("Moon").longitude
    span = 360.0 / 27.0
    idx = int(lon // span) % 27
    frac = (lon % span) / span
    start_lord = idx % 9
    cursor = session.birth.local_datetime - dt.timedelta(
        days=frac * VIMSHOTTARI[start_lord][1] * SIDEREAL_YEAR)
    if when.tzinfo is None:
        when = when.replace(tzinfo=ZoneInfo(session.birth.timezone))
    for i in range(18):
        lord, years = VIMSHOTTARI[(start_lord + i) % 9]
        end = cursor + dt.timedelta(days=years * SIDEREAL_YEAR)
        if cursor <= when < end:
            maha = {"lord": lord, "start": cursor, "end": end, "years": years}
            antar = next(a for a in _subperiods(lord, cursor, years) if a["start"] <= when < a["end"])
            praty = next((p for p in _subperiods(antar["lord"], antar["start"], antar["years"])
                          if p["start"] <= when < p["end"]), None)
            return {"maha": maha, "antar": antar, "pratyantar": praty}
        cursor = end
    return None


def dasha_window(session: ChartSession, start: dt.datetime, end: dt.datetime) -> dict:
    """The dasha on the first moment of the window and each change inside it."""
    at = dasha_at(session, start)
    if not at:
        return {}
    changes = []
    cur = at
    guard = 0
    while cur and cur["pratyantar"] and cur["pratyantar"]["end"] <= end and guard < 200:
        moment = cur["pratyantar"]["end"]
        nxt = dasha_at(session, moment + dt.timedelta(seconds=1))
        if not nxt:
            break
        levels = [lvl for lvl in ("maha", "antar", "pratyantar")
                  if nxt[lvl]["lord"] != cur[lvl]["lord"] or nxt[lvl]["start"] != cur[lvl]["start"]]
        changes.append({"date": moment.astimezone(IST).date(), "levels": levels,
                        "maha": nxt["maha"]["lord"], "antar": nxt["antar"]["lord"],
                        "pratyantar": nxt["pratyantar"]["lord"],
                        "pratyantar_end": nxt["pratyantar"]["end"].astimezone(IST).date()})
        cur = nxt
        guard += 1

    def d(p: dict) -> dict:
        return {"lord": p["lord"], "start": p["start"].astimezone(IST).date(),
                "end": p["end"].astimezone(IST).date()}
    return {"maha": d(at["maha"]), "antar": d(at["antar"]),
            "pratyantar": d(at["pratyantar"]) if at["pratyantar"] else None,
            "changes": changes}


# --------------------------------------------------------------------------
# The Moon, day by day
# --------------------------------------------------------------------------

def _moon_sign(jd: float) -> int:
    return int(_lon(jd, pe.swe.MOON) // 30)


def _moon_nak(jd: float) -> int:
    return int(_lon(jd, pe.swe.MOON) // (360.0 / 27.0)) % 27


@functools.lru_cache(maxsize=4096)
def _sunrise(day: dt.date) -> dt.datetime:
    rise = pe.sun_times(day, DELHI[0], DELHI[1], "Asia/Kolkata")[0]
    return rise or dt.datetime.combine(day, dt.time(6, 0), IST)


def moon_days(start: dt.date, end: dt.date) -> tuple[list[dict], list[tuple[dt.datetime, int]]]:
    """Per IST day: Moon sign segments and the sunrise nakshatra. Also returns
    every Moon sign ingress (IST datetime, new sign) from a little before the
    window to a little after, for Chandrashtama spans."""
    pe._ephemeris()
    jd0 = _jd(dt.datetime.combine(start - dt.timedelta(days=3), dt.time(), IST))
    jd1 = _jd(dt.datetime.combine(end + dt.timedelta(days=4), dt.time(), IST))
    ingress = [(_when(j), s) for j, s in _changes(_moon_sign, jd0, jd1, 0.25)]
    first_sign = _moon_sign(jd0)

    def sign_at(moment: dt.datetime) -> int:
        s = first_sign
        for t, new in ingress:
            if t <= moment:
                s = new
            else:
                break
        return s

    days = []
    d = start
    while d <= end:
        midnight = dt.datetime.combine(d, dt.time(), IST)
        nxt = midnight + dt.timedelta(days=1)
        # An ingress in the first minutes after midnight starts the day rather
        # than splitting it ("Moon in Gemini until 00:00 IST" says nothing).
        lead = midnight + dt.timedelta(minutes=5)
        segs = [{"sign": sign_at(lead), "from": None, "until": None}]
        for t, new in ingress:
            if lead < t < nxt:
                segs[-1]["until"] = t
                segs.append({"sign": new, "from": t, "until": None})
        # The segment that covers most of the day sets the day's tone.
        main = max(segs, key=lambda s: ((s["until"] or nxt) - (s["from"] or midnight)))
        rise = _sunrise(d)
        days.append({"date": d, "segments": segs, "main_sign": main["sign"],
                     "nakshatra": _moon_nak(_jd(rise)), "sunrise": rise})
        d += dt.timedelta(days=1)
    return days, ingress


def chandrashtama_spans(ingress: list[tuple[dt.datetime, int]], natal_moon_sign: int,
                        start: dt.date, end: dt.date) -> list[dict]:
    """Every stretch the Moon spends in the 8th from the natal Moon that touches
    the window, with IST start and end."""
    eighth = (natal_moon_sign + 7) % 12
    out = []
    for i, (t, sign) in enumerate(ingress):
        if sign != eighth:
            continue
        until = ingress[i + 1][0] if i + 1 < len(ingress) else None
        if until is None:
            continue
        if until.date() < start or t.date() > end:
            continue
        out.append({"from": t, "until": until})
    return out


# --------------------------------------------------------------------------
# Slow planets
# --------------------------------------------------------------------------

_SLOW = (("Saturn", "SATURN"), ("Jupiter", "JUPITER"), ("Rahu", "MEAN_NODE"))


def slow_planets(start: dt.date, end: dt.date, moon_sign: int, lagna_sign: int) -> list[dict]:
    pe._ephemeris()
    swe = pe.swe
    noon = _jd(dt.datetime.combine(start, dt.time(12), IST))
    jd_end = _jd(dt.datetime.combine(end, dt.time(23, 59), IST))
    out = []
    for name, const in _SLOW:
        body = getattr(swe, const)

        def sign(jd: float, body=body) -> int:
            return int(_lon(jd, body) // 30)

        def retro(jd: float, body=body) -> bool:
            return swe.calc_ut(jd, body, swe.FLG_SWIEPH | swe.FLG_SPEED)[0][3] < 0

        s0 = sign(noon)
        events = []
        for t, new in _changes(sign, noon, jd_end, 1.0):
            events.append({"kind": "ingress", "date": _when(t).date(), "sign": new})
        if name != "Rahu":                       # the mean node is always retrograde
            for t, r in _changes(retro, noon, jd_end, 1.0):
                events.append({"kind": "retrograde" if r else "direct", "date": _when(t).date()})
        events.sort(key=lambda e: e["date"])
        out.append({"planet": name, "sign": s0, "retrograde": retro(noon),
                    "from_moon": house_from(moon_sign, s0),
                    "from_lagna": house_from(lagna_sign, s0), "events": events})
        if name == "Rahu":
            k0 = (s0 + 6) % 12
            out.append({"planet": "Ketu", "sign": k0, "retrograde": True,
                        "from_moon": house_from(moon_sign, k0),
                        "from_lagna": house_from(lagna_sign, k0),
                        "events": [{"kind": "ingress", "date": e["date"], "sign": (e["sign"] + 6) % 12}
                                   for e in events if e["kind"] == "ingress"]})
    return out


def slow_quality(planet: str, house: int) -> str:
    good = {"Saturn": SATURN_FAVOURABLE, "Jupiter": JUPITER_FAVOURABLE,
            "Rahu": NODE_FAVOURABLE, "Ketu": NODE_FAVOURABLE}[planet]
    return "favourable" if house in good else "testing"


def sade_sati_status(moon_sign: int, start: dt.date) -> dict:
    try:
        ss = pe.sade_sati_for_moon_sign(moon_sign, dt.datetime.combine(start, dt.time(12), IST),
                                        timezone="Asia/Kolkata", window_years=8.0)
    except Exception:                                   # noqa: BLE001 — never fatal
        return {}
    out: dict = {"running": ss["running"], "dhaiya": ss["dhaiya"]["running"]}
    if ss["running"] and ss.get("phase"):
        ph = ss["phase"]
        out["phase"] = ph["phase"]
        out["phase_name"] = ph["name"]
        cur = ss["current_period"]
        out["period_start"] = _iso_date(cur.get("start"))
        out["period_end"] = _iso_date(cur.get("end"))
    if ss["dhaiya"]["running"]:
        cur = ss["dhaiya"]["current"]
        out["dhaiya_name"] = cur["phases"][0]["name"] if cur.get("phases") else "Dhaiya"
        out["dhaiya_start"] = _iso_date(cur.get("start"))
        out["dhaiya_end"] = _iso_date(cur.get("end"))
    return out


def _iso_date(s: str | None) -> dt.date | None:
    return dt.datetime.fromisoformat(s).date() if s else None


# --------------------------------------------------------------------------
# Observances
# --------------------------------------------------------------------------

def observances(start: dt.date, end: dt.date) -> list[dict]:
    try:
        items = festivals.observances(start, end)
    except Exception:                                   # noqa: BLE001
        return []
    seen, out = set(), []
    for o in items:
        key = (o["date"], (o.get("tithi") or {}).get("number"))
        # "Amavasya" and "Sarva Pitru Amavasya" on one date are one event.
        if key in seen and not o.get("major"):
            continue
        seen.add(key)
        out.append({"date": dt.date.fromisoformat(o["date"]), "name": o["name_en"],
                    "name_hi": o.get("name_hi") or o["name_en"], "major": bool(o.get("major")),
                    "key": o.get("key")})
    # Navratri is listed by its first day; Dussehra closes it, so when both
    # fall in the same window the span between them is named too.
    nav = next((o for o in out if o["key"] == "navratri"), None)
    dus = next((o for o in out if o["key"] == "dussehra"), None)
    if nav and dus and dus["date"] > nav["date"]:
        nav["until"] = dus["date"] - dt.timedelta(days=1)
    return out


# --------------------------------------------------------------------------
# Putting it together
# --------------------------------------------------------------------------

def analyse_window(session: ChartSession, period: Period, topic=None) -> dict:
    """Every computed fact for the window, ready to render or to hand the
    narration layer. `topic` is a topics.Topic or None (a plain "how is my
    week" question)."""
    view = pe._chart_view(session)
    natal_moon = view["longitudes"]["Moon"]
    moon_sign = int(natal_moon // 30)
    janma_nak = int(natal_moon // (360.0 / 27.0)) % 27
    lagna_sign = int(view["cusps"][0] // 30)

    weigh = topic is not None and topic.key not in ("period", "timing", "self")
    days, ingress = moon_days(period.start, period.end)
    spans = chandrashtama_spans(ingress, moon_sign, period.start, period.end)

    scored = []
    for d in days:
        house = house_from(moon_sign, d["main_sign"])
        tone = moon_tone(house)
        tara = tara_of(janma_nak, d["nakshatra"])
        score = {"good": 2.0, "mixed": 0.0, "easy": -2.0}[tone]
        chandrashtama = any(house_from(moon_sign, s["sign"]) == 8 for s in d["segments"])
        if house == 8:
            score -= 1.0
        score += TARA_SCORE[tara]
        boosts = []
        lagna_house = house_from(lagna_sign, d["main_sign"])
        lord = WEEKDAY_LORDS[d["date"].weekday()]
        if weigh:
            if lagna_house in topic.primary_houses:
                score += 1.0
                boosts.append(("moon_topic_house", lagna_house))
            if lord in topic.significators:
                score += 0.5
                boosts.append(("weekday_lord", lord))
        scored.append({
            **d, "moon_house": house, "tone": tone, "tara": tara,
            "chandrashtama": chandrashtama, "lagna_house": lagna_house,
            "weekday_lord": lord, "score": round(score, 2), "boosts": boosts,
            # The day's net reading, Moon and tara together.
            "net": "good" if score >= 1.0 else "caution" if score <= -1.0 else "mixed",
        })

    best = sorted((d for d in scored if d["score"] > 0 and not d["chandrashtama"]),
                  key=lambda d: (-d["score"], d["date"]))[:5]
    caution_pool = [d for d in scored if d["chandrashtama"] or d["score"] <= -1.5]
    caution = sorted(caution_pool, key=lambda d: (d["score"], d["date"]))[:6]
    best.sort(key=lambda d: d["date"])
    caution.sort(key=lambda d: d["date"])

    mean = sum(d["score"] for d in scored) / max(len(scored), 1)
    window_score = max(-1.0, min(1.0, mean / 3.0))

    return {
        "period": period.to_dict(),
        "natal": {"moon_sign": moon_sign, "janma_nakshatra": janma_nak, "lagna_sign": lagna_sign},
        "topic": topic.key if topic is not None else None,
        "topic_label": topic.label if topic is not None else None,
        "topic_houses": list(topic.primary_houses) if weigh else [],
        "topic_significators": list(topic.significators) if weigh else [],
        "weighted": weigh,
        "dasha": dasha_window(session, dt.datetime.combine(period.start, dt.time(), IST),
                              dt.datetime.combine(period.end, dt.time(23, 59, 59), IST)),
        "days": scored,
        "chandrashtama": spans,
        "best": best,
        "caution": caution,
        "slow": slow_planets(period.start, period.end, moon_sign, lagna_sign),
        "sade_sati": sade_sati_status(moon_sign, period.start),
        "observances": observances(period.start, period.end),
        "score": round(window_score, 3),
        "counts": {t: sum(1 for d in scored if d["tone"] == t) for t in ("good", "mixed", "easy")},
    }


# --------------------------------------------------------------------------
# Rendering — English and Hindi
# --------------------------------------------------------------------------

def verdict_of(score: float) -> tuple[str, str]:
    if score >= 0.2:
        return "Largely favourable", "अधिकतर अनुकूल"
    if score >= -0.1:
        return "Mixed", "मिश्रित"
    return "Needs care", "सावधानी का समय"


def _d(d: dt.date, lang: str, weekday: bool = False) -> str:
    if lang == "hi":
        s = f"{d.day} {MONTHS_HI[d.month - 1]} {d.year}"
        return f"{s} ({VARA_HI[d.strftime('%A')]})" if weekday else s
    return f"{fmt_date(d)} ({d:%a})" if weekday else fmt_date(d)


def _t(moment: dt.datetime, lang: str, with_date: bool = True) -> str:
    m = moment.astimezone(IST)
    hhmm = f"{m:%H:%M}"
    if not with_date:
        return f"{hhmm} IST"
    return f"{_d(m.date(), lang)} {hhmm} IST"


def _sign(i: int, lang: str) -> str:
    return SIGNS_HI[i] if lang == "hi" else SIGNS[i]


def _planet(p: str, lang: str) -> str:
    return PLANET_HI.get(p, p) if lang == "hi" else p


def _nak(i: int, lang: str) -> str:
    return NAKSHATRAS_HI.get(NAKSHATRAS[i], NAKSHATRAS[i]) if lang == "hi" else NAKSHATRAS[i]


def _tara(t: str, lang: str) -> str:
    return TARAS_HI[TARAS.index(t)] if lang == "hi" else t


def day_reason(d: dict, w: dict, lang: str = "en") -> str:
    """One line: why this day scored the way it did."""
    hi = lang == "hi"
    moon = (f"चंद्रमा {_sign(d['main_sign'], lang)} में, आपकी चंद्र राशि से {HOUSE_HI[d['moon_house']]} भाव में "
            f"({MOON_GLOSS_HI[d['moon_house']]})" if hi else
            f"Moon in {_sign(d['main_sign'], lang)}, {_ord(d['moon_house'])} from your Moon "
            f"({MOON_GLOSS[d['moon_house']]})")
    tara = (f"{_tara(d['tara'], lang)} तारा — {_nak(d['nakshatra'], lang)} "
            f"({TARA_GLOSS_HI[d['tara']]})" if hi else
            f"{d['tara']} tara — {_nak(d['nakshatra'], lang)} ({TARA_GLOSS[d['tara']]})")
    parts = [moon, tara]
    for seg in d["segments"]:
        if d["moon_house"] != 8 and house_from(w["natal"]["moon_sign"], seg["sign"]) == 8:
            if seg["from"]:
                parts.append(f"{_t(seg['from'], lang, with_date=False)} से चंद्राष्टम" if hi else
                             f"Chandrashtama from {_t(seg['from'], lang, with_date=False)}")
            elif seg["until"]:
                parts.append(f"{_t(seg['until'], lang, with_date=False)} तक चंद्राष्टम" if hi else
                             f"Chandrashtama until {_t(seg['until'], lang, with_date=False)}")
    other = [s for s in d["segments"] if s["sign"] != d["main_sign"]]
    if len(d["segments"]) > 1 and not (
            other and d["moon_house"] != 8
            and house_from(w["natal"]["moon_sign"], other[0]["sign"]) == 8):
        ch = d["segments"][1]
        if ch["sign"] == d["main_sign"]:
            prev = d["segments"][0]["sign"]
            parts.append(f"{_t(ch['from'], lang, with_date=False)} तक चंद्रमा {_sign(prev, lang)} में"
                         if hi else
                         f"Moon in {_sign(prev, lang)} until {_t(ch['from'], lang, with_date=False)}")
        else:
            parts.append(f"{_t(ch['from'], lang, with_date=False)} से चंद्रमा {_sign(ch['sign'], lang)} में"
                         if hi else
                         f"Moon moves into {_sign(ch['sign'], lang)} at "
                         f"{_t(ch['from'], lang, with_date=False)}")
    label_hi = TOPIC_HI.get(w.get("topic") or "", w.get("topic_label") or "")
    for kind, val in d["boosts"]:
        if kind == "moon_topic_house":
            parts.append(f"चंद्रमा लग्न से {HOUSE_HI[val]} भाव ({label_hi}) को सक्रिय करता है" if hi
                         else f"Moon activates your {_ord(val)} house from Lagna ({w['topic_label']})")
        elif kind == "weekday_lord":
            parts.append(f"वार-स्वामी {_planet(val, lang)} {label_hi} का कारक" if hi
                         else f"the day's lord {val} is a significator of {w['topic_label']}")
    return " · ".join(parts)


def render(w: dict, lang: str = "en") -> str:
    """The engine's answer for a window question (markdown, like compose())."""
    hi = lang == "hi"
    p = w["period"]
    start, end = dt.date.fromisoformat(p["start"]), dt.date.fromisoformat(p["end"])
    span = _d(start, lang) if start == end else f"{_d(start, lang)} – {_d(end, lang)}"
    v_en, v_hi = verdict_of(w["score"])
    c = w["counts"]
    n = len(w["days"])
    lines: list[str] = []

    topic_bit = ""
    if w["weighted"]:
        topic_bit = (f", {TOPIC_HI.get(w['topic'], w['topic_label'])} के लिए" if hi
                     else f", read for {w['topic_label']}")
    if hi:
        lines.append(f"**{v_hi} — {span}{topic_bit}।** इस अवधि के {n} दिनों में चंद्र गोचर "
                     f"{c['good']} दिन अनुकूल, {c['mixed']} दिन मिश्रित और {c['easy']} दिन संयम वाले हैं।")
    else:
        lines.append(f"**{v_en} — {span}{topic_bit}.** Of the {n} day{'s' if n != 1 else ''} in "
                     f"this window, the Moon's transit is favourable on {c['good']}, mixed on "
                     f"{c['mixed']} and asks for care on {c['easy']}.")
    if p["past"]:
        lines.append("_यह अवधि बीत चुकी है — यह उस समय का पिछला विवरण है।_" if hi else
                     "_This window is already in the past — this is a look back at it._")
    elif p["partly_past"]:
        lines.append("_इस अवधि का कुछ हिस्सा बीत चुका है।_" if hi else
                     "_Part of this window has already passed._")
    if p["rolled_year"]:
        lines.append(f"_इस वर्ष की यह तारीख़ बीत चुकी है, इसलिए इसे {start.year} के लिए पढ़ा गया है।_"
                     if hi else
                     f"_That date has already passed this year, so I have read it as {start.year}._")
    if p["truncated"]:
        lines.append("_लंबी अवधि को एक वर्ष तक सीमित किया गया है।_" if hi else
                     "_A very long window is read for its first year only._")
    lines.append("")

    # Dasha
    ds = w.get("dasha") or {}
    if ds:
        lines.append("### चल रही दशा" if hi else "### The running dasha")
        md, ad, pd = ds["maha"], ds["antar"], ds.get("pratyantar")
        if hi:
            lines.append(f"- **{_planet(md['lord'], lang)} महादशा** ({_d(md['start'], lang)} – {_d(md['end'], lang)}), "
                         f"**{_planet(ad['lord'], lang)} अंतर्दशा** ({_d(ad['start'], lang)} – {_d(ad['end'], lang)})"
                         + (f", **{_planet(pd['lord'], lang)} प्रत्यंतर दशा** ({_d(pd['start'], lang)} – "
                            f"{_d(pd['end'], lang)})" if pd else "") + "।")
        else:
            lines.append(f"- **{md['lord']} mahadasha** ({_d(md['start'], lang)} – {_d(md['end'], lang)}), "
                         f"**{ad['lord']} antardasha** ({_d(ad['start'], lang)} – {_d(ad['end'], lang)})"
                         + (f", **{pd['lord']} pratyantardasha** ({_d(pd['start'], lang)} – "
                            f"{_d(pd['end'], lang)})" if pd else "") + ".")
        level_en = {"maha": "mahadasha", "antar": "antardasha", "pratyantar": "pratyantardasha"}
        level_hi = {"maha": "महादशा", "antar": "अंतर्दशा", "pratyantar": "प्रत्यंतर दशा"}
        for ch in ds.get("changes") or []:
            top = ch["levels"][0]
            who = ch[top]
            if hi:
                lines.append(f"- **{_d(ch['date'], lang)}** — {level_hi[top]} बदलकर "
                             f"**{_planet(who, lang)}** की होती है"
                             + (f" (प्रत्यंतर {_planet(ch['pratyantar'], lang)})" if top != "pratyantar" else "")
                             + "।")
            else:
                lines.append(f"- **{_d(ch['date'], lang)}** — the {level_en[top]} changes to "
                             f"**{who}**"
                             + (f" (pratyantar {ch['pratyantar']})" if top != "pratyantar" else "")
                             + ".")
        if not ds.get("changes"):
            lines.append("- इस अवधि में दशा नहीं बदलती।" if hi else
                         "- No dasha level changes inside this window.")
        lines.append("")

    # Timing
    lines.append("### समय — शुभ दिन और सावधानी के दिन" if hi else "### Timing")
    if w["best"]:
        lines.append("**सबसे अच्छे दिन:**" if hi else "**Best days:**")
        for d in w["best"]:
            lines.append(f"- **{_d(d['date'], lang, weekday=True)}** — {day_reason(d, w, lang)}")
    else:
        lines.append("इस अवधि में कोई दिन स्पष्ट रूप से अनुकूल नहीं है।" if hi else
                     "No day in this window stands out as clearly favourable.")
    lines.append("")
    if w["caution"]:
        lines.append("**सावधानी के दिन:**" if hi else "**Days to go carefully:**")
        for d in w["caution"]:
            lines.append(f"- **{_d(d['date'], lang, weekday=True)}** — {day_reason(d, w, lang)}")
    lines.append("")
    if w["chandrashtama"]:
        if hi:
            lines.append("**चंद्राष्टम** (चंद्रमा आपकी जन्म राशि से आठवें भाव में — बड़े निर्णय, यात्रा "
                         "और जोखिम टालें):")
        else:
            lines.append("**Chandrashtama** (the Moon in the 8th from your natal Moon — avoid big "
                         "decisions, risky travel and confrontations):")
        for s in w["chandrashtama"]:
            lines.append(f"- {_t(s['from'], lang)} {'से' if hi else 'to'} {_t(s['until'], lang)}"
                         + (" तक" if hi else ""))
        lines.append("")

    if len(w["days"]) <= 31:
        lines.append("**दिन-प्रतिदिन:**" if hi else "**Day by day:**")
        tone_en = {"good": "favourable", "mixed": "mixed", "caution": "go carefully"}
        tone_hi = {"good": "अनुकूल", "mixed": "मिश्रित", "caution": "सावधानी"}
        for d in w["days"]:
            tag = (tone_hi if hi else tone_en)[d["net"]]
            if d["chandrashtama"]:
                tag = "चंद्राष्टम" if hi else "Chandrashtama"
            if hi:
                lines.append(f"- **{_d(d['date'], lang, weekday=True)}** — चंद्रमा {_sign(d['main_sign'], lang)} "
                             f"({HOUSE_HI_NOM[d['moon_house']]}), {_tara(d['tara'], lang)} तारा — {tag}")
            else:
                lines.append(f"- **{_d(d['date'], lang, weekday=True)}** — Moon {_sign(d['main_sign'], lang)} "
                             f"({_ord(d['moon_house'])}), {d['tara']} tara — {tag}")
        lines.append("")
    else:
        lines.append("**महीनेवार:**" if hi else "**Month by month:**")
        months: dict[tuple[int, int], list[dict]] = {}
        for d in w["days"]:
            months.setdefault((d["date"].year, d["date"].month), []).append(d)
        for (y, mo), ds_ in months.items():
            g = sum(1 for d in ds_ if d["tone"] == "good")
            e = sum(1 for d in ds_ if d["tone"] == "easy")
            top = max(ds_, key=lambda d: d["score"])
            first = ds_[0]["date"]
            if hi:
                lines.append(f"- **{MONTHS_HI[mo - 1]} {y}** — {g} अनुकूल, {e} संयम के दिन; "
                             f"सबसे अच्छा दिन {_d(top['date'], lang)}")
            else:
                lines.append(f"- **{first:%b %Y}** — {g} favourable and {e} take-it-easy days; "
                             f"best day {_d(top['date'], lang)}")
        lines.append("")

    # Slow planets
    lines.append("### धीमे ग्रह (पृष्ठभूमि)" if hi else "### The slow planets (the backdrop)")
    for s in w["slow"]:
        q = slow_quality(s["planet"], s["from_moon"])
        retro = (" (वक्री)" if hi else " (retrograde)") if s["retrograde"] and s["planet"] in ("Saturn", "Jupiter") else ""
        if hi:
            line = (f"- **{_planet(s['planet'], lang)}** {_sign(s['sign'], lang)} में{retro} — चंद्र राशि से "
                    f"{HOUSE_HI_NOM[s['from_moon']]}, लग्न से {HOUSE_HI_NOM[s['from_lagna']]} भाव "
                    f"({'अनुकूल' if q == 'favourable' else 'परीक्षा वाला'})")
        else:
            line = (f"- **{s['planet']}** in {_sign(s['sign'], lang)}{retro} — {_ord(s['from_moon'])} from "
                    f"your Moon, {_ord(s['from_lagna'])} from your Lagna ({q})")
        for e in s["events"]:
            if e["kind"] == "ingress":
                line += (f"; {_d(e['date'], lang)} को {_sign(e['sign'], lang)} में प्रवेश" if hi else
                         f"; enters {_sign(e['sign'], lang)} on {_d(e['date'], lang)}")
            else:
                word = ({"retrograde": "वक्री", "direct": "मार्गी"} if hi else
                        {"retrograde": "turns retrograde", "direct": "turns direct"})[e["kind"]]
                line += (f"; {_d(e['date'], lang)} को {word}" if hi else
                         f"; {word} on {_d(e['date'], lang)}")
        lines.append(line + ("।" if hi else "."))
    ss = w.get("sade_sati") or {}
    if ss.get("running"):
        if hi:
            lines.append(f"- **साढ़ेसाती चल रही है** — चरण {ss.get('phase')}"
                         + (f" ({_d(ss['period_start'], lang)} – {_d(ss['period_end'], lang)})"
                            if ss.get("period_start") and ss.get("period_end") else "") + "।")
        else:
            lines.append(f"- **Sade Sati is running** — phase {ss.get('phase')} ({ss.get('phase_name')})"
                         + (f", the whole span {_d(ss['period_start'], lang)} – {_d(ss['period_end'], lang)}"
                            if ss.get("period_start") and ss.get("period_end") else "") + ".")
    elif ss.get("dhaiya"):
        if hi:
            lines.append("- **शनि की ढैया चल रही है**"
                         + (f" ({_d(ss['dhaiya_start'], lang)} – {_d(ss['dhaiya_end'], lang)})"
                            if ss.get("dhaiya_start") and ss.get("dhaiya_end") else "") + "।")
        else:
            lines.append(f"- **Saturn's Dhaiya is running** — {ss.get('dhaiya_name')}"
                         + (f" ({_d(ss['dhaiya_start'], lang)} – {_d(ss['dhaiya_end'], lang)})"
                            if ss.get("dhaiya_start") and ss.get("dhaiya_end") else "") + ".")
    elif ss:
        lines.append("- साढ़ेसाती या ढैया नहीं चल रही।" if hi else "- No Sade Sati or Dhaiya is running.")
    lines.append("")

    obs = w.get("observances") or []
    if obs:
        lines.append("### इस अवधि के व्रत-त्योहार" if hi else "### Festivals and observances in this window")
        for o in obs[:12]:
            name = o["name_hi"] if hi else o["name"]
            if o.get("until"):
                name = (f"शारदीय नवरात्रि ({_d(o['date'], lang)} – {_d(o['until'], lang)})" if hi else
                        f"Sharad Navratri ({_d(o['date'], lang)} – {_d(o['until'], lang)})")
            lines.append(f"- **{_d(o['date'], lang)}** — {name}")
        lines.append("")

    lines.append("### यह कैसे पढ़ा गया" if hi else "### How this is read")
    if hi:
        lines.append("चंद्र गोचर आपकी जन्म चंद्र राशि से गिना गया है (पहला, तीसरा, छठा, सातवाँ, दसवाँ, "
                     "ग्यारहवाँ अनुकूल; चौथा, आठवाँ, बारहवाँ संयम; दूसरा, पाँचवाँ, नौवाँ मिश्रित)। तारा बल "
                     "जन्म नक्षत्र से उस दिन के सूर्योदय के नक्षत्र तक गिनकर (9 से भाग) निकाला गया है; विपत, "
                     "प्रत्यक और नैधन तारा प्रतिकूल हैं।"
                     + (f" {TOPIC_HI.get(w['topic'], w['topic_label'])} के लिए, जिस दिन चंद्रमा लग्न से "
                        f"{' या '.join(HOUSE_HI[h] for h in w['topic_houses'])} भाव में हो, या वार का "
                        f"स्वामी विषय का कारक ग्रह हो, उसे अधिक अंक दिए गए हैं — "
                        "यह विषय की सक्रियता है, परिणाम की गारंटी नहीं।" if w["weighted"] else ""))
    else:
        lines.append("The Moon's transit is counted from your natal Moon sign (1st, 3rd, 6th, 7th, "
                     "10th, 11th favourable; 4th, 8th, 12th take it easy; 2nd, 5th, 9th mixed). Tara "
                     "bala counts from your birth nakshatra to the nakshatra at that day's sunrise, "
                     "modulo 9; Vipat, Pratyak and Naidhana are the unfavourable taras."
                     + (f" For {w['topic_label']}, days when the Moon transits your "
                        f"{', '.join(_ord(h) for h in w['topic_houses'])} house from the Lagna, or "
                        f"fall on a weekday ruled by one of "
                        f"{', '.join(w['topic_significators'])}, score higher — that marks the topic "
                        f"being activated, not a guaranteed outcome." if w["weighted"] else ""))
    lines.append("")
    lines.append("> यह गोचर आपकी परिस्थितियों का संकेत है, निश्चित परिणाम नहीं।" if hi else
                 "> Transits describe the conditions you are working in, not a fixed outcome.")
    return "\n".join(lines).strip()


def json_safe(obj):
    """Dates and datetimes to ISO strings, recursively (the API result is
    serialised with json.dumps)."""
    if isinstance(obj, (dt.date, dt.datetime)):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [json_safe(v) for v in obj]
    return obj


def facts_block(w: dict) -> str:
    """The window as dated facts for the polish prompt (English; every date in
    'D Mon YYYY' form so llm._allowed_dates_note lists it)."""
    p = w["period"]
    start, end = dt.date.fromisoformat(p["start"]), dt.date.fromisoformat(p["end"])
    out = [f"- The question asks about the window {fmt_date(start)} to {fmt_date(end)} "
           f"({p['days']} days). Answer about THIS window, not the person's general nature."]
    if p["past"]:
        out.append("- This window is already in the past; describe it as a look back.")
    if p["rolled_year"]:
        out.append(f"- The date had already passed this year, so it was read as {start.year}; say so.")
    if w["weighted"]:
        out.append(f"- Read for {w['topic_label']}: days with the Moon in the "
                   f"{', '.join(_ord(h) for h in w['topic_houses'])} house from the Lagna score higher.")
    out.append(f"- Window verdict: {verdict_of(w['score'])[0]} — Moon transit favourable on "
               f"{w['counts']['good']} days, mixed on {w['counts']['mixed']}, take-it-easy on "
               f"{w['counts']['easy']}.")
    ds = w.get("dasha") or {}
    if ds:
        md, ad, pd = ds["maha"], ds["antar"], ds.get("pratyantar")
        out.append(f"- Running dasha: {md['lord']} mahadasha ({fmt_date(md['start'])} to "
                   f"{fmt_date(md['end'])}), {ad['lord']} antardasha ({fmt_date(ad['start'])} to "
                   f"{fmt_date(ad['end'])})"
                   + (f", {pd['lord']} pratyantardasha ({fmt_date(pd['start'])} to "
                      f"{fmt_date(pd['end'])})" if pd else ""))
        for ch in ds.get("changes") or []:
            top = ch["levels"][0]
            out.append(f"- Dasha change on {fmt_date(ch['date'])}: {top} level -> {ch[top]} "
                       f"(now {ch['maha']}/{ch['antar']}/{ch['pratyantar']})")
    for d in w["best"]:
        out.append(f"- Best day {fmt_date(d['date'])} ({d['date']:%A}): {day_reason(d, w)}")
    for d in w["caution"]:
        out.append(f"- Caution day {fmt_date(d['date'])} ({d['date']:%A}): {day_reason(d, w)}")
    for s in w["chandrashtama"]:
        out.append(f"- Chandrashtama from {_t(s['from'], 'en')} to {_t(s['until'], 'en')}")
    if len(w["days"]) <= 31:
        for d in w["days"]:
            out.append(f"- {fmt_date(d['date'])}: Moon {SIGNS[d['main_sign']]} "
                       f"({_ord(d['moon_house'])} from Moon, {d['tone']}), {d['tara']} tara"
                       + f"; overall {d['net']}"
                       + (", Chandrashtama" if d["chandrashtama"] else ""))
    for s in w["slow"]:
        ev = "; ".join(
            (f"enters {SIGNS[e['sign']]} on {fmt_date(e['date'])}" if e["kind"] == "ingress"
             else f"turns {'retrograde' if e['kind'] == 'retrograde' else 'direct'} on {fmt_date(e['date'])}")
            for e in s["events"])
        out.append(f"- {s['planet']} in {SIGNS[s['sign']]}"
                   + (" (retrograde)" if s["retrograde"] and s["planet"] in ("Saturn", "Jupiter") else "")
                   + f", {_ord(s['from_moon'])} from Moon, {_ord(s['from_lagna'])} from Lagna "
                   f"({slow_quality(s['planet'], s['from_moon'])})" + (f"; {ev}" if ev else ""))
    ss = w.get("sade_sati") or {}
    if ss.get("running"):
        out.append(f"- Sade Sati running, phase {ss.get('phase')} ({ss.get('phase_name')})")
    elif ss.get("dhaiya"):
        out.append(f"- Saturn Dhaiya running: {ss.get('dhaiya_name')}")
    for o in (w.get("observances") or [])[:12]:
        name = o["name"]
        if o.get("until"):
            name = f"Sharad Navratri {fmt_date(o['date'])} to {fmt_date(o['until'])}"
        out.append(f"- Observance {fmt_date(o['date'])}: {name}")
    return ("\nDate-window evidence (the question is about these dates — use only these; "
            "do not invent others):\n" + "\n".join(out) + "\n")
