"""The text of the daily Rashifal pages (rashifal_pages.py), per language.

TRANSLATORS: this file is data. To translate /rashifal and /rashifal/<sign>
into, say, Kannada:

* add a "kn" dict to TEXT with any subset of the "en" keys,
* add a "kn" list to MORE_LINKS,
* add a "kn" entry to TONE_LABEL and to every phrase-bank entry (MOON_HOUSE,
  SATURN_HOUSE, JUPITER_HOUSE, RAHU_HOUSE: one per house 1-12; KETU_LINE),
* then add "kn" to rashifal_pages.TRANSLATED.

A key you leave out falls back to the "_native" template (sign names in the
language's own script, from app/astro/names_<code>.py) and then to English.
Templates keep their `{placeholders}`; HTML values keep their tags (write
`&amp;` for "&"). Rashi, nakshatra, tithi, weekday and month names are not
here: they come from app/astro/names_<code>.py.

Placeholders: {name} the sign's traditional name (Mesh), {english} (Aries),
{local} the sign in the page's language (मेष / ಮೇಷ), {name_hi} (मेष), {house} the house word
(4th / चौथे), {date} {date_short} {weekday} {brand} {tone} {tone_lower}.
"""

from __future__ import annotations

GOOD, MIXED, EASY = "good", "mixed", "easy"

