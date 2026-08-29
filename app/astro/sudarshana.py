"""Classical Sudarshana Chakra Triple-Lagna Synthesis Engine.

Implements the classical Vedic 3-wheel Sudarshana Chakra:
1. Janma Lagna (Ascendant): The physical body, environment, and concrete actions.
2. Chandra Lagna (Moon Ascendant): The mental fortitude, psychological peace, and emotional experience.
3. Surya Lagna (Sun Ascendant): The soul vitality, divine will, authority, and public standing.

Synthesizes house strength across all three tiers simultaneously to determine:
- Unanimous Convergence: Houses with strong benefic strength across all 3 ascendants
  deliver spectacular, unhindered life achievements.
- Divergent/Conflicted Houses: Houses strong in one tier but afflicted in another
  explain why someone might succeed externally (Surya/Janma) while feeling unfulfilled internally (Chandra).
"""

from __future__ import annotations

from typing import Any
from ..chart_service import DOMICILE, SIGNS

SIGNS_HI = {
    "Aries": "मेष", "Taurus": "वृषभ", "Gemini": "मिथुन", "Cancer": "कर्क",
    "Leo": "सिंह", "Virgo": "कन्या", "Libra": "तुला", "Scorpio": "वृश्चिक",
    "Sagittarius": "धनु", "Capricorn": "मकर", "Aquarius": "कुंभ", "Pisces": "मीन"
}

PLANETS_HI = {
    "Sun": "सूर्य", "Moon": "चंद्र", "Mars": "मंगल", "Mercury": "बुध",
    "Jupiter": "गुरु", "Venus": "शुक्र", "Saturn": "शनि", "Rahu": "राहु",
    "Ketu": "केतु", "ASC": "लग्न", "Lagna": "लग्न"
}

HOUSE_AREAS = {
    1: {"name": "Physical Self & Vitality", "name_hi": "तनु भाव — शरीर, स्वास्थ्य व आत्मबल"},
    2: {"name": "Wealth, Speech & Family", "name_hi": "धन भाव — कुटुंब, वाणी व संचित धन"},
    3: {"name": "Courage & Siblings", "name_hi": "सहज भाव — पराक्रम, उद्यम व बंधु"},
    4: {"name": "Mother, Home & Happiness", "name_hi": "सुख भाव — माता, गृह, भूमि व मानसिक शांति"},
    5: {"name": "Intellect, Wisdom & Progeny", "name_hi": "पुत्र भाव — बुद्धि, ज्ञान, मंत्र व संतान"},
    6: {"name": "Enemies, Debt & Health", "name_hi": "रिपु भाव — रोग, ऋण, शत्रु व प्रतिस्पर्धा"},
    7: {"name": "Partnerships & Marriage", "name_hi": "जाया भाव — जीवनसाथी, व्यापार व साझेदारी"},
    8: {"name": "Transformation & Longevity", "name_hi": "आयुर्भाव — आयु, गूढ़ रहस्य व अप्रत्याशित परिवर्तन"},
    9: {"name": "Fortune, Dharma & Mentors", "name_hi": "भाग्य भाव — धर्म, गुरु कृपा व उच्च भाग्य"},
    10: {"name": "Career, Authority & Karma", "name_hi": "कर्म भाव — आजीविका, प्रतिष्ठा व सामाजिक प्रभाव"},
    11: {"name": "Gains, Income & Desires", "name_hi": "लाभ भाव — सर्व लाभ, मित्र व आर्थिक उन्नति"},
    12: {"name": "Expenditure, Travel & Moksha", "name_hi": "व्यय भाव — मोक्ष, विदेश गमन व व्यय"},
}

NATURAL_BENEFICS = {"Jupiter", "Venus", "Mercury", "Moon"}
NATURAL_MALEFICS = {"Saturn", "Mars", "Rahu", "Ketu", "Sun"}


