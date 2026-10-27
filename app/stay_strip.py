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

DIVASTRO-164: `top_bar` repeats the share and channel links right under the
answer box of the festival / vrat / muhurat / katha / panchang / milan pages,
counted with detail "top".

DIVASTRO-167: `ask_strip`, placed right after that bar on the festival and matching
pages, offers two or three questions that open the app's question-first flow.
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
        "forward": "Forward to family",          # DIVASTRO-164: the bar under the answer
        # DIVASTRO-167: "Have a question about your own chart?" (ask_strip)
        "ask_head": "Have a question about your own chart?",
        "ask_free": "Ask free, no sign-in",
        "ask_go": "Ask the AI astrologer",
        "ask_q_marriage": "When will I get married?",
        "ask_q_married_life": "How will my married life be?",
        "ask_q_manglik": "Do I have Mangal dosha?",
        "ask_q_year": "How will the coming year be for me?",
        "ask_q_career": "When will my career pick up?",
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
        "forward": "परिवार को भेजें",
        "ask_head": "अपनी कुंडली के बारे में कोई प्रश्न है?",
        "ask_free": "मुफ़्त पूछें, साइन-इन की ज़रूरत नहीं",
        "ask_go": "एआई ज्योतिषी से पूछें",
        "ask_q_marriage": "मेरी शादी कब होगी?",
        "ask_q_married_life": "मेरा वैवाहिक जीवन कैसा रहेगा?",
        "ask_q_manglik": "क्या मेरी कुंडली में मंगल दोष है?",
        "ask_q_year": "आने वाला साल मेरे लिए कैसा रहेगा?",
        "ask_q_career": "मेरा करियर कब आगे बढ़ेगा?",
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
        "forward": "ಕುಟುಂಬಕ್ಕೆ ಕಳುಹಿಸಿ",
        "ask_head": "ನಿಮ್ಮ ಸ್ವಂತ ಜಾತಕದ ಬಗ್ಗೆ ಪ್ರಶ್ನೆ ಇದೆಯೇ?",
        "ask_free": "ಉಚಿತವಾಗಿ ಕೇಳಿ, ಸೈನ್-ಇನ್ ಬೇಕಿಲ್ಲ",
        "ask_go": "ಎಐ ಜ್ಯೋತಿಷಿಯನ್ನು ಕೇಳಿ",
        "ask_q_marriage": "ನನ್ನ ಮದುವೆ ಯಾವಾಗ ಆಗುತ್ತದೆ?",
        "ask_q_married_life": "ನನ್ನ ವೈವಾಹಿಕ ಜೀವನ ಹೇಗಿರುತ್ತದೆ?",
        "ask_q_manglik": "ನನ್ನ ಜಾತಕದಲ್ಲಿ ಮಂಗಳ ದೋಷ ಇದೆಯೇ?",
        "ask_q_year": "ಮುಂದಿನ ವರ್ಷ ನನಗೆ ಹೇಗಿರುತ್ತದೆ?",
        "ask_q_career": "ನನ್ನ ವೃತ್ತಿ ಯಾವಾಗ ಮುಂದುವರಿಯುತ್ತದೆ?",
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
        "forward": "కుటుంబానికి పంపండి",
        "ask_head": "మీ సొంత జాతకం గురించి ప్రశ్న ఉందా?",
        "ask_free": "ఉచితంగా అడగండి, సైన్-ఇన్ అవసరం లేదు",
        "ask_go": "ఏఐ జ్యోతిష్కుడిని అడగండి",
        "ask_q_marriage": "నా పెళ్లి ఎప్పుడు అవుతుంది?",
        "ask_q_married_life": "నా వైవాహిక జీవితం ఎలా ఉంటుంది?",
        "ask_q_manglik": "నా జాతకంలో కుజ దోషం ఉందా?",
        "ask_q_year": "రాబోయే సంవత్సరం నాకు ఎలా ఉంటుంది?",
        "ask_q_career": "నా కెరీర్ ఎప్పుడు ముందుకు సాగుతుంది?",
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
        "forward": "குடும்பத்துக்கு அனுப்புங்கள்",
        "ask_head": "உங்கள் சொந்த ஜாதகம் பற்றி கேள்வி உள்ளதா?",
        "ask_free": "இலவசமாகக் கேளுங்கள், உள்நுழைவு தேவையில்லை",
        "ask_go": "ஏஐ ஜோதிடரிடம் கேளுங்கள்",
        "ask_q_marriage": "எனக்கு எப்போது திருமணம் நடக்கும்?",
        "ask_q_married_life": "என் திருமண வாழ்க்கை எப்படி இருக்கும்?",
        "ask_q_manglik": "என் ஜாதகத்தில் செவ்வாய் தோஷம் உள்ளதா?",
        "ask_q_year": "வரும் ஆண்டு எனக்கு எப்படி இருக்கும்?",
        "ask_q_career": "என் தொழில் எப்போது முன்னேறும்?",
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
        "forward": "കുടുംബത്തിന് അയക്കൂ",
        "ask_head": "നിങ്ങളുടെ സ്വന്തം ജാതകത്തെക്കുറിച്ച് ചോദ്യമുണ്ടോ?",
        "ask_free": "സൗജന്യമായി ചോദിക്കൂ, സൈൻ ഇൻ വേണ്ട",
        "ask_go": "എഐ ജ്യോതിഷിയോട് ചോദിക്കൂ",
        "ask_q_marriage": "എന്റെ വിവാഹം എപ്പോൾ നടക്കും?",
        "ask_q_married_life": "എന്റെ ദാമ്പത്യ ജീവിതം എങ്ങനെയായിരിക്കും?",
        "ask_q_manglik": "എന്റെ ജാതകത്തിൽ ചൊവ്വാദോഷം ഉണ്ടോ?",
        "ask_q_year": "വരുന്ന വർഷം എനിക്ക് എങ്ങനെയായിരിക്കും?",
        "ask_q_career": "എന്റെ കരിയർ എപ്പോൾ മുന്നേറും?",
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
        "forward": "পরিবারকে পাঠান",
        "ask_head": "নিজের কুষ্ঠি নিয়ে কোনো প্রশ্ন আছে?",
        "ask_free": "বিনামূল্যে জিজ্ঞাসা করুন, সাইন-ইন লাগবে না",
        "ask_go": "এআই জ্যোতিষীকে জিজ্ঞাসা করুন",
        "ask_q_marriage": "আমার বিয়ে কবে হবে?",
        "ask_q_married_life": "আমার বিবাহিত জীবন কেমন হবে?",
        "ask_q_manglik": "আমার কুষ্ঠিতে কি মঙ্গল দোষ আছে?",
        "ask_q_year": "আগামী বছর আমার কেমন যাবে?",
        "ask_q_career": "আমার কেরিয়ার কবে এগোবে?",
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
        "forward": "ପରିବାରକୁ ପଠାନ୍ତୁ",
        "ask_head": "ନିଜ କୁଣ୍ଡଳୀ ବିଷୟରେ କିଛି ପ୍ରଶ୍ନ ଅଛି କି?",
        "ask_free": "ମାଗଣାରେ ପଚାରନ୍ତୁ, ସାଇନ୍-ଇନ୍ ଦରକାର ନାହିଁ",
        "ask_go": "ଏଆଇ ଜ୍ୟୋତିଷଙ୍କୁ ପଚାରନ୍ତୁ",
        "ask_q_marriage": "ମୋର ବିବାହ କେବେ ହେବ?",
        "ask_q_married_life": "ମୋର ବୈବାହିକ ଜୀବନ କିପରି ହେବ?",
        "ask_q_manglik": "ମୋ କୁଣ୍ଡଳୀରେ ମଙ୍ଗଳ ଦୋଷ ଅଛି କି?",
        "ask_q_year": "ଆଗାମୀ ବର୍ଷ ମୋ ପାଇଁ କିପରି ରହିବ?",
        "ask_q_career": "ମୋ କ୍ୟାରିଅର କେବେ ଆଗକୁ ବଢ଼ିବ?",
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


