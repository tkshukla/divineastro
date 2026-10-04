"""Classical Vedic Choghadiya engine.

Calculates real-time Day and Night Choghadiya intervals:
- Amrit (अमृत) - Highly Auspicious / Best
- Shubh (शुभ) - Auspicious / Good for religious and important work
- Labh (लाभ) - Auspicious / Commercial gains, business & wealth
- Char (चल) - Neutral / Travel and dynamic activities
- Rog (रोग) - Inauspicious / Avoid new beginnings
- Kaal (काल) - Inauspicious / Saturn ruled, delays & losses
- Udveg (उद्वेग) - Inauspicious / Sun ruled, disputes & unrest
"""

from __future__ import annotations

import datetime as dt
from typing import Any
from zoneinfo import ZoneInfo

from .panchang import sun_times

# Choghadiya properties
# description_<code>: the slot text on the regional /<code>/choghadiya pages
# (seo_pages._slot_text; DIVASTRO-123). The JSON API keeps en/hi only.
CHOGHADIYA_INFO = {
    "Amrit": {
        "name_hi": "अमृत",
        "ruler": "Moon",
        "ruler_hi": "चंद्र",
        "quality": "auspicious",
        "quality_hi": "अति शुभ",
        "score": 95,
        "description": "Best time for all ceremonies, investments, agreements, and starting important endeavors.",
        "description_hi": "सभी प्रकार के मांगलिक कार्य, निवेश, समझौता एवं नवीन शुरुआत हेतु सर्वश्रेष्ठ समय।",
        "description_kn": "ಎಲ್ಲಾ ಶುಭ ಕಾರ್ಯಗಳು, ಹೂಡಿಕೆ, ಒಪ್ಪಂದಗಳು ಮತ್ತು ಮಹತ್ವದ ಕೆಲಸಗಳ ಆರಂಭಕ್ಕೆ ಅತ್ಯುತ್ತಮ ಸಮಯ.",
        "description_te": "అన్ని శుభకార్యాలు, పెట్టుబడులు, ఒప్పందాలు మరియు ముఖ్యమైన పనుల ప్రారంభానికి అత్యుత్తమ సమయం.",
        "description_ta": "எல்லாச் சடங்குகள், முதலீடு, ஒப்பந்தங்கள், முக்கியமான புதிய தொடக்கங்களுக்கு மிகச் சிறந்த நேரம்.",
        "description_ml": "എല്ലാ ചടങ്ങുകൾക്കും നിക്ഷേപങ്ങൾക്കും കരാറുകൾക്കും പ്രധാന തുടക്കങ്ങൾക്കും ഏറ്റവും ഉത്തമമായ സമയം.",
        "description_bn": "সব শুভ অনুষ্ঠান, বিনিয়োগ, চুক্তি এবং গুরুত্বপূর্ণ কাজ শুরু করার জন্য সর্বোত্তম সময়।",
        "description_or": "ସମସ୍ତ ଶୁଭ କାର୍ଯ୍ୟ, ନିବେଶ, ଚୁକ୍ତି ଓ ଗୁରୁତ୍ୱପୂର୍ଣ୍ଣ କାମ ଆରମ୍ଭ ପାଇଁ ସର୍ବୋତ୍ତମ ସମୟ।",
    },
    "Shubh": {
        "name_hi": "शुभ",
        "ruler": "Jupiter",
        "ruler_hi": "गुरु",
        "quality": "auspicious",
        "quality_hi": "शुभ",
        "score": 90,
        "description": "Highly auspicious for ceremonies, religious rituals, education, and purchasing property.",
        "description_hi": "विवाह, धार्मिक अनुष्ठान, शिक्षा आरंभ एवं संपत्ति क्रय हेतु अत्यंत शुभ मुहूर्त।",
        "description_kn": "ಶುಭ ಸಮಾರಂಭಗಳು, ಧಾರ್ಮಿಕ ವಿಧಿಗಳು, ವಿದ್ಯಾಭ್ಯಾಸ ಮತ್ತು ಆಸ್ತಿ ಖರೀದಿಗೆ ಅತ್ಯಂತ ಶುಭ.",
        "description_te": "శుభకార్యాలు, ధార్మిక కర్మలు, విద్య మరియు ఆస్తి కొనుగోలుకు ఎంతో శుభప్రదం.",
        "description_ta": "சடங்குகள், வழிபாடு, கல்வித் தொடக்கம், சொத்து வாங்குதல் ஆகியவற்றுக்கு மிகவும் சுபம்.",
        "description_ml": "ചടങ്ങുകൾ, മതപരമായ കർമങ്ങൾ, വിദ്യാരംഭം, വസ്തു വാങ്ങൽ എന്നിവയ്ക്ക് ഏറെ ശുഭം.",
        "description_bn": "শুভ অনুষ্ঠান, ধর্মীয় আচার, বিদ্যারম্ভ ও সম্পত্তি কেনার জন্য অত্যন্ত শুভ।",
        "description_or": "ଶୁଭ ଅନୁଷ୍ଠାନ, ଧାର୍ମିକ ବିଧି, ବିଦ୍ୟାରମ୍ଭ ଓ ସମ୍ପତ୍ତି କିଣିବା ପାଇଁ ଅତ୍ୟନ୍ତ ଶୁଭ।",
    },
    "Labh": {
        "name_hi": "लाभ",
        "ruler": "Mercury",
        "ruler_hi": "बुध",
        "quality": "auspicious",
        "quality_hi": "शुभ / लाभप्रद",
        "score": 85,
        "description": "Favorable for business, trade, financial transactions, launching products, and interviews.",
        "description_hi": "व्यापार, आर्थिक लेनदेन, नवीन उत्पाद शुभारंभ एवं साक्षात्कार हेतु अनुकूल समय।",
        "description_kn": "ವ್ಯಾಪಾರ, ವಹಿವಾಟು, ಹಣಕಾಸಿನ ವ್ಯವಹಾರಗಳು, ಹೊಸ ಉತ್ಪನ್ನಗಳ ಬಿಡುಗಡೆ ಮತ್ತು ಸಂದರ್ಶನಗಳಿಗೆ ಅನುಕೂಲ.",
        "description_te": "వ్యాపారం, వాణిజ్యం, ఆర్థిక లావాదేవీలు, కొత్త ఉత్పత్తుల ప్రారంభం మరియు ఇంటర్వ్యూలకు అనుకూలం.",
        "description_ta": "வணிகம், வர்த்தகம், பணப் பரிவர்த்தனை, புதிய பொருள் அறிமுகம், நேர்காணலுக்கு உகந்தது.",
        "description_ml": "വ്യാപാരം, കച്ചവടം, സാമ്പത്തിക ഇടപാടുകൾ, പുതിയ ഉൽപ്പന്നങ്ങളുടെ തുടക്കം, അഭിമുഖങ്ങൾ എന്നിവയ്ക്ക് അനുകൂലം.",
        "description_bn": "ব্যবসা, বাণিজ্য, আর্থিক লেনদেন, নতুন পণ্যের সূচনা ও সাক্ষাৎকারের জন্য অনুকূল।",
        "description_or": "ବ୍ୟବସାୟ, ବାଣିଜ୍ୟ, ଆର୍ଥିକ କାରବାର, ନୂଆ ଉତ୍ପାଦର ଶୁଭାରମ୍ଭ ଓ ସାକ୍ଷାତକାର ପାଇଁ ଅନୁକୂଳ।",
    },
    "Char": {
        "name_hi": "चल",
        "ruler": "Venus",
        "ruler_hi": "शुक्र",
        "quality": "neutral",
        "quality_hi": "सामान्य / गतिमान",
        "score": 60,
        "description": "Neutral. Excellent for journeys, travel, vehicle purchases, and shifting places.",
        "description_hi": "सामान्य अनुकूल। यात्रा, वाहन क्रय एवं स्थान परिवर्तन हेतु उत्तम।",
        "description_kn": "ಮಧ್ಯಮ. ಪ್ರಯಾಣ, ಯಾತ್ರೆ, ವಾಹನ ಖರೀದಿ ಮತ್ತು ಸ್ಥಳ ಬದಲಾವಣೆಗೆ ಅತ್ಯುತ್ತಮ.",
        "description_te": "మధ్యమం. ప్రయాణాలు, యాత్రలు, వాహన కొనుగోలు మరియు నివాసం మార్పుకు చాలా మంచిది.",
        "description_ta": "பயணம், வாகனம் வாங்குதல், இடம் மாறுதல் ஆகியவற்றுக்கு மிகவும் நல்லது.",
        "description_ml": "യാത്രകൾക്കും വാഹനം വാങ്ങുന്നതിനും താമസം മാറുന്നതിനും വളരെ നല്ലത്.",
        "description_bn": "সাধারণ। যাত্রা, ভ্রমণ, যানবাহন কেনা ও স্থান পরিবর্তনের জন্য উত্তম।",
        "description_or": "ସାଧାରଣ। ଯାତ୍ରା, ଭ୍ରମଣ, ଯାନବାହନ କିଣିବା ଓ ସ୍ଥାନ ପରିବର୍ତ୍ତନ ପାଇଁ ଉତ୍ତମ।",
    },
    "Rog": {
        "name_hi": "रोग",
        "ruler": "Mars",
        "ruler_hi": "मंगल",
        "quality": "inauspicious",
        "quality_hi": "अशुभ / रोग",
        "score": 25,
        "description": "Inauspicious. Avoid medical procedures or conflict. Only suitable for competitive sports or defeating rivals.",
        "description_hi": "अशुभ। मांगलिक कार्य वर्जित। प्रतिस्पर्धा व वाद-विवाद निवारण हेतु ही उपयोगी।",
        "description_kn": "ಅಶುಭ. ವೈದ್ಯಕೀಯ ಪ್ರಕ್ರಿಯೆಗಳು ಮತ್ತು ಜಗಳಗಳನ್ನು ತಪ್ಪಿಸಿ. ಸ್ಪರ್ಧಾತ್ಮಕ ಕ್ರೀಡೆಗಳು ಅಥವಾ ಪ್ರತಿಸ್ಪರ್ಧಿಗಳನ್ನು ಗೆಲ್ಲುವುದಕ್ಕೆ ಮಾತ್ರ ಸೂಕ್ತ.",
        "description_te": "అశుభం. వైద్య ప్రక్రియలు, వివాదాలను నివారించండి. పోటీ క్రీడలకు లేదా ప్రత్యర్థులను జయించడానికి మాత్రమే అనుకూలం.",
        "description_ta": "மருத்துவ நடைமுறைகளையும் வாக்குவாதத்தையும் தவிர்க்கவும். போட்டிகளுக்கும் எதிரிகளை வெல்வதற்கும் மட்டும் ஏற்றது.",
        "description_ml": "ചികിത്സാ നടപടികളും തർക്കങ്ങളും ഒഴിവാക്കുക. മത്സരങ്ങൾക്കും എതിരാളികളെ മറികടക്കാനും മാത്രം യോജിച്ചത്.",
        "description_bn": "অশুভ। চিকিৎসা-প্রক্রিয়া ও বিবাদ এড়িয়ে চলুন। কেবল প্রতিযোগিতা বা প্রতিপক্ষকে পরাস্ত করার জন্য উপযুক্ত।",
        "description_or": "ଅଶୁଭ। ଚିକିତ୍ସା ପ୍ରକ୍ରିୟା ଓ ବିବାଦରୁ ଦୂରେଇ ରୁହନ୍ତୁ। କେବଳ ପ୍ରତିଯୋଗିତା ବା ପ୍ରତିଦ୍ୱନ୍ଦ୍ୱୀଙ୍କୁ ପରାସ୍ତ କରିବା ପାଇଁ ଉପଯୁକ୍ତ।",
    },
    "Kaal": {
        "name_hi": "काल",
        "ruler": "Saturn",
        "ruler_hi": "शनि",
        "quality": "inauspicious",
        "quality_hi": "अशुभ / काल",
        "score": 20,
        "description": "Inauspicious. Ruled by Saturn; causes delays and setbacks. Avoid new ventures or signing documents.",
        "description_hi": "अशुभ। कार्यों में विलंब व हानि संभव। नए सौदों व अनुबंधों से बचें।",
        "description_kn": "ಅಶುಭ. ಶನಿಯ ಅಧಿಪತ್ಯ; ವಿಳಂಬ ಮತ್ತು ಹಿನ್ನಡೆ ತರುತ್ತದೆ. ಹೊಸ ಕೆಲಸಗಳ ಆರಂಭ ಅಥವಾ ದಾಖಲೆಗಳಿಗೆ ಸಹಿ ಮಾಡುವುದನ್ನು ತಪ್ಪಿಸಿ.",
        "description_te": "అశుభం. శని ఆధిపత్యం; ఆలస్యాలు, ఆటంకాలు కలిగిస్తుంది. కొత్త పనుల ప్రారంభం లేదా పత్రాలపై సంతకాలు చేయడం మానుకోండి.",
        "description_ta": "சனியின் ஆதிக்கம்; தாமதங்களும் தடைகளும் வரலாம். புதிய முயற்சிகளையும் ஆவணங்களில் கையெழுத்திடுவதையும் தவிர்க்கவும்.",
        "description_ml": "ശനിയുടെ ആധിപത്യം; താമസവും തടസ്സങ്ങളും ഉണ്ടാകാം. പുതിയ സംരംഭങ്ങളും രേഖകളിൽ ഒപ്പിടലും ഒഴിവാക്കുക.",
        "description_bn": "অশুভ। শনির আধিপত্য; বিলম্ব ও বাধা আনে। নতুন উদ্যোগ বা দলিলে সই করা এড়িয়ে চলুন।",
        "description_or": "ଅଶୁଭ। ଶନିଙ୍କ ଆଧିପତ୍ୟ; ବିଳମ୍ବ ଓ ବାଧା ଆଣେ। ନୂଆ ଉଦ୍ୟମ ବା ଦଲିଲରେ ଦସ୍ତଖତ କରିବାରୁ ଦୂରେଇ ରୁହନ୍ତୁ।",
    },
    "Udveg": {
        "name_hi": "उद्वेग",
        "ruler": "Sun",
        "ruler_hi": "सूर्य",
        "quality": "inauspicious",
        "quality_hi": "अशुभ / उद्वेग",
        "score": 30,
        "description": "Inauspicious. Causes restlessness and anxiety. Favorable only for government filings or official duties.",
        "description_hi": "अशुभ। मानसिक तनाव व अशांति संभव। केवल राजकीय कार्यों व कर आदि हेतु उपयुक्त।",
        "description_kn": "ಅಶುಭ. ಚಡಪಡಿಕೆ ಮತ್ತು ಆತಂಕ ಉಂಟುಮಾಡುತ್ತದೆ. ಸರ್ಕಾರಿ ಅರ್ಜಿಗಳು ಅಥವಾ ಅಧಿಕೃತ ಕರ್ತವ್ಯಗಳಿಗೆ ಮಾತ್ರ ಅನುಕೂಲ.",
        "description_te": "అశుభం. అశాంతి, ఆందోళన కలిగిస్తుంది. ప్రభుత్వ దరఖాస్తులు లేదా అధికారిక విధులకు మాత్రమే అనుకూలం.",
        "description_ta": "அமைதியின்மையும் பதற்றமும் தரலாம். அரசு விண்ணப்பங்கள், அலுவல் பணிகளுக்கு மட்டும் உகந்தது.",
        "description_ml": "അസ്വസ്ഥതയും ഉത്കണ്ഠയും ഉണ്ടാക്കാം. സർക്കാർ അപേക്ഷകൾക്കും ഔദ്യോഗിക ജോലികൾക്കും മാത്രം അനുകൂലം.",
        "description_bn": "অশুভ। অস্থিরতা ও উদ্বেগ আনে। কেবল সরকারি আবেদন বা দাপ্তরিক কাজের জন্য অনুকূল।",
        "description_or": "ଅଶୁଭ। ଅସ୍ଥିରତା ଓ ଉଦ୍ବେଗ ଆଣେ। କେବଳ ସରକାରୀ ଆବେଦନ ବା ଦାପ୍ତରିକ କାମ ପାଇଁ ଅନୁକୂଳ।",
    },
}

