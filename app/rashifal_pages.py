"""Daily Rashifal pages — /rashifal, /rashifal/<sign>, /hi/rashifal, /hi/rashifal/<sign>.

Why (DIVASTRO-105): "aaj ka rashifal" / "today's horoscope <sign>" are among
the highest-volume daily astrology searches in India. These pages answer them
in the raw HTML, in English and Hindi, the same way seo_pages.py does for the
panchang (and reusing its style, footer and cache rule).

**Computed, not invented.** Every statement on a page is keyed to a real
sidereal (Lahiri) position for today in IST, from the same Swiss Ephemeris
route the panchang engine and the kundali use (`panchang._sidereal`, mean
node, as in `panchang._chart_view`):

  * the house the transiting Moon occupies counted from each rashi (Chandra
    gochar), with the IST time if the Moon changes sign during the day;
  * the houses Saturn, Jupiter and Rahu/Ketu occupy from that rashi — the slow
    transits that set the longer backdrop — and Sade Sati / Dhaiya, which is
    Saturn in the 12th/1st/2nd (4th/8th) from the Moon sign, the same
    sign-ingress rule as `panchang.sade_sati_for_moon_sign`;
  * today's tithi and nakshatra from `daily_panchang` (New Delhi sunrise, the
    same numbers /panchang prints).

Those facts are turned into text through a fixed phrase bank (below), so the
text for a given house is the same for every sign and every day it applies —
nothing is generated, and nothing ("lucky colour", "lucky number") is shown
that does not follow from a documented rule.

**The classical scheme** (gochara phala, results of transits counted from the
janma rashi, i.e. the natal Moon sign):

  * Moon — favourable in the 1st, 3rd, 6th, 7th, 10th and 11th from the
    janma rashi; unfavourable elsewhere. Varahamihira, Brihat Samhita ch. 104
    (Grahagocharadhyaya) and Mantreswara, Phaladeepika ch. 26 (Gocharaphala)
    agree on this set. We grade the unfavourable six in two steps: 4th, 8th
    and 12th (the dusthana/kendra-of-unease positions; the 8th is the widely
    observed *Chandrashtama*) as "take it easy", and 2nd, 5th, 9th as "mixed",
    which is how most published Indian rashifals soften them.
  * Saturn — favourable in the 3rd, 6th and 11th; 12th/1st/2nd is Sade Sati;
    4th and 8th are the two Dhaiyas (Kantaka / Ashtama Shani).
  * Jupiter — favourable in the 2nd, 5th, 7th, 9th and 11th.
  * Rahu and Ketu — favourable in the 3rd, 6th and 11th (Phaladeepika 26
    treats the nodes like Saturn).

Vedha (obstruction of a transit by another planet at its vedha point) and
Ashtakavarga bindus are NOT applied — both refine a transit for an individual
chart, which is exactly what the page says a personal reading adds.

The phrase gist follows those texts (e.g. Moon in the 6th: victory over
opponents and well-being; in the 12th: expense) rewritten in warm, practical
language, never fear-based, with no medical or financial promises.
"""

from __future__ import annotations

import datetime as dt
import functools
import json
from dataclasses import dataclass

from fastapi import APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse

from . import seo_cities
from .astro import panchang as panchang_engine
from .astro.muhurat import NAKSHATRAS_HI, TITHI_HI, VARA_HI
from .chart_service import SIGNS
from .seo_pages import (
    ADSENSE_CLIENT, BRAND, IST, PAKSHA_HI, SITE_URL, _STYLE, _cache_headers, _clock, _e,
    _footer, _panchang, _today,
)

router = APIRouter()


# --------------------------------------------------------------------------
# Signs
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Rashi:
    index: int          # 0 = Aries, as chart_service.SIGNS
    slug: str           # the public URL segment — never rename one
    name: str           # Mesh
    name_hi: str        # मेष
    english: str        # Aries

    @property
    def english_slug(self) -> str:
        return self.english.lower()


RASHIS: tuple[Rashi, ...] = tuple(
    Rashi(i, slug, name, hi, SIGNS[i]) for i, (slug, name, hi) in enumerate((
        ("mesh", "Mesh", "मेष"), ("vrishabh", "Vrishabh", "वृषभ"),
        ("mithun", "Mithun", "मिथुन"), ("kark", "Kark", "कर्क"),
        ("simha", "Simha", "सिंह"), ("kanya", "Kanya", "कन्या"),
        ("tula", "Tula", "तुला"), ("vrishchik", "Vrishchik", "वृश्चिक"),
        ("dhanu", "Dhanu", "धनु"), ("makar", "Makar", "मकर"),
        ("kumbh", "Kumbh", "कुंभ"), ("meen", "Meen", "मीन"),
    )))
BY_SLUG = {r.slug: r for r in RASHIS}
BY_ENGLISH = {r.english_slug: r for r in RASHIS}

LANGS = ("en", "hi")

MONTHS_HI = ("जनवरी", "फ़रवरी", "मार्च", "अप्रैल", "मई", "जून", "जुलाई", "अगस्त",
             "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर")
HOUSE_HI = {1: "पहले", 2: "दूसरे", 3: "तीसरे", 4: "चौथे", 5: "पाँचवें", 6: "छठे",
            7: "सातवें", 8: "आठवें", 9: "नौवें", 10: "दसवें", 11: "ग्यारहवें", 12: "बारहवें"}
PLANET_HI = {"Moon": "चंद्रमा", "Saturn": "शनि", "Jupiter": "गुरु", "Rahu": "राहु", "Ketu": "केतु"}


def _ordinal(n: int) -> str:
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def house_from(rashi_index: int, sign_index: int) -> int:
    """The house `sign_index` occupies counted from `rashi_index` (1..12),
    inclusive counting as in every gochar table: the rashi itself is the 1st."""
    return (sign_index - rashi_index) % 12 + 1


def path(rashi: Rashi | None, lang: str) -> str:
    base = "/hi/rashifal" if lang == "hi" else "/rashifal"
    return f"{base}/{rashi.slug}" if rashi else base


def sitemap_paths() -> list[str]:
    """All 26 canonical URLs (index + 12 signs, in both languages)."""
    return [path(r, lang) for lang in LANGS for r in (None, *RASHIS)]


PUBLIC_PATHS = frozenset(sitemap_paths())


def is_public_path(p: str) -> bool:
    """For analytics.is_public_page: only the canonical URLs count."""
    return p in PUBLIC_PATHS


# --------------------------------------------------------------------------
# The phrase bank — see the module docstring for the classical scheme.
# --------------------------------------------------------------------------

GOOD, MIXED, EASY = "good", "mixed", "easy"
MOON_FAVOURABLE = frozenset({1, 3, 6, 7, 10, 11})
MOON_CHALLENGING = frozenset({4, 8, 12})
SATURN_FAVOURABLE = frozenset({3, 6, 11})
JUPITER_FAVOURABLE = frozenset({2, 5, 7, 9, 11})
NODE_FAVOURABLE = frozenset({3, 6, 11})
SADE_SATI = {12: 1, 1: 2, 2: 3}          # house of Saturn from the Moon sign -> phase
DHAIYA = frozenset({4, 8})

