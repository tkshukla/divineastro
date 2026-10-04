"""The text of the vrat & tyohar pages (vrat_pages.py), per language.

TRANSLATORS: this file is data. To translate /vrat-tyohar, /vrat-tyohar/<year
or city>, /ekadashi-<year> and /tyohar/<festival>-<year> into, say, Kannada:

* add a "kn" dict to TEXT with any subset of the "en" keys;
* add "kn" entries to ABOUT (what each festival is) and NOTES (where
  traditions differ), keyed by the festival slug;
* then add "kn" to vrat_pages.TRANSLATED.

A key you leave out falls back to TEXT["_native"] (if it has one) and then to
English. Templates keep their `{placeholders}`; the word order is yours.
Values marked HTML are inserted as they are (keep the tags, write `&amp;` for
"&"); every other value is plain text and escaped by the code. As in
seo_text.py, {t_<timing>} and {l_<limb>} are available in every template.

NOT here, because every language already has them in app/astro/names_<code>.py:
festival and Ekadashi names (FESTIVALS / EKADASHI), puja-timing labels
(FESTIVAL_TIMINGS), tithi and paksha names, weekdays and months. The festival
rules ("rule_en"/"rule_hi") come from app/astro/festivals.py.
"""

from __future__ import annotations

TEXT: dict[str, dict[str, str]] = {
    "en": {
        # -- shared pieces --------------------------------------------------
        "crumb": "Vrat & festivals",
        # "8 Nov, Sunday": {date} {weekday}
        "day_label": "{date}, {weekday}",
        # one timing (plain text): {label} {prefix} (the other day's date + ", " or "") {value}
        "timing": "{label}: {prefix}{value}",
        # the tithi line: {paksha} {name} {start} {end}
        "tithi.text": "{paksha} {name}: {start} to {end}",
        "tithi.paksha": "{paksha}",
        # list tables (HTML): {city}
        "table.th": "<tr><th>Date</th><th>Vrat / festival</th><th>Timing ({city})</th></tr>",
        # HTML. {city}
        "city_note": ('<div class="box"><p><strong>Timings vary by city.</strong> Every time here is '
                      "for {city}'s sunrise, sunset and moonrise; in another city they shift by a few "
                      "minutes and occasionally the date does too. Dates follow Drik Panchang's Smarta "
                      "(default) reckoning. Check the Panchang for your own city.</p></div>"),
        "top_note": ('<p class="note"><small>For most observances the date is the same across India, but '
                     "puja muhurat, parana and moonrise times differ from city to city - every time here is "
                     "for <strong>{city}</strong>. Regional traditions may vary.</small></p>"),
        "cities.heading": "Vrat & festivals in your city",
        # plain text: {city}
        "tools.panchang": "Today's Panchang in {city}",
        "tools.rahu": "Rahu Kaal in {city}",
        "tools.heading": "More for {city}",
        "cta": "See the Panchang for your city — free",
        "more.today": "Today's vrat & festivals",
        "more.year": "Festival calendar {year}",
        "more.ekadashi": "Ekadashi {year}",
        "more.panchang": "Today's Panchang",
        "more.rashifal": "Today's Rashifal",
        "more.heading": "More",
        "majors.heading": "Major festivals {year}",
        # the box on a day with observances / without: {name} (HTML link) {day}
        "today.rule": "Rule",
        "today.none": "No major vrat or festival today.",
        "today.next": " Next: <strong>{name}</strong> on {day}.",
        # the /panchang pages' block (HTML)
        "block.heading": "Vrat &amp; Festivals today",
        "nf.h1": "Page not found",

        # -- /vrat-tyohar[/<city>] ------------------------------------------
        # {date} (short) {city}
        "hub.title_default": "Aaj Ke Vrat aur Tyohar: Today's Vrat & Festivals ({date})",
        "hub.title_city": "Today's Vrat & Festivals in {city} ({date}) - Aaj Ke Vrat",
        "hub.h1_default": "Today's vrat & festivals",
        "hub.h1_city": "Today's vrat & festivals in {city}",
        # {date} (long) {names}
        "hub.desc_today": "Today, {date}: {names}. ",
        "hub.desc_none": "{date}: no major vrat today. ",
        "hub.desc_rest": ("Upcoming fasts and festivals for 30 days with Ekadashi parana, Pradosh "
                          "and Sankashti moonrise times - {city}."),
        "hub.sub": '<p class="hi" lang="hi">आज के व्रत और त्योहार</p>',
        "hub.upcoming": "Next 30 days",

        # -- /vrat-tyohar/<year> --------------------------------------------
        "year.title": "Hindu Festival & Vrat Calendar {year} (New Delhi): Dates and Muhurat",
        "year.h1": "Vrat & festival calendar {year}",
        "year.desc": ("Every Hindu vrat and festival of {year}, month by month - Ekadashi, "
                      "Pradosh, Sankashti, Purnima, Amavasya, Shivratri and festivals like Diwali, "
                      "Navratri and Raksha Bandhan, with puja muhurat for New Delhi."),
        # HTML. {count} {year}
        "year.intro": ("<p><strong>{count}</strong> fasts and festivals in {year} for New Delhi, "
                       "computed from the panchang. Tap a major festival for its puja muhurat and "
                       "what it is about.</p>"),
        "year.month": "{month} {year}",
        "year.itemlist": "Major Hindu festivals {year}",

        # -- /ekadashi-<year> -----------------------------------------------
        "ek.title": "Ekadashi {year}: All Ekadashi Vrat Dates and Parana Time (New Delhi)",
        "ek.h1": "Ekadashi {year}: dates and parana time",
        "ek.desc": ("All {count} Ekadashis of {year} - fasting date, Ekadashi tithi times "
                    "and the parana (fast-breaking) window next day, for New Delhi."),
        "ek.th": "<tr><th>Ekadashi</th><th>Fast</th><th>Parana</th></tr>",
        "ek.rule": ("<p><strong>Rule (Smarta):</strong> fast on the day Ekadashi prevails at sunrise; "
                    "if it prevails at two sunrises, the second day, and if at none, the day it falls "
                    "in. Parana is the next day after sunrise, once Hari Vasara (the first quarter of "
                    "Dwadashi) is over, within Pratahkala and before Dwadashi ends; if Hari Vasara runs "
                    "past Pratahkala, parana moves to Aparahna (Madhyahna is avoided).</p>"),
        "ek.sub": '<p class="hi" lang="hi">एकादशी {year}</p>',
        "ek.crumb": "Ekadashi {year}",

        # -- /tyohar/<festival>-<year> --------------------------------------
        # {name} {year} {short} (short date) {date} (long date) {weekday} {main}
        "fest.title": "{name} {year}: Date and Puja Muhurat - {short}",
        "fest.h1": "{name} {year}: date and muhurat",
        "fest.main": "{text}. ",
        "fest.desc": "{name} {year} is on {weekday}, {date}. {main}Puja timings for New Delhi.",
        # HTML. {name} {year} {when}
        "fest.when": "{name} {year} is on <strong>{when}</strong>.",
        "fest.sub": '<p class="hi" lang="hi">{name_hi} {year}</p>',
        "fest.about_h2": "What it is and how it is observed",
        "fest.rule_h2": "How the date is fixed",
        "fest.faq_h2": "Frequently asked questions",
        "event.place": "India",
        # FAQ (plain text): {name} {year} {weekday} {date} {short} {timings} {rule} {when}
        "faq.when_q": "When is {name} {year}?",
        "faq.when_a": "{name} {year} is on {weekday}, {date}.",
        "faq.muhurat_q": "What is the {name} {year} puja muhurat?",
        "faq.timings_q": "What are the {name} {year} timings?",
        "faq.timings_a": ("For New Delhi - {timings}. Timings vary by city by a few minutes; "
                          "check the Panchang for your city."),
        "faq.why_q": "Why is {name} {year} observed on {short}?",
        "faq.why_a": "The date follows the rule: {rule}. In {year} that is {when} (New Delhi).",
    },

    "hi": {
        "crumb": "व्रत और त्योहार",
        "tithi.text": "{paksha} {name}: {start} से {end} तक",
        "tithi.paksha": "{paksha} पक्ष",
        "table.th": "<tr><th>दिनांक</th><th>व्रत / त्योहार</th><th>समय ({city})</th></tr>",
        "city_note": ('<div class="box"><p><strong>समय शहर के अनुसार बदलते हैं।</strong> यहां दिए सभी '
                      "समय {city} के सूर्योदय-सूर्यास्त और चंद्रोदय पर आधारित हैं; दूसरे शहर में कुछ "
                      "मिनट और कभी-कभी तिथि भी बदल सकती है। तिथियां द्रिक पंचांग की स्मार्त (सामान्य) "
                      "गणना से मेल खाती हैं। अपने शहर के लिए पंचांग देखें।</p></div>"),
        "top_note": ('<p class="note"><small>अधिकांश व्रत-त्योहारों की तिथि पूरे भारत में एक ही होती है, '
                     "पर पूजा मुहूर्त, पारण और चंद्रोदय का समय शहर के अनुसार बदलता है - यहां सभी समय "
                     "<strong>{city}</strong> के हैं। क्षेत्रीय परंपराएं भिन्न हो सकती हैं।</small></p>"),
        "cities.heading": "अपने शहर के व्रत-त्योहार",
        "tools.panchang": "{city} का आज का पंचांग",
        "tools.rahu": "{city} का राहु काल",
        "tools.heading": "{city} के लिए और",
        "cta": "अपने शहर का पंचांग देखें — मुफ़्त",
        "more.today": "आज के व्रत और त्योहार",
        "more.year": "व्रत-त्योहार {year}",
        "more.ekadashi": "एकादशी {year}",
        "more.panchang": "आज का पंचांग",
        "more.rashifal": "आज का राशिफल",
        "more.heading": "और देखें",
        "majors.heading": "{year} के प्रमुख त्योहार",
        "today.rule": "नियम",
        "today.none": "आज कोई प्रमुख व्रत या त्योहार नहीं है।",
        "today.next": " अगला: <strong>{name}</strong>, {day}।",
        "block.heading": "आज के व्रत-त्योहार",
        "nf.h1": "पृष्ठ नहीं मिला",

        "hub.title_default": "आज के व्रत और त्योहार ({date}) - मुहूर्त सहित",
        "hub.title_city": "{city} में आज के व्रत और त्योहार ({date}) - मुहूर्त सहित",
        "hub.h1_default": "आज के व्रत और त्योहार",
        "hub.h1_city": "{city} में आज के व्रत और त्योहार",
        "hub.desc_today": "आज {date}: {names}। ",
        "hub.desc_none": "{date}: आज कोई प्रमुख व्रत नहीं। ",
        "hub.desc_rest": "अगले 30 दिनों के व्रत-त्योहार, एकादशी पारण, प्रदोष, संकष्टी चंद्रोदय समय - {city}।",
        "hub.sub": '<p class="hi" lang="en">Today\'s vrat &amp; festivals</p>',
        "hub.upcoming": "अगले 30 दिन",

        "year.title": "व्रत-त्योहार {year}: पूरी सूची, तिथि और मुहूर्त (नई दिल्ली)",
        "year.h1": "व्रत और त्योहार {year}",
        "year.desc": ("{year} के सभी व्रत और त्योहार माहवार - एकादशी, प्रदोष, संकष्टी, पूर्णिमा, "
                      "अमावस्या, शिवरात्रि और दीपावली, होली, नवरात्रि जैसे पर्व, पूजा मुहूर्त सहित।"),
        "year.intro": ("<p>{year} में नई दिल्ली के लिए <strong>{count}</strong> व्रत और त्योहार, "
                       "पंचांग से गणना किए गए। प्रमुख त्योहार पर क्लिक कर पूजा मुहूर्त और विधि देखें।</p>"),
        "year.itemlist": "प्रमुख त्योहार {year}",

        "ek.title": "एकादशी {year}: सभी एकादशी व्रत तिथि और पारण समय (नई दिल्ली)",
        "ek.h1": "एकादशी {year}",
        "ek.desc": ("{year} की सभी {count} एकादशी - व्रत की तिथि, एकादशी तिथि का आरंभ-समाप्ति "
                    "और अगले दिन पारण का समय, नई दिल्ली के लिए।"),
        "ek.th": "<tr><th>एकादशी</th><th>व्रत</th><th>पारण</th></tr>",
        "ek.rule": ("<p><strong>नियम (स्मार्त):</strong> जिस दिन सूर्योदय के समय एकादशी हो उस दिन व्रत; "
                    "दो सूर्योदय पर हो तो दूसरा दिन, और किसी सूर्योदय पर न हो तो जिस दिन एकादशी पड़े। पारण "
                    "अगले दिन सूर्योदय के बाद, हरि वासर (द्वादशी का पहला चौथाई भाग) समाप्त होने पर, "
                    "प्रातःकाल में और द्वादशी समाप्त होने से पहले किया जाता है; हरि वासर प्रातःकाल के बाद तक "
                    "रहे तो मध्याह्न छोड़कर अपराह्न में।</p>"),
        "ek.sub": '<p class="hi" lang="en">Ekadashi {year}</p>',
        "ek.crumb": "एकादशी {year}",

        "fest.title": "{name} {year}: तिथि और शुभ मुहूर्त - {short}",
        "fest.h1": "{name} {year}",
        "fest.main": "{text}। ",
        "fest.desc": "{name} {year} {date}, {weekday} को है। {main}नई दिल्ली के लिए पूजा मुहूर्त व तिथि।",
        "fest.when": "{name} {year} में <strong>{when}</strong> को है।",
        "fest.sub": '<p class="hi" lang="en">{name_en} {year}</p>',
        "fest.about_h2": "क्या है और कैसे मनाएं",
        "fest.rule_h2": "तिथि का नियम",
        "fest.faq_h2": "अक्सर पूछे जाने वाले प्रश्न",
        "event.place": "भारत",
        "faq.when_q": "{name} {year} कब है?",
        "faq.when_a": "{name} {year} {weekday}, {date} को है।",
        "faq.muhurat_q": "{name} {year} का पूजा मुहूर्त क्या है?",
        "faq.timings_q": "{name} {year} का समय क्या है?",
        "faq.timings_a": ("नई दिल्ली के लिए - {timings}। समय शहर के अनुसार कुछ मिनट बदलता है; "
                          "अपने शहर के लिए पंचांग देखें।"),
        "faq.why_q": "{name} {year} {short} को ही क्यों है?",
        "faq.why_a": "तिथि का नियम: {rule}। {year} में यह {when} को पड़ता है (नई दिल्ली)।",
    },

    "te": {
        "crumb": "పండుగలు, వ్రతాలు",
        "day_label": "{date}, {weekday}",
        "timing": "{label}: {prefix}{value}",
        "tithi.text": "{paksha} {name}: {start} నుండి {end} వరకు",
        "tithi.paksha": "{paksha}",
        "table.th": "<tr><th>తేదీ</th><th>వ్రతం / పండుగ</th><th>సమయం ({city})</th></tr>",
        "city_note": ('<div class="box"><p><strong>సమయాలు నగరాన్ని బట్టి మారుతాయి.</strong> ఇక్కడి '
                      "సమయాలన్నీ {city} నగర సూర్యోదయం, సూర్యాస్తమయం, చంద్రోదయం ఆధారంగా లెక్కించినవి; "
                      "వేరే నగరంలో ఇవి కొన్ని నిమిషాలు మారుతాయి, అప్పుడప్పుడు తేదీ కూడా మారవచ్చు. "
                      "తేదీలు దృక్ పంచాంగం స్మార్త (సాధారణ) గణనను అనుసరిస్తాయి. మీ నగర పంచాంగం "
                      "చూడండి.</p></div>"),
        "top_note": ('<p class="note"><small>చాలా వ్రతాలు, పండుగల తేదీ భారతదేశమంతటా ఒకటే, కానీ '
                     "పూజ ముహూర్తం, పారణ, చంద్రోదయ సమయాలు నగరాన్ని బట్టి మారుతాయి - ఇక్కడి సమయాలన్నీ "
                     "<strong>{city}</strong> నగరానికి సంబంధించినవి. ప్రాంతీయ సంప్రదాయాలు వేరుగా "
                     "ఉండవచ్చు.</small></p>"),
        "cities.heading": "మీ నగరంలో పండుగలు, వ్రతాలు",
        "tools.panchang": "ఈరోజు పంచాంగం - {city}",
        "tools.rahu": "{t_rahu_kaal} - {city}",
        "tools.heading": "{city} కోసం మరిన్ని",
        "cta": "మీ నగర పంచాంగం చూడండి — ఉచితం",
        "more.today": "ఈరోజు పండుగలు, వ్రతాలు",
        "more.year": "పండుగల క్యాలెండర్ {year}",
        "more.ekadashi": "ఏకాదశి {year}",
        "more.panchang": "ఈరోజు పంచాంగం",
        "more.rashifal": "ఈరోజు రాశి ఫలాలు",
        "more.heading": "మరిన్ని",
        "majors.heading": "{year} ప్రధాన పండుగలు",
        "today.rule": "నియమం",
        "today.none": "ఈరోజు ప్రధాన వ్రతం లేదా పండుగ లేదు.",
        "today.next": " తదుపరి: <strong>{name}</strong>, {day}.",
        "block.heading": "ఈరోజు పండుగలు, వ్రతాలు",
        "nf.h1": "పేజీ కనబడలేదు",

        "hub.title_default": "ఈరోజు పండుగలు, వ్రతాలు ({date}) - ముహూర్త సమయాలతో",
        "hub.title_city": "ఈరోజు పండుగలు, వ్రతాలు - {city} ({date})",
        "hub.h1_default": "ఈరోజు పండుగలు, వ్రతాలు",
        "hub.h1_city": "ఈరోజు పండుగలు, వ్రతాలు - {city}",
        "hub.desc_today": "ఈరోజు, {date}: {names}. ",
        "hub.desc_none": "{date}: ఈరోజు ప్రధాన వ్రతం లేదు. ",
        "hub.desc_rest": ("రాబోయే 30 రోజుల ఉపవాసాలు, పండుగలు - ఏకాదశి పారణ, ప్రదోషం, సంకష్టహర "
                          "చతుర్థి చంద్రోదయ సమయాలతో - {city}."),
        "hub.sub": '<p class="hi">నేటి పండుగలు, వ్రతాలు, ముహూర్తాలు</p>',
        "hub.upcoming": "రాబోయే 30 రోజులు",

        "year.title": "హిందూ పండుగలు, వ్రతాలు {year}: తేదీలు, ముహూర్తాలు (న్యూఢిల్లీ)",
        "year.h1": "పండుగలు, వ్రతాల క్యాలెండర్ {year}",
        "year.desc": ("{year}లోని అన్ని హిందూ వ్రతాలు, పండుగలు నెలవారీగా - ఏకాదశి, ప్రదోషం, సంకష్టహర "
                      "చతుర్థి, పౌర్ణమి, అమావాస్య, శివరాత్రి, దీపావళి, నవరాత్రులు, రాఖీ పౌర్ణమి వంటి "
                      "పండుగలు, న్యూఢిల్లీ పూజ ముహూర్తాలతో."),
        "year.intro": ("<p>{year}లో న్యూఢిల్లీకి <strong>{count}</strong> వ్రతాలు, పండుగలు, పంచాంగం "
                       "ఆధారంగా లెక్కించినవి. ప్రధాన పండుగపై నొక్కి దాని పూజ ముహూర్తం, విశేషాలు "
                       "చూడండి.</p>"),
        "year.month": "{month} {year}",
        "year.itemlist": "{year} ప్రధాన హిందూ పండుగలు",

        "ek.title": "ఏకాదశి {year} తేదీలు: అన్ని ఏకాదశి వ్రతాలు, పారణ సమయం (న్యూఢిల్లీ)",
        "ek.h1": "ఏకాదశి {year}: తేదీలు, పారణ సమయం",
        "ek.desc": ("{year}లోని మొత్తం {count} ఏకాదశులు - ఉపవాస తేదీ, ఏకాదశి తిథి ప్రారంభ, ముగింపు "
                    "సమయాలు, మరుసటి రోజు పారణ (ఉపవాస విరమణ) సమయం, న్యూఢిల్లీకి."),
        "ek.th": "<tr><th>ఏకాదశి</th><th>ఉపవాసం</th><th>పారణ</th></tr>",
        "ek.rule": ("<p><strong>నియమం (స్మార్త):</strong> సూర్యోదయ సమయంలో ఏకాదశి ఉన్న రోజున "
                    "ఉపవాసం; రెండు సూర్యోదయాల్లో ఉంటే రెండవ రోజు, ఏ సూర్యోదయంలోనూ లేకపోతే ఏకాదశి "
                    "వచ్చిన రోజు. పారణ మరుసటి రోజు సూర్యోదయం తర్వాత, హరి వాసరం (ద్వాదశి మొదటి పావు "
                    "భాగం) ముగిశాక, ప్రాతఃకాలంలో, ద్వాదశి ముగియక ముందే చేయాలి; హరి వాసరం "
                    "ప్రాతఃకాలం దాటి కొనసాగితే పారణ అపరాహ్ణానికి మారుతుంది (మధ్యాహ్నం "
                    "వదిలివేస్తారు).</p>"),
        "ek.sub": '<p class="hi">ఏకాదశి వ్రతం {year} - పారణ సమయాలు</p>',
        "ek.crumb": "ఏకాదశి {year}",

        "fest.title": "{name} {year} తేదీ, ముహూర్తం - {short}",
        "fest.h1": "{name} {year}: తేదీ, ముహూర్తం",
        "fest.main": "{text}. ",
        "fest.desc": "{name} {year} తేదీ: {date}, {weekday}. {main}న్యూఢిల్లీకి పూజ సమయాలు.",
        "fest.when": "{name} {year} తేదీ: <strong>{when}</strong>.",
        "fest.sub": '<p class="hi">పండుగ తేదీ, పూజ ముహూర్తం {year}</p>',
        "fest.about_h2": "పండుగ విశేషం, ఆచరించే విధానం",
        "fest.rule_h2": "తేదీ ఎలా నిర్ణయిస్తారు",
        "fest.faq_h2": "తరచుగా అడిగే ప్రశ్నలు",
        "event.place": "భారతదేశం",
        "faq.when_q": "{name} {year} ఎప్పుడు?",
        "faq.when_a": "{name} {year} తేదీ: {date}, {weekday}.",
        "faq.muhurat_q": "{name} {year} పూజ ముహూర్తం ఏమిటి?",
        "faq.timings_q": "{name} {year} సమయాలు ఏమిటి?",
        "faq.timings_a": ("న్యూఢిల్లీకి - {timings}. సమయాలు నగరాన్ని బట్టి కొన్ని నిమిషాలు మారుతాయి; "
                          "మీ నగర పంచాంగం చూడండి."),
        "faq.why_q": "{name} {year} {short} నాడే ఎందుకు?",
        "faq.why_a": "తేదీ ఈ నియమం ప్రకారం: {rule}. {year}లో అది {when} (న్యూఢిల్లీ).",
    },

    "kn": {
        "crumb": "ವ್ರತ ಮತ್ತು ಹಬ್ಬಗಳು",
        "day_label": "{date}, {weekday}",
        "timing": "{label}: {prefix}{value}",
        "tithi.text": "{paksha} {name}: {start} ರಿಂದ {end} ವರೆಗೆ",
        "tithi.paksha": "{paksha} ಪಕ್ಷ",
        "table.th": "<tr><th>ದಿನಾಂಕ</th><th>ವ್ರತ / ಹಬ್ಬ</th><th>ಸಮಯ ({city})</th></tr>",
        "city_note": ('<div class="box"><p><strong>ಸಮಯಗಳು ನಗರದಿಂದ ನಗರಕ್ಕೆ ಬದಲಾಗುತ್ತವೆ.</strong> ಇಲ್ಲಿನ '
                      "ಎಲ್ಲಾ ಸಮಯಗಳು {city} ನಗರದ ಸೂರ್ಯೋದಯ, ಸೂರ್ಯಾಸ್ತ ಮತ್ತು ಚಂದ್ರೋದಯವನ್ನು ಆಧರಿಸಿವೆ; "
                      "ಬೇರೆ ನಗರದಲ್ಲಿ ಇವು ಕೆಲವು ನಿಮಿಷಗಳಷ್ಟು ಬದಲಾಗುತ್ತವೆ ಮತ್ತು ಕೆಲವೊಮ್ಮೆ ದಿನಾಂಕವೂ "
                      "ಬದಲಾಗಬಹುದು. ದಿನಾಂಕಗಳು ದೃಕ್ ಪಂಚಾಂಗದ ಸ್ಮಾರ್ತ (ಸಾಮಾನ್ಯ) ಗಣನೆಯನ್ನು "
                      "ಅನುಸರಿಸುತ್ತವೆ. ನಿಮ್ಮ ನಗರದ ಪಂಚಾಂಗವನ್ನು ನೋಡಿ.</p></div>"),
        "top_note": ('<p class="note"><small>ಹೆಚ್ಚಿನ ವ್ರತ-ಹಬ್ಬಗಳ ದಿನಾಂಕ ಭಾರತದಾದ್ಯಂತ ಒಂದೇ ಆಗಿರುತ್ತದೆ, '
                     "ಆದರೆ ಪೂಜಾ ಮುಹೂರ್ತ, ಪಾರಣೆ ಮತ್ತು ಚಂದ್ರೋದಯದ ಸಮಯಗಳು ನಗರದಿಂದ ನಗರಕ್ಕೆ "
                     "ಬದಲಾಗುತ್ತವೆ - ಇಲ್ಲಿನ ಎಲ್ಲಾ ಸಮಯಗಳು <strong>{city}</strong> ನಗರದವು. ಪ್ರಾದೇಶಿಕ "
                     "ಸಂಪ್ರದಾಯಗಳು ಭಿನ್ನವಾಗಿರಬಹುದು.</small></p>"),
        "cities.heading": "ನಿಮ್ಮ ನಗರದ ವ್ರತ ಮತ್ತು ಹಬ್ಬಗಳು",
        "tools.panchang": "{city} ಇಂದಿನ ಪಂಚಾಂಗ",
        "tools.rahu": "{city} ರಾಹು ಕಾಲ",
        "tools.heading": "{city} ನಗರಕ್ಕೆ ಇನ್ನಷ್ಟು",
        "cta": "ನಿಮ್ಮ ನಗರದ ಪಂಚಾಂಗ ನೋಡಿ — ಉಚಿತ",
        "more.today": "ಇಂದಿನ ವ್ರತ ಮತ್ತು ಹಬ್ಬಗಳು",
        "more.year": "ಹಬ್ಬಗಳ ಕ್ಯಾಲೆಂಡರ್ {year}",
        "more.ekadashi": "ಏಕಾದಶಿ {year}",
        "more.panchang": "ಇಂದಿನ ಪಂಚಾಂಗ",
        "more.rashifal": "ಇಂದಿನ ರಾಶಿ ಭವಿಷ್ಯ",
        "more.heading": "ಇನ್ನಷ್ಟು",
        "majors.heading": "{year}ರ ಪ್ರಮುಖ ಹಬ್ಬಗಳು",
        "today.rule": "ನಿಯಮ",
        "today.none": "ಇಂದು ಯಾವುದೇ ಪ್ರಮುಖ ವ್ರತ ಅಥವಾ ಹಬ್ಬ ಇಲ್ಲ.",
        "today.next": " ಮುಂದಿನದು: <strong>{name}</strong>, {day}.",
        "block.heading": "ಇಂದಿನ ವ್ರತ ಮತ್ತು ಹಬ್ಬಗಳು",
        "nf.h1": "ಪುಟ ಕಂಡುಬಂದಿಲ್ಲ",

        "hub.title_default": "ಇಂದಿನ ವ್ರತ ಮತ್ತು ಹಬ್ಬಗಳು ({date}) - ಪೂಜಾ ಮುಹೂರ್ತ ಸಹಿತ",
        "hub.title_city": "ಇಂದಿನ ವ್ರತ ಮತ್ತು ಹಬ್ಬಗಳು {city} ({date}) - ಮುಹೂರ್ತ ಸಹಿತ",
        "hub.h1_default": "ಇಂದಿನ ವ್ರತ ಮತ್ತು ಹಬ್ಬಗಳು",
        "hub.h1_city": "{city} ನಗರದ ಇಂದಿನ ವ್ರತ ಮತ್ತು ಹಬ್ಬಗಳು",
        "hub.desc_today": "ಇಂದು, {date}: {names}. ",
        "hub.desc_none": "{date}: ಇಂದು ಯಾವುದೇ ಪ್ರಮುಖ ವ್ರತ ಇಲ್ಲ. ",
        "hub.desc_rest": ("ಮುಂದಿನ 30 ದಿನಗಳ ವ್ರತ ಮತ್ತು ಹಬ್ಬಗಳು, ಏಕಾದಶಿ ಪಾರಣೆ, ಪ್ರದೋಷ ಮತ್ತು "
                          "ಸಂಕಷ್ಟಹರ ಚತುರ್ಥಿಯ ಚಂದ್ರೋದಯ ಸಮಯಗಳೊಂದಿಗೆ - {city}."),
        "hub.sub": '<p class="hi">ಇಂದು ಯಾವ ಹಬ್ಬ? ವ್ರತ, ಹಬ್ಬ ಮತ್ತು ಪೂಜಾ ಮುಹೂರ್ತ</p>',
        "hub.upcoming": "ಮುಂದಿನ 30 ದಿನಗಳು",

        "year.title": "{year} ಹಬ್ಬಗಳ ಪಟ್ಟಿ: ವ್ರತ, ಹಬ್ಬಗಳ ದಿನಾಂಕ ಮತ್ತು ಮುಹೂರ್ತ (ನವದೆಹಲಿ)",
        "year.h1": "ವ್ರತ ಮತ್ತು ಹಬ್ಬಗಳ ಕ್ಯಾಲೆಂಡರ್ {year}",
        "year.desc": ("{year}ರ ಎಲ್ಲಾ ಹಿಂದೂ ವ್ರತ-ಹಬ್ಬಗಳು ತಿಂಗಳುವಾರು - ಏಕಾದಶಿ, ಪ್ರದೋಷ, "
                      "ಸಂಕಷ್ಟಹರ ಚತುರ್ಥಿ, ಹುಣ್ಣಿಮೆ, ಅಮಾವಾಸ್ಯೆ, ಶಿವರಾತ್ರಿ, ದೀಪಾವಳಿ, ನವರಾತ್ರಿ, "
                      "ರಕ್ಷಾ ಬಂಧನ - ನವದೆಹಲಿಯ ಪೂಜಾ ಮುಹೂರ್ತದೊಂದಿಗೆ."),
        "year.intro": ("<p>{year}ರಲ್ಲಿ ನವದೆಹಲಿಗೆ <strong>{count}</strong> ವ್ರತ ಮತ್ತು ಹಬ್ಬಗಳು, "
                       "ಪಂಚಾಂಗದಿಂದ ಲೆಕ್ಕ ಹಾಕಲಾಗಿದೆ. ಪೂಜಾ ಮುಹೂರ್ತ ಮತ್ತು ಹಬ್ಬದ ವಿವರಕ್ಕಾಗಿ "
                       "ಪ್ರಮುಖ ಹಬ್ಬದ ಮೇಲೆ ಟ್ಯಾಪ್ ಮಾಡಿ.</p>"),
        "year.month": "{month} {year}",
        "year.itemlist": "ಪ್ರಮುಖ ಹಿಂದೂ ಹಬ್ಬಗಳು {year}",

        "ek.title": "ಏಕಾದಶಿ {year} ದಿನಾಂಕಗಳು: ಎಲ್ಲಾ ಏಕಾದಶಿ ವ್ರತ ಮತ್ತು ಪಾರಣೆ ಸಮಯ (ನವದೆಹಲಿ)",
        "ek.h1": "ಏಕಾದಶಿ {year}: ದಿನಾಂಕಗಳು ಮತ್ತು ಪಾರಣೆ ಸಮಯ",
        "ek.desc": ("{year}ರ ಎಲ್ಲಾ {count} ಏಕಾದಶಿಗಳು - ಉಪವಾಸದ ದಿನ, ಏಕಾದಶಿ ತಿಥಿಯ ಆರಂಭ-ಮುಕ್ತಾಯ "
                    "ಸಮಯ ಮತ್ತು ಮರುದಿನದ ಪಾರಣೆ (ಉಪವಾಸ ಮುಕ್ತಾಯ) ಸಮಯ, ನವದೆಹಲಿಗೆ."),
        "ek.th": "<tr><th>ಏಕಾದಶಿ</th><th>ಉಪವಾಸ</th><th>ಪಾರಣೆ</th></tr>",
        "ek.rule": ("<p><strong>ನಿಯಮ (ಸ್ಮಾರ್ತ):</strong> ಸೂರ್ಯೋದಯದ ಸಮಯದಲ್ಲಿ ಏಕಾದಶಿ ಇರುವ ದಿನ "
                    "ಉಪವಾಸ; ಎರಡು ಸೂರ್ಯೋದಯಗಳಲ್ಲಿ ಇದ್ದರೆ ಎರಡನೇ ದಿನ, ಯಾವ ಸೂರ್ಯೋದಯದಲ್ಲೂ "
                    "ಇಲ್ಲದಿದ್ದರೆ ಏಕಾದಶಿ ಬರುವ ದಿನ. ಪಾರಣೆ ಮರುದಿನ ಸೂರ್ಯೋದಯದ ನಂತರ, ಹರಿ ವಾಸರ "
                    "(ದ್ವಾದಶಿಯ ಮೊದಲ ಕಾಲು ಭಾಗ) ಮುಗಿದ ಮೇಲೆ, ಪ್ರಾತಃಕಾಲದಲ್ಲಿ ಮತ್ತು ದ್ವಾದಶಿ "
                    "ಮುಗಿಯುವ ಮೊದಲು; ಹರಿ ವಾಸರ ಪ್ರಾತಃಕಾಲವನ್ನು ಮೀರಿದರೆ ಪಾರಣೆ ಅಪರಾಹ್ನಕ್ಕೆ "
                    "ಸರಿಯುತ್ತದೆ (ಮಧ್ಯಾಹ್ನವನ್ನು ತಪ್ಪಿಸಲಾಗುತ್ತದೆ).</p>"),
        "ek.sub": '<p class="hi">ಏಕಾದಶಿ ಉಪವಾಸದ ಪಟ್ಟಿ {year}</p>',
        "ek.crumb": "ಏಕಾದಶಿ {year}",

        "fest.title": "{name} {year} ದಿನಾಂಕ ಮತ್ತು ಮುಹೂರ್ತ - {short}",
        "fest.h1": "{name} {year}: ದಿನಾಂಕ ಮತ್ತು ಮುಹೂರ್ತ",
        "fest.main": "{text}. ",
        "fest.desc": "{name} {year}: {weekday}, {date} ರಂದು. {main}ನವದೆಹಲಿಯ ಪೂಜಾ ಸಮಯಗಳು.",
        "fest.when": "{name} {year} ದಿನಾಂಕ: <strong>{when}</strong>.",
        "fest.sub": '<p class="hi">ವ್ರತ-ಹಬ್ಬದ ದಿನಾಂಕ ಮತ್ತು ಪೂಜಾ ಮುಹೂರ್ತ {year}</p>',
        "fest.about_h2": "ಏನು ಮತ್ತು ಹೇಗೆ ಆಚರಿಸಲಾಗುತ್ತದೆ",
        "fest.rule_h2": "ದಿನಾಂಕವನ್ನು ಹೇಗೆ ನಿರ್ಧರಿಸಲಾಗುತ್ತದೆ",
        "fest.faq_h2": "ಪದೇ ಪದೇ ಕೇಳಲಾಗುವ ಪ್ರಶ್ನೆಗಳು",
        "event.place": "ಭಾರತ",
        "faq.when_q": "{name} {year} ಯಾವಾಗ?",
        "faq.when_a": "{name} {year}: {weekday}, {date} ರಂದು.",
        "faq.muhurat_q": "{name} {year} ಪೂಜಾ ಮುಹೂರ್ತ ಯಾವುದು?",
        "faq.timings_q": "{name} {year} ಸಮಯಗಳು ಯಾವುವು?",
        "faq.timings_a": ("ನವದೆಹಲಿಗೆ - {timings}. ಸಮಯಗಳು ನಗರದಿಂದ ನಗರಕ್ಕೆ ಕೆಲವು ನಿಮಿಷಗಳಷ್ಟು "
                          "ಬದಲಾಗುತ್ತವೆ; ನಿಮ್ಮ ನಗರದ ಪಂಚಾಂಗವನ್ನು ನೋಡಿ."),
        "faq.why_q": "{name} {year} ಅನ್ನು {short} ರಂದೇ ಏಕೆ ಆಚರಿಸಲಾಗುತ್ತದೆ?",
        "faq.why_a": "ದಿನಾಂಕವು ಈ ನಿಯಮವನ್ನು ಅನುಸರಿಸುತ್ತದೆ: {rule}. {year}ರಲ್ಲಿ ಅದು {when} (ನವದೆಹಲಿ).",
    },

    # Tamil (DIVASTRO-123)
    "ta": {
        "crumb": "விரதங்கள், பண்டிகைகள்",
        "day_label": "{date}, {weekday}",
        "timing": "{label}: {prefix}{value}",
        "tithi.text": "{paksha} {name}: {start} முதல் {end} வரை",
        "tithi.paksha": "{paksha}",
        "table.th": "<tr><th>தேதி</th><th>விரதம் / பண்டிகை</th><th>நேரம் ({city})</th></tr>",
        "city_note": ("<div class=\"box\"><p><strong>நேரங்கள் ஊருக்கு ஊர் மாறும்.</strong> இங்குள்ள எல்லா "
                      "நேரங்களும் {city} நகரின் சூரிய உதயம், அஸ்தமனம், சந்திர உதயத்தைக் கொண்டு "
                      "கணக்கிடப்பட்டவை; வேறு ஊரில் சில நிமிடங்கள் மாறலாம், சில சமயம் தேதியும் மாறலாம். "
                      "தேதிகள் த்ருக் பஞ்சாங்கத்தின் ஸ்மார்த்த (பொது) முறைப்படி உள்ளன. உங்கள் ஊருக்கான "
                      "பஞ்சாங்கத்தைப் பாருங்கள்.</p></div>"),
        "top_note": ("<p class=\"note\"><small>பெரும்பாலான விரதங்கள், பண்டிகைகளின் தேதி இந்தியா முழுவதும் "
                     "ஒன்றே; ஆனால் பூஜை முகூர்த்தம், பாரணை, சந்திர உதய நேரங்கள் ஊருக்கு ஊர் வேறுபடும் - "
                     "இங்குள்ள எல்லா நேரங்களும் <strong>{city}</strong> நகருக்கானவை. பிராந்திய மரபுகள் "
                     "மாறுபடலாம்.</small></p>"),
        "cities.heading": "உங்கள் ஊரின் விரதங்கள், பண்டிகைகள்",
        "tools.panchang": "{city} இன்றைய பஞ்சாங்கம்",
        "tools.rahu": "{city} ராகு காலம்",
        "tools.heading": "{city} - மேலும்",
        "cta": "உங்கள் ஊரின் பஞ்சாங்கத்தைப் பாருங்கள் — இலவசம்",
        "more.today": "இன்றைய விரதங்கள், பண்டிகைகள்",
        "more.year": "பண்டிகை நாட்காட்டி {year}",
        "more.ekadashi": "ஏகாதசி {year}",
        "more.panchang": "இன்றைய பஞ்சாங்கம்",
        "more.rashifal": "இன்றைய ராசி பலன்",
        "more.heading": "மேலும்",
        "majors.heading": "{year} முக்கிய பண்டிகைகள்",
        "today.rule": "விதி",
        "today.none": "இன்று முக்கிய விரதமோ பண்டிகையோ இல்லை.",
        "today.next": " அடுத்து: <strong>{name}</strong>, {day}.",
        "block.heading": "இன்றைய விரதங்கள், பண்டிகைகள்",
        "nf.h1": "பக்கம் கிடைக்கவில்லை",
        "hub.title_default": "இன்றைய விரதங்கள் மற்றும் பண்டிகைகள் ({date}) - பூஜை நேரத்துடன்",
        "hub.title_city": "{city} இன்றைய விரதங்கள், பண்டிகைகள் ({date}) - பூஜை நேரம்",
        "hub.h1_default": "இன்றைய விரதங்கள் மற்றும் பண்டிகைகள்",
        "hub.h1_city": "{city}: இன்றைய விரதங்கள் மற்றும் பண்டிகைகள்",
        "hub.desc_today": "இன்று, {date}: {names}. ",
        "hub.desc_none": "{date}: இன்று முக்கிய விரதம் இல்லை. ",
        "hub.desc_rest": ("அடுத்த 30 நாட்களின் விரதங்கள், பண்டிகைகள் - ஏகாதசி பாரணை, பிரதோஷம், சங்கடஹர "
                          "சதுர்த்தி சந்திர உதய நேரங்களுடன் - {city}."),
        "hub.sub": "<p class=\"hi\">இன்று என்ன விசேஷம்? - விரதம், பண்டிகை, பூஜை நேரம்</p>",
        "hub.upcoming": "அடுத்த 30 நாட்கள்",
        "year.title": "விரதங்கள் மற்றும் பண்டிகைகள் {year}: தேதிகள், முகூர்த்தம் (புது தில்லி)",
        "year.h1": "விரத, பண்டிகை நாட்காட்டி {year}",
        "year.desc": ("{year} ஆம் ஆண்டின் எல்லா இந்து விரதங்களும் பண்டிகைகளும் மாதவாரியாக - ஏகாதசி, "
                      "பிரதோஷம், சங்கடஹர சதுர்த்தி, பௌர்ணமி, அமாவாசை, சிவராத்திரி, தீபாவளி, நவராத்திரி, "
                      "ரக்ஷா பந்தன் போன்ற பண்டிகைகள், புது தில்லிக்கான பூஜை முகூர்த்தத்துடன்."),
        "year.intro": ("<p>{year} இல் புது தில்லிக்கு <strong>{count}</strong> விரதங்கள், பண்டிகைகள் - "
                       "பஞ்சாங்கப்படி கணக்கிடப்பட்டவை. ஒரு முக்கிய பண்டிகையைத் தொட்டால் அதன் பூஜை "
                       "முகூர்த்தமும் விவரமும் கிடைக்கும்.</p>"),
        "year.month": "{month} {year}",
        "year.itemlist": "முக்கிய இந்து பண்டிகைகள் {year}",
        "ek.title": "ஏகாதசி {year} தேதிகள்: எல்லா ஏகாதசி விரதமும் பாரணை நேரமும் (புது தில்லி)",
        "ek.h1": "ஏகாதசி {year}: தேதிகள், பாரணை நேரம்",
        "ek.desc": ("{year} ஆம் ஆண்டின் எல்லா {count} ஏகாதசிகளும் - விரத நாள், ஏகாதசி திதி நேரம், மறுநாள் "
                    "பாரணை (விரதம் முடிக்கும்) நேரம், புது தில்லிக்கு."),
        "ek.th": "<tr><th>ஏகாதசி</th><th>விரதம்</th><th>பாரணை</th></tr>",
        "ek.rule": ("<p><strong>விதி (ஸ்மார்த்தம்):</strong> சூரிய உதயத்தின்போது ஏகாதசி இருக்கும் நாளில் "
                    "விரதம்; இரண்டு சூரிய உதயங்களில் இருந்தால் இரண்டாம் நாள், எந்த உதயத்திலும் "
                    "இல்லையெனில் ஏகாதசி வரும் நாள். பாரணை மறுநாள் சூரிய உதயத்துக்குப் பிறகு, ஹரி வாசரம் "
                    "(துவாதசியின் முதல் கால் பகுதி) முடிந்ததும், பிராதக் காலத்துக்குள், துவாதசி "
                    "முடிவதற்கு முன் செய்யப்படும்; ஹரி வாசரம் பிராதக் காலத்தைத் தாண்டி நீடித்தால், பாரணை "
                    "அபராஹ்ணத்துக்கு மாறும் (மத்தியானம் தவிர்க்கப்படும்).</p>"),
        "ek.sub": "<p class=\"hi\">ஏகாதசி விரதம் {year} - தேதி, பாரணை நேரம்</p>",
        "ek.crumb": "ஏகாதசி {year}",
        "fest.title": "{name} {year}: தேதி, பூஜை நேரம் - {short}",
        "fest.h1": "{name} {year}: தேதி, முகூர்த்தம்",
        "fest.main": "{text}. ",
        "fest.desc": "{name} {year}: {date}, {weekday}. {main}புது தில்லிக்கான பூஜை நேரங்கள்.",
        "fest.when": "{name} {year} <strong>{when}</strong> அன்று.",
        "fest.sub": "<p class=\"hi\">{year} தேதி, நல்ல நேரம், வழிபாட்டு முறை</p>",
        "fest.about_h2": "இது என்ன, எப்படிக் கொண்டாடப்படுகிறது",
        "fest.rule_h2": "தேதி எப்படி நிர்ணயிக்கப்படுகிறது",
        "fest.faq_h2": "அடிக்கடி கேட்கப்படும் கேள்விகள்",
        "event.place": "இந்தியா",
        "faq.when_q": "{name} {year} எப்போது?",
        "faq.when_a": "{name} {year} {date}, {weekday} அன்று.",
        "faq.muhurat_q": "{name} {year} பூஜை முகூர்த்தம் என்ன?",
        "faq.timings_q": "{name} {year} நேரங்கள் என்ன?",
        "faq.timings_a": ("புது தில்லிக்கு - {timings}. நேரங்கள் ஊருக்கு ஊர் சில நிமிடங்கள் மாறும்; உங்கள் "
                          "ஊரின் பஞ்சாங்கத்தைப் பாருங்கள்."),
        "faq.why_q": "{name} {year} ஏன் {short} அன்று?",
        "faq.why_a": "தேதி இந்த விதிப்படி: {rule}. {year} இல் அது {when} (புது தில்லி).",
    },

    # Malayalam (DIVASTRO-123)
    "ml": {
        "crumb": "വ്രതങ്ങളും ഉത്സവങ്ങളും",
        "day_label": "{date}, {weekday}",
        "timing": "{label}: {prefix}{value}",
        "tithi.text": "{paksha} {name}: {start} മുതൽ {end} വരെ",
        "tithi.paksha": "{paksha}പക്ഷ",
        "table.th": "<tr><th>തീയതി</th><th>വ്രതം / ഉത്സവം</th><th>സമയം ({city})</th></tr>",
        "city_note": ("<div class=\"box\"><p><strong>സമയം ഓരോ നഗരത്തിലും വ്യത്യാസപ്പെടും.</strong> ഇവിടെയുള്ള "
                      "എല്ലാ സമയങ്ങളും {city} നഗരത്തിലെ സൂര്യോദയം, സൂര്യാസ്തമയം, ചന്ദ്രോദയം എന്നിവ "
                      "അനുസരിച്ചാണ്; മറ്റൊരു നഗരത്തിൽ ഏതാനും മിനിറ്റുകൾ മാറാം, ചിലപ്പോൾ തീയതിയും മാറാം. "
                      "തീയതികൾ ദൃക് പഞ്ചാംഗത്തിന്റെ സ്മാർത്ത (പൊതു) രീതി പിന്തുടരുന്നു. നിങ്ങളുടെ "
                      "നഗരത്തിന്റെ പഞ്ചാംഗം നോക്കുക.</p></div>"),
        "top_note": ("<p class=\"note\"><small>മിക്ക വ്രതങ്ങളുടെയും ഉത്സവങ്ങളുടെയും തീയതി ഇന്ത്യയിലാകെ "
                     "ഒന്നുതന്നെ; എന്നാൽ പൂജാ മുഹൂർത്തം, പാരണ, ചന്ദ്രോദയ സമയങ്ങൾ നഗരത്തിനനുസരിച്ച് മാറും - "
                     "ഇവിടെയുള്ള എല്ലാ സമയങ്ങളും <strong>{city}</strong> നഗരത്തിലേതാണ്. പ്രാദേശിക ആചാരങ്ങൾ "
                     "വ്യത്യാസപ്പെടാം.</small></p>"),
        "cities.heading": "നിങ്ങളുടെ നഗരത്തിലെ വ്രതങ്ങളും ഉത്സവങ്ങളും",
        "tools.panchang": "{city} ഇന്നത്തെ പഞ്ചാംഗം",
        "tools.rahu": "{city} രാഹുകാലം",
        "tools.heading": "{city} - കൂടുതൽ",
        "cta": "നിങ്ങളുടെ നഗരത്തിന്റെ പഞ്ചാംഗം കാണുക — സൗജന്യം",
        "more.today": "ഇന്നത്തെ വ്രതങ്ങളും ഉത്സവങ്ങളും",
        "more.year": "ഉത്സവ കലണ്ടർ {year}",
        "more.ekadashi": "ഏകാദശി {year}",
        "more.panchang": "ഇന്നത്തെ പഞ്ചാംഗം",
        "more.rashifal": "ഇന്നത്തെ നക്ഷത്രഫലം",
        "more.heading": "കൂടുതൽ",
        "majors.heading": "{year}-ലെ പ്രധാന ഉത്സവങ്ങൾ",
        "today.rule": "നിയമം",
        "today.none": "ഇന്ന് പ്രധാന വ്രതമോ ഉത്സവമോ ഇല്ല.",
        "today.next": " അടുത്തത്: <strong>{name}</strong>, {day}.",
        "block.heading": "ഇന്നത്തെ വ്രതങ്ങളും ഉത്സവങ്ങളും",
        "nf.h1": "പേജ് കണ്ടെത്തിയില്ല",
        "hub.title_default": "ഇന്നത്തെ വ്രതങ്ങളും ഉത്സവങ്ങളും ({date}) - മുഹൂർത്തം സഹിതം",
        "hub.title_city": "{city}: ഇന്നത്തെ വ്രതങ്ങളും ഉത്സവങ്ങളും ({date}) - മുഹൂർത്തം",
        "hub.h1_default": "ഇന്നത്തെ വ്രതങ്ങളും ഉത്സവങ്ങളും",
        "hub.h1_city": "{city}: ഇന്നത്തെ വ്രതങ്ങളും ഉത്സവങ്ങളും",
        "hub.desc_today": "ഇന്ന്, {date}: {names}. ",
        "hub.desc_none": "{date}: ഇന്ന് പ്രധാന വ്രതമില്ല. ",
        "hub.desc_rest": ("അടുത്ത 30 ദിവസത്തെ വ്രതങ്ങളും ഉത്സവങ്ങളും - ഏകാദശി പാരണ, പ്രദോഷം, സങ്കഷ്ടി ചന്ദ്രോദയ "
                          "സമയങ്ങൾ സഹിതം - {city}."),
        "hub.sub": "<p class=\"hi\">ഇന്നത്തെ വിശേഷ ദിവസങ്ങൾ - വ്രതം, ഉത്സവം, പൂജാ സമയം</p>",
        "hub.upcoming": "അടുത്ത 30 ദിവസം",
        "year.title": "വ്രതങ്ങളും ഉത്സവങ്ങളും {year}: തീയതികളും മുഹൂർത്തവും (ന്യൂഡൽഹി)",
        "year.h1": "വ്രത-ഉത്സവ കലണ്ടർ {year}",
        "year.desc": ("{year}-ലെ എല്ലാ ഹിന്ദു വ്രതങ്ങളും ഉത്സവങ്ങളും മാസം തിരിച്ച് - ഏകാദശി, പ്രദോഷം, "
                      "സങ്കഷ്ടി, പൗർണമി, അമാവാസി, ശിവരാത്രി, ദീപാവലി, നവരാത്രി, രക്ഷാബന്ധൻ തുടങ്ങിയ "
                      "ഉത്സവങ്ങൾ, ന്യൂഡൽഹിയിലെ പൂജാ മുഹൂർത്തം സഹിതം."),
        "year.intro": ("<p>{year}-ൽ ന്യൂഡൽഹിക്കായി <strong>{count}</strong> വ്രതങ്ങളും ഉത്സവങ്ങളും, "
                       "പഞ്ചാംഗത്തിൽ നിന്ന് കണക്കാക്കിയത്. ഒരു പ്രധാന ഉത്സവത്തിൽ തൊട്ടാൽ അതിന്റെ പൂജാ "
                       "മുഹൂർത്തവും വിവരണവും കാണാം.</p>"),
        "year.month": "{month} {year}",
        "year.itemlist": "പ്രധാന ഹിന്ദു ഉത്സവങ്ങൾ {year}",
        "ek.title": "ഏകാദശി {year}: എല്ലാ ഏകാദശി വ്രത തീയതികളും പാരണ സമയവും (ന്യൂഡൽഹി)",
        "ek.h1": "ഏകാദശി {year}: തീയതികളും പാരണ സമയവും",
        "ek.desc": ("{year}-ലെ എല്ലാ {count} ഏകാദശികളും - വ്രത ദിവസം, ഏകാദശി തിഥി സമയം, പിറ്റേന്നത്തെ "
                    "പാരണ (വ്രതം മുറിക്കൽ) സമയം, ന്യൂഡൽഹിക്ക്."),
        "ek.th": "<tr><th>ഏകാദശി</th><th>വ്രതം</th><th>പാരണ</th></tr>",
        "ek.rule": ("<p><strong>നിയമം (സ്മാർത്തം):</strong> സൂര്യോദയ സമയത്ത് ഏകാദശിയുള്ള ദിവസം വ്രതം; "
                    "രണ്ട് സൂര്യോദയങ്ങളിൽ ഉണ്ടെങ്കിൽ രണ്ടാം ദിവസം, ഒരു സൂര്യോദയത്തിലും ഇല്ലെങ്കിൽ ഏകാദശി "
                    "വരുന്ന ദിവസം. പാരണ പിറ്റേന്ന് സൂര്യോദയത്തിനു ശേഷം, ഹരിവാസരം (ദ്വാദശിയുടെ ആദ്യ "
                    "കാൽഭാഗം) കഴിഞ്ഞ്, പ്രാതഃകാലത്തിനുള്ളിൽ, ദ്വാദശി തീരും മുമ്പ്; ഹരിവാസരം പ്രാതഃകാലം "
                    "കടന്നും നീണ്ടാൽ പാരണ അപരാഹ്നത്തിലേക്ക് മാറും (മധ്യാഹ്നം ഒഴിവാക്കും).</p>"),
        "ek.sub": "<p class=\"hi\">ഏകാദശി വ്രതം {year} - തീയതിയും പാരണ സമയവും</p>",
        "ek.crumb": "ഏകാദശി {year}",
        "fest.title": "{name} {year}: തീയതിയും പൂജാ മുഹൂർത്തവും - {short}",
        "fest.h1": "{name} {year}: തീയതിയും മുഹൂർത്തവും",
        "fest.main": "{text}. ",
        "fest.desc": "{name} {year}: {date}, {weekday}. {main}ന്യൂഡൽഹിയിലെ പൂജാ സമയങ്ങൾ.",
        "fest.when": "{name} {year} <strong>{when}</strong> ആണ്.",
        "fest.sub": "<p class=\"hi\">{year} തീയതി, മുഹൂർത്തം, ആചരണ രീതി</p>",
        "fest.about_h2": "എന്താണ്, എങ്ങനെ ആചരിക്കുന്നു",
        "fest.rule_h2": "തീയതി നിശ്ചയിക്കുന്നത് എങ്ങനെ",
        "fest.faq_h2": "പതിവ് ചോദ്യങ്ങൾ",
        "event.place": "ഇന്ത്യ",
        "faq.when_q": "{name} {year} എന്നാണ്?",
        "faq.when_a": "{name} {year} {date}, {weekday} ആണ്.",
        "faq.muhurat_q": "{name} {year} പൂജാ മുഹൂർത്തം എപ്പോൾ?",
        "faq.timings_q": "{name} {year} സമയങ്ങൾ എന്തൊക്കെ?",
        "faq.timings_a": ("ന്യൂഡൽഹിക്ക് - {timings}. സമയം നഗരമനുസരിച്ച് ഏതാനും മിനിറ്റ് മാറും; നിങ്ങളുടെ "
                          "നഗരത്തിന്റെ പഞ്ചാംഗം നോക്കുക."),
        "faq.why_q": "{name} {year} എന്തുകൊണ്ട് {short}-ന്?",
        "faq.why_a": "തീയതി ഈ നിയമം അനുസരിച്ചാണ്: {rule}. {year}-ൽ അത് {when} ആണ് (ന്യൂഡൽഹി).",
    },

    # Used by a language for a key it has not translated yet, before English.
    "_native": {
        "tithi.paksha": "{paksha} {l_paksha}",
    },
}