TEXT: dict[str, dict[str, str]] = {
    "en": {
        # house words: the ordinal ("4th") is computed for English; a language
        # writes "house.1".."house.12" to use its own words
        "house_short": "{house} house",
        "rx": " (retrograde)",
        "planet.Moon": "Moon", "planet.Saturn": "Saturn", "planet.Jupiter": "Jupiter",
        "planet.Rahu": "Rahu", "planet.Ketu": "Ketu",
        # a sign in a sentence / in the sign list / as a crumb
        "sign_label": "{english} ({name})",
        "sign_link": "{name} · {english}",
        "sign_crumb": "{name}",
        "sade_name": "{name}",
        "crumb_root": "Rashifal",
        "sub_lang": "hi",
        # -- sign page -------------------------------------------------------
        "s.title": "{name} Rashifal Today, {date_short} — {english} Daily Horoscope | {brand}",
        "s.desc": ("{name} ({english} Moon sign) rashifal for {weekday}, "
                   "{date}: the Moon transits your {house} house — "
                   "{tone_lower}. Plus Saturn, Jupiter and Rahu–Ketu transits, Sade Sati "
                   "status and today's tithi, computed from the sidereal sky."),
        "s.h1": "{name} Rashifal Today — {english} Daily Horoscope",
        "s.sub": "आज का {name_hi} राशिफल",
        # HTML; {name} is escaped
        "s.summary": "the Moon is in your {house} house from {name}.",
        "s.about_rashi": "About {name} rashi — traits, nakshatras and name letters",
        # Moon section (HTML): {sign} {house} {time}
        "moon.head": "Today's Moon transit (Chandra gochar)",
        "moon.allday": "The Moon is in {sign} all day — your {house} house.",
        "moon.until": "<strong>Until {time} IST:</strong> the Moon is in {sign} — your {house} house.",
        "moon.from": "<strong>From {time} IST:</strong> the Moon enters {sign} — your {house} house.",
        "moon.two": "<p>The Moon changes sign during the day, so the day reads in two parts.</p>",
        # slow transits (HTML)
        "back.head": "The longer backdrop: slow transits",
        "back.intro": ("<p>These planets stay in one sign for months or years, so they set the background "
                       "against which each day plays out.</p>"),
        "back.where": "{sign}{rx} · {house} house",
        "phase.1": "first (rising)", "phase.2": "second (peak)", "phase.3": "third (setting)",
        "sade.running": ("<strong>Sade Sati is running</strong> — the {phase} phase. It is a "
                         "slow, disciplining period rather than something to fear; steady routine, "
                         "service and patience make it lighter."),
        "sade.dhaiya": "<strong>No Sade Sati</strong>, but Saturn's Dhaiya is running (see above).",
        "sade.none": ("<strong>No Sade Sati</strong> — Saturn is not in the 12th, 1st or 2nd from "
                      "your sign."),
        # today's panchang (HTML): {paksha} {paksha_full} {tithi} {nakshatra}
        "panchang": ("<h2>Today's Panchang</h2><p>At sunrise in New Delhi it is "
                     "<strong>{paksha} {tithi}</strong> tithi with the Moon in "
                     "<strong>{nakshatra}</strong> nakshatra. Rahu Kaal, sunrise and the full almanac are "
                     'on <a href="/panchang">today\'s Panchang</a>.</p>'),
        "personal": ("<p class=\"note\">This rashifal is read from your Moon sign alone — the same for "
                     "everyone born with the Moon in that sign. A personal reading uses your full birth "
                     "chart: the ascendant, your running dasha and the ashtakavarga strength of each "
                     "transit. Not sure of your Moon sign (rashi)? It is the first thing your free kundali "
                     "shows — it is usually not your Western sun sign.</p>"),
        "cta": "Get your free kundali — then ask a question about your own chart",
        "signs.head": "Today's Rashifal for every sign",
        "more.head": "More free tools",
        "method": ("<h2>How this is calculated</h2><p>Planet positions are computed for today (IST) "
                   "with the Swiss Ephemeris in the sidereal zodiac (Lahiri ayanamsa) — the same "
                   "positions our kundali and panchang use. Houses are counted from your Moon sign, as "
                   "in classical gochar. Which houses are favourable follows the scheme of Varahamihira's "
                   "Brihat Samhita (ch. 104) and Mantreswara's Phaladeepika (ch. 26): the Moon is "
                   "favourable in the 1st, 3rd, 6th, 7th, 10th and 11th; Saturn, Rahu and Ketu in the "
                   "3rd, 6th and 11th; Jupiter in the 2nd, 5th, 7th, 9th and 11th.</p>"),
        # -- index page ------------------------------------------------------
        "i.title": "Aaj Ka Rashifal, {date_short} — Today's Horoscope for All 12 Signs | {brand}",
        "i.desc": ("Today's rashifal for {weekday}, {date}: "
                   "daily horoscope for all 12 Moon signs from Mesh to Meen — Moon transit, "
                   "Saturn, Jupiter and Rahu, and Sade Sati, computed from the sidereal sky."),
        "i.h1": "Today's Rashifal — Daily Horoscope",
        "i.sub": "आज का राशिफल — सभी 12 राशियाँ",
        # HTML: {moon_text} {sat_sign} {sade_names}
        "i.intro": ("<p>Rashifal is read from your <strong>Moon sign</strong> (rashi). {moon_text} "
                    "Saturn is in {sat_sign}, so Sade Sati is running for {sade_names}.</p>"),
        "i.moon_two": ("The Moon is in {now} until {time} IST, then in {next}. The table "
                       "shows the position for most of the day."),
        "i.moon_one": "The Moon is in {now} all day.",
        # HTML: {name} {english} {local} (escaped)
        "i.name": "{name} <small>{english}</small>",
        "i.sade": "<small>Sade Sati</small>",
        "i.head_row": "<tr><th>Sign</th><th>Moon in your</th><th>Today</th></tr>",
        # -- 404 -------------------------------------------------------------
        "nf.title": "Sign not found",
        "nf.body": ("<h1>Sign not found</h1><p>There is no rashi called “{slug}”. Pick your Moon "
                    "sign below.</p>"),
    },

    "hi": {
        "house.1": "पहले", "house.2": "दूसरे", "house.3": "तीसरे", "house.4": "चौथे",
        "house.5": "पाँचवें", "house.6": "छठे", "house.7": "सातवें", "house.8": "आठवें",
        "house.9": "नौवें", "house.10": "दसवें", "house.11": "ग्यारहवें", "house.12": "बारहवें",
        "house_short": "{house} भाव",
        "rx": " (वक्री)",
        "planet.Moon": "चंद्रमा", "planet.Saturn": "शनि", "planet.Jupiter": "गुरु",
        "planet.Rahu": "राहु", "planet.Ketu": "केतु",
        "home": "मुख्य पृष्ठ",
        "sign_label": "{local} ({name})",
        "sign_link": "{local}",
        "sign_crumb": "{local}",
        "sade_name": "{local}",
        "crumb_root": "आज का राशिफल",
        "sub_lang": "en",
        "s.title": "आज का {local} राशिफल, {date} — {name} Rashifal Today | {brand}",
        "s.desc": ("{local} राशि का आज का राशिफल ({weekday}, "
                   "{date}): चंद्रमा आपकी राशि से {house} भाव में — "
                   "{tone}। साथ में शनि, गुरु, राहु-केतु का गोचर, साढ़ेसाती की स्थिति और आज का "
                   "पंचांग।"),
        "s.h1": "आज का {local} राशिफल",
        "s.sub": "{name} Rashifal · {english}",
        "s.summary": "चंद्रमा आपकी राशि से {house} भाव में।",
        "s.about_rashi": "{local} राशि — स्वभाव, नक्षत्र और नामाक्षर",
        "moon.head": "आज चंद्रमा का गोचर (चंद्र गोचर)",
        "moon.allday": "आज पूरे दिन चंद्रमा {sign} में है — आपकी राशि से {house} भाव में।",
        "moon.until": ("<strong>{time} (IST) तक:</strong> चंद्रमा {sign} में — आपकी राशि से "
                       "{house} भाव में।"),
        "moon.from": ("<strong>{time} (IST) से:</strong> चंद्रमा {sign} में प्रवेश करता है — आपकी "
                      "राशि से {house} भाव में।"),
        "moon.two": "<p>आज दिन में चंद्रमा राशि बदलता है, इसलिए दिन के दो हिस्से अलग पढ़ें।</p>",
        "back.head": "लंबी अवधि का गोचर",
        "back.intro": ("<p>ये ग्रह महीनों या वर्षों तक एक राशि में रहते हैं, इसलिए ये रोज़ के दिन की "
                       "पृष्ठभूमि बनाते हैं।</p>"),
        "back.where": "{sign}{rx} · {house} भाव",
        "phase.1": "पहला (आरंभ)", "phase.2": "दूसरा (मध्य)", "phase.3": "तीसरा (अंतिम)",
        "sade.running": ("<strong>साढ़ेसाती चल रही है</strong> — {phase} चरण। यह धीमी, "
                         "अनुशासन सिखाने वाली अवधि है, डरने की नहीं; नियमित दिनचर्या, सेवा और धैर्य "
                         "इसे हल्का करते हैं।"),
        "sade.dhaiya": "<strong>साढ़ेसाती नहीं</strong>, पर शनि की ढैया चल रही है (ऊपर देखें)।",
        "sade.none": ("<strong>साढ़ेसाती नहीं</strong> — शनि आपकी राशि से 12वें, पहले या दूसरे भाव में "
                      "नहीं हैं।"),
        "panchang": ("<h2>आज का पंचांग</h2><p>नई दिल्ली में सूर्योदय के समय "
                     "<strong>{paksha_full} {tithi}</strong> "
                     "तिथि और <strong>{nakshatra}</strong> नक्षत्र है। राहु काल, "
                     'सूर्योदय और पूरा पंचांग <a href="/panchang">आज के पंचांग</a> में देखें।</p>'),
        "personal": ("<p class=\"note\">यह राशिफल केवल आपकी चंद्र राशि से चंद्रमा, शनि, गुरु और "
                     "राहु-केतु के गोचर पर आधारित है — एक ही राशि वाले सभी लोगों के लिए समान। व्यक्तिगत "
                     "फलादेश आपकी पूरी जन्म कुंडली — लग्न, दशा और अष्टकवर्ग — से होता है। अपनी चंद्र "
                     "राशि नहीं पता? आपकी मुफ़्त कुंडली में यह सबसे ऊपर दिखती है।</p>"),
        "cta": "अपनी मुफ़्त कुंडली बनाएँ — फिर अपनी कुंडली पर प्रश्न पूछें",
        "signs.head": "अन्य राशियों का आज का राशिफल",
        "more.head": "और भी",
        "method": ("<h2>यह कैसे निकाला गया</h2><p>ग्रहों की स्थिति आज (भारतीय मानक समय) के लिए स्विस "
                   "एफ़ेमेरिस से निरयण (लाहिड़ी अयनांश) पद्धति में गणना की गई है — वही जो हमारी कुंडली और "
                   "पंचांग में प्रयुक्त है। भाव आपकी चंद्र राशि से गिने गए हैं (गोचर)। शुभ-अशुभ का आधार "
                   "वराहमिहिर की बृहत्संहिता (अध्याय 104) और मंत्रेश्वर की फलदीपिका (अध्याय 26) की "
                   "शास्त्रीय गोचर पद्धति है: चंद्रमा 1, 3, 6, 7, 10, 11वें भाव में शुभ; शनि और "
                   "राहु-केतु 3, 6, 11वें में; गुरु 2, 5, 7, 9, 11वें में।</p>"),
        "i.title": "आज का राशिफल, {date} — सभी 12 राशियों का दैनिक राशिफल | {brand}",
        "i.desc": ("आज का राशिफल ({weekday}, {date}) मेष से मीन "
                   "तक सभी 12 राशियों के लिए — चंद्र गोचर, शनि-गुरु-राहु का प्रभाव और साढ़ेसाती, "
                   "निरयण (लाहिड़ी) गणना पर आधारित।"),
        "i.h1": "आज का राशिफल",
        "i.sub": "Aaj ka Rashifal — today's horoscope for all 12 signs",
        "i.intro": ("<p>राशिफल आपकी <strong>चंद्र राशि</strong> से पढ़ा जाता है। {moon_text} शनि "
                    "{sat_sign} में हैं, इसलिए {sade_names} राशि वालों की साढ़ेसाती चल रही है।</p>"),
        "i.moon_two": ("चंद्रमा {time} (IST) तक {now} में, फिर {next} में। तालिका दिन के "
                       "अधिकांश भाग वाली स्थिति दिखाती है।"),
        "i.moon_one": "आज पूरे दिन चंद्रमा {now} में है।",
        "i.name": "{local} <small>{name}</small>",
        "i.sade": "<small>साढ़ेसाती</small>",
        "i.head_row": "<tr><th>राशि</th><th>चंद्रमा</th><th>आज</th></tr>",
        "nf.title": "राशि नहीं मिली",
        "nf.body": "<h1>राशि नहीं मिली</h1><p>“{slug}” नाम की कोई राशि नहीं है। नीचे अपनी राशि चुनें।</p>",
    },

    # -- Tamil (DIVASTRO-123) ------------------------------------------------
    "ta": {
        "house.1": "முதல்", "house.2": "இரண்டாம்", "house.3": "மூன்றாம்", "house.4": "நான்காம்",
        "house.5": "ஐந்தாம்", "house.6": "ஆறாம்", "house.7": "ஏழாம்", "house.8": "எட்டாம்",
        "house.9": "ஒன்பதாம்", "house.10": "பத்தாம்", "house.11": "பதினொன்றாம்",
        "house.12": "பன்னிரண்டாம்",
        "house_short": "{house} வீடு",
        "rx": " (வக்ரம்)",
        "planet.Moon": "சந்திரன்", "planet.Saturn": "சனி", "planet.Jupiter": "குரு",
        "planet.Rahu": "ராகு", "planet.Ketu": "கேது",
        "sign_label": "{local}",
        "sign_link": "{local}",
        "sign_crumb": "{local}",
        "sade_name": "{local}",
        "crumb_root": "இன்றைய ராசி பலன்",
        "sub_lang": "ta",
        "s.title": "இன்றைய {local} ராசி பலன், {date_short} | {brand}",
        "s.desc": ("{local} ராசிக்கு இன்றைய ராசி பலன் ({weekday}, {date}): சந்திரன் உங்கள் "
                   "ராசிக்கு {house} வீட்டில் — {tone}. கூடவே சனி, குரு, ராகு-கேது பெயர்ச்சி, "
                   "ஏழரைச் சனி நிலை மற்றும் இன்றைய பஞ்சாங்கம்."),
        "s.h1": "இன்றைய {local} ராசி பலன்",
        "s.sub": "{local} ராசி பலன் இன்று — சந்திர கோசாரம்",
        "s.summary": "சந்திரன் உங்கள் ராசிக்கு {house} வீட்டில் இருக்கிறார்.",
        "s.about_rashi": "{local} ராசி — குணங்கள், நட்சத்திரங்கள், பெயர் எழுத்துகள்",
        "moon.head": "இன்றைய சந்திர கோசாரம்",
        "moon.allday": "இன்று நாள் முழுவதும் சந்திரன் {sign} ராசியில் — உங்கள் ராசிக்கு {house} வீட்டில்.",
        "moon.until": ("<strong>{time} (IST) வரை:</strong> சந்திரன் {sign} ராசியில் — உங்கள் "
                       "ராசிக்கு {house} வீட்டில்."),
        "moon.from": ("<strong>{time} (IST) முதல்:</strong> சந்திரன் {sign} ராசிக்குள் நுழைகிறார் — "
                      "உங்கள் ராசிக்கு {house} வீட்டில்."),
        "moon.two": ("<p>இன்று பகலில் சந்திரன் ராசி மாறுகிறார்; எனவே நாளை இரண்டு பகுதிகளாகப் "
                     "பாருங்கள்.</p>"),
        "back.head": "நீண்ட காலப் பின்னணி: மெதுவான கிரகப் பெயர்ச்சிகள்",
        "back.intro": ("<p>இந்தக் கிரகங்கள் ஒரு ராசியில் பல மாதங்கள் அல்லது ஆண்டுகள் தங்குகின்றன; "
                       "ஒவ்வொரு நாளும் நடக்கும் பின்னணியை இவையே அமைக்கின்றன.</p>"),
        "back.where": "{sign}{rx} · {house} வீடு",
        "phase.1": "முதல் (விரயச் சனி)", "phase.2": "இரண்டாம் (ஜென்மச் சனி)",
        "phase.3": "மூன்றாம் (பாதச் சனி)",
        "sade.running": ("<strong>ஏழரைச் சனி நடக்கிறது</strong> — {phase} கட்டம். இது அஞ்ச "
                         "வேண்டிய காலம் அல்ல; மெதுவாக ஒழுங்கைக் கற்றுத்தரும் காலம். சீரான அன்றாட "
                         "வழக்கம், சேவை, பொறுமை ஆகியவை இதை எளிதாக்கும்."),
        "sade.dhaiya": ("<strong>ஏழரைச் சனி இல்லை</strong>, ஆனால் அர்த்தாஷ்டம / அஷ்டம சனி "
                        "நடக்கிறது (மேலே பார்க்கவும்)."),
        "sade.none": ("<strong>ஏழரைச் சனி இல்லை</strong> — சனி உங்கள் ராசிக்கு 12, 1 அல்லது "
                      "2-ஆம் வீட்டில் இல்லை."),
        "panchang": ("<h2>இன்றைய பஞ்சாங்கம்</h2><p>புது தில்லியில் சூரிய உதயத்தின்போது "
                     "<strong>{paksha} {tithi}</strong> திதி, சந்திரன் <strong>{nakshatra}</strong> "
                     "நட்சத்திரத்தில். ராகு காலம், சூரிய உதயம், முழு பஞ்சாங்கம் ஆகியவற்றை "
                     '<a href="/panchang">இன்றைய பஞ்சாங்கம்</a> பக்கத்தில் பாருங்கள்.</p>'),
        "personal": ("<p class=\"note\">இந்த ராசி பலன் உங்கள் சந்திர ராசியை மட்டும் வைத்துக் "
                     "கணிக்கப்பட்டது — அதே ராசியில் சந்திரன் இருக்கும்போது பிறந்த அனைவருக்கும் "
                     "ஒன்றே. தனிப்பட்ட பலனுக்கு உங்கள் முழு ஜாதகம் தேவை: லக்னம், நடப்பு தசை, "
                     "ஒவ்வொரு பெயர்ச்சியின் அஷ்டகவர்க்க பலம். உங்கள் சந்திர ராசி தெரியவில்லையா? "
                     "உங்கள் இலவச ஜாதகம் முதலில் காட்டுவது அதைத்தான் — அது பொதுவாக மேற்கத்திய "
                     "சூரிய ராசி அல்ல.</p>"),
        "cta": "உங்கள் இலவச ஜாதகத்தைப் பெறுங்கள் — பிறகு உங்கள் ஜாதகம் பற்றிக் கேள்வி கேளுங்கள்",
        "signs.head": "எல்லா ராசிகளுக்கும் இன்றைய ராசி பலன்",
        "more.head": "மேலும் இலவசக் கருவிகள்",
        "method": ("<h2>இது எப்படிக் கணிக்கப்படுகிறது</h2><p>இன்றைய (IST) கிரக நிலைகள் சுவிஸ் "
                   "எஃபெமெரிஸ் கொண்டு நிராயன (லாஹிரி அயனாம்சம்) முறையில் கணிக்கப்படுகின்றன — "
                   "எங்கள் ஜாதகமும் பஞ்சாங்கமும் பயன்படுத்தும் அதே நிலைகள். பாரம்பரிய கோசார "
                   "முறைப்படி வீடுகள் உங்கள் சந்திர ராசியிலிருந்து எண்ணப்படுகின்றன. எந்த வீடுகள் "
                   "சாதகம் என்பது வராகமிகிரரின் பிருஹத் சம்ஹிதை (அத்தியாயம் 104), மந்திரேஸ்வரரின் "
                   "பலதீபிகை (அத்தியாயம் 26) ஆகியவற்றின் முறைப்படி: சந்திரன் 1, 3, 6, 7, 10, "
                   "11-ஆம் வீடுகளில் சாதகம்; சனி, ராகு, கேது 3, 6, 11-இல்; குரு 2, 5, 7, 9, "
                   "11-இல்.</p>"),
        "i.title": "இன்றைய ராசி பலன், {date_short} — 12 ராசிகளுக்கும் | {brand}",
        "i.desc": ("இன்றைய ராசி பலன் ({weekday}, {date}): மேஷம் முதல் மீனம் வரை 12 சந்திர "
                   "ராசிகளுக்கும் — சந்திர கோசாரம், சனி, குரு, ராகு பெயர்ச்சி, ஏழரைச் சனி; "
                   "நிராயன முறையில் கணிக்கப்பட்டது."),
        "i.h1": "இன்றைய ராசி பலன்",
        "i.sub": "இன்று ராசி பலன் — மேஷம் முதல் மீனம் வரை 12 ராசிகளுக்கும்",
        "i.intro": ("<p>ராசி பலன் உங்கள் <strong>சந்திர ராசியை</strong> வைத்துப் "
                    "பார்க்கப்படுகிறது. {moon_text} சனி {sat_sign} ராசியில் இருப்பதால் "
                    "{sade_names} ராசிகளுக்கு ஏழரைச் சனி நடக்கிறது.</p>"),
        "i.moon_two": ("சந்திரன் {time} (IST) வரை {now} ராசியில், பிறகு {next} ராசியில். "
                       "அட்டவணை நாளின் பெரும்பகுதிக்கான நிலையைக் காட்டுகிறது."),
        "i.moon_one": "இன்று நாள் முழுவதும் சந்திரன் {now} ராசியில்.",
        "i.name": "{local}",
        "i.sade": "<small>ஏழரைச் சனி</small>",
        "i.head_row": "<tr><th>ராசி</th><th>சந்திரன்</th><th>இன்று</th></tr>",
        "nf.title": "ராசி கிடைக்கவில்லை",
        "nf.body": ("<h1>ராசி கிடைக்கவில்லை</h1><p>“{slug}” என்ற பெயரில் ராசி இல்லை. கீழே "
                    "உங்கள் சந்திர ராசியைத் தேர்ந்தெடுங்கள்.</p>"),
    },

    # -- Malayalam (DIVASTRO-123) --------------------------------------------
    "ml": {
        "house.1": "ഒന്നാം", "house.2": "രണ്ടാം", "house.3": "മൂന്നാം", "house.4": "നാലാം",
        "house.5": "അഞ്ചാം", "house.6": "ആറാം", "house.7": "ഏഴാം", "house.8": "എട്ടാം",
        "house.9": "ഒമ്പതാം", "house.10": "പത്താം", "house.11": "പതിനൊന്നാം",
        "house.12": "പന്ത്രണ്ടാം",
        "house_short": "{house} ഭാവം",
        "rx": " (വക്രം)",
        "planet.Moon": "ചന്ദ്രൻ", "planet.Saturn": "ശനി", "planet.Jupiter": "വ്യാഴം",
        "planet.Rahu": "രാഹു", "planet.Ketu": "കേതു",
        "sign_label": "{local}",
        "sign_link": "{local}",
        "sign_crumb": "{local}",
        "sade_name": "{local}",
        "crumb_root": "ഇന്നത്തെ രാശിഫലം",
        "sub_lang": "ml",
        "s.title": "{local} രാശിഫലം ഇന്ന്, {date_short} — നക്ഷത്രഫലം | {brand}",
        "s.desc": ("{local} രാശിക്കാരുടെ ഇന്നത്തെ രാശിഫലം ({weekday}, {date}): ചന്ദ്രൻ നിങ്ങളുടെ "
                   "രാശിയിൽ നിന്ന് {house} ഭാവത്തിൽ — {tone}. ഒപ്പം ശനി, വ്യാഴം, രാഹു-കേതു "
                   "ഗോചരം, ഏഴരശ്ശനി നില, ഇന്നത്തെ പഞ്ചാംഗം."),
        "s.h1": "ഇന്നത്തെ {local} രാശിഫലം",
        "s.sub": "{local} രാശി — ഇന്നത്തെ നക്ഷത്രഫലം",
        "s.summary": "ചന്ദ്രൻ നിങ്ങളുടെ രാശിയിൽ നിന്ന് {house} ഭാവത്തിലാണ്.",
        "s.about_rashi": "{local} രാശി — സ്വഭാവം, നക്ഷത്രങ്ങൾ, പേരിന്റെ ആദ്യാക്ഷരങ്ങൾ",
        "moon.head": "ഇന്നത്തെ ചന്ദ്രഗോചരം",
        "moon.allday": ("ഇന്ന് ദിവസം മുഴുവൻ ചന്ദ്രൻ {sign} രാശിയിൽ — നിങ്ങളുടെ രാശിയിൽ നിന്ന് "
                        "{house} ഭാവത്തിൽ."),
        "moon.until": ("<strong>{time} (IST) വരെ:</strong> ചന്ദ്രൻ {sign} രാശിയിൽ — നിങ്ങളുടെ "
                       "രാശിയിൽ നിന്ന് {house} ഭാവത്തിൽ."),
        "moon.from": ("<strong>{time} (IST) മുതൽ:</strong> ചന്ദ്രൻ {sign} രാശിയിലേക്ക് കടക്കുന്നു "
                      "— നിങ്ങളുടെ രാശിയിൽ നിന്ന് {house} ഭാവത്തിൽ."),
        "moon.two": ("<p>ഇന്ന് പകൽ ചന്ദ്രൻ രാശി മാറുന്നു; അതിനാൽ ദിവസം രണ്ടു ഭാഗമായി "
                     "വായിക്കുക.</p>"),
        "back.head": "ദീർഘകാല പശ്ചാത്തലം: മന്ദഗതിയിലുള്ള ഗ്രഹഗോചരം",
        "back.intro": ("<p>ഈ ഗ്രഹങ്ങൾ മാസങ്ങളോ വർഷങ്ങളോ ഒരു രാശിയിൽ തുടരുന്നു; ഓരോ ദിവസവും "
                       "നടക്കുന്നതിന്റെ പശ്ചാത്തലം ഒരുക്കുന്നത് ഇവയാണ്.</p>"),
        "back.where": "{sign}{rx} · {house} ഭാവം",
        "phase.1": "ഒന്നാം (ആരംഭം)", "phase.2": "രണ്ടാം (മൂർധന്യം)", "phase.3": "മൂന്നാം (അവസാനം)",
        "sade.running": ("<strong>ഏഴരശ്ശനി നടക്കുന്നു</strong> — {phase} ഘട്ടം. ഭയപ്പെടേണ്ട "
                         "കാലമല്ല, സാവധാനം അച്ചടക്കം പഠിപ്പിക്കുന്ന കാലമാണിത്; ചിട്ടയായ ദിനചര്യ, "
                         "സേവനം, ക്ഷമ എന്നിവ ഇതിനെ ലഘൂകരിക്കും."),
        "sade.dhaiya": ("<strong>ഏഴരശ്ശനി ഇല്ല</strong>, എന്നാൽ കണ്ടകശ്ശനി / അഷ്ടമശ്ശനി "
                        "നടക്കുന്നു (മുകളിൽ കാണുക)."),
        "sade.none": ("<strong>ഏഴരശ്ശനി ഇല്ല</strong> — ശനി നിങ്ങളുടെ രാശിയിൽ നിന്ന് 12, 1, 2 "
                      "ഭാവങ്ങളിൽ ഇല്ല."),
        "panchang": ("<h2>ഇന്നത്തെ പഞ്ചാംഗം</h2><p>ന്യൂഡൽഹിയിൽ സൂര്യോദയ സമയത്ത് "
                     "<strong>{paksha} പക്ഷ {tithi}</strong> തിഥിയും ചന്ദ്രൻ "
                     "<strong>{nakshatra}</strong> നക്ഷത്രത്തിലുമാണ്. രാഹുകാലം, സൂര്യോദയം, മുഴുവൻ "
                     'പഞ്ചാംഗം എന്നിവ <a href="/panchang">ഇന്നത്തെ പഞ്ചാംഗം</a> പേജിൽ കാണാം.</p>'),
        "personal": ("<p class=\"note\">ഈ രാശിഫലം നിങ്ങളുടെ ചന്ദ്രരാശി (കൂറ്) മാത്രം "
                     "അടിസ്ഥാനമാക്കിയുള്ളതാണ് — ചന്ദ്രൻ ആ രാശിയിലായിരിക്കെ ജനിച്ച എല്ലാവർക്കും "
                     "ഒരുപോലെ. വ്യക്തിപരമായ ഫലത്തിന് നിങ്ങളുടെ പൂർണ ജാതകം വേണം: ലഗ്നം, നടക്കുന്ന "
                     "ദശ, ഓരോ ഗോചരത്തിന്റെയും അഷ്ടകവർഗ ബലം. നിങ്ങളുടെ കൂറ് അറിയില്ലേ? നിങ്ങളുടെ "
                     "സൗജന്യ ജാതകം ആദ്യം കാണിക്കുന്നത് അതാണ് — സാധാരണയായി അത് പാശ്ചാത്യ "
                     "സൂര്യരാശിയല്ല.</p>"),
        "cta": "നിങ്ങളുടെ സൗജന്യ ജാതകം നേടൂ — പിന്നെ സ്വന്തം ജാതകത്തെക്കുറിച്ച് ചോദ്യം ചോദിക്കൂ",
        "signs.head": "എല്ലാ രാശികളുടെയും ഇന്നത്തെ രാശിഫലം",
        "more.head": "കൂടുതൽ സൗജന്യ ടൂളുകൾ",
        "method": ("<h2>ഇത് എങ്ങനെ കണക്കാക്കുന്നു</h2><p>ഇന്നത്തെ (IST) ഗ്രഹസ്ഥിതികൾ സ്വിസ് "
                   "എഫെമെറിസ് ഉപയോഗിച്ച് നിരയന (ലാഹിരി അയനാംശം) രീതിയിൽ കണക്കാക്കുന്നു — "
                   "ഞങ്ങളുടെ ജാതകവും പഞ്ചാംഗവും ഉപയോഗിക്കുന്ന അതേ സ്ഥിതികൾ. പരമ്പരാഗത "
                   "ഗോചരരീതി പോലെ ഭാവങ്ങൾ നിങ്ങളുടെ ചന്ദ്രരാശിയിൽ നിന്ന് എണ്ണുന്നു. ഏതു ഭാവങ്ങൾ "
                   "അനുകൂലമെന്നത് വരാഹമിഹിരന്റെ ബൃഹത്സംഹിത (അധ്യായം 104), മന്ത്രേശ്വരന്റെ "
                   "ഫലദീപിക (അധ്യായം 26) എന്നിവയുടെ രീതി പിന്തുടരുന്നു: ചന്ദ്രൻ 1, 3, 6, 7, 10, "
                   "11 ഭാവങ്ങളിൽ അനുകൂലം; ശനി, രാഹു, കേതു 3, 6, 11-ൽ; വ്യാഴം 2, 5, 7, 9, "
                   "11-ൽ.</p>"),
        "i.title": "ഇന്നത്തെ രാശിഫലം, {date_short} — നക്ഷത്രഫലം | {brand}",
        "i.desc": ("ഇന്നത്തെ രാശിഫലം ({weekday}, {date}): മേടം മുതൽ മീനം വരെ 12 ചന്ദ്രരാശികൾക്കും "
                   "— ചന്ദ്രഗോചരം, ശനി, വ്യാഴം, രാഹു എന്നിവയുടെ സ്വാധീനം, ഏഴരശ്ശനി; നിരയന "
                   "രീതിയിൽ കണക്കാക്കിയത്."),
        "i.h1": "ഇന്നത്തെ രാശിഫലം",
        "i.sub": "ഇന്നത്തെ നക്ഷത്രഫലം — മേടം മുതൽ മീനം വരെ 12 രാശികൾക്കും",
        "i.intro": ("<p>രാശിഫലം നിങ്ങളുടെ <strong>ചന്ദ്രരാശി</strong> (കൂറ്) അടിസ്ഥാനമാക്കിയാണ് "
                    "വായിക്കുന്നത്. {moon_text} ശനി {sat_sign} രാശിയിലായതിനാൽ {sade_names} "
                    "രാശിക്കാർക്ക് ഏഴരശ്ശനി നടക്കുന്നു.</p>"),
        "i.moon_two": ("ചന്ദ്രൻ {time} (IST) വരെ {now} രാശിയിൽ, പിന്നെ {next} രാശിയിൽ. പട്ടിക "
                       "ദിവസത്തിന്റെ ഭൂരിഭാഗം സമയത്തെ സ്ഥിതി കാണിക്കുന്നു."),
        "i.moon_one": "ഇന്ന് ദിവസം മുഴുവൻ ചന്ദ്രൻ {now} രാശിയിൽ.",
        "i.name": "{local}",
        "i.sade": "<small>ഏഴരശ്ശനി</small>",
        "i.head_row": "<tr><th>രാശി</th><th>ചന്ദ്രൻ</th><th>ഇന്ന്</th></tr>",
        "nf.title": "രാശി കണ്ടെത്തിയില്ല",
        "nf.body": ("<h1>രാശി കണ്ടെത്തിയില്ല</h1><p>“{slug}” എന്ന പേരിൽ ഒരു രാശിയില്ല. താഴെ "
                    "നിന്ന് നിങ്ങളുടെ ചന്ദ്രരാശി തിരഞ്ഞെടുക്കുക.</p>"),
    },

    # A language's fallback for a key it has not translated, before English:
    # the sign names in its own script.
    "_native": {
        "sign_label": "{local} ({name})",
        "sign_link": "{local} · {english}",
        "sign_crumb": "{local}",
        "sade_name": "{local}",
        "i.name": "{local} <small>{english}</small>",
    },
}

