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
    "Pratipada": "प्रतिपदा",
    "Dwitiya": "द्वितीया",
    "Tritiya": "तृतीया",
    "Chaturthi": "चतुर्थी",
    "Panchami": "पंचमी",
    "Shashthi": "षष्ठी",
    "Saptami": "सप्तमी",
    "Ashtami": "अष्टमी",
    "Navami": "नवमी",
    "Dashami": "दशमी",
    "Ekadashi": "एकादशी",
    "Dwadashi": "द्वादशी",
    "Trayodashi": "त्रयोदशी",
    "Chaturdashi": "चतुर्दशी",
    "Purnima": "पौर्णिमा",
    "Amavasya": "अमावस्या",
}

NAKSHATRAS_MR = {
    "Ashwini": "अश्विनी",
    "Bharani": "भरणी",
    "Krittika": "कृत्तिका",
    "Rohini": "रोहिणी",
    "Mrigashira": "मृगशीर्ष",
    "Ardra": "आर्द्रा",
    "Punarvasu": "पुनर्वसू",
    "Pushya": "पुष्य",
    "Ashlesha": "आश्लेषा",
    "Magha": "मघा",
    "Purva Phalguni": "पूर्वा फाल्गुनी",
    "Uttara Phalguni": "उत्तरा फाल्गुनी",
    "Hasta": "हस्त",
    "Chitra": "चित्रा",
    "Swati": "स्वाती",
    "Vishakha": "विशाखा",
    "Anuradha": "अनुराधा",
    "Jyeshtha": "ज्येष्ठा",
    "Mula": "मूळ",
    "Purva Ashadha": "पूर्वाषाढा",
    "Uttara Ashadha": "उत्तराषाढा",
    "Shravana": "श्रवण",
    "Dhanishta": "धनिष्ठा",
    "Shatabhisha": "शततारका",
    "Purva Bhadrapada": "पूर्वा भाद्रपदा",
    "Uttara Bhadrapada": "उत्तरा भाद्रपदा",
    "Revati": "रेवती",
}

VARA_MR = {
    "Sunday": "रविवार",
    "Monday": "सोमवार",
    "Tuesday": "मंगळवार",
    "Wednesday": "बुधवार",
    "Thursday": "गुरुवार",
    "Friday": "शुक्रवार",
    "Saturday": "शनिवार",
}

YOGA_MR = {
    "Vishkambha": "विष्कंभ",
    "Priti": "प्रीती",
    "Ayushman": "आयुष्मान",
    "Saubhagya": "सौभाग्य",
    "Shobhana": "शोभन",
    "Atiganda": "अतिगंड",
    "Sukarma": "सुकर्मा",
    "Dhriti": "धृती",
    "Shula": "शूल",
    "Ganda": "गंड",
    "Vriddhi": "वृद्धी",
    "Dhruva": "ध्रुव",
    "Vyaghata": "व्याघात",
    "Harshana": "हर्षण",
    "Vajra": "वज्र",
    "Siddhi": "सिद्धी",
    "Vyatipata": "व्यतिपात",
    "Variyana": "वरीयान",
    "Parigha": "परिघ",
    "Shiva": "शिव",
    "Siddha": "सिद्ध",
    "Sadhya": "साध्य",
    "Shubha": "शुभ",
    "Shukla": "शुक्ल",
    "Brahma": "ब्रह्म",
    "Indra": "इंद्र",
    "Vaidhriti": "वैधृती",
}

KARANA_MR = {
    "Bava": "बव",
    "Balava": "बालव",
    "Kaulava": "कौलव",
    "Taitila": "तैतिल",
    "Gara": "गर",
    "Vanija": "वणिज",
    "Vishti": "विष्टी (भद्रा)",
    "Shakuni": "शकुनी",
    "Chatushpada": "चतुष्पाद",
    "Naga": "नाग",
    "Kimstughna": "किंस्तुघ्न",
}

PAKSHA_MR = {
    "Shukla": "शुक्ल",
    "Krishna": "कृष्ण",
}

MASA_MR = {
    "Chaitra": "चैत्र",
    "Vaishakha": "वैशाख",
    "Jyeshtha": "ज्येष्ठ",
    "Ashadha": "आषाढ",
    "Shravana": "श्रावण",
    "Bhadrapada": "भाद्रपद",
    "Ashwin": "आश्विन",
    "Kartika": "कार्तिक",
    "Margashirsha": "मार्गशीर्ष",
    "Pausha": "पौष",
    "Magha": "माघ",
    "Phalguna": "फाल्गुन",
}

