"""The text of the recurring-observance year pages (recurring_pages.py), per language
(DIVASTRO-141).

    /purnima-2026  /amavasya-2026  /pradosh-vrat-2026  /sankashti-chaturthi-2026
    /masik-shivratri-2026  /kalashtami-2026   (+ 2027, + /hi/ /kn/ ... copies)

TRANSLATORS: this file is data, in the same style as vrat_text.py. To translate
the pages into another language add a dict to TEXT with any subset of the "en"
keys, then (if every "about.*" key is there) the page is indexable in that
language automatically (recurring_pages.TRANSLATED). A key you leave out falls
back to English.

* Templates keep their `{placeholders}`; the word order around them is yours.
* Values are HTML where marked (the answer box, the about text, notes), plain
  text elsewhere (titles, descriptions, FAQ, labels) - the code escapes those.
* The six observances are keyed by the engine's own key (astro/festivals.py):
  purnima, amavasya, pradosh, sankashti, masik_shivratri, kalashtami.
* Names of the observances, of tithis, months, weekdays and timings
  (moonrise, Pradosh puja, Nishita kaal) are NOT here: they come from
  app/astro/names_<code>.py. A few generic pieces (day label, timing line,
  "timings vary by city", the FAQ's timings answer) are reused from vrat_text.
* Nothing below states a date or a time: every one on the page is computed.
"""

from __future__ import annotations

from . import vrat_text