# "More free tools" at the foot of every page: (href, link text). "{twin}" is
# this page in the other language the list offers.
MORE_LINKS: dict[str, tuple[tuple[str, str], ...]] = {
    "en": (("{twin:hi}", "हिन्दी में पढ़ें"), ("/panchang", "Today's Panchang"),
           ("/rahu-kaal", "Rahu Kaal today"), ("/choghadiya", "Choghadiya today"),
           ("/kundali-milan", "Kundali Milan"), ("/vrat-tyohar", "Today's vrat & festivals")),
    "hi": (("{twin:en}", "Read in English"), ("/panchang", "आज का पंचांग"),
           ("/rahu-kaal", "आज का राहु काल"), ("/choghadiya", "आज का चौघड़िया"),
           ("/kundali-milan", "कुंडली मिलान"), ("/hi/vrat-tyohar", "आज के व्रत और त्योहार")),
    "ta": (("/panchang", "இன்றைய பஞ்சாங்கம்"), ("/rahu-kaal", "இன்று ராகு காலம்"),
           ("/choghadiya", "இன்றைய சௌகடியா முகூர்த்தம்"), ("/kundali-milan", "ஜாதகப் பொருத்தம்"),
           ("/vrat-tyohar", "இன்றைய விரதங்கள், பண்டிகைகள்")),
    "ml": (("/panchang", "ഇന്നത്തെ പഞ്ചാംഗം"), ("/rahu-kaal", "രാഹുകാലം ഇന്ന്"),
           ("/choghadiya", "ഇന്നത്തെ ചോഘടിയ മുഹൂർത്തം"), ("/kundali-milan", "ജാതകപ്പൊരുത്തം"),
           ("/vrat-tyohar", "ഇന്നത്തെ വ്രതങ്ങളും ഉത്സവങ്ങളും")),
}

