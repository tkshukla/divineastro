"""Kundali (chart) PDF labels in Kannada, Telugu, Tamil, Malayalam, Bengali and
Odia (DIVASTRO-124).

pdf_report.py has carried English and Hindi side by side since the reports were
written; the Hindi strings stay where they are. This module is the same job for
the six regional languages, as tables:

  LABELS[code]   every heading, table header and row label the chart PDF prints
  VOCAB[code]    the engine's English cell values (dignity, aspect, motion,
                 status, zodiac, house system, ayanamsa, outer planets, angles,
                 yogini names) -> the language's word

Names that already exist in `app/astro/names_<code>.py` (grahas, rashis,
nakshatras, months) are read from there through `vocab()`, not copied, so the
PDF prints the same ಕುಜ / செவ்வாய் the panchang pages do. The house/dasha words
come from `app/astro_terms.py`, shared with the chat glossary.

`translate(value, code)` is pdf_report._translate_val's regional twin: whole
cells, comma lists, "Mars R" (retrograde) and "23°07' Aries" are all handled the
same way the Hindi edition handles them.
"""

from __future__ import annotations

import functools
import re

from .astro_terms import TERMS

REGIONAL = ("kn", "te", "ta", "ml", "bn", "or")

# The Noto families that carry each script, serif first (the report body is a
# serif). fonts-noto-core in the Docker image ships all of them except Noto
# Serif Oriya, hence the Sans fallback in every list.
SCRIPT_FONTS: dict[str, tuple[str, ...]] = {
    "kn": ("Noto Serif Kannada", "Noto Sans Kannada"),
    "te": ("Noto Serif Telugu", "Noto Sans Telugu"),
    "ta": ("Noto Serif Tamil", "Noto Sans Tamil"),
    "ml": ("Noto Serif Malayalam", "Noto Sans Malayalam"),
    "bn": ("Noto Serif Bengali", "Noto Sans Bengali"),
    "or": ("Noto Serif Oriya", "Noto Sans Oriya"),
}

# --------------------------------------------------------------------------
# Labels
# --------------------------------------------------------------------------

