"""Nepali (नेपाली, Devanagari) — the data a translator fills (DIVASTRO-143).

This file is the ONLY place the ne text of the shared tables is edited; app/lang_data merges it
into them at import time, as if it were written in app/seo_text.py and friends.

  python -m app.lang_data check ne      what is left, per table (exit 0 = complete)
  python -m app.lang_data skeleton ne --force   regenerate (DISCARDS your edits)

Rules: every key below stays; a value "" means "not translated yet" (English shows, the
checker complains). Keep every {placeholder} the comment lists under `keep:`; the word order
is yours. HTML values keep their tags (write &amp; for &). Astrology names (tithi, nakshatra,
rashi, graha ...) are not here: they are in app/astro/names_ne.py. Digits are ASCII, as in
the other languages. Full instructions: docs/lang-agent-brief.md.

Set READY when a whole page module is complete, and only then — an unfinished module in READY
fails `check` and CI. A module that is not READY renders the English body, noindex.
"""

from __future__ import annotations

# Page modules that are complete for this language (the table groups below):
#   "seo" "rashifal" "vrat" "nakshatra" "muhurat" "recurring" "hub" "app"
READY = frozenset({"seo", "rashifal", "vrat", "nakshatra", "muhurat", "recurring", "hub", "app"})

# Latin-script words the ne text may keep besides the defaults (WhatsApp, UPI, PDF ...).
ALLOW_LATIN = frozenset()

# static/i18n/ne.json keys whose value is deliberately the English word (brand names, "OK").
KEEP_ENGLISH = frozenset()

# Namakshar syllables are Devanagari in the engine; this maps a letter to this script:
# (Unicode block start, {Devanagari letter: this script's letter where the offset is wrong}).
# Already set — `check` verifies all 108 syllables come out in the ne script.
AKSHAR = (0x0900, {})


# ----------------------------------------------------------------------------
# seo       /panchang /rahu-kaal /choghadiya /kundali-milan /free-kundali + shared chrome, cities
# ----------------------------------------------------------------------------

# app/seo_text.py TEXT["ne"] — page text of /panchang /rahu-kaal /choghadiya /kundali-milan /free-kundali  [134]
SEO_TEXT = {
    # EN: Panchang
    "tool.panchang": "पञ्चाङ्ग",
    # EN: Rahu Kaal
    "tool.rahu-kaal": "राहुकाल",
    # EN: Choghadiya
    "tool.choghadiya": "चौघडिया",
    # EN: {vara}, {date} · {place} · IST
    # keep: {date} {place} {vara}
    "when": "{vara}, {date} · {place} · IST",
    # EN: {name} until {time}
    # keep: {name} {time}
    "limb.until": "{name} {time} सम्म",
    # EN: then {name}
    # keep: {name}
    "limb.then": "त्यसपछि {name}",
    # EN: pada
    "limb.pada": "पाद",
    # EN: {paksha} paksha
    # keep: {paksha}
    "paksha.full": "{paksha}",
    # EN: {tool} in other cities
    # keep: {tool}
    "cities.heading": "अन्य सहरहरूको {tool}",
    # EN: More free tools
    "links.heading": "थप निःशुल्क सेवाहरू",
    # EN: {tool} in {city}
    # keep: {city} {tool}
    "links.tool_in_city": "{city}को {tool}",
    # EN: Kundali Milan (36 guna)
    "links.milan": "कुण्डली मिलान (36 गुण)",
    # EN: Free Janam Kundali
    "links.kundali": "निःशुल्क जन्मकुण्डली",
    # EN: Muhurat Finder
    "links.muhurat": "मुहूर्त खोज्नुहोस्",
    # EN: Today's Rashifal
    "links.rashifal": "आजको राशिफल",
    # EN: Today's Vrat & Festivals in {city}
    # keep: {city}
    "links.vrat": "{city}मा आजका व्रत र चाडपर्व",
    # EN: City not found — {brand}
    # keep: {brand}
    "nf.title": "सहर भेटिएन — {brand}",
    # EN: {tool} city not found.
    # keep: {tool}
    "nf.desc": "{tool}का लागि यो सहर भेटिएन।",
    # EN: <h1>{tool}: city not found</h1><p>We don't have a page for “{slug}” yet. Pick a city
    #     below, or <a href="{app}">open the {tool} tool</a> to use any place in the world.</p>
    # keep: {app} {slug} {tool}
    "nf.body": "<h1>{tool}: सहर भेटिएन</h1><p>“{slug}” को पृष्ठ हामीसँग अहिले छैन। तल कुनै सहर छान्नुहोस्, वा संसारको कुनै पनि ठाउँका लागि <a href=\"{app}\">{tool} उपकरण खोल्नुहोस्</a>।</p>",
    # EN: Today's Panchang in {city}, {date} — Tithi, Nakshatra, Rahu Kaal | {brand}
    # keep: {brand} {city} {date}
    "p.title": "{city}को आजको पञ्चाङ्ग, {date} — तिथि, नक्षत्र, राहुकाल | {brand}",
    # EN: Aaj ka Panchang for {city} on {vara}, {date}: {tithi} tithi ({paksha} paksha), {nakshatra}
    #     nakshatra, sunrise {sunrise}, Rahu Kaal {rahu}. Computed with Swiss Ephemeris.
    # keep: {city} {date} {nakshatra} {rahu} {sunrise} {tithi} {vara}
    # may also use: {paksha_full} {paksha}
    "p.desc": "{city}को {vara}, {date}को पञ्चाङ्ग: {tithi} तिथि ({paksha}), {nakshatra} नक्षत्र, सूर्योदय {sunrise}, राहुकाल {rahu}। स्विस एफेमेरिसबाट गणना गरिएको।",
    # EN: <h1>Today's Panchang in {city}</h1>
    # keep: {city}
    "p.h1": "<h1>{city}को आजको पञ्चाङ्ग</h1>",
    # EN: <p class="hi" lang="hi">आज का पंचांग — {city_hi}</p>
    # keep: {city}
    "p.sub": "<p class=\"hi\">{city}को तिथि, नक्षत्र, योग, करण र राहुकाल</p>",
    # EN: <div class="box"><p>Today in {city} is <strong>{paksha} {tithi}</strong> with the Moon in
    #     <strong>{nakshatra}</strong> nakshatra. Rahu Kaal runs <strong>{rahu}</strong> — avoid
    #     starting anything new in that window.</p></div>
    # keep: {city} {nakshatra} {rahu} {tithi}
    # may also use: {paksha_full} {paksha}
    "p.box": "<div class=\"box\"><p>आज {city}मा <strong>{paksha} {tithi}</strong> छ र चन्द्रमा <strong>{nakshatra}</strong> नक्षत्रमा छन्। राहुकाल <strong>{rahu}</strong> सम्म रहन्छ — त्यस बेला कुनै नयाँ काम सुरु नगर्नुहोस्।</p></div>",
    # EN: Vaar (weekday)
    "p.r_vara": "वार",
    # EN: Tithi
    "p.r_tithi": "तिथि",
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
    "p.r_moonrise": "चन्द्रोदय",
    # EN: Moonset
    "p.r_moonset": "चन्द्रास्त",
    # EN: Moon sign
    "p.r_moon_sign": "चन्द्र राशि",
    # EN: Rahu Kaal
    "p.r_rahu": "राहुकाल",
    # EN: Yamaganda
    "p.r_yama": "यमघण्ट",
    # EN: Gulika Kaal
    "p.r_gulika": "गुलिक काल",
    # EN: Abhijit Muhurat
    "p.r_abhijit": "अभिजित मुहूर्त",
    # EN: {vara_en} — {weekday} <span lang="hi">({vara_hi})</span>
    # keep: {vara}
    "p.v_vara": "{vara}",
    # EN: {paksha_en} <span lang="hi">({paksha_hi_full})</span>
    # keep: {paksha_full}
    "p.v_paksha": "{paksha_full}",
    # EN: No moonrise this day
    "p.no_moonrise": "यस दिन चन्द्रोदय हुँदैन",
    # EN: No moonset this day
    "p.no_moonset": "यस दिन चन्द्रास्त हुँदैन",
    # EN: Not observed on Wednesday (Budhavara)
    "p.no_abhijit": "बुधबार अभिजित मुहूर्त मानिँदैन",
    # EN: <p>Times are for {place} ({lat}°N, {lon}°E) in Indian Standard Time. The panchang day runs
    #     from sunrise to the next sunrise, so a tithi or nakshatra may end after midnight. Sunrise
    #     is the visible upper limb with refraction, as printed in Indian almanacs; nakshatra and
    #     yoga use the Lahiri ayanamsa.</p>
    # keep: {lat} {lon}
    # may also use: {city} {place}
    "p.note": "<p>समय {place} ({lat}°N, {lon}°E) का लागि भारतीय मानक समयमा दिइएको हो। पञ्चाङ्गको दिन सूर्योदयदेखि अर्को सूर्योदयसम्म चल्छ, त्यसैले कुनै तिथि वा नक्षत्र मध्यरातपछि पनि समाप्त हुन सक्छ। सूर्योदय भारतीय पञ्चाङ्गमा छापिने जस्तै, अपवर्तनसहित सूर्यको माथिल्लो किनारा देखिएको क्षण हो; नक्षत्र र योगमा लाहिरी अयनांश प्रयोग गरिएको छ।</p>",
    # EN: Open the full Panchang — any city, any date
    "p.cta": "पूरा पञ्चाङ्ग हेर्नुहोस् — कुनै पनि सहर, कुनै पनि मिति",
    # EN: <h2>The five limbs of the Panchang</h2> <p><strong>Tithi</strong> is the lunar day — each
    #     12° the Moon gains on the Sun. <strong>Nakshatra</strong> is the Moon's lunar mansion, one
    #     of 27. <strong>Yoga</strong> comes from the combined longitudes of Sun and Moon, and
    #     <strong>Karana</strong> is half a tithi. <strong>Vaar</strong> is the weekday, reckoned
    #     from sunrise. Together they are the <span lang="hi">पंचांग</span> (“five limbs”) consulted
    #     before any auspicious work.</p>
    "p.limbs": "<h2>पञ्चाङ्गका पाँच अङ्ग</h2> <p><strong>तिथि</strong> चान्द्र दिन हो — चन्द्रमाले सूर्यभन्दा प्रत्येक 12° अगाडि बढ्दा एक तिथि बन्छ। <strong>नक्षत्र</strong> चन्द्रमाको 27 तारासमूहमध्ये एक हो। <strong>योग</strong> सूर्य र चन्द्रमाको जोडिएको भोगांशबाट बन्छ, र <strong>करण</strong> आधा तिथि हो। <strong>वार</strong> सूर्योदयदेखि गणना गरिने हप्ताको दिन हो। यी पाँचलाई मिलाएर पञ्चाङ्ग (“पाँच अङ्ग”) बन्छ, जसलाई कुनै पनि शुभ काम गर्नुअघि हेरिन्छ।</p>",
    # EN: Rahu Kaal Today in {city} — {rahu}, {date} | {brand}
    # keep: {brand} {city} {rahu}
    # may also use: {date}
    "rk.title": "{city}मा आजको राहुकाल — {rahu}, {date} | {brand}",
    # EN: Rahu Kaal today in {city} ({vara}, {date}) is {rahu}. Also Yamaganda {yama} and Gulika
    #     {gulika}, with this week's timings and what Rahu Kaal means.
    # keep: {city} {date} {gulika} {rahu} {vara} {yama}
    "rk.desc": "{city}मा आजको ({vara}, {date}) राहुकाल {rahu} हो। साथै यमघण्ट {yama} र गुलिक काल {gulika}, यस हप्ताका समय र राहुकालको अर्थसहित।",
    # EN: <h1>Rahu Kaal Today in {city}</h1>
    # keep: {city}
    "rk.h1": "<h1>{city}मा आजको राहुकाल</h1>",
    # EN: <p class="hi" lang="hi">आज का राहु काल — {city_hi}</p>
    # keep: {city}
    "rk.sub": "<p class=\"hi\">राहुकाल, यमघण्ट र गुलिक काल — {city}</p>",
    # EN: Rahu Kaal <span lang="hi">(राहु काल)</span>
    "rk.r_rahu": "राहुकाल",
    # EN: Yamaganda <span lang="hi">(यमगण्ड)</span>
    "rk.r_yama": "यमघण्ट",
    # EN: Gulika Kaal <span lang="hi">(गुलिक काल)</span>
    "rk.r_gulika": "गुलिक काल",
    # EN: Abhijit Muhurat
    "rk.r_abhijit": "अभिजित मुहूर्त",
    # EN: Sunrise / Sunset
    "rk.r_sun": "सूर्योदय / सूर्यास्त",
    # EN: Not observed on Wednesday
    "rk.no_abhijit": "बुधबार मानिँदैन",
    # EN: Check Rahu Kaal for any city or date
    "rk.cta": "कुनै पनि सहर वा मितिको राहुकाल हेर्नुहोस्",
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
    "rk.about": "<h2>राहुकाल भनेको के हो?</h2> <p>राहुकाल प्रत्येक दिन लगभग डेढ घण्टाको अवधि हो, जसलाई परम्परागत रूपमा उत्तरी चन्द्रपात राहुको अधिकारमा मानिन्छ। सूर्योदयदेखि सूर्यास्तसम्मको दिनलाई आठ बराबर भागमा बाँडिन्छ, र त्यसमध्ये एक भाग राहुको हुन्छ। कुन भाग हो भन्ने हप्ताको वारमा भर पर्छ: आइतबार 8औँ, सोमबार 2रो, मङ्गलबार 7औँ, बुधबार 5औँ, बिहीबार 6ठौँ, शुक्रबार 4थो र शनिबार 3रो भाग।</p> <p>यो वास्तविक सूर्योदय र सूर्यास्तअनुसार चल्ने भएकाले राहुकाल हरेक सहरमा फरक हुन्छ र वर्षभरि सर्दै जान्छ — त्यसैले “सोमबार 7:30–9:00” जस्तो स्थिर तालिका अनुमानमात्र हो। चलनअनुसार राहुकालमा नयाँ काम सुरु गर्ने, सम्झौता गर्ने, यात्रा थाल्ने वा ठूलो किनमेल गर्ने काम टारिन्छ; सुरु भइसकेको काम भने जारी राख्न सकिन्छ। यमघण्ट र गुलिक काल दिनका अरू दुई अष्टमांश हुन्, जसलाई यस्तै सावधानीसाथ हेरिन्छ।</p>",
    # EN: <h2>Rahu Kaal in {city} this week</h2>
    # keep: {city}
    "rk.week_h2": "<h2>यस हप्ता {city}को राहुकाल</h2>",
    # EN: Day
    "rk.th_day": "दिन",
    # EN: Rahu Kaal
    "rk.th_rahu": "राहुकाल",
    # EN: Yamaganda
    "rk.th_yama": "यमघण्ट",
    # EN: Gulika
    "rk.th_gulika": "गुलिक",
    # EN: Choghadiya Today in {city}, {date} — Day & Night Timings | {brand}
    # keep: {brand} {city} {date}
    "ch.title": "{city}मा आजको चौघडिया, {date} — दिन र रातको समय | {brand}",
    # EN: Today's choghadiya for {city} ({vara}, {date}): all 16 day and night muhurtas — Amrit,
    #     Shubh, Labh, Char, Rog, Kaal, Udveg — with exact start and end times from sunrise
    #     {sunrise}.
    # keep: {city} {date} {sunrise} {vara}
    "ch.desc": "{city}को आजको ({vara}, {date}) चौघडिया: दिन र रातका सबै 16 मुहूर्त — अमृत, शुभ, लाभ, चर, रोग, काल, उद्वेग — सूर्योदय {sunrise} देखि सुरु हुने ठ्याक्कै समयसहित।",
    # EN: <h1>Choghadiya Today in {city}</h1>
    # keep: {city}
    "ch.h1": "<h1>{city}मा आजको चौघडिया</h1>",
    # EN: <p class="hi" lang="hi">आज का चौघड़िया — {city_hi}</p>
    # keep: {city}
    "ch.sub": "<p class=\"hi\">दिन र रातका शुभ र अशुभ समय — {city}</p>",
    # EN: {name} from {time}
    # keep: {name} {time}
    "ch.first_good": "{name} {time} देखि",
    # EN: none
    "ch.none": "छैन",
    # EN: <div class="box"><p>Sunrise <strong>{sunrise}</strong>, sunset <strong>{sunset}</strong>.
    #     First auspicious daytime choghadiya: <strong>{first_good}</strong>.</p></div>
    # keep: {first_good} {sunrise} {sunset}
    "ch.box": "<div class=\"box\"><p>सूर्योदय <strong>{sunrise}</strong>, सूर्यास्त <strong>{sunset}</strong>। दिनको पहिलो शुभ चौघडिया: <strong>{first_good}</strong>।</p></div>",
    # EN: <h2>Day Choghadiya <span lang="hi">(दिन का चौघड़िया)</span></h2>
    "ch.day_h2": "<h2>दिनको चौघडिया</h2>",
    # EN: <h2>Night Choghadiya <span lang="hi">(रात का चौघड़िया)</span></h2>
    "ch.night_h2": "<h2>रातको चौघडिया</h2>",
    # EN: <tr><th>Time</th><th>Choghadiya</th><th>Nature</th></tr>
    "ch.th": "<tr><th>समय</th><th>चौघडिया</th><th>स्वभाव</th></tr>",
    # EN: <tr><td>{when}</td><td class="{cls}"><strong>{name}</strong> <span lang="hi">({name_hi})</
    #     span><small>{ruler}</small></td><td>{quality}<small>{desc}</small></td></tr>
    # keep: {cls} {desc} {name} {quality} {ruler} {when}
    "ch.row": "<tr><td>{when}</td><td class=\"{cls}\"><strong>{name}</strong><small>स्वामी: {ruler}</small></td><td>{quality}<small>{desc}</small></td></tr>",
    # EN: Open the live Choghadiya clock
    "ch.cta": "लाइभ चौघडिया घडी खोल्नुहोस्",
    # EN: <h2>How choghadiya works</h2> <p>The day from sunrise to sunset, and the night from sunset
    #     to the next sunrise, are each divided into eight equal parts called choghadiya (<span
    #     lang="hi">चौघड़िया</span>, “four ghadis”). Each is ruled by a planet and named for its
    #     nature: <strong>Amrit</strong>, <strong>Shubh</strong> and <strong>Labh</strong> are
    #     auspicious, <strong>Char</strong> is neutral and good for travel, while
    #     <strong>Rog</strong>, <strong>Kaal</strong> and <strong>Udveg</strong> are avoided for new
    #     beginnings. The order starts from the weekday's ruler, so it changes every day — and the
    #     length of each slot follows the real day length in {city}.</p>
    # keep: {city}
    "ch.about": "<h2>चौघडिया कसरी चल्छ</h2> <p>सूर्योदयदेखि सूर्यास्तसम्मको दिन र सूर्यास्तदेखि अर्को सूर्योदयसम्मको रात — दुवैलाई आठ-आठ बराबर भागमा बाँडिन्छ, जसलाई चौघडिया (“चार घडी”) भनिन्छ। प्रत्येक भागको एक ग्रह स्वामी हुन्छ र त्यसको स्वभावअनुसार नाम राखिएको हुन्छ: <strong>अमृत</strong>, <strong>शुभ</strong> र <strong>लाभ</strong> शुभ मानिन्छन्, <strong>चर</strong> सामान्य र यात्राका लागि राम्रो हो, भने <strong>रोग</strong>, <strong>काल</strong> र <strong>उद्वेग</strong> नयाँ काम सुरु गर्न टारिन्छन्। क्रम त्यस दिनको स्वामीबाट सुरु हुन्छ, त्यसैले हरेक दिन फरक हुन्छ — र प्रत्येक भागको अवधि {city}को वास्तविक दिनको लम्बाइअनुसार हुन्छ।</p>",
    # EN: Kundali Milan — Ashtakoot Guna Milan ({total} Gun) Explained | {brand}
    # keep: {brand} {total}
    "km.title": "कुण्डली मिलान — अष्टकूट गुण मिलान ({total} गुण) बुझ्नुहोस् | {brand}",
    # EN: How Kundali Milan works: the 8 kootas of Ashtakoot Guna Milan, {total} points, what score
    #     is good for marriage, and how Mangal Dosha is checked. Free online matching in English and
    #     Hindi.
    # keep: {total}
    "km.desc": "कुण्डली मिलान कसरी हुन्छ: अष्टकूट गुण मिलानका 8 कूट, {total} अङ्क, विवाहका लागि कति गुण राम्रो मानिन्छ, र मङ्गल दोष कसरी हेरिन्छ। अङ्ग्रेजी र हिन्दीमा निःशुल्क अनलाइन मिलान।",
    # EN: Kundali Milan
    "km.crumb": "कुण्डली मिलान",
    # EN: <h1>Kundali Milan: Ashtakoot Guna Milan explained</h1> <p class="hi" lang="hi">कुंडली
    #     मिलान — अष्टकूट गुण मिलान ({total} गुण)</p> <p>Kundali Milan (<span lang="hi">कुंडली
    #     मिलान</span>) is the traditional Vedic way of checking marriage compatibility. The most
    #     widely used method in North India is <strong>Ashtakoot Guna Milan</strong>: eight factors
    #     (<em>kootas</em>) are compared between the bride's and groom's charts and scored out of
    #     <strong>{total} points (gunas)</strong>. Every one of them is read from the
    #     <strong>Moon</strong> — its sign (rashi) and its nakshatra at birth — which is why the
    #     score needs an accurate birth date and place, but barely depends on the birth time.</p>
    # keep: {total}
    "km.intro": "<h1>कुण्डली मिलान: अष्टकूट गुण मिलान बुझ्नुहोस्</h1> <p class=\"hi\">कुण्डली मिलान — अष्टकूट गुण मिलान ({total} गुण)</p> <p>कुण्डली मिलान विवाहको अनुकूलता जाँच्ने परम्परागत वैदिक विधि हो। उत्तर भारतमा सबैभन्दा बढी प्रयोग हुने विधि <strong>अष्टकूट गुण मिलान</strong> हो: वर र वधूको कुण्डलीबाट आठ कुरा (<em>कूट</em>) तुलना गरी <strong>{total} अङ्क (गुण)</strong> मध्ये अङ्क दिइन्छ। यी सबै <strong>चन्द्रमा</strong>बाट हेरिन्छन् — जन्मका बेलाको चन्द्र राशि र नक्षत्रबाट — त्यसैले अङ्कका लागि सही जन्ममिति र जन्मस्थान चाहिन्छ, तर जन्मको समयमा त्यति निर्भर हुँदैन।</p>",
    # EN: Match two kundalis now — free
    "km.cta1": "अहिले दुई कुण्डली मिलाउनुहोस् — निःशुल्क",
    # EN: <p>Don't know the birth times? Try <a href="{href}">Naam se Kundali Milan</a> — the
    #     traditional match by the first letter of each name.</p>
    # keep: {href}
    "km.naam": "<p>जन्मको समय थाहा छैन? <a href=\"{href}\">नामबाट कुण्डली मिलान</a> प्रयोग गरेर हेर्नुहोस् — प्रत्येक नामको पहिलो अक्षरबाट गरिने परम्परागत मिलान।</p>",
    # EN: <h2>The 8 kootas and their points</h2>
    "km.kootas_h2": "<h2>आठ कूट र तिनका अङ्क</h2>",
    # EN: <tr><th>Koota</th><th>Points</th><th>What it measures</th></tr>
    "km.th": "<tr><th>कूट</th><th>अङ्क</th><th>के जाँचिन्छ</th></tr>",
    # EN: <tr><td><strong>{name}</strong> <span
    #     lang="hi">({name_hi})</span></td><td>{pts}</td><td>{text}</td></tr>
    # keep: {name} {pts} {text}
    "km.row": "<tr><td><strong>{name}</strong></td><td>{pts}</td><td>{text}</td></tr>",
    # EN: Total
    "km.total": "जम्मा",
    # EN: <h2>What is a good Guna Milan score?</h2>
    "km.score_h2": "<h2>कति गुण मिलेको राम्रो मानिन्छ?</h2>",
    # EN: <tr><th>Gunas</th><th>Conventional reading</th></tr>
    "km.score_th": "<tr><th>गुण</th><th>परम्परागत अर्थ</th></tr>",
    # EN: Below {n}
    # keep: {n}
    "km.below": "{n} भन्दा कम",
    # EN: <p>18 is the conventional minimum. The total alone is not the whole story: a high score
    #     with an uncancelled Nadi or Bhakoot dosha is read with caution, and a modest score with
    #     strong Graha Maitri and no doshas is often considered workable. These bands are a
    #     convention with a long history, not a measurement — they are guidance, not a verdict on a
    #     relationship.</p>
    "km.score_p": "<p>18 परम्परागत न्यूनतम सीमा हो। जम्मा अङ्कले मात्र पूरा कुरा भन्दैन: उच्च अङ्कसँग नाडी वा भकूट दोष कटिएको छैन भने सावधानीले हेरिन्छ, र कम अङ्क भए पनि ग्रह मैत्री राम्रो छ र कुनै दोष छैन भने मिलान प्रायः चल्नेखालको मानिन्छ। यी सीमा लामो इतिहास भएको चलन हुन्, नापजोख होइनन् — यी मार्गदर्शनमात्र हुन्, कुनै सम्बन्धबारे अन्तिम निर्णय होइनन्।</p>",
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
    "km.or": " वा ",
    # EN: <h2>Mangal Dosha (Manglik)</h2> <p>Mangal Dosha is checked separately from the 36 points.
    #     A chart is Manglik when Mars sits in the {houses} house counted from the
    #     <strong>Lagna</strong> (ascendant), the <strong>Moon</strong> or <strong>Venus</strong>.
    #     Classical texts exempt certain sign placements (for example Mars in its own sign Aries in
    #     the 1st), and Jupiter's aspect on Mars is held to soften it. When <strong>both</strong>
    #     partners are Manglik the dosha is conventionally treated as mutually cancelled — which is
    #     why Manglik matches are made with Manglik partners. Because it depends on the Lagna,
    #     Mangal Dosha does need a reliable birth time.</p>
    # keep: {houses}
    "km.mangal": "<h2>मङ्गल दोष (माङ्गलिक)</h2> <p>मङ्गल दोष 36 अङ्कभन्दा अलग्गै हेरिन्छ। <strong>लग्न</strong>, <strong>चन्द्रमा</strong> वा <strong>शुक्र</strong>बाट गन्दा मङ्गल {houses} भावमा परेको छ भने कुण्डली माङ्गलिक हुन्छ। शास्त्रीय ग्रन्थहरूले केही राशिस्थितिलाई छुट दिन्छन् (जस्तै पहिलो भावमा आफ्नै राशि मेषमा मङ्गल), र मङ्गलमाथि बृहस्पतिको दृष्टिले दोष कम हुन्छ भनिन्छ। <strong>दुवै</strong> जना माङ्गलिक छन् भने दोष परस्पर कटेको मानिन्छ — त्यसैले माङ्गलिकको विवाह माङ्गलिकसँगै गरिन्छ। लग्नमा भर पर्ने भएकाले मङ्गल दोषका लागि भरपर्दो जन्मसमय चाहिन्छ।</p>",
    # EN: <h2>How our matching tool works</h2> <p>Enter both people's date, time and place of birth.
    #     Both charts are cast with the sidereal zodiac (Lahiri ayanamsa) from the Swiss Ephemeris,
    #     and each koota is scored by table lookup from the classical tables, with every
    #     cancellation named. You get the full {total}-point breakdown and both partners' Mangal
    #     Dosha status, in English or <span lang="hi">हिन्दी</span>, free and without signing
    #     up.</p>
    # keep: {total}
    "km.how": "<h2>हाम्रो मिलान उपकरण कसरी चल्छ</h2> <p>दुवै जनाको जन्ममिति, समय र स्थान हाल्नुहोस्। स्विस एफेमेरिसबाट निरयन राशिचक्र (लाहिरी अयनांश) मा दुवै कुण्डली बनाइन्छ, र प्रत्येक कूटको अङ्क शास्त्रीय तालिकाबाट निकालिन्छ, जहाँ लागू भएको हरेक काटलाई नाम दिइन्छ। तपाईंले {total} अङ्कको पूरा विवरण र दुवैको मङ्गल दोषको अवस्था, अङ्ग्रेजी वा हिन्दीमा, निःशुल्क र दर्ता नगरी पाउनुहुन्छ।</p>",
    # EN: Open Kundali Milan
    "km.cta2": "कुण्डली मिलान खोल्नुहोस्",
    # EN: Varna
    "koota.varna": "वर्ण",
    # EN: Vashya
    "koota.vashya": "वश्य",
    # EN: Tara
    "koota.tara": "तारा",
    # EN: Yoni
    "koota.yoni": "योनि",
    # EN: Graha Maitri
    "koota.graha_maitri": "ग्रह मैत्री",
    # EN: Gana
    "koota.gana": "गण",
    # EN: Bhakoot
    "koota.bhakoot": "भकूट",
    # EN: Nadi
    "koota.nadi": "नाडी",
    # EN: Spiritual and working temperament, from the Moon sign's varna. Full point when the groom's
    #     varna is not below the bride's.
    "koota_about.varna": "चन्द्र राशिको वर्णबाट हेरिने आध्यात्मिक र कार्य-स्वभाव। वरको वर्ण वधूको भन्दा तल छैन भने पूरा अङ्क पाइन्छ।",
    # EN: Mutual attraction and influence — which sign “draws” the other.
    "koota_about.vashya": "आपसी आकर्षण र प्रभाव — कुन राशिले अर्कोलाई “आफूतिर तान्छ”।",
    # EN: Health and wellbeing, from the count between the two birth nakshatras; the 3rd, 5th and
    #     7th taras are unfavourable.
    "koota_about.tara": "दुवैको जन्म नक्षत्रबीचको गणनाबाट हेरिने स्वास्थ्य र कल्याण; 3रो, 5औँ र 7औँ तारा प्रतिकूल मानिन्छन्।",
    # EN: Physical and intimate compatibility; each nakshatra has an animal yoni, and sworn-enemy
    #     animals score zero.
    "koota_about.yoni": "शारीरिक र निजी अनुकूलता; प्रत्येक नक्षत्रको एउटा पशु योनि हुन्छ, र जन्मजात शत्रु पशु भए शून्य अङ्क पाइन्छ।",
    # EN: Friendship between the lords of the two Moon signs — the mental wavelength of the couple.
    "koota_about.graha_maitri": "दुवै चन्द्र राशिका स्वामीबीचको मित्रता — दम्पतीको मानसिक तालमेल।",
    # EN: Temperament: Deva (divine), Manushya (human) or Rakshasa (fierce).
    "koota_about.gana": "स्वभाव: देव (दिव्य), मनुष्य (मानव) वा राक्षस (उग्र)।",
    # EN: The relative placement of the two Moon signs. The 2/12, 5/9 and 6/8 positions form Bhakoot
    #     dosha, cancelled when the sign lords are the same or friends.
    "koota_about.bhakoot": "दुवै चन्द्र राशिको आपसी स्थिति। 2/12, 5/9 र 6/8 स्थितिले भकूट दोष बनाउँछ, जुन राशिका स्वामी एउटै वा मित्र भएमा कटिन्छ।",
    # EN: The highest-weighted koota, tied to health and progeny. The same nadi for both is Nadi
    #     dosha, with classical cancellations for the same sign/different nakshatra or same
    #     nakshatra/different pada.
    "koota_about.nadi": "सबैभन्दा बढी अङ्क भएको कूट, जसको सम्बन्ध स्वास्थ्य र सन्तानसँग छ। दुवैको नाडी एउटै भए नाडी दोष हुन्छ; एउटै राशि तर फरक नक्षत्र, वा एउटै नक्षत्र तर फरक पादमा शास्त्रीय काट छ।",
    # EN: Free Kundali Online — Janam Kundali (Birth Chart) in English & Hindi | {brand}
    # keep: {brand}
    "fk.title": "निःशुल्क कुण्डली अनलाइन — जन्मकुण्डली अङ्ग्रेजी र हिन्दीमा | {brand}",
    # EN: Make your free janam kundali online: Lagna chart in North or South Indian style, planet
    #     positions, Moon nakshatra, Vimshottari dasha, Navamsa and other divisional charts,
    #     Manglik, Sade Sati and Kaal Sarp check — in English or Hindi, no sign-in needed.
    "fk.desc": "अनलाइन निःशुल्क जन्मकुण्डली बनाउनुहोस्: उत्तर वा दक्षिण भारतीय शैलीमा लग्न कुण्डली, ग्रहस्थिति, चन्द्र नक्षत्र, विंशोत्तरी दशा, नवांश र अन्य वर्ग कुण्डली, माङ्गलिक, साढेसाती र कालसर्प जाँच — अङ्ग्रेजी वा हिन्दीमा, दर्ता नगरी।",
    # EN: Free Kundali
    "fk.crumb": "निःशुल्क कुण्डली",
    # EN: <h1>Free Janam Kundali online</h1> <p class="hi" lang="hi">मुफ़्त जन्म कुंडली — हिंदी और
    #     अंग्रेज़ी में</p> <p>A <strong>janam kundali</strong> (<span lang="hi">जन्म कुंडली</span>,
    #     birth chart) is a map of the sky at the exact moment and place you were born: which of the
    #     twelve signs was rising on the eastern horizon (your <strong>Lagna</strong>), and where
    #     the Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu and Ketu stood among the signs
    #     and the 27 nakshatras. Vedic astrology reads everything else — personality, the twelve
    #     areas of life, and above all <em>timing</em> through the dasha periods — from this one
    #     chart. Ours is computed to the minute and is free.</p>
    "fk.intro": "<h1>अनलाइन निःशुल्क जन्मकुण्डली</h1> <p class=\"hi\">निःशुल्क जन्मकुण्डली — अङ्ग्रेजी र हिन्दीमा</p> <p><strong>जन्मकुण्डली</strong> तपाईं जन्मेको ठ्याक्कै क्षण र ठाउँको आकाशको नक्सा हो: पूर्वी क्षितिजमा बाह्र राशिमध्ये कुन उदाउँदै थियो (तपाईंको <strong>लग्न</strong>), र सूर्य, चन्द्रमा, मङ्गल, बुध, बृहस्पति, शुक्र, शनि, राहु र केतु राशि तथा 27 नक्षत्रमा कहाँ थिए। वैदिक ज्योतिषले यही एउटा कुण्डलीबाट बाँकी सबै पढ्छ — स्वभाव, जीवनका बाह्र क्षेत्र, र सबैभन्दा बढी दशा-कालको मार्फत <em>समय</em>। हाम्रो गणना मिनेटसम्म सही र निःशुल्क छ।</p>",
    # EN: Make my free kundali now
    "fk.cta1": "अहिले मेरो निःशुल्क कुण्डली बनाउनुहोस्",
    # EN: <p>You need your <strong>date</strong>, <strong>time</strong> and <strong>place</strong>
    #     of birth. No sign-in, no card.</p>
    "fk.need": "<p>तपाईंको <strong>जन्ममिति</strong>, <strong>जन्मसमय</strong> र <strong>जन्मस्थान</strong> चाहिन्छ। दर्ता गर्नुपर्दैन, कार्ड पनि चाहिँदैन।</p>",
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
    "fk.includes": "<h2>तपाईंको निःशुल्क कुण्डलीमा के-के हुन्छ</h2> <ul> <li><strong>लग्न कुण्डली (D1)</strong> उत्तर वा दक्षिण भारतीय शैलीमा — एक ट्यापमा बदल्न सकिन्छ।</li> <li><strong>ग्रहस्थिति</strong>: नौ ग्रह र लग्नको राशि, अंश, भाव, बल र वक्री अवस्था, साथै चन्द्रमाको नक्षत्र र पाद।</li> <li><strong>बाह्र भाव</strong> र प्रत्येकमा रहेका ग्रह।</li> <li><strong>विंशोत्तरी दशा</strong>: तपाईंको चलिरहेको महादशा र अन्तर्दशा मितिसहित, दृश्य समयरेखामा।</li> <li><strong>वर्ग कुण्डली</strong>: {vargas}।</li> <li><strong>अष्टकवर्ग</strong>: भाव अनुसार सर्वाष्टकवर्ग र भिन्नाष्टकवर्गका बिन्दु।</li> <li><strong>जैमिनि</strong> चर कारक (आत्मकारकदेखि दारकारकसम्म) र आरूढ पद, तथा लग्न, चन्द्रमा र सूर्यबाट एकसाथ कुण्डली हेर्ने <strong>सुदर्शन चक्र</strong>।</li> <li><strong>दोष जाँच</strong>: मङ्गल दोष (माङ्गलिक), साढेसाती र कालसर्प।</li> <li>तपाईंको कुण्डली र चलिरहेको दशाअनुसार <strong>रत्न र उपाय</strong>का सुझाव।</li> <li>कुण्डलीको ड्यासबोर्डमा तपाईंको <strong>दैनिक राशिफल</strong> र आजको पञ्चाङ्ग।</li> </ul> <p>सबै गणना <strong>निरयन राशिचक्र र लाहिरी अयनांश</strong>, सम-राशि भाव पद्धतिमा, स्विस एफेमेरिसबाट गरिएको हो। निःशुल्क खाताले कुण्डली सुरक्षित गर्न, अङ्ग्रेजी वा हिन्दीमा PDF डाउनलोड गर्न, र एआई ज्योतिषीलाई सुरुका प्रश्न निःशुल्क सोध्न पनि दिन्छ।</p>",
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
    "fk.read": "<h2>आफ्नो कुण्डली कसरी पढ्ने</h2> <h3>1. लग्नबाट सुरु गर्नुहोस्</h3> <p>पहिलो भाव जन्मका बेला उदाउँदै गरेको राशि हो। उत्तर भारतीय कुण्डलीमा यो माथिको बीचको हीरा आकारको घर हो, र प्रत्येक घरमा लेखिएको अङ्क भाव होइन, <em>राशि</em> हो (1 = मेष … 12 = मीन)। दक्षिण भारतीय कुण्डलीमा राशिहरू स्थिर खानामा रहन्छन् र लग्न चिन्ह लगाइएको हुन्छ। लग्न र त्यसका स्वामीले शरीर, स्वभाव र जीवनको समग्र दिशा बताउँछन्।</p> <h3>2. चन्द्र राशि र नक्षत्र हेर्नुहोस्</h3> <p>भारतीय चलनमा तपाईंको <strong>राशि</strong> भनेको चन्द्रमाको राशि हो, सूर्यको होइन। राशिफल, साढेसाती र कुण्डली मिलानमा यही राशि प्रयोग हुन्छ, र चन्द्रमाको नक्षत्रले विंशोत्तरी दशा कहाँबाट सुरु हुने भन्ने निर्धारण गर्छ।</p> <h3>3. ग्रहलाई भावअनुसार पढ्नुहोस्</h3> <p>प्रत्येक भाव जीवनको एउटा क्षेत्र हो: 1ला स्वयं, 2रो धन र परिवार, 3रो साहस र दाजुभाइ-दिदीबहिनी, 4थो घर र आमा, 5औँ सन्तान र बुद्धि, 6ठौँ स्वास्थ्य र शत्रु, 7औँ विवाह र साझेदारी, 8औँ आयु र अचानक परिवर्तन, 9औँ भाग्य र धर्म, 10औँ कर्म-क्षेत्र, 11औँ लाभ, 12औँ खर्च र मोक्ष। ग्रहले आफू बसेको भाव र आफूले शासन गर्ने भावलाई रङ्ग्याउँछ; उसको बल (उच्च, स्वराशि, नीच) ले उसले कतिको फल दिन सक्छ भन्ने देखाउँछ।</p> <h3>4. चलिरहेको दशा हेर्नुहोस्</h3> <p>दशाले <em>कहिले</em> भन्ने बताउँछ। महादशाका स्वामी र त्यसभित्र अन्तर्दशाका स्वामी ग्रहका भावहरू यस अवधिमा सक्रिय हुन्छन् — त्यसैले मिल्दाजुल्दा कुण्डली भएका दुई जनाका वर्ष धेरै फरक हुन सक्छन्।</p> <h3>5. दोषलाई सन्दर्भसहित बुझ्नुहोस्</h3> <p>दोष पढ्नुपर्ने एउटा ढाँचा हो, अन्तिम निर्णय होइन। मङ्गल दोषका शास्त्रीय काट छन्; साढेसाती साढे सात वर्षको गोचर हो, जो सबैले दुई-तीन पटक भोग्छन्। दोष प्रतिवेदनले भेटिएका काटहरूको नाम दिन्छ।</p>",
    # EN: Create my janam kundali — free
    "fk.cta2": "मेरो जन्मकुण्डली बनाउनुहोस् — निःशुल्क",
    # EN: <h2>Frequently asked questions</h2>
    "fk.faq_h2": "<h2>बारम्बार सोधिने प्रश्नहरू</h2>",
    # EN: Rashi
    "varga.D1": "राशि",
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
    "km.band0": "सिफारिस गरिँदैन",
    # EN: Acceptable
    "km.band1": "स्वीकार्य",
    # EN: Good
    "km.band2": "राम्रो",
    # EN: Excellent
    "km.band3": "उत्कृष्ट",
}

