"""The detailed Kundali Milan report (DIVASTRO-156): a ₹51 PDF for two people.

Sold under the match result (the in-app matching screen and the public
/kundali-milan pages). It is written for a PAIR, so it cannot hang off a saved
chart the way the single-topic reports and the Life Book do:

  ORDER    billing.create_order(..., milan={"groom": {...}, "bride": {...}, "lang"})
           -> `order_data()` checks both sides (each chart must cast and the two
           must match), and freezes them onto Order.order_data (JSON) together
           with the address the PDF is emailed to (the account's deliverable
           email today; a guest checkout can put its own there later, because
           delivery reads only the ORDER).
  PAID     billing.mark_paid -> `schedule_delivery()`: the PDF is built in a
           background thread and emailed to the order's address, once (the
           order records `emailed_at`).
  DOWNLOAD GET /api/pdf/milan/<order id>?lang=en|hi (main.py): the owner of a
           paid order downloads it any time from My orders.
  SAMPLE   /samples/milan_report.pdf: the same builder on a fixed fictional pair.

CONTENT: every fact in the report is the engine's: the eight kootas exactly as
astro.matching scores them (one by one, with what each koota measures from the
published /kundali-milan text), the total and its conventional band, Manglik dosh
for both and the pair verdict (cancellation when both are Manglik), the key
placements of the two charts and the classical friendships between their lords
(matching's own naisargika table), and the wedding (vivah) dates of the next 15
months from the same engine and almanac as the /muhurat/vivah-<year> pages (New
Delhi). There is no narration model: like the single-topic reports, it is written
by the rule engine, so nothing in it can be invented, re-dated or re-scored, and it
reads the same with or without a model configured. Printed in English or Hindi
(pdf_report._report_language); other languages get the English copy.
"""

from __future__ import annotations

import datetime as dt
import json
import logging
import threading

from . import i18n, pdf_report
from .astro import matching
from .chart_service import DOMICILE, SIGNS, BirthData, build

log = logging.getLogger("astro.milan_report")

SIDES = ("groom", "bride")
MAX_NAME = 60
MAX_PLACE = 120
WEDDING_MONTHS = 15            # this month and the 14 after it
DATES_PER_MONTH = 8            # a month lists at most this many dates (the count is always printed)
_NAME_UNSAFE = str.maketrans({c: " " for c in "*_`#>[]<{}\\|\r\n\t"})


class MilanDataError(ValueError):
    """The two people's details cannot make a report (billing: HTTP 400)."""


# --------------------------------------------------------------------------
# The order's data
# --------------------------------------------------------------------------

def _clean_person(raw: object, side: str) -> dict:
    """One side of the matching form, reduced to what the report needs."""
    if not isinstance(raw, dict):
        raise MilanDataError(f"The {side}'s birth details are missing.")
    try:
        date = dt.date.fromisoformat(str(raw.get("date", "")).strip()).isoformat()
    except ValueError:
        raise MilanDataError(f"The {side}'s date of birth is not a date.") from None
    known = raw.get("time_known", True) is not False
    time = str(raw.get("time") or "12:00").strip()[:5] if known else "12:00"
    try:
        dt.time.fromisoformat(time)
    except ValueError:
        raise MilanDataError(f"The {side}'s time of birth is not a time.") from None
    try:
        lat, lon = float(raw["latitude"]), float(raw["longitude"])
    except (KeyError, TypeError, ValueError):
        raise MilanDataError(f"The {side}'s place of birth has no coordinates.") from None
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise MilanDataError(f"The {side}'s place of birth is out of range.")
    name = " ".join(str(raw.get("name") or "").translate(_NAME_UNSAFE).split())[:MAX_NAME]
    place = " ".join(str(raw.get("place") or "").translate(_NAME_UNSAFE).split())[:MAX_PLACE]
    return {"name": name, "date": date, "time": time, "time_known": known,
            "place": place or f"{lat:.4f}, {lon:.4f}", "latitude": round(lat, 6),
            "longitude": round(lon, 6), "timezone": str(raw.get("timezone") or "").strip()[:64]}


def _birth(p: dict) -> BirthData:
    """The same chart the matching tool casts (api_tools._chart): sidereal, Lahiri,
    whole sign, noon for an unknown time."""
    from . import geo
    return BirthData(
        name=p["name"] or "—", date=p["date"], time=p["time"] if p["time_known"] else "12:00",
        latitude=p["latitude"], longitude=p["longitude"],
        timezone=p["timezone"] or geo.timezone_for(p["latitude"], p["longitude"]),
        place=p["place"], zodiac="sidereal", ayanamsa="lahiri", house_system="Whole Sign",
        time_known=p["time_known"])