def get_sudarshana_data(session: Any, lang: str = "en") -> dict[str, Any]:
    """Compute Sudarshana Chakra 3-tier synthesis for all 12 houses."""
    bundle = getattr(session, "bundle", session)
    objects = bundle.get("objects", {})
    hi = lang == "hi"

    body_lons: dict[str, float] = {}
    for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        if p in objects:
            body_lons[p] = float(objects[p].get("longitude", 0.0))
        elif p == "Rahu" and ("True Node" in objects or "North Node" in objects):
            node = objects.get("True Node") or objects.get("North Node")
            body_lons["Rahu"] = float(node.get("longitude", 0.0))
            body_lons["Ketu"] = (body_lons["Rahu"] + 180.0) % 360.0

    asc_lon = 0.0
    if "ASC" in objects:
        asc_lon = float(objects["ASC"].get("longitude", 0.0))

    sun_lon = body_lons.get("Sun", 0.0)
    moon_lon = body_lons.get("Moon", 0.0)

    # 3 Ascendant Sign Indices
    janma_lagna_idx = int(asc_lon // 30.0) % 12
    chandra_lagna_idx = int(moon_lon // 30.0) % 12
    surya_lagna_idx = int(sun_lon // 30.0) % 12

    # Map planets to sign index
    planet_signs: dict[str, int] = {}
    for p, lon in body_lons.items():
        planet_signs[p] = int(lon // 30.0) % 12

    houses_synthesis = []
    convergence_highlights = []

    for h in range(1, 13):
        # 1. Janma Lagna tier
        j_sign_idx = (janma_lagna_idx + (h - 1)) % 12
        j_sign_name = SIGNS[j_sign_idx]
        j_planets = [p for p, s_idx in planet_signs.items() if s_idx == j_sign_idx]

        # 2. Chandra Lagna tier
        c_sign_idx = (chandra_lagna_idx + (h - 1)) % 12
        c_sign_name = SIGNS[c_sign_idx]
        c_planets = [p for p, s_idx in planet_signs.items() if s_idx == c_sign_idx]

        # 3. Surya Lagna tier
        s_sign_idx = (surya_lagna_idx + (h - 1)) % 12
        s_sign_name = SIGNS[s_sign_idx]
        s_planets = [p for p, s_idx in planet_signs.items() if s_idx == s_sign_idx]

        # Count benefics and malefics across all 3 tiers
        all_occupants = j_planets + c_planets + s_planets
        benefic_hits = sum(1 for p in all_occupants if p in NATURAL_BENEFICS)
        malefic_hits = sum(1 for p in all_occupants if p in NATURAL_MALEFICS)

        # Calculate Strength Rating (1 to 5 stars)
        score = 3 + benefic_hits - malefic_hits
        score = max(1, min(5, score))

        if score >= 4:
            verdict = "अत्यंत शुभ व बलवान" if hi else "Highly Auspicious & Strong"
            verdict_code = "strong"
        elif score == 3:
            verdict = "संतुलित व सामान्य" if hi else "Balanced & Moderate"
            verdict_code = "average"
        else:
            verdict = "संवेदनशील / विचारणीय" if hi else "Sensitive / Needs Focus"
            verdict_code = "weak"

        meta = HOUSE_AREAS[h]
        houses_synthesis.append({
            "house": h,
            "title": meta["name_hi"] if hi else meta["name"],
            "score": score,
            "verdict": verdict,
            "verdict_code": verdict_code,
            "janma_tier": {
                "sign": j_sign_name,
                "sign_label": SIGNS_HI.get(j_sign_name, j_sign_name) if hi else j_sign_name,
                "planets": [PLANETS_HI.get(p, p) if hi else p for p in j_planets],
            },
            "chandra_tier": {
                "sign": c_sign_name,
                "sign_label": SIGNS_HI.get(c_sign_name, c_sign_name) if hi else c_sign_name,
                "planets": [PLANETS_HI.get(p, p) if hi else p for p in c_planets],
            },
            "surya_tier": {
                "sign": s_sign_name,
                "sign_label": SIGNS_HI.get(s_sign_name, s_sign_name) if hi else s_sign_name,
                "planets": [PLANETS_HI.get(p, p) if hi else p for p in s_planets],
            },
        })

        if score >= 4 and h in [1, 9, 10, 11]:
            if hi:
                convergence_highlights.append(f"भाव {h} ({meta['name_hi']}): तीनों लग्नों (तनु, चंद्र, सूर्य) से अत्यंत बलवान होकर जीवन में उत्कृष्ट सफलता प्रदान करता है।")
            else:
                convergence_highlights.append(f"House {h} ({meta['name']}): Strong across all 3 tiers (Lagna, Moon & Sun), indicating powerful life manifestation.")

    # Overview notes
    j_sign = SIGNS[janma_lagna_idx]
    c_sign = SIGNS[chandra_lagna_idx]
    s_sign = SIGNS[surya_lagna_idx]

    if hi:
        summary_text = (
            f"सुदर्शन चक्र विश्लेषण: आपका लग्न {SIGNS_HI.get(j_sign, j_sign)}, "
            f"चंद्र लग्न {SIGNS_HI.get(c_sign, c_sign)}, और सूर्य लग्न {SIGNS_HI.get(s_sign, s_sign)} है। "
            f"यह त्रि-स्तरीय चक्र आपके शारीरिक, मानसिक और आत्मिक संतुलन का समग्र चित्र प्रस्तुत करता है।"
        )
    else:
        summary_text = (
            f"Sudarshana Chakra Synthesis: Janma Lagna is {j_sign}, Chandra Lagna is {c_sign}, "
            f"and Surya Lagna is {s_sign}. This 3-tier view provides a holistic snapshot of your physical, emotional, and soul alignment."
        )

    return {
        "summary": summary_text,
        "convergence_highlights": convergence_highlights,
        "lagnas": {
            "janma": {"sign": j_sign, "sign_label": SIGNS_HI.get(j_sign, j_sign) if hi else j_sign},
            "chandra": {"sign": c_sign, "sign_label": SIGNS_HI.get(c_sign, c_sign) if hi else c_sign},
            "surya": {"sign": s_sign, "sign_label": SIGNS_HI.get(s_sign, s_sign) if hi else s_sign},
        },
        "houses": houses_synthesis,
    }
