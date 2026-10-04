"""Odia (ଓଡ଼ିଆ) names for the panchang, festivals and matching (DIVASTRO-123).

Same shape as names_hi.py, with the suffix _OR, plus the extra tables that
names_i18n.names_for("or") exposes. Every value is in Odia script; the
sentence-ending dari (।, U+0964) is shared with Devanagari and is allowed.

Regional choices (for a native reviewer):
  * Odia spellings double the consonant after repha as Odia almanacs do
    (ଚତୁର୍ଦ୍ଦଶୀ, ପୂର୍ଣ୍ଣିମା, ମୁହୂର୍ତ୍ତ, କାର୍ତ୍ତିକ).
  * The Odia calendar's months are SOLAR (Pana Sankranti / Maha Vishuba
    starts ବୈଶାଖ): SOLAR_MASA. Lunar months use the same words (Bhadrapada =
    ଭାଦ୍ରବ, Margashirsha = ମାର୍ଗଶିର).
  * ରାହୁ କାଳ, ଯମଗଣ୍ଡ, ଗୁଳିକ କାଳ. The almanac is ପାଞ୍ଜି.
  * Odisha names: Ashwin Purnima = କୁମାର ପୂର୍ଣ୍ଣିମା, Shravana Purnima =
    ଗହମା ପୂର୍ଣ୍ଣିମା, Vat Savitri = ସାବିତ୍ରୀ ବ୍ରତ, Devshayani = ହରିଶୟନ
    ଏକାଦଶୀ, Parsva = ପାର୍ଶ୍ୱ ପରିବର୍ତ୍ତନ ଏକାଦଶୀ.
  * Varjyam is transliterated (ବର୍ଜ୍ୟମ); not common in Odia almanacs.
"""

from __future__ import annotations

TITHI_OR = {
    "Pratipada": "ପ୍ରତିପଦା", "Dwitiya": "ଦ୍ୱିତୀୟା", "Tritiya": "ତୃତୀୟା",
    "Chaturthi": "ଚତୁର୍ଥୀ", "Panchami": "ପଞ୍ଚମୀ", "Shashthi": "ଷଷ୍ଠୀ",
    "Saptami": "ସପ୍ତମୀ", "Ashtami": "ଅଷ୍ଟମୀ", "Navami": "ନବମୀ",
    "Dashami": "ଦଶମୀ", "Ekadashi": "ଏକାଦଶୀ", "Dwadashi": "ଦ୍ୱାଦଶୀ",
    "Trayodashi": "ତ୍ରୟୋଦଶୀ", "Chaturdashi": "ଚତୁର୍ଦ୍ଦଶୀ", "Purnima": "ପୂର୍ଣ୍ଣିମା",
    "Amavasya": "ଅମାବାସ୍ୟା",
}

NAKSHATRAS_OR = {
    "Ashwini": "ଅଶ୍ୱିନୀ", "Bharani": "ଭରଣୀ", "Krittika": "କୃତ୍ତିକା", "Rohini": "ରୋହିଣୀ",
    "Mrigashira": "ମୃଗଶିରା", "Ardra": "ଆର୍ଦ୍ରା", "Punarvasu": "ପୁନର୍ବସୁ",
    "Pushya": "ପୁଷ୍ୟା", "Ashlesha": "ଅଶ୍ଳେଷା", "Magha": "ମଘା",
    "Purva Phalguni": "ପୂର୍ବ ଫାଲ୍ଗୁନୀ", "Uttara Phalguni": "ଉତ୍ତର ଫାଲ୍ଗୁନୀ",
    "Hasta": "ହସ୍ତା", "Chitra": "ଚିତ୍ରା", "Swati": "ସ୍ୱାତୀ", "Vishakha": "ବିଶାଖା",
    "Anuradha": "ଅନୁରାଧା", "Jyeshtha": "ଜ୍ୟେଷ୍ଠା", "Mula": "ମୂଳା",
    "Purva Ashadha": "ପୂର୍ବାଷାଢ଼ା", "Uttara Ashadha": "ଉତ୍ତରାଷାଢ଼ା",
    "Shravana": "ଶ୍ରବଣା", "Dhanishta": "ଧନିଷ୍ଠା", "Shatabhisha": "ଶତଭିଷା",
    "Purva Bhadrapada": "ପୂର୍ବ ଭାଦ୍ରପଦ", "Uttara Bhadrapada": "ଉତ୍ତର ଭାଦ୍ରପଦ",
    "Revati": "ରେବତୀ",
}

