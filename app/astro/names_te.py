"""Telugu (తెలుగు) names for the panchang, festivals and matching (DIVASTRO-123).

Same shape as names_hi.py, with the suffix _TE, plus the extra tables that
names_i18n.names_for("te") exposes. Every value is in Telugu script.

Regional choices (for a native reviewer):
  * Paksha is శుద్ధ / బహుళ, as Telugu panchangams write it ("చైత్ర శుద్ధ
    పాడ్యమి", "బహుళ అష్టమి"); శుక్ల / కృష్ణ are the alternatives.
  * Tithis use the everyday Telugu forms పాడ్యమి, విదియ, తదియ, చవితి.
  * Nakshatras use the Telugu panchangam forms: పుష్యమి, మఖ, పుబ్బ (Purva
    Phalguni), ఉత్తర (Uttara Phalguni), చిత్త, శ్రవణం, శతభిషం.
  * Mars is కుజుడు (the astrological name; అంగారకుడు is the alternative).
  * Rahukalam = రాహుకాలం, Yamagandam = యమగండం, Gulika = గుళిక కాలం,
    Durmuhurtham = దుర్ముహూర్తం, Varjyam = వర్జ్యం.
  * Devshayani Ekadashi is తొలి ఏకాదశి in Telugu homes.
"""

from __future__ import annotations

TITHI_TE = {
    "Pratipada": "పాడ్యమి", "Dwitiya": "విదియ", "Tritiya": "తదియ",
    "Chaturthi": "చవితి", "Panchami": "పంచమి", "Shashthi": "షష్ఠి",
    "Saptami": "సప్తమి", "Ashtami": "అష్టమి", "Navami": "నవమి",
    "Dashami": "దశమి", "Ekadashi": "ఏకాదశి", "Dwadashi": "ద్వాదశి",
    "Trayodashi": "త్రయోదశి", "Chaturdashi": "చతుర్దశి", "Purnima": "పౌర్ణమి",
    "Amavasya": "అమావాస్య",
}

NAKSHATRAS_TE = {
    "Ashwini": "అశ్విని", "Bharani": "భరణి", "Krittika": "కృత్తిక", "Rohini": "రోహిణి",
    "Mrigashira": "మృగశిర", "Ardra": "ఆర్ద్ర", "Punarvasu": "పునర్వసు",
    "Pushya": "పుష్యమి", "Ashlesha": "ఆశ్లేష", "Magha": "మఖ",
    "Purva Phalguni": "పుబ్బ",          # పూర్వ ఫల్గుణి
    "Uttara Phalguni": "ఉత్తర",         # ఉత్తర ఫల్గుణి
    "Hasta": "హస్త", "Chitra": "చిత్త", "Swati": "స్వాతి", "Vishakha": "విశాఖ",
    "Anuradha": "అనూరాధ", "Jyeshtha": "జ్యేష్ఠ", "Mula": "మూల",
    "Purva Ashadha": "పూర్వాషాఢ", "Uttara Ashadha": "ఉత్తరాషాఢ",
    "Shravana": "శ్రవణం", "Dhanishta": "ధనిష్ఠ", "Shatabhisha": "శతభిషం",
    "Purva Bhadrapada": "పూర్వాభాద్ర", "Uttara Bhadrapada": "ఉత్తరాభాద్ర",
    "Revati": "రేవతి",
}

VARA_TE = {
    "Sunday": "ఆదివారం", "Monday": "సోమవారం", "Tuesday": "మంగళవారం",
    "Wednesday": "బుధవారం", "Thursday": "గురువారం", "Friday": "శుక్రవారం",
    "Saturday": "శనివారం",
}