def cast(pair: dict) -> tuple:
    """(groom chart, bride chart) for a cleaned pair."""
    return build(_birth(pair["groom"])), build(_birth(pair["bride"]))


def clean_pair(milan: object) -> dict:
    """{"groom", "bride", "lang"} checked: both charts cast and the two match."""
    if not isinstance(milan, dict):
        raise MilanDataError("The Kundali Milan report needs both people's birth details.")
    pair = {side: _clean_person(milan.get(side), side) for side in SIDES}
    lang = str(milan.get("lang") or "en")
    pair["lang"] = lang if lang in ("en", "hi") else "en"
    try:
        groom, bride = cast(pair)
        matching.match(groom, bride)
    except Exception as exc:
        raise MilanDataError(f"Those birth details could not be matched: {exc}") from exc
    return pair


def order_data(milan: object, *, email: str = "") -> str:
    """The JSON frozen onto Order.order_data for a Kundali Milan report."""
    pair = clean_pair(milan)
    return json.dumps({"v": 1, "milan": {s: pair[s] for s in SIDES}, "lang": pair["lang"],
                       "email": (email or "").strip()[:255]}, ensure_ascii=False)


def load(order) -> dict:
    """The order's data ({} when it has none or it is unreadable)."""
    try:
        data = json.loads(getattr(order, "order_data", "") or "{}")
    except ValueError:
        return {}
    return data if isinstance(data, dict) else {}


def order_email(order) -> str:
    """Where this order's report is emailed: the ORDER's address, never the account's
    current one (an order may have no account behind it once guests can buy)."""
    own = (getattr(order, "guest_email", "") or "").strip()  # DIVASTRO-158: a guest order's typed address wins
    return own or str(load(order).get("email") or "").strip()


def pair_label(order) -> str:
    """"Asha & Ravi" for My orders ("" when the names were left out)."""
    milan = load(order).get("milan") or {}
    names = [(milan.get(s) or {}).get("name", "") for s in SIDES]
    return " & ".join(n for n in names if n)


# --------------------------------------------------------------------------
# Text (English and Hindi; the report prints in one of the two)
# --------------------------------------------------------------------------