VARA_OR = {
    "Sunday": "ରବିବାର", "Monday": "ସୋମବାର", "Tuesday": "ମଙ୍ଗଳବାର",
    "Wednesday": "ବୁଧବାର", "Thursday": "ଗୁରୁବାର", "Friday": "ଶୁକ୍ରବାର",
    "Saturday": "ଶନିବାର",
}

YOGA_OR = {
    "Vishkambha": "ବିଷ୍କମ୍ଭ", "Priti": "ପ୍ରୀତି", "Ayushman": "ଆୟୁଷ୍ମାନ",
    "Saubhagya": "ସୌଭାଗ୍ୟ", "Shobhana": "ଶୋଭନ", "Atiganda": "ଅତିଗଣ୍ଡ",
    "Sukarma": "ସୁକର୍ମା", "Dhriti": "ଧୃତି", "Shula": "ଶୂଳ", "Ganda": "ଗଣ୍ଡ",
    "Vriddhi": "ବୃଦ୍ଧି", "Dhruva": "ଧ୍ରୁବ", "Vyaghata": "ବ୍ୟାଘାତ",
    "Harshana": "ହର୍ଷଣ", "Vajra": "ବଜ୍ର", "Siddhi": "ସିଦ୍ଧି",
    "Vyatipata": "ବ୍ୟତୀପାତ", "Variyana": "ବରୀୟାନ", "Parigha": "ପରିଘ",
    "Shiva": "ଶିବ", "Siddha": "ସିଦ୍ଧ", "Sadhya": "ସାଧ୍ୟ", "Shubha": "ଶୁଭ",
    "Shukla": "ଶୁକ୍ଳ", "Brahma": "ବ୍ରହ୍ମ", "Indra": "ଇନ୍ଦ୍ର", "Vaidhriti": "ବୈଧୃତି",
}

KARANA_OR = {
    "Bava": "ବବ", "Balava": "ବାଳବ", "Kaulava": "କୌଳବ", "Taitila": "ତୈତିଳ",
    "Gara": "ଗର", "Vanija": "ବଣିଜ", "Vishti": "ବିଷ୍ଟି (ଭଦ୍ରା)", "Shakuni": "ଶକୁନି",
    "Chatushpada": "ଚତୁଷ୍ପାଦ", "Naga": "ନାଗ", "Kimstughna": "କିଂସ୍ତୁଘ୍ନ",
}

PAKSHA_OR = {"Shukla": "ଶୁକ୍ଳ", "Krishna": "କୃଷ୍ଣ"}

NOTE_POLAR_OR = ("ଏହି ତାରିଖରେ ଏହି ଅକ୍ଷାଂଶରେ ସୂର୍ଯ୍ୟ ଉଦୟ ବା ଅସ୍ତ ହୁଅନ୍ତି ନାହିଁ, ତେଣୁ ବୈଦିକ ଦିନ "
                 "ସୂର୍ଯ୍ୟୋଦୟରୁ ଗଣାଯାଇପାରିବ ନାହିଁ। ତଳେ ଥିବା ଅଙ୍ଗଗୁଡ଼ିକ ସ୍ଥାନୀୟ ମଧ୍ୟରାତ୍ରିରୁ ଗଣନା "
                 "କରାଯାଇଛି, ଏବଂ ସୂର୍ଯ୍ୟୋଦୟ ଆଧାରିତ ମୁହୂର୍ତ୍ତ ପ୍ରଯୁଜ୍ୟ ନୁହେଁ।")
NOTE_WEDNESDAY_OR = ("ବୁଧବାରରେ ଅଭିଜିତ ମୁହୂର୍ତ୍ତ ଗ୍ରହଣ କରାଯାଏ ନାହିଁ — ବାରର ଅଧିପତି ବୁଧ "
                     "ଏହାକୁ ଦୂଷିତ କରନ୍ତି ବୋଲି ମାନାଯାଏ।")

