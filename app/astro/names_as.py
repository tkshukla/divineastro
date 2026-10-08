"""Assamese (অসমীয়া, Assamese/Bengali script) names for the panchang, festivals and matching (DIVASTRO-143/146).

Same shape as names_kn.py / names_bn.py: one table per name, suffix _AS, keyed by the
ENGLISH name the engines emit; names_i18n.names_for("as") exposes them.

Choices for a native reviewer (see also docs/lang-review/as.md):
  * Script: ৰ for the r-sound and ৱ for the w/v-sound in the middle of a word (দেৱ, অমাৱস্যা,
    নৱমী, দীপাৱলী); word-initially the Sanskrit v is written ব (বিজয়া, বসন্ত, বিশাখা).
  * Lunar months (MASA) use the Assamese forms: চ'ত বহাগ জেঠ আহাৰ শাওন ভাদ আহিন কাতি
    আঘোণ পুহ মাঘ ফাগুন. The Assamese Bhaskarabda year is solar, but the engine's months are
    lunar (Amanta), so SOLAR_MASA is left empty.
  * Nakshatra, tithi, yoga, karana names are the Sanskrit forms spelled the Assamese way
    (ৰোহিণী, পূৰ্ব ফল্গুনী, ধনিষ্ঠা ...), not Bengali spellings.
  * Weekdays: দেওবাৰ (Sunday) and the others with -বাৰ. Gregorian months as Assamese media
    write them (জানুৱাৰী ... ডিচেম্বৰ).
  * Rahu Kaal = ৰাহুকাল, Yamaganda = যমগণ্ড, Gulika = গুলিক কাল, Abhijit = অভিজিৎ মুহূৰ্ত.
  * Festivals use names Assamese speakers use for the matching engine observance; Dussehra is
    বিজয়া দশমী and Sharad Navratri carries দুৰ্গা পূজা in REGIONAL_NOTE. Bihu festivals are
    deliberately absent (the engine has no such observance).
"""

from __future__ import annotations

TITHI_AS = {
    "Pratipada": "প্ৰতিপদ", "Dwitiya": "দ্বিতীয়া", "Tritiya": "তৃতীয়া",
    "Chaturthi": "চতুৰ্থী", "Panchami": "পঞ্চমী", "Shashthi": "ষষ্ঠী",
    "Saptami": "সপ্তমী", "Ashtami": "অষ্টমী", "Navami": "নৱমী",
    "Dashami": "দশমী", "Ekadashi": "একাদশী", "Dwadashi": "দ্বাদশী",
    "Trayodashi": "ত্ৰয়োদশী", "Chaturdashi": "চতুৰ্দশী", "Purnima": "পূৰ্ণিমা",
    "Amavasya": "অমাৱস্যা",
}

NAKSHATRAS_AS = {
    "Ashwini": "অশ্বিনী", "Bharani": "ভৰণী", "Krittika": "কৃত্তিকা", "Rohini": "ৰোহিণী",
    "Mrigashira": "মৃগশিৰা", "Ardra": "আৰ্দ্ৰা", "Punarvasu": "পুনৰ্বসু",
    "Pushya": "পুষ্যা", "Ashlesha": "অশ্লেষা", "Magha": "মঘা",
    "Purva Phalguni": "পূৰ্ব ফল্গুনী", "Uttara Phalguni": "উত্তৰ ফল্গুনী",
    "Hasta": "হস্তা", "Chitra": "চিত্ৰা", "Swati": "স্বাতী", "Vishakha": "বিশাখা",
    "Anuradha": "অনুৰাধা", "Jyeshtha": "জ্যেষ্ঠা", "Mula": "মূলা",
    "Purva Ashadha": "পূৰ্বাষাঢ়া", "Uttara Ashadha": "উত্তৰাষাঢ়া",
    "Shravana": "শ্ৰৱণা", "Dhanishta": "ধনিষ্ঠা", "Shatabhisha": "শতভিষা",
    "Purva Bhadrapada": "পূৰ্ব ভাদ্ৰপদ", "Uttara Bhadrapada": "উত্তৰ ভাদ্ৰপদ",
    "Revati": "ৰেৱতী",
}

VARA_AS = {
    "Sunday": "দেওবাৰ", "Monday": "সোমবাৰ", "Tuesday": "মঙ্গলবাৰ",
    "Wednesday": "বুধবাৰ", "Thursday": "বৃহস্পতিবাৰ", "Friday": "শুক্ৰবাৰ",
    "Saturday": "শনিবাৰ",
}

