"""Malayalam (മലയാളം) names for the panchang, festivals and matching (DIVASTRO-123).

Same shape as names_hi.py, with the suffix _ML, plus the extra tables that
names_i18n.names_for("ml") exposes. Every value is in Malayalam script.

Regional choices (for a native reviewer):
  * Nakshatras are the Kerala names (അശ്വതി, മകയിരം, തിരുവാതിര, ... ചോതി,
    അനിഴം, തൃക്കേട്ട, പൂരുരുട്ടാതി).
  * Rashis use the Kerala names that double as the solar month names
    (മേടം, ഇടവം, ... ചിങ്ങം, കന്നി); Sanskrit forms (മേഷം, ഋഷഭം) are the
    alternative. കർക്കടകം is also spelt കർക്കിടകം.
  * The Malayalam calendar (Kollavarsham) is SOLAR, starting at ചിങ്ങം: those
    are SOLAR_MASA. Lunar month names are given in their Sanskrit form.
  * Paksha is ശുക്ല / കൃഷ്ണ (വെളുത്ത / കറുത്ത പക്ഷം is the colloquial pair).
  * രാഹുകാലം, യമകണ്ടം, ഗുളികകാലം. Gana in matching is ദേവ / മനുഷ്യ / അസുര
    (Kerala says അസുരഗണം rather than രാക്ഷസ).
  * Karanas are given in Sanskrit; Kerala almanacs also use animal names
    (സിംഹം, പുലി, ...) - not used here, needs a reviewer if wanted.
  * Mars = ചൊവ്വ, Jupiter = വ്യാഴം.
"""

from __future__ import annotations

TITHI_ML = {
    "Pratipada": "പ്രഥമ", "Dwitiya": "ദ്വിതീയ", "Tritiya": "തൃതീയ",
    "Chaturthi": "ചതുർഥി",          # also ചതുർത്ഥി
    "Panchami": "പഞ്ചമി", "Shashthi": "ഷഷ്ഠി",
    "Saptami": "സപ്തമി", "Ashtami": "അഷ്ടമി", "Navami": "നവമി",
    "Dashami": "ദശമി", "Ekadashi": "ഏകാദശി", "Dwadashi": "ദ്വാദശി",
    "Trayodashi": "ത്രയോദശി", "Chaturdashi": "ചതുർദശി",
    "Purnima": "പൗർണമി",            # വെളുത്തവാവ്
    "Amavasya": "അമാവാസി",          # കറുത്തവാവ്
}

NAKSHATRAS_ML = {
    "Ashwini": "അശ്വതി", "Bharani": "ഭരണി", "Krittika": "കാർത്തിക", "Rohini": "രോഹിണി",
    "Mrigashira": "മകയിരം", "Ardra": "തിരുവാതിര", "Punarvasu": "പുണർതം",
    "Pushya": "പൂയം", "Ashlesha": "ആയില്യം", "Magha": "മകം", "Purva Phalguni": "പൂരം",
    "Uttara Phalguni": "ഉത്രം", "Hasta": "അത്തം", "Chitra": "ചിത്തിര", "Swati": "ചോതി",
    "Vishakha": "വിശാഖം", "Anuradha": "അനിഴം", "Jyeshtha": "തൃക്കേട്ട", "Mula": "മൂലം",
    "Purva Ashadha": "പൂരാടം", "Uttara Ashadha": "ഉത്രാടം", "Shravana": "തിരുവോണം",
    "Dhanishta": "അവിട്ടം", "Shatabhisha": "ചതയം",
    "Purva Bhadrapada": "പൂരുരുട്ടാതി", "Uttara Bhadrapada": "ഉത്രട്ടാതി",
    "Revati": "രേവതി",
}