MASA_OR = {
    "Chaitra": "ଚୈତ୍ର", "Vaishakha": "ବୈଶାଖ", "Jyeshtha": "ଜ୍ୟେଷ୍ଠ",
    "Ashadha": "ଆଷାଢ଼", "Shravana": "ଶ୍ରାବଣ", "Bhadrapada": "ଭାଦ୍ରବ",
    "Ashwin": "ଆଶ୍ୱିନ", "Kartika": "କାର୍ତ୍ତିକ", "Margashirsha": "ମାର୍ଗଶିର",
    "Pausha": "ପୌଷ", "Magha": "ମାଘ", "Phalguna": "ଫାଲ୍ଗୁନ",
}

# Odia solar months, keyed by the sidereal sign the Sun is in.
SOLAR_MASA_OR = {
    "Aries": "ବୈଶାଖ", "Taurus": "ଜ୍ୟେଷ୍ଠ", "Gemini": "ଆଷାଢ଼", "Cancer": "ଶ୍ରାବଣ",
    "Leo": "ଭାଦ୍ରବ", "Virgo": "ଆଶ୍ୱିନ", "Libra": "କାର୍ତ୍ତିକ", "Scorpio": "ମାର୍ଗଶିର",
    "Sagittarius": "ପୌଷ", "Capricorn": "ମାଘ", "Aquarius": "ଫାଲ୍ଗୁନ", "Pisces": "ଚୈତ୍ର",
}

RASHI_OR = {
    "Aries": "ମେଷ", "Taurus": "ବୃଷ", "Gemini": "ମିଥୁନ", "Cancer": "କର୍କଟ",
    "Leo": "ସିଂହ", "Virgo": "କନ୍ୟା", "Libra": "ତୁଳା", "Scorpio": "ବୃଶ୍ଚିକ",
    "Sagittarius": "ଧନୁ", "Capricorn": "ମକର", "Aquarius": "କୁମ୍ଭ", "Pisces": "ମୀନ",
}

GRAHA_OR = {
    "Sun": "ସୂର୍ଯ୍ୟ", "Moon": "ଚନ୍ଦ୍ର", "Mars": "ମଙ୍ଗଳ", "Mercury": "ବୁଧ",
    "Jupiter": "ବୃହସ୍ପତି", "Venus": "ଶୁକ୍ର", "Saturn": "ଶନି", "Rahu": "ରାହୁ", "Ketu": "କେତୁ",
}

CHOGHADIYA_OR = {
    "Amrit": "ଅମୃତ", "Shubh": "ଶୁଭ", "Labh": "ଲାଭ", "Char": "ଚର",
    "Rog": "ରୋଗ", "Kaal": "କାଳ", "Udveg": "ଉଦ୍ବେଗ",
}
CHOGHADIYA_QUALITY_OR = {"auspicious": "ଶୁଭ", "neutral": "ମଧ୍ୟମ", "inauspicious": "ଅଶୁଭ"}

TIMINGS_OR = {
    "rahu_kaal": "ରାହୁ କାଳ", "yamaganda": "ଯମଗଣ୍ଡ", "gulika": "ଗୁଳିକ କାଳ",
    "abhijit": "ଅଭିଜିତ ମୁହୂର୍ତ୍ତ", "brahma_muhurta": "ବ୍ରହ୍ମ ମୁହୂର୍ତ୍ତ",
    "pradosh": "ପ୍ରଦୋଷ କାଳ", "nishita": "ନିଶୀଥ କାଳ",
    "sunrise": "ସୂର୍ଯ୍ୟୋଦୟ", "sunset": "ସୂର୍ଯ୍ୟାସ୍ତ",
    "moonrise": "ଚନ୍ଦ୍ରୋଦୟ", "moonset": "ଚନ୍ଦ୍ରାସ୍ତ",
    "parana": "ପାରଣ ସମୟ", "durmuhurtam": "ଦୁର୍ମୁହୂର୍ତ୍ତ", "varjyam": "ବର୍ଜ୍ୟମ",
    "good_time": "ଶୁଭ ସମୟ",
}