TONE_LABEL = {
    "en": {GOOD: "Favourable day", MIXED: "Mixed day", EASY: "Take it easy"},
    "hi": {GOOD: "अनुकूल दिन", MIXED: "मिश्रित दिन", EASY: "संयम का दिन"},
}


def moon_tone(house: int) -> str:
    return GOOD if house in MOON_FAVOURABLE else EASY if house in MOON_CHALLENGING else MIXED


MOON_HOUSE: dict[int, dict[str, str]] = {
    1: {"en": "The Moon moves through your own sign today (Janma Chandra). Classical texts read "
              "this as a day of comfort and good spirits — good food, warm company and a clear "
              "sense of yourself. A good day to look after your own needs and begin small, "
              "personal things.",
        "hi": "आज चंद्रमा आपकी अपनी राशि (जन्म राशि) में गोचर कर रहा है। शास्त्रों में इसे सुख और "
              "प्रसन्नता का दिन माना गया है — अच्छा भोजन, अपनों का साथ और मन में स्पष्टता। अपनी "
              "ज़रूरतों का ध्यान रखने और छोटे निजी काम शुरू करने के लिए अच्छा दिन है।"},
    2: {"en": "The Moon is in your 2nd house today. Tradition asks for care with money and words — "
              "expenses can creep up and small misunderstandings arise easily. Keep spending "
              "planned and speak gently at home; routine work goes fine.",
        "hi": "आज चंद्रमा आपकी राशि से दूसरे भाव में है। परंपरा के अनुसार आज धन और वाणी में "
              "सावधानी रखें — खर्च बढ़ सकते हैं और छोटी-छोटी गलतफ़हमियाँ हो सकती हैं। खर्च योजना से "
              "करें और घर में मधुर बोलें; नियमित काम ठीक चलेंगे।"},
    3: {"en": "The Moon in your 3rd house is a favourable transit. Courage and initiative are "
              "high, effort brings results, and contact with siblings, friends and neighbours "
              "goes well. A good day for short trips, calls and pushing a pending task over the "
              "line.",
        "hi": "चंद्रमा का तीसरे भाव में गोचर शुभ माना गया है। साहस और उत्साह बढ़ा रहेगा, प्रयासों का "
              "फल मिलेगा, और भाई-बहनों, मित्रों व पड़ोसियों से संपर्क अच्छा रहेगा। छोटी यात्रा, "
              "बातचीत और अटके काम पूरे करने के लिए अच्छा दिन है।"},
    4: {"en": "The Moon in your 4th house can leave the mind a little unsettled — home matters or "
              "travel may feel tiring. Keep the day simple, avoid arguments at home and give "
              "yourself some quiet time; the mood lifts as the Moon moves on.",
        "hi": "चौथे भाव में चंद्रमा मन को थोड़ा अशांत कर सकता है — घरेलू बातें या यात्रा थकाऊ लग "
              "सकती हैं। दिन को सरल रखें, घर में बहस से बचें और कुछ समय शांति से बिताएँ; चंद्रमा के "
              "आगे बढ़ते ही मन हल्का होगा।"},
    5: {"en": "The Moon in your 5th house is a mixed transit. Plans may meet small hurdles and "
              "the mind can swing between ideas. Avoid speculative decisions; study, creative "
              "work and time with children are better uses of the day.",
        "hi": "पाँचवें भाव में चंद्रमा मिश्रित फल देता है। योजनाओं में छोटी रुकावटें आ सकती हैं और "
              "मन विचारों में डोल सकता है। जोखिम भरे निर्णयों से बचें; पढ़ाई, रचनात्मक काम और बच्चों "
              "के साथ समय बिताना बेहतर रहेगा।"},
    6: {"en": "The Moon in your 6th house is one of its best transits. Classical texts promise "
              "success over rivals and obstacles, and the energy to clear a backlog. A good day "
              "for competitive work, settling pending issues and steady routines.",
        "hi": "छठे भाव में चंद्रमा का गोचर सबसे शुभ स्थितियों में गिना जाता है। शास्त्रों के अनुसार "
              "विरोधियों और बाधाओं पर विजय मिलती है और रुके काम निपटाने की ऊर्जा मिलती है। "
              "प्रतियोगिता, लंबित मामलों को सुलझाने और नियमित दिनचर्या के लिए अच्छा दिन है।"},
    7: {"en": "The Moon in your 7th house favours partnership and company. Time with your spouse "
              "or partner, meetings and agreements tend to go smoothly, with comfort and good "
              "food. A good day to reach out and work together.",
        "hi": "सातवें भाव में चंद्रमा साझेदारी और संगति के लिए अनुकूल है। जीवनसाथी के साथ समय, "
              "मुलाक़ातें और समझौते सहजता से होते हैं, साथ में सुख-सुविधा भी। मिल-जुलकर काम करने का "
              "अच्छा दिन है।"},
    8: {"en": "The Moon is in your 8th house — the period known as Chandrashtama. Tradition "
              "advises against starting important new things today; unexpected delays are more "
              "likely and the mind can feel anxious. Keep a margin in your schedule, stick to "
              "familiar work and be gentle with yourself — it passes within two to three days.",
        "hi": "आज चंद्रमा आपकी राशि से आठवें भाव में है — इसे चंद्राष्टम कहा जाता है। परंपरा के अनुसार "
              "आज कोई महत्वपूर्ण नया काम शुरू न करें; अचानक देरी हो सकती है और मन में चिंता रह सकती "
              "है। समय में गुंजाइश रखें, जाने-पहचाने काम करें और स्वयं के प्रति धैर्य रखें — यह दो-तीन "
              "दिन में बीत जाता है।"},
    9: {"en": "The Moon in your 9th house is a mixed transit. Plans may need extra effort and you "
              "may feel tired or distracted. Prayer, reading and time with elders or teachers "
              "suit the day better than big new ventures.",
        "hi": "नौवें भाव में चंद्रमा मिश्रित फल देता है। योजनाओं में अधिक मेहनत लग सकती है और थकान "
              "या ध्यान भटक सकता है। बड़े नए कामों की बजाय पूजा-पाठ, अध्ययन और बड़ों या गुरुजनों के "
              "साथ समय बिताना बेहतर रहेगा।"},
    10: {"en": "The Moon in your 10th house supports work and reputation. Tasks get done, seniors "
               "are receptive and effort is noticed. A good day to present your work, take a "
               "professional step or finish something visible.",
         "hi": "दसवें भाव में चंद्रमा कार्य और प्रतिष्ठा के लिए अनुकूल है। काम पूरे होंगे, वरिष्ठ लोग "
               "बात सुनेंगे और मेहनत दिखेगी। अपना काम प्रस्तुत करने या कार्यक्षेत्र में नया कदम उठाने "
               "के लिए अच्छा दिन है।"},
    11: {"en": "The Moon in your 11th house — the house of gains — is a very favourable transit. "
               "Expect support from friends, good news and the fruit of earlier effort. A good "
               "day for networking, making requests and celebrating with others.",
         "hi": "ग्यारहवें भाव (लाभ भाव) में चंद्रमा बहुत शुभ माना गया है। मित्रों का सहयोग, शुभ "
               "समाचार और पिछली मेहनत का फल मिल सकता है। मेल-जोल बढ़ाने, अनुरोध करने और अपनों के "
               "साथ ख़ुशी मनाने का अच्छा दिन है।"},
    12: {"en": "The Moon in your 12th house can bring extra expenses and a tired, inward mood. "
               "Avoid overspending and late nights; the day suits rest, prayer, charity and "
               "finishing old work rather than starting new.",
         "hi": "बारहवें भाव में चंद्रमा अतिरिक्त खर्च और थका हुआ, अंतर्मुखी मन दे सकता है। फ़िज़ूलखर्ची "
               "और देर रात जागने से बचें; आज नया शुरू करने की बजाय विश्राम, पूजा, दान और पुराने काम "
               "पूरे करना अच्छा रहेगा।"},
}

