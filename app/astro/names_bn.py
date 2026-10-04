"""Bengali (বাংলা) names for the panchang, festivals and matching (DIVASTRO-123).

Same shape as names_hi.py, with the suffix _BN, plus the extra tables that
names_i18n.names_for("bn") exposes. Every value is in Bengali script; the
sentence-ending dari (।, U+0964) is shared with Devanagari and is allowed.

Regional choices (for a native reviewer):
  * Nakshatra names follow the Bengali panjika's feminine forms (পুষ্যা,
    হস্তা, মূলা, শ্রবণা).
  * The Bengali calendar (বঙ্গাব্দ) is SOLAR, starting at বৈশাখ (Sun in
    Mesha): those are SOLAR_MASA. Lunar month names are the same words
    (Margashirsha = অগ্রহায়ণ, Bhadrapada = ভাদ্র).
  * রাহুকাল, যমগণ্ড, গুলিক কাল. Bengali panjikas also print বারবেলা /
    কালবেলা / কালরাত্রি and অমৃতযোগ / মাহেন্দ্রযোগ, which this engine does
    not compute.
  * Varjyam is given as বর্জ্যম: plain বর্জ্য means "waste" in Bengali, so a
    reviewer should confirm (or drop it from the UI for bn).
  * Gana in matching is দেব / নর / রাক্ষস (নরগণ is the Bengali word);
    Nadi is আদ্য / মধ্য / অন্ত্য.
  * Bhai Dooj is ভাইফোঁটা; Vasant Panchami is সরস্বতী পূজা in Bengal;
    Sharad Navratri stays শারদীয় নবরাত্রি (দুর্গাপূজা is in REGIONAL_NOTE).
"""

from __future__ import annotations

TITHI_BN = {
    "Pratipada": "প্রতিপদ", "Dwitiya": "দ্বিতীয়া", "Tritiya": "তৃতীয়া",
    "Chaturthi": "চতুর্থী", "Panchami": "পঞ্চমী", "Shashthi": "ষষ্ঠী",
    "Saptami": "সপ্তমী", "Ashtami": "অষ্টমী", "Navami": "নবমী",
    "Dashami": "দশমী", "Ekadashi": "একাদশী", "Dwadashi": "দ্বাদশী",
    "Trayodashi": "ত্রয়োদশী", "Chaturdashi": "চতুর্দশী", "Purnima": "পূর্ণিমা",
    "Amavasya": "অমাবস্যা",
}

NAKSHATRAS_BN = {
    "Ashwini": "অশ্বিনী", "Bharani": "ভরণী", "Krittika": "কৃত্তিকা", "Rohini": "রোহিণী",
    "Mrigashira": "মৃগশিরা", "Ardra": "আর্দ্রা", "Punarvasu": "পুনর্বসু",
    "Pushya": "পুষ্যা", "Ashlesha": "অশ্লেষা", "Magha": "মঘা",
    "Purva Phalguni": "পূর্বফাল্গুনী", "Uttara Phalguni": "উত্তরফাল্গুনী",
    "Hasta": "হস্তা", "Chitra": "চিত্রা", "Swati": "স্বাতী", "Vishakha": "বিশাখা",
    "Anuradha": "অনুরাধা", "Jyeshtha": "জ্যেষ্ঠা", "Mula": "মূলা",
    "Purva Ashadha": "পূর্বাষাঢ়া", "Uttara Ashadha": "উত্তরাষাঢ়া",
    "Shravana": "শ্রবণা", "Dhanishta": "ধনিষ্ঠা", "Shatabhisha": "শতভিষা",
    "Purva Bhadrapada": "পূর্বভাদ্রপদ", "Uttara Bhadrapada": "উত্তরভাদ্রপদ",
    "Revati": "রেবতী",
}

VARA_BN = {
    "Sunday": "রবিবার", "Monday": "সোমবার", "Tuesday": "মঙ্গলবার",
    "Wednesday": "বুধবার", "Thursday": "বৃহস্পতিবার", "Friday": "শুক্রবার",
    "Saturday": "শনিবার",
}