YOGA_AS = {
    "Vishkambha": "বিষ্কম্ভ", "Priti": "প্ৰীতি", "Ayushman": "আয়ুষ্মান",
    "Saubhagya": "সৌভাগ্য", "Shobhana": "শোভন", "Atiganda": "অতিগণ্ড",
    "Sukarma": "সুকৰ্মা", "Dhriti": "ধৃতি", "Shula": "শূল", "Ganda": "গণ্ড",
    "Vriddhi": "বৃদ্ধি", "Dhruva": "ধ্ৰুৱ", "Vyaghata": "ব্যাঘাত",
    "Harshana": "হৰ্ষণ", "Vajra": "বজ্ৰ", "Siddhi": "সিদ্ধি",
    "Vyatipata": "ব্যতীপাত", "Variyana": "বৰীয়ান", "Parigha": "পৰিঘ",
    "Shiva": "শিৱ", "Siddha": "সিদ্ধ", "Sadhya": "সাধ্য", "Shubha": "শুভ",
    "Shukla": "শুক্ল", "Brahma": "ব্ৰহ্ম", "Indra": "ইন্দ্ৰ", "Vaidhriti": "বৈধৃতি",
}

KARANA_AS = {
    "Bava": "বৱ", "Balava": "বালৱ", "Kaulava": "কৌলৱ", "Taitila": "তৈতিল",
    "Gara": "গৰ", "Vanija": "বণিজ", "Vishti": "বিষ্টি (ভদ্ৰা)", "Shakuni": "শকুনি",
    "Chatushpada": "চতুষ্পদ", "Naga": "নাগ", "Kimstughna": "কিংস্তুঘ্ন",
}

PAKSHA_AS = {"Shukla": "শুক্ল", "Krishna": "কৃষ্ণ"}

MASA_AS = {
    "Chaitra": "চ'ত", "Vaishakha": "বহাগ", "Jyeshtha": "জেঠ",
    "Ashadha": "আহাৰ", "Shravana": "শাওন", "Bhadrapada": "ভাদ",
    "Ashwin": "আহিন", "Kartika": "কাতি", "Margashirsha": "আঘোণ",
    "Pausha": "পুহ", "Magha": "মাঘ", "Phalguna": "ফাগুন",
}

# lunar months are MASA; fill this only if the calendar is solar (keys "Aries".."Pisces")
SOLAR_MASA_AS = {}

RASHI_AS = {
    "Aries": "মেষ", "Taurus": "বৃষ", "Gemini": "মিথুন", "Cancer": "কৰ্কট",
    "Leo": "সিংহ", "Virgo": "কন্যা", "Libra": "তুলা", "Scorpio": "বৃশ্চিক",
    "Sagittarius": "ধনু", "Capricorn": "মকৰ", "Aquarius": "কুম্ভ", "Pisces": "মীন",
}

GRAHA_AS = {
    "Sun": "সূৰ্য", "Moon": "চন্দ্ৰ", "Mars": "মঙ্গল", "Mercury": "বুধ",
    "Jupiter": "বৃহস্পতি", "Venus": "শুক্ৰ", "Saturn": "শনি", "Rahu": "ৰাহু",
    "Ketu": "কেতু",
}

CHOGHADIYA_AS = {
    "Amrit": "অমৃত", "Shubh": "শুভ", "Labh": "লাভ", "Char": "চৰ",
    "Rog": "ৰোগ", "Kaal": "কাল", "Udveg": "উদ্বেগ",
}

CHOGHADIYA_QUALITY_AS = {"auspicious": "শুভ", "neutral": "মধ্যম", "inauspicious": "অশুভ"}

TIMINGS_AS = {
    "rahu_kaal": "ৰাহুকাল", "yamaganda": "যমগণ্ড", "gulika": "গুলিক কাল",
    "abhijit": "অভিজিৎ মুহূৰ্ত", "brahma_muhurta": "ব্ৰহ্ম মুহূৰ্ত",
    "pradosh": "প্ৰদোষ কাল", "nishita": "নিশীথ কাল",
    "sunrise": "সূৰ্যোদয়", "sunset": "সূৰ্যাস্ত",
    "moonrise": "চন্দ্ৰোদয়", "moonset": "চন্দ্ৰাস্ত",
    "parana": "পাৰণৰ সময়", "durmuhurtam": "দুৰ্মুহূৰ্ত", "varjyam": "বৰ্জ্যম",
    "good_time": "শুভ সময়",
}

