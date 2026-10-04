"""Tamil (தமிழ்) names for the panchang, festivals and matching (DIVASTRO-123).

Same shape as names_hi.py, with the suffix _TA, plus the extra tables that
names_i18n.names_for("ta") exposes. Every value is in Tamil script (Grantha
letters ஜ ஷ ஸ ஹ are part of the Tamil block and are used where Tamil
panchangams use them).

Regional choices (for a native reviewer):
  * Paksha is வளர்பிறை / தேய்பிறை (waxing / waning), as Tamil calendars print
    it, not சுக்ல / கிருஷ்ண.
  * Rahu Kalam = ராகு காலம், Yamagandam = எமகண்டம், Gulika = குளிகை,
    Varjyam = தியாஜ்யம் (the Tamil panchangam word), "good time" = நல்ல நேரம்.
  * Nakshatras are the Tamil forms (திருவாதிரை, திருவோணம், கேட்டை, ...).
  * Tamil daily life runs on the SOLAR months (சித்திரை ...); the lunar
    month names are given as Tamil panchangams print them (சைத்ரம் ...).
  * Yoga names follow Tamil panchangams (சுப்பிரம் for Shukla, பிராம்யம் for
    Brahma, ஐந்திரம் for Indra).
"""

from __future__ import annotations

TITHI_TA = {
    "Pratipada": "பிரதமை", "Dwitiya": "துவிதியை", "Tritiya": "திருதியை",
    "Chaturthi": "சதுர்த்தி", "Panchami": "பஞ்சமி", "Shashthi": "சஷ்டி",
    "Saptami": "சப்தமி", "Ashtami": "அஷ்டமி", "Navami": "நவமி",
    "Dashami": "தசமி", "Ekadashi": "ஏகாதசி", "Dwadashi": "துவாதசி",
    "Trayodashi": "திரயோதசி", "Chaturdashi": "சதுர்த்தசி",
    "Purnima": "பௌர்ணமி",          # also பூர்ணிமை
    "Amavasya": "அமாவாசை",
}

NAKSHATRAS_TA = {
    "Ashwini": "அஸ்வினி",            # also அசுவினி
    "Bharani": "பரணி", "Krittika": "கார்த்திகை", "Rohini": "ரோகிணி",
    "Mrigashira": "மிருகசீரிஷம்",      # also மிருகசீரிடம்
    "Ardra": "திருவாதிரை", "Punarvasu": "புனர்பூசம்", "Pushya": "பூசம்",
    "Ashlesha": "ஆயில்யம்", "Magha": "மகம்", "Purva Phalguni": "பூரம்",
    "Uttara Phalguni": "உத்திரம்", "Hasta": "அஸ்தம்", "Chitra": "சித்திரை",
    "Swati": "சுவாதி", "Vishakha": "விசாகம்", "Anuradha": "அனுஷம்",
    "Jyeshtha": "கேட்டை", "Mula": "மூலம்", "Purva Ashadha": "பூராடம்",
    "Uttara Ashadha": "உத்திராடம்", "Shravana": "திருவோணம்", "Dhanishta": "அவிட்டம்",
    "Shatabhisha": "சதயம்", "Purva Bhadrapada": "பூரட்டாதி",
    "Uttara Bhadrapada": "உத்திரட்டாதி", "Revati": "ரேவதி",
}

# Keyed by the English weekday. Full "-கிழமை" forms; WEEKDAY_TA has the short ones.
VARA_TA = {
    "Sunday": "ஞாயிற்றுக்கிழமை", "Monday": "திங்கட்கிழமை", "Tuesday": "செவ்வாய்க்கிழமை",
    "Wednesday": "புதன்கிழமை", "Thursday": "வியாழக்கிழமை", "Friday": "வெள்ளிக்கிழமை",
    "Saturday": "சனிக்கிழமை",
}

YOGA_TA = {
    "Vishkambha": "விஷ்கம்பம்", "Priti": "ப்ரீதி", "Ayushman": "ஆயுஷ்மான்",
    "Saubhagya": "சௌபாக்கியம்", "Shobhana": "சோபனம்", "Atiganda": "அதிகண்டம்",
    "Sukarma": "சுகர்மம்", "Dhriti": "திருதி", "Shula": "சூலம்", "Ganda": "கண்டம்",
    "Vriddhi": "விருத்தி", "Dhruva": "துருவம்", "Vyaghata": "வியாகாதம்",
    "Harshana": "ஹர்ஷணம்", "Vajra": "வஜ்ரம்", "Siddhi": "சித்தி",
    "Vyatipata": "வியதீபாதம்", "Variyana": "வரீயான்", "Parigha": "பரிகம்",
    "Shiva": "சிவம்", "Siddha": "சித்தம்", "Sadhya": "சாத்தியம்", "Shubha": "சுபம்",
    "Shukla": "சுப்பிரம்", "Brahma": "பிராம்யம்", "Indra": "ஐந்திரம்",
    "Vaidhriti": "வைதிருதி",
}

