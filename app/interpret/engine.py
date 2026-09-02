"""The analysis engine.

Given a natal chart and a question, this module:

  1. routes the question to a topic and an intent (``topics.classify``),
  2. gathers *evidence* — specific, cited chart factors relevant to that topic,
  3. scores those factors into a verdict,
  4. composes an answer that quotes the factors it used.

No text is produced that is not backed by an evidence item, and every evidence
item carries the exact placement it came from. That is what keeps the output
honest: if you disagree with the answer, you can see precisely which chart
factor produced it.
"""

from __future__ import annotations

import datetime as dt
import logging
import re
from dataclasses import dataclass, field, asdict
from zoneinfo import ZoneInfo

from ..chart_service import (
    ALL_PLANETS, BENEFICS, DOMICILE, MALEFICS, ChartSession,
    dms, house_of, timing_snapshot, transit_chart, transits,
)
from . import knowledge as kb
from .topics import Routing, Topic, classify

_log = logging.getLogger(__name__)

# --------------------------------------------------------------------------
# Scoring
# --------------------------------------------------------------------------

DIGNITY_POINTS = {
    "domicile": 2.0, "rulership": 2.0, "exaltation": 2.0, "triplicity": 1.0,
    "term": 0.5, "bound": 0.5, "face": 0.25, "decan": 0.25,
    "peregrine": -0.5, "detriment": -2.0, "fall": -2.0,
}
PLACEMENT_POINTS = {"angular": 1.0, "succedent": 0.25, "cadent": -0.5}
SOLAR_POINTS = {"cazimi": 1.5, "combust": -1.5, "under the beams": -0.5, "free": 0.0, "n/a": 0.0}


@dataclass
class Evidence:
    text: str
    score: float                 # -3 .. +3, signed contribution
    weight: float                # importance multiplier
    factor: str                  # short machine-ish label, e.g. "10th ruler"
    detail: str = ""             # the raw placement it came from

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Analysis:
    question: str
    topic: str
    topic_label: str
    intent: str
    verdict: str
    score: float
    answer: str
    evidence: list[Evidence] = field(default_factory=list)
    timing: dict = field(default_factory=dict)
    used: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["evidence"] = [e.to_dict() for e in self.evidence]
        return d


def planet_strength(session: ChartSession, name: str) -> tuple[float, list[str]]:
    """Traditional condition of a planet, as a signed score plus reasons."""
    o = session.obj(name)
    if o is None or o["kind"] != "planet":
        return 0.0, []

    score, notes = 0.0, []

    for dig in o.get("dignities", []):
        pts = DIGNITY_POINTS.get(str(dig).lower())
        if pts:
            score += pts
            notes.append(kb.DIGNITY_TEXT.get(str(dig).lower(), str(dig)))

    score += PLACEMENT_POINTS[o["placement"]]
    notes.append(kb.PLACEMENT_TEXT[o["placement"]])

    solar = o.get("solar_phase", "free")
    score += SOLAR_POINTS.get(solar, 0.0)
    if solar not in ("free", "n/a"):
        notes.append(kb.SOLAR_PHASE_TEXT[solar])

    if o["retrograde"] and name not in ("Uranus", "Neptune", "Pluto"):
        score -= 0.5
        notes.append("retrograde, so it works inwardly and revisits things")

    if o.get("sect_status") in ("of the sect", "sect light"):
        score += 0.75
        notes.append("of the sect in favour, so it behaves at its best")
    elif o.get("sect_status") == "contrary to sect":
        score -= 0.5
        notes.append("contrary to sect, so it behaves at its more difficult")

    benefic_help = malefic_harm = 0.0
    for a in session.aspects_to(name):
        other = a["b"] if a["a"] == name else a["a"]
        if other not in ALL_PLANETS:
            continue
        strength = a["strength"]
        if other in BENEFICS:
            if a["nature"] in ("harmonious", "fusing"):
                benefic_help += 0.9 * strength
            elif a["nature"] == "hard":
                benefic_help += 0.3 * strength
        elif other in MALEFICS:
            if a["nature"] == "hard":
                malefic_harm += 0.9 * strength
            elif a["nature"] == "fusing":
                malefic_harm += 0.7 * strength
            else:
                malefic_harm += 0.15 * strength

    benefic_help, malefic_harm = min(benefic_help, 1.5), min(malefic_harm, 1.5)
    score += benefic_help - malefic_harm
    if benefic_help > 0.4:
        notes.append("supported by aspect from a benefic")
    if malefic_harm > 0.4:
        notes.append("pressured by aspect from a malefic")

    return max(-3.0, min(3.0, score)), notes


def describe(session: ChartSession, name: str) -> str:
    """'Mercury at 8°02′ Taurus in the 8th house, retrograde'."""
    o = session.obj(name)
    if o is None:
        return name
    bits = [f"**{name}** at {o['dms']} {o['sign']}"]
    if o["kind"] != "angle":
        bits.append(f"in the {_ord(o['house'])} house")
    if o.get("retrograde"):
        bits.append("retrograde")
    return " ".join(bits)


def _ord(n: int) -> str:
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def _condition_phrase(session: ChartSession, name: str) -> str:
    _, notes = planet_strength(session, name)
    return "; ".join(notes[:3]) if notes else "in average condition"


# --------------------------------------------------------------------------
# Evidence gathering
# --------------------------------------------------------------------------

