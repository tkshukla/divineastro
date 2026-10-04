"""Kannada (ಕನ್ನಡ) names for the panchang, festivals and matching (DIVASTRO-123).

Same shape as names_hi.py, with the suffix _KN, plus the extra tables that
names_i18n.names_for("kn") exposes. Every value is in Kannada script.

Regional choices (for a native reviewer):
  * Paksha is ಶುಕ್ಲ / ಕೃಷ್ಣ (the form Kannada panchanga sites print);
    traditional almanacs also write ಶುದ್ಧ / ಬಹುಳ.
  * Tithis use the everyday ಪಾಡ್ಯ, ಬಿದಿಗೆ, ತದಿಗೆ and ಹುಣ್ಣಿಮೆ (Purnima;
    ಪೌರ್ಣಮಿ is the formal alternative); Chaturthi is ಚತುರ್ಥಿ (ಚೌತಿ colloquial).
  * Nakshatras follow Kannada panchangas: ಮಖಾ, ಪುಬ್ಬ, ಉತ್ತರಾ, ಚಿತ್ತಾ.
  * Mars is ಕುಜ (astrological; ಮಂಗಳ is the alternative).
  * ರಾಹು ಕಾಲ, ಯಮಗಂಡ ಕಾಲ, ಗುಳಿಕ ಕಾಲ.
  * Hartalika Teej's day is Karnataka's ಗೌರಿ ಹಬ್ಬ; Govardhan Puja's day is
    ಬಲಿಪಾಡ್ಯಮಿ; Nag Panchami is ನಾಗರ ಪಂಚಮಿ.
"""

from __future__ import annotations

TITHI_KN = {
    "Pratipada": "ಪಾಡ್ಯ", "Dwitiya": "ಬಿದಿಗೆ", "Tritiya": "ತದಿಗೆ",
    "Chaturthi": "ಚತುರ್ಥಿ", "Panchami": "ಪಂಚಮಿ", "Shashthi": "ಷಷ್ಠಿ",
    "Saptami": "ಸಪ್ತಮಿ", "Ashtami": "ಅಷ್ಟಮಿ", "Navami": "ನವಮಿ",
    "Dashami": "ದಶಮಿ", "Ekadashi": "ಏಕಾದಶಿ", "Dwadashi": "ದ್ವಾದಶಿ",
    "Trayodashi": "ತ್ರಯೋದಶಿ", "Chaturdashi": "ಚತುರ್ದಶಿ", "Purnima": "ಹುಣ್ಣಿಮೆ",
    "Amavasya": "ಅಮಾವಾಸ್ಯೆ",
}

NAKSHATRAS_KN = {
    "Ashwini": "ಅಶ್ವಿನಿ", "Bharani": "ಭರಣಿ", "Krittika": "ಕೃತ್ತಿಕಾ", "Rohini": "ರೋಹಿಣಿ",
    "Mrigashira": "ಮೃಗಶಿರ", "Ardra": "ಆರ್ದ್ರಾ", "Punarvasu": "ಪುನರ್ವಸು",
    "Pushya": "ಪುಷ್ಯ", "Ashlesha": "ಆಶ್ಲೇಷ", "Magha": "ಮಖಾ",
    "Purva Phalguni": "ಪುಬ್ಬ",          # ಪೂರ್ವ ಫಲ್ಗುಣಿ
    "Uttara Phalguni": "ಉತ್ತರಾ",       # ಉತ್ತರ ಫಲ್ಗುಣಿ
    "Hasta": "ಹಸ್ತ", "Chitra": "ಚಿತ್ತಾ", "Swati": "ಸ್ವಾತಿ", "Vishakha": "ವಿಶಾಖ",
    "Anuradha": "ಅನುರಾಧ", "Jyeshtha": "ಜ್ಯೇಷ್ಠ", "Mula": "ಮೂಲ",
    "Purva Ashadha": "ಪೂರ್ವಾಷಾಢ", "Uttara Ashadha": "ಉತ್ತರಾಷಾಢ",
    "Shravana": "ಶ್ರವಣ", "Dhanishta": "ಧನಿಷ್ಠ", "Shatabhisha": "ಶತಭಿಷ",
    "Purva Bhadrapada": "ಪೂರ್ವಾಭಾದ್ರ", "Uttara Bhadrapada": "ಉತ್ತರಾಭಾದ್ರ",
    "Revati": "ರೇವತಿ",
}

