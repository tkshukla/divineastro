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
    "kn": {
        "kind.vivah": "ವಿವಾಹ ಮುಹೂರ್ತ",
        "kind.griha-pravesh": "ಗೃಹ ಪ್ರವೇಶ ಮುಹೂರ್ತ",
        # {noun} is written in the dative ("for a wedding"): it is only used as
        # "{noun} ಶುಭ ದಿನಾಂಕಗಳು" below.
        "noun.vivah": "ಮದುವೆಗೆ",
        "noun.griha-pravesh": "ಗೃಹ ಪ್ರವೇಶಕ್ಕೆ",
        "title": "{name} {year} — {noun_title} ಶುಭ ದಿನಾಂಕಗಳು | {brand}",
        "h1": "{name} {year}: {noun} ಶುಭ ದಿನಾಂಕಗಳು",
        "desc": ("{name} {year}: ನವದೆಹಲಿಗೆ ತಿಂಗಳುವಾರು ಶುಭ ದಿನಾಂಕಗಳು, ತಿಥಿ-ನಕ್ಷತ್ರ ಸಹಿತ. "
                 "ಒಟ್ಟು {count} ದಿನಾಂಕಗಳು; ಚಾತುರ್ಮಾಸ, ಖರಮಾಸ, ಅಧಿಕ ಮಾಸ, ಪಿತೃ ಪಕ್ಷ, "
                 "ಗುರು-ಶುಕ್ರ ಮೌಢ್ಯ ವಿವರ."),
        "sub": '<p class="hi">{year}ರ ಶುಭ ದಿನಗಳ ಪಟ್ಟಿ — ಪಂಚಾಂಗದ ಪ್ರಕಾರ</p>',
        "place": "{label} · IST",
        "intro": ("<p>ಪಂಚಾಂಗದ ಪ್ರಕಾರ {year}ರಲ್ಲಿ ನವದೆಹಲಿಗೆ ಒಟ್ಟು <strong>{count}</strong> "
                  "{name} ದಿನಾಂಕಗಳಿವೆ, ಈ ತಿಂಗಳುಗಳಲ್ಲಿ: {months}. ಪ್ರತಿ ದಿನಾಂಕವೂ ಸೂರ್ಯೋದಯದ "
                  "ತಿಥಿ, ನಕ್ಷತ್ರ, ವಾರ, ಯೋಗ ಮತ್ತು ಭದ್ರಾ ಕುರಿತ ಶಾಸ್ತ್ರೀಯ ನಿಯಮಗಳನ್ನು "
                  "ಪೂರೈಸುತ್ತದೆ, ಮತ್ತು ಚಾತುರ್ಮಾಸ, ಖರಮಾಸ, ಅಧಿಕ ಮಾಸ, ಪಿತೃ ಪಕ್ಷ ಹಾಗೂ ಗುರು-ಶುಕ್ರ "
                  "ಮೌಢ್ಯದ (ಅಸ್ತ) ಅವಧಿಗಳ ಹೊರಗಿದೆ.</p>"),
        "note": ("<p><strong>ಸಮಯ ನಗರದಿಂದ ನಗರಕ್ಕೆ ಬದಲಾಗುತ್ತದೆ.</strong> ಈ ದಿನಾಂಕಗಳನ್ನು "
                 "ನವದೆಹಲಿಯ ಸೂರ್ಯೋದಯದಿಂದ ಲೆಕ್ಕಹಾಕಲಾಗಿದೆ; ಬೇರೆಡೆ ತಿಥಿ ಅಥವಾ ನಕ್ಷತ್ರ ಬೇರೆ "
                 "ದಿನದಲ್ಲಿ ಬದಲಾಗಬಹುದು. ಮದುವೆ ಅಥವಾ ಗೃಹ ಪ್ರವೇಶದ ನಿಖರ ಮುಹೂರ್ತವನ್ನು (ಲಗ್ನ) "
                 "ನಿಮ್ಮ ಕುಟುಂಬದ ಪುರೋಹಿತರಿಂದ ನಿಗದಿಪಡಿಸಿಕೊಳ್ಳಿ. ನಿಮ್ಮ ನಗರದ ದಿನಾಂಕಗಳನ್ನು "
                 "‘ಮುಹೂರ್ತ ಹುಡುಕಿ’ಯಲ್ಲಿ ನೋಡಿ.</p>"),
        "cta": "ನಿಮ್ಮ ನಗರಕ್ಕೆ ಮುಹೂರ್ತ ಹುಡುಕಿ — ಉಚಿತ",
        "crumb": "{name} {year}",
        "more": "ಇನ್ನಷ್ಟು ಮುಹೂರ್ತ ದಿನಾಂಕಗಳು",
        "link.kind": "{name} {year}",
        "link.panchang": "ಇಂದಿನ ಪಂಚಾಂಗ",
        "link.milan": "ಜಾತಕ ಹೊಂದಾಣಿಕೆ",
        "periods.h2": "{year}ರಲ್ಲಿ {name} ಇಲ್ಲದ ಅವಧಿಗಳು",
        "periods.intro": ("ಈ ಅವಧಿಗಳಲ್ಲಿ {name} ನೀಡಲಾಗುವುದಿಲ್ಲ. ದಿನಾಂಕಗಳನ್ನು ಪಂಚಾಂಗದಿಂದ "
                          "ಲೆಕ್ಕಹಾಕಲಾಗಿದೆ (ನವದೆಹಲಿ, ಸೂರ್ಯೋದಯ):"),
        "periods.item": "<li><strong>{period}</strong>, {range} — {about}.</li>",
        "none.periods": "{month}ರಲ್ಲಿ {name} ಇಲ್ಲ — {periods}.",
        "none.plain": ("{month}ರಲ್ಲಿ {name} ಇಲ್ಲ — ಈ ತಿಂಗಳ ಯಾವ ದಿನವೂ ತಿಥಿ, ನಕ್ಷತ್ರ, ವಾರ ಮತ್ತು "
                       "ಯೋಗದ ನಿಯಮಗಳನ್ನು ಪೂರೈಸುವುದಿಲ್ಲ."),
        "th": "<tr><th>ದಿನಾಂಕ</th><th>ವಾರ</th><th>ತಿಥಿ</th><th>ನಕ್ಷತ್ರ</th></tr>",
        "nf.title": "ಮುಹೂರ್ತ ಪುಟ ಕಂಡುಬಂದಿಲ್ಲ",
        "nf.open": "ಮುಹೂರ್ತ ಹುಡುಕಿ ತೆರೆಯಿರಿ",
        # astro/muhurat.PERIODS
        "period.chaturmas": "ಚಾತುರ್ಮಾಸ",
        "period_about.chaturmas": ("ಶಯನಿ ಏಕಾದಶಿಯಿಂದ ಉತ್ಥಾನ ಏಕಾದಶಿಯವರೆಗೆ, ಶ್ರೀ ವಿಷ್ಣು "
                                   "ಯೋಗನಿದ್ರೆಯಲ್ಲಿರುವ ಕಾಲ"),
        "period.kharmas": "ಖರಮಾಸ",
        "period_about.kharmas": "ಸೂರ್ಯನು ಧನು ಅಥವಾ ಮೀನ ರಾಶಿಯಲ್ಲಿರುವ ಕಾಲ",
        "period.adhik_maas": "ಅಧಿಕ ಮಾಸ",
        "period_about.adhik_maas": "ಸೂರ್ಯನ ಯಾವುದೇ ಸಂಕ್ರಮಣವಿಲ್ಲದ ಹೆಚ್ಚುವರಿ ಚಾಂದ್ರ ಮಾಸ",
        "period.pitru_paksha": "ಪಿತೃ ಪಕ್ಷ",
        "period_about.pitru_paksha": ("ಭಾದ್ರಪದ ಹುಣ್ಣಿಮೆಯಿಂದ ಮಹಾಲಯ ಅಮಾವಾಸ್ಯೆಯವರೆಗೆ, "
                                      "ಶ್ರಾದ್ಧದ ಪಕ್ಷ"),
        "period.shukra_asta": "ಶುಕ್ರ ಮೌಢ್ಯ",
        "period_about.shukra_asta": ("ಶುಕ್ರ ಗ್ರಹ ಅಸ್ತ (ಸೂರ್ಯನಿಗೆ ತೀರ ಹತ್ತಿರವಿದ್ದು "
                                     "ಕಾಣಿಸುವುದಿಲ್ಲ), ಹಿಂದೆ-ಮುಂದೆ 3 ದಿನಗಳ ಸಹಿತ"),
        "period.guru_asta": "ಗುರು ಮೌಢ್ಯ",
        "period_about.guru_asta": ("ಗುರು ಗ್ರಹ ಅಸ್ತ (ಸೂರ್ಯನಿಗೆ ತೀರ ಹತ್ತಿರವಿದ್ದು "
                                   "ಕಾಣಿಸುವುದಿಲ್ಲ), ಹಿಂದೆ-ಮುಂದೆ 3 ದಿನಗಳ ಸಹಿತ"),
    },
    "te": {
        # plural "muhurats": {name} is used with plural verbs (ఉన్నాయి, లేవు) below.
        "kind.vivah": "వివాహ ముహూర్తాలు",
        "kind.griha-pravesh": "గృహ ప్రవేశ ముహూర్తాలు",
        "noun.vivah": "పెళ్లి",
        "noun.griha-pravesh": "గృహ ప్రవేశ",
        "title": "{name} {year} — {noun_title} శుభ తేదీలు | {brand}",
        "h1": "{name} {year}: {noun} శుభ తేదీలు",
        "desc": ("న్యూఢిల్లీకి {name} {year} — నెలవారీ శుభ తేదీలు, తిథి, నక్షత్రాలతో. మొత్తం "
                 "{count} తేదీలు; చాతుర్మాస్యం, ఖర మాసం, అధిక మాసం, పితృ పక్షం, గురు-శుక్ర "
                 "మౌఢ్యం వివరాలు."),
        "sub": '<p class="hi">{year} శుభ తేదీల జాబితా — పంచాంగం ప్రకారం</p>',
        "place": "{label} · IST",
        "intro": ("<p>పంచాంగం ప్రకారం {year}లో న్యూఢిల్లీకి మొత్తం <strong>{count}</strong> "
                  "{name} ఉన్నాయి, ఈ నెలల్లో: {months}. ప్రతి తేదీ సూర్యోదయ సమయంలోని తిథి, "
                  "నక్షత్రం, వారం, యోగం, భద్ర గురించిన శాస్త్రీయ నియమాలకు సరిపోతుంది; "
                  "చాతుర్మాస్యం, ఖర మాసం, అధిక మాసం, పితృ పక్షం, గురు-శుక్ర మౌఢ్యం (అస్తంగత్వం) "
                  "కాలాలకు వెలుపల ఉంటుంది.</p>"),
        "note": ("<p><strong>సమయాలు ఊరిని బట్టి మారుతాయి.</strong> ఈ తేదీలు న్యూఢిల్లీ "
                 "సూర్యోదయం ఆధారంగా లెక్కించినవి; ఇతర ప్రాంతాల్లో తిథి లేదా నక్షత్రం వేరే రోజున "
                 "మారవచ్చు. పెళ్లి లేదా గృహ ప్రవేశానికి ఖచ్చితమైన ముహూర్తం (లగ్నం) మీ కుటుంబ "
                 "పురోహితుల ద్వారా నిర్ణయించుకోండి. మీ ఊరి తేదీలను ‘ముహూర్తం వెతకండి’లో "
                 "చూడండి.</p>"),
        "cta": "మీ ఊరికి ముహూర్తం వెతకండి — ఉచితం",
        "crumb": "{name} {year}",
        "more": "మరిన్ని ముహూర్త తేదీలు",
        "link.kind": "{name} {year}",
        "link.panchang": "ఈరోజు పంచాంగం",
        "link.milan": "జాతక పొంతన",
        "periods.h2": "{year}లో {name} లేని కాలాలు",
        "periods.intro": ("ఈ కాలాల్లో {name} ఉండవు. తేదీలను పంచాంగం నుండి లెక్కించాము "
                          "(న్యూఢిల్లీ, సూర్యోదయం):"),
        "periods.item": "<li><strong>{period}</strong>, {range} — {about}.</li>",
        "none.periods": "{month}లో {name} లేవు — {periods}.",
        "none.plain": ("{month}లో {name} లేవు — ఈ నెలలో ఏ రోజూ తిథి, నక్షత్రం, వారం, యోగ "
                       "నియమాలకు సరిపోదు."),
        "th": "<tr><th>తేదీ</th><th>వారం</th><th>తిథి</th><th>నక్షత్రం</th></tr>",
        "nf.title": "ముహూర్తం పేజీ కనబడలేదు",
        "nf.open": "ముహూర్తం వెతకండి తెరవండి",
        # astro/muhurat.PERIODS
        "period.chaturmas": "చాతుర్మాస్యం",
        "period_about.chaturmas": ("తొలి ఏకాదశి నుండి ఉత్థాన ఏకాదశి వరకు, శ్రీ మహావిష్ణువు "
                                   "యోగనిద్రలో ఉండే కాలం"),
        "period.kharmas": "ఖర మాసం",
        "period_about.kharmas": "సూర్యుడు ధనుస్సు లేదా మీన రాశిలో ఉండే కాలం",
        "period.adhik_maas": "అధిక మాసం",
        "period_about.adhik_maas": "సూర్య సంక్రమణం లేని అదనపు చాంద్ర మాసం",
        "period.pitru_paksha": "పితృ పక్షం",
        "period_about.pitru_paksha": ("భాద్రపద పౌర్ణమి నుండి మహాలయ అమావాస్య వరకు, శ్రాద్ధాల "
                                      "పక్షం"),
        "period.shukra_asta": "శుక్ర మౌఢ్యం",
        "period_about.shukra_asta": ("శుక్ర గ్రహం అస్తంగతం (సూర్యునికి అతి దగ్గరగా ఉండి "
                                     "కనిపించదు), ముందు-వెనుక 3 రోజులతో సహా"),
        "period.guru_asta": "గురు మౌఢ్యం",
        "period_about.guru_asta": ("గురు గ్రహం అస్తంగతం (సూర్యునికి అతి దగ్గరగా ఉండి "
                                   "కనిపించదు), ముందు-వెనుక 3 రోజులతో సహా"),
    },
    # Tamil (DIVASTRO-123). Pitru Paksha = மகாளய பட்சம், asta = அஸ்தமனம்.
    "ta": {
        "kind.vivah": "திருமண முகூர்த்தம்",
        "kind.griha-pravesh": "கிரகப்பிரவேச முகூர்த்தம்",
        "noun.vivah": "திருமண",
        "noun.griha-pravesh": "கிரகப்பிரவேச",
        "title": "{noun} முகூர்த்த நாட்கள் {year} — புது தில்லி | {brand}",
        "h1": "{noun} முகூர்த்த நாட்கள் {year}",
        "desc": ("{year} {noun} முகூர்த்த நாட்கள் — புது தில்லிக்கான மாதவாரியான நல்ல நாட்கள், "
                 "திதி, நட்சத்திரத்துடன். மொத்தம் {count} நாட்கள்; சாதுர்மாஸ்யம், கர்மாஸ், "
                 "அதிக மாதம், மகாளய பட்சம், குரு-சுக்கிர அஸ்தமனம் பற்றிய விளக்கமும்."),
        "sub": '<p class="hi">{year} ஆம் ஆண்டின் {name} — மாதவாரியாக</p>',
        "place": "{label} · IST",
        "intro": ("<p>பஞ்சாங்கப்படி {year} இல் புது தில்லிக்கு <strong>{count}</strong> "
                  "{noun} முகூர்த்த நாட்கள் உள்ளன; அவை வரும் மாதங்கள்: {months}. ஒவ்வொரு நாளும் "
                  "சூரிய உதய நேரத் திதி, நட்சத்திரம், கிழமை, யோகம், பத்திரை (விஷ்டி கரணம்) ஆகிய "
                  "சாஸ்திர விதிகளின்படி சரிபார்க்கப்பட்டது; சாதுர்மாஸ்யம், கர்மாஸ், அதிக மாதம், "
                  "மகாளய பட்சம், குரு, சுக்கிர அஸ்தமனக் காலங்கள் தவிர்க்கப்பட்டுள்ளன.</p>"),
        "note": ("<p><strong>ஊருக்கு ஊர் நேரம் மாறும்.</strong> இந்த நாட்கள் புது தில்லியின் "
                 "சூரிய உதயத்தை வைத்துக் கணக்கிடப்பட்டவை; வேறு ஊரில் ஒரு திதியோ நட்சத்திரமோ "
                 "வேறு நாளில் மாறலாம். திருமணம் அல்லது கிரகப்பிரவேசத்துக்கான சரியான முகூர்த்த "
                 "நேரத்தை (லக்னம்) உங்கள் குடும்ப ஜோதிடர் / புரோகிதரிடம் உறுதி செய்துகொள்ளுங்கள். "
                 "உங்கள் ஊருக்கான நாட்களை முகூர்த்தம் தேடலில் பாருங்கள்.</p>"),
        "cta": "உங்கள் ஊருக்கான முகூர்த்தம் தேடுங்கள் — இலவசம்",
        "crumb": "{name} {year}",
        "more": "மேலும் முகூர்த்த நாட்கள்",
        "link.kind": "{name} {year}",
        "link.panchang": "இன்றைய பஞ்சாங்கம்",
        "link.milan": "ஜாதகப் பொருத்தம்",
        "periods.h2": "{year} இல் {noun} முகூர்த்தம் இல்லாத காலங்கள்",
        "periods.intro": ("இந்தக் காலங்களில் {noun} முகூர்த்தம் வைக்கப்படுவதில்லை. நாட்கள் "
                          "பஞ்சாங்கத்திலிருந்து கணக்கிடப்பட்டவை (புது தில்லி, சூரிய உதயம்):"),
        "periods.item": "<li><strong>{period}</strong>, {range} — {about}.</li>",
        "none.periods": "{month} இல் {noun} முகூர்த்தம் இல்லை — {periods}.",
        "none.plain": ("{month} இல் {noun} முகூர்த்தம் இல்லை — இந்த மாதத்தில் எந்த நாளும் திதி, "
                       "நட்சத்திரம், கிழமை, யோக விதிகளைப் பூர்த்தி செய்யவில்லை."),
        "th": "<tr><th>தேதி</th><th>கிழமை</th><th>திதி</th><th>நட்சத்திரம்</th></tr>",
        "nf.title": "முகூர்த்தப் பக்கம் கிடைக்கவில்லை",
        "nf.open": "முகூர்த்தம் தேடலைத் திறக்கவும்",
        "period.chaturmas": "சாதுர்மாஸ்யம்",
        "period_about.chaturmas": ("சயன (தேவசயனி) ஏகாதசி முதல் உத்தான (பிரபோதினி) ஏகாதசி வரை, "
                                   "மகாவிஷ்ணு யோக நித்திரையில் இருக்கும் காலம்"),
        "period.kharmas": "கர்மாஸ்",
        "period_about.kharmas": "சூரியன் தனுசு (மார்கழி) அல்லது மீன (பங்குனி) ராசியில் இருக்கும் காலம்",
        "period.adhik_maas": "அதிக மாதம்",
        "period_about.adhik_maas": "சூரியன் ராசி மாறாத (சங்கராந்தி இல்லாத) கூடுதல் சந்திர மாதம்",
        "period.pitru_paksha": "மகாளய பட்சம்",
        "period_about.pitru_paksha": ("பாத்ரபத பௌர்ணமி முதல் மகாளய அமாவாசை வரை, முன்னோர்களுக்குச் "
                                      "சிரார்த்தம் செய்யும் பதினைந்து நாட்கள்"),
        "period.shukra_asta": "சுக்கிர அஸ்தமனம்",
        "period_about.shukra_asta": ("சுக்கிரன் சூரியனுக்கு மிக அருகில் இருந்து கண்ணுக்குத் தெரியாத காலம், "
                                     "முன்னும் பின்னும் 3 நாட்கள் சேர்த்து"),
        "period.guru_asta": "குரு அஸ்தமனம்",
        "period_about.guru_asta": ("குரு சூரியனுக்கு மிக அருகில் இருந்து கண்ணுக்குத் தெரியாத காலம், "
                                   "முன்னும் பின்னும் 3 நாட்கள் சேர்த்து"),
    },
    # Malayalam (DIVASTRO-123). Asta = മൗഢ്യം, as Kerala panchangams print it.
    "ml": {
        "kind.vivah": "വിവാഹ മുഹൂർത്തം",
        "kind.griha-pravesh": "ഗൃഹപ്രവേശ മുഹൂർത്തം",
        "noun.vivah": "വിവാഹ",
        "noun.griha-pravesh": "ഗൃഹപ്രവേശ",
        "title": "{name} {year}: ശുഭദിനങ്ങൾ (ന്യൂഡൽഹി) | {brand}",
        "h1": "{name} {year}: ശുഭദിനങ്ങൾ",
        "desc": ("{year}-ലെ {name} — ന്യൂഡൽഹിക്കുള്ള മാസം തിരിച്ചുള്ള ശുഭദിനങ്ങൾ, തിഥിയും "
                 "നക്ഷത്രവും സഹിതം. ആകെ {count} ദിവസങ്ങൾ; ചാതുർമാസ്യം, ഖർമാസം, അധിക മാസം, "
                 "പിതൃപക്ഷം, ഗുരു-ശുക്ര മൗഢ്യം എന്നിവയുടെ വിശദീകരണവും."),
        "sub": '<p class="hi">{year}-ലെ {noun} ശുഭദിനങ്ങൾ — മാസം തിരിച്ച്</p>',
        "place": "{label} · IST",
        "intro": ("<p>പഞ്ചാംഗപ്രകാരം {year}-ൽ ന്യൂഡൽഹിക്ക് <strong>{count}</strong> "
                  "{noun} മുഹൂർത്ത ദിവസങ്ങളുണ്ട്; അവ വരുന്ന മാസങ്ങൾ: {months}. ഓരോ ദിവസവും "
                  "സൂര്യോദയ സമയത്തെ തിഥി, നക്ഷത്രം, ആഴ്ച, യോഗം, ഭദ്ര (വിഷ്ടി കരണം) എന്നീ "
                  "ശാസ്ത്രനിയമങ്ങൾ പ്രകാരം പരിശോധിച്ചതാണ്; ചാതുർമാസ്യം, ഖർമാസം, അധിക മാസം, "
                  "പിതൃപക്ഷം, ഗുരു-ശുക്ര മൗഢ്യം എന്നീ കാലങ്ങൾ ഒഴിവാക്കിയിട്ടുണ്ട്.</p>"),
        "note": ("<p><strong>സമയം നഗരത്തിനനുസരിച്ച് മാറും.</strong> ഈ ദിവസങ്ങൾ ന്യൂഡൽഹിയിലെ "
                 "സൂര്യോദയം അടിസ്ഥാനമാക്കി കണക്കാക്കിയതാണ്; മറ്റൊരിടത്ത് ഒരു തിഥിയോ നക്ഷത്രമോ "
                 "വേറൊരു ദിവസം മാറിയേക്കാം. വിവാഹത്തിനോ ഗൃഹപ്രവേശത്തിനോ ഉള്ള കൃത്യമായ മുഹൂർത്തം "
                 "(ലഗ്നം) കുടുംബ ജ്യോതിഷിയെക്കൊണ്ട് ഉറപ്പിക്കുക. നിങ്ങളുടെ നഗരത്തിലെ ദിവസങ്ങൾ "
                 "മുഹൂർത്തം കണ്ടെത്താം ടൂളിൽ നോക്കൂ.</p>"),
        "cta": "നിങ്ങളുടെ നഗരത്തിലെ മുഹൂർത്തം കണ്ടെത്തൂ — സൗജന്യം",
        "crumb": "{name} {year}",
        "more": "കൂടുതൽ മുഹൂർത്ത ദിവസങ്ങൾ",
        "link.kind": "{name} {year}",
        "link.panchang": "ഇന്നത്തെ പഞ്ചാംഗം",
        "link.milan": "ജാതകപ്പൊരുത്തം",
        "periods.h2": "{year}-ൽ {noun} മുഹൂർത്തമില്ലാത്ത കാലങ്ങൾ",
        "periods.intro": ("ഈ കാലങ്ങളിൽ {noun} മുഹൂർത്തം നിശ്ചയിക്കാറില്ല. ദിവസങ്ങൾ "
                          "പഞ്ചാംഗത്തിൽ നിന്ന് കണക്കാക്കിയതാണ് (ന്യൂഡൽഹി, സൂര്യോദയം):"),
        "periods.item": "<li><strong>{period}</strong>, {range} — {about}.</li>",
        "none.periods": "{month}-ൽ {noun} മുഹൂർത്തമില്ല — {periods}.",
        "none.plain": ("{month}-ൽ {noun} മുഹൂർത്തമില്ല — ഈ മാസം ഒരു ദിവസവും തിഥി, നക്ഷത്രം, "
                       "ആഴ്ച, യോഗം എന്നീ നിയമങ്ങൾ പാലിക്കുന്നില്ല."),
        "th": "<tr><th>തീയതി</th><th>ആഴ്ച</th><th>തിഥി</th><th>നക്ഷത്രം</th></tr>",
        "nf.title": "മുഹൂർത്ത പേജ് കണ്ടെത്തിയില്ല",
        "nf.open": "മുഹൂർത്തം കണ്ടെത്താം തുറക്കുക",
        "period.chaturmas": "ചാതുർമാസ്യം",
        "period_about.chaturmas": ("ശയന ഏകാദശി മുതൽ ഉത്ഥാന (പ്രബോധിനി) ഏകാദശി വരെ, "
                                   "മഹാവിഷ്ണു യോഗനിദ്രയിലായിരിക്കുന്ന കാലം"),
        "period.kharmas": "ഖർമാസം",
        "period_about.kharmas": "സൂര്യൻ ധനു അല്ലെങ്കിൽ മീനം രാശിയിൽ നിൽക്കുന്ന കാലം",
        "period.adhik_maas": "അധിക മാസം",
        "period_about.adhik_maas": "സൂര്യസംക്രമം ഇല്ലാത്ത അധിക ചാന്ദ്രമാസം",
        "period.pitru_paksha": "പിതൃപക്ഷം",
        "period_about.pitru_paksha": ("ഭാദ്രപദ പൗർണമി മുതൽ മഹാലയ അമാവാസി വരെ, "
                                      "ശ്രാദ്ധം അനുഷ്ഠിക്കുന്ന രണ്ടാഴ്ച"),
        "period.shukra_asta": "ശുക്ര മൗഢ്യം",
        "period_about.shukra_asta": ("ശുക്രൻ സൂര്യനോട് വളരെ അടുത്തായി കാണാനാവാത്ത കാലം, "
                                     "മുമ്പും ശേഷവും 3 ദിവസം ഉൾപ്പെടെ"),
        "period.guru_asta": "ഗുരു മൗഢ്യം",
        "period_about.guru_asta": ("വ്യാഴം (ഗുരു) സൂര്യനോട് വളരെ അടുത്തായി കാണാനാവാത്ത കാലം, "
                                   "മുമ്പും ശേഷവും 3 ദിവസം ഉൾപ്പെടെ"),
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
        "place": "{label} · ভারতীয় সময়",
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
        "place": "{label} · ଭାରତୀୟ ସମୟ",
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

# DIVASTRO-141: /muhurat/mundan-<year>. Mundan (chudakarma) has its own rules in
# astro/muhurat.EVENT_RULES["mundan"]; "rules.body" prints them from the engine
# (muhurat_pages._rules_section) so the page can never disagree with the tool.
# Placeholders of rules.body (comma-joined names in the language, from
# names_<code>): {tithi_bad} {tithi_good} {nak_good} {nak_bad} {yoga_bad}
# {vara_good} {vara_bad}. "note.mundan" replaces "note" (which names a wedding)
# on this kind's page only.
MUNDAN: dict[str, dict[str, str]] = {
    "en": {
        "kind.mundan": "Mundan Muhurat",
        "noun.mundan": "mundan",
        "note.mundan": ("<p><strong>Timings vary by city.</strong> These dates are reckoned from New "
                        "Delhi's sunrise; elsewhere a tithi or nakshatra can change on a different "
                        "day. The exact muhurat for the mundan (chudakarma) should be fixed by your "
                        "family priest. Check your own city in the Muhurat Finder.</p>"),
        "rules.h2": "{name} {year}: the rules these dates follow",
        "rules.body": (
            "<p>Mundan (chudakarma, the first haircut) is judged by its own rules, not a "
            "wedding's. A day is listed only when none of the barred items below applies and it "
            "falls in a favourable nakshatra:</p><ul>"
            "<li><strong>Barred tithis:</strong> {tithi_bad}.</li>"
            "<li><strong>Favoured tithis</strong> (in either paksha): {tithi_good}; the others are "
            "neutral.</li>"
            "<li><strong>Favourable nakshatras</strong> (every date below falls in one): "
            "{nak_good}.</li>"
            "<li><strong>Barred nakshatras:</strong> {nak_bad}.</li>"
            "<li><strong>Barred yoga and karana:</strong> {yoga_bad}, and Bhadra (Vishti).</li>"
            "<li><strong>Weekdays:</strong> {vara_good} are favoured; {vara_bad} count against a "
            "day without ruling it out, so a few such dates appear - skip them if your family "
            "avoids those days.</li></ul>"),
    },
    "hi": {
        "kind.mundan": "मुंडन मुहूर्त",
        "note.mundan": ("<p><strong>ध्यान दें:</strong> ये तिथियां नई दिल्ली के सूर्योदय पर आधारित हैं। "
                        "दूसरे शहर में तिथि-नक्षत्र का समय बदलता है, और मुंडन (चूड़ाकरण) का सटीक "
                        "मुहूर्त परिवार के पंडित जी से अवश्य दिखवाएं। अपने शहर की तिथियां मुहूर्त "
                        "खोजक में देखें।</p>"),
        "rules.h2": "{name} {year}: ये तिथियां किन नियमों से चुनी गई हैं",
        "rules.body": (
            "<p>मुंडन (चूड़ाकरण, पहली बार बाल उतारना) के अपने नियम हैं, विवाह के नियमों से अलग। कोई दिन तभी "
            "सूची में आता है जब नीचे के वर्जित में से कुछ भी लागू न हो और वह शुभ नक्षत्र में पड़े:</p><ul>"
            "<li><strong>वर्जित तिथियां:</strong> {tithi_bad}।</li>"
            "<li><strong>शुभ तिथियां</strong> (दोनों पक्षों में): {tithi_good}; बाकी सामान्य हैं।</li>"
            "<li><strong>शुभ नक्षत्र</strong> (नीचे की हर तिथि इनमें से किसी एक में है): {nak_good}।</li>"
            "<li><strong>वर्जित नक्षत्र:</strong> {nak_bad}।</li>"
            "<li><strong>वर्जित योग व करण:</strong> {yoga_bad} और भद्रा (विष्टि)।</li>"
            "<li><strong>वार:</strong> {vara_good} शुभ माने गए हैं; {vara_bad} दिन के विरुद्ध गिने जाते हैं "
            "पर उसे सूची से बाहर नहीं करते, इसलिए ऐसे कुछ दिन सूची में आ जाते हैं - परिवार में ये वार "
            "वर्जित हों तो उन्हें छोड़ दें।</li></ul>"),
    },
    "kn": {
        "kind.mundan": "ಮುಂಡನ ಮುಹೂರ್ತ",
        "noun.mundan": "ಮುಂಡನಕ್ಕೆ",
        "note.mundan": ("<p><strong>ಸಮಯ ನಗರದಿಂದ ನಗರಕ್ಕೆ ಬದಲಾಗುತ್ತದೆ.</strong> ಈ ದಿನಾಂಕಗಳನ್ನು "
                        "ನವದೆಹಲಿಯ ಸೂರ್ಯೋದಯದಿಂದ ಲೆಕ್ಕಹಾಕಲಾಗಿದೆ; ಬೇರೆಡೆ ತಿಥಿ ಅಥವಾ ನಕ್ಷತ್ರ ಬೇರೆ "
                        "ದಿನದಲ್ಲಿ ಬದಲಾಗಬಹುದು. ಮುಂಡನ (ಚೌಲ) ದ ನಿಖರ ಮುಹೂರ್ತವನ್ನು ನಿಮ್ಮ ಕುಟುಂಬದ "
                        "ಪುರೋಹಿತರಿಂದ ನಿಗದಿಪಡಿಸಿಕೊಳ್ಳಿ. ನಿಮ್ಮ ನಗರದ ದಿನಾಂಕಗಳನ್ನು ‘ಮುಹೂರ್ತ ಹುಡುಕಿ’ಯಲ್ಲಿ "
                        "ನೋಡಿ.</p>"),
        "rules.h2": "{name} {year}: ಈ ದಿನಾಂಕಗಳು ಅನುಸರಿಸುವ ನಿಯಮಗಳು",
        "rules.body": (
            "<p>ಮುಂಡನ (ಚೌಲ, ಮೊದಲ ಕ್ಷೌರ)ಕ್ಕೆ ಮದುವೆಗಿಂತ ಬೇರೆಯೇ ನಿಯಮಗಳಿವೆ. ಕೆಳಗಿನ ನಿಷಿದ್ಧಗಳಲ್ಲಿ ಯಾವುದೂ "
            "ಅನ್ವಯಿಸದೆ, ಶುಭ ನಕ್ಷತ್ರದಲ್ಲಿ ಬಂದರೆ ಮಾತ್ರ ದಿನವನ್ನು ಪಟ್ಟಿ ಮಾಡಲಾಗಿದೆ:</p><ul>"
            "<li><strong>ನಿಷಿದ್ಧ ತಿಥಿಗಳು:</strong> {tithi_bad}.</li>"
            "<li><strong>ಶುಭ ತಿಥಿಗಳು</strong> (ಎರಡೂ ಪಕ್ಷಗಳಲ್ಲಿ): {tithi_good}; ಉಳಿದವು ಸಾಮಾನ್ಯ.</li>"
            "<li><strong>ಶುಭ ನಕ್ಷತ್ರಗಳು</strong> (ಕೆಳಗಿನ ಪ್ರತಿ ದಿನಾಂಕವೂ ಇವುಗಳಲ್ಲಿ ಒಂದರಲ್ಲಿದೆ): {nak_good}.</li>"
            "<li><strong>ನಿಷಿದ್ಧ ನಕ್ಷತ್ರಗಳು:</strong> {nak_bad}.</li>"
            "<li><strong>ನಿಷಿದ್ಧ ಯೋಗ ಮತ್ತು ಕರಣ:</strong> {yoga_bad} ಹಾಗೂ ಭದ್ರಾ (ವಿಷ್ಟಿ).</li>"
            "<li><strong>ವಾರಗಳು:</strong> {vara_good} ಶುಭ; {vara_bad} ದಿನದ ವಿರುದ್ಧ ಎಣಿಕೆಯಾಗುತ್ತವೆ, ಆದರೆ ದಿನವನ್ನು "
            "ಹೊರಗಿಡುವುದಿಲ್ಲ; ಆದ್ದರಿಂದ ಅಂಥ ಕೆಲವು ದಿನಗಳು ಪಟ್ಟಿಯಲ್ಲಿ ಬರುತ್ತವೆ - ನಿಮ್ಮ ಕುಟುಂಬ ಆ ವಾರಗಳನ್ನು "
            "ವರ್ಜಿಸಿದರೆ ಬಿಟ್ಟುಬಿಡಿ.</li></ul>"),
    },
    "te": {
        "kind.mundan": "ముండన ముహూర్తాలు",
        "noun.mundan": "ముండన",
        "note.mundan": ("<p><strong>సమయాలు ఊరిని బట్టి మారుతాయి.</strong> ఈ తేదీలు న్యూఢిల్లీ "
                        "సూర్యోదయం ఆధారంగా లెక్కించినవి; ఇతర ప్రాంతాల్లో తిథి లేదా నక్షత్రం వేరే రోజున "
                        "మారవచ్చు. ముండన (చౌలం) కు ఖచ్చితమైన ముహూర్తాన్ని మీ కుటుంబ పురోహితుల ద్వారా "
                        "నిర్ణయించుకోండి. మీ ఊరి తేదీలను ‘ముహూర్తం వెతకండి’లో చూడండి.</p>"),
        "rules.h2": "{name} {year}: ఈ తేదీలు అనుసరించే నియమాలు",
        "rules.body": (
            "<p>ముండన (చౌలం, మొదటి కేశఖండన)కు వివాహానికి భిన్నమైన సొంత నియమాలు ఉన్నాయి. కింది నిషిద్ధాల్లో ఏదీ "
            "వర్తించకుండా, శుభ నక్షత్రంలో వస్తేనే రోజును జాబితాలో చేర్చాం:</p><ul>"
            "<li><strong>నిషిద్ధ తిథులు:</strong> {tithi_bad}.</li>"
            "<li><strong>శుభ తిథులు</strong> (రెండు పక్షాల్లో): {tithi_good}; మిగతావి సాధారణం.</li>"
            "<li><strong>శుభ నక్షత్రాలు</strong> (కింది ప్రతి తేదీ వీటిలో ఒకదానిలో ఉంది): {nak_good}.</li>"
            "<li><strong>నిషిద్ధ నక్షత్రాలు:</strong> {nak_bad}.</li>"
            "<li><strong>నిషిద్ధ యోగం, కరణం:</strong> {yoga_bad}, భద్ర (విష్టి).</li>"
            "<li><strong>వారాలు:</strong> {vara_good} శుభం; {vara_bad} రోజుకు వ్యతిరేకంగా లెక్కవేస్తారు కానీ రోజును "
            "పూర్తిగా తొలగించవు, అందుకే అలాంటి కొన్ని తేదీలు కనిపిస్తాయి - మీ కుటుంబంలో ఆ వారాలు వర్జ్యమైతే "
            "వదిలేయండి.</li></ul>"),
    },
    "ta": {
        "kind.mundan": "முண்டன முகூர்த்தம்",
        "noun.mundan": "முண்டன",
        "note.mundan": ("<p><strong>ஊருக்கு ஊர் நேரம் மாறும்.</strong> இந்த நாட்கள் புது தில்லியின் "
                        "சூரிய உதயத்தை வைத்துக் கணக்கிடப்பட்டவை; வேறு ஊரில் ஒரு திதியோ நட்சத்திரமோ "
                        "வேறு நாளில் மாறலாம். முண்டன (சௌளம்) முகூர்த்தத்தை உங்கள் குடும்ப புரோகிதரிடம் "
                        "உறுதி செய்துகொள்ளுங்கள். உங்கள் ஊருக்கான நாட்களை முகூர்த்தம் தேடலில் பாருங்கள்.</p>"),
        "rules.h2": "{name} {year}: இந்த நாட்கள் பின்பற்றும் விதிகள்",
        "rules.body": (
            "<p>முண்டனத்துக்கு (சௌளம், முதல் முடி எடுத்தல்) திருமணத்திலிருந்து வேறுபட்ட சொந்த விதிகள் உள்ளன. கீழே உள்ள "
            "விலக்குகளில் எதுவும் பொருந்தாமல், நல்ல நட்சத்திரத்தில் வந்தால் மட்டுமே நாள் பட்டியலில் சேர்க்கப்படும்:</p><ul>"
            "<li><strong>விலக்கப்பட்ட திதிகள்:</strong> {tithi_bad}.</li>"
            "<li><strong>நல்ல திதிகள்</strong> (இரு பட்சங்களிலும்): {tithi_good}; மற்றவை சாதாரணம்.</li>"
            "<li><strong>நல்ல நட்சத்திரங்கள்</strong> (கீழுள்ள ஒவ்வொரு நாளும் இவற்றில் ஒன்றில் உள்ளது): {nak_good}.</li>"
            "<li><strong>விலக்கப்பட்ட நட்சத்திரங்கள்:</strong> {nak_bad}.</li>"
            "<li><strong>விலக்கப்பட்ட யோகம், கரணம்:</strong> {yoga_bad}, பத்ரா (விஷ்டி).</li>"
            "<li><strong>கிழமைகள்:</strong> {vara_good} நல்லவை; {vara_bad} நாளுக்கு எதிராகக் கணக்கிடப்படும், ஆனால் "
            "நாளை முழுமையாக நீக்காது; அதனால் அத்தகைய சில நாட்கள் தென்படும் - உங்கள் குடும்பத்தில் அந்தக் கிழமைகள் "
            "விலக்கப்பட்டால் தவிர்த்துவிடுங்கள்.</li></ul>"),
    },
    "ml": {
        "kind.mundan": "മുണ്ഡന മുഹൂർത്തം",
        "noun.mundan": "മുണ്ഡന",
        "note.mundan": ("<p><strong>സമയം നഗരത്തിനനുസരിച്ച് മാറും.</strong> ഈ തീയതികൾ ന്യൂഡൽഹിയിലെ "
                        "സൂര്യോദയം അടിസ്ഥാനമാക്കി കണക്കാക്കിയതാണ്; മറ്റിടങ്ങളിൽ തിഥിയോ നക്ഷത്രമോ മറ്റൊരു "
                        "ദിവസം മാറാം. മുണ്ഡനത്തിന്റെ (ചൗളം) കൃത്യമായ മുഹൂർത്തം നിങ്ങളുടെ കുടുംബ പുരോഹിതനെക്കൊണ്ട് "
                        "നിശ്ചയിപ്പിക്കുക. നിങ്ങളുടെ നഗരത്തിലെ തീയതികൾ ‘മുഹൂർത്ത ഫൈൻഡറി’ൽ കാണുക.</p>"),
        "rules.h2": "{name} {year}: ഈ തീയതികൾ പാലിക്കുന്ന നിയമങ്ങൾ",
        "rules.body": (
            "<p>മുണ്ഡനത്തിന് (ചൗളം, ആദ്യ ക്ഷൗരം) വിവാഹത്തിൽ നിന്ന് വ്യത്യസ്തമായ സ്വന്തം നിയമങ്ങളുണ്ട്. താഴെയുള്ള "
            "വർജ്യങ്ങളിൽ ഒന്നും ബാധകമാകാതെ, ശുഭ നക്ഷത്രത്തിൽ വന്നാൽ മാത്രമേ ദിവസം പട്ടികയിൽ ചേർക്കൂ:</p><ul>"
            "<li><strong>വർജ്യ തിഥികൾ:</strong> {tithi_bad}.</li>"
            "<li><strong>ശുഭ തിഥികൾ</strong> (രണ്ടു പക്ഷത്തിലും): {tithi_good}; മറ്റുള്ളവ സാധാരണം.</li>"
            "<li><strong>ശുഭ നക്ഷത്രങ്ങൾ</strong> (താഴെയുള്ള ഓരോ തീയതിയും ഇവയിലൊന്നിലാണ്): {nak_good}.</li>"
            "<li><strong>വർജ്യ നക്ഷത്രങ്ങൾ:</strong> {nak_bad}.</li>"
            "<li><strong>വർജ്യ യോഗവും കരണവും:</strong> {yoga_bad}, ഭദ്ര (വിഷ്ടി).</li>"
            "<li><strong>ആഴ്ചകൾ:</strong> {vara_good} ശുഭം; {vara_bad} ദിവസത്തിന് എതിരായി കണക്കാക്കും, പക്ഷേ ദിവസത്തെ "
            "പൂർണമായി ഒഴിവാക്കില്ല; അതിനാൽ അത്തരം ചില തീയതികൾ കാണാം - നിങ്ങളുടെ കുടുംബത്തിൽ ആ ദിവസങ്ങൾ "
            "വർജ്യമെങ്കിൽ ഒഴിവാക്കുക.</li></ul>"),
    },
    "bn": {
        "kind.mundan": "মুণ্ডনের শুভ মুহূর্ত",
        "noun.mundan": "মুণ্ডনের",
        "note.mundan": ("<p><strong>শহরভেদে সময় বদলায়।</strong> এই দিনগুলি নয়াদিল্লির সূর্যোদয় ধরে "
                        "গণনা করা; অন্য জায়গায় তিথি বা নক্ষত্র অন্য দিনে বদলাতে পারে। মুণ্ডনের (চূড়াকরণ) সঠিক "
                        "মুহূর্ত আপনার পারিবারিক পুরোহিতের কাছ থেকে ঠিক করিয়ে নিন। নিজের শহরের দিন দেখুন শুভ "
                        "মুহূর্ত সন্ধানে।</p>"),
        "rules.h2": "{name} {year}: এই তারিখগুলি যে নিয়ম মেনে বাছা",
        "rules.body": (
            "<p>মুণ্ডনের (চূড়াকরণ, প্রথম চুল কাটা) নিজস্ব নিয়ম আছে, বিবাহের নিয়ম থেকে আলাদা। নিচের নিষিদ্ধ বিষয়ের "
            "কোনোটি না পড়লে এবং শুভ নক্ষত্রে হলেই কেবল দিনটি তালিকায় আসে:</p><ul>"
            "<li><strong>নিষিদ্ধ তিথি:</strong> {tithi_bad}।</li>"
            "<li><strong>শুভ তিথি</strong> (দুই পক্ষেই): {tithi_good}; বাকিগুলি সাধারণ।</li>"
            "<li><strong>শুভ নক্ষত্র</strong> (নিচের প্রতিটি তারিখ এর কোনো একটিতে পড়ে): {nak_good}।</li>"
            "<li><strong>নিষিদ্ধ নক্ষত্র:</strong> {nak_bad}।</li>"
            "<li><strong>নিষিদ্ধ যোগ ও করণ:</strong> {yoga_bad} এবং ভদ্রা (বিষ্টি)।</li>"
            "<li><strong>বার:</strong> {vara_good} শুভ; {vara_bad} দিনের বিপক্ষে গণ্য হয়, কিন্তু দিনটি বাদ দেয় না, "
            "তাই এমন কিছু তারিখ তালিকায় আসে - আপনার পরিবারে ওই বারগুলি নিষিদ্ধ হলে এড়িয়ে যান।</li></ul>"),
    },
    "or": {
        "kind.mundan": "ମୁଣ୍ଡନ ଶୁଭ ମୁହୂର୍ତ୍ତ",
        "noun.mundan": "ମୁଣ୍ଡନର",
        "note.mundan": ("<p><strong>ସହର ଅନୁସାରେ ସମୟ ବଦଳେ।</strong> ଏହି ତାରିଖଗୁଡ଼ିକ ନୂଆଦିଲ୍ଲୀର "
                        "ସୂର୍ଯ୍ୟୋଦୟ ଅନୁସାରେ ଗଣନା କରାଯାଇଛି; ଅନ୍ୟ ସ୍ଥାନରେ ତିଥି ବା ନକ୍ଷତ୍ର ଭିନ୍ନ ଦିନରେ "
                        "ବଦଳିପାରେ। ମୁଣ୍ଡନ (ଚୂଡ଼ାକରଣ)ର ସଠିକ୍ ମୁହୂର୍ତ୍ତ ଆପଣଙ୍କ ପରିବାରର ପୁରୋହିତଙ୍କ ଦ୍ୱାରା "
                        "ସ୍ଥିର କରାନ୍ତୁ। ନିଜ ସହରର ତାରିଖ ଶୁଭ ମୁହୂର୍ତ୍ତ ସନ୍ଧାନରେ ଦେଖନ୍ତୁ।</p>"),
        "rules.h2": "{name} {year}: ଏହି ତାରିଖଗୁଡ଼ିକ ମାନୁଥିବା ନିୟମ",
        "rules.body": (
            "<p>ମୁଣ୍ଡନ (ଚୂଡ଼ାକରଣ, ପ୍ରଥମ କେଶ କାଟିବା)ର ନିଜସ୍ୱ ନିୟମ ଅଛି, ବିବାହର ନିୟମଠାରୁ ଭିନ୍ନ। ତଳେ ଥିବା ନିଷିଦ୍ଧ "
            "ବିଷୟ ମଧ୍ୟରୁ କୌଣସି ପ୍ରଯୁଜ୍ୟ ନହେଲେ ଏବଂ ଶୁଭ ନକ୍ଷତ୍ରରେ ପଡ଼ିଲେ ହିଁ ଦିନଟି ତାଲିକାରେ ଆସେ:</p><ul>"
            "<li><strong>ନିଷିଦ୍ଧ ତିଥି:</strong> {tithi_bad}।</li>"
            "<li><strong>ଶୁଭ ତିଥି</strong> (ଉଭୟ ପକ୍ଷରେ): {tithi_good}; ବାକି ସାଧାରଣ।</li>"
            "<li><strong>ଶୁଭ ନକ୍ଷତ୍ର</strong> (ତଳର ପ୍ରତ୍ୟେକ ତାରିଖ ଏଥିରୁ ଗୋଟିଏରେ ପଡ଼େ): {nak_good}।</li>"
            "<li><strong>ନିଷିଦ୍ଧ ନକ୍ଷତ୍ର:</strong> {nak_bad}।</li>"
            "<li><strong>ନିଷିଦ୍ଧ ଯୋଗ ଓ କରଣ:</strong> {yoga_bad} ଏବଂ ଭଦ୍ରା (ବିଷ୍ଟି)।</li>"
            "<li><strong>ବାର:</strong> {vara_good} ଶୁଭ; {vara_bad} ଦିନ ବିପକ୍ଷରେ ଗଣାଯାଏ, କିନ୍ତୁ ଦିନଟିକୁ ବାଦ ଦିଏ ନାହିଁ, "
            "ତେଣୁ ଏପରି କିଛି ତାରିଖ ତାଲିକାରେ ଆସେ - ଆପଣଙ୍କ ପରିବାରରେ ସେହି ବାର ନିଷିଦ୍ଧ ହେଲେ ଛାଡ଼ିଦିଅନ୍ତୁ।</li></ul>"),
    },
}
# DIVASTRO-143: pa/ne/as/mr/gu live in app/lang_data/<code>.py; overlaid here as if written inline.
from . import lang_data  # noqa: E402
lang_data.merge("MUHURAT_TEXT", TEXT)
lang_data.merge("MUHURAT_MUNDAN", MUNDAN)

for _l, _t in MUNDAN.items():
    TEXT[_l].update(_t)

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

# DIVASTRO-143: pa/ne/as/mr/gu live in app/lang_data/<code>.py; overlaid here as if written inline.
from . import lang_data  # noqa: E402
lang_data.merge("MUHURAT_MONTHS", MONTHS)