def house_evidence(session: ChartSession, hnum: int, weight: float) -> list[Evidence]:
    """Read one house: its sign, its ruler's condition, and its occupants."""
    out: list[Evidence] = []
    sign_name = session.house_sign(hnum)
    ruler = session.house_ruler(hnum)
    hk = kb.house(hnum)

    ruler_obj = session.obj(ruler)
    rscore, rnotes = planet_strength(session, ruler)
    if ruler_obj:
        out.append(Evidence(
            text=(
                f"{sign_name} is on your {_ord(hnum)} house, so **{ruler}** rules "
                f"{hk['field']}. It sits at {ruler_obj['dms']} {ruler_obj['sign']} in the "
                f"{_ord(ruler_obj['house'])} house — {'; '.join(rnotes[:3]) or 'in average condition'}. "
                f"That routes this part of your life through "
                f"{kb.house(ruler_obj['house'])['field']}."
            ),
            score=rscore,
            weight=weight * 1.4,
            factor=f"{_ord(hnum)} ruler",
            detail=f"{ruler} {ruler_obj['position']} H{ruler_obj['house']}",
        ))

    for occ in session.planets_in_house(hnum):
        name = occ["name"]
        oscore, onotes = planet_strength(session, name)
        pk = kb.planet(name)
        polarity = "helps" if name in BENEFICS else "pressures" if name in MALEFICS else "colours"
        out.append(Evidence(
            text=(
                f"**{name}** sits in the {_ord(hnum)} house itself, at {occ['dms']} "
                f"{occ['sign']}. {pk['core'].capitalize()} — it {polarity} this area directly. "
                f"Condition: {'; '.join(onotes[:2]) or 'average'}."
            ),
            score=oscore * (1.0 if name in BENEFICS | MALEFICS else 0.6),
            weight=weight,
            factor=f"{name} in {_ord(hnum)}",
            detail=f"{name} {occ['position']}",
        ))

    if not session.planets_in_house(hnum):
        out.append(Evidence(
            text=(
                f"No planet occupies your {_ord(hnum)} house, which is normal — with only ten "
                f"bodies most houses are empty. The matter is read from {ruler} instead."
            ),
            score=0.0, weight=0.15, factor=f"{_ord(hnum)} empty",
            detail=f"{sign_name} on cusp",
        ))
    return out


def significator_evidence(session: ChartSession, name: str, topic: Topic,
                          weight: float) -> Evidence | None:
    o = session.obj(name)
    if o is None or o["kind"] != "planet":
        return None
    score, notes = planet_strength(session, name)
    pk, sk = kb.planet(name), kb.sign(o["sign"])
    return Evidence(
        text=(
            f"**{name}**, the natural significator of {topic.label}, is at {o['dms']} "
            f"{o['sign']} in the {_ord(o['house'])} house. It {pk['verb']} "
            f"{sk['style']}, applied to {kb.house(o['house'])['field']}. "
            f"{'; '.join(notes[:2]).capitalize() or 'Condition is average'}."
        ),
        score=score,
        weight=weight,
        factor=f"{name} (significator)",
        detail=f"{name} {o['position']} H{o['house']}",
    )


def aspect_evidence(session: ChartSession, names: list[str], weight: float,
                    limit: int = 4) -> list[Evidence]:
    """The strongest aspects touching the topic's key planets."""
    seen, out = set(), []
    for a in session.bundle["aspects"]:
        if a["a"] not in names and a["b"] not in names:
            continue
        if a["a"] not in ALL_PLANETS or a["b"] not in ALL_PLANETS:
            continue
        key = tuple(sorted((a["a"], a["b"], a["type"])))
        if key in seen:
            continue
        seen.add(key)
        ak = kb.aspect(a["type"])
        polarity = {"harmonious": 1.0, "fusing": 0.4, "hard": -1.0, "minor": -0.2}[a["nature"]]
        both = {a["a"], a["b"]}
        if both & MALEFICS and a["nature"] == "hard":
            polarity = -1.3
        if both & BENEFICS and a["nature"] in ("harmonious", "fusing"):
            polarity = 1.3
        out.append(Evidence(
            text=(
                f"**{a['a']} {a['type'].lower()} {a['b']}** ({dms(a['orb'])} orb"
                f"{', applying' if a['applying'] else ''}) — {ak['note']}. "
                f"{kb.planet(a['a'])['core'].capitalize()} meets "
                f"{kb.planet(a['b'])['core']}."
            ),
            score=polarity * a["strength"] * 3.0,
            weight=weight * (0.6 + a["strength"]),
            factor=f"{a['a']}–{a['b']} {a['type'].lower()}",
            detail=a["text"],
        ))
        if len(out) >= limit:
            break
    return out


def gather(session: ChartSession, topic: Topic) -> list[Evidence]:
    evidence: list[Evidence] = []
    for i, h in enumerate(topic.primary_houses):
        evidence += house_evidence(session, h, weight=1.0 if i == 0 else 0.7)
    # Slices matched to the largest `Topic` definitions (career: 3 support
    # houses, 5 significators) — a smaller cap here silently dropped real
    # signal for those topics before scoring ever saw it.
    for h in topic.support_houses[:3]:
        evidence += house_evidence(session, h, weight=0.35)

    key_planets = [session.house_ruler(h) for h in topic.primary_houses]
    for i, sig in enumerate(topic.significators[:5]):
        ev = significator_evidence(session, sig, topic, weight=0.9 if i == 0 else 0.55)
        if ev:
            evidence.append(ev)
            key_planets.append(sig)

    evidence += aspect_evidence(session, key_planets, weight=0.6)
    return evidence


def score_of(evidence: list[Evidence]) -> float:
    """Weighted mean of evidence, normalised to -1 .. +1."""
    total_w = sum(e.weight for e in evidence) or 1.0
    raw = sum(e.score * e.weight for e in evidence) / total_w
    return max(-1.0, min(1.0, raw / 2.0))


VERDICTS = [
    (0.42, "Strongly supported", "This is a genuine strength in your chart."),
    (0.15, "Well supported", "The chart backs this, with some work required."),
    (-0.15, "Mixed", "Real potential and real friction, roughly in balance."),
    (-0.42, "Challenged", "This area asks more of you than it gives back easily."),
    (-1.01, "Difficult", "The chart shows sustained resistance here — it can be worked with, but not casually."),
]


def verdict_of(score: float) -> tuple[str, str]:
    for threshold, label, gloss in VERDICTS:
        if score >= threshold:
            return label, gloss
    return VERDICTS[-1][1], VERDICTS[-1][2]


# --------------------------------------------------------------------------
# Timing
# --------------------------------------------------------------------------

