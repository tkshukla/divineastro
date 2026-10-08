"""Marathi (मराठी, Devanagari) — the data a translator fills (DIVASTRO-143).

This file is the ONLY place the mr text of the shared tables is edited; app/lang_data merges it
into them at import time, as if it were written in app/seo_text.py and friends.

  python -m app.lang_data check mr      what is left, per table (exit 0 = complete)
  python -m app.lang_data skeleton mr --force   regenerate (DISCARDS your edits)

Rules: every key below stays; a value "" means "not translated yet" (English shows, the
checker complains). Keep every {placeholder} the comment lists under `keep:`; the word order
is yours. HTML values keep their tags (write &amp; for &). Astrology names (tithi, nakshatra,
rashi, graha ...) are not here: they are in app/astro/names_mr.py. Digits are ASCII, as in
the other languages. Full instructions: docs/lang-agent-brief.md.

Set READY when a whole page module is complete, and only then — an unfinished module in READY
fails `check` and CI. A module that is not READY renders the English body, noindex.
"""

from __future__ import annotations

# Page modules that are complete for this language (the table groups below):
#   "seo" "rashifal" "vrat" "nakshatra" "muhurat" "recurring" "hub" "app"
READY = frozenset({"seo", "rashifal", "vrat", "nakshatra", "muhurat", "recurring", "hub", "app"})

# Latin-script words the mr text may keep besides the defaults (WhatsApp, UPI, PDF ...).
ALLOW_LATIN = frozenset()

# static/i18n/mr.json keys whose value is deliberately the English word (brand names, "OK").
KEEP_ENGLISH = frozenset()

# Namakshar syllables are Devanagari in the engine; this maps a letter to this script:
# (Unicode block start, {Devanagari letter: this script's letter where the offset is wrong}).
# Already set — `check` verifies all 108 syllables come out in the mr script.
AKSHAR = (0x0900, {})


# ----------------------------------------------------------------------------
# seo       /panchang /rahu-kaal /choghadiya /kundali-milan /free-kundali + shared chrome, cities
# ----------------------------------------------------------------------------

# app/seo_text.py TEXT["mr"] — page text of /panchang /rahu-kaal /choghadiya /kundali-milan /free-kundali  [134]
SEO_TEXT = {
    # EN: Panchang
    "tool.panchang": "पंचांग",
    # EN: Rahu Kaal
    "tool.rahu-kaal": "राहुकाळ",
    # EN: Choghadiya
    "tool.choghadiya": "चौघडिया",
    # EN: {vara}, {date} · {place} · IST
    # keep: {date} {place} {vara}
    "when": "{vara}, {date} · {place} · भारतीय वेळ",
    # EN: {name} until {time}
    # keep: {name} {time}
    "limb.until": "{name} {time} पर्यंत",
    # EN: then {name}
    # keep: {name}
    "limb.then": "नंतर {name}",
    # EN: pada
    "limb.pada": "चरण",
    # EN: {paksha} paksha
    # keep: {paksha}
    "paksha.full": "{paksha} पक्ष",
    # EN: {tool} in other cities
    # keep: {tool}
    "cities.heading": "इतर शहरांतील {tool}",
    # EN: More free tools
    "links.heading": "आणखी मोफत साधने",
    # EN: {tool} in {city}
    # keep: {city} {tool}
    "links.tool_in_city": "{city} मधील {tool}",
    # EN: Kundali Milan (36 guna)
    "links.milan": "कुंडली मिलन (36 गुण)",
    # EN: Free Janam Kundali
    "links.kundali": "मोफत जन्मकुंडली",
    # EN: Muhurat Finder
    "links.muhurat": "मुहूर्त शोधक",
    # EN: Today's Rashifal
    "links.rashifal": "आजचे राशिभविष्य",
    # EN: Today's Vrat & Festivals in {city}
    # keep: {city}
    "links.vrat": "{city} मधील आजची व्रते आणि सण",
    # EN: City not found — {brand}
    # keep: {brand}
    "nf.title": "शहर सापडले नाही — {brand}",
    # EN: {tool} city not found.
    # keep: {tool}
    "nf.desc": "{tool} साठी हे शहर सापडले नाही.",
    # EN: <h1>{tool}: city not found</h1><p>We don't have a page for “{slug}” yet. Pick a city
    #     below, or <a href="{app}">open the {tool} tool</a> to use any place in the world.</p>
    # keep: {app} {slug} {tool}
    "nf.body": "<h1>{tool}: शहर सापडले नाही</h1><p>“{slug}” साठी आमच्याकडे अद्याप पान नाही. खालील यादीतून एखादे शहर निवडा, किंवा जगातील कोणतेही ठिकाण वापरण्यासाठी <a href=\"{app}\">{tool} साधन उघडा</a>.</p>",
    # EN: Today's Panchang in {city}, {date} — Tithi, Nakshatra, Rahu Kaal | {brand}
    # keep: {brand} {city} {date}
    "p.title": "{city} मधील आजचे पंचांग, {date} — तिथी, नक्षत्र, राहुकाळ | {brand}",
    # EN: Aaj ka Panchang for {city} on {vara}, {date}: {tithi} tithi ({paksha} paksha), {nakshatra}
    #     nakshatra, sunrise {sunrise}, Rahu Kaal {rahu}. Computed with Swiss Ephemeris.
    # keep: {city} {date} {nakshatra} {rahu} {sunrise} {tithi} {vara}
    # may also use: {paksha_full} {paksha}
    "p.desc": "{city} साठी {vara}, {date} चे पंचांग: {paksha} पक्ष, {tithi} तिथी, {nakshatra} नक्षत्र, सूर्योदय {sunrise}, राहुकाळ {rahu}. स्विस एफेमेरिसने केलेली अचूक गणना.",
    # EN: <h1>Today's Panchang in {city}</h1>
    # keep: {city}
    "p.h1": "<h1>{city} मधील आजचे पंचांग</h1>",
    # EN: <p class="hi" lang="hi">आज का पंचांग — {city_hi}</p>
    # keep: {city}
    "p.sub": "<p class=\"hi\">तिथी, नक्षत्र, योग, करण आणि राहुकाळ — {city}</p>",
    # EN: <div class="box"><p>Today in {city} is <strong>{paksha} {tithi}</strong> with the Moon in
    #     <strong>{nakshatra}</strong> nakshatra. Rahu Kaal runs <strong>{rahu}</strong> — avoid
    #     starting anything new in that window.</p></div>
    # keep: {city} {nakshatra} {rahu} {tithi}
    # may also use: {paksha_full} {paksha}
    "p.box": "<div class=\"box\"><p>आज {city} मध्ये <strong>{paksha} {tithi}</strong> आहे आणि चंद्र <strong>{nakshatra}</strong> नक्षत्रात आहे. राहुकाळ <strong>{rahu}</strong> या वेळेत आहे — या वेळेत कोणतेही नवीन काम सुरू करू नका.</p></div>",
    # EN: Vaar (weekday)
    "p.r_vara": "वार",
    # EN: Tithi
    "p.r_tithi": "तिथी",
    # EN: Paksha
    "p.r_paksha": "पक्ष",
    # EN: Nakshatra
    "p.r_nakshatra": "नक्षत्र",
    # EN: Yoga
    "p.r_yoga": "योग",
    # EN: Karana
    "p.r_karana": "करण",
    # EN: Sunrise
    "p.r_sunrise": "सूर्योदय",
    # EN: Sunset
    "p.r_sunset": "सूर्यास्त",
    # EN: Moonrise
    "p.r_moonrise": "चंद्रोदय",
    # EN: Moonset
    "p.r_moonset": "चंद्रास्त",
    # EN: Moon sign
    "p.r_moon_sign": "चंद्र रास",
    # EN: Rahu Kaal
    "p.r_rahu": "राहुकाळ",
    # EN: Yamaganda
    "p.r_yama": "यमगंड",
    # EN: Gulika Kaal
    "p.r_gulika": "गुलिक काळ",
    # EN: Abhijit Muhurat
    "p.r_abhijit": "अभिजित मुहूर्त",
    # EN: {vara_en} — {weekday} <span lang="hi">({vara_hi})</span>
    # keep: {vara}
    "p.v_vara": "{vara}",
    # EN: {paksha_en} <span lang="hi">({paksha_hi_full})</span>
    # keep: {paksha_full}
    "p.v_paksha": "{paksha_full}",
    # EN: No moonrise this day
    "p.no_moonrise": "या दिवशी चंद्रोदय नाही",
    # EN: No moonset this day
    "p.no_moonset": "या दिवशी चंद्रास्त नाही",
    # EN: Not observed on Wednesday (Budhavara)
    "p.no_abhijit": "बुधवारी पाळला जात नाही",
    # EN: <p>Times are for {place} ({lat}°N, {lon}°E) in Indian Standard Time. The panchang day runs
    #     from sunrise to the next sunrise, so a tithi or nakshatra may end after midnight. Sunrise
    #     is the visible upper limb with refraction, as printed in Indian almanacs; nakshatra and
    #     yoga use the Lahiri ayanamsa.</p>
    # keep: {lat} {lon}
    # may also use: {city} {place}
    "p.note": "<p>वेळा {place} ({lat}°उ, {lon}°पू) साठी भारतीय प्रमाणवेळेनुसार आहेत. पंचांगाचा दिवस एका सूर्योदयापासून पुढच्या सूर्योदयापर्यंत असतो, त्यामुळे एखादी तिथी किंवा नक्षत्र मध्यरात्रीनंतरही संपू शकते. सूर्योदय म्हणजे भारतीय पंचांगांप्रमाणे सूर्याची वरची कडा दिसू लागण्याची वेळ (वातावरणीय अपवर्तनासह); नक्षत्र आणि योग लाहिरी अयनांशानुसार काढले आहेत.</p>",
    # EN: Open the full Panchang — any city, any date
    "p.cta": "संपूर्ण पंचांग उघडा — कोणतेही शहर, कोणतीही तारीख",
    # EN: <h2>The five limbs of the Panchang</h2> <p><strong>Tithi</strong> is the lunar day — each
    #     12° the Moon gains on the Sun. <strong>Nakshatra</strong> is the Moon's lunar mansion, one
    #     of 27. <strong>Yoga</strong> comes from the combined longitudes of Sun and Moon, and
    #     <strong>Karana</strong> is half a tithi. <strong>Vaar</strong> is the weekday, reckoned
    #     from sunrise. Together they are the <span lang="hi">पंचांग</span> (“five limbs”) consulted
    #     before any auspicious work.</p>
    "p.limbs": "<h2>पंचांगाची पाच अंगे</h2> <p><strong>तिथी</strong> म्हणजे चांद्र दिवस — चंद्र सूर्यापेक्षा प्रत्येकी 12° पुढे सरकला की एक तिथी होते. <strong>नक्षत्र</strong> म्हणजे चंद्र ज्या 27 नक्षत्रांपैकी एकात असतो ते. <strong>योग</strong> सूर्य आणि चंद्र यांच्या रेखांशांच्या बेरजेवरून ठरतो, आणि <strong>करण</strong> म्हणजे अर्धी तिथी. <strong>वार</strong> म्हणजे आठवड्याचा दिवस, जो सूर्योदयापासून मोजला जातो. हे पाचही मिळून पंचांग (“पाच अंगे”) बनते, जे कोणतेही शुभ कार्य करण्यापूर्वी पाहिले जाते.</p>",
    # EN: Rahu Kaal Today in {city} — {rahu}, {date} | {brand}
    # keep: {brand} {city} {rahu}
    # may also use: {date}
    "rk.title": "{city} मधील आजचा राहुकाळ — {rahu}, {date} | {brand}",
    # EN: Rahu Kaal today in {city} ({vara}, {date}) is {rahu}. Also Yamaganda {yama} and Gulika
    #     {gulika}, with this week's timings and what Rahu Kaal means.
    # keep: {city} {date} {gulika} {rahu} {vara} {yama}
    "rk.desc": "{city} मध्ये आज ({vara}, {date}) राहुकाळ {rahu} आहे. यमगंड {yama} आणि गुलिक काळ {gulika}, तसेच या आठवड्याच्या वेळा आणि राहुकाळ म्हणजे काय ते पाहा.",
    # EN: <h1>Rahu Kaal Today in {city}</h1>
    # keep: {city}
    "rk.h1": "<h1>{city} मधील आजचा राहुकाळ</h1>",
    # EN: <p class="hi" lang="hi">आज का राहु काल — {city_hi}</p>
    # keep: {city}
    "rk.sub": "<p class=\"hi\">आजचा राहुकाळ, यमगंड आणि गुलिक काळ केव्हा — {city}</p>",
    # EN: Rahu Kaal <span lang="hi">(राहु काल)</span>
    "rk.r_rahu": "राहुकाळ",
    # EN: Yamaganda <span lang="hi">(यमगण्ड)</span>
    "rk.r_yama": "यमगंड",
    # EN: Gulika Kaal <span lang="hi">(गुलिक काल)</span>
    "rk.r_gulika": "गुलिक काळ",
    # EN: Abhijit Muhurat
    "rk.r_abhijit": "अभिजित मुहूर्त",
    # EN: Sunrise / Sunset
    "rk.r_sun": "सूर्योदय / सूर्यास्त",
    # EN: Not observed on Wednesday
    "rk.no_abhijit": "बुधवारी पाळला जात नाही",
    # EN: Check Rahu Kaal for any city or date
    "rk.cta": "कोणत्याही शहराचा किंवा तारखेचा राहुकाळ पाहा",
    # EN: <h2>What is Rahu Kaal?</h2> <p>Rahu Kaal (<span lang="hi">राहु काल</span>) is a period of
    #     roughly an hour and a half each day that is traditionally held to be ruled by Rahu, the
    #     north lunar node. Daylight — sunrise to sunset — is divided into eight equal parts, and
    #     one of them belongs to Rahu. Which part depends on the weekday: the 8th on Sunday, 2nd on
    #     Monday, 7th on Tuesday, 5th on Wednesday, 6th on Thursday, 4th on Friday and 3rd on
    #     Saturday.</p> <p>Because it follows the real sunrise and sunset, Rahu Kaal is different in
    #     every city and shifts through the year — which is why a fixed “Monday 7:30–9:00” chart is
    #     only an approximation. By custom, people avoid beginning new ventures, signing agreements,
    #     starting journeys or making major purchases during Rahu Kaal; work already under way can
    #     continue. Yamaganda and Gulika Kaal are two further eighths of the day treated with
    #     similar caution.</p>
    "rk.about": "<h2>राहुकाळ म्हणजे काय?</h2> <p>राहुकाळ हा दररोजचा साधारण दीड तासाचा कालावधी असतो, जो परंपरेनुसार उत्तर चंद्रपात राहूच्या अधिपत्याखाली मानला जातो. सूर्योदयापासून सूर्यास्तापर्यंतचा दिवसाचा काळ आठ समान भागांत विभागला जातो, आणि त्यापैकी एक भाग राहूचा असतो. कोणता भाग ते वारावर अवलंबून असते: रविवारी 8वा, सोमवारी 2रा, मंगळवारी 7वा, बुधवारी 5वा, गुरुवारी 6वा, शुक्रवारी 4था आणि शनिवारी 3रा.</p> <p>तो प्रत्यक्ष सूर्योदय आणि सूर्यास्ताप्रमाणे ठरत असल्यामुळे राहुकाळ प्रत्येक शहरात वेगळा असतो आणि वर्षभर बदलत राहतो — म्हणूनच “सोमवार सकाळी 7:30–9:00” असा ठरावीक तक्ता केवळ अंदाजे असतो. प्रथेनुसार राहुकाळात नवीन उपक्रम सुरू करणे, करारांवर सही करणे, प्रवास सुरू करणे किंवा मोठी खरेदी करणे टाळले जाते; आधीच सुरू असलेले काम पुढे चालू ठेवता येते. यमगंड आणि गुलिक काळ हे दिवसाचे आणखी दोन अष्टमांश आहेत, ज्यांच्याबाबतही अशीच काळजी घेतली जाते.</p>",
    # EN: <h2>Rahu Kaal in {city} this week</h2>
    # keep: {city}
    "rk.week_h2": "<h2>या आठवड्यात {city} मधील राहुकाळ</h2>",
    # EN: Day
    "rk.th_day": "वार",
    # EN: Rahu Kaal
    "rk.th_rahu": "राहुकाळ",
    # EN: Yamaganda
    "rk.th_yama": "यमगंड",
    # EN: Gulika
    "rk.th_gulika": "गुलिक",
    # EN: Choghadiya Today in {city}, {date} — Day & Night Timings | {brand}
    # keep: {brand} {city} {date}
    "ch.title": "{city} मधील आजचा चौघडिया, {date} — दिवस आणि रात्रीच्या वेळा | {brand}",
    # EN: Today's choghadiya for {city} ({vara}, {date}): all 16 day and night muhurtas — Amrit,
    #     Shubh, Labh, Char, Rog, Kaal, Udveg — with exact start and end times from sunrise
    #     {sunrise}.
    # keep: {city} {date} {sunrise} {vara}
    "ch.desc": "{city} साठी आजचा चौघडिया ({vara}, {date}): दिवस आणि रात्रीचे सर्व 16 मुहूर्त — अमृत, शुभ, लाभ, चर, रोग, काळ, उद्वेग — सूर्योदय {sunrise} पासून अचूक सुरुवात आणि शेवटाच्या वेळांसह.",
    # EN: <h1>Choghadiya Today in {city}</h1>
    # keep: {city}
    "ch.h1": "<h1>{city} मधील आजचा चौघडिया</h1>",
    # EN: <p class="hi" lang="hi">आज का चौघड़िया — {city_hi}</p>
    # keep: {city}
    "ch.sub": "<p class=\"hi\">दिवस आणि रात्रीच्या शुभ-अशुभ वेळा — {city}</p>",
    # EN: {name} from {time}
    # keep: {name} {time}
    "ch.first_good": "{time} पासून {name}",
    # EN: none
    "ch.none": "नाही",
    # EN: <div class="box"><p>Sunrise <strong>{sunrise}</strong>, sunset <strong>{sunset}</strong>.
    #     First auspicious daytime choghadiya: <strong>{first_good}</strong>.</p></div>
    # keep: {first_good} {sunrise} {sunset}
    "ch.box": "<div class=\"box\"><p>सूर्योदय <strong>{sunrise}</strong>, सूर्यास्त <strong>{sunset}</strong>. दिवसाचा पहिला शुभ चौघडिया: <strong>{first_good}</strong>.</p></div>",
    # EN: <h2>Day Choghadiya <span lang="hi">(दिन का चौघड़िया)</span></h2>
    "ch.day_h2": "<h2>दिवसाचा चौघडिया</h2>",
    # EN: <h2>Night Choghadiya <span lang="hi">(रात का चौघड़िया)</span></h2>
    "ch.night_h2": "<h2>रात्रीचा चौघडिया</h2>",
    # EN: <tr><th>Time</th><th>Choghadiya</th><th>Nature</th></tr>
    "ch.th": "<tr><th>वेळ</th><th>चौघडिया</th><th>स्वरूप</th></tr>",
    # EN: <tr><td>{when}</td><td class="{cls}"><strong>{name}</strong> <span lang="hi">({name_hi})</
    #     span><small>{ruler}</small></td><td>{quality}<small>{desc}</small></td></tr>
    # keep: {cls} {desc} {name} {quality} {ruler} {when}
    "ch.row": "<tr><td>{when}</td><td class=\"{cls}\"><strong>{name}</strong><small>स्वामी: {ruler}</small></td><td>{quality}<small>{desc}</small></td></tr>",
    # EN: Open the live Choghadiya clock
    "ch.cta": "थेट चौघडिया घड्याळ उघडा",
    # EN: <h2>How choghadiya works</h2> <p>The day from sunrise to sunset, and the night from sunset
    #     to the next sunrise, are each divided into eight equal parts called choghadiya (<span
    #     lang="hi">चौघड़िया</span>, “four ghadis”). Each is ruled by a planet and named for its
    #     nature: <strong>Amrit</strong>, <strong>Shubh</strong> and <strong>Labh</strong> are
    #     auspicious, <strong>Char</strong> is neutral and good for travel, while
    #     <strong>Rog</strong>, <strong>Kaal</strong> and <strong>Udveg</strong> are avoided for new
    #     beginnings. The order starts from the weekday's ruler, so it changes every day — and the
    #     length of each slot follows the real day length in {city}.</p>
    # keep: {city}
    "ch.about": "<h2>चौघडिया कसा पाहतात</h2> <p>सूर्योदयापासून सूर्यास्तापर्यंतचा दिवस आणि सूर्यास्तापासून पुढच्या सूर्योदयापर्यंतची रात्र, हे प्रत्येकी आठ समान भागांत विभागले जातात; या भागांना चौघडिया (“चार घटिका”) म्हणतात. प्रत्येक चौघडियाचा एक ग्रह स्वामी असतो आणि त्याच्या स्वरूपावरून त्याचे नाव ठरते: <strong>अमृत</strong>, <strong>शुभ</strong> आणि <strong>लाभ</strong> हे शुभ मानले जातात, <strong>चर</strong> हा सामान्य असून प्रवासासाठी चांगला असतो, तर <strong>रोग</strong>, <strong>काळ</strong> आणि <strong>उद्वेग</strong> हे नवीन कामाच्या सुरुवातीसाठी टाळले जातात. क्रम त्या वाराच्या स्वामीपासून सुरू होतो, म्हणून तो रोज बदलतो — आणि प्रत्येक चौघडियाचा कालावधी {city} मधील दिवसाच्या खऱ्या लांबीनुसार ठरतो.</p>",
    # EN: Kundali Milan — Ashtakoot Guna Milan ({total} Gun) Explained | {brand}
    # keep: {brand} {total}
    "km.title": "कुंडली मिलन — अष्टकूट गुण मिलन ({total} गुण) सोप्या भाषेत | {brand}",
    # EN: How Kundali Milan works: the 8 kootas of Ashtakoot Guna Milan, {total} points, what score
    #     is good for marriage, and how Mangal Dosha is checked. Free online matching in English and
    #     Hindi.
    # keep: {total}
    "km.desc": "कुंडली मिलन कसे चालते: अष्टकूट गुण मिलनाचे 8 कूट, {total} गुण, विवाहासाठी किती गुण चांगले आणि मंगळ दोष कसा तपासतात. इंग्रजी आणि हिंदीत मोफत ऑनलाइन जुळवणी.",
    # EN: Kundali Milan
    "km.crumb": "कुंडली मिलन",
    # EN: <h1>Kundali Milan: Ashtakoot Guna Milan explained</h1> <p class="hi" lang="hi">कुंडली
    #     मिलान — अष्टकूट गुण मिलान ({total} गुण)</p> <p>Kundali Milan (<span lang="hi">कुंडली
    #     मिलान</span>) is the traditional Vedic way of checking marriage compatibility. The most
    #     widely used method in North India is <strong>Ashtakoot Guna Milan</strong>: eight factors
    #     (<em>kootas</em>) are compared between the bride's and groom's charts and scored out of
    #     <strong>{total} points (gunas)</strong>. Every one of them is read from the
    #     <strong>Moon</strong> — its sign (rashi) and its nakshatra at birth — which is why the
    #     score needs an accurate birth date and place, but barely depends on the birth time.</p>
    # keep: {total}
    "km.intro": "<h1>कुंडली मिलन: अष्टकूट गुण मिलन सोप्या भाषेत</h1> <p class=\"hi\">कुंडली मिलन — अष्टकूट गुण मिलन ({total} गुण)</p> <p>कुंडली मिलन म्हणजे विवाहापूर्वी वधू-वरांची सुसंगतता तपासण्याची पारंपरिक वैदिक पद्धत. उत्तर भारतात सर्वाधिक वापरली जाणारी पद्धत म्हणजे <strong>अष्टकूट गुण मिलन</strong>: वधू आणि वराच्या कुंडलीतील आठ घटकांची (<em>कूट</em>) तुलना केली जाते आणि एकूण <strong>{total} गुणांपैकी</strong> गुण दिले जातात. हे सर्व घटक <strong>चंद्रावरून</strong> पाहिले जातात — जन्माच्या वेळची त्याची रास आणि नक्षत्र — म्हणूनच गुणांसाठी अचूक जन्मतारीख आणि जन्मस्थान लागते, पण जन्मवेळेवर ते फारसे अवलंबून नसते.</p>",
    # EN: Match two kundalis now — free
    "km.cta1": "आत्ताच दोन कुंडल्या जुळवा — मोफत",
    # EN: <p>Don't know the birth times? Try <a href="{href}">Naam se Kundali Milan</a> — the
    #     traditional match by the first letter of each name.</p>
    # keep: {href}
    "km.naam": "<p>जन्मवेळ माहीत नाही? <a href=\"{href}\">नावावरून कुंडली मिलन</a> पाहा — प्रत्येकाच्या नावाच्या पहिल्या अक्षरावरून केली जाणारी पारंपरिक जुळवणी.</p>",
    # EN: <h2>The 8 kootas and their points</h2>
    "km.kootas_h2": "<h2>8 कूट आणि त्यांचे गुण</h2>",
    # EN: <tr><th>Koota</th><th>Points</th><th>What it measures</th></tr>
    "km.th": "<tr><th>कूट</th><th>गुण</th><th>काय पाहिले जाते</th></tr>",
    # EN: <tr><td><strong>{name}</strong> <span
    #     lang="hi">({name_hi})</span></td><td>{pts}</td><td>{text}</td></tr>
    # keep: {name} {pts} {text}
    "km.row": "<tr><td><strong>{name}</strong></td><td>{pts}</td><td>{text}</td></tr>",
    # EN: Total
    "km.total": "एकूण",
    # EN: <h2>What is a good Guna Milan score?</h2>
    "km.score_h2": "<h2>गुण मिलनात किती गुण चांगले?</h2>",
    # EN: <tr><th>Gunas</th><th>Conventional reading</th></tr>
    "km.score_th": "<tr><th>गुण</th><th>प्रचलित अर्थ</th></tr>",
    # EN: Below {n}
    # keep: {n}
    "km.below": "{n} पेक्षा कमी",
    # EN: <p>18 is the conventional minimum. The total alone is not the whole story: a high score
    #     with an uncancelled Nadi or Bhakoot dosha is read with caution, and a modest score with
    #     strong Graha Maitri and no doshas is often considered workable. These bands are a
    #     convention with a long history, not a measurement — they are guidance, not a verdict on a
    #     relationship.</p>
    "km.score_p": "<p>18 हे प्रचलित किमान गुण आहेत. केवळ एकूण गुण म्हणजे सर्वकाही नाही: नाडी किंवा भकूट दोषाचा परिहार न झालेला असेल तर जास्त गुणही सावधगिरीने पाहिले जातात, आणि ग्रहमैत्री चांगली असून दोष नसतील तर कमी गुणही अनेकदा चालण्याजोगे मानले जातात. हे टप्पे दीर्घ परंपरेतील संकेत आहेत, मोजमाप नाही — ते मार्गदर्शन आहे, नात्याबद्दलचा निकाल नाही.</p>",
    # EN: {n}st
    # keep: {n}
    "km.ord1": "{n}",
    # EN: {n}nd
    # keep: {n}
    "km.ord2": "{n}",
    # EN: {n}th
    # keep: {n}
    "km.ordn": "{n}",
    # EN: or
    "km.or": " किंवा ",
    # EN: <h2>Mangal Dosha (Manglik)</h2> <p>Mangal Dosha is checked separately from the 36 points.
    #     A chart is Manglik when Mars sits in the {houses} house counted from the
    #     <strong>Lagna</strong> (ascendant), the <strong>Moon</strong> or <strong>Venus</strong>.
    #     Classical texts exempt certain sign placements (for example Mars in its own sign Aries in
    #     the 1st), and Jupiter's aspect on Mars is held to soften it. When <strong>both</strong>
    #     partners are Manglik the dosha is conventionally treated as mutually cancelled — which is
    #     why Manglik matches are made with Manglik partners. Because it depends on the Lagna,
    #     Mangal Dosha does need a reliable birth time.</p>
    # keep: {houses}
    "km.mangal": "<h2>मंगळ दोष (मांगलिक)</h2> <p>मंगळ दोष 36 गुणांपेक्षा वेगळा तपासला जातो. मंगळ <strong>लग्न</strong>, <strong>चंद्र</strong> किंवा <strong>शुक्र</strong> यांपासून मोजल्यास {houses} यांपैकी एखाद्या भावात असेल, तर कुंडली मांगलिक मानली जाते. शास्त्रीय ग्रंथ काही राशीस्थितींना अपवाद मानतात (उदाहरणार्थ, पहिल्या भावात मंगळ स्वराशी मेषेत असणे), आणि मंगळावर गुरूची दृष्टी असल्यास दोष सौम्य होतो असे मानले जाते. जेव्हा <strong>दोघेही</strong> जोडीदार मांगलिक असतात, तेव्हा हा दोष परस्पर रद्द झाला असे परंपरेने मानले जाते — म्हणूनच मांगलिकाचे लग्न मांगलिकाशी केले जाते. तो लग्नावर अवलंबून असल्यामुळे मंगळ दोषासाठी जन्मवेळ विश्वासार्ह असणे आवश्यक असते.</p>",
    # EN: <h2>How our matching tool works</h2> <p>Enter both people's date, time and place of birth.
    #     Both charts are cast with the sidereal zodiac (Lahiri ayanamsa) from the Swiss Ephemeris,
    #     and each koota is scored by table lookup from the classical tables, with every
    #     cancellation named. You get the full {total}-point breakdown and both partners' Mangal
    #     Dosha status, in English or <span lang="hi">हिन्दी</span>, free and without signing
    #     up.</p>
    # keep: {total}
    "km.how": "<h2>आमचे जुळवणी साधन कसे काम करते</h2> <p>दोघांचीही जन्मतारीख, जन्मवेळ आणि जन्मस्थान टाका. स्विस एफेमेरिसवरून निरयन राशिचक्रात (लाहिरी अयनांश) दोन्ही कुंडल्या मांडल्या जातात, आणि प्रत्येक कूटाचे गुण शास्त्रीय तक्त्यांवरून दिले जातात, प्रत्येक परिहाराचे नाव सांगून. तुम्हाला {total} गुणांचे संपूर्ण तपशीलवार विवरण आणि दोघांच्याही मंगळ दोषाची स्थिती मिळते, मराठी, इंग्रजी किंवा हिंदीत, मोफत आणि साइन-अप न करता.</p>",
    # EN: Open Kundali Milan
    "km.cta2": "कुंडली मिलन उघडा",
    # EN: Varna
    "koota.varna": "वर्ण",
    # EN: Vashya
    "koota.vashya": "वश्य",
    # EN: Tara
    "koota.tara": "तारा",
    # EN: Yoni
    "koota.yoni": "योनी",
    # EN: Graha Maitri
    "koota.graha_maitri": "ग्रहमैत्री",
    # EN: Gana
    "koota.gana": "गण",
    # EN: Bhakoot
    "koota.bhakoot": "भकूट",
    # EN: Nadi
    "koota.nadi": "नाडी",
    # EN: Spiritual and working temperament, from the Moon sign's varna. Full point when the groom's
    #     varna is not below the bride's.
    "koota_about.varna": "चंद्र राशीच्या वर्णावरून पाहिलेला आध्यात्मिक आणि कार्यस्वभाव. वराचा वर्ण वधूच्या वर्णापेक्षा खालचा नसल्यास पूर्ण गुण मिळतात.",
    # EN: Mutual attraction and influence — which sign “draws” the other.
    "koota_about.vashya": "परस्पर आकर्षण आणि प्रभाव — कोणती रास दुसरीला “वश” करते.",
    # EN: Health and wellbeing, from the count between the two birth nakshatras; the 3rd, 5th and
    #     7th taras are unfavourable.
    "koota_about.tara": "आरोग्य आणि कल्याण, दोन जन्मनक्षत्रांमधील अंतरावरून; 3री, 5वी आणि 7वी तारा प्रतिकूल मानल्या जातात.",
    # EN: Physical and intimate compatibility; each nakshatra has an animal yoni, and sworn-enemy
    #     animals score zero.
    "koota_about.yoni": "शारीरिक आणि जवळिकीची सुसंगतता; प्रत्येक नक्षत्राला एक प्राणी योनी असते, आणि जन्मशत्रू प्राण्यांना शून्य गुण मिळतात.",
    # EN: Friendship between the lords of the two Moon signs — the mental wavelength of the couple.
    "koota_about.graha_maitri": "दोन्ही चंद्र राशींच्या स्वामींमधील मैत्री — जोडप्याची मानसिक सुसंगतता.",
    # EN: Temperament: Deva (divine), Manushya (human) or Rakshasa (fierce).
    "koota_about.gana": "स्वभाव: देव (दैवी), मनुष्य (मानवी) किंवा राक्षस (उग्र).",
    # EN: The relative placement of the two Moon signs. The 2/12, 5/9 and 6/8 positions form Bhakoot
    #     dosha, cancelled when the sign lords are the same or friends.
    "koota_about.bhakoot": "दोन्ही चंद्र राशींची परस्पर स्थिती. 2/12, 5/9 आणि 6/8 स्थानांमुळे भकूट दोष होतो; राशिस्वामी एकच किंवा मित्र असल्यास त्याचा परिहार होतो.",
    # EN: The highest-weighted koota, tied to health and progeny. The same nadi for both is Nadi
    #     dosha, with classical cancellations for the same sign/different nakshatra or same
    #     nakshatra/different pada.
    "koota_about.nadi": "सर्वाधिक गुणांचा कूट, आरोग्य आणि संततीशी संबंधित. दोघांची नाडी एकच असल्यास नाडी दोष होतो; एकच रास पण वेगळे नक्षत्र, किंवा एकच नक्षत्र पण वेगळा चरण असल्यास शास्त्रीय परिहार आहेत.",
    # EN: Free Kundali Online — Janam Kundali (Birth Chart) in English & Hindi | {brand}
    # keep: {brand}
    "fk.title": "मोफत कुंडली ऑनलाइन — जन्मकुंडली मराठी, हिंदी आणि इंग्रजीत | {brand}",
    # EN: Make your free janam kundali online: Lagna chart in North or South Indian style, planet
    #     positions, Moon nakshatra, Vimshottari dasha, Navamsa and other divisional charts,
    #     Manglik, Sade Sati and Kaal Sarp check — in English or Hindi, no sign-in needed.
    "fk.desc": "तुमची मोफत जन्मकुंडली ऑनलाइन काढा: उत्तर किंवा दक्षिण भारतीय शैलीतील लग्न कुंडली, ग्रहस्थिती, चंद्र नक्षत्र, विंशोत्तरी दशा, नवांश आणि इतर वर्ग कुंडल्या, मांगलिक, साडेसाती आणि कालसर्प तपासणी — मराठी, हिंदी किंवा इंग्रजीत, साइन-इन न करता.",
    # EN: Free Kundali
    "fk.crumb": "मोफत कुंडली",
    # EN: <h1>Free Janam Kundali online</h1> <p class="hi" lang="hi">मुफ़्त जन्म कुंडली — हिंदी और
    #     अंग्रेज़ी में</p> <p>A <strong>janam kundali</strong> (<span lang="hi">जन्म कुंडली</span>,
    #     birth chart) is a map of the sky at the exact moment and place you were born: which of the
    #     twelve signs was rising on the eastern horizon (your <strong>Lagna</strong>), and where
    #     the Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu and Ketu stood among the signs
    #     and the 27 nakshatras. Vedic astrology reads everything else — personality, the twelve
    #     areas of life, and above all <em>timing</em> through the dasha periods — from this one
    #     chart. Ours is computed to the minute and is free.</p>
    "fk.intro": "<h1>मोफत जन्मकुंडली ऑनलाइन</h1> <p class=\"hi\">मोफत जन्मकुंडली — लग्न, ग्रह, दशा आणि दोष तपासणी</p> <p><strong>जन्मकुंडली</strong> म्हणजे तुमच्या जन्माच्या अचूक क्षणी आणि ठिकाणी असलेला आकाशाचा नकाशा: पूर्व क्षितिजावर बारा राशींपैकी कोणती उगवत होती (तुमचे <strong>लग्न</strong>), आणि सूर्य, चंद्र, मंगळ, बुध, गुरू, शुक्र, शनी, राहू आणि केतू कोणत्या राशींत व 27 नक्षत्रांपैकी कोणत्या नक्षत्रात होते. वैदिक ज्योतिष बाकी सर्व काही — स्वभाव, जीवनाची बारा क्षेत्रे, आणि सर्वात महत्त्वाचे म्हणजे दशांमधून <em>काळ</em> — याच एका कुंडलीवरून पाहते. आमची कुंडली मिनिटापर्यंत अचूक काढलेली आहे आणि मोफत आहे.</p>",
    # EN: Make my free kundali now
    "fk.cta1": "माझी मोफत कुंडली आत्ता काढा",
    # EN: <p>You need your <strong>date</strong>, <strong>time</strong> and <strong>place</strong>
    #     of birth. No sign-in, no card.</p>
    "fk.need": "<p>तुमची <strong>जन्मतारीख</strong>, <strong>जन्मवेळ</strong> आणि <strong>जन्मस्थान</strong> लागेल. साइन-इन नको, कार्ड नको.</p>",
    # EN: <h2>What your free kundali includes</h2> <ul> <li><strong>Lagna chart (D1)</strong> in
    #     North Indian or South Indian style — switch with one tap.</li> <li><strong>Planet
    #     positions</strong>: sign, degree, house, dignity and retrograde status of all nine grahas
    #     and the ascendant, with your Moon's nakshatra and pada.</li> <li><strong>The twelve houses
    #     (bhavas)</strong> with the planets in each.</li> <li><strong>Vimshottari dasha</strong>:
    #     your current mahadasha and antardasha with their dates, on a visual timeline.</li>
    #     <li><strong>Divisional charts (vargas)</strong>: {vargas}.</li>
    #     <li><strong>Ashtakavarga</strong>: Sarvashtakavarga and Bhinnashtakavarga bindus by
    #     house.</li> <li><strong>Jaimini</strong> chara karakas (Atmakaraka to Darakaraka) and the
    #     Arudha padas, and the <strong>Sudarshana Chakra</strong> reading of the chart from Lagna,
    #     Moon and Sun together.</li> <li><strong>Dosha check</strong>: Mangal Dosha (Manglik), Sade
    #     Sati and Kaal Sarp.</li> <li><strong>Gemstone and remedy</strong> suggestions for your
    #     chart and current dasha.</li> <li>Your <strong>daily forecast</strong> and today's
    #     panchang, on your chart's dashboard.</li> </ul> <p>Everything is cast in the
    #     <strong>sidereal zodiac with the Lahiri ayanamsa</strong>, whole-sign houses, from the
    #     Swiss Ephemeris. With a free account you can also save charts, download the kundali as a
    #     PDF in English or Hindi, and ask the AI astrologer your first questions free.</p>
    # keep: {vargas}
    "fk.includes": "<h2>तुमच्या मोफत कुंडलीत काय मिळते</h2> <ul> <li><strong>लग्न कुंडली (D1)</strong> उत्तर भारतीय किंवा दक्षिण भारतीय शैलीत — एका टॅपने बदला.</li> <li><strong>ग्रहस्थिती</strong>: नऊ ग्रह आणि लग्न यांची रास, अंश, भाव, बल आणि वक्री स्थिती, तसेच तुमच्या चंद्राचे नक्षत्र आणि चरण.</li> <li><strong>बारा भाव</strong> आणि प्रत्येकातील ग्रह.</li> <li><strong>विंशोत्तरी दशा</strong>: तुमची सध्याची महादशा आणि अंतर्दशा त्यांच्या तारखांसह, दृश्य कालरेषेवर.</li> <li><strong>वर्ग कुंडल्या</strong>: {vargas}.</li> <li><strong>अष्टकवर्ग</strong>: भावानुसार सर्वाष्टकवर्ग आणि भिन्नाष्टकवर्गाचे बिंदू.</li> <li><strong>जैमिनी</strong> चर कारक (आत्मकारक ते दारकारक) आणि आरूढ पदे, तसेच लग्न, चंद्र आणि सूर्य यांवरून एकत्र पाहिलेले <strong>सुदर्शन चक्र</strong>.</li> <li><strong>दोष तपासणी</strong>: मंगळ दोष (मांगलिक), साडेसाती आणि कालसर्प.</li> <li>तुमच्या कुंडलीसाठी आणि सध्याच्या दशेसाठी <strong>रत्ने आणि उपायांच्या</strong> सूचना.</li> <li>तुमच्या कुंडलीच्या डॅशबोर्डवर तुमचे <strong>दैनिक भविष्य</strong> आणि आजचे पंचांग.</li> </ul> <p>सर्व काही स्विस एफेमेरिसवरून <strong>लाहिरी अयनांशासह निरयन राशिचक्रात</strong>, संपूर्ण-राशी भाव पद्धतीने मांडले जाते. मोफत खात्याने तुम्ही कुंडल्या जतन करू शकता, कुंडली मराठी किंवा इंग्रजीत PDF म्हणून डाउनलोड करू शकता, आणि एआय ज्योतिषाला तुमचे पहिले प्रश्न मोफत विचारू शकता.</p>",
    # EN: <h2>How to read your kundali</h2> <h3>1. Start with the Lagna</h3> <p>The first house is
    #     the sign rising at birth. In the North Indian chart it is the top centre diamond, and the
    #     number written in each house is the <em>sign</em> (1 = Aries … 12 = Pisces), not the
    #     house. In the South Indian chart the signs stay in fixed boxes and the Lagna is marked.
    #     The Lagna and its lord describe the body, temperament and the overall direction of
    #     life.</p> <h3>2. Note your Moon sign and nakshatra</h3> <p>Your <strong>rashi</strong> in
    #     Indian usage is the Moon's sign, not the Sun's. It is the sign used for rashifal, Sade
    #     Sati and Kundali Milan, and the Moon's nakshatra decides where your Vimshottari dasha
    #     begins.</p> <h3>3. Read the planets by house</h3> <p>Each house is an area of life: 1st
    #     self, 2nd wealth and family, 3rd courage and siblings, 4th home and mother, 5th children
    #     and intellect, 6th health and rivals, 7th marriage and partnership, 8th longevity and
    #     sudden change, 9th fortune and dharma, 10th career, 11th gains, 12th expenses and moksha.
    #     A planet colours the house it sits in and the houses it rules; its dignity (exalted, own
    #     sign, debilitated) says how well it can deliver.</p> <h3>4. Check the dasha you are
    #     running</h3> <p>The dasha says <em>when</em>. The mahadasha lord, and within it the
    #     antardasha lord, are the planets whose houses come alive in this period — which is why two
    #     people with similar charts can have very different years.</p> <h3>5. Treat doshas in
    #     context</h3> <p>A dosha is a pattern to read, not a verdict. Mangal Dosha has classical
    #     cancellations; Sade Sati is a seven-and-a-half-year transit everyone meets two or three
    #     times. The dosha report names the cancellations it found.</p>
    "fk.read": "<h2>तुमची कुंडली कशी वाचावी</h2> <h3>1. लग्नापासून सुरुवात करा</h3> <p>पहिला भाव म्हणजे जन्माच्या वेळी उगवणारी रास. उत्तर भारतीय कुंडलीत तो वरच्या मध्यभागी असलेला हिरकणीचा आकार असतो, आणि प्रत्येक भावात लिहिलेला अंक <em>रास</em> दर्शवतो (1 = मेष … 12 = मीन), भाव नाही. दक्षिण भारतीय कुंडलीत राशी ठरावीक चौकटींत राहतात आणि लग्न चिन्हांकित केलेले असते. लग्न आणि त्याचा स्वामी शरीर, स्वभाव आणि आयुष्याची एकूण दिशा सांगतात.</p> <h3>2. तुमची चंद्र रास आणि नक्षत्र पाहा</h3> <p>भारतीय पद्धतीत तुमची <strong>रास</strong> म्हणजे चंद्राची रास, सूर्याची नाही. राशिभविष्य, साडेसाती आणि कुंडली मिलनासाठी हीच रास वापरली जाते, आणि चंद्राचे नक्षत्र तुमची विंशोत्तरी दशा कुठून सुरू होते ते ठरवते.</p> <h3>3. भावानुसार ग्रह वाचा</h3> <p>प्रत्येक भाव म्हणजे जीवनाचे एक क्षेत्र: 1ला स्वतः, 2रा धन आणि कुटुंब, 3रा पराक्रम आणि भावंडे, 4था घर आणि माता, 5वा संतती आणि बुद्धी, 6वा आरोग्य आणि शत्रू, 7वा विवाह आणि भागीदारी, 8वा आयुष्य आणि अचानक बदल, 9वा भाग्य आणि धर्म, 10वा करिअर, 11वा लाभ, 12वा खर्च आणि मोक्ष. ग्रह तो ज्या भावात बसला आहे आणि ज्या भावांचा स्वामी आहे त्यांवर आपला रंग चढवतो; त्याचे बल (उच्च, स्वराशी, नीच) तो किती चांगले फळ देऊ शकतो ते सांगते.</p> <h3>4. चालू दशा तपासा</h3> <p>दशा <em>केव्हा</em> ते सांगते. महादशेचा स्वामी, आणि त्यातील अंतर्दशेचा स्वामी, हे असे ग्रह आहेत ज्यांचे भाव या काळात जागृत होतात — म्हणूनच सारख्या कुंडल्या असलेल्या दोन व्यक्तींची वर्षे खूप वेगळी जाऊ शकतात.</p> <h3>5. दोषांकडे संदर्भासह पाहा</h3> <p>दोष हा वाचायचा एक नमुना आहे, निकाल नव्हे. मंगळ दोषाला शास्त्रीय परिहार आहेत; साडेसाती हे साडेसात वर्षांचे गोचर आहे जे प्रत्येकाच्या आयुष्यात दोन-तीन वेळा येते. दोष अहवाल त्याला सापडलेल्या परिहारांची नावे सांगतो.</p>",
    # EN: Create my janam kundali — free
    "fk.cta2": "माझी जन्मकुंडली काढा — मोफत",
    # EN: <h2>Frequently asked questions</h2>
    "fk.faq_h2": "<h2>नेहमी विचारले जाणारे प्रश्न</h2>",
    # EN: Rashi
    "varga.D1": "राशी",
    # EN: Drekkana
    "varga.D3": "द्रेष्काण",
    # EN: Saptamsa
    "varga.D7": "सप्तांश",
    # EN: Navamsa
    "varga.D9": "नवांश",
    # EN: Dashamsa
    "varga.D10": "दशांश",
    # EN: Dwadashamsa
    "varga.D12": "द्वादशांश",
    # EN: Not recommended
    "km.band0": "शिफारस नाही",
    # EN: Acceptable
    "km.band1": "स्वीकारार्ह",
    # EN: Good
    "km.band2": "चांगले",
    # EN: Excellent
    "km.band3": "उत्तम",
}