SATURN_HOUSE: dict[int, dict[str, str]] = {
    1: {"en": "Saturn is passing over your Moon sign — the peak phase of Sade Sati. It rewards "
              "patience, routine and honest effort; take on a little less and finish what you "
              "start.",
        "hi": "शनि आपकी चंद्र राशि पर गोचर कर रहे हैं — साढ़ेसाती का मध्य (चरम) चरण। यह समय धैर्य, "
              "नियमितता और ईमानदार मेहनत का फल देता है; थोड़ा कम काम हाथ में लें और जो शुरू करें उसे "
              "पूरा करें।"},
    2: {"en": "Saturn is in your 2nd — the last phase of Sade Sati. Be measured with spending and "
              "with words at home; the pressure is easing.",
        "hi": "शनि दूसरे भाव में हैं — साढ़ेसाती का अंतिम चरण। घर में खर्च और वाणी संयमित रखें; दबाव "
              "धीरे-धीरे कम हो रहा है।"},
    3: {"en": "Saturn in your 3rd is one of its best positions — steady effort pays, courage grows "
              "and long-running work gains traction.",
        "hi": "शनि तीसरे भाव में हैं — शनि की सबसे शुभ स्थितियों में से एक। लगातार प्रयास फल देते हैं, "
              "साहस बढ़ता है और लंबे समय से चल रहे काम गति पकड़ते हैं।"},
    4: {"en": "Saturn in your 4th (Dhaiya, Kantaka Shani) can make home life and peace of mind feel "
              "heavier; keep routines simple and handle family matters calmly.",
        "hi": "शनि चौथे भाव में हैं (ढैया, कंटक शनि) — घर और मन की शांति पर बोझ महसूस हो सकता है; "
              "दिनचर्या सरल रखें और पारिवारिक बातें शांति से सँभालें।"},
    5: {"en": "Saturn in your 5th asks for patience with plans, studies and children's matters — "
              "slow and careful beats quick.",
        "hi": "शनि पाँचवें भाव में हैं — योजनाओं, पढ़ाई और संतान संबंधी बातों में धैर्य रखें; जल्दबाज़ी "
              "से अच्छा है धीमे और सोच-समझकर चलना।"},
    6: {"en": "Saturn in your 6th works in your favour — discipline wins over rivals and backlog, "
              "and hard work gets noticed.",
        "hi": "शनि छठे भाव में आपके पक्ष में हैं — अनुशासन से विरोधियों और अटके कामों पर जीत मिलती है, "
              "और मेहनत पर लोगों की नज़र जाती है।"},
    7: {"en": "Saturn in your 7th puts partnerships in a slow, serious light — clear agreements "
              "and patience help.",
        "hi": "शनि सातवें भाव में हैं — साझेदारी और संबंधों में गंभीरता आती है; स्पष्ट बातचीत और धैर्य "
              "सहायक हैं।"},
    8: {"en": "Saturn in your 8th (Dhaiya, Ashtama Shani) is a time to avoid shortcuts and keep a "
              "margin for delays.",
        "hi": "शनि आठवें भाव में हैं (ढैया, अष्टम शनि) — शॉर्टकट से बचें और देरी के लिए समय की "
              "गुंजाइश रखें।"},
    9: {"en": "Saturn in your 9th can slow luck and long journeys; respect for elders and steady "
              "duty keep things on track.",
        "hi": "शनि नौवें भाव में भाग्य और लंबी यात्राओं को धीमा कर सकते हैं; बड़ों का सम्मान और "
              "कर्तव्य-पालन चीज़ों को पटरी पर रखते हैं।"},
    10: {"en": "Saturn in your 10th brings responsibility at work — a heavier load, but sincere "
               "effort builds a lasting reputation.",
         "hi": "शनि दसवें भाव में हैं — कार्यक्षेत्र में ज़िम्मेदारी बढ़ती है; भार अधिक है, पर सच्ची "
               "मेहनत स्थायी प्रतिष्ठा बनाती है।"},
    11: {"en": "Saturn in your 11th is favourable — gains come slowly but surely, and long effort "
               "starts to pay off.",
         "hi": "शनि ग्यारहवें भाव में शुभ हैं — लाभ धीरे-धीरे पर पक्के तौर पर आता है और लंबी मेहनत का "
               "फल मिलने लगता है।"},
    12: {"en": "Saturn is in your 12th — the opening phase of Sade Sati. Watch expenses and rest "
               "well; a good time for quiet, inward work.",
         "hi": "शनि बारहवें भाव में हैं — साढ़ेसाती का पहला चरण। खर्चों पर नज़र रखें और पर्याप्त विश्राम "
               "करें; शांत, आत्मचिंतन वाले काम के लिए अच्छा समय।"},
}