FESTIVAL_TIMINGS_AS = {
    "parana": "পাৰণ (উপবাস ভঙ্গ)",
    "pradosh": "প্ৰদোষ পূজা",
    "pradosh_kaal": "প্ৰদোষ কাল",
    "moonrise": "চন্দ্ৰোদয়",
    "madhyahna": "মধ্যাহ্ন পূজাৰ মুহূৰ্ত",
    "nishita": "নিশীথ কালৰ পূজা",
    "aparahna": "অপৰাহ্ণ পূজা",
    "vijay": "বিজয় মুহূৰ্ত",
    "ghatasthapana": "ঘটস্থাপনৰ মুহূৰ্ত",
    "ghatasthapana_abhijit": "ঘটস্থাপন (অভিজিৎ)",
    "lakshmi_puja": "লক্ষ্মী পূজাৰ মুহূৰ্ত",
    "dhanteras_puja": "ধনতেৰস পূজাৰ মুহূৰ্ত",
    "vrishabha": "বৃষ কাল (স্থিৰ লগ্ন)",
    "punya_kaal": "পুণ্যকাল",
    "maha_punya_kaal": "মহাপুণ্যকাল",
    "sankranti": "সংক্ৰান্তিৰ মুহূৰ্ত",
    "holika_dahan": "হোলিকা দহনৰ মুহূৰ্ত",
    "holika_after_bhadra": "ভদ্ৰা শেষ হোৱাৰ পিছত হোলিকা দহন",
    "rakhi": "ৰাখী বন্ধনৰ মুহূৰ্ত",
    "karwa_puja": "পূজাৰ মুহূৰ্ত",
    "puja": "পূজাৰ মুহূৰ্ত",
    "sandhya_arghya": "সন্ধ্যা অৰ্ঘ্য (সূৰ্যাস্ত)",
    "usha_arghya": "ঊষা অৰ্ঘ্য (সূৰ্যোদয়, পিছদিনা)",
    "pratah": "প্ৰাতঃকালৰ মুহূৰ্ত",
    "sayahna": "সায়ংকালৰ মুহূৰ্ত",
    "tithi": "তিথি",
    "dwadashi_end": "দ্বাদশী শেষ",
    "hari_vasara_end": "হৰিবাসৰ শেষ",
    "kutup": "কুতুপ মুহূৰ্ত",
    "rohina": "ৰৌহিণ মুহূৰ্ত",
    "aparahna_kaal": "অপৰাহ্ণ কাল",
    "abhyang": "অভ্যঙ্গ স্নান (চন্দ্ৰোদয়ৰ পৰা সূৰ্যোদয়লৈ)",
}