YOGA_BN = {
    "Vishkambha": "বিষ্কম্ভ", "Priti": "প্রীতি", "Ayushman": "আয়ুষ্মান",
    "Saubhagya": "সৌভাগ্য", "Shobhana": "শোভন", "Atiganda": "অতিগণ্ড",
    "Sukarma": "সুকর্মা", "Dhriti": "ধৃতি", "Shula": "শূল", "Ganda": "গণ্ড",
    "Vriddhi": "বৃদ্ধি", "Dhruva": "ধ্রুব", "Vyaghata": "ব্যাঘাত",
    "Harshana": "হর্ষণ", "Vajra": "বজ্র", "Siddhi": "সিদ্ধি",
    "Vyatipata": "ব্যতীপাত", "Variyana": "বরীয়ান", "Parigha": "পরিঘ",
    "Shiva": "শিব", "Siddha": "সিদ্ধ", "Sadhya": "সাধ্য", "Shubha": "শুভ",
    "Shukla": "শুক্ল", "Brahma": "ব্রহ্ম", "Indra": "ইন্দ্র", "Vaidhriti": "বৈধৃতি",
}

KARANA_BN = {
    "Bava": "বব", "Balava": "বালব", "Kaulava": "কৌলব", "Taitila": "তৈতিল",
    "Gara": "গর", "Vanija": "বণিজ", "Vishti": "বিষ্টি (ভদ্রা)", "Shakuni": "শকুনি",
    "Chatushpada": "চতুষ্পদ", "Naga": "নাগ", "Kimstughna": "কিংস্তুঘ্ন",
}

PAKSHA_BN = {"Shukla": "শুক্ল", "Krishna": "কৃষ্ণ"}

NOTE_POLAR_BN = ("এই তারিখে এই অক্ষাংশে সূর্য ওঠেও না, অস্তও যায় না; তাই বৈদিক দিন "
                 "সূর্যোদয় থেকে গোনা যায় না। নীচের অঙ্গগুলি স্থানীয় মধ্যরাত্রি থেকে গণনা করা "
                 "হয়েছে, এবং সূর্যোদয়-ভিত্তিক মুহূর্ত প্রযোজ্য নয়।")
NOTE_WEDNESDAY_BN = ("বুধবারে অভিজিৎ মুহূর্ত গ্রহণ করা হয় না — বারের অধিপতি বুধ একে "
                     "দূষিত করেন বলে মানা হয়।")

MASA_BN = {
    "Chaitra": "চৈত্র", "Vaishakha": "বৈশাখ", "Jyeshtha": "জ্যৈষ্ঠ",
    "Ashadha": "আষাঢ়", "Shravana": "শ্রাবণ", "Bhadrapada": "ভাদ্র",
    "Ashwin": "আশ্বিন", "Kartika": "কার্তিক", "Margashirsha": "অগ্রহায়ণ",
    "Pausha": "পৌষ", "Magha": "মাঘ", "Phalguna": "ফাল্গুন",
}

# Bangla solar months (বঙ্গাব্দ), keyed by the sidereal sign the Sun is in.
SOLAR_MASA_BN = {
    "Aries": "বৈশাখ", "Taurus": "জ্যৈষ্ঠ", "Gemini": "আষাঢ়", "Cancer": "শ্রাবণ",
    "Leo": "ভাদ্র", "Virgo": "আশ্বিন", "Libra": "কার্তিক", "Scorpio": "অগ্রহায়ণ",
    "Sagittarius": "পৌষ", "Capricorn": "মাঘ", "Aquarius": "ফাল্গুন", "Pisces": "চৈত্র",
}

RASHI_BN = {
    "Aries": "মেষ", "Taurus": "বৃষ", "Gemini": "মিথুন", "Cancer": "কর্কট",
    "Leo": "সিংহ", "Virgo": "কন্যা", "Libra": "তুলা", "Scorpio": "বৃশ্চিক",
    "Sagittarius": "ধনু", "Capricorn": "মকর", "Aquarius": "কুম্ভ", "Pisces": "মীন",
}

GRAHA_BN = {
    "Sun": "সূর্য", "Moon": "চন্দ্র", "Mars": "মঙ্গল", "Mercury": "বুধ",
    "Jupiter": "বৃহস্পতি", "Venus": "শুক্র", "Saturn": "শনি", "Rahu": "রাহু",
    "Ketu": "কেতু",
}

CHOGHADIYA_BN = {
    "Amrit": "অমৃত", "Shubh": "শুভ", "Labh": "লাভ", "Char": "চর",
    "Rog": "রোগ", "Kaal": "কাল", "Udveg": "উদ্বেগ",
}
CHOGHADIYA_QUALITY_BN = {"auspicious": "শুভ", "neutral": "মধ্যম", "inauspicious": "অশুভ"}

