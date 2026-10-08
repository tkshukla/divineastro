"""Gujarati (ગુજરાતી, Gujarati script) names for the panchang, festivals and matching (DIVASTRO-143).

Same shape as names_kn.py / names_bn.py: one table per name, suffix _GU, keyed by the
ENGLISH name the engines emit; names_i18n.names_for("gu") exposes them. A key left "" (or a
table left out) falls back to the English name, so the site works while this fills up; `python -m
app.lang_data check gu` lists what is left. Use the names Gujarati panchang and jyotish
tradition uses, in this language's script, not a transliteration of the English. Document
choices a native reviewer should confirm in this docstring (see names_bn.py).

Choices for a native reviewer (Gujarat panchang tradition):
  * Months are the Gujarati panchang forms (ચૈત્ર વૈશાખ જેઠ અષાઢ શ્રાવણ ભાદરવો આસો કારતક માગશર
    પોષ મહા ફાગણ). The Gujarati calendar is Vikram Samvat, whose year begins the day after Diwali
    (Kartak sud ekam, બેસતું વર્ષ), and its months are reckoned Amanta (a month ends on Amavasya,
    so Diwali falls on આસો વદ અમાસ). The engine's MASA table is Amanta too, so Gujarati month
    names map one-to-one (Ashwin = આસો, Bhadrapada = ભાદરવો). The festival dates come from the
    engine and are the same for every language.
  * Paksha is સુદ / વદ (as printed in Gujarati panchangs and newspapers), so a tithi label reads
    "સુદ પાંચમ". Tithis are the everyday Gujarati forms (એકમ બીજ ત્રીજ ચોથ પાંચમ છઠ સાતમ આઠમ
    નોમ દશમ અગિયારસ બારસ તેરસ ચૌદશ પૂનમ અમાસ); the Ekadashi vrat names use એકાદશી.
  * Rahu Kaal is રાહુકાળ, Yamaganda યમગંડ, Gulika ગુલિક કાળ, Varjyam વર્જ્ય (also an ordinary word
    meaning "to be avoided"; the reviewer should confirm).
  * Govardhan Puja is the day Gujaratis keep as બેસતું વર્ષ: shown as a REGIONAL_NOTE only, the
    engine has no separate New Year observance. Holi is ધુળેટી, Makar Sankranti is shown as
    ઉત્તરાયણ in brackets, Raksha Bandhan notes બળેવ.
  * Yoni names use the traditional Sanskrit animal words (અશ્વ ગજ મેષ ...), Nadi is આદ્ય / મધ્ય /
    અંત્ય, Gana દેવ / મનુષ્ય / રાક્ષસ.

Tables: TITHI(16) NAKSHATRAS(27) VARA(7) YOGA(27) KARANA(11) PAKSHA(2) MASA(12 lunar months)
SOLAR_MASA(optional: only if the calendar is solar) RASHI(12) GRAHA(9) CHOGHADIYA(7)
CHOGHADIYA_QUALITY(3) TIMINGS FESTIVAL_TIMINGS FESTIVALS EKADASHI REGIONAL_NOTE(optional)
KOOTA GANA NADI VARNA VASHYA YONI TARA WEEKDAY(7, short) MONTHS(12) CLOCK(4) LIMBS(10) and
the two notes NOTE_POLAR / NOTE_WEDNESDAY.
"""

from __future__ import annotations


TITHI_GU = {
    "Pratipada": "એકમ",
    "Dwitiya": "બીજ",
    "Tritiya": "ત્રીજ",
    "Chaturthi": "ચોથ",
    "Panchami": "પાંચમ",
    "Shashthi": "છઠ",
    "Saptami": "સાતમ",
    "Ashtami": "આઠમ",
    "Navami": "નોમ",
    "Dashami": "દશમ",
    "Ekadashi": "અગિયારસ",
    "Dwadashi": "બારસ",
    "Trayodashi": "તેરસ",
    "Chaturdashi": "ચૌદશ",
    "Purnima": "પૂનમ",
    "Amavasya": "અમાસ",
}

