"""The text of the year-long muhurat pages (muhurat_pages.py), per language.

TRANSLATORS: this file is data. To translate /muhurat/vivah-2026 and friends
into, say, Kannada, add a "kn" dict to TEXT with any subset of the "en" keys
(and, if your month names should differ from app/astro/names_kn.py, a "kn"
entry in MONTHS), then add "kn" to muhurat_pages.TRANSLATED. A key you leave
out falls back to the "_native" template (an astrology label in Kannada
script) and then to English.

* Templates keep their `{placeholders}`; the word order around them is yours.
* Values are HTML unless marked "plain text" (titles, descriptions, link and
  crumb labels, which the code escapes). Write `&amp;` for a literal "&" in HTML.
* Placeholders available in EVERY template, from app/astro/names_<code>.py:
  {t_<timing>} (TIMINGS) and {l_tithi} {l_nakshatra} {l_vara} ... (LIMBS).
* Tithi, paksha, nakshatra, weekday and month names are NOT here: they come
  from app/astro/names_<code>.py.
* Kind placeholders: {name} the muhurat's name ("Vivah Muhurat"), {name_lower}
  ("vivah muhurat"), {noun} ("wedding"), {noun_title} ("Wedding").
"""

from __future__ import annotations

from .astro.muhurat import PERIODS