LABELS: dict[str, dict] = {
    "kn": {
        # section headings (pdf_report._LOCALIZED_TEXTS keys)
        "title": "ಜನ್ಮ ಜಾತಕ ವರದಿ", "born": "ಜನನ ಸಮಯ", "at": "ಜನನ ಸ್ಥಳ",
        "system": "ಪದ್ಧತಿ", "generated": "ದಿನಾಂಕ", "birth_details": "ಜನನ ವಿವರಗಳು",
        "d1_title": "ರಾಶಿ ಕುಂಡಲಿ (D1)", "d9_title": "ನವಾಂಶ ಕುಂಡಲಿ (D9)",
        "north_indian": "ಉತ್ತರ ಭಾರತೀಯ ಶೈಲಿ", "south_indian": "ದಕ್ಷಿಣ ಭಾರತೀಯ ಶೈಲಿ",
        "planetary_positions": "ಗ್ರಹ ಸ್ಥಿತಿ", "houses": "ಭಾವ ಸ್ಥಿತಿ",
        "aspects": "ಪ್ರಮುಖ ದೃಷ್ಟಿಗಳು", "dasha": "ವಿಂಶೋತ್ತರಿ ಮಹಾದಶೆ",
        "varshphal_title": "ಮಾಸವಾರು ವರ್ಷಫಲ", "upcoming_title": "ಮುಂಬರುವ ಪ್ರಮುಖ ಕಾಲಗಳು",
        "house_summary_title": "ಭಾವಫಲ ಸಾರಾಂಶ", "vargas_title": "ವರ್ಗ ಕುಂಡಲಿ ಸ್ಥಿತಿ",
        "ashtakavarga_title": "ಸರ್ವಾಷ್ಟಕವರ್ಗ (337 ಬಿಂದುಗಳು)",
        "yogas_title": "ಜಾತಕದಲ್ಲಿನ ಪ್ರಮುಖ ಯೋಗಗಳು",
        "antardasha_title": "ನಡೆಯುತ್ತಿರುವ ಮಹಾದಶೆಯ ಅಂತರ್ದಶೆಗಳು",
        "houses_detailed_title": "ದ್ವಾದಶ ಭಾವಫಲ ವಿವರಣೆ",
        "planets_detailed_title": "ಗ್ರಹಫಲ ವಿವರಣೆ",
        "remedies_detailed_title": "ಜ್ಯೋತಿಷ ಪರಿಹಾರಗಳು ಮತ್ತು ಮಂತ್ರಗಳು",
        # birth details
        "name": "ಹೆಸರು", "date_time": "ಜನನ ದಿನಾಂಕ ಮತ್ತು ಸಮಯ", "time_unknown": "ಸಮಯ ತಿಳಿದಿಲ್ಲ",
        "place": "ಜನನ ಸ್ಥಳ", "time_zone": "ಸಮಯ ವಲಯ", "universal_time": "ಸಾರ್ವತ್ರಿಕ ಸಮಯ (UT)",
        "zodiac": "ರಾಶಿಚಕ್ರ / ಅಯನಾಂಶ", "ayanamsa": "ಅಯನಾಂಶ", "house_system": "ಭಾವ ಪದ್ಧತಿ",
        "sect": "ಜನನ ಕಾಲ", "day_chart": "ಹಗಲಿನ ಜನನ", "night_chart": "ರಾತ್ರಿಯ ಜನನ",
        # dasha summary
        "moon": "ಚಂದ್ರ", "nakshatra": "ನಕ್ಷತ್ರ", "pada": "ಪಾದ",
        "mahadasha_now": "ನಡೆಯುತ್ತಿರುವ ಮಹಾದಶೆ", "antardasha_now": "ನಡೆಯುತ್ತಿರುವ ಅಂತರ್ದಶೆ",
        "yogini_dasha": "ಯೋಗಿನಿ ದಶೆ", "yogini_antardasha": "ಯೋಗಿನಿ ಅಂತರ್ದಶೆ",
        "as_of": "ಈ ದಿನಾಂಕದಂತೆ",
        # table headers
        "dasha_headers": ["ಮಹಾದಶೆ", "ವರ್ಷಗಳು", "ಆರಂಭ", "ಅಂತ್ಯ", "ಸ್ಥಿತಿ"],
        "antardasha_headers": ["ಅಂತರ್ದಶೆ", "ಆರಂಭ", "ಅಂತ್ಯ", "ಸ್ಥಿತಿ"],
        "positions_headers": ["ಗ್ರಹ", "ರಾಶಿ", "ಅಂಶ", "ಭಾವ", "ಭಾವ ಸ್ಥಾನ", "ಬಲ / ಗೌರವ"],
        "houses_headers": ["ಭಾವ", "ರಾಶಿ", "ಆರಂಭ ಅಂಶ", "ಭಾವಾಧಿಪತಿ", "ಸ್ಥಿತ ಗ್ರಹಗಳು"],
        "aspects_headers": ["ಗ್ರಹ", "ದೃಷ್ಟಿ", "ಗ್ರಹ", "ಅಂತರ (orb)", "ಗತಿ"],
        "vargas_headers": ["ಗ್ರಹ / ಲಗ್ನ", "D1 (ರಾಶಿ)", "D3 (ದ್ರೇಕ್ಕಾಣ)", "D7 (ಸಪ್ತಾಂಶ)",
                           "D9 (ನವಾಂಶ)", "D10 (ದಶಾಂಶ)", "D12 (ದ್ವಾದಶಾಂಶ)"],
        "yogas_headers": ["ಯೋಗ", "ವರ್ಗ", "ಗ್ರಹಗಳು", "ಫಲ / ವಿವರಣೆ"],
        "no_yogas": "ಪ್ರಮುಖ ಯೋಗಗಳು ರೂಪುಗೊಂಡಿಲ್ಲ",
        "no_yogas_note": "ಗ್ರಹ ಶಾಂತಿಗಾಗಿ ನಿತ್ಯ ಪ್ರಾರ್ಥನೆ ಮತ್ತು ಮಂತ್ರ ಜಪ ಮಾಡಿ.",
        "english_sections": "ಈ ವಿವರಣಾ ಭಾಗಗಳನ್ನು ಇಂಗ್ಲಿಷ್‌ನಲ್ಲಿ ತೋರಿಸಲಾಗಿದೆ.",
    },
    "te": {
        "title": "జన్మ జాతక నివేదిక", "born": "జనన సమయం", "at": "జన్మ స్థలం",
        "system": "పద్ధతి", "generated": "తేదీ", "birth_details": "జనన వివరాలు",
        "d1_title": "రాశి చక్రం (D1)", "d9_title": "నవాంశ చక్రం (D9)",
        "north_indian": "ఉత్తర భారత శైలి", "south_indian": "దక్షిణ భారత శైలి",
        "planetary_positions": "గ్రహ స్థితి", "houses": "భావ స్థితి",
        "aspects": "ముఖ్య దృష్టులు", "dasha": "వింశోత్తరి మహాదశ",
        "varshphal_title": "నెలవారీ వర్షఫలం", "upcoming_title": "రాబోయే ముఖ్య కాలాలు",
        "house_summary_title": "భావఫల సారాంశం", "vargas_title": "వర్గ చక్రాల స్థితి",
        "ashtakavarga_title": "సర్వాష్టకవర్గం (337 బిందువులు)",
        "yogas_title": "జాతకంలోని ముఖ్య యోగాలు",
        "antardasha_title": "ప్రస్తుత మహాదశలోని అంతర్దశలు",
        "houses_detailed_title": "ద్వాదశ భావఫల వివరణ",
        "planets_detailed_title": "గ్రహఫల వివరణ",
        "remedies_detailed_title": "జ్యోతిష పరిహారాలు మరియు మంత్రాలు",
        "name": "పేరు", "date_time": "జనన తేదీ మరియు సమయం", "time_unknown": "సమయం తెలియదు",
        "place": "జన్మ స్థలం", "time_zone": "సమయ మండలం", "universal_time": "సార్వత్రిక సమయం (UT)",
        "zodiac": "రాశిచక్రం / అయనాంశ", "ayanamsa": "అయనాంశ", "house_system": "భావ పద్ధతి",
        "sect": "జనన కాలం", "day_chart": "పగటి జననం", "night_chart": "రాత్రి జననం",
        "moon": "చంద్రుడు", "nakshatra": "నక్షత్రం", "pada": "పాదం",
        "mahadasha_now": "ప్రస్తుత మహాదశ", "antardasha_now": "ప్రస్తుత అంతర్దశ",
        "yogini_dasha": "యోగిని దశ", "yogini_antardasha": "యోగిని అంతర్దశ",
        "as_of": "ఈ తేదీ నాటికి",
        "dasha_headers": ["మహాదశ", "సంవత్సరాలు", "ప్రారంభం", "ముగింపు", "స్థితి"],
        "antardasha_headers": ["అంతర్దశ", "ప్రారంభం", "ముగింపు", "స్థితి"],
        "positions_headers": ["గ్రహం", "రాశి", "అంశ", "భావం", "భావ స్థానం", "బలం / గౌరవం"],
        "houses_headers": ["భావం", "రాశి", "ప్రారంభ అంశ", "భావాధిపతి", "స్థిత గ్రహాలు"],
        "aspects_headers": ["గ్రహం", "దృష్టి", "గ్రహం", "అంతరం (orb)", "గతి"],
        "vargas_headers": ["గ్రహం / లగ్నం", "D1 (రాశి)", "D3 (ద్రేక్కాణం)", "D7 (సప్తాంశ)",
                           "D9 (నవాంశ)", "D10 (దశాంశ)", "D12 (ద్వాదశాంశ)"],
        "yogas_headers": ["యోగం", "వర్గం", "గ్రహాలు", "ఫలం / వివరణ"],
        "no_yogas": "ముఖ్య యోగాలు ఏర్పడలేదు",
        "no_yogas_note": "గ్రహ శాంతి కోసం నిత్యం ప్రార్థన మరియు మంత్ర జపం చేయండి.",
        "english_sections": "ఈ వివరణ భాగాలు ఆంగ్లంలో చూపబడ్డాయి.",
    },
    "ta": {
        "title": "ஜாதக அறிக்கை", "born": "பிறந்த நேரம்", "at": "பிறந்த இடம்",
        "system": "முறை", "generated": "தேதி", "birth_details": "பிறப்பு விவரங்கள்",
        "d1_title": "ராசி சக்கரம் (D1)", "d9_title": "நவாம்ச சக்கரம் (D9)",
        "north_indian": "வட இந்திய முறை", "south_indian": "தென் இந்திய முறை",
        "planetary_positions": "கிரக நிலைகள்", "houses": "பாவ நிலைகள்",
        "aspects": "முக்கிய பார்வைகள்", "dasha": "விம்சோத்தரி தசை",
        "varshphal_title": "மாதவாரி வருட பலன்", "upcoming_title": "வரவிருக்கும் முக்கிய காலங்கள்",
        "house_summary_title": "பாவ பலன் சுருக்கம்", "vargas_title": "வர்க்க சக்கர நிலைகள்",
        "ashtakavarga_title": "சர்வாஷ்டகவர்க்கம் (337 பரல்கள்)",
        "yogas_title": "ஜாதகத்தில் உள்ள முக்கிய யோகங்கள்",
        "antardasha_title": "நடப்பு மகா தசையின் புக்திகள்",
        "houses_detailed_title": "பன்னிரண்டு பாவ பலன்கள்",
        "planets_detailed_title": "கிரக பலன் விளக்கம்",
        "remedies_detailed_title": "பரிகாரங்களும் மந்திரங்களும்",
        "name": "பெயர்", "date_time": "பிறந்த தேதி மற்றும் நேரம்", "time_unknown": "நேரம் தெரியவில்லை",
        "place": "பிறந்த இடம்", "time_zone": "நேர மண்டலம்", "universal_time": "சர்வதேச நேரம் (UT)",
        "zodiac": "ராசி மண்டலம் / அயனாம்சம்", "ayanamsa": "அயனாம்சம்", "house_system": "பாவ முறை",
        "sect": "பிறப்பு காலம்", "day_chart": "பகல் பிறப்பு", "night_chart": "இரவு பிறப்பு",
        "moon": "சந்திரன்", "nakshatra": "நட்சத்திரம்", "pada": "பாதம்",
        "mahadasha_now": "நடப்பு மகா தசை", "antardasha_now": "நடப்பு புக்தி",
        "yogini_dasha": "யோகினி தசை", "yogini_antardasha": "யோகினி புக்தி",
        "as_of": "இந்தத் தேதியின்படி",
        "dasha_headers": ["மகா தசை", "ஆண்டுகள்", "தொடக்கம்", "முடிவு", "நிலை"],
        "antardasha_headers": ["புக்தி", "தொடக்கம்", "முடிவு", "நிலை"],
        "positions_headers": ["கிரகம்", "ராசி", "பாகை", "பாவம்", "பாவ நிலை", "பலம் / கௌரவம்"],
        "houses_headers": ["பாவம்", "ராசி", "தொடக்கப் பாகை", "பாவாதிபதி", "இருக்கும் கிரகங்கள்"],
        "aspects_headers": ["கிரகம்", "பார்வை", "கிரகம்", "இடைவெளி (orb)", "கதி"],
        "vargas_headers": ["கிரகம் / லக்னம்", "D1 (ராசி)", "D3 (திரேக்காணம்)", "D7 (சப்தாம்சம்)",
                           "D9 (நவாம்சம்)", "D10 (தசாம்சம்)", "D12 (துவாதசாம்சம்)"],
        "yogas_headers": ["யோகம்", "வகை", "கிரகங்கள்", "பலன் / விளக்கம்"],
        "no_yogas": "முக்கிய யோகங்கள் உருவாகவில்லை",
        "no_yogas_note": "கிரக சாந்திக்காக தினமும் பிரார்த்தனையும் மந்திர ஜபமும் செய்யவும்.",
        "english_sections": "இந்த விளக்கப் பகுதிகள் ஆங்கிலத்தில் காட்டப்பட்டுள்ளன.",
    },
    "ml": {
        "title": "ജാതക റിപ്പോർട്ട്", "born": "ജനന സമയം", "at": "ജനന സ്ഥലം",
        "system": "പദ്ധതി", "generated": "തീയതി", "birth_details": "ജനന വിവരങ്ങൾ",
        "d1_title": "രാശി ചക്രം (D1)", "d9_title": "നവാംശക ചക്രം (D9)",
        "north_indian": "ഉത്തരേന്ത്യൻ ശൈലി", "south_indian": "ദക്ഷിണേന്ത്യൻ ശൈലി",
        "planetary_positions": "ഗ്രഹസ്ഥിതി", "houses": "ഭാവസ്ഥിതി",
        "aspects": "പ്രധാന ദൃഷ്ടികൾ", "dasha": "വിംശോത്തരി ദശ",
        "varshphal_title": "മാസംതോറുമുള്ള വർഷഫലം", "upcoming_title": "വരാനിരിക്കുന്ന പ്രധാന കാലങ്ങൾ",
        "house_summary_title": "ഭാവഫല സംഗ്രഹം", "vargas_title": "വർഗ്ഗ ചക്ര സ്ഥിതി",
        "ashtakavarga_title": "സർവാഷ്ടകവർഗ്ഗം (337 ബിന്ദുക്കൾ)",
        "yogas_title": "ജാതകത്തിലെ പ്രധാന യോഗങ്ങൾ",
        "antardasha_title": "നടപ്പ് മഹാദശയിലെ അപഹാരങ്ങൾ",
        "houses_detailed_title": "ദ്വാദശ ഭാവഫല വിവരണം",
        "planets_detailed_title": "ഗ്രഹഫല വിവരണം",
        "remedies_detailed_title": "ജ്യോതിഷ പരിഹാരങ്ങളും മന്ത്രങ്ങളും",
        "name": "പേര്", "date_time": "ജനന തീയതിയും സമയവും", "time_unknown": "സമയം അറിയില്ല",
        "place": "ജനന സ്ഥലം", "time_zone": "സമയ മേഖല", "universal_time": "സാർവത്രിക സമയം (UT)",
        "zodiac": "രാശിചക്രം / അയനാംശം", "ayanamsa": "അയനാംശം", "house_system": "ഭാവ പദ്ധതി",
        "sect": "ജനന കാലം", "day_chart": "പകൽ ജനനം", "night_chart": "രാത്രി ജനനം",
        "moon": "ചന്ദ്രൻ", "nakshatra": "നക്ഷത്രം", "pada": "പാദം",
        "mahadasha_now": "നടപ്പ് മഹാദശ", "antardasha_now": "നടപ്പ് അപഹാരം",
        "yogini_dasha": "യോഗിനി ദശ", "yogini_antardasha": "യോഗിനി അപഹാരം",
        "as_of": "ഈ തീയതി പ്രകാരം",
        "dasha_headers": ["മഹാദശ", "വർഷങ്ങൾ", "ആരംഭം", "അവസാനം", "സ്ഥിതി"],
        "antardasha_headers": ["അപഹാരം", "ആരംഭം", "അവസാനം", "സ്ഥിതി"],
        "positions_headers": ["ഗ്രഹം", "രാശി", "അംശം", "ഭാവം", "ഭാവ സ്ഥാനം", "ബലം / ഗൗരവം"],
        "houses_headers": ["ഭാവം", "രാശി", "ആരംഭ അംശം", "ഭാവാധിപൻ", "നിൽക്കുന്ന ഗ്രഹങ്ങൾ"],
        "aspects_headers": ["ഗ്രഹം", "ദൃഷ്ടി", "ഗ്രഹം", "അന്തരം (orb)", "ഗതി"],
        "vargas_headers": ["ഗ്രഹം / ലഗ്നം", "D1 (രാശി)", "D3 (ദ്രേക്കാണം)", "D7 (സപ്താംശം)",
                           "D9 (നവാംശം)", "D10 (ദശാംശം)", "D12 (ദ്വാദശാംശം)"],
        "yogas_headers": ["യോഗം", "വിഭാഗം", "ഗ്രഹങ്ങൾ", "ഫലം / വിവരണം"],
        "no_yogas": "പ്രധാന യോഗങ്ങൾ രൂപപ്പെട്ടിട്ടില്ല",
        "no_yogas_note": "ഗ്രഹശാന്തിക്കായി ദിവസവും പ്രാർത്ഥനയും മന്ത്രജപവും ചെയ്യുക.",
        "english_sections": "ഈ വിവരണ ഭാഗങ്ങൾ ഇംഗ്ലീഷിലാണ് കാണിച്ചിരിക്കുന്നത്.",
    },
    "bn": {
        "title": "জন্মকুণ্ডলী প্রতিবেদন", "born": "জন্ম সময়", "at": "জন্মস্থান",
        "system": "পদ্ধতি", "generated": "তারিখ", "birth_details": "জন্ম বিবরণ",
        "d1_title": "রাশি চক্র (D1)", "d9_title": "নবাংশ চক্র (D9)",
        "north_indian": "উত্তর ভারতীয় শৈলী", "south_indian": "দক্ষিণ ভারতীয় শৈলী",
        "planetary_positions": "গ্রহের অবস্থান", "houses": "ভাবের অবস্থান",
        "aspects": "প্রধান দৃষ্টি", "dasha": "বিংশোত্তরী মহাদশা",
        "varshphal_title": "মাসিক বর্ষফল", "upcoming_title": "আসন্ন গুরুত্বপূর্ণ সময়",
        "house_summary_title": "ভাবফল সারাংশ", "vargas_title": "বর্গ চক্রে অবস্থান",
        "ashtakavarga_title": "সর্বাষ্টকবর্গ (337 বিন্দু)",
        "yogas_title": "কুণ্ডলীর প্রধান যোগ",
        "antardasha_title": "চলমান মহাদশার অন্তর্দশা",
        "houses_detailed_title": "দ্বাদশ ভাবফল বিশ্লেষণ",
        "planets_detailed_title": "গ্রহফল বিশ্লেষণ",
        "remedies_detailed_title": "জ্যোতিষ প্রতিকার ও মন্ত্র",
        "name": "নাম", "date_time": "জন্ম তারিখ ও সময়", "time_unknown": "সময় অজানা",
        "place": "জন্মস্থান", "time_zone": "সময় অঞ্চল", "universal_time": "সার্বজনীন সময় (UT)",
        "zodiac": "রাশিচক্র / অয়নাংশ", "ayanamsa": "অয়নাংশ", "house_system": "ভাব পদ্ধতি",
        "sect": "জন্মকাল", "day_chart": "দিবা জন্ম", "night_chart": "রাত্রি জন্ম",
        "moon": "চন্দ্র", "nakshatra": "নক্ষত্র", "pada": "পাদ",
        "mahadasha_now": "চলমান মহাদশা", "antardasha_now": "চলমান অন্তর্দশা",
        "yogini_dasha": "যোগিনী দশা", "yogini_antardasha": "যোগিনী অন্তর্দশা",
        "as_of": "এই তারিখ অনুযায়ী",
        "dasha_headers": ["মহাদশা", "বছর", "শুরু", "শেষ", "অবস্থা"],
        "antardasha_headers": ["অন্তর্দশা", "শুরু", "শেষ", "অবস্থা"],
        "positions_headers": ["গ্রহ", "রাশি", "অংশ", "ভাব", "ভাব-অবস্থান", "বল / মর্যাদা"],
        "houses_headers": ["ভাব", "রাশি", "আরম্ভ অংশ", "ভাবেশ", "অবস্থিত গ্রহ"],
        "aspects_headers": ["গ্রহ", "দৃষ্টি", "গ্রহ", "ব্যবধান (orb)", "গতি"],
        "vargas_headers": ["গ্রহ / লগ্ন", "D1 (রাশি)", "D3 (দ্রেক্কাণ)", "D7 (সপ্তাংশ)",
                           "D9 (নবাংশ)", "D10 (দশাংশ)", "D12 (দ্বাদশাংশ)"],
        "yogas_headers": ["যোগ", "শ্রেণি", "গ্রহ", "ফল / বিবরণ"],
        "no_yogas": "কোনো প্রধান যোগ গঠিত হয়নি",
        "no_yogas_note": "গ্রহশান্তির জন্য প্রতিদিন প্রার্থনা ও মন্ত্রজপ করুন।",
        "english_sections": "এই বিশ্লেষণ অংশগুলি ইংরেজিতে দেখানো হয়েছে।",
    },
    "or": {
        "title": "ଜନ୍ମ କୁଣ୍ଡଳୀ ବିବରଣୀ", "born": "ଜନ୍ମ ସମୟ", "at": "ଜନ୍ମ ସ୍ଥାନ",
        "system": "ପଦ୍ଧତି", "generated": "ତାରିଖ", "birth_details": "ଜନ୍ମ ବିବରଣୀ",
        "d1_title": "ରାଶି ଚକ୍ର (D1)", "d9_title": "ନବାଂଶ ଚକ୍ର (D9)",
        "north_indian": "ଉତ୍ତର ଭାରତୀୟ ଶୈଳୀ", "south_indian": "ଦକ୍ଷିଣ ଭାରତୀୟ ଶୈଳୀ",
        "planetary_positions": "ଗ୍ରହ ସ୍ଥିତି", "houses": "ଭାବ ସ୍ଥିତି",
        "aspects": "ପ୍ରମୁଖ ଦୃଷ୍ଟି", "dasha": "ବିଂଶୋତ୍ତରୀ ମହାଦଶା",
        "varshphal_title": "ମାସିକ ବର୍ଷଫଳ", "upcoming_title": "ଆଗାମୀ ଗୁରୁତ୍ୱପୂର୍ଣ୍ଣ ସମୟ",
        "house_summary_title": "ଭାବଫଳ ସାରାଂଶ", "vargas_title": "ବର୍ଗ ଚକ୍ର ସ୍ଥିତି",
        "ashtakavarga_title": "ସର୍ବାଷ୍ଟକବର୍ଗ (337 ବିନ୍ଦୁ)",
        "yogas_title": "କୁଣ୍ଡଳୀର ପ୍ରମୁଖ ଯୋଗ",
        "antardasha_title": "ଚାଲୁ ମହାଦଶାର ଅନ୍ତର୍ଦଶା",
        "houses_detailed_title": "ଦ୍ୱାଦଶ ଭାବଫଳ ବିଶ୍ଳେଷଣ",
        "planets_detailed_title": "ଗ୍ରହଫଳ ବିଶ୍ଳେଷଣ",
        "remedies_detailed_title": "ଜ୍ୟୋତିଷ ପ୍ରତିକାର ଓ ମନ୍ତ୍ର",
        "name": "ନାମ", "date_time": "ଜନ୍ମ ତାରିଖ ଓ ସମୟ", "time_unknown": "ସମୟ ଅଜଣା",
        "place": "ଜନ୍ମ ସ୍ଥାନ", "time_zone": "ସମୟ ମଣ୍ଡଳ", "universal_time": "ସାର୍ବଜନୀନ ସମୟ (UT)",
        "zodiac": "ରାଶିଚକ୍ର / ଅୟନାଂଶ", "ayanamsa": "ଅୟନାଂଶ", "house_system": "ଭାବ ପଦ୍ଧତି",
        "sect": "ଜନ୍ମ କାଳ", "day_chart": "ଦିବା ଜନ୍ମ", "night_chart": "ରାତ୍ରି ଜନ୍ମ",
        "moon": "ଚନ୍ଦ୍ର", "nakshatra": "ନକ୍ଷତ୍ର", "pada": "ପାଦ",
        "mahadasha_now": "ଚାଲୁ ମହାଦଶା", "antardasha_now": "ଚାଲୁ ଅନ୍ତର୍ଦଶା",
        "yogini_dasha": "ଯୋଗିନୀ ଦଶା", "yogini_antardasha": "ଯୋଗିନୀ ଅନ୍ତର୍ଦଶା",
        "as_of": "ଏହି ତାରିଖ ଅନୁସାରେ",
        "dasha_headers": ["ମହାଦଶା", "ବର୍ଷ", "ଆରମ୍ଭ", "ଶେଷ", "ସ୍ଥିତି"],
        "antardasha_headers": ["ଅନ୍ତର୍ଦଶା", "ଆରମ୍ଭ", "ଶେଷ", "ସ୍ଥିତି"],
        "positions_headers": ["ଗ୍ରହ", "ରାଶି", "ଅଂଶ", "ଭାବ", "ଭାବ ସ୍ଥାନ", "ବଳ / ମର୍ଯ୍ୟାଦା"],
        "houses_headers": ["ଭାବ", "ରାଶି", "ଆରମ୍ଭ ଅଂଶ", "ଭାବେଶ", "ସ୍ଥିତ ଗ୍ରହ"],
        "aspects_headers": ["ଗ୍ରହ", "ଦୃଷ୍ଟି", "ଗ୍ରହ", "ବ୍ୟବଧାନ (orb)", "ଗତି"],
        "vargas_headers": ["ଗ୍ରହ / ଲଗ୍ନ", "D1 (ରାଶି)", "D3 (ଦ୍ରେକ୍କାଣ)", "D7 (ସପ୍ତାଂଶ)",
                           "D9 (ନବାଂଶ)", "D10 (ଦଶାଂଶ)", "D12 (ଦ୍ୱାଦଶାଂଶ)"],
        "yogas_headers": ["ଯୋଗ", "ଶ୍ରେଣୀ", "ଗ୍ରହ", "ଫଳ / ବିବରଣୀ"],
        "no_yogas": "କୌଣସି ପ୍ରମୁଖ ଯୋଗ ଗଠିତ ହୋଇନାହିଁ",
        "no_yogas_note": "ଗ୍ରହ ଶାନ୍ତି ପାଇଁ ପ୍ରତିଦିନ ପ୍ରାର୍ଥନା ଓ ମନ୍ତ୍ର ଜପ କରନ୍ତୁ।",
        "english_sections": "ଏହି ବିଶ୍ଳେଷଣ ଅଂଶଗୁଡ଼ିକ ଇଂରାଜୀରେ ଦେଖାଯାଇଛି।",
    },
}