# Classical Weekday sequences
# Day sequence starts with weekday ruler
DAY_SEQUENCE = {
    0: ["Udveg", "Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg"],      # Sunday
    1: ["Amrit", "Kaal", "Shubh", "Rog", "Udveg", "Char", "Labh", "Amrit"],      # Monday
    2: ["Rog", "Udveg", "Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog"],        # Tuesday
    3: ["Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg", "Char", "Labh"],        # Wednesday
    4: ["Shubh", "Rog", "Udveg", "Char", "Labh", "Amrit", "Kaal", "Shubh"],      # Thursday
    5: ["Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg", "Char"],        # Friday
    6: ["Kaal", "Shubh", "Rog", "Udveg", "Char", "Labh", "Amrit", "Kaal"],        # Saturday
}

# Night sequence starts with 5th weekday ruler from day ruler
NIGHT_SEQUENCE = {
    0: ["Shubh", "Amrit", "Char", "Rog", "Kaal", "Labh", "Udveg", "Shubh"],      # Sunday Night
    1: ["Char", "Rog", "Kaal", "Labh", "Udveg", "Shubh", "Amrit", "Char"],        # Monday Night
    2: ["Kaal", "Labh", "Udveg", "Shubh", "Amrit", "Char", "Rog", "Kaal"],        # Tuesday Night
    3: ["Udveg", "Shubh", "Amrit", "Char", "Rog", "Kaal", "Labh", "Udveg"],      # Wednesday Night
    4: ["Amrit", "Char", "Rog", "Kaal", "Labh", "Udveg", "Shubh", "Amrit"],      # Thursday Night
    5: ["Rog", "Kaal", "Labh", "Udveg", "Shubh", "Amrit", "Char", "Rog"],        # Friday Night
    6: ["Labh", "Udveg", "Shubh", "Amrit", "Char", "Rog", "Kaal", "Labh"],        # Saturday Night
}


