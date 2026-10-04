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
}