VARA_ML = {
    "Sunday": "ഞായറാഴ്ച", "Monday": "തിങ്കളാഴ്ച", "Tuesday": "ചൊവ്വാഴ്ച",
    "Wednesday": "ബുധനാഴ്ച", "Thursday": "വ്യാഴാഴ്ച", "Friday": "വെള്ളിയാഴ്ച",
    "Saturday": "ശനിയാഴ്ച",
}

YOGA_ML = {
    "Vishkambha": "വിഷ്കംഭം", "Priti": "പ്രീതി", "Ayushman": "ആയുഷ്മാൻ",
    "Saubhagya": "സൗഭാഗ്യം", "Shobhana": "ശോഭനം", "Atiganda": "അതിഗണ്ഡം",
    "Sukarma": "സുകർമ്മം", "Dhriti": "ധൃതി", "Shula": "ശൂലം", "Ganda": "ഗണ്ഡം",
    "Vriddhi": "വൃദ്ധി", "Dhruva": "ധ്രുവം", "Vyaghata": "വ്യാഘാതം",
    "Harshana": "ഹർഷണം", "Vajra": "വജ്രം", "Siddhi": "സിദ്ധി",
    "Vyatipata": "വ്യതീപാതം", "Variyana": "വരീയാൻ", "Parigha": "പരിഘം",
    "Shiva": "ശിവം", "Siddha": "സിദ്ധം", "Sadhya": "സാധ്യം", "Shubha": "ശുഭം",
    "Shukla": "ശുക്ലം", "Brahma": "ബ്രഹ്മം", "Indra": "ഐന്ദ്രം", "Vaidhriti": "വൈധൃതി",
}

KARANA_ML = {
    "Bava": "ബവം", "Balava": "ബാലവം", "Kaulava": "കൗലവം", "Taitila": "തൈതിലം",
    "Gara": "ഗരജം", "Vanija": "വണിജം", "Vishti": "വിഷ്ടി (ഭദ്ര)", "Shakuni": "ശകുനി",
    "Chatushpada": "ചതുഷ്പാദം", "Naga": "നാഗവം", "Kimstughna": "കിംസ്തുഘ്നം",
}

PAKSHA_ML = {"Shukla": "ശുക്ല", "Krishna": "കൃഷ്ണ"}

NOTE_POLAR_ML = ("ഈ തീയതിയിൽ ഈ അക്ഷാംശത്തിൽ സൂര്യൻ ഉദിക്കുകയോ അസ്തമിക്കുകയോ ചെയ്യുന്നില്ല; "
                 "അതിനാൽ വൈദിക ദിനം സൂര്യോദയം മുതൽ കണക്കാക്കാനാവില്ല. താഴെയുള്ള അംഗങ്ങൾ "
                 "പ്രാദേശിക അർധരാത്രി മുതൽ കണക്കാക്കിയതാണ്; സൂര്യോദയത്തെ ആശ്രയിക്കുന്ന "
                 "മുഹൂർത്തങ്ങൾ ബാധകമല്ല.")
NOTE_WEDNESDAY_ML = ("ബുധനാഴ്ച അഭിജിത് മുഹൂർത്തം എടുക്കാറില്ല — ആഴ്ചയുടെ അധിപനായ ബുധൻ "
                     "അതിനെ ദോഷപ്പെടുത്തുന്നുവെന്നാണ് വിശ്വാസം.")

# Lunar months (Sanskrit forms; Kerala daily life uses SOLAR_MASA_ML).
MASA_ML = {
    "Chaitra": "ചൈത്രം", "Vaishakha": "വൈശാഖം", "Jyeshtha": "ജ്യേഷ്ഠം",
    "Ashadha": "ആഷാഢം", "Shravana": "ശ്രാവണം", "Bhadrapada": "ഭാദ്രപദം",
    "Ashwin": "ആശ്വിനം", "Kartika": "കാർത്തികം", "Margashirsha": "മാർഗശീർഷം",
    "Pausha": "പൗഷം", "Magha": "മാഘം", "Phalguna": "ഫാൽഗുനം",
}