VARA_KN = {
    "Sunday": "ಭಾನುವಾರ", "Monday": "ಸೋಮವಾರ", "Tuesday": "ಮಂಗಳವಾರ",
    "Wednesday": "ಬುಧವಾರ", "Thursday": "ಗುರುವಾರ", "Friday": "ಶುಕ್ರವಾರ",
    "Saturday": "ಶನಿವಾರ",
}

YOGA_KN = {
    "Vishkambha": "ವಿಷ್ಕಂಭ", "Priti": "ಪ್ರೀತಿ", "Ayushman": "ಆಯುಷ್ಮಾನ್",
    "Saubhagya": "ಸೌಭಾಗ್ಯ", "Shobhana": "ಶೋಭನ", "Atiganda": "ಅತಿಗಂಡ",
    "Sukarma": "ಸುಕರ್ಮ", "Dhriti": "ಧೃತಿ", "Shula": "ಶೂಲ", "Ganda": "ಗಂಡ",
    "Vriddhi": "ವೃದ್ಧಿ", "Dhruva": "ಧ್ರುವ", "Vyaghata": "ವ್ಯಾಘಾತ",
    "Harshana": "ಹರ್ಷಣ", "Vajra": "ವಜ್ರ", "Siddhi": "ಸಿದ್ಧಿ",
    "Vyatipata": "ವ್ಯತೀಪಾತ", "Variyana": "ವರೀಯಾನ್", "Parigha": "ಪರಿಘ",
    "Shiva": "ಶಿವ", "Siddha": "ಸಿದ್ಧ", "Sadhya": "ಸಾಧ್ಯ", "Shubha": "ಶುಭ",
    "Shukla": "ಶುಕ್ಲ", "Brahma": "ಬ್ರಹ್ಮ", "Indra": "ಐಂದ್ರ", "Vaidhriti": "ವೈಧೃತಿ",
}

KARANA_KN = {
    "Bava": "ಬವ", "Balava": "ಬಾಲವ", "Kaulava": "ಕೌಲವ", "Taitila": "ತೈತಿಲ",
    "Gara": "ಗರಜ", "Vanija": "ವಣಿಜ", "Vishti": "ವಿಷ್ಟಿ (ಭದ್ರಾ)", "Shakuni": "ಶಕುನಿ",
    "Chatushpada": "ಚತುಷ್ಪಾದ", "Naga": "ನಾಗ", "Kimstughna": "ಕಿಂಸ್ತುಘ್ನ",
}

PAKSHA_KN = {"Shukla": "ಶುಕ್ಲ", "Krishna": "ಕೃಷ್ಣ"}

NOTE_POLAR_KN = ("ಈ ದಿನಾಂಕದಂದು ಈ ಅಕ್ಷಾಂಶದಲ್ಲಿ ಸೂರ್ಯ ಉದಯಿಸುವುದೂ ಇಲ್ಲ, ಅಸ್ತಮಿಸುವುದೂ ಇಲ್ಲ; "
                 "ಆದ್ದರಿಂದ ವೈದಿಕ ದಿನವನ್ನು ಸೂರ್ಯೋದಯದಿಂದ ಎಣಿಸಲಾಗುವುದಿಲ್ಲ. ಕೆಳಗಿನ ಅಂಗಗಳನ್ನು "
                 "ಸ್ಥಳೀಯ ಮಧ್ಯರಾತ್ರಿಯಿಂದ ಎಣಿಸಲಾಗಿದೆ; ಸೂರ್ಯೋದಯ ಆಧಾರಿತ ಮುಹೂರ್ತಗಳು "
                 "ಅನ್ವಯಿಸುವುದಿಲ್ಲ.")
NOTE_WEDNESDAY_KN = ("ಬುಧವಾರ ಅಭಿಜಿತ್ ಮುಹೂರ್ತವನ್ನು ಪರಿಗಣಿಸುವುದಿಲ್ಲ — ವಾರದ ಅಧಿಪತಿ ಬುಧನು "
                     "ಅದನ್ನು ದೂಷಿತಗೊಳಿಸುತ್ತಾನೆ ಎಂದು ನಂಬಲಾಗಿದೆ.")