# --------------------------------------------------------------------------
# DIVASTRO-164: the same two WhatsApp actions near the TOP of the page
# --------------------------------------------------------------------------

TOP_CAMPAIGN = "top-share"


def top_bar(*, lang: str, path: str, title: str) -> str:
    """Two buttons placed straight under a page's answer box: forward the page
    (the strip's share text — the page title, which carries the answer — tagged
    utm_campaign=top-share) and join the channel. Plain links: static/strip.js
    (loaded by the strip lower down) counts taps as strip_share / strip_channel
    with detail "top". Styling: .share-wa and .seo .wa-top in static/styles.css."""
    e = html.escape
    share = whatsapp_href(title, share_url(path, TOP_CAMPAIGN))
    return (
        '<div class="wa-top">'
        f'<a class="share-wa" href="{e(share)}" target="_blank" rel="noopener" '
        f'data-strip="strip_share" data-detail="top">{_ICON}<span>{e(_tx("forward", lang))}</span></a>'
        f'<a class="share-wa" href="{e(CHANNEL_URL)}" target="_blank" rel="noopener" '
        f'data-strip="strip_channel" data-detail="top">{_ICON}<span>{e(_tx("channel", lang))}</span></a>'
        '</div>')


# --------------------------------------------------------------------------
# DIVASTRO-167: "Have a question about your own chart?" under the top bar
# --------------------------------------------------------------------------