TEXTS = {
    "en": {
        "title": "Detailed Kundali Milan Report",
        "groom": "Groom", "bride": "Bride", "and": "&",
        "cover_pair": "Match", "cover_score": "Guna Milan", "generated": "Generated",
        "people_title": "The two charts",
        "people_headers": ["", "{groom}", "{bride}"],
        "born": "Born", "place": "Place", "moon": "Moon sign (rashi)", "nakshatra": "Nakshatra",
        "lagna": "Lagna (ascendant)", "time_unknown": "time not known (noon used)",
        "pada": "pada", "d1": "{who} — Rashi chart (D1)",
        "summary_title": "Guna Milan at a glance",
        "total": "Total", "verdict": "Conventional reading",
        "before": "Before cancellation: {n} — {list}",
        "koota_title": "The eight kootas, one by one",
        "koota_headers": ["Koota", "{groom}", "{bride}", "Points"],
        "means": "What it measures",
        "result": "In these two charts",
        "cancelled": "Dosha cancelled",
        "mangal_title": "Manglik dosh",
        "manglik_yes": "**{who}: Manglik** ({severity}). {summary}",
        "manglik_no": "**{who}: not Manglik.** {summary}",
        "relief": "Classical relief in this chart: {list}.",
        "pair": "**For the pair: {verdict}.** {note}",
        "mangal_time": "A birth time is missing for {who}, so noon was used. The 36-point score does not "
                       "depend on it (it is read from the Moon), but the Manglik reading depends on the "
                       "ascendant and should not be relied on here.",
        "planets_title": "Key planetary points of the two charts",
        "planets_headers": ["", "{groom}", "{bride}"],
        "row_lagna": "Lagna and its lord", "row_moon": "Moon sign and its lord",
        "row_venus": "Venus", "row_mars": "Mars", "row_jupiter": "Jupiter",
        "row_seventh": "7th house (marriage) and its lord",
        "in_house": "{sign}, house {house}", "lord_of": "{sign} — lord {lord}",
        "lord_in": "{sign} — lord {lord} in house {house}",
        "rel_moon": "Moon-sign lords {a} ({x}) and {b} ({y}): {a} counts {b} as {r1}; {b} counts {a} as {r2}.",
        "rel_lagna": "Lagna lords {a} ({x}) and {b} ({y}): {a} counts {b} as {r1}; {b} counts {a} as {r2}.",
        "rel_seventh": "7th-house lords {a} ({x}) and {b} ({y}): {a} counts {b} as {r1}; {b} counts {a} as {r2}.",
        "same_lord": "{label}: both are ruled by {a}.",
        "lbl_moon": "Moon-sign lords", "lbl_lagna": "Lagna lords", "lbl_seventh": "7th-house lords",
        "cross_moon": "{x}'s Moon falls in the {n} house counted from {y}'s Lagna.",
        "planets_note": "Friend, neutral and enemy are the classical natural (naisargika) relationships the "
                        "Graha Maitri koota itself uses. The lagna-based lines need a birth time and are left "
                        "out for a chart cast without one.",
        "relations": {"friend": "a friend", "neutral": "neutral", "enemy": "an enemy"},
        "wedding_title": "Wedding (vivah) dates in the coming months",
        "wedding_headers": ["Month", "Dates", "Days"],
        "wedding_none": "no dates",
        "wedding_none_why": "no dates ({why})",
        "wedding_note": "These are the vivah dates of the classical almanac (Muhurta Chintamani rules, "
                        "Lahiri, New Delhi), the same engine and list as our /muhurat/vivah pages: an "
                        "auspicious tithi, weekday and one of the eleven vivah nakshatras, with Chaturmas, "
                        "Kharmas and the combustion of Venus or Jupiter excluded. They are the same for every "
                        "couple — not a personal muhurat — so fix the hour with your family priest.",
        "wedding_more": "and {n} more",
        "about_title": "About this report",
        "about": "Written by our rule engine from the two birth charts: the Ashtakoot tables, the Mangal "
                 "dosha rules and the almanac above, exactly as the free matching tool computes them. No AI "
                 "model writes or changes any of it. Ashtakoot is a traditional convention, not a "
                 "measurement, and it should not be the deciding input on a marriage.",
        "subject": "{a} & {b}",
        "omit_wedding": "The wedding dates could not be computed for this copy.",
    },
    "hi": {
        "title": "विस्तृत कुंडली मिलान रिपोर्ट",
        "groom": "वर", "bride": "कन्या", "and": "एवं",
        "cover_pair": "मिलान", "cover_score": "गुण मिलान", "generated": "तिथि",
        "people_title": "दोनों की कुंडली",
        "people_headers": ["", "{groom}", "{bride}"],
        "born": "जन्म", "place": "जन्म स्थान", "moon": "चंद्र राशि", "nakshatra": "नक्षत्र",
        "lagna": "लग्न", "time_unknown": "जन्म समय ज्ञात नहीं (दोपहर 12 बजे लिया गया)",
        "pada": "पाद", "d1": "{who} — लग्न कुंडली (D1)",
        "summary_title": "गुण मिलान एक नज़र में",
        "total": "कुल गुण", "verdict": "पारंपरिक अर्थ",
        "before": "परिहार से पहले: {n} — {list}",
        "koota_title": "आठों कूट, एक-एक करके",
        "koota_headers": ["कूट", "{groom}", "{bride}", "गुण"],
        "means": "क्या देखा जाता है",
        "result": "इन दोनों कुंडलियों में",
        "cancelled": "दोष का परिहार",
        "mangal_title": "मांगलिक दोष",
        "manglik_yes": "**{who}: मांगलिक** ({severity})। {summary}",
        "manglik_no": "**{who}: मांगलिक नहीं।** {summary}",
        "relief": "इस कुंडली में शास्त्रीय परिहार: {list}।",
        "pair": "**दोनों के लिए: {verdict}।** {note}",
        "mangal_time": "{who} का जन्म समय उपलब्ध न होने से दोपहर 12:00 का समय लिया गया है। 36 गुण मिलान चंद्र "
                       "पर आधारित होने से सटीक है, किंतु मांगलिक विचार लग्न पर निर्भर होने से सांकेतिक है।",
        "planets_title": "दोनों कुंडलियों के मुख्य ग्रह-संबंध",
        "planets_headers": ["", "{groom}", "{bride}"],
        "row_lagna": "लग्न और लग्नेश", "row_moon": "चंद्र राशि और राशीश",
        "row_venus": "शुक्र", "row_mars": "मंगल", "row_jupiter": "गुरु",
        "row_seventh": "सप्तम भाव (विवाह) और सप्तमेश",
        "in_house": "{sign}, {house}वाँ भाव", "lord_of": "{sign} — स्वामी {lord}",
        "lord_in": "{sign} — स्वामी {lord}, {house}वें भाव में",
        "rel_moon": "राशि स्वामी {a} ({x}) और {b} ({y}): {a} के लिए {b} {r1} हैं; {b} के लिए {a} {r2} हैं।",
        "rel_lagna": "लग्नेश {a} ({x}) और {b} ({y}): {a} के लिए {b} {r1} हैं; {b} के लिए {a} {r2} हैं।",
        "rel_seventh": "सप्तमेश {a} ({x}) और {b} ({y}): {a} के लिए {b} {r1} हैं; {b} के लिए {a} {r2} हैं।",
        "same_lord": "{label}: दोनों के स्वामी {a} हैं।",
        "lbl_moon": "राशि स्वामी", "lbl_lagna": "लग्नेश", "lbl_seventh": "सप्तमेश",
        "cross_moon": "{x} का चंद्र {y} के लग्न से {n} भाव में पड़ता है।",
        "planets_note": "मित्र, सम और शत्रु ग्रहों के वही नैसर्गिक संबंध हैं जिनसे ग्रह मैत्री कूट के गुण बनते हैं। "
                        "लग्न पर आधारित पंक्तियों के लिए जन्म समय चाहिए; जिस कुंडली का जन्म समय ज्ञात नहीं, उसके लिए वे छोड़ दी गई हैं।",
        "relations": {"friend": "मित्र", "neutral": "सम", "enemy": "शत्रु"},
        "wedding_title": "आने वाले महीनों के विवाह मुहूर्त",
        "wedding_headers": ["महीना", "तिथियाँ", "दिन"],
        "wedding_none": "कोई नहीं",
        "wedding_none_why": "कोई नहीं ({why})",
        "wedding_note": "ये शास्त्रीय पंचांग (मुहूर्त चिंतामणि के नियम, लाहिड़ी, नई दिल्ली) की विवाह तिथियाँ हैं, वही गणना "
                        "और सूची जो हमारे /muhurat/vivah पृष्ठों पर है: शुभ तिथि, शुभ वार और विवाह के ग्यारह नक्षत्रों में "
                        "से एक, तथा चातुर्मास, खरमास और शुक्र या गुरु के अस्त काल को छोड़कर। ये हर दंपती के लिए "
                        "समान हैं, व्यक्तिगत मुहूर्त नहीं; समय अपने कुल पुरोहित से निश्चित कराएँ।",
        "wedding_more": "और {n}",
        "about_title": "इस रिपोर्ट के बारे में",
        "about": "यह रिपोर्ट हमारे नियम-आधारित इंजन ने दोनों जन्म कुंडलियों से बनाई है: अष्टकूट सारणियाँ, मंगल दोष के नियम "
                 "और ऊपर का पंचांग, ठीक वैसे ही जैसे मुफ़्त मिलान टूल गणना करता है। इसका कोई भी अंश किसी AI मॉडल ने न "
                 "लिखा है, न बदला है। अष्टकूट एक पारंपरिक पद्धति है, माप नहीं; यह विवाह के निर्णय का एकमात्र आधार नहीं होना चाहिए।",
        "subject": "{a} एवं {b}",
        "omit_wedding": "इस प्रति में विवाह मुहूर्त की गणना नहीं हो सकी।",
    },
}