FESTIVALS_AS = {
    "pradosh": "প্ৰদোষ ব্ৰত",
    "sankashti": "সংকষ্টী চতুৰ্থী",
    "vinayaka": "বিনায়ক চতুৰ্থী",
    "purnima": "পূৰ্ণিমা ব্ৰত",
    "amavasya": "অমাৱস্যা",
    "masik_shivratri": "মাহেকীয়া শিৱৰাত্ৰি",
    "durgashtami": "মাহেকীয়া দুৰ্গাষ্টমী",
    "kalashtami": "কালাষ্টমী",
    "skanda_shashthi": "স্কন্দ ষষ্ঠী",
    "maha_shivratri": "মহাশিৱৰাত্ৰি",
    "holika_dahan": "হোলিকা দহন",
    "ram_navami": "ৰাম নৱমী",
    "hanuman_jayanti": "হনুমান জয়ন্তী",
    "akshaya_tritiya": "অক্ষয় তৃতীয়া",
    "raksha_bandhan": "ৰাখী বন্ধন",
    "janmashtami": "শ্ৰীকৃষ্ণ জন্মাষ্টমী",
    "ganesh_chaturthi": "গণেশ চতুৰ্থী",
    "chaitra_navratri": "চৈত্ৰ নৱৰাত্ৰি আৰম্ভ",
    "navratri": "শাৰদীয় নৱৰাত্ৰি আৰম্ভ",
    "dussehra": "বিজয়া দশমী",
    "karwa_chauth": "কৰৱা চৌথ",
    "ahoi_ashtami": "অহোই অষ্টমী",
    "dhanteras": "ধনতেৰস",
    "diwali": "দীপাৱলী (লক্ষ্মী পূজা)",
    "govardhan": "গোৱৰ্ধন পূজা",
    "bhai_dooj": "ভাতৃ দ্বিতীয়া",
    "chhath": "ছঠ পূজা",
    "vasant_panchami": "বসন্ত পঞ্চমী (সৰস্বতী পূজা)",
    "guru_purnima": "গুৰু পূৰ্ণিমা",
    "sharad_purnima": "শৰৎ পূৰ্ণিমা",
    "sakat_chauth": "সকট চৌথ",
    "mauni_amavasya": "মৌনী অমাৱস্যা",
    "sheetala_ashtami": "শীতলা অষ্টমী",
    "gudi_padwa": "গুড়ি পাডৱা / উগাদি",
    "gangaur": "গণগৌৰ",
    "vat_savitri": "বট সাৱিত্ৰী ব্ৰত",
    "ganga_dussehra": "গঙ্গা দশহৰা",
    "vat_purnima": "বট পূৰ্ণিমা ব্ৰত",
    "hariyali_teej": "হৰিয়ালী তীজ",
    "nag_panchami": "নাগ পঞ্চমী",
    "kajari_teej": "কাজৰী তীজ",
    "hal_shashthi": "হল ষষ্ঠী (বলৰাম জয়ন্তী)",
    "hartalika_teej": "হৰতালিকা তীজ",
    "rishi_panchami": "ঋষি পঞ্চমী",
    "anant_chaturdashi": "অনন্ত চতুৰ্দশী",
    "pitru_paksha": "পিতৃ পক্ষ আৰম্ভ (প্ৰতিপদ শ্ৰাদ্ধ)",
    "jivitputrika": "জীৱিতপুত্ৰিকা ব্ৰত (জিতিয়া)",
    "sarva_pitru_amavasya": "মহালয়া (সৰ্বপিতৃ অমাৱস্যা)",
    "narak_chaturdashi": "নৰক চতুৰ্দশী",
    "tulsi_vivah": "তুলসী বিবাহ",
    "kartik_purnima": "কাৰ্তিক পূৰ্ণিমা",
    "dev_deepawali": "দেৱ দীপাৱলী",
    "makar_sankranti": "মকৰ সংক্ৰান্তি",
    "lohri": "লোহৰী",
    "holi": "হোলি",
    "ekadashi": "একাদশী",
    "santan_saptami": "সন্তান সপ্তমী",
}

EKADASHI_AS = {
    "Kamada Ekadashi": "কামদা একাদশী",
    "Varuthini Ekadashi": "বৰূথিনী একাদশী",
    "Mohini Ekadashi": "মোহিনী একাদশী",
    "Apara Ekadashi": "অপৰা একাদশী",
    "Nirjala Ekadashi": "নিৰ্জলা একাদশী",
    "Yogini Ekadashi": "যোগিনী একাদশী",
    "Devshayani Ekadashi": "দেৱশয়নী একাদশী",
    "Kamika Ekadashi": "কামিকা একাদশী",
    "Shravana Putrada Ekadashi": "শ্ৰাৱণ পুত্ৰদা একাদশী",
    "Aja Ekadashi": "অজা একাদশী",
    "Parsva Ekadashi": "পাৰ্শ্ব একাদশী",
    "Indira Ekadashi": "ইন্দিৰা একাদশী",
    "Papankusha Ekadashi": "পাপাঙ্কুশা একাদশী",
    "Rama Ekadashi": "ৰমা একাদশী",
    "Devutthana Ekadashi": "দেৱোত্থান একাদশী",
    "Utpanna Ekadashi": "উৎপন্না একাদশী",
    "Mokshada Ekadashi": "মোক্ষদা একাদশী",
    "Saphala Ekadashi": "সফলা একাদশী",
    "Pausha Putrada Ekadashi": "পৌষ পুত্ৰদা একাদশী",
    "Shattila Ekadashi": "ষট্তিলা একাদশী",
    "Jaya Ekadashi": "জয়া একাদশী",
    "Vijaya Ekadashi": "বিজয়া একাদশী",
    "Amalaki Ekadashi": "আমলকী একাদশী",
    "Papmochani Ekadashi": "পাপমোচনী একাদশী",
    "Padmini Ekadashi": "পদ্মিনী একাদশী",
    "Parama Ekadashi": "পৰমা একাদশী",
}

# optional strong regional framing per festival key
REGIONAL_NOTE_AS = {
    "navratri": "দুৰ্গা পূজা",
}

