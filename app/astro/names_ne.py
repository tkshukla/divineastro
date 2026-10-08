"""Nepali (नेपाली, Devanagari) names for the panchang, festivals and matching (DIVASTRO-145).

Same shape as names_kn.py / names_bn.py: one table per name, suffix _NE, keyed by the
ENGLISH name the engines emit; names_i18n.names_for("ne") exposes them. A key left "" falls
back to the English name; `python -m app.lang_data check ne` lists what is left.

Choices for a native reviewer to confirm:
  * Calendar: the site shows Gregorian dates and the Hindu lunar months (amanta, as the
    engine emits them). Bikram Sambat dates and months (Baisakh ... Chaitra as civil months)
    are NOT used. Lunar months are written as the Nepali patro names them: चैत्र बैशाख
    जेष्ठ आषाढ श्रावण भाद्र आश्विन कार्तिक मङ्सिर पौष माघ फाल्गुन.
  * Gregorian months as Nepali media write them: जनवरी, फेब्रुअरी, मार्च, अप्रिल, मे,
    जुन, जुलाई, अगस्ट, सेप्टेम्बर, अक्टोबर, नोभेम्बर, डिसेम्बर. Weekdays आइतबार ...
    शनिबार (बिहीबार, not बृहस्पतिबार).
  * Amavasya is औंसी, as in the Nepali patro (and Purnima is पूर्णिमा, kept).
  * Dussehra is विजयादशमी (दशैं), Diwali is दीपावली (तिहार), Bhai Dooj is भाइटीका,
    Holi is होली (फागु पूर्णिमा), Makar Sankranti is also माघे सङ्क्रान्ति: the Nepali
    names are added in brackets only where the engine's observance is the same festival.
  * Yamaganda is यमघण्ट, Gulika is गुलिक काल, Rahu Kaal is राहुकाल.
  * Rashi names in the Nepali patro form: मेष वृष मिथुन कर्कट सिंह कन्या तुला वृश्चिक धनु
    मकर कुम्भ मीन (कर्कट, not कर्क).
  * Nakshatra names without the Hindi feminine forms where Nepali patros drop them
    (पुष्य, हस्त, मूल, श्रवण).
  * Varjyam is वर्ज्य; Vishti karana is विष्टि (भद्रा).
"""

from __future__ import annotations


TITHI_NE = {
    "Pratipada": "प्रतिपदा",
    "Dwitiya": "द्वितीया",
    "Tritiya": "तृतीया",
    "Chaturthi": "चतुर्थी",
    "Panchami": "पञ्चमी",
    "Shashthi": "षष्ठी",
    "Saptami": "सप्तमी",
    "Ashtami": "अष्टमी",
    "Navami": "नवमी",
    "Dashami": "दशमी",
    "Ekadashi": "एकादशी",
    "Dwadashi": "द्वादशी",
    "Trayodashi": "त्रयोदशी",
    "Chaturdashi": "चतुर्दशी",
    "Purnima": "पूर्णिमा",
    "Amavasya": "औंसी",
}

NAKSHATRAS_NE = {
    "Ashwini": "अश्विनी",
    "Bharani": "भरणी",
    "Krittika": "कृत्तिका",
    "Rohini": "रोहिणी",
    "Mrigashira": "मृगशिरा",
    "Ardra": "आर्द्रा",
    "Punarvasu": "पुनर्वसु",
    "Pushya": "पुष्य",
    "Ashlesha": "आश्लेषा",
    "Magha": "मघा",
    "Purva Phalguni": "पूर्वफाल्गुनी",
    "Uttara Phalguni": "उत्तरफाल्गुनी",
    "Hasta": "हस्त",
    "Chitra": "चित्रा",
    "Swati": "स्वाती",
    "Vishakha": "विशाखा",
    "Anuradha": "अनुराधा",
    "Jyeshtha": "ज्येष्ठा",
    "Mula": "मूल",
    "Purva Ashadha": "पूर्वाषाढा",
    "Uttara Ashadha": "उत्तराषाढा",
    "Shravana": "श्रवण",
    "Dhanishta": "धनिष्ठा",
    "Shatabhisha": "शतभिषा",
    "Purva Bhadrapada": "पूर्वभाद्रपद",
    "Uttara Bhadrapada": "उत्तरभाद्रपद",
    "Revati": "रेवती",
}