FESTIVAL_TIMINGS_OR = {
    "parana": "ପାରଣ (ଉପବାସ ଭଙ୍ଗ)",
    "pradosh": "ପ୍ରଦୋଷ ପୂଜା",
    "pradosh_kaal": "ପ୍ରଦୋଷ କାଳ",
    "moonrise": "ଚନ୍ଦ୍ରୋଦୟ",
    "madhyahna": "ମଧ୍ୟାହ୍ନ ପୂଜା ମୁହୂର୍ତ୍ତ",
    "nishita": "ନିଶୀଥ କାଳ ପୂଜା",
    "aparahna": "ଅପରାହ୍ନ ପୂଜା",
    "vijay": "ବିଜୟ ମୁହୂର୍ତ୍ତ",
    "ghatasthapana": "ଘଟସ୍ଥାପନ ମୁହୂର୍ତ୍ତ",
    "ghatasthapana_abhijit": "ଘଟସ୍ଥାପନ (ଅଭିଜିତ)",
    "lakshmi_puja": "ଲକ୍ଷ୍ମୀ ପୂଜା ମୁହୂର୍ତ୍ତ",
    "dhanteras_puja": "ଧନତ୍ରୟୋଦଶୀ ପୂଜା ମୁହୂର୍ତ୍ତ",
    "vrishabha": "ବୃଷ କାଳ (ସ୍ଥିର ଲଗ୍ନ)",
    "punya_kaal": "ପୁଣ୍ୟ କାଳ",
    "maha_punya_kaal": "ମହା ପୁଣ୍ୟ କାଳ",
    "sankranti": "ସଂକ୍ରାନ୍ତି ସମୟ",
    "holika_dahan": "ହୋଲିକା ଦହନ ମୁହୂର୍ତ୍ତ",
    "holika_after_bhadra": "ଭଦ୍ରା ଶେଷ ପରେ ହୋଲିକା ଦହନ",
    "rakhi": "ରାକ୍ଷୀ ବାନ୍ଧିବା ମୁହୂର୍ତ୍ତ",
    "karwa_puja": "ପୂଜା ମୁହୂର୍ତ୍ତ",
    "puja": "ପୂଜା ମୁହୂର୍ତ୍ତ",
    "sandhya_arghya": "ସନ୍ଧ୍ୟା ଅର୍ଘ୍ୟ (ସୂର୍ଯ୍ୟାସ୍ତ)",
    "usha_arghya": "ଉଷା ଅର୍ଘ୍ୟ (ସୂର୍ଯ୍ୟୋଦୟ, ପରଦିନ)",
    "pratah": "ପ୍ରାତଃକାଳ ମୁହୂର୍ତ୍ତ",
    "sayahna": "ସାୟଂକାଳ ମୁହୂର୍ତ୍ତ",
    "tithi": "ତିଥି",
    "dwadashi_end": "ଦ୍ୱାଦଶୀ ଶେଷ",
    "hari_vasara_end": "ହରିବାସର ଶେଷ",
    "kutup": "କୁତପ ମୁହୂର୍ତ୍ତ",
    "rohina": "ରୌହିଣ ମୁହୂର୍ତ୍ତ",
    "aparahna_kaal": "ଅପରାହ୍ନ କାଳ",
    "abhyang": "ଅଭ୍ୟଙ୍ଗ ସ୍ନାନ (ଚନ୍ଦ୍ରୋଦୟରୁ ସୂର୍ଯ୍ୟୋଦୟ)",
}