# The rashifal's clock times are printed "6:29 AM" on the Hindi pages too (as
# they always have been); other languages use their own clock words.
CLOCK_LANG = {"hi": "en"}

# -- the phrase bank: see rashifal_pages' docstring for the classical scheme --

TONE_LABEL = {
    "en": {GOOD: "Favourable day", MIXED: "Mixed day", EASY: "Take it easy"},
    "hi": {GOOD: "अनुकूल दिन", MIXED: "मिश्रित दिन", EASY: "संयम का दिन"},
    "ta": {GOOD: "சாதகமான நாள்", MIXED: "கலவையான நாள்", EASY: "நிதானமாக இருங்கள்"},
    "ml": {GOOD: "അനുകൂല ദിവസം", MIXED: "സമ്മിശ്ര ദിവസം", EASY: "സാവധാനം നീങ്ങുക"},
}
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


# -- Tamil / Malayalam (DIVASTRO-123) ------------------------------------------
# The phrase bank in ta and ml, attached to the entries above (house 1..12).

_MOON_TA_ML = {
    1: ("இன்று சந்திரன் உங்கள் சொந்த ராசியில் சஞ்சரிக்கிறார் (ஜென்ம சந்திரன்). இதை மனநிறைவும் "
        "உற்சாகமும் தரும் நாளாக நூல்கள் கூறுகின்றன — நல்ல உணவு, அன்பானவர்களின் துணை, உங்களைப் "
        "பற்றிய தெளிவு. உங்கள் தேவைகளைக் கவனிக்கவும் சிறிய தனிப்பட்ட காரியங்களைத் தொடங்கவும் "
        "நல்ல நாள்.",
        "ഇന്ന് ചന്ദ്രൻ നിങ്ങളുടെ സ്വന്തം രാശിയിലൂടെ സഞ്ചരിക്കുന്നു (ജന്മചന്ദ്രൻ). സുഖവും "
        "സന്തോഷവും നൽകുന്ന ദിവസമായാണ് ശാസ്ത്രങ്ങൾ ഇതിനെ കാണുന്നത് — നല്ല ഭക്ഷണം, "
        "പ്രിയപ്പെട്ടവരുടെ സാന്നിധ്യം, മനസ്സിൽ തെളിമ. സ്വന്തം ആവശ്യങ്ങൾ ശ്രദ്ധിക്കാനും ചെറിയ "
        "വ്യക്തിപരമായ കാര്യങ്ങൾ തുടങ്ങാനും നല്ല ദിവസം."),
    2: ("இன்று சந்திரன் உங்கள் ராசிக்கு 2-ஆம் வீட்டில். பணத்திலும் பேச்சிலும் கவனம் தேவை என்பது "
        "மரபு — செலவுகள் கூடலாம், சிறு தவறான புரிதல்கள் எளிதில் வரலாம். செலவைத் திட்டமிட்டுச் "
        "செய்யுங்கள், வீட்டில் மென்மையாகப் பேசுங்கள்; அன்றாட வேலைகள் நன்றாக நடக்கும்.",
        "ഇന്ന് ചന്ദ്രൻ നിങ്ങളുടെ 2-ാം ഭാവത്തിൽ. പണത്തിലും വാക്കിലും ശ്രദ്ധ വേണമെന്നാണ് "
        "പാരമ്പര്യം — ചെലവുകൾ കൂടാം, ചെറിയ തെറ്റിദ്ധാരണകൾ എളുപ്പത്തിൽ ഉണ്ടാകാം. ചെലവ് "
        "ആസൂത്രണം ചെയ്യുക, വീട്ടിൽ സൗമ്യമായി സംസാരിക്കുക; പതിവു ജോലികൾ നന്നായി നടക്കും."),
    3: ("3-ஆம் வீட்டில் சந்திரன் சாதகமான கோசாரம். தைரியமும் முனைப்பும் அதிகம், முயற்சிக்குப் "
        "பலன் கிடைக்கும், உடன்பிறந்தவர்கள், நண்பர்கள், அண்டை வீட்டாருடன் தொடர்பு நன்றாக "
        "இருக்கும். சிறு பயணங்கள், அழைப்புகள், நிலுவையில் உள்ள வேலையை முடிப்பதற்கு நல்ல நாள்.",
        "3-ാം ഭാവത്തിലെ ചന്ദ്രൻ അനുകൂലമായ ഗോചരമാണ്. ധൈര്യവും ഉത്സാഹവും കൂടുതലായിരിക്കും, "
        "പ്രയത്നത്തിന് ഫലം ലഭിക്കും, സഹോദരങ്ങൾ, സുഹൃത്തുക്കൾ, അയൽക്കാർ എന്നിവരുമായുള്ള ബന്ധം "
        "നന്നായി പോകും. ചെറുയാത്രകൾക്കും ഫോൺവിളികൾക്കും മുടങ്ങിക്കിടക്കുന്ന ജോലി "
        "പൂർത്തിയാക്കാനും നല്ല ദിവസം."),
    4: ("4-ஆம் வீட்டில் சந்திரன் மனதைச் சற்று அமைதியற்றதாக்கலாம் — வீட்டு விஷயங்களோ பயணமோ "
        "சோர்வாகத் தோன்றலாம். நாளை எளிமையாக வைத்துக்கொள்ளுங்கள், வீட்டில் வாக்குவாதங்களைத் "
        "தவிர்த்து, சிறிது நேரம் அமைதியாக இருங்கள்; சந்திரன் நகர்ந்ததும் மனம் லேசாகும்.",
        "4-ാം ഭാവത്തിലെ ചന്ദ്രൻ മനസ്സിനെ അൽപം അസ്വസ്ഥമാക്കിയേക്കാം — വീട്ടുകാര്യങ്ങളോ യാത്രയോ "
        "ക്ഷീണമായി തോന്നാം. ദിവസം ലളിതമാക്കുക, വീട്ടിൽ തർക്കങ്ങൾ ഒഴിവാക്കുക, കുറച്ചു സമയം "
        "ശാന്തമായി ചെലവഴിക്കുക; ചന്ദ്രൻ നീങ്ങുന്നതോടെ മനസ്സ് തെളിയും."),
    5: ("5-ஆம் வீட்டில் சந்திரன் கலவையான பலன் தரும். திட்டங்களில் சிறு தடைகள் வரலாம், மனம் பல "
        "யோசனைகளுக்கு இடையே ஊசலாடலாம். ஊக முடிவுகளைத் தவிர்க்கவும்; படிப்பு, படைப்பு வேலை, "
        "குழந்தைகளுடன் நேரம் செலவிடுவது இன்றைக்கு நல்லது.",
        "5-ാം ഭാവത്തിലെ ചന്ദ്രൻ സമ്മിശ്ര ഫലം നൽകുന്നു. പദ്ധതികൾക്ക് ചെറിയ തടസ്സങ്ങൾ വരാം, മനസ്സ് "
        "പല ആശയങ്ങൾക്കിടയിൽ ചാഞ്ചാടാം. ഊഹാധിഷ്ഠിത തീരുമാനങ്ങൾ ഒഴിവാക്കുക; പഠനം, സർഗാത്മക "
        "ജോലി, കുട്ടികളോടൊപ്പമുള്ള സമയം എന്നിവയാണ് ഇന്ന് നല്ലത്."),
    6: ("6-ஆம் வீட்டில் சந்திரன் மிகச் சிறந்த கோசாரங்களில் ஒன்று. எதிரிகள், தடைகள் மீது வெற்றியும், "
        "தேங்கிய வேலைகளை முடிக்கும் ஆற்றலும் கிடைக்கும் என்று நூல்கள் கூறுகின்றன. போட்டி "
        "வேலைகள், நிலுவைப் பிரச்சினைகளைத் தீர்ப்பது, சீரான அன்றாட வழக்கம் — இவற்றுக்கு நல்ல நாள்.",
        "6-ാം ഭാവത്തിലെ ചന്ദ്രൻ ഏറ്റവും നല്ല ഗോചരങ്ങളിൽ ഒന്നാണ്. എതിരാളികൾക്കും തടസ്സങ്ങൾക്കും "
        "മേൽ വിജയവും കെട്ടിക്കിടക്കുന്ന ജോലികൾ തീർക്കാനുള്ള ഊർജവും ശാസ്ത്രങ്ങൾ വാഗ്ദാനം "
        "ചെയ്യുന്നു. മത്സരസ്വഭാവമുള്ള ജോലി, തീർപ്പാകാത്ത കാര്യങ്ങൾ പരിഹരിക്കൽ, ചിട്ടയായ "
        "ദിനചര്യ എന്നിവയ്ക്ക് നല്ല ദിവസം."),
    7: ("7-ஆம் வீட்டில் சந்திரன் கூட்டுறவுக்கும் நட்புறவுக்கும் சாதகம். வாழ்க்கைத் துணையுடன் நேரம், "
        "சந்திப்புகள், ஒப்பந்தங்கள் சுமுகமாக நடக்கும்; சுகமும் நல்ல உணவும் கிடைக்கும். "
        "மற்றவர்களை அணுகி இணைந்து செயல்பட நல்ல நாள்.",
        "7-ാം ഭാവത്തിലെ ചന്ദ്രൻ പങ്കാളിത്തത്തിനും കൂട്ടായ്മയ്ക്കും അനുകൂലമാണ്. ജീവിതപങ്കാളിയോടൊപ്പമുള്ള "
        "സമയം, കൂടിക്കാഴ്ചകൾ, കരാറുകൾ എന്നിവ സുഗമമായി നടക്കും, ഒപ്പം സുഖവും നല്ല ഭക്ഷണവും. "
        "മറ്റുള്ളവരെ സമീപിക്കാനും ഒരുമിച്ച് പ്രവർത്തിക്കാനും നല്ല ദിവസം."),
    8: ("இன்று சந்திரன் உங்கள் ராசிக்கு 8-ஆம் வீட்டில் — இதுவே சந்திராஷ்டமம். இன்று முக்கியமான "
        "புதிய காரியங்களைத் தொடங்க வேண்டாம் என்பது மரபு; எதிர்பாராத தாமதங்கள் வரலாம், மனதில் "
        "பதற்றம் இருக்கலாம். நேரத்தில் இடைவெளி வைத்து, பழகிய வேலைகளைச் செய்து, உங்களிடமே "
        "பொறுமையாக இருங்கள் — இது இரண்டு மூன்று நாட்களில் கடந்துவிடும்.",
        "ഇന്ന് ചന്ദ്രൻ നിങ്ങളുടെ 8-ാം ഭാവത്തിൽ — ചന്ദ്രാഷ്ടമം എന്നറിയപ്പെടുന്ന സമയം. ഇന്ന് "
        "പ്രധാനപ്പെട്ട പുതിയ കാര്യങ്ങൾ തുടങ്ങരുതെന്നാണ് പാരമ്പര്യം; അപ്രതീക്ഷിത താമസങ്ങൾക്ക് "
        "സാധ്യത കൂടുതലാണ്, മനസ്സിൽ ആശങ്ക തോന്നാം. സമയക്രമത്തിൽ ഇടവേള വെക്കുക, പരിചിതമായ "
        "ജോലികളിൽ ഉറച്ചുനിൽക്കുക, സ്വയം സൗമ്യത പുലർത്തുക — രണ്ടു മൂന്നു ദിവസത്തിനകം ഇത് "
        "കടന്നുപോകും."),
    9: ("9-ஆம் வீட்டில் சந்திரன் கலவையான பலன் தரும். திட்டங்களுக்குக் கூடுதல் முயற்சி "
        "தேவைப்படலாம், சோர்வோ கவனச் சிதறலோ இருக்கலாம். பெரிய புதிய முயற்சிகளைவிட வழிபாடு, "
        "வாசிப்பு, பெரியோர் அல்லது ஆசிரியர்களுடன் நேரம் செலவிடுவது இன்றைக்குப் பொருத்தம்.",
        "9-ാം ഭാവത്തിലെ ചന്ദ്രൻ സമ്മിശ്ര ഫലം നൽകുന്നു. പദ്ധതികൾക്ക് കൂടുതൽ പ്രയത്നം "
        "വേണ്ടിവരാം, ക്ഷീണമോ ശ്രദ്ധക്കുറവോ തോന്നാം. വലിയ പുതിയ സംരംഭങ്ങളേക്കാൾ പ്രാർഥന, "
        "വായന, മുതിർന്നവരോടോ ഗുരുക്കന്മാരോടോ ഒപ്പമുള്ള സമയം എന്നിവയാണ് ഇന്നേക്ക് ചേരുന്നത്."),
    10: ("10-ஆம் வீட்டில் சந்திரன் வேலைக்கும் நற்பெயருக்கும் துணை நிற்கும். வேலைகள் முடியும், "
         "மேலதிகாரிகள் செவிசாய்ப்பார்கள், உழைப்பு கவனிக்கப்படும். உங்கள் வேலையை முன்வைக்கவும், "
         "தொழிலில் ஓர் அடி முன்னேறவும், கண்ணுக்குத் தெரியும் ஒன்றை முடிக்கவும் நல்ல நாள்.",
         "10-ാം ഭാവത്തിലെ ചന്ദ്രൻ ജോലിക്കും പ്രശസ്തിക്കും തുണയാകുന്നു. ജോലികൾ പൂർത്തിയാകും, "
         "മേലുദ്യോഗസ്ഥർ ശ്രദ്ധിക്കും, പ്രയത്നം അംഗീകരിക്കപ്പെടും. നിങ്ങളുടെ ജോലി അവതരിപ്പിക്കാനോ "
         "തൊഴിലിൽ ഒരു ചുവട് മുന്നോട്ടു വെക്കാനോ ശ്രദ്ധേയമായ ഒന്ന് പൂർത്തിയാക്കാനോ നല്ല ദിവസം."),
    11: ("11-ஆம் வீட்டில் — லாப ஸ்தானத்தில் — சந்திரன் மிகச் சாதகமான கோசாரம். நண்பர்களின் "
         "ஆதரவு, நல்ல செய்தி, முந்தைய முயற்சிகளின் பலன் கிடைக்கலாம். தொடர்புகளை வளர்க்கவும், "
         "கோரிக்கைகள் வைக்கவும், மற்றவர்களுடன் கொண்டாடவும் நல்ல நாள்.",
         "11-ാം ഭാവത്തിലെ — ലാഭഭാവത്തിലെ — ചന്ദ്രൻ വളരെ അനുകൂലമായ ഗോചരമാണ്. സുഹൃത്തുക്കളുടെ "
         "പിന്തുണ, നല്ല വാർത്ത, മുൻപ്രയത്നങ്ങളുടെ ഫലം എന്നിവ പ്രതീക്ഷിക്കാം. ബന്ധങ്ങൾ "
         "വളർത്താനും അഭ്യർഥനകൾ നടത്താനും മറ്റുള്ളവരോടൊപ്പം ആഘോഷിക്കാനും നല്ല ദിവസം."),
    12: ("12-ஆம் வீட்டில் சந்திரன் கூடுதல் செலவுகளையும், சோர்வான, உள்முகமான மனநிலையையும் "
         "தரலாம். அதிகச் செலவையும் இரவில் தாமதமாக விழித்திருப்பதையும் தவிர்க்கவும்; புதிதாகத் "
         "தொடங்குவதைவிட ஓய்வு, வழிபாடு, தானம், பழைய வேலைகளை முடிப்பது இன்றைக்கு ஏற்றது.",
         "12-ാം ഭാവത്തിലെ ചന്ദ്രൻ അധികച്ചെലവും ക്ഷീണിച്ച, ഉൾവലിഞ്ഞ മനോഭാവവും നൽകിയേക്കാം. "
         "അമിതച്ചെലവും രാത്രി വൈകിയുള്ള ഉറക്കമൊഴിയലും ഒഴിവാക്കുക; പുതിയത് തുടങ്ങുന്നതിനേക്കാൾ "
         "വിശ്രമം, പ്രാർഥന, ദാനം, പഴയ ജോലികൾ തീർക്കൽ എന്നിവയ്ക്കാണ് ഇന്ന് യോജിച്ചത്."),
}