# app/seo_text.py FAQ["mr"] — the seven free-kundali FAQ pairs (plain text)  [7]
SEO_FAQ = (
    # EN q: Is the kundali really free?
    # EN a: Yes. Casting the chart, the dashas, the divisional charts and the dosha check cost
    #       nothing, and you do not need to sign in to see them. Only the AI astrologer's answers
    #       beyond your free questions, and in-depth paid reports such as the Life Book, cost money.
    ("कुंडली खरोखरच मोफत आहे का?", "होय. कुंडली मांडणे, दशा, वर्ग कुंडल्या आणि दोष तपासणी यांसाठी पैसे पडत नाहीत, आणि ते पाहण्यासाठी साइन-इन करण्याचीही गरज नाही. फक्त तुमच्या मोफत प्रश्नांनंतरची एआय ज्योतिषाची उत्तरे आणि जीवन ग्रंथासारखे सखोल सशुल्क अहवाल यांसाठी पैसे लागतात."),
    # EN q: What details do I need?
    # EN a: Your date of birth, time of birth and place of birth. The place sets the latitude,
    #       longitude and time zone, which decide the Lagna (ascendant) and the house positions.
    ("मला कोणता तपशील लागेल?", "तुमची जन्मतारीख, जन्मवेळ आणि जन्मस्थान. ठिकाणावरून अक्षांश, रेखांश आणि वेळक्षेत्र ठरते, आणि त्यावरून लग्न आणि भावांची स्थिती ठरते."),
    # EN q: What if I don't know my exact birth time?
    # EN a: The chart is still cast, at 12:00 noon. The Moon sign and nakshatra are usually still
    #       right (unless the Moon changed sign or nakshatra that day), so Moon-based readings, Sade
    #       Sati and Kundali Milan stay useful — but the Lagna, the houses and Mangal Dosha need a
    #       reliable time. A time from a birth certificate or hospital record is best.
    ("माझी अचूक जन्मवेळ माहीत नसेल तर?", "कुंडली तरीही दुपारी 12:00 वाजताची धरून मांडली जाते. चंद्र रास आणि नक्षत्र सहसा तरीही बरोबर येतात (त्या दिवशी चंद्राने रास किंवा नक्षत्र बदलले नसेल तर), त्यामुळे चंद्रावर आधारित भविष्य, साडेसाती आणि कुंडली मिलन उपयुक्त राहतात — पण लग्न, भाव आणि मंगळ दोषासाठी विश्वासार्ह वेळ लागते. जन्म दाखला किंवा रुग्णालयाच्या नोंदीतील वेळ सर्वात चांगली."),
    # EN q: Which system do you use — Lahiri, KP, tropical?
    # EN a: Every chart is sidereal (Nirayana) with the Lahiri (Chitrapaksha) ayanamsa, whole-sign
    #       houses and Vimshottari dasha — the convention of most Indian almanacs and astrologers.
    #       Planet positions come from the Swiss Ephemeris.
    ("तुम्ही कोणती पद्धत वापरता — लाहिरी, केपी की सायन?", "प्रत्येक कुंडली निरयन असून लाहिरी (चित्रपक्ष) अयनांश, संपूर्ण-राशी भाव पद्धती आणि विंशोत्तरी दशा वापरून मांडली जाते — बहुतेक भारतीय पंचांगे आणि ज्योतिषी हीच पद्धत वापरतात. ग्रहस्थिती स्विस एफेमेरिसवरून घेतली जाते."),
    # EN q: Can I see my kundali in Hindi?
    # EN a: Yes. Switch the app to हिन्दी and the chart, planet and sign names, dashas and readings
    #       all appear in Hindi; the PDF can be downloaded in Hindi too.
    ("मी माझी कुंडली मराठीत पाहू शकतो का?", "होय. अ‍ॅप मराठीवर बदला, की कुंडली, ग्रह आणि राशींची नावे, दशा आणि भविष्यफल सर्व मराठीत दिसते; PDF देखील मराठीत डाउनलोड करता येते."),
    # EN q: North Indian or South Indian chart?
    # EN a: Both. The same chart can be shown as the North Indian diamond chart (houses fixed, signs
    #       numbered) or the South Indian square chart (signs fixed), with one tap.
    ("उत्तर भारतीय की दक्षिण भारतीय कुंडली?", "दोन्ही. एकच कुंडली एका टॅपने उत्तर भारतीय हिरकणी शैलीत (भाव स्थिर, राशींना अंक) किंवा दक्षिण भारतीय चौकोनी शैलीत (राशी स्थिर) दाखवता येते."),
    # EN q: Is this the same as a horoscope?
    # EN a: A janam kundali is the birth chart itself — the fixed map of the sky at your birth. A
    #       daily horoscope or rashifal is a short general forecast for everyone with the same Moon
    #       sign. Your kundali is personal; a rashifal is not.
    ("हे राशिभविष्यासारखेच आहे का?", "जन्मकुंडली म्हणजे स्वतः जन्मकुंडलीच — तुमच्या जन्माच्या वेळी आकाशाचा स्थिर नकाशा. दैनिक राशिभविष्य हे एकाच चंद्र राशीच्या सर्वांसाठी असलेले छोटेसे सर्वसाधारण भाकीत असते. तुमची कुंडली वैयक्तिक असते; राशिभविष्य तसे नसते."),
)

# app/i18n.py CHROME["mr"] — chrome shared by every server page: breadcrumb, footer links, disclaimer (HTML: write &amp;)  [10]
CHROME = {
    # EN: Home
    "home": "मुखपृष्ठ",
    # EN: Breadcrumb
    "breadcrumb": "मार्गदर्शक पट्टी",
    # EN: Share on WhatsApp
    "share": "WhatsApp वर शेअर करा",
    # EN: Kathas
    "f_katha": "कथा",
    # EN: Terms &amp; Conditions
    "f_terms": "अटी आणि शर्ती",
    # EN: Privacy Policy
    "f_privacy": "गोपनीयता धोरण",
    # EN: Refund &amp; Cancellation
    "f_refund": "परतावा आणि रद्दीकरण",
    # EN: Contact Us
    "f_contact": "संपर्क",
    # EN: Feedback
    "f_feedback": "अभिप्राय",
    # EN: Astrological readings are provided for guidance and entertainment. They are not medical,
    #     legal or financial advice.
    "disclaimer": "ज्योतिषीय भविष्य मार्गदर्शन आणि मनोरंजनासाठी दिले आहे. तो वैद्यकीय, कायदेशीर किंवा आर्थिक सल्ला नाही.",
}

# app/stay_strip.py TEXT["mr"] — the 'Stay in touch' strip at the foot of the pages  [8]
STAY_STRIP = {
    # EN: Stay in touch
    "head": "संपर्कात राहा",
    # EN: Get today's panchang on your phone every morning
    "push": "रोज सकाळी आजचे पंचांग तुमच्या फोनवर मिळवा",
    # EN: Turning on…
    "busy": "सुरू करत आहे…",
    # EN: Done — you will get it every morning.
    "on": "झाले — तुम्हाला ते रोज सकाळी मिळेल.",
    # EN: Could not turn on alerts. Please try again.
    "err": "सूचना सुरू करता आल्या नाहीत. कृपया पुन्हा प्रयत्न करा.",
    # EN: Notifications are blocked for this site in your browser settings.
    "denied": "तुमच्या ब्राउझर सेटिंग्जमध्ये या साइटसाठी सूचना बंद आहेत.",
    # EN: Join our WhatsApp channel
    "channel": "आमच्या WhatsApp चॅनेलमध्ये सामील व्हा",
    # EN: Share this page on WhatsApp
    "share": "हे पान WhatsApp वर शेअर करा",
}

# app/seo_city_names.py CITIES["mr"] — the 114 cities as that language's newspapers spell them (key = URL slug)  [114]
CITY_NAMES = {
    # EN: New Delhi
    "new-delhi": "नवी दिल्ली",
    # EN: Mumbai
    "mumbai": "मुंबई",
    # EN: Kolkata
    "kolkata": "कोलकाता",
    # EN: Chennai
    "chennai": "चेन्नई",
    # EN: Bengaluru
    "bengaluru": "बेंगळुरू",
    # EN: Hyderabad
    "hyderabad": "हैदराबाद",
    # EN: Ahmedabad
    "ahmedabad": "अहमदाबाद",
    # EN: Pune
    "pune": "पुणे",
    # EN: Jaipur
    "jaipur": "जयपूर",
    # EN: Lucknow
    "lucknow": "लखनऊ",
    # EN: Kanpur
    "kanpur": "कानपूर",
    # EN: Nagpur
    "nagpur": "नागपूर",
    # EN: Indore
    "indore": "इंदूर",
    # EN: Bhopal
    "bhopal": "भोपाळ",
    # EN: Patna
    "patna": "पाटणा",
    # EN: Varanasi
    "varanasi": "वाराणसी",
    # EN: Prayagraj
    "prayagraj": "प्रयागराज",
    # EN: Surat
    "surat": "सुरत",
    # EN: Vadodara
    "vadodara": "वडोदरा",
    # EN: Chandigarh
    "chandigarh": "चंदीगड",
    # EN: Amritsar
    "amritsar": "अमृतसर",
    # EN: Dehradun
    "dehradun": "डेहराडून",
    # EN: Haridwar
    "haridwar": "हरिद्वार",
    # EN: Noida
    "noida": "नोएडा",
    # EN: Gurugram
    "gurugram": "गुरुग्राम",
    # EN: Bhubaneswar
    "bhubaneswar": "भुवनेश्वर",
    # EN: Guwahati
    "guwahati": "गुवाहाटी",
    # EN: Ranchi
    "ranchi": "रांची",
    # EN: Kochi
    "kochi": "कोची",
    # EN: Visakhapatnam
    "visakhapatnam": "विशाखापट्टणम",
    # EN: Thane
    "thane": "ठाणे",
    # EN: Navi Mumbai
    "navi-mumbai": "नवी मुंबई",
    # EN: Nashik
    "nashik": "नाशिक",
    # EN: Chhatrapati Sambhajinagar
    "chhatrapati-sambhajinagar": "छत्रपती संभाजीनगर",
    # EN: Solapur
    "solapur": "सोलापूर",
    # EN: Kolhapur
    "kolhapur": "कोल्हापूर",
    # EN: Amravati
    "amravati": "अमरावती",
    # EN: Shirdi
    "shirdi": "शिर्डी",
    # EN: Rajkot
    "rajkot": "राजकोट",
    # EN: Bhavnagar
    "bhavnagar": "भावनगर",
    # EN: Jamnagar
    "jamnagar": "जामनगर",
    # EN: Gandhinagar
    "gandhinagar": "गांधीनगर",
    # EN: Dwarka
    "dwarka": "द्वारका",
    # EN: Somnath
    "somnath": "सोमनाथ",
    # EN: Jodhpur
    "jodhpur": "जोधपूर",
    # EN: Udaipur
    "udaipur": "उदयपूर",
    # EN: Kota
    "kota": "कोटा",
    # EN: Ajmer
    "ajmer": "अजमेर",
    # EN: Bikaner
    "bikaner": "बिकानेर",
    # EN: Agra
    "agra": "आग्रा",
    # EN: Ghaziabad
    "ghaziabad": "गाझियाबाद",
    # EN: Meerut
    "meerut": "मेरठ",
    # EN: Bareilly
    "bareilly": "बरेली",
    # EN: Aligarh
    "aligarh": "अलीगढ",
    # EN: Moradabad
    "moradabad": "मुरादाबाद",
    # EN: Gorakhpur
    "gorakhpur": "गोरखपूर",
    # EN: Saharanpur
    "saharanpur": "सहारनपूर",
    # EN: Ayodhya
    "ayodhya": "अयोध्या",
    # EN: Mathura
    "mathura": "मथुरा",
    # EN: Vrindavan
    "vrindavan": "वृंदावन",
    # EN: Jhansi
    "jhansi": "झाशी",
    # EN: Faridabad
    "faridabad": "फरीदाबाद",
    # EN: Kurukshetra
    "kurukshetra": "कुरुक्षेत्र",
    # EN: Ludhiana
    "ludhiana": "लुधियाना",
    # EN: Jalandhar
    "jalandhar": "जालंधर",
    # EN: Patiala
    "patiala": "पतियाळा",
    # EN: Rishikesh
    "rishikesh": "ऋषिकेश",
    # EN: Shimla
    "shimla": "शिमला",
    # EN: Jammu
    "jammu": "जम्मू",
    # EN: Srinagar
    "srinagar": "श्रीनगर",
    # EN: Katra
    "katra": "कटरा",
    # EN: Gwalior
    "gwalior": "ग्वाल्हेर",
    # EN: Jabalpur
    "jabalpur": "जबलपूर",
    # EN: Ujjain
    "ujjain": "उज्जैन",
    # EN: Raipur
    "raipur": "रायपूर",
    # EN: Bhilai
    "bhilai": "भिलाई",
    # EN: Gaya
    "gaya": "गया",
    # EN: Bhagalpur
    "bhagalpur": "भागलपूर",
    # EN: Muzaffarpur
    "muzaffarpur": "मुझफ्फरपूर",
    # EN: Jamshedpur
    "jamshedpur": "जमशेदपूर",
    # EN: Dhanbad
    "dhanbad": "धनबाद",
    # EN: Deoghar
    "deoghar": "देवघर",
    # EN: Howrah
    "howrah": "हावडा",
    # EN: Asansol
    "asansol": "आसनसोल",
    # EN: Siliguri
    "siliguri": "सिलीगुडी",
    # EN: Cuttack
    "cuttack": "कटक",
    # EN: Puri
    "puri": "पुरी",
    # EN: Coimbatore
    "coimbatore": "कोईम्बतूर",
    # EN: Madurai
    "madurai": "मदुराई",
    # EN: Tiruchirappalli
    "tiruchirappalli": "तिरुचिरापल्ली",
    # EN: Salem
    "salem": "सेलम",
    # EN: Rameswaram
    "rameswaram": "रामेश्वरम",
    # EN: Thiruvananthapuram
    "thiruvananthapuram": "तिरुवनंतपुरम",
    # EN: Kozhikode
    "kozhikode": "कोझिकोड",
    # EN: Thrissur
    "thrissur": "त्रिशूर",
    # EN: Kollam
    "kollam": "कोल्लम",
    # EN: Kannur
    "kannur": "कन्नूर",
    # EN: Malappuram
    "malappuram": "मलप्पुरम",
    # EN: Mysuru
    "mysuru": "म्हैसूर",
    # EN: Mangaluru
    "mangaluru": "मंगळुरू",
    # EN: Hubballi
    "hubballi": "हुबळी",
    # EN: Warangal
    "warangal": "वारंगळ",
    # EN: Vijayawada
    "vijayawada": "विजयवाडा",
    # EN: Tirupati
    "tirupati": "तिरुपती",
    # EN: Guntur
    "guntur": "गुंटूर",
    # EN: Panaji
    "panaji": "पणजी",
    # EN: Shillong
    "shillong": "शिलाँग",
    # EN: Imphal
    "imphal": "इम्फाळ",
    # EN: Agartala
    "agartala": "आगरतळा",
    # EN: Gangtok
    "gangtok": "गंगटोक",
    # EN: Aizawl
    "aizawl": "ऐझॉल",
    # EN: Kohima
    "kohima": "कोहिमा",
    # EN: Itanagar
    "itanagar": "इटानगर",
    # EN: Puducherry
    "puducherry": "पुदुच्चेरी",
}

# app/seo_city_names.py STATES["mr"] — the states and union territories (key = English state name)  [32]
STATE_NAMES = {
    # EN: Andhra Pradesh
    "Andhra Pradesh": "आंध्र प्रदेश",
    # EN: Arunachal Pradesh
    "Arunachal Pradesh": "अरुणाचल प्रदेश",
    # EN: Assam
    "Assam": "आसाम",
    # EN: Bihar
    "Bihar": "बिहार",
    # EN: Chandigarh
    "Chandigarh": "चंदीगड",
    # EN: Chhattisgarh
    "Chhattisgarh": "छत्तीसगड",
    # EN: Delhi
    "Delhi": "दिल्ली",
    # EN: Goa
    "Goa": "गोवा",
    # EN: Gujarat
    "Gujarat": "गुजरात",
    # EN: Haryana
    "Haryana": "हरियाणा",
    # EN: Himachal Pradesh
    "Himachal Pradesh": "हिमाचल प्रदेश",
    # EN: Jammu and Kashmir
    "Jammu and Kashmir": "जम्मू आणि काश्मीर",
    # EN: Jharkhand
    "Jharkhand": "झारखंड",
    # EN: Karnataka
    "Karnataka": "कर्नाटक",
    # EN: Kerala
    "Kerala": "केरळ",
    # EN: Madhya Pradesh
    "Madhya Pradesh": "मध्य प्रदेश",
    # EN: Maharashtra
    "Maharashtra": "महाराष्ट्र",
    # EN: Manipur
    "Manipur": "मणिपूर",
    # EN: Meghalaya
    "Meghalaya": "मेघालय",
    # EN: Mizoram
    "Mizoram": "मिझोराम",
    # EN: Nagaland
    "Nagaland": "नागालँड",
    # EN: Odisha
    "Odisha": "ओडिशा",
    # EN: Puducherry
    "Puducherry": "पुदुच्चेरी",
    # EN: Punjab
    "Punjab": "पंजाब",
    # EN: Rajasthan
    "Rajasthan": "राजस्थान",
    # EN: Sikkim
    "Sikkim": "सिक्कीम",
    # EN: Tamil Nadu
    "Tamil Nadu": "तमिळनाडू",
    # EN: Telangana
    "Telangana": "तेलंगणा",
    # EN: Tripura
    "Tripura": "त्रिपुरा",
    # EN: Uttar Pradesh
    "Uttar Pradesh": "उत्तर प्रदेश",
    # EN: Uttarakhand
    "Uttarakhand": "उत्तराखंड",
    # EN: West Bengal
    "West Bengal": "पश्चिम बंगाल",
}

# app/astro/choghadiya.py CHOGHADIYA_INFO["mr"] — one-line description of each of the seven choghadiya slots  [7]
CHOGHADIYA_DESC = {
    # EN: Best time for all ceremonies, investments, agreements, and starting important endeavors.
    "Amrit": "सर्व समारंभ, गुंतवणूक, करार आणि महत्त्वाची कामे सुरू करण्यासाठी सर्वोत्तम वेळ.",
    # EN: Highly auspicious for ceremonies, religious rituals, education, and purchasing property.
    "Shubh": "समारंभ, धार्मिक विधी, शिक्षण आणि मालमत्ता खरेदीसाठी अत्यंत शुभ.",
    # EN: Favorable for business, trade, financial transactions, launching products, and interviews.
    "Labh": "व्यवसाय, व्यापार, आर्थिक व्यवहार, उत्पादन सुरू करणे आणि मुलाखतींसाठी अनुकूल.",
    # EN: Neutral. Excellent for journeys, travel, vehicle purchases, and shifting places.
    "Char": "सामान्य. प्रवास, वाहन खरेदी आणि स्थलांतरासाठी उत्तम.",
    # EN: Inauspicious. Avoid medical procedures or conflict. Only suitable for competitive sports
    #     or defeating rivals.
    "Rog": "अशुभ. वैद्यकीय प्रक्रिया किंवा संघर्ष टाळा. फक्त स्पर्धात्मक खेळ किंवा प्रतिस्पर्ध्यांवर मात करण्यासाठी योग्य.",
    # EN: Inauspicious. Ruled by Saturn; causes delays and setbacks. Avoid new ventures or signing
    #     documents.
    "Kaal": "अशुभ. शनीचा अंमल; विलंब आणि अडथळे येतात. नवीन उपक्रम किंवा कागदपत्रांवर सह्या टाळा.",
    # EN: Inauspicious. Causes restlessness and anxiety. Favorable only for government filings or
    #     official duties.
    "Udveg": "अशुभ. अस्वस्थता आणि चिंता वाढवतो. फक्त सरकारी कागदपत्रे किंवा अधिकृत कामांसाठी अनुकूल.",
}

# ----------------------------------------------------------------------------
# rashifal  /rashifal and /rashifal/<sign>
# ----------------------------------------------------------------------------

# app/rashifal_text.py TEXT["mr"] — page text of /rashifal and /rashifal/<sign>  [63]
RASHIFAL_TEXT = {
    # EN: {house} house
    # keep: {house}
    "house_short": "{house} भावात",
    # EN: (retrograde)
    "rx": " (वक्री)",
    # EN: Moon
    "planet.Moon": "चंद्र",
    # EN: Saturn
    "planet.Saturn": "शनी",
    # EN: Jupiter
    "planet.Jupiter": "गुरू",
    # EN: Rahu
    "planet.Rahu": "राहू",
    # EN: Ketu
    "planet.Ketu": "केतू",
    # EN: {english} ({name})
    # keep: {local}
    "sign_label": "{local}",
    # EN: {name} · {english}
    # keep: {local}
    "sign_link": "{local}",
    # EN: {name}
    # keep: {local}
    "sign_crumb": "{local}",
    # EN: {name}
    # keep: {local}
    "sade_name": "{local}",
    # EN: Rashifal
    "crumb_root": "राशिभविष्य",
    # EN: hi
    "sub_lang": 'mr',
    # EN: {name} Rashifal Today, {date_short} — {english} Daily Horoscope | {brand}
    # keep: {brand} {local}
    # may also use: {date_short} {date}
    "s.title": "{local} राशिभविष्य आज, {date_short} — दैनिक राशिभविष्य | {brand}",
    # EN: {name} ({english} Moon sign) rashifal for {weekday}, {date}: the Moon transits your
    #     {house} house — {tone_lower}. Plus Saturn, Jupiter and Rahu–Ketu transits, Sade Sati
    #     status and today's tithi, computed from the sidereal sky.
    # keep: {date} {house} {local} {tone} {weekday}
    "s.desc": "{local} राशीचे {weekday}, {date} चे राशिभविष्य: चंद्र तुमच्या राशीपासून {house} भावात आहे — {tone}. तसेच शनी, गुरू आणि राहू-केतू यांचे गोचर, साडेसातीची स्थिती आणि आजची तिथी, निरयन आकाशावरून काढलेली.",
    # EN: {name} Rashifal Today — {english} Daily Horoscope
    # keep: {local}
    "s.h1": "{local} राशिभविष्य आज — दैनिक भविष्य",
    # EN: आज का {name_hi} राशिफल
    # may also use: {local}
    "s.sub": "{local} रास · दैनिक राशिभविष्य",
    # EN: the Moon is in your {house} house from {name}.
    # keep: {house}
    "s.summary": "चंद्र तुमच्या राशीपासून {house} भावात आहे.",
    # EN: About {name} rashi — traits, nakshatras and name letters
    # keep: {local}
    "s.about_rashi": "{local} रास — स्वभाव, नक्षत्रे आणि नावाची अक्षरे",
    # EN: Today's Moon transit (Chandra gochar)
    "moon.head": "आजचे चंद्र गोचर",
    # EN: The Moon is in {sign} all day — your {house} house.
    # keep: {house} {sign}
    "moon.allday": "चंद्र दिवसभर {sign} राशीत आहे — तुमच्या {house} भावात.",
    # EN: <strong>Until {time} IST:</strong> the Moon is in {sign} — your {house} house.
    # keep: {house} {sign} {time}
    "moon.until": "<strong>{time} पर्यंत:</strong> चंद्र {sign} राशीत आहे — तुमच्या {house} भावात.",
    # EN: <strong>From {time} IST:</strong> the Moon enters {sign} — your {house} house.
    # keep: {house} {sign} {time}
    "moon.from": "<strong>{time} पासून:</strong> चंद्र {sign} राशीत प्रवेश करतो — तुमच्या {house} भावात.",
    # EN: <p>The Moon changes sign during the day, so the day reads in two parts.</p>
    "moon.two": "<p>चंद्र दिवसभरात रास बदलतो, त्यामुळे दिवसाचे दोन भाग करून पाहावे लागते.</p>",
    # EN: The longer backdrop: slow transits
    "back.head": "मोठी पार्श्वभूमी: संथ गोचर",
    # EN: <p>These planets stay in one sign for months or years, so they set the background against
    #     which each day plays out.</p>
    "back.intro": "<p>हे ग्रह अनेक महिने किंवा वर्षे एकाच राशीत राहतात, म्हणून ते रोजच्या दिवसांची पार्श्वभूमी ठरवतात.</p>",
    # EN: {sign}{rx} · {house} house
    # keep: {house} {rx} {sign}
    "back.where": "{sign}{rx} · {house} भावात",
    # EN: first (rising)
    "phase.1": "पहिला (आरंभीचा)",
    # EN: second (peak)
    "phase.2": "दुसरा (शिखराचा)",
    # EN: third (setting)
    "phase.3": "तिसरा (उतरता)",
    # EN: <strong>Sade Sati is running</strong> — the {phase} phase. It is a slow, disciplining
    #     period rather than something to fear; steady routine, service and patience make it
    #     lighter.
    # keep: {phase}
    "sade.running": "<strong>साडेसाती सुरू आहे</strong> — {phase} टप्पा. हा घाबरण्याचा काळ नाही, तर शिस्त लावणारा संथ काळ आहे; नियमित दिनक्रम, सेवा आणि संयम यांनी तो सुसह्य होतो.",
    # EN: <strong>No Sade Sati</strong>, but Saturn's Dhaiya is running (see above).
    "sade.dhaiya": "<strong>साडेसाती नाही</strong>, पण शनीची पनवती (ढैया) सुरू आहे (वर पाहा).",
    # EN: <strong>No Sade Sati</strong> — Saturn is not in the 12th, 1st or 2nd from your sign.
    "sade.none": "<strong>साडेसाती नाही</strong> — शनी तुमच्या राशीपासून बाराव्या, पहिल्या किंवा दुसऱ्या स्थानी नाही.",
    # EN: <h2>Today's Panchang</h2><p>At sunrise in New Delhi it is <strong>{paksha}
    #     {tithi}</strong> tithi with the Moon in <strong>{nakshatra}</strong> nakshatra. Rahu Kaal,
    #     sunrise and the full almanac are on <a href="/panchang">today's Panchang</a>.</p>
    # keep: {nakshatra} {tithi}
    # may also use: {paksha_full} {paksha}
    "panchang": "<h2>आजचे पंचांग</h2><p>नवी दिल्लीत सूर्योदयाच्या वेळी <strong>{paksha} {tithi}</strong> तिथी असून चंद्र <strong>{nakshatra}</strong> नक्षत्रात आहे. राहुकाळ, सूर्योदय आणि संपूर्ण पंचांग <a href=\"/panchang\">आजच्या पंचांगात</a> पाहा.</p>",
    # EN: <p class="note">This rashifal is read from your Moon sign alone — the same for everyone
    #     born with the Moon in that sign. A personal reading uses your full birth chart: the
    #     ascendant, your running dasha and the ashtakavarga strength of each transit. Not sure of
    #     your Moon sign (rashi)? It is the first thing your free kundali shows — it is usually not
    #     your Western sun sign.</p>
    "personal": "<p class=\"note\">हे राशिभविष्य केवळ तुमच्या चंद्र राशीवरून पाहिलेले आहे — त्या राशीत चंद्र असताना जन्मलेल्या सर्वांसाठी ते सारखेच असते. वैयक्तिक भविष्यासाठी तुमची संपूर्ण जन्मकुंडली वापरली जाते: लग्न, तुमची चालू दशा आणि प्रत्येक गोचराचे अष्टकवर्ग बल. तुमची चंद्र रास (रास) नक्की माहीत नाही? तुमची मोफत कुंडली सर्वात आधी तीच दाखवते — ती सहसा तुमची पाश्चात्य सूर्य रास नसते.</p>",
    # EN: Get your free kundali — then ask a question about your own chart
    "cta": "तुमची मोफत कुंडली मिळवा — आणि मग स्वतःच्या कुंडलीबद्दल प्रश्न विचारा",
    # EN: Today's Rashifal for every sign
    "signs.head": "सर्व राशींचे आजचे राशिभविष्य",
    # EN: More free tools
    "more.head": "आणखी मोफत साधने",
    # EN: <h2>How this is calculated</h2><p>Planet positions are computed for today (IST) with the
    #     Swiss Ephemeris in the sidereal zodiac (Lahiri ayanamsa) — the same positions our kundali
    #     and panchang use. Houses are counted from your Moon sign, as in classical gochar. Which
    #     houses are favourable follows the scheme of Varahamihira's Brihat Samhita (ch. 104) and
    #     Mantreswara's Phaladeepika (ch. 26): the Moon is favourable in the 1st, 3rd, 6th, 7th,
    #     10th and 11th; Saturn, Rahu and Ketu in the 3rd, 6th and 11th; Jupiter in the 2nd, 5th,
    #     7th, 9th and 11th.</p>
    "method": "<h2>हे कसे काढले जाते</h2><p>ग्रहांची स्थिती आजसाठी (भारतीय वेळेनुसार) स्विस एफेमेरिसने निरयन राशिचक्रात (लाहिरी अयनांश) काढली जाते — आमची कुंडली आणि पंचांग वापरतात तीच स्थिती. शास्त्रीय गोचराप्रमाणे भाव तुमच्या चंद्र राशीपासून मोजले जातात. कोणते भाव अनुकूल आहेत ते वराहमिहिराच्या बृहत्संहितेतील (अ. 104) आणि मंत्रेश्वराच्या फलदीपिकेतील (अ. 26) पद्धतीनुसार ठरते: चंद्र पहिल्या, तिसऱ्या, सहाव्या, सातव्या, दहाव्या आणि अकराव्या भावात अनुकूल असतो; शनी, राहू आणि केतू तिसऱ्या, सहाव्या आणि अकराव्या भावात; गुरू दुसऱ्या, पाचव्या, सातव्या, नवव्या आणि अकराव्या भावात.</p>",
    # EN: Aaj Ka Rashifal, {date_short} — Today's Horoscope for All 12 Signs | {brand}
    # keep: {brand}
    # may also use: {date_short} {date}
    "i.title": "आजचे राशिभविष्य, {date_short} — सर्व 12 राशींचे दैनिक भविष्य | {brand}",
    # EN: Today's rashifal for {weekday}, {date}: daily horoscope for all 12 Moon signs from Mesh to
    #     Meen — Moon transit, Saturn, Jupiter and Rahu, and Sade Sati, computed from the sidereal
    #     sky.
    # keep: {date} {weekday}
    "i.desc": "{weekday}, {date} चे राशिभविष्य: मेषेपासून मीनेपर्यंत सर्व 12 चंद्र राशींचे दैनिक भविष्य — चंद्र गोचर, शनी, गुरू आणि राहू, आणि साडेसाती, निरयन आकाशावरून काढलेले.",
    # EN: Today's Rashifal — Daily Horoscope
    "i.h1": "आजचे राशिभविष्य — दैनिक भविष्य",
    # EN: आज का राशिफल — सभी 12 राशियाँ
    "i.sub": "आजचे राशिभविष्य — सर्व 12 राशी",
    # EN: <p>Rashifal is read from your <strong>Moon sign</strong> (rashi). {moon_text} Saturn is in
    #     {sat_sign}, so Sade Sati is running for {sade_names}.</p>
    # keep: {moon_text} {sade_names} {sat_sign}
    "i.intro": "<p>राशिभविष्य तुमच्या <strong>चंद्र राशीवरून</strong> पाहिले जाते. {moon_text} शनी {sat_sign} राशीत आहे, त्यामुळे {sade_names} या राशींना साडेसाती सुरू आहे.</p>",
    # EN: The Moon is in {now} until {time} IST, then in {next}. The table shows the position for
    #     most of the day.
    # keep: {next} {now} {time}
    "i.moon_two": "चंद्र {time} पर्यंत {now} राशीत आहे, त्यानंतर {next} राशीत. तक्त्यात दिवसाच्या बहुतेक वेळची स्थिती दाखवली आहे.",
    # EN: The Moon is in {now} all day.
    # keep: {now}
    "i.moon_one": "चंद्र दिवसभर {now} राशीत आहे.",
    # EN: {name} <small>{english}</small>
    # keep: {local}
    "i.name": "{local}",
    # EN: <small>Sade Sati</small>
    "i.sade": "<small>साडेसाती</small>",
    # EN: <tr><th>Sign</th><th>Moon in your</th><th>Today</th></tr>
    "i.head_row": "<tr><th>रास</th><th>तुमच्या राशीपासून चंद्र</th><th>आज</th></tr>",
    # EN: Sign not found
    "nf.title": "रास सापडली नाही",
    # EN: <h1>Sign not found</h1><p>There is no rashi called “{slug}”. Pick your Moon sign
    #     below.</p>
    # keep: {slug}
    "nf.body": "<h1>रास सापडली नाही</h1><p>“{slug}” नावाची कोणतीही रास नाही. खालून तुमची चंद्र रास निवडा.</p>",
    # EN: 1st
    "house.1": "पहिल्या",
    # EN: 2nd
    "house.2": "दुसऱ्या",
    # EN: 3rd
    "house.3": "तिसऱ्या",
    # EN: 4th
    "house.4": "चौथ्या",
    # EN: 5th
    "house.5": "पाचव्या",
    # EN: 6th
    "house.6": "सहाव्या",
    # EN: 7th
    "house.7": "सातव्या",
    # EN: 8th
    "house.8": "आठव्या",
    # EN: 9th
    "house.9": "नवव्या",
    # EN: 10th
    "house.10": "दहाव्या",
    # EN: 11th
    "house.11": "अकराव्या",
    # EN: 12th
    "house.12": "बाराव्या",
}

