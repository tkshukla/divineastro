"""Marathi (मराठी, Devanagari) names for the panchang, festivals and matching (DIVASTRO-143).

Same shape as names_kn.py / names_bn.py: one table per name, suffix _MR, keyed by the
ENGLISH name the engines emit; names_i18n.names_for("mr") exposes them. A key left "" (or a
table left out) falls back to the English name, so the site works while this fills up; `python -m
app.lang_data check mr` lists what is left. Use the names Marathi panchang and jyotish
tradition uses, in this language's script, not a transliteration of the English. Document
choices a native reviewer should confirm in this docstring (see names_bn.py).

Tables: TITHI(16) NAKSHATRAS(27) VARA(7) YOGA(27) KARANA(11) PAKSHA(2) MASA(12 lunar months)
SOLAR_MASA(optional: only if the calendar is solar) RASHI(12) GRAHA(9) CHOGHADIYA(7)
CHOGHADIYA_QUALITY(3) TIMINGS FESTIVAL_TIMINGS FESTIVALS EKADASHI REGIONAL_NOTE(optional)
KOOTA GANA NADI VARNA VASHYA YONI TARA WEEKDAY(7, short) MONTHS(12) CLOCK(4) LIMBS(10) and
the two notes NOTE_POLAR / NOTE_WEDNESDAY.
"""

from __future__ import annotations


TITHI_MR = {
    "Pratipada": "",
    "Dwitiya": "",
    "Tritiya": "",
    "Chaturthi": "",
    "Panchami": "",
    "Shashthi": "",
    "Saptami": "",
    "Ashtami": "",
    "Navami": "",
    "Dashami": "",
    "Ekadashi": "",
    "Dwadashi": "",
    "Trayodashi": "",
    "Chaturdashi": "",
    "Purnima": "",
    "Amavasya": "",
}

NAKSHATRAS_MR = {
    "Ashwini": "",
    "Bharani": "",
    "Krittika": "",
    "Rohini": "",
    "Mrigashira": "",
    "Ardra": "",
    "Punarvasu": "",
    "Pushya": "",
    "Ashlesha": "",
    "Magha": "",
    "Purva Phalguni": "",
    "Uttara Phalguni": "",
    "Hasta": "",
    "Chitra": "",
    "Swati": "",
    "Vishakha": "",
    "Anuradha": "",
    "Jyeshtha": "",
    "Mula": "",
    "Purva Ashadha": "",
    "Uttara Ashadha": "",
    "Shravana": "",
    "Dhanishta": "",
    "Shatabhisha": "",
    "Purva Bhadrapada": "",
    "Uttara Bhadrapada": "",
    "Revati": "",
}

VARA_MR = {
    "Sunday": "",
    "Monday": "",
    "Tuesday": "",
    "Wednesday": "",
    "Thursday": "",
    "Friday": "",
    "Saturday": "",
}

YOGA_MR = {
    "Vishkambha": "",
    "Priti": "",
    "Ayushman": "",
    "Saubhagya": "",
    "Shobhana": "",
    "Atiganda": "",
    "Sukarma": "",
    "Dhriti": "",
    "Shula": "",
    "Ganda": "",
    "Vriddhi": "",
    "Dhruva": "",
    "Vyaghata": "",
    "Harshana": "",
    "Vajra": "",
    "Siddhi": "",
    "Vyatipata": "",
    "Variyana": "",
    "Parigha": "",
    "Shiva": "",
    "Siddha": "",
    "Sadhya": "",
    "Shubha": "",
    "Shukla": "",
    "Brahma": "",
    "Indra": "",
    "Vaidhriti": "",
}

KARANA_MR = {
    "Bava": "",
    "Balava": "",
    "Kaulava": "",
    "Taitila": "",
    "Gara": "",
    "Vanija": "",
    "Vishti": "",
    "Shakuni": "",
    "Chatushpada": "",
    "Naga": "",
    "Kimstughna": "",
}

PAKSHA_MR = {
    "Shukla": "",
    "Krishna": "",
}

