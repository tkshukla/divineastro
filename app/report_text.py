"""Chart-specific report text written by the rule engine, not a model (DIVASTRO-150).

The Life Book and the single-topic reports used to depend on a language model
for their prose and, when none was configured or the call failed, fell back to
canned paragraphs that said things like "your Lagna lord is well-placed"
whatever the chart. This module builds the same sections from the chart's own
facts: the sign on each house, where its lord sits, who occupies it, the
classical delineation text for each graha (app/astro/delineation.py), and the
real Vimshottari sub-periods. Every sentence here is either a fact read from
the chart or a published classical result for that fact.

English is complete. Hindi carries the same facts (names, houses, dates) in
Devanagari, but the classical delineation passages exist in English only, so a
Hindi section says so once rather than mixing languages silently.

Pure functions over plain data (rows and dicts), so they test without a chart.
"""
from __future__ import annotations

import datetime as dt

_ORD_EN = ["", "first", "second", "third", "fourth", "fifth", "sixth",
           "seventh", "eighth", "ninth", "tenth", "eleventh", "twelfth"]
_ORD_HI = ["", "प्रथम", "द्वितीय", "तृतीय", "चतुर्थ", "पंचम", "षष्ठ",
           "सप्तम", "अष्टम", "नवम", "दशम", "एकादश", "द्वादश"]

HOUSE_THEME_EN = [
    "", "the body, appearance and sense of self", "wealth, speech and family",
    "courage, siblings and short journeys", "home, mother and inner peace",
    "intellect, education and children", "health, debts and rivals",
    "spouse and partnerships", "longevity, transformation and the hidden",
    "fortune, dharma and the father", "career, status and action",
    "gains, income and friends", "expenses, solitude and liberation",
]
HOUSE_THEME_HI = [
    "", "शरीर, व्यक्तित्व और आत्म-बोध", "धन, वाणी और कुटुंब",
    "पराक्रम, सहोदर और लघु यात्राएँ", "घर, माता और मानसिक शांति",
    "बुद्धि, शिक्षा और संतान", "स्वास्थ्य, ऋण और शत्रु",
    "जीवनसाथी और साझेदारी", "आयु, परिवर्तन और गुप्त विषय",
    "भाग्य, धर्म और पिता", "कर्म, व्यवसाय और प्रतिष्ठा",
    "आय, लाभ और मित्र", "व्यय, एकांत और मोक्ष",
]

PLANET_ORDER = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
PLANET_ROLE_EN = {
    "Sun": "soul, authority and the father", "Moon": "mind, emotion and the mother",
    "Mars": "energy, courage and action", "Mercury": "speech, intellect and trade",
    "Jupiter": "wisdom, fortune and expansion", "Venus": "love, comfort and the arts",
    "Saturn": "discipline, labour and delay", "Rahu": "worldly desire and sudden change",
    "Ketu": "detachment, past merit and liberation",
}
PLANET_ROLE_HI = {
    "Sun": "आत्मा, अधिकार और पिता", "Moon": "मन, भावना और माता",
    "Mars": "ऊर्जा, साहस और कर्म", "Mercury": "वाणी, बुद्धि और व्यापार",
    "Jupiter": "ज्ञान, भाग्य और विस्तार", "Venus": "प्रेम, सुख और कला",
    "Saturn": "अनुशासन, श्रम और विलंब", "Rahu": "सांसारिक इच्छा और अचानक परिवर्तन",
    "Ketu": "वैराग्य, पूर्व-पुण्य और मोक्ष",
}

PLANET_HI = {"Sun": "सूर्य", "Moon": "चंद्रमा", "Mars": "मंगल", "Mercury": "बुध",
             "Jupiter": "बृहस्पति", "Venus": "शुक्र", "Saturn": "शनि", "Rahu": "राहु", "Ketu": "केतु",
             "Uranus": "अरुण", "Neptune": "वरुण", "Pluto": "यम", "Chiron": "चिरोन"}
