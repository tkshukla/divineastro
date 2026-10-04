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

    "kn": {
        "house.1": "1ನೇ", "house.2": "2ನೇ", "house.3": "3ನೇ", "house.4": "4ನೇ",
        "house.5": "5ನೇ", "house.6": "6ನೇ", "house.7": "7ನೇ", "house.8": "8ನೇ",
        "house.9": "9ನೇ", "house.10": "10ನೇ", "house.11": "11ನೇ", "house.12": "12ನೇ",
        "house_short": "{house} ಮನೆ",
        "rx": " (ವಕ್ರಿ)",
        "planet.Moon": "ಚಂದ್ರ", "planet.Saturn": "ಶನಿ", "planet.Jupiter": "ಗುರು",
        "planet.Rahu": "ರಾಹು", "planet.Ketu": "ಕೇತು",
        "sign_label": "{local}",
        "sign_link": "{local}",
        "sign_crumb": "{local}",
        "sade_name": "{local}",
        "crumb_root": "ರಾಶಿ ಭವಿಷ್ಯ",
        "sub_lang": "kn",
        "s.title": "{local} ರಾಶಿ ಭವಿಷ್ಯ ಇಂದು, {date} — ದಿನ ಭವಿಷ್ಯ | {brand}",
        "s.desc": ("{local} ರಾಶಿಯ ಇಂದಿನ ಭವಿಷ್ಯ ({weekday}, {date}): ಚಂದ್ರ ನಿಮ್ಮ {house} "
                   "ಮನೆಯಲ್ಲಿ — {tone}. ಶನಿ, ಗುರು, ರಾಹು-ಕೇತು ಗೋಚಾರ, ಸಾಡೇಸಾತಿ ಮತ್ತು ಇಂದಿನ "
                   "ತಿಥಿ, ನಿರಯಣ ಗಣನೆಯಿಂದ."),
        "s.h1": "{local} ರಾಶಿ ಭವಿಷ್ಯ ಇಂದು",
        "s.sub": "ಇಂದಿನ ದಿನ ಭವಿಷ್ಯ — ಚಂದ್ರ ಗೋಚಾರದ ಆಧಾರದಲ್ಲಿ",
        "s.summary": "ಚಂದ್ರ ನಿಮ್ಮ ರಾಶಿಯಿಂದ {house} ಮನೆಯಲ್ಲಿದ್ದಾನೆ.",
        "s.about_rashi": "{local} ರಾಶಿ — ಸ್ವಭಾವ, ನಕ್ಷತ್ರಗಳು ಮತ್ತು ಹೆಸರಿನ ಅಕ್ಷರಗಳು",
        "moon.head": "ಇಂದಿನ ಚಂದ್ರ ಸಂಚಾರ (ಚಂದ್ರ ಗೋಚಾರ)",
        "moon.allday": "ಇಂದು ದಿನವಿಡೀ ಚಂದ್ರ {sign} ರಾಶಿಯಲ್ಲಿದ್ದಾನೆ — ನಿಮ್ಮ ರಾಶಿಯಿಂದ {house} ಮನೆ.",
        "moon.until": ("<strong>{time} (IST) ರವರೆಗೆ:</strong> ಚಂದ್ರ {sign} ರಾಶಿಯಲ್ಲಿ — ನಿಮ್ಮ "
                       "ರಾಶಿಯಿಂದ {house} ಮನೆ."),
        "moon.from": ("<strong>{time} (IST) ರಿಂದ:</strong> ಚಂದ್ರ {sign} ರಾಶಿಯನ್ನು ಪ್ರವೇಶಿಸುತ್ತಾನೆ — "
                      "ನಿಮ್ಮ ರಾಶಿಯಿಂದ {house} ಮನೆ."),
        "moon.two": "<p>ಇಂದು ದಿನದ ಮಧ್ಯೆ ಚಂದ್ರ ರಾಶಿ ಬದಲಿಸುತ್ತಾನೆ, ಆದ್ದರಿಂದ ದಿನವನ್ನು ಎರಡು ಭಾಗಗಳಾಗಿ ಓದಿ.</p>",
        "back.head": "ದೀರ್ಘಾವಧಿಯ ಹಿನ್ನೆಲೆ: ನಿಧಾನ ಗ್ರಹಗಳ ಗೋಚಾರ",
        "back.intro": ("<p>ಈ ಗ್ರಹಗಳು ತಿಂಗಳುಗಟ್ಟಲೆ ಅಥವಾ ವರ್ಷಗಟ್ಟಲೆ ಒಂದೇ ರಾಶಿಯಲ್ಲಿರುತ್ತವೆ, ಆದ್ದರಿಂದ "
                       "ಪ್ರತಿದಿನಕ್ಕೆ ಅವು ಹಿನ್ನೆಲೆಯನ್ನು ರೂಪಿಸುತ್ತವೆ.</p>"),
        "back.where": "{sign}{rx} · {house} ಮನೆ",
        "phase.1": "ಮೊದಲ (ಆರಂಭದ)", "phase.2": "ಎರಡನೇ (ಉತ್ತುಂಗದ)", "phase.3": "ಮೂರನೇ (ಕೊನೆಯ)",
        "sade.running": ("<strong>ಸಾಡೇಸಾತಿ ನಡೆಯುತ್ತಿದೆ</strong> — {phase} ಹಂತ. ಇದು ಭಯಪಡಬೇಕಾದ "
                         "ಕಾಲವಲ್ಲ, ನಿಧಾನವಾಗಿ ಶಿಸ್ತು ಕಲಿಸುವ ಅವಧಿ; ನಿಯಮಿತ ದಿನಚರಿ, ಸೇವೆ ಮತ್ತು "
                         "ತಾಳ್ಮೆ ಇದನ್ನು ಹಗುರಗೊಳಿಸುತ್ತವೆ."),
        "sade.dhaiya": ("<strong>ಸಾಡೇಸಾತಿ ಇಲ್ಲ</strong>, ಆದರೆ ಶನಿಯ ಢೈಯಾ (ಅರ್ಧಾಷ್ಟಮ / ಅಷ್ಟಮ ಶನಿ) "
                        "ನಡೆಯುತ್ತಿದೆ (ಮೇಲೆ ನೋಡಿ)."),
        "sade.none": ("<strong>ಸಾಡೇಸಾತಿ ಇಲ್ಲ</strong> — ಶನಿ ನಿಮ್ಮ ರಾಶಿಯಿಂದ 12ನೇ, 1ನೇ ಅಥವಾ 2ನೇ "
                      "ಮನೆಯಲ್ಲಿಲ್ಲ."),
        "panchang": ("<h2>ಇಂದಿನ ಪಂಚಾಂಗ</h2><p>ನವದೆಹಲಿಯಲ್ಲಿ ಸೂರ್ಯೋದಯದ ವೇಳೆಗೆ "
                     "<strong>{paksha_full} {tithi}</strong> ತಿಥಿ, ಚಂದ್ರ "
                     "<strong>{nakshatra}</strong> ನಕ್ಷತ್ರದಲ್ಲಿದ್ದಾನೆ. ರಾಹು ಕಾಲ, ಸೂರ್ಯೋದಯ ಮತ್ತು "
                     'ಸಂಪೂರ್ಣ ಪಂಚಾಂಗವನ್ನು <a href="/panchang">ಇಂದಿನ ಪಂಚಾಂಗ</a> ಪುಟದಲ್ಲಿ ನೋಡಿ.</p>'),
        "personal": ("<p class=\"note\">ಈ ರಾಶಿ ಭವಿಷ್ಯವನ್ನು ನಿಮ್ಮ ಚಂದ್ರ ರಾಶಿಯಿಂದ ಮಾತ್ರ ಓದಲಾಗಿದೆ — ಆ "
                     "ರಾಶಿಯಲ್ಲಿ ಚಂದ್ರನಿರುವಾಗ ಜನಿಸಿದ ಎಲ್ಲರಿಗೂ ಒಂದೇ. ವೈಯಕ್ತಿಕ ಫಲಾದೇಶಕ್ಕೆ ನಿಮ್ಮ "
                     "ಸಂಪೂರ್ಣ ಜನ್ಮ ಜಾತಕ ಬೇಕು: ಲಗ್ನ, ನಡೆಯುತ್ತಿರುವ ದಶೆ ಮತ್ತು ಪ್ರತಿ ಗೋಚಾರದ ಅಷ್ಟಕವರ್ಗ "
                     "ಬಲ. ನಿಮ್ಮ ಚಂದ್ರ ರಾಶಿ ಗೊತ್ತಿಲ್ಲವೇ? ನಿಮ್ಮ ಉಚಿತ ಜಾತಕ ಮೊದಲು ತೋರಿಸುವುದೇ ಅದನ್ನು — "
                     "ಅದು ಸಾಮಾನ್ಯವಾಗಿ ಪಾಶ್ಚಾತ್ಯ ಪದ್ಧತಿಯ ಸೂರ್ಯ ರಾಶಿ ಅಲ್ಲ.</p>"),
        "cta": "ನಿಮ್ಮ ಉಚಿತ ಜಾತಕ ಪಡೆಯಿರಿ — ನಂತರ ನಿಮ್ಮ ಜಾತಕದ ಬಗ್ಗೆ ಪ್ರಶ್ನೆ ಕೇಳಿ",
        "signs.head": "ಎಲ್ಲಾ ರಾಶಿಗಳ ಇಂದಿನ ಭವಿಷ್ಯ",
        "more.head": "ಇನ್ನಷ್ಟು ಉಚಿತ ಸೇವೆಗಳು",
        "method": ("<h2>ಇದನ್ನು ಹೇಗೆ ಲೆಕ್ಕ ಹಾಕಲಾಗಿದೆ</h2><p>ಗ್ರಹಗಳ ಸ್ಥಾನಗಳನ್ನು ಇಂದಿಗೆ (IST) ಸ್ವಿಸ್ "
                   "ಎಫೆಮೆರಿಸ್ ಬಳಸಿ ನಿರಯಣ ರಾಶಿಚಕ್ರದಲ್ಲಿ (ಲಾಹಿರಿ ಅಯನಾಂಶ) ಲೆಕ್ಕ ಹಾಕಲಾಗಿದೆ — ನಮ್ಮ "
                   "ಜಾತಕ ಮತ್ತು ಪಂಚಾಂಗ ಬಳಸುವ ಅದೇ ಸ್ಥಾನಗಳು. ಶಾಸ್ತ್ರೀಯ ಗೋಚಾರದಂತೆ ಮನೆಗಳನ್ನು ನಿಮ್ಮ "
                   "ಚಂದ್ರ ರಾಶಿಯಿಂದ ಎಣಿಸಲಾಗಿದೆ. ಯಾವ ಮನೆಗಳು ಶುಭ ಎಂಬುದು ವರಾಹಮಿಹಿರನ ಬೃಹತ್ಸಂಹಿತೆ "
                   "(ಅಧ್ಯಾಯ 104) ಮತ್ತು ಮಂತ್ರೇಶ್ವರನ ಫಲದೀಪಿಕೆ (ಅಧ್ಯಾಯ 26) ಪದ್ಧತಿಯನ್ನು ಅನುಸರಿಸುತ್ತದೆ: "
                   "ಚಂದ್ರ 1, 3, 6, 7, 10 ಮತ್ತು 11ನೇ ಮನೆಗಳಲ್ಲಿ ಶುಭ; ಶನಿ, ರಾಹು ಮತ್ತು ಕೇತು 3, 6 ಮತ್ತು "
                   "11ನೇ ಮನೆಗಳಲ್ಲಿ; ಗುರು 2, 5, 7, 9 ಮತ್ತು 11ನೇ ಮನೆಗಳಲ್ಲಿ.</p>"),
        "i.title": "ಇಂದಿನ ರಾಶಿ ಭವಿಷ್ಯ, {date} — ಎಲ್ಲಾ 12 ರಾಶಿಗಳ ದಿನ ಭವಿಷ್ಯ | {brand}",
        "i.desc": ("ಇಂದಿನ ರಾಶಿ ಭವಿಷ್ಯ ({weekday}, {date}): ಮೇಷದಿಂದ ಮೀನದವರೆಗೆ ಎಲ್ಲಾ 12 ಚಂದ್ರ "
                   "ರಾಶಿಗಳ ದಿನ ಭವಿಷ್ಯ — ಚಂದ್ರ ಗೋಚಾರ, ಶನಿ, ಗುರು, ರಾಹು ಮತ್ತು ಸಾಡೇಸಾತಿ, ನಿರಯಣ "
                   "ಗಣನೆಯ ಆಧಾರದಲ್ಲಿ."),
        "i.h1": "ಇಂದಿನ ರಾಶಿ ಭವಿಷ್ಯ",
        "i.sub": "ದಿನ ಭವಿಷ್ಯ — ಎಲ್ಲಾ 12 ರಾಶಿಗಳು",
        "i.intro": ("<p>ರಾಶಿ ಭವಿಷ್ಯವನ್ನು ನಿಮ್ಮ <strong>ಚಂದ್ರ ರಾಶಿ</strong>ಯಿಂದ ಓದಲಾಗುತ್ತದೆ. "
                    "{moon_text} ಶನಿ {sat_sign} ರಾಶಿಯಲ್ಲಿದ್ದಾನೆ, ಆದ್ದರಿಂದ {sade_names} ರಾಶಿಯವರಿಗೆ "
                    "ಸಾಡೇಸಾತಿ ನಡೆಯುತ್ತಿದೆ.</p>"),
        "i.moon_two": ("ಚಂದ್ರ {time} (IST) ರವರೆಗೆ {now} ರಾಶಿಯಲ್ಲಿ, ನಂತರ {next} ರಾಶಿಯಲ್ಲಿ. ಕೋಷ್ಟಕವು "
                       "ದಿನದ ಹೆಚ್ಚಿನ ಭಾಗದ ಸ್ಥಾನವನ್ನು ತೋರಿಸುತ್ತದೆ."),
        "i.moon_one": "ಇಂದು ದಿನವಿಡೀ ಚಂದ್ರ {now} ರಾಶಿಯಲ್ಲಿದ್ದಾನೆ.",
        "i.name": "{local}",
        "i.sade": "<small>ಸಾಡೇಸಾತಿ</small>",
        "i.head_row": "<tr><th>ರಾಶಿ</th><th>ಚಂದ್ರ ಇರುವ ಮನೆ</th><th>ಇಂದು</th></tr>",
        "nf.title": "ರಾಶಿ ಸಿಗಲಿಲ್ಲ",
        "nf.body": ("<h1>ರಾಶಿ ಸಿಗಲಿಲ್ಲ</h1><p>“{slug}” ಎಂಬ ಹೆಸರಿನ ಯಾವುದೇ ರಾಶಿ ಇಲ್ಲ. ಕೆಳಗೆ ನಿಮ್ಮ "
                    "ಚಂದ್ರ ರಾಶಿಯನ್ನು ಆರಿಸಿ.</p>"),
    },

    "te": {
        "house.1": "1వ", "house.2": "2వ", "house.3": "3వ", "house.4": "4వ",
        "house.5": "5వ", "house.6": "6వ", "house.7": "7వ", "house.8": "8వ",
        "house.9": "9వ", "house.10": "10వ", "house.11": "11వ", "house.12": "12వ",
        "house_short": "{house} స్థానం",
        "rx": " (వక్రం)",
        "planet.Moon": "చంద్రుడు", "planet.Saturn": "శని", "planet.Jupiter": "గురువు",
        "planet.Rahu": "రాహువు", "planet.Ketu": "కేతువు",
        "sign_label": "{local}",
        "sign_link": "{local}",
        "sign_crumb": "{local}",
        "sade_name": "{local}",
        "crumb_root": "రాశి ఫలాలు",
        "sub_lang": "te",
        "s.title": "{local} రాశి ఫలాలు ఈరోజు, {date} — దిన ఫలాలు | {brand}",
        "s.desc": ("{local} రాశి ఫలాలు ఈరోజు ({weekday}, {date}): చంద్రుడు మీ {house} "
                   "స్థానంలో — {tone}. శని, గురువు, రాహు-కేతు గోచారం, ఏలినాటి శని, నేటి తిథి, "
                   "నిరయన గణనతో."),
        "s.h1": "{local} రాశి ఫలాలు ఈరోజు",
        "s.sub": "నేటి దిన ఫలాలు — చంద్ర గోచారం ఆధారంగా",
        "s.summary": "చంద్రుడు మీ రాశి నుండి {house} స్థానంలో ఉన్నాడు.",
        "s.about_rashi": "{local} రాశి — స్వభావం, నక్షత్రాలు, పేరు అక్షరాలు",
        "moon.head": "నేటి చంద్ర సంచారం (చంద్ర గోచారం)",
        "moon.allday": "ఈరోజు రోజంతా చంద్రుడు {sign}లో ఉన్నాడు — మీ రాశి నుండి {house} స్థానం.",
        "moon.until": ("<strong>{time} (IST) వరకు:</strong> చంద్రుడు {sign}లో — మీ రాశి నుండి "
                       "{house} స్థానం."),
        "moon.from": ("<strong>{time} (IST) నుండి:</strong> చంద్రుడు {sign}లోకి ప్రవేశిస్తాడు — మీ "
                      "రాశి నుండి {house} స్థానం."),
        "moon.two": "<p>ఈరోజు పగటిపూట చంద్రుడు రాశి మారుతాడు, అందువల్ల రోజును రెండు భాగాలుగా చదవండి.</p>",
        "back.head": "దీర్ఘకాలిక నేపథ్యం: నెమ్మదిగా కదిలే గ్రహాల గోచారం",
        "back.intro": ("<p>ఈ గ్రహాలు నెలలు లేదా సంవత్సరాల పాటు ఒకే రాశిలో ఉంటాయి, అందువల్ల ప్రతి "
                       "రోజుకు అవి నేపథ్యాన్ని ఏర్పరుస్తాయి.</p>"),
        "back.where": "{sign}{rx} · {house} స్థానం",
        "phase.1": "మొదటి (ప్రారంభ)", "phase.2": "రెండవ (ప్రధాన)", "phase.3": "మూడవ (ముగింపు)",
        "sade.running": ("<strong>ఏలినాటి శని నడుస్తోంది</strong> — {phase} దశ. ఇది భయపడాల్సిన "
                         "కాలం కాదు, నెమ్మదిగా క్రమశిక్షణ నేర్పే కాలం; స్థిరమైన దినచర్య, సేవ, ఓర్పు "
                         "దీనిని తేలిక చేస్తాయి."),
        "sade.dhaiya": ("<strong>ఏలినాటి శని లేదు</strong>, కానీ శని ఢైయా (అర్ధాష్టమ / అష్టమ శని) "
                        "నడుస్తోంది (పైన చూడండి)."),
        "sade.none": ("<strong>ఏలినాటి శని లేదు</strong> — శని మీ రాశి నుండి 12వ, 1వ లేదా 2వ "
                      "స్థానంలో లేడు."),
        "panchang": ("<h2>ఈరోజు పంచాంగం</h2><p>న్యూఢిల్లీలో సూర్యోదయ సమయానికి "
                     "<strong>{paksha_full} {tithi}</strong> తిథి, చంద్రుడు "
                     "<strong>{nakshatra}</strong> నక్షత్రంలో ఉన్నాడు. రాహుకాలం, సూర్యోదయం, పూర్తి "
                     'పంచాంగం <a href="/panchang">ఈరోజు పంచాంగం</a> పేజీలో చూడండి.</p>'),
        "personal": ("<p class=\"note\">ఈ రాశి ఫలాలు మీ చంద్ర రాశి ఆధారంగా మాత్రమే — ఆ రాశిలో "
                     "చంద్రుడు ఉండగా పుట్టిన అందరికీ ఒకటే. వ్యక్తిగత ఫలితాలకు మీ పూర్తి జన్మ జాతకం "
                     "కావాలి: లగ్నం, నడుస్తున్న దశ, ప్రతి గోచారం యొక్క అష్టకవర్గు బలం. మీ చంద్ర రాశి "
                     "తెలియదా? మీ ఉచిత జాతకం మొదట చూపించేది అదే — ఇది సాధారణంగా పాశ్చాత్య పద్ధతిలోని "
                     "సూర్య రాశి కాదు.</p>"),
        "cta": "మీ ఉచిత జాతకం పొందండి — తర్వాత మీ జాతకం గురించి ప్రశ్న అడగండి",
        "signs.head": "అన్ని రాశుల నేటి ఫలాలు",
        "more.head": "మరిన్ని ఉచిత సేవలు",
        "method": ("<h2>ఇది ఎలా లెక్కించబడింది</h2><p>గ్రహాల స్థానాలను ఈరోజుకు (IST) స్విస్ "
                   "ఎఫెమెరిస్‌తో నిరయన రాశిచక్రంలో (లాహిరి అయనాంశ) లెక్కించాము — మా జాతకం, "
                   "పంచాంగం ఉపయోగించే అవే స్థానాలు. శాస్త్రీయ గోచారంలో లాగా స్థానాలను మీ చంద్ర రాశి "
                   "నుండి లెక్కిస్తాము. ఏ స్థానాలు శుభప్రదం అన్నది వరాహమిహిరుని బృహత్సంహిత "
                   "(అధ్యాయం 104), మంత్రేశ్వరుని ఫలదీపిక (అధ్యాయం 26) పద్ధతిని అనుసరిస్తుంది: "
                   "చంద్రుడు 1, 3, 6, 7, 10, 11వ స్థానాల్లో శుభం; శని, రాహువు, కేతువు 3, 6, 11వ "
                   "స్థానాల్లో; గురువు 2, 5, 7, 9, 11వ స్థానాల్లో.</p>"),
        "i.title": "రాశి ఫలాలు ఈరోజు, {date} — 12 రాశుల దిన ఫలాలు | {brand}",
        "i.desc": ("రాశి ఫలాలు ఈరోజు ({weekday}, {date}): మేషం నుండి మీనం వరకు అన్ని 12 చంద్ర "
                   "రాశుల దిన ఫలాలు — చంద్ర గోచారం, శని, గురువు, రాహువు, ఏలినాటి శని, నిరయన గణన "
                   "ఆధారంగా."),
        "i.h1": "రాశి ఫలాలు ఈరోజు",
        "i.sub": "నేటి దిన ఫలాలు — అన్ని 12 రాశులు",
        "i.intro": ("<p>రాశి ఫలాలను మీ <strong>చంద్ర రాశి</strong> నుండి చూస్తారు. {moon_text} శని "
                    "{sat_sign}లో ఉన్నాడు, అందువల్ల {sade_names} రాశుల వారికి ఏలినాటి శని "
                    "నడుస్తోంది.</p>"),
        "i.moon_two": ("చంద్రుడు {time} (IST) వరకు {now}లో, తర్వాత {next}లో ఉంటాడు. పట్టిక రోజులో "
                       "ఎక్కువ భాగం ఉండే స్థానాన్ని చూపుతుంది."),
        "i.moon_one": "ఈరోజు రోజంతా చంద్రుడు {now}లో ఉన్నాడు.",
        "i.name": "{local}",
        "i.sade": "<small>ఏలినాటి శని</small>",
        "i.head_row": "<tr><th>రాశి</th><th>చంద్రుడు ఉన్న స్థానం</th><th>ఈరోజు</th></tr>",
        "nf.title": "రాశి కనబడలేదు",
        "nf.body": ("<h1>రాశి కనబడలేదు</h1><p>“{slug}” అనే పేరుతో ఏ రాశీ లేదు. క్రింద మీ చంద్ర "
                    "రాశిని ఎంచుకోండి.</p>"),
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

    # Bengali (DIVASTRO-123). Sign names come in Bengali script ({local}); the
    # Latin {name}/{english} are left out so the body stays in Bengali.
    "bn": {
        "house.1": "প্রথম", "house.2": "দ্বিতীয়", "house.3": "তৃতীয়", "house.4": "চতুর্থ",
        "house.5": "পঞ্চম", "house.6": "ষষ্ঠ", "house.7": "সপ্তম", "house.8": "অষ্টম",
        "house.9": "নবম", "house.10": "দশম", "house.11": "একাদশ", "house.12": "দ্বাদশ",
        "house_short": "{house} ভাব",
        "rx": " (বক্রী)",
        "planet.Moon": "চন্দ্র", "planet.Saturn": "শনি", "planet.Jupiter": "বৃহস্পতি",
        "planet.Rahu": "রাহু", "planet.Ketu": "কেতু",
        "sign_label": "{local}",
        "sign_link": "{local}",
        "sign_crumb": "{local}",
        "sade_name": "{local}",
        "crumb_root": "আজকের রাশিফল",
        "sub_lang": "bn",
        "s.title": "{local} রাশিফল আজ, {date_short} — আজকের রাশিফল | {brand}",
        "s.desc": ("{local} রাশির আজকের রাশিফল ({weekday}, {date}): চন্দ্র আপনার রাশি থেকে "
                   "{house} ভাবে — {tone}। সঙ্গে শনি, বৃহস্পতি ও রাহু-কেতুর গোচর, সাড়েসাতির "
                   "অবস্থা ও আজকের তিথি, নিরয়ণ গণনায়।"),
        "s.h1": "{local} রাশির আজকের রাশিফল",
        "s.sub": "{local} রাশি · দৈনিক রাশিফল",
        "s.summary": "চন্দ্র আপনার রাশি থেকে {house} ভাবে।",
        "s.about_rashi": "{local} রাশি — স্বভাব, নক্ষত্র ও নামের আদ্যক্ষর",
        "moon.head": "আজকের চন্দ্র গোচর",
        "moon.allday": "আজ সারাদিন চন্দ্র {sign} রাশিতে — আপনার রাশি থেকে {house} ভাবে।",
        "moon.until": ("<strong>{time} পর্যন্ত:</strong> চন্দ্র {sign} রাশিতে — আপনার রাশি থেকে "
                       "{house} ভাবে।"),
        "moon.from": ("<strong>{time} থেকে:</strong> চন্দ্র {sign} রাশিতে প্রবেশ করছে — আপনার "
                      "রাশি থেকে {house} ভাবে।"),
        "moon.two": "<p>আজ দিনের মধ্যেই চন্দ্র রাশি বদলাচ্ছে, তাই দিনটিকে দুই ভাগে পড়ুন।</p>",
        "back.head": "দীর্ঘ সময়ের পটভূমি: ধীর গ্রহের গোচর",
        "back.intro": ("<p>এই গ্রহগুলি মাসের পর মাস বা বছরের পর বছর একই রাশিতে থাকে, তাই "
                       "প্রতিদিনের ঘটনার পটভূমি এরাই তৈরি করে।</p>"),
        "back.where": "{sign}{rx} · {house} ভাব",
        "phase.1": "প্রথম (আরম্ভ)", "phase.2": "দ্বিতীয় (চরম)", "phase.3": "তৃতীয় (শেষ)",
        "sade.running": ("<strong>সাড়েসাতি চলছে</strong> — {phase} পর্যায়। এটি ভয়ের কিছু নয়, "
                         "বরং ধীরে ধীরে শৃঙ্খলা শেখানোর সময়; নিয়মিত দিনচর্যা, সেবা ও ধৈর্য "
                         "একে হালকা করে।"),
        "sade.dhaiya": ("<strong>সাড়েসাতি নেই</strong>, তবে শনির আড়াই বছরের প্রভাব (ঢাইয়া) "
                        "চলছে (উপরে দেখুন)।"),
        "sade.none": ("<strong>সাড়েসাতি নেই</strong> — শনি আপনার রাশি থেকে দ্বাদশ, প্রথম বা "
                      "দ্বিতীয় ভাবে নেই।"),
        "panchang": ("<h2>আজকের পঞ্জিকা</h2><p>নয়াদিল্লিতে সূর্যোদয়ের সময় "
                     "<strong>{paksha} {tithi}</strong> তিথি, চন্দ্র <strong>{nakshatra}</strong> "
                     "নক্ষত্রে। রাহুকাল, সূর্যোদয় ও পূর্ণ পঞ্জিকা দেখুন "
                     '<a href="/panchang">আজকের পঞ্জিকায়</a>।</p>'),
        "personal": ("<p class=\"note\">এই রাশিফল শুধু আপনার চন্দ্র রাশি থেকে পড়া — ওই রাশিতে "
                     "চন্দ্র নিয়ে জন্মানো সবার জন্য একই। ব্যক্তিগত ফল দেখা হয় আপনার পূর্ণ "
                     "জন্মকোষ্ঠী থেকে: লগ্ন, চলতি দশা এবং প্রতিটি গোচরের অষ্টকবর্গ বল। নিজের "
                     "চন্দ্র রাশি জানেন না? বিনামূল্যে কোষ্ঠীতে সবার আগে সেটিই দেখা যায় — "
                     "সাধারণত এটি পাশ্চাত্য মতের সূর্য রাশি নয়।</p>"),
        "cta": "বিনামূল্যে কোষ্ঠী তৈরি করুন — তারপর নিজের কোষ্ঠী নিয়ে প্রশ্ন করুন",
        "signs.head": "সব রাশির আজকের রাশিফল",
        "more.head": "আরও বিনামূল্যের সুবিধা",
        "method": ("<h2>কীভাবে গণনা করা হয়</h2><p>আজকের (ভারতীয় সময়) গ্রহের অবস্থান সুইস "
                   "এফিমেরিস দিয়ে নিরয়ণ রাশিচক্রে (লাহিড়ী অয়নাংশ) গণনা করা হয়েছে — আমাদের "
                   "কোষ্ঠী ও পঞ্জিকায় সেই একই অবস্থান ব্যবহার হয়। শাস্ত্রীয় গোচরের নিয়মে ভাব "
                   "গোনা হয়েছে আপনার চন্দ্র রাশি থেকে। কোন ভাব শুভ, তা বরাহমিহিরের বৃহৎসংহিতা "
                   "(অধ্যায় 104) ও মন্ত্রেশ্বরের ফলদীপিকা (অধ্যায় 26) অনুসারে: চন্দ্র 1, 3, 6, 7, "
                   "10 ও 11 নং ভাবে শুভ; শনি, রাহু ও কেতু 3, 6 ও 11 নং ভাবে; বৃহস্পতি 2, 5, 7, 9 "
                   "ও 11 নং ভাবে।</p>"),
        "i.title": "আজকের রাশিফল, {date_short} — 12টি রাশির দৈনিক রাশিফল | {brand}",
        "i.desc": ("আজকের রাশিফল ({weekday}, {date}): মেষ থেকে মীন — 12টি চন্দ্র রাশির দৈনিক "
                   "রাশিফল, চন্দ্র গোচর, শনি, বৃহস্পতি ও রাহুর প্রভাব এবং সাড়েসাতি, নিরয়ণ "
                   "গণনায়।"),
        "i.h1": "আজকের রাশিফল",
        "i.sub": "সব 12টি রাশির দৈনিক রাশিফল",
        "i.intro": ("<p>রাশিফল পড়া হয় আপনার <strong>চন্দ্র রাশি</strong> থেকে। {moon_text} শনি "
                    "এখন {sat_sign} রাশিতে, তাই {sade_names} রাশির সাড়েসাতি চলছে।</p>"),
        "i.moon_two": ("{time} পর্যন্ত চন্দ্র {now} রাশিতে, তারপর {next} রাশিতে। তালিকায় দিনের "
                       "বেশির ভাগ সময়ের অবস্থান দেখানো হয়েছে।"),
        "i.moon_one": "আজ সারাদিন চন্দ্র {now} রাশিতে।",
        "i.name": "{local}",
        "i.sade": "<small>সাড়েসাতি</small>",
        "i.head_row": "<tr><th>রাশি</th><th>চন্দ্রের ভাব</th><th>আজ</th></tr>",
        "nf.title": "রাশি পাওয়া যায়নি",
        "nf.body": ("<h1>রাশি পাওয়া যায়নি</h1><p>“{slug}” নামে কোনো রাশি নেই। নীচে আপনার "
                    "চন্দ্র রাশি বেছে নিন।</p>"),
    },

    # Odia (DIVASTRO-123).
    "or": {
        "house.1": "ପ୍ରଥମ", "house.2": "ଦ୍ୱିତୀୟ", "house.3": "ତୃତୀୟ", "house.4": "ଚତୁର୍ଥ",
        "house.5": "ପଞ୍ଚମ", "house.6": "ଷଷ୍ଠ", "house.7": "ସପ୍ତମ", "house.8": "ଅଷ୍ଟମ",
        "house.9": "ନବମ", "house.10": "ଦଶମ", "house.11": "ଏକାଦଶ", "house.12": "ଦ୍ୱାଦଶ",
        "house_short": "{house} ଭାବ",
        "rx": " (ବକ୍ରୀ)",
        "planet.Moon": "ଚନ୍ଦ୍ର", "planet.Saturn": "ଶନି", "planet.Jupiter": "ବୃହସ୍ପତି",
        "planet.Rahu": "ରାହୁ", "planet.Ketu": "କେତୁ",
        "sign_label": "{local}",
        "sign_link": "{local}",
        "sign_crumb": "{local}",
        "sade_name": "{local}",
        "crumb_root": "ଆଜିର ରାଶିଫଳ",
        "sub_lang": "or",
        "s.title": "{local} ରାଶିଫଳ ଆଜି, {date_short} — ଆଜିର ରାଶିଫଳ | {brand}",
        "s.desc": ("{local} ରାଶିର ଆଜିର ରାଶିଫଳ ({weekday}, {date}): ଚନ୍ଦ୍ର ଆପଣଙ୍କ ରାଶିରୁ {house} "
                   "ଭାବରେ — {tone}। ସହିତ ଶନି, ବୃହସ୍ପତି ଓ ରାହୁ-କେତୁଙ୍କ ଗୋଚର, ସାଢ଼େସାତି ସ୍ଥିତି ଓ "
                   "ଆଜିର ତିଥି, ନିରୟନ ଗଣନାରେ।"),
        "s.h1": "{local} ରାଶିର ଆଜିର ରାଶିଫଳ",
        "s.sub": "{local} ରାଶି · ଦୈନିକ ରାଶିଫଳ",
        "s.summary": "ଚନ୍ଦ୍ର ଆପଣଙ୍କ ରାଶିରୁ {house} ଭାବରେ।",
        "s.about_rashi": "{local} ରାଶି — ସ୍ୱଭାବ, ନକ୍ଷତ୍ର ଓ ନାମର ଆଦ୍ୟାକ୍ଷର",
        "moon.head": "ଆଜିର ଚନ୍ଦ୍ର ଗୋଚର",
        "moon.allday": "ଆଜି ଦିନସାରା ଚନ୍ଦ୍ର {sign} ରାଶିରେ — ଆପଣଙ୍କ ରାଶିରୁ {house} ଭାବରେ।",
        "moon.until": ("<strong>{time} ପର୍ଯ୍ୟନ୍ତ:</strong> ଚନ୍ଦ୍ର {sign} ରାଶିରେ — ଆପଣଙ୍କ ରାଶିରୁ "
                       "{house} ଭାବରେ।"),
        "moon.from": ("<strong>{time} ଠାରୁ:</strong> ଚନ୍ଦ୍ର {sign} ରାଶିରେ ପ୍ରବେଶ କରନ୍ତି — ଆପଣଙ୍କ "
                      "ରାଶିରୁ {house} ଭାବରେ।"),
        "moon.two": "<p>ଆଜି ଦିନ ମଧ୍ୟରେ ଚନ୍ଦ୍ର ରାଶି ବଦଳାନ୍ତି, ତେଣୁ ଦିନଟିକୁ ଦୁଇ ଭାଗରେ ପଢ଼ନ୍ତୁ।</p>",
        "back.head": "ଦୀର୍ଘ ସମୟର ପୃଷ୍ଠଭୂମି: ମନ୍ଥର ଗ୍ରହଙ୍କ ଗୋଚର",
        "back.intro": ("<p>ଏହି ଗ୍ରହମାନେ ମାସ ମାସ ବା ବର୍ଷ ବର୍ଷ ଧରି ଗୋଟିଏ ରାଶିରେ ରହନ୍ତି, ତେଣୁ "
                       "ପ୍ରତିଦିନର ଘଟଣାର ପୃଷ୍ଠଭୂମି ଏମାନେ ହିଁ ଗଢ଼ନ୍ତି।</p>"),
        "back.where": "{sign}{rx} · {house} ଭାବ",
        "phase.1": "ପ୍ରଥମ (ଆରମ୍ଭ)", "phase.2": "ଦ୍ୱିତୀୟ (ଶିଖର)", "phase.3": "ତୃତୀୟ (ଶେଷ)",
        "sade.running": ("<strong>ସାଢ଼େସାତି ଚାଲିଛି</strong> — {phase} ପର୍ଯ୍ୟାୟ। ଏହା ଭୟ କରିବାର "
                         "ବିଷୟ ନୁହେଁ, ବରଂ ଧୀରେ ଧୀରେ ଅନୁଶାସନ ଶିଖାଇବାର ସମୟ; ନିୟମିତ ଦିନଚର୍ଯ୍ୟା, "
                         "ସେବା ଓ ଧୈର୍ଯ୍ୟ ଏହାକୁ ହାଲୁକା କରେ।"),
        "sade.dhaiya": ("<strong>ସାଢ଼େସାତି ନାହିଁ</strong>, କିନ୍ତୁ ଶନିଙ୍କ ଅଢ଼େଇ ବର୍ଷର ପ୍ରଭାବ "
                        "(ଢାଇୟା) ଚାଲିଛି (ଉପରେ ଦେଖନ୍ତୁ)।"),
        "sade.none": ("<strong>ସାଢ଼େସାତି ନାହିଁ</strong> — ଶନି ଆପଣଙ୍କ ରାଶିରୁ ଦ୍ୱାଦଶ, ପ୍ରଥମ ବା "
                      "ଦ୍ୱିତୀୟ ଭାବରେ ନାହାନ୍ତି।"),
        "panchang": ("<h2>ଆଜିର ପାଞ୍ଜି</h2><p>ନୂଆଦିଲ୍ଲୀରେ ସୂର୍ଯ୍ୟୋଦୟ ସମୟରେ "
                     "<strong>{paksha} {tithi}</strong> ତିଥି, ଚନ୍ଦ୍ର <strong>{nakshatra}</strong> "
                     "ନକ୍ଷତ୍ରରେ। ରାହୁ କାଳ, ସୂର୍ଯ୍ୟୋଦୟ ଓ ସମ୍ପୂର୍ଣ୍ଣ ପାଞ୍ଜି "
                     '<a href="/panchang">ଆଜିର ପାଞ୍ଜି</a>ରେ ଦେଖନ୍ତୁ।</p>'),
        "personal": ("<p class=\"note\">ଏହି ରାଶିଫଳ କେବଳ ଆପଣଙ୍କ ଚନ୍ଦ୍ର ରାଶିରୁ ପଢ଼ାଯାଇଛି — ସେହି "
                     "ରାଶିରେ ଚନ୍ଦ୍ର ଥାଇ ଜନ୍ମ ହୋଇଥିବା ସମସ୍ତଙ୍କ ପାଇଁ ସମାନ। ବ୍ୟକ୍ତିଗତ ଫଳ ଆପଣଙ୍କ "
                     "ସମ୍ପୂର୍ଣ୍ଣ ଜନ୍ମ କୁଣ୍ଡଳୀରୁ ଦେଖାଯାଏ: ଲଗ୍ନ, ଚାଲୁଥିବା ଦଶା ଓ ପ୍ରତ୍ୟେକ ଗୋଚରର "
                     "ଅଷ୍ଟକବର୍ଗ ବଳ। ନିଜ ଚନ୍ଦ୍ର ରାଶି ଜାଣନ୍ତି ନାହିଁ? ମାଗଣା କୁଣ୍ଡଳୀରେ ଏହା "
                     "ସବୁଠାରୁ ଆଗରେ ଦେଖାଯାଏ — ସାଧାରଣତଃ ଏହା ପାଶ୍ଚାତ୍ୟ ମତର ସୂର୍ଯ୍ୟ ରାଶି ନୁହେଁ।</p>"),
        "cta": "ମାଗଣା କୁଣ୍ଡଳୀ ପାଆନ୍ତୁ — ତାପରେ ନିଜ କୁଣ୍ଡଳୀ ବିଷୟରେ ପ୍ରଶ୍ନ ପଚାରନ୍ତୁ",
        "signs.head": "ସମସ୍ତ ରାଶିର ଆଜିର ରାଶିଫଳ",
        "more.head": "ଆହୁରି ମାଗଣା ସେବା",
        "method": ("<h2>ଏହା କିପରି ଗଣନା କରାଯାଏ</h2><p>ଆଜିର (ଭାରତୀୟ ସମୟ) ଗ୍ରହ ସ୍ଥିତି ସ୍ୱିସ୍ "
                   "ଏଫିମେରିସ୍ ଦ୍ୱାରା ନିରୟନ ରାଶିଚକ୍ରରେ (ଲାହିଡ଼ୀ ଅୟନାଂଶ) ଗଣନା କରାଯାଇଛି — ଆମ "
                   "କୁଣ୍ଡଳୀ ଓ ପାଞ୍ଜିରେ ସେହି ସମାନ ସ୍ଥିତି ବ୍ୟବହୃତ ହୁଏ। ଶାସ୍ତ୍ରୀୟ ଗୋଚର ନିୟମରେ ଭାବ "
                   "ଆପଣଙ୍କ ଚନ୍ଦ୍ର ରାଶିରୁ ଗଣାଯାଇଛି। କେଉଁ ଭାବ ଶୁଭ, ତାହା ବରାହମିହିରଙ୍କ ବୃହତ୍ "
                   "ସଂହିତା (ଅଧ୍ୟାୟ 104) ଓ ମନ୍ତ୍ରେଶ୍ୱରଙ୍କ ଫଳଦୀପିକା (ଅଧ୍ୟାୟ 26) ଅନୁସାରେ: ଚନ୍ଦ୍ର "
                   "1, 3, 6, 7, 10 ଓ 11 ଭାବରେ ଶୁଭ; ଶନି, ରାହୁ ଓ କେତୁ 3, 6 ଓ 11 ଭାବରେ; "
                   "ବୃହସ୍ପତି 2, 5, 7, 9 ଓ 11 ଭାବରେ।</p>"),
        "i.title": "ଆଜିର ରାଶିଫଳ, {date_short} — 12 ରାଶିର ଦୈନିକ ରାଶିଫଳ | {brand}",
        "i.desc": ("ଆଜିର ରାଶିଫଳ ({weekday}, {date}): ମେଷ ଠାରୁ ମୀନ ପର୍ଯ୍ୟନ୍ତ 12 ଚନ୍ଦ୍ର ରାଶିର "
                   "ଦୈନିକ ରାଶିଫଳ — ଚନ୍ଦ୍ର ଗୋଚର, ଶନି, ବୃହସ୍ପତି ଓ ରାହୁଙ୍କ ପ୍ରଭାବ ଏବଂ ସାଢ଼େସାତି, "
                   "ନିରୟନ ଗଣନାରେ।"),
        "i.h1": "ଆଜିର ରାଶିଫଳ",
        "i.sub": "ସମସ୍ତ 12 ରାଶିର ଦୈନିକ ରାଶିଫଳ",
        "i.intro": ("<p>ରାଶିଫଳ ଆପଣଙ୍କ <strong>ଚନ୍ଦ୍ର ରାଶି</strong>ରୁ ପଢ଼ାଯାଏ। {moon_text} ଶନି ଏବେ "
                    "{sat_sign} ରାଶିରେ ଅଛନ୍ତି, ତେଣୁ {sade_names} ରାଶିର ସାଢ଼େସାତି ଚାଲିଛି।</p>"),
        "i.moon_two": ("{time} ପର୍ଯ୍ୟନ୍ତ ଚନ୍ଦ୍ର {now} ରାଶିରେ, ତାପରେ {next} ରାଶିରେ। ସାରଣୀରେ ଦିନର "
                       "ଅଧିକାଂଶ ସମୟର ସ୍ଥିତି ଦିଆଯାଇଛି।"),
        "i.moon_one": "ଆଜି ଦିନସାରା ଚନ୍ଦ୍ର {now} ରାଶିରେ।",
        "i.name": "{local}",
        "i.sade": "<small>ସାଢ଼େସାତି</small>",
        "i.head_row": "<tr><th>ରାଶି</th><th>ଚନ୍ଦ୍ରଙ୍କ ଭାବ</th><th>ଆଜି</th></tr>",
        "nf.title": "ରାଶି ମିଳିଲା ନାହିଁ",
        "nf.body": ("<h1>ରାଶି ମିଳିଲା ନାହିଁ</h1><p>“{slug}” ନାମରେ କୌଣସି ରାଶି ନାହିଁ। ତଳୁ ଆପଣଙ୍କ "
                    "ଚନ୍ଦ୍ର ରାଶି ବାଛନ୍ତୁ।</p>"),
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
    # kn/te hrefs are the English paths: i18n.localize_links adds the /kn/, /te/ prefix
    "kn": (("{twin:en}", "ಇಂಗ್ಲಿಷ್‌ನಲ್ಲಿ ಓದಿ"), ("/panchang", "ಇಂದಿನ ಪಂಚಾಂಗ"),
           ("/rahu-kaal", "ರಾಹು ಕಾಲ ಇಂದು"), ("/choghadiya", "ಇಂದಿನ ಚೌಘಡಿಯಾ"),
           ("/kundali-milan", "ಜಾತಕ ಹೊಂದಾಣಿಕೆ"), ("/vrat-tyohar", "ಇಂದಿನ ವ್ರತ ಮತ್ತು ಹಬ್ಬಗಳು")),
    "te": (("{twin:en}", "ఇంగ్లీష్‌లో చదవండి"), ("/panchang", "ఈరోజు పంచాంగం"),
           ("/rahu-kaal", "నేటి రాహుకాలం"), ("/choghadiya", "నేటి చౌఘడియా"),
           ("/kundali-milan", "జాతక పొంతన"), ("/vrat-tyohar", "నేటి పండుగలు, వ్రతాలు")),
    "ta": (("{twin:en}", "ஆங்கிலத்தில் படிக்க"), ("/panchang", "இன்றைய பஞ்சாங்கம்"), ("/rahu-kaal", "இன்று ராகு காலம்"),
           ("/choghadiya", "இன்றைய சௌகடியா முகூர்த்தம்"), ("/kundali-milan", "ஜாதகப் பொருத்தம்"),
           ("/vrat-tyohar", "இன்றைய விரதங்கள், பண்டிகைகள்")),
    "ml": (("{twin:en}", "ഇംഗ്ലീഷിൽ വായിക്കുക"), ("/panchang", "ഇന്നത്തെ പഞ്ചാംഗം"), ("/rahu-kaal", "രാഹുകാലം ഇന്ന്"),
           ("/choghadiya", "ഇന്നത്തെ ചോഘടിയ മുഹൂർത്തം"), ("/kundali-milan", "ജാതകപ്പൊരുത്തം"),
           ("/vrat-tyohar", "ഇന്നത്തെ വ്രതങ്ങളും ഉത്സവങ്ങളും")),
    "bn": (("{twin:en}", "ইংরেজিতে পড়ুন"), ("/panchang", "আজকের পঞ্জিকা"),
           ("/rahu-kaal", "আজকের রাহুকাল"), ("/choghadiya", "আজকের চৌঘড়িয়া"),
           ("/kundali-milan", "যোটক বিচার"), ("/vrat-tyohar", "আজকের ব্রত ও পার্বণ")),
    "or": (("{twin:en}", "ଇଂରାଜୀରେ ପଢ଼ନ୍ତୁ"), ("/panchang", "ଆଜିର ପାଞ୍ଜି"),
           ("/rahu-kaal", "ଆଜିର ରାହୁ କାଳ"), ("/choghadiya", "ଆଜିର ଚୌଘଡ଼ିଆ"),
           ("/kundali-milan", "କୁଣ୍ଡଳୀ ମିଳନ"), ("/vrat-tyohar", "ଆଜିର ବ୍ରତ ଓ ପର୍ବପର୍ବାଣି")),
}

# The rashifal's clock times are printed "6:29 AM" on the Hindi pages too (as
# they always have been); other languages use their own clock words.
CLOCK_LANG = {"hi": "en"}

# -- the phrase bank: see rashifal_pages' docstring for the classical scheme --

TONE_LABEL = {
    "en": {GOOD: "Favourable day", MIXED: "Mixed day", EASY: "Take it easy"},
    "hi": {GOOD: "अनुकूल दिन", MIXED: "मिश्रित दिन", EASY: "संयम का दिन"},
    "kn": {GOOD: "ಅನುಕೂಲಕರ ದಿನ", MIXED: "ಮಿಶ್ರ ಫಲದ ದಿನ", EASY: "ಸಂಯಮದ ದಿನ"},
    "te": {GOOD: "అనుకూలమైన రోజు", MIXED: "మిశ్రమ ఫలితాల రోజు", EASY: "సంయమనం పాటించే రోజు"},
    "ta": {GOOD: "சாதகமான நாள்", MIXED: "கலவையான நாள்", EASY: "நிதானமாக இருங்கள்"},
    "ml": {GOOD: "അനുകൂല ദിവസം", MIXED: "സമ്മിശ്ര ദിവസം", EASY: "സാവധാനം നീങ്ങുക"},
    "bn": {GOOD: "অনুকূল দিন", MIXED: "মিশ্র দিন", EASY: "সংযমের দিন"},
    "or": {GOOD: "ଅନୁକୂଳ ଦିନ", MIXED: "ମିଶ୍ରିତ ଦିନ", EASY: "ସଂଯମର ଦିନ"},
}
MOON_HOUSE: dict[int, dict[str, str]] = {
    1: {"en": "The Moon moves through your own sign today (Janma Chandra). Classical texts read "
              "this as a day of comfort and good spirits — good food, warm company and a clear "
              "sense of yourself. A good day to look after your own needs and begin small, "
              "personal things.",
        "hi": "आज चंद्रमा आपकी अपनी राशि (जन्म राशि) में गोचर कर रहा है। शास्त्रों में इसे सुख और "
              "प्रसन्नता का दिन माना गया है — अच्छा भोजन, अपनों का साथ और मन में स्पष्टता। अपनी "
              "ज़रूरतों का ध्यान रखने और छोटे निजी काम शुरू करने के लिए अच्छा दिन है।",
        "bn": "আজ চন্দ্র আপনার নিজের রাশিতে (জন্ম রাশি) গোচর করছে। শাস্ত্রে একে সুখ ও "
              "প্রসন্নতার দিন বলা হয় — ভালো খাবার, আপনজনের সঙ্গ আর মনে স্বচ্ছতা। নিজের "
              "প্রয়োজনের দিকে নজর দেওয়া ও ছোটখাটো ব্যক্তিগত কাজ শুরু করার জন্য ভালো "
              "দিন।",
        "or": "ଆଜି ଚନ୍ଦ୍ର ଆପଣଙ୍କ ନିଜ ରାଶିରେ (ଜନ୍ମ ରାଶି) ଗୋଚର କରୁଛନ୍ତି। ଶାସ୍ତ୍ରରେ ଏହାକୁ "
              "ସୁଖ ଓ ପ୍ରସନ୍ନତାର ଦିନ ବୋଲି ମାନାଯାଏ — ଭଲ ଖାଦ୍ୟ, ଆପଣାର ଲୋକଙ୍କ ସାଙ୍ଗ ଓ ମନରେ "
              "ସ୍ପଷ୍ଟତା। ନିଜ ଆବଶ୍ୟକତା ପ୍ରତି ଧ୍ୟାନ ଦେବା ଓ ଛୋଟ ଛୋଟ ବ୍ୟକ୍ତିଗତ କାମ ଆରମ୍ଭ "
              "କରିବା ପାଇଁ ଭଲ ଦିନ।"},
    2: {"en": "The Moon is in your 2nd house today. Tradition asks for care with money and words — "
              "expenses can creep up and small misunderstandings arise easily. Keep spending "
              "planned and speak gently at home; routine work goes fine.",
        "hi": "आज चंद्रमा आपकी राशि से दूसरे भाव में है। परंपरा के अनुसार आज धन और वाणी में "
              "सावधानी रखें — खर्च बढ़ सकते हैं और छोटी-छोटी गलतफ़हमियाँ हो सकती हैं। खर्च योजना से "
              "करें और घर में मधुर बोलें; नियमित काम ठीक चलेंगे।",
        "bn": "আজ চন্দ্র আপনার রাশি থেকে দ্বিতীয় ভাবে। প্রথা অনুযায়ী আজ টাকাপয়সা ও "
              "কথাবার্তায় সাবধান থাকুন — খরচ অজান্তে বাড়তে পারে, ছোটখাটো ভুল "
              "বোঝাবুঝিও সহজে হয়। খরচ পরিকল্পনা করে করুন আর বাড়িতে নরম সুরে কথা বলুন; "
              "রোজকার কাজ ঠিকঠাক চলবে।",
        "or": "ଆଜି ଚନ୍ଦ୍ର ଆପଣଙ୍କ ରାଶିରୁ ଦ୍ୱିତୀୟ ଭାବରେ ଅଛନ୍ତି। ପରମ୍ପରା ଅନୁସାରେ ଆଜି "
              "ଟଙ୍କାପଇସା ଓ କଥାବାର୍ତ୍ତାରେ ସାବଧାନ ରୁହନ୍ତୁ — ଖର୍ଚ୍ଚ ଅଜାଣତରେ ବଢ଼ିପାରେ ଏବଂ "
              "ଛୋଟ ଛୋଟ ଭୁଲ ବୁଝାମଣା ସହଜରେ ହୋଇପାରେ। ଯୋଜନା କରି ଖର୍ଚ୍ଚ କରନ୍ତୁ ଓ ଘରେ ମଧୁର "
              "ଭାଷାରେ କଥା କୁହନ୍ତୁ; ନିତିଦିନିଆ କାମ ଠିକ୍ ଚାଲିବ।"},
    3: {"en": "The Moon in your 3rd house is a favourable transit. Courage and initiative are "
              "high, effort brings results, and contact with siblings, friends and neighbours "
              "goes well. A good day for short trips, calls and pushing a pending task over the "
              "line.",
        "hi": "चंद्रमा का तीसरे भाव में गोचर शुभ माना गया है। साहस और उत्साह बढ़ा रहेगा, प्रयासों का "
              "फल मिलेगा, और भाई-बहनों, मित्रों व पड़ोसियों से संपर्क अच्छा रहेगा। छोटी यात्रा, "
              "बातचीत और अटके काम पूरे करने के लिए अच्छा दिन है।",
        "bn": "তৃতীয় ভাবে চন্দ্রের গোচর শুভ। সাহস ও উদ্যম বেশি থাকবে, চেষ্টার ফল "
              "মিলবে, আর ভাইবোন, বন্ধু ও প্রতিবেশীদের সঙ্গে যোগাযোগ ভালো হবে। ছোট "
              "যাত্রা, ফোনালাপ আর আটকে থাকা কাজ শেষ করার জন্য ভালো দিন।",
        "or": "ତୃତୀୟ ଭାବରେ ଚନ୍ଦ୍ରଙ୍କ ଗୋଚର ଶୁଭ। ସାହସ ଓ ଉତ୍ସାହ ଅଧିକ ରହିବ, ଚେଷ୍ଟାର ଫଳ "
              "ମିଳିବ, ଏବଂ ଭାଇଭଉଣୀ, ବନ୍ଧୁ ଓ ପଡ଼ୋଶୀଙ୍କ ସହ ଯୋଗାଯୋଗ ଭଲ ରହିବ। ଛୋଟ ଯାତ୍ରା, "
              "ଫୋନ୍‌ରେ କଥାବାର୍ତ୍ତା ଓ ଅଟକି ରହିଥିବା କାମ ସାରିବା ପାଇଁ ଭଲ ଦିନ।"},
    4: {"en": "The Moon in your 4th house can leave the mind a little unsettled — home matters or "
              "travel may feel tiring. Keep the day simple, avoid arguments at home and give "
              "yourself some quiet time; the mood lifts as the Moon moves on.",
        "hi": "चौथे भाव में चंद्रमा मन को थोड़ा अशांत कर सकता है — घरेलू बातें या यात्रा थकाऊ लग "
              "सकती हैं। दिन को सरल रखें, घर में बहस से बचें और कुछ समय शांति से बिताएँ; चंद्रमा के "
              "आगे बढ़ते ही मन हल्का होगा।",
        "bn": "চতুর্থ ভাবে চন্দ্র মনকে খানিকটা অস্থির করতে পারে — সংসারের বিষয় বা "
              "যাতায়াত ক্লান্তিকর লাগতে পারে। দিনটা সহজ রাখুন, বাড়িতে তর্ক এড়িয়ে "
              "চলুন এবং নিজেকে কিছুটা শান্ত সময় দিন; চন্দ্র এগিয়ে গেলেই মন হালকা হবে।",
        "or": "ଚତୁର୍ଥ ଭାବରେ ଚନ୍ଦ୍ର ମନକୁ ଟିକିଏ ଅସ୍ଥିର କରିପାରନ୍ତି — ଘର କଥା ବା ଯାତ୍ରା "
              "କ୍ଳାନ୍ତିକର ଲାଗିପାରେ। ଦିନଟିକୁ ସରଳ ରଖନ୍ତୁ, ଘରେ ଯୁକ୍ତିତର୍କରୁ ଦୂରେଇ ରୁହନ୍ତୁ "
              "ଓ ନିଜକୁ କିଛି ଶାନ୍ତ ସମୟ ଦିଅନ୍ତୁ; ଚନ୍ଦ୍ର ଆଗକୁ ବଢ଼ିଲେ ମନ ହାଲୁକା ହେବ।"},
    5: {"en": "The Moon in your 5th house is a mixed transit. Plans may meet small hurdles and "
              "the mind can swing between ideas. Avoid speculative decisions; study, creative "
              "work and time with children are better uses of the day.",
        "hi": "पाँचवें भाव में चंद्रमा मिश्रित फल देता है। योजनाओं में छोटी रुकावटें आ सकती हैं और "
              "मन विचारों में डोल सकता है। जोखिम भरे निर्णयों से बचें; पढ़ाई, रचनात्मक काम और बच्चों "
              "के साथ समय बिताना बेहतर रहेगा।",
        "bn": "পঞ্চম ভাবে চন্দ্রের গোচর মিশ্র ফল দেয়। পরিকল্পনায় ছোটখাটো বাধা আসতে "
              "পারে, মন এক ভাবনা থেকে আরেক ভাবনায় দুলতে পারে। ঝুঁকির সিদ্ধান্ত এড়িয়ে "
              "চলুন; পড়াশোনা, সৃজনশীল কাজ ও সন্তানদের সঙ্গে সময় কাটানোই আজ ভালো।",
        "or": "ପଞ୍ଚମ ଭାବରେ ଚନ୍ଦ୍ରଙ୍କ ଗୋଚର ମିଶ୍ରିତ ଫଳ ଦିଏ। ଯୋଜନାରେ ଛୋଟ ଛୋଟ ବାଧା ଆସିପାରେ "
              "ଏବଂ ମନ ଗୋଟିଏ ଭାବନାରୁ ଆଉ ଗୋଟିଏକୁ ଦୋହଲିପାରେ। ଝୁଙ୍କିପୂର୍ଣ୍ଣ ନିଷ୍ପତ୍ତିରୁ "
              "ଦୂରେଇ ରୁହନ୍ତୁ; ପାଠପଢ଼ା, ସୃଜନଶୀଳ କାମ ଓ ପିଲାମାନଙ୍କ ସହ ସମୟ ବିତାଇବା ଆଜି ଭଲ।"},
    6: {"en": "The Moon in your 6th house is one of its best transits. Classical texts promise "
              "success over rivals and obstacles, and the energy to clear a backlog. A good day "
              "for competitive work, settling pending issues and steady routines.",
        "hi": "छठे भाव में चंद्रमा का गोचर सबसे शुभ स्थितियों में गिना जाता है। शास्त्रों के अनुसार "
              "विरोधियों और बाधाओं पर विजय मिलती है और रुके काम निपटाने की ऊर्जा मिलती है। "
              "प्रतियोगिता, लंबित मामलों को सुलझाने और नियमित दिनचर्या के लिए अच्छा दिन है।",
        "bn": "ষষ্ঠ ভাবে চন্দ্রের গোচর সবচেয়ে শুভ অবস্থানগুলির একটি। শাস্ত্রমতে "
              "প্রতিপক্ষ ও বাধার ওপর জয় আসে, জমে থাকা কাজ সামলানোর শক্তিও মেলে। "
              "প্রতিযোগিতার কাজ, ঝুলে থাকা বিষয় মেটানো ও নিয়মিত দিনচর্যার জন্য ভালো "
              "দিন।",
        "or": "ଷଷ୍ଠ ଭାବରେ ଚନ୍ଦ୍ରଙ୍କ ଗୋଚର ସବୁଠାରୁ ଶୁଭ ସ୍ଥିତିମାନଙ୍କ ମଧ୍ୟରୁ ଗୋଟିଏ। ଶାସ୍ତ୍ର "
              "ଅନୁସାରେ ପ୍ରତିଦ୍ୱନ୍ଦ୍ୱୀ ଓ ବାଧା ଉପରେ ବିଜୟ ମିଳେ ଏବଂ ଜମି ରହିଥିବା କାମ ସାରିବାର "
              "ଶକ୍ତି ମିଳେ। ପ୍ରତିଯୋଗିତା, ବାକି ଥିବା ବିଷୟର ସମାଧାନ ଓ ନିୟମିତ ଦିନଚର୍ଯ୍ୟା ପାଇଁ "
              "ଭଲ ଦିନ।"},
    7: {"en": "The Moon in your 7th house favours partnership and company. Time with your spouse "
              "or partner, meetings and agreements tend to go smoothly, with comfort and good "
              "food. A good day to reach out and work together.",
        "hi": "सातवें भाव में चंद्रमा साझेदारी और संगति के लिए अनुकूल है। जीवनसाथी के साथ समय, "
              "मुलाक़ातें और समझौते सहजता से होते हैं, साथ में सुख-सुविधा भी। मिल-जुलकर काम करने का "
              "अच्छा दिन है।",
        "bn": "সপ্তম ভাবে চন্দ্র অংশীদারি ও সঙ্গের পক্ষে অনুকূল। জীবনসঙ্গীর সঙ্গে সময়, "
              "সাক্ষাৎ ও চুক্তি সাধারণত মসৃণভাবে হয়, সঙ্গে আরাম ও ভালো খাওয়াদাওয়া। "
              "অন্যদের সঙ্গে যোগাযোগ করা ও একসঙ্গে কাজ করার ভালো দিন।",
        "or": "ସପ୍ତମ ଭାବରେ ଚନ୍ଦ୍ର ଭାଗିଦାରୀ ଓ ସାହଚର୍ଯ୍ୟ ପାଇଁ ଅନୁକୂଳ। ଜୀବନସାଥୀଙ୍କ ସହ ସମୟ, "
              "ସାକ୍ଷାତ ଓ ଚୁକ୍ତି ସାଧାରଣତଃ ସହଜରେ ହୁଏ, ସାଙ୍ଗରେ ଆରାମ ଓ ଭଲ ଖାଦ୍ୟ। ଅନ୍ୟମାନଙ୍କ "
              "ସହ ଯୋଗାଯୋଗ କରିବା ଓ ମିଳିମିଶି କାମ କରିବାର ଭଲ ଦିନ।"},
    8: {"en": "The Moon is in your 8th house — the period known as Chandrashtama. Tradition "
              "advises against starting important new things today; unexpected delays are more "
              "likely and the mind can feel anxious. Keep a margin in your schedule, stick to "
              "familiar work and be gentle with yourself — it passes within two to three days.",
        "hi": "आज चंद्रमा आपकी राशि से आठवें भाव में है — इसे चंद्राष्टम कहा जाता है। परंपरा के अनुसार "
              "आज कोई महत्वपूर्ण नया काम शुरू न करें; अचानक देरी हो सकती है और मन में चिंता रह सकती "
              "है। समय में गुंजाइश रखें, जाने-पहचाने काम करें और स्वयं के प्रति धैर्य रखें — यह दो-तीन "
              "दिन में बीत जाता है।",
        "bn": "আজ চন্দ্র আপনার রাশি থেকে অষ্টম ভাবে — একে চন্দ্রাষ্টম বলা হয়। প্রথা "
              "অনুযায়ী আজ গুরুত্বপূর্ণ নতুন কাজ শুরু না করাই ভালো; হঠাৎ দেরি হওয়ার "
              "সম্ভাবনা বেশি, মনে দুশ্চিন্তাও আসতে পারে। সময়সূচিতে হাতে কিছুটা সময় "
              "রাখুন, চেনা কাজে থাকুন এবং নিজের প্রতি সদয় হোন — দুই-তিন দিনের মধ্যেই "
              "এই সময় কেটে যায়।",
        "or": "ଆଜି ଚନ୍ଦ୍ର ଆପଣଙ୍କ ରାଶିରୁ ଅଷ୍ଟମ ଭାବରେ — ଏହାକୁ ଚନ୍ଦ୍ରାଷ୍ଟମ କୁହାଯାଏ। "
              "ପରମ୍ପରା ଅନୁସାରେ ଆଜି କୌଣସି ଗୁରୁତ୍ୱପୂର୍ଣ୍ଣ ନୂଆ କାମ ଆରମ୍ଭ ନକରିବା ଭଲ; ହଠାତ୍ "
              "ବିଳମ୍ବ ହେବାର ସମ୍ଭାବନା ଅଧିକ ଏବଂ ମନରେ ଚିନ୍ତା ଆସିପାରେ। କାର୍ଯ୍ୟସୂଚୀରେ କିଛି "
              "ସମୟ ହାତରେ ରଖନ୍ତୁ, ଜଣାଶୁଣା କାମରେ ଲାଗି ରୁହନ୍ତୁ ଓ ନିଜ ପ୍ରତି ସଦୟ ରୁହନ୍ତୁ — "
              "ଦୁଇ-ତିନି ଦିନ ମଧ୍ୟରେ ଏହି ସମୟ ବିତିଯାଏ।"},
    9: {"en": "The Moon in your 9th house is a mixed transit. Plans may need extra effort and you "
              "may feel tired or distracted. Prayer, reading and time with elders or teachers "
              "suit the day better than big new ventures.",
        "hi": "नौवें भाव में चंद्रमा मिश्रित फल देता है। योजनाओं में अधिक मेहनत लग सकती है और थकान "
              "या ध्यान भटक सकता है। बड़े नए कामों की बजाय पूजा-पाठ, अध्ययन और बड़ों या गुरुजनों के "
              "साथ समय बिताना बेहतर रहेगा।",
        "bn": "নবম ভাবে চন্দ্রের গোচর মিশ্র ফল দেয়। পরিকল্পনায় বাড়তি পরিশ্রম লাগতে "
              "পারে, ক্লান্তি বা অন্যমনস্কতাও আসতে পারে। বড় নতুন উদ্যোগের চেয়ে "
              "প্রার্থনা, পাঠ এবং গুরুজন বা শিক্ষকদের সঙ্গে সময় কাটানো আজ বেশি "
              "মানানসই।",
        "or": "ନବମ ଭାବରେ ଚନ୍ଦ୍ରଙ୍କ ଗୋଚର ମିଶ୍ରିତ ଫଳ ଦିଏ। ଯୋଜନାରେ ଅଧିକ ପରିଶ୍ରମ ଲାଗିପାରେ "
              "ଏବଂ କ୍ଳାନ୍ତି ବା ଅନ୍ୟମନସ୍କତା ଆସିପାରେ। ବଡ଼ ନୂଆ ଉଦ୍ୟମ ଅପେକ୍ଷା ପ୍ରାର୍ଥନା, "
              "ପଠନ ଓ ଗୁରୁଜନ ବା ଶିକ୍ଷକଙ୍କ ସହ ସମୟ ବିତାଇବା ଆଜି ଅଧିକ ଉପଯୁକ୍ତ।"},
    10: {"en": "The Moon in your 10th house supports work and reputation. Tasks get done, seniors "
               "are receptive and effort is noticed. A good day to present your work, take a "
               "professional step or finish something visible.",
         "hi": "दसवें भाव में चंद्रमा कार्य और प्रतिष्ठा के लिए अनुकूल है। काम पूरे होंगे, वरिष्ठ लोग "
               "बात सुनेंगे और मेहनत दिखेगी। अपना काम प्रस्तुत करने या कार्यक्षेत्र में नया कदम उठाने "
               "के लिए अच्छा दिन है।",
         "bn": "দশম ভাবে চন্দ্র কাজ ও সুনামের পক্ষে সহায়ক। কাজ সম্পন্ন হবে, ঊর্ধ্বতনরা "
               "মন দিয়ে শুনবেন, পরিশ্রম নজরে পড়বে। নিজের কাজ তুলে ধরা, কর্মক্ষেত্রে "
               "নতুন পদক্ষেপ নেওয়া বা চোখে পড়ার মতো কোনো কাজ শেষ করার জন্য ভালো দিন।",
         "or": "ଦଶମ ଭାବରେ ଚନ୍ଦ୍ର କାମ ଓ ସୁନାମ ପାଇଁ ସହାୟକ। କାମ ସମ୍ପୂର୍ଣ୍ଣ ହେବ, ବରିଷ୍ଠମାନେ "
               "ଧ୍ୟାନ ଦେଇ ଶୁଣିବେ ଓ ପରିଶ୍ରମ ନଜରକୁ ଆସିବ। ନିଜ କାମ ଉପସ୍ଥାପନ କରିବା, "
               "କର୍ମକ୍ଷେତ୍ରରେ ନୂଆ ପଦକ୍ଷେପ ନେବା ବା ସମସ୍ତଙ୍କ ନଜରକୁ ଆସୁଥିବା କୌଣସି କାମ "
               "ସାରିବା ପାଇଁ ଭଲ ଦିନ।"},
    11: {"en": "The Moon in your 11th house — the house of gains — is a very favourable transit. "
               "Expect support from friends, good news and the fruit of earlier effort. A good "
               "day for networking, making requests and celebrating with others.",
         "hi": "ग्यारहवें भाव (लाभ भाव) में चंद्रमा बहुत शुभ माना गया है। मित्रों का सहयोग, शुभ "
               "समाचार और पिछली मेहनत का फल मिल सकता है। मेल-जोल बढ़ाने, अनुरोध करने और अपनों के "
               "साथ ख़ुशी मनाने का अच्छा दिन है।",
         "bn": "একাদশ ভাবে — লাভ ভাবে — চন্দ্রের গোচর খুবই শুভ। বন্ধুদের সহযোগিতা, সুখবর "
               "আর আগের পরিশ্রমের ফল আশা করতে পারেন। মেলামেশা বাড়ানো, অনুরোধ জানানো ও "
               "আপনজনের সঙ্গে আনন্দ ভাগ করে নেওয়ার ভালো দিন।",
         "or": "ଏକାଦଶ ଭାବରେ — ଲାଭ ଭାବରେ — ଚନ୍ଦ୍ରଙ୍କ ଗୋଚର ଅତି ଶୁଭ। ବନ୍ଧୁମାନଙ୍କ ସହଯୋଗ, ଶୁଭ "
               "ସମ୍ବାଦ ଓ ପୂର୍ବ ପରିଶ୍ରମର ଫଳ ଆଶା କରିପାରନ୍ତି। ମେଳାମେଶା ବଢ଼ାଇବା, ଅନୁରୋଧ "
               "କରିବା ଓ ଆପଣାର ଲୋକଙ୍କ ସହ ଖୁସି ବାଣ୍ଟିବାର ଭଲ ଦିନ।"},
    12: {"en": "The Moon in your 12th house can bring extra expenses and a tired, inward mood. "
               "Avoid overspending and late nights; the day suits rest, prayer, charity and "
               "finishing old work rather than starting new.",
         "hi": "बारहवें भाव में चंद्रमा अतिरिक्त खर्च और थका हुआ, अंतर्मुखी मन दे सकता है। फ़िज़ूलखर्ची "
               "और देर रात जागने से बचें; आज नया शुरू करने की बजाय विश्राम, पूजा, दान और पुराने काम "
               "पूरे करना अच्छा रहेगा।",
         "bn": "দ্বাদশ ভাবে চন্দ্র বাড়তি খরচ এবং ক্লান্ত, অন্তর্মুখী মেজাজ আনতে পারে। "
               "অতিরিক্ত খরচ ও রাত জাগা এড়িয়ে চলুন; নতুন কিছু শুরুর চেয়ে বিশ্রাম, "
               "প্রার্থনা, দান এবং পুরোনো কাজ শেষ করার জন্য দিনটি উপযুক্ত।",
         "or": "ଦ୍ୱାଦଶ ଭାବରେ ଚନ୍ଦ୍ର ଅତିରିକ୍ତ ଖର୍ଚ୍ଚ ଓ କ୍ଳାନ୍ତ, ଅନ୍ତର୍ମୁଖୀ ମନୋଭାବ "
               "ଆଣିପାରନ୍ତି। ଅଯଥା ଖର୍ଚ୍ଚ ଓ ରାତି ଉଜାଗରରୁ ଦୂରେଇ ରୁହନ୍ତୁ; ନୂଆ କିଛି ଆରମ୍ଭ "
               "କରିବା ଅପେକ୍ଷା ବିଶ୍ରାମ, ପ୍ରାର୍ଥନା, ଦାନ ଓ ପୁରୁଣା କାମ ସାରିବା ପାଇଁ ଦିନଟି "
               "ଉପଯୁକ୍ତ।"},
}

# Kannada
for _k, _v in {
    1: ("ಇಂದು ಚಂದ್ರ ನಿಮ್ಮದೇ ರಾಶಿಯಲ್ಲಿ ಸಂಚರಿಸುತ್ತಿದ್ದಾನೆ (ಜನ್ಮ ಚಂದ್ರ). ಶಾಸ್ತ್ರಗಳು ಇದನ್ನು ಸುಖ ಮತ್ತು "
        "ಉಲ್ಲಾಸದ ದಿನವೆಂದು ಹೇಳುತ್ತವೆ — ಒಳ್ಳೆಯ ಊಟ, ಆತ್ಮೀಯರ ಒಡನಾಟ ಮತ್ತು ನಿಮ್ಮ ಬಗ್ಗೆ ಸ್ಪಷ್ಟತೆ. ನಿಮ್ಮ "
        "ಅಗತ್ಯಗಳನ್ನು ನೋಡಿಕೊಳ್ಳಲು ಮತ್ತು ಸಣ್ಣ ವೈಯಕ್ತಿಕ ಕೆಲಸಗಳನ್ನು ಆರಂಭಿಸಲು ಒಳ್ಳೆಯ ದಿನ."),
    2: ("ಇಂದು ಚಂದ್ರ ನಿಮ್ಮ 2ನೇ ಮನೆಯಲ್ಲಿದ್ದಾನೆ. ಹಣ ಮತ್ತು ಮಾತಿನಲ್ಲಿ ಎಚ್ಚರಿಕೆ ವಹಿಸಲು ಸಂಪ್ರದಾಯ ಹೇಳುತ್ತದೆ "
        "— ಖರ್ಚು ಸದ್ದಿಲ್ಲದೆ ಹೆಚ್ಚಬಹುದು, ಸಣ್ಣ ತಪ್ಪುತಿಳುವಳಿಕೆಗಳು ಸುಲಭವಾಗಿ ಉಂಟಾಗಬಹುದು. ಖರ್ಚನ್ನು "
        "ಯೋಜಿತವಾಗಿಡಿ, ಮನೆಯಲ್ಲಿ ಮೃದುವಾಗಿ ಮಾತನಾಡಿ; ದಿನನಿತ್ಯದ ಕೆಲಸಗಳು ಸರಾಗವಾಗಿ ನಡೆಯುತ್ತವೆ."),
    3: ("ನಿಮ್ಮ 3ನೇ ಮನೆಯಲ್ಲಿ ಚಂದ್ರನ ಸಂಚಾರ ಶುಭ. ಧೈರ್ಯ ಮತ್ತು ಉತ್ಸಾಹ ಹೆಚ್ಚಾಗಿರುತ್ತದೆ, ಪ್ರಯತ್ನಕ್ಕೆ ಫಲ "
        "ಸಿಗುತ್ತದೆ, ಸಹೋದರ-ಸಹೋದರಿಯರು, ಸ್ನೇಹಿತರು ಮತ್ತು ನೆರೆಹೊರೆಯವರೊಂದಿಗಿನ ಸಂಪರ್ಕ ಚೆನ್ನಾಗಿರುತ್ತದೆ. ಸಣ್ಣ"
        " ಪ್ರಯಾಣ, ಮಾತುಕತೆ ಮತ್ತು ಬಾಕಿ ಇರುವ ಕೆಲಸವನ್ನು ಪೂರ್ಣಗೊಳಿಸಲು ಒಳ್ಳೆಯ ದಿನ."),
    4: ("ನಿಮ್ಮ 4ನೇ ಮನೆಯಲ್ಲಿ ಚಂದ್ರ ಮನಸ್ಸನ್ನು ಸ್ವಲ್ಪ ಅಸ್ಥಿರಗೊಳಿಸಬಹುದು — ಮನೆಯ ವಿಷಯಗಳು ಅಥವಾ ಪ್ರಯಾಣ ಆಯಾಸ "
        "ತರಬಹುದು. ದಿನವನ್ನು ಸರಳವಾಗಿಡಿ, ಮನೆಯಲ್ಲಿ ವಾದಗಳನ್ನು ತಪ್ಪಿಸಿ ಮತ್ತು ಸ್ವಲ್ಪ ಶಾಂತ ಸಮಯ ಕಳೆಯಿರಿ; "
        "ಚಂದ್ರ ಮುಂದೆ ಸಾಗಿದಂತೆ ಮನಸ್ಸು ಹಗುರಾಗುತ್ತದೆ."),
    5: ("ನಿಮ್ಮ 5ನೇ ಮನೆಯಲ್ಲಿ ಚಂದ್ರನ ಸಂಚಾರ ಮಿಶ್ರ ಫಲದಾಯಕ. ಯೋಜನೆಗಳಿಗೆ ಸಣ್ಣ ಅಡೆತಡೆಗಳು ಬರಬಹುದು, ಮನಸ್ಸು "
        "ಒಂದು ಯೋಚನೆಯಿಂದ ಇನ್ನೊಂದಕ್ಕೆ ತೂಗಾಡಬಹುದು. ಊಹೆಯ ಮೇಲೆ ನಿಂತ ನಿರ್ಧಾರಗಳನ್ನು ತಪ್ಪಿಸಿ; ಓದು, ಸೃಜನಶೀಲ "
        "ಕೆಲಸ ಮತ್ತು ಮಕ್ಕಳೊಂದಿಗೆ ಸಮಯ ಕಳೆಯುವುದು ಇಂದಿಗೆ ಹೆಚ್ಚು ಸೂಕ್ತ."),
    6: ("ನಿಮ್ಮ 6ನೇ ಮನೆಯಲ್ಲಿ ಚಂದ್ರನ ಸಂಚಾರ ಅತ್ಯುತ್ತಮ ಸ್ಥಾನಗಳಲ್ಲಿ ಒಂದು. ಪ್ರತಿಸ್ಪರ್ಧಿಗಳು ಮತ್ತು ಅಡೆತಡೆಗಳ "
        "ಮೇಲೆ ಜಯ, ಬಾಕಿ ಕೆಲಸಗಳನ್ನು ಮುಗಿಸುವ ಶಕ್ತಿ ಸಿಗುತ್ತದೆ ಎಂದು ಶಾಸ್ತ್ರಗಳು ಹೇಳುತ್ತವೆ. ಸ್ಪರ್ಧಾತ್ಮಕ "
        "ಕೆಲಸ, ಬಾಕಿ ವಿಷಯಗಳ ಇತ್ಯರ್ಥ ಮತ್ತು ನಿಯಮಿತ ದಿನಚರಿಗೆ ಒಳ್ಳೆಯ ದಿನ."),
    7: ("ನಿಮ್ಮ 7ನೇ ಮನೆಯಲ್ಲಿ ಚಂದ್ರ ಸಹಭಾಗಿತ್ವ ಮತ್ತು ಒಡನಾಟಕ್ಕೆ ಅನುಕೂಲ. ಸಂಗಾತಿಯೊಂದಿಗಿನ ಸಮಯ, ಭೇಟಿಗಳು "
        "ಮತ್ತು ಒಪ್ಪಂದಗಳು ಸುಗಮವಾಗಿ ನಡೆಯುತ್ತವೆ, ಜೊತೆಗೆ ಸುಖ ಮತ್ತು ಒಳ್ಳೆಯ ಊಟ. ಇತರರನ್ನು ಸಂಪರ್ಕಿಸಿ "
        "ಜೊತೆಯಾಗಿ ಕೆಲಸ ಮಾಡಲು ಒಳ್ಳೆಯ ದಿನ."),
    8: ("ಚಂದ್ರ ನಿಮ್ಮ 8ನೇ ಮನೆಯಲ್ಲಿದ್ದಾನೆ — ಇದನ್ನು ಚಂದ್ರಾಷ್ಟಮ ಎನ್ನುತ್ತಾರೆ. ಇಂದು ಮುಖ್ಯವಾದ ಹೊಸ "
        "ಕೆಲಸಗಳನ್ನು ಆರಂಭಿಸಬೇಡಿ ಎಂದು ಸಂಪ್ರದಾಯ ಸಲಹೆ ನೀಡುತ್ತದೆ; ಅನಿರೀಕ್ಷಿತ ವಿಳಂಬಗಳ ಸಾಧ್ಯತೆ ಹೆಚ್ಚು, "
        "ಮನಸ್ಸಿಗೆ ಆತಂಕ ಅನಿಸಬಹುದು. ವೇಳಾಪಟ್ಟಿಯಲ್ಲಿ ಸ್ವಲ್ಪ ಬಿಡುವು ಇಟ್ಟುಕೊಳ್ಳಿ, ಪರಿಚಿತ ಕೆಲಸಕ್ಕೇ "
        "ಅಂಟಿಕೊಳ್ಳಿ ಮತ್ತು ನಿಮ್ಮ ಬಗ್ಗೆ ಮೃದುವಾಗಿರಿ — ಇದು ಎರಡು-ಮೂರು ದಿನಗಳಲ್ಲಿ ಕಳೆದುಹೋಗುತ್ತದೆ."),
    9: ("ನಿಮ್ಮ 9ನೇ ಮನೆಯಲ್ಲಿ ಚಂದ್ರನ ಸಂಚಾರ ಮಿಶ್ರ ಫಲದಾಯಕ. ಯೋಜನೆಗಳಿಗೆ ಹೆಚ್ಚುವರಿ ಶ್ರಮ ಬೇಕಾಗಬಹುದು, ಆಯಾಸ "
        "ಅಥವಾ ಗಮನದ ಕೊರತೆ ಅನಿಸಬಹುದು. ದೊಡ್ಡ ಹೊಸ ಉದ್ಯಮಗಳಿಗಿಂತ ಪ್ರಾರ್ಥನೆ, ಓದು ಮತ್ತು ಹಿರಿಯರು ಅಥವಾ "
        "ಗುರುಜನರೊಂದಿಗೆ ಸಮಯ ಕಳೆಯುವುದು ಇಂದಿಗೆ ಹೆಚ್ಚು ಸೂಕ್ತ."),
    10: ("ನಿಮ್ಮ 10ನೇ ಮನೆಯಲ್ಲಿ ಚಂದ್ರ ಕೆಲಸ ಮತ್ತು ಕೀರ್ತಿಗೆ ಬೆಂಬಲ ನೀಡುತ್ತಾನೆ. ಕೆಲಸಗಳು ಪೂರ್ಣಗೊಳ್ಳುತ್ತವೆ, "
         "ಹಿರಿಯರು ನಿಮ್ಮ ಮಾತಿಗೆ ಕಿವಿಗೊಡುತ್ತಾರೆ ಮತ್ತು ಶ್ರಮ ಗಮನಕ್ಕೆ ಬರುತ್ತದೆ. ನಿಮ್ಮ ಕೆಲಸವನ್ನು "
         "ಪ್ರಸ್ತುತಪಡಿಸಲು, ವೃತ್ತಿಯಲ್ಲಿ ಒಂದು ಹೆಜ್ಜೆ ಇಡಲು ಅಥವಾ ಎಲ್ಲರಿಗೂ ಕಾಣುವ ಕೆಲಸವನ್ನು ಮುಗಿಸಲು ಒಳ್ಳೆಯ "
         "ದಿನ."),
    11: ("ನಿಮ್ಮ 11ನೇ ಮನೆಯಲ್ಲಿ — ಲಾಭ ಸ್ಥಾನದಲ್ಲಿ — ಚಂದ್ರನ ಸಂಚಾರ ಬಹಳ ಶುಭ. ಸ್ನೇಹಿತರ ಬೆಂಬಲ, ಶುಭ ಸುದ್ದಿ "
         "ಮತ್ತು ಹಿಂದಿನ ಪ್ರಯತ್ನಗಳ ಫಲ ನಿರೀಕ್ಷಿಸಬಹುದು. ಸಂಪರ್ಕ ಬೆಳೆಸಲು, ವಿನಂತಿಗಳನ್ನು ಮಾಡಲು ಮತ್ತು "
         "ಇತರರೊಂದಿಗೆ ಸಂಭ್ರಮಿಸಲು ಒಳ್ಳೆಯ ದಿನ."),
    12: ("ನಿಮ್ಮ 12ನೇ ಮನೆಯಲ್ಲಿ ಚಂದ್ರ ಹೆಚ್ಚುವರಿ ಖರ್ಚು ಮತ್ತು ದಣಿದ, ಅಂತರ್ಮುಖಿ ಮನಸ್ಥಿತಿಯನ್ನು ತರಬಹುದು. "
         "ಅತಿಯಾದ ಖರ್ಚು ಮತ್ತು ತಡರಾತ್ರಿಯವರೆಗೆ ಎಚ್ಚರವಿರುವುದನ್ನು ತಪ್ಪಿಸಿ; ಹೊಸದನ್ನು ಆರಂಭಿಸುವುದಕ್ಕಿಂತ "
         "ವಿಶ್ರಾಂತಿ, ಪ್ರಾರ್ಥನೆ, ದಾನ ಮತ್ತು ಹಳೆಯ ಕೆಲಸಗಳನ್ನು ಮುಗಿಸುವುದು ಇಂದಿಗೆ ಸೂಕ್ತ."),
}.items():
    MOON_HOUSE[_k]["kn"] = _v

# Telugu
for _k, _v in {
    1: ("ఈరోజు చంద్రుడు మీ సొంత రాశిలో సంచరిస్తున్నాడు (జన్మ చంద్రుడు). శాస్త్రాలు దీనిని సుఖం, "
        "ఉల్లాసం కలిగించే రోజుగా చెబుతాయి — మంచి భోజనం, ఆత్మీయుల సాంగత్యం, మీ గురించి మీకు స్పష్టత. "
        "మీ అవసరాలను చూసుకోవడానికి, చిన్న వ్యక్తిగత పనులు ప్రారంభించడానికి మంచి రోజు."),
    2: ("ఈరోజు చంద్రుడు మీ 2వ స్థానంలో ఉన్నాడు. డబ్బు, మాట విషయంలో జాగ్రత్తగా ఉండమని సంప్రదాయం "
        "చెబుతుంది — ఖర్చులు తెలియకుండానే పెరగవచ్చు, చిన్న అపార్థాలు సులభంగా తలెత్తవచ్చు. ఖర్చులను "
        "ప్రణాళికతో చేయండి, ఇంట్లో మృదువుగా మాట్లాడండి; రోజువారీ పనులు సాఫీగా సాగుతాయి."),
    3: ("మీ 3వ స్థానంలో చంద్ర సంచారం శుభప్రదం. ధైర్యం, చొరవ ఎక్కువగా ఉంటాయి, ప్రయత్నాలకు ఫలితం "
        "దక్కుతుంది, తోబుట్టువులు, స్నేహితులు, ఇరుగుపొరుగువారితో సంబంధాలు బాగుంటాయి. చిన్న "
        "ప్రయాణాలు, సంభాషణలు, నిలిచిపోయిన పనిని పూర్తి చేయడానికి మంచి రోజు."),
    4: ("మీ 4వ స్థానంలో చంద్రుడు మనసును కొంత అశాంతిగా ఉంచవచ్చు — ఇంటి విషయాలు లేదా ప్రయాణం అలసటగా "
        "అనిపించవచ్చు. రోజును సరళంగా ఉంచండి, ఇంట్లో వాదనలు నివారించండి, కొంత ప్రశాంత సమయం గడపండి; "
        "చంద్రుడు ముందుకు సాగగానే మనసు తేలికపడుతుంది."),
    5: ("మీ 5వ స్థానంలో చంద్ర సంచారం మిశ్రమ ఫలితాలనిస్తుంది. ప్రణాళికలకు చిన్న ఆటంకాలు ఎదురుకావచ్చు,"
        " మనసు ఆలోచనల మధ్య ఊగిసలాడవచ్చు. ఊహాగానాలపై ఆధారపడిన నిర్ణయాలను నివారించండి; చదువు, "
        "సృజనాత్మక పనులు, పిల్లలతో గడపడం ఈ రోజుకు మరింత ఉపయోగకరం."),
    6: ("మీ 6వ స్థానంలో చంద్ర సంచారం దాని ఉత్తమ స్థానాల్లో ఒకటి. ప్రత్యర్థులు, ఆటంకాలపై విజయం, "
        "పేరుకుపోయిన పనులను పూర్తి చేసే శక్తి లభిస్తాయని శాస్త్రాలు చెబుతాయి. పోటీతో కూడిన పనులు, "
        "అపరిష్కృత విషయాల పరిష్కారం, క్రమబద్ధమైన దినచర్యకు మంచి రోజు."),
    7: ("మీ 7వ స్థానంలో చంద్రుడు భాగస్వామ్యానికి, సాంగత్యానికి అనుకూలం. జీవిత భాగస్వామితో గడిపే "
        "సమయం, సమావేశాలు, ఒప్పందాలు సాఫీగా సాగుతాయి, సుఖం, మంచి భోజనం కూడా. ఇతరులను సంప్రదించి కలిసి"
        " పనిచేయడానికి మంచి రోజు."),
    8: ("చంద్రుడు మీ 8వ స్థానంలో ఉన్నాడు — దీనిని చంద్రాష్టమం అంటారు. ఈరోజు ముఖ్యమైన కొత్త పనులు "
        "ప్రారంభించవద్దని సంప్రదాయం సూచిస్తుంది; అనుకోని ఆలస్యాలకు అవకాశం ఎక్కువ, మనసులో ఆందోళన "
        "అనిపించవచ్చు. మీ కార్యక్రమాల్లో కొంత వెసులుబాటు ఉంచుకోండి, తెలిసిన పనులకే పరిమితం కండి, మీ "
        "పట్ల మృదువుగా ఉండండి — ఇది రెండు మూడు రోజుల్లో గడిచిపోతుంది."),
    9: ("మీ 9వ స్థానంలో చంద్ర సంచారం మిశ్రమ ఫలితాలనిస్తుంది. ప్రణాళికలకు అదనపు శ్రమ అవసరం కావచ్చు, "
        "అలసటగా లేదా ఏకాగ్రత లోపించినట్లు అనిపించవచ్చు. పెద్ద కొత్త ప్రయత్నాల కంటే ప్రార్థన, పఠనం, "
        "పెద్దలు లేదా గురువులతో గడపడం ఈ రోజుకు బాగా సరిపోతాయి."),
    10: ("మీ 10వ స్థానంలో చంద్రుడు ఉద్యోగానికి, ప్రతిష్ఠకు తోడ్పడతాడు. పనులు పూర్తవుతాయి, పై "
         "అధికారులు సానుకూలంగా వింటారు, మీ శ్రమ గుర్తింపు పొందుతుంది. మీ పనిని ప్రదర్శించడానికి, "
         "వృత్తిలో ఒక అడుగు వేయడానికి లేదా అందరికీ కనిపించే పనిని పూర్తి చేయడానికి మంచి రోజు."),
    11: ("మీ 11వ స్థానంలో — లాభ స్థానంలో — చంద్ర సంచారం చాలా శుభప్రదం. స్నేహితుల సహకారం, శుభవార్తలు,"
         " గత ప్రయత్నాల ఫలం ఆశించవచ్చు. పరిచయాలు పెంచుకోవడానికి, అభ్యర్థనలు చేయడానికి, ఇతరులతో కలిసి"
         " సంతోషించడానికి మంచి రోజు."),
    12: ("మీ 12వ స్థానంలో చంద్రుడు అదనపు ఖర్చులను, అలసిన, అంతర్ముఖ మనస్థితిని తేవచ్చు. అతిగా ఖర్చు "
         "చేయడం, రాత్రి ఆలస్యంగా మేల్కొనడం నివారించండి; కొత్తవి ప్రారంభించడం కంటే విశ్రాంతి, "
         "ప్రార్థన, దానం, పాత పనులు పూర్తి చేయడం ఈ రోజుకు తగినవి."),
}.items():
    MOON_HOUSE[_k]["te"] = _v

SATURN_HOUSE: dict[int, dict[str, str]] = {
    1: {"en": "Saturn is passing over your Moon sign — the peak phase of Sade Sati. It rewards "
              "patience, routine and honest effort; take on a little less and finish what you "
              "start.",
        "hi": "शनि आपकी चंद्र राशि पर गोचर कर रहे हैं — साढ़ेसाती का मध्य (चरम) चरण। यह समय धैर्य, "
              "नियमितता और ईमानदार मेहनत का फल देता है; थोड़ा कम काम हाथ में लें और जो शुरू करें उसे "
              "पूरा करें।",
        "bn": "শনি আপনার চন্দ্র রাশির ওপর দিয়ে গোচর করছেন — সাড়েসাতির মধ্য (চরম) "
              "পর্যায়। এই সময় ধৈর্য, নিয়মানুবর্তিতা ও সৎ পরিশ্রমের ফল দেয়; একটু কম "
              "দায়িত্ব নিন এবং যা শুরু করেন তা শেষ করুন।",
        "or": "ଶନି ଆପଣଙ୍କ ଚନ୍ଦ୍ର ରାଶି ଉପରେ ଗୋଚର କରୁଛନ୍ତି — ସାଢ଼େସାତିର ମଧ୍ୟ (ଶିଖର) "
              "ପର୍ଯ୍ୟାୟ। ଏହି ସମୟ ଧୈର୍ଯ୍ୟ, ନିୟମାନୁବର୍ତ୍ତିତା ଓ ସଚ୍ଚୋଟ ପରିଶ୍ରମର ଫଳ ଦିଏ; "
              "ଟିକିଏ କମ୍ ଦାୟିତ୍ୱ ନିଅନ୍ତୁ ଏବଂ ଯାହା ଆରମ୍ଭ କରନ୍ତି ତାହା ଶେଷ କରନ୍ତୁ।"},
    2: {"en": "Saturn is in your 2nd — the last phase of Sade Sati. Be measured with spending and "
              "with words at home; the pressure is easing.",
        "hi": "शनि दूसरे भाव में हैं — साढ़ेसाती का अंतिम चरण। घर में खर्च और वाणी संयमित रखें; दबाव "
              "धीरे-धीरे कम हो रहा है।",
        "bn": "শনি দ্বিতীয় ভাবে — সাড়েসাতির শেষ পর্যায়। বাড়িতে খরচ ও কথায় সংযত "
              "থাকুন; চাপ ধীরে ধীরে কমছে।",
        "or": "ଶନି ଦ୍ୱିତୀୟ ଭାବରେ — ସାଢ଼େସାତିର ଶେଷ ପର୍ଯ୍ୟାୟ। ଘରେ ଖର୍ଚ୍ଚ ଓ କଥାରେ ସଂଯତ "
              "ରୁହନ୍ତୁ; ଚାପ ଧୀରେ ଧୀରେ କମୁଛି।"},
    3: {"en": "Saturn in your 3rd is one of its best positions — steady effort pays, courage grows "
              "and long-running work gains traction.",
        "hi": "शनि तीसरे भाव में हैं — शनि की सबसे शुभ स्थितियों में से एक। लगातार प्रयास फल देते हैं, "
              "साहस बढ़ता है और लंबे समय से चल रहे काम गति पकड़ते हैं।",
        "bn": "তৃতীয় ভাবে শনি তাঁর সেরা অবস্থানগুলির একটিতে — নিয়মিত চেষ্টা ফল দেয়, "
              "সাহস বাড়ে এবং দীর্ঘদিনের কাজ গতি পায়।",
        "or": "ତୃତୀୟ ଭାବରେ ଶନି ତାଙ୍କ ସର୍ବୋତ୍ତମ ସ୍ଥିତିମାନଙ୍କ ମଧ୍ୟରୁ ଗୋଟିଏରେ — ନିରନ୍ତର "
              "ଚେଷ୍ଟା ଫଳ ଦିଏ, ସାହସ ବଢ଼େ ଏବଂ ଦୀର୍ଘ ଦିନର କାମ ଗତି ପାଏ।"},
    4: {"en": "Saturn in your 4th (Dhaiya, Kantaka Shani) can make home life and peace of mind feel "
              "heavier; keep routines simple and handle family matters calmly.",
        "hi": "शनि चौथे भाव में हैं (ढैया, कंटक शनि) — घर और मन की शांति पर बोझ महसूस हो सकता है; "
              "दिनचर्या सरल रखें और पारिवारिक बातें शांति से सँभालें।",
        "bn": "চতুর্থ ভাবে শনি (ঢাইয়া, কণ্টক শনি) সংসার ও মনের শান্তিকে কিছুটা ভারী "
              "করে তুলতে পারেন; দিনচর্যা সহজ রাখুন এবং পারিবারিক বিষয় শান্তভাবে "
              "সামলান।",
        "or": "ଚତୁର୍ଥ ଭାବରେ ଶନି (ଢାଇୟା, କଣ୍ଟକ ଶନି) ଘର ଓ ମନର ଶାନ୍ତିକୁ ଟିକିଏ ଭାରି "
              "କରିପାରନ୍ତି; ଦିନଚର୍ଯ୍ୟା ସରଳ ରଖନ୍ତୁ ଓ ପାରିବାରିକ କଥା ଶାନ୍ତ ଭାବରେ "
              "ସମ୍ଭାଳନ୍ତୁ।"},
    5: {"en": "Saturn in your 5th asks for patience with plans, studies and children's matters — "
              "slow and careful beats quick.",
        "hi": "शनि पाँचवें भाव में हैं — योजनाओं, पढ़ाई और संतान संबंधी बातों में धैर्य रखें; जल्दबाज़ी "
              "से अच्छा है धीमे और सोच-समझकर चलना।",
        "bn": "পঞ্চম ভাবে শনি পরিকল্পনা, পড়াশোনা ও সন্তান-সংক্রান্ত বিষয়ে ধৈর্য চান — "
              "তাড়াহুড়োর চেয়ে ধীরে ও ভেবেচিন্তে চলাই ভালো।",
        "or": "ପଞ୍ଚମ ଭାବରେ ଶନି ଯୋଜନା, ପାଠପଢ଼ା ଓ ସନ୍ତାନ ସମ୍ବନ୍ଧୀୟ କଥାରେ ଧୈର୍ଯ୍ୟ ଚାହାନ୍ତି "
              "— ତରବର ଅପେକ୍ଷା ଧୀରେ ଓ ଚିନ୍ତା କରି ଚାଲିବା ଭଲ।"},
    6: {"en": "Saturn in your 6th works in your favour — discipline wins over rivals and backlog, "
              "and hard work gets noticed.",
        "hi": "शनि छठे भाव में आपके पक्ष में हैं — अनुशासन से विरोधियों और अटके कामों पर जीत मिलती है, "
              "और मेहनत पर लोगों की नज़र जाती है।",
        "bn": "ষষ্ঠ ভাবে শনি আপনার পক্ষে কাজ করেন — শৃঙ্খলা দিয়ে প্রতিপক্ষ ও জমে থাকা "
              "কাজের ওপর জয় আসে, পরিশ্রম সবার নজরে পড়ে।",
        "or": "ଷଷ୍ଠ ଭାବରେ ଶନି ଆପଣଙ୍କ ସପକ୍ଷରେ କାମ କରନ୍ତି — ଅନୁଶାସନ ଦ୍ୱାରା ପ୍ରତିଦ୍ୱନ୍ଦ୍ୱୀ "
              "ଓ ଜମା କାମ ଉପରେ ବିଜୟ ମିଳେ, ପରିଶ୍ରମ ସମସ୍ତଙ୍କ ନଜରକୁ ଆସେ।"},
    7: {"en": "Saturn in your 7th puts partnerships in a slow, serious light — clear agreements "
              "and patience help.",
        "hi": "शनि सातवें भाव में हैं — साझेदारी और संबंधों में गंभीरता आती है; स्पष्ट बातचीत और धैर्य "
              "सहायक हैं।",
        "bn": "সপ্তম ভাবে শনি অংশীদারি ও সম্পর্ককে ধীর, গম্ভীর আলোয় দেখান — স্পষ্ট "
              "বোঝাপড়া ও ধৈর্য সাহায্য করে।",
        "or": "ସପ୍ତମ ଭାବରେ ଶନି ଭାଗିଦାରୀ ଓ ସମ୍ପର୍କରେ ଧୀର, ଗମ୍ଭୀର ଭାବ ଆଣନ୍ତି — ସ୍ପଷ୍ଟ "
              "ବୁଝାମଣା ଓ ଧୈର୍ଯ୍ୟ ସାହାଯ୍ୟ କରେ।"},
    8: {"en": "Saturn in your 8th (Dhaiya, Ashtama Shani) is a time to avoid shortcuts and keep a "
              "margin for delays.",
        "hi": "शनि आठवें भाव में हैं (ढैया, अष्टम शनि) — शॉर्टकट से बचें और देरी के लिए समय की "
              "गुंजाइश रखें।",
        "bn": "অষ্টম ভাবে শনি (ঢাইয়া, অষ্টম শনি) — চটজলদি সহজ পথ এড়িয়ে চলুন এবং "
              "দেরির জন্য হাতে সময় রাখুন।",
        "or": "ଅଷ୍ଟମ ଭାବରେ ଶନି (ଢାଇୟା, ଅଷ୍ଟମ ଶନି) — ଚଟ୍‌ଜଲଦି ସହଜ ବାଟରୁ ଦୂରେଇ ରୁହନ୍ତୁ "
              "ଏବଂ ବିଳମ୍ବ ପାଇଁ ହାତରେ ସମୟ ରଖନ୍ତୁ।"},
    9: {"en": "Saturn in your 9th can slow luck and long journeys; respect for elders and steady "
              "duty keep things on track.",
        "hi": "शनि नौवें भाव में भाग्य और लंबी यात्राओं को धीमा कर सकते हैं; बड़ों का सम्मान और "
              "कर्तव्य-पालन चीज़ों को पटरी पर रखते हैं।",
        "bn": "নবম ভাবে শনি ভাগ্য ও দূরযাত্রাকে ধীর করতে পারেন; গুরুজনদের প্রতি শ্রদ্ধা "
              "ও নিয়মিত কর্তব্যপালন সবকিছু ঠিক পথে রাখে।",
        "or": "ନବମ ଭାବରେ ଶନି ଭାଗ୍ୟ ଓ ଦୂର ଯାତ୍ରାକୁ ଧୀମା କରିପାରନ୍ତି; ଗୁରୁଜନଙ୍କ ପ୍ରତି "
              "ସମ୍ମାନ ଓ ନିୟମିତ କର୍ତ୍ତବ୍ୟ ପାଳନ ସବୁକିଛି ଠିକ୍ ବାଟରେ ରଖେ।"},
    10: {"en": "Saturn in your 10th brings responsibility at work — a heavier load, but sincere "
               "effort builds a lasting reputation.",
         "hi": "शनि दसवें भाव में हैं — कार्यक्षेत्र में ज़िम्मेदारी बढ़ती है; भार अधिक है, पर सच्ची "
               "मेहनत स्थायी प्रतिष्ठा बनाती है।",
         "bn": "দশম ভাবে শনি কর্মক্ষেত্রে দায়িত্ব বাড়ান — বোঝা বেশি, তবে আন্তরিক "
               "পরিশ্রম স্থায়ী সুনাম গড়ে তোলে।",
         "or": "ଦଶମ ଭାବରେ ଶନି କର୍ମକ୍ଷେତ୍ରରେ ଦାୟିତ୍ୱ ବଢ଼ାନ୍ତି — ଭାର ଅଧିକ, କିନ୍ତୁ ଆନ୍ତରିକ "
               "ପରିଶ୍ରମ ସ୍ଥାୟୀ ସୁନାମ ଗଢ଼େ।"},
    11: {"en": "Saturn in your 11th is favourable — gains come slowly but surely, and long effort "
               "starts to pay off.",
         "hi": "शनि ग्यारहवें भाव में शुभ हैं — लाभ धीरे-धीरे पर पक्के तौर पर आता है और लंबी मेहनत का "
               "फल मिलने लगता है।",
         "bn": "একাদশ ভাবে শনি শুভ — লাভ আসে ধীরে কিন্তু নিশ্চিতভাবে, দীর্ঘ পরিশ্রমের ফল "
               "মিলতে শুরু করে।",
         "or": "ଏକାଦଶ ଭାବରେ ଶନି ଶୁଭ — ଲାଭ ଧୀରେ କିନ୍ତୁ ନିଶ୍ଚିତ ଭାବରେ ଆସେ, ଦୀର୍ଘ ପରିଶ୍ରମର "
               "ଫଳ ମିଳିବା ଆରମ୍ଭ ହୁଏ।"},
    12: {"en": "Saturn is in your 12th — the opening phase of Sade Sati. Watch expenses and rest "
               "well; a good time for quiet, inward work.",
         "hi": "शनि बारहवें भाव में हैं — साढ़ेसाती का पहला चरण। खर्चों पर नज़र रखें और पर्याप्त विश्राम "
               "करें; शांत, आत्मचिंतन वाले काम के लिए अच्छा समय।",
         "bn": "শনি দ্বাদশ ভাবে — সাড়েসাতির প্রথম পর্যায়। খরচের দিকে নজর রাখুন ও ভালো "
               "করে বিশ্রাম নিন; শান্ত, অন্তর্মুখী কাজের পক্ষে ভালো সময়।",
         "or": "ଶନି ଦ୍ୱାଦଶ ଭାବରେ — ସାଢ଼େସାତିର ପ୍ରଥମ ପର୍ଯ୍ୟାୟ। ଖର୍ଚ୍ଚ ଉପରେ ନଜର ରଖନ୍ତୁ ଓ "
               "ଭଲ ଭାବରେ ବିଶ୍ରାମ ନିଅନ୍ତୁ; ଶାନ୍ତ, ଅନ୍ତର୍ମୁଖୀ କାମ ପାଇଁ ଭଲ ସମୟ।"},
}

# Kannada
for _k, _v in {
    1: ("ಶನಿ ನಿಮ್ಮ ಚಂದ್ರ ರಾಶಿಯ ಮೇಲೆ ಸಂಚರಿಸುತ್ತಿದ್ದಾನೆ — ಸಾಡೇಸಾತಿಯ ಉತ್ತುಂಗದ (ಮಧ್ಯದ) ಹಂತ. ಇದು ತಾಳ್ಮೆ, "
        "ನಿಯಮಿತ ದಿನಚರಿ ಮತ್ತು ಪ್ರಾಮಾಣಿಕ ಪ್ರಯತ್ನಕ್ಕೆ ಫಲ ನೀಡುತ್ತದೆ; ಸ್ವಲ್ಪ ಕಡಿಮೆ ಕೆಲಸ ವಹಿಸಿಕೊಳ್ಳಿ ಮತ್ತು"
        " ಆರಂಭಿಸಿದ್ದನ್ನು ಮುಗಿಸಿ."),
    2: ("ಶನಿ ನಿಮ್ಮ 2ನೇ ಮನೆಯಲ್ಲಿ — ಸಾಡೇಸಾತಿಯ ಕೊನೆಯ ಹಂತ. ಖರ್ಚಿನಲ್ಲಿ ಮತ್ತು ಮನೆಯಲ್ಲಿ ಮಾತಿನಲ್ಲಿ "
        "ಮಿತವಾಗಿರಿ; ಒತ್ತಡ ಕಡಿಮೆಯಾಗುತ್ತಿದೆ."),
    3: ("ನಿಮ್ಮ 3ನೇ ಮನೆಯಲ್ಲಿ ಶನಿ — ಶನಿಯ ಅತ್ಯುತ್ತಮ ಸ್ಥಾನಗಳಲ್ಲಿ ಒಂದು. ನಿರಂತರ ಪ್ರಯತ್ನ ಫಲ ನೀಡುತ್ತದೆ, "
        "ಧೈರ್ಯ ಬೆಳೆಯುತ್ತದೆ ಮತ್ತು ದೀರ್ಘಕಾಲದ ಕೆಲಸಗಳು ವೇಗ ಪಡೆಯುತ್ತವೆ."),
    4: ("ನಿಮ್ಮ 4ನೇ ಮನೆಯಲ್ಲಿ ಶನಿ (ಢೈಯಾ — ಅರ್ಧಾಷ್ಟಮ / ಕಂಟಕ ಶನಿ) ಮನೆಯ ಜೀವನ ಮತ್ತು ಮನಶ್ಶಾಂತಿಯನ್ನು ಸ್ವಲ್ಪ "
        "ಭಾರವಾಗಿಸಬಹುದು; ದಿನಚರಿಯನ್ನು ಸರಳವಾಗಿಡಿ ಮತ್ತು ಕುಟುಂಬದ ವಿಷಯಗಳನ್ನು ಶಾಂತವಾಗಿ ನಿಭಾಯಿಸಿ."),
    5: ("ನಿಮ್ಮ 5ನೇ ಮನೆಯಲ್ಲಿ ಶನಿ ಯೋಜನೆಗಳು, ಓದು ಮತ್ತು ಮಕ್ಕಳ ವಿಷಯಗಳಲ್ಲಿ ತಾಳ್ಮೆ ಬಯಸುತ್ತಾನೆ — ಆತುರಕ್ಕಿಂತ "
        "ನಿಧಾನ ಮತ್ತು ಎಚ್ಚರಿಕೆಯೇ ಉತ್ತಮ."),
    6: ("ನಿಮ್ಮ 6ನೇ ಮನೆಯಲ್ಲಿ ಶನಿ ನಿಮ್ಮ ಪರವಾಗಿ ಕೆಲಸ ಮಾಡುತ್ತಾನೆ — ಶಿಸ್ತಿನಿಂದ ಪ್ರತಿಸ್ಪರ್ಧಿಗಳು ಮತ್ತು ಬಾಕಿ"
        " ಕೆಲಸಗಳ ಮೇಲೆ ಜಯ, ಕಠಿಣ ಪರಿಶ್ರಮ ಗಮನಕ್ಕೆ ಬರುತ್ತದೆ."),
    7: ("ನಿಮ್ಮ 7ನೇ ಮನೆಯಲ್ಲಿ ಶನಿ ಸಹಭಾಗಿತ್ವಗಳಿಗೆ ನಿಧಾನ, ಗಂಭೀರ ಸ್ವರೂಪ ನೀಡುತ್ತಾನೆ — ಸ್ಪಷ್ಟ ಒಪ್ಪಂದಗಳು "
        "ಮತ್ತು ತಾಳ್ಮೆ ನೆರವಾಗುತ್ತವೆ."),
    8: ("ನಿಮ್ಮ 8ನೇ ಮನೆಯಲ್ಲಿ ಶನಿ (ಢೈಯಾ — ಅಷ್ಟಮ ಶನಿ) — ಅಡ್ಡದಾರಿಗಳನ್ನು ತಪ್ಪಿಸಿ ಮತ್ತು ವಿಳಂಬಗಳಿಗಾಗಿ "
        "ಸಮಯದಲ್ಲಿ ಬಿಡುವು ಇಟ್ಟುಕೊಳ್ಳುವ ಕಾಲ."),
    9: ("ನಿಮ್ಮ 9ನೇ ಮನೆಯಲ್ಲಿ ಶನಿ ಅದೃಷ್ಟ ಮತ್ತು ದೂರ ಪ್ರಯಾಣಗಳನ್ನು ನಿಧಾನಗೊಳಿಸಬಹುದು; ಹಿರಿಯರಿಗೆ ಗೌರವ ಮತ್ತು "
        "ಸ್ಥಿರವಾದ ಕರ್ತವ್ಯ ಪಾಲನೆ ಎಲ್ಲವನ್ನೂ ಸರಿಯಾದ ದಾರಿಯಲ್ಲಿಡುತ್ತವೆ."),
    10: ("ನಿಮ್ಮ 10ನೇ ಮನೆಯಲ್ಲಿ ಶನಿ ಕೆಲಸದಲ್ಲಿ ಜವಾಬ್ದಾರಿ ತರುತ್ತಾನೆ — ಹೊರೆ ಹೆಚ್ಚು, ಆದರೆ ಪ್ರಾಮಾಣಿಕ "
         "ಪ್ರಯತ್ನ ಶಾಶ್ವತ ಕೀರ್ತಿಯನ್ನು ಕಟ್ಟುತ್ತದೆ."),
    11: ("ನಿಮ್ಮ 11ನೇ ಮನೆಯಲ್ಲಿ ಶನಿ ಶುಭ — ಲಾಭ ನಿಧಾನವಾಗಿ ಆದರೆ ಖಚಿತವಾಗಿ ಬರುತ್ತದೆ, ದೀರ್ಘ ಪ್ರಯತ್ನಕ್ಕೆ ಫಲ "
         "ಸಿಗಲಾರಂಭಿಸುತ್ತದೆ."),
    12: ("ಶನಿ ನಿಮ್ಮ 12ನೇ ಮನೆಯಲ್ಲಿ — ಸಾಡೇಸಾತಿಯ ಆರಂಭದ ಹಂತ. ಖರ್ಚುಗಳ ಮೇಲೆ ಗಮನವಿಡಿ ಮತ್ತು ಚೆನ್ನಾಗಿ "
         "ವಿಶ್ರಾಂತಿ ಪಡೆಯಿರಿ; ಶಾಂತ, ಅಂತರ್ಮುಖಿ ಕೆಲಸಕ್ಕೆ ಒಳ್ಳೆಯ ಸಮಯ."),
}.items():
    SATURN_HOUSE[_k]["kn"] = _v

# Telugu
for _k, _v in {
    1: ("శని మీ చంద్ర రాశిపై సంచరిస్తున్నాడు — ఏలినాటి శనిలో ప్రధానమైన (మధ్య) దశ. ఇది ఓర్పు, క్రమమైన"
        " దినచర్య, నిజాయితీ శ్రమకు ఫలమిస్తుంది; కొంచెం తక్కువ పనులు చేపట్టండి, ప్రారంభించినది పూర్తి"
        " చేయండి."),
    2: ("శని మీ 2వ స్థానంలో — ఏలినాటి శని చివరి దశ. ఖర్చుల్లో, ఇంట్లో మాటల్లో మితంగా ఉండండి; ఒత్తిడి"
        " తగ్గుతోంది."),
    3: ("మీ 3వ స్థానంలో శని — శని ఉత్తమ స్థానాల్లో ఒకటి. నిరంతర శ్రమ ఫలిస్తుంది, ధైర్యం పెరుగుతుంది,"
        " చాలా కాలంగా సాగుతున్న పనులు వేగం పుంజుకుంటాయి."),
    4: ("మీ 4వ స్థానంలో శని (ఢైయా — అర్ధాష్టమ / కంటక శని) ఇంటి జీవితాన్ని, మనశ్శాంతిని కొంత భారంగా "
        "అనిపించేలా చేయవచ్చు; దినచర్యను సరళంగా ఉంచండి, కుటుంబ విషయాలను ప్రశాంతంగా చక్కబెట్టండి."),
    5: ("మీ 5వ స్థానంలో శని ప్రణాళికలు, చదువు, పిల్లల విషయాల్లో ఓర్పును కోరుతాడు — తొందర కంటే "
        "నెమ్మదిగా, జాగ్రత్తగా వెళ్లడమే మేలు."),
    6: ("మీ 6వ స్థానంలో శని మీకు అనుకూలంగా పనిచేస్తాడు — క్రమశిక్షణతో ప్రత్యర్థులపై, పేరుకుపోయిన "
        "పనులపై విజయం, కష్టపడి చేసిన పనికి గుర్తింపు."),
    7: ("మీ 7వ స్థానంలో శని భాగస్వామ్యాలకు నెమ్మదైన, గంభీరమైన స్వభావాన్ని ఇస్తాడు — స్పష్టమైన "
        "ఒప్పందాలు, ఓర్పు సహాయపడతాయి."),
    8: ("మీ 8వ స్థానంలో శని (ఢైయా — అష్టమ శని) — అడ్డదారులను నివారించి, ఆలస్యాల కోసం సమయంలో "
        "వెసులుబాటు ఉంచుకోవలసిన కాలం."),
    9: ("మీ 9వ స్థానంలో శని అదృష్టాన్ని, దూర ప్రయాణాలను నెమ్మదింపజేయవచ్చు; పెద్దల పట్ల గౌరవం, "
        "స్థిరమైన కర్తవ్య పాలన పనులను సరైన దారిలో ఉంచుతాయి."),
    10: ("మీ 10వ స్థానంలో శని ఉద్యోగంలో బాధ్యతలను తెస్తాడు — భారం ఎక్కువే, కానీ నిజాయితీతో చేసే శ్రమ"
         " శాశ్వతమైన పేరు తెస్తుంది."),
    11: ("మీ 11వ స్థానంలో శని శుభప్రదం — లాభాలు నెమ్మదిగా అయినా తప్పకుండా వస్తాయి, దీర్ఘకాల శ్రమ "
         "ఫలించడం మొదలవుతుంది."),
    12: ("శని మీ 12వ స్థానంలో — ఏలినాటి శని ప్రారంభ దశ. ఖర్చులపై దృష్టి పెట్టండి, తగినంత విశ్రాంతి "
         "తీసుకోండి; ప్రశాంతమైన, అంతర్ముఖ పనులకు మంచి సమయం."),
}.items():
    SATURN_HOUSE[_k]["te"] = _v

JUPITER_HOUSE: dict[int, dict[str, str]] = {
    1: {"en": "Jupiter over your Moon sign is classically a restless position; keep plans "
              "grounded and avoid over-committing.",
        "hi": "गुरु आपकी चंद्र राशि पर हैं — शास्त्रों में इसे अस्थिरता की स्थिति माना गया है; योजनाएँ "
              "व्यावहारिक रखें और ज़रूरत से ज़्यादा वादे न करें।",
        "bn": "আপনার চন্দ্র রাশির ওপর বৃহস্পতি শাস্ত্রমতে অস্থিরতার অবস্থান; পরিকল্পনা "
              "বাস্তবসম্মত রাখুন এবং সাধ্যের বেশি প্রতিশ্রুতি দেবেন না।",
        "or": "ଆପଣଙ୍କ ଚନ୍ଦ୍ର ରାଶି ଉପରେ ବୃହସ୍ପତି ଶାସ୍ତ୍ର ଅନୁସାରେ ଅସ୍ଥିରତାର ସ୍ଥିତି; ଯୋଜନା "
              "ବାସ୍ତବଧର୍ମୀ ରଖନ୍ତୁ ଓ ସାମର୍ଥ୍ୟଠାରୁ ଅଧିକ ପ୍ରତିଶ୍ରୁତି ଦିଅନ୍ତୁ ନାହିଁ।"},
    2: {"en": "Jupiter in your 2nd supports family harmony, savings and kind speech.",
        "hi": "गुरु दूसरे भाव में पारिवारिक सौहार्द, बचत और मधुर वाणी को बल देते हैं।",
        "bn": "দ্বিতীয় ভাবে বৃহস্পতি পারিবারিক সম্প্রীতি, সঞ্চয় ও মধুর বাক্যকে বল "
              "দেন।",
        "or": "ଦ୍ୱିତୀୟ ଭାବରେ ବୃହସ୍ପତି ପାରିବାରିକ ସଦ୍ଭାବ, ସଞ୍ଚୟ ଓ ମଧୁର ବାଣୀକୁ ବଳ ଦିଅନ୍ତି।"},
    3: {"en": "Jupiter in your 3rd asks a little more effort for the same result — keep at it.",
        "hi": "गुरु तीसरे भाव में हैं — उसी परिणाम के लिए थोड़ी अधिक मेहनत लगती है; लगे रहें।",
        "bn": "তৃতীয় ভাবে বৃহস্পতি থাকলে একই ফলের জন্য একটু বেশি পরিশ্রম লাগে — লেগে "
              "থাকুন।",
        "or": "ତୃତୀୟ ଭାବରେ ବୃହସ୍ପତି ଥିଲେ ସମାନ ଫଳ ପାଇଁ ଟିକିଏ ଅଧିକ ପରିଶ୍ରମ ଲାଗେ — ଲାଗି "
              "ରୁହନ୍ତୁ।"},
    4: {"en": "Jupiter in your 4th can unsettle home matters; patience with relatives helps.",
        "hi": "गुरु चौथे भाव में घरेलू मामलों में उतार-चढ़ाव ला सकते हैं; रिश्तेदारों के साथ धैर्य रखें।",
        "bn": "চতুর্থ ভাবে বৃহস্পতি সংসারের বিষয়ে কিছুটা অস্থিরতা আনতে পারেন; "
              "আত্মীয়দের সঙ্গে ধৈর্য রাখলে সুবিধা হয়।",
        "or": "ଚତୁର୍ଥ ଭାବରେ ବୃହସ୍ପତି ଘରୋଇ କଥାରେ କିଛି ଅସ୍ଥିରତା ଆଣିପାରନ୍ତି; ସମ୍ପର୍କୀୟଙ୍କ "
              "ସହ ଧୈର୍ଯ୍ୟ ରଖିଲେ ସୁବିଧା ହୁଏ।"},
    5: {"en": "Jupiter in your 5th favours learning, children's matters, creativity and good "
              "counsel.",
        "hi": "गुरु पाँचवें भाव में विद्या, संतान, रचनात्मकता और अच्छी सलाह के लिए शुभ हैं।",
        "bn": "পঞ্চম ভাবে বৃহস্পতি বিদ্যা, সন্তান, সৃজনশীলতা ও সৎ পরামর্শের পক্ষে শুভ।",
        "or": "ପଞ୍ଚମ ଭାବରେ ବୃହସ୍ପତି ବିଦ୍ୟା, ସନ୍ତାନ, ସୃଜନଶୀଳତା ଓ ଭଲ ପରାମର୍ଶ ପାଇଁ ଶୁଭ।"},
    6: {"en": "Jupiter in your 6th: steer clear of small disputes and overwork.",
        "hi": "गुरु छठे भाव में हैं — छोटे विवादों और काम के अधिक बोझ से बचें।",
        "bn": "ষষ্ঠ ভাবে বৃহস্পতি: ছোটখাটো বিবাদ ও অতিরিক্ত কাজের চাপ থেকে দূরে থাকুন।",
        "or": "ଷଷ୍ଠ ଭାବରେ ବୃହସ୍ପତି: ଛୋଟ ଛୋଟ ବିବାଦ ଓ ଅତିରିକ୍ତ କାମର ଚାପରୁ ଦୂରେଇ ରୁହନ୍ତୁ।"},
    7: {"en": "Jupiter in your 7th blesses partnerships, marriage talks and travel.",
        "hi": "गुरु सातवें भाव में साझेदारी, विवाह की बातचीत और यात्रा के लिए शुभ हैं।",
        "bn": "সপ্তম ভাবে বৃহস্পতি অংশীদারি, বিয়ের কথাবার্তা ও যাত্রায় আশীর্বাদ দেন।",
        "or": "ସପ୍ତମ ଭାବରେ ବୃହସ୍ପତି ଭାଗିଦାରୀ, ବିବାହ କଥାବାର୍ତ୍ତା ଓ ଯାତ୍ରାକୁ ଆଶୀର୍ବାଦ "
              "ଦିଅନ୍ତି।"},
    8: {"en": "Jupiter in your 8th suggests care with big decisions — go slow.",
        "hi": "गुरु आठवें भाव में हैं — बड़े निर्णयों में सावधानी रखें; धीरे चलें।",
        "bn": "অষ্টম ভাবে বৃহস্পতি বড় সিদ্ধান্তে সাবধানতার ইঙ্গিত দেন — ধীরে চলুন।",
        "or": "ଅଷ୍ଟମ ଭାବରେ ବୃହସ୍ପତି ବଡ଼ ନିଷ୍ପତ୍ତିରେ ସାବଧାନତାର ସଙ୍କେତ ଦିଅନ୍ତି — ଧୀରେ "
              "ଚାଲନ୍ତୁ।"},
    9: {"en": "Jupiter in your 9th is one of its best positions — fortune, dharma and guidance "
              "from teachers.",
        "hi": "गुरु नौवें भाव में हैं — सबसे शुभ स्थितियों में से एक: भाग्य, धर्म और गुरुजनों का "
              "मार्गदर्शन।",
        "bn": "নবম ভাবে বৃহস্পতি তাঁর সেরা অবস্থানগুলির একটিতে — ভাগ্য, ধর্ম ও গুরুজনের "
              "পথনির্দেশ।",
        "or": "ନବମ ଭାବରେ ବୃହସ୍ପତି ତାଙ୍କ ସର୍ବୋତ୍ତମ ସ୍ଥିତିମାନଙ୍କ ମଧ୍ୟରୁ ଗୋଟିଏରେ — ଭାଗ୍ୟ, "
              "ଧର୍ମ ଓ ଗୁରୁଜନଙ୍କ ମାର୍ଗଦର୍ଶନ।"},
    10: {"en": "Jupiter in your 10th may bring changes at work; stay adaptable.",
         "hi": "गुरु दसवें भाव में कार्यक्षेत्र में बदलाव ला सकते हैं; लचीले रहें।",
         "bn": "দশম ভাবে বৃহস্পতি কর্মক্ষেত্রে পরিবর্তন আনতে পারেন; মানিয়ে নেওয়ার মন "
               "রাখুন।",
         "or": "ଦଶମ ଭାବରେ ବୃହସ୍ପତି କର୍ମକ୍ଷେତ୍ରରେ ପରିବର୍ତ୍ତନ ଆଣିପାରନ୍ତି; ଖାପ ଖୁଆଇ "
               "ଚାଲନ୍ତୁ।"},
    11: {"en": "Jupiter in your 11th brings gains, fulfilled wishes and helpful friends.",
         "hi": "गुरु ग्यारहवें भाव में लाभ, इच्छापूर्ति और मित्रों का सहयोग देते हैं।",
         "bn": "একাদশ ভাবে বৃহস্পতি লাভ, ইচ্ছাপূরণ ও সহায়ক বন্ধু এনে দেন।",
         "or": "ଏକାଦଶ ଭାବରେ ବୃହସ୍ପତି ଲାଭ, ଇଚ୍ଛାପୂରଣ ଓ ସହାୟକ ବନ୍ଧୁ ଆଣନ୍ତି।"},
    12: {"en": "Jupiter in your 12th brings expenses, often on good causes; charity and spiritual "
               "practice are well placed.",
         "hi": "गुरु बारहवें भाव में खर्च कराते हैं, अक्सर अच्छे कामों पर; दान और आध्यात्मिक साधना "
               "शुभ है।",
         "bn": "দ্বাদশ ভাবে বৃহস্পতি খরচ বাড়ান, প্রায়ই ভালো কাজে; দান ও আধ্যাত্মিক "
               "সাধনার জন্য সময়টি অনুকূল।",
         "or": "ଦ୍ୱାଦଶ ଭାବରେ ବୃହସ୍ପତି ଖର୍ଚ୍ଚ କରାନ୍ତି, ଅନେକ ସମୟରେ ଭଲ କାମରେ; ଦାନ ଓ "
               "ଆଧ୍ୟାତ୍ମିକ ସାଧନା ପାଇଁ ସମୟଟି ଅନୁକୂଳ।"},
}

# Kannada
for _k, _v in {
    1: ("ನಿಮ್ಮ ಚಂದ್ರ ರಾಶಿಯ ಮೇಲೆ ಗುರು ಶಾಸ್ತ್ರೀಯವಾಗಿ ಅಸ್ಥಿರತೆಯ ಸ್ಥಾನ; ಯೋಜನೆಗಳನ್ನು ವಾಸ್ತವಿಕವಾಗಿಡಿ ಮತ್ತು"
        " ಶಕ್ತಿ ಮೀರಿ ಹೊಣೆ ಹೊರಬೇಡಿ."),
    2: "ನಿಮ್ಮ 2ನೇ ಮನೆಯಲ್ಲಿ ಗುರು ಕುಟುಂಬದ ಸಾಮರಸ್ಯ, ಉಳಿತಾಯ ಮತ್ತು ಸೌಮ್ಯ ಮಾತಿಗೆ ಬಲ ನೀಡುತ್ತಾನೆ.",
    3: "ನಿಮ್ಮ 3ನೇ ಮನೆಯಲ್ಲಿ ಗುರು ಅದೇ ಫಲಕ್ಕೆ ಸ್ವಲ್ಪ ಹೆಚ್ಚು ಶ್ರಮ ಬಯಸುತ್ತಾನೆ — ಪ್ರಯತ್ನ ಮುಂದುವರಿಸಿ.",
    4: ("ನಿಮ್ಮ 4ನೇ ಮನೆಯಲ್ಲಿ ಗುರು ಮನೆಯ ವಿಷಯಗಳಲ್ಲಿ ಅಸ್ಥಿರತೆ ತರಬಹುದು; ಸಂಬಂಧಿಕರೊಂದಿಗೆ ತಾಳ್ಮೆ "
        "ನೆರವಾಗುತ್ತದೆ."),
    5: "ನಿಮ್ಮ 5ನೇ ಮನೆಯಲ್ಲಿ ಗುರು ವಿದ್ಯೆ, ಮಕ್ಕಳ ವಿಷಯಗಳು, ಸೃಜನಶೀಲತೆ ಮತ್ತು ಒಳ್ಳೆಯ ಸಲಹೆಗೆ ಅನುಕೂಲ.",
    6: "ನಿಮ್ಮ 6ನೇ ಮನೆಯಲ್ಲಿ ಗುರು: ಸಣ್ಣ ವಿವಾದಗಳು ಮತ್ತು ಅತಿಯಾದ ಕೆಲಸದಿಂದ ದೂರವಿರಿ.",
    7: "ನಿಮ್ಮ 7ನೇ ಮನೆಯಲ್ಲಿ ಗುರು ಸಹಭಾಗಿತ್ವ, ವಿವಾಹದ ಮಾತುಕತೆ ಮತ್ತು ಪ್ರಯಾಣಕ್ಕೆ ಶುಭ.",
    8: ("ನಿಮ್ಮ 8ನೇ ಮನೆಯಲ್ಲಿ ಗುರು ದೊಡ್ಡ ನಿರ್ಧಾರಗಳಲ್ಲಿ ಎಚ್ಚರಿಕೆಯನ್ನು ಸೂಚಿಸುತ್ತಾನೆ — ನಿಧಾನವಾಗಿ "
        "ಮುಂದುವರಿಯಿರಿ."),
    9: ("ನಿಮ್ಮ 9ನೇ ಮನೆಯಲ್ಲಿ ಗುರು — ಗುರುವಿನ ಅತ್ಯುತ್ತಮ ಸ್ಥಾನಗಳಲ್ಲಿ ಒಂದು: ಭಾಗ್ಯ, ಧರ್ಮ ಮತ್ತು ಗುರುಜನರ "
        "ಮಾರ್ಗದರ್ಶನ."),
    10: "ನಿಮ್ಮ 10ನೇ ಮನೆಯಲ್ಲಿ ಗುರು ಕೆಲಸದಲ್ಲಿ ಬದಲಾವಣೆಗಳನ್ನು ತರಬಹುದು; ಹೊಂದಿಕೊಳ್ಳುವ ಮನೋಭಾವ ಇಟ್ಟುಕೊಳ್ಳಿ.",
    11: "ನಿಮ್ಮ 11ನೇ ಮನೆಯಲ್ಲಿ ಗುರು ಲಾಭ, ಇಷ್ಟಾರ್ಥ ಸಿದ್ಧಿ ಮತ್ತು ಸಹಾಯ ಮಾಡುವ ಸ್ನೇಹಿತರನ್ನು ತರುತ್ತಾನೆ.",
    12: ("ನಿಮ್ಮ 12ನೇ ಮನೆಯಲ್ಲಿ ಗುರು ಖರ್ಚು ತರುತ್ತಾನೆ, ಹೆಚ್ಚಾಗಿ ಒಳ್ಳೆಯ ಕಾರ್ಯಗಳಿಗೆ; ದಾನ ಮತ್ತು ಆಧ್ಯಾತ್ಮಿಕ"
         " ಸಾಧನೆಗೆ ಇದು ಸೂಕ್ತ."),
}.items():
    JUPITER_HOUSE[_k]["kn"] = _v

# Telugu
for _k, _v in {
    1: ("మీ చంద్ర రాశిపై గురువు శాస్త్రరీత్యా అస్థిరతను సూచించే స్థానం; ప్రణాళికలను వాస్తవికంగా "
        "ఉంచండి, శక్తికి మించి బాధ్యతలు తీసుకోకండి."),
    2: "మీ 2వ స్థానంలో గురువు కుటుంబ సామరస్యానికి, పొదుపుకు, మృదువైన మాటకు బలమిస్తాడు.",
    3: "మీ 3వ స్థానంలో గురువు అదే ఫలితానికి కొంచెం ఎక్కువ శ్రమను కోరుతాడు — పట్టు వదలకండి.",
    4: "మీ 4వ స్థానంలో గురువు ఇంటి విషయాల్లో అస్థిరత తేవచ్చు; బంధువులతో ఓర్పు సహాయపడుతుంది.",
    5: "మీ 5వ స్థానంలో గురువు విద్య, సంతాన విషయాలు, సృజనాత్మకత, మంచి సలహాలకు అనుకూలం.",
    6: "మీ 6వ స్థానంలో గురువు: చిన్న వివాదాలకు, అధిక పనిభారానికి దూరంగా ఉండండి.",
    7: "మీ 7వ స్థానంలో గురువు భాగస్వామ్యాలకు, వివాహ సంప్రదింపులకు, ప్రయాణాలకు శుభప్రదం.",
    8: "మీ 8వ స్థానంలో గురువు పెద్ద నిర్ణయాల్లో జాగ్రత్తను సూచిస్తాడు — నెమ్మదిగా ముందుకు వెళ్లండి.",
    9: ("మీ 9వ స్థానంలో గురువు — గురువుకు ఉత్తమ స్థానాల్లో ఒకటి: భాగ్యం, ధర్మం, ఆచార్యుల "
        "మార్గదర్శనం."),
    10: "మీ 10వ స్థానంలో గురువు ఉద్యోగంలో మార్పులు తేవచ్చు; పరిస్థితులకు అనుగుణంగా మారండి.",
    11: "మీ 11వ స్థానంలో గురువు లాభాలు, కోరికల నెరవేర్పు, సహాయపడే స్నేహితులను ఇస్తాడు.",
    12: ("మీ 12వ స్థానంలో గురువు ఖర్చులు తెస్తాడు, తరచుగా మంచి పనుల కోసం; దానం, ఆధ్యాత్మిక సాధనకు "
         "ఇది అనుకూలం."),
}.items():
    JUPITER_HOUSE[_k]["te"] = _v

RAHU_HOUSE: dict[int, dict[str, str]] = {
    1: {"en": "Rahu over your Moon sign can stir restlessness and unusual wants; stay grounded.",
        "hi": "राहु आपकी चंद्र राशि पर बेचैनी और असामान्य इच्छाएँ जगा सकते हैं; ज़मीन से जुड़े रहें।",
        "bn": "আপনার চন্দ্র রাশির ওপর রাহু অস্থিরতা ও অস্বাভাবিক কামনা জাগাতে পারেন; "
              "মাটিতে পা রেখে চলুন।",
        "or": "ଆପଣଙ୍କ ଚନ୍ଦ୍ର ରାଶି ଉପରେ ରାହୁ ଅସ୍ଥିରତା ଓ ଅସାଧାରଣ ଇଚ୍ଛା ଜଗାଇପାରନ୍ତି; "
              "ମାଟିରେ ପାଦ ରଖି ଚାଲନ୍ତୁ।"},
    2: {"en": "Rahu in your 2nd: take care with speech and money talk within the family.",
        "hi": "राहु दूसरे भाव में हैं — परिवार में धन और वाणी के मामलों में सावधानी रखें।",
        "bn": "দ্বিতীয় ভাবে রাহু: পরিবারে কথাবার্তা ও টাকাপয়সার আলোচনায় সাবধান "
              "থাকুন।",
        "or": "ଦ୍ୱିତୀୟ ଭାବରେ ରାହୁ: ପରିବାରରେ କଥାବାର୍ତ୍ତା ଓ ଟଙ୍କାପଇସା ଆଲୋଚନାରେ ସାବଧାନ "
              "ରୁହନ୍ତୁ।"},
    3: {"en": "Rahu in your 3rd is favourable — bold initiatives and communication succeed.",
        "hi": "राहु तीसरे भाव में शुभ हैं — साहसिक पहल और संवाद सफल होते हैं।",
        "bn": "তৃতীয় ভাবে রাহু শুভ — সাহসী উদ্যোগ ও যোগাযোগে সাফল্য আসে।",
        "or": "ତୃତୀୟ ଭାବରେ ରାହୁ ଶୁଭ — ସାହସିକ ପଦକ୍ଷେପ ଓ ଯୋଗାଯୋଗରେ ସଫଳତା ମିଳେ।"},
    4: {"en": "Rahu in your 4th can unsettle domestic peace; avoid hasty property moves.",
        "hi": "राहु चौथे भाव में घरेलू शांति को हिला सकते हैं; संपत्ति संबंधी जल्दबाज़ी से बचें।",
        "bn": "চতুর্থ ভাবে রাহু ঘরের শান্তি কিছুটা নাড়িয়ে দিতে পারেন; সম্পত্তি নিয়ে "
              "তাড়াহুড়ো করবেন না।",
        "or": "ଚତୁର୍ଥ ଭାବରେ ରାହୁ ଘରର ଶାନ୍ତିକୁ କିଛିଟା ବିଚଳିତ କରିପାରନ୍ତି; ସମ୍ପତ୍ତି ବିଷୟରେ "
              "ତରବର କରନ୍ତୁ ନାହିଁ।"},
    5: {"en": "Rahu in your 5th: double-check risky ideas and keep a clear head.",
        "hi": "राहु पाँचवें भाव में हैं — जोखिम भरे विचारों को दोबारा जाँचें; मन स्पष्ट रखें।",
        "bn": "পঞ্চম ভাবে রাহু: ঝুঁকিপূর্ণ ভাবনা আরেকবার যাচাই করুন এবং মাথা ঠান্ডা "
              "রাখুন।",
        "or": "ପଞ୍ଚମ ଭାବରେ ରାହୁ: ଝୁଙ୍କିପୂର୍ଣ୍ଣ ଚିନ୍ତାଧାରାକୁ ପୁଣି ଥରେ ଯାଞ୍ଚ କରନ୍ତୁ ଓ ମନ "
              "ସ୍ଥିର ରଖନ୍ତୁ।"},
    6: {"en": "Rahu in your 6th helps you get past competition and obstacles.",
        "hi": "राहु छठे भाव में प्रतियोगिता और बाधाओं पर विजय दिलाते हैं।",
        "bn": "ষষ্ঠ ভাবে রাহু প্রতিযোগিতা ও বাধা পেরোতে সাহায্য করেন।",
        "or": "ଷଷ୍ଠ ଭାବରେ ରାହୁ ପ୍ରତିଯୋଗିତା ଓ ବାଧା ଅତିକ୍ରମ କରିବାରେ ସାହାଯ୍ୟ କରନ୍ତି।"},
    7: {"en": "Rahu in your 7th: keep partnerships transparent.",
        "hi": "राहु सातवें भाव में हैं — साझेदारी में पारदर्शिता रखें।",
        "bn": "সপ্তম ভাবে রাহু: অংশীদারিতে স্বচ্ছতা বজায় রাখুন।",
        "or": "ସପ୍ତମ ଭାବରେ ରାହୁ: ଭାଗିଦାରୀରେ ସ୍ୱଚ୍ଛତା ରଖନ୍ତୁ।"},
    8: {"en": "Rahu in your 8th: avoid risky shortcuts and stay calm when the unexpected comes.",
        "hi": "राहु आठवें भाव में हैं — जोखिम भरे शॉर्टकट से बचें; अनपेक्षित स्थितियों में शांत रहें।",
        "bn": "অষ্টম ভাবে রাহু: ঝুঁকির সহজ পথ এড়িয়ে চলুন এবং অপ্রত্যাশিত কিছু ঘটলে "
              "শান্ত থাকুন।",
        "or": "ଅଷ୍ଟମ ଭାବରେ ରାହୁ: ଝୁଙ୍କିପୂର୍ଣ୍ଣ ସହଜ ବାଟରୁ ଦୂରେଇ ରୁହନ୍ତୁ ଓ ଅପ୍ରତ୍ୟାଶିତ "
              "କିଛି ଘଟିଲେ ଶାନ୍ତ ରୁହନ୍ତୁ।"},
    9: {"en": "Rahu in your 9th can raise doubts about beliefs or mentors; seek advice you trust.",
        "hi": "राहु नौवें भाव में आस्था या मार्गदर्शकों को लेकर संदेह ला सकते हैं; भरोसेमंद सलाह लें।",
        "bn": "নবম ভাবে রাহু বিশ্বাস বা পথপ্রদর্শকদের নিয়ে সংশয় জাগাতে পারেন; ভরসার "
              "মানুষের পরামর্শ নিন।",
        "or": "ନବମ ଭାବରେ ରାହୁ ବିଶ୍ୱାସ ବା ମାର୍ଗଦର୍ଶକଙ୍କ ବିଷୟରେ ସନ୍ଦେହ ଜଗାଇପାରନ୍ତି; "
              "ଭରସାଯୋଗ୍ୟ ଲୋକଙ୍କ ପରାମର୍ଶ ନିଅନ୍ତୁ।"},
    10: {"en": "Rahu in your 10th brings ambition and sudden openings at work; move with "
               "integrity.",
         "hi": "राहु दसवें भाव में महत्वाकांक्षा और कार्यक्षेत्र में अचानक अवसर लाते हैं; ईमानदारी से "
               "आगे बढ़ें।",
         "bn": "দশম ভাবে রাহু উচ্চাকাঙ্ক্ষা ও কর্মক্ষেত্রে হঠাৎ সুযোগ আনেন; সততার সঙ্গে "
               "এগোন।",
         "or": "ଦଶମ ଭାବରେ ରାହୁ ଉଚ୍ଚାକାଂକ୍ଷା ଓ କର୍ମକ୍ଷେତ୍ରରେ ହଠାତ୍ ସୁଯୋଗ ଆଣନ୍ତି; "
               "ସଚ୍ଚୋଟତାର ସହ ଆଗକୁ ବଢ଼ନ୍ତୁ।"},
    11: {"en": "Rahu in your 11th — gains through networks and new contacts.",
         "hi": "राहु ग्यारहवें भाव में हैं — नए संपर्कों और नेटवर्क से लाभ।",
         "bn": "একাদশ ভাবে রাহু — পরিচিতি ও নতুন যোগাযোগের মাধ্যমে লাভ।",
         "or": "ଏକାଦଶ ଭାବରେ ରାହୁ — ପରିଚିତି ଓ ନୂଆ ଯୋଗାଯୋଗ ମାଧ୍ୟମରେ ଲାଭ।"},
    12: {"en": "Rahu in your 12th: watch hidden expenses and get proper rest.",
         "hi": "राहु बारहवें भाव में हैं — छिपे खर्चों पर नज़र रखें और पूरा विश्राम लें।",
         "bn": "দ্বাদশ ভাবে রাহু: লুকোনো খরচের দিকে নজর রাখুন এবং ঠিকমতো বিশ্রাম নিন।",
         "or": "ଦ୍ୱାଦଶ ଭାବରେ ରାହୁ: ଲୁଚି ରହିଥିବା ଖର୍ଚ୍ଚ ଉପରେ ନଜର ରଖନ୍ତୁ ଓ ଠିକ୍ ଭାବରେ "
               "ବିଶ୍ରାମ ନିଅନ୍ତୁ।"},
}

# Kannada
for _k, _v in {
    1: "ನಿಮ್ಮ ಚಂದ್ರ ರಾಶಿಯ ಮೇಲೆ ರಾಹು ಚಡಪಡಿಕೆ ಮತ್ತು ಅಸಾಮಾನ್ಯ ಆಸೆಗಳನ್ನು ಕೆರಳಿಸಬಹುದು; ಸ್ಥಿಮಿತದಿಂದಿರಿ.",
    2: "ನಿಮ್ಮ 2ನೇ ಮನೆಯಲ್ಲಿ ರಾಹು: ಕುಟುಂಬದಲ್ಲಿ ಮಾತು ಮತ್ತು ಹಣದ ಚರ್ಚೆಗಳಲ್ಲಿ ಎಚ್ಚರಿಕೆ ವಹಿಸಿ.",
    3: "ನಿಮ್ಮ 3ನೇ ಮನೆಯಲ್ಲಿ ರಾಹು ಶುಭ — ಧೈರ್ಯದ ಉಪಕ್ರಮಗಳು ಮತ್ತು ಸಂವಹನ ಯಶಸ್ವಿಯಾಗುತ್ತವೆ.",
    4: "ನಿಮ್ಮ 4ನೇ ಮನೆಯಲ್ಲಿ ರಾಹು ಮನೆಯ ಶಾಂತಿಯನ್ನು ಕದಡಬಹುದು; ಆಸ್ತಿ ವಿಷಯಗಳಲ್ಲಿ ಆತುರದ ಹೆಜ್ಜೆ ಇಡಬೇಡಿ.",
    5: ("ನಿಮ್ಮ 5ನೇ ಮನೆಯಲ್ಲಿ ರಾಹು: ಅಪಾಯದ ಯೋಚನೆಗಳನ್ನು ಮತ್ತೊಮ್ಮೆ ಪರಿಶೀಲಿಸಿ ಮತ್ತು ಮನಸ್ಸನ್ನು "
        "ಸ್ಪಷ್ಟವಾಗಿಡಿ."),
    6: "ನಿಮ್ಮ 6ನೇ ಮನೆಯಲ್ಲಿ ರಾಹು ಸ್ಪರ್ಧೆ ಮತ್ತು ಅಡೆತಡೆಗಳನ್ನು ದಾಟಲು ನೆರವಾಗುತ್ತಾನೆ.",
    7: "ನಿಮ್ಮ 7ನೇ ಮನೆಯಲ್ಲಿ ರಾಹು: ಸಹಭಾಗಿತ್ವಗಳಲ್ಲಿ ಪಾರದರ್ಶಕತೆ ಇರಲಿ.",
    8: ("ನಿಮ್ಮ 8ನೇ ಮನೆಯಲ್ಲಿ ರಾಹು: ಅಪಾಯದ ಅಡ್ಡದಾರಿಗಳನ್ನು ತಪ್ಪಿಸಿ ಮತ್ತು ಅನಿರೀಕ್ಷಿತ ಸಂದರ್ಭಗಳಲ್ಲಿ "
        "ಶಾಂತವಾಗಿರಿ."),
    9: ("ನಿಮ್ಮ 9ನೇ ಮನೆಯಲ್ಲಿ ರಾಹು ನಂಬಿಕೆಗಳು ಅಥವಾ ಮಾರ್ಗದರ್ಶಕರ ಬಗ್ಗೆ ಸಂದೇಹ ಮೂಡಿಸಬಹುದು; ನೀವು ನಂಬುವವರ "
        "ಸಲಹೆ ಪಡೆಯಿರಿ."),
    10: ("ನಿಮ್ಮ 10ನೇ ಮನೆಯಲ್ಲಿ ರಾಹು ಮಹತ್ವಾಕಾಂಕ್ಷೆ ಮತ್ತು ಕೆಲಸದಲ್ಲಿ ಅನಿರೀಕ್ಷಿತ ಅವಕಾಶಗಳನ್ನು ತರುತ್ತಾನೆ; "
         "ಪ್ರಾಮಾಣಿಕತೆಯಿಂದ ಮುನ್ನಡೆಯಿರಿ."),
    11: "ನಿಮ್ಮ 11ನೇ ಮನೆಯಲ್ಲಿ ರಾಹು — ಸಂಪರ್ಕ ಜಾಲ ಮತ್ತು ಹೊಸ ಪರಿಚಯಗಳ ಮೂಲಕ ಲಾಭ.",
    12: "ನಿಮ್ಮ 12ನೇ ಮನೆಯಲ್ಲಿ ರಾಹು: ಕಾಣದ ಖರ್ಚುಗಳ ಮೇಲೆ ಗಮನವಿಡಿ ಮತ್ತು ಸರಿಯಾಗಿ ವಿಶ್ರಾಂತಿ ಪಡೆಯಿರಿ.",
}.items():
    RAHU_HOUSE[_k]["kn"] = _v

# Telugu
for _k, _v in {
    1: "మీ చంద్ర రాశిపై రాహువు అశాంతిని, అసాధారణ కోరికలను రేకెత్తించవచ్చు; నిలకడగా ఉండండి.",
    2: "మీ 2వ స్థానంలో రాహువు: కుటుంబంలో మాటల్లో, డబ్బుకు సంబంధించిన చర్చల్లో జాగ్రత్త వహించండి.",
    3: "మీ 3వ స్థానంలో రాహువు శుభప్రదం — సాహసోపేత ప్రయత్నాలు, సంభాషణలు విజయవంతమవుతాయి.",
    4: ("మీ 4వ స్థానంలో రాహువు ఇంటి ప్రశాంతతను కదిలించవచ్చు; ఆస్తి విషయాల్లో తొందరపాటు నిర్ణయాలు "
        "వద్దు."),
    5: ("మీ 5వ స్థానంలో రాహువు: ప్రమాదకరమైన ఆలోచనలను మరోసారి పరిశీలించండి, మనసును స్పష్టంగా "
        "ఉంచుకోండి."),
    6: "మీ 6వ స్థానంలో రాహువు పోటీని, ఆటంకాలను అధిగమించడానికి సహాయపడతాడు.",
    7: "మీ 7వ స్థానంలో రాహువు: భాగస్వామ్యాల్లో పారదర్శకత పాటించండి.",
    8: ("మీ 8వ స్థానంలో రాహువు: ప్రమాదకరమైన అడ్డదారులను నివారించండి, అనుకోనిది ఎదురైనప్పుడు "
        "ప్రశాంతంగా ఉండండి."),
    9: ("మీ 9వ స్థానంలో రాహువు నమ్మకాలపై లేదా మార్గదర్శకులపై సందేహాలు కలిగించవచ్చు; మీరు నమ్మే వారి "
        "సలహా తీసుకోండి."),
    10: ("మీ 10వ స్థానంలో రాహువు ఆశయాన్ని, ఉద్యోగంలో అనుకోని అవకాశాలను తెస్తాడు; నిజాయితీతో ముందుకు "
         "సాగండి."),
    11: "మీ 11వ స్థానంలో రాహువు — పరిచయాల ద్వారా, కొత్త సంబంధాల ద్వారా లాభం.",
    12: "మీ 12వ స్థానంలో రాహువు: కనిపించని ఖర్చులపై కన్నేసి ఉంచండి, తగినంత విశ్రాంతి తీసుకోండి.",
}.items():
    RAHU_HOUSE[_k]["te"] = _v

KETU_LINE = {
    True: {"en": "Ketu in your {n} house works quietly in your favour — obstacles clear with "
                 "less fuss.",
           "hi": "केतु {n} भाव में अनुकूल हैं — बाधाएँ कम झंझट में दूर होती हैं।",
           "bn": "{n} ভাবে কেতু নিঃশব্দে আপনার অনুকূলে কাজ করেন — বাধা কম ঝামেলায় দূর "
                 "হয়।",
           "or": "{n} ଭାବରେ କେତୁ ନୀରବରେ ଆପଣଙ୍କ ସପକ୍ଷରେ କାମ କରନ୍ତି — ବାଧା କମ୍ ଝାମେଲାରେ ଦୂର "
                 "ହୁଏ।"},
    False: {"en": "Ketu in your {n} house is a quieter, inward influence — good for reflection "
                  "and spiritual practice, less so for impulsive moves.",
            "hi": "केतु {n} भाव में हैं — अंतर्मुखी प्रभाव; आत्मचिंतन और साधना के लिए अच्छा, "
                  "जल्दबाज़ी के कदमों के लिए कम।",
            "bn": "{n} ভাবে কেতু শান্ত, অন্তর্মুখী প্রভাব দেন — আত্মচিন্তা ও আধ্যাত্মিক "
                  "সাধনার পক্ষে ভালো, হঠাৎ নেওয়া পদক্ষেপের পক্ষে নয়।",
            "or": "{n} ଭାବରେ କେତୁ ଏକ ଶାନ୍ତ, ଅନ୍ତର୍ମୁଖୀ ପ୍ରଭାବ ଦିଅନ୍ତି — ଆତ୍ମଚିନ୍ତନ ଓ "
                  "ଆଧ୍ୟାତ୍ମିକ ସାଧନା ପାଇଁ ଭଲ, ହଠାତ୍ ନିଆଯାଇଥିବା ପଦକ୍ଷେପ ପାଇଁ କମ୍।"},
}

# Kannada
for _k, _v in {
    True: ("ನಿಮ್ಮ {n} ಮನೆಯಲ್ಲಿ ಕೇತು ಸದ್ದಿಲ್ಲದೆ ನಿಮ್ಮ ಪರವಾಗಿ ಕೆಲಸ ಮಾಡುತ್ತಾನೆ — ಅಡೆತಡೆಗಳು ಹೆಚ್ಚು "
           "ಗೊಂದಲವಿಲ್ಲದೆ ನಿವಾರಣೆಯಾಗುತ್ತವೆ."),
    False: ("ನಿಮ್ಮ {n} ಮನೆಯಲ್ಲಿ ಕೇತು ಶಾಂತ, ಅಂತರ್ಮುಖಿ ಪ್ರಭಾವ — ಆತ್ಮಚಿಂತನೆ ಮತ್ತು ಆಧ್ಯಾತ್ಮಿಕ ಸಾಧನೆಗೆ "
            "ಒಳ್ಳೆಯದು, ಆವೇಗದ ನಿರ್ಧಾರಗಳಿಗೆ ಅಷ್ಟಾಗಿ ಅಲ್ಲ."),
}.items():
    KETU_LINE[_k]["kn"] = _v

# Telugu
for _k, _v in {
    True: ("మీ {n} స్థానంలో కేతువు నిశ్శబ్దంగా మీకు అనుకూలంగా పనిచేస్తాడు — ఆటంకాలు పెద్ద హడావుడి "
           "లేకుండా తొలగిపోతాయి."),
    False: ("మీ {n} స్థానంలో కేతువు ప్రశాంతమైన, అంతర్ముఖ ప్రభావం — ఆత్మపరిశీలనకు, ఆధ్యాత్మిక సాధనకు "
            "మంచిది, ఆవేశపూరిత నిర్ణయాలకు అంతగా కాదు."),
}.items():
    KETU_LINE[_k]["te"] = _v


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