# lunar months are MASA; fill this only if the calendar is solar (keys "Aries".."Pisces")
SOLAR_MASA_MR = {}

RASHI_MR = {
    "Aries": "मेष",
    "Taurus": "वृषभ",
    "Gemini": "मिथुन",
    "Cancer": "कर्क",
    "Leo": "सिंह",
    "Virgo": "कन्या",
    "Libra": "तूळ",
    "Scorpio": "वृश्चिक",
    "Sagittarius": "धनु",
    "Capricorn": "मकर",
    "Aquarius": "कुंभ",
    "Pisces": "मीन",
}

GRAHA_MR = {
    "Sun": "सूर्य",
    "Moon": "चंद्र",
    "Mars": "मंगळ",
    "Mercury": "बुध",
    "Jupiter": "गुरू",
    "Venus": "शुक्र",
    "Saturn": "शनी",
    "Rahu": "राहू",
    "Ketu": "केतू",
}

CHOGHADIYA_MR = {
    "Amrit": "अमृत",
    "Shubh": "शुभ",
    "Labh": "लाभ",
    "Char": "चर",
    "Rog": "रोग",
    "Kaal": "काळ",
    "Udveg": "उद्वेग",
}

CHOGHADIYA_QUALITY_MR = {
    "auspicious": "शुभ",   # Auspicious
    "neutral": "मध्यम",   # Neutral
    "inauspicious": "अशुभ",   # Inauspicious
}

TIMINGS_MR = {
    "rahu_kaal": "राहुकाळ",   # Rahu Kaal
    "yamaganda": "यमगंड",   # Yamaganda
    "gulika": "गुलिक काळ",   # Gulika Kaal
    "abhijit": "अभिजित मुहूर्त",   # Abhijit Muhurta
    "brahma_muhurta": "ब्राह्ममुहूर्त",   # Brahma Muhurta
    "pradosh": "प्रदोषकाळ",   # Pradosh Kaal
    "nishita": "निशीथ काळ",   # Nishita Kaal
    "sunrise": "सूर्योदय",   # Sunrise
    "sunset": "सूर्यास्त",   # Sunset
    "moonrise": "चंद्रोदय",   # Moonrise
    "moonset": "चंद्रास्त",   # Moonset
    "parana": "पारणाची वेळ",   # Parana time
    "durmuhurtam": "दुर्मुहूर्त",   # Durmuhurtam
    "varjyam": "वर्ज्य",   # Varjyam
    "good_time": "शुभ वेळ",   # Good time
}

FESTIVAL_TIMINGS_MR = {
    "parana": "पारणे (उपवास सोडण्याची वेळ)",   # Parana (breaking the fast)
    "pradosh": "प्रदोष पूजा",   # Pradosh puja
    "pradosh_kaal": "प्रदोषकाळ",   # Pradosh kaal
    "moonrise": "चंद्रोदय",   # Moonrise
    "madhyahna": "मध्याह्न पूजेचा मुहूर्त",   # Madhyahna puja muhurat
    "nishita": "निशीथ काळातील पूजा",   # Nishita kaal puja
    "aparahna": "अपराह्न पूजा",   # Aparahna puja
    "vijay": "विजय मुहूर्त",   # Vijay muhurat
    "ghatasthapana": "घटस्थापनेचा मुहूर्त",   # Ghatasthapana muhurat
    "ghatasthapana_abhijit": "घटस्थापना (अभिजित)",   # Ghatasthapana (Abhijit)
    "lakshmi_puja": "लक्ष्मीपूजनाचा मुहूर्त",   # Lakshmi puja muhurat
    "dhanteras_puja": "धनत्रयोदशी पूजेचा मुहूर्त",   # Dhanteras puja muhurat
    "vrishabha": "वृषभ काळ (स्थिर लग्न)",   # Vrishabha kaal (sthir lagna)
    "punya_kaal": "पुण्यकाळ",   # Punya kaal
    "maha_punya_kaal": "महापुण्यकाळ",   # Maha punya kaal
    "sankranti": "संक्रांतीचा क्षण",   # Sankranti moment
    "holika_dahan": "होलिका दहनाचा मुहूर्त",   # Holika Dahan muhurat
    "holika_after_bhadra": "भद्रा संपल्यानंतर होलिका दहन",   # Holika Dahan after Bhadra ends
    "rakhi": "राखी बांधण्याचा मुहूर्त",   # Rakhi muhurat
    "karwa_puja": "पूजेचा मुहूर्त",   # Puja muhurat
    "puja": "पूजेचा मुहूर्त",   # Puja muhurat
    "sandhya_arghya": "संध्या अर्घ्य (सूर्यास्त)",   # Sandhya arghya (sunset)
    "usha_arghya": "उषा अर्घ्य (सूर्योदय, दुसऱ्या दिवशी)",   # Usha arghya (sunrise, next day)
    "pratah": "प्रातःकाळचा मुहूर्त",   # Pratahkala muhurat
    "sayahna": "सायंकाळचा मुहूर्त",   # Sayahnakala muhurat
    "tithi": "तिथी",   # Tithi
    "dwadashi_end": "द्वादशी समाप्ती",   # Dwadashi ends
    "hari_vasara_end": "हरिवासर समाप्ती",   # Hari Vasara ends
    "kutup": "कुतुप मुहूर्त",   # Kutup muhurat
    "rohina": "रौहिण मुहूर्त",   # Rohina muhurat
    "aparahna_kaal": "अपराह्न काळ",   # Aparahna kaal
    "abhyang": "अभ्यंगस्नान (चंद्रोदयापासून सूर्योदयापर्यंत)",   # Abhyang snan (moonrise to sunrise)
}