YOGA_TE = {
    "Vishkambha": "విష్కంభం", "Priti": "ప్రీతి", "Ayushman": "ఆయుష్మాన్",
    "Saubhagya": "సౌభాగ్యం", "Shobhana": "శోభనం", "Atiganda": "అతిగండం",
    "Sukarma": "సుకర్మ", "Dhriti": "ధృతి", "Shula": "శూలం", "Ganda": "గండం",
    "Vriddhi": "వృద్ధి", "Dhruva": "ధ్రువం", "Vyaghata": "వ్యాఘాతం",
    "Harshana": "హర్షణం", "Vajra": "వజ్రం", "Siddhi": "సిద్ధి",
    "Vyatipata": "వ్యతీపాతం", "Variyana": "వరీయాన్", "Parigha": "పరిఘం",
    "Shiva": "శివం", "Siddha": "సిద్ధం", "Sadhya": "సాధ్యం", "Shubha": "శుభం",
    "Shukla": "శుక్లం", "Brahma": "బ్రహ్మం", "Indra": "ఐంద్రం", "Vaidhriti": "వైధృతి",
}

KARANA_TE = {
    "Bava": "బవ", "Balava": "బాలవ", "Kaulava": "కౌలవ", "Taitila": "తైతుల",
    "Gara": "గరజి", "Vanija": "వణిజ", "Vishti": "విష్టి (భద్ర)", "Shakuni": "శకుని",
    "Chatushpada": "చతుష్పాత్", "Naga": "నాగవం", "Kimstughna": "కింస్తుఘ్నం",
}

PAKSHA_TE = {"Shukla": "శుద్ధ", "Krishna": "బహుళ"}

NOTE_POLAR_TE = ("ఈ తేదీన ఈ అక్షాంశంలో సూర్యుడు ఉదయించడు, అస్తమించడు; అందువల్ల వైదిక "
                 "దినాన్ని సూర్యోదయం నుండి లెక్కించలేము. క్రింది అంగాలు స్థానిక అర్ధరాత్రి నుండి "
                 "లెక్కించబడ్డాయి; సూర్యోదయం ఆధారిత ముహూర్తాలు వర్తించవు.")
NOTE_WEDNESDAY_TE = ("బుధవారం అభిజిత్ ముహూర్తం తీసుకోరు — వారాధిపతి బుధుడు దానిని "
                     "దూషితం చేస్తాడని భావిస్తారు.")

MASA_TE = {
    "Chaitra": "చైత్రము", "Vaishakha": "వైశాఖము", "Jyeshtha": "జ్యేష్ఠము",
    "Ashadha": "ఆషాఢము", "Shravana": "శ్రావణము", "Bhadrapada": "భాద్రపదము",
    "Ashwin": "ఆశ్వయుజము", "Kartika": "కార్తీకము", "Margashirsha": "మార్గశిరము",
    "Pausha": "పుష్యము", "Magha": "మాఘము", "Phalguna": "ఫాల్గుణము",
}

# Telugu reckons by the lunar (amanta) month; no solar-month calendar in daily use.
SOLAR_MASA_TE: dict[str, str] = {}

RASHI_TE = {
    "Aries": "మేషం", "Taurus": "వృషభం", "Gemini": "మిథునం", "Cancer": "కర్కాటకం",
    "Leo": "సింహం", "Virgo": "కన్య", "Libra": "తుల", "Scorpio": "వృశ్చికం",
    "Sagittarius": "ధనుస్సు", "Capricorn": "మకరం", "Aquarius": "కుంభం", "Pisces": "మీనం",
}

GRAHA_TE = {
    "Sun": "సూర్యుడు", "Moon": "చంద్రుడు", "Mars": "కుజుడు", "Mercury": "బుధుడు",
    "Jupiter": "గురువు", "Venus": "శుక్రుడు", "Saturn": "శని", "Rahu": "రాహువు",
    "Ketu": "కేతువు",
}

CHOGHADIYA_TE = {
    "Amrit": "అమృతం", "Shubh": "శుభం", "Labh": "లాభం", "Char": "చరం",
    "Rog": "రోగం", "Kaal": "కాలం", "Udveg": "ఉద్వేగం",
}
CHOGHADIYA_QUALITY_TE = {"auspicious": "శుభం", "neutral": "మధ్యమం", "inauspicious": "అశుభం"}

