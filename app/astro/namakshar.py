"""Nakshatra reference data and the namakshar (name-syllable) lookup — DIVASTRO-115.

Two kinds of data live here, and they are kept apart on purpose:

* **Derived, never re-typed.** Each nakshatra's gana, yoni and nadi come from
  `astro.matching`'s Ashtakoot tables, and its Vimshottari lord from
  `chart_service.VIMSHOTTARI` (the dasha module), so the public pages cannot
  contradict the Kundali Milan tool or the dasha the kundali prints. Degree
  spans, padas and the rashi of every pada are geometry (13°20′ per
  nakshatra, 3°20′ per pada, 30° per sign) and are computed.

* **Curated here, because no engine needs them:** the deity, the symbol and
  the namakshar syllable of each of the 108 padas.

Sources for the curated table
-----------------------------
  * Syllables: the 108 "pada swar" list of Swar Siddhanta as published by
    Drik Panchang ("Hindu Name Initials — List of 108 Pada Swars based on 27
    Nakshatras", drikpanchang.com/swar-siddhanta/nakshatra/), which is the
    Avakahada Chakra printed in North-Indian panchangs. Checked entry by entry
    against that page (October 2026). Drik's short-vowel spellings (चु, वु, गु)
    and bare consonants (घ, ङ, छ, ष, ण, ठ, ढ, थ, झ, ञ, च) are kept verbatim.
  * Deity and symbol: the classical list (Taittiriya Brahmana for the deities;
    the symbols as handed down in the jyotisha tradition), checked against
    Wikipedia's "List of Nakshatras" table and Drik Panchang's nakshatra pages.
    Where the tradition gives two symbols both are shown ("bow and quiver").

Known variants (documented, not silently chosen):
  * Shravana: खी खू खे खो (used here, Drik's list). Another current panchang
    tradition gives जू जे जो खा to Shravana, which this list assigns to
    Abhijit — see ABHIJIT below.
  * In Devanagari every pada's syllable is distinct (asserted at import). In
    Latin transliteration several collide — Ta (टा Purva Phalguni / ता Swati),
    Ti/Tu/Te/To (ट / त), Da/Di/Du/De/Do (ड / द), Dha (धा / ढ), Tha (ठ / थ),
    Na (ण / ना). That is why the Naam Milan form shows which syllable it used
    and lets the reader pick another.

Name → syllable rules (the traditional shortcut, as Hindi panchangs apply it):
  * the first akshar decides: its first consonant plus its vowel. A conjunct
    keeps its first consonant (प्रिया → प + ि → पी); nukta is ignored
    (ज़ → ज); anusvara/chandrabindu/visarga are ignored.
  * vowel length is not distinguished (अ = आ, इ = ई, उ = ऊ), ऐ counts as ए and
    औ as ओ, and ृ (as in कृष्ण) is read "ri" → इ.
  * ब counts as व (the Avakahada Chakra writes व/ब as one row);
    श counts as ष with the a-vowel (Hasta) and as स otherwise (शिव → सी);
    a leading ऋ is read as री.
  * Abhijit, the 28th nakshatra, is not part of the 27-nakshatra wheel; its
    syllables जू जे जो खा are folded into Uttara Ashadha pada 4 (Abhijit
    begins at 276°40′, the start of that pada — both readings fall in Makar).
  * when the exact syllable is not in the list (e.g. धी), the nearest
    syllable with the same consonant is used and flagged as approximate.
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass, replace

from ..chart_service import NAKSHATRAS, SIGNS, VIMSHOTTARI
from . import matching
from .names_hi import NAKSHATRAS_HI

NAK_MIN = 800          # one nakshatra = 13°20′ = 800 arc-minutes
PADA_MIN = 200         # one pada = 3°20′
SIGN_MIN = 1800        # one sign = 30°

# --------------------------------------------------------------------------
# The curated table: slug, deity (EN, HI), symbol (EN, HI), 4 syllables
# (Devanagari, Latin). See the module docstring for sources.
# --------------------------------------------------------------------------

_CURATED = (
    ("ashwini", "The Ashwini Kumaras, the divine physicians", "अश्विनी कुमार (देव-वैद्य)",
     "A horse's head", "अश्व का मुख", (("चु", "Chu"), ("चे", "Che"), ("चो", "Cho"), ("ला", "La"))),
    ("bharani", "Yama, lord of dharma", "यम (धर्मराज)",
     "The yoni (womb)", "योनि", (("ली", "Li"), ("लू", "Lu"), ("ले", "Le"), ("लो", "Lo"))),
    ("krittika", "Agni, the fire", "अग्नि देव",
     "A razor or flame", "छुरा / अग्निशिखा", (("अ", "A"), ("ई", "I"), ("उ", "U"), ("ए", "E"))),
    ("rohini", "Brahma (Prajapati)", "ब्रह्मा (प्रजापति)",
     "A chariot or ox-cart", "रथ / बैलगाड़ी", (("ओ", "O"), ("वा", "Va"), ("वी", "Vi"), ("वु", "Vu"))),
    ("mrigashira", "Soma, the Moon", "सोम (चंद्र देव)",
     "A deer's head", "मृग का मुख", (("वे", "Ve"), ("वो", "Vo"), ("का", "Ka"), ("की", "Ki"))),
    ("ardra", "Rudra", "रुद्र",
     "A teardrop or diamond", "अश्रुबिंदु / हीरा", (("कु", "Ku"), ("घ", "Gha"), ("ङ", "Nga"), ("छ", "Chha"))),
    ("punarvasu", "Aditi, mother of the gods", "अदिति (देवमाता)",
     "A bow and quiver", "धनुष और तूणीर", (("के", "Ke"), ("को", "Ko"), ("हा", "Ha"), ("ही", "Hi"))),
    ("pushya", "Brihaspati, guru of the gods", "बृहस्पति (देवगुरु)",
     "A cow's udder or lotus", "गाय का थन / कमल", (("हु", "Hu"), ("हे", "He"), ("हो", "Ho"), ("डा", "Da"))),
    ("ashlesha", "The Nagas (serpent deities)", "नाग देवता",
     "A coiled serpent", "कुंडली मारे सर्प", (("डी", "Di"), ("डू", "Du"), ("डे", "De"), ("डो", "Do"))),
    ("magha", "The Pitris (ancestors)", "पितृ (पूर्वज)",
     "A royal throne", "राजसिंहासन", (("मा", "Ma"), ("मी", "Mi"), ("मू", "Mu"), ("मे", "Me"))),
    ("purva-phalguni", "Bhaga, giver of fortune", "भग देव",
     "The front legs of a bed", "पलंग के अगले पाये", (("मो", "Mo"), ("टा", "Ta"), ("टी", "Ti"), ("टू", "Tu"))),
    ("uttara-phalguni", "Aryaman, lord of friendship", "अर्यमा",
     "The back legs of a bed", "पलंग के पिछले पाये", (("टे", "Te"), ("टो", "To"), ("पा", "Pa"), ("पी", "Pi"))),
    ("hasta", "Savitr, the Sun", "सविता (सूर्य देव)",
     "A hand", "हाथ (हस्त)", (("पू", "Pu"), ("ष", "Sha"), ("ण", "Na"), ("ठ", "Tha"))),
    ("chitra", "Tvashtr (Vishwakarma), the divine architect", "त्वष्टा (विश्वकर्मा)",
     "A bright jewel", "चमकता रत्न / मोती", (("पे", "Pe"), ("पो", "Po"), ("रा", "Ra"), ("री", "Ri"))),
    ("swati", "Vayu, the wind", "वायु देव",
     "A young shoot swaying in the wind", "हवा में लहराता अंकुर", (("रू", "Ru"), ("रे", "Re"), ("रो", "Ro"), ("ता", "Ta"))),
    ("vishakha", "Indra and Agni (Indragni)", "इन्द्र और अग्नि (इन्द्राग्नि)",
     "A triumphal arch", "तोरण द्वार", (("ती", "Ti"), ("तू", "Tu"), ("ते", "Te"), ("तो", "To"))),
    ("anuradha", "Mitra, lord of friendship", "मित्र देव",
     "A lotus", "कमल", (("ना", "Na"), ("नी", "Ni"), ("नू", "Nu"), ("ने", "Ne"))),
    ("jyeshtha", "Indra, king of the gods", "इन्द्र (देवराज)",
     "A circular amulet or earring", "गोल कुंडल / ताबीज़", (("नो", "No"), ("या", "Ya"), ("यी", "Yi"), ("यू", "Yu"))),
    ("mula", "Nirriti", "निऋति",
     "A bunch of roots", "जड़ों का गुच्छा", (("ये", "Ye"), ("यो", "Yo"), ("भा", "Bha"), ("भी", "Bhi"))),
    ("purva-ashadha", "Apas, the waters", "आपः (जल देवता)",
     "A winnowing fan or elephant tusk", "सूप (पंखा) / हाथी दाँत", (("भू", "Bhu"), ("धा", "Dha"), ("फा", "Pha"), ("ढ", "Dha"))),
    ("uttara-ashadha", "The Vishvedevas (universal gods)", "विश्वेदेव",
     "An elephant tusk", "हाथी दाँत", (("भे", "Bhe"), ("भो", "Bho"), ("जा", "Ja"), ("जी", "Ji"))),
    ("shravana", "Vishnu", "भगवान विष्णु",
     "An ear, or three footprints", "कान / तीन पदचिह्न", (("खी", "Khi"), ("खू", "Khu"), ("खे", "Khe"), ("खो", "Kho"))),
    ("dhanishta", "The eight Vasus", "अष्ट वसु",
     "A drum (mridanga)", "मृदंग (ढोल)", (("गा", "Ga"), ("गी", "Gi"), ("गु", "Gu"), ("गे", "Ge"))),
    ("shatabhisha", "Varuna, lord of the waters", "वरुण देव",
     "An empty circle", "रिक्त वृत्त", (("गो", "Go"), ("सा", "Sa"), ("सी", "Si"), ("सू", "Su"))),
    ("purva-bhadrapada", "Aja Ekapada", "अज एकपाद",
     "Swords, or the front legs of a cot", "तलवार / खाट के अगले पाये", (("से", "Se"), ("सो", "So"), ("दा", "Da"), ("दी", "Di"))),
    ("uttara-bhadrapada", "Ahir Budhnya, serpent of the deep", "अहिर्बुध्न्य",
     "The back legs of a cot, or twins", "खाट के पिछले पाये / जुड़वाँ", (("दू", "Du"), ("थ", "Tha"), ("झ", "Jha"), ("ञ", "Nya"))),
    ("revati", "Pushan, the nourisher and guide", "पूषा देव",
     "A fish (or a drum)", "मछली (या मृदंग)", (("दे", "De"), ("दो", "Do"), ("च", "Cha"), ("ची", "Chi"))),
)

# Abhijit's syllables, folded into Uttara Ashadha pada 4 (see the docstring).
ABHIJIT = (("जू", "Ju"), ("जे", "Je"), ("जो", "Jo"), ("खा", "Kha"))
ABHIJIT_TARGET = (20, 4)   # (nakshatra index, pada)


@dataclass(frozen=True)
class Nakshatra:
    index: int                 # 0 = Ashwini
    name: str                  # chart_service.NAKSHATRAS spelling (the engines' key)
    slug: str
    name_hi: str
    deity: str
    deity_hi: str
    symbol: str
    symbol_hi: str
    syllables: tuple[tuple[str, str], ...]   # 4 x (Devanagari, Latin)
    # DIVASTRO-123: Kannada / Telugu (nakshatra_pages._own reads <field>_<lang>)
    deity_kn: str = ""
    symbol_kn: str = ""
    deity_te: str = ""
    symbol_te: str = ""

    @property
    def start_min(self) -> int:
        return self.index * NAK_MIN

    @property
    def lord(self) -> str:
        """Vimshottari lord — the same table the dasha engine starts from."""
        return VIMSHOTTARI[self.index % 9][0]

    @property
    def gana(self) -> str:
        return matching.GANA_OF_NAKSHATRA[self.name]

    @property
    def yoni(self) -> tuple[str, str]:
        return matching.YONI_OF_NAKSHATRA[self.name]

    @property
    def nadi(self) -> str:
        return matching.NADI_OF_NAKSHATRA[self.name]

    def pada_sign(self, pada: int) -> int:
        """Sign index (0 = Aries) that pada 1..4 falls in."""
        return (self.start_min + (pada - 1) * PADA_MIN) // SIGN_MIN

    @property
    def signs(self) -> list[int]:
        out: list[int] = []
        for p in range(1, 5):
            s = self.pada_sign(p)
            if s not in out:
                out.append(s)
        return out


NAKSHATRA_LIST: tuple[Nakshatra, ...] = tuple(
    Nakshatra(i, NAKSHATRAS[i], slug, NAKSHATRAS_HI[NAKSHATRAS[i]], d, dh, s, sh, syl)
    for i, (slug, d, dh, s, sh, syl) in enumerate(_CURATED))

# DIVASTRO-123: deity and symbol in Kannada and Telugu: slug -> (deity, symbol).
_LOCAL = {
    "kn": {
        "ashwini": ("ಅಶ್ವಿನಿ ಕುಮಾರರು (ದೇವವೈದ್ಯರು)", "ಕುದುರೆಯ ಮುಖ"),
        "bharani": ("ಯಮ (ಧರ್ಮರಾಜ)", "ಯೋನಿ (ಗರ್ಭ)"),
        "krittika": ("ಅಗ್ನಿ ದೇವ", "ಕ್ಷೌರಕತ್ತಿ / ಅಗ್ನಿಜ್ವಾಲೆ"),
        "rohini": ("ಬ್ರಹ್ಮ (ಪ್ರಜಾಪತಿ)", "ರಥ / ಎತ್ತಿನ ಬಂಡಿ"),
        "mrigashira": ("ಸೋಮ (ಚಂದ್ರ)", "ಜಿಂಕೆಯ ಮುಖ"),
        "ardra": ("ರುದ್ರ", "ಕಣ್ಣೀರಿನ ಹನಿ / ವಜ್ರ"),
        "punarvasu": ("ಅದಿತಿ (ದೇವಮಾತೆ)", "ಬಿಲ್ಲು ಮತ್ತು ಬತ್ತಳಿಕೆ"),
        "pushya": ("ಬೃಹಸ್ಪತಿ (ದೇವಗುರು)", "ಹಸುವಿನ ಕೆಚ್ಚಲು / ಕಮಲ"),
        "ashlesha": ("ನಾಗ ದೇವತೆಗಳು", "ಸುರುಳಿ ಸುತ್ತಿದ ಸರ್ಪ"),
        "magha": ("ಪಿತೃಗಳು (ಪೂರ್ವಜರು)", "ರಾಜಸಿಂಹಾಸನ"),
        "purva-phalguni": ("ಭಗ ದೇವ (ಭಾಗ್ಯದಾತ)", "ಮಂಚದ ಮುಂದಿನ ಕಾಲುಗಳು"),
        "uttara-phalguni": ("ಅರ್ಯಮ (ಸ್ನೇಹದ ಅಧಿದೇವತೆ)", "ಮಂಚದ ಹಿಂದಿನ ಕಾಲುಗಳು"),
        "hasta": ("ಸವಿತೃ (ಸೂರ್ಯ)", "ಕೈ (ಹಸ್ತ)"),
        "chitra": ("ತ್ವಷ್ಟೃ (ವಿಶ್ವಕರ್ಮ)", "ಹೊಳೆಯುವ ರತ್ನ"),
        "swati": ("ವಾಯು ದೇವ", "ಗಾಳಿಗೆ ತೂಗುವ ಚಿಗುರು"),
        "vishakha": ("ಇಂದ್ರ ಮತ್ತು ಅಗ್ನಿ (ಇಂದ್ರಾಗ್ನಿ)", "ತೋರಣ ದ್ವಾರ"),
        "anuradha": ("ಮಿತ್ರ ದೇವ", "ಕಮಲ"),
        "jyeshtha": ("ಇಂದ್ರ (ದೇವರಾಜ)", "ಕುಂಡಲ / ತಾಯಿತ"),
        "mula": ("ನಿಋತಿ", "ಬೇರುಗಳ ಗೊಂಚಲು"),
        "purva-ashadha": ("ಆಪಃ (ಜಲ ದೇವತೆ)", "ಮೊರ / ಆನೆಯ ದಂತ"),
        "uttara-ashadha": ("ವಿಶ್ವೇದೇವರು", "ಆನೆಯ ದಂತ"),
        "shravana": ("ಶ್ರೀ ವಿಷ್ಣು", "ಕಿವಿ / ಮೂರು ಹೆಜ್ಜೆಗುರುತುಗಳು"),
        "dhanishta": ("ಅಷ್ಟ ವಸುಗಳು", "ಮೃದಂಗ"),
        "shatabhisha": ("ವರುಣ ದೇವ", "ಖಾಲಿ ವೃತ್ತ"),
        "purva-bhadrapada": ("ಅಜ ಏಕಪಾದ", "ಖಡ್ಗ / ಮಂಚದ ಮುಂದಿನ ಕಾಲುಗಳು"),
        "uttara-bhadrapada": ("ಅಹಿರ್ಬುಧ್ನ್ಯ", "ಮಂಚದ ಹಿಂದಿನ ಕಾಲುಗಳು / ಅವಳಿಗಳು"),
        "revati": ("ಪೂಷನ್ ದೇವ", "ಮೀನು (ಅಥವಾ ಮೃದಂಗ)"),
    },
    "te": {
        "ashwini": ("అశ్విని కుమారులు (దేవ వైద్యులు)", "గుర్రపు ముఖం"),
        "bharani": ("యముడు (ధర్మరాజు)", "యోని (గర్భం)"),
        "krittika": ("అగ్ని దేవుడు", "కత్తి / అగ్నిజ్వాల"),
        "rohini": ("బ్రహ్మ (ప్రజాపతి)", "రథం / ఎడ్లబండి"),
        "mrigashira": ("సోముడు (చంద్రుడు)", "జింక ముఖం"),
        "ardra": ("రుద్రుడు", "కన్నీటి బిందువు / వజ్రం"),
        "punarvasu": ("అదితి (దేవమాత)", "విల్లు, అమ్ములపొది"),
        "pushya": ("బృహస్పతి (దేవగురువు)", "ఆవు పొదుగు / పద్మం"),
        "ashlesha": ("నాగ దేవతలు", "చుట్టుకున్న సర్పం"),
        "magha": ("పితృదేవతలు (పూర్వీకులు)", "రాజ సింహాసనం"),
        "purva-phalguni": ("భగుడు (అదృష్టప్రదాత)", "మంచం ముందు కాళ్లు"),
        "uttara-phalguni": ("అర్యముడు (స్నేహానికి అధిపతి)", "మంచం వెనుక కాళ్లు"),
        "hasta": ("సవిత (సూర్యుడు)", "చేయి (హస్తం)"),
        "chitra": ("త్వష్ట (విశ్వకర్మ)", "మెరిసే రత్నం"),
        "swati": ("వాయు దేవుడు", "గాలికి ఊగే మొలక"),
        "vishakha": ("ఇంద్రుడు, అగ్ని (ఇంద్రాగ్ని)", "తోరణ ద్వారం"),
        "anuradha": ("మిత్రుడు", "పద్మం"),
        "jyeshtha": ("ఇంద్రుడు (దేవరాజు)", "కుండలం / తాయెత్తు"),
        "mula": ("నిరృతి", "వేర్ల గుత్తి"),
        "purva-ashadha": ("ఆపః (జల దేవత)", "చేట / ఏనుగు దంతం"),
        "uttara-ashadha": ("విశ్వేదేవతలు", "ఏనుగు దంతం"),
        "shravana": ("శ్రీ మహావిష్ణువు", "చెవి / మూడు పాదముద్రలు"),
        "dhanishta": ("అష్ట వసువులు", "మృదంగం"),
        "shatabhisha": ("వరుణ దేవుడు", "శూన్య వృత్తం"),
        "purva-bhadrapada": ("అజ ఏకపాదుడు", "ఖడ్గాలు / మంచం ముందు కాళ్లు"),
        "uttara-bhadrapada": ("అహిర్బుధ్న్యుడు", "మంచం వెనుక కాళ్లు / కవలలు"),
        "revati": ("పూషుడు", "చేప (లేదా మృదంగం)"),
    },
}
NAKSHATRA_LIST = tuple(
    replace(n, **{f"{field}_{lang}": _LOCAL[lang][n.slug][i]
                  for lang in _LOCAL for i, field in enumerate(("deity", "symbol"))})
    for n in NAKSHATRA_LIST)
BY_SLUG = {n.slug: n for n in NAKSHATRA_LIST}


# DIVASTRO-123: the Kannada and Telugu pages print the namakshar syllables in
# their own script. Every Devanagari letter and vowel sign the table uses has
# its counterpart at a fixed offset in the Kannada and Telugu blocks (ए/े are
# the long ಏ/ೇ, ఏ/ే - the vowel Hindi writes).
_SCRIPT_OFFSET = {"kn": 0x0C80 - 0x0900, "te": 0x0C00 - 0x0900}


def syllable_text(text: str, lang: str) -> str:
    """`text` with its Devanagari moved into `lang`'s script (kn, te); unchanged otherwise."""
    off = _SCRIPT_OFFSET.get(lang)
    if not off:
        return text
    out = []
    for c in text:
        if 0x0900 <= ord(c) <= 0x097F and unicodedata.name(chr(ord(c) + off), ""):
            c = chr(ord(c) + off)
        out.append(c)
    return "".join(out)


