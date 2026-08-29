"""Classical Parashari Ashtakavarga engine.

Calculates:
- Bhinnashtakavarga (BAV) for all 7 planets (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn)
  contributing exact benefic points across the 12 zodiac signs/houses.
- Sarvashtakavarga (SAV): The aggregate sum across all 7 planets per sign/house (Total 337 bindus).
- House strength classifications (>28 = Strong/Auspicious, 28 = Neutral, <28 = Weak).
"""

from __future__ import annotations

from typing import Any

PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

SIGNS_HI = {
    "Aries": "मेष", "Taurus": "वृषभ", "Gemini": "मिथुन", "Cancer": "कर्क",
    "Leo": "सिंह", "Virgo": "कन्या", "Libra": "तुला", "Scorpio": "वृश्चिक",
    "Sagittarius": "धनु", "Capricorn": "मकर", "Aquarius": "कुंभ", "Pisces": "मीन"
}

PLANETS_HI = {
    "Sun": "सूर्य", "Moon": "चंद्र", "Mars": "मंगल", "Mercury": "बुध",
    "Jupiter": "गुरु", "Venus": "शुक्र", "Saturn": "शनि", "Ascendant": "लग्न"
}

# Classical Parashari Benefic Points Rules (House offsets 1-12)
# Sun: 48 points
BAV_RULES_SUN = {
    "Sun": [1, 2, 4, 7, 8, 9, 10, 11],
    "Moon": [3, 6, 10, 11],
    "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
    "Mercury": [3, 5, 6, 9, 10, 11, 12],
    "Jupiter": [5, 6, 9, 11],
    "Venus": [6, 7, 12],
    "Saturn": [1, 2, 4, 7, 8, 9, 10, 11],
    "Ascendant": [3, 4, 6, 10, 11, 12],
}

# Moon: 49 points
BAV_RULES_MOON = {
    "Sun": [3, 6, 7, 8, 10, 11],
    "Moon": [1, 3, 6, 7, 10, 11],
    "Mars": [2, 3, 5, 6, 9, 10, 11],
    "Mercury": [1, 3, 4, 5, 7, 8, 10, 11],
    "Jupiter": [1, 4, 7, 8, 10, 11, 12],
    "Venus": [3, 4, 5, 7, 9, 10, 11],
    "Saturn": [3, 5, 6, 11],
    "Ascendant": [3, 6, 10, 11],
}

# Mars: 39 points
BAV_RULES_MARS = {
    "Sun": [3, 5, 6, 10, 11],
    "Moon": [3, 6, 11],
    "Mars": [1, 2, 4, 7, 8, 10, 11],
    "Mercury": [3, 5, 6, 11],
    "Jupiter": [6, 10, 11, 12],
    "Venus": [6, 8, 11, 12],
    "Saturn": [1, 4, 7, 8, 9, 10, 11],
    "Ascendant": [1, 3, 6, 10, 11],
}

# Mercury: 54 points
BAV_RULES_MERCURY = {
    "Sun": [5, 6, 9, 11, 12],
    "Moon": [2, 4, 6, 8, 10, 11],
    "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
    "Mercury": [1, 3, 5, 6, 9, 10, 11, 12],
    "Jupiter": [6, 8, 11, 12],
    "Venus": [1, 2, 3, 4, 5, 8, 9, 11],
    "Saturn": [1, 2, 4, 7, 8, 9, 10, 11],
    "Ascendant": [1, 2, 4, 6, 8, 10, 11],
}

# Jupiter: 56 points
BAV_RULES_JUPITER = {
    "Sun": [1, 2, 3, 4, 7, 8, 9, 10, 11],
    "Moon": [2, 5, 7, 9, 11],
    "Mars": [1, 2, 4, 7, 8, 10, 11],
    "Mercury": [1, 2, 4, 5, 6, 9, 10, 11],
    "Jupiter": [1, 2, 3, 4, 7, 8, 10, 11],
    "Venus": [2, 5, 6, 9, 10, 11],
    "Saturn": [3, 5, 6, 12],
    "Ascendant": [1, 2, 4, 5, 6, 7, 9, 10, 11],
}

# Venus: 52 points
BAV_RULES_VENUS = {
    "Sun": [8, 11, 12],
    "Moon": [1, 2, 3, 4, 5, 8, 9, 11, 12],
    "Mars": [3, 5, 6, 9, 11, 12],
    "Mercury": [3, 5, 6, 9, 11],
    "Jupiter": [5, 8, 9, 10, 11],
    "Venus": [1, 2, 3, 4, 5, 8, 9, 10, 11],
    "Saturn": [3, 4, 5, 8, 9, 10, 11],
    "Ascendant": [1, 2, 3, 4, 5, 8, 9, 11],
}

# Saturn: 39 points
BAV_RULES_SATURN = {
    "Sun": [1, 2, 4, 7, 8, 10, 11],
    "Moon": [3, 6, 11],
    "Mars": [3, 5, 6, 10, 11, 12],
    "Mercury": [6, 8, 9, 10, 11, 12],
    "Jupiter": [5, 6, 11, 12],
    "Venus": [6, 11, 12],
    "Saturn": [3, 5, 6, 11],
    "Ascendant": [1, 3, 4, 6, 10, 11],
}

BAV_MAP = {
    "Sun": BAV_RULES_SUN,
    "Moon": BAV_RULES_MOON,
    "Mars": BAV_RULES_MARS,
    "Mercury": BAV_RULES_MERCURY,
    "Jupiter": BAV_RULES_JUPITER,
    "Venus": BAV_RULES_VENUS,
    "Saturn": BAV_RULES_SATURN,
}