_SATURN_TA_ML = {
    1: ("சனி உங்கள் சந்திர ராசியைக் கடந்து செல்கிறார் — ஏழரைச் சனியின் உச்சக் கட்டம் "
        "(ஜென்மச் சனி). பொறுமை, சீரான வழக்கம், நேர்மையான உழைப்புக்கு இது பலன் தரும்; சற்றுக் "
        "குறைவாகவே ஏற்றுக்கொண்டு, தொடங்கியதை முடியுங்கள்.",
        "ശനി നിങ്ങളുടെ ചന്ദ്രരാശിയിലൂടെ കടന്നുപോകുന്നു — ഏഴരശ്ശനിയുടെ മൂർധന്യഘട്ടം "
        "(ജന്മശ്ശനി). ക്ഷമ, ചിട്ട, സത്യസന്ധമായ പ്രയത്നം എന്നിവയ്ക്ക് ഇത് ഫലം നൽകും; അൽപം "
        "കുറച്ചു മാത്രം ഏറ്റെടുക്കുക, തുടങ്ങിയത് പൂർത്തിയാക്കുക."),
    2: ("சனி 2-ஆம் வீட்டில் — ஏழரைச் சனியின் கடைசிக் கட்டம் (பாதச் சனி). செலவிலும் வீட்டில் "
        "பேச்சிலும் அளவோடு இருங்கள்; அழுத்தம் குறைந்து வருகிறது.",
        "ശനി 2-ാം ഭാവത്തിൽ — ഏഴരശ്ശനിയുടെ അവസാന ഘട്ടം. ചെലവിലും വീട്ടിലെ സംസാരത്തിലും "
        "മിതത്വം പാലിക്കുക; സമ്മർദം കുറഞ്ഞുവരുന്നു."),
    3: ("3-ஆம் வீட்டில் சனி மிகச் சிறந்த நிலைகளில் ஒன்று — தொடர்ந்த முயற்சி பலன் தரும், "
        "தைரியம் வளரும், நீண்ட நாள் வேலைகள் வேகம் பெறும்.",
        "3-ാം ഭാവത്തിലെ ശനി ഏറ്റവും നല്ല സ്ഥാനങ്ങളിൽ ഒന്നാണ് — സ്ഥിരപ്രയത്നം ഫലം കാണും, "
        "ധൈര്യം വർധിക്കും, ഏറെക്കാലമായി നടക്കുന്ന ജോലികൾ പുരോഗമിക്കും."),
    4: ("4-ஆம் வீட்டில் சனி (அர்த்தாஷ்டம சனி, கண்டகச் சனி) வீட்டு வாழ்க்கையையும் மன "
        "அமைதியையும் சற்றுக் கனமாக்கலாம்; அன்றாட வழக்கத்தை எளிமையாக வைத்து, குடும்ப "
        "விஷயங்களை அமைதியாகக் கையாளுங்கள்.",
        "4-ാം ഭാവത്തിലെ ശനി (കണ്ടകശ്ശനി) കുടുംബജീവിതത്തിനും മനസ്സമാധാനത്തിനും ഭാരം "
        "തോന്നിച്ചേക്കാം; ദിനചര്യ ലളിതമാക്കുക, കുടുംബകാര്യങ്ങൾ ശാന്തമായി കൈകാര്യം ചെയ്യുക."),
    5: ("5-ஆம் வீட்டில் சனி திட்டங்கள், படிப்பு, குழந்தைகள் விஷயங்களில் பொறுமையைக் "
        "கேட்கிறார் — அவசரத்தைவிட மெதுவாகக் கவனமாகச் செல்வதே நல்லது.",
        "5-ാം ഭാവത്തിലെ ശനി പദ്ധതികളിലും പഠനത്തിലും കുട്ടികളുടെ കാര്യങ്ങളിലും ക്ഷമ "
        "ആവശ്യപ്പെടുന്നു — തിടുക്കത്തേക്കാൾ നല്ലത് സാവധാനം ശ്രദ്ധയോടെ നീങ്ങുന്നതാണ്."),
    6: ("6-ஆம் வீட்டில் சனி உங்களுக்குச் சாதகம் — ஒழுக்கத்தால் எதிரிகளையும் தேங்கிய "
        "வேலைகளையும் வெல்லலாம், கடின உழைப்பு கவனிக்கப்படும்.",
        "6-ാം ഭാവത്തിലെ ശനി നിങ്ങൾക്ക് അനുകൂലമാണ് — അച്ചടക്കം എതിരാളികളെയും "
        "കെട്ടിക്കിടക്കുന്ന ജോലികളെയും മറികടക്കും, കഠിനാധ്വാനം ശ്രദ്ധിക്കപ്പെടും."),
    7: ("7-ஆம் வீட்டில் சனி கூட்டாண்மைகளை மெதுவான, தீவிரமான கோணத்தில் வைக்கிறார் — "
        "தெளிவான ஒப்பந்தங்களும் பொறுமையும் உதவும்.",
        "7-ാം ഭാവത്തിലെ ശനി പങ്കാളിത്തങ്ങൾക്ക് മന്ദവും ഗൗരവമുള്ളതുമായ ഭാവം നൽകുന്നു — "
        "വ്യക്തമായ ധാരണകളും ക്ഷമയും സഹായിക്കും."),
    8: ("8-ஆம் வீட்டில் சனி (அஷ்டம சனி) — குறுக்கு வழிகளைத் தவிர்த்து, தாமதங்களுக்கு நேர "
        "இடைவெளி வைத்துக்கொள்ள வேண்டிய காலம்.",
        "8-ാം ഭാവത്തിലെ ശനി (അഷ്ടമശ്ശനി) — കുറുക്കുവഴികൾ ഒഴിവാക്കി, താമസങ്ങൾക്കായി സമയം "
        "കരുതിവെക്കേണ്ട കാലം."),
    9: ("9-ஆம் வீட்டில் சனி அதிர்ஷ்டத்தையும் நீண்ட பயணங்களையும் மெதுவாக்கலாம்; பெரியோரை "
        "மதிப்பதும் கடமையைச் சீராகச் செய்வதும் விஷயங்களைச் சரியான பாதையில் வைக்கும்.",
        "9-ാം ഭാവത്തിലെ ശനി ഭാഗ്യത്തെയും ദീർഘയാത്രകളെയും മന്ദഗതിയിലാക്കിയേക്കാം; "
        "മുതിർന്നവരോടുള്ള ബഹുമാനവും സ്ഥിരമായ കർത്തവ്യനിർവഹണവും കാര്യങ്ങളെ ശരിയായ വഴിയിൽ "
        "നിർത്തും."),
    10: ("10-ஆம் வீட்டில் சனி வேலையில் பொறுப்பைக் கூட்டுகிறார் — சுமை அதிகம், ஆனால் உண்மையான "
         "உழைப்பு நிலையான நற்பெயரை உருவாக்கும்.",
         "10-ാം ഭാവത്തിലെ ശനി ജോലിയിൽ ഉത്തരവാദിത്തം കൂട്ടുന്നു — ഭാരം കൂടുതലാണ്, എന്നാൽ "
         "ആത്മാർഥമായ പ്രയത്നം നിലനിൽക്കുന്ന പ്രശസ്തി നേടിത്തരും."),
    11: ("11-ஆம் வீட்டில் சனி சாதகம் — லாபம் மெதுவாக ஆனால் உறுதியாக வரும், நீண்ட கால "
         "உழைப்புக்குப் பலன் கிடைக்கத் தொடங்கும்.",
         "11-ാം ഭാവത്തിലെ ശനി അനുകൂലമാണ് — നേട്ടങ്ങൾ സാവധാനമെങ്കിലും ഉറപ്പായും വരും, "
         "ദീർഘകാല പ്രയത്നം ഫലം കണ്ടുതുടങ്ങും."),
    12: ("சனி 12-ஆம் வீட்டில் — ஏழரைச் சனியின் தொடக்கக் கட்டம் (விரயச் சனி). செலவுகளைக் "
         "கவனித்து, நன்றாக ஓய்வெடுங்கள்; அமைதியான, உள்முகமான வேலைகளுக்கு ஏற்ற காலம்.",
         "ശനി 12-ാം ഭാവത്തിൽ — ഏഴരശ്ശനിയുടെ ആരംഭഘട്ടം. ചെലവുകൾ ശ്രദ്ധിക്കുക, നന്നായി "
         "വിശ്രമിക്കുക; ശാന്തവും ആത്മപരിശോധനാപരവുമായ ജോലികൾക്ക് നല്ല സമയം."),
}

