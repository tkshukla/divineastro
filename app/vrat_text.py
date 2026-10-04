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
rules ("rule_en"/"rule_hi") come from app/astro/festivals.py; other languages
build theirs from RULE below (vrat_pages._rule), English where it has none.
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

    "bn": {
        "crumb": "ব্রত ও পার্বণ",
        "day_label": "{date}, {weekday}",
        "timing": "{label}: {prefix}{value}",
        "tithi.text": "{paksha} {name}: {start} থেকে {end}",
        "tithi.paksha": "{paksha} পক্ষ",
        "table.th": "<tr><th>তারিখ</th><th>ব্রত / পার্বণ</th><th>সময় ({city})</th></tr>",
        "city_note": ('<div class="box"><p><strong>সময় শহর অনুযায়ী বদলায়।</strong> এখানে দেওয়া '
                      "প্রতিটি সময় {city}-এর সূর্যোদয়, সূর্যাস্ত ও চন্দ্রোদয় অনুযায়ী; অন্য শহরে তা কয়েক "
                      "মিনিট এগিয়ে-পিছিয়ে যায়, কখনও কখনও তারিখও বদলায়। তারিখগুলি দৃক পঞ্চাঙ্গের স্মার্ত "
                      "(সাধারণ) গণনা মেনে দেওয়া। নিজের শহরের পঞ্জিকা দেখে নিন।</p></div>"),
        "top_note": ('<p class="note"><small>বেশিরভাগ ব্রত-পার্বণের তারিখ সারা ভারতে একই, কিন্তু '
                     "পূজার মুহূর্ত, পারণ ও চন্দ্রোদয়ের সময় শহর ভেদে আলাদা - এখানে প্রতিটি সময় "
                     "<strong>{city}</strong>-এর। আঞ্চলিক প্রথা আলাদা হতে পারে।</small></p>"),
        "cities.heading": "আপনার শহরের ব্রত ও পার্বণ",
        "tools.panchang": "{city}-এর আজকের পঞ্জিকা",
        "tools.rahu": "{city}-এ রাহুকাল",
        "tools.heading": "{city}-এর জন্য আরও",
        "cta": "আপনার শহরের পঞ্জিকা দেখুন — বিনামূল্যে",
        "more.today": "আজকের ব্রত ও পার্বণ",
        "more.year": "ব্রত-পার্বণের তালিকা {year}",
        "more.ekadashi": "একাদশী {year}",
        "more.panchang": "আজকের পঞ্জিকা",
        "more.rashifal": "আজকের রাশিফল",
        "more.heading": "আরও দেখুন",
        "majors.heading": "{year}-এর প্রধান উৎসব",
        "today.rule": "নিয়ম",
        "today.none": "আজ কোনো প্রধান ব্রত বা উৎসব নেই।",
        "today.next": " পরবর্তী: <strong>{name}</strong>, {day}।",
        "block.heading": "আজকের ব্রত ও পার্বণ",
        "nf.h1": "পাতাটি পাওয়া যায়নি",

        "hub.title_default": "আজকের ব্রত ও পার্বণ ({date}) - পূজার শুভ মুহূর্ত সহ",
        "hub.title_city": "{city}-এ আজকের ব্রত ও পার্বণ ({date}) - শুভ মুহূর্ত",
        "hub.h1_default": "আজকের ব্রত ও পার্বণ",
        "hub.h1_city": "{city}-এ আজকের ব্রত ও পার্বণ",
        "hub.desc_today": "আজ {date}: {names}। ",
        "hub.desc_none": "{date}: আজ কোনো প্রধান ব্রত নেই। ",
        "hub.desc_rest": ("আগামী 30 দিনের ব্রত ও উৎসব, একাদশীর পারণ, প্রদোষ ও সংকষ্টী চতুর্থীর "
                          "চন্দ্রোদয়ের সময় - {city}।"),
        "hub.sub": '<p class="hi">আজ কোন ব্রত, কোন পার্বণ</p>',
        "hub.upcoming": "আগামী 30 দিন",

        "year.title": "ব্রত ও পার্বণ {year}: উৎসবের তালিকা, তারিখ ও শুভ মুহূর্ত",
        "year.h1": "ব্রত ও উৎসবের ক্যালেন্ডার {year}",
        "year.desc": ("{year}-এর সব হিন্দু ব্রত ও উৎসব, মাস অনুযায়ী - একাদশী, প্রদোষ, সংকষ্টী, "
                      "পূর্ণিমা, অমাবস্যা, শিবরাত্রি এবং দীপাবলি, নবরাত্রি, রাখি বন্ধনের মতো উৎসব, "
                      "নয়াদিল্লির পূজার মুহূর্ত সহ।"),
        "year.intro": ("<p>{year}-এ নয়াদিল্লির জন্য <strong>{count}</strong>টি ব্রত ও উৎসব, পঞ্জিকা "
                       "থেকে গণনা করা। কোনো প্রধান উৎসবে ট্যাপ করে তার পূজার মুহূর্ত ও বিবরণ দেখুন।</p>"),
        "year.month": "{month} {year}",
        "year.itemlist": "{year}-এর প্রধান হিন্দু উৎসব",

        "ek.title": "একাদশী {year} তালিকা: সব একাদশী ব্রতের তারিখ ও পারণের সময়",
        "ek.h1": "একাদশী {year}: তারিখ ও পারণের সময়",
        "ek.desc": ("{year}-এর সব {count}টি একাদশী - উপবাসের তারিখ, একাদশী তিথির শুরু ও শেষ "
                    "এবং পরদিন পারণের (উপবাস ভাঙার) সময়, নয়াদিল্লির জন্য।"),
        "ek.th": "<tr><th>একাদশী</th><th>উপবাস</th><th>পারণ</th></tr>",
        "ek.rule": ("<p><strong>নিয়ম (স্মার্ত):</strong> যেদিন সূর্যোদয়ে একাদশী থাকে সেদিন উপবাস; "
                    "দুই সূর্যোদয়েই থাকলে দ্বিতীয় দিন, আর কোনো সূর্যোদয়েই না থাকলে যেদিন একাদশী "
                    "পড়ে সেদিন। পারণ পরদিন সূর্যোদয়ের পর, হরিবাসর (দ্বাদশীর প্রথম চতুর্থাংশ) শেষ "
                    "হলে, প্রাতঃকালের মধ্যে এবং দ্বাদশী শেষ হওয়ার আগে; হরিবাসর প্রাতঃকাল পেরিয়ে "
                    "গেলে মধ্যাহ্ন এড়িয়ে অপরাহ্ণে পারণ হয়।</p>"),
        "ek.sub": '<p class="hi">একাদশী ব্রত {year}</p>',
        "ek.crumb": "একাদশী {year}",

        "fest.title": "{name} {year}: তারিখ ও শুভ মুহূর্ত - {short}",
        "fest.h1": "{name} {year}: তারিখ ও মুহূর্ত",
        "fest.main": "{text}। ",
        "fest.desc": "{name} {year} পড়ছে {weekday}, {date}। {main}নয়াদিল্লির পূজার সময়।",
        "fest.when": "{name} {year} পড়ছে <strong>{when}</strong>।",
        "fest.sub": '<p class="hi">তিথি, শুভ মুহূর্ত ও পূজার সময় · {year}</p>',
        "fest.about_h2": "উৎসবটি কী এবং কীভাবে পালন করা হয়",
        "fest.rule_h2": "তারিখ কীভাবে ঠিক হয়",
        "fest.faq_h2": "প্রায়ই জিজ্ঞাসিত প্রশ্ন",
        "event.place": "ভারত",
        "faq.when_q": "{name} {year} কবে?",
        "faq.when_a": "{name} {year} পড়ছে {weekday}, {date}।",
        "faq.muhurat_q": "{name} {year}-এর পূজার শুভ মুহূর্ত কখন?",
        "faq.timings_q": "{name} {year}-এর সময় কী?",
        "faq.timings_a": ("নয়াদিল্লির জন্য - {timings}। শহর অনুযায়ী সময় কয়েক মিনিট বদলায়; "
                          "নিজের শহরের পঞ্জিকা দেখুন।"),
        "faq.why_q": "{name} {year} কেন {short} তারিখে পালিত হবে?",
        "faq.why_a": "তারিখের নিয়ম: {rule}। {year}-এ তা পড়ছে {when} (নয়াদিল্লি)।",
    },

    "or": {
        "crumb": "ବ୍ରତ ଓ ପର୍ବ",
        "day_label": "{date}, {weekday}",
        "timing": "{label}: {prefix}{value}",
        "tithi.text": "{paksha} {name}: {start}ରୁ {end} ପର୍ଯ୍ୟନ୍ତ",
        "tithi.paksha": "{paksha} ପକ୍ଷ",
        "table.th": "<tr><th>ତାରିଖ</th><th>ବ୍ରତ / ପର୍ବ</th><th>ସମୟ ({city})</th></tr>",
        "city_note": ('<div class="box"><p><strong>ସମୟ ସହର ଅନୁସାରେ ବଦଳେ।</strong> ଏଠାରେ ଦିଆଯାଇଥିବା '
                      "ପ୍ରତ୍ୟେକ ସମୟ {city}ର ସୂର୍ଯ୍ୟୋଦୟ, ସୂର୍ଯ୍ୟାସ୍ତ ଓ ଚନ୍ଦ୍ରୋଦୟ ଅନୁସାରେ; ଅନ୍ୟ ସହରରେ ଏହା "
                      "କିଛି ମିନିଟ ଆଗପଛ ହୁଏ ଏବଂ କେବେକେବେ ତାରିଖ ମଧ୍ୟ ବଦଳେ। ତାରିଖଗୁଡ଼ିକ ଦୃକ ପଞ୍ଚାଙ୍ଗର "
                      "ସ୍ମାର୍ତ୍ତ (ସାଧାରଣ) ଗଣନା ଅନୁଯାୟୀ। ନିଜ ସହରର ପାଞ୍ଜି ଦେଖନ୍ତୁ।</p></div>"),
        "top_note": ('<p class="note"><small>ଅଧିକାଂଶ ବ୍ରତ-ପର୍ବର ତାରିଖ ସାରା ଭାରତରେ ସମାନ, କିନ୍ତୁ '
                     "ପୂଜା ମୁହୂର୍ତ୍ତ, ପାରଣ ଓ ଚନ୍ଦ୍ରୋଦୟ ସମୟ ସହର ଅନୁସାରେ ଭିନ୍ନ - ଏଠାରେ ସବୁ ସମୟ "
                     "<strong>{city}</strong>ର। ଆଞ୍ଚଳିକ ପରମ୍ପରା ଭିନ୍ନ ହୋଇପାରେ।</small></p>"),
        "cities.heading": "ଆପଣଙ୍କ ସହରର ବ୍ରତ ଓ ପର୍ବ",
        "tools.panchang": "{city}ର ଆଜିର ପାଞ୍ଜି",
        "tools.rahu": "{city}ରେ ରାହୁ କାଳ",
        "tools.heading": "{city} ପାଇଁ ଆହୁରି",
        "cta": "ଆପଣଙ୍କ ସହରର ପାଞ୍ଜି ଦେଖନ୍ତୁ — ମାଗଣା",
        "more.today": "ଆଜିର ବ୍ରତ ଓ ପର୍ବ",
        "more.year": "ବ୍ରତ ଓ ପର୍ବ ତାଲିକା {year}",
        "more.ekadashi": "ଏକାଦଶୀ {year}",
        "more.panchang": "ଆଜିର ପାଞ୍ଜି",
        "more.rashifal": "ଆଜିର ରାଶିଫଳ",
        "more.heading": "ଆହୁରି ଦେଖନ୍ତୁ",
        "majors.heading": "{year}ର ପ୍ରମୁଖ ପର୍ବ",
        "today.rule": "ନିୟମ",
        "today.none": "ଆଜି କୌଣସି ପ୍ରମୁଖ ବ୍ରତ ବା ପର୍ବ ନାହିଁ।",
        "today.next": " ପରବର୍ତ୍ତୀ: <strong>{name}</strong>, {day}।",
        "block.heading": "ଆଜିର ବ୍ରତ ଓ ପର୍ବ",
        "nf.h1": "ପୃଷ୍ଠାଟି ମିଳିଲା ନାହିଁ",

        "hub.title_default": "ଆଜିର ବ୍ରତ ଓ ପର୍ବ ({date}) - ପୂଜା ମୁହୂର୍ତ୍ତ ସହିତ",
        "hub.title_city": "{city}ରେ ଆଜିର ବ୍ରତ ଓ ପର୍ବ ({date}) - ଶୁଭ ମୁହୂର୍ତ୍ତ",
        "hub.h1_default": "ଆଜିର ବ୍ରତ ଓ ପର୍ବ",
        "hub.h1_city": "{city}ରେ ଆଜିର ବ୍ରତ ଓ ପର୍ବ",
        "hub.desc_today": "ଆଜି {date}: {names}। ",
        "hub.desc_none": "{date}: ଆଜି କୌଣସି ପ୍ରମୁଖ ବ୍ରତ ନାହିଁ। ",
        "hub.desc_rest": ("ଆଗାମୀ 30 ଦିନର ବ୍ରତ ଓ ପର୍ବ, ଏକାଦଶୀ ପାରଣ, ପ୍ରଦୋଷ ଓ ସଙ୍କଷ୍ଟି ଚତୁର୍ଥୀର "
                          "ଚନ୍ଦ୍ରୋଦୟ ସମୟ - {city}।"),
        "hub.sub": '<p class="hi">ଆଜି କେଉଁ ବ୍ରତ, କେଉଁ ପର୍ବ</p>',
        "hub.upcoming": "ଆଗାମୀ 30 ଦିନ",

        "year.title": "ବ୍ରତ ଓ ପର୍ବ {year}: ସମ୍ପୂର୍ଣ୍ଣ ତାଲିକା, ତାରିଖ ଓ ଶୁଭ ମୁହୂର୍ତ୍ତ",
        "year.h1": "ବ୍ରତ ଓ ପର୍ବ ପାଞ୍ଜି {year}",
        "year.desc": ("{year}ର ସମସ୍ତ ହିନ୍ଦୁ ବ୍ରତ ଓ ପର୍ବ, ମାସ ଅନୁସାରେ - ଏକାଦଶୀ, ପ୍ରଦୋଷ, ସଙ୍କଷ୍ଟି, "
                      "ପୂର୍ଣ୍ଣିମା, ଅମାବାସ୍ୟା, ଶିବରାତ୍ରି ଏବଂ ଦୀପାବଳି, ନବରାତ୍ରି, ରକ୍ଷା ବନ୍ଧନ ଭଳି ପର୍ବ, "
                      "ନୂଆଦିଲ୍ଲୀର ପୂଜା ମୁହୂର୍ତ୍ତ ସହିତ।"),
        "year.intro": ("<p>{year}ରେ ନୂଆଦିଲ୍ଲୀ ପାଇଁ <strong>{count}</strong>ଟି ବ୍ରତ ଓ ପର୍ବ, ପଞ୍ଚାଙ୍ଗରୁ "
                       "ଗଣନା କରାଯାଇଛି। କୌଣସି ପ୍ରମୁଖ ପର୍ବ ଉପରେ ଟାପ କରି ତାହାର ପୂଜା ମୁହୂର୍ତ୍ତ ଓ ବିବରଣୀ "
                       "ଦେଖନ୍ତୁ।</p>"),
        "year.month": "{month} {year}",
        "year.itemlist": "{year}ର ପ୍ରମୁଖ ହିନ୍ଦୁ ପର୍ବ",

        "ek.title": "ଏକାଦଶୀ {year} ତାଲିକା: ସମସ୍ତ ଏକାଦଶୀ ବ୍ରତ ତାରିଖ ଓ ପାରଣ ସମୟ",
        "ek.h1": "ଏକାଦଶୀ {year}: ତାରିଖ ଓ ପାରଣ ସମୟ",
        "ek.desc": ("{year}ର ସମସ୍ତ {count}ଟି ଏକାଦଶୀ - ଉପବାସ ତାରିଖ, ଏକାଦଶୀ ତିଥିର ଆରମ୍ଭ ଓ ଶେଷ "
                    "ଏବଂ ପରଦିନ ପାରଣ (ଉପବାସ ଭାଙ୍ଗିବା) ସମୟ, ନୂଆଦିଲ୍ଲୀ ପାଇଁ।"),
        "ek.th": "<tr><th>ଏକାଦଶୀ</th><th>ଉପବାସ</th><th>ପାରଣ</th></tr>",
        "ek.rule": ("<p><strong>ନିୟମ (ସ୍ମାର୍ତ୍ତ):</strong> ଯେଉଁ ଦିନ ସୂର୍ଯ୍ୟୋଦୟ ସମୟରେ ଏକାଦଶୀ ଥାଏ ସେହି "
                    "ଦିନ ଉପବାସ; ଦୁଇଟି ସୂର୍ଯ୍ୟୋଦୟରେ ଥିଲେ ଦ୍ୱିତୀୟ ଦିନ, ଆଉ କୌଣସି ସୂର୍ଯ୍ୟୋଦୟରେ ନଥିଲେ "
                    "ଯେଉଁ ଦିନ ଏକାଦଶୀ ପଡ଼େ ସେହି ଦିନ। ପାରଣ ପରଦିନ ସୂର୍ଯ୍ୟୋଦୟ ପରେ, ହରିବାସର (ଦ୍ୱାଦଶୀର "
                    "ପ୍ରଥମ ଚତୁର୍ଥାଂଶ) ଶେଷ ହେବା ପରେ, ପ୍ରାତଃକାଳ ମଧ୍ୟରେ ଓ ଦ୍ୱାଦଶୀ ଶେଷ ହେବା ପୂର୍ବରୁ "
                    "କରାଯାଏ; ହରିବାସର ପ୍ରାତଃକାଳ ପରେ ମଧ୍ୟ ରହିଲେ ମଧ୍ୟାହ୍ନ ଛାଡ଼ି ଅପରାହ୍ଣରେ ପାରଣ ହୁଏ।</p>"),
        "ek.sub": '<p class="hi">ଏକାଦଶୀ ବ୍ରତ {year}</p>',
        "ek.crumb": "ଏକାଦଶୀ {year}",

        "fest.title": "{name} {year}: ତାରିଖ ଓ ଶୁଭ ମୁହୂର୍ତ୍ତ - {short}",
        "fest.h1": "{name} {year}: ତାରିଖ ଓ ମୁହୂର୍ତ୍ତ",
        "fest.main": "{text}। ",
        "fest.desc": "{name} {year} {weekday}, {date} ଦିନ ପଡ଼ୁଛି। {main}ନୂଆଦିଲ୍ଲୀର ପୂଜା ସମୟ।",
        "fest.when": "{name} {year} <strong>{when}</strong> ଦିନ ପଡ଼ୁଛି।",
        "fest.sub": '<p class="hi">ତିଥି, ଶୁଭ ମୁହୂର୍ତ୍ତ ଓ ପୂଜା ସମୟ · {year}</p>',
        "fest.about_h2": "ଏହା କ'ଣ ଓ କିପରି ପାଳନ କରାଯାଏ",
        "fest.rule_h2": "ତାରିଖ କିପରି ସ୍ଥିର ହୁଏ",
        "fest.faq_h2": "ବାରମ୍ବାର ପଚରାଯାଉଥିବା ପ୍ରଶ୍ନ",
        "event.place": "ଭାରତ",
        "faq.when_q": "{name} {year} କେବେ?",
        "faq.when_a": "{name} {year} {weekday}, {date} ଦିନ ପଡ଼ୁଛି।",
        "faq.muhurat_q": "{name} {year}ର ପୂଜା ମୁହୂର୍ତ୍ତ କେବେ?",
        "faq.timings_q": "{name} {year}ର ସମୟ କ'ଣ?",
        "faq.timings_a": ("ନୂଆଦିଲ୍ଲୀ ପାଇଁ - {timings}। ସହର ଅନୁସାରେ ସମୟ କିଛି ମିନିଟ ବଦଳେ; "
                          "ନିଜ ସହରର ପାଞ୍ଜି ଦେଖନ୍ତୁ।"),
        "faq.why_q": "{name} {year} କାହିଁକି {short} ଦିନ ପାଳନ କରାଯିବ?",
        "faq.why_a": "ତାରିଖର ନିୟମ: {rule}। {year}ରେ ଏହା {when} ଦିନ ପଡ଼ୁଛି (ନୂଆଦିଲ୍ଲୀ)।",
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
    "bn": {
        "makar-sankranti": ("মকর সংক্রান্তিতে সূর্য মকর রাশিতে প্রবেশ করে এবং উত্তরায়ণ শুরু হয়। এটি "
             "ফসলের উৎসব: মানুষ পবিত্র নদীতে স্নান করেন, তিল, গুড়, খিচুড়ি ও কম্বল দান করেন এবং "
             "ঘুড়ি ওড়ান। বাংলায় দিনটি পৌষ সংক্রান্তি - পিঠেপুলি আর গঙ্গাসাগর স্নানের দিন।"),
        "maha-shivratri": ("মহাশিবরাত্রি, শিবের মহারাত্রি, অমান্ত গণনায় মাঘ মাসের কৃষ্ণ চতুর্দশীতে "
             "পড়ে। ভক্তেরা উপবাস করেন, শিবলিঙ্গে জল, দুধ ও বেলপাতা অর্পণ করেন, ওঁ নমঃ শিবায় জপ "
             "করেন এবং রাতের চার প্রহর জেগে থাকেন; মধ্যরাতের কাছাকাছি নিশীথ কালের পূজাই সবচেয়ে "
             "গুরুত্বপূর্ণ।"),
        "holika-dahan": ("হোলিকা দহন, হোলির আগের সন্ধ্যায়, প্রহ্লাদের ভক্তি এবং অশুভের উপর শুভের "
             "জয় উদযাপন করে। সূর্যাস্তের পর, ভদ্রা এড়িয়ে, আগুন জ্বালানো হয় এবং পরিবারগুলি শস্য, "
             "নারকেল ও প্রার্থনা নিবেদন করে তা প্রদক্ষিণ করে। বাংলায় এটি ন্যাড়াপোড়া নামে পরিচিত।"),
        "holi": ("রঙের উৎসব হোলি পালিত হয় হোলিকা দহনের পরের সকালে - রং, গান, গুজিয়ার মতো মিষ্টি "
             "আর আত্মীয়-বন্ধুর বাড়ি যাওয়া নিয়ে। বাংলায় এর সঙ্গেই পালিত হয় দোলযাত্রা।"),
        "ram-navami": ("রাম নবমী চৈত্র শুক্লা নবমীর মধ্যাহ্নে শ্রীরামচন্দ্রের জন্ম উদযাপন করে। ভক্তেরা "
             "উপবাস করেন, রামচরিতমানস পাঠ করেন এবং তাঁর জন্মের সময়, মধ্যাহ্ন মুহূর্তে, পূজা করেন।"),
        "hanuman-jayanti": ("হনুমান জয়ন্তী (উত্তর ভারতে চৈত্র পূর্ণিমা) শ্রীহনুমানের জন্মদিন। ভক্তেরা "
             "হনুমান মন্দিরে যান, হনুমান চালিসা ও সুন্দরকাণ্ড পাঠ করেন এবং সিঁদুর ও লাড্ডু নিবেদন "
             "করেন।"),
        "akshaya-tritiya": ("বৈশাখ শুক্লা তৃতীয়া, অক্ষয় তৃতীয়ায় করা প্রতিটি ভালো কাজ 'অক্ষয়' - যার "
             "ক্ষয় নেই - বলে মনে করা হয়। মানুষ বিষ্ণু ও লক্ষ্মীর পূজা করেন, দান করেন এবং নতুন কাজ "
             "শুরু করেন বা সোনা কেনেন।"),
        "raksha-bandhan": ("শ্রাবণ পূর্ণিমায় রাখি বন্ধন ভাই-বোনের বন্ধনের উৎসব। বোনেরা ভাইয়ের হাতে "
             "রাখি বেঁধে তার মঙ্গল কামনা করেন; রাখি বাঁধা হয় ভদ্রামুক্ত সময়ে। বাংলায় এই পূর্ণিমা "
             "ঝুলন পূর্ণিমা নামেও পরিচিত।"),
        "janmashtami": ("শ্রীকৃষ্ণ জন্মাষ্টমী ভাদ্রপদ (পূর্ণিমান্ত) কৃষ্ণা অষ্টমীর মধ্যরাতে শ্রীকৃষ্ণের "
             "জন্ম উদযাপন করে। ভক্তেরা সারাদিন উপবাস করেন এবং নিশীথ (মধ্যরাত) পূজার পর উপবাস "
             "ভাঙেন, যখন শিশু কৃষ্ণকে স্নান করিয়ে দোলনায় শোয়ানো হয়।"),
        "ganesh-chaturthi": ("ভাদ্রপদ শুক্লা চতুর্থী, গণেশ চতুর্থীতে শ্রীগণেশকে ঘরে আবাহন করা হয়। তাঁর "
             "জন্মের সময় মধ্যাহ্ন মুহূর্তে মূর্তি স্থাপন করে মোদক, দূর্বা ও লাল ফুলে পূজা করা হয়; "
             "এদিন চাঁদ দেখা এড়িয়ে চলা হয়।"),
        "chaitra-navratri": ("চৈত্র নবরাত্রি, বসন্তে দেবী দুর্গার নয় রাত্রি, শুরু হয় চৈত্র শুক্লা "
             "প্রতিপদে - যা হিন্দু নববর্ষও (বিক্রম সংবৎ)। ঘটস্থাপন (কলস স্থাপন) দিয়ে নয় দিনের পূজা "
             "শুরু হয়। বাংলায় এই সময়ে বাসন্তী পূজা হয়।"),
        "navratri": ("শারদীয় নবরাত্রি, শরতে দেবী দুর্গার নয় রাত্রি, আশ্বিন শুক্লা প্রতিপদের সকালে "
             "ঘটস্থাপন - কলস স্থাপন ও যব বোনা - দিয়ে শুরু হয়। প্রতিদিন দেবীর নয় রূপের একটির পূজা "
             "হয়। বাংলায় এই সময়েই দুর্গাপূজা - ষষ্ঠী থেকে বিজয়া দশমী।"),
        "dussehra": ("দশেরা (বিজয়া দশমী) রাবণের উপর শ্রীরামের এবং মহিষাসুরের উপর দেবী দুর্গার জয়ের "
             "দিন। অপরাহ্ণে শমী পূজা, অপরাজিতা পূজা ও রাবণ দহন হয়; বিজয় মুহূর্ত নতুন কাজ শুরুর "
             "জন্য শুভ বলে ধরা হয়। বাংলায় এদিন প্রতিমা বিসর্জন আর বিজয়ার শুভেচ্ছা বিনিময় হয়।"),
        "karwa-chauth": ("করবা চৌথে বিবাহিত মহিলারা স্বামীর দীর্ঘায়ু কামনায় সূর্যোদয় থেকে চন্দ্রোদয় "
             "পর্যন্ত উপবাস করেন। সন্ধ্যায় করবা মাতার পূজার পর চাঁদকে জল (অর্ঘ্য) দিয়ে উপবাস ভাঙা "
             "হয়।"),
        "ahoi-ashtami": ("অহোই অষ্টমীতে, দীপাবলির আট দিন আগে, মায়েরা সন্তানের মঙ্গল কামনায় উপবাস করেন "
             "এবং সন্ধ্যায় অহোই মাতার পূজা করেন; প্রথা অনুযায়ী তারা দেখে (কোনো কোনো পরিবারে চাঁদ "
             "দেখে) উপবাস ভাঙা হয়।"),
        "dhanteras": ("ধনতেরাস, দীপাবলির প্রথম দিন, ধন্বন্তরি ও দেবী লক্ষ্মীকে উৎসর্গিত। মানুষ নতুন "
             "বাসন, সোনা বা রুপো কেনেন এবং সন্ধ্যায় যমের প্রদীপ জ্বালান; পূজা হয় প্রদোষ কালে, সম্ভব "
             "হলে স্থির বৃষ লগ্নে।"),
        "diwali": ("কার্তিক অমাবস্যায় দীপাবলি আলোর উৎসব। সন্ধ্যায় প্রদোষ কালে, সম্ভব হলে স্থির বৃষ "
             "লগ্নে - যাতে সমৃদ্ধি স্থির থাকে - লক্ষ্মী ও গণেশের পূজা হয় এবং ঘর প্রদীপে আলোকিত হয়। "
             "বাংলায় এই অমাবস্যার রাতে কালীপূজা হয়।"),
        "govardhan-puja": ("গোবর্ধন পূজা (অন্নকূট), দীপাবলির পরের দিন, শ্রীকৃষ্ণের গোবর্ধন পর্বত তুলে "
             "ধরার স্মরণ। গোবর বা খাবার দিয়ে গোবর্ধন গড়ে পূজা করা হয় এবং নানা পদের অন্নকূট "
             "নিবেদন করা হয়, সাধারণত সকালে (প্রাতঃকাল)।"),
        "bhai-dooj": ("ভাইফোঁটা (ভাই দুজ), কার্তিক শুক্লা দ্বিতীয়া, ভাই-বোনের উৎসব: বোনেরা ভাইয়ের "
             "কপালে ফোঁটা দেন, আরতি করেন এবং তার দীর্ঘায়ু কামনা করেন; উত্তম সময় অপরাহ্ণ। দিনটি "
             "যম দ্বিতীয়া নামেও পরিচিত।"),
        "chhath-puja": ("ছট পূজায় চার দিন ধরে সূর্যদেব ও ছঠী মাইয়ার আরাধনা হয়। প্রধান দিনে (কার্তিক "
             "শুক্লা ষষ্ঠী) ব্রতীরা জলে দাঁড়িয়ে অস্তগামী সূর্যকে এবং পরদিন সকালে উদীয়মান সূর্যকে "
             "অর্ঘ্য দিয়ে নির্জলা উপবাস শেষ করেন।"),
        "vasant-panchami": ("মাঘ শুক্লা পঞ্চমী, বসন্ত পঞ্চমী বসন্তকে স্বাগত জানায় এবং দেবী সরস্বতীর "
             "আরাধনার দিন। ছাত্রছাত্রী ও শিল্পীরা বই ও বাদ্যযন্ত্রের পূজা করেন, অনেকে হলুদ পোশাক "
             "পরেন এবং শিশুদের প্রায়ই হাতেখড়ি (বিদ্যারম্ভ) হয়। বাংলায় এটিই সরস্বতী পূজা।"),
        "guru-purnima": ("গুরু পূর্ণিমা, আষাঢ় পূর্ণিমা, গুরুজনদের এবং এই দিনে জন্মানো মহর্ষি "
             "বেদব্যাসকে শ্রদ্ধা জানানোর দিন। শিষ্যেরা গুরুকে কৃতজ্ঞতা, ফুল ও উপহার নিবেদন করেন।"),
        "sharad-purnima": ("শরৎ পূর্ণিমা, আশ্বিন পূর্ণিমা, সেই রাত যখন চাঁদ সবচেয়ে উজ্জ্বল ও অমৃতময় "
             "বলে মনে করা হয়। জ্যোৎস্নায় সারারাত ক্ষীর (পায়েস) রেখে প্রসাদ হিসেবে খাওয়া হয়; "
             "লক্ষ্মীর পূজা হয়। বাংলায় এটি কোজাগরী লক্ষ্মীপূজা।"),
        "devuthani-ekadashi": ("উত্থান (প্রবোধিনী) একাদশী, কার্তিক শুক্লা একাদশীতে, ভগবান বিষ্ণু চার "
             "মাসের যোগনিদ্রা থেকে জাগেন বলে বিশ্বাস; এতে চাতুর্মাস্য শেষ হয়। তুলসী বিবাহ শুরু হয় "
             "এবং বিয়ের মরসুম খোলে। ভক্তেরা উপবাস করেন এবং পরদিন পারণ করেন।"),
        "jivitputrika": ("জীবিতপুত্রিকা (জিতিয়া, জিউতিয়া) ব্রত বিহার, ঝাড়খণ্ড, পূর্ব উত্তরপ্রদেশ ও "
             "নেপালের মায়েরা সন্তানের দীর্ঘায়ু ও মঙ্গল কামনায় আশ্বিন কৃষ্ণা অষ্টমীতে (পূর্ণিমান্ত) "
             "পালন করেন। আগের দিন নহায়-খায় দিয়ে শুরু; উপবাসটি নির্জলা, সারা দিন-রাত জল ছাড়াই, "
             "সঙ্গে জীমূতবাহনের পূজা ও জিতিয়া কথা। পারণ, অর্থাৎ উপবাস ভাঙা, পরদিন সকালে।"),
        "lohri": ("লোহরি, মকর সংক্রান্তির আগের সন্ধ্যা, পাঞ্জাব ও উত্তর ভারতের শীতের ফসলের উৎসব। "
             "সন্ধ্যায় আগুন জ্বালিয়ে তাতে তিল, গুড়, রেউড়ি, চিনাবাদাম ও খই নিবেদন করা হয়, গান ও "
             "নাচ হয়; নতুন বউ বা নবজাতকের জন্য এটি বিশেষ ধুমধামে পালিত হয়।"),
        "sakat-chauth": ("সকট চৌথ (তিলকুট চৌথ), মাঘের (পূর্ণিমান্ত) সংকষ্টী চতুর্থী, মায়েরা সন্তানের "
             "জন্য পালন করেন। তিল ও গুড় দিয়ে গণেশ ও সকট মাতার পূজা হয় এবং উদীয়মান চাঁদকে অর্ঘ্য "
             "দিয়ে উপবাস ভাঙা হয়।"),
        "mauni-amavasya": ("মৌনী অমাবস্যা, মাঘের (পূর্ণিমান্ত) অমাবস্যা, প্রয়াগরাজের মাঘ মেলার প্রধান "
             "স্নানের দিন। ভক্তেরা গঙ্গা বা কোনো পবিত্র নদীতে স্নান করেন, মৌন (নীরবতা) পালন করেন "
             "এবং দান করেন।"),
        "sheetala-ashtami": ("শীতলা অষ্টমী (বসোড়া), চৈত্র কৃষ্ণা অষ্টমী (পূর্ণিমান্ত), জ্বর ও বসন্ত "
             "রোগ থেকে রক্ষাকর্ত্রী দেবী শীতলা মাতার পূজার দিন। খাবার আগের দিন রান্না করা হয় এবং "
             "সেই বাসি খাবার নিবেদন করে খাওয়া হয়; সেদিন রান্নার জন্য উনুন জ্বালানো হয় না।"),
        "gudi-padwa": ("গুড়ি পড়ওয়া (মহারাষ্ট্র) ও উগাদি (কর্নাটক, অন্ধ্রপ্রদেশ, তেলেঙ্গানা) চৈত্র "
             "শুক্লা প্রতিপদে চান্দ্র নববর্ষ। দরজায় গুড়ি - কাপড় ও কলস দিয়ে সাজানো একটি দণ্ড - তোলা "
             "হয় এবং মিষ্টি-তেতো দুই-ই মেশানো বছরের প্রতীক হিসেবে গুড়ের সঙ্গে নিম খাওয়া হয়।"),
        "gangaur": ("গণগৌর, চৈত্র শুক্লা তৃতীয়া, রাজস্থানের গৌরী (পার্বতী) ও শিবের উৎসব। মহিলারা "
             "দাম্পত্য সুখের জন্য গৌরীর পূজা করেন - বিবাহিতারা স্বামীর জন্য, মেয়েরা ভালো বরের জন্য; "
             "হোলির পরের দিন থেকে শুরু হওয়া আঠারো দিনের পূজা এদিন শেষ হয়।"),
        "vat-savitri": ("বট সাবিত্রী ব্রত, উত্তর ভারতে জ্যৈষ্ঠ অমাবস্যায় (পূর্ণিমান্ত), সেই সাবিত্রীকে "
             "স্মরণ করে, যিনি যমের কাছ থেকে স্বামী সত্যবানের প্রাণ ফিরিয়ে এনেছিলেন। বিবাহিত মহিলারা "
             "উপবাস করেন, বটগাছের পূজা করেন, প্রদক্ষিণ করতে করতে কাঁচা সুতো জড়ান এবং সাবিত্রী কথা "
             "শোনেন।"),
        "vat-purnima": ("বট পূর্ণিমা সেই একই বট সাবিত্রী ব্রত, যা মহারাষ্ট্র, গুজরাট ও দক্ষিণ ভারতে "
             "(অমান্ত পঞ্জিকা) জ্যৈষ্ঠ পূর্ণিমায় পালিত হয় - উত্তর ভারতের তারিখের পনেরো দিন পরে। "
             "বিবাহিত মহিলারা স্বামীর দীর্ঘায়ু কামনায় উপবাস করে বটগাছের পূজা করেন।"),
        "ganga-dussehra": ("গঙ্গা দশহরা, জ্যৈষ্ঠ শুক্লা দশমী, ভগীরথের তপস্যায় গঙ্গার মর্ত্যে অবতরণের "
             "উৎসব। ভক্তেরা গঙ্গায় স্নান করেন, প্রদীপ নিবেদন করেন ও দান করেন; এই স্নান দশ রকমের "
             "পাপ ধুয়ে দেয় বলে বিশ্বাস।"),
        "hariyali-teej": ("হরিয়ালি তীজ, শ্রাবণ শুক্লা তৃতীয়া, বর্ষায় শিব ও পার্বতীর পুনর্মিলনের উৎসব। "
             "মহিলারা সবুজ পোশাক পরেন, মেহেন্দি পরেন, সাজানো দোলনায় দোলেন, শ্রাবণের গান গান এবং "
             "অনেকে স্বামীর জন্য উপবাস করেন।"),
        "nag-panchami": ("নাগ পঞ্চমী, শ্রাবণ শুক্লা পঞ্চমী, নাগদেবতাদের পূজার দিন। সাপের ছবি এঁকে বা "
             "মূর্তি স্থাপন করে দুধ, ফুল ও মিষ্টি নিবেদন করা হয় এবং পরিবারের সুরক্ষার জন্য প্রার্থনা "
             "করা হয়। (গুজরাটে নাগ পঞ্চম পরে, ভাদ্রপদে পড়ে।)"),
        "kajari-teej": ("কাজরী (কাজলি, বড়ি) তীজ, ভাদ্রপদ কৃষ্ণা তৃতীয়া (পূর্ণিমান্ত), উত্তরপ্রদেশ, "
             "বিহার, রাজস্থান ও মধ্যপ্রদেশের বিবাহিত মহিলারা পালন করেন। তাঁরা উপবাস করেন, নিমগাছের "
             "(নিমড়ি মাতা) পূজা করেন এবং চাঁদকে অর্ঘ্য দিয়ে উপবাস ভাঙেন; কাজরী লোকগান গাওয়া হয়।"),
        "hal-shashthi": ("হল ষষ্ঠী (ললহী ছঠ, হরছঠ), ভাদ্রপদ কৃষ্ণা ষষ্ঠী (পূর্ণিমান্ত), শ্রীবলরামের "
             "জন্মদিন, যাঁর অস্ত্র লাঙল (হল)। মায়েরা সন্তানের জন্য উপবাস করেন এবং লাঙল দিয়ে চষা "
             "জমির কোনো ফসল খান না - প্রায়ই পসহী চাল ও মোষের দুধ খাওয়া হয়।"),
        "hartalika-teej": ("হরতালিকা তীজ, ভাদ্রপদ শুক্লা তৃতীয়া, শিবকে পাওয়ার জন্য পার্বতীর তপস্যার "
             "স্মরণ। মহিলারা নির্জলা উপবাস করেন, মাটি দিয়ে শিব-পার্বতীর মূর্তি গড়ে পূজা করেন "
             "(প্রাতঃকালের পূজা শ্রেয়), রাতে জাগরণ করেন এবং পরদিন সকালে উপবাস ভাঙেন।"),
        "rishi-panchami": ("ঋষি পঞ্চমী, ভাদ্রপদ শুক্লা পঞ্চমী, সপ্তর্ষি - সাত মহর্ষিকে - শ্রদ্ধা "
             "জানানোর দিন। বিশেষত মহিলারা স্নান ও উপবাস করে মধ্যাহ্নে ঋষিদের পূজা করেন, অজান্তে "
             "হওয়া ত্রুটি থেকে শুদ্ধির জন্য।"),
        "anant-chaturdashi": ("অনন্ত চতুর্দশী, ভাদ্রপদ শুক্লা চতুর্দশী, অনন্ত রূপে ভগবান বিষ্ণুর "
             "পূজার দিন। পূজার পর চোদ্দোটি গিঁটের পবিত্র সুতো (অনন্ত সূত্র) বাহুতে বাঁধা হয়; এই "
             "দিনেই গণেশ প্রতিমার বিসর্জন (গণেশ বিসর্জন) হয়।"),
        "pitru-paksha": ("পিতৃপক্ষ, পূর্বপুরুষদের পক্ষ, আশ্বিনের (পূর্ণিমান্ত) কৃষ্ণপক্ষের প্রতিপদ "
             "থেকে অমাবস্যা পর্যন্ত চলে। পূর্বপুরুষের প্রয়াণ তিথিতে পরিবারগুলি কুতুপ, রৌহিণ বা "
             "অপরাহ্ণ কালে তর্পণ ও শ্রাদ্ধ করে - পিণ্ডদান, ব্রাহ্মণ ভোজন এবং গরু, কাক ও কুকুরকে "
             "খাবার দেওয়া।"),
        "sarva-pitru-amavasya": ("সর্বপিতৃ অমাবস্যা (মহালয়া অমাবস্যা) পিতৃপক্ষের শেষ দিন। এই দিনের "
             "শ্রাদ্ধ সব পূর্বপুরুষের কাছে পৌঁছায়, যাঁদের তিথি জানা নেই তাঁদের কাছেও; এটি কুতুপ, "
             "রৌহিণ বা অপরাহ্ণ কালে করা হয়। বাংলায় মহালয়ার ভোরে গঙ্গায় তর্পণ হয়, তার পরেই "
             "দেবীপক্ষ শুরু।"),
        "narak-chaturdashi": ("নরক চতুর্দশী (রূপ চৌদস), কার্তিক কৃষ্ণা চতুর্দশী (পূর্ণিমান্ত), "
             "নরকাসুরের উপর শ্রীকৃষ্ণের জয়ের স্মরণ। সূর্যোদয়ের আগে, চাঁদ আকাশে থাকতেই, উবটন মেখে "
             "তেলে স্নান (অভ্যঙ্গ স্নান) করা হয় এবং সন্ধ্যায় যমের উদ্দেশে প্রদীপ জ্বালানো হয়। "
             "বাংলায় এটি ভূত চতুর্দশী - চোদ্দো শাক খাওয়া ও চোদ্দো প্রদীপ জ্বালানোর দিন।"),
        "tulsi-vivah": ("তুলসী বিবাহ, কার্তিক শুক্লা দ্বাদশীতে, তুলসী গাছের (বৃন্দা রূপে) সঙ্গে "
             "শালগ্রাম রূপী ভগবান বিষ্ণুর আনুষ্ঠানিক বিবাহ। পরিবারগুলি তুলসীকে কনের মতো সাজিয়ে "
             "বিয়ের আচার পালন করে; এর পরে হিন্দু বিয়ের মরসুম শুরু হয়।"),
        "kartik-purnima": ("কার্তিক পূর্ণিমা পবিত্র কার্তিক মাসের সমাপ্তি। গঙ্গা বা কোনো পবিত্র নদীতে "
             "স্নান ও দানের এটি এক মহাদিন; আবার গুরু নানক জয়ন্তী এবং ত্রিপুরী পূর্ণিমাও, যেদিন শিব "
             "ত্রিপুরাসুরকে বধ করেছিলেন। বাংলায় এটি রাস পূর্ণিমা।"),
        "dev-deepawali": ("দেব দীপাবলি, 'দেবতাদের দীপাবলি', কার্তিক পূর্ণিমার সন্ধ্যায় পালিত হয়, "
             "সবচেয়ে জাঁকজমকে বারাণসীর ঘাটে, যেগুলি লক্ষ লক্ষ প্রদীপে আলোকিত হয়। এটি "
             "ত্রিপুরাসুরের উপর শিবের জয়ের দিন; প্রদোষ কালে গঙ্গাকে প্রদীপ নিবেদন করা হয়।"),
    },
    "or": {
        "makar-sankranti": ("ମକର ସଂକ୍ରାନ୍ତିରେ ସୂର୍ଯ୍ୟ ମକର ରାଶିରେ ପ୍ରବେଶ କରନ୍ତି ଏବଂ ଉତ୍ତରାୟଣ ଆରମ୍ଭ "
             "ହୁଏ। ଏହା ଫସଲର ପର୍ବ: ଲୋକେ ପବିତ୍ର ନଦୀରେ ସ୍ନାନ କରନ୍ତି, ତିଳ, ଗୁଡ଼, ଖେଚୁଡ଼ି ଓ କମ୍ବଳ ଦାନ "
             "କରନ୍ତି ଏବଂ ଗୁଡ଼ି ଉଡ଼ାନ୍ତି। ଓଡ଼ିଶାରେ ଏହି ଦିନ ମକର ଚାଉଳ ଭୋଗ ଲାଗେ।"),
        "maha-shivratri": ("ମହାଶିବରାତ୍ରି, ଶିବଙ୍କ ମହାରାତ୍ରି, ଅମାନ୍ତ ଗଣନାରେ ମାଘ ମାସର କୃଷ୍ଣ ଚତୁର୍ଦ୍ଦଶୀରେ "
             "ପଡ଼େ। ଭକ୍ତମାନେ ଉପବାସ କରନ୍ତି, ଶିବଲିଙ୍ଗରେ ଜଳ, କ୍ଷୀର ଓ ବେଲପତ୍ର ଅର୍ପଣ କରନ୍ତି, ଓଁ ନମଃ "
             "ଶିବାୟ ଜପ କରନ୍ତି ଏବଂ ରାତିର ଚାରି ପ୍ରହର ଜାଗରଣ କରନ୍ତି; ମଧ୍ୟରାତ୍ରି ନିକଟରେ ନିଶୀଥ କାଳର "
             "ପୂଜା ସବୁଠାରୁ ଗୁରୁତ୍ୱପୂର୍ଣ୍ଣ। ଓଡ଼ିଶାରେ ମନ୍ଦିରରେ ମହାଦୀପ ଉଠିବା ପରେ ଭକ୍ତମାନେ ଉପବାସ "
             "ଭାଙ୍ଗନ୍ତି।"),
        "holika-dahan": ("ହୋଲିକା ଦହନ, ହୋଲିର ପୂର୍ବ ସନ୍ଧ୍ୟାରେ, ପ୍ରହ୍ଲାଦଙ୍କ ଭକ୍ତି ଓ ଅଶୁଭ ଉପରେ ଶୁଭର "
             "ବିଜୟକୁ ପାଳନ କରେ। ସୂର୍ଯ୍ୟାସ୍ତ ପରେ, ଭଦ୍ରା ଏଡ଼ାଇ, ନିଆଁ ଜଳାଯାଏ ଏବଂ ପରିବାରମାନେ ଶସ୍ୟ, "
             "ନଡ଼ିଆ ଓ ପ୍ରାର୍ଥନା ଅର୍ପଣ କରି ତାହାକୁ ପରିକ୍ରମା କରନ୍ତି।"),
        "holi": ("ରଙ୍ଗର ପର୍ବ ହୋଲି ହୋଲିକା ଦହନର ପରଦିନ ସକାଳେ ରଙ୍ଗ, ସଙ୍ଗୀତ, ଗୁଜିଆ ଭଳି ମିଠା ଓ "
             "ପରିବାର-ବନ୍ଧୁଙ୍କ ଘରକୁ ଯିବା ସହିତ ପାଳନ କରାଯାଏ। ଓଡ଼ିଶାରେ ଏହା ସହିତ ଦୋଳ ପୂର୍ଣ୍ଣିମା ଓ "
             "ଦୋଳଯାତ୍ରା ପାଳିତ ହୁଏ।"),
        "ram-navami": ("ରାମ ନବମୀ ଚୈତ୍ର ଶୁକ୍ଳ ନବମୀର ମଧ୍ୟାହ୍ନରେ ପ୍ରଭୁ ଶ୍ରୀରାମଙ୍କ ଜନ୍ମକୁ ପାଳନ କରେ। "
             "ଭକ୍ତମାନେ ଉପବାସ କରନ୍ତି, ରାମଚରିତମାନସ ପାଠ କରନ୍ତି ଏବଂ ତାଙ୍କ ଜନ୍ମ ସମୟ, ମଧ୍ୟାହ୍ନ "
             "ମୁହୂର୍ତ୍ତରେ, ପୂଜା କରନ୍ତି।"),
        "hanuman-jayanti": ("ହନୁମାନ ଜୟନ୍ତୀ (ଉତ୍ତର ଭାରତରେ ଚୈତ୍ର ପୂର୍ଣ୍ଣିମା) ପ୍ରଭୁ ହନୁମାନଙ୍କ ଜନ୍ମୋତ୍ସବ। "
             "ଭକ୍ତମାନେ ହନୁମାନ ମନ୍ଦିରକୁ ଯାଆନ୍ତି, ହନୁମାନ ଚାଳିଶା ଓ ସୁନ୍ଦରକାଣ୍ଡ ପାଠ କରନ୍ତି ଏବଂ ସିନ୍ଦୂର "
             "ଓ ଲଡ଼ୁ ଅର୍ପଣ କରନ୍ତି। ଓଡ଼ିଶାରେ ହନୁମାନ ଜୟନ୍ତୀ ପଣା ସଂକ୍ରାନ୍ତି (ମହାବିଷୁବ ସଂକ୍ରାନ୍ତି) ଦିନ "
             "ପାଳିତ ହୁଏ।"),
        "akshaya-tritiya": ("ବୈଶାଖ ଶୁକ୍ଳ ତୃତୀୟା, ଅକ୍ଷୟ ତୃତୀୟାରେ କରାଯାଇଥିବା ପ୍ରତ୍ୟେକ ଭଲ କାମ 'ଅକ୍ଷୟ' - "
             "ଯାହାର କ୍ଷୟ ନାହିଁ - ବୋଲି ମନେ କରାଯାଏ। ଲୋକେ ବିଷ୍ଣୁ ଓ ଲକ୍ଷ୍ମୀଙ୍କ ପୂଜା କରନ୍ତି, ଦାନ କରନ୍ତି "
             "ଏବଂ ନୂଆ କାମ ଆରମ୍ଭ କରନ୍ତି ବା ସୁନା କିଣନ୍ତି। ଓଡ଼ିଶାରେ ଏହି ଦିନ ରଥଯାତ୍ରା ପାଇଁ ରଥ ନିର୍ମାଣ "
             "ଆରମ୍ଭ ହୁଏ ଓ ଚାଷୀମାନେ ଅଖି ମୁଠି ଅନୁକୂଳ କରନ୍ତି।"),
        "raksha-bandhan": ("ଶ୍ରାବଣ ପୂର୍ଣ୍ଣିମାରେ ରକ୍ଷା ବନ୍ଧନ ଭାଇ-ଭଉଣୀଙ୍କ ସ୍ନେହର ପର୍ବ। ଭଉଣୀମାନେ ଭାଇର "
             "ହାତରେ ରାକ୍ଷୀ ବାନ୍ଧି ତାର ମଙ୍ଗଳ କାମନା କରନ୍ତି; ରାକ୍ଷୀ ଭଦ୍ରା ରହିତ ସମୟରେ ବନ୍ଧାଯାଏ। "
             "ଓଡ଼ିଶାରେ ଏହି ଦିନ ଗହମା ପୂର୍ଣ୍ଣିମା, ବଳଭଦ୍ରଙ୍କ ଜନ୍ମୋତ୍ସବ।"),
        "janmashtami": ("ଶ୍ରୀକୃଷ୍ଣ ଜନ୍ମାଷ୍ଟମୀ ଭାଦ୍ରପଦ (ପୂର୍ଣ୍ଣିମାନ୍ତ) କୃଷ୍ଣ ଅଷ୍ଟମୀର ମଧ୍ୟରାତ୍ରିରେ ପ୍ରଭୁ "
             "ଶ୍ରୀକୃଷ୍ଣଙ୍କ ଜନ୍ମକୁ ପାଳନ କରେ। ଭକ୍ତମାନେ ଦିନସାରା ଉପବାସ କରନ୍ତି ଏବଂ ନିଶୀଥ (ମଧ୍ୟରାତ୍ରି) "
             "ପୂଜା ପରେ ଉପବାସ ଭାଙ୍ଗନ୍ତି, ଯେତେବେଳେ ଶିଶୁ କୃଷ୍ଣଙ୍କୁ ସ୍ନାନ କରାଇ ଦୋଳିରେ ଶୁଆଇ ଦିଆଯାଏ।"),
        "ganesh-chaturthi": ("ଭାଦ୍ରପଦ ଶୁକ୍ଳ ଚତୁର୍ଥୀ, ଗଣେଶ ଚତୁର୍ଥୀରେ ଶ୍ରୀଗଣେଶଙ୍କୁ ଘରକୁ ସ୍ୱାଗତ କରାଯାଏ। "
             "ତାଙ୍କ ଜନ୍ମ ସମୟ ମଧ୍ୟାହ୍ନ ମୁହୂର୍ତ୍ତରେ ମୂର୍ତ୍ତି ସ୍ଥାପନ କରି ମୋଦକ, ଦୂବ ଓ ନାଲି ଫୁଲରେ ପୂଜା "
             "କରାଯାଏ; ଏହି ଦିନ ଜହ୍ନ ଦେଖିବା ଏଡ଼ାଯାଏ।"),
        "chaitra-navratri": ("ଚୈତ୍ର ନବରାତ୍ରି, ବସନ୍ତରେ ମା' ଦୁର୍ଗାଙ୍କ ନଅ ରାତି, ଚୈତ୍ର ଶୁକ୍ଳ ପ୍ରତିପଦାରେ "
             "ଆରମ୍ଭ ହୁଏ - ଯାହା ହିନ୍ଦୁ ନବବର୍ଷ (ବିକ୍ରମ ସମ୍ବତ) ମଧ୍ୟ। ଘଟସ୍ଥାପନ (କଳସ ସ୍ଥାପନ) ସହିତ ନଅ "
             "ଦିନର ପୂଜା ଆରମ୍ଭ ହୁଏ।"),
        "navratri": ("ଶାରଦୀୟ ନବରାତ୍ରି, ଶରତରେ ମା' ଦୁର୍ଗାଙ୍କ ନଅ ରାତି, ଆଶ୍ୱିନ ଶୁକ୍ଳ ପ୍ରତିପଦାର ସକାଳେ "
             "ଘଟସ୍ଥାପନ - କଳସ ସ୍ଥାପନ ଓ ଯବ ବୁଣିବା - ସହିତ ଆରମ୍ଭ ହୁଏ। ପ୍ରତିଦିନ ଦେବୀଙ୍କ ନଅ ରୂପ ମଧ୍ୟରୁ "
             "ଗୋଟିଏର ପୂଜା ହୁଏ। ଓଡ଼ିଶାରେ ଏହି ସମୟରେ ଦୁର୍ଗା ପୂଜା ମହାସମାରୋହରେ ପାଳିତ ହୁଏ।"),
        "dussehra": ("ଦଶହରା (ବିଜୟା ଦଶମୀ) ରାବଣ ଉପରେ ଶ୍ରୀରାମଙ୍କ ଓ ମହିଷାସୁର ଉପରେ ମା' ଦୁର୍ଗାଙ୍କ ବିଜୟର "
             "ଦିନ। ଅପରାହ୍ଣରେ ଶମୀ ପୂଜା, ଅପରାଜିତା ପୂଜା ଓ ରାବଣ ପୋଡ଼ି ହୁଏ; ବିଜୟ ମୁହୂର୍ତ୍ତ ନୂଆ କାମ "
             "ଆରମ୍ଭ ପାଇଁ ଶୁଭ ବୋଲି ମନେ କରାଯାଏ।"),
        "karwa-chauth": ("କରୱା ଚୌଥରେ ବିବାହିତା ମହିଳାମାନେ ସ୍ୱାମୀଙ୍କ ଦୀର୍ଘାୟୁ ପାଇଁ ସୂର୍ଯ୍ୟୋଦୟରୁ "
             "ଚନ୍ଦ୍ରୋଦୟ ପର୍ଯ୍ୟନ୍ତ ଉପବାସ କରନ୍ତି। ସନ୍ଧ୍ୟାରେ କରୱା ମାତାଙ୍କ ପୂଜା ପରେ ଜହ୍ନକୁ ଜଳ (ଅର୍ଘ୍ୟ) "
             "ଦେଇ ଉପବାସ ଭାଙ୍ଗନ୍ତି।"),
        "ahoi-ashtami": ("ଅହୋଇ ଅଷ୍ଟମୀରେ, ଦୀପାବଳିର ଆଠ ଦିନ ପୂର୍ବରୁ, ମାଆମାନେ ସନ୍ତାନଙ୍କ ମଙ୍ଗଳ ପାଇଁ "
             "ଉପବାସ କରନ୍ତି ଏବଂ ସନ୍ଧ୍ୟାରେ ଅହୋଇ ମାତାଙ୍କ ପୂଜା କରନ୍ତି; ପରମ୍ପରା ଅନୁସାରେ ତାରା ଦେଖି "
             "(କିଛି ପରିବାରରେ ଜହ୍ନ ଦେଖି) ଉପବାସ ଭାଙ୍ଗନ୍ତି।"),
        "dhanteras": ("ଧନତେରସ, ଦୀପାବଳିର ପ୍ରଥମ ଦିନ, ଧନ୍ୱନ୍ତରି ଓ ମା' ଲକ୍ଷ୍ମୀଙ୍କୁ ସମର୍ପିତ। ଲୋକେ ନୂଆ "
             "ବାସନ, ସୁନା ବା ରୁପା କିଣନ୍ତି ଏବଂ ସନ୍ଧ୍ୟାରେ ଯମ ଦୀପ ଜାଳନ୍ତି; ପୂଜା ପ୍ରଦୋଷ କାଳରେ, ସମ୍ଭବ "
             "ହେଲେ ସ୍ଥିର ବୃଷ ଲଗ୍ନରେ କରାଯାଏ।"),
        "diwali": ("କାର୍ତ୍ତିକ ଅମାବାସ୍ୟାରେ ଦୀପାବଳି ଆଲୋକର ପର୍ବ। ସନ୍ଧ୍ୟାରେ ପ୍ରଦୋଷ କାଳରେ, ସମ୍ଭବ ହେଲେ ସ୍ଥିର "
             "ବୃଷ ଲଗ୍ନରେ - ଯେପରି ସମୃଦ୍ଧି ସ୍ଥିର ରହେ - ଲକ୍ଷ୍ମୀ ଓ ଗଣେଶଙ୍କ ପୂଜା ହୁଏ ଏବଂ ଘର ଦୀପରେ "
             "ଆଲୋକିତ ହୁଏ। ଓଡ଼ିଶାରେ ଏହି ସନ୍ଧ୍ୟାରେ କଉଡ଼ିଆ କାଠି ଜାଳି ପିତୃପୁରୁଷଙ୍କୁ ସ୍ମରଣ କରାଯାଏ।"),
        "govardhan-puja": ("ଗୋବର୍ଦ୍ଧନ ପୂଜା (ଅନ୍ନକୂଟ), ଦୀପାବଳିର ପରଦିନ, ଶ୍ରୀକୃଷ୍ଣଙ୍କ ଗୋବର୍ଦ୍ଧନ ପର୍ବତ "
             "ଟେକିବାକୁ ସ୍ମରଣ କରେ। ଗୋବର ବା ଖାଦ୍ୟରେ ଗୋବର୍ଦ୍ଧନ ତିଆରି କରି ପୂଜା କରାଯାଏ ଏବଂ ଅନେକ "
             "ବ୍ୟଞ୍ଜନର ଅନ୍ନକୂଟ ଭୋଗ ଲାଗେ, ସାଧାରଣତଃ ସକାଳେ (ପ୍ରାତଃକାଳ)।"),
        "bhai-dooj": ("ଭାଇ ଦୁଜ (ଯମ ଦ୍ୱିତୀୟା), କାର୍ତ୍ତିକ ଶୁକ୍ଳ ଦ୍ୱିତୀୟା, ଭାଇ-ଭଉଣୀଙ୍କ ପର୍ବ: ଭଉଣୀମାନେ "
             "ଭାଇର କପାଳରେ ଟୀକା ଲଗାନ୍ତି, ଆରତି କରନ୍ତି ଏବଂ ତାର ଦୀର୍ଘାୟୁ କାମନା କରନ୍ତି; ଉତ୍ତମ ସମୟ "
             "ଅପରାହ୍ଣ।"),
        "chhath-puja": ("ଛଠ ପୂଜାରେ ଚାରି ଦିନ ଧରି ସୂର୍ଯ୍ୟଦେବ ଓ ଛଠି ମାଈଙ୍କ ଉପାସନା ହୁଏ। ମୁଖ୍ୟ ଦିନ "
             "(କାର୍ତ୍ତିକ ଶୁକ୍ଳ ଷଷ୍ଠୀ) ବ୍ରତୀମାନେ ପାଣିରେ ଠିଆ ହୋଇ ଅସ୍ତଗାମୀ ସୂର୍ଯ୍ୟଙ୍କୁ ଓ ପରଦିନ ସକାଳେ "
             "ଉଦୀୟମାନ ସୂର୍ଯ୍ୟଙ୍କୁ ଅର୍ଘ୍ୟ ଦେଇ ନିର୍ଜଳା ଉପବାସ ସମାପ୍ତ କରନ୍ତି।"),
        "vasant-panchami": ("ମାଘ ଶୁକ୍ଳ ପଞ୍ଚମୀ, ବସନ୍ତ ପଞ୍ଚମୀ ବସନ୍ତକୁ ସ୍ୱାଗତ କରେ ଓ ମା' ସରସ୍ୱତୀଙ୍କ "
             "ଆରାଧନାର ଦିନ। ଛାତ୍ରଛାତ୍ରୀ ଓ କଳାକାରମାନେ ବହି ଓ ବାଦ୍ୟଯନ୍ତ୍ରର ପୂଜା କରନ୍ତି, ଅନେକେ ହଳଦିଆ "
             "ପୋଷାକ ପିନ୍ଧନ୍ତି ଏବଂ ପିଲାମାନଙ୍କର ପ୍ରାୟତଃ ଖଡ଼ି ଛୁଆଁ (ବିଦ୍ୟାରମ୍ଭ) ହୁଏ। ଓଡ଼ିଶାରେ ଏହା "
             "ସରସ୍ୱତୀ ପୂଜା।"),
        "guru-purnima": ("ଗୁରୁ ପୂର୍ଣ୍ଣିମା, ଆଷାଢ଼ ପୂର୍ଣ୍ଣିମା, ଗୁରୁଜନ ଓ ଏହି ଦିନ ଜନ୍ମିଥିବା ମହର୍ଷି "
             "ବେଦବ୍ୟାସଙ୍କୁ ସମ୍ମାନ ଦେବାର ଦିନ। ଶିଷ୍ୟମାନେ ଗୁରୁଙ୍କୁ କୃତଜ୍ଞତା, ଫୁଲ ଓ ଉପହାର ଅର୍ପଣ କରନ୍ତି।"),
        "sharad-purnima": ("ଶରଦ ପୂର୍ଣ୍ଣିମା, ଆଶ୍ୱିନ ପୂର୍ଣ୍ଣିମା, ସେହି ରାତି ଯେତେବେଳେ ଜହ୍ନ ସବୁଠାରୁ "
             "ଉଜ୍ଜ୍ୱଳ ଓ ଅମୃତମୟ ବୋଲି ମନେ କରାଯାଏ। ଜହ୍ନ ଆଲୁଅରେ ରାତିସାରା କ୍ଷୀରି ରଖି ପ୍ରସାଦ ଭାବେ "
             "ଖିଆଯାଏ; ଲକ୍ଷ୍ମୀ ପୂଜା (କୋଜାଗରୀ) ହୁଏ। ଓଡ଼ିଶାରେ ଏହା କୁମାର ପୂର୍ଣ୍ଣିମା - କୁମାରୀମାନେ "
             "ସକାଳେ ସୂର୍ଯ୍ୟଙ୍କୁ ଓ ସନ୍ଧ୍ୟାରେ ଜହ୍ନକୁ ପୂଜା କରନ୍ତି।"),
        "devuthani-ekadashi": ("ଦେବୋତ୍ଥାନ (ପ୍ରବୋଧିନୀ) ଏକାଦଶୀ, କାର୍ତ୍ତିକ ଶୁକ୍ଳ ଏକାଦଶୀରେ, ଭଗବାନ ବିଷ୍ଣୁ "
             "ଚାରି ମାସର ଯୋଗନିଦ୍ରାରୁ ଉଠନ୍ତି ବୋଲି ବିଶ୍ୱାସ; ଏଥିରେ ଚାତୁର୍ମାସ୍ୟ ଶେଷ ହୁଏ। ତୁଳସୀ ବିବାହ "
             "ଆରମ୍ଭ ହୁଏ ଓ ବିବାହ ଋତୁ ଖୋଲେ। ଭକ୍ତମାନେ ଉପବାସ କରି ପରଦିନ ପାରଣ କରନ୍ତି।"),
        "jivitputrika": ("ଜୀବିତପୁତ୍ରିକା (ଜିତିଆ, ଜିଉତିଆ) ବ୍ରତ ବିହାର, ଝାଡ଼ଖଣ୍ଡ, ପୂର୍ବ ଉତ୍ତରପ୍ରଦେଶ ଓ "
             "ନେପାଳର ମାଆମାନେ ସନ୍ତାନଙ୍କ ଦୀର୍ଘାୟୁ ଓ ମଙ୍ଗଳ ପାଇଁ ଆଶ୍ୱିନ କୃଷ୍ଣ ଅଷ୍ଟମୀ (ପୂର୍ଣ୍ଣିମାନ୍ତ) ଦିନ "
             "ପାଳନ କରନ୍ତି। ଆଗଦିନ ନହାୟ-ଖାୟ ସହିତ ଆରମ୍ଭ ହୁଏ; ଉପବାସଟି ନିର୍ଜଳା, ଦିନରାତି ପାଣି ବିନା, "
             "ସହିତ ଜୀମୂତବାହନଙ୍କ ପୂଜା ଓ ଜିତିଆ କଥା। ପାରଣ, ଅର୍ଥାତ୍ ଉପବାସ ଭାଙ୍ଗିବା, ପରଦିନ ସକାଳେ।"),
        "lohri": ("ଲୋହରି, ମକର ସଂକ୍ରାନ୍ତିର ପୂର୍ବ ସନ୍ଧ୍ୟା, ପଞ୍ଜାବ ଓ ଉତ୍ତର ଭାରତର ଶୀତ ଋତୁର ଫସଲ ପର୍ବ। "
             "ସନ୍ଧ୍ୟାରେ ନିଆଁ ଜାଳି ସେଥିରେ ତିଳ, ଗୁଡ଼, ରେଉଡ଼ି, ଚିନାବାଦାମ ଓ ଲିଆ ଅର୍ପଣ କରାଯାଏ, ଗୀତ ଓ "
             "ନାଚ ହୁଏ; ନୂଆ ବୋହୂ ବା ନବଜାତ ଶିଶୁ ପାଇଁ ଏହା ବିଶେଷ ଉତ୍ସାହରେ ପାଳିତ ହୁଏ।"),
        "sakat-chauth": ("ସକଟ ଚୌଥ (ତିଳକୁଟ ଚୌଥ), ମାଘ (ପୂର୍ଣ୍ଣିମାନ୍ତ)ର ସଙ୍କଷ୍ଟି ଚତୁର୍ଥୀ, ମାଆମାନେ "
             "ସନ୍ତାନଙ୍କ ପାଇଁ ପାଳନ କରନ୍ତି। ତିଳ ଓ ଗୁଡ଼ରେ ଗଣେଶ ଓ ସକଟ ମାତାଙ୍କ ପୂଜା ହୁଏ ଏବଂ ଉଦୀୟମାନ "
             "ଜହ୍ନକୁ ଅର୍ଘ୍ୟ ଦେଇ ଉପବାସ ଭାଙ୍ଗନ୍ତି।"),
        "mauni-amavasya": ("ମୌନୀ ଅମାବାସ୍ୟା, ମାଘ (ପୂର୍ଣ୍ଣିମାନ୍ତ)ର ଅମାବାସ୍ୟା, ପ୍ରୟାଗରାଜର ମାଘ ମେଳାର "
             "ପ୍ରମୁଖ ସ୍ନାନ ଦିନ। ଭକ୍ତମାନେ ଗଙ୍ଗା ବା କୌଣସି ପବିତ୍ର ନଦୀରେ ସ୍ନାନ କରନ୍ତି, ମୌନ (ନୀରବତା) "
             "ପାଳନ କରନ୍ତି ଏବଂ ଦାନ କରନ୍ତି।"),
        "sheetala-ashtami": ("ଶୀତଳା ଅଷ୍ଟମୀ (ବସୋଡ଼ା), ଚୈତ୍ର କୃଷ୍ଣ ଅଷ୍ଟମୀ (ପୂର୍ଣ୍ଣିମାନ୍ତ), ଜ୍ୱର ଓ ବସନ୍ତ "
             "ରୋଗରୁ ରକ୍ଷା କରୁଥିବା ଦେବୀ ଶୀତଳା ମାତାଙ୍କ ପୂଜାର ଦିନ। ଖାଦ୍ୟ ଆଗଦିନ ରନ୍ଧାଯାଏ ଏବଂ ସେହି "
             "ବାସି ଖାଦ୍ୟ ଭୋଗ ଲଗାଇ ଖିଆଯାଏ; ସେଦିନ ରାନ୍ଧିବା ପାଇଁ ଚୁଲି ଜଳାଯାଏ ନାହିଁ।"),
        "gudi-padwa": ("ଗୁଡ଼ି ପାଡ଼ୱା (ମହାରାଷ୍ଟ୍ର) ଓ ଉଗାଦି (କର୍ଣ୍ଣାଟକ, ଆନ୍ଧ୍ରପ୍ରଦେଶ, ତେଲେଙ୍ଗାନା) ଚୈତ୍ର "
             "ଶୁକ୍ଳ ପ୍ରତିପଦାରେ ଚାନ୍ଦ୍ର ନବବର୍ଷ। ଦ୍ୱାରରେ ଗୁଡ଼ି - ଲୁଗା ଓ କଳସରେ ସଜା ଏକ ବାଡ଼ି - ଟଙ୍ଗାଯାଏ "
             "ଏବଂ ମିଠା ଓ ପିତା ଦୁଇଟିଯାକ ଅନୁଭବର ବର୍ଷ ପାଇଁ ଗୁଡ଼ ସହିତ ନିମ୍ବ ଖିଆଯାଏ।"),
        "gangaur": ("ଗଣଗୌର, ଚୈତ୍ର ଶୁକ୍ଳ ତୃତୀୟା, ରାଜସ୍ଥାନର ଗୌରୀ (ପାର୍ବତୀ) ଓ ଶିବଙ୍କ ପର୍ବ। ମହିଳାମାନେ "
             "ଦାମ୍ପତ୍ୟ ସୁଖ ପାଇଁ ଗୌରୀଙ୍କ ପୂଜା କରନ୍ତି - ବିବାହିତାମାନେ ସ୍ୱାମୀଙ୍କ ପାଇଁ, କନ୍ୟାମାନେ ଭଲ ବର "
             "ପାଇଁ; ହୋଲିର ପରଦିନଠାରୁ ଆରମ୍ଭ ହେଉଥିବା ଅଠର ଦିନର ପୂଜା ଏହି ଦିନ ଶେଷ ହୁଏ।"),
        "vat-savitri": ("ବଟ ସାବିତ୍ରୀ ବ୍ରତ, ଉତ୍ତର ଭାରତରେ ଜ୍ୟେଷ୍ଠ ଅମାବାସ୍ୟା (ପୂର୍ଣ୍ଣିମାନ୍ତ)ରେ, ସେହି "
             "ସାବିତ୍ରୀଙ୍କୁ ସ୍ମରଣ କରେ, ଯିଏ ଯମଙ୍କଠାରୁ ସ୍ୱାମୀ ସତ୍ୟବାନଙ୍କ ପ୍ରାଣ ଫେରାଇ ଆଣିଥିଲେ। "
             "ବିବାହିତା ମହିଳାମାନେ ଉପବାସ କରନ୍ତି, ବରଗଛ (ବଟ)ର ପୂଜା କରନ୍ତି, ପରିକ୍ରମା "
             "କରୁକରୁ କଞ୍ଚା ସୂତା ଗୁଡ଼ାନ୍ତି ଏବଂ ସାବିତ୍ରୀ କଥା ଶୁଣନ୍ତି। ଓଡ଼ିଶାରେ ଏହା ସାବିତ୍ରୀ ବ୍ରତ "
             "ଭାବେ ପାଳିତ ହୁଏ।"),
        "vat-purnima": ("ବଟ ପୂର୍ଣ୍ଣିମା ସେହି ସମାନ ବଟ ସାବିତ୍ରୀ ବ୍ରତ, ଯାହା ମହାରାଷ୍ଟ୍ର, ଗୁଜରାଟ ଓ ଦକ୍ଷିଣ "
             "ଭାରତରେ (ଅମାନ୍ତ ପାଞ୍ଜି) ଜ୍ୟେଷ୍ଠ ପୂର୍ଣ୍ଣିମାରେ ପାଳିତ ହୁଏ - ଉତ୍ତର ଭାରତର ତାରିଖର ପନ୍ଦର "
             "ଦିନ ପରେ। ବିବାହିତା ମହିଳାମାନେ ସ୍ୱାମୀଙ୍କ ଦୀର୍ଘାୟୁ ପାଇଁ ଉପବାସ କରି ବରଗଛର ପୂଜା କରନ୍ତି।"),
        "ganga-dussehra": ("ଗଙ୍ଗା ଦଶହରା, ଜ୍ୟେଷ୍ଠ ଶୁକ୍ଳ ଦଶମୀ, ଭଗୀରଥଙ୍କ ତପସ୍ୟାରେ ଗଙ୍ଗାଙ୍କ ପୃଥିବୀକୁ "
             "ଅବତରଣର ପର୍ବ। ଭକ୍ତମାନେ ଗଙ୍ଗାରେ ସ୍ନାନ କରନ୍ତି, ଦୀପ ଅର୍ପଣ କରନ୍ତି ଓ ଦାନ କରନ୍ତି; ଏହି "
             "ସ୍ନାନ ଦଶ ପ୍ରକାର ପାପ ଧୋଇଦିଏ ବୋଲି ବିଶ୍ୱାସ।"),
        "hariyali-teej": ("ହରିୟାଲି ତୀଜ, ଶ୍ରାବଣ ଶୁକ୍ଳ ତୃତୀୟା, ବର୍ଷାରେ ଶିବ ଓ ପାର୍ବତୀଙ୍କ ପୁନର୍ମିଳନର "
             "ଉତ୍ସବ। ମହିଳାମାନେ ସବୁଜ ପୋଷାକ ପିନ୍ଧନ୍ତି, ମେହେନ୍ଦି ଲଗାନ୍ତି, ସଜା ଦୋଳିରେ ଦୋଳି ଖେଳନ୍ତି, "
             "ଶ୍ରାବଣର ଗୀତ ଗାଆନ୍ତି ଏବଂ ଅନେକେ ସ୍ୱାମୀଙ୍କ ପାଇଁ ଉପବାସ କରନ୍ତି।"),
        "nag-panchami": ("ନାଗ ପଞ୍ଚମୀ, ଶ୍ରାବଣ ଶୁକ୍ଳ ପଞ୍ଚମୀ, ନାଗ ଦେବତାଙ୍କ ପୂଜାର ଦିନ। ସାପର ଚିତ୍ର ଆଙ୍କି "
             "ବା ମୂର୍ତ୍ତି ସ୍ଥାପନ କରି କ୍ଷୀର, ଫୁଲ ଓ ମିଠା ଅର୍ପଣ କରାଯାଏ ଏବଂ ପରିବାରର ସୁରକ୍ଷା ପାଇଁ "
             "ପ୍ରାର୍ଥନା କରାଯାଏ। (ଗୁଜରାଟରେ ନାଗ ପଞ୍ଚମ ପରେ, ଭାଦ୍ରପଦରେ ପଡ଼େ।)"),
        "kajari-teej": ("କଜରୀ (କଜଲି, ବଡ଼ି) ତୀଜ, ଭାଦ୍ରପଦ କୃଷ୍ଣ ତୃତୀୟା (ପୂର୍ଣ୍ଣିମାନ୍ତ), ଉତ୍ତରପ୍ରଦେଶ, "
             "ବିହାର, ରାଜସ୍ଥାନ ଓ ମଧ୍ୟପ୍ରଦେଶର ବିବାହିତା ମହିଳାମାନେ ପାଳନ କରନ୍ତି। ସେମାନେ ଉପବାସ କରନ୍ତି, "
             "ନିମ୍ବ ଗଛ (ନିମଡ଼ି ମାତା)ର ପୂଜା କରନ୍ତି ଏବଂ ଜହ୍ନକୁ ଅର୍ଘ୍ୟ ଦେଇ ଉପବାସ ଭାଙ୍ଗନ୍ତି; କଜରୀ "
             "ଲୋକଗୀତ ଗାନ କରାଯାଏ।"),
        "hal-shashthi": ("ହଳ ଷଷ୍ଠୀ (ଲଲହୀ ଛଠ, ହରଛଠ), ଭାଦ୍ରପଦ କୃଷ୍ଣ ଷଷ୍ଠୀ (ପୂର୍ଣ୍ଣିମାନ୍ତ), ଶ୍ରୀବଳରାମଙ୍କ "
             "ଜନ୍ମଦିନ, ଯାହାଙ୍କ ଅସ୍ତ୍ର ହଳ। ମାଆମାନେ ସନ୍ତାନଙ୍କ ପାଇଁ ଉପବାସ କରନ୍ତି ଏବଂ ହଳରେ ଚଷା ଜମିର "
             "କୌଣସି ଫସଲ ଖାଆନ୍ତି ନାହିଁ - ପ୍ରାୟତଃ ପସହୀ ଚାଉଳ ଓ ମଇଁଷି କ୍ଷୀର ଖିଆଯାଏ।"),
        "hartalika-teej": ("ହରତାଳିକା ତୀଜ, ଭାଦ୍ରପଦ ଶୁକ୍ଳ ତୃତୀୟା, ଶିବଙ୍କୁ ପାଇବା ପାଇଁ ପାର୍ବତୀଙ୍କ ତପସ୍ୟାକୁ "
             "ସ୍ମରଣ କରେ। ମହିଳାମାନେ ନିର୍ଜଳା ଉପବାସ କରନ୍ତି, ମାଟିରେ ଶିବ-ପାର୍ବତୀଙ୍କ ମୂର୍ତ୍ତି ଗଢ଼ି ପୂଜା "
             "କରନ୍ତି (ପ୍ରାତଃକାଳର ପୂଜା ଶ୍ରେୟ), ରାତିରେ ଜାଗରଣ କରନ୍ତି ଏବଂ ପରଦିନ ସକାଳେ ଉପବାସ "
             "ଭାଙ୍ଗନ୍ତି।"),
        "rishi-panchami": ("ଋଷି ପଞ୍ଚମୀ, ଭାଦ୍ରପଦ ଶୁକ୍ଳ ପଞ୍ଚମୀ, ସପ୍ତର୍ଷି - ସାତ ମହର୍ଷିଙ୍କୁ - ସମ୍ମାନ "
             "ଦେବାର ଦିନ। ବିଶେଷକରି ମହିଳାମାନେ ସ୍ନାନ ଓ ଉପବାସ କରି ମଧ୍ୟାହ୍ନରେ ଋଷିମାନଙ୍କ ପୂଜା କରନ୍ତି, "
             "ଅଜାଣତରେ ହୋଇଥିବା ତ୍ରୁଟିରୁ ଶୁଦ୍ଧି ପାଇଁ।"),
        "anant-chaturdashi": ("ଅନନ୍ତ ଚତୁର୍ଦ୍ଦଶୀ, ଭାଦ୍ରପଦ ଶୁକ୍ଳ ଚତୁର୍ଦ୍ଦଶୀ, ଅନନ୍ତ ରୂପରେ ଭଗବାନ ବିଷ୍ଣୁଙ୍କ "
             "ପୂଜାର ଦିନ। ପୂଜା ପରେ ଚଉଦଟି ଗଣ୍ଠି ଥିବା ପବିତ୍ର ସୂତା (ଅନନ୍ତ ସୂତ୍ର) ବାହୁରେ ବନ୍ଧାଯାଏ; ଏହି "
             "ଦିନ ଗଣେଶ ପ୍ରତିମା ବିସର୍ଜନ (ଗଣେଶ ବିସର୍ଜନ) ମଧ୍ୟ ହୁଏ।"),
        "pitru-paksha": ("ପିତୃପକ୍ଷ, ପିତୃପୁରୁଷଙ୍କ ପକ୍ଷ, ଆଶ୍ୱିନ (ପୂର୍ଣ୍ଣିମାନ୍ତ)ର କୃଷ୍ଣପକ୍ଷର ପ୍ରତିପଦାରୁ "
             "ଅମାବାସ୍ୟା ପର୍ଯ୍ୟନ୍ତ ଚାଲେ। ପିତୃପୁରୁଷଙ୍କ ପରଲୋକ ତିଥିରେ ପରିବାରମାନେ କୁତୁପ, ରୌହିଣ ବା "
             "ଅପରାହ୍ଣ କାଳରେ ତର୍ପଣ ଓ ଶ୍ରାଦ୍ଧ କରନ୍ତି - ପିଣ୍ଡଦାନ, ବ୍ରାହ୍ମଣ ଭୋଜନ ଏବଂ ଗାଈ, କାଉ ଓ "
             "କୁକୁରଙ୍କୁ ଖାଦ୍ୟ ଦେବା।"),
        "sarva-pitru-amavasya": ("ସର୍ବପିତୃ ଅମାବାସ୍ୟା (ମହାଳୟା ଅମାବାସ୍ୟା) ପିତୃପକ୍ଷର ଶେଷ ଦିନ। ଏହି "
             "ଦିନର ଶ୍ରାଦ୍ଧ ସମସ୍ତ ପିତୃପୁରୁଷଙ୍କ ପାଖରେ ପହଞ୍ଚେ, ଯାହାଙ୍କ ତିଥି ଜଣା ନାହିଁ ସେମାନଙ୍କ "
             "ପାଖରେ ମଧ୍ୟ; ଏହା କୁତୁପ, ରୌହିଣ ବା ଅପରାହ୍ଣ କାଳରେ କରାଯାଏ।"),
        "narak-chaturdashi": ("ନରକ ଚତୁର୍ଦ୍ଦଶୀ (ରୂପ ଚୌଦସ), କାର୍ତ୍ତିକ କୃଷ୍ଣ ଚତୁର୍ଦ୍ଦଶୀ (ପୂର୍ଣ୍ଣିମାନ୍ତ), "
             "ନରକାସୁର ଉପରେ ଶ୍ରୀକୃଷ୍ଣଙ୍କ ବିଜୟକୁ ସ୍ମରଣ କରେ। ସୂର୍ଯ୍ୟୋଦୟ ପୂର୍ବରୁ, ଜହ୍ନ ଆକାଶରେ ଥିବା "
             "ବେଳେ, ଉବଟନ ଲଗାଇ ତେଲ ସ୍ନାନ (ଅଭ୍ୟଙ୍ଗ ସ୍ନାନ) କରାଯାଏ ଏବଂ ସନ୍ଧ୍ୟାରେ ଯମଙ୍କ ପାଇଁ ଦୀପ "
             "ଜଳାଯାଏ।"),
        "tulsi-vivah": ("ତୁଳସୀ ବିବାହ, କାର୍ତ୍ତିକ ଶୁକ୍ଳ ଦ୍ୱାଦଶୀରେ, ତୁଳସୀ ଗଛ (ବୃନ୍ଦା ରୂପରେ) ସହିତ "
             "ଶାଳଗ୍ରାମ ରୂପୀ ଭଗବାନ ବିଷ୍ଣୁଙ୍କ ବିଧିବଦ୍ଧ ବିବାହ। ପରିବାରମାନେ ତୁଳସୀଙ୍କୁ କନ୍ୟା ପରି ସଜାଇ "
             "ବିବାହର ରୀତିନୀତି ପାଳନ କରନ୍ତି; ଏହା ପରେ ହିନ୍ଦୁ ବିବାହ ଋତୁ ଆରମ୍ଭ ହୁଏ।"),
        "kartik-purnima": ("କାର୍ତ୍ତିକ ପୂର୍ଣ୍ଣିମା ପବିତ୍ର କାର୍ତ୍ତିକ ମାସର ସମାପ୍ତି। ଗଙ୍ଗା ବା କୌଣସି ପବିତ୍ର "
             "ନଦୀରେ ସ୍ନାନ ଓ ଦାନ ପାଇଁ ଏହା ଏକ ମହାନ ଦିନ; ଏହା ଗୁରୁ ନାନକ ଜୟନ୍ତୀ ଓ ତ୍ରିପୁରୀ ପୂର୍ଣ୍ଣିମା "
             "ମଧ୍ୟ, ଯେଉଁ ଦିନ ଶିବ ତ୍ରିପୁରାସୁରକୁ ବଧ କରିଥିଲେ। ଓଡ଼ିଶାରେ ଏହି ଦିନ ଭୋରରୁ ବୋଇତ ବନ୍ଦାଣ "
             "ହୁଏ - ଛୋଟ ଡଙ୍ଗା ଭସାଇ ସାଧବମାନଙ୍କ ସମୁଦ୍ର ଯାତ୍ରାକୁ ସ୍ମରଣ କରାଯାଏ।"),
        "dev-deepawali": ("ଦେବ ଦୀପାବଳି, 'ଦେବତାଙ୍କ ଦୀପାବଳି', କାର୍ତ୍ତିକ ପୂର୍ଣ୍ଣିମାର ସନ୍ଧ୍ୟାରେ ପାଳିତ ହୁଏ, "
             "ସବୁଠାରୁ ଅଧିକ ବାରାଣସୀର ଘାଟରେ, ଯାହା ଲକ୍ଷ ଲକ୍ଷ ଦୀପରେ ଆଲୋକିତ ହୁଏ। ଏହା ତ୍ରିପୁରାସୁର "
             "ଉପରେ ଶିବଙ୍କ ବିଜୟର ଦିନ; ପ୍ରଦୋଷ କାଳରେ ଗଙ୍ଗାଙ୍କୁ ଦୀପ ଅର୍ପଣ କରାଯାଏ।"),
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
    "bn": {
        "holika-dahan": ("তারিখ দৃক পঞ্চাঙ্গ অনুযায়ী। পূর্ণিমার পুরো রাত ভদ্রা থাকলে এবং পরদিনের "
             "বেশিরভাগ সময় পূর্ণিমা থাকলে দৃক পঞ্চাঙ্গ হোলিকা দহন পরের সন্ধ্যার প্রদোষে দেয় (যেমন "
             "2026-এ, 3 মার্চ); কিছু পঞ্জিকা আবার প্রথম রাতেই, ভদ্রা শেষ হওয়ার পরে, দেরির একটি সময় "
             "দেয়।"),
        "janmashtami": ("তারিখ দৃক পঞ্চাঙ্গের স্মার্ত (সাধারণ) গণনা অনুযায়ী, মধ্যরাতে রোহিণী নক্ষত্রকে "
             "অগ্রাধিকার দিয়ে। বৈষ্ণব/ইসকন সম্প্রদায় কখনও কখনও এক দিন পরে জন্মাষ্টমী পালন করে।"),
        "devuthani-ekadashi": ("এটি স্মার্ত (গৃহস্থ) তারিখ। একাদশী দুদিন জুড়ে থাকলে বৈষ্ণবরা দ্বিতীয় "
             "দিনে উপবাস করতে পারেন।"),
        "dussehra": ("তারিখ দৃক পঞ্চাঙ্গ অনুযায়ী (অপরাহ্ণে দশমী, শ্রবণা নক্ষত্রকে অগ্রাধিকার)। বাংলায় "
             "ও কিছু পঞ্জিকায় বিজয়া দশমী এক দিন পরে পড়তে পারে।"),
        "jivitputrika": ("তারিখ দৃক পঞ্চাঙ্গ অনুযায়ী (মধ্যাহ্নে অষ্টমী; সূর্যোদয়ে অল্প সময়ের জন্য "
             "থাকলে, যেমন 2023-এ, আগের দিন)। নহায়-খায় আগের দিন এবং পারণ পরদিন সকালে; আঞ্চলিক "
             "পঞ্জিকায় (যেমন মিথিলা) এক দিনের তফাত হতে পারে।"),
        "vat-savitri": ("দুটি প্রথা: উত্তর ভারত বট সাবিত্রী পালন করে জ্যৈষ্ঠ অমাবস্যায় (এই তারিখ); "
             "মহারাষ্ট্র, গুজরাট ও দক্ষিণ ভারত পনেরো দিন পরে বট পূর্ণিমা হিসেবে পালন করে।"),
        "vat-purnima": ("দুটি প্রথা: এটি মহারাষ্ট্র, গুজরাট ও দক্ষিণ ভারতের পূর্ণিমা (অমান্ত) তারিখ; "
             "উত্তর ভারত পনেরো দিন আগে অমাবস্যায় বট সাবিত্রী পালন করে।"),
        "ganga-dussehra": ("জ্যৈষ্ঠ মাস দুবার হলে (অধিক মাস, যেমন 2026-এ) দৃক পঞ্চাঙ্গ গঙ্গা দশহরা "
             "অধিক জ্যৈষ্ঠেই রাখে; কিছু পঞ্জিকা এক মাস পরে নিজ জ্যৈষ্ঠের তারিখ দেয়।"),
        "pitru-paksha": ("দৃক পঞ্চাঙ্গ পিতৃপক্ষ গোনে প্রতিপদ শ্রাদ্ধ থেকে; পূর্ণিমা শ্রাদ্ধ তার আগের "
             "দিন, এবং অনেক ক্যালেন্ডার পক্ষটি সেখান থেকেই শুরু করে।"),
        "dev-deepawali": ("দৃক পঞ্চাঙ্গ দেব দীপাবলির তারিখ বারাণসীর জন্য প্রকাশ করে; এখানকার তারিখ "
             "একই নিয়মে (প্রদোষে পূর্ণিমা), আর দেখানো প্রদোষ কাল নয়াদিল্লির।"),
        "kartik-purnima": ("এটি স্নান-দানের দিন (সূর্যোদয়ে পূর্ণিমা)। পূর্ণিমা আগের দিন দুপুরের পরে "
             "শুরু হলে পূর্ণিমার উপবাস ও দেব দীপাবলি এক দিন আগে পড়তে পারে।"),
    },
    "or": {
        "holika-dahan": ("ତାରିଖ ଦୃକ ପଞ୍ଚାଙ୍ଗ ଅନୁଯାୟୀ। ପୂର୍ଣ୍ଣିମାର ପୂରା ରାତି ଭଦ୍ରା ରହିଲେ ଏବଂ ପରଦିନର "
             "ଅଧିକାଂଶ ସମୟ ପୂର୍ଣ୍ଣିମା ରହିଲେ ଦୃକ ପଞ୍ଚାଙ୍ଗ ହୋଲିକା ଦହନ ପରଦିନ ସନ୍ଧ୍ୟାର ପ୍ରଦୋଷରେ ଦିଏ "
             "(ଯେପରି 2026ରେ, 3 ମାର୍ଚ୍ଚ); କିଛି ପାଞ୍ଜି ପ୍ରଥମ ରାତିରେ ହିଁ, ଭଦ୍ରା ଶେଷ ହେବା ପରେ, ଡେରିର "
             "ଏକ ସମୟ ଦିଅନ୍ତି।"),
        "janmashtami": ("ତାରିଖ ଦୃକ ପଞ୍ଚାଙ୍ଗର ସ୍ମାର୍ତ୍ତ (ସାଧାରଣ) ଗଣନା ଅନୁଯାୟୀ, ମଧ୍ୟରାତ୍ରିରେ ରୋହିଣୀ "
             "ନକ୍ଷତ୍ରକୁ ଅଗ୍ରାଧିକାର ଦେଇ। ବୈଷ୍ଣବ/ଇସ୍କନ ସମ୍ପ୍ରଦାୟ କେବେକେବେ ଗୋଟିଏ ଦିନ ପରେ ଜନ୍ମାଷ୍ଟମୀ "
             "ପାଳନ କରନ୍ତି।"),
        "devuthani-ekadashi": ("ଏହା ସ୍ମାର୍ତ୍ତ (ଗୃହସ୍ଥ) ତାରିଖ। ଏକାଦଶୀ ଦୁଇ ଦିନ ବ୍ୟାପୀ ରହିଲେ ବୈଷ୍ଣବମାନେ "
             "ଦ୍ୱିତୀୟ ଦିନ ଉପବାସ କରିପାରନ୍ତି।"),
        "dussehra": ("ତାରିଖ ଦୃକ ପଞ୍ଚାଙ୍ଗ ଅନୁଯାୟୀ (ଅପରାହ୍ଣରେ ଦଶମୀ, ଶ୍ରବଣା ନକ୍ଷତ୍ରକୁ ଅଗ୍ରାଧିକାର)। ବଙ୍ଗ "
             "ଓ କିଛି ପାଞ୍ଜିରେ ବିଜୟା ଦଶମୀ ଗୋଟିଏ ଦିନ ପରେ ପଡ଼ିପାରେ।"),
        "jivitputrika": ("ତାରିଖ ଦୃକ ପଞ୍ଚାଙ୍ଗ ଅନୁଯାୟୀ (ମଧ୍ୟାହ୍ନରେ ଅଷ୍ଟମୀ; ସୂର୍ଯ୍ୟୋଦୟରେ ଅଳ୍ପ ସମୟ ପାଇଁ "
             "ଥିଲେ, ଯେପରି 2023ରେ, ଆଗଦିନ)। ନହାୟ-ଖାୟ ଆଗଦିନ ଏବଂ ପାରଣ ପରଦିନ ସକାଳେ; ଆଞ୍ଚଳିକ ପାଞ୍ଜିରେ "
             "(ଯେପରି ମିଥିଳା) ଗୋଟିଏ ଦିନର ଫରକ ହୋଇପାରେ।"),
        "vat-savitri": ("ଦୁଇଟି ପରମ୍ପରା: ଉତ୍ତର ଭାରତ ବଟ ସାବିତ୍ରୀ ଜ୍ୟେଷ୍ଠ ଅମାବାସ୍ୟାରେ (ଏହି ତାରିଖ) ପାଳନ "
             "କରେ; ମହାରାଷ୍ଟ୍ର, ଗୁଜରାଟ ଓ ଦକ୍ଷିଣ ଭାରତ ପନ୍ଦର ଦିନ ପରେ ବଟ ପୂର୍ଣ୍ଣିମା ଭାବେ ପାଳନ କରେ।"),
        "vat-purnima": ("ଦୁଇଟି ପରମ୍ପରା: ଏହା ମହାରାଷ୍ଟ୍ର, ଗୁଜରାଟ ଓ ଦକ୍ଷିଣ ଭାରତର ପୂର୍ଣ୍ଣିମା (ଅମାନ୍ତ) "
             "ତାରିଖ; ଉତ୍ତର ଭାରତ ପନ୍ଦର ଦିନ ପୂର୍ବରୁ ଅମାବାସ୍ୟାରେ ବଟ ସାବିତ୍ରୀ ପାଳନ କରେ।"),
        "ganga-dussehra": ("ଜ୍ୟେଷ୍ଠ ମାସ ଦୁଇଥର ହେଲେ (ଅଧିକ ମାସ, ଯେପରି 2026ରେ) ଦୃକ ପଞ୍ଚାଙ୍ଗ ଗଙ୍ଗା "
             "ଦଶହରା ଅଧିକ ଜ୍ୟେଷ୍ଠରେ ରଖେ; କିଛି ପାଞ୍ଜି ଏକ ମାସ ପରେ ନିଜ ଜ୍ୟେଷ୍ଠର ତାରିଖ ଦିଅନ୍ତି।"),
        "pitru-paksha": ("ଦୃକ ପଞ୍ଚାଙ୍ଗ ପିତୃପକ୍ଷ ପ୍ରତିପଦା ଶ୍ରାଦ୍ଧରୁ ଗଣେ; ପୂର୍ଣ୍ଣିମା ଶ୍ରାଦ୍ଧ ତାହାର ଆଗଦିନ, "
             "ଏବଂ ଅନେକ କ୍ୟାଲେଣ୍ଡର ପକ୍ଷଟି ସେଠାରୁ ହିଁ ଆରମ୍ଭ କରନ୍ତି।"),
        "dev-deepawali": ("ଦୃକ ପଞ୍ଚାଙ୍ଗ ଦେବ ଦୀପାବଳିର ତାରିଖ ବାରାଣସୀ ପାଇଁ ପ୍ରକାଶ କରେ; ଏଠାରେ ତାରିଖ ସେହି "
             "ସମାନ ନିୟମରେ (ପ୍ରଦୋଷରେ ପୂର୍ଣ୍ଣିମା), ଆଉ ଦେଖାଯାଇଥିବା ପ୍ରଦୋଷ କାଳ ନୂଆଦିଲ୍ଲୀର।"),
        "kartik-purnima": ("ଏହା ସ୍ନାନ-ଦାନର ଦିନ (ସୂର୍ଯ୍ୟୋଦୟରେ ପୂର୍ଣ୍ଣିମା)। ପୂର୍ଣ୍ଣିମା ଆଗଦିନ ଅପରାହ୍ନରେ "
             "ଆରମ୍ଭ ହେଲେ ପୂର୍ଣ୍ଣିମା ଉପବାସ ଓ ଦେବ ଦୀପାବଳି ଗୋଟିଏ ଦିନ ଆଗରୁ ପଡ଼ିପାରେ।"),
    },
}


# DIVASTRO-123: "how the date is fixed" for languages festivals.py does not write
# (it writes rule_en / rule_hi). vrat_pages._rule builds
#   [month (amanta)] paksha tithi: <rule.<kind>>
# from the observance's tithi and lunar month (names_<code>), or uses key.<key>
# for the four observances festivals.py describes in its own words.
# Placeholders: "tithi" {month} {paksha} {tithi} {rule}; "month" {month}.
RULE: dict[str, dict[str, str]] = {
    "bn": {
        "tithi": "{month}{paksha} {tithi}: {rule}",
        "month": "{month} (অমান্ত) ",
        "rule.udaya": "সূর্যোদয়ের সময় যে তিথি থাকে",
        "rule.pratah": "প্রাতঃকালে (দিনের প্রথম পঞ্চমাংশে) ব্যাপ্ত তিথি",
        "rule.purvahna": "পূর্বাহ্ণে ব্যাপ্ত তিথি",
        "rule.madhyahna": "মধ্যাহ্নে (দিনের মাঝের পঞ্চমাংশে) ব্যাপ্ত তিথি",
        "rule.aparahna": "অপরাহ্ণে (দিনের চতুর্থ পঞ্চমাংশে) ব্যাপ্ত তিথি",
        "rule.dina": "সূর্যোদয় থেকে সূর্যাস্তের মধ্যে তিথি থাকা প্রথম দিন",
        "rule.sayahna": "সূর্যাস্তের সময় যে তিথি থাকে",
        "rule.pradosh": "প্রদোষকালে (সূর্যাস্তের পরে) ব্যাপ্ত তিথি",
        "rule.nishita": "নিশীথকালে (মধ্যরাতে) ব্যাপ্ত তিথি",
        "rule.moonrise": "চন্দ্রোদয়ের সময় ব্যাপ্ত তিথি",
        "key.ekadashi": ("স্মার্ত মত: সূর্যোদয়ের সময় একাদশী (দুই সূর্যোদয়ে থাকলে দ্বিতীয় দিন); "
                         "পারণ পরের দিন সূর্যোদয় ও হরিবাসরের পরে, প্রাতঃকালের মধ্যে এবং দ্বাদশী "
                         "শেষ হওয়ার আগে"),
        "key.makar_sankranti": "নিরয়ণ মকর রাশিতে সূর্যের প্রবেশ; সংক্রান্তি থেকে সূর্যাস্ত পর্যন্ত পুণ্যকাল",
        "key.lohri": "মকর সংক্রান্তির আগের দিন",
        "key.holi": "হোলিকা দহনের পরের দিন",
    },
    "or": {
        "tithi": "{month}{paksha} {tithi}: {rule}",
        "month": "{month} (ଅମାନ୍ତ) ",
        "rule.udaya": "ସୂର୍ଯ୍ୟୋଦୟ ସମୟରେ ଥିବା ତିଥି",
        "rule.pratah": "ପ୍ରାତଃକାଳରେ (ଦିନର ପ୍ରଥମ ପଞ୍ଚମାଂଶରେ) ବ୍ୟାପ୍ତ ତିଥି",
        "rule.purvahna": "ପୂର୍ବାହ୍ଣରେ ବ୍ୟାପ୍ତ ତିଥି",
        "rule.madhyahna": "ମଧ୍ୟାହ୍ନରେ (ଦିନର ମଝି ପଞ୍ଚମାଂଶରେ) ବ୍ୟାପ୍ତ ତିଥି",
        "rule.aparahna": "ଅପରାହ୍ଣରେ (ଦିନର ଚତୁର୍ଥ ପଞ୍ଚମାଂଶରେ) ବ୍ୟାପ୍ତ ତିଥି",
        "rule.dina": "ସୂର୍ଯ୍ୟୋଦୟରୁ ସୂର୍ଯ୍ୟାସ୍ତ ମଧ୍ୟରେ ତିଥି ଥିବା ପ୍ରଥମ ଦିନ",
        "rule.sayahna": "ସୂର୍ଯ୍ୟାସ୍ତ ସମୟରେ ଥିବା ତିଥି",
        "rule.pradosh": "ପ୍ରଦୋଷ କାଳରେ (ସୂର୍ଯ୍ୟାସ୍ତ ପରେ) ବ୍ୟାପ୍ତ ତିଥି",
        "rule.nishita": "ନିଶୀଥ କାଳରେ (ମଧ୍ୟରାତ୍ରିରେ) ବ୍ୟାପ୍ତ ତିଥି",
        "rule.moonrise": "ଚନ୍ଦ୍ରୋଦୟ ସମୟରେ ବ୍ୟାପ୍ତ ତିଥି",
        "key.ekadashi": ("ସ୍ମାର୍ତ୍ତ ମତ: ସୂର୍ଯ୍ୟୋଦୟ ସମୟରେ ଏକାଦଶୀ (ଦୁଇ ସୂର୍ଯ୍ୟୋଦୟରେ ଥିଲେ ଦ୍ୱିତୀୟ ଦିନ); "
                         "ପାରଣ ପରଦିନ ସୂର୍ଯ୍ୟୋଦୟ ଓ ହରିବାସର ପରେ, ପ୍ରାତଃକାଳ ମଧ୍ୟରେ ଏବଂ ଦ୍ୱାଦଶୀ "
                         "ଶେଷ ହେବା ପୂର୍ବରୁ"),
        "key.makar_sankranti": "ନିରୟଣ ମକର ରାଶିରେ ସୂର୍ଯ୍ୟଙ୍କ ପ୍ରବେଶ; ସଂକ୍ରାନ୍ତିରୁ ସୂର୍ଯ୍ୟାସ୍ତ ପର୍ଯ୍ୟନ୍ତ ପୁଣ୍ୟ କାଳ",
        "key.lohri": "ମକର ସଂକ୍ରାନ୍ତିର ପୂର୍ବ ଦିନ",
        "key.holi": "ହୋଲିକା ଦହନର ପରଦିନ",
    },
}