TIMINGS_BN = {
    "rahu_kaal": "রাহুকাল", "yamaganda": "যমগণ্ড", "gulika": "গুলিক কাল",
    "abhijit": "অভিজিৎ মুহূর্ত", "brahma_muhurta": "ব্রাহ্মমুহূর্ত",
    "pradosh": "প্রদোষ কাল", "nishita": "নিশীথ কাল",
    "sunrise": "সূর্যোদয়", "sunset": "সূর্যাস্ত",
    "moonrise": "চন্দ্রোদয়", "moonset": "চন্দ্রাস্ত",
    "parana": "পারণের সময়", "durmuhurtam": "দুর্মুহূর্ত", "varjyam": "বর্জ্যম",
    "good_time": "শুভ সময়",
}

FESTIVAL_TIMINGS_BN = {
    "parana": "পারণ (উপবাস ভঙ্গ)",
    "pradosh": "প্রদোষ পূজা",
    "pradosh_kaal": "প্রদোষ কাল",
    "moonrise": "চন্দ্রোদয়",
    "madhyahna": "মধ্যাহ্ন পূজার মুহূর্ত",
    "nishita": "নিশীথ কালের পূজা",
    "aparahna": "অপরাহ্ণ পূজা",
    "vijay": "বিজয় মুহূর্ত",
    "ghatasthapana": "ঘটস্থাপনের মুহূর্ত",
    "ghatasthapana_abhijit": "ঘটস্থাপন (অভিজিৎ)",
    "lakshmi_puja": "লক্ষ্মীপূজার মুহূর্ত",
    "dhanteras_puja": "ধনতেরাস পূজার মুহূর্ত",
    "vrishabha": "বৃষ কাল (স্থির লগ্ন)",
    "punya_kaal": "পুণ্যকাল",
    "maha_punya_kaal": "মহাপুণ্যকাল",
    "sankranti": "সংক্রান্তির মুহূর্ত",
    "holika_dahan": "হোলিকা দহনের মুহূর্ত",
    "holika_after_bhadra": "ভদ্রা শেষে হোলিকা দহন",
    "rakhi": "রাখি বাঁধার মুহূর্ত",
    "karwa_puja": "পূজার মুহূর্ত",
    "puja": "পূজার মুহূর্ত",
    "sandhya_arghya": "সন্ধ্যা অর্ঘ্য (সূর্যাস্ত)",
    "usha_arghya": "ঊষা অর্ঘ্য (সূর্যোদয়, পরের দিন)",
    "pratah": "প্রাতঃকালের মুহূর্ত",
    "sayahna": "সায়াহ্নের মুহূর্ত",
    "tithi": "তিথি",
    "dwadashi_end": "দ্বাদশী শেষ",
    "hari_vasara_end": "হরিবাসর শেষ",
    "kutup": "কুতপ মুহূর্ত",
    "rohina": "রৌহিণ মুহূর্ত",
    "aparahna_kaal": "অপরাহ্ণ কাল",
    "abhyang": "অভ্যঙ্গ স্নান (চন্দ্রোদয় থেকে সূর্যোদয়)",
}