FESTIVALS_MR = {
    "pradosh": "प्रदोष व्रत",   # Pradosh Vrat
    "sankashti": "संकष्टी चतुर्थी",   # Sankashti Chaturthi
    "vinayaka": "विनायकी चतुर्थी",   # Vinayaka Chaturthi
    "purnima": "पौर्णिमा व्रत",   # Purnima Vrat
    "amavasya": "अमावस्या",   # Amavasya
    "masik_shivratri": "मासिक शिवरात्री",   # Masik Shivratri
    "durgashtami": "मासिक दुर्गाष्टमी",   # Masik Durgashtami
    "kalashtami": "कालाष्टमी",   # Kalashtami
    "skanda_shashthi": "स्कंद षष्ठी",   # Skanda Shashthi
    "maha_shivratri": "महाशिवरात्री",   # Maha Shivratri
    "holika_dahan": "होळी (होलिका दहन)",   # Holika Dahan
    "ram_navami": "रामनवमी",   # Ram Navami
    "hanuman_jayanti": "हनुमान जयंती",   # Hanuman Jayanti
    "akshaya_tritiya": "अक्षय्य तृतीया",   # Akshaya Tritiya
    "raksha_bandhan": "रक्षाबंधन",   # Raksha Bandhan
    "janmashtami": "श्रीकृष्ण जन्माष्टमी",   # Krishna Janmashtami
    "ganesh_chaturthi": "गणेश चतुर्थी",   # Ganesh Chaturthi
    "chaitra_navratri": "चैत्र नवरात्र प्रारंभ",   # Chaitra Navratri begins
    "navratri": "शारदीय नवरात्र प्रारंभ",   # Sharad Navratri begins
    "dussehra": "दसरा (विजयादशमी)",   # Dussehra (Vijayadashami)
    "karwa_chauth": "करवा चौथ",   # Karwa Chauth
    "ahoi_ashtami": "अहोई अष्टमी",   # Ahoi Ashtami
    "dhanteras": "धनत्रयोदशी",   # Dhanteras
    "diwali": "दिवाळी (लक्ष्मीपूजन)",   # Diwali (Lakshmi Puja)
    "govardhan": "गोवर्धन पूजा (दिवाळी पाडवा)",   # Govardhan Puja
    "bhai_dooj": "भाऊबीज",   # Bhai Dooj
    "chhath": "छठ पूजा",   # Chhath Puja
    "vasant_panchami": "वसंत पंचमी",   # Vasant Panchami
    "guru_purnima": "गुरुपौर्णिमा",   # Guru Purnima
    "sharad_purnima": "शरद पौर्णिमा (कोजागरी)",   # Sharad Purnima
    "sakat_chauth": "सकट चौथ",   # Sakat Chauth
    "mauni_amavasya": "मौनी अमावस्या",   # Mauni Amavasya
    "sheetala_ashtami": "शीतला अष्टमी",   # Sheetala Ashtami (Basoda)
    "gudi_padwa": "गुढीपाडवा (उगादी)",   # Gudi Padwa / Ugadi
    "gangaur": "गणगौर",   # Gangaur
    "vat_savitri": "वटसावित्री व्रत",   # Vat Savitri Vrat
    "ganga_dussehra": "गंगा दशहरा",   # Ganga Dussehra
    "vat_purnima": "वटपौर्णिमा व्रत",   # Vat Purnima Vrat
    "hariyali_teej": "हरियाली तीज",   # Hariyali Teej
    "nag_panchami": "नागपंचमी",   # Nag Panchami
    "kajari_teej": "कजरी तीज",   # Kajari Teej
    "hal_shashthi": "हल षष्ठी (बलराम जयंती)",   # Hal Shashthi (Lalahi Chhath)
    "hartalika_teej": "हरतालिका तृतीया",   # Hartalika Teej
    "rishi_panchami": "ऋषिपंचमी",   # Rishi Panchami
    "anant_chaturdashi": "अनंत चतुर्दशी",   # Anant Chaturdashi
    "pitru_paksha": "पितृपक्ष प्रारंभ (प्रतिपदा श्राद्ध)",   # Pitru Paksha begins (Pratipada Shraddha)
    "jivitputrika": "जीवितपुत्रिका व्रत (जितिया)",   # Jivitputrika Vrat (Jitiya)
    "sarva_pitru_amavasya": "सर्वपित्री अमावस्या (महालय)",   # Sarva Pitru Amavasya (Mahalaya)
    "narak_chaturdashi": "नरक चतुर्दशी (रूप चौदस)",   # Narak Chaturdashi (Roop Chaudas)
    "tulsi_vivah": "तुलसी विवाह",   # Tulsi Vivah
    "kartik_purnima": "कार्तिक पौर्णिमा (त्रिपुरारी पौर्णिमा)",   # Kartik Purnima
    "dev_deepawali": "देव दिवाळी",   # Dev Deepawali
    "makar_sankranti": "मकर संक्रांत",   # Makar Sankranti
    "lohri": "लोहरी",   # Lohri
    "holi": "धुळवड (रंगांची होळी)",   # Holi
    "ekadashi": "एकादशी",   # Ekadashi
    "santan_saptami": "संतान सप्तमी",   # Santan Saptami
}