MASA_KN = {
    "Chaitra": "ಚೈತ್ರ", "Vaishakha": "ವೈಶಾಖ", "Jyeshtha": "ಜ್ಯೇಷ್ಠ",
    "Ashadha": "ಆಷಾಢ", "Shravana": "ಶ್ರಾವಣ", "Bhadrapada": "ಭಾದ್ರಪದ",
    "Ashwin": "ಆಶ್ವಯುಜ", "Kartika": "ಕಾರ್ತಿಕ", "Margashirsha": "ಮಾರ್ಗಶಿರ",
    "Pausha": "ಪುಷ್ಯ", "Magha": "ಮಾಘ", "Phalguna": "ಫಾಲ್ಗುಣ",
}

# Karnataka (except the coast, where Tulu/solar months are used) reckons by the
# lunar amanta month; no solar-month calendar is in daily use.
SOLAR_MASA_KN: dict[str, str] = {}

RASHI_KN = {
    "Aries": "ಮೇಷ", "Taurus": "ವೃಷಭ", "Gemini": "ಮಿಥುನ", "Cancer": "ಕರ್ಕಾಟಕ",
    "Leo": "ಸಿಂಹ", "Virgo": "ಕನ್ಯಾ", "Libra": "ತುಲಾ", "Scorpio": "ವೃಶ್ಚಿಕ",
    "Sagittarius": "ಧನು", "Capricorn": "ಮಕರ", "Aquarius": "ಕುಂಭ", "Pisces": "ಮೀನ",
}

GRAHA_KN = {
    "Sun": "ಸೂರ್ಯ", "Moon": "ಚಂದ್ರ", "Mars": "ಕುಜ", "Mercury": "ಬುಧ",
    "Jupiter": "ಗುರು", "Venus": "ಶುಕ್ರ", "Saturn": "ಶನಿ", "Rahu": "ರಾಹು", "Ketu": "ಕೇತು",
}

CHOGHADIYA_KN = {
    "Amrit": "ಅಮೃತ", "Shubh": "ಶುಭ", "Labh": "ಲಾಭ", "Char": "ಚರ",
    "Rog": "ರೋಗ", "Kaal": "ಕಾಲ", "Udveg": "ಉದ್ವೇಗ",
}
CHOGHADIYA_QUALITY_KN = {"auspicious": "ಶುಭ", "neutral": "ಮಧ್ಯಮ", "inauspicious": "ಅಶುಭ"}

TIMINGS_KN = {
    "rahu_kaal": "ರಾಹು ಕಾಲ", "yamaganda": "ಯಮಗಂಡ ಕಾಲ", "gulika": "ಗುಳಿಕ ಕಾಲ",
    "abhijit": "ಅಭಿಜಿತ್ ಮುಹೂರ್ತ", "brahma_muhurta": "ಬ್ರಹ್ಮ ಮುಹೂರ್ತ",
    "pradosh": "ಪ್ರದೋಷ ಕಾಲ", "nishita": "ನಿಶೀಥ ಕಾಲ",
    "sunrise": "ಸೂರ್ಯೋದಯ", "sunset": "ಸೂರ್ಯಾಸ್ತ",
    "moonrise": "ಚಂದ್ರೋದಯ", "moonset": "ಚಂದ್ರಾಸ್ತ",
    "parana": "ಪಾರಣೆ ಸಮಯ", "durmuhurtam": "ದುರ್ಮುಹೂರ್ತ", "varjyam": "ವರ್ಜ್ಯ",
    "good_time": "ಶುಭ ಸಮಯ",
}