# app/seo_text.py FAQ["ne"] — the seven free-kundali FAQ pairs (plain text)  [7]
SEO_FAQ = (
    # EN q: Is the kundali really free?
    # EN a: Yes. Casting the chart, the dashas, the divisional charts and the dosha check cost
    #       nothing, and you do not need to sign in to see them. Only the AI astrologer's answers
    #       beyond your free questions, and in-depth paid reports such as the Life Book, cost money.
    ("कुण्डली साँच्चै निःशुल्क हो?", "हो। कुण्डली बनाउने, दशा, वर्ग कुण्डली र दोष जाँच गर्नेमा केही पैसा लाग्दैन, र हेर्न दर्ता गर्नुपर्दैन। निःशुल्क प्रश्नपछिका एआई ज्योतिषीका उत्तर र जीवन पुस्तक जस्ता विस्तृत सशुल्क प्रतिवेदनमा मात्र शुल्क लाग्छ।"),
    # EN q: What details do I need?
    # EN a: Your date of birth, time of birth and place of birth. The place sets the latitude,
    #       longitude and time zone, which decide the Lagna (ascendant) and the house positions.
    ("मलाई कस्ता विवरण चाहिन्छ?", "तपाईंको जन्ममिति, जन्मसमय र जन्मस्थान। जन्मस्थानले अक्षांश, देशान्तर र समय क्षेत्र तय गर्छ, जसले लग्न र भावका स्थान निर्धारण गर्छन्।"),
    # EN q: What if I don't know my exact birth time?
    # EN a: The chart is still cast, at 12:00 noon. The Moon sign and nakshatra are usually still
    #       right (unless the Moon changed sign or nakshatra that day), so Moon-based readings, Sade
    #       Sati and Kundali Milan stay useful — but the Lagna, the houses and Mangal Dosha need a
    #       reliable time. A time from a birth certificate or hospital record is best.
    ("जन्मको ठ्याक्कै समय थाहा छैन भने के गर्ने?", "कुण्डली तैपनि दिउँसो 12:00 बजेको मानेर बनाइन्छ। चन्द्र राशि र नक्षत्र प्रायः सही नै हुन्छन् (त्यस दिन चन्द्रमाले राशि वा नक्षत्र नफेरेको भए), त्यसैले चन्द्रमामा आधारित फल, साढेसाती र कुण्डली मिलान उपयोगी रहन्छन् — तर लग्न, भाव र मङ्गल दोषका लागि भरपर्दो समय चाहिन्छ। जन्म प्रमाणपत्र वा अस्पतालको अभिलेखमा भएको समय सबैभन्दा राम्रो हो।"),
    # EN q: Which system do you use — Lahiri, KP, tropical?
    # EN a: Every chart is sidereal (Nirayana) with the Lahiri (Chitrapaksha) ayanamsa, whole-sign
    #       houses and Vimshottari dasha — the convention of most Indian almanacs and astrologers.
    #       Planet positions come from the Swiss Ephemeris.
    ("तपाईंहरूले कुन पद्धति प्रयोग गर्नुहुन्छ — लाहिरी, केपी कि सायन?", "हरेक कुण्डली निरयन (निरयण) पद्धतिमा लाहिरी (चित्रपक्ष) अयनांश, सम-राशि भाव र विंशोत्तरी दशासहित बन्छ — अधिकांश भारतीय पञ्चाङ्ग र ज्योतिषीले मान्ने चलन। ग्रहस्थिति स्विस एफेमेरिसबाट आउँछ।"),
    # EN q: Can I see my kundali in Hindi?
    # EN a: Yes. Switch the app to हिन्दी and the chart, planet and sign names, dashas and readings
    #       all appear in Hindi; the PDF can be downloaded in Hindi too.
    ("के म आफ्नो कुण्डली हिन्दीमा हेर्न सक्छु?", "सक्नुहुन्छ। एपलाई हिन्दीमा बदल्नुहोस्, कुण्डली, ग्रह र राशिका नाम, दशा र फल सबै हिन्दीमा देखिन्छन्; PDF पनि हिन्दीमा डाउनलोड गर्न सकिन्छ।"),
    # EN q: North Indian or South Indian chart?
    # EN a: Both. The same chart can be shown as the North Indian diamond chart (houses fixed, signs
    #       numbered) or the South Indian square chart (signs fixed), with one tap.
    ("उत्तर भारतीय कि दक्षिण भारतीय कुण्डली?", "दुवै। एउटै कुण्डली एक ट्यापमा उत्तर भारतीय हीरा आकारको शैली (भाव स्थिर, राशि अङ्कित) वा दक्षिण भारतीय वर्गाकार शैली (राशि स्थिर) मा देखाउन सकिन्छ।"),
    # EN q: Is this the same as a horoscope?
    # EN a: A janam kundali is the birth chart itself — the fixed map of the sky at your birth. A
    #       daily horoscope or rashifal is a short general forecast for everyone with the same Moon
    #       sign. Your kundali is personal; a rashifal is not.
    ("के यो र होरोस्कोप उही हो?", "जन्मकुण्डली जन्मका बेलाको आकाशको स्थिर नक्सा हो — जन्मपत्री नै हो। दैनिक राशिफल एउटै चन्द्र राशि भएका सबैका लागि छोटो सामान्य भविष्यवाणी हो। कुण्डली व्यक्तिगत हुन्छ; राशिफल हुँदैन।"),
)

# app/i18n.py CHROME["ne"] — chrome shared by every server page: breadcrumb, footer links, disclaimer (HTML: write &amp;)  [10]
CHROME = {
    # EN: Home
    "home": "गृहपृष्ठ",
    # EN: Breadcrumb
    "breadcrumb": "ब्रेडक्रम्ब",
    # EN: Share on WhatsApp
    "share": "WhatsApp मा सेयर गर्नुहोस्",
    # EN: Kathas
    "f_katha": "कथाहरू",
    # EN: Terms &amp; Conditions
    "f_terms": "सेवाका सर्त",
    # EN: Privacy Policy
    "f_privacy": "गोपनीयता नीति",
    # EN: Refund &amp; Cancellation
    "f_refund": "फिर्ता र रद्दीकरण",
    # EN: Contact Us
    "f_contact": "सम्पर्क गर्नुहोस्",
    # EN: Feedback
    "f_feedback": "प्रतिक्रिया",
    # EN: Astrological readings are provided for guidance and entertainment. They are not medical,
    #     legal or financial advice.
    "disclaimer": "ज्योतिषीय फल मार्गदर्शन र मनोरञ्जनका लागि मात्र हो। यो चिकित्सा, कानुनी वा वित्तीय सल्लाह होइन।",
}

# app/stay_strip.py TEXT["ne"] — the 'Stay in touch' strip at the foot of the pages  [8]
STAY_STRIP = {
    # EN: Stay in touch
    "head": "सम्पर्कमा रहनुहोस्",
    # EN: Get today's panchang on your phone every morning
    "push": "हरेक बिहान आफ्नो फोनमा आजको पञ्चाङ्ग पाउनुहोस्",
    # EN: Turning on…
    "busy": "सुरु गर्दै…",
    # EN: Done — you will get it every morning.
    "on": "भयो — तपाईंले हरेक बिहान पाउनुहुनेछ।",
    # EN: Could not turn on alerts. Please try again.
    "err": "सूचना सुरु गर्न सकिएन। कृपया फेरि प्रयास गर्नुहोस्।",
    # EN: Notifications are blocked for this site in your browser settings.
    "denied": "तपाईंको ब्राउजर सेटिङमा यस साइटका लागि सूचना रोकिएको छ।",
    # EN: Join our WhatsApp channel
    "channel": "हाम्रो WhatsApp च्यानलमा जोडिनुहोस्",
    # EN: Share this page on WhatsApp
    "share": "यो पृष्ठ WhatsApp मा सेयर गर्नुहोस्",
}

# app/seo_city_names.py CITIES["ne"] — the 114 cities as that language's newspapers spell them (key = URL slug)  [114]
CITY_NAMES = {
    # EN: New Delhi
    "new-delhi": "नयाँ दिल्ली",
    # EN: Mumbai
    "mumbai": "मुम्बई",
    # EN: Kolkata
    "kolkata": "कोलकाता",
    # EN: Chennai
    "chennai": "चेन्नई",
    # EN: Bengaluru
    "bengaluru": "बेङ्गलुरु",
    # EN: Hyderabad
    "hyderabad": "हैदराबाद",
    # EN: Ahmedabad
    "ahmedabad": "अहमदाबाद",
    # EN: Pune
    "pune": "पुणे",
    # EN: Jaipur
    "jaipur": "जयपुर",
    # EN: Lucknow
    "lucknow": "लखनऊ",
    # EN: Kanpur
    "kanpur": "कानपुर",
    # EN: Nagpur
    "nagpur": "नागपुर",
    # EN: Indore
    "indore": "इन्दौर",
    # EN: Bhopal
    "bhopal": "भोपाल",
    # EN: Patna
    "patna": "पटना",
    # EN: Varanasi
    "varanasi": "वाराणसी",
    # EN: Prayagraj
    "prayagraj": "प्रयागराज",
    # EN: Surat
    "surat": "सुरत",
    # EN: Vadodara
    "vadodara": "वडोदरा",
    # EN: Chandigarh
    "chandigarh": "चण्डीगढ",
    # EN: Amritsar
    "amritsar": "अमृतसर",
    # EN: Dehradun
    "dehradun": "देहरादुन",
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
    "ranchi": "राँची",
    # EN: Kochi
    "kochi": "कोच्चि",
    # EN: Visakhapatnam
    "visakhapatnam": "विशाखापट्टनम",
    # EN: Thane
    "thane": "ठाणे",
    # EN: Navi Mumbai
    "navi-mumbai": "नवी मुम्बई",
    # EN: Nashik
    "nashik": "नासिक",
    # EN: Chhatrapati Sambhajinagar
    "chhatrapati-sambhajinagar": "छत्रपति सम्भाजीनगर",
    # EN: Solapur
    "solapur": "सोलापुर",
    # EN: Kolhapur
    "kolhapur": "कोल्हापुर",
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
    "gandhinagar": "गान्धीनगर",
    # EN: Dwarka
    "dwarka": "द्वारका",
    # EN: Somnath
    "somnath": "सोमनाथ",
    # EN: Jodhpur
    "jodhpur": "जोधपुर",
    # EN: Udaipur
    "udaipur": "उदयपुर",
    # EN: Kota
    "kota": "कोटा",
    # EN: Ajmer
    "ajmer": "अजमेर",
    # EN: Bikaner
    "bikaner": "बिकानेर",
    # EN: Agra
    "agra": "आगरा",
    # EN: Ghaziabad
    "ghaziabad": "गाजियाबाद",
    # EN: Meerut
    "meerut": "मेरठ",
    # EN: Bareilly
    "bareilly": "बरेली",
    # EN: Aligarh
    "aligarh": "अलिगढ",
    # EN: Moradabad
    "moradabad": "मुरादाबाद",
    # EN: Gorakhpur
    "gorakhpur": "गोरखपुर",
    # EN: Saharanpur
    "saharanpur": "सहारनपुर",
    # EN: Ayodhya
    "ayodhya": "अयोध्या",
    # EN: Mathura
    "mathura": "मथुरा",
    # EN: Vrindavan
    "vrindavan": "वृन्दावन",
    # EN: Jhansi
    "jhansi": "झाँसी",
    # EN: Faridabad
    "faridabad": "फरिदाबाद",
    # EN: Kurukshetra
    "kurukshetra": "कुरुक्षेत्र",
    # EN: Ludhiana
    "ludhiana": "लुधियाना",
    # EN: Jalandhar
    "jalandhar": "जालन्धर",
    # EN: Patiala
    "patiala": "पटियाला",
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
    "gwalior": "ग्वालियर",
    # EN: Jabalpur
    "jabalpur": "जबलपुर",
    # EN: Ujjain
    "ujjain": "उज्जैन",
    # EN: Raipur
    "raipur": "रायपुर",
    # EN: Bhilai
    "bhilai": "भिलाई",
    # EN: Gaya
    "gaya": "गया",
    # EN: Bhagalpur
    "bhagalpur": "भागलपुर",
    # EN: Muzaffarpur
    "muzaffarpur": "मुजफ्फरपुर",
    # EN: Jamshedpur
    "jamshedpur": "जमशेदपुर",
    # EN: Dhanbad
    "dhanbad": "धनबाद",
    # EN: Deoghar
    "deoghar": "देवघर",
    # EN: Howrah
    "howrah": "हावडा",
    # EN: Asansol
    "asansol": "आसनसोल",
    # EN: Siliguri
    "siliguri": "सिलिगुडी",
    # EN: Cuttack
    "cuttack": "कटक",
    # EN: Puri
    "puri": "पुरी",
    # EN: Coimbatore
    "coimbatore": "कोयम्बटूर",
    # EN: Madurai
    "madurai": "मदुरै",
    # EN: Tiruchirappalli
    "tiruchirappalli": "तिरुचिरापल्ली",
    # EN: Salem
    "salem": "सेलम",
    # EN: Rameswaram
    "rameswaram": "रामेश्वरम्",
    # EN: Thiruvananthapuram
    "thiruvananthapuram": "तिरुवनन्तपुरम्",
    # EN: Kozhikode
    "kozhikode": "कोझिकोड",
    # EN: Thrissur
    "thrissur": "त्रिशूर",
    # EN: Kollam
    "kollam": "कोल्लम",
    # EN: Kannur
    "kannur": "कन्नुर",
    # EN: Malappuram
    "malappuram": "मलप्पुरम",
    # EN: Mysuru
    "mysuru": "मैसुर",
    # EN: Mangaluru
    "mangaluru": "मङ्गलुरु",
    # EN: Hubballi
    "hubballi": "हुब्बल्ली",
    # EN: Warangal
    "warangal": "वारङ्गल",
    # EN: Vijayawada
    "vijayawada": "विजयवाडा",
    # EN: Tirupati
    "tirupati": "तिरुपति",
    # EN: Guntur
    "guntur": "गुन्टुर",
    # EN: Panaji
    "panaji": "पणजी",
    # EN: Shillong
    "shillong": "शिलाङ",
    # EN: Imphal
    "imphal": "इम्फाल",
    # EN: Agartala
    "agartala": "अगरतला",
    # EN: Gangtok
    "gangtok": "गङ्टोक",
    # EN: Aizawl
    "aizawl": "आइजोल",
    # EN: Kohima
    "kohima": "कोहिमा",
    # EN: Itanagar
    "itanagar": "ईटानगर",
    # EN: Puducherry
    "puducherry": "पुदुचेरी",
}

# app/seo_city_names.py STATES["ne"] — the states and union territories (key = English state name)  [32]
STATE_NAMES = {
    # EN: Andhra Pradesh
    "Andhra Pradesh": "आन्ध्र प्रदेश",
    # EN: Arunachal Pradesh
    "Arunachal Pradesh": "अरुणाचल प्रदेश",
    # EN: Assam
    "Assam": "असम",
    # EN: Bihar
    "Bihar": "बिहार",
    # EN: Chandigarh
    "Chandigarh": "चण्डीगढ",
    # EN: Chhattisgarh
    "Chhattisgarh": "छत्तीसगढ",
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
    "Jammu and Kashmir": "जम्मू तथा कश्मीर",
    # EN: Jharkhand
    "Jharkhand": "झारखण्ड",
    # EN: Karnataka
    "Karnataka": "कर्नाटक",
    # EN: Kerala
    "Kerala": "केरल",
    # EN: Madhya Pradesh
    "Madhya Pradesh": "मध्य प्रदेश",
    # EN: Maharashtra
    "Maharashtra": "महाराष्ट्र",
    # EN: Manipur
    "Manipur": "मणिपुर",
    # EN: Meghalaya
    "Meghalaya": "मेघालय",
    # EN: Mizoram
    "Mizoram": "मिजोरम",
    # EN: Nagaland
    "Nagaland": "नागाल्यान्ड",
    # EN: Odisha
    "Odisha": "ओडिशा",
    # EN: Puducherry
    "Puducherry": "पुदुचेरी",
    # EN: Punjab
    "Punjab": "पञ्जाब",
    # EN: Rajasthan
    "Rajasthan": "राजस्थान",
    # EN: Sikkim
    "Sikkim": "सिक्किम",
    # EN: Tamil Nadu
    "Tamil Nadu": "तमिलनाडु",
    # EN: Telangana
    "Telangana": "तेलङ्गाना",
    # EN: Tripura
    "Tripura": "त्रिपुरा",
    # EN: Uttar Pradesh
    "Uttar Pradesh": "उत्तर प्रदेश",
    # EN: Uttarakhand
    "Uttarakhand": "उत्तराखण्ड",
    # EN: West Bengal
    "West Bengal": "पश्चिम बङ्गाल",
}

# app/astro/choghadiya.py CHOGHADIYA_INFO["ne"] — one-line description of each of the seven choghadiya slots  [7]
CHOGHADIYA_DESC = {
    # EN: Best time for all ceremonies, investments, agreements, and starting important endeavors.
    "Amrit": "सबै संस्कार, लगानी, सम्झौता र महत्त्वपूर्ण काम सुरु गर्न सबैभन्दा राम्रो समय।",
    # EN: Highly auspicious for ceremonies, religious rituals, education, and purchasing property.
    "Shubh": "संस्कार, धार्मिक अनुष्ठान, पढाइ र सम्पत्ति किन्न अत्यन्त शुभ।",
    # EN: Favorable for business, trade, financial transactions, launching products, and interviews.
    "Labh": "व्यापार, कारोबार, आर्थिक लेनदेन, नयाँ उत्पादन सुरु गर्ने र अन्तर्वार्ताका लागि अनुकूल।",
    # EN: Neutral. Excellent for journeys, travel, vehicle purchases, and shifting places.
    "Char": "सामान्य। यात्रा, सवारी साधन किन्ने र ठाउँ सर्नका लागि उत्तम।",
    # EN: Inauspicious. Avoid medical procedures or conflict. Only suitable for competitive sports
    #     or defeating rivals.
    "Rog": "अशुभ। चिकित्सा प्रक्रिया वा द्वन्द्व नगर्नुहोस्। प्रतिस्पर्धात्मक खेल वा शत्रुमाथि विजयका लागि मात्र उपयुक्त।",
    # EN: Inauspicious. Ruled by Saturn; causes delays and setbacks. Avoid new ventures or signing
    #     documents.
    "Kaal": "अशुभ। शनिको अधिकारमा रहने यो समयले ढिलाइ र अवरोध ल्याउँछ। नयाँ काम सुरु नगर्नुहोस् र कागजातमा हस्ताक्षर नगर्नुहोस्।",
    # EN: Inauspicious. Causes restlessness and anxiety. Favorable only for government filings or
    #     official duties.
    "Udveg": "अशुभ। बेचैनी र चिन्ता ल्याउँछ। सरकारी कागजात बुझाउने वा आधिकारिक काममा मात्र अनुकूल।",
}

# ----------------------------------------------------------------------------
# rashifal  /rashifal and /rashifal/<sign>
# ----------------------------------------------------------------------------

# app/rashifal_text.py TEXT["ne"] — page text of /rashifal and /rashifal/<sign>  [63]
RASHIFAL_TEXT = {
    # EN: {house} house
    # keep: {house}
    "house_short": "{house} भाव",
    # EN: (retrograde)
    "rx": " (वक्री)",
    # EN: Moon
    "planet.Moon": "चन्द्रमा",
    # EN: Saturn
    "planet.Saturn": "शनि",
    # EN: Jupiter
    "planet.Jupiter": "बृहस्पति",
    # EN: Rahu
    "planet.Rahu": "राहु",
    # EN: Ketu
    "planet.Ketu": "केतु",
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
    "crumb_root": "राशिफल",
    # EN: hi
    "sub_lang": 'ne',
    # EN: {name} Rashifal Today, {date_short} — {english} Daily Horoscope | {brand}
    # keep: {brand} {local}
    # may also use: {date_short} {date}
    "s.title": "आजको {local} राशिफल, {date_short} — दैनिक राशिफल | {brand}",
    # EN: {name} ({english} Moon sign) rashifal for {weekday}, {date}: the Moon transits your
    #     {house} house — {tone_lower}. Plus Saturn, Jupiter and Rahu–Ketu transits, Sade Sati
    #     status and today's tithi, computed from the sidereal sky.
    # keep: {date} {house} {local} {tone} {weekday}
    "s.desc": "{weekday}, {date} को {local} राशिफल: चन्द्रमा तपाईंको {house} भावमा गोचर गर्दै छ — {tone}। साथै शनि, बृहस्पति र राहु–केतुको गोचर, साढेसातीको स्थिति र आजको तिथि, निरयन आकाशबाट गणना गरिएको।",
    # EN: {name} Rashifal Today — {english} Daily Horoscope
    # keep: {local}
    "s.h1": "आजको {local} राशिफल",
    # EN: आज का {name_hi} राशिफल
    # may also use: {local}
    "s.sub": "आजको {local} राशिफल",
    # EN: the Moon is in your {house} house from {name}.
    # keep: {house}
    "s.summary": "चन्द्रमा तपाईंको राशिबाट {house} भावमा छ।",
    # EN: About {name} rashi — traits, nakshatras and name letters
    # keep: {local}
    "s.about_rashi": "{local} राशिबारे — स्वभाव, नक्षत्र र नामका अक्षर",
    # EN: Today's Moon transit (Chandra gochar)
    "moon.head": "आजको चन्द्र गोचर (चन्द्र गोचर)",
    # EN: The Moon is in {sign} all day — your {house} house.
    # keep: {house} {sign}
    "moon.allday": "चन्द्रमा दिनभर {sign} मा छ — तपाईंको {house} भाव।",
    # EN: <strong>Until {time} IST:</strong> the Moon is in {sign} — your {house} house.
    # keep: {house} {sign} {time}
    "moon.until": "<strong>IST {time} सम्म:</strong> चन्द्रमा {sign} मा छ — तपाईंको {house} भाव।",
    # EN: <strong>From {time} IST:</strong> the Moon enters {sign} — your {house} house.
    # keep: {house} {sign} {time}
    "moon.from": "<strong>IST {time} देखि:</strong> चन्द्रमा {sign} मा प्रवेश गर्छ — तपाईंको {house} भाव।",
    # EN: <p>The Moon changes sign during the day, so the day reads in two parts.</p>
    "moon.two": "<p>चन्द्रमाले दिनमै राशि बदल्ने भएकाले आजको फल दुई भागमा हेरिन्छ।</p>",
    # EN: The longer backdrop: slow transits
    "back.head": "लामो पृष्ठभूमि: मन्द गतिका गोचर",
    # EN: <p>These planets stay in one sign for months or years, so they set the background against
    #     which each day plays out.</p>
    "back.intro": "<p>यी ग्रह महिनौँ वा वर्षौँसम्म एउटै राशिमा रहन्छन्, त्यसैले दैनिक फलको पृष्ठभूमि यिनले बनाउँछन्।</p>",
    # EN: {sign}{rx} · {house} house
    # keep: {house} {rx} {sign}
    "back.where": "{sign}{rx} · {house} भाव",
    # EN: first (rising)
    "phase.1": "पहिलो (आरम्भ)",
    # EN: second (peak)
    "phase.2": "दोस्रो (चरम)",
    # EN: third (setting)
    "phase.3": "तेस्रो (अन्तिम)",
    # EN: <strong>Sade Sati is running</strong> — the {phase} phase. It is a slow, disciplining
    #     period rather than something to fear; steady routine, service and patience make it
    #     lighter.
    # keep: {phase}
    "sade.running": "<strong>साढेसाती चलिरहेको छ</strong> — {phase} चरण। यो डराउनुपर्ने कुरा होइन, अनुशासन सिकाउने ढिलो समय हो; नियमित दिनचर्या, सेवा र धैर्यले यसलाई हल्का बनाउँछ।",
    # EN: <strong>No Sade Sati</strong>, but Saturn's Dhaiya is running (see above).
    "sade.dhaiya": "<strong>साढेसाती छैन</strong>, तर शनिको ढैया चलिरहेको छ (माथि हेर्नुहोस्)।",
    # EN: <strong>No Sade Sati</strong> — Saturn is not in the 12th, 1st or 2nd from your sign.
    "sade.none": "<strong>साढेसाती छैन</strong> — शनि तपाईंको राशिबाट बाह्रौँ, पहिलो वा दोस्रो भावमा छैन।",
    # EN: <h2>Today's Panchang</h2><p>At sunrise in New Delhi it is <strong>{paksha}
    #     {tithi}</strong> tithi with the Moon in <strong>{nakshatra}</strong> nakshatra. Rahu Kaal,
    #     sunrise and the full almanac are on <a href="/panchang">today's Panchang</a>.</p>
    # keep: {nakshatra} {tithi}
    # may also use: {paksha_full} {paksha}
    "panchang": "<h2>आजको पञ्चाङ्ग</h2><p>नयाँ दिल्लीमा सूर्योदयको समयमा <strong>{paksha} {tithi}</strong> तिथि छ र चन्द्रमा <strong>{nakshatra}</strong> नक्षत्रमा छ। राहुकाल, सूर्योदय र पूरा पञ्चाङ्ग <a href=\"/panchang\">आजको पञ्चाङ्ग</a> मा छ।</p>",
    # EN: <p class="note">This rashifal is read from your Moon sign alone — the same for everyone
    #     born with the Moon in that sign. A personal reading uses your full birth chart: the
    #     ascendant, your running dasha and the ashtakavarga strength of each transit. Not sure of
    #     your Moon sign (rashi)? It is the first thing your free kundali shows — it is usually not
    #     your Western sun sign.</p>
    "personal": "<p class=\"note\">यो राशिफल तपाईंको चन्द्र राशिबाट मात्र हेरिएको हो — त्यही राशिमा चन्द्रमा भएका सबैका लागि एउटै हुन्छ। व्यक्तिगत फल हेर्न तपाईंको पूरा जन्मकुण्डली चाहिन्छ: लग्न, चलिरहेको दशा र प्रत्येक गोचरको अष्टकवर्ग बल। आफ्नो चन्द्र राशि (राशि) थाहा छैन? तपाईंको निःशुल्क कुण्डलीले सबैभन्दा पहिले त्यही देखाउँछ — यो प्रायः पश्चिमी सूर्य राशि हुँदैन।</p>",
    # EN: Get your free kundali — then ask a question about your own chart
    "cta": "आफ्नो निःशुल्क कुण्डली बनाउनुहोस् — अनि आफ्नै कुण्डलीबारे प्रश्न सोध्नुहोस्",
    # EN: Today's Rashifal for every sign
    "signs.head": "सबै राशिको आजको राशिफल",
    # EN: More free tools
    "more.head": "अरू निःशुल्क सेवाहरू",
    # EN: <h2>How this is calculated</h2><p>Planet positions are computed for today (IST) with the
    #     Swiss Ephemeris in the sidereal zodiac (Lahiri ayanamsa) — the same positions our kundali
    #     and panchang use. Houses are counted from your Moon sign, as in classical gochar. Which
    #     houses are favourable follows the scheme of Varahamihira's Brihat Samhita (ch. 104) and
    #     Mantreswara's Phaladeepika (ch. 26): the Moon is favourable in the 1st, 3rd, 6th, 7th,
    #     10th and 11th; Saturn, Rahu and Ketu in the 3rd, 6th and 11th; Jupiter in the 2nd, 5th,
    #     7th, 9th and 11th.</p>
    "method": "<h2>यो कसरी गणना गरिन्छ</h2><p>ग्रहका स्थिति आजका लागि (IST) स्विस एफेमेरिसबाट निरयन राशिचक्रमा (लाहिरी अयनांश) गणना गरिन्छन् — हाम्रो कुण्डली र पञ्चाङ्गले प्रयोग गर्ने उही स्थिति। परम्परागत गोचरजस्तै भावहरू तपाईंको चन्द्र राशिबाट गनिन्छन्। कुन भाव शुभ हुन्छ भन्ने कुरा वराहमिहिरको बृहत्संहिता (अध्याय 104) र मन्त्रेश्वरको फलदीपिका (अध्याय 26) को योजनाअनुसार हो: चन्द्रमा 1, 3, 6, 7, 10 र 11 औँ भावमा शुभ; शनि, राहु र केतु 3, 6 र 11 औँ भावमा; बृहस्पति 2, 5, 7, 9 र 11 औँ भावमा।</p>",
    # EN: Aaj Ka Rashifal, {date_short} — Today's Horoscope for All 12 Signs | {brand}
    # keep: {brand}
    # may also use: {date_short} {date}
    "i.title": "आजको राशिफल, {date_short} — सबै 12 राशिको दैनिक राशिफल | {brand}",
    # EN: Today's rashifal for {weekday}, {date}: daily horoscope for all 12 Moon signs from Mesh to
    #     Meen — Moon transit, Saturn, Jupiter and Rahu, and Sade Sati, computed from the sidereal
    #     sky.
    # keep: {date} {weekday}
    "i.desc": "{weekday}, {date} को राशिफल: मेषदेखि मीनसम्म सबै 12 चन्द्र राशिको दैनिक राशिफल — चन्द्र गोचर, शनि, बृहस्पति र राहु, र साढेसाती, निरयन आकाशबाट गणना गरिएको।",
    # EN: Today's Rashifal — Daily Horoscope
    "i.h1": "आजको राशिफल — दैनिक राशिफल",
    # EN: आज का राशिफल — सभी 12 राशियाँ
    "i.sub": "आजको राशिफल — सबै 12 राशि",
    # EN: <p>Rashifal is read from your <strong>Moon sign</strong> (rashi). {moon_text} Saturn is in
    #     {sat_sign}, so Sade Sati is running for {sade_names}.</p>
    # keep: {moon_text} {sade_names} {sat_sign}
    "i.intro": "<p>राशिफल तपाईंको <strong>चन्द्र राशि</strong> (राशि) बाट हेरिन्छ। {moon_text} शनि {sat_sign} मा छ, त्यसैले {sade_names} का लागि साढेसाती चलिरहेको छ।</p>",
    # EN: The Moon is in {now} until {time} IST, then in {next}. The table shows the position for
    #     most of the day.
    # keep: {next} {now} {time}
    "i.moon_two": "चन्द्रमा IST {time} सम्म {now} मा छ, त्यसपछि {next} मा जान्छ। तालिकाले दिनको अधिकांश समयको स्थिति देखाउँछ।",
    # EN: The Moon is in {now} all day.
    # keep: {now}
    "i.moon_one": "चन्द्रमा दिनभर {now} मा छ।",
    # EN: {name} <small>{english}</small>
    # keep: {local}
    "i.name": "{local}",
    # EN: <small>Sade Sati</small>
    "i.sade": "<small>साढेसाती</small>",
    # EN: <tr><th>Sign</th><th>Moon in your</th><th>Today</th></tr>
    "i.head_row": "<tr><th>राशि</th><th>तपाईंको चन्द्रमा</th><th>आज</th></tr>",
    # EN: Sign not found
    "nf.title": "राशि फेला परेन",
    # EN: <h1>Sign not found</h1><p>There is no rashi called “{slug}”. Pick your Moon sign
    #     below.</p>
    # keep: {slug}
    "nf.body": "<h1>राशि फेला परेन</h1><p>“{slug}” नामको कुनै राशि छैन। तल आफ्नो चन्द्र राशि छान्नुहोस्।</p>",
    # EN: 1st
    "house.1": "पहिलो",
    # EN: 2nd
    "house.2": "दोस्रो",
    # EN: 3rd
    "house.3": "तेस्रो",
    # EN: 4th
    "house.4": "चौथो",
    # EN: 5th
    "house.5": "पाँचौँ",
    # EN: 6th
    "house.6": "छैटौँ",
    # EN: 7th
    "house.7": "सातौँ",
    # EN: 8th
    "house.8": "आठौँ",
    # EN: 9th
    "house.9": "नवौँ",
    # EN: 10th
    "house.10": "दसौँ",
    # EN: 11th
    "house.11": "एघारौँ",
    # EN: 12th
    "house.12": "बाह्रौँ",
}