NAKSHATRAS_GU = {
    "Ashwini": "અશ્વિની",
    "Bharani": "ભરણી",
    "Krittika": "કૃત્તિકા",
    "Rohini": "રોહિણી",
    "Mrigashira": "મૃગશીર્ષ",
    "Ardra": "આર્દ્રા",
    "Punarvasu": "પુનર્વસુ",
    "Pushya": "પુષ્ય",
    "Ashlesha": "આશ્લેષા",
    "Magha": "મઘા",
    "Purva Phalguni": "પૂર્વા ફાલ્ગુની",
    "Uttara Phalguni": "ઉત્તરા ફાલ્ગુની",
    "Hasta": "હસ્ત",
    "Chitra": "ચિત્રા",
    "Swati": "સ્વાતિ",
    "Vishakha": "વિશાખા",
    "Anuradha": "અનુરાધા",
    "Jyeshtha": "જ્યેષ્ઠા",
    "Mula": "મૂળ",
    "Purva Ashadha": "પૂર્વાષાઢા",
    "Uttara Ashadha": "ઉત્તરાષાઢા",
    "Shravana": "શ્રવણ",
    "Dhanishta": "ધનિષ્ઠા",
    "Shatabhisha": "શતભિષા",
    "Purva Bhadrapada": "પૂર્વા ભાદ્રપદ",
    "Uttara Bhadrapada": "ઉત્તરા ભાદ્રપદ",
    "Revati": "રેવતી",
}

VARA_GU = {
    "Sunday": "રવિવાર",
    "Monday": "સોમવાર",
    "Tuesday": "મંગળવાર",
    "Wednesday": "બુધવાર",
    "Thursday": "ગુરુવાર",
    "Friday": "શુક્રવાર",
    "Saturday": "શનિવાર",
}

YOGA_GU = {
    "Vishkambha": "વિષ્કુંભ",
    "Priti": "પ્રીતિ",
    "Ayushman": "આયુષ્માન",
    "Saubhagya": "સૌભાગ્ય",
    "Shobhana": "શોભન",
    "Atiganda": "અતિગંડ",
    "Sukarma": "સુકર્મા",
    "Dhriti": "ધૃતિ",
    "Shula": "શૂળ",
    "Ganda": "ગંડ",
    "Vriddhi": "વૃદ્ધિ",
    "Dhruva": "ધ્રુવ",
    "Vyaghata": "વ્યાઘાત",
    "Harshana": "હર્ષણ",
    "Vajra": "વજ્ર",
    "Siddhi": "સિદ્ધિ",
    "Vyatipata": "વ્યતીપાત",
    "Variyana": "વરીયાન",
    "Parigha": "પરિઘ",
    "Shiva": "શિવ",
    "Siddha": "સિદ્ધ",
    "Sadhya": "સાધ્ય",
    "Shubha": "શુભ",
    "Shukla": "શુક્લ",
    "Brahma": "બ્રહ્મ",
    "Indra": "ઇન્દ્ર",
    "Vaidhriti": "વૈધૃતિ",
}

KARANA_GU = {
    "Bava": "બવ",
    "Balava": "બાલવ",
    "Kaulava": "કૌલવ",
    "Taitila": "તૈતિલ",
    "Gara": "ગર",
    "Vanija": "વણિજ",
    "Vishti": "વિષ્ટિ (ભદ્રા)",
    "Shakuni": "શકુનિ",
    "Chatushpada": "ચતુષ્પાદ",
    "Naga": "નાગ",
    "Kimstughna": "કિંસ્તુઘ્ન",
}

PAKSHA_GU = {
    "Shukla": "સુદ",
    "Krishna": "વદ",
}

MASA_GU = {
    "Chaitra": "ચૈત્ર",
    "Vaishakha": "વૈશાખ",
    "Jyeshtha": "જેઠ",
    "Ashadha": "અષાઢ",
    "Shravana": "શ્રાવણ",
    "Bhadrapada": "ભાદરવો",
    "Ashwin": "આસો",
    "Kartika": "કારતક",
    "Margashirsha": "માગશર",
    "Pausha": "પોષ",
    "Magha": "મહા",
    "Phalguna": "ફાગણ",
}

# lunar months are MASA; fill this only if the calendar is solar (keys "Aries".."Pisces")
SOLAR_MASA_GU = {}

RASHI_GU = {
    "Aries": "મેષ",
    "Taurus": "વૃષભ",
    "Gemini": "મિથુન",
    "Cancer": "કર્ક",
    "Leo": "સિંહ",
    "Virgo": "કન્યા",
    "Libra": "તુલા",
    "Scorpio": "વૃશ્ચિક",
    "Sagittarius": "ધનુ",
    "Capricorn": "મકર",
    "Aquarius": "કુંભ",
    "Pisces": "મીન",
}

