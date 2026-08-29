"""Classical Jaimini Astrology Engine — Chara Karakas & Arudha Padas.

Implements Maharishi Jaimini's classical Upadesha Sutras:
1. 7 Chara Karakas (variable planetary significators determined by degrees within sign):
   - Atmakaraka (AK): King of the chart, soul's deepest mission and spiritual evolution.
   - Amatyakaraka (AmK): Intellect, career standing, advisors, and executive action.
   - Bhratrikaraka (BK): Mentors, gurus, siblings, and spiritual courage.
   - Matrikaraka (MK): Mother, property, emotional peace, and nurturing roots.
   - Putrakaraka (PK): Creativity, wisdom, offspring, and past-life merit.
   - Gnatikaraka (GK): Obstacles, cousins/relatives, karmic tests, and illness.
   - Darakaraka (DK): Spouse, union, desire, and financial partners.

2. Karakamsha (Sign of Atmakaraka in the D9 Navamsha chart):
   The premier Jaimini reference point for moksha, spiritual destiny, and hidden genius.

3. 12 Arudha Padas (A1/AL to A12/UL):
   The illusion/manifestation (Maya) of each house in the worldly realm.
   Includes classical exceptions: if the pada falls in the house itself or in the
   7th from it, jump 10 houses forward (as Parashara & Jaimini dictate).
"""

from __future__ import annotations

from typing import Any
from .vargas import varga_sign
from ..chart_service import DOMICILE, SIGNS

# 7 Classical physical grahas used in the 7-Karaka scheme
SEVEN_GRAHAS = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")

KARAKA_TITLES = {
    "AK": {
        "name": "Atmakaraka",
        "name_hi": "आत्मकारक",
        "role": "Soul's Primary Purpose & Destiny",
        "role_hi": "आत्मा का स्वभाव, आत्मज्ञान व जीवन का मुख्य ध्येय",
    },
    "AmK": {
        "name": "Amatyakaraka",
        "name_hi": "अमात्यकारक",
        "role": "Career, Intellect & Social Standing",
        "role_hi": "कर्म, बुद्धि, आजीविका व मंत्री पद",
    },
    "BK": {
        "name": "Bhratrikaraka",
        "name_hi": "भ्रातृकारक",
        "role": "Guru, Mentors, Courage & Siblings",
        "role_hi": "गुरु, मार्गदर्शक, भ्राता व पराक्रम",
    },
    "MK": {
        "name": "Matrikaraka",
        "name_hi": "मातृकारक",
        "role": "Mother, Inner Peace, Home & Assets",
        "role_hi": "माता, मानसिक सुख, गृह व संपत्ति",
    },
    "PK": {
        "name": "Putrakaraka",
        "name_hi": "पुत्रकारक",
        "role": "Children, Creativity & Intellect",
        "role_hi": "संतान, बुद्धि, रचनात्मकता व पूर्व पुण्य",
    },
    "GK": {
        "name": "Gnatikaraka",
        "name_hi": "ज्ञातिकारक",
        "role": "Karmic Obstacles, Rivals & Growth",
        "role_hi": "शत्रु, रोग, संघर्ष व कर्म परीक्षा",
    },
    "DK": {
        "name": "Darakaraka",
        "name_hi": "दारकारक",
        "role": "Spouse, Marriage, Wealth & Unions",
        "role_hi": "जीवनसाथी, वैवाहिक सुख, साझेदारी व धन",
    },
}

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