_VALUE_HI = {**matching.VARNA_HI, **matching.VASHYA_HI, **matching.TARA_HI,
             **matching.GANA_HI, **matching.NADI_HI, **matching.PLANET_HI}


def _hi_value(v: str) -> str:
    return _VALUE_HI.get(v) or matching.YONI_HI.get(v) or matching.SIGNS_HI.get(v) or v


def _ordinal(n: int, lang: str) -> str:
    return f"{n}वें" if lang == "hi" else matching._ordinal(n)


# --------------------------------------------------------------------------
# The report's facts, all from the engine
# --------------------------------------------------------------------------

def _koota_cells(k: dict, lang: str) -> tuple[str, str]:
    """What each side contributes to this koota, as the engine reports it."""
    key = k["key"]
    hi = lang == "hi"
    v = (lambda x: _hi_value(str(x))) if hi else (lambda x: str(x))
    if key == "tara":
        return (f"{k['groom_to_bride']} · {v(k['groom_to_bride_name'])}",
                f"{k['bride_to_groom']} · {v(k['bride_to_groom_name'])}")
    if key == "yoni":
        return v(k["groom_yoni"]), v(k["bride_yoni"])
    if key == "graha_maitri":
        return v(k["groom_lord"]), v(k["bride_lord"])
    if key == "bhakoot":
        return str(k["groom_to_bride"]), str(k["bride_to_groom"])
    field = {"varna": "varna", "vashya": "vashya", "gana": "gana", "nadi": "nadi"}[key]
    return v(k[f"groom_{field}"]), v(k[f"bride_{field}"])


def _num(x: float) -> str:
    return f"{x:g}"