GRAHA_GU = {
    "Sun": "સૂર્ય",
    "Moon": "ચંદ્ર",
    "Mars": "મંગળ",
    "Mercury": "બુધ",
    "Jupiter": "ગુરુ",
    "Venus": "શુક્ર",
    "Saturn": "શનિ",
    "Rahu": "રાહુ",
    "Ketu": "કેતુ",
}

CHOGHADIYA_GU = {
    "Amrit": "અમૃત",
    "Shubh": "શુભ",
    "Labh": "લાભ",
    "Char": "ચલ",
    "Rog": "રોગ",
    "Kaal": "કાળ",
    "Udveg": "ઉદ્વેગ",
}

CHOGHADIYA_QUALITY_GU = {
    "auspicious": "શુભ",   # Auspicious
    "neutral": "મધ્યમ",   # Neutral
    "inauspicious": "અશુભ",   # Inauspicious
}

TIMINGS_GU = {
    "rahu_kaal": "રાહુકાળ",   # Rahu Kaal
    "yamaganda": "યમગંડ",   # Yamaganda
    "gulika": "ગુલિક કાળ",   # Gulika Kaal
    "abhijit": "અભિજિત મુહૂર્ત",   # Abhijit Muhurta
    "brahma_muhurta": "બ્રહ્મ મુહૂર્ત",   # Brahma Muhurta
    "pradosh": "પ્રદોષ કાળ",   # Pradosh Kaal
    "nishita": "નિશીથ કાળ",   # Nishita Kaal
    "sunrise": "સૂર્યોદય",   # Sunrise
    "sunset": "સૂર્યાસ્ત",   # Sunset
    "moonrise": "ચંદ્રોદય",   # Moonrise
    "moonset": "ચંદ્રાસ્ત",   # Moonset
    "parana": "પારણાનો સમય",   # Parana time
    "durmuhurtam": "દુર્મુહૂર્ત",   # Durmuhurtam
    "varjyam": "વર્જ્ય",   # Varjyam
    "good_time": "શુભ સમય",   # Good time
}

FESTIVAL_TIMINGS_GU = {
    "parana": "પારણાં (વ્રત છોડવાનો સમય)",   # Parana (breaking the fast)
    "pradosh": "પ્રદોષ પૂજા",   # Pradosh puja
    "pradosh_kaal": "પ્રદોષ કાળ",   # Pradosh kaal
    "moonrise": "ચંદ્રોદય",   # Moonrise
    "madhyahna": "મધ્યાહ્ન પૂજા મુહૂર્ત",   # Madhyahna puja muhurat
    "nishita": "નિશીથ કાળ પૂજા",   # Nishita kaal puja
    "aparahna": "અપરાહ્ન પૂજા",   # Aparahna puja
    "vijay": "વિજય મુહૂર્ત",   # Vijay muhurat
    "ghatasthapana": "ઘટસ્થાપના મુહૂર્ત",   # Ghatasthapana muhurat
    "ghatasthapana_abhijit": "ઘટસ્થાપના (અભિજિત)",   # Ghatasthapana (Abhijit)
    "lakshmi_puja": "લક્ષ્મી પૂજન મુહૂર્ત",   # Lakshmi puja muhurat
    "dhanteras_puja": "ધનતેરસ પૂજા મુહૂર્ત",   # Dhanteras puja muhurat
    "vrishabha": "વૃષભ કાળ (સ્થિર લગ્ન)",   # Vrishabha kaal (sthir lagna)
    "punya_kaal": "પુણ્ય કાળ",   # Punya kaal
    "maha_punya_kaal": "મહાપુણ્ય કાળ",   # Maha punya kaal
    "sankranti": "સંક્રાંતિની ક્ષણ",   # Sankranti moment
    "holika_dahan": "હોલિકા દહન મુહૂર્ત",   # Holika Dahan muhurat
    "holika_after_bhadra": "ભદ્રા પૂરી થયા પછી હોલિકા દહન",   # Holika Dahan after Bhadra ends
    "rakhi": "રાખડી બાંધવાનું મુહૂર્ત",   # Rakhi muhurat
    "karwa_puja": "પૂજા મુહૂર્ત",   # Puja muhurat
    "puja": "પૂજા મુહૂર્ત",   # Puja muhurat
    "sandhya_arghya": "સંધ્યા અર્ઘ્ય (સૂર્યાસ્ત)",   # Sandhya arghya (sunset)
    "usha_arghya": "ઉષા અર્ઘ્ય (બીજા દિવસે સૂર્યોદય)",   # Usha arghya (sunrise, next day)
    "pratah": "પ્રાતઃકાળ મુહૂર્ત",   # Pratahkala muhurat
    "sayahna": "સાયંકાળ મુહૂર્ત",   # Sayahnakala muhurat
    "tithi": "તિથિ",   # Tithi
    "dwadashi_end": "બારસ પૂરી થાય",   # Dwadashi ends
    "hari_vasara_end": "હરિવાસર પૂરો થાય",   # Hari Vasara ends
    "kutup": "કુતુપ મુહૂર્ત",   # Kutup muhurat
    "rohina": "રોહિણ મુહૂર્ત",   # Rohina muhurat
    "aparahna_kaal": "અપરાહ્ન કાળ",   # Aparahna kaal
    "abhyang": "અભ્યંગ સ્નાન (ચંદ્રોદયથી સૂર્યોદય)",   # Abhyang snan (moonrise to sunrise)
}