#: The questions offered on each kind of page (keys of TEXT): marriage on the two
#: matching pages, general ones on the festival pages.
ASK_QUESTIONS: dict[str, tuple[str, ...]] = {
    "milan": ("ask_q_marriage", "ask_q_married_life", "ask_q_manglik"),
    "naam-milan": ("ask_q_marriage", "ask_q_married_life", "ask_q_manglik"),
    "tyohar": ("ask_q_year", "ask_q_career", "ask_q_marriage"),
}
ASK_MEDIUM = "ask"      # static/app.js reads utm_medium=ask as ask_start "page"


def ask_href(question: str, lang: str, campaign: str) -> str:
    """The app's question-first flow (static/app.js startAsk) with `question` filled in,
    in the page's language. No utm_source on purpose: the visit stays "internal" in the
    traffic tables; utm_medium / utm_campaign say which page sent it."""
    from urllib.parse import urlencode
    return "/?" + urlencode({"ask": question, "lang": lang,
                             "utm_medium": ASK_MEDIUM, "utm_campaign": campaign})


def ask_strip(*, lang: str, kind: str) -> str:
    """A compact line placed straight after the top bar (top_bar above): "Have a
    question about your own chart? Ask free, no sign-in" and two or three question
    chips that open the app with that question (/?ask=...). Plain links, no script
    (CSP). "free, no sign-in" only while app/guest.py gives a signed-out visitor an
    answer; otherwise it just offers to ask. Styling: .seo .ask-strip in static/styles.css."""
    from . import guest          # lazy: guest -> analytics -> page modules -> here
    e = html.escape
    free = _tx("ask_free" if guest.GUEST_ANSWERS > 0 else "ask_go", lang)
    chips = "".join(
        f'<a class="ask-strip-chip" href="{e(ask_href(_tx(k, lang), lang, kind))}">{e(_tx(k, lang))}</a>'
        for k in ASK_QUESTIONS[kind])
    return (
        f'<nav class="ask-strip" aria-label="{e(_tx("ask_head", lang))}">'
        f'<p class="ask-strip-head"><b>{e(_tx("ask_head", lang))}</b> <span>{e(free)}</span></p>'
        f'<div class="ask-strip-chips">{chips}</div>'
        '</nav>')


def forward_line(lang: str = "hi") -> str:
    """The last line of the daily WhatsApp channel post (daily_message.promo_lines):
    ask to forward it to family. No link: WhatsApp shows the channel's name on a
    forwarded channel post, and a post over whatsapp_channel.CAPTION_LIMIT goes out
    without its image card, so every character counts."""
    if lang == "hi":
        return "🙏 परिवार को भी भेजें।"
    return "🙏 Forward to your family."