# app/rashifal_text.py MORE_LINKS["ne"] — 'More free tools' links: keep every href, translate the text; the first href is '{twin:en}' (this page in English)  [6]
RASHIFAL_MORE_LINKS = (
    # EN href: {twin:en}
    # EN text: Read in English
    ("{twin:en}", "अङ्ग्रेजीमा पढ्नुहोस्"),
    # EN href: /panchang
    # EN text: Today's Panchang
    ("/panchang", "आजको पञ्चाङ्ग"),
    # EN href: /rahu-kaal
    # EN text: Rahu Kaal today
    ("/rahu-kaal", "आजको राहुकाल"),
    # EN href: /choghadiya
    # EN text: Choghadiya today
    ("/choghadiya", "आजको चौघडिया"),
    # EN href: /kundali-milan
    # EN text: Kundali Milan
    ("/kundali-milan", "कुण्डली मिलान"),
    # EN href: /vrat-tyohar
    # EN text: Today's vrat & festivals
    ("/vrat-tyohar", "आजका व्रत र चाडपर्व"),
)

# app/rashifal_text.py TONE_LABEL["ne"] — the three day tones (keys good / mixed / easy)  [3]
RASHIFAL_TONE_LABEL = {
    # EN: Favourable day
    "good": "शुभ दिन",
    # EN: Mixed day
    "mixed": "मिश्रित दिन",
    # EN: Take it easy
    "easy": "सहज रूपमा चल्नुहोस्",
}

# app/rashifal_text.py MOON_HOUSE["ne"] — Moon transit through houses 1-12 (key = house number)  [12]
RASHIFAL_MOON_HOUSE = {
    # EN: The Moon moves through your own sign today (Janma Chandra). Classical texts read this as a
    #     day of comfort and good spirits — good food, warm company and a clear sense of yourself. A
    #     good day to look after your own needs and begin small, personal things.
    1: "आज चन्द्रमा तपाईंकै राशिमा गोचर गर्दै छ (जन्म चन्द्र)। शास्त्रीय ग्रन्थहरूले यसलाई सुख र उत्साहको दिन मानेका छन् — राम्रो भोजन, न्यानो सङ्गत र आफ्नै बारेमा स्पष्ट बोध। आफ्ना आवश्यकताको ख्याल राख्न र साना व्यक्तिगत कामको सुरुआत गर्न राम्रो दिन।",
    # EN: The Moon is in your 2nd house today. Tradition asks for care with money and words —
    #     expenses can creep up and small misunderstandings arise easily. Keep spending planned and
    #     speak gently at home; routine work goes fine.
    2: "आज चन्द्रमा तपाईंको दोस्रो भावमा छ। परम्पराले पैसा र बोलीमा होसियार रहन भन्छ — खर्च बिस्तारै बढ्न सक्छ र साना गलतफहमी सजिलै हुन्छन्। खर्च योजनाबद्ध राख्नुहोस्, घरमा नरम बोल्नुहोस्; नियमित काम ठीकसँग चल्छ।",
    # EN: The Moon in your 3rd house is a favourable transit. Courage and initiative are high,
    #     effort brings results, and contact with siblings, friends and neighbours goes well. A good
    #     day for short trips, calls and pushing a pending task over the line.
    3: "तेस्रो भावमा चन्द्रमा शुभ गोचर हो। साहस र पहल उच्च हुन्छ, प्रयासले फल दिन्छ, दाजुभाइदिदीबहिनी, साथी र छिमेकीसँगको सम्पर्क राम्रो रहन्छ। छोटो यात्रा, फोन गर्न र बाँकी रहेको काम पूरा गर्न राम्रो दिन।",
    # EN: The Moon in your 4th house can leave the mind a little unsettled — home matters or travel
    #     may feel tiring. Keep the day simple, avoid arguments at home and give yourself some quiet
    #     time; the mood lifts as the Moon moves on.
    4: "चौथो भावमा चन्द्रमाले मनलाई केही अस्थिर बनाउन सक्छ — घरका कुरा वा यात्रा थकाइलाग्दो लाग्न सक्छ। दिन सरल राख्नुहोस्, घरमा झगडा नगर्नुहोस् र आफूलाई केही शान्त समय दिनुहोस्; चन्द्रमा अघि बढेपछि मन हल्का हुन्छ।",
    # EN: The Moon in your 5th house is a mixed transit. Plans may meet small hurdles and the mind
    #     can swing between ideas. Avoid speculative decisions; study, creative work and time with
    #     children are better uses of the day.
    5: "पाँचौँ भावमा चन्द्रमा मिश्रित गोचर हो। योजनामा साना बाधा आउन सक्छन् र मन विचारहरूबीच डुलिरहन सक्छ। सट्टाबाजीजस्ता निर्णय नगर्नुहोस्; अध्ययन, सिर्जनात्मक काम र बच्चाहरूसँगको समय दिनका लागि बढी उपयुक्त हुन्छन्।",
    # EN: The Moon in your 6th house is one of its best transits. Classical texts promise success
    #     over rivals and obstacles, and the energy to clear a backlog. A good day for competitive
    #     work, settling pending issues and steady routines.
    6: "छैटौँ भावमा चन्द्रमा यसको सबैभन्दा राम्रो गोचरमध्ये एक हो। शास्त्रीय ग्रन्थहरूले शत्रु र बाधामाथि विजय र जम्मा भएका काम निमिट्याउने शक्ति बताएका छन्। प्रतिस्पर्धी काम, बाँकी विषय मिलाउन र स्थिर दिनचर्याका लागि राम्रो दिन।",
    # EN: The Moon in your 7th house favours partnership and company. Time with your spouse or
    #     partner, meetings and agreements tend to go smoothly, with comfort and good food. A good
    #     day to reach out and work together.
    7: "सातौँ भावमा चन्द्रमाले साझेदारी र सङ्गतलाई साथ दिन्छ। जीवनसाथी वा साझेदारसँगको समय, भेटघाट र सम्झौता सहज हुन्छन्, सुख र राम्रो भोजन मिल्छ। अरूसँग सम्पर्क गर्न र मिलेर काम गर्न राम्रो दिन।",
    # EN: The Moon is in your 8th house — the period known as Chandrashtama. Tradition advises
    #     against starting important new things today; unexpected delays are more likely and the
    #     mind can feel anxious. Keep a margin in your schedule, stick to familiar work and be
    #     gentle with yourself — it passes within two to three days.
    8: "आज चन्द्रमा तपाईंको आठौँ भावमा छ — यो अवधि चन्द्राष्टम भनिन्छ। परम्पराले आज कुनै महत्त्वपूर्ण नयाँ काम सुरु नगर्न सल्लाह दिन्छ; अप्रत्याशित ढिलाइ हुने सम्भावना बढी हुन्छ र मन चिन्तित हुन सक्छ। तालिकामा केही खाली समय राख्नुहोस्, चिनेजानेकै काममा लाग्नुहोस् र आफूप्रति नरम रहनुहोस् — दुई–तीन दिनमा यो बित्छ।",
    # EN: The Moon in your 9th house is a mixed transit. Plans may need extra effort and you may
    #     feel tired or distracted. Prayer, reading and time with elders or teachers suit the day
    #     better than big new ventures.
    9: "नवौँ भावमा चन्द्रमा मिश्रित गोचर हो। योजनाहरूमा थप मेहनत लाग्न सक्छ र तपाईं थकित वा अन्यमनस्क हुन सक्नुहुन्छ। ठूला नयाँ काम भन्दा पूजा, पठनपाठन र ठूलाबडा वा गुरुहरूसँगको समय दिनका लागि बढी उपयुक्त हुन्छ।",
    # EN: The Moon in your 10th house supports work and reputation. Tasks get done, seniors are
    #     receptive and effort is noticed. A good day to present your work, take a professional step
    #     or finish something visible.
    10: "दसौँ भावमा चन्द्रमाले काम र प्रतिष्ठालाई साथ दिन्छ। काम सम्पन्न हुन्छन्, वरिष्ठहरू ग्रहणशील हुन्छन् र प्रयासको कदर हुन्छ। आफ्नो काम प्रस्तुत गर्न, पेसागत कदम चाल्न वा देखिने कुनै काम सक्न राम्रो दिन।",
    # EN: The Moon in your 11th house — the house of gains — is a very favourable transit. Expect
    #     support from friends, good news and the fruit of earlier effort. A good day for
    #     networking, making requests and celebrating with others.
    11: "लाभको भाव एघारौँमा चन्द्रमा अत्यन्त शुभ गोचर हो। साथीहरूको साथ, शुभ समाचार र अघिल्ला प्रयासको फल मिल्ने आशा गर्नुहोस्। सम्पर्क बढाउन, अनुरोध गर्न र अरूसँग खुसी मनाउन राम्रो दिन।",
    # EN: The Moon in your 12th house can bring extra expenses and a tired, inward mood. Avoid
    #     overspending and late nights; the day suits rest, prayer, charity and finishing old work
    #     rather than starting new.
    12: "बाह्रौँ भावमा चन्द्रमाले थप खर्च र थकित, भित्रतिर फर्केको मनस्थिति ल्याउन सक्छ। धेरै खर्च र राति ढिलोसम्म जाग्नबाट बच्नुहोस्; दिन नयाँ काम सुरु गर्नुभन्दा आराम, पूजा, दान र पुराना काम टुङ्ग्याउन उपयुक्त छ।",
}

# app/rashifal_text.py SATURN_HOUSE["ne"] — Saturn transit through houses 1-12  [12]
RASHIFAL_SATURN_HOUSE = {
    # EN: Saturn is passing over your Moon sign — the peak phase of Sade Sati. It rewards patience,
    #     routine and honest effort; take on a little less and finish what you start.
    1: "शनि तपाईंको चन्द्र राशिमाथि गुज्रिरहेको छ — साढेसातीको चरम चरण। यसले धैर्य, दिनचर्या र इमानदार प्रयासलाई पुरस्कृत गर्छ; अलि कम काम लिनुहोस् र सुरु गरेको काम पूरा गर्नुहोस्।",
    # EN: Saturn is in your 2nd — the last phase of Sade Sati. Be measured with spending and with
    #     words at home; the pressure is easing.
    2: "शनि तपाईंको दोस्रो भावमा छ — साढेसातीको अन्तिम चरण। खर्च र घरमा बोलीमा संयम राख्नुहोस्; दबाब घट्दै छ।",
    # EN: Saturn in your 3rd is one of its best positions — steady effort pays, courage grows and
    #     long-running work gains traction.
    3: "तेस्रो भावमा शनि यसको सबैभन्दा राम्रो स्थितिमध्ये एक हो — स्थिर प्रयासले फल दिन्छ, साहस बढ्छ र लामो समयदेखि चलिरहेको काम अघि बढ्छ।",
    # EN: Saturn in your 4th (Dhaiya, Kantaka Shani) can make home life and peace of mind feel
    #     heavier; keep routines simple and handle family matters calmly.
    4: "चौथो भावमा शनि (ढैया, कण्टक शनि) ले घरजीवन र मनको शान्ति केही भारी लाग्न सक्छ; दिनचर्या सरल राख्नुहोस् र पारिवारिक कुरा शान्तसँग सम्हाल्नुहोस्।",
    # EN: Saturn in your 5th asks for patience with plans, studies and children's matters — slow and
    #     careful beats quick.
    5: "पाँचौँ भावमा शनिले योजना, अध्ययन र सन्तानसम्बन्धी कुरामा धैर्य माग्छ — हतारभन्दा ढिलो र सावधानी राम्रो।",
    # EN: Saturn in your 6th works in your favour — discipline wins over rivals and backlog, and
    #     hard work gets noticed.
    6: "छैटौँ भावमा शनि तपाईंको पक्षमा काम गर्छ — अनुशासनले प्रतिद्वन्द्वी र जम्मा भएका कामलाई जित्छ, र कडा मेहनतको कदर हुन्छ।",
    # EN: Saturn in your 7th puts partnerships in a slow, serious light — clear agreements and
    #     patience help.
    7: "सातौँ भावमा शनिले साझेदारीलाई ढिलो र गम्भीर रूपमा देखाउँछ — स्पष्ट सम्झौता र धैर्यले मद्दत गर्छ।",
    # EN: Saturn in your 8th (Dhaiya, Ashtama Shani) is a time to avoid shortcuts and keep a margin
    #     for delays.
    8: "आठौँ भावमा शनि (ढैया, अष्टम शनि) को समयमा सजिलो बाटो नखोज्नुहोस् र ढिलाइका लागि समय छुट्याएर राख्नुहोस्।",
    # EN: Saturn in your 9th can slow luck and long journeys; respect for elders and steady duty
    #     keep things on track.
    9: "नवौँ भावमा शनिले भाग्य र लामो यात्रा ढिलो बनाउन सक्छ; ठूलाबडाप्रति आदर र स्थिर कर्तव्यपालनले काम ठीक चलाउँछ।",
    # EN: Saturn in your 10th brings responsibility at work — a heavier load, but sincere effort
    #     builds a lasting reputation.
    10: "दसौँ भावमा शनिले कार्यक्षेत्रमा जिम्मेवारी ल्याउँछ — भार बढी हुन्छ, तर इमानदार प्रयासले दीर्घकालीन प्रतिष्ठा बनाउँछ।",
    # EN: Saturn in your 11th is favourable — gains come slowly but surely, and long effort starts
    #     to pay off.
    11: "एघारौँ भावमा शनि शुभ छ — लाभ बिस्तारै तर पक्का रूपमा आउँछ, र लामो प्रयासले फल दिन थाल्छ।",
    # EN: Saturn is in your 12th — the opening phase of Sade Sati. Watch expenses and rest well; a
    #     good time for quiet, inward work.
    12: "शनि तपाईंको बाह्रौँ भावमा छ — साढेसातीको प्रारम्भिक चरण। खर्चमा ध्यान दिनुहोस् र राम्ररी आराम गर्नुहोस्; शान्त, भित्री कामका लागि राम्रो समय।",
}

# app/rashifal_text.py JUPITER_HOUSE["ne"] — Jupiter transit through houses 1-12  [12]
RASHIFAL_JUPITER_HOUSE = {
    # EN: Jupiter over your Moon sign is classically a restless position; keep plans grounded and
    #     avoid over-committing.
    1: "तपाईंको चन्द्र राशिमाथि बृहस्पति शास्त्रअनुसार अस्थिर स्थिति हो; योजना व्यावहारिक राख्नुहोस् र धेरै प्रतिबद्धता नलिनुहोस्।",
    # EN: Jupiter in your 2nd supports family harmony, savings and kind speech.
    2: "दोस्रो भावमा बृहस्पतिले पारिवारिक सद्भाव, बचत र मधुर बोलीलाई साथ दिन्छ।",
    # EN: Jupiter in your 3rd asks a little more effort for the same result — keep at it.
    3: "तेस्रो भावमा बृहस्पतिले उही नतिजाका लागि अलि बढी प्रयास माग्छ — लागिरहनुहोस्।",
    # EN: Jupiter in your 4th can unsettle home matters; patience with relatives helps.
    4: "चौथो भावमा बृहस्पतिले घरका कुरा अस्थिर बनाउन सक्छ; नातेदारसँग धैर्य राख्नु राम्रो हुन्छ।",
    # EN: Jupiter in your 5th favours learning, children's matters, creativity and good counsel.
    5: "पाँचौँ भावमा बृहस्पतिले विद्या, सन्तानसम्बन्धी कुरा, सिर्जनशीलता र असल सल्लाहलाई साथ दिन्छ।",
    # EN: Jupiter in your 6th: steer clear of small disputes and overwork.
    6: "छैटौँ भावमा बृहस्पति: साना विवाद र अत्यधिक काम गर्नबाट टाढा रहनुहोस्।",
    # EN: Jupiter in your 7th blesses partnerships, marriage talks and travel.
    7: "सातौँ भावमा बृहस्पतिले साझेदारी, विवाहको कुरा र यात्रालाई आशीर्वाद दिन्छ।",
    # EN: Jupiter in your 8th suggests care with big decisions — go slow.
    8: "आठौँ भावमा बृहस्पतिले ठूला निर्णयमा होसियार हुन सुझाउँछ — बिस्तारै अघि बढ्नुहोस्।",
    # EN: Jupiter in your 9th is one of its best positions — fortune, dharma and guidance from
    #     teachers.
    9: "नवौँ भावमा बृहस्पति यसको सबैभन्दा राम्रो स्थितिमध्ये एक हो — भाग्य, धर्म र गुरुहरूको मार्गदर्शन।",
    # EN: Jupiter in your 10th may bring changes at work; stay adaptable.
    10: "दसौँ भावमा बृहस्पतिले कार्यक्षेत्रमा परिवर्तन ल्याउन सक्छ; लचिलो रहनुहोस्।",
    # EN: Jupiter in your 11th brings gains, fulfilled wishes and helpful friends.
    11: "एघारौँ भावमा बृहस्पतिले लाभ, इच्छा पूर्ति र सहयोगी साथीहरू ल्याउँछ।",
    # EN: Jupiter in your 12th brings expenses, often on good causes; charity and spiritual practice
    #     are well placed.
    12: "बाह्रौँ भावमा बृहस्पतिले खर्च ल्याउँछ, प्रायः असल कामका लागि; दान र आध्यात्मिक साधना उपयुक्त हुन्छन्।",
}

# app/rashifal_text.py RAHU_HOUSE["ne"] — Rahu transit through houses 1-12  [12]
RASHIFAL_RAHU_HOUSE = {
    # EN: Rahu over your Moon sign can stir restlessness and unusual wants; stay grounded.
    1: "तपाईंको चन्द्र राशिमाथि राहुले बेचैनी र असामान्य चाहना जगाउन सक्छ; जमिनमै खुट्टा राख्नुहोस्।",
    # EN: Rahu in your 2nd: take care with speech and money talk within the family.
    2: "दोस्रो भावमा राहु: परिवारभित्र बोली र पैसाको कुरामा सावधान रहनुहोस्।",
    # EN: Rahu in your 3rd is favourable — bold initiatives and communication succeed.
    3: "तेस्रो भावमा राहु शुभ छ — साहसी पहल र सञ्चारमा सफलता मिल्छ।",
    # EN: Rahu in your 4th can unsettle domestic peace; avoid hasty property moves.
    4: "चौथो भावमा राहुले घरको शान्ति बिथोल्न सक्छ; सम्पत्तिसम्बन्धी हतारिएको निर्णय नगर्नुहोस्।",
    # EN: Rahu in your 5th: double-check risky ideas and keep a clear head.
    5: "पाँचौँ भावमा राहु: जोखिमपूर्ण विचारलाई दोहोर्‍याएर जाँच्नुहोस् र मन शान्त राख्नुहोस्।",
    # EN: Rahu in your 6th helps you get past competition and obstacles.
    6: "छैटौँ भावमा राहुले प्रतिस्पर्धा र बाधा पार गर्न मद्दत गर्छ।",
    # EN: Rahu in your 7th: keep partnerships transparent.
    7: "सातौँ भावमा राहु: साझेदारीलाई पारदर्शी राख्नुहोस्।",
    # EN: Rahu in your 8th: avoid risky shortcuts and stay calm when the unexpected comes.
    8: "आठौँ भावमा राहु: जोखिमपूर्ण सजिलो बाटो नखोज्नुहोस् र अप्रत्याशित कुरा आउँदा शान्त रहनुहोस्।",
    # EN: Rahu in your 9th can raise doubts about beliefs or mentors; seek advice you trust.
    9: "नवौँ भावमा राहुले आस्था वा मार्गदर्शकबारे शङ्का उब्जाउन सक्छ; भरपर्दो सल्लाह लिनुहोस्।",
    # EN: Rahu in your 10th brings ambition and sudden openings at work; move with integrity.
    10: "दसौँ भावमा राहुले महत्त्वाकाङ्क्षा र कार्यक्षेत्रमा अचानक अवसर ल्याउँछ; इमानदारीसाथ अघि बढ्नुहोस्।",
    # EN: Rahu in your 11th — gains through networks and new contacts.
    11: "एघारौँ भावमा राहु — सम्पर्क र नयाँ चिनजानबाट लाभ।",
    # EN: Rahu in your 12th: watch hidden expenses and get proper rest.
    12: "बाह्रौँ भावमा राहु: लुकेका खर्चमा ध्यान दिनुहोस् र राम्ररी आराम गर्नुहोस्।",
}

# app/rashifal_text.py KETU_LINE["ne"] — Ketu line, True = favourable house, False = quiet house; {n} is the house  [2]
RASHIFAL_KETU_LINE = {
    # EN: Ketu in your {n} house works quietly in your favour — obstacles clear with less fuss.
    # keep: {n}
    True: "तपाईंको {n} भावमा केतुले चुपचाप तपाईंको पक्षमा काम गर्छ — बाधा सजिलै हट्छन्।",
    # EN: Ketu in your {n} house is a quieter, inward influence — good for reflection and spiritual
    #     practice, less so for impulsive moves.
    # keep: {n}
    False: "तपाईंको {n} भावमा केतु शान्त, भित्री प्रभाव हो — मनन र आध्यात्मिक साधनाका लागि राम्रो, हतारमा लिइने कदमका लागि कम।",
}

# app/rashifal_text.py CLOCK_LANG["ne"] — leave '' (the language's own clock words); 'en' prints 6:29 AM as Hindi pages do
# (optional: may stay empty)
RASHIFAL_CLOCK_LANG = ""

# ----------------------------------------------------------------------------
# vrat      /vrat-tyohar /ekadashi-<year> /tyohar/<slug>-<year>
# ----------------------------------------------------------------------------

# app/vrat_text.py TEXT["ne"] — page text of /vrat-tyohar, /ekadashi-<year>, /tyohar/<slug>-<year>  [64]
VRAT_TEXT = {
    # EN: Vrat & festivals
    "crumb": "व्रत र चाडपर्व",
    # EN: {date}, {weekday}
    # keep: {date} {weekday}
    "day_label": "{date}, {weekday}",
    # EN: {label}: {prefix}{value}
    # keep: {label} {prefix} {value}
    "timing": "{label}: {prefix}{value}",
    # EN: {paksha} {name}: {start} to {end}
    # keep: {end} {name} {paksha} {start}
    "tithi.text": "{paksha} {name}: {start} देखि {end} सम्म",
    # EN: {paksha}
    # keep: {paksha}
    "tithi.paksha": "{paksha}",
    # EN: <tr><th>Date</th><th>Vrat / festival</th><th>Timing ({city})</th></tr>
    # keep: {city}
    "table.th": "<tr><th>मिति</th><th>व्रत / चाडपर्व</th><th>समय ({city})</th></tr>",
    # EN: <div class="box"><p><strong>Timings vary by city.</strong> Every time here is for {city}'s
    #     sunrise, sunset and moonrise; in another city they shift by a few minutes and occasionally
    #     the date does too. Dates follow Drik Panchang's Smarta (default) reckoning. Check the
    #     Panchang for your own city.</p></div>
    # keep: {city}
    "city_note": "<div class=\"box\"><p><strong>समय सहरअनुसार फरक पर्छ।</strong> यहाँ दिइएका सबै समय {city} को सूर्योदय, सूर्यास्त र चन्द्रोदयअनुसारका हुन्; अर्को सहरमा ती केही मिनेट फरक पर्छन् र कहिलेकाहीँ मिति पनि फरक पर्न सक्छ। मिति दृक पञ्चाङ्गको स्मार्त (सामान्य) गणनाअनुसार हो। आफ्नै सहरको पञ्चाङ्ग हेर्नुहोस्।</p></div>",
    # EN: <p class="note"><small>For most observances the date is the same across India, but puja
    #     muhurat, parana and moonrise times differ from city to city - every time here is for
    #     <strong>{city}</strong>. Regional traditions may vary.</small></p>
    # keep: {city}
    "top_note": "<p class=\"note\"><small>प्रायः सबै पर्वको मिति भारतभर एउटै हुन्छ, तर पूजा मुहूर्त, पारण र चन्द्रोदयको समय सहरअनुसार फरक पर्छ — यहाँ दिइएका सबै समय <strong>{city}</strong> का लागि हुन्। क्षेत्रीय परम्परा फरक हुन सक्छ।</small></p>",
    # EN: Vrat & festivals in your city
    "cities.heading": "तपाईंको सहरका व्रत र चाडपर्व",
    # EN: Today's Panchang in {city}
    # keep: {city}
    "tools.panchang": "{city} को आजको पञ्चाङ्ग",
    # EN: Rahu Kaal in {city}
    # keep: {city}
    # may also use: {t_rahu_kaal}
    "tools.rahu": "{city} मा राहुकाल",
    # EN: More for {city}
    # keep: {city}
    "tools.heading": "{city} का लागि थप",
    # EN: See the Panchang for your city — free
    "cta": "आफ्नो सहरको पञ्चाङ्ग हेर्नुहोस् — निःशुल्क",
    # EN: Today's vrat & festivals
    "more.today": "आजका व्रत र चाडपर्व",
    # EN: Festival calendar {year}
    # keep: {year}
    "more.year": "चाडपर्व पात्रो {year}",
    # EN: Ekadashi {year}
    # keep: {year}
    "more.ekadashi": "एकादशी {year}",
    # EN: Today's Panchang
    "more.panchang": "आजको पञ्चाङ्ग",
    # EN: Today's Rashifal
    "more.rashifal": "आजको राशिफल",
    # EN: More
    "more.heading": "थप",
    # EN: Major festivals {year}
    # keep: {year}
    "majors.heading": "प्रमुख चाडपर्व {year}",
    # EN: Rule
    "today.rule": "नियम",
    # EN: No major vrat or festival today.
    "today.none": "आज कुनै प्रमुख व्रत वा चाड छैन।",
    # EN: Next: <strong>{name}</strong> on {day}.
    # keep: {day} {name}
    "today.next": " अर्को: <strong>{name}</strong>, {day} मा।",
    # EN: Vrat &amp; Festivals today
    "block.heading": "आजका व्रत र चाडपर्व",
    # EN: Page not found
    "nf.h1": "पृष्ठ फेला परेन",
    # EN: Aaj Ke Vrat aur Tyohar: Today's Vrat & Festivals ({date})
    # keep: {date}
    "hub.title_default": "आजका व्रत र चाडपर्व ({date})",
    # EN: Today's Vrat & Festivals in {city} ({date}) - Aaj Ke Vrat
    # keep: {city} {date}
    "hub.title_city": "{city} मा आजका व्रत र चाडपर्व ({date})",
    # EN: Today's vrat & festivals
    "hub.h1_default": "आजका व्रत र चाडपर्व",
    # EN: Today's vrat & festivals in {city}
    # keep: {city}
    "hub.h1_city": "{city} मा आजका व्रत र चाडपर्व",
    # EN: Today, {date}: {names}.
    # keep: {date} {names}
    "hub.desc_today": "आज, {date}: {names}। ",
    # EN: {date}: no major vrat today.
    # keep: {date}
    "hub.desc_none": "{date}: आज कुनै प्रमुख व्रत छैन। ",
    # EN: Upcoming fasts and festivals for 30 days with Ekadashi parana, Pradosh and Sankashti
    #     moonrise times - {city}.
    # keep: {city}
    "hub.desc_rest": "आगामी 30 दिनका व्रत र चाडपर्व — एकादशीको पारण, प्रदोष र सङ्कष्टी चन्द्रोदयको समयसहित — {city}।",
    # EN: <p class="hi" lang="hi">आज के व्रत और त्योहार</p>
    "hub.sub": "<p class=\"hi\" lang=\"ne\">आजका व्रत र चाडपर्व</p>",
    # EN: Next 30 days
    "hub.upcoming": "आगामी 30 दिन",
    # EN: Hindu Festival & Vrat Calendar {year} (New Delhi): Dates and Muhurat
    # keep: {year}
    "year.title": "हिन्दू चाडपर्व र व्रत पात्रो {year} (नयाँ दिल्ली): मिति र मुहूर्त",
    # EN: Vrat & festival calendar {year}
    # keep: {year}
    "year.h1": "व्रत र चाडपर्व पात्रो {year}",
    # EN: Every Hindu vrat and festival of {year}, month by month - Ekadashi, Pradosh, Sankashti,
    #     Purnima, Amavasya, Shivratri and festivals like Diwali, Navratri and Raksha Bandhan, with
    #     puja muhurat for New Delhi.
    # keep: {year}
    "year.desc": "{year} का हिन्दू व्रत र चाडपर्व महिनैपिच्छे — एकादशी, प्रदोष, सङ्कष्टी, पूर्णिमा, औंसी, शिवरात्रि र दीपावली, नवरात्र, रक्षाबन्धनजस्ता चाड, नयाँ दिल्लीको पूजा मुहूर्तसहित।",
    # EN: <p><strong>{count}</strong> fasts and festivals in {year} for New Delhi, computed from the
    #     panchang. Tap a major festival for its puja muhurat and what it is about.</p>
    # keep: {count} {year}
    "year.intro": "<p>नयाँ दिल्लीका लागि {year} मा <strong>{count}</strong> व्रत र चाडपर्व, पञ्चाङ्गबाट गणना गरिएको। कुनै प्रमुख चाडमा थिच्नुहोस् — त्यसको पूजा मुहूर्त र महत्त्व हेर्न।</p>",
    # EN: {month} {year}
    # keep: {month} {year}
    "year.month": "{month} {year}",
    # EN: Major Hindu festivals {year}
    # keep: {year}
    "year.itemlist": "प्रमुख हिन्दू चाडपर्व {year}",
    # EN: Ekadashi {year}: All Ekadashi Vrat Dates and Parana Time (New Delhi)
    # keep: {year}
    "ek.title": "एकादशी {year}: सबै एकादशी व्रतको मिति र पारण समय (नयाँ दिल्ली)",
    # EN: Ekadashi {year}: dates and parana time
    # keep: {year}
    "ek.h1": "एकादशी {year}: मिति र पारण समय",
    # EN: All {count} Ekadashis of {year} - fasting date, Ekadashi tithi times and the parana (fast-
    #     breaking) window next day, for New Delhi.
    # keep: {count} {year}
    "ek.desc": "{year} का सबै {count} एकादशी — व्रतको मिति, एकादशी तिथिको समय र भोलिपल्टको पारण (व्रत खोल्ने) समय, नयाँ दिल्लीका लागि।",
    # EN: <tr><th>Ekadashi</th><th>Fast</th><th>Parana</th></tr>
    "ek.th": "<tr><th>एकादशी</th><th>व्रत</th><th>पारण</th></tr>",
    # EN: <p><strong>Rule (Smarta):</strong> fast on the day Ekadashi prevails at sunrise; if it
    #     prevails at two sunrises, the second day, and if at none, the day it falls in. Parana is
    #     the next day after sunrise, once Hari Vasara (the first quarter of Dwadashi) is over,
    #     within Pratahkala and before Dwadashi ends; if Hari Vasara runs past Pratahkala, parana
    #     moves to Aparahna (Madhyahna is avoided).</p>
    "ek.rule": "<p><strong>नियम (स्मार्त):</strong> सूर्योदयमा एकादशी तिथि भएको दिन व्रत गर्नुहोस्; दुई सूर्योदयमा परे दोस्रो दिन, र कुनै सूर्योदयमा नपरे जुन दिन पर्छ त्यही दिन। पारण भोलिपल्ट सूर्योदयपछि, हरि वासर (द्वादशीको पहिलो चौथाइ) सकिएपछि, प्रातःकालभित्र र द्वादशी सकिनुअघि गरिन्छ; हरि वासर प्रातःकाल नाघेर गए पारण अपराह्नमा सारिन्छ (मध्याह्न छोडिन्छ)।</p>",
    # EN: <p class="hi" lang="hi">एकादशी {year}</p>
    # keep: {year}
    "ek.sub": "<p class=\"hi\" lang=\"ne\">एकादशी {year}</p>",
    # EN: Ekadashi {year}
    # keep: {year}
    "ek.crumb": "एकादशी {year}",
    # EN: {name} {year}: Date and Puja Muhurat - {short}
    # keep: {name} {short} {year}
    "fest.title": "{name} {year}: मिति र पूजा मुहूर्त - {short}",
    # EN: {name} {year}: date and muhurat
    # keep: {name} {year}
    "fest.h1": "{name} {year}: मिति र मुहूर्त",
    # EN: {text}.
    # keep: {text}
    "fest.main": "{text}। ",
    # EN: {name} {year} is on {weekday}, {date}. {main}Puja timings for New Delhi.
    # keep: {date} {main} {name} {weekday} {year}
    "fest.desc": "{name} {year} {weekday}, {date} मा पर्छ। {main}नयाँ दिल्लीको पूजा समय।",
    # EN: {name} {year} is on <strong>{when}</strong>.
    # keep: {name} {when} {year}
    "fest.when": "{name} {year} <strong>{when}</strong> मा पर्छ।",
    # EN: <p class="hi" lang="hi">{name_hi} {year}</p>
    # keep: {year}
    "fest.sub": "<p class=\"hi\" lang=\"ne\">{year} को मिति र पूजा मुहूर्त</p>",
    # EN: What it is and how it is observed
    "fest.about_h2": "यो के हो र कसरी मनाइन्छ",
    # EN: How the date is fixed
    "fest.rule_h2": "मिति कसरी निर्धारण गरिन्छ",
    # EN: Frequently asked questions
    "fest.faq_h2": "प्रायः सोधिने प्रश्नहरू",
    # EN: India
    "event.place": "भारत",
    # EN: When is {name} {year}?
    # keep: {name} {year}
    "faq.when_q": "{name} {year} कहिले पर्छ?",
    # EN: {name} {year} is on {weekday}, {date}.
    # keep: {date} {name} {weekday} {year}
    "faq.when_a": "{name} {year} {weekday}, {date} मा पर्छ।",
    # EN: What is the {name} {year} puja muhurat?
    # keep: {name} {year}
    "faq.muhurat_q": "{name} {year} को पूजा मुहूर्त कति बजे हो?",
    # EN: What are the {name} {year} timings?
    # keep: {name} {year}
    "faq.timings_q": "{name} {year} को समय कति हो?",
    # EN: For New Delhi - {timings}. Timings vary by city by a few minutes; check the Panchang for
    #     your city.
    # keep: {timings}
    "faq.timings_a": "नयाँ दिल्लीका लागि - {timings}। समय सहरअनुसार केही मिनेट फरक पर्छ; आफ्नो सहरको पञ्चाङ्ग हेर्नुहोस्।",
    # EN: Why is {name} {year} observed on {short}?
    # keep: {name} {short} {year}
    "faq.why_q": "{name} {year} किन {short} मा मनाइन्छ?",
    # EN: The date follows the rule: {rule}. In {year} that is {when} (New Delhi).
    # keep: {rule} {when} {year}
    "faq.why_a": "मिति यो नियमअनुसार तय हुन्छ: {rule}। {year} मा त्यो {when} (नयाँ दिल्ली) हो।",
}