EKADASHI_MR = {
    "Kamada Ekadashi": "कामदा एकादशी",
    "Varuthini Ekadashi": "वरूथिनी एकादशी",
    "Mohini Ekadashi": "मोहिनी एकादशी",
    "Apara Ekadashi": "अपरा एकादशी",
    "Nirjala Ekadashi": "निर्जला एकादशी",
    "Yogini Ekadashi": "योगिनी एकादशी",
    "Devshayani Ekadashi": "देवशयनी (आषाढी) एकादशी",
    "Kamika Ekadashi": "कामिका एकादशी",
    "Shravana Putrada Ekadashi": "श्रावण पुत्रदा एकादशी",
    "Aja Ekadashi": "अजा एकादशी",
    "Parsva Ekadashi": "पार्श्व (परिवर्तिनी) एकादशी",
    "Indira Ekadashi": "इंदिरा एकादशी",
    "Papankusha Ekadashi": "पापांकुशा एकादशी",
    "Rama Ekadashi": "रमा एकादशी",
    "Devutthana Ekadashi": "देवउठनी (कार्तिकी) एकादशी",
    "Utpanna Ekadashi": "उत्पन्ना एकादशी",
    "Mokshada Ekadashi": "मोक्षदा एकादशी",
    "Saphala Ekadashi": "सफला एकादशी",
    "Pausha Putrada Ekadashi": "पौष पुत्रदा एकादशी",
    "Shattila Ekadashi": "षट्तिला एकादशी",
    "Jaya Ekadashi": "जया (माघी) एकादशी",
    "Vijaya Ekadashi": "विजया एकादशी",
    "Amalaki Ekadashi": "आमलकी एकादशी",
    "Papmochani Ekadashi": "पापमोचनी एकादशी",
    "Padmini Ekadashi": "पद्मिनी एकादशी",
    "Parama Ekadashi": "परमा एकादशी",
}

# optional strong regional framing per festival key
REGIONAL_NOTE_MR = {}

KOOTA_MR = {
    "varna": "वर्ण",   # Varna
    "vashya": "वश्य",   # Vashya
    "tara": "तारा (दिनकूट)",   # Tara (Dina)
    "yoni": "योनी",   # Yoni
    "graha_maitri": "ग्रहमैत्री",   # Graha Maitri
    "gana": "गण",   # Gana
    "bhakoot": "भकूट",   # Bhakoot
    "nadi": "नाडी",   # Nadi
}