FESTIVALS_OR = {
    "pradosh": "ପ୍ରଦୋଷ ବ୍ରତ",
    "sankashti": "ସଙ୍କଷ୍ଟି ଚତୁର୍ଥୀ",
    "vinayaka": "ବିନାୟକ ଚତୁର୍ଥୀ",
    "purnima": "ପୂର୍ଣ୍ଣିମା ବ୍ରତ",
    "amavasya": "ଅମାବାସ୍ୟା",
    "masik_shivratri": "ମାସିକ ଶିବରାତ୍ରି",
    "durgashtami": "ମାସିକ ଦୁର୍ଗାଷ୍ଟମୀ",
    "kalashtami": "କାଳାଷ୍ଟମୀ",
    "skanda_shashthi": "ସ୍କନ୍ଦ ଷଷ୍ଠୀ",
    "maha_shivratri": "ମହାଶିବରାତ୍ରି",
    "holika_dahan": "ହୋଲିକା ଦହନ",
    "ram_navami": "ରାମ ନବମୀ",
    "hanuman_jayanti": "ହନୁମାନ ଜୟନ୍ତୀ",
    "akshaya_tritiya": "ଅକ୍ଷୟ ତୃତୀୟା",
    "raksha_bandhan": "ରକ୍ଷା ବନ୍ଧନ (ଗହମା ପୂର୍ଣ୍ଣିମା)",
    "janmashtami": "ଶ୍ରୀକୃଷ୍ଣ ଜନ୍ମାଷ୍ଟମୀ",
    "ganesh_chaturthi": "ଗଣେଶ ଚତୁର୍ଥୀ",
    "chaitra_navratri": "ଚୈତ୍ର ନବରାତ୍ରି ଆରମ୍ଭ",
    "navratri": "ଶାରଦୀୟ ନବରାତ୍ରି ଆରମ୍ଭ",
    "dussehra": "ବିଜୟା ଦଶମୀ (ଦଶହରା)",
    "karwa_chauth": "କରୱା ଚୌଥ",
    "ahoi_ashtami": "ଅହୋଇ ଅଷ୍ଟମୀ",
    "dhanteras": "ଧନତେରସ",
    "diwali": "ଦୀପାବଳି (ଲକ୍ଷ୍ମୀ ପୂଜା)",
    "govardhan": "ଗୋବର୍ଦ୍ଧନ ପୂଜା",
    "bhai_dooj": "ଭାଇ ଦୁଜ (ଯମ ଦ୍ୱିତୀୟା)",
    "chhath": "ଛଠ ପୂଜା",
    "vasant_panchami": "ବସନ୍ତ ପଞ୍ଚମୀ (ସରସ୍ୱତୀ ପୂଜା)",
    "guru_purnima": "ଗୁରୁ ପୂର୍ଣ୍ଣିମା",
    "sharad_purnima": "କୁମାର ପୂର୍ଣ୍ଣିମା (ଶରଦ ପୂର୍ଣ୍ଣିମା)",
    "sakat_chauth": "ସକଟ ଚୌଥ",
    "mauni_amavasya": "ମୌନୀ ଅମାବାସ୍ୟା",
    "sheetala_ashtami": "ଶୀତଳା ଅଷ୍ଟମୀ",
    "gudi_padwa": "ଗୁଡ଼ି ପାଡ଼ୱା / ଉଗାଦି",
    "gangaur": "ଗଣଗୌର",
    "vat_savitri": "ସାବିତ୍ରୀ ବ୍ରତ",
    "ganga_dussehra": "ଗଙ୍ଗା ଦଶହରା",
    "vat_purnima": "ବଟ ପୂର୍ଣ୍ଣିମା ବ୍ରତ",
    "hariyali_teej": "ହରିୟାଲି ତୀଜ",
    "nag_panchami": "ନାଗ ପଞ୍ଚମୀ",
    "kajari_teej": "କଜରୀ ତୀଜ",
    "hal_shashthi": "ହଳ ଷଷ୍ଠୀ (ବଳରାମ ଜୟନ୍ତୀ)",
    "hartalika_teej": "ହରତାଳିକା ତୀଜ",
    "rishi_panchami": "ଋଷି ପଞ୍ଚମୀ",
    "anant_chaturdashi": "ଅନନ୍ତ ଚତୁର୍ଦ୍ଦଶୀ",
    "pitru_paksha": "ପିତୃପକ୍ଷ ଆରମ୍ଭ (ପ୍ରତିପଦା ଶ୍ରାଦ୍ଧ)",
    "jivitputrika": "ଜୀବିତପୁତ୍ରିକା ବ୍ରତ (ଜିତିଆ)",
    "sarva_pitru_amavasya": "ମହାଳୟା (ସର୍ବପିତୃ ଅମାବାସ୍ୟା)",
    "narak_chaturdashi": "ନରକ ଚତୁର୍ଦ୍ଦଶୀ",
    "tulsi_vivah": "ତୁଳସୀ ବିବାହ",
    "kartik_purnima": "କାର୍ତ୍ତିକ ପୂର୍ଣ୍ଣିମା",
    "dev_deepawali": "ଦେବ ଦୀପାବଳି",
    "makar_sankranti": "ମକର ସଂକ୍ରାନ୍ତି",
    "lohri": "ଲୋହରି",
    "holi": "ହୋଲି",
    "ekadashi": "ଏକାଦଶୀ",
    "santan_saptami": "ସନ୍ତାନ ସପ୍ତମୀ",
}

