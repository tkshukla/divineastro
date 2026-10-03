"""Vrat and festival dates with their puja timings (DIVASTRO-111).

    observances(start, end, latitude, longitude, timezone) -> list[dict]

Every Hindu vrat and festival is "tithi X of lunar month Y", but WHICH civil
day keeps it depends on a rule about which part of the day the tithi must be
present in. The rules below are the ones Drik Panchang (default/Smarta
reckoning) follows. Every recurring vrat was checked against all of Drik's
2026 New Delhi dates (~140), and every festival rule against Drik's own dates
for 2022-2030 (to 2033 where Drik lists them) - 146 festival dates, all
matching. tests/test_festivals.py holds the tables and sources.

THE DAY'S PARTS (sunrise to sunset divided into five equal parts, as in
Hemadri/Nirnaya Sindhu: Pratah, Sangava, Madhyahna, Aparahna, Sayahna; the
night likewise into 15 muhurtas):

  udaya       the tithi prevailing at sunrise   - Amavasya, Durgashtami,
                                                  Navratri, Hanuman Jayanti
  purvahna    sunrise to midday                 - Akshaya Tritiya, Vasant Panchami
  madhyahna   3rd fifth of the day              - Ram Navami, Ganesh/Vinayaka
                                                  Chaturthi, Purnima vrat
  aparahna    4th fifth of the day              - Vijayadashami, Bhai Dooj,
                                                  Raksha Bandhan (+ Bhadra)
  sayahna     the tithi at sunset               - Chhath, Ahoi Ashtami
  pradosh     sunset + 2 muhurtas (96 min) for DATING (the DIVASTRO-90 helper);
              the Pradosh window printed is sunset + 3 night muhurtas
                                                - Pradosh vrat, Dhanteras, Diwali
  nishita     8th of the 15 night muhurtas      - Shivratri, Janmashtami
  moonrise    the tithi at moonrise             - Sankashti, Karwa Chauth
  dina        first day with the tithi between sunrise and sunset - Skanda Shashthi

Added after the Jivitputrika report (3 Oct 2026): Jivitputrika (madhyahna,
udaya3 tie - Drik 2022/2023/2024/2026/2029), the Teejs, Nag/Rishi Panchami,
Anant Chaturdashi, Pitru Paksha + Sarva Pitru Amavasya (aparahna, with Kutup/
Rohina), Vat Savitri / Vat Purnima, Ganga Dussehra (in the ADHIKA Jyeshtha when
there is one - Spec.adhika_first), Sheetala Ashtami, Gangaur, Gudi Padwa, Tulsi
Vivah, Kartik Purnima, Dev Deepawali, Narak Chaturdashi (abhyang snan), Sakat
Chauth, Mauni Amavasya, Hal Shashthi, Lohri (eve of Makar Sankranti), and the
monthly Kalashtami (pradosh) and Skanda Shashthi (dina).

TIES - the tithi touching the part on two consecutive days:
  * default: the earlier day (purva-viddha) - Pradosh, Shivratri, Purnima vrat;
  * "udaya3" (madhyahna/purvahna/aparahna festivals): a day whose whole window
    is inside the tithi wins; otherwise the later day only if the tithi runs
    for at least 3 muhurtas (a fifth of the day) after its sunrise;
  * per-festival rules (each in its own function, with the years that pin it):
    Janmashtami (Rohini at midnight), Vijayadashami (Shravana in Aparahna),
    Diwali (second evening if Amavasya lasts > 1 ghati after sunset), Raksha
    Bandhan and Holika Dahan (Bhadra).
When it touches the part on NEITHER day (a kshaya tithi), the civil day that
holds most of it. Every observance carries `rule_en`/`rule_hi` and `decided`.

EKADASHI (Smarta, Drik's default; 24/24 dates and paranas of 2026):
  * fast on the day Ekadashi prevails at sunrise; when it prevails at two
    sunrises, on the SECOND (Padmini 27 May 2026); when it touches no sunrise
    (kshaya), the day it falls in (Yogini, Devutthana 2026). Drik's extra
    "Gauna"/Vaishnava day is not shown.
  * PARANA (breaking the fast) is on the next day: it starts at sunrise or,
    if later, when Hari Vasara (the first quarter of Dwadashi) ends, and ends
    with Pratahkala (the first fifth of the day) or with Dwadashi if that is
    earlier. If Hari Vasara outlasts Pratahkala, Madhyahna is avoided and
    parana is in Aparahna. (Drik: "Parana should be done within Dwadashi...
    avoid parana during Hari Vasara... preferred time is Pratahkal... avoid
    Madhyahna".)

Anything not validated against the published dates lives in OMITTED, with the
reason, and is never returned - a wrong vrat date is worse than none.

All instants are computed with the same Swiss Ephemeris plumbing as
astro/panchang.py (visible sunrise, Lahiri, disc-centre moonrise), so a time
printed here and the in-app Panchang agree.
"""

from __future__ import annotations

import datetime as dt
import functools
from dataclasses import dataclass
from zoneinfo import ZoneInfo

from . import panchang as P

swe = P.swe

DELHI = (28.6139, 77.2090, "Asia/Kolkata")

# --------------------------------------------------------------------------
# Names
# --------------------------------------------------------------------------

# Ekadashi names by AMANTA month index (0 = Chaitra) and paksha. The Krishna
# paksha of an amanta month is the purnimanta NEXT month's Krishna paksha,
# which is where the traditional (purnimanta) names below come from:
# amanta Ashwin Krishna == purnimanta Kartika Krishna == Rama Ekadashi.
EKADASHI_NAMES = {
    (0, "Shukla"): ("Kamada Ekadashi", "कामदा एकादशी"),
    (0, "Krishna"): ("Varuthini Ekadashi", "वरूथिनी एकादशी"),
    (1, "Shukla"): ("Mohini Ekadashi", "मोहिनी एकादशी"),
    (1, "Krishna"): ("Apara Ekadashi", "अपरा एकादशी"),
    (2, "Shukla"): ("Nirjala Ekadashi", "निर्जला एकादशी"),
    (2, "Krishna"): ("Yogini Ekadashi", "योगिनी एकादशी"),
    (3, "Shukla"): ("Devshayani Ekadashi", "देवशयनी एकादशी"),
    (3, "Krishna"): ("Kamika Ekadashi", "कामिका एकादशी"),
    (4, "Shukla"): ("Shravana Putrada Ekadashi", "श्रावण पुत्रदा एकादशी"),
    (4, "Krishna"): ("Aja Ekadashi", "अजा एकादशी"),
    (5, "Shukla"): ("Parsva Ekadashi", "परिवर्तिनी एकादशी"),
    (5, "Krishna"): ("Indira Ekadashi", "इंदिरा एकादशी"),
    (6, "Shukla"): ("Papankusha Ekadashi", "पापांकुशा एकादशी"),
    (6, "Krishna"): ("Rama Ekadashi", "रमा एकादशी"),
    (7, "Shukla"): ("Devutthana Ekadashi", "देवउठनी एकादशी"),
    (7, "Krishna"): ("Utpanna Ekadashi", "उत्पन्ना एकादशी"),
    (8, "Shukla"): ("Mokshada Ekadashi", "मोक्षदा एकादशी"),
    (8, "Krishna"): ("Saphala Ekadashi", "सफला एकादशी"),
    (9, "Shukla"): ("Pausha Putrada Ekadashi", "पौष पुत्रदा एकादशी"),
    (9, "Krishna"): ("Shattila Ekadashi", "षटतिला एकादशी"),
    (10, "Shukla"): ("Jaya Ekadashi", "जया एकादशी"),
    (10, "Krishna"): ("Vijaya Ekadashi", "विजया एकादशी"),
    (11, "Shukla"): ("Amalaki Ekadashi", "आमलकी एकादशी"),
    (11, "Krishna"): ("Papmochani Ekadashi", "पापमोचनी एकादशी"),
}
ADHIKA_EKADASHI_NAMES = {
    "Shukla": ("Padmini Ekadashi", "पद्मिनी एकादशी"),
    "Krishna": ("Parama Ekadashi", "परमा एकादशी"),
}