# Keys of pdf_report._LOCALIZED_TEXTS: the template reads d.texts.<key>.
TEXT_KEYS = (
    "title", "born", "at", "system", "generated", "birth_details", "d1_title", "d9_title",
    "north_indian", "south_indian", "planetary_positions", "houses", "aspects", "dasha",
    "varshphal_title", "upcoming_title", "house_summary_title", "vargas_title",
    "ashtakavarga_title", "yogas_title", "antardasha_title", "houses_detailed_title",
    "planets_detailed_title", "remedies_detailed_title",
)

# --------------------------------------------------------------------------
# Cell vocabulary — the engine's English words, matched case-insensitively
# --------------------------------------------------------------------------

_DIGNITY_KEYS = ("ruler", "domicile", "exalted", "exaltation", "exaltation_degree",
                 "exaltation_exact", "detriment", "fall", "triplicity", "term", "face",
                 "decan", "peregrine", "participating_ruler", "debilitated", "own",
                 "friendly", "neutral", "inimical", "moolatrikona")


def _dignities(own_lord, own, exalted, exalt_deg, exalt_max, enemy_sign, fall, trip, term,
               face, decan, weak, partner, friend, neutral, enemy, mt) -> dict[str, str]:
    values = (own_lord, own, exalted, exalted, exalt_deg, exalt_max, enemy_sign, fall, trip,
              term, face, decan, weak, partner, fall, own, friend, neutral, enemy, mt)
    return dict(zip(_DIGNITY_KEYS, values))