MASA_MR = {
    "Chaitra": "",
    "Vaishakha": "",
    "Jyeshtha": "",
    "Ashadha": "",
    "Shravana": "",
    "Bhadrapada": "",
    "Ashwin": "",
    "Kartika": "",
    "Margashirsha": "",
    "Pausha": "",
    "Magha": "",
    "Phalguna": "",
}

# lunar months are MASA; fill this only if the calendar is solar (keys "Aries".."Pisces")
SOLAR_MASA_MR = {}

RASHI_MR = {
    "Aries": "",
    "Taurus": "",
    "Gemini": "",
    "Cancer": "",
    "Leo": "",
    "Virgo": "",
    "Libra": "",
    "Scorpio": "",
    "Sagittarius": "",
    "Capricorn": "",
    "Aquarius": "",
    "Pisces": "",
}

GRAHA_MR = {
    "Sun": "",
    "Moon": "",
    "Mars": "",
    "Mercury": "",
    "Jupiter": "",
    "Venus": "",
    "Saturn": "",
    "Rahu": "",
    "Ketu": "",
}

CHOGHADIYA_MR = {
    "Amrit": "",
    "Shubh": "",
    "Labh": "",
    "Char": "",
    "Rog": "",
    "Kaal": "",
    "Udveg": "",
}

CHOGHADIYA_QUALITY_MR = {
    "auspicious": "",   # Auspicious
    "neutral": "",   # Neutral
    "inauspicious": "",   # Inauspicious
}

TIMINGS_MR = {
    "rahu_kaal": "",   # Rahu Kaal
    "yamaganda": "",   # Yamaganda
    "gulika": "",   # Gulika Kaal
    "abhijit": "",   # Abhijit Muhurta
    "brahma_muhurta": "",   # Brahma Muhurta
    "pradosh": "",   # Pradosh Kaal
    "nishita": "",   # Nishita Kaal
    "sunrise": "",   # Sunrise
    "sunset": "",   # Sunset
    "moonrise": "",   # Moonrise
    "moonset": "",   # Moonset
    "parana": "",   # Parana time
    "durmuhurtam": "",   # Durmuhurtam
    "varjyam": "",   # Varjyam
    "good_time": "",   # Good time
}

FESTIVAL_TIMINGS_MR = {
    "parana": "",   # Parana (breaking the fast)
    "pradosh": "",   # Pradosh puja
    "pradosh_kaal": "",   # Pradosh kaal
    "moonrise": "",   # Moonrise
    "madhyahna": "",   # Madhyahna puja muhurat
    "nishita": "",   # Nishita kaal puja
    "aparahna": "",   # Aparahna puja
    "vijay": "",   # Vijay muhurat
    "ghatasthapana": "",   # Ghatasthapana muhurat
    "ghatasthapana_abhijit": "",   # Ghatasthapana (Abhijit)
    "lakshmi_puja": "",   # Lakshmi puja muhurat
    "dhanteras_puja": "",   # Dhanteras puja muhurat
    "vrishabha": "",   # Vrishabha kaal (sthir lagna)
    "punya_kaal": "",   # Punya kaal
    "maha_punya_kaal": "",   # Maha punya kaal
    "sankranti": "",   # Sankranti moment
    "holika_dahan": "",   # Holika Dahan muhurat
    "holika_after_bhadra": "",   # Holika Dahan after Bhadra ends
    "rakhi": "",   # Rakhi muhurat
    "karwa_puja": "",   # Puja muhurat
    "puja": "",   # Puja muhurat
    "sandhya_arghya": "",   # Sandhya arghya (sunset)
    "usha_arghya": "",   # Usha arghya (sunrise, next day)
    "pratah": "",   # Pratahkala muhurat
    "sayahna": "",   # Sayahnakala muhurat
    "tithi": "",   # Tithi
    "dwadashi_end": "",   # Dwadashi ends
    "hari_vasara_end": "",   # Hari Vasara ends
    "kutup": "",   # Kutup muhurat
    "rohina": "",   # Rohina muhurat
    "aparahna_kaal": "",   # Aparahna kaal
    "abhyang": "",   # Abhyang snan (moonrise to sunrise)
}