# Kollavarsham solar months, keyed by the sidereal sign the Sun is in. The year
# begins with ചിങ്ങം (Sun in Leo).
SOLAR_MASA_ML = {
    "Aries": "മേടം", "Taurus": "ഇടവം", "Gemini": "മിഥുനം", "Cancer": "കർക്കടകം",
    "Leo": "ചിങ്ങം", "Virgo": "കന്നി", "Libra": "തുലാം", "Scorpio": "വൃശ്ചികം",
    "Sagittarius": "ധനു", "Capricorn": "മകരം", "Aquarius": "കുംഭം", "Pisces": "മീനം",
}

# Kerala names the rashis (and a person's കൂറ്) by the same words.
RASHI_ML = dict(SOLAR_MASA_ML)

GRAHA_ML = {
    "Sun": "സൂര്യൻ", "Moon": "ചന്ദ്രൻ", "Mars": "ചൊവ്വ", "Mercury": "ബുധൻ",
    "Jupiter": "വ്യാഴം", "Venus": "ശുക്രൻ", "Saturn": "ശനി", "Rahu": "രാഹു", "Ketu": "കേതു",
}

CHOGHADIYA_ML = {
    "Amrit": "അമൃതം", "Shubh": "ശുഭം", "Labh": "ലാഭം", "Char": "ചരം",
    "Rog": "രോഗം", "Kaal": "കാലം", "Udveg": "ഉദ്വേഗം",
}
CHOGHADIYA_QUALITY_ML = {"auspicious": "ശുഭം", "neutral": "മധ്യമം", "inauspicious": "അശുഭം"}

TIMINGS_ML = {
    "rahu_kaal": "രാഹുകാലം", "yamaganda": "യമകണ്ടം", "gulika": "ഗുളികകാലം",
    "abhijit": "അഭിജിത് മുഹൂർത്തം", "brahma_muhurta": "ബ്രഹ്മമുഹൂർത്തം",
    "pradosh": "പ്രദോഷകാലം", "nishita": "നിശീഥകാലം",
    "sunrise": "സൂര്യോദയം", "sunset": "സൂര്യാസ്തമയം",
    "moonrise": "ചന്ദ്രോദയം", "moonset": "ചന്ദ്രാസ്തമയം",
    "parana": "പാരണ സമയം", "durmuhurtam": "ദുർമുഹൂർത്തം",
    "varjyam": "വർജ്യം",             # Kerala almanacs: വിഷനാഴിക is a related idea
    "good_time": "നല്ല സമയം",
}

