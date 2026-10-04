"""The text of the server-rendered tool pages (seo_pages.py), per language.

TRANSLATORS: this file is data. To translate the /panchang, /rahu-kaal,
/choghadiya, /kundali-milan and /free-kundali pages into, say, Kannada, add a
"kn" dict to TEXT (and to FAQ) with any subset of the "en" keys, then add "kn"
to seo_pages.TRANSLATED. A key you leave out falls back to the "_native"
template (an astrology name in Kannada script) and then to English.

* Templates keep their `{placeholders}`; the word order around them is yours.
  Every page's placeholders are listed above its keys.
* Values marked HTML are inserted into the page as they are: keep the tags,
  write `&amp;` for a literal "&". Title / description / link-text values are
  plain text (escaped by the code).
* Placeholders available in EVERY template, from app/astro/names_<code>.py:
  {t_rahu_kaal} {t_yamaganda} {t_gulika} {t_abhijit} {t_sunrise} {t_sunset}
  {t_moonrise} {t_moonset} ... (TIMINGS) and {l_tithi} {l_nakshatra} {l_yoga}
  {l_karana} {l_vara} {l_paksha} {l_moon_sign} {l_panchang} (LIMBS).
* Astrology names (tithi, nakshatra, yoga, karana, weekday, month, rashi,
  choghadiya, koota) are NOT here: they come from app/astro/names_<code>.py.
"""

from __future__ import annotations

from .astro import matching