KARANA_TA = {
    "Bava": "பவம்", "Balava": "பாலவம்", "Kaulava": "கௌலவம்", "Taitila": "தைதுலம்",
    "Gara": "கரசை", "Vanija": "வணிசை", "Vishti": "பத்திரை (விஷ்டி)",
    "Shakuni": "சகுனி", "Chatushpada": "சதுஷ்பாதம்", "Naga": "நாகவம்",
    "Kimstughna": "கிம்ஸ்துக்னம்",
}

# The word that prefixes a tithi ("தேய்பிறை அஷ்டமி").
PAKSHA_TA = {"Shukla": "வளர்பிறை", "Krishna": "தேய்பிறை"}

NOTE_POLAR_TA = ("இந்த தேதியில் இந்த அட்சரேகையில் சூரியன் உதிப்பதும் இல்லை, மறைவதும் இல்லை; "
                 "எனவே வேத நாளை சூரிய உதயத்திலிருந்து கணக்கிட முடியாது. கீழே உள்ள அங்கங்கள் "
                 "உள்ளூர் நள்ளிரவிலிருந்து கணக்கிடப்பட்டுள்ளன; சூரிய உதயத்தை அடிப்படையாகக் "
                 "கொண்ட முகூர்த்தங்கள் பொருந்தாது.")
NOTE_WEDNESDAY_TA = ("புதன்கிழமை அபிஜித் முகூர்த்தம் எடுத்துக்கொள்ளப்படுவதில்லை — கிழமையின் "
                     "அதிபதியான புதன் அதைக் கெடுப்பதாகக் கருதப்படுகிறது.")

# Lunar months as Tamil panchangams print them, keyed by panchang.LUNAR_MONTHS.
MASA_TA = {
    "Chaitra": "சைத்ரம்", "Vaishakha": "வைசாகம்", "Jyeshtha": "ஜ்யேஷ்டம்",
    "Ashadha": "ஆஷாடம்", "Shravana": "ஸ்ராவணம்", "Bhadrapada": "பாத்ரபதம்",
    "Ashwin": "ஆஸ்வயுஜம்", "Kartika": "கார்த்திகம்", "Margashirsha": "மார்கசீர்ஷம்",
    "Pausha": "பௌஷ்யம்", "Magha": "மாகம்", "Phalguna": "பால்குனம்",
}

# The Tamil SOLAR months - what Tamil speakers actually call the month. Keyed by
# the sidereal sign the Sun is in (சித்திரை = Sun in Mesha/Aries).
SOLAR_MASA_TA = {
    "Aries": "சித்திரை", "Taurus": "வைகாசி", "Gemini": "ஆனி", "Cancer": "ஆடி",
    "Leo": "ஆவணி", "Virgo": "புரட்டாசி", "Libra": "ஐப்பசி", "Scorpio": "கார்த்திகை",
    "Sagittarius": "மார்கழி", "Capricorn": "தை", "Aquarius": "மாசி", "Pisces": "பங்குனி",
}

RASHI_TA = {
    "Aries": "மேஷம்", "Taurus": "ரிஷபம்", "Gemini": "மிதுனம்", "Cancer": "கடகம்",
    "Leo": "சிம்மம்", "Virgo": "கன்னி", "Libra": "துலாம்", "Scorpio": "விருச்சிகம்",
    "Sagittarius": "தனுசு", "Capricorn": "மகரம்", "Aquarius": "கும்பம்", "Pisces": "மீனம்",
}

GRAHA_TA = {
    "Sun": "சூரியன்", "Moon": "சந்திரன்", "Mars": "செவ்வாய்", "Mercury": "புதன்",
    "Jupiter": "குரு", "Venus": "சுக்கிரன்", "Saturn": "சனி", "Rahu": "ராகு",
    "Ketu": "கேது",
}

CHOGHADIYA_TA = {
    "Amrit": "அமிர்தம்", "Shubh": "சுபம்", "Labh": "லாபம்", "Char": "சரம்",
    "Rog": "ரோகம்", "Kaal": "காலம்", "Udveg": "உத்வேகம்",
}
CHOGHADIYA_QUALITY_TA = {"auspicious": "சுபம்", "neutral": "மத்திமம்", "inauspicious": "அசுபம்"}

