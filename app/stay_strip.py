"""The "stay in touch" strip at the foot of the server-rendered content pages (DIVASTRO-135).

Readers land on a katha / rashifal / panchang page, read it and leave. One
compact strip near the end of the main content offers three ways to come back:

* daily Panchang on the phone — the existing opt-in web push (static/push.js),
  a button that push.js reveals only when the browser can do push, push is on
  at the server and the reader is not already subscribed; without JS it stays
  hidden;
* the WhatsApp channel — a plain link, new tab;
* "share this page on WhatsApp" — a plain wa.me link with the page title and
  the page URL, UTM-tagged like every share (share.py).

Copy lives in TEXT below, per language, like every other page module's table:
add a language by adding its dict (any key left out falls back to English).
Clicks are counted by static/strip.js through window.daTrack
(analytics.EVENT_NAMES: strip_push, strip_channel, strip_share).
"""

from __future__ import annotations

import html

from . import i18n
from .share import _ICON, share_url, whatsapp_href

CHANNEL_URL = "https://whatsapp.com/channel/0029VbDPiNeCsU9RAVK8G03G"
CAMPAIGN = "page-share"

# head / push / channel / share are the visible copy; busy / on / err / denied are
# the push button's states, read by push.js from data- attributes.
TEXT: dict[str, dict[str, str]] = {
    "en": {
        "head": "Stay in touch",
        "push": "Get today's panchang on your phone every morning",
        "busy": "Turning on…",
        "on": "Done — you will get it every morning.",
        "err": "Could not turn on alerts. Please try again.",
        "denied": "Notifications are blocked for this site in your browser settings.",
        "channel": "Join our WhatsApp channel",
        "share": "Share this page on WhatsApp",
    },
    "hi": {
        "head": "जुड़े रहें",
        "push": "रोज़ सुबह आज का पंचांग अपने फ़ोन पर पाएं",
        "busy": "चालू हो रही है…",
        "on": "हो गया — रोज़ सुबह सूचना मिलेगी।",
        "err": "सूचना चालू नहीं हो सकी। कृपया फिर से कोशिश करें।",
        "denied": "आपके ब्राउज़र में इस साइट की सूचनाएं बंद हैं।",
        "channel": "हमारे WhatsApp चैनल से जुड़ें",
        "share": "इस पेज को WhatsApp पर शेयर करें",
    },
    "kn": {
        "head": "ಸಂಪರ್ಕದಲ್ಲಿರಿ",
        "push": "ಪ್ರತಿದಿನ ಬೆಳಿಗ್ಗೆ ಇಂದಿನ ಪಂಚಾಂಗವನ್ನು ನಿಮ್ಮ ಫೋನ್‌ನಲ್ಲಿ ಪಡೆಯಿರಿ",
        "busy": "ಆನ್ ಆಗುತ್ತಿದೆ…",
        "on": "ಆಯಿತು — ಪ್ರತಿದಿನ ಬೆಳಿಗ್ಗೆ ಸೂಚನೆ ಬರುತ್ತದೆ.",
        "err": "ಸೂಚನೆ ಆನ್ ಆಗಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.",
        "denied": "ನಿಮ್ಮ ಬ್ರೌಸರ್ ಸೆಟ್ಟಿಂಗ್‌ಗಳಲ್ಲಿ ಈ ಸೈಟ್‌ನ ಅಧಿಸೂಚನೆಗಳು ನಿರ್ಬಂಧಿತವಾಗಿವೆ.",
        "channel": "ನಮ್ಮ WhatsApp ಚಾನಲ್‌ಗೆ ಸೇರಿ",
        "share": "ಈ ಪುಟವನ್ನು WhatsApp ನಲ್ಲಿ ಹಂಚಿಕೊಳ್ಳಿ",
    },
    "te": {
        "head": "మాతో కనెక్ట్ అయి ఉండండి",
        "push": "ప్రతి ఉదయం నేటి పంచాంగాన్ని మీ ఫోన్‌లో పొందండి",
        "busy": "ఆన్ అవుతోంది…",
        "on": "అయింది — ప్రతి ఉదయం నోటిఫికేషన్ వస్తుంది.",
        "err": "అలర్ట్‌లు ఆన్ కాలేదు. దయచేసి మళ్లీ ప్రయత్నించండి.",
        "denied": "మీ బ్రౌజర్ సెట్టింగ్‌లలో ఈ సైట్‌కు నోటిఫికేషన్లు బ్లాక్ చేయబడ్డాయి.",
        "channel": "మా WhatsApp ఛానల్‌లో చేరండి",
        "share": "ఈ పేజీని WhatsAppలో షేర్ చేయండి",
    },
    "ta": {
        "head": "தொடர்பில் இருங்கள்",
        "push": "தினமும் காலை இன்றைய பஞ்சாங்கத்தை உங்கள் தொலைபேசியில் பெறுங்கள்",
        "busy": "இயக்கப்படுகிறது…",
        "on": "முடிந்தது — தினமும் காலை அறிவிப்பு வரும்.",
        "err": "அறிவிப்புகளை இயக்க முடியவில்லை. மீண்டும் முயற்சிக்கவும்.",
        "denied": "உங்கள் உலாவி அமைப்புகளில் இந்தத் தளத்தின் அறிவிப்புகள் தடுக்கப்பட்டுள்ளன.",
        "channel": "எங்கள் WhatsApp சேனலில் சேருங்கள்",
        "share": "இந்தப் பக்கத்தை WhatsApp-இல் பகிருங்கள்",
    },
    "ml": {
        "head": "ബന്ധം നിലനിർത്തൂ",
        "push": "എല്ലാ രാവിലെയും ഇന്നത്തെ പഞ്ചാംഗം ഫോണിൽ ലഭിക്കൂ",
        "busy": "ഓണാക്കുന്നു…",
        "on": "ശരി — എല്ലാ രാവിലെയും അറിയിപ്പ് ലഭിക്കും.",
        "err": "അലേർട്ടുകൾ ഓണാക്കാനായില്ല. ദയവായി വീണ്ടും ശ്രമിക്കൂ.",
        "denied": "നിങ്ങളുടെ ബ്രൗസർ ക്രമീകരണങ്ങളിൽ ഈ സൈറ്റിന്റെ അറിയിപ്പുകൾ തടഞ്ഞിരിക്കുന്നു.",
        "channel": "ഞങ്ങളുടെ WhatsApp ചാനലിൽ ചേരൂ",
        "share": "ഈ പേജ് WhatsApp-ൽ ഷെയർ ചെയ്യൂ",
    },
    "bn": {
        "head": "যোগাযোগে থাকুন",
        "push": "প্রতিদিন সকালে আজকের পঞ্চাঙ্গ ফোনে পান",
        "busy": "চালু হচ্ছে…",
        "on": "হয়ে গেছে — প্রতিদিন সকালে বিজ্ঞপ্তি পাবেন।",
        "err": "বিজ্ঞপ্তি চালু করা যায়নি। আবার চেষ্টা করুন।",
        "denied": "আপনার ব্রাউজার সেটিংসে এই সাইটের বিজ্ঞপ্তি বন্ধ করা আছে।",
        "channel": "আমাদের WhatsApp চ্যানেলে যোগ দিন",
        "share": "এই পাতাটি WhatsApp-এ শেয়ার করুন",
    },
    "or": {
        "head": "ଯୋଗାଯୋଗରେ ରୁହନ୍ତୁ",
        "push": "ପ୍ରତିଦିନ ସକାଳେ ଆଜିର ପଞ୍ଚାଙ୍ଗ ଆପଣଙ୍କ ଫୋନରେ ପାଆନ୍ତୁ",
        "busy": "ଚାଲୁ ହେଉଛି…",
        "on": "ହୋଇଗଲା — ପ୍ରତିଦିନ ସକାଳେ ସୂଚନା ମିଳିବ।",
        "err": "ସୂଚନା ଚାଲୁ ହେଲା ନାହିଁ। ଦୟାକରି ପୁଣି ଚେଷ୍ଟା କରନ୍ତୁ।",
        "denied": "ଆପଣଙ୍କ ବ୍ରାଉଜର ସେଟିଂସରେ ଏହି ସାଇଟ୍‌ର ବିଜ୍ଞପ୍ତି ବ୍ଲକ୍ ହୋଇଛି।",
        "channel": "ଆମର WhatsApp ଚ୍ୟାନେଲରେ ଯୋଗ ଦିଅନ୍ତୁ",
        "share": "ଏହି ପୃଷ୍ଠାକୁ WhatsAppରେ ସେୟାର କରନ୍ତୁ",
    },
}