TIMINGS_TE = {
    "rahu_kaal": "రాహుకాలం", "yamaganda": "యమగండం", "gulika": "గుళిక కాలం",
    "abhijit": "అభిజిత్ ముహూర్తం", "brahma_muhurta": "బ్రహ్మ ముహూర్తం",
    "pradosh": "ప్రదోష కాలం", "nishita": "నిశీథ కాలం",
    "sunrise": "సూర్యోదయం", "sunset": "సూర్యాస్తమయం",
    "moonrise": "చంద్రోదయం", "moonset": "చంద్రాస్తమయం",
    "parana": "పారణ సమయం", "durmuhurtam": "దుర్ముహూర్తం", "varjyam": "వర్జ్యం",
    "good_time": "శుభ సమయం",
}

FESTIVAL_TIMINGS_TE = {
    "parana": "పారణ (ఉపవాస విరమణ)",
    "pradosh": "ప్రదోష పూజ",
    "pradosh_kaal": "ప్రదోష కాలం",
    "moonrise": "చంద్రోదయం",
    "madhyahna": "మధ్యాహ్న పూజ ముహూర్తం",
    "nishita": "నిశీథ కాల పూజ",
    "aparahna": "అపరాహ్ణ పూజ",
    "vijay": "విజయ ముహూర్తం",
    "ghatasthapana": "కలశ స్థాపన ముహూర్తం",
    "ghatasthapana_abhijit": "కలశ స్థాపన (అభిజిత్)",
    "lakshmi_puja": "లక్ష్మీ పూజ ముహూర్తం",
    "dhanteras_puja": "ధన త్రయోదశి పూజ ముహూర్తం",
    "vrishabha": "వృషభ కాలం (స్థిర లగ్నం)",
    "punya_kaal": "పుణ్య కాలం",
    "maha_punya_kaal": "మహా పుణ్య కాలం",
    "sankranti": "సంక్రమణ సమయం",
    "holika_dahan": "హోలికా దహనం ముహూర్తం",
    "holika_after_bhadra": "భద్ర ముగిసిన తర్వాత హోలికా దహనం",
    "rakhi": "రాఖీ కట్టే ముహూర్తం",
    "karwa_puja": "పూజ ముహూర్తం",
    "puja": "పూజ ముహూర్తం",
    "sandhya_arghya": "సంధ్యా అర్ఘ్యం (సూర్యాస్తమయం)",
    "usha_arghya": "ఉషా అర్ఘ్యం (సూర్యోదయం, మరుసటి రోజు)",
    "pratah": "ప్రాతఃకాల ముహూర్తం",
    "sayahna": "సాయంకాల ముహూర్తం",
    "tithi": "తిథి",
    "dwadashi_end": "ద్వాదశి ముగింపు",
    "hari_vasara_end": "హరి వాసరం ముగింపు",
    "kutup": "కుతప ముహూర్తం",
    "rohina": "రౌహిణ ముహూర్తం",
    "aparahna_kaal": "అపరాహ్ణ కాలం",
    "abhyang": "అభ్యంగ స్నానం (చంద్రోదయం నుండి సూర్యోదయం వరకు)",
}