VARA_NE = {
    "Sunday": "आइतबार",
    "Monday": "सोमबार",
    "Tuesday": "मङ्गलबार",
    "Wednesday": "बुधबार",
    "Thursday": "बिहीबार",
    "Friday": "शुक्रबार",
    "Saturday": "शनिबार",
}

YOGA_NE = {
    "Vishkambha": "विष्कम्भ",
    "Priti": "प्रीति",
    "Ayushman": "आयुष्मान",
    "Saubhagya": "सौभाग्य",
    "Shobhana": "शोभन",
    "Atiganda": "अतिगण्ड",
    "Sukarma": "सुकर्मा",
    "Dhriti": "धृति",
    "Shula": "शूल",
    "Ganda": "गण्ड",
    "Vriddhi": "वृद्धि",
    "Dhruva": "ध्रुव",
    "Vyaghata": "व्याघात",
    "Harshana": "हर्षण",
    "Vajra": "वज्र",
    "Siddhi": "सिद्धि",
    "Vyatipata": "व्यतिपात",
    "Variyana": "वरीयान",
    "Parigha": "परिघ",
    "Shiva": "शिव",
    "Siddha": "सिद्ध",
    "Sadhya": "साध्य",
    "Shubha": "शुभ",
    "Shukla": "शुक्ल",
    "Brahma": "ब्रह्म",
    "Indra": "ऐन्द्र",
    "Vaidhriti": "वैधृति",
}

KARANA_NE = {
    "Bava": "बव",
    "Balava": "बालव",
    "Kaulava": "कौलव",
    "Taitila": "तैतिल",
    "Gara": "गर",
    "Vanija": "वणिज",
    "Vishti": "विष्टि (भद्रा)",
    "Shakuni": "शकुनि",
    "Chatushpada": "चतुष्पाद",
    "Naga": "नाग",
    "Kimstughna": "किंस्तुघ्न",
}

PAKSHA_NE = {
    "Shukla": "शुक्ल पक्ष",
    "Krishna": "कृष्ण पक्ष",
}

MASA_NE = {
    "Chaitra": "चैत्र",
    "Vaishakha": "बैशाख",
    "Jyeshtha": "जेष्ठ",
    "Ashadha": "आषाढ",
    "Shravana": "श्रावण",
    "Bhadrapada": "भाद्र",
    "Ashwin": "आश्विन",
    "Kartika": "कार्तिक",
    "Margashirsha": "मङ्सिर",
    "Pausha": "पौष",
    "Magha": "माघ",
    "Phalguna": "फाल्गुन",
}

# lunar months are MASA; fill this only if the calendar is solar (keys "Aries".."Pisces")
SOLAR_MASA_NE = {}

RASHI_NE = {
    "Aries": "मेष",
    "Taurus": "वृष",
    "Gemini": "मिथुन",
    "Cancer": "कर्कट",
    "Leo": "सिंह",
    "Virgo": "कन्या",
    "Libra": "तुला",
    "Scorpio": "वृश्चिक",
    "Sagittarius": "धनु",
    "Capricorn": "मकर",
    "Aquarius": "कुम्भ",
    "Pisces": "मीन",
}

GRAHA_NE = {
    "Sun": "सूर्य",
    "Moon": "चन्द्रमा",
    "Mars": "मङ्गल",
    "Mercury": "बुध",
    "Jupiter": "बृहस्पति",
    "Venus": "शुक्र",
    "Saturn": "शनि",
    "Rahu": "राहु",
    "Ketu": "केतु",
}

CHOGHADIYA_NE = {
    "Amrit": "अमृत",
    "Shubh": "शुभ",
    "Labh": "लाभ",
    "Char": "चर",
    "Rog": "रोग",
    "Kaal": "काल",
    "Udveg": "उद्वेग",
}