MONTHS_HI = ["चैत्र", "वैशाख", "ज्येष्ठ", "आषाढ़", "श्रावण", "भाद्रपद", "आश्विन",
             "कार्तिक", "मार्गशीर्ष", "पौष", "माघ", "फाल्गुन"]

# Timing labels, EN / HI.
LABELS = {
    "parana": ("Parana (breaking the fast)", "पारण का समय"),
    "pradosh": ("Pradosh puja", "प्रदोष पूजा"),
    "pradosh_kaal": ("Pradosh kaal", "प्रदोष काल"),
    "moonrise": ("Moonrise", "चंद्रोदय"),
    "madhyahna": ("Madhyahna puja muhurat", "मध्याह्न पूजा मुहूर्त"),
    "nishita": ("Nishita kaal puja", "निशीथ काल पूजा"),
    "aparahna": ("Aparahna puja", "अपराह्न पूजा"),
    "vijay": ("Vijay muhurat", "विजय मुहूर्त"),
    "ghatasthapana": ("Ghatasthapana muhurat", "घटस्थापना मुहूर्त"),
    "ghatasthapana_abhijit": ("Ghatasthapana (Abhijit)", "घटस्थापना (अभिजित)"),
    "lakshmi_puja": ("Lakshmi puja muhurat", "लक्ष्मी पूजा मुहूर्त"),
    "dhanteras_puja": ("Dhanteras puja muhurat", "धनतेरस पूजा मुहूर्त"),
    "vrishabha": ("Vrishabha kaal (sthir lagna)", "वृषभ काल (स्थिर लग्न)"),
    "punya_kaal": ("Punya kaal", "पुण्य काल"),
    "maha_punya_kaal": ("Maha punya kaal", "महा पुण्य काल"),
    "sankranti": ("Sankranti moment", "संक्रांति का क्षण"),
    "holika_dahan": ("Holika Dahan muhurat", "होलिका दहन मुहूर्त"),
    "holika_after_bhadra": ("Holika Dahan after Bhadra ends", "भद्रा समाप्ति के बाद होलिका दहन"),
    "rakhi": ("Rakhi muhurat", "राखी बांधने का मुहूर्त"),
    "karwa_puja": ("Puja muhurat", "पूजा मुहूर्त"),
    "puja": ("Puja muhurat", "पूजा मुहूर्त"),
    "sandhya_arghya": ("Sandhya arghya (sunset)", "संध्या अर्घ्य (सूर्यास्त)"),
    "usha_arghya": ("Usha arghya (sunrise, next day)", "उषा अर्घ्य (सूर्योदय, अगले दिन)"),
    "pratah": ("Pratahkala muhurat", "प्रातःकाल मुहूर्त"),
    "sayahna": ("Sayahnakala muhurat", "सायंकाल मुहूर्त"),
    "tithi": ("Tithi", "तिथि"),
    "dwadashi_end": ("Dwadashi ends", "द्वादशी समाप्त"),
    "hari_vasara_end": ("Hari Vasara ends", "हरि वासर समाप्त"),
    "kutup": ("Kutup muhurat", "कुतुप मुहूर्त"),
    "rohina": ("Rohina muhurat", "रौहिण मुहूर्त"),
    "aparahna_kaal": ("Aparahna kaal", "अपराह्न काल"),
    "abhyang": ("Abhyang snan (moonrise to sunrise)", "अभ्यंग स्नान (चंद्रोदय से सूर्योदय)"),
}

# --------------------------------------------------------------------------
# Definitions
# --------------------------------------------------------------------------

# 0-based tithi index: Shukla Pratipada 0 .. Purnima 14, Krishna Pratipada 15
# .. Amavasya 29.
S, K = 0, 15


@dataclass(frozen=True)
class Spec:
    key: str
    name_en: str
    name_hi: str
    tithi: int                       # 0..29
    month: int | None                # amanta month index, None = every month
    rule: str                        # udaya / madhyahna / aparahna / pradosh / nishita / moonrise
    major: bool = False              # gets its own /tyohar page
    slug: str | None = None
    tie: str = "first"               # which day when the tithi touches the part on two days
    # Kept in the ADHIKA month when its month is doubled (and then not in the
    # nija month) - Ganga Dussehra 2026 (Drik: 25 May, adhika Jyeshtha).
    adhika_first: bool = False


RECURRING = [
    Spec("pradosh", "Pradosh Vrat", "प्रदोष व्रत", S + 12, None, "pradosh"),
    Spec("pradosh", "Pradosh Vrat", "प्रदोष व्रत", K + 12, None, "pradosh"),
    Spec("sankashti", "Sankashti Chaturthi", "संकष्टी चतुर्थी", K + 3, None, "moonrise"),
    Spec("vinayaka", "Vinayaka Chaturthi", "विनायक चतुर्थी", S + 3, None, "madhyahna",
         tie="udaya3"),
    # Drik's "Purnima Vrat" is the day Purnima touches Madhyahna, which is
    # often the day BEFORE the sunrise ("<month> Purnima") date - checked on
    # all 13 dates of 2026.
    Spec("purnima", "Purnima Vrat", "पूर्णिमा व्रत", S + 14, None, "madhyahna"),
    Spec("amavasya", "Amavasya", "अमावस्या", K + 14, None, "udaya"),
    Spec("masik_shivratri", "Masik Shivratri", "मासिक शिवरात्रि", K + 13, None, "nishita"),
    Spec("durgashtami", "Masik Durgashtami", "मासिक दुर्गाष्टमी", S + 7, None, "udaya"),
    # Kalashtami: Krishna Ashtami prevailing in the evening (Pradosh) - all
    # 13 Drik dates of 2026 (incl. 10 Apr and 1 Dec, where Nishita would
    # give the day before).
    Spec("kalashtami", "Kalashtami", "कालाष्टमी", K + 7, None, "pradosh"),
    # Skanda Shashthi: the first day on which Shashthi is present between
    # sunrise and sunset (Panchami-yukta Shashthi preferred) - all 12 Drik
    # dates of 2026 (Sayahna fails 24 Mar, Madhyahna fails 19 Jun).
    Spec("skanda_shashthi", "Skanda Shashthi", "स्कंद षष्ठी", S + 5, None, "dina"),
]