FESTIVALS_GU = {
    "pradosh": "પ્રદોષ વ્રત",   # Pradosh Vrat
    "sankashti": "સંકષ્ટી ચતુર્થી",   # Sankashti Chaturthi
    "vinayaka": "વિનાયક ચતુર્થી",   # Vinayaka Chaturthi
    "purnima": "પૂનમ વ્રત",   # Purnima Vrat
    "amavasya": "અમાસ",   # Amavasya
    "masik_shivratri": "માસિક શિવરાત્રિ",   # Masik Shivratri
    "durgashtami": "માસિક દુર્ગાષ્ટમી",   # Masik Durgashtami
    "kalashtami": "કાલાષ્ટમી",   # Kalashtami
    "skanda_shashthi": "સ્કંદ ષષ્ઠી",   # Skanda Shashthi
    "maha_shivratri": "મહાશિવરાત્રિ",   # Maha Shivratri
    "holika_dahan": "હોલિકા દહન",   # Holika Dahan
    "ram_navami": "રામ નવમી",   # Ram Navami
    "hanuman_jayanti": "હનુમાન જયંતી",   # Hanuman Jayanti
    "akshaya_tritiya": "અક્ષય તૃતીયા",   # Akshaya Tritiya
    "raksha_bandhan": "રક્ષાબંધન",   # Raksha Bandhan
    "janmashtami": "જન્માષ્ટમી",   # Krishna Janmashtami
    "ganesh_chaturthi": "ગણેશ ચતુર્થી",   # Ganesh Chaturthi
    "chaitra_navratri": "ચૈત્ર નવરાત્રિ પ્રારંભ",   # Chaitra Navratri begins
    "navratri": "શારદીય નવરાત્રિ પ્રારંભ",   # Sharad Navratri begins
    "dussehra": "દશેરા (વિજયાદશમી)",   # Dussehra (Vijayadashami)
    "karwa_chauth": "કરવા ચોથ",   # Karwa Chauth
    "ahoi_ashtami": "અહોઈ આઠમ",   # Ahoi Ashtami
    "dhanteras": "ધનતેરસ",   # Dhanteras
    "diwali": "દિવાળી (લક્ષ્મી પૂજન)",   # Diwali (Lakshmi Puja)
    "govardhan": "ગોવર્ધન પૂજા",   # Govardhan Puja
    "bhai_dooj": "ભાઈબીજ",   # Bhai Dooj
    "chhath": "છઠ પૂજા",   # Chhath Puja
    "vasant_panchami": "વસંત પંચમી",   # Vasant Panchami
    "guru_purnima": "ગુરુ પૂનમ",   # Guru Purnima
    "sharad_purnima": "શરદ પૂનમ",   # Sharad Purnima
    "sakat_chauth": "સકટ ચોથ",   # Sakat Chauth
    "mauni_amavasya": "મૌની અમાસ",   # Mauni Amavasya
    "sheetala_ashtami": "શીતળા આઠમ (બસોડા)",   # Sheetala Ashtami (Basoda)
    "gudi_padwa": "ગુડી પડવો / ઉગાદી",   # Gudi Padwa / Ugadi
    "gangaur": "ગણગૌર",   # Gangaur
    "vat_savitri": "વટ સાવિત્રી વ્રત",   # Vat Savitri Vrat
    "ganga_dussehra": "ગંગા દશેરા",   # Ganga Dussehra
    "vat_purnima": "વટ પૂનમ વ્રત",   # Vat Purnima Vrat
    "hariyali_teej": "હરિયાળી તીજ",   # Hariyali Teej
    "nag_panchami": "નાગ પાંચમ",   # Nag Panchami
    "kajari_teej": "કજરી તીજ",   # Kajari Teej
    "hal_shashthi": "હળ છઠ (લલહી છઠ)",   # Hal Shashthi (Lalahi Chhath)
    "hartalika_teej": "હરતાલિકા તીજ",   # Hartalika Teej
    "rishi_panchami": "ઋષિ પાંચમ",   # Rishi Panchami
    "anant_chaturdashi": "અનંત ચૌદશ",   # Anant Chaturdashi
    "pitru_paksha": "પિતૃ પક્ષ પ્રારંભ (એકમનું શ્રાદ્ધ)",   # Pitru Paksha begins (Pratipada Shraddha)
    "jivitputrika": "જીવિત્પુત્રિકા વ્રત (જિતિયા)",   # Jivitputrika Vrat (Jitiya)
    "sarva_pitru_amavasya": "સર્વપિતૃ અમાસ (મહાલય)",   # Sarva Pitru Amavasya (Mahalaya)
    "narak_chaturdashi": "નરક ચતુર્દશી (કાળી ચૌદશ)",   # Narak Chaturdashi (Roop Chaudas)
    "tulsi_vivah": "તુલસી વિવાહ",   # Tulsi Vivah
    "kartik_purnima": "કારતક પૂનમ",   # Kartik Purnima
    "dev_deepawali": "દેવ દિવાળી",   # Dev Deepawali
    "makar_sankranti": "મકરસંક્રાંતિ (ઉત્તરાયણ)",   # Makar Sankranti
    "lohri": "લોહડી",   # Lohri
    "holi": "ધુળેટી",   # Holi
    "ekadashi": "એકાદશી",   # Ekadashi
    "santan_saptami": "સંતાન સાતમ",   # Santan Saptami
}