CHOGHADIYA_QUALITY_NE = {
    "auspicious": "शुभ",   # Auspicious
    "neutral": "सामान्य",   # Neutral
    "inauspicious": "अशुभ",   # Inauspicious
}

TIMINGS_NE = {
    "rahu_kaal": "राहुकाल",   # Rahu Kaal
    "yamaganda": "यमघण्ट",   # Yamaganda
    "gulika": "गुलिक काल",   # Gulika Kaal
    "abhijit": "अभिजित मुहूर्त",   # Abhijit Muhurta
    "brahma_muhurta": "ब्रह्म मुहूर्त",   # Brahma Muhurta
    "pradosh": "प्रदोष काल",   # Pradosh Kaal
    "nishita": "निशीथ काल",   # Nishita Kaal
    "sunrise": "सूर्योदय",   # Sunrise
    "sunset": "सूर्यास्त",   # Sunset
    "moonrise": "चन्द्रोदय",   # Moonrise
    "moonset": "चन्द्रास्त",   # Moonset
    "parana": "पारण समय",   # Parana time
    "durmuhurtam": "दुर्मुहूर्त",   # Durmuhurtam
    "varjyam": "वर्ज्य",   # Varjyam
    "good_time": "शुभ समय",   # Good time
}

FESTIVAL_TIMINGS_NE = {
    "parana": "पारण (व्रत खोल्ने समय)",   # Parana (breaking the fast)
    "pradosh": "प्रदोष पूजा",   # Pradosh puja
    "pradosh_kaal": "प्रदोष काल",   # Pradosh kaal
    "moonrise": "चन्द्रोदय",   # Moonrise
    "madhyahna": "मध्याह्न पूजा मुहूर्त",   # Madhyahna puja muhurat
    "nishita": "निशीथ काल पूजा",   # Nishita kaal puja
    "aparahna": "अपराह्न पूजा",   # Aparahna puja
    "vijay": "विजय मुहूर्त",   # Vijay muhurat
    "ghatasthapana": "घटस्थापना मुहूर्त",   # Ghatasthapana muhurat
    "ghatasthapana_abhijit": "घटस्थापना (अभिजित)",   # Ghatasthapana (Abhijit)
    "lakshmi_puja": "लक्ष्मी पूजा मुहूर्त",   # Lakshmi puja muhurat
    "dhanteras_puja": "धनतेरस पूजा मुहूर्त",   # Dhanteras puja muhurat
    "vrishabha": "वृष काल (स्थिर लग्न)",   # Vrishabha kaal (sthir lagna)
    "punya_kaal": "पुण्य काल",   # Punya kaal
    "maha_punya_kaal": "महापुण्य काल",   # Maha punya kaal
    "sankranti": "सङ्क्रान्ति क्षण",   # Sankranti moment
    "holika_dahan": "होलिका दहन मुहूर्त",   # Holika Dahan muhurat
    "holika_after_bhadra": "भद्रा सकिएपछि होलिका दहन",   # Holika Dahan after Bhadra ends
    "rakhi": "राखी बाँध्ने मुहूर्त",   # Rakhi muhurat
    "karwa_puja": "पूजा मुहूर्त",   # Puja muhurat
    "puja": "पूजा मुहूर्त",   # Puja muhurat
    "sandhya_arghya": "साँझको अर्घ्य (सूर्यास्त)",   # Sandhya arghya (sunset)
    "usha_arghya": "बिहानको अर्घ्य (भोलिपल्ट सूर्योदय)",   # Usha arghya (sunrise, next day)
    "pratah": "प्रातःकाल मुहूर्त",   # Pratahkala muhurat
    "sayahna": "सायंकाल मुहूर्त",   # Sayahnakala muhurat
    "tithi": "तिथि",   # Tithi
    "dwadashi_end": "द्वादशी समाप्त",   # Dwadashi ends
    "hari_vasara_end": "हरि वासर समाप्त",   # Hari Vasara ends
    "kutup": "कुतुप मुहूर्त",   # Kutup muhurat
    "rohina": "रौहिण मुहूर्त",   # Rohina muhurat
    "aparahna_kaal": "अपराह्न काल",   # Aparahna kaal
    "abhyang": "अभ्यङ्ग स्नान (चन्द्रोदयदेखि सूर्योदयसम्म)",   # Abhyang snan (moonrise to sunrise)
}