FESTIVAL_TIMINGS_KN = {
    "parana": "ಪಾರಣೆ (ಉಪವಾಸ ಮುಕ್ತಾಯ)",
    "pradosh": "ಪ್ರದೋಷ ಪೂಜೆ",
    "pradosh_kaal": "ಪ್ರದೋಷ ಕಾಲ",
    "moonrise": "ಚಂದ್ರೋದಯ",
    "madhyahna": "ಮಧ್ಯಾಹ್ನ ಪೂಜಾ ಮುಹೂರ್ತ",
    "nishita": "ನಿಶೀಥ ಕಾಲ ಪೂಜೆ",
    "aparahna": "ಅಪರಾಹ್ನ ಪೂಜೆ",
    "vijay": "ವಿಜಯ ಮುಹೂರ್ತ",
    "ghatasthapana": "ಕಲಶ ಸ್ಥಾಪನೆ ಮುಹೂರ್ತ",
    "ghatasthapana_abhijit": "ಕಲಶ ಸ್ಥಾಪನೆ (ಅಭಿಜಿತ್)",
    "lakshmi_puja": "ಲಕ್ಷ್ಮೀ ಪೂಜಾ ಮುಹೂರ್ತ",
    "dhanteras_puja": "ಧನ ತ್ರಯೋದಶಿ ಪೂಜಾ ಮುಹೂರ್ತ",
    "vrishabha": "ವೃಷಭ ಕಾಲ (ಸ್ಥಿರ ಲಗ್ನ)",
    "punya_kaal": "ಪುಣ್ಯ ಕಾಲ",
    "maha_punya_kaal": "ಮಹಾ ಪುಣ್ಯ ಕಾಲ",
    "sankranti": "ಸಂಕ್ರಮಣ ಸಮಯ",
    "holika_dahan": "ಹೋಳಿಕಾ ದಹನ ಮುಹೂರ್ತ",
    "holika_after_bhadra": "ಭದ್ರಾ ಮುಗಿದ ನಂತರ ಹೋಳಿಕಾ ದಹನ",
    "rakhi": "ರಾಖಿ ಕಟ್ಟುವ ಮುಹೂರ್ತ",
    "karwa_puja": "ಪೂಜಾ ಮುಹೂರ್ತ",
    "puja": "ಪೂಜಾ ಮುಹೂರ್ತ",
    "sandhya_arghya": "ಸಂಧ್ಯಾ ಅರ್ಘ್ಯ (ಸೂರ್ಯಾಸ್ತ)",
    "usha_arghya": "ಉಷಾ ಅರ್ಘ್ಯ (ಸೂರ್ಯೋದಯ, ಮರುದಿನ)",
    "pratah": "ಪ್ರಾತಃಕಾಲ ಮುಹೂರ್ತ",
    "sayahna": "ಸಾಯಂಕಾಲ ಮುಹೂರ್ತ",
    "tithi": "ತಿಥಿ",
    "dwadashi_end": "ದ್ವಾದಶಿ ಮುಕ್ತಾಯ",
    "hari_vasara_end": "ಹರಿ ವಾಸರ ಮುಕ್ತಾಯ",
    "kutup": "ಕುತಪ ಮುಹೂರ್ತ",
    "rohina": "ರೌಹಿಣ ಮುಹೂರ್ತ",
    "aparahna_kaal": "ಅಪರಾಹ್ನ ಕಾಲ",
    "abhyang": "ಅಭ್ಯಂಗ ಸ್ನಾನ (ಚಂದ್ರೋದಯದಿಂದ ಸೂರ್ಯೋದಯದವರೆಗೆ)",
}