# app/vrat_text.py ABOUT["ne"] — what each of the 47 festivals / vrats is (key = festival slug)  [47]
VRAT_ABOUT = {
    # EN: Makar Sankranti marks the Sun's entry into Makara (Capricorn) and the start of its
    #     northward journey (Uttarayana). It is a harvest festival: people bathe in holy rivers,
    #     give til (sesame), jaggery, khichdi and blankets in charity, and fly kites.
    "makar-sankranti": "मकर सङ्क्रान्ति सूर्य मकर राशिमा प्रवेश गर्ने र उत्तरायणतर्फ यात्रा सुरु गर्ने दिन हो। यो बाली भित्र्याउने चाड हो: मानिसहरू पवित्र नदीमा स्नान गर्छन्, तिल, गुड, खिचडी र कम्बल दान गर्छन् र चङ्गा उडाउँछन्।",
    # EN: Maha Shivratri, the great night of Shiva, falls on the Krishna Chaturdashi of Magha.
    #     Devotees fast, offer water, milk and bel leaves on the Shivling, chant Om Namah Shivaya
    #     and keep vigil through the four prahars of the night; the Nishita kaal puja around
    #     midnight is the most important.
    "maha-shivratri": "महाशिवरात्रि, शिवको महान् रात, माघ कृष्ण चतुर्दशीमा पर्छ। भक्तहरू व्रत बस्छन्, शिवलिङ्गमा जल, दूध र बेलपत्र चढाउँछन्, ॐ नमः शिवाय जप्छन् र रातका चार प्रहर जागरण बस्छन्; मध्यरातको निशीथ काल पूजा सबैभन्दा महत्त्वपूर्ण मानिन्छ।",
    # EN: Holika Dahan, on the eve of Holi, celebrates Prahlad's devotion and the victory of good
    #     over evil. A bonfire is lit after sunset, avoiding Bhadra, and families circle it offering
    #     grain, coconut and prayers.
    "holika-dahan": "होली अघिल्लो साँझ गरिने होलिका दहनले प्रह्लादको भक्ति र असत्यमाथि सत्यको विजयको उत्सव मनाउँछ। सूर्यास्तपछि, भद्रा छोडेर, आगो बालिन्छ र परिवारका सदस्य त्यसको परिक्रमा गर्दै अन्न, नरिवल र प्रार्थना अर्पण गर्छन्।",
    # EN: Holi, the festival of colours, is celebrated the morning after Holika Dahan with colours,
    #     music, sweets like gujiya and visits to family and friends.
    "holi": "रङहरूको चाड होली होलिका दहनको भोलिपल्ट बिहान रङ, सङ्गीत, गुजिया जस्ता मिठाई र परिवार तथा साथीभाइकहाँको भेटघाटसँग मनाइन्छ।",
    # EN: Ram Navami celebrates the birth of Lord Rama on Chaitra Shukla Navami, at midday. Devotees
    #     fast, read the Ramcharitmanas, and offer puja in the Madhyahna muhurat, the time of his
    #     birth.
    "ram-navami": "रामनवमीले चैत्र शुक्ल नवमीको मध्यान्हमा भगवान रामको जन्मको उत्सव मनाउँछ। भक्तहरू व्रत बस्छन्, रामचरितमानस पढ्छन् र उनको जन्मको समय मध्याह्न मुहूर्तमा पूजा गर्छन्।",
    # EN: Hanuman Jayanti (Chaitra Purnima in North India) celebrates the birth of Lord Hanuman.
    #     Devotees visit Hanuman temples, recite the Hanuman Chalisa and Sundarkand, and offer
    #     sindoor and laddoos.
    "hanuman-jayanti": "हनुमान जयन्ती (उत्तर भारतमा चैत्र पूर्णिमा) ले भगवान हनुमानको जन्म मनाउँछ। भक्तहरू हनुमान मन्दिर जान्छन्, हनुमान चालीसा र सुन्दरकाण्ड पढ्छन् र सिन्दूर तथा लड्डू चढाउँछन्।",
    # EN: Akshaya Tritiya, Vaishakha Shukla Tritiya, is held to make every good deed 'akshaya' -
    #     undiminishing. People worship Vishnu and Lakshmi, give in charity, and begin new ventures
    #     or buy gold.
    "akshaya-tritiya": "अक्षय तृतीया, बैशाख शुक्ल तृतीया, मा गरिएका हरेक असल काम 'अक्षय' अर्थात् कहिल्यै नघट्ने हुन्छन् भन्ने मान्यता छ। मानिसहरू विष्णु र लक्ष्मीको पूजा गर्छन्, दान दिन्छन् र नयाँ काम सुरु गर्छन् वा सुन किन्छन्।",
    # EN: Raksha Bandhan, on Shravana Purnima, celebrates the bond between brothers and sisters.
    #     Sisters tie a rakhi on their brother's wrist and pray for his well-being; the rakhi is
    #     tied in a time free of Bhadra.
    "raksha-bandhan": "रक्षाबन्धन, श्रावण पूर्णिमामा, दाजुभाइ र दिदीबहिनीबीचको सम्बन्धको उत्सव हो। बहिनीले दाजु वा भाइको नाडीमा राखी बाँध्छिन् र उनको कल्याणको कामना गर्छिन्; राखी भद्रा नभएको समयमा बाँधिन्छ।",
    # EN: Krishna Janmashtami celebrates the birth of Lord Krishna at midnight on Krishna Ashtami of
    #     Bhadrapada (purnimanta). Devotees fast through the day and break it after the Nishita
    #     (midnight) puja, when the infant Krishna is bathed and placed in a cradle.
    "janmashtami": "कृष्ण जन्माष्टमीले भाद्र कृष्ण अष्टमी (पूर्णिमान्त) को मध्यरातमा भगवान श्रीकृष्णको जन्म मनाउँछ। भक्तहरू दिनभर व्रत बस्छन् र निशीथ (मध्यरात) पूजापछि व्रत खोल्छन्, जब बाल कृष्णलाई स्नान गराएर पालनामा राखिन्छ।",
    # EN: Ganesh Chaturthi, Bhadrapada Shukla Chaturthi, welcomes Lord Ganesha home. The idol is
    #     installed and worshipped in the Madhyahna (midday) muhurat, the time of his birth, with
    #     modak, durva grass and red flowers; looking at the Moon on this day is avoided.
    "ganesh-chaturthi": "गणेश चतुर्थी, भाद्र शुक्ल चतुर्थी, मा भगवान गणेशलाई घरमा स्वागत गरिन्छ। उनको जन्मको समय मध्याह्न (दिउँसो) मुहूर्तमा मूर्ति स्थापना गरी मोदक, दूर्वा र रातो फूलले पूजा गरिन्छ; यस दिन चन्द्रमा हेर्नुहुँदैन भन्ने मान्यता छ।",
    # EN: Chaitra Navratri, the nine nights of Goddess Durga in spring, begins on Chaitra Shukla
    #     Pratipada - also the Hindu New Year (Vikram Samvat). Ghatasthapana (installing the kalash)
    #     opens the nine days of worship.
    "chaitra-navratri": "चैत्र नवरात्र, वसन्त ऋतुमा देवी दुर्गाका नौ रात, चैत्र शुक्ल प्रतिपदामा सुरु हुन्छ — यही दिन हिन्दू नयाँ वर्ष (विक्रम संवत्) पनि हो। घटस्थापना (कलश स्थापना) ले नौ दिनको पूजा सुरु गर्छ।",
    # EN: Sharad Navratri, the nine nights of Goddess Durga in autumn, begins on Ashwin Shukla
    #     Pratipada with Ghatasthapana - installing the kalash and sowing barley - in the morning.
    #     Each day honours one of the nine forms of the Goddess.
    "navratri": "शारदीय नवरात्र (दशैंको सुरुआत), शरद ऋतुमा देवी दुर्गाका नौ रात, आश्विन शुक्ल प्रतिपदामा बिहान घटस्थापना — कलश स्थापना र जौ रोपेर — सुरु हुन्छ। हरेक दिन देवीको नौ रूपमध्ये एकको पूजा गरिन्छ।",
    # EN: Dussehra (Vijayadashami) marks Lord Rama's victory over Ravana and Goddess Durga's over
    #     Mahishasura. Shami puja, Aparajita puja and the burning of Ravana effigies are held in the
    #     afternoon; the Vijay muhurat is considered good for starting anything new.
    "dussehra": "विजयादशमी (दशैं) ले भगवान रामको रावणमाथि र देवी दुर्गाको महिषासुरमाथिको विजय मनाउँछ। शमी पूजा, अपराजिता पूजा र रावणको पुतला दहन अपराह्नमा हुन्छ; नयाँ काम सुरु गर्न विजय मुहूर्त शुभ मानिन्छ।",
    # EN: On Karwa Chauth married women keep a fast from sunrise to moonrise for their husbands'
    #     long life. The evening puja of Karwa Mata is followed by offering water (arghya) to the
    #     Moon, after which the fast is broken.
    "karwa-chauth": "करवा चौथमा विवाहित महिलाहरू पतिको दीर्घायुका लागि सूर्योदयदेखि चन्द्रोदयसम्म व्रत बस्छन्। साँझ करवा माताको पूजापछि चन्द्रमालाई अर्घ्य दिइन्छ, त्यसपछि व्रत खोलिन्छ।",
    # EN: On Ahoi Ashtami, eight days before Diwali, mothers keep a fast for the well-being of their
    #     children and worship Ahoi Mata in the evening; the fast is traditionally broken after
    #     sighting the stars (or, in some families, the Moon).
    "ahoi-ashtami": "दीपावलीभन्दा आठ दिनअघि पर्ने अहोई अष्टमीमा आमाहरू सन्तानको कल्याणका लागि व्रत बस्छन् र साँझ अहोई मातालाई पूजा गर्छन्; परम्परागत रूपमा तारा देखेपछि (केही परिवारमा चन्द्रमा देखेपछि) व्रत खोलिन्छ।",
    # EN: Dhanteras, the first day of Diwali, honours Dhanvantari and Goddess Lakshmi. People buy
    #     new utensils, gold or silver and light the Yama deepak at dusk; the puja is done in
    #     Pradosh kaal, ideally in the fixed (sthir) Vrishabha lagna.
    "dhanteras": "दीपावलीको पहिलो दिन धनतेरसमा धन्वन्तरि र देवी लक्ष्मीको पूजा गरिन्छ। मानिसहरू नयाँ भाँडा, सुन वा चाँदी किन्छन् र गोधूलिमा यम दीप बाल्छन्; पूजा प्रदोष कालमा, आदर्श रूपमा स्थिर वृष लग्नमा गरिन्छ।",
    # EN: Diwali, on Kartika Amavasya, is the festival of lights. Lakshmi and Ganesha are worshipped
    #     in the evening - in Pradosh kaal, preferably in the fixed (sthir) Vrishabha lagna so that
    #     prosperity stays - and homes are lit with diyas.
    "diwali": "कार्तिक औंसीमा पर्ने दीपावली (तिहारको लक्ष्मी पूजा) प्रकाशको चाड हो। साँझ — प्रदोष कालमा, समृद्धि टिकिरहोस् भनेर सकेसम्म स्थिर वृष लग्नमा — लक्ष्मी र गणेशको पूजा गरिन्छ र घरमा दियो बालिन्छ।",
    # EN: Govardhan Puja (Annakut), the day after Diwali, remembers Krishna lifting Govardhan hill.
    #     A Govardhan of cow-dung or food is worshipped and an annakut of many dishes is offered,
    #     usually in the morning (Pratahkala).
    "govardhan-puja": "गोवर्धन पूजा (अन्नकूट), दीपावलीको भोलिपल्ट, कृष्णले गोवर्धन पर्वत उठाएको सम्झना गर्छ। गोबर वा खानेकुराको गोवर्धन बनाएर पूजा गरिन्छ र थुप्रै परिकारको अन्नकूट चढाइन्छ, सामान्यतया बिहान (प्रातःकाल) मा।",
    # EN: Bhai Dooj, Kartika Shukla Dwitiya, celebrates brothers and sisters: sisters apply a tilak,
    #     perform aarti and pray for their brother's long life, ideally in the Aparahna (afternoon)
    #     time.
    "bhai-dooj": "भाइदूज (भाइटीका), कार्तिक शुक्ल द्वितीया, दाजुभाइ र दिदीबहिनीको चाड हो: बहिनीले टीका लगाइदिन्छिन्, आरती गर्छिन् र दाजु वा भाइको दीर्घायुको कामना गर्छिन्, आदर्श रूपमा अपराह्न (दिउँसो) को समयमा।",
    # EN: Chhath Puja worships the Sun God and Chhathi Maiya over four days. On the main day
    #     (Kartika Shukla Shashthi) devotees stand in water and offer arghya to the setting Sun, and
    #     to the rising Sun the next morning, ending a fast kept without water.
    "chhath-puja": "छठ पूजामा चार दिनसम्म सूर्य देवता र छठी मैयाको पूजा गरिन्छ। मुख्य दिन (कार्तिक शुक्ल षष्ठी) भक्तहरू पानीमा उभिएर अस्ताउँदो सूर्यलाई र भोलिपल्ट बिहान उदाउँदो सूर्यलाई अर्घ्य दिन्छन्, र निर्जल व्रत सक्छन्।",
    # EN: Vasant Panchami, Magha Shukla Panchami, welcomes spring and honours Goddess Saraswati.
    #     Students and artists worship books and instruments, people wear yellow, and children often
    #     begin learning to write (vidyarambh).
    "vasant-panchami": "वसन्त पञ्चमी (श्रीपञ्चमी), माघ शुक्ल पञ्चमी, मा वसन्त ऋतुको स्वागत गरिन्छ र देवी सरस्वतीको पूजा गरिन्छ। विद्यार्थी र कलाकारहरू किताब र वाद्ययन्त्रको पूजा गर्छन्, मानिसहरू पहेँलो लुगा लगाउँछन् र बच्चाहरूले प्रायः लेख्न सिक्न सुरु गर्छन् (विद्यारम्भ)।",
    # EN: Guru Purnima, Ashadha Purnima, honours one's teachers and Maharishi Ved Vyasa, born on
    #     this day. Disciples offer gratitude, flowers and gifts to their guru.
    "guru-purnima": "गुरु पूर्णिमा, आषाढ पूर्णिमा, मा आफ्ना गुरुहरू र यसै दिन जन्मेका महर्षि वेदव्यासको सम्मान गरिन्छ। शिष्यहरूले आफ्ना गुरुलाई कृतज्ञता, फूल र उपहार अर्पण गर्छन्।",
    # EN: Sharad Purnima, Ashwin Purnima, is the night the Moon is held to be brightest and full of
    #     nectar. Kheer is kept in the moonlight overnight and eaten as prasad; Lakshmi is
    #     worshipped (Kojagari).
    "sharad-purnima": "शरद पूर्णिमा, आश्विन पूर्णिमा, मा चन्द्रमा सबैभन्दा उज्यालो र अमृतले भरिएको हुन्छ भन्ने मान्यता छ। खीर रातभर चाँदनीमा राखेर प्रसादका रूपमा खाइन्छ; लक्ष्मीको पूजा गरिन्छ (कोजागरी)।",
    # EN: Devuthani (Prabodhini) Ekadashi, Kartika Shukla Ekadashi, is when Lord Vishnu is held to
    #     wake from his four-month sleep, ending Chaturmas. Tulsi vivah begins and the wedding
    #     season opens. Devotees fast and break the fast (parana) the next day.
    "devuthani-ekadashi": "देवउठनी (प्रबोधिनी) एकादशी, कार्तिक शुक्ल एकादशी, मा भगवान विष्णु चार महिनाको निद्रापछि ब्युँझिन्छन् भन्ने मान्यता छ, जसले चातुर्मास सकिन्छ। तुलसी विवाह सुरु हुन्छ र विवाहको लगन खुल्छ। भक्तहरू व्रत बस्छन् र भोलिपल्ट पारण गर्छन्।",
    # EN: Jivitputrika (Jitiya, Jiutiya) is kept by mothers in Bihar, Jharkhand, eastern Uttar
    #     Pradesh and Nepal for the long life and well-being of their children, on Ashwin Krishna
    #     Ashtami (purnimanta). It begins with nahay-khay the day before; the fast itself is
    #     nirjala, without water, through the day and night, with worship of Jimutavahana and the
    #     Jitiya katha. Parana, breaking the fast, is the next morning.
    "jivitputrika": "जीवित्पुत्रिका (जितिया, जिउतिया) बिहार, झारखण्ड, पूर्वी उत्तर प्रदेश र नेपालका आमाहरूले सन्तानको दीर्घायु र कल्याणका लागि आश्विन कृष्ण अष्टमी (पूर्णिमान्त) मा गर्छन्। यो अघिल्लो दिन नहाय–खाय बाट सुरु हुन्छ; व्रत आफैँ निर्जल हुन्छ, दिन र रातभर, जीमूतवाहनको पूजा र जितिया कथासहित। पारण भोलिपल्ट बिहान हुन्छ।",
    # EN: Lohri, the evening before Makar Sankranti, is the winter harvest festival of Punjab and
    #     North India. A bonfire is lit at dusk and people offer til, gur, rewari, peanuts and
    #     popcorn to it, sing and dance; it is especially celebrated for a new bride or a newborn.
    "lohri": "लोहडी, मकर सङ्क्रान्तिको अघिल्लो साँझ, पन्जाब र उत्तर भारतको हिउँदे बाली भित्र्याउने चाड हो। गोधूलिमा आगो बालिन्छ र मानिसहरू त्यसमा तिल, गुड, रेवडी, बदाम र पप्कर्न चढाउँछन्, गीत गाउँछन् र नाच्छन्; नयाँ दुलही वा नवजात शिशु भएको घरमा विशेष रूपले मनाइन्छ।",
    # EN: Sakat Chauth (Tilkut Chauth), the Sankashti Chaturthi of Magha (purnimanta), is kept by
    #     mothers for their children. Ganesha and Sakat Mata are worshipped with til and jaggery,
    #     and the fast is broken after offering arghya to the rising Moon.
    "sakat-chauth": "सकट चौथ (तिलकूट चौथ), माघ (पूर्णिमान्त) को सङ्कष्टी चतुर्थी, आमाहरूले सन्तानका लागि गर्छन्। तिल र गुडले गणेश र सकट मातालाई पूजा गरिन्छ, र उदाउँदो चन्द्रमालाई अर्घ्य दिएपछि व्रत खोलिन्छ।",
    # EN: Mauni Amavasya, the Amavasya of Magha (purnimanta), is the great bathing day of the Magh
    #     Mela at Prayagraj. Devotees bathe in the Ganga or a holy river, keep silence (mauna) and
    #     give in charity.
    "mauni-amavasya": "मौनी औंसी, माघ (पूर्णिमान्त) को औंसी, प्रयागराजमा लाग्ने माघ मेलाको प्रमुख स्नान दिन हो। भक्तहरू गङ्गा वा कुनै पवित्र नदीमा स्नान गर्छन्, मौन (मौन व्रत) बस्छन् र दान दिन्छन्।",
    # EN: Sheetala Ashtami (Basoda), Chaitra Krishna Ashtami (purnimanta), honours Sheetala Mata,
    #     the goddess who protects from fevers and pox. Food is cooked the day before and the stale
    #     (basi) food is offered and eaten; no fire is lit for cooking that day.
    "sheetala-ashtami": "शीतला अष्टमी (बसोडा), चैत्र कृष्ण अष्टमी (पूर्णिमान्त), ज्वरो र दाग निकाल्ने रोगबाट बचाउने देवी शीतला मातालाई समर्पित छ। खाना अघिल्लो दिन पकाइन्छ र बासी खाना चढाएर खाइन्छ; त्यस दिन पकाउनका लागि आगो बालिँदैन।",
    # EN: Gudi Padwa (Maharashtra) and Ugadi (Karnataka, Andhra Pradesh, Telangana) mark the lunar
    #     New Year on Chaitra Shukla Pratipada. A gudi - a decorated pole with a cloth and kalash -
    #     is raised at the door, and neem with jaggery is eaten for a year of both sweet and bitter.
    "gudi-padwa": "गुडी पाडवा (महाराष्ट्र) र उगादी (कर्नाटक, आन्ध्र प्रदेश, तेलङ्गाना) ले चैत्र शुक्ल प्रतिपदामा चन्द्र नववर्ष मनाउँछन्। कपडा र कलश सजाएको गुडी भन्ने बाँस ढोकामा उठाइन्छ, र वर्षभरि मीठो र तितो दुवै अनुभवको प्रतीकका रूपमा गुडसँग नीम खाइन्छ।",
    # EN: Gangaur, Chaitra Shukla Tritiya, is Rajasthan's festival of Gauri (Parvati) and Shiva.
    #     Women worship Gauri for marital happiness - married women for their husbands, girls for a
    #     good match - ending eighteen days of puja that begin the day after Holi.
    "gangaur": "गणगौर, चैत्र शुक्ल तृतीया, गौरी (पार्वती) र शिवको राजस्थानी चाड हो। महिलाहरूले दाम्पत्य सुखका लागि गौरीको पूजा गर्छन् — विवाहित महिलाले पतिका लागि, कन्याले राम्रो वरका लागि — होलीको भोलिपल्टदेखि सुरु भएको अठार दिनको पूजा यसै दिन सम्पन्न हुन्छ।",
    # EN: Vat Savitri Vrat, on Jyeshtha Amavasya in North India (purnimanta), remembers Savitri, who
    #     won back her husband Satyavan's life from Yama. Married women fast, worship the banyan
    #     (vat) tree, tie raw thread around it while circling it, and hear the Savitri katha.
    "vat-savitri": "वट सावित्री व्रत, उत्तर भारतमा जेष्ठ औंसी (पूर्णिमान्त) मा, सावित्रीको सम्झना हो, जसले यमबाट पति सत्यवानको प्राण फिर्ता ल्याइन्। विवाहित महिलाहरू व्रत बस्छन्, वट (बरको) रूखको पूजा गर्छन्, परिक्रमा गर्दै त्यसमा काँचो धागो बेर्छन् र सावित्री कथा सुन्छन्।",
    # EN: Vat Purnima is the same Vat Savitri vrat as kept on Jyeshtha Purnima in Maharashtra,
    #     Gujarat and the south (amanta calendar), fifteen days after the North Indian date. Married
    #     women fast and worship the banyan tree for their husbands' long life.
    "vat-purnima": "वट पूर्णिमा त्यही वट सावित्री व्रत हो जुन महाराष्ट्र, गुजरात र दक्षिणमा (अमान्त पात्रो) जेष्ठ पूर्णिमामा, उत्तर भारतको मितिभन्दा पन्ध्र दिनपछि गरिन्छ। विवाहित महिलाहरू पतिको दीर्घायुका लागि व्रत बस्छन् र बरको रूखको पूजा गर्छन्।",
    # EN: Ganga Dussehra, Jyeshtha Shukla Dashami, celebrates the descent of the Ganga to earth
    #     through Bhagiratha's penance. Devotees bathe in the Ganga, offer lamps and give in
    #     charity; the bath is held to wash away ten kinds of sin.
    "ganga-dussehra": "गङ्गा दसहरा, जेष्ठ शुक्ल दशमी, मा भगीरथको तपस्याले गङ्गा पृथ्वीमा अवतरण भएको उत्सव मनाइन्छ। भक्तहरू गङ्गामा स्नान गर्छन्, दीप चढाउँछन् र दान दिन्छन्; यो स्नानले दस प्रकारका पाप धुन्छ भन्ने मान्यता छ।",
    # EN: Hariyali Teej, Shravana Shukla Tritiya, celebrates the reunion of Shiva and Parvati in the
    #     monsoon. Women wear green, apply mehndi, swing on decorated jhoolas, sing Sawan songs and
    #     many keep a fast for their husbands.
    "hariyali-teej": "हरियाली तीज, श्रावण शुक्ल तृतीया, मा वर्षा ऋतुमा शिव र पार्वतीको पुनर्मिलनको उत्सव मनाइन्छ। महिलाहरू हरियो लुगा लगाउँछन्, मेहन्दी लगाउँछन्, सजाइएको झुलामा झुल्छन्, सावनका गीत गाउँछन् र धेरैले पतिका लागि व्रत बस्छन्।",
    # EN: Nag Panchami, Shravana Shukla Panchami, is the day serpent deities (nagas) are worshipped.
    #     Images of snakes are drawn or installed and offered milk, flowers and sweets, with prayers
    #     for the family's protection. (In Gujarat, Nag Pancham falls later, in Bhadrapada.)
    "nag-panchami": "नाग पञ्चमी, श्रावण शुक्ल पञ्चमी, मा सर्प देवता (नाग) को पूजा गरिन्छ। सर्पका चित्र बनाइन्छ वा मूर्ति राखिन्छ र दूध, फूल तथा मिठाई चढाएर परिवारको रक्षाको प्रार्थना गरिन्छ। (गुजरातमा नाग पञ्चम पछि, भाद्रमा पर्छ।)",
    # EN: Kajari (Kajli, Badi) Teej, Bhadrapada Krishna Tritiya (purnimanta), is kept by married
    #     women of Uttar Pradesh, Bihar, Rajasthan and Madhya Pradesh. They fast, worship the neem
    #     tree (Neemadi Mata) and break the fast after offering arghya to the Moon; kajari folk
    #     songs are sung.
    "kajari-teej": "कजरी (कजली, बडी) तीज, भाद्र कृष्ण तृतीया (पूर्णिमान्त), उत्तर प्रदेश, बिहार, राजस्थान र मध्य प्रदेशका विवाहित महिलाहरूले गर्छन्। उनीहरू व्रत बस्छन्, नीमको रूख (नीमडी माता) को पूजा गर्छन् र चन्द्रमालाई अर्घ्य दिएपछि व्रत खोल्छन्; कजरी लोकगीत गाइन्छ।",
    # EN: Hal Shashthi (Lalahi Chhath, Har Chhath), Bhadrapada Krishna Shashthi (purnimanta), is
    #     Lord Balarama's birthday, whose weapon is the plough (hal). Mothers fast for their
    #     children and eat nothing grown with a plough - often pasahi rice and buffalo milk.
    "hal-shashthi": "हल षष्ठी (ललही छठ, हर छठ), भाद्र कृष्ण षष्ठी (पूर्णिमान्त), भगवान बलरामको जन्मदिन हो, जसको अस्त्र हल (हलो) हो। आमाहरू सन्तानका लागि व्रत बस्छन् र हलोले जोतेर उब्जाएको केही पनि खाँदैनन् — प्रायः पसही चामल र भैंसीको दूध खान्छन्।",
    # EN: Hartalika Teej, Bhadrapada Shukla Tritiya, honours Parvati's penance to win Shiva. Women
    #     keep a nirjala fast, make clay images of Shiva and Parvati, worship them (morning puja in
    #     Pratahkala is preferred), keep vigil at night and break the fast next morning.
    "hartalika-teej": "हरितालिका तीज, भाद्र शुक्ल तृतीया, मा शिवलाई पाउन पार्वतीले गरेको तपस्याको सम्मान गरिन्छ। महिलाहरू निर्जल व्रत बस्छन्, माटोका शिव–पार्वती बनाएर पूजा गर्छन् (प्रातःकालको बिहानको पूजा उत्तम मानिन्छ), रात जागरण बस्छन् र भोलिपल्ट बिहान व्रत खोल्छन्।",
    # EN: Rishi Panchami, Bhadrapada Shukla Panchami, honours the Saptarishis, the seven sages.
    #     Women in particular bathe, fast and worship the sages at midday (Madhyahna), seeking
    #     purification from faults committed unknowingly.
    "rishi-panchami": "ऋषि पञ्चमी, भाद्र शुक्ल पञ्चमी, मा सप्तर्षिहरू, सात ऋषिहरूको सम्मान गरिन्छ। विशेषगरी महिलाहरू स्नान गर्छन्, व्रत बस्छन् र अनजानमा भएका त्रुटिबाट शुद्धि खोज्दै मध्याह्नमा ऋषिहरूको पूजा गर्छन्।",
    # EN: Anant Chaturdashi, Bhadrapada Shukla Chaturdashi, is the worship of Lord Vishnu as Anant.
    #     A sacred thread with fourteen knots (the anant sutra) is tied on the arm after puja; it is
    #     also the day Ganesh idols are immersed (Ganesh Visarjan).
    "anant-chaturdashi": "अनन्त चतुर्दशी, भाद्र शुक्ल चतुर्दशी, मा भगवान विष्णुको अनन्त रूपमा पूजा गरिन्छ। पूजापछि चौध गाँठो भएको पवित्र धागो (अनन्त सूत्र) पाखुरामा बाँधिन्छ; यो गणेश मूर्ति विसर्जन (गणेश विसर्जन) गरिने दिन पनि हो।",
    # EN: Pitru Paksha, the fortnight of the ancestors, runs from Pratipada to Amavasya of the dark
    #     half of Ashwin (purnimanta). On the tithi of an ancestor's passing, families offer tarpan
    #     and shraddha - pinda, food for Brahmins, cows, crows and dogs - in the Kutup, Rohina or
    #     Aparahna time.
    "pitru-paksha": "पितृ पक्ष, पितृहरूको पक्ष, आश्विन (पूर्णिमान्त) को कृष्ण पक्षको प्रतिपदादेखि औंसीसम्म चल्छ। पितृको निधन भएको तिथिमा परिवारले कुतुप, रौहिण वा अपराह्न समयमा तर्पण र श्राद्ध — पिण्ड, ब्राह्मण, गाई, काग र कुकुरलाई खाना — अर्पण गर्छन्।",
    # EN: Sarva Pitru Amavasya (Mahalaya Amavasya) closes Pitru Paksha. Shraddha on this day reaches
    #     all ancestors, including those whose tithi is not known; it is done in the Kutup, Rohina
    #     or Aparahna time.
    "sarva-pitru-amavasya": "सर्वपितृ औंसी (महालय औंसी) ले पितृ पक्ष समाप्त गर्छ। यस दिनको श्राद्ध तिथि थाहा नभएकाहरू सहित सबै पितृसम्म पुग्छ; यो कुतुप, रौहिण वा अपराह्न समयमा गरिन्छ।",
    # EN: Narak Chaturdashi (Roop Chaudas), Kartika Krishna Chaturdashi (purnimanta), remembers
    #     Krishna's victory over Narakasura. Before sunrise, while the Moon is up, people take an
    #     oil bath with ubtan (Abhyang snan), and a lamp for Yama is lit in the evening.
    "narak-chaturdashi": "नरक चतुर्दशी (रूप चौदस), कार्तिक कृष्ण चतुर्दशी (पूर्णिमान्त), ले कृष्णको नरकासुरमाथिको विजय सम्झाउँछ। सूर्योदयअघि, चन्द्रमा आकाशमै हुँदा, उबटनसहित तेल स्नान (अभ्यङ्ग स्नान) गरिन्छ, र साँझ यमका लागि दीप बालिन्छ।",
    # EN: Tulsi Vivah, on Kartika Shukla Dwadashi, is the ceremonial wedding of the tulsi plant (as
    #     Vrinda) to Lord Vishnu as Shaligram. Families decorate the tulsi like a bride and perform
    #     the rites of a wedding; the Hindu wedding season begins after it.
    "tulsi-vivah": "तुलसी विवाह, कार्तिक शुक्ल द्वादशीमा, तुलसीको बिरुवा (वृन्दाका रूपमा) र शालिग्रामका रूपमा भगवान विष्णुको औपचारिक विवाह हो। परिवारहरूले तुलसीलाई दुलहीझैँ सजाउँछन् र विवाहका विधि गर्छन्; यसपछि हिन्दू विवाहको लगन सुरु हुन्छ।",
    # EN: Kartik Purnima ends the holy month of Kartika. It is a great day for bathing in the Ganga
    #     or a holy river and giving in charity, and also Guru Nanak Jayanti and Tripuri Purnima,
    #     when Shiva destroyed Tripurasura.
    "kartik-purnima": "कार्तिक पूर्णिमाले पवित्र कार्तिक महिना समाप्त गर्छ। यो गङ्गा वा पवित्र नदीमा स्नान र दानको महान् दिन हो, र गुरु नानक जयन्ती तथा त्रिपुरी पूर्णिमा पनि हो, जब शिवले त्रिपुरासुरको संहार गरे।",
    # EN: Dev Deepawali, the 'Diwali of the gods', is celebrated on Kartik Purnima evening, above
    #     all on the ghats of Varanasi, which are lit with lakhs of diyas. It marks Shiva's victory
    #     over Tripurasura; lamps are offered to the Ganga in Pradosh kaal.
    "dev-deepawali": "देव दीपावली, 'देवताहरूको दीपावली', कार्तिक पूर्णिमाको साँझ मनाइन्छ, विशेषगरी वाराणसीका घाटमा, जहाँ लाखौँ दियो बालिन्छन्। यो शिवको त्रिपुरासुरमाथिको विजयको उत्सव हो; प्रदोष कालमा गङ्गालाई दीप अर्पण गरिन्छ।",
}