def profection_years(session: ChartSession, houses: tuple[int, ...],
                     now: dt.datetime, span: int = 12) -> list[dict]:
    """Ages/years at which an annual profection activates one of these houses."""
    birth = session.birth.local_datetime
    age_now = int((now - birth).days // 365.2425)
    out = []
    for age in range(age_now, age_now + span):
        h = (age % 12) + 1
        if h in houses:
            start = birth.year + age
            out.append({
                "age": age,
                "house": h,
                "sign": session.house_sign(h),
                "lord": session.house_ruler(h),
                "from": f"{_month(birth)} {start}",
                "to": f"{_month(birth)} {start + 1}",
            })
    return out


def _month(d: dt.datetime) -> str:
    return d.strftime("%b")


def _localise(session: ChartSession, moment: dt.datetime) -> dt.datetime:
    """Everything downstream compares against the tz-aware birth moment."""
    if moment.tzinfo is None:
        return moment.replace(tzinfo=ZoneInfo(session.birth.timezone))
    return moment


_MONTHS = ("january", "february", "march", "april", "may", "june", "july",
           "august", "september", "october", "november", "december")


def extract_when(question: str, session: ChartSession,
                 now: dt.datetime) -> tuple[dt.datetime | None, str]:
    """Pull an explicit moment out of the question, if there is one.

    Handles 'in 2012', 'March 2015', 'when I was 25', 'three years ago',
    'next year'. Returns (moment, human label) or (None, '').
    """
    q = question.lower()
    birth = session.birth.local_datetime

    m = re.search(r"\b(" + "|".join(_MONTHS) + r")\s+(19|20)(\d{2})\b", q)
    if m:
        year = int(m.group(2) + m.group(3))
        month = _MONTHS.index(m.group(1)) + 1
        return birth.replace(year=year, month=month, day=15, hour=12, minute=0), \
            f"{m.group(1).capitalize()} {year}"

    m = re.search(r"\b(19[5-9]\d|20[0-4]\d)\b", q)
    if m:
        year = int(m.group(1))
        return birth.replace(year=year, month=7, day=1, hour=12, minute=0), str(year)

    m = re.search(r"\b(?:when i was|at age|aged|age)\s+(\d{1,2})\b", q)
    if m:
        age = int(m.group(1))
        return birth + dt.timedelta(days=age * 365.2425 + 180), f"age {age}"

    m = re.search(r"\b(\d{1,2}|a|one|two|three|four|five|ten)\s+years?\s+ago\b", q)
    if m:
        words = {"a": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "ten": 10}
        n = words.get(m.group(1), 0) or int(m.group(1) or 0)
        return now - dt.timedelta(days=n * 365.2425), f"{n} years ago"

    if re.search(r"\blast year\b", q):
        return now - dt.timedelta(days=365), "last year"
    if re.search(r"\bnext year\b", q):
        return now + dt.timedelta(days=365), "next year"

    return None, ""


def transit_windows(session: ChartSession, topic: Topic, now: dt.datetime,
                    months: int = 48) -> list[dict]:
    """Months in which a slow transit contacts the topic's ruler or house cusp.

    Sampled monthly — Jupiter moves ~2.5°/month and Saturn ~1°/month, so a
    monthly walk with a 2.5° window catches every contact without missing one
    between samples.
    """
    # Keyed by longitude so a planet that is both house ruler and natural
    # significator produces one window, not two identical ones.
    by_degree: dict[float, str] = {}
    for h in topic.primary_houses:
        ruler = session.house_ruler(h)
        ro = session.obj(ruler)
        if ro:
            by_degree.setdefault(round(ro["longitude"], 3),
                                 f"{ruler} (ruler of your {_ord(h)})")
        cusp = round(session.bundle["houses"]["cusps"][h - 1], 3)
        by_degree.setdefault(cusp, f"the cusp of your {_ord(h)} house")
    for sig in topic.significators[:2]:
        so = session.obj(sig)
        if so:
            by_degree.setdefault(round(so["longitude"], 3), f"natal {sig}")
    targets: list[tuple[str, float]] = [(label, lon) for lon, label in by_degree.items()]

    movers = [m for m in topic.timing_movers if m in ("Jupiter", "Saturn", "Uranus", "Neptune", "Pluto")]
    aspects = [("conjunction", 0.0), ("square", 90.0), ("trine", 120.0), ("opposition", 180.0)]
    natal_cusps = session.bundle["houses"]["cusps"]

    found: dict[tuple, dict] = {}
    cursor = now.replace(day=1, hour=12, minute=0, second=0, microsecond=0)
    for step in range(months):
        moment = _add_months(cursor, step)
        tchart = transit_chart(session, moment)
        for mover in movers:
            tp = tchart.get_object(mover)
            if tp is None:
                continue
            t_house = house_of(tp.longitude, natal_cusps)
            if t_house in topic.primary_houses:
                key = (mover, "ingress", t_house)
                found.setdefault(key, {
                    "mover": mover, "kind": "in house",
                    "text": f"transiting {mover} moving through your {_ord(t_house)} house",
                    "from": moment, "to": moment, "quality": _quality(mover, "conjunction"),
                })
                found[key]["to"] = moment
            for label, lon in targets:
                sep = abs(((tp.longitude - lon + 180.0) % 360.0) - 180.0)
                for aname, angle in aspects:
                    if abs(sep - angle) <= 2.5:
                        key = (mover, aname, label)
                        entry = found.setdefault(key, {
                            "mover": mover, "kind": aname,
                            "text": f"transiting {mover} {aname} {label}",
                            "from": moment, "to": moment,
                            "quality": _quality(mover, aname),
                        })
                        entry["to"] = moment
    windows = sorted(found.values(), key=lambda w: w["from"])
    for w in windows:
        w["from"] = w["from"].strftime("%b %Y")
        w["to"] = w["to"].strftime("%b %Y")
    return windows


def releasing_events(session: ChartSession, start: dt.datetime,
                     months: int = 48) -> list[dict]:
    """Months flagged by Zodiacal Releasing as peaks or loosings of the bond.

    These are the strongest event markers in the Hellenistic toolkit — a peak
    period is where the lot's affairs come to a head, and a loosing of the bond
    is an abrupt change of chapter. Consecutive flagged months are merged into
    one window.
    """
    cursor = start.replace(day=1, hour=12, minute=0, second=0, microsecond=0)
    flagged: list[tuple[dt.datetime, str, str]] = []

    for step in range(months):
        moment = _add_months(cursor, step)
        try:
            zr = session.chart.zr_at_date(moment.astimezone(dt.timezone.utc))
        except Exception:
            continue
        kinds = []
        if getattr(zr, "is_peak", False):
            kinds.append("peak")
        if getattr(zr, "is_lb", False):
            kinds.append("loosing of the bond")
        for kind in kinds:
            sign = zr.l2.sign if zr.l2 else (zr.l1.sign if zr.l1 else "")
            flagged.append((moment, kind, sign))

    windows: list[dict] = []
    for moment, kind, sign in flagged:
        if windows and windows[-1]["kind"] == kind and \
                (moment - windows[-1]["_last"]).days <= 62:
            windows[-1]["_last"] = moment
            windows[-1]["to"] = moment
        else:
            windows.append({"kind": kind, "sign": sign, "from": moment,
                            "to": moment, "_last": moment})

    for w in windows:
        w.pop("_last")
        w["text"] = (
            f"Zodiacal Releasing **{w['kind']}** in the {w['sign']} period"
            if w["kind"] == "peak" else
            f"Zodiacal Releasing **loosing of the bond** — an abrupt change of chapter"
        )
        w["from"] = w["from"].strftime("%b %Y")
        w["to"] = w["to"].strftime("%b %Y")
    return windows


def search_periods(session: ChartSession, topic: Topic, start: dt.datetime,
                   end: dt.datetime) -> list[dict]:
    """Find *when* a topic was most strongly activated, rather than being told.

    Walks the range month by month, scoring every technique the chart supports,
    and ranks the years. A year scores on its single strongest month (that is
    what an event looks like — several techniques coinciding) with the yearly
    total as a tiebreaker, so a twelve-month feature such as an annual
    profection cannot outrank a genuine convergence.
    """
    vedic = session.birth.zodiac == "sidereal"
    rulers = {h: session.house_ruler(h) for h in topic.primary_houses}
    key_planets = set(rulers.values()) | set(topic.significators[:3])
    # Occupants of the topic's own houses are significators of it too — central
    # to Vedic dasha judgement, and sound traditionally either way.
    for h in topic.primary_houses:
        key_planets |= {o["name"] for o in session.planets_in_house(h)}

    # Vedic technique does not use the outer planets at all; including them in a
    # sidereal chart manufactures signals the tradition would never read. Uranus
    # crossing the 7th is a disruption marker, not a marriage one.
    movers = ("Jupiter", "Saturn") if vedic else ("Jupiter", "Saturn", "Uranus", "Pluto")
    cusps = session.bundle["houses"]["cusps"]
    house_signs = {h: session.house_sign(h) for h in topic.primary_houses}

    targets: list[tuple[str, float]] = []
    seen_lon: set[float] = set()
    for h in topic.primary_houses:
        for label, lon in ((f"the cusp of your {_ord(h)}", cusps[h - 1]),
                           (f"{rulers[h]}, ruler of your {_ord(h)}",
                            (session.obj(rulers[h]) or {}).get("longitude"))):
            if lon is not None and round(lon, 2) not in seen_lon:
                seen_lon.add(round(lon, 2))
                targets.append((label, lon))
    for sig in topic.significators[:2]:
        so = session.obj(sig)
        if so and round(so["longitude"], 2) not in seen_lon:
            seen_lon.add(round(so["longitude"], 2))
            targets.append((f"natal {sig}", so["longitude"]))

    def score_month(moment: dt.datetime, with_monthly: bool) -> tuple[float, list[str]]:
        # Scored per technique family, so that one family running all year
        # cannot outweigh several families converging in a single month.
        fam = {"profection": 0.0, "releasing": 0.0, "transit": 0.0, "dasha": 0.0}
        reasons: list[str] = []

        # --- profections -------------------------------------------------
        # The monthly profection costs ~25ms against ~0ms for the annual, so it
        # is only computed on the second pass over the shortlisted years.
        try:
            result = session.chart.profection(
                date=moment.replace(tzinfo=None).isoformat(),
                include_monthly=with_monthly)
            annual, monthly = result if with_monthly else (result, None)
            if annual.profected_house in topic.primary_houses:
                fam["profection"] += 3.0
                reasons.append(
                    f"annual profection to the {_ord(annual.profected_house)} house "
                    f"(lord {annual.ruler})")
            if annual.ruler in key_planets:
                fam["profection"] += 1.0
                reasons.append(f"lord of the year is {annual.ruler}, a key significator")
            if monthly is not None and monthly.profected_house in topic.primary_houses:
                fam["profection"] += 1.5
                reasons.append(
                    f"monthly profection to the {_ord(monthly.profected_house)} house")
        except Exception:
            # Visibility only — a failure here just drops profection's
            # contribution to this month's score with no other signal that
            # it happened, silently ranking candidate years on fewer
            # techniques than intended.
            _log.warning("search_periods: profection failed for %s", moment, exc_info=True)

        # --- zodiacal releasing ------------------------------------------
        try:
            zr = session.chart.zr_at_date(moment.astimezone(dt.timezone.utc))
            if getattr(zr, "is_peak", False):
                fam["releasing"] += 2.5
                reasons.append("Zodiacal Releasing peak period")
            if getattr(zr, "is_lb", False):
                fam["releasing"] += 1.5
                reasons.append("Zodiacal Releasing loosing of the bond")
            if zr.l2 and zr.l2.sign in house_signs.values():
                fam["releasing"] += 1.2
                house = next(h for h, s in house_signs.items() if s == zr.l2.sign)
                reasons.append(
                    f"releasing into {zr.l2.sign} — the sign on your {_ord(house)} house")
        except Exception:
            _log.warning("search_periods: zodiacal releasing failed for %s", moment, exc_info=True)

        # --- slow transits -----------------------------------------------
        try:
            tchart = transit_chart(session, moment)
        except Exception:
            tchart = None
        if tchart is not None:
            for mover in movers:
                tp = tchart.get_object(mover)
                if tp is None:
                    continue
                t_house = house_of(tp.longitude, cusps)
                if t_house in topic.primary_houses:
                    # Jupiter crossing the house is the classic opener; the
                    # malefic and the outers passing through are not.
                    bonus = {"Jupiter": 2.0, "Saturn": 0.8}.get(mover, 0.3)
                    fam["transit"] += bonus
                    reasons.append(
                        f"transiting {mover} moving through your {_ord(t_house)} house")
                for label, lon in targets:
                    sep = abs(((tp.longitude - lon + 180.0) % 360.0) - 180.0)
                    for aname, angle, w_jup, w_other in (
                        ("conjunct", 0.0, 2.5, 1.0),
                        ("trine", 120.0, 1.5, 0.5),
                        # In Vedic drishti Jupiter's 7th aspect is full strength,
                        # so an opposition counts for as much as a trine.
                        ("opposite", 180.0, 1.5 if vedic else 0.4, 0.6),
                        ("sextile", 60.0, 0.8, 0.3),
                        ("square", 90.0, 0.4, 0.6),
                    ):
                        if abs(sep - angle) <= 2.0:
                            fam["transit"] += w_jup if mover == "Jupiter" else w_other
                            reasons.append(f"transiting {mover} {aname} {label}")

        # --- vimshottari (sidereal charts) -------------------------------
        if vedic:
            try:
                from ..chart_service import vimshottari
                v = vimshottari(session, moment)
                md = (v.get("mahadasha") or {}).get("lord")
                ad = (v.get("antardasha") or {}).get("lord")
                if md in key_planets:
                    fam["dasha"] += 2.0
                    reasons.append(f"{md} mahadasha — a key significator")
                if ad in key_planets:
                    fam["dasha"] += 2.0
                    reasons.append(f"{ad} antardasha — a key significator")
            except Exception:
                _log.warning("search_periods: vimshottari failed for %s", moment, exc_info=True)

        active = sum(1 for v in fam.values() if v > 0)
        return sum(fam.values()) * (1.0 + 0.3 * max(0, active - 1)), reasons

    cursor = start.replace(day=1, hour=12, minute=0, second=0, microsecond=0)
    total_months = max(0, (end.year - cursor.year) * 12 + (end.month - cursor.month)) + 1

    def walk(steps: list[int], with_monthly: bool) -> dict[int, dict]:
        acc: dict[int, dict] = {}
        for step in steps:
            moment = _add_months(cursor, step)
            score, reasons = score_month(moment, with_monthly)
            entry = acc.setdefault(moment.year, {
                "year": moment.year, "peak": 0.0, "total": 0.0,
                "reasons": {}, "peak_month": "",
            })
            entry["total"] += score
            if score > entry["peak"]:
                entry["peak"] = score
                entry["peak_month"] = moment.strftime("%B")
            for r in reasons:
                entry["reasons"].setdefault(r, []).append(moment.strftime("%b"))
        return acc

    years = walk(list(range(total_months)), with_monthly=False)

    # Second pass: re-score the shortlist with the expensive monthly profection,
    # so the ordering at the top is computed on the full technique set.
    shortlist = {y["year"] for y in
                 sorted(years.values(), key=lambda y: (-y["peak"], -y["total"]))[:5]}
    refine = [s for s in range(total_months)
              if _add_months(cursor, s).year in shortlist]
    years.update(walk(refine, with_monthly=True))

    ranked = sorted(years.values(), key=lambda y: (-y["peak"], -y["total"]))
    for y in ranked:
        y["peak"] = round(y["peak"], 2)
        y["total"] = round(y["total"], 1)
        # Keep the reasons that actually distinguish the year, longest run first.
        y["top_reasons"] = [
            f"{r} ({months[0]}–{months[-1]})" if len(months) > 1 else f"{r} ({months[0]})"
            for r, months in sorted(y["reasons"].items(), key=lambda kv: -len(kv[1]))[:6]
        ]
        del y["reasons"]
    return ranked


def _quality(mover: str, aspect: str) -> str:
    if mover == "Jupiter":
        return "opening" if aspect in ("conjunction", "trine") else "expansive but unfocused"
    if mover == "Saturn":
        return "consolidating" if aspect in ("conjunction", "trine") else "restrictive, a test"
    if mover == "Uranus":
        return "disruptive, sudden"
    if mover == "Neptune":
        return "blurring, idealising"
    return "transformative, non-negotiable"


def _add_months(d: dt.datetime, n: int) -> dt.datetime:
    month = d.month - 1 + n
    return d.replace(year=d.year + month // 12, month=month % 12 + 1)


def monthly_profection_hits(session: ChartSession, topic: Topic,
                            around: dt.datetime) -> list[dict]:
    """Months in the surrounding year whose monthly profection lands on the topic.

    The annual profection is the headline, but a monthly profection into the
    relevant house is what dates an event inside that year.
    """
    hits = []
    start = _add_months(around.replace(day=1, hour=12, minute=0, second=0, microsecond=0), -6)
    for step in range(18):
        moment = _add_months(start, step)
        try:
            annual, monthly = session.chart.profection(
                date=moment.replace(tzinfo=None).isoformat())
        except Exception:
            continue
        if monthly.profected_house in topic.primary_houses:
            hits.append({
                "month": moment.strftime("%b %Y"),
                "house": monthly.profected_house,
                "sign": monthly.profected_sign,
                "lord": monthly.ruler,
                "annual_house": annual.profected_house,
                "annual_lord": annual.ruler,
            })
    return hits


def timing_block(session: ChartSession, topic: Topic, now: dt.datetime,
                 deep: bool, mode: str = "forward") -> dict:
    snap = timing_snapshot(session, now)
    block = {"snapshot": snap, "active_transits": [], "profection_years": [],
             "windows": [], "zr_events": [], "monthly_hits": [], "mode": mode}

    relevant = set(topic.significators) | {session.house_ruler(h) for h in topic.primary_houses}
    relevant |= {"Sun", "Moon", "ASC", "MC"}
    hits = transits(session, now)
    block["active_transits"] = [
        h for h in hits
        if h["natal"] in relevant or h["transit_house"] in topic.primary_houses
    ][:8]

    prof = snap.get("profection") or {}
    if prof.get("house") in topic.primary_houses:
        block["profection_active"] = "house"
    elif prof.get("lord_of_year") in relevant:
        block["profection_active"] = "lord"
    else:
        block["profection_active"] = None

    if mode in ("search_past", "search_future"):
        forward = mode == "search_future"
        birth = session.birth.local_datetime
        if forward:
            start, end = now, now + dt.timedelta(days=365 * 15)
        else:
            # Events people ask to date start in adolescence at the earliest.
            start = max(birth + dt.timedelta(days=365 * 14), now - dt.timedelta(days=365 * 40))
            end = now
        block["candidates"] = search_periods(session, topic, start, end)
        block["search_forward"] = forward
        block["search_window"] = f"{start:%Y}–{end:%Y}"
        return block

    if deep and mode == "review":
        # Centre the search on the date asked about rather than on today.
        start = _add_months(now, -6)
        block["windows"] = transit_windows(session, topic, start, months=18)
        block["zr_events"] = releasing_events(session, start, months=18)
        block["monthly_hits"] = monthly_profection_hits(session, topic, now)
    elif deep:
        block["profection_years"] = profection_years(session, topic.primary_houses, now)
        block["windows"] = transit_windows(session, topic, now, months=48)
        block["zr_events"] = releasing_events(session, now, months=48)
    return block


# --------------------------------------------------------------------------
# Composition
# --------------------------------------------------------------------------

def _search_prose(ranked: list[dict], topic: Topic, forward: bool,
                  window: str) -> list[str]:
    """Present the ranked candidate years for an event the user has not dated."""
    if not ranked:
        return ["I could not scan a usable range for that question."]

    lines: list[str] = []
    best = ranked[0]
    runner = ranked[1] if len(ranked) > 1 else None

    # How far clear the leader is. Anything under ~12% is a cluster, not an
    # answer, and saying so is more useful than a confident wrong year.
    separation = ((best["peak"] - runner["peak"]) / best["peak"]) if runner and best["peak"] else 1.0
    decisive = separation >= 0.12

    if decisive:
        lines.append(
            f"Scanning {window} for {topic.label}, one year stands clear: **{best['year']}**, "
            f"strongest around **{best['peak_month']} {best['year']}**."
        )
    else:
        cluster = ", ".join(str(y["year"]) for y in ranked[:3])
        lines.append(
            f"Scanning {window} for {topic.label}, the chart gives a **cluster, not a single "
            f"year**: {cluster} score within {separation * 100:.0f}% of each other. "
            f"Be sceptical of the ordering — treat all three as live candidates."
        )

    for i, y in enumerate(ranked[:3]):
        rank = (["Most likely", "Second", "Third"][i] if decisive
                else ["Candidate", "Candidate", "Candidate"][i])
        bullets = "\n".join(f"  - {r}" for r in y["top_reasons"])
        lines.append(
            f"**{rank} — {y['year']}** (convergence {y['peak']}, peaking in "
            f"{y['peak_month']}):\n{bullets}")

    runners = ", ".join(str(y["year"]) for y in ranked[3:6])
    if runners:
        lines.append(f"Next after those: {runners}.")

    lines.append(
        f"**On how much to trust this:** dating an event backwards from the chart alone is "
        f"the hardest thing in this app. It narrows {window} to a shortlist — genuinely "
        f"better than chance — but it does not pinpoint. Tell me the actual year "
        f"(*\"it was 2012\"*) and I will show you exactly which techniques fired, which is "
        f"the part worth keeping."
    )
    return lines


def _opening(session: ChartSession, topic: Topic, verdict: str, gloss: str) -> str:
    return f"**{verdict} — {topic.label}.** {gloss}"


def _self_portrait(session: ChartSession) -> list[str]:
    asc = session.obj("ASC")
    sun, moon = session.obj("Sun"), session.obj("Moon")
    asc_ruler = session.house_ruler(1)
    ro = session.obj(asc_ruler)
    dist = session.bundle["distribution"]

    lines = [
        f"**Rising {asc['sign']} ({asc['dms']}).** {kb.RISING[asc['sign']]}",
        f"Your chart ruler is **{asc_ruler}**, at {ro['dms']} {ro['sign']} in the "
        f"{_ord(ro['house'])} house — {_condition_phrase(session, asc_ruler)}. "
        f"That means the thread of your life runs through "
        f"{kb.house(ro['house'])['field']}.",
        f"**Sun in {sun['sign']}, {_ord(sun['house'])} house** — {kb.SUN_SIGN[sun['sign']]}, "
        f"and you do it in the arena of {kb.house(sun['house'])['field']}.",
        f"**Moon in {moon['sign']}, {_ord(moon['house'])} house** — {kb.MOON_SIGN[moon['sign']]}. "
        f"Emotionally you are fed or starved by {kb.house(moon['house'])['field']}.",
    ]

    el = dist["elements"]
    dominant = dist["dominant_element"]
    missing = dist["missing_elements"]
    balance = (
        f"**Elemental balance:** {el['Fire']} Fire, {el['Earth']} Earth, {el['Air']} Air, "
        f"{el['Water']} Water — dominantly **{dominant}**, mostly **{dist['dominant_modality']}**."
    )
    if missing:
        balance += (
            f" You have no planets in **{', '.join(missing)}**, which usually shows up as either "
            f"a blind spot there or an over-compensating preoccupation with it."
        )
    lines.append(balance)
    return lines


# How the advice should be framed, per topic. Generic "lean into your strength"
# language is wrong for health or obstacles, so each topic gets its own verbs.
GUIDANCE_FRAME = {
    "career": ("Build the career around it — put yourself in roles where {gift} is the thing "
               "being paid for.",
               "Career progress here comes from deliberate positioning rather than momentum.",
               "Advancement will be slower and more earned than it looks from outside."),
    "money": ("Income follows {gift}; that is the channel worth widening.",
              "Money responds to structure here — systems, not windfalls.",
              "Treat money as something to be defended and managed, not assumed."),
    "love": ("Relationships work when {gift} is allowed to lead.",
             "Partnership here takes conscious effort and clear agreements.",
             "Relationships ask real work of you; the pattern repeats until it is named."),
    "family": ("Home and family are a genuine resource — use them as a base.",
               "Domestic life takes tending; it does not run itself.",
               "Family matters carry weight and old history; expect them to need managing."),
    "children": ("This area is fertile; {gift} is what makes it work.",
                 "Creative and family life here rewards patience and planning.",
                 "Timing and expectation both need care here."),
    "health": ("Vitality holds up well; the maintenance that protects it is {gift}.",
               "Health is manageable but not self-maintaining — routine is the lever.",
               "Health needs active management. Regular monitoring beats reacting to crises."),
    "education": ("Study comes naturally through {gift}; formal qualifications are worth pursuing.",
                  "Learning works here with structure and a set schedule.",
                  "Study takes persistence rather than flair; break it into small, repeated steps."),
    "travel": ("Foreign ground genuinely suits you; {gift} travels well.",
               "Moves are workable but need planning and paperwork discipline.",
               "Relocation carries friction; do it with contingency, not on impulse."),
    "spirituality": ("There is real depth available here through {gift}.",
                     "Inner life rewards regular practice more than intensity.",
                     "Solitude and doubt are part of the path here rather than a failure of it."),
    "friends": ("Your network is an asset; {gift} is what makes people back you.",
                "Alliances need tending — they form through contribution, not proximity.",
                "Be selective. Groups cost you more than they return unless chosen carefully."),
    "obstacles": ("You have more capacity to absorb difficulty than most.",
                  "Obstacles here are real but proportionate; meet them procedurally.",
                  "Resistance is a structural feature of this chart. Endurance and allies "
                  "matter more than clever solutions."),
    "timing": ("The current period supports action.",
               "The period is workable — neither push nor stall.",
               "The period rewards consolidation over new commitments."),
}


def _guidance(topic: Topic, score: float, session: ChartSession) -> str:
    ruler = session.house_ruler(topic.primary_houses[0])
    ro = session.obj(ruler)
    pk = kb.planet(ruler)
    sk = kb.sign(ro["sign"]) if ro else {"style": ""}

    frames = GUIDANCE_FRAME.get(topic.key, GUIDANCE_FRAME["timing"])
    band = 0 if score >= 0.15 else 1 if score >= -0.15 else 2
    lead = frames[band].format(gift=pk["gift"])

    mechanism = (
        f"The working part is **{ruler}** at {ro['dms']} {ro['sign']} in your "
        f"{_ord(ro['house'])} house — it {pk['verb']} {sk['style']}. "
        if ro else ""
    )
    watch = f"The failure mode to watch is {pk['shadow']}."
    return f"{lead} {mechanism}{watch}"


def _health_detail(session: ChartSession) -> list[str]:
    """Body-zone specifics — only meaningful for health questions."""
    lines: list[str] = []
    asc = session.obj("ASC")
    asc_ruler = session.house_ruler(1)
    ro = session.obj(asc_ruler)
    lines.append(
        f"**Constitution:** {asc['sign']} rising governs the {kb.SIGN_BODY[asc['sign']]}. "
        f"Its ruler {asc_ruler} is in {ro['sign']}, which brings in the "
        f"{kb.SIGN_BODY[ro['sign']]}."
    )

    for name in ("Mars", "Saturn"):
        o = session.obj(name)
        if not o:
            continue
        if o["house"] in (1, 6, 8, 12):
            pk = kb.planet(name)
            lines.append(
                f"**{name}** — the {'inflammatory, acute' if name == 'Mars' else 'chronic, structural'} "
                f"significator — is in your {_ord(o['house'])} house in {o['sign']}, pointing at the "
                f"{kb.SIGN_BODY[o['sign']]} ({pk['body']})."
            )

    moon = session.obj("Moon")
    mscore, mnotes = planet_strength(session, "Moon")
    lines.append(
        f"**Moon in {moon['sign']}** carries physical rhythm and fluid balance — "
        f"{kb.SIGN_BODY[moon['sign']]}. {'; '.join(mnotes[:2]).capitalize() or 'Condition average'}."
    )
    lines.append(
        "*Astrological health indications are symbolic pattern-reading, not diagnosis. "
        "Anything you are actually worried about belongs with a doctor.*"
    )
    return lines


def _strengths_weaknesses(session: ChartSession) -> list[str]:
    """The best- and worst-conditioned planets, with the reasons for each."""
    scored = []
    for name in ("Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"):
        if session.obj(name):
            scored.append((planet_strength(session, name), name))
    scored.sort(key=lambda s: -s[0][0])

    lines = []
    for (score, notes), name in scored[:2]:
        o = session.obj(name)
        pk = kb.planet(name)
        lines.append(
            f"**Strength — {name}** ({score:+.1f}) at {o['dms']} {o['sign']}, "
            f"{_ord(o['house'])} house: {'; '.join(notes[:2])}. This gives you {pk['gift']}."
        )
    for (score, notes), name in scored[-2:]:
        o = session.obj(name)
        pk = kb.planet(name)
        lines.append(
            f"**Blind spot — {name}** ({score:+.1f}) at {o['dms']} {o['sign']}, "
            f"{_ord(o['house'])} house: {'; '.join(notes[:2])}. Watch for {pk['shadow']}."
        )
    return lines


def _timing_prose(block: dict, topic: Topic, intent: str) -> list[str]:
    snap = block["snapshot"]
    lines: list[str] = []
    past = intent == "review"
    was = "was running" if past else "is running"
    in_force = "Transits in force at that time" if past else "Transits in force right now"
    ahead = "Slow-planet windows across that period" if past else "Windows ahead"

    prof = snap.get("profection") or {}
    if prof and "error" not in prof:
        marker = {
            "house": " — **this is exactly the area you asked about**",
            "lord": " — **and that planet is one of the significators of what you asked about**",
        }.get(block.get("profection_active"), "")
        lines.append(
            f"**Annual profection (age {int(snap['age'])}):** your year {was} through the "
            f"**{_ord(prof['house'])} house** in {prof['sign']}, so **{prof['lord_of_year']}** "
            f"is your lord of the year, sitting natally in your {_ord(prof['lord_house'])} house "
            f"at {prof['lord_position']}{marker}. Whatever that planet touches gets emphasised "
            f"for these twelve months."
        )

    zr = snap.get("zodiacal_releasing")
    if zr and zr.get("l1"):
        l1, l2 = zr["l1"], zr["l2"]
        peak = " This is a **peak period**." if zr.get("is_peak") else ""
        lb = " A **loosing of the bond** falls here — an abrupt change of chapter." if zr.get("is_loosing_bond") else ""
        lines.append(
            f"**Zodiacal releasing from {zr['lot']}:** you are in a {l1['sign']} major chapter "
            f"({l1['start']} – {l1['end']}, ruled by {l1['ruler']}), and within it a {l2['sign']} "
            f"sub-period ({l2['start']} – {l2['end']}, ruled by {l2['ruler']}).{peak}{lb}"
        )

    fd = snap.get("firdaria")
    if fd:
        lines.append(
            f"**Firdaria:** {fd['major']} major period (to {fd['major_until']})"
            + (f", {fd['sub']} sub-period" if fd.get("sub") else "") + "."
        )

    vim = snap.get("vimshottari")
    if vim and vim.get("mahadasha"):
        md, ad = vim["mahadasha"], vim.get("antardasha")
        lines.append(
            f"**Vimshottari dasha:** Moon in **{vim['nakshatra']}** pada {vim['pada']}, so you are "
            f"running **{md['lord']} mahadasha** ({md['start']} – {md['end']})"
            + (f" with **{ad['lord']} antardasha** ({ad['start']} – {ad['end']})." if ad else ".")
        )

    active = block.get("active_transits") or []
    if active:
        bullets = "\n".join(f"  - {h['text']}" for h in active[:5])
        lines.append(f"**{in_force}:**\n{bullets}")

    zr_events = block.get("zr_events") or []
    if zr_events:
        rows = "\n".join(
            f"  - **{w['from']}" + (f" – {w['to']}" if w["to"] != w["from"] else "") +
            f"** — {w['text']}"
            for w in zr_events[:5])
        lines.append(
            f"**Zodiacal Releasing markers** (the strongest event flags in the "
            f"Hellenistic toolkit):\n{rows}")

    hits = block.get("monthly_hits") or []
    if hits:
        rows = "\n".join(
            f"  - **{h['month']}** — monthly profection to the {_ord(h['house'])} house "
            f"in {h['sign']}, lord {h['lord']}"
            for h in hits[:6])
        lines.append(
            f"**Monthly profections onto {topic.label}** — the annual profection sets the "
            f"year's theme, but these months are when it comes due:\n{rows}")

    windows = block.get("windows") or []
    if windows:
        upcoming = "\n".join(
            f"  - **{w['from']}"
            + (f" – {w['to']}" if w["to"] != w["from"] else "")
            + f"** — {w['text']} ({w['quality']})"
            for w in windows[:7]
        )
        lines.append(f"**{ahead}:**\n{upcoming}")

    years = block.get("profection_years") or []
    if years:
        ys = ", ".join(f"age {y['age']} ({y['from']}–{y['to']}, lord {y['lord']})" for y in years[:3])
        lines.append(
            f"**Profection years that put {topic.label} centre-stage:** {ys}."
        )

    if intent in ("timing", "forecast") and not windows and not active:
        lines.append(
            "No major slow-planet contact is close to exact right now, which itself is "
            "information: this is a period of ordinary momentum rather than a turning point."
        )
    return lines


_SW = re.compile(
    r"\b(strengths?|weaknesses?|blind spots?|good at|bad at|talents?|flaws?)\b", re.I)


def compose(session: ChartSession, routing: Routing, evidence: list[Evidence],
            score: float, timing: dict, question: str = "",
            period_label: str = "") -> str:
    topic, intent = routing.topic, routing.intent
    verdict, gloss = verdict_of(score)

    if intent == "search":
        head = [f"**Searching your chart for the year** — {topic.label}.", ""]
    elif intent == "review":
        head = [
            f"**What your chart was doing in {period_label or 'that period'}** — read against "
            f"{topic.label}.", ""
        ]
    else:
        head = [_opening(session, topic, verdict, gloss), ""]
    parts: list[str] = []

    if topic.key == "self":
        parts.append("### Your core signature")
        parts += [f"{line}\n" for line in _self_portrait(session)]
        if _SW.search(question):
            parts.append("### Strongest and weakest hands")
            parts += [f"- {line}" for line in _strengths_weaknesses(session)]
            parts.append("")
    else:
        parts.append(f"### What the chart shows — {topic.blurb}")
        # The ruler of the primary house is the spine of the judgement, so it
        # leads regardless of how loudly the other factors score.
        spine = f"{_ord(topic.primary_houses[0])} ruler"
        lead = [e for e in evidence if e.factor == spine]
        rest = sorted((e for e in evidence if e.factor != spine),
                      key=lambda e: -abs(e.score) * e.weight)
        for e in (lead + rest)[:6]:
            parts.append(f"- {e.text}")
        parts.append("")

        if topic.key == "health":
            parts.append("### Where it shows up in the body")
            parts += [f"- {line}" for line in _health_detail(session)]
            parts.append("")

    timing_parts: list[str] = []
    if intent == "search":
        timing_parts.append("### The years that stand out")
        timing_parts += [f"{p}\n" for p in _search_prose(
            timing.get("candidates") or [], topic,
            timing.get("search_forward", False), timing.get("search_window", ""))]
    elif intent in ("timing", "forecast", "advice", "review") or topic.key == "timing":
        prose = _timing_prose(timing, topic, intent)
        if prose:
            heading = (f"### The time-lords in {period_label}" if intent == "review"
                       else "### Timing")
            timing_parts.append(heading)
            timing_parts += [f"{p}\n" for p in prose]

    # A "when" or "what happened" question wants the clock first and the natal
    # reasoning second.
    if intent in ("timing", "review", "search"):
        parts = timing_parts + ["### Why — the natal basis"] + parts[1:]
    else:
        parts += timing_parts

    if topic.key != "self":
        parts.append("### How to work with it")
        parts.append(_guidance(topic, score, session))
        parts.append("")

    if intent == "review":
        parts.append(
            "> Read backwards like this, astrology is being *checked*, not tested — I already "
            "know the outcome. The honest use of it is to see which techniques flagged the "
            "period, and to trust those more when reading your future."
        )
    elif intent == "forecast":
        parts.append(
            "> A natal chart shows disposition and timing pressure, not certainty. "
            "Read the above as *the conditions you are working in*, not as a fixed outcome."
        )
    elif intent == "advice":
        parts.append(
            "> This is chart-based reasoning, not professional advice. For anything medical, "
            "legal or financial, treat it as one input among several."
        )

    return "\n".join(head + parts).strip()


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------

def analyse(session: ChartSession, question: str,
            now: dt.datetime | None = None) -> Analysis:
    now = _localise(session, now or dt.datetime.now())
    routing = classify(question)
    topic = routing.topic

    # A question may name its own moment ("in 2012", "when I was 25"). If it
    # does, that becomes the reference point instead of today.
    asked_when, period_label = extract_when(question, session, now)
    reference = _localise(session, asked_when) if asked_when else now
    intent = routing.intent
    if asked_when and reference < now and intent not in ("review",):
        intent = "review"          # a named past date is always a look-back
        routing = Routing(topic=topic, intent=intent, score=routing.score,
                          matched=routing.matched, secondary=routing.secondary)
    # A past-tense question with no date to anchor it is really a search — "I
    # got married a few years ago" wants the year found, not today analysed.
    if intent == "review" and asked_when is None:
        intent = "search"
    if intent == "search" and asked_when is not None:
        intent = "review"          # they named the date after all
    if intent == "review" and not period_label:
        period_label = reference.strftime("%B %Y")

    evidence = gather(session, topic)
    score = score_of(evidence)

    deep = intent in ("timing", "forecast", "review") or topic.key == "timing"
    if intent == "search":
        forward = bool(re.search(r"\b(will|going to|shall|future|ahead)\b", question, re.I))
        mode = "search_future" if forward else "search_past"
    else:
        mode = "review" if intent == "review" else "forward"
    timing = timing_block(session, topic, reference, deep=deep, mode=mode)

    # A strongly activated timing picture nudges the verdict, since the question
    # is usually about the present, not the birth chart in the abstract.
    if timing.get("profection_active"):
        score += 0.05
    answer = compose(session, routing, evidence, score, timing, question, period_label)

    used = sorted({e.detail for e in evidence if e.detail})
    return Analysis(
        question=question,
        topic=topic.key,
        topic_label=topic.label,
        intent=intent,
        verdict=verdict_of(score)[0],
        score=round(score, 3),
        answer=answer,
        evidence=sorted(evidence, key=lambda e: -abs(e.score) * e.weight),
        timing=timing,
        used=used,
    )
