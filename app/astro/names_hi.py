"""Hindi names for the panchang limbs — the one copy.

main.py (dashboard), muhurat.py, seo_pages.py and /api/panchang (the in-app
Panchang tool and the home Today strip) all read these tables. Before this module
the yoga and karana tables were copied between main.py and seo_pages.py, and the
Today strip carried a third, JavaScript copy of the tithi and nakshatra ones.
"""

from __future__ import annotations

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

# Keyed by the English weekday (panchang's vara["weekday"]).
VARA_HI = {
    "Sunday": "रविवार", "Monday": "सोमवार", "Tuesday": "मंगलवार",
    "Wednesday": "बुधवार", "Thursday": "गुरुवार", "Friday": "शुक्रवार",
    "Saturday": "शनिवार"
}

YOGA_HI = {
    "Vishkambha": "विष्कम्भ", "Priti": "प्रीति", "Ayushman": "आयुष्मान",
    "Saubhagya": "सौभाग्य", "Shobhana": "शोभन", "Atiganda": "अतिगण्ड",
    "Sukarma": "सुकर्मा", "Dhriti": "धृति", "Shula": "शूल", "Ganda": "गण्ड",
    "Vriddhi": "वृद्धि", "Dhruva": "ध्रुव", "Vyaghata": "व्याघात",
    "Harshana": "हर्षण", "Vajra": "वज्र", "Siddhi": "सिद्धि",
    "Vyatipata": "व्यतीपात", "Variyana": "वरीयान", "Parigha": "परिघ",
    "Shiva": "शिव", "Siddha": "सिद्ध", "Sadhya": "साध्य", "Shubha": "शुभ",
    "Shukla": "शुक्ल", "Brahma": "ब्रह्म", "Indra": "इन्द्र", "Vaidhriti": "वैधृति"
}

KARANA_HI = {
    "Bava": "बव", "Balava": "बालव", "Kaulava": "कौलव", "Taitila": "तैतिल",
    "Gara": "गर", "Vanija": "वणिज", "Vishti": "विष्टि (भद्रा)", "Shakuni": "शकुनि",
    "Chatushpada": "चतुष्पाद", "Naga": "नाग", "Kimstughna": "किंस्तुघ्न"
}

# The bare word, as it prefixes a tithi ("कृष्ण अष्टमी"). The SEO pages add "पक्ष".
PAKSHA_HI = {"Shukla": "शुक्ल", "Krishna": "कृष्ण"}

NOTE_POLAR_HI = ("इस तिथि को इस अक्षांश पर सूर्य का उदय और अस्त दोनों नहीं होते, इसलिए "
                 "वैदिक दिन सूर्योदय से नहीं गिना जा सकता। नीचे के अंग स्थानीय मध्यरात्रि "
                 "से गिने गए हैं, और सूर्योदय पर आधारित मुहूर्त लागू नहीं होते।")
NOTE_WEDNESDAY_HI = "बुधवार को अभिजित मुहूर्त नहीं लिया जाता — वार के स्वामी बुध इसे दूषित मानते हैं।"


def add_hindi(p: dict) -> dict:
    """Add Hindi names beside the English ones in a `daily_panchang` result.

    Additive only: every English field keeps its value, so nothing that already
    reads the response changes. Each limb row gains `name_hi` (tithis also
    `paksha_hi` and `label_hi`, e.g. "कृष्ण अष्टमी"), the vara gains `name_hi`,
    and `notes_hi` mirrors `notes`. Both languages travel together so the page
    can switch EN / हिं without asking the server again.
    """
    for row in p.get("tithi") or []:
        row["name_hi"] = TITHI_HI.get(row.get("name"), row.get("name"))
        row["paksha_hi"] = PAKSHA_HI.get(row.get("paksha"), row.get("paksha"))
        row["label_hi"] = f"{row['paksha_hi'] or ''} {row['name_hi']}".strip()
    for key, table in (("nakshatra", NAKSHATRAS_HI), ("yoga", YOGA_HI), ("karana", KARANA_HI)):
        for row in p.get(key) or []:
            row["name_hi"] = table.get(row.get("name"), row.get("name"))
    vara = p.get("vara")
    if vara:
        vara["name_hi"] = VARA_HI.get(vara.get("weekday"), vara.get("name"))
    # The engine writes its notes in English prose; the two it can write follow
    # from the data, so their Hindi is derived the same way rather than by
    # matching the English text.
    notes_hi = []
    if p.get("reckoned_from") == "midnight":
        notes_hi.append(NOTE_POLAR_HI)
    elif (p.get("muhurta") or {}).get("abhijit") is None and p.get("reckoned_from") == "sunrise":
        notes_hi.append(NOTE_WEDNESDAY_HI)
    p["notes_hi"] = notes_hi
    return p
