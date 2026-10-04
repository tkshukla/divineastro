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
}