_JUPITER_TA_ML = {
    1: ("சந்திர ராசியில் குரு (ஜென்ம குரு) பாரம்பரியமாக அமைதியின்மை தரும் நிலை; திட்டங்களை "
        "நடைமுறைக்கு ஏற்றதாக வைத்து, அளவுக்கு மீறி ஒப்புக்கொள்ள வேண்டாம்.",
        "ചന്ദ്രരാശിയിലെ വ്യാഴം (ജന്മവ്യാഴം) ശാസ്ത്രപ്രകാരം അസ്വസ്ഥതയുടെ സ്ഥാനമാണ്; പദ്ധതികൾ "
        "പ്രായോഗികമാക്കുക, അമിതമായി ഏറ്റെടുക്കാതിരിക്കുക."),
    2: ("2-ஆம் வீட்டில் குரு குடும்ப ஒற்றுமை, சேமிப்பு, இனிய பேச்சுக்குத் துணை நிற்கும்.",
        "2-ാം ഭാവത്തിലെ വ്യാഴം കുടുംബസൗഹാർദം, സമ്പാദ്യം, മധുരമായ സംസാരം എന്നിവയെ "
        "പിന്തുണയ്ക്കുന്നു."),
    3: ("3-ஆம் வீட்டில் குரு — அதே பலனுக்குச் சற்றுக் கூடுதல் உழைப்பு தேவை; தொடர்ந்து முயலுங்கள்.",
        "3-ാം ഭാവത്തിലെ വ്യാഴം — അതേ ഫലത്തിന് അൽപം കൂടുതൽ പ്രയത്നം വേണം; തുടരുക."),
    4: ("4-ஆம் வீட்டில் குரு வீட்டு விஷயங்களில் சலனம் தரலாம்; உறவினர்களிடம் பொறுமை உதவும்.",
        "4-ാം ഭാവത്തിലെ വ്യാഴം വീട്ടുകാര്യങ്ങളിൽ അസ്ഥിരത വരുത്തിയേക്കാം; ബന്ധുക്കളോട് ക്ഷമ "
        "കാണിക്കുന്നത് സഹായിക്കും."),
    5: ("5-ஆம் வீட்டில் குரு கல்வி, குழந்தைகள் விஷயங்கள், படைப்பாற்றல், நல்ல ஆலோசனைக்குச் "
        "சாதகம்.",
        "5-ാം ഭാവത്തിലെ വ്യാഴം പഠനം, കുട്ടികളുടെ കാര്യങ്ങൾ, സർഗാത്മകത, നല്ല ഉപദേശം "
        "എന്നിവയ്ക്ക് അനുകൂലമാണ്."),
    6: ("6-ஆம் வீட்டில் குரு: சிறு தகராறுகளையும் அதிக வேலைப்பளுவையும் தவிர்க்கவும்.",
        "6-ാം ഭാവത്തിലെ വ്യാഴം: ചെറിയ തർക്കങ്ങളും അമിതജോലിയും ഒഴിവാക്കുക."),
    7: ("7-ஆம் வீட்டில் குரு கூட்டாண்மை, திருமணப் பேச்சு, பயணங்களுக்கு அருள் தரும்.",
        "7-ാം ഭാവത്തിലെ വ്യാഴം പങ്കാളിത്തം, വിവാഹാലോചനകൾ, യാത്ര എന്നിവയ്ക്ക് അനുഗ്രഹമാണ്."),
    8: ("8-ஆம் வீட்டில் குரு — பெரிய முடிவுகளில் கவனம் தேவை; நிதானமாகச் செல்லுங்கள்.",
        "8-ാം ഭാവത്തിലെ വ്യാഴം — വലിയ തീരുമാനങ്ങളിൽ ശ്രദ്ധ വേണം; സാവധാനം നീങ്ങുക."),
    9: ("9-ஆம் வீட்டில் குரு மிகச் சிறந்த நிலைகளில் ஒன்று — பாக்கியம், தர்மம், ஆசிரியர்களின் "
        "வழிகாட்டல்.",
        "9-ാം ഭാവത്തിലെ വ്യാഴം ഏറ്റവും നല്ല സ്ഥാനങ്ങളിൽ ഒന്നാണ് — ഭാഗ്യം, ധർമം, ഗുരുക്കന്മാരുടെ "
        "മാർഗനിർദേശം."),
    10: ("10-ஆம் வீட்டில் குரு வேலையில் மாற்றங்களைக் கொண்டுவரலாம்; நெகிழ்வாக இருங்கள்.",
         "10-ാം ഭാവത്തിലെ വ്യാഴം ജോലിയിൽ മാറ്റങ്ങൾ കൊണ്ടുവന്നേക്കാം; വഴക്കത്തോടെ നിൽക്കുക."),
    11: ("11-ஆம் வீட்டில் குரு லாபம், நிறைவேறும் விருப்பங்கள், உதவும் நண்பர்களைத் தரும்.",
         "11-ാം ഭാവത്തിലെ വ്യാഴം നേട്ടങ്ങളും ആഗ്രഹസാഫല്യവും സഹായിക്കുന്ന സുഹൃത്തുക്കളെയും "
         "നൽകുന്നു."),
    12: ("12-ஆம் வீட்டில் குரு செலவுகளைத் தரும், பெரும்பாலும் நல்ல காரியங்களுக்கு; தானமும் "
         "ஆன்மிகப் பயிற்சியும் ஏற்றவை.",
         "12-ാം ഭാവത്തിലെ വ്യാഴം ചെലവുകൾ വരുത്തും, പലപ്പോഴും നല്ല കാര്യങ്ങൾക്കായി; ദാനവും "
         "ആത്മീയസാധനയും ഉചിതമാണ്."),
}