GANA_MR = {
    "Deva": "देव",
    "Manushya": "मनुष्य",
    "Rakshasa": "राक्षस",
}

NADI_MR = {
    "Adi": "आद्य",
    "Madhya": "मध्य",
    "Antya": "अंत्य",
}

VARNA_MR = {
    "Brahmin": "ब्राह्मण",
    "Kshatriya": "क्षत्रिय",
    "Vaishya": "वैश्य",
    "Shudra": "शूद्र",
}

VASHYA_MR = {
    "Chatushpada": "चतुष्पाद",
    "Manava": "मानव",
    "Jalachara": "जलचर",
    "Vanachara": "वनचर",
    "Keeta": "कीट",
}

YONI_MR = {
    "Horse": "घोडा",
    "Elephant": "हत्ती",
    "Sheep": "मेंढा",
    "Serpent": "साप",
    "Dog": "कुत्रा",
    "Cat": "मांजर",
    "Rat": "उंदीर",
    "Cow": "गाय",
    "Buffalo": "म्हैस",
    "Tiger": "वाघ",
    "Deer": "हरीण",
    "Monkey": "माकड",
    "Mongoose": "मुंगूस",
    "Lion": "सिंह",
}

TARA_MR = {
    "Janma": "जन्म",
    "Sampat": "संपत",
    "Vipat": "विपत",
    "Kshema": "क्षेम",
    "Pratyak": "प्रत्यरी",
    "Sadhaka": "साधक",
    "Vadha": "वध",
    "Mitra": "मैत्र",
    "Ati-Mitra": "अतिमैत्र",
}

WEEKDAY_MR = {
    "Sunday": "रवि",   # Sun
    "Monday": "सोम",   # Mon
    "Tuesday": "मंगळ",   # Tue
    "Wednesday": "बुध",   # Wed
    "Thursday": "गुरू",   # Thu
    "Friday": "शुक्र",   # Fri
    "Saturday": "शनी",   # Sat
}

MONTHS_MR = [
    "जानेवारी",   # January
    "फेब्रुवारी",   # February
    "मार्च",   # March
    "एप्रिल",   # April
    "मे",   # May
    "जून",   # June
    "जुलै",   # July
    "ऑगस्ट",   # August
    "सप्टेंबर",   # September
    "ऑक्टोबर",   # October
    "नोव्हेंबर",   # November
    "डिसेंबर",   # December
]

CLOCK_MR = {
    "morning": "सकाळी",
    "afternoon": "दुपारी",
    "evening": "संध्याकाळी",
    "night": "रात्री",
}

LIMBS_MR = {
    "tithi": "तिथी",   # Tithi
    "nakshatra": "नक्षत्र",   # Nakshatra
    "yoga": "योग",   # Yoga
    "karana": "करण",   # Karana
    "vara": "वार",   # Vara
    "paksha": "पक्ष",   # Paksha
    "masa": "मास",   # Month
    "moon_sign": "चंद्र रास",   # Moon sign
    "sun_sign": "सूर्य रास",   # Sun sign
    "panchang": "पंचांग",   # Panchang
}

# EN: The Sun does not both rise and set on this date at this latitude, so the vedic day cannot be
#     bounded by sunrise. The limbs below are reckoned from local midnight instead, and the sunrise-
#     based muhurtas are not defined.
NOTE_POLAR_MR = "या तारखेला या अक्षांशावर सूर्य उगवतही नाही आणि मावळतही नाही, त्यामुळे वैदिक दिवस सूर्योदयापासून मोजता येत नाही. खालील अंगे स्थानिक मध्यरात्रीपासून मोजली आहेत आणि सूर्योदयावर आधारित मुहूर्त लागू होत नाहीत."

# EN: Abhijit muhurta is omitted on Wednesday, whose lord Mercury is held to spoil it.
NOTE_WEDNESDAY_MR = "बुधवारी अभिजित मुहूर्त वगळला जातो, कारण वाराचा स्वामी बुध त्याला बिघडवतो असे मानले जाते."


def add_mr(p: dict) -> dict:
    """add_hindi's twin for Marathi: name_mr / paksha_mr / label_mr / notes_mr."""
    from .names_i18n import add_names
    return add_names(p, "mr")