FESTIVALS_BN = {
    "pradosh": "প্রদোষ ব্রত",
    "sankashti": "সংকষ্টী চতুর্থী",
    "vinayaka": "বিনায়ক চতুর্থী",
    "purnima": "পূর্ণিমা ব্রত",
    "amavasya": "অমাবস্যা",
    "masik_shivratri": "মাসিক শিবরাত্রি",
    "durgashtami": "মাসিক দুর্গাষ্টমী",
    "kalashtami": "কালাষ্টমী",
    "skanda_shashthi": "স্কন্দ ষষ্ঠী",
    "maha_shivratri": "মহাশিবরাত্রি",
    "holika_dahan": "হোলিকা দহন (ন্যাড়াপোড়া)",
    "ram_navami": "রাম নবমী",
    "hanuman_jayanti": "হনুমান জয়ন্তী",
    "akshaya_tritiya": "অক্ষয় তৃতীয়া",
    "raksha_bandhan": "রাখি বন্ধন",
    "janmashtami": "শ্রীকৃষ্ণ জন্মাষ্টমী",
    "ganesh_chaturthi": "গণেশ চতুর্থী",
    "chaitra_navratri": "চৈত্র নবরাত্রি আরম্ভ",
    "navratri": "শারদীয় নবরাত্রি আরম্ভ",
    "dussehra": "বিজয়া দশমী",
    "karwa_chauth": "করবা চৌথ",
    "ahoi_ashtami": "অহোই অষ্টমী",
    "dhanteras": "ধনতেরাস",
    "diwali": "দীপাবলি (লক্ষ্মীপূজা)",
    "govardhan": "গোবর্ধন পূজা",
    "bhai_dooj": "ভাইফোঁটা",
    "chhath": "ছট পূজা",
    "vasant_panchami": "বসন্ত পঞ্চমী (সরস্বতী পূজা)",
    "guru_purnima": "গুরু পূর্ণিমা",
    "sharad_purnima": "শরৎ পূর্ণিমা",
    "sakat_chauth": "সকট চৌথ",
    "mauni_amavasya": "মৌনী অমাবস্যা",
    "sheetala_ashtami": "শীতলা অষ্টমী",
    "gudi_padwa": "গুড়ি পড়ওয়া / উগাদি",
    "gangaur": "গণগৌর",
    "vat_savitri": "বট সাবিত্রী ব্রত",
    "ganga_dussehra": "গঙ্গা দশহরা",
    "vat_purnima": "বট পূর্ণিমা ব্রত",
    "hariyali_teej": "হরিয়ালি তীজ",
    "nag_panchami": "নাগ পঞ্চমী",
    "kajari_teej": "কাজরী তীজ",
    "hal_shashthi": "হল ষষ্ঠী (বলরাম জয়ন্তী)",
    "hartalika_teej": "হরতালিকা তীজ",
    "rishi_panchami": "ঋষি পঞ্চমী",
    "anant_chaturdashi": "অনন্ত চতুর্দশী",
    "pitru_paksha": "পিতৃপক্ষ আরম্ভ (প্রতিপদ শ্রাদ্ধ)",
    "jivitputrika": "জীবিতপুত্রিকা ব্রত (জিতিয়া / জিতাষ্টমী)",
    "sarva_pitru_amavasya": "মহালয়া (সর্বপিতৃ অমাবস্যা)",
    "narak_chaturdashi": "নরক চতুর্দশী (ভূত চতুর্দশী)",
    "tulsi_vivah": "তুলসী বিবাহ",
    "kartik_purnima": "কার্তিক পূর্ণিমা (রাস পূর্ণিমা)",
    "dev_deepawali": "দেব দীপাবলি",
    "makar_sankranti": "মকর সংক্রান্তি (পৌষ সংক্রান্তি)",
    "lohri": "লোহরি",
    "holi": "হোলি",
    "ekadashi": "একাদশী",
    "santan_saptami": "সন্তান সপ্তমী",
}

EKADASHI_BN = {
    "Kamada Ekadashi": "কামদা একাদশী",
    "Varuthini Ekadashi": "বরূথিনী একাদশী",
    "Mohini Ekadashi": "মোহিনী একাদশী",
    "Apara Ekadashi": "অপরা একাদশী",
    "Nirjala Ekadashi": "নির্জলা একাদশী",
    "Yogini Ekadashi": "যোগিনী একাদশী",
    "Devshayani Ekadashi": "দেবশয়নী একাদশী",
    "Kamika Ekadashi": "কামিকা একাদশী",
    "Shravana Putrada Ekadashi": "শ্রাবণ পুত্রদা একাদশী",
    "Aja Ekadashi": "অজা একাদশী",
    "Parsva Ekadashi": "পার্শ্ব একাদশী",
    "Indira Ekadashi": "ইন্দিরা একাদশী",
    "Papankusha Ekadashi": "পাপাঙ্কুশা একাদশী",
    "Rama Ekadashi": "রমা একাদশী",
    "Devutthana Ekadashi": "উত্থান একাদশী",
    "Utpanna Ekadashi": "উৎপন্না একাদশী",
    "Mokshada Ekadashi": "মোক্ষদা একাদশী",
    "Saphala Ekadashi": "সফলা একাদশী",
    "Pausha Putrada Ekadashi": "পৌষ পুত্রদা একাদশী",
    "Shattila Ekadashi": "ষটতিলা একাদশী",
    "Jaya Ekadashi": "জয়া একাদশী",
    "Vijaya Ekadashi": "বিজয়া একাদশী",
    "Amalaki Ekadashi": "আমলকী একাদশী",
    "Papmochani Ekadashi": "পাপমোচনী একাদশী",
    "Padmini Ekadashi": "পদ্মিনী একাদশী",
    "Parama Ekadashi": "পরমা একাদশী",
}