EKADASHI_OR = {
    "Kamada Ekadashi": "କାମଦା ଏକାଦଶୀ",
    "Varuthini Ekadashi": "ବରୂଥିନୀ ଏକାଦଶୀ",
    "Mohini Ekadashi": "ମୋହିନୀ ଏକାଦଶୀ",
    "Apara Ekadashi": "ଅପରା ଏକାଦଶୀ",
    "Nirjala Ekadashi": "ନିର୍ଜଳା ଏକାଦଶୀ",
    "Yogini Ekadashi": "ଯୋଗିନୀ ଏକାଦଶୀ",
    "Devshayani Ekadashi": "ହରିଶୟନ ଏକାଦଶୀ",
    "Kamika Ekadashi": "କାମିକା ଏକାଦଶୀ",
    "Shravana Putrada Ekadashi": "ଶ୍ରାବଣ ପୁତ୍ରଦା ଏକାଦଶୀ",
    "Aja Ekadashi": "ଅଜା ଏକାଦଶୀ",
    "Parsva Ekadashi": "ପାର୍ଶ୍ୱ ପରିବର୍ତ୍ତନ ଏକାଦଶୀ",
    "Indira Ekadashi": "ଇନ୍ଦିରା ଏକାଦଶୀ",
    "Papankusha Ekadashi": "ପାପାଙ୍କୁଶା ଏକାଦଶୀ",
    "Rama Ekadashi": "ରମା ଏକାଦଶୀ",
    "Devutthana Ekadashi": "ଦେବୋତ୍ଥାନ ଏକାଦଶୀ",
    "Utpanna Ekadashi": "ଉତ୍ପନ୍ନା ଏକାଦଶୀ",
    "Mokshada Ekadashi": "ମୋକ୍ଷଦା ଏକାଦଶୀ",
    "Saphala Ekadashi": "ସଫଳା ଏକାଦଶୀ",
    "Pausha Putrada Ekadashi": "ପୌଷ ପୁତ୍ରଦା ଏକାଦଶୀ",
    "Shattila Ekadashi": "ଷଟତିଳା ଏକାଦଶୀ",
    "Jaya Ekadashi": "ଜୟା ଏକାଦଶୀ",
    "Vijaya Ekadashi": "ବିଜୟା ଏକାଦଶୀ",
    "Amalaki Ekadashi": "ଆମଳକୀ ଏକାଦଶୀ",
    "Papmochani Ekadashi": "ପାପମୋଚନୀ ଏକାଦଶୀ",
    "Padmini Ekadashi": "ପଦ୍ମିନୀ ଏକାଦଶୀ",
    "Parama Ekadashi": "ପରମା ଏକାଦଶୀ",
}

# Regional framings. Odisha keeps Hanuman Jayanti on Pana Sankranti (solar,
# another date); Kartik Purnima is Boita Bandana; Phalguna Purnima is Dola
# Purnima (the day of Holika Dahan).
REGIONAL_NOTE_OR = {
    "navratri": "ଦୁର୍ଗା ପୂଜା",
    "sharad_purnima": "କୁମାର ପୂର୍ଣ୍ଣିମା",
    "raksha_bandhan": "ଗହମା ପୂର୍ଣ୍ଣିମା",
    "kartik_purnima": "ବୋଇତ ବନ୍ଦାଣ",
    "holika_dahan": "ଦୋଳ ପୂର୍ଣ୍ଣିମା",
    "vat_savitri": "ସାବିତ୍ରୀ ବ୍ରତ",
}