VOCAB: dict[str, dict[str, str]] = {
    "kn": {
        **_dignities("ಸ್ವಕ್ಷೇತ್ರ (ಅಧಿಪತಿ)", "ಸ್ವಕ್ಷೇತ್ರ", "ಉಚ್ಚ", "ಉಚ್ಚಾಂಶ", "ಪರಮೋಚ್ಚ",
                     "ಶತ್ರುಕ್ಷೇತ್ರ", "ನೀಚ", "ತ್ರಿಕೋಣ ಬಲ", "ಸೀಮಾ ಬಲ", "ದ್ರೇಕ್ಕಾಣ ಬಲ",
                     "ದ್ರೇಕ್ಕಾಣ", "ಬಲಹೀನ", "ಸಹಭಾಗಿ ಅಧಿಪತಿ", "ಮಿತ್ರ", "ಸಮ", "ಶತ್ರು",
                     "ಮೂಲತ್ರಿಕೋಣ"),
        "retrograde": "ವಕ್ರ", "direct": "ಮಾರ್ಗಿ", "combust": "ಅಸ್ತ", "yes": "ಹೌದು", "no": "ಇಲ್ಲ",
        "angular": "ಕೇಂದ್ರ", "succedent": "ಪಣಫರ", "cadent": "ಆಪೋಕ್ಲಿಮ",
        "conjunction": "ಯುತಿ", "opposition": "ಪ್ರತಿಯುತಿ (180°)",
        "square": "ಕೇಂದ್ರ ದೃಷ್ಟಿ (90°)", "trine": "ತ್ರಿಕೋಣ ದೃಷ್ಟಿ (120°)",
        "sextile": "ಷಷ್ಠಕ ದೃಷ್ಟಿ (60°)",
        "past": "ಮುಗಿದಿದೆ", "current": "ನಡೆಯುತ್ತಿದೆ", "ahead": "ಮುಂಬರುವ",
        "applying": "ಸಮೀಪಿಸುತ್ತಿದೆ", "separating": "ದೂರ ಸರಿಯುತ್ತಿದೆ",
        "sidereal": "ನಿರಯಣ (Sidereal)", "tropical": "ಸಾಯನ (Tropical)",
        "whole sign": "ರಾಶಿ ಭಾವ ಪದ್ಧತಿ (Whole Sign)", "equal house": "ಸಮ ಭಾವ (Equal House)",
        "lahiri": "ಲಾಹಿರಿ (ಚಿತ್ರಪಕ್ಷ)",
        "Uranus": "ಯುರೇನಸ್", "Neptune": "ನೆಪ್ಚೂನ್", "Pluto": "ಪ್ಲೂಟೊ", "Chiron": "ಕೈರಾನ್",
        "Lagna": "ಲಗ್ನ", "ASC": "ಲಗ್ನ", "MC": "ದಶಮ ಭಾವ", "DSC": "ಸಪ್ತಮ ಭಾವ", "IC": "ಚತುರ್ಥ ಭಾವ",
        "Mangala": "ಮಂಗಳಾ", "Pingala": "ಪಿಂಗಳಾ", "Dhanya": "ಧಾನ್ಯಾ", "Bhramari": "ಭ್ರಾಮರೀ",
        "Bhadrika": "ಭದ್ರಿಕಾ", "Ulka": "ಉಲ್ಕಾ", "Siddha": "ಸಿದ್ಧಾ", "Sankata": "ಸಂಕಟಾ",
    },
    "te": {
        **_dignities("స్వక్షేత్రం (అధిపతి)", "స్వక్షేత్రం", "ఉచ్ఛ", "ఉచ్ఛాంశ", "పరమోచ్ఛ",
                     "శత్రుక్షేత్రం", "నీచ", "త్రికోణ బలం", "సీమా బలం", "ద్రేక్కాణ బలం",
                     "ద్రేక్కాణం", "బలహీనం", "సహభాగి అధిపతి", "మిత్ర", "సమ", "శత్రు",
                     "మూలత్రికోణం"),
        "retrograde": "వక్రం", "direct": "మార్గి", "combust": "అస్తంగతం", "yes": "అవును", "no": "కాదు",
        "angular": "కేంద్రం", "succedent": "పణఫరం", "cadent": "ఆపోక్లిమం",
        "conjunction": "యుతి", "opposition": "ప్రతియుతి (180°)",
        "square": "కేంద్ర దృష్టి (90°)", "trine": "త్రికోణ దృష్టి (120°)",
        "sextile": "షష్ఠక దృష్టి (60°)",
        "past": "గతం", "current": "ప్రస్తుతం", "ahead": "రాబోయేది",
        "applying": "సమీపిస్తోంది", "separating": "దూరమవుతోంది",
        "sidereal": "నిరయన (Sidereal)", "tropical": "సాయన (Tropical)",
        "whole sign": "రాశి భావ పద్ధతి (Whole Sign)", "equal house": "సమ భావ (Equal House)",
        "lahiri": "లాహిరి (చిత్రపక్ష)",
        "Uranus": "యురేనస్", "Neptune": "నెప్ట్యూన్", "Pluto": "ప్లూటో", "Chiron": "కైరాన్",
        "Lagna": "లగ్నం", "ASC": "లగ్నం", "MC": "దశమ భావం", "DSC": "సప్తమ భావం", "IC": "చతుర్థ భావం",
        "Mangala": "మంగళా", "Pingala": "పింగళా", "Dhanya": "ధాన్యా", "Bhramari": "భ్రామరీ",
        "Bhadrika": "భద్రికా", "Ulka": "ఉల్కా", "Siddha": "సిద్ధా", "Sankata": "సంకటా",
    },
    "ta": {
        **_dignities("ஆட்சி (அதிபதி)", "ஆட்சி", "உச்சம்", "உச்ச பாகை", "பரம உச்சம்",
                     "பகை வீடு", "நீசம்", "திரிகோண பலம்", "எல்லை பலம்", "திரேக்காண பலம்",
                     "திரேக்காணம்", "பலமற்றது", "இணை அதிபதி", "நட்பு", "சமம்", "பகை",
                     "மூலத்திரிகோணம்"),
        "retrograde": "வக்ரம்", "direct": "நேர்கதி", "combust": "அஸ்தங்கம்", "yes": "ஆம்", "no": "இல்லை",
        "angular": "கேந்திரம்", "succedent": "பணபரம்", "cadent": "ஆபோக்லிமம்",
        "conjunction": "சேர்க்கை", "opposition": "எதிர்ப் பார்வை (180°)",
        "square": "கேந்திரப் பார்வை (90°)", "trine": "திரிகோணப் பார்வை (120°)",
        "sextile": "ஷஷ்டகப் பார்வை (60°)",
        "past": "முடிந்தது", "current": "நடப்பு", "ahead": "வரவிருப்பது",
        "applying": "நெருங்குகிறது", "separating": "விலகுகிறது",
        "sidereal": "நிராயனம் (Sidereal)", "tropical": "சாயனம் (Tropical)",
        "whole sign": "ராசி பாவ முறை (Whole Sign)", "equal house": "சம பாவம் (Equal House)",
        "lahiri": "லாஹிரி (சித்ரபக்ஷ)",
        "Uranus": "யுரேனஸ்", "Neptune": "நெப்டியூன்", "Pluto": "புளூட்டோ", "Chiron": "கைரான்",
        "Lagna": "லக்னம்", "ASC": "லக்னம்", "MC": "பத்தாம் பாவம்", "DSC": "ஏழாம் பாவம்",
        "IC": "நான்காம் பாவம்",
        "Mangala": "மங்களா", "Pingala": "பிங்களா", "Dhanya": "தான்யா", "Bhramari": "பிராமரி",
        "Bhadrika": "பத்ரிகா", "Ulka": "உல்கா", "Siddha": "சித்தா", "Sankata": "சங்கடா",
    },
    "ml": {
        **_dignities("സ്വക്ഷേത്രം (അധിപൻ)", "സ്വക്ഷേത്രം", "ഉച്ചം", "ഉച്ചാംശം", "പരമോച്ചം",
                     "ശത്രുക്ഷേത്രം", "നീചം", "ത്രികോണ ബലം", "സീമാ ബലം", "ദ്രേക്കാണ ബലം",
                     "ദ്രേക്കാണം", "ബലഹീനം", "സഹ അധിപൻ", "മിത്രം", "സമം", "ശത്രു",
                     "മൂലത്രികോണം"),
        "retrograde": "വക്രം", "direct": "നേർഗതി", "combust": "മൗഢ്യം", "yes": "അതെ", "no": "ഇല്ല",
        "angular": "കേന്ദ്രം", "succedent": "പണഫരം", "cadent": "ആപോക്ലിമം",
        "conjunction": "യുതി", "opposition": "പ്രതിയുതി (180°)",
        "square": "കേന്ദ്ര ദൃഷ്ടി (90°)", "trine": "ത്രികോണ ദൃഷ്ടി (120°)",
        "sextile": "ഷഷ്ഠക ദൃഷ്ടി (60°)",
        "past": "കഴിഞ്ഞത്", "current": "നടപ്പ്", "ahead": "വരാനിരിക്കുന്നത്",
        "applying": "അടുക്കുന്നു", "separating": "അകലുന്നു",
        "sidereal": "നിരയനം (Sidereal)", "tropical": "സായനം (Tropical)",
        "whole sign": "രാശി ഭാവ പദ്ധതി (Whole Sign)", "equal house": "സമ ഭാവം (Equal House)",
        "lahiri": "ലാഹിരി (ചിത്രപക്ഷ)",
        "Uranus": "യുറാനസ്", "Neptune": "നെപ്റ്റ്യൂൺ", "Pluto": "പ്ലൂട്ടോ", "Chiron": "കൈറോൺ",
        "Lagna": "ലഗ്നം", "ASC": "ലഗ്നം", "MC": "പത്താം ഭാവം", "DSC": "ഏഴാം ഭാവം",
        "IC": "നാലാം ഭാവം",
        "Mangala": "മംഗളാ", "Pingala": "പിംഗളാ", "Dhanya": "ധാന്യാ", "Bhramari": "ഭ്രാമരീ",
        "Bhadrika": "ഭദ്രികാ", "Ulka": "ഉൽക്കാ", "Siddha": "സിദ്ധാ", "Sankata": "സങ്കടാ",
    },
    "bn": {
        **_dignities("স্বক্ষেত্র (অধিপতি)", "স্বক্ষেত্র", "উচ্চ", "উচ্চাংশ", "পরমোচ্চ",
                     "শত্রুক্ষেত্র", "নীচ", "ত্রিকোণ বল", "সীমা বল", "দ্রেক্কাণ বল",
                     "দ্রেক্কাণ", "বলহীন", "সহ-অধিপতি", "মিত্র", "সম", "শত্রু",
                     "মূলত্রিকোণ"),
        "retrograde": "বক্রী", "direct": "মার্গী", "combust": "অস্তমিত", "yes": "হ্যাঁ", "no": "না",
        "angular": "কেন্দ্র", "succedent": "পণফর", "cadent": "আপোক্লিম",
        "conjunction": "যুতি", "opposition": "প্রতিযুতি (180°)",
        "square": "কেন্দ্র দৃষ্টি (90°)", "trine": "ত্রিকোণ দৃষ্টি (120°)",
        "sextile": "ষষ্ঠক দৃষ্টি (60°)",
        "past": "অতীত", "current": "চলমান", "ahead": "আসন্ন",
        "applying": "নিকটবর্তী হচ্ছে", "separating": "দূরে সরছে",
        "sidereal": "নিরয়ণ (Sidereal)", "tropical": "সায়ন (Tropical)",
        "whole sign": "রাশি ভাব পদ্ধতি (Whole Sign)", "equal house": "সম ভাব (Equal House)",
        "lahiri": "লাহিড়ী (চিত্রপক্ষ)",
        "Uranus": "ইউরেনাস", "Neptune": "নেপচুন", "Pluto": "প্লুটো", "Chiron": "কাইরন",
        "Lagna": "লগ্ন", "ASC": "লগ্ন", "MC": "দশম ভাব", "DSC": "সপ্তম ভাব", "IC": "চতুর্থ ভাব",
        "Mangala": "মঙ্গলা", "Pingala": "পিঙ্গলা", "Dhanya": "ধান্যা", "Bhramari": "ভ্রামরী",
        "Bhadrika": "ভদ্রিকা", "Ulka": "উল্কা", "Siddha": "সিদ্ধা", "Sankata": "সঙ্কটা",
    },
    "or": {
        **_dignities("ସ୍ୱକ୍ଷେତ୍ର (ଅଧିପତି)", "ସ୍ୱକ୍ଷେତ୍ର", "ଉଚ୍ଚ", "ଉଚ୍ଚାଂଶ", "ପରମୋଚ୍ଚ",
                     "ଶତ୍ରୁକ୍ଷେତ୍ର", "ନୀଚ", "ତ୍ରିକୋଣ ବଳ", "ସୀମା ବଳ", "ଦ୍ରେକ୍କାଣ ବଳ",
                     "ଦ୍ରେକ୍କାଣ", "ବଳହୀନ", "ସହ-ଅଧିପତି", "ମିତ୍ର", "ସମ", "ଶତ୍ରୁ",
                     "ମୂଳତ୍ରିକୋଣ"),
        "retrograde": "ବକ୍ରୀ", "direct": "ମାର୍ଗୀ", "combust": "ଅସ୍ତ", "yes": "ହଁ", "no": "ନା",
        "angular": "କେନ୍ଦ୍ର", "succedent": "ପଣଫର", "cadent": "ଆପୋକ୍ଲିମ",
        "conjunction": "ଯୁତି", "opposition": "ପ୍ରତିଯୁତି (180°)",
        "square": "କେନ୍ଦ୍ର ଦୃଷ୍ଟି (90°)", "trine": "ତ୍ରିକୋଣ ଦୃଷ୍ଟି (120°)",
        "sextile": "ଷଷ୍ଠକ ଦୃଷ୍ଟି (60°)",
        "past": "ଅତୀତ", "current": "ଚାଲୁ", "ahead": "ଆଗାମୀ",
        "applying": "ନିକଟତର ହେଉଛି", "separating": "ଦୂରେଇ ଯାଉଛି",
        "sidereal": "ନିରୟଣ (Sidereal)", "tropical": "ସାୟନ (Tropical)",
        "whole sign": "ରାଶି ଭାବ ପଦ୍ଧତି (Whole Sign)", "equal house": "ସମ ଭାବ (Equal House)",
        "lahiri": "ଲାହିରୀ (ଚିତ୍ରପକ୍ଷ)",
        "Uranus": "ୟୁରେନସ", "Neptune": "ନେପଚ୍ୟୁନ", "Pluto": "ପ୍ଲୁଟୋ", "Chiron": "କାଇରନ",
        "Lagna": "ଲଗ୍ନ", "ASC": "ଲଗ୍ନ", "MC": "ଦଶମ ଭାବ", "DSC": "ସପ୍ତମ ଭାବ", "IC": "ଚତୁର୍ଥ ଭାବ",
        "Mangala": "ମଙ୍ଗଳା", "Pingala": "ପିଙ୍ଗଳା", "Dhanya": "ଧାନ୍ୟା", "Bhramari": "ଭ୍ରାମରୀ",
        "Bhadrika": "ଭଦ୍ରିକା", "Ulka": "ଉଲ୍କା", "Siddha": "ସିଦ୍ଧା", "Sankata": "ସଙ୍କଟା",
    },
}