_RAHU_TA_ML = {
    1: ("சந்திர ராசியில் ராகு அமைதியின்மையையும் வழக்கத்துக்கு மாறான ஆசைகளையும் தூண்டலாம்; "
        "நிதானமாக இருங்கள்.",
        "ചന്ദ്രരാശിയിലെ രാഹു അസ്വസ്ഥതയും അസാധാരണ ആഗ്രഹങ്ങളും ഉണർത്തിയേക്കാം; കാലുറപ്പിച്ചു "
        "നിൽക്കുക."),
    2: ("2-ஆம் வீட்டில் ராகு: குடும்பத்தில் பேச்சிலும் பண விஷயங்களிலும் கவனமாக இருங்கள்.",
        "2-ാം ഭാവത്തിലെ രാഹു: കുടുംബത്തിനുള്ളിൽ സംസാരത്തിലും പണസംബന്ധമായ ചർച്ചകളിലും "
        "ശ്രദ്ധിക്കുക."),
    3: ("3-ஆம் வீட்டில் ராகு சாதகம் — துணிச்சலான முயற்சிகளும் தொடர்புகளும் வெற்றி பெறும்.",
        "3-ാം ഭാവത്തിലെ രാഹു അനുകൂലമാണ് — ധീരമായ സംരംഭങ്ങളും ആശയവിനിമയവും വിജയിക്കും."),
    4: ("4-ஆம் வீட்டில் ராகு வீட்டு அமைதியைக் குலைக்கலாம்; சொத்து விஷயங்களில் அவசர "
        "முடிவுகளைத் தவிர்க்கவும்.",
        "4-ാം ഭാവത്തിലെ രാഹു വീട്ടിലെ സമാധാനം ഉലച്ചേക്കാം; വസ്തുസംബന്ധമായ തിടുക്കത്തിലുള്ള "
        "നീക്കങ്ങൾ ഒഴിവാക്കുക."),
    5: ("5-ஆம் வீட்டில் ராகு: ஆபத்தான யோசனைகளை இருமுறை சரிபார்த்து, தெளிவான மனதுடன் இருங்கள்.",
        "5-ാം ഭാവത്തിലെ രാഹു: അപകടസാധ്യതയുള്ള ആശയങ്ങൾ രണ്ടുവട്ടം പരിശോധിക്കുക, മനസ്സ് "
        "തെളിമയോടെ വെക്കുക."),
    6: ("6-ஆம் வீட்டில் ராகு போட்டிகளையும் தடைகளையும் கடக்க உதவும்.",
        "6-ാം ഭാവത്തിലെ രാഹു മത്സരങ്ങളും തടസ്സങ്ങളും മറികടക്കാൻ സഹായിക്കുന്നു."),
    7: ("7-ஆம் வீட்டில் ராகு: கூட்டாண்மைகளை வெளிப்படையாக வைத்துக்கொள்ளுங்கள்.",
        "7-ാം ഭാവത്തിലെ രാഹു: പങ്കാളിത്തങ്ങളിൽ സുതാര്യത പുലർത്തുക."),
    8: ("8-ஆம் வீட்டில் ராகு: ஆபத்தான குறுக்கு வழிகளைத் தவிர்த்து, எதிர்பாராதது நடக்கும்போது "
        "அமைதியாக இருங்கள்.",
        "8-ാം ഭാവത്തിലെ രാഹു: അപകടകരമായ കുറുക്കുവഴികൾ ഒഴിവാക്കുക, അപ്രതീക്ഷിതമായത് "
        "വരുമ്പോൾ ശാന്തരായിരിക്കുക."),
    9: ("9-ஆம் வீட்டில் ராகு நம்பிக்கைகள் அல்லது வழிகாட்டிகள் பற்றிச் சந்தேகங்களை எழுப்பலாம்; "
        "நீங்கள் நம்பும் ஆலோசனையை நாடுங்கள்.",
        "9-ാം ഭാവത്തിലെ രാഹു വിശ്വാസങ്ങളെക്കുറിച്ചോ മാർഗദർശികളെക്കുറിച്ചോ സംശയങ്ങൾ "
        "ഉയർത്തിയേക്കാം; വിശ്വസിക്കാവുന്ന ഉപദേശം തേടുക."),
    10: ("10-ஆம் வீட்டில் ராகு லட்சியத்தையும் வேலையில் திடீர் வாய்ப்புகளையும் தரும்; "
         "நேர்மையுடன் முன்னேறுங்கள்.",
         "10-ാം ഭാവത്തിലെ രാഹു ജോലിയിൽ അഭിലാഷവും പെട്ടെന്നുള്ള അവസരങ്ങളും നൽകുന്നു; "
         "സത്യസന്ധതയോടെ മുന്നോട്ടു പോകുക."),
    11: ("11-ஆம் வீட்டில் ராகு — தொடர்புகள், புதிய அறிமுகங்கள் மூலம் லாபம்.",
         "11-ാം ഭാവത്തിലെ രാഹു — ബന്ധങ്ങളിലൂടെയും പുതിയ പരിചയങ്ങളിലൂടെയും നേട്ടം."),
    12: ("12-ஆம் வீட்டில் ராகு: மறைமுகச் செலவுகளைக் கவனித்து, போதுமான ஓய்வு எடுங்கள்.",
         "12-ാം ഭാവത്തിലെ രാഹു: മറഞ്ഞിരിക്കുന്ന ചെലവുകൾ ശ്രദ്ധിക്കുക, ആവശ്യത്തിന് വിശ്രമിക്കുക."),
}