# app/rashifal_text.py MORE_LINKS["mr"] — 'More free tools' links: keep every href, translate the text; the first href is '{twin:en}' (this page in English)  [6]
RASHIFAL_MORE_LINKS = (
    # EN href: {twin:en}
    # EN text: Read in English
    ("{twin:en}", "इंग्रजीत वाचा"),
    # EN href: /panchang
    # EN text: Today's Panchang
    ("/panchang", "आजचे पंचांग"),
    # EN href: /rahu-kaal
    # EN text: Rahu Kaal today
    ("/rahu-kaal", "आजचा राहुकाळ"),
    # EN href: /choghadiya
    # EN text: Choghadiya today
    ("/choghadiya", "आजचा चौघडिया"),
    # EN href: /kundali-milan
    # EN text: Kundali Milan
    ("/kundali-milan", "कुंडली मिलन"),
    # EN href: /vrat-tyohar
    # EN text: Today's vrat & festivals
    ("/vrat-tyohar", "आजची व्रते आणि सण"),
)

# app/rashifal_text.py TONE_LABEL["mr"] — the three day tones (keys good / mixed / easy)  [3]
RASHIFAL_TONE_LABEL = {
    # EN: Favourable day
    "good": "अनुकूल दिवस",
    # EN: Mixed day
    "mixed": "संमिश्र दिवस",
    # EN: Take it easy
    "easy": "सावकाश घेण्याचा दिवस",
}

# app/rashifal_text.py MOON_HOUSE["mr"] — Moon transit through houses 1-12 (key = house number)  [12]
RASHIFAL_MOON_HOUSE = {
    # EN: The Moon moves through your own sign today (Janma Chandra). Classical texts read this as a
    #     day of comfort and good spirits — good food, warm company and a clear sense of yourself. A
    #     good day to look after your own needs and begin small, personal things.
    1: "आज चंद्र तुमच्याच राशीतून फिरत आहे (जन्मचंद्र). शास्त्रीय ग्रंथ हा दिवस सुखाचा आणि उत्साहाचा मानतात — चांगले जेवण, आपुलकीची संगत आणि स्वतःविषयी स्पष्टता. स्वतःच्या गरजांकडे लक्ष देण्यासाठी आणि लहान, वैयक्तिक गोष्टी सुरू करण्यासाठी हा चांगला दिवस आहे.",
    # EN: The Moon is in your 2nd house today. Tradition asks for care with money and words —
    #     expenses can creep up and small misunderstandings arise easily. Keep spending planned and
    #     speak gently at home; routine work goes fine.
    2: "आज चंद्र तुमच्या दुसऱ्या भावात आहे. परंपरेनुसार पैसा आणि बोलणे यांबाबत जपावे लागते — खर्च हळूहळू वाढू शकतात आणि लहानसहान गैरसमज सहज होतात. खर्चाचे नियोजन करा आणि घरात मृदू बोला; नेहमीची कामे नीट होतात.",
    # EN: The Moon in your 3rd house is a favourable transit. Courage and initiative are high,
    #     effort brings results, and contact with siblings, friends and neighbours goes well. A good
    #     day for short trips, calls and pushing a pending task over the line.
    3: "चंद्र तुमच्या तिसऱ्या भावात असणे हे अनुकूल गोचर आहे. धैर्य आणि पुढाकार जास्त असतात, प्रयत्नांना फळ मिळते आणि भावंडे, मित्र व शेजाऱ्यांशी संपर्क चांगला राहतो. लहान प्रवास, फोन आणि प्रलंबित काम पूर्ण करण्यासाठी हा चांगला दिवस आहे.",
    # EN: The Moon in your 4th house can leave the mind a little unsettled — home matters or travel
    #     may feel tiring. Keep the day simple, avoid arguments at home and give yourself some quiet
    #     time; the mood lifts as the Moon moves on.
    4: "चंद्र तुमच्या चौथ्या भावात असल्यास मन थोडे अस्वस्थ राहू शकते — घरचे प्रश्न किंवा प्रवास थकवणारे वाटू शकतात. दिवस साधा ठेवा, घरात वाद टाळा आणि थोडा शांत वेळ स्वतःला द्या; चंद्र पुढे सरकला की मन हलके होते.",
    # EN: The Moon in your 5th house is a mixed transit. Plans may meet small hurdles and the mind
    #     can swing between ideas. Avoid speculative decisions; study, creative work and time with
    #     children are better uses of the day.
    5: "चंद्र तुमच्या पाचव्या भावात असणे हे संमिश्र गोचर आहे. योजनांना लहान अडथळे येऊ शकतात आणि मन विविध कल्पनांमध्ये हेलकावू शकते. सट्टेबाजीचे निर्णय टाळा; अभ्यास, सर्जनशील काम आणि मुलांसोबत वेळ घालवण्यासाठी दिवस अधिक चांगला आहे.",
    # EN: The Moon in your 6th house is one of its best transits. Classical texts promise success
    #     over rivals and obstacles, and the energy to clear a backlog. A good day for competitive
    #     work, settling pending issues and steady routines.
    6: "चंद्र तुमच्या सहाव्या भावात असणे हे त्याचे सर्वोत्तम गोचरांपैकी एक आहे. शास्त्रीय ग्रंथ शत्रू आणि अडथळ्यांवर यश तसेच साचलेली कामे संपवण्याची ऊर्जा सांगतात. स्पर्धात्मक काम, प्रलंबित प्रश्न मिटवणे आणि नियमित दिनचर्येसाठी चांगला दिवस.",
    # EN: The Moon in your 7th house favours partnership and company. Time with your spouse or
    #     partner, meetings and agreements tend to go smoothly, with comfort and good food. A good
    #     day to reach out and work together.
    7: "चंद्र तुमच्या सातव्या भावात असल्यास भागीदारी आणि संगत अनुकूल ठरते. जोडीदारासोबतचा वेळ, बैठका आणि करार सहसा सुरळीत पार पडतात, सोबत सुख आणि चांगले जेवण असते. पुढाकार घेऊन एकत्र काम करण्यासाठी चांगला दिवस.",
    # EN: The Moon is in your 8th house — the period known as Chandrashtama. Tradition advises
    #     against starting important new things today; unexpected delays are more likely and the
    #     mind can feel anxious. Keep a margin in your schedule, stick to familiar work and be
    #     gentle with yourself — it passes within two to three days.
    8: "आज चंद्र तुमच्या आठव्या भावात आहे — हा काळ चंद्राष्टम म्हणून ओळखला जातो. परंपरेनुसार आज महत्त्वाच्या नवीन गोष्टी सुरू करू नयेत; अनपेक्षित विलंब होण्याची शक्यता जास्त असते आणि मन चिंताग्रस्त वाटू शकते. वेळापत्रकात थोडी मोकळीक ठेवा, ओळखीच्या कामाला चिकटून राहा आणि स्वतःशी सौम्य राहा — हे दोन-तीन दिवसांत निघून जाते.",
    # EN: The Moon in your 9th house is a mixed transit. Plans may need extra effort and you may
    #     feel tired or distracted. Prayer, reading and time with elders or teachers suit the day
    #     better than big new ventures.
    9: "चंद्र तुमच्या नवव्या भावात असणे हे संमिश्र गोचर आहे. योजनांसाठी जास्त मेहनत लागू शकते आणि थकवा किंवा लक्ष विचलित झाल्यासारखे वाटू शकते. मोठ्या नवीन उपक्रमांपेक्षा प्रार्थना, वाचन आणि वडीलधारी किंवा गुरुजनांसोबत वेळ घालवणे या दिवसाला अधिक शोभते.",
    # EN: The Moon in your 10th house supports work and reputation. Tasks get done, seniors are
    #     receptive and effort is noticed. A good day to present your work, take a professional step
    #     or finish something visible.
    10: "चंद्र तुमच्या दहाव्या भावात असल्यास काम आणि प्रतिष्ठेला बळ मिळते. कामे पूर्ण होतात, वरिष्ठ ग्रहणशील असतात आणि प्रयत्नांची दखल घेतली जाते. तुमचे काम सादर करण्यासाठी, व्यावसायिक पाऊल उचलण्यासाठी किंवा दृश्य स्वरूपाचे काहीतरी पूर्ण करण्यासाठी चांगला दिवस.",
    # EN: The Moon in your 11th house — the house of gains — is a very favourable transit. Expect
    #     support from friends, good news and the fruit of earlier effort. A good day for
    #     networking, making requests and celebrating with others.
    11: "चंद्र तुमच्या अकराव्या भावात — लाभाच्या भावात — असणे हे अतिशय अनुकूल गोचर आहे. मित्रांकडून साथ, चांगली बातमी आणि आधीच्या प्रयत्नांचे फळ अपेक्षित आहे. ओळखी वाढवण्यासाठी, विनंती करण्यासाठी आणि इतरांसोबत आनंद साजरा करण्यासाठी चांगला दिवस.",
    # EN: The Moon in your 12th house can bring extra expenses and a tired, inward mood. Avoid
    #     overspending and late nights; the day suits rest, prayer, charity and finishing old work
    #     rather than starting new.
    12: "चंद्र तुमच्या बाराव्या भावात असल्यास अतिरिक्त खर्च आणि थकलेली, अंतर्मुख मनःस्थिती येऊ शकते. अतिखर्च आणि जागरणे टाळा; नवीन सुरू करण्यापेक्षा विश्रांती, प्रार्थना, दान आणि जुनी कामे संपवणे या दिवसाला जास्त शोभते.",
}

# app/rashifal_text.py SATURN_HOUSE["mr"] — Saturn transit through houses 1-12  [12]
RASHIFAL_SATURN_HOUSE = {
    # EN: Saturn is passing over your Moon sign — the peak phase of Sade Sati. It rewards patience,
    #     routine and honest effort; take on a little less and finish what you start.
    1: "शनी तुमच्या चंद्र राशीवरून जात आहे — साडेसातीचा शिखर टप्पा. संयम, नियमित दिनक्रम आणि प्रामाणिक प्रयत्नांना याचे फळ मिळते; थोडे कमी हाती घ्या आणि सुरू केलेले पूर्ण करा.",
    # EN: Saturn is in your 2nd — the last phase of Sade Sati. Be measured with spending and with
    #     words at home; the pressure is easing.
    2: "शनी तुमच्या दुसऱ्या भावात आहे — साडेसातीचा शेवटचा टप्पा. खर्चात आणि घरातील बोलण्यात संयम ठेवा; दबाव कमी होत आहे.",
    # EN: Saturn in your 3rd is one of its best positions — steady effort pays, courage grows and
    #     long-running work gains traction.
    3: "शनी तिसऱ्या भावात असणे ही त्याची सर्वोत्तम स्थितींपैकी एक आहे — सातत्यपूर्ण प्रयत्नांना फळ मिळते, धैर्य वाढते आणि बऱ्याच काळापासून चाललेल्या कामाला गती येते.",
    # EN: Saturn in your 4th (Dhaiya, Kantaka Shani) can make home life and peace of mind feel
    #     heavier; keep routines simple and handle family matters calmly.
    4: "शनी तुमच्या चौथ्या भावात (ढैया, कंटक शनी) असल्यास घरचे जीवन आणि मनःशांती जड वाटू शकते; दिनक्रम साधा ठेवा आणि कौटुंबिक बाबी शांतपणे हाताळा.",
    # EN: Saturn in your 5th asks for patience with plans, studies and children's matters — slow and
    #     careful beats quick.
    5: "शनी पाचव्या भावात असल्यास योजना, अभ्यास आणि मुलांच्या बाबतीत संयम ठेवावा लागतो — घाईपेक्षा सावकाश आणि काळजीपूर्वक केलेले काम उजवे ठरते.",
    # EN: Saturn in your 6th works in your favour — discipline wins over rivals and backlog, and
    #     hard work gets noticed.
    6: "शनी सहाव्या भावात असणे तुमच्या बाजूने काम करते — शिस्तीमुळे शत्रू आणि साचलेल्या कामांवर मात होते आणि मेहनतीची दखल घेतली जाते.",
    # EN: Saturn in your 7th puts partnerships in a slow, serious light — clear agreements and
    #     patience help.
    7: "शनी सातव्या भावात असल्यास भागीदारी संथ आणि गंभीर स्वरूपात दिसते — स्पष्ट करार आणि संयम उपयोगी ठरतात.",
    # EN: Saturn in your 8th (Dhaiya, Ashtama Shani) is a time to avoid shortcuts and keep a margin
    #     for delays.
    8: "शनी आठव्या भावात (ढैया, अष्टम शनी) असताना शॉर्टकट टाळण्याची आणि विलंबासाठी थोडी मोकळीक ठेवण्याची वेळ असते.",
    # EN: Saturn in your 9th can slow luck and long journeys; respect for elders and steady duty
    #     keep things on track.
    9: "शनी नवव्या भावात असल्यास भाग्य आणि लांबचे प्रवास मंदावू शकतात; वडीलधाऱ्यांचा आदर आणि कर्तव्यातील सातत्य गोष्टी मार्गावर ठेवतात.",
    # EN: Saturn in your 10th brings responsibility at work — a heavier load, but sincere effort
    #     builds a lasting reputation.
    10: "शनी दहाव्या भावात असल्यास कामाच्या ठिकाणी जबाबदारी येते — भार जास्त, पण प्रामाणिक प्रयत्न टिकणारी प्रतिष्ठा घडवतात.",
    # EN: Saturn in your 11th is favourable — gains come slowly but surely, and long effort starts
    #     to pay off.
    11: "शनी अकराव्या भावात असणे अनुकूल आहे — लाभ हळूहळू पण खात्रीने मिळतात, आणि दीर्घ प्रयत्नांचे फळ दिसू लागते.",
    # EN: Saturn is in your 12th — the opening phase of Sade Sati. Watch expenses and rest well; a
    #     good time for quiet, inward work.
    12: "शनी तुमच्या बाराव्या भावात आहे — साडेसातीचा पहिला टप्पा. खर्चावर लक्ष ठेवा आणि नीट विश्रांती घ्या; शांत, अंतर्मुख कामासाठी चांगला काळ.",
}

# app/rashifal_text.py JUPITER_HOUSE["mr"] — Jupiter transit through houses 1-12  [12]
RASHIFAL_JUPITER_HOUSE = {
    # EN: Jupiter over your Moon sign is classically a restless position; keep plans grounded and
    #     avoid over-committing.
    1: "गुरू तुमच्या चंद्र राशीवर असणे शास्त्रानुसार अस्थिरता आणणारे असते; योजना वास्तववादी ठेवा आणि जास्त वचने देऊ नका.",
    # EN: Jupiter in your 2nd supports family harmony, savings and kind speech.
    2: "गुरू दुसऱ्या भावात असल्यास कौटुंबिक सलोखा, बचत आणि गोड बोलण्याला बळ मिळते.",
    # EN: Jupiter in your 3rd asks a little more effort for the same result — keep at it.
    3: "गुरू तिसऱ्या भावात असल्यास तेवढ्याच निकालासाठी थोडे जास्त प्रयत्न लागतात — चिकाटी ठेवा.",
    # EN: Jupiter in your 4th can unsettle home matters; patience with relatives helps.
    4: "गुरू चौथ्या भावात असल्यास घरचे प्रश्न अस्वस्थ करू शकतात; नातेवाइकांशी संयमाने वागा.",
    # EN: Jupiter in your 5th favours learning, children's matters, creativity and good counsel.
    5: "गुरू पाचव्या भावात असल्यास शिक्षण, मुलांच्या बाबी, सर्जनशीलता आणि चांगला सल्ला यांना अनुकूलता मिळते.",
    # EN: Jupiter in your 6th: steer clear of small disputes and overwork.
    6: "गुरू सहाव्या भावात असल्यास लहान वाद आणि अतिश्रम टाळा.",
    # EN: Jupiter in your 7th blesses partnerships, marriage talks and travel.
    7: "गुरू सातव्या भावात असल्यास भागीदारी, विवाहाच्या बोलण्या आणि प्रवासाला आशीर्वाद लाभतात.",
    # EN: Jupiter in your 8th suggests care with big decisions — go slow.
    8: "गुरू आठव्या भावात असल्यास मोठ्या निर्णयांबाबत काळजी घ्या — सावकाश चला.",
    # EN: Jupiter in your 9th is one of its best positions — fortune, dharma and guidance from
    #     teachers.
    9: "गुरू नवव्या भावात असणे ही त्याची सर्वोत्तम स्थितींपैकी एक आहे — भाग्य, धर्म आणि गुरुजनांचे मार्गदर्शन.",
    # EN: Jupiter in your 10th may bring changes at work; stay adaptable.
    10: "गुरू दहाव्या भावात असल्यास कामात बदल होऊ शकतात; लवचिक राहा.",
    # EN: Jupiter in your 11th brings gains, fulfilled wishes and helpful friends.
    11: "गुरू अकराव्या भावात असल्यास लाभ, इच्छापूर्ती आणि मदत करणारे मित्र मिळतात.",
    # EN: Jupiter in your 12th brings expenses, often on good causes; charity and spiritual practice
    #     are well placed.
    12: "गुरू बाराव्या भावात असल्यास खर्च होतो, बहुधा चांगल्या कारणांसाठी; दान आणि आध्यात्मिक साधना यांना हा काळ योग्य आहे.",
}

# app/rashifal_text.py RAHU_HOUSE["mr"] — Rahu transit through houses 1-12  [12]
RASHIFAL_RAHU_HOUSE = {
    # EN: Rahu over your Moon sign can stir restlessness and unusual wants; stay grounded.
    1: "राहू तुमच्या चंद्र राशीवर असल्यास अस्वस्थता आणि विचित्र इच्छा जागृत होऊ शकतात; पाय जमिनीवर ठेवा.",
    # EN: Rahu in your 2nd: take care with speech and money talk within the family.
    2: "राहू दुसऱ्या भावात असल्यास कुटुंबात बोलण्यावर आणि पैशांच्या चर्चेवर लक्ष ठेवा.",
    # EN: Rahu in your 3rd is favourable — bold initiatives and communication succeed.
    3: "राहू तिसऱ्या भावात असणे अनुकूल आहे — धाडसी पुढाकार आणि संवाद यशस्वी होतात.",
    # EN: Rahu in your 4th can unsettle domestic peace; avoid hasty property moves.
    4: "राहू चौथ्या भावात असल्यास घरची शांतता बिघडू शकते; मालमत्तेचे घाईचे व्यवहार टाळा.",
    # EN: Rahu in your 5th: double-check risky ideas and keep a clear head.
    5: "राहू पाचव्या भावात असल्यास जोखमीच्या कल्पना पुन्हा तपासा आणि डोके शांत ठेवा.",
    # EN: Rahu in your 6th helps you get past competition and obstacles.
    6: "राहू सहाव्या भावात असल्यास स्पर्धा आणि अडथळ्यांवर मात करायला मदत होते.",
    # EN: Rahu in your 7th: keep partnerships transparent.
    7: "राहू सातव्या भावात असल्यास भागीदारी पारदर्शक ठेवा.",
    # EN: Rahu in your 8th: avoid risky shortcuts and stay calm when the unexpected comes.
    8: "राहू आठव्या भावात असल्यास जोखमीचे शॉर्टकट टाळा आणि अनपेक्षित घडले तरी शांत राहा.",
    # EN: Rahu in your 9th can raise doubts about beliefs or mentors; seek advice you trust.
    9: "राहू नवव्या भावात असल्यास श्रद्धा किंवा मार्गदर्शकांबद्दल शंका येऊ शकतात; विश्वासार्ह सल्ला घ्या.",
    # EN: Rahu in your 10th brings ambition and sudden openings at work; move with integrity.
    10: "राहू दहाव्या भावात असल्यास महत्त्वाकांक्षा आणि कामात अचानक संधी येतात; प्रामाणिकपणे पुढे जा.",
    # EN: Rahu in your 11th — gains through networks and new contacts.
    11: "राहू अकराव्या भावात असल्यास ओळखी आणि नवीन संपर्कांमधून लाभ होतो.",
    # EN: Rahu in your 12th: watch hidden expenses and get proper rest.
    12: "राहू बाराव्या भावात असल्यास छुप्या खर्चांवर लक्ष ठेवा आणि नीट विश्रांती घ्या.",
}

# app/rashifal_text.py KETU_LINE["mr"] — Ketu line, True = favourable house, False = quiet house; {n} is the house  [2]
RASHIFAL_KETU_LINE = {
    # EN: Ketu in your {n} house works quietly in your favour — obstacles clear with less fuss.
    # keep: {n}
    True: "केतू तुमच्या {n} भावात शांतपणे तुमच्या बाजूने काम करतो — अडथळे फारसा गाजावाजा न करता दूर होतात.",
    # EN: Ketu in your {n} house is a quieter, inward influence — good for reflection and spiritual
    #     practice, less so for impulsive moves.
    # keep: {n}
    False: "केतू तुमच्या {n} भावात शांत, अंतर्मुख करणारा प्रभाव टाकतो — चिंतन आणि आध्यात्मिक साधनेसाठी चांगला, आवेगी कृतींसाठी कमी.",
}

# app/rashifal_text.py CLOCK_LANG["mr"] — leave '' (the language's own clock words); 'en' prints 6:29 AM as Hindi pages do
# (optional: may stay empty)
RASHIFAL_CLOCK_LANG = ""

# ----------------------------------------------------------------------------
# vrat      /vrat-tyohar /ekadashi-<year> /tyohar/<slug>-<year>
# ----------------------------------------------------------------------------

# app/vrat_text.py TEXT["mr"] — page text of /vrat-tyohar, /ekadashi-<year>, /tyohar/<slug>-<year>  [64]
VRAT_TEXT = {
    # EN: Vrat & festivals
    "crumb": "व्रते आणि सण",
    # EN: {date}, {weekday}
    # keep: {date} {weekday}
    "day_label": "{date}, {weekday}",
    # EN: {label}: {prefix}{value}
    # keep: {label} {prefix} {value}
    "timing": "{label}: {prefix}{value}",
    # EN: {paksha} {name}: {start} to {end}
    # keep: {end} {name} {paksha} {start}
    "tithi.text": "{paksha} {name}: {start} ते {end}",
    # EN: {paksha}
    # keep: {paksha}
    "tithi.paksha": "{paksha} पक्ष",
    # EN: <tr><th>Date</th><th>Vrat / festival</th><th>Timing ({city})</th></tr>
    # keep: {city}
    "table.th": "<tr><th>तारीख</th><th>व्रत / सण</th><th>वेळ ({city})</th></tr>",
    # EN: <div class="box"><p><strong>Timings vary by city.</strong> Every time here is for {city}'s
    #     sunrise, sunset and moonrise; in another city they shift by a few minutes and occasionally
    #     the date does too. Dates follow Drik Panchang's Smarta (default) reckoning. Check the
    #     Panchang for your own city.</p></div>
    # keep: {city}
    "city_note": "<div class=\"box\"><p><strong>वेळा शहरानुसार बदलतात.</strong> येथील प्रत्येक वेळ {city} मधील सूर्योदय, सूर्यास्त आणि चंद्रोदयानुसार आहे; दुसऱ्या शहरात त्या काही मिनिटांनी बदलतात आणि कधीकधी तारीखही बदलते. तारखा दृक पंचांगाच्या स्मार्त (डीफॉल्ट) गणनेनुसार आहेत. तुमच्या स्वतःच्या शहराचे पंचांग पाहा.</p></div>",
    # EN: <p class="note"><small>For most observances the date is the same across India, but puja
    #     muhurat, parana and moonrise times differ from city to city - every time here is for
    #     <strong>{city}</strong>. Regional traditions may vary.</small></p>
    # keep: {city}
    "top_note": "<p class=\"note\"><small>बहुतेक व्रतांची आणि सणांची तारीख भारतभर सारखीच असते, पण पूजेचा मुहूर्त, पारणे आणि चंद्रोदयाच्या वेळा शहरानुसार वेगळ्या असतात — येथील प्रत्येक वेळ <strong>{city}</strong> साठी आहे. प्रादेशिक परंपरांनुसार फरक असू शकतो.</small></p>",
    # EN: Vrat & festivals in your city
    "cities.heading": "तुमच्या शहरातील व्रते आणि सण",
    # EN: Today's Panchang in {city}
    # keep: {city}
    "tools.panchang": "{city} मधील आजचे पंचांग",
    # EN: Rahu Kaal in {city}
    # keep: {city}
    # may also use: {t_rahu_kaal}
    "tools.rahu": "{city} मधील राहुकाळ",
    # EN: More for {city}
    # keep: {city}
    "tools.heading": "{city} साठी आणखी",
    # EN: See the Panchang for your city — free
    "cta": "तुमच्या शहराचे पंचांग पाहा — मोफत",
    # EN: Today's vrat & festivals
    "more.today": "आजची व्रते आणि सण",
    # EN: Festival calendar {year}
    # keep: {year}
    "more.year": "सण-उत्सव दिनदर्शिका {year}",
    # EN: Ekadashi {year}
    # keep: {year}
    "more.ekadashi": "एकादशी {year}",
    # EN: Today's Panchang
    "more.panchang": "आजचे पंचांग",
    # EN: Today's Rashifal
    "more.rashifal": "आजचे राशिभविष्य",
    # EN: More
    "more.heading": "आणखी",
    # EN: Major festivals {year}
    # keep: {year}
    "majors.heading": "प्रमुख सण {year}",
    # EN: Rule
    "today.rule": "नियम",
    # EN: No major vrat or festival today.
    "today.none": "आज कोणतेही प्रमुख व्रत किंवा सण नाही.",
    # EN: Next: <strong>{name}</strong> on {day}.
    # keep: {day} {name}
    "today.next": " पुढील: <strong>{name}</strong>, {day}.",
    # EN: Vrat &amp; Festivals today
    "block.heading": "आजची व्रते आणि सण",
    # EN: Page not found
    "nf.h1": "पान सापडले नाही",
    # EN: Aaj Ke Vrat aur Tyohar: Today's Vrat & Festivals ({date})
    # keep: {date}
    "hub.title_default": "आजची व्रते आणि सण: आजचे उपवास व सण ({date})",
    # EN: Today's Vrat & Festivals in {city} ({date}) - Aaj Ke Vrat
    # keep: {city} {date}
    "hub.title_city": "{city} मधील आजची व्रते आणि सण ({date}) - आजचे व्रत",
    # EN: Today's vrat & festivals
    "hub.h1_default": "आजची व्रते आणि सण",
    # EN: Today's vrat & festivals in {city}
    # keep: {city}
    "hub.h1_city": "{city} मधील आजची व्रते आणि सण",
    # EN: Today, {date}: {names}.
    # keep: {date} {names}
    "hub.desc_today": "आज, {date}: {names}.",
    # EN: {date}: no major vrat today.
    # keep: {date}
    "hub.desc_none": "{date}: आज कोणतेही प्रमुख व्रत नाही.",
    # EN: Upcoming fasts and festivals for 30 days with Ekadashi parana, Pradosh and Sankashti
    #     moonrise times - {city}.
    # keep: {city}
    "hub.desc_rest": "पुढील 30 दिवसांचे उपवास आणि सण — एकादशी पारणे, प्रदोष आणि संकष्टी चंद्रोदयाच्या वेळांसह - {city}.",
    # EN: <p class="hi" lang="hi">आज के व्रत और त्योहार</p>
    "hub.sub": "<p class=\"hi\">आज कोणते व्रत, कोणता सण</p>",
    # EN: Next 30 days
    "hub.upcoming": "पुढील 30 दिवस",
    # EN: Hindu Festival & Vrat Calendar {year} (New Delhi): Dates and Muhurat
    # keep: {year}
    "year.title": "हिंदू सण आणि व्रत दिनदर्शिका {year} (नवी दिल्ली): तारखा आणि मुहूर्त",
    # EN: Vrat & festival calendar {year}
    # keep: {year}
    "year.h1": "व्रत आणि सण दिनदर्शिका {year}",
    # EN: Every Hindu vrat and festival of {year}, month by month - Ekadashi, Pradosh, Sankashti,
    #     Purnima, Amavasya, Shivratri and festivals like Diwali, Navratri and Raksha Bandhan, with
    #     puja muhurat for New Delhi.
    # keep: {year}
    "year.desc": "{year} मधील प्रत्येक हिंदू व्रत आणि सण, महिन्यानुसार - एकादशी, प्रदोष, संकष्टी, पौर्णिमा, अमावस्या, शिवरात्री आणि दिवाळी, नवरात्र, रक्षाबंधन यांसारखे सण, नवी दिल्लीसाठी पूजा मुहूर्तासह.",
    # EN: <p><strong>{count}</strong> fasts and festivals in {year} for New Delhi, computed from the
    #     panchang. Tap a major festival for its puja muhurat and what it is about.</p>
    # keep: {count} {year}
    "year.intro": "<p>नवी दिल्लीसाठी {year} मधील <strong>{count}</strong> उपवास आणि सण, पंचांगावरून काढलेले. पूजा मुहूर्त आणि त्याविषयी माहिती पाहण्यासाठी एखाद्या प्रमुख सणावर टॅप करा.</p>",
    # EN: {month} {year}
    # keep: {month} {year}
    "year.month": "{month} {year}",
    # EN: Major Hindu festivals {year}
    # keep: {year}
    "year.itemlist": "प्रमुख हिंदू सण {year}",
    # EN: Ekadashi {year}: All Ekadashi Vrat Dates and Parana Time (New Delhi)
    # keep: {year}
    "ek.title": "एकादशी {year}: सर्व एकादशी व्रताच्या तारखा आणि पारणे वेळ (नवी दिल्ली)",
    # EN: Ekadashi {year}: dates and parana time
    # keep: {year}
    "ek.h1": "एकादशी {year}: तारखा आणि पारणे वेळ",
    # EN: All {count} Ekadashis of {year} - fasting date, Ekadashi tithi times and the parana (fast-
    #     breaking) window next day, for New Delhi.
    # keep: {count} {year}
    "ek.desc": "{year} मधील सर्व {count} एकादशी - उपवासाची तारीख, एकादशी तिथीच्या वेळा आणि दुसऱ्या दिवशीचा पारणे (उपवास सोडण्याचा) कालावधी, नवी दिल्लीसाठी.",
    # EN: <tr><th>Ekadashi</th><th>Fast</th><th>Parana</th></tr>
    "ek.th": "<tr><th>एकादशी</th><th>उपवास</th><th>पारणे</th></tr>",
    # EN: <p><strong>Rule (Smarta):</strong> fast on the day Ekadashi prevails at sunrise; if it
    #     prevails at two sunrises, the second day, and if at none, the day it falls in. Parana is
    #     the next day after sunrise, once Hari Vasara (the first quarter of Dwadashi) is over,
    #     within Pratahkala and before Dwadashi ends; if Hari Vasara runs past Pratahkala, parana
    #     moves to Aparahna (Madhyahna is avoided).</p>
    "ek.rule": "<p><strong>नियम (स्मार्त):</strong> सूर्योदयाच्या वेळी जी एकादशी असते त्या दिवशी उपवास करावा; ती दोन सूर्योदयांना असल्यास दुसऱ्या दिवशी, आणि एकाही सूर्योदयाला नसल्यास ज्या दिवशी ती येते त्या दिवशी. पारणे दुसऱ्या दिवशी सूर्योदयानंतर, हरिवासर (द्वादशीचा पहिला चतुर्थांश) संपल्यावर, प्रातःकाळात आणि द्वादशी संपण्यापूर्वी करावे; हरिवासर प्रातःकाळाच्या पुढे गेल्यास पारणे अपराह्नात होते (मध्याह्न टाळला जातो).</p>",
    # EN: <p class="hi" lang="hi">एकादशी {year}</p>
    # keep: {year}
    "ek.sub": "<p class=\"hi\">एकादशी व्रत {year}</p>",
    # EN: Ekadashi {year}
    # keep: {year}
    "ek.crumb": "एकादशी {year}",
    # EN: {name} {year}: Date and Puja Muhurat - {short}
    # keep: {name} {short} {year}
    "fest.title": "{name} {year}: तारीख आणि पूजा मुहूर्त - {short}",
    # EN: {name} {year}: date and muhurat
    # keep: {name} {year}
    "fest.h1": "{name} {year}: तारीख आणि मुहूर्त",
    # EN: {text}.
    # keep: {text}
    "fest.main": "{text}. ",
    # EN: {name} {year} is on {weekday}, {date}. {main}Puja timings for New Delhi.
    # keep: {date} {main} {name} {weekday} {year}
    "fest.desc": "{name} {year} {weekday}, {date} रोजी आहे. {main}नवी दिल्लीसाठी पूजेच्या वेळा.",
    # EN: {name} {year} is on <strong>{when}</strong>.
    # keep: {name} {when} {year}
    "fest.when": "{name} {year} <strong>{when}</strong> रोजी आहे.",
    # EN: <p class="hi" lang="hi">{name_hi} {year}</p>
    # keep: {year}
    "fest.sub": "<p class=\"hi\">तिथी, शुभ मुहूर्त आणि पूजेच्या वेळा · {year}</p>",
    # EN: What it is and how it is observed
    "fest.about_h2": "हे काय आहे आणि कसे पाळले जाते",
    # EN: How the date is fixed
    "fest.rule_h2": "तारीख कशी ठरते",
    # EN: Frequently asked questions
    "fest.faq_h2": "नेहमी विचारले जाणारे प्रश्न",
    # EN: India
    "event.place": "भारत",
    # EN: When is {name} {year}?
    # keep: {name} {year}
    "faq.when_q": "{name} {year} केव्हा आहे?",
    # EN: {name} {year} is on {weekday}, {date}.
    # keep: {date} {name} {weekday} {year}
    "faq.when_a": "{name} {year} {weekday}, {date} रोजी आहे.",
    # EN: What is the {name} {year} puja muhurat?
    # keep: {name} {year}
    "faq.muhurat_q": "{name} {year} चा पूजा मुहूर्त कोणता?",
    # EN: What are the {name} {year} timings?
    # keep: {name} {year}
    "faq.timings_q": "{name} {year} च्या वेळा कोणत्या?",
    # EN: For New Delhi - {timings}. Timings vary by city by a few minutes; check the Panchang for
    #     your city.
    # keep: {timings}
    "faq.timings_a": "नवी दिल्लीसाठी - {timings}. वेळा शहरानुसार काही मिनिटांनी बदलतात; तुमच्या शहराचे पंचांग पाहा.",
    # EN: Why is {name} {year} observed on {short}?
    # keep: {name} {short} {year}
    "faq.why_q": "{name} {year} हे {short} रोजी का आहे?",
    # EN: The date follows the rule: {rule}. In {year} that is {when} (New Delhi).
    # keep: {rule} {when} {year}
    "faq.why_a": "तारीख या नियमानुसार ठरते: {rule}. {year} मध्ये ती {when} रोजी येते (नवी दिल्ली).",
}