TEXT: dict[str, dict[str, str]] = {
    "en": {
        # -- shared ---------------------------------------------------------
        "tool.panchang": "Panchang",
        "tool.rahu-kaal": "Rahu Kaal",
        "tool.choghadiya": "Choghadiya",
        # <p class="date">: {vara} {date} {place}
        "when": "{vara}, {date} · {place} · IST",
        # a limb that changes during the day: {name} {time}
        "limb.until": "{name} until {time}",
        "limb.then": "then {name}",
        "limb.pada": "pada",
        # "Shukla paksha" — {paksha} is the bare word (names PAKSHA)
        "paksha.full": "{paksha} paksha",
        # city / tool link clouds (plain text): {tool} {city}
        "cities.heading": "{tool} in other cities",
        "links.heading": "More free tools",
        "links.tool_in_city": "{tool} in {city}",
        "links.milan": "Kundali Milan (36 guna)",
        "links.kundali": "Free Janam Kundali",
        "links.muhurat": "Muhurat Finder",
        "links.rashifal": "Today's Rashifal",
        "links.vrat": "Today's Vrat & Festivals in {city}",
        # 404: {tool} {slug} {app} {brand}
        "nf.title": "City not found — {brand}",
        "nf.desc": "{tool} city not found.",
        "nf.body": ("<h1>{tool}: city not found</h1>"
                    "<p>We don't have a page for “{slug}” yet. Pick a city below, or "
                    '<a href="{app}">open the {tool} tool</a> to use '
                    "any place in the world.</p>"),

        # -- /panchang ------------------------------------------------------
        # {city} {date} {vara} {tithi} {paksha} {paksha_full} {nakshatra} {sunrise} {rahu} {brand}
        "p.title": "Today's Panchang in {city}, {date} — Tithi, Nakshatra, Rahu Kaal | {brand}",
        "p.desc": ("Aaj ka Panchang for {city} on {vara}, {date}: {tithi} tithi "
                   "({paksha} paksha), {nakshatra} nakshatra, sunrise {sunrise}, "
                   "Rahu Kaal {rahu}. Computed with Swiss Ephemeris."),
        # HTML. {city} {city_en} {city_hi}
        "p.h1": "<h1>Today's Panchang in {city}</h1>",
        "p.sub": '<p class="hi" lang="hi">आज का पंचांग — {city_hi}</p>',
        "p.box": ("<div class=\"box\"><p>Today in {city} is <strong>{paksha} {tithi}</strong>\n"
                  "with the Moon in <strong>{nakshatra}</strong> nakshatra. Rahu Kaal runs\n"
                  "<strong>{rahu}</strong> — avoid starting anything new in that window.</p></div>"),
        # table row labels (plain text)
        "p.r_vara": "Vaar (weekday)",
        "p.r_tithi": "Tithi",
        "p.r_paksha": "Paksha",
        "p.r_nakshatra": "Nakshatra",
        "p.r_yoga": "Yoga",
        "p.r_karana": "Karana",
        "p.r_sunrise": "Sunrise",
        "p.r_sunset": "Sunset",
        "p.r_moonrise": "Moonrise",
        "p.r_moonset": "Moonset",
        "p.r_moon_sign": "Moon sign",
        "p.r_rahu": "Rahu Kaal",
        "p.r_yama": "Yamaganda",
        "p.r_gulika": "Gulika Kaal",
        "p.r_abhijit": "Abhijit Muhurat",
        # table values (HTML): {vara} {vara_en} {vara_hi} {weekday} {paksha} {paksha_en} {paksha_hi_full}
        "p.v_vara": '{vara_en} — {weekday} <span lang="hi">({vara_hi})</span>',
        "p.v_paksha": '{paksha_en} <span lang="hi">({paksha_hi_full})</span>',
        "p.no_moonrise": "No moonrise this day",
        "p.no_moonset": "No moonset this day",
        "p.no_abhijit": "Not observed on Wednesday (Budhavara)",
        # HTML. {city} {place} {lat} {lon}
        "p.note": ("<p>Times are for {place} ({lat}°N, {lon}°E) in\n"
                   "Indian Standard Time. The panchang day runs from sunrise to the next sunrise, so a tithi\n"
                   "or nakshatra may end after midnight. Sunrise is the visible upper limb with refraction,\n"
                   "as printed in Indian almanacs; nakshatra and yoga use the Lahiri ayanamsa.</p>"),
        "p.cta": "Open the full Panchang — any city, any date",
        "p.limbs": ("<h2>The five limbs of the Panchang</h2>\n"
                    "<p><strong>Tithi</strong> is the lunar day — each 12° the Moon gains on the Sun.\n"
                    "<strong>Nakshatra</strong> is the Moon's lunar mansion, one of 27. <strong>Yoga</strong> comes\n"
                    "from the combined longitudes of Sun and Moon, and <strong>Karana</strong> is half a tithi.\n"
                    "<strong>Vaar</strong> is the weekday, reckoned from sunrise. Together they are the\n"
                    "<span lang=\"hi\">पंचांग</span> (“five limbs”) consulted before any auspicious work.</p>"),

        # -- /rahu-kaal -----------------------------------------------------
        # {city} {date} {vara} {rahu} {yama} {gulika} {brand}
        "rk.title": "Rahu Kaal Today in {city} — {rahu}, {date} | {brand}",
        "rk.desc": ("Rahu Kaal today in {city} ({vara}, {date}) is {rahu}. "
                    "Also Yamaganda {yama} and Gulika {gulika}, "
                    "with this week's timings and what Rahu Kaal means."),
        "rk.h1": "<h1>Rahu Kaal Today in {city}</h1>",
        "rk.sub": '<p class="hi" lang="hi">आज का राहु काल — {city_hi}</p>',
        # row labels (HTML)
        "rk.r_rahu": 'Rahu Kaal <span lang="hi">(राहु काल)</span>',
        "rk.r_yama": 'Yamaganda <span lang="hi">(यमगण्ड)</span>',
        "rk.r_gulika": 'Gulika Kaal <span lang="hi">(गुलिक काल)</span>',
        "rk.r_abhijit": "Abhijit Muhurat",
        "rk.r_sun": "Sunrise / Sunset",
        "rk.no_abhijit": "Not observed on Wednesday",
        "rk.cta": "Check Rahu Kaal for any city or date",
        "rk.about": ("<h2>What is Rahu Kaal?</h2>\n"
                     "<p>Rahu Kaal (<span lang=\"hi\">राहु काल</span>) is a period of roughly an hour and a half each day\n"
                     "that is traditionally held to be ruled by Rahu, the north lunar node. Daylight — sunrise to\n"
                     "sunset — is divided into eight equal parts, and one of them belongs to Rahu. Which part\n"
                     "depends on the weekday: the 8th on Sunday, 2nd on Monday, 7th on Tuesday, 5th on Wednesday,\n"
                     "6th on Thursday, 4th on Friday and 3rd on Saturday.</p>\n"
                     "<p>Because it follows the real sunrise and sunset, Rahu Kaal is different in every city and\n"
                     "shifts through the year — which is why a fixed “Monday 7:30–9:00” chart is only an\n"
                     "approximation. By custom, people avoid beginning new ventures, signing agreements, starting\n"
                     "journeys or making major purchases during Rahu Kaal; work already under way can continue.\n"
                     "Yamaganda and Gulika Kaal are two further eighths of the day treated with similar caution.</p>"),
        "rk.week_h2": "<h2>Rahu Kaal in {city} this week</h2>",
        "rk.th_day": "Day",
        "rk.th_rahu": "Rahu Kaal",
        "rk.th_yama": "Yamaganda",
        "rk.th_gulika": "Gulika",

        # -- /choghadiya ----------------------------------------------------
        # {city} {date} {vara} {sunrise} {brand}
        "ch.title": "Choghadiya Today in {city}, {date} — Day & Night Timings | {brand}",
        "ch.desc": ("Today's choghadiya for {city} ({vara}, {date}): all 16 day and night "
                    "muhurtas — Amrit, Shubh, Labh, Char, Rog, Kaal, Udveg — with exact start and end "
                    "times from sunrise {sunrise}."),
        "ch.h1": "<h1>Choghadiya Today in {city}</h1>",
        "ch.sub": '<p class="hi" lang="hi">आज का चौघड़िया — {city_hi}</p>',
        # {name} {time}
        "ch.first_good": "{name} from {time}",
        "ch.none": "none",
        # HTML. {sunrise} {sunset} {first_good}
        "ch.box": ("<div class=\"box\"><p>Sunrise <strong>{sunrise}</strong>, sunset\n"
                   "<strong>{sunset}</strong>. First auspicious daytime choghadiya:\n"
                   "<strong>{first_good}</strong>.</p></div>"),
        "ch.day_h2": '<h2>Day Choghadiya <span lang="hi">(दिन का चौघड़िया)</span></h2>',
        "ch.night_h2": '<h2>Night Choghadiya <span lang="hi">(रात का चौघड़िया)</span></h2>',
        "ch.th": "<tr><th>Time</th><th>Choghadiya</th><th>Nature</th></tr>",
        # one slot (HTML): {when} {cls} {name} {name_hi} {ruler} {quality} {desc}
        "ch.row": ('<tr><td>{when}</td><td class="{cls}"><strong>{name}</strong> '
                   '<span lang="hi">({name_hi})</span><small>{ruler}</small></td>'
                   "<td>{quality}<small>{desc}</small></td></tr>"),
        "ch.cta": "Open the live Choghadiya clock",
        "ch.about": ("<h2>How choghadiya works</h2>\n"
                     "<p>The day from sunrise to sunset, and the night from sunset to the next sunrise, are each\n"
                     "divided into eight equal parts called choghadiya (<span lang=\"hi\">चौघड़िया</span>, “four\n"
                     "ghadis”). Each is ruled by a planet and named for its nature: <strong>Amrit</strong>,\n"
                     "<strong>Shubh</strong> and <strong>Labh</strong> are auspicious, <strong>Char</strong> is\n"
                     "neutral and good for travel, while <strong>Rog</strong>, <strong>Kaal</strong> and\n"
                     "<strong>Udveg</strong> are avoided for new beginnings. The order starts from the weekday's\n"
                     "ruler, so it changes every day — and the length of each slot follows the real day length in\n"
                     "{city}.</p>"),

        # -- /kundali-milan -------------------------------------------------
        # {total} {brand}
        "km.title": "Kundali Milan — Ashtakoot Guna Milan ({total} Gun) Explained | {brand}",
        "km.desc": ("How Kundali Milan works: the 8 kootas of Ashtakoot Guna Milan, {total} points, what "
                    "score is good for marriage, and how Mangal Dosha is checked. Free online matching "
                    "in English and Hindi."),
        "km.crumb": "Kundali Milan",
        "km.intro": ("<h1>Kundali Milan: Ashtakoot Guna Milan explained</h1>\n"
                     "<p class=\"hi\" lang=\"hi\">कुंडली मिलान — अष्टकूट गुण मिलान ({total} गुण)</p>\n"
                     "<p>Kundali Milan (<span lang=\"hi\">कुंडली मिलान</span>) is the traditional Vedic way of checking\n"
                     "marriage compatibility. The most widely used method in North India is <strong>Ashtakoot Guna\n"
                     "Milan</strong>: eight factors (<em>kootas</em>) are compared between the bride's and groom's\n"
                     "charts and scored out of <strong>{total} points (gunas)</strong>. Every one of them is read from\n"
                     "the <strong>Moon</strong> — its sign (rashi) and its nakshatra at birth — which is why\n"
                     "the score needs an accurate birth date and place, but barely depends on the birth time.</p>"),
        "km.cta1": "Match two kundalis now — free",
        # HTML. {href}
        "km.naam": ('<p>Don\'t know the birth times? Try <a href="{href}">Naam se Kundali Milan</a> — '
                    "the traditional match by the first letter of each name.</p>"),
        "km.kootas_h2": "<h2>The 8 kootas and their points</h2>",
        "km.th": "<tr><th>Koota</th><th>Points</th><th>What it measures</th></tr>",
        # one koota (HTML): {name} {name_hi} {pts} {text}
        "km.row": ('<tr><td><strong>{name}</strong> <span lang="hi">({name_hi})</span></td>'
                   "<td>{pts}</td><td>{text}</td></tr>"),
        "km.total": "Total",
        "km.score_h2": "<h2>What is a good Guna Milan score?</h2>",
        "km.score_th": "<tr><th>Gunas</th><th>Conventional reading</th></tr>",
        "km.below": "Below {n}",
        "km.score_p": ("<p>18 is the conventional minimum. The total alone is not the whole story: a high score with an\n"
                       "uncancelled Nadi or Bhakoot dosha is read with caution, and a modest score with strong\n"
                       "Graha Maitri and no doshas is often considered workable. These bands are a convention with a\n"
                       "long history, not a measurement — they are guidance, not a verdict on a relationship.</p>"),
        # Mars's houses: {n}
        "km.ord1": "{n}st",
        "km.ord2": "{n}nd",
        "km.ordn": "{n}th",
        "km.or": " or ",
        # HTML. {houses}
        "km.mangal": ("<h2>Mangal Dosha (Manglik)</h2>\n"
                      "<p>Mangal Dosha is checked separately from the 36 points. A chart is Manglik when Mars sits in\n"
                      "the {houses} house counted from the <strong>Lagna</strong> (ascendant), the\n"
                      "<strong>Moon</strong> or <strong>Venus</strong>. Classical texts exempt certain sign\n"
                      "placements (for example Mars in its own sign Aries in the 1st), and Jupiter's aspect on Mars\n"
                      "is held to soften it. When <strong>both</strong> partners are Manglik the dosha is\n"
                      "conventionally treated as mutually cancelled — which is why Manglik matches are made with\n"
                      "Manglik partners. Because it depends on the Lagna, Mangal Dosha does need a reliable birth\n"
                      "time.</p>"),
        "km.how": ("<h2>How our matching tool works</h2>\n"
                   "<p>Enter both people's date, time and place of birth. Both charts are cast with the sidereal\n"
                   "zodiac (Lahiri ayanamsa) from the Swiss Ephemeris, and each koota is scored by table lookup\n"
                   "from the classical tables, with every cancellation named. You get the full {total}-point\n"
                   "breakdown and both partners' Mangal Dosha status, in English or\n"
                   "<span lang=\"hi\">हिन्दी</span>, free and without signing up.</p>"),
        "km.cta2": "Open Kundali Milan",
        # the 8 kootas: names (shown instead of names_<code>.KOOTA) and what each measures
        "koota.varna": "Varna",
        "koota.vashya": "Vashya",
        "koota.tara": "Tara",
        "koota.yoni": "Yoni",
        "koota.graha_maitri": "Graha Maitri",
        "koota.gana": "Gana",
        "koota.bhakoot": "Bhakoot",
        "koota.nadi": "Nadi",
        "koota_about.varna": ("Spiritual and working temperament, from the Moon sign's varna. "
                              "Full point when the groom's varna is not below the bride's."),
        "koota_about.vashya": "Mutual attraction and influence — which sign “draws” the other.",
        "koota_about.tara": ("Health and wellbeing, from the count between the two birth "
                             "nakshatras; the 3rd, 5th and 7th taras are unfavourable."),
        "koota_about.yoni": ("Physical and intimate compatibility; each nakshatra has an animal yoni, "
                             "and sworn-enemy animals score zero."),
        "koota_about.graha_maitri": ("Friendship between the lords of the two Moon signs — "
                                     "the mental wavelength of the couple."),
        "koota_about.gana": "Temperament: Deva (divine), Manushya (human) or Rakshasa (fierce).",
        "koota_about.bhakoot": ("The relative placement of the two Moon signs. The 2/12, 5/9 and "
                                "6/8 positions form Bhakoot dosha, cancelled when the sign lords are the same or friends."),
        "koota_about.nadi": ("The highest-weighted koota, tied to health and progeny. The same nadi "
                             "for both is Nadi dosha, with classical cancellations for the same sign/different "
                             "nakshatra or same nakshatra/different pada."),

        # -- /free-kundali --------------------------------------------------
        "fk.title": "Free Kundali Online — Janam Kundali (Birth Chart) in English & Hindi | {brand}",
        "fk.desc": ("Make your free janam kundali online: Lagna chart in North or South Indian style, planet "
                    "positions, Moon nakshatra, Vimshottari dasha, Navamsa and other divisional charts, "
                    "Manglik, Sade Sati and Kaal Sarp check — in English or Hindi, no sign-in needed."),
        "fk.crumb": "Free Kundali",
        "fk.intro": ("<h1>Free Janam Kundali online</h1>\n"
                     "<p class=\"hi\" lang=\"hi\">मुफ़्त जन्म कुंडली — हिंदी और अंग्रेज़ी में</p>\n"
                     "<p>A <strong>janam kundali</strong> (<span lang=\"hi\">जन्म कुंडली</span>, birth chart) is a map of\n"
                     "the sky at the exact moment and place you were born: which of the twelve signs was rising on the\n"
                     "eastern horizon (your <strong>Lagna</strong>), and where the Sun, Moon, Mars, Mercury, Jupiter,\n"
                     "Venus, Saturn, Rahu and Ketu stood among the signs and the 27 nakshatras. Vedic astrology reads\n"
                     "everything else — personality, the twelve areas of life, and above all <em>timing</em> through\n"
                     "the dasha periods — from this one chart. Ours is computed to the minute and is free.</p>"),
        "fk.cta1": "Make my free kundali now",
        "fk.need": ("<p>You need your <strong>date</strong>, <strong>time</strong> and <strong>place</strong> of birth.\n"
                    "No sign-in, no card.</p>"),
        # HTML. {vargas}
        "fk.includes": ("<h2>What your free kundali includes</h2>\n"
                        "<ul>\n"
                        "<li><strong>Lagna chart (D1)</strong> in North Indian or South Indian style — switch with one tap.</li>\n"
                        "<li><strong>Planet positions</strong>: sign, degree, house, dignity and retrograde status of all\n"
                        "nine grahas and the ascendant, with your Moon's nakshatra and pada.</li>\n"
                        "<li><strong>The twelve houses (bhavas)</strong> with the planets in each.</li>\n"
                        "<li><strong>Vimshottari dasha</strong>: your current mahadasha and antardasha with their dates,\n"
                        "on a visual timeline.</li>\n"
                        "<li><strong>Divisional charts (vargas)</strong>: {vargas}.</li>\n"
                        "<li><strong>Ashtakavarga</strong>: Sarvashtakavarga and Bhinnashtakavarga bindus by house.</li>\n"
                        "<li><strong>Jaimini</strong> chara karakas (Atmakaraka to Darakaraka) and the Arudha padas, and the\n"
                        "<strong>Sudarshana Chakra</strong> reading of the chart from Lagna, Moon and Sun together.</li>\n"
                        "<li><strong>Dosha check</strong>: Mangal Dosha (Manglik), Sade Sati and Kaal Sarp.</li>\n"
                        "<li><strong>Gemstone and remedy</strong> suggestions for your chart and current dasha.</li>\n"
                        "<li>Your <strong>daily forecast</strong> and today's panchang, on your chart's dashboard.</li>\n"
                        "</ul>\n"
                        "<p>Everything is cast in the <strong>sidereal zodiac with the Lahiri ayanamsa</strong>, whole-sign\n"
                        "houses, from the Swiss Ephemeris. With a free account you can also save charts, download the\n"
                        "kundali as a PDF in English or Hindi, and ask the AI astrologer your first questions free.</p>"),
        "fk.read": ("<h2>How to read your kundali</h2>\n"
                    "<h3>1. Start with the Lagna</h3>\n"
                    "<p>The first house is the sign rising at birth. In the North Indian chart it is the top centre\n"
                    "diamond, and the number written in each house is the <em>sign</em> (1 = Aries … 12 = Pisces), not\n"
                    "the house. In the South Indian chart the signs stay in fixed boxes and the Lagna is marked. The\n"
                    "Lagna and its lord describe the body, temperament and the overall direction of life.</p>\n"
                    "<h3>2. Note your Moon sign and nakshatra</h3>\n"
                    "<p>Your <strong>rashi</strong> in Indian usage is the Moon's sign, not the Sun's. It is the\n"
                    "sign used for rashifal, Sade Sati and Kundali Milan, and the Moon's nakshatra decides where\n"
                    "your Vimshottari dasha begins.</p>\n"
                    "<h3>3. Read the planets by house</h3>\n"
                    "<p>Each house is an area of life: 1st self, 2nd wealth and family, 3rd courage and siblings,\n"
                    "4th home and mother, 5th children and intellect, 6th health and rivals, 7th marriage and\n"
                    "partnership, 8th longevity and sudden change, 9th fortune and dharma, 10th career,\n"
                    "11th gains, 12th expenses and moksha. A planet colours the house it sits in and the houses it\n"
                    "rules; its dignity (exalted, own sign, debilitated) says how well it can deliver.</p>\n"
                    "<h3>4. Check the dasha you are running</h3>\n"
                    "<p>The dasha says <em>when</em>. The mahadasha lord, and within it the antardasha lord, are\n"
                    "the planets whose houses come alive in this period — which is why two people with similar\n"
                    "charts can have very different years.</p>\n"
                    "<h3>5. Treat doshas in context</h3>\n"
                    "<p>A dosha is a pattern to read, not a verdict. Mangal Dosha has classical cancellations;\n"
                    "Sade Sati is a seven-and-a-half-year transit everyone meets two or three times. The dosha\n"
                    "report names the cancellations it found.</p>"),
        "fk.cta2": "Create my janam kundali — free",
        "fk.faq_h2": "<h2>Frequently asked questions</h2>",
        # the default varga list: "D9 Navamsa"
        "varga.D1": "Rashi", "varga.D3": "Drekkana", "varga.D7": "Saptamsa",
        "varga.D9": "Navamsa", "varga.D10": "Dashamsa", "varga.D12": "Dwadashamsa",
    },

    "hi": {
        "tool.panchang": "पंचांग",
        "tool.rahu-kaal": "राहु काल",
        "tool.choghadiya": "चौघड़िया",
        "limb.until": "{name} {time} तक",
        "limb.then": "फिर {name}",
        "limb.pada": "पाद",
        "paksha.full": "{paksha} पक्ष",
        "cities.heading": "अन्य शहरों में {tool}",
        "links.heading": "और मुफ़्त टूल",
        "links.tool_in_city": "{city} का {tool}",
        "links.milan": "कुंडली मिलान (36 गुण)",
        "links.kundali": "मुफ़्त जन्म कुंडली",
        "links.muhurat": "मुहूर्त खोजें",
        "links.rashifal": "आज का राशिफल",
        "links.vrat": "{city} के आज के व्रत और त्योहार",
        "nf.title": "शहर नहीं मिला — {brand}",
        "nf.desc": "{tool}: यह शहर हमारी सूची में नहीं है।",
        "nf.body": ("<h1>{tool}: शहर नहीं मिला</h1>"
                    "<p>“{slug}” के लिए अभी हमारे पास पेज नहीं है। नीचे से अपना शहर चुनें, या "
                    '<a href="{app}">{tool} टूल खोलें</a> — उसमें दुनिया की '
                    "कोई भी जगह चुनी जा सकती है।</p>"),

        "p.title": "आज का पंचांग {city}, {date} — तिथि, नक्षत्र, राहु काल | {brand}",
        "p.desc": ("{city} का आज का पंचांग ({vara}, {date}): {paksha_full} {tithi} तिथि, "
                   "{nakshatra} नक्षत्र, सूर्योदय {sunrise}, राहु काल {rahu}। स्विस एफ़िमेरिस से सटीक गणना।"),
        "p.h1": "<h1>{city} में आज का पंचांग</h1>",
        "p.sub": '<p class="hi" lang="en">Today\'s Panchang in {city_en}</p>',
        "p.box": ("<div class=\"box\"><p>आज {city} में <strong>{paksha_full} की {tithi}</strong> तिथि है और\n"
                  "चंद्रमा <strong>{nakshatra}</strong> नक्षत्र में है। राहु काल <strong>{rahu}</strong> तक रहेगा —\n"
                  "इस समय में कोई नया काम शुरू न करें।</p></div>"),
        "p.r_vara": "वार",
        "p.r_tithi": "तिथि",
        "p.r_paksha": "पक्ष",
        "p.r_nakshatra": "नक्षत्र",
        "p.r_yoga": "योग",
        "p.r_karana": "करण",
        "p.r_sunrise": "सूर्योदय",
        "p.r_sunset": "सूर्यास्त",
        "p.r_moonrise": "चंद्रोदय",
        "p.r_moonset": "चंद्रास्त",
        "p.r_moon_sign": "चंद्र राशि",
        "p.r_rahu": "राहु काल",
        "p.r_yama": "यमगण्ड",
        "p.r_gulika": "गुलिक काल",
        "p.r_abhijit": "अभिजित मुहूर्त",
        "p.v_vara": "{vara}",
        "p.v_paksha": "{paksha_full}",
        "p.no_moonrise": "इस दिन चंद्रोदय नहीं",
        "p.no_moonset": "इस दिन चंद्रास्त नहीं",
        "p.no_abhijit": "बुधवार को अभिजित मुहूर्त नहीं माना जाता",
        "p.note": ("<p>सभी समय {city} ({lat}°N, {lon}°E) के लिए भारतीय मानक\n"
                   "समय (IST) में हैं। पंचांग का दिन सूर्योदय से अगले सूर्योदय तक चलता है, इसलिए कोई तिथि या नक्षत्र\n"
                   "आधी रात के बाद भी समाप्त हो सकता है। सूर्योदय भारतीय पंचांगों की तरह सूर्य के ऊपरी किनारे के\n"
                   "दिखने (वायुमंडलीय अपवर्तन सहित) से लिया गया है; नक्षत्र और योग लाहिड़ी अयनांश से हैं।</p>"),
        "p.cta": "पूरा पंचांग खोलें — कोई भी शहर, कोई भी तारीख",
        "p.limbs": ("<h2>पंचांग के पाँच अंग</h2>\n"
                    "<p><strong>तिथि</strong> चंद्र दिवस है — चंद्रमा सूर्य से जितनी बार 12° आगे बढ़ता है, उतनी\n"
                    "तिथियाँ। <strong>नक्षत्र</strong> 27 में से वह नक्षत्र है जिसमें चंद्रमा स्थित है।\n"
                    "<strong>योग</strong> सूर्य और चंद्रमा के भोगांशों के योग से बनता है, और <strong>करण</strong>\n"
                    "आधी तिथि होता है। <strong>वार</strong> सप्ताह का दिन है, जो सूर्योदय से गिना जाता है। ये पाँचों\n"
                    "मिलकर पंचांग (“पाँच अंग”) कहलाते हैं, जिन्हें हर शुभ कार्य से पहले देखा जाता है।</p>"),

        "rk.title": "आज का राहु काल {city} — {rahu}, {date} | {brand}",
        "rk.desc": ("{city} में आज ({vara}, {date}) राहु काल {rahu} है। साथ में यमगण्ड "
                    "{yama} और गुलिक काल {gulika}, "
                    "पूरे सप्ताह का समय और राहु काल का अर्थ।"),
        "rk.h1": "<h1>{city} में आज का राहु काल</h1>",
        "rk.sub": '<p class="hi" lang="en">Rahu Kaal Today in {city_en}</p>',
        "rk.r_rahu": "राहु काल",
        "rk.r_yama": "यमगण्ड",
        "rk.r_gulika": "गुलिक काल",
        "rk.r_abhijit": "अभिजित मुहूर्त",
        "rk.r_sun": "सूर्योदय / सूर्यास्त",
        "rk.no_abhijit": "बुधवार को अभिजित मुहूर्त नहीं माना जाता",
        "rk.cta": "किसी भी शहर या तारीख का राहु काल देखें",
        "rk.about": ("<h2>राहु काल क्या है?</h2>\n"
                     "<p>राहु काल हर दिन लगभग डेढ़ घंटे की वह अवधि है जिस पर परंपरा से राहु (चंद्रमा का उत्तरी\n"
                     "पात) का प्रभाव माना जाता है। सूर्योदय से सूर्यास्त तक के दिन को आठ बराबर भागों में बाँटा\n"
                     "जाता है और उनमें से एक भाग राहु का होता है। कौन-सा भाग, यह वार पर निर्भर है: रविवार को आठवाँ,\n"
                     "सोमवार को दूसरा, मंगलवार को सातवाँ, बुधवार को पाँचवाँ, गुरुवार को छठा, शुक्रवार को चौथा और\n"
                     "शनिवार को तीसरा।</p>\n"
                     "<p>चूँकि यह वास्तविक सूर्योदय और सूर्यास्त पर आधारित है, इसलिए राहु काल हर शहर में अलग होता है\n"
                     "और साल भर बदलता रहता है — “सोमवार 7:30–9:00” जैसी तय तालिका केवल अनुमान है। परंपरा के अनुसार\n"
                     "राहु काल में नया काम शुरू करना, अनुबंध पर हस्ताक्षर, यात्रा आरंभ या बड़ी ख़रीदारी टाली जाती है;\n"
                     "पहले से चल रहा काम जारी रखा जा सकता है। यमगण्ड और गुलिक काल दिन के दो और आठवें भाग हैं, जिनमें\n"
                     "भी ऐसी ही सावधानी रखी जाती है।</p>"),
        "rk.week_h2": "<h2>{city} में इस सप्ताह का राहु काल</h2>",
        "rk.th_day": "दिन",
        "rk.th_rahu": "राहु काल",
        "rk.th_yama": "यमगण्ड",
        "rk.th_gulika": "गुलिक",

        "ch.title": "आज का चौघड़िया {city}, {date} — दिन और रात का चौघड़िया | {brand}",
        "ch.desc": ("{city} का आज का चौघड़िया ({vara}, {date}): दिन और रात के सभी 16 मुहूर्त — "
                    "अमृत, शुभ, लाभ, चल, रोग, काल, उद्वेग — सूर्योदय {sunrise} से सटीक आरंभ और समाप्ति समय के साथ।"),
        "ch.h1": "<h1>{city} में आज का चौघड़िया</h1>",
        "ch.sub": '<p class="hi" lang="en">Choghadiya Today in {city_en}</p>',
        "ch.first_good": "{name} — {time} से",
        "ch.none": "कोई नहीं",
        "ch.box": ("<div class=\"box\"><p>सूर्योदय <strong>{sunrise}</strong>, सूर्यास्त\n"
                   "<strong>{sunset}</strong>। दिन का पहला शुभ चौघड़िया:\n"
                   "<strong>{first_good}</strong>।</p></div>"),
        "ch.day_h2": "<h2>दिन का चौघड़िया</h2>",
        "ch.night_h2": "<h2>रात का चौघड़िया</h2>",
        "ch.th": "<tr><th>समय</th><th>चौघड़िया</th><th>स्वभाव</th></tr>",
        "ch.row": ('<tr><td>{when}</td><td class="{cls}"><strong>{name}</strong>'
                   "<small>स्वामी: {ruler}</small></td>"
                   "<td>{quality}<small>{desc}</small></td></tr>"),
        "ch.cta": "लाइव चौघड़िया घड़ी खोलें",
        "ch.about": ("<h2>चौघड़िया कैसे निकाला जाता है</h2>\n"
                     "<p>सूर्योदय से सूर्यास्त तक का दिन, और सूर्यास्त से अगले सूर्योदय तक की रात — दोनों को आठ-आठ\n"
                     "बराबर भागों में बाँटा जाता है, जिन्हें चौघड़िया (“चार घड़ी”) कहते हैं। हर भाग का एक स्वामी ग्रह\n"
                     "होता है और नाम उसके स्वभाव से: <strong>अमृत</strong>, <strong>शुभ</strong> और\n"
                     "<strong>लाभ</strong> शुभ हैं, <strong>चल</strong> (चर) सामान्य है और यात्रा के लिए अच्छा माना जाता है,\n"
                     "जबकि <strong>रोग</strong>, <strong>काल</strong> और <strong>उद्वेग</strong> में नए काम की\n"
                     "शुरुआत टाली जाती है। क्रम वार के स्वामी से शुरू होता है, इसलिए हर दिन बदलता है — और हर भाग की\n"
                     "लंबाई {city} में दिन की वास्तविक लंबाई पर निर्भर करती है।</p>"),

        "km.title": "कुंडली मिलान — अष्टकूट गुण मिलान ({total} गुण) की पूरी जानकारी | {brand}",
        "km.desc": ("कुंडली मिलान कैसे होता है: अष्टकूट गुण मिलान के 8 कूट, कुल {total} गुण, विवाह के लिए "
                    "कितने गुण अच्छे माने जाते हैं, और मांगलिक दोष की जाँच। हिंदी और अंग्रेज़ी में मुफ़्त "
                    "ऑनलाइन कुंडली मिलान।"),
        "km.crumb": "कुंडली मिलान",
        "km.intro": ("<h1>कुंडली मिलान: अष्टकूट गुण मिलान की पूरी जानकारी</h1>\n"
                     "<p class=\"hi\" lang=\"en\">Kundali Milan — Ashtakoot Guna Milan ({total} points)</p>\n"
                     "<p>कुंडली मिलान विवाह से पहले वर और कन्या की अनुकूलता देखने की पारंपरिक वैदिक विधि है।\n"
                     "उत्तर भारत में सबसे अधिक प्रचलित तरीक़ा <strong>अष्टकूट गुण मिलान</strong> है: दोनों की कुंडलियों\n"
                     "में आठ कूटों की तुलना की जाती है और कुल <strong>{total} गुणों</strong> में से अंक दिए जाते हैं।\n"
                     "ये सभी <strong>चंद्रमा</strong> से देखे जाते हैं — जन्म के समय उसकी राशि और नक्षत्र से — इसलिए\n"
                     "सही जन्म तिथि और स्थान ज़रूरी है, पर जन्म समय का असर बहुत कम पड़ता है।</p>"),
        "km.cta1": "अभी दो कुंडलियाँ मिलाएँ — मुफ़्त",
        "km.naam": ('<p>जन्म समय पता नहीं? <a href="{href}">नाम से कुंडली मिलान</a> करें — '
                    "नाम के पहले अक्षर से पारंपरिक गुण मिलान।</p>"),
        "km.kootas_h2": "<h2>आठ कूट और उनके गुण</h2>",
        "km.th": "<tr><th>कूट</th><th>गुण</th><th>क्या देखा जाता है</th></tr>",
        "km.row": "<tr><td><strong>{name}</strong></td><td>{pts}</td><td>{text}</td></tr>",
        "km.total": "कुल",
        "km.score_h2": "<h2>कितने गुण मिलना अच्छा है?</h2>",
        "km.score_th": "<tr><th>गुण</th><th>पारंपरिक अर्थ</th></tr>",
        "km.below": "{n} से कम",
        "km.score_p": ("<p>18 गुण पारंपरिक न्यूनतम सीमा है। केवल कुल अंक से पूरी बात नहीं कही जा सकती: ऊँचे अंकों के साथ\n"
                       "बिना परिहार का नाड़ी या भकूट दोष हो तो सावधानी से देखा जाता है, और कम अंक होने पर भी अच्छी ग्रह\n"
                       "मैत्री और कोई दोष न हो तो मिलान अक्सर स्वीकार्य माना जाता है। ये सीमाएँ एक पुरानी परंपरा हैं,\n"
                       "कोई माप नहीं — ये मार्गदर्शन हैं, किसी रिश्ते पर अंतिम निर्णय नहीं।</p>"),
        "km.ord1": "{n}",
        "km.ord2": "{n}",
        "km.ordn": "{n}",
        "km.or": " या ",
        "km.mangal": ("<h2>मांगलिक दोष (मंगल दोष)</h2>\n"
                      "<p>मांगलिक दोष 36 गुणों से अलग देखा जाता है। कुंडली मांगलिक तब होती है जब मंगल\n"
                      "<strong>लग्न</strong>, <strong>चंद्रमा</strong> या <strong>शुक्र</strong> से गिनकर {houses}वें\n"
                      "भाव में हो। शास्त्रों में कुछ राशि-स्थितियों को छूट दी गई है (जैसे पहले भाव में अपनी राशि मेष\n"
                      "में मंगल), और मंगल पर गुरु की दृष्टि से दोष कम माना जाता है। जब वर और कन्या\n"
                      "<strong>दोनों</strong> मांगलिक हों तो परंपरा से दोष आपस में कट जाता है — इसीलिए मांगलिक का\n"
                      "विवाह मांगलिक से किया जाता है। लग्न पर निर्भर होने के कारण मांगलिक दोष के लिए सही जन्म समय\n"
                      "ज़रूरी है।</p>"),
        "km.how": ("<h2>हमारा मिलान टूल कैसे काम करता है</h2>\n"
                   "<p>दोनों की जन्म तिथि, समय और स्थान भरें। दोनों कुंडलियाँ स्विस एफ़िमेरिस से निरयण (लाहिड़ी\n"
                   "अयनांश) पद्धति में बनती हैं, और हर कूट के अंक शास्त्रीय तालिकाओं से दिए जाते हैं — हर परिहार\n"
                   "का नाम लेकर। आपको पूरे {total} गुणों का ब्योरा और दोनों का मांगलिक विचार हिंदी या अंग्रेज़ी में,\n"
                   "मुफ़्त और बिना साइन-अप के मिलता है।</p>"),
        "km.cta2": "कुंडली मिलान खोलें",
        "koota_about.varna": ("चंद्र राशि के वर्ण से आध्यात्मिक और कार्य-स्वभाव। वर का वर्ण कन्या के वर्ण से "
                              "कम न हो तो पूरा अंक।"),
        "koota_about.vashya": "आपसी आकर्षण और प्रभाव — कौन-सी राशि दूसरी को “वश” में करती है।",
        "koota_about.tara": ("स्वास्थ्य और कल्याण, दोनों जन्म नक्षत्रों के बीच की गिनती से; तीसरी, पाँचवीं और "
                             "सातवीं तारा प्रतिकूल मानी जाती है।"),
        "koota_about.yoni": ("शारीरिक और दांपत्य अनुकूलता; हर नक्षत्र की एक पशु योनि होती है, और परस्पर शत्रु "
                             "योनियों को शून्य अंक मिलता है।"),
        "koota_about.graha_maitri": "दोनों चंद्र राशियों के स्वामियों की मित्रता — दंपति का मानसिक तालमेल।",
        "koota_about.gana": "स्वभाव: देव, मनुष्य या राक्षस गण।",
        "koota_about.bhakoot": ("दोनों चंद्र राशियों की परस्पर स्थिति। 2/12, 5/9 और 6/8 की स्थिति भकूट दोष "
                                "बनाती है, जो दोनों राशियों के स्वामी एक हों या मित्र हों तो निरस्त हो जाता है।"),
        "koota_about.nadi": ("सबसे अधिक अंकों वाला कूट, स्वास्थ्य और संतान से जुड़ा। दोनों की एक ही नाड़ी होना "
                             "नाड़ी दोष है; राशि एक पर नक्षत्र भिन्न, या नक्षत्र एक पर चरण भिन्न होने पर इसका "
                             "शास्त्रीय परिहार माना जाता है।"),

        "fk.title": "मुफ़्त जन्म कुंडली ऑनलाइन — हिंदी में फ्री कुंडली बनाएँ | {brand}",
        "fk.desc": ("अपनी जन्म कुंडली मुफ़्त बनाएँ: उत्तर या दक्षिण भारतीय शैली में लग्न कुंडली, ग्रह "
                    "स्थिति, चंद्र नक्षत्र, विंशोत्तरी दशा, नवांश और अन्य वर्ग कुंडलियाँ, मांगलिक, "
                    "साढ़ेसाती और कालसर्प दोष — हिंदी या अंग्रेज़ी में, बिना साइन-इन।"),
        "fk.crumb": "मुफ़्त कुंडली",
        "fk.intro": ("<h1>मुफ़्त जन्म कुंडली ऑनलाइन</h1>\n"
                     "<p class=\"hi\" lang=\"en\">Free Janam Kundali — in Hindi and English</p>\n"
                     "<p><strong>जन्म कुंडली</strong> आपके जन्म के सटीक क्षण और स्थान पर आकाश का नक्शा है: उस समय पूर्वी\n"
                     "क्षितिज पर बारह में से कौन-सी राशि उदित हो रही थी (आपका <strong>लग्न</strong>), और सूर्य, चंद्रमा,\n"
                     "मंगल, बुध, गुरु, शुक्र, शनि, राहु और केतु किस राशि और 27 में से किस नक्षत्र में थे। वैदिक ज्योतिष\n"
                     "स्वभाव, जीवन के बारह क्षेत्र और सबसे बढ़कर <em>समय</em> — दशाओं के माध्यम से — इसी एक कुंडली से\n"
                     "देखता है। हमारी कुंडली मिनट तक सटीक गणना से बनती है और मुफ़्त है।</p>"),
        "fk.cta1": "अभी मेरी मुफ़्त कुंडली बनाएँ",
        "fk.need": ("<p>आपको अपनी जन्म <strong>तिथि</strong>, <strong>समय</strong> और <strong>स्थान</strong> चाहिए।\n"
                    "न साइन-इन, न कार्ड।</p>"),
        "fk.includes": ("<h2>मुफ़्त कुंडली में क्या-क्या मिलता है</h2>\n"
                        "<ul>\n"
                        "<li><strong>लग्न कुंडली (D1)</strong> उत्तर भारतीय या दक्षिण भारतीय शैली में — एक टैप से बदलें।</li>\n"
                        "<li><strong>ग्रह स्थिति</strong>: सभी नौ ग्रहों और लग्न की राशि, अंश, भाव, बल (उच्च/स्वराशि/नीच) और\n"
                        "वक्री स्थिति, साथ में चंद्रमा का नक्षत्र और पाद।</li>\n"
                        "<li><strong>बारह भाव</strong> और हर भाव में स्थित ग्रह।</li>\n"
                        "<li><strong>विंशोत्तरी दशा</strong>: वर्तमान महादशा और अंतर्दशा, तिथियों के साथ, समय-रेखा पर।</li>\n"
                        "<li><strong>वर्ग कुंडलियाँ</strong>: {vargas}।</li>\n"
                        "<li><strong>अष्टकवर्ग</strong>: हर भाव के सर्वाष्टकवर्ग और भिन्नाष्टकवर्ग बिंदु।</li>\n"
                        "<li><strong>जैमिनी</strong> चर कारक (आत्मकारक से दाराकारक तक) और आरूढ़ पद, तथा लग्न, चंद्र और सूर्य\n"
                        "से एक साथ देखा गया <strong>सुदर्शन चक्र</strong>।</li>\n"
                        "<li><strong>दोष जाँच</strong>: मांगलिक (मंगल दोष), साढ़ेसाती और कालसर्प दोष।</li>\n"
                        "<li>आपकी कुंडली और वर्तमान दशा के अनुसार <strong>रत्न और उपाय</strong>।</li>\n"
                        "<li>कुंडली के डैशबोर्ड पर आपका <strong>दैनिक फल</strong> और आज का पंचांग।</li>\n"
                        "</ul>\n"
                        "<p>सब कुछ <strong>निरयण राशिचक्र और लाहिड़ी अयनांश</strong>, संपूर्ण राशि भाव पद्धति और स्विस\n"
                        "एफ़िमेरिस से बनता है। मुफ़्त अकाउंट से आप कुंडलियाँ सहेज सकते हैं, कुंडली की PDF हिंदी या\n"
                        "अंग्रेज़ी में डाउनलोड कर सकते हैं, और एआई ज्योतिषी से शुरुआती प्रश्न मुफ़्त पूछ सकते हैं।</p>"),
        "fk.read": ("<h2>अपनी कुंडली कैसे पढ़ें</h2>\n"
                    "<h3>1. लग्न से शुरू करें</h3>\n"
                    "<p>पहला भाव वह राशि है जो जन्म के समय उदित हो रही थी। उत्तर भारतीय कुंडली में यह ऊपर बीच का\n"
                    "चौकोर (हीरे जैसा) खाना है, और हर खाने में लिखा अंक <em>राशि</em> का है (1 = मेष … 12 = मीन), भाव\n"
                    "का नहीं। दक्षिण भारतीय कुंडली में राशियाँ तय खानों में रहती हैं और लग्न अलग से चिह्नित होता है।\n"
                    "लग्न और लग्नेश शरीर, स्वभाव और जीवन की दिशा बताते हैं।</p>\n"
                    "<h3>2. अपनी चंद्र राशि और नक्षत्र देखें</h3>\n"
                    "<p>भारतीय परंपरा में आपकी <strong>राशि</strong> चंद्रमा की राशि है, सूर्य की नहीं। राशिफल,\n"
                    "साढ़ेसाती और कुंडली मिलान इसी से देखे जाते हैं, और चंद्रमा का नक्षत्र तय करता है कि आपकी\n"
                    "विंशोत्तरी दशा कहाँ से शुरू होगी।</p>\n"
                    "<h3>3. भाव के अनुसार ग्रह पढ़ें</h3>\n"
                    "<p>हर भाव जीवन का एक क्षेत्र है: पहला स्वयं, दूसरा धन और कुटुंब, तीसरा पराक्रम और भाई-बहन, चौथा\n"
                    "घर और माता, पाँचवाँ संतान और बुद्धि, छठा रोग और शत्रु, सातवाँ विवाह और साझेदारी, आठवाँ आयु और\n"
                    "अचानक परिवर्तन, नौवाँ भाग्य और धर्म, दसवाँ कर्म और करियर, ग्यारहवाँ लाभ, बारहवाँ व्यय और मोक्ष।\n"
                    "ग्रह जिस भाव में बैठा है और जिन भावों का स्वामी है, उन्हें प्रभावित करता है; उसकी स्थिति\n"
                    "(उच्च, स्वराशि, नीच) बताती है कि वह कितना फल दे पाएगा।</p>\n"
                    "<h3>4. चल रही दशा देखें</h3>\n"
                    "<p>दशा बताती है <em>कब</em>। महादशा का स्वामी, और उसके भीतर अंतर्दशा का स्वामी, वे ग्रह हैं जिनके\n"
                    "भाव इस अवधि में सक्रिय होते हैं — इसीलिए मिलती-जुलती कुंडली वाले दो लोगों के साल बहुत अलग हो\n"
                    "सकते हैं।</p>\n"
                    "<h3>5. दोषों को संदर्भ में देखें</h3>\n"
                    "<p>दोष पढ़ने का एक संकेत है, कोई फ़ैसला नहीं। मंगल दोष के शास्त्रीय परिहार हैं; साढ़ेसाती शनि का\n"
                    "साढ़े सात साल का गोचर है जो हर किसी के जीवन में दो-तीन बार आता है। दोष रिपोर्ट में मिले हुए परिहारों\n"
                    "के नाम भी दिए जाते हैं।</p>"),
        "fk.cta2": "मेरी जन्म कुंडली बनाएँ — मुफ़्त",
        "fk.faq_h2": "<h2>अक्सर पूछे जाने वाले प्रश्न</h2>",
        "varga.D1": "राशि", "varga.D3": "द्रेष्काण", "varga.D7": "सप्तांश",
        "varga.D9": "नवांश", "varga.D10": "दशमांश", "varga.D12": "द्वादशांश",
    },

    # Used by a language for a key it has not translated yet, before English:
    # only the keys that are (mostly) an astrology name, which every language
    # already has in app/astro/names_<code>.py.
    "_native": {
        "tool.rahu-kaal": "{t_rahu_kaal}",
        "tool.panchang": "{l_panchang}",
        "paksha.full": "{paksha} {l_paksha}",
        "p.r_vara": "{l_vara}",
        "p.r_tithi": "{l_tithi}",
        "p.r_paksha": "{l_paksha}",
        "p.r_nakshatra": "{l_nakshatra}",
        "p.r_yoga": "{l_yoga}",
        "p.r_karana": "{l_karana}",
        "p.r_sunrise": "{t_sunrise}",
        "p.r_sunset": "{t_sunset}",
        "p.r_moonrise": "{t_moonrise}",
        "p.r_moonset": "{t_moonset}",
        "p.r_moon_sign": "{l_moon_sign}",
        "p.r_rahu": "{t_rahu_kaal}",
        "p.r_yama": "{t_yamaganda}",
        "p.r_gulika": "{t_gulika}",
        "p.r_abhijit": "{t_abhijit}",
        "p.v_vara": "{vara}",
        "p.v_paksha": "{paksha_full}",
        "rk.r_rahu": "{t_rahu_kaal}",
        "rk.r_yama": "{t_yamaganda}",
        "rk.r_gulika": "{t_gulika}",
        "rk.r_abhijit": "{t_abhijit}",
        "rk.r_sun": "{t_sunrise} / {t_sunset}",
        "rk.th_rahu": "{t_rahu_kaal}",
        "rk.th_yama": "{t_yamaganda}",
        "rk.th_gulika": "{t_gulika}",
        "ch.row": ('<tr><td>{when}</td><td class="{cls}"><strong>{name}</strong>'
                   "<small>{ruler}</small></td>"
                   "<td>{quality}<small>{desc}</small></td></tr>"),
        "km.row": "<tr><td><strong>{name}</strong></td><td>{pts}</td><td>{text}</td></tr>",
    },
}

