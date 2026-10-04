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
        "place": "புது தில்லி, டெல்லி · IST",
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
        "place": "ന്യൂഡൽഹി, ഡൽഹി · IST",
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