for _bank, _texts in ((MOON_HOUSE, _MOON_TA_ML), (SATURN_HOUSE, _SATURN_TA_ML),
                      (JUPITER_HOUSE, _JUPITER_TA_ML), (RAHU_HOUSE, _RAHU_TA_ML)):
    for _house, (_ta, _ml) in _texts.items():
        _bank[_house].update(ta=_ta, ml=_ml)

KETU_LINE[True].update(
    ta="உங்கள் ராசிக்கு {n} வீட்டில் கேது அமைதியாக உங்களுக்குச் சாதகமாகச் செயல்படுகிறார் — "
       "தடைகள் பெரிய சிரமமின்றி விலகும்.",
    ml="നിങ്ങളുടെ {n} ഭാവത്തിലെ കേതു നിശ്ശബ്ദമായി നിങ്ങൾക്ക് അനുകൂലമായി പ്രവർത്തിക്കുന്നു — "
       "തടസ്സങ്ങൾ വലിയ ബുദ്ധിമുട്ടില്ലാതെ നീങ്ങും.")
KETU_LINE[False].update(
    ta="உங்கள் ராசிக்கு {n} வீட்டில் கேது அமைதியான, உள்முகமான தாக்கம் — சிந்தனைக்கும் ஆன்மிகப் "
       "பயிற்சிக்கும் நல்லது, அவசர நடவடிக்கைகளுக்கு அவ்வளவு அல்ல.",
    ml="നിങ്ങളുടെ {n} ഭാവത്തിലെ കേതു ശാന്തവും ഉൾമുഖവുമായ സ്വാധീനമാണ് — ആത്മചിന്തനത്തിനും "
       "ആത്മീയസാധനയ്ക്കും നല്ലത്, ആവേശത്തിലുള്ള നീക്കങ്ങൾക്ക് അത്ര നല്ലതല്ല.")