# The score bands' verdicts, read from the matching engine so the page and the
# tool's verdict never disagree ("Excellent" / "अति उत्तम / सर्वश्रेष्ठ").
TEXT["en"].update({f"km.band{i}": b[1].capitalize() for i, b in enumerate(matching.SCORE_BANDS)})
TEXT["hi"].update({f"km.band{i}": b[1] for i, b in enumerate(matching.SCORE_BANDS_HI)})

# The free-kundali FAQ: (question, answer) pairs, plain text. Shown on the page
# and marked up as FAQPage JSON-LD from this one list.
FAQ: dict[str, tuple[tuple[str, str], ...]] = {
    "en": (
        ("Is the kundali really free?",
         "Yes. Casting the chart, the dashas, the divisional charts and the dosha check cost "
         "nothing, and you do not need to sign in to see them. Only the AI astrologer's answers "
         "beyond your free questions, and in-depth paid reports such as the Life Book, cost money."),
        ("What details do I need?",
         "Your date of birth, time of birth and place of birth. The place sets the latitude, "
         "longitude and time zone, which decide the Lagna (ascendant) and the house positions."),
        ("What if I don't know my exact birth time?",
         "The chart is still cast, at 12:00 noon. The Moon sign and nakshatra are usually still "
         "right (unless the Moon changed sign or nakshatra that day), so Moon-based readings, "
         "Sade Sati and Kundali Milan stay useful — but the Lagna, the houses and Mangal Dosha "
         "need a reliable time. A time from a birth certificate or hospital record is best."),
        ("Which system do you use — Lahiri, KP, tropical?",
         "Every chart is sidereal (Nirayana) with the Lahiri (Chitrapaksha) ayanamsa, whole-sign "
         "houses and Vimshottari dasha — the convention of most Indian almanacs and astrologers. "
         "Planet positions come from the Swiss Ephemeris."),
        ("Can I see my kundali in Hindi?",
         "Yes. Switch the app to हिन्दी and the chart, planet and sign names, dashas and "
         "readings all appear in Hindi; the PDF can be downloaded in Hindi too."),
        ("North Indian or South Indian chart?",
         "Both. The same chart can be shown as the North Indian diamond chart (houses fixed, signs "
         "numbered) or the South Indian square chart (signs fixed), with one tap."),
        ("Is this the same as a horoscope?",
         "A janam kundali is the birth chart itself — the fixed map of the sky at your birth. "
         "A daily horoscope or rashifal is a short general forecast for everyone with the same "
         "Moon sign. Your kundali is personal; a rashifal is not."),
    ),
    "hi": (
        ("क्या कुंडली सच में मुफ़्त है?",
         "हाँ। कुंडली बनाना, दशाएँ, वर्ग कुंडलियाँ और दोष जाँच पूरी तरह मुफ़्त हैं, और इन्हें देखने के "
         "लिए साइन-इन की ज़रूरत नहीं। केवल मुफ़्त प्रश्नों के बाद एआई ज्योतिषी के उत्तर और लाइफ़ "
         "बुक जैसी विस्तृत रिपोर्ट सशुल्क हैं।"),
        ("कुंडली बनाने के लिए क्या चाहिए?",
         "आपकी जन्म तिथि, जन्म समय और जन्म स्थान। स्थान से अक्षांश, देशांतर और समय क्षेत्र तय होते "
         "हैं, जिनसे लग्न और भावों की स्थिति निकलती है।"),
        ("अगर सही जन्म समय पता न हो तो?",
         "कुंडली फिर भी दोपहर 12:00 बजे के हिसाब से बन जाती है। चंद्र राशि और नक्षत्र आमतौर पर सही "
         "रहते हैं (जब तक उस दिन चंद्रमा ने राशि या नक्षत्र न बदला हो), इसलिए चंद्र-आधारित फल, "
         "साढ़ेसाती और कुंडली मिलान उपयोगी रहते हैं — पर लग्न, भाव और मांगलिक दोष के लिए सही समय "
         "ज़रूरी है। जन्म प्रमाणपत्र या अस्पताल के रिकॉर्ड का समय सबसे अच्छा है।"),
        ("कौन-सी पद्धति इस्तेमाल होती है?",
         "हर कुंडली निरयण (सायन नहीं) पद्धति में लाहिड़ी (चित्रापक्ष) अयनांश, संपूर्ण राशि भाव "
         "(whole sign) और विंशोत्तरी दशा से बनती है — जो अधिकांश भारतीय पंचांगों और ज्योतिषियों की "
         "परंपरा है। ग्रहों की स्थिति स्विस एफ़िमेरिस से ली जाती है।"),
        ("क्या कुंडली हिंदी में मिलेगी?",
         "हाँ। ऐप को हिन्दी में बदलें — कुंडली, ग्रहों और राशियों के नाम, दशाएँ और फलादेश सब हिंदी में "
         "दिखेंगे; PDF भी हिंदी में डाउनलोड की जा सकती है।"),
        ("उत्तर भारतीय या दक्षिण भारतीय कुंडली?",
         "दोनों। एक ही कुंडली को उत्तर भारतीय (भाव स्थिर, राशियों के अंक) या दक्षिण भारतीय (राशियाँ "
         "स्थिर) शैली में एक टैप से देखा जा सकता है।"),
        ("जन्म कुंडली और राशिफल में क्या अंतर है?",
         "जन्म कुंडली आपके जन्म के क्षण के आकाश का स्थायी नक्शा है। दैनिक राशिफल एक ही चंद्र राशि वाले "
         "सभी लोगों के लिए छोटा सामान्य फल है। कुंडली व्यक्तिगत है; राशिफल नहीं।"),
    ),
}