TEXT: dict[str, dict[str, str]] = {
    "en": {
        # the two kinds of page (plain text)
        "kind.vivah": "Vivah Muhurat",
        "kind.griha-pravesh": "Griha Pravesh Muhurat",
        "noun.vivah": "wedding",
        "noun.griha-pravesh": "house-warming",
        # page head (plain text): {name} {name_lower} {noun} {noun_title} {year} {count} {brand}
        "title": "{name} {year}: Auspicious {noun_title} Dates (New Delhi) | {brand}",
        "h1": "{name} {year}: auspicious {noun} dates",
        "desc": ("{name} {year} for New Delhi — month-by-month auspicious "
                 "{noun} dates with tithi and nakshatra. {count} dates; "
                 "Chaturmas, Kharmas, Adhik Maas, Pitru Paksha and Guru/Shukra asta explained."),
        # the other language's name under the h1 (HTML): {name_en} {name_hi} {year}
        "sub": '<p class="hi" lang="hi">{name_hi} {year}</p>',
        # under it (plain text): {city} the city in this language, {label} "New Delhi, Delhi"
        "place": "{label} · IST",
        # HTML. {count} {name_lower} {year} {months} (escaped month list, or —)
        "intro": ("<p>By the panchang there are <strong>{count}</strong> "
                  "{name_lower} dates in {year} for New Delhi, in "
                  "{months}. Each date passes the classical checks on the sunrise "
                  "tithi, nakshatra, weekday, yoga and Bhadra, and falls outside Chaturmas, "
                  "Kharmas, Adhik Maas, Pitru Paksha and the combustion (asta) of Jupiter and "
                  "Venus.</p>"),
        "note": ("<p><strong>Timings vary by city.</strong> These dates are reckoned from New "
                 "Delhi's sunrise; elsewhere a tithi or nakshatra can change on a different day. "
                 "The exact muhurat (lagna) for a wedding or griha pravesh should be fixed by "
                 "your family priest. Check your own city in the Muhurat Finder.</p>"),
        "cta": "Find muhurat for your city — free",
        # crumb and link labels (plain text): {name} {year}
        "crumb": "{name} {year}",
        "more": "More muhurat dates",
        "link.kind": "{name} {year}",
        "link.panchang": "Today's Panchang",
        "link.milan": "Kundali Milan",
        # "When there is no ..." (heading plain text, intro HTML): {name_lower} {year}
        "periods.h2": "When there is no {name_lower} in {year}",
        "periods.intro": ("No {name_lower} is given during these periods. The dates are "
                          "computed from the panchang (New Delhi, sunrise):"),
        # one period (HTML): {period} {range} {about}
        "periods.item": "<li><strong>{period}</strong>, {range} — {about}.</li>",
        # a month with no dates (HTML): {name_lower} {month} {periods}
        "none.periods": "No {name_lower} in {month} — {periods}.",
        "none.plain": ("No {name_lower} in {month} — no day this month passes the tithi, "
                       "nakshatra, weekday and yoga checks."),
        # the month table's header (HTML)
        "th": "<tr><th>Date</th><th>Day</th><th>Tithi</th><th>Nakshatra</th></tr>",
        # the 404 page (plain text)
        "nf.title": "Muhurat page not found",
        "nf.open": "Open the Muhurat Finder",
    },
    "hi": {
        "kind.vivah": "विवाह मुहूर्त",
        "kind.griha-pravesh": "गृह प्रवेश मुहूर्त",
        "title": "{name} {year}: शुभ तिथियां (नई दिल्ली) | {brand}",
        "h1": "{name} {year}",
        "desc": ("{year} के {name} — नई दिल्ली के लिए माहवार शुभ तिथियां, तिथि व "
                 "नक्षत्र सहित। कुल {count} तिथियां; चातुर्मास, खरमास, अधिक मास, "
                 "पितृ पक्ष और गुरु-शुक्र अस्त की अवधि भी।"),
        "sub": '<p class="hi" lang="en">{name_en} {year}</p>',
        "place": "{city} · IST",
        "intro": ("<p>पंचांग के अनुसार {year} में नई दिल्ली के लिए <strong>{count}</strong> "
                  "{name} की तिथियां हैं, इन महीनों में: {months}। "
                  "हर तिथि सूर्योदय के तिथि, नक्षत्र, वार, योग और भद्रा के शास्त्रीय नियमों से "
                  "जांची गई है, और चातुर्मास, खरमास, अधिक मास, पितृ पक्ष तथा गुरु-शुक्र अस्त की "
                  "अवधि को छोड़ा गया है।</p>"),
        "note": ("<p><strong>ध्यान दें:</strong> ये तिथियां नई दिल्ली के सूर्योदय पर आधारित हैं। "
                 "दूसरे शहर में तिथि-नक्षत्र का समय बदलता है, और विवाह या गृह प्रवेश का सटीक "
                 "मुहूर्त (लग्न) परिवार के पंडित जी से अवश्य दिखवाएं। अपने शहर की तिथियां "
                 "मुहूर्त खोजक में देखें।</p>"),
        "cta": "अपने शहर के लिए शुभ मुहूर्त खोजें",
        "more": "और मुहूर्त",
        "link.panchang": "आज का पंचांग",
        "link.milan": "कुंडली मिलान",
        "periods.h2": "{year} में {name} कब नहीं है",
        "periods.intro": ("इन अवधियों में कोई {name} नहीं होता। ये तिथियां पंचांग से गणना की "
                          "गई हैं (नई दिल्ली, सूर्योदय):"),
        "periods.item": "<li><strong>{period}</strong>, {range} — {about}।</li>",
        "none.periods": "{month} में कोई {name} नहीं — {periods}।",
        "none.plain": "{month} में कोई {name} नहीं — इस माह कोई दिन तिथि, नक्षत्र, वार व योग की शर्तें पूरी नहीं करता।",
        "th": "<tr><th>तिथि (दिनांक)</th><th>वार</th><th>तिथि</th><th>नक्षत्र</th></tr>",
    },
    "bn": {
        "kind.vivah": "বিবাহের শুভ মুহূর্ত",
        "kind.griha-pravesh": "গৃহপ্রবেশের শুভ মুহূর্ত",
        # {noun} is used before "শুভ দিন", so it is the genitive form
        "noun.vivah": "বিয়ের",
        "noun.griha-pravesh": "গৃহপ্রবেশের",
        "title": "{name} {year}: শুভ দিন ও তারিখের তালিকা (নয়াদিল্লি) | {brand}",
        "h1": "{name} {year}: {noun} শুভ দিনগুলি",
        "desc": ("{name} {year} — নয়াদিল্লির জন্য মাস অনুযায়ী {noun} শুভ দিন, তিথি ও "
                 "নক্ষত্রসহ। মোট {count}টি দিন; চাতুর্মাস, খরমাস, অধিক মাস, পিতৃপক্ষ এবং "
                 "গুরু-শুক্র অস্তের সময়ও বুঝিয়ে বলা হয়েছে।"),
        "sub": '<p class="hi">পঞ্জিকা অনুযায়ী মাসভিত্তিক শুভ দিনের তালিকা · {year}</p>',
        "place": "নয়াদিল্লি, দিল্লি · ভারতীয় সময়",
        "intro": ("<p>পঞ্জিকা অনুযায়ী {year} সালে নয়াদিল্লির জন্য {name_lower} হিসেবে "
                  "<strong>{count}</strong>টি দিন পাওয়া যায়, এই মাসগুলিতে: {months}। প্রতিটি দিন সূর্যোদয়কালীন "
                  "তিথি, নক্ষত্র, বার, যোগ ও ভদ্রার শাস্ত্রীয় নিয়মে যাচাই করা, এবং চাতুর্মাস, "
                  "খরমাস, অধিক মাস, পিতৃপক্ষ ও বৃহস্পতি-শুক্রের অস্তকালের বাইরে।</p>"),
        "note": ("<p><strong>শহরভেদে সময় বদলায়।</strong> এই দিনগুলি নয়াদিল্লির সূর্যোদয় ধরে "
                 "গণনা করা; অন্য জায়গায় তিথি বা নক্ষত্র অন্য দিনে বদলাতে পারে। বিয়ে বা "
                 "গৃহপ্রবেশের সঠিক মুহূর্ত (লগ্ন) আপনার পারিবারিক পুরোহিতের কাছ থেকে ঠিক করিয়ে "
                 "নিন। নিজের শহরের দিন দেখুন শুভ মুহূর্ত সন্ধানে।</p>"),
        "cta": "আপনার শহরের শুভ মুহূর্ত খুঁজুন — বিনামূল্যে",
        "crumb": "{name} {year}",
        "more": "আরও শুভ মুহূর্ত",
        "link.kind": "{name} {year}",
        "link.panchang": "আজকের পঞ্জিকা",
        "link.milan": "যোটক বিচার",
        "periods.h2": "{year} সালে কখন {name_lower} নেই",
        "periods.intro": ("এই সময়গুলিতে কোনো {name_lower} দেওয়া হয় না। দিনগুলি পঞ্জিকা থেকে "
                          "গণনা করা (নয়াদিল্লি, সূর্যোদয়):"),
        "periods.item": "<li><strong>{period}</strong>, {range} — {about}।</li>",
        "none.periods": "{month} মাসে কোনো {name_lower} নেই — {periods}।",
        "none.plain": ("{month} মাসে কোনো {name_lower} নেই — এই মাসে কোনো দিনই তিথি, নক্ষত্র, "
                       "বার ও যোগের শর্ত পূরণ করে না।"),
        "th": "<tr><th>তারিখ</th><th>বার</th><th>তিথি</th><th>নক্ষত্র</th></tr>",
        "nf.title": "শুভ মুহূর্তের পাতাটি পাওয়া যায়নি",
        "nf.open": "শুভ মুহূর্ত সন্ধান খুলুন",
        "period.chaturmas": "চাতুর্মাস",
        "period_about.chaturmas": ("দেবশয়নী একাদশী থেকে উত্থান একাদশী পর্যন্ত, যখন ভগবান বিষ্ণু "
                                   "যোগনিদ্রায় থাকেন"),
        "period.kharmas": "খরমাস",
        "period_about.kharmas": "সূর্য ধনু বা মীন রাশিতে থাকার সময়",
        "period.adhik_maas": "অধিক মাস (মলমাস)",
        "period_about.adhik_maas": "যে চান্দ্র মাসে সূর্যের কোনো সংক্রান্তি হয় না",
        "period.pitru_paksha": "পিতৃপক্ষ",
        "period_about.pitru_paksha": ("ভাদ্র পূর্ণিমা থেকে সর্বপিতৃ অমাবস্যা (মহালয়া) পর্যন্ত, "
                                      "শ্রাদ্ধের পক্ষ"),
        "period.shukra_asta": "শুক্র অস্ত",
        "period_about.shukra_asta": ("শুক্র গ্রহ অস্ত (সূর্যের খুব কাছে থাকায় দেখা যায় না), "
                                     "আগে-পরে 3 দিনসহ"),
        "period.guru_asta": "গুরু অস্ত",
        "period_about.guru_asta": ("বৃহস্পতি গ্রহ অস্ত (সূর্যের খুব কাছে থাকায় দেখা যায় না), "
                                   "আগে-পরে 3 দিনসহ"),
    },
    "or": {
        "kind.vivah": "ବିବାହ ଶୁଭ ମୁହୂର୍ତ୍ତ",
        "kind.griha-pravesh": "ଗୃହପ୍ରବେଶ ଶୁଭ ମୁହୂର୍ତ୍ତ",
        # {noun} is used before "ଶୁଭ ଦିନ", so it is the genitive form
        "noun.vivah": "ବିବାହର",
        "noun.griha-pravesh": "ଗୃହପ୍ରବେଶର",
        "title": "{name} {year}: ଶୁଭ ଦିନ ଓ ତାରିଖ ତାଲିକା (ନୂଆଦିଲ୍ଲୀ) | {brand}",
        "h1": "{name} {year}: {noun} ଶୁଭ ଦିନ",
        "desc": ("{name} {year} — ନୂଆଦିଲ୍ଲୀ ପାଇଁ ମାସ ଅନୁସାରେ {noun} ଶୁଭ ଦିନ, ତିଥି ଓ "
                 "ନକ୍ଷତ୍ର ସହିତ। ମୋଟ {count}ଟି ଦିନ; ଚାତୁର୍ମାସ୍ୟ, ଖରମାସ, ଅଧିକ ମାସ, ପିତୃପକ୍ଷ ଓ "
                 "ଗୁରୁ-ଶୁକ୍ର ଅସ୍ତର ସମୟ ମଧ୍ୟ ବୁଝାଇ ଦିଆଯାଇଛି।"),
        "sub": '<p class="hi">ପାଞ୍ଜି ଅନୁସାରେ ମାସ ଅନୁଯାୟୀ ଶୁଭ ଦିନର ତାଲିକା · {year}</p>',
        "place": "ନୂଆଦିଲ୍ଲୀ, ଦିଲ୍ଲୀ · ଭାରତୀୟ ସମୟ",
        "intro": ("<p>ପାଞ୍ଜି ଅନୁସାରେ {year} ରେ ନୂଆଦିଲ୍ଲୀ ପାଇଁ <strong>{count}</strong>ଟି "
                  "{name_lower}ର ଦିନ ଅଛି, ଏହି ମାସଗୁଡ଼ିକରେ: {months}। ପ୍ରତ୍ୟେକ ଦିନ ସୂର୍ଯ୍ୟୋଦୟ ସମୟର "
                  "ତିଥି, ନକ୍ଷତ୍ର, ବାର, ଯୋଗ ଓ ଭଦ୍ରାର ଶାସ୍ତ୍ରୀୟ ନିୟମରେ ଯାଞ୍ଚ କରାଯାଇଛି, ଏବଂ "
                  "ଚାତୁର୍ମାସ୍ୟ, ଖରମାସ, ଅଧିକ ମାସ, ପିତୃପକ୍ଷ ଓ ବୃହସ୍ପତି-ଶୁକ୍ରଙ୍କ ଅସ୍ତ ସମୟ ବାହାରେ "
                  "ପଡ଼େ।</p>"),
        "note": ("<p><strong>ସହର ଅନୁସାରେ ସମୟ ବଦଳେ।</strong> ଏହି ଦିନଗୁଡ଼ିକ ନୂଆଦିଲ୍ଲୀର "
                 "ସୂର୍ଯ୍ୟୋଦୟ ଅନୁସାରେ ଗଣନା କରାଯାଇଛି; ଅନ୍ୟ ସ୍ଥାନରେ ତିଥି ବା ନକ୍ଷତ୍ର ଭିନ୍ନ ଦିନରେ "
                 "ବଦଳିପାରେ। ବିବାହ ବା ଗୃହପ୍ରବେଶର ସଠିକ୍ ମୁହୂର୍ତ୍ତ (ଲଗ୍ନ) ଆପଣଙ୍କ ପରିବାରର "
                 "ପୁରୋହିତଙ୍କ ଦ୍ୱାରା ସ୍ଥିର କରାନ୍ତୁ। ନିଜ ସହରର ଦିନ ଶୁଭ ମୁହୂର୍ତ୍ତ ସନ୍ଧାନରେ "
                 "ଦେଖନ୍ତୁ।</p>"),
        "cta": "ଆପଣଙ୍କ ସହରର ଶୁଭ ମୁହୂର୍ତ୍ତ ଖୋଜନ୍ତୁ — ମାଗଣା",
        "crumb": "{name} {year}",
        "more": "ଅଧିକ ଶୁଭ ମୁହୂର୍ତ୍ତ",
        "link.kind": "{name} {year}",
        "link.panchang": "ଆଜିର ପାଞ୍ଜି",
        "link.milan": "କୁଣ୍ଡଳୀ ମିଳନ",
        "periods.h2": "{year} ରେ କେବେ {name_lower} ନାହିଁ",
        "periods.intro": ("ଏହି ସମୟରେ କୌଣସି {name_lower} ଦିଆଯାଏ ନାହିଁ। ଦିନଗୁଡ଼ିକ ପାଞ୍ଜିରୁ "
                          "ଗଣନା କରାଯାଇଛି (ନୂଆଦିଲ୍ଲୀ, ସୂର୍ଯ୍ୟୋଦୟ):"),
        "periods.item": "<li><strong>{period}</strong>, {range} — {about}।</li>",
        "none.periods": "{month} ମାସରେ କୌଣସି {name_lower} ନାହିଁ — {periods}।",
        "none.plain": ("{month} ମାସରେ କୌଣସି {name_lower} ନାହିଁ — ଏହି ମାସର କୌଣସି ଦିନ ତିଥି, "
                       "ନକ୍ଷତ୍ର, ବାର ଓ ଯୋଗର ସର୍ତ୍ତ ପୂରଣ କରେ ନାହିଁ।"),
        "th": "<tr><th>ତାରିଖ</th><th>ବାର</th><th>ତିଥି</th><th>ନକ୍ଷତ୍ର</th></tr>",
        "nf.title": "ଶୁଭ ମୁହୂର୍ତ୍ତ ପୃଷ୍ଠା ମିଳିଲା ନାହିଁ",
        "nf.open": "ଶୁଭ ମୁହୂର୍ତ୍ତ ସନ୍ଧାନ ଖୋଲନ୍ତୁ",
        "period.chaturmas": "ଚାତୁର୍ମାସ୍ୟ",
        "period_about.chaturmas": ("ହରିଶୟନ ଏକାଦଶୀରୁ ଦେବୋତ୍ଥାନ ଏକାଦଶୀ ପର୍ଯ୍ୟନ୍ତ, ଯେତେବେଳେ "
                                   "ଭଗବାନ ବିଷ୍ଣୁ ଯୋଗନିଦ୍ରାରେ ଥାଆନ୍ତି"),
        "period.kharmas": "ଖରମାସ",
        "period_about.kharmas": "ସୂର୍ଯ୍ୟ ଧନୁ ବା ମୀନ ରାଶିରେ ଥିବା ସମୟ",
        "period.adhik_maas": "ଅଧିକ ମାସ (ମଳମାସ)",
        "period_about.adhik_maas": "ଯେଉଁ ଚାନ୍ଦ୍ର ମାସରେ ସୂର୍ଯ୍ୟଙ୍କ କୌଣସି ସଂକ୍ରାନ୍ତି ହୁଏ ନାହିଁ",
        "period.pitru_paksha": "ପିତୃପକ୍ଷ",
        "period_about.pitru_paksha": ("ଭାଦ୍ରବ ପୂର୍ଣ୍ଣିମାରୁ ସର୍ବପିତୃ ଅମାବାସ୍ୟା (ମହାଳୟା) "
                                      "ପର୍ଯ୍ୟନ୍ତ, ଶ୍ରାଦ୍ଧର ପକ୍ଷ"),
        "period.shukra_asta": "ଶୁକ୍ର ଅସ୍ତ",
        "period_about.shukra_asta": ("ଶୁକ୍ର ଗ୍ରହ ଅସ୍ତ (ସୂର୍ଯ୍ୟଙ୍କ ଅତି ନିକଟରେ ଥିବାରୁ ଦେଖାଯାଏ "
                                     "ନାହିଁ), ଆଗପଛ 3 ଦିନ ସହିତ"),
        "period.guru_asta": "ଗୁରୁ ଅସ୍ତ",
        "period_about.guru_asta": ("ବୃହସ୍ପତି ଗ୍ରହ ଅସ୍ତ (ସୂର୍ଯ୍ୟଙ୍କ ଅତି ନିକଟରେ ଥିବାରୁ ଦେଖାଯାଏ "
                                   "ନାହିଁ), ଆଗପଛ 3 ଦିନ ସହିତ"),
    },
    # A language's fallback for a key it has not translated, before English:
    # only labels that are astrology names (from app/astro/names_<code>.py).
    "_native": {
        "th": "<tr><th>Date</th><th>{l_vara}</th><th>{l_tithi}</th><th>{l_nakshatra}</th></tr>",
    },
}

# The classical periods with no muhurat (Chaturmas, Kharmas ...): name and what
# it is, read from the engine (astro/muhurat.PERIODS) so the page and the
# Muhurat Finder's reasons never disagree. Add "period.<key>" /
# "period_about.<key>" to your language above to translate them.
for _k, _p in PERIODS.items():
    TEXT["en"][f"period.{_k}"], TEXT["en"][f"period_about.{_k}"] = _p.name_en, _p.about_en
    TEXT["hi"][f"period.{_k}"], TEXT["hi"][f"period_about.{_k}"] = _p.name_hi, _p.about_hi

# Month names where this page spells them differently from names_<code>.MONTHS
# (the Hindi pages have always printed "फरवरी" without the nukta).
MONTHS: dict[str, tuple[str, ...]] = {
    "hi": ("जनवरी", "फरवरी", "मार्च", "अप्रैल", "मई", "जून", "जुलाई", "अगस्त",
           "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर"),
}