# DIVASTRO-143: pa/ne/as/mr/gu live in app/lang_data/<code>.py; overlaid here as if written inline.
from . import lang_data  # noqa: E402
lang_data.merge("STAY_STRIP", TEXT)

def _tx(key: str, lang: str) -> str:
    return i18n.t(key, lang, TEXT)


def stay_strip(*, lang: str, path: str, title: str) -> str:
    """The strip for the page at `path` (its canonical, language-prefixed path)
    titled `title`. Markup only; styling is in seo_pages._STYLE, behaviour in
    static/strip.js (loaded with defer, so without JS the strip is plain links)."""
    e = html.escape
    share = whatsapp_href(title, share_url(path, CAMPAIGN))
    states = "".join(f' data-{k}="{e(_tx(k, lang))}"' for k in ("busy", "on", "err", "denied"))
    return (
        '<aside class="stay" id="stay-strip" aria-labelledby="stay-head">'
        f'<h2 id="stay-head">{e(_tx("head", lang))}</h2>'
        '<ul>'
        f'<li><button type="button" class="stay-btn" id="strip-push" data-strip="strip_push" '
        f'hidden{states}>'
        f'{e(_tx("push", lang))}</button></li>'
        f'<li><a href="{e(CHANNEL_URL)}" target="_blank" rel="noopener" data-strip="strip_channel">'
        f'{_ICON}<span>{e(_tx("channel", lang))}</span></a></li>'
        f'<li><a href="{e(share)}" target="_blank" rel="noopener" data-strip="strip_share">'
        f'{_ICON}<span>{e(_tx("share", lang))}</span></a></li>'
        '</ul>'
        '<script src="/static/strip.js" defer></script>'
        '</aside>')