TIMINGS_TA = {
    "rahu_kaal": "ராகு காலம்", "yamaganda": "எமகண்டம்", "gulika": "குளிகை",
    "abhijit": "அபிஜித் முகூர்த்தம்", "brahma_muhurta": "பிரம்ம முகூர்த்தம்",
    "pradosh": "பிரதோஷ காலம்", "nishita": "நிசீத காலம்",
    "sunrise": "சூரிய உதயம்", "sunset": "சூரிய அஸ்தமனம்",
    "moonrise": "சந்திர உதயம்", "moonset": "சந்திர அஸ்தமனம்",
    "parana": "பாரணை நேரம்", "durmuhurtam": "துர்முகூர்த்தம்",
    "varjyam": "தியாஜ்யம்",           # Tamil panchangam term for Varjyam
    "good_time": "நல்ல நேரம்",
}

# festivals.LABELS, key for key.
FESTIVAL_TIMINGS_TA = {
    "parana": "பாரணை (விரதம் முடிக்கும் நேரம்)",
    "pradosh": "பிரதோஷ பூஜை",
    "pradosh_kaal": "பிரதோஷ காலம்",
    "moonrise": "சந்திர உதயம்",
    "madhyahna": "மத்தியான பூஜை முகூர்த்தம்",
    "nishita": "நிசீத கால பூஜை",
    "aparahna": "அபராஹ்ண பூஜை",
    "vijay": "விஜய முகூர்த்தம்",
    "ghatasthapana": "கலச ஸ்தாபன முகூர்த்தம்",
    "ghatasthapana_abhijit": "கலச ஸ்தாபனம் (அபிஜித்)",
    "lakshmi_puja": "லட்சுமி பூஜை முகூர்த்தம்",
    "dhanteras_puja": "தன திரயோதசி பூஜை முகூர்த்தம்",
    "vrishabha": "ரிஷப காலம் (ஸ்திர லக்னம்)",
    "punya_kaal": "புண்ணிய காலம்",
    "maha_punya_kaal": "மகா புண்ணிய காலம்",
    "sankranti": "சங்கராந்தி நேரம்",
    "holika_dahan": "ஹோலிகா தகன முகூர்த்தம்",
    "holika_after_bhadra": "பத்திரை முடிந்த பின் ஹோலிகா தகனம்",
    "rakhi": "ராக்கி கட்டும் முகூர்த்தம்",
    "karwa_puja": "பூஜை முகூர்த்தம்",
    "puja": "பூஜை முகூர்த்தம்",
    "sandhya_arghya": "சந்தியா அர்க்கியம் (சூரிய அஸ்தமனம்)",
    "usha_arghya": "உஷா அர்க்கியம் (சூரிய உதயம், மறுநாள்)",
    "pratah": "பிராதக்கால முகூர்த்தம்",
    "sayahna": "சாயங்கால முகூர்த்தம்",
    "tithi": "திதி",
    "dwadashi_end": "துவாதசி முடிவு",
    "hari_vasara_end": "ஹரி வாசரம் முடிவு",
    "kutup": "குதப முகூர்த்தம்",
    "rohina": "ரௌஹிண முகூர்த்தம்",
    "aparahna_kaal": "அபராஹ்ண காலம்",
    "abhyang": "அப்யங்க ஸ்நானம் (சந்திர உதயம் முதல் சூரிய உதயம் வரை)",
}