def texts(code: str) -> dict[str, str]:
    """The template's d.texts for `code` (only the section-heading keys)."""
    table = LABELS[code]
    return {k: table[k] for k in TEXT_KEYS}


def label(code: str, key: str):
    return LABELS[code][key]


@functools.lru_cache(maxsize=None)
def _proper(code: str) -> dict[str, str]:
    """Proper nouns, matched case-sensitively: grahas, rashis, nakshatras (from
    the names tables), outer planets, angles and yogini names (from VOCAB)."""
    from .astro.names_i18n import names_for

    n = names_for(code)
    out: dict[str, str] = {}
    out.update(n.GRAHA)
    out.update(n.RASHI)
    out.update(n.NAKSHATRAS)
    out.update({k: v for k, v in VOCAB[code].items() if k[:1].isupper()})
    # The chart bundle's Western names for the nodes.
    out.update({"True Node": n.GRAHA["Rahu"], "Mean Node": n.GRAHA["Rahu"],
                "North Node": n.GRAHA["Rahu"], "South Node": n.GRAHA["Ketu"]})
    return out


@functools.lru_cache(maxsize=None)
def _words(code: str) -> dict[str, str]:
    """Vocabulary matched case-insensitively (the engine is not consistent)."""
    return {k.lower(): v for k, v in VOCAB[code].items() if not k[:1].isupper()}