def eighths(start: dt.datetime, end: dt.datetime) -> list[tuple[dt.datetime, dt.datetime]]:
    """Cut [start, end) into the eight equal choghadiya parts.

    Each boundary is computed from `start` (not by accumulating steps) so the
    last part ends exactly at `end` and the parts are contiguous.
    """
    step = (end - start) / 8
    return [(start + i * step, end if i == 7 else start + (i + 1) * step) for i in range(8)]


def day_night_slots(
    vara: int,
    sunrise: dt.datetime,
    sunset: dt.datetime,
    next_sunrise: dt.datetime,
) -> tuple[list[tuple[str, dt.datetime, dt.datetime]], list[tuple[str, dt.datetime, dt.datetime]]]:
    """(name, start, end) for the 8 day slots (sunrise -> sunset) and the 8 night
    slots (sunset -> next sunrise) of a vedic weekday (Sunday = 0).

    The single implementation shared by the in-app tool (/api/choghadiya) and
    the server-rendered /choghadiya pages (seo_pages.choghadiya_slots).
    """
    day = [(n, s, e) for n, (s, e) in zip(DAY_SEQUENCE[vara], eighths(sunrise, sunset))]
    night = [(n, s, e) for n, (s, e) in zip(NIGHT_SEQUENCE[vara], eighths(sunset, next_sunrise))]
    return day, night