EKADASHI_GU = {
    "Kamada Ekadashi": "કામદા એકાદશી",
    "Varuthini Ekadashi": "વરુથિની એકાદશી",
    "Mohini Ekadashi": "મોહિની એકાદશી",
    "Apara Ekadashi": "અપરા એકાદશી",
    "Nirjala Ekadashi": "નિર્જળા એકાદશી",
    "Yogini Ekadashi": "યોગિની એકાદશી",
    "Devshayani Ekadashi": "દેવશયની એકાદશી",
    "Kamika Ekadashi": "કામિકા એકાદશી",
    "Shravana Putrada Ekadashi": "શ્રાવણ પુત્રદા એકાદશી",
    "Aja Ekadashi": "અજા એકાદશી",
    "Parsva Ekadashi": "પાર્શ્વ એકાદશી (પરિવર્તિની)",
    "Indira Ekadashi": "ઇન્દિરા એકાદશી",
    "Papankusha Ekadashi": "પાપાંકુશા એકાદશી",
    "Rama Ekadashi": "રમા એકાદશી",
    "Devutthana Ekadashi": "દેવઊઠી એકાદશી",
    "Utpanna Ekadashi": "ઉત્પન્ના એકાદશી",
    "Mokshada Ekadashi": "મોક્ષદા એકાદશી",
    "Saphala Ekadashi": "સફળા એકાદશી",
    "Pausha Putrada Ekadashi": "પોષ પુત્રદા એકાદશી",
    "Shattila Ekadashi": "ષટતિલા એકાદશી",
    "Jaya Ekadashi": "જયા એકાદશી",
    "Vijaya Ekadashi": "વિજયા એકાદશી",
    "Amalaki Ekadashi": "આમલકી એકાદશી",
    "Papmochani Ekadashi": "પાપમોચની એકાદશી",
    "Padmini Ekadashi": "પદ્મિની એકાદશી",
    "Parama Ekadashi": "પરમા એકાદશી",
}

# optional strong regional framing per festival key
REGIONAL_NOTE_GU = {
    "govardhan": "બેસતું વર્ષ",
    "raksha_bandhan": "બળેવ",
}

KOOTA_GU = {
    "varna": "વર્ણ",   # Varna
    "vashya": "વશ્ય",   # Vashya
    "tara": "તારા (દિન)",   # Tara (Dina)
    "yoni": "યોનિ",   # Yoni
    "graha_maitri": "ગ્રહમૈત્રી",   # Graha Maitri
    "gana": "ગણ",   # Gana
    "bhakoot": "ભકૂટ",   # Bhakoot
    "nadi": "નાડી",   # Nadi
}

GANA_GU = {
    "Deva": "દેવ",
    "Manushya": "મનુષ્ય",
    "Rakshasa": "રાક્ષસ",
}