_DATE_DMY = re.compile(r"(\d+)\s+([A-Za-z]+)\s+(\d{4})(?:,\s+(\d+:\d+))?$")
_MONTH_NUM = {m: i for i, m in enumerate(
    ("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"), 1)}


def month_year(text: str, code: str) -> str:
    """"Jul 2019" -> "ಜುಲೈ 2019". The dasha summaries are month precision."""
    from .astro.names_i18n import names_for
    m = re.fullmatch(r"([A-Za-z]{3,9})\.?\s+(\d{4})", (text or "").strip())
    if not m or m.group(1)[:3].lower() not in _MONTH_NUM:
        return text
    return f"{names_for(code).MONTHS[_MONTH_NUM[m.group(1)[:3].lower()] - 1]} {m.group(2)}"


def long_date(day, code: str) -> str:
    """A date as "4 ಅಕ್ಟೋಬರ್ 2026"."""
    from .astro.names_i18n import names_for
    return f"{day.day} {names_for(code).MONTHS[day.month - 1]} {day.year}"


def translate(val, code: str):
    """One table cell from the engine's English into `code` (pdf_report's
    _translate_val for the regional languages). Unknown text is left as is."""
    if not isinstance(val, str):
        return str(val)
    v = val.strip()
    if not v:
        return val
    proper = _proper(code)
    if v in proper:
        return proper[v]
    words = _words(code)
    if v.lower() in words:
        return words[v.lower()]
    if v.endswith(" R") and v[:-2] in proper:
        return f"{proper[v[:-2]]} ({TERMS[code]['retrograde']})"
    if "," in v:
        return ", ".join(translate(p.strip(), code) for p in v.split(","))
    if "°" in v:
        from .astro.names_i18n import names_for
        for en, loc in names_for(code).RASHI.items():
            if en in v:
                return v.replace(en, loc)
        return v
    if " / " in v:
        return " / ".join(translate(p, code) for p in v.split(" / "))
    m = _DATE_DMY.match(v)
    if m and m.group(2)[:3].lower() in _MONTH_NUM:
        out = f"{int(m.group(1)):02d}-{_MONTH_NUM[m.group(2)[:3].lower()]:02d}-{m.group(3)}"
        return f"{out}, {m.group(4)}" if m.group(4) else out
    return val


# The North/South Indian squares are NOT translated. They are SVG drawn by
# stellium, and Typst rasterises SVG text without complex-script shaping: a
# Kannada label came out with its vowel signs on the wrong consonant and broken
# conjuncts (ಗುರು printed as ಗಹು) even with Noto Sans Kannada named as the
# font. The squares keep stellium's Latin abbreviations (Ari, Su, ...), which
# are correct; the captions under them are Typst text and are translated.
# (The Hindi squares are affected by the same limitation — see DIVASTRO-124.)