FESTIVALS_TE = {
    "pradosh": "ప్రదోష వ్రతం",
    "sankashti": "సంకష్టహర చతుర్థి",
    "vinayaka": "మాస వినాయక చతుర్థి",
    "purnima": "పౌర్ణమి వ్రతం",
    "amavasya": "అమావాస్య",
    "masik_shivratri": "మాస శివరాత్రి",
    "durgashtami": "మాస దుర్గాష్టమి",
    "kalashtami": "కాలాష్టమి",
    "skanda_shashthi": "స్కంద షష్ఠి",
    "maha_shivratri": "మహా శివరాత్రి",
    "holika_dahan": "హోలికా దహనం (కామదహనం)",
    "ram_navami": "శ్రీరామ నవమి",
    "hanuman_jayanti": "హనుమాన్ జయంతి",
    "akshaya_tritiya": "అక్షయ తృతీయ",
    "raksha_bandhan": "రక్షా బంధన్ (రాఖీ పౌర్ణమి)",
    "janmashtami": "శ్రీ కృష్ణ జన్మాష్టమి",
    "ganesh_chaturthi": "వినాయక చవితి",
    "chaitra_navratri": "వసంత నవరాత్రులు ప్రారంభం",
    "navratri": "శరన్నవరాత్రులు ప్రారంభం",
    "dussehra": "విజయదశమి (దసరా)",
    "karwa_chauth": "కర్వా చౌత్",
    "ahoi_ashtami": "అహోయి అష్టమి",
    "dhanteras": "ధన త్రయోదశి",
    "diwali": "దీపావళి (లక్ష్మీ పూజ)",
    "govardhan": "గోవర్ధన పూజ",
    "bhai_dooj": "భగినీ హస్త భోజనం (యమ ద్వితీయ)",
    "chhath": "ఛఠ్ పూజ",
    "vasant_panchami": "వసంత పంచమి (శ్రీ పంచమి)",
    "guru_purnima": "గురు పౌర్ణమి (వ్యాస పౌర్ణమి)",
    "sharad_purnima": "శరత్ పౌర్ణమి",
    "sakat_chauth": "సకట్ చౌత్",
    "mauni_amavasya": "మౌని అమావాస్య",
    "sheetala_ashtami": "శీతలా అష్టమి",
    "gudi_padwa": "ఉగాది",
    "gangaur": "గణగౌర్",
    "vat_savitri": "వట సావిత్రి వ్రతం",
    "ganga_dussehra": "గంగా దశహరా",
    "vat_purnima": "వట పౌర్ణమి వ్రతం",
    "hariyali_teej": "హరియాలీ తీజ్",
    "nag_panchami": "నాగ పంచమి",
    "kajari_teej": "కజరీ తీజ్",
    "hal_shashthi": "హల షష్ఠి (బలరామ జయంతి)",
    "hartalika_teej": "హరితాళిక వ్రతం",
    "rishi_panchami": "ఋషి పంచమి",
    "anant_chaturdashi": "అనంత చతుర్దశి (అనంత పద్మనాభ వ్రతం)",
    "pitru_paksha": "మహాలయ పక్షం ప్రారంభం (పాడ్యమి శ్రాద్ధం)",
    "jivitputrika": "జీవిత్పుత్రికా వ్రతం (జితియా)",
    "sarva_pitru_amavasya": "మహాలయ అమావాస్య",
    "narak_chaturdashi": "నరక చతుర్దశి",
    "tulsi_vivah": "తులసి వివాహం (క్షీరాబ్ది ద్వాదశి)",
    "kartik_purnima": "కార్తీక పౌర్ణమి",
    "dev_deepawali": "దేవ దీపావళి",
    "makar_sankranti": "మకర సంక్రాంతి",
    "lohri": "లోహ్రీ",
    "holi": "హోలీ",
    "ekadashi": "ఏకాదశి",
    "santan_saptami": "సంతాన సప్తమి",
}

EKADASHI_TE = {
    "Kamada Ekadashi": "కామద ఏకాదశి",
    "Varuthini Ekadashi": "వరూధిని ఏకాదశి",
    "Mohini Ekadashi": "మోహినీ ఏకాదశి",
    "Apara Ekadashi": "అపర ఏకాదశి",
    "Nirjala Ekadashi": "నిర్జల ఏకాదశి",
    "Yogini Ekadashi": "యోగినీ ఏకాదశి",
    "Devshayani Ekadashi": "తొలి ఏకాదశి (శయన ఏకాదశి)",
    "Kamika Ekadashi": "కామికా ఏకాదశి",
    "Shravana Putrada Ekadashi": "శ్రావణ పుత్రద ఏకాదశి",
    "Aja Ekadashi": "అజ ఏకాదశి",
    "Parsva Ekadashi": "పరివర్తిని ఏకాదశి",
    "Indira Ekadashi": "ఇందిరా ఏకాదశి",
    "Papankusha Ekadashi": "పాపాంకుశ ఏకాదశి",
    "Rama Ekadashi": "రమా ఏకాదశి",
    "Devutthana Ekadashi": "ఉత్థాన ఏకాదశి",
    "Utpanna Ekadashi": "ఉత్పన్న ఏకాదశి",
    # Often, not always, the day of ముక్కోటి / వైకుంఠ ఏకాదశి (fixed by Dhanurmasa).
    "Mokshada Ekadashi": "మోక్షద ఏకాదశి",
    "Saphala Ekadashi": "సఫల ఏకాదశి",
    "Pausha Putrada Ekadashi": "పుష్య పుత్రద ఏకాదశి",
    "Shattila Ekadashi": "షట్తిల ఏకాదశి",
    "Jaya Ekadashi": "జయ ఏకాదశి",
    "Vijaya Ekadashi": "విజయ ఏకాదశి",
    "Amalaki Ekadashi": "ఆమలకీ ఏకాదశి",
    "Papmochani Ekadashi": "పాపమోచని ఏకాదశి",
    "Padmini Ekadashi": "పద్మినీ ఏకాదశి",
    "Parama Ekadashi": "పరమ ఏకాదశి",
}