TEXT: dict[str, dict[str, str]] = {
    "en": {
        # -- page head (plain text): {name} {year} {what} {count} ---------------
        "what.purnima": "Full Moon Dates and Tithi Time",
        "what.amavasya": "New Moon Dates and Tithi Time",
        "what.pradosh": "All Dates and Pradosh Puja Time",
        "what.sankashti": "All Dates and Moonrise Time",
        "what.masik_shivratri": "All Dates and Nishita Puja Time",
        "what.kalashtami": "All Dates and Kala Bhairav Puja",
        "title": "{name} {year}: {what} (New Delhi)",
        "h1": "{name} {year}: {what}",
        "desc": ("All {count} {name} dates in {year} with weekday, Hindu month and tithi start and "
                 "end for New Delhi. {about}{keytime}{next}"),
        "desc.about.purnima": "Full-moon vrat days for Satyanarayan puja, bathing and charity.",
        "desc.about.amavasya": "New-moon days for shraddha and tarpan, with Somvati and Shani Amavasya.",
        "desc.about.pradosh": "Lord Shiva's twilight fast on Trayodashi, with the puja window.",
        "desc.about.sankashti": "Lord Ganesha's fast on Krishna Chaturthi, broken after moonrise.",
        "desc.about.masik_shivratri": "The monthly night of Shiva on Krishna Chaturdashi, with the midnight puja.",
        "desc.about.kalashtami": "Kala Bhairava worship on Krishna Ashtami, every month.",
        "desc.key": " Includes {label}.",
        "desc.next": " Next: {date}.",
        # -- the answer at the top (HTML): {name} {year} {count} {when} {details} -
        "ans.next": "The next {name} is on <strong>{when}</strong> ({details}).",
        "ans.first": ("The first {name} of {year} is on <strong>{when}</strong> ({details}). "
                      "All {count} dates for {year} are listed below."),
        "ans.past": ("All {count} {name} dates for {year} are listed below; the last was on "
                     "<strong>{when}</strong>."),
        "ans.more": " Dates for {year}: {link}.",
        # -- the table (plain text / HTML) ---------------------------------------
        "table.h2": "{name} {year}: all dates",
        "th.date": "Date",
        "th.month": "Hindu month",
        "th.tithi": "Tithi",
        "adhika": "Adhik {month}",
        "also": "Also: ",
        "months.note": ('<p class="note"><small>Months are amanta (a month ends on Amavasya, as in '
                        "South and West India). North Indian purnimanta calendars name the dark "
                        "fortnight one month later.</small></p>"),
        # weekday names that carry their own name (key is Python's weekday, Monday = 0)
        "variant.pradosh.0": "Som Pradosh",
        "variant.pradosh.1": "Bhauma Pradosh",
        "variant.pradosh.5": "Shani Pradosh",
        "variant.sankashti.1": "Angarki Chaturthi",
        "variant.amavasya.0": "Somvati Amavasya",
        "variant.amavasya.5": "Shani Amavasya",
        # -- sections --------------------------------------------------------------
        "about.h2": "What {name} is and how it is observed",
        "city.h2": "Panchang for your city",
        "related.h2": "Related dates and calendars",
        "crumb.page": "{name} {year}",
        # -- what it is and how it is observed (HTML) -------------------------------
        "about.purnima": (
            "<p>Purnima is the full-moon tithi, the last (15th) tithi of the bright fortnight "
            "(Shukla paksha), when the Moon stands opposite the Sun and shines full. Devotees keep a "
            "fast, bathe at dawn (in a river or tirtha where they can), worship Lord Vishnu - "
            "Satyanarayan Katha is the usual Purnima puja - and offer arghya to the Moon in the "
            "evening. Charity (daan) of food, clothes or money on this day is said to bring "
            "multiplied merit.</p><p>Some Purnimas are festivals in their own right: Guru Purnima, "
            "Sharad Purnima, Kartik Purnima and Buddha Purnima, and Holika Dahan is kept on the "
            "Purnima of Phalguna.</p>"),
        "about.amavasya": (
            "<p>Amavasya is the new-moon tithi, the 30th and last tithi of the dark fortnight "
            "(Krishna paksha), when the Moon is in conjunction with the Sun and cannot be seen. It "
            "is the day of the ancestors (pitru): families offer tarpan and shraddha, feed "
            "Brahmins and the poor, give in charity and bathe in holy water. Many people fast and "
            "avoid starting anything new.</p><p>An Amavasya on a Monday is called Somvati "
            "Amavasya and one on a Saturday Shani Amavasya, both given extra weight. The "
            "great Amavasyas are Mauni Amavasya, Sarva Pitru Amavasya (the end of Pitru Paksha) "
            "and the Amavasya of Diwali.</p>"),
        "about.pradosh": (
            "<p>Pradosh Vrat is the fast of Lord Shiva kept on Trayodashi, the 13th tithi, of both "
            "fortnights - so twice a month. Pradosh kaal is the twilight window just after sunset, "
            "when Shiva is believed to be most pleased. Devotees fast through the day, bathe, and "
            "do Shiva puja in the Pradosh window: abhishek with water, milk and bilva (bel) "
            "leaves, a lamp and the Pradosh stotra or Shiva Chalisa. The fast is broken after the "
            "puja.</p><p>A Pradosh on Monday is Som Pradosh, on Tuesday Bhauma Pradosh and on "
            "Saturday Shani Pradosh; the Saturday one is considered especially powerful.</p>"),
        "about.sankashti": (
            "<p>Sankashti Chaturthi (Sankat Hara Chaturthi) is the monthly fast of Lord Ganesha on "
            "Chaturthi, the 4th tithi, of the dark fortnight (Krishna paksha); \"sankashti\" means "
            "deliverance from trouble. Devotees fast through the day, worship Ganesha in the "
            "evening and break the fast only after seeing the Moon and offering it arghya, which "
            "is why moonrise is the key time on this page.</p><p>A Sankashti on a Tuesday is "
            "Angarki Sankashti Chaturthi, believed to be especially fruitful. The Sankashti of "
            "Magha (purnimanta) is kept in North India as Sakat Chauth.</p>"),
        "about.masik_shivratri": (
            "<p>Masik Shivratri (monthly Shivratri) is the night of Lord Shiva kept on Chaturdashi, "
            "the 14th tithi, of the dark fortnight (Krishna paksha) every month. Devotees fast and "
            "keep vigil through the night, bathing the Shiva linga with water, milk, honey and "
            "bilva leaves and chanting \"Om Namah Shivaya\". The best time for the puja is Nishita "
            "kaal, the midnight window.</p><p>Maha Shivratri, which falls on Krishna Chaturdashi of "
            "Phalguna (Magha in the amanta calendar), is the greatest of the twelve.</p>"),
        "about.kalashtami": (
            "<p>Kalashtami (Kala Ashtami) is the monthly day of Lord Kala Bhairava, the fierce form "
            "of Shiva who guards time, kept on Ashtami, the 8th tithi, of the dark fortnight "
            "(Krishna paksha). Devotees fast, worship Bhairava at night with a mustard-oil lamp "
            "and offerings such as black sesame, and feed dogs, which are associated with "
            "him.</p><p>The Kalashtami of Margashirsha in the purnimanta calendar (Kartika in the "
            "amanta calendar) is Kalabhairava Jayanti, his appearance day and the most important "
            "of the year.</p>"),
        # -- why the date is where it is (HTML, after the engine's own rule) ---------
        "note.purnima": (
            "Purnima can begin one evening and end the next afternoon, so the day the tithi starts "
            "and the day of the vrat can differ. The rule settles it: the vrat goes to the day on "
            "which the tithi covers Madhyahna (the middle fifth of the daytime); if it covers "
            "Madhyahna on both days, the earlier day is taken. Some traditions use the sunrise "
            "tithi for the holy bath and charity instead; the table gives the start and end of the "
            "tithi so you can check."),
        "note.amavasya": (
            "Amavasya is a daytime observance (shraddha and tarpan are done in the day), so the date "
            "is the day on which the Amavasya tithi is running at sunrise. The tithi often starts "
            "the evening before, so the times in the table can begin on the previous date. Festival "
            "Amavasyas follow their own rules - Diwali is fixed by Pradosh, Sarva Pitru Amavasya by "
            "Aparahna - and can fall a day away from the date here."),
        "note.pradosh": (
            "The date is decided in the evening, not at sunrise: the vrat goes to the day on which "
            "Trayodashi is running in Pradosh kaal after sunset, so a Trayodashi that starts at "
            "noon and ends the next afternoon is kept on the first day. If the tithi touches "
            "Pradosh kaal on two evenings, the earlier evening is taken. The puja window in the "
            "table starts at sunset in New Delhi, so it moves through the year and from city to "
            "city."),
        "note.sankashti": (
            "Sankashti is decided by the Moon, not the Sun: the vrat goes to the evening on which "
            "Chaturthi is running at moonrise, since that is when the fast is broken. The date can "
            "therefore differ from the Chaturthi date of a Panchang that goes by sunrise. Moonrise "
            "is roughly 50 minutes later each day and differs by several minutes between cities, "
            "so check it for your own city."),
        "note.masik_shivratri": (
            "This is a midnight observance, so the date is the day on which Chaturdashi is running "
            "at Nishita kaal (the 8th of the 15 muhurtas of the night, around midnight). Nishita "
            "can fall just after 12 o'clock, in which case the puja is done in the early hours of "
            "the next date and the time shown carries that date. If the tithi touches Nishita on "
            "two nights, the earlier night is taken."),
        "note.kalashtami": (
            "Kalashtami is a night worship, so the date is the day on which Ashtami is running in "
            "Pradosh kaal (the evening window after sunset); the tithi may begin the previous "
            "morning or end during the night, so check its start and end times in the table. If it "
            "touches Pradosh kaal on two evenings, the earlier evening is taken. Some traditions go "
            "by the midnight tithi instead, which can occasionally differ by a day."),
        # -- FAQ (plain text): {name} {year} {count} {dates} {when} {details} {label} {short} {rule}
        "faq.all_q": "What are the {name} dates in {year}?",
        "faq.all_a": "There are {count} {name} dates in {year} (New Delhi): {dates}.",
        "faq.next_q": "When is the next {name}?",
        "faq.first_q": "When is the first {name} of {year}?",
        "faq.on_a": "{name} is on {when} ({details}).",
        "faq.key_q": "What is the {label} on {name} {short}?",
        "faq.tithi_q": "At what time does the {name} tithi start and end on {short}?",
        "faq.why_q": "How is the {name} date decided?",
        "faq.why_a": "The date follows the rule: {rule}. In {year} this gives {count} dates (New Delhi).",
    },
    "hi": {
        "what.purnima": "पूर्णिमा की सभी तिथियां और तिथि का समय",
        "what.amavasya": "अमावस्या की सभी तिथियां और तिथि का समय",
        "what.pradosh": "सभी तिथियां और प्रदोष पूजा का समय",
        "what.sankashti": "सभी तिथियां और चंद्रोदय का समय",
        "what.masik_shivratri": "सभी तिथियां और निशीथ काल पूजा का समय",
        "what.kalashtami": "सभी तिथियां और काल भैरव पूजा",
        "title": "{name} {year}: {what} (नई दिल्ली)",
        "h1": "{name} {year}: {what}",
        "desc": ("{year} में {name} की सभी {count} तिथियां - वार, हिंदू माह और तिथि का आरंभ व अंत "
                 "(नई दिल्ली)। {about}{keytime}{next}"),
        "desc.about.purnima": "सत्यनारायण पूजा, स्नान और दान वाला पूर्णिमा व्रत।",
        "desc.about.amavasya": "श्राद्ध-तर्पण की अमावस्या, सोमवती और शनि अमावस्या सहित।",
        "desc.about.pradosh": "त्रयोदशी पर भगवान शिव का प्रदोष व्रत और पूजा का समय।",
        "desc.about.sankashti": "कृष्ण चतुर्थी पर गणेश जी का व्रत, चंद्रोदय के बाद पारण।",
        "desc.about.masik_shivratri": "कृष्ण चतुर्दशी की मासिक शिवरात्रि और निशीथ काल की पूजा।",
        "desc.about.kalashtami": "हर माह कृष्ण अष्टमी पर काल भैरव की पूजा।",
        "desc.key": " साथ में {label}।",
        "desc.next": " अगली तिथि: {date}।",
        "ans.next": "{name} की अगली तिथि <strong>{when}</strong> को है ({details})।",
        "ans.first": ("{year} में {name} की पहली तिथि <strong>{when}</strong> को है ({details})। "
                      "{year} की सभी {count} तिथियां नीचे सूची में हैं।"),
        "ans.past": ("{year} में {name} की सभी {count} तिथियां नीचे सूची में हैं; अंतिम तिथि "
                     "<strong>{when}</strong> को थी।"),
        "ans.more": " {year} की तिथियां: {link}।",
        "table.h2": "{name} {year}: सभी तिथियां",
        "th.date": "दिनांक",
        "th.month": "हिंदू माह",
        "th.tithi": "तिथि",
        "adhika": "अधिक {month}",
        "also": "साथ में: ",
        "months.note": ('<p class="note"><small>माह अमांत हैं (माह अमावस्या पर पूरा होता है, जैसा दक्षिण व '
                        "पश्चिम भारत में)। उत्तर भारत के पूर्णिमांत पंचांग में कृष्ण पक्ष का नाम एक माह "
                        "आगे का होता है।</small></p>"),
        "variant.pradosh.0": "सोम प्रदोष",
        "variant.pradosh.1": "भौम प्रदोष",
        "variant.pradosh.5": "शनि प्रदोष",
        "variant.sankashti.1": "अंगारकी चतुर्थी",
        "variant.amavasya.0": "सोमवती अमावस्या",
        "variant.amavasya.5": "शनि अमावस्या",
        "about.h2": "{name} क्या है और कैसे मनाई जाती है",
        "city.h2": "अपने शहर का पंचांग",
        "related.h2": "संबंधित तिथियां और कैलेंडर",
        "crumb.page": "{name} {year}",
        "about.purnima": (
            "<p>पूर्णिमा चंद्रमा की पूर्ण तिथि है - शुक्ल पक्ष की अंतिम (15वीं) तिथि, जब चंद्रमा सूर्य के "
            "ठीक सामने होकर पूरा चमकता है। भक्त व्रत रखते हैं, प्रातः स्नान करते हैं (संभव हो तो नदी या "
            "तीर्थ में), भगवान विष्णु की पूजा करते हैं - सत्यनारायण कथा पूर्णिमा की प्रचलित पूजा है - और "
            "शाम को चंद्रमा को अर्घ्य देते हैं। इस दिन अन्न, वस्त्र या धन का दान कई गुना पुण्य देने वाला "
            "माना जाता है।</p><p>कुछ पूर्णिमाएं स्वयं पर्व हैं: गुरु पूर्णिमा, शरद पूर्णिमा, कार्तिक पूर्णिमा और "
            "बुद्ध पूर्णिमा; होलिका दहन फाल्गुन की पूर्णिमा को होता है।</p>"),
        "about.amavasya": (
            "<p>अमावस्या चंद्रमा की नवीन तिथि है - कृष्ण पक्ष की 30वीं और अंतिम तिथि, जब चंद्रमा सूर्य के साथ "
            "होता है और दिखाई नहीं देता। यह पितरों का दिन है: परिवार तर्पण और श्राद्ध करते हैं, ब्राह्मणों व "
            "गरीबों को भोजन कराते हैं, दान देते हैं और पवित्र जल में स्नान करते हैं। बहुत से लोग व्रत रखते हैं और "
            "कोई नया काम शुरू नहीं करते।</p><p>सोमवार की अमावस्या सोमवती अमावस्या और शनिवार की अमावस्या "
            "शनि अमावस्या कहलाती है, दोनों का विशेष महत्व है। प्रमुख अमावस्याएं हैं: मौनी अमावस्या, सर्वपितृ "
            "अमावस्या (पितृ पक्ष का अंत) और दीपावली की अमावस्या।</p>"),
        "about.pradosh": (
            "<p>प्रदोष व्रत भगवान शिव का व्रत है, जो दोनों पक्षों की त्रयोदशी (13वीं तिथि) को रखा जाता है - यानी "
            "महीने में दो बार। प्रदोष काल सूर्यास्त के ठीक बाद का संध्या-समय है, जब शिव जी सबसे प्रसन्न माने "
            "जाते हैं। भक्त दिन भर व्रत रखते हैं, स्नान करते हैं और प्रदोष काल में शिव पूजा करते हैं: जल, दूध और "
            "बिल्वपत्र से अभिषेक, दीपक, प्रदोष स्तोत्र या शिव चालीसा। पूजा के बाद व्रत खोला जाता है।</p>"
            "<p>सोमवार का प्रदोष सोम प्रदोष, मंगलवार का भौम प्रदोष और शनिवार का शनि प्रदोष कहलाता है; "
            "शनि प्रदोष को विशेष शक्तिशाली माना जाता है।</p>"),
        "about.sankashti": (
            "<p>संकष्टी चतुर्थी (संकट हरण चतुर्थी) कृष्ण पक्ष की चतुर्थी (चौथी तिथि) को रखा जाने वाला भगवान "
            "गणेश का मासिक व्रत है; \"संकष्टी\" का अर्थ है संकट से मुक्ति। भक्त दिन भर व्रत रखते हैं, शाम को "
            "गणेश जी की पूजा करते हैं और चंद्रमा के दर्शन कर उसे अर्घ्य देने के बाद ही व्रत खोलते हैं - इसीलिए इस "
            "पन्ने पर चंद्रोदय का समय मुख्य है।</p><p>मंगलवार को पड़ने वाली संकष्टी अंगारकी संकष्टी चतुर्थी "
            "कहलाती है, जिसे विशेष फलदायी माना जाता है। माघ (पूर्णिमांत) की संकष्टी उत्तर भारत में सकट चौथ "
            "के रूप में मनाई जाती है।</p>"),
        "about.masik_shivratri": (
            "<p>मासिक शिवरात्रि हर माह कृष्ण पक्ष की चतुर्दशी (14वीं तिथि) को मनाई जाने वाली भगवान शिव की रात्रि है। "
            "भक्त व्रत रखकर रात भर जागरण करते हैं, शिवलिंग को जल, दूध, शहद और बिल्वपत्र से स्नान कराते हैं और "
            "\"ॐ नमः शिवाय\" का जाप करते हैं। पूजा का श्रेष्ठ समय निशीथ काल, यानी मध्यरात्रि है।</p>"
            "<p>महाशिवरात्रि, जो फाल्गुन (अमांत गणना में माघ) की कृष्ण चतुर्दशी को पड़ती है, बारह में सबसे "
            "बड़ी है।</p>"),
        "about.kalashtami": (
            "<p>कालाष्टमी भगवान काल भैरव का मासिक दिन है - शिव का वह उग्र रूप जो समय के रक्षक हैं - जो कृष्ण पक्ष की "
            "अष्टमी (आठवीं तिथि) को मनाया जाता है। भक्त व्रत रखते हैं, रात में सरसों के तेल के दीपक और काले तिल जैसी "
            "भेंट से भैरव की पूजा करते हैं और कुत्तों को भोजन कराते हैं, जो भैरव से जुड़े माने जाते हैं।</p>"
            "<p>पूर्णिमांत गणना में मार्गशीर्ष (अमांत में कार्तिक) की कालाष्टमी कालभैरव जयंती है - उनका प्रकट "
            "दिवस और वर्ष की सबसे प्रमुख कालाष्टमी।</p>"),
        "note.purnima": (
            "पूर्णिमा एक शाम को शुरू होकर अगली दोपहर तक रह सकती है, इसलिए तिथि जिस दिन शुरू होती है और व्रत का "
            "दिन अलग हो सकते हैं। नियम यह तय करता है: व्रत उस दिन होता है जब तिथि मध्याह्न (दिन का बीच का "
            "पांचवां भाग) में रहती है; दोनों दिन मध्याह्न में हो तो पहला दिन लिया जाता है। कुछ परंपराएं स्नान-दान "
            "के लिए सूर्योदय की तिथि लेती हैं; जांचने के लिए तालिका में तिथि का आरंभ और अंत दिया है।"),
        "note.amavasya": (
            "अमावस्या दिन का अनुष्ठान है (श्राद्ध और तर्पण दिन में होते हैं), इसलिए तारीख वह दिन है जब "
            "सूर्योदय पर अमावस्या तिथि चल रही हो। तिथि अक्सर एक दिन पहले शाम को शुरू हो जाती है, इसलिए तालिका में "
            "समय पिछली तारीख से भी शुरू हो सकता है। पर्व वाली अमावस्याओं के अपने नियम हैं - दीपावली प्रदोष से और "
            "सर्वपितृ अमावस्या अपराह्न से तय होती है - और वे यहां की तारीख से एक दिन आगे-पीछे हो सकती हैं।"),
        "note.pradosh": (
            "तारीख शाम से तय होती है, सूर्योदय से नहीं: व्रत उस दिन होता है जब सूर्यास्त के बाद प्रदोष काल में "
            "त्रयोदशी चल रही हो, इसलिए दोपहर में शुरू होकर अगली दोपहर तक रहने वाली त्रयोदशी का व्रत पहले दिन होता "
            "है। यदि तिथि दो शामों को प्रदोष काल को छूए तो पहली शाम ली जाती है। तालिका में पूजा का समय नई दिल्ली "
            "के सूर्यास्त से शुरू होता है, इसलिए यह साल भर और शहर-शहर बदलता है।"),
        "note.sankashti": (
            "संकष्टी चंद्रमा से तय होती है, सूर्य से नहीं: व्रत उस शाम को होता है जब चंद्रोदय के समय चतुर्थी चल रही हो, "
            "क्योंकि उसी समय व्रत खोला जाता है। इसलिए तारीख सूर्योदय वाले पंचांग की चतुर्थी की तारीख से अलग हो "
            "सकती है। चंद्रोदय हर दिन लगभग 50 मिनट देर से होता है और शहरों में कई मिनट का अंतर रहता है, इसलिए "
            "अपने शहर का समय देखें।"),
        "note.masik_shivratri": (
            "यह मध्यरात्रि का अनुष्ठान है, इसलिए तारीख वह दिन है जब निशीथ काल (रात के 15 मुहूर्तों में आठवां, "
            "लगभग मध्यरात्रि) में चतुर्दशी चल रही हो। निशीथ 12 बजे के कुछ बाद पड़ सकता है, तब पूजा अगली तारीख की "
            "भोर के घंटों में होती है और दिखाया समय उसी तारीख के साथ दिया है। यदि तिथि दो रातों को निशीथ को छूए तो "
            "पहली रात ली जाती है।"),
        "note.kalashtami": (
            "कालाष्टमी रात की उपासना है, इसलिए तारीख वह दिन है जब प्रदोष काल (सूर्यास्त के बाद की संध्या) में "
            "अष्टमी चल रही हो; तिथि पिछली सुबह शुरू या रात में समाप्त हो सकती है, इसलिए तालिका में उसका आरंभ और "
            "अंत देखें। यदि वह दो शामों को प्रदोष काल को छूए तो पहली शाम ली जाती है। कुछ परंपराएं मध्यरात्रि की तिथि "
            "मानती हैं, जिससे कभी-कभी एक दिन का अंतर आ सकता है।"),
        "faq.all_q": "{year} में {name} की तिथियां कौन-सी हैं?",
        "faq.all_a": "{year} में {name} की {count} तिथियां हैं (नई दिल्ली): {dates}।",
        "faq.next_q": "{name} की अगली तिथि कब है?",
        "faq.first_q": "{year} में {name} की पहली तिथि कब है?",
        "faq.on_a": "{name} {when} को है ({details})।",
        "faq.key_q": "{name} {short} को {label} क्या है?",
        "faq.tithi_q": "{name} {short} को तिथि कितने बजे शुरू और खत्म होती है?",
        "faq.why_q": "{name} की तारीख कैसे तय होती है?",
        "faq.why_a": "तारीख इस नियम से तय होती है: {rule}। {year} में इससे {count} तिथियां बनती हैं (नई दिल्ली)।",
    },
    "kn": {
        "what.purnima": "ಹುಣ್ಣಿಮೆ ದಿನಾಂಕಗಳು ಮತ್ತು ತಿಥಿ ಸಮಯ",
        "what.amavasya": "ಅಮಾವಾಸ್ಯೆ ದಿನಾಂಕಗಳು ಮತ್ತು ತಿಥಿ ಸಮಯ",
        "what.pradosh": "ಎಲ್ಲ ದಿನಾಂಕಗಳು ಮತ್ತು ಪ್ರದೋಷ ಪೂಜಾ ಸಮಯ",
        "what.sankashti": "ಎಲ್ಲ ದಿನಾಂಕಗಳು ಮತ್ತು ಚಂದ್ರೋದಯ ಸಮಯ",
        "what.masik_shivratri": "ಎಲ್ಲ ದಿನಾಂಕಗಳು ಮತ್ತು ನಿಶೀಥ ಪೂಜಾ ಸಮಯ",
        "what.kalashtami": "ಎಲ್ಲ ದಿನಾಂಕಗಳು ಮತ್ತು ಕಾಲಭೈರವ ಪೂಜೆ",
        "title": "{name} {year}: {what} (ನವದೆಹಲಿ)",
        "h1": "{name} {year}: {what}",
        "desc": ("{year}ರಲ್ಲಿ {name}: ಎಲ್ಲ {count} ದಿನಾಂಕಗಳು - ವಾರ, ಹಿಂದೂ ಮಾಸ, ತಿಥಿ ಆರಂಭ ಮತ್ತು ಅಂತ್ಯ "
                 "(ನವದೆಹಲಿ). {about}{keytime}{next}"),
        "desc.about.purnima": "ಸತ್ಯನಾರಾಯಣ ಪೂಜೆ, ಸ್ನಾನ ಮತ್ತು ದಾನದ ಹುಣ್ಣಿಮೆ ವ್ರತ.",
        "desc.about.amavasya": "ಶ್ರಾದ್ಧ-ತರ್ಪಣದ ಅಮಾವಾಸ್ಯೆ, ಸೋಮವತಿ ಮತ್ತು ಶನಿ ಅಮಾವಾಸ್ಯೆ ಸೇರಿ.",
        "desc.about.pradosh": "ತ್ರಯೋದಶಿಯಂದು ಶಿವನ ಪ್ರದೋಷ ವ್ರತ ಮತ್ತು ಪೂಜಾ ಸಮಯ.",
        "desc.about.sankashti": "ಕೃಷ್ಣ ಚತುರ್ಥಿಯಂದು ಗಣೇಶನ ವ್ರತ, ಚಂದ್ರೋದಯದ ನಂತರ ಪಾರಣೆ.",
        "desc.about.masik_shivratri": "ಕೃಷ್ಣ ಚತುರ್ದಶಿಯ ಮಾಸ ಶಿವರಾತ್ರಿ ಮತ್ತು ನಿಶೀಥ ಕಾಲದ ಪೂಜೆ.",
        "desc.about.kalashtami": "ಪ್ರತಿ ತಿಂಗಳು ಕೃಷ್ಣ ಅಷ್ಟಮಿಯಂದು ಕಾಲಭೈರವ ಪೂಜೆ.",
        "desc.key": " ಜೊತೆಗೆ {label}.",
        "desc.next": " ಮುಂದಿನದು: {date}.",
        "ans.next": "ಮುಂದಿನ {name} <strong>{when}</strong> ರಂದು ({details}).",
        "ans.first": ("{year}ರ ಮೊದಲ {name} <strong>{when}</strong> ರಂದು ({details}). "
                      "{year}ರ ಎಲ್ಲ {count} ದಿನಾಂಕಗಳು ಕೆಳಗಿವೆ."),
        "ans.past": ("{year}ರ ಎಲ್ಲ {count} {name} ದಿನಾಂಕಗಳು ಕೆಳಗಿವೆ; ಕೊನೆಯದು "
                     "<strong>{when}</strong> ರಂದು ಇತ್ತು."),
        "ans.more": " {year}ರ ದಿನಾಂಕಗಳು: {link}.",
        "table.h2": "{name} {year}: ಎಲ್ಲ ದಿನಾಂಕಗಳು",
        "th.date": "ದಿನಾಂಕ",
        "th.month": "ಹಿಂದೂ ಮಾಸ",
        "th.tithi": "ತಿಥಿ",
        "adhika": "ಅಧಿಕ {month}",
        "also": "ಜೊತೆಗೆ: ",
        "months.note": ('<p class="note"><small>ಮಾಸಗಳು ಅಮಾಂತ (ಮಾಸ ಅಮಾವಾಸ್ಯೆಗೆ ಮುಗಿಯುತ್ತದೆ; ದಕ್ಷಿಣ ಮತ್ತು '
                        "ಪಶ್ಚಿಮ ಭಾರತದಲ್ಲಿ ಹೀಗೆ). ಉತ್ತರ ಭಾರತದ ಪೂರ್ಣಿಮಾಂತ ಪಂಚಾಂಗದಲ್ಲಿ ಕೃಷ್ಣ ಪಕ್ಷಕ್ಕೆ ಒಂದು ತಿಂಗಳು "
                        "ಮುಂದಿನ ಹೆಸರು ಇರುತ್ತದೆ.</small></p>"),
        "variant.pradosh.0": "ಸೋಮ ಪ್ರದೋಷ",
        "variant.pradosh.1": "ಭೌಮ ಪ್ರದೋಷ",
        "variant.pradosh.5": "ಶನಿ ಪ್ರದೋಷ",
        "variant.sankashti.1": "ಅಂಗಾರಕ ಚತುರ್ಥಿ",
        "variant.amavasya.0": "ಸೋಮವತಿ ಅಮಾವಾಸ್ಯೆ",
        "variant.amavasya.5": "ಶನಿ ಅಮಾವಾಸ್ಯೆ",
        "about.h2": "{name} ಎಂದರೇನು ಮತ್ತು ಹೇಗೆ ಆಚರಿಸುತ್ತಾರೆ",
        "city.h2": "ನಿಮ್ಮ ನಗರದ ಪಂಚಾಂಗ",
        "related.h2": "ಸಂಬಂಧಿತ ದಿನಾಂಕಗಳು ಮತ್ತು ಕ್ಯಾಲೆಂಡರ್",
        "crumb.page": "{name} {year}",
        "about.purnima": (
            "<p>ಹುಣ್ಣಿಮೆ ಶುಕ್ಲ ಪಕ್ಷದ ಕೊನೆಯ (15ನೇ) ತಿಥಿ; ಆಗ ಚಂದ್ರ ಸೂರ್ಯನ ಎದುರಿಗೆ ಇದ್ದು ಪೂರ್ಣವಾಗಿ ಬೆಳಗುತ್ತಾನೆ. "
            "ಭಕ್ತರು ಉಪವಾಸ ಮಾಡಿ, ಬೆಳಗ್ಗೆ ಸ್ನಾನ ಮಾಡಿ, ವಿಷ್ಣುವನ್ನು ಪೂಜಿಸುತ್ತಾರೆ - ಸತ್ಯನಾರಾಯಣ ಕಥೆ ಹುಣ್ಣಿಮೆಯ "
            "ಸಾಮಾನ್ಯ ಪೂಜೆ - ಮತ್ತು ಸಂಜೆ ಚಂದ್ರನಿಗೆ ಅರ್ಘ್ಯ ನೀಡುತ್ತಾರೆ. ಈ ದಿನ ಮಾಡುವ ದಾನಕ್ಕೆ ಹೆಚ್ಚಿನ ಪುಣ್ಯ "
            "ಎಂದು ನಂಬಿಕೆ.</p><p>ಗುರು ಪೂರ್ಣಿಮೆ, ಶರದ್ ಪೂರ್ಣಿಮೆ, ಕಾರ್ತಿಕ ಪೂರ್ಣಿಮೆ ಮತ್ತು ಬುದ್ಧ ಪೂರ್ಣಿಮೆ ತಮ್ಮದೇ "
            "ಹಬ್ಬಗಳು; ಹೋಲಿಕಾ ದಹನ ಫಾಲ್ಗುಣ ಹುಣ್ಣಿಮೆಯಂದು ನಡೆಯುತ್ತದೆ.</p>"),
        "about.amavasya": (
            "<p>ಅಮಾವಾಸ್ಯೆ ಕೃಷ್ಣ ಪಕ್ಷದ 30ನೇ ಮತ್ತು ಕೊನೆಯ ತಿಥಿ; ಆಗ ಚಂದ್ರ ಸೂರ್ಯನ ಜೊತೆ ಇದ್ದು ಕಾಣಿಸುವುದಿಲ್ಲ. "
            "ಇದು ಪಿತೃಗಳ ದಿನ: ತರ್ಪಣ ಮತ್ತು ಶ್ರಾದ್ಧ ಮಾಡುತ್ತಾರೆ, ಬ್ರಾಹ್ಮಣರಿಗೆ ಮತ್ತು ಬಡವರಿಗೆ ಊಟ ನೀಡುತ್ತಾರೆ, ದಾನ "
            "ಮಾಡುತ್ತಾರೆ, ಪವಿತ್ರ ಜಲದಲ್ಲಿ ಸ್ನಾನ ಮಾಡುತ್ತಾರೆ.</p><p>ಸೋಮವಾರದ ಅಮಾವಾಸ್ಯೆ ಸೋಮವತಿ ಅಮಾವಾಸ್ಯೆ, "
            "ಶನಿವಾರದ್ದು ಶನಿ ಅಮಾವಾಸ್ಯೆ. ಮೌನಿ ಅಮಾವಾಸ್ಯೆ, ಸರ್ವಪಿತೃ ಅಮಾವಾಸ್ಯೆ ಮತ್ತು ದೀಪಾವಳಿಯ ಅಮಾವಾಸ್ಯೆ "
            "ಪ್ರಮುಖವಾದವು.</p>"),
        "about.pradosh": (
            "<p>ಪ್ರದೋಷ ವ್ರತ ಎರಡೂ ಪಕ್ಷಗಳ ತ್ರಯೋದಶಿ (13ನೇ ತಿಥಿ) ದಿನ ಮಾಡುವ ಶಿವನ ವ್ರತ - ತಿಂಗಳಿಗೆ ಎರಡು ಬಾರಿ. "
            "ಪ್ರದೋಷ ಕಾಲ ಸೂರ್ಯಾಸ್ತದ ನಂತರದ ಸಂಧ್ಯಾ ಸಮಯ. ಭಕ್ತರು ಹಗಲು ಉಪವಾಸ ಮಾಡಿ, ಪ್ರದೋಷ ಕಾಲದಲ್ಲಿ ಶಿವ ಪೂಜೆ "
            "ಮಾಡುತ್ತಾರೆ: ನೀರು, ಹಾಲು, ಬಿಲ್ವ ಪತ್ರೆಯಿಂದ ಅಭಿಷೇಕ ಮತ್ತು ದೀಪ. ಪೂಜೆಯ ನಂತರ ಉಪವಾಸ ಬಿಡುತ್ತಾರೆ.</p>"
            "<p>ಸೋಮವಾರದ ಪ್ರದೋಷ ಸೋಮ ಪ್ರದೋಷ, ಮಂಗಳವಾರದ್ದು ಭೌಮ ಪ್ರದೋಷ, ಶನಿವಾರದ್ದು ಶನಿ ಪ್ರದೋಷ.</p>"),
        "about.sankashti": (
            "<p>ಸಂಕಷ್ಟಹರ ಚತುರ್ಥಿ ಕೃಷ್ಣ ಪಕ್ಷದ ಚತುರ್ಥಿ (4ನೇ ತಿಥಿ) ದಿನ ಗಣೇಶನಿಗೆ ಮಾಡುವ ಮಾಸಿಕ ವ್ರತ. ಭಕ್ತರು ಹಗಲು "
            "ಉಪವಾಸ ಮಾಡಿ, ಸಂಜೆ ಗಣೇಶನನ್ನು ಪೂಜಿಸಿ, ಚಂದ್ರನನ್ನು ನೋಡಿ ಅರ್ಘ್ಯ ನೀಡಿದ ನಂತರವೇ ಉಪವಾಸ ಬಿಡುತ್ತಾರೆ - "
            "ಆದ್ದರಿಂದ ಈ ಪುಟದಲ್ಲಿ ಚಂದ್ರೋದಯ ಮುಖ್ಯ ಸಮಯ.</p><p>ಮಂಗಳವಾರ ಬರುವ ಸಂಕಷ್ಟಹರ ಚತುರ್ಥಿ ಅಂಗಾರಕ ಚತುರ್ಥಿ; "
            "ಅದು ವಿಶೇಷ ಫಲದಾಯಕ ಎಂದು ನಂಬಿಕೆ.</p>"),
        "about.masik_shivratri": (
            "<p>ಮಾಸ ಶಿವರಾತ್ರಿ ಪ್ರತಿ ತಿಂಗಳ ಕೃಷ್ಣ ಪಕ್ಷದ ಚತುರ್ದಶಿ (14ನೇ ತಿಥಿ) ದಿನ ಆಚರಿಸುವ ಶಿವನ ರಾತ್ರಿ. ಭಕ್ತರು ಉಪವಾಸ "
            "ಮಾಡಿ ರಾತ್ರಿ ಜಾಗರಣೆ ಮಾಡುತ್ತಾರೆ, ಶಿವಲಿಂಗಕ್ಕೆ ನೀರು, ಹಾಲು, ಜೇನುತುಪ್ಪ, ಬಿಲ್ವ ಪತ್ರೆಯಿಂದ ಅಭಿಷೇಕ ಮಾಡುತ್ತಾರೆ. "
            "ಪೂಜೆಗೆ ಉತ್ತಮ ಸಮಯ ನಿಶೀಥ ಕಾಲ, ಅಂದರೆ ಮಧ್ಯರಾತ್ರಿ.</p><p>ಮಹಾ ಶಿವರಾತ್ರಿ ಹನ್ನೆರಡರಲ್ಲಿ ದೊಡ್ಡದು.</p>"),
        "about.kalashtami": (
            "<p>ಕಾಲಾಷ್ಟಮಿ ಕೃಷ್ಣ ಪಕ್ಷದ ಅಷ್ಟಮಿ (8ನೇ ತಿಥಿ) ದಿನ ಆಚರಿಸುವ ಕಾಲಭೈರವನ ಮಾಸಿಕ ದಿನ. ಭಕ್ತರು ಉಪವಾಸ ಮಾಡಿ, ರಾತ್ರಿ "
            "ಸಾಸಿವೆ ಎಣ್ಣೆಯ ದೀಪದೊಂದಿಗೆ ಭೈರವನನ್ನು ಪೂಜಿಸುತ್ತಾರೆ ಮತ್ತು ನಾಯಿಗಳಿಗೆ ಆಹಾರ ನೀಡುತ್ತಾರೆ.</p>"
            "<p>ಪೂರ್ಣಿಮಾಂತ ಪಂಚಾಂಗದ ಮಾರ್ಗಶಿರ (ಅಮಾಂತದಲ್ಲಿ ಕಾರ್ತಿಕ) ಮಾಸದ ಕಾಲಾಷ್ಟಮಿ ಕಾಲಭೈರವ ಜಯಂತಿ - ವರ್ಷದ "
            "ಪ್ರಮುಖ ಕಾಲಾಷ್ಟಮಿ.</p>"),
        "note.purnima": (
            "ಹುಣ್ಣಿಮೆ ಒಂದು ಸಂಜೆ ಆರಂಭವಾಗಿ ಮರುದಿನ ಮಧ್ಯಾಹ್ನದವರೆಗೆ ಇರಬಹುದು; ಆದ್ದರಿಂದ ತಿಥಿ ಆರಂಭವಾಗುವ ದಿನ ಮತ್ತು ವ್ರತದ "
            "ದಿನ ಬೇರೆಯಾಗಬಹುದು. ನಿಯಮದ ಪ್ರಕಾರ ತಿಥಿ ಮಧ್ಯಾಹ್ನ ಕಾಲದಲ್ಲಿ ವ್ಯಾಪಿಸಿರುವ ದಿನ ವ್ರತ; ಎರಡೂ ದಿನ ವ್ಯಾಪಿಸಿದ್ದರೆ "
            "ಮೊದಲ ದಿನ. ಪರಿಶೀಲಿಸಲು ಕೋಷ್ಟಕದಲ್ಲಿ ತಿಥಿಯ ಆರಂಭ ಮತ್ತು ಅಂತ್ಯ ನೀಡಲಾಗಿದೆ."),
        "note.amavasya": (
            "ಅಮಾವಾಸ್ಯೆ ಹಗಲಿನ ಆಚರಣೆ (ಶ್ರಾದ್ಧ-ತರ್ಪಣ ಹಗಲಿನಲ್ಲಿ), ಆದ್ದರಿಂದ ಸೂರ್ಯೋದಯದ ಸಮಯದಲ್ಲಿ ಅಮಾವಾಸ್ಯೆ ತಿಥಿ ಇರುವ ದಿನವೇ "
            "ದಿನಾಂಕ. ತಿಥಿ ಹಿಂದಿನ ಸಂಜೆಯೇ ಆರಂಭವಾಗಬಹುದು. ದೀಪಾವಳಿ (ಪ್ರದೋಷ) ಮತ್ತು ಸರ್ವಪಿತೃ ಅಮಾವಾಸ್ಯೆ (ಅಪರಾಹ್ಣ) "
            "ತಮ್ಮದೇ ನಿಯಮ ಅನುಸರಿಸುತ್ತವೆ, ಇಲ್ಲಿನ ದಿನಾಂಕಕ್ಕಿಂತ ಒಂದು ದಿನ ವ್ಯತ್ಯಾಸವಾಗಬಹುದು."),
        "note.pradosh": (
            "ದಿನಾಂಕ ಸಂಜೆಯಿಂದ ನಿರ್ಧಾರವಾಗುತ್ತದೆ, ಸೂರ್ಯೋದಯದಿಂದ ಅಲ್ಲ: ಸೂರ್ಯಾಸ್ತದ ನಂತರ ಪ್ರದೋಷ ಕಾಲದಲ್ಲಿ ತ್ರಯೋದಶಿ ಇರುವ "
            "ದಿನ ವ್ರತ. ಎರಡು ಸಂಜೆ ಪ್ರದೋಷ ಕಾಲವನ್ನು ತಿಥಿ ಮುಟ್ಟಿದರೆ ಮೊದಲ ಸಂಜೆ. ಕೋಷ್ಟಕದ ಪೂಜಾ ಸಮಯ ನವದೆಹಲಿಯ "
            "ಸೂರ್ಯಾಸ್ತದಿಂದ ಆರಂಭ; ಇದು ವರ್ಷದುದ್ದಕ್ಕೂ ಮತ್ತು ನಗರದಿಂದ ನಗರಕ್ಕೆ ಬದಲಾಗುತ್ತದೆ."),
        "note.sankashti": (
            "ಸಂಕಷ್ಟಹರ ಚತುರ್ಥಿ ಚಂದ್ರನಿಂದ ನಿರ್ಧಾರ, ಸೂರ್ಯನಿಂದ ಅಲ್ಲ: ಚಂದ್ರೋದಯದ ಸಮಯದಲ್ಲಿ ಚತುರ್ಥಿ ಇರುವ ಸಂಜೆ ವ್ರತ, "
            "ಏಕೆಂದರೆ ಆಗಲೇ ಉಪವಾಸ ಬಿಡುತ್ತಾರೆ. ಚಂದ್ರೋದಯ ಪ್ರತಿದಿನ ಸುಮಾರು 50 ನಿಮಿಷ ತಡವಾಗುತ್ತದೆ ಮತ್ತು ನಗರಗಳ ನಡುವೆ "
            "ಕೆಲವು ನಿಮಿಷ ವ್ಯತ್ಯಾಸ ಇರುತ್ತದೆ; ನಿಮ್ಮ ನಗರದ ಸಮಯ ನೋಡಿ."),
        "note.masik_shivratri": (
            "ಇದು ಮಧ್ಯರಾತ್ರಿಯ ಆಚರಣೆ; ನಿಶೀಥ ಕಾಲದಲ್ಲಿ (ರಾತ್ರಿಯ 15 ಮುಹೂರ್ತಗಳಲ್ಲಿ 8ನೇದು) ಚತುರ್ದಶಿ ಇರುವ ದಿನವೇ ದಿನಾಂಕ. "
            "ನಿಶೀಥ 12 ಗಂಟೆಯ ನಂತರ ಬಂದರೆ ಪೂಜೆ ಮರುದಿನದ ಬೆಳಗಿನ ಜಾವದಲ್ಲಿ ನಡೆಯುತ್ತದೆ; ತೋರಿಸಿದ ಸಮಯದೊಂದಿಗೆ ಆ ದಿನಾಂಕ "
            "ಇರುತ್ತದೆ. ಎರಡು ರಾತ್ರಿ ನಿಶೀಥ ಮುಟ್ಟಿದರೆ ಮೊದಲ ರಾತ್ರಿ."),
        "note.kalashtami": (
            "ಕಾಲಾಷ್ಟಮಿ ರಾತ್ರಿಯ ಪೂಜೆ; ಪ್ರದೋಷ ಕಾಲದಲ್ಲಿ (ಸೂರ್ಯಾಸ್ತದ ನಂತರ) ಅಷ್ಟಮಿ ಇರುವ ದಿನವೇ ದಿನಾಂಕ. ತಿಥಿ ಹಿಂದಿನ ಬೆಳಗ್ಗೆ "
            "ಆರಂಭವಾಗಬಹುದು ಅಥವಾ ರಾತ್ರಿಯಲ್ಲಿ ಮುಗಿಯಬಹುದು; ಕೋಷ್ಟಕದಲ್ಲಿ ಆರಂಭ ಮತ್ತು ಅಂತ್ಯ ನೋಡಿ. ಎರಡು ಸಂಜೆ ಮುಟ್ಟಿದರೆ "
            "ಮೊದಲ ಸಂಜೆ."),
        "faq.all_q": "{year}ರಲ್ಲಿ {name} ದಿನಾಂಕಗಳು ಯಾವುವು?",
        "faq.all_a": "{year}ರಲ್ಲಿ {name}: {count} ದಿನಾಂಕಗಳಿವೆ (ನವದೆಹಲಿ): {dates}.",
        "faq.next_q": "ಮುಂದಿನ {name} ಯಾವಾಗ?",
        "faq.first_q": "{year}ರ ಮೊದಲ {name} ಯಾವಾಗ?",
        "faq.on_a": "{name} {when} ರಂದು ({details}).",
        "faq.key_q": "{name} {short} ರಂದು {label} ಯಾವಾಗ?",
        "faq.tithi_q": "{name} {short} ರಂದು ತಿಥಿ ಎಷ್ಟು ಗಂಟೆಗೆ ಆರಂಭ ಮತ್ತು ಅಂತ್ಯ?",
        "faq.why_q": "{name} ದಿನಾಂಕ ಹೇಗೆ ನಿರ್ಧಾರವಾಗುತ್ತದೆ?",
        "faq.why_a": "ದಿನಾಂಕ ಈ ನಿಯಮದಂತೆ: {rule}. {year}ರಲ್ಲಿ ಇದರಿಂದ {count} ದಿನಾಂಕಗಳು (ನವದೆಹಲಿ).",
    },
    "te": {
        "what.purnima": "పౌర్ణమి తేదీలు, తిథి సమయం",
        "what.amavasya": "అమావాస్య తేదీలు, తిథి సమయం",
        "what.pradosh": "అన్ని తేదీలు, ప్రదోష పూజా సమయం",
        "what.sankashti": "అన్ని తేదీలు, చంద్రోదయ సమయం",
        "what.masik_shivratri": "అన్ని తేదీలు, నిశీథ పూజా సమయం",
        "what.kalashtami": "అన్ని తేదీలు, కాలభైరవ పూజ",
        "title": "{name} {year}: {what} (న్యూఢిల్లీ)",
        "h1": "{name} {year}: {what}",
        "desc": ("{year}లో {name} అన్ని {count} తేదీలు - వారం, హిందూ మాసం, తిథి ప్రారంభం, ముగింపు "
                 "(న్యూఢిల్లీ). {about}{keytime}{next}"),
        "desc.about.purnima": "సత్యనారాయణ పూజ, స్నానం, దానం చేసే పౌర్ణమి వ్రతం.",
        "desc.about.amavasya": "శ్రాద్ధ-తర్పణాల అమావాస్య, సోమవతి, శని అమావాస్యలతో సహా.",
        "desc.about.pradosh": "త్రయోదశినాడు శివుని ప్రదోష వ్రతం, పూజా సమయం.",
        "desc.about.sankashti": "కృష్ణ చతుర్థినాడు గణపతి వ్రతం, చంద్రోదయం తర్వాత విరమణ.",
        "desc.about.masik_shivratri": "కృష్ణ చతుర్దశి మాస శివరాత్రి, నిశీథ కాల పూజ.",
        "desc.about.kalashtami": "ప్రతి నెలా కృష్ణ అష్టమినాడు కాలభైరవ పూజ.",
        "desc.key": " అలాగే {label}.",
        "desc.next": " తదుపరిది: {date}.",
        "ans.next": "తదుపరి {name} <strong>{when}</strong> న ({details}).",
        "ans.first": ("{year}లో మొదటి {name} <strong>{when}</strong> న ({details}). "
                      "{year} అన్ని {count} తేదీలు కింద ఉన్నాయి."),
        "ans.past": ("{year} అన్ని {count} {name} తేదీలు కింద ఉన్నాయి; చివరిది "
                     "<strong>{when}</strong> న."),
        "ans.more": " {year} తేదీలు: {link}.",
        "table.h2": "{name} {year}: అన్ని తేదీలు",
        "th.date": "తేదీ",
        "th.month": "హిందూ మాసం",
        "th.tithi": "తిథి",
        "adhika": "అధిక {month}",
        "also": "అలాగే: ",
        "months.note": ('<p class="note"><small>మాసాలు అమాంత పద్ధతి (మాసం అమావాస్యతో ముగుస్తుంది; దక్షిణ, పశ్చిమ '
                        "భారతంలో ఇలా). ఉత్తర భారత పూర్ణిమాంత పంచాంగంలో కృష్ణ పక్షానికి ఒక నెల తర్వాతి పేరు ఉంటుంది."
                        "</small></p>"),
        "variant.pradosh.0": "సోమ ప్రదోషం",
        "variant.pradosh.1": "భౌమ ప్రదోషం",
        "variant.pradosh.5": "శని ప్రదోషం",
        "variant.sankashti.1": "అంగారక చతుర్థి",
        "variant.amavasya.0": "సోమవతి అమావాస్య",
        "variant.amavasya.5": "శని అమావాస్య",
        "about.h2": "{name} అంటే ఏమిటి, ఎలా జరుపుకుంటారు",
        "city.h2": "మీ నగర పంచాంగం",
        "related.h2": "సంబంధిత తేదీలు, క్యాలెండర్లు",
        "crumb.page": "{name} {year}",
        "about.purnima": (
            "<p>పౌర్ణమి శుక్ల పక్షంలో చివరి (15వ) తిథి; అప్పుడు చంద్రుడు సూర్యునికి ఎదురుగా పూర్తిగా ప్రకాశిస్తాడు. "
            "భక్తులు ఉపవాసం ఉండి, ఉదయం స్నానం చేసి, విష్ణువును పూజిస్తారు - సత్యనారాయణ కథ పౌర్ణమి సాధారణ పూజ - "
            "సాయంత్రం చంద్రునికి అర్ఘ్యం ఇస్తారు. ఈ రోజు చేసే దానానికి అధిక పుణ్యం అని నమ్మకం.</p>"
            "<p>గురు పౌర్ణమి, శరద్ పౌర్ణమి, కార్తీక పౌర్ణమి, బుద్ధ పౌర్ణమి స్వతంత్ర పండుగలు; హోలికా దహనం ఫాల్గుణ "
            "పౌర్ణమినాడు జరుగుతుంది.</p>"),
        "about.amavasya": (
            "<p>అమావాస్య కృష్ణ పక్షంలో 30వ, చివరి తిథి; అప్పుడు చంద్రుడు సూర్యునితో కలిసి ఉండి కనిపించడు. ఇది పితృదేవతల "
            "రోజు: తర్పణం, శ్రాద్ధం చేస్తారు, బ్రాహ్మణులకు, పేదలకు భోజనం పెడతారు, దానం చేస్తారు, పవిత్ర జలంలో స్నానం "
            "చేస్తారు.</p><p>సోమవారం అమావాస్య సోమవతి అమావాస్య, శనివారం అమావాస్య శని అమావాస్య. మౌని అమావాస్య, సర్వ "
            "పితృ అమావాస్య, దీపావళి అమావాస్య ముఖ్యమైనవి.</p>"),
        "about.pradosh": (
            "<p>ప్రదోష వ్రతం రెండు పక్షాల త్రయోదశి (13వ తిథి) నాడు చేసే శివ వ్రతం - నెలకు రెండుసార్లు. ప్రదోష కాలం "
            "సూర్యాస్తమయం తర్వాతి సంధ్యా సమయం. భక్తులు పగలు ఉపవాసం ఉండి, ప్రదోష కాలంలో శివ పూజ చేస్తారు: నీరు, పాలు, "
            "బిల్వ పత్రాలతో అభిషేకం, దీపం. పూజ తర్వాత ఉపవాసం విరమిస్తారు.</p><p>సోమవారం ప్రదోషం సోమ ప్రదోషం, మంగళవారం "
            "భౌమ ప్రదోషం, శనివారం శని ప్రదోషం.</p>"),
        "about.sankashti": (
            "<p>సంకష్టహర చతుర్థి కృష్ణ పక్షంలో చతుర్థి (4వ తిథి) నాడు గణపతికి చేసే మాస వ్రతం. భక్తులు పగలు ఉపవాసం ఉండి, "
            "సాయంత్రం గణపతిని పూజించి, చంద్రుడిని చూసి అర్ఘ్యం ఇచ్చిన తర్వాతే ఉపవాసం విరమిస్తారు - అందుకే ఈ పేజీలో "
            "చంద్రోదయం ముఖ్య సమయం.</p><p>మంగళవారం వచ్చే సంకష్టహర చతుర్థి అంగారక చతుర్థి; అది విశేష ఫలదాయకమని "
            "నమ్మకం.</p>"),
        "about.masik_shivratri": (
            "<p>మాస శివరాత్రి ప్రతి నెలా కృష్ణ పక్షం చతుర్దశి (14వ తిథి) నాడు జరుపుకునే శివుని రాత్రి. భక్తులు ఉపవాసం ఉండి "
            "రాత్రి జాగరణ చేస్తారు, శివలింగానికి నీరు, పాలు, తేనె, బిల్వ పత్రాలతో అభిషేకం చేస్తారు. పూజకు ఉత్తమ సమయం "
            "నిశీథ కాలం, అంటే అర్ధరాత్రి.</p><p>మహా శివరాత్రి పన్నెండింటిలో గొప్పది.</p>"),
        "about.kalashtami": (
            "<p>కాలాష్టమి కృష్ణ పక్షం అష్టమి (8వ తిథి) నాడు జరుపుకునే కాలభైరవుని మాస దినం. భక్తులు ఉపవాసం ఉండి, రాత్రి "
            "ఆవనూనె దీపంతో భైరవుని పూజిస్తారు, కుక్కలకు ఆహారం పెడతారు.</p><p>పూర్ణిమాంత పంచాంగంలో మార్గశిర (అమాంతంలో "
            "కార్తీక) మాసపు కాలాష్టమి కాలభైరవ జయంతి - ఏడాదిలో ముఖ్యమైనది.</p>"),
        "note.purnima": (
            "పౌర్ణమి ఒక సాయంత్రం మొదలై మరుసటి మధ్యాహ్నం వరకు ఉండవచ్చు; అందుకే తిథి మొదలయ్యే రోజు, వ్రతం రోజు వేరు కావచ్చు. "
            "నియమం ప్రకారం తిథి మధ్యాహ్న కాలంలో ఉన్న రోజు వ్రతం; రెండు రోజులూ ఉంటే మొదటి రోజు. పరిశీలించుకోవడానికి "
            "పట్టికలో తిథి ప్రారంభం, ముగింపు ఇచ్చాం."),
        "note.amavasya": (
            "అమావాస్య పగటి కార్యక్రమం (శ్రాద్ధ తర్పణాలు పగలు చేస్తారు), కాబట్టి సూర్యోదయ సమయంలో అమావాస్య తిథి ఉన్న రోజే తేదీ. "
            "తిథి ముందు రోజు సాయంత్రమే మొదలు కావచ్చు. దీపావళి (ప్రదోషం), సర్వ పితృ అమావాస్య (అపరాహ్ణం) తమ నియమాలను "
            "అనుసరిస్తాయి; ఇక్కడి తేదీకి ఒక రోజు తేడా ఉండవచ్చు."),
        "note.pradosh": (
            "తేదీ సాయంత్రం ఆధారంగా నిర్ణయమవుతుంది, సూర్యోదయం కాదు: సూర్యాస్తమయం తర్వాత ప్రదోష కాలంలో త్రయోదశి ఉన్న రోజు "
            "వ్రతం. రెండు సాయంత్రాలు ప్రదోష కాలాన్ని తిథి తాకితే మొదటి సాయంత్రం. పట్టికలోని పూజా సమయం న్యూఢిల్లీ "
            "సూర్యాస్తమయంతో మొదలవుతుంది; ఇది ఏడాది పొడవునా, నగరాన్ని బట్టి మారుతుంది."),
        "note.sankashti": (
            "సంకష్టహర చతుర్థి చంద్రుని బట్టి నిర్ణయమవుతుంది, సూర్యుని బట్టి కాదు: చంద్రోదయ సమయంలో చతుర్థి ఉన్న సాయంత్రం "
            "వ్రతం, ఎందుకంటే అప్పుడే ఉపవాసం విరమిస్తారు. చంద్రోదయం రోజుకు సుమారు 50 నిమిషాలు ఆలస్యమవుతుంది, నగరాల "
            "మధ్య కొన్ని నిమిషాల తేడా ఉంటుంది; మీ నగర సమయం చూడండి."),
        "note.masik_shivratri": (
            "ఇది అర్ధరాత్రి ఆచారం; నిశీథ కాలంలో (రాత్రి 15 ముహూర్తాల్లో 8వది) చతుర్దశి ఉన్న రోజే తేదీ. నిశీథం 12 తర్వాత "
            "వస్తే పూజ మరుసటి తేదీ తెల్లవారుజామున జరుగుతుంది; చూపిన సమయంతో ఆ తేదీ ఉంటుంది. రెండు రాత్రులు నిశీథాన్ని "
            "తాకితే మొదటి రాత్రి."),
        "note.kalashtami": (
            "కాలాష్టమి రాత్రి పూజ; ప్రదోష కాలంలో (సూర్యాస్తమయం తర్వాత) అష్టమి ఉన్న రోజే తేదీ. తిథి ముందు రోజు ఉదయం మొదలై "
            "లేదా రాత్రిలో ముగియవచ్చు; పట్టికలో ప్రారంభం, ముగింపు చూడండి. రెండు సాయంత్రాలు తాకితే మొదటి సాయంత్రం."),
        "faq.all_q": "{year}లో {name} తేదీలు ఏవి?",
        "faq.all_a": "{year}లో {name} {count} తేదీలు ఉన్నాయి (న్యూఢిల్లీ): {dates}.",
        "faq.next_q": "తదుపరి {name} ఎప్పుడు?",
        "faq.first_q": "{year}లో మొదటి {name} ఎప్పుడు?",
        "faq.on_a": "{name} {when} న ({details}).",
        "faq.key_q": "{name} {short} న {label} ఎప్పుడు?",
        "faq.tithi_q": "{name} {short} న తిథి ఏ సమయానికి మొదలై ముగుస్తుంది?",
        "faq.why_q": "{name} తేదీ ఎలా నిర్ణయిస్తారు?",
        "faq.why_a": "తేదీ ఈ నియమం ప్రకారం: {rule}. {year}లో దీని ప్రకారం {count} తేదీలు (న్యూఢిల్లీ).",
    },
    "ta": {
        "what.purnima": "பௌர்ணமி தேதிகள், திதி நேரம்",
        "what.amavasya": "அமாவாசை தேதிகள், திதி நேரம்",
        "what.pradosh": "அனைத்து தேதிகள், பிரதோஷ பூஜை நேரம்",
        "what.sankashti": "அனைத்து தேதிகள், சந்திர உதய நேரம்",
        "what.masik_shivratri": "அனைத்து தேதிகள், நிசீத கால பூஜை நேரம்",
        "what.kalashtami": "அனைத்து தேதிகள், கால பைரவ பூஜை",
        "title": "{name} {year}: {what} (புது தில்லி)",
        "h1": "{name} {year}: {what}",
        "desc": ("{year} ஆண்டின் {name} அனைத்து {count} தேதிகள் - கிழமை, இந்து மாதம், திதி தொடக்கம், முடிவு "
                 "(புது தில்லி). {about}{keytime}{next}"),
        "desc.about.purnima": "சத்தியநாராயண பூஜை, நீராடல், தானம் செய்யும் பௌர்ணமி விரதம்.",
        "desc.about.amavasya": "சிராத்தம்-தர்ப்பணம் செய்யும் அமாவாசை; சோமவதி, சனி அமாவாசை உட்பட.",
        "desc.about.pradosh": "திரயோதசியில் சிவனுக்கான பிரதோஷ விரதம், பூஜை நேரம்.",
        "desc.about.sankashti": "தேய்பிறை சதுர்த்தியில் விநாயகர் விரதம், சந்திர உதயத்துக்குப் பின் நிறைவு.",
        "desc.about.masik_shivratri": "தேய்பிறை சதுர்தசியின் மாத சிவராத்திரி, நிசீத கால பூஜை.",
        "desc.about.kalashtami": "ஒவ்வொரு மாதமும் தேய்பிறை அஷ்டமியில் கால பைரவ வழிபாடு.",
        "desc.key": " கூடுதலாக {label}.",
        "desc.next": " அடுத்தது: {date}.",
        "ans.next": "அடுத்த {name} <strong>{when}</strong> அன்று ({details}).",
        "ans.first": ("{year} ஆண்டின் முதல் {name} <strong>{when}</strong> அன்று ({details}). "
                      "{year} ஆண்டின் அனைத்து {count} தேதிகளும் கீழே உள்ளன."),
        "ans.past": ("{year} ஆண்டின் அனைத்து {count} {name} தேதிகளும் கீழே உள்ளன; கடைசியானது "
                     "<strong>{when}</strong> அன்று."),
        "ans.more": " {year} தேதிகள்: {link}.",
        "table.h2": "{name} {year}: அனைத்து தேதிகள்",
        "th.date": "தேதி",
        "th.month": "இந்து மாதம்",
        "th.tithi": "திதி",
        "adhika": "அதிக {month}",
        "also": "மேலும்: ",
        "months.note": ('<p class="note"><small>மாதங்கள் அமாந்த முறையில் (மாதம் அமாவாசையுடன் முடியும்; தென், மேற்கு '
                        "இந்தியாவில் இவ்வாறு). வட இந்திய பூர்ணிமாந்த பஞ்சாங்கத்தில் தேய்பிறைக்கு ஒரு மாதம் பிந்தைய பெயர் "
                        "இருக்கும்.</small></p>"),
        "variant.pradosh.0": "சோம பிரதோஷம்",
        "variant.pradosh.1": "பௌம பிரதோஷம்",
        "variant.pradosh.5": "சனி பிரதோஷம்",
        "variant.sankashti.1": "அங்காரக சதுர்த்தி",
        "variant.amavasya.0": "சோமவதி அமாவாசை",
        "variant.amavasya.5": "சனி அமாவாசை",
        "about.h2": "{name} என்றால் என்ன, எப்படி அனுசரிக்கிறார்கள்",
        "city.h2": "உங்கள் ஊரின் பஞ்சாங்கம்",
        "related.h2": "தொடர்புடைய தேதிகள், நாட்காட்டிகள்",
        "crumb.page": "{name} {year}",
        "about.purnima": (
            "<p>பௌர்ணமி வளர்பிறையின் கடைசி (15-ஆம்) திதி; அப்போது சந்திரன் சூரியனுக்கு எதிரே முழுமையாக ஒளிரும். "
            "பக்தர்கள் விரதம் இருந்து, காலையில் நீராடி, விஷ்ணுவை வழிபடுவர் - சத்தியநாராயண கதை பௌர்ணமியின் வழக்கமான "
            "பூஜை - மாலையில் சந்திரனுக்கு அர்க்யம் தருவர். இந்நாளில் செய்யும் தானத்துக்குப் பன்மடங்கு புண்ணியம் என்பர்.</p>"
            "<p>குரு பௌர்ணமி, சரத் பௌர்ணமி, கார்த்திகை பௌர்ணமி, புத்த பௌர்ணமி தனிப் பண்டிகைகள்; ஹோலிகா தகனம் "
            "பங்குனி பௌர்ணமியில் நடக்கும்.</p>"),
        "about.amavasya": (
            "<p>அமாவாசை தேய்பிறையின் 30-ஆம், கடைசி திதி; அப்போது சந்திரன் சூரியனுடன் சேர்ந்து தெரியாது. இது முன்னோர் "
            "நாள்: தர்ப்பணம், சிராத்தம் செய்வர், அந்தணர்களுக்கும் ஏழைகளுக்கும் உணவளிப்பர், தானம் செய்வர், புனித நீரில் "
            "நீராடுவர்.</p><p>திங்கள் அமாவாசை சோமவதி அமாவாசை, சனிக்கிழமை அமாவாசை சனி அமாவாசை. மௌனி அமாவாசை, "
            "மகாளய (சர்வ பித்ரு) அமாவாசை, தீபாவளி அமாவாசை முக்கியமானவை.</p>"),
        "about.pradosh": (
            "<p>பிரதோஷ விரதம் இரு பட்சங்களின் திரயோதசி (13-ஆம் திதி) அன்று சிவனுக்கு இருக்கும் விரதம் - மாதம் இருமுறை. "
            "பிரதோஷ காலம் சூரிய அஸ்தமனத்துக்குப் பின் வரும் மாலை நேரம். பக்தர்கள் பகலில் விரதம் இருந்து, பிரதோஷ காலத்தில் "
            "சிவபூஜை செய்வர்: நீர், பால், வில்வ இலைகளால் அபிஷேகம், தீபம். பூஜைக்குப் பின் விரதம் முடிப்பர்.</p>"
            "<p>திங்கள் பிரதோஷம் சோம பிரதோஷம், செவ்வாய் பௌம பிரதோஷம், சனிக்கிழமை சனி பிரதோஷம்.</p>"),
        "about.sankashti": (
            "<p>சங்கடஹர சதுர்த்தி தேய்பிறை சதுர்த்தி (4-ஆம் திதி) அன்று விநாயகருக்கு இருக்கும் மாத விரதம். பக்தர்கள் பகலில் "
            "விரதம் இருந்து, மாலையில் விநாயகரை வழிபட்டு, சந்திரனைக் கண்டு அர்க்யம் தந்த பின்பே விரதம் முடிப்பர் - அதனால் "
            "இப்பக்கத்தில் சந்திர உதய நேரமே முக்கியம்.</p><p>செவ்வாய்க்கிழமை வரும் சங்கடஹர சதுர்த்தி அங்காரக சதுர்த்தி; "
            "அது சிறப்புப் பலன் தரும் என்பர்.</p>"),
        "about.masik_shivratri": (
            "<p>மாத சிவராத்திரி ஒவ்வொரு மாதமும் தேய்பிறை சதுர்தசி (14-ஆம் திதி) அன்று அனுசரிக்கும் சிவனின் இரவு. "
            "பக்தர்கள் விரதம் இருந்து இரவு விழித்திருந்து, சிவலிங்கத்துக்கு நீர், பால், தேன், வில்வ இலைகளால் அபிஷேகம் "
            "செய்வர். பூஜைக்கு உகந்த நேரம் நிசீத காலம், அதாவது நள்ளிரவு.</p><p>மகா சிவராத்திரி பன்னிரண்டில் பெரியது.</p>"),
        "about.kalashtami": (
            "<p>காலாஷ்டமி தேய்பிறை அஷ்டமி (8-ஆம் திதி) அன்று அனுசரிக்கும் கால பைரவரின் மாத நாள். பக்தர்கள் விரதம் இருந்து, "
            "இரவில் கடுகு எண்ணெய் தீபத்துடன் பைரவரை வழிபடுவர், நாய்களுக்கு உணவளிப்பர்.</p><p>பூர்ணிமாந்த பஞ்சாங்கத்தில் "
            "மார்கழி (அமாந்தத்தில் கார்த்திகை) மாத காலாஷ்டமி கால பைரவ ஜெயந்தி - ஆண்டின் முக்கியமானது.</p>"),
        "note.purnima": (
            "பௌர்ணமி ஒரு மாலையில் தொடங்கி மறுநாள் மதியம் வரை இருக்கலாம்; எனவே திதி தொடங்கும் நாளும் விரத நாளும் "
            "வேறுபடலாம். விதிப்படி திதி மத்தியான காலத்தில் இருக்கும் நாளே விரதம்; இரு நாளும் இருந்தால் முதல் நாள். "
            "சரிபார்க்க அட்டவணையில் திதியின் தொடக்கமும் முடிவும் தரப்பட்டுள்ளன."),
        "note.amavasya": (
            "அமாவாசை பகல் நேர அனுசரிப்பு (சிராத்தம், தர்ப்பணம் பகலில்), எனவே சூரிய உதயத்தில் அமாவாசை திதி இருக்கும் நாளே "
            "தேதி. திதி முந்தைய மாலையே தொடங்கலாம். தீபாவளி (பிரதோஷம்), சர்வ பித்ரு அமாவாசை (அபராஹ்ணம்) தங்கள் "
            "விதிகளைப் பின்பற்றுவதால் இங்குள்ள தேதியிலிருந்து ஒரு நாள் மாறலாம்."),
        "note.pradosh": (
            "தேதி மாலையைக் கொண்டு முடிவாகும், சூரிய உதயத்தை அல்ல: சூரிய அஸ்தமனத்துக்குப் பின் பிரதோஷ காலத்தில் திரயோதசி "
            "இருக்கும் நாளே விரதம். இரு மாலைகளிலும் திதி பிரதோஷ காலத்தைத் தொட்டால் முதல் மாலை. அட்டவணையில் பூஜை நேரம் "
            "புது தில்லியின் சூரிய அஸ்தமனத்தில் தொடங்கும்; அது ஆண்டு முழுவதும், ஊருக்கு ஊர் மாறும்."),
        "note.sankashti": (
            "சங்கடஹர சதுர்த்தி சந்திரனைக் கொண்டு முடிவாகும், சூரியனை அல்ல: சந்திர உதயத்தில் சதுர்த்தி இருக்கும் மாலையே "
            "விரதம், ஏனெனில் அப்போதுதான் விரதம் முடிக்கப்படும். சந்திர உதயம் நாளுக்கு சுமார் 50 நிமிடம் தாமதமாகும்; "
            "ஊர்களுக்கிடையே சில நிமிட வேறுபாடு இருக்கும்; உங்கள் ஊரின் நேரத்தைப் பாருங்கள்."),
        "note.masik_shivratri": (
            "இது நள்ளிரவு அனுசரிப்பு; நிசீத காலத்தில் (இரவின் 15 முகூர்த்தங்களில் 8-ஆவது) சதுர்தசி இருக்கும் நாளே தேதி. "
            "நிசீதம் 12 மணிக்குப் பின் வந்தால் பூஜை மறுநாள் அதிகாலையில் நடக்கும்; காட்டப்படும் நேரத்துடன் அந்தத் தேதியும் "
            "இருக்கும். இரு இரவுகளில் திதி நிசீதத்தைத் தொட்டால் முதல் இரவு."),
        "note.kalashtami": (
            "காலாஷ்டமி இரவு வழிபாடு; பிரதோஷ காலத்தில் (சூரிய அஸ்தமனத்துக்குப் பின்) அஷ்டமி இருக்கும் நாளே தேதி. திதி முந்தைய "
            "காலையில் தொடங்கலாம் அல்லது இரவில் முடியலாம்; அட்டவணையில் தொடக்கம், முடிவு பாருங்கள். இரு மாலைகளைத் "
            "தொட்டால் முதல் மாலை."),
        "faq.all_q": "{year} ஆண்டில் {name} தேதிகள் எவை?",
        "faq.all_a": "{year} ஆண்டில் {name} {count} தேதிகள் உள்ளன (புது தில்லி): {dates}.",
        "faq.next_q": "அடுத்த {name} எப்போது?",
        "faq.first_q": "{year} ஆண்டின் முதல் {name} எப்போது?",
        "faq.on_a": "{name} {when} அன்று ({details}).",
        "faq.key_q": "{name} {short} அன்று {label} எப்போது?",
        "faq.tithi_q": "{name} {short} அன்று திதி எத்தனை மணிக்குத் தொடங்கி முடிகிறது?",
        "faq.why_q": "{name} தேதி எப்படி முடிவு செய்யப்படுகிறது?",
        "faq.why_a": "தேதி இந்த விதிப்படி: {rule}. {year} ஆண்டில் இதன்படி {count} தேதிகள் (புது தில்லி).",
    },
    "ml": {
        "what.purnima": "പൗർണമി തീയതികളും തിഥി സമയവും",
        "what.amavasya": "അമാവാസി തീയതികളും തിഥി സമയവും",
        "what.pradosh": "എല്ലാ തീയതികളും പ്രദോഷ പൂജാ സമയവും",
        "what.sankashti": "എല്ലാ തീയതികളും ചന്ദ്രോദയ സമയവും",
        "what.masik_shivratri": "എല്ലാ തീയതികളും നിശീഥ പൂജാ സമയവും",
        "what.kalashtami": "എല്ലാ തീയതികളും കാലഭൈരവ പൂജയും",
        "title": "{name} {year}: {what} (ന്യൂഡൽഹി)",
        "h1": "{name} {year}: {what}",
        "desc": ("{year}-ലെ {name}: എല്ലാ {count} തീയതികൾ - ആഴ്ച, ഹിന്ദു മാസം, തിഥി തുടക്കവും അവസാനവും "
                 "(ന്യൂഡൽഹി). {about}{keytime}{next}"),
        "desc.about.purnima": "സത്യനാരായണ പൂജ, സ്നാനം, ദാനം എന്നിവയുള്ള പൗർണമി വ്രതം.",
        "desc.about.amavasya": "ശ്രാദ്ധ-തർപ്പണത്തിന്റെ അമാവാസി; സോമവതി, ശനി അമാവാസി ഉൾപ്പെടെ.",
        "desc.about.pradosh": "ത്രയോദശിയിൽ ശിവന്റെ പ്രദോഷ വ്രതവും പൂജാ സമയവും.",
        "desc.about.sankashti": "കൃഷ്ണ ചതുർഥിയിൽ ഗണപതിയുടെ വ്രതം, ചന്ദ്രോദയത്തിനു ശേഷം പാരണ.",
        "desc.about.masik_shivratri": "കൃഷ്ണ ചതുർദശിയിലെ മാസ ശിവരാത്രിയും നിശീഥ കാല പൂജയും.",
        "desc.about.kalashtami": "എല്ലാ മാസവും കൃഷ്ണ അഷ്ടമിയിൽ കാലഭൈരവ പൂജ.",
        "desc.key": " കൂടാതെ {label}.",
        "desc.next": " അടുത്തത്: {date}.",
        "ans.next": "അടുത്ത {name} <strong>{when}</strong> ({details}).",
        "ans.first": ("{year}-ലെ ആദ്യ {name} <strong>{when}</strong> ({details}). "
                      "{year}-ലെ എല്ലാ {count} തീയതികളും താഴെ."),
        "ans.past": ("{year}-ലെ എല്ലാ {count} {name} തീയതികളും താഴെ; അവസാനത്തേത് "
                     "<strong>{when}</strong> ആയിരുന്നു."),
        "ans.more": " {year}-ലെ തീയതികൾ: {link}.",
        "table.h2": "{name} {year}: എല്ലാ തീയതികളും",
        "th.date": "തീയതി",
        "th.month": "ഹിന്ദു മാസം",
        "th.tithi": "തിഥി",
        "adhika": "അധിക {month}",
        "also": "കൂടാതെ: ",
        "months.note": ('<p class="note"><small>മാസങ്ങൾ അമാന്ത രീതിയിൽ (മാസം അമാവാസിയിൽ അവസാനിക്കും; ദക്ഷിണ, പശ്ചിമ '
                        "ഇന്ത്യയിൽ ഇങ്ങനെ). ഉത്തരേന്ത്യൻ പൂർണിമാന്ത പഞ്ചാംഗത്തിൽ കൃഷ്ണ പക്ഷത്തിന് ഒരു മാസം കഴിഞ്ഞുള്ള പേരാണ്."
                        "</small></p>"),
        "variant.pradosh.0": "സോമ പ്രദോഷം",
        "variant.pradosh.1": "ഭൗമ പ്രദോഷം",
        "variant.pradosh.5": "ശനി പ്രദോഷം",
        "variant.sankashti.1": "അംഗാരക ചതുർഥി",
        "variant.amavasya.0": "സോമവതി അമാവാസി",
        "variant.amavasya.5": "ശനി അമാവാസി",
        "about.h2": "{name} എന്താണ്, എങ്ങനെ ആചരിക്കുന്നു",
        "city.h2": "നിങ്ങളുടെ നഗരത്തിലെ പഞ്ചാംഗം",
        "related.h2": "ബന്ധപ്പെട്ട തീയതികളും കലണ്ടറുകളും",
        "crumb.page": "{name} {year}",
        "about.purnima": (
            "<p>പൗർണമി ശുക്ല പക്ഷത്തിലെ അവസാന (15-ാം) തിഥിയാണ്; അപ്പോൾ ചന്ദ്രൻ സൂര്യന് എതിർവശത്ത് പൂർണമായി "
            "തിളങ്ങുന്നു. ഭക്തർ വ്രതമെടുത്ത് രാവിലെ സ്നാനം ചെയ്ത് വിഷ്ണുവിനെ ആരാധിക്കുന്നു - സത്യനാരായണ കഥ "
            "പൗർണമിയിലെ പതിവ് പൂജയാണ് - വൈകുന്നേരം ചന്ദ്രന് അർഘ്യം നൽകുന്നു. ഈ ദിവസത്തെ ദാനത്തിന് ഇരട്ടി പുണ്യം "
            "എന്നാണ് വിശ്വാസം.</p><p>ഗുരു പൂർണിമ, ശരദ് പൂർണിമ, കാർത്തിക പൂർണിമ, ബുദ്ധ പൂർണിമ എന്നിവ സ്വന്തം "
            "ആഘോഷങ്ങളാണ്; ഹോളികാ ദഹനം ഫാൽഗുന പൗർണമിയിലാണ്.</p>"),
        "about.amavasya": (
            "<p>അമാവാസി കൃഷ്ണ പക്ഷത്തിലെ 30-ാമത്തെയും അവസാനത്തെയും തിഥിയാണ്; അപ്പോൾ ചന്ദ്രൻ സൂര്യനോടൊപ്പമായി "
            "കാണാനാവില്ല. ഇത് പിതൃക്കളുടെ ദിവസം: തർപ്പണവും ശ്രാദ്ധവും ചെയ്യുന്നു, ബ്രാഹ്മണർക്കും ദരിദ്രർക്കും ഭക്ഷണം "
            "നൽകുന്നു, ദാനം ചെയ്യുന്നു, പുണ്യജലത്തിൽ സ്നാനം ചെയ്യുന്നു.</p><p>തിങ്കളാഴ്ചയിലെ അമാവാസി സോമവതി "
            "അമാവാസി, ശനിയാഴ്ചയിലേത് ശനി അമാവാസി. മൗനി അമാവാസി, സർവ പിതൃ അമാവാസി, ദീപാവലി അമാവാസി "
            "പ്രധാനപ്പെട്ടവയാണ്.</p>"),
        "about.pradosh": (
            "<p>പ്രദോഷ വ്രതം രണ്ടു പക്ഷങ്ങളിലെയും ത്രയോദശി (13-ാം തിഥി) നാളിൽ ശിവനുവേണ്ടി എടുക്കുന്ന വ്രതമാണ് - മാസത്തിൽ "
            "രണ്ടു തവണ. പ്രദോഷ കാലം സൂര്യാസ്തമയത്തിനു ശേഷമുള്ള സന്ധ്യാ സമയമാണ്. ഭക്തർ പകൽ വ്രതമെടുത്ത് പ്രദോഷ "
            "കാലത്ത് ശിവപൂജ ചെയ്യുന്നു: വെള്ളം, പാൽ, കൂവളത്തില എന്നിവ കൊണ്ട് അഭിഷേകം, ദീപം. പൂജയ്ക്കു ശേഷം വ്രതം "
            "മുറിക്കുന്നു.</p><p>തിങ്കളാഴ്ചയിലെ പ്രദോഷം സോമ പ്രദോഷം, ചൊവ്വാഴ്ചയിലേത് ഭൗമ പ്രദോഷം, ശനിയാഴ്ചയിലേത് "
            "ശനി പ്രദോഷം.</p>"),
        "about.sankashti": (
            "<p>സങ്കഷ്ടഹര ചതുർഥി കൃഷ്ണ പക്ഷത്തിലെ ചതുർഥി (4-ാം തിഥി) നാളിൽ ഗണപതിക്കായി എടുക്കുന്ന മാസ വ്രതമാണ്. "
            "ഭക്തർ പകൽ വ്രതമെടുത്ത്, വൈകുന്നേരം ഗണപതിയെ ആരാധിച്ച്, ചന്ദ്രനെ കണ്ട് അർഘ്യം നൽകിയ ശേഷം മാത്രം വ്രതം "
            "മുറിക്കുന്നു - അതിനാൽ ഈ പേജിൽ ചന്ദ്രോദയമാണ് പ്രധാന സമയം.</p><p>ചൊവ്വാഴ്ച വരുന്ന സങ്കഷ്ടഹര ചതുർഥി "
            "അംഗാരക ചതുർഥി; അത് പ്രത്യേക ഫലദായകം എന്നാണ് വിശ്വാസം.</p>"),
        "about.masik_shivratri": (
            "<p>മാസ ശിവരാത്രി എല്ലാ മാസവും കൃഷ്ണ പക്ഷത്തിലെ ചതുർദശി (14-ാം തിഥി) നാളിൽ ആചരിക്കുന്ന ശിവന്റെ രാത്രിയാണ്. "
            "ഭക്തർ വ്രതമെടുത്ത് രാത്രി ഉറക്കമൊഴിഞ്ഞ് ശിവലിംഗത്തിന് വെള്ളം, പാൽ, തേൻ, കൂവളത്തില എന്നിവ കൊണ്ട് "
            "അഭിഷേകം ചെയ്യുന്നു. പൂജയ്ക്ക് ഏറ്റവും നല്ല സമയം നിശീഥ കാലം, അതായത് അർധരാത്രിയാണ്.</p>"
            "<p>മഹാശിവരാത്രി പന്ത്രണ്ടിൽ ഏറ്റവും വലുതാണ്.</p>"),
        "about.kalashtami": (
            "<p>കാലാഷ്ടമി കൃഷ്ണ പക്ഷത്തിലെ അഷ്ടമി (8-ാം തിഥി) നാളിൽ ആചരിക്കുന്ന കാലഭൈരവന്റെ മാസ ദിനമാണ്. ഭക്തർ വ്രതമെടുത്ത്, "
            "രാത്രി കടുകെണ്ണ വിളക്കോടെ ഭൈരവനെ ആരാധിക്കുകയും നായ്ക്കൾക്ക് ഭക്ഷണം നൽകുകയും ചെയ്യുന്നു.</p>"
            "<p>പൂർണിമാന്ത പഞ്ചാംഗത്തിലെ മാർഗശീർഷ (അമാന്തത്തിൽ കാർത്തിക) മാസത്തിലെ കാലാഷ്ടമി കാലഭൈരവ ജയന്തിയാണ് - "
            "വർഷത്തിലെ പ്രധാനം.</p>"),
        "note.purnima": (
            "പൗർണമി ഒരു വൈകുന്നേരം തുടങ്ങി പിറ്റേന്ന് ഉച്ചവരെ നിൽക്കാം; അതിനാൽ തിഥി തുടങ്ങുന്ന ദിവസവും വ്രത ദിവസവും "
            "വ്യത്യസ്തമാകാം. നിയമപ്രകാരം തിഥി മധ്യാഹ്ന കാലത്ത് ഉള്ള ദിവസമാണ് വ്രതം; രണ്ടു ദിവസവും ഉണ്ടെങ്കിൽ ആദ്യ "
            "ദിവസം. പരിശോധിക്കാൻ പട്ടികയിൽ തിഥിയുടെ തുടക്കവും അവസാനവും നൽകിയിട്ടുണ്ട്."),
        "note.amavasya": (
            "അമാവാസി പകൽ അനുഷ്ഠാനമാണ് (ശ്രാദ്ധവും തർപ്പണവും പകൽ ചെയ്യുന്നു); അതിനാൽ സൂര്യോദയ സമയത്ത് അമാവാസി തിഥി "
            "ഉള്ള ദിവസമാണ് തീയതി. തിഥി തലേന്ന് വൈകുന്നേരം തുടങ്ങാം. ദീപാവലി (പ്രദോഷം), സർവ പിതൃ അമാവാസി (അപരാഹ്നം) "
            "എന്നിവ സ്വന്തം നിയമം പിന്തുടരുന്നതിനാൽ ഇവിടത്തെ തീയതിയിൽ നിന്ന് ഒരു ദിവസം വ്യത്യാസപ്പെടാം."),
        "note.pradosh": (
            "തീയതി വൈകുന്നേരത്തെ ആശ്രയിച്ചാണ്, സൂര്യോദയത്തെ അല്ല: സൂര്യാസ്തമയത്തിനു ശേഷം പ്രദോഷ കാലത്ത് ത്രയോദശി ഉള്ള "
            "ദിവസമാണ് വ്രതം. രണ്ടു വൈകുന്നേരങ്ങളിൽ തിഥി പ്രദോഷ കാലത്തെ തൊട്ടാൽ ആദ്യ വൈകുന്നേരം. പട്ടികയിലെ പൂജാ "
            "സമയം ന്യൂഡൽഹിയിലെ സൂര്യാസ്തമയത്തിൽ തുടങ്ങുന്നു; അത് വർഷം മുഴുവൻ, നഗരത്തിനനുസരിച്ച് മാറും."),
        "note.sankashti": (
            "സങ്കഷ്ടഹര ചതുർഥി ചന്ദ്രനെ ആശ്രയിച്ചാണ്, സൂര്യനെ അല്ല: ചന്ദ്രോദയ സമയത്ത് ചതുർഥി ഉള്ള വൈകുന്നേരമാണ് വ്രതം, "
            "കാരണം അപ്പോഴാണ് വ്രതം മുറിക്കുന്നത്. ചന്ദ്രോദയം ദിവസവും ഏകദേശം 50 മിനിറ്റ് വൈകും; നഗരങ്ങൾ തമ്മിൽ ചില "
            "മിനിറ്റ് വ്യത്യാസമുണ്ട്; നിങ്ങളുടെ നഗരത്തിലെ സമയം നോക്കുക."),
        "note.masik_shivratri": (
            "ഇത് അർധരാത്രി അനുഷ്ഠാനമാണ്; നിശീഥ കാലത്ത് (രാത്രിയിലെ 15 മുഹൂർത്തങ്ങളിൽ എട്ടാമത്തേത്) ചതുർദശി ഉള്ള ദിവസമാണ് "
            "തീയതി. നിശീഥം 12 കഴിഞ്ഞാൽ പൂജ പിറ്റേന്ന് പുലർച്ചെ നടക്കും; കാണിച്ച സമയത്തോടൊപ്പം ആ തീയതിയും ഉണ്ടാകും. രണ്ടു "
            "രാത്രികളിൽ തിഥി നിശീഥത്തെ തൊട്ടാൽ ആദ്യ രാത്രി."),
        "note.kalashtami": (
            "കാലാഷ്ടമി രാത്രി ആരാധനയാണ്; പ്രദോഷ കാലത്ത് (സൂര്യാസ്തമയത്തിനു ശേഷം) അഷ്ടമി ഉള്ള ദിവസമാണ് തീയതി. തിഥി തലേന്ന് "
            "രാവിലെ തുടങ്ങുകയോ രാത്രിയിൽ അവസാനിക്കുകയോ ചെയ്യാം; പട്ടികയിൽ തുടക്കവും അവസാനവും നോക്കുക. രണ്ടു "
            "വൈകുന്നേരങ്ങളിൽ തൊട്ടാൽ ആദ്യ വൈകുന്നേരം."),
        "faq.all_q": "{year}-ൽ {name} തീയതികൾ ഏതൊക്കെ?",
        "faq.all_a": "{year}-ൽ {name}: {count} തീയതികളുണ്ട് (ന്യൂഡൽഹി): {dates}.",
        "faq.next_q": "അടുത്ത {name} എപ്പോൾ?",
        "faq.first_q": "{year}-ലെ ആദ്യ {name} എപ്പോൾ?",
        "faq.on_a": "{name} {when} ({details}).",
        "faq.key_q": "{name} {short}-ന് {label} എപ്പോൾ?",
        "faq.tithi_q": "{name} {short}-ന് തിഥി എപ്പോൾ തുടങ്ങി എപ്പോൾ അവസാനിക്കും?",
        "faq.why_q": "{name} തീയതി എങ്ങനെ നിശ്ചയിക്കുന്നു?",
        "faq.why_a": "തീയതി ഈ നിയമപ്രകാരം: {rule}. {year}-ൽ ഇതനുസരിച്ച് {count} തീയതികൾ (ന്യൂഡൽഹി).",
    },
    "bn": {
        "what.purnima": "পূর্ণিমার তারিখ ও তিথির সময়",
        "what.amavasya": "অমাবস্যার তারিখ ও তিথির সময়",
        "what.pradosh": "সব তারিখ ও প্রদোষ পূজার সময়",
        "what.sankashti": "সব তারিখ ও চন্দ্রোদয়ের সময়",
        "what.masik_shivratri": "সব তারিখ ও নিশীথ পূজার সময়",
        "what.kalashtami": "সব তারিখ ও কালভৈরব পূজা",
        "title": "{name} {year}: {what} (নয়াদিল্লি)",
        "h1": "{name} {year}: {what}",
        "desc": ("{year} সালে {name}: সব {count}টি তারিখ - বার, হিন্দু মাস, তিথির শুরু ও শেষ "
                 "(নয়াদিল্লি)। {about}{keytime}{next}"),
        "desc.about.purnima": "সত্যনারায়ণ পূজা, স্নান ও দানের পূর্ণিমা ব্রত।",
        "desc.about.amavasya": "শ্রাদ্ধ-তর্পণের অমাবস্যা, সোমবতী ও শনি অমাবস্যা সহ।",
        "desc.about.pradosh": "ত্রয়োদশীতে শিবের প্রদোষ ব্রত ও পূজার সময়।",
        "desc.about.sankashti": "কৃষ্ণ চতুর্থীতে গণেশের ব্রত, চন্দ্রোদয়ের পর পারণ।",
        "desc.about.masik_shivratri": "কৃষ্ণ চতুর্দশীর মাসিক শিবরাত্রি ও নিশীথ কালের পূজা।",
        "desc.about.kalashtami": "প্রতি মাসে কৃষ্ণ অষ্টমীতে কালভৈরব পূজা।",
        "desc.key": " সঙ্গে {label}।",
        "desc.next": " পরেরটি: {date}।",
        "ans.next": "পরবর্তী {name} <strong>{when}</strong> ({details})।",
        "ans.first": ("{year} সালের প্রথম {name} <strong>{when}</strong> ({details})। "
                      "{year} সালের সব {count}টি তারিখ নিচে দেওয়া আছে।"),
        "ans.past": ("{year} সালের {name}: সব {count}টি তারিখ নিচে দেওয়া আছে; শেষটি ছিল "
                     "<strong>{when}</strong>।"),
        "ans.more": " {year} সালের তারিখ: {link}।",
        "table.h2": "{name} {year}: সব তারিখ",
        "th.date": "তারিখ",
        "th.month": "হিন্দু মাস",
        "th.tithi": "তিথি",
        "adhika": "অধিক {month}",
        "also": "সঙ্গে: ",
        "months.note": ('<p class="note"><small>মাসগুলি অমান্ত (মাস অমাবস্যায় শেষ হয়, যেমন দক্ষিণ ও পশ্চিম ভারতে)। '
                        "উত্তর ভারতের পূর্ণিমান্ত পঞ্জিকায় কৃষ্ণ পক্ষের নাম এক মাস পরের হয়।</small></p>"),
        "variant.pradosh.0": "সোম প্রদোষ",
        "variant.pradosh.1": "ভৌম প্রদোষ",
        "variant.pradosh.5": "শনি প্রদোষ",
        "variant.sankashti.1": "অঙ্গারকী চতুর্থী",
        "variant.amavasya.0": "সোমবতী অমাবস্যা",
        "variant.amavasya.5": "শনি অমাবস্যা",
        "about.h2": "{name} কী এবং কীভাবে পালিত হয়",
        "city.h2": "আপনার শহরের পঞ্জিকা",
        "related.h2": "সম্পর্কিত তারিখ ও ক্যালেন্ডার",
        "crumb.page": "{name} {year}",
        "about.purnima": (
            "<p>পূর্ণিমা শুক্ল পক্ষের শেষ (১৫তম) তিথি, যখন চাঁদ সূর্যের বিপরীতে পূর্ণ আলোয় থাকে। ভক্তেরা উপবাস করেন, "
            "ভোরে স্নান করেন, বিষ্ণুর পূজা করেন - সত্যনারায়ণ কথা পূর্ণিমার প্রচলিত পূজা - এবং সন্ধ্যায় চাঁদকে অর্ঘ্য "
            "দেন। এই দিনের দান বহুগুণ পুণ্য দেয় বলে বিশ্বাস।</p><p>গুরু পূর্ণিমা, শরৎ পূর্ণিমা, কার্তিক পূর্ণিমা ও "
            "বুদ্ধ পূর্ণিমা নিজেরাই উৎসব; হোলিকা দহন ফাল্গুনের পূর্ণিমায় হয়।</p>"),
        "about.amavasya": (
            "<p>অমাবস্যা কৃষ্ণ পক্ষের ৩০তম ও শেষ তিথি, যখন চাঁদ সূর্যের সঙ্গে থাকে এবং দেখা যায় না। এটি পিতৃপুরুষের "
            "দিন: তর্পণ ও শ্রাদ্ধ করা হয়, ব্রাহ্মণ ও গরিবদের খাওয়ানো হয়, দান করা হয়, পবিত্র জলে স্নান করা হয়।</p>"
            "<p>সোমবারের অমাবস্যা সোমবতী অমাবস্যা, শনিবারের অমাবস্যা শনি অমাবস্যা। মৌনী অমাবস্যা, সর্বপিতৃ অমাবস্যা "
            "(মহালয়া) ও দীপাবলির অমাবস্যা প্রধান।</p>"),
        "about.pradosh": (
            "<p>প্রদোষ ব্রত দুই পক্ষের ত্রয়োদশী (১৩তম তিথি) তিথিতে শিবের ব্রত - মাসে দুবার। প্রদোষ কাল সূর্যাস্তের ঠিক "
            "পরের সন্ধ্যার সময়। ভক্তেরা সারাদিন উপবাস করে প্রদোষ কালে শিবপূজা করেন: জল, দুধ ও বিল্বপত্রে অভিষেক, "
            "প্রদীপ। পূজার পরে উপবাস ভাঙা হয়।</p><p>সোমবারের প্রদোষ সোম প্রদোষ, মঙ্গলবারের ভৌম প্রদোষ, শনিবারের "
            "শনি প্রদোষ।</p>"),
        "about.sankashti": (
            "<p>সংকষ্টী চতুর্থী কৃষ্ণ পক্ষের চতুর্থী (৪র্থ তিথি) তিথিতে গণেশের মাসিক ব্রত। ভক্তেরা সারাদিন উপবাস করে "
            "সন্ধ্যায় গণেশের পূজা করেন এবং চাঁদ দেখে অর্ঘ্য দেওয়ার পরেই উপবাস ভাঙেন - তাই এই পাতায় চন্দ্রোদয়ের সময়ই "
            "মুখ্য।</p><p>মঙ্গলবার পড়লে সংকষ্টী চতুর্থী অঙ্গারকী চতুর্থী, যা বিশেষ ফলদায়ক বলে বিশ্বাস।</p>"),
        "about.masik_shivratri": (
            "<p>মাসিক শিবরাত্রি প্রতি মাসে কৃষ্ণ পক্ষের চতুর্দশী (১৪তম তিথি) তিথিতে পালিত শিবের রাত। ভক্তেরা উপবাস করে "
            "রাত জাগেন, শিবলিঙ্গে জল, দুধ, মধু ও বিল্বপত্রে অভিষেক করেন। পূজার শ্রেষ্ঠ সময় নিশীথ কাল, অর্থাৎ মধ্যরাত।</p>"
            "<p>মহাশিবরাত্রি বারোটির মধ্যে সবচেয়ে বড়।</p>"),
        "about.kalashtami": (
            "<p>কালাষ্টমী কৃষ্ণ পক্ষের অষ্টমী (৮ম তিথি) তিথিতে পালিত কালভৈরবের মাসিক দিন। ভক্তেরা উপবাস করে রাতে "
            "সরষের তেলের প্রদীপ দিয়ে ভৈরবের পূজা করেন এবং কুকুরকে খাওয়ান।</p><p>পূর্ণিমান্ত পঞ্জিকায় মার্গশীর্ষ "
            "(অমান্তে কার্তিক) মাসের কালাষ্টমী কালভৈরব জয়ন্তী - বছরের প্রধান কালাষ্টমী।</p>"),
        "note.purnima": (
            "পূর্ণিমা এক সন্ধ্যায় শুরু হয়ে পরদিন দুপুর পর্যন্ত থাকতে পারে, তাই তিথি শুরুর দিন ও ব্রতের দিন আলাদা হতে "
            "পারে। নিয়ম অনুযায়ী তিথি মধ্যাহ্নে থাকে যে দিন, সেদিন ব্রত; দুদিনই থাকলে প্রথম দিন। যাচাইয়ের জন্য "
            "সারণিতে তিথির শুরু ও শেষ দেওয়া আছে।"),
        "note.amavasya": (
            "অমাবস্যা দিনের অনুষ্ঠান (শ্রাদ্ধ ও তর্পণ দিনে হয়), তাই সূর্যোদয়ে অমাবস্যা তিথি থাকে যে দিন সেটাই তারিখ। "
            "তিথি আগের সন্ধ্যায় শুরু হতে পারে। দীপাবলি (প্রদোষ) ও সর্বপিতৃ অমাবস্যা (অপরাহ্ণ) নিজস্ব নিয়ম মানে, তাই "
            "এখানকার তারিখ থেকে একদিন আগে-পরে হতে পারে।"),
        "note.pradosh": (
            "তারিখ সন্ধ্যা দেখে ঠিক হয়, সূর্যোদয় দেখে নয়: সূর্যাস্তের পর প্রদোষ কালে ত্রয়োদশী থাকে যে দিন সেদিন ব্রত। "
            "দুই সন্ধ্যায় তিথি প্রদোষ কাল ছুঁলে প্রথম সন্ধ্যা। সারণির পূজার সময় নয়াদিল্লির সূর্যাস্ত থেকে শুরু; তা সারা "
            "বছর ও শহরভেদে বদলায়।"),
        "note.sankashti": (
            "সংকষ্টী চাঁদ দেখে ঠিক হয়, সূর্য দেখে নয়: চন্দ্রোদয়ের সময় চতুর্থী থাকে যে সন্ধ্যায় সেদিন ব্রত, কারণ তখনই "
            "উপবাস ভাঙা হয়। চন্দ্রোদয় প্রতিদিন প্রায় ৫০ মিনিট দেরিতে হয় এবং শহরভেদে কয়েক মিনিট তফাত হয়; নিজের "
            "শহরের সময় দেখুন।"),
        "note.masik_shivratri": (
            "এটি মধ্যরাতের অনুষ্ঠান; নিশীথ কালে (রাতের ১৫ মুহূর্তের ৮ম) চতুর্দশী থাকে যে দিন সেটাই তারিখ। নিশীথ ১২টার "
            "পরে পড়লে পূজা পরের তারিখের ভোররাতে হয়; দেখানো সময়ের সঙ্গে সেই তারিখ থাকে। দুই রাতে তিথি নিশীথ ছুঁলে "
            "প্রথম রাত।"),
        "note.kalashtami": (
            "কালাষ্টমী রাতের পূজা; প্রদোষ কালে (সূর্যাস্তের পর) অষ্টমী থাকে যে দিন সেটাই তারিখ। তিথি আগের সকালে শুরু "
            "বা রাতে শেষ হতে পারে; সারণিতে শুরু ও শেষ দেখুন। দুই সন্ধ্যা ছুঁলে প্রথম সন্ধ্যা।"),
        "faq.all_q": "{year} সালে {name} কোন কোন তারিখে পড়ছে?",
        "faq.all_a": "{year} সালে {name}: {count}টি তারিখ আছে (নয়াদিল্লি): {dates}।",
        "faq.next_q": "পরবর্তী {name} কবে?",
        "faq.first_q": "{year} সালের প্রথম {name} কবে?",
        "faq.on_a": "{name} {when} ({details})।",
        "faq.key_q": "{name} {short} তারিখে {label} কখন?",
        "faq.tithi_q": "{name} {short} তারিখে তিথি কখন শুরু ও শেষ হয়?",
        "faq.why_q": "{name} কোন তারিখে পড়বে তা কীভাবে ঠিক হয়?",
        "faq.why_a": "তারিখ এই নিয়মে ঠিক হয়: {rule}। {year} সালে এতে {count}টি তারিখ হয় (নয়াদিল্লি)।",
    },
    "or": {
        "what.purnima": "ପୂର୍ଣ୍ଣିମା ତାରିଖ ଓ ତିଥି ସମୟ",
        "what.amavasya": "ଅମାବାସ୍ୟା ତାରିଖ ଓ ତିଥି ସମୟ",
        "what.pradosh": "ସବୁ ତାରିଖ ଓ ପ୍ରଦୋଷ ପୂଜା ସମୟ",
        "what.sankashti": "ସବୁ ତାରିଖ ଓ ଚନ୍ଦ୍ରୋଦୟ ସମୟ",
        "what.masik_shivratri": "ସବୁ ତାରିଖ ଓ ନିଶୀଥ ପୂଜା ସମୟ",
        "what.kalashtami": "ସବୁ ତାରିଖ ଓ କାଳଭୈରବ ପୂଜା",
        "title": "{name} {year}: {what} (ନୂଆଦିଲ୍ଲୀ)",
        "h1": "{name} {year}: {what}",
        "desc": ("{year} ରେ {name}ର ସମସ୍ତ {count}ଟି ତାରିଖ - ବାର, ହିନ୍ଦୁ ମାସ, ତିଥିର ଆରମ୍ଭ ଓ ଶେଷ "
                 "(ନୂଆଦିଲ୍ଲୀ)। {about}{keytime}{next}"),
        "desc.about.purnima": "ସତ୍ୟନାରାୟଣ ପୂଜା, ସ୍ନାନ ଓ ଦାନର ପୂର୍ଣ୍ଣିମା ବ୍ରତ।",
        "desc.about.amavasya": "ଶ୍ରାଦ୍ଧ-ତର୍ପଣର ଅମାବାସ୍ୟା, ସୋମବତୀ ଓ ଶନି ଅମାବାସ୍ୟା ସହିତ।",
        "desc.about.pradosh": "ତ୍ରୟୋଦଶୀରେ ଶିବଙ୍କ ପ୍ରଦୋଷ ବ୍ରତ ଓ ପୂଜା ସମୟ।",
        "desc.about.sankashti": "କୃଷ୍ଣ ଚତୁର୍ଥୀରେ ଗଣେଶଙ୍କ ବ୍ରତ, ଚନ୍ଦ୍ରୋଦୟ ପରେ ପାରଣ।",
        "desc.about.masik_shivratri": "କୃଷ୍ଣ ଚତୁର୍ଦ୍ଦଶୀର ମାସିକ ଶିବରାତ୍ରି ଓ ନିଶୀଥ କାଳର ପୂଜା।",
        "desc.about.kalashtami": "ପ୍ରତି ମାସ କୃଷ୍ଣ ଅଷ୍ଟମୀରେ କାଳଭୈରବ ପୂଜା।",
        "desc.key": " ସହିତ {label}।",
        "desc.next": " ପରବର୍ତ୍ତୀ: {date}।",
        "ans.next": "ପରବର୍ତ୍ତୀ {name} <strong>{when}</strong> ({details})।",
        "ans.first": ("{year} ର ପ୍ରଥମ {name} <strong>{when}</strong> ({details})। "
                      "{year} ର ସମସ୍ତ {count}ଟି ତାରିଖ ତଳେ ଅଛି।"),
        "ans.past": ("{year} ର ସମସ୍ତ {count}ଟି {name} ତାରିଖ ତଳେ ଅଛି; ଶେଷଟି ଥିଲା "
                     "<strong>{when}</strong>।"),
        "ans.more": " {year} ର ତାରିଖ: {link}।",
        "table.h2": "{name} {year}: ସମସ୍ତ ତାରିଖ",
        "th.date": "ତାରିଖ",
        "th.month": "ହିନ୍ଦୁ ମାସ",
        "th.tithi": "ତିଥି",
        "adhika": "ଅଧିକ {month}",
        "also": "ସହିତ: ",
        "months.note": ('<p class="note"><small>ମାସଗୁଡ଼ିକ ଅମାନ୍ତ (ମାସ ଅମାବାସ୍ୟାରେ ଶେଷ ହୁଏ, ଯେପରି ଦକ୍ଷିଣ ଓ ପଶ୍ଚିମ '
                        "ଭାରତରେ)। ଉତ୍ତର ଭାରତର ପୂର୍ଣ୍ଣିମାନ୍ତ ପଞ୍ଜିକାରେ କୃଷ୍ଣ ପକ୍ଷର ନାମ ଏକ ମାସ ପରର ହୁଏ।</small></p>"),
        "variant.pradosh.0": "ସୋମ ପ୍ରଦୋଷ",
        "variant.pradosh.1": "ଭୌମ ପ୍ରଦୋଷ",
        "variant.pradosh.5": "ଶନି ପ୍ରଦୋଷ",
        "variant.sankashti.1": "ଅଙ୍ଗାରକ ଚତୁର୍ଥୀ",
        "variant.amavasya.0": "ସୋମବତୀ ଅମାବାସ୍ୟା",
        "variant.amavasya.5": "ଶନି ଅମାବାସ୍ୟା",
        "about.h2": "{name} କ'ଣ ଏବଂ କିପରି ପାଳନ କରାଯାଏ",
        "city.h2": "ଆପଣଙ୍କ ସହରର ପଞ୍ଜିକା",
        "related.h2": "ସମ୍ବନ୍ଧିତ ତାରିଖ ଓ କ୍ୟାଲେଣ୍ଡର",
        "crumb.page": "{name} {year}",
        "about.purnima": (
            "<p>ପୂର୍ଣ୍ଣିମା ଶୁକ୍ଳ ପକ୍ଷର ଶେଷ (୧୫ତମ) ତିଥି, ଯେତେବେଳେ ଚନ୍ଦ୍ର ସୂର୍ଯ୍ୟଙ୍କ ବିପରୀତରେ ପୂର୍ଣ୍ଣ ଆଲୋକିତ ହୁଏ। "
            "ଭକ୍ତମାନେ ଉପବାସ କରନ୍ତି, ପ୍ରଭାତରେ ସ୍ନାନ କରନ୍ତି, ବିଷ୍ଣୁଙ୍କ ପୂଜା କରନ୍ତି - ସତ୍ୟନାରାୟଣ କଥା ପୂର୍ଣ୍ଣିମାର "
            "ପ୍ରଚଳିତ ପୂଜା - ଏବଂ ସନ୍ଧ୍ୟାରେ ଚନ୍ଦ୍ରଙ୍କୁ ଅର୍ଘ୍ୟ ଦିଅନ୍ତି। ଏହି ଦିନର ଦାନ ବହୁଗୁଣ ପୁଣ୍ୟ ଦିଏ ବୋଲି "
            "ବିଶ୍ୱାସ।</p><p>ଗୁରୁ ପୂର୍ଣ୍ଣିମା, ଶରତ ପୂର୍ଣ୍ଣିମା, କାର୍ତ୍ତିକ ପୂର୍ଣ୍ଣିମା ଓ ବୁଦ୍ଧ ପୂର୍ଣ୍ଣିମା ନିଜେ ପର୍ବ; "
            "ହୋଲିକା ଦହନ ଫାଲ୍ଗୁନ ପୂର୍ଣ୍ଣିମାରେ ହୁଏ।</p>"),
        "about.amavasya": (
            "<p>ଅମାବାସ୍ୟା କୃଷ୍ଣ ପକ୍ଷର ୩୦ତମ ଓ ଶେଷ ତିଥି, ଯେତେବେଳେ ଚନ୍ଦ୍ର ସୂର୍ଯ୍ୟଙ୍କ ସହିତ ରହି ଦେଖାଯାଏ ନାହିଁ। ଏହା "
            "ପିତୃପୁରୁଷଙ୍କ ଦିନ: ତର୍ପଣ ଓ ଶ୍ରାଦ୍ଧ କରାଯାଏ, ବ୍ରାହ୍ମଣ ଓ ଗରିବଙ୍କୁ ଭୋଜନ ଦିଆଯାଏ, ଦାନ କରାଯାଏ, ପବିତ୍ର "
            "ଜଳରେ ସ୍ନାନ କରାଯାଏ।</p><p>ସୋମବାରର ଅମାବାସ୍ୟା ସୋମବତୀ ଅମାବାସ୍ୟା, ଶନିବାରର ଅମାବାସ୍ୟା ଶନି ଅମାବାସ୍ୟା। "
            "ମୌନୀ ଅମାବାସ୍ୟା, ସର୍ବପିତୃ (ମହାଳୟା) ଅମାବାସ୍ୟା ଓ ଦୀପାବଳିର ଅମାବାସ୍ୟା ପ୍ରମୁଖ।</p>"),
        "about.pradosh": (
            "<p>ପ୍ରଦୋଷ ବ୍ରତ ଦୁଇ ପକ୍ଷର ତ୍ରୟୋଦଶୀ (୧୩ତମ ତିଥି) ଦିନ ଶିବଙ୍କ ପାଇଁ ରଖାଯାଉଥିବା ବ୍ରତ - ମାସକୁ ଦୁଇଥର। ପ୍ରଦୋଷ "
            "କାଳ ସୂର୍ଯ୍ୟାସ୍ତ ପରର ସନ୍ଧ୍ୟା ସମୟ। ଭକ୍ତମାନେ ଦିନସାରା ଉପବାସ କରି ପ୍ରଦୋଷ କାଳରେ ଶିବ ପୂଜା କରନ୍ତି: ଜଳ, "
            "କ୍ଷୀର ଓ ବେଲପତ୍ରରେ ଅଭିଷେକ, ଦୀପ। ପୂଜା ପରେ ଉପବାସ ଭାଙ୍ଗନ୍ତି।</p><p>ସୋମବାରର ପ୍ରଦୋଷ ସୋମ ପ୍ରଦୋଷ, "
            "ମଙ୍ଗଳବାରର ଭୌମ ପ୍ରଦୋଷ, ଶନିବାରର ଶନି ପ୍ରଦୋଷ।</p>"),
        "about.sankashti": (
            "<p>ସଙ୍କଷ୍ଟି ଚତୁର୍ଥୀ କୃଷ୍ଣ ପକ୍ଷର ଚତୁର୍ଥୀ (୪ର୍ଥ ତିଥି) ଦିନ ଗଣେଶଙ୍କ ମାସିକ ବ୍ରତ। ଭକ୍ତମାନେ ଦିନସାରା ଉପବାସ "
            "କରି ସନ୍ଧ୍ୟାରେ ଗଣେଶଙ୍କ ପୂଜା କରନ୍ତି ଏବଂ ଚନ୍ଦ୍ର ଦେଖି ଅର୍ଘ୍ୟ ଦେବା ପରେ ହିଁ ଉପବାସ ଭାଙ୍ଗନ୍ତି - ତେଣୁ ଏହି "
            "ପୃଷ୍ଠାରେ ଚନ୍ଦ୍ରୋଦୟ ସମୟ ମୁଖ୍ୟ।</p><p>ମଙ୍ଗଳବାର ପଡ଼ିଲେ ସଙ୍କଷ୍ଟି ଚତୁର୍ଥୀ ଅଙ୍ଗାରକ ଚତୁର୍ଥୀ, ଯାହା "
            "ବିଶେଷ ଫଳଦାୟକ ବୋଲି ବିଶ୍ୱାସ।</p>"),
        "about.masik_shivratri": (
            "<p>ମାସିକ ଶିବରାତ୍ରି ପ୍ରତି ମାସ କୃଷ୍ଣ ପକ୍ଷର ଚତୁର୍ଦ୍ଦଶୀ (୧୪ତମ ତିଥି) ଦିନ ପାଳିତ ଶିବଙ୍କ ରାତ୍ରି। ଭକ୍ତମାନେ ଉପବାସ "
            "କରି ରାତି ଜାଗରଣ କରନ୍ତି, ଶିବଲିଙ୍ଗକୁ ଜଳ, କ୍ଷୀର, ମହୁ ଓ ବେଲପତ୍ରରେ ଅଭିଷେକ କରନ୍ତି। ପୂଜାର ଶ୍ରେଷ୍ଠ ସମୟ "
            "ନିଶୀଥ କାଳ, ଅର୍ଥାତ୍ ମଧ୍ୟରାତ୍ରି।</p><p>ମହାଶିବରାତ୍ରି ବାର ମଧ୍ୟରେ ସବୁଠୁ ବଡ଼।</p>"),
        "about.kalashtami": (
            "<p>କାଳାଷ୍ଟମୀ କୃଷ୍ଣ ପକ୍ଷର ଅଷ୍ଟମୀ (୮ମ ତିଥି) ଦିନ ପାଳିତ କାଳଭୈରବଙ୍କ ମାସିକ ଦିନ। ଭକ୍ତମାନେ ଉପବାସ କରି ରାତିରେ "
            "ସୋରିଷ ତେଲ ଦୀପ ସହ ଭୈରବଙ୍କ ପୂଜା କରନ୍ତି ଏବଂ କୁକୁରମାନଙ୍କୁ ଖାଇବାକୁ ଦିଅନ୍ତି।</p><p>ପୂର୍ଣ୍ଣିମାନ୍ତ ପଞ୍ଜିକାରେ "
            "ମାର୍ଗଶିର (ଅମାନ୍ତରେ କାର୍ତ୍ତିକ) ମାସର କାଳାଷ୍ଟମୀ କାଳଭୈରବ ଜୟନ୍ତୀ - ବର୍ଷର ପ୍ରମୁଖ କାଳାଷ୍ଟମୀ।</p>"),
        "note.purnima": (
            "ପୂର୍ଣ୍ଣିମା ଗୋଟିଏ ସନ୍ଧ୍ୟାରେ ଆରମ୍ଭ ହୋଇ ପରଦିନ ଅପରାହ୍ନ ପର୍ଯ୍ୟନ୍ତ ରହିପାରେ; ତେଣୁ ତିଥି ଆରମ୍ଭ ହେବା ଦିନ ଓ ବ୍ରତ ଦିନ "
            "ଭିନ୍ନ ହୋଇପାରେ। ନିୟମ ଅନୁସାରେ ତିଥି ମଧ୍ୟାହ୍ନରେ ଥିବା ଦିନ ବ୍ରତ; ଦୁଇ ଦିନ ଥିଲେ ପ୍ରଥମ ଦିନ। ଯାଞ୍ଚ ପାଇଁ ତାଲିକାରେ "
            "ତିଥିର ଆରମ୍ଭ ଓ ଶେଷ ଦିଆଯାଇଛି।"),
        "note.amavasya": (
            "ଅମାବାସ୍ୟା ଦିନର ଅନୁଷ୍ଠାନ (ଶ୍ରାଦ୍ଧ ଓ ତର୍ପଣ ଦିନରେ ହୁଏ), ତେଣୁ ସୂର୍ଯ୍ୟୋଦୟରେ ଅମାବାସ୍ୟା ତିଥି ଥିବା ଦିନ ହିଁ "
            "ତାରିଖ। ତିଥି ଆଗ ସନ୍ଧ୍ୟାରୁ ଆରମ୍ଭ ହୋଇପାରେ। ଦୀପାବଳି (ପ୍ରଦୋଷ) ଓ ସର୍ବପିତୃ ଅମାବାସ୍ୟା (ଅପରାହ୍ନ) ନିଜ ନିୟମ "
            "ମାନନ୍ତି, ତେଣୁ ଏଠାର ତାରିଖଠାରୁ ଏକ ଦିନ ଭିନ୍ନ ହୋଇପାରେ।"),
        "note.pradosh": (
            "ତାରିଖ ସନ୍ଧ୍ୟାରୁ ସ୍ଥିର ହୁଏ, ସୂର୍ଯ୍ୟୋଦୟରୁ ନୁହେଁ: ସୂର୍ଯ୍ୟାସ୍ତ ପରେ ପ୍ରଦୋଷ କାଳରେ ତ୍ରୟୋଦଶୀ ଥିବା ଦିନ ବ୍ରତ। ଦୁଇ "
            "ସନ୍ଧ୍ୟାରେ ତିଥି ପ୍ରଦୋଷ କାଳକୁ ଛୁଇଁଲେ ପ୍ରଥମ ସନ୍ଧ୍ୟା। ତାଲିକାର ପୂଜା ସମୟ ନୂଆଦିଲ୍ଲୀର ସୂର୍ଯ୍ୟାସ୍ତରୁ ଆରମ୍ଭ; "
            "ଏହା ବର୍ଷସାରା ଓ ସହର ଅନୁସାରେ ବଦଳେ।"),
        "note.sankashti": (
            "ସଙ୍କଷ୍ଟି ଚନ୍ଦ୍ରରୁ ସ୍ଥିର ହୁଏ, ସୂର୍ଯ୍ୟରୁ ନୁହେଁ: ଚନ୍ଦ୍ରୋଦୟ ସମୟରେ ଚତୁର୍ଥୀ ଥିବା ସନ୍ଧ୍ୟାରେ ବ୍ରତ, କାରଣ ସେତେବେଳେ "
            "ଉପବାସ ଭାଙ୍ଗାଯାଏ। ଚନ୍ଦ୍ରୋଦୟ ପ୍ରତିଦିନ ପ୍ରାୟ ୫୦ ମିନିଟ ଡେରିରେ ହୁଏ ଏବଂ ସହର ଅନୁସାରେ କେତେ ମିନିଟ ତଫାତ ରହେ; "
            "ନିଜ ସହରର ସମୟ ଦେଖନ୍ତୁ।"),
        "note.masik_shivratri": (
            "ଏହା ମଧ୍ୟରାତ୍ରିର ଅନୁଷ୍ଠାନ; ନିଶୀଥ କାଳରେ (ରାତ୍ରିର ୧୫ ମୁହୂର୍ତ୍ତ ମଧ୍ୟରୁ ୮ମ) ଚତୁର୍ଦ୍ଦଶୀ ଥିବା ଦିନ ହିଁ ତାରିଖ। "
            "ନିଶୀଥ ୧୨ଟା ପରେ ପଡ଼ିଲେ ପୂଜା ପରଦିନ ଭୋରରେ ହୁଏ; ଦେଖାଯାଇଥିବା ସମୟ ସହ ସେହି ତାରିଖ ରହେ। ଦୁଇ ରାତ୍ରି ନିଶୀଥକୁ "
            "ଛୁଇଁଲେ ପ୍ରଥମ ରାତ୍ରି।"),
        "note.kalashtami": (
            "କାଳାଷ୍ଟମୀ ରାତ୍ରି ପୂଜା; ପ୍ରଦୋଷ କାଳରେ (ସୂର୍ଯ୍ୟାସ୍ତ ପରେ) ଅଷ୍ଟମୀ ଥିବା ଦିନ ହିଁ ତାରିଖ। ତିଥି ଆଗ ସକାଳୁ ଆରମ୍ଭ "
            "କିମ୍ବା ରାତିରେ ଶେଷ ହୋଇପାରେ; ତାଲିକାରେ ଆରମ୍ଭ ଓ ଶେଷ ଦେଖନ୍ତୁ। ଦୁଇ ସନ୍ଧ୍ୟା ଛୁଇଁଲେ ପ୍ରଥମ ସନ୍ଧ୍ୟା।"),
        "faq.all_q": "{year} ରେ {name}ର ତାରିଖଗୁଡ଼ିକ କ'ଣ?",
        "faq.all_a": "{year} ରେ {name}ର {count}ଟି ତାରିଖ ଅଛି (ନୂଆଦିଲ୍ଲୀ): {dates}।",
        "faq.next_q": "ପରବର୍ତ୍ତୀ {name} କେବେ?",
        "faq.first_q": "{year} ର ପ୍ରଥମ {name} କେବେ?",
        "faq.on_a": "{name} {when} ({details})।",
        "faq.key_q": "{name} {short} ରେ {label} କେତେବେଳେ?",
        "faq.tithi_q": "{name} {short} ରେ ତିଥି କେତେବେଳେ ଆରମ୍ଭ ଓ ଶେଷ ହୁଏ?",
        "faq.why_q": "{name}ର ତାରିଖ କିପରି ସ୍ଥିର ହୁଏ?",
        "faq.why_a": "ତାରିଖ ଏହି ନିୟମରେ: {rule}। {year} ରେ ଏଥିରେ {count}ଟି ତାରିଖ ହୁଏ (ନୂଆଦିଲ୍ଲୀ)।",
    },
}