# Regional framings. Bengal keeps Kali Puja on Diwali's Amavasya night, Durga
# Puja over Sharad Navratri (Shashthi-Dashami), Dol on Phalguna Purnima (the
# day of Holika Dahan) and Kojagari Lakshmi Puja on Ashwin Purnima.
REGIONAL_NOTE_BN = {
    "navratri": "দুর্গাপূজা",
    "chaitra_navratri": "বাসন্তী পূজা",
    "diwali": "কালীপূজা",
    "sharad_purnima": "কোজাগরী লক্ষ্মীপূজা",
    "holika_dahan": "দোলযাত্রা",
    "vasant_panchami": "সরস্বতী পূজা",
}

KOOTA_BN = {
    "varna": "বর্ণ", "vashya": "বশ্য", "tara": "তারা", "yoni": "যোনি",
    "graha_maitri": "গ্রহমৈত্রী", "gana": "গণ", "bhakoot": "রাশিকূট (ভকূট)",
    "nadi": "নাড়ী",
}
GANA_BN = {"Deva": "দেব", "Manushya": "নর", "Rakshasa": "রাক্ষস"}
NADI_BN = {"Adi": "আদ্য", "Madhya": "মধ্য", "Antya": "অন্ত্য"}
VARNA_BN = {"Brahmin": "ব্রাহ্মণ", "Kshatriya": "ক্ষত্রিয়", "Vaishya": "বৈশ্য",
            "Shudra": "শূদ্র"}
VASHYA_BN = {"Chatushpada": "চতুষ্পদ", "Manava": "মানব", "Jalachara": "জলচর",
             "Vanachara": "বনচর", "Keeta": "কীট"}
YONI_BN = {
    "Horse": "ঘোড়া", "Elephant": "হাতি", "Sheep": "ভেড়া", "Serpent": "সাপ",
    "Dog": "কুকুর", "Cat": "বিড়াল", "Rat": "ইঁদুর", "Cow": "গরু", "Buffalo": "মহিষ",
    "Tiger": "বাঘ", "Deer": "হরিণ", "Monkey": "বানর", "Mongoose": "বেজি",
    "Lion": "সিংহ",
}
TARA_BN = {
    "Janma": "জন্ম", "Sampat": "সম্পৎ", "Vipat": "বিপৎ", "Kshema": "ক্ষেম",
    "Pratyak": "প্রত্যরি", "Sadhaka": "সাধক", "Vadha": "বধ", "Mitra": "মিত্র",
    "Ati-Mitra": "অতিমিত্র",
}

WEEKDAY_BN = {
    "Sunday": "রবি", "Monday": "সোম", "Tuesday": "মঙ্গল", "Wednesday": "বুধ",
    "Thursday": "বৃহস্পতি", "Friday": "শুক্র", "Saturday": "শনি",
}

MONTHS_BN = ["জানুয়ারি", "ফেব্রুয়ারি", "মার্চ", "এপ্রিল", "মে", "জুন", "জুলাই", "আগস্ট",
             "সেপ্টেম্বর", "অক্টোবর", "নভেম্বর", "ডিসেম্বর"]

# Bengali splits Hindi's शाम: বিকেল (late afternoon, before sunset) and সন্ধ্যা
# (evening). names_i18n.clock_word() prints বিকেল for 16:00-17:59.
CLOCK_BN = {"morning": "সকাল", "afternoon": "দুপুর", "late_afternoon": "বিকেল",
            "evening": "সন্ধ্যা", "night": "রাত"}

LIMBS_BN = {
    "tithi": "তিথি", "nakshatra": "নক্ষত্র", "yoga": "যোগ", "karana": "করণ",
    "vara": "বার", "paksha": "পক্ষ", "masa": "মাস", "moon_sign": "চন্দ্র রাশি",
    "sun_sign": "সূর্য রাশি", "panchang": "পঞ্জিকা",
}


def add_bn(p: dict) -> dict:
    """add_hindi's Bengali twin: name_bn / paksha_bn / label_bn / notes_bn."""
    from .names_i18n import add_names
    return add_names(p, "bn")
