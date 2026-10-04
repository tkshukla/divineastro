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
                   "<td>{quality}</td></tr>"),
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
                   "<td>{quality}</td></tr>"),
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