ARUDHA_NAMES = {
    1: {"code": "AL", "name": "Arudha Lagna", "name_hi": "आरूढ़ लग्न", "area": "Public Image & Manifested Status", "area_hi": "सामाजिक प्रतिष्ठा व सांसारिक छवि"},
    2: {"code": "A2", "name": "Dhana Pada", "name_hi": "धन आरूढ़", "area": "Accumulated Wealth & Tangible Assets", "area_hi": "संचित धन व आर्थिक स्थिति"},
    3: {"code": "A3", "name": "Bhratru Pada", "name_hi": "भ्रातृ आरूढ़", "area": "Initiative, Courage & Siblings", "area_hi": "पराक्रम, संवाद व भाई-बहन"},
    4: {"code": "A4", "name": "Matru Pada", "name_hi": "मातृ आरूढ़", "area": "Vehicles, Property & Comfort", "area_hi": "वाहन, भूमि व भौतिक सुख"},
    5: {"code": "A5", "name": "Mantra Pada", "name_hi": "मंत्र आरूढ़", "area": "Fame, Intuition & Progeny", "area_hi": "ख्याति, प्रतिभा व संतान"},
    6: {"code": "A6", "name": "Shatru Pada", "name_hi": "शत्रु आरूढ़", "area": "Litigation, Debts & Competition", "area_hi": "प्रतिस्पर्धा, ऋण व स्वास्थ्य"},
    7: {"code": "A7", "name": "Dara Pada", "name_hi": "दार आरूढ़", "area": "Commercial Partnerships & Business", "area_hi": "व्यापारिक संबंध व प्रत्यक्ष लाभ"},
    8: {"code": "A8", "name": "Mrityu Pada", "name_hi": "मृत्यु आरूढ़", "area": "Longevity & Secret Knowledge", "area_hi": "आयु, गूढ़ विद्या व अप्रत्याशित परिवर्तन"},
    9: {"code": "A9", "name": "Bhagya Pada", "name_hi": "भाग्य आरूढ़", "area": "Higher Fortune, Dharma & Pilgrimage", "area_hi": "भाग्य, धर्म, तीर्थ व गुरु कृपा"},
    10: {"code": "A10", "name": "Rajya Pada", "name_hi": "राज्य आरूढ़", "area": "Career Achievements & Authority", "area_hi": "कर्मक्षेत्र, पद, प्रभाव व सत्ता"},
    11: {"code": "A11", "name": "Labha Pada", "name_hi": "लाभ आरूढ़", "area": "Income Streams, Profits & Networks", "area_hi": "आय, सर्व लाभ व मित्र समूह"},
    12: {"code": "UL", "name": "Upapada Lagna", "name_hi": "उपपद लग्न", "area": "Spousal Nature & Marriage Quality", "area_hi": "वैवाहिक जीवन व जीवनसाथी का स्वभाव"},
}


def _calc_arudha_sign(house_sign_idx: int, lord_sign_idx: int) -> int:
    """Calculate the Arudha Pada sign for a house with Jaimini exception rules.
    
    Formula: Distance D = (lord_idx - house_idx) % 12.
    Base Pada = (lord_idx + D) % 12.
    Exceptions:
    - If Base Pada == house_idx (1st from house): add 10 signs ((house_idx + 9) % 12)
    - If Base Pada == (house_idx + 6) % 12 (7th from house): add 10 signs ((house_idx + 6 + 9) % 12 = (house_idx + 3) % 12)
    """
    d = (lord_sign_idx - house_sign_idx) % 12
    base = (lord_sign_idx + d) % 12
    
    # Exception 1: Pada falls in the house itself
    if base == house_sign_idx:
        return (base + 9) % 12
    # Exception 2: Pada falls in the 7th from house
    if base == (house_sign_idx + 6) % 12:
        return (base + 9) % 12
    return base