# Regional framings. Bathukamma runs from Mahalaya Amavasya to Durgashtami in
# Telangana. Telugu Hanuman Jayanti is Vaishakha Bahula Dashami (other date).
REGIONAL_NOTE_TE = {
    "navratri": "బతుకమ్మ (తెలంగాణ)",
    "sarva_pitru_amavasya": "ఎంగిలిపూల బతుకమ్మ",
    "dussehra": "దసరా",
    "raksha_bandhan": "రాఖీ పౌర్ణమి",
}

KOOTA_TE = {
    "varna": "వర్ణం", "vashya": "వశ్యం", "tara": "తార (దిన)", "yoni": "యోని",
    "graha_maitri": "గ్రహ మైత్రి", "gana": "గణం", "bhakoot": "రాశి కూటమి (భకూట్)",
    "nadi": "నాడి",
}
GANA_TE = {"Deva": "దేవ", "Manushya": "మనుష్య", "Rakshasa": "రాక్షస"}
NADI_TE = {"Adi": "ఆది", "Madhya": "మధ్య", "Antya": "అంత్య"}
VARNA_TE = {"Brahmin": "బ్రాహ్మణ", "Kshatriya": "క్షత్రియ", "Vaishya": "వైశ్య",
            "Shudra": "శూద్ర"}
VASHYA_TE = {"Chatushpada": "చతుష్పాద", "Manava": "మానవ", "Jalachara": "జలచర",
             "Vanachara": "వనచర", "Keeta": "కీటక"}
YONI_TE = {
    "Horse": "గుర్రం", "Elephant": "ఏనుగు", "Sheep": "గొర్రె", "Serpent": "పాము",
    "Dog": "కుక్క", "Cat": "పిల్లి", "Rat": "ఎలుక", "Cow": "ఆవు", "Buffalo": "గేదె",
    "Tiger": "పులి", "Deer": "జింక", "Monkey": "కోతి", "Mongoose": "ముంగిస",
    "Lion": "సింహం",
}
TARA_TE = {
    "Janma": "జన్మ", "Sampat": "సంపత్", "Vipat": "విపత్", "Kshema": "క్షేమ",
    "Pratyak": "ప్రత్యక్", "Sadhaka": "సాధక", "Vadha": "వధ", "Mitra": "మిత్ర",
    "Ati-Mitra": "అతి మిత్ర",
}

WEEKDAY_TE = {
    "Sunday": "ఆది", "Monday": "సోమ", "Tuesday": "మంగళ", "Wednesday": "బుధ",
    "Thursday": "గురు", "Friday": "శుక్ర", "Saturday": "శని",
}

MONTHS_TE = ["జనవరి", "ఫిబ్రవరి", "మార్చి", "ఏప్రిల్", "మే", "జూన్", "జూలై", "ఆగస్టు",
             "సెప్టెంబర్", "అక్టోబర్", "నవంబర్", "డిసెంబర్"]

CLOCK_TE = {"morning": "ఉదయం", "afternoon": "మధ్యాహ్నం", "evening": "సాయంత్రం",
            "night": "రాత్రి"}

LIMBS_TE = {
    "tithi": "తిథి", "nakshatra": "నక్షత్రం", "yoga": "యోగం", "karana": "కరణం",
    "vara": "వారం", "paksha": "పక్షం", "masa": "మాసం", "moon_sign": "చంద్ర రాశి",
    "sun_sign": "సూర్య రాశి", "panchang": "పంచాంగం",
}


def add_te(p: dict) -> dict:
    """add_hindi's Telugu twin: name_te / paksha_te / label_te / notes_te."""
    from .names_i18n import add_names
    return add_names(p, "te")