def _lord_rel(T: dict, kind: str, a: str, b: str, x: str, y: str, lang: str) -> str:
    hi = lang == "hi"
    name = (lambda p: matching.PLANET_HI.get(p, p)) if hi else (lambda p: p)
    if a == b:
        return T["same_lord"].format(label=T[f"lbl_{kind}"], a=name(a))
    rels = T["relations"]
    return T[f"rel_{kind}"].format(a=name(a), b=name(b), x=x, y=y,
                                   r1=rels[matching._relation(a, b)], r2=rels[matching._relation(b, a)])


def _sign(s: str, lang: str) -> str:
    return matching.SIGNS_HI.get(s, s) if lang == "hi" else s


def _planet(p: str, lang: str) -> str:
    return matching.PLANET_HI.get(p, p) if lang == "hi" else p


def _placements(chart, time_known: bool, lang: str, T: dict) -> dict:
    """The rows of the key-placements table for one chart."""
    objs = chart.bundle["objects"]
    asc = objs["ASC"]["sign"]
    seventh = SIGNS[(SIGNS.index(asc) + 6) % 12]
    lord7 = DOMICILE[seventh]
    moon = objs["Moon"]["sign"]
    dash = "—"

    def at(p: str) -> str:
        o = objs.get(p)
        if not o:
            return dash
        return T["in_house"].format(sign=_sign(o["sign"], lang), house=o["house"]) if time_known \
            else _sign(o["sign"], lang)

    return {
        "lagna": (T["lord_of"].format(sign=_sign(asc, lang), lord=_planet(DOMICILE[asc], lang))
                  if time_known else dash),
        "moon": T["lord_of"].format(sign=_sign(moon, lang), lord=_planet(DOMICILE[moon], lang)),
        "venus": at("Venus"), "mars": at("Mars"), "jupiter": at("Jupiter"),
        "seventh": (T["lord_in"].format(sign=_sign(seventh, lang), lord=_planet(lord7, lang),
                                        house=objs[lord7]["house"]) if time_known else dash),
        "_asc": asc, "_lord7": lord7, "_moon": moon,
    }


def wedding_months(today: dt.date, lang: str, months: int = WEDDING_MONTHS) -> list[list[str]]:
    """[[month, dates, count]] for this month and the next ones, from the vivah year
    lists of muhurat_pages (New Delhi; past dates of this month are left out)."""
    from . import muhurat_pages
    from .astro.muhurat import PERIODS
    rows = []
    y, m = today.year, today.month
    for _ in range(months):
        data = muhurat_pages._year_data("vivah", y)
        days = [d["date"] for d in data["months"][m] if d["date"] >= today]
        label = muhurat_pages._month_name(m, y, lang)           # "November 2026"
        if days:
            shown = ", ".join(str(d.day) for d in days[:DATES_PER_MONTH])
            if len(days) > DATES_PER_MONTH:
                shown += " " + TEXTS[lang]["wedding_more"].format(n=len(days) - DATES_PER_MONTH)
            rows.append([label, shown, str(len(days))])
        else:
            why = [PERIODS[k] for k in sorted(data["month_periods"][m]) if k in PERIODS]
            names = ", ".join((p.name_hi if lang == "hi" else p.name_en) for p in why)
            rows.append([label, TEXTS[lang]["wedding_none_why"].format(why=names) if names
                         else TEXTS[lang]["wedding_none"], "0"])
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return rows


def report_facts(pair: dict, lang: str = "en", today: dt.date | None = None) -> dict:
    """Everything the report prints, computed by the engine (no text is invented)."""
    from .seo_text import TEXT as SEO
    T = TEXTS[lang]
    groom, bride = cast(pair)
    res = matching.match(groom, bride, lang=lang)
    ak = res["ashtakoot"]
    who = {s: (pair[s]["name"] or T[s]) for s in SIDES}
    known = {s: pair[s]["time_known"] for s in SIDES}
    charts = {"groom": groom, "bride": bride}
    places = {s: _placements(charts[s], known[s], lang, T) for s in SIDES}

    kootas = []
    for k in ak["kootas"]:
        g, b = _koota_cells(k, lang)
        about = SEO[lang].get(f"koota_about.{k['key']}") or SEO["en"][f"koota_about.{k['key']}"]
        kootas.append({"key": k["key"], "label": k["label"], "groom": g, "bride": b,
                       "score": k["score"], "max": k["max"], "about": about, "note": k.get("note", ""),
                       "cancelled": bool(k.get("cancelled")), "cancellation": k.get("cancellation", "")})

    lines = []
    gp, bp = places["groom"], places["bride"]
    lines.append(_lord_rel(T, "moon", DOMICILE[gp["_moon"]], DOMICILE[bp["_moon"]],
                           who["groom"], who["bride"], lang))
    if known["groom"] and known["bride"]:
        lines.append(_lord_rel(T, "lagna", DOMICILE[gp["_asc"]], DOMICILE[bp["_asc"]],
                               who["groom"], who["bride"], lang))
        lines.append(_lord_rel(T, "seventh", gp["_lord7"], bp["_lord7"], who["groom"], who["bride"], lang))
    for x, y in (("groom", "bride"), ("bride", "groom")):
        if known[y]:
            n = matching._sign_distance(places[y]["_asc"], places[x]["_moon"])
            lines.append(T["cross_moon"].format(x=who[x], y=who[y], n=_ordinal(n, lang)))

    return {"match": res, "who": who, "known": known, "kootas": kootas, "places": places, "charts": charts,
            "lines": lines, "moon": {s: ak[s] for s in SIDES},
            "today": today or dt.date.today()}


