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
           "hi": "केतु {n} भाव में अनुकूल हैं — बाधाएँ कम झंझट में दूर होती हैं।"},
    False: {"en": "Ketu in your {n} house is a quieter, inward influence — good for reflection "
                  "and spiritual practice, less so for impulsive moves.",
            "hi": "केतु {n} भाव में हैं — अंतर्मुखी प्रभाव; आत्मचिंतन और साधना के लिए अच्छा, "
                  "जल्दबाज़ी के कदमों के लिए कम।"},
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