FESTIVALS_KN = {
    "pradosh": "ಪ್ರದೋಷ ವ್ರತ",
    "sankashti": "ಸಂಕಷ್ಟಹರ ಚತುರ್ಥಿ",
    "vinayaka": "ಮಾಸಿಕ ವಿನಾಯಕ ಚತುರ್ಥಿ",
    "purnima": "ಹುಣ್ಣಿಮೆ ವ್ರತ",
    "amavasya": "ಅಮಾವಾಸ್ಯೆ",
    "masik_shivratri": "ಮಾಸ ಶಿವರಾತ್ರಿ",
    "durgashtami": "ಮಾಸಿಕ ದುರ್ಗಾಷ್ಟಮಿ",
    "kalashtami": "ಕಾಲಾಷ್ಟಮಿ",
    "skanda_shashthi": "ಸ್ಕಂದ ಷಷ್ಠಿ",
    "maha_shivratri": "ಮಹಾ ಶಿವರಾತ್ರಿ",
    "holika_dahan": "ಹೋಳಿಕಾ ದಹನ (ಕಾಮದಹನ)",
    "ram_navami": "ಶ್ರೀ ರಾಮ ನವಮಿ",
    "hanuman_jayanti": "ಹನುಮ ಜಯಂತಿ",
    "akshaya_tritiya": "ಅಕ್ಷಯ ತೃತೀಯ",
    "raksha_bandhan": "ರಕ್ಷಾ ಬಂಧನ",
    "janmashtami": "ಶ್ರೀ ಕೃಷ್ಣ ಜನ್ಮಾಷ್ಟಮಿ (ಗೋಕುಲಾಷ್ಟಮಿ)",
    "ganesh_chaturthi": "ಗಣೇಶ ಚತುರ್ಥಿ",
    "chaitra_navratri": "ವಸಂತ ನವರಾತ್ರಿ ಆರಂಭ",
    "navratri": "ಶರನ್ನವರಾತ್ರಿ ಆರಂಭ",
    "dussehra": "ವಿಜಯದಶಮಿ (ದಸರಾ)",
    "karwa_chauth": "ಕರ್ವಾ ಚೌತ್",
    "ahoi_ashtami": "ಅಹೋಯಿ ಅಷ್ಟಮಿ",
    "dhanteras": "ಧನ ತ್ರಯೋದಶಿ",
    "diwali": "ದೀಪಾವಳಿ (ಲಕ್ಷ್ಮೀ ಪೂಜೆ)",
    "govardhan": "ಗೋವರ್ಧನ ಪೂಜೆ (ಬಲಿಪಾಡ್ಯಮಿ)",
    "bhai_dooj": "ಭಾಯಿ ದೂಜ್ (ಯಮ ದ್ವಿತೀಯಾ)",
    "chhath": "ಛಠ್ ಪೂಜೆ",
    "vasant_panchami": "ವಸಂತ ಪಂಚಮಿ",
    "guru_purnima": "ಗುರು ಪೂರ್ಣಿಮೆ",
    "sharad_purnima": "ಶರದ್ ಪೂರ್ಣಿಮೆ",
    "sakat_chauth": "ಸಕಟ್ ಚೌತ್",
    "mauni_amavasya": "ಮೌನಿ ಅಮಾವಾಸ್ಯೆ",
    "sheetala_ashtami": "ಶೀತಲಾ ಅಷ್ಟಮಿ",
    "gudi_padwa": "ಯುಗಾದಿ",
    "gangaur": "ಗಣಗೌರ್",
    "vat_savitri": "ವಟ ಸಾವಿತ್ರಿ ವ್ರತ",
    "ganga_dussehra": "ಗಂಗಾ ದಸರಾ",
    "vat_purnima": "ವಟ ಪೂರ್ಣಿಮೆ ವ್ರತ",
    "hariyali_teej": "ಹರಿಯಾಲಿ ತೀಜ್",
    "nag_panchami": "ನಾಗರ ಪಂಚಮಿ",
    "kajari_teej": "ಕಜರಿ ತೀಜ್",
    "hal_shashthi": "ಹಲ ಷಷ್ಠಿ (ಬಲರಾಮ ಜಯಂತಿ)",
    "hartalika_teej": "ಹರತಾಳಿಕಾ ವ್ರತ (ಗೌರಿ ಹಬ್ಬ)",
    "rishi_panchami": "ಋಷಿ ಪಂಚಮಿ",
    "anant_chaturdashi": "ಅನಂತ ಚತುರ್ದಶಿ (ಅನಂತ ಪದ್ಮನಾಭ ವ್ರತ)",
    "pitru_paksha": "ಪಿತೃ ಪಕ್ಷ (ಮಹಾಲಯ ಪಕ್ಷ) ಆರಂಭ",
    "jivitputrika": "ಜೀವಿತ್ಪುತ್ರಿಕಾ ವ್ರತ (ಜಿತಿಯಾ)",
    "sarva_pitru_amavasya": "ಮಹಾಲಯ ಅಮಾವಾಸ್ಯೆ",
    "narak_chaturdashi": "ನರಕ ಚತುರ್ದಶಿ",
    "tulsi_vivah": "ತುಳಸಿ ವಿವಾಹ (ಉತ್ಥಾನ ದ್ವಾದಶಿ)",
    "kartik_purnima": "ಕಾರ್ತಿಕ ಹುಣ್ಣಿಮೆ",
    "dev_deepawali": "ದೇವ ದೀಪಾವಳಿ",
    "makar_sankranti": "ಮಕರ ಸಂಕ್ರಾಂತಿ",
    "lohri": "ಲೋಹ್ರಿ",
    "holi": "ಹೋಳಿ",
    "ekadashi": "ಏಕಾದಶಿ",
    "santan_saptami": "ಸಂತಾನ ಸಪ್ತಮಿ",
}