# What each major festival is (short, factual, respectful): festival slug -> text.
ABOUT: dict[str, dict[str, str]] = {
    "en": {
        "makar-sankranti": ("Makar Sankranti marks the Sun's entry into Makara (Capricorn) and the start of its "
             'northward journey (Uttarayana). It is a harvest festival: people bathe in holy '
             'rivers, give til (sesame), jaggery, khichdi and blankets in charity, and fly kites.'),
        "maha-shivratri": ('Maha Shivratri, the great night of Shiva, falls on the Krishna Chaturdashi of '
             'Magha. Devotees fast, offer water, milk and bel leaves on the Shivling, chant Om '
             'Namah Shivaya and keep vigil through the four prahars of the night; the Nishita '
             'kaal puja around midnight is the most important.'),
        "holika-dahan": ("Holika Dahan, on the eve of Holi, celebrates Prahlad's devotion and the victory of "
             'good over evil. A bonfire is lit after sunset, avoiding Bhadra, and families circle '
             'it offering grain, coconut and prayers.'),
        "holi": ('Holi, the festival of colours, is celebrated the morning after Holika Dahan with '
             'colours, music, sweets like gujiya and visits to family and friends.'),
        "ram-navami": ('Ram Navami celebrates the birth of Lord Rama on Chaitra Shukla Navami, at midday. '
             'Devotees fast, read the Ramcharitmanas, and offer puja in the Madhyahna muhurat, '
             'the time of his birth.'),
        "hanuman-jayanti": ('Hanuman Jayanti (Chaitra Purnima in North India) celebrates the birth of Lord '
             'Hanuman. Devotees visit Hanuman temples, recite the Hanuman Chalisa and Sundarkand, '
             'and offer sindoor and laddoos.'),
        "akshaya-tritiya": ('Akshaya Tritiya, Vaishakha Shukla Tritiya, is held to make every good deed '
             "'akshaya' - undiminishing. People worship Vishnu and Lakshmi, give in charity, and "
             'begin new ventures or buy gold.'),
        "raksha-bandhan": ('Raksha Bandhan, on Shravana Purnima, celebrates the bond between brothers and '
             "sisters. Sisters tie a rakhi on their brother's wrist and pray for his well-being; "
             'the rakhi is tied in a time free of Bhadra.'),
        "janmashtami": ('Krishna Janmashtami celebrates the birth of Lord Krishna at midnight on Krishna '
             'Ashtami of Bhadrapada (purnimanta). Devotees fast through the day and break it '
             'after the Nishita (midnight) puja, when the infant Krishna is bathed and placed in '
             'a cradle.'),
        "ganesh-chaturthi": ('Ganesh Chaturthi, Bhadrapada Shukla Chaturthi, welcomes Lord Ganesha home. The idol '
             'is installed and worshipped in the Madhyahna (midday) muhurat, the time of his '
             'birth, with modak, durva grass and red flowers; looking at the Moon on this day is '
             'avoided.'),
        "chaitra-navratri": ('Chaitra Navratri, the nine nights of Goddess Durga in spring, begins on Chaitra '
             'Shukla Pratipada - also the Hindu New Year (Vikram Samvat). Ghatasthapana '
             '(installing the kalash) opens the nine days of worship.'),
        "navratri": ('Sharad Navratri, the nine nights of Goddess Durga in autumn, begins on Ashwin '
             'Shukla Pratipada with Ghatasthapana - installing the kalash and sowing barley - in '
             'the morning. Each day honours one of the nine forms of the Goddess.'),
        "dussehra": ("Dussehra (Vijayadashami) marks Lord Rama's victory over Ravana and Goddess Durga's "
             'over Mahishasura. Shami puja, Aparajita puja and the burning of Ravana effigies are '
             'held in the afternoon; the Vijay muhurat is considered good for starting anything '
             'new.'),
        "karwa-chauth": ('On Karwa Chauth married women keep a fast from sunrise to moonrise for their '
             "husbands' long life. The evening puja of Karwa Mata is followed by offering water "
             '(arghya) to the Moon, after which the fast is broken.'),
        "ahoi-ashtami": ('On Ahoi Ashtami, eight days before Diwali, mothers keep a fast for the well-being '
             'of their children and worship Ahoi Mata in the evening; the fast is traditionally '
             'broken after sighting the stars (or, in some families, the Moon).'),
        "dhanteras": ('Dhanteras, the first day of Diwali, honours Dhanvantari and Goddess Lakshmi. People '
             'buy new utensils, gold or silver and light the Yama deepak at dusk; the puja is '
             'done in Pradosh kaal, ideally in the fixed (sthir) Vrishabha lagna.'),
        "diwali": ('Diwali, on Kartika Amavasya, is the festival of lights. Lakshmi and Ganesha are '
             'worshipped in the evening - in Pradosh kaal, preferably in the fixed (sthir) '
             'Vrishabha lagna so that prosperity stays - and homes are lit with diyas.'),
        "govardhan-puja": ('Govardhan Puja (Annakut), the day after Diwali, remembers Krishna lifting Govardhan '
             'hill. A Govardhan of cow-dung or food is worshipped and an annakut of many dishes '
             'is offered, usually in the morning (Pratahkala).'),
        "bhai-dooj": ('Bhai Dooj, Kartika Shukla Dwitiya, celebrates brothers and sisters: sisters apply a '
             "tilak, perform aarti and pray for their brother's long life, ideally in the "
             'Aparahna (afternoon) time.'),
        "chhath-puja": ('Chhath Puja worships the Sun God and Chhathi Maiya over four days. On the main day '
             '(Kartika Shukla Shashthi) devotees stand in water and offer arghya to the setting '
             'Sun, and to the rising Sun the next morning, ending a fast kept without water.'),
        "vasant-panchami": ('Vasant Panchami, Magha Shukla Panchami, welcomes spring and honours Goddess '
             'Saraswati. Students and artists worship books and instruments, people wear yellow, '
             'and children often begin learning to write (vidyarambh).'),
        "guru-purnima": ("Guru Purnima, Ashadha Purnima, honours one's teachers and Maharishi Ved Vyasa, born "
             'on this day. Disciples offer gratitude, flowers and gifts to their guru.'),
        "sharad-purnima": ('Sharad Purnima, Ashwin Purnima, is the night the Moon is held to be brightest and '
             'full of nectar. Kheer is kept in the moonlight overnight and eaten as prasad; '
             'Lakshmi is worshipped (Kojagari).'),
        "devuthani-ekadashi": ('Devuthani (Prabodhini) Ekadashi, Kartika Shukla Ekadashi, is when Lord Vishnu is '
             'held to wake from his four-month sleep, ending Chaturmas. Tulsi vivah begins and '
             'the wedding season opens. Devotees fast and break the fast (parana) the next day.'),
        "jivitputrika": ('Jivitputrika (Jitiya, Jiutiya) is kept by mothers in Bihar, Jharkhand, eastern '
             'Uttar Pradesh and Nepal for the long life and well-being of their children, on '
             'Ashwin Krishna Ashtami (purnimanta). It begins with nahay-khay the day before; the '
             'fast itself is nirjala, without water, through the day and night, with worship of '
             'Jimutavahana and the Jitiya katha. Parana, breaking the fast, is the next morning.'),
        "lohri": ('Lohri, the evening before Makar Sankranti, is the winter harvest festival of Punjab '
             'and North India. A bonfire is lit at dusk and people offer til, gur, rewari, '
             'peanuts and popcorn to it, sing and dance; it is especially celebrated for a new '
             'bride or a newborn.'),
        "sakat-chauth": ('Sakat Chauth (Tilkut Chauth), the Sankashti Chaturthi of Magha (purnimanta), is '
             'kept by mothers for their children. Ganesha and Sakat Mata are worshipped with til '
             'and jaggery, and the fast is broken after offering arghya to the rising Moon.'),
        "mauni-amavasya": ('Mauni Amavasya, the Amavasya of Magha (purnimanta), is the great bathing day of the '
             'Magh Mela at Prayagraj. Devotees bathe in the Ganga or a holy river, keep silence '
             '(mauna) and give in charity.'),
        "sheetala-ashtami": ('Sheetala Ashtami (Basoda), Chaitra Krishna Ashtami (purnimanta), honours Sheetala '
             'Mata, the goddess who protects from fevers and pox. Food is cooked the day before '
             'and the stale (basi) food is offered and eaten; no fire is lit for cooking that day.'),
        "gudi-padwa": ('Gudi Padwa (Maharashtra) and Ugadi (Karnataka, Andhra Pradesh, Telangana) mark the '
             'lunar New Year on Chaitra Shukla Pratipada. A gudi - a decorated pole with a cloth '
             'and kalash - is raised at the door, and neem with jaggery is eaten for a year of '
             'both sweet and bitter.'),
        "gangaur": ("Gangaur, Chaitra Shukla Tritiya, is Rajasthan's festival of Gauri (Parvati) and "
             'Shiva. Women worship Gauri for marital happiness - married women for their '
             'husbands, girls for a good match - ending eighteen days of puja that begin the day '
             'after Holi.'),
        "vat-savitri": ('Vat Savitri Vrat, on Jyeshtha Amavasya in North India (purnimanta), remembers '
             "Savitri, who won back her husband Satyavan's life from Yama. Married women fast, "
             'worship the banyan (vat) tree, tie raw thread around it while circling it, and hear '
             'the Savitri katha.'),
        "vat-purnima": ('Vat Purnima is the same Vat Savitri vrat as kept on Jyeshtha Purnima in '
             'Maharashtra, Gujarat and the south (amanta calendar), fifteen days after the North '
             "Indian date. Married women fast and worship the banyan tree for their husbands' "
             'long life.'),
        "ganga-dussehra": ('Ganga Dussehra, Jyeshtha Shukla Dashami, celebrates the descent of the Ganga to '
             "earth through Bhagiratha's penance. Devotees bathe in the Ganga, offer lamps and "
             'give in charity; the bath is held to wash away ten kinds of sin.'),
        "hariyali-teej": ('Hariyali Teej, Shravana Shukla Tritiya, celebrates the reunion of Shiva and Parvati '
             'in the monsoon. Women wear green, apply mehndi, swing on decorated jhoolas, sing '
             'Sawan songs and many keep a fast for their husbands.'),
        "nag-panchami": ('Nag Panchami, Shravana Shukla Panchami, is the day serpent deities (nagas) are '
             'worshipped. Images of snakes are drawn or installed and offered milk, flowers and '
             "sweets, with prayers for the family's protection. (In Gujarat, Nag Pancham falls "
             'later, in Bhadrapada.)'),
        "kajari-teej": ('Kajari (Kajli, Badi) Teej, Bhadrapada Krishna Tritiya (purnimanta), is kept by '
             'married women of Uttar Pradesh, Bihar, Rajasthan and Madhya Pradesh. They fast, '
             'worship the neem tree (Neemadi Mata) and break the fast after offering arghya to '
             'the Moon; kajari folk songs are sung.'),
        "hal-shashthi": ('Hal Shashthi (Lalahi Chhath, Har Chhath), Bhadrapada Krishna Shashthi (purnimanta), '
             "is Lord Balarama's birthday, whose weapon is the plough (hal). Mothers fast for "
             'their children and eat nothing grown with a plough - often pasahi rice and buffalo '
             'milk.'),
        "hartalika-teej": ("Hartalika Teej, Bhadrapada Shukla Tritiya, honours Parvati's penance to win Shiva. "
             'Women keep a nirjala fast, make clay images of Shiva and Parvati, worship them '
             '(morning puja in Pratahkala is preferred), keep vigil at night and break the fast '
             'next morning.'),
        "rishi-panchami": ('Rishi Panchami, Bhadrapada Shukla Panchami, honours the Saptarishis, the seven '
             'sages. Women in particular bathe, fast and worship the sages at midday (Madhyahna), '
             'seeking purification from faults committed unknowingly.'),
        "anant-chaturdashi": ('Anant Chaturdashi, Bhadrapada Shukla Chaturdashi, is the worship of Lord Vishnu as '
             'Anant. A sacred thread with fourteen knots (the anant sutra) is tied on the arm '
             'after puja; it is also the day Ganesh idols are immersed (Ganesh Visarjan).'),
        "pitru-paksha": ('Pitru Paksha, the fortnight of the ancestors, runs from Pratipada to Amavasya of '
             "the dark half of Ashwin (purnimanta). On the tithi of an ancestor's passing, "
             'families offer tarpan and shraddha - pinda, food for Brahmins, cows, crows and dogs '
             '- in the Kutup, Rohina or Aparahna time.'),
        "sarva-pitru-amavasya": ('Sarva Pitru Amavasya (Mahalaya Amavasya) closes Pitru Paksha. Shraddha on this day '
             'reaches all ancestors, including those whose tithi is not known; it is done in the '
             'Kutup, Rohina or Aparahna time.'),
        "narak-chaturdashi": ('Narak Chaturdashi (Roop Chaudas), Kartika Krishna Chaturdashi (purnimanta), '
             "remembers Krishna's victory over Narakasura. Before sunrise, while the Moon is up, "
             'people take an oil bath with ubtan (Abhyang snan), and a lamp for Yama is lit in '
             'the evening.'),
        "tulsi-vivah": ('Tulsi Vivah, on Kartika Shukla Dwadashi, is the ceremonial wedding of the tulsi '
             'plant (as Vrinda) to Lord Vishnu as Shaligram. Families decorate the tulsi like a '
             'bride and perform the rites of a wedding; the Hindu wedding season begins after it.'),
        "kartik-purnima": ('Kartik Purnima ends the holy month of Kartika. It is a great day for bathing in the '
             'Ganga or a holy river and giving in charity, and also Guru Nanak Jayanti and '
             'Tripuri Purnima, when Shiva destroyed Tripurasura.'),
        "dev-deepawali": ("Dev Deepawali, the 'Diwali of the gods', is celebrated on Kartik Purnima evening, "
             'above all on the ghats of Varanasi, which are lit with lakhs of diyas. It marks '
             "Shiva's victory over Tripurasura; lamps are offered to the Ganga in Pradosh kaal."),
    },
    "hi": {
        "makar-sankranti": ('मकर संक्रांति पर सूर्य मकर राशि में प्रवेश करते हैं और उत्तरायण आरंभ होता है। यह '
             'फसल का पर्व है - पवित्र नदियों में स्नान, तिल-गुड़, खिचड़ी व कंबल का दान और '
             'पतंगबाज़ी इसकी पहचान हैं।'),
        "maha-shivratri": ('महाशिवरात्रि फाल्गुन (अमांत माघ) कृष्ण चतुर्दशी को भगवान शिव की महान रात्रि है। '
             'भक्त व्रत रखते हैं, शिवलिंग पर जल, दूध व बेलपत्र चढ़ाते हैं, ॐ नमः शिवाय का जाप '
             'करते हैं और रात्रि के चारों प्रहर जागरण करते हैं; मध्यरात्रि का निशीथ काल पूजन सबसे '
             'महत्वपूर्ण है।'),
        "holika-dahan": ('होलिका दहन, होली की पूर्व संध्या पर, प्रह्लाद की भक्ति और बुराई पर अच्छाई की विजय '
             'का पर्व है। सूर्यास्त के बाद, भद्रा से बचकर, होलिका जलाई जाती है और परिवार परिक्रमा '
             'कर अन्न, नारियल व प्रार्थना अर्पित करते हैं।'),
        "holi": ('रंगों का पर्व होली होलिका दहन की अगली सुबह रंग-गुलाल, संगीत, गुझिया जैसी मिठाइयों '
             'और अपनों से मिलने के साथ मनाया जाता है।'),
        "ram-navami": ('राम नवमी चैत्र शुक्ल नवमी को मध्याह्न में भगवान श्रीराम के जन्म का उत्सव है। भक्त '
             'व्रत रखते हैं, रामचरितमानस का पाठ करते हैं और मध्याह्न मुहूर्त में पूजन करते हैं।'),
        "hanuman-jayanti": ('हनुमान जयंती (उत्तर भारत में चैत्र पूर्णिमा) भगवान हनुमान का जन्मोत्सव है। भक्त '
             'हनुमान मंदिर जाते हैं, हनुमान चालीसा व सुंदरकांड का पाठ करते हैं और सिंदूर व लड्डू '
             'चढ़ाते हैं।'),
        "akshaya-tritiya": ("वैशाख शुक्ल तृतीया, अक्षय तृतीया पर किया गया शुभ कर्म 'अक्षय' माना जाता है। इस दिन "
             'विष्णु-लक्ष्मी पूजन, दान, नए कार्य का आरंभ और सोना खरीदने की परंपरा है।'),
        "raksha-bandhan": ('श्रावण पूर्णिमा को रक्षा बंधन भाई-बहन के स्नेह का पर्व है। बहनें भाई की कलाई पर '
             'राखी बांधकर उसकी कुशलता की प्रार्थना करती हैं; राखी भद्रा रहित समय में बांधी जाती '
             'है।'),
        "janmashtami": ('कृष्ण जन्माष्टमी भाद्रपद कृष्ण अष्टमी की मध्यरात्रि भगवान श्रीकृष्ण के जन्म का '
             'उत्सव है। भक्त दिनभर व्रत रखते हैं और निशीथ (मध्यरात्रि) पूजा में बाल गोपाल का '
             'अभिषेक कर उन्हें पालने में झुलाते हैं।'),
        "ganesh-chaturthi": ('भाद्रपद शुक्ल चतुर्थी, गणेश चतुर्थी पर गणपति का घर में स्वागत होता है। मध्याह्न '
             'मुहूर्त में मूर्ति स्थापना कर मोदक, दूर्वा व लाल फूलों से पूजन किया जाता है; इस दिन '
             'चंद्र दर्शन वर्जित माना जाता है।'),
        "chaitra-navratri": ('चैत्र नवरात्रि, वसंत में माँ दुर्गा की नौ रात्रियां, चैत्र शुक्ल प्रतिपदा से आरंभ '
             'होती हैं - यही हिंदू नववर्ष (विक्रम संवत) भी है। घटस्थापना (कलश स्थापना) से नौ दिन '
             'की पूजा शुरू होती है।'),
        "navratri": ('शारदीय नवरात्रि, शरद ऋतु में माँ दुर्गा की नौ रात्रियां, आश्विन शुक्ल प्रतिपदा को '
             'प्रातः घटस्थापना - कलश स्थापना और जौ बोने - से आरंभ होती है। हर दिन देवी के एक '
             'स्वरूप की पूजा होती है।'),
        "dussehra": ('दशहरा (विजयादशमी) श्रीराम की रावण पर और माँ दुर्गा की महिषासुर पर विजय का पर्व है। '
             'अपराह्न में शमी पूजा, अपराजिता पूजा और रावण दहन होता है; विजय मुहूर्त नए कार्य के '
             'आरंभ के लिए शुभ माना जाता है।'),
        "karwa-chauth": ('करवा चौथ पर सुहागिन स्त्रियां पति की दीर्घायु के लिए सूर्योदय से चंद्रोदय तक व्रत '
             'रखती हैं। संध्या को करवा माता की पूजा के बाद चंद्रमा को अर्घ्य देकर व्रत खोला जाता '
             'है।'),
        "ahoi-ashtami": ('दीपावली से आठ दिन पहले अहोई अष्टमी पर माताएं संतान की कुशलता के लिए व्रत रखती हैं '
             'और संध्या को अहोई माता की पूजा करती हैं; परंपरागत रूप से तारों (कुछ परिवारों में '
             'चंद्रमा) के दर्शन के बाद व्रत खोला जाता है।'),
        "dhanteras": ('धनतेरस, दीपावली का पहला दिन, धन्वंतरि और माँ लक्ष्मी को समर्पित है। लोग नए बर्तन, '
             'सोना-चांदी खरीदते हैं और संध्या को यम दीपक जलाते हैं; पूजन प्रदोष काल में, संभव हो '
             'तो स्थिर वृषभ लग्न में, किया जाता है।'),
        "diwali": ('कार्तिक अमावस्या को दीपावली प्रकाश का पर्व है। संध्या को प्रदोष काल में, संभव हो तो '
             'स्थिर वृषभ लग्न में (ताकि लक्ष्मी स्थिर रहें), लक्ष्मी-गणेश पूजन होता है और घर '
             'दीयों से जगमगाते हैं।'),
        "govardhan-puja": ('गोवर्धन पूजा (अन्नकूट), दीपावली के अगले दिन, श्रीकृष्ण द्वारा गोवर्धन पर्वत उठाने '
             'की स्मृति है। गोबर या अन्न का गोवर्धन बनाकर पूजा जाता है और अनेक व्यंजनों का '
             'अन्नकूट भोग लगता है, प्रायः प्रातःकाल।'),
        "bhai-dooj": ('कार्तिक शुक्ल द्वितीया, भाई दूज पर बहनें भाई को तिलक लगाकर आरती करती हैं और उसकी '
             'लंबी आयु की कामना करती हैं, उत्तम समय अपराह्न है।'),
        "chhath-puja": ('छठ पूजा चार दिन तक सूर्य देव और छठी मैया की उपासना है। मुख्य दिन (कार्तिक शुक्ल '
             'षष्ठी) व्रती जल में खड़े होकर डूबते सूर्य को और अगली सुबह उगते सूर्य को अर्घ्य देकर '
             'निर्जला व्रत पूरा करते हैं।'),
        "vasant-panchami": ('माघ शुक्ल पंचमी, वसंत पंचमी वसंत ऋतु का स्वागत और माँ सरस्वती की पूजा का पर्व है। '
             'विद्यार्थी व कलाकार पुस्तकों और वाद्यों की पूजा करते हैं, पीले वस्त्र पहने जाते हैं '
             'और विद्यारंभ होता है।'),
        "guru-purnima": ('आषाढ़ पूर्णिमा, गुरु पूर्णिमा गुरुजनों और इसी दिन जन्मे महर्षि वेदव्यास को समर्पित '
             'है। शिष्य अपने गुरु के प्रति कृतज्ञता, पुष्प व भेंट अर्पित करते हैं।'),
        "sharad-purnima": ('आश्विन पूर्णिमा, शरद पूर्णिमा की रात चंद्रमा सबसे उज्ज्वल और अमृतमय माना जाता है। '
             'खीर रात भर चांदनी में रखकर प्रसाद रूप में ली जाती है; कोजागरी लक्ष्मी पूजा भी होती '
             'है।'),
        "devuthani-ekadashi": ('देवउठनी (प्रबोधिनी) एकादशी, कार्तिक शुक्ल एकादशी पर भगवान विष्णु चार माह की '
             'योगनिद्रा से जागते हैं और चातुर्मास समाप्त होता है। तुलसी विवाह होता है और विवाह के '
             'मुहूर्त फिर शुरू होते हैं। भक्त व्रत रखकर अगले दिन पारण करते हैं।'),
        "jivitputrika": ('जीवित्पुत्रिका (जितिया, जिउतिया) व्रत बिहार, झारखंड, पूर्वी उत्तर प्रदेश और नेपाल '
             'में माताएं संतान की लंबी आयु और कुशलता के लिए आश्विन कृष्ण अष्टमी (पूर्णिमांत) को '
             'रखती हैं। एक दिन पहले नहाय-खाय होता है; व्रत निर्जला होता है, दिन-रात जल भी ग्रहण '
             'नहीं किया जाता, जीमूतवाहन की पूजा व जितिया कथा होती है। पारण अगली सुबह किया जाता है।'),
        "lohri": ('लोहड़ी, मकर संक्रांति से पहले की शाम, पंजाब और उत्तर भारत का शीतकालीन फसल पर्व है। '
             'संध्या को अलाव जलाकर तिल, गुड़, रेवड़ी, मूंगफली व मक्का अर्पित किए जाते हैं, गीत और '
             'नृत्य होते हैं; नई बहू या नवजात के घर यह विशेष उत्साह से मनाई जाती है।'),
        "sakat-chauth": ('सकट चौथ (तिलकुट चौथ), माघ (पूर्णिमांत) की संकष्टी चतुर्थी, माताएं संतान के लिए रखती '
             'हैं। तिल-गुड़ से गणेश जी और सकट माता की पूजा होती है और चंद्रोदय पर अर्घ्य देकर '
             'व्रत खोला जाता है।'),
        "mauni-amavasya": ('माघ (पूर्णिमांत) की अमावस्या, मौनी अमावस्या प्रयागराज के माघ मेले का प्रमुख स्नान '
             'पर्व है। श्रद्धालु गंगा या पवित्र नदी में स्नान, मौन व्रत और दान करते हैं।'),
        "sheetala-ashtami": ('चैत्र कृष्ण अष्टमी (पूर्णिमांत), शीतला अष्टमी (बसौड़ा) पर शीतला माता की पूजा होती '
             'है, जो रोगों से रक्षा करती हैं। भोजन एक दिन पहले बनाया जाता है और बासी भोजन का भोग '
             'लगाकर ग्रहण किया जाता है; उस दिन चूल्हा नहीं जलाया जाता।'),
        "gudi-padwa": ('चैत्र शुक्ल प्रतिपदा को गुड़ी पड़वा (महाराष्ट्र) और उगादी (कर्नाटक, आंध्र, '
             'तेलंगाना) चांद्र नववर्ष के रूप में मनाए जाते हैं। द्वार पर गुड़ी - वस्त्र व कलश से '
             'सजा डंडा - लगाई जाती है और नीम-गुड़ खाकर वर्ष के मीठे-कड़वे अनुभवों को स्वीकार किया '
             'जाता है।'),
        "gangaur": ('चैत्र शुक्ल तृतीया, गणगौर राजस्थान का गौरी (पार्वती) और शिव का पर्व है। सुहागिनें '
             'पति के लिए और कन्याएं अच्छे वर के लिए गौरी पूजन करती हैं; होली के अगले दिन से चलने '
             'वाली अठारह दिन की पूजा इसी दिन पूर्ण होती है।'),
        "vat-savitri": ('उत्तर भारत में ज्येष्ठ अमावस्या (पूर्णिमांत) को वट सावित्री व्रत सावित्री की स्मृति '
             'है, जिन्होंने यमराज से पति सत्यवान के प्राण वापस पाए। सुहागिनें व्रत रखकर वट वृक्ष '
             'की पूजा करती हैं, कच्चा सूत लपेटते हुए परिक्रमा करती हैं और सावित्री कथा सुनती हैं।'),
        "vat-purnima": ('वट पूर्णिमा वही वट सावित्री व्रत है जो महाराष्ट्र, गुजरात और दक्षिण भारत (अमांत) '
             'में ज्येष्ठ पूर्णिमा को, उत्तर भारत की तिथि से पंद्रह दिन बाद, रखा जाता है। '
             'सुहागिनें पति की दीर्घायु के लिए व्रत रखकर वट वृक्ष की पूजा करती हैं।'),
        "ganga-dussehra": ('ज्येष्ठ शुक्ल दशमी, गंगा दशहरा भगीरथ के तप से गंगा के पृथ्वी पर अवतरण का पर्व है। '
             'श्रद्धालु गंगा स्नान, दीपदान और दान करते हैं; यह स्नान दस प्रकार के पापों को हरने '
             'वाला माना जाता है।'),
        "hariyali-teej": ('श्रावण शुक्ल तृतीया, हरियाली तीज सावन में शिव-पार्वती के मिलन का उत्सव है। '
             'स्त्रियां हरे वस्त्र पहनती हैं, मेहंदी लगाती हैं, झूला झूलती हैं, सावन के गीत गाती '
             'हैं और अनेक पति के लिए व्रत रखती हैं।'),
        "nag-panchami": ('श्रावण शुक्ल पंचमी, नाग पंचमी पर नाग देवताओं की पूजा होती है। नाग की आकृति बनाकर या '
             'स्थापित कर दूध, पुष्प और मिष्ठान्न अर्पित किए जाते हैं और परिवार की रक्षा की '
             'प्रार्थना होती है। (गुजरात में नाग पंचम बाद में, भाद्रपद में होती है।)'),
        "kajari-teej": ('भाद्रपद कृष्ण तृतीया (पूर्णिमांत), कजरी (कजली, बड़ी) तीज उत्तर प्रदेश, बिहार, '
             'राजस्थान और मध्य प्रदेश में सुहागिनें रखती हैं। वे व्रत रखकर नीमड़ी माता की पूजा '
             'करती हैं और चंद्रमा को अर्घ्य देकर व्रत खोलती हैं; कजरी लोकगीत गाए जाते हैं।'),
        "hal-shashthi": ('भाद्रपद कृष्ण षष्ठी (पूर्णिमांत), हल षष्ठी (ललही छठ, हरछठ) हलधर बलराम जी की जयंती '
             'है। माताएं संतान के लिए व्रत रखती हैं और हल से जोती भूमि का अन्न नहीं खातीं - '
             'प्रायः पसही चावल और भैंस का दूध लिया जाता है।'),
        "hartalika-teej": ('भाद्रपद शुक्ल तृतीया, हरतालिका तीज शिव को पाने के लिए पार्वती के तप की स्मृति है। '
             'स्त्रियां निर्जला व्रत रखकर मिट्टी के शिव-पार्वती बनाकर पूजन करती हैं (प्रातःकाल '
             'पूजा उत्तम), रात्रि जागरण करती हैं और अगली सुबह व्रत खोलती हैं।'),
        "rishi-panchami": ('भाद्रपद शुक्ल पंचमी, ऋषि पंचमी सप्तर्षियों को समर्पित है। विशेष रूप से स्त्रियां '
             'स्नान, व्रत और मध्याह्न में सप्तर्षि पूजन करती हैं, ताकि अनजाने में हुए दोषों से '
             'शुद्धि हो।'),
        "anant-chaturdashi": ('भाद्रपद शुक्ल चतुर्दशी, अनंत चतुर्दशी पर भगवान विष्णु के अनंत रूप की पूजा होती है। '
             'पूजा के बाद चौदह गांठों वाला अनंत सूत्र बांह पर बांधा जाता है; इसी दिन गणेश विसर्जन '
             'भी होता है।'),
        "pitru-paksha": ('पितृ पक्ष, पितरों का पखवाड़ा, आश्विन (पूर्णिमांत) कृष्ण प्रतिपदा से अमावस्या तक '
             'चलता है। पूर्वज की मृत्यु तिथि पर परिवार कुतुप, रौहिण या अपराह्न काल में तर्पण और '
             'श्राद्ध - पिंडदान, ब्राह्मण भोजन तथा गाय, कौए व कुत्ते के लिए भोजन - करते हैं।'),
        "sarva-pitru-amavasya": ('सर्व पितृ अमावस्या (महालया अमावस्या) पितृ पक्ष का अंतिम दिन है। इस दिन किया गया '
             'श्राद्ध सभी पितरों तक पहुंचता है, उन तक भी जिनकी तिथि ज्ञात न हो; यह कुतुप, रौहिण '
             'या अपराह्न काल में किया जाता है।'),
        "narak-chaturdashi": ('कार्तिक कृष्ण चतुर्दशी (पूर्णिमांत), नरक चतुर्दशी (रूप चौदस) श्रीकृष्ण की नरकासुर '
             'पर विजय की स्मृति है। सूर्योदय से पहले, चंद्रोदय के बाद, उबटन व तेल से अभ्यंग स्नान '
             'किया जाता है और संध्या को यम का दीपक जलाया जाता है।'),
        "tulsi-vivah": ('कार्तिक शुक्ल द्वादशी को तुलसी विवाह में तुलसी (वृंदा) का शालिग्राम रूप भगवान '
             'विष्णु से विधिवत विवाह कराया जाता है। तुलसी को दुल्हन की तरह सजाकर विवाह की रस्में '
             'की जाती हैं; इसके बाद विवाह के मुहूर्त शुरू होते हैं।'),
        "kartik-purnima": ('कार्तिक पूर्णिमा पवित्र कार्तिक मास का समापन है। यह गंगा या पवित्र नदी में स्नान और '
             'दान का महापर्व है; इसी दिन गुरु नानक जयंती और त्रिपुरी पूर्णिमा (शिव द्वारा '
             'त्रिपुरासुर वध) भी है।'),
        "dev-deepawali": ("देव दीपावली, 'देवताओं की दिवाली', कार्तिक पूर्णिमा की संध्या को, विशेषकर वाराणसी के "
             'घाटों पर लाखों दीयों के साथ मनाई जाती है। यह शिव की त्रिपुरासुर पर विजय का पर्व है; '
             'प्रदोष काल में गंगा को दीपदान किया जाता है।'),
    },
    "kn": {
        "makar-sankranti": ('ಮಕರ ಸಂಕ್ರಾಂತಿಯಂದು ಸೂರ್ಯನು ಮಕರ ರಾಶಿಯನ್ನು ಪ್ರವೇಶಿಸುತ್ತಾನೆ ಮತ್ತು ಅವನ '
             'ಉತ್ತರ ದಿಕ್ಕಿನ ಪಯಣ (ಉತ್ತರಾಯಣ) ಆರಂಭವಾಗುತ್ತದೆ. ಇದು ಸುಗ್ಗಿಯ ಹಬ್ಬ: ಜನರು ಪವಿತ್ರ '
             'ನದಿಗಳಲ್ಲಿ ಸ್ನಾನ ಮಾಡುತ್ತಾರೆ, ಎಳ್ಳು, ಬೆಲ್ಲ, ಕಿಚಡಿ ಮತ್ತು ಕಂಬಳಿಗಳನ್ನು ದಾನ '
             'ಮಾಡುತ್ತಾರೆ ಮತ್ತು ಗಾಳಿಪಟ ಹಾರಿಸುತ್ತಾರೆ.'),
        "maha-shivratri": ('ಮಹಾ ಶಿವರಾತ್ರಿ, ಶಿವನ ಮಹಾ ರಾತ್ರಿ, ಮಾಘ ಕೃಷ್ಣ ಚತುರ್ದಶಿಯಂದು ಬರುತ್ತದೆ. ಭಕ್ತರು '
             'ಉಪವಾಸ ಮಾಡಿ, ಶಿವಲಿಂಗಕ್ಕೆ ನೀರು, ಹಾಲು ಮತ್ತು ಬಿಲ್ವಪತ್ರೆ ಅರ್ಪಿಸುತ್ತಾರೆ, ಓಂ ನಮಃ '
             'ಶಿವಾಯ ಜಪಿಸುತ್ತಾರೆ ಮತ್ತು ರಾತ್ರಿಯ ನಾಲ್ಕು ಪ್ರಹರಗಳಲ್ಲೂ ಜಾಗರಣೆ ಮಾಡುತ್ತಾರೆ; '
             'ಮಧ್ಯರಾತ್ರಿಯ ಸುಮಾರಿನ ನಿಶೀಥ ಕಾಲದ ಪೂಜೆ ಅತ್ಯಂತ ಮುಖ್ಯ.'),
        "holika-dahan": ('ಹೋಳಿಯ ಮುನ್ನಾದಿನದ ಹೋಳಿಕಾ ದಹನ (ಕಾಮದಹನ) ಪ್ರಹ್ಲಾದನ ಭಕ್ತಿಯನ್ನು ಮತ್ತು ಕೆಟ್ಟದರ '
             'ಮೇಲೆ ಒಳ್ಳೆಯದರ ವಿಜಯವನ್ನು ಆಚರಿಸುತ್ತದೆ. ಸೂರ್ಯಾಸ್ತದ ನಂತರ, ಭದ್ರಾವನ್ನು ತಪ್ಪಿಸಿ, '
             'ಬೆಂಕಿ ಹಚ್ಚಲಾಗುತ್ತದೆ; ಕುಟುಂಬಗಳು ಅದರ ಸುತ್ತ ಪ್ರದಕ್ಷಿಣೆ ಹಾಕಿ ಧಾನ್ಯ, ತೆಂಗಿನಕಾಯಿ '
             'ಮತ್ತು ಪ್ರಾರ್ಥನೆ ಅರ್ಪಿಸುತ್ತವೆ.'),
        "holi": ('ಬಣ್ಣಗಳ ಹಬ್ಬ ಹೋಳಿಯನ್ನು ಹೋಳಿಕಾ ದಹನದ ಮರುದಿನ ಬೆಳಿಗ್ಗೆ ಬಣ್ಣಗಳು, ಸಂಗೀತ, ಗುಜಿಯಾದಂತಹ '
             'ಸಿಹಿತಿಂಡಿಗಳು ಮತ್ತು ಕುಟುಂಬ-ಸ್ನೇಹಿತರ ಭೇಟಿಯೊಂದಿಗೆ ಆಚರಿಸಲಾಗುತ್ತದೆ.'),
        "ram-navami": ('ಶ್ರೀ ರಾಮ ನವಮಿ ಚೈತ್ರ ಶುಕ್ಲ ನವಮಿಯಂದು ಮಧ್ಯಾಹ್ನ ಶ್ರೀರಾಮನ ಜನ್ಮವನ್ನು ಆಚರಿಸುತ್ತದೆ. '
             'ಭಕ್ತರು ಉಪವಾಸ ಮಾಡಿ, ರಾಮಚರಿತಮಾನಸವನ್ನು ಪಠಿಸುತ್ತಾರೆ ಮತ್ತು ಅವನ ಜನ್ಮ ಸಮಯವಾದ '
             'ಮಧ್ಯಾಹ್ನ ಮುಹೂರ್ತದಲ್ಲಿ ಪೂಜೆ ಸಲ್ಲಿಸುತ್ತಾರೆ.'),
        "hanuman-jayanti": ('ಹನುಮ ಜಯಂತಿ (ಉತ್ತರ ಭಾರತದಲ್ಲಿ ಚೈತ್ರ ಹುಣ್ಣಿಮೆ) ಹನುಮಂತನ ಜನ್ಮವನ್ನು '
             'ಆಚರಿಸುತ್ತದೆ. ಭಕ್ತರು ಹನುಮಂತನ ದೇವಾಲಯಗಳಿಗೆ ಭೇಟಿ ನೀಡುತ್ತಾರೆ, ಹನುಮಾನ್ ಚಾಲೀಸಾ ಮತ್ತು '
             'ಸುಂದರಕಾಂಡ ಪಠಿಸುತ್ತಾರೆ ಮತ್ತು ಸಿಂದೂರ ಹಾಗೂ ಲಡ್ಡು ಅರ್ಪಿಸುತ್ತಾರೆ.'),
        "akshaya-tritiya": ("ವೈಶಾಖ ಶುಕ್ಲ ತೃತೀಯವಾದ ಅಕ್ಷಯ ತೃತೀಯದಂದು ಮಾಡಿದ ಪ್ರತಿಯೊಂದು ಸತ್ಕಾರ್ಯವೂ "
             "'ಅಕ್ಷಯ' - ಎಂದಿಗೂ ಕ್ಷಯಿಸದ್ದು - ಎಂದು ನಂಬಲಾಗಿದೆ. ಜನರು ವಿಷ್ಣು ಮತ್ತು ಲಕ್ಷ್ಮಿಯನ್ನು "
             'ಪೂಜಿಸುತ್ತಾರೆ, ದಾನ ಮಾಡುತ್ತಾರೆ ಮತ್ತು ಹೊಸ ಕಾರ್ಯಗಳನ್ನು ಆರಂಭಿಸುತ್ತಾರೆ ಅಥವಾ ಚಿನ್ನ '
             'ಖರೀದಿಸುತ್ತಾರೆ.'),
        "raksha-bandhan": ('ಶ್ರಾವಣ ಹುಣ್ಣಿಮೆಯಂದು ಬರುವ ರಕ್ಷಾ ಬಂಧನ ಸಹೋದರ-ಸಹೋದರಿಯರ ಬಾಂಧವ್ಯವನ್ನು '
             'ಆಚರಿಸುತ್ತದೆ. ಸಹೋದರಿಯರು ಸಹೋದರನ ಮಣಿಕಟ್ಟಿಗೆ ರಾಖಿ ಕಟ್ಟಿ ಅವನ ಒಳಿತಿಗಾಗಿ '
             'ಪ್ರಾರ್ಥಿಸುತ್ತಾರೆ; ರಾಖಿಯನ್ನು ಭದ್ರಾ ಇಲ್ಲದ ಸಮಯದಲ್ಲಿ ಕಟ್ಟಲಾಗುತ್ತದೆ.'),
        "janmashtami": ('ಶ್ರೀ ಕೃಷ್ಣ ಜನ್ಮಾಷ್ಟಮಿ ಭಾದ್ರಪದ (ಪೂರ್ಣಿಮಾಂತ) ಕೃಷ್ಣ ಅಷ್ಟಮಿಯ ಮಧ್ಯರಾತ್ರಿ '
             'ಶ್ರೀಕೃಷ್ಣನ ಜನ್ಮವನ್ನು ಆಚರಿಸುತ್ತದೆ. ಭಕ್ತರು ದಿನವಿಡೀ ಉಪವಾಸ ಮಾಡಿ, ನಿಶೀಥ '
             '(ಮಧ್ಯರಾತ್ರಿ) ಪೂಜೆಯಲ್ಲಿ ಬಾಲಕೃಷ್ಣನಿಗೆ ಅಭಿಷೇಕ ಮಾಡಿ ತೊಟ್ಟಿಲಲ್ಲಿ ಇರಿಸಿದ ನಂತರ '
             'ಉಪವಾಸ ಮುಗಿಸುತ್ತಾರೆ.'),
        "ganesh-chaturthi": ('ಭಾದ್ರಪದ ಶುಕ್ಲ ಚತುರ್ಥಿಯಾದ ಗಣೇಶ ಚತುರ್ಥಿಯಂದು ಗಣಪತಿಯನ್ನು ಮನೆಗೆ '
             'ಸ್ವಾಗತಿಸಲಾಗುತ್ತದೆ. ಅವನ ಜನ್ಮ ಸಮಯವಾದ ಮಧ್ಯಾಹ್ನ ಮುಹೂರ್ತದಲ್ಲಿ ಮೂರ್ತಿಯನ್ನು '
             'ಪ್ರತಿಷ್ಠಾಪಿಸಿ ಮೋದಕ, ಗರಿಕೆ ಮತ್ತು ಕೆಂಪು ಹೂವುಗಳಿಂದ ಪೂಜಿಸಲಾಗುತ್ತದೆ; ಈ ದಿನ '
             'ಚಂದ್ರನನ್ನು ನೋಡುವುದನ್ನು ತಪ್ಪಿಸಲಾಗುತ್ತದೆ.'),
        "chaitra-navratri": ('ವಸಂತ ನವರಾತ್ರಿ (ಚೈತ್ರ ನವರಾತ್ರಿ), ವಸಂತ ಋತುವಿನಲ್ಲಿ ದುರ್ಗಾ ದೇವಿಯ ಒಂಬತ್ತು '
             'ರಾತ್ರಿಗಳು, ಚೈತ್ರ ಶುಕ್ಲ ಪ್ರತಿಪದೆಯಂದು ಆರಂಭವಾಗುತ್ತದೆ - ಇದೇ ಹಿಂದೂ ಹೊಸ ವರ್ಷವೂ '
             '(ವಿಕ್ರಮ ಸಂವತ್) ಹೌದು. ಘಟಸ್ಥಾಪನೆಯಿಂದ (ಕಲಶ ಸ್ಥಾಪನೆ) ಒಂಬತ್ತು ದಿನಗಳ ಪೂಜೆ '
             'ಆರಂಭವಾಗುತ್ತದೆ.'),
        "navratri": ('ಶರನ್ನವರಾತ್ರಿ, ಶರದ್ ಋತುವಿನಲ್ಲಿ ದುರ್ಗಾ ದೇವಿಯ ಒಂಬತ್ತು ರಾತ್ರಿಗಳು, ಆಶ್ವಯುಜ ಶುಕ್ಲ '
             'ಪ್ರತಿಪದೆಯಂದು ಬೆಳಿಗ್ಗೆ ಘಟಸ್ಥಾಪನೆಯೊಂದಿಗೆ - ಕಲಶ ಸ್ಥಾಪಿಸಿ ಜವೆಗೋಧಿ ಬಿತ್ತುವುದರೊಂದಿಗೆ '
             '- ಆರಂಭವಾಗುತ್ತದೆ. ಪ್ರತಿ ದಿನ ದೇವಿಯ ಒಂಬತ್ತು ರೂಪಗಳಲ್ಲಿ ಒಂದನ್ನು ಪೂಜಿಸಲಾಗುತ್ತದೆ.'),
        "dussehra": ('ವಿಜಯದಶಮಿ (ದಸರಾ) ರಾವಣನ ಮೇಲೆ ಶ್ರೀರಾಮನ ಮತ್ತು ಮಹಿಷಾಸುರನ ಮೇಲೆ ದುರ್ಗಾ ದೇವಿಯ '
             'ವಿಜಯವನ್ನು ಸೂಚಿಸುತ್ತದೆ. ಶಮೀ ಪೂಜೆ, ಅಪರಾಜಿತಾ ಪೂಜೆ ಮತ್ತು ರಾವಣನ ಪ್ರತಿಕೃತಿ ದಹನ '
             'ಅಪರಾಹ್ನದಲ್ಲಿ ನಡೆಯುತ್ತವೆ; ವಿಜಯ ಮುಹೂರ್ತವನ್ನು ಯಾವುದೇ ಹೊಸ ಕಾರ್ಯ ಆರಂಭಿಸಲು '
             'ಶುಭವೆಂದು ಪರಿಗಣಿಸಲಾಗುತ್ತದೆ.'),
        "karwa-chauth": ('ಕರ್ವಾ ಚೌತ್ ದಿನ ವಿವಾಹಿತ ಮಹಿಳೆಯರು ಪತಿಯ ದೀರ್ಘಾಯುಷ್ಯಕ್ಕಾಗಿ ಸೂರ್ಯೋದಯದಿಂದ '
             'ಚಂದ್ರೋದಯದವರೆಗೆ ಉಪವಾಸ ಮಾಡುತ್ತಾರೆ. ಸಂಜೆ ಕರ್ವಾ ಮಾತೆಯ ಪೂಜೆಯ ನಂತರ ಚಂದ್ರನಿಗೆ '
             'ಅರ್ಘ್ಯ (ನೀರು) ಅರ್ಪಿಸಿ ಉಪವಾಸ ಮುಗಿಸಲಾಗುತ್ತದೆ.'),
        "ahoi-ashtami": ('ದೀಪಾವಳಿಗೆ ಎಂಟು ದಿನ ಮೊದಲು ಬರುವ ಅಹೋಯಿ ಅಷ್ಟಮಿಯಂದು ತಾಯಂದಿರು ಮಕ್ಕಳ ಒಳಿತಿಗಾಗಿ '
             'ಉಪವಾಸ ಮಾಡಿ ಸಂಜೆ ಅಹೋಯಿ ಮಾತೆಯನ್ನು ಪೂಜಿಸುತ್ತಾರೆ; ಸಂಪ್ರದಾಯದಂತೆ ನಕ್ಷತ್ರಗಳನ್ನು '
             '(ಕೆಲವು ಕುಟುಂಬಗಳಲ್ಲಿ ಚಂದ್ರನನ್ನು) ನೋಡಿದ ನಂತರ ಉಪವಾಸ ಮುಗಿಸಲಾಗುತ್ತದೆ.'),
        "dhanteras": ('ದೀಪಾವಳಿಯ ಮೊದಲ ದಿನವಾದ ಧನ ತ್ರಯೋದಶಿ ಧನ್ವಂತರಿ ಮತ್ತು ಲಕ್ಷ್ಮೀ ದೇವಿಗೆ ಸಮರ್ಪಿತ. '
             'ಜನರು ಹೊಸ ಪಾತ್ರೆಗಳು, ಚಿನ್ನ ಅಥವಾ ಬೆಳ್ಳಿ ಖರೀದಿಸುತ್ತಾರೆ ಮತ್ತು ಸಂಜೆ ಯಮ ದೀಪ '
             'ಹಚ್ಚುತ್ತಾರೆ; ಪೂಜೆಯನ್ನು ಪ್ರದೋಷ ಕಾಲದಲ್ಲಿ, ಸಾಧ್ಯವಾದರೆ ಸ್ಥಿರ ವೃಷಭ ಲಗ್ನದಲ್ಲಿ '
             'ಮಾಡಲಾಗುತ್ತದೆ.'),
        "diwali": ('ಕಾರ್ತಿಕ ಅಮಾವಾಸ್ಯೆಯಂದು ಬರುವ ದೀಪಾವಳಿ ಬೆಳಕಿನ ಹಬ್ಬ. ಸಂಜೆ ಪ್ರದೋಷ ಕಾಲದಲ್ಲಿ - ಸಮೃದ್ಧಿ '
             'ನೆಲೆಸಲೆಂದು ಸಾಧ್ಯವಾದರೆ ಸ್ಥಿರ ವೃಷಭ ಲಗ್ನದಲ್ಲಿ - ಲಕ್ಷ್ಮೀ ಮತ್ತು ಗಣೇಶರನ್ನು '
             'ಪೂಜಿಸಲಾಗುತ್ತದೆ ಮತ್ತು ಮನೆಗಳನ್ನು ಹಣತೆಗಳಿಂದ ಬೆಳಗಿಸಲಾಗುತ್ತದೆ.'),
        "govardhan-puja": ('ದೀಪಾವಳಿಯ ಮರುದಿನದ ಗೋವರ್ಧನ ಪೂಜೆ (ಅನ್ನಕೂಟ) ಶ್ರೀಕೃಷ್ಣನು ಗೋವರ್ಧನ ಗಿರಿಯನ್ನು '
             'ಎತ್ತಿದುದನ್ನು ಸ್ಮರಿಸುತ್ತದೆ. ಸಗಣಿ ಅಥವಾ ಆಹಾರದಿಂದ ಮಾಡಿದ ಗೋವರ್ಧನವನ್ನು ಪೂಜಿಸಿ, '
             'ಅನೇಕ ಭಕ್ಷ್ಯಗಳ ಅನ್ನಕೂಟವನ್ನು ಸಾಮಾನ್ಯವಾಗಿ ಬೆಳಿಗ್ಗೆ (ಪ್ರಾತಃಕಾಲ) ಅರ್ಪಿಸಲಾಗುತ್ತದೆ.'),
        "bhai-dooj": ('ಕಾರ್ತಿಕ ಶುಕ್ಲ ದ್ವಿತೀಯಾದ ಭಾಯಿ ದೂಜ್ ಸಹೋದರ-ಸಹೋದರಿಯರ ಹಬ್ಬ: ಸಹೋದರಿಯರು '
             'ತಿಲಕವಿಟ್ಟು, ಆರತಿ ಮಾಡಿ ಸಹೋದರನ ದೀರ್ಘಾಯುಷ್ಯಕ್ಕಾಗಿ ಪ್ರಾರ್ಥಿಸುತ್ತಾರೆ; ಅಪರಾಹ್ನದ '
             '(ಮಧ್ಯಾಹ್ನದ ನಂತರದ) ಸಮಯ ಉತ್ತಮ.'),
        "chhath-puja": ('ಛಠ್ ಪೂಜೆ ನಾಲ್ಕು ದಿನಗಳ ಕಾಲ ಸೂರ್ಯ ದೇವ ಮತ್ತು ಛಠೀ ಮಾತೆಯ ಆರಾಧನೆ. ಮುಖ್ಯ ದಿನದಂದು '
             '(ಕಾರ್ತಿಕ ಶುಕ್ಲ ಷಷ್ಠಿ) ಭಕ್ತರು ನೀರಿನಲ್ಲಿ ನಿಂತು ಅಸ್ತಮಿಸುವ ಸೂರ್ಯನಿಗೆ, ಮತ್ತು ಮರುದಿನ '
             'ಬೆಳಿಗ್ಗೆ ಉದಯಿಸುವ ಸೂರ್ಯನಿಗೆ ಅರ್ಘ್ಯ ಅರ್ಪಿಸಿ, ನೀರನ್ನೂ ಸೇವಿಸದೆ ಮಾಡಿದ ಉಪವಾಸವನ್ನು '
             'ಮುಗಿಸುತ್ತಾರೆ.'),
        "vasant-panchami": ('ಮಾಘ ಶುಕ್ಲ ಪಂಚಮಿಯಾದ ವಸಂತ ಪಂಚಮಿ ವಸಂತ ಋತುವನ್ನು ಸ್ವಾಗತಿಸುತ್ತದೆ ಮತ್ತು '
             'ಸರಸ್ವತಿ ದೇವಿಯನ್ನು ಗೌರವಿಸುತ್ತದೆ. ವಿದ್ಯಾರ್ಥಿಗಳು ಮತ್ತು ಕಲಾವಿದರು ಪುಸ್ತಕಗಳು ಮತ್ತು '
             'ವಾದ್ಯಗಳನ್ನು ಪೂಜಿಸುತ್ತಾರೆ, ಜನರು ಹಳದಿ ಬಟ್ಟೆ ಧರಿಸುತ್ತಾರೆ ಮತ್ತು ಮಕ್ಕಳು ಅನೇಕ ವೇಳೆ '
             'ಅಕ್ಷರಾಭ್ಯಾಸ (ವಿದ್ಯಾರಂಭ) ಆರಂಭಿಸುತ್ತಾರೆ.'),
        "guru-purnima": ('ಆಷಾಢ ಹುಣ್ಣಿಮೆಯಾದ ಗುರು ಪೂರ್ಣಿಮೆ ಗುರುಗಳನ್ನು ಮತ್ತು ಈ ದಿನ ಜನಿಸಿದ ಮಹರ್ಷಿ '
             'ವೇದವ್ಯಾಸರನ್ನು ಗೌರವಿಸುತ್ತದೆ. ಶಿಷ್ಯರು ತಮ್ಮ ಗುರುವಿಗೆ ಕೃತಜ್ಞತೆ, ಹೂವುಗಳು ಮತ್ತು '
             'ಕಾಣಿಕೆಗಳನ್ನು ಅರ್ಪಿಸುತ್ತಾರೆ.'),
        "sharad-purnima": ('ಆಶ್ವಯುಜ ಹುಣ್ಣಿಮೆಯಾದ ಶರದ್ ಪೂರ್ಣಿಮೆಯ ರಾತ್ರಿ ಚಂದ್ರನು ಅತ್ಯಂತ ಪ್ರಕಾಶಮಾನನಾಗಿ, '
             'ಅಮೃತಮಯನಾಗಿ ಇರುತ್ತಾನೆ ಎಂದು ನಂಬಲಾಗಿದೆ. ಖೀರನ್ನು (ಹಾಲಿನ ಪಾಯಸ) ರಾತ್ರಿಯಿಡೀ '
             'ಬೆಳದಿಂಗಳಲ್ಲಿ ಇಟ್ಟು ಪ್ರಸಾದವಾಗಿ ಸೇವಿಸಲಾಗುತ್ತದೆ; ಲಕ್ಷ್ಮಿಯನ್ನು ಪೂಜಿಸಲಾಗುತ್ತದೆ '
             '(ಕೋಜಾಗರಿ).'),
        "devuthani-ekadashi": ('ಕಾರ್ತಿಕ ಶುಕ್ಲ ಏಕಾದಶಿಯಾದ ಉತ್ಥಾನ (ಪ್ರಬೋಧಿನಿ) ಏಕಾದಶಿಯಂದು ಭಗವಾನ್ '
             'ವಿಷ್ಣು ನಾಲ್ಕು ತಿಂಗಳ ನಿದ್ರೆಯಿಂದ ಏಳುತ್ತಾನೆ ಎಂದು ನಂಬಲಾಗಿದೆ; ಇದರೊಂದಿಗೆ ಚಾತುರ್ಮಾಸ '
             'ಮುಗಿಯುತ್ತದೆ. ತುಳಸಿ ವಿವಾಹ ಆರಂಭವಾಗುತ್ತದೆ ಮತ್ತು ಮದುವೆಗಳ ಕಾಲ ಶುರುವಾಗುತ್ತದೆ. '
             'ಭಕ್ತರು ಉಪವಾಸ ಮಾಡಿ ಮರುದಿನ ಪಾರಣೆ (ಉಪವಾಸ ಮುಕ್ತಾಯ) ಮಾಡುತ್ತಾರೆ.'),
        "jivitputrika": ('ಜೀವಿತ್ಪುತ್ರಿಕಾ ವ್ರತವನ್ನು (ಜಿತಿಯಾ, ಜಿಉತಿಯಾ) ಬಿಹಾರ, ಜಾರ್ಖಂಡ್, ಪೂರ್ವ ಉತ್ತರ '
             'ಪ್ರದೇಶ ಮತ್ತು ನೇಪಾಳದ ತಾಯಂದಿರು ಮಕ್ಕಳ ದೀರ್ಘಾಯುಷ್ಯ ಮತ್ತು ಒಳಿತಿಗಾಗಿ ಆಶ್ವಯುಜ ಕೃಷ್ಣ '
             'ಅಷ್ಟಮಿಯಂದು (ಪೂರ್ಣಿಮಾಂತ) ಆಚರಿಸುತ್ತಾರೆ. ಇದು ಹಿಂದಿನ ದಿನದ ನಹಾಯ್-ಖಾಯ್ ಆಚರಣೆಯೊಂದಿಗೆ '
             'ಆರಂಭವಾಗುತ್ತದೆ; ಉಪವಾಸವು ನಿರ್ಜಲ - ಹಗಲು ರಾತ್ರಿ ನೀರನ್ನೂ ಸೇವಿಸದೆ - ಜೀಮೂತವಾಹನನ '
             'ಪೂಜೆ ಮತ್ತು ಜಿತಿಯಾ ಕಥೆಯೊಂದಿಗೆ. ಪಾರಣೆ, ಅಂದರೆ ಉಪವಾಸ ಮುಕ್ತಾಯ, ಮರುದಿನ ಬೆಳಿಗ್ಗೆ.'),
        "lohri": ('ಮಕರ ಸಂಕ್ರಾಂತಿಯ ಹಿಂದಿನ ಸಂಜೆಯ ಲೋಹ್ರಿ ಪಂಜಾಬ್ ಮತ್ತು ಉತ್ತರ ಭಾರತದ ಚಳಿಗಾಲದ ಸುಗ್ಗಿ '
             'ಹಬ್ಬ. ಸಂಜೆ ಬೆಂಕಿ ಹಚ್ಚಿ ಜನರು ಅದಕ್ಕೆ ಎಳ್ಳು, ಬೆಲ್ಲ, ರೇವಡಿ, ಕಡಲೆಕಾಯಿ ಮತ್ತು ಜೋಳದ '
             'ಅರಳು ಅರ್ಪಿಸುತ್ತಾರೆ, ಹಾಡುತ್ತಾರೆ ಮತ್ತು ಕುಣಿಯುತ್ತಾರೆ; ಹೊಸ ವಧು ಅಥವಾ ನವಜಾತ '
             'ಶಿಶುವಿಗಾಗಿ ಇದನ್ನು ವಿಶೇಷವಾಗಿ ಆಚರಿಸಲಾಗುತ್ತದೆ.'),
        "sakat-chauth": ('ಸಕಟ್ ಚೌತ್ (ತಿಲಕುಟ್ ಚೌತ್), ಮಾಘ (ಪೂರ್ಣಿಮಾಂತ) ಮಾಸದ ಸಂಕಷ್ಟಹರ ಚತುರ್ಥಿ, '
             'ತಾಯಂದಿರು ಮಕ್ಕಳಿಗಾಗಿ ಆಚರಿಸುವ ವ್ರತ. ಎಳ್ಳು ಮತ್ತು ಬೆಲ್ಲದಿಂದ ಗಣೇಶ ಮತ್ತು ಸಕಟ್ '
             'ಮಾತೆಯನ್ನು ಪೂಜಿಸಿ, ಉದಯಿಸುವ ಚಂದ್ರನಿಗೆ ಅರ್ಘ್ಯ ಅರ್ಪಿಸಿದ ನಂತರ ಉಪವಾಸ '
             'ಮುಗಿಸಲಾಗುತ್ತದೆ.'),
        "mauni-amavasya": ('ಮಾಘ (ಪೂರ್ಣಿಮಾಂತ) ಮಾಸದ ಅಮಾವಾಸ್ಯೆಯಾದ ಮೌನಿ ಅಮಾವಾಸ್ಯೆ ಪ್ರಯಾಗರಾಜದ ಮಾಘ '
             'ಮೇಳದ ಪ್ರಮುಖ ಸ್ನಾನದ ದಿನ. ಭಕ್ತರು ಗಂಗೆ ಅಥವಾ ಪವಿತ್ರ ನದಿಯಲ್ಲಿ ಸ್ನಾನ ಮಾಡಿ, ಮೌನ '
             'ಪಾಲಿಸಿ ದಾನ ಮಾಡುತ್ತಾರೆ.'),
        "sheetala-ashtami": ('ಚೈತ್ರ ಕೃಷ್ಣ ಅಷ್ಟಮಿಯ (ಪೂರ್ಣಿಮಾಂತ) ಶೀತಲಾ ಅಷ್ಟಮಿ (ಬಸೋಡಾ) ಜ್ವರ ಮತ್ತು '
             'ಸಿಡುಬಿನಿಂದ ರಕ್ಷಿಸುವ ಶೀತಲಾ ಮಾತೆಯನ್ನು ಗೌರವಿಸುತ್ತದೆ. ಹಿಂದಿನ ದಿನವೇ ಅಡುಗೆ ಮಾಡಿ, ಆ '
             'ಹಳೆಯ (ಬಾಸಿ) ಆಹಾರವನ್ನು ನೈವೇದ್ಯ ಮಾಡಿ ಸೇವಿಸಲಾಗುತ್ತದೆ; ಆ ದಿನ ಅಡುಗೆಗೆ ಒಲೆ '
             'ಹಚ್ಚುವುದಿಲ್ಲ.'),
        "gudi-padwa": ('ಯುಗಾದಿ (ಕರ್ನಾಟಕ, ಆಂಧ್ರ ಪ್ರದೇಶ, ತೆಲಂಗಾಣ) ಮತ್ತು ಗುಡಿ ಪಾಡ್ವಾ (ಮಹಾರಾಷ್ಟ್ರ) ಚೈತ್ರ '
             'ಶುಕ್ಲ ಪ್ರತಿಪದೆಯಂದು ಚಾಂದ್ರಮಾನ ಹೊಸ ವರ್ಷವನ್ನು ಸೂಚಿಸುತ್ತವೆ. ಬಾಗಿಲಲ್ಲಿ ಗುಡಿ - '
             'ಬಟ್ಟೆ ಮತ್ತು ಕಲಶದಿಂದ ಅಲಂಕರಿಸಿದ ಕೋಲು - ಏರಿಸಲಾಗುತ್ತದೆ, ಮತ್ತು ಸಿಹಿ-ಕಹಿ ಎರಡೂ ಇರುವ '
             'ವರ್ಷಕ್ಕಾಗಿ ಬೇವು-ಬೆಲ್ಲ ಸೇವಿಸಲಾಗುತ್ತದೆ.'),
        "gangaur": ('ಚೈತ್ರ ಶುಕ್ಲ ತೃತೀಯದ ಗಣಗೌರ್ ರಾಜಸ್ಥಾನದಲ್ಲಿ ಗೌರಿ (ಪಾರ್ವತಿ) ಮತ್ತು ಶಿವನ ಹಬ್ಬ. '
             'ಮಹಿಳೆಯರು ದಾಂಪತ್ಯ ಸುಖಕ್ಕಾಗಿ ಗೌರಿಯನ್ನು ಪೂಜಿಸುತ್ತಾರೆ - ವಿವಾಹಿತರು ಪತಿಗಾಗಿ, '
             'ಹುಡುಗಿಯರು ಒಳ್ಳೆಯ ವರನಿಗಾಗಿ; ಹೋಳಿಯ ಮರುದಿನದಿಂದ ಆರಂಭವಾಗುವ ಹದಿನೆಂಟು ದಿನಗಳ ಪೂಜೆ '
             'ಈ ದಿನ ಮುಗಿಯುತ್ತದೆ.'),
        "vat-savitri": ('ಉತ್ತರ ಭಾರತದಲ್ಲಿ ಜ್ಯೇಷ್ಠ ಅಮಾವಾಸ್ಯೆಯಂದು (ಪೂರ್ಣಿಮಾಂತ) ಆಚರಿಸುವ ವಟ ಸಾವಿತ್ರಿ ವ್ರತ, '
             'ಯಮನಿಂದ ಪತಿ ಸತ್ಯವಾನನ ಪ್ರಾಣವನ್ನು ಮರಳಿ ಪಡೆದ ಸಾವಿತ್ರಿಯನ್ನು ಸ್ಮರಿಸುತ್ತದೆ. ವಿವಾಹಿತ '
             'ಮಹಿಳೆಯರು ಉಪವಾಸ ಮಾಡಿ, ಆಲದ (ವಟ) ಮರವನ್ನು ಪೂಜಿಸಿ, ಪ್ರದಕ್ಷಿಣೆ ಹಾಕುತ್ತಾ ಅದಕ್ಕೆ ಹಸಿ '
             'ದಾರ ಸುತ್ತುತ್ತಾರೆ ಮತ್ತು ಸಾವಿತ್ರಿ ಕಥೆ ಕೇಳುತ್ತಾರೆ.'),
        "vat-purnima": ('ವಟ ಪೂರ್ಣಿಮೆ ವ್ರತವು ಅದೇ ವಟ ಸಾವಿತ್ರಿ ವ್ರತ; ಮಹಾರಾಷ್ಟ್ರ, ಗುಜರಾತ್ ಮತ್ತು ದಕ್ಷಿಣ '
             'ಭಾರತದಲ್ಲಿ (ಅಮಾಂತ ಪಂಚಾಂಗ) ಇದನ್ನು ಜ್ಯೇಷ್ಠ ಹುಣ್ಣಿಮೆಯಂದು, ಉತ್ತರ ಭಾರತದ ದಿನಾಂಕಕ್ಕಿಂತ '
             'ಹದಿನೈದು ದಿನ ನಂತರ ಆಚರಿಸಲಾಗುತ್ತದೆ. ವಿವಾಹಿತ ಮಹಿಳೆಯರು ಪತಿಯ ದೀರ್ಘಾಯುಷ್ಯಕ್ಕಾಗಿ '
             'ಉಪವಾಸ ಮಾಡಿ ಆಲದ ಮರವನ್ನು ಪೂಜಿಸುತ್ತಾರೆ.'),
        "ganga-dussehra": ('ಜ್ಯೇಷ್ಠ ಶುಕ್ಲ ದಶಮಿಯ ಗಂಗಾ ದಸರಾ ಭಗೀರಥನ ತಪಸ್ಸಿನಿಂದ ಗಂಗೆ ಭೂಮಿಗೆ ಇಳಿದುದನ್ನು '
             'ಆಚರಿಸುತ್ತದೆ. ಭಕ್ತರು ಗಂಗೆಯಲ್ಲಿ ಸ್ನಾನ ಮಾಡಿ, ದೀಪಗಳನ್ನು ಅರ್ಪಿಸಿ ದಾನ ಮಾಡುತ್ತಾರೆ; ಈ '
             'ಸ್ನಾನವು ಹತ್ತು ಬಗೆಯ ಪಾಪಗಳನ್ನು ತೊಳೆಯುತ್ತದೆ ಎಂದು ನಂಬಲಾಗಿದೆ.'),
        "hariyali-teej": ('ಶ್ರಾವಣ ಶುಕ್ಲ ತೃತೀಯದ ಹರಿಯಾಲಿ ತೀಜ್ ಮಳೆಗಾಲದಲ್ಲಿ ಶಿವ-ಪಾರ್ವತಿಯರ ಪುನರ್ಮಿಲನವನ್ನು '
             'ಆಚರಿಸುತ್ತದೆ. ಮಹಿಳೆಯರು ಹಸಿರು ಬಟ್ಟೆ ಧರಿಸಿ, ಮೆಹಂದಿ ಹಚ್ಚಿ, ಅಲಂಕರಿಸಿದ ಉಯ್ಯಾಲೆಗಳಲ್ಲಿ '
             'ತೂಗುತ್ತಾರೆ, ಶ್ರಾವಣದ ಹಾಡುಗಳನ್ನು ಹಾಡುತ್ತಾರೆ ಮತ್ತು ಅನೇಕರು ಪತಿಗಾಗಿ ಉಪವಾಸ '
             'ಮಾಡುತ್ತಾರೆ.'),
        "nag-panchami": ('ಶ್ರಾವಣ ಶುಕ್ಲ ಪಂಚಮಿಯಾದ ನಾಗರ ಪಂಚಮಿಯಂದು ನಾಗ ದೇವತೆಗಳನ್ನು ಪೂಜಿಸಲಾಗುತ್ತದೆ. '
             'ನಾಗರ ಚಿತ್ರಗಳನ್ನು ಬರೆದು ಅಥವಾ ಪ್ರತಿಮೆಗಳನ್ನು ಸ್ಥಾಪಿಸಿ ಹಾಲು, ಹೂವು ಮತ್ತು ಸಿಹಿ ಅರ್ಪಿಸಿ, '
             'ಕುಟುಂಬದ ರಕ್ಷಣೆಗಾಗಿ ಪ್ರಾರ್ಥಿಸಲಾಗುತ್ತದೆ. (ಗುಜರಾತಿನಲ್ಲಿ ನಾಗ ಪಂಚಮ ನಂತರ, '
             'ಭಾದ್ರಪದದಲ್ಲಿ ಬರುತ್ತದೆ.)'),
        "kajari-teej": ('ಭಾದ್ರಪದ ಕೃಷ್ಣ ತೃತೀಯದ (ಪೂರ್ಣಿಮಾಂತ) ಕಜರಿ (ಕಜಲಿ, ಬಡೀ) ತೀಜ್ ಅನ್ನು ಉತ್ತರ ಪ್ರದೇಶ, '
             'ಬಿಹಾರ, ರಾಜಸ್ಥಾನ ಮತ್ತು ಮಧ್ಯ ಪ್ರದೇಶದ ವಿವಾಹಿತ ಮಹಿಳೆಯರು ಆಚರಿಸುತ್ತಾರೆ. ಅವರು ಉಪವಾಸ '
             'ಮಾಡಿ, ಬೇವಿನ ಮರವನ್ನು (ನೀಮಡಿ ಮಾತೆ) ಪೂಜಿಸಿ, ಚಂದ್ರನಿಗೆ ಅರ್ಘ್ಯ ಅರ್ಪಿಸಿದ ನಂತರ ಉಪವಾಸ '
             'ಮುಗಿಸುತ್ತಾರೆ; ಕಜರಿ ಜಾನಪದ ಹಾಡುಗಳನ್ನು ಹಾಡಲಾಗುತ್ತದೆ.'),
        "hal-shashthi": ('ಭಾದ್ರಪದ ಕೃಷ್ಣ ಷಷ್ಠಿಯ (ಪೂರ್ಣಿಮಾಂತ) ಹಲ ಷಷ್ಠಿ (ಲಲಹೀ ಛಠ್, ಹರ ಛಠ್) ನೇಗಿಲನ್ನು '
             '(ಹಲ) ಆಯುಧವಾಗಿ ಹೊಂದಿರುವ ಬಲರಾಮನ ಜನ್ಮದಿನ. ತಾಯಂದಿರು ಮಕ್ಕಳಿಗಾಗಿ ಉಪವಾಸ ಮಾಡುತ್ತಾರೆ '
             'ಮತ್ತು ನೇಗಿಲಿನಿಂದ ಉತ್ತು ಬೆಳೆದ ಯಾವುದನ್ನೂ ಸೇವಿಸುವುದಿಲ್ಲ - ಸಾಮಾನ್ಯವಾಗಿ ಪಸಹೀ ಅಕ್ಕಿ '
             'ಮತ್ತು ಎಮ್ಮೆಯ ಹಾಲು.'),
        "hartalika-teej": ('ಭಾದ್ರಪದ ಶುಕ್ಲ ತೃತೀಯದ ಹರತಾಳಿಕಾ ವ್ರತ ಶಿವನನ್ನು ಪಡೆಯಲು ಪಾರ್ವತಿ ಮಾಡಿದ '
             'ತಪಸ್ಸನ್ನು ಗೌರವಿಸುತ್ತದೆ. ಮಹಿಳೆಯರು ನಿರ್ಜಲ ಉಪವಾಸ ಮಾಡಿ, ಶಿವ-ಪಾರ್ವತಿಯರ ಮಣ್ಣಿನ '
             'ಮೂರ್ತಿಗಳನ್ನು ಮಾಡಿ ಪೂಜಿಸುತ್ತಾರೆ (ಪ್ರಾತಃಕಾಲದ ಪೂಜೆ ಉತ್ತಮ), ರಾತ್ರಿ ಜಾಗರಣೆ ಮಾಡಿ '
             'ಮರುದಿನ ಬೆಳಿಗ್ಗೆ ಉಪವಾಸ ಮುಗಿಸುತ್ತಾರೆ.'),
        "rishi-panchami": ('ಭಾದ್ರಪದ ಶುಕ್ಲ ಪಂಚಮಿಯ ಋಷಿ ಪಂಚಮಿ ಸಪ್ತರ್ಷಿಗಳನ್ನು - ಏಳು ಋಷಿಗಳನ್ನು - '
             'ಗೌರವಿಸುತ್ತದೆ. ವಿಶೇಷವಾಗಿ ಮಹಿಳೆಯರು ಸ್ನಾನ ಮಾಡಿ, ಉಪವಾಸವಿದ್ದು, ಮಧ್ಯಾಹ್ನದಲ್ಲಿ '
             'ಋಷಿಗಳನ್ನು ಪೂಜಿಸುತ್ತಾರೆ; ತಿಳಿಯದೆ ಆದ ದೋಷಗಳಿಂದ ಶುದ್ಧಿಯನ್ನು ಬಯಸಿ.'),
        "anant-chaturdashi": ('ಭಾದ್ರಪದ ಶುಕ್ಲ ಚತುರ್ದಶಿಯ ಅನಂತ ಚತುರ್ದಶಿಯಂದು ಭಗವಾನ್ ವಿಷ್ಣುವನ್ನು ಅನಂತನಾಗಿ '
             'ಪೂಜಿಸಲಾಗುತ್ತದೆ. ಪೂಜೆಯ ನಂತರ ಹದಿನಾಲ್ಕು ಗಂಟುಗಳ ಪವಿತ್ರ ದಾರವನ್ನು (ಅನಂತ ಸೂತ್ರ) '
             'ತೋಳಿಗೆ ಕಟ್ಟಲಾಗುತ್ತದೆ; ಇದೇ ದಿನ ಗಣೇಶ ಮೂರ್ತಿಗಳ ವಿಸರ್ಜನೆಯೂ ನಡೆಯುತ್ತದೆ.'),
        "pitru-paksha": ('ಪಿತೃ ಪಕ್ಷ (ಮಹಾಲಯ ಪಕ್ಷ), ಪೂರ್ವಜರ ಹದಿನೈದು ದಿನಗಳು, ಆಶ್ವಯುಜ (ಪೂರ್ಣಿಮಾಂತ) '
             'ಕೃಷ್ಣ ಪಕ್ಷದ ಪ್ರತಿಪದೆಯಿಂದ ಅಮಾವಾಸ್ಯೆಯವರೆಗೆ ಇರುತ್ತದೆ. ಪೂರ್ವಜರು ಗತಿಸಿದ ತಿಥಿಯಂದು '
             'ಕುಟುಂಬಗಳು ಕುತಪ, ರೌಹಿಣ ಅಥವಾ ಅಪರಾಹ್ನ ಕಾಲದಲ್ಲಿ ತರ್ಪಣ ಮತ್ತು ಶ್ರಾದ್ಧ - ಪಿಂಡ, '
             'ಬ್ರಾಹ್ಮಣರಿಗೆ ಭೋಜನ, ಹಸು, ಕಾಗೆ ಮತ್ತು ನಾಯಿಗಳಿಗೆ ಆಹಾರ - ಅರ್ಪಿಸುತ್ತವೆ.'),
        "sarva-pitru-amavasya": ('ಮಹಾಲಯ ಅಮಾವಾಸ್ಯೆ (ಸರ್ವ ಪಿತೃ ಅಮಾವಾಸ್ಯೆ) ಪಿತೃ ಪಕ್ಷವನ್ನು ಮುಗಿಸುತ್ತದೆ. '
             'ಈ ದಿನ ಮಾಡುವ ಶ್ರಾದ್ಧವು ತಿಥಿ ತಿಳಿಯದವರೂ ಸೇರಿದಂತೆ ಎಲ್ಲಾ ಪೂರ್ವಜರನ್ನು ತಲುಪುತ್ತದೆ; '
             'ಇದನ್ನು ಕುತಪ, ರೌಹಿಣ ಅಥವಾ ಅಪರಾಹ್ನ ಕಾಲದಲ್ಲಿ ಮಾಡಲಾಗುತ್ತದೆ.'),
        "narak-chaturdashi": ('ಕಾರ್ತಿಕ ಕೃಷ್ಣ ಚತುರ್ದಶಿಯ (ಪೂರ್ಣಿಮಾಂತ) ನರಕ ಚತುರ್ದಶಿ (ರೂಪ ಚೌದಸ್) ನರಕಾಸುರನ '
             'ಮೇಲೆ ಶ್ರೀಕೃಷ್ಣನ ವಿಜಯವನ್ನು ಸ್ಮರಿಸುತ್ತದೆ. ಸೂರ್ಯೋದಯಕ್ಕೆ ಮೊದಲು, ಚಂದ್ರನು ಆಕಾಶದಲ್ಲಿ '
             'ಇರುವಾಗ, ಜನರು ಉಬಟನ್ ಹಚ್ಚಿ ಎಣ್ಣೆ ಸ್ನಾನ (ಅಭ್ಯಂಗ ಸ್ನಾನ) ಮಾಡುತ್ತಾರೆ ಮತ್ತು ಸಂಜೆ '
             'ಯಮನಿಗಾಗಿ ದೀಪ ಹಚ್ಚಲಾಗುತ್ತದೆ.'),
        "tulsi-vivah": ('ಕಾರ್ತಿಕ ಶುಕ್ಲ ದ್ವಾದಶಿಯ ತುಳಸಿ ವಿವಾಹ ತುಳಸಿ ಗಿಡಕ್ಕೆ (ವೃಂದೆಯಾಗಿ) ಸಾಲಿಗ್ರಾಮ '
             'ರೂಪದ ಭಗವಾನ್ ವಿಷ್ಣುವಿನೊಂದಿಗೆ ನಡೆಸುವ ವಿಧ್ಯುಕ್ತ ವಿವಾಹ. ಕುಟುಂಬಗಳು ತುಳಸಿಯನ್ನು '
             'ವಧುವಿನಂತೆ ಅಲಂಕರಿಸಿ ವಿವಾಹದ ವಿಧಿಗಳನ್ನು ನೆರವೇರಿಸುತ್ತವೆ; ಇದರ ನಂತರ ಹಿಂದೂ '
             'ಮದುವೆಗಳ ಕಾಲ ಆರಂಭವಾಗುತ್ತದೆ.'),
        "kartik-purnima": ('ಕಾರ್ತಿಕ ಹುಣ್ಣಿಮೆ ಪವಿತ್ರ ಕಾರ್ತಿಕ ಮಾಸವನ್ನು ಮುಗಿಸುತ್ತದೆ. ಗಂಗೆ ಅಥವಾ ಪವಿತ್ರ '
             'ನದಿಯಲ್ಲಿ ಸ್ನಾನ ಮತ್ತು ದಾನಕ್ಕೆ ಇದು ಮಹತ್ವದ ದಿನ; ಇದೇ ದಿನ ಗುರು ನಾನಕ್ ಜಯಂತಿ ಮತ್ತು '
             'ಶಿವನು ತ್ರಿಪುರಾಸುರನನ್ನು ಸಂಹರಿಸಿದ ತ್ರಿಪುರಿ ಪೂರ್ಣಿಮೆಯೂ ಹೌದು.'),
        "dev-deepawali": ("ದೇವ ದೀಪಾವಳಿ, 'ದೇವತೆಗಳ ದೀಪಾವಳಿ', ಕಾರ್ತಿಕ ಹುಣ್ಣಿಮೆಯ ಸಂಜೆ, ವಿಶೇಷವಾಗಿ "
             'ಲಕ್ಷಾಂತರ ಹಣತೆಗಳಿಂದ ಬೆಳಗುವ ವಾರಾಣಸಿಯ ಘಾಟುಗಳಲ್ಲಿ ಆಚರಿಸಲಾಗುತ್ತದೆ. ಇದು '
             'ತ್ರಿಪುರಾಸುರನ ಮೇಲೆ ಶಿವನ ವಿಜಯವನ್ನು ಸೂಚಿಸುತ್ತದೆ; ಪ್ರದೋಷ ಕಾಲದಲ್ಲಿ ಗಂಗೆಗೆ '
             'ದೀಪಗಳನ್ನು ಅರ್ಪಿಸಲಾಗುತ್ತದೆ.'),
    },
    "te": {
        "makar-sankranti": ("మకర సంక్రాంతి నాడు సూర్యుడు మకర రాశిలో ప్రవేశిస్తాడు, ఉత్తరాయణం "
             "ప్రారంభమవుతుంది. ఇది పంటల పండుగ: పవిత్ర నదుల్లో స్నానం చేస్తారు, నువ్వులు, బెల్లం, "
             "కిచిడీ, కంబళ్ళు దానం చేస్తారు, గాలిపటాలు ఎగరేస్తారు."),
        "maha-shivratri": ("మహా శివరాత్రి, శివుని మహా రాత్రి, మాఘ బహుళ చతుర్దశి నాడు వస్తుంది. భక్తులు "
             "ఉపవాసం ఉండి, శివలింగానికి జలం, పాలు, బిల్వ పత్రాలు సమర్పిస్తారు, ఓం నమః శివాయ జపిస్తూ "
             "రాత్రి నాలుగు జాములూ జాగరణ చేస్తారు; అర్ధరాత్రి సమయంలోని నిశీథ కాల పూజ అత్యంత "
             "ముఖ్యమైనది."),
        "holika-dahan": ("హోలీకి ముందు రోజు రాత్రి జరిగే హోలికా దహనం (కామదహనం) ప్రహ్లాదుని భక్తిని, "
             "చెడుపై మంచి సాధించిన విజయాన్ని స్మరించుకునే వేడుక. సూర్యాస్తమయం తర్వాత, భద్రను "
             "తప్పించి, మంట వెలిగిస్తారు; కుటుంబాలు దాని చుట్టూ ప్రదక్షిణ చేస్తూ ధాన్యం, కొబ్బరికాయ "
             "సమర్పించి ప్రార్థిస్తారు."),
        "holi": ("హోలీ, రంగుల పండుగ, హోలికా దహనం మరుసటి రోజు ఉదయం జరుపుకుంటారు - రంగులు, సంగీతం, "
             "గుజియా వంటి మిఠాయిలు, బంధుమిత్రుల ఇళ్లకు వెళ్లడంతో."),
        "ram-navami": ("శ్రీరామ నవమి చైత్ర శుద్ధ నవమి నాడు మధ్యాహ్నం శ్రీరాముని జన్మను జరుపుకునే పండుగ. "
             "భక్తులు ఉపవాసం ఉండి, రామచరితమానస్ పఠిస్తారు, ఆయన జన్మించిన సమయమైన మధ్యాహ్న "
             "ముహూర్తంలో పూజ చేస్తారు."),
        "hanuman-jayanti": ("హనుమాన్ జయంతి (ఉత్తర భారతదేశంలో చైత్ర పౌర్ణమి) హనుమంతుని జన్మను జరుపుకునే "
             "పండుగ. భక్తులు హనుమాన్ ఆలయాలను దర్శించి, హనుమాన్ చాలీసా, సుందరకాండ పఠిస్తారు, "
             "సిందూరం, లడ్డూలు సమర్పిస్తారు."),
        "akshaya-tritiya": ("వైశాఖ శుద్ధ తదియ అయిన అక్షయ తృతీయ నాడు చేసే ప్రతి మంచి పని 'అక్షయం' - "
             "తరగనిది - అవుతుందని నమ్మకం. ప్రజలు విష్ణువును, లక్ష్మీదేవిని పూజిస్తారు, దానాలు "
             "చేస్తారు, కొత్త పనులు ప్రారంభిస్తారు లేదా బంగారం కొంటారు."),
        "raksha-bandhan": ("శ్రావణ పౌర్ణమి నాడు జరిగే రక్షా బంధన్ (రాఖీ పౌర్ణమి) సోదరసోదరీల అనుబంధాన్ని "
             "జరుపుకునే పండుగ. సోదరీమణులు సోదరుని మణికట్టుకు రాఖీ కట్టి అతని క్షేమం కోసం "
             "ప్రార్థిస్తారు; రాఖీని భద్ర లేని సమయంలో కడతారు."),
        "janmashtami": ("శ్రీ కృష్ణ జన్మాష్టమి భాద్రపద బహుళ అష్టమి (పూర్ణిమాంతం; అమాంత పంచాంగంలో శ్రావణ "
             "బహుళ అష్టమి) అర్ధరాత్రి శ్రీకృష్ణుని జన్మను జరుపుకునే పండుగ. భక్తులు పగలంతా ఉపవాసం "
             "ఉండి, నిశీథ (అర్ధరాత్రి) పూజ తర్వాత విరమిస్తారు; ఆ సమయంలో బాలకృష్ణునికి స్నానం "
             "చేయించి ఊయలలో ఉంచుతారు."),
        "ganesh-chaturthi": ("భాద్రపద శుద్ధ చవితి అయిన వినాయక చవితి నాడు గణపతిని ఇంటికి ఆహ్వానిస్తారు. "
             "ఆయన జన్మించిన సమయమైన మధ్యాహ్న ముహూర్తంలో విగ్రహాన్ని ప్రతిష్ఠించి, మోదకాలు, గరిక, "
             "ఎర్రని పువ్వులతో పూజిస్తారు; ఈ రోజు చంద్రుణ్ణి చూడటం మానుకుంటారు."),
        "chaitra-navratri": ("వసంత నవరాత్రులు, వసంత ఋతువులో దుర్గాదేవి తొమ్మిది రాత్రులు, చైత్ర శుద్ధ "
             "పాడ్యమి నాడు ప్రారంభమవుతాయి - ఇది హిందూ నూతన సంవత్సరం (విక్రమ సంవత్సరం) కూడా. "
             "ఘటస్థాపన (కలశ స్థాపన)తో తొమ్మిది రోజుల పూజ మొదలవుతుంది."),
        "navratri": ("శరన్నవరాత్రులు, శరదృతువులో దుర్గాదేవి తొమ్మిది రాత్రులు, ఆశ్వయుజ శుద్ధ పాడ్యమి "
             "నాడు ఉదయం ఘటస్థాపనతో - కలశం స్థాపించి, యవలు విత్తి - ప్రారంభమవుతాయి. ప్రతి రోజు "
             "అమ్మవారి తొమ్మిది రూపాల్లో ఒకదాన్ని పూజిస్తారు."),
        "dussehra": ("విజయదశమి (దసరా) రావణునిపై శ్రీరాముని విజయానికి, మహిషాసురునిపై దుర్గాదేవి "
             "విజయానికి గుర్తు. శమీ పూజ, అపరాజితా పూజ, రావణ దిష్టిబొమ్మల దహనం అపరాహ్ణంలో "
             "జరుగుతాయి; విజయ ముహూర్తం ఏ కొత్త పని ప్రారంభానికైనా మంచిదని భావిస్తారు."),
        "karwa-chauth": ("కర్వా చౌత్ నాడు వివాహిత స్త్రీలు భర్తల దీర్ఘాయుష్షు కోసం సూర్యోదయం నుండి "
             "చంద్రోదయం వరకు ఉపవాసం ఉంటారు. సాయంత్రం కర్వా మాత పూజ తర్వాత చంద్రునికి అర్ఘ్యం "
             "(జలం) సమర్పించి ఉపవాసం విరమిస్తారు."),
        "ahoi-ashtami": ("దీపావళికి ఎనిమిది రోజుల ముందు వచ్చే అహోయి అష్టమి నాడు తల్లులు పిల్లల క్షేమం "
             "కోసం ఉపవాసం ఉండి సాయంత్రం అహోయి మాతను పూజిస్తారు; సంప్రదాయంగా నక్షత్రాలను చూసిన "
             "తర్వాత (కొన్ని కుటుంబాల్లో చంద్రుణ్ణి చూసిన తర్వాత) ఉపవాసం విరమిస్తారు."),
        "dhanteras": ("దీపావళి ఉత్సవాల్లో మొదటి రోజైన ధన త్రయోదశి నాడు ధన్వంతరిని, లక్ష్మీదేవిని "
             "పూజిస్తారు. కొత్త పాత్రలు, బంగారం లేదా వెండి కొంటారు, సంధ్యా సమయంలో యమ దీపం "
             "వెలిగిస్తారు; పూజను ప్రదోష కాలంలో, వీలైతే స్థిర వృషభ లగ్నంలో చేస్తారు."),
        "diwali": ("కార్తీక అమావాస్య (పూర్ణిమాంతం; అమాంత పంచాంగంలో ఆశ్వయుజ అమావాస్య) నాడు వచ్చే "
             "దీపావళి దీపాల పండుగ. సాయంత్రం ప్రదోష కాలంలో - సంపద నిలిచి ఉండాలని వీలైతే స్థిర వృషభ "
             "లగ్నంలో - లక్ష్మీదేవిని, గణపతిని పూజిస్తారు; ఇళ్లను దీపాలతో వెలిగిస్తారు."),
        "govardhan-puja": ("గోవర్ధన పూజ (అన్నకూట్), దీపావళి మరుసటి రోజు, శ్రీకృష్ణుడు గోవర్ధన గిరిని "
             "ఎత్తిన ఘట్టాన్ని స్మరిస్తుంది. ఆవు పేడతో లేదా ఆహారంతో చేసిన గోవర్ధనాన్ని పూజించి, "
             "అనేక వంటకాల అన్నకూటాన్ని సమర్పిస్తారు, సాధారణంగా ఉదయం (ప్రాతఃకాలంలో)."),
        "bhai-dooj": ("భగినీ హస్త భోజనం (యమ ద్వితీయ), కార్తీక శుద్ధ విదియ, సోదరసోదరీల పండుగ: "
             "సోదరీమణులు సోదరునికి తిలకం దిద్ది, హారతి ఇచ్చి, అతని దీర్ఘాయుష్షు కోసం ప్రార్థిస్తారు - "
             "వీలైతే అపరాహ్ణ (మధ్యాహ్నం తర్వాతి) సమయంలో."),
        "chhath-puja": ("ఛఠ్ పూజలో నాలుగు రోజుల పాటు సూర్యదేవుని, ఛఠీ మైయాను పూజిస్తారు. ముఖ్య దినాన "
             "(కార్తీక శుద్ధ షష్ఠి) భక్తులు నీటిలో నిలబడి అస్తమించే సూర్యునికి, మరుసటి ఉదయం "
             "ఉదయించే సూర్యునికి అర్ఘ్యం సమర్పించి, నీరు కూడా తాగకుండా ఉంచిన ఉపవాసాన్ని "
             "ముగిస్తారు."),
        "vasant-panchami": ("వసంత పంచమి (శ్రీ పంచమి), మాఘ శుద్ధ పంచమి, వసంత ఋతువును ఆహ్వానిస్తూ "
             "సరస్వతీ దేవిని పూజించే రోజు. విద్యార్థులు, కళాకారులు పుస్తకాలను, వాయిద్యాలను "
             "పూజిస్తారు, పసుపు రంగు దుస్తులు ధరిస్తారు, పిల్లలకు తరచుగా అక్షరాభ్యాసం (విద్యారంభం) "
             "చేయిస్తారు."),
        "guru-purnima": ("గురు పౌర్ణమి (వ్యాస పౌర్ణమి), ఆషాఢ పౌర్ణమి, గురువులను, ఈ రోజు జన్మించిన "
             "మహర్షి వేదవ్యాసుని గౌరవించే రోజు. శిష్యులు తమ గురువుకు కృతజ్ఞతలు, పువ్వులు, కానుకలు "
             "సమర్పిస్తారు."),
        "sharad-purnima": ("శరత్ పౌర్ణమి, ఆశ్వయుజ పౌర్ణమి, చంద్రుడు అత్యంత ప్రకాశవంతంగా, అమృతంతో నిండి "
             "ఉంటాడని భావించే రాత్రి. పాయసాన్ని రాత్రంతా వెన్నెలలో ఉంచి ప్రసాదంగా తింటారు; "
             "లక్ష్మీదేవిని పూజిస్తారు (కోజాగరి)."),
        "devuthani-ekadashi": ("ఉత్థాన (ప్రబోధిని) ఏకాదశి, కార్తీక శుద్ధ ఏకాదశి, శ్రీమహావిష్ణువు "
             "నాలుగు నెలల నిద్ర నుండి మేల్కొనే రోజుగా భావిస్తారు; దీనితో చాతుర్మాస్యం ముగుస్తుంది. "
             "తులసి వివాహాలు మొదలవుతాయి, పెళ్లిళ్ల కాలం ప్రారంభమవుతుంది. భక్తులు ఉపవాసం ఉండి "
             "మరుసటి రోజు పారణ (ఉపవాస విరమణ) చేస్తారు."),
        "jivitputrika": ("జీవిత్పుత్రికా వ్రతం (జితియా, జియుతియా) బీహార్, జార్ఖండ్, తూర్పు ఉత్తరప్రదేశ్, "
             "నేపాల్‌లో తల్లులు పిల్లల దీర్ఘాయుష్షు, క్షేమం కోసం ఆశ్వయుజ బహుళ అష్టమి (పూర్ణిమాంతం; "
             "అమాంత పంచాంగంలో భాద్రపద బహుళ అష్టమి) నాడు ఆచరిస్తారు. ముందు రోజు నహాయ్-ఖాయ్‌తో "
             "మొదలవుతుంది; వ్రతం నిర్జలంగా - నీరు కూడా లేకుండా - పగలూ రాత్రీ కొనసాగుతుంది, "
             "జీమూతవాహనుని పూజ, జితియా కథ ఉంటాయి. పారణ, అంటే ఉపవాస విరమణ, మరుసటి ఉదయం."),
        "lohri": ("లోహ్రీ, మకర సంక్రాంతికి ముందు రోజు సాయంత్రం, పంజాబ్, ఉత్తర భారతదేశపు శీతాకాల పంటల "
             "పండుగ. సంధ్యా సమయంలో మంట వెలిగించి, అందులో నువ్వులు, బెల్లం, రేవడీ, వేరుశనగలు, "
             "మొక్కజొన్న పేలాలు సమర్పిస్తారు, పాటలు పాడి నృత్యం చేస్తారు; కొత్త పెళ్లికూతురు లేదా "
             "నవజాత శిశువు కోసం దీన్ని ప్రత్యేకంగా జరుపుకుంటారు."),
        "sakat-chauth": ("సకట్ చౌత్ (తిల్‌కుట్ చౌత్), మాఘ మాస సంకష్టహర చతుర్థి (పూర్ణిమాంతం; అమాంత "
             "పంచాంగంలో పుష్య బహుళ చవితి), తల్లులు పిల్లల కోసం ఆచరిస్తారు. గణపతిని, సకట్ మాతను "
             "నువ్వులు, బెల్లంతో పూజించి, ఉదయించిన చంద్రునికి అర్ఘ్యం సమర్పించాక ఉపవాసం "
             "విరమిస్తారు."),
        "mauni-amavasya": ("మౌని అమావాస్య, మాఘ అమావాస్య (పూర్ణిమాంతం; అమాంత పంచాంగంలో పుష్య "
             "అమావాస్య), ప్రయాగ్‌రాజ్ మాఘ మేళాలో ప్రధాన స్నాన దినం. భక్తులు గంగలో లేదా పవిత్ర "
             "నదిలో స్నానం చేసి, మౌనం పాటించి, దానాలు చేస్తారు."),
        "sheetala-ashtami": ("శీతలా అష్టమి (బసోడా), చైత్ర బహుళ అష్టమి (పూర్ణిమాంతం; అమాంత పంచాంగంలో "
             "ఫాల్గుణ బహుళ అష్టమి), జ్వరాలు, మశూచి నుండి కాపాడే దేవత శీతలా మాతను పూజించే రోజు. "
             "ముందు రోజే వంట చేసి, ఆ చల్లారిన (బాసీ) ఆహారాన్ని నైవేద్యంగా సమర్పించి తింటారు; ఆ "
             "రోజు వంటకు పొయ్యి వెలిగించరు."),
        "gudi-padwa": ("ఉగాది (కర్ణాటక, ఆంధ్రప్రదేశ్, తెలంగాణ), గుడి పాడ్వా (మహారాష్ట్ర) చైత్ర శుద్ధ "
             "పాడ్యమి నాడు చాంద్రమాన నూతన సంవత్సరాన్ని సూచిస్తాయి. గుమ్మం వద్ద గుడి - వస్త్రం, "
             "కలశంతో అలంకరించిన కర్ర - నిలబెడతారు; ఏడాదంతా తీపి, చేదు రెండూ ఉంటాయని సూచిస్తూ "
             "వేపను బెల్లంతో కలిపి తింటారు."),
        "gangaur": ("గణగౌర్, చైత్ర శుద్ధ తదియ, గౌరీ (పార్వతి), శివుల రాజస్థానీ పండుగ. స్త్రీలు దాంపత్య "
             "సౌఖ్యం కోసం గౌరిని పూజిస్తారు - వివాహితలు భర్తల కోసం, అమ్మాయిలు మంచి వరుడి కోసం; "
             "హోలీ మరుసటి రోజు మొదలయ్యే పద్దెనిమిది రోజుల పూజ ఈ రోజుతో ముగుస్తుంది."),
        "vat-savitri": ("వట సావిత్రి వ్రతం, ఉత్తర భారతదేశంలో జ్యేష్ఠ అమావాస్య నాడు (పూర్ణిమాంతం; అమాంత "
             "పంచాంగంలో వైశాఖ అమావాస్య), యముని నుండి భర్త సత్యవంతుని ప్రాణాలను తిరిగి పొందిన "
             "సావిత్రిని స్మరిస్తుంది. వివాహిత స్త్రీలు ఉపవాసం ఉండి, మర్రి (వట) చెట్టును పూజించి, "
             "దాని చుట్టూ ప్రదక్షిణ చేస్తూ ముడి దారం చుడతారు, సావిత్రి కథ వింటారు."),
        "vat-purnima": ("వట పౌర్ణమి వ్రతం అదే వట సావిత్రి వ్రతం - మహారాష్ట్ర, గుజరాత్, దక్షిణాదిలో "
             "(అమాంత పంచాంగం) జ్యేష్ఠ పౌర్ణమి నాడు, ఉత్తర భారత తేదీకి పదిహేను రోజుల తర్వాత "
             "ఆచరిస్తారు. వివాహిత స్త్రీలు భర్తల దీర్ఘాయుష్షు కోసం ఉపవాసం ఉండి మర్రి చెట్టును "
             "పూజిస్తారు."),
        "ganga-dussehra": ("గంగా దశహరా, జ్యేష్ఠ శుద్ధ దశమి, భగీరథుని తపస్సు వల్ల గంగ భూమికి దిగివచ్చిన "
             "సందర్భాన్ని జరుపుకుంటుంది. భక్తులు గంగలో స్నానం చేసి, దీపాలు సమర్పించి, దానాలు "
             "చేస్తారు; ఈ స్నానం పది రకాల పాపాలను పోగొడుతుందని నమ్మకం."),
        "hariyali-teej": ("హరియాలీ తీజ్, శ్రావణ శుద్ధ తదియ, వర్షాకాలంలో శివపార్వతుల పునఃసమాగమాన్ని "
             "జరుపుకుంటుంది. స్త్రీలు ఆకుపచ్చ దుస్తులు ధరించి, గోరింటాకు పెట్టుకుని, అలంకరించిన "
             "ఊయలలు ఊగుతూ, శ్రావణ పాటలు పాడతారు; చాలామంది భర్తల కోసం ఉపవాసం ఉంటారు."),
        "nag-panchami": ("నాగ పంచమి, శ్రావణ శుద్ధ పంచమి, నాగదేవతలను పూజించే రోజు. నాగుల చిత్రాలు గీసి "
             "లేదా ప్రతిమలు ఉంచి పాలు, పువ్వులు, మిఠాయిలు సమర్పిస్తారు, కుటుంబ రక్షణ కోసం "
             "ప్రార్థిస్తారు. (గుజరాత్‌లో నాగ పంచమ్ తర్వాత, భాద్రపదంలో వస్తుంది.)"),
        "kajari-teej": ("కజరీ (కజ్లీ, బడీ) తీజ్, భాద్రపద బహుళ తదియ (పూర్ణిమాంతం; అమాంత పంచాంగంలో "
             "శ్రావణ బహుళ తదియ), ఉత్తరప్రదేశ్, బీహార్, రాజస్థాన్, మధ్యప్రదేశ్ వివాహిత స్త్రీలు "
             "ఆచరిస్తారు. వారు ఉపవాసం ఉండి, వేప చెట్టును (నీమడీ మాత) పూజించి, చంద్రునికి అర్ఘ్యం "
             "సమర్పించాక ఉపవాసం విరమిస్తారు; కజరీ జానపద పాటలు పాడతారు."),
        "hal-shashthi": ("హల షష్ఠి (లలహీ ఛఠ్, హర్ ఛఠ్), భాద్రపద బహుళ షష్ఠి (పూర్ణిమాంతం; అమాంత "
             "పంచాంగంలో శ్రావణ బహుళ షష్ఠి), నాగలి (హలం) ఆయుధంగా గల బలరాముని జన్మదినం. తల్లులు "
             "పిల్లల కోసం ఉపవాసం ఉండి, నాగలితో పండించినవేవీ తినరు - తరచుగా పసహీ బియ్యం, గేదె పాలు "
             "తీసుకుంటారు."),
        "hartalika-teej": ("హరితాళిక వ్రతం, భాద్రపద శుద్ధ తదియ, శివుని పొందడానికి పార్వతి చేసిన "
             "తపస్సును స్మరిస్తుంది. స్త్రీలు నిర్జల ఉపవాసం ఉండి, మట్టితో శివపార్వతుల ప్రతిమలు చేసి "
             "పూజిస్తారు (ప్రాతఃకాలంలో ఉదయం పూజ శ్రేష్ఠం), రాత్రి జాగరణ చేసి మరుసటి ఉదయం ఉపవాసం "
             "విరమిస్తారు."),
        "rishi-panchami": ("ఋషి పంచమి, భాద్రపద శుద్ధ పంచమి, సప్తర్షులను - ఏడుగురు మహర్షులను - "
             "పూజించే రోజు. ముఖ్యంగా స్త్రీలు స్నానం చేసి, ఉపవాసం ఉండి, తెలియక చేసిన దోషాల నుండి "
             "శుద్ధి కోరుతూ మధ్యాహ్న కాలంలో ఋషులను పూజిస్తారు."),
        "anant-chaturdashi": ("అనంత చతుర్దశి, భాద్రపద శుద్ధ చతుర్దశి, శ్రీమహావిష్ణువును అనంతునిగా "
             "పూజించే రోజు. పూజ తర్వాత పద్నాలుగు ముడులు గల పవిత్ర దారాన్ని (అనంత సూత్రం) చేతికి "
             "కడతారు; ఇదే రోజు గణపతి విగ్రహాల నిమజ్జనం కూడా జరుగుతుంది."),
        "pitru-paksha": ("మహాలయ పక్షం (పితృ పక్షం), పితరుల పక్షం, ఆశ్వయుజ బహుళ పక్షంలో (పూర్ణిమాంతం; "
             "అమాంత పంచాంగంలో భాద్రపద బహుళం) పాడ్యమి నుండి అమావాస్య వరకు ఉంటుంది. పితరులు "
             "గతించిన తిథి నాడు కుటుంబాలు కుతప, రౌహిణ లేదా అపరాహ్ణ కాలంలో తర్పణం, శ్రాద్ధం - "
             "పిండ ప్రదానం, బ్రాహ్మణులకు, ఆవులకు, కాకులకు, కుక్కలకు ఆహారం - చేస్తారు."),
        "sarva-pitru-amavasya": ("మహాలయ అమావాస్య (సర్వ పితృ అమావాస్య)తో మహాలయ పక్షం ముగుస్తుంది. ఈ "
             "రోజు చేసే శ్రాద్ధం తిథి తెలియని వారితో సహా పితరులందరికీ చేరుతుంది; దీన్ని కుతప, "
             "రౌహిణ లేదా అపరాహ్ణ కాలంలో చేస్తారు."),
        "narak-chaturdashi": ("నరక చతుర్దశి (రూప్ చౌదస్), కార్తీక బహుళ చతుర్దశి (పూర్ణిమాంతం; అమాంత "
             "పంచాంగంలో ఆశ్వయుజ బహుళ చతుర్దశి), నరకాసురునిపై శ్రీకృష్ణుని విజయాన్ని స్మరిస్తుంది. "
             "సూర్యోదయానికి ముందు, చంద్రుడు ఆకాశంలో ఉండగానే, నలుగు పెట్టుకుని నూనెతో అభ్యంగ స్నానం "
             "చేస్తారు; సాయంత్రం యముని కోసం దీపం వెలిగిస్తారు."),
        "tulsi-vivah": ("తులసి వివాహం, కార్తీక శుద్ధ ద్వాదశి నాడు, తులసి మొక్కకు (బృందగా) సాలగ్రామ "
             "రూపంలోని శ్రీమహావిష్ణువుతో జరిపే వివాహ వేడుక. కుటుంబాలు తులసిని పెళ్లికూతురిలా "
             "అలంకరించి వివాహ క్రతువులు నిర్వహిస్తాయి; దీని తర్వాత హిందూ వివాహాల కాలం "
             "మొదలవుతుంది."),
        "kartik-purnima": ("పూర్ణిమాంత పంచాంగంలో పవిత్ర కార్తీక మాసం కార్తీక పౌర్ణమితో ముగుస్తుంది. "
             "గంగలో లేదా పవిత్ర నదిలో స్నానానికి, దానాలకు ఇది గొప్ప రోజు; ఇదే రోజు గురునానక్ జయంతి, "
             "శివుడు త్రిపురాసురుని సంహరించిన త్రిపుర పౌర్ణమి కూడా."),
        "dev-deepawali": ("దేవ దీపావళి, 'దేవతల దీపావళి', కార్తీక పౌర్ణమి సాయంత్రం జరుపుకుంటారు - అన్నిటికంటే "
             "ఎక్కువగా వారణాసి ఘాట్‌లలో, అవి లక్షలాది దీపాలతో వెలుగుతాయి. ఇది త్రిపురాసురునిపై శివుని "
             "విజయానికి గుర్తు; ప్రదోష కాలంలో గంగకు దీపాలు సమర్పిస్తారు."),
    },

    # Tamil (DIVASTRO-123)
    "ta": {
        "makar-sankranti": ("மகர சங்கராந்தி, சூரியன் மகர ராசியில் நுழைந்து வடக்கு நோக்கிய பயணத்தை (உத்தராயணம்) "
                            "தொடங்கும் நாள். இது ஒரு அறுவடைத் திருநாள்: மக்கள் புனித நதிகளில் நீராடி, எள், "
                            "வெல்லம், கிச்சடி, கம்பளி போன்றவற்றைத் தானம் செய்து, பட்டம் விடுகிறார்கள். "
                            "தமிழ்நாட்டில் இந்நாள் தைப் பொங்கல் - புதுப் பானையில் பொங்கல் வைத்து சூரியனுக்குப் "
                            "படைக்கிறார்கள்."),
        "maha-shivratri": ("சிவபெருமானின் பெரும் இரவான மகா சிவராத்திரி, மாக மாதத் தேய்பிறை சதுர்த்தசியில் "
                           "வருகிறது. பக்தர்கள் விரதம் இருந்து, சிவலிங்கத்துக்கு நீர், பால், வில்வ இலை "
                           "சமர்ப்பித்து, ஓம் நமசிவாய ஜபித்து, இரவின் நான்கு ஜாமங்களிலும் கண்விழிக்கிறார்கள்; "
                           "நள்ளிரவை ஒட்டிய நிசீத கால பூஜை மிக முக்கியமானது."),
        "holika-dahan": ("ஹோலிக்கு முந்தைய மாலை நடைபெறும் ஹோலிகா தகனம், பிரகலாதனின் பக்தியையும் தீமையை நன்மை "
                         "வென்றதையும் கொண்டாடுகிறது. சூரிய அஸ்தமனத்துக்குப் பிறகு, பத்ரா காலத்தைத் தவிர்த்து, "
                         "தீ மூட்டப்படுகிறது; குடும்பங்கள் அதைச் சுற்றி வந்து தானியம், தேங்காய் படைத்து "
                         "வழிபடுகின்றன."),
        "holi": ("வண்ணங்களின் திருநாளான ஹோலி, ஹோலிகா தகனத்துக்கு மறுநாள் காலை கொண்டாடப்படுகிறது - "
                 "வண்ணப் பொடிகள், இசை, குஜியா போன்ற இனிப்புகள், உறவினர்களையும் நண்பர்களையும் "
                 "சந்தித்தல் என மகிழ்ச்சியாக."),
        "ram-navami": ("ஸ்ரீ ராம நவமி, சைத்ர மாத வளர்பிறை நவமியில் நண்பகலில் ஸ்ரீ ராமர் அவதரித்ததைக் "
                       "கொண்டாடுகிறது. பக்தர்கள் விரதம் இருந்து, ராமசரிதமானஸ் (ராமாயணம்) படித்து, அவர் "
                       "பிறந்த நேரமான மத்தியான முகூர்த்தத்தில் பூஜை செய்கிறார்கள்."),
        "hanuman-jayanti": ("ஹனுமான் ஜெயந்தி (வட இந்தியாவில் சைத்ர பௌர்ணமி) ஸ்ரீ ஆஞ்சநேயரின் அவதாரத்தைக் "
                            "கொண்டாடுகிறது. பக்தர்கள் ஆஞ்சநேயர் கோயில்களுக்குச் சென்று, ஹனுமான் சாலீசா, சுந்தர "
                            "காண்டம் பாராயணம் செய்து, செந்தூரமும் லட்டும் படைக்கிறார்கள். தமிழ்நாட்டில் அனுமன் "
                            "ஜெயந்தி மார்கழி மாத அமாவாசையில் தனியாகக் கொண்டாடப்படுகிறது."),
        "akshaya-tritiya": ("வைசாக வளர்பிறை திருதியையான அட்சய திருதியையில் செய்யும் ஒவ்வொரு நற்செயலும் 'அட்சயம்' "
                            "- குறையாதது - என்று நம்பப்படுகிறது. மக்கள் விஷ்ணுவையும் லட்சுமியையும் வழிபட்டு, "
                            "தானம் செய்து, புதிய முயற்சிகளைத் தொடங்குகிறார்கள் அல்லது தங்கம் வாங்குகிறார்கள்."),
        "raksha-bandhan": ("ஷ்ராவண பௌர்ணமியில் வரும் ரக்ஷா பந்தன், சகோதர-சகோதரி பாசத்தைக் கொண்டாடுகிறது. "
                           "சகோதரிகள் சகோதரனின் மணிக்கட்டில் ராக்கி கட்டி அவன் நலனுக்காக வேண்டுகிறார்கள்; ராக்கி "
                           "பத்ரா இல்லாத நேரத்தில் கட்டப்படுகிறது. தென்னிந்தியாவில் பெரும்பாலும் இதே நாளில் ஆவணி "
                           "அவிட்டம் (பூணூல் மாற்றுதல்) அனுசரிக்கப்படுகிறது."),
        "janmashtami": ("கிருஷ்ண ஜெயந்தி, பாத்ரபத மாதத் (பூர்ணிமாந்த முறை) தேய்பிறை அஷ்டமி நள்ளிரவில் ஸ்ரீ "
                        "கிருஷ்ணர் அவதரித்ததைக் கொண்டாடுகிறது. பக்தர்கள் பகல் முழுவதும் விரதம் இருந்து, நிசீத "
                        "(நள்ளிரவு) பூஜையில் குழந்தைக் கண்ணனுக்கு அபிஷேகம் செய்து தொட்டிலில் இட்ட பிறகு "
                        "விரதத்தை முடிக்கிறார்கள். தமிழ்நாட்டில் இது கோகுலாஷ்டமி - வாசலிலிருந்து பூஜை அறை வரை "
                        "கண்ணனின் சிறு பாதச் சுவடுகள் வரையப்படுகின்றன."),
        "ganesh-chaturthi": ("பாத்ரபத வளர்பிறை சதுர்த்தியில் வரும் விநாயகர் சதுர்த்தி, விநாயகப் பெருமானை "
                             "வீட்டுக்கு வரவேற்கும் திருநாள். அவர் அவதரித்த நேரமான மத்தியான (நண்பகல்) "
                             "முகூர்த்தத்தில் சிலை பிரதிஷ்டை செய்யப்பட்டு, மோதகம் (கொழுக்கட்டை), அருகம்புல், "
                             "சிவப்பு மலர்களால் வழிபடப்படுகிறது; இந்நாளில் சந்திரனைப் பார்ப்பது "
                             "தவிர்க்கப்படுகிறது."),
        "chaitra-navratri": ("வசந்த காலத்தில் துர்கா தேவிக்கான ஒன்பது இரவுகளான சைத்ர நவராத்திரி, சைத்ர வளர்பிறை "
                             "பிரதமையில் தொடங்குகிறது - இது இந்துப் புத்தாண்டும் (விக்ரம சம்வத்) ஆகும். கலச "
                             "ஸ்தாபனம் (கலசம் நிறுவுதல்) ஒன்பது நாள் வழிபாட்டைத் தொடங்கிவைக்கிறது."),
        "navratri": ("இலையுதிர் காலத்தில் துர்கா தேவிக்கான ஒன்பது இரவுகளான சாரதா நவராத்திரி, ஆஸ்வின "
                     "வளர்பிறை பிரதமையில் காலையில் கலச ஸ்தாபனத்துடன் - கலசம் நிறுவி, பார்லி விதைத்து - "
                     "தொடங்குகிறது. ஒவ்வொரு நாளும் தேவியின் ஒன்பது வடிவங்களில் ஒன்று வழிபடப்படுகிறது. "
                     "தமிழ்நாட்டில் இந்நாட்களில் வீடுகளில் கொலு வைத்து வழிபடுகிறார்கள்."),
        "dussehra": ("தசரா (விஜயதசமி), ஸ்ரீ ராமர் ராவணனை வென்றதையும் துர்கா தேவி மகிஷாசுரனை வென்றதையும் "
                     "குறிக்கிறது. சமி பூஜை, அபராஜிதா பூஜை, ராவண உருவ பொம்மை எரிப்பு ஆகியவை பிற்பகலில் "
                     "நடைபெறுகின்றன; விஜய முகூர்த்தம் எந்தப் புதிய தொடக்கத்துக்கும் உகந்ததாகக் "
                     "கருதப்படுகிறது. தமிழ்நாட்டில் முந்தைய நாள் ஆயுத பூஜை - சரஸ்வதி பூஜை; விஜயதசமி அன்று "
                     "குழந்தைகளுக்கு வித்யாரம்பம் (எழுத்தறிவித்தல்) நடைபெறுகிறது."),
        "karwa-chauth": ("கர்வா சௌத் அன்று திருமணமான பெண்கள் கணவரின் நீண்ட ஆயுளுக்காக சூரிய உதயம் முதல் சந்திர "
                         "உதயம் வரை விரதம் இருக்கிறார்கள். மாலையில் கர்வா மாதா பூஜைக்குப் பிறகு சந்திரனுக்கு "
                         "நீர் (அர்க்கியம்) அளித்து விரதத்தை முடிக்கிறார்கள்."),
        "ahoi-ashtami": ("தீபாவளிக்கு எட்டு நாள் முன் வரும் அஹோய் அஷ்டமி அன்று தாய்மார்கள் குழந்தைகளின் "
                         "நலனுக்காக விரதம் இருந்து மாலையில் அஹோய் மாதாவை வழிபடுகிறார்கள்; நட்சத்திரங்களைப் "
                         "பார்த்த பிறகு (சில குடும்பங்களில் சந்திரனைப் பார்த்த பிறகு) விரதம் "
                         "முடிக்கப்படுகிறது."),
        "dhanteras": ("தீபாவளியின் முதல் நாளான தன திரயோதசி (தந்தேரஸ்), தன்வந்திரியையும் லட்சுமி தேவியையும் "
                      "போற்றுகிறது. மக்கள் புதிய பாத்திரங்கள், தங்கம் அல்லது வெள்ளி வாங்கி, அந்தி வேளையில் "
                      "யம தீபம் ஏற்றுகிறார்கள்; பூஜை பிரதோஷ காலத்தில், முடிந்தால் ஸ்திர (நிலையான) ரிஷப "
                      "லக்னத்தில் செய்யப்படுகிறது."),
        "diwali": ("கார்த்திக அமாவாசையில் வரும் தீபாவளி, ஒளியின் திருநாள். மாலையில் பிரதோஷ காலத்தில் - "
                   "செல்வம் நிலைக்க வேண்டி, முடிந்தால் ஸ்திர ரிஷப லக்னத்தில் - லட்சுமியும் விநாயகரும் "
                   "வழிபடப்படுகிறார்கள்; வீடுகள் அகல் விளக்குகளால் ஒளிர்கின்றன. தமிழ்நாட்டில் தீபாவளி "
                   "பெரும்பாலும் நரக சதுர்த்தசி அதிகாலை எண்ணெய்க் குளியலுடன் (கங்கா ஸ்நானம்) "
                   "கொண்டாடப்படுகிறது."),
        "govardhan-puja": ("தீபாவளிக்கு மறுநாள் வரும் கோவர்த்தன பூஜை (அன்னகூடம்), கிருஷ்ணர் கோவர்த்தன மலையைத் "
                           "தூக்கியதை நினைவுகூர்கிறது. பசுஞ்சாணம் அல்லது உணவால் செய்த கோவர்த்தனம் வழிபடப்பட்டு, "
                           "பல வகை உணவுகளின் அன்னகூடம் படைக்கப்படுகிறது - வழக்கமாகக் காலையில் (பிராதக் காலம்)."),
        "bhai-dooj": ("கார்த்திக வளர்பிறை துவிதியையான பாய் தூஜ், சகோதர-சகோதரி உறவைக் கொண்டாடுகிறது: "
                      "சகோதரிகள் திலகமிட்டு, ஆரத்தி எடுத்து, சகோதரனின் நீண்ட ஆயுளுக்கு வேண்டுகிறார்கள் - "
                      "முடிந்தால் அபராஹ்ண (பிற்பகல்) நேரத்தில்."),
        "chhath-puja": ("சட் பூஜை, நான்கு நாட்கள் சூரிய தேவனையும் சட்டி மையாவையும் வழிபடும் விழா. முக்கிய "
                        "நாளில் (கார்த்திக வளர்பிறை சஷ்டி) பக்தர்கள் நீரில் நின்று மறையும் சூரியனுக்கும், "
                        "மறுநாள் காலை உதிக்கும் சூரியனுக்கும் அர்க்கியம் அளித்து, தண்ணீர் கூட அருந்தாமல் "
                        "இருந்த விரதத்தை முடிக்கிறார்கள்."),
        "vasant-panchami": ("மாக வளர்பிறை பஞ்சமியான வசந்த பஞ்சமி, வசந்தத்தை வரவேற்று சரஸ்வதி தேவியைப் "
                            "போற்றுகிறது. மாணவர்களும் கலைஞர்களும் புத்தகங்களையும் இசைக்கருவிகளையும் "
                            "வழிபடுகிறார்கள், மக்கள் மஞ்சள் ஆடை அணிகிறார்கள், குழந்தைகளுக்குப் பெரும்பாலும் "
                            "எழுத்தறிவித்தல் (வித்யாரம்பம்) தொடங்கப்படுகிறது."),
        "guru-purnima": ("ஆஷாட பௌர்ணமியான குரு பௌர்ணமி, ஆசிரியர்களையும் இந்நாளில் பிறந்த வேத வியாச "
                         "மகரிஷியையும் போற்றுகிறது. சீடர்கள் தங்கள் குருவுக்கு நன்றி செலுத்தி, மலர்களும் "
                         "காணிக்கைகளும் அளிக்கிறார்கள்."),
        "sharad-purnima": ("ஆஸ்வின பௌர்ணமியான சரத் பௌர்ணமி, சந்திரன் மிகப் பிரகாசமாக, அமிர்தம் நிறைந்து "
                           "இருப்பதாகக் கருதப்படும் இரவு. பால் பாயசம் (கீர்) இரவு முழுவதும் நிலவொளியில் "
                           "வைக்கப்பட்டு பிரசாதமாக உண்ணப்படுகிறது; லட்சுமி வழிபாடும் (கோஜாகரி) நடைபெறுகிறது."),
        "devuthani-ekadashi": ("கார்த்திக வளர்பிறை ஏகாதசியான தேவுத்தானி (பிரபோதினி) ஏகாதசி அன்று, ஸ்ரீ விஷ்ணு நான்கு "
                               "மாத யோக நித்திரையிலிருந்து எழுவதாகக் கருதப்படுகிறது; சாதுர்மாசியம் நிறைவடைகிறது. "
                               "துளசி விவாகம் தொடங்கி, திருமணக் காலம் ஆரம்பமாகிறது. பக்தர்கள் விரதம் இருந்து மறுநாள் "
                               "பாரணை செய்கிறார்கள்."),
        "jivitputrika": ("ஜீவித்புத்ரிகா (ஜிதியா, ஜியுதியா) விரதத்தை பிகார், ஜார்க்கண்ட், கிழக்கு உத்தரப் "
                         "பிரதேசம், நேபாளத் தாய்மார்கள் குழந்தைகளின் நீண்ட ஆயுளுக்கும் நலனுக்குமாக ஆஸ்வின "
                         "தேய்பிறை அஷ்டமியில் (பூர்ணிமாந்த முறை) கடைப்பிடிக்கிறார்கள். முந்தைய நாள் "
                         "'நஹாய்-காய்' உடன் தொடங்குகிறது; விரதம் நிர்ஜலம் - பகலும் இரவும் தண்ணீர் கூட இல்லாமல் "
                         "- ஜீமூதவாகனர் வழிபாடும் ஜிதியா கதையும் உண்டு. விரதம் முடிக்கும் பாரணை மறுநாள் காலை."),
        "lohri": ("மகர சங்கராந்திக்கு முந்தைய மாலை வரும் லோஹ்ரி, பஞ்சாப் மற்றும் வட இந்தியாவின் "
                  "குளிர்கால அறுவடைத் திருநாள். அந்தி வேளையில் தீ மூட்டி, எள், வெல்லம், ரேவடி, "
                  "வேர்க்கடலை, பாப்கார்ன் ஆகியவற்றை அதில் இட்டு, பாடி ஆடுகிறார்கள்; புதுமணப் பெண் "
                  "அல்லது புதிதாகப் பிறந்த குழந்தை உள்ள வீடுகளில் இது சிறப்பாகக் கொண்டாடப்படுகிறது."),
        "sakat-chauth": ("சகட் சௌத் (தில்குட் சௌத்) - மாக மாதத்தின் (பூர்ணிமாந்த முறை) சங்கடஹர சதுர்த்தி - "
                         "தாய்மார்கள் குழந்தைகளுக்காகக் கடைப்பிடிக்கும் விரதம். விநாயகரும் சகட் மாதாவும் எள், "
                         "வெல்லத்தால் வழிபடப்பட்டு, உதிக்கும் சந்திரனுக்கு அர்க்கியம் அளித்த பின் விரதம் "
                         "முடிக்கப்படுகிறது."),
        "mauni-amavasya": ("மாக மாத (பூர்ணிமாந்த முறை) அமாவாசையான மௌனி அமாவாசை, பிரயாக்ராஜ் மாக மேளாவின் பெரும் "
                           "புனித நீராடல் நாள். பக்தர்கள் கங்கையிலோ புனித நதியிலோ நீராடி, மௌனம் காத்து, தானம் "
                           "செய்கிறார்கள்."),
        "sheetala-ashtami": ("சீதளா அஷ்டமி (பசோடா), சைத்ர தேய்பிறை அஷ்டமி (பூர்ணிமாந்த முறை), காய்ச்சல், அம்மை "
                             "நோய்களிலிருந்து காக்கும் சீதளா மாதாவைப் போற்றுகிறது. முந்தைய நாளே சமைத்த ஆறிய உணவு "
                             "படைக்கப்பட்டு உண்ணப்படுகிறது; அன்று சமையலுக்கு அடுப்பு மூட்டுவதில்லை."),
        "gudi-padwa": ("குடி பாட்வா (மகாராஷ்டிரா), யுகாதி (கர்நாடகா, ஆந்திரா, தெலங்கானா) - சைத்ர வளர்பிறை "
                       "பிரதமையில் வரும் சந்திரமானப் புத்தாண்டு. வாசலில் 'குடி' - துணியும் கலசமும் அணிவித்த "
                       "அலங்காரக் கம்பம் - நாட்டப்படுகிறது; இனிப்பும் கசப்பும் கலந்த ஆண்டுக்கு அடையாளமாக "
                       "வேப்பம்பூவும் வெல்லமும் உண்ணப்படுகிறது. (தமிழ்ப் புத்தாண்டு, சூரிய மாதமான சித்திரை "
                       "முதல் நாளில், தனியாக வருகிறது.)"),
        "gangaur": ("சைத்ர வளர்பிறை திருதியையான கணகௌர், கௌரி (பார்வதி) - சிவனுக்கான ராஜஸ்தானின் திருநாள். "
                    "மணவாழ்வு மகிழ்ச்சிக்காகப் பெண்கள் கௌரியை வழிபடுகிறார்கள் - திருமணமானவர்கள் "
                    "கணவருக்காக, இளம் பெண்கள் நல்ல வரனுக்காக; ஹோலிக்கு மறுநாள் தொடங்கும் பதினெட்டு நாள் "
                    "பூஜை இந்நாளில் நிறைவடைகிறது."),
        "vat-savitri": ("வட இந்தியாவில் (பூர்ணிமாந்த முறை) ஜ்யேஷ்ட அமாவாசையில் வரும் வட சாவித்திரி விரதம், "
                        "எமனிடமிருந்து கணவர் சத்தியவானின் உயிரை மீட்ட சாவித்திரியை நினைவுகூர்கிறது. திருமணமான "
                        "பெண்கள் விரதம் இருந்து, ஆலமரத்தை (வடம்) வழிபட்டு, அதைச் சுற்றி வந்து நூல் கட்டி, "
                        "சாவித்திரி கதையைக் கேட்கிறார்கள்."),
        "vat-purnima": ("வட பௌர்ணமி என்பது அதே வட சாவித்திரி விரதம் - மகாராஷ்டிரா, குஜராத், தென்னிந்தியாவில் "
                        "(அமாந்த நாட்காட்டி) ஜ்யேஷ்ட பௌர்ணமியில், வட இந்தியத் தேதிக்குப் பதினைந்து நாள் "
                        "கழித்துக் கடைப்பிடிக்கப்படுகிறது. திருமணமான பெண்கள் கணவரின் நீண்ட ஆயுளுக்காக விரதம் "
                        "இருந்து ஆலமரத்தை வழிபடுகிறார்கள்."),
        "ganga-dussehra": ("ஜ்யேஷ்ட வளர்பிறை தசமியான கங்கா தசரா, பகீரதனின் தவத்தால் கங்கை பூமிக்கு இறங்கியதைக் "
                           "கொண்டாடுகிறது. பக்தர்கள் கங்கையில் நீராடி, தீபங்கள் சமர்ப்பித்து, தானம் "
                           "செய்கிறார்கள்; இந்த நீராடல் பத்து வகைப் பாவங்களைப் போக்குவதாக நம்பப்படுகிறது."),
        "hariyali-teej": ("ஷ்ராவண வளர்பிறை திருதியையான ஹரியாலி தீஜ், மழைக்காலத்தில் சிவன்-பார்வதி மீண்டும் "
                          "இணைந்ததைக் கொண்டாடுகிறது. பெண்கள் பச்சை ஆடை அணிந்து, மருதாணி இட்டு, அலங்கார "
                          "ஊஞ்சல்களில் ஆடி, சாவன் பாடல்கள் பாடுகிறார்கள்; பலர் கணவருக்காக விரதம் "
                          "இருக்கிறார்கள்."),
        "nag-panchami": ("ஷ்ராவண வளர்பிறை பஞ்சமியான நாக பஞ்சமி, நாக தெய்வங்களை வழிபடும் நாள். பாம்பு உருவங்கள் "
                         "வரையப்பட்டு அல்லது வைக்கப்பட்டு, பால், மலர், இனிப்புகள் படைத்து, குடும்பத்தின் "
                         "பாதுகாப்புக்காக வேண்டுகிறார்கள். (குஜராத்தில் நாக பஞ்சம் பின்னர், பாத்ரபத மாதத்தில் "
                         "வருகிறது.)"),
        "kajari-teej": ("கஜரி (கஜ்லி, படி) தீஜ், பாத்ரபத தேய்பிறை திருதியை (பூர்ணிமாந்த முறை), உத்தரப் "
                        "பிரதேசம், பிகார், ராஜஸ்தான், மத்தியப் பிரதேசத் திருமணமான பெண்களால் "
                        "கடைப்பிடிக்கப்படுகிறது. அவர்கள் விரதம் இருந்து, வேப்ப மரத்தை (நீமடி மாதா) வழிபட்டு, "
                        "சந்திரனுக்கு அர்க்கியம் அளித்த பின் விரதத்தை முடிக்கிறார்கள்; கஜரி நாட்டுப்புறப் "
                        "பாடல்கள் பாடப்படுகின்றன."),
        "hal-shashthi": ("ஹல சஷ்டி (லலஹி சட், ஹர் சட்), பாத்ரபத தேய்பிறை சஷ்டி (பூர்ணிமாந்த முறை), கலப்பையை "
                         "(ஹலம்) ஆயுதமாகக் கொண்ட பலராமரின் பிறந்த நாள். தாய்மார்கள் குழந்தைகளுக்காக விரதம் "
                         "இருந்து, கலப்பையால் உழுது விளைந்த எதையும் உண்பதில்லை - பெரும்பாலும் பசாஹி அரிசியும் "
                         "எருமைப் பாலும் உண்கிறார்கள்."),
        "hartalika-teej": ("பாத்ரபத வளர்பிறை திருதியையான ஹர்தாலிகா தீஜ், சிவனை அடையப் பார்வதி செய்த தவத்தைப் "
                           "போற்றுகிறது. பெண்கள் நிர்ஜல விரதம் இருந்து, சிவன்-பார்வதியின் களிமண் உருவங்களைச் "
                           "செய்து வழிபடுகிறார்கள் (காலையில் பிராதக் கால பூஜை சிறந்தது), இரவு கண்விழித்து, "
                           "மறுநாள் காலை விரதத்தை முடிக்கிறார்கள்."),
        "rishi-panchami": ("பாத்ரபத வளர்பிறை பஞ்சமியான ரிஷி பஞ்சமி, சப்த ரிஷிகளைப் போற்றுகிறது. குறிப்பாகப் "
                           "பெண்கள் நீராடி, விரதம் இருந்து, நண்பகலில் (மத்தியானம்) ரிஷிகளை வழிபட்டு, அறியாமல் "
                           "செய்த தவறுகளிலிருந்து தூய்மை வேண்டுகிறார்கள்."),
        "anant-chaturdashi": ("பாத்ரபத வளர்பிறை சதுர்த்தசியான அனந்த சதுர்த்தசி, ஸ்ரீ விஷ்ணுவை அனந்தராக வழிபடும் "
                              "நாள். பூஜைக்குப் பின் பதினான்கு முடிச்சுகள் கொண்ட புனித நூல் (அனந்த சூத்திரம்) "
                              "கையில் கட்டப்படுகிறது; விநாயகர் சிலைகள் கரைக்கப்படும் (விநாயகர் விசர்ஜனம்) நாளும் "
                              "இதுவே."),
        "pitru-paksha": ("முன்னோர்களுக்கான பதினைந்து நாட்களான பித்ரு பட்சம் (மகாளய பட்சம்), ஆஸ்வின மாதத் "
                         "(பூர்ணிமாந்த முறை) தேய்பிறை பிரதமை முதல் அமாவாசை வரை நீள்கிறது. ஒரு முன்னோர் மறைந்த "
                         "திதியில், குடும்பங்கள் தர்ப்பணமும் சிராத்தமும் - பிண்டம், அந்தணர்களுக்கு உணவு, பசு, "
                         "காகம், நாய்க்கு உணவு - குதப, ரௌஹிண அல்லது அபராஹ்ண நேரத்தில் செய்கிறார்கள்."),
        "sarva-pitru-amavasya": ("சர்வ பித்ரு அமாவாசை (மகாளய அமாவாசை) பித்ரு பட்சத்தை நிறைவு செய்கிறது. இந்நாளில் "
                                 "செய்யும் சிராத்தம், திதி தெரியாதவர்கள் உட்பட எல்லா முன்னோர்களையும் சென்றடைகிறது; இது "
                                 "குதப, ரௌஹிண அல்லது அபராஹ்ண நேரத்தில் செய்யப்படுகிறது."),
        "narak-chaturdashi": ("நரக சதுர்த்தசி (ரூப் சௌதஸ்), கார்த்திக தேய்பிறை சதுர்த்தசி (பூர்ணிமாந்த முறை), "
                              "நரகாசுரனைக் கிருஷ்ணர் வென்றதை நினைவுகூர்கிறது. சூரிய உதயத்துக்கு முன், சந்திரன் "
                              "வானில் இருக்கும்போதே, மக்கள் மூலிகைப் பொடி தேய்த்து எண்ணெய்க் குளியல் (அப்யங்க "
                              "ஸ்நானம்) செய்கிறார்கள்; மாலையில் எமனுக்கு விளக்கு ஏற்றப்படுகிறது."),
        "tulsi-vivah": ("கார்த்திக வளர்பிறை துவாதசியில் நடைபெறும் துளசி விவாகம், துளசிச் செடிக்கு "
                        "(விருந்தையாக) சாளக்கிராம வடிவிலான ஸ்ரீ விஷ்ணுவுடன் நடத்தப்படும் சடங்குத் திருமணம். "
                        "குடும்பங்கள் துளசியை மணப்பெண் போல அலங்கரித்து, திருமணச் சடங்குகளை நடத்துகின்றன; அதன் "
                        "பிறகு இந்துத் திருமணக் காலம் தொடங்குகிறது."),
        "kartik-purnima": ("கார்த்திக பௌர்ணமி, புனிதமான கார்த்திக மாதத்தை நிறைவு செய்கிறது. கங்கையிலோ புனித "
                           "நதியிலோ நீராடவும் தானம் செய்யவும் சிறந்த நாள்; குரு நானக் ஜெயந்தியும், சிவன் "
                           "திரிபுராசுரனை அழித்த திரிபுரி பௌர்ணமியும் இதுவே. (தமிழ்நாட்டின் கார்த்திகை தீபம் "
                           "சூரிய மாதமான கார்த்திகையில் கார்த்திகை நட்சத்திரத்தன்று வருவதால், தேதி வேறுபடலாம்.)"),
        "dev-deepawali": ("'தேவர்களின் தீபாவளி' எனப்படும் தேவ தீபாவளி, கார்த்திக பௌர்ணமி மாலையில், குறிப்பாக "
                          "லட்சக்கணக்கான அகல் விளக்குகளால் ஒளிரும் வாரணாசி படித்துறைகளில் கொண்டாடப்படுகிறது. "
                          "சிவன் திரிபுராசுரனை வென்றதை இது குறிக்கிறது; பிரதோஷ காலத்தில் கங்கைக்கு விளக்குகள் "
                          "சமர்ப்பிக்கப்படுகின்றன."),
    },

    # Malayalam (DIVASTRO-123)
    "ml": {
        "makar-sankranti": ("സൂര്യൻ മകരം രാശിയിൽ പ്രവേശിച്ച് വടക്കോട്ടുള്ള യാത്ര (ഉത്തരായണം) ആരംഭിക്കുന്ന "
                            "ദിവസമാണ് മകരസംക്രാന്തി. ഇതൊരു വിളവെടുപ്പ് ഉത്സവമാണ്: ആളുകൾ പുണ്യനദികളിൽ സ്നാനം "
                            "ചെയ്യുന്നു, എള്ള്, ശർക്കര, കിച്ചടി, കമ്പിളി എന്നിവ ദാനം ചെയ്യുന്നു, പട്ടം "
                            "പറത്തുന്നു. കേരളത്തിൽ ഈ ദിവസമാണ് ശബരിമലയിലെ മകരവിളക്ക്."),
        "maha-shivratri": ("ശിവന്റെ മഹാരാത്രിയായ മഹാശിവരാത്രി മാഘ മാസത്തിലെ കൃഷ്ണപക്ഷ ചതുർദശിയിലാണ്. ഭക്തർ "
                           "വ്രതമെടുത്ത്, ശിവലിംഗത്തിൽ ജലം, പാൽ, കൂവളത്തില എന്നിവ അർപ്പിച്ച്, ഓം നമഃ ശിവായ "
                           "ജപിച്ച്, രാത്രിയുടെ നാല് യാമങ്ങളിലും ഉറക്കമൊഴിയുന്നു; അർധരാത്രിയോടടുത്ത നിശീഥ കാല "
                           "പൂജയാണ് ഏറ്റവും പ്രധാനം. കേരളത്തിൽ ആലുവ മണപ്പുറത്തെ ശിവരാത്രി പ്രസിദ്ധമാണ്."),
        "holika-dahan": ("ഹോളിയുടെ തലേന്നത്തെ ഹോളികാ ദഹനം പ്രഹ്ലാദന്റെ ഭക്തിയെയും തിന്മയ്ക്കു മേൽ നന്മയുടെ "
                         "വിജയത്തെയും ആഘോഷിക്കുന്നു. സൂര്യാസ്തമയത്തിനു ശേഷം, ഭദ്ര ഒഴിവാക്കി, അഗ്നി "
                         "കൊളുത്തുന്നു; കുടുംബങ്ങൾ ധാന്യവും തേങ്ങയും അർപ്പിച്ച് പ്രാർഥനയോടെ അതിനെ "
                         "വലംവയ്ക്കുന്നു."),
        "holi": ("നിറങ്ങളുടെ ഉത്സവമായ ഹോളി ഹോളികാ ദഹനത്തിന്റെ പിറ്റേന്ന് രാവിലെ ആഘോഷിക്കുന്നു - "
                 "നിറങ്ങൾ, സംഗീതം, ഗുജിയ പോലുള്ള മധുരപലഹാരങ്ങൾ, ബന്ധുമിത്രാദികളെ സന്ദർശിക്കൽ "
                 "എന്നിവയോടെ."),
        "ram-navami": ("ചൈത്ര ശുക്ല നവമിയിൽ മധ്യാഹ്നത്തിൽ ശ്രീരാമൻ അവതരിച്ചതിന്റെ ആഘോഷമാണ് ശ്രീരാമനവമി. "
                       "ഭക്തർ വ്രതമെടുത്ത്, രാമചരിതമാനസം (രാമായണം) വായിച്ച്, അദ്ദേഹത്തിന്റെ ജനനസമയമായ "
                       "മധ്യാഹ്ന മുഹൂർത്തത്തിൽ പൂജ ചെയ്യുന്നു."),
        "hanuman-jayanti": ("ഹനുമാൻ ജയന്തി (ഉത്തരേന്ത്യയിൽ ചൈത്ര പൗർണമി) ശ്രീ ഹനുമാന്റെ ജനനം ആഘോഷിക്കുന്നു. ഭക്തർ "
                            "ഹനുമാൻ ക്ഷേത്രങ്ങൾ സന്ദർശിച്ച്, ഹനുമാൻ ചാലീസയും സുന്ദരകാണ്ഡവും പാരായണം ചെയ്ത്, "
                            "സിന്ദൂരവും ലഡ്ഡുവും സമർപ്പിക്കുന്നു."),
        "akshaya-tritiya": ("വൈശാഖ ശുക്ല തൃതീയയായ അക്ഷയ തൃതീയയിൽ ചെയ്യുന്ന ഓരോ സത്കർമവും 'അക്ഷയം' - ഒരിക്കലും "
                            "കുറയാത്തത് - ആകുമെന്നാണ് വിശ്വാസം. ആളുകൾ വിഷ്ണുവിനെയും ലക്ഷ്മിയെയും ആരാധിക്കുന്നു, "
                            "ദാനം ചെയ്യുന്നു, പുതിയ സംരംഭങ്ങൾ തുടങ്ങുകയോ സ്വർണം വാങ്ങുകയോ ചെയ്യുന്നു."),
        "raksha-bandhan": ("ശ്രാവണ പൗർണമിയിലെ രക്ഷാബന്ധൻ സഹോദരീസഹോദരന്മാരുടെ ബന്ധം ആഘോഷിക്കുന്നു. സഹോദരിമാർ "
                           "സഹോദരന്റെ കൈത്തണ്ടയിൽ രാഖി കെട്ടി അവന്റെ ക്ഷേമത്തിനായി പ്രാർഥിക്കുന്നു; "
                           "ഭദ്രയില്ലാത്ത സമയത്താണ് രാഖി കെട്ടുന്നത്. ദക്ഷിണേന്ത്യയിൽ പലപ്പോഴും ഇതേ ദിവസമാണ് "
                           "ആവണി അവിട്ടം (പൂണൂൽ മാറ്റൽ)."),
        "janmashtami": ("ഭാദ്രപദ (പൂർണിമാന്ത) കൃഷ്ണപക്ഷ അഷ്ടമിയിലെ അർധരാത്രിയിൽ ശ്രീകൃഷ്ണൻ ജനിച്ചതിന്റെ "
                        "ആഘോഷമാണ് ശ്രീകൃഷ്ണ ജന്മാഷ്ടമി. ഭക്തർ പകൽ മുഴുവൻ വ്രതമെടുത്ത്, ഉണ്ണിക്കൃഷ്ണനെ അഭിഷേകം "
                        "ചെയ്ത് തൊട്ടിലിൽ കിടത്തുന്ന നിശീഥ (അർധരാത്രി) പൂജയ്ക്കു ശേഷം വ്രതം മുറിക്കുന്നു. "
                        "കേരളത്തിൽ ഇത് അഷ്ടമിരോഹിണിയാണ് - ചിങ്ങമാസത്തിൽ അഷ്ടമിയും രോഹിണിയും ചേരുന്ന ദിവസം, "
                        "അതിനാൽ കേരളത്തിലെ തീയതി ചിലപ്പോൾ വ്യത്യാസപ്പെടാം."),
        "ganesh-chaturthi": ("ഭാദ്രപദ ശുക്ല ചതുർഥിയിലെ വിനായക ചതുർഥി ഗണപതിയെ വീട്ടിലേക്ക് സ്വാഗതം ചെയ്യുന്നു. "
                             "അദ്ദേഹത്തിന്റെ ജനനസമയമായ മധ്യാഹ്ന മുഹൂർത്തത്തിൽ വിഗ്രഹം പ്രതിഷ്ഠിച്ച് മോദകം "
                             "(കൊഴുക്കട്ട), കറുകപ്പുല്ല്, ചുവന്ന പൂക്കൾ എന്നിവ കൊണ്ട് പൂജിക്കുന്നു; ഈ ദിവസം "
                             "ചന്ദ്രനെ നോക്കുന്നത് ഒഴിവാക്കുന്നു."),
        "chaitra-navratri": ("വസന്തകാലത്ത് ദുർഗാദേവിയുടെ ഒൻപത് രാത്രികളായ ചൈത്ര നവരാത്രി ചൈത്ര ശുക്ല പ്രഥമയിൽ "
                             "ആരംഭിക്കുന്നു - ഇത് ഹിന്ദു പുതുവർഷവും (വിക്രമ സംവത്) ആണ്. ഘടസ്ഥാപനം (കലശം "
                             "സ്ഥാപിക്കൽ) ഒൻപത് ദിവസത്തെ ആരാധനയ്ക്ക് തുടക്കം കുറിക്കുന്നു."),
        "navratri": ("ശരത്കാലത്ത് ദുർഗാദേവിയുടെ ഒൻപത് രാത്രികളായ ശാരദ നവരാത്രി ആശ്വിന ശുക്ല പ്രഥമയിൽ "
                     "രാവിലെ ഘടസ്ഥാപനത്തോടെ - കലശം സ്ഥാപിച്ച് യവം വിതച്ച് - ആരംഭിക്കുന്നു. ഓരോ ദിവസവും "
                     "ദേവിയുടെ ഒൻപത് രൂപങ്ങളിൽ ഒന്നിനെ ആരാധിക്കുന്നു. കേരളത്തിൽ ദുർഗാഷ്ടമിക്ക് പൂജവയ്പ്പും "
                     "മഹാനവമിയും കഴിഞ്ഞ് വിജയദശമിക്ക് വിദ്യാരംഭം നടക്കുന്നു."),
        "dussehra": ("ദസറ (വിജയദശമി) ശ്രീരാമൻ രാവണനെയും ദുർഗാദേവി മഹിഷാസുരനെയും ജയിച്ചതിന്റെ ഓർമയാണ്. ശമീ "
                     "പൂജ, അപരാജിതാ പൂജ, രാവണ കോലം കത്തിക്കൽ എന്നിവ ഉച്ചതിരിഞ്ഞാണ്; വിജയ മുഹൂർത്തം പുതിയ "
                     "എന്തും തുടങ്ങാൻ ഉത്തമമായി കരുതപ്പെടുന്നു. കേരളത്തിൽ ഈ ദിവസം കുട്ടികളെ ആദ്യാക്ഷരം "
                     "കുറിക്കുന്ന വിദ്യാരംഭമാണ്."),
        "karwa-chauth": ("കർവാ ചൗത്തിൽ വിവാഹിതരായ സ്ത്രീകൾ ഭർത്താവിന്റെ ദീർഘായുസ്സിനായി സൂര്യോദയം മുതൽ "
                         "ചന്ദ്രോദയം വരെ വ്രതമെടുക്കുന്നു. വൈകുന്നേരം കർവാ മാതാ പൂജയ്ക്കു ശേഷം ചന്ദ്രന് ജലം "
                         "(അർഘ്യം) അർപ്പിച്ച് വ്രതം മുറിക്കുന്നു."),
        "ahoi-ashtami": ("ദീപാവലിക്ക് എട്ടു ദിവസം മുമ്പുള്ള അഹോയി അഷ്ടമിയിൽ അമ്മമാർ കുട്ടികളുടെ ക്ഷേമത്തിനായി "
                         "വ്രതമെടുത്ത് വൈകുന്നേരം അഹോയി മാതാവിനെ ആരാധിക്കുന്നു; നക്ഷത്രങ്ങളെ (ചില കുടുംബങ്ങളിൽ "
                         "ചന്ദ്രനെ) കണ്ട ശേഷമാണ് പരമ്പരാഗതമായി വ്രതം മുറിക്കുന്നത്."),
        "dhanteras": ("ദീപാവലിയുടെ ആദ്യ ദിവസമായ ധനത്രയോദശി (ധൻതേരസ്) ധന്വന്തരിയെയും ലക്ഷ്മീദേവിയെയും "
                      "ആദരിക്കുന്നു. ആളുകൾ പുതിയ പാത്രങ്ങളോ സ്വർണമോ വെള്ളിയോ വാങ്ങുകയും സന്ധ്യയ്ക്ക് യമദീപം "
                      "കൊളുത്തുകയും ചെയ്യുന്നു; പൂജ പ്രദോഷ കാലത്ത്, സാധ്യമെങ്കിൽ സ്ഥിര ലഗ്നമായ ഇടവ "
                      "ലഗ്നത്തിൽ, ചെയ്യുന്നു."),
        "diwali": ("കാർത്തിക അമാവാസിയിലെ ദീപാവലി ദീപങ്ങളുടെ ഉത്സവമാണ്. വൈകുന്നേരം പ്രദോഷ കാലത്ത് - "
                   "ഐശ്വര്യം നിലനിൽക്കാൻ, സാധ്യമെങ്കിൽ സ്ഥിര ലഗ്നമായ ഇടവ ലഗ്നത്തിൽ - ലക്ഷ്മിയെയും "
                   "ഗണപതിയെയും പൂജിക്കുന്നു; വീടുകൾ ചെരാതുകൾ കൊണ്ട് ദീപാലംകൃതമാക്കുന്നു. കേരളത്തിൽ "
                   "ദീപാവലി പ്രധാനമായും നരക ചതുർദശിയിലെ പുലർച്ചെയുള്ള എണ്ണതേച്ചുകുളിയോടെയാണ് "
                   "ആഘോഷിക്കുന്നത്."),
        "govardhan-puja": ("ദീപാവലിയുടെ പിറ്റേന്നുള്ള ഗോവർധന പൂജ (അന്നകൂട്) ശ്രീകൃഷ്ണൻ ഗോവർധന പർവതം "
                           "ഉയർത്തിയതിന്റെ ഓർമയാണ്. ചാണകം കൊണ്ടോ ഭക്ഷണം കൊണ്ടോ ഉണ്ടാക്കിയ ഗോവർധനത്തെ പൂജിച്ച്, "
                           "അനേകം വിഭവങ്ങളുടെ അന്നകൂട് സമർപ്പിക്കുന്നു - സാധാരണയായി രാവിലെ (പ്രാതഃകാലം)."),
        "bhai-dooj": ("കാർത്തിക ശുക്ല ദ്വിതീയയിലെ ഭായി ദൂജ് സഹോദരീസഹോദരന്മാരുടെ ആഘോഷമാണ്: സഹോദരിമാർ തിലകം "
                      "ചാർത്തി, ആരതി ഉഴിഞ്ഞ്, സഹോദരന്റെ ദീർഘായുസ്സിനായി പ്രാർഥിക്കുന്നു - സാധ്യമെങ്കിൽ "
                      "അപരാഹ്ന (ഉച്ചതിരിഞ്ഞ്) സമയത്ത്."),
        "chhath-puja": ("ഛഠ് പൂജ നാലു ദിവസങ്ങളിലായി സൂര്യദേവനെയും ഛഠി മയ്യയെയും ആരാധിക്കുന്നു. പ്രധാന ദിവസം "
                        "(കാർത്തിക ശുക്ല ഷഷ്ഠി) ഭക്തർ വെള്ളത്തിൽ നിന്ന് അസ്തമിക്കുന്ന സൂര്യനും പിറ്റേന്ന് "
                        "രാവിലെ ഉദിക്കുന്ന സൂര്യനും അർഘ്യം അർപ്പിച്ച്, ജലപാനം പോലുമില്ലാതെ അനുഷ്ഠിച്ച വ്രതം "
                        "അവസാനിപ്പിക്കുന്നു."),
        "vasant-panchami": ("മാഘ ശുക്ല പഞ്ചമിയിലെ വസന്ത പഞ്ചമി വസന്തത്തെ വരവേൽക്കുകയും സരസ്വതീദേവിയെ ആദരിക്കുകയും "
                            "ചെയ്യുന്നു. വിദ്യാർഥികളും കലാകാരന്മാരും പുസ്തകങ്ങളെയും വാദ്യോപകരണങ്ങളെയും "
                            "പൂജിക്കുന്നു, ആളുകൾ മഞ്ഞ വസ്ത്രം ധരിക്കുന്നു, കുട്ടികൾ പലപ്പോഴും എഴുത്തിനിരുത്തൽ "
                            "(വിദ്യാരംഭം) നടത്തുന്നു."),
        "guru-purnima": ("ആഷാഢ പൗർണമിയിലെ ഗുരു പൂർണിമ ഗുരുക്കന്മാരെയും ഈ ദിവസം ജനിച്ച വേദവ്യാസ മഹർഷിയെയും "
                         "ആദരിക്കുന്നു. ശിഷ്യർ തങ്ങളുടെ ഗുരുവിന് നന്ദിയും പൂക്കളും കാണിക്കകളും അർപ്പിക്കുന്നു."),
        "sharad-purnima": ("ആശ്വിന പൗർണമിയിലെ ശരത് പൂർണിമ, ചന്ദ്രൻ ഏറ്റവും തിളക്കമുള്ളതും അമൃതം നിറഞ്ഞതുമാണെന്ന് "
                           "കരുതപ്പെടുന്ന രാത്രിയാണ്. പാൽപ്പായസം (ഖീർ) രാത്രി മുഴുവൻ നിലാവിൽ വച്ച് പ്രസാദമായി "
                           "കഴിക്കുന്നു; ലക്ഷ്മീപൂജയും (കോജാഗരി) നടക്കുന്നു."),
        "devuthani-ekadashi": ("കാർത്തിക ശുക്ല ഏകാദശിയായ ദേവുത്ഥാനി (പ്രബോധിനി) ഏകാദശിയിൽ മഹാവിഷ്ണു നാലു മാസത്തെ "
                               "യോഗനിദ്രയിൽ നിന്ന് ഉണരുന്നുവെന്നാണ് വിശ്വാസം; ചാതുർമാസ്യം അവസാനിക്കുന്നു. തുളസി "
                               "വിവാഹം ആരംഭിക്കുകയും വിവാഹകാലം തുടങ്ങുകയും ചെയ്യുന്നു. ഭക്തർ വ്രതമെടുത്ത് പിറ്റേന്ന് "
                               "പാരണ ചെയ്യുന്നു."),
        "jivitputrika": ("ബിഹാർ, ഝാർഖണ്ഡ്, കിഴക്കൻ ഉത്തർപ്രദേശ്, നേപ്പാൾ എന്നിവിടങ്ങളിലെ അമ്മമാർ കുട്ടികളുടെ "
                         "ദീർഘായുസ്സിനും ക്ഷേമത്തിനുമായി ആശ്വിന കൃഷ്ണ അഷ്ടമിയിൽ (പൂർണിമാന്ത) ആചരിക്കുന്ന "
                         "വ്രതമാണ് ജീവിത്പുത്രിക (ജിതിയ, ജിയുതിയ). തലേന്ന് 'നഹായ്-ഖായ്'യോടെ ആരംഭിക്കുന്നു; "
                         "വ്രതം നിർജലമാണ് - പകലും രാത്രിയും ജലമില്ലാതെ - ജീമൂതവാഹന പൂജയും ജിതിയ കഥയും ഉണ്ട്. "
                         "വ്രതം മുറിക്കുന്ന പാരണ പിറ്റേന്ന് രാവിലെയാണ്."),
        "lohri": ("മകരസംക്രാന്തിയുടെ തലേന്ന് വൈകുന്നേരമുള്ള ലോഹ്രി പഞ്ചാബിന്റെയും ഉത്തരേന്ത്യയുടെയും "
                  "ശൈത്യകാല വിളവെടുപ്പ് ഉത്സവമാണ്. സന്ധ്യയ്ക്ക് അഗ്നി കൊളുത്തി എള്ള്, ശർക്കര, രേവ്ഡി, "
                  "നിലക്കടല, പോപ്കോൺ എന്നിവ അർപ്പിച്ച് പാടുകയും നൃത്തം ചെയ്യുകയും ചെയ്യുന്നു; നവവധുവോ "
                  "നവജാത ശിശുവോ ഉള്ള വീടുകളിൽ ഇത് പ്രത്യേകമായി ആഘോഷിക്കുന്നു."),
        "sakat-chauth": ("സകട് ചൗത്ത് (തിൽകുട് ചൗത്ത്) - മാഘ മാസത്തിലെ (പൂർണിമാന്ത) സങ്കഷ്ടി ചതുർഥി - അമ്മമാർ "
                         "കുട്ടികൾക്കായി ആചരിക്കുന്നു. ഗണപതിയെയും സകട് മാതാവിനെയും എള്ളും ശർക്കരയും കൊണ്ട് "
                         "പൂജിച്ച്, ഉദിക്കുന്ന ചന്ദ്രന് അർഘ്യം അർപ്പിച്ച ശേഷം വ്രതം മുറിക്കുന്നു."),
        "mauni-amavasya": ("മാഘ മാസത്തിലെ (പൂർണിമാന്ത) അമാവാസിയായ മൗനി അമാവാസി പ്രയാഗ്‌രാജിലെ മാഘമേളയുടെ "
                           "മഹാസ്നാന ദിനമാണ്. ഭക്തർ ഗംഗയിലോ പുണ്യനദിയിലോ സ്നാനം ചെയ്ത്, മൗനം പാലിച്ച്, ദാനം "
                           "ചെയ്യുന്നു."),
        "sheetala-ashtami": ("ശീതളാ അഷ്ടമി (ബസോഡ), ചൈത്ര കൃഷ്ണ അഷ്ടമി (പൂർണിമാന്ത), പനിയിൽ നിന്നും വസൂരിയിൽ "
                             "നിന്നും സംരക്ഷിക്കുന്ന ശീതളാ മാതാവിനെ ആദരിക്കുന്നു. തലേന്ന് പാകം ചെയ്ത ഭക്ഷണം "
                             "നിവേദിച്ച് കഴിക്കുന്നു; അന്ന് പാചകത്തിന് അടുപ്പ് കത്തിക്കുന്നില്ല."),
        "gudi-padwa": ("ഗുഡി പാഡ്വ (മഹാരാഷ്ട്ര), ഉഗാദി (കർണാടക, ആന്ധ്രാപ്രദേശ്, തെലങ്കാന) എന്നിവ ചൈത്ര ശുക്ല "
                       "പ്രഥമയിലെ ചാന്ദ്ര പുതുവർഷമാണ്. വാതിൽക്കൽ 'ഗുഡി' - തുണിയും കലശവും അണിയിച്ച അലങ്കൃത "
                       "കമ്പ് - ഉയർത്തുന്നു; മധുരവും കയ്പും ചേർന്ന ഒരു വർഷത്തിന്റെ പ്രതീകമായി വേപ്പും "
                       "ശർക്കരയും കഴിക്കുന്നു. (കേരളത്തിന്റെ വിഷു മേടം ഒന്നിന്, വേറെയാണ്.)"),
        "gangaur": ("ചൈത്ര ശുക്ല തൃതീയയിലെ ഗണഗൗർ ഗൗരിയുടെയും (പാർവതി) ശിവന്റെയും രാജസ്ഥാനി ഉത്സവമാണ്. "
                    "ദാമ്പത്യ സൗഭാഗ്യത്തിനായി സ്ത്രീകൾ ഗൗരിയെ ആരാധിക്കുന്നു - വിവാഹിതർ ഭർത്താവിനായി, "
                    "പെൺകുട്ടികൾ നല്ല വരനായി; ഹോളിയുടെ പിറ്റേന്ന് തുടങ്ങുന്ന പതിനെട്ട് ദിവസത്തെ പൂജ ഇതോടെ "
                    "അവസാനിക്കുന്നു."),
        "vat-savitri": ("ഉത്തരേന്ത്യയിൽ (പൂർണിമാന്ത) ജ്യേഷ്ഠ അമാവാസിയിലെ വട സാവിത്രി വ്രതം, യമനിൽ നിന്ന് "
                        "ഭർത്താവ് സത്യവാന്റെ ജീവൻ തിരികെ നേടിയ സാവിത്രിയെ സ്മരിക്കുന്നു. വിവാഹിതരായ സ്ത്രീകൾ "
                        "വ്രതമെടുത്ത്, പേരാലിനെ (വടവൃക്ഷം) പൂജിച്ച്, അതിനെ വലംവച്ച് നൂൽ ചുറ്റിക്കെട്ടി, "
                        "സാവിത്രി കഥ കേൾക്കുന്നു."),
        "vat-purnima": ("വട പൂർണിമ അതേ വട സാവിത്രി വ്രതം തന്നെയാണ് - മഹാരാഷ്ട്ര, ഗുജറാത്ത്, ദക്ഷിണേന്ത്യ "
                        "എന്നിവിടങ്ങളിൽ (അമാന്ത കലണ്ടർ) ജ്യേഷ്ഠ പൗർണമിയിൽ, ഉത്തരേന്ത്യൻ തീയതിക്ക് പതിനഞ്ചു "
                        "ദിവസം കഴിഞ്ഞ് ആചരിക്കുന്നു. വിവാഹിതരായ സ്ത്രീകൾ ഭർത്താവിന്റെ ദീർഘായുസ്സിനായി "
                        "വ്രതമെടുത്ത് പേരാലിനെ പൂജിക്കുന്നു."),
        "ganga-dussehra": ("ജ്യേഷ്ഠ ശുക്ല ദശമിയിലെ ഗംഗാ ദസറ ഭഗീരഥന്റെ തപസ്സിലൂടെ ഗംഗ ഭൂമിയിലേക്ക് ഇറങ്ങിയതിന്റെ "
                           "ആഘോഷമാണ്. ഭക്തർ ഗംഗയിൽ സ്നാനം ചെയ്ത്, ദീപങ്ങൾ അർപ്പിച്ച്, ദാനം ചെയ്യുന്നു; ഈ സ്നാനം "
                           "പത്തുതരം പാപങ്ങൾ കഴുകിക്കളയുമെന്നാണ് വിശ്വാസം."),
        "hariyali-teej": ("ശ്രാവണ ശുക്ല തൃതീയയിലെ ഹരിയാലി തീജ് മഴക്കാലത്ത് ശിവപാർവതിമാരുടെ പുനഃസമാഗമം "
                          "ആഘോഷിക്കുന്നു. സ്ത്രീകൾ പച്ച വസ്ത്രം ധരിച്ച്, മൈലാഞ്ചി അണിഞ്ഞ്, അലങ്കരിച്ച "
                          "ഊഞ്ഞാലുകളിൽ ആടി, ശ്രാവണ ഗാനങ്ങൾ പാടുന്നു; പലരും ഭർത്താവിനായി വ്രതമെടുക്കുന്നു."),
        "nag-panchami": ("ശ്രാവണ ശുക്ല പഞ്ചമിയിലെ നാഗപഞ്ചമി നാഗദേവതകളെ ആരാധിക്കുന്ന ദിവസമാണ്. സർപ്പരൂപങ്ങൾ "
                         "വരച്ചോ പ്രതിഷ്ഠിച്ചോ പാൽ, പൂക്കൾ, മധുരം എന്നിവ അർപ്പിച്ച് കുടുംബത്തിന്റെ "
                         "സംരക്ഷണത്തിനായി പ്രാർഥിക്കുന്നു. (ഗുജറാത്തിൽ നാഗ് പാഞ്ചം പിന്നീട്, ഭാദ്രപദത്തിലാണ്.)"),
        "kajari-teej": ("കജരി (കജ്‌ലി, ബഡി) തീജ്, ഭാദ്രപദ കൃഷ്ണ തൃതീയ (പൂർണിമാന്ത), ഉത്തർപ്രദേശ്, ബിഹാർ, "
                        "രാജസ്ഥാൻ, മധ്യപ്രദേശ് എന്നിവിടങ്ങളിലെ വിവാഹിതരായ സ്ത്രീകൾ ആചരിക്കുന്നു. അവർ "
                        "വ്രതമെടുത്ത്, വേപ്പുമരത്തെ (നീമഡി മാതാ) പൂജിച്ച്, ചന്ദ്രന് അർഘ്യം അർപ്പിച്ച ശേഷം "
                        "വ്രതം മുറിക്കുന്നു; കജരി നാടൻപാട്ടുകൾ പാടുന്നു."),
        "hal-shashthi": ("ഹല ഷഷ്ഠി (ലലഹി ഛഠ്, ഹർ ഛഠ്), ഭാദ്രപദ കൃഷ്ണ ഷഷ്ഠി (പൂർണിമാന്ത), കലപ്പ (ഹലം) "
                         "ആയുധമായുള്ള ബലരാമന്റെ ജന്മദിനമാണ്. അമ്മമാർ കുട്ടികൾക്കായി വ്രതമെടുക്കുകയും കലപ്പ "
                         "കൊണ്ട് ഉഴുത് വിളയിച്ചതൊന്നും കഴിക്കാതിരിക്കുകയും ചെയ്യുന്നു - പലപ്പോഴും പസഹി അരിയും "
                         "എരുമപ്പാലും കഴിക്കുന്നു."),
        "hartalika-teej": ("ഭാദ്രപദ ശുക്ല തൃതീയയിലെ ഹർതാലിക തീജ് ശിവനെ നേടാൻ പാർവതി ചെയ്ത തപസ്സിനെ ആദരിക്കുന്നു. "
                           "സ്ത്രീകൾ നിർജല വ്രതമെടുത്ത്, ശിവപാർവതിമാരുടെ കളിമൺ രൂപങ്ങൾ ഉണ്ടാക്കി പൂജിക്കുന്നു "
                           "(രാവിലെ പ്രാതഃകാല പൂജയാണ് ഉത്തമം), രാത്രി ഉറക്കമൊഴിഞ്ഞ്, പിറ്റേന്ന് രാവിലെ വ്രതം "
                           "മുറിക്കുന്നു."),
        "rishi-panchami": ("ഭാദ്രപദ ശുക്ല പഞ്ചമിയിലെ ഋഷി പഞ്ചമി സപ്തർഷികളെ ആദരിക്കുന്നു. പ്രത്യേകിച്ച് സ്ത്രീകൾ "
                           "സ്നാനം ചെയ്ത്, വ്രതമെടുത്ത്, ഉച്ചയ്ക്ക് (മധ്യാഹ്നം) ഋഷിമാരെ പൂജിക്കുന്നു - അറിയാതെ "
                           "ചെയ്ത തെറ്റുകളിൽ നിന്നുള്ള ശുദ്ധിക്കായി."),
        "anant-chaturdashi": ("ഭാദ്രപദ ശുക്ല ചതുർദശിയിലെ അനന്ത ചതുർദശി മഹാവിഷ്ണുവിനെ അനന്തനായി ആരാധിക്കുന്ന "
                              "ദിവസമാണ്. പൂജയ്ക്കു ശേഷം പതിനാല് കെട്ടുകളുള്ള പുണ്യനൂൽ (അനന്ത സൂത്രം) കൈയിൽ "
                              "കെട്ടുന്നു; ഗണേശ വിഗ്രഹങ്ങൾ നിമജ്ജനം ചെയ്യുന്ന (ഗണേശ വിസർജനം) ദിവസവും ഇതാണ്."),
        "pitru-paksha": ("പിതൃക്കളുടെ പക്ഷമായ പിതൃപക്ഷം ആശ്വിന (പൂർണിമാന്ത) കൃഷ്ണപക്ഷ പ്രഥമ മുതൽ അമാവാസി "
                         "വരെയാണ്. ഒരു പിതൃവിന്റെ മരണതിഥിയിൽ കുടുംബങ്ങൾ തർപ്പണവും ശ്രാദ്ധവും - പിണ്ഡം, "
                         "ബ്രാഹ്മണർക്കും പശു, കാക്ക, നായ എന്നിവയ്ക്കും ഭക്ഷണം - കുതപ, രൗഹിണ അല്ലെങ്കിൽ അപരാഹ്ന "
                         "സമയത്ത് നടത്തുന്നു."),
        "sarva-pitru-amavasya": ("സർവ പിതൃ അമാവാസി (മഹാലയ അമാവാസി) പിതൃപക്ഷം അവസാനിപ്പിക്കുന്നു. ഈ ദിവസത്തെ ശ്രാദ്ധം "
                                 "തിഥി അറിയാത്തവർ ഉൾപ്പെടെ എല്ലാ പിതൃക്കളിലും എത്തുന്നു; ഇത് കുതപ, രൗഹിണ അല്ലെങ്കിൽ "
                                 "അപരാഹ്ന സമയത്ത് ചെയ്യുന്നു."),
        "narak-chaturdashi": ("നരക ചതുർദശി (രൂപ് ചൗദസ്), കാർത്തിക കൃഷ്ണ ചതുർദശി (പൂർണിമാന്ത), ശ്രീകൃഷ്ണൻ നരകാസുരനെ "
                              "ജയിച്ചതിന്റെ ഓർമയാണ്. സൂര്യോദയത്തിനു മുമ്പ്, ചന്ദ്രൻ ആകാശത്തുള്ളപ്പോൾ, ആളുകൾ "
                              "ഔഷധക്കൂട്ട് (ഉബ്ടൻ) തേച്ച് എണ്ണതേച്ചുകുളിക്കുന്നു (അഭ്യംഗ സ്നാനം); വൈകുന്നേരം യമനായി "
                              "ഒരു ദീപം കൊളുത്തുന്നു."),
        "tulsi-vivah": ("കാർത്തിക ശുക്ല ദ്വാദശിയിലെ തുളസി വിവാഹം, തുളസിച്ചെടിയെ (വൃന്ദയായി) സാളഗ്രാമ "
                        "രൂപത്തിലുള്ള മഹാവിഷ്ണുവുമായി ആചാരപൂർവം വിവാഹം കഴിപ്പിക്കുന്ന ചടങ്ങാണ്. കുടുംബങ്ങൾ "
                        "തുളസിയെ വധുവിനെപ്പോലെ അലങ്കരിച്ച് വിവാഹച്ചടങ്ങുകൾ നടത്തുന്നു; അതിനു ശേഷം ഹിന്ദു "
                        "വിവാഹകാലം ആരംഭിക്കുന്നു."),
        "kartik-purnima": ("കാർത്തിക പൗർണമി പുണ്യമാസമായ കാർത്തികം അവസാനിപ്പിക്കുന്നു. ഗംഗയിലോ പുണ്യനദിയിലോ "
                           "സ്നാനം ചെയ്യാനും ദാനം ചെയ്യാനും ഉത്തമ ദിവസം; ഗുരുനാനാക്ക് ജയന്തിയും ശിവൻ "
                           "ത്രിപുരാസുരനെ നശിപ്പിച്ച ത്രിപുരി പൂർണിമയും ഇതുതന്നെ. (കേരളത്തിലെ തൃക്കാർത്തിക "
                           "സൗരമാസമായ വൃശ്ചികത്തിലെ കാർത്തിക നാളിലായതിനാൽ തീയതി വ്യത്യാസപ്പെടാം.)"),
        "dev-deepawali": ("'ദേവന്മാരുടെ ദീപാവലി' ആയ ദേവ ദീപാവലി കാർത്തിക പൗർണമി സന്ധ്യയ്ക്ക്, പ്രത്യേകിച്ച് "
                          "ലക്ഷക്കണക്കിന് ചെരാതുകൾ കൊണ്ട് പ്രകാശിക്കുന്ന വാരാണസിയിലെ ഘാട്ടുകളിൽ ആഘോഷിക്കുന്നു. "
                          "ശിവൻ ത്രിപുരാസുരനെ ജയിച്ചതിന്റെ ഓർമയാണിത്; പ്രദോഷ കാലത്ത് ഗംഗയ്ക്ക് ദീപങ്ങൾ "
                          "അർപ്പിക്കുന്നു."),
    },
}