def get_jaimini_data(session: Any, lang: str = "en") -> dict[str, Any]:
    """Compute 7 Chara Karakas, Karakamsha, and 12 Arudha Padas."""
    bundle = getattr(session, "bundle", session)
    objects = bundle.get("objects", {})
    hi = lang == "hi"

    # Extract longitudes
    body_lons: dict[str, float] = {}
    for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        if p in objects:
            body_lons[p] = float(objects[p].get("longitude", 0.0))

    asc_lon = 0.0
    if "ASC" in objects:
        asc_lon = float(objects["ASC"].get("longitude", 0.0))

    # Calculate degrees within sign (0.0 to 30.0) for the 7 classical planets
    graha_degrees = []
    for p in SEVEN_GRAHAS:
        if p in body_lons:
            lon = body_lons[p]
            deg_in_sign = lon % 30.0
            sign_idx = int(lon // 30.0) % 12
            graha_degrees.append({
                "planet": p,
                "deg": deg_in_sign,
                "lon": lon,
                "sign_idx": sign_idx,
                "sign": SIGNS[sign_idx],
            })

    # Sort descending by degrees within sign
    graha_degrees.sort(key=lambda x: x["deg"], reverse=True)

    karaka_keys = ["AK", "AmK", "BK", "MK", "PK", "GK", "DK"]
    karakas_result = []
    atmakaraka_planet = ""
    atmakaraka_navamsha_sign = ""

    for i, k_key in enumerate(karaka_keys):
        if i < len(graha_degrees):
            item = graha_degrees[i]
            p_name = item["planet"]
            meta = KARAKA_TITLES[k_key]
            
            # Navamsha sign of planet
            nav_sign = varga_sign(item["lon"], "D9")
            if k_key == "AK":
                atmakaraka_planet = p_name
                atmakaraka_navamsha_sign = nav_sign

            deg_int = int(item["deg"])
            min_int = int((item["deg"] - deg_int) * 60)
            deg_formatted = f"{deg_int:02d}°{min_int:02d}′"

            karakas_result.append({
                "code": k_key,
                "title": meta["name_hi"] if hi else meta["name"],
                "role": meta["role_hi"] if hi else meta["role"],
                "planet": p_name,
                "planet_label": PLANETS_HI.get(p_name, p_name) if hi else p_name,
                "sign": item["sign"],
                "sign_label": SIGNS_HI.get(item["sign"], item["sign"]) if hi else item["sign"],
                "degree": deg_formatted,
                "navamsha_sign": nav_sign,
                "navamsha_label": SIGNS_HI.get(nav_sign, nav_sign) if hi else nav_sign,
            })

    # Calculate 12 Arudha Padas (A1/AL to A12/UL)
    asc_sign_idx = int(asc_lon // 30.0) % 12
    arudhas_result = []

    for h in range(1, 13):
        h_sign_idx = (asc_sign_idx + (h - 1)) % 12
        h_sign_name = SIGNS[h_sign_idx]
        lord_name = DOMICILE[h_sign_name]
        
        lord_lon = body_lons.get(lord_name, 0.0)
        lord_sign_idx = int(lord_lon // 30.0) % 12
        
        arudha_sign_idx = _calc_arudha_sign(h_sign_idx, lord_sign_idx)
        arudha_sign_name = SIGNS[arudha_sign_idx]
        
        # House distance from Lagna
        arudha_house = ((arudha_sign_idx - asc_sign_idx) % 12) + 1
        
        meta = ARUDHA_NAMES[h]
        arudhas_result.append({
            "house": h,
            "code": meta["code"],
            "title": meta["name_hi"] if hi else meta["name"],
            "area": meta["area_hi"] if hi else meta["area"],
            "sign": arudha_sign_name,
            "sign_label": SIGNS_HI.get(arudha_sign_name, arudha_sign_name) if hi else arudha_sign_name,
            "arudha_house": arudha_house,
            "lord": lord_name,
            "lord_label": PLANETS_HI.get(lord_name, lord_name) if hi else lord_name,
        })

    # Karakamsha analysis note
    ak_label = PLANETS_HI.get(atmakaraka_planet, atmakaraka_planet) if hi else atmakaraka_planet
    kl_label = SIGNS_HI.get(atmakaraka_navamsha_sign, atmakaraka_navamsha_sign) if hi else atmakaraka_navamsha_sign
    
    if hi:
        karakamsha_summary = f"आपकी कुंडली में आत्मकारक ग्रह {ak_label} है जो नवमांश में {kl_label} राशि में स्थित होकर 'कारकांश लग्न' बनाता है। यह आपकी आत्मा की आंतरिक इच्छा, आध्यात्मिक साधना और जीवन के गुप्त सामर्थ्य का मुख्य केंद्र है।"
    else:
        karakamsha_summary = f"Your Atmakaraka (Soul Planet) is {atmakaraka_planet}, placed in {atmakaraka_navamsha_sign} in the Navamsha (D9) chart to form your Karakamsha Lagna. This marks your core spiritual mission and latent intellectual mastery."

    return {
        "karakas": karakas_result,
        "arudhas": arudhas_result,
        "karakamsha": {
            "atmakaraka": atmakaraka_planet,
            "atmakaraka_label": ak_label,
            "sign": atmakaraka_navamsha_sign,
            "sign_label": kl_label,
            "summary": karakamsha_summary,
        },
    }