# app/vrat_text.py ABOUT["mr"] — what each of the 47 festivals / vrats is (key = festival slug)  [47]
VRAT_ABOUT = {
    # EN: Makar Sankranti marks the Sun's entry into Makara (Capricorn) and the start of its
    #     northward journey (Uttarayana). It is a harvest festival: people bathe in holy rivers,
    #     give til (sesame), jaggery, khichdi and blankets in charity, and fly kites.
    "makar-sankranti": "मकर संक्रांत म्हणजे सूर्याचा मकर राशीत प्रवेश आणि त्याच्या उत्तरेकडील प्रवासाचा (उत्तरायणाचा) आरंभ. हा कापणीचा सण आहे: लोक पवित्र नद्यांत स्नान करतात, तीळ, गूळ, खिचडी आणि ब्लँकेट दान करतात आणि पतंग उडवतात.",
    # EN: Maha Shivratri, the great night of Shiva, falls on the Krishna Chaturdashi of Magha.
    #     Devotees fast, offer water, milk and bel leaves on the Shivling, chant Om Namah Shivaya
    #     and keep vigil through the four prahars of the night; the Nishita kaal puja around
    #     midnight is the most important.
    "maha-shivratri": "महाशिवरात्री, शिवाची महान रात्र, माघ कृष्ण चतुर्दशीला येते. भाविक उपवास करतात, शिवलिंगावर पाणी, दूध आणि बेलपत्र वाहतात, ‘ओम नमः शिवाय’चा जप करतात आणि रात्रीच्या चारही प्रहरांत जागरण करतात; मध्यरात्रीच्या सुमारास होणारी निशीथ काळातील पूजा सर्वांत महत्त्वाची मानली जाते.",
    # EN: Holika Dahan, on the eve of Holi, celebrates Prahlad's devotion and the victory of good
    #     over evil. A bonfire is lit after sunset, avoiding Bhadra, and families circle it offering
    #     grain, coconut and prayers.
    "holika-dahan": "होळीच्या आदल्या रात्री होणारे होलिका दहन प्रल्हादाची भक्ती आणि वाईटावर चांगल्याचा विजय साजरा करते. सूर्यास्तानंतर, भद्रा टाळून, होळी पेटवली जाते आणि कुटुंबे तिच्याभोवती फिरून धान्य, नारळ अर्पण करतात आणि प्रार्थना करतात.",
    # EN: Holi, the festival of colours, is celebrated the morning after Holika Dahan with colours,
    #     music, sweets like gujiya and visits to family and friends.
    "holi": "होळी, रंगांचा सण, होलिका दहनाच्या दुसऱ्या दिवशी सकाळी रंग, संगीत, गुजियासारखी मिठाई आणि कुटुंबीय-मित्रांच्या भेटींनी साजरा केला जातो.",
    # EN: Ram Navami celebrates the birth of Lord Rama on Chaitra Shukla Navami, at midday. Devotees
    #     fast, read the Ramcharitmanas, and offer puja in the Madhyahna muhurat, the time of his
    #     birth.
    "ram-navami": "रामनवमी चैत्र शुक्ल नवमीला दुपारी होणाऱ्या भगवान रामाच्या जन्माचा उत्सव आहे. भाविक उपवास करतात, रामचरितमानस वाचतात आणि त्यांच्या जन्माच्या वेळी, म्हणजे मध्याह्न मुहूर्तावर, पूजा करतात.",
    # EN: Hanuman Jayanti (Chaitra Purnima in North India) celebrates the birth of Lord Hanuman.
    #     Devotees visit Hanuman temples, recite the Hanuman Chalisa and Sundarkand, and offer
    #     sindoor and laddoos.
    "hanuman-jayanti": "हनुमान जयंती (उत्तर भारतात चैत्र पौर्णिमेला) भगवान हनुमानाच्या जन्माचा उत्सव आहे. भाविक हनुमान मंदिरांत जातात, हनुमान चालीसा आणि सुंदरकांडाचे पठण करतात आणि शेंदूर व लाडू अर्पण करतात.",
    # EN: Akshaya Tritiya, Vaishakha Shukla Tritiya, is held to make every good deed 'akshaya' -
    #     undiminishing. People worship Vishnu and Lakshmi, give in charity, and begin new ventures
    #     or buy gold.
    "akshaya-tritiya": "अक्षय्य तृतीया, वैशाख शुक्ल तृतीया, प्रत्येक शुभ कर्म ‘अक्षय्य’ — कधीही न संपणारे — करते असे मानले जाते. लोक विष्णू आणि लक्ष्मीची पूजा करतात, दान देतात आणि नवीन उपक्रम सुरू करतात किंवा सोने खरेदी करतात.",
    # EN: Raksha Bandhan, on Shravana Purnima, celebrates the bond between brothers and sisters.
    #     Sisters tie a rakhi on their brother's wrist and pray for his well-being; the rakhi is
    #     tied in a time free of Bhadra.
    "raksha-bandhan": "रक्षाबंधन, श्रावण पौर्णिमेला, भाऊ-बहिणीच्या नात्याचा उत्सव आहे. बहिणी भावाच्या मनगटावर राखी बांधतात आणि त्याच्या कल्याणासाठी प्रार्थना करतात; राखी भद्रामुक्त वेळेत बांधली जाते.",
    # EN: Krishna Janmashtami celebrates the birth of Lord Krishna at midnight on Krishna Ashtami of
    #     Bhadrapada (purnimanta). Devotees fast through the day and break it after the Nishita
    #     (midnight) puja, when the infant Krishna is bathed and placed in a cradle.
    "janmashtami": "श्रीकृष्ण जन्माष्टमी भाद्रपद (पौर्णिमांत) कृष्ण अष्टमीला मध्यरात्री झालेल्या भगवान श्रीकृष्णाच्या जन्माचा उत्सव आहे. भाविक दिवसभर उपवास करतात आणि निशीथ (मध्यरात्रीच्या) पूजेनंतर तो सोडतात, तेव्हा बाळकृष्णाला स्नान घालून पाळण्यात ठेवले जाते.",
    # EN: Ganesh Chaturthi, Bhadrapada Shukla Chaturthi, welcomes Lord Ganesha home. The idol is
    #     installed and worshipped in the Madhyahna (midday) muhurat, the time of his birth, with
    #     modak, durva grass and red flowers; looking at the Moon on this day is avoided.
    "ganesh-chaturthi": "गणेश चतुर्थी, भाद्रपद शुक्ल चतुर्थी, भगवान गणेशाचे घरी स्वागत करते. मूर्तीची प्रतिष्ठापना करून मोदक, दूर्वा आणि लाल फुलांनी मध्याह्न (दुपारच्या) मुहूर्तावर, म्हणजे त्यांच्या जन्माच्या वेळी, पूजा केली जाते; या दिवशी चंद्र पाहणे टाळले जाते.",
    # EN: Chaitra Navratri, the nine nights of Goddess Durga in spring, begins on Chaitra Shukla
    #     Pratipada - also the Hindu New Year (Vikram Samvat). Ghatasthapana (installing the kalash)
    #     opens the nine days of worship.
    "chaitra-navratri": "चैत्र नवरात्र, वसंत ऋतूतील देवी दुर्गेच्या नऊ रात्री, चैत्र शुक्ल प्रतिपदेला सुरू होते — हाच हिंदू नववर्षाचा (विक्रम संवत) दिवसही आहे. घटस्थापनेने (कलश बसवून) नऊ दिवसांच्या पूजेला प्रारंभ होतो.",
    # EN: Sharad Navratri, the nine nights of Goddess Durga in autumn, begins on Ashwin Shukla
    #     Pratipada with Ghatasthapana - installing the kalash and sowing barley - in the morning.
    #     Each day honours one of the nine forms of the Goddess.
    "navratri": "शारदीय नवरात्र, शरद ऋतूतील देवी दुर्गेच्या नऊ रात्री, आश्विन शुक्ल प्रतिपदेला सकाळी घटस्थापनेने — कलश बसवून आणि जव पेरून — सुरू होते. प्रत्येक दिवशी देवीच्या नऊ रूपांपैकी एका रूपाचा सन्मान केला जातो.",
    # EN: Dussehra (Vijayadashami) marks Lord Rama's victory over Ravana and Goddess Durga's over
    #     Mahishasura. Shami puja, Aparajita puja and the burning of Ravana effigies are held in the
    #     afternoon; the Vijay muhurat is considered good for starting anything new.
    "dussehra": "दसरा (विजयादशमी) भगवान रामाचा रावणावरील आणि देवी दुर्गेचा महिषासुरावरील विजय साजरा करतो. दुपारी शमीपूजन, अपराजिता पूजन आणि रावण दहन केले जाते; विजय मुहूर्त कोणतीही नवी गोष्ट सुरू करण्यासाठी शुभ मानला जातो.",
    # EN: On Karwa Chauth married women keep a fast from sunrise to moonrise for their husbands'
    #     long life. The evening puja of Karwa Mata is followed by offering water (arghya) to the
    #     Moon, after which the fast is broken.
    "karwa-chauth": "करवा चौथला विवाहित स्त्रिया पतीच्या दीर्घायुष्यासाठी सूर्योदयापासून चंद्रोदयापर्यंत उपवास करतात. संध्याकाळी करवा मातेची पूजा केल्यानंतर चंद्राला अर्घ्य दिले जाते, आणि त्यानंतर उपवास सोडला जातो.",
    # EN: On Ahoi Ashtami, eight days before Diwali, mothers keep a fast for the well-being of their
    #     children and worship Ahoi Mata in the evening; the fast is traditionally broken after
    #     sighting the stars (or, in some families, the Moon).
    "ahoi-ashtami": "दिवाळीच्या आठ दिवस आधी येणाऱ्या अहोई अष्टमीला माता मुलांच्या कल्याणासाठी उपवास करतात आणि संध्याकाळी अहोई मातेची पूजा करतात; परंपरेनुसार तारे दिसल्यानंतर (काही कुटुंबांत चंद्र दिसल्यानंतर) उपवास सोडला जातो.",
    # EN: Dhanteras, the first day of Diwali, honours Dhanvantari and Goddess Lakshmi. People buy
    #     new utensils, gold or silver and light the Yama deepak at dusk; the puja is done in
    #     Pradosh kaal, ideally in the fixed (sthir) Vrishabha lagna.
    "dhanteras": "धनत्रयोदशी, दिवाळीचा पहिला दिवस, धन्वंतरी आणि देवी लक्ष्मीचा सन्मान करते. लोक नवीन भांडी, सोने किंवा चांदी खरेदी करतात आणि सायंकाळी यमदीप लावतात; पूजा प्रदोषकाळात, शक्यतो स्थिर वृषभ लग्नात केली जाते.",
    # EN: Diwali, on Kartika Amavasya, is the festival of lights. Lakshmi and Ganesha are worshipped
    #     in the evening - in Pradosh kaal, preferably in the fixed (sthir) Vrishabha lagna so that
    #     prosperity stays - and homes are lit with diyas.
    "diwali": "दिवाळी, कार्तिक अमावस्येला, दिव्यांचा सण आहे. संध्याकाळी — प्रदोषकाळात, शक्यतो स्थिर वृषभ लग्नात, म्हणजे समृद्धी टिकून राहावी म्हणून — लक्ष्मी आणि गणेशाची पूजा केली जाते आणि घरे पणत्यांनी उजळवली जातात.",
    # EN: Govardhan Puja (Annakut), the day after Diwali, remembers Krishna lifting Govardhan hill.
    #     A Govardhan of cow-dung or food is worshipped and an annakut of many dishes is offered,
    #     usually in the morning (Pratahkala).
    "govardhan-puja": "गोवर्धन पूजा (अन्नकूट), दिवाळीच्या दुसऱ्या दिवशी, कृष्णाने गोवर्धन पर्वत उचलल्याची आठवण करते. शेणाच्या किंवा अन्नाच्या गोवर्धनाची पूजा केली जाते आणि अनेक पदार्थांचा अन्नकूट अर्पण केला जातो, सहसा सकाळी (प्रातःकाळात).",
    # EN: Bhai Dooj, Kartika Shukla Dwitiya, celebrates brothers and sisters: sisters apply a tilak,
    #     perform aarti and pray for their brother's long life, ideally in the Aparahna (afternoon)
    #     time.
    "bhai-dooj": "भाऊबीज, कार्तिक शुक्ल द्वितीया, भाऊ-बहिणींचा उत्सव आहे: बहिणी भावाला टिळा लावतात, ओवाळतात आणि त्याच्या दीर्घायुष्यासाठी प्रार्थना करतात, शक्यतो अपराह्न (दुपारनंतरच्या) वेळेत.",
    # EN: Chhath Puja worships the Sun God and Chhathi Maiya over four days. On the main day
    #     (Kartika Shukla Shashthi) devotees stand in water and offer arghya to the setting Sun, and
    #     to the rising Sun the next morning, ending a fast kept without water.
    "chhath-puja": "छठ पूजा चार दिवस सूर्यदेव आणि छठी मैयाची उपासना करते. मुख्य दिवशी (कार्तिक शुक्ल षष्ठी) भाविक पाण्यात उभे राहून मावळत्या सूर्याला आणि दुसऱ्या दिवशी सकाळी उगवत्या सूर्याला अर्घ्य देतात, आणि निर्जला उपवास संपवतात.",
    # EN: Vasant Panchami, Magha Shukla Panchami, welcomes spring and honours Goddess Saraswati.
    #     Students and artists worship books and instruments, people wear yellow, and children often
    #     begin learning to write (vidyarambh).
    "vasant-panchami": "वसंत पंचमी, माघ शुक्ल पंचमी, वसंत ऋतूचे स्वागत करते आणि देवी सरस्वतीचा सन्मान करते. विद्यार्थी आणि कलावंत पुस्तके व वाद्यांची पूजा करतात, लोक पिवळे कपडे घालतात, आणि मुले अनेकदा लिहायला शिकण्यास सुरुवात करतात (विद्यारंभ).",
    # EN: Guru Purnima, Ashadha Purnima, honours one's teachers and Maharishi Ved Vyasa, born on
    #     this day. Disciples offer gratitude, flowers and gifts to their guru.
    "guru-purnima": "गुरुपौर्णिमा, आषाढ पौर्णिमा, आपल्या गुरूंचा आणि या दिवशी जन्मलेल्या महर्षी वेदव्यासांचा सन्मान करते. शिष्य आपल्या गुरूंना कृतज्ञता, फुले आणि भेटवस्तू अर्पण करतात.",
    # EN: Sharad Purnima, Ashwin Purnima, is the night the Moon is held to be brightest and full of
    #     nectar. Kheer is kept in the moonlight overnight and eaten as prasad; Lakshmi is
    #     worshipped (Kojagari).
    "sharad-purnima": "शरद पौर्णिमा, आश्विन पौर्णिमा, ही अशी रात्र आहे जेव्हा चंद्र सर्वात तेजस्वी आणि अमृताने भरलेला असतो असे मानले जाते. खीर रात्रभर चांदण्यात ठेवून प्रसाद म्हणून खाल्ली जाते; लक्ष्मीची पूजा केली जाते (कोजागरी).",
    # EN: Devuthani (Prabodhini) Ekadashi, Kartika Shukla Ekadashi, is when Lord Vishnu is held to
    #     wake from his four-month sleep, ending Chaturmas. Tulsi vivah begins and the wedding
    #     season opens. Devotees fast and break the fast (parana) the next day.
    "devuthani-ekadashi": "देवउठनी (प्रबोधिनी) एकादशी, कार्तिक शुक्ल एकादशी, या दिवशी भगवान विष्णू चार महिन्यांच्या निद्रेतून जागे होतात असे मानले जाते, आणि चातुर्मास संपतो. तुळशी विवाहाला सुरुवात होते आणि विवाहाचा हंगाम सुरू होतो. भाविक उपवास करतात आणि दुसऱ्या दिवशी पारणे करतात.",
    # EN: Jivitputrika (Jitiya, Jiutiya) is kept by mothers in Bihar, Jharkhand, eastern Uttar
    #     Pradesh and Nepal for the long life and well-being of their children, on Ashwin Krishna
    #     Ashtami (purnimanta). It begins with nahay-khay the day before; the fast itself is
    #     nirjala, without water, through the day and night, with worship of Jimutavahana and the
    #     Jitiya katha. Parana, breaking the fast, is the next morning.
    "jivitputrika": "जीवितपुत्रिका (जितिया, जिउतिया) बिहार, झारखंड, पूर्व उत्तर प्रदेश आणि नेपाळमधील माता मुलांच्या दीर्घायुष्य आणि कल्याणासाठी आश्विन कृष्ण अष्टमीला (पौर्णिमांत) करतात. आदल्या दिवशी नहाय-खाय होऊन व्रताला सुरुवात होते; उपवास स्वतः निर्जला असतो, दिवसरात्र पाण्याशिवाय, त्यात जीमूतवाहनाची पूजा आणि जितिया कथा असते. पारणे दुसऱ्या दिवशी सकाळी होते.",
    # EN: Lohri, the evening before Makar Sankranti, is the winter harvest festival of Punjab and
    #     North India. A bonfire is lit at dusk and people offer til, gur, rewari, peanuts and
    #     popcorn to it, sing and dance; it is especially celebrated for a new bride or a newborn.
    "lohri": "लोहरी, मकर संक्रांतीच्या आदल्या संध्याकाळी, पंजाब आणि उत्तर भारताचा हिवाळी कापणीचा सण आहे. संध्याकाळी होळी पेटवली जाते आणि लोक तीळ, गूळ, रेवडी, शेंगदाणे आणि पॉपकॉर्न अर्पण करतात, गाणी गातात आणि नाचतात; नववधू किंवा नवजात बाळ असलेल्या घरात तो विशेषत्वाने साजरा होतो.",
    # EN: Sakat Chauth (Tilkut Chauth), the Sankashti Chaturthi of Magha (purnimanta), is kept by
    #     mothers for their children. Ganesha and Sakat Mata are worshipped with til and jaggery,
    #     and the fast is broken after offering arghya to the rising Moon.
    "sakat-chauth": "सकट चौथ (तिळकूट चौथ), माघ (पौर्णिमांत) महिन्यातील संकष्टी चतुर्थी, माता मुलांसाठी करतात. तीळ आणि गुळाने गणेश आणि सकट मातेची पूजा केली जाते, आणि उगवत्या चंद्राला अर्घ्य दिल्यानंतर उपवास सोडला जातो.",
    # EN: Mauni Amavasya, the Amavasya of Magha (purnimanta), is the great bathing day of the Magh
    #     Mela at Prayagraj. Devotees bathe in the Ganga or a holy river, keep silence (mauna) and
    #     give in charity.
    "mauni-amavasya": "मौनी अमावस्या, माघ (पौर्णिमांत) महिन्याची अमावस्या, प्रयागराज येथील माघ मेळ्यातील मुख्य स्नानाचा दिवस आहे. भाविक गंगा किंवा एखाद्या पवित्र नदीत स्नान करतात, मौन पाळतात आणि दान देतात.",
    # EN: Sheetala Ashtami (Basoda), Chaitra Krishna Ashtami (purnimanta), honours Sheetala Mata,
    #     the goddess who protects from fevers and pox. Food is cooked the day before and the stale
    #     (basi) food is offered and eaten; no fire is lit for cooking that day.
    "sheetala-ashtami": "शीतला अष्टमी (बसोडा), चैत्र कृष्ण अष्टमी (पौर्णिमांत), ताप आणि कांजिण्यांपासून रक्षण करणाऱ्या शीतला मातेचा सन्मान करते. आदल्या दिवशी अन्न शिजवले जाते आणि शिळे (बासी) अन्न अर्पण करून खाल्ले जाते; त्या दिवशी स्वयंपाकासाठी अग्नी पेटवला जात नाही.",
    # EN: Gudi Padwa (Maharashtra) and Ugadi (Karnataka, Andhra Pradesh, Telangana) mark the lunar
    #     New Year on Chaitra Shukla Pratipada. A gudi - a decorated pole with a cloth and kalash -
    #     is raised at the door, and neem with jaggery is eaten for a year of both sweet and bitter.
    "gudi-padwa": "गुढीपाडवा (महाराष्ट्र) आणि उगादी (कर्नाटक, आंध्र प्रदेश, तेलंगणा) चैत्र शुक्ल प्रतिपदेला चांद्र नववर्ष साजरे करतात. दारात गुढी — कापड आणि कलश लावलेली सजवलेली काठी — उभारली जाते, आणि गोड-कडू अशा संपूर्ण वर्षाचे प्रतीक म्हणून गुळासह कडुनिंब खाल्ला जातो.",
    # EN: Gangaur, Chaitra Shukla Tritiya, is Rajasthan's festival of Gauri (Parvati) and Shiva.
    #     Women worship Gauri for marital happiness - married women for their husbands, girls for a
    #     good match - ending eighteen days of puja that begin the day after Holi.
    "gangaur": "गणगौर, चैत्र शुक्ल तृतीया, गौरी (पार्वती) आणि शिव यांचा राजस्थानचा सण आहे. स्त्रिया वैवाहिक सुखासाठी गौरीची पूजा करतात — विवाहित स्त्रिया पतीसाठी, मुली चांगल्या वराच्या प्राप्तीसाठी — होळीच्या दुसऱ्या दिवशी सुरू होणाऱ्या अठरा दिवसांच्या पूजेची यादिवशी सांगता होते.",
    # EN: Vat Savitri Vrat, on Jyeshtha Amavasya in North India (purnimanta), remembers Savitri, who
    #     won back her husband Satyavan's life from Yama. Married women fast, worship the banyan
    #     (vat) tree, tie raw thread around it while circling it, and hear the Savitri katha.
    "vat-savitri": "वटसावित्री व्रत, उत्तर भारतात ज्येष्ठ अमावस्येला (पौर्णिमांत), पती सत्यवानाचे प्राण यमाकडून परत मिळवणाऱ्या सावित्रीचे स्मरण करते. विवाहित स्त्रिया उपवास करतात, वडाच्या झाडाची पूजा करतात, त्याला प्रदक्षिणा घालत कच्चा धागा गुंडाळतात आणि सावित्रीची कथा ऐकतात.",
    # EN: Vat Purnima is the same Vat Savitri vrat as kept on Jyeshtha Purnima in Maharashtra,
    #     Gujarat and the south (amanta calendar), fifteen days after the North Indian date. Married
    #     women fast and worship the banyan tree for their husbands' long life.
    "vat-purnima": "वटपौर्णिमा हेच वटसावित्री व्रत महाराष्ट्र, गुजरात आणि दक्षिणेत ज्येष्ठ पौर्णिमेला (अमांत पंचांगानुसार), उत्तर भारतातील तारखेनंतर पंधरा दिवसांनी, केले जाते. विवाहित स्त्रिया पतीच्या दीर्घायुष्यासाठी उपवास करतात आणि वडाच्या झाडाची पूजा करतात.",
    # EN: Ganga Dussehra, Jyeshtha Shukla Dashami, celebrates the descent of the Ganga to earth
    #     through Bhagiratha's penance. Devotees bathe in the Ganga, offer lamps and give in
    #     charity; the bath is held to wash away ten kinds of sin.
    "ganga-dussehra": "गंगा दशहरा, ज्येष्ठ शुक्ल दशमी, भगीरथाच्या तपश्चर्येमुळे गंगा पृथ्वीवर अवतरल्याचा उत्सव आहे. भाविक गंगेत स्नान करतात, दीप अर्पण करतात आणि दान देतात; या स्नानाने दहा प्रकारची पापे धुतली जातात असे मानले जाते.",
    # EN: Hariyali Teej, Shravana Shukla Tritiya, celebrates the reunion of Shiva and Parvati in the
    #     monsoon. Women wear green, apply mehndi, swing on decorated jhoolas, sing Sawan songs and
    #     many keep a fast for their husbands.
    "hariyali-teej": "हरियाली तीज, श्रावण शुक्ल तृतीया, पावसाळ्यात शिव आणि पार्वतीच्या पुनर्मिलनाचा उत्सव आहे. स्त्रिया हिरवे कपडे घालतात, मेंदी लावतात, सजवलेल्या झुल्यांवर झोके घेतात, सावनची गाणी गातात आणि अनेकजणी पतीसाठी उपवास करतात.",
    # EN: Nag Panchami, Shravana Shukla Panchami, is the day serpent deities (nagas) are worshipped.
    #     Images of snakes are drawn or installed and offered milk, flowers and sweets, with prayers
    #     for the family's protection. (In Gujarat, Nag Pancham falls later, in Bhadrapada.)
    "nag-panchami": "नागपंचमी, श्रावण शुक्ल पंचमी, या दिवशी नागदेवतांची पूजा केली जाते. सापांची चित्रे काढली किंवा प्रतिमा बसवल्या जातात आणि त्यांना दूध, फुले व मिठाई अर्पण करून कुटुंबाच्या रक्षणासाठी प्रार्थना केली जाते. (गुजरातमध्ये नाग पंचम भाद्रपदात, नंतर येते.)",
    # EN: Kajari (Kajli, Badi) Teej, Bhadrapada Krishna Tritiya (purnimanta), is kept by married
    #     women of Uttar Pradesh, Bihar, Rajasthan and Madhya Pradesh. They fast, worship the neem
    #     tree (Neemadi Mata) and break the fast after offering arghya to the Moon; kajari folk
    #     songs are sung.
    "kajari-teej": "कजरी (कजली, बडी) तीज, भाद्रपद कृष्ण तृतीया (पौर्णिमांत), उत्तर प्रदेश, बिहार, राजस्थान आणि मध्य प्रदेशातील विवाहित स्त्रिया करतात. त्या उपवास करतात, कडुनिंबाच्या झाडाची (नीमडी मातेची) पूजा करतात आणि चंद्राला अर्घ्य दिल्यानंतर उपवास सोडतात; कजरीची लोकगीते गायली जातात.",
    # EN: Hal Shashthi (Lalahi Chhath, Har Chhath), Bhadrapada Krishna Shashthi (purnimanta), is
    #     Lord Balarama's birthday, whose weapon is the plough (hal). Mothers fast for their
    #     children and eat nothing grown with a plough - often pasahi rice and buffalo milk.
    "hal-shashthi": "हल षष्ठी (ललही छठ, हर छठ), भाद्रपद कृष्ण षष्ठी (पौर्णिमांत), हा भगवान बलरामाचा जन्मदिवस आहे, ज्यांचे शस्त्र नांगर (हल) आहे. माता मुलांसाठी उपवास करतात आणि नांगरणीने पिकवलेले काहीही खात नाहीत — बहुधा पसाही तांदूळ आणि म्हशीचे दूध.",
    # EN: Hartalika Teej, Bhadrapada Shukla Tritiya, honours Parvati's penance to win Shiva. Women
    #     keep a nirjala fast, make clay images of Shiva and Parvati, worship them (morning puja in
    #     Pratahkala is preferred), keep vigil at night and break the fast next morning.
    "hartalika-teej": "हरतालिका तृतीया, भाद्रपद शुक्ल तृतीया, शिवाला मिळवण्यासाठी पार्वतीने केलेल्या तपश्चर्येचा सन्मान करते. स्त्रिया निर्जला उपवास करतात, मातीच्या शिव-पार्वतीच्या मूर्ती बनवून त्यांची पूजा करतात (प्रातःकाळातील सकाळची पूजा श्रेष्ठ), रात्री जागरण करतात आणि दुसऱ्या दिवशी सकाळी उपवास सोडतात.",
    # EN: Rishi Panchami, Bhadrapada Shukla Panchami, honours the Saptarishis, the seven sages.
    #     Women in particular bathe, fast and worship the sages at midday (Madhyahna), seeking
    #     purification from faults committed unknowingly.
    "rishi-panchami": "ऋषिपंचमी, भाद्रपद शुक्ल पंचमी, सप्तर्षींचा, म्हणजे सात ऋषींचा सन्मान करते. विशेषतः स्त्रिया स्नान करतात, उपवास करतात आणि मध्याह्नात ऋषींची पूजा करतात, नकळत घडलेल्या दोषांपासून शुद्धीसाठी.",
    # EN: Anant Chaturdashi, Bhadrapada Shukla Chaturdashi, is the worship of Lord Vishnu as Anant.
    #     A sacred thread with fourteen knots (the anant sutra) is tied on the arm after puja; it is
    #     also the day Ganesh idols are immersed (Ganesh Visarjan).
    "anant-chaturdashi": "अनंत चतुर्दशी, भाद्रपद शुक्ल चतुर्दशी, म्हणजे भगवान विष्णूंची अनंत रूपात पूजा. पूजेनंतर चौदा गाठींचा पवित्र धागा (अनंत सूत्र) दंडावर बांधला जातो; याच दिवशी गणेश मूर्तींचे विसर्जन (गणेश विसर्जन) होते.",
    # EN: Pitru Paksha, the fortnight of the ancestors, runs from Pratipada to Amavasya of the dark
    #     half of Ashwin (purnimanta). On the tithi of an ancestor's passing, families offer tarpan
    #     and shraddha - pinda, food for Brahmins, cows, crows and dogs - in the Kutup, Rohina or
    #     Aparahna time.
    "pitru-paksha": "पितृपक्ष, पूर्वजांचा पंधरवडा, आश्विन (पौर्णिमांत) कृष्ण पक्षातील प्रतिपदेपासून अमावस्येपर्यंत चालतो. पूर्वजांच्या निधनाच्या तिथीला कुटुंबे कुतुप, रौहिण किंवा अपराह्न वेळेत तर्पण आणि श्राद्ध — पिंड, ब्राह्मण, गाय, कावळे आणि कुत्र्यांसाठी अन्न — अर्पण करतात.",
    # EN: Sarva Pitru Amavasya (Mahalaya Amavasya) closes Pitru Paksha. Shraddha on this day reaches
    #     all ancestors, including those whose tithi is not known; it is done in the Kutup, Rohina
    #     or Aparahna time.
    "sarva-pitru-amavasya": "सर्वपित्री अमावस्या (महालय अमावस्या) पितृपक्षाची सांगता करते. या दिवशी केलेले श्राद्ध सर्व पूर्वजांपर्यंत पोहोचते, ज्यांची तिथी माहीत नाही त्यांच्यापर्यंतही; ते कुतुप, रौहिण किंवा अपराह्न वेळेत केले जाते.",
    # EN: Narak Chaturdashi (Roop Chaudas), Kartika Krishna Chaturdashi (purnimanta), remembers
    #     Krishna's victory over Narakasura. Before sunrise, while the Moon is up, people take an
    #     oil bath with ubtan (Abhyang snan), and a lamp for Yama is lit in the evening.
    "narak-chaturdashi": "नरक चतुर्दशी (रूप चौदस), कार्तिक कृष्ण चतुर्दशी (पौर्णिमांत), कृष्णाने नरकासुरावर मिळवलेल्या विजयाचे स्मरण करते. सूर्योदयापूर्वी, चंद्र आकाशात असताना, उटण्यासह तेलाने स्नान (अभ्यंगस्नान) केले जाते, आणि संध्याकाळी यमासाठी दिवा लावला जातो.",
    # EN: Tulsi Vivah, on Kartika Shukla Dwadashi, is the ceremonial wedding of the tulsi plant (as
    #     Vrinda) to Lord Vishnu as Shaligram. Families decorate the tulsi like a bride and perform
    #     the rites of a wedding; the Hindu wedding season begins after it.
    "tulsi-vivah": "तुलसी विवाह, कार्तिक शुक्ल द्वादशीला, तुळशीचे (वृंदा म्हणून) भगवान विष्णूंशी (शाळिग्राम रूपात) होणारे विधिपूर्वक लग्न आहे. कुटुंबे तुळशीला नववधूप्रमाणे सजवतात आणि लग्नाचे विधी करतात; त्यानंतर हिंदू विवाहाचा हंगाम सुरू होतो.",
    # EN: Kartik Purnima ends the holy month of Kartika. It is a great day for bathing in the Ganga
    #     or a holy river and giving in charity, and also Guru Nanak Jayanti and Tripuri Purnima,
    #     when Shiva destroyed Tripurasura.
    "kartik-purnima": "कार्तिक पौर्णिमा पवित्र कार्तिक महिन्याची सांगता करते. गंगा किंवा पवित्र नदीत स्नान आणि दान देण्यासाठी हा मोठा दिवस आहे, तसेच गुरु नानक जयंती आणि त्रिपुरी पौर्णिमाही, ज्या दिवशी शिवाने त्रिपुरासुराचा संहार केला.",
    # EN: Dev Deepawali, the 'Diwali of the gods', is celebrated on Kartik Purnima evening, above
    #     all on the ghats of Varanasi, which are lit with lakhs of diyas. It marks Shiva's victory
    #     over Tripurasura; lamps are offered to the Ganga in Pradosh kaal.
    "dev-deepawali": "देव दिवाळी, ‘देवांची दिवाळी’, कार्तिक पौर्णिमेच्या संध्याकाळी साजरी होते, विशेषतः वाराणसीच्या घाटांवर, जे लाखो पणत्यांनी उजळतात. हा शिवाचा त्रिपुरासुरावरील विजय साजरा करतो; प्रदोषकाळात गंगेला दीप अर्पण केले जातात.",
}