# Short notes where traditions differ, shown on the festival page: slug (or
# observance key) -> text.
NOTES: dict[str, dict[str, str]] = {
    "en": {
        "holika-dahan": ('Dates follow Drik Panchang. When Bhadra covers the whole Purnima night and Purnima '
             "lasts most of the next day, Drik moves Holika Dahan to the next evening's Pradosh "
             '(as in 2026, 3 March); some almanacs instead give a time late on the first night, '
             'after Bhadra ends.'),
        "janmashtami": ("Dates follow Drik Panchang's Smarta (default) reckoning, with Rohini nakshatra at "
             'midnight preferred. Vaishnava/ISKCON communities sometimes keep Janmashtami a day '
             'later.'),
        "devuthani-ekadashi": ('This is the Smarta (householder) date. Where Ekadashi spans two days, Vaishnavas '
             'may fast on the second day.'),
        "dussehra": ('Dates follow Drik Panchang (Dashami in Aparahna, Shravana nakshatra preferred). In '
             'Bengal and some almanacs Vijayadashami can fall a day later.'),
        "jivitputrika": ('Dates follow Drik Panchang (Ashtami at midday; when it is at sunrise only briefly, '
             'as in 2023, the previous day). Nahay-khay is the day before and parana the next '
             'morning; regional panchangs (e.g. Mithila) can differ by a day.'),
        "vat-savitri": ('Two traditions: North India keeps Vat Savitri on Jyeshtha Amavasya (this date); '
             'Maharashtra, Gujarat and the south keep it as Vat Purnima fifteen days later.'),
        "vat-purnima": ('Two traditions: this is the Purnima (amanta) date of Maharashtra, Gujarat and the '
             'south; North India keeps Vat Savitri on the Amavasya fifteen days earlier.'),
        "ganga-dussehra": ('When Jyeshtha is doubled (an adhika month, as in 2026), Drik Panchang keeps Ganga '
             'Dussehra in the adhika Jyeshtha; some almanacs give the nija Jyeshtha date a month '
             'later.'),
        "pitru-paksha": ('Drik Panchang counts Pitru Paksha from the Pratipada shraddha; Purnima shraddha is '
             'on the day before, and many calendars start the fortnight there.'),
        "dev-deepawali": ('Drik Panchang publishes Dev Deepawali for Varanasi; the date here uses the same '
             "rule (Purnima in Pradosh), and the Pradosh kaal shown is New Delhi's."),
        "kartik-purnima": ('This is the snan-daan day (Purnima at sunrise). When Purnima begins the previous '
             'afternoon, the Purnima fast and Dev Deepawali can fall a day earlier.'),
    },
    "hi": {
        "holika-dahan": ('तिथि द्रिक पंचांग के अनुसार है। जब पूर्णिमा की पूरी रात भद्रा हो और पूर्णिमा अगले '
             'दिन अधिकांश समय रहे, तो द्रिक पंचांग होलिका दहन अगली संध्या के प्रदोष में बताता है '
             '(जैसे 2026 में 3 मार्च); कुछ पंचांग पहली रात भद्रा समाप्ति के बाद का समय देते हैं।'),
        "janmashtami": ('तिथि द्रिक पंचांग की स्मार्त (सामान्य) गणना से है, जिसमें मध्यरात्रि में रोहिणी '
             'नक्षत्र को प्राथमिकता दी गई है। वैष्णव/इस्कॉन परंपरा कभी-कभी अगले दिन जन्माष्टमी '
             'मनाती है।'),
        "devuthani-ekadashi": 'यह स्मार्त (गृहस्थ) तिथि है। जब एकादशी दो दिन हो, वैष्णव दूसरे दिन व्रत रख सकते हैं।',
        "dussehra": ('तिथि द्रिक पंचांग के अनुसार है (अपराह्न में दशमी, श्रवण नक्षत्र को प्राथमिकता)। '
             'बंगाल और कुछ पंचांगों में विजयादशमी एक दिन बाद हो सकती है।'),
        "jivitputrika": ('तिथि द्रिक पंचांग के अनुसार है (मध्याह्न में अष्टमी; सूर्योदय पर थोड़ी देर ही हो, '
             'जैसे 2023 में, तो पिछला दिन)। नहाय-खाय एक दिन पहले और पारण अगली सुबह होता है; '
             'क्षेत्रीय पंचांगों (जैसे मिथिला) में कभी-कभी एक दिन का अंतर होता है।'),
        "vat-savitri": ('दो परंपराएं: उत्तर भारत में वट सावित्री ज्येष्ठ अमावस्या (यह तिथि) को; महाराष्ट्र, '
             'गुजरात और दक्षिण भारत में पंद्रह दिन बाद वट पूर्णिमा के रूप में।'),
        "vat-purnima": ('दो परंपराएं: यह महाराष्ट्र, गुजरात और दक्षिण भारत की पूर्णिमा (अमांत) तिथि है; '
             'उत्तर भारत में वट सावित्री पंद्रह दिन पहले अमावस्या को होता है।'),
        "ganga-dussehra": ('जब ज्येष्ठ दो हों (अधिक मास, जैसे 2026 में), द्रिक पंचांग गंगा दशहरा अधिक ज्येष्ठ '
             'में बताता है; कुछ पंचांग एक माह बाद निज ज्येष्ठ की तिथि देते हैं।'),
        "pitru-paksha": ('द्रिक पंचांग पितृ पक्ष प्रतिपदा श्राद्ध से गिनता है; पूर्णिमा श्राद्ध एक दिन पहले '
             'होता है और कई कैलेंडर पखवाड़ा वहीं से शुरू करते हैं।'),
        "dev-deepawali": ('द्रिक पंचांग देव दीपावली वाराणसी के लिए देता है; यहां तिथि उसी नियम (प्रदोष में '
             'पूर्णिमा) से है और दिया गया प्रदोष काल नई दिल्ली का है।'),
        "kartik-purnima": ('यह स्नान-दान का दिन है (सूर्योदय पर पूर्णिमा)। जब पूर्णिमा पिछले दिन दोपहर बाद शुरू '
             'हो, तो पूर्णिमा व्रत और देव दीपावली एक दिन पहले हो सकते हैं।'),
    },
    "kn": {
        "holika-dahan": ('ದಿನಾಂಕಗಳು ದೃಕ್ ಪಂಚಾಂಗವನ್ನು ಅನುಸರಿಸುತ್ತವೆ. ಹುಣ್ಣಿಮೆಯ ಇಡೀ ರಾತ್ರಿ ಭದ್ರಾ ಇದ್ದು, '
             'ಹುಣ್ಣಿಮೆ ಮರುದಿನದ ಹೆಚ್ಚಿನ ಭಾಗ ಇದ್ದರೆ, ದೃಕ್ ಪಂಚಾಂಗ ಹೋಳಿಕಾ ದಹನವನ್ನು ಮರುದಿನ ಸಂಜೆಯ '
             'ಪ್ರದೋಷಕ್ಕೆ ಸರಿಸುತ್ತದೆ (2026ರಲ್ಲಿ ಮಾರ್ಚ್ 3ರಂದು ಆದಂತೆ); ಕೆಲವು ಪಂಚಾಂಗಗಳು ಬದಲಿಗೆ '
             'ಮೊದಲ ರಾತ್ರಿಯೇ ತಡವಾಗಿ, ಭದ್ರಾ ಮುಗಿದ ನಂತರದ ಸಮಯವನ್ನು ನೀಡುತ್ತವೆ.'),
        "janmashtami": ('ದಿನಾಂಕಗಳು ದೃಕ್ ಪಂಚಾಂಗದ ಸ್ಮಾರ್ತ (ಸಾಮಾನ್ಯ) ಗಣನೆಯನ್ನು ಅನುಸರಿಸುತ್ತವೆ; '
             'ಮಧ್ಯರಾತ್ರಿಯಲ್ಲಿ ರೋಹಿಣಿ ನಕ್ಷತ್ರಕ್ಕೆ ಆದ್ಯತೆ. ವೈಷ್ಣವ/ಇಸ್ಕಾನ್ ಸಮುದಾಯಗಳು ಕೆಲವೊಮ್ಮೆ '
             'ಜನ್ಮಾಷ್ಟಮಿಯನ್ನು ಒಂದು ದಿನ ನಂತರ ಆಚರಿಸುತ್ತವೆ.'),
        "devuthani-ekadashi": ('ಇದು ಸ್ಮಾರ್ತ (ಗೃಹಸ್ಥ) ದಿನಾಂಕ. ಏಕಾದಶಿ ಎರಡು ದಿನಗಳಲ್ಲಿ ಇದ್ದಾಗ ವೈಷ್ಣವರು '
             'ಎರಡನೇ ದಿನ ಉಪವಾಸ ಮಾಡಬಹುದು.'),
        "dussehra": ('ದಿನಾಂಕಗಳು ದೃಕ್ ಪಂಚಾಂಗವನ್ನು ಅನುಸರಿಸುತ್ತವೆ (ಅಪರಾಹ್ನದಲ್ಲಿ ದಶಮಿ, ಶ್ರವಣ '
             'ನಕ್ಷತ್ರಕ್ಕೆ ಆದ್ಯತೆ). ಬಂಗಾಳ ಮತ್ತು ಕೆಲವು ಪಂಚಾಂಗಗಳಲ್ಲಿ ವಿಜಯದಶಮಿ ಒಂದು ದಿನ ನಂತರ '
             'ಬರಬಹುದು.'),
        "jivitputrika": ('ದಿನಾಂಕಗಳು ದೃಕ್ ಪಂಚಾಂಗವನ್ನು ಅನುಸರಿಸುತ್ತವೆ (ಮಧ್ಯಾಹ್ನದಲ್ಲಿ ಅಷ್ಟಮಿ; '
             'ಸೂರ್ಯೋದಯದಲ್ಲಿ ಅದು ಸ್ವಲ್ಪ ಹೊತ್ತು ಮಾತ್ರ ಇದ್ದರೆ, 2023ರಂತೆ, ಹಿಂದಿನ ದಿನ). ನಹಾಯ್-ಖಾಯ್ '
             'ಹಿಂದಿನ ದಿನ ಮತ್ತು ಪಾರಣೆ ಮರುದಿನ ಬೆಳಿಗ್ಗೆ; ಪ್ರಾದೇಶಿಕ ಪಂಚಾಂಗಗಳಲ್ಲಿ (ಉದಾ. ಮಿಥಿಲಾ) '
             'ಒಂದು ದಿನದ ವ್ಯತ್ಯಾಸ ಇರಬಹುದು.'),
        "vat-savitri": ('ಎರಡು ಸಂಪ್ರದಾಯಗಳು: ಉತ್ತರ ಭಾರತದಲ್ಲಿ ವಟ ಸಾವಿತ್ರಿಯನ್ನು ಜ್ಯೇಷ್ಠ ಅಮಾವಾಸ್ಯೆಯಂದು '
             '(ಈ ದಿನಾಂಕ) ಆಚರಿಸಲಾಗುತ್ತದೆ; ಮಹಾರಾಷ್ಟ್ರ, ಗುಜರಾತ್ ಮತ್ತು ದಕ್ಷಿಣ ಭಾರತದಲ್ಲಿ ಹದಿನೈದು '
             'ದಿನ ನಂತರ ವಟ ಪೂರ್ಣಿಮೆಯಾಗಿ.'),
        "vat-purnima": ('ಎರಡು ಸಂಪ್ರದಾಯಗಳು: ಇದು ಮಹಾರಾಷ್ಟ್ರ, ಗುಜರಾತ್ ಮತ್ತು ದಕ್ಷಿಣ ಭಾರತದ ಹುಣ್ಣಿಮೆ '
             '(ಅಮಾಂತ) ದಿನಾಂಕ; ಉತ್ತರ ಭಾರತದಲ್ಲಿ ವಟ ಸಾವಿತ್ರಿಯನ್ನು ಹದಿನೈದು ದಿನ ಮೊದಲು '
             'ಅಮಾವಾಸ್ಯೆಯಂದು ಆಚರಿಸಲಾಗುತ್ತದೆ.'),
        "ganga-dussehra": ('ಜ್ಯೇಷ್ಠ ಮಾಸ ಎರಡು ಬಾರಿ ಬಂದಾಗ (ಅಧಿಕ ಮಾಸ, 2026ರಂತೆ), ದೃಕ್ ಪಂಚಾಂಗ ಗಂಗಾ '
             'ದಸರಾವನ್ನು ಅಧಿಕ ಜ್ಯೇಷ್ಠದಲ್ಲಿ ನೀಡುತ್ತದೆ; ಕೆಲವು ಪಂಚಾಂಗಗಳು ಒಂದು ತಿಂಗಳ ನಂತರದ ನಿಜ '
             'ಜ್ಯೇಷ್ಠದ ದಿನಾಂಕವನ್ನು ನೀಡುತ್ತವೆ.'),
        "pitru-paksha": ('ದೃಕ್ ಪಂಚಾಂಗ ಪಿತೃ ಪಕ್ಷವನ್ನು ಪ್ರತಿಪದೆಯ ಶ್ರಾದ್ಧದಿಂದ ಎಣಿಸುತ್ತದೆ; ಹುಣ್ಣಿಮೆಯ '
             'ಶ್ರಾದ್ಧ ಹಿಂದಿನ ದಿನ ಇರುತ್ತದೆ, ಮತ್ತು ಅನೇಕ ಪಂಚಾಂಗಗಳು ಪಕ್ಷವನ್ನು ಅಲ್ಲಿಂದಲೇ '
             'ಆರಂಭಿಸುತ್ತವೆ.'),
        "dev-deepawali": ('ದೃಕ್ ಪಂಚಾಂಗ ದೇವ ದೀಪಾವಳಿಯನ್ನು ವಾರಾಣಸಿಗಾಗಿ ಪ್ರಕಟಿಸುತ್ತದೆ; ಇಲ್ಲಿನ ದಿನಾಂಕ ಅದೇ '
             'ನಿಯಮವನ್ನು (ಪ್ರದೋಷದಲ್ಲಿ ಹುಣ್ಣಿಮೆ) ಬಳಸುತ್ತದೆ, ಮತ್ತು ತೋರಿಸಿರುವ ಪ್ರದೋಷ ಕಾಲ '
             'ನವದೆಹಲಿಯದು.'),
        "kartik-purnima": ('ಇದು ಸ್ನಾನ-ದಾನದ ದಿನ (ಸೂರ್ಯೋದಯದಲ್ಲಿ ಹುಣ್ಣಿಮೆ). ಹುಣ್ಣಿಮೆ ಹಿಂದಿನ ದಿನ '
             'ಮಧ್ಯಾಹ್ನದ ನಂತರ ಆರಂಭವಾದರೆ, ಹುಣ್ಣಿಮೆ ವ್ರತ ಮತ್ತು ದೇವ ದೀಪಾವಳಿ ಒಂದು ದಿನ ಮೊದಲು '
             'ಬರಬಹುದು.'),
    },
    "te": {
        "holika-dahan": ("తేదీలు దృక్ పంచాంగం ప్రకారం. పౌర్ణమి రాత్రంతా భద్ర ఉండి, మరుసటి రోజు ఎక్కువ "
             "భాగం పౌర్ణమి కొనసాగితే, దృక్ పంచాంగం హోలికా దహనాన్ని మరుసటి సాయంత్రం ప్రదోష కాలానికి "
             "మారుస్తుంది (2026లో మార్చి 3 వలె); కొన్ని పంచాంగాలు బదులుగా మొదటి రాత్రే, భద్ర "
             "ముగిసిన తర్వాత, ఆలస్యమైన సమయాన్ని ఇస్తాయి."),
        "janmashtami": ("తేదీలు దృక్ పంచాంగం స్మార్త (సాధారణ) గణన ప్రకారం, అర్ధరాత్రి రోహిణి నక్షత్రం "
             "ఉండటానికి ప్రాధాన్యం ఇస్తూ. వైష్ణవ/ఇస్కాన్ సంప్రదాయాలు కొన్నిసార్లు జన్మాష్టమిని ఒక "
             "రోజు తర్వాత జరుపుకుంటాయి."),
        "devuthani-ekadashi": ("ఇది స్మార్త (గృహస్థ) తేదీ. ఏకాదశి రెండు రోజులు ఉన్నప్పుడు వైష్ణవులు "
             "రెండవ రోజు ఉపవాసం ఉండవచ్చు."),
        "dussehra": ("తేదీలు దృక్ పంచాంగం ప్రకారం (అపరాహ్ణంలో దశమి, శ్రవణ నక్షత్రానికి ప్రాధాన్యం). "
             "బెంగాల్‌లో, కొన్ని పంచాంగాల్లో విజయదశమి ఒక రోజు తర్వాత రావచ్చు."),
        "jivitputrika": ("తేదీలు దృక్ పంచాంగం ప్రకారం (మధ్యాహ్నం అష్టమి; సూర్యోదయం వద్ద అది కొద్దిసేపే "
             "ఉంటే, 2023లో వలె, ముందు రోజు). నహాయ్-ఖాయ్ ముందు రోజు, పారణ మరుసటి ఉదయం; ప్రాంతీయ "
             "పంచాంగాల్లో (ఉదా. మిథిల) ఒక రోజు తేడా ఉండవచ్చు."),
        "vat-savitri": ("రెండు సంప్రదాయాలు: ఉత్తర భారతదేశంలో వట సావిత్రిని జ్యేష్ఠ అమావాస్య నాడు (ఈ "
             "తేదీ) ఆచరిస్తారు; మహారాష్ట్ర, గుజరాత్, దక్షిణాదిలో పదిహేను రోజుల తర్వాత వట పౌర్ణమిగా "
             "ఆచరిస్తారు."),
        "vat-purnima": ("రెండు సంప్రదాయాలు: ఇది మహారాష్ట్ర, గుజరాత్, దక్షిణాది పౌర్ణమి (అమాంత) తేదీ; "
             "ఉత్తర భారతదేశంలో వట సావిత్రిని పదిహేను రోజుల ముందు అమావాస్య నాడు ఆచరిస్తారు."),
        "ganga-dussehra": ("జ్యేష్ఠ మాసం రెండుసార్లు వచ్చినప్పుడు (అధిక మాసం, 2026లో వలె), దృక్ పంచాంగం "
             "గంగా దశహరాను అధిక జ్యేష్ఠంలో ఇస్తుంది; కొన్ని పంచాంగాలు ఒక నెల తర్వాతి నిజ జ్యేష్ఠ "
             "తేదీని ఇస్తాయి."),
        "pitru-paksha": ("దృక్ పంచాంగం మహాలయ పక్షాన్ని పాడ్యమి శ్రాద్ధం నుండి లెక్కిస్తుంది; పౌర్ణమి "
             "శ్రాద్ధం ముందు రోజు, చాలా క్యాలెండర్లు పక్షాన్ని అక్కడి నుండే ప్రారంభిస్తాయి."),
        "dev-deepawali": ("దృక్ పంచాంగం దేవ దీపావళిని వారణాసి కోసం ప్రచురిస్తుంది; ఇక్కడి తేదీ అదే నియమం "
             "(ప్రదోష కాలంలో పౌర్ణమి) ప్రకారం, చూపిన ప్రదోష కాలం న్యూఢిల్లీది."),
        "kartik-purnima": ("ఇది స్నాన-దానాల రోజు (సూర్యోదయం వద్ద పౌర్ణమి). పౌర్ణమి ముందు రోజు మధ్యాహ్నం "
             "తర్వాత ప్రారంభమైతే, పౌర్ణమి వ్రతం, దేవ దీపావళి ఒక రోజు ముందే రావచ్చు."),
    },

    # Tamil (DIVASTRO-123)
    "ta": {
        "holika-dahan": ("தேதிகள் த்ருக் பஞ்சாங்கப்படி. பௌர்ணமி இரவு முழுவதும் பத்ரா இருந்து, மறுநாளின் "
                         "பெரும்பகுதி பௌர்ணமி நீடித்தால், த்ருக் பஞ்சாங்கம் ஹோலிகா தகனத்தை மறுநாள் மாலை "
                         "பிரதோஷத்துக்கு மாற்றுகிறது (2026 இல் மார்ச் 3 போல); சில பஞ்சாங்கங்கள் முதல் "
                         "இரவிலேயே, பத்ரா முடிந்த பின் தாமதமான நேரத்தைத் தருகின்றன."),
        "janmashtami": ("தேதிகள் த்ருக் பஞ்சாங்கத்தின் ஸ்மார்த்த (பொது) முறைப்படி; நள்ளிரவில் ரோகிணி "
                        "நட்சத்திரம் இருப்பது விரும்பப்படுகிறது. வைஷ்ணவ/இஸ்கான் சமூகங்கள் சில சமயம் ஒரு நாள் "
                        "கழித்துக் கடைப்பிடிக்கின்றன."),
        "devuthani-ekadashi": ("இது ஸ்மார்த்த (இல்லறத்தார்) தேதி. ஏகாதசி இரண்டு நாட்களில் பரவியிருந்தால், "
                               "வைஷ்ணவர்கள் இரண்டாம் நாள் விரதம் இருக்கலாம்."),
        "dussehra": ("தேதிகள் த்ருக் பஞ்சாங்கப்படி (அபராஹ்ணத்தில் தசமி; திருவோண நட்சத்திரம் "
                     "விரும்பப்படுகிறது). வங்காளத்திலும் சில பஞ்சாங்கங்களிலும் விஜயதசமி ஒரு நாள் கழித்து "
                     "வரலாம்."),
        "jivitputrika": ("தேதிகள் த்ருக் பஞ்சாங்கப்படி (நண்பகலில் அஷ்டமி; சூரிய உதயத்தில் சிறிது நேரமே "
                         "இருந்தால், 2023 போல, முந்தைய நாள்). நஹாய்-காய் முந்தைய நாள், பாரணை மறுநாள் காலை; "
                         "பிராந்தியப் பஞ்சாங்கங்கள் (எ.கா. மிதிலா) ஒரு நாள் வேறுபடலாம்."),
        "vat-savitri": ("இரண்டு மரபுகள்: வட இந்தியா வட சாவித்திரியை ஜ்யேஷ்ட அமாவாசையில் (இந்தத் தேதி) "
                        "கடைப்பிடிக்கிறது; மகாராஷ்டிரா, குஜராத், தென்னிந்தியா பதினைந்து நாள் கழித்து வட "
                        "பௌர்ணமியாகக் கடைப்பிடிக்கின்றன."),
        "vat-purnima": ("இரண்டு மரபுகள்: இது மகாராஷ்டிரா, குஜராத், தென்னிந்தியாவின் பௌர்ணமி (அமாந்த) தேதி; வட "
                        "இந்தியா பதினைந்து நாள் முன்னதாக அமாவாசையில் வட சாவித்திரியைக் கடைப்பிடிக்கிறது."),
        "ganga-dussehra": ("ஜ்யேஷ்ட மாதம் இரட்டிக்கும்போது (2026 போல அதிக மாதம்), த்ருக் பஞ்சாங்கம் கங்கா தசராவை "
                           "அதிக ஜ்யேஷ்டத்தில் வைக்கிறது; சில பஞ்சாங்கங்கள் ஒரு மாதம் கழித்து நிஜ ஜ்யேஷ்டத் "
                           "தேதியைத் தருகின்றன."),
        "pitru-paksha": ("த்ருக் பஞ்சாங்கம் பித்ரு பட்சத்தைப் பிரதமை சிராத்தத்திலிருந்து கணக்கிடுகிறது; "
                         "பௌர்ணமி சிராத்தம் அதற்கு முந்தைய நாள், பல நாட்காட்டிகள் அங்கிருந்தே பட்சத்தைத் "
                         "தொடங்குகின்றன."),
        "dev-deepawali": ("த்ருக் பஞ்சாங்கம் தேவ தீபாவளியை வாரணாசிக்காக வெளியிடுகிறது; இங்குள்ள தேதி அதே "
                          "விதியைப் (பிரதோஷத்தில் பௌர்ணமி) பின்பற்றுகிறது, காட்டப்படும் பிரதோஷ காலம் புது "
                          "தில்லிக்கானது."),
        "kartik-purnima": ("இது ஸ்நான-தான நாள் (சூரிய உதயத்தில் பௌர்ணமி). பௌர்ணமி முந்தைய நாள் பிற்பகலில் "
                           "தொடங்கினால், பௌர்ணமி விரதமும் தேவ தீபாவளியும் ஒரு நாள் முன்னதாக வரலாம்."),
    },

    # Malayalam (DIVASTRO-123)
    "ml": {
        "holika-dahan": ("തീയതികൾ ദൃക് പഞ്ചാംഗം അനുസരിച്ചാണ്. പൗർണമി രാത്രി മുഴുവൻ ഭദ്രയുണ്ടായിരിക്കുകയും "
                         "പിറ്റേന്നത്തെ ഭൂരിഭാഗവും പൗർണമി നിലനിൽക്കുകയും ചെയ്താൽ, ദൃക് പഞ്ചാംഗം ഹോളികാ ദഹനം "
                         "പിറ്റേന്നത്തെ പ്രദോഷത്തിലേക്ക് മാറ്റുന്നു (2026-ൽ മാർച്ച് 3 പോലെ); ചില പഞ്ചാംഗങ്ങൾ "
                         "ആദ്യ രാത്രി തന്നെ, ഭദ്ര കഴിഞ്ഞുള്ള വൈകിയ സമയം നൽകുന്നു."),
        "janmashtami": ("തീയതികൾ ദൃക് പഞ്ചാംഗത്തിന്റെ സ്മാർത്ത (പൊതു) രീതിയിലാണ്; അർധരാത്രിയിൽ രോഹിണി "
                        "നക്ഷത്രം ഉള്ളതിന് മുൻഗണന. വൈഷ്ണവ/ഇസ്കോൺ സമൂഹങ്ങൾ ചിലപ്പോൾ ഒരു ദിവസം കഴിഞ്ഞ് "
                        "ആചരിക്കുന്നു."),
        "devuthani-ekadashi": ("ഇത് സ്മാർത്ത (ഗൃഹസ്ഥ) തീയതിയാണ്. ഏകാദശി രണ്ടു ദിവസങ്ങളിലായി വരുമ്പോൾ വൈഷ്ണവർ രണ്ടാം "
                               "ദിവസം വ്രതമെടുത്തേക്കാം."),
        "dussehra": ("തീയതികൾ ദൃക് പഞ്ചാംഗം അനുസരിച്ച് (അപരാഹ്നത്തിൽ ദശമി; തിരുവോണം നക്ഷത്രത്തിന് മുൻഗണന). "
                     "ബംഗാളിലും ചില പഞ്ചാംഗങ്ങളിലും വിജയദശമി ഒരു ദിവസം കഴിഞ്ഞാകാം."),
        "jivitputrika": ("തീയതികൾ ദൃക് പഞ്ചാംഗം അനുസരിച്ച് (മധ്യാഹ്നത്തിൽ അഷ്ടമി; സൂര്യോദയത്തിൽ അൽപനേരം "
                         "മാത്രമാണെങ്കിൽ, 2023-ലെ പോലെ, തലേദിവസം). നഹായ്-ഖായ് തലേന്നും പാരണ പിറ്റേന്ന് "
                         "രാവിലെയും; പ്രാദേശിക പഞ്ചാംഗങ്ങളിൽ (ഉദാ. മിഥില) ഒരു ദിവസത്തെ വ്യത്യാസം വരാം."),
        "vat-savitri": ("രണ്ട് പാരമ്പര്യങ്ങൾ: ഉത്തരേന്ത്യ വട സാവിത്രി ജ്യേഷ്ഠ അമാവാസിയിൽ (ഈ തീയതി) "
                        "ആചരിക്കുന്നു; മഹാരാഷ്ട്ര, ഗുജറാത്ത്, ദക്ഷിണേന്ത്യ എന്നിവിടങ്ങളിൽ പതിനഞ്ചു ദിവസം "
                        "കഴിഞ്ഞ് വട പൂർണിമയായി ആചരിക്കുന്നു."),
        "vat-purnima": ("രണ്ട് പാരമ്പര്യങ്ങൾ: ഇത് മഹാരാഷ്ട്ര, ഗുജറാത്ത്, ദക്ഷിണേന്ത്യ എന്നിവിടങ്ങളിലെ പൗർണമി "
                        "(അമാന്ത) തീയതിയാണ്; ഉത്തരേന്ത്യ പതിനഞ്ചു ദിവസം മുമ്പ് അമാവാസിയിൽ വട സാവിത്രി "
                        "ആചരിക്കുന്നു."),
        "ganga-dussehra": ("ജ്യേഷ്ഠ മാസം ഇരട്ടിക്കുമ്പോൾ (2026-ലെ പോലെ അധിക മാസം), ദൃക് പഞ്ചാംഗം ഗംഗാ ദസറ അധിക "
                           "ജ്യേഷ്ഠത്തിൽ നൽകുന്നു; ചില പഞ്ചാംഗങ്ങൾ ഒരു മാസം കഴിഞ്ഞുള്ള നിജ ജ്യേഷ്ഠ തീയതി "
                           "നൽകുന്നു."),
        "pitru-paksha": ("ദൃക് പഞ്ചാംഗം പിതൃപക്ഷം പ്രഥമ ശ്രാദ്ധം മുതൽ കണക്കാക്കുന്നു; പൗർണമി ശ്രാദ്ധം അതിന്റെ "
                         "തലേന്നാണ്, പല കലണ്ടറുകളും പക്ഷം അവിടെ നിന്ന് തുടങ്ങുന്നു."),
        "dev-deepawali": ("ദൃക് പഞ്ചാംഗം ദേവ ദീപാവലി വാരാണസിക്കായാണ് പ്രസിദ്ധീകരിക്കുന്നത്; ഇവിടത്തെ തീയതി അതേ "
                          "നിയമം (പ്രദോഷത്തിൽ പൗർണമി) പിന്തുടരുന്നു, കാണിക്കുന്ന പ്രദോഷ കാലം ന്യൂഡൽഹിയിലേതാണ്."),
        "kartik-purnima": ("ഇത് സ്നാന-ദാന ദിവസമാണ് (സൂര്യോദയത്തിൽ പൗർണമി). പൗർണമി തലേന്ന് ഉച്ചതിരിഞ്ഞ് "
                           "തുടങ്ങുകയാണെങ്കിൽ പൗർണമി വ്രതവും ദേവ ദീപാവലിയും ഒരു ദിവസം മുമ്പാകാം."),
    },
}