FESTIVALS_NE = {
    "pradosh": "प्रदोष व्रत",   # Pradosh Vrat
    "sankashti": "सङ्कष्टी चतुर्थी",   # Sankashti Chaturthi
    "vinayaka": "विनायक चतुर्थी",   # Vinayaka Chaturthi
    "purnima": "पूर्णिमा व्रत",   # Purnima Vrat
    "amavasya": "औंसी",   # Amavasya
    "masik_shivratri": "मासिक शिवरात्रि",   # Masik Shivratri
    "durgashtami": "मासिक दुर्गाष्टमी",   # Masik Durgashtami
    "kalashtami": "कालाष्टमी",   # Kalashtami
    "skanda_shashthi": "स्कन्द षष्ठी",   # Skanda Shashthi
    "maha_shivratri": "महाशिवरात्रि",   # Maha Shivratri
    "holika_dahan": "होलिका दहन",   # Holika Dahan
    "ram_navami": "रामनवमी",   # Ram Navami
    "hanuman_jayanti": "हनुमान जयन्ती",   # Hanuman Jayanti
    "akshaya_tritiya": "अक्षय तृतीया",   # Akshaya Tritiya
    "raksha_bandhan": "रक्षाबन्धन",   # Raksha Bandhan
    "janmashtami": "कृष्ण जन्माष्टमी",   # Krishna Janmashtami
    "ganesh_chaturthi": "गणेश चतुर्थी",   # Ganesh Chaturthi
    "chaitra_navratri": "चैत्र नवरात्र आरम्भ",   # Chaitra Navratri begins
    "navratri": "शारदीय नवरात्र आरम्भ (दशैं)",   # Sharad Navratri begins
    "dussehra": "विजयादशमी (दशैं)",   # Dussehra (Vijayadashami)
    "karwa_chauth": "करवा चौथ",   # Karwa Chauth
    "ahoi_ashtami": "अहोई अष्टमी",   # Ahoi Ashtami
    "dhanteras": "धनतेरस",   # Dhanteras
    "diwali": "दीपावली (तिहार, लक्ष्मी पूजा)",   # Diwali (Lakshmi Puja)
    "govardhan": "गोवर्धन पूजा",   # Govardhan Puja
    "bhai_dooj": "भाइटीका (भाइदूज)",   # Bhai Dooj
    "chhath": "छठ पूजा",   # Chhath Puja
    "vasant_panchami": "वसन्त पञ्चमी (श्रीपञ्चमी)",   # Vasant Panchami
    "guru_purnima": "गुरु पूर्णिमा",   # Guru Purnima
    "sharad_purnima": "शरद पूर्णिमा",   # Sharad Purnima
    "sakat_chauth": "सकट चौथ",   # Sakat Chauth
    "mauni_amavasya": "मौनी औंसी",   # Mauni Amavasya
    "sheetala_ashtami": "शीतला अष्टमी (बसोडा)",   # Sheetala Ashtami (Basoda)
    "gudi_padwa": "गुडी पाडवा / उगादी",   # Gudi Padwa / Ugadi
    "gangaur": "गणगौर",   # Gangaur
    "vat_savitri": "वट सावित्री व्रत",   # Vat Savitri Vrat
    "ganga_dussehra": "गङ्गा दशहरा",   # Ganga Dussehra
    "vat_purnima": "वट पूर्णिमा व्रत",   # Vat Purnima Vrat
    "hariyali_teej": "हरियाली तीज",   # Hariyali Teej
    "nag_panchami": "नाग पञ्चमी",   # Nag Panchami
    "kajari_teej": "कजरी तीज",   # Kajari Teej
    "hal_shashthi": "हल षष्ठी (ललही छठ)",   # Hal Shashthi (Lalahi Chhath)
    "hartalika_teej": "हरितालिका तीज",   # Hartalika Teej
    "rishi_panchami": "ऋषि पञ्चमी",   # Rishi Panchami
    "anant_chaturdashi": "अनन्त चतुर्दशी",   # Anant Chaturdashi
    "pitru_paksha": "पितृ पक्ष आरम्भ (प्रतिपदा श्राद्ध)",   # Pitru Paksha begins (Pratipada Shraddha)
    "jivitputrika": "जीवित्पुत्रिका व्रत (जितिया)",   # Jivitputrika Vrat (Jitiya)
    "sarva_pitru_amavasya": "सर्वपितृ औंसी (महालय)",   # Sarva Pitru Amavasya (Mahalaya)
    "narak_chaturdashi": "नरक चतुर्दशी (रूप चौदस)",   # Narak Chaturdashi (Roop Chaudas)
    "tulsi_vivah": "तुलसी विवाह",   # Tulsi Vivah
    "kartik_purnima": "कार्तिक पूर्णिमा",   # Kartik Purnima
    "dev_deepawali": "देव दीपावली",   # Dev Deepawali
    "makar_sankranti": "मकर सङ्क्रान्ति (माघे सङ्क्रान्ति)",   # Makar Sankranti
    "lohri": "लोहडी",   # Lohri
    "holi": "होली (फागु पूर्णिमा)",   # Holi
    "ekadashi": "एकादशी",   # Ekadashi
    "santan_saptami": "सन्तान सप्तमी",   # Santan Saptami
}