FESTIVALS_MR = {
    "pradosh": "",   # Pradosh Vrat
    "sankashti": "",   # Sankashti Chaturthi
    "vinayaka": "",   # Vinayaka Chaturthi
    "purnima": "",   # Purnima Vrat
    "amavasya": "",   # Amavasya
    "masik_shivratri": "",   # Masik Shivratri
    "durgashtami": "",   # Masik Durgashtami
    "kalashtami": "",   # Kalashtami
    "skanda_shashthi": "",   # Skanda Shashthi
    "maha_shivratri": "",   # Maha Shivratri
    "holika_dahan": "",   # Holika Dahan
    "ram_navami": "",   # Ram Navami
    "hanuman_jayanti": "",   # Hanuman Jayanti
    "akshaya_tritiya": "",   # Akshaya Tritiya
    "raksha_bandhan": "",   # Raksha Bandhan
    "janmashtami": "",   # Krishna Janmashtami
    "ganesh_chaturthi": "",   # Ganesh Chaturthi
    "chaitra_navratri": "",   # Chaitra Navratri begins
    "navratri": "",   # Sharad Navratri begins
    "dussehra": "",   # Dussehra (Vijayadashami)
    "karwa_chauth": "",   # Karwa Chauth
    "ahoi_ashtami": "",   # Ahoi Ashtami
    "dhanteras": "",   # Dhanteras
    "diwali": "",   # Diwali (Lakshmi Puja)
    "govardhan": "",   # Govardhan Puja
    "bhai_dooj": "",   # Bhai Dooj
    "chhath": "",   # Chhath Puja
    "vasant_panchami": "",   # Vasant Panchami
    "guru_purnima": "",   # Guru Purnima
    "sharad_purnima": "",   # Sharad Purnima
    "sakat_chauth": "",   # Sakat Chauth
    "mauni_amavasya": "",   # Mauni Amavasya
    "sheetala_ashtami": "",   # Sheetala Ashtami (Basoda)
    "gudi_padwa": "",   # Gudi Padwa / Ugadi
    "gangaur": "",   # Gangaur
    "vat_savitri": "",   # Vat Savitri Vrat
    "ganga_dussehra": "",   # Ganga Dussehra
    "vat_purnima": "",   # Vat Purnima Vrat
    "hariyali_teej": "",   # Hariyali Teej
    "nag_panchami": "",   # Nag Panchami
    "kajari_teej": "",   # Kajari Teej
    "hal_shashthi": "",   # Hal Shashthi (Lalahi Chhath)
    "hartalika_teej": "",   # Hartalika Teej
    "rishi_panchami": "",   # Rishi Panchami
    "anant_chaturdashi": "",   # Anant Chaturdashi
    "pitru_paksha": "",   # Pitru Paksha begins (Pratipada Shraddha)
    "jivitputrika": "",   # Jivitputrika Vrat (Jitiya)
    "sarva_pitru_amavasya": "",   # Sarva Pitru Amavasya (Mahalaya)
    "narak_chaturdashi": "",   # Narak Chaturdashi (Roop Chaudas)
    "tulsi_vivah": "",   # Tulsi Vivah
    "kartik_purnima": "",   # Kartik Purnima
    "dev_deepawali": "",   # Dev Deepawali
    "makar_sankranti": "",   # Makar Sankranti
    "lohri": "",   # Lohri
    "holi": "",   # Holi
    "ekadashi": "",   # Ekadashi
    "santan_saptami": "",   # Santan Saptami
}