def get_choghadiya_schedule(
    target_date: str | dt.date | None = None,
    latitude: float = 28.6139,
    longitude: float = 77.2090,
    tz_name: str = "Asia/Kolkata",
    now_dt: dt.datetime | None = None,
    lang: str = "en",
) -> dict[str, Any]:
    """Calculate complete 16-slot Day and Night Choghadiya timeline with active slot."""
    hi = lang == "hi"
    tz = ZoneInfo(tz_name)

    if isinstance(target_date, str):
        c_date = dt.date.fromisoformat(target_date)
    elif isinstance(target_date, dt.date):
        c_date = target_date
    else:
        c_date = dt.datetime.now(tz).date()

    if now_dt is None:
        current_time = dt.datetime.now(tz)
    else:
        current_time = now_dt.astimezone(tz) if now_dt.tzinfo else now_dt.replace(tzinfo=tz)

    # The same Swiss Ephemeris sunrise/sunset the Panchang prints (DIVASTRO-103:
    # this used to be a seasonal estimate, ~20-50 min off for Delhi in October).
    sunrise, sunset, next_sunrise = sun_times(c_date, latitude, longitude, tz_name)
    if not (sunrise and sunset and next_sunrise):
        raise ValueError("The Sun does not both rise and set on this date at this "
                         "latitude, so Choghadiya is not defined.")

    # 0 = Monday in Python weekday(), convert to 0 = Sunday (Vedic standard)
    py_weekday = c_date.weekday()
    vedic_weekday = (py_weekday + 1) % 7

    day_parts, night_parts = day_night_slots(vedic_weekday, sunrise, sunset, next_sunrise)

    def slot(index: int, period: str, name: str, s_time: dt.datetime, e_time: dt.datetime) -> dict[str, Any]:
        info = CHOGHADIYA_INFO[name]
        return {
            "index": index,
            "period": period,
            "name": name,
            "name_label": info["name_hi"] if hi else name,
            "ruler": info["ruler"],
            "ruler_label": info["ruler_hi"] if hi else info["ruler"],
            "quality": info["quality"],
            "quality_label": info["quality_hi"] if hi else info["quality"].capitalize(),
            "score": info["score"],
            "start": s_time.strftime("%H:%M"),
            "end": e_time.strftime("%H:%M"),
            "start_iso": s_time.isoformat(),
            "end_iso": e_time.isoformat(),
            "description": info["description_hi"] if hi else info["description"],
            "is_current": s_time <= current_time < e_time,
        }

    day_slots = [slot(i + 1, "day", n, s, e) for i, (n, s, e) in enumerate(day_parts)]
    night_slots = [slot(i + 9, "night", n, s, e) for i, (n, s, e) in enumerate(night_parts)]
    active_slot: dict[str, Any] | None = next(
        (x for x in day_slots + night_slots if x["is_current"]), None)

    # Between midnight and this date's sunrise the running choghadiya belongs to
    # the PREVIOUS vedic day's night (sunset yesterday -> sunrise today), whose
    # sequence follows yesterday's weekday lord.
    if active_slot is None and current_time < sunrise:
        prev = c_date - dt.timedelta(days=1)
        p_rise, p_set, p_next = sun_times(prev, latitude, longitude, tz_name)
        if p_rise and p_set and p_next:
            _, prev_night = day_night_slots((prev.weekday() + 1) % 7, p_rise, p_set, p_next)
            for i, (n, s, e) in enumerate(prev_night):
                if s <= current_time < e:
                    active_slot = slot(i + 9, "night", n, s, e)
                    active_slot["date"] = prev.isoformat()
                    break

    # A date that is neither today nor tomorrow-before-sunrise: keep the old
    # behaviour of pointing at the first slot (not marked current).
    if active_slot is None:
        active_slot = day_slots[0]

    return {
        "date": c_date.isoformat(),
        "weekday": ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"][vedic_weekday],
        "weekday_hi": ["रविवार", "सोमवार", "मंगलवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार"][vedic_weekday],
        "sunrise": sunrise.strftime("%H:%M"),
        "sunset": sunset.strftime("%H:%M"),
        "active_slot": active_slot,
        "day_slots": day_slots,
        "night_slots": night_slots,
    }