# app/vrat_text.py NOTES["mr"] — tradition notes on dates that differ between almanacs (key = festival slug)  [11]
VRAT_NOTES = {
    # EN: Dates follow Drik Panchang. When Bhadra covers the whole Purnima night and Purnima lasts
    #     most of the next day, Drik moves Holika Dahan to the next evening's Pradosh (as in 2026, 3
    #     March); some almanacs instead give a time late on the first night, after Bhadra ends.
    "holika-dahan": "तारखा दृक पंचांगानुसार आहेत. जेव्हा भद्रा पौर्णिमेची संपूर्ण रात्र व्यापते आणि पौर्णिमा दुसऱ्या दिवसाचा बराचसा भाग टिकते, तेव्हा दृक पंचांग होलिका दहन दुसऱ्या संध्याकाळच्या प्रदोषात नेते (जसे 2026 मध्ये, 3 मार्च रोजी); काही पंचांगे त्याऐवजी पहिल्या रात्री भद्रा संपल्यानंतरची उशिराची वेळ देतात.",
    # EN: Dates follow Drik Panchang's Smarta (default) reckoning, with Rohini nakshatra at midnight
    #     preferred. Vaishnava/ISKCON communities sometimes keep Janmashtami a day later.
    "janmashtami": "तारखा दृक पंचांगाच्या स्मार्त (डीफॉल्ट) गणनेनुसार आहेत, मध्यरात्री रोहिणी नक्षत्र असलेला दिवस श्रेष्ठ मानला जातो. वैष्णव/इस्कॉन समुदाय कधीकधी जन्माष्टमी एक दिवस उशिरा साजरी करतात.",
    # EN: This is the Smarta (householder) date. Where Ekadashi spans two days, Vaishnavas may fast
    #     on the second day.
    "devuthani-ekadashi": "ही स्मार्त (गृहस्थ) तारीख आहे. एकादशी दोन दिवसांवर पसरली असल्यास वैष्णव दुसऱ्या दिवशी उपवास करू शकतात.",
    # EN: Dates follow Drik Panchang (Dashami in Aparahna, Shravana nakshatra preferred). In Bengal
    #     and some almanacs Vijayadashami can fall a day later.
    "dussehra": "तारखा दृक पंचांगानुसार आहेत (अपराह्नात दशमी, श्रवण नक्षत्र श्रेष्ठ). बंगालमध्ये आणि काही पंचांगांत विजयादशमी एक दिवस उशिरा येऊ शकते.",
    # EN: Dates follow Drik Panchang (Ashtami at midday; when it is at sunrise only briefly, as in
    #     2023, the previous day). Nahay-khay is the day before and parana the next morning;
    #     regional panchangs (e.g. Mithila) can differ by a day.
    "jivitputrika": "तारखा दृक पंचांगानुसार आहेत (दुपारी अष्टमी; 2023 प्रमाणे, सूर्योदयाला ती थोडाच वेळ असल्यास, आदला दिवस). नहाय-खाय आदल्या दिवशी आणि पारणे दुसऱ्या दिवशी सकाळी असते; प्रादेशिक पंचांगे (उदा. मिथिला) एका दिवसाने वेगळी असू शकतात.",
    # EN: Two traditions: North India keeps Vat Savitri on Jyeshtha Amavasya (this date);
    #     Maharashtra, Gujarat and the south keep it as Vat Purnima fifteen days later.
    "vat-savitri": "दोन परंपरा आहेत: उत्तर भारत वटसावित्री ज्येष्ठ अमावस्येला करतो (ही तारीख); महाराष्ट्र, गुजरात आणि दक्षिण भारत ते पंधरा दिवसांनी वटपौर्णिमा म्हणून करतात.",
    # EN: Two traditions: this is the Purnima (amanta) date of Maharashtra, Gujarat and the south;
    #     North India keeps Vat Savitri on the Amavasya fifteen days earlier.
    "vat-purnima": "दोन परंपरा आहेत: ही महाराष्ट्र, गुजरात आणि दक्षिणेतील पौर्णिमेची (अमांत) तारीख आहे; उत्तर भारत वटसावित्री पंधरा दिवस आधीच्या अमावस्येला करतो.",
    # EN: When Jyeshtha is doubled (an adhika month, as in 2026), Drik Panchang keeps Ganga Dussehra
    #     in the adhika Jyeshtha; some almanacs give the nija Jyeshtha date a month later.
    "ganga-dussehra": "जेव्हा ज्येष्ठ महिना दुप्पट असतो (अधिक मास, जसा 2026 मध्ये), तेव्हा दृक पंचांग गंगा दशहरा अधिक ज्येष्ठात ठेवते; काही पंचांगे निज ज्येष्ठाची तारीख एका महिन्याने नंतर देतात.",
    # EN: Drik Panchang counts Pitru Paksha from the Pratipada shraddha; Purnima shraddha is on the
    #     day before, and many calendars start the fortnight there.
    "pitru-paksha": "दृक पंचांग पितृपक्ष प्रतिपदा श्राद्धापासून मोजते; पौर्णिमा श्राद्ध आदल्या दिवशी असते, आणि अनेक दिनदर्शिका पंधरवडा तिथून सुरू करतात.",
    # EN: Drik Panchang publishes Dev Deepawali for Varanasi; the date here uses the same rule
    #     (Purnima in Pradosh), and the Pradosh kaal shown is New Delhi's.
    "dev-deepawali": "दृक पंचांग देव दिवाळी वाराणसीसाठी प्रकाशित करते; येथील तारीख त्याच नियमाने (प्रदोषात पौर्णिमा) ठरवली आहे, आणि दाखवलेला प्रदोषकाळ नवी दिल्लीचा आहे.",
    # EN: This is the snan-daan day (Purnima at sunrise). When Purnima begins the previous
    #     afternoon, the Purnima fast and Dev Deepawali can fall a day earlier.
    "kartik-purnima": "हा स्नान-दानाचा दिवस आहे (सूर्योदयाला पौर्णिमा). पौर्णिमा आदल्या दिवशी दुपारी सुरू होत असल्यास पौर्णिमा व्रत आणि देव दिवाळी एक दिवस आधी येऊ शकतात.",
}

# app/vrat_text.py RULES["mr"] — 'how the date is fixed' sentences: head {month}, tithi {paksha} {tithi}, rule.<kind>, key.<observance>  [16]
VRAT_RULES = {
    # EN: {month} (amanta)
    # keep: {month}
    "head": "{month} (अमांत) ",
    # EN: {paksha} {tithi}:
    # keep: {paksha} {tithi}
    "tithi": "{paksha} {tithi}: ",
    # EN: tithi prevailing at sunrise
    "rule.udaya": "सूर्योदयाच्या वेळी असलेली तिथी",
    # EN: tithi prevailing in Pratahkala (first fifth of the day)
    "rule.pratah": "प्रातःकाळात (दिवसाच्या पहिल्या पंचमांशात) असलेली तिथी",
    # EN: tithi prevailing in the forenoon (purvahna)
    "rule.purvahna": "पूर्वाह्नात असलेली तिथी",
    # EN: tithi prevailing at Madhyahna (midday fifth of the day)
    "rule.madhyahna": "मध्याह्नात (दिवसाच्या मधल्या पंचमांशात) असलेली तिथी",
    # EN: tithi prevailing at Aparahna (fourth fifth of the day)
    "rule.aparahna": "अपराह्नात (दिवसाच्या चौथ्या पंचमांशात) असलेली तिथी",
    # EN: first day on which the tithi is present between sunrise and sunset
    "rule.dina": "सूर्योदय ते सूर्यास्त यांच्या दरम्यान तिथी असलेला पहिला दिवस",
    # EN: tithi prevailing at sunset
    "rule.sayahna": "सूर्यास्ताच्या वेळी असलेली तिथी",
    # EN: tithi prevailing in Pradosh kaal (after sunset)
    "rule.pradosh": "प्रदोषकाळात (सूर्यास्तानंतर) असलेली तिथी",
    # EN: tithi prevailing at Nishita kaal (midnight)
    "rule.nishita": "निशीथ काळात (मध्यरात्री) असलेली तिथी",
    # EN: tithi prevailing at moonrise
    "rule.moonrise": "चंद्रोदयाच्या वेळी असलेली तिथी",
    # EN: Smarta: Ekadashi prevailing at sunrise (second day if at two sunrises); parana next day
    #     after sunrise and after Hari Vasara, within Pratahkala and before Dwadashi ends
    "key.ekadashi": "स्मार्त: सूर्योदयाच्या वेळी असलेली एकादशी (दोन सूर्योदयांना असल्यास दुसरा दिवस); पारणे दुसऱ्या दिवशी सूर्योदयानंतर आणि हरिवासरानंतर, प्रातःकाळात आणि द्वादशी संपण्यापूर्वी",
    # EN: the Sun's entry into sidereal Makara (Capricorn); punya kaal follows it until sunset
    "key.makar_sankranti": "सूर्याचा निरयन मकर राशीत प्रवेश; त्यानंतर सूर्यास्तापर्यंत पुण्यकाळ",
    # EN: the day before Makar Sankranti
    "key.lohri": "मकर संक्रांतीचा आदला दिवस",
    # EN: the day after Holika Dahan
    "key.holi": "होलिका दहनानंतरचा दिवस",
}

# ----------------------------------------------------------------------------
# nakshatra /nakshatra /rashi /naam-se-kundali-milan
# ----------------------------------------------------------------------------

# app/nakshatra_page_text.py TEXT["mr"] — page text of /nakshatra /rashi (nakshatra_pages.py)  [88]
NAKSHATRA_PAGE_TEXT = {
    # EN: Get your free kundali — find your exact birth nakshatra and Moon sign
    "kundali_cta": "तुमची मोफत कुंडली मिळवा — तुमचे अचूक जन्मनक्षत्र आणि चंद्र रास शोधा",
    # EN: More free tools
    "more.heading": "आणखी मोफत साधने",
    # EN: All 27 nakshatras
    "more.naks": "सर्व 27 नक्षत्रे",
    # EN: All 12 rashis
    "more.rashis": "सर्व 12 राशी",
    # EN: Naam se Kundali Milan
    "more.milan": "नावावरून कुंडली मिलन",
    # EN: Kundali Milan (36 guna)
    "more.kundali_milan": "कुंडली मिलन (36 गुण)",
    # EN: Today's Rashifal
    "more.rashifal": "आजचे राशिभविष्य",
    # EN: Today's Panchang
    "more.panchang": "आजचे पंचांग",
    # EN: All 27 nakshatras
    "list.naks": "सर्व 27 नक्षत्रे",
    # EN: All 12 rashis
    "list.rashis": "सर्व 12 राशी",
    # EN: {name} ({english})
    # keep: {name}
    "sign": "{name}",
    # EN: {name} · {english}
    # keep: {name}
    "sign.pill": "{name}",
    # EN: <strong>Today the Moon is in {name} (at sunrise in New Delhi).</strong>
    # keep: {name}
    "today.same": "<strong>आज (नवी दिल्लीत सूर्योदयाच्या वेळी) चंद्र {name} मध्ये आहे.</strong>",
    # EN: Today's nakshatra is <a href="{href}"><strong>{name}</strong></a> (at sunrise in New
    #     Delhi).
    # keep: {href} {name}
    "today.other": "आजचे नक्षत्र <a href=\"{href}\"><strong>{name}</strong></a> आहे (नवी दिल्लीत सूर्योदयाच्या वेळी).",
    # EN: Its end time, the tithi and Rahu Kaal are on <a href="{pan}">today's Panchang</a>.
    # keep: {pan}
    "today.tail": "त्याची समाप्तीची वेळ, तिथी आणि राहुकाळ <a href=\"{pan}\">आजच्या पंचांगात</a> पाहा.",
    # EN: Nakshatras
    "crumb.naks": "नक्षत्रे",
    # EN: Rashis
    "crumb.rashis": "राशी",
    # EN: Nakshatra not found
    "nf.nak": "नक्षत्र सापडले नाही",
    # EN: Rashi not found
    "nf.rashi": "रास सापडली नाही",
    # EN: Nature and traits
    "trait_head": "स्वभाव आणि वैशिष्ट्ये",
    # EN: male
    "gender.male": "पुरुष",
    # EN: female
    "gender.female": "स्त्री",
    # EN: Fire
    "element.Fire": "अग्नी",
    # EN: Earth
    "element.Earth": "पृथ्वी",
    # EN: Air
    "element.Air": "वायू",
    # EN: Water
    "element.Water": "जल",
    # EN: Movable (Chara)
    "quality.Cardinal": "चर",
    # EN: Fixed (Sthira)
    "quality.Fixed": "स्थिर",
    # EN: Dual (Dwiswabhava)
    "quality.Mutable": "द्विस्वभाव",
    # EN: {name} Nakshatra — Deity, Lord, Gana, Yoni, Nadi & Name Letters ({lat}) | {brand}
    # keep: {brand} {name}
    "nak.title": "{name} नक्षत्र — देवता, स्वामी, गण, योनी, नाडी आणि नामाक्षरे | {brand}",
    # EN: {name} nakshatra ({name_hi}): {span}, ruled by {lord}, deity {deity_short}, {gana} gana,
    #     {nadi} nadi, {yoni} yoni. Name syllables {lat} and traits.
    # keep: {gana} {lord} {nadi} {name} {span} {yoni}
    # may also use: {name_en}
    "nak.desc": "{name} नक्षत्र: {span}, स्वामी {lord}, {gana} गण, {nadi} नाडी, {yoni} योनी. चरणांनुसार नामाक्षरे आणि स्वभाव.",
    # EN: <h1>{name} Nakshatra</h1>
    # keep: {name}
    "nak.h1": "<h1>{name} नक्षत्र</h1>",
    # EN: <p class="hi" lang="hi">{name_hi} नक्षत्र</p>
    # may also use: {name_en} {name}
    "nak.sub": "<p class=\"hi\">नक्षत्र · चरण आणि नामाक्षरे</p>",
    # EN: <p class="note">These are traditional tendencies, not verdicts. Your full kundali —
    #     ascendant, planets and dasha — gives the personal picture.</p>
    "nak.trait_note": "<p class=\"note\">हे परंपरेतील कल आहेत, निकाल नाहीत. वैयक्तिक चित्र तुमच्या संपूर्ण कुंडलीतून — लग्न, ग्रह आणि दशा — मिळते.</p>",
    # EN: Number
    "f.number": "क्रमांक",
    # EN: {n} of 27
    # keep: {n}
    "f.number_v": "27 पैकी {n}",
    # EN: Span (sidereal)
    "f.span": "विस्तार (निरयन)",
    # EN: Rashi
    "f.rashi": "रास",
    # EN: Ruling planet (Vimshottari lord)
    "f.lord": "स्वामी ग्रह (विंशोत्तरी स्वामी)",
    # EN: {lord} <small>{years}-year mahadasha</small>
    # keep: {lord} {years}
    "f.lord_v": "{lord} <small>{years} वर्षांची महादशा</small>",
    # EN: Deity
    "f.deity": "देवता",
    # EN: Symbol
    "f.symbol": "प्रतीक",
    # EN: Gana
    "f.gana": "गण",
    # EN: {gana} <small lang="hi">{gana_hi}</small>
    # keep: {gana}
    "f.gana_v": "{gana}",
    # EN: Yoni (animal)
    "f.yoni": "योनी (प्राणी)",
    # EN: Nadi
    "f.nadi": "नाडी",
    # EN: Varna (from its rashi, as used in Guna Milan)
    "f.varna": "वर्ण (राशीवरून, गुण मिलनात वापरला जाणारा)",
    # EN: Name syllables (namakshar)
    "f.syl": "नामाक्षरे",
    # EN: <span class="syl" lang="hi">{syl}</span> <small>{lat}</small>
    # keep: {syl}
    "f.syl_v": "<span class=\"syl\">{syl}</span>",
    # EN: The four padas and their name syllables
    "pada.title": "चार चरण आणि त्यांची नामाक्षरे",
    # EN: <tr><th>Pada</th><th>Span</th><th>Rashi</th><th>Name syllable</th></tr>
    "pada.head": "<tr><th>चरण</th><th>विस्तार</th><th>रास</th><th>नामाक्षर</th></tr>",
    # EN: <p class="note">Traditionally a child's name begins with the syllable of the pada the Moon
    #     occupied at birth (namakshar). Syllables follow the 108-pada Swar Siddhanta list (the
    #     Avakahada Chakra) as published by Drik Panchang.</p>
    "pada.note": "<p class=\"note\">परंपरेनुसार मुलाचे नाव जन्माच्या वेळी चंद्र ज्या चरणात होता त्या चरणाच्या अक्षराने (नामाक्षर) सुरू होते. अक्षरे दृक पंचांगाने प्रकाशित केलेल्या 108-चरणांच्या स्वर सिद्धांत यादीनुसार (अवकहडा चक्र) आहेत.</p>",
    # EN: Related
    "rel.heading": "संबंधित",
    # EN: Today's {name} Rashifal
    # keep: {name}
    "rel.rashifal": "आजचे {name} राशिभविष्य",
    # EN: The 27 Nakshatras — Lords, Deities, Gana & Name Syllables | {brand}
    # keep: {brand}
    "ni.title": "27 नक्षत्रे — स्वामी, देवता, गण आणि नामाक्षरे | {brand}",
    # EN: All 27 nakshatras from Ashwini to Revati: span, rashi, ruling planet, deity, gana, yoni,
    #     nadi and the name syllables of all four padas — consistent with our Kundali Milan tables.
    "ni.desc": "अश्विनीपासून रेवतीपर्यंत सर्व 27 नक्षत्रे: विस्तार, रास, स्वामी ग्रह, देवता, गण, योनी, नाडी आणि चारही चरणांची नामाक्षरे — आमच्या कुंडली मिलनाच्या तक्त्यांशी सुसंगत.",
    # EN: <h1>The 27 Nakshatras</h1>
    "ni.h1": "<h1>27 नक्षत्रे</h1>",
    # EN: <p class="hi" lang="hi">27 नक्षत्र</p>
    "ni.sub": "<p class=\"hi\">अश्विनी ते रेवती</p>",
    # EN: <p>Vedic astrology divides the zodiac into 27 nakshatras (lunar mansions) of 13°20′ each,
    #     and each nakshatra into four padas of 3°20′. The 108 padas fall exactly nine to a sign
    #     across the 12 rashis. Your birth nakshatra is the one the Moon occupied when you were
    #     born: it starts your Vimshottari dasha and drives the Tara, Yoni, Gana and Nadi kootas of
    #     Kundali Milan.</p>
    "ni.intro": "<p>वैदिक ज्योतिष राशिचक्राला प्रत्येकी 13°20′ च्या 27 नक्षत्रांत विभागते, आणि प्रत्येक नक्षत्राला 3°20′ च्या चार चरणांत. 108 चरण 12 राशींमध्ये अगदी नऊ प्रति रास असे बसतात. तुमचे जन्मनक्षत्र म्हणजे तुमच्या जन्माच्या वेळी चंद्र ज्यात होता ते: त्यावरून तुमची विंशोत्तरी दशा सुरू होते आणि कुंडली मिलनातील तारा, योनी, गण आणि नाडी हे कूट ठरतात.</p>",
    # EN: <tr><th>#</th><th>Nakshatra</th><th>Rashi</th><th>Lord</th><th>Gana</th><th>Name
    #     syllables</th></tr>
    "ni.head": "<tr><th>#</th><th>नक्षत्र</th><th>रास</th><th>स्वामी</th><th>गण</th><th>नामाक्षरे</th></tr>",
    # EN: {name} Rashi ({english}) — Lord, Element, Nakshatras & Name Letters | {brand}
    # keep: {brand} {name}
    # may also use: {english}
    "rs.title": "{name} रास — स्वामी, तत्त्व, नक्षत्रे आणि नामाक्षरे | {brand}",
    # EN: {name} rashi ({english} Moon sign, {name_hi}): ruled by {lord}, {element_lower} element,
    #     {quality_lower} quality. Its 9 nakshatra padas, name syllables ({lat}) and traits.
    # keep: {lord} {name}
    # may also use: {element_lower} {element} {english} {name_en} {quality_lower} {quality}
    "rs.desc": "{name} रास (चंद्र रास): स्वामी {lord}, {element_lower} तत्त्व, {quality_lower} स्वभाव. तिचे 9 नक्षत्र चरण, नामाक्षरे आणि स्वभाव.",
    # EN: <h1>{name} Rashi — {english} Moon Sign</h1>
    # keep: {name}
    # may also use: {english}
    "rs.h1": "<h1>{name} रास — चंद्र रास</h1>",
    # EN: <p class="hi" lang="hi">{name_hi} राशि</p>
    # may also use: {english} {name_en} {name}
    "rs.sub": "<p class=\"hi\">रास · स्वभाव आणि नक्षत्रे</p>",
    # EN: Read today's {name} Rashifal
    # keep: {name}
    "rs.today": "आजचे {name} राशिभविष्य वाचा",
    # EN: <p class="note">In Vedic astrology "rashi" usually means the Moon sign — the sign the Moon
    #     occupied at birth, in the sidereal zodiac. It is often different from a Western sun
    #     sign.</p>
    "rs.note": "<p class=\"note\">वैदिक ज्योतिषात “रास” म्हणजे सहसा चंद्र रास — निरयन राशिचक्रात जन्माच्या वेळी चंद्र ज्या राशीत होता ती. ती अनेकदा पाश्चात्य सूर्य राशीपेक्षा वेगळी असते.</p>",
    # EN: Number
    "r.number": "क्रमांक",
    # EN: {n} of 12
    # keep: {n}
    "r.number_v": "12 पैकी {n}",
    # EN: Span (sidereal zodiac)
    "r.span": "विस्तार (निरयन राशिचक्र)",
    # EN: Sign lord
    "r.lord": "राशी स्वामी",
    # EN: Element
    "r.element": "तत्त्व",
    # EN: Quality
    "r.quality": "स्वभाव",
    # EN: Varna (used in Guna Milan)
    "r.varna": "वर्ण (गुण मिलनात वापरला जाणारा)",
    # EN: Nakshatras
    "r.naks": "नक्षत्रे",
    # EN: Name syllables (namakshar)
    "r.syl": "नामाक्षरे",
    # EN: <span class="syl" lang="hi">{syl}</span>
    # keep: {syl}
    "r.syl_v": "<span class=\"syl\">{syl}</span>",
    # EN: The nine nakshatra padas in this sign
    "rp.title": "या राशीतील नऊ नक्षत्र चरण",
    # EN: <tr><th>Nakshatra</th><th>Pada</th><th>Degrees in sign</th><th>Syllable</th></tr>
    "rp.head": "<tr><th>नक्षत्र</th><th>चरण</th><th>राशीतील अंश</th><th>अक्षर</th></tr>",
    # EN: The 12 Rashis — Lords, Elements, Nakshatras & Name Letters | {brand}
    # keep: {brand}
    "ri.title": "12 राशी — स्वामी, तत्त्वे, नक्षत्रे आणि नामाक्षरे | {brand}",
    # EN: All 12 rashis (Vedic Moon signs) from Mesh to Meen: sign lord, element, quality, the nine
    #     nakshatra padas in each and their name syllables (namakshar).
    "ri.desc": "मेषेपासून मीनेपर्यंत सर्व 12 राशी (वैदिक चंद्र राशी): राशी स्वामी, तत्त्व, स्वभाव, प्रत्येकातील नऊ नक्षत्र चरण आणि त्यांची नामाक्षरे.",
    # EN: <h1>The 12 Rashis (Moon Signs)</h1>
    "ri.h1": "<h1>12 राशी (चंद्र राशी)</h1>",
    # EN: <p class="hi" lang="hi">12 राशियाँ</p>
    "ri.sub": "<p class=\"hi\">मेष ते मीन</p>",
    # EN: <p>Each rashi spans 30° of the sidereal zodiac and holds exactly nine nakshatra padas.
    #     Your rashi is your Moon sign — the sign the Moon occupied at birth — and it is what
    #     rashifal, Sade Sati and Kundali Milan are read from.</p>
    "ri.intro": "<p>प्रत्येक रास निरयन राशिचक्राचे 30° व्यापते आणि तिच्यात अगदी नऊ नक्षत्र चरण असतात. तुमची रास म्हणजे तुमची चंद्र रास — जन्माच्या वेळी चंद्र ज्या राशीत होता ती — आणि राशिभविष्य, साडेसाती व कुंडली मिलन तिच्यावरूनच पाहिले जाते.</p>",
    # EN: <tr><th>Rashi</th><th>Lord</th><th>Element</th><th>Nakshatras</th><th>Name
    #     syllables</th></tr>
    "ri.head": "<tr><th>रास</th><th>स्वामी</th><th>तत्त्व</th><th>नक्षत्रे</th><th>नामाक्षरे</th></tr>",
    # EN: {name} <small>{english}</small>
    # keep: {name}
    # may also use: {english}
    "ri.name": "{name}",
    # EN: Vata
    "humour.Vata": "वात",
    # EN: Pitta
    "humour.Pitta": "पित्त",
    # EN: Kapha
    "humour.Kapha": "कफ",
}

