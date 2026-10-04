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
}

# The rashifal's clock times are printed "6:29 AM" on the Hindi pages too (as
# they always have been); other languages use their own clock words.
CLOCK_LANG = {"hi": "en"}

# -- the phrase bank: see rashifal_pages' docstring for the classical scheme --

TONE_LABEL = {
    "en": {GOOD: "Favourable day", MIXED: "Mixed day", EASY: "Take it easy"},
    "hi": {GOOD: "अनुकूल दिन", MIXED: "मिश्रित दिन", EASY: "संयम का दिन"},
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