FESTIVALS = [
    Spec("maha_shivratri", "Maha Shivratri", "महाशिवरात्रि", K + 13, 10, "nishita", True,
         "maha-shivratri"),
    Spec("holika_dahan", "Holika Dahan", "होलिका दहन", S + 14, 11, "pradosh", True,
         "holika-dahan"),
    Spec("ram_navami", "Ram Navami", "राम नवमी", S + 8, 0, "madhyahna", True, "ram-navami",
         tie="udaya3"),
    Spec("hanuman_jayanti", "Hanuman Jayanti", "हनुमान जयंती", S + 14, 0, "udaya", True,
         "hanuman-jayanti"),
    Spec("akshaya_tritiya", "Akshaya Tritiya", "अक्षय तृतीया", S + 2, 1, "purvahna", True,
         "akshaya-tritiya", tie="udaya3"),
    Spec("raksha_bandhan", "Raksha Bandhan", "रक्षा बंधन", S + 14, 4, "aparahna", True,
         "raksha-bandhan"),
    Spec("janmashtami", "Krishna Janmashtami", "कृष्ण जन्माष्टमी", K + 7, 4, "nishita", True,
         "janmashtami"),
    Spec("ganesh_chaturthi", "Ganesh Chaturthi", "गणेश चतुर्थी", S + 3, 5, "madhyahna", True,
         "ganesh-chaturthi", tie="udaya3"),
    Spec("chaitra_navratri", "Chaitra Navratri begins", "चैत्र नवरात्रि प्रारंभ", S + 0, 0,
         "udaya", True, "chaitra-navratri"),
    Spec("navratri", "Sharad Navratri begins", "शारदीय नवरात्रि प्रारंभ", S + 0, 6, "udaya",
         True, "navratri"),
    Spec("dussehra", "Dussehra (Vijayadashami)", "दशहरा (विजयादशमी)", S + 9, 6, "aparahna",
         True, "dussehra", tie="udaya3"),
    Spec("karwa_chauth", "Karwa Chauth", "करवा चौथ", K + 3, 6, "moonrise", True,
         "karwa-chauth"),
    # Ahoi Ashtami: Ashtami at sunset - all nine Drik dates 2022-2030.
    Spec("ahoi_ashtami", "Ahoi Ashtami", "अहोई अष्टमी", K + 7, 6, "sayahna", True,
         "ahoi-ashtami"),
    Spec("dhanteras", "Dhanteras", "धनतेरस", K + 12, 6, "pradosh", True, "dhanteras"),
    Spec("diwali", "Diwali (Lakshmi Puja)", "दीपावली (लक्ष्मी पूजा)", K + 14, 6, "pradosh",
         True, "diwali"),
    Spec("govardhan", "Govardhan Puja", "गोवर्धन पूजा", S + 0, 7, "pratah", True, "govardhan-puja"),
    Spec("bhai_dooj", "Bhai Dooj", "भाई दूज", S + 1, 7, "aparahna", True, "bhai-dooj",
         tie="udaya3"),
    Spec("chhath", "Chhath Puja", "छठ पूजा", S + 5, 7, "sayahna", True, "chhath-puja"),
    Spec("vasant_panchami", "Vasant Panchami", "वसंत पंचमी", S + 4, 10, "purvahna", True,
         "vasant-panchami", tie="udaya3"),
    Spec("guru_purnima", "Guru Purnima", "गुरु पूर्णिमा", S + 14, 3, "udaya", True,
         "guru-purnima"),
    Spec("sharad_purnima", "Sharad Purnima", "शरद पूर्णिमा", S + 14, 6, "moonrise", True,
         "sharad-purnima"),
    # ---- Added after the Jivitputrika report (3 Oct 2026). Each rule is the
    # one that reproduces Drik Panchang's New Delhi dates in the years where
    # the candidate rules disagree; tests/test_festivals.py lists them.
    # Sakat Chauth = the Sankashti of (purnimanta) Magha: Chaturthi at moonrise.
    Spec("sakat_chauth", "Sakat Chauth", "सकट चौथ", K + 3, 9, "moonrise", True, "sakat-chauth"),
    # Magha (purnimanta) Amavasya at sunrise, like every Amavasya snan day.
    Spec("mauni_amavasya", "Mauni Amavasya", "मौनी अमावस्या", K + 14, 9, "udaya", True,
         "mauni-amavasya"),
    # Chaitra (purnimanta) Krishna Ashtami at sunrise (2024: 2 Apr; 2027: 30 Mar).
    Spec("sheetala_ashtami", "Sheetala Ashtami (Basoda)", "शीतला अष्टमी (बसौड़ा)", K + 7, 11,
         "udaya", True, "sheetala-ashtami"),
    # Chaitra Shukla Pratipada at sunrise - the Chaitra Navratri rule.
    Spec("gudi_padwa", "Gudi Padwa / Ugadi", "गुड़ी पड़वा / उगादी", S + 0, 0, "udaya", True,
         "gudi-padwa"),
    Spec("gangaur", "Gangaur", "गणगौर", S + 2, 0, "udaya", True, "gangaur"),
    # Jyeshtha (purnimanta) Amavasya touching Madhyahna, earlier day on a tie
    # (2022: 30 May; 2025: 26 May, not the sunrise day 27 May).
    Spec("vat_savitri", "Vat Savitri Vrat", "वट सावित्री व्रत", K + 14, 1, "madhyahna", True,
         "vat-savitri"),
    # Jyeshtha Shukla Dashami in the forenoon (2022: 9 Jun; 2023: 30 May), in
    # the adhika month when Jyeshtha is doubled (2026: 25 May).
    Spec("ganga_dussehra", "Ganga Dussehra", "गंगा दशहरा", S + 9, 2, "purvahna", True,
         "ganga-dussehra", tie="udaya3", adhika_first=True),
    # Jyeshtha Purnima, the Purnima-vrat rule (Madhyahna, earlier day):
    # 2023: 3 Jun; 2025: 10 Jun.
    Spec("vat_purnima", "Vat Purnima Vrat", "वट पूर्णिमा व्रत", S + 14, 2, "madhyahna", True,
         "vat-purnima"),
    Spec("hariyali_teej", "Hariyali Teej", "हरियाली तीज", S + 2, 4, "udaya", True,
         "hariyali-teej"),
    Spec("nag_panchami", "Nag Panchami", "नाग पंचमी", S + 4, 4, "udaya", True, "nag-panchami"),
    # Bhadrapada (purnimanta) Krishna Tritiya at sunrise (2025: 12 Aug; 2026: 31 Aug).
    Spec("kajari_teej", "Kajari Teej", "कजरी तीज", K + 2, 4, "udaya", True, "kajari-teej"),
    Spec("hal_shashthi", "Hal Shashthi (Lalahi Chhath)", "हल षष्ठी (ललही छठ)", K + 5, 4, "udaya",
         True, "hal-shashthi"),
    # Tritiya at sunrise, however briefly (2029: 4 minutes - Drik still 11 Sep).
    Spec("hartalika_teej", "Hartalika Teej", "हरतालिका तीज", S + 2, 5, "udaya", True,
         "hartalika-teej"),
    # Panchami at Madhyahna, earlier day (2027: 4 Sep, Panchami from 12:25).
    Spec("rishi_panchami", "Rishi Panchami", "ऋषि पंचमी", S + 4, 5, "madhyahna", True,
         "rishi-panchami"),
    Spec("anant_chaturdashi", "Anant Chaturdashi", "अनंत चतुर्दशी", S + 13, 5, "udaya", True,
         "anant-chaturdashi"),
    # Shraddha days: the tithi in Aparahna (Drik's shraddha pages).
    Spec("pitru_paksha", "Pitru Paksha begins (Pratipada Shraddha)",
         "पितृ पक्ष आरंभ (प्रतिपदा श्राद्ध)", K + 0, 5, "aparahna", True, "pitru-paksha"),
    # Jivitputrika: Ashwin (purnimanta) Krishna Ashtami at Madhyahna, with the
    # udaya3 tie: 2022 18 Sep (sunrise day), 2023 6 Oct (NOT the sunrise day 7
    # Oct, Ashtami over by 8:08 AM), 2024 25 Sep, 2026 3 Oct, 2029 1 Oct.
    Spec("jivitputrika", "Jivitputrika Vrat (Jitiya)", "जीवित्पुत्रिका व्रत (जितिया)", K + 7, 5,
         "madhyahna", True, "jivitputrika", tie="udaya3"),
    Spec("sarva_pitru_amavasya", "Sarva Pitru Amavasya (Mahalaya)",
         "सर्व पितृ अमावस्या (महालया)", K + 14, 5, "aparahna", True, "sarva-pitru-amavasya"),
    # Abhyang snan: Chaturdashi at (pre-dawn moonrise and) sunrise.
    Spec("narak_chaturdashi", "Narak Chaturdashi (Roop Chaudas)", "नरक चतुर्दशी (रूप चौदस)",
         K + 13, 6, "udaya", True, "narak-chaturdashi"),
    # Kartika Shukla Dwadashi at sunrise (2024: 13 Nov; 2027: 11 Nov).
    Spec("tulsi_vivah", "Tulsi Vivah", "तुलसी विवाह", S + 11, 7, "udaya", True, "tulsi-vivah"),
    # Snan-daan day: Purnima at sunrise (2027: 14 Nov, the vrat being 13 Nov).
    Spec("kartik_purnima", "Kartik Purnima", "कार्तिक पूर्णिमा", S + 14, 7, "udaya", True,
         "kartik-purnima"),
    # Purnima in Pradosh (2023: 26 Nov; 2027: 13 Nov).
    Spec("dev_deepawali", "Dev Deepawali", "देव दीपावली", S + 14, 7, "pradosh", True,
         "dev-deepawali"),
]