SIGN_HI = {"Aries": "मेष", "Taurus": "वृषभ", "Gemini": "मिथुन", "Cancer": "कर्क", "Leo": "सिंह",
           "Virgo": "कन्या", "Libra": "तुला", "Scorpio": "वृश्चिक", "Sagittarius": "धनु",
           "Capricorn": "मकर", "Aquarius": "कुंभ", "Pisces": "मीन"}
MONTH_HI = ["जनवरी", "फरवरी", "मार्च", "अप्रैल", "मई", "जून", "जुलाई", "अगस्त",
            "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर"]

NOTE_EN_ONLY_HI = ("> इस खंड में आपकी कुंडली के तथ्य दिए गए हैं। शास्त्रीय फल का विस्तृत पाठ "
                   "केवल अंग्रेज़ी रिपोर्ट में उपलब्ध है।")
NOTE_ENGINE_EN = ("> This section is read directly from your chart by our rule engine "
                  "(placements and classical results), not written by an AI model.")
NOTE_ENGINE_HI = ("> यह खंड हमारे नियम-आधारित इंजन ने आपकी कुंडली से सीधे पढ़ा है "
                  "(स्थितियाँ और शास्त्रीय फल), किसी AI मॉडल ने नहीं लिखा।")


ROLE_HI = {"Life Stone (Lagna Lord)": "जीवन रत्न (लग्नेश)",
           "Lucky Stone (5th Lord)": "शुभ रत्न (पंचमेश)",
           "Fortune Stone (9th Lord)": "भाग्य रत्न (नवमेश)"}
_REMEDY_WORDS_HI = [
    ("Ring or Little finger of right hand", "दाहिने हाथ की अनामिका या कनिष्ठा"),
    ("Ring finger of right hand", "दाहिने हाथ की अनामिका"),
    ("Little finger of right hand", "दाहिने हाथ की कनिष्ठा"),
    ("Index finger of right hand", "दाहिने हाथ की तर्जनी"),
    ("Middle finger of right hand", "दाहिने हाथ की मध्यमा"),
    ("Panchdhatu", "पंचधातु"), ("Ashtadhatu", "अष्टधातु"), ("Platinum", "प्लैटिनम"),
    ("Copper", "तांबा"), ("Silver", "चांदी"), ("Gold", "सोना"), ("Iron", "लोहा"),
    (" or ", " या "),
]


def _remedy_hi(text: str) -> str:
    for en, hi in _REMEDY_WORDS_HI:
        text = text.replace(en, hi)
    return text


def _p(name: str, hi: bool) -> str:
    return PLANET_HI.get(name, name) if hi else name


def _s(name: str, hi: bool) -> str:
    return SIGN_HI.get(name, name) if hi else name


def _sentence(text: str) -> str:
    text = (text or "").strip()
    if not text:
        return ""
    text = text[0].upper() + text[1:]
    return text if text[-1] in ".!?।" else text + "."


def month_year(d: dt.datetime, hi: bool) -> str:
    return (f"{MONTH_HI[d.month - 1]} {d.year}" if hi else d.strftime("%b %Y"))


def planet_places(pos_rows: list[list[str]]) -> dict[str, dict]:
    """Planet -> {sign, house} from the positions table rows
    (Body, Sign, Degree, House, ...). Retrograde marks ("Jupiter R") dropped."""
    out: dict[str, dict] = {}
    for row in pos_rows:
        name = str(row[0]).replace(" R", "").strip()
        if name in PLANET_ORDER and len(row) > 3:
            try:
                out[name] = {"sign": row[1], "house": int(row[3]),
                             "retro": str(row[0]).endswith(" R")}
            except ValueError:
                continue
    return out