JUPITER_HOUSE: dict[int, dict[str, str]] = {
    1: {"en": "Jupiter over your Moon sign is classically a restless position; keep plans "
              "grounded and avoid over-committing.",
        "hi": "गुरु आपकी चंद्र राशि पर हैं — शास्त्रों में इसे अस्थिरता की स्थिति माना गया है; योजनाएँ "
              "व्यावहारिक रखें और ज़रूरत से ज़्यादा वादे न करें।"},
    2: {"en": "Jupiter in your 2nd supports family harmony, savings and kind speech.",
        "hi": "गुरु दूसरे भाव में पारिवारिक सौहार्द, बचत और मधुर वाणी को बल देते हैं।"},
    3: {"en": "Jupiter in your 3rd asks a little more effort for the same result — keep at it.",
        "hi": "गुरु तीसरे भाव में हैं — उसी परिणाम के लिए थोड़ी अधिक मेहनत लगती है; लगे रहें।"},
    4: {"en": "Jupiter in your 4th can unsettle home matters; patience with relatives helps.",
        "hi": "गुरु चौथे भाव में घरेलू मामलों में उतार-चढ़ाव ला सकते हैं; रिश्तेदारों के साथ धैर्य रखें।"},
    5: {"en": "Jupiter in your 5th favours learning, children's matters, creativity and good "
              "counsel.",
        "hi": "गुरु पाँचवें भाव में विद्या, संतान, रचनात्मकता और अच्छी सलाह के लिए शुभ हैं।"},
    6: {"en": "Jupiter in your 6th: steer clear of small disputes and overwork.",
        "hi": "गुरु छठे भाव में हैं — छोटे विवादों और काम के अधिक बोझ से बचें।"},
    7: {"en": "Jupiter in your 7th blesses partnerships, marriage talks and travel.",
        "hi": "गुरु सातवें भाव में साझेदारी, विवाह की बातचीत और यात्रा के लिए शुभ हैं।"},
    8: {"en": "Jupiter in your 8th suggests care with big decisions — go slow.",
        "hi": "गुरु आठवें भाव में हैं — बड़े निर्णयों में सावधानी रखें; धीरे चलें।"},
    9: {"en": "Jupiter in your 9th is one of its best positions — fortune, dharma and guidance "
              "from teachers.",
        "hi": "गुरु नौवें भाव में हैं — सबसे शुभ स्थितियों में से एक: भाग्य, धर्म और गुरुजनों का "
              "मार्गदर्शन।"},
    10: {"en": "Jupiter in your 10th may bring changes at work; stay adaptable.",
         "hi": "गुरु दसवें भाव में कार्यक्षेत्र में बदलाव ला सकते हैं; लचीले रहें।"},
    11: {"en": "Jupiter in your 11th brings gains, fulfilled wishes and helpful friends.",
         "hi": "गुरु ग्यारहवें भाव में लाभ, इच्छापूर्ति और मित्रों का सहयोग देते हैं।"},
    12: {"en": "Jupiter in your 12th brings expenses, often on good causes; charity and spiritual "
               "practice are well placed.",
         "hi": "गुरु बारहवें भाव में खर्च कराते हैं, अक्सर अच्छे कामों पर; दान और आध्यात्मिक साधना "
               "शुभ है।"},
}

RAHU_HOUSE: dict[int, dict[str, str]] = {
    1: {"en": "Rahu over your Moon sign can stir restlessness and unusual wants; stay grounded.",
        "hi": "राहु आपकी चंद्र राशि पर बेचैनी और असामान्य इच्छाएँ जगा सकते हैं; ज़मीन से जुड़े रहें।"},
    2: {"en": "Rahu in your 2nd: take care with speech and money talk within the family.",
        "hi": "राहु दूसरे भाव में हैं — परिवार में धन और वाणी के मामलों में सावधानी रखें।"},
    3: {"en": "Rahu in your 3rd is favourable — bold initiatives and communication succeed.",
        "hi": "राहु तीसरे भाव में शुभ हैं — साहसिक पहल और संवाद सफल होते हैं।"},
    4: {"en": "Rahu in your 4th can unsettle domestic peace; avoid hasty property moves.",
        "hi": "राहु चौथे भाव में घरेलू शांति को हिला सकते हैं; संपत्ति संबंधी जल्दबाज़ी से बचें।"},
    5: {"en": "Rahu in your 5th: double-check risky ideas and keep a clear head.",
        "hi": "राहु पाँचवें भाव में हैं — जोखिम भरे विचारों को दोबारा जाँचें; मन स्पष्ट रखें।"},
    6: {"en": "Rahu in your 6th helps you get past competition and obstacles.",
        "hi": "राहु छठे भाव में प्रतियोगिता और बाधाओं पर विजय दिलाते हैं।"},
    7: {"en": "Rahu in your 7th: keep partnerships transparent.",
        "hi": "राहु सातवें भाव में हैं — साझेदारी में पारदर्शिता रखें।"},
    8: {"en": "Rahu in your 8th: avoid risky shortcuts and stay calm when the unexpected comes.",
        "hi": "राहु आठवें भाव में हैं — जोखिम भरे शॉर्टकट से बचें; अनपेक्षित स्थितियों में शांत रहें।"},
    9: {"en": "Rahu in your 9th can raise doubts about beliefs or mentors; seek advice you trust.",
        "hi": "राहु नौवें भाव में आस्था या मार्गदर्शकों को लेकर संदेह ला सकते हैं; भरोसेमंद सलाह लें।"},
    10: {"en": "Rahu in your 10th brings ambition and sudden openings at work; move with "
               "integrity.",
         "hi": "राहु दसवें भाव में महत्वाकांक्षा और कार्यक्षेत्र में अचानक अवसर लाते हैं; ईमानदारी से "
               "आगे बढ़ें।"},
    11: {"en": "Rahu in your 11th — gains through networks and new contacts.",
         "hi": "राहु ग्यारहवें भाव में हैं — नए संपर्कों और नेटवर्क से लाभ।"},
    12: {"en": "Rahu in your 12th: watch hidden expenses and get proper rest.",
         "hi": "राहु बारहवें भाव में हैं — छिपे खर्चों पर नज़र रखें और पूरा विश्राम लें।"},
}

KETU_LINE = {
    True: {"en": "Ketu in your {n} house works quietly in your favour — obstacles clear with "
                 "less fuss.",
           "hi": "केतु {n} भाव में अनुकूल हैं — बाधाएँ कम झंझट में दूर होती हैं।"},
    False: {"en": "Ketu in your {n} house is a quieter, inward influence — good for reflection "
                  "and spiritual practice, less so for impulsive moves.",
            "hi": "केतु {n} भाव में हैं — अंतर्मुखी प्रभाव; आत्मचिंतन और साधना के लिए अच्छा, "
                  "जल्दबाज़ी के कदमों के लिए कम।"},
}


def _house_word(n: int, lang: str) -> str:
    return HOUSE_HI[n] if lang == "hi" else _ordinal(n)


# --------------------------------------------------------------------------
# The sky for one IST day
# --------------------------------------------------------------------------