# app/nakshatra_text.py NAKSHATRA_TRAITS["mr"] — character paragraph of each of the 27 nakshatras (key = slug)  [27]
NAKSHATRA_TRAITS = {
    # EN: Ashwini is the first nakshatra, ruled by the Ashwini Kumaras, the twin healers of the
    #     gods, and symbolised by a horse's head. People with the Moon here are often quick,
    #     energetic and eager to begin things — the first to help, the first to try something new.
    #     Tradition links Ashwini with healing, speed and fresh starts, so many feel drawn to
    #     medicine, sport, travel or any work that needs swift, practical action. The gift of this
    #     nakshatra is initiative and a youthful optimism; the lesson is patience, finishing what
    #     was started with the same enthusiasm with which it began.
    "ashwini": "अश्विनी हे पहिले नक्षत्र आहे, ज्याचे स्वामी देवांचे जुळे वैद्य अश्विनीकुमार आहेत, आणि त्याचे प्रतीक घोड्याचे डोके आहे. ज्यांचा चंद्र इथे असतो ते लोक अनेकदा चपळ, उत्साही आणि गोष्टी सुरू करण्यास उत्सुक असतात — मदतीला सर्वात आधी धावणारे, नवीन काही करून पाहणारे सर्वात पहिले. परंपरा अश्विनीला उपचार, वेग आणि नव्या सुरुवातींशी जोडते, म्हणून अनेकांना वैद्यकीय क्षेत्र, खेळ, प्रवास किंवा झटपट, व्यावहारिक कृती लागणाऱ्या कामाकडे ओढ वाटते. या नक्षत्राची देणगी म्हणजे पुढाकार आणि तारुण्यसुलभ आशावाद; शिकवण म्हणजे संयम — जे सुरू केले ते तेवढ्याच उत्साहाने पूर्ण करणे.",
    # EN: Bharani is ruled by Yama, the lord of dharma, and its symbol is the yoni, the womb that
    #     carries and protects new life. People with the Moon here often have strong will, deep
    #     feelings and a serious sense of responsibility. They tend to carry their commitments
    #     through to the end and are not easily swayed. Tradition sees Bharani as the nakshatra of
    #     bearing and nurturing — holding something until it is ready to be born — so creativity,
    #     family, art and work that asks for endurance suit it well. Its strength is steadfastness;
    #     its lesson is balancing desire with restraint and kindness.
    "bharani": "भरणीचा स्वामी धर्माचा अधिपती यम आहे, आणि त्याचे प्रतीक योनी आहे, नवे जीवन धारण करून त्याचे रक्षण करणारे गर्भाशय. ज्यांचा चंद्र इथे असतो त्यांच्यात अनेकदा प्रबळ इच्छाशक्ती, खोल भावना आणि जबाबदारीची गंभीर जाणीव असते. ते आपल्या वचनबद्धता शेवटपर्यंत नेतात आणि सहज प्रभावित होत नाहीत. परंपरा भरणीला धारण आणि पोषणाचे नक्षत्र मानते — एखादी गोष्ट जन्माला येण्यास तयार होईपर्यंत तिला जपणे — म्हणून सर्जनशीलता, कुटुंब, कला आणि सहनशक्ती लागणारे काम त्याला चांगले जुळते. त्याचे बळ म्हणजे दृढता; शिकवण म्हणजे इच्छेचा समतोल संयम आणि दयाळूपणाशी साधणे.",
    # EN: Krittika is ruled by Agni, the sacred fire, and symbolised by a razor or a flame. Fire
    #     purifies and cuts through confusion, and people with the Moon here are often direct,
    #     principled and sharp in judgement. They can be protective of those they love and are
    #     willing to say what needs to be said. Krittika is also the nakshatra of the six mothers
    #     who nursed Kartikeya, so beneath the sharpness there is real warmth and care. Teaching,
    #     cooking, leadership and any work that needs clarity suit it. Its lesson is to let the fire
    #     warm and guide rather than burn.
    "krittika": "कृत्तिकेचा स्वामी पवित्र अग्नी आहे, आणि त्याचे प्रतीक वस्तरा किंवा ज्योत आहे. अग्नी शुद्ध करतो आणि गोंधळ कापून काढतो, आणि ज्यांचा चंद्र इथे असतो ते अनेकदा सरळ, तत्त्वनिष्ठ आणि निर्णयात तीक्ष्ण असतात. ते प्रिय व्यक्तींचे रक्षण करणारे असू शकतात आणि जे बोलायला हवे ते बोलायला तयार असतात. कृत्तिका हे कार्तिकेयाला पाळणाऱ्या सहा मातांचेही नक्षत्र आहे, म्हणून तीक्ष्णतेखाली खरी ऊब आणि काळजी असते. शिकवणे, स्वयंपाक, नेतृत्व आणि स्पष्टता लागणारे कोणतेही काम त्याला जुळते. शिकवण म्हणजे अग्नीने जाळण्याऐवजी ऊब द्यावी आणि मार्ग दाखवावा.",
    # EN: Rohini is ruled by Brahma, the creator, and symbolised by a chariot or ox-cart. It is said
    #     to be the Moon's favourite nakshatra, and people with the Moon here are often warm,
    #     attractive, artistic and fond of comfort and beauty. They have a gift for making things
    #     grow — gardens, homes, businesses and relationships. Tradition associates Rohini with
    #     fertility, abundance and steady progress, so agriculture, the arts, design, food and
    #     hospitality suit it well. Its nature is gentle and settled; its lesson is to enjoy what is
    #     beautiful without holding on too tightly to it.
    "rohini": "रोहिणीचा स्वामी सृष्टिकर्ता ब्रह्मा आहे, आणि त्याचे प्रतीक रथ किंवा बैलगाडी आहे. हे चंद्राचे आवडते नक्षत्र असल्याचे सांगितले जाते, आणि ज्यांचा चंद्र इथे असतो ते अनेकदा उबदार, आकर्षक, कलात्मक आणि सुखसोयी व सौंदर्याची आवड असलेले असतात. गोष्टी वाढवण्याची त्यांच्यात देणगी असते — बागा, घरे, व्यवसाय आणि नाती. परंपरा रोहिणीला सुपीकता, समृद्धी आणि स्थिर प्रगतीशी जोडते, म्हणून शेती, कला, रचना, अन्न आणि आतिथ्य त्याला चांगले जुळते. त्याचा स्वभाव सौम्य आणि स्थिर आहे; शिकवण म्हणजे जे सुंदर आहे त्याचा आनंद घ्यावा, पण त्याला फार घट्ट धरून बसू नये.",
    # EN: Mrigashira is ruled by Soma, the Moon, and its symbol is a deer's head — the deer that is
    #     always alert, curious and searching. People with the Moon here are often gentle,
    #     inquisitive and fond of learning, travel and conversation. They enjoy exploring ideas and
    #     places and rarely stop asking questions. Tradition sees Mrigashira as the seeker's
    #     nakshatra, which suits research, writing, teaching, trade and any work that rewards
    #     curiosity. Its charm is a light, friendly mind; its lesson is to settle on what has been
    #     found, so that the search leads somewhere rather than becoming restlessness.
    "mrigashira": "मृगशीर्षाचा स्वामी चंद्र (सोम) आहे, आणि त्याचे प्रतीक हरणाचे डोके आहे — सतत सावध, जिज्ञासू आणि शोध घेणारे हरीण. ज्यांचा चंद्र इथे असतो ते अनेकदा सौम्य, जिज्ञासू आणि शिकणे, प्रवास व संवाद आवडणारे असतात. त्यांना कल्पना आणि ठिकाणे शोधणे आवडते आणि ते क्वचितच प्रश्न विचारणे थांबवतात. परंपरा मृगशीर्षाला शोधकाचे नक्षत्र मानते, जे संशोधन, लेखन, शिकवणे, व्यापार आणि जिज्ञासेला बक्षीस देणाऱ्या कोणत्याही कामाला जुळते. त्याचे आकर्षण म्हणजे हलके, मैत्रीपूर्ण मन; शिकवण म्हणजे जे सापडले त्यावर स्थिर व्हावे, म्हणजे शोध कुठेतरी पोहोचतो, अस्वस्थतेत बदलत नाही.",
    # EN: Ardra is ruled by Rudra, the storm form of Shiva, and symbolised by a teardrop or a
    #     diamond. As a storm clears the air and brings rain, people with the Moon here often have a
    #     strong, searching intellect and the ability to see through things to the truth. They can
    #     feel deeply and are not afraid of change. Tradition links Ardra with renewal after
    #     difficulty, so research, technology, writing, counselling and problem-solving suit it
    #     well. Its gift is honesty and a sharp mind; its lesson is to let feelings pass like the
    #     rain, leaving the ground greener.
    "ardra": "आर्द्राचा स्वामी शिवाचे वादळी रूप रुद्र आहे, आणि त्याचे प्रतीक अश्रू किंवा हिरा आहे. वादळ जसे हवा स्वच्छ करते आणि पाऊस आणते, तसे ज्यांचा चंद्र इथे असतो त्यांच्यात अनेकदा प्रबळ, शोधक बुद्धी आणि गोष्टींच्या आरपार सत्य पाहण्याची क्षमता असते. ते खोलवर अनुभवू शकतात आणि बदलाला घाबरत नाहीत. परंपरा आर्द्राला अडचणीनंतरच्या नवनिर्मितीशी जोडते, म्हणून संशोधन, तंत्रज्ञान, लेखन, समुपदेशन आणि समस्या सोडवणे त्याला चांगले जुळते. त्याची देणगी म्हणजे प्रामाणिकपणा आणि तीक्ष्ण मन; शिकवण म्हणजे भावना पावसासारख्या जाऊ द्याव्यात, जमीन अधिक हिरवी करून.",
    # EN: Punarvasu is ruled by Aditi, the boundless mother of the gods, and symbolised by a bow and
    #     quiver. Its name means "return of the light", and people with the Moon here are often
    #     optimistic, generous and able to begin again after any setback. They tend to be content
    #     with simple things, good-humoured and caring towards family and guests. Tradition sees
    #     Punarvasu as a nakshatra of renewal and homecoming, suited to teaching, counselling,
    #     writing, travel and caring work. Its blessing is a hopeful, forgiving heart; its lesson is
    #     to aim the arrow — to choose a direction and stay with it.
    "punarvasu": "पुनर्वसूची स्वामिनी देवांची अमर्याद माता अदिती आहे, आणि त्याचे प्रतीक धनुष्य व भाता आहे. त्याच्या नावाचा अर्थ “प्रकाशाचे पुनरागमन” आहे, आणि ज्यांचा चंद्र इथे असतो ते अनेकदा आशावादी, उदार आणि कोणत्याही धक्क्यानंतर पुन्हा सुरुवात करू शकणारे असतात. ते साध्या गोष्टींत समाधानी, विनोदी आणि कुटुंब व पाहुण्यांची काळजी घेणारे असतात. परंपरा पुनर्वसूला नवनिर्मिती आणि घरवापसीचे नक्षत्र मानते, जे शिकवणे, समुपदेशन, लेखन, प्रवास आणि काळजी घेणाऱ्या कामाला जुळते. त्याचा आशीर्वाद म्हणजे आशावादी, क्षमाशील हृदय; शिकवण म्हणजे बाण नेम धरून सोडावा — दिशा निवडून तिला धरून राहावे.",
    # EN: Pushya is ruled by Brihaspati, the guru of the gods, and symbolised by a cow's udder or a
    #     lotus — images of nourishment. It is counted among the most auspicious nakshatras, and
    #     people with the Moon here are often caring, dependable, devoted and generous with their
    #     time. They like to support others, keep traditions and build something lasting. Tradition
    #     links Pushya with nourishment and wisdom, so teaching, counselling, food, social service,
    #     finance and spiritual work suit it well. Its gift is a steady, protective kindness; its
    #     lesson is to nourish oneself as faithfully as one nourishes others.
    "pushya": "पुष्याचा स्वामी देवांचा गुरू बृहस्पती आहे, आणि त्याचे प्रतीक गायीचे कास किंवा कमळ आहे — पोषणाची प्रतिमा. हे सर्वात शुभ नक्षत्रांपैकी मानले जाते, आणि ज्यांचा चंद्र इथे असतो ते अनेकदा काळजी घेणारे, विश्वासू, निष्ठावान आणि वेळ देण्यात उदार असतात. त्यांना इतरांना आधार द्यायला, परंपरा जपायला आणि कायमस्वरूपी काहीतरी उभे करायला आवडते. परंपरा पुष्याला पोषण आणि ज्ञानाशी जोडते, म्हणून शिकवणे, समुपदेशन, अन्न, समाजसेवा, वित्त आणि आध्यात्मिक कार्य त्याला चांगले जुळते. त्याची देणगी म्हणजे स्थिर, रक्षण करणारी दयाळूपणा; शिकवण म्हणजे जितक्या निष्ठेने इतरांचे पोषण करतो तितक्याच निष्ठेने स्वतःचेही करावे.",
    # EN: Ashlesha is ruled by the Nagas, the serpent deities, and symbolised by a coiled serpent —
    #     an image of kundalini, hidden energy and deep wisdom. People with the Moon here are often
    #     perceptive, intelligent and good at understanding what others leave unsaid. They can be
    #     persuasive and strategic, with a strong instinct for self-protection. Tradition links
    #     Ashlesha with insight and with the healing knowledge of herbs, so psychology, research,
    #     medicine, writing and negotiation suit it well. Its gift is penetrating understanding; its
    #     lesson is to use that insight to embrace and heal, the way the serpent's coil protects.
    "ashlesha": "आश्लेषाचे स्वामी नाग, म्हणजे सर्पदेवता आहेत, आणि त्याचे प्रतीक वेटोळे घातलेला साप आहे — कुंडलिनी, गुप्त ऊर्जा आणि खोल ज्ञानाची प्रतिमा. ज्यांचा चंद्र इथे असतो ते अनेकदा चाणाक्ष, बुद्धिमान आणि इतरांनी न बोललेले समजून घेण्यात कुशल असतात. ते पटवून देणारे आणि डावपेच आखणारे असू शकतात, आत्मरक्षणाची तीव्र सहजप्रवृत्ती असलेले. परंपरा आश्लेषाला अंतर्दृष्टी आणि वनौषधींच्या उपचारज्ञानाशी जोडते, म्हणून मानसशास्त्र, संशोधन, वैद्यकीय क्षेत्र, लेखन आणि वाटाघाटी त्याला चांगल्या जुळतात. त्याची देणगी म्हणजे आरपार समज; शिकवण म्हणजे ती अंतर्दृष्टी आलिंगन देण्यासाठी आणि बरे करण्यासाठी वापरावी, सापाच्या वेटोळ्याप्रमाणे जे रक्षण करते.",
    # EN: Magha is ruled by the Pitris, the ancestors, and symbolised by a royal throne. People with
    #     the Moon here often carry a natural dignity, a respect for family and tradition, and a
    #     wish to live up to the name they were given. They can be generous leaders who take
    #     responsibility for their people. Tradition links Magha with lineage, honour and authority,
    #     so leadership, administration, history, law and work that preserves heritage suit it well.
    #     Its gift is nobility of heart; its lesson is to wear the crown lightly — to lead through
    #     service and to honour the ancestors through good deeds.
    "magha": "मघाचे स्वामी पितर, म्हणजे पूर्वज आहेत, आणि त्याचे प्रतीक राजसिंहासन आहे. ज्यांचा चंद्र इथे असतो त्यांच्यात अनेकदा सहज प्रतिष्ठा, कुटुंब आणि परंपरेबद्दल आदर, आणि आपल्याला मिळालेल्या नावाला जागण्याची इच्छा असते. ते आपल्या माणसांची जबाबदारी घेणारे उदार नेते असू शकतात. परंपरा मघाला वंश, सन्मान आणि अधिकाराशी जोडते, म्हणून नेतृत्व, प्रशासन, इतिहास, कायदा आणि वारसा जपणारे काम त्याला चांगले जुळते. त्याची देणगी म्हणजे मनाचे मोठेपण; शिकवण म्हणजे मुकुट हलकेपणाने धारण करावा — सेवेतून नेतृत्व करावे आणि चांगल्या कर्मांतून पूर्वजांचा सन्मान करावा.",
    # EN: Purva Phalguni is ruled by Bhaga, the god of fortune and marital happiness, and symbolised
    #     by the front legs of a bed — an image of rest and enjoyment. People with the Moon here are
    #     often warm, charming, creative and fond of celebration, music and good company. They bring
    #     people together and know how to relax and enjoy what they have earned. Tradition links
    #     Purva Phalguni with love, the arts and leisure, so entertainment, design, hospitality and
    #     relationship-centred work suit it well. Its gift is joy that is easily shared; its lesson
    #     is balance between pleasure and duty.
    "purva-phalguni": "पूर्वा फाल्गुनीचा स्वामी सौभाग्य आणि वैवाहिक सुखाचा देव भग आहे, आणि त्याचे प्रतीक पलंगाचे पुढचे पाय आहे — विश्रांती आणि उपभोगाची प्रतिमा. ज्यांचा चंद्र इथे असतो ते अनेकदा उबदार, आकर्षक, सर्जनशील आणि उत्सव, संगीत व चांगली संगत आवडणारे असतात. ते लोकांना एकत्र आणतात आणि मिळवलेल्याचा आनंद कसा घ्यावा हे जाणतात. परंपरा पूर्वा फाल्गुनीला प्रेम, कला आणि फुरसतीशी जोडते, म्हणून मनोरंजन, रचना, आतिथ्य आणि नात्यांवर केंद्रित काम त्याला चांगले जुळते. त्याची देणगी म्हणजे सहज वाटून घेता येणारा आनंद; शिकवण म्हणजे सुख आणि कर्तव्य यांचा समतोल.",
    # EN: Uttara Phalguni is ruled by Aryaman, the god of friendship, contracts and marriage vows,
    #     and symbolised by the back legs of a bed. Where its twin Purva Phalguni enjoys, Uttara
    #     Phalguni commits. People with the Moon here are often reliable, helpful, fair-minded and
    #     loyal to friends and partners. They keep their word and like to be of real use to others.
    #     Tradition links this nakshatra with patronage and lasting partnerships, so management,
    #     public service, counselling, law and charitable work suit it well. Its gift is dependable
    #     kindness; its lesson is to accept help as gracefully as it is given.
    "uttara-phalguni": "उत्तरा फाल्गुनीचा स्वामी मैत्री, करार आणि विवाह-शपथांचा देव अर्यमा आहे, आणि त्याचे प्रतीक पलंगाचे मागचे पाय आहे. जिथे त्याची जोडीदार पूर्वा फाल्गुनी उपभोग घेते, तिथे उत्तरा फाल्गुनी वचनबद्ध होते. ज्यांचा चंद्र इथे असतो ते अनेकदा विश्वासार्ह, उपयोगी पडणारे, न्यायी आणि मित्र व जोडीदारांशी निष्ठावान असतात. ते दिलेला शब्द पाळतात आणि इतरांच्या खरोखर उपयोगी पडायला आवडतात. परंपरा या नक्षत्राला आश्रय देणे आणि टिकणाऱ्या भागीदारीशी जोडते, म्हणून व्यवस्थापन, लोकसेवा, समुपदेशन, कायदा आणि धर्मादाय कार्य त्याला चांगले जुळते. त्याची देणगी म्हणजे भरवशाची दयाळूपणा; शिकवण म्हणजे मदत जितक्या कृपेने दिली जाते तितक्याच कृपेने स्वीकारावी.",
    # EN: Hasta is ruled by Savitr, the radiant Sun, and symbolised by a hand. People with the Moon
    #     here are often skilful, practical, witty and clever with their hands as well as their
    #     minds. They like to get things done and can turn an idea into something real. Tradition
    #     links Hasta with craftsmanship, healing touch and resourcefulness, so crafts, the arts,
    #     surgery, massage, writing, trade and any skilled trade suit it well. Its gift is the
    #     ability to make and to mend; its lesson is to hold things with an open hand, trusting that
    #     effort brings its own rewards.
    "hasta": "हस्ताचा स्वामी तेजस्वी सूर्य सवितृ आहे, आणि त्याचे प्रतीक हात आहे. ज्यांचा चंद्र इथे असतो ते अनेकदा कुशल, व्यवहारी, विनोदी आणि मनाइतकेच हातांनीही हुशार असतात. त्यांना कामे पूर्ण करायला आवडते आणि कल्पनेला प्रत्यक्ष रूप देता येते. परंपरा हस्ताला कारागिरी, उपचारक स्पर्श आणि कल्पकतेशी जोडते, म्हणून हस्तकला, कला, शस्त्रक्रिया, मालिश, लेखन, व्यापार आणि कोणताही कौशल्याचा व्यवसाय त्याला चांगला जुळतो. त्याची देणगी म्हणजे घडवण्याची आणि दुरुस्त करण्याची क्षमता; शिकवण म्हणजे गोष्टी मोकळ्या हाताने धराव्यात, प्रयत्नांना स्वतःचे फळ मिळते यावर विश्वास ठेवून.",
    # EN: Chitra is ruled by Tvashtr, also known as Vishwakarma, the divine architect, and
    #     symbolised by a bright jewel. Its name means "brilliant" or "picture", and people with the
    #     Moon here often have a strong sense of beauty, design and form. They enjoy creating things
    #     that are both useful and attractive, and they notice detail. Tradition links Chitra with
    #     architecture, the arts and craftsmanship, so design, engineering, fashion, jewellery,
    #     photography and planning suit it well. Its gift is the eye of an artist and the hand of a
    #     builder; its lesson is to value inner beauty as much as outer polish.
    "chitra": "चित्राचा स्वामी विश्वकर्मा म्हणूनही ओळखला जाणारा, दिव्य शिल्पकार त्वष्टा आहे, आणि त्याचे प्रतीक तेजस्वी रत्न आहे. त्याच्या नावाचा अर्थ “तेजस्वी” किंवा “चित्र” आहे, आणि ज्यांचा चंद्र इथे असतो त्यांच्यात अनेकदा सौंदर्य, रचना आणि आकाराची तीव्र जाण असते. उपयुक्त आणि आकर्षक अशा गोष्टी घडवायला त्यांना आवडते, आणि त्यांचे तपशिलाकडे लक्ष असते. परंपरा चित्राला वास्तुकला, कला आणि कारागिरीशी जोडते, म्हणून रचना, अभियांत्रिकी, फॅशन, दागिने, छायाचित्रण आणि नियोजन त्याला चांगले जुळते. त्याची देणगी म्हणजे कलाकाराची नजर आणि बांधकाम करणाऱ्याचा हात; शिकवण म्हणजे बाह्य झळाळीइतकेच अंतरंगाच्या सौंदर्यालाही महत्त्व द्यावे.",
    # EN: Swati is ruled by Vayu, the wind, and symbolised by a young shoot swaying in the breeze —
    #     flexible, independent and able to bend without breaking. People with the Moon here often
    #     value freedom, fairness and their own way of doing things. They are usually diplomatic,
    #     courteous and good at business and negotiation. Tradition links Swati with trade, travel
    #     and self-reliance, so commerce, law, diplomacy, communication and independent work suit it
    #     well. Its gift is adaptability and a gentle, balanced manner; its lesson is to put down
    #     roots, so that the young shoot can grow into a strong tree.
    "swati": "स्वातीचा स्वामी वारा, म्हणजे वायू आहे, आणि त्याचे प्रतीक झुळकेत डोलणारा कोवळा अंकुर आहे — लवचिक, स्वतंत्र आणि न तुटता वाकू शकणारा. ज्यांचा चंद्र इथे असतो ते अनेकदा स्वातंत्र्य, न्याय आणि स्वतःची काम करण्याची पद्धत यांना महत्त्व देतात. ते सहसा मुत्सद्दी, सभ्य आणि व्यवसाय व वाटाघाटीत कुशल असतात. परंपरा स्वातीला व्यापार, प्रवास आणि स्वावलंबनाशी जोडते, म्हणून वाणिज्य, कायदा, मुत्सद्देगिरी, संवाद आणि स्वतंत्र काम त्याला चांगले जुळते. त्याची देणगी म्हणजे अनुकूलन आणि सौम्य, संतुलित वागणूक; शिकवण म्हणजे मुळे रुजवावीत, म्हणजे कोवळा अंकुर मजबूत वृक्ष होऊ शकेल.",
    # EN: Vishakha is ruled by Indra and Agni together, and symbolised by a triumphal arch decorated
    #     with leaves. People with the Moon here are often purposeful, ambitious and determined to
    #     reach the goal they have set. They have energy, conviction and the patience to keep going
    #     over a long road. Tradition calls Vishakha the nakshatra of purpose, so leadership,
    #     research, politics, sales, teaching and any long-term mission suit it well. Its gift is
    #     focus and the ability to inspire others towards a shared aim; its lesson is to enjoy the
    #     journey, not only the arch at its end.
    "vishakha": "विशाखाचे स्वामी इंद्र आणि अग्नी दोघे मिळून आहेत, आणि त्याचे प्रतीक पानांनी सजवलेले विजयतोरण आहे. ज्यांचा चंद्र इथे असतो ते अनेकदा ध्येयनिष्ठ, महत्त्वाकांक्षी आणि ठरवलेले ध्येय गाठण्याचा निश्चय असलेले असतात. त्यांच्यात ऊर्जा, ठाम विश्वास आणि लांबच्या वाटेवर चालत राहण्याचा संयम असतो. परंपरा विशाखाला उद्देशाचे नक्षत्र म्हणते, म्हणून नेतृत्व, संशोधन, राजकारण, विक्री, शिकवणे आणि कोणतीही दीर्घकालीन मोहीम त्याला चांगली जुळते. त्याची देणगी म्हणजे एकाग्रता आणि इतरांना समान ध्येयाकडे प्रेरित करण्याची क्षमता; शिकवण म्हणजे प्रवासाचाही आनंद घ्यावा, केवळ त्याच्या शेवटच्या तोरणाचा नाही.",
    # EN: Anuradha is ruled by Mitra, the god of friendship and cooperation, and symbolised by a
    #     lotus that blooms out of muddy water. People with the Moon here are often loyal friends,
    #     devoted to their ideals and able to keep going with quiet faith in difficult places. They
    #     are good at bringing people together in groups and organisations. Tradition links Anuradha
    #     with friendship, devotion and success away from home, so teamwork, organisation,
    #     counselling, travel and spiritual practice suit it well. Its gift is the ability to
    #     blossom anywhere; its lesson is to be as gentle with oneself as with friends.
    "anuradha": "अनुराधाचा स्वामी मैत्री आणि सहकार्याचा देव मित्र आहे, आणि त्याचे प्रतीक चिखलाच्या पाण्यातून फुलणारे कमळ आहे. ज्यांचा चंद्र इथे असतो ते अनेकदा निष्ठावान मित्र, आपल्या आदर्शांना समर्पित आणि कठीण ठिकाणीही शांत श्रद्धेने पुढे चालत राहणारे असतात. गट आणि संस्थांमध्ये लोकांना एकत्र आणण्यात ते कुशल असतात. परंपरा अनुराधाला मैत्री, भक्ती आणि घरापासून दूर मिळणाऱ्या यशाशी जोडते, म्हणून सांघिक काम, संघटन, समुपदेशन, प्रवास आणि आध्यात्मिक साधना त्याला चांगली जुळते. त्याची देणगी म्हणजे कुठेही फुलण्याची क्षमता; शिकवण म्हणजे मित्रांशी जितके सौम्य वागतो तितकेच स्वतःशीही वागावे.",
    # EN: Jyeshtha is ruled by Indra, king of the gods, and symbolised by a circular amulet or
    #     earring. Its name means "the eldest", and people with the Moon here often take on
    #     responsibility early, protect those around them and carry a quiet authority. They are
    #     resourceful, perceptive and capable under pressure. Tradition links Jyeshtha with
    #     seniority and protection, so leadership, management, administration, security and any role
    #     that looks after others suit it well. Its gift is courage and capability; its lesson is to
    #     lead with humility and to let others share the load rather than carrying everything alone.
    "jyeshtha": "ज्येष्ठाचा स्वामी देवांचा राजा इंद्र आहे, आणि त्याचे प्रतीक गोलाकार ताईत किंवा कर्णभूषण आहे. त्याच्या नावाचा अर्थ “सर्वात मोठा” आहे, आणि ज्यांचा चंद्र इथे असतो ते अनेकदा लहान वयातच जबाबदारी घेतात, आसपासच्यांचे रक्षण करतात आणि शांत अधिकार बाळगतात. ते कल्पक, चाणाक्ष आणि दबावाखाली सक्षम असतात. परंपरा ज्येष्ठाला ज्येष्ठत्व आणि संरक्षणाशी जोडते, म्हणून नेतृत्व, व्यवस्थापन, प्रशासन, सुरक्षा आणि इतरांची काळजी घेणारी कोणतीही भूमिका त्याला चांगली जुळते. त्याची देणगी म्हणजे धैर्य आणि सामर्थ्य; शिकवण म्हणजे नम्रतेने नेतृत्व करावे आणि सर्व काही एकट्याने वाहण्याऐवजी इतरांनाही भार वाटून घेऊ द्यावा.",
    # EN: Mula is ruled by Nirriti and symbolised by a bunch of roots. Its name means "the root",
    #     and people with the Moon here are often drawn to get to the bottom of things — to find the
    #     origin of a question, an idea or a tradition. They can be independent, philosophical and
    #     unafraid to start again from first principles. Tradition links Mula with investigation and
    #     with letting go of what is no longer needed, so research, medicine, philosophy, botany and
    #     spiritual inquiry suit it well. Its gift is depth; its lesson is that clearing old ground
    #     makes room for new growth.
    "mula": "मूळाचा स्वामी निर्ऋती आहे, आणि त्याचे प्रतीक मुळांचा गुच्छ आहे. त्याच्या नावाचा अर्थ “मूळ” आहे, आणि ज्यांचा चंद्र इथे असतो त्यांना अनेकदा गोष्टींच्या तळाशी जाण्याची ओढ असते — एखाद्या प्रश्नाचे, कल्पनेचे किंवा परंपरेचे उगमस्थान शोधण्याची. ते स्वतंत्र, तत्त्वचिंतक आणि मूलभूत तत्त्वांपासून पुन्हा सुरुवात करायला न घाबरणारे असू शकतात. परंपरा मूळाला अन्वेषण आणि जे आता नको आहे ते सोडून देण्याशी जोडते, म्हणून संशोधन, वैद्यकीय क्षेत्र, तत्त्वज्ञान, वनस्पतिशास्त्र आणि आध्यात्मिक शोध त्याला चांगले जुळतात. त्याची देणगी म्हणजे खोली; शिकवण म्हणजे जुनी जमीन साफ केल्याने नव्या वाढीला जागा होते.",
    # EN: Purva Ashadha is ruled by Apas, the cosmic waters, and symbolised by a winnowing fan or an
    #     elephant tusk. Its name means "the early invincible", and people with the Moon here are
    #     often confident, persuasive and full of conviction. Like water, they can be gentle and yet
    #     wear down any obstacle in time. Tradition links Purva Ashadha with purification and with
    #     victory won through persistence, so teaching, law, debate, the arts, shipping and anything
    #     to do with water suit it well. Its gift is optimism and inner strength; its lesson is to
    #     stay open to other views while holding firm to its own.
    "purva-ashadha": "पूर्वाषाढाचा स्वामी विश्वातील जल, म्हणजे आपस आहे, आणि त्याचे प्रतीक सूप किंवा हत्तीचा सुळा आहे. त्याच्या नावाचा अर्थ “आधीचा अजिंक्य” आहे, आणि ज्यांचा चंद्र इथे असतो ते अनेकदा आत्मविश्वासू, पटवून देणारे आणि ठाम विश्वासाने भरलेले असतात. पाण्याप्रमाणे ते सौम्य असूनही कालांतराने कोणत्याही अडथळ्याला झिजवू शकतात. परंपरा पूर्वाषाढाला शुद्धीकरण आणि चिकाटीने मिळवलेल्या विजयाशी जोडते, म्हणून शिकवणे, कायदा, वादविवाद, कला, जलवाहतूक आणि पाण्याशी संबंधित प्रत्येक गोष्ट त्याला चांगली जुळते. त्याची देणगी म्हणजे आशावाद आणि आंतरिक बळ; शिकवण म्हणजे स्वतःच्या मतावर ठाम राहूनही इतरांच्या मतांसाठी खुले राहावे.",
    # EN: Uttara Ashadha is ruled by the Vishvedevas, the universal gods, and symbolised by an
    #     elephant tusk. Its name means "the later invincible" — the victory that lasts because it
    #     was earned honestly. People with the Moon here are often principled, patient, responsible
    #     and respected for their integrity. They take the long view and finish what they commit to.
    #     Tradition links Uttara Ashadha with righteous leadership, so government, management, law,
    #     teaching and social causes suit it well. Its gift is steady, ethical strength; its lesson
    #     is to keep a little lightness and warmth alongside the seriousness of duty.
    "uttara-ashadha": "उत्तराषाढाचे स्वामी विश्वदेव, म्हणजे विश्वातील देवता आहेत, आणि त्याचे प्रतीक हत्तीचा सुळा आहे. त्याच्या नावाचा अर्थ “नंतरचा अजिंक्य” आहे — प्रामाणिकपणे कमावल्यामुळे टिकणारा विजय. ज्यांचा चंद्र इथे असतो ते अनेकदा तत्त्वनिष्ठ, संयमी, जबाबदार आणि सचोटीबद्दल आदरणीय असतात. ते दूरचा विचार करतात आणि हाती घेतलेले पूर्ण करतात. परंपरा उत्तराषाढाला धर्मनिष्ठ नेतृत्वाशी जोडते, म्हणून सरकारी सेवा, व्यवस्थापन, कायदा, शिकवणे आणि सामाजिक कार्य त्याला चांगले जुळते. त्याची देणगी म्हणजे स्थिर, नैतिक बळ; शिकवण म्हणजे कर्तव्याच्या गांभीर्यासोबत थोडा हलकेपणा आणि उबदारपणा जपावा.",
    # EN: Shravana is ruled by Vishnu, the preserver, and symbolised by an ear or three footprints.
    #     Its name means "hearing", and people with the Moon here are often good listeners, eager
    #     learners and keepers of knowledge and tradition. They learn by listening and pass on what
    #     they have learned. Tradition links Shravana with wisdom gained through study and with
    #     connecting people, so teaching, counselling, media, languages, music and travel suit it
    #     well. Its gift is attentive understanding and a wish to be useful; its lesson is to listen
    #     to one's own inner voice as carefully as to others.
    "shravana": "श्रवणाचा स्वामी पालनकर्ता विष्णू आहे, आणि त्याचे प्रतीक कान किंवा तीन पदचिन्हे आहे. त्याच्या नावाचा अर्थ “ऐकणे” आहे, आणि ज्यांचा चंद्र इथे असतो ते अनेकदा चांगले श्रोते, शिकण्यास उत्सुक आणि ज्ञान व परंपरा जपणारे असतात. ते ऐकून शिकतात आणि शिकलेले पुढे देतात. परंपरा श्रवणाला अभ्यासातून मिळणारे ज्ञान आणि लोकांना जोडण्याशी जोडते, म्हणून शिकवणे, समुपदेशन, माध्यमे, भाषा, संगीत आणि प्रवास त्याला चांगले जुळतात. त्याची देणगी म्हणजे लक्षपूर्वक समजून घेणे आणि उपयोगी पडण्याची इच्छा; शिकवण म्हणजे इतरांचे जितके काळजीपूर्वक ऐकतो तितकेच स्वतःच्या अंतर्मनाचा आवाजही ऐकावा.",
    # EN: Dhanishta is ruled by the eight Vasus, gods of abundance, and symbolised by a drum. Its
    #     name means "the wealthiest", and people with the Moon here often have rhythm, energy and a
    #     talent for music, dance or teamwork. They are generous, sociable and able to keep a group
    #     moving together. Tradition links Dhanishta with prosperity and with sound, so music,
    #     performance, sport, property, finance and community work suit it well. Its gift is the
    #     ability to set the beat that others follow; its lesson is to listen as well as play,
    #     leaving space for others' rhythms.
    "dhanishta": "धनिष्ठाचे स्वामी समृद्धीचे देव, आठ वसू आहेत, आणि त्याचे प्रतीक ढोल आहे. त्याच्या नावाचा अर्थ “सर्वात धनवान” आहे, आणि ज्यांचा चंद्र इथे असतो त्यांच्यात अनेकदा लय, ऊर्जा आणि संगीत, नृत्य किंवा सांघिक कामाची प्रतिभा असते. ते उदार, मिलनसार आणि गटाला एकत्र पुढे नेण्यास सक्षम असतात. परंपरा धनिष्ठाला समृद्धी आणि नादाशी जोडते, म्हणून संगीत, सादरीकरण, खेळ, मालमत्ता, वित्त आणि समाजकार्य त्याला चांगले जुळते. त्याची देणगी म्हणजे इतर ज्याचे अनुसरण करतात तो ठेका धरण्याची क्षमता; शिकवण म्हणजे वाजवण्याबरोबर ऐकावेही, इतरांच्या लयीला जागा सोडून.",
    # EN: Shatabhisha is ruled by Varuna, lord of the cosmic waters and of truth, and symbolised by
    #     an empty circle. Its name means "a hundred healers", and people with the Moon here are
    #     often independent thinkers, private, truthful and drawn to understanding how things really
    #     work. They can see patterns others miss. Tradition links Shatabhisha with healing and with
    #     the search for hidden truth, so medicine, research, science, technology, astronomy and
    #     alternative healing suit it well. Its gift is clear, original insight; its lesson is to
    #     let others into the circle, sharing what is understood with warmth.
    "shatabhisha": "शततारकेचा स्वामी विश्वातील जल आणि सत्याचा अधिपती वरुण आहे, आणि त्याचे प्रतीक रिकामे वर्तुळ आहे. त्याच्या नावाचा अर्थ “शंभर वैद्य” आहे, आणि ज्यांचा चंद्र इथे असतो ते अनेकदा स्वतंत्र विचारवंत, खाजगी स्वभावाचे, सत्यवादी आणि गोष्टी प्रत्यक्षात कशा चालतात हे समजून घेण्याची ओढ असलेले असतात. इतरांना न दिसणारे नमुने ते पाहू शकतात. परंपरा शततारकेला उपचार आणि दडलेल्या सत्याच्या शोधाशी जोडते, म्हणून वैद्यकीय क्षेत्र, संशोधन, विज्ञान, तंत्रज्ञान, खगोलशास्त्र आणि पर्यायी उपचार त्याला चांगले जुळतात. त्याची देणगी म्हणजे स्पष्ट, मौलिक अंतर्दृष्टी; शिकवण म्हणजे इतरांना वर्तुळात येऊ द्यावे, जे समजले ते उबदारपणे वाटून घ्यावे.",
    # EN: Purva Bhadrapada is ruled by Aja Ekapada, the one-footed form of Shiva, and symbolised by
    #     swords or the front legs of a cot. People with the Moon here are often idealistic, intense
    #     and willing to give themselves fully to a cause they believe in. They can be eloquent,
    #     generous and deeply spiritual. Tradition links Purva Bhadrapada with transformation and
    #     with the fire of tapas — sincere effort for a higher aim — so social reform, philosophy,
    #     writing, research and spiritual life suit it well. Its gift is passionate commitment; its
    #     lesson is to temper intensity with patience and calm.
    "purva-bhadrapada": "पूर्वा भाद्रपदेचा स्वामी शिवाचे एकपाद रूप अज एकपाद आहे, आणि त्याचे प्रतीक तलवारी किंवा खाटेचे पुढचे पाय आहे. ज्यांचा चंद्र इथे असतो ते अनेकदा आदर्शवादी, तीव्र आणि आपल्या श्रद्धेच्या कार्यासाठी स्वतःला पूर्णपणे झोकून देण्यास तयार असतात. ते वक्तृत्ववान, उदार आणि खोलवर आध्यात्मिक असू शकतात. परंपरा पूर्वा भाद्रपदेला परिवर्तन आणि तपाच्या अग्नीशी — उच्च ध्येयासाठीच्या प्रामाणिक प्रयत्नाशी — जोडते, म्हणून समाजसुधारणा, तत्त्वज्ञान, लेखन, संशोधन आणि आध्यात्मिक जीवन त्याला चांगले जुळते. त्याची देणगी म्हणजे उत्कट वचनबद्धता; शिकवण म्हणजे तीव्रतेला संयम आणि शांततेची जोड द्यावी.",
    # EN: Uttara Bhadrapada is ruled by Ahir Budhnya, the serpent of the deep waters, and symbolised
    #     by the back legs of a cot or twins. Where Purva Bhadrapada burns, Uttara Bhadrapada
    #     settles into calm depth. People with the Moon here are often wise, patient, composed and
    #     compassionate, with self-control and a gift for counsel. They tend to think before they
    #     speak and are steady in difficult times. Tradition links this nakshatra with depth,
    #     renunciation and kindness, so counselling, charity, teaching, research and spiritual
    #     practice suit it well. Its gift is serene wisdom; its lesson is to share it actively, not
    #     only privately.
    "uttara-bhadrapada": "उत्तरा भाद्रपदेचा स्वामी खोल पाण्यातील सर्प अहिर्बुध्न्य आहे, आणि त्याचे प्रतीक खाटेचे मागचे पाय किंवा जुळे आहे. जिथे पूर्वा भाद्रपदा जळते, तिथे उत्तरा भाद्रपदा शांत खोलीत स्थिरावते. ज्यांचा चंद्र इथे असतो ते अनेकदा ज्ञानी, संयमी, शांत आणि करुणामय असतात, आत्मसंयम आणि सल्ला देण्याची देणगी असलेले. ते बोलण्यापूर्वी विचार करतात आणि कठीण काळात स्थिर राहतात. परंपरा या नक्षत्राला खोली, त्याग आणि दयाळूपणाशी जोडते, म्हणून समुपदेशन, दानधर्म, शिकवणे, संशोधन आणि आध्यात्मिक साधना त्याला चांगली जुळते. त्याची देणगी म्हणजे शांत ज्ञान; शिकवण म्हणजे ते केवळ एकांतात न ठेवता सक्रियपणे वाटावे.",
    # EN: Revati, the last nakshatra, is ruled by Pushan, the nourisher who guides travellers and
    #     protects herds on their way, and symbolised by a fish. People with the Moon here are often
    #     gentle, kind, imaginative and protective of the weak, with a love of animals, art and
    #     music. They make good companions on any journey and help others reach their destination
    #     safely. Tradition links Revati with safe journeys, prosperity and completion, so caring
    #     work, the arts, travel, hospitality and spiritual life suit it well. Its gift is
    #     compassion and faith; its lesson is to care for oneself while caring for everyone else.
    "revati": "रेवती, शेवटचे नक्षत्र, याचा स्वामी प्रवाशांना मार्ग दाखवणारा आणि गुरांचे वाटेवर रक्षण करणारा पोषणकर्ता पूषा आहे, आणि त्याचे प्रतीक मासा आहे. ज्यांचा चंद्र इथे असतो ते अनेकदा सौम्य, दयाळू, कल्पक आणि दुर्बलांचे रक्षण करणारे असतात, प्राणी, कला आणि संगीताची आवड असलेले. ते कोणत्याही प्रवासात चांगले सोबती ठरतात आणि इतरांना सुरक्षित ठिकाणी पोहोचण्यास मदत करतात. परंपरा रेवतीला सुरक्षित प्रवास, समृद्धी आणि पूर्णतेशी जोडते, म्हणून काळजी घेणारे काम, कला, प्रवास, आतिथ्य आणि आध्यात्मिक जीवन त्याला चांगले जुळते. त्याची देणगी म्हणजे करुणा आणि श्रद्धा; शिकवण म्हणजे इतर सर्वांची काळजी घेताना स्वतःचीही काळजी घ्यावी.",
}