EKADASHI_NE = {
    "Kamada Ekadashi": "कामदा एकादशी",
    "Varuthini Ekadashi": "वरुथिनी एकादशी",
    "Mohini Ekadashi": "मोहिनी एकादशी",
    "Apara Ekadashi": "अपरा एकादशी",
    "Nirjala Ekadashi": "निर्जला एकादशी",
    "Yogini Ekadashi": "योगिनी एकादशी",
    "Devshayani Ekadashi": "देवशयनी एकादशी (हरिशयनी)",
    "Kamika Ekadashi": "कामिका एकादशी",
    "Shravana Putrada Ekadashi": "श्रावण पुत्रदा एकादशी",
    "Aja Ekadashi": "अजा एकादशी",
    "Parsva Ekadashi": "परिवर्तिनी एकादशी (पार्श्व)",
    "Indira Ekadashi": "इन्दिरा एकादशी",
    "Papankusha Ekadashi": "पापाङ्कुशा एकादशी",
    "Rama Ekadashi": "रमा एकादशी",
    "Devutthana Ekadashi": "देवउठनी एकादशी (हरिबोधिनी)",
    "Utpanna Ekadashi": "उत्पन्ना एकादशी",
    "Mokshada Ekadashi": "मोक्षदा एकादशी",
    "Saphala Ekadashi": "सफला एकादशी",
    "Pausha Putrada Ekadashi": "पौष पुत्रदा एकादशी",
    "Shattila Ekadashi": "षट्तिला एकादशी",
    "Jaya Ekadashi": "जया एकादशी",
    "Vijaya Ekadashi": "विजया एकादशी",
    "Amalaki Ekadashi": "आमलकी एकादशी",
    "Papmochani Ekadashi": "पापमोचनी एकादशी",
    "Padmini Ekadashi": "पद्मिनी एकादशी",
    "Parama Ekadashi": "परमा एकादशी",
}

# optional strong regional framing per festival key
REGIONAL_NOTE_NE = {}

KOOTA_NE = {
    "varna": "वर्ण",   # Varna
    "vashya": "वश्य",   # Vashya
    "tara": "तारा (दिन)",   # Tara (Dina)
    "yoni": "योनि",   # Yoni
    "graha_maitri": "ग्रह मैत्री",   # Graha Maitri
    "gana": "गण",   # Gana
    "bhakoot": "भकूट",   # Bhakoot
    "nadi": "नाडी",   # Nadi
}

GANA_NE = {
    "Deva": "देव",
    "Manushya": "मनुष्य",
    "Rakshasa": "राक्षस",
}

NADI_NE = {
    "Adi": "आद्य",
    "Madhya": "मध्य",
    "Antya": "अन्त्य",
}