def _sign_index(sign_name: str) -> int:
    """Return 0-indexed sign integer (0=Aries, 11=Pisces)."""
    s = sign_name.strip().capitalize()
    if s in SIGNS:
        return SIGNS.index(s)
    # Check Hindi
    for k, v in SIGNS_HI.items():
        if v == sign_name.strip():
            return SIGNS.index(k)
    return 0


def calculate_ashtakavarga(session: Any, lang: str = "en") -> dict[str, Any]:
    """Calculate complete BAV and SAV matrix from a chart session.

    Returns:
    - bav: {planet: [12 bindus per sign 0..11]}
    - sav: [12 total bindus per sign 0..11] (Sum = 337)
    - houses_sav: [12 total bindus per house 1..12 from Lagna]
    - summary: list of house-level interpretations
    """
    bundle = getattr(session, "bundle", session)
    objects = bundle.get("objects", {})

    # Extract sign indices for the 7 planets and Lagna/ASC
    positions: dict[str, int] = {}
    for p in PLANETS:
        if p in objects:
            positions[p] = _sign_index(objects[p]["sign"])
        else:
            positions[p] = 0

    asc_sign = _sign_index(objects.get("ASC", {}).get("sign", "Aries"))
    positions["Ascendant"] = asc_sign

    # Initialize BAV grids (7 planets x 12 signs)
    bav: dict[str, list[int]] = {p: [0] * 12 for p in PLANETS}

    for target_planet, rules in BAV_MAP.items():
        for source_body, house_offsets in rules.items():
            source_sign_idx = positions.get(source_body, 0)
            for offset in house_offsets:
                target_sign_idx = (source_sign_idx + (offset - 1)) % 12
                bav[target_planet][target_sign_idx] += 1

    # Sarvashtakavarga (SAV) per sign (0..11)
    sav_by_sign = [0] * 12
    for sign_idx in range(12):
        sav_by_sign[sign_idx] = sum(bav[p][sign_idx] for p in PLANETS)

    # SAV per house (1..12 from Ascendant)
    sav_by_house: list[dict[str, Any]] = []
    hi = lang == "hi"

    for h in range(1, 13):
        sign_idx = (asc_sign + (h - 1)) % 12
        sign_name = SIGNS[sign_idx]
        sign_label = SIGNS_HI[sign_name] if hi else sign_name
        score = sav_by_sign[sign_idx]

        if score >= 32:
            rating = "Extremely Strong" if not hi else "अत्यधिक प्रबल"
            status = "high"
        elif score >= 28:
            rating = "Strong / Auspicious" if not hi else "शुभ व अनुकूल"
            status = "medium"
        elif score >= 25:
            rating = "Average" if not hi else "मध्यम"
            status = "neutral"
        else:
            rating = "Needs Remediation" if not hi else "न्यून / शांति योग्य"
            status = "low"

        sav_by_house.append({
            "house": h,
            "sign": sign_name,
            "sign_label": sign_label,
            "bindus": score,
            "rating": rating,
            "status": status,
        })

    # Summary analysis
    strongest_house = max(sav_by_house, key=lambda x: x["bindus"])
    weakest_house = min(sav_by_house, key=lambda x: x["bindus"])

    # Dhana vs Vyaya (11th house gains vs 12th house expenses)
    h11_bindus = sav_by_house[10]["bindus"]
    h12_bindus = sav_by_house[11]["bindus"]
    financial_promising = h11_bindus >= h12_bindus

    if hi:
        finance_note = (
            f"एकादश भाव (आय/लाभ) में {h11_bindus} बिंदु हैं जबकि द्वादश भाव (व्यय) में {h12_bindus} बिंदु हैं। "
            + ("आय व्यय से अधिक रहने के शुभ संकेत हैं।" if financial_promising else "वित्तीय प्रबंधन में विशेष सतर्कता बरतें।")
        )
    else:
        finance_note = (
            f"11th house of gains has {h11_bindus} bindus vs 12th house of expenses with {h12_bindus} bindus. "
            + ("Indicates strong wealth accumulation and income over expenses." if financial_promising else "Suggests disciplined budget management is recommended.")
        )

    # Formatted matrix for UI table
    matrix_headers = ["Sign", "Sun", "Moon", "Mars", "Mer", "Jup", "Ven", "Sat", "SAV"] if not hi else [
        "राशि", "सूर्य", "चंद्र", "मंगल", "बुध", "गुरु", "शुक्र", "शनि", "कुल योग"
    ]

    matrix_rows = []
    for sign_idx in range(12):
        s_name = SIGNS[sign_idx] if not hi else SIGNS_HI[SIGNS[sign_idx]]
        row = [
            s_name,
            bav["Sun"][sign_idx],
            bav["Moon"][sign_idx],
            bav["Mars"][sign_idx],
            bav["Mercury"][sign_idx],
            bav["Jupiter"][sign_idx],
            bav["Venus"][sign_idx],
            bav["Saturn"][sign_idx],
            sav_by_sign[sign_idx],
        ]
        matrix_rows.append(row)

    return {
        "bav": bav,
        "sav_by_sign": sav_by_sign,
        "sav_by_house": sav_by_house,
        "total_bindus": sum(sav_by_sign),
        "strongest_house": strongest_house,
        "weakest_house": weakest_house,
        "financial_note": finance_note,
        "table": {
            "headers": matrix_headers,
            "rows": matrix_rows,
        }
    }