# app/nakshatra_text.py RASHI_TRAITS["mr"] — character paragraph of each of the 12 rashis (key = slug)  [12]
RASHI_TRAITS = {
    # EN: Mesh (Aries) is the first rashi, a movable fire sign ruled by Mars. People with the Moon
    #     in Mesh are often energetic, direct, courageous and quick to act — natural starters who
    #     enjoy a challenge and like to lead from the front. They are honest about their feelings
    #     and recover quickly from setbacks. Their emotional life is warm and spontaneous, and they
    #     bring enthusiasm wherever they go. Work that rewards initiative — sport, the armed forces,
    #     engineering, entrepreneurship, surgery — often suits them. Their growth lies in patience
    #     and in listening before acting, so that their courage is matched by care for others.
    "mesh": "मेष ही पहिली रास आहे, मंगळ स्वामी असलेली चर अग्नितत्त्वाची रास. मेषेत चंद्र असलेले लोक अनेकदा उत्साही, सरळ, धाडसी आणि पटकन कृती करणारे असतात — जन्मजात सुरुवात करणारे, ज्यांना आव्हान आवडते आणि जे पुढे राहून नेतृत्व करतात. ते आपल्या भावनांबद्दल प्रामाणिक असतात आणि धक्क्यांतून लवकर सावरतात. त्यांचे भावनिक जीवन उबदार आणि उत्स्फूर्त असते, आणि ते जिथे जातात तिथे उत्साह घेऊन जातात. पुढाकाराला बक्षीस देणारे काम — खेळ, सैन्यदल, अभियांत्रिकी, उद्योजकता, शस्त्रक्रिया — त्यांना अनेकदा जुळते. त्यांची वाढ संयमात आणि कृतीपूर्वी ऐकण्यात आहे, म्हणजे त्यांच्या धैर्याला इतरांच्या काळजीची जोड मिळेल.",
    # EN: Vrishabh (Taurus) is a fixed earth sign ruled by Venus, and the Moon is exalted here.
    #     People with the Moon in Vrishabh are often calm, patient, loyal and steady, with a love of
    #     comfort, good food, music and beautiful things. They build slowly and surely, and what
    #     they build tends to last. Emotionally they are dependable and affectionate, preferring
    #     security to drama. Finance, agriculture, the arts, food, design and any work that rewards
    #     persistence often suit them. Their growth lies in flexibility — welcoming change when it
    #     comes, and holding possessions and opinions a little more lightly.
    "vrishabh": "वृषभ ही शुक्र स्वामी असलेली स्थिर पृथ्वीतत्त्वाची रास आहे, आणि चंद्र येथे उच्चीचा असतो. वृषभेत चंद्र असलेले लोक अनेकदा शांत, संयमी, निष्ठावान आणि स्थिर असतात, सुखसोयी, चांगले जेवण, संगीत आणि सुंदर वस्तूंची आवड असलेले. ते हळूहळू पण खात्रीने उभारणी करतात आणि जे उभारतात ते टिकते. भावनिकदृष्ट्या ते भरवशाचे आणि प्रेमळ असतात, नाट्यापेक्षा सुरक्षिततेला प्राधान्य देणारे. वित्त, शेती, कला, अन्न, रचना आणि चिकाटीला बक्षीस देणारे कोणतेही काम त्यांना अनेकदा जुळते. त्यांची वाढ लवचिकतेत आहे — बदल आला की त्याचे स्वागत करणे, आणि वस्तू व मते थोडी हलकेपणाने धरणे.",
    # EN: Mithun (Gemini) is a dual air sign ruled by Mercury. People with the Moon in Mithun are
    #     often curious, witty, talkative and quick to learn, with many interests and a gift for
    #     connecting ideas and people. They enjoy conversation, reading, travel and anything that
    #     keeps the mind busy. Emotionally they need variety and a partner who is also a friend they
    #     can talk to. Writing, teaching, media, sales, technology and trade often suit them. Their
    #     growth lies in depth and focus — choosing a few things and seeing them through — and in
    #     giving their own feelings the attention they give to ideas.
    "mithun": "मिथुन ही बुध स्वामी असलेली द्विस्वभाव वायुतत्त्वाची रास आहे. मिथुनेत चंद्र असलेले लोक अनेकदा जिज्ञासू, विनोदी, बोलके आणि पटकन शिकणारे असतात, अनेक आवडी आणि कल्पना व माणसे जोडण्याची देणगी असलेले. त्यांना संभाषण, वाचन, प्रवास आणि मन व्यग्र ठेवणारी प्रत्येक गोष्ट आवडते. भावनिकदृष्ट्या त्यांना वैविध्य हवे असते आणि असा जोडीदार हवा जो मित्र असेल आणि ज्याच्याशी ते बोलू शकतील. लेखन, शिकवणे, माध्यमे, विक्री, तंत्रज्ञान आणि व्यापार त्यांना अनेकदा जुळतात. त्यांची वाढ खोलीत आणि एकाग्रतेत आहे — थोड्या गोष्टी निवडून त्या पूर्ण करणे — आणि कल्पनांना देतात तेवढेच लक्ष स्वतःच्या भावनांना देणे.",
    # EN: Kark (Cancer) is a movable water sign ruled by the Moon itself, so the Moon is at home
    #     here. People with the Moon in Kark are often caring, sensitive, intuitive and devoted to
    #     family and home. They remember kindness, protect those they love and create warmth
    #     wherever they live. Their moods can change like the tides, but their loyalty runs deep.
    #     Nursing, teaching, hospitality, food, real estate, counselling and public service often
    #     suit them. Their growth lies in trusting their own strength, letting go of old hurts and
    #     allowing others to care for them in return.
    "kark": "कर्क ही स्वतः चंद्र स्वामी असलेली चर जलतत्त्वाची रास आहे, म्हणून चंद्र येथे स्वगृही असतो. कर्केत चंद्र असलेले लोक अनेकदा काळजी घेणारे, संवेदनशील, अंतर्ज्ञानी आणि कुटुंब व घराला समर्पित असतात. ते दयाळूपणा लक्षात ठेवतात, प्रिय व्यक्तींचे रक्षण करतात आणि जिथे राहतात तिथे ऊब निर्माण करतात. त्यांची मनःस्थिती भरती-ओहोटीसारखी बदलू शकते, पण त्यांची निष्ठा खोलवर असते. परिचर्या, शिकवणे, आतिथ्य, अन्न, स्थावर मालमत्ता, समुपदेशन आणि लोकसेवा त्यांना अनेकदा जुळतात. त्यांची वाढ स्वतःच्या बळावर विश्वास ठेवण्यात, जुन्या दुखावलेपणाला सोडण्यात आणि बदल्यात इतरांना आपली काळजी घेऊ देण्यात आहे.",
    # EN: Simha (Leo) is a fixed fire sign ruled by the Sun. People with the Moon in Simha are often
    #     generous, dignified, confident and warm-hearted, with a natural sense of leadership and a
    #     love of recognition. They are loyal to those who trust them and protective of their family
    #     and friends. Emotionally they are proud and open-hearted, and they shine when appreciated.
    #     Leadership, administration, politics, the performing arts, teaching and government service
    #     often suit them. Their growth lies in humility — letting others share the stage, and
    #     finding confidence from within rather than from applause.
    "simha": "सिंह ही सूर्य स्वामी असलेली स्थिर अग्नितत्त्वाची रास आहे. सिंहेत चंद्र असलेले लोक अनेकदा उदार, प्रतिष्ठित, आत्मविश्वासू आणि मनमोकळे असतात, नेतृत्वाची जन्मजात जाण आणि कौतुकाची आवड असलेले. जे त्यांच्यावर विश्वास ठेवतात त्यांच्याशी ते निष्ठावान असतात आणि कुटुंब व मित्रांचे रक्षण करतात. भावनिकदृष्ट्या ते स्वाभिमानी आणि मोकळ्या मनाचे असतात, आणि कौतुक झाल्यावर ते चमकतात. नेतृत्व, प्रशासन, राजकारण, रंगमंचीय कला, शिकवणे आणि सरकारी सेवा त्यांना अनेकदा जुळतात. त्यांची वाढ नम्रतेत आहे — इतरांनाही मंचावर जागा देणे, आणि टाळ्यांऐवजी आतून आत्मविश्वास शोधणे.",
    # EN: Kanya (Virgo) is a dual earth sign ruled by Mercury. People with the Moon in Kanya are
    #     often practical, analytical, modest and helpful, with an eye for detail and a wish to make
    #     things work properly. They show care through service — fixing, organising and looking
    #     after the small things others overlook. Emotionally they can be reserved, but they are
    #     deeply dependable. Medicine, accounting, research, editing, nutrition, teaching and any
    #     precise craft often suit them. Their growth lies in self-acceptance: being as kind to
    #     their own imperfections as they are patient with other people's needs.
    "kanya": "कन्या ही बुध स्वामी असलेली द्विस्वभाव पृथ्वीतत्त्वाची रास आहे. कन्येत चंद्र असलेले लोक अनेकदा व्यवहारी, विश्लेषक, विनम्र आणि मदतीला तत्पर असतात, तपशिलाकडे लक्ष देणारे आणि गोष्टी नीट चालाव्यात अशी इच्छा असलेले. ते सेवेतून काळजी व्यक्त करतात — दुरुस्ती करणे, व्यवस्था लावणे आणि इतरांच्या नजरेतून सुटणाऱ्या लहान गोष्टींकडे लक्ष देणे. भावनिकदृष्ट्या ते राखीव असू शकतात, पण खोलवर भरवशाचे असतात. वैद्यकीय क्षेत्र, लेखा, संशोधन, संपादन, आहारशास्त्र, शिकवणे आणि कोणतीही काटेकोर कला त्यांना अनेकदा जुळते. त्यांची वाढ स्वतःला स्वीकारण्यात आहे: इतरांच्या गरजांबाबत जितके संयमी असतात तितकेच स्वतःच्या उणिवांबाबतही दयाळू राहणे.",
    # EN: Tula (Libra) is a movable air sign ruled by Venus, symbolised by the scales. People with
    #     the Moon in Tula are often gracious, fair-minded, sociable and diplomatic, with a strong
    #     sense of beauty and justice. They value harmony in relationships and are good at seeing
    #     both sides of a question. Emotionally they need partnership and feel most at ease when
    #     things around them are balanced. Law, diplomacy, design, fashion, the arts, counselling
    #     and business partnerships often suit them. Their growth lies in decisiveness — trusting
    #     their own judgement and accepting that a little disagreement can be healthy.
    "tula": "तूळ ही शुक्र स्वामी असलेली चर वायुतत्त्वाची रास आहे, ज्याचे प्रतीक तराजू आहे. तुळेत चंद्र असलेले लोक अनेकदा सुसंस्कृत, न्यायी, मिलनसार आणि मुत्सद्दी असतात, सौंदर्य आणि न्यायाची तीव्र जाण असलेले. त्यांना नात्यांतील सलोखा महत्त्वाचा वाटतो आणि प्रश्नाच्या दोन्ही बाजू पाहण्यात ते कुशल असतात. भावनिकदृष्ट्या त्यांना जोडीदार हवा असतो आणि आसपास समतोल असला की त्यांना सर्वात सहज वाटते. कायदा, मुत्सद्देगिरी, रचना, फॅशन, कला, समुपदेशन आणि व्यावसायिक भागीदारी त्यांना अनेकदा जुळतात. त्यांची वाढ निर्णायकतेत आहे — स्वतःच्या निर्णयावर विश्वास ठेवणे आणि थोडा मतभेद निरोगी असू शकतो हे स्वीकारणे.",
    # EN: Vrishchik (Scorpio) is a fixed water sign ruled by Mars. People with the Moon in Vrishchik
    #     are often intense, perceptive, determined and deeply loyal, with feelings that run far
    #     below the surface. They are not satisfied with appearances and want to understand what is
    #     really going on. Once they commit — to a person, a cause or a goal — they rarely let go.
    #     Research, investigation, medicine, psychology, finance and crisis work often suit them.
    #     Their growth lies in trust and forgiveness: letting others in, and allowing old feelings
    #     to transform rather than be held.
    "vrishchik": "वृश्चिक ही मंगळ स्वामी असलेली स्थिर जलतत्त्वाची रास आहे. वृश्चिकेत चंद्र असलेले लोक अनेकदा तीव्र, चाणाक्ष, निश्चयी आणि खोलवर निष्ठावान असतात, ज्यांच्या भावना पृष्ठभागाच्या खूप खाली वाहतात. ते दिखाव्याने समाधानी होत नाहीत आणि प्रत्यक्षात काय चालले आहे ते समजून घ्यायचे असते. एकदा त्यांनी बांधिलकी स्वीकारली — एखादी व्यक्ती, ध्येय किंवा उद्देश — की ते क्वचितच सोडतात. संशोधन, तपास, वैद्यकीय क्षेत्र, मानसशास्त्र, वित्त आणि संकटकालीन काम त्यांना अनेकदा जुळते. त्यांची वाढ विश्वास आणि क्षमेत आहे: इतरांना आत येऊ देणे, आणि जुन्या भावना धरून ठेवण्याऐवजी त्यांचे रूपांतर होऊ देणे.",
    # EN: Dhanu (Sagittarius) is a dual fire sign ruled by Jupiter, symbolised by the archer. People
    #     with the Moon in Dhanu are often optimistic, honest, generous and philosophical, with a
    #     love of learning, travel and freedom. They look for meaning in life and enjoy sharing what
    #     they have learned. Emotionally they are open and cheerful, and they need room to grow.
    #     Teaching, law, religion and philosophy, publishing, travel and sport often suit them.
    #     Their growth lies in following through — giving the same attention to the details of daily
    #     life that they give to big ideas and distant horizons.
    "dhanu": "धनु ही गुरू स्वामी असलेली द्विस्वभाव अग्नितत्त्वाची रास आहे, ज्याचे प्रतीक धनुर्धारी आहे. धनूत चंद्र असलेले लोक अनेकदा आशावादी, प्रामाणिक, उदार आणि तत्त्वचिंतक असतात, शिकणे, प्रवास आणि स्वातंत्र्याची आवड असलेले. ते जीवनाचा अर्थ शोधतात आणि जे शिकले ते वाटून घेणे त्यांना आवडते. भावनिकदृष्ट्या ते खुले आणि आनंदी असतात, आणि त्यांना वाढण्यासाठी जागा हवी असते. शिकवणे, कायदा, धर्म आणि तत्त्वज्ञान, प्रकाशन, प्रवास आणि खेळ त्यांना अनेकदा जुळतात. त्यांची वाढ पाठपुराव्यात आहे — मोठ्या कल्पना आणि दूरच्या क्षितिजांना देतात तेवढेच लक्ष रोजच्या जीवनाच्या तपशिलांनाही देणे.",
    # EN: Makar (Capricorn) is a movable earth sign ruled by Saturn. People with the Moon in Makar
    #     are often responsible, disciplined, practical and ambitious in a patient, long-term way.
    #     They take duty seriously, work steadily and earn respect over time. Emotionally they can
    #     seem reserved, but they show love through reliability and quiet support. Administration,
    #     management, engineering, government service, finance and any field that rewards
    #     perseverance often suit them. Their growth lies in warmth and rest — allowing themselves
    #     joy along the way, and remembering that their worth is not measured only by achievement.
    "makar": "मकर ही शनी स्वामी असलेली चर पृथ्वीतत्त्वाची रास आहे. मकरेत चंद्र असलेले लोक अनेकदा जबाबदार, शिस्तप्रिय, व्यवहारी आणि संयमी, दीर्घकालीन पद्धतीने महत्त्वाकांक्षी असतात. ते कर्तव्य गांभीर्याने घेतात, स्थिरपणे काम करतात आणि कालांतराने आदर मिळवतात. भावनिकदृष्ट्या ते राखीव वाटू शकतात, पण विश्वासार्हता आणि शांत आधाराद्वारे प्रेम व्यक्त करतात. प्रशासन, व्यवस्थापन, अभियांत्रिकी, सरकारी सेवा, वित्त आणि चिकाटीला बक्षीस देणारे कोणतेही क्षेत्र त्यांना अनेकदा जुळते. त्यांची वाढ ऊब आणि विश्रांतीत आहे — वाटेत स्वतःला आनंद घेऊ देणे, आणि आपली किंमत केवळ यशावरून मोजली जात नाही हे लक्षात ठेवणे.",
    # EN: Kumbh (Aquarius) is a fixed air sign ruled by Saturn, symbolised by the water-bearer who
    #     pours knowledge out for all. People with the Moon in Kumbh are often independent,
    #     humanitarian, inventive and loyal to friends and ideals. They think about the wider
    #     community and enjoy new ideas, science and reform. Emotionally they value friendship and
    #     freedom, and they show care through principle and action. Science, technology, social
    #     work, research, education and community organisations often suit them. Their growth lies
    #     in closeness — letting their warmth show to individuals as well as to humanity as a whole.
    "kumbh": "कुंभ ही शनी स्वामी असलेली स्थिर वायुतत्त्वाची रास आहे, ज्याचे प्रतीक सर्वांसाठी ज्ञान ओतणारा जलवाहक आहे. कुंभेत चंद्र असलेले लोक अनेकदा स्वतंत्र, मानवतावादी, संशोधक वृत्तीचे आणि मित्र व आदर्शांशी निष्ठावान असतात. ते व्यापक समाजाचा विचार करतात आणि नवीन कल्पना, विज्ञान व सुधारणा त्यांना आवडतात. भावनिकदृष्ट्या ते मैत्री आणि स्वातंत्र्याला महत्त्व देतात, आणि तत्त्व व कृतीतून काळजी व्यक्त करतात. विज्ञान, तंत्रज्ञान, समाजकार्य, संशोधन, शिक्षण आणि सामुदायिक संस्था त्यांना अनेकदा जुळतात. त्यांची वाढ जवळिकीत आहे — त्यांची ऊब संपूर्ण मानवतेसोबत व्यक्तींनाही दिसू देणे.",
    # EN: Meen (Pisces) is a dual water sign ruled by Jupiter, the last of the twelve rashis. People
    #     with the Moon in Meen are often compassionate, imaginative, gentle and spiritually
    #     inclined, with a deep sensitivity to the feelings of others. They forgive easily, help
    #     without being asked and are moved by music, art and devotion. Emotionally they are open-
    #     hearted and intuitive. Healing, counselling, the arts, music, charity, teaching and
    #     spiritual work often suit them. Their growth lies in healthy boundaries — caring for
    #     others without losing themselves, and turning their rich imagination into practical
    #     action.
    "meen": "मीन ही गुरू स्वामी असलेली द्विस्वभाव जलतत्त्वाची रास आहे, बारा राशींपैकी शेवटची. मीनेत चंद्र असलेले लोक अनेकदा करुणामय, कल्पक, सौम्य आणि आध्यात्मिक कल असलेले असतात, इतरांच्या भावनांबद्दल खोल संवेदनशीलता असलेले. ते सहज क्षमा करतात, न मागता मदत करतात आणि संगीत, कला व भक्तीने हेलावतात. भावनिकदृष्ट्या ते मोकळ्या मनाचे आणि अंतर्ज्ञानी असतात. उपचार, समुपदेशन, कला, संगीत, दानधर्म, शिकवणे आणि आध्यात्मिक कार्य त्यांना अनेकदा जुळते. त्यांची वाढ निरोगी सीमांमध्ये आहे — स्वतःला न गमावता इतरांची काळजी घेणे, आणि आपल्या समृद्ध कल्पनाशक्तीचे व्यावहारिक कृतीत रूपांतर करणे.",
}

# app/nakshatra_text.py FACTS["mr"] — deity.<slug> and symbol.<slug> of each nakshatra  [54]
NAKSHATRA_FACTS = {
    # EN: The Ashwini Kumaras, the divine physicians
    "deity.ashwini": "अश्विनीकुमार, दिव्य वैद्य",
    # EN: A horse's head
    "symbol.ashwini": "घोड्याचे डोके",
    # EN: Yama, lord of dharma
    "deity.bharani": "यम, धर्माचा अधिपती",
    # EN: The yoni (womb)
    "symbol.bharani": "योनी (गर्भाशय)",
    # EN: Agni, the fire
    "deity.krittika": "अग्नी",
    # EN: A razor or flame
    "symbol.krittika": "वस्तरा किंवा ज्योत",
    # EN: Brahma (Prajapati)
    "deity.rohini": "ब्रह्मा (प्रजापती)",
    # EN: A chariot or ox-cart
    "symbol.rohini": "रथ किंवा बैलगाडी",
    # EN: Soma, the Moon
    "deity.mrigashira": "सोम, चंद्र",
    # EN: A deer's head
    "symbol.mrigashira": "हरणाचे डोके",
    # EN: Rudra
    "deity.ardra": "रुद्र",
    # EN: A teardrop or diamond
    "symbol.ardra": "अश्रू किंवा हिरा",
    # EN: Aditi, mother of the gods
    "deity.punarvasu": "अदिती, देवांची माता",
    # EN: A bow and quiver
    "symbol.punarvasu": "धनुष्य आणि भाता",
    # EN: Brihaspati, guru of the gods
    "deity.pushya": "बृहस्पती, देवांचा गुरू",
    # EN: A cow's udder or lotus
    "symbol.pushya": "गायीचे कास किंवा कमळ",
    # EN: The Nagas (serpent deities)
    "deity.ashlesha": "नाग (सर्पदेवता)",
    # EN: A coiled serpent
    "symbol.ashlesha": "वेटोळे घातलेला साप",
    # EN: The Pitris (ancestors)
    "deity.magha": "पितर (पूर्वज)",
    # EN: A royal throne
    "symbol.magha": "राजसिंहासन",
    # EN: Bhaga, giver of fortune
    "deity.purva-phalguni": "भग, सौभाग्य देणारा",
    # EN: The front legs of a bed
    "symbol.purva-phalguni": "पलंगाचे पुढचे पाय",
    # EN: Aryaman, lord of friendship
    "deity.uttara-phalguni": "अर्यमा, मैत्रीचा अधिपती",
    # EN: The back legs of a bed
    "symbol.uttara-phalguni": "पलंगाचे मागचे पाय",
    # EN: Savitr, the Sun
    "deity.hasta": "सवितृ, सूर्य",
    # EN: A hand
    "symbol.hasta": "हात",
    # EN: Tvashtr (Vishwakarma), the divine architect
    "deity.chitra": "त्वष्टा (विश्वकर्मा), दिव्य शिल्पकार",
    # EN: A bright jewel
    "symbol.chitra": "तेजस्वी रत्न",
    # EN: Vayu, the wind
    "deity.swati": "वायू, वारा",
    # EN: A young shoot swaying in the wind
    "symbol.swati": "वाऱ्यात डोलणारा कोवळा अंकुर",
    # EN: Indra and Agni (Indragni)
    "deity.vishakha": "इंद्र आणि अग्नी (इंद्राग्नी)",
    # EN: A triumphal arch
    "symbol.vishakha": "विजयतोरण",
    # EN: Mitra, lord of friendship
    "deity.anuradha": "मित्र, मैत्रीचा अधिपती",
    # EN: A lotus
    "symbol.anuradha": "कमळ",
    # EN: Indra, king of the gods
    "deity.jyeshtha": "इंद्र, देवांचा राजा",
    # EN: A circular amulet or earring
    "symbol.jyeshtha": "गोलाकार ताईत किंवा कर्णभूषण",
    # EN: Nirriti
    "deity.mula": "निर्ऋती",
    # EN: A bunch of roots
    "symbol.mula": "मुळांचा गुच्छ",
    # EN: Apas, the waters
    "deity.purva-ashadha": "आपस, जल",
    # EN: A winnowing fan or elephant tusk
    "symbol.purva-ashadha": "सूप किंवा हत्तीचा सुळा",
    # EN: The Vishvedevas (universal gods)
    "deity.uttara-ashadha": "विश्वदेव (विश्वातील देवता)",
    # EN: An elephant tusk
    "symbol.uttara-ashadha": "हत्तीचा सुळा",
    # EN: Vishnu
    "deity.shravana": "विष्णू",
    # EN: An ear, or three footprints
    "symbol.shravana": "कान, किंवा तीन पदचिन्हे",
    # EN: The eight Vasus
    "deity.dhanishta": "अष्टवसू",
    # EN: A drum (mridanga)
    "symbol.dhanishta": "ढोल (मृदंग)",
    # EN: Varuna, lord of the waters
    "deity.shatabhisha": "वरुण, जलाचा अधिपती",
    # EN: An empty circle
    "symbol.shatabhisha": "रिकामे वर्तुळ",
    # EN: Aja Ekapada
    "deity.purva-bhadrapada": "अज एकपाद",
    # EN: Swords, or the front legs of a cot
    "symbol.purva-bhadrapada": "तलवारी, किंवा खाटेचे पुढचे पाय",
    # EN: Ahir Budhnya, serpent of the deep
    "deity.uttara-bhadrapada": "अहिर्बुध्न्य, खोल जलातील सर्प",
    # EN: The back legs of a cot, or twins
    "symbol.uttara-bhadrapada": "खाटेचे मागचे पाय, किंवा जुळे",
    # EN: Pushan, the nourisher and guide
    "deity.revati": "पूषा, पोषणकर्ता आणि मार्गदर्शक",
    # EN: A fish (or a drum)
    "symbol.revati": "मासा (किंवा ढोल)",
}

# app/naam_milan_text.py TEXT["mr"] — page text of /naam-se-kundali-milan  [34]
NAAM_MILAN_TEXT = {
    # EN: Naam se Kundali Milan — Match 36 Gunas by Name, Free | {brand}
    # keep: {brand}
    "title": "नावावरून कुंडली मिलन — नामाक्षरावरून 36 गुण जुळवा, मोफत | {brand}",
    # EN: Kundali milan by name: the first syllable of the boy's and girl's names gives each
    #     nakshatra and rashi, then the full 36-guna Ashtakoot match. Type names in Hindi or English
    #     — free, no sign-up.
    "desc": "नावावरून कुंडली मिलन: वराच्या आणि वधूच्या नावाच्या पहिल्या अक्षरावरून नक्षत्र आणि रास काढून संपूर्ण 36 गुणांचे अष्टकूट जुळवणे. नावे मराठी, हिंदी किंवा इंग्रजीत टाइप करा — मोफत, साइन-अप न करता.",
    # EN: Naam se Kundali Milan
    "crumb": "नावावरून कुंडली मिलन",
    # EN: <h1>Naam se Kundali Milan — Match by Name</h1>
    "h1": "<h1>नावावरून कुंडली मिलन — नावानुसार जुळवणी</h1>",
    # EN: <p class="hi" lang="hi">नाम से कुंडली मिलान</p>
    "sub": "<p class=\"hi\">नावाच्या पहिल्या अक्षरावरून नक्षत्र, रास आणि 36 गुण</p>",
    # EN: <p>When birth times are not known, tradition matches a couple by the <strong>first
    #     syllable of their names</strong>. Type both names in Hindi or English: we show the
    #     syllable used, its nakshatra pada and rashi, and the full 36-guna match.</p>
    "intro": "<p>जन्मवेळ माहीत नसते तेव्हा परंपरेनुसार जोडप्याची जुळवणी त्यांच्या <strong>नावाच्या पहिल्या अक्षरावरून</strong> केली जाते. दोन्ही नावे मराठी, हिंदी किंवा इंग्रजीत टाइप करा: वापरलेले अक्षर, त्याचे नक्षत्र चरण आणि रास, आणि संपूर्ण 36 गुणांची जुळवणी आम्ही दाखवतो.</p>",
    # EN: Open birth-chart Kundali Milan
    "open_milan": "जन्मकुंडलीवरून कुंडली मिलन उघडा",
    # EN: Automatic, from the name
    "auto": "नावावरून आपोआप",
    # EN: Other likely syllables for this name
    "alt_head": "या नावासाठी इतर संभाव्य अक्षरे",
    # EN: All 108 syllables
    "all_head": "सर्व 108 अक्षरे",
    # EN: Boy's name (groom)
    "boy_label": "वराचे नाव",
    # EN: Girl's name (bride)
    "girl_label": "वधूचे नाव",
    # EN: e.g. Ram or राम
    "boy_ph": "उदा. राम",
    # EN: e.g. Sita or सीता
    "girl_ph": "उदा. सीता",
    # EN: Change the first syllable
    "pick": "पहिले अक्षर बदला",
    # EN: Match the gunas
    "button": "गुण जुळवा",
    # EN: This syllable belongs to Abhijit, the 28th nakshatra; in the 27-nakshatra wheel it is
    #     counted in Uttara Ashadha pada 4.
    "via.abhijit": "हे अक्षर अभिजित, म्हणजे 28 व्या नक्षत्राचे आहे; 27 नक्षत्रांच्या चक्रात ते उत्तराषाढा चरण 4 मध्ये गणले जाते.",
    # EN: By the traditional rule, ब is read as व, and श as ष (with the a-vowel) or स.
    "via.alias": "पारंपरिक नियमानुसार ब हा व म्हणून वाचला आहे, आणि श हा ष (अ-स्वरासह) किंवा स म्हणून.",
    # EN: This exact syllable is not in the 108-syllable list, so the nearest syllable with the same
    #     consonant was used — change it below if you prefer.
    "via.nearest": "हे अचूक अक्षर 108 अक्षरांच्या यादीत नाही, म्हणून त्याच व्यंजनाचे सर्वात जवळचे अक्षर वापरले आहे — हवे असल्यास खाली बदला.",
    # EN: An English spelling cannot settle this syllable (e.g. T = त or ट), so the most common
    #     reading was used — pick another below if needed.
    "via.latin": "इंग्रजी स्पेलिंगवरून हे अक्षर निश्चित करता येत नाही (उदा. त की ट), म्हणून सर्वात प्रचलित वाचन घेतले आहे — गरज असल्यास खाली दुसरे निवडा.",
    # EN: You chose this syllable.
    "via.chosen": "हे अक्षर तुम्ही निवडले आहे.",
    # EN: Could not read a first syllable from this name — pick one from the list below.
    "unreadable": "या नावावरून पहिले अक्षर वाचता आले नाही — खालील यादीतून एक निवडा.",
    # EN: pada
    "pada": "चरण",
    # EN: Result
    "result": "निकाल",
    # EN: <tr><th></th><th>First syllable</th><th>Nakshatra</th><th>Rashi</th></tr>
    "res.head": "<tr><th></th><th>पहिले अक्षर</th><th>नक्षत्र</th><th>रास</th></tr>",
    # EN: Boy
    "boy": "वर",
    # EN: Girl
    "girl": "वधू",
    # EN: <tr><th>Koota</th><th>Points</th><th>Why</th></tr>
    "res.th": "<tr><th>कूट</th><th>गुण</th><th>कारण</th></tr>",
    # EN: Total
    "total": "एकूण",
    # EN: <strong>Mangal dosha: not applicable.</strong> Mangal dosha depends on where Mars stood
    #     from the Lagna, Moon and Venus at birth — a name cannot tell you that. Use birth-chart
    #     matching for it.
    "mangal": "<strong>मंगळ दोष: लागू नाही.</strong> मंगळ दोष जन्माच्या वेळी मंगळ लग्न, चंद्र आणि शुक्र यांपासून कुठे होता यावर अवलंबून असतो — नावावरून तो कळत नाही. त्यासाठी जन्मकुंडलीवरून जुळवणी करा.",
    # EN: Match by birth details instead — more accurate, free
    "res.cta": "त्याऐवजी जन्मतपशिलावरून जुळवा — अधिक अचूक, मोफत",
    # EN: <div class="box"><p><strong>Please note:</strong> name-based matching is a traditional
    #     shortcut, used when birth details are not known. It assumes each name was chosen from the
    #     syllable of the person's birth nakshatra — which today is often not the case. Matching
    #     from the date, time and place of birth is far more accurate, and is the only way to check
    #     Mangal dosha.</p></div>
    "caveat": "<div class=\"box\"><p><strong>कृपया लक्षात घ्या:</strong> नावावरून जुळवणी हा परंपरागत शॉर्टकट आहे, जो जन्मतपशील माहीत नसताना वापरला जातो. त्यात असे गृहीत धरले जाते की प्रत्येकाचे नाव त्याच्या जन्मनक्षत्राच्या अक्षरावरून ठेवले होते — जे आज बहुतेकदा खरे नसते. जन्मतारीख, वेळ आणि ठिकाणावरून केलेली जुळवणी अधिक अचूक असते, आणि मंगळ दोष तपासण्याचा तोच एकमेव मार्ग आहे.</p></div>",
    # EN: <tr><th>Rashi</th><th>Name syllables</th></tr>
    "syl.head": "<tr><th>रास</th><th>नामाक्षरे</th></tr>",
    # EN: <h2>How name-based matching works</h2> <p>Each of the 27 nakshatras has four padas, and
    #     each pada has a syllable (namakshar) — 108 in all. The pada whose syllable a name
    #     <strong>begins with</strong> is taken as that person's nakshatra, and its sign as their
    #     Moon sign. The same <strong>Ashtakoot (36 guna)</strong> match used with birth charts —
    #     Varna, Vashya, Tara, Yoni, Graha Maitri, Gana, Bhakoot and Nadi — is then computed from
    #     those two nakshatras, by the very engine behind our Kundali Milan tool.</p> <h3>How the
    #     first syllable is read</h3> <ul> <li>The first consonant of the first akshar and its
    #     vowel: <strong>Priya / प्रिया → पी</strong>, <strong>Kshitij / क्षितिज → की</strong>. Long
    #     and short vowels count the same (इ/ई, उ/ऊ); ऐ counts as ए and औ as ओ.</li> <li>ब is read
    #     as व, and श as ष (with the a-vowel) or स; ऋ as री.</li> <li>Abhijit's syllables
    #     ({abhijit}) are counted in Uttara Ashadha pada 4.</li> <li>Names typed in English are
    #     transliterated; letters such as T, D, N, Th and Dh can stand for two Hindi letters (त/ट,
    #     द/ड), so the result shows which syllable was used and lets you pick another. Hindi
    #     (Devanagari) input is read exactly.</li> </ul> <h3>Name syllables by rashi</h3>
    #     {syllables} <p>For each nakshatra's syllables, deity, gana and nadi see <a
    #     href="{href}">all 27 nakshatras</a>.</p>
    # keep: {abhijit} {href} {syllables}
    "explainer": "<h2>नावावरून जुळवणी कशी चालते</h2> <p>27 नक्षत्रांपैकी प्रत्येकाला चार चरण असतात, आणि प्रत्येक चरणाला एक अक्षर (नामाक्षर) असते — एकूण 108. ज्या चरणाच्या अक्षराने नावाची <strong>सुरुवात</strong> होते तो चरण त्या व्यक्तीचे नक्षत्र म्हणून घेतला जातो, आणि त्याची रास तिची चंद्र रास. जन्मकुंडलीसाठी वापरली जाणारी तीच <strong>अष्टकूट (36 गुण)</strong> जुळवणी — वर्ण, वश्य, तारा, योनी, ग्रहमैत्री, गण, भकूट आणि नाडी — त्या दोन नक्षत्रांवरून काढली जाते, आमच्या कुंडली मिलन साधनामागील त्याच इंजिनद्वारे.</p> <h3>पहिले अक्षर कसे वाचले जाते</h3> <ul> <li>पहिल्या अक्षरातील पहिले व्यंजन आणि त्याचा स्वर: <strong>प्रिया → पी</strong>, <strong>क्षितिज → की</strong>. ह्रस्व आणि दीर्घ स्वर सारखेच मानले जातात (इ/ई, उ/ऊ); ऐ हा ए आणि औ हा ओ मानला जातो.</li> <li>ब हा व म्हणून वाचला जातो, आणि श हा ष (अ-स्वरासह) किंवा स म्हणून; ऋ हा री म्हणून.</li> <li>अभिजितची अक्षरे ({abhijit}) उत्तराषाढा चरण 4 मध्ये गणली जातात.</li> <li>इंग्रजीत टाइप केलेल्या नावांचे लिप्यंतर केले जाते; काही इंग्रजी अक्षरे दोन देवनागरी अक्षरांसाठी येऊ शकतात (उदा. त/ट, द/ड), म्हणून निकालात कोणते अक्षर वापरले ते दाखवले जाते आणि तुम्हाला दुसरे निवडू देते. मराठी/हिंदी (देवनागरी) लेखन जसे आहे तसे वाचले जाते.</li> </ul> <h3>राशीनुसार नामाक्षरे</h3> {syllables} <p>प्रत्येक नक्षत्राची अक्षरे, देवता, गण आणि नाडी पाहण्यासाठी <a href=\"{href}\">सर्व 27 नक्षत्रे</a> पाहा.</p>",
}

# app/naam_milan_text.py ENGINE["mr"] — score-band notes and the convention note of a naam-milan result  [5]
NAAM_MILAN_ENGINE = {
    # EN: Below the traditional minimum of 18 gunas.
    "band_note0": "पारंपरिक किमान 18 गुणांपेक्षा कमी.",
    # EN: In the traditional 18-24 gunas band.
    "band_note1": "पारंपरिक 18-24 गुणांच्या श्रेणीत.",
    # EN: In the traditional 25-32 gunas band.
    "band_note2": "पारंपरिक 25-32 गुणांच्या श्रेणीत.",
    # EN: In the traditional 33-36 gunas band.
    "band_note3": "पारंपरिक 33-36 गुणांच्या श्रेणीत.",
    # EN: The 18/25/33 guna thresholds are a widely used convention, not a measurement. Astrologers
    #     often accept a lower total if the heavily weighted kootas are free of dosha.
    "convention_note": "18/25/33 गुणांच्या मर्यादा हा व्यापक वापरातील संकेत आहे, मोजमाप नाही. जास्त गुण असलेले कूट दोषमुक्त असतील तर ज्योतिषी अनेकदा कमी एकूण गुणही स्वीकारतात.",
}

# ----------------------------------------------------------------------------
# muhurat   /muhurat/<kind>-<year>
# ----------------------------------------------------------------------------