def house_reading(h: int, houses_rows: list[list[str]], places: dict[str, dict],
                  dignities: dict[str, str], hi: bool) -> str:
    """One bullet: sign, lord, where the lord sits, who occupies the house."""
    row = next((r for r in houses_rows if str(r[0]).strip() == str(h)), None)
    if row is None:
        return ""
    sign, lord, occ = row[1], row[3], str(row[4])
    theme = (HOUSE_THEME_HI if hi else HOUSE_THEME_EN)[h]
    lp = places.get(lord)
    occupants = [] if occ.strip() in ("", "—") else [o.strip() for o in occ.split(",")]
    if hi:
        head = f"* **{_ORD_HI[h]} भाव — {_s(sign, True)}** ({theme}): "
        body = f"भावेश {_p(lord, True)}"
        if lp:
            body += f" {_s(lp['sign'], True)} राशि में, {_ORD_HI[lp['house']]} भाव में स्थित है।"
        else:
            body += "।"
        body += (" इसमें " + ", ".join(_p(o, True) for o in occupants) + " स्थित हैं।"
                 if occupants else " इसमें कोई ग्रह स्थित नहीं है।")
        return head + body
    head = f"* **{_ORD_EN[h].capitalize()} house — {sign}** ({theme}): "
    body = f"ruled by {lord}"
    if lp:
        dig = dignities.get(lord)
        body += (f", which sits in {lp['sign']} in the {_ORD_EN[lp['house']]} house"
                 + (f" ({dig})" if dig else "") + ".")
    else:
        body += "."
    body += (f" Occupied by {', '.join(occupants)}." if occupants else " No planet occupies it.")
    return head + body


def houses_section(houses_rows, places, dignities, hi) -> str:
    lines = [house_reading(h, houses_rows, places, dignities, hi) for h in range(1, 13)]
    return "\n".join(x for x in lines if x)


def planet_reading(name: str, places: dict[str, dict], delin: dict | None, hi: bool) -> str:
    pl = places.get(name)
    if pl is None:
        return ""
    role = (PLANET_ROLE_HI if hi else PLANET_ROLE_EN)[name]
    retro = pl.get("retro")
    if hi:
        txt = (f"* **{_p(name, True)} — {_s(pl['sign'], True)}, {_ORD_HI[pl['house']]} भाव"
               f"{' (वक्री)' if retro else ''}**: कारकत्व: {role}।")
        return txt
    head = (f"* **{name} — {pl['sign']}, {_ORD_EN[pl['house']]} house"
            f"{' (retrograde)' if retro else ''}**: significator of {role}.")
    d = (delin or {}).get(name)
    if d:
        bits = [_sentence(d["dignity"]["note"]) if d["dignity"].get("note") else "",
                _sentence(d.get("house_text", ""))]
        av = d.get("avastha") or {}
        if av.get("state"):
            bits.append(_sentence(f"State ({av['state']}): {av.get('note', '')}"))
        head += " " + " ".join(b for b in bits if b)
    return head


def planets_section(places, delin, hi) -> str:
    lines = [planet_reading(n, places, delin, hi) for n in PLANET_ORDER]
    return "\n".join(x for x in lines if x)


def yogas_remedies_section(yoga_rows: list[list[str]], rem: dict | None, hi: bool) -> str:
    out: list[str] = []
    out.append(yogas_section(yoga_rows, hi))
    if rem:
        out.append(remedies_section(rem, hi))
    return "\n\n".join(out)


def yogas_section(yoga_rows: list[list[str]], hi: bool) -> str:
    out: list[str] = []
    if hi:
        out.append("### बने हुए योग")
        out.append("\n".join(f"* **{r[0]}** — {r[3]}" for r in yoga_rows)
                   if yoga_rows else "इस कुंडली में सारणी में जाँचे गए प्रमुख योग नहीं बने।")
    else:
        out.append("### Yogas formed in this chart")
        out.append("\n".join(f"* **{r[0]}** ({r[1]}) — {r[3]}" for r in yoga_rows)
                   if yoga_rows else "None of the classical yogas this report tests for forms in this chart.")
    return "\n\n".join(out)