# DIVASTRO-123: "How the date is fixed" for languages the festival engine does
# not write (it writes rule_en / rule_hi). vrat_pages._rule builds the line from
# the engine's month, paksha and tithi (names_<code>) and the rule below; the
# fixed sentences are keyed by their English text.
RULE: dict[str, dict[str, str]] = {
    "kn": {
        "amanta": "(ಅಮಾಂತ)",
        "udaya": "ಸೂರ್ಯೋದಯದ ಸಮಯದಲ್ಲಿರುವ ತಿಥಿ",
        "pratah": "ಪ್ರಾತಃಕಾಲದಲ್ಲಿ (ಹಗಲಿನ ಮೊದಲ ಐದನೇ ಒಂದು ಭಾಗ) ವ್ಯಾಪಿಸಿರುವ ತಿಥಿ",
        "purvahna": "ಪೂರ್ವಾಹ್ಣದಲ್ಲಿ (ಮಧ್ಯಾಹ್ನದ ಮುಂಚಿನ ಭಾಗ) ವ್ಯಾಪಿಸಿರುವ ತಿಥಿ",
        "madhyahna": "ಮಧ್ಯಾಹ್ನ ಕಾಲದಲ್ಲಿ (ಹಗಲಿನ ಮಧ್ಯದ ಐದನೇ ಒಂದು ಭಾಗ) ವ್ಯಾಪಿಸಿರುವ ತಿಥಿ",
        "aparahna": "ಅಪರಾಹ್ಣದಲ್ಲಿ (ಹಗಲಿನ ನಾಲ್ಕನೇ ಐದನೇ ಒಂದು ಭಾಗ) ವ್ಯಾಪಿಸಿರುವ ತಿಥಿ",
        "dina": "ಸೂರ್ಯೋದಯ ಮತ್ತು ಸೂರ್ಯಾಸ್ತದ ನಡುವೆ ತಿಥಿ ಇರುವ ಮೊದಲ ದಿನ",
        "sayahna": "ಸೂರ್ಯಾಸ್ತದ ಸಮಯದಲ್ಲಿರುವ ತಿಥಿ",
        "pradosh": "ಪ್ರದೋಷ ಕಾಲದಲ್ಲಿ (ಸೂರ್ಯಾಸ್ತದ ನಂತರ) ವ್ಯಾಪಿಸಿರುವ ತಿಥಿ",
        "nishita": "ನಿಶೀಥ ಕಾಲದಲ್ಲಿ (ಮಧ್ಯರಾತ್ರಿ) ವ್ಯಾಪಿಸಿರುವ ತಿಥಿ",
        "moonrise": "ಚಂದ್ರೋದಯದ ಸಮಯದಲ್ಲಿರುವ ತಿಥಿ",
        "ekadashi": ("ಸ್ಮಾರ್ತ: ಸೂರ್ಯೋದಯದ ಸಮಯದಲ್ಲಿರುವ ಏಕಾದಶಿ (ಎರಡು ಸೂರ್ಯೋದಯಗಳಲ್ಲಿ ಇದ್ದರೆ ಎರಡನೇ ದಿನ); "
                     "ಪಾರಣೆ ಮರುದಿನ ಸೂರ್ಯೋದಯ ಮತ್ತು ಹರಿ ವಾಸರದ ನಂತರ, ಪ್ರಾತಃಕಾಲದೊಳಗೆ ಹಾಗೂ ದ್ವಾದಶಿ "
                     "ಮುಗಿಯುವ ಮೊದಲು"),
        "the Sun's entry into sidereal Makara (Capricorn); punya kaal follows it until sunset":
            "ಸೂರ್ಯನ ಮಕರ ರಾಶಿ (ನಿರಯಣ) ಪ್ರವೇಶ; ಪುಣ್ಯ ಕಾಲ ಸಂಕ್ರಾಂತಿಯಿಂದ ಸೂರ್ಯಾಸ್ತದವರೆಗೆ",
        "the day before Makar Sankranti": "ಮಕರ ಸಂಕ್ರಾಂತಿಯ ಹಿಂದಿನ ದಿನ",
        "the day after Holika Dahan": "ಹೋಳಿಕಾ ದಹನದ ಮರುದಿನ",
    },
    "te": {
        "amanta": "(అమాంత)",
        "udaya": "సూర్యోదయ సమయంలో ఉన్న తిథి",
        "pratah": "ప్రాతఃకాలంలో (పగటి మొదటి ఐదో భాగం) వ్యాపించిన తిథి",
        "purvahna": "పూర్వాహ్ణంలో (మధ్యాహ్నానికి ముందు భాగం) వ్యాపించిన తిథి",
        "madhyahna": "మధ్యాహ్న కాలంలో (పగటి మధ్య ఐదో భాగం) వ్యాపించిన తిథి",
        "aparahna": "అపరాహ్ణంలో (పగటి నాలుగో ఐదో భాగం) వ్యాపించిన తిథి",
        "dina": "సూర్యోదయం, సూర్యాస్తమయం మధ్య తిథి ఉన్న మొదటి రోజు",
        "sayahna": "సూర్యాస్తమయ సమయంలో ఉన్న తిథి",
        "pradosh": "ప్రదోష కాలంలో (సూర్యాస్తమయం తర్వాత) వ్యాపించిన తిథి",
        "nishita": "నిశీథ కాలంలో (అర్ధరాత్రి) వ్యాపించిన తిథి",
        "moonrise": "చంద్రోదయ సమయంలో ఉన్న తిథి",
        "ekadashi": ("స్మార్త: సూర్యోదయ సమయంలో ఉన్న ఏకాదశి (రెండు సూర్యోదయాల్లో ఉంటే రెండో రోజు); "
                     "పారణ మరుసటి రోజు సూర్యోదయం, హరి వాసరం తర్వాత, ప్రాతఃకాలంలోనే, ద్వాదశి "
                     "ముగియక ముందు"),
        "the Sun's entry into sidereal Makara (Capricorn); punya kaal follows it until sunset":
            "సూర్యుడు మకర రాశిలో (నిరయణ) ప్రవేశించడం; పుణ్య కాలం సంక్రాంతి నుంచి సూర్యాస్తమయం వరకు",
        "the day before Makar Sankranti": "మకర సంక్రాంతికి ముందు రోజు",
        "the day after Holika Dahan": "హోలికా దహనం తర్వాతి రోజు",
    },
}