# app/muhurat_text.py TEXT["mr"] — page text of /muhurat/<kind>-<year> (the mundan-only keys are MUHURAT_MUNDAN)  [37]
MUHURAT_TEXT = {
    # EN: Vivah Muhurat
    "kind.vivah": "विवाह मुहूर्त",
    # EN: Griha Pravesh Muhurat
    "kind.griha-pravesh": "गृहप्रवेश मुहूर्त",
    # EN: wedding
    "noun.vivah": "विवाह",
    # EN: house-warming
    "noun.griha-pravesh": "गृहप्रवेश",
    # EN: {name} {year}: Auspicious {noun_title} Dates (New Delhi) | {brand}
    # keep: {brand} {year}
    # may also use: {name} {noun_title} {noun}
    "title": "{name} {year}: शुभ {noun} तारखा (नवी दिल्ली) | {brand}",
    # EN: {name} {year}: auspicious {noun} dates
    # keep: {year}
    # may also use: {name} {noun}
    "h1": "{name} {year}: शुभ {noun} तारखा",
    # EN: {name} {year} for New Delhi — month-by-month auspicious {noun} dates with tithi and
    #     nakshatra. {count} dates; Chaturmas, Kharmas, Adhik Maas, Pitru Paksha and Guru/Shukra
    #     asta explained.
    # keep: {count} {year}
    # may also use: {name} {noun}
    "desc": "{name} {year}, नवी दिल्लीसाठी — तिथी आणि नक्षत्रासह महिन्यानुसार शुभ {noun} तारखा. एकूण {count} तारखा; चातुर्मास, खरमास, अधिक मास, पितृपक्ष आणि गुरू/शुक्र अस्त यांचे स्पष्टीकरण.",
    # EN: <p class="hi" lang="hi">{name_hi} {year}</p>
    # keep: {year}
    # may also use: {name} {noun}
    "sub": "<p class=\"hi\">{name} {year} · शुभ तारखा</p>",
    # EN: {label} · IST
    # keep: {label}
    "place": "{label} · भारतीय वेळ",
    # EN: <p>By the panchang there are <strong>{count}</strong> {name_lower} dates in {year} for New
    #     Delhi, in {months}. Each date passes the classical checks on the sunrise tithi, nakshatra,
    #     weekday, yoga and Bhadra, and falls outside Chaturmas, Kharmas, Adhik Maas, Pitru Paksha
    #     and the combustion (asta) of Jupiter and Venus.</p>
    # keep: {count} {months} {year}
    # may also use: {name_lower} {name} {noun}
    "intro": "<p>पंचांगानुसार नवी दिल्लीसाठी {year} मध्ये {months} मध्ये {name_lower} च्या <strong>{count}</strong> तारखा आहेत. प्रत्येक तारीख सूर्योदयाची तिथी, नक्षत्र, वार, योग आणि भद्रा यांच्या शास्त्रीय तपासण्यांतून पार पडते, आणि चातुर्मास, खरमास, अधिक मास, पितृपक्ष तसेच गुरू व शुक्र यांच्या अस्तकाळाच्या बाहेर येते.</p>",
    # EN: <p><strong>Timings vary by city.</strong> These dates are reckoned from New Delhi's
    #     sunrise; elsewhere a tithi or nakshatra can change on a different day. The exact muhurat
    #     (lagna) for a wedding or griha pravesh should be fixed by your family priest. Check your
    #     own city in the Muhurat Finder.</p>
    "note": "<p><strong>वेळा शहरानुसार बदलतात.</strong> या तारखा नवी दिल्लीच्या सूर्योदयानुसार मोजल्या आहेत; इतरत्र एखादी तिथी किंवा नक्षत्र वेगळ्या दिवशी बदलू शकते. विवाह किंवा गृहप्रवेशाचा नेमका मुहूर्त (लग्न) तुमच्या कुलपुरोहितांनी ठरवावा. तुमच्या शहरासाठी मुहूर्त शोधकात पाहा.</p>",
    # EN: Find muhurat for your city — free
    "cta": "तुमच्या शहरासाठी मुहूर्त शोधा — मोफत",
    # EN: {name} {year}
    # keep: {name} {year}
    "crumb": "{name} {year}",
    # EN: More muhurat dates
    "more": "आणखी मुहूर्त तारखा",
    # EN: {name} {year}
    # keep: {name} {year}
    "link.kind": "{name} {year}",
    # EN: Today's Panchang
    "link.panchang": "आजचे पंचांग",
    # EN: Kundali Milan
    "link.milan": "कुंडली मिलन",
    # EN: When there is no {name_lower} in {year}
    # keep: {year}
    # may also use: {name_lower} {name} {noun}
    "periods.h2": "{year} मध्ये {name_lower} कधी नसतो",
    # EN: No {name_lower} is given during these periods. The dates are computed from the panchang
    #     (New Delhi, sunrise):
    # may also use: {name_lower} {name} {noun}
    "periods.intro": "या कालखंडांत {name_lower} दिला जात नाही. तारखा पंचांगावरून (नवी दिल्ली, सूर्योदय) काढल्या आहेत:",
    # EN: <li><strong>{period}</strong>, {range} — {about}.</li>
    # keep: {about} {period} {range}
    "periods.item": "<li><strong>{period}</strong>, {range} — {about}.</li>",
    # EN: No {name_lower} in {month} — {periods}.
    # keep: {month} {periods}
    # may also use: {name_lower} {name} {noun}
    "none.periods": "{month} मध्ये {name_lower} नाही — {periods}.",
    # EN: No {name_lower} in {month} — no day this month passes the tithi, nakshatra, weekday and
    #     yoga checks.
    # keep: {month}
    # may also use: {name_lower} {name} {noun}
    "none.plain": "{month} मध्ये {name_lower} नाही — या महिन्यातील एकही दिवस तिथी, नक्षत्र, वार आणि योगाच्या तपासण्यांत बसत नाही.",
    # EN: <tr><th>Date</th><th>Day</th><th>Tithi</th><th>Nakshatra</th></tr>
    "th": "<tr><th>तारीख</th><th>वार</th><th>तिथी</th><th>नक्षत्र</th></tr>",
    # EN: Muhurat page not found
    "nf.title": "मुहूर्त पान सापडले नाही",
    # EN: Open the Muhurat Finder
    "nf.open": "मुहूर्त शोधक उघडा",
    # EN: Chaturmas
    "period.chaturmas": "चातुर्मास",
    # EN: Devshayani Ekadashi to Devuthani Ekadashi, when Lord Vishnu is in yoga-nidra
    "period_about.chaturmas": "देवशयनी एकादशीपासून देवउठनी एकादशीपर्यंत, जेव्हा भगवान विष्णू योगनिद्रेत असतात",
    # EN: Kharmas
    "period.kharmas": "खरमास",
    # EN: the Sun in Dhanu (Sagittarius) or Meena (Pisces)
    "period_about.kharmas": "सूर्य धनु किंवा मीन राशीत असतो",
    # EN: Adhik Maas
    "period.adhik_maas": "अधिक मास",
    # EN: an intercalary lunar month with no solar ingress
    "period_about.adhik_maas": "सूर्याचे राशी संक्रमण नसलेला अतिरिक्त चांद्र महिना",
    # EN: Pitru Paksha
    "period.pitru_paksha": "पितृपक्ष",
    # EN: Bhadrapada Purnima to Sarva Pitru Amavasya, the fortnight of shraddha
    "period_about.pitru_paksha": "भाद्रपद पौर्णिमेपासून सर्वपित्री अमावस्येपर्यंत, श्राद्धाचा पंधरवडा",
    # EN: Shukra Asta
    "period.shukra_asta": "शुक्र अस्त",
    # EN: Venus combust (too close to the Sun to be seen), with 3 days either side
    "period_about.shukra_asta": "शुक्र सूर्याच्या अगदी जवळ येऊन दिसेनासा होणे (अस्त), दोन्ही बाजूंच्या 3 दिवसांसह",
    # EN: Guru Asta
    "period.guru_asta": "गुरू अस्त",
    # EN: Jupiter combust (too close to the Sun to be seen), with 3 days either side
    "period_about.guru_asta": "गुरू सूर्याच्या अगदी जवळ येऊन दिसेनासा होणे (अस्त), दोन्ही बाजूंच्या 3 दिवसांसह",
}

# app/muhurat_text.py MUNDAN["mr"] — the mundan (first haircut) muhurat's own wording  [5]
MUHURAT_MUNDAN = {
    # EN: Mundan Muhurat
    "kind.mundan": "मुंडन मुहूर्त",
    # EN: mundan
    "noun.mundan": "मुंडन (जावळ)",
    # EN: <p><strong>Timings vary by city.</strong> These dates are reckoned from New Delhi's
    #     sunrise; elsewhere a tithi or nakshatra can change on a different day. The exact muhurat
    #     for the mundan (chudakarma) should be fixed by your family priest. Check your own city in
    #     the Muhurat Finder.</p>
    "note.mundan": "<p><strong>वेळा शहरानुसार बदलतात.</strong> या तारखा नवी दिल्लीच्या सूर्योदयानुसार मोजल्या आहेत; इतरत्र एखादी तिथी किंवा नक्षत्र वेगळ्या दिवशी बदलू शकते. मुंडनाचा (चूडाकर्म, जावळ) नेमका मुहूर्त तुमच्या कुलपुरोहितांनी ठरवावा. तुमच्या शहरासाठी मुहूर्त शोधकात पाहा.</p>",
    # EN: {name} {year}: the rules these dates follow
    # keep: {name} {year}
    "rules.h2": "{name} {year}: या तारखा ज्या नियमांनुसार आहेत",
    # EN: <p>Mundan (chudakarma, the first haircut) is judged by its own rules, not a wedding's. A
    #     day is listed only when none of the barred items below applies and it falls in a
    #     favourable nakshatra:</p><ul><li><strong>Barred tithis:</strong>
    #     {tithi_bad}.</li><li><strong>Favoured tithis</strong> (in either paksha): {tithi_good};
    #     the others are neutral.</li><li><strong>Favourable nakshatras</strong> (every date below
    #     falls in one): {nak_good}.</li><li><strong>Barred nakshatras:</strong>
    #     {nak_bad}.</li><li><strong>Barred yoga and karana:</strong> {yoga_bad}, and Bhadra
    #     (Vishti).</li><li><strong>Weekdays:</strong> {vara_good} are favoured; {vara_bad} count
    #     against a day without ruling it out, so a few such dates appear - skip them if your family
    #     avoids those days.</li></ul>
    # keep: {nak_bad} {nak_good} {tithi_bad} {tithi_good} {vara_bad} {vara_good} {yoga_bad}
    "rules.body": "<p>मुंडन (चूडाकर्म, पहिले केस कापणे) विवाहाच्या नव्हे, तर स्वतःच्या नियमांनुसार तपासले जाते. खालील वर्ज्य गोष्टींपैकी काहीही लागू नसेल आणि दिवस शुभ नक्षत्रात असेल तेव्हाच तो यादीत येतो:</p><ul><li><strong>वर्ज्य तिथी:</strong> {tithi_bad}.</li><li><strong>शुभ तिथी</strong> (कोणत्याही पक्षात): {tithi_good}; इतर सामान्य.</li><li><strong>शुभ नक्षत्रे</strong> (खालील प्रत्येक तारीख यापैकी एकात येते): {nak_good}.</li><li><strong>वर्ज्य नक्षत्रे:</strong> {nak_bad}.</li><li><strong>वर्ज्य योग आणि करण:</strong> {yoga_bad}, आणि भद्रा (विष्टी).</li><li><strong>वार:</strong> {vara_good} शुभ मानले जातात; {vara_bad} दिवसाला नाकारत नाहीत पण त्याच्या विरोधात गणले जातात, म्हणून अशा काही तारखा दिसतात — तुमचे कुटुंब ते वार टाळत असेल तर त्या वगळा.</li></ul>",
}

# app/muhurat_text.py MONTHS["mr"] — only if this page must spell the months differently from names_<code>.MONTHS; else leave ()  [12]
# (optional: may stay empty)
MUHURAT_MONTHS = ()   # or 12 month names, January first

# ----------------------------------------------------------------------------
# recurring /purnima-<year> /amavasya-<year> /pradosh-vrat-<year> ... (DIVASTRO-141)
# ----------------------------------------------------------------------------

# app/recurring_text.py TEXT["mr"] — page text of /purnima-<year>, /amavasya-<year>, /pradosh-vrat-<year> ... (the keys it shares with VRAT_TEXT are taken from there)  [60]
RECURRING_TEXT = {
    # EN: Full Moon Dates and Tithi Time
    "what.purnima": "पौर्णिमेच्या तारखा आणि तिथीची वेळ",
    # EN: New Moon Dates and Tithi Time
    "what.amavasya": "अमावस्येच्या तारखा आणि तिथीची वेळ",
    # EN: All Dates and Pradosh Puja Time
    "what.pradosh": "सर्व तारखा आणि प्रदोष पूजेची वेळ",
    # EN: All Dates and Moonrise Time
    "what.sankashti": "सर्व तारखा आणि चंद्रोदयाची वेळ",
    # EN: All Dates and Nishita Puja Time
    "what.masik_shivratri": "सर्व तारखा आणि निशीथ पूजेची वेळ",
    # EN: All Dates and Kala Bhairav Puja
    "what.kalashtami": "सर्व तारखा आणि कालभैरव पूजा",
    # EN: {name} {year}: {what} (New Delhi)
    # keep: {name} {what} {year}
    "title": "{name} {year}: {what} (नवी दिल्ली)",
    # EN: {name} {year}: {what}
    # keep: {name} {what} {year}
    "h1": "{name} {year}: {what}",
    # EN: All {count} {name} dates in {year} with weekday, Hindu month and tithi start and end for
    #     New Delhi. {about}{keytime}{next}
    # keep: {about} {count} {keytime} {name} {next} {year}
    "desc": "{year} मधील {name} च्या सर्व {count} तारखा — वार, हिंदू महिना आणि तिथीची सुरुवात व समाप्ती, नवी दिल्लीसाठी. {about}{keytime}{next}",
    # EN: Full-moon vrat days for Satyanarayan puja, bathing and charity.
    "desc.about.purnima": "सत्यनारायण पूजा, स्नान आणि दानासाठी पौर्णिमेच्या व्रताचे दिवस.",
    # EN: New-moon days for shraddha and tarpan, with Somvati and Shani Amavasya.
    "desc.about.amavasya": "श्राद्ध आणि तर्पणासाठी अमावस्येचे दिवस, सोमवती आणि शनी अमावस्येसह.",
    # EN: Lord Shiva's twilight fast on Trayodashi, with the puja window.
    "desc.about.pradosh": "त्रयोदशीला भगवान शंकराचे संध्याकाळचे व्रत, पूजेच्या वेळेसह.",
    # EN: Lord Ganesha's fast on Krishna Chaturthi, broken after moonrise.
    "desc.about.sankashti": "कृष्ण चतुर्थीला भगवान गणेशाचे व्रत, चंद्रोदयानंतर सोडले जाणारे.",
    # EN: The monthly night of Shiva on Krishna Chaturdashi, with the midnight puja.
    "desc.about.masik_shivratri": "कृष्ण चतुर्दशीला येणारी शिवाची मासिक रात्र, मध्यरात्रीच्या पूजेसह.",
    # EN: Kala Bhairava worship on Krishna Ashtami, every month.
    "desc.about.kalashtami": "दर महिन्याच्या कृष्ण अष्टमीला कालभैरवाची उपासना.",
    # EN: Includes {label}.
    # keep: {label}
    "desc.key": " यात {label} समाविष्ट आहे.",
    # EN: Next: {date}.
    # keep: {date}
    "desc.next": " पुढील: {date}.",
    # EN: The next {name} is on <strong>{when}</strong> ({details}).
    # keep: {details} {name} {when}
    "ans.next": "पुढील {name} <strong>{when}</strong> रोजी आहे ({details}).",
    # EN: The first {name} of {year} is on <strong>{when}</strong> ({details}). All {count} dates
    #     for {year} are listed below.
    # keep: {count} {details} {name} {when} {year}
    "ans.first": "{year} मधील पहिले {name} <strong>{when}</strong> रोजी आहे ({details}). {year} च्या सर्व {count} तारखा खाली दिल्या आहेत.",
    # EN: All {count} {name} dates for {year} are listed below; the last was on
    #     <strong>{when}</strong>.
    # keep: {count} {name} {when} {year}
    "ans.past": "{year} च्या {name} च्या सर्व {count} तारखा खाली दिल्या आहेत; शेवटची <strong>{when}</strong> रोजी होती.",
    # EN: Dates for {year}: {link}.
    # keep: {link} {year}
    "ans.more": "{year} च्या तारखा: {link}.",
    # EN: {name} {year}: all dates
    # keep: {name} {year}
    "table.h2": "{name} {year}: सर्व तारखा",
    # EN: Date
    "th.date": "तारीख",
    # EN: Hindu month
    "th.month": "हिंदू महिना",
    # EN: Tithi
    "th.tithi": "तिथी",
    # EN: Adhik {month}
    # keep: {month}
    "adhika": "अधिक {month}",
    # EN: Also:
    "also": "तसेच: ",
    # EN: <p class="note"><small>Months are amanta (a month ends on Amavasya, as in South and West
    #     India). North Indian purnimanta calendars name the dark fortnight one month
    #     later.</small></p>
    "months.note": "<p class=\"note\"><small>महिने अमांत आहेत (महिना अमावस्येला संपतो, जसा दक्षिण आणि पश्चिम भारतात). उत्तर भारतीय पौर्णिमांत पंचांगांत कृष्ण पक्षाला एक महिना पुढचे नाव दिले जाते.</small></p>",
    # EN: Som Pradosh
    "variant.pradosh.0": "सोम प्रदोष",
    # EN: Bhauma Pradosh
    "variant.pradosh.1": "भौम प्रदोष",
    # EN: Shani Pradosh
    "variant.pradosh.5": "शनी प्रदोष",
    # EN: Angarki Chaturthi
    "variant.sankashti.1": "अंगारकी चतुर्थी",
    # EN: Somvati Amavasya
    "variant.amavasya.0": "सोमवती अमावस्या",
    # EN: Shani Amavasya
    "variant.amavasya.5": "शनी अमावस्या",
    # EN: What {name} is and how it is observed
    # keep: {name}
    "about.h2": "{name} म्हणजे काय आणि ते कसे पाळले जाते",
    # EN: Panchang for your city
    "city.h2": "तुमच्या शहराचे पंचांग",
    # EN: Related dates and calendars
    "related.h2": "संबंधित तारखा आणि दिनदर्शिका",
    # EN: {name} {year}
    # keep: {name} {year}
    "crumb.page": "{name} {year}",
    # EN: <p>Purnima is the full-moon tithi, the last (15th) tithi of the bright fortnight (Shukla
    #     paksha), when the Moon stands opposite the Sun and shines full. Devotees keep a fast,
    #     bathe at dawn (in a river or tirtha where they can), worship Lord Vishnu - Satyanarayan
    #     Katha is the usual Purnima puja - and offer arghya to the Moon in the evening. Charity
    #     (daan) of food, clothes or money on this day is said to bring multiplied merit.</p><p>Some
    #     Purnimas are festivals in their own right: Guru Purnima, Sharad Purnima, Kartik Purnima
    #     and Buddha Purnima, and Holika Dahan is kept on the Purnima of Phalguna.</p>
    "about.purnima": "<p>पौर्णिमा ही चंद्राची पूर्ण तिथी आहे, शुक्ल पक्षाची शेवटची (15 वी) तिथी, जेव्हा चंद्र सूर्याच्या समोर असतो आणि पूर्ण तेजाने चमकतो. भाविक उपवास करतात, पहाटे स्नान करतात (शक्य तिथे नदीत किंवा तीर्थात), भगवान विष्णूंची पूजा करतात — सत्यनारायण कथा ही पौर्णिमेची नेहमीची पूजा आहे — आणि संध्याकाळी चंद्राला अर्घ्य देतात. या दिवशी अन्न, वस्त्र किंवा पैशांचे दान केल्याने अनेकपट पुण्य मिळते असे सांगितले जाते.</p><p>काही पौर्णिमा स्वतःच सण आहेत: गुरुपौर्णिमा, शरद पौर्णिमा, कार्तिक पौर्णिमा आणि बुद्ध पौर्णिमा, आणि होलिका दहन फाल्गुनाच्या पौर्णिमेला होते.</p>",
    # EN: <p>Amavasya is the new-moon tithi, the 30th and last tithi of the dark fortnight (Krishna
    #     paksha), when the Moon is in conjunction with the Sun and cannot be seen. It is the day of
    #     the ancestors (pitru): families offer tarpan and shraddha, feed Brahmins and the poor,
    #     give in charity and bathe in holy water. Many people fast and avoid starting anything
    #     new.</p><p>An Amavasya on a Monday is called Somvati Amavasya and one on a Saturday Shani
    #     Amavasya, both given extra weight. The great Amavasyas are Mauni Amavasya, Sarva Pitru
    #     Amavasya (the end of Pitru Paksha) and the Amavasya of Diwali.</p>
    "about.amavasya": "<p>अमावस्या ही नवचंद्राची तिथी आहे, कृष्ण पक्षाची 30 वी आणि शेवटची तिथी, जेव्हा चंद्र सूर्यासोबत युतीत असतो आणि दिसत नाही. हा पितरांचा (पितृ) दिवस आहे: कुटुंबे तर्पण आणि श्राद्ध करतात, ब्राह्मणांना आणि गरिबांना जेवू घालतात, दान देतात आणि पवित्र पाण्यात स्नान करतात. अनेकजण उपवास करतात आणि काहीही नवीन सुरू करणे टाळतात.</p><p>सोमवारी येणाऱ्या अमावस्येला सोमवती अमावस्या आणि शनिवारी येणाऱ्या अमावस्येला शनी अमावस्या म्हणतात; दोन्हींना अधिक महत्त्व दिले जाते. मोठ्या अमावस्या म्हणजे मौनी अमावस्या, सर्वपित्री अमावस्या (पितृपक्षाची सांगता) आणि दिवाळीची अमावस्या.</p>",
    # EN: <p>Pradosh Vrat is the fast of Lord Shiva kept on Trayodashi, the 13th tithi, of both
    #     fortnights - so twice a month. Pradosh kaal is the twilight window just after sunset, when
    #     Shiva is believed to be most pleased. Devotees fast through the day, bathe, and do Shiva
    #     puja in the Pradosh window: abhishek with water, milk and bilva (bel) leaves, a lamp and
    #     the Pradosh stotra or Shiva Chalisa. The fast is broken after the puja.</p><p>A Pradosh on
    #     Monday is Som Pradosh, on Tuesday Bhauma Pradosh and on Saturday Shani Pradosh; the
    #     Saturday one is considered especially powerful.</p>
    "about.pradosh": "<p>प्रदोष व्रत हे भगवान शंकराचे व्रत आहे, जे दोन्ही पक्षांच्या त्रयोदशीला, म्हणजे 13 व्या तिथीला केले जाते — म्हणजे महिन्यातून दोनदा. प्रदोषकाळ म्हणजे सूर्यास्तानंतरचा लगेचचा संध्याकाळचा कालावधी, ज्यात शिव सर्वाधिक प्रसन्न असतात असे मानले जाते. भाविक दिवसभर उपवास करतात, स्नान करतात आणि प्रदोषकाळात शिवपूजा करतात: पाणी, दूध आणि बेलपत्रांचा अभिषेक, दीप, आणि प्रदोष स्तोत्र किंवा शिव चालीसा. पूजेनंतर उपवास सोडला जातो.</p><p>सोमवारचा प्रदोष सोम प्रदोष, मंगळवारचा भौम प्रदोष आणि शनिवारचा शनी प्रदोष; शनिवारचा विशेष प्रभावी मानला जातो.</p>",
    # EN: <p>Sankashti Chaturthi (Sankat Hara Chaturthi) is the monthly fast of Lord Ganesha on
    #     Chaturthi, the 4th tithi, of the dark fortnight (Krishna paksha); "sankashti" means
    #     deliverance from trouble. Devotees fast through the day, worship Ganesha in the evening
    #     and break the fast only after seeing the Moon and offering it arghya, which is why
    #     moonrise is the key time on this page.</p><p>A Sankashti on a Tuesday is Angarki Sankashti
    #     Chaturthi, believed to be especially fruitful. The Sankashti of Magha (purnimanta) is kept
    #     in North India as Sakat Chauth.</p>
    "about.sankashti": "<p>संकष्टी चतुर्थी (संकटहर चतुर्थी) हे भगवान गणेशाचे मासिक व्रत आहे, जे कृष्ण पक्षाच्या चतुर्थीला, म्हणजे 4 थ्या तिथीला केले जाते; “संकष्टी” म्हणजे संकटांतून मुक्ती. भाविक दिवसभर उपवास करतात, संध्याकाळी गणेशाची पूजा करतात आणि चंद्र पाहून त्याला अर्घ्य दिल्यानंतरच उपवास सोडतात, म्हणूनच या पानावर चंद्रोदय ही मुख्य वेळ आहे.</p><p>मंगळवारी येणारी संकष्टी अंगारकी संकष्टी चतुर्थी, जी विशेष फलदायी मानली जाते. माघ (पौर्णिमांत) महिन्याची संकष्टी उत्तर भारतात सकट चौथ म्हणून पाळली जाते.</p>",
    # EN: <p>Masik Shivratri (monthly Shivratri) is the night of Lord Shiva kept on Chaturdashi, the
    #     14th tithi, of the dark fortnight (Krishna paksha) every month. Devotees fast and keep
    #     vigil through the night, bathing the Shiva linga with water, milk, honey and bilva leaves
    #     and chanting "Om Namah Shivaya". The best time for the puja is Nishita kaal, the midnight
    #     window.</p><p>Maha Shivratri, which falls on Krishna Chaturdashi of Phalguna (Magha in the
    #     amanta calendar), is the greatest of the twelve.</p>
    "about.masik_shivratri": "<p>मासिक शिवरात्री ही भगवान शंकराची रात्र आहे, जी दर महिन्याला कृष्ण पक्षाच्या चतुर्दशीला, म्हणजे 14 व्या तिथीला पाळली जाते. भाविक उपवास करतात आणि रात्रभर जागरण करतात, शिवलिंगाला पाणी, दूध, मध आणि बेलपत्रांनी स्नान घालतात आणि “ओम नमः शिवाय”चा जप करतात. पूजेसाठी सर्वोत्तम वेळ निशीथ काळ, म्हणजे मध्यरात्रीचा कालावधी.</p><p>महाशिवरात्री, जी फाल्गुनाच्या कृष्ण चतुर्दशीला येते (अमांत पंचांगात माघ), ही बारा शिवरात्रींपैकी सर्वात मोठी आहे.</p>",
    # EN: <p>Kalashtami (Kala Ashtami) is the monthly day of Lord Kala Bhairava, the fierce form of
    #     Shiva who guards time, kept on Ashtami, the 8th tithi, of the dark fortnight (Krishna
    #     paksha). Devotees fast, worship Bhairava at night with a mustard-oil lamp and offerings
    #     such as black sesame, and feed dogs, which are associated with him.</p><p>The Kalashtami
    #     of Margashirsha in the purnimanta calendar (Kartika in the amanta calendar) is
    #     Kalabhairava Jayanti, his appearance day and the most important of the year.</p>
    "about.kalashtami": "<p>कालाष्टमी (काल अष्टमी) हा काळाचे रक्षण करणाऱ्या शिवाच्या उग्र रूपाचा, भगवान कालभैरवाचा मासिक दिवस आहे, जो कृष्ण पक्षाच्या अष्टमीला, म्हणजे 8 व्या तिथीला पाळला जातो. भाविक उपवास करतात, रात्री मोहरीच्या तेलाचा दीप लावून भैरवाची पूजा करतात, काळ्या तिळासारखे नैवेद्य अर्पण करतात आणि त्याच्याशी जोडलेल्या कुत्र्यांना अन्न देतात.</p><p>पौर्णिमांत पंचांगातील मार्गशीर्षाची कालाष्टमी (अमांत पंचांगात कार्तिक) म्हणजे कालभैरव जयंती, त्याचा प्रकटदिन आणि वर्षातील सर्वात महत्त्वाचा.</p>",
    # EN: Purnima can begin one evening and end the next afternoon, so the day the tithi starts and
    #     the day of the vrat can differ. The rule settles it: the vrat goes to the day on which the
    #     tithi covers Madhyahna (the middle fifth of the daytime); if it covers Madhyahna on both
    #     days, the earlier day is taken. Some traditions use the sunrise tithi for the holy bath
    #     and charity instead; the table gives the start and end of the tithi so you can check.
    "note.purnima": "पौर्णिमा एका संध्याकाळी सुरू होऊन दुसऱ्या दुपारी संपू शकते, म्हणून तिथी सुरू होण्याचा दिवस आणि व्रताचा दिवस वेगळा असू शकतो. नियम हे ठरवतो: ज्या दिवशी तिथी मध्याह्न (दिवसाचा मधला पंचमांश) व्यापते त्या दिवशी व्रत केले जाते; ती दोन्ही दिवशी मध्याह्न व्यापत असेल तर आधीचा दिवस घेतला जातो. काही परंपरा पवित्र स्नान आणि दानासाठी त्याऐवजी सूर्योदयाची तिथी वापरतात; तुम्हाला तपासता यावे म्हणून तक्त्यात तिथीची सुरुवात आणि समाप्ती दिली आहे.",
    # EN: Amavasya is a daytime observance (shraddha and tarpan are done in the day), so the date is
    #     the day on which the Amavasya tithi is running at sunrise. The tithi often starts the
    #     evening before, so the times in the table can begin on the previous date. Festival
    #     Amavasyas follow their own rules - Diwali is fixed by Pradosh, Sarva Pitru Amavasya by
    #     Aparahna - and can fall a day away from the date here.
    "note.amavasya": "अमावस्या हा दिवसाचा विधी आहे (श्राद्ध आणि तर्पण दिवसा केले जातात), म्हणून तारीख म्हणजे सूर्योदयाला अमावस्या तिथी चालू असलेला दिवस. तिथी अनेकदा आदल्या संध्याकाळी सुरू होते, म्हणून तक्त्यातील वेळा आधीच्या तारखेपासून सुरू होऊ शकतात. सणांच्या अमावस्या आपल्या स्वतःच्या नियमांनुसार असतात — दिवाळी प्रदोषाने, सर्वपित्री अमावस्या अपराह्नाने ठरते — आणि येथील तारखेपासून एक दिवस दूर येऊ शकतात.",
    # EN: The date is decided in the evening, not at sunrise: the vrat goes to the day on which
    #     Trayodashi is running in Pradosh kaal after sunset, so a Trayodashi that starts at noon
    #     and ends the next afternoon is kept on the first day. If the tithi touches Pradosh kaal on
    #     two evenings, the earlier evening is taken. The puja window in the table starts at sunset
    #     in New Delhi, so it moves through the year and from city to city.
    "note.pradosh": "तारीख सूर्योदयाला नव्हे, तर संध्याकाळी ठरते: ज्या दिवशी सूर्यास्तानंतरच्या प्रदोषकाळात त्रयोदशी चालू असते त्या दिवशी व्रत केले जाते, म्हणून दुपारी सुरू होऊन दुसऱ्या दुपारी संपणारी त्रयोदशी पहिल्या दिवशी पाळली जाते. तिथी दोन संध्याकाळी प्रदोषकाळाला स्पर्श करत असेल तर आधीची संध्याकाळ घेतली जाते. तक्त्यातील पूजेची वेळ नवी दिल्लीतील सूर्यास्ताला सुरू होते, म्हणून ती वर्षभर आणि शहरानुसार बदलते.",
    # EN: Sankashti is decided by the Moon, not the Sun: the vrat goes to the evening on which
    #     Chaturthi is running at moonrise, since that is when the fast is broken. The date can
    #     therefore differ from the Chaturthi date of a Panchang that goes by sunrise. Moonrise is
    #     roughly 50 minutes later each day and differs by several minutes between cities, so check
    #     it for your own city.
    "note.sankashti": "संकष्टी चंद्रावरून ठरते, सूर्यावरून नाही: ज्या संध्याकाळी चंद्रोदयाला चतुर्थी चालू असते त्या संध्याकाळी व्रत केले जाते, कारण तेव्हाच उपवास सोडला जातो. म्हणून तारीख सूर्योदयावरून चालणाऱ्या पंचांगातील चतुर्थीच्या तारखेपेक्षा वेगळी असू शकते. चंद्रोदय रोज साधारण 50 मिनिटे उशिरा होतो आणि शहरानुसार काही मिनिटांनी वेगळा असतो, म्हणून तुमच्या स्वतःच्या शहरासाठी तो तपासा.",
    # EN: This is a midnight observance, so the date is the day on which Chaturdashi is running at
    #     Nishita kaal (the 8th of the 15 muhurtas of the night, around midnight). Nishita can fall
    #     just after 12 o'clock, in which case the puja is done in the early hours of the next date
    #     and the time shown carries that date. If the tithi touches Nishita on two nights, the
    #     earlier night is taken.
    "note.masik_shivratri": "हा मध्यरात्रीचा विधी आहे, म्हणून तारीख म्हणजे निशीथ काळी (रात्रीच्या 15 मुहूर्तांपैकी 8 वा, मध्यरात्रीच्या सुमारास) चतुर्दशी चालू असलेला दिवस. निशीथ 12 वाजल्यानंतर लगेच येऊ शकतो, अशा वेळी पूजा पुढच्या तारखेच्या पहाटे केली जाते आणि दाखवलेल्या वेळेसोबत ती तारीख असते. तिथी दोन रात्री निशीथाला स्पर्श करत असेल तर आधीची रात्र घेतली जाते.",
    # EN: Kalashtami is a night worship, so the date is the day on which Ashtami is running in
    #     Pradosh kaal (the evening window after sunset); the tithi may begin the previous morning
    #     or end during the night, so check its start and end times in the table. If it touches
    #     Pradosh kaal on two evenings, the earlier evening is taken. Some traditions go by the
    #     midnight tithi instead, which can occasionally differ by a day.
    "note.kalashtami": "कालाष्टमी ही रात्रीची उपासना आहे, म्हणून तारीख म्हणजे प्रदोषकाळी (सूर्यास्तानंतरचा संध्याकाळचा कालावधी) अष्टमी चालू असलेला दिवस; तिथी आदल्या सकाळी सुरू होऊ शकते किंवा रात्री संपू शकते, म्हणून तक्त्यात तिची सुरुवात आणि समाप्तीची वेळ तपासा. ती दोन संध्याकाळी प्रदोषकाळाला स्पर्श करत असेल तर आधीची संध्याकाळ घेतली जाते. काही परंपरा त्याऐवजी मध्यरात्रीची तिथी पाहतात, जी कधीकधी एका दिवसाने वेगळी असू शकते.",
    # EN: What are the {name} dates in {year}?
    # keep: {name} {year}
    "faq.all_q": "{year} मध्ये {name} च्या तारखा कोणत्या?",
    # EN: There are {count} {name} dates in {year} (New Delhi): {dates}.
    # keep: {count} {dates} {name} {year}
    "faq.all_a": "{year} मध्ये (नवी दिल्ली) {name} च्या {count} तारखा आहेत: {dates}.",
    # EN: When is the next {name}?
    # keep: {name}
    "faq.next_q": "पुढील {name} केव्हा आहे?",
    # EN: When is the first {name} of {year}?
    # keep: {name} {year}
    "faq.first_q": "{year} मधील पहिले {name} केव्हा आहे?",
    # EN: {name} is on {when} ({details}).
    # keep: {details} {name} {when}
    "faq.on_a": "{name} {when} रोजी आहे ({details}).",
    # EN: What is the {label} on {name} {short}?
    # keep: {label} {name} {short}
    "faq.key_q": "{name} {short} रोजी {label} काय आहे?",
    # EN: At what time does the {name} tithi start and end on {short}?
    # keep: {name} {short}
    "faq.tithi_q": "{short} रोजी {name} तिथी किती वाजता सुरू होते आणि संपते?",
    # EN: How is the {name} date decided?
    # keep: {name}
    "faq.why_q": "{name} ची तारीख कशी ठरते?",
    # EN: The date follows the rule: {rule}. In {year} this gives {count} dates (New Delhi).
    # keep: {count} {rule} {year}
    "faq.why_a": "तारीख या नियमानुसार ठरते: {rule}. {year} मध्ये यानुसार {count} तारखा येतात (नवी दिल्ली).",
    # EN: Monthly vrat dates
    "hub.h2": "मासिक व्रताच्या तारखा",
}

# ----------------------------------------------------------------------------
# hub       /sitemap
# ----------------------------------------------------------------------------

# app/hub_text.py LABELS["mr"] — section names of the crawlable /sitemap page and the footer link block  [19]
HUB_LABELS = {
    # EN: Site map
    "sitemap": "साइट मॅप",
    # EN: Panchang
    "panchang": "पंचांग",
    # EN: Rashifal (daily horoscope)
    "rashifal": "राशिभविष्य (दैनिक)",
    # EN: Vrat &amp; festivals
    "vrat": "व्रते आणि सण",
    # EN: Shubh muhurat
    "muhurat": "शुभ मुहूर्त",
    # EN: Nakshatra
    "nakshatra": "नक्षत्र",
    # EN: Rashi (zodiac signs)
    "rashi": "रास (राशिचक्र)",
    # EN: Kathas
    "katha": "कथा",
    # EN: Free tools
    "tools": "मोफत साधने",
    # EN: Kundali Milan
    "milan": "कुंडली मिलन",
    # EN: Free Kundali
    "kundali": "मोफत कुंडली",
    # EN: Rahu Kaal
    "rahu": "राहुकाळ",
    # EN: Choghadiya
    "choghadiya": "चौघडिया",
    # EN: Naam se Kundali Milan
    "naam": "नावावरून कुंडली मिलन",
    # EN: Today's Panchang by city
    "cities": "शहरानुसार आजचे पंचांग",
    # EN: Rashifal by sign
    "signs": "राशीनुसार राशिभविष्य",
    # EN: Vrat and festival calendars
    "years": "व्रत आणि सण दिनदर्शिका",
    # EN: Ekadashi
    "ekadashi": "एकादशी",
    # EN: Every section of Divine Astro in one place: daily Panchang for Indian cities, Rashifal,
    #     vrat and festival dates, shubh muhurat, nakshatra and rashi guides, kathas and the free
    #     tools.
    "intro": "Divine Astro चे सर्व विभाग एकाच ठिकाणी: भारतीय शहरांचे दैनिक पंचांग, राशिभविष्य, व्रत आणि सणांच्या तारखा, शुभ मुहूर्त, नक्षत्र व रास मार्गदर्शिका, कथा आणि मोफत साधने.",
}

# ----------------------------------------------------------------------------
# app       AI-narration vocabulary here; names_<code>.py and static/i18n/<code>.json beside it
# ----------------------------------------------------------------------------

# app/astro_terms.py TERMS["mr"] — house / dasha / sign vocabulary for the AI narration and the chart labels  [16]
ASTRO_TERMS = {
    # EN: house
    "house": "भाव",
    # EN: sign
    "sign": "रास",
    # EN: lord
    "lord": "स्वामी",
    # EN: dasha
    "dasha": "दशा",
    # EN: mahadasha
    "mahadasha": "महादशा",
    # EN: antardasha
    "antardasha": "अंतर्दशा",
    # EN: ascendant
    "ascendant": "लग्न",
    # EN: transit
    "transit": "गोचर",
    # EN: retrograde
    "retrograde": "वक्री",
    # EN: exalted
    "exalted": "उच्च",
    # EN: debilitated
    "debilitated": "नीच",
    # EN: own sign
    "own sign": "स्वराशी",
    # EN: Sade Sati
    "Sade Sati": "साडेसाती",
    # EN: Navamsa
    "Navamsa": "नवांश",
    # EN: yoga
    "yoga": "योग",
    # EN: remedy
    "remedy": "उपाय",
}

# app/astro_terms.py MONTH_VARIANTS["mr"] — other spellings of a Gregorian month the AI may write (month number -> spellings)
# (optional: may stay empty)
ASTRO_MONTHS = {2: ("फेब्रूवारी",), 4: ("एप्रील",), 8: ("ऑगष्ट",), 10: ("ऑक्टोंबर",), 11: ("नोव्हेम्बर",)}   # {month number: (other spellings,)}
