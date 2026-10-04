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