# festivals.py observance keys.
FESTIVALS_TA = {
    "pradosh": "பிரதோஷம்",
    "sankashti": "சங்கடஹர சதுர்த்தி",
    "vinayaka": "மாத விநாயக சதுர்த்தி",
    "purnima": "பௌர்ணமி விரதம்",
    "amavasya": "அமாவாசை",
    "masik_shivratri": "மாத சிவராத்திரி",
    "durgashtami": "மாத துர்காஷ்டமி",
    "kalashtami": "காலாஷ்டமி",
    "skanda_shashthi": "சஷ்டி விரதம்",
    "maha_shivratri": "மகா சிவராத்திரி",
    "holika_dahan": "ஹோலிகா தகனம்",
    "ram_navami": "ஸ்ரீ ராம நவமி",
    "hanuman_jayanti": "ஹனுமான் ஜெயந்தி",
    "akshaya_tritiya": "அட்சய திருதியை",
    "raksha_bandhan": "ரக்ஷா பந்தன்",
    "janmashtami": "கிருஷ்ண ஜெயந்தி (கோகுலாஷ்டமி)",
    "ganesh_chaturthi": "விநாயகர் சதுர்த்தி",
    "chaitra_navratri": "வசந்த நவராத்திரி தொடக்கம்",
    "navratri": "நவராத்திரி தொடக்கம்",
    "dussehra": "விஜயதசமி",
    "karwa_chauth": "கர்வா சௌத்",
    "ahoi_ashtami": "அஹோய் அஷ்டமி",
    "dhanteras": "தன திரயோதசி",
    "diwali": "தீபாவளி (லட்சுமி பூஜை)",
    "govardhan": "கோவர்த்தன பூஜை",
    "bhai_dooj": "பாய் தூஜ் (யம துவிதியை)",
    "chhath": "சட் பூஜை",
    "vasant_panchami": "வசந்த பஞ்சமி",
    "guru_purnima": "குரு பௌர்ணமி",
    "sharad_purnima": "சரத் பௌர்ணமி",
    "sakat_chauth": "சகட் சௌத்",
    "mauni_amavasya": "மௌனி அமாவாசை",
    "sheetala_ashtami": "சீதளா அஷ்டமி",
    "gudi_padwa": "யுகாதி / குடி பாட்வா",
    "gangaur": "கணகௌர்",
    "vat_savitri": "வட சாவித்திரி விரதம்",
    "ganga_dussehra": "கங்கா தசரா",
    "vat_purnima": "வட பௌர்ணமி விரதம்",
    "hariyali_teej": "ஹரியாலி தீஜ்",
    "nag_panchami": "நாக பஞ்சமி",
    "kajari_teej": "கஜரி தீஜ்",
    "hal_shashthi": "ஹல சஷ்டி (பலராம ஜெயந்தி)",
    "hartalika_teej": "ஹர்தாலிகா தீஜ்",
    "rishi_panchami": "ரிஷி பஞ்சமி",
    "anant_chaturdashi": "அனந்த சதுர்த்தசி",
    "pitru_paksha": "மகாளய பட்சம் தொடக்கம் (பிரதமை சிராத்தம்)",
    "jivitputrika": "ஜீவித்புத்ரிகா விரதம் (ஜிதியா)",
    "sarva_pitru_amavasya": "மகாளய அமாவாசை",
    "narak_chaturdashi": "நரக சதுர்த்தசி",
    "tulsi_vivah": "துளசி விவாகம்",
    "kartik_purnima": "கார்த்திக பௌர்ணமி",
    "dev_deepawali": "தேவ தீபாவளி",
    "makar_sankranti": "பொங்கல் (மகர சங்கராந்தி)",
    "lohri": "லோஹ்ரி",
    "holi": "ஹோலி",
    "ekadashi": "ஏகாதசி",
    "santan_saptami": "சந்தான சப்தமி",
}

# Keyed by festivals.py's English Ekadashi name.
EKADASHI_TA = {
    "Kamada Ekadashi": "காமதா ஏகாதசி",
    "Varuthini Ekadashi": "வருதினி ஏகாதசி",
    "Mohini Ekadashi": "மோகினி ஏகாதசி",
    "Apara Ekadashi": "அபரா ஏகாதசி",
    "Nirjala Ekadashi": "நிர்ஜலா ஏகாதசி",
    "Yogini Ekadashi": "யோகினி ஏகாதசி",
    "Devshayani Ekadashi": "தேவசயனி ஏகாதசி",
    "Kamika Ekadashi": "காமிகா ஏகாதசி",
    "Shravana Putrada Ekadashi": "ஸ்ராவண புத்ரதா ஏகாதசி",
    "Aja Ekadashi": "அஜா ஏகாதசி",
    "Parsva Ekadashi": "பரிவர்த்தினி ஏகாதசி",
    "Indira Ekadashi": "இந்திரா ஏகாதசி",
    "Papankusha Ekadashi": "பாபாங்குசா ஏகாதசி",
    "Rama Ekadashi": "ரமா ஏகாதசி",
    "Devutthana Ekadashi": "உத்தான ஏகாதசி",
    "Utpanna Ekadashi": "உத்பன்ன ஏகாதசி",
    # Usually (not always) the same day as Vaikunta Ekadasi (வைகுண்ட ஏகாதசி),
    # which Tamil Nadu fixes by the solar month Margazhi.
    "Mokshada Ekadashi": "மோட்சதா ஏகாதசி",
    "Saphala Ekadashi": "சபலா ஏகாதசி",
    "Pausha Putrada Ekadashi": "பௌஷ புத்ரதா ஏகாதசி",
    "Shattila Ekadashi": "ஷட்திலா ஏகாதசி",
    "Jaya Ekadashi": "ஜயா ஏகாதசி",
    "Vijaya Ekadashi": "விஜயா ஏகாதசி",
    "Amalaki Ekadashi": "ஆமலகி ஏகாதசி",
    "Papmochani Ekadashi": "பாபமோசனி ஏகாதசி",
    "Padmini Ekadashi": "பத்மினி ஏகாதசி",
    "Parama Ekadashi": "பரமா ஏகாதசி",
}

