"""Vedic Remedies and Gemstone suggestions.

Determines the Life Stone (Lagna Lord), Lucky Stone (5th Lord), and Fortune Stone (9th Lord),
along with recommendations for mantras and charity based on current dasha.
"""

from __future__ import annotations

GEMSTONES = {
    "Sun": {"name": "Ruby (Manik)", "finger": "Ring finger of right hand", "metal": "Gold or Copper"},
    "Moon": {"name": "Pearl (Moti)", "finger": "Little finger of right hand", "metal": "Silver"},
    "Mars": {"name": "Red Coral (Moonga)", "finger": "Ring finger of right hand", "metal": "Copper or Gold"},
    "Mercury": {"name": "Emerald (Panna)", "finger": "Little finger of right hand", "metal": "Gold or Silver"},
    "Jupiter": {"name": "Yellow Sapphire (Pukhraj)", "finger": "Index finger of right hand", "metal": "Gold"},
    "Venus": {"name": "Diamond or White Sapphire", "finger": "Ring or Little finger of right hand", "metal": "Gold or Platinum"},
    "Saturn": {"name": "Blue Sapphire (Neelam)", "finger": "Middle finger of right hand", "metal": "Panchdhatu or Iron"},
    "Rahu": {"name": "Hessonite (Gomed)", "finger": "Middle finger of right hand", "metal": "Silver or Ashtadhatu"},
    "Ketu": {"name": "Cat's Eye (Lehsuniya)", "finger": "Middle finger of right hand", "metal": "Silver"},
}

MANTRAS = {
    "Sun": "Om Hraam Hreem Hroum Sah Suryaya Namah (108 times daily)",
    "Moon": "Om Shram Shreem Shroum Sah Chandraya Namah (108 times daily)",
    "Mars": "Om Kram Kreem Kroum Sah Bhaumaya Namah (108 times daily)",
    "Mercury": "Om Bram Breem Broum Sah Budhaya Namah (108 times daily)",
    "Jupiter": "Om Gram Greem Groum Sah Gurave Namah (108 times daily)",
    "Venus": "Om Dram Dreem Droum Sah Shukraya Namah (108 times daily)",
    "Saturn": "Om Pram Preem Proum Sah Shanishcharaya Namah (108 times daily)",
    "Rahu": "Om Bhram Bhreem Bhroum Sah Rahave Namah (108 times daily)",
    "Ketu": "Om Sram Sreem Sroum Sah Ketave Namah (108 times daily)",
}

CHARITIES = {
    "Sun": "Donate wheat, copper, or ruby-red cloth on Sunday mornings.",
    "Moon": "Donate milk, rice, silver, or white flowers on Monday evenings.",
    "Mars": "Donate red lentils (masoor dal), copper, or red flowers on Tuesday mornings.",
    "Mercury": "Donate green vegetables, mung dal, or green cloth on Wednesday mornings.",
    "Jupiter": "Donate chickpeas (chana dal), turmeric, yellow cloth, or bananas on Thursday mornings.",
    "Venus": "Donate white rice, sugar, ghee, or white silk cloth on Friday mornings.",
    "Saturn": "Donate black sesame seeds, mustard oil, iron articles, or black cloth on Saturday evenings.",
    "Rahu": "Donate black sesame, blanket, lead, or mustard oil to the needy on Saturday evenings.",
    "Ketu": "Donate multi-colored blankets, sesame seeds, or feed stray dogs on Saturday mornings.",
}


def recommend_remedies(session) -> dict:
    """Calculate gemstones and dasha remedies for a chart session."""
    # Resolve Lagna, 5th, and 9th lords from the whole-sign houses
    house_signs = session.bundle.get("houses", {}).get("signs", [])
    if not house_signs:
        # Fallback if bundle is empty/uncast
        from ..chart_service import DOMICILE
        house_signs = [session.bundle["objects"]["ASC"]["sign"]]
        for i in range(1, 12):
            house_signs.append("") # Placeholder

    # Lords of 1st, 5th, and 9th houses
    from ..chart_service import DOMICILE
    lagna_lord = DOMICILE[session.bundle["objects"]["ASC"]["sign"]]
    
    # 5th and 9th signs from Lagna
    lagna_idx = house_signs.index(session.bundle["objects"]["ASC"]["sign"])
    sign_5 = house_signs[(lagna_idx + 4) % 12]
    sign_9 = house_signs[(lagna_idx + 8) % 12]
    
    lord_5 = DOMICILE[sign_5]
    lord_9 = DOMICILE[sign_9]

    # Calculate active Mahadasha lord
    from ..chart_service import vimshottari
    import datetime as dt
    now = dt.datetime.now(dt.timezone.utc)
    dasha_info = vimshottari(session, now)
    mahadasha_lord = dasha_info.get("mahadasha", {}).get("lord", "Sun")

    return {
        "gemstones": {
            "life_stone": {
                "role": "Life Stone (Lagna Lord)",
                "planet": lagna_lord,
                **GEMSTONES.get(lagna_lord, {"name": "N/A", "finger": "", "metal": ""})
            },
            "lucky_stone": {
                "role": "Lucky Stone (5th Lord)",
                "planet": lord_5,
                **GEMSTONES.get(lord_5, {"name": "N/A", "finger": "", "metal": ""})
            },
            "fortune_stone": {
                "role": "Fortune Stone (9th Lord)",
                "planet": lord_9,
                **GEMSTONES.get(lord_9, {"name": "N/A", "finger": "", "metal": ""})
            }
        },
        "dasha_remedies": {
            "mahadasha_lord": mahadasha_lord,
            "mantra": MANTRAS.get(mahadasha_lord, ""),
            "charity": CHARITIES.get(mahadasha_lord, "")
        }
    }