# --------------------------------------------------------------------------
# The PDF
# --------------------------------------------------------------------------

def _d1_svg(session, language: str) -> str:
    """One chart's Rashi (D1) square, North Indian, as the other reports draw it ("" if
    it cannot be drawn)."""
    import os
    import shutil
    import tempfile
    scratch = tempfile.mkdtemp(prefix="astro_milan_")
    try:
        target = os.path.join(scratch, "d1.svg")
        session.chart.draw_vedic(target, style="north_indian", theme="classic", size=520)
        return pdf_report._translate_svg(pdf_report._read_svg(target), language)
    except Exception as exc:
        log.info("milan report: chart drawing unavailable: %s", exc)
        return ""
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


_BODY = """
#cover(d.subject)
#counter(page).update(1)
#set page(paper: "a4", margin: (x: 54pt, top: 64pt, bottom: 58pt), header: running, footer: SAMPLE_FOOT, foreground: SAMPLE_FG)

#let section(title) = block(above: 14pt, below: 6pt, {
  text(font: DISP, size: 12pt, fill: ACC, title)
  v(3pt)
  line(length: 100%, stroke: 0.6pt + RULE)
})

#section(d.texts.people_title)
#datatable(d.people)
#if d.drawings.len() > 0 [
  #v(6pt)
  #grid(columns: d.drawings.map(c => 1fr), gutter: 14pt,
    ..d.drawings.map(c => align(center)[
      #image(c.at(0), width: 100%)
      #v(3pt)
      #text(size: 8.2pt, fill: MUTED, c.at(1))
    ]))
]

#section(d.texts.summary_title)
#block(width: 100%, fill: WASH, inset: 12pt, radius: 4pt, stroke: 0.5pt + RULE)[
  #text(size: 22pt, weight: "bold", fill: ACC, d.total) #h(10pt) #text(size: 12pt, d.verdict)
  #v(4pt)
  #blocks(d.summary)
]

#section(d.texts.koota_title)
#datatable(d.koota_table)
#for k in d.kootas [
  #block(breakable: false, above: 12pt)[
    #text(weight: "semibold", fill: ACC, k.at(0))
    #blocks(k.at(1))
  ]
]

#section(d.texts.mangal_title)
#blocks(d.mangal)

#section(d.texts.planets_title)
#datatable(d.planets)
#v(4pt)
#blocks(d.planet_lines)

#if d.wedding.rows.len() > 0 [
  #section(d.texts.wedding_title)
  #datatable(d.wedding)
  #v(4pt)
  #blocks(d.wedding_note)
]

#section(d.texts.about_title)
#blocks(d.about)
"""