# Strong regional framings of an observance (shown beside, never instead of,
# the faithful name). Dates can differ: Tamil Hanuman Jayanthi is in Margazhi
# (Moolam nakshatra), and Deepavali is kept on the Naraka Chaturdashi morning.
REGIONAL_NOTE_TA = {
    "navratri": "நவராத்திரி கொலு",
    "makar_sankranti": "தை பொங்கல்",
    "janmashtami": "கோகுலாஷ்டமி",
    "raksha_bandhan": "ஆவணி அவிட்டம்",
    "dussehra": "விஜயதசமி (முந்தைய நாள் ஆயுத பூஜை / சரஸ்வதி பூஜை)",
    "narak_chaturdashi": "தீபாவளி (கங்கா ஸ்நானம்)",
}

# Ashtakoota labels. Tamil matching speaks of பொருத்தம்; the closest porutham
# name is used where one exists (தினம் = Tara, ராசி = Bhakoot, ராசி அதிபதி =
# Graha Maitri).
KOOTA_TA = {
    "varna": "வர்ணம்", "vashya": "வசியம்", "tara": "தினம் (தாரா)", "yoni": "யோனி",
    "graha_maitri": "ராசி அதிபதி (கிரக மைத்ரி)", "gana": "கணம்",
    "bhakoot": "ராசி (பகூட்)", "nadi": "நாடி",
}
GANA_TA = {"Deva": "தேவ", "Manushya": "மனித", "Rakshasa": "ராட்சச"}
NADI_TA = {"Adi": "ஆதி", "Madhya": "மத்திய", "Antya": "அந்திய"}
VARNA_TA = {"Brahmin": "பிராமணர்", "Kshatriya": "க்ஷத்திரியர்", "Vaishya": "வைசியர்",
            "Shudra": "சூத்திரர்"}
VASHYA_TA = {"Chatushpada": "சதுஷ்பாதம்", "Manava": "மானவம்", "Jalachara": "ஜலசரம்",
             "Vanachara": "வனசரம்", "Keeta": "கீடம்"}
YONI_TA = {
    "Horse": "குதிரை", "Elephant": "யானை", "Sheep": "ஆடு", "Serpent": "பாம்பு",
    "Dog": "நாய்", "Cat": "பூனை", "Rat": "எலி", "Cow": "பசு", "Buffalo": "எருமை",
    "Tiger": "புலி", "Deer": "மான்", "Monkey": "குரங்கு", "Mongoose": "கீரி",
    "Lion": "சிங்கம்",
}
TARA_TA = {
    "Janma": "ஜன்மம்", "Sampat": "சம்பத்", "Vipat": "விபத்", "Kshema": "க்ஷேமம்",
    "Pratyak": "பிரத்யக்", "Sadhaka": "சாதகம்", "Vadha": "வதம்", "Mitra": "மித்திரம்",
    "Ati-Mitra": "அதி மித்திரம்",
}

WEEKDAY_TA = {
    "Sunday": "ஞாயிறு", "Monday": "திங்கள்", "Tuesday": "செவ்வாய்", "Wednesday": "புதன்",
    "Thursday": "வியாழன்", "Friday": "வெள்ளி", "Saturday": "சனி",
}

MONTHS_TA = ["ஜனவரி", "பிப்ரவரி", "மார்ச்", "ஏப்ரல்", "மே", "ஜூன்", "ஜூலை", "ஆகஸ்ட்",
             "செப்டம்பர்", "அக்டோபர்", "நவம்பர்", "டிசம்பர்"]

# Part-of-day words printed before a 12-hour time ("காலை 6:14").
CLOCK_TA = {"morning": "காலை", "afternoon": "மதியம்", "evening": "மாலை", "night": "இரவு"}

# Row labels of the Panchang table.
LIMBS_TA = {
    "tithi": "திதி", "nakshatra": "நட்சத்திரம்", "yoga": "யோகம்", "karana": "கரணம்",
    "vara": "கிழமை", "paksha": "பட்சம்", "masa": "மாதம்", "moon_sign": "சந்திர ராசி",
    "sun_sign": "சூரிய ராசி", "panchang": "பஞ்சாங்கம்",
}


def add_ta(p: dict) -> dict:
    """add_hindi's Tamil twin: name_ta / paksha_ta / label_ta / notes_ta."""
    from .names_i18n import add_names
    return add_names(p, "ta")