# app/vrat_text.py NOTES["ne"] — tradition notes on dates that differ between almanacs (key = festival slug)  [11]
VRAT_NOTES = {
    # EN: Dates follow Drik Panchang. When Bhadra covers the whole Purnima night and Purnima lasts
    #     most of the next day, Drik moves Holika Dahan to the next evening's Pradosh (as in 2026, 3
    #     March); some almanacs instead give a time late on the first night, after Bhadra ends.
    "holika-dahan": "मिति दृक पञ्चाङ्गअनुसार हो। जब भद्राले पूरै पूर्णिमाको रात ढाक्छ र पूर्णिमा भोलिपल्टको अधिकांश समयसम्म रहन्छ, दृकले होलिका दहन भोलिपल्ट साँझको प्रदोषमा सार्छ (जस्तै 2026 को 3 मार्चमा); केही पञ्चाङ्गले भने पहिलो रात भद्रा सकिएपछि ढिलो समय दिन्छन्।",
    # EN: Dates follow Drik Panchang's Smarta (default) reckoning, with Rohini nakshatra at midnight
    #     preferred. Vaishnava/ISKCON communities sometimes keep Janmashtami a day later.
    "janmashtami": "मिति दृक पञ्चाङ्गको स्मार्त (सामान्य) गणनाअनुसार हो, जसमा मध्यरातमा रोहिणी नक्षत्र हुनुलाई प्राथमिकता दिइन्छ। वैष्णव/इस्कोन समुदायले कहिलेकाहीँ जन्माष्टमी एक दिन पछि मनाउँछन्।",
    # EN: This is the Smarta (householder) date. Where Ekadashi spans two days, Vaishnavas may fast
    #     on the second day.
    "devuthani-ekadashi": "यो स्मार्त (गृहस्थ) मिति हो। जहाँ एकादशी दुई दिन पर्छ, वैष्णवहरूले दोस्रो दिन व्रत बस्न सक्छन्।",
    # EN: Dates follow Drik Panchang (Dashami in Aparahna, Shravana nakshatra preferred). In Bengal
    #     and some almanacs Vijayadashami can fall a day later.
    "dussehra": "मिति दृक पञ्चाङ्गअनुसार हो (अपराह्नमा दशमी, श्रवण नक्षत्रलाई प्राथमिकता)। बङ्गाल र केही पञ्चाङ्गमा विजयादशमी एक दिन पछि पर्न सक्छ।",
    # EN: Dates follow Drik Panchang (Ashtami at midday; when it is at sunrise only briefly, as in
    #     2023, the previous day). Nahay-khay is the day before and parana the next morning;
    #     regional panchangs (e.g. Mithila) can differ by a day.
    "jivitputrika": "मिति दृक पञ्चाङ्गअनुसार हो (मध्याह्नमा अष्टमी; जब सूर्योदयमा थोरै समय मात्र हुन्छ, जस्तै 2023 मा, अघिल्लो दिन)। नहाय–खाय अघिल्लो दिन र पारण भोलिपल्ट बिहान हुन्छ; क्षेत्रीय पञ्चाङ्ग (जस्तै मिथिला) मा एक दिन फरक पर्न सक्छ।",
    # EN: Two traditions: North India keeps Vat Savitri on Jyeshtha Amavasya (this date);
    #     Maharashtra, Gujarat and the south keep it as Vat Purnima fifteen days later.
    "vat-savitri": "दुई परम्परा छन्: उत्तर भारतमा वट सावित्री जेष्ठ औंसीमा (यही मिति) मनाइन्छ; महाराष्ट्र, गुजरात र दक्षिणमा यो पन्ध्र दिनपछि वट पूर्णिमाका रूपमा मनाइन्छ।",
    # EN: Two traditions: this is the Purnima (amanta) date of Maharashtra, Gujarat and the south;
    #     North India keeps Vat Savitri on the Amavasya fifteen days earlier.
    "vat-purnima": "दुई परम्परा छन्: यो महाराष्ट्र, गुजरात र दक्षिणको पूर्णिमा (अमान्त) मिति हो; उत्तर भारतमा वट सावित्री पन्ध्र दिन अघि औंसीमा मनाइन्छ।",
    # EN: When Jyeshtha is doubled (an adhika month, as in 2026), Drik Panchang keeps Ganga Dussehra
    #     in the adhika Jyeshtha; some almanacs give the nija Jyeshtha date a month later.
    "ganga-dussehra": "जब जेष्ठ दोहोरिन्छ (अधिक मास, जस्तै 2026 मा), दृक पञ्चाङ्गले गङ्गा दसहरा अधिक जेष्ठमा राख्छ; केही पञ्चाङ्गले निज जेष्ठको मिति एक महिना पछि दिन्छन्।",
    # EN: Drik Panchang counts Pitru Paksha from the Pratipada shraddha; Purnima shraddha is on the
    #     day before, and many calendars start the fortnight there.
    "pitru-paksha": "दृक पञ्चाङ्गले पितृ पक्ष प्रतिपदा श्राद्धबाट गणना गर्छ; पूर्णिमा श्राद्ध अघिल्लो दिन पर्छ, र धेरै पात्रोले पक्ष त्यहीँबाट सुरु गर्छन्।",
    # EN: Drik Panchang publishes Dev Deepawali for Varanasi; the date here uses the same rule
    #     (Purnima in Pradosh), and the Pradosh kaal shown is New Delhi's.
    "dev-deepawali": "दृक पञ्चाङ्गले देव दीपावली वाराणसीका लागि प्रकाशित गर्छ; यहाँको मिति पनि उही नियम (प्रदोषमा पूर्णिमा) अनुसार हो, र देखाइएको प्रदोष काल नयाँ दिल्लीको हो।",
    # EN: This is the snan-daan day (Purnima at sunrise). When Purnima begins the previous
    #     afternoon, the Purnima fast and Dev Deepawali can fall a day earlier.
    "kartik-purnima": "यो स्नान–दानको दिन हो (सूर्योदयमा पूर्णिमा)। जब पूर्णिमा अघिल्लो दिन अपराह्नमै सुरु हुन्छ, पूर्णिमा व्रत र देव दीपावली एक दिन अघि पर्न सक्छन्।",
}

# app/vrat_text.py RULES["ne"] — 'how the date is fixed' sentences: head {month}, tithi {paksha} {tithi}, rule.<kind>, key.<observance>  [16]
VRAT_RULES = {
    # EN: {month} (amanta)
    # keep: {month}
    "head": "{month} (अमान्त) ",
    # EN: {paksha} {tithi}:
    # keep: {paksha} {tithi}
    "tithi": "{paksha} {tithi}: ",
    # EN: tithi prevailing at sunrise
    "rule.udaya": "सूर्योदयमा रहेको तिथि",
    # EN: tithi prevailing in Pratahkala (first fifth of the day)
    "rule.pratah": "प्रातःकाल (दिनको पहिलो पाँचौँ भाग) मा रहेको तिथि",
    # EN: tithi prevailing in the forenoon (purvahna)
    "rule.purvahna": "पूर्वाह्न (मध्याह्नअघि) मा रहेको तिथि",
    # EN: tithi prevailing at Madhyahna (midday fifth of the day)
    "rule.madhyahna": "मध्याह्न (दिनको बीचको पाँचौँ भाग) मा रहेको तिथि",
    # EN: tithi prevailing at Aparahna (fourth fifth of the day)
    "rule.aparahna": "अपराह्न (दिनको चौथो पाँचौँ भाग) मा रहेको तिथि",
    # EN: first day on which the tithi is present between sunrise and sunset
    "rule.dina": "सूर्योदय र सूर्यास्तबीच तिथि रहेको पहिलो दिन",
    # EN: tithi prevailing at sunset
    "rule.sayahna": "सूर्यास्तमा रहेको तिथि",
    # EN: tithi prevailing in Pradosh kaal (after sunset)
    "rule.pradosh": "प्रदोष काल (सूर्यास्तपछि) मा रहेको तिथि",
    # EN: tithi prevailing at Nishita kaal (midnight)
    "rule.nishita": "निशीथ काल (मध्यरात) मा रहेको तिथि",
    # EN: tithi prevailing at moonrise
    "rule.moonrise": "चन्द्रोदयमा रहेको तिथि",
    # EN: Smarta: Ekadashi prevailing at sunrise (second day if at two sunrises); parana next day
    #     after sunrise and after Hari Vasara, within Pratahkala and before Dwadashi ends
    "key.ekadashi": "स्मार्त: सूर्योदयमा रहेको एकादशी (दुई सूर्योदयमा परे दोस्रो दिन); पारण भोलिपल्ट सूर्योदयपछि र हरि वासरपछि, प्रातःकालभित्र र द्वादशी सकिनुअघि",
    # EN: the Sun's entry into sidereal Makara (Capricorn); punya kaal follows it until sunset
    "key.makar_sankranti": "सूर्यको निरयन मकर राशिमा प्रवेश; पुण्य काल यसपछि सूर्यास्तसम्म रहन्छ",
    # EN: the day before Makar Sankranti
    "key.lohri": "मकर सङ्क्रान्तिको अघिल्लो दिन",
    # EN: the day after Holika Dahan
    "key.holi": "होलिका दहनको भोलिपल्ट",
}

# ----------------------------------------------------------------------------
# nakshatra /nakshatra /rashi /naam-se-kundali-milan
# ----------------------------------------------------------------------------

# app/nakshatra_page_text.py TEXT["ne"] — page text of /nakshatra /rashi (nakshatra_pages.py)  [88]
NAKSHATRA_PAGE_TEXT = {
    # EN: Get your free kundali — find your exact birth nakshatra and Moon sign
    "kundali_cta": "निःशुल्क कुण्डली बनाउनुहोस् — आफ्नो ठ्याक्कै जन्म नक्षत्र र चन्द्र राशि पत्ता लगाउनुहोस्",
    # EN: More free tools
    "more.heading": "थप निःशुल्क सेवाहरू",
    # EN: All 27 nakshatras
    "more.naks": "सबै 27 नक्षत्र",
    # EN: All 12 rashis
    "more.rashis": "सबै 12 राशि",
    # EN: Naam se Kundali Milan
    "more.milan": "नामबाट कुण्डली मिलान",
    # EN: Kundali Milan (36 guna)
    "more.kundali_milan": "कुण्डली मिलान (36 गुण)",
    # EN: Today's Rashifal
    "more.rashifal": "आजको राशिफल",
    # EN: Today's Panchang
    "more.panchang": "आजको पञ्चाङ्ग",
    # EN: All 27 nakshatras
    "list.naks": "सबै 27 नक्षत्र",
    # EN: All 12 rashis
    "list.rashis": "सबै 12 राशि",
    # EN: {name} ({english})
    # keep: {name}
    "sign": "{name}",
    # EN: {name} · {english}
    # keep: {name}
    "sign.pill": "{name}",
    # EN: <strong>Today the Moon is in {name} (at sunrise in New Delhi).</strong>
    # keep: {name}
    "today.same": "<strong>आज चन्द्रमा {name} मा छन् (नयाँ दिल्लीमा सूर्योदयको समयमा)।</strong>",
    # EN: Today's nakshatra is <a href="{href}"><strong>{name}</strong></a> (at sunrise in New
    #     Delhi).
    # keep: {href} {name}
    "today.other": "आजको नक्षत्र <a href=\"{href}\"><strong>{name}</strong></a> हो (नयाँ दिल्लीमा सूर्योदयको समयमा)।",
    # EN: Its end time, the tithi and Rahu Kaal are on <a href="{pan}">today's Panchang</a>.
    # keep: {pan}
    "today.tail": " यसको समाप्ति समय, तिथि र राहुकाल <a href=\"{pan}\">आजको पञ्चाङ्ग</a>मा हेर्नुहोस्।",
    # EN: Nakshatras
    "crumb.naks": "नक्षत्र",
    # EN: Rashis
    "crumb.rashis": "राशि",
    # EN: Nakshatra not found
    "nf.nak": "नक्षत्र फेला परेन",
    # EN: Rashi not found
    "nf.rashi": "राशि फेला परेन",
    # EN: Nature and traits
    "trait_head": "स्वभाव र विशेषता",
    # EN: male
    "gender.male": "पुरुष",
    # EN: female
    "gender.female": "स्त्री",
    # EN: Fire
    "element.Fire": "अग्नि",
    # EN: Earth
    "element.Earth": "पृथ्वी",
    # EN: Air
    "element.Air": "वायु",
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
    "nak.title": "{name} नक्षत्र — देवता, स्वामी, गण, योनि, नाडी र नामाक्षर | {brand}",
    # EN: {name} nakshatra ({name_hi}): {span}, ruled by {lord}, deity {deity_short}, {gana} gana,
    #     {nadi} nadi, {yoni} yoni. Name syllables {lat} and traits.
    # keep: {gana} {lord} {nadi} {name} {span} {yoni}
    # may also use: {name_en}
    "nak.desc": "{name} नक्षत्र: {span}, स्वामी {lord}, {gana} गण, {nadi} नाडी, {yoni} योनि। नामाक्षर र स्वभावका विशेषता।",
    # EN: <h1>{name} Nakshatra</h1>
    # keep: {name}
    "nak.h1": "<h1>{name} नक्षत्र</h1>",
    # EN: <p class="hi" lang="hi">{name_hi} नक्षत्र</p>
    # may also use: {name_en} {name}
    "nak.sub": "<p class=\"hi\" lang=\"ne\">{name} नक्षत्र</p>",
    # EN: <p class="note">These are traditional tendencies, not verdicts. Your full kundali —
    #     ascendant, planets and dasha — gives the personal picture.</p>
    "nak.trait_note": "<p class=\"note\">यी परम्परागत प्रवृत्ति मात्र हुन्, निर्णय होइनन्। लग्न, ग्रह र दशासहितको तपाईंको पूर्ण कुण्डलीले व्यक्तिगत तस्बिर दिन्छ।</p>",
    # EN: Number
    "f.number": "क्रम",
    # EN: {n} of 27
    # keep: {n}
    "f.number_v": "27 मध्ये {n}",
    # EN: Span (sidereal)
    "f.span": "विस्तार (निरयण)",
    # EN: Rashi
    "f.rashi": "राशि",
    # EN: Ruling planet (Vimshottari lord)
    "f.lord": "स्वामी ग्रह (विंशोत्तरी स्वामी)",
    # EN: {lord} <small>{years}-year mahadasha</small>
    # keep: {lord} {years}
    "f.lord_v": "{lord} <small>{years} वर्षको महादशा</small>",
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
    "f.yoni": "योनि (जनावर)",
    # EN: Nadi
    "f.nadi": "नाडी",
    # EN: Varna (from its rashi, as used in Guna Milan)
    "f.varna": "वर्ण (राशिबाट, गुण मिलानमा प्रयोग हुने)",
    # EN: Name syllables (namakshar)
    "f.syl": "नामाक्षर",
    # EN: <span class="syl" lang="hi">{syl}</span> <small>{lat}</small>
    # keep: {syl}
    "f.syl_v": "<span class=\"syl\" lang=\"ne\">{syl}</span>",
    # EN: The four padas and their name syllables
    "pada.title": "चार चरण र तिनका नामाक्षर",
    # EN: <tr><th>Pada</th><th>Span</th><th>Rashi</th><th>Name syllable</th></tr>
    "pada.head": "<tr><th>चरण</th><th>विस्तार</th><th>राशि</th><th>नामाक्षर</th></tr>",
    # EN: <p class="note">Traditionally a child's name begins with the syllable of the pada the Moon
    #     occupied at birth (namakshar). Syllables follow the 108-pada Swar Siddhanta list (the
    #     Avakahada Chakra) as published by Drik Panchang.</p>
    "pada.note": "<p class=\"note\">परम्परा अनुसार बच्चाको नाम जन्मका बेला चन्द्रमा रहेको चरणको अक्षरबाट सुरु गरिन्छ (नामाक्षर)। अक्षरहरू द्रिक पञ्चाङ्गले प्रकाशित गरेको 108 चरणको स्वर सिद्धान्त सूची (अवकहडा चक्र) अनुसार हुन्।</p>",
    # EN: Related
    "rel.heading": "सम्बन्धित",
    # EN: Today's {name} Rashifal
    # keep: {name}
    "rel.rashifal": "आजको {name} राशिफल",
    # EN: The 27 Nakshatras — Lords, Deities, Gana & Name Syllables | {brand}
    # keep: {brand}
    "ni.title": "27 नक्षत्र — स्वामी, देवता, गण र नामाक्षर | {brand}",
    # EN: All 27 nakshatras from Ashwini to Revati: span, rashi, ruling planet, deity, gana, yoni,
    #     nadi and the name syllables of all four padas — consistent with our Kundali Milan tables.
    "ni.desc": "अश्विनीदेखि रेवतीसम्म सबै 27 नक्षत्र: विस्तार, राशि, स्वामी ग्रह, देवता, गण, योनि, नाडी र चारै चरणका नामाक्षर — हाम्रा कुण्डली मिलान तालिकासँग मिल्दो।",
    # EN: <h1>The 27 Nakshatras</h1>
    "ni.h1": "<h1>27 नक्षत्र</h1>",
    # EN: <p class="hi" lang="hi">27 नक्षत्र</p>
    "ni.sub": "<p class=\"hi\" lang=\"ne\">27 नक्षत्र</p>",
    # EN: <p>Vedic astrology divides the zodiac into 27 nakshatras (lunar mansions) of 13°20′ each,
    #     and each nakshatra into four padas of 3°20′. The 108 padas fall exactly nine to a sign
    #     across the 12 rashis. Your birth nakshatra is the one the Moon occupied when you were
    #     born: it starts your Vimshottari dasha and drives the Tara, Yoni, Gana and Nadi kootas of
    #     Kundali Milan.</p>
    "ni.intro": "<p>वैदिक ज्योतिषले राशिचक्रलाई 13°20′ का 27 नक्षत्रमा बाँड्छ, र प्रत्येक नक्षत्रलाई 3°20′ का चार चरणमा। 108 चरण 12 राशिमा ठ्याक्कै नौ-नौवटा गरी पर्छन्। तपाईंको जन्म नक्षत्र भनेको तपाईं जन्मँदा चन्द्रमा रहेको नक्षत्र हो: त्यसैबाट तपाईंको विंशोत्तरी दशा सुरु हुन्छ, र कुण्डली मिलानका तारा, योनि, गण र नाडी कूट निर्धारण हुन्छन्।</p>",
    # EN: <tr><th>#</th><th>Nakshatra</th><th>Rashi</th><th>Lord</th><th>Gana</th><th>Name
    #     syllables</th></tr>
    "ni.head": "<tr><th>#</th><th>नक्षत्र</th><th>राशि</th><th>स्वामी</th><th>गण</th><th>नामाक्षर</th></tr>",
    # EN: {name} Rashi ({english}) — Lord, Element, Nakshatras & Name Letters | {brand}
    # keep: {brand} {name}
    # may also use: {english}
    "rs.title": "{name} राशि ({english}) — स्वामी, तत्त्व, नक्षत्र र नामाक्षर | {brand}",
    # EN: {name} rashi ({english} Moon sign, {name_hi}): ruled by {lord}, {element_lower} element,
    #     {quality_lower} quality. Its 9 nakshatra padas, name syllables ({lat}) and traits.
    # keep: {lord} {name}
    # may also use: {element_lower} {element} {english} {name_en} {quality_lower} {quality}
    "rs.desc": "{name} राशि ({english} चन्द्र राशि): स्वामी {lord}, {element_lower} तत्त्व, {quality_lower} स्वभाव। यसका 9 नक्षत्र चरण, नामाक्षर र विशेषता।",
    # EN: <h1>{name} Rashi — {english} Moon Sign</h1>
    # keep: {name}
    # may also use: {english}
    "rs.h1": "<h1>{name} राशि — {english} चन्द्र राशि</h1>",
    # EN: <p class="hi" lang="hi">{name_hi} राशि</p>
    # may also use: {english} {name_en} {name}
    "rs.sub": "<p class=\"hi\" lang=\"ne\">{name} राशि</p>",
    # EN: Read today's {name} Rashifal
    # keep: {name}
    "rs.today": "आजको {name} राशिफल पढ्नुहोस्",
    # EN: <p class="note">In Vedic astrology "rashi" usually means the Moon sign — the sign the Moon
    #     occupied at birth, in the sidereal zodiac. It is often different from a Western sun
    #     sign.</p>
    "rs.note": "<p class=\"note\">वैदिक ज्योतिषमा “राशि” भन्नाले प्रायः चन्द्र राशि बुझिन्छ — जन्मका बेला निरयण राशिचक्रमा चन्द्रमा रहेको राशि। यो पश्चिमी सूर्य राशिभन्दा प्रायः फरक हुन्छ।</p>",
    # EN: Number
    "r.number": "क्रम",
    # EN: {n} of 12
    # keep: {n}
    "r.number_v": "12 मध्ये {n}",
    # EN: Span (sidereal zodiac)
    "r.span": "विस्तार (निरयण राशिचक्र)",
    # EN: Sign lord
    "r.lord": "राशि स्वामी",
    # EN: Element
    "r.element": "तत्त्व",
    # EN: Quality
    "r.quality": "स्वभाव",
    # EN: Varna (used in Guna Milan)
    "r.varna": "वर्ण (गुण मिलानमा प्रयोग हुने)",
    # EN: Nakshatras
    "r.naks": "नक्षत्र",
    # EN: Name syllables (namakshar)
    "r.syl": "नामाक्षर",
    # EN: <span class="syl" lang="hi">{syl}</span>
    # keep: {syl}
    "r.syl_v": "<span class=\"syl\" lang=\"ne\">{syl}</span>",
    # EN: The nine nakshatra padas in this sign
    "rp.title": "यस राशिका नौ नक्षत्र चरण",
    # EN: <tr><th>Nakshatra</th><th>Pada</th><th>Degrees in sign</th><th>Syllable</th></tr>
    "rp.head": "<tr><th>नक्षत्र</th><th>चरण</th><th>राशिमा अंश</th><th>अक्षर</th></tr>",
    # EN: The 12 Rashis — Lords, Elements, Nakshatras & Name Letters | {brand}
    # keep: {brand}
    "ri.title": "12 राशि — स्वामी, तत्त्व, नक्षत्र र नामाक्षर | {brand}",
    # EN: All 12 rashis (Vedic Moon signs) from Mesh to Meen: sign lord, element, quality, the nine
    #     nakshatra padas in each and their name syllables (namakshar).
    "ri.desc": "मेषदेखि मीनसम्म सबै 12 राशि (वैदिक चन्द्र राशि): राशि स्वामी, तत्त्व, स्वभाव, प्रत्येकका नौ नक्षत्र चरण र तिनका नामाक्षर।",
    # EN: <h1>The 12 Rashis (Moon Signs)</h1>
    "ri.h1": "<h1>12 राशि (चन्द्र राशि)</h1>",
    # EN: <p class="hi" lang="hi">12 राशियाँ</p>
    "ri.sub": "<p class=\"hi\" lang=\"ne\">12 राशि</p>",
    # EN: <p>Each rashi spans 30° of the sidereal zodiac and holds exactly nine nakshatra padas.
    #     Your rashi is your Moon sign — the sign the Moon occupied at birth — and it is what
    #     rashifal, Sade Sati and Kundali Milan are read from.</p>
    "ri.intro": "<p>प्रत्येक राशि निरयण राशिचक्रको 30° फैलिएको हुन्छ र त्यसमा ठ्याक्कै नौ नक्षत्र चरण पर्छन्। तपाईंको राशि भनेको तपाईंको चन्द्र राशि हो — जन्मका बेला चन्द्रमा रहेको राशि — र राशिफल, साढेसाती तथा कुण्डली मिलान यसैबाट हेरिन्छ।</p>",
    # EN: <tr><th>Rashi</th><th>Lord</th><th>Element</th><th>Nakshatras</th><th>Name
    #     syllables</th></tr>
    "ri.head": "<tr><th>राशि</th><th>स्वामी</th><th>तत्त्व</th><th>नक्षत्र</th><th>नामाक्षर</th></tr>",
    # EN: {name} <small>{english}</small>
    # keep: {name}
    # may also use: {english}
    "ri.name": "{name} <small>{english}</small>",
    # EN: Vata
    "humour.Vata": "वात",
    # EN: Pitta
    "humour.Pitta": "पित्त",
    # EN: Kapha
    "humour.Kapha": "कफ",
}