@functools.lru_cache(maxsize=16)
def sky(day: dt.date) -> dict:
    """Sidereal (Lahiri) positions for the IST civil day `day`.

    The Moon is checked at 00:00 and just before 24:00 IST; it spends ~2¼ days
    in a sign, so it changes sign at most once a day, and the instant is found
    by bisection to the second. Saturn, Jupiter and the (mean) nodes are read at
    12:00 IST — they move a few arc-minutes a day, and the very rare day one of
    them changes sign is described by its noon position.
    """
    pe = panchang_engine
    pe._ephemeris()
    swe = pe.swe
    aya = pe.DEFAULT_AYANAMSA

    def lon(jd: float, body: int) -> float:
        return pe._sidereal(jd, body, aya)

    start = dt.datetime.combine(day, dt.time(), IST)
    jd0 = pe._to_jd(start)
    jd1 = pe._to_jd(start + dt.timedelta(days=1)) - 1e-7
    first = int(lon(jd0, swe.MOON) // 30)
    last = int(lon(jd1, swe.MOON) // 30)
    segments = [{"sign": first, "from": None, "until": None}]
    if last != first:
        lo, hi = jd0, jd1
        while hi - lo > pe._TOLERANCE_DAYS:
            mid = (lo + hi) / 2
            if int(lon(mid, swe.MOON) // 30) == first:
                lo = mid
            else:
                hi = mid
        change = pe._from_jd(hi, IST)
        segments[0]["until"] = change
        segments.append({"sign": last, "from": change, "until": None})

    noon = pe._to_jd(start + dt.timedelta(hours=12))
    rahu = lon(noon, swe.MEAN_NODE)

    def slow(body: int) -> dict:
        speed = swe.calc_ut(noon, body, swe.FLG_SWIEPH | swe.FLG_SPEED)[0][3]
        return {"sign": int(lon(noon, body) // 30), "retrograde": speed < 0}

    p = _panchang(seo_cities.DEFAULT.slug, day)
    return {
        "day": day,
        "moon": segments,
        "saturn": slow(swe.SATURN),
        "jupiter": slow(swe.JUPITER),
        "rahu": {"sign": int(rahu // 30)},
        "ketu": {"sign": int(((rahu + 180.0) % 360.0) // 30)},
        "panchang": p,
    }


def main_moon(s: dict) -> dict:
    """The Moon segment that covers more of the day (for titles and summaries)."""
    segs = s["moon"]
    if len(segs) == 1:
        return segs[0]
    change = segs[0]["until"]
    return segs[0] if change.hour * 60 + change.minute >= 720 else segs[1]


def reading(rashi: Rashi, day: dt.date) -> dict:
    """Every computed fact the page shows for one rashi, before rendering."""
    s = sky(day)
    moon = [{**seg, "house": house_from(rashi.index, seg["sign"])} for seg in s["moon"]]
    main = house_from(rashi.index, main_moon(s)["sign"])
    sat = house_from(rashi.index, s["saturn"]["sign"])
    return {
        "moon": moon,
        "main_house": main,
        "tone": moon_tone(main),
        "saturn": sat,
        "jupiter": house_from(rashi.index, s["jupiter"]["sign"]),
        "rahu": house_from(rashi.index, s["rahu"]["sign"]),
        "ketu": house_from(rashi.index, s["ketu"]["sign"]),
        "sade_sati_phase": SADE_SATI.get(sat),
        "dhaiya": sat in DHAIYA,
    }


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------

_EXTRA_STYLE = """
  .seo .tone { display: inline-block; padding: 3px 10px; border-radius: 999px; font-size: 13px;
               border: 1px solid var(--line); margin-left: 6px; }
  .seo .tone.good { color: var(--green); border-color: var(--green); }
  .seo .tone.easy { color: var(--rose); border-color: var(--rose); }
  .seo .tone.mixed { color: var(--gold); border-color: var(--gold); }
  .seo .note { font-size: 13.5px; color: var(--ink-faint); }
"""

_SHELL = """<!DOCTYPE html>
<html lang="{html_lang}"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{title}</title>
<meta name="description" content="{description}"/>
<link rel="canonical" href="{canonical}"/>
<link rel="alternate" hreflang="en-IN" href="{alt_en}"/>
<link rel="alternate" hreflang="hi-IN" href="{alt_hi}"/>
<link rel="alternate" hreflang="x-default" href="{alt_en}"/>
<meta property="og:type" content="article"/>
<meta property="og:site_name" content="{brand}"/>
<meta property="og:title" content="{title}"/>
<meta property="og:description" content="{description}"/>
<meta property="og:url" content="{canonical}"/>
<meta property="og:image" content="{site}/static/icon-512.png"/>
<meta property="og:locale" content="{og_locale}"/>
<meta name="twitter:card" content="summary"/>
<meta name="google-adsense-account" content="{adsense}"/>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={adsense}"
        crossorigin="anonymous"></script>
<script src="/static/visit.js" defer></script>   <!-- counts the page load: see analytics.py -->
<link rel="icon" href="/static/favicon.ico"/>
<link rel="apple-touch-icon" href="/static/apple-touch-icon.png"/>
<link rel="stylesheet" href="/static/styles.css"/>
<style>{style}</style>
<script type="application/ld+json">{jsonld}</script>
</head>
<body class="sacred">
<main class="seo">
  <a class="back" href="/">&larr; {brand}</a>
  <nav class="crumbs" aria-label="Breadcrumb">{crumbs}</nav>
  {body}
</main>
{footer}
</body></html>"""


def _date_text(day: dt.date, lang: str, short: bool = False) -> str:
    if lang == "hi":
        return f"{day.day} {MONTHS_HI[day.month - 1]} {day.year}"
    return f"{day.day} {day.strftime('%b' if short else '%B')} {day.year}"


def _weekday(day: dt.date, lang: str) -> str:
    name = day.strftime("%A")
    return VARA_HI.get(name, name) if lang == "hi" else name


def _shell(*, lang: str, rashi: Rashi | None, title: str, description: str,
           crumbs: list[tuple[str, str]], body: str, day: dt.date,
           status: int = 200, cache: bool = True) -> HTMLResponse:
    canonical = SITE_URL + path(rashi, lang)
    trail = [("मुख्य पृष्ठ" if lang == "hi" else "Home", "/")] + crumbs
    crumb_html = " › ".join(
        f'<a href="{_e(href)}">{_e(name)}</a>' if i < len(trail) - 1 else _e(name)
        for i, (name, href) in enumerate(trail))
    in_lang = "hi-IN" if lang == "hi" else "en-IN"
    graph = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "WebPage", "name": title, "description": description, "url": canonical,
             "inLanguage": in_lang, "datePublished": day.isoformat(),
             "dateModified": day.isoformat(),
             "isPartOf": {"@type": "WebSite", "name": BRAND, "url": SITE_URL + "/"}},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": name, "item": SITE_URL + href}
                for i, (name, href) in enumerate(trail)]},
        ],
    }
    jsonld = json.dumps(graph, ensure_ascii=False).replace("</", "<\\/")
    page = _SHELL.format(
        html_lang=in_lang, title=_e(title), description=_e(description),
        canonical=_e(canonical), alt_en=_e(SITE_URL + path(rashi, "en")),
        alt_hi=_e(SITE_URL + path(rashi, "hi")), og_locale="hi_IN" if lang == "hi" else "en_IN",
        brand=_e(BRAND), site=_e(SITE_URL), adsense=ADSENSE_CLIENT,
        style=_STYLE + _EXTRA_STYLE, jsonld=jsonld, crumbs=crumb_html, body=body,
        footer=_footer(lang))
    headers = _cache_headers() if cache else {"Cache-Control": "no-store"}
    return HTMLResponse(page, status_code=status, headers=headers)


def _sign_label(index: int, lang: str) -> str:
    r = RASHIS[index]
    return f"{r.name_hi} ({r.name})" if lang == "hi" else f"{r.english} ({r.name})"


def _sign_links(current: Rashi | None, lang: str) -> str:
    items = "".join(
        f'<li><a href="{path(r, lang)}"' + (' aria-current="page"' if r == current else "")
        + f'>{_e(r.name_hi if lang == "hi" else f"{r.name} · {r.english}")}</a></li>'
        for r in RASHIS)
    head = "अन्य राशियों का आज का राशिफल" if lang == "hi" else "Today's Rashifal for every sign"
    return f'<h2>{head}</h2><ul class="links">{items}</ul>'


def _more_links(rashi: Rashi | None, lang: str) -> str:
    if lang == "hi":
        links = [(path(rashi, "en"), "Read in English"), ("/panchang", "आज का पंचांग"),
                 ("/rahu-kaal", "आज का राहु काल"), ("/choghadiya", "आज का चौघड़िया"),
                 ("/kundali-milan", "कुंडली मिलान")]
        head = "और भी"
    else:
        links = [(path(rashi, "hi"), "हिन्दी में पढ़ें"), ("/panchang", "Today's Panchang"),
                 ("/rahu-kaal", "Rahu Kaal today"), ("/choghadiya", "Choghadiya today"),
                 ("/kundali-milan", "Kundali Milan")]
        head = "More free tools"
    items = "".join(f'<li><a href="{_e(h)}">{_e(t)}</a></li>' for h, t in links)
    return f'<h2>{head}</h2><ul class="links">{items}</ul>'


def _cta(lang: str) -> str:
    """Into the birth form (tools.js `?open=kundali` clicks the home CTA). A
    question needs a chart first, so the kundali is the one door for both."""
    text = ("अपनी मुफ़्त कुंडली बनाएँ — फिर अपनी कुंडली पर प्रश्न पूछें" if lang == "hi"
            else "Get your free kundali — then ask a question about your own chart")
    return f'<a class="cta" href="/?open=kundali">{_e(text)}</a>'


def _personal_line(lang: str) -> str:
    if lang == "hi":
        return ("<p class=\"note\">यह राशिफल केवल आपकी चंद्र राशि से चंद्रमा, शनि, गुरु और "
                "राहु-केतु के गोचर पर आधारित है — एक ही राशि वाले सभी लोगों के लिए समान। व्यक्तिगत "
                "फलादेश आपकी पूरी जन्म कुंडली — लग्न, दशा और अष्टकवर्ग — से होता है। अपनी चंद्र "
                "राशि नहीं पता? आपकी मुफ़्त कुंडली में यह सबसे ऊपर दिखती है।</p>")
    return ("<p class=\"note\">This rashifal is read from your Moon sign alone — the same for "
            "everyone born with the Moon in that sign. A personal reading uses your full birth "
            "chart: the ascendant, your running dasha and the ashtakavarga strength of each "
            "transit. Not sure of your Moon sign (rashi)? It is the first thing your free kundali "
            "shows — it is usually not your Western sun sign.</p>")


def _time(moment: dt.datetime, day: dt.date) -> str:
    text = _clock(moment)
    return text if moment.date() == day else f"{text} ({moment.day} {moment.strftime('%b')})"


def _moon_section(rashi: Rashi, r: dict, day: dt.date, lang: str) -> str:
    hi = lang == "hi"
    moon = r["moon"]
    parts = []
    for seg in moon:
        h = seg["house"]
        sign = _sign_label(seg["sign"], lang)
        if len(moon) == 1:
            lead = (f"आज पूरे दिन चंद्रमा {_e(sign)} में है — आपकी राशि से {HOUSE_HI[h]} भाव में।"
                    if hi else f"The Moon is in {_e(sign)} all day — your {_ordinal(h)} house.")
        elif seg["until"]:
            t = _time(seg["until"], day)
            lead = (f"<strong>{t} (IST) तक:</strong> चंद्रमा {_e(sign)} में — आपकी राशि से "
                    f"{HOUSE_HI[h]} भाव में।" if hi else
                    f"<strong>Until {t} IST:</strong> the Moon is in {_e(sign)} — your "
                    f"{_ordinal(h)} house.")
        else:
            t = _time(seg["from"], day)
            lead = (f"<strong>{t} (IST) से:</strong> चंद्रमा {_e(sign)} में प्रवेश करता है — आपकी "
                    f"राशि से {HOUSE_HI[h]} भाव में।" if hi else
                    f"<strong>From {t} IST:</strong> the Moon enters {_e(sign)} — your "
                    f"{_ordinal(h)} house.")
        tone = moon_tone(h)
        parts.append(f'<p>{lead} <span class="tone {tone}">{_e(TONE_LABEL[lang][tone])}</span></p>'
                     f"<p>{_e(MOON_HOUSE[h][lang])}</p>")
    if len(moon) > 1:
        intro = ("<p>आज दिन में चंद्रमा राशि बदलता है, इसलिए दिन के दो हिस्से अलग पढ़ें।</p>" if hi
                 else "<p>The Moon changes sign during the day, so the day reads in two parts.</p>")
        parts.insert(0, intro)
    head = "आज चंद्रमा का गोचर (चंद्र गोचर)" if hi else "Today's Moon transit (Chandra gochar)"
    return f"<h2>{head}</h2>" + "".join(parts)


def _backdrop_section(r: dict, s: dict, lang: str) -> str:
    hi = lang == "hi"
    rows = []

    def row(planet: str, sign_index: int, house: int, text: str, retro: bool = False) -> None:
        name = PLANET_HI[planet] if hi else planet
        rx = (" (वक्री)" if hi else " (retrograde)") if retro else ""
        where = (f"{_e(_sign_label(sign_index, lang))}{rx} · {HOUSE_HI[house]} भाव" if hi
                 else f"{_e(_sign_label(sign_index, lang))}{rx} · {_ordinal(house)} house")
        rows.append(f'<tr><th scope="row">{_e(name)}<small>{where}</small></th>'
                    f"<td>{_e(text)}</td></tr>")

    row("Saturn", s["saturn"]["sign"], r["saturn"], SATURN_HOUSE[r["saturn"]][lang],
        s["saturn"]["retrograde"])
    row("Jupiter", s["jupiter"]["sign"], r["jupiter"], JUPITER_HOUSE[r["jupiter"]][lang],
        s["jupiter"]["retrograde"])
    row("Rahu", s["rahu"]["sign"], r["rahu"], RAHU_HOUSE[r["rahu"]][lang])
    ketu = KETU_LINE[r["ketu"] in NODE_FAVOURABLE][lang].format(n=_house_word(r["ketu"], lang))
    row("Ketu", s["ketu"]["sign"], r["ketu"], ketu)

    phase = r["sade_sati_phase"]
    if phase:
        names_hi = {1: "पहला (आरंभ)", 2: "दूसरा (मध्य)", 3: "तीसरा (अंतिम)"}
        names_en = {1: "first (rising)", 2: "second (peak)", 3: "third (setting)"}
        status = (f"<strong>साढ़ेसाती चल रही है</strong> — {names_hi[phase]} चरण। यह धीमी, "
                  "अनुशासन सिखाने वाली अवधि है, डरने की नहीं; नियमित दिनचर्या, सेवा और धैर्य "
                  "इसे हल्का करते हैं।" if hi else
                  f"<strong>Sade Sati is running</strong> — the {names_en[phase]} phase. It is a "
                  "slow, disciplining period rather than something to fear; steady routine, "
                  "service and patience make it lighter.")
    elif r["dhaiya"]:
        status = ("<strong>साढ़ेसाती नहीं</strong>, पर शनि की ढैया चल रही है (ऊपर देखें)।" if hi
                  else "<strong>No Sade Sati</strong>, but Saturn's Dhaiya is running (see above).")
    else:
        status = ("<strong>साढ़ेसाती नहीं</strong> — शनि आपकी राशि से 12वें, पहले या दूसरे भाव में "
                  "नहीं हैं।" if hi else
                  "<strong>No Sade Sati</strong> — Saturn is not in the 12th, 1st or 2nd from "
                  "your sign.")
    head = "लंबी अवधि का गोचर" if hi else "The longer backdrop: slow transits"
    intro = ("<p>ये ग्रह महीनों या वर्षों तक एक राशि में रहते हैं, इसलिए ये रोज़ के दिन की "
             "पृष्ठभूमि बनाते हैं।</p>" if hi else
             "<p>These planets stay in one sign for months or years, so they set the background "
             "against which each day plays out.</p>")
    return (f"<h2>{head}</h2>{intro}<div class=\"scroll\"><table>{''.join(rows)}</table></div>"
            f'<div class="box"><p>{status}</p></div>')


def _panchang_line(s: dict, day: dt.date, lang: str) -> str:
    p = s["panchang"]
    summ = p["summary"]
    paksha, tithi, nak = summ["paksha"] or "", summ["tithi"] or "", summ["nakshatra"] or ""
    if lang == "hi":
        return ("<h2>आज का पंचांग</h2><p>नई दिल्ली में सूर्योदय के समय "
                f"<strong>{_e(PAKSHA_HI.get(paksha, paksha))} {_e(TITHI_HI.get(tithi, tithi))}</strong> "
                f"तिथि और <strong>{_e(NAKSHATRAS_HI.get(nak, nak))}</strong> नक्षत्र है। राहु काल, "
                'सूर्योदय और पूरा पंचांग <a href="/panchang">आज के पंचांग</a> में देखें।</p>')
    return ("<h2>Today's Panchang</h2><p>At sunrise in New Delhi it is "
            f"<strong>{_e(paksha)} {_e(tithi)}</strong> tithi with the Moon in "
            f"<strong>{_e(nak)}</strong> nakshatra. Rahu Kaal, sunrise and the full almanac are "
            'on <a href="/panchang">today\'s Panchang</a>.</p>')


def _method_note(lang: str) -> str:
    if lang == "hi":
        return ("<h2>यह कैसे निकाला गया</h2><p>ग्रहों की स्थिति आज (भारतीय मानक समय) के लिए स्विस "
                "एफ़ेमेरिस से निरयण (लाहिड़ी अयनांश) पद्धति में गणना की गई है — वही जो हमारी कुंडली और "
                "पंचांग में प्रयुक्त है। भाव आपकी चंद्र राशि से गिने गए हैं (गोचर)। शुभ-अशुभ का आधार "
                "वराहमिहिर की बृहत्संहिता (अध्याय 104) और मंत्रेश्वर की फलदीपिका (अध्याय 26) की "
                "शास्त्रीय गोचर पद्धति है: चंद्रमा 1, 3, 6, 7, 10, 11वें भाव में शुभ; शनि और "
                "राहु-केतु 3, 6, 11वें में; गुरु 2, 5, 7, 9, 11वें में।</p>")
    return ("<h2>How this is calculated</h2><p>Planet positions are computed for today (IST) "
            "with the Swiss Ephemeris in the sidereal zodiac (Lahiri ayanamsa) — the same "
            "positions our kundali and panchang use. Houses are counted from your Moon sign, as "
            "in classical gochar. Which houses are favourable follows the scheme of Varahamihira's "
            "Brihat Samhita (ch. 104) and Mantreswara's Phaladeepika (ch. 26): the Moon is "
            "favourable in the 1st, 3rd, 6th, 7th, 10th and 11th; Saturn, Rahu and Ketu in the "
            "3rd, 6th and 11th; Jupiter in the 2nd, 5th, 7th, 9th and 11th.</p>")


@functools.lru_cache(maxsize=128)
def _sign_page(day: dt.date, slug: str, lang: str) -> tuple[str, str, str, str]:
    """(title, description, body, h1-crumb) for one sign — cached per (date, sign, lang)."""
    rashi = BY_SLUG[slug]
    s = sky(day)
    r = reading(rashi, day)
    hi = lang == "hi"
    main = r["main_house"]
    tone = TONE_LABEL[lang][r["tone"]]
    if hi:
        title = (f"आज का {rashi.name_hi} राशिफल, {_date_text(day, lang)} — {rashi.name} Rashifal "
                 f"Today | {BRAND}")
        description = (f"{rashi.name_hi} राशि का आज का राशिफल ({_weekday(day, lang)}, "
                       f"{_date_text(day, lang)}): चंद्रमा आपकी राशि से {HOUSE_HI[main]} भाव में — "
                       f"{tone}। साथ में शनि, गुरु, राहु-केतु का गोचर, साढ़ेसाती की स्थिति और आज का "
                       "पंचांग।")
    else:
        title = (f"{rashi.name} Rashifal Today, {_date_text(day, lang, short=True)} — "
                 f"{rashi.english} Daily Horoscope | {BRAND}")
        description = (f"{rashi.name} ({rashi.english} Moon sign) rashifal for {_weekday(day, lang)}, "
                       f"{_date_text(day, lang)}: the Moon transits your {_ordinal(main)} house — "
                       f"{tone.lower()}. Plus Saturn, Jupiter and Rahu–Ketu transits, Sade Sati "
                       "status and today's tithi, computed from the sidereal sky.")
    h1 = (f"आज का {rashi.name_hi} राशिफल" if hi else
          f"{rashi.name} Rashifal Today — {rashi.english} Daily Horoscope")
    sub = (f"{rashi.name} Rashifal · {rashi.english}" if hi else
           f"आज का {rashi.name_hi} राशिफल")
    sub_lang = "en" if hi else "hi"
    summary_box = (
        f'<div class="box"><p><strong>{_e(tone)}</strong> — '
        + (f"चंद्रमा आपकी राशि से {HOUSE_HI[main]} भाव में।" if hi
           else f"the Moon is in your {_ordinal(main)} house from {_e(rashi.name)}.")
        + "</p></div>")
    body = f"""
<h1>{_e(h1)}</h1>
<p class="hi" lang="{sub_lang}">{_e(sub)}</p>
<p class="date">{_e(_weekday(day, lang))}, {_e(_date_text(day, lang))} · IST</p>
{summary_box}
{_moon_section(rashi, r, day, lang)}
{_backdrop_section(r, s, lang)}
{_panchang_line(s, day, lang)}
{_personal_line(lang)}
{_cta(lang)}
{_sign_links(rashi, lang)}
{_method_note(lang)}
{_more_links(rashi, lang)}"""
    return title, description, body, (rashi.name_hi if hi else rashi.name)


@functools.lru_cache(maxsize=8)
def _index_page(day: dt.date, lang: str) -> tuple[str, str, str]:
    s = sky(day)
    hi = lang == "hi"
    rows = []
    for rashi in RASHIS:
        r = reading(rashi, day)
        h = r["main_house"]
        name = (f"{rashi.name_hi} <small>{_e(rashi.name)}</small>" if hi
                else f"{_e(rashi.name)} <small>{_e(rashi.english)}</small>")
        where = f"{HOUSE_HI[h]} भाव" if hi else f"{_ordinal(h)} house"
        sade = ""
        if r["sade_sati_phase"]:
            sade = "<small>साढ़ेसाती</small>" if hi else "<small>Sade Sati</small>"
        rows.append(f'<tr><td><a href="{path(rashi, lang)}">{name}</a></td><td>{where}</td>'
                    f'<td class="{"good" if r["tone"] == GOOD else "bad" if r["tone"] == EASY else ""}">'
                    f'{_e(TONE_LABEL[lang][r["tone"]])}{sade}</td></tr>')
    head_row = ("<tr><th>राशि</th><th>चंद्रमा</th><th>आज</th></tr>" if hi
                else "<tr><th>Sign</th><th>Moon in your</th><th>Today</th></tr>")
    segs = s["moon"]
    moon_now = _sign_label(segs[0]["sign"], lang)
    if len(segs) > 1:
        t = _time(segs[0]["until"], day)
        nxt = _sign_label(segs[1]["sign"], lang)
        moon_text = (f"चंद्रमा {t} (IST) तक {_e(moon_now)} में, फिर {_e(nxt)} में। तालिका दिन के "
                     "अधिकांश भाग वाली स्थिति दिखाती है।" if hi else
                     f"The Moon is in {_e(moon_now)} until {t} IST, then in {_e(nxt)}. The table "
                     "shows the position for most of the day.")
    else:
        moon_text = (f"आज पूरे दिन चंद्रमा {_e(moon_now)} में है।" if hi
                     else f"The Moon is in {_e(moon_now)} all day.")
    sade_signs = [RASHIS[(s["saturn"]["sign"] + k) % 12] for k in (1, 0, -1)]
    sade_names = ", ".join((x.name_hi if hi else x.name) for x in sade_signs)
    sat_sign = _sign_label(s["saturn"]["sign"], lang)
    if hi:
        title = (f"आज का राशिफल, {_date_text(day, lang)} — सभी 12 राशियों का दैनिक राशिफल | "
                 f"{BRAND}")
        description = (f"आज का राशिफल ({_weekday(day, lang)}, {_date_text(day, lang)}) मेष से मीन "
                       "तक सभी 12 राशियों के लिए — चंद्र गोचर, शनि-गुरु-राहु का प्रभाव और साढ़ेसाती, "
                       "निरयण (लाहिड़ी) गणना पर आधारित।")
        intro = (f"<p>राशिफल आपकी <strong>चंद्र राशि</strong> से पढ़ा जाता है। {moon_text} शनि "
                 f"{_e(sat_sign)} में हैं, इसलिए {_e(sade_names)} राशि वालों की साढ़ेसाती चल रही है।</p>")
        h1, sub = "आज का राशिफल", "Aaj ka Rashifal — today's horoscope for all 12 signs"
    else:
        title = (f"Aaj Ka Rashifal, {_date_text(day, lang, short=True)} — Today's Horoscope for "
                 f"All 12 Signs | {BRAND}")
        description = (f"Today's rashifal for {_weekday(day, lang)}, {_date_text(day, lang)}: "
                       "daily horoscope for all 12 Moon signs from Mesh to Meen — Moon transit, "
                       "Saturn, Jupiter and Rahu, and Sade Sati, computed from the sidereal sky.")
        intro = (f"<p>Rashifal is read from your <strong>Moon sign</strong> (rashi). {moon_text} "
                 f"Saturn is in {_e(sat_sign)}, so Sade Sati is running for {_e(sade_names)}.</p>")
        h1, sub = "Today's Rashifal — Daily Horoscope", "आज का राशिफल — सभी 12 राशियाँ"
    body = f"""
<h1>{_e(h1)}</h1>
<p class="hi" lang="{'en' if hi else 'hi'}">{_e(sub)}</p>
<p class="date">{_e(_weekday(day, lang))}, {_e(_date_text(day, lang))} · IST</p>
{intro}
<div class="scroll"><table>{head_row}{''.join(rows)}</table></div>
{_panchang_line(s, day, lang)}
{_personal_line(lang)}
{_cta(lang)}
{_sign_links(None, lang)}
{_method_note(lang)}
{_more_links(None, lang)}"""
    return title, description, body


def _crumb_root(lang: str) -> tuple[str, str]:
    return ("आज का राशिफल", "/hi/rashifal") if lang == "hi" else ("Rashifal", "/rashifal")


def render_index(lang: str, day: dt.date | None = None) -> HTMLResponse:
    day = day or _today()
    title, description, body = _index_page(day, lang)
    return _shell(lang=lang, rashi=None, title=title, description=description,
                  crumbs=[_crumb_root(lang)], body=body, day=day)


def render_sign(slug: str, lang: str, day: dt.date | None = None) -> HTMLResponse:
    day = day or _today()
    rashi = BY_SLUG[slug]
    title, description, body, crumb = _sign_page(day, slug, lang)
    return _shell(lang=lang, rashi=rashi, title=title, description=description,
                  crumbs=[_crumb_root(lang), (crumb, path(rashi, lang))], body=body, day=day)


def _resolve(slug: str, lang: str) -> HTMLResponse | RedirectResponse:
    if slug in BY_SLUG:
        return render_sign(slug, lang)
    key = slug.lower()
    rashi = BY_SLUG.get(key) or BY_ENGLISH.get(key)
    if rashi:
        return RedirectResponse(path(rashi, lang), status_code=301)
    day = _today()
    hi = lang == "hi"
    body = ((f"<h1>राशि नहीं मिली</h1><p>“{_e(slug)}” नाम की कोई राशि नहीं है। नीचे अपनी राशि चुनें।</p>")
            if hi else
            (f"<h1>Sign not found</h1><p>There is no rashi called “{_e(slug)}”. Pick your Moon "
             "sign below.</p>")) + _sign_links(None, lang)
    return _shell(lang=lang, rashi=None, title=f"{'राशि नहीं मिली' if hi else 'Sign not found'} — {BRAND}",
                  description="Rashifal sign not found.", crumbs=[_crumb_root(lang)], body=body,
                  day=day, status=404, cache=False)


@router.get("/rashifal", response_class=HTMLResponse)
def rashifal_index() -> HTMLResponse:
    return render_index("en")


@router.get("/rashifal/{slug}", response_class=HTMLResponse)
def rashifal_sign(slug: str):
    return _resolve(slug, "en")


@router.get("/hi/rashifal", response_class=HTMLResponse)
def rashifal_index_hi() -> HTMLResponse:
    return render_index("hi")


@router.get("/hi/rashifal/{slug}", response_class=HTMLResponse)
def rashifal_sign_hi(slug: str):
    return _resolve(slug, "hi")