KOOTA_AS = {
    "varna": "বৰ্ণ", "vashya": "বশ্য", "tara": "তাৰা", "yoni": "যোনি",
    "graha_maitri": "গ্ৰহ মৈত্ৰী", "gana": "গণ", "bhakoot": "ভকূট",
    "nadi": "নাড়ী",
}

GANA_AS = {"Deva": "দেৱ", "Manushya": "মানৱ", "Rakshasa": "ৰাক্ষস"}

NADI_AS = {"Adi": "আদ্য", "Madhya": "মধ্য", "Antya": "অন্ত্য"}

VARNA_AS = {"Brahmin": "ব্ৰাহ্মণ", "Kshatriya": "ক্ষত্ৰিয়", "Vaishya": "বৈশ্য",
            "Shudra": "শূদ্ৰ"}

VASHYA_AS = {"Chatushpada": "চতুষ্পদ", "Manava": "মানৱ", "Jalachara": "জলচৰ",
             "Vanachara": "বনচৰ", "Keeta": "কীট"}

YONI_AS = {
    "Horse": "ঘোঁৰা", "Elephant": "হাতী", "Sheep": "ভেড়া", "Serpent": "সাপ",
    "Dog": "কুকুৰ", "Cat": "মেকুৰী", "Rat": "ইন্দুৰ", "Cow": "গৰু", "Buffalo": "ম'হ",
    "Tiger": "বাঘ", "Deer": "হৰিণ", "Monkey": "বান্দৰ", "Mongoose": "নেউল",
    "Lion": "সিংহ",
}

TARA_AS = {
    "Janma": "জন্ম", "Sampat": "সম্পৎ", "Vipat": "বিপৎ", "Kshema": "ক্ষেম",
    "Pratyak": "প্ৰত্যৰি", "Sadhaka": "সাধক", "Vadha": "বধ", "Mitra": "মিত্ৰ",
    "Ati-Mitra": "অতিমিত্ৰ",
}

WEEKDAY_AS = {
    "Sunday": "দেও", "Monday": "সোম", "Tuesday": "মঙ্গল", "Wednesday": "বুধ",
    "Thursday": "বৃহস্পতি", "Friday": "শুক্ৰ", "Saturday": "শনি",
}

MONTHS_AS = [
    "জানুৱাৰী", "ফেব্ৰুৱাৰী", "মাৰ্চ", "এপ্ৰিল", "মে'", "জুন", "জুলাই", "আগষ্ট",
    "ছেপ্টেম্বৰ", "অক্টোবৰ", "নৱেম্বৰ", "ডিচেম্বৰ",
]

CLOCK_AS = {
    "morning": "ৰাতিপুৱা",
    "afternoon": "দুপৰীয়া",
    "evening": "সন্ধিয়া",
    "night": "ৰাতি",
}

LIMBS_AS = {
    "tithi": "তিথি", "nakshatra": "নক্ষত্ৰ", "yoga": "যোগ", "karana": "কৰণ",
    "vara": "বাৰ", "paksha": "পক্ষ", "masa": "মাহ", "moon_sign": "চন্দ্ৰ ৰাশি",
    "sun_sign": "সূৰ্য ৰাশি", "panchang": "পঞ্জিকা",
}

# EN: The Sun does not both rise and set on this date at this latitude, so the vedic day cannot be
#     bounded by sunrise. The limbs below are reckoned from local midnight instead, and the sunrise-
#     based muhurtas are not defined.
NOTE_POLAR_AS = ("এই তাৰিখে এই অক্ষাংশত সূৰ্য উদয় আৰু অস্ত দুয়োটা নহয়, গতিকে বৈদিক দিনটো "
                 "সূৰ্যোদয়েৰে গণনা কৰিব নোৱাৰি। তলৰ অঙ্গবোৰ স্থানীয় মাজৰাতিৰ পৰা গণনা কৰা "
                 "হৈছে, আৰু সূৰ্যোদয়ভিত্তিক মুহূৰ্ত প্ৰযোজ্য নহয়।")

# EN: Abhijit muhurta is omitted on Wednesday, whose lord Mercury is held to spoil it.
NOTE_WEDNESDAY_AS = ("বুধবাৰে অভিজিৎ মুহূৰ্ত ধৰা নহয়, কাৰণ বাৰটোৰ অধিপতি বুধে ইয়াক "
                     "নষ্ট কৰে বুলি মানা হয়।")


def add_as(p: dict) -> dict:
    """add_hindi's twin for Assamese: name_as / paksha_as / label_as / notes_as."""
    from .names_i18n import add_names
    return add_names(p, "as")