# app/nakshatra_text.py NAKSHATRA_TRAITS["ne"] — character paragraph of each of the 27 nakshatras (key = slug)  [27]
NAKSHATRA_TRAITS = {
    # EN: Ashwini is the first nakshatra, ruled by the Ashwini Kumaras, the twin healers of the
    #     gods, and symbolised by a horse's head. People with the Moon here are often quick,
    #     energetic and eager to begin things — the first to help, the first to try something new.
    #     Tradition links Ashwini with healing, speed and fresh starts, so many feel drawn to
    #     medicine, sport, travel or any work that needs swift, practical action. The gift of this
    #     nakshatra is initiative and a youthful optimism; the lesson is patience, finishing what
    #     was started with the same enthusiasm with which it began.
    "ashwini": "अश्विनी पहिलो नक्षत्र हो। यसका स्वामी देवताहरूका जुम्ल्याहा वैद्य अश्विनीकुमार हुन् र प्रतीक घोडाको टाउको हो। यहाँ चन्द्रमा भएका व्यक्ति प्रायः फुर्तिला, ऊर्जावान र नयाँ काम सुरु गर्न उत्सुक हुन्छन् — मद्दत गर्न पहिलो, नयाँ कुरा प्रयास गर्न पनि पहिलो। परम्परामा अश्विनीलाई उपचार, गति र नयाँ सुरुवातसँग जोडिन्छ, त्यसैले धेरैलाई चिकित्सा, खेलकुद, यात्रा वा तुरुन्त व्यावहारिक कदम चाल्नुपर्ने काम मन पर्छ। यस नक्षत्रको वरदान पहल गर्ने क्षमता र तरुण आशावाद हो; सिक्नुपर्ने पाठ धैर्य हो — सुरु गरेको काम सुरुमा जत्तिकै उत्साहले पूरा गर्नु।",
    # EN: Bharani is ruled by Yama, the lord of dharma, and its symbol is the yoni, the womb that
    #     carries and protects new life. People with the Moon here often have strong will, deep
    #     feelings and a serious sense of responsibility. They tend to carry their commitments
    #     through to the end and are not easily swayed. Tradition sees Bharani as the nakshatra of
    #     bearing and nurturing — holding something until it is ready to be born — so creativity,
    #     family, art and work that asks for endurance suit it well. Its strength is steadfastness;
    #     its lesson is balancing desire with restraint and kindness.
    "bharani": "भरणीका स्वामी धर्मका अधिपति यम हुन् र यसको प्रतीक योनि हो — नयाँ जीवनलाई धारण र रक्षा गर्ने गर्भ। यहाँ चन्द्रमा भएका व्यक्तिमा प्रायः दृढ इच्छाशक्ति, गहिरो भावना र जिम्मेवारीको गम्भीर बोध हुन्छ। उनीहरू आफ्नो वचन अन्तसम्म निभाउँछन् र सजिलै डगमगाउँदैनन्। परम्पराले भरणीलाई धारण र पालनपोषणको नक्षत्र मान्छ — कुनै कुरा जन्मन तयार नभएसम्म सम्हालेर राख्ने — त्यसैले सिर्जना, परिवार, कला र सहनशीलता चाहिने काम यसलाई सुहाउँछ। यसको शक्ति अटलता हो; सिक्नुपर्ने पाठ इच्छालाई संयम र दयासँग सन्तुलनमा राख्नु हो।",
    # EN: Krittika is ruled by Agni, the sacred fire, and symbolised by a razor or a flame. Fire
    #     purifies and cuts through confusion, and people with the Moon here are often direct,
    #     principled and sharp in judgement. They can be protective of those they love and are
    #     willing to say what needs to be said. Krittika is also the nakshatra of the six mothers
    #     who nursed Kartikeya, so beneath the sharpness there is real warmth and care. Teaching,
    #     cooking, leadership and any work that needs clarity suit it. Its lesson is to let the fire
    #     warm and guide rather than burn.
    "krittika": "कृत्तिकाका स्वामी पवित्र अग्नि हुन् र प्रतीक छुरा वा ज्वाला हो। अग्निले शुद्ध गर्छ र भ्रमलाई काट्छ; यहाँ चन्द्रमा भएका व्यक्ति प्रायः स्पष्टवक्ता, सिद्धान्तनिष्ठ र तीक्ष्ण निर्णयका हुन्छन्। आफ्ना प्रियजनको रक्षा गर्न तत्पर रहन्छन् र भन्नैपर्ने कुरा भन्न हिचकिचाउँदैनन्। कृत्तिका कार्तिकेयलाई दूध खुवाउने छ जना आमाहरूको नक्षत्र पनि हो, त्यसैले तीक्ष्णताको तल साँचो न्यानोपन र माया हुन्छ। शिक्षण, खाना पकाउने काम, नेतृत्व र स्पष्टता चाहिने कुनै पनि काम यसलाई सुहाउँछ। सिक्नुपर्ने पाठ अग्निले जलाउनुभन्दा न्यानो दिने र बाटो देखाउने बनोस् भन्ने हो।",
    # EN: Rohini is ruled by Brahma, the creator, and symbolised by a chariot or ox-cart. It is said
    #     to be the Moon's favourite nakshatra, and people with the Moon here are often warm,
    #     attractive, artistic and fond of comfort and beauty. They have a gift for making things
    #     grow — gardens, homes, businesses and relationships. Tradition associates Rohini with
    #     fertility, abundance and steady progress, so agriculture, the arts, design, food and
    #     hospitality suit it well. Its nature is gentle and settled; its lesson is to enjoy what is
    #     beautiful without holding on too tightly to it.
    "rohini": "रोहिणीका स्वामी सृष्टिकर्ता ब्रह्मा हुन् र प्रतीक रथ वा गोरुगाडा हो। यो चन्द्रमाको सबैभन्दा प्रिय नक्षत्र मानिन्छ, र यहाँ चन्द्रमा भएका व्यक्ति प्रायः न्यानो स्वभावका, आकर्षक, कलाप्रेमी र सुख-सुविधा तथा सौन्दर्यका सौखिन हुन्छन्। बगैँचा, घर, व्यापार र सम्बन्ध — जे कुरा हुर्काउन पनि उनीहरूमा विशेष क्षमता हुन्छ। परम्पराले रोहिणीलाई उर्वरता, समृद्धि र स्थिर प्रगतिसँग जोड्छ, त्यसैले कृषि, कला, डिजाइन, खानपान र आतिथ्य यसलाई सुहाउँछ। स्वभाव कोमल र स्थिर हुन्छ; सिक्नुपर्ने पाठ सुन्दर कुरालाई अति कसेर नसमाती आनन्द लिनु हो।",
    # EN: Mrigashira is ruled by Soma, the Moon, and its symbol is a deer's head — the deer that is
    #     always alert, curious and searching. People with the Moon here are often gentle,
    #     inquisitive and fond of learning, travel and conversation. They enjoy exploring ideas and
    #     places and rarely stop asking questions. Tradition sees Mrigashira as the seeker's
    #     nakshatra, which suits research, writing, teaching, trade and any work that rewards
    #     curiosity. Its charm is a light, friendly mind; its lesson is to settle on what has been
    #     found, so that the search leads somewhere rather than becoming restlessness.
    "mrigashira": "मृगशिराका स्वामी चन्द्रमा (सोम) हुन् र प्रतीक मृगको टाउको हो — सधैँ सतर्क, जिज्ञासु र खोजी गरिरहने मृग। यहाँ चन्द्रमा भएका व्यक्ति प्रायः कोमल, जिज्ञासु र अध्ययन, यात्रा तथा कुराकानी मन पराउने हुन्छन्। नयाँ विचार र ठाउँ खोज्न रमाउँछन् र प्रश्न सोध्न कहिल्यै रोकिँदैनन्। परम्पराले मृगशिरालाई खोजीकर्ताको नक्षत्र मान्छ, त्यसैले अनुसन्धान, लेखन, शिक्षण, व्यापार र जिज्ञासाको मूल्य हुने कुनै पनि काम यसलाई सुहाउँछ। यसको आकर्षण हल्का र मिलनसार मन हो; सिक्नुपर्ने पाठ फेला परेको कुरामा टिक्नु हो, ताकि खोज कतै पुगोस्, छटपटीमा नबदलियोस्।",
    # EN: Ardra is ruled by Rudra, the storm form of Shiva, and symbolised by a teardrop or a
    #     diamond. As a storm clears the air and brings rain, people with the Moon here often have a
    #     strong, searching intellect and the ability to see through things to the truth. They can
    #     feel deeply and are not afraid of change. Tradition links Ardra with renewal after
    #     difficulty, so research, technology, writing, counselling and problem-solving suit it
    #     well. Its gift is honesty and a sharp mind; its lesson is to let feelings pass like the
    #     rain, leaving the ground greener.
    "ardra": "आर्द्राका स्वामी शिवको प्रचण्ड रूप रुद्र हुन् र प्रतीक आँसुको थोपा वा हीरा हो। आँधीले हावा सफा गर्छ र वर्षा ल्याउँछ; त्यसैगरी यहाँ चन्द्रमा भएका व्यक्तिमा प्रायः तीव्र, खोजी गर्ने बुद्धि र कुराको तहसम्म पुगेर सत्य देख्ने क्षमता हुन्छ। उनीहरूले गहिरो अनुभूति गर्छन् र परिवर्तनसँग डराउँदैनन्। परम्पराले आर्द्रालाई कठिनाइपछिको नवीकरणसँग जोड्छ, त्यसैले अनुसन्धान, प्रविधि, लेखन, परामर्श र समस्या समाधान यसलाई सुहाउँछ। यसको वरदान इमानदारी र तीक्ष्ण मन हो; सिक्नुपर्ने पाठ भावनालाई वर्षाझैँ बग्न दिनु हो, जसले माटो अझ हरियो छोडोस्।",
    # EN: Punarvasu is ruled by Aditi, the boundless mother of the gods, and symbolised by a bow and
    #     quiver. Its name means "return of the light", and people with the Moon here are often
    #     optimistic, generous and able to begin again after any setback. They tend to be content
    #     with simple things, good-humoured and caring towards family and guests. Tradition sees
    #     Punarvasu as a nakshatra of renewal and homecoming, suited to teaching, counselling,
    #     writing, travel and caring work. Its blessing is a hopeful, forgiving heart; its lesson is
    #     to aim the arrow — to choose a direction and stay with it.
    "punarvasu": "पुनर्वसुकी स्वामिनी देवताहरूकी असीम माता अदिति हुन् र प्रतीक धनुष र तरकस हो। यसको नामको अर्थ “प्रकाशको पुनरागमन” हो, र यहाँ चन्द्रमा भएका व्यक्ति प्रायः आशावादी, उदार र जुनसुकै असफलतापछि फेरि सुरु गर्न सक्ने हुन्छन्। सादा कुरामै सन्तुष्ट, हँसिला र परिवार तथा पाहुनाप्रति स्नेही हुन्छन्। परम्पराले पुनर्वसुलाई नवीकरण र घर फर्कने नक्षत्र मान्छ; शिक्षण, परामर्श, लेखन, यात्रा र सेवामूलक काम यसलाई सुहाउँछ। यसको आशीर्वाद आशावान् र क्षमाशील हृदय हो; सिक्नुपर्ने पाठ तीर लक्ष्यमा ताक्नु हो — दिशा रोजेर त्यसमै अडिग रहनु।",
    # EN: Pushya is ruled by Brihaspati, the guru of the gods, and symbolised by a cow's udder or a
    #     lotus — images of nourishment. It is counted among the most auspicious nakshatras, and
    #     people with the Moon here are often caring, dependable, devoted and generous with their
    #     time. They like to support others, keep traditions and build something lasting. Tradition
    #     links Pushya with nourishment and wisdom, so teaching, counselling, food, social service,
    #     finance and spiritual work suit it well. Its gift is a steady, protective kindness; its
    #     lesson is to nourish oneself as faithfully as one nourishes others.
    "pushya": "पुष्यका स्वामी देवताहरूका गुरु बृहस्पति हुन् र प्रतीक गाईको थुन वा कमल हो — पोषणका प्रतीक। यो सबैभन्दा शुभ नक्षत्रमध्ये गनिन्छ, र यहाँ चन्द्रमा भएका व्यक्ति प्रायः स्नेही, भरपर्दा, समर्पित र आफ्नो समय दिन उदार हुन्छन्। अरूलाई सहयोग गर्न, परम्परा जोगाउन र दिगो केही बनाउन मन पराउँछन्। परम्पराले पुष्यलाई पोषण र ज्ञानसँग जोड्छ, त्यसैले शिक्षण, परामर्श, खाद्य, समाजसेवा, वित्त र आध्यात्मिक काम यसलाई सुहाउँछ। यसको वरदान स्थिर, रक्षक दयालुता हो; सिक्नुपर्ने पाठ अरूलाई जत्तिकै निष्ठाका साथ आफूलाई पनि पोषण गर्नु हो।",
    # EN: Ashlesha is ruled by the Nagas, the serpent deities, and symbolised by a coiled serpent —
    #     an image of kundalini, hidden energy and deep wisdom. People with the Moon here are often
    #     perceptive, intelligent and good at understanding what others leave unsaid. They can be
    #     persuasive and strategic, with a strong instinct for self-protection. Tradition links
    #     Ashlesha with insight and with the healing knowledge of herbs, so psychology, research,
    #     medicine, writing and negotiation suit it well. Its gift is penetrating understanding; its
    #     lesson is to use that insight to embrace and heal, the way the serpent's coil protects.
    "ashlesha": "आश्लेषाका स्वामी सर्प देवता नागहरू हुन् र प्रतीक बेरिएको सर्प हो — कुण्डलिनी, लुकेको ऊर्जा र गहिरो ज्ञानको प्रतिबिम्ब। यहाँ चन्द्रमा भएका व्यक्ति प्रायः सूक्ष्मदर्शी, बुद्धिमान र अरूले नभनेको कुरा बुझ्न माहिर हुन्छन्। उनीहरू मन जित्न सक्ने र रणनीतिक हुन्छन्, आत्मरक्षाको तीव्र सहज बोधसहित। परम्पराले आश्लेषालाई अन्तर्दृष्टि र जडीबुटीको उपचार ज्ञानसँग जोड्छ, त्यसैले मनोविज्ञान, अनुसन्धान, चिकित्सा, लेखन र वार्ता यसलाई सुहाउँछ। यसको वरदान भेदक समझ हो; सिक्नुपर्ने पाठ त्यो अन्तर्दृष्टिले अँगाल्न र निको पार्न — सर्पको कुण्डलीले जसरी रक्षा गर्छ।",
    # EN: Magha is ruled by the Pitris, the ancestors, and symbolised by a royal throne. People with
    #     the Moon here often carry a natural dignity, a respect for family and tradition, and a
    #     wish to live up to the name they were given. They can be generous leaders who take
    #     responsibility for their people. Tradition links Magha with lineage, honour and authority,
    #     so leadership, administration, history, law and work that preserves heritage suit it well.
    #     Its gift is nobility of heart; its lesson is to wear the crown lightly — to lead through
    #     service and to honour the ancestors through good deeds.
    "magha": "मघाका स्वामी पितृहरू (पुर्खा) हुन् र प्रतीक राजसिंहासन हो। यहाँ चन्द्रमा भएका व्यक्तिमा प्रायः स्वाभाविक गरिमा, परिवार र परम्पराप्रति आदर, र आफूलाई दिइएको नामको मर्यादा राख्ने चाहना हुन्छ। उनीहरू आफ्ना मानिसको जिम्मेवारी लिने उदार नेता बन्न सक्छन्। परम्पराले मघालाई वंश, सम्मान र अधिकारसँग जोड्छ, त्यसैले नेतृत्व, प्रशासन, इतिहास, कानुन र सम्पदा जोगाउने काम यसलाई सुहाउँछ। यसको वरदान हृदयको उदारता हो; सिक्नुपर्ने पाठ मुकुट हल्का भएर लगाउनु हो — सेवाबाट नेतृत्व गर्नु र असल कर्मले पुर्खाको सम्मान गर्नु।",
    # EN: Purva Phalguni is ruled by Bhaga, the god of fortune and marital happiness, and symbolised
    #     by the front legs of a bed — an image of rest and enjoyment. People with the Moon here are
    #     often warm, charming, creative and fond of celebration, music and good company. They bring
    #     people together and know how to relax and enjoy what they have earned. Tradition links
    #     Purva Phalguni with love, the arts and leisure, so entertainment, design, hospitality and
    #     relationship-centred work suit it well. Its gift is joy that is easily shared; its lesson
    #     is balance between pleasure and duty.
    "purva-phalguni": "पूर्वफाल्गुनीका स्वामी सौभाग्य र दाम्पत्य सुखका देवता भग हुन् र प्रतीक खाटका अगाडिका खुट्टा हो — विश्राम र आनन्दको प्रतिबिम्ब। यहाँ चन्द्रमा भएका व्यक्ति प्रायः न्यानो स्वभावका, आकर्षक, सिर्जनशील र उत्सव, सङ्गीत तथा असल सङ्गतिका सौखिन हुन्छन्। मानिसलाई जोड्न जान्दछन् र आफूले कमाएको कुरामा आराम गरी आनन्द लिन जान्दछन्। परम्पराले पूर्वफाल्गुनीलाई प्रेम, कला र फुर्सदसँग जोड्छ, त्यसैले मनोरञ्जन, डिजाइन, आतिथ्य र सम्बन्धमा केन्द्रित काम यसलाई सुहाउँछ। यसको वरदान सजिलै बाँड्न सकिने आनन्द हो; सिक्नुपर्ने पाठ सुख र कर्तव्यबीच सन्तुलन राख्नु हो।",
    # EN: Uttara Phalguni is ruled by Aryaman, the god of friendship, contracts and marriage vows,
    #     and symbolised by the back legs of a bed. Where its twin Purva Phalguni enjoys, Uttara
    #     Phalguni commits. People with the Moon here are often reliable, helpful, fair-minded and
    #     loyal to friends and partners. They keep their word and like to be of real use to others.
    #     Tradition links this nakshatra with patronage and lasting partnerships, so management,
    #     public service, counselling, law and charitable work suit it well. Its gift is dependable
    #     kindness; its lesson is to accept help as gracefully as it is given.
    "uttara-phalguni": "उत्तरफाल्गुनीका स्वामी मित्रता, सम्झौता र विवाहको वचनका देवता अर्यमा हुन् र प्रतीक खाटका पछाडिका खुट्टा हो। पूर्वफाल्गुनीले आनन्द लिन्छ भने उत्तरफाल्गुनीले प्रतिबद्धता निभाउँछ। यहाँ चन्द्रमा भएका व्यक्ति प्रायः भरपर्दा, सहयोगी, न्यायप्रिय र साथी तथा जीवनसाथीप्रति निष्ठावान हुन्छन्। वचन पालना गर्छन् र अरूको साँच्चै काम लाग्न चाहन्छन्। परम्पराले यस नक्षत्रलाई संरक्षण र दीर्घ साझेदारीसँग जोड्छ, त्यसैले व्यवस्थापन, सार्वजनिक सेवा, परामर्श, कानुन र परोपकारी काम यसलाई सुहाउँछ। यसको वरदान भरोसायोग्य दयालुता हो; सिक्नुपर्ने पाठ सहयोग दिए जत्तिकै शालीनताले लिन सक्नु हो।",
    # EN: Hasta is ruled by Savitr, the radiant Sun, and symbolised by a hand. People with the Moon
    #     here are often skilful, practical, witty and clever with their hands as well as their
    #     minds. They like to get things done and can turn an idea into something real. Tradition
    #     links Hasta with craftsmanship, healing touch and resourcefulness, so crafts, the arts,
    #     surgery, massage, writing, trade and any skilled trade suit it well. Its gift is the
    #     ability to make and to mend; its lesson is to hold things with an open hand, trusting that
    #     effort brings its own rewards.
    "hasta": "हस्तका स्वामी तेजस्वी सूर्य सविता हुन् र प्रतीक हात हो। यहाँ चन्द्रमा भएका व्यक्ति प्रायः दक्ष, व्यावहारिक, हाजिरीजवाफी र दिमागजत्तिकै हातले पनि सिपालु हुन्छन्। काम सम्पन्न गर्न मन पराउँछन् र विचारलाई साँचो रूप दिन सक्छन्। परम्पराले हस्तलाई हस्तकला, उपचारको स्पर्श र साधन-सम्पन्नतासँग जोड्छ, त्यसैले हस्तशिल्प, कला, शल्यचिकित्सा, मालिस, लेखन, व्यापार र कुनै पनि सीपयुक्त पेशा यसलाई सुहाउँछ। यसको वरदान बनाउन र मर्मत गर्न सक्ने क्षमता हो; सिक्नुपर्ने पाठ खुला हातले समात्नु हो, परिश्रमले आफ्नै फल दिन्छ भन्ने भरोसा राखेर।",
    # EN: Chitra is ruled by Tvashtr, also known as Vishwakarma, the divine architect, and
    #     symbolised by a bright jewel. Its name means "brilliant" or "picture", and people with the
    #     Moon here often have a strong sense of beauty, design and form. They enjoy creating things
    #     that are both useful and attractive, and they notice detail. Tradition links Chitra with
    #     architecture, the arts and craftsmanship, so design, engineering, fashion, jewellery,
    #     photography and planning suit it well. Its gift is the eye of an artist and the hand of a
    #     builder; its lesson is to value inner beauty as much as outer polish.
    "chitra": "चित्राका स्वामी दिव्य वास्तुकार त्वष्टा (विश्वकर्मा) हुन् र प्रतीक चम्किलो रत्न हो। यसको नामको अर्थ “चम्किलो” वा “चित्र” हुन्छ, र यहाँ चन्द्रमा भएका व्यक्तिमा प्रायः सौन्दर्य, डिजाइन र आकारको तीव्र बोध हुन्छ। उपयोगी र आकर्षक दुवै वस्तु बनाउन रमाउँछन् र सूक्ष्म कुरा नोट गर्छन्। परम्पराले चित्रालाई वास्तुकला, कला र शिल्पसँग जोड्छ, त्यसैले डिजाइन, इन्जिनियरिङ, फेसन, गहना, फोटोग्राफी र योजना यसलाई सुहाउँछ। यसको वरदान कलाकारको आँखा र निर्माताको हात हो; सिक्नुपर्ने पाठ बाहिरी चमकजत्तिकै भित्री सुन्दरताको कदर गर्नु हो।",
    # EN: Swati is ruled by Vayu, the wind, and symbolised by a young shoot swaying in the breeze —
    #     flexible, independent and able to bend without breaking. People with the Moon here often
    #     value freedom, fairness and their own way of doing things. They are usually diplomatic,
    #     courteous and good at business and negotiation. Tradition links Swati with trade, travel
    #     and self-reliance, so commerce, law, diplomacy, communication and independent work suit it
    #     well. Its gift is adaptability and a gentle, balanced manner; its lesson is to put down
    #     roots, so that the young shoot can grow into a strong tree.
    "swati": "स्वातीका स्वामी वायु (हावा) हुन् र प्रतीक हावामा झुलिरहेको कलिलो बिरुवा हो — लचिलो, स्वतन्त्र र नटुटी झुक्न सक्ने। यहाँ चन्द्रमा भएका व्यक्ति प्रायः स्वतन्त्रता, न्याय र आफ्नै शैलीमा काम गर्ने तरिकालाई महत्त्व दिन्छन्। उनीहरू सामान्यतः कूटनीतिक, शिष्ट र व्यापार तथा वार्तामा कुशल हुन्छन्। परम्पराले स्वातीलाई व्यापार, यात्रा र आत्मनिर्भरतासँग जोड्छ, त्यसैले वाणिज्य, कानुन, कूटनीति, सञ्चार र स्वतन्त्र काम यसलाई सुहाउँछ। यसको वरदान अनुकूलन क्षमता र कोमल, सन्तुलित व्यवहार हो; सिक्नुपर्ने पाठ जरा गाड्नु हो, ताकि कलिलो बिरुवा बलियो रूखमा बदलियोस्।",
    # EN: Vishakha is ruled by Indra and Agni together, and symbolised by a triumphal arch decorated
    #     with leaves. People with the Moon here are often purposeful, ambitious and determined to
    #     reach the goal they have set. They have energy, conviction and the patience to keep going
    #     over a long road. Tradition calls Vishakha the nakshatra of purpose, so leadership,
    #     research, politics, sales, teaching and any long-term mission suit it well. Its gift is
    #     focus and the ability to inspire others towards a shared aim; its lesson is to enjoy the
    #     journey, not only the arch at its end.
    "vishakha": "विशाखाका स्वामी इन्द्र र अग्नि दुवै हुन् र प्रतीक पातले सजाइएको विजय तोरण हो। यहाँ चन्द्रमा भएका व्यक्ति प्रायः उद्देश्यमुखी, महत्त्वाकाङ्क्षी र तोकेको लक्ष्यमा पुग्न दृढ हुन्छन्। उनीहरूमा ऊर्जा, विश्वास र लामो बाटो हिँड्ने धैर्य हुन्छ। परम्पराले विशाखालाई उद्देश्यको नक्षत्र भन्छ, त्यसैले नेतृत्व, अनुसन्धान, राजनीति, बिक्री, शिक्षण र दीर्घकालीन अभियान यसलाई सुहाउँछ। यसको वरदान एकाग्रता र अरूलाई साझा लक्ष्यतर्फ प्रेरित गर्ने क्षमता हो; सिक्नुपर्ने पाठ यात्राको पनि आनन्द लिनु हो, अन्त्यको तोरणमात्र होइन।",
    # EN: Anuradha is ruled by Mitra, the god of friendship and cooperation, and symbolised by a
    #     lotus that blooms out of muddy water. People with the Moon here are often loyal friends,
    #     devoted to their ideals and able to keep going with quiet faith in difficult places. They
    #     are good at bringing people together in groups and organisations. Tradition links Anuradha
    #     with friendship, devotion and success away from home, so teamwork, organisation,
    #     counselling, travel and spiritual practice suit it well. Its gift is the ability to
    #     blossom anywhere; its lesson is to be as gentle with oneself as with friends.
    "anuradha": "अनुराधाका स्वामी मित्रता र सहकार्यका देवता मित्र हुन् र प्रतीक हिलोको पानीबाट फक्रने कमल हो। यहाँ चन्द्रमा भएका व्यक्ति प्रायः निष्ठावान मित्र हुन्छन्, आफ्ना आदर्शप्रति समर्पित र कठिन ठाउँमा पनि शान्त विश्वासका साथ अघि बढ्न सक्ने। समूह र संस्थामा मानिसलाई जोड्न माहिर हुन्छन्। परम्पराले अनुराधालाई मित्रता, भक्ति र घरबाहिर सफलतासँग जोड्छ, त्यसैले टोली कार्य, सङ्गठन, परामर्श, यात्रा र आध्यात्मिक साधना यसलाई सुहाउँछ। यसको वरदान जहाँ पनि फक्रन सक्ने क्षमता हो; सिक्नुपर्ने पाठ साथीसँग जत्तिकै आफूसँग पनि कोमल हुनु हो।",
    # EN: Jyeshtha is ruled by Indra, king of the gods, and symbolised by a circular amulet or
    #     earring. Its name means "the eldest", and people with the Moon here often take on
    #     responsibility early, protect those around them and carry a quiet authority. They are
    #     resourceful, perceptive and capable under pressure. Tradition links Jyeshtha with
    #     seniority and protection, so leadership, management, administration, security and any role
    #     that looks after others suit it well. Its gift is courage and capability; its lesson is to
    #     lead with humility and to let others share the load rather than carrying everything alone.
    "jyeshtha": "ज्येष्ठाका स्वामी देवताहरूका राजा इन्द्र हुन् र प्रतीक गोलाकार ताबिज वा कुण्डल हो। यसको नामको अर्थ “जेठो” हो, र यहाँ चन्द्रमा भएका व्यक्तिले प्रायः सानैमा जिम्मेवारी लिन्छन्, वरिपरिकाको रक्षा गर्छन् र शान्त अधिकार बोकेका हुन्छन्। उनीहरू साधन-सम्पन्न, सूक्ष्मदर्शी र दबाबमा सक्षम हुन्छन्। परम्पराले ज्येष्ठालाई ज्येष्ठता र संरक्षणसँग जोड्छ, त्यसैले नेतृत्व, व्यवस्थापन, प्रशासन, सुरक्षा र अरूको हेरचाह गर्ने कुनै पनि भूमिका यसलाई सुहाउँछ। यसको वरदान साहस र क्षमता हो; सिक्नुपर्ने पाठ नम्रतासाथ नेतृत्व गर्नु र सबै भार एक्लै नबोकी अरूलाई पनि बाँड्न दिनु हो।",
    # EN: Mula is ruled by Nirriti and symbolised by a bunch of roots. Its name means "the root",
    #     and people with the Moon here are often drawn to get to the bottom of things — to find the
    #     origin of a question, an idea or a tradition. They can be independent, philosophical and
    #     unafraid to start again from first principles. Tradition links Mula with investigation and
    #     with letting go of what is no longer needed, so research, medicine, philosophy, botany and
    #     spiritual inquiry suit it well. Its gift is depth; its lesson is that clearing old ground
    #     makes room for new growth.
    "mula": "मूलकी स्वामिनी निरृति हुन् र प्रतीक जराहरूको झुप्पो हो। यसको नामको अर्थ “जरा” हो, र यहाँ चन्द्रमा भएका व्यक्ति प्रायः कुनै प्रश्न, विचार वा परम्पराको उद्गम खोज्दै तहसम्म पुग्न चाहन्छन्। उनीहरू स्वतन्त्र, दार्शनिक र आधारभूत सिद्धान्तबाट फेरि सुरु गर्न नडराउने हुन सक्छन्। परम्पराले मूललाई अनुसन्धान र अब नचाहिने कुरा त्याग्नुसँग जोड्छ, त्यसैले अनुसन्धान, चिकित्सा, दर्शन, वनस्पतिशास्त्र र आध्यात्मिक जिज्ञासा यसलाई सुहाउँछ। यसको वरदान गहिराइ हो; सिक्नुपर्ने पाठ पुरानो जग सफा गर्दा नयाँ वृद्धिलाई ठाउँ मिल्छ भन्ने हो।",
    # EN: Purva Ashadha is ruled by Apas, the cosmic waters, and symbolised by a winnowing fan or an
    #     elephant tusk. Its name means "the early invincible", and people with the Moon here are
    #     often confident, persuasive and full of conviction. Like water, they can be gentle and yet
    #     wear down any obstacle in time. Tradition links Purva Ashadha with purification and with
    #     victory won through persistence, so teaching, law, debate, the arts, shipping and anything
    #     to do with water suit it well. Its gift is optimism and inner strength; its lesson is to
    #     stay open to other views while holding firm to its own.
    "purva-ashadha": "पूर्वाषाढाका स्वामी ब्रह्माण्डीय जल आपः हुन् र प्रतीक सुप्पो वा हात्तीको दाह्रा हो। यसको नामको अर्थ “पहिलेको अजेय” हो, र यहाँ चन्द्रमा भएका व्यक्ति प्रायः आत्मविश्वासी, मनाउन सक्ने र दृढ विश्वासले भरिएका हुन्छन्। पानीझैँ कोमल हुँदाहुँदै पनि समयक्रममा जुनसुकै बाधा खिइदिन सक्छन्। परम्पराले पूर्वाषाढालाई शुद्धीकरण र दृढताबाट प्राप्त विजयसँग जोड्छ, त्यसैले शिक्षण, कानुन, वादविवाद, कला, जलमार्ग र पानीसँग सम्बन्धित जुनसुकै काम यसलाई सुहाउँछ। यसको वरदान आशावाद र भित्री बल हो; सिक्नुपर्ने पाठ अरूका विचारप्रति खुला रहँदै आफ्नोमा अडिग रहनु हो।",
    # EN: Uttara Ashadha is ruled by the Vishvedevas, the universal gods, and symbolised by an
    #     elephant tusk. Its name means "the later invincible" — the victory that lasts because it
    #     was earned honestly. People with the Moon here are often principled, patient, responsible
    #     and respected for their integrity. They take the long view and finish what they commit to.
    #     Tradition links Uttara Ashadha with righteous leadership, so government, management, law,
    #     teaching and social causes suit it well. Its gift is steady, ethical strength; its lesson
    #     is to keep a little lightness and warmth alongside the seriousness of duty.
    "uttara-ashadha": "उत्तराषाढाका स्वामी विश्वेदेवा (सार्वभौम देवता) हुन् र प्रतीक हात्तीको दाह्रा हो। यसको नामको अर्थ “पछिको अजेय” हो — इमानदारीले कमाइएकाले टिकिरहने विजय। यहाँ चन्द्रमा भएका व्यक्ति प्रायः सिद्धान्तवादी, धैर्यवान्, जिम्मेवार र आफ्नो सत्यनिष्ठाका लागि सम्मानित हुन्छन्। उनीहरू लामो दृष्टि राख्छन् र प्रतिबद्ध भएको काम पूरा गर्छन्। परम्पराले उत्तराषाढालाई धर्मपरायण नेतृत्वसँग जोड्छ, त्यसैले सरकारी सेवा, व्यवस्थापन, कानुन, शिक्षण र सामाजिक अभियान यसलाई सुहाउँछ। यसको वरदान स्थिर, नैतिक बल हो; सिक्नुपर्ने पाठ कर्तव्यको गम्भीरताका साथसाथै अलिकति हल्कापन र न्यानोपन जोगाउनु हो।",
    # EN: Shravana is ruled by Vishnu, the preserver, and symbolised by an ear or three footprints.
    #     Its name means "hearing", and people with the Moon here are often good listeners, eager
    #     learners and keepers of knowledge and tradition. They learn by listening and pass on what
    #     they have learned. Tradition links Shravana with wisdom gained through study and with
    #     connecting people, so teaching, counselling, media, languages, music and travel suit it
    #     well. Its gift is attentive understanding and a wish to be useful; its lesson is to listen
    #     to one's own inner voice as carefully as to others.
    "shravana": "श्रवणका स्वामी पालनकर्ता विष्णु हुन् र प्रतीक कान वा तीन पाइला हो। यसको नामको अर्थ “सुन्नु” हो, र यहाँ चन्द्रमा भएका व्यक्ति प्रायः राम्रा श्रोता, उत्सुक विद्यार्थी र ज्ञान तथा परम्पराका रक्षक हुन्छन्। उनीहरू सुनेर सिक्छन् र सिकेको कुरा अरूलाई सुम्पन्छन्। परम्पराले श्रवणलाई अध्ययनबाट प्राप्त बुद्धि र मानिसलाई जोड्ने कामसँग जोड्छ, त्यसैले शिक्षण, परामर्श, सञ्चार माध्यम, भाषा, सङ्गीत र यात्रा यसलाई सुहाउँछ। यसको वरदान ध्यानपूर्वक बुझ्ने क्षमता र उपयोगी हुने चाहना हो; सिक्नुपर्ने पाठ अरूको जत्तिकै आफ्नै भित्री आवाज पनि ध्यानले सुन्नु हो।",
    # EN: Dhanishta is ruled by the eight Vasus, gods of abundance, and symbolised by a drum. Its
    #     name means "the wealthiest", and people with the Moon here often have rhythm, energy and a
    #     talent for music, dance or teamwork. They are generous, sociable and able to keep a group
    #     moving together. Tradition links Dhanishta with prosperity and with sound, so music,
    #     performance, sport, property, finance and community work suit it well. Its gift is the
    #     ability to set the beat that others follow; its lesson is to listen as well as play,
    #     leaving space for others' rhythms.
    "dhanishta": "धनिष्ठाका स्वामी समृद्धिका देवता आठ वसु हुन् र प्रतीक ढोल हो। यसको नामको अर्थ “सबैभन्दा धनी” हो, र यहाँ चन्द्रमा भएका व्यक्तिमा प्रायः लय, ऊर्जा र सङ्गीत, नृत्य वा टोली कार्यको प्रतिभा हुन्छ। उनीहरू उदार, मिलनसार र समूहलाई सँगै अघि बढाउन सक्ने हुन्छन्। परम्पराले धनिष्ठालाई समृद्धि र ध्वनिसँग जोड्छ, त्यसैले सङ्गीत, प्रदर्शन, खेलकुद, सम्पत्ति, वित्त र सामुदायिक काम यसलाई सुहाउँछ। यसको वरदान अरूले पछ्याउने ताल उठाउन सक्ने क्षमता हो; सिक्नुपर्ने पाठ बजाउनुजत्तिकै सुन्नु पनि हो, अरूका लयका लागि ठाउँ छोडेर।",
    # EN: Shatabhisha is ruled by Varuna, lord of the cosmic waters and of truth, and symbolised by
    #     an empty circle. Its name means "a hundred healers", and people with the Moon here are
    #     often independent thinkers, private, truthful and drawn to understanding how things really
    #     work. They can see patterns others miss. Tradition links Shatabhisha with healing and with
    #     the search for hidden truth, so medicine, research, science, technology, astronomy and
    #     alternative healing suit it well. Its gift is clear, original insight; its lesson is to
    #     let others into the circle, sharing what is understood with warmth.
    "shatabhisha": "शतभिषाका स्वामी ब्रह्माण्डीय जल र सत्यका अधिपति वरुण हुन् र प्रतीक खाली गोलो घेरा हो। यसको नामको अर्थ “सय वैद्य” हो, र यहाँ चन्द्रमा भएका व्यक्ति प्रायः स्वतन्त्र चिन्तक, एकान्तप्रिय, सत्यवादी र कुराहरू साँच्चै कसरी चल्छन् भन्ने बुझ्न चाहने हुन्छन्। अरूले नदेखेका ढाँचा उनीहरूले देख्छन्। परम्पराले शतभिषालाई उपचार र लुकेको सत्यको खोजीसँग जोड्छ, त्यसैले चिकित्सा, अनुसन्धान, विज्ञान, प्रविधि, खगोलशास्त्र र वैकल्पिक उपचार यसलाई सुहाउँछ। यसको वरदान स्पष्ट, मौलिक अन्तर्दृष्टि हो; सिक्नुपर्ने पाठ अरूलाई घेराभित्र आउन दिनु र बुझेको कुरा न्यानोपनका साथ बाँड्नु हो।",
    # EN: Purva Bhadrapada is ruled by Aja Ekapada, the one-footed form of Shiva, and symbolised by
    #     swords or the front legs of a cot. People with the Moon here are often idealistic, intense
    #     and willing to give themselves fully to a cause they believe in. They can be eloquent,
    #     generous and deeply spiritual. Tradition links Purva Bhadrapada with transformation and
    #     with the fire of tapas — sincere effort for a higher aim — so social reform, philosophy,
    #     writing, research and spiritual life suit it well. Its gift is passionate commitment; its
    #     lesson is to temper intensity with patience and calm.
    "purva-bhadrapada": "पूर्वभाद्रपदका स्वामी शिवको एकपाद रूप अजैकपाद हुन् र प्रतीक तरवार वा खाटका अगाडिका खुट्टा हो। यहाँ चन्द्रमा भएका व्यक्ति प्रायः आदर्शवादी, तीव्र र आफूले विश्वास गरेको उद्देश्यमा पूर्ण रूपमा आफूलाई समर्पित गर्न तयार हुन्छन्। उनीहरू वाक्पटु, उदार र गहिरो आध्यात्मिक हुन सक्छन्। परम्पराले पूर्वभाद्रपदलाई रूपान्तरण र तपको अग्निसँग जोड्छ — उच्च लक्ष्यका लागि इमानदार प्रयास — त्यसैले समाज सुधार, दर्शन, लेखन, अनुसन्धान र आध्यात्मिक जीवन यसलाई सुहाउँछ। यसको वरदान उत्कट प्रतिबद्धता हो; सिक्नुपर्ने पाठ तीव्रतालाई धैर्य र शान्तिले सन्तुलित गर्नु हो।",
    # EN: Uttara Bhadrapada is ruled by Ahir Budhnya, the serpent of the deep waters, and symbolised
    #     by the back legs of a cot or twins. Where Purva Bhadrapada burns, Uttara Bhadrapada
    #     settles into calm depth. People with the Moon here are often wise, patient, composed and
    #     compassionate, with self-control and a gift for counsel. They tend to think before they
    #     speak and are steady in difficult times. Tradition links this nakshatra with depth,
    #     renunciation and kindness, so counselling, charity, teaching, research and spiritual
    #     practice suit it well. Its gift is serene wisdom; its lesson is to share it actively, not
    #     only privately.
    "uttara-bhadrapada": "उत्तरभाद्रपदका स्वामी गहिरो जलका सर्प अहिर्बुध्न्य हुन् र प्रतीक खाटका पछाडिका खुट्टा वा जुम्ल्याहा हो। पूर्वभाद्रपद दन्किँदा उत्तरभाद्रपद शान्त गहिराइमा स्थिर हुन्छ। यहाँ चन्द्रमा भएका व्यक्ति प्रायः बुद्धिमान्, धैर्यवान्, शान्त र करुणामय हुन्छन्, आत्मसंयम र सल्लाह दिने प्रतिभासहित। बोल्नुअघि सोच्ने र कठिन समयमा स्थिर रहने स्वभावका हुन्छन्। परम्पराले यस नक्षत्रलाई गहिराइ, त्याग र दयालुतासँग जोड्छ, त्यसैले परामर्श, दान, शिक्षण, अनुसन्धान र आध्यात्मिक साधना यसलाई सुहाउँछ। यसको वरदान शान्त बुद्धि हो; सिक्नुपर्ने पाठ त्यसलाई एक्लै नराखी सक्रिय रूपमा बाँड्नु हो।",
    # EN: Revati, the last nakshatra, is ruled by Pushan, the nourisher who guides travellers and
    #     protects herds on their way, and symbolised by a fish. People with the Moon here are often
    #     gentle, kind, imaginative and protective of the weak, with a love of animals, art and
    #     music. They make good companions on any journey and help others reach their destination
    #     safely. Tradition links Revati with safe journeys, prosperity and completion, so caring
    #     work, the arts, travel, hospitality and spiritual life suit it well. Its gift is
    #     compassion and faith; its lesson is to care for oneself while caring for everyone else.
    "revati": "रेवती अन्तिम नक्षत्र हो; यसका स्वामी यात्रुलाई बाटो देखाउने र पशुधनको रक्षा गर्ने पोषक देवता पूषन् हुन् र प्रतीक माछा हो। यहाँ चन्द्रमा भएका व्यक्ति प्रायः कोमल, दयालु, कल्पनाशील र कमजोरको रक्षा गर्ने, जनावर, कला र सङ्गीतप्रति प्रेम राख्ने हुन्छन्। उनीहरू कुनै पनि यात्रामा राम्रा साथी हुन् र अरूलाई सुरक्षित गन्तव्यमा पुग्न मद्दत गर्छन्। परम्पराले रेवतीलाई सुरक्षित यात्रा, समृद्धि र पूर्णतासँग जोड्छ, त्यसैले सेवामूलक काम, कला, यात्रा, आतिथ्य र आध्यात्मिक जीवन यसलाई सुहाउँछ। यसको वरदान करुणा र आस्था हो; सिक्नुपर्ने पाठ सबैको ख्याल राख्दा आफ्नो पनि ख्याल राख्नु हो।",
}