# How each date is fixed ("Ashwin (amanta) Shukla Dashami: tithi prevailing at
# Aparahna ..."), for the languages astro/festivals.py does not write itself
# (it has rule_en / rule_hi). vrat_pages._rule composes it: "head" (only when
# the English rule names the month) + "tithi" + "rule.<festivals rule>", with
# month, paksha and tithi from names_<code>; "key.<observance key>" replaces the
# whole sentence for the observances that are not a tithi rule.
# Placeholders: head {month}; tithi {paksha} {tithi}.
RULES: dict[str, dict[str, str]] = {
    # Tamil (DIVASTRO-123)
    "ta": {
        "head": "{month} மாதம் (அமாந்த) ",
        "tithi": "{paksha} {tithi}: ",
        "rule.udaya": "சூரிய உதயத்தின்போது நிலவும் திதி",
        "rule.pratah": "பிராதக் காலத்தில் (பகலின் முதல் ஐந்தில் ஒரு பங்கு) நிலவும் திதி",
        "rule.purvahna": "முற்பகலில் (பூர்வாஹ்ணம்) நிலவும் திதி",
        "rule.madhyahna": "மத்தியான காலத்தில் (பகலின் நடு ஐந்தில் ஒரு பங்கு) நிலவும் திதி",
        "rule.aparahna": "அபராஹ்ண காலத்தில் (பகலின் நான்காம் ஐந்தில் ஒரு பங்கு) நிலவும் திதி",
        "rule.dina": "சூரிய உதயம் முதல் அஸ்தமனம் வரையிலான நேரத்தில் திதி இருக்கும் முதல் நாள்",
        "rule.sayahna": "சூரிய அஸ்தமனத்தின்போது நிலவும் திதி",
        "rule.pradosh": "பிரதோஷ காலத்தில் (சூரிய அஸ்தமனத்துக்குப் பின்) நிலவும் திதி",
        "rule.nishita": "நிசீத காலத்தில் (நள்ளிரவு) நிலவும் திதி",
        "rule.moonrise": "சந்திர உதயத்தின்போது நிலவும் திதி",
        "key.ekadashi": ("ஸ்மார்த்த முறை: சூரிய உதயத்தின்போது நிலவும் ஏகாதசி (இரண்டு சூரிய உதயங்களில் "
                         "இருந்தால் இரண்டாம் நாள்); பாரணை மறுநாள் சூரிய உதயத்துக்கும் ஹரி வாசரத்துக்கும் "
                         "பின், பிராதக் காலத்துக்குள், துவாதசி முடியும் முன்"),
        "key.makar_sankranti": ("சூரியன் நிராயன மகர ராசியில் பிரவேசிக்கும் நேரம்; அதிலிருந்து சூரிய "
                                "அஸ்தமனம் வரை புண்ணிய காலம்"),
        "key.lohri": "மகர சங்கராந்திக்கு முந்தைய நாள்",
        "key.holi": "ஹோலிகா தகனத்துக்கு அடுத்த நாள்",
    },
    # Malayalam (DIVASTRO-123)
    "ml": {
        "head": "{month} മാസം (അമാന്ത) ",
        "tithi": "{paksha}പക്ഷ {tithi}: ",
        "rule.udaya": "സൂര്യോദയസമയത്തുള്ള തിഥി",
        "rule.pratah": "പ്രാതഃകാലത്ത് (പകലിന്റെ ആദ്യ അഞ്ചിലൊന്ന്) നിലനിൽക്കുന്ന തിഥി",
        "rule.purvahna": "പൂർവാഹ്നത്തിൽ (മുൻപകൽ) നിലനിൽക്കുന്ന തിഥി",
        "rule.madhyahna": "മധ്യാഹ്നത്തിൽ (പകലിന്റെ നടുവിലെ അഞ്ചിലൊന്ന്) നിലനിൽക്കുന്ന തിഥി",
        "rule.aparahna": "അപരാഹ്നത്തിൽ (പകലിന്റെ നാലാമത്തെ അഞ്ചിലൊന്ന്) നിലനിൽക്കുന്ന തിഥി",
        "rule.dina": "സൂര്യോദയത്തിനും അസ്തമയത്തിനുമിടയിൽ തിഥിയുള്ള ആദ്യ ദിവസം",
        "rule.sayahna": "സൂര്യാസ്തമയസമയത്തുള്ള തിഥി",
        "rule.pradosh": "പ്രദോഷകാലത്ത് (അസ്തമയശേഷം) നിലനിൽക്കുന്ന തിഥി",
        "rule.nishita": "നിശീഥകാലത്ത് (അർധരാത്രി) നിലനിൽക്കുന്ന തിഥി",
        "rule.moonrise": "ചന്ദ്രോദയസമയത്തുള്ള തിഥി",
        "key.ekadashi": ("സ്മാർത്ത രീതി: സൂര്യോദയസമയത്തുള്ള ഏകാദശി (രണ്ട് സൂര്യോദയങ്ങളിലുണ്ടെങ്കിൽ രണ്ടാം "
                         "ദിവസം); പാരണ പിറ്റേന്ന് സൂര്യോദയത്തിനും ഹരിവാസരത്തിനും ശേഷം, പ്രാതഃകാലത്തിനുള്ളിൽ, "
                         "ദ്വാദശി തീരുംമുമ്പ്"),
        "key.makar_sankranti": ("സൂര്യൻ നിരയന മകരം രാശിയിൽ പ്രവേശിക്കുന്ന സമയം; അതുമുതൽ "
                                "സൂര്യാസ്തമയം വരെ പുണ്യകാലം"),
        "key.lohri": "മകരസംക്രാന്തിയുടെ തലേന്ന്",
        "key.holi": "ഹോളികാദഹനത്തിന്റെ പിറ്റേന്ന്",
    },
}
