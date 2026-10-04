"""The text of the /nakshatra and /rashi pages (nakshatra_pages.py), per language.

TRANSLATORS: this file is data. To translate these pages into, say, Kannada,
add a "kn" dict to TEXT with any subset of the "en" keys (and "kn" entries to
nakshatra_text.NAKSHATRA_TRAITS / RASHI_TRAITS), then add "kn" to
nakshatra_pages.TRANSLATED. A key you leave out falls back to the "_native"
template and then to English.

* Templates keep their `{placeholders}`; word order around them is yours.
* Values are HTML unless marked "plain text": keep the tags, write `&amp;`
  for a literal "&". Placeholder values arrive already escaped.
* Nakshatra, rashi, graha, gana, yoni, nadi and varna names are NOT here:
  they come from app/astro/names_<code>.py (Hindi: the engines' own tables).
"""

from __future__ import annotations

from .astro import matching

TEXT: dict[str, dict[str, str]] = {
    "en": {
        # shared ------------------------------------------------------------
        # plain text; a language without it uses i18n.CHROME "home"
        # "home": "",
        "kundali_cta": "Get your free kundali — find your exact birth nakshatra and Moon sign",
        "more.heading": "More free tools",
        "more.naks": "All 27 nakshatras",
        "more.rashis": "All 12 rashis",
        "more.milan": "Naam se Kundali Milan",
        "more.kundali_milan": "Kundali Milan (36 guna)",
        "more.rashifal": "Today's Rashifal",
        "more.panchang": "Today's Panchang",
        "list.naks": "All 27 nakshatras",
        "list.rashis": "All 12 rashis",
        # a rashi in running text / lists: {name} (Mesh / मेष / names_<code> RASHI) {english} (Aries)
        "sign": "{name} ({english})",
        "sign.pill": "{name} · {english}",
        # today's nakshatra box: {name} {href} {pan}
        "today.same": "<strong>Today the Moon is in {name} (at sunrise in New Delhi).</strong>",
        "today.other": ("Today's nakshatra is <a href=\"{href}\"><strong>{name}"
                        "</strong></a> (at sunrise in New Delhi)."),
        "today.tail": (' Its end time, the tithi and Rahu Kaal are on <a href="{pan}">today\'s '
                       "Panchang</a>."),
        "crumb.naks": "Nakshatras",
        "crumb.rashis": "Rashis",
        "nf.nak": "Nakshatra not found",
        "nf.rashi": "Rashi not found",
        "trait_head": "Nature and traits",
        "gender.male": "male",
        "gender.female": "female",
        "element.Fire": "Fire", "element.Earth": "Earth", "element.Air": "Air",
        "element.Water": "Water",
        "quality.Cardinal": "Movable (Chara)", "quality.Fixed": "Fixed (Sthira)",
        "quality.Mutable": "Dual (Dwiswabhava)",

        # /nakshatra/<slug> -------------------------------------------------
        # plain text: {name} {name_en} {name_hi} {lat} {syl} {span} {lord} {deity}
        #   {deity_short} {gana} {nadi} {yoni} {brand}
        "nak.title": ("{name} Nakshatra — Deity, Lord, Gana, Yoni, Nadi & Name Letters "
                      "({lat}) | {brand}"),
        "nak.desc": ("{name} nakshatra ({name_hi}): {span}, ruled by "
                     "{lord}, deity {deity_short}, {gana} gana, {nadi} nadi, "
                     "{yoni} yoni. Name syllables {lat} and traits."),
        "nak.h1": "<h1>{name} Nakshatra</h1>",
        "nak.sub": '<p class="hi" lang="hi">{name_hi} नक्षत्र</p>',
        "nak.trait_note": ("<p class=\"note\">These are traditional tendencies, not verdicts. Your full "
                           "kundali — ascendant, planets and dasha — gives the personal picture.</p>"),
        # facts table: row labels and values
        "f.number": "Number", "f.number_v": "{n} of 27",
        "f.span": "Span (sidereal)",
        "f.rashi": "Rashi",
        "f.lord": "Ruling planet (Vimshottari lord)",
        "f.lord_v": "{lord} <small>{years}-year mahadasha</small>",
        "f.deity": "Deity",
        "f.symbol": "Symbol",
        "f.gana": "Gana", "f.gana_v": '{gana} <small lang="hi">{gana_hi}</small>',
        "f.yoni": "Yoni (animal)",
        "f.nadi": "Nadi",
        "f.varna": "Varna (from its rashi, as used in Guna Milan)",
        "f.syl": "Name syllables (namakshar)",
        "f.syl_v": '<span class="syl" lang="hi">{syl}</span> <small>{lat}</small>',
        # the pada table
        "pada.title": "The four padas and their name syllables",
        "pada.head": "<tr><th>Pada</th><th>Span</th><th>Rashi</th><th>Name syllable</th></tr>",
        "pada.note": ("<p class=\"note\">Traditionally a child's name begins with the syllable of the pada the "
                      "Moon occupied at birth (namakshar). Syllables follow the 108-pada Swar Siddhanta list "
                      "(the Avakahada Chakra) as published by Drik Panchang.</p>"),
        # related links (plain text): {name}
        "rel.heading": "Related",
        "rel.rashifal": "Today's {name} Rashifal",

        # /nakshatra --------------------------------------------------------
        "ni.title": "The 27 Nakshatras — Lords, Deities, Gana & Name Syllables | {brand}",
        "ni.desc": ("All 27 nakshatras from Ashwini to Revati: span, rashi, ruling planet, "
                    "deity, gana, yoni, nadi and the name syllables of all four padas — "
                    "consistent with our Kundali Milan tables."),
        "ni.h1": "<h1>The 27 Nakshatras</h1>",
        "ni.sub": '<p class="hi" lang="hi">27 नक्षत्र</p>',
        "ni.intro": ("<p>Vedic astrology divides the zodiac into 27 nakshatras (lunar mansions) of "
                     "13°20′ each, and each nakshatra into four padas of 3°20′. The 108 padas fall "
                     "exactly nine to a sign across the 12 rashis. Your birth nakshatra is the one the "
                     "Moon occupied when you were born: it starts your Vimshottari dasha and drives "
                     "the Tara, Yoni, Gana and Nadi kootas of Kundali Milan.</p>"),
        "ni.head": ("<tr><th>#</th><th>Nakshatra</th><th>Rashi</th><th>Lord</th><th>Gana</th>"
                    "<th>Name syllables</th></tr>"),

        # /rashi/<slug> -----------------------------------------------------
        # plain text: {name} {name_en} {name_hi} {english} {lord} {element} {element_lower}
        #   {quality} {quality_lower} {syl} {lat} {brand}
        "rs.title": ("{name} Rashi ({english}) — Lord, Element, Nakshatras & Name Letters | "
                     "{brand}"),
        "rs.desc": ("{name} rashi ({english} Moon sign, {name_hi}): ruled by {lord}, "
                    "{element_lower} element, {quality_lower}"
                    " quality. Its 9 nakshatra padas, name syllables ({lat}) and traits."),
        "rs.h1": "<h1>{name} Rashi — {english} Moon Sign</h1>",
        "rs.sub": '<p class="hi" lang="hi">{name_hi} राशि</p>',
        "rs.today": "Read today's {name} Rashifal",
        "rs.note": ("<p class=\"note\">In Vedic astrology \"rashi\" usually means the Moon sign — the sign "
                    "the Moon occupied at birth, in the sidereal zodiac. It is often different from a "
                    "Western sun sign.</p>"),
        "r.number": "Number", "r.number_v": "{n} of 12",
        "r.span": "Span (sidereal zodiac)",
        "r.lord": "Sign lord",
        "r.element": "Element",
        "r.quality": "Quality",
        "r.varna": "Varna (used in Guna Milan)",
        "r.naks": "Nakshatras",
        "r.syl": "Name syllables (namakshar)",
        "r.syl_v": '<span class="syl" lang="hi">{syl}</span>',
        "rp.title": "The nine nakshatra padas in this sign",
        "rp.head": "<tr><th>Nakshatra</th><th>Pada</th><th>Degrees in sign</th><th>Syllable</th></tr>",

        # /rashi ------------------------------------------------------------
        "ri.title": "The 12 Rashis — Lords, Elements, Nakshatras & Name Letters | {brand}",
        "ri.desc": ("All 12 rashis (Vedic Moon signs) from Mesh to Meen: sign lord, element, "
                    "quality, the nine nakshatra padas in each and their name syllables "
                    "(namakshar)."),
        "ri.h1": "<h1>The 12 Rashis (Moon Signs)</h1>",
        "ri.sub": '<p class="hi" lang="hi">12 राशियाँ</p>',
        "ri.intro": ("<p>Each rashi spans 30° of the sidereal zodiac and holds exactly nine nakshatra "
                     "padas. Your rashi is your Moon sign — the sign the Moon occupied at birth — and "
                     "it is what rashifal, Sade Sati and Kundali Milan are read from.</p>"),
        "ri.head": ("<tr><th>Rashi</th><th>Lord</th><th>Element</th><th>Nakshatras</th>"
                    "<th>Name syllables</th></tr>"),
        # the name cell: {name} {name_en} {english}
        "ri.name": "{name} <small>{english}</small>",
    },

    "hi": {
        "home": "मुख्य पृष्ठ",
        "kundali_cta": "अपनी मुफ़्त कुंडली बनाएँ — जानें आपका जन्म नक्षत्र और चंद्र राशि",
        "more.heading": "और भी",
        "more.naks": "सभी 27 नक्षत्र",
        "more.rashis": "सभी 12 राशियाँ",
        "more.milan": "नाम से कुंडली मिलान",
        "more.kundali_milan": "कुंडली मिलान (36 गुण)",
        "more.rashifal": "आज का राशिफल",
        "more.panchang": "आज का पंचांग",
        "list.naks": "सभी 27 नक्षत्र",
        "list.rashis": "सभी 12 राशियाँ",
        "today.same": ("<strong>आज (नई दिल्ली में सूर्योदय के समय) चंद्रमा {name} नक्षत्र में है।"
                       "</strong>"),
        "today.other": ('आज का नक्षत्र (नई दिल्ली में सूर्योदय के समय) '
                        '<a href="{href}"><strong>{name}</strong></a> है।'),
        "today.tail": ' नक्षत्र का समाप्ति-समय, तिथि और राहु काल <a href="{pan}">आज के पंचांग</a> में देखें।',
        "crumb.naks": "नक्षत्र",
        "crumb.rashis": "राशियाँ",
        "nf.nak": "नक्षत्र नहीं मिला",
        "nf.rashi": "राशि नहीं मिली",
        "trait_head": "स्वभाव",
        "gender.male": "पुरुष",
        "gender.female": "स्त्री",
        "element.Fire": "अग्नि", "element.Earth": "पृथ्वी", "element.Air": "वायु",
        "element.Water": "जल",
        "quality.Cardinal": "चर", "quality.Fixed": "स्थिर", "quality.Mutable": "द्विस्वभाव",

        "nak.title": "{name} नक्षत्र — देवता, स्वामी, गण, योनि, नाड़ी और नामाक्षर ({syl}) | {brand}",
        "nak.desc": ("{name} नक्षत्र ({name_en}): {span}, स्वामी "
                     "{lord}, देवता {deity}, {gana} "
                     "गण, नाड़ी {nadi}। नामाक्षर {syl} और स्वभाव।"),
        "nak.h1": "<h1>{name} नक्षत्र</h1>",
        "nak.sub": '<p class="hi" lang="en">{name_en} Nakshatra</p>',
        "nak.trait_note": ("<p class=\"note\">ये पारंपरिक प्रवृत्तियाँ हैं, निर्णय नहीं। आपकी पूरी कुंडली — "
                           "लग्न, ग्रह और दशा — व्यक्तिगत चित्र देती है।</p>"),
        "f.number": "क्रम", "f.number_v": "27 में से {n}वाँ",
        "f.span": "अंश (निरयण)",
        "f.rashi": "राशि",
        "f.lord": "स्वामी ग्रह (विंशोत्तरी)",
        "f.lord_v": "{lord} <small>महादशा {years} वर्ष</small>",
        "f.deity": "देवता",
        "f.symbol": "प्रतीक",
        "f.gana": "गण",
        "f.yoni": "योनि",
        "f.nadi": "नाड़ी",
        "f.varna": "वर्ण (राशि से, गुण मिलान में)",
        "f.syl": "नामाक्षर",
        "f.syl_v": '<span class="syl">{syl}</span>',
        "pada.title": "चार चरण और नामाक्षर",
        "pada.head": "<tr><th>चरण</th><th>अंश</th><th>राशि</th><th>नामाक्षर</th></tr>",
        "pada.note": ("<p class=\"note\">परंपरा में बच्चे का नाम जन्म नक्षत्र के चरण के अक्षर से रखा जाता है "
                      "(नामाक्षर)। अक्षर ड्रिक पंचांग में प्रकाशित स्वर-सिद्धांत की 108 चरण-अक्षरों की सूची "
                      "(अवकहड़ा चक्र) के अनुसार हैं।</p>"),
        "rel.heading": "संबंधित",
        "rel.rashifal": "आज का {name} राशिफल",

        "ni.title": "27 नक्षत्र — नाम, स्वामी, देवता, गण और नामाक्षर की पूरी सूची | {brand}",
        "ni.desc": ("अश्विनी से रेवती तक सभी 27 नक्षत्र: हर नक्षत्र के अंश, राशि, स्वामी ग्रह, "
                    "देवता, गण, योनि, नाड़ी और चारों चरणों के नामाक्षर — कुंडली मिलान की तालिकाओं "
                    "से मेल खाते हुए।"),
        "ni.h1": "<h1>27 नक्षत्र</h1>",
        "ni.sub": '<p class="hi" lang="en">The 27 Nakshatras</p>',
        "ni.intro": ("<p>वैदिक ज्योतिष में राशि-चक्र 27 नक्षत्रों में बँटा है — हर नक्षत्र 13°20′ का, "
                     "और हर नक्षत्र के 3°20′ के चार चरण। कुल 108 चरण 12 राशियों में बँटते हैं, हर राशि "
                     "में ठीक 9 चरण। आपका जन्म नक्षत्र वह है जिसमें जन्म के समय चंद्रमा था; उसी से "
                     "विंशोत्तरी दशा शुरू होती है और कुंडली मिलान के तारा, योनि, गण और नाड़ी कूट "
                     "देखे जाते हैं।</p>"),
        "ni.head": ("<tr><th>#</th><th>नक्षत्र</th><th>राशि</th><th>स्वामी</th><th>गण</th>"
                    "<th>नामाक्षर</th></tr>"),

        "rs.title": "{name} राशि — स्वामी, तत्व, नक्षत्र, नामाक्षर ({syl}) और स्वभाव | {brand}",
        "rs.desc": ("{name} राशि ({name_en}, {english}): स्वामी {lord}, "
                    "{element} तत्व, {quality} "
                    "स्वभाव। इसके 9 नक्षत्र-चरण, नामाक्षर {syl} और स्वभाव।"),
        "rs.h1": "<h1>{name} राशि</h1>",
        "rs.sub": '<p class="hi" lang="en">{name_en} Rashi · {english}</p>',
        "rs.today": "आज का {name} राशिफल पढ़ें",
        "rs.note": ("<p class=\"note\">वैदिक ज्योतिष में राशि का अर्थ प्रायः चंद्र राशि होता है — जन्म के समय "
                    "चंद्रमा जिस राशि में था। यह अक्सर पश्चिमी सूर्य राशि से अलग होती है।</p>"),
        "r.number": "क्रम", "r.number_v": "12 में से {n}वीं",
        "r.span": "अंश (निरयण राशि-चक्र)",
        "r.lord": "स्वामी ग्रह",
        "r.element": "तत्व",
        "r.quality": "स्वभाव (गुण)",
        "r.varna": "वर्ण (गुण मिलान में)",
        "r.naks": "नक्षत्र",
        "r.syl": "नामाक्षर",
        "r.syl_v": '<span class="syl">{syl}</span>',
        "rp.title": "इस राशि के 9 नक्षत्र-चरण",
        "rp.head": "<tr><th>नक्षत्र</th><th>चरण</th><th>अंश</th><th>नामाक्षर</th></tr>",

        "ri.title": "12 राशियाँ — स्वामी, तत्व, नक्षत्र और नामाक्षर की पूरी सूची | {brand}",
        "ri.desc": ("मेष से मीन तक सभी 12 राशियाँ: हर राशि का स्वामी ग्रह, तत्व, स्वभाव, उसमें "
                    "आने वाले 9 नक्षत्र-चरण और नाम के पहले अक्षर (नामाक्षर)।"),
        "ri.h1": "<h1>12 राशियाँ</h1>",
        "ri.sub": '<p class="hi" lang="en">The 12 Rashis (Moon signs)</p>',
        "ri.intro": ("<p>हर राशि 30° की है और उसमें ठीक 9 नक्षत्र-चरण आते हैं। आपकी राशि (चंद्र राशि) "
                     "वह है जिसमें जन्म के समय चंद्रमा था — राशिफल, साढ़ेसाती और कुंडली मिलान इसी से "
                     "देखे जाते हैं।</p>"),
        "ri.head": "<tr><th>राशि</th><th>स्वामी</th><th>तत्व</th><th>नक्षत्र</th><th>नामाक्षर</th></tr>",
        "ri.name": "{name} <small>{name_en}</small>",
        "sign": "{name}",
        "sign.pill": "{name}",
    },

    "kn": {
        "kundali_cta": "ಉಚಿತ ಜಾತಕ ಪಡೆಯಿರಿ — ನಿಮ್ಮ ನಿಖರ ಜನ್ಮ ನಕ್ಷತ್ರ ಮತ್ತು ಚಂದ್ರ ರಾಶಿ ತಿಳಿಯಿರಿ",
        "more.heading": "ಇನ್ನಷ್ಟು ಉಚಿತ ಸಾಧನಗಳು",
        "more.naks": "ಎಲ್ಲಾ 27 ನಕ್ಷತ್ರಗಳು",
        "more.rashis": "ಎಲ್ಲಾ 12 ರಾಶಿಗಳು",
        "more.milan": "ಹೆಸರಿನಿಂದ ಜಾತಕ ಹೊಂದಾಣಿಕೆ",
        "more.kundali_milan": "ಜಾತಕ ಹೊಂದಾಣಿಕೆ (36 ಗುಣ)",
        "more.rashifal": "ಇಂದಿನ ರಾಶಿ ಭವಿಷ್ಯ",
        "more.panchang": "ಇಂದಿನ ಪಂಚಾಂಗ",
        "list.naks": "ಎಲ್ಲಾ 27 ನಕ್ಷತ್ರಗಳು",
        "list.rashis": "ಎಲ್ಲಾ 12 ರಾಶಿಗಳು",
        "sign": "{name}",
        "sign.pill": "{name}",
        "today.same": ("<strong>ಇಂದು (ನವದೆಹಲಿಯಲ್ಲಿ ಸೂರ್ಯೋದಯದ ಸಮಯದಲ್ಲಿ) ಚಂದ್ರನು {name} ನಕ್ಷತ್ರದಲ್ಲಿದ್ದಾನೆ."
                       "</strong>"),
        "today.other": ('ಇಂದಿನ ನಕ್ಷತ್ರ (ನವದೆಹಲಿಯಲ್ಲಿ ಸೂರ್ಯೋದಯದ ಸಮಯದಲ್ಲಿ) '
                        '<a href="{href}"><strong>{name}</strong></a>.'),
        "today.tail": (' ಅದರ ಮುಕ್ತಾಯ ಸಮಯ, ತಿಥಿ ಮತ್ತು ರಾಹು ಕಾಲವನ್ನು <a href="{pan}">ಇಂದಿನ ಪಂಚಾಂಗದಲ್ಲಿ</a> '
                       "ನೋಡಿ."),
        "crumb.naks": "ನಕ್ಷತ್ರಗಳು",
        "crumb.rashis": "ರಾಶಿಗಳು",
        "nf.nak": "ನಕ್ಷತ್ರ ಸಿಗಲಿಲ್ಲ",
        "nf.rashi": "ರಾಶಿ ಸಿಗಲಿಲ್ಲ",
        "trait_head": "ಸ್ವಭಾವ ಮತ್ತು ಗುಣಲಕ್ಷಣಗಳು",
        "gender.male": "ಪುರುಷ",
        "gender.female": "ಸ್ತ್ರೀ",
        "element.Fire": "ಅಗ್ನಿ", "element.Earth": "ಪೃಥ್ವಿ", "element.Air": "ವಾಯು",
        "element.Water": "ಜಲ",
        "quality.Cardinal": "ಚರ", "quality.Fixed": "ಸ್ಥಿರ", "quality.Mutable": "ದ್ವಿಸ್ವಭಾವ",

        "nak.title": "{name} ನಕ್ಷತ್ರ — ಗುಣಲಕ್ಷಣ, ಅಧಿಪತಿ, ಪಾದ, ಹೆಸರಿನ ಅಕ್ಷರಗಳು | {brand}",
        "nak.desc": ("{name} ನಕ್ಷತ್ರ: {span}, ಅಧಿಪತಿ {lord}, {gana} ಗಣ, {nadi} ನಾಡಿ, "
                     "{yoni} ಯೋನಿ. ನಾಲ್ಕು ಪಾದಗಳ ಹೆಸರಿನ ಅಕ್ಷರಗಳು ಮತ್ತು ಸ್ವಭಾವ."),
        "nak.h1": "<h1>{name} ನಕ್ಷತ್ರ</h1>",
        "nak.sub": '<p class="hi">ನಕ್ಷತ್ರದ ಹೆಸರಿನ ಅಕ್ಷರಗಳು, ಪಾದಗಳು ಮತ್ತು ಸ್ವಭಾವ</p>',
        "nak.trait_note": ("<p class=\"note\">ಇವು ಸಾಂಪ್ರದಾಯಿಕ ಪ್ರವೃತ್ತಿಗಳು, ತೀರ್ಪುಗಳಲ್ಲ. ನಿಮ್ಮ ಪೂರ್ಣ "
                           "ಜಾತಕ — ಲಗ್ನ, ಗ್ರಹಗಳು ಮತ್ತು ದಶೆ — ವೈಯಕ್ತಿಕ ಚಿತ್ರಣವನ್ನು ನೀಡುತ್ತದೆ.</p>"),
        "f.number": "ಕ್ರಮಸಂಖ್ಯೆ", "f.number_v": "27ರಲ್ಲಿ {n}ನೇ",
        "f.span": "ವ್ಯಾಪ್ತಿ (ನಿರಯನ)",
        "f.rashi": "ರಾಶಿ",
        "f.lord": "ಅಧಿಪತಿ ಗ್ರಹ (ವಿಂಶೋತ್ತರಿ)",
        "f.lord_v": "{lord} <small>{years} ವರ್ಷಗಳ ಮಹಾದಶೆ</small>",
        "f.deity": "ದೇವತೆ",
        "f.symbol": "ಸಂಕೇತ",
        "f.gana": "ಗಣ", "f.gana_v": "{gana}",
        "f.yoni": "ಯೋನಿ (ಪ್ರಾಣಿ)",
        "f.nadi": "ನಾಡಿ",
        "f.varna": "ವರ್ಣ (ರಾಶಿಯಿಂದ, ಜಾತಕ ಹೊಂದಾಣಿಕೆಯಲ್ಲಿ ಬಳಸುವಂತೆ)",
        "f.syl": "ಹೆಸರಿನ ಅಕ್ಷರಗಳು (ನಾಮಾಕ್ಷರ)",
        "f.syl_v": '<span class="syl">{syl}</span>',
        "pada.title": "ನಾಲ್ಕು ಪಾದಗಳು ಮತ್ತು ಅವುಗಳ ಹೆಸರಿನ ಅಕ್ಷರಗಳು",
        "pada.head": "<tr><th>ಪಾದ</th><th>ವ್ಯಾಪ್ತಿ</th><th>ರಾಶಿ</th><th>ಹೆಸರಿನ ಅಕ್ಷರ</th></tr>",
        "pada.note": ("<p class=\"note\">ಸಂಪ್ರದಾಯದಂತೆ ಮಗುವಿನ ಹೆಸರು ಜನನದ ಸಮಯದಲ್ಲಿ ಚಂದ್ರನಿದ್ದ ಪಾದದ "
                      "ಅಕ್ಷರದಿಂದ ಆರಂಭವಾಗುತ್ತದೆ (ನಾಮಾಕ್ಷರ). ಅಕ್ಷರಗಳು ದೃಕ್ ಪಂಚಾಂಗ ಪ್ರಕಟಿಸಿರುವ ಸ್ವರ "
                      "ಸಿದ್ಧಾಂತದ 108 ಪಾದಗಳ ಪಟ್ಟಿಯನ್ನು (ಅವಕಹಡಾ ಚಕ್ರ) ಅನುಸರಿಸುತ್ತವೆ.</p>"),
        "rel.heading": "ಸಂಬಂಧಿತ",
        "rel.rashifal": "ಇಂದಿನ {name} ರಾಶಿ ಭವಿಷ್ಯ",

        "ni.title": "27 ನಕ್ಷತ್ರಗಳು — ಅಧಿಪತಿ, ದೇವತೆ, ಗಣ ಮತ್ತು ಹೆಸರಿನ ಅಕ್ಷರಗಳು | {brand}",
        "ni.desc": ("ಅಶ್ವಿನಿಯಿಂದ ರೇವತಿಯವರೆಗೆ ಎಲ್ಲಾ 27 ನಕ್ಷತ್ರಗಳು: ವ್ಯಾಪ್ತಿ, ರಾಶಿ, ಅಧಿಪತಿ ಗ್ರಹ, "
                    "ದೇವತೆ, ಗಣ, ಯೋನಿ, ನಾಡಿ ಮತ್ತು ನಾಲ್ಕೂ ಪಾದಗಳ ಹೆಸರಿನ ಅಕ್ಷರಗಳು — ನಮ್ಮ "
                    "ಜಾತಕ ಹೊಂದಾಣಿಕೆ ಕೋಷ್ಟಕಗಳಿಗೆ ಅನುಗುಣವಾಗಿ."),
        "ni.h1": "<h1>27 ನಕ್ಷತ್ರಗಳು</h1>",
        "ni.sub": '<p class="hi">ನಕ್ಷತ್ರಗಳ ಪಟ್ಟಿ ಮತ್ತು ಹೆಸರಿನ ಅಕ್ಷರಗಳು</p>',
        "ni.intro": ("<p>ವೈದಿಕ ಜ್ಯೋತಿಷ್ಯವು ರಾಶಿಚಕ್ರವನ್ನು ತಲಾ 13°20′ನ 27 ನಕ್ಷತ್ರಗಳಾಗಿ ವಿಭಜಿಸುತ್ತದೆ, "
                     "ಮತ್ತು ಪ್ರತಿ ನಕ್ಷತ್ರವನ್ನು ತಲಾ 3°20′ನ ನಾಲ್ಕು ಪಾದಗಳಾಗಿ. 108 ಪಾದಗಳು 12 ರಾಶಿಗಳಲ್ಲಿ "
                     "ಪ್ರತಿ ರಾಶಿಗೆ ನಿಖರವಾಗಿ ಒಂಬತ್ತರಂತೆ ಹಂಚಿಹೋಗುತ್ತವೆ. ನೀವು ಹುಟ್ಟಿದಾಗ ಚಂದ್ರನಿದ್ದ "
                     "ನಕ್ಷತ್ರವೇ ನಿಮ್ಮ ಜನ್ಮ ನಕ್ಷತ್ರ: ಅದರಿಂದಲೇ ನಿಮ್ಮ ವಿಂಶೋತ್ತರಿ ದಶೆ ಆರಂಭವಾಗುತ್ತದೆ ಮತ್ತು "
                     "ಜಾತಕ ಹೊಂದಾಣಿಕೆಯ ತಾರಾ, ಯೋನಿ, ಗಣ ಮತ್ತು ನಾಡಿ ಕೂಟಗಳು ನಿರ್ಧಾರವಾಗುತ್ತವೆ.</p>"),
        "ni.head": ("<tr><th>#</th><th>ನಕ್ಷತ್ರ</th><th>ರಾಶಿ</th><th>ಅಧಿಪತಿ</th><th>ಗಣ</th>"
                    "<th>ಹೆಸರಿನ ಅಕ್ಷರಗಳು</th></tr>"),

        "rs.title": "{name} ರಾಶಿ ಗುಣಲಕ್ಷಣಗಳು — ಅಧಿಪತಿ, ತತ್ವ, ನಕ್ಷತ್ರಗಳು, ಹೆಸರಿನ ಅಕ್ಷರಗಳು | {brand}",
        "rs.desc": ("{name} ರಾಶಿ (ಚಂದ್ರ ರಾಶಿ): ಅಧಿಪತಿ {lord}, {element} ತತ್ವ, {quality} "
                    "ಸ್ವಭಾವ. ಇದರ 9 ನಕ್ಷತ್ರ ಪಾದಗಳು, ಹೆಸರಿನ ಅಕ್ಷರಗಳು (ನಾಮಾಕ್ಷರ) ಮತ್ತು ಗುಣಲಕ್ಷಣಗಳು."),
        "rs.h1": "<h1>{name} ರಾಶಿ — ಚಂದ್ರ ರಾಶಿ</h1>",
        "rs.sub": '<p class="hi">ರಾಶಿಯ ಗುಣಲಕ್ಷಣಗಳು, ನಕ್ಷತ್ರ ಪಾದಗಳು ಮತ್ತು ಹೆಸರಿನ ಅಕ್ಷರಗಳು</p>',
        "rs.today": "ಇಂದಿನ {name} ರಾಶಿ ಭವಿಷ್ಯ ಓದಿ",
        "rs.note": ("<p class=\"note\">ವೈದಿಕ ಜ್ಯೋತಿಷ್ಯದಲ್ಲಿ “ರಾಶಿ” ಎಂದರೆ ಸಾಮಾನ್ಯವಾಗಿ ಚಂದ್ರ ರಾಶಿ — "
                    "ಜನನದ ಸಮಯದಲ್ಲಿ ನಿರಯನ ರಾಶಿಚಕ್ರದಲ್ಲಿ ಚಂದ್ರನಿದ್ದ ರಾಶಿ. ಇದು ಹಲವು ಬಾರಿ ಪಾಶ್ಚಾತ್ಯ "
                    "ಸೂರ್ಯ ರಾಶಿಗಿಂತ ಭಿನ್ನವಾಗಿರುತ್ತದೆ.</p>"),
        "r.number": "ಕ್ರಮಸಂಖ್ಯೆ", "r.number_v": "12ರಲ್ಲಿ {n}ನೇ",
        "r.span": "ವ್ಯಾಪ್ತಿ (ನಿರಯನ ರಾಶಿಚಕ್ರ)",
        "r.lord": "ರಾಶ್ಯಧಿಪತಿ",
        "r.element": "ತತ್ವ",
        "r.quality": "ಸ್ವಭಾವ",
        "r.varna": "ವರ್ಣ (ಜಾತಕ ಹೊಂದಾಣಿಕೆಯಲ್ಲಿ ಬಳಸುವ)",
        "r.naks": "ನಕ್ಷತ್ರಗಳು",
        "r.syl": "ಹೆಸರಿನ ಅಕ್ಷರಗಳು (ನಾಮಾಕ್ಷರ)",
        "r.syl_v": '<span class="syl">{syl}</span>',
        "rp.title": "ಈ ರಾಶಿಯಲ್ಲಿರುವ ಒಂಬತ್ತು ನಕ್ಷತ್ರ ಪಾದಗಳು",
        "rp.head": "<tr><th>ನಕ್ಷತ್ರ</th><th>ಪಾದ</th><th>ರಾಶಿಯಲ್ಲಿ ಅಂಶ</th><th>ಅಕ್ಷರ</th></tr>",

        "ri.title": "12 ರಾಶಿಗಳು — ಅಧಿಪತಿ, ತತ್ವ, ನಕ್ಷತ್ರಗಳು ಮತ್ತು ಹೆಸರಿನ ಅಕ್ಷರಗಳು | {brand}",
        "ri.desc": ("ಮೇಷದಿಂದ ಮೀನದವರೆಗೆ ಎಲ್ಲಾ 12 ರಾಶಿಗಳು (ಚಂದ್ರ ರಾಶಿಗಳು): ರಾಶ್ಯಧಿಪತಿ, ತತ್ವ, "
                    "ಸ್ವಭಾವ, ಪ್ರತಿ ರಾಶಿಯ ಒಂಬತ್ತು ನಕ್ಷತ್ರ ಪಾದಗಳು ಮತ್ತು ಅವುಗಳ ಹೆಸರಿನ ಅಕ್ಷರಗಳು (ನಾಮಾಕ್ಷರ)."),
        "ri.h1": "<h1>12 ರಾಶಿಗಳು (ಚಂದ್ರ ರಾಶಿಗಳು)</h1>",
        "ri.sub": '<p class="hi">ರಾಶಿಗಳ ಪಟ್ಟಿ ಮತ್ತು ಹೆಸರಿನ ಅಕ್ಷರಗಳು</p>',
        "ri.intro": ("<p>ಪ್ರತಿ ರಾಶಿಯು ನಿರಯನ ರಾಶಿಚಕ್ರದ 30° ವ್ಯಾಪಿಸುತ್ತದೆ ಮತ್ತು ಅದರಲ್ಲಿ ನಿಖರವಾಗಿ ಒಂಬತ್ತು "
                     "ನಕ್ಷತ್ರ ಪಾದಗಳಿವೆ. ನಿಮ್ಮ ರಾಶಿ ಎಂದರೆ ನಿಮ್ಮ ಚಂದ್ರ ರಾಶಿ — ಜನನದ ಸಮಯದಲ್ಲಿ ಚಂದ್ರನಿದ್ದ "
                     "ರಾಶಿ — ರಾಶಿ ಭವಿಷ್ಯ, ಸಾಡೇಸಾತಿ ಮತ್ತು ಜಾತಕ ಹೊಂದಾಣಿಕೆಯನ್ನು ಇದರಿಂದಲೇ ನೋಡಲಾಗುತ್ತದೆ.</p>"),
        "ri.head": ("<tr><th>ರಾಶಿ</th><th>ಅಧಿಪತಿ</th><th>ತತ್ವ</th><th>ನಕ್ಷತ್ರಗಳು</th>"
                    "<th>ಹೆಸರಿನ ಅಕ್ಷರಗಳು</th></tr>"),
        "ri.name": "{name}",
        "humour.Vata": "ವಾತ", "humour.Pitta": "ಪಿತ್ತ", "humour.Kapha": "ಕಫ",
    },

    "te": {
        "kundali_cta": "ఉచిత జాతకం పొందండి — మీ ఖచ్చితమైన జన్మ నక్షత్రం, చంద్ర రాశి తెలుసుకోండి",
        "more.heading": "మరిన్ని ఉచిత సాధనాలు",
        "more.naks": "మొత్తం 27 నక్షత్రాలు",
        "more.rashis": "మొత్తం 12 రాశులు",
        "more.milan": "పేరుతో జాతక పొంతన",
        "more.kundali_milan": "జాతక పొంతన (36 గుణాలు)",
        "more.rashifal": "ఈరోజు రాశి ఫలాలు",
        "more.panchang": "ఈరోజు పంచాంగం",
        "list.naks": "మొత్తం 27 నక్షత్రాలు",
        "list.rashis": "మొత్తం 12 రాశులు",
        "sign": "{name}",
        "sign.pill": "{name}",
        "today.same": ("<strong>ఈరోజు (న్యూఢిల్లీలో సూర్యోదయ సమయానికి) చంద్రుడు {name} నక్షత్రంలో ఉన్నాడు."
                       "</strong>"),
        "today.other": ('ఈరోజు నక్షత్రం (న్యూఢిల్లీలో సూర్యోదయ సమయానికి) '
                        '<a href="{href}"><strong>{name}</strong></a>.'),
        "today.tail": (' దాని ముగింపు సమయం, తిథి, రాహుకాలం <a href="{pan}">ఈరోజు పంచాంగంలో</a> '
                       "చూడండి."),
        "crumb.naks": "నక్షత్రాలు",
        "crumb.rashis": "రాశులు",
        "nf.nak": "నక్షత్రం కనబడలేదు",
        "nf.rashi": "రాశి కనబడలేదు",
        "trait_head": "స్వభావం, లక్షణాలు",
        "gender.male": "పురుష",
        "gender.female": "స్త్రీ",
        "element.Fire": "అగ్ని", "element.Earth": "భూమి", "element.Air": "వాయువు",
        "element.Water": "జలం",
        "quality.Cardinal": "చర", "quality.Fixed": "స్థిర", "quality.Mutable": "ద్విస్వభావ",

        "nak.title": "{name} నక్షత్రం — లక్షణాలు, అధిపతి, పాదాలు, పేరు అక్షరాలు | {brand}",
        "nak.desc": ("{name} నక్షత్రం: {span}, అధిపతి {lord}, {gana} గణం, {nadi} నాడి, "
                     "{yoni} యోని. నాలుగు పాదాల పేరు అక్షరాలు, స్వభావం."),
        "nak.h1": "<h1>{name} నక్షత్రం</h1>",
        "nak.sub": '<p class="hi">నక్షత్రం పేరు అక్షరాలు, పాదాలు, స్వభావం</p>',
        "nak.trait_note": ("<p class=\"note\">ఇవి సంప్రదాయ ధోరణులు మాత్రమే, తీర్పులు కావు. మీ పూర్తి "
                           "జాతకం — లగ్నం, గ్రహాలు, దశ — మీ వ్యక్తిగత చిత్రాన్ని ఇస్తుంది.</p>"),
        "f.number": "క్రమ సంఖ్య", "f.number_v": "27లో {n}వది",
        "f.span": "విస్తృతి (నిరయన)",
        "f.rashi": "రాశి",
        "f.lord": "అధిపతి గ్రహం (వింశోత్తరి)",
        "f.lord_v": "{lord} <small>{years} సంవత్సరాల మహాదశ</small>",
        "f.deity": "దేవత",
        "f.symbol": "చిహ్నం",
        "f.gana": "గణం", "f.gana_v": "{gana}",
        "f.yoni": "యోని (జంతువు)",
        "f.nadi": "నాడి",
        "f.varna": "వర్ణం (రాశి నుండి, జాతక పొంతనలో వాడే విధంగా)",
        "f.syl": "పేరు అక్షరాలు (నామాక్షరం)",
        "f.syl_v": '<span class="syl">{syl}</span>',
        "pada.title": "నాలుగు పాదాలు, వాటి పేరు అక్షరాలు",
        "pada.head": "<tr><th>పాదం</th><th>విస్తృతి</th><th>రాశి</th><th>పేరు అక్షరం</th></tr>",
        "pada.note": ("<p class=\"note\">సంప్రదాయం ప్రకారం శిశువు పేరు జన్మ సమయంలో చంద్రుడు ఉన్న పాదం "
                      "అక్షరంతో మొదలవుతుంది (నామాక్షరం). ఈ అక్షరాలు దృక్ పంచాంగం ప్రచురించిన స్వర "
                      "సిద్ధాంతపు 108 పాదాల జాబితా (అవకహడా చక్రం) ప్రకారం ఉన్నాయి.</p>"),
        "rel.heading": "సంబంధిత",
        "rel.rashifal": "ఈరోజు {name} రాశి ఫలాలు",

        "ni.title": "27 నక్షత్రాలు — అధిపతులు, దేవతలు, గణం, పేరు అక్షరాలు | {brand}",
        "ni.desc": ("అశ్విని నుండి రేవతి వరకు మొత్తం 27 నక్షత్రాలు: విస్తృతి, రాశి, అధిపతి గ్రహం, "
                    "దేవత, గణం, యోని, నాడి, నాలుగు పాదాల పేరు అక్షరాలు — మా జాతక పొంతన "
                    "పట్టికలకు అనుగుణంగా."),
        "ni.h1": "<h1>27 నక్షత్రాలు</h1>",
        "ni.sub": '<p class="hi">నక్షత్రాల జాబితా, పేరు అక్షరాలు</p>',
        "ni.intro": ("<p>వైదిక జ్యోతిషం రాశిచక్రాన్ని ఒక్కొక్కటి 13°20′ ఉన్న 27 నక్షత్రాలుగా, "
                     "ప్రతి నక్షత్రాన్ని ఒక్కొక్కటి 3°20′ ఉన్న నాలుగు పాదాలుగా విభజిస్తుంది. 108 పాదాలు "
                     "12 రాశులలో ఒక్కో రాశికి సరిగ్గా తొమ్మిది చొప్పున వస్తాయి. మీరు పుట్టినప్పుడు "
                     "చంద్రుడు ఉన్న నక్షత్రమే మీ జన్మ నక్షత్రం: దాని నుండే మీ వింశోత్తరి దశ మొదలవుతుంది, "
                     "జాతక పొంతనలోని తార, యోని, గణ, నాడి కూటాలు దాని ఆధారంగానే నిర్ణయమవుతాయి.</p>"),
        "ni.head": ("<tr><th>#</th><th>నక్షత్రం</th><th>రాశి</th><th>అధిపతి</th><th>గణం</th>"
                    "<th>పేరు అక్షరాలు</th></tr>"),

        "rs.title": "{name} రాశి లక్షణాలు — అధిపతి, తత్త్వం, నక్షత్రాలు, పేరు అక్షరాలు | {brand}",
        "rs.desc": ("{name} రాశి (చంద్ర రాశి): అధిపతి {lord}, {element} తత్త్వం, {quality} "
                    "స్వభావం. ఇందులోని 9 నక్షత్ర పాదాలు, పేరు అక్షరాలు (నామాక్షరం), లక్షణాలు."),
        "rs.h1": "<h1>{name} రాశి — చంద్ర రాశి</h1>",
        "rs.sub": '<p class="hi">రాశి లక్షణాలు, నక్షత్ర పాదాలు, పేరు అక్షరాలు</p>',
        "rs.today": "ఈరోజు {name} రాశి ఫలాలు చదవండి",
        "rs.note": ("<p class=\"note\">వైదిక జ్యోతిషంలో “రాశి” అంటే సాధారణంగా చంద్ర రాశి — జన్మ "
                    "సమయంలో నిరయన రాశిచక్రంలో చంద్రుడు ఉన్న రాశి. ఇది తరచుగా పాశ్చాత్య సూర్య "
                    "రాశికి భిన్నంగా ఉంటుంది.</p>"),
        "r.number": "క్రమ సంఖ్య", "r.number_v": "12లో {n}వది",
        "r.span": "విస్తృతి (నిరయన రాశిచక్రం)",
        "r.lord": "రాశ్యధిపతి",
        "r.element": "తత్త్వం",
        "r.quality": "స్వభావం",
        "r.varna": "వర్ణం (జాతక పొంతనలో వాడేది)",
        "r.naks": "నక్షత్రాలు",
        "r.syl": "పేరు అక్షరాలు (నామాక్షరం)",
        "r.syl_v": '<span class="syl">{syl}</span>',
        "rp.title": "ఈ రాశిలోని తొమ్మిది నక్షత్ర పాదాలు",
        "rp.head": "<tr><th>నక్షత్రం</th><th>పాదం</th><th>రాశిలో డిగ్రీలు</th><th>అక్షరం</th></tr>",

        "ri.title": "12 రాశులు — అధిపతులు, తత్త్వాలు, నక్షత్రాలు, పేరు అక్షరాలు | {brand}",
        "ri.desc": ("మేషం నుండి మీనం వరకు మొత్తం 12 రాశులు (చంద్ర రాశులు): రాశ్యధిపతి, తత్త్వం, "
                    "స్వభావం, ప్రతి రాశిలోని తొమ్మిది నక్షత్ర పాదాలు, వాటి పేరు అక్షరాలు (నామాక్షరం)."),
        "ri.h1": "<h1>12 రాశులు (చంద్ర రాశులు)</h1>",
        "ri.sub": '<p class="hi">రాశుల జాబితా, పేరు అక్షరాలు</p>',
        "ri.intro": ("<p>ప్రతి రాశి నిరయన రాశిచక్రంలో 30° విస్తరించి ఉంటుంది, అందులో సరిగ్గా తొమ్మిది "
                     "నక్షత్ర పాదాలు ఉంటాయి. మీ రాశి అంటే మీ చంద్ర రాశి — జన్మ సమయంలో చంద్రుడు ఉన్న "
                     "రాశి — రాశి ఫలాలు, ఏలినాటి శని, జాతక పొంతన అన్నీ దీని నుండే చూస్తారు.</p>"),
        "ri.head": ("<tr><th>రాశి</th><th>అధిపతి</th><th>తత్త్వం</th><th>నక్షత్రాలు</th>"
                    "<th>పేరు అక్షరాలు</th></tr>"),
        "ri.name": "{name}",
        "humour.Vata": "వాతం", "humour.Pitta": "పిత్తం", "humour.Kapha": "కఫం",
    },

    # Tamil (DIVASTRO-123). Names from names_ta; no English/Hindi glosses.
    "ta": {
        "kundali_cta": "உங்கள் இலவச ஜாதகத்தைப் பெறுங்கள் — உங்கள் சரியான ஜன்ம நட்சத்திரத்தையும் சந்திர ராசியையும் அறியுங்கள்",
        "more.heading": "மேலும் இலவச கருவிகள்",
        "more.naks": "27 நட்சத்திரங்களும்",
        "more.rashis": "12 ராசிகளும்",
        "more.milan": "பெயர் பொருத்தம்",
        "more.kundali_milan": "ஜாதகப் பொருத்தம் (36 குணம்)",
        "more.rashifal": "இன்றைய ராசி பலன்",
        "more.panchang": "இன்றைய பஞ்சாங்கம்",
        "list.naks": "27 நட்சத்திரங்களும்",
        "list.rashis": "12 ராசிகளும்",
        "sign": "{name}",
        "sign.pill": "{name}",
        "today.same": "<strong>இன்று சந்திரன் {name} நட்சத்திரத்தில் இருக்கிறார் (புது தில்லியில் சூரிய உதய நேரத்தில்).</strong>",
        "today.other": ("இன்றைய நட்சத்திரம் <a href=\"{href}\"><strong>{name}</strong></a> "
                        "(புது தில்லியில் சூரிய உதய நேரத்தில்)."),
        "today.tail": (' நட்சத்திரம் முடியும் நேரம், திதி, ராகு காலம் ஆகியவற்றை '
                       '<a href="{pan}">இன்றைய பஞ்சாங்கத்தில்</a> பாருங்கள்.'),
        "crumb.naks": "நட்சத்திரங்கள்",
        "crumb.rashis": "ராசிகள்",
        "nf.nak": "நட்சத்திரம் கிடைக்கவில்லை",
        "nf.rashi": "ராசி கிடைக்கவில்லை",
        "trait_head": "இயல்பும் குணங்களும்",
        "gender.male": "ஆண்",
        "gender.female": "பெண்",
        "element.Fire": "நெருப்பு", "element.Earth": "நிலம்", "element.Air": "காற்று",
        "element.Water": "நீர்",
        "quality.Cardinal": "சரம்", "quality.Fixed": "ஸ்திரம்", "quality.Mutable": "உபயம்",

        "nak.title": "{name} நட்சத்திரம் — குணங்கள், அதிபதி, தெய்வம் | {brand}",
        "nak.desc": ("{name} நட்சத்திரம்: {span}, அதிபதி {lord}, {gana} கணம், "
                     "{nadi} நாடி, {yoni} யோனி. நான்கு பாதங்களின் பெயர் எழுத்துகளும் குணங்களும்."),
        "nak.h1": "<h1>{name} நட்சத்திரம்</h1>",
        "nak.sub": '<p class="hi">{name} நட்சத்திர குணங்கள், பாதங்கள், பெயர் எழுத்துகள்</p>',
        "nak.trait_note": ("<p class=\"note\">இவை பாரம்பரியமாகச் சொல்லப்படும் போக்குகள், தீர்ப்புகள் அல்ல. "
                           "லக்னம், கிரகங்கள், தசை அடங்கிய உங்கள் முழு ஜாதகமே தனிப்பட்ட சித்திரத்தைத் தரும்.</p>"),
        "f.number": "வரிசை எண்", "f.number_v": "27-இல் {n}",
        "f.span": "பரப்பு (நிராயன)",
        "f.rashi": "ராசி",
        "f.lord": "அதிபதி கிரகம் (விம்சோத்தரி)",
        "f.lord_v": "{lord} <small>{years} ஆண்டு மகா தசை</small>",
        "f.deity": "தெய்வம்",
        "f.symbol": "சின்னம்",
        "f.gana": "கணம்", "f.gana_v": "{gana}",
        "f.yoni": "யோனி (விலங்கு)",
        "f.nadi": "நாடி",
        "f.varna": "வர்ணம் (ராசிப்படி)",
        "f.syl": "பெயர் எழுத்துகள்",
        "f.syl_v": '<span class="syl" lang="ta">{syl}</span>',
        "pada.title": "நான்கு பாதங்களும் அவற்றின் பெயர் எழுத்துகளும்",
        "pada.head": "<tr><th>பாதம்</th><th>பரப்பு</th><th>ராசி</th><th>பெயர் எழுத்து</th></tr>",
        "pada.note": ("<p class=\"note\">பிறந்த நேரத்தில் சந்திரன் இருந்த பாதத்தின் எழுத்தில் குழந்தையின் பெயரைத் "
                      "தொடங்குவது மரபு (நாமாக்ஷரம்). எழுத்துகள் த்ருக் பஞ்சாங்கம் வெளியிட்ட ஸ்வர சித்தாந்தத்தின் "
                      "108 பாதப் பட்டியலை (அவகஹடா சக்கரம்) பின்பற்றுகின்றன.</p>"),
        "rel.heading": "தொடர்புடையவை",
        "rel.rashifal": "இன்றைய {name} ராசி பலன்",

        "ni.title": "27 நட்சத்திரங்கள் — அதிபதி, கணம், பெயர் எழுத்துகள் | {brand}",
        "ni.desc": ("அஸ்வினி முதல் ரேவதி வரை 27 நட்சத்திரங்களும்: பரப்பு, ராசி, அதிபதி கிரகம், தெய்வம், "
                    "கணம், யோனி, நாடி, நான்கு பாதங்களின் பெயர் எழுத்துகள் — எங்கள் ஜாதகப் பொருத்த "
                    "அட்டவணைகளுடன் ஒத்துப்போகும்."),
        "ni.h1": "<h1>27 நட்சத்திரங்கள்</h1>",
        "ni.sub": '<p class="hi">நட்சத்திரப் பட்டியல் — அதிபதி, கணம், பெயர் எழுத்துகள்</p>',
        "ni.intro": ("<p>வேத ஜோதிடம் ராசிச் சக்கரத்தை தலா 13°20′ கொண்ட 27 நட்சத்திரங்களாகவும், ஒவ்வொரு "
                     "நட்சத்திரத்தையும் 3°20′ கொண்ட நான்கு பாதங்களாகவும் பிரிக்கிறது. 108 பாதங்கள் 12 ராசிகளில் "
                     "ஒரு ராசிக்குச் சரியாக ஒன்பது வீதம் அமைகின்றன. நீங்கள் பிறந்தபோது சந்திரன் இருந்த "
                     "நட்சத்திரமே உங்கள் ஜன்ம நட்சத்திரம்: உங்கள் விம்சோத்தரி தசை அதிலிருந்தே தொடங்குகிறது; "
                     "ஜாதகப் பொருத்தத்தின் தாரா, யோனி, கணம், நாடி ஆகிய பொருத்தங்களும் அதைக் கொண்டே "
                     "பார்க்கப்படுகின்றன.</p>"),
        "ni.head": ("<tr><th>#</th><th>நட்சத்திரம்</th><th>ராசி</th><th>அதிபதி</th><th>கணம்</th>"
                    "<th>பெயர் எழுத்துகள்</th></tr>"),

        "rs.title": "{name} ராசி — குணங்கள், அதிபதி, நட்சத்திரங்கள் | {brand}",
        "rs.desc": ("{name} ராசி (சந்திர ராசி): அதிபதி {lord}, {element} தத்துவம், {quality} ராசி. "
                    "இதில் அடங்கும் 9 நட்சத்திரப் பாதங்கள், பெயர் எழுத்துகள், குணங்கள்."),
        "rs.h1": "<h1>{name} ராசி — சந்திர ராசி</h1>",
        "rs.sub": '<p class="hi">{name} ராசி குணங்கள், நட்சத்திரங்கள், பெயர் எழுத்துகள்</p>',
        "rs.today": "இன்றைய {name} ராசி பலனைப் படியுங்கள்",
        "rs.note": ("<p class=\"note\">வேத ஜோதிடத்தில் \"ராசி\" என்றால் பொதுவாக சந்திர ராசி — பிறந்தபோது "
                    "நிராயன ராசிச் சக்கரத்தில் சந்திரன் இருந்த ராசி. இது மேற்கத்திய சூரிய ராசியிலிருந்து "
                    "பெரும்பாலும் வேறுபடும்.</p>"),
        "r.number": "வரிசை எண்", "r.number_v": "12-இல் {n}",
        "r.span": "பரப்பு (நிராயன ராசிச் சக்கரம்)",
        "r.lord": "ராசி அதிபதி",
        "r.element": "தத்துவம்",
        "r.quality": "தன்மை",
        "r.varna": "வர்ணம் (பொருத்தத்தில் பயன்படுவது)",
        "r.naks": "நட்சத்திரங்கள்",
        "r.syl": "பெயர் எழுத்துகள் (நாமாக்ஷரம்)",
        "r.syl_v": '<span class="syl" lang="ta">{syl}</span>',
        "rp.title": "இந்த ராசியில் உள்ள ஒன்பது நட்சத்திரப் பாதங்கள்",
        "rp.head": "<tr><th>நட்சத்திரம்</th><th>பாதம்</th><th>ராசியில் பாகை</th><th>எழுத்து</th></tr>",

        "ri.title": "12 ராசிகள் — அதிபதி, தத்துவம், நட்சத்திரங்கள் | {brand}",
        "ri.desc": ("மேஷம் முதல் மீனம் வரை 12 ராசிகளும் (வேத சந்திர ராசிகள்): ராசி அதிபதி, தத்துவம், "
                    "தன்மை, ஒவ்வொன்றிலும் உள்ள ஒன்பது நட்சத்திரப் பாதங்கள், அவற்றின் பெயர் எழுத்துகள் "
                    "(நாமாக்ஷரம்)."),
        "ri.h1": "<h1>12 ராசிகள் (சந்திர ராசிகள்)</h1>",
        "ri.sub": '<p class="hi">ராசிப் பட்டியல் — அதிபதி, தத்துவம், நட்சத்திரங்கள்</p>',
        "ri.intro": ("<p>ஒவ்வொரு ராசியும் நிராயன ராசிச் சக்கரத்தில் 30° பரப்புடையது; அதில் சரியாக ஒன்பது "
                     "நட்சத்திரப் பாதங்கள் அடங்கும். உங்கள் ராசி என்பது உங்கள் சந்திர ராசி — பிறந்தபோது "
                     "சந்திரன் இருந்த ராசி. ராசி பலன், ஏழரைச் சனி, ஜாதகப் பொருத்தம் எல்லாம் இதைக் கொண்டே "
                     "பார்க்கப்படுகின்றன.</p>"),
        "ri.head": ("<tr><th>ராசி</th><th>அதிபதி</th><th>தத்துவம்</th><th>நட்சத்திரங்கள்</th>"
                    "<th>பெயர் எழுத்துகள்</th></tr>"),
        "ri.name": "{name}",
        "humour.Vata": "வாதம்", "humour.Pitta": "பித்தம்", "humour.Kapha": "கபம்",
    },

    # Malayalam (DIVASTRO-123). Names from names_ml; no English/Hindi glosses.
    "ml": {
        "kundali_cta": "നിങ്ങളുടെ സൗജന്യ ജാതകം നേടൂ — കൃത്യമായ ജന്മനക്ഷത്രവും ചന്ദ്രരാശിയും അറിയൂ",
        "more.heading": "കൂടുതൽ സൗജന്യ ടൂളുകൾ",
        "more.naks": "27 നക്ഷത്രങ്ങളും",
        "more.rashis": "12 രാശികളും",
        "more.milan": "പേര് പൊരുത്തം",
        "more.kundali_milan": "ജാതകപ്പൊരുത്തം (36 ഗുണം)",
        "more.rashifal": "ഇന്നത്തെ രാശിഫലം",
        "more.panchang": "ഇന്നത്തെ പഞ്ചാംഗം",
        "list.naks": "27 നക്ഷത്രങ്ങളും",
        "list.rashis": "12 രാശികളും",
        "sign": "{name}",
        "sign.pill": "{name}",
        "today.same": "<strong>ഇന്ന് ചന്ദ്രൻ {name} നക്ഷത്രത്തിലാണ് (ന്യൂഡൽഹിയിൽ സൂര്യോദയ സമയത്ത്).</strong>",
        "today.other": ("ഇന്നത്തെ നക്ഷത്രം <a href=\"{href}\"><strong>{name}</strong></a> ആണ് "
                        "(ന്യൂഡൽഹിയിൽ സൂര്യോദയ സമയത്ത്)."),
        "today.tail": (' നക്ഷത്രം അവസാനിക്കുന്ന സമയം, തിഥി, രാഹുകാലം എന്നിവ '
                       '<a href="{pan}">ഇന്നത്തെ പഞ്ചാംഗത്തിൽ</a> കാണാം.'),
        "crumb.naks": "നക്ഷത്രങ്ങൾ",
        "crumb.rashis": "രാശികൾ",
        "nf.nak": "നക്ഷത്രം കണ്ടെത്തിയില്ല",
        "nf.rashi": "രാശി കണ്ടെത്തിയില്ല",
        "trait_head": "സ്വഭാവവും ഗുണങ്ങളും",
        "gender.male": "ആൺ",
        "gender.female": "പെൺ",
        "element.Fire": "അഗ്നി", "element.Earth": "ഭൂമി", "element.Air": "വായു",
        "element.Water": "ജലം",
        "quality.Cardinal": "ചരം", "quality.Fixed": "സ്ഥിരം", "quality.Mutable": "ഉഭയം",

        "nak.title": "{name} നക്ഷത്രം — സ്വഭാവം, ഫലം, നാമാക്ഷരം | {brand}",
        "nak.desc": ("{name} നക്ഷത്രം: {span}, അധിപൻ {lord}, {gana} ഗണം, {nadi} നാഡി, "
                     "{yoni} യോനി. നാല് പാദങ്ങളിലെ പേരിന്റെ അക്ഷരങ്ങളും സ്വഭാവവും."),
        "nak.h1": "<h1>{name} നക്ഷത്രം</h1>",
        "nak.sub": '<p class="hi">{name} നക്ഷത്രം — സ്വഭാവം, പാദങ്ങൾ, പേരിന്റെ അക്ഷരങ്ങൾ</p>',
        "nak.trait_note": ("<p class=\"note\">ഇവ പരമ്പരാഗതമായി പറയുന്ന പ്രവണതകളാണ്, വിധികളല്ല. ലഗ്നം, ഗ്രഹങ്ങൾ, "
                           "ദശ എന്നിവ ഉൾപ്പെടുന്ന നിങ്ങളുടെ പൂർണ്ണ ജാതകമാണ് വ്യക്തിപരമായ ചിത്രം നൽകുന്നത്.</p>"),
        "f.number": "ക്രമനമ്പർ", "f.number_v": "27-ൽ {n}",
        "f.span": "വ്യാപ്തി (നിരയനം)",
        "f.rashi": "രാശി",
        "f.lord": "അധിപ ഗ്രഹം (വിംശോത്തരി)",
        "f.lord_v": "{lord} <small>{years} വർഷത്തെ മഹാദശ</small>",
        "f.deity": "ദേവത",
        "f.symbol": "പ്രതീകം",
        "f.gana": "ഗണം", "f.gana_v": "{gana}",
        "f.yoni": "യോനി (മൃഗം)",
        "f.nadi": "നാഡി",
        "f.varna": "വർണം (രാശിപ്രകാരം)",
        "f.syl": "നാമാക്ഷരം",
        "f.syl_v": '<span class="syl" lang="ml">{syl}</span>',
        "pada.title": "നാല് പാദങ്ങളും അവയുടെ നാമാക്ഷരങ്ങളും",
        "pada.head": "<tr><th>പാദം</th><th>വ്യാപ്തി</th><th>രാശി</th><th>നാമാക്ഷരം</th></tr>",
        "pada.note": ("<p class=\"note\">ജനനസമയത്ത് ചന്ദ്രൻ നിന്ന പാദത്തിന്റെ അക്ഷരത്തിൽ കുഞ്ഞിന്റെ പേര് "
                      "തുടങ്ങുന്നതാണ് പാരമ്പര്യം (നാമാക്ഷരം). അക്ഷരങ്ങൾ ദൃക് പഞ്ചാംഗം പ്രസിദ്ധീകരിച്ച "
                      "സ്വരസിദ്ധാന്തത്തിലെ 108 പാദങ്ങളുടെ പട്ടിക (അവകഹഡാ ചക്രം) പിന്തുടരുന്നു.</p>"),
        "rel.heading": "ബന്ധപ്പെട്ടവ",
        "rel.rashifal": "ഇന്നത്തെ {name} രാശിഫലം",

        "ni.title": "27 നക്ഷത്രങ്ങൾ — അധിപൻ, ഗണം, നാമാക്ഷരം | {brand}",
        "ni.desc": ("അശ്വതി മുതൽ രേവതി വരെ 27 നക്ഷത്രങ്ങളും: വ്യാപ്തി, രാശി, അധിപ ഗ്രഹം, ദേവത, ഗണം, "
                    "യോനി, നാഡി, നാല് പാദങ്ങളിലെയും നാമാക്ഷരങ്ങൾ — ഞങ്ങളുടെ ജാതകപ്പൊരുത്ത "
                    "പട്ടികകളുമായി ഒത്തുപോകുന്നവ."),
        "ni.h1": "<h1>27 നക്ഷത്രങ്ങൾ</h1>",
        "ni.sub": '<p class="hi">നക്ഷത്രങ്ങളുടെ പട്ടിക — അധിപൻ, ഗണം, നാമാക്ഷരം</p>',
        "ni.intro": ("<p>ജ്യോതിഷം രാശിചക്രത്തെ 13°20′ വീതമുള്ള 27 നക്ഷത്രങ്ങളായും ഓരോ നക്ഷത്രത്തെയും "
                     "3°20′ വീതമുള്ള നാല് പാദങ്ങളായും വിഭജിക്കുന്നു. 108 പാദങ്ങൾ 12 രാശികളിലായി ഓരോ "
                     "രാശിയിലും കൃത്യം ഒൻപത് എന്ന നിലയിൽ വരുന്നു. നിങ്ങൾ ജനിച്ചപ്പോൾ ചന്ദ്രൻ നിന്ന "
                     "നക്ഷത്രമാണ് നിങ്ങളുടെ ജന്മനക്ഷത്രം: വിംശോത്തരി ദശ അതിൽ നിന്നാണ് തുടങ്ങുന്നത്; "
                     "ജാതകപ്പൊരുത്തത്തിലെ താരാ, യോനി, ഗണം, നാഡി പൊരുത്തങ്ങളും അതിനെ ആശ്രയിക്കുന്നു.</p>"),
        "ni.head": ("<tr><th>#</th><th>നക്ഷത്രം</th><th>രാശി</th><th>അധിപൻ</th><th>ഗണം</th>"
                    "<th>നാമാക്ഷരങ്ങൾ</th></tr>"),

        "rs.title": "{name} രാശി — സ്വഭാവം, അധിപൻ, നക്ഷത്രങ്ങൾ | {brand}",
        "rs.desc": ("{name} രാശി (ചന്ദ്രരാശി): അധിപൻ {lord}, {element} തത്ത്വം, {quality} രാശി. "
                    "ഇതിലെ 9 നക്ഷത്രപാദങ്ങൾ, നാമാക്ഷരങ്ങൾ, സ്വഭാവം."),
        "rs.h1": "<h1>{name} രാശി — ചന്ദ്രരാശി</h1>",
        "rs.sub": '<p class="hi">{name} രാശി — സ്വഭാവം, നക്ഷത്രങ്ങൾ, നാമാക്ഷരങ്ങൾ</p>',
        "rs.today": "ഇന്നത്തെ {name} രാശിഫലം വായിക്കൂ",
        "rs.note": ("<p class=\"note\">ജ്യോതിഷത്തിൽ \"രാശി\" എന്നാൽ സാധാരണയായി ചന്ദ്രരാശിയാണ് — ജനനസമയത്ത് "
                    "നിരയന രാശിചക്രത്തിൽ ചന്ദ്രൻ നിന്ന രാശി. ഇത് പാശ്ചാത്യ സൂര്യരാശിയിൽ നിന്ന് പലപ്പോഴും "
                    "വ്യത്യസ്തമായിരിക്കും.</p>"),
        "r.number": "ക്രമനമ്പർ", "r.number_v": "12-ൽ {n}",
        "r.span": "വ്യാപ്തി (നിരയന രാശിചക്രം)",
        "r.lord": "രാശ്യധിപൻ",
        "r.element": "തത്ത്വം",
        "r.quality": "സ്വഭാവം",
        "r.varna": "വർണ്ണം (പൊരുത്തത്തിൽ ഉപയോഗിക്കുന്നത്)",
        "r.naks": "നക്ഷത്രങ്ങൾ",
        "r.syl": "പേരിന്റെ അക്ഷരങ്ങൾ (നാമാക്ഷരം)",
        "r.syl_v": '<span class="syl" lang="ml">{syl}</span>',
        "rp.title": "ഈ രാശിയിലെ ഒൻപത് നക്ഷത്രപാദങ്ങൾ",
        "rp.head": "<tr><th>നക്ഷത്രം</th><th>പാദം</th><th>രാശിയിലെ ഡിഗ്രി</th><th>അക്ഷരം</th></tr>",

        "ri.title": "12 രാശികൾ — അധിപൻ, തത്ത്വം, നക്ഷത്രങ്ങൾ | {brand}",
        "ri.desc": ("മേടം മുതൽ മീനം വരെ 12 രാശികളും (ചന്ദ്രരാശികൾ): രാശ്യധിപൻ, തത്ത്വം, സ്വഭാവം, "
                    "ഓരോന്നിലുമുള്ള ഒൻപത് നക്ഷത്രപാദങ്ങൾ, അവയുടെ നാമാക്ഷരങ്ങൾ."),
        "ri.h1": "<h1>12 രാശികൾ (ചന്ദ്രരാശികൾ)</h1>",
        "ri.sub": '<p class="hi">രാശികളുടെ പട്ടിക — അധിപൻ, തത്ത്വം, നക്ഷത്രങ്ങൾ</p>',
        "ri.intro": ("<p>ഓരോ രാശിയും നിരയന രാശിചക്രത്തിൽ 30° വ്യാപിക്കുന്നു; അതിൽ കൃത്യം ഒൻപത് "
                     "നക്ഷത്രപാദങ്ങളുണ്ട്. നിങ്ങളുടെ രാശി എന്നാൽ ചന്ദ്രരാശി — ജനനസമയത്ത് ചന്ദ്രൻ നിന്ന രാശി. "
                     "രാശിഫലം, ഏഴരശനി, ജാതകപ്പൊരുത്തം എന്നിവയെല്ലാം ഇതിൽ നിന്നാണ് നോക്കുന്നത്.</p>"),
        "ri.head": ("<tr><th>രാശി</th><th>അധിപൻ</th><th>തത്ത്വം</th><th>നക്ഷത്രങ്ങൾ</th>"
                    "<th>നാമാക്ഷരങ്ങൾ</th></tr>"),
        "ri.name": "{name}",
        "humour.Vata": "വാതം", "humour.Pitta": "പിത്തം", "humour.Kapha": "കഫം",
    },

    # A language's fallback for a key it has not translated, before English:
    # the keys whose English is (mostly) an astrology name, so an untranslated
    # page shows names_<code> in its own script.
    "_native": {
        "f.gana_v": "{gana}",
    },
}

# The nadi's humour, after the nadi ("Adi <small>Vata</small>").
TEXT["en"].update({f"humour.{h}": h for h in matching.NADI_HUMOUR_HI})
TEXT["hi"].update({f"humour.{h}": v for h, v in matching.NADI_HUMOUR_HI.items()})