EKADASHI_MR = {
    "Kamada Ekadashi": "",
    "Varuthini Ekadashi": "",
    "Mohini Ekadashi": "",
    "Apara Ekadashi": "",
    "Nirjala Ekadashi": "",
    "Yogini Ekadashi": "",
    "Devshayani Ekadashi": "",
    "Kamika Ekadashi": "",
    "Shravana Putrada Ekadashi": "",
    "Aja Ekadashi": "",
    "Parsva Ekadashi": "",
    "Indira Ekadashi": "",
    "Papankusha Ekadashi": "",
    "Rama Ekadashi": "",
    "Devutthana Ekadashi": "",
    "Utpanna Ekadashi": "",
    "Mokshada Ekadashi": "",
    "Saphala Ekadashi": "",
    "Pausha Putrada Ekadashi": "",
    "Shattila Ekadashi": "",
    "Jaya Ekadashi": "",
    "Vijaya Ekadashi": "",
    "Amalaki Ekadashi": "",
    "Papmochani Ekadashi": "",
    "Padmini Ekadashi": "",
    "Parama Ekadashi": "",
}

# optional strong regional framing per festival key
REGIONAL_NOTE_MR = {}

KOOTA_MR = {
    "varna": "",   # Varna
    "vashya": "",   # Vashya
    "tara": "",   # Tara (Dina)
    "yoni": "",   # Yoni
    "graha_maitri": "",   # Graha Maitri
    "gana": "",   # Gana
    "bhakoot": "",   # Bhakoot
    "nadi": "",   # Nadi
}

GANA_MR = {
    "Deva": "",
    "Manushya": "",
    "Rakshasa": "",
}

NADI_MR = {
    "Adi": "",
    "Madhya": "",
    "Antya": "",
}

VARNA_MR = {
    "Brahmin": "",
    "Kshatriya": "",
    "Vaishya": "",
    "Shudra": "",
}

VASHYA_MR = {
    "Chatushpada": "",
    "Manava": "",
    "Jalachara": "",
    "Vanachara": "",
    "Keeta": "",
}

YONI_MR = {
    "Horse": "",
    "Elephant": "",
    "Sheep": "",
    "Serpent": "",
    "Dog": "",
    "Cat": "",
    "Rat": "",
    "Cow": "",
    "Buffalo": "",
    "Tiger": "",
    "Deer": "",
    "Monkey": "",
    "Mongoose": "",
    "Lion": "",
}

TARA_MR = {
    "Janma": "",
    "Sampat": "",
    "Vipat": "",
    "Kshema": "",
    "Pratyak": "",
    "Sadhaka": "",
    "Vadha": "",
    "Mitra": "",
    "Ati-Mitra": "",
}

WEEKDAY_MR = {
    "Sunday": "",   # Sun
    "Monday": "",   # Mon
    "Tuesday": "",   # Tue
    "Wednesday": "",   # Wed
    "Thursday": "",   # Thu
    "Friday": "",   # Fri
    "Saturday": "",   # Sat
}

MONTHS_MR = [
    "",   # January
    "",   # February
    "",   # March
    "",   # April
    "",   # May
    "",   # June
    "",   # July
    "",   # August
    "",   # September
    "",   # October
    "",   # November
    "",   # December
]

CLOCK_MR = {
    "morning": "",
    "afternoon": "",
    "evening": "",
    "night": "",
}

LIMBS_MR = {
    "tithi": "",   # Tithi
    "nakshatra": "",   # Nakshatra
    "yoga": "",   # Yoga
    "karana": "",   # Karana
    "vara": "",   # Vara
    "paksha": "",   # Paksha
    "masa": "",   # Month
    "moon_sign": "",   # Moon sign
    "sun_sign": "",   # Sun sign
    "panchang": "",   # Panchang
}

# EN: The Sun does not both rise and set on this date at this latitude, so the vedic day cannot be
#     bounded by sunrise. The limbs below are reckoned from local midnight instead, and the sunrise-
#     based muhurtas are not defined.
NOTE_POLAR_MR = ""

# EN: Abhijit muhurta is omitted on Wednesday, whose lord Mercury is held to spoil it.
NOTE_WEDNESDAY_MR = ""


def add_mr(p: dict) -> dict:
    """add_hindi's twin for Marathi: name_mr / paksha_mr / label_mr / notes_mr."""
    from .names_i18n import add_names
    return add_names(p, "mr")
