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

    "te": {
        "tool.panchang": "పంచాంగం",
        "tool.rahu-kaal": "రాహుకాలం",
        "tool.choghadiya": "చౌఘడియా",
        "when": "{vara}, {date} · {place} · IST",
        "limb.until": "{time} వరకు {name}",
        "limb.then": "తర్వాత {name}",
        "limb.pada": "పాదం",
        "paksha.full": "{paksha} పక్షం",
        "cities.heading": "ఇతర నగరాల్లో {tool}",
        "links.heading": "మరిన్ని ఉచిత సాధనాలు",
        "links.tool_in_city": "{city} {tool}",
        "links.milan": "జాతక పొంతన (36 గుణాలు)",
        "links.kundali": "ఉచిత జన్మ జాతకం",
        "links.muhurat": "ముహూర్తం వెతకండి",
        "links.rashifal": "ఈరోజు రాశి ఫలాలు",
        "links.vrat": "{city} — నేటి వ్రతాలు & పండుగలు",
        "nf.title": "నగరం కనబడలేదు — {brand}",
        "nf.desc": "{tool}: ఈ నగరం మా జాబితాలో లేదు.",
        "nf.body": ("<h1>{tool}: నగరం కనబడలేదు</h1>"
                    "<p>“{slug}” కోసం మా దగ్గర ఇంకా పేజీ లేదు. కింది జాబితా నుండి మీ నగరాన్ని ఎంచుకోండి, లేదా "
                    '<a href="{app}">{tool} సాధనాన్ని తెరవండి</a> — అందులో ప్రపంచంలోని '
                    "ఏ ప్రదేశాన్నైనా ఎంచుకోవచ్చు.</p>"),

        "p.title": "ఈరోజు పంచాంగం {city}, {date} — తిథి, నక్షత్రం, రాహుకాలం | {brand}",
        "p.desc": ("{city} ఈరోజు పంచాంగం ({vara}, {date}): {paksha_full} {tithi} తిథి, "
                   "{nakshatra} నక్షత్రం, సూర్యోదయం {sunrise}, రాహుకాలం {rahu}. స్విస్ ఎఫెమెరిస్‌తో ఖచ్చితమైన గణన."),
        "p.h1": "<h1>ఈరోజు పంచాంగం — {city}</h1>",
        "p.sub": '<p class="hi">{city} పంచాంగం ఈరోజు — తిథి, నక్షత్రం, రాహుకాలం</p>',
        "p.box": ("<div class=\"box\"><p>ఈరోజు {city} లో <strong>{paksha_full} {tithi}</strong> తిథి,\n"
                  "చంద్రుడు <strong>{nakshatra}</strong> నక్షత్రంలో ఉన్నాడు. రాహుకాలం <strong>{rahu}</strong> —\n"
                  "ఈ సమయంలో కొత్త పనులేవీ ప్రారంభించకండి.</p></div>"),
        "p.r_vara": "వారం",
        "p.r_tithi": "తిథి",
        "p.r_paksha": "పక్షం",
        "p.r_nakshatra": "నక్షత్రం",
        "p.r_yoga": "యోగం",
        "p.r_karana": "కరణం",
        "p.r_sunrise": "సూర్యోదయం",
        "p.r_sunset": "సూర్యాస్తమయం",
        "p.r_moonrise": "చంద్రోదయం",
        "p.r_moonset": "చంద్రాస్తమయం",
        "p.r_moon_sign": "చంద్ర రాశి",
        "p.r_rahu": "రాహుకాలం",
        "p.r_yama": "యమగండం",
        "p.r_gulika": "గుళిక కాలం",
        "p.r_abhijit": "అభిజిత్ ముహూర్తం",
        "p.v_vara": "{vara}",
        "p.v_paksha": "{paksha_full}",
        "p.no_moonrise": "ఈ రోజు చంద్రోదయం లేదు",
        "p.no_moonset": "ఈ రోజు చంద్రాస్తమయం లేదు",
        "p.no_abhijit": "బుధవారం అభిజిత్ ముహూర్తం పాటించరు",
        "p.note": ("<p>సమయాలన్నీ {city} ({lat}°N, {lon}°E) కోసం భారత ప్రామాణిక\n"
                   "కాలం (IST) ప్రకారం ఉన్నాయి. పంచాంగ దినం సూర్యోదయం నుండి మరుసటి సూర్యోదయం వరకు ఉంటుంది, కాబట్టి తిథి\n"
                   "లేదా నక్షత్రం అర్ధరాత్రి తర్వాత కూడా ముగియవచ్చు. భారతీయ పంచాంగాల్లో లాగే, వాతావరణ వక్రీభవనంతో సహా\n"
                   "సూర్యబింబం పై అంచు కనిపించే క్షణమే సూర్యోదయం; నక్షత్రం, యోగం లాహిరి అయనాంశతో లెక్కించబడ్డాయి.</p>"),
        "p.cta": "పూర్తి పంచాంగం తెరవండి — ఏ నగరమైనా, ఏ తేదీ అయినా",
        "p.limbs": ("<h2>పంచాంగంలోని ఐదు అంగాలు</h2>\n"
                    "<p><strong>తిథి</strong> అంటే చాంద్రమాన దినం — చంద్రుడు సూర్యుని కంటే ప్రతి 12° ముందుకు వెళ్ళే కాలం.\n"
                    "<strong>నక్షత్రం</strong> అంటే 27 నక్షత్రాల్లో చంద్రుడు ఉన్న నక్షత్రం. <strong>యోగం</strong>\n"
                    "సూర్యచంద్రుల రేఖాంశాల మొత్తం నుండి వస్తుంది, <strong>కరణం</strong> అంటే సగం తిథి.\n"
                    "<strong>వారం</strong> అంటే వారంలోని రోజు, సూర్యోదయం నుండి లెక్కిస్తారు. ఈ ఐదూ కలిసి\n"
                    "పంచాంగం (“ఐదు అంగాలు”) — ఏ శుభకార్యానికైనా ముందు దీన్ని చూస్తారు.</p>"),

        "rk.title": "నేటి రాహుకాలం {city} — {rahu}, {date} | {brand}",
        "rk.desc": ("{city} లో ఈరోజు ({vara}, {date}) రాహుకాలం {rahu}. యమగండం {yama}, "
                    "గుళిక కాలం {gulika} కూడా — ఈ వారం సమయాలు, రాహుకాలం అంటే ఏమిటో తెలుసుకోండి."),
        "rk.h1": "<h1>నేటి రాహుకాలం — {city}</h1>",
        "rk.sub": '<p class="hi">{city} రాహుకాలం ఈరోజు — యమగండం, గుళిక కాలం</p>',
        "rk.r_rahu": "రాహుకాలం",
        "rk.r_yama": "యమగండం",
        "rk.r_gulika": "గుళిక కాలం",
        "rk.r_abhijit": "అభిజిత్ ముహూర్తం",
        "rk.r_sun": "సూర్యోదయం / సూర్యాస్తమయం",
        "rk.no_abhijit": "బుధవారం అభిజిత్ ముహూర్తం పాటించరు",
        "rk.cta": "ఏ నగరానికైనా, ఏ తేదీకైనా రాహుకాలం చూడండి",
        "rk.about": ("<h2>రాహుకాలం అంటే ఏమిటి?</h2>\n"
                     "<p>రాహుకాలం ప్రతిరోజూ సుమారు గంటన్నర పాటు ఉండే సమయం; సంప్రదాయం ప్రకారం దానిపై రాహువు (చంద్రుని\n"
                     "ఉత్తర పాతం) ఆధిపత్యం ఉంటుందని భావిస్తారు. సూర్యోదయం నుండి సూర్యాస్తమయం వరకు ఉన్న పగటి కాలాన్ని\n"
                     "ఎనిమిది సమాన భాగాలుగా విభజిస్తారు, వాటిలో ఒక భాగం రాహువుది. అది ఏ భాగమనేది వారాన్ని బట్టి ఉంటుంది:\n"
                     "ఆదివారం 8వది, సోమవారం 2వది, మంగళవారం 7వది, బుధవారం 5వది, గురువారం 6వది, శుక్రవారం 4వది,\n"
                     "శనివారం 3వది.</p>\n"
                     "<p>ఇది నిజమైన సూర్యోదయ, సూర్యాస్తమయాలను అనుసరిస్తుంది కాబట్టి రాహుకాలం ప్రతి నగరంలో వేరుగా ఉంటుంది,\n"
                     "సంవత్సరం పొడవునా మారుతూ ఉంటుంది — అందుకే “సోమవారం 7:30–9:00” వంటి స్థిర పట్టిక కేవలం\n"
                     "ఉజ్జాయింపు మాత్రమే. ఆచారం ప్రకారం రాహుకాలంలో కొత్త పనులు ప్రారంభించడం, ఒప్పందాలపై సంతకం చేయడం,\n"
                     "ప్రయాణం మొదలుపెట్టడం, పెద్ద కొనుగోళ్ళు చేయడం మానుకుంటారు; ఇప్పటికే జరుగుతున్న పనులు కొనసాగించవచ్చు.\n"
                     "యమగండం, గుళిక కాలం పగటిలోని మరో రెండు ఎనిమిదో భాగాలు; వాటి విషయంలోనూ ఇదే జాగ్రత్త పాటిస్తారు.</p>"),
        "rk.week_h2": "<h2>ఈ వారం రాహుకాలం — {city}</h2>",
        "rk.th_day": "రోజు",
        "rk.th_rahu": "రాహుకాలం",
        "rk.th_yama": "యమగండం",
        "rk.th_gulika": "గుళిక",

        "ch.title": "ఈరోజు చౌఘడియా {city}, {date} — పగలు, రాత్రి సమయాలు | {brand}",
        "ch.desc": ("{city} ఈరోజు చౌఘడియా ({vara}, {date}): పగలు, రాత్రి కలిపి మొత్తం 16 ముహూర్తాలు — "
                    "అమృతం, శుభం, లాభం, చరం, రోగం, కాలం, ఉద్వేగం — సూర్యోదయం {sunrise} నుండి ఖచ్చితమైన "
                    "ప్రారంభ, ముగింపు సమయాలతో."),
        "ch.h1": "<h1>ఈరోజు చౌఘడియా — {city}</h1>",
        "ch.sub": '<p class="hi">{city} చౌఘడియా ఈరోజు — శుభ, అశుభ సమయాలు</p>',
        "ch.first_good": "{time} నుండి {name}",
        "ch.none": "ఏదీ లేదు",
        "ch.box": ("<div class=\"box\"><p>సూర్యోదయం <strong>{sunrise}</strong>, సూర్యాస్తమయం\n"
                   "<strong>{sunset}</strong>. పగటిలో మొదటి శుభ చౌఘడియా:\n"
                   "<strong>{first_good}</strong>.</p></div>"),
        "ch.day_h2": "<h2>పగటి చౌఘడియా</h2>",
        "ch.night_h2": "<h2>రాత్రి చౌఘడియా</h2>",
        "ch.th": "<tr><th>సమయం</th><th>చౌఘడియా</th><th>స్వభావం</th></tr>",
        "ch.row": ('<tr><td>{when}</td><td class="{cls}"><strong>{name}</strong>'
                   "<small>అధిపతి: {ruler}</small></td>"
                   "<td>{quality}<small>{desc}</small></td></tr>"),
        "ch.cta": "ప్రత్యక్ష చౌఘడియా గడియారం తెరవండి",
        "ch.about": ("<h2>చౌఘడియా ఎలా లెక్కిస్తారు</h2>\n"
                     "<p>సూర్యోదయం నుండి సూర్యాస్తమయం వరకు పగలు, సూర్యాస్తమయం నుండి మరుసటి సూర్యోదయం వరకు రాత్రి — రెండింటినీ\n"
                     "ఎనిమిదేసి సమాన భాగాలుగా విభజిస్తారు; వీటినే చౌఘడియా (“నాలుగు ఘడియలు”) అంటారు. ప్రతి భాగానికి ఒక\n"
                     "అధిపతి గ్రహం ఉంటుంది, దాని స్వభావాన్ని బట్టి పేరు: <strong>అమృతం</strong>, <strong>శుభం</strong>,\n"
                     "<strong>లాభం</strong> శుభప్రదమైనవి, <strong>చరం</strong> మధ్యమం — ప్రయాణాలకు మంచిది, కాగా\n"
                     "<strong>రోగం</strong>, <strong>కాలం</strong>, <strong>ఉద్వేగం</strong> సమయాల్లో కొత్త పనుల\n"
                     "ప్రారంభం మానుకుంటారు. క్రమం ఆ వారపు అధిపతి నుండి మొదలవుతుంది కాబట్టి రోజూ మారుతుంది — ప్రతి భాగం\n"
                     "నిడివి {city} లో పగటి కాలం యొక్క నిజమైన నిడివిపై ఆధారపడి ఉంటుంది.</p>"),

        "km.title": "జాతక పొంతన — అష్టకూట గుణ మిలన్ ({total} గుణాలు) పూర్తి వివరణ | {brand}",
        "km.desc": ("జాతక పొంతన ఎలా చూస్తారు: అష్టకూట గుణ మిలన్‌లోని 8 కూటాలు, మొత్తం {total} గుణాలు, వివాహానికి "
                    "ఎన్ని గుణాలు మంచివి, కుజ దోషం ఎలా చూస్తారు. ఇంగ్లీష్, హిందీలో ఉచిత ఆన్‌లైన్ పొంతన."),
        "km.crumb": "జాతక పొంతన",
        "km.intro": ("<h1>జాతక పొంతన: అష్టకూట గుణ మిలన్ పూర్తి వివరణ</h1>\n"
                     "<p class=\"hi\">కుండలి మిలన్ — అష్టకూట గుణ మిలన్ ({total} గుణాలు)</p>\n"
                     "<p>జాతక పొంతన (కుండలి మిలన్) వివాహ అనుకూలతను చూసే సంప్రదాయ వైదిక పద్ధతి. ఉత్తర భారతదేశంలో\n"
                     "ఎక్కువగా వాడే పద్ధతి <strong>అష్టకూట గుణ మిలన్</strong>: వధూవరుల జాతకాల్లో ఎనిమిది అంశాలను\n"
                     "(<em>కూటాలు</em>) పోల్చి, మొత్తం <strong>{total} గుణాలకు (పాయింట్లకు)</strong> మార్కులు ఇస్తారు. ఇవన్నీ\n"
                     "<strong>చంద్రుని</strong> నుండే — పుట్టినప్పుడు చంద్రుడు ఉన్న రాశి, నక్షత్రం నుండి — చూస్తారు;\n"
                     "అందుకే పుట్టిన తేదీ, ప్రదేశం ఖచ్చితంగా ఉండాలి, కానీ పుట్టిన సమయం ప్రభావం చాలా తక్కువ.</p>"),
        "km.cta1": "ఇప్పుడే రెండు జాతకాలు పొంతన చూడండి — ఉచితం",
        "km.naam": ('<p>పుట్టిన సమయాలు తెలియవా? <a href="{href}">పేరుతో జాతక పొంతన</a> ప్రయత్నించండి — '
                    "ప్రతి పేరులోని మొదటి అక్షరంతో చేసే సంప్రదాయ పొంతన.</p>"),
        "km.kootas_h2": "<h2>8 కూటాలు, వాటి గుణాలు</h2>",
        "km.th": "<tr><th>కూటం</th><th>గుణాలు</th><th>ఏమి చూస్తారు</th></tr>",
        "km.row": "<tr><td><strong>{name}</strong></td><td>{pts}</td><td>{text}</td></tr>",
        "km.total": "మొత్తం",
        "km.score_h2": "<h2>ఎన్ని గుణాలు కలిస్తే మంచిది?</h2>",
        "km.score_th": "<tr><th>గుణాలు</th><th>సంప్రదాయ అర్థం</th></tr>",
        "km.below": "{n} కంటే తక్కువ",
        "km.score_p": ("<p>18 గుణాలు సంప్రదాయ కనీస పరిమితి. మొత్తం గుణాలు మాత్రమే పూర్తి కథ చెప్పవు: ఎక్కువ గుణాలు ఉన్నా\n"
                       "పరిహారం లేని నాడి లేదా భకూట దోషం ఉంటే జాగ్రత్తగా చూస్తారు, తక్కువ గుణాలు ఉన్నా బలమైన గ్రహ మైత్రి\n"
                       "ఉండి దోషాలేవీ లేకపోతే ఆ పొంతనను తరచుగా ఆమోదయోగ్యంగా భావిస్తారు. ఈ పరిమితులు ఎంతో కాలంగా వస్తున్న\n"
                       "సంప్రదాయం, కొలత కాదు — ఇవి మార్గదర్శకాలు మాత్రమే, ఏ బంధంపైనా తుది తీర్పు కాదు.</p>"),
        "km.ord1": "{n}వ",
        "km.ord2": "{n}వ",
        "km.ordn": "{n}వ",
        "km.or": " లేదా ",
        "km.mangal": ("<h2>కుజ దోషం (మాంగళిక దోషం)</h2>\n"
                      "<p>కుజ దోషాన్ని 36 గుణాలతో సంబంధం లేకుండా విడిగా చూస్తారు. <strong>లగ్నం</strong>,\n"
                      "<strong>చంద్రుడు</strong> లేదా <strong>శుక్రుడు</strong> నుండి లెక్కిస్తే కుజుడు {houses}\n"
                      "భావంలో ఉంటే ఆ జాతకంలో కుజ దోషం ఉన్నట్లు. శాస్త్ర గ్రంథాలు కొన్ని రాశి స్థానాలకు మినహాయింపు ఇస్తాయి\n"
                      "(ఉదాహరణకు 1వ భావంలో స్వక్షేత్రమైన మేషంలో కుజుడు), గురువు దృష్టి కుజునిపై ఉంటే దోషం తగ్గుతుందని\n"
                      "భావిస్తారు. వధూవరులు <strong>ఇద్దరికీ</strong> కుజ దోషం ఉంటే సంప్రదాయం ప్రకారం దోషం పరస్పరం\n"
                      "రద్దవుతుంది — అందుకే కుజ దోషం ఉన్నవారికి కుజ దోషం ఉన్నవారితోనే పొంతన చూస్తారు. ఇది లగ్నంపై\n"
                      "ఆధారపడుతుంది కాబట్టి కుజ దోషానికి నమ్మదగిన పుట్టిన సమయం తప్పనిసరి.</p>"),
        "km.how": ("<h2>మా పొంతన సాధనం ఎలా పనిచేస్తుంది</h2>\n"
                   "<p>ఇద్దరి పుట్టిన తేదీ, సమయం, ప్రదేశం నమోదు చేయండి. రెండు జాతకాలూ స్విస్ ఎఫెమెరిస్ ఆధారంగా నిరయన\n"
                   "(లాహిరి అయనాంశ) పద్ధతిలో వేయబడతాయి, ప్రతి కూటానికి శాస్త్రీయ పట్టికల నుండి గుణాలు ఇవ్వబడతాయి —\n"
                   "ప్రతి పరిహారాన్ని పేరుతో సహా చూపిస్తాం. మొత్తం {total} గుణాల పూర్తి వివరాలు, ఇద్దరి కుజ దోష స్థితి\n"
                   "ఇంగ్లీష్ లేదా హిందీలో, ఉచితంగా, సైన్ అప్ అవసరం లేకుండా పొందుతారు.</p>"),
        "km.cta2": "జాతక పొంతన తెరవండి",
        "km.band0": "సిఫార్సు చేయదగినది కాదు",
        "km.band1": "ఆమోదయోగ్యం",
        "km.band2": "మంచిది / శుభం",
        "km.band3": "అత్యుత్తమం",
        "koota.varna": "వర్ణం",
        "koota.vashya": "వశ్యం",
        "koota.tara": "తార (దిన)",
        "koota.yoni": "యోని",
        "koota.graha_maitri": "గ్రహ మైత్రి",
        "koota.gana": "గణం",
        "koota.bhakoot": "రాశి కూటమి (భకూట్)",
        "koota.nadi": "నాడి",
        "koota_about.varna": ("చంద్ర రాశి వర్ణం నుండి ఆధ్యాత్మిక, పని స్వభావం. వరుడి వర్ణం వధువు వర్ణం కంటే "
                              "తక్కువ కాకపోతే పూర్తి గుణం."),
        "koota_about.vashya": "పరస్పర ఆకర్షణ, ప్రభావం — ఏ రాశి మరో రాశిని “వశం” చేసుకుంటుంది.",
        "koota_about.tara": ("ఆరోగ్యం, శ్రేయస్సు — రెండు జన్మ నక్షత్రాల మధ్య లెక్క నుండి; 3వ, 5వ, 7వ "
                             "తారలు ప్రతికూలం."),
        "koota_about.yoni": ("శారీరక, దాంపత్య అనుకూలత; ప్రతి నక్షత్రానికి ఒక జంతు యోని ఉంటుంది, బద్ధ శత్రువులైన "
                             "జంతువులకు సున్నా గుణాలు."),
        "koota_about.graha_maitri": "రెండు చంద్ర రాశుల అధిపతుల మధ్య మైత్రి — దంపతుల మానసిక సామరస్యం.",
        "koota_about.gana": "స్వభావం: దేవ (దైవిక), మనుష్య (మానవ) లేదా రాక్షస (ఉగ్ర) గణం.",
        "koota_about.bhakoot": ("రెండు చంద్ర రాశుల పరస్పర స్థానం. 2/12, 5/9, 6/8 స్థానాలు భకూట దోషం; "
                                "రెండు రాశుల అధిపతులు ఒకరే అయినా, మిత్రులైనా ఈ దోషం రద్దవుతుంది."),
        "koota_about.nadi": ("అత్యధిక గుణాలున్న కూటం, ఆరోగ్యం, సంతానంతో ముడిపడినది. ఇద్దరిదీ ఒకే నాడి అయితే "
                             "నాడి దోషం; రాశి ఒకటే కానీ నక్షత్రం వేరు, లేదా నక్షత్రం ఒకటే కానీ పాదం వేరు అయితే "
                             "శాస్త్రీయ పరిహారం ఉంటుంది."),

        "fk.title": "ఉచిత జాతకం ఆన్‌లైన్ — జన్మ కుండలి (జాతక చక్రం) | {brand}",
        "fk.desc": ("మీ జన్మ జాతకం ఉచితంగా ఆన్‌లైన్‌లో: ఉత్తర లేదా దక్షిణ భారత శైలిలో లగ్న చక్రం, గ్రహ స్థితులు, "
                    "చంద్ర నక్షత్రం, వింశోత్తరి దశ, నవాంశ, ఇతర వర్గ చక్రాలు, కుజ దోషం, ఏలినాటి శని, "
                    "కాలసర్ప దోష పరిశీలన — తెలుగు లేదా ఇంగ్లీష్‌లో, సైన్ ఇన్ అవసరం లేదు."),
        "fk.crumb": "ఉచిత జాతకం",
        "fk.intro": ("<h1>ఉచిత జన్మ జాతకం ఆన్‌లైన్</h1>\n"
                     "<p class=\"hi\">ఉచిత జన్మ కుండలి — జాతక చక్రం, దశలు, దోషాలు</p>\n"
                     "<p><strong>జన్మ జాతకం</strong> (జన్మ కుండలి) మీరు పుట్టిన ఖచ్చితమైన క్షణంలో, పుట్టిన ప్రదేశం నుండి\n"
                     "ఆకాశం ఎలా ఉందో చూపే పటం: ఆ సమయంలో తూర్పు దిగంతంలో పన్నెండు రాశుల్లో ఏది ఉదయిస్తోంది (మీ\n"
                     "<strong>లగ్నం</strong>), సూర్యుడు, చంద్రుడు, కుజుడు, బుధుడు, గురువు, శుక్రుడు, శని, రాహువు, కేతువు\n"
                     "ఏ రాశుల్లో, 27 నక్షత్రాల్లో ఎక్కడ ఉన్నారు. వైదిక జ్యోతిషం మిగతా అంతా — వ్యక్తిత్వం, జీవితంలోని\n"
                     "పన్నెండు రంగాలు, అన్నింటికంటే ముఖ్యంగా దశల ద్వారా <em>సమయం</em> — ఈ ఒక్క చక్రం నుండే చదువుతుంది.\n"
                     "మా జాతకం నిమిషం వరకు ఖచ్చితంగా లెక్కించబడుతుంది, పూర్తిగా ఉచితం.</p>"),
        "fk.cta1": "ఇప్పుడే నా ఉచిత జాతకం వేయండి",
        "fk.need": ("<p>మీ పుట్టిన <strong>తేదీ</strong>, <strong>సమయం</strong>, <strong>ప్రదేశం</strong> కావాలి.\n"
                    "సైన్ ఇన్ అక్కర్లేదు, కార్డ్ అక్కర్లేదు.</p>"),
        "fk.includes": ("<h2>మీ ఉచిత జాతకంలో ఏమేమి ఉంటాయి</h2>\n"
                        "<ul>\n"
                        "<li><strong>లగ్న చక్రం (D1)</strong> ఉత్తర భారత లేదా దక్షిణ భారత శైలిలో — ఒక్క ట్యాప్‌తో మార్చుకోండి.</li>\n"
                        "<li><strong>గ్రహ స్థితులు</strong>: తొమ్మిది గ్రహాలు, లగ్నం — రాశి, అంశ, భావం, బలం, వక్ర స్థితి;\n"
                        "దానితో పాటు మీ చంద్రుని నక్షత్రం, పాదం.</li>\n"
                        "<li><strong>పన్నెండు భావాలు</strong>, ప్రతి భావంలో ఉన్న గ్రహాలు.</li>\n"
                        "<li><strong>వింశోత్తరి దశ</strong>: మీ ప్రస్తుత మహాదశ, అంతర్దశ వాటి తేదీలతో,\n"
                        "దృశ్య కాలరేఖపై.</li>\n"
                        "<li><strong>వర్గ చక్రాలు</strong>: {vargas}.</li>\n"
                        "<li><strong>అష్టకవర్గు</strong>: ప్రతి భావానికి సర్వాష్టకవర్గు, భిన్నాష్టకవర్గు బిందువులు.</li>\n"
                        "<li><strong>జైమిని</strong> చర కారకాలు (ఆత్మకారకుడి నుండి దారాకారకుడి వరకు), ఆరూఢ పదాలు; లగ్నం,\n"
                        "చంద్రుడు, సూర్యుడు మూడింటి నుండి కలిపి చూసే <strong>సుదర్శన చక్రం</strong>.</li>\n"
                        "<li><strong>దోష పరిశీలన</strong>: కుజ దోషం, ఏలినాటి శని, కాలసర్ప దోషం.</li>\n"
                        "<li>మీ జాతకానికి, ప్రస్తుత దశకు తగిన <strong>రత్నాలు, పరిహారాల</strong> సూచనలు.</li>\n"
                        "<li>మీ జాతకపు డ్యాష్‌బోర్డ్‌లో <strong>దైనందిన ఫలం</strong>, నేటి పంచాంగం.</li>\n"
                        "</ul>\n"
                        "<p>అంతా <strong>నిరయన రాశిచక్రం, లాహిరి అయనాంశ</strong>, సంపూర్ణ రాశి భావ పద్ధతిలో, స్విస్\n"
                        "ఎఫెమెరిస్ ఆధారంగా లెక్కించబడుతుంది. ఉచిత ఖాతాతో జాతకాలను భద్రపరచుకోవచ్చు, జాతకాన్ని ఇంగ్లీష్ లేదా\n"
                        "హిందీలో PDF గా డౌన్‌లోడ్ చేసుకోవచ్చు, AI జ్యోతిష్యుడిని మొదటి ప్రశ్నలు ఉచితంగా అడగవచ్చు.</p>"),
        "fk.read": ("<h2>మీ జాతకాన్ని ఎలా చదవాలి</h2>\n"
                    "<h3>1. లగ్నంతో మొదలుపెట్టండి</h3>\n"
                    "<p>మొదటి భావం అంటే పుట్టిన సమయంలో ఉదయిస్తున్న రాశి. ఉత్తర భారత చక్రంలో ఇది పైన మధ్యలో ఉండే\n"
                    "వజ్రాకార గడి; ప్రతి గడిలో రాసిన సంఖ్య <em>రాశి</em>ని సూచిస్తుంది (1 = మేషం … 12 = మీనం),\n"
                    "భావాన్ని కాదు. దక్షిణ భారత చక్రంలో రాశులు స్థిరమైన గడుల్లో ఉంటాయి, లగ్నాన్ని గుర్తుతో చూపిస్తారు.\n"
                    "లగ్నం, లగ్నాధిపతి శరీరం, స్వభావం, జీవితపు మొత్తం దిశను సూచిస్తాయి.</p>\n"
                    "<h3>2. మీ చంద్ర రాశి, నక్షత్రం గమనించండి</h3>\n"
                    "<p>భారతీయ వాడుకలో మీ <strong>రాశి</strong> అంటే చంద్రుడు ఉన్న రాశి, సూర్యుడిది కాదు. రాశి ఫలాలు,\n"
                    "ఏలినాటి శని, జాతక పొంతన అన్నీ ఈ రాశి నుండే చూస్తారు; చంద్రుని నక్షత్రం మీ వింశోత్తరి దశ\n"
                    "ఎక్కడ మొదలవుతుందో నిర్ణయిస్తుంది.</p>\n"
                    "<h3>3. భావాల వారీగా గ్రహాలను చదవండి</h3>\n"
                    "<p>ప్రతి భావం జీవితంలో ఒక రంగం: 1వది స్వయం, 2వది ధనం, కుటుంబం, 3వది ధైర్యం, తోబుట్టువులు,\n"
                    "4వది ఇల్లు, తల్లి, 5వది సంతానం, బుద్ధి, 6వది ఆరోగ్యం, ప్రత్యర్థులు, 7వది వివాహం,\n"
                    "భాగస్వామ్యం, 8వది ఆయుష్షు, ఆకస్మిక మార్పులు, 9వది భాగ్యం, ధర్మం, 10వది వృత్తి,\n"
                    "11వది లాభాలు, 12వది వ్యయం, మోక్షం. ఒక గ్రహం తాను ఉన్న భావంపై, తాను అధిపతిగా ఉన్న భావాలపై\n"
                    "ప్రభావం చూపుతుంది; దాని బలం (ఉచ్చ, స్వక్షేత్రం, నీచ) అది ఎంత బాగా ఫలితం ఇవ్వగలదో చెబుతుంది.</p>\n"
                    "<h3>4. నడుస్తున్న దశను చూడండి</h3>\n"
                    "<p>దశ <em>ఎప్పుడు</em> అనేది చెబుతుంది. మహాదశాధిపతి, దానిలోని అంతర్దశాధిపతి — ఈ కాలంలో ఈ\n"
                    "గ్రహాల భావాలే చురుకుగా ఉంటాయి; అందుకే ఒకేలాంటి జాతకాలు ఉన్న ఇద్దరికి సంవత్సరాలు చాలా భిన్నంగా\n"
                    "గడవచ్చు.</p>\n"
                    "<h3>5. దోషాలను సందర్భంతో చూడండి</h3>\n"
                    "<p>దోషం చదవాల్సిన ఒక అమరిక, తీర్పు కాదు. కుజ దోషానికి శాస్త్రీయ పరిహారాలు ఉన్నాయి; ఏలినాటి శని\n"
                    "ప్రతి ఒక్కరి జీవితంలో రెండు మూడు సార్లు వచ్చే ఏడున్నర సంవత్సరాల గోచారం. దోష నివేదిక తాను కనుగొన్న\n"
                    "పరిహారాలను పేరుతో సహా చూపిస్తుంది.</p>"),
        "fk.cta2": "నా జన్మ జాతకం వేయండి — ఉచితం",
        "fk.faq_h2": "<h2>తరచుగా అడిగే ప్రశ్నలు</h2>",
        "varga.D1": "రాశి", "varga.D3": "ద్రేక్కాణం", "varga.D7": "సప్తాంశ",
        "varga.D9": "నవాంశ", "varga.D10": "దశాంశ", "varga.D12": "ద్వాదశాంశ",
    },

    "kn": {
        "tool.panchang": "ಪಂಚಾಂಗ",
        "tool.rahu-kaal": "ರಾಹು ಕಾಲ",
        "tool.choghadiya": "ಚೌಘಡಿಯಾ",
        "when": "{vara}, {date} · {place} · IST",
        "limb.until": "{name} {time} ರವರೆಗೆ",
        "limb.then": "ನಂತರ {name}",
        "limb.pada": "ಪಾದ",
        "paksha.full": "{paksha} ಪಕ್ಷ",
        "cities.heading": "ಇತರ ನಗರಗಳ {tool}",
        "links.heading": "ಇನ್ನಷ್ಟು ಉಚಿತ ಸಾಧನಗಳು",
        "links.tool_in_city": "{city} {tool}",
        "links.milan": "ಜಾತಕ ಹೊಂದಾಣಿಕೆ (36 ಗುಣ)",
        "links.kundali": "ಉಚಿತ ಜನ್ಮ ಜಾತಕ",
        "links.muhurat": "ಮುಹೂರ್ತ ಹುಡುಕಿ",
        "links.rashifal": "ಇಂದಿನ ರಾಶಿ ಭವಿಷ್ಯ",
        "links.vrat": "{city} ನಗರದಲ್ಲಿ ಇಂದಿನ ವ್ರತ ಮತ್ತು ಹಬ್ಬಗಳು",
        "nf.title": "ನಗರ ಸಿಗಲಿಲ್ಲ — {brand}",
        "nf.desc": "{tool}: ಈ ನಗರ ನಮ್ಮ ಪಟ್ಟಿಯಲ್ಲಿ ಇಲ್ಲ.",
        "nf.body": ("<h1>{tool}: ನಗರ ಸಿಗಲಿಲ್ಲ</h1>"
                    "<p>“{slug}” ಗಾಗಿ ನಮ್ಮಲ್ಲಿ ಇನ್ನೂ ಪುಟವಿಲ್ಲ. ಕೆಳಗಿನ ಪಟ್ಟಿಯಿಂದ ನಿಮ್ಮ ನಗರವನ್ನು ಆಯ್ಕೆಮಾಡಿ, ಅಥವಾ "
                    '<a href="{app}">{tool} ಸಾಧನವನ್ನು ತೆರೆಯಿರಿ</a> — ಅದರಲ್ಲಿ ಜಗತ್ತಿನ '
                    "ಯಾವುದೇ ಸ್ಥಳವನ್ನು ಆಯ್ಕೆಮಾಡಬಹುದು.</p>"),

        "p.title": "ಇಂದಿನ ಪಂಚಾಂಗ {city}, {date} — ತಿಥಿ, ನಕ್ಷತ್ರ, ರಾಹು ಕಾಲ | {brand}",
        "p.desc": ("{city} ಇಂದಿನ ಪಂಚಾಂಗ ({vara}, {date}): {paksha_full} {tithi} ತಿಥಿ, "
                   "{nakshatra} ನಕ್ಷತ್ರ, ಸೂರ್ಯೋದಯ {sunrise}, ರಾಹು ಕಾಲ {rahu}. ಸ್ವಿಸ್ ಎಫೆಮೆರಿಸ್ ಆಧಾರಿತ ನಿಖರ ಲೆಕ್ಕ."),
        "p.h1": "<h1>{city} ಇಂದಿನ ಪಂಚಾಂಗ</h1>",
        "p.sub": '<p class="hi">{city} ಪಂಚಾಂಗ ಇಂದು — ತಿಥಿ, ನಕ್ಷತ್ರ, ಯೋಗ, ಕರಣ</p>',
        "p.box": ("<div class=\"box\"><p>ಇಂದು {city} ನಗರದಲ್ಲಿ <strong>{paksha_full} {tithi}</strong> ತಿಥಿ,\n"
                  "ಚಂದ್ರನು <strong>{nakshatra}</strong> ನಕ್ಷತ್ರದಲ್ಲಿದ್ದಾನೆ. ರಾಹು ಕಾಲ <strong>{rahu}</strong> —\n"
                  "ಈ ಅವಧಿಯಲ್ಲಿ ಯಾವುದೇ ಹೊಸ ಕೆಲಸವನ್ನು ಆರಂಭಿಸಬೇಡಿ.</p></div>"),
        "p.r_vara": "ವಾರ",
        "p.r_tithi": "ತಿಥಿ",
        "p.r_paksha": "ಪಕ್ಷ",
        "p.r_nakshatra": "ನಕ್ಷತ್ರ",
        "p.r_yoga": "ಯೋಗ",
        "p.r_karana": "ಕರಣ",
        "p.r_sunrise": "ಸೂರ್ಯೋದಯ",
        "p.r_sunset": "ಸೂರ್ಯಾಸ್ತ",
        "p.r_moonrise": "ಚಂದ್ರೋದಯ",
        "p.r_moonset": "ಚಂದ್ರಾಸ್ತ",
        "p.r_moon_sign": "ಚಂದ್ರ ರಾಶಿ",
        "p.r_rahu": "ರಾಹು ಕಾಲ",
        "p.r_yama": "ಯಮಗಂಡ ಕಾಲ",
        "p.r_gulika": "ಗುಳಿಕ ಕಾಲ",
        "p.r_abhijit": "ಅಭಿಜಿತ್ ಮುಹೂರ್ತ",
        "p.v_vara": "{vara}",
        "p.v_paksha": "{paksha_full}",
        "p.no_moonrise": "ಈ ದಿನ ಚಂದ್ರೋದಯ ಇಲ್ಲ",
        "p.no_moonset": "ಈ ದಿನ ಚಂದ್ರಾಸ್ತ ಇಲ್ಲ",
        "p.no_abhijit": "ಬುಧವಾರ ಅಭಿಜಿತ್ ಮುಹೂರ್ತವನ್ನು ಪರಿಗಣಿಸುವುದಿಲ್ಲ",
        "p.note": ("<p>ಎಲ್ಲಾ ಸಮಯಗಳು {place} ({lat}°N, {lon}°E) ಸ್ಥಳಕ್ಕೆ, ಭಾರತೀಯ ಪ್ರಮಾಣಿತ\n"
                   "ಸಮಯದಲ್ಲಿ (IST) ಇವೆ. ಪಂಚಾಂಗದ ದಿನ ಸೂರ್ಯೋದಯದಿಂದ ಮರುದಿನದ ಸೂರ್ಯೋದಯದವರೆಗೆ ಇರುತ್ತದೆ, ಆದ್ದರಿಂದ ತಿಥಿ\n"
                   "ಅಥವಾ ನಕ್ಷತ್ರ ಮಧ್ಯರಾತ್ರಿಯ ನಂತರವೂ ಮುಗಿಯಬಹುದು. ಸೂರ್ಯೋದಯವನ್ನು ಭಾರತೀಯ ಪಂಚಾಂಗಗಳಂತೆ ಸೂರ್ಯಬಿಂಬದ\n"
                   "ಮೇಲಂಚು ಕಾಣುವ ಕ್ಷಣದಿಂದ (ವಾತಾವರಣದ ವಕ್ರೀಭವನ ಸಹಿತ) ಲೆಕ್ಕಿಸಲಾಗಿದೆ; ನಕ್ಷತ್ರ ಮತ್ತು ಯೋಗಗಳು ಲಾಹಿರಿ ಅಯನಾಂಶ ಆಧಾರಿತ.</p>"),
        "p.cta": "ಪೂರ್ಣ ಪಂಚಾಂಗ ತೆರೆಯಿರಿ — ಯಾವುದೇ ನಗರ, ಯಾವುದೇ ದಿನಾಂಕ",
        "p.limbs": ("<h2>ಪಂಚಾಂಗದ ಐದು ಅಂಗಗಳು</h2>\n"
                    "<p><strong>ತಿಥಿ</strong> ಚಾಂದ್ರ ದಿನ — ಚಂದ್ರನು ಸೂರ್ಯನಿಗಿಂತ ಪ್ರತಿ 12° ಮುಂದೆ ಸಾಗಿದಾಗ ಒಂದು ತಿಥಿ.\n"
                    "<strong>ನಕ್ಷತ್ರ</strong> 27ರಲ್ಲಿ ಚಂದ್ರನು ಇರುವ ನಕ್ಷತ್ರ. <strong>ಯೋಗ</strong> ಸೂರ್ಯ ಮತ್ತು\n"
                    "ಚಂದ್ರರ ರೇಖಾಂಶಗಳ ಮೊತ್ತದಿಂದ ಬರುತ್ತದೆ, ಮತ್ತು <strong>ಕರಣ</strong> ಅರ್ಧ ತಿಥಿ.\n"
                    "<strong>ವಾರ</strong> ವಾರದ ದಿನ, ಇದನ್ನು ಸೂರ್ಯೋದಯದಿಂದ ಎಣಿಸಲಾಗುತ್ತದೆ. ಈ ಐದೂ ಸೇರಿ\n"
                    "ಪಂಚಾಂಗ (“ಐದು ಅಂಗಗಳು”) ಎನಿಸುತ್ತವೆ; ಯಾವುದೇ ಶುಭ ಕಾರ್ಯಕ್ಕೆ ಮೊದಲು ಇವನ್ನು ನೋಡಲಾಗುತ್ತದೆ.</p>"),

        "rk.title": "ರಾಹು ಕಾಲ ಇಂದು {city} — {rahu}, {date} | {brand}",
        "rk.desc": ("{city} ನಗರದಲ್ಲಿ ಇಂದು ({vara}, {date}) ರಾಹು ಕಾಲ {rahu}. ಜೊತೆಗೆ ಯಮಗಂಡ "
                    "{yama} ಮತ್ತು ಗುಳಿಕ ಕಾಲ {gulika}, "
                    "ಈ ವಾರದ ಸಮಯಗಳು ಮತ್ತು ರಾಹು ಕಾಲದ ಅರ್ಥ."),
        "rk.h1": "<h1>{city} ರಾಹು ಕಾಲ ಇಂದು</h1>",
        "rk.sub": '<p class="hi">ಇಂದಿನ ರಾಹು ಕಾಲ, ಯಮಗಂಡ, ಗುಳಿಕ ಕಾಲ — {city}</p>',
        "rk.r_rahu": "ರಾಹು ಕಾಲ",
        "rk.r_yama": "ಯಮಗಂಡ ಕಾಲ",
        "rk.r_gulika": "ಗುಳಿಕ ಕಾಲ",
        "rk.r_abhijit": "ಅಭಿಜಿತ್ ಮುಹೂರ್ತ",
        "rk.r_sun": "ಸೂರ್ಯೋದಯ / ಸೂರ್ಯಾಸ್ತ",
        "rk.no_abhijit": "ಬುಧವಾರ ಪರಿಗಣಿಸುವುದಿಲ್ಲ",
        "rk.cta": "ಯಾವುದೇ ನಗರ ಅಥವಾ ದಿನಾಂಕದ ರಾಹು ಕಾಲ ನೋಡಿ",
        "rk.about": ("<h2>ರಾಹು ಕಾಲ ಎಂದರೇನು?</h2>\n"
                     "<p>ರಾಹು ಕಾಲ ಪ್ರತಿದಿನ ಸುಮಾರು ಒಂದೂವರೆ ಗಂಟೆಯ ಅವಧಿ; ಸಂಪ್ರದಾಯದ ಪ್ರಕಾರ ಇದು ರಾಹುವಿನ (ಚಂದ್ರನ\n"
                     "ಉತ್ತರ ಪಾತ) ಆಳ್ವಿಕೆಯ ಸಮಯ. ಸೂರ್ಯೋದಯದಿಂದ ಸೂರ್ಯಾಸ್ತದವರೆಗಿನ ಹಗಲನ್ನು ಎಂಟು ಸಮ ಭಾಗಗಳಾಗಿ\n"
                     "ವಿಂಗಡಿಸಲಾಗುತ್ತದೆ, ಅವುಗಳಲ್ಲಿ ಒಂದು ಭಾಗ ರಾಹುವಿನದು. ಯಾವ ಭಾಗ ಎಂಬುದು ವಾರವನ್ನು ಅವಲಂಬಿಸಿದೆ: ಭಾನುವಾರ\n"
                     "8ನೇ, ಸೋಮವಾರ 2ನೇ, ಮಂಗಳವಾರ 7ನೇ, ಬುಧವಾರ 5ನೇ, ಗುರುವಾರ 6ನೇ, ಶುಕ್ರವಾರ 4ನೇ ಮತ್ತು\n"
                     "ಶನಿವಾರ 3ನೇ ಭಾಗ.</p>\n"
                     "<p>ಇದು ನಿಜವಾದ ಸೂರ್ಯೋದಯ ಮತ್ತು ಸೂರ್ಯಾಸ್ತವನ್ನು ಅನುಸರಿಸುವುದರಿಂದ, ರಾಹು ಕಾಲ ಪ್ರತಿ ನಗರದಲ್ಲೂ ಬೇರೆ ಮತ್ತು\n"
                     "ವರ್ಷವಿಡೀ ಬದಲಾಗುತ್ತದೆ — ಆದ್ದರಿಂದ “ಸೋಮವಾರ 7:30–9:00” ಎಂಬಂತಹ ಸ್ಥಿರ ಪಟ್ಟಿ ಕೇವಲ ಅಂದಾಜು.\n"
                     "ಸಂಪ್ರದಾಯದಂತೆ ರಾಹು ಕಾಲದಲ್ಲಿ ಹೊಸ ಕಾರ್ಯ ಆರಂಭ, ಒಪ್ಪಂದಕ್ಕೆ ಸಹಿ, ಪ್ರಯಾಣ ಆರಂಭ ಅಥವಾ ದೊಡ್ಡ\n"
                     "ಖರೀದಿಗಳನ್ನು ತಪ್ಪಿಸಲಾಗುತ್ತದೆ; ಈಗಾಗಲೇ ನಡೆಯುತ್ತಿರುವ ಕೆಲಸ ಮುಂದುವರಿಯಬಹುದು. ಯಮಗಂಡ ಮತ್ತು ಗುಳಿಕ\n"
                     "ಕಾಲಗಳು ಹಗಲಿನ ಇನ್ನೆರಡು ಎಂಟನೇ ಭಾಗಗಳು; ಅವುಗಳಲ್ಲೂ ಇದೇ ರೀತಿಯ ಎಚ್ಚರಿಕೆ ವಹಿಸಲಾಗುತ್ತದೆ.</p>"),
        "rk.week_h2": "<h2>{city} ನಗರದಲ್ಲಿ ಈ ವಾರದ ರಾಹು ಕಾಲ</h2>",
        "rk.th_day": "ದಿನ",
        "rk.th_rahu": "ರಾಹು ಕಾಲ",
        "rk.th_yama": "ಯಮಗಂಡ",
        "rk.th_gulika": "ಗುಳಿಕ",

        "ch.title": "ಇಂದಿನ ಚೌಘಡಿಯಾ {city}, {date} — ಹಗಲು ಮತ್ತು ರಾತ್ರಿ ಸಮಯ | {brand}",
        "ch.desc": ("{city} ಇಂದಿನ ಚೌಘಡಿಯಾ ({vara}, {date}): ಹಗಲು ಮತ್ತು ರಾತ್ರಿಯ ಎಲ್ಲಾ 16 ಮುಹೂರ್ತಗಳು — "
                    "ಅಮೃತ, ಶುಭ, ಲಾಭ, ಚರ, ರೋಗ, ಕಾಲ, ಉದ್ವೇಗ — ಸೂರ್ಯೋದಯ {sunrise} ರಿಂದ ನಿಖರ ಆರಂಭ ಮತ್ತು ಅಂತ್ಯ ಸಮಯಗಳೊಂದಿಗೆ."),
        "ch.h1": "<h1>{city} ಇಂದಿನ ಚೌಘಡಿಯಾ</h1>",
        "ch.sub": '<p class="hi">{city} ಚೌಘಡಿಯಾ ಮುಹೂರ್ತ ಇಂದು — ಹಗಲು ಮತ್ತು ರಾತ್ರಿ</p>',
        "ch.first_good": "{name} — {time} ರಿಂದ",
        "ch.none": "ಯಾವುದೂ ಇಲ್ಲ",
        "ch.box": ("<div class=\"box\"><p>ಸೂರ್ಯೋದಯ <strong>{sunrise}</strong>, ಸೂರ್ಯಾಸ್ತ\n"
                   "<strong>{sunset}</strong>. ಹಗಲಿನ ಮೊದಲ ಶುಭ ಚೌಘಡಿಯಾ:\n"
                   "<strong>{first_good}</strong>.</p></div>"),
        "ch.day_h2": "<h2>ಹಗಲಿನ ಚೌಘಡಿಯಾ</h2>",
        "ch.night_h2": "<h2>ರಾತ್ರಿಯ ಚೌಘಡಿಯಾ</h2>",
        "ch.th": "<tr><th>ಸಮಯ</th><th>ಚೌಘಡಿಯಾ</th><th>ಸ್ವಭಾವ</th></tr>",
        "ch.row": ('<tr><td>{when}</td><td class="{cls}"><strong>{name}</strong>'
                   "<small>ಅಧಿಪತಿ: {ruler}</small></td>"
                   "<td>{quality}<small>{desc}</small></td></tr>"),
        "ch.cta": "ಲೈವ್ ಚೌಘಡಿಯಾ ಗಡಿಯಾರ ತೆರೆಯಿರಿ",
        "ch.about": ("<h2>ಚೌಘಡಿಯಾ ಹೇಗೆ ಲೆಕ್ಕಿಸಲಾಗುತ್ತದೆ</h2>\n"
                     "<p>ಸೂರ್ಯೋದಯದಿಂದ ಸೂರ್ಯಾಸ್ತದವರೆಗಿನ ಹಗಲು ಮತ್ತು ಸೂರ್ಯಾಸ್ತದಿಂದ ಮರುದಿನದ ಸೂರ್ಯೋದಯದವರೆಗಿನ ರಾತ್ರಿ —\n"
                     "ಎರಡನ್ನೂ ಎಂಟು ಸಮ ಭಾಗಗಳಾಗಿ ವಿಂಗಡಿಸಲಾಗುತ್ತದೆ; ಇವನ್ನು ಚೌಘಡಿಯಾ (“ನಾಲ್ಕು ಘಳಿಗೆ”) ಎನ್ನುತ್ತಾರೆ.\n"
                     "ಪ್ರತಿಯೊಂದಕ್ಕೂ ಒಬ್ಬ ಗ್ರಹ ಅಧಿಪತಿ, ಮತ್ತು ಅದರ ಸ್ವಭಾವಕ್ಕೆ ತಕ್ಕ ಹೆಸರು: <strong>ಅಮೃತ</strong>,\n"
                     "<strong>ಶುಭ</strong> ಮತ್ತು <strong>ಲಾಭ</strong> ಶುಭ, <strong>ಚರ</strong> ಮಧ್ಯಮ ಮತ್ತು\n"
                     "ಪ್ರಯಾಣಕ್ಕೆ ಒಳ್ಳೆಯದು, ಆದರೆ <strong>ರೋಗ</strong>, <strong>ಕಾಲ</strong> ಮತ್ತು\n"
                     "<strong>ಉದ್ವೇಗ</strong> ಸಮಯದಲ್ಲಿ ಹೊಸ ಆರಂಭಗಳನ್ನು ತಪ್ಪಿಸಲಾಗುತ್ತದೆ. ಕ್ರಮ ವಾರದ ಅಧಿಪತಿಯಿಂದ\n"
                     "ಆರಂಭವಾಗುವುದರಿಂದ ಪ್ರತಿದಿನ ಬದಲಾಗುತ್ತದೆ — ಮತ್ತು ಪ್ರತಿ ಭಾಗದ ಅವಧಿ {city} ನಗರದಲ್ಲಿ ಹಗಲಿನ ನಿಜವಾದ\n"
                     "ಉದ್ದವನ್ನು ಅನುಸರಿಸುತ್ತದೆ.</p>"),

        "km.title": "ಜಾತಕ ಹೊಂದಾಣಿಕೆ — ಅಷ್ಟಕೂಟ ಗುಣ ಮಿಲನ ({total} ಗುಣ) ವಿವರಣೆ | {brand}",
        "km.desc": ("ಜಾತಕ ಹೊಂದಾಣಿಕೆ ಹೇಗೆ: ಅಷ್ಟಕೂಟ ಗುಣ ಮಿಲನದ 8 ಕೂಟಗಳು, ಒಟ್ಟು {total} ಗುಣ, ಮದುವೆಗೆ "
                    "ಎಷ್ಟು ಗುಣ ಒಳ್ಳೆಯದು, ಕುಜ ದೋಷ ಪರಿಶೀಲನೆ. ಇಂಗ್ಲಿಷ್ ಮತ್ತು ಹಿಂದಿಯಲ್ಲಿ ಉಚಿತ "
                    "ಆನ್‌ಲೈನ್ ಹೊಂದಾಣಿಕೆ."),
        "km.crumb": "ಜಾತಕ ಹೊಂದಾಣಿಕೆ",
        "km.intro": ("<h1>ಜಾತಕ ಹೊಂದಾಣಿಕೆ: ಅಷ್ಟಕೂಟ ಗುಣ ಮಿಲನದ ವಿವರಣೆ</h1>\n"
                     "<p class=\"hi\">ಕುಂಡಲಿ ಮಿಲನ — ವಿವಾಹಕ್ಕೆ {total} ಗುಣಗಳ ಹೊಂದಾಣಿಕೆ</p>\n"
                     "<p>ಜಾತಕ ಹೊಂದಾಣಿಕೆ (ಕುಂಡಲಿ ಮಿಲನ) ವಿವಾಹದ ಅನುಕೂಲತೆಯನ್ನು ನೋಡುವ ಸಾಂಪ್ರದಾಯಿಕ ವೈದಿಕ ವಿಧಾನ.\n"
                     "ಉತ್ತರ ಭಾರತದಲ್ಲಿ ಹೆಚ್ಚು ಬಳಕೆಯಲ್ಲಿರುವ ವಿಧಾನ <strong>ಅಷ್ಟಕೂಟ ಗುಣ ಮಿಲನ</strong>: ವಧು ಮತ್ತು ವರನ\n"
                     "ಜಾತಕಗಳಲ್ಲಿ ಎಂಟು ಅಂಶಗಳನ್ನು (<em>ಕೂಟಗಳು</em>) ಹೋಲಿಸಿ, ಒಟ್ಟು <strong>{total} ಅಂಕಗಳಿಗೆ (ಗುಣಗಳು)</strong>\n"
                     "ಅಂಕ ನೀಡಲಾಗುತ್ತದೆ. ಇವೆಲ್ಲವನ್ನೂ <strong>ಚಂದ್ರ</strong>ನಿಂದ — ಜನನದ ಸಮಯದಲ್ಲಿ ಅವನ ರಾಶಿ ಮತ್ತು\n"
                     "ನಕ್ಷತ್ರದಿಂದ — ನೋಡಲಾಗುತ್ತದೆ; ಆದ್ದರಿಂದ ಸರಿಯಾದ ಜನ್ಮ ದಿನಾಂಕ ಮತ್ತು ಸ್ಥಳ ಅಗತ್ಯ, ಆದರೆ ಜನ್ಮ ಸಮಯದ\n"
                     "ಪ್ರಭಾವ ಬಹಳ ಕಡಿಮೆ.</p>"),
        "km.cta1": "ಈಗಲೇ ಎರಡು ಜಾತಕಗಳನ್ನು ಹೊಂದಿಸಿ — ಉಚಿತ",
        "km.naam": ('<p>ಜನ್ಮ ಸಮಯ ಗೊತ್ತಿಲ್ಲವೇ? <a href="{href}">ಹೆಸರಿನಿಂದ ಜಾತಕ ಹೊಂದಾಣಿಕೆ</a> ಪ್ರಯತ್ನಿಸಿ — '
                    "ಪ್ರತಿ ಹೆಸರಿನ ಮೊದಲ ಅಕ್ಷರದಿಂದ ಮಾಡುವ ಸಾಂಪ್ರದಾಯಿಕ ಹೊಂದಾಣಿಕೆ.</p>"),
        "km.kootas_h2": "<h2>ಎಂಟು ಕೂಟಗಳು ಮತ್ತು ಅವುಗಳ ಗುಣಗಳು</h2>",
        "km.th": "<tr><th>ಕೂಟ</th><th>ಗುಣ</th><th>ಏನನ್ನು ನೋಡುತ್ತದೆ</th></tr>",
        "km.row": "<tr><td><strong>{name}</strong></td><td>{pts}</td><td>{text}</td></tr>",
        "km.total": "ಒಟ್ಟು",
        "km.score_h2": "<h2>ಎಷ್ಟು ಗುಣ ಹೊಂದಿದರೆ ಒಳ್ಳೆಯದು?</h2>",
        "km.score_th": "<tr><th>ಗುಣಗಳು</th><th>ಸಾಂಪ್ರದಾಯಿಕ ಅರ್ಥ</th></tr>",
        "km.below": "{n}ಕ್ಕಿಂತ ಕಡಿಮೆ",
        "km.band0": "ಶಿಫಾರಸು ಮಾಡುವುದಿಲ್ಲ",
        "km.band1": "ಸ್ವೀಕಾರಾರ್ಹ",
        "km.band2": "ಉತ್ತಮ",
        "km.band3": "ಅತ್ಯುತ್ತಮ",
        "km.score_p": ("<p>18 ಗುಣ ಸಾಂಪ್ರದಾಯಿಕ ಕನಿಷ್ಠ ಮಿತಿ. ಒಟ್ಟು ಅಂಕ ಮಾತ್ರ ಪೂರ್ಣ ಚಿತ್ರಣ ನೀಡುವುದಿಲ್ಲ: ಹೆಚ್ಚು ಅಂಕಗಳಿದ್ದರೂ\n"
                       "ಪರಿಹಾರವಿಲ್ಲದ ನಾಡಿ ಅಥವಾ ಭಕೂಟ ದೋಷವಿದ್ದರೆ ಎಚ್ಚರಿಕೆಯಿಂದ ನೋಡಲಾಗುತ್ತದೆ, ಮತ್ತು ಕಡಿಮೆ ಅಂಕಗಳಿದ್ದರೂ\n"
                       "ಉತ್ತಮ ಗ್ರಹ ಮೈತ್ರಿ ಇದ್ದು ಯಾವುದೇ ದೋಷವಿಲ್ಲದಿದ್ದರೆ ಹೊಂದಾಣಿಕೆಯನ್ನು ಹಲವು ಬಾರಿ ಸ್ವೀಕಾರಾರ್ಹವೆಂದು ಪರಿಗಣಿಸಲಾಗುತ್ತದೆ.\n"
                       "ಈ ಮಿತಿಗಳು ದೀರ್ಘ ಇತಿಹಾಸವಿರುವ ಸಂಪ್ರದಾಯ, ಅಳತೆಯಲ್ಲ — ಇವು ಮಾರ್ಗದರ್ಶನ, ಯಾವುದೇ ಸಂಬಂಧದ ಮೇಲಿನ ಅಂತಿಮ ತೀರ್ಪಲ್ಲ.</p>"),
        "km.ord1": "{n}ನೇ",
        "km.ord2": "{n}ನೇ",
        "km.ordn": "{n}ನೇ",
        "km.or": " ಅಥವಾ ",
        "km.mangal": ("<h2>ಕುಜ ದೋಷ (ಮಾಂಗಲಿಕ)</h2>\n"
                      "<p>ಕುಜ ದೋಷವನ್ನು 36 ಗುಣಗಳಿಂದ ಪ್ರತ್ಯೇಕವಾಗಿ ನೋಡಲಾಗುತ್ತದೆ. <strong>ಲಗ್ನ</strong>,\n"
                      "<strong>ಚಂದ್ರ</strong> ಅಥವಾ <strong>ಶುಕ್ರ</strong>ನಿಂದ ಎಣಿಸಿದಾಗ ಕುಜನು {houses} ಭಾವದಲ್ಲಿದ್ದರೆ\n"
                      "ಜಾತಕದಲ್ಲಿ ಕುಜ ದೋಷವಿದೆ ಎನ್ನಲಾಗುತ್ತದೆ. ಶಾಸ್ತ್ರಗಳು ಕೆಲವು ರಾಶಿ ಸ್ಥಿತಿಗಳಿಗೆ ವಿನಾಯಿತಿ ನೀಡುತ್ತವೆ (ಉದಾಹರಣೆಗೆ\n"
                      "1ನೇ ಭಾವದಲ್ಲಿ ಸ್ವರಾಶಿ ಮೇಷದಲ್ಲಿರುವ ಕುಜ), ಮತ್ತು ಕುಜನ ಮೇಲೆ ಗುರುವಿನ ದೃಷ್ಟಿ ದೋಷವನ್ನು ತಗ್ಗಿಸುತ್ತದೆ\n"
                      "ಎನ್ನಲಾಗುತ್ತದೆ. ವಧು-ವರರು <strong>ಇಬ್ಬರೂ</strong> ಕುಜ ದೋಷವುಳ್ಳವರಾದರೆ ಸಂಪ್ರದಾಯದಂತೆ ದೋಷ\n"
                      "ಪರಸ್ಪರ ರದ್ದಾಗುತ್ತದೆ — ಆದ್ದರಿಂದಲೇ ಕುಜ ದೋಷವಿರುವವರಿಗೆ ಕುಜ ದೋಷವಿರುವವರೊಂದಿಗೆ ಸಂಬಂಧ ಮಾಡಲಾಗುತ್ತದೆ.\n"
                      "ಇದು ಲಗ್ನವನ್ನು ಅವಲಂಬಿಸಿರುವುದರಿಂದ ಕುಜ ದೋಷಕ್ಕೆ ವಿಶ್ವಾಸಾರ್ಹ ಜನ್ಮ ಸಮಯ ಅಗತ್ಯ.</p>"),
        "km.how": ("<h2>ನಮ್ಮ ಹೊಂದಾಣಿಕೆ ಸಾಧನ ಹೇಗೆ ಕೆಲಸ ಮಾಡುತ್ತದೆ</h2>\n"
                   "<p>ಇಬ್ಬರ ಜನ್ಮ ದಿನಾಂಕ, ಸಮಯ ಮತ್ತು ಸ್ಥಳವನ್ನು ನಮೂದಿಸಿ. ಎರಡೂ ಜಾತಕಗಳನ್ನು ಸ್ವಿಸ್ ಎಫೆಮೆರಿಸ್‌ನಿಂದ\n"
                   "ನಿರಯನ (ಲಾಹಿರಿ ಅಯನಾಂಶ) ಪದ್ಧತಿಯಲ್ಲಿ ರಚಿಸಲಾಗುತ್ತದೆ, ಮತ್ತು ಪ್ರತಿ ಕೂಟದ ಅಂಕಗಳನ್ನು ಶಾಸ್ತ್ರೀಯ\n"
                   "ಕೋಷ್ಟಕಗಳಿಂದ ನೀಡಲಾಗುತ್ತದೆ — ಪ್ರತಿ ಪರಿಹಾರವನ್ನೂ ಹೆಸರಿಸಿ. ಪೂರ್ಣ {total} ಗುಣಗಳ ವಿವರ ಮತ್ತು\n"
                   "ಇಬ್ಬರ ಕುಜ ದೋಷ ಸ್ಥಿತಿ ಇಂಗ್ಲಿಷ್ ಅಥವಾ ಹಿಂದಿಯಲ್ಲಿ, ಉಚಿತವಾಗಿ ಮತ್ತು ಸೈನ್ ಅಪ್ ಇಲ್ಲದೆ ಸಿಗುತ್ತದೆ.</p>"),
        "km.cta2": "ಜಾತಕ ಹೊಂದಾಣಿಕೆ ತೆರೆಯಿರಿ",
        "koota.varna": "ವರ್ಣ",
        "koota.vashya": "ವಶ್ಯ",
        "koota.tara": "ತಾರಾ",
        "koota.yoni": "ಯೋನಿ",
        "koota.graha_maitri": "ಗ್ರಹ ಮೈತ್ರಿ",
        "koota.gana": "ಗಣ",
        "koota.bhakoot": "ಭಕೂಟ",
        "koota.nadi": "ನಾಡಿ",
        "koota_about.varna": ("ಚಂದ್ರ ರಾಶಿಯ ವರ್ಣದಿಂದ ಆಧ್ಯಾತ್ಮಿಕ ಮತ್ತು ಕಾರ್ಯ ಸ್ವಭಾವ. ವರನ ವರ್ಣ ವಧುವಿನ ವರ್ಣಕ್ಕಿಂತ "
                              "ಕಡಿಮೆ ಇಲ್ಲದಿದ್ದರೆ ಪೂರ್ಣ ಅಂಕ."),
        "koota_about.vashya": "ಪರಸ್ಪರ ಆಕರ್ಷಣೆ ಮತ್ತು ಪ್ರಭಾವ — ಯಾವ ರಾಶಿ ಇನ್ನೊಂದನ್ನು “ಸೆಳೆಯುತ್ತದೆ”.",
        "koota_about.tara": ("ಆರೋಗ್ಯ ಮತ್ತು ಯೋಗಕ್ಷೇಮ, ಎರಡು ಜನ್ಮ ನಕ್ಷತ್ರಗಳ ನಡುವಿನ ಎಣಿಕೆಯಿಂದ; 3ನೇ, 5ನೇ ಮತ್ತು "
                             "7ನೇ ತಾರೆಗಳು ಪ್ರತಿಕೂಲ."),
        "koota_about.yoni": ("ದೈಹಿಕ ಮತ್ತು ದಾಂಪತ್ಯ ಅನುಕೂಲತೆ; ಪ್ರತಿ ನಕ್ಷತ್ರಕ್ಕೂ ಒಂದು ಪ್ರಾಣಿ ಯೋನಿ ಇದೆ, ಮತ್ತು "
                             "ಬದ್ಧ ವೈರಿ ಪ್ರಾಣಿಗಳಿಗೆ ಶೂನ್ಯ ಅಂಕ."),
        "koota_about.graha_maitri": "ಎರಡು ಚಂದ್ರ ರಾಶಿಗಳ ಅಧಿಪತಿಗಳ ಮೈತ್ರಿ — ದಂಪತಿಗಳ ಮಾನಸಿಕ ಹೊಂದಾಣಿಕೆ.",
        "koota_about.gana": "ಸ್ವಭಾವ: ದೇವ (ದೈವಿಕ), ಮನುಷ್ಯ (ಮಾನವ) ಅಥವಾ ರಾಕ್ಷಸ (ಉಗ್ರ) ಗಣ.",
        "koota_about.bhakoot": ("ಎರಡು ಚಂದ್ರ ರಾಶಿಗಳ ಪರಸ್ಪರ ಸ್ಥಾನ. 2/12, 5/9 ಮತ್ತು 6/8 ಸ್ಥಾನಗಳು ಭಕೂಟ ದೋಷ "
                                "ಉಂಟುಮಾಡುತ್ತವೆ; ಎರಡೂ ರಾಶ್ಯಧಿಪತಿಗಳು ಒಬ್ಬರೇ ಅಥವಾ ಮಿತ್ರರಾಗಿದ್ದರೆ ಅದು ರದ್ದಾಗುತ್ತದೆ."),
        "koota_about.nadi": ("ಅತಿ ಹೆಚ್ಚು ಅಂಕಗಳ ಕೂಟ, ಆರೋಗ್ಯ ಮತ್ತು ಸಂತಾನಕ್ಕೆ ಸಂಬಂಧಿಸಿದ್ದು. ಇಬ್ಬರಿಗೂ ಒಂದೇ ನಾಡಿ "
                             "ಇದ್ದರೆ ನಾಡಿ ದೋಷ; ರಾಶಿ ಒಂದೇ ಆದರೆ ನಕ್ಷತ್ರ ಬೇರೆ, ಅಥವಾ ನಕ್ಷತ್ರ ಒಂದೇ ಆದರೆ ಪಾದ ಬೇರೆಯಾದಾಗ "
                             "ಶಾಸ್ತ್ರೀಯ ಪರಿಹಾರವಿದೆ."),

        "fk.title": "ಉಚಿತ ಜನ್ಮ ಜಾತಕ ಆನ್‌ಲೈನ್ — ಕನ್ನಡದಲ್ಲಿ ಕುಂಡಲಿ | {brand}",
        "fk.desc": ("ನಿಮ್ಮ ಜನ್ಮ ಜಾತಕವನ್ನು ಉಚಿತವಾಗಿ ರಚಿಸಿ: ಉತ್ತರ ಅಥವಾ ದಕ್ಷಿಣ ಭಾರತೀಯ ಶೈಲಿಯ ಲಗ್ನ ಕುಂಡಲಿ, ಗ್ರಹ "
                    "ಸ್ಥಿತಿ, ಚಂದ್ರ ನಕ್ಷತ್ರ, ವಿಂಶೋತ್ತರಿ ದಶೆ, ನವಾಂಶ ಮತ್ತು ಇತರ ವರ್ಗ ಕುಂಡಲಿಗಳು, ಕುಜ ದೋಷ, "
                    "ಸಾಡೇಸಾತಿ ಮತ್ತು ಕಾಳಸರ್ಪ ದೋಷ — ಕನ್ನಡ ಅಥವಾ ಇಂಗ್ಲಿಷ್‌ನಲ್ಲಿ, ಸೈನ್ ಇನ್ ಬೇಕಿಲ್ಲ."),
        "fk.crumb": "ಉಚಿತ ಜಾತಕ",
        "fk.intro": ("<h1>ಉಚಿತ ಜನ್ಮ ಜಾತಕ ಆನ್‌ಲೈನ್</h1>\n"
                     "<p class=\"hi\">ಉಚಿತ ಜನ್ಮ ಕುಂಡಲಿ — ಕನ್ನಡದಲ್ಲಿ ಜಾತಕ</p>\n"
                     "<p><strong>ಜನ್ಮ ಜಾತಕ</strong> (ಜನ್ಮ ಕುಂಡಲಿ) ನೀವು ಹುಟ್ಟಿದ ನಿಖರ ಕ್ಷಣ ಮತ್ತು ಸ್ಥಳದಲ್ಲಿ ಆಕಾಶದ ನಕ್ಷೆ:\n"
                     "ಆಗ ಪೂರ್ವ ದಿಗಂತದಲ್ಲಿ ಹನ್ನೆರಡು ರಾಶಿಗಳಲ್ಲಿ ಯಾವುದು ಉದಯಿಸುತ್ತಿತ್ತು (ನಿಮ್ಮ <strong>ಲಗ್ನ</strong>), ಮತ್ತು ಸೂರ್ಯ, ಚಂದ್ರ,\n"
                     "ಕುಜ, ಬುಧ, ಗುರು, ಶುಕ್ರ, ಶನಿ, ರಾಹು ಮತ್ತು ಕೇತು ಯಾವ ರಾಶಿಗಳಲ್ಲಿ ಮತ್ತು 27 ನಕ್ಷತ್ರಗಳಲ್ಲಿ ಎಲ್ಲಿದ್ದವು. ವೈದಿಕ ಜ್ಯೋತಿಷ\n"
                     "ಉಳಿದೆಲ್ಲವನ್ನೂ — ವ್ಯಕ್ತಿತ್ವ, ಜೀವನದ ಹನ್ನೆರಡು ಕ್ಷೇತ್ರಗಳು, ಮತ್ತು ಮುಖ್ಯವಾಗಿ ದಶೆಗಳ ಮೂಲಕ <em>ಕಾಲ</em> —\n"
                     "ಈ ಒಂದೇ ಜಾತಕದಿಂದ ನೋಡುತ್ತದೆ. ನಮ್ಮ ಜಾತಕ ನಿಮಿಷದವರೆಗೆ ನಿಖರವಾಗಿ ಲೆಕ್ಕಿಸಲ್ಪಡುತ್ತದೆ ಮತ್ತು ಉಚಿತ.</p>"),
        "fk.cta1": "ಈಗಲೇ ನನ್ನ ಉಚಿತ ಜಾತಕ ರಚಿಸಿ",
        "fk.need": ("<p>ನಿಮಗೆ ನಿಮ್ಮ ಜನ್ಮ <strong>ದಿನಾಂಕ</strong>, <strong>ಸಮಯ</strong> ಮತ್ತು <strong>ಸ್ಥಳ</strong> ಬೇಕು.\n"
                    "ಸೈನ್ ಇನ್ ಬೇಕಿಲ್ಲ, ಕಾರ್ಡ್ ಬೇಕಿಲ್ಲ.</p>"),
        "fk.includes": ("<h2>ನಿಮ್ಮ ಉಚಿತ ಜಾತಕದಲ್ಲಿ ಏನೆಲ್ಲಾ ಇದೆ</h2>\n"
                        "<ul>\n"
                        "<li><strong>ಲಗ್ನ ಕುಂಡಲಿ (D1)</strong> ಉತ್ತರ ಭಾರತೀಯ ಅಥವಾ ದಕ್ಷಿಣ ಭಾರತೀಯ ಶೈಲಿಯಲ್ಲಿ — ಒಂದು ಟ್ಯಾಪ್‌ನಲ್ಲಿ ಬದಲಿಸಿ.</li>\n"
                        "<li><strong>ಗ್ರಹ ಸ್ಥಿತಿ</strong>: ಎಲ್ಲಾ ಒಂಬತ್ತು ಗ್ರಹಗಳು ಮತ್ತು ಲಗ್ನದ ರಾಶಿ, ಅಂಶ, ಭಾವ, ಬಲ ಮತ್ತು\n"
                        "ವಕ್ರ ಸ್ಥಿತಿ, ಜೊತೆಗೆ ನಿಮ್ಮ ಚಂದ್ರನ ನಕ್ಷತ್ರ ಮತ್ತು ಪಾದ.</li>\n"
                        "<li><strong>ಹನ್ನೆರಡು ಭಾವಗಳು</strong> ಮತ್ತು ಪ್ರತಿ ಭಾವದಲ್ಲಿರುವ ಗ್ರಹಗಳು.</li>\n"
                        "<li><strong>ವಿಂಶೋತ್ತರಿ ದಶೆ</strong>: ನಿಮ್ಮ ಪ್ರಸ್ತುತ ಮಹಾದಶೆ ಮತ್ತು ಅಂತರ್ದಶೆ ದಿನಾಂಕಗಳೊಂದಿಗೆ,\n"
                        "ಕಾಲರೇಖೆಯ ಮೇಲೆ.</li>\n"
                        "<li><strong>ವರ್ಗ ಕುಂಡಲಿಗಳು</strong>: {vargas}.</li>\n"
                        "<li><strong>ಅಷ್ಟಕವರ್ಗ</strong>: ಪ್ರತಿ ಭಾವದ ಸರ್ವಾಷ್ಟಕವರ್ಗ ಮತ್ತು ಭಿನ್ನಾಷ್ಟಕವರ್ಗ ಬಿಂದುಗಳು.</li>\n"
                        "<li><strong>ಜೈಮಿನಿ</strong> ಚರ ಕಾರಕಗಳು (ಆತ್ಮಕಾರಕದಿಂದ ದಾರಕಾರಕದವರೆಗೆ) ಮತ್ತು ಆರೂಢ ಪದಗಳು, ಹಾಗೂ\n"
                        "ಲಗ್ನ, ಚಂದ್ರ ಮತ್ತು ಸೂರ್ಯರಿಂದ ಒಟ್ಟಿಗೆ ನೋಡುವ <strong>ಸುದರ್ಶನ ಚಕ್ರ</strong>.</li>\n"
                        "<li><strong>ದೋಷ ಪರಿಶೀಲನೆ</strong>: ಕುಜ ದೋಷ (ಮಾಂಗಲಿಕ), ಸಾಡೇಸಾತಿ ಮತ್ತು ಕಾಳಸರ್ಪ ದೋಷ.</li>\n"
                        "<li>ನಿಮ್ಮ ಜಾತಕ ಮತ್ತು ಪ್ರಸ್ತುತ ದಶೆಗೆ ತಕ್ಕ <strong>ರತ್ನ ಮತ್ತು ಪರಿಹಾರ</strong> ಸಲಹೆಗಳು.</li>\n"
                        "<li>ನಿಮ್ಮ ಜಾತಕದ ಡ್ಯಾಶ್‌ಬೋರ್ಡ್‌ನಲ್ಲಿ <strong>ದೈನಂದಿನ ಭವಿಷ್ಯ</strong> ಮತ್ತು ಇಂದಿನ ಪಂಚಾಂಗ.</li>\n"
                        "</ul>\n"
                        "<p>ಎಲ್ಲವನ್ನೂ <strong>ನಿರಯನ ರಾಶಿಚಕ್ರ ಮತ್ತು ಲಾಹಿರಿ ಅಯನಾಂಶ</strong>, ಪೂರ್ಣ-ರಾಶಿ ಭಾವ ಪದ್ಧತಿ\n"
                        "ಮತ್ತು ಸ್ವಿಸ್ ಎಫೆಮೆರಿಸ್‌ನಿಂದ ಲೆಕ್ಕಿಸಲಾಗುತ್ತದೆ. ಉಚಿತ ಖಾತೆಯೊಂದಿಗೆ ನೀವು ಜಾತಕಗಳನ್ನು ಉಳಿಸಬಹುದು,\n"
                        "ಜಾತಕದ PDF ಅನ್ನು ಕನ್ನಡ, ಇಂಗ್ಲಿಷ್ ಅಥವಾ ಹಿಂದಿಯಲ್ಲಿ ಡೌನ್‌ಲೋಡ್ ಮಾಡಬಹುದು, ಮತ್ತು AI ಜ್ಯೋತಿಷಿಗೆ\n"
                        "ನಿಮ್ಮ ಮೊದಲ ಪ್ರಶ್ನೆಗಳನ್ನು ಉಚಿತವಾಗಿ ಕೇಳಬಹುದು.</p>"),
        "fk.read": ("<h2>ನಿಮ್ಮ ಜಾತಕವನ್ನು ಹೇಗೆ ಓದುವುದು</h2>\n"
                    "<h3>1. ಲಗ್ನದಿಂದ ಆರಂಭಿಸಿ</h3>\n"
                    "<p>ಮೊದಲ ಭಾವ ಜನನದ ಸಮಯದಲ್ಲಿ ಉದಯಿಸುತ್ತಿದ್ದ ರಾಶಿ. ಉತ್ತರ ಭಾರತೀಯ ಜಾತಕದಲ್ಲಿ ಇದು ಮೇಲಿನ ಮಧ್ಯದ\n"
                    "ವಜ್ರಾಕಾರದ ಮನೆ, ಮತ್ತು ಪ್ರತಿ ಮನೆಯಲ್ಲಿ ಬರೆದ ಸಂಖ್ಯೆ <em>ರಾಶಿ</em>ಯದು (1 = ಮೇಷ … 12 = ಮೀನ),\n"
                    "ಭಾವದ್ದಲ್ಲ. ದಕ್ಷಿಣ ಭಾರತೀಯ ಜಾತಕದಲ್ಲಿ ರಾಶಿಗಳು ಸ್ಥಿರ ಮನೆಗಳಲ್ಲಿರುತ್ತವೆ ಮತ್ತು ಲಗ್ನವನ್ನು ಗುರುತಿಸಲಾಗುತ್ತದೆ.\n"
                    "ಲಗ್ನ ಮತ್ತು ಲಗ್ನಾಧಿಪತಿ ದೇಹ, ಸ್ವಭಾವ ಮತ್ತು ಜೀವನದ ಒಟ್ಟಾರೆ ದಿಕ್ಕನ್ನು ಸೂಚಿಸುತ್ತಾರೆ.</p>\n"
                    "<h3>2. ನಿಮ್ಮ ಚಂದ್ರ ರಾಶಿ ಮತ್ತು ನಕ್ಷತ್ರವನ್ನು ಗಮನಿಸಿ</h3>\n"
                    "<p>ಭಾರತೀಯ ಪದ್ಧತಿಯಲ್ಲಿ ನಿಮ್ಮ <strong>ರಾಶಿ</strong> ಎಂದರೆ ಚಂದ್ರನ ರಾಶಿ, ಸೂರ್ಯನದಲ್ಲ. ರಾಶಿ ಭವಿಷ್ಯ,\n"
                    "ಸಾಡೇಸಾತಿ ಮತ್ತು ಜಾತಕ ಹೊಂದಾಣಿಕೆಗೆ ಇದೇ ರಾಶಿಯನ್ನು ಬಳಸಲಾಗುತ್ತದೆ, ಮತ್ತು ಚಂದ್ರನ ನಕ್ಷತ್ರ ನಿಮ್ಮ\n"
                    "ವಿಂಶೋತ್ತರಿ ದಶೆ ಎಲ್ಲಿಂದ ಆರಂಭವಾಗುತ್ತದೆ ಎಂಬುದನ್ನು ನಿರ್ಧರಿಸುತ್ತದೆ.</p>\n"
                    "<h3>3. ಭಾವಗಳ ಪ್ರಕಾರ ಗ್ರಹಗಳನ್ನು ಓದಿ</h3>\n"
                    "<p>ಪ್ರತಿ ಭಾವ ಜೀವನದ ಒಂದು ಕ್ಷೇತ್ರ: 1ನೇ ಸ್ವಯಂ, 2ನೇ ಧನ ಮತ್ತು ಕುಟುಂಬ, 3ನೇ ಧೈರ್ಯ ಮತ್ತು ಸಹೋದರರು,\n"
                    "4ನೇ ಮನೆ ಮತ್ತು ತಾಯಿ, 5ನೇ ಮಕ್ಕಳು ಮತ್ತು ಬುದ್ಧಿ, 6ನೇ ಆರೋಗ್ಯ ಮತ್ತು ಶತ್ರುಗಳು, 7ನೇ ವಿವಾಹ ಮತ್ತು\n"
                    "ಪಾಲುದಾರಿಕೆ, 8ನೇ ಆಯುಷ್ಯ ಮತ್ತು ಹಠಾತ್ ಬದಲಾವಣೆ, 9ನೇ ಭಾಗ್ಯ ಮತ್ತು ಧರ್ಮ, 10ನೇ ವೃತ್ತಿ,\n"
                    "11ನೇ ಲಾಭ, 12ನೇ ವ್ಯಯ ಮತ್ತು ಮೋಕ್ಷ. ಗ್ರಹವು ತಾನು ಇರುವ ಭಾವ ಮತ್ತು ತಾನು ಅಧಿಪತಿಯಾಗಿರುವ ಭಾವಗಳ\n"
                    "ಮೇಲೆ ಪ್ರಭಾವ ಬೀರುತ್ತದೆ; ಅದರ ಸ್ಥಿತಿ (ಉಚ್ಚ, ಸ್ವಕ್ಷೇತ್ರ, ನೀಚ) ಅದು ಎಷ್ಟು ಫಲ ನೀಡಬಲ್ಲದು ಎಂದು ತಿಳಿಸುತ್ತದೆ.</p>\n"
                    "<h3>4. ನಡೆಯುತ್ತಿರುವ ದಶೆಯನ್ನು ನೋಡಿ</h3>\n"
                    "<p>ದಶೆ <em>ಯಾವಾಗ</em> ಎಂದು ಹೇಳುತ್ತದೆ. ಮಹಾದಶಾಧಿಪತಿ, ಮತ್ತು ಅದರೊಳಗಿನ ಅಂತರ್ದಶಾಧಿಪತಿ — ಈ ಅವಧಿಯಲ್ಲಿ\n"
                    "ಇವರ ಭಾವಗಳು ಸಕ್ರಿಯವಾಗುತ್ತವೆ — ಆದ್ದರಿಂದಲೇ ಹೋಲುವ ಜಾತಕಗಳಿರುವ ಇಬ್ಬರಿಗೆ ಬಹಳ ಭಿನ್ನವಾದ\n"
                    "ವರ್ಷಗಳು ಬರಬಹುದು.</p>\n"
                    "<h3>5. ದೋಷಗಳನ್ನು ಸಂದರ್ಭದಲ್ಲಿ ನೋಡಿ</h3>\n"
                    "<p>ದೋಷ ಓದಬೇಕಾದ ಒಂದು ಮಾದರಿ, ತೀರ್ಪಲ್ಲ. ಕುಜ ದೋಷಕ್ಕೆ ಶಾಸ್ತ್ರೀಯ ಪರಿಹಾರಗಳಿವೆ;\n"
                    "ಸಾಡೇಸಾತಿ ಏಳೂವರೆ ವರ್ಷಗಳ ಗೋಚಾರ, ಪ್ರತಿಯೊಬ್ಬರ ಜೀವನದಲ್ಲಿ ಎರಡು ಅಥವಾ ಮೂರು ಬಾರಿ ಬರುತ್ತದೆ. ದೋಷ\n"
                    "ವರದಿ ತಾನು ಕಂಡ ಪರಿಹಾರಗಳನ್ನೂ ಹೆಸರಿಸುತ್ತದೆ.</p>"),
        "fk.cta2": "ನನ್ನ ಜನ್ಮ ಜಾತಕ ರಚಿಸಿ — ಉಚಿತ",
        "fk.faq_h2": "<h2>ಪದೇ ಪದೇ ಕೇಳುವ ಪ್ರಶ್ನೆಗಳು</h2>",
        "varga.D1": "ರಾಶಿ", "varga.D3": "ದ್ರೇಕ್ಕಾಣ", "varga.D7": "ಸಪ್ತಾಂಶ",
        "varga.D9": "ನವಾಂಶ", "varga.D10": "ದಶಾಂಶ", "varga.D12": "ದ್ವಾದಶಾಂಶ",
    },

    # Tamil (DIVASTRO-123). Paksha is வளர்பிறை / தேய்பிறை (names_ta), which
    # already means "waxing / waning fortnight": paksha.full is the bare word.
    "ta": {
        "tool.panchang": "பஞ்சாங்கம்",
        "tool.rahu-kaal": "ராகு காலம்",
        "tool.choghadiya": "சௌகடியா",
        "when": "{vara}, {date} · {place} · IST",
        "limb.until": "{name} {time} வரை",
        "limb.then": "பிறகு {name}",
        "limb.pada": "பாதம்",
        "paksha.full": "{paksha}",
        "cities.heading": "மற்ற நகரங்களில் {tool}",
        "links.heading": "மேலும் இலவசக் கருவிகள்",
        "links.tool_in_city": "{city} {tool}",
        "links.milan": "ஜாதகப் பொருத்தம் (36 குணம்)",
        "links.kundali": "இலவச ஜாதகம்",
        "links.muhurat": "முகூர்த்தம் தேடல்",
        "links.rashifal": "இன்றைய ராசி பலன்",
        "links.vrat": "{city} — இன்றைய விரதங்கள், பண்டிகைகள்",
        "nf.title": "நகரம் கிடைக்கவில்லை — {brand}",
        "nf.desc": "{tool}: இந்த நகரம் எங்கள் பட்டியலில் இல்லை.",
        "nf.body": ("<h1>{tool}: நகரம் கிடைக்கவில்லை</h1>"
                    "<p>“{slug}” என்பதற்கு இன்னும் எங்களிடம் பக்கம் இல்லை. கீழே உங்கள் நகரத்தைத் "
                    'தேர்ந்தெடுங்கள், அல்லது <a href="{app}">{tool} கருவியைத் திறந்து</a> உலகின் '
                    "எந்த இடத்தையும் பயன்படுத்துங்கள்.</p>"),

        "p.title": "இன்றைய பஞ்சாங்கம் {city}, {date} — ராகு காலம் | {brand}",
        "p.desc": ("{city} இன்றைய பஞ்சாங்கம் ({vara}, {date}): {paksha_full} {tithi} திதி, "
                   "{nakshatra} நட்சத்திரம், சூரிய உதயம் {sunrise}, ராகு காலம் {rahu}. "
                   "ஸ்விஸ் எஃபெமெரிஸ் மூலம் துல்லியமான கணிப்பு."),
        "p.h1": "<h1>{city} — இன்றைய பஞ்சாங்கம்</h1>",
        "p.sub": '<p class="hi">இன்றைய திதி, நட்சத்திரம், ராகு காலம், எமகண்டம் — {city}</p>',
        "p.box": ("<div class=\"box\"><p>இன்று {city}-இல் <strong>{paksha_full} {tithi}</strong> திதி;\n"
                  "சந்திரன் <strong>{nakshatra}</strong> நட்சத்திரத்தில் இருக்கிறார். ராகு காலம்\n"
                  "<strong>{rahu}</strong> — இந்த நேரத்தில் புதிய காரியங்களைத் தொடங்க வேண்டாம்.</p></div>"),
        "p.r_vara": "கிழமை",
        "p.r_tithi": "திதி",
        "p.r_paksha": "பட்சம்",
        "p.r_nakshatra": "நட்சத்திரம்",
        "p.r_yoga": "யோகம்",
        "p.r_karana": "கரணம்",
        "p.r_sunrise": "சூரிய உதயம்",
        "p.r_sunset": "சூரிய அஸ்தமனம்",
        "p.r_moonrise": "சந்திர உதயம்",
        "p.r_moonset": "சந்திர அஸ்தமனம்",
        "p.r_moon_sign": "சந்திர ராசி",
        "p.r_rahu": "ராகு காலம்",
        "p.r_yama": "எமகண்டம்",
        "p.r_gulika": "குளிகை",
        "p.r_abhijit": "அபிஜித் முகூர்த்தம்",
        "p.v_vara": "{vara}",
        "p.v_paksha": "{paksha_full}",
        "p.no_moonrise": "இன்று சந்திர உதயம் இல்லை",
        "p.no_moonset": "இன்று சந்திர அஸ்தமனம் இல்லை",
        "p.no_abhijit": "புதன்கிழமை அபிஜித் முகூர்த்தம் எடுத்துக்கொள்ளப்படுவதில்லை",
        "p.note": ("<p>நேரங்கள் {city} ({lat}°N, {lon}°E) இடத்துக்கு, இந்திய நேரத்தில் (IST)\n"
                   "தரப்பட்டுள்ளன. பஞ்சாங்க நாள் சூரிய உதயம் முதல் அடுத்த சூரிய உதயம் வரை; எனவே ஒரு திதி\n"
                   "அல்லது நட்சத்திரம் நள்ளிரவுக்குப் பிறகு முடியலாம். இந்தியப் பஞ்சாங்கங்களில் உள்ளபடி, சூரிய\n"
                   "உதயம் என்பது ஒளிவிலகலுடன் சூரியனின் மேல் விளிம்பு தெரியும் நேரம்; நட்சத்திரமும் யோகமும்\n"
                   "லாஹிரி அயனாம்சப்படி கணிக்கப்படுகின்றன.</p>"),
        "p.cta": "முழு பஞ்சாங்கத்தைத் திறக்கவும் — எந்த நகரமும், எந்தத் தேதியும்",
        "p.limbs": ("<h2>பஞ்சாங்கத்தின் ஐந்து அங்கங்கள்</h2>\n"
                    "<p><strong>திதி</strong> என்பது சந்திர நாள் — சந்திரன் சூரியனை விட ஒவ்வொரு 12° முன்னேறும்போதும்\n"
                    "ஒரு திதி. <strong>நட்சத்திரம்</strong> என்பது 27 நட்சத்திரங்களில் சந்திரன் இருக்கும் நட்சத்திரம்.\n"
                    "<strong>யோகம்</strong> சூரியன், சந்திரன் இருவரின் பாகைகளின் கூட்டுத்தொகையிலிருந்து வருகிறது;\n"
                    "<strong>கரணம்</strong> என்பது அரை திதி. <strong>கிழமை</strong> சூரிய உதயத்திலிருந்து கணக்கிடப்படும்\n"
                    "வார நாள். இந்த ஐந்தும் சேர்ந்ததே பஞ்சாங்கம் (“ஐந்து அங்கங்கள்”) — எந்த நல்ல காரியத்துக்கும்\n"
                    "முன் இதைப் பார்ப்பது வழக்கம்.</p>"),

        "rk.title": "இன்று ராகு காலம் {city}: {rahu} | {brand}",
        "rk.desc": ("இன்று ({vara}, {date}) {city}-இல் ராகு காலம் {rahu}. எமகண்டம் {yama}, "
                    "குளிகை {gulika} — இந்த வாரத்தின் நேரங்களும் ராகு காலத்தின் பொருளும்."),
        "rk.h1": "<h1>இன்று ராகு காலம் — {city}</h1>",
        "rk.sub": '<p class="hi">இன்றைய ராகு காலம், எமகண்டம், குளிகை நேரங்கள் — {city}</p>',
        "rk.r_rahu": "ராகு காலம்",
        "rk.r_yama": "எமகண்டம்",
        "rk.r_gulika": "குளிகை",
        "rk.r_abhijit": "அபிஜித் முகூர்த்தம்",
        "rk.r_sun": "சூரிய உதயம் / அஸ்தமனம்",
        "rk.no_abhijit": "புதன்கிழமை எடுத்துக்கொள்ளப்படுவதில்லை",
        "rk.cta": "எந்த நகரத்துக்கும் எந்தத் தேதிக்கும் ராகு காலம் பாருங்கள்",
        "rk.about": ("<h2>ராகு காலம் என்றால் என்ன?</h2>\n"
                     "<p>ராகு காலம் என்பது ஒவ்வொரு நாளும் சுமார் ஒன்றரை மணி நேரம் நீடிக்கும், மரபுப்படி ராகுவின்\n"
                     "(சந்திரனின் வடக்குக் கணு) ஆதிக்கத்தில் உள்ளதாகக் கருதப்படும் நேரம். சூரிய உதயம் முதல் அஸ்தமனம்\n"
                     "வரையிலான பகல் எட்டு சம பகுதிகளாகப் பிரிக்கப்படுகிறது; அவற்றில் ஒன்று ராகுவுக்கு உரியது. எந்தப்\n"
                     "பகுதி என்பது கிழமையைப் பொறுத்தது: ஞாயிறு 8-ஆவது, திங்கள் 2-ஆவது, செவ்வாய் 7-ஆவது, புதன்\n"
                     "5-ஆவது, வியாழன் 6-ஆவது, வெள்ளி 4-ஆவது, சனி 3-ஆவது.</p>\n"
                     "<p>இது உண்மையான சூரிய உதய, அஸ்தமன நேரங்களைப் பின்பற்றுவதால், ராகு காலம் ஒவ்வொரு நகரத்திலும்\n"
                     "வேறுபடும், ஆண்டு முழுவதும் மாறிக்கொண்டே இருக்கும் — அதனால்தான் “திங்கள் 7:30–9:00” போன்ற\n"
                     "நிலையான அட்டவணை தோராயம் மட்டுமே. வழக்கப்படி ராகு காலத்தில் புதிய முயற்சிகளைத் தொடங்குவது,\n"
                     "ஒப்பந்தங்களில் கையெழுத்திடுவது, பயணம் புறப்படுவது, பெரிய பொருள்கள் வாங்குவது தவிர்க்கப்படுகிறது;\n"
                     "ஏற்கனவே நடந்துகொண்டிருக்கும் வேலையைத் தொடரலாம். எமகண்டமும் குளிகையும் பகலின் மேலும் இரண்டு\n"
                     "எட்டில் ஒரு பகுதிகள்; அவற்றிலும் இதே போன்ற கவனம் கடைப்பிடிக்கப்படுகிறது.</p>"),
        "rk.week_h2": "<h2>இந்த வாரம் {city} ராகு காலம்</h2>",
        "rk.th_day": "நாள்",
        "rk.th_rahu": "ராகு காலம்",
        "rk.th_yama": "எமகண்டம்",
        "rk.th_gulika": "குளிகை",

        "ch.title": "இன்றைய நல்ல நேரம் — சௌகடியா {city}, {date} | {brand}",
        "ch.desc": ("{city} இன்றைய சௌகடியா ({vara}, {date}): பகல், இரவின் 16 முகூர்த்தங்களும் — "
                    "அமிர்தம், சுபம், லாபம், சரம், ரோகம், காலம், உத்வேகம் — சூரிய உதயம் {sunrise} முதல் "
                    "துல்லியமான தொடக்க, முடிவு நேரங்களுடன்."),
        "ch.h1": "<h1>இன்றைய சௌகடியா — {city}</h1>",
        "ch.sub": '<p class="hi">பகல், இரவு சௌகடியா — நல்ல நேரம், கெட்ட நேரம் — {city}</p>',
        "ch.first_good": "{name} — {time} முதல்",
        "ch.none": "இல்லை",
        "ch.box": ("<div class=\"box\"><p>சூரிய உதயம் <strong>{sunrise}</strong>, அஸ்தமனம்\n"
                   "<strong>{sunset}</strong>. பகலின் முதல் நல்ல சௌகடியா:\n"
                   "<strong>{first_good}</strong>.</p></div>"),
        "ch.day_h2": "<h2>பகல் சௌகடியா</h2>",
        "ch.night_h2": "<h2>இரவு சௌகடியா</h2>",
        "ch.th": "<tr><th>நேரம்</th><th>சௌகடியா</th><th>தன்மை</th></tr>",
        "ch.row": ('<tr><td>{when}</td><td class="{cls}"><strong>{name}</strong>'
                   "<small>அதிபதி: {ruler}</small></td>"
                   "<td>{quality}<small>{desc}</small></td></tr>"),
        "ch.cta": "நேரடி சௌகடியா கடிகாரத்தைத் திறக்கவும்",
        "ch.about": ("<h2>சௌகடியா எப்படிக் கணக்கிடப்படுகிறது</h2>\n"
                     "<p>சூரிய உதயம் முதல் அஸ்தமனம் வரையிலான பகலும், அஸ்தமனம் முதல் அடுத்த உதயம் வரையிலான இரவும்\n"
                     "தனித்தனியே எட்டு சம பகுதிகளாகப் பிரிக்கப்படுகின்றன; அவையே சௌகடியா (“நான்கு நாழிகை”).\n"
                     "ஒவ்வொன்றுக்கும் ஒரு கிரகம் அதிபதி; அதன் தன்மைக்கேற்பப் பெயர்: <strong>அமிர்தம்</strong>,\n"
                     "<strong>சுபம்</strong>, <strong>லாபம்</strong> நல்லவை; <strong>சரம்</strong> மத்திமம், பயணத்துக்கு\n"
                     "ஏற்றது; <strong>ரோகம்</strong>, <strong>காலம்</strong>, <strong>உத்வேகம்</strong> ஆகியவற்றில்\n"
                     "புதிய தொடக்கங்கள் தவிர்க்கப்படுகின்றன. வரிசை கிழமையின் அதிபதியிலிருந்து தொடங்குவதால் தினமும்\n"
                     "மாறும் — ஒவ்வொரு பகுதியின் நீளமும் {city}-இன் உண்மையான பகல் நீளத்தைப் பொறுத்தது.\n"
                     "(தமிழ்நாட்டில் பரவலாகப் பார்க்கப்படும் கௌரி நல்ல நேரம் இதைப் போன்ற, ஆனால் தனியான முறை.)</p>"),

        "km.title": "ஜாதகப் பொருத்தம் — அஷ்டகூட குணப் பொருத்தம் ({total} குணம்) | {brand}",
        "km.desc": ("ஜாதகப் பொருத்தம் எப்படிப் பார்க்கப்படுகிறது: அஷ்டகூட முறையின் 8 கூடங்கள், மொத்தம் "
                    "{total} குணங்கள், திருமணத்துக்கு எத்தனை குணம் நல்லது, செவ்வாய் தோஷம் எப்படிச் "
                    "சோதிக்கப்படுகிறது. இலவச ஆன்லைன் ஜாதகப் பொருத்தம்."),
        "km.crumb": "ஜாதகப் பொருத்தம்",
        "km.intro": ("<h1>ஜாதகப் பொருத்தம்: அஷ்டகூட குணப் பொருத்தம் — முழு விளக்கம்</h1>\n"
                     "<p class=\"hi\">திருமணப் பொருத்தம் — அஷ்டகூடம் ({total} குணம்)</p>\n"
                     "<p>ஜாதகப் பொருத்தம் (குண்டலி மிலன்) என்பது திருமணப் பொருத்தம் பார்க்கும் பாரம்பரிய வேத முறை.\n"
                     "வட இந்தியாவில் மிகப் பரவலான முறை <strong>அஷ்டகூட குணப் பொருத்தம்</strong>: மணமகள்,\n"
                     "மணமகன் ஜாதகங்களில் எட்டு அம்சங்கள் (<em>கூடங்கள்</em>) ஒப்பிடப்பட்டு <strong>{total}\n"
                     "புள்ளிகளுக்கு (குணங்கள்)</strong> மதிப்பெண் தரப்படுகிறது. (தமிழ்நாட்டில் வழக்கமான பத்துப்\n"
                     "பொருத்த முறை இதிலிருந்து வேறுபட்டது.) இவை அனைத்தும் <strong>சந்திரனிலிருந்து</strong> —\n"
                     "பிறப்பின்போது அதன் ராசி, நட்சத்திரத்திலிருந்து — பார்க்கப்படுகின்றன; எனவே சரியான பிறந்த\n"
                     "தேதியும் இடமும் தேவை, ஆனால் பிறந்த நேரம் மதிப்பெண்ணை அரிதாகவே மாற்றும்.</p>"),
        "km.cta1": "இப்போதே இரண்டு ஜாதகங்களைப் பொருத்திப் பாருங்கள் — இலவசம்",
        "km.naam": ('<p>பிறந்த நேரம் தெரியாதா? <a href="{href}">பெயர் மூலம் ஜாதகப் பொருத்தம்</a> பாருங்கள் — '
                    "ஒவ்வொருவர் பெயரின் முதல் எழுத்தைக் கொண்டு பார்க்கும் பாரம்பரியப் பொருத்தம்.</p>"),
        "km.kootas_h2": "<h2>8 கூடங்களும் அவற்றின் புள்ளிகளும்</h2>",
        "km.th": "<tr><th>கூடம்</th><th>புள்ளிகள்</th><th>எதைப் பார்க்கிறது</th></tr>",
        "km.row": "<tr><td><strong>{name}</strong></td><td>{pts}</td><td>{text}</td></tr>",
        "km.total": "மொத்தம்",
        "km.score_h2": "<h2>எத்தனை குணம் பொருந்தினால் நல்லது?</h2>",
        "km.score_th": "<tr><th>குணங்கள்</th><th>வழக்கமான பொருள்</th></tr>",
        "km.below": "{n}-க்குக் கீழ்",
        "km.score_p": ("<p>18 என்பது வழக்கமான குறைந்தபட்ச அளவு. மொத்த மதிப்பெண் மட்டுமே முழுக் கதை அல்ல:\n"
                       "அதிக மதிப்பெண் இருந்தாலும் பரிகாரம் இல்லாத நாடி அல்லது பகூட் தோஷம் இருந்தால் கவனத்துடன்\n"
                       "பார்க்கப்படுகிறது; குறைந்த மதிப்பெண் இருந்தாலும் வலுவான கிரக மைத்ரியும் தோஷமின்மையும்\n"
                       "இருந்தால் பெரும்பாலும் ஏற்கத்தக்கதாகக் கருதப்படுகிறது. இந்த வரம்புகள் நீண்ட மரபின் வழக்கம்,\n"
                       "அளவீடு அல்ல — அவை வழிகாட்டுதல்தான், ஒரு உறவைப் பற்றிய இறுதித் தீர்ப்பு அல்ல.</p>"),
        "km.ord1": "{n}",
        "km.ord2": "{n}",
        "km.ordn": "{n}",
        "km.or": " அல்லது ",
        "km.mangal": ("<h2>செவ்வாய் தோஷம் (மாங்கலிக்)</h2>\n"
                      "<p>செவ்வாய் தோஷம் 36 புள்ளிகளிலிருந்து தனியாகப் பார்க்கப்படுகிறது. <strong>லக்னம்</strong>,\n"
                      "<strong>சந்திரன்</strong> அல்லது <strong>சுக்கிரன்</strong> இவற்றிலிருந்து எண்ணும்போது செவ்வாய்\n"
                      "{houses}-ஆம் பாவத்தில் இருந்தால் அது செவ்வாய் தோஷ ஜாதகம். சில ராசி நிலைகளுக்குப் பாரம்பரிய\n"
                      "நூல்கள் விலக்கு அளிக்கின்றன (உதாரணமாக 1-ஆம் பாவத்தில் தன் சொந்த ராசியான மேஷத்தில் செவ்வாய்),\n"
                      "செவ்வாய் மீது குருவின் பார்வை தோஷத்தைக் குறைப்பதாகவும் கருதப்படுகிறது. <strong>இருவருக்குமே</strong>\n"
                      "செவ்வாய் தோஷம் இருந்தால் தோஷம் ஒன்றையொன்று சமன் செய்வதாக மரபு — அதனால்தான் செவ்வாய் தோஷ\n"
                      "ஜாதகத்துக்கு செவ்வாய் தோஷ ஜாதகமே பொருத்தப்படுகிறது. லக்னத்தைப் பொறுத்தது என்பதால் செவ்வாய்\n"
                      "தோஷத்துக்கு நம்பகமான பிறந்த நேரம் தேவை.</p>"),
        "km.how": ("<h2>எங்கள் பொருத்தக் கருவி எப்படி வேலை செய்கிறது</h2>\n"
                   "<p>இருவரின் பிறந்த தேதி, நேரம், இடத்தை உள்ளிடுங்கள். இரண்டு ஜாதகங்களும் ஸ்விஸ் எஃபெமெரிஸ்\n"
                   "கொண்டு நிராயன (லாஹிரி அயனாம்சம்) முறையில் கணிக்கப்படுகின்றன; ஒவ்வொரு கூடத்துக்கும்\n"
                   "பாரம்பரிய அட்டவணைகளின்படி மதிப்பெண் தரப்படுகிறது, ஒவ்வொரு பரிகாரமும் பெயருடன் காட்டப்படுகிறது.\n"
                   "முழு {total} புள்ளி விவரமும் இருவரின் செவ்வாய் தோஷ நிலையும் இலவசமாக, பதிவு செய்யாமலேயே\n"
                   "கிடைக்கும்.</p>"),
        "km.cta2": "ஜாதகப் பொருத்தத்தைத் திறக்கவும்",
        "koota.varna": "வர்ணம்",
        "koota.vashya": "வசியம்",
        "koota.tara": "தாரா (தினம்)",
        "koota.yoni": "யோனி",
        "koota.graha_maitri": "கிரக மைத்ரி",
        "koota.gana": "கணம்",
        "koota.bhakoot": "பகூட் (ராசி)",
        "koota.nadi": "நாடி",
        "koota_about.varna": ("சந்திர ராசியின் வர்ணத்திலிருந்து ஆன்மிக, பணி மனப்பான்மை. மணமகனின் வர்ணம் "
                              "மணமகளின் வர்ணத்தை விடக் குறைவாக இல்லையெனில் முழுப் புள்ளி."),
        "koota_about.vashya": "பரஸ்பர ஈர்ப்பும் செல்வாக்கும் — எந்த ராசி மற்றதை “ஈர்க்கிறது”.",
        "koota_about.tara": ("ஆரோக்கியமும் நலமும், இரண்டு ஜன்ம நட்சத்திரங்களுக்கு இடையிலான எண்ணிக்கையிலிருந்து; "
                             "3, 5, 7-ஆம் தாரைகள் சாதகமற்றவை."),
        "koota_about.yoni": ("உடல், தாம்பத்தியப் பொருத்தம்; ஒவ்வொரு நட்சத்திரத்துக்கும் ஒரு விலங்கு யோனி உண்டு; "
                             "ஒன்றுக்கொன்று பகையான விலங்குகளுக்குப் பூஜ்யம் புள்ளி."),
        "koota_about.graha_maitri": ("இரண்டு சந்திர ராசிகளின் அதிபதிகளுக்கு இடையிலான நட்பு — "
                                     "தம்பதியின் மன ஒத்திசைவு."),
        "koota_about.gana": "குணம்: தேவ (தெய்வீக), மனித அல்லது ராட்சச (உக்கிர) கணம்.",
        "koota_about.bhakoot": ("இரண்டு சந்திர ராசிகளின் பரஸ்பர நிலை. 2/12, 5/9, 6/8 நிலைகள் பகூட் தோஷம்; "
                                "ராசி அதிபதிகள் ஒருவரே அல்லது நண்பர்கள் என்றால் இது நீங்கும்."),
        "koota_about.nadi": ("அதிகப் புள்ளிகள் கொண்ட கூடம், ஆரோக்கியம், சந்ததியுடன் தொடர்புடையது. இருவருக்கும் "
                             "ஒரே நாடி என்றால் நாடி தோஷம்; ஒரே ராசி/வேறு நட்சத்திரம், அல்லது ஒரே நட்சத்திரம்/வேறு "
                             "பாதம் என்றால் பாரம்பரியப் பரிகாரம் உண்டு."),
        "km.band0": "பரிந்துரைக்கப்படவில்லை",
        "km.band1": "ஏற்கத்தக்கது",
        "km.band2": "நல்லது",
        "km.band3": "மிகச் சிறந்தது",

        "fk.title": "இலவச ஜாதகம் ஆன்லைன் — தமிழில் ஜனன ஜாதகம் | {brand}",
        "fk.desc": ("உங்கள் ஜனன ஜாதகத்தை இலவசமாக ஆன்லைனில் கணியுங்கள்: வட அல்லது தென்னிந்திய முறையில் "
                    "ராசி கட்டம், கிரக நிலைகள், சந்திர நட்சத்திரம், விம்சோத்தரி தசை, நவாம்சம் உள்ளிட்ட "
                    "வர்க்கச் சக்கரங்கள், செவ்வாய் தோஷம், ஏழரைச் சனி, கால சர்ப்ப தோஷச் சோதனை — "
                    "உள்நுழைவு தேவையில்லை."),
        "fk.crumb": "இலவச ஜாதகம்",
        "fk.intro": ("<h1>இலவச ஜனன ஜாதகம் ஆன்லைன்</h1>\n"
                     "<p class=\"hi\">தமிழில் இலவச ஜாதகம் — ராசி கட்டம், நவாம்சம், தசா புக்தி</p>\n"
                     "<p><strong>ஜனன ஜாதகம்</strong> (பிறப்பு ஜாதகம்) என்பது நீங்கள் பிறந்த சரியான நேரத்திலும்\n"
                     "இடத்திலும் வானத்தின் வரைபடம்: அப்போது கிழக்கு அடிவானத்தில் பன்னிரண்டு ராசிகளில் எது\n"
                     "உதயமாகிக்கொண்டிருந்தது (உங்கள் <strong>லக்னம்</strong>), சூரியன், சந்திரன், செவ்வாய், புதன், குரு,\n"
                     "சுக்கிரன், சனி, ராகு, கேது ஆகியவை எந்த ராசிகளிலும் 27 நட்சத்திரங்களில் எவற்றிலும் இருந்தன\n"
                     "என்பது. குணம், வாழ்க்கையின் பன்னிரண்டு துறைகள், எல்லாவற்றுக்கும் மேலாக தசைகள் மூலம்\n"
                     "<em>காலம்</em> — இவை அனைத்தையும் வேத ஜோதிடம் இந்த ஒரு ஜாதகத்திலிருந்தே படிக்கிறது. எங்கள்\n"
                     "ஜாதகம் நிமிடம் வரை துல்லியமாகக் கணிக்கப்படுகிறது, இலவசம்.</p>"),
        "fk.cta1": "இப்போதே என் இலவச ஜாதகத்தைக் கணி",
        "fk.need": ("<p>உங்கள் பிறந்த <strong>தேதி</strong>, <strong>நேரம்</strong>, <strong>இடம்</strong> தேவை.\n"
                    "உள்நுழைவு இல்லை, கார்டு இல்லை.</p>"),
        "fk.includes": ("<h2>இலவச ஜாதகத்தில் என்னென்ன கிடைக்கும்</h2>\n"
                        "<ul>\n"
                        "<li><strong>ராசி கட்டம் (D1)</strong> வட இந்திய அல்லது தென்னிந்திய முறையில் — ஒரே தொடுதலில் மாற்றலாம்.</li>\n"
                        "<li><strong>கிரக நிலைகள்</strong>: ஒன்பது கிரகங்கள், லக்னம் ஆகியவற்றின் ராசி, பாகை, பாவம், பலம்\n"
                        "(உச்சம்/ஆட்சி/நீசம்), வக்ர நிலை — உங்கள் சந்திர நட்சத்திரம், பாதத்துடன்.</li>\n"
                        "<li><strong>பன்னிரண்டு பாவங்கள்</strong>, ஒவ்வொன்றிலும் உள்ள கிரகங்களுடன்.</li>\n"
                        "<li><strong>விம்சோத்தரி தசை</strong>: நடப்பு மகா தசை, புக்தி — அவற்றின் தேதிகளுடன்,\n"
                        "காலவரிசைப் படமாக.</li>\n"
                        "<li><strong>வர்க்கச் சக்கரங்கள்</strong>: {vargas}.</li>\n"
                        "<li><strong>அஷ்டகவர்க்கம்</strong>: பாவ வாரியாக சர்வாஷ்டகவர்க்க, பின்னாஷ்டகவர்க்கப் பிந்துக்கள்.</li>\n"
                        "<li><strong>ஜைமினி</strong> சர காரகர்கள் (ஆத்மகாரகன் முதல் தாரகாரகன் வரை), ஆரூட பதங்கள், மேலும்\n"
                        "லக்னம், சந்திரன், சூரியன் மூன்றிலிருந்தும் ஒன்றாகப் பார்க்கும் <strong>சுதர்சன சக்கரம்</strong>.</li>\n"
                        "<li><strong>தோஷச் சோதனை</strong>: செவ்வாய் தோஷம், ஏழரைச் சனி, கால சர்ப்ப தோஷம்.</li>\n"
                        "<li>உங்கள் ஜாதகம், நடப்பு தசைக்கேற்ற <strong>ரத்தினம், பரிகாரம்</strong> பரிந்துரைகள்.</li>\n"
                        "<li>ஜாதக டாஷ்போர்டில் உங்கள் <strong>தினசரி பலன்</strong>, இன்றைய பஞ்சாங்கம்.</li>\n"
                        "</ul>\n"
                        "<p>அனைத்தும் <strong>நிராயன ராசிச் சக்கரம், லாஹிரி அயனாம்சம்</strong>, முழு ராசி பாவ முறையில்\n"
                        "ஸ்விஸ் எஃபெமெரிஸ் கொண்டு கணிக்கப்படுகின்றன. இலவசக் கணக்குடன் ஜாதகங்களைச் சேமிக்கலாம்,\n"
                        "ஜாதகத்தை PDF ஆகப் பதிவிறக்கலாம், AI ஜோதிடரிடம் முதல் கேள்விகளை இலவசமாகக் கேட்கலாம்.</p>"),
        "fk.read": ("<h2>உங்கள் ஜாதகத்தை எப்படிப் படிப்பது</h2>\n"
                    "<h3>1. லக்னத்திலிருந்து தொடங்குங்கள்</h3>\n"
                    "<p>முதல் பாவம் என்பது பிறப்பின்போது உதயமான ராசி. வட இந்திய கட்டத்தில் இது மேல் நடுவில் உள்ள\n"
                    "வைர வடிவக் கட்டம்; ஒவ்வொரு கட்டத்திலும் எழுதப்பட்ட எண் <em>ராசி</em>யைக் குறிக்கிறது (1 = மேஷம் …\n"
                    "12 = மீனம்), பாவத்தை அல்ல. தென்னிந்திய கட்டத்தில் ராசிகள் நிலையான கட்டங்களில் இருக்கும், லக்னம்\n"
                    "குறிக்கப்பட்டிருக்கும். லக்னமும் அதன் அதிபதியும் உடல், குணம், வாழ்க்கையின் ஒட்டுமொத்தத் திசையை\n"
                    "விவரிக்கின்றன.</p>\n"
                    "<h3>2. உங்கள் சந்திர ராசி, நட்சத்திரத்தைக் குறித்துக்கொள்ளுங்கள்</h3>\n"
                    "<p>இந்திய வழக்கில் உங்கள் <strong>ராசி</strong> என்பது சந்திரனின் ராசி, சூரியனுடையது அல்ல. ராசி பலன்,\n"
                    "ஏழரைச் சனி, ஜாதகப் பொருத்தம் ஆகியவற்றுக்கு இதுவே பயன்படுகிறது; சந்திரனின் நட்சத்திரமே உங்கள்\n"
                    "விம்சோத்தரி தசை எங்கிருந்து தொடங்குகிறது என்பதைத் தீர்மானிக்கிறது.</p>\n"
                    "<h3>3. பாவ வாரியாகக் கிரகங்களைப் படியுங்கள்</h3>\n"
                    "<p>ஒவ்வொரு பாவமும் வாழ்க்கையின் ஒரு துறை: 1 தான், 2 செல்வம், குடும்பம், 3 தைரியம், உடன்பிறப்புகள்,\n"
                    "4 வீடு, தாய், 5 குழந்தைகள், அறிவு, 6 ஆரோக்கியம், எதிரிகள், 7 திருமணம், கூட்டாண்மை, 8 ஆயுள்,\n"
                    "திடீர் மாற்றம், 9 பாக்கியம், தர்மம், 10 தொழில், 11 லாபம், 12 செலவு, மோட்சம். ஒரு கிரகம் தான்\n"
                    "அமர்ந்த பாவத்தையும் தான் ஆளும் பாவங்களையும் பாதிக்கிறது; அதன் பலம் (உச்சம், ஆட்சி, நீசம்) அது\n"
                    "எவ்வளவு நன்றாகப் பலன் தரும் என்பதைச் சொல்கிறது.</p>\n"
                    "<h3>4. நடப்பு தசையைப் பாருங்கள்</h3>\n"
                    "<p>தசை <em>எப்போது</em> என்பதைச் சொல்கிறது. மகா தசை அதிபதியும், அதற்குள் புக்தி அதிபதியும் —\n"
                    "இந்தக் காலத்தில் இவர்களின் பாவங்களே செயல்படுகின்றன; அதனால்தான் ஒத்த ஜாதகம் உள்ள இருவருக்கு\n"
                    "மிகவும் வேறுபட்ட ஆண்டுகள் அமையலாம்.</p>\n"
                    "<h3>5. தோஷங்களைச் சூழலுடன் பாருங்கள்</h3>\n"
                    "<p>தோஷம் என்பது படித்துப் புரிந்துகொள்ள வேண்டிய ஒரு அமைப்பு, தீர்ப்பு அல்ல. செவ்வாய் தோஷத்துக்குப்\n"
                    "பாரம்பரியப் பரிகாரங்கள் உண்டு; ஏழரைச் சனி என்பது ஒவ்வொருவரும் வாழ்வில் இரண்டு மூன்று முறை\n"
                    "சந்திக்கும் ஏழரை ஆண்டு சனி கோசாரம். தோஷ அறிக்கை தான் கண்டறிந்த பரிகாரங்களையும் பெயருடன்\n"
                    "காட்டும்.</p>"),
        "fk.cta2": "என் ஜனன ஜாதகத்தைக் கணி — இலவசம்",
        "fk.faq_h2": "<h2>அடிக்கடி கேட்கப்படும் கேள்விகள்</h2>",
        "varga.D1": "ராசி", "varga.D3": "திரேக்காணம்", "varga.D7": "சப்தாம்சம்",
        "varga.D9": "நவாம்சம்", "varga.D10": "தசாம்சம்", "varga.D12": "துவாதசாம்சம்",
    },

    # Malayalam (DIVASTRO-123). Kerala usage: രാശി of the Moon = കൂറ്,
    # antardasha = അപഹാരം, Kundali Milan = ജാതകപ്പൊരുത്തം.
    "ml": {
        "tool.panchang": "പഞ്ചാംഗം",
        "tool.rahu-kaal": "രാഹുകാലം",
        "tool.choghadiya": "ചോഘടിയ",
        "when": "{vara}, {date} · {place} · IST",
        "limb.until": "{name} {time} വരെ",
        "limb.then": "തുടർന്ന് {name}",
        "limb.pada": "പാദം",
        "paksha.full": "{paksha}പക്ഷം",
        "cities.heading": "മറ്റു നഗരങ്ങളിലെ {tool}",
        "links.heading": "കൂടുതൽ സൗജന്യ ടൂളുകൾ",
        "links.tool_in_city": "{city} {tool}",
        "links.milan": "ജാതകപ്പൊരുത്തം (36 ഗുണം)",
        "links.kundali": "സൗജന്യ ജാതകം",
        "links.muhurat": "മുഹൂർത്തം കണ്ടെത്താം",
        "links.rashifal": "ഇന്നത്തെ രാശിഫലം",
        "links.vrat": "{city} — ഇന്നത്തെ വ്രതങ്ങളും ആഘോഷങ്ങളും",
        "nf.title": "നഗരം കണ്ടെത്താനായില്ല — {brand}",
        "nf.desc": "{tool}: ഈ നഗരം ഞങ്ങളുടെ പട്ടികയിലില്ല.",
        "nf.body": ("<h1>{tool}: നഗരം കണ്ടെത്താനായില്ല</h1>"
                    "<p>“{slug}” എന്നതിന് ഇപ്പോൾ ഞങ്ങൾക്ക് പേജില്ല. താഴെനിന്ന് നിങ്ങളുടെ നഗരം "
                    'തിരഞ്ഞെടുക്കുക, അല്ലെങ്കിൽ <a href="{app}">{tool} ടൂൾ തുറന്ന്</a> ലോകത്തിലെ '
                    "ഏത് സ്ഥലവും ഉപയോഗിക്കുക.</p>"),

        "p.title": "ഇന്നത്തെ പഞ്ചാംഗം {city}, {date} — നാൾ, രാഹുകാലം | {brand}",
        "p.desc": ("{city} ഇന്നത്തെ പഞ്ചാംഗം ({vara}, {date}): {paksha_full} {tithi} തിഥി, "
                   "{nakshatra} നക്ഷത്രം, സൂര്യോദയം {sunrise}, രാഹുകാലം {rahu}. "
                   "സ്വിസ് എഫെമെറിസ് ഉപയോഗിച്ചുള്ള കൃത്യമായ ഗണനം."),
        "p.h1": "<h1>{city} — ഇന്നത്തെ പഞ്ചാംഗം</h1>",
        "p.sub": '<p class="hi">ഇന്നത്തെ നാൾ, തിഥി, രാഹുകാലം, യമകണ്ടം — {city}</p>',
        "p.box": ("<div class=\"box\"><p>ഇന്ന് {city}-ൽ <strong>{paksha_full} {tithi}</strong> തിഥി;\n"
                  "ചന്ദ്രൻ <strong>{nakshatra}</strong> നക്ഷത്രത്തിൽ. രാഹുകാലം\n"
                  "<strong>{rahu}</strong> — ഈ സമയത്ത് പുതിയ കാര്യങ്ങൾ തുടങ്ങാതിരിക്കുക.</p></div>"),
        "p.r_vara": "ആഴ്ച",
        "p.r_tithi": "തിഥി",
        "p.r_paksha": "പക്ഷം",
        "p.r_nakshatra": "നക്ഷത്രം",
        "p.r_yoga": "യോഗം",
        "p.r_karana": "കരണം",
        "p.r_sunrise": "സൂര്യോദയം",
        "p.r_sunset": "സൂര്യാസ്തമയം",
        "p.r_moonrise": "ചന്ദ്രോദയം",
        "p.r_moonset": "ചന്ദ്രാസ്തമയം",
        "p.r_moon_sign": "കൂറ് (ചന്ദ്രരാശി)",
        "p.r_rahu": "രാഹുകാലം",
        "p.r_yama": "യമകണ്ടം",
        "p.r_gulika": "ഗുളികകാലം",
        "p.r_abhijit": "അഭിജിത് മുഹൂർത്തം",
        "p.v_vara": "{vara}",
        "p.v_paksha": "{paksha_full}",
        "p.no_moonrise": "ഈ ദിവസം ചന്ദ്രോദയമില്ല",
        "p.no_moonset": "ഈ ദിവസം ചന്ദ്രാസ്തമയമില്ല",
        "p.no_abhijit": "ബുധനാഴ്ച അഭിജിത് മുഹൂർത്തം എടുക്കാറില്ല",
        "p.note": ("<p>സമയങ്ങൾ {city} ({lat}°N, {lon}°E) സ്ഥലത്തിന്, ഇന്ത്യൻ സമയത്തിൽ (IST) ആണ്.\n"
                   "പഞ്ചാംഗദിനം സൂര്യോദയം മുതൽ അടുത്ത സൂര്യോദയം വരെയാണ്; അതിനാൽ ഒരു തിഥിയോ നക്ഷത്രമോ\n"
                   "അർധരാത്രിക്കു ശേഷം അവസാനിക്കാം. ഇന്ത്യൻ പഞ്ചാംഗങ്ങളിലെന്നപോലെ, അന്തരീക്ഷ അപവർത്തനം ഉൾപ്പെടെ\n"
                   "സൂര്യന്റെ മുകൾവിളുമ്പ് ദൃശ്യമാകുന്ന സമയമാണ് സൂര്യോദയം; നക്ഷത്രവും യോഗവും ലാഹിരി\n"
                   "അയനാംശപ്രകാരമാണ്.</p>"),
        "p.cta": "മുഴുവൻ പഞ്ചാംഗം തുറക്കുക — ഏത് നഗരവും, ഏത് തീയതിയും",
        "p.limbs": ("<h2>പഞ്ചാംഗത്തിന്റെ അഞ്ച് അംഗങ്ങൾ</h2>\n"
                    "<p><strong>തിഥി</strong> ചാന്ദ്രദിനമാണ് — ചന്ദ്രൻ സൂര്യനെക്കാൾ ഓരോ 12° മുന്നേറുമ്പോഴും ഒരു\n"
                    "തിഥി. <strong>നക്ഷത്രം</strong> 27 നക്ഷത്രങ്ങളിൽ ചന്ദ്രൻ നിൽക്കുന്നതാണ്. <strong>യോഗം</strong>\n"
                    "സൂര്യന്റെയും ചന്ദ്രന്റെയും സ്ഫുടങ്ങളുടെ തുകയിൽ നിന്നു വരുന്നു; <strong>കരണം</strong> അര\n"
                    "തിഥിയാണ്. <strong>ആഴ്ച</strong> സൂര്യോദയം മുതൽ കണക്കാക്കുന്ന ദിവസമാണ്. ഇവ അഞ്ചും\n"
                    "ചേർന്നതാണ് പഞ്ചാംഗം (“അഞ്ച് അംഗങ്ങൾ”) — ഏത് ശുഭകാര്യത്തിനു മുമ്പും നോക്കുന്നത്.</p>"),

        "rk.title": "രാഹുകാലം ഇന്ന് {city}: {rahu} | {brand}",
        "rk.desc": ("ഇന്ന് ({vara}, {date}) {city}-ൽ രാഹുകാലം {rahu}. യമകണ്ടം {yama}, "
                    "ഗുളികകാലം {gulika} — ഈ ആഴ്ചയിലെ സമയങ്ങളും രാഹുകാലത്തിന്റെ അർഥവും."),
        "rk.h1": "<h1>രാഹുകാലം ഇന്ന് — {city}</h1>",
        "rk.sub": '<p class="hi">ഇന്നത്തെ രാഹുകാലം, യമകണ്ടം, ഗുളികകാലം — {city}</p>',
        "rk.r_rahu": "രാഹുകാലം",
        "rk.r_yama": "യമകണ്ടം",
        "rk.r_gulika": "ഗുളികകാലം",
        "rk.r_abhijit": "അഭിജിത് മുഹൂർത്തം",
        "rk.r_sun": "സൂര്യോദയം / സൂര്യാസ്തമയം",
        "rk.no_abhijit": "ബുധനാഴ്ച എടുക്കാറില്ല",
        "rk.cta": "ഏത് നഗരത്തിലെയും ഏത് തീയതിയിലെയും രാഹുകാലം നോക്കുക",
        "rk.about": ("<h2>രാഹുകാലം എന്നാൽ എന്ത്?</h2>\n"
                     "<p>ഓരോ ദിവസവും ഏകദേശം ഒന്നര മണിക്കൂർ നീളുന്ന, പാരമ്പര്യപ്രകാരം രാഹുവിന്റെ (ചന്ദ്രന്റെ\n"
                     "ഉത്തരപാതം) ആധിപത്യത്തിലുള്ളതായി കരുതുന്ന സമയമാണ് രാഹുകാലം. സൂര്യോദയം മുതൽ\n"
                     "സൂര്യാസ്തമയം വരെയുള്ള പകലിനെ എട്ട് തുല്യഭാഗങ്ങളായി തിരിക്കുന്നു; അതിലൊന്ന് രാഹുവിന്റേതാണ്.\n"
                     "ഏത് ഭാഗം എന്നത് ആഴ്ചയെ ആശ്രയിച്ചിരിക്കുന്നു: ഞായർ 8-ാമത്തേത്, തിങ്കൾ 2-ാമത്തേത്, ചൊവ്വ\n"
                     "7-ാമത്തേത്, ബുധൻ 5-ാമത്തേത്, വ്യാഴം 6-ാമത്തേത്, വെള്ളി 4-ാമത്തേത്, ശനി 3-ാമത്തേത്.</p>\n"
                     "<p>യഥാർഥ സൂര്യോദയ-അസ്തമയങ്ങളെ പിന്തുടരുന്നതിനാൽ രാഹുകാലം ഓരോ നഗരത്തിലും വ്യത്യസ്തമാണ്,\n"
                     "വർഷം മുഴുവൻ മാറിക്കൊണ്ടിരിക്കും — അതുകൊണ്ടാണ് “തിങ്കൾ 7:30–9:00” പോലുള്ള നിശ്ചിത പട്ടിക\n"
                     "ഏകദേശക്കണക്ക് മാത്രമാകുന്നത്. ആചാരപ്രകാരം രാഹുകാലത്ത് പുതിയ സംരംഭങ്ങൾ തുടങ്ങുക, കരാറുകളിൽ\n"
                     "ഒപ്പിടുക, യാത്ര പുറപ്പെടുക, വലിയ സാധനങ്ങൾ വാങ്ങുക എന്നിവ ഒഴിവാക്കുന്നു; നേരത്തേ തുടങ്ങിയ\n"
                     "ജോലി തുടരാം. യമകണ്ടവും ഗുളികകാലവും പകലിന്റെ മറ്റു രണ്ട് എട്ടിലൊന്നുകളാണ്; അവയിലും സമാനമായ\n"
                     "ശ്രദ്ധ പാലിക്കുന്നു.</p>"),
        "rk.week_h2": "<h2>ഈ ആഴ്ച {city}-ലെ രാഹുകാലം</h2>",
        "rk.th_day": "ദിവസം",
        "rk.th_rahu": "രാഹുകാലം",
        "rk.th_yama": "യമകണ്ടം",
        "rk.th_gulika": "ഗുളികകാലം",

        "ch.title": "ഇന്നത്തെ ശുഭസമയം — ചോഘടിയ {city}, {date} | {brand}",
        "ch.desc": ("{city} ഇന്നത്തെ ചോഘടിയ ({vara}, {date}): പകലിലെയും രാത്രിയിലെയും 16 മുഹൂർത്തങ്ങളും — "
                    "അമൃതം, ശുഭം, ലാഭം, ചരം, രോഗം, കാലം, ഉദ്വേഗം — സൂര്യോദയം {sunrise} മുതൽ കൃത്യമായ "
                    "ആരംഭ-അവസാന സമയങ്ങളോടെ."),
        "ch.h1": "<h1>ഇന്നത്തെ ചോഘടിയ — {city}</h1>",
        "ch.sub": '<p class="hi">പകലിലെയും രാത്രിയിലെയും ശുഭ-അശുഭ സമയങ്ങൾ — {city}</p>',
        "ch.first_good": "{name} — {time} മുതൽ",
        "ch.none": "ഇല്ല",
        "ch.box": ("<div class=\"box\"><p>സൂര്യോദയം <strong>{sunrise}</strong>, സൂര്യാസ്തമയം\n"
                   "<strong>{sunset}</strong>. പകലിലെ ആദ്യ ശുഭ ചോഘടിയ:\n"
                   "<strong>{first_good}</strong>.</p></div>"),
        "ch.day_h2": "<h2>പകൽ ചോഘടിയ</h2>",
        "ch.night_h2": "<h2>രാത്രി ചോഘടിയ</h2>",
        "ch.th": "<tr><th>സമയം</th><th>ചോഘടിയ</th><th>സ്വഭാവം</th></tr>",
        "ch.row": ('<tr><td>{when}</td><td class="{cls}"><strong>{name}</strong>'
                   "<small>അധിപൻ: {ruler}</small></td>"
                   "<td>{quality}<small>{desc}</small></td></tr>"),
        "ch.cta": "തത്സമയ ചോഘടിയ ഘടികാരം തുറക്കുക",
        "ch.about": ("<h2>ചോഘടിയ കണക്കാക്കുന്നത് എങ്ങനെ</h2>\n"
                     "<p>സൂര്യോദയം മുതൽ അസ്തമയം വരെയുള്ള പകലും, അസ്തമയം മുതൽ അടുത്ത ഉദയം വരെയുള്ള രാത്രിയും\n"
                     "എട്ട് തുല്യഭാഗങ്ങളായി തിരിക്കുന്നു; അവയാണ് ചോഘടിയ (“നാല് നാഴിക”). ഓരോന്നിനും ഒരു ഗ്രഹം\n"
                     "അധിപനാണ്; സ്വഭാവമനുസരിച്ചാണ് പേര്: <strong>അമൃതം</strong>, <strong>ശുഭം</strong>,\n"
                     "<strong>ലാഭം</strong> എന്നിവ ശുഭം; <strong>ചരം</strong> മധ്യമം, യാത്രയ്ക്ക് നല്ലത്;\n"
                     "<strong>രോഗം</strong>, <strong>കാലം</strong>, <strong>ഉദ്വേഗം</strong> എന്നിവയിൽ പുതിയ\n"
                     "തുടക്കങ്ങൾ ഒഴിവാക്കുന്നു. ക്രമം ആഴ്ചയുടെ അധിപനിൽ നിന്നു തുടങ്ങുന്നതിനാൽ ദിവസവും മാറും —\n"
                     "ഓരോ ഭാഗത്തിന്റെയും നീളം {city}-ലെ യഥാർഥ പകൽദൈർഘ്യത്തെ ആശ്രയിച്ചിരിക്കുന്നു.</p>"),

        "km.title": "ജാതകപ്പൊരുത്തം — അഷ്ടകൂട ഗുണപ്പൊരുത്തം ({total} ഗുണം) | {brand}",
        "km.desc": ("ജാതകപ്പൊരുത്തം എങ്ങനെ നോക്കുന്നു: അഷ്ടകൂട രീതിയിലെ 8 കൂടങ്ങൾ, ആകെ {total} ഗുണം, "
                    "വിവാഹത്തിന് എത്ര ഗുണം നല്ലത്, ചൊവ്വാദോഷം എങ്ങനെ പരിശോധിക്കുന്നു. സൗജന്യ ഓൺലൈൻ "
                    "ജാതകപ്പൊരുത്തം."),
        "km.crumb": "ജാതകപ്പൊരുത്തം",
        "km.intro": ("<h1>ജാതകപ്പൊരുത്തം: അഷ്ടകൂട ഗുണപ്പൊരുത്തം വിശദമായി</h1>\n"
                     "<p class=\"hi\">വിവാഹപ്പൊരുത്തം — അഷ്ടകൂടം ({total} ഗുണം)</p>\n"
                     "<p>ജാതകപ്പൊരുത്തം (കുണ്ഡലി മിലൻ) വിവാഹപ്പൊരുത്തം നോക്കാനുള്ള പരമ്പരാഗത വൈദിക രീതിയാണ്.\n"
                     "ഉത്തരേന്ത്യയിൽ ഏറ്റവും പ്രചാരമുള്ളത് <strong>അഷ്ടകൂട ഗുണപ്പൊരുത്തം</strong> ആണ്: വധുവിന്റെയും\n"
                     "വരന്റെയും ജാതകങ്ങളിൽ എട്ട് ഘടകങ്ങൾ (<em>കൂടങ്ങൾ</em>) താരതമ്യം ചെയ്ത് <strong>{total}\n"
                     "പോയിന്റിൽ (ഗുണം)</strong> മാർക്ക് നൽകുന്നു. (കേരളത്തിൽ പതിവുള്ള പത്തു പൊരുത്തം രീതി ഇതിൽ നിന്ന്\n"
                     "വ്യത്യസ്തമാണ്.) ഇവയെല്ലാം <strong>ചന്ദ്രനിൽ</strong> നിന്നാണ് — ജനനസമയത്തെ കൂറും നക്ഷത്രവും —\n"
                     "നോക്കുന്നത്; അതിനാൽ കൃത്യമായ ജനനത്തീയതിയും സ്ഥലവും വേണം, എന്നാൽ ജനനസമയം മാർക്കിനെ\n"
                     "കാര്യമായി ബാധിക്കില്ല.</p>"),
        "km.cta1": "രണ്ട് ജാതകങ്ങൾ ഇപ്പോൾത്തന്നെ ചേർത്തുനോക്കൂ — സൗജന്യം",
        "km.naam": ('<p>ജനനസമയം അറിയില്ലേ? <a href="{href}">പേരുകൊണ്ടുള്ള ജാതകപ്പൊരുത്തം</a> നോക്കൂ — '
                    "ഓരോരുത്തരുടെയും പേരിന്റെ ആദ്യാക്ഷരം കൊണ്ടുള്ള പരമ്പരാഗത പൊരുത്തം.</p>"),
        "km.kootas_h2": "<h2>8 കൂടങ്ങളും അവയുടെ പോയിന്റുകളും</h2>",
        "km.th": "<tr><th>കൂടം</th><th>പോയിന്റ്</th><th>എന്ത് നോക്കുന്നു</th></tr>",
        "km.row": "<tr><td><strong>{name}</strong></td><td>{pts}</td><td>{text}</td></tr>",
        "km.total": "ആകെ",
        "km.score_h2": "<h2>എത്ര ഗുണം പൊരുത്തപ്പെട്ടാൽ നല്ലത്?</h2>",
        "km.score_th": "<tr><th>ഗുണം</th><th>പരമ്പരാഗത വ്യാഖ്യാനം</th></tr>",
        "km.below": "{n}-ൽ താഴെ",
        "km.score_p": ("<p>18 ആണ് പരമ്പരാഗതമായ കുറഞ്ഞ പരിധി. ആകെ മാർക്ക് മാത്രം മുഴുവൻ കഥയല്ല: ഉയർന്ന\n"
                       "മാർക്കിനൊപ്പം പരിഹാരമില്ലാത്ത നാഡീദോഷമോ ഭകൂടദോഷമോ ഉണ്ടെങ്കിൽ ശ്രദ്ധയോടെ കാണുന്നു;\n"
                       "കുറഞ്ഞ മാർക്കാണെങ്കിലും ശക്തമായ ഗ്രഹമൈത്രിയും ദോഷങ്ങളില്ലായ്മയും ഉണ്ടെങ്കിൽ പലപ്പോഴും\n"
                       "സ്വീകാര്യമായി കരുതുന്നു. ഈ പരിധികൾ ദീർഘകാല പാരമ്പര്യമാണ്, അളവല്ല — അവ മാർഗനിർദേശമാണ്,\n"
                       "ഒരു ബന്ധത്തെക്കുറിച്ചുള്ള അന്തിമവിധിയല്ല.</p>"),
        "km.ord1": "{n}",
        "km.ord2": "{n}",
        "km.ordn": "{n}",
        "km.or": " അല്ലെങ്കിൽ ",
        "km.mangal": ("<h2>ചൊവ്വാദോഷം (മാംഗലിക്)</h2>\n"
                      "<p>ചൊവ്വാദോഷം 36 ഗുണങ്ങളിൽ നിന്നു വേറിട്ടാണ് നോക്കുന്നത്. <strong>ലഗ്നം</strong>,\n"
                      "<strong>ചന്ദ്രൻ</strong> അല്ലെങ്കിൽ <strong>ശുക്രൻ</strong> എന്നിവയിൽ നിന്ന് എണ്ണുമ്പോൾ ചൊവ്വ\n"
                      "{houses}-ാം ഭാവത്തിൽ നിൽക്കുന്നെങ്കിൽ ജാതകം ചൊവ്വാദോഷമുള്ളതാണ്. ചില രാശിസ്ഥിതികൾക്ക്\n"
                      "ശാസ്ത്രഗ്രന്ഥങ്ങൾ ഇളവ് നൽകുന്നു (ഉദാഹരണത്തിന് 1-ാം ഭാവത്തിൽ സ്വക്ഷേത്രമായ മേടത്തിൽ ചൊവ്വ),\n"
                      "ചൊവ്വയിൽ വ്യാഴത്തിന്റെ ദൃഷ്ടി ദോഷം കുറയ്ക്കുമെന്നും കരുതുന്നു. <strong>രണ്ടുപേർക്കും</strong>\n"
                      "ചൊവ്വാദോഷമുണ്ടെങ്കിൽ ദോഷം പരസ്പരം റദ്ദാകുമെന്നാണ് പാരമ്പര്യം — അതുകൊണ്ടാണ് ചൊവ്വാദോഷ\n"
                      "ജാതകത്തിന് ചൊവ്വാദോഷ ജാതകം തന്നെ ചേർക്കുന്നത്. ലഗ്നത്തെ ആശ്രയിക്കുന്നതിനാൽ ചൊവ്വാദോഷം\n"
                      "നോക്കാൻ വിശ്വസനീയമായ ജനനസമയം വേണം.</p>"),
        "km.how": ("<h2>ഞങ്ങളുടെ പൊരുത്തം ടൂൾ പ്രവർത്തിക്കുന്നത് എങ്ങനെ</h2>\n"
                   "<p>രണ്ടുപേരുടെയും ജനനത്തീയതി, സമയം, സ്ഥലം നൽകുക. രണ്ട് ജാതകങ്ങളും സ്വിസ് എഫെമെറിസ്\n"
                   "ഉപയോഗിച്ച് നിരയന (ലാഹിരി അയനാംശം) രീതിയിൽ ഗണിക്കുന്നു; ഓരോ കൂടത്തിനും ശാസ്ത്രീയ\n"
                   "പട്ടികകളനുസരിച്ച് മാർക്ക് നൽകുന്നു, ഓരോ പരിഹാരവും പേരെടുത്തു കാണിക്കുന്നു. മുഴുവൻ {total}\n"
                   "പോയിന്റ് വിശദാംശവും രണ്ടുപേരുടെയും ചൊവ്വാദോഷ നിലയും സൗജന്യമായി, സൈൻ അപ്പ് ഇല്ലാതെ\n"
                   "ലഭിക്കും.</p>"),
        "km.cta2": "ജാതകപ്പൊരുത്തം തുറക്കുക",
        "koota.varna": "വർണം",
        "koota.vashya": "വശ്യം",
        "koota.tara": "താരാ (ദിനം)",
        "koota.yoni": "യോനി",
        "koota.graha_maitri": "ഗ്രഹമൈത്രി",
        "koota.gana": "ഗണം",
        "koota.bhakoot": "ഭകൂടം (രാശി)",
        "koota.nadi": "നാഡി",
        "koota_about.varna": ("ചന്ദ്രരാശിയുടെ വർണത്തിൽ നിന്നുള്ള ആത്മീയ-തൊഴിൽ സ്വഭാവം. വരന്റെ വർണം "
                              "വധുവിന്റേതിനെക്കാൾ താഴെയല്ലെങ്കിൽ മുഴുവൻ പോയിന്റ്."),
        "koota_about.vashya": "പരസ്പര ആകർഷണവും സ്വാധീനവും — ഏത് രാശി മറ്റേതിനെ “ആകർഷിക്കുന്നു”.",
        "koota_about.tara": ("ആരോഗ്യവും ക്ഷേമവും, രണ്ട് ജന്മനക്ഷത്രങ്ങൾക്കിടയിലെ എണ്ണത്തിൽ നിന്ന്; "
                             "3, 5, 7 താരകൾ പ്രതികൂലമാണ്."),
        "koota_about.yoni": ("ശാരീരികവും ദാമ്പത്യപരവുമായ പൊരുത്തം; ഓരോ നക്ഷത്രത്തിനും ഒരു മൃഗയോനിയുണ്ട്, "
                             "പരസ്പരം ശത്രുക്കളായ മൃഗങ്ങൾക്ക് പൂജ്യം പോയിന്റ്."),
        "koota_about.graha_maitri": ("രണ്ട് ചന്ദ്രരാശികളുടെയും അധിപന്മാർ തമ്മിലുള്ള സൗഹൃദം — "
                                     "ദമ്പതികളുടെ മാനസിക ഇണക്കം."),
        "koota_about.gana": "സ്വഭാവം: ദേവ (ദൈവികം), മനുഷ്യ (മാനുഷികം) അല്ലെങ്കിൽ അസുര (ഉഗ്രം) ഗണം.",
        "koota_about.bhakoot": ("രണ്ട് ചന്ദ്രരാശികളുടെ പരസ്പര സ്ഥാനം. 2/12, 5/9, 6/8 സ്ഥാനങ്ങൾ ഭകൂടദോഷമാണ്; "
                                "രാശ്യധിപന്മാർ ഒന്നോ മിത്രങ്ങളോ ആണെങ്കിൽ ഇത് റദ്ദാകും."),
        "koota_about.nadi": ("ഏറ്റവും കൂടുതൽ പോയിന്റുള്ള കൂടം, ആരോഗ്യവും സന്താനവുമായി ബന്ധപ്പെട്ടത്. ഇരുവർക്കും "
                             "ഒരേ നാഡിയെങ്കിൽ നാഡീദോഷം; ഒരേ രാശി/വ്യത്യസ്ത നക്ഷത്രം, അല്ലെങ്കിൽ ഒരേ നക്ഷത്രം/"
                             "വ്യത്യസ്ത പാദം ആണെങ്കിൽ ശാസ്ത്രീയ പരിഹാരമുണ്ട്."),
        "km.band0": "ശുപാർശ ചെയ്യുന്നില്ല",
        "km.band1": "സ്വീകാര്യം",
        "km.band2": "നല്ലത്",
        "km.band3": "അത്യുത്തമം",

        "fk.title": "സൗജന്യ ജാതകം ഓൺലൈൻ — മലയാളത്തിൽ ജനന ജാതകം | {brand}",
        "fk.desc": ("നിങ്ങളുടെ ജനന ജാതകം സൗജന്യമായി ഓൺലൈനിൽ: ഉത്തര/ദക്ഷിണേന്ത്യൻ ശൈലിയിൽ രാശിചക്രം, "
                    "ഗ്രഹനില, ജന്മനക്ഷത്രം, വിംശോത്തരി ദശ, നവാംശം ഉൾപ്പെടെ വർഗചക്രങ്ങൾ, ചൊവ്വാദോഷം, "
                    "ഏഴരശ്ശനി, കാലസർപ്പദോഷ പരിശോധന — സൈൻ ഇൻ വേണ്ട."),
        "fk.crumb": "സൗജന്യ ജാതകം",
        "fk.intro": ("<h1>സൗജന്യ ജനന ജാതകം ഓൺലൈൻ</h1>\n"
                     "<p class=\"hi\">മലയാളത്തിൽ സൗജന്യ ജാതകം — ഗ്രഹനില, നവാംശം, ദശാപഹാരം</p>\n"
                     "<p><strong>ജനന ജാതകം</strong> (ജന്മകുണ്ഡലി) നിങ്ങൾ ജനിച്ച കൃത്യ നിമിഷത്തിലും സ്ഥലത്തിലുമുള്ള\n"
                     "ആകാശത്തിന്റെ ഭൂപടമാണ്: അപ്പോൾ കിഴക്കേ ചക്രവാളത്തിൽ പന്ത്രണ്ട് രാശികളിൽ ഏതാണ്\n"
                     "ഉദിച്ചുകൊണ്ടിരുന്നത് (നിങ്ങളുടെ <strong>ലഗ്നം</strong>), സൂര്യൻ, ചന്ദ്രൻ, ചൊവ്വ, ബുധൻ, വ്യാഴം,\n"
                     "ശുക്രൻ, ശനി, രാഹു, കേതു എന്നിവ ഏതെല്ലാം രാശികളിലും 27 നക്ഷത്രങ്ങളിൽ ഏതിലും നിന്നിരുന്നു\n"
                     "എന്നത്. സ്വഭാവം, ജീവിതത്തിന്റെ പന്ത്രണ്ട് മേഖലകൾ, എല്ലാറ്റിനുമുപരി ദശകളിലൂടെ <em>കാലം</em> —\n"
                     "ഇവയെല്ലാം വൈദിക ജ്യോതിഷം ഈ ഒരു ജാതകത്തിൽ നിന്നാണ് വായിക്കുന്നത്. ഞങ്ങളുടെ ജാതകം\n"
                     "മിനിറ്റുവരെ കൃത്യമായി ഗണിക്കുന്നു, സൗജന്യവുമാണ്.</p>"),
        "fk.cta1": "എന്റെ സൗജന്യ ജാതകം ഇപ്പോൾ തയ്യാറാക്കൂ",
        "fk.need": ("<p>നിങ്ങളുടെ ജനന <strong>തീയതി</strong>, <strong>സമയം</strong>, <strong>സ്ഥലം</strong> എന്നിവ വേണം.\n"
                    "സൈൻ ഇൻ ഇല്ല, കാർഡ് ഇല്ല.</p>"),
        "fk.includes": ("<h2>സൗജന്യ ജാതകത്തിൽ എന്തെല്ലാം</h2>\n"
                        "<ul>\n"
                        "<li><strong>രാശിചക്രം (D1)</strong> ഉത്തരേന്ത്യൻ അല്ലെങ്കിൽ ദക്ഷിണേന്ത്യൻ ശൈലിയിൽ — ഒറ്റ ടാപ്പിൽ മാറ്റാം.</li>\n"
                        "<li><strong>ഗ്രഹനില</strong>: ഒമ്പത് ഗ്രഹങ്ങളുടെയും ലഗ്നത്തിന്റെയും രാശി, ഡിഗ്രി, ഭാവം, ബലം\n"
                        "(ഉച്ചം/സ്വക്ഷേത്രം/നീചം), വക്രസ്ഥിതി — ചന്ദ്രന്റെ നക്ഷത്രവും പാദവും സഹിതം.</li>\n"
                        "<li><strong>പന്ത്രണ്ട് ഭാവങ്ങൾ</strong>, ഓരോന്നിലുമുള്ള ഗ്രഹങ്ങളോടെ.</li>\n"
                        "<li><strong>വിംശോത്തരി ദശ</strong>: ഇപ്പോഴത്തെ മഹാദശയും അപഹാരവും തീയതികളോടെ,\n"
                        "ദൃശ്യ സമയരേഖയിൽ.</li>\n"
                        "<li><strong>വർഗചക്രങ്ങൾ</strong>: {vargas}.</li>\n"
                        "<li><strong>അഷ്ടകവർഗം</strong>: ഭാവം തിരിച്ച് സർവാഷ്ടകവർഗ, ഭിന്നാഷ്ടകവർഗ ബിന്ദുക്കൾ.</li>\n"
                        "<li><strong>ജൈമിനി</strong> ചരകാരകങ്ങൾ (ആത്മകാരകൻ മുതൽ ദാരകാരകൻ വരെ), ആരൂഢപദങ്ങൾ, ഒപ്പം\n"
                        "ലഗ്നം, ചന്ദ്രൻ, സൂര്യൻ എന്നിവയിൽ നിന്ന് ഒരുമിച്ച് നോക്കുന്ന <strong>സുദർശന ചക്രം</strong>.</li>\n"
                        "<li><strong>ദോഷ പരിശോധന</strong>: ചൊവ്വാദോഷം, ഏഴരശ്ശനി, കാലസർപ്പദോഷം.</li>\n"
                        "<li>നിങ്ങളുടെ ജാതകത്തിനും ഇപ്പോഴത്തെ ദശയ്ക്കും അനുസരിച്ച് <strong>രത്നവും പരിഹാരവും</strong>.</li>\n"
                        "<li>ജാതക ഡാഷ്ബോർഡിൽ നിങ്ങളുടെ <strong>ദിനഫലം</strong>, ഇന്നത്തെ പഞ്ചാംഗം.</li>\n"
                        "</ul>\n"
                        "<p>എല്ലാം <strong>നിരയന രാശിചക്രവും ലാഹിരി അയനാംശവും</strong>, സമ്പൂർണ രാശി ഭാവരീതിയും\n"
                        "ഉപയോഗിച്ച് സ്വിസ് എഫെമെറിസിൽ നിന്ന് ഗണിക്കുന്നു. സൗജന്യ അക്കൗണ്ടിൽ ജാതകങ്ങൾ സൂക്ഷിക്കാം,\n"
                        "ജാതകം PDF ആയി ഡൗൺലോഡ് ചെയ്യാം, AI ജ്യോതിഷിയോട് ആദ്യ ചോദ്യങ്ങൾ സൗജന്യമായി ചോദിക്കാം.</p>"),
        "fk.read": ("<h2>നിങ്ങളുടെ ജാതകം എങ്ങനെ വായിക്കാം</h2>\n"
                    "<h3>1. ലഗ്നത്തിൽ നിന്നു തുടങ്ങുക</h3>\n"
                    "<p>ഒന്നാം ഭാവം ജനനസമയത്ത് ഉദിച്ചുകൊണ്ടിരുന്ന രാശിയാണ്. ഉത്തരേന്ത്യൻ ചക്രത്തിൽ ഇത് മുകളിൽ\n"
                    "നടുവിലെ വജ്രാകൃതിയിലുള്ള കളമാണ്; ഓരോ കളത്തിലും എഴുതിയ സംഖ്യ <em>രാശി</em>യെയാണ് കാണിക്കുന്നത്\n"
                    "(1 = മേടം … 12 = മീനം), ഭാവത്തെയല്ല. ദക്ഷിണേന്ത്യൻ ചക്രത്തിൽ രാശികൾ സ്ഥിരം കളങ്ങളിലാണ്,\n"
                    "ലഗ്നം അടയാളപ്പെടുത്തിയിരിക്കും. ലഗ്നവും ലഗ്നാധിപനും ശരീരം, സ്വഭാവം, ജീവിതത്തിന്റെ പൊതുദിശ\n"
                    "എന്നിവ വിവരിക്കുന്നു.</p>\n"
                    "<h3>2. നിങ്ങളുടെ കൂറും നക്ഷത്രവും ശ്രദ്ധിക്കുക</h3>\n"
                    "<p>ഇന്ത്യൻ രീതിയിൽ നിങ്ങളുടെ <strong>രാശി</strong> (കൂറ്) ചന്ദ്രൻ നിൽക്കുന്ന രാശിയാണ്, സൂര്യന്റേതല്ല.\n"
                    "രാശിഫലം, ഏഴരശ്ശനി, ജാതകപ്പൊരുത്തം എന്നിവയ്ക്ക് ഇതാണ് ഉപയോഗിക്കുന്നത്; നിങ്ങളുടെ\n"
                    "വിംശോത്തരി ദശ എവിടെനിന്നു തുടങ്ങുന്നു എന്നു നിശ്ചയിക്കുന്നത് ചന്ദ്രന്റെ നക്ഷത്രമാണ്.</p>\n"
                    "<h3>3. ഭാവമനുസരിച്ച് ഗ്രഹങ്ങളെ വായിക്കുക</h3>\n"
                    "<p>ഓരോ ഭാവവും ജീവിതത്തിന്റെ ഒരു മേഖലയാണ്: 1 സ്വയം, 2 ധനവും കുടുംബവും, 3 ധൈര്യവും\n"
                    "സഹോദരങ്ങളും, 4 വീടും അമ്മയും, 5 മക്കളും ബുദ്ധിയും, 6 ആരോഗ്യവും ശത്രുക്കളും, 7 വിവാഹവും\n"
                    "പങ്കാളിത്തവും, 8 ആയുസ്സും പെട്ടെന്നുള്ള മാറ്റങ്ങളും, 9 ഭാഗ്യവും ധർമവും, 10 തൊഴിൽ, 11 ലാഭം,\n"
                    "12 ചെലവും മോക്ഷവും. ഒരു ഗ്രഹം അത് നിൽക്കുന്ന ഭാവത്തെയും അത് ഭരിക്കുന്ന ഭാവങ്ങളെയും\n"
                    "സ്വാധീനിക്കുന്നു; അതിന്റെ ബലം (ഉച്ചം, സ്വക്ഷേത്രം, നീചം) അത് എത്ര നന്നായി ഫലം തരുമെന്ന് പറയുന്നു.</p>\n"
                    "<h3>4. നടക്കുന്ന ദശ നോക്കുക</h3>\n"
                    "<p>ദശ <em>എപ്പോൾ</em> എന്നു പറയുന്നു. മഹാദശാനാഥനും അതിനുള്ളിലെ അപഹാരനാഥനും — ഈ കാലയളവിൽ\n"
                    "അവരുടെ ഭാവങ്ങളാണ് സജീവമാകുന്നത്; അതുകൊണ്ടാണ് സമാനമായ ജാതകമുള്ള രണ്ടുപേർക്ക് വളരെ\n"
                    "വ്യത്യസ്തമായ വർഷങ്ങൾ ഉണ്ടാകുന്നത്.</p>\n"
                    "<h3>5. ദോഷങ്ങളെ സന്ദർഭത്തിൽ കാണുക</h3>\n"
                    "<p>ദോഷം വായിച്ചു മനസ്സിലാക്കേണ്ട ഒരു ഘടനയാണ്, വിധിയല്ല. ചൊവ്വാദോഷത്തിന് ശാസ്ത്രീയ\n"
                    "പരിഹാരങ്ങളുണ്ട്; ഏഴരശ്ശനി എല്ലാവരും ജീവിതത്തിൽ രണ്ടോ മൂന്നോ തവണ കടന്നുപോകുന്ന ഏഴര\n"
                    "വർഷത്തെ ശനി ഗോചാരമാണ്. ദോഷ റിപ്പോർട്ട് അത് കണ്ടെത്തിയ പരിഹാരങ്ങൾ പേരെടുത്തു പറയുന്നു.</p>"),
        "fk.cta2": "എന്റെ ജനന ജാതകം തയ്യാറാക്കൂ — സൗജന്യം",
        "fk.faq_h2": "<h2>പതിവ് ചോദ്യങ്ങൾ</h2>",
        "varga.D1": "രാശി", "varga.D3": "ദ്രേക്കാണം", "varga.D7": "സപ്താംശം",
        "varga.D9": "നവാംശം", "varga.D10": "ദശാംശം", "varga.D12": "ദ്വാദശാംശം",
    },

    "bn": {
        "tool.panchang": "পঞ্জিকা",
        "tool.rahu-kaal": "রাহুকাল",
        "tool.choghadiya": "চৌঘড়িয়া",
        "when": "{vara}, {date} · {place} · ভারতীয় সময়",
        "limb.until": "{name} {time} পর্যন্ত",
        "limb.then": "তারপর {name}",
        "limb.pada": "পাদ",
        "paksha.full": "{paksha} পক্ষ",
        "cities.heading": "অন্যান্য শহরের {tool}",
        "links.heading": "আরও বিনামূল্যের পরিষেবা",
        "links.tool_in_city": "{city}-এর {tool}",
        "links.milan": "যোটক বিচার (36 গুণ)",
        "links.kundali": "বিনামূল্যে জন্মকুণ্ডলী",
        "links.muhurat": "শুভ মুহূর্ত খুঁজুন",
        "links.rashifal": "আজকের রাশিফল",
        "links.vrat": "{city}-এ আজকের ব্রত ও উৎসব",
        "nf.title": "শহর পাওয়া যায়নি — {brand}",
        "nf.desc": "{tool}: এই শহরটি আমাদের তালিকায় নেই।",
        "nf.body": ("<h1>{tool}: শহর পাওয়া যায়নি</h1>"
                    "<p>“{slug}”-এর জন্য এখনও আমাদের কোনো পাতা নেই। নীচে থেকে একটি শহর বেছে নিন, অথবা "
                    '<a href="{app}">{tool} খুলুন</a> — সেখানে পৃথিবীর '
                    "যেকোনো জায়গা বেছে নেওয়া যায়।</p>"),

        "p.title": "আজকের পঞ্জিকা {city}, {date} — তিথি, নক্ষত্র, রাহুকাল | {brand}",
        "p.desc": ("{city}-এর আজকের পঞ্জিকা ({vara}, {date}): {paksha} পক্ষের {tithi} তিথি, "
                   "{nakshatra} নক্ষত্র, সূর্যোদয় {sunrise}, রাহুকাল {rahu}। সুইস এফেমেরিস থেকে নির্ভুল গণনা।"),
        "p.h1": "<h1>{city}-এর আজকের পঞ্জিকা</h1>",
        "p.sub": '<p class="hi">তিথি, নক্ষত্র, যোগ, করণ ও রাহুকাল — {city}</p>',
        "p.box": ("<div class=\"box\"><p>আজ {city}-এ <strong>{paksha} {tithi}</strong>,\n"
                  "চন্দ্র রয়েছে <strong>{nakshatra}</strong> নক্ষত্রে। রাহুকাল\n"
                  "<strong>{rahu}</strong> — এই সময়ে নতুন কোনো কাজ শুরু করবেন না।</p></div>"),
        "p.r_vara": "বার",
        "p.r_tithi": "তিথি",
        "p.r_paksha": "পক্ষ",
        "p.r_nakshatra": "নক্ষত্র",
        "p.r_yoga": "যোগ",
        "p.r_karana": "করণ",
        "p.r_sunrise": "সূর্যোদয়",
        "p.r_sunset": "সূর্যাস্ত",
        "p.r_moonrise": "চন্দ্রোদয়",
        "p.r_moonset": "চন্দ্রাস্ত",
        "p.r_moon_sign": "চন্দ্র রাশি",
        "p.r_rahu": "রাহুকাল",
        "p.r_yama": "যমগণ্ড",
        "p.r_gulika": "গুলিক কাল",
        "p.r_abhijit": "অভিজিৎ মুহূর্ত",
        "p.v_vara": "{vara}",
        "p.v_paksha": "{paksha_full}",
        "p.no_moonrise": "এই দিন চন্দ্রোদয় নেই",
        "p.no_moonset": "এই দিন চন্দ্রাস্ত নেই",
        "p.no_abhijit": "বুধবারে অভিজিৎ মুহূর্ত ধরা হয় না",
        "p.note": ("<p>সব সময় {place} ({lat}° উত্তর, {lon}° পূর্ব)-এর জন্য, ভারতীয় প্রমাণ\n"
                   "সময়ে। পঞ্জিকার দিন এক সূর্যোদয় থেকে পরের সূর্যোদয় পর্যন্ত, তাই কোনো তিথি বা নক্ষত্র\n"
                   "মাঝরাতের পরেও শেষ হতে পারে। সূর্যোদয় ধরা হয়েছে ভারতীয় পঞ্জিকার মতো সূর্যের উপরের প্রান্ত\n"
                   "দেখা দেওয়ার মুহূর্তে (বায়ুমণ্ডলীয় প্রতিসরণ সহ); নক্ষত্র ও যোগ লাহিড়ী অয়নাংশে গণনা করা।</p>"),
        "p.cta": "পুরো পঞ্জিকা খুলুন — যেকোনো শহর, যেকোনো তারিখ",
        "p.limbs": ("<h2>পঞ্জিকার পাঁচ অঙ্গ</h2>\n"
                    "<p><strong>তিথি</strong> হল চান্দ্র দিন — চন্দ্র সূর্যের থেকে প্রতি 12° এগোলে একটি তিথি।\n"
                    "<strong>নক্ষত্র</strong> হল 27টির মধ্যে যে নক্ষত্রে চন্দ্র থাকে। <strong>যোগ</strong> আসে\n"
                    "সূর্য ও চন্দ্রের দ্রাঘিমার যোগফল থেকে, আর <strong>করণ</strong> হল অর্ধেক তিথি।\n"
                    "<strong>বার</strong> সপ্তাহের দিন, যা সূর্যোদয় থেকে গোনা হয়। এই পাঁচটি মিলেই\n"
                    "পঞ্চাঙ্গ বা পঞ্জিকা (“পাঁচ অঙ্গ”), যা যেকোনো শুভ কাজের আগে দেখা হয়।</p>"),

        "rk.title": "রাহুকাল আজ {city} — {rahu}, {date} | {brand}",
        "rk.desc": ("আজ ({vara}, {date}) {city}-এ রাহুকাল {rahu}। সঙ্গে যমগণ্ড "
                    "{yama} ও গুলিক কাল {gulika}, "
                    "এই সপ্তাহের সময়সূচি এবং রাহুকালের অর্থ।"),
        "rk.h1": "<h1>{city}-এ আজকের রাহুকাল</h1>",
        "rk.sub": '<p class="hi">আজ রাহুকাল, যমগণ্ড ও গুলিক কাল কখন — {city}</p>',
        "rk.r_rahu": "রাহুকাল",
        "rk.r_yama": "যমগণ্ড",
        "rk.r_gulika": "গুলিক কাল",
        "rk.r_abhijit": "অভিজিৎ মুহূর্ত",
        "rk.r_sun": "সূর্যোদয় / সূর্যাস্ত",
        "rk.no_abhijit": "বুধবারে অভিজিৎ মুহূর্ত ধরা হয় না",
        "rk.cta": "যেকোনো শহর বা তারিখের রাহুকাল দেখুন",
        "rk.about": ("<h2>রাহুকাল কী?</h2>\n"
                     "<p>রাহুকাল হল প্রতিদিনের প্রায় দেড় ঘণ্টার একটি সময়, যা প্রথা অনুযায়ী রাহুর (চন্দ্রের উত্তর\n"
                     "পাত) অধীন বলে ধরা হয়। সূর্যোদয় থেকে সূর্যাস্ত পর্যন্ত দিনকে আটটি সমান ভাগে ভাগ করা হয়,\n"
                     "তার একটি ভাগ রাহুর। কোন ভাগ, তা বারের উপর নির্ভর করে: রবিবার অষ্টম, সোমবার দ্বিতীয়,\n"
                     "মঙ্গলবার সপ্তম, বুধবার পঞ্চম, বৃহস্পতিবার ষষ্ঠ, শুক্রবার চতুর্থ এবং শনিবার তৃতীয়।</p>\n"
                     "<p>যেহেতু এটি প্রকৃত সূর্যোদয় ও সূর্যাস্ত মেনে চলে, তাই রাহুকাল প্রতিটি শহরে আলাদা এবং\n"
                     "সারা বছর ধরে বদলায় — সেজন্য “সোমবার 7:30–9:00”-এর মতো বাঁধা তালিকা কেবল আনুমানিক। প্রথা\n"
                     "অনুযায়ী রাহুকালে নতুন উদ্যোগ শুরু, চুক্তিতে সই, যাত্রা শুরু বা বড় কেনাকাটা এড়িয়ে চলা হয়;\n"
                     "আগে থেকে চলা কাজ চালিয়ে যাওয়া যায়। যমগণ্ড ও গুলিক কাল দিনের আরও দুটি অষ্টমাংশ, যেগুলিতেও\n"
                     "একই রকম সাবধানতা মানা হয়।</p>"),
        "rk.week_h2": "<h2>এই সপ্তাহে {city}-এর রাহুকাল</h2>",
        "rk.th_day": "দিন",
        "rk.th_rahu": "রাহুকাল",
        "rk.th_yama": "যমগণ্ড",
        "rk.th_gulika": "গুলিক",

        "ch.title": "আজকের চৌঘড়িয়া {city}, {date} — দিন ও রাতের শুভ সময় | {brand}",
        "ch.desc": ("{city}-এর আজকের চৌঘড়িয়া ({vara}, {date}): দিন ও রাতের সব 16টি মুহূর্ত — "
                    "অমৃত, শুভ, লাভ, চর, রোগ, কাল, উদ্বেগ — সূর্যোদয় {sunrise} থেকে শুরু ও শেষের নির্ভুল সময় সহ।"),
        "ch.h1": "<h1>{city}-এ আজকের চৌঘড়িয়া</h1>",
        "ch.sub": '<p class="hi">দিন ও রাতের শুভ-অশুভ সময় — {city}</p>',
        "ch.first_good": "{name} — {time} থেকে",
        "ch.none": "নেই",
        "ch.box": ("<div class=\"box\"><p>সূর্যোদয় <strong>{sunrise}</strong>, সূর্যাস্ত\n"
                   "<strong>{sunset}</strong>। দিনের প্রথম শুভ চৌঘড়িয়া:\n"
                   "<strong>{first_good}</strong>।</p></div>"),
        "ch.day_h2": "<h2>দিনের চৌঘড়িয়া</h2>",
        "ch.night_h2": "<h2>রাতের চৌঘড়িয়া</h2>",
        "ch.th": "<tr><th>সময়</th><th>চৌঘড়িয়া</th><th>প্রকৃতি</th></tr>",
        # {desc} (the engine's slot description, English or Hindi only) is left out
        "ch.row": ('<tr><td>{when}</td><td class="{cls}"><strong>{name}</strong>'
                   "<small>অধিপতি: {ruler}</small></td>"
                   "<td>{quality}<small>{desc}</small></td></tr>"),
        "ch.cta": "লাইভ চৌঘড়িয়া ঘড়ি খুলুন",
        "ch.about": ("<h2>চৌঘড়িয়া কীভাবে হিসাব করা হয়</h2>\n"
                     "<p>সূর্যোদয় থেকে সূর্যাস্ত পর্যন্ত দিন, আর সূর্যাস্ত থেকে পরের সূর্যোদয় পর্যন্ত রাত — দুটিকেই\n"
                     "আটটি করে সমান ভাগে ভাগ করা হয়, যাদের বলে চৌঘড়িয়া (“চার ঘড়ি”)। প্রতিটি ভাগের একজন অধিপতি\n"
                     "গ্রহ আছে, আর নাম তার প্রকৃতি অনুযায়ী: <strong>অমৃত</strong>, <strong>শুভ</strong> ও\n"
                     "<strong>লাভ</strong> শুভ, <strong>চর</strong> মধ্যম এবং যাত্রার পক্ষে ভালো, আর\n"
                     "<strong>রোগ</strong>, <strong>কাল</strong> ও <strong>উদ্বেগ</strong>-এ নতুন কাজ শুরু এড়িয়ে\n"
                     "চলা হয়। ক্রম শুরু হয় বারের অধিপতি থেকে, তাই প্রতিদিন বদলায় — আর প্রতিটি ভাগের দৈর্ঘ্য\n"
                     "{city}-এর প্রকৃত দিনের দৈর্ঘ্য মেনে চলে।</p>"),

        "km.title": "যোটক বিচার — অষ্টকূট গুণ মিলন ({total} গুণ) বিস্তারিত | {brand}",
        "km.desc": ("যোটক বিচার বা কুণ্ডলী মিলন কীভাবে হয়: অষ্টকূট গুণ মিলনের 8টি কূট, মোট {total} গুণ, "
                    "বিয়ের জন্য কত গুণ ভালো, আর মঙ্গল দোষ কীভাবে দেখা হয়। বিনামূল্যে অনলাইন "
                    "যোটক বিচার।"),
        "km.crumb": "যোটক বিচার",
        "km.intro": ("<h1>যোটক বিচার: অষ্টকূট গুণ মিলনের পূর্ণ ব্যাখ্যা</h1>\n"
                     "<p class=\"hi\">কুণ্ডলী মিলন — অষ্টকূট গুণ মিলন ({total} গুণ)</p>\n"
                     "<p>যোটক বিচার (কুণ্ডলী মিলন) হল বিয়ের আগে পাত্র-পাত্রীর সামঞ্জস্য দেখার প্রথাগত বৈদিক\n"
                     "পদ্ধতি। উত্তর ভারতে সবচেয়ে প্রচলিত পদ্ধতি <strong>অষ্টকূট গুণ মিলন</strong>: কনে ও বরের\n"
                     "কোষ্ঠীতে আটটি বিষয় (<em>কূট</em>) তুলনা করে মোট <strong>{total} গুণের</strong> মধ্যে নম্বর\n"
                     "দেওয়া হয়। প্রতিটিই দেখা হয় <strong>চন্দ্র</strong> থেকে — জন্মের সময় তার রাশি ও নক্ষত্র —\n"
                     "তাই সঠিক জন্মতারিখ ও জন্মস্থান দরকার, কিন্তু জন্মসময়ের উপর ফল প্রায় নির্ভর করে না।</p>"),
        "km.cta1": "এখনই দুটি কোষ্ঠী মিলিয়ে দেখুন — বিনামূল্যে",
        "km.naam": ('<p>জন্মসময় জানা নেই? <a href="{href}">নাম দিয়ে যোটক বিচার</a> করে দেখুন — '
                    "নামের প্রথম অক্ষর দিয়ে প্রথাগত মিলন।</p>"),
        "km.kootas_h2": "<h2>আটটি কূট ও তাদের গুণ</h2>",
        "km.th": "<tr><th>কূট</th><th>গুণ</th><th>কী দেখা হয়</th></tr>",
        "km.row": "<tr><td><strong>{name}</strong></td><td>{pts}</td><td>{text}</td></tr>",
        "km.total": "মোট",
        "km.score_h2": "<h2>কত গুণ মিললে ভালো?</h2>",
        "km.score_th": "<tr><th>গুণ</th><th>প্রথাগত অর্থ</th></tr>",
        "km.below": "{n}-এর কম",
        "km.score_p": ("<p>18 গুণ প্রথাগত ন্যূনতম সীমা। শুধু মোট নম্বর দিয়ে পুরো কথা বলা যায় না: বেশি নম্বরের\n"
                       "সঙ্গে পরিহারহীন নাড়ী বা ভকূট দোষ থাকলে সাবধানে বিচার করা হয়, আর কম নম্বরেও ভালো\n"
                       "গ্রহমৈত্রী থাকলে ও কোনো দোষ না থাকলে মিলন প্রায়ই চলনসই ধরা হয়। এই সীমাগুলি দীর্ঘ\n"
                       "ঐতিহ্যের একটি রীতি, কোনো পরিমাপ নয় — এগুলি পথনির্দেশ, কোনো সম্পর্কের উপর চূড়ান্ত রায় নয়।</p>"),
        "km.ord1": "{n}",
        "km.ord2": "{n}",
        "km.ordn": "{n}",
        "km.or": " বা ",
        "km.mangal": ("<h2>মঙ্গল দোষ (মাঙ্গলিক)</h2>\n"
                      "<p>মঙ্গল দোষ 36 গুণের থেকে আলাদা করে দেখা হয়। কোষ্ঠী মাঙ্গলিক হয় যখন মঙ্গল\n"
                      "<strong>লগ্ন</strong>, <strong>চন্দ্র</strong> বা <strong>শুক্র</strong> থেকে গুনে {houses} নম্বর\n"
                      "ভাবে থাকে। শাস্ত্রে কিছু রাশি-অবস্থানকে ছাড় দেওয়া হয়েছে (যেমন প্রথম ভাবে নিজের রাশি মেষে\n"
                      "মঙ্গল), আর মঙ্গলের উপর বৃহস্পতির দৃষ্টি দোষকে নরম করে বলে ধরা হয়। পাত্র-পাত্রী\n"
                      "<strong>দুজনেই</strong> মাঙ্গলিক হলে প্রথা অনুযায়ী দোষ পরস্পর কেটে যায় — সেজন্যই মাঙ্গলিকের\n"
                      "বিয়ে মাঙ্গলিকের সঙ্গে দেওয়া হয়। লগ্নের উপর নির্ভর করে বলে মঙ্গল দোষ বিচারে নির্ভরযোগ্য\n"
                      "জন্মসময় দরকার।</p>"),
        "km.how": ("<h2>আমাদের যোটক বিচার কীভাবে কাজ করে</h2>\n"
                   "<p>দুজনের জন্মতারিখ, সময় ও স্থান দিন। দুটি কোষ্ঠীই সুইস এফেমেরিস থেকে নিরয়ণ (লাহিড়ী\n"
                   "অয়নাংশ) পদ্ধতিতে তৈরি হয়, আর প্রতিটি কূটের নম্বর শাস্ত্রীয় সারণি থেকে দেওয়া হয় — প্রতিটি\n"
                   "পরিহারের নাম সহ। আপনি পাবেন পুরো {total} গুণের বিস্তারিত হিসাব এবং দুজনের মঙ্গল দোষের\n"
                   "অবস্থা — বিনামূল্যে, সাইন-আপ ছাড়াই।</p>"),
        "km.cta2": "যোটক বিচার খুলুন",
        "koota.varna": "বর্ণ",
        "koota.vashya": "বশ্য",
        "koota.tara": "তারা",
        "koota.yoni": "যোনি",
        "koota.graha_maitri": "গ্রহমৈত্রী",
        "koota.gana": "গণ",
        "koota.bhakoot": "ভকূট (রাশিকূট)",
        "koota.nadi": "নাড়ী",
        "koota_about.varna": ("চন্দ্র রাশির বর্ণ থেকে আধ্যাত্মিক ও কর্মগত স্বভাব। বরের বর্ণ কনের বর্ণের "
                              "চেয়ে নীচে না হলে পূর্ণ নম্বর।"),
        "koota_about.vashya": "পারস্পরিক আকর্ষণ ও প্রভাব — কোন রাশি অন্যটিকে “বশ” করে।",
        "koota_about.tara": ("স্বাস্থ্য ও কল্যাণ, দুই জন্মনক্ষত্রের মধ্যেকার গণনা থেকে; তৃতীয়, পঞ্চম ও "
                             "সপ্তম তারা প্রতিকূল।"),
        "koota_about.yoni": ("শারীরিক ও দাম্পত্য সামঞ্জস্য; প্রতিটি নক্ষত্রের একটি পশু-যোনি আছে, আর "
                             "পরস্পর চিরশত্রু পশুর ক্ষেত্রে নম্বর শূন্য।"),
        "koota_about.graha_maitri": "দুই চন্দ্র রাশির অধিপতিদের বন্ধুত্ব — দম্পতির মানসিক মিল।",
        "koota_about.gana": "স্বভাব: দেব (দৈব), নর (মানবিক) বা রাক্ষস (উগ্র) গণ।",
        "koota_about.bhakoot": ("দুই চন্দ্র রাশির পারস্পরিক অবস্থান। 2/12, 5/9 ও 6/8 অবস্থানে ভকূট দোষ "
                                "হয়, যা দুই রাশির অধিপতি এক হলে বা পরস্পর মিত্র হলে কেটে যায়।"),
        "koota_about.nadi": ("সবচেয়ে বেশি নম্বরের কূট, স্বাস্থ্য ও সন্তানের সঙ্গে যুক্ত। দুজনের একই নাড়ী হলে "
                             "নাড়ী দোষ; রাশি এক কিন্তু নক্ষত্র ভিন্ন, বা নক্ষত্র এক কিন্তু পাদ ভিন্ন হলে এর "
                             "শাস্ত্রীয় পরিহার আছে।"),
        # the score bands of matching.SCORE_BANDS, in order
        "km.band0": "অনুপযুক্ত",
        "km.band1": "গ্রহণযোগ্য",
        "km.band2": "ভালো",
        "km.band3": "উত্তম",

        "fk.title": "বিনামূল্যে জন্মকুণ্ডলী — অনলাইনে কোষ্ঠী তৈরি করুন | {brand}",
        "fk.desc": ("বিনামূল্যে অনলাইনে জন্মকুণ্ডলী তৈরি করুন: উত্তর বা দক্ষিণ ভারতীয় ধাঁচে লগ্ন কুণ্ডলী, "
                    "গ্রহের অবস্থান, চন্দ্র নক্ষত্র, বিংশোত্তরী দশা, নবাংশ ও অন্যান্য বর্গ কুণ্ডলী, "
                    "মাঙ্গলিক, সাড়েসাতি ও কালসর্প দোষ বিচার — সাইন-ইন ছাড়াই।"),
        "fk.crumb": "বিনামূল্যে কোষ্ঠী",
        "fk.intro": ("<h1>বিনামূল্যে জন্মকুণ্ডলী অনলাইন</h1>\n"
                     "<p class=\"hi\">বিনামূল্যে কোষ্ঠী — লগ্ন, গ্রহ, দশা ও দোষ বিচার</p>\n"
                     "<p><strong>জন্মকুণ্ডলী</strong> (কোষ্ঠী) হল আপনার জন্মের ঠিক মুহূর্তে ও স্থানে আকাশের\n"
                     "মানচিত্র: সেই সময় পূর্ব দিগন্তে বারোটি রাশির কোনটি উদিত হচ্ছিল (আপনার <strong>লগ্ন</strong>),\n"
                     "আর সূর্য, চন্দ্র, মঙ্গল, বুধ, বৃহস্পতি, শুক্র, শনি, রাহু ও কেতু কোন রাশিতে এবং 27টি নক্ষত্রের\n"
                     "কোনটিতে ছিল। বৈদিক জ্যোতিষ বাকি সবকিছু — স্বভাব, জীবনের বারোটি ক্ষেত্র, আর সবচেয়ে বড় কথা\n"
                     "দশার মাধ্যমে <em>সময়</em> — এই একটি কুণ্ডলী থেকেই বিচার করে। আমাদের কুণ্ডলী মিনিট পর্যন্ত\n"
                     "নির্ভুল গণনায় তৈরি এবং বিনামূল্যে।</p>"),
        "fk.cta1": "এখনই আমার বিনামূল্যে কোষ্ঠী তৈরি করুন",
        "fk.need": ("<p>আপনার জন্মের <strong>তারিখ</strong>, <strong>সময়</strong> ও <strong>স্থান</strong> দরকার।\n"
                    "সাইন-ইন লাগবে না, কার্ডও না।</p>"),
        "fk.includes": ("<h2>বিনামূল্যের কোষ্ঠীতে যা যা পাবেন</h2>\n"
                        "<ul>\n"
                        "<li><strong>লগ্ন কুণ্ডলী (D1)</strong> উত্তর ভারতীয় বা দক্ষিণ ভারতীয় ধাঁচে — এক ট্যাপে বদলান।</li>\n"
                        "<li><strong>গ্রহের অবস্থান</strong>: নয়টি গ্রহ ও লগ্নের রাশি, অংশ, ভাব, বল (উচ্চ/স্বক্ষেত্র/নীচ) ও\n"
                        "বক্রী অবস্থা, সঙ্গে চন্দ্রের নক্ষত্র ও পাদ।</li>\n"
                        "<li><strong>বারোটি ভাব</strong> এবং প্রতিটি ভাবে থাকা গ্রহ।</li>\n"
                        "<li><strong>বিংশোত্তরী দশা</strong>: বর্তমান মহাদশা ও অন্তর্দশা তারিখ সহ, সময়রেখায়।</li>\n"
                        "<li><strong>বর্গ কুণ্ডলী</strong>: {vargas}।</li>\n"
                        "<li><strong>অষ্টকবর্গ</strong>: প্রতিটি ভাবের সর্বাষ্টকবর্গ ও ভিন্নাষ্টকবর্গ বিন্দু।</li>\n"
                        "<li><strong>জৈমিনী</strong> চর কারক (আত্মকারক থেকে দারাকারক) ও আরূঢ় পদ, এবং লগ্ন, চন্দ্র ও\n"
                        "সূর্য থেকে একসঙ্গে দেখা <strong>সুদর্শন চক্র</strong>।</li>\n"
                        "<li><strong>দোষ বিচার</strong>: মঙ্গল দোষ (মাঙ্গলিক), সাড়েসাতি ও কালসর্প।</li>\n"
                        "<li>আপনার কোষ্ঠী ও বর্তমান দশা অনুযায়ী <strong>রত্ন ও প্রতিকারের</strong> পরামর্শ।</li>\n"
                        "<li>কোষ্ঠীর ড্যাশবোর্ডে আপনার <strong>দৈনিক ফল</strong> ও আজকের পঞ্জিকা।</li>\n"
                        "</ul>\n"
                        "<p>সবকিছু তৈরি হয় <strong>নিরয়ণ রাশিচক্র ও লাহিড়ী অয়নাংশে</strong>, সম্পূর্ণ-রাশি ভাব\n"
                        "পদ্ধতিতে, সুইস এফেমেরিস থেকে। বিনামূল্যের অ্যাকাউন্টে কোষ্ঠী সংরক্ষণ করতে পারবেন, কোষ্ঠীর\n"
                        "PDF ডাউনলোড করতে পারবেন, আর এআই জ্যোতিষীকে প্রথম প্রশ্নগুলি বিনামূল্যে করতে পারবেন।</p>"),
        "fk.read": ("<h2>কীভাবে নিজের কোষ্ঠী পড়বেন</h2>\n"
                    "<h3>1. লগ্ন দিয়ে শুরু করুন</h3>\n"
                    "<p>প্রথম ভাব হল জন্মের সময় উদিত রাশি। উত্তর ভারতীয় কুণ্ডলীতে এটি উপরের মাঝের রম্বস-আকৃতির\n"
                    "ঘর, আর প্রতিটি ঘরে লেখা সংখ্যাটি <em>রাশির</em> (1 = মেষ … 12 = মীন), ভাবের নয়। দক্ষিণ\n"
                    "ভারতীয় কুণ্ডলীতে রাশিগুলি নির্দিষ্ট ঘরে থাকে এবং লগ্ন আলাদা করে চিহ্নিত থাকে। লগ্ন ও\n"
                    "লগ্নপতি দেহ, স্বভাব ও জীবনের সামগ্রিক দিক বোঝায়।</p>\n"
                    "<h3>2. আপনার চন্দ্র রাশি ও নক্ষত্র দেখুন</h3>\n"
                    "<p>ভারতীয় রীতিতে আপনার <strong>রাশি</strong> হল চন্দ্রের রাশি, সূর্যের নয়। রাশিফল,\n"
                    "সাড়েসাতি ও যোটক বিচার এই রাশি থেকেই দেখা হয়, আর চন্দ্রের নক্ষত্র ঠিক করে আপনার\n"
                    "বিংশোত্তরী দশা কোথা থেকে শুরু হবে।</p>\n"
                    "<h3>3. ভাব অনুযায়ী গ্রহ পড়ুন</h3>\n"
                    "<p>প্রতিটি ভাব জীবনের একটি ক্ষেত্র: প্রথম নিজে, দ্বিতীয় ধন ও পরিবার, তৃতীয় সাহস ও ভাইবোন,\n"
                    "চতুর্থ গৃহ ও মা, পঞ্চম সন্তান ও বুদ্ধি, ষষ্ঠ স্বাস্থ্য ও প্রতিদ্বন্দ্বী, সপ্তম বিবাহ ও\n"
                    "অংশীদারি, অষ্টম আয়ু ও আকস্মিক পরিবর্তন, নবম ভাগ্য ও ধর্ম, দশম কর্মজীবন, একাদশ লাভ,\n"
                    "দ্বাদশ ব্যয় ও মোক্ষ। গ্রহ যে ভাবে বসে আছে এবং যে ভাবগুলির অধিপতি, সেগুলিকে প্রভাবিত করে;\n"
                    "তার অবস্থা (উচ্চ, স্বক্ষেত্র, নীচ) বলে দেয় সে কতটা ফল দিতে পারবে।</p>\n"
                    "<h3>4. চলতি দশা দেখুন</h3>\n"
                    "<p>দশা বলে <em>কখন</em>। মহাদশার অধিপতি, এবং তার ভিতরে অন্তর্দশার অধিপতি — এই গ্রহগুলির\n"
                    "ভাবই এই সময়ে সক্রিয় হয় — সেজন্যই প্রায় একই রকম কুণ্ডলীর দুজন মানুষের বছর খুব আলাদা হতে\n"
                    "পারে।</p>\n"
                    "<h3>5. দোষকে প্রসঙ্গ মেনে দেখুন</h3>\n"
                    "<p>দোষ হল বিচার করার একটি নকশা, কোনো রায় নয়। মঙ্গল দোষের শাস্ত্রীয় পরিহার আছে;\n"
                    "সাড়েসাতি শনির সাড়ে সাত বছরের গোচর, যা প্রত্যেকের জীবনে দু-তিনবার আসে। দোষের রিপোর্টে\n"
                    "পাওয়া পরিহারগুলির নামও দেওয়া থাকে।</p>"),
        "fk.cta2": "আমার জন্মকুণ্ডলী তৈরি করুন — বিনামূল্যে",
        "fk.faq_h2": "<h2>প্রায়শই জিজ্ঞাসিত প্রশ্ন</h2>",
        "varga.D1": "রাশি", "varga.D3": "দ্রেক্কাণ", "varga.D7": "সপ্তাংশ",
        "varga.D9": "নবাংশ", "varga.D10": "দশমাংশ", "varga.D12": "দ্বাদশাংশ",
    },

    "or": {
        "tool.panchang": "ପାଞ୍ଜି",
        "tool.rahu-kaal": "ରାହୁ କାଳ",
        "tool.choghadiya": "ଚୌଘଡ଼ିଆ",
        "when": "{vara}, {date} · {place} · ଭାରତୀୟ ସମୟ",
        "limb.until": "{name} {time} ପର୍ଯ୍ୟନ୍ତ",
        "limb.then": "ତା'ପରେ {name}",
        "limb.pada": "ପାଦ",
        "paksha.full": "{paksha} ପକ୍ଷ",
        "cities.heading": "ଅନ୍ୟ ସହରର {tool}",
        "links.heading": "ଆହୁରି ମାଗଣା ସେବା",
        "links.tool_in_city": "{city}ର {tool}",
        "links.milan": "କୁଣ୍ଡଳୀ ମିଳନ (36 ଗୁଣ)",
        "links.kundali": "ମାଗଣା ଜନ୍ମ କୁଣ୍ଡଳୀ",
        "links.muhurat": "ଶୁଭ ମୁହୂର୍ତ୍ତ ଖୋଜନ୍ତୁ",
        "links.rashifal": "ଆଜିର ରାଶିଫଳ",
        "links.vrat": "{city}ରେ ଆଜିର ବ୍ରତ ଓ ପର୍ବ",
        "nf.title": "ସହର ମିଳିଲା ନାହିଁ — {brand}",
        "nf.desc": "{tool}: ଏହି ସହର ଆମ ତାଲିକାରେ ନାହିଁ।",
        "nf.body": ("<h1>{tool}: ସହର ମିଳିଲା ନାହିଁ</h1>"
                    "<p>“{slug}” ପାଇଁ ଏବେ ଆମ ପାଖରେ କୌଣସି ପୃଷ୍ଠା ନାହିଁ। ତଳୁ ଗୋଟିଏ ସହର ବାଛନ୍ତୁ, କିମ୍ବା "
                    '<a href="{app}">{tool} ଖୋଲନ୍ତୁ</a> — ସେଥିରେ ପୃଥିବୀର '
                    "ଯେକୌଣସି ସ୍ଥାନ ବାଛିହେବ।</p>"),

        "p.title": "ଆଜିର ପାଞ୍ଜି {city}, {date} — ତିଥି, ନକ୍ଷତ୍ର, ରାହୁ କାଳ | {brand}",
        "p.desc": ("{city}ର ଆଜିର ପାଞ୍ଜି ({vara}, {date}): {paksha} ପକ୍ଷ {tithi} ତିଥି, "
                   "{nakshatra} ନକ୍ଷତ୍ର, ସୂର୍ଯ୍ୟୋଦୟ {sunrise}, ରାହୁ କାଳ {rahu}। ସୁଇସ୍ ଏଫେମେରିସ୍‌ରୁ ସଠିକ୍ ଗଣନା।"),
        "p.h1": "<h1>{city}ର ଆଜିର ପାଞ୍ଜି</h1>",
        "p.sub": '<p class="hi">ତିଥି, ନକ୍ଷତ୍ର, ଯୋଗ, କରଣ ଓ ରାହୁ କାଳ — {city}</p>',
        "p.box": ("<div class=\"box\"><p>ଆଜି {city}ରେ <strong>{paksha} {tithi}</strong>\n"
                  "ଏବଂ ଚନ୍ଦ୍ର <strong>{nakshatra}</strong> ନକ୍ଷତ୍ରରେ ଅଛନ୍ତି। ରାହୁ କାଳ\n"
                  "<strong>{rahu}</strong> — ଏହି ସମୟରେ କୌଣସି ନୂଆ କାମ ଆରମ୍ଭ କରନ୍ତୁ ନାହିଁ।</p></div>"),
        "p.r_vara": "ବାର",
        "p.r_tithi": "ତିଥି",
        "p.r_paksha": "ପକ୍ଷ",
        "p.r_nakshatra": "ନକ୍ଷତ୍ର",
        "p.r_yoga": "ଯୋଗ",
        "p.r_karana": "କରଣ",
        "p.r_sunrise": "ସୂର୍ଯ୍ୟୋଦୟ",
        "p.r_sunset": "ସୂର୍ଯ୍ୟାସ୍ତ",
        "p.r_moonrise": "ଚନ୍ଦ୍ରୋଦୟ",
        "p.r_moonset": "ଚନ୍ଦ୍ରାସ୍ତ",
        "p.r_moon_sign": "ଚନ୍ଦ୍ର ରାଶି",
        "p.r_rahu": "ରାହୁ କାଳ",
        "p.r_yama": "ଯମଗଣ୍ଡ",
        "p.r_gulika": "ଗୁଳିକ କାଳ",
        "p.r_abhijit": "ଅଭିଜିତ ମୁହୂର୍ତ୍ତ",
        "p.v_vara": "{vara}",
        "p.v_paksha": "{paksha_full}",
        "p.no_moonrise": "ଏହି ଦିନ ଚନ୍ଦ୍ରୋଦୟ ନାହିଁ",
        "p.no_moonset": "ଏହି ଦିନ ଚନ୍ଦ୍ରାସ୍ତ ନାହିଁ",
        "p.no_abhijit": "ବୁଧବାରରେ ଅଭିଜିତ ମୁହୂର୍ତ୍ତ ଗ୍ରହଣ କରାଯାଏ ନାହିଁ",
        "p.note": ("<p>ସମସ୍ତ ସମୟ {place} ({lat}° ଉତ୍ତର, {lon}° ପୂର୍ବ) ପାଇଁ, ଭାରତୀୟ ମାନକ\n"
                   "ସମୟରେ। ପାଞ୍ଜିର ଦିନ ସୂର୍ଯ୍ୟୋଦୟରୁ ପରବର୍ତ୍ତୀ ସୂର୍ଯ୍ୟୋଦୟ ପର୍ଯ୍ୟନ୍ତ, ତେଣୁ କୌଣସି ତିଥି ବା ନକ୍ଷତ୍ର\n"
                   "ମଧ୍ୟରାତ୍ରି ପରେ ମଧ୍ୟ ଶେଷ ହୋଇପାରେ। ସୂର୍ଯ୍ୟୋଦୟ ଭାରତୀୟ ପାଞ୍ଜି ପରି ସୂର୍ଯ୍ୟର ଉପର ଧାର ଦେଖାଯିବା\n"
                   "ମୁହୂର୍ତ୍ତରୁ (ବାୟୁମଣ୍ଡଳୀୟ ପ୍ରତିସରଣ ସହିତ) ଧରାଯାଇଛି; ନକ୍ଷତ୍ର ଓ ଯୋଗ ଲାହିଡ଼ୀ ଅୟନାଂଶରେ ଗଣନା କରାଯାଇଛି।</p>"),
        "p.cta": "ପୂରା ପାଞ୍ଜି ଖୋଲନ୍ତୁ — ଯେକୌଣସି ସହର, ଯେକୌଣସି ତାରିଖ",
        "p.limbs": ("<h2>ପାଞ୍ଜିର ପାଞ୍ଚ ଅଙ୍ଗ</h2>\n"
                    "<p><strong>ତିଥି</strong> ହେଉଛି ଚାନ୍ଦ୍ର ଦିନ — ଚନ୍ଦ୍ର ସୂର୍ଯ୍ୟଙ୍କଠାରୁ ପ୍ରତି 12° ଆଗେଇଲେ ଗୋଟିଏ ତିଥି।\n"
                    "<strong>ନକ୍ଷତ୍ର</strong> ହେଉଛି 27ଟି ମଧ୍ୟରୁ ଯେଉଁ ନକ୍ଷତ୍ରରେ ଚନ୍ଦ୍ର ଥାଆନ୍ତି। <strong>ଯୋଗ</strong>\n"
                    "ସୂର୍ଯ୍ୟ ଓ ଚନ୍ଦ୍ରଙ୍କ ଦ୍ରାଘିମାର ସମଷ୍ଟିରୁ ଆସେ, ଏବଂ <strong>କରଣ</strong> ହେଉଛି ଅଧା ତିଥି।\n"
                    "<strong>ବାର</strong> ସପ୍ତାହର ଦିନ, ଯାହା ସୂର୍ଯ୍ୟୋଦୟରୁ ଗଣାଯାଏ। ଏହି ପାଞ୍ଚଟି ମିଶି ପଞ୍ଚାଙ୍ଗ ବା\n"
                    "ପାଞ୍ଜି (“ପାଞ୍ଚ ଅଙ୍ଗ”), ଯାହା ପ୍ରତ୍ୟେକ ଶୁଭ କାମ ପୂର୍ବରୁ ଦେଖାଯାଏ।</p>"),

        "rk.title": "ରାହୁ କାଳ ଆଜି {city} — {rahu}, {date} | {brand}",
        "rk.desc": ("ଆଜି ({vara}, {date}) {city}ରେ ରାହୁ କାଳ {rahu}। ସହିତ ଯମଗଣ୍ଡ "
                    "{yama} ଓ ଗୁଳିକ କାଳ {gulika}, "
                    "ଏହି ସପ୍ତାହର ସମୟ ଏବଂ ରାହୁ କାଳର ଅର୍ଥ।"),
        "rk.h1": "<h1>{city}ରେ ଆଜିର ରାହୁ କାଳ</h1>",
        "rk.sub": '<p class="hi">ଆଜି ରାହୁ କାଳ, ଯମଗଣ୍ଡ ଓ ଗୁଳିକ କାଳ କେବେ — {city}</p>',
        "rk.r_rahu": "ରାହୁ କାଳ",
        "rk.r_yama": "ଯମଗଣ୍ଡ",
        "rk.r_gulika": "ଗୁଳିକ କାଳ",
        "rk.r_abhijit": "ଅଭିଜିତ ମୁହୂର୍ତ୍ତ",
        "rk.r_sun": "ସୂର୍ଯ୍ୟୋଦୟ / ସୂର୍ଯ୍ୟାସ୍ତ",
        "rk.no_abhijit": "ବୁଧବାରରେ ଅଭିଜିତ ମୁହୂର୍ତ୍ତ ଗ୍ରହଣ କରାଯାଏ ନାହିଁ",
        "rk.cta": "ଯେକୌଣସି ସହର ବା ତାରିଖର ରାହୁ କାଳ ଦେଖନ୍ତୁ",
        "rk.about": ("<h2>ରାହୁ କାଳ କ'ଣ?</h2>\n"
                     "<p>ରାହୁ କାଳ ହେଉଛି ପ୍ରତିଦିନର ପ୍ରାୟ ଦେଢ଼ ଘଣ୍ଟାର ଏକ ସମୟ, ଯାହା ପରମ୍ପରା ଅନୁସାରେ ରାହୁଙ୍କ (ଚନ୍ଦ୍ରଙ୍କ\n"
                     "ଉତ୍ତର ପାତ) ଅଧୀନ ବୋଲି ମାନାଯାଏ। ସୂର୍ଯ୍ୟୋଦୟରୁ ସୂର୍ଯ୍ୟାସ୍ତ ପର୍ଯ୍ୟନ୍ତ ଦିନକୁ ଆଠଟି ସମାନ ଭାଗରେ ବିଭକ୍ତ\n"
                     "କରାଯାଏ, ଏବଂ ସେଥିରୁ ଗୋଟିଏ ଭାଗ ରାହୁଙ୍କର। କେଉଁ ଭାଗ, ତାହା ବାର ଉପରେ ନିର୍ଭର କରେ: ରବିବାର ଅଷ୍ଟମ,\n"
                     "ସୋମବାର ଦ୍ୱିତୀୟ, ମଙ୍ଗଳବାର ସପ୍ତମ, ବୁଧବାର ପଞ୍ଚମ, ଗୁରୁବାର ଷଷ୍ଠ, ଶୁକ୍ରବାର ଚତୁର୍ଥ ଏବଂ ଶନିବାର\n"
                     "ତୃତୀୟ।</p>\n"
                     "<p>ଏହା ପ୍ରକୃତ ସୂର୍ଯ୍ୟୋଦୟ ଓ ସୂର୍ଯ୍ୟାସ୍ତକୁ ଅନୁସରଣ କରୁଥିବାରୁ ରାହୁ କାଳ ପ୍ରତ୍ୟେକ ସହରରେ ଭିନ୍ନ ଏବଂ\n"
                     "ବର୍ଷସାରା ବଦଳେ — ସେଥିପାଇଁ “ସୋମବାର 7:30–9:00” ଭଳି ସ୍ଥିର ତାଲିକା କେବଳ ଆନୁମାନିକ। ପରମ୍ପରା\n"
                     "ଅନୁସାରେ ରାହୁ କାଳରେ ନୂଆ ଉଦ୍ୟମ ଆରମ୍ଭ, ଚୁକ୍ତିରେ ଦସ୍ତଖତ, ଯାତ୍ରା ଆରମ୍ଭ ବା ବଡ଼ କିଣାକିଣି ଏଡ଼ାଇ\n"
                     "ଦିଆଯାଏ; ପୂର୍ବରୁ ଚାଲିଥିବା କାମ ଜାରି ରଖାଯାଇପାରେ। ଯମଗଣ୍ଡ ଓ ଗୁଳିକ କାଳ ଦିନର ଆଉ ଦୁଇଟି\n"
                     "ଅଷ୍ଟମାଂଶ, ଯେଉଁଥିରେ ମଧ୍ୟ ସେହିପରି ସାବଧାନତା ରଖାଯାଏ।</p>"),
        "rk.week_h2": "<h2>ଏହି ସପ୍ତାହରେ {city}ର ରାହୁ କାଳ</h2>",
        "rk.th_day": "ଦିନ",
        "rk.th_rahu": "ରାହୁ କାଳ",
        "rk.th_yama": "ଯମଗଣ୍ଡ",
        "rk.th_gulika": "ଗୁଳିକ",

        "ch.title": "ଆଜିର ଚୌଘଡ଼ିଆ {city}, {date} — ଦିନ ଓ ରାତିର ଶୁଭ ସମୟ | {brand}",
        "ch.desc": ("{city}ର ଆଜିର ଚୌଘଡ଼ିଆ ({vara}, {date}): ଦିନ ଓ ରାତିର ସମସ୍ତ 16ଟି ମୁହୂର୍ତ୍ତ — "
                    "ଅମୃତ, ଶୁଭ, ଲାଭ, ଚର, ରୋଗ, କାଳ, ଉଦ୍ବେଗ — ସୂର୍ଯ୍ୟୋଦୟ {sunrise}ରୁ ଆରମ୍ଭ ଓ ଶେଷର ସଠିକ୍ ସମୟ ସହିତ।"),
        "ch.h1": "<h1>{city}ରେ ଆଜିର ଚୌଘଡ଼ିଆ</h1>",
        "ch.sub": '<p class="hi">ଦିନ ଓ ରାତିର ଶୁଭ-ଅଶୁଭ ସମୟ — {city}</p>',
        "ch.first_good": "{name} — {time}ରୁ",
        "ch.none": "ନାହିଁ",
        "ch.box": ("<div class=\"box\"><p>ସୂର୍ଯ୍ୟୋଦୟ <strong>{sunrise}</strong>, ସୂର୍ଯ୍ୟାସ୍ତ\n"
                   "<strong>{sunset}</strong>। ଦିନର ପ୍ରଥମ ଶୁଭ ଚୌଘଡ଼ିଆ:\n"
                   "<strong>{first_good}</strong>।</p></div>"),
        "ch.day_h2": "<h2>ଦିନର ଚୌଘଡ଼ିଆ</h2>",
        "ch.night_h2": "<h2>ରାତିର ଚୌଘଡ଼ିଆ</h2>",
        "ch.th": "<tr><th>ସମୟ</th><th>ଚୌଘଡ଼ିଆ</th><th>ପ୍ରକୃତି</th></tr>",
        # {desc} (the engine's slot description, English or Hindi only) is left out
        "ch.row": ('<tr><td>{when}</td><td class="{cls}"><strong>{name}</strong>'
                   "<small>ଅଧିପତି: {ruler}</small></td>"
                   "<td>{quality}<small>{desc}</small></td></tr>"),
        "ch.cta": "ଲାଇଭ୍ ଚୌଘଡ଼ିଆ ଘଣ୍ଟା ଖୋଲନ୍ତୁ",
        "ch.about": ("<h2>ଚୌଘଡ଼ିଆ କିପରି ହିସାବ କରାଯାଏ</h2>\n"
                     "<p>ସୂର୍ଯ୍ୟୋଦୟରୁ ସୂର୍ଯ୍ୟାସ୍ତ ପର୍ଯ୍ୟନ୍ତ ଦିନ, ଏବଂ ସୂର୍ଯ୍ୟାସ୍ତରୁ ପରବର୍ତ୍ତୀ ସୂର୍ଯ୍ୟୋଦୟ ପର୍ଯ୍ୟନ୍ତ ରାତି —\n"
                     "ଦୁହିଁକୁ ଆଠଟି ଲେଖାଏଁ ସମାନ ଭାଗରେ ବିଭକ୍ତ କରାଯାଏ, ଯାହାକୁ ଚୌଘଡ଼ିଆ (“ଚାରି ଘଡ଼ି”) କୁହାଯାଏ।\n"
                     "ପ୍ରତ୍ୟେକ ଭାଗର ଜଣେ ଅଧିପତି ଗ୍ରହ ଅଛନ୍ତି, ଏବଂ ନାମ ତାହାର ପ୍ରକୃତି ଅନୁସାରେ: <strong>ଅମୃତ</strong>,\n"
                     "<strong>ଶୁଭ</strong> ଓ <strong>ଲାଭ</strong> ଶୁଭ, <strong>ଚର</strong> ମଧ୍ୟମ ଏବଂ ଯାତ୍ରା ପାଇଁ\n"
                     "ଭଲ, କିନ୍ତୁ <strong>ରୋଗ</strong>, <strong>କାଳ</strong> ଓ <strong>ଉଦ୍ବେଗ</strong>ରେ ନୂଆ କାମ ଆରମ୍ଭ\n"
                     "ଏଡ଼ାଇ ଦିଆଯାଏ। କ୍ରମ ବାରର ଅଧିପତିଙ୍କଠାରୁ ଆରମ୍ଭ ହୁଏ, ତେଣୁ ପ୍ରତିଦିନ ବଦଳେ — ଏବଂ ପ୍ରତ୍ୟେକ ଭାଗର\n"
                     "ଦୈର୍ଘ୍ୟ {city}ର ପ୍ରକୃତ ଦିନର ଦୈର୍ଘ୍ୟକୁ ଅନୁସରଣ କରେ।</p>"),

        "km.title": "କୁଣ୍ଡଳୀ ମିଳନ — ଅଷ୍ଟକୂଟ ଗୁଣ ମିଳନ ({total} ଗୁଣ) ସମ୍ପୂର୍ଣ୍ଣ ତଥ୍ୟ | {brand}",
        "km.desc": ("କୁଣ୍ଡଳୀ ମିଳନ କିପରି ହୁଏ: ଅଷ୍ଟକୂଟ ଗୁଣ ମିଳନର 8ଟି କୂଟ, ମୋଟ {total} ଗୁଣ, ବିବାହ ପାଇଁ "
                    "କେତେ ଗୁଣ ଭଲ, ଏବଂ ମଙ୍ଗଳ ଦୋଷ କିପରି ଦେଖାଯାଏ। ମାଗଣାରେ ଅନଲାଇନ୍ "
                    "କୁଣ୍ଡଳୀ ମିଳନ।"),
        "km.crumb": "କୁଣ୍ଡଳୀ ମିଳନ",
        "km.intro": ("<h1>କୁଣ୍ଡଳୀ ମିଳନ: ଅଷ୍ଟକୂଟ ଗୁଣ ମିଳନର ସମ୍ପୂର୍ଣ୍ଣ ବ୍ୟାଖ୍ୟା</h1>\n"
                     "<p class=\"hi\">ଜାତକ ମିଳନ — ଅଷ୍ଟକୂଟ ଗୁଣ ମିଳନ ({total} ଗୁଣ)</p>\n"
                     "<p>କୁଣ୍ଡଳୀ ମିଳନ ହେଉଛି ବିବାହ ପୂର୍ବରୁ ବର ଓ କନ୍ୟାଙ୍କ ଅନୁକୂଳତା ଦେଖିବାର ପାରମ୍ପରିକ ବୈଦିକ ପଦ୍ଧତି।\n"
                     "ଉତ୍ତର ଭାରତରେ ସବୁଠାରୁ ପ୍ରଚଳିତ ପଦ୍ଧତି ହେଉଛି <strong>ଅଷ୍ଟକୂଟ ଗୁଣ ମିଳନ</strong>: ବର ଓ କନ୍ୟାଙ୍କ\n"
                     "କୁଣ୍ଡଳୀରେ ଆଠଟି ବିଷୟ (<em>କୂଟ</em>) ତୁଳନା କରି ମୋଟ <strong>{total} ଗୁଣ</strong> ମଧ୍ୟରୁ ନମ୍ବର\n"
                     "ଦିଆଯାଏ। ପ୍ରତ୍ୟେକଟି <strong>ଚନ୍ଦ୍ର</strong>ଙ୍କଠାରୁ ଦେଖାଯାଏ — ଜନ୍ମ ସମୟରେ ତାଙ୍କ ରାଶି ଓ ନକ୍ଷତ୍ର —\n"
                     "ତେଣୁ ସଠିକ୍ ଜନ୍ମ ତାରିଖ ଓ ଜନ୍ମ ସ୍ଥାନ ଆବଶ୍ୟକ, କିନ୍ତୁ ଜନ୍ମ ସମୟ ଉପରେ ଫଳ ପ୍ରାୟ ନିର୍ଭର କରେ ନାହିଁ।</p>"),
        "km.cta1": "ଏବେ ଦୁଇଟି କୁଣ୍ଡଳୀ ମିଳାନ୍ତୁ — ମାଗଣା",
        "km.naam": ('<p>ଜନ୍ମ ସମୟ ଜଣା ନାହିଁ? <a href="{href}">ନାମରୁ କୁଣ୍ଡଳୀ ମିଳନ</a> କରି ଦେଖନ୍ତୁ — '
                    "ନାମର ପ୍ରଥମ ଅକ୍ଷରରୁ ପାରମ୍ପରିକ ମିଳନ।</p>"),
        "km.kootas_h2": "<h2>ଆଠଟି କୂଟ ଓ ସେମାନଙ୍କ ଗୁଣ</h2>",
        "km.th": "<tr><th>କୂଟ</th><th>ଗୁଣ</th><th>କ'ଣ ଦେଖାଯାଏ</th></tr>",
        "km.row": "<tr><td><strong>{name}</strong></td><td>{pts}</td><td>{text}</td></tr>",
        "km.total": "ମୋଟ",
        "km.score_h2": "<h2>କେତେ ଗୁଣ ମିଳିଲେ ଭଲ?</h2>",
        "km.score_th": "<tr><th>ଗୁଣ</th><th>ପାରମ୍ପରିକ ଅର୍ଥ</th></tr>",
        "km.below": "{n}ରୁ କମ୍",
        "km.score_p": ("<p>18 ଗୁଣ ପାରମ୍ପରିକ ସର୍ବନିମ୍ନ ସୀମା। କେବଳ ମୋଟ ନମ୍ବରରୁ ପୂରା କଥା କୁହାଯାଏ ନାହିଁ: ଅଧିକ\n"
                       "ନମ୍ବର ସହିତ ପରିହାରହୀନ ନାଡ଼ୀ ବା ଭକୂଟ ଦୋଷ ଥିଲେ ସାବଧାନତାର ସହ ବିଚାର କରାଯାଏ, ଏବଂ କମ୍ ନମ୍ବରରେ\n"
                       "ମଧ୍ୟ ଭଲ ଗ୍ରହମୈତ୍ରୀ ଥିଲେ ଓ କୌଣସି ଦୋଷ ନଥିଲେ ମିଳନ ପ୍ରାୟତଃ ଚଳିବା ଭଳି ମାନାଯାଏ। ଏହି ସୀମାଗୁଡ଼ିକ\n"
                       "ଦୀର୍ଘ ପରମ୍ପରାର ଏକ ରୀତି, କୌଣସି ମାପ ନୁହେଁ — ଏଗୁଡ଼ିକ ମାର୍ଗଦର୍ଶନ, କୌଣସି ସମ୍ପର୍କ ଉପରେ ଶେଷ\n"
                       "ରାୟ ନୁହେଁ।</p>"),
        "km.ord1": "{n}",
        "km.ord2": "{n}",
        "km.ordn": "{n}",
        "km.or": " ବା ",
        "km.mangal": ("<h2>ମଙ୍ଗଳ ଦୋଷ (ମାଙ୍ଗଳିକ)</h2>\n"
                      "<p>ମଙ୍ଗଳ ଦୋଷ 36 ଗୁଣଠାରୁ ଅଲଗା ଭାବେ ଦେଖାଯାଏ। କୁଣ୍ଡଳୀ ମାଙ୍ଗଳିକ ହୁଏ ଯେତେବେଳେ ମଙ୍ଗଳ\n"
                      "<strong>ଲଗ୍ନ</strong>, <strong>ଚନ୍ଦ୍ର</strong> ବା <strong>ଶୁକ୍ର</strong>ଙ୍କଠାରୁ ଗଣି {houses} ନମ୍ବର\n"
                      "ଭାବରେ ଥାଆନ୍ତି। ଶାସ୍ତ୍ରରେ କେତେକ ରାଶି-ସ୍ଥିତିକୁ ଛାଡ଼ ଦିଆଯାଇଛି (ଯେପରି ପ୍ରଥମ ଭାବରେ ନିଜ ରାଶି\n"
                      "ମେଷରେ ମଙ୍ଗଳ), ଏବଂ ମଙ୍ଗଳଙ୍କ ଉପରେ ଗୁରୁଙ୍କ ଦୃଷ୍ଟି ଦୋଷକୁ କୋହଳ କରେ ବୋଲି ମାନାଯାଏ। ବର ଓ କନ୍ୟା\n"
                      "<strong>ଦୁହେଁ</strong> ମାଙ୍ଗଳିକ ହେଲେ ପରମ୍ପରା ଅନୁସାରେ ଦୋଷ ପରସ୍ପର କଟିଯାଏ — ସେଥିପାଇଁ ମାଙ୍ଗଳିକଙ୍କ\n"
                      "ବିବାହ ମାଙ୍ଗଳିକଙ୍କ ସହ କରାଯାଏ। ଲଗ୍ନ ଉପରେ ନିର୍ଭର କରୁଥିବାରୁ ମଙ୍ଗଳ ଦୋଷ ବିଚାର ପାଇଁ ବିଶ୍ୱସନୀୟ\n"
                      "ଜନ୍ମ ସମୟ ଆବଶ୍ୟକ।</p>"),
        "km.how": ("<h2>ଆମର କୁଣ୍ଡଳୀ ମିଳନ କିପରି କାମ କରେ</h2>\n"
                   "<p>ଦୁହିଁଙ୍କ ଜନ୍ମ ତାରିଖ, ସମୟ ଓ ସ୍ଥାନ ଦିଅନ୍ତୁ। ଦୁଇଟି କୁଣ୍ଡଳୀ ସୁଇସ୍ ଏଫେମେରିସ୍‌ରୁ ନିରୟନ (ଲାହିଡ଼ୀ\n"
                   "ଅୟନାଂଶ) ପଦ୍ଧତିରେ ପ୍ରସ୍ତୁତ ହୁଏ, ଏବଂ ପ୍ରତ୍ୟେକ କୂଟର ନମ୍ବର ଶାସ୍ତ୍ରୀୟ ସାରଣୀରୁ ଦିଆଯାଏ — ପ୍ରତ୍ୟେକ\n"
                   "ପରିହାରର ନାମ ସହିତ। ଆପଣ ପାଇବେ ପୂରା {total} ଗୁଣର ବିସ୍ତୃତ ହିସାବ ଏବଂ ଦୁହିଁଙ୍କ ମଙ୍ଗଳ ଦୋଷର\n"
                   "ସ୍ଥିତି — ମାଗଣାରେ, ସାଇନ୍-ଅପ୍ ବିନା।</p>"),
        "km.cta2": "କୁଣ୍ଡଳୀ ମିଳନ ଖୋଲନ୍ତୁ",
        "koota.varna": "ବର୍ଣ୍ଣ",
        "koota.vashya": "ବଶ୍ୟ",
        "koota.tara": "ତାରା",
        "koota.yoni": "ଯୋନି",
        "koota.graha_maitri": "ଗ୍ରହମୈତ୍ରୀ",
        "koota.gana": "ଗଣ",
        "koota.bhakoot": "ଭକୂଟ",
        "koota.nadi": "ନାଡ଼ୀ",
        "koota_about.varna": ("ଚନ୍ଦ୍ର ରାଶିର ବର୍ଣ୍ଣରୁ ଆଧ୍ୟାତ୍ମିକ ଓ କର୍ମଗତ ସ୍ୱଭାବ। ବରର ବର୍ଣ୍ଣ କନ୍ୟାର ବର୍ଣ୍ଣଠାରୁ "
                              "ତଳେ ନଥିଲେ ପୂର୍ଣ୍ଣ ନମ୍ବର।"),
        "koota_about.vashya": "ପାରସ୍ପରିକ ଆକର୍ଷଣ ଓ ପ୍ରଭାବ — କେଉଁ ରାଶି ଅନ୍ୟଟିକୁ “ବଶ” କରେ।",
        "koota_about.tara": ("ସ୍ୱାସ୍ଥ୍ୟ ଓ କଲ୍ୟାଣ, ଦୁଇ ଜନ୍ମ ନକ୍ଷତ୍ର ମଧ୍ୟରେ ଗଣନାରୁ; ତୃତୀୟ, ପଞ୍ଚମ ଓ ସପ୍ତମ "
                             "ତାରା ପ୍ରତିକୂଳ।"),
        "koota_about.yoni": ("ଶାରୀରିକ ଓ ଦାମ୍ପତ୍ୟ ଅନୁକୂଳତା; ପ୍ରତ୍ୟେକ ନକ୍ଷତ୍ରର ଏକ ପଶୁ ଯୋନି ଅଛି, ଏବଂ "
                             "ପରସ୍ପର ଚିରଶତ୍ରୁ ପଶୁଙ୍କ କ୍ଷେତ୍ରରେ ନମ୍ବର ଶୂନ।"),
        "koota_about.graha_maitri": "ଦୁଇ ଚନ୍ଦ୍ର ରାଶିର ଅଧିପତିଙ୍କ ମଧ୍ୟରେ ମିତ୍ରତା — ଦମ୍ପତିଙ୍କ ମାନସିକ ମେଳ।",
        "koota_about.gana": "ସ୍ୱଭାବ: ଦେବ (ଦୈବ), ମନୁଷ୍ୟ (ମାନବୀୟ) ବା ରାକ୍ଷସ (ଉଗ୍ର) ଗଣ।",
        "koota_about.bhakoot": ("ଦୁଇ ଚନ୍ଦ୍ର ରାଶିର ପାରସ୍ପରିକ ସ୍ଥିତି। 2/12, 5/9 ଓ 6/8 ସ୍ଥିତିରେ ଭକୂଟ ଦୋଷ "
                                "ହୁଏ, ଯାହା ଦୁଇ ରାଶିର ଅଧିପତି ଏକ ହେଲେ ବା ପରସ୍ପର ମିତ୍ର ହେଲେ କଟିଯାଏ।"),
        "koota_about.nadi": ("ସବୁଠାରୁ ଅଧିକ ନମ୍ବରର କୂଟ, ସ୍ୱାସ୍ଥ୍ୟ ଓ ସନ୍ତାନ ସହ ଜଡ଼ିତ। ଦୁହିଁଙ୍କ ଏକା ନାଡ଼ୀ ହେଲେ "
                             "ନାଡ଼ୀ ଦୋଷ; ରାଶି ଏକ କିନ୍ତୁ ନକ୍ଷତ୍ର ଭିନ୍ନ, ବା ନକ୍ଷତ୍ର ଏକ କିନ୍ତୁ ପାଦ ଭିନ୍ନ ହେଲେ ଏହାର "
                             "ଶାସ୍ତ୍ରୀୟ ପରିହାର ଅଛି।"),
        # the score bands of matching.SCORE_BANDS, in order
        "km.band0": "ଅନୁପଯୁକ୍ତ",
        "km.band1": "ଗ୍ରହଣୀୟ",
        "km.band2": "ଭଲ",
        "km.band3": "ଉତ୍ତମ",

        "fk.title": "ମାଗଣା ଜନ୍ମ କୁଣ୍ଡଳୀ — ଅନଲାଇନ୍ ଜାତକ ପ୍ରସ୍ତୁତ କରନ୍ତୁ | {brand}",
        "fk.desc": ("ମାଗଣାରେ ଅନଲାଇନ୍ ଜନ୍ମ କୁଣ୍ଡଳୀ ପ୍ରସ୍ତୁତ କରନ୍ତୁ: ଉତ୍ତର ବା ଦକ୍ଷିଣ ଭାରତୀୟ ଶୈଳୀରେ ଲଗ୍ନ "
                    "କୁଣ୍ଡଳୀ, ଗ୍ରହ ସ୍ଥିତି, ଚନ୍ଦ୍ର ନକ୍ଷତ୍ର, ବିଂଶୋତ୍ତରୀ ଦଶା, ନବାଂଶ ଓ ଅନ୍ୟ ବର୍ଗ କୁଣ୍ଡଳୀ, "
                    "ମାଙ୍ଗଳିକ, ସାଢ଼େସାତି ଓ କାଳସର୍ପ ଦୋଷ ବିଚାର — ସାଇନ୍-ଇନ୍ ବିନା।"),
        "fk.crumb": "ମାଗଣା କୁଣ୍ଡଳୀ",
        "fk.intro": ("<h1>ମାଗଣା ଜନ୍ମ କୁଣ୍ଡଳୀ ଅନଲାଇନ୍</h1>\n"
                     "<p class=\"hi\">ମାଗଣା ଜାତକ — ଲଗ୍ନ, ଗ୍ରହ, ଦଶା ଓ ଦୋଷ ବିଚାର</p>\n"
                     "<p><strong>ଜନ୍ମ କୁଣ୍ଡଳୀ</strong> (ଜାତକ) ହେଉଛି ଆପଣଙ୍କ ଜନ୍ମର ଠିକ୍ କ୍ଷଣ ଓ ସ୍ଥାନରେ ଆକାଶର\n"
                     "ମାନଚିତ୍ର: ସେତେବେଳେ ପୂର୍ବ ଦିଗନ୍ତରେ ବାରଟି ରାଶି ମଧ୍ୟରୁ କେଉଁଟି ଉଦୟ ହେଉଥିଲା (ଆପଣଙ୍କ\n"
                     "<strong>ଲଗ୍ନ</strong>), ଏବଂ ସୂର୍ଯ୍ୟ, ଚନ୍ଦ୍ର, ମଙ୍ଗଳ, ବୁଧ, ଗୁରୁ, ଶୁକ୍ର, ଶନି, ରାହୁ ଓ କେତୁ କେଉଁ\n"
                     "ରାଶିରେ ଏବଂ 27ଟି ନକ୍ଷତ୍ର ମଧ୍ୟରୁ କେଉଁଟିରେ ଥିଲେ। ବୈଦିକ ଜ୍ୟୋତିଷ ଅନ୍ୟ ସବୁକିଛି — ସ୍ୱଭାବ, ଜୀବନର\n"
                     "ବାରଟି କ୍ଷେତ୍ର, ଏବଂ ସର୍ବୋପରି ଦଶା ମାଧ୍ୟମରେ <em>ସମୟ</em> — ଏହି ଗୋଟିଏ କୁଣ୍ଡଳୀରୁ ବିଚାର କରେ।\n"
                     "ଆମ କୁଣ୍ଡଳୀ ମିନିଟ୍ ପର୍ଯ୍ୟନ୍ତ ସଠିକ୍ ଗଣନାରେ ପ୍ରସ୍ତୁତ ଏବଂ ମାଗଣା।</p>"),
        "fk.cta1": "ଏବେ ମୋର ମାଗଣା କୁଣ୍ଡଳୀ ପ୍ରସ୍ତୁତ କରନ୍ତୁ",
        "fk.need": ("<p>ଆପଣଙ୍କ ଜନ୍ମର <strong>ତାରିଖ</strong>, <strong>ସମୟ</strong> ଓ <strong>ସ୍ଥାନ</strong> ଆବଶ୍ୟକ।\n"
                    "ସାଇନ୍-ଇନ୍ ନାହିଁ, କାର୍ଡ ନାହିଁ।</p>"),
        "fk.includes": ("<h2>ମାଗଣା କୁଣ୍ଡଳୀରେ କ'ଣ କ'ଣ ମିଳିବ</h2>\n"
                        "<ul>\n"
                        "<li><strong>ଲଗ୍ନ କୁଣ୍ଡଳୀ (D1)</strong> ଉତ୍ତର ଭାରତୀୟ ବା ଦକ୍ଷିଣ ଭାରତୀୟ ଶୈଳୀରେ — ଗୋଟିଏ ଟ୍ୟାପରେ ବଦଳାନ୍ତୁ।</li>\n"
                        "<li><strong>ଗ୍ରହ ସ୍ଥିତି</strong>: ନଅଟି ଗ୍ରହ ଓ ଲଗ୍ନର ରାଶି, ଅଂଶ, ଭାବ, ବଳ (ଉଚ୍ଚ/ସ୍ୱକ୍ଷେତ୍ର/ନୀଚ) ଓ\n"
                        "ବକ୍ରୀ ସ୍ଥିତି, ସହିତ ଚନ୍ଦ୍ରଙ୍କ ନକ୍ଷତ୍ର ଓ ପାଦ।</li>\n"
                        "<li><strong>ବାରଟି ଭାବ</strong> ଏବଂ ପ୍ରତ୍ୟେକ ଭାବରେ ଥିବା ଗ୍ରହ।</li>\n"
                        "<li><strong>ବିଂଶୋତ୍ତରୀ ଦଶା</strong>: ବର୍ତ୍ତମାନର ମହାଦଶା ଓ ଅନ୍ତର୍ଦ୍ଦଶା ତାରିଖ ସହିତ, ସମୟରେଖାରେ।</li>\n"
                        "<li><strong>ବର୍ଗ କୁଣ୍ଡଳୀ</strong>: {vargas}।</li>\n"
                        "<li><strong>ଅଷ୍ଟକବର୍ଗ</strong>: ପ୍ରତ୍ୟେକ ଭାବର ସର୍ବାଷ୍ଟକବର୍ଗ ଓ ଭିନ୍ନାଷ୍ଟକବର୍ଗ ବିନ୍ଦୁ।</li>\n"
                        "<li><strong>ଜୈମିନି</strong> ଚର କାରକ (ଆତ୍ମକାରକରୁ ଦାରାକାରକ) ଓ ଆରୂଢ଼ ପଦ, ଏବଂ ଲଗ୍ନ, ଚନ୍ଦ୍ର ଓ\n"
                        "ସୂର୍ଯ୍ୟଙ୍କଠାରୁ ଏକାସାଙ୍ଗରେ ଦେଖାଯାଇଥିବା <strong>ସୁଦର୍ଶନ ଚକ୍ର</strong>।</li>\n"
                        "<li><strong>ଦୋଷ ବିଚାର</strong>: ମଙ୍ଗଳ ଦୋଷ (ମାଙ୍ଗଳିକ), ସାଢ଼େସାତି ଓ କାଳସର୍ପ।</li>\n"
                        "<li>ଆପଣଙ୍କ କୁଣ୍ଡଳୀ ଓ ବର୍ତ୍ତମାନ ଦଶା ଅନୁସାରେ <strong>ରତ୍ନ ଓ ପ୍ରତିକାର</strong> ପରାମର୍ଶ।</li>\n"
                        "<li>କୁଣ୍ଡଳୀର ଡ୍ୟାସବୋର୍ଡରେ ଆପଣଙ୍କ <strong>ଦୈନିକ ଫଳ</strong> ଓ ଆଜିର ପାଞ୍ଜି।</li>\n"
                        "</ul>\n"
                        "<p>ସବୁକିଛି <strong>ନିରୟନ ରାଶିଚକ୍ର ଓ ଲାହିଡ଼ୀ ଅୟନାଂଶରେ</strong>, ସମ୍ପୂର୍ଣ୍ଣ-ରାଶି ଭାବ ପଦ୍ଧତିରେ,\n"
                        "ସୁଇସ୍ ଏଫେମେରିସ୍‌ରୁ ପ୍ରସ୍ତୁତ ହୁଏ। ମାଗଣା ଆକାଉଣ୍ଟରେ ଆପଣ କୁଣ୍ଡଳୀ ସଞ୍ଚୟ କରିପାରିବେ, କୁଣ୍ଡଳୀର\n"
                        "PDF ଡାଉନଲୋଡ୍ କରିପାରିବେ, ଏବଂ ଏଆଇ ଜ୍ୟୋତିଷଙ୍କୁ ପ୍ରଥମ ପ୍ରଶ୍ନଗୁଡ଼ିକ ମାଗଣାରେ ପଚାରିପାରିବେ।</p>"),
        "fk.read": ("<h2>ନିଜ କୁଣ୍ଡଳୀ କିପରି ପଢ଼ିବେ</h2>\n"
                    "<h3>1. ଲଗ୍ନରୁ ଆରମ୍ଭ କରନ୍ତୁ</h3>\n"
                    "<p>ପ୍ରଥମ ଭାବ ହେଉଛି ଜନ୍ମ ସମୟରେ ଉଦୟ ହେଉଥିବା ରାଶି। ଉତ୍ତର ଭାରତୀୟ କୁଣ୍ଡଳୀରେ ଏହା ଉପର ମଝିର\n"
                    "ହୀରା ଆକୃତିର ଘର, ଏବଂ ପ୍ରତ୍ୟେକ ଘରେ ଲେଖାଥିବା ସଂଖ୍ୟା <em>ରାଶିର</em> (1 = ମେଷ … 12 = ମୀନ),\n"
                    "ଭାବର ନୁହେଁ। ଦକ୍ଷିଣ ଭାରତୀୟ କୁଣ୍ଡଳୀରେ ରାଶିଗୁଡ଼ିକ ସ୍ଥିର ଘରେ ରହେ ଏବଂ ଲଗ୍ନ ଅଲଗା ଭାବେ ଚିହ୍ନିତ\n"
                    "ହୁଏ। ଲଗ୍ନ ଓ ଲଗ୍ନେଶ ଶରୀର, ସ୍ୱଭାବ ଓ ଜୀବନର ସାମଗ୍ରିକ ଦିଗ ଦର୍ଶାନ୍ତି।</p>\n"
                    "<h3>2. ଆପଣଙ୍କ ଚନ୍ଦ୍ର ରାଶି ଓ ନକ୍ଷତ୍ର ଦେଖନ୍ତୁ</h3>\n"
                    "<p>ଭାରତୀୟ ପରମ୍ପରାରେ ଆପଣଙ୍କ <strong>ରାଶି</strong> ହେଉଛି ଚନ୍ଦ୍ରଙ୍କ ରାଶି, ସୂର୍ଯ୍ୟଙ୍କ ନୁହେଁ। ରାଶିଫଳ,\n"
                    "ସାଢ଼େସାତି ଓ କୁଣ୍ଡଳୀ ମିଳନ ଏହି ରାଶିରୁ ଦେଖାଯାଏ, ଏବଂ ଚନ୍ଦ୍ରଙ୍କ ନକ୍ଷତ୍ର ସ୍ଥିର କରେ ଆପଣଙ୍କ\n"
                    "ବିଂଶୋତ୍ତରୀ ଦଶା କେଉଁଠାରୁ ଆରମ୍ଭ ହେବ।</p>\n"
                    "<h3>3. ଭାବ ଅନୁସାରେ ଗ୍ରହ ପଢ଼ନ୍ତୁ</h3>\n"
                    "<p>ପ୍ରତ୍ୟେକ ଭାବ ଜୀବନର ଏକ କ୍ଷେତ୍ର: ପ୍ରଥମ ନିଜେ, ଦ୍ୱିତୀୟ ଧନ ଓ ପରିବାର, ତୃତୀୟ ସାହସ ଓ ଭାଇଭଉଣୀ,\n"
                    "ଚତୁର୍ଥ ଘର ଓ ମାଆ, ପଞ୍ଚମ ସନ୍ତାନ ଓ ବୁଦ୍ଧି, ଷଷ୍ଠ ସ୍ୱାସ୍ଥ୍ୟ ଓ ପ୍ରତିଦ୍ୱନ୍ଦ୍ୱୀ, ସପ୍ତମ ବିବାହ ଓ ଅଂଶୀଦାରି,\n"
                    "ଅଷ୍ଟମ ଆୟୁ ଓ ହଠାତ୍ ପରିବର୍ତ୍ତନ, ନବମ ଭାଗ୍ୟ ଓ ଧର୍ମ, ଦଶମ କର୍ମଜୀବନ, ଏକାଦଶ ଲାଭ, ଦ୍ୱାଦଶ ବ୍ୟୟ\n"
                    "ଓ ମୋକ୍ଷ। ଗ୍ରହ ଯେଉଁ ଭାବରେ ବସିଛନ୍ତି ଏବଂ ଯେଉଁ ଭାବଗୁଡ଼ିକର ଅଧିପତି, ସେଗୁଡ଼ିକୁ ପ୍ରଭାବିତ କରନ୍ତି;\n"
                    "ତାଙ୍କ ସ୍ଥିତି (ଉଚ୍ଚ, ସ୍ୱକ୍ଷେତ୍ର, ନୀଚ) କହେ ସେ କେତେ ଫଳ ଦେଇପାରିବେ।</p>\n"
                    "<h3>4. ଚାଲିଥିବା ଦଶା ଦେଖନ୍ତୁ</h3>\n"
                    "<p>ଦଶା କହେ <em>କେବେ</em>। ମହାଦଶାର ଅଧିପତି, ଏବଂ ତା' ଭିତରେ ଅନ୍ତର୍ଦ୍ଦଶାର ଅଧିପତି — ଏହି ଗ୍ରହଙ୍କ\n"
                    "ଭାବ ଏହି ସମୟରେ ସକ୍ରିୟ ହୁଏ — ସେଥିପାଇଁ ପ୍ରାୟ ଏକାପରି କୁଣ୍ଡଳୀ ଥିବା ଦୁଇ ଜଣଙ୍କ ବର୍ଷ ବହୁତ ଅଲଗା\n"
                    "ହୋଇପାରେ।</p>\n"
                    "<h3>5. ଦୋଷକୁ ପ୍ରସଙ୍ଗ ସହ ଦେଖନ୍ତୁ</h3>\n"
                    "<p>ଦୋଷ ହେଉଛି ବିଚାର କରିବାର ଏକ ସଙ୍କେତ, କୌଣସି ରାୟ ନୁହେଁ। ମଙ୍ଗଳ ଦୋଷର ଶାସ୍ତ୍ରୀୟ ପରିହାର ଅଛି;\n"
                    "ସାଢ଼େସାତି ଶନିଙ୍କ ସାଢ଼େ ସାତ ବର୍ଷର ଗୋଚର, ଯାହା ପ୍ରତ୍ୟେକଙ୍କ ଜୀବନରେ ଦୁଇ-ତିନି ଥର ଆସେ। ଦୋଷ\n"
                    "ରିପୋର୍ଟରେ ମିଳିଥିବା ପରିହାରଗୁଡ଼ିକର ନାମ ମଧ୍ୟ ଦିଆଯାଏ।</p>"),
        "fk.cta2": "ମୋର ଜନ୍ମ କୁଣ୍ଡଳୀ ପ୍ରସ୍ତୁତ କରନ୍ତୁ — ମାଗଣା",
        "fk.faq_h2": "<h2>ବାରମ୍ବାର ପଚରାଯାଉଥିବା ପ୍ରଶ୍ନ</h2>",
        "varga.D1": "ରାଶି", "varga.D3": "ଦ୍ରେକ୍କାଣ", "varga.D7": "ସପ୍ତାଂଶ",
        "varga.D9": "ନବାଂଶ", "varga.D10": "ଦଶମାଂଶ", "varga.D12": "ଦ୍ୱାଦଶାଂଶ",
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
    "kn": (
        ("ಜಾತಕ ನಿಜವಾಗಿಯೂ ಉಚಿತವೇ?",
         "ಹೌದು. ಜಾತಕ ರಚನೆ, ದಶೆಗಳು, ವರ್ಗ ಕುಂಡಲಿಗಳು ಮತ್ತು ದೋಷ ಪರಿಶೀಲನೆ ಸಂಪೂರ್ಣ ಉಚಿತ, ಮತ್ತು ಇವನ್ನು "
         "ನೋಡಲು ಸೈನ್ ಇನ್ ಬೇಕಿಲ್ಲ. ನಿಮ್ಮ ಉಚಿತ ಪ್ರಶ್ನೆಗಳ ನಂತರದ AI ಜ್ಯೋತಿಷಿಯ ಉತ್ತರಗಳು ಮತ್ತು ಜೀವನ "
         "ಗ್ರಂಥದಂತಹ ವಿಸ್ತೃತ ವರದಿಗಳಿಗೆ ಮಾತ್ರ ಶುಲ್ಕವಿದೆ."),
        ("ಜಾತಕಕ್ಕೆ ಯಾವ ವಿವರಗಳು ಬೇಕು?",
         "ನಿಮ್ಮ ಜನ್ಮ ದಿನಾಂಕ, ಜನ್ಮ ಸಮಯ ಮತ್ತು ಜನ್ಮ ಸ್ಥಳ. ಸ್ಥಳದಿಂದ ಅಕ್ಷಾಂಶ, ರೇಖಾಂಶ ಮತ್ತು ಸಮಯ ವಲಯ "
         "ನಿರ್ಧಾರವಾಗುತ್ತವೆ; ಇವು ಲಗ್ನ ಮತ್ತು ಭಾವಗಳ ಸ್ಥಾನವನ್ನು ನಿರ್ಧರಿಸುತ್ತವೆ."),
        ("ನಿಖರ ಜನ್ಮ ಸಮಯ ಗೊತ್ತಿಲ್ಲದಿದ್ದರೆ?",
         "ಜಾತಕವನ್ನು ಆಗಲೂ ಮಧ್ಯಾಹ್ನ 12:00ಕ್ಕೆ ರಚಿಸಲಾಗುತ್ತದೆ. ಚಂದ್ರ ರಾಶಿ ಮತ್ತು ನಕ್ಷತ್ರ ಸಾಮಾನ್ಯವಾಗಿ ಸರಿಯಾಗಿಯೇ "
         "ಇರುತ್ತವೆ (ಆ ದಿನ ಚಂದ್ರ ರಾಶಿ ಅಥವಾ ನಕ್ಷತ್ರ ಬದಲಿಸದಿದ್ದರೆ), ಆದ್ದರಿಂದ ಚಂದ್ರ ಆಧಾರಿತ ಫಲಗಳು, "
         "ಸಾಡೇಸಾತಿ ಮತ್ತು ಜಾತಕ ಹೊಂದಾಣಿಕೆ ಉಪಯುಕ್ತವಾಗಿರುತ್ತವೆ — ಆದರೆ ಲಗ್ನ, ಭಾವಗಳು ಮತ್ತು ಕುಜ ದೋಷಕ್ಕೆ "
         "ವಿಶ್ವಾಸಾರ್ಹ ಸಮಯ ಬೇಕು. ಜನನ ಪ್ರಮಾಣಪತ್ರ ಅಥವಾ ಆಸ್ಪತ್ರೆ ದಾಖಲೆಯ ಸಮಯ ಅತ್ಯುತ್ತಮ."),
        ("ಯಾವ ಪದ್ಧತಿ ಬಳಸುತ್ತೀರಿ — ಲಾಹಿರಿ, ಕೆಪಿ, ಸಾಯನ?",
         "ಪ್ರತಿ ಜಾತಕವೂ ನಿರಯನ ಪದ್ಧತಿಯಲ್ಲಿ ಲಾಹಿರಿ (ಚಿತ್ರಾಪಕ್ಷ) ಅಯನಾಂಶ, ಪೂರ್ಣ-ರಾಶಿ ಭಾವ "
         "ಮತ್ತು ವಿಂಶೋತ್ತರಿ ದಶೆಯೊಂದಿಗೆ ರಚನೆಯಾಗುತ್ತದೆ — ಇದು ಹೆಚ್ಚಿನ ಭಾರತೀಯ ಪಂಚಾಂಗಗಳು ಮತ್ತು ಜ್ಯೋತಿಷಿಗಳ "
         "ಸಂಪ್ರದಾಯ. ಗ್ರಹಗಳ ಸ್ಥಾನಗಳನ್ನು ಸ್ವಿಸ್ ಎಫೆಮೆರಿಸ್‌ನಿಂದ ಪಡೆಯಲಾಗುತ್ತದೆ."),
        ("ನನ್ನ ಜಾತಕವನ್ನು ಕನ್ನಡದಲ್ಲಿ ನೋಡಬಹುದೇ?",
         "ಹೌದು. ಆ್ಯಪ್ ಅನ್ನು ಕನ್ನಡಕ್ಕೆ ಬದಲಿಸಿ — ಆ್ಯಪ್‌ನ ಪರದೆಗಳು, ಜಾತಕ, ಗ್ರಹ ಮತ್ತು ರಾಶಿಗಳ ಹೆಸರುಗಳು "
         "ಹಾಗೂ ದಶೆಗಳು ಕನ್ನಡದಲ್ಲಿ ಕಾಣುತ್ತವೆ, ಮತ್ತು AI ಜ್ಯೋತಿಷಿ ಕನ್ನಡದಲ್ಲೇ ಉತ್ತರಿಸುತ್ತಾರೆ; ಜಾತಕದ PDF "
         "ಅನ್ನೂ ಕನ್ನಡದಲ್ಲಿ ಡೌನ್‌ಲೋಡ್ ಮಾಡಬಹುದು."),
        ("ಉತ್ತರ ಭಾರತೀಯ ಅಥವಾ ದಕ್ಷಿಣ ಭಾರತೀಯ ಜಾತಕ?",
         "ಎರಡೂ. ಒಂದೇ ಜಾತಕವನ್ನು ಉತ್ತರ ಭಾರತೀಯ ವಜ್ರಾಕಾರದ ಜಾತಕವಾಗಿ (ಭಾವಗಳು ಸ್ಥಿರ, ರಾಶಿಗಳಿಗೆ ಸಂಖ್ಯೆ) "
         "ಅಥವಾ ದಕ್ಷಿಣ ಭಾರತೀಯ ಚೌಕ ಜಾತಕವಾಗಿ (ರಾಶಿಗಳು ಸ್ಥಿರ) ಒಂದು ಟ್ಯಾಪ್‌ನಲ್ಲಿ ನೋಡಬಹುದು."),
        ("ಜನ್ಮ ಜಾತಕ ಮತ್ತು ರಾಶಿ ಭವಿಷ್ಯ ಒಂದೇನಾ?",
         "ಜನ್ಮ ಜಾತಕವೇ ಜನ್ಮ ಕುಂಡಲಿ — ನಿಮ್ಮ ಜನನದ ಕ್ಷಣದ ಆಕಾಶದ ಸ್ಥಿರ ನಕ್ಷೆ. ದೈನಂದಿನ ರಾಶಿ ಭವಿಷ್ಯ "
         "ಒಂದೇ ಚಂದ್ರ ರಾಶಿಯ ಎಲ್ಲರಿಗೂ ಇರುವ ಚಿಕ್ಕ ಸಾಮಾನ್ಯ ಭವಿಷ್ಯ. ನಿಮ್ಮ ಜಾತಕ ವೈಯಕ್ತಿಕ; ರಾಶಿ ಭವಿಷ್ಯ ಅಲ್ಲ."),
    ),
    "te": (
        ("జాతకం నిజంగా ఉచితమేనా?",
         "అవును. జాతక చక్రం వేయడం, దశలు, వర్గ చక్రాలు, దోష పరిశీలన — వీటికి ఏమీ చెల్లించనక్కర్లేదు, "
         "వీటిని చూడటానికి సైన్ ఇన్ కూడా అవసరం లేదు. మీ ఉచిత ప్రశ్నల తర్వాత AI జ్యోతిష్యుడి సమాధానాలు, "
         "జీవిత గ్రంథం వంటి విస్తృత నివేదికలకు మాత్రమే రుసుము ఉంటుంది."),
        ("ఏ వివరాలు కావాలి?",
         "మీ పుట్టిన తేదీ, పుట్టిన సమయం, పుట్టిన ప్రదేశం. ప్రదేశం నుండి అక్షాంశం, రేఖాంశం, కాలమండలం "
         "నిర్ణయమవుతాయి; వీటి ఆధారంగానే లగ్నం, భావాల స్థానాలు తేలుతాయి."),
        ("నా ఖచ్చితమైన పుట్టిన సమయం తెలియకపోతే?",
         "జాతకం అప్పుడు కూడా మధ్యాహ్నం 12:00 గంటలకు వేయబడుతుంది. చంద్ర రాశి, నక్షత్రం సాధారణంగా సరిగానే "
         "ఉంటాయి (ఆ రోజు చంద్రుడు రాశి లేదా నక్షత్రం మారితే తప్ప), కాబట్టి చంద్రుని ఆధారిత ఫలాలు, ఏలినాటి శని, "
         "జాతక పొంతన ఉపయోగపడతాయి — కానీ లగ్నం, భావాలు, కుజ దోషానికి నమ్మదగిన సమయం కావాలి. జనన "
         "ధృవీకరణ పత్రం లేదా ఆసుపత్రి రికార్డులోని సమయం అన్నింటికంటే మంచిది."),
        ("ఏ పద్ధతి వాడుతారు — లాహిరి, KP, సాయన?",
         "ప్రతి జాతకం నిరయన పద్ధతిలో లాహిరి (చిత్రాపక్ష) అయనాంశతో, సంపూర్ణ రాశి భావాలు, వింశోత్తరి దశతో "
         "వేయబడుతుంది — చాలా భారతీయ పంచాంగాలు, జ్యోతిష్యులు పాటించే సంప్రదాయం ఇదే. గ్రహ స్థితులు స్విస్ "
         "ఎఫెమెరిస్ నుండి తీసుకోబడతాయి."),
        ("నా జాతకాన్ని తెలుగులో చూడవచ్చా?",
         "అవును. యాప్‌ను తెలుగులోకి మార్చండి — యాప్ తెరలు, జాతక చక్రం, గ్రహాలు, రాశుల పేర్లు, దశలు "
         "తెలుగులో కనిపిస్తాయి, AI జ్యోతిష్కుడు తెలుగులోనే సమాధానం ఇస్తారు; జాతకం PDF ను కూడా "
         "తెలుగులో డౌన్‌లోడ్ చేసుకోవచ్చు."),
        ("ఉత్తర భారత చక్రమా, దక్షిణ భారత చక్రమా?",
         "రెండూ. ఒకే జాతకాన్ని ఉత్తర భారత వజ్రాకార చక్రంగా (భావాలు స్థిరం, రాశులకు సంఖ్యలు) లేదా దక్షిణ "
         "భారత చతురస్ర చక్రంగా (రాశులు స్థిరం) ఒక్క ట్యాప్‌తో చూడవచ్చు."),
        ("ఇది రాశి ఫలాలు లాంటిదేనా?",
         "జన్మ జాతకం అంటే జాతక చక్రమే — మీ పుట్టుక సమయంలో ఆకాశపు స్థిర పటం. దైనందిన రాశి ఫలాలు ఒకే చంద్ర "
         "రాశి ఉన్న అందరికీ వర్తించే చిన్న సాధారణ అంచనా. మీ జాతకం వ్యక్తిగతం; రాశి ఫలాలు కాదు."),
    ),
    # Tamil (DIVASTRO-123). The "in Hindi?" question is asked about Tamil:
    # names, panchang and AI answers are Tamil; some engine readings are English.
    "ta": (
        ("ஜாதகம் உண்மையிலேயே இலவசமா?",
         "ஆம். ஜாதகம் கணித்தல், தசைகள், வர்க்கச் சக்கரங்கள், தோஷச் சோதனை எதற்கும் கட்டணம் இல்லை; "
         "இவற்றைப் பார்க்க உள்நுழையவும் தேவையில்லை. உங்கள் இலவசக் கேள்விகளுக்குப் பிறகான AI "
         "ஜோதிடரின் பதில்களும், லைஃப் புக் போன்ற விரிவான கட்டண அறிக்கைகளும் மட்டுமே கட்டணம் உள்ளவை."),
        ("என்ன விவரங்கள் தேவை?",
         "உங்கள் பிறந்த தேதி, பிறந்த நேரம், பிறந்த இடம். இடம் அட்சரேகை, தீர்க்கரேகை, நேர மண்டலத்தைத் "
         "தீர்மானிக்கிறது; அவையே லக்னத்தையும் பாவ நிலைகளையும் முடிவு செய்கின்றன."),
        ("சரியான பிறந்த நேரம் தெரியாவிட்டால்?",
         "அப்போதும் ஜாதகம் மதியம் 12:00 மணிக்குக் கணிக்கப்படும். சந்திர ராசியும் நட்சத்திரமும் பொதுவாகச் "
         "சரியாகவே இருக்கும் (அன்று சந்திரன் ராசி அல்லது நட்சத்திரம் மாறியிருந்தால் தவிர), எனவே "
         "சந்திரனை அடிப்படையாகக் கொண்ட பலன்கள், ஏழரைச் சனி, ஜாதகப் பொருத்தம் பயனுள்ளதாகவே இருக்கும் — "
         "ஆனால் லக்னம், பாவங்கள், செவ்வாய் தோஷம் ஆகியவற்றுக்கு நம்பகமான நேரம் தேவை. பிறப்புச் "
         "சான்றிதழ் அல்லது மருத்துவமனைப் பதிவிலுள்ள நேரமே சிறந்தது."),
        ("எந்த முறையைப் பயன்படுத்துகிறீர்கள் — லாஹிரி, KP, சாயனம்?",
         "ஒவ்வொரு ஜாதகமும் நிராயன முறையில், லாஹிரி (சித்திரபக்ஷ) அயனாம்சம், முழு ராசி பாவங்கள், "
         "விம்சோத்தரி தசையுடன் கணிக்கப்படுகிறது — பெரும்பாலான இந்தியப் பஞ்சாங்கங்களும் ஜோதிடர்களும் "
         "பின்பற்றும் வழக்கம் இது. கிரக நிலைகள் ஸ்விஸ் எஃபெமெரிஸிலிருந்து எடுக்கப்படுகின்றன."),
        ("என் ஜாதகத்தைத் தமிழில் பார்க்கலாமா?",
         "ஆம். ஆப்பைத் தமிழுக்கு மாற்றினால் ஜாதகம், கிரகங்கள், ராசிகள், நட்சத்திரங்களின் பெயர்களும் "
         "பஞ்சாங்கமும் தமிழில் தெரியும்; AI ஜோதிடரின் பதில்களும் தமிழில் எழுதப்படும். சில விரிவான "
         "விளக்கங்கள் தற்போது ஆங்கிலத்தில் காட்டப்படலாம்."),
        ("வட இந்திய கட்டமா, தென்னிந்திய கட்டமா?",
         "இரண்டும். ஒரே ஜாதகத்தை வட இந்திய வைர வடிவக் கட்டமாகவும் (பாவங்கள் நிலையானவை, ராசிகளுக்கு "
         "எண்கள்) தென்னிந்தியச் சதுரக் கட்டமாகவும் (ராசிகள் நிலையானவை) ஒரே தொடுதலில் பார்க்கலாம்."),
        ("ஜாதகமும் ராசி பலனும் ஒன்றா?",
         "ஜனன ஜாதகம் என்பது பிறப்பு ஜாதகமே — நீங்கள் பிறந்தபோது வானத்தின் நிலையான வரைபடம். தினசரி "
         "ராசி பலன் என்பது ஒரே சந்திர ராசி உள்ள அனைவருக்குமான சுருக்கமான பொதுப் பலன். உங்கள் ஜாதகம் "
         "தனிப்பட்டது; ராசி பலன் அப்படியல்ல."),
    ),
    # Malayalam (DIVASTRO-123); the language question as in "ta".
    "ml": (
        ("ജാതകം ശരിക്കും സൗജന്യമാണോ?",
         "അതെ. ജാതകം ഗണിക്കൽ, ദശകൾ, വർഗചക്രങ്ങൾ, ദോഷ പരിശോധന എന്നിവയ്ക്കൊന്നും പണം വേണ്ട; ഇവ "
         "കാണാൻ സൈൻ ഇൻ ചെയ്യേണ്ടതുമില്ല. നിങ്ങളുടെ സൗജന്യ ചോദ്യങ്ങൾക്കു ശേഷമുള്ള AI ജ്യോതിഷിയുടെ "
         "ഉത്തരങ്ങൾക്കും ലൈഫ് ബുക്ക് പോലുള്ള വിശദമായ പണമടച്ചുള്ള റിപ്പോർട്ടുകൾക്കും മാത്രമാണ് പണം."),
        ("എന്തെല്ലാം വിവരങ്ങൾ വേണം?",
         "നിങ്ങളുടെ ജനനത്തീയതി, ജനനസമയം, ജനനസ്ഥലം. സ്ഥലത്തിൽ നിന്നാണ് അക്ഷാംശം, രേഖാംശം, "
         "സമയമേഖല എന്നിവ നിശ്ചയിക്കുന്നത്; അവയാണ് ലഗ്നവും ഭാവസ്ഥാനങ്ങളും തീരുമാനിക്കുന്നത്."),
        ("കൃത്യമായ ജനനസമയം അറിയില്ലെങ്കിലോ?",
         "അപ്പോഴും ജാതകം ഉച്ചയ്ക്ക് 12:00-ന് ഗണിക്കും. കൂറും നക്ഷത്രവും സാധാരണയായി ശരിയായിരിക്കും "
         "(അന്ന് ചന്ദ്രൻ രാശിയോ നക്ഷത്രമോ മാറിയിട്ടില്ലെങ്കിൽ), അതിനാൽ ചന്ദ്രനെ ആധാരമാക്കിയുള്ള "
         "ഫലങ്ങൾ, ഏഴരശ്ശനി, ജാതകപ്പൊരുത്തം എന്നിവ പ്രയോജനപ്പെടും — എന്നാൽ ലഗ്നം, ഭാവങ്ങൾ, "
         "ചൊവ്വാദോഷം എന്നിവയ്ക്ക് വിശ്വസനീയമായ സമയം വേണം. ജനന സർട്ടിഫിക്കറ്റിലോ ആശുപത്രി രേഖയിലോ "
         "ഉള്ള സമയമാണ് ഏറ്റവും നല്ലത്."),
        ("ഏത് രീതിയാണ് ഉപയോഗിക്കുന്നത് — ലാഹിരി, KP, സായനം?",
         "ഓരോ ജാതകവും നിരയന രീതിയിൽ, ലാഹിരി (ചിത്രാപക്ഷ) അയനാംശം, സമ്പൂർണ രാശി ഭാവങ്ങൾ, "
         "വിംശോത്തരി ദശ എന്നിവയോടെ ഗണിക്കുന്നു — മിക്ക ഇന്ത്യൻ പഞ്ചാംഗങ്ങളും ജ്യോതിഷികളും "
         "പിന്തുടരുന്ന രീതി. ഗ്രഹസ്ഥാനങ്ങൾ സ്വിസ് എഫെമെറിസിൽ നിന്നാണ് എടുക്കുന്നത്."),
        ("എന്റെ ജാതകം മലയാളത്തിൽ കാണാമോ?",
         "അതെ. ആപ്പ് മലയാളത്തിലേക്ക് മാറ്റിയാൽ ജാതകം, ഗ്രഹങ്ങൾ, രാശികൾ, നക്ഷത്രങ്ങൾ എന്നിവയുടെ "
         "പേരുകളും പഞ്ചാംഗവും മലയാളത്തിൽ കാണാം; AI ജ്യോതിഷിയുടെ ഉത്തരങ്ങളും മലയാളത്തിലായിരിക്കും. "
         "ചില വിശദ വിവരണങ്ങൾ ഇപ്പോൾ ഇംഗ്ലീഷിൽ കാണിച്ചേക്കാം."),
        ("ഉത്തരേന്ത്യൻ ചക്രമോ ദക്ഷിണേന്ത്യൻ ചക്രമോ?",
         "രണ്ടും. ഒരേ ജാതകം ഉത്തരേന്ത്യൻ വജ്രാകൃതി ചക്രമായും (ഭാവങ്ങൾ സ്ഥിരം, രാശികൾക്ക് സംഖ്യ) "
         "ദക്ഷിണേന്ത്യൻ ചതുര ചക്രമായും (രാശികൾ സ്ഥിരം) ഒറ്റ ടാപ്പിൽ കാണാം."),
        ("ജാതകവും രാശിഫലവും ഒന്നാണോ?",
         "ജനന ജാതകം ജനനസമയത്തെ ആകാശത്തിന്റെ സ്ഥിരമായ ഭൂപടമാണ്. ദിവസേനയുള്ള രാശിഫലം ഒരേ കൂറുള്ള "
         "എല്ലാവർക്കുമുള്ള ചെറിയ പൊതുഫലമാണ്. നിങ്ങളുടെ ജാതകം വ്യക്തിപരമാണ്; രാശിഫലം അങ്ങനെയല്ല."),
    ),
    "bn": (
        ("কোষ্ঠী কি সত্যিই বিনামূল্যে?",
         "হ্যাঁ। কুণ্ডলী তৈরি, দশা, বর্গ কুণ্ডলী ও দোষ বিচারে কোনো খরচ নেই, আর এগুলি দেখতে সাইন-ইন "
         "করতেও হয় না। শুধু বিনামূল্যের প্রশ্নগুলির পরে এআই জ্যোতিষীর উত্তর এবং লাইফ বুকের মতো "
         "বিস্তারিত সশুল্ক রিপোর্টের জন্য টাকা লাগে।"),
        ("কী কী তথ্য দরকার?",
         "আপনার জন্মতারিখ, জন্মসময় ও জন্মস্থান। স্থান থেকে অক্ষাংশ, দ্রাঘিমাংশ ও সময় অঞ্চল ঠিক হয়, "
         "যা লগ্ন ও ভাবগুলির অবস্থান নির্ধারণ করে।"),
        ("সঠিক জন্মসময় না জানলে কী হবে?",
         "তবুও কুণ্ডলী তৈরি হবে, দুপুর 12:00 ধরে। চন্দ্র রাশি ও নক্ষত্র সাধারণত ঠিকই থাকে (যদি না "
         "সেদিন চন্দ্র রাশি বা নক্ষত্র বদলায়), তাই চন্দ্র-ভিত্তিক ফল, সাড়েসাতি ও যোটক বিচার কাজে "
         "লাগে — কিন্তু লগ্ন, ভাব ও মঙ্গল দোষের জন্য নির্ভরযোগ্য সময় দরকার। জন্ম শংসাপত্র বা "
         "হাসপাতালের নথিতে লেখা সময়ই সবচেয়ে ভালো।"),
        ("কোন পদ্ধতি ব্যবহার করা হয় — লাহিড়ী, কেপি, না সায়ন?",
         "প্রতিটি কুণ্ডলী নিরয়ণ পদ্ধতিতে, লাহিড়ী (চিত্রাপক্ষ) অয়নাংশ, সম্পূর্ণ-রাশি ভাব ও বিংশোত্তরী "
         "দশা দিয়ে তৈরি — যা অধিকাংশ ভারতীয় পঞ্জিকা ও জ্যোতিষীর রীতি। গ্রহের অবস্থান নেওয়া হয় "
         "সুইস এফেমেরিস থেকে।"),
        ("কোষ্ঠী কি বাংলায় দেখা যায়?",
         "হ্যাঁ। অ্যাপের ভাষা বাংলা বেছে নিন — কুণ্ডলী, গ্রহ ও রাশির নাম এবং দশা বাংলায় দেখাবে। "
         "চাইলে ইংরেজি বা হিন্দিও বেছে নিতে পারেন।"),
        ("উত্তর ভারতীয় না দক্ষিণ ভারতীয় কুণ্ডলী?",
         "দুটোই। একই কুণ্ডলী উত্তর ভারতীয় রম্বস-ধাঁচে (ভাব স্থির, রাশির সংখ্যা লেখা) বা দক্ষিণ "
         "ভারতীয় চৌকো ধাঁচে (রাশি স্থির) এক ট্যাপে দেখা যায়।"),
        ("জন্মকুণ্ডলী আর রাশিফল কি একই?",
         "জন্মকুণ্ডলী হল খোদ জন্মছক — আপনার জন্মের মুহূর্তে আকাশের স্থির মানচিত্র। দৈনিক রাশিফল "
         "একই চন্দ্র রাশির সবার জন্য একটি ছোট সাধারণ পূর্বাভাস। কোষ্ঠী ব্যক্তিগত; রাশিফল নয়।"),
    ),
    "or": (
        ("କୁଣ୍ଡଳୀ ସତରେ ମାଗଣା କି?",
         "ହଁ। କୁଣ୍ଡଳୀ ପ୍ରସ୍ତୁତି, ଦଶା, ବର୍ଗ କୁଣ୍ଡଳୀ ଓ ଦୋଷ ବିଚାର ପାଇଁ କୌଣସି ଖର୍ଚ୍ଚ ନାହିଁ, ଏବଂ ଏଗୁଡ଼ିକ "
         "ଦେଖିବା ପାଇଁ ସାଇନ୍-ଇନ୍ ଆବଶ୍ୟକ ନାହିଁ। କେବଳ ମାଗଣା ପ୍ରଶ୍ନ ପରେ ଏଆଇ ଜ୍ୟୋତିଷଙ୍କ ଉତ୍ତର ଏବଂ ଲାଇଫ୍ "
         "ବୁକ୍ ଭଳି ବିସ୍ତୃତ ଦେୟଯୁକ୍ତ ରିପୋର୍ଟ ପାଇଁ ଟଙ୍କା ଲାଗେ।"),
        ("କେଉଁ ତଥ୍ୟ ଆବଶ୍ୟକ?",
         "ଆପଣଙ୍କ ଜନ୍ମ ତାରିଖ, ଜନ୍ମ ସମୟ ଓ ଜନ୍ମ ସ୍ଥାନ। ସ୍ଥାନରୁ ଅକ୍ଷାଂଶ, ଦ୍ରାଘିମା ଓ ସମୟ ମଣ୍ଡଳ ସ୍ଥିର ହୁଏ, "
         "ଯାହା ଲଗ୍ନ ଓ ଭାବଗୁଡ଼ିକର ସ୍ଥିତି ନିର୍ଦ୍ଧାରଣ କରେ।"),
        ("ସଠିକ୍ ଜନ୍ମ ସମୟ ଜଣା ନଥିଲେ କ'ଣ ହେବ?",
         "ତଥାପି କୁଣ୍ଡଳୀ ପ୍ରସ୍ତୁତ ହେବ, ମଧ୍ୟାହ୍ନ 12:00 ଧରି। ଚନ୍ଦ୍ର ରାଶି ଓ ନକ୍ଷତ୍ର ସାଧାରଣତଃ ଠିକ୍ ରହେ "
         "(ଯଦି ସେଦିନ ଚନ୍ଦ୍ର ରାଶି ବା ନକ୍ଷତ୍ର ବଦଳାଇ ନଥାଆନ୍ତି), ତେଣୁ ଚନ୍ଦ୍ର-ଆଧାରିତ ଫଳ, ସାଢ଼େସାତି ଓ "
         "କୁଣ୍ଡଳୀ ମିଳନ ଉପଯୋଗୀ ରହେ — କିନ୍ତୁ ଲଗ୍ନ, ଭାବ ଓ ମଙ୍ଗଳ ଦୋଷ ପାଇଁ ବିଶ୍ୱସନୀୟ ସମୟ ଆବଶ୍ୟକ। "
         "ଜନ୍ମ ପ୍ରମାଣପତ୍ର ବା ହସ୍ପିଟାଲ ରେକର୍ଡର ସମୟ ସବୁଠାରୁ ଭଲ।"),
        ("କେଉଁ ପଦ୍ଧତି ବ୍ୟବହାର ହୁଏ — ଲାହିଡ଼ୀ, କେପି, ନା ସାୟନ?",
         "ପ୍ରତ୍ୟେକ କୁଣ୍ଡଳୀ ନିରୟନ ପଦ୍ଧତିରେ, ଲାହିଡ଼ୀ (ଚିତ୍ରାପକ୍ଷ) ଅୟନାଂଶ, ସମ୍ପୂର୍ଣ୍ଣ-ରାଶି ଭାବ ଓ "
         "ବିଂଶୋତ୍ତରୀ ଦଶାରେ ପ୍ରସ୍ତୁତ — ଯାହା ଅଧିକାଂଶ ଭାରତୀୟ ପାଞ୍ଜି ଓ ଜ୍ୟୋତିଷଙ୍କ ପରମ୍ପରା। ଗ୍ରହ ସ୍ଥିତି "
         "ସୁଇସ୍ ଏଫେମେରିସ୍‌ରୁ ନିଆଯାଏ।"),
        ("କୁଣ୍ଡଳୀ ଓଡ଼ିଆରେ ଦେଖିହେବ କି?",
         "ହଁ। ଆପ୍‌ର ଭାଷା ଓଡ଼ିଆ ବାଛନ୍ତୁ — କୁଣ୍ଡଳୀ, ଗ୍ରହ ଓ ରାଶିର ନାମ ଏବଂ ଦଶା ଓଡ଼ିଆରେ ଦେଖାଯିବ। "
         "ଚାହିଁଲେ ଇଂରାଜୀ ବା ହିନ୍ଦୀ ମଧ୍ୟ ବାଛିପାରିବେ।"),
        ("ଉତ୍ତର ଭାରତୀୟ ନା ଦକ୍ଷିଣ ଭାରତୀୟ କୁଣ୍ଡଳୀ?",
         "ଦୁଇଟି। ଏକା କୁଣ୍ଡଳୀକୁ ଉତ୍ତର ଭାରତୀୟ ହୀରା ଶୈଳୀରେ (ଭାବ ସ୍ଥିର, ରାଶିର ସଂଖ୍ୟା ଲେଖା) ବା ଦକ୍ଷିଣ "
         "ଭାରତୀୟ ଚାରିକୋଣିଆ ଶୈଳୀରେ (ରାଶି ସ୍ଥିର) ଗୋଟିଏ ଟ୍ୟାପରେ ଦେଖିହେବ।"),
        ("ଜନ୍ମ କୁଣ୍ଡଳୀ ଓ ରାଶିଫଳ କ'ଣ ଏକା?",
         "ଜନ୍ମ କୁଣ୍ଡଳୀ ହେଉଛି ସ୍ୱୟଂ ଜନ୍ମ ଚକ୍ର — ଆପଣଙ୍କ ଜନ୍ମ କ୍ଷଣରେ ଆକାଶର ସ୍ଥିର ମାନଚିତ୍ର। ଦୈନିକ "
         "ରାଶିଫଳ ଏକା ଚନ୍ଦ୍ର ରାଶିର ସମସ୍ତଙ୍କ ପାଇଁ ଏକ ଛୋଟ ସାଧାରଣ ପୂର୍ବାନୁମାନ। କୁଣ୍ଡଳୀ ବ୍ୟକ୍ତିଗତ; "
         "ରାଶିଫଳ ନୁହେଁ।"),
    ),
}