def remedies_section(rem: dict, hi: bool) -> str:
    out: list[str] = []
    if rem:
        gems = rem.get("gemstones", {})
        dr = rem.get("dasha_remedies", {})
        out.append("### उपाय" if hi else "### Remedies for this chart")
        lines = []
        for key in ("life_stone", "lucky_stone", "fortune_stone"):
            g = gems.get(key)
            if g:
                if hi:
                    lines.append(
                        f"* **{ROLE_HI.get(g['role'], g['role'])}:** {g['name']}, "
                        f"धातु: {_remedy_hi(g['metal'])}, उँगली: {_remedy_hi(g['finger'])}।")
                else:
                    lines.append(
                        f"* **{g['role']}:** {g['name']}, set in {g['metal']}, "
                        f"worn on the {g['finger']}.")
        if dr.get("mantra"):
            lines.append(f"* **{'दशा मंत्र' if hi else 'Mantra for your running dasha'} "
                         f"({_p(dr.get('mahadasha_lord', ''), hi)}):** {dr['mantra']}")
        if dr.get("charity"):
            lines.append(f"* **{'दान (अंग्रेज़ी में)' if hi else 'Charity'}:** {dr['charity']}")
        out.append("\n".join(lines))
    return "\n\n".join(out)


def antardasha_periods(mahadashas, when: dt.datetime, days: int,
                       vimshottari: list[tuple[str, int]], year_days: float):
    """Every antardasha overlapping [when, when+days] as (maha, antar, start, end).

    `mahadashas` is pdf_report._mahadasha_periods(): (lord, years, start, end)."""
    order = [lord for lord, _ in vimshottari]
    horizon = when + dt.timedelta(days=days)
    out = []
    for m_lord, m_years, m_start, m_end in mahadashas:
        if m_end <= when or m_start >= horizon:
            continue
        cursor = m_start
        idx = order.index(m_lord)
        for step in range(9):
            a_lord, a_years = vimshottari[(idx + step) % 9]
            end = cursor + dt.timedelta(days=(m_years * a_years / 120.0) * year_days)
            if end > when and cursor < horizon:
                out.append((m_lord, a_lord, cursor, end))
            cursor = end
    return out


def outlook_rows(periods, antar_text, hi: bool, when: dt.datetime | None = None,
                 key_planets: dict[str, str] | set[str] | None = None, key_label: str = "") -> list[list[str]]:
    """[[label, markdown], ...] for the sub-periods in `periods`.

    `antar_text` maps a planet to its classical antardasha result (English).
    A period whose lord is in `key_planets` is flagged, which is how a
    single-topic report says when its topic is switched on."""
    rows = []
    for m, a, start, end in periods:
        label = (f"{month_year(start, hi)} – {month_year(end, hi)}")
        if when is not None and start <= when.replace(tzinfo=start.tzinfo):
            label += ("\n(चल रही)" if hi else "\n(running now)")
        text = f"**{_p(m, hi)} – {_p(a, hi)}**"
        if key_planets and a in key_planets:
            reason = key_planets[a] if isinstance(key_planets, dict) else ""
            text += f" — {key_label}" if key_label else ""
            if reason:
                text += f" ({_p(a, hi)}: {reason})"
        reading = antar_text.get(a)
        if reading and not hi:
            text += "\n\n" + _sentence(f"Classically this sub-period brings {reading}")
        rows.append([label, text])
    return rows


# --------------------------------------------------------------------------
# Single-topic reports
# --------------------------------------------------------------------------

