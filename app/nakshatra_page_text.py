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

    # DIVASTRO-123: Bengali. The builder prints the syllables ({syl}) in Bengali
    # script (nakshatra_text.SYLLABLE_SCRIPT); the subtitle shows the English name.
    "bn": {
        "kundali_cta": "বিনামূল্যে আপনার কোষ্ঠী তৈরি করুন — জেনে নিন সঠিক জন্ম নক্ষত্র ও চন্দ্র রাশি",
        "more.heading": "আরও বিনামূল্যের টুল",
        "more.naks": "সব 27টি নক্ষত্র",
        "more.rashis": "সব 12টি রাশি",
        "more.milan": "নাম দিয়ে যোটক বিচার",
        "more.kundali_milan": "যোটক বিচার (36 গুণ)",
        "more.rashifal": "আজকের রাশিফল",
        "more.panchang": "আজকের পঞ্জিকা",
        "list.naks": "সব 27টি নক্ষত্র",
        "list.rashis": "সব 12টি রাশি",
        "sign": "{name}",
        "sign.pill": "{name}",
        "today.same": "<strong>আজ (নয়াদিল্লিতে সূর্যোদয়ের সময়) চন্দ্র {name} নক্ষত্রে আছে।</strong>",
        "today.other": ('আজকের নক্ষত্র (নয়াদিল্লিতে সূর্যোদয়ের সময়) '
                        '<a href="{href}"><strong>{name}</strong></a>।'),
        "today.tail": ' নক্ষত্রের শেষ সময়, তিথি ও রাহুকাল দেখুন <a href="{pan}">আজকের পঞ্জিকায়</a>।',
        "crumb.naks": "নক্ষত্র",
        "crumb.rashis": "রাশি",
        "nf.nak": "নক্ষত্র পাওয়া যায়নি",
        "nf.rashi": "রাশি পাওয়া যায়নি",
        "trait_head": "স্বভাব ও বৈশিষ্ট্য",
        "gender.male": "পুরুষ",
        "gender.female": "স্ত্রী",
        "element.Fire": "অগ্নি", "element.Earth": "পৃথ্বী", "element.Air": "বায়ু",
        "element.Water": "জল",
        "quality.Cardinal": "চর", "quality.Fixed": "স্থির", "quality.Mutable": "দ্বিস্বভাব",

        "nak.title": "{name} নক্ষত্র — দেবতা, অধিপতি, গণ, যোনি, নাড়ী ও নামাক্ষর | {brand}",
        "nak.desc": ("{name} নক্ষত্র ({name_en}): {span}, অধিপতি গ্রহ {lord}, "
                     "{gana} গণ, {nadi} নাড়ী, যোনি {yoni}। চার পাদের "
                     "নামাক্ষর ও স্বভাব।"),
        "nak.h1": "<h1>{name} নক্ষত্র</h1>",
        "nak.sub": '<p class="hi" lang="en">{name_en} Nakshatra</p>',
        "nak.trait_note": ("<p class=\"note\">এগুলি প্রথাগত প্রবণতা, চূড়ান্ত রায় নয়। আপনার সম্পূর্ণ "
                           "কোষ্ঠী — লগ্ন, গ্রহ ও দশা — ব্যক্তিগত ছবিটি তুলে ধরে।</p>"),
        "f.number": "ক্রম", "f.number_v": "27টির মধ্যে {n} নম্বর",
        "f.span": "বিস্তার (নিরয়ণ)",
        "f.rashi": "রাশি",
        "f.lord": "অধিপতি গ্রহ (বিংশোত্তরী)",
        "f.lord_v": "{lord} <small>মহাদশা {years} বছর</small>",
        "f.deity": "দেবতা",
        "f.symbol": "প্রতীক",
        "f.gana": "গণ", "f.gana_v": "{gana}",
        "f.yoni": "যোনি (প্রাণী)",
        "f.nadi": "নাড়ী",
        "f.varna": "বর্ণ (রাশি অনুযায়ী, গুণ মিলনে ব্যবহৃত)",
        "f.syl": "নামের আদ্যক্ষর (নামাক্ষর)",
        "f.syl_v": '<span class="syl">{syl}</span>',
        "pada.title": "চারটি পাদ ও তাদের নামাক্ষর",
        "pada.head": "<tr><th>পাদ</th><th>বিস্তার</th><th>রাশি</th><th>নামাক্ষর</th></tr>",
        "pada.note": ("<p class=\"note\">প্রথা অনুযায়ী শিশুর নাম শুরু হয় জন্মের সময় চন্দ্র যে পাদে "
                      "ছিল তার অক্ষর দিয়ে (নামাক্ষর)। অক্ষরগুলি দৃক পঞ্চাঙ্গে প্রকাশিত স্বর-সিদ্ধান্তের "
                      "108 পাদের তালিকা (অবকহড়া চক্র) অনুসারে দেওয়া।</p>"),
        "rel.heading": "সম্পর্কিত",
        "rel.rashifal": "আজকের {name} রাশিফল",

        "ni.title": "27টি নক্ষত্র — অধিপতি, দেবতা, গণ ও নামাক্ষরের তালিকা | {brand}",
        "ni.desc": ("অশ্বিনী থেকে রেবতী — সব 27টি নক্ষত্র: বিস্তার, রাশি, অধিপতি গ্রহ, দেবতা, "
                    "গণ, যোনি, নাড়ী এবং চার পাদের নামাক্ষর, আমাদের যোটক বিচারের তালিকার "
                    "সঙ্গে মিলিয়ে।"),
        "ni.h1": "<h1>27টি নক্ষত্র</h1>",
        "ni.sub": '<p class="hi">অশ্বিনী থেকে রেবতী</p>',
        "ni.intro": ("<p>বৈদিক জ্যোতিষে রাশিচক্রকে 13°20′ করে 27টি নক্ষত্রে ভাগ করা হয়, আর "
                     "প্রতিটি নক্ষত্রকে 3°20′-এর চারটি পাদে। মোট 108টি পাদ 12টি রাশিতে ঠিক নয়টি "
                     "করে পড়ে। আপনার জন্ম নক্ষত্র হল জন্মের সময় চন্দ্র যে নক্ষত্রে ছিল: সেখান "
                     "থেকেই বিংশোত্তরী দশা শুরু হয়, আর যোটক বিচারের তারা, যোনি, গণ ও নাড়ী "
                     "কূট এর উপরই নির্ভর করে।</p>"),
        "ni.head": ("<tr><th>#</th><th>নক্ষত্র</th><th>রাশি</th><th>অধিপতি</th><th>গণ</th>"
                    "<th>নামাক্ষর</th></tr>"),

        "rs.title": "{name} রাশি ({english}) — অধিপতি, তত্ত্ব, নক্ষত্র ও নামাক্ষর | {brand}",
        "rs.desc": ("{name} রাশি ({name_en}, {english} চন্দ্র রাশি): অধিপতি {lord}, "
                    "{element_lower} তত্ত্ব, {quality_lower} স্বভাব। এর 9টি নক্ষত্র-পাদ, "
                    "নামাক্ষর ও স্বভাব।"),
        "rs.h1": "<h1>{name} রাশি — {english} চন্দ্র রাশি</h1>",
        "rs.sub": '<p class="hi" lang="en">{name_en} Rashi · {english}</p>',
        "rs.today": "আজকের {name} রাশিফল পড়ুন",
        "rs.note": ("<p class=\"note\">বৈদিক জ্যোতিষে “রাশি” বলতে সাধারণত চন্দ্র রাশি বোঝায় — "
                    "জন্মের সময় নিরয়ণ রাশিচক্রে চন্দ্র যে রাশিতে ছিল। এটি প্রায়ই পাশ্চাত্য "
                    "সূর্য রাশি থেকে আলাদা হয়।</p>"),
        "r.number": "ক্রম", "r.number_v": "12টির মধ্যে {n} নম্বর",
        "r.span": "বিস্তার (নিরয়ণ রাশিচক্র)",
        "r.lord": "রাশির অধিপতি",
        "r.element": "তত্ত্ব",
        "r.quality": "স্বভাব (চর / স্থির / দ্বিস্বভাব)",
        "r.varna": "বর্ণ (গুণ মিলনে ব্যবহৃত)",
        "r.naks": "নক্ষত্র",
        "r.syl": "নামের আদ্যক্ষর (নামাক্ষর)",
        "r.syl_v": '<span class="syl">{syl}</span>',
        "rp.title": "এই রাশির নয়টি নক্ষত্র-পাদ",
        "rp.head": "<tr><th>নক্ষত্র</th><th>পাদ</th><th>রাশিতে অংশ</th><th>নামাক্ষর</th></tr>",

        "ri.title": "12টি রাশি — অধিপতি, তত্ত্ব, নক্ষত্র ও নামাক্ষরের তালিকা | {brand}",
        "ri.desc": ("মেষ থেকে মীন — সব 12টি রাশি (বৈদিক চন্দ্র রাশি): অধিপতি গ্রহ, তত্ত্ব, "
                    "স্বভাব, প্রতিটির নয়টি নক্ষত্র-পাদ ও নামের আদ্যক্ষর (নামাক্ষর)।"),
        "ri.h1": "<h1>12টি রাশি (চন্দ্র রাশি)</h1>",
        "ri.sub": '<p class="hi">মেষ থেকে মীন</p>',
        "ri.intro": ("<p>প্রতিটি রাশি নিরয়ণ রাশিচক্রের 30° জুড়ে থাকে এবং তাতে ঠিক নয়টি "
                     "নক্ষত্র-পাদ পড়ে। আপনার রাশি হল আপনার চন্দ্র রাশি — জন্মের সময় চন্দ্র যে "
                     "রাশিতে ছিল — আর রাশিফল, সাড়েসাতি ও যোটক বিচার এখান থেকেই দেখা হয়।</p>"),
        "ri.head": ("<tr><th>রাশি</th><th>অধিপতি</th><th>তত্ত্ব</th><th>নক্ষত্র</th>"
                    "<th>নামাক্ষর</th></tr>"),
        "ri.name": "{name} <small>{english}</small>",
        "humour.Vata": "বাত", "humour.Pitta": "পিত্ত", "humour.Kapha": "কফ",
    },

    # DIVASTRO-123: Odia.
    "or": {
        "kundali_cta": "ମାଗଣାରେ ଆପଣଙ୍କ କୁଣ୍ଡଳୀ ତିଆରି କରନ୍ତୁ — ଜାଣନ୍ତୁ ସଠିକ ଜନ୍ମ ନକ୍ଷତ୍ର ଓ ଚନ୍ଦ୍ର ରାଶି",
        "more.heading": "ଆହୁରି ମାଗଣା ଟୁଲ୍",
        "more.naks": "ସମସ୍ତ 27 ନକ୍ଷତ୍ର",
        "more.rashis": "ସମସ୍ତ 12 ରାଶି",
        "more.milan": "ନାମରୁ କୁଣ୍ଡଳୀ ମିଳନ",
        "more.kundali_milan": "କୁଣ୍ଡଳୀ ମିଳନ (36 ଗୁଣ)",
        "more.rashifal": "ଆଜିର ରାଶିଫଳ",
        "more.panchang": "ଆଜିର ପାଞ୍ଜି",
        "list.naks": "ସମସ୍ତ 27 ନକ୍ଷତ୍ର",
        "list.rashis": "ସମସ୍ତ 12 ରାଶି",
        "sign": "{name}",
        "sign.pill": "{name}",
        "today.same": "<strong>ଆଜି (ନୂଆଦିଲ୍ଲୀରେ ସୂର୍ଯ୍ୟୋଦୟ ସମୟରେ) ଚନ୍ଦ୍ର {name} ନକ୍ଷତ୍ରରେ ଅଛନ୍ତି।</strong>",
        "today.other": ('ଆଜିର ନକ୍ଷତ୍ର (ନୂଆଦିଲ୍ଲୀରେ ସୂର୍ଯ୍ୟୋଦୟ ସମୟରେ) '
                        '<a href="{href}"><strong>{name}</strong></a>।'),
        "today.tail": ' ନକ୍ଷତ୍ରର ଶେଷ ସମୟ, ତିଥି ଓ ରାହୁ କାଳ <a href="{pan}">ଆଜିର ପାଞ୍ଜି</a>ରେ ଦେଖନ୍ତୁ।',
        "crumb.naks": "ନକ୍ଷତ୍ର",
        "crumb.rashis": "ରାଶି",
        "nf.nak": "ନକ୍ଷତ୍ର ମିଳିଲା ନାହିଁ",
        "nf.rashi": "ରାଶି ମିଳିଲା ନାହିଁ",
        "trait_head": "ସ୍ୱଭାବ ଓ ବୈଶିଷ୍ଟ୍ୟ",
        "gender.male": "ପୁରୁଷ",
        "gender.female": "ସ୍ତ୍ରୀ",
        "element.Fire": "ଅଗ୍ନି", "element.Earth": "ପୃଥ୍ୱୀ", "element.Air": "ବାୟୁ",
        "element.Water": "ଜଳ",
        "quality.Cardinal": "ଚର", "quality.Fixed": "ସ୍ଥିର", "quality.Mutable": "ଦ୍ୱିସ୍ୱଭାବ",

        "nak.title": "{name} ନକ୍ଷତ୍ର — ଦେବତା, ଅଧିପତି, ଗଣ, ଯୋନି, ନାଡ଼ୀ ଓ ନାମାକ୍ଷର | {brand}",
        "nak.desc": ("{name} ନକ୍ଷତ୍ର ({name_en}): {span}, ଅଧିପତି ଗ୍ରହ {lord}, "
                     "{gana} ଗଣ, {nadi} ନାଡ଼ୀ, ଯୋନି {yoni}। ଚାରି ପାଦର "
                     "ନାମାକ୍ଷର ଓ ସ୍ୱଭାବ।"),
        "nak.h1": "<h1>{name} ନକ୍ଷତ୍ର</h1>",
        "nak.sub": '<p class="hi" lang="en">{name_en} Nakshatra</p>',
        "nak.trait_note": ("<p class=\"note\">ଏଗୁଡ଼ିକ ପାରମ୍ପରିକ ପ୍ରବୃତ୍ତି, ଚୂଡ଼ାନ୍ତ ରାୟ ନୁହେଁ। ଆପଣଙ୍କ "
                           "ସମ୍ପୂର୍ଣ୍ଣ କୁଣ୍ଡଳୀ — ଲଗ୍ନ, ଗ୍ରହ ଓ ଦଶା — ବ୍ୟକ୍ତିଗତ ଚିତ୍ର ଦେଇଥାଏ।</p>"),
        "f.number": "କ୍ରମ", "f.number_v": "27 ମଧ୍ୟରୁ {n} ନମ୍ବର",
        "f.span": "ବିସ୍ତାର (ନିରୟଣ)",
        "f.rashi": "ରାଶି",
        "f.lord": "ଅଧିପତି ଗ୍ରହ (ବିଂଶୋତ୍ତରୀ)",
        "f.lord_v": "{lord} <small>ମହାଦଶା {years} ବର୍ଷ</small>",
        "f.deity": "ଦେବତା",
        "f.symbol": "ପ୍ରତୀକ",
        "f.gana": "ଗଣ", "f.gana_v": "{gana}",
        "f.yoni": "ଯୋନି (ପ୍ରାଣୀ)",
        "f.nadi": "ନାଡ଼ୀ",
        "f.varna": "ବର୍ଣ୍ଣ (ରାଶି ଅନୁସାରେ, ଗୁଣ ମିଳନରେ ବ୍ୟବହୃତ)",
        "f.syl": "ନାମର ପ୍ରଥମ ଅକ୍ଷର (ନାମାକ୍ଷର)",
        "f.syl_v": '<span class="syl">{syl}</span>',
        "pada.title": "ଚାରି ପାଦ ଓ ସେମାନଙ୍କ ନାମାକ୍ଷର",
        "pada.head": "<tr><th>ପାଦ</th><th>ବିସ୍ତାର</th><th>ରାଶି</th><th>ନାମାକ୍ଷର</th></tr>",
        "pada.note": ("<p class=\"note\">ପରମ୍ପରା ଅନୁସାରେ ଶିଶୁର ନାମ ଜନ୍ମ ସମୟରେ ଚନ୍ଦ୍ର ଥିବା ପାଦର "
                      "ଅକ୍ଷରରୁ ଆରମ୍ଭ ହୁଏ (ନାମାକ୍ଷର)। ଅକ୍ଷରଗୁଡ଼ିକ ଦୃକ୍ ପଞ୍ଚାଙ୍ଗରେ ପ୍ରକାଶିତ ସ୍ୱର-ସିଦ୍ଧାନ୍ତର "
                      "108 ପାଦ ତାଲିକା (ଅବକହଡ଼ା ଚକ୍ର) ଅନୁସାରେ ଦିଆଯାଇଛି।</p>"),
        "rel.heading": "ସମ୍ବନ୍ଧିତ",
        "rel.rashifal": "ଆଜିର {name} ରାଶିଫଳ",

        "ni.title": "27 ନକ୍ଷତ୍ର — ଅଧିପତି, ଦେବତା, ଗଣ ଓ ନାମାକ୍ଷରର ତାଲିକା | {brand}",
        "ni.desc": ("ଅଶ୍ୱିନୀଠାରୁ ରେବତୀ ପର୍ଯ୍ୟନ୍ତ ସମସ୍ତ 27 ନକ୍ଷତ୍ର: ବିସ୍ତାର, ରାଶି, ଅଧିପତି ଗ୍ରହ, "
                    "ଦେବତା, ଗଣ, ଯୋନି, ନାଡ଼ୀ ଏବଂ ଚାରି ପାଦର ନାମାକ୍ଷର — ଆମ କୁଣ୍ଡଳୀ ମିଳନ "
                    "ତାଲିକା ସହ ମେଳ ଖାଉଥିବା।"),
        "ni.h1": "<h1>27 ନକ୍ଷତ୍ର</h1>",
        "ni.sub": '<p class="hi">ଅଶ୍ୱିନୀଠାରୁ ରେବତୀ</p>',
        "ni.intro": ("<p>ବୈଦିକ ଜ୍ୟୋତିଷରେ ରାଶିଚକ୍ରକୁ 13°20′ କରି 27 ନକ୍ଷତ୍ରରେ ଭାଗ କରାଯାଏ, ଏବଂ "
                     "ପ୍ରତ୍ୟେକ ନକ୍ଷତ୍ରକୁ 3°20′ର ଚାରି ପାଦରେ। ମୋଟ 108 ପାଦ 12 ରାଶିରେ ଠିକ୍ ନଅଟି "
                     "ଲେଖାଏଁ ପଡ଼େ। ଆପଣଙ୍କ ଜନ୍ମ ନକ୍ଷତ୍ର ହେଉଛି ଜନ୍ମ ସମୟରେ ଚନ୍ଦ୍ର ଥିବା ନକ୍ଷତ୍ର: "
                     "ସେଠାରୁ ବିଂଶୋତ୍ତରୀ ଦଶା ଆରମ୍ଭ ହୁଏ, ଏବଂ କୁଣ୍ଡଳୀ ମିଳନର ତାରା, ଯୋନି, ଗଣ ଓ "
                     "ନାଡ଼ୀ କୂଟ ଏହା ଉପରେ ନିର୍ଭର କରେ।</p>"),
        "ni.head": ("<tr><th>#</th><th>ନକ୍ଷତ୍ର</th><th>ରାଶି</th><th>ଅଧିପତି</th><th>ଗଣ</th>"
                    "<th>ନାମାକ୍ଷର</th></tr>"),

        "rs.title": "{name} ରାଶି ({english}) — ଅଧିପତି, ତତ୍ତ୍ୱ, ନକ୍ଷତ୍ର ଓ ନାମାକ୍ଷର | {brand}",
        "rs.desc": ("{name} ରାଶି ({name_en}, {english} ଚନ୍ଦ୍ର ରାଶି): ଅଧିପତି {lord}, "
                    "{element_lower} ତତ୍ତ୍ୱ, {quality_lower} ସ୍ୱଭାବ। ଏହାର 9ଟି ନକ୍ଷତ୍ର-ପାଦ, "
                    "ନାମାକ୍ଷର ଓ ସ୍ୱଭାବ।"),
        "rs.h1": "<h1>{name} ରାଶି — {english} ଚନ୍ଦ୍ର ରାଶି</h1>",
        "rs.sub": '<p class="hi" lang="en">{name_en} Rashi · {english}</p>',
        "rs.today": "ଆଜିର {name} ରାଶିଫଳ ପଢ଼ନ୍ତୁ",
        "rs.note": ("<p class=\"note\">ବୈଦିକ ଜ୍ୟୋତିଷରେ “ରାଶି” କହିଲେ ସାଧାରଣତଃ ଚନ୍ଦ୍ର ରାଶି ବୁଝାଏ — "
                    "ଜନ୍ମ ସମୟରେ ନିରୟଣ ରାଶିଚକ୍ରରେ ଚନ୍ଦ୍ର ଥିବା ରାଶି। ଏହା ପ୍ରାୟତଃ ପାଶ୍ଚାତ୍ୟ "
                    "ସୂର୍ଯ୍ୟ ରାଶିଠାରୁ ଭିନ୍ନ ହୋଇଥାଏ।</p>"),
        "r.number": "କ୍ରମ", "r.number_v": "12 ମଧ୍ୟରୁ {n} ନମ୍ବର",
        "r.span": "ବିସ୍ତାର (ନିରୟଣ ରାଶିଚକ୍ର)",
        "r.lord": "ରାଶିର ଅଧିପତି",
        "r.element": "ତତ୍ତ୍ୱ",
        "r.quality": "ସ୍ୱଭାବ (ଚର / ସ୍ଥିର / ଦ୍ୱିସ୍ୱଭାବ)",
        "r.varna": "ବର୍ଣ୍ଣ (ଗୁଣ ମିଳନରେ ବ୍ୟବହୃତ)",
        "r.naks": "ନକ୍ଷତ୍ର",
        "r.syl": "ନାମର ପ୍ରଥମ ଅକ୍ଷର (ନାମାକ୍ଷର)",
        "r.syl_v": '<span class="syl">{syl}</span>',
        "rp.title": "ଏହି ରାଶିର ନଅଟି ନକ୍ଷତ୍ର-ପାଦ",
        "rp.head": "<tr><th>ନକ୍ଷତ୍ର</th><th>ପାଦ</th><th>ରାଶିରେ ଅଂଶ</th><th>ନାମାକ୍ଷର</th></tr>",

        "ri.title": "12 ରାଶି — ଅଧିପତି, ତତ୍ତ୍ୱ, ନକ୍ଷତ୍ର ଓ ନାମାକ୍ଷରର ତାଲିକା | {brand}",
        "ri.desc": ("ମେଷଠାରୁ ମୀନ ପର୍ଯ୍ୟନ୍ତ ସମସ୍ତ 12 ରାଶି (ବୈଦିକ ଚନ୍ଦ୍ର ରାଶି): ଅଧିପତି ଗ୍ରହ, "
                    "ତତ୍ତ୍ୱ, ସ୍ୱଭାବ, ପ୍ରତ୍ୟେକର ନଅଟି ନକ୍ଷତ୍ର-ପାଦ ଓ ନାମର ପ୍ରଥମ ଅକ୍ଷର (ନାମାକ୍ଷର)।"),
        "ri.h1": "<h1>12 ରାଶି (ଚନ୍ଦ୍ର ରାଶି)</h1>",
        "ri.sub": '<p class="hi">ମେଷଠାରୁ ମୀନ</p>',
        "ri.intro": ("<p>ପ୍ରତ୍ୟେକ ରାଶି ନିରୟଣ ରାଶିଚକ୍ରର 30° ବ୍ୟାପିଥାଏ ଏବଂ ସେଥିରେ ଠିକ୍ ନଅଟି "
                     "ନକ୍ଷତ୍ର-ପାଦ ପଡ଼େ। ଆପଣଙ୍କ ରାଶି ହେଉଛି ଆପଣଙ୍କ ଚନ୍ଦ୍ର ରାଶି — ଜନ୍ମ ସମୟରେ ଚନ୍ଦ୍ର "
                     "ଥିବା ରାଶି — ଏବଂ ରାଶିଫଳ, ସାଢ଼େସାତି ଓ କୁଣ୍ଡଳୀ ମିଳନ ଏଥିରୁ ହିଁ ଦେଖାଯାଏ।</p>"),
        "ri.head": ("<tr><th>ରାଶି</th><th>ଅଧିପତି</th><th>ତତ୍ତ୍ୱ</th><th>ନକ୍ଷତ୍ର</th>"
                    "<th>ନାମାକ୍ଷର</th></tr>"),
        "ri.name": "{name} <small>{english}</small>",
        "humour.Vata": "ବାତ", "humour.Pitta": "ପିତ୍ତ", "humour.Kapha": "କଫ",
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