# app/nakshatra_text.py RASHI_TRAITS["ne"] — character paragraph of each of the 12 rashis (key = slug)  [12]
RASHI_TRAITS = {
    # EN: Mesh (Aries) is the first rashi, a movable fire sign ruled by Mars. People with the Moon
    #     in Mesh are often energetic, direct, courageous and quick to act — natural starters who
    #     enjoy a challenge and like to lead from the front. They are honest about their feelings
    #     and recover quickly from setbacks. Their emotional life is warm and spontaneous, and they
    #     bring enthusiasm wherever they go. Work that rewards initiative — sport, the armed forces,
    #     engineering, entrepreneurship, surgery — often suits them. Their growth lies in patience
    #     and in listening before acting, so that their courage is matched by care for others.
    "mesh": "मेष पहिलो राशि हो — मङ्गलद्वारा शासित चर अग्नि राशि। मेषमा चन्द्रमा भएका व्यक्ति प्रायः ऊर्जावान, स्पष्टवक्ता, साहसी र छिटो कदम चाल्ने हुन्छन् — स्वाभाविक रूपमा काम सुरु गर्ने, चुनौती मन पराउने र अगाडिबाट नेतृत्व गर्न रुचाउने। उनीहरू आफ्ना भावनाबारे इमानदार हुन्छन् र असफलताबाट छिट्टै उठ्छन्। भावनात्मक जीवन न्यानो र सहज हुन्छ, र जहाँ गए पनि उत्साह लिएर जान्छन्। खेलकुद, सेना, इन्जिनियरिङ, उद्यमशीलता, शल्यचिकित्सा जस्ता पहल गर्नेलाई पुरस्कृत गर्ने काम प्रायः सुहाउँछ। विकासको बाटो धैर्य र कारबाही गर्नुअघि सुन्नुमा छ, ताकि साहससँगै अरूप्रतिको ख्याल पनि रहोस्।",
    # EN: Vrishabh (Taurus) is a fixed earth sign ruled by Venus, and the Moon is exalted here.
    #     People with the Moon in Vrishabh are often calm, patient, loyal and steady, with a love of
    #     comfort, good food, music and beautiful things. They build slowly and surely, and what
    #     they build tends to last. Emotionally they are dependable and affectionate, preferring
    #     security to drama. Finance, agriculture, the arts, food, design and any work that rewards
    #     persistence often suit them. Their growth lies in flexibility — welcoming change when it
    #     comes, and holding possessions and opinions a little more lightly.
    "vrishabh": "वृष स्थिर पृथ्वी राशि हो, शुक्रद्वारा शासित, र यहाँ चन्द्रमा उच्च हुन्छन्। वृषमा चन्द्रमा भएका व्यक्ति प्रायः शान्त, धैर्यवान्, निष्ठावान र स्थिर हुन्छन्, सुख-सुविधा, राम्रो खाना, सङ्गीत र सुन्दर वस्तुप्रति प्रेम राख्ने। उनीहरू बिस्तारै तर पक्का निर्माण गर्छन्, र जे बनाउँछन् त्यो टिक्छ। भावनात्मक रूपमा भरपर्दा र स्नेही हुन्छन्, नाटकभन्दा सुरक्षा रुचाउने। वित्त, कृषि, कला, खाद्य, डिजाइन र लगनशीलतालाई पुरस्कृत गर्ने काम प्रायः सुहाउँछ। विकासको बाटो लचिलोपनमा छ — परिवर्तन आउँदा स्वागत गर्नु, र सम्पत्ति तथा धारणालाई अलि हल्का रूपमा समात्नु।",
    # EN: Mithun (Gemini) is a dual air sign ruled by Mercury. People with the Moon in Mithun are
    #     often curious, witty, talkative and quick to learn, with many interests and a gift for
    #     connecting ideas and people. They enjoy conversation, reading, travel and anything that
    #     keeps the mind busy. Emotionally they need variety and a partner who is also a friend they
    #     can talk to. Writing, teaching, media, sales, technology and trade often suit them. Their
    #     growth lies in depth and focus — choosing a few things and seeing them through — and in
    #     giving their own feelings the attention they give to ideas.
    "mithun": "मिथुन बुधद्वारा शासित द्विस्वभाव वायु राशि हो। मिथुनमा चन्द्रमा भएका व्यक्ति प्रायः जिज्ञासु, हाजिरीजवाफी, बोल्न रुचाउने र छिटो सिक्ने हुन्छन्, धेरै रुचि र विचार तथा मानिसलाई जोड्ने प्रतिभासहित। कुराकानी, पढाइ, यात्रा र मनलाई व्यस्त राख्ने जुनसुकै कुरा मन पराउँछन्। भावनात्मक रूपमा उनीहरूलाई विविधता र कुरा गर्न सकिने साथी जस्तै जीवनसाथी चाहिन्छ। लेखन, शिक्षण, सञ्चार माध्यम, बिक्री, प्रविधि र व्यापार प्रायः सुहाउँछ। विकासको बाटो गहिराइ र एकाग्रतामा छ — केही थोरै कुरा रोजेर पूरा गर्नु — र विचारलाई दिने ध्यान आफ्ना भावनालाई पनि दिनु।",
    # EN: Kark (Cancer) is a movable water sign ruled by the Moon itself, so the Moon is at home
    #     here. People with the Moon in Kark are often caring, sensitive, intuitive and devoted to
    #     family and home. They remember kindness, protect those they love and create warmth
    #     wherever they live. Their moods can change like the tides, but their loyalty runs deep.
    #     Nursing, teaching, hospitality, food, real estate, counselling and public service often
    #     suit them. Their growth lies in trusting their own strength, letting go of old hurts and
    #     allowing others to care for them in return.
    "kark": "कर्कट चन्द्रमा स्वयंद्वारा शासित चर जल राशि हो, त्यसैले चन्द्रमा यहाँ आफ्नै घरमा हुन्छन्। कर्कटमा चन्द्रमा भएका व्यक्ति प्रायः स्नेही, संवेदनशील, सहज बोध भएका र परिवार तथा घरप्रति समर्पित हुन्छन्। उनीहरू दयालुपन सम्झन्छन्, प्रियजनको रक्षा गर्छन् र जहाँ बसे पनि न्यानोपन सिर्जना गर्छन्। मन ज्वारभाटाझैँ फेरिन सक्छ, तर निष्ठा गहिरो हुन्छ। नर्सिङ, शिक्षण, आतिथ्य, खाद्य, घरजग्गा, परामर्श र सार्वजनिक सेवा प्रायः सुहाउँछ। विकासको बाटो आफ्नै बलमा विश्वास गर्नु, पुराना घाउ छोड्नु र बदलामा अरूलाई पनि आफ्नो ख्याल राख्न दिनुमा छ।",
    # EN: Simha (Leo) is a fixed fire sign ruled by the Sun. People with the Moon in Simha are often
    #     generous, dignified, confident and warm-hearted, with a natural sense of leadership and a
    #     love of recognition. They are loyal to those who trust them and protective of their family
    #     and friends. Emotionally they are proud and open-hearted, and they shine when appreciated.
    #     Leadership, administration, politics, the performing arts, teaching and government service
    #     often suit them. Their growth lies in humility — letting others share the stage, and
    #     finding confidence from within rather than from applause.
    "simha": "सिंह सूर्यद्वारा शासित स्थिर अग्नि राशि हो। सिंहमा चन्द्रमा भएका व्यक्ति प्रायः उदार, गरिमामय, आत्मविश्वासी र न्यानो हृदयका हुन्छन्, स्वाभाविक नेतृत्व र मान्यताको चाहनासहित। आफूमाथि भरोसा गर्नेप्रति निष्ठावान र परिवार तथा साथीको रक्षक हुन्छन्। भावनात्मक रूपमा स्वाभिमानी र खुला हृदयका हुन्छन्, र कदर पाउँदा चम्किन्छन्। नेतृत्व, प्रशासन, राजनीति, प्रदर्शन कला, शिक्षण र सरकारी सेवा प्रायः सुहाउँछ। विकासको बाटो नम्रतामा छ — अरूलाई पनि मञ्चमा ठाउँ दिनु, र आत्मविश्वास तालीबाट होइन, भित्रबाट खोज्नु।",
    # EN: Kanya (Virgo) is a dual earth sign ruled by Mercury. People with the Moon in Kanya are
    #     often practical, analytical, modest and helpful, with an eye for detail and a wish to make
    #     things work properly. They show care through service — fixing, organising and looking
    #     after the small things others overlook. Emotionally they can be reserved, but they are
    #     deeply dependable. Medicine, accounting, research, editing, nutrition, teaching and any
    #     precise craft often suit them. Their growth lies in self-acceptance: being as kind to
    #     their own imperfections as they are patient with other people's needs.
    "kanya": "कन्या बुधद्वारा शासित द्विस्वभाव पृथ्वी राशि हो। कन्यामा चन्द्रमा भएका व्यक्ति प्रायः व्यावहारिक, विश्लेषणात्मक, विनम्र र सहयोगी हुन्छन्, सूक्ष्म कुरामा नजर र काम ठीकसँग चलोस् भन्ने चाहनासहित। उनीहरू सेवाबाट माया देखाउँछन् — मर्मत गरेर, मिलाएर र अरूले बेवास्ता गर्ने साना कुराको ख्याल राखेर। भावनात्मक रूपमा संयमित देखिए पनि गहिरो भरपर्दा हुन्छन्। चिकित्सा, लेखा, अनुसन्धान, सम्पादन, पोषण, शिक्षण र सूक्ष्म शिल्प प्रायः सुहाउँछ। विकासको बाटो आत्मस्वीकारमा छ: अरूका आवश्यकतामा जत्तिको धैर्य राख्छन्, आफ्ना कमजोरीप्रति पनि त्यत्तिकै दयालु हुनु।",
    # EN: Tula (Libra) is a movable air sign ruled by Venus, symbolised by the scales. People with
    #     the Moon in Tula are often gracious, fair-minded, sociable and diplomatic, with a strong
    #     sense of beauty and justice. They value harmony in relationships and are good at seeing
    #     both sides of a question. Emotionally they need partnership and feel most at ease when
    #     things around them are balanced. Law, diplomacy, design, fashion, the arts, counselling
    #     and business partnerships often suit them. Their growth lies in decisiveness — trusting
    #     their own judgement and accepting that a little disagreement can be healthy.
    "tula": "तुला शुक्रद्वारा शासित चर वायु राशि हो, तराजु यसको प्रतीक। तुलामा चन्द्रमा भएका व्यक्ति प्रायः शालीन, न्यायप्रिय, मिलनसार र कूटनीतिक हुन्छन्, सौन्दर्य र न्यायको तीव्र बोधसहित। सम्बन्धमा सामञ्जस्यलाई महत्त्व दिन्छन् र प्रश्नका दुवै पक्ष देख्न सक्छन्। भावनात्मक रूपमा उनीहरूलाई साझेदारी चाहिन्छ र वरिपरि सन्तुलन हुँदा सबैभन्दा सहज महसुस गर्छन्। कानुन, कूटनीति, डिजाइन, फेसन, कला, परामर्श र व्यावसायिक साझेदारी प्रायः सुहाउँछ। विकासको बाटो निर्णायकतामा छ — आफ्नै विवेकमा भरोसा गर्नु, र अलिकति असहमति पनि स्वस्थ हुन सक्छ भन्ने स्वीकार्नु।",
    # EN: Vrishchik (Scorpio) is a fixed water sign ruled by Mars. People with the Moon in Vrishchik
    #     are often intense, perceptive, determined and deeply loyal, with feelings that run far
    #     below the surface. They are not satisfied with appearances and want to understand what is
    #     really going on. Once they commit — to a person, a cause or a goal — they rarely let go.
    #     Research, investigation, medicine, psychology, finance and crisis work often suit them.
    #     Their growth lies in trust and forgiveness: letting others in, and allowing old feelings
    #     to transform rather than be held.
    "vrishchik": "वृश्चिक मङ्गलद्वारा शासित स्थिर जल राशि हो। वृश्चिकमा चन्द्रमा भएका व्यक्ति प्रायः तीव्र, सूक्ष्मदर्शी, दृढ र गहिरो निष्ठावान हुन्छन्, सतहभन्दा धेरै तल बग्ने भावनासहित। देखावटमा सन्तुष्ट हुँदैनन्, साँच्चै के भइरहेको छ बुझ्न चाहन्छन्। कुनै व्यक्ति, उद्देश्य वा लक्ष्यप्रति एकपटक प्रतिबद्ध भएपछि विरलै छोड्छन्। अनुसन्धान, जाँचबुझ, चिकित्सा, मनोविज्ञान, वित्त र सङ्कटकालीन काम प्रायः सुहाउँछ। विकासको बाटो विश्वास र क्षमामा छ: अरूलाई भित्र आउन दिनु, र पुराना भावनालाई पक्रेर राख्नुको सट्टा रूपान्तरण हुन दिनु।",
    # EN: Dhanu (Sagittarius) is a dual fire sign ruled by Jupiter, symbolised by the archer. People
    #     with the Moon in Dhanu are often optimistic, honest, generous and philosophical, with a
    #     love of learning, travel and freedom. They look for meaning in life and enjoy sharing what
    #     they have learned. Emotionally they are open and cheerful, and they need room to grow.
    #     Teaching, law, religion and philosophy, publishing, travel and sport often suit them.
    #     Their growth lies in following through — giving the same attention to the details of daily
    #     life that they give to big ideas and distant horizons.
    "dhanu": "धनु बृहस्पतिद्वारा शासित द्विस्वभाव अग्नि राशि हो, धनुर्धर यसको प्रतीक। धनुमा चन्द्रमा भएका व्यक्ति प्रायः आशावादी, इमानदार, उदार र दार्शनिक हुन्छन्, अध्ययन, यात्रा र स्वतन्त्रताप्रति प्रेमसहित। उनीहरू जीवनको अर्थ खोज्छन् र सिकेको कुरा बाँड्न रमाउँछन्। भावनात्मक रूपमा खुला र हँसिला हुन्छन्, र बढ्न ठाउँ चाहिन्छ। शिक्षण, कानुन, धर्म र दर्शन, प्रकाशन, यात्रा र खेलकुद प्रायः सुहाउँछ। विकासको बाटो काम पूरा गर्नुमा छ — ठूला विचार र टाढाका क्षितिजलाई दिने ध्यान दैनिक जीवनका सानातिना कुरामा पनि दिनु।",
    # EN: Makar (Capricorn) is a movable earth sign ruled by Saturn. People with the Moon in Makar
    #     are often responsible, disciplined, practical and ambitious in a patient, long-term way.
    #     They take duty seriously, work steadily and earn respect over time. Emotionally they can
    #     seem reserved, but they show love through reliability and quiet support. Administration,
    #     management, engineering, government service, finance and any field that rewards
    #     perseverance often suit them. Their growth lies in warmth and rest — allowing themselves
    #     joy along the way, and remembering that their worth is not measured only by achievement.
    "makar": "मकर शनिद्वारा शासित चर पृथ्वी राशि हो। मकरमा चन्द्रमा भएका व्यक्ति प्रायः जिम्मेवार, अनुशासित, व्यावहारिक र धैर्यपूर्वक दीर्घकालीन महत्त्वाकाङ्क्षा राख्ने हुन्छन्। कर्तव्यलाई गम्भीर रूपमा लिन्छन्, स्थिर रूपमा काम गर्छन् र समयक्रममा सम्मान कमाउँछन्। भावनात्मक रूपमा संयमित देखिए पनि भरोसा र चुपचाप सहयोगमार्फत माया देखाउँछन्। प्रशासन, व्यवस्थापन, इन्जिनियरिङ, सरकारी सेवा, वित्त र लगनशीलतालाई पुरस्कृत गर्ने कुनै पनि क्षेत्र प्रायः सुहाउँछ। विकासको बाटो न्यानोपन र विश्राममा छ — बाटोमा आनन्द लिन आफैँलाई अनुमति दिनु, र आफ्नो मूल्य उपलब्धिले मात्र नमापिने कुरा सम्झनु।",
    # EN: Kumbh (Aquarius) is a fixed air sign ruled by Saturn, symbolised by the water-bearer who
    #     pours knowledge out for all. People with the Moon in Kumbh are often independent,
    #     humanitarian, inventive and loyal to friends and ideals. They think about the wider
    #     community and enjoy new ideas, science and reform. Emotionally they value friendship and
    #     freedom, and they show care through principle and action. Science, technology, social
    #     work, research, education and community organisations often suit them. Their growth lies
    #     in closeness — letting their warmth show to individuals as well as to humanity as a whole.
    "kumbh": "कुम्भ शनिद्वारा शासित स्थिर वायु राशि हो, जसको प्रतीक सबैका लागि ज्ञान ढल्ने जलवाहक हो। कुम्भमा चन्द्रमा भएका व्यक्ति प्रायः स्वतन्त्र, मानवतावादी, आविष्कारशील र साथी तथा आदर्शप्रति निष्ठावान हुन्छन्। उनीहरू व्यापक समुदायबारे सोच्छन् र नयाँ विचार, विज्ञान तथा सुधारमा रमाउँछन्। भावनात्मक रूपमा मित्रता र स्वतन्त्रतालाई महत्त्व दिन्छन्, र सिद्धान्त तथा कार्यबाट माया देखाउँछन्। विज्ञान, प्रविधि, समाजसेवा, अनुसन्धान, शिक्षा र सामुदायिक सङ्गठन प्रायः सुहाउँछ। विकासको बाटो निकटतामा छ — आफ्नो न्यानोपन मानवतालाई मात्र होइन, व्यक्तिहरूलाई पनि देखाउनु।",
    # EN: Meen (Pisces) is a dual water sign ruled by Jupiter, the last of the twelve rashis. People
    #     with the Moon in Meen are often compassionate, imaginative, gentle and spiritually
    #     inclined, with a deep sensitivity to the feelings of others. They forgive easily, help
    #     without being asked and are moved by music, art and devotion. Emotionally they are open-
    #     hearted and intuitive. Healing, counselling, the arts, music, charity, teaching and
    #     spiritual work often suit them. Their growth lies in healthy boundaries — caring for
    #     others without losing themselves, and turning their rich imagination into practical
    #     action.
    "meen": "मीन बृहस्पतिद्वारा शासित द्विस्वभाव जल राशि हो, बाह्र राशिमध्ये अन्तिम। मीनमा चन्द्रमा भएका व्यक्ति प्रायः करुणामय, कल्पनाशील, कोमल र आध्यात्मिक झुकाव भएका हुन्छन्, अरूका भावनाप्रति गहिरो संवेदनशीलतासहित। उनीहरू सजिलै क्षमा गर्छन्, नभनी मद्दत गर्छन् र सङ्गीत, कला तथा भक्तिले छुन्छ। भावनात्मक रूपमा खुला हृदय र सहज बोध भएका हुन्छन्। उपचार, परामर्श, कला, सङ्गीत, दान, शिक्षण र आध्यात्मिक काम प्रायः सुहाउँछ। विकासको बाटो स्वस्थ सीमामा छ — आफू नगुमाई अरूको ख्याल राख्नु, र समृद्ध कल्पनालाई व्यावहारिक कदममा बदल्नु।",
}

# app/nakshatra_text.py FACTS["ne"] — deity.<slug> and symbol.<slug> of each nakshatra  [54]
NAKSHATRA_FACTS = {
    # EN: The Ashwini Kumaras, the divine physicians
    "deity.ashwini": "अश्विनीकुमारहरू, देवताका वैद्य",
    # EN: A horse's head
    "symbol.ashwini": "घोडाको टाउको",
    # EN: Yama, lord of dharma
    "deity.bharani": "यम, धर्मका अधिपति",
    # EN: The yoni (womb)
    "symbol.bharani": "योनि (गर्भ)",
    # EN: Agni, the fire
    "deity.krittika": "अग्नि",
    # EN: A razor or flame
    "symbol.krittika": "छुरा वा ज्वाला",
    # EN: Brahma (Prajapati)
    "deity.rohini": "ब्रह्मा (प्रजापति)",
    # EN: A chariot or ox-cart
    "symbol.rohini": "रथ वा गोरुगाडा",
    # EN: Soma, the Moon
    "deity.mrigashira": "सोम, चन्द्रमा",
    # EN: A deer's head
    "symbol.mrigashira": "मृगको टाउको",
    # EN: Rudra
    "deity.ardra": "रुद्र",
    # EN: A teardrop or diamond
    "symbol.ardra": "आँसुको थोपा वा हीरा",
    # EN: Aditi, mother of the gods
    "deity.punarvasu": "अदिति, देवताहरूकी आमा",
    # EN: A bow and quiver
    "symbol.punarvasu": "धनुष र तरकस",
    # EN: Brihaspati, guru of the gods
    "deity.pushya": "बृहस्पति, देवताहरूका गुरु",
    # EN: A cow's udder or lotus
    "symbol.pushya": "गाईको थुन वा कमल",
    # EN: The Nagas (serpent deities)
    "deity.ashlesha": "नागहरू (सर्प देवता)",
    # EN: A coiled serpent
    "symbol.ashlesha": "बेरिएको सर्प",
    # EN: The Pitris (ancestors)
    "deity.magha": "पितृहरू (पुर्खा)",
    # EN: A royal throne
    "symbol.magha": "राजसिंहासन",
    # EN: Bhaga, giver of fortune
    "deity.purva-phalguni": "भग, सौभाग्यदाता",
    # EN: The front legs of a bed
    "symbol.purva-phalguni": "खाटका अगाडिका खुट्टा",
    # EN: Aryaman, lord of friendship
    "deity.uttara-phalguni": "अर्यमा, मित्रताका अधिपति",
    # EN: The back legs of a bed
    "symbol.uttara-phalguni": "खाटका पछाडिका खुट्टा",
    # EN: Savitr, the Sun
    "deity.hasta": "सविता, सूर्य",
    # EN: A hand
    "symbol.hasta": "हात",
    # EN: Tvashtr (Vishwakarma), the divine architect
    "deity.chitra": "त्वष्टा (विश्वकर्मा), दिव्य वास्तुकार",
    # EN: A bright jewel
    "symbol.chitra": "चम्किलो रत्न",
    # EN: Vayu, the wind
    "deity.swati": "वायु, हावा",
    # EN: A young shoot swaying in the wind
    "symbol.swati": "हावामा हल्लिरहेको कलिलो बिरुवा",
    # EN: Indra and Agni (Indragni)
    "deity.vishakha": "इन्द्र र अग्नि (इन्द्राग्नि)",
    # EN: A triumphal arch
    "symbol.vishakha": "विजय तोरण",
    # EN: Mitra, lord of friendship
    "deity.anuradha": "मित्र, मित्रताका अधिपति",
    # EN: A lotus
    "symbol.anuradha": "कमल",
    # EN: Indra, king of the gods
    "deity.jyeshtha": "इन्द्र, देवताहरूका राजा",
    # EN: A circular amulet or earring
    "symbol.jyeshtha": "गोलाकार ताबिज वा कुण्डल",
    # EN: Nirriti
    "deity.mula": "निरृति",
    # EN: A bunch of roots
    "symbol.mula": "जराहरूको झुप्पो",
    # EN: Apas, the waters
    "deity.purva-ashadha": "आपः, जल",
    # EN: A winnowing fan or elephant tusk
    "symbol.purva-ashadha": "सुप्पो वा हात्तीको दाह्रा",
    # EN: The Vishvedevas (universal gods)
    "deity.uttara-ashadha": "विश्वेदेवा (सबै देवता)",
    # EN: An elephant tusk
    "symbol.uttara-ashadha": "हात्तीको दाह्रा",
    # EN: Vishnu
    "deity.shravana": "विष्णु",
    # EN: An ear, or three footprints
    "symbol.shravana": "कान, वा तीन पाइला",
    # EN: The eight Vasus
    "deity.dhanishta": "आठ वसु",
    # EN: A drum (mridanga)
    "symbol.dhanishta": "ढोल (मृदङ्ग)",
    # EN: Varuna, lord of the waters
    "deity.shatabhisha": "वरुण, जलका अधिपति",
    # EN: An empty circle
    "symbol.shatabhisha": "खाली गोलो घेरा",
    # EN: Aja Ekapada
    "deity.purva-bhadrapada": "अजैकपाद",
    # EN: Swords, or the front legs of a cot
    "symbol.purva-bhadrapada": "तरवार, वा खाटका अगाडिका खुट्टा",
    # EN: Ahir Budhnya, serpent of the deep
    "deity.uttara-bhadrapada": "अहिर्बुध्न्य, गहिरो जलका सर्प",
    # EN: The back legs of a cot, or twins
    "symbol.uttara-bhadrapada": "खाटका पछाडिका खुट्टा, वा जुम्ल्याहा",
    # EN: Pushan, the nourisher and guide
    "deity.revati": "पूषन्, पोषक र मार्गदर्शक",
    # EN: A fish (or a drum)
    "symbol.revati": "माछा (वा ढोल)",
}

# app/naam_milan_text.py TEXT["ne"] — page text of /naam-se-kundali-milan  [34]
NAAM_MILAN_TEXT = {
    # EN: Naam se Kundali Milan — Match 36 Gunas by Name, Free | {brand}
    # keep: {brand}
    "title": "नामबाट कुण्डली मिलान — 36 गुण नि:शुल्क जाँच | {brand}",
    # EN: Kundali milan by name: the first syllable of the boy's and girl's names gives each
    #     nakshatra and rashi, then the full 36-guna Ashtakoot match. Type names in Hindi or English
    #     — free, no sign-up.
    "desc": "नामबाट कुण्डली मिलान: केटा र केटीको नामको पहिलो अक्षरले नक्षत्र र राशि निर्धारण गर्छ, त्यसपछि पूरा 36 गुणको अष्टकूट मिलान हुन्छ। नाम हिन्दी वा अङ्ग्रेजीमा लेख्न सकिन्छ — नि:शुल्क, साइन-अप चाहिँदैन।",
    # EN: Naam se Kundali Milan
    "crumb": "नामबाट कुण्डली मिलान",
    # EN: <h1>Naam se Kundali Milan — Match by Name</h1>
    "h1": "<h1>नामबाट कुण्डली मिलान — नाम हेरेर गुण मिलाउनुहोस्</h1>",
    # EN: <p class="hi" lang="hi">नाम से कुंडली मिलान</p>
    "sub": "<p class=\"hi\" lang=\"ne\">नामबाट कुण्डली मिलान</p>",
    # EN: <p>When birth times are not known, tradition matches a couple by the <strong>first
    #     syllable of their names</strong>. Type both names in Hindi or English: we show the
    #     syllable used, its nakshatra pada and rashi, and the full 36-guna match.</p>
    "intro": "<p>जन्म समय थाहा नभएको खण्डमा परम्परा अनुसार जोडीको <strong>नामको पहिलो अक्षर</strong>बाट मिलान गरिन्छ। दुवैको नाम हिन्दी वा अङ्ग्रेजीमा लेख्नुहोस्: हामी प्रयोग भएको अक्षर, त्यसको नक्षत्र चरण र राशि, अनि पूरा 36 गुणको मिलान देखाउँछौँ।</p>",
    # EN: Open birth-chart Kundali Milan
    "open_milan": "जन्मकुण्डलीबाट कुण्डली मिलान खोल्नुहोस्",
    # EN: Automatic, from the name
    "auto": "नामबाट आफैँ निर्धारण भएको",
    # EN: Other likely syllables for this name
    "alt_head": "यस नामका अन्य सम्भावित अक्षरहरू",
    # EN: All 108 syllables
    "all_head": "सबै 108 अक्षर",
    # EN: Boy's name (groom)
    "boy_label": "केटाको नाम (दुलहा)",
    # EN: Girl's name (bride)
    "girl_label": "केटीको नाम (दुलही)",
    # EN: e.g. Ram or राम
    "boy_ph": "जस्तै: राम",
    # EN: e.g. Sita or सीता
    "girl_ph": "जस्तै: सीता",
    # EN: Change the first syllable
    "pick": "पहिलो अक्षर बदल्नुहोस्",
    # EN: Match the gunas
    "button": "गुण मिलाउनुहोस्",
    # EN: This syllable belongs to Abhijit, the 28th nakshatra; in the 27-nakshatra wheel it is
    #     counted in Uttara Ashadha pada 4.
    "via.abhijit": "यो अक्षर 28औँ नक्षत्र अभिजितको हो; 27 नक्षत्रको चक्रमा यसलाई उत्तराषाढा चरण 4 मा गनिन्छ।",
    # EN: By the traditional rule, ब is read as व, and श as ष (with the a-vowel) or स.
    "via.alias": "परम्परागत नियम अनुसार ब लाई व र श लाई ष (अ-स्वरसहित) वा स पढिन्छ।",
    # EN: This exact syllable is not in the 108-syllable list, so the nearest syllable with the same
    #     consonant was used — change it below if you prefer.
    "via.nearest": "यही अक्षर 108 अक्षरको सूचीमा छैन, त्यसैले समान व्यञ्जन भएको नजिकको अक्षर प्रयोग गरियो — चाहनुभयो भने तल बदल्न सक्नुहुन्छ।",
    # EN: An English spelling cannot settle this syllable (e.g. T = त or ट), so the most common
    #     reading was used — pick another below if needed.
    "via.latin": "अङ्ग्रेजी हिज्जेले यो अक्षर निश्चित गर्न सक्दैन (जस्तै T = त वा ट), त्यसैले सबैभन्दा प्रचलित पढाइ लिइएको छ — आवश्यक परे तल अर्को छान्नुहोस्।",
    # EN: You chose this syllable.
    "via.chosen": "तपाईंले यो अक्षर छान्नुभएको हो।",
    # EN: Could not read a first syllable from this name — pick one from the list below.
    "unreadable": "यो नामबाट पहिलो अक्षर पढ्न सकिएन — तलको सूचीबाट एउटा छान्नुहोस्।",
    # EN: pada
    "pada": "चरण",
    # EN: Result
    "result": "नतिजा",
    # EN: <tr><th></th><th>First syllable</th><th>Nakshatra</th><th>Rashi</th></tr>
    "res.head": "<tr><th></th><th>पहिलो अक्षर</th><th>नक्षत्र</th><th>राशि</th></tr>",
    # EN: Boy
    "boy": "केटा",
    # EN: Girl
    "girl": "केटी",
    # EN: <tr><th>Koota</th><th>Points</th><th>Why</th></tr>
    "res.th": "<tr><th>कूट</th><th>अङ्क</th><th>कारण</th></tr>",
    # EN: Total
    "total": "जम्मा",
    # EN: <strong>Mangal dosha: not applicable.</strong> Mangal dosha depends on where Mars stood
    #     from the Lagna, Moon and Venus at birth — a name cannot tell you that. Use birth-chart
    #     matching for it.
    "mangal": "<strong>मङ्गल दोष: लागू हुँदैन।</strong> मङ्गल दोष जन्मका बेला लग्न, चन्द्रमा र शुक्रबाट मङ्गल कुन भावमा थियो भन्नेमा निर्भर हुन्छ — नामले त्यो भन्न सक्दैन। त्यसका लागि जन्मकुण्डलीबाट मिलान गर्नुहोस्।",
    # EN: Match by birth details instead — more accurate, free
    "res.cta": "जन्मको विवरणबाट मिलान गर्नुहोस् — अझ सही, नि:शुल्क",
    # EN: <div class="box"><p><strong>Please note:</strong> name-based matching is a traditional
    #     shortcut, used when birth details are not known. It assumes each name was chosen from the
    #     syllable of the person's birth nakshatra — which today is often not the case. Matching
    #     from the date, time and place of birth is far more accurate, and is the only way to check
    #     Mangal dosha.</p></div>
    "caveat": "<div class=\"box\"><p><strong>ध्यान दिनुहोस्:</strong> नामबाट मिलान जन्मको विवरण थाहा नभएको बेला प्रयोग गरिने परम्परागत छोटो बाटो हो। यसले प्रत्येक व्यक्तिको नाम उसको जन्म नक्षत्रको अक्षरबाट राखिएको हो भनेर मानेर चल्छ — आजकल प्रायः त्यसो हुँदैन। जन्मको मिति, समय र स्थानबाट गरिने मिलान धेरै सही हुन्छ, र मङ्गल दोष जाँच्ने त्यही एक मात्र उपाय हो।</p></div>",
    # EN: <tr><th>Rashi</th><th>Name syllables</th></tr>
    "syl.head": "<tr><th>राशि</th><th>नामका अक्षरहरू</th></tr>",
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
    "explainer": " <h2>नामबाट मिलान कसरी काम गर्छ</h2> <p>27 वटै नक्षत्रका चार चरण हुन्छन्, र प्रत्येक चरणको एउटा अक्षर (नामाक्षर) हुन्छ — जम्मा 108। नाम जुन अक्षरबाट <strong>सुरु हुन्छ</strong>, त्यही अक्षर भएको चरणलाई ती व्यक्तिको नक्षत्र र त्यसको राशिलाई उनको चन्द्र राशि मानिन्छ। जन्मकुण्डलीसँग प्रयोग गरिने उही <strong>अष्टकूट (36 गुण)</strong> मिलान — वर्ण, वश्य, तारा, योनि, ग्रह मैत्री, गण, भकूट र नाडी — यी दुई नक्षत्रबाट गणना गरिन्छ, हाम्रो कुण्डली मिलान उपकरणको उही इन्जिनबाट।</p> <h3>पहिलो अक्षर कसरी पढिन्छ</h3> <ul> <li>पहिलो अक्षरको पहिलो व्यञ्जन र त्यसको स्वर: <strong>प्रिया → पी</strong>, <strong>क्षितिज → की</strong>। ह्रस्व र दीर्घ स्वर उस्तै गनिन्छन् (इ/ई, उ/ऊ); ऐ लाई ए र औ लाई ओ मानिन्छ।</li> <li>ब लाई व, श लाई ष (अ-स्वरसहित) वा स, र ऋ लाई री पढिन्छ।</li> <li>अभिजितका अक्षरहरू ({abhijit}) उत्तराषाढा चरण 4 मा गनिन्छन्।</li> <li>अङ्ग्रेजीमा लेखिएका नाम लिप्यन्तरण गरिन्छन्; T, D, N, Th, Dh जस्ता अक्षरले देवनागरीका दुई अक्षर (त/ट, द/ड) जनाउन सक्छन्, त्यसैले नतिजामा कुन अक्षर प्रयोग भयो देखाइन्छ र तपाईं अर्को छान्न सक्नुहुन्छ। देवनागरीमा लेखेको नाम ठ्याक्कै पढिन्छ।</li> </ul> <h3>राशि अनुसार नामका अक्षरहरू</h3> {syllables} <p>प्रत्येक नक्षत्रका अक्षर, देवता, गण र नाडी हेर्न <a href=\"{href}\">सबै 27 नक्षत्र</a> हेर्नुहोस्।</p>",
}

# app/naam_milan_text.py ENGINE["ne"] — score-band notes and the convention note of a naam-milan result  [5]
NAAM_MILAN_ENGINE = {
    # EN: Below the traditional minimum of 18 gunas.
    "band_note0": "परम्परागत न्यूनतम 18 गुणभन्दा कम।",
    # EN: In the traditional 18-24 gunas band.
    "band_note1": "परम्परागत 18-24 गुणको दायरामा।",
    # EN: In the traditional 25-32 gunas band.
    "band_note2": "परम्परागत 25-32 गुणको दायरामा।",
    # EN: In the traditional 33-36 gunas band.
    "band_note3": "परम्परागत 33-36 गुणको दायरामा।",
    # EN: The 18/25/33 guna thresholds are a widely used convention, not a measurement. Astrologers
    #     often accept a lower total if the heavily weighted kootas are free of dosha.
    "convention_note": "18/25/33 गुणको सीमा व्यापक रूपमा प्रचलित मान्यता हो, मापन होइन। भारी अङ्क भएका कूटहरूमा दोष नभए ज्योतिषीहरूले प्रायः कम जोड पनि स्वीकार गर्छन्।",
}

# ----------------------------------------------------------------------------
# muhurat   /muhurat/<kind>-<year>
# ----------------------------------------------------------------------------