# Recurring / festival keys switched off because they could not be validated
# or disagree with the published dates. Never returned. key -> reason.
OMITTED: dict[str, str] = {
    "holi": (
        "Rangwali Holi's date could not be validated as a rule: Drik gives 4 Mar 2026 (the "
        "day after Holika Dahan), but in other years (e.g. 2027, when Purnima runs into the "
        "afternoon after Holika Dahan) the colour day and the Pratipada at sunrise can fall "
        "on different days, and Drik's multi-year Holi list could not be retrieved "
        "(rate-limited). Holika Dahan itself is validated and shown."),
    "santan_saptami": (
        "Santan Saptami (Bhadrapada Shukla Saptami): Drik's date could not be retrieved, and "
        "the candidate rules disagree in 2026 (Saptami at sunrise -> 18 Sep, at Madhyahna -> "
        "17 Sep) and 2027 (7 vs 6 Sep). Not computed."),
}
# Considered for DIVASTRO-111's audit and deliberately NOT modelled (no key is
# ever produced for them; listed so the next audit does not redo the work):
#   Skanda Shashthi/Kalashtami/Nirjala Ekadashi/Basant (Vasant) Panchami are in
#   RECURRING/FESTIVALS/EKADASHI_NAMES; "Choti Diwali" is Narak Chaturdashi
#   (Drik shows both on Diwali day itself in 2026, so no separate entry).
# Individual timings switched off: (observance key, timing key) -> reason.
OMITTED_TIMINGS: dict[tuple[str, str], str] = {
    ("holika_dahan", "holika_after_bhadra"): (
        "the 'after Bhadra ends, same night' moment (2024/2025-type years) matches Drik's "
        "start time from memory only and could not be re-checked; the date is validated."),
    ("makar_sankranti", "sankranti"): (
        "the sankranti moment disagrees between sources (Drik 3:13 PM, Prokerala "
        "3:04 PM, ours 3:07 PM for 14 Jan 2026); the date agrees everywhere."),
    ("makar_sankranti", "punya_kaal"): "starts at the sankranti moment - see above.",
    ("chaitra_navratri", "ghatasthapana"): (
        "Drik shifts Chaitra ghatasthapana to the Pratipada start and the end of a "
        "dual-sign lagna (2026: 6:52-7:43 AM); the lagna rule is not modelled. The "
        "Abhijit alternative matches and is shown."),
    ("jivitputrika", "parana"): (
        "Drik prints no parana time for Jivitputrika (only the Ashtami span); news sources "
        "give 'next morning after sunrise' with city-dependent clock times that do not "
        "agree. The page says parana is the next morning, without a time."),
}


# --------------------------------------------------------------------------
# Astronomy helpers
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Day:
    date: dt.date
    sunrise: float
    sunset: float
    next_sunrise: float

    @property
    def day_len(self) -> float:
        return self.sunset - self.sunrise

    @property
    def night_len(self) -> float:
        return self.next_sunrise - self.sunset

    def part(self, n: int) -> tuple[float, float]:
        """n-th (1..5) fifth of daylight."""
        f = self.day_len / 5.0
        return self.sunrise + (n - 1) * f, self.sunrise + n * f

    def day_muhurta(self, n: int) -> tuple[float, float]:
        f = self.day_len / 15.0
        return self.sunrise + (n - 1) * f, self.sunrise + n * f

    def night_muhurta(self, n: int) -> tuple[float, float]:
        f = self.night_len / 15.0
        return self.sunset + (n - 1) * f, self.sunset + n * f


