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