def milan_report_pdf(pair: dict, *, brand: str = "Divine Astro", site: str = "divineastro.org",
                     language: str = "en", today: dt.date | None = None,
                     sample: bool = False) -> bytes:
    """The detailed Kundali Milan report for a cleaned pair (clean_pair / the order's data)."""
    notes: list[str] = []
    lang = pdf_report._report_language(language, notes)
    T = TEXTS[lang]
    f = report_facts(pair, lang, today)
    res, who = f["match"], f["who"]
    ak = res["ashtakoot"]
    hi = lang == "hi"
    heads = lambda hs: [h.format(groom=who["groom"], bride=who["bride"]) for h in hs]  # noqa: E731

    # the two charts
    def person_rows(s: str) -> list[str]:
        p, mp = f["places"][s], f["moon"][s]
        nak = pdf_report._NAKSHATRAS_HI.get(mp["nakshatra"], mp["nakshatra"]) if hi else mp["nakshatra"]
        born = i18n.format_date(dt.date.fromisoformat(pair[s]["date"]), lang)
        born += f", {pair[s]['time']}" if f["known"][s] else f" ({T['time_unknown']})"
        return [born, pair[s]["place"], _sign(mp["rashi"], lang), f"{nak}, {T['pada']} {mp['pada']}",
                _sign(p["_asc"], lang) if f["known"][s] else "—"]
    g_rows, b_rows = person_rows("groom"), person_rows("bride")
    labels = [T["born"], T["place"], T["moon"], T["nakshatra"], T["lagna"]]
    people = {"headers": heads(T["people_headers"]), "cols": [0, 1, 1],
              "rows": [[lab, g, b] for lab, g, b in zip(labels, g_rows, b_rows)]}

    # each chart's D1 (North Indian), only for a chart cast with its birth time: without
    # one the Lagna, and so every house in the drawing, is a guess
    files: dict[str, str] = {}
    drawings = []
    for s in SIDES:
        svg = _d1_svg(f["charts"][s], lang) if f["known"][s] else ""
        if svg:
            files[f"{s}_d1.svg"] = svg
            drawings.append([f"{s}_d1.svg", T["d1"].format(who=who[s])])

    # the summary
    summary_md = [ak["band_note"], ak["convention_note"]]
    if ak["cancellations_applied"]:
        label = {k["key"]: k["label"] for k in ak["kootas"]}
        summary_md.insert(0, T["before"].format(
            n=_num(ak["total_before_cancellation"]),
            list="; ".join(f"{label.get(c['koota'], c['koota'])}: {c['reason']}"
                           for c in ak["cancellations_applied"])))

    # the eight kootas
    koota_table = {"headers": heads(T["koota_headers"]), "cols": [1, 1, 1, 0],
                   "rows": [[k["label"], k["groom"], k["bride"], f"{_num(k['score'])} / {_num(k['max'])}"]
                            for k in f["kootas"]]}
    kootas = []
    for k in f["kootas"]:
        md = f"*{T['means']}:* {k['about']}\n\n*{T['result']}:* {k['note']}"
        if k["cancelled"] and k["cancellation"]:
            md += f"\n\n*{T['cancelled']}:* {k['cancellation']}"
        kootas.append([f"{k['label']} — {_num(k['score'])} / {_num(k['max'])}",
                       pdf_report.markdown_blocks(md)])

    # Manglik dosh
    mangal = res["mangal"]
    mlines = []
    for s in SIDES:
        m = mangal[s]
        tpl = T["manglik_yes"] if m["manglik"] else T["manglik_no"]
        line = tpl.format(who=who[s], severity=m["severity"], summary=m["summary"])
        if m["manglik"] and m["mitigations"]:
            line += " " + T["relief"].format(list="; ".join(m["mitigations"]))
        mlines.append(line)
    mlines.append(T["pair"].format(verdict=mangal["pair"]["verdict"], note=mangal["pair"]["note"]))
    missing = [who[s] for s in SIDES if not f["known"][s]]
    if missing:
        mlines.append("*" + T["mangal_time"].format(who=f" {T['and']} ".join(missing)) + "*")
    mlines.append(mangal["pair"]["tradition_note"])

    # planets
    rows = [("row_lagna", "lagna"), ("row_moon", "moon"), ("row_venus", "venus"),
            ("row_mars", "mars"), ("row_jupiter", "jupiter"), ("row_seventh", "seventh")]
    planets = {"headers": heads(T["planets_headers"]), "cols": [1, 1, 1],
               "rows": [[T[r], f["places"]["groom"][k], f["places"]["bride"][k]] for r, k in rows]}
    planet_md = "\n".join(f"* {line}" for line in f["lines"]) + "\n\n*" + T["planets_note"] + "*"

    # wedding months
    wedding = {"headers": T["wedding_headers"], "cols": [0, 1, 0], "rows": []}
    try:
        wedding["rows"] = wedding_months(f["today"], lang)
    except Exception as exc:          # the almanac is best effort; say so rather than fail the report
        log.warning("milan report: wedding months unavailable: %s", exc)
        notes.append(T["omit_wedding"])

    subject = T["subject"].format(a=who["groom"], b=who["bride"])
    total = f"{_num(ak['total'])} / {_num(ak['maximum'])}"
    verdict = str(ak["verdict"])
    verdict = verdict[:1].upper() + verdict[1:]
    data = {
        "brand": brand, "title": T["title"], "subject": subject, "lang": lang,
        "cover": [[T["cover_pair"], subject], [T["cover_score"], f"{total} — {verdict}"],
                  [T["generated"], i18n.format_date(f["today"], lang)]],
        "footer": f"{brand} · {site}",
        "people": people, "drawings": drawings,
        "total": total, "verdict": verdict,
        "summary": pdf_report.markdown_blocks("\n\n".join(summary_md)),
        "koota_table": koota_table, "kootas": kootas,
        "mangal": pdf_report.markdown_blocks("\n\n".join(mlines)),
        "planets": planets, "planet_lines": pdf_report.markdown_blocks(planet_md),
        "wedding": wedding,
        "wedding_note": pdf_report.markdown_blocks(T["wedding_note"]),
        "about": pdf_report.markdown_blocks(
            T["about"] + (("\n\n" + "\n".join(f"* {n}" for n in notes)) if notes else "")),
        "texts": T,
        "sample": pdf_report._sample_block(sample, lang),
    }
    return pdf_report._compile(_BODY, data, files)