# app/muhurat_text.py TEXT["ne"] — page text of /muhurat/<kind>-<year> (the mundan-only keys are MUHURAT_MUNDAN)  [37]
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
    "title": "{name} {year}: शुभ {noun_title} मितिहरू (नयाँ दिल्ली) | {brand}",
    # EN: {name} {year}: auspicious {noun} dates
    # keep: {year}
    # may also use: {name} {noun}
    "h1": "{name} {year}: शुभ {noun} मितिहरू",
    # EN: {name} {year} for New Delhi — month-by-month auspicious {noun} dates with tithi and
    #     nakshatra. {count} dates; Chaturmas, Kharmas, Adhik Maas, Pitru Paksha and Guru/Shukra
    #     asta explained.
    # keep: {count} {year}
    # may also use: {name} {noun}
    "desc": "{name} {year} नयाँ दिल्लीका लागि — तिथि र नक्षत्रसहित महिनाअनुसार शुभ {noun} मितिहरू। {count} मिति; चातुर्मास, खरमास, अधिक मास, पितृ पक्ष र गुरु/शुक्र अस्तको व्याख्यासहित।",
    # EN: <p class="hi" lang="hi">{name_hi} {year}</p>
    # keep: {year}
    # may also use: {name} {noun}
    "sub": "<p class=\"hi\" lang=\"ne\">{name} {year}</p>",
    # EN: {label} · IST
    # keep: {label}
    "place": "{label} · IST",
    # EN: <p>By the panchang there are <strong>{count}</strong> {name_lower} dates in {year} for New
    #     Delhi, in {months}. Each date passes the classical checks on the sunrise tithi, nakshatra,
    #     weekday, yoga and Bhadra, and falls outside Chaturmas, Kharmas, Adhik Maas, Pitru Paksha
    #     and the combustion (asta) of Jupiter and Venus.</p>
    # keep: {count} {months} {year}
    # may also use: {name_lower} {name} {noun}
    "intro": "<p>पञ्चाङ्ग अनुसार नयाँ दिल्लीका लागि {year} मा {months} महिनाहरूमा <strong>{count}</strong> वटा {name_lower} मिति छन्। प्रत्येक मिति सूर्योदयको तिथि, नक्षत्र, वार, योग र भद्राको शास्त्रीय जाँचमा उत्तीर्ण छ, र चातुर्मास, खरमास, अधिक मास, पितृ पक्ष तथा गुरु र शुक्रको अस्त (अस्तङ्गत) बाहिर पर्छ।</p>",
    # EN: <p><strong>Timings vary by city.</strong> These dates are reckoned from New Delhi's
    #     sunrise; elsewhere a tithi or nakshatra can change on a different day. The exact muhurat
    #     (lagna) for a wedding or griha pravesh should be fixed by your family priest. Check your
    #     own city in the Muhurat Finder.</p>
    "note": "<p><strong>समय सहरअनुसार फरक हुन्छ।</strong> यी मितिहरू नयाँ दिल्लीको सूर्योदयबाट गणना गरिएका हुन्; अन्यत्र तिथि वा नक्षत्र अर्कै दिन बदलिन सक्छ। विवाह वा गृहप्रवेशको ठ्याक्कै मुहूर्त (लग्न) तपाईंको पारिवारिक पुरोहितले तय गर्नुपर्छ। आफ्नो सहरको मुहूर्त मुहूर्त खोजकर्तामा हेर्नुहोस्।</p>",
    # EN: Find muhurat for your city — free
    "cta": "आफ्नो सहरको मुहूर्त खोज्नुहोस् — नि:शुल्क",
    # EN: {name} {year}
    # keep: {name} {year}
    "crumb": "{name} {year}",
    # EN: More muhurat dates
    "more": "थप मुहूर्त मितिहरू",
    # EN: {name} {year}
    # keep: {name} {year}
    "link.kind": "{name} {year}",
    # EN: Today's Panchang
    "link.panchang": "आजको पञ्चाङ्ग",
    # EN: Kundali Milan
    "link.milan": "कुण्डली मिलान",
    # EN: When there is no {name_lower} in {year}
    # keep: {year}
    # may also use: {name_lower} {name} {noun}
    "periods.h2": "{year} मा {name_lower} नहुने समय",
    # EN: No {name_lower} is given during these periods. The dates are computed from the panchang
    #     (New Delhi, sunrise):
    # may also use: {name_lower} {name} {noun}
    "periods.intro": "यी अवधिहरूमा {name_lower} दिइँदैन। मितिहरू पञ्चाङ्गबाट (नयाँ दिल्ली, सूर्योदय) गणना गरिएका हुन्:",
    # EN: <li><strong>{period}</strong>, {range} — {about}.</li>
    # keep: {about} {period} {range}
    "periods.item": "<li><strong>{period}</strong>, {range} — {about}।</li>",
    # EN: No {name_lower} in {month} — {periods}.
    # keep: {month} {periods}
    # may also use: {name_lower} {name} {noun}
    "none.periods": "{month} मा {name_lower} छैन — {periods}।",
    # EN: No {name_lower} in {month} — no day this month passes the tithi, nakshatra, weekday and
    #     yoga checks.
    # keep: {month}
    # may also use: {name_lower} {name} {noun}
    "none.plain": "{month} मा {name_lower} छैन — यस महिनाको कुनै दिनले तिथि, नक्षत्र, वार र योगको जाँच पार गर्दैन।",
    # EN: <tr><th>Date</th><th>Day</th><th>Tithi</th><th>Nakshatra</th></tr>
    "th": "<tr><th>मिति</th><th>वार</th><th>तिथि</th><th>नक्षत्र</th></tr>",
    # EN: Muhurat page not found
    "nf.title": "मुहूर्त पृष्ठ फेला परेन",
    # EN: Open the Muhurat Finder
    "nf.open": "मुहूर्त खोजकर्ता खोल्नुहोस्",
    # EN: Chaturmas
    "period.chaturmas": "चातुर्मास",
    # EN: Devshayani Ekadashi to Devuthani Ekadashi, when Lord Vishnu is in yoga-nidra
    "period_about.chaturmas": "देवशयनी एकादशीदेखि देवउठनी एकादशीसम्म, जब भगवान् विष्णु योगनिद्रामा हुन्छन्",
    # EN: Kharmas
    "period.kharmas": "खरमास",
    # EN: the Sun in Dhanu (Sagittarius) or Meena (Pisces)
    "period_about.kharmas": "सूर्य धनु वा मीन राशिमा हुने समय",
    # EN: Adhik Maas
    "period.adhik_maas": "अधिक मास",
    # EN: an intercalary lunar month with no solar ingress
    "period_about.adhik_maas": "सूर्य सङ्क्रान्ति नपर्ने अतिरिक्त चान्द्र महिना",
    # EN: Pitru Paksha
    "period.pitru_paksha": "पितृ पक्ष",
    # EN: Bhadrapada Purnima to Sarva Pitru Amavasya, the fortnight of shraddha
    "period_about.pitru_paksha": "भाद्र पूर्णिमादेखि सर्वपितृ औंसीसम्म, श्राद्धको पक्ष",
    # EN: Shukra Asta
    "period.shukra_asta": "शुक्र अस्त",
    # EN: Venus combust (too close to the Sun to be seen), with 3 days either side
    "period_about.shukra_asta": "शुक्र अस्त (सूर्यको अति नजिक भएकाले नदेखिने), दुवैतिर 3 दिनसहित",
    # EN: Guru Asta
    "period.guru_asta": "गुरु अस्त",
    # EN: Jupiter combust (too close to the Sun to be seen), with 3 days either side
    "period_about.guru_asta": "बृहस्पति अस्त (सूर्यको अति नजिक भएकाले नदेखिने), दुवैतिर 3 दिनसहित",
}

# app/muhurat_text.py MUNDAN["ne"] — the mundan (first haircut) muhurat's own wording  [5]
MUHURAT_MUNDAN = {
    # EN: Mundan Muhurat
    "kind.mundan": "मुण्डन मुहूर्त",
    # EN: mundan
    "noun.mundan": "मुण्डन",
    # EN: <p><strong>Timings vary by city.</strong> These dates are reckoned from New Delhi's
    #     sunrise; elsewhere a tithi or nakshatra can change on a different day. The exact muhurat
    #     for the mundan (chudakarma) should be fixed by your family priest. Check your own city in
    #     the Muhurat Finder.</p>
    "note.mundan": "<p><strong>समय सहरअनुसार फरक हुन्छ।</strong> यी मितिहरू नयाँ दिल्लीको सूर्योदयबाट गणना गरिएका हुन्; अन्यत्र तिथि वा नक्षत्र अर्कै दिन बदलिन सक्छ। मुण्डन (चूडाकरण) को ठ्याक्कै मुहूर्त तपाईंको पारिवारिक पुरोहितले तय गर्नुपर्छ। आफ्नो सहरको मुहूर्त मुहूर्त खोजकर्तामा हेर्नुहोस्।</p>",
    # EN: {name} {year}: the rules these dates follow
    # keep: {name} {year}
    "rules.h2": "{name} {year}: यी मितिहरूले पालना गर्ने नियम",
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
    "rules.body": "<p>मुण्डन (चूडाकरण, पहिलो कपाल काट्ने संस्कार) विवाहको भन्दा आफ्नै नियमले हेरिन्छ। तल दिइएका वर्जित कुनै पनि नपरेको र शुभ नक्षत्रमा परेको दिन मात्र सूचीमा राखिन्छ:</p><ul><li><strong>वर्जित तिथि:</strong> {tithi_bad}।</li><li><strong>शुभ तिथि</strong> (दुवै पक्षमा): {tithi_good}; अरू सामान्य हुन्।</li><li><strong>शुभ नक्षत्र</strong> (तलका सबै मिति यीमध्ये कुनैमा पर्छन्): {nak_good}।</li><li><strong>वर्जित नक्षत्र:</strong> {nak_bad}।</li><li><strong>वर्जित योग र करण:</strong> {yoga_bad}, र भद्रा (विष्टि)।</li><li><strong>वार:</strong> {vara_good} शुभ मानिन्छन्; {vara_bad} ले दिनलाई पूरै अयोग्य नबनाए पनि प्रतिकूल गनिन्छ, त्यसैले यस्ता केही मिति देखिन सक्छन् - तपाईंको परिवारले ती वार मान्दैन भने छोड्नुहोस्।</li></ul>",
}

# app/muhurat_text.py MONTHS["ne"] — only if this page must spell the months differently from names_<code>.MONTHS; else leave ()  [12]
# (optional: may stay empty)
MUHURAT_MONTHS = ()   # or 12 month names, January first

# ----------------------------------------------------------------------------
# recurring /purnima-<year> /amavasya-<year> /pradosh-vrat-<year> ... (DIVASTRO-141)
# ----------------------------------------------------------------------------

# app/recurring_text.py TEXT["ne"] — page text of /purnima-<year>, /amavasya-<year>, /pradosh-vrat-<year> ... (the keys it shares with VRAT_TEXT are taken from there)  [60]
RECURRING_TEXT = {
    # EN: Full Moon Dates and Tithi Time
    "what.purnima": "पूर्णिमाका मिति र तिथि समय",
    # EN: New Moon Dates and Tithi Time
    "what.amavasya": "औंसीका मिति र तिथि समय",
    # EN: All Dates and Pradosh Puja Time
    "what.pradosh": "सबै मिति र प्रदोष पूजा समय",
    # EN: All Dates and Moonrise Time
    "what.sankashti": "सबै मिति र चन्द्रोदय समय",
    # EN: All Dates and Nishita Puja Time
    "what.masik_shivratri": "सबै मिति र निशीथ पूजा समय",
    # EN: All Dates and Kala Bhairav Puja
    "what.kalashtami": "सबै मिति र कालभैरव पूजा",
    # EN: {name} {year}: {what} (New Delhi)
    # keep: {name} {what} {year}
    "title": "{name} {year}: {what} (नयाँ दिल्ली)",
    # EN: {name} {year}: {what}
    # keep: {name} {what} {year}
    "h1": "{name} {year}: {what}",
    # EN: All {count} {name} dates in {year} with weekday, Hindu month and tithi start and end for
    #     New Delhi. {about}{keytime}{next}
    # keep: {about} {count} {keytime} {name} {next} {year}
    "desc": "{year} का सबै {count} {name} मिति — नयाँ दिल्लीका लागि वार, हिन्दू महिना र तिथि सुरु तथा अन्त्यसहित। {about}{keytime}{next}",
    # EN: Full-moon vrat days for Satyanarayan puja, bathing and charity.
    "desc.about.purnima": "सत्यनारायण पूजा, स्नान र दानका लागि पूर्णिमा व्रतका दिन।",
    # EN: New-moon days for shraddha and tarpan, with Somvati and Shani Amavasya.
    "desc.about.amavasya": "श्राद्ध र तर्पणका लागि औंसीका दिन, सोमवती र शनि औंसीसहित।",
    # EN: Lord Shiva's twilight fast on Trayodashi, with the puja window.
    "desc.about.pradosh": "त्रयोदशीमा भगवान् शिवको साँझको व्रत, पूजा समयसहित।",
    # EN: Lord Ganesha's fast on Krishna Chaturthi, broken after moonrise.
    "desc.about.sankashti": "कृष्ण चतुर्थीमा भगवान् गणेशको व्रत, चन्द्रोदयपछि खोलिने।",
    # EN: The monthly night of Shiva on Krishna Chaturdashi, with the midnight puja.
    "desc.about.masik_shivratri": "कृष्ण चतुर्दशीमा शिवको मासिक रात, मध्यरातको पूजासहित।",
    # EN: Kala Bhairava worship on Krishna Ashtami, every month.
    "desc.about.kalashtami": "हरेक महिना कृष्ण अष्टमीमा कालभैरवको पूजा।",
    # EN: Includes {label}.
    # keep: {label}
    "desc.key": " {label} समावेश छ।",
    # EN: Next: {date}.
    # keep: {date}
    "desc.next": " अर्को: {date}।",
    # EN: The next {name} is on <strong>{when}</strong> ({details}).
    # keep: {details} {name} {when}
    "ans.next": "अर्को {name} <strong>{when}</strong> मा पर्छ ({details})।",
    # EN: The first {name} of {year} is on <strong>{when}</strong> ({details}). All {count} dates
    #     for {year} are listed below.
    # keep: {count} {details} {name} {when} {year}
    "ans.first": "{year} को पहिलो {name} <strong>{when}</strong> मा पर्छ ({details})। {year} का सबै {count} मिति तल सूचीबद्ध छन्।",
    # EN: All {count} {name} dates for {year} are listed below; the last was on
    #     <strong>{when}</strong>.
    # keep: {count} {name} {when} {year}
    "ans.past": "{year} का सबै {count} {name} मिति तल सूचीबद्ध छन्; अन्तिम <strong>{when}</strong> मा थियो।",
    # EN: Dates for {year}: {link}.
    # keep: {link} {year}
    "ans.more": " {year} का मितिहरू: {link}।",
    # EN: {name} {year}: all dates
    # keep: {name} {year}
    "table.h2": "{name} {year}: सबै मितिहरू",
    # EN: Date
    "th.date": "मिति",
    # EN: Hindu month
    "th.month": "हिन्दू महिना",
    # EN: Tithi
    "th.tithi": "तिथि",
    # EN: Adhik {month}
    # keep: {month}
    "adhika": "अधिक {month}",
    # EN: Also:
    "also": "साथै: ",
    # EN: <p class="note"><small>Months are amanta (a month ends on Amavasya, as in South and West
    #     India). North Indian purnimanta calendars name the dark fortnight one month
    #     later.</small></p>
    "months.note": "<p class=\"note\"><small>महिनाहरू अमान्त हुन् (दक्षिण र पश्चिम भारतझैँ महिना औंसीमा सकिन्छ)। उत्तर भारतका पूर्णिमान्त पात्रोले कृष्ण पक्षलाई एक महिना पछिको नाम दिन्छन्।</small></p>",
    # EN: Som Pradosh
    "variant.pradosh.0": "सोम प्रदोष",
    # EN: Bhauma Pradosh
    "variant.pradosh.1": "भौम प्रदोष",
    # EN: Shani Pradosh
    "variant.pradosh.5": "शनि प्रदोष",
    # EN: Angarki Chaturthi
    "variant.sankashti.1": "अङ्गारकी चतुर्थी",
    # EN: Somvati Amavasya
    "variant.amavasya.0": "सोमवती औंसी",
    # EN: Shani Amavasya
    "variant.amavasya.5": "शनि औंसी",
    # EN: What {name} is and how it is observed
    # keep: {name}
    "about.h2": "{name} के हो र कसरी मनाइन्छ",
    # EN: Panchang for your city
    "city.h2": "तपाईंको सहरको पञ्चाङ्ग",
    # EN: Related dates and calendars
    "related.h2": "सम्बन्धित मिति र पात्रोहरू",
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
    "about.purnima": "<p>पूर्णिमा चन्द्रमा पूर्ण देखिने तिथि हो, शुक्ल पक्षको अन्तिम (15औँ) तिथि, जब चन्द्रमा सूर्यको ठीक विपरीत हुन्छ। भक्तजन व्रत बस्छन्, बिहानै (सकेसम्म नदी वा तीर्थमा) स्नान गर्छन्, भगवान् विष्णुको पूजा गर्छन् - सत्यनारायण कथा पूर्णिमाको प्रचलित पूजा हो - र साँझ चन्द्रमालाई अर्घ्य दिन्छन्। यस दिन अन्न, वस्त्र वा धनको दान गरे पुण्य धेरै गुणा हुन्छ भनिन्छ।</p><p>केही पूर्णिमा आफैँमा पर्व हुन्: गुरु पूर्णिमा, शरद पूर्णिमा, कार्तिक पूर्णिमा र बुद्ध पूर्णिमा, र फाल्गुनको पूर्णिमामा होलिका दहन गरिन्छ।</p>",
    # EN: <p>Amavasya is the new-moon tithi, the 30th and last tithi of the dark fortnight (Krishna
    #     paksha), when the Moon is in conjunction with the Sun and cannot be seen. It is the day of
    #     the ancestors (pitru): families offer tarpan and shraddha, feed Brahmins and the poor,
    #     give in charity and bathe in holy water. Many people fast and avoid starting anything
    #     new.</p><p>An Amavasya on a Monday is called Somvati Amavasya and one on a Saturday Shani
    #     Amavasya, both given extra weight. The great Amavasyas are Mauni Amavasya, Sarva Pitru
    #     Amavasya (the end of Pitru Paksha) and the Amavasya of Diwali.</p>
    "about.amavasya": "<p>औंसी चन्द्रमा नदेखिने तिथि हो, कृष्ण पक्षको 30औँ र अन्तिम तिथि, जब चन्द्रमा सूर्यसँग एउटै ठाउँमा हुन्छ। यो पितृ (पूर्वज) को दिन हो: परिवारले तर्पण र श्राद्ध गर्छन्, ब्राह्मण र गरिबलाई भोजन गराउँछन्, दान दिन्छन् र पवित्र जलमा स्नान गर्छन्। धेरैले व्रत बस्छन् र नयाँ काम सुरु गर्नबाट टाढा रहन्छन्।</p><p>सोमबार पर्ने औंसीलाई सोमवती औंसी र शनिबार पर्नेलाई शनि औंसी भनिन्छ, दुवैलाई विशेष महत्त्व दिइन्छ। मुख्य औंसीहरू मौनी औंसी, सर्वपितृ औंसी (पितृ पक्षको अन्त्य) र दीपावलीको औंसी हुन्।</p>",
    # EN: <p>Pradosh Vrat is the fast of Lord Shiva kept on Trayodashi, the 13th tithi, of both
    #     fortnights - so twice a month. Pradosh kaal is the twilight window just after sunset, when
    #     Shiva is believed to be most pleased. Devotees fast through the day, bathe, and do Shiva
    #     puja in the Pradosh window: abhishek with water, milk and bilva (bel) leaves, a lamp and
    #     the Pradosh stotra or Shiva Chalisa. The fast is broken after the puja.</p><p>A Pradosh on
    #     Monday is Som Pradosh, on Tuesday Bhauma Pradosh and on Saturday Shani Pradosh; the
    #     Saturday one is considered especially powerful.</p>
    "about.pradosh": "<p>प्रदोष व्रत दुवै पक्षको त्रयोदशी (13औँ तिथि) मा गरिने भगवान् शिवको व्रत हो - अर्थात् महिनामा दुई पटक। प्रदोष काल सूर्यास्तपछिको साँझको समय हो, जब शिव सबैभन्दा प्रसन्न हुन्छन् भन्ने विश्वास छ। भक्तजन दिनभर व्रत बस्छन्, स्नान गर्छन् र प्रदोष कालमा शिवपूजा गर्छन्: जल, दूध र बेलपत्रले अभिषेक, दीप र प्रदोष स्तोत्र वा शिव चालिसा। पूजापछि व्रत खोलिन्छ।</p><p>सोमबार पर्ने प्रदोष सोम प्रदोष, मङ्गलबार भौम प्रदोष र शनिबार शनि प्रदोष हो; शनिबारको प्रदोष विशेष शक्तिशाली मानिन्छ।</p>",
    # EN: <p>Sankashti Chaturthi (Sankat Hara Chaturthi) is the monthly fast of Lord Ganesha on
    #     Chaturthi, the 4th tithi, of the dark fortnight (Krishna paksha); "sankashti" means
    #     deliverance from trouble. Devotees fast through the day, worship Ganesha in the evening
    #     and break the fast only after seeing the Moon and offering it arghya, which is why
    #     moonrise is the key time on this page.</p><p>A Sankashti on a Tuesday is Angarki Sankashti
    #     Chaturthi, believed to be especially fruitful. The Sankashti of Magha (purnimanta) is kept
    #     in North India as Sakat Chauth.</p>
    "about.sankashti": "<p>सङ्कष्टी चतुर्थी (सङ्कटहरा चतुर्थी) कृष्ण पक्षको चतुर्थी (4औँ तिथि) मा गरिने भगवान् गणेशको मासिक व्रत हो; \"सङ्कष्टी\" को अर्थ सङ्कटबाट मुक्ति हो। भक्तजन दिनभर व्रत बस्छन्, साँझ गणेशको पूजा गर्छन् र चन्द्रमा देखेर अर्घ्य दिएपछि मात्र व्रत खोल्छन्, त्यसैले यो पृष्ठमा चन्द्रोदय मुख्य समय हो।</p><p>मङ्गलबार पर्ने सङ्कष्टी अङ्गारकी सङ्कष्टी चतुर्थी हो, जसलाई विशेष फलदायी मानिन्छ। माघ (पूर्णिमान्त) को सङ्कष्टी उत्तर भारतमा सकट चौथका रूपमा मनाइन्छ।</p>",
    # EN: <p>Masik Shivratri (monthly Shivratri) is the night of Lord Shiva kept on Chaturdashi, the
    #     14th tithi, of the dark fortnight (Krishna paksha) every month. Devotees fast and keep
    #     vigil through the night, bathing the Shiva linga with water, milk, honey and bilva leaves
    #     and chanting "Om Namah Shivaya". The best time for the puja is Nishita kaal, the midnight
    #     window.</p><p>Maha Shivratri, which falls on Krishna Chaturdashi of Phalguna (Magha in the
    #     amanta calendar), is the greatest of the twelve.</p>
    "about.masik_shivratri": "<p>मासिक शिवरात्रि हरेक महिना कृष्ण पक्षको चतुर्दशी (14औँ तिथि) मा मनाइने भगवान् शिवको रात हो। भक्तजन व्रत बसेर रातभर जागरण गर्छन्, शिवलिङ्गमा जल, दूध, मह र बेलपत्र चढाउँछन् र \"ॐ नमः शिवाय\" जप गर्छन्। पूजाको उत्तम समय निशीथ काल, अर्थात् मध्यरातको समय हो।</p><p>फाल्गुन (अमान्त पात्रोमा माघ) को कृष्ण चतुर्दशीमा पर्ने महाशिवरात्रि बाह्रमध्ये सबैभन्दा ठूलो हो।</p>",
    # EN: <p>Kalashtami (Kala Ashtami) is the monthly day of Lord Kala Bhairava, the fierce form of
    #     Shiva who guards time, kept on Ashtami, the 8th tithi, of the dark fortnight (Krishna
    #     paksha). Devotees fast, worship Bhairava at night with a mustard-oil lamp and offerings
    #     such as black sesame, and feed dogs, which are associated with him.</p><p>The Kalashtami
    #     of Margashirsha in the purnimanta calendar (Kartika in the amanta calendar) is
    #     Kalabhairava Jayanti, his appearance day and the most important of the year.</p>
    "about.kalashtami": "<p>कालाष्टमी (काल अष्टमी) हरेक महिना कृष्ण पक्षको अष्टमी (8औँ तिथि) मा पर्ने भगवान् कालभैरवको दिन हो, जो समयका रक्षक शिवका उग्र रूप हुन्। भक्तजन व्रत बस्छन्, रातमा तोरीको तेलको दीप र कालो तिल जस्ता चढाउने वस्तुसहित भैरवको पूजा गर्छन्, र उनीसँग जोडिएका कुकुरलाई खुवाउँछन्।</p><p>पूर्णिमान्त पात्रोको मङ्सिर (अमान्तमा कार्तिक) को कालाष्टमी कालभैरव जयन्ती हो, उनको प्राकट्य दिन र वर्षको सबैभन्दा महत्त्वपूर्ण।</p>",
    # EN: Purnima can begin one evening and end the next afternoon, so the day the tithi starts and
    #     the day of the vrat can differ. The rule settles it: the vrat goes to the day on which the
    #     tithi covers Madhyahna (the middle fifth of the daytime); if it covers Madhyahna on both
    #     days, the earlier day is taken. Some traditions use the sunrise tithi for the holy bath
    #     and charity instead; the table gives the start and end of the tithi so you can check.
    "note.purnima": "पूर्णिमा एक साँझ सुरु भई अर्को दिनको दिउँसो सकिन सक्छ, त्यसैले तिथि सुरु हुने दिन र व्रतको दिन फरक पर्न सक्छ। नियमले यसलाई टुङ्ग्याउँछ: तिथिले मध्याह्न (दिनको बीचको पाँचौँ भाग) लाई छोएको दिन व्रत पर्छ; दुवै दिन मध्याह्न छोए अघिल्लो दिन लिइन्छ। केही परम्पराले पवित्र स्नान र दानका लागि सूर्योदयको तिथि लिन्छन्; तपाईंले जाँच्न सक्नुहोस् भनेर तालिकाले तिथिको सुरु र अन्त्य दिन्छ।",
    # EN: Amavasya is a daytime observance (shraddha and tarpan are done in the day), so the date is
    #     the day on which the Amavasya tithi is running at sunrise. The tithi often starts the
    #     evening before, so the times in the table can begin on the previous date. Festival
    #     Amavasyas follow their own rules - Diwali is fixed by Pradosh, Sarva Pitru Amavasya by
    #     Aparahna - and can fall a day away from the date here.
    "note.amavasya": "औंसी दिउँसो गरिने कर्म हो (श्राद्ध र तर्पण दिनमा गरिन्छ), त्यसैले मिति सूर्योदयमा औंसी तिथि चलिरहेको दिन हो। तिथि प्रायः अघिल्लो साँझ सुरु हुन्छ, त्यसैले तालिकाका समय अघिल्लो मितिदेखि सुरु हुन सक्छन्। पर्वका औंसीहरू आफ्नै नियम मान्छन् - दीपावली प्रदोषले, सर्वपितृ औंसी अपराह्नले तय हुन्छ - र यहाँको मितिभन्दा एक दिन फरक पर्न सक्छन्।",
    # EN: The date is decided in the evening, not at sunrise: the vrat goes to the day on which
    #     Trayodashi is running in Pradosh kaal after sunset, so a Trayodashi that starts at noon
    #     and ends the next afternoon is kept on the first day. If the tithi touches Pradosh kaal on
    #     two evenings, the earlier evening is taken. The puja window in the table starts at sunset
    #     in New Delhi, so it moves through the year and from city to city.
    "note.pradosh": "मिति सूर्योदयमा होइन, साँझमा तय हुन्छ: सूर्यास्तपछिको प्रदोष कालमा त्रयोदशी चलिरहेको दिन व्रत पर्छ, त्यसैले दिउँसो सुरु भई अर्को दिनको दिउँसो सकिने त्रयोदशी पहिलो दिन मनाइन्छ। दुई साँझ तिथिले प्रदोष काल छोए अघिल्लो साँझ लिइन्छ। तालिकाको पूजा समय नयाँ दिल्लीको सूर्यास्तबाट सुरु हुन्छ, त्यसैले यो वर्षभर र सहरअनुसार सर्छ।",
    # EN: Sankashti is decided by the Moon, not the Sun: the vrat goes to the evening on which
    #     Chaturthi is running at moonrise, since that is when the fast is broken. The date can
    #     therefore differ from the Chaturthi date of a Panchang that goes by sunrise. Moonrise is
    #     roughly 50 minutes later each day and differs by several minutes between cities, so check
    #     it for your own city.
    "note.sankashti": "सङ्कष्टी सूर्यले होइन, चन्द्रमाले तय गर्छ: चन्द्रोदयमा चतुर्थी चलिरहेको साँझ व्रत पर्छ, किनकि त्यही बेला व्रत खोलिन्छ। त्यसैले सूर्योदयअनुसार चल्ने पञ्चाङ्गको चतुर्थी मितिभन्दा मिति फरक पर्न सक्छ। चन्द्रोदय हरेक दिन झन्डै 50 मिनेट ढिलो हुन्छ र सहरहरू बीच केही मिनेट फरक पर्छ, त्यसैले आफ्नो सहरको जाँच गर्नुहोस्।",
    # EN: This is a midnight observance, so the date is the day on which Chaturdashi is running at
    #     Nishita kaal (the 8th of the 15 muhurtas of the night, around midnight). Nishita can fall
    #     just after 12 o'clock, in which case the puja is done in the early hours of the next date
    #     and the time shown carries that date. If the tithi touches Nishita on two nights, the
    #     earlier night is taken.
    "note.masik_shivratri": "यो मध्यरातको अनुष्ठान हो, त्यसैले मिति निशीथ काल (रातका 15 मुहूर्तमध्ये 8औँ, मध्यरातको वरिपरि) मा चतुर्दशी चलिरहेको दिन हो। निशीथ 12 बजेपछि पर्न सक्छ, त्यस अवस्थामा पूजा अर्को मितिको तडकेमा हुन्छ र देखाइएको समयले त्यही मिति बोक्छ। दुई रात तिथिले निशीथ छोए अघिल्लो रात लिइन्छ।",
    # EN: Kalashtami is a night worship, so the date is the day on which Ashtami is running in
    #     Pradosh kaal (the evening window after sunset); the tithi may begin the previous morning
    #     or end during the night, so check its start and end times in the table. If it touches
    #     Pradosh kaal on two evenings, the earlier evening is taken. Some traditions go by the
    #     midnight tithi instead, which can occasionally differ by a day.
    "note.kalashtami": "कालाष्टमी रातको पूजा हो, त्यसैले मिति प्रदोष काल (सूर्यास्तपछिको साँझको समय) मा अष्टमी चलिरहेको दिन हो; तिथि अघिल्लो बिहान सुरु भई रातमै सकिन सक्छ, त्यसैले तालिकामा त्यसको सुरु र अन्त्य समय हेर्नुहोस्। दुई साँझ प्रदोष काल छोए अघिल्लो साँझ लिइन्छ। केही परम्पराले मध्यरातको तिथि हेर्छन्, जसले कहिलेकाहीँ एक दिन फरक पार्न सक्छ।",
    # EN: What are the {name} dates in {year}?
    # keep: {name} {year}
    "faq.all_q": "{year} मा {name} कुन-कुन मितिमा पर्छन्?",
    # EN: There are {count} {name} dates in {year} (New Delhi): {dates}.
    # keep: {count} {dates} {name} {year}
    "faq.all_a": "{year} मा {name} का {count} मिति छन् (नयाँ दिल्ली): {dates}।",
    # EN: When is the next {name}?
    # keep: {name}
    "faq.next_q": "अर्को {name} कहिले हो?",
    # EN: When is the first {name} of {year}?
    # keep: {name} {year}
    "faq.first_q": "{year} को पहिलो {name} कहिले हो?",
    # EN: {name} is on {when} ({details}).
    # keep: {details} {name} {when}
    "faq.on_a": "{name} {when} मा पर्छ ({details})।",
    # EN: What is the {label} on {name} {short}?
    # keep: {label} {name} {short}
    "faq.key_q": "{short} को {name} को {label} कति बजे हो?",
    # EN: At what time does the {name} tithi start and end on {short}?
    # keep: {name} {short}
    "faq.tithi_q": "{short} मा {name} तिथि कति बजे सुरु हुन्छ र कति बजे सकिन्छ?",
    # EN: How is the {name} date decided?
    # keep: {name}
    "faq.why_q": "{name} को मिति कसरी तय हुन्छ?",
    # EN: The date follows the rule: {rule}. In {year} this gives {count} dates (New Delhi).
    # keep: {count} {rule} {year}
    "faq.why_a": "मिति यो नियम अनुसार तय हुन्छ: {rule}। {year} मा यसले {count} मिति दिन्छ (नयाँ दिल्ली)।",
    # EN: Monthly vrat dates
    "hub.h2": "मासिक व्रतका मितिहरू",
}

# ----------------------------------------------------------------------------
# hub       /sitemap
# ----------------------------------------------------------------------------

# app/hub_text.py LABELS["ne"] — section names of the crawlable /sitemap page and the footer link block  [19]
HUB_LABELS = {
    # EN: Site map
    "sitemap": "साइट नक्सा",
    # EN: Panchang
    "panchang": "पञ्चाङ्ग",
    # EN: Rashifal (daily horoscope)
    "rashifal": "राशिफल (दैनिक भविष्यफल)",
    # EN: Vrat &amp; festivals
    "vrat": "व्रत र चाडपर्व",
    # EN: Shubh muhurat
    "muhurat": "शुभ मुहूर्त",
    # EN: Nakshatra
    "nakshatra": "नक्षत्र",
    # EN: Rashi (zodiac signs)
    "rashi": "राशि (बाह्र राशि)",
    # EN: Kathas
    "katha": "कथाहरू",
    # EN: Free tools
    "tools": "निःशुल्क उपकरणहरू",
    # EN: Kundali Milan
    "milan": "कुण्डली मिलान",
    # EN: Free Kundali
    "kundali": "निःशुल्क कुण्डली",
    # EN: Rahu Kaal
    "rahu": "राहुकाल",
    # EN: Choghadiya
    "choghadiya": "चौघडिया",
    # EN: Naam se Kundali Milan
    "naam": "नामबाट कुण्डली मिलान",
    # EN: Today's Panchang by city
    "cities": "सहर अनुसार आजको पञ्चाङ्ग",
    # EN: Rashifal by sign
    "signs": "राशि अनुसार राशिफल",
    # EN: Vrat and festival calendars
    "years": "व्रत र चाडपर्वका पात्रो",
    # EN: Ekadashi
    "ekadashi": "एकादशी",
    # EN: Every section of Divine Astro in one place: daily Panchang for Indian cities, Rashifal,
    #     vrat and festival dates, shubh muhurat, nakshatra and rashi guides, kathas and the free
    #     tools.
    "intro": "Divine Astro का सबै खण्ड एकै ठाउँमा: भारतीय सहरहरूको दैनिक पञ्चाङ्ग, राशिफल, व्रत र चाडपर्वका मिति, शुभ मुहूर्त, नक्षत्र र राशि मार्गदर्शन, कथाहरू र निःशुल्क उपकरणहरू।",
}

# ----------------------------------------------------------------------------
# app       AI-narration vocabulary here; names_<code>.py and static/i18n/<code>.json beside it
# ----------------------------------------------------------------------------

# app/astro_terms.py TERMS["ne"] — house / dasha / sign vocabulary for the AI narration and the chart labels  [16]
ASTRO_TERMS = {
    # EN: house
    "house": "भाव",
    # EN: sign
    "sign": "राशि",
    # EN: lord
    "lord": "स्वामी",
    # EN: dasha
    "dasha": "दशा",
    # EN: mahadasha
    "mahadasha": "महादशा",
    # EN: antardasha
    "antardasha": "अन्तर्दशा",
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
    "own sign": "स्वराशि",
    # EN: Sade Sati
    "Sade Sati": "साढेसाती",
    # EN: Navamsa
    "Navamsa": "नवांश",
    # EN: yoga
    "yoga": "योग",
    # EN: remedy
    "remedy": "उपाय",
}

# app/astro_terms.py MONTH_VARIANTS["ne"] — other spellings of a Gregorian month the AI may write (month number -> spellings)
# (optional: may stay empty)
ASTRO_MONTHS = {}   # {month number: (other spellings,)}, e.g. {2: ("...",)}