# Generic pieces the vrat & festival pages already have in every language
# (day label, timing line, tithi line, "timings vary by city", the FAQ's timings
# answer, headings, the 404 heading): reused as they are, never copied.
_REUSED = ("crumb", "day_label", "timing", "tithi.text", "tithi.paksha", "city_note", "tools.panchang",
           "more.today", "more.year", "more.ekadashi", "fest.rule_h2", "fest.faq_h2",
           "faq.timings_a", "nf.h1", "cta")
for _lang, _table in vrat_text.TEXT.items():
    if _lang in TEXT:
        for _k in _REUSED:
            if _table.get(_k):
                TEXT[_lang].setdefault(_k, _table[_k])

# The /sitemap page's heading for this family of pages.
for _lang, _v in {
        "en": "Monthly vrat dates", "hi": "मासिक व्रत की तिथियां", "kn": "ಮಾಸಿಕ ವ್ರತ ದಿನಾಂಕಗಳು",
        "te": "నెలవారీ వ్రత తేదీలు", "ta": "மாதாந்திர விரத தேதிகள்",
        "ml": "മാസ വ്രത തീയതികൾ", "bn": "মাসিক ব্রতের তারিখ", "or": "ମାସିକ ବ୍ରତ ତାରିଖ"}.items():
    TEXT[_lang]["hub.h2"] = _v