def _tithi_span(jd: float) -> tuple[int, float, float]:
    angle = P._elongation(jd)
    index = int(angle // 12.0) % 30
    into = angle - index * 12.0
    return index, P._retreat(P._elongation, jd, into), P._advance(P._elongation, jd, 12.0 - into)


@functools.lru_cache(maxsize=8192)
def _day(date: dt.date, lat: float, lon: float, tz: str) -> Day | None:
    P._ephemeris()
    z = ZoneInfo(tz)
    jd0 = P._to_jd(dt.datetime(date.year, date.month, date.day, tzinfo=z))
    rise, set_, nxt = P._sun_jds(jd0, (lon, lat, 0.0))
    if not (rise and set_ and nxt):
        return None
    return Day(date, rise, set_, nxt)


def _moonrise_evening(d: Day, lat: float, lon: float) -> float | None:
    """The first moonrise after noon (so the evening/night rise for a
    Chaturthi or Purnima evening), within the vedic day."""
    noon = (d.sunrise + d.sunset) / 2.0
    return P._rise_or_set(noon, swe.MOON, (lon, lat, 0.0), True, d.next_sunrise - noon)


def _sidereal_asc(jd: float, lat: float, lon: float) -> float:
    swe.set_sid_mode(P.get_ayanamsa(P.DEFAULT_AYANAMSA).swe_constant)
    return swe.houses_ex(jd, lat, lon, b"W", swe.FLG_SIDEREAL)[1][0] % 360.0


def _lagna_window(sign: int, jd_from: float, jd_to: float, lat: float, lon: float
                  ) -> tuple[float, float] | None:
    """The first interval in [jd_from, jd_to) during which sidereal `sign`
    (0 = Mesha) is rising."""
    step = 5.0 / 1440.0

    def inside(jd: float) -> bool:
        return int(_sidereal_asc(jd, lat, lon) // 30) == sign

    def edge(lo: float, hi: float, lo_in: bool) -> float:
        while hi - lo > 1e-5:
            mid = (lo + hi) / 2
            if inside(mid) == lo_in:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2

    jd, prev = jd_from, inside(jd_from)
    start = jd_from if prev else None
    while jd < jd_to:
        nxt = min(jd + step, jd_to)
        now = inside(nxt)
        if now and not prev:
            start = edge(jd, nxt, False)
        if prev and not now and start is not None:
            return start, edge(jd, nxt, True)
        jd, prev = nxt, now
    return (start, jd_to) if start is not None else None


def _sun_ingress(sign: int, jd_guess: float) -> float:
    """When the Sun enters sidereal `sign` (0 = Mesha), searching from 20 days
    before `jd_guess`."""
    target = sign * 30.0

    def gained(jd: float) -> float:
        return (P._sidereal(jd, swe.SUN, P.DEFAULT_AYANAMSA) - target + 180.0) % 360.0 - 180.0

    lo, hi = jd_guess - 20.0, jd_guess + 20.0
    while hi - lo > 1e-6:
        mid = (lo + hi) / 2
        if gained(mid) < 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def _bhadra_spans(jd_from: float, jd_to: float) -> list[tuple[float, float]]:
    """Vishti karana (Bhadra) spans overlapping the interval."""
    out = []
    for index, s, e in P._limb_run(P._elongation, 60, jd_from, jd_to, max_entries=12):
        if 1 <= index <= 56 and index % 7 == 0:
            out.append((s, e))
    return out


def _overlap(a: tuple[float, float], b: tuple[float, float]) -> float:
    return max(0.0, min(a[1], b[1]) - max(a[0], b[0]))


def _window(d: Day, rule: str, lat: float, lon: float) -> tuple[float, float] | None:
    """The part of day `d` a rule tests the tithi against (point rules give a
    zero-length window)."""
    if rule == "udaya":
        return d.sunrise, d.sunrise
    if rule == "pratah":
        return d.part(1)
    if rule == "purvahna":                       # first half of daylight
        return d.sunrise, (d.sunrise + d.sunset) / 2
    if rule == "madhyahna":
        return d.part(3)
    if rule == "aparahna":
        return d.part(4)
    if rule == "dina":                           # sunrise to sunset
        return d.sunrise, d.sunset
    if rule == "sayahna":
        return d.sunset, d.sunset
    if rule == "pradosh":
        return d.sunset, d.sunset + 96.0 / 1440.0
    if rule == "nishita":
        return d.night_muhurta(8)
    if rule == "moonrise":
        m = _moonrise_evening(d, lat, lon)
        return (m, m) if m else None
    raise ValueError(rule)


# --------------------------------------------------------------------------
# Choosing the day
# --------------------------------------------------------------------------

def _candidate_days(start: float, end: float, lat: float, lon: float, tz: str
                    ) -> list[Day]:
    z = ZoneInfo(tz)
    first = P._from_jd(start, z).date() - dt.timedelta(days=1)
    last = P._from_jd(end, z).date()
    out = []
    d = first
    while d <= last:
        day = _day(d, lat, lon, tz)
        if day:
            out.append(day)
        d += dt.timedelta(days=1)
    return out


def _choose_day(span: tuple[float, float], rule: str, tie: str, lat: float, lon: float,
                tz: str) -> tuple[Day, str] | None:
    """(the civil day that keeps a tithi occurrence, how it was decided)."""
    start, end = span
    days = _candidate_days(start, end, lat, lon, tz)
    hits = []
    for d in days:
        w = _window(d, rule, lat, lon)
        if w is None:
            continue
        if w[0] == w[1]:
            if start <= w[0] < end:
                hits.append((d, 1.0))
        else:
            ov = _overlap(w, span)
            if ov > 0:
                hits.append((d, ov / (w[1] - w[0])))
    if hits:
        if len(hits) == 1:
            return hits[0][0], "single"
        if tie == "last":
            return hits[-1][0], "two-days-later"
        if tie == "udaya3":
            # A day whose whole window is in the tithi wins outright (Ganesh
            # Chaturthi 2023 and 2033, Akshaya Tritiya 2022). Otherwise the
            # later day only if the tithi still runs for 3 muhurtas (a fifth of
            # the day) after its sunrise, else the earlier day (Akshaya Tritiya
            # 2023/2026 vs 2027, Ram Navami 2029).
            full = [d for d, cov in hits if cov >= 0.999]
            if full:
                return full[0], "window-fully-covered"
            d2 = hits[-1][0]
            if span[0] <= d2.sunrise and span[1] - d2.sunrise >= d2.day_len / 5.0:
                return d2, "two-days-later-tithi-3-muhurtas-after-sunrise"
            return hits[0][0], "two-days-earlier"
        if tie == "most":
            best = max(hits, key=lambda h: h[1])
            return best[0], "two-days-greater-coverage"
        return hits[0][0], "two-days-earlier"
    # The tithi touches the part on no day (a short "kshaya" tithi): keep it
    # on the civil day (sunrise to sunrise) that contains most of it.
    best = max(days, key=lambda d: _overlap((d.sunrise, d.next_sunrise), span), default=None)
    return (best, "kshaya") if best else None


# --------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------

def _iso(jd: float | None, tz: str) -> str | None:
    return P._from_jd(jd, ZoneInfo(tz)).isoformat() if jd else None


def _timing(key: str, tz: str, start: float | None = None, end: float | None = None,
            at: float | None = None) -> dict:
    en, hi = LABELS[key]
    t = {"key": key, "label_en": en, "label_hi": hi}
    if at is not None:
        t["at"] = _iso(at, tz)
    else:
        t["start"], t["end"] = _iso(start, tz), _iso(end, tz)
    return t


def _tithi_info(index: int, start: float, end: float, tz: str) -> dict:
    name, paksha, number = P._tithi_label(index)
    return {"name": name, "paksha": paksha, "number": number,
            "start": _iso(start, tz), "end": _iso(end, tz)}


RULE_TEXT = {
    "udaya": ("tithi prevailing at sunrise", "सूर्योदय के समय की तिथि"),
    "pratah": ("tithi prevailing in Pratahkala (first fifth of the day)",
               "प्रातःकाल में व्याप्त तिथि"),
    "purvahna": ("tithi prevailing in the forenoon (purvahna)", "पूर्वाह्न व्यापिनी तिथि"),
    "madhyahna": ("tithi prevailing at Madhyahna (midday fifth of the day)",
                  "मध्याह्न व्यापिनी तिथि"),
    "aparahna": ("tithi prevailing at Aparahna (fourth fifth of the day)",
                 "अपराह्न व्यापिनी तिथि"),
    "dina": ("first day on which the tithi is present between sunrise and sunset",
             "पहला दिन जब सूर्योदय से सूर्यास्त के बीच तिथि हो"),
    "sayahna": ("tithi prevailing at sunset", "सूर्यास्त के समय की तिथि"),
    "pradosh": ("tithi prevailing in Pradosh kaal (after sunset)", "प्रदोष व्यापिनी तिथि"),
    "nishita": ("tithi prevailing at Nishita kaal (midnight)", "निशीथ व्यापिनी तिथि"),
    "moonrise": ("tithi prevailing at moonrise", "चंद्रोदय व्यापिनी तिथि"),
}


def _tithi_words(index: int, month: dict, spec: Spec, lang: str) -> str:
    """'Ashwin (amanta) Krishna Amavasya: ' - what the rule is applied to."""
    from .muhurat import TITHI_HI
    name, paksha, _n = P._tithi_label(index)
    if lang == "hi":
        head = f"{MONTHS_HI[month['index']]} (अमांत) " if spec.month is not None else ""
        return f"{head}{'शुक्ल' if paksha == 'Shukla' else 'कृष्ण'} {TITHI_HI.get(name, name)}: "
    head = f"{P.LUNAR_MONTHS[month['index']]} (amanta) " if spec.month is not None else ""
    return f"{head}{paksha} {name}: "


def _base(spec: Spec, d: Day, how: str, index: int, span: tuple[float, float], tz: str,
          month: dict) -> dict:
    return {
        "key": spec.key, "name_en": spec.name_en, "name_hi": spec.name_hi,
        "date": d.date.isoformat(), "major": spec.major, "slug": spec.slug,
        "kind": "festival" if spec.major else "vrat",
        "rule": spec.rule,
        "rule_en": _tithi_words(index, month, spec, "en") + RULE_TEXT[spec.rule][0],
        "rule_hi": _tithi_words(index, month, spec, "hi") + RULE_TEXT[spec.rule][1],
        "decided": how,
        "month": {"name": P.LUNAR_MONTHS[month["index"]], "name_hi": MONTHS_HI[month["index"]],
                  "adhika": month["adhika"]},
        "tithi": _tithi_info(index, span[0], span[1], tz),
        "timings": [],
    }


def _ekadashi(index: int, span: tuple[float, float], lat: float, lon: float, tz: str,
              month: dict) -> dict | None:
    start, end = span
    days = _candidate_days(start, end, lat, lon, tz)
    at_sunrise = [d for d in days if start <= d.sunrise < end]
    if at_sunrise:
        # Ekadashi at two sunrises (vriddhi): the fast is on the second day.
        fast = at_sunrise[-1]
        how = "two-sunrises-second-day" if len(at_sunrise) > 1 else "single"
    else:
        fast = max(days, key=lambda d: _overlap((d.sunrise, d.next_sunrise), span))
        how = "kshaya"
    paksha = "Shukla" if index < 15 else "Krishna"
    if month["adhika"]:
        en, hi = ADHIKA_EKADASHI_NAMES[paksha]
    else:
        en, hi = EKADASHI_NAMES[(month["index"], paksha)]
    spec = Spec("ekadashi", en, hi, index, None, "udaya")
    o = _base(spec, fast, how, index, span, tz, month)
    o["name_en"], o["name_hi"] = en, hi
    o["rule_en"] = ("Smarta: Ekadashi prevailing at sunrise (second day if at two sunrises); "
                    "parana next day after sunrise and after Hari Vasara, within Pratahkala "
                    "and before Dwadashi ends")
    o["rule_hi"] = ("स्मार्त: सूर्योदय के समय एकादशी (दो सूर्योदय पर हो तो दूसरा दिन); पारण अगले दिन "
                    "सूर्योदय व हरि वासर के बाद, प्रातःकाल में और द्वादशी समाप्त होने से पहले")
    o["key"] = "ekadashi"
    o["slug"] = None
    if (month["index"], paksha) == (7, "Shukla") and not month["adhika"]:
        o["major"], o["slug"], o["kind"] = True, "devuthani-ekadashi", "festival"
    # Parana, next day.
    nxt = _day(fast.date + dt.timedelta(days=1), lat, lon, tz)
    _di, d_start, d_end = _tithi_span(end + 1e-5)       # Dwadashi follows Ekadashi
    hari_end = d_start + (d_end - d_start) / 4.0
    if nxt:
        p_start = max(nxt.sunrise, hari_end)
        pratah_end = nxt.part(1)[1]
        if p_start < pratah_end:
            p_end = min(pratah_end, d_end) if d_end > p_start else pratah_end
        else:
            # Hari Vasara runs past Pratahkala. Madhyahna is avoided for parana,
            # so it moves to Aparahna (Drik: Yogini, Shravana Putrada and
            # Devutthana 2026).
            p_start, p_end = nxt.part(4)
            if p_start < d_end < p_end:
                p_end = d_end
        o["parana"] = {"date": nxt.date.isoformat(), "start": _iso(p_start, tz),
                       "end": _iso(p_end, tz),
                       "dwadashi_end": _iso(d_end, tz),
                       "hari_vasara_end": _iso(hari_end, tz) if hari_end > nxt.sunrise else None,
                       "dwadashi_over_before_sunrise": d_end <= nxt.sunrise}
        o["timings"].append(dict(_timing("parana", tz, p_start, p_end), date=nxt.date.isoformat()))
    return o


def _add_timings(o: dict, spec: Spec, d: Day, span: tuple[float, float], lat: float,
                 lon: float, tz: str) -> None:
    t = o["timings"]
    key = spec.key
    if spec.rule == "moonrise" or key in ("karwa_chauth", "ahoi_ashtami"):
        m = _moonrise_evening(d, lat, lon)
        if m:
            t.append(_timing("moonrise", tz, at=m))
    if key == "pradosh":
        # Sunset + 3 night muhurtas, cut to the Trayodashi (as Drik prints it).
        w = _clip((d.sunset, d.sunset + 3 * d.night_len / 15.0), span)
        if w:
            t.append(_timing("pradosh", tz, *w))
    if key in ("vinayaka", "ganesh_chaturthi"):
        w = _clip(d.part(3), span)
        if w:
            t.append(_timing("madhyahna", tz, *w))
    if key == "ram_navami":                     # Drik prints the whole Madhyahna here
        t.append(_timing("madhyahna", tz, *d.part(3)))
    if key in ("masik_shivratri", "maha_shivratri", "janmashtami"):
        t.append(_timing("nishita", tz, *d.night_muhurta(8)))
    if key == "dussehra":
        t.append(_timing("vijay", tz, *d.day_muhurta(11)))
        t.append(_timing("aparahna", tz, *d.part(4)))
    if key == "bhai_dooj":
        t.append(_timing("aparahna", tz, *d.part(4)))
    if key in ("navratri", "chaitra_navratri"):
        # First third of the day, inside the Pratipada.
        w = _clip((d.sunrise, d.sunrise + d.day_len / 3.0), span)
        if w:
            t.append(_timing("ghatasthapana", tz, *w))
        t.append(_timing("ghatasthapana_abhijit", tz, *d.day_muhurta(8)))
    if key in ("diwali", "dhanteras"):
        # Puja muhurat = Pradosh kaal AND the fixed Vrishabha (Taurus) lagna
        # AND the tithi - Drik's rule, matched to the minute for 2026 and 2027.
        pr = (d.sunset, d.sunset + 3 * d.night_len / 15.0)
        vr = _lagna_window(1, d.sunset - 2 / 24, d.sunset + 6 / 24, lat, lon)
        if vr:
            s, e = max(pr[0], vr[0], span[0]), min(pr[1], vr[1], span[1])
            if e > s:
                t.append(_timing("lakshmi_puja" if key == "diwali" else "dhanteras_puja",
                                 tz, s, e))
        t.append(_timing("pradosh_kaal", tz, *pr))
        if vr:
            t.append(_timing("vrishabha", tz, *vr))
    if key in ("akshaya_tritiya", "vasant_panchami"):
        # Purvahna (sunrise to midday), inside the tithi.
        w = _clip((d.sunrise, (d.sunrise + d.sunset) / 2), span)
        if w:
            t.append(_timing("puja", tz, *w))
    if key == "govardhan":
        for k, part in (("pratah", 1), ("sayahna", 5)):
            w = _clip(d.part(part), span)
            if w:
                t.append(_timing(k, tz, *w))
    if key == "chhath":
        t.append(_timing("sandhya_arghya", tz, at=d.sunset))
        t.append(_timing("usha_arghya", tz, at=d.next_sunrise))
    if key in ("karwa_chauth", "ahoi_ashtami"):
        # Sunset + a tenth of the night (Drik 2026: Karwa Chauth 29 Oct
        # 5:38-6:56 PM, Ahoi Ashtami 1 Nov 5:36-6:54 PM).
        t.insert(0, _timing("karwa_puja", tz, d.sunset, d.sunset + d.night_len / 10.0))
    if key == "rishi_panchami":                 # Drik 2026 11:02-1:30 PM, 2027 12:25-1:36 PM
        w = _clip(d.part(3), span)
        if w:
            t.append(_timing("madhyahna", tz, *w))
    if key == "hartalika_teej":                 # Pratahkala in the Tritiya (2029: 4 minutes)
        w = _clip(d.part(1), span)
        if w:
            t.append(_timing("pratah", tz, *w))
    if key == "anant_chaturdashi":              # sunrise to the end of Chaturdashi
        w = _clip((d.sunrise, d.next_sunrise), span)
        if w:
            t.append(_timing("puja", tz, *w))
    if key == "sheetala_ashtami":               # sunrise to sunset
        t.append(_timing("puja", tz, d.sunrise, d.sunset))
    if key in ("pitru_paksha", "sarva_pitru_amavasya"):
        # Shraddha: Kutup and Rohina are the 8th and 9th day muhurtas, then
        # Aparahna (the 4th fifth of the day).
        t.append(_timing("kutup", tz, *d.day_muhurta(8)))
        t.append(_timing("rohina", tz, *d.day_muhurta(9)))
        t.append(_timing("aparahna_kaal", tz, *d.part(4)))
    if key == "narak_chaturdashi":
        # Abhyang snan: from moonrise (or the start of Chaturdashi) to sunrise.
        m = P._rise_or_set(d.sunrise - 0.25, swe.MOON, (lon, lat, 0.0), True, 0.25)
        if m and m < d.sunrise:
            s = max(m, span[0])
            if s < d.sunrise:
                t.append(_timing("abhyang", tz, s, d.sunrise))
    if key == "dev_deepawali":                  # sunset + 3 night muhurtas
        t.append(_timing("pradosh_kaal", tz, d.sunset, d.sunset + 3 * d.night_len / 15.0))



def _clip(w: tuple[float, float], span: tuple[float, float]) -> tuple[float, float] | None:
    s, e = max(w[0], span[0]), min(w[1], span[1])
    return (s, e) if e > s else None


def _bhadra_free(w: tuple[float, float], span: tuple[float, float]) -> tuple[float, float] | None:
    """The part of window `w` inside the tithi and outside Bhadra (largest piece)."""
    s, e = max(w[0], span[0]), min(w[1], span[1])
    if e <= s:
        return None
    pieces = [(s, e)]
    for bs, be in _bhadra_spans(s - 1.0, e):
        nxt = []
        for ps, pe in pieces:
            if be <= ps or bs >= pe:
                nxt.append((ps, pe))
                continue
            if bs > ps:
                nxt.append((ps, bs))
            if be < pe:
                nxt.append((be, pe))
        pieces = nxt
    pieces = [p for p in pieces if p[1] - p[0] > 1.0 / 1440.0]
    return max(pieces, key=lambda p: p[1] - p[0]) if pieces else None


def _is_rohini(jd: float) -> bool:
    return int(P._sidereal(jd, swe.MOON, P.DEFAULT_AYANAMSA) // (360.0 / 27.0)) == 3


def _janmashtami(span: tuple[float, float], lat: float, lon: float, tz: str
                 ) -> tuple[Day, str] | None:
    """Krishna Janmashtami (Smarta), Drik's rule: Ashtami at Nishita (midnight),
    except that a day on which Ashtami is present (at Nishita or at sunrise)
    AND Rohini nakshatra holds at Nishita - "Jayanti" - wins, the later one if
    both nights qualify. Checked on Drik's dates 2022-2033. (2027: Ashtami
    is at the 24 Aug midnight, but Rohini is at the 25 Aug midnight with
    Ashtami at its sunrise -> 25 Aug, as Drik prints.)"""
    days = _candidate_days(span[0], span[1], lat, lon, tz)
    jayanti = []
    for d in days:
        n = d.night_muhurta(8)
        has_ashtami = _overlap(n, span) > 0 or span[0] <= d.sunrise < span[1]
        if has_ashtami and _is_rohini((n[0] + n[1]) / 2):
            jayanti.append(d)
    if jayanti:
        # On both nights: the later, with Ashtami at its sunrise (2032).
        return jayanti[-1], "jayanti-rohini-at-nishita"
    return _choose_day(span, "nishita", "first", lat, lon, tz)


def _nakshatra_in(index: int, w: tuple[float, float]) -> bool:
    """Whether the Moon is in nakshatra `index` at any point of window `w`."""
    span = 360.0 / 27.0
    a = P._sidereal(w[0], swe.MOON, P.DEFAULT_AYANAMSA) // span
    b = P._sidereal(w[1], swe.MOON, P.DEFAULT_AYANAMSA) // span
    return index in (int(a) % 27, int(b) % 27)


def _diwali(span: tuple[float, float], lat: float, lon: float, tz: str
            ) -> tuple[Day, str] | None:
    """Diwali / Lakshmi Puja: Amavasya in Pradosh (DIVASTRO-90's rule, earlier
    day on a tie) - except that when Amavasya touches Pradosh on both evenings
    and lasts more than one ghati (24 min) past the second sunset, the second
    evening (Drik: 1 Nov 2024, Amavasya till 6:16 PM). Checked 2023-2033."""
    chosen = _choose_day(span, "pradosh", "first", lat, lon, tz)
    if chosen is None or chosen[1] != "two-days-earlier":
        return chosen
    d2 = _day(chosen[0].date + dt.timedelta(days=1), lat, lon, tz)
    if d2 and span[0] <= d2.sunrise and span[1] - d2.sunset > 24.0 / 1440.0:
        return d2, "two-days-second-amavasya-over-1-ghati-after-sunset"
    return chosen


def _dussehra(span: tuple[float, float], lat: float, lon: float, tz: str
              ) -> tuple[Day, str] | None:
    """Vijayadashami, Drik's rules, checked on 2022-2028:

      * Dashami covering the WHOLE Aparahna on one day only -> that day
        (2025, 2026, 2028 - even when Shravana is in the next day's Aparahna);
      * on both days -> the first, unless Shravana nakshatra is in the second
        day's Aparahna;
      * on neither -> the day whose Aparahna has Shravana with Dashami present
        that day (at Aparahna or sunrise) (2022), else the day with more of
        Aparahna in Dashami (2023).
    """
    days = _candidate_days(span[0], span[1], lat, lon, tz)
    full = [d for d in days if span[0] <= d.part(4)[0] and d.part(4)[1] <= span[1]]
    if len(full) == 1:
        return full[0], "aparahna-vyapini"
    if len(full) >= 2:
        if _nakshatra_in(21, full[1].part(4)):
            return full[1], "both-days-shravana-on-second"
        return full[0], "both-days-first"
    for d in days:
        w = d.part(4)
        present = _overlap(w, span) > 0 or span[0] <= d.sunrise < span[1]
        if present and _nakshatra_in(21, w):
            return d, "shravana-at-aparahna"
    return _choose_day(span, "aparahna", "most", lat, lon, tz)


def _holika_dahan(span: tuple[float, float], lat: float, lon: float, tz: str
                  ) -> tuple[Day, str, tuple[float, float]] | None:
    """Holika Dahan (Phalguna Purnima), Drik's rules: the Bhadra-free part of
    Pradosh (sunset + 3 night muhurtas) while Purnima prevails; if Bhadra
    spoils that evening and Purnima is at the next sunrise for at least 3.5
    prahars, the NEXT evening's Pradosh even though Pratipada has begun
    (2023, 2026); failing both, Bhadra Punchha that night (2022, 2027)."""
    days = _candidate_days(span[0], span[1], lat, lon, tz)
    first = None
    for d in days:
        pr = (d.sunset, d.sunset + 3 * d.night_len / 15.0)
        if _overlap(pr, span) > 0:
            first = first or d
            free = _bhadra_free(pr, span)
            if free:
                return d, "pradosh-bhadra-free", free
    if first:
        # Bhadra over Pradosh but ending before midnight: after Bhadra, same night.
        midnight = first.sunset + first.night_len / 2.0
        ends = [be for bs, be in _bhadra_spans(first.sunset - 1.0, first.next_sunrise)
                if bs < first.sunset + 3 * first.night_len / 15.0 and be > first.sunset]
        if ends and max(ends) <= midnight and max(ends) < span[1]:
            return first, "after-bhadra-before-midnight", (max(ends), max(ends))
    for d in days:
        # Purnima lasting 3.5 prahars (7/8 of the day) after the next sunrise.
        if span[0] <= d.sunrise < span[1] and span[1] - d.sunrise >= d.day_len * 7 / 8 \
                and (first is None or d.date > first.date):
            return d, "next-pradosh-purnima-3.5-prahars", (d.sunset, d.sunset + 3 * d.night_len / 15.0)
    if first:
        # Drik then uses Bhadra Punchha the same night (2022, 2027); its
        # division of Bhadra is not modelled, so the date is given without a time.
        return first, "bhadra-punchha-same-night", None
    return None


def _raksha_bandhan(span: tuple[float, float], lat: float, lon: float, tz: str
                    ) -> tuple[Day, str, tuple[float, float]] | None:
    """Raksha Bandhan (Shravana Purnima), Drik's rule: the Bhadra-free part of
    Aparahna on the Purnima day; if Bhadra spoils that, the next day's morning
    provided Purnima lasts at least 3 muhurtas (a fifth of the day) after its
    sunrise; failing both, the Bhadra-free part of that first evening's
    Pradosh. (2026: Bhadra over Aparahna on 27 Aug, Purnima till 9:48 AM on
    28 Aug -> 28 Aug, 5:57-9:48 AM, as Drik prints.)"""
    days = _candidate_days(span[0], span[1], lat, lon, tz)
    first = None
    for d in days:
        if _overlap(d.part(4), span) > 0:
            first = first or d
            free = _bhadra_free(d.part(4), span)
            if free:
                return d, "aparahna-bhadra-free", free
    for d in days:
        if span[0] <= d.sunrise < span[1] and span[1] - d.sunrise >= d.day_len / 5.0:
            free = _bhadra_free((d.sunrise, span[1]), span)
            if free:
                return d, "next-morning-bhadra-free", free
    if first:
        free = _bhadra_free((first.sunset, first.sunset + 3 * first.night_len / 15.0), span)
        if free:
            return first, "pradosh-bhadra-free", free
        # Bhadra outlasts Pradosh too: after Bhadra ends that night (2023: 9:01 PM).
        free = _bhadra_free((first.sunset, first.next_sunrise), span)
        if free:
            return first, "after-bhadra-night", free
    return None


def _makar_sankranti(year: int, lat: float, lon: float, tz: str) -> dict | None:
    z = ZoneInfo(tz)
    guess = P._to_jd(dt.datetime(year, 1, 14, 12, tzinfo=z))
    jd = _sun_ingress(9, guess)
    local = P._from_jd(jd, z)
    d = _day(local.date(), lat, lon, tz)
    if d is None:
        return None
    if jd >= d.sunset:                                 # after sunset: next day's daytime
        d = _day(local.date() + dt.timedelta(days=1), lat, lon, tz)
        start = d.sunrise
    elif jd < d.sunrise:
        start = d.sunrise
    else:
        start = jd
    o = {
        "key": "makar_sankranti", "name_en": "Makar Sankranti", "name_hi": "मकर संक्रांति",
        "date": d.date.isoformat(), "major": True, "slug": "makar-sankranti",
        "kind": "festival", "rule": "sankranti",
        "rule_en": "the Sun's entry into sidereal Makara (Capricorn); punya kaal follows it "
                   "until sunset",
        "rule_hi": "सूर्य का मकर राशि (निरयण) में प्रवेश; पुण्य काल संक्रांति से सूर्यास्त तक",
        "decided": "sankranti", "month": None, "tithi": None,
        "timings": [_timing("sankranti", tz, at=jd),
                    _timing("punya_kaal", tz, start, d.sunset)],
    }
    return o


# --------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------

def _tithi_runs(jd_from: float, jd_to: float) -> list[tuple[int, float, float]]:
    out = []
    cursor = jd_from
    while cursor < jd_to:
        idx, s, e = _tithi_span(cursor)
        out.append((idx, s, e))
        cursor = e + 1e-5
    return out


def _doubled(month: dict) -> bool:
    """Whether this lunar month occurs twice this year: it is the adhika one,
    or the month before it was the adhika month of the same name."""
    if month["adhika"]:
        return True
    prev = P.lunar_month_at(month["start_jd"] - 1.0)
    return bool(prev["adhika"] and prev["index"] == month["index"])


def _lohri(ms: dict) -> dict:
    """Lohri: the day before Makar Sankranti (Drik: 13 Jan 2026, 14 Jan 2024)."""
    d = dt.date.fromisoformat(ms["date"]) - dt.timedelta(days=1)
    return {
        "key": "lohri", "name_en": "Lohri", "name_hi": "लोहड़ी", "date": d.isoformat(),
        "major": True, "slug": "lohri", "kind": "festival", "rule": "sankranti-eve",
        "rule_en": "the day before Makar Sankranti", "rule_hi": "मकर संक्रांति से एक दिन पहले",
        "decided": "day-before-makar-sankranti", "month": None, "tithi": None, "timings": [],
    }


def _compute(first: dt.date, last: dt.date, lat: float, lon: float, tz: str) -> list[dict]:
    """Every validated observance dated first..last, unsorted."""
    P._ephemeris()
    z = ZoneInfo(tz)
    # Pad: an observance can fall a day or two either side of its tithi.
    jd_from = P._to_jd(dt.datetime.combine(first - dt.timedelta(days=3), dt.time(), z))
    jd_to = P._to_jd(dt.datetime.combine(last + dt.timedelta(days=3), dt.time(), z))
    out: list[dict] = []
    by_tithi: dict[int, list[Spec]] = {}
    for spec in RECURRING + FESTIVALS:
        by_tithi.setdefault(spec.tithi, []).append(spec)
    for index, s, e in _tithi_runs(jd_from, jd_to):
        span = (s, e)
        month = P.lunar_month_at((s + e) / 2.0)
        if index in (S + 10, K + 10):
            o = _ekadashi(index, span, lat, lon, tz, month)
            if o:
                out.append(o)
        for spec in by_tithi.get(index, ()):
            if spec.month is not None:
                if spec.month != month["index"]:
                    continue
                if month["adhika"] != (spec.adhika_first and _doubled(month)):
                    continue
            rakhi = None
            if spec.key == "janmashtami":
                chosen = _janmashtami(span, lat, lon, tz)
            elif spec.key == "dussehra":
                chosen = _dussehra(span, lat, lon, tz)
            elif spec.key == "diwali":
                chosen = _diwali(span, lat, lon, tz)
            elif spec.key == "holika_dahan":
                chosen = _holika_dahan(span, lat, lon, tz)
                if chosen:
                    chosen, rakhi = chosen[:2], chosen[2]
            elif spec.key == "raksha_bandhan":
                chosen = _raksha_bandhan(span, lat, lon, tz)
                if chosen:
                    chosen, rakhi = chosen[:2], chosen[2]
            else:
                chosen = _choose_day(span, spec.rule, spec.tie, lat, lon, tz)
            if chosen is None:
                continue
            d, how = chosen
            o = _base(spec, d, how, index, span, tz, month)
            _add_timings(o, spec, d, span, lat, lon, tz)
            if rakhi and rakhi[0] == rakhi[1]:            # "after Bhadra ends" - a moment
                o["timings"].append(_timing("holika_after_bhadra", tz, at=rakhi[0]))
            elif rakhi:
                o["timings"].append(_timing(
                    "holika_dahan" if spec.key == "holika_dahan" else "rakhi", tz, *rakhi))
            out.append(o)
            if spec.key == "holika_dahan":
                nd = _day(d.date + dt.timedelta(days=1), lat, lon, tz)
                holi = dict(o, key="holi", name_en="Holi", name_hi="होली", slug="holi",
                            date=nd.date.isoformat(), decided="day-after-holika-dahan",
                            rule_en="the day after Holika Dahan",
                            rule_hi="होलिका दहन के अगले दिन", timings=[])
                out.append(holi)
    for year in range(first.year, last.year + 1):
        if first <= dt.date(year, 1, 16) and dt.date(year, 1, 11) <= last:
            ms = _makar_sankranti(year, lat, lon, tz)
            if ms:
                out.append(ms)
                out.append(_lohri(ms))
    lo, hi = first.isoformat(), last.isoformat()
    out = [o for o in out if lo <= o["date"] <= hi and o["key"] not in OMITTED]
    for o in out:
        o["timings"] = [t for t in o["timings"] if (o["key"], t["key"]) not in OMITTED_TIMINGS]
    out.sort(key=lambda o: (o["date"], not o["major"], o["key"]))
    return out


@functools.lru_cache(maxsize=16)
def _year(year: int, lat: float, lon: float, tz: str) -> tuple[dict, ...]:
    """Every observance dated in `year` (~0.4 s; computed once per process)."""
    return tuple(_compute(dt.date(year, 1, 1), dt.date(year, 12, 31), lat, lon, tz))


def observances(start: dt.date, end: dt.date, latitude: float = DELHI[0],
                longitude: float = DELHI[1], timezone: str = DELHI[2]) -> list[dict]:
    """Every validated vrat/festival with start <= date <= end, in date order.
    Dicts are shared with the per-process cache: treat them as read-only."""
    lat, lon = round(float(latitude), 4), round(float(longitude), 4)
    out: list[dict] = []
    for y in range(start.year, end.year + 1):
        out += [o for o in _year(y, lat, lon, timezone)
                if start.isoformat() <= o["date"] <= end.isoformat()]
    return out


def window(start: dt.date, end: dt.date, latitude: float, longitude: float,
           timezone: str) -> list[dict]:
    """observances() for a short range WITHOUT computing (and caching) whole
    years: ~40 ms for 31 days at any place, against ~0.4 s per year. For the
    per-city /vrat-tyohar/<city> pages (DIVASTRO-114), which cache the result
    per (city, day) themselves - 114 cities would thrash `_year`'s cache. Same
    engine, same OMITTED filtering, same order as observances()."""
    return _compute(start, end, round(float(latitude), 4), round(float(longitude), 4), timezone)


@functools.lru_cache(maxsize=1024)
def _on(day: dt.date, lat: float, lon: float, tz: str) -> tuple[dict, ...]:
    return tuple(_compute(day, day, lat, lon, tz))


def on(day: dt.date, latitude: float = DELHI[0], longitude: float = DELHI[1],
       timezone: str = DELHI[2]) -> list[dict]:
    """The observances of one day. For an arbitrary city this computes only a
    week of tithis around `day` (~20 ms), not the whole year."""
    lat, lon = round(float(latitude), 2), round(float(longitude), 2)
    if (lat, lon, timezone) == (round(DELHI[0], 2), round(DELHI[1], 2), DELHI[2]):
        return observances(day, day)
    return list(_on(day, lat, lon, timezone))