TOPICS = {
    "career": {
        "houses": [10, 6, 11, 2, 1], "karakas": ["Sun", "Saturn", "Mercury", "Jupiter"],
        "title_en": "Career & Profession Guidance Report",
        "title_hi": "करियर एवं व्यवसाय मार्गदर्शन रिपोर्ट",
        "subject_en": "your career", "subject_hi": "आपके करियर",
        "scope_en": ("This report reads the tenth house of career, the sixth of service and competition, "
                     "the eleventh of gains and recognition, the second of income and the first of the self, "
                     "and the planets that rule or occupy them, against your running dasha."),
        "scope_hi": ("यह रिपोर्ट आपकी कुंडली के दशम (कर्म), षष्ठ (सेवा व प्रतिस्पर्धा), एकादश (लाभ), "
                     "द्वितीय (आय) और प्रथम भाव तथा उनके स्वामी और स्थित ग्रहों को आपकी चल रही दशा के साथ पढ़ती है।"),
    },
    "marriage": {
        "houses": [7, 2, 11, 4, 8], "karakas": ["Venus", "Jupiter", "Mars"],
        "title_en": "Marriage & Relationship Timing Report",
        "title_hi": "विवाह समय एवं संबंध मार्गदर्शन रिपोर्ट",
        "subject_en": "marriage and relationships", "subject_hi": "विवाह और संबंधों",
        "scope_en": ("This report reads the seventh house of marriage, the second of family, the eleventh of "
                     "fulfilment, the fourth of home and the eighth of the marriage bond, and the planets that "
                     "rule or occupy them, with Venus, Jupiter and Mars as significators, against your running dasha."),
        "scope_hi": ("यह रिपोर्ट सप्तम (विवाह), द्वितीय (कुटुंब), एकादश (इच्छापूर्ति), चतुर्थ (गृहस्थ सुख) और अष्टम भाव, "
                     "तथा शुक्र, गुरु और मंगल को कारक मानकर, आपकी चल रही दशा के साथ पढ़ती है।"),
    },
    "wealth": {
        "houses": [2, 11, 9, 5, 10], "karakas": ["Jupiter", "Venus", "Mercury"],
        "title_en": "Wealth, Finance & Growth Report",
        "title_hi": "धन, वित्त एवं व्यापार वृद्धि रिपोर्ट",
        "subject_en": "wealth and business", "subject_hi": "धन और व्यापार",
        "scope_en": ("This report reads the second house of savings, the eleventh of gains, the ninth of fortune, "
                     "the fifth of speculation and merit and the tenth of livelihood, and the planets that rule or "
                     "occupy them, with Jupiter, Venus and Mercury as significators, against your running dasha."),
        "scope_hi": ("यह रिपोर्ट द्वितीय (संचित धन), एकादश (लाभ), नवम (भाग्य), पंचम (पूर्व-पुण्य) और दशम (आजीविका) भाव, "
                     "तथा गुरु, शुक्र और बुध को कारक मानकर, आपकी चल रही दशा के साथ पढ़ती है।"),
    },
}


def topic_for(sku_or_topic: str) -> str:
    t = (sku_or_topic or "career").lower().replace("sq_", "")
    if "marriage" in t or "relationship" in t:
        return "marriage"
    if "wealth" in t or "finance" in t or "business" in t:
        return "wealth"
    return "career"


def key_planets(topic: str, houses_rows: list[list[str]], hi: bool) -> tuple[list[str], dict[str, str]]:
    """The planets a topic turns on, and why: lords of its houses, then its significators."""
    cfg = TOPICS[topic]
    order: list[str] = []
    why: dict[str, list[str]] = {}
    lord_of = {int(str(r[0]).strip()): r[3] for r in houses_rows if str(r[0]).strip().isdigit()}
    for h in cfg["houses"]:
        lord = lord_of.get(h)
        if lord in PLANET_ORDER:
            if lord not in order:
                order.append(lord)
            why.setdefault(lord, []).append(
                f"{_ORD_HI[h]} भाव का स्वामी" if hi else f"lord of the {_ORD_EN[h]} house")
    for k in cfg["karakas"]:
        if k not in order:
            order.append(k)
        why.setdefault(k, []).append(
            f"{cfg['subject_hi']} का कारक" if hi else f"natural significator of {cfg['subject_en']}")
    return order, {k: "; ".join(v) for k, v in why.items()}