FESTIVAL_TIMINGS_ML = {
    "parana": "പാരണ (വ്രതം മുറിക്കൽ)",
    "pradosh": "പ്രദോഷ പൂജ",
    "pradosh_kaal": "പ്രദോഷകാലം",
    "moonrise": "ചന്ദ്രോദയം",
    "madhyahna": "മധ്യാഹ്ന പൂജാ മുഹൂർത്തം",
    "nishita": "നിശീഥകാല പൂജ",
    "aparahna": "അപരാഹ്ന പൂജ",
    "vijay": "വിജയ മുഹൂർത്തം",
    "ghatasthapana": "കലശസ്ഥാപന മുഹൂർത്തം",
    "ghatasthapana_abhijit": "കലശസ്ഥാപനം (അഭിജിത്)",
    "lakshmi_puja": "ലക്ഷ്മീ പൂജാ മുഹൂർത്തം",
    "dhanteras_puja": "ധനത്രയോദശി പൂജാ മുഹൂർത്തം",
    "vrishabha": "വൃഷഭ കാലം (സ്ഥിര ലഗ്നം)",
    "punya_kaal": "പുണ്യകാലം",
    "maha_punya_kaal": "മഹാപുണ്യകാലം",
    "sankranti": "സംക്രമ സമയം",
    "holika_dahan": "ഹോളികാ ദഹന മുഹൂർത്തം",
    "holika_after_bhadra": "ഭദ്ര കഴിഞ്ഞ് ഹോളികാ ദഹനം",
    "rakhi": "രാഖി കെട്ടാനുള്ള മുഹൂർത്തം",
    "karwa_puja": "പൂജാ മുഹൂർത്തം",
    "puja": "പൂജാ മുഹൂർത്തം",
    "sandhya_arghya": "സന്ധ്യാ അർഘ്യം (സൂര്യാസ്തമയം)",
    "usha_arghya": "ഉഷാ അർഘ്യം (സൂര്യോദയം, പിറ്റേന്ന്)",
    "pratah": "പ്രാതഃകാല മുഹൂർത്തം",
    "sayahna": "സായാഹ്ന മുഹൂർത്തം",
    "tithi": "തിഥി",
    "dwadashi_end": "ദ്വാദശി അവസാനം",
    "hari_vasara_end": "ഹരിവാസരം അവസാനം",
    "kutup": "കുതപ മുഹൂർത്തം",
    "rohina": "രൗഹിണ മുഹൂർത്തം",
    "aparahna_kaal": "അപരാഹ്നകാലം",
    "abhyang": "അഭ്യംഗസ്നാനം (ചന്ദ്രോദയം മുതൽ സൂര്യോദയം വരെ)",
}

FESTIVALS_ML = {
    "pradosh": "പ്രദോഷ വ്രതം",
    "sankashti": "സങ്കഷ്ടഹര ചതുർഥി",
    "vinayaka": "മാസ വിനായക ചതുർഥി",
    "purnima": "പൗർണമി വ്രതം",
    "amavasya": "അമാവാസി",
    "masik_shivratri": "മാസ ശിവരാത്രി",
    "durgashtami": "മാസ ദുർഗാഷ്ടമി",
    "kalashtami": "കാലാഷ്ടമി",
    "skanda_shashthi": "ഷഷ്ഠി വ്രതം",
    "maha_shivratri": "മഹാശിവരാത്രി",
    "holika_dahan": "ഹോളികാ ദഹനം",
    "ram_navami": "ശ്രീരാമനവമി",
    "hanuman_jayanti": "ഹനുമാൻ ജയന്തി",
    "akshaya_tritiya": "അക്ഷയ തൃതീയ",
    "raksha_bandhan": "രക്ഷാബന്ധൻ",
    "janmashtami": "ശ്രീകൃഷ്ണ ജന്മാഷ്ടമി",
    "ganesh_chaturthi": "വിനായക ചതുർഥി",
    "chaitra_navratri": "വസന്ത നവരാത്രി ആരംഭം",
    "navratri": "നവരാത്രി ആരംഭം",
    "dussehra": "വിജയദശമി",
    "karwa_chauth": "കർവാ ചൗത്ത്",
    "ahoi_ashtami": "അഹോയി അഷ്ടമി",
    "dhanteras": "ധനത്രയോദശി",
    "diwali": "ദീപാവലി (ലക്ഷ്മീ പൂജ)",
    "govardhan": "ഗോവർധന പൂജ",
    "bhai_dooj": "ഭായി ദൂജ് (യമ ദ്വിതീയ)",
    "chhath": "ഛഠ് പൂജ",
    "vasant_panchami": "വസന്ത പഞ്ചമി",
    "guru_purnima": "ഗുരു പൂർണിമ",
    "sharad_purnima": "ശരത് പൂർണിമ",
    "sakat_chauth": "സകട് ചൗത്ത്",
    "mauni_amavasya": "മൗനി അമാവാസി",
    "sheetala_ashtami": "ശീതളാ അഷ്ടമി",
    "gudi_padwa": "ഉഗാദി / ഗുഡി പാഡ്വ",
    "gangaur": "ഗണഗൗർ",
    "vat_savitri": "വട സാവിത്രി വ്രതം",
    "ganga_dussehra": "ഗംഗാ ദസറ",
    "vat_purnima": "വട പൂർണിമ വ്രതം",
    "hariyali_teej": "ഹരിയാലി തീജ്",
    "nag_panchami": "നാഗപഞ്ചമി",
    "kajari_teej": "കജരി തീജ്",
    "hal_shashthi": "ഹല ഷഷ്ഠി (ബലരാമ ജയന്തി)",
    "hartalika_teej": "ഹർതാലിക തീജ്",
    "rishi_panchami": "ഋഷി പഞ്ചമി",
    "anant_chaturdashi": "അനന്ത ചതുർദശി",
    "pitru_paksha": "പിതൃപക്ഷം ആരംഭം (പ്രഥമ ശ്രാദ്ധം)",
    "jivitputrika": "ജീവിത്പുത്രികാ വ്രതം (ജിതിയ)",
    "sarva_pitru_amavasya": "മഹാലയ അമാവാസി",
    "narak_chaturdashi": "നരക ചതുർദശി",
    "tulsi_vivah": "തുളസി വിവാഹം",
    "kartik_purnima": "കാർത്തിക പൗർണമി",
    "dev_deepawali": "ദേവ ദീപാവലി",
    "makar_sankranti": "മകരസംക്രാന്തി",
    "lohri": "ലോഹ്രി",
    "holi": "ഹോളി",
    "ekadashi": "ഏകാദശി",
    "santan_saptami": "സന്താന സപ്തമി",
}