def order_pdf(order, language: str | None = None, *, brand: str = "Divine Astro",
              site: str = "divineastro.org") -> bytes:
    """The report for a paid order, from the order's own data."""
    data = load(order)
    milan = data.get("milan")
    if not isinstance(milan, dict):
        raise MilanDataError("This order has no birth details to write the report from.")
    pair = {s: milan[s] for s in SIDES}
    lang = language or data.get("lang") or "en"
    return milan_report_pdf(pair, brand=brand, site=site, language=lang)


def filename(order) -> str:
    milan = load(order).get("milan") or {}
    names = [(milan.get(s) or {}).get("name", "") for s in SIDES]
    return pdf_report.safe_filename("Divine-Astro", "kundali-milan", *names)


# --------------------------------------------------------------------------
# Delivery: the ORDER's email, once
# --------------------------------------------------------------------------

MAIL = {
    "en": {"subject": "Your Kundali Milan report — {pair}",
           "body": "Namaste,\n\nThank you for your order. Your detailed Kundali Milan report for {pair} is "
                   "attached as a PDF.\n\nIt is also kept under My orders on {site}, where you can "
                   "download it again at any time.\n\n— {brand}\n"},
    "hi": {"subject": "आपकी कुंडली मिलान रिपोर्ट — {pair}",
           "body": "नमस्ते,\n\nआपके ऑर्डर के लिए धन्यवाद। {pair} की विस्तृत कुंडली मिलान रिपोर्ट PDF के रूप में "
                   "संलग्न है।\n\nयह {site} पर 'मेरे ऑर्डर' में भी रखी है, जहाँ से आप इसे कभी भी फिर से डाउनलोड कर "
                   "सकते हैं।\n\n— {brand}\n"},
}


def deliver(order_id: int, *, brand: str = "Divine Astro", site: str = "divineastro.org") -> bool:
    """Email a paid order's report to the order's address. True when it was sent now.

    Skipped (False) for an order that is not a paid Kundali Milan report, that has no
    address, or that was emailed already (order_data.emailed_at)."""
    from . import billing, mail
    from .db import Order, OrderStatus, session as db_session, utcnow
    with db_session() as db:
        order = db.get(Order, order_id)
        if order is None or order.sku != billing.MILAN_SKU or order.status != OrderStatus.paid:
            return False
        data = load(order)
        to = order_email(order)
        if not to or data.get("emailed_at"):
            return False
        lang = data.get("lang") if data.get("lang") in ("en", "hi") else "en"
        try:
            pdf = order_pdf(order, lang, brand=brand, site=site)
        except Exception:
            log.exception("milan report for order %s could not be built", order_id)
            return False
        who = pair_label(order) or TEXTS[lang]["title"]
        m = MAIL[lang]
        sent = mail.send([to], m["subject"].format(pair=who),
                         m["body"].format(pair=who, site=site, brand=brand),
                         attachments=[(filename(order), "application/pdf", pdf)])
        if sent:
            data["emailed_at"] = utcnow().isoformat()
            order.order_data = json.dumps(data, ensure_ascii=False)
            db.commit()
        else:
            log.warning("milan report for order %s was not emailed (mail off or failed)", order_id)
        return sent


def schedule_delivery(order_id: int) -> threading.Thread | None:
    """Email the report in the background (building it takes a few seconds). Nothing
    is started when mail is off: the report is still in My orders."""
    from . import mail
    if not mail.configured():
        return None
    t = threading.Thread(target=_deliver_quietly, args=(order_id,), daemon=True,
                         name=f"milan-report-{order_id}")
    t.start()
    return t


def _deliver_quietly(order_id: int) -> None:
    try:
        import os
        from .legal import BRAND
        site = os.environ.get("ASTRO_SITE_URL", "https://divineastro.org").split("://")[-1].rstrip("/")
        deliver(order_id, brand=BRAND, site=site)
    except Exception:
        log.exception("milan report delivery for order %s failed", order_id)
