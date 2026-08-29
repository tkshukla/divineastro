"""Muhurat Finder — Classical Electional Astrology Engine.

Evaluates date ranges against classical electional (Muhurta) rules for
major life events (Marriage, Griha Pravesh, Mundan, Namkaran, General Auspicious).
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from zoneinfo import ZoneInfo

from .panchang import daily_panchang

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

TITHI_HI = {
    "Pratipada": "प्रतिपदा", "Dwitiya": "द्वितीया", "Tritiya": "तृतीया",
    "Chaturthi": "चतुर्थी", "Panchami": "पंचमी", "Shashthi": "षष्ठी",
    "Saptami": "सप्तमी", "Ashtami": "अष्टमी", "Navami": "नवमी",
    "Dashami": "दशमी", "Ekadashi": "एकादशी", "Dwadashi": "द्वादशी",
    "Trayodashi": "त्रयोदशी", "Chaturdashi": "चतुर्दशी", "Purnima": "पूर्णिमा",
    "Amavasya": "अमावस्या"
}

NAKSHATRAS_HI = {
    "Ashwini": "अश्विनी", "Bharani": "भरणी", "Krittika": "कृत्तिका",
    "Rohini": "रोहिणी", "Mrigashira": "मृगशिरा", "Ardra": "आर्द्रा",
    "Punarvasu": "पुनर्वसु", "Pushya": "पुष्य", "Ashlesha": "आश्लेषा",
    "Magha": "मघा", "Purva Phalguni": "पूर्वा फाल्गुनी",
    "Uttara Phalguni": "उत्तरा फाल्गुनी", "Hasta": "हस्त", "Chitra": "चित्रा",
    "Swati": "स्वाति", "Vishakha": "विशाखा", "Anuradha": "अनुराधा",
    "Jyeshtha": "ज्येष्ठा", "Mula": "मूल", "Purva Ashadha": "पूर्वाषाढ़ा",
    "Uttara Ashadha": "उत्तराषाढ़ा", "Shravana": "श्रवण",
    "Dhanishta": "धनिष्ठा", "Shatabhisha": "शतभिषा",
    "Purva Bhadrapada": "पूर्व भाद्रपद", "Uttara Bhadrapada": "उत्तर भाद्रपद",
    "Revati": "रेवती"
}

VARA_HI = {
    "Sunday": "रविवार", "Monday": "सोमवार", "Tuesday": "मंगलवार",
    "Wednesday": "बुधवार", "Thursday": "गुरुवार", "Friday": "शुक्रवार",
    "Saturday": "शनिवार"
}


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
    
    rule = EVENT_RULES[event]
    results = []
    
    curr = from_date
    while curr <= to_date:
        p = daily_panchang(curr, latitude, longitude, timezone, ayanamsa=ayanamsa)
        
        tithis = p.get("tithi", [])
        t_info = tithis[0] if tithis else {}
        t_num = t_info.get("number", 1)
        t_name = t_info.get("name", "—")
        
        nakshatras = p.get("nakshatra", [])
        n_info = nakshatras[0] if nakshatras else {}
        n_name = n_info.get("name", "—")
        
        yogas = p.get("yoga", [])
        y_info = yogas[0] if yogas else {}
        y_name = y_info.get("name", "—")
        
        karanas = p.get("karana", [])
        k_info = karanas[0] if karanas else {}
        k_name = k_info.get("name", "—")
        
        vara_eng = p.get("vara", {}).get("english", curr.strftime("%A"))
        
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
            reasons_hi.append(f"अशुभ योग ({y_name})")
            
        # 5. Vishti Karana (Bhadra)
        if k_name == "Vishti":
            score -= 25
            is_bad = True
            reasons.append("Bhadra (Vishti Karana) active")
            reasons_hi.append("विष्टि (भद्रा) करण सक्रिय")
            
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
        
        item = {
            "date": curr.isoformat(),
            "vara": VARA_HI.get(vara_eng, vara_eng) if language == "hi" else vara_eng,
            "tithi": TITHI_HI.get(t_name, t_name) if language == "hi" else t_name,
            "nakshatra": NAKSHATRAS_HI.get(n_name, n_name) if language == "hi" else n_name,
            "yoga": y_name,
            "karana": k_name,
            "score": score,
            "verdict": verdict,
            "badge": verdict_badge,
            "abhijit": abhijit_str,
            "rahu_kaal": rahu_str,
            "reasons": reasons_hi if language == "hi" else reasons,
            "sunrise": p.get("sun", {}).get("rise"),
            "sunset": p.get("sun", {}).get("set"),
        }
        results.append(item)
        curr += dt.timedelta(days=1)
        
    return results
