"""Section names for the crawlable site map (/sitemap) and the footer link block
(DIVASTRO-133), in every registry language. No imports: seo_pages (the footer)
and site_hub (the page) both read it.

Keys: sitemap, panchang, rashifal, vrat, muhurat, nakshatra, rashi, katha,
tools, milan, kundali, rahu, choghadiya, naam, cities, signs, years, intro.
"""

LABELS: dict[str, dict[str, str]] = {
    "en": {
        "sitemap": "Site map", "panchang": "Panchang", "rashifal": "Rashifal (daily horoscope)",
        "vrat": "Vrat &amp; festivals", "muhurat": "Shubh muhurat", "nakshatra": "Nakshatra",
        "rashi": "Rashi (zodiac signs)", "katha": "Kathas", "tools": "Free tools",
        "milan": "Kundali Milan", "kundali": "Free Kundali", "rahu": "Rahu Kaal",
        "choghadiya": "Choghadiya", "naam": "Naam se Kundali Milan",
        "cities": "Today's Panchang by city", "signs": "Rashifal by sign",
        "years": "Vrat and festival calendars", "ekadashi": "Ekadashi",
        "pricing": "Prices",
        "intro": "Every section of Divine Astro in one place: daily Panchang for Indian cities, "
                 "Rashifal, vrat and festival dates, shubh muhurat, nakshatra and rashi guides, "
                 "kathas and the free tools.",
    },
    "hi": {
        "sitemap": "साइट मैप", "panchang": "पंचांग", "rashifal": "राशिफल",
        "vrat": "व्रत-त्योहार", "muhurat": "शुभ मुहूर्त", "nakshatra": "नक्षत्र",
        "rashi": "राशि", "katha": "कथाएँ", "tools": "मुफ़्त टूल",
        "milan": "कुंडली मिलान", "kundali": "मुफ़्त कुंडली", "rahu": "राहु काल",
        "choghadiya": "चौघड़िया", "naam": "नाम से कुंडली मिलान",
        "cities": "शहर के अनुसार आज का पंचांग", "signs": "राशि के अनुसार राशिफल",
        "years": "व्रत और त्योहार कैलेंडर", "ekadashi": "एकादशी",
        "pricing": "कीमतें",
        "intro": "डिवाइन एस्ट्रो के सभी भाग एक जगह: भारतीय शहरों का दैनिक पंचांग, राशिफल, "
                 "व्रत-त्योहार की तिथियाँ, शुभ मुहूर्त, नक्षत्र और राशि, कथाएँ और मुफ़्त टूल।",
    },
    "kn": {
        "sitemap": "ಸೈಟ್ ಮ್ಯಾಪ್", "panchang": "ಪಂಚಾಂಗ", "rashifal": "ರಾಶಿ ಭವಿಷ್ಯ",
        "vrat": "ವ್ರತ-ಹಬ್ಬಗಳು", "muhurat": "ಶುಭ ಮುಹೂರ್ತ", "nakshatra": "ನಕ್ಷತ್ರ",
        "rashi": "ರಾಶಿ", "katha": "ಕಥೆಗಳು", "tools": "ಉಚಿತ ಸಾಧನಗಳು",
        "milan": "ಕುಂಡಲಿ ಮಿಲನ", "kundali": "ಉಚಿತ ಕುಂಡಲಿ", "rahu": "ರಾಹು ಕಾಲ",
        "choghadiya": "ಚೌಘಡಿಯ", "naam": "ಹೆಸರಿನಿಂದ ಕುಂಡಲಿ ಮಿಲನ",
        "cities": "ನಗರವಾರು ಇಂದಿನ ಪಂಚಾಂಗ", "signs": "ರಾಶಿವಾರು ಭವಿಷ್ಯ",
        "years": "ವ್ರತ ಮತ್ತು ಹಬ್ಬಗಳ ಕ್ಯಾಲೆಂಡರ್", "ekadashi": "ಏಕಾದಶಿ",
        "pricing": "ಬೆಲೆಗಳು",
        "intro": "ಡಿವೈನ್ ಆಸ್ಟ್ರೋದ ಎಲ್ಲ ವಿಭಾಗಗಳು ಒಂದೇ ಕಡೆ: ನಗರವಾರು ಪಂಚಾಂಗ, ರಾಶಿ ಭವಿಷ್ಯ, "
                 "ವ್ರತ-ಹಬ್ಬಗಳು, ಶುಭ ಮುಹೂರ್ತ, ನಕ್ಷತ್ರ, ರಾಶಿ, ಕಥೆಗಳು ಮತ್ತು ಉಚಿತ ಸಾಧನಗಳು.",
    },
    "te": {
        "sitemap": "సైట్ మ్యాప్", "panchang": "పంచాంగం", "rashifal": "రాశి ఫలాలు",
        "vrat": "వ్రతాలు-పండుగలు", "muhurat": "శుభ ముహూర్తం", "nakshatra": "నక్షత్రం",
        "rashi": "రాశి", "katha": "కథలు", "tools": "ఉచిత సాధనాలు",
        "milan": "కుండలి మిలనం", "kundali": "ఉచిత కుండలి", "rahu": "రాహు కాలం",
        "choghadiya": "చౌఘడియా", "naam": "పేరుతో కుండలి మిలనం",
        "cities": "నగరాల వారీగా నేటి పంచాంగం", "signs": "రాశుల వారీగా ఫలాలు",
        "years": "వ్రతాలు, పండుగల క్యాలెండర్", "ekadashi": "ఏకాదశి",
        "pricing": "ధరలు",
        "intro": "డివైన్ ఆస్ట్రో విభాగాలన్నీ ఒకే చోట: నగరాల పంచాంగం, రాశి ఫలాలు, వ్రతాలు-పండుగలు, "
                 "శుభ ముహూర్తం, నక్షత్రం, రాశి, కథలు, ఉచిత సాధనాలు.",
    },
    "ta": {
        "sitemap": "தள வரைபடம்", "panchang": "பஞ்சாங்கம்", "rashifal": "ராசி பலன்",
        "vrat": "விரதம்-பண்டிகைகள்", "muhurat": "சுப முகூர்த்தம்", "nakshatra": "நட்சத்திரம்",
        "rashi": "ராசி", "katha": "கதைகள்", "tools": "இலவச கருவிகள்",
        "milan": "குண்டலி பொருத்தம்", "kundali": "இலவச ஜாதகம்", "rahu": "ராகு காலம்",
        "choghadiya": "சோகடியா", "naam": "பெயர் மூலம் குண்டலி பொருத்தம்",
        "cities": "நகரவாரியாக இன்றைய பஞ்சாங்கம்", "signs": "ராசிவாரியாக பலன்",
        "years": "விரதம், பண்டிகை நாட்காட்டி", "ekadashi": "ஏகாதசி",
        "pricing": "விலைகள்",
        "intro": "டிவைன் ஆஸ்ட்ரோவின் அனைத்துப் பகுதிகளும் ஒரே இடத்தில்: நகர பஞ்சாங்கம், ராசி பலன், "
                 "விரதம்-பண்டிகைகள், சுப முகூர்த்தம், நட்சத்திரம், ராசி, கதைகள், இலவச கருவிகள்.",
    },
    "ml": {
        "sitemap": "സൈറ്റ് മാപ്പ്", "panchang": "പഞ്ചാംഗം", "rashifal": "രാശിഫലം",
        "vrat": "വ്രതം-ഉത്സവങ്ങൾ", "muhurat": "ശുഭ മുഹൂർത്തം", "nakshatra": "നക്ഷത്രം",
        "rashi": "രാശി", "katha": "കഥകൾ", "tools": "സൗജന്യ ടൂളുകൾ",
        "milan": "ജാതക പൊരുത്തം", "kundali": "സൗജന്യ ജാതകം", "rahu": "രാഹുകാലം",
        "choghadiya": "ചോഘടിയ", "naam": "പേരിൽ നിന്ന് ജാതക പൊരുത്തം",
        "cities": "നഗരം തിരിച്ചുള്ള ഇന്നത്തെ പഞ്ചാംഗം", "signs": "രാശി തിരിച്ചുള്ള ഫലം",
        "years": "വ്രത, ഉത്സവ കലണ്ടർ", "ekadashi": "ഏകാദശി",
        "pricing": "വിലകൾ",
        "intro": "ഡിവൈൻ ആസ്ട്രോയുടെ എല്ലാ വിഭാഗങ്ങളും ഒരിടത്ത്: നഗര പഞ്ചാംഗം, രാശിഫലം, "
                 "വ്രതം-ഉത്സവങ്ങൾ, ശുഭ മുഹൂർത്തം, നക്ഷത്രം, രാശി, കഥകൾ, സൗജന്യ ടൂളുകൾ.",
    },
    "bn": {
        "sitemap": "সাইট ম্যাপ", "panchang": "পঞ্জিকা", "rashifal": "রাশিফল",
        "vrat": "ব্রত-উৎসব", "muhurat": "শুভ মুহূর্ত", "nakshatra": "নক্ষত্র",
        "rashi": "রাশি", "katha": "কথা-কাহিনি", "tools": "বিনামূল্যের টুল",
        "milan": "কুণ্ডলী মিলন", "kundali": "বিনামূল্যে কুণ্ডলী", "rahu": "রাহুকাল",
        "choghadiya": "চৌঘড়িয়া", "naam": "নাম থেকে কুণ্ডলী মিলন",
        "cities": "শহর অনুযায়ী আজকের পঞ্জিকা", "signs": "রাশি অনুযায়ী রাশিফল",
        "years": "ব্রত ও উৎসবের ক্যালেন্ডার", "ekadashi": "একাদশী",
        "pricing": "দাম",
        "intro": "ডিভাইন অ্যাস্ট্রোর সব বিভাগ এক জায়গায়: শহরের পঞ্জিকা, রাশিফল, ব্রত-উৎসব, "
                 "শুভ মুহূর্ত, নক্ষত্র, রাশি, কথা-কাহিনি ও বিনামূল্যের টুল।",
    },
    "or": {
        "sitemap": "ସାଇଟ୍ ମ୍ୟାପ୍", "panchang": "ପଞ୍ଚାଙ୍ଗ", "rashifal": "ରାଶିଫଳ",
        "vrat": "ବ୍ରତ-ପର୍ବ", "muhurat": "ଶୁଭ ମୁହୂର୍ତ୍ତ", "nakshatra": "ନକ୍ଷତ୍ର",
        "rashi": "ରାଶି", "katha": "ପୁରାଣ କଥା", "tools": "ମାଗଣା ଟୁଲ୍",
        "milan": "କୁଣ୍ଡଳୀ ମିଳନ", "kundali": "ମାଗଣା କୁଣ୍ଡଳୀ", "rahu": "ରାହୁ କାଳ",
        "choghadiya": "ଚୌଘଡ଼ିଆ", "naam": "ନାମରୁ କୁଣ୍ଡଳୀ ମିଳନ",
        "cities": "ସହର ଅନୁଯାୟୀ ଆଜିର ପଞ୍ଚାଙ୍ଗ", "signs": "ରାଶି ଅନୁଯାୟୀ ରାଶିଫଳ",
        "years": "ବ୍ରତ ଓ ପର୍ବ କ୍ୟାଲେଣ୍ଡର", "ekadashi": "ଏକାଦଶୀ",
        "pricing": "ମୂଲ୍ୟ",
        "intro": "ଡିଭାଇନ୍ ଆଷ୍ଟ୍ରୋର ସମସ୍ତ ବିଭାଗ ଗୋଟିଏ ସ୍ଥାନରେ: ସହର ପଞ୍ଚାଙ୍ଗ, ରାଶିଫଳ, ବ୍ରତ-ପର୍ବ, "
                 "ଶୁଭ ମୁହୂର୍ତ୍ତ, ନକ୍ଷତ୍ର, ରାଶି, କଥା ଓ ମାଗଣା ଟୁଲ୍।",
    },
}


# DIVASTRO-143: pa/ne/as/mr/gu live in app/lang_data/<code>.py; overlaid here as if written inline.
from . import lang_data  # noqa: E402
lang_data.merge("HUB_LABELS", LABELS)

def label(key: str, lang: str) -> str:
    """The section name in `lang` (HTML-safe: '&amp;' is already escaped), English fallback."""
    return LABELS.get(lang, LABELS["en"]).get(key) or LABELS["en"][key]