VARNA_NE = {
    "Brahmin": "ब्राह्मण",
    "Kshatriya": "क्षत्रिय",
    "Vaishya": "वैश्य",
    "Shudra": "शूद्र",
}

VASHYA_NE = {
    "Chatushpada": "चतुष्पाद",
    "Manava": "मानव",
    "Jalachara": "जलचर",
    "Vanachara": "वनचर",
    "Keeta": "कीट",
}

YONI_NE = {
    "Horse": "घोडा",
    "Elephant": "हात्ती",
    "Sheep": "भेडा",
    "Serpent": "सर्प",
    "Dog": "कुकुर",
    "Cat": "बिरालो",
    "Rat": "मुसो",
    "Cow": "गाई",
    "Buffalo": "भैंसी",
    "Tiger": "बाघ",
    "Deer": "मृग",
    "Monkey": "बाँदर",
    "Mongoose": "न्यौरी",
    "Lion": "सिंह",
}

TARA_NE = {
    "Janma": "जन्म",
    "Sampat": "सम्पत्",
    "Vipat": "विपत्",
    "Kshema": "क्षेम",
    "Pratyak": "प्रत्यरि",
    "Sadhaka": "साधक",
    "Vadha": "वध",
    "Mitra": "मित्र",
    "Ati-Mitra": "अति मित्र",
}

WEEKDAY_NE = {
    "Sunday": "आइत",   # Sun
    "Monday": "सोम",   # Mon
    "Tuesday": "मङ्गल",   # Tue
    "Wednesday": "बुध",   # Wed
    "Thursday": "बिही",   # Thu
    "Friday": "शुक्र",   # Fri
    "Saturday": "शनि",   # Sat
}

MONTHS_NE = [
    "जनवरी",   # January
    "फेब्रुअरी",   # February
    "मार्च",   # March
    "अप्रिल",   # April
    "मे",   # May
    "जुन",   # June
    "जुलाई",   # July
    "अगस्ट",   # August
    "सेप्टेम्बर",   # September
    "अक्टोबर",   # October
    "नोभेम्बर",   # November
    "डिसेम्बर",   # December
]

CLOCK_NE = {
    "morning": "बिहान",
    "afternoon": "दिउँसो",
    "evening": "साँझ",
    "night": "राति",
}

LIMBS_NE = {
    "tithi": "तिथि",   # Tithi
    "nakshatra": "नक्षत्र",   # Nakshatra
    "yoga": "योग",   # Yoga
    "karana": "करण",   # Karana
    "vara": "वार",   # Vara
    "paksha": "पक्ष",   # Paksha
    "masa": "महिना",   # Month
    "moon_sign": "चन्द्र राशि",   # Moon sign
    "sun_sign": "सूर्य राशि",   # Sun sign
    "panchang": "पञ्चाङ्ग",   # Panchang
}

# EN: The Sun does not both rise and set on this date at this latitude, so the vedic day cannot be
#     bounded by sunrise. The limbs below are reckoned from local midnight instead, and the sunrise-
#     based muhurtas are not defined.
NOTE_POLAR_NE = "यस मितिमा यो अक्षांशमा सूर्य उदाउँदैन र अस्ताउँदैन पनि, त्यसैले वैदिक दिनलाई सूर्योदयले सीमाबद्ध गर्न सकिँदैन। तल दिइएका अङ्गहरू स्थानीय मध्यरातदेखि गणना गरिएका हुन्, र सूर्योदयमा आधारित मुहूर्तहरू परिभाषित छैनन्।"

# EN: Abhijit muhurta is omitted on Wednesday, whose lord Mercury is held to spoil it.
NOTE_WEDNESDAY_NE = "बुधबार अभिजित मुहूर्त गणना गरिँदैन, किनकि यसका स्वामी बुध ग्रहले यसलाई बिगार्छ भन्ने मान्यता छ।"


def add_ne(p: dict) -> dict:
    """add_hindi's twin for Nepali: name_ne / paksha_ne / label_ne / notes_ne."""
    from .names_i18n import add_names
    return add_names(p, "ne")