NADI_GU = {
    "Adi": "આદ્ય",
    "Madhya": "મધ્ય",
    "Antya": "અંત્ય",
}

VARNA_GU = {
    "Brahmin": "બ્રાહ્મણ",
    "Kshatriya": "ક્ષત્રિય",
    "Vaishya": "વૈશ્ય",
    "Shudra": "શૂદ્ર",
}

VASHYA_GU = {
    "Chatushpada": "ચતુષ્પાદ",
    "Manava": "માનવ",
    "Jalachara": "જળચર",
    "Vanachara": "વનચર",
    "Keeta": "કીટ",
}

YONI_GU = {
    "Horse": "અશ્વ",
    "Elephant": "ગજ",
    "Sheep": "મેષ",
    "Serpent": "સર્પ",
    "Dog": "શ્વાન",
    "Cat": "માર્જાર",
    "Rat": "મૂષક",
    "Cow": "ગાય",
    "Buffalo": "મહિષ",
    "Tiger": "વ્યાઘ્ર",
    "Deer": "મૃગ",
    "Monkey": "વાનર",
    "Mongoose": "નકુલ",
    "Lion": "સિંહ",
}

TARA_GU = {
    "Janma": "જન્મ",
    "Sampat": "સંપત",
    "Vipat": "વિપત",
    "Kshema": "ક્ષેમ",
    "Pratyak": "પ્રત્યક",
    "Sadhaka": "સાધક",
    "Vadha": "વધ",
    "Mitra": "મિત્ર",
    "Ati-Mitra": "અતિમિત્ર",
}

WEEKDAY_GU = {
    "Sunday": "રવિ",   # Sun
    "Monday": "સોમ",   # Mon
    "Tuesday": "મંગળ",   # Tue
    "Wednesday": "બુધ",   # Wed
    "Thursday": "ગુરુ",   # Thu
    "Friday": "શુક્ર",   # Fri
    "Saturday": "શનિ",   # Sat
}

MONTHS_GU = [
    "જાન્યુઆરી",   # January
    "ફેબ્રુઆરી",   # February
    "માર્ચ",   # March
    "એપ્રિલ",   # April
    "મે",   # May
    "જૂન",   # June
    "જુલાઈ",   # July
    "ઑગસ્ટ",   # August
    "સપ્ટેમ્બર",   # September
    "ઑક્ટોબર",   # October
    "નવેમ્બર",   # November
    "ડિસેમ્બર",   # December
]

CLOCK_GU = {
    "morning": "સવાર",
    "afternoon": "બપોર",
    "evening": "સાંજ",
    "night": "રાત",
}

LIMBS_GU = {
    "tithi": "તિથિ",   # Tithi
    "nakshatra": "નક્ષત્ર",   # Nakshatra
    "yoga": "યોગ",   # Yoga
    "karana": "કરણ",   # Karana
    "vara": "વાર",   # Vara
    "paksha": "પક્ષ",   # Paksha
    "masa": "માસ",   # Month
    "moon_sign": "ચંદ્ર રાશિ",   # Moon sign
    "sun_sign": "સૂર્ય રાશિ",   # Sun sign
    "panchang": "પંચાંગ",   # Panchang
}

# EN: The Sun does not both rise and set on this date at this latitude, so the vedic day cannot be
#     bounded by sunrise. The limbs below are reckoned from local midnight instead, and the sunrise-
#     based muhurtas are not defined.
NOTE_POLAR_GU = "આ તારીખે આ અક્ષાંશ પર સૂર્ય ઊગતો પણ નથી અને આથમતો પણ નથી, તેથી વૈદિક દિવસ સૂર્યોદયથી ગણી શકાતો નથી. નીચેનાં અંગો સ્થાનિક મધ્યરાત્રિથી ગણવામાં આવ્યાં છે, અને સૂર્યોદય આધારિત મુહૂર્તો લાગુ પડતાં નથી."

# EN: Abhijit muhurta is omitted on Wednesday, whose lord Mercury is held to spoil it.
NOTE_WEDNESDAY_GU = "બુધવારે અભિજિત મુહૂર્ત ગણવામાં આવતું નથી, કારણ કે વારના અધિપતિ બુધ તેને બગાડે છે એવી માન્યતા છે."


def add_gu(p: dict) -> dict:
    """add_hindi's twin for Gujarati: name_gu / paksha_gu / label_gu / notes_gu."""
    from .names_i18n import add_names
    return add_names(p, "gu")
