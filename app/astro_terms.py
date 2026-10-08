"""Astrology vocabulary for the six regional languages (DIVASTRO-124).

`app/astro/names_<code>.py` (DIVASTRO-123) already carries the names the
panchang needs: grahas, rashis, nakshatras, months, Rahu Kaal and the other
timings. A reading and a kundali PDF also need the words *around* those names —
house, dasha, ascendant, transit, exalted — which those tables do not have.
They live here, one row per language, keyed by the English term the engine and
the prompts use. The LLM glossary (llm._glossary) and the PDF labels
(pdf_i18n) both read this table, so a chat answer and the PDF printed for the
same person use one word for one thing.

Choices a native reviewer may want to revisit:
  * kn  antardasha ಅಂತರ್ದಶೆ (ಭುಕ್ತಿ is the almanac word for the same period);
        Sade Sati ಸಾಡೇಸಾತಿ, the everyday ಏಳರಾಟ ಶನಿ given beside it.
  * te  Sade Sati is ఏలినాటి శని, the Telugu name for the 7½-year period.
  * ta  a house is வீடு (பாவம் is the Sanskrit word); antardasha is புக்தி;
        own sign is ஆட்சி, exalted உச்சம், debilitated நீசம் — Tamil jothidam usage.
  * ml  antardasha is അപഹാരം, Sade Sati ഏഴരശ്ശനി — Kerala jyothisham usage.
  * bn / or  a house is ভাব / ଭାବ (ঘর / ଘର colloquially).
"""

from __future__ import annotations

TERMS: dict[str, dict[str, str]] = {
    "kn": {
        "house": "ಭಾವ", "sign": "ರಾಶಿ", "lord": "ಅಧಿಪತಿ", "dasha": "ದಶೆ",
        "mahadasha": "ಮಹಾದಶೆ", "antardasha": "ಅಂತರ್ದಶೆ (ಭುಕ್ತಿ)",
        "ascendant": "ಲಗ್ನ", "transit": "ಗೋಚಾರ", "retrograde": "ವಕ್ರ",
        "exalted": "ಉಚ್ಚ", "debilitated": "ನೀಚ", "own sign": "ಸ್ವಕ್ಷೇತ್ರ",
        "Sade Sati": "ಸಾಡೇಸಾತಿ (ಏಳರಾಟ ಶನಿ)", "Navamsa": "ನವಾಂಶ", "yoga": "ಯೋಗ",
        "remedy": "ಪರಿಹಾರ",
    },
    "te": {
        "house": "భావం", "sign": "రాశి", "lord": "అధిపతి", "dasha": "దశ",
        "mahadasha": "మహాదశ", "antardasha": "అంతర్దశ",
        "ascendant": "లగ్నం", "transit": "గోచారం", "retrograde": "వక్రం",
        "exalted": "ఉచ్ఛ", "debilitated": "నీచ", "own sign": "స్వక్షేత్రం",
        "Sade Sati": "ఏలినాటి శని", "Navamsa": "నవాంశ", "yoga": "యోగం",
        "remedy": "పరిహారం",
    },
    "ta": {
        "house": "வீடு (பாவம்)", "sign": "ராசி", "lord": "அதிபதி", "dasha": "தசை",
        "mahadasha": "மகா தசை", "antardasha": "புக்தி",
        "ascendant": "லக்னம்", "transit": "கோசாரம்", "retrograde": "வக்ரம்",
        "exalted": "உச்சம்", "debilitated": "நீசம்", "own sign": "ஆட்சி",
        "Sade Sati": "ஏழரைச் சனி", "Navamsa": "நவாம்சம்", "yoga": "யோகம்",
        "remedy": "பரிகாரம்",
    },
    "ml": {
        "house": "ഭാവം", "sign": "രാശി", "lord": "അധിപൻ", "dasha": "ദശ",
        "mahadasha": "മഹാദശ", "antardasha": "അപഹാരം",
        "ascendant": "ലഗ്നം", "transit": "ഗോചരം", "retrograde": "വക്രം",
        "exalted": "ഉച്ചം", "debilitated": "നീചം", "own sign": "സ്വക്ഷേത്രം",
        "Sade Sati": "ഏഴരശ്ശനി", "Navamsa": "നവാംശകം", "yoga": "യോഗം",
        "remedy": "പരിഹാരം",
    },
    "bn": {
        "house": "ভাব", "sign": "রাশি", "lord": "অধিপতি", "dasha": "দশা",
        "mahadasha": "মহাদশা", "antardasha": "অন্তর্দশা",
        "ascendant": "লগ্ন", "transit": "গোচর", "retrograde": "বক্রী",
        "exalted": "উচ্চ", "debilitated": "নীচ", "own sign": "স্বক্ষেত্র",
        "Sade Sati": "সাড়েসাতি", "Navamsa": "নবাংশ", "yoga": "যোগ",
        "remedy": "প্রতিকার",
    },
    "or": {
        "house": "ଭାବ", "sign": "ରାଶି", "lord": "ଅଧିପତି", "dasha": "ଦଶା",
        "mahadasha": "ମହାଦଶା", "antardasha": "ଅନ୍ତର୍ଦଶା",
        "ascendant": "ଲଗ୍ନ", "transit": "ଗୋଚର", "retrograde": "ବକ୍ରୀ",
        "exalted": "ଉଚ୍ଚ", "debilitated": "ନୀଚ", "own sign": "ସ୍ୱକ୍ଷେତ୍ର",
        "Sade Sati": "ସାଢ଼େସାତି", "Navamsa": "ନବାଂଶ", "yoga": "ଯୋଗ",
        "remedy": "ପ୍ରତିକାର",
    },
}

# Spellings of the Gregorian months a model (or a person) commonly writes
# beside the one names_<code>.MONTHS prints — the date auditor reads both.
# Indexed 1..12 like a calendar.
MONTH_VARIANTS: dict[str, dict[int, tuple[str, ...]]] = {
    "hi": {2: ("फरवरी",), 9: ("सितम्बर",), 10: ("अक्तूबर",), 11: ("नवम्बर",), 12: ("दिसम्बर",)},
    "kn": {2: ("ಫೆಬ್ರುವರಿ",), 9: ("ಸೆಪ್ಟಂಬರ್",), 10: ("ಅಕ್ಟೊಬರ್",), 11: ("ನವಂಬರ್",),
           12: ("ಡಿಸಂಬರ್",)},
    "te": {3: ("మార్చ్",), 7: ("జులై",), 8: ("ఆగస్ట్",), 9: ("సెప్టెంబరు",),
           10: ("అక్టోబరు",), 11: ("నవంబరు",), 12: ("డిసెంబరు",)},
    "ta": {2: ("பெப்ரவரி",), 8: ("ஆகஸ்டு",), 9: ("செப்டெம்பர்",)},
    "ml": {5: ("മെയ്",), 7: ("ജൂലായ്",), 8: ("ആഗസ്റ്റ്",), 9: ("സെപ്തംബർ",),
           10: ("ഒക്‌ടോബർ",)},
    "bn": {1: ("জানুয়ারী",), 2: ("ফেব্রুয়ারী",), 8: ("আগষ্ট",)},
    "or": {1: ("ଜାନୁଆରି",), 2: ("ଫେବ୍ରୁଆରୀ",), 5: ("ମେ",)},
}

# DIVASTRO-143: pa/ne/as/mr/gu live in app/lang_data/<code>.py; overlaid here as if written inline.
from . import lang_data  # noqa: E402
lang_data.merge("ASTRO_TERMS", TERMS)
lang_data.merge("ASTRO_MONTHS", MONTH_VARIANTS)