def syllable_lang(lang: str) -> str:
    """The lang="" attribute of a syllable: Hindi (Devanagari) except where moved."""
    return lang if lang in _SCRIPT_OFFSET else "hi"
BY_NAME = {n.name: n for n in NAKSHATRA_LIST}


def sign_padas(sign_index: int) -> list[tuple[Nakshatra, int]]:
    """The nine (nakshatra, pada) quarters inside one sign, in order."""
    first = sign_index * SIGN_MIN // PADA_MIN
    return [(NAKSHATRA_LIST[g // 4], g % 4 + 1) for g in range(first, first + 9)]


def pada_longitude(index: int, pada: int) -> float:
    """Sidereal longitude of the middle of a pada — the stand-in Moon the
    name method gives the matching engine."""
    return (index * NAK_MIN + (pada - 1) * PADA_MIN + PADA_MIN / 2) / 60.0


# --------------------------------------------------------------------------
# Syllable keys: (consonant or "", vowel class)
# --------------------------------------------------------------------------

VIRAMA, NUKTA = "्", "़"
INDEPENDENT = {"अ": "a", "आ": "a", "इ": "i", "ई": "i", "उ": "u", "ऊ": "u", "ए": "e",
               "ऐ": "e", "ओ": "o", "औ": "o", "ऍ": "e", "ऑ": "o"}
MATRA = {"ा": "a", "ि": "i", "ी": "i", "ु": "u", "ू": "u", "े": "e", "ै": "e",
         "ो": "o", "ौ": "o", "ृ": "i", "ॄ": "i", "ॅ": "e", "ॉ": "o"}
VOWEL_ORDER = ("a", "i", "u", "e", "o")


def _is_consonant(ch: str) -> bool:
    return "क" <= ch <= "ह"


def _parse_dev(text: str) -> tuple[str, str] | None:
    """(first consonant or "", vowel class) of the first akshar of `text`."""
    s = unicodedata.normalize("NFD", text).replace(NUKTA, "")
    s = "".join(ch for ch in s if "ऀ" <= ch <= "ॿ")
    if not s:
        return None
    ch = s[0]
    if ch in ("ऋ", "ॠ"):
        return "र", "i"
    if ch in INDEPENDENT:
        return "", INDEPENDENT[ch]
    if not _is_consonant(ch):
        return None
    first, i = ch, 1
    while i + 1 < len(s) and s[i] == VIRAMA and _is_consonant(s[i + 1]):
        i += 2                                   # conjunct: keep the first consonant
    vowel = MATRA.get(s[i], "a") if i < len(s) else "a"
    return first, vowel


def _key_of(dev: str) -> tuple[str, str]:
    k = _parse_dev(dev)
    assert k is not None, dev
    return k


# key -> (nakshatra index, pada)
TABLE: dict[tuple[str, str], tuple[int, int]] = {}
for _n in NAKSHATRA_LIST:
    for _p, (_dev, _lat) in enumerate(_n.syllables, start=1):
        _k = _key_of(_dev)
        if _k in TABLE:
            raise AssertionError(f"duplicate namakshar {_dev}")
        TABLE[_k] = (_n.index, _p)
ABHIJIT_KEYS = {_key_of(d): d for d, _ in ABHIJIT}
for _k in ABHIJIT_KEYS:
    if _k in TABLE:
        raise AssertionError(f"Abhijit syllable collides: {_k}")


def all_padas() -> list[tuple[Nakshatra, int]]:
    return [(n, p) for n in NAKSHATRA_LIST for p in range(1, 5)]


def pada_id(n: Nakshatra, pada: int) -> str:
    """Stable form value for one pada, e.g. "chitra-3"."""
    return f"{n.slug}-{pada}"


def from_pada_id(value: str) -> tuple[Nakshatra, int] | None:
    slug, _, p = (value or "").rpartition("-")
    n = BY_SLUG.get(slug)
    if n is None or p not in ("1", "2", "3", "4"):
        return None
    return n, int(p)


# --------------------------------------------------------------------------
# Latin transliteration (first syllable only)
# --------------------------------------------------------------------------

# Longest first. Each maps to the Devanagari consonant used by default plus the
# alternatives a Latin spelling cannot tell apart.
LATIN_CONSONANTS = (
    ("chh", "छ", ()), ("ksh", "क", ()), ("shr", "श", ()), ("gy", "ज", ("ग",)),
    ("sh", "श", ("ष", "स")), ("kh", "ख", ()), ("gh", "घ", ()), ("ch", "च", ("छ",)),
    ("jh", "झ", ()), ("th", "थ", ("ठ", "त")), ("dh", "ध", ("ढ",)), ("ph", "फ", ()),
    ("bh", "भ", ()),
    ("k", "क", ()), ("g", "ग", ()), ("c", "क", ("च",)), ("j", "ज", ()), ("z", "ज", ()),
    ("t", "त", ("ट",)), ("d", "द", ("ड",)), ("n", "न", ("ण",)), ("p", "प", ()),
    ("f", "फ", ()), ("b", "ब", ()), ("m", "म", ()), ("y", "य", ()), ("r", "र", ()),
    ("l", "ल", ()), ("v", "व", ()), ("w", "व", ()), ("s", "स", ("श",)), ("h", "ह", ()),
    ("q", "क", ()),
)
LATIN_VOWELS = (
    ("aa", "a"), ("ai", "e"), ("ay", "e"), ("au", "o"), ("aw", "o"), ("ee", "i"),
    ("ei", "e"), ("oo", "u"), ("ou", "o"), ("a", "a"), ("i", "i"), ("y", "i"),
    ("u", "u"), ("e", "e"), ("o", "o"),
)
_VOWEL_LETTERS = set("aeiouy")


def _parse_latin(text: str) -> tuple[list[str], str] | None:
    """([Devanagari consonant candidates] or [""], vowel class)."""
    s = "".join(ch for ch in text.lower() if "a" <= ch <= "z")
    if not s:
        return None
    if s[0] in "aeiou":
        cands, rest = [""], s
    else:
        for lat, dev, alts in LATIN_CONSONANTS:
            if s.startswith(lat):
                cands, rest = [dev, *alts], s[len(lat):]
                break
        else:
            return None
        # A conjunct (Pr-, Shy-, Sw-, Kr-): skip to the vowel. "y" before a
        # vowel is a consonant (Shyam); otherwise it is the vowel (Lyn).
        while rest and (rest[0] not in _VOWEL_LETTERS
                        or (rest[0] == "y" and len(rest) > 1 and rest[1] in "aeiou")):
            rest = rest[1:]
    for lat, v in LATIN_VOWELS:
        if rest.startswith(lat):
            return cands, v
    return cands, "a"                            # a bare consonant reads with the inherent a


# --------------------------------------------------------------------------
# Lookup
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Match:
    nakshatra: Nakshatra
    pada: int
    akshar: str                 # what was read off the name, in Devanagari
    syllable: str               # the table syllable it maps to
    exact: bool                 # False when a rule or the nearest syllable was used
    via: str                    # "" | "abhijit" | "alias" | "nearest" | "latin"
    alternatives: tuple[tuple[Nakshatra, int], ...]

    @property
    def sign(self) -> int:
        return self.nakshatra.pada_sign(self.pada)


def _alias(cons: str, vowel: str) -> tuple[str, bool]:
    if cons == "ब":
        return "व", True
    if cons == "श":
        return ("ष" if vowel == "a" else "स"), True
    return cons, False


def _render(cons: str, vowel: str) -> str:
    matra = {"a": "ा", "i": "ी", "u": "ु", "e": "े", "o": "ो"}[vowel]
    if not cons:
        return {"a": "अ", "i": "ई", "u": "उ", "e": "ए", "o": "ओ"}[vowel]
    return cons + matra


def _resolve(cons: str, vowel: str) -> tuple[tuple[int, int], str, str] | None:
    """((index, pada), via, syllable) for one key, applying the documented rules."""
    if (cons, vowel) in TABLE:
        idx, p = TABLE[(cons, vowel)]
        return (idx, p), "", NAKSHATRA_LIST[idx].syllables[p - 1][0]
    if (cons, vowel) in ABHIJIT_KEYS:
        return ABHIJIT_TARGET, "abhijit", ABHIJIT_KEYS[(cons, vowel)]
    c2, aliased = _alias(cons, vowel)
    if aliased and (c2, vowel) in TABLE:
        idx, p = TABLE[(c2, vowel)]
        return (idx, p), "alias", NAKSHATRA_LIST[idx].syllables[p - 1][0]
    same = [(k, v) for k, v in TABLE.items() if k[0] == c2]
    if same:
        same.sort(key=lambda kv: abs(VOWEL_ORDER.index(kv[0][1]) - VOWEL_ORDER.index(vowel)))
        (k, (idx, p)) = same[0]
        return (idx, p), "nearest", NAKSHATRA_LIST[idx].syllables[p - 1][0]
    return None


def lookup(name: str) -> Match | None:
    """The namakshar pada for a name in Devanagari or Latin script, or None."""
    name = (name or "").strip()
    if not name:
        return None
    dev_first = next((ch for ch in name if "ऀ" <= ch <= "ॿ" or ch.isalpha()), "")
    if not dev_first:
        return None
    if "ऀ" <= dev_first <= "ॿ":
        key = _parse_dev(name)
        if key is None:
            return None
        cands, vowel, latin = [key[0]], key[1], False
    else:
        parsed = _parse_latin(name)
        if parsed is None:
            return None
        cands, vowel = parsed
        latin = True
    results = []
    for cons in cands:
        r = _resolve(cons, vowel)
        # Alternatives from an ambiguous Latin letter are offered only when
        # they are real table syllables, not "nearest" guesses.
        if r and results and r[1] == "nearest":
            continue
        if r and r[0] not in [x[0] for x in results]:
            results.append(r)
    if not results:
        return None
    (idx, p), via, syllable = results[0]
    alts = tuple((NAKSHATRA_LIST[i], q) for (i, q), _, _ in results[1:])
    if latin and alts and not via:
        via = "latin"
    akshar = _render(cands[0], vowel)
    return Match(NAKSHATRA_LIST[idx], p, akshar, syllable,
                 exact=(via == ""), via=via, alternatives=alts)


def match_for_pada(n: Nakshatra, pada: int) -> Match:
    """A Match chosen by hand (the reader picked a syllable)."""
    syl = n.syllables[pada - 1][0]
    return Match(n, pada, syl, syl, exact=True, via="chosen", alternatives=())


def moon_bundle(n: Nakshatra, pada: int) -> dict:
    """A minimal sidereal chart bundle whose Moon sits mid-pada — what
    `matching.ashtakoot` reads (`moon_profile`). No name is put in it."""
    lon = pada_longitude(n.index, pada)
    sign = SIGNS[int(lon // 30)]
    deg = lon % 30
    return {"meta": {"zodiac": "sidereal", "name": ""},
            "objects": {"Moon": {"longitude": lon, "sign": sign, "degree": deg,
                                 "position": f"{sign} {deg:.2f}"}}}