EKADASHI_ML = {
    "Kamada Ekadashi": "കാമദ ഏകാദശി",
    "Varuthini Ekadashi": "വരൂഥിനി ഏകാദശി",
    "Mohini Ekadashi": "മോഹിനി ഏകാദശി",
    "Apara Ekadashi": "അപര ഏകാദശി",
    "Nirjala Ekadashi": "നിർജല ഏകാദശി",
    "Yogini Ekadashi": "യോഗിനി ഏകാദശി",
    "Devshayani Ekadashi": "ദേവശയനി ഏകാദശി",
    "Kamika Ekadashi": "കാമിക ഏകാദശി",
    "Shravana Putrada Ekadashi": "ശ്രാവണ പുത്രദ ഏകാദശി",
    "Aja Ekadashi": "അജ ഏകാദശി",
    "Parsva Ekadashi": "പരിവർത്തിനി ഏകാദശി",
    "Indira Ekadashi": "ഇന്ദിര ഏകാദശി",
    "Papankusha Ekadashi": "പാപാങ്കുശ ഏകാദശി",
    "Rama Ekadashi": "രമ ഏകാദശി",
    "Devutthana Ekadashi": "ഉത്ഥാന ഏകാദശി",
    "Utpanna Ekadashi": "ഉത്പന്ന ഏകാദശി",
    "Mokshada Ekadashi": "മോക്ഷദ ഏകാദശി",
    "Saphala Ekadashi": "സഫല ഏകാദശി",
    "Pausha Putrada Ekadashi": "പൗഷ പുത്രദ ഏകാദശി",
    "Shattila Ekadashi": "ഷട്തില ഏകാദശി",
    "Jaya Ekadashi": "ജയ ഏകാദശി",
    "Vijaya Ekadashi": "വിജയ ഏകാദശി",
    "Amalaki Ekadashi": "ആമലകി ഏകാദശി",
    "Papmochani Ekadashi": "പാപമോചനി ഏകാദശി",
    "Padmini Ekadashi": "പദ്മിനി ഏകാദശി",
    "Parama Ekadashi": "പരമ ഏകാദശി",
}