KOOTA_OR = {
    "varna": "ବର୍ଣ୍ଣ", "vashya": "ବଶ୍ୟ", "tara": "ତାରା", "yoni": "ଯୋନି",
    "graha_maitri": "ଗ୍ରହମୈତ୍ରୀ", "gana": "ଗଣ", "bhakoot": "ଭକୂଟ", "nadi": "ନାଡ଼ୀ",
}
GANA_OR = {"Deva": "ଦେବ", "Manushya": "ମନୁଷ୍ୟ", "Rakshasa": "ରାକ୍ଷସ"}
NADI_OR = {"Adi": "ଆଦ୍ୟ", "Madhya": "ମଧ୍ୟ", "Antya": "ଅନ୍ତ୍ୟ"}
VARNA_OR = {"Brahmin": "ବ୍ରାହ୍ମଣ", "Kshatriya": "କ୍ଷତ୍ରିୟ", "Vaishya": "ବୈଶ୍ୟ",
            "Shudra": "ଶୂଦ୍ର"}
VASHYA_OR = {"Chatushpada": "ଚତୁଷ୍ପଦ", "Manava": "ମାନବ", "Jalachara": "ଜଳଚର",
             "Vanachara": "ବନଚର", "Keeta": "କୀଟ"}
YONI_OR = {
    "Horse": "ଘୋଡ଼ା", "Elephant": "ହାତୀ", "Sheep": "ମେଣ୍ଢା", "Serpent": "ସାପ",
    "Dog": "କୁକୁର", "Cat": "ବିରାଡ଼ି", "Rat": "ମୂଷା", "Cow": "ଗାଈ", "Buffalo": "ମଇଁଷି",
    "Tiger": "ବାଘ", "Deer": "ହରିଣ", "Monkey": "ମାଙ୍କଡ଼", "Mongoose": "ନେଉଳ",
    "Lion": "ସିଂହ",
}
TARA_OR = {
    "Janma": "ଜନ୍ମ", "Sampat": "ସମ୍ପତ", "Vipat": "ବିପତ", "Kshema": "କ୍ଷେମ",
    "Pratyak": "ପ୍ରତ୍ୟରି", "Sadhaka": "ସାଧକ", "Vadha": "ବଧ", "Mitra": "ମିତ୍ର",
    "Ati-Mitra": "ଅତିମିତ୍ର",
}

WEEKDAY_OR = {
    "Sunday": "ରବି", "Monday": "ସୋମ", "Tuesday": "ମଙ୍ଗଳ", "Wednesday": "ବୁଧ",
    "Thursday": "ଗୁରୁ", "Friday": "ଶୁକ୍ର", "Saturday": "ଶନି",
}

MONTHS_OR = ["ଜାନୁଆରୀ", "ଫେବୃଆରୀ", "ମାର୍ଚ୍ଚ", "ଅପ୍ରେଲ", "ମଇ", "ଜୁନ", "ଜୁଲାଇ", "ଅଗଷ୍ଟ",
             "ସେପ୍ଟେମ୍ବର", "ଅକ୍ଟୋବର", "ନଭେମ୍ବର", "ଡିସେମ୍ବର"]

CLOCK_OR = {"morning": "ସକାଳ", "afternoon": "ଦ୍ୱିପହର", "evening": "ସନ୍ଧ୍ୟା",
            "night": "ରାତି"}

LIMBS_OR = {
    "tithi": "ତିଥି", "nakshatra": "ନକ୍ଷତ୍ର", "yoga": "ଯୋଗ", "karana": "କରଣ",
    "vara": "ବାର", "paksha": "ପକ୍ଷ", "masa": "ମାସ", "moon_sign": "ଚନ୍ଦ୍ର ରାଶି",
    "sun_sign": "ସୂର୍ଯ୍ୟ ରାଶି", "panchang": "ପାଞ୍ଜି",
}


def add_or(p: dict) -> dict:
    """add_hindi's Odia twin: name_or / paksha_or / label_or / notes_or."""
    from .names_i18n import add_names
    return add_names(p, "or")