EKADASHI_KN = {
    "Kamada Ekadashi": "ಕಾಮದಾ ಏಕಾದಶಿ",
    "Varuthini Ekadashi": "ವರೂಥಿನಿ ಏಕಾದಶಿ",
    "Mohini Ekadashi": "ಮೋಹಿನಿ ಏಕಾದಶಿ",
    "Apara Ekadashi": "ಅಪರಾ ಏಕಾದಶಿ",
    "Nirjala Ekadashi": "ನಿರ್ಜಲಾ ಏಕಾದಶಿ",
    "Yogini Ekadashi": "ಯೋಗಿನಿ ಏಕಾದಶಿ",
    "Devshayani Ekadashi": "ಶಯನಿ ಏಕಾದಶಿ (ಪ್ರಥಮ ಏಕಾದಶಿ)",
    "Kamika Ekadashi": "ಕಾಮಿಕಾ ಏಕಾದಶಿ",
    "Shravana Putrada Ekadashi": "ಶ್ರಾವಣ ಪುತ್ರದಾ ಏಕಾದಶಿ",
    "Aja Ekadashi": "ಅಜಾ ಏಕಾದಶಿ",
    "Parsva Ekadashi": "ಪರಿವರ್ತಿನಿ ಏಕಾದಶಿ",
    "Indira Ekadashi": "ಇಂದಿರಾ ಏಕಾದಶಿ",
    "Papankusha Ekadashi": "ಪಾಪಾಂಕುಶಾ ಏಕಾದಶಿ",
    "Rama Ekadashi": "ರಮಾ ಏಕಾದಶಿ",
    "Devutthana Ekadashi": "ಉತ್ಥಾನ ಏಕಾದಶಿ (ಪ್ರಬೋಧಿನಿ)",
    "Utpanna Ekadashi": "ಉತ್ಪನ್ನಾ ಏಕಾದಶಿ",
    "Mokshada Ekadashi": "ಮೋಕ್ಷದಾ ಏಕಾದಶಿ",
    "Saphala Ekadashi": "ಸಫಲಾ ಏಕಾದಶಿ",
    "Pausha Putrada Ekadashi": "ಪುಷ್ಯ ಪುತ್ರದಾ ಏಕಾದಶಿ",
    "Shattila Ekadashi": "ಷಟ್ತಿಲಾ ಏಕಾದಶಿ",
    "Jaya Ekadashi": "ಜಯಾ ಏಕಾದಶಿ",
    "Vijaya Ekadashi": "ವಿಜಯಾ ಏಕಾದಶಿ",
    "Amalaki Ekadashi": "ಆಮಲಕೀ ಏಕಾದಶಿ",
    "Papmochani Ekadashi": "ಪಾಪಮೋಚನಿ ಏಕಾದಶಿ",
    "Padmini Ekadashi": "ಪದ್ಮಿನಿ ಏಕಾದಶಿ",
    "Parama Ekadashi": "ಪರಮಾ ಏಕಾದಶಿ",
}

# Regional framings. Karnataka's Hanuman Jayanti is Margashirsha Shukla
# Trayodashi (a different date).
REGIONAL_NOTE_KN = {
    "navratri": "ಮೈಸೂರು ದಸರಾ",
    "dussehra": "ಮೈಸೂರು ದಸರಾ (ಜಂಬೂ ಸವಾರಿ)",
    "hartalika_teej": "ಗೌರಿ ಹಬ್ಬ",
    "govardhan": "ಬಲಿಪಾಡ್ಯಮಿ",
    "ganesh_chaturthi": "ಗಣೇಶ ಚೌತಿ",
}