# Regional framings. Kerala keeps Krishna's birthday as അഷ്ടമിരോഹിണി (solar
# Chingam, Rohini nakshatra), which can fall on a different day; Guruvayur
# Ekadashi is fixed by the solar month Vrischikam.
REGIONAL_NOTE_ML = {
    "janmashtami": "അഷ്ടമിരോഹിണി",
    "dussehra": "വിജയദശമി — വിദ്യാരംഭം",
    "navratri": "നവരാത്രി — പൂജവയ്പ്പ്",
    "makar_sankranti": "മകരവിളക്ക്",
}

KOOTA_ML = {
    "varna": "വർണം", "vashya": "വശ്യം", "tara": "ദിനം (താരാ)", "yoni": "യോനി",
    "graha_maitri": "രാശ്യാധിപ (ഗ്രഹമൈത്രി)", "gana": "ഗണം",
    "bhakoot": "രാശി (ഭകൂടം)", "nadi": "നാഡി",
}
GANA_ML = {"Deva": "ദേവ", "Manushya": "മനുഷ്യ", "Rakshasa": "അസുര"}
NADI_ML = {"Adi": "ആദി", "Madhya": "മധ്യ", "Antya": "അന്ത്യ"}
VARNA_ML = {"Brahmin": "ബ്രാഹ്മണ", "Kshatriya": "ക്ഷത്രിയ", "Vaishya": "വൈശ്യ",
            "Shudra": "ശൂദ്ര"}
VASHYA_ML = {"Chatushpada": "ചതുഷ്പാദം", "Manava": "മാനവം", "Jalachara": "ജലചരം",
             "Vanachara": "വനചരം", "Keeta": "കീടം"}
YONI_ML = {
    "Horse": "കുതിര", "Elephant": "ആന", "Sheep": "ആട്", "Serpent": "പാമ്പ്",
    "Dog": "നായ", "Cat": "പൂച്ച", "Rat": "എലി", "Cow": "പശു", "Buffalo": "എരുമ",
    "Tiger": "പുലി", "Deer": "മാൻ", "Monkey": "കുരങ്ങ്", "Mongoose": "കീരി",
    "Lion": "സിംഹം",
}
TARA_ML = {
    "Janma": "ജന്മം", "Sampat": "സമ്പത്ത്", "Vipat": "വിപത്ത്", "Kshema": "ക്ഷേമം",
    "Pratyak": "പ്രത്യക്", "Sadhaka": "സാധകം", "Vadha": "വധം", "Mitra": "മിത്രം",
    "Ati-Mitra": "അതിമിത്രം",
}

WEEKDAY_ML = {
    "Sunday": "ഞായർ", "Monday": "തിങ്കൾ", "Tuesday": "ചൊവ്വ", "Wednesday": "ബുധൻ",
    "Thursday": "വ്യാഴം", "Friday": "വെള്ളി", "Saturday": "ശനി",
}

MONTHS_ML = ["ജനുവരി", "ഫെബ്രുവരി", "മാർച്ച്", "ഏപ്രിൽ", "മേയ്", "ജൂൺ", "ജൂലൈ", "ഓഗസ്റ്റ്",
             "സെപ്റ്റംബർ", "ഒക്ടോബർ", "നവംബർ", "ഡിസംബർ"]

CLOCK_ML = {"morning": "രാവിലെ", "afternoon": "ഉച്ചയ്ക്ക്", "evening": "വൈകുന്നേരം",
            "night": "രാത്രി"}

LIMBS_ML = {
    "tithi": "തിഥി", "nakshatra": "നക്ഷത്രം", "yoga": "യോഗം", "karana": "കരണം",
    "vara": "ആഴ്ച", "paksha": "പക്ഷം", "masa": "മാസം", "moon_sign": "കൂറ് (ചന്ദ്രരാശി)",
    "sun_sign": "സൂര്യരാശി", "panchang": "പഞ്ചാംഗം",
}


def add_ml(p: dict) -> dict:
    """add_hindi's Malayalam twin: name_ml / paksha_ml / label_ml / notes_ml."""
    from .names_i18n import add_names
    return add_names(p, "ml")