KOOTA_KN = {
    "varna": "ವರ್ಣ", "vashya": "ವಶ್ಯ", "tara": "ತಾರಾ (ದಿನ)", "yoni": "ಯೋನಿ",
    "graha_maitri": "ಗ್ರಹ ಮೈತ್ರಿ", "gana": "ಗಣ", "bhakoot": "ರಾಶಿ (ಭಕೂಟ)",
    "nadi": "ನಾಡಿ",
}
GANA_KN = {"Deva": "ದೇವ", "Manushya": "ಮನುಷ್ಯ", "Rakshasa": "ರಾಕ್ಷಸ"}
NADI_KN = {"Adi": "ಆದಿ", "Madhya": "ಮಧ್ಯ", "Antya": "ಅಂತ್ಯ"}
VARNA_KN = {"Brahmin": "ಬ್ರಾಹ್ಮಣ", "Kshatriya": "ಕ್ಷತ್ರಿಯ", "Vaishya": "ವೈಶ್ಯ",
            "Shudra": "ಶೂದ್ರ"}
VASHYA_KN = {"Chatushpada": "ಚತುಷ್ಪಾದ", "Manava": "ಮಾನವ", "Jalachara": "ಜಲಚರ",
             "Vanachara": "ವನಚರ", "Keeta": "ಕೀಟ"}
YONI_KN = {
    "Horse": "ಕುದುರೆ", "Elephant": "ಆನೆ", "Sheep": "ಕುರಿ", "Serpent": "ಹಾವು",
    "Dog": "ನಾಯಿ", "Cat": "ಬೆಕ್ಕು", "Rat": "ಇಲಿ", "Cow": "ಹಸು", "Buffalo": "ಎಮ್ಮೆ",
    "Tiger": "ಹುಲಿ", "Deer": "ಜಿಂಕೆ", "Monkey": "ಕೋತಿ", "Mongoose": "ಮುಂಗುಸಿ",
    "Lion": "ಸಿಂಹ",
}
TARA_KN = {
    "Janma": "ಜನ್ಮ", "Sampat": "ಸಂಪತ್", "Vipat": "ವಿಪತ್", "Kshema": "ಕ್ಷೇಮ",
    "Pratyak": "ಪ್ರತ್ಯಕ್", "Sadhaka": "ಸಾಧಕ", "Vadha": "ವಧ", "Mitra": "ಮಿತ್ರ",
    "Ati-Mitra": "ಅತಿ ಮಿತ್ರ",
}

WEEKDAY_KN = {
    "Sunday": "ಭಾನು", "Monday": "ಸೋಮ", "Tuesday": "ಮಂಗಳ", "Wednesday": "ಬುಧ",
    "Thursday": "ಗುರು", "Friday": "ಶುಕ್ರ", "Saturday": "ಶನಿ",
}

MONTHS_KN = ["ಜನವರಿ", "ಫೆಬ್ರವರಿ", "ಮಾರ್ಚ್", "ಏಪ್ರಿಲ್", "ಮೇ", "ಜೂನ್", "ಜುಲೈ", "ಆಗಸ್ಟ್",
             "ಸೆಪ್ಟೆಂಬರ್", "ಅಕ್ಟೋಬರ್", "ನವೆಂಬರ್", "ಡಿಸೆಂಬರ್"]

CLOCK_KN = {"morning": "ಬೆಳಿಗ್ಗೆ", "afternoon": "ಮಧ್ಯಾಹ್ನ", "evening": "ಸಂಜೆ",
            "night": "ರಾತ್ರಿ"}

LIMBS_KN = {
    "tithi": "ತಿಥಿ", "nakshatra": "ನಕ್ಷತ್ರ", "yoga": "ಯೋಗ", "karana": "ಕರಣ",
    "vara": "ವಾರ", "paksha": "ಪಕ್ಷ", "masa": "ಮಾಸ", "moon_sign": "ಚಂದ್ರ ರಾಶಿ",
    "sun_sign": "ಸೂರ್ಯ ರಾಶಿ", "panchang": "ಪಂಚಾಂಗ",
}


def add_kn(p: dict) -> dict:
    """add_hindi's Kannada twin: name_kn / paksha_kn / label_kn / notes_kn."""
    from .names_i18n import add_names
    return add_names(p, "kn")
