"""Gujarati (ગુજરાતી, Gujarati script) — the data a translator fills (DIVASTRO-143).

This file is the ONLY place the gu text of the shared tables is edited; app/lang_data merges it
into them at import time, as if it were written in app/seo_text.py and friends.

  python -m app.lang_data check gu      what is left, per table (exit 0 = complete)
  python -m app.lang_data skeleton gu --force   regenerate (DISCARDS your edits)

Rules: every key below stays; a value "" means "not translated yet" (English shows, the
checker complains). Keep every {placeholder} the comment lists under `keep:`; the word order
is yours. HTML values keep their tags (write &amp; for &). Astrology names (tithi, nakshatra,
rashi, graha ...) are not here: they are in app/astro/names_gu.py. Digits are ASCII, as in
the other languages. Full instructions: docs/lang-agent-brief.md.

Set READY when a whole page module is complete, and only then — an unfinished module in READY
fails `check` and CI. A module that is not READY renders the English body, noindex.
"""

from __future__ import annotations

# Page modules that are complete for this language (the table groups below):
#   "seo" "rashifal" "vrat" "nakshatra" "muhurat" "recurring" "hub" "app"
READY = frozenset({"seo", "rashifal", "vrat", "nakshatra", "muhurat", "recurring", "hub", "app"})

# Latin-script words the gu text may keep besides the defaults (WhatsApp, UPI, PDF ...).
ALLOW_LATIN = frozenset()

# static/i18n/gu.json keys whose value is deliberately the English word (brand names, "OK").
KEEP_ENGLISH = frozenset()

# Namakshar syllables are Devanagari in the engine; this maps a letter to this script:
# (Unicode block start, {Devanagari letter: this script's letter where the offset is wrong}).
# Already set — `check` verifies all 108 syllables come out in the gu script.
AKSHAR = (0x0A80, {})


# ----------------------------------------------------------------------------
# seo       /panchang /rahu-kaal /choghadiya /kundali-milan /free-kundali + shared chrome, cities
# ----------------------------------------------------------------------------

# app/seo_text.py TEXT["gu"] — page text of /panchang /rahu-kaal /choghadiya /kundali-milan /free-kundali  [134]
SEO_TEXT = {
    # EN: Panchang
    "tool.panchang": "પંચાંગ",
    # EN: Rahu Kaal
    "tool.rahu-kaal": "રાહુકાળ",
    # EN: Choghadiya
    "tool.choghadiya": "ચોઘડિયાં",
    # EN: {vara}, {date} · {place} · IST
    # keep: {date} {place} {vara}
    "when": "{vara}, {date} · {place} · ભારતીય સમય",
    # EN: {name} until {time}
    # keep: {name} {time}
    "limb.until": "{name} {time} સુધી",
    # EN: then {name}
    # keep: {name}
    "limb.then": "પછી {name}",
    # EN: pada
    "limb.pada": "ચરણ",
    # EN: {paksha} paksha
    # keep: {paksha}
    "paksha.full": "{paksha} પક્ષ",
    # EN: {tool} in other cities
    # keep: {tool}
    "cities.heading": "અન્ય શહેરોમાં {tool}",
    # EN: More free tools
    "links.heading": "વધુ મફત સાધનો",
    # EN: {tool} in {city}
    # keep: {city} {tool}
    "links.tool_in_city": "{city}માં {tool}",
    # EN: Kundali Milan (36 guna)
    "links.milan": "કુંડળી મિલન (36 ગુણ)",
    # EN: Free Janam Kundali
    "links.kundali": "મફત જન્મકુંડળી",
    # EN: Muhurat Finder
    "links.muhurat": "શુભ મુહૂર્ત શોધો",
    # EN: Today's Rashifal
    "links.rashifal": "આજનું રાશિફળ",
    # EN: Today's Vrat & Festivals in {city}
    # keep: {city}
    "links.vrat": "{city}માં આજનાં વ્રત અને તહેવાર",
    # EN: City not found — {brand}
    # keep: {brand}
    "nf.title": "શહેર મળ્યું નથી — {brand}",
    # EN: {tool} city not found.
    # keep: {tool}
    "nf.desc": "{tool}: આ શહેર અમારી યાદીમાં નથી.",
    # EN: <h1>{tool}: city not found</h1><p>We don't have a page for “{slug}” yet. Pick a city
    #     below, or <a href="{app}">open the {tool} tool</a> to use any place in the world.</p>
    # keep: {app} {slug} {tool}
    "nf.body": "<h1>{tool}: શહેર મળ્યું નથી</h1><p>“{slug}” માટે અમારી પાસે હજી કોઈ પેજ નથી. નીચેથી કોઈ શહેર પસંદ કરો, અથવા <a href=\"{app}\">{tool} ખોલો</a> — તેમાં દુનિયાનું કોઈ પણ સ્થળ પસંદ કરી શકાય છે.</p>",
    # EN: Today's Panchang in {city}, {date} — Tithi, Nakshatra, Rahu Kaal | {brand}
    # keep: {brand} {city} {date}
    "p.title": "{city}માં આજનું પંચાંગ, {date} — તિથિ, નક્ષત્ર, રાહુકાળ | {brand}",
    # EN: Aaj ka Panchang for {city} on {vara}, {date}: {tithi} tithi ({paksha} paksha), {nakshatra}
    #     nakshatra, sunrise {sunrise}, Rahu Kaal {rahu}. Computed with Swiss Ephemeris.
    # keep: {city} {date} {nakshatra} {rahu} {sunrise} {tithi} {vara}
    # may also use: {paksha_full} {paksha}
    "p.desc": "{city}નું {vara}, {date}નું પંચાંગ: {paksha} {tithi}, ચંદ્ર {nakshatra} નક્ષત્રમાં, સૂર્યોદય {sunrise}, રાહુકાળ {rahu}. સ્વિસ એફેમેરિસથી ચોક્કસ ગણતરી.",
    # EN: <h1>Today's Panchang in {city}</h1>
    # keep: {city}
    "p.h1": "<h1>{city}નું આજનું પંચાંગ</h1>",
    # EN: <p class="hi" lang="hi">आज का पंचांग — {city_hi}</p>
    # keep: {city}
    "p.sub": "<p class=\"hi\">તિથિ, નક્ષત્ર, યોગ, કરણ અને રાહુકાળ — {city}</p>",
    # EN: <div class="box"><p>Today in {city} is <strong>{paksha} {tithi}</strong> with the Moon in
    #     <strong>{nakshatra}</strong> nakshatra. Rahu Kaal runs <strong>{rahu}</strong> — avoid
    #     starting anything new in that window.</p></div>
    # keep: {city} {nakshatra} {rahu} {tithi}
    # may also use: {paksha_full} {paksha}
    "p.box": "<div class=\"box\"><p>આજે {city}માં <strong>{paksha} {tithi}</strong> છે અને ચંદ્ર <strong>{nakshatra}</strong> નક્ષત્રમાં છે. રાહુકાળ <strong>{rahu}</strong> દરમિયાન છે — આ સમયમાં કોઈ નવું કામ શરૂ ન કરો.</p></div>",
    # EN: Vaar (weekday)
    "p.r_vara": "વાર",
    # EN: Tithi
    "p.r_tithi": "તિથિ",
    # EN: Paksha
    "p.r_paksha": "પક્ષ",
    # EN: Nakshatra
    "p.r_nakshatra": "નક્ષત્ર",
    # EN: Yoga
    "p.r_yoga": "યોગ",
    # EN: Karana
    "p.r_karana": "કરણ",
    # EN: Sunrise
    "p.r_sunrise": "સૂર્યોદય",
    # EN: Sunset
    "p.r_sunset": "સૂર્યાસ્ત",
    # EN: Moonrise
    "p.r_moonrise": "ચંદ્રોદય",
    # EN: Moonset
    "p.r_moonset": "ચંદ્રાસ્ત",
    # EN: Moon sign
    "p.r_moon_sign": "ચંદ્ર રાશિ",
    # EN: Rahu Kaal
    "p.r_rahu": "રાહુકાળ",
    # EN: Yamaganda
    "p.r_yama": "યમગંડ",
    # EN: Gulika Kaal
    "p.r_gulika": "ગુલિક કાળ",
    # EN: Abhijit Muhurat
    "p.r_abhijit": "અભિજિત મુહૂર્ત",
    # EN: {vara_en} — {weekday} <span lang="hi">({vara_hi})</span>
    # keep: {vara}
    "p.v_vara": "{vara}",
    # EN: {paksha_en} <span lang="hi">({paksha_hi_full})</span>
    # keep: {paksha_full}
    "p.v_paksha": "{paksha_full}",
    # EN: No moonrise this day
    "p.no_moonrise": "આ દિવસે ચંદ્રોદય નથી",
    # EN: No moonset this day
    "p.no_moonset": "આ દિવસે ચંદ્રાસ્ત નથી",
    # EN: Not observed on Wednesday (Budhavara)
    "p.no_abhijit": "બુધવારે અભિજિત મુહૂર્ત ગણાતું નથી",
    # EN: <p>Times are for {place} ({lat}°N, {lon}°E) in Indian Standard Time. The panchang day runs
    #     from sunrise to the next sunrise, so a tithi or nakshatra may end after midnight. Sunrise
    #     is the visible upper limb with refraction, as printed in Indian almanacs; nakshatra and
    #     yoga use the Lahiri ayanamsa.</p>
    # keep: {lat} {lon}
    # may also use: {city} {place}
    "p.note": "<p>બધા સમય {place} ({lat}° ઉત્તર, {lon}° પૂર્વ) માટે ભારતીય માનક સમયમાં આપ્યા છે. પંચાંગનો દિવસ એક સૂર્યોદયથી બીજા સૂર્યોદય સુધીનો હોય છે, તેથી કોઈ તિથિ કે નક્ષત્ર મધ્યરાત્રિ પછી પણ પૂરું થઈ શકે છે. સૂર્યોદય ભારતીય પંચાંગોની જેમ સૂર્યના ઉપરના કિનારાના દેખાવાના ક્ષણે (વાતાવરણીય વક્રીભવન સહિત) લીધો છે; નક્ષત્ર અને યોગની ગણતરી લાહિરી અયનાંશથી કરી છે.</p>",
    # EN: Open the full Panchang — any city, any date
    "p.cta": "પૂરું પંચાંગ ખોલો — કોઈ પણ શહેર, કોઈ પણ તારીખ",
    # EN: <h2>The five limbs of the Panchang</h2> <p><strong>Tithi</strong> is the lunar day — each
    #     12° the Moon gains on the Sun. <strong>Nakshatra</strong> is the Moon's lunar mansion, one
    #     of 27. <strong>Yoga</strong> comes from the combined longitudes of Sun and Moon, and
    #     <strong>Karana</strong> is half a tithi. <strong>Vaar</strong> is the weekday, reckoned
    #     from sunrise. Together they are the <span lang="hi">पंचांग</span> (“five limbs”) consulted
    #     before any auspicious work.</p>
    "p.limbs": "<h2>પંચાંગનાં પાંચ અંગ</h2> <p><strong>તિથિ</strong> એટલે ચાંદ્ર દિવસ — ચંદ્ર સૂર્યથી દર 12° આગળ વધે ત્યારે એક તિથિ બને છે. <strong>નક્ષત્ર</strong> એટલે ચંદ્ર જે 27 નક્ષત્રોમાંથી જેમાં હોય તે. <strong>યોગ</strong> સૂર્ય અને ચંદ્રના રેખાંશના સરવાળા પરથી બને છે, અને <strong>કરણ</strong> એટલે અડધી તિથિ. <strong>વાર</strong> સપ્તાહનો દિવસ છે, જે સૂર્યોદયથી ગણાય છે. આ પાંચેય મળીને પંચાંગ (“પાંચ અંગ”) બને છે, જે કોઈ પણ શુભ કાર્ય પહેલાં જોવામાં આવે છે.</p>",
    # EN: Rahu Kaal Today in {city} — {rahu}, {date} | {brand}
    # keep: {brand} {city} {rahu}
    # may also use: {date}
    "rk.title": "આજનો રાહુકાળ {city}માં — {rahu}, {date} | {brand}",
    # EN: Rahu Kaal today in {city} ({vara}, {date}) is {rahu}. Also Yamaganda {yama} and Gulika
    #     {gulika}, with this week's timings and what Rahu Kaal means.
    # keep: {city} {date} {gulika} {rahu} {vara} {yama}
    "rk.desc": "{city}માં આજનો ({vara}, {date}) રાહુકાળ {rahu} છે. સાથે યમગંડ {yama} અને ગુલિક કાળ {gulika}, આ અઠવાડિયાના સમય અને રાહુકાળનો અર્થ.",
    # EN: <h1>Rahu Kaal Today in {city}</h1>
    # keep: {city}
    "rk.h1": "<h1>{city}માં આજનો રાહુકાળ</h1>",
    # EN: <p class="hi" lang="hi">आज का राहु काल — {city_hi}</p>
    # keep: {city}
    "rk.sub": "<p class=\"hi\">આજે રાહુકાળ, યમગંડ અને ગુલિક કાળ ક્યારે — {city}</p>",
    # EN: Rahu Kaal <span lang="hi">(राहु काल)</span>
    "rk.r_rahu": "રાહુકાળ",
    # EN: Yamaganda <span lang="hi">(यमगण्ड)</span>
    "rk.r_yama": "યમગંડ",
    # EN: Gulika Kaal <span lang="hi">(गुलिक काल)</span>
    "rk.r_gulika": "ગુલિક કાળ",
    # EN: Abhijit Muhurat
    "rk.r_abhijit": "અભિજિત મુહૂર્ત",
    # EN: Sunrise / Sunset
    "rk.r_sun": "સૂર્યોદય / સૂર્યાસ્ત",
    # EN: Not observed on Wednesday
    "rk.no_abhijit": "બુધવારે ગણાતું નથી",
    # EN: Check Rahu Kaal for any city or date
    "rk.cta": "કોઈ પણ શહેર કે તારીખનો રાહુકાળ જુઓ",
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
    "rk.about": "<h2>રાહુકાળ એટલે શું?</h2> <p>રાહુકાળ એ દરરોજનો લગભગ દોઢ કલાકનો સમય છે, જે પરંપરા મુજબ રાહુ (ચંદ્રના ઉત્તર પાત)ના અધિકારમાં ગણાય છે. સૂર્યોદયથી સૂર્યાસ્ત સુધીના દિવસને આઠ સરખા ભાગમાં વહેંચવામાં આવે છે અને તેમાંનો એક ભાગ રાહુનો હોય છે. કયો ભાગ તે વાર પર આધાર રાખે છે: રવિવારે 8મો, સોમવારે 2જો, મંગળવારે 7મો, બુધવારે 5મો, ગુરુવારે 6ઠ્ઠો, શુક્રવારે 4થો અને શનિવારે 3જો.</p> <p>તે વાસ્તવિક સૂર્યોદય અને સૂર્યાસ્તને અનુસરે છે, તેથી રાહુકાળ દરેક શહેરમાં અલગ હોય છે અને આખા વર્ષ દરમિયાન બદલાતો રહે છે — એટલે “સોમવાર 7:30–9:00” જેવું નિશ્ચિત કોષ્ટક માત્ર અંદાજ છે. રિવાજ મુજબ રાહુકાળમાં નવું સાહસ શરૂ કરવાનું, કરાર પર સહી કરવાનું, મુસાફરી શરૂ કરવાનું કે મોટી ખરીદી કરવાનું ટાળવામાં આવે છે; પહેલેથી ચાલતું કામ ચાલુ રાખી શકાય. યમગંડ અને ગુલિક કાળ દિવસના બીજા બે આઠમા ભાગ છે, જેમાં પણ એવી જ સાવધાની રખાય છે.</p>",
    # EN: <h2>Rahu Kaal in {city} this week</h2>
    # keep: {city}
    "rk.week_h2": "<h2>આ અઠવાડિયે {city}માં રાહુકાળ</h2>",
    # EN: Day
    "rk.th_day": "વાર",
    # EN: Rahu Kaal
    "rk.th_rahu": "રાહુકાળ",
    # EN: Yamaganda
    "rk.th_yama": "યમગંડ",
    # EN: Gulika
    "rk.th_gulika": "ગુલિક",
    # EN: Choghadiya Today in {city}, {date} — Day & Night Timings | {brand}
    # keep: {brand} {city} {date}
    "ch.title": "આજનાં ચોઘડિયાં {city}માં, {date} — દિવસ અને રાતના સમય | {brand}",
    # EN: Today's choghadiya for {city} ({vara}, {date}): all 16 day and night muhurtas — Amrit,
    #     Shubh, Labh, Char, Rog, Kaal, Udveg — with exact start and end times from sunrise
    #     {sunrise}.
    # keep: {city} {date} {sunrise} {vara}
    "ch.desc": "{city}નાં આજનાં ({vara}, {date}) ચોઘડિયાં: દિવસ અને રાતનાં બધાં 16 મુહૂર્ત — અમૃત, શુભ, લાભ, ચલ, રોગ, કાળ, ઉદ્વેગ — સૂર્યોદય {sunrise} થી ચોક્કસ શરૂઆત અને અંતના સમય સાથે.",
    # EN: <h1>Choghadiya Today in {city}</h1>
    # keep: {city}
    "ch.h1": "<h1>{city}માં આજનાં ચોઘડિયાં</h1>",
    # EN: <p class="hi" lang="hi">आज का चौघड़िया — {city_hi}</p>
    # keep: {city}
    "ch.sub": "<p class=\"hi\">દિવસ અને રાતનાં ચોઘડિયાં — {city}</p>",
    # EN: {name} from {time}
    # keep: {name} {time}
    "ch.first_good": "{time} થી {name}",
    # EN: none
    "ch.none": "કોઈ નહીં",
    # EN: <div class="box"><p>Sunrise <strong>{sunrise}</strong>, sunset <strong>{sunset}</strong>.
    #     First auspicious daytime choghadiya: <strong>{first_good}</strong>.</p></div>
    # keep: {first_good} {sunrise} {sunset}
    "ch.box": "<div class=\"box\"><p>સૂર્યોદય <strong>{sunrise}</strong>, સૂર્યાસ્ત <strong>{sunset}</strong>. દિવસનું પહેલું શુભ ચોઘડિયું: <strong>{first_good}</strong>.</p></div>",
    # EN: <h2>Day Choghadiya <span lang="hi">(दिन का चौघड़िया)</span></h2>
    "ch.day_h2": "<h2>દિવસનાં ચોઘડિયાં</h2>",
    # EN: <h2>Night Choghadiya <span lang="hi">(रात का चौघड़िया)</span></h2>
    "ch.night_h2": "<h2>રાતનાં ચોઘડિયાં</h2>",
    # EN: <tr><th>Time</th><th>Choghadiya</th><th>Nature</th></tr>
    "ch.th": "<tr><th>સમય</th><th>ચોઘડિયું</th><th>સ્વરૂપ</th></tr>",
    # EN: <tr><td>{when}</td><td class="{cls}"><strong>{name}</strong> <span lang="hi">({name_hi})</
    #     span><small>{ruler}</small></td><td>{quality}<small>{desc}</small></td></tr>
    # keep: {cls} {desc} {name} {quality} {ruler} {when}
    "ch.row": "<tr><td>{when}</td><td class=\"{cls}\"><strong>{name}</strong><small>સ્વામી: {ruler}</small></td><td>{quality}<small>{desc}</small></td></tr>",
    # EN: Open the live Choghadiya clock
    "ch.cta": "લાઇવ ચોઘડિયાં ઘડિયાળ ખોલો",
    # EN: <h2>How choghadiya works</h2> <p>The day from sunrise to sunset, and the night from sunset
    #     to the next sunrise, are each divided into eight equal parts called choghadiya (<span
    #     lang="hi">चौघड़िया</span>, “four ghadis”). Each is ruled by a planet and named for its
    #     nature: <strong>Amrit</strong>, <strong>Shubh</strong> and <strong>Labh</strong> are
    #     auspicious, <strong>Char</strong> is neutral and good for travel, while
    #     <strong>Rog</strong>, <strong>Kaal</strong> and <strong>Udveg</strong> are avoided for new
    #     beginnings. The order starts from the weekday's ruler, so it changes every day — and the
    #     length of each slot follows the real day length in {city}.</p>
    # keep: {city}
    "ch.about": "<h2>ચોઘડિયાં કેવી રીતે કામ કરે છે</h2> <p>સૂર્યોદયથી સૂર્યાસ્ત સુધીનો દિવસ અને સૂર્યાસ્તથી આગલા સૂર્યોદય સુધીની રાત — બંનેને આઠ સરખા ભાગમાં વહેંચવામાં આવે છે, જેને ચોઘડિયાં (“ચાર ઘડી”) કહે છે. દરેકનો એક ગ્રહ સ્વામી હોય છે અને તેના સ્વભાવ પ્રમાણે નામ મળે છે: <strong>અમૃત</strong>, <strong>શુભ</strong> અને <strong>લાભ</strong> શુભ ગણાય છે, <strong>ચલ</strong> મધ્યમ છે અને મુસાફરી માટે સારું છે, જ્યારે <strong>રોગ</strong>, <strong>કાળ</strong> અને <strong>ઉદ્વેગ</strong> નવી શરૂઆત માટે ટાળવામાં આવે છે. ક્રમ વારના સ્વામીથી શરૂ થાય છે, તેથી તે રોજ બદલાય છે — અને દરેક ચોઘડિયાની લંબાઈ {city}ના વાસ્તવિક દિવસની લંબાઈ પ્રમાણે હોય છે.</p>",
    # EN: Kundali Milan — Ashtakoot Guna Milan ({total} Gun) Explained | {brand}
    # keep: {brand} {total}
    "km.title": "કુંડળી મિલન — અષ્ટકૂટ ગુણ મિલન ({total} ગુણ) સમજૂતી | {brand}",
    # EN: How Kundali Milan works: the 8 kootas of Ashtakoot Guna Milan, {total} points, what score
    #     is good for marriage, and how Mangal Dosha is checked. Free online matching in English and
    #     Hindi.
    # keep: {total}
    "km.desc": "કુંડળી મિલન કેવી રીતે થાય છે: અષ્ટકૂટ ગુણ મિલનના 8 કૂટ, {total} ગુણ, લગ્ન માટે કેટલા ગુણ સારા અને મંગળ દોષ કેવી રીતે તપાસાય છે. મફત ઓનલાઇન મેળાપક અંગ્રેજી અને હિન્દીમાં.",
    # EN: Kundali Milan
    "km.crumb": "કુંડળી મિલન",
    # EN: <h1>Kundali Milan: Ashtakoot Guna Milan explained</h1> <p class="hi" lang="hi">कुंडली
    #     मिलान — अष्टकूट गुण मिलान ({total} गुण)</p> <p>Kundali Milan (<span lang="hi">कुंडली
    #     मिलान</span>) is the traditional Vedic way of checking marriage compatibility. The most
    #     widely used method in North India is <strong>Ashtakoot Guna Milan</strong>: eight factors
    #     (<em>kootas</em>) are compared between the bride's and groom's charts and scored out of
    #     <strong>{total} points (gunas)</strong>. Every one of them is read from the
    #     <strong>Moon</strong> — its sign (rashi) and its nakshatra at birth — which is why the
    #     score needs an accurate birth date and place, but barely depends on the birth time.</p>
    # keep: {total}
    "km.intro": "<h1>કુંડળી મિલન: અષ્ટકૂટ ગુણ મિલનની સમજૂતી</h1> <p>કુંડળી મિલન એ લગ્નની સુસંગતતા તપાસવાની પરંપરાગત વૈદિક રીત છે. ઉત્તર ભારતમાં સૌથી વધુ વપરાતી પદ્ધતિ <strong>અષ્ટકૂટ ગુણ મિલન</strong> છે: કન્યા અને વરની કુંડળીઓ વચ્ચે આઠ બાબતો (<em>કૂટ</em>) સરખાવીને કુલ <strong>{total} ગુણ</strong>માંથી ગુણ અપાય છે. તે બધા <strong>ચંદ્ર</strong> પરથી જોવાય છે — જન્મ સમયની તેની રાશિ અને નક્ષત્ર — એટલે ગુણ માટે જન્મની સાચી તારીખ અને સ્થળ જોઈએ, પણ જન્મના સમય પર તે ભાગ્યે જ આધાર રાખે છે.</p>",
    # EN: Match two kundalis now — free
    "km.cta1": "બે કુંડળી હમણાં જ મેળવો — મફત",
    # EN: <p>Don't know the birth times? Try <a href="{href}">Naam se Kundali Milan</a> — the
    #     traditional match by the first letter of each name.</p>
    # keep: {href}
    "km.naam": "<p>જન્મનો સમય ખબર નથી? <a href=\"{href}\">નામ પરથી કુંડળી મિલન</a> અજમાવો — દરેક નામના પહેલા અક્ષર પ્રમાણેનું પરંપરાગત મિલન.</p>",
    # EN: <h2>The 8 kootas and their points</h2>
    "km.kootas_h2": "<h2>8 કૂટ અને તેમના ગુણ</h2>",
    # EN: <tr><th>Koota</th><th>Points</th><th>What it measures</th></tr>
    "km.th": "<tr><th>કૂટ</th><th>ગુણ</th><th>શું માપે છે</th></tr>",
    # EN: <tr><td><strong>{name}</strong> <span
    #     lang="hi">({name_hi})</span></td><td>{pts}</td><td>{text}</td></tr>
    # keep: {name} {pts} {text}
    "km.row": "<tr><td><strong>{name}</strong></td><td>{pts}</td><td>{text}</td></tr>",
    # EN: Total
    "km.total": "કુલ",
    # EN: <h2>What is a good Guna Milan score?</h2>
    "km.score_h2": "<h2>ગુણ મિલનમાં કેટલા ગુણ સારા ગણાય?</h2>",
    # EN: <tr><th>Gunas</th><th>Conventional reading</th></tr>
    "km.score_th": "<tr><th>ગુણ</th><th>પરંપરાગત અર્થ</th></tr>",
    # EN: Below {n}
    # keep: {n}
    "km.below": "{n}થી ઓછા",
    # EN: <p>18 is the conventional minimum. The total alone is not the whole story: a high score
    #     with an uncancelled Nadi or Bhakoot dosha is read with caution, and a modest score with
    #     strong Graha Maitri and no doshas is often considered workable. These bands are a
    #     convention with a long history, not a measurement — they are guidance, not a verdict on a
    #     relationship.</p>
    "km.score_p": "<p>18 એ પરંપરાગત ન્યૂનતમ છે. માત્ર કુલ ગુણથી આખી વાત નથી થતી: ઊંચા ગુણ સાથે પરિહાર વગરનો નાડી કે ભકૂટ દોષ હોય તો સાવધાનીથી વિચારાય છે, અને ઓછા ગુણ છતાં સારી ગ્રહમૈત્રી હોય અને કોઈ દોષ ન હોય તો મેળ ઘણી વાર ચાલે તેવો ગણાય છે. આ શ્રેણીઓ લાંબા ઇતિહાસવાળી પ્રથા છે, માપ નથી — તે માર્ગદર્શન છે, કોઈ સંબંધ પર અંતિમ ચુકાદો નથી.</p>",
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
    "km.or": " અથવા ",
    # EN: <h2>Mangal Dosha (Manglik)</h2> <p>Mangal Dosha is checked separately from the 36 points.
    #     A chart is Manglik when Mars sits in the {houses} house counted from the
    #     <strong>Lagna</strong> (ascendant), the <strong>Moon</strong> or <strong>Venus</strong>.
    #     Classical texts exempt certain sign placements (for example Mars in its own sign Aries in
    #     the 1st), and Jupiter's aspect on Mars is held to soften it. When <strong>both</strong>
    #     partners are Manglik the dosha is conventionally treated as mutually cancelled — which is
    #     why Manglik matches are made with Manglik partners. Because it depends on the Lagna,
    #     Mangal Dosha does need a reliable birth time.</p>
    # keep: {houses}
    "km.mangal": "<h2>મંગળ દોષ (માંગલિક)</h2> <p>મંગળ દોષ 36 ગુણથી અલગ તપાસાય છે. કુંડળી માંગલિક ત્યારે ગણાય જ્યારે <strong>લગ્ન</strong>, <strong>ચંદ્ર</strong> અથવા <strong>શુક્ર</strong>થી ગણતાં મંગળ {houses} ભાવમાં હોય. શાસ્ત્રોમાં કેટલીક રાશિ-સ્થિતિઓને છૂટ અપાઈ છે (દા.ત. પહેલા ભાવમાં પોતાની રાશિ મેષનો મંગળ), અને મંગળ પર ગુરુની દૃષ્ટિ દોષને હળવો કરે છે એમ મનાય છે. જ્યારે <strong>બંને</strong> પાત્રો માંગલિક હોય ત્યારે પરંપરા મુજબ દોષ પરસ્પર કપાઈ જાય છે — એટલે જ માંગલિકના લગ્ન માંગલિક સાથે કરાય છે. તે લગ્ન પર આધારિત હોવાથી મંગળ દોષ માટે જન્મનો ભરોસાપાત્ર સમય જરૂરી છે.</p>",
    # EN: <h2>How our matching tool works</h2> <p>Enter both people's date, time and place of birth.
    #     Both charts are cast with the sidereal zodiac (Lahiri ayanamsa) from the Swiss Ephemeris,
    #     and each koota is scored by table lookup from the classical tables, with every
    #     cancellation named. You get the full {total}-point breakdown and both partners' Mangal
    #     Dosha status, in English or <span lang="hi">हिन्दी</span>, free and without signing
    #     up.</p>
    # keep: {total}
    "km.how": "<h2>અમારું મેળાપક સાધન કેવી રીતે કામ કરે છે</h2> <p>બંને વ્યક્તિની જન્મ તારીખ, સમય અને સ્થળ નાખો. બંને કુંડળી સ્વિસ એફેમેરિસથી નિરયન રાશિચક્ર (લાહિરી અયનાંશ) મુજબ બને છે, અને દરેક કૂટના ગુણ શાસ્ત્રીય કોષ્ટકોમાંથી મળે છે, દરેક પરિહારના નામ સાથે. તમને {total} ગુણનું પૂરું વિવરણ અને બંને પાત્રોની મંગળ દોષની સ્થિતિ મળે છે — અંગ્રેજી કે હિન્દીમાં, મફત અને સાઇન અપ કર્યા વગર.</p>",
    # EN: Open Kundali Milan
    "km.cta2": "કુંડળી મિલન ખોલો",
    # EN: Varna
    "koota.varna": "વર્ણ",
    # EN: Vashya
    "koota.vashya": "વશ્ય",
    # EN: Tara
    "koota.tara": "તારા",
    # EN: Yoni
    "koota.yoni": "યોનિ",
    # EN: Graha Maitri
    "koota.graha_maitri": "ગ્રહમૈત્રી",
    # EN: Gana
    "koota.gana": "ગણ",
    # EN: Bhakoot
    "koota.bhakoot": "ભકૂટ",
    # EN: Nadi
    "koota.nadi": "નાડી",
    # EN: Spiritual and working temperament, from the Moon sign's varna. Full point when the groom's
    #     varna is not below the bride's.
    "koota_about.varna": "ચંદ્ર રાશિના વર્ણ પરથી આધ્યાત્મિક અને કાર્યસ્વભાવ. વરનો વર્ણ કન્યાથી નીચો ન હોય તો પૂરો ગુણ મળે.",
    # EN: Mutual attraction and influence — which sign “draws” the other.
    "koota_about.vashya": "પરસ્પર આકર્ષણ અને પ્રભાવ — કઈ રાશિ બીજીને “વશ” કરે છે.",
    # EN: Health and wellbeing, from the count between the two birth nakshatras; the 3rd, 5th and
    #     7th taras are unfavourable.
    "koota_about.tara": "બંનેના જન્મ નક્ષત્ર વચ્ચેની ગણતરી પરથી સ્વાસ્થ્ય અને કલ્યાણ; 3જી, 5મી અને 7મી તારા પ્રતિકૂળ છે.",
    # EN: Physical and intimate compatibility; each nakshatra has an animal yoni, and sworn-enemy
    #     animals score zero.
    "koota_about.yoni": "શારીરિક અને અંગત સુસંગતતા; દરેક નક્ષત્રની એક પ્રાણી યોનિ હોય છે, અને જન્મજાત શત્રુ પ્રાણીઓના ગુણ શૂન્ય મળે છે.",
    # EN: Friendship between the lords of the two Moon signs — the mental wavelength of the couple.
    "koota_about.graha_maitri": "બંને ચંદ્ર રાશિના સ્વામીઓ વચ્ચેની મિત્રતા — દંપતીની માનસિક તરંગલંબાઈ.",
    # EN: Temperament: Deva (divine), Manushya (human) or Rakshasa (fierce).
    "koota_about.gana": "સ્વભાવ: દેવ (દિવ્ય), મનુષ્ય (માનવ) કે રાક્ષસ (ઉગ્ર).",
    # EN: The relative placement of the two Moon signs. The 2/12, 5/9 and 6/8 positions form Bhakoot
    #     dosha, cancelled when the sign lords are the same or friends.
    "koota_about.bhakoot": "બંને ચંદ્ર રાશિની પરસ્પર સ્થિતિ. 2/12, 5/9 અને 6/8 સ્થિતિથી ભકૂટ દોષ બને છે, જે રાશિસ્વામી એક જ હોય કે મિત્ર હોય ત્યારે કપાઈ જાય છે.",
    # EN: The highest-weighted koota, tied to health and progeny. The same nadi for both is Nadi
    #     dosha, with classical cancellations for the same sign/different nakshatra or same
    #     nakshatra/different pada.
    "koota_about.nadi": "સૌથી વધુ ગુણવાળો કૂટ, જે સ્વાસ્થ્ય અને સંતાન સાથે જોડાયેલો છે. બંનેની નાડી એક જ હોય તો નાડી દોષ બને છે; એક જ રાશિ અને અલગ નક્ષત્ર, અથવા એક જ નક્ષત્ર અને અલગ ચરણ હોય તો શાસ્ત્રીય પરિહાર મળે છે.",
    # EN: Free Kundali Online — Janam Kundali (Birth Chart) in English & Hindi | {brand}
    # keep: {brand}
    "fk.title": "મફત કુંડળી ઓનલાઇન — જન્મકુંડળી અંગ્રેજી અને હિન્દીમાં | {brand}",
    # EN: Make your free janam kundali online: Lagna chart in North or South Indian style, planet
    #     positions, Moon nakshatra, Vimshottari dasha, Navamsa and other divisional charts,
    #     Manglik, Sade Sati and Kaal Sarp check — in English or Hindi, no sign-in needed.
    "fk.desc": "તમારી મફત જન્મકુંડળી ઓનલાઇન બનાવો: ઉત્તર કે દક્ષિણ ભારતીય શૈલીમાં લગ્ન કુંડળી, ગ્રહોની સ્થિતિ, ચંદ્ર નક્ષત્ર, વિંશોત્તરી દશા, નવમાંશ અને બીજા વિભાગીય ચાર્ટ, માંગલિક, સાડાસાતી અને કાલસર્પ તપાસ — અંગ્રેજી કે હિન્દીમાં, સાઇન-ઇન વગર.",
    # EN: Free Kundali
    "fk.crumb": "મફત કુંડળી",
    # EN: <h1>Free Janam Kundali online</h1> <p class="hi" lang="hi">मुफ़्त जन्म कुंडली — हिंदी और
    #     अंग्रेज़ी में</p> <p>A <strong>janam kundali</strong> (<span lang="hi">जन्म कुंडली</span>,
    #     birth chart) is a map of the sky at the exact moment and place you were born: which of the
    #     twelve signs was rising on the eastern horizon (your <strong>Lagna</strong>), and where
    #     the Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu and Ketu stood among the signs
    #     and the 27 nakshatras. Vedic astrology reads everything else — personality, the twelve
    #     areas of life, and above all <em>timing</em> through the dasha periods — from this one
    #     chart. Ours is computed to the minute and is free.</p>
    "fk.intro": "<h1>મફત જન્મકુંડળી ઓનલાઇન</h1> <p class=\"hi\">તમારા જન્મ સમયના આકાશનો નકશો — મફત</p> <p><strong>જન્મકુંડળી</strong> એટલે તમારા જન્મના ચોક્કસ સમયે અને સ્થળે આકાશનો નકશો: પૂર્વ ક્ષિતિજ પર બાર રાશિમાંથી કઈ રાશિ ઉદય પામી રહી હતી (તમારું <strong>લગ્ન</strong>), અને સૂર્ય, ચંદ્ર, મંગળ, બુધ, ગુરુ, શુક્ર, શનિ, રાહુ અને કેતુ રાશિઓ અને 27 નક્ષત્રોમાં ક્યાં હતા. વૈદિક જ્યોતિષ બાકીનું બધું — સ્વભાવ, જીવનનાં બાર ક્ષેત્રો અને સૌથી વધુ તો દશા દ્વારા <em>સમય</em> — આ એક જ કુંડળી પરથી વાંચે છે. અમારી કુંડળી મિનિટ સુધી ચોક્કસ ગણાય છે અને મફત છે.</p>",
    # EN: Make my free kundali now
    "fk.cta1": "મારી મફત કુંડળી હમણાં બનાવો",
    # EN: <p>You need your <strong>date</strong>, <strong>time</strong> and <strong>place</strong>
    #     of birth. No sign-in, no card.</p>
    "fk.need": "<p>તમારે જન્મની <strong>તારીખ</strong>, <strong>સમય</strong> અને <strong>સ્થળ</strong> જોઈશે. સાઇન-ઇન નહીં, કાર્ડ નહીં.</p>",
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
    "fk.includes": "<h2>તમારી મફત કુંડળીમાં શું મળે છે</h2> <ul> <li><strong>લગ્ન કુંડળી (D1)</strong> ઉત્તર કે દક્ષિણ ભારતીય શૈલીમાં — એક ટેપથી બદલો.</li> <li><strong>ગ્રહોની સ્થિતિ</strong>: નવેય ગ્રહ અને લગ્નની રાશિ, અંશ, ભાવ, બળ અને વક્રી સ્થિતિ, સાથે તમારા ચંદ્રનું નક્ષત્ર અને ચરણ.</li> <li><strong>બાર ભાવ</strong> અને દરેકમાં રહેલા ગ્રહો.</li> <li><strong>વિંશોત્તરી દશા</strong>: તમારી હાલની મહાદશા અને અંતર્દશા તારીખો સાથે, દૃશ્ય સમયરેખા પર.</li> <li><strong>વિભાગીય ચાર્ટ (વર્ગ)</strong>: {vargas}.</li> <li><strong>અષ્ટકવર્ગ</strong>: ભાવ પ્રમાણે સર્વાષ્ટકવર્ગ અને ભિન્નાષ્ટકવર્ગના બિંદુ.</li> <li><strong>જૈમિની</strong> ચર કારક (આત્મકારકથી દારાકારક સુધી) અને આરૂઢ પદ, તથા લગ્ન, ચંદ્ર અને સૂર્ય ત્રણેયથી કુંડળીનું <strong>સુદર્શન ચક્ર</strong> વાચન.</li> <li><strong>દોષ તપાસ</strong>: મંગળ દોષ (માંગલિક), સાડાસાતી અને કાલસર્પ.</li> <li>તમારી કુંડળી અને હાલની દશા માટે <strong>રત્ન અને ઉપાય</strong> સૂચનો.</li> <li>તમારા ડેશબોર્ડ પર તમારું <strong>દૈનિક ભવિષ્ય</strong> અને આજનું પંચાંગ.</li> </ul> <p>બધું <strong>લાહિરી અયનાંશ સાથે નિરયન રાશિચક્ર</strong>, સંપૂર્ણ-રાશિ ભાવો અને સ્વિસ એફેમેરિસથી ગણાય છે. મફત ખાતાથી તમે કુંડળીઓ સાચવી શકો છો, કુંડળી અંગ્રેજી કે હિન્દીમાં PDF તરીકે ડાઉનલોડ કરી શકો છો, અને AI જ્યોતિષીને તમારા પ્રથમ પ્રશ્નો મફત પૂછી શકો છો.</p>",
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
    "fk.read": "<h2>તમારી કુંડળી કેવી રીતે વાંચવી</h2> <h3>1. લગ્નથી શરૂ કરો</h3> <p>પ્રથમ ભાવ એટલે જન્મ સમયે ઉદય પામતી રાશિ. ઉત્તર ભારતીય કુંડળીમાં તે ઉપરનો મધ્યનો હીરાકાર ખાનો છે, અને દરેક ભાવમાં લખેલો અંક <em>રાશિ</em> છે (1 = મેષ … 12 = મીન), ભાવ નથી. દક્ષિણ ભારતીય કુંડળીમાં રાશિઓ નિશ્ચિત ખાનામાં રહે છે અને લગ્ન ચિહ્નિત હોય છે. લગ્ન અને તેનો સ્વામી શરીર, સ્વભાવ અને જીવનની એકંદર દિશા દર્શાવે છે.</p> <h3>2. તમારી ચંદ્ર રાશિ અને નક્ષત્ર જુઓ</h3> <p>ભારતીય પ્રથામાં તમારી <strong>રાશિ</strong> એટલે ચંદ્રની રાશિ, સૂર્યની નહીં. રાશિફળ, સાડાસાતી અને કુંડળી મિલન માટે આ જ રાશિ વપરાય છે, અને ચંદ્રનું નક્ષત્ર નક્કી કરે છે કે તમારી વિંશોત્તરી દશા ક્યાંથી શરૂ થાય છે.</p> <h3>3. ગ્રહોને ભાવ પ્રમાણે વાંચો</h3> <p>દરેક ભાવ જીવનનું એક ક્ષેત્ર છે: 1લો સ્વ, 2જો ધન અને કુટુંબ, 3જો પરાક્રમ અને ભાઈ-બહેન, 4થો ઘર અને માતા, 5મો સંતાન અને બુદ્ધિ, 6ઠ્ઠો આરોગ્ય અને શત્રુ, 7મો લગ્ન અને ભાગીદારી, 8મો આયુષ્ય અને અચાનક પરિવર્તન, 9મો ભાગ્ય અને ધર્મ, 10મો કારકિર્દી, 11મો લાભ, 12મો ખર્ચ અને મોક્ષ. ગ્રહ જે ભાવમાં બેઠો હોય અને જે ભાવોનો સ્વામી હોય તેને રંગ આપે છે; તેનું બળ (ઉચ્ચ, સ્વરાશિ, નીચ) કહે છે કે તે કેટલું ફળ આપી શકે.</p> <h3>4. ચાલતી દશા તપાસો</h3> <p>દશા કહે છે <em>ક્યારે</em>. મહાદશાનો સ્વામી અને તેની અંદર અંતર્દશાનો સ્વામી એ ગ્રહો છે જેમના ભાવ આ સમયગાળામાં સક્રિય થાય છે — એટલે સમાન કુંડળીવાળા બે જણનાં વર્ષો ઘણાં અલગ હોઈ શકે.</p> <h3>5. દોષને સંદર્ભમાં જુઓ</h3> <p>દોષ એક પેટર્ન છે જે વાંચવાની હોય, ચુકાદો નહીં. મંગળ દોષના શાસ્ત્રીય પરિહાર છે; સાડાસાતી સાડા સાત વર્ષનું ગોચર છે જે દરેકને બે-ત્રણ વાર આવે છે. દોષ અહેવાલ જે પરિહાર મળ્યા તેનાં નામ આપે છે.</p>",
    # EN: Create my janam kundali — free
    "fk.cta2": "મારી જન્મકુંડળી બનાવો — મફત",
    # EN: <h2>Frequently asked questions</h2>
    "fk.faq_h2": "<h2>વારંવાર પૂછાતા પ્રશ્નો</h2>",
    # EN: Rashi
    "varga.D1": "રાશિ",
    # EN: Drekkana
    "varga.D3": "દ્રેષ્કાણ",
    # EN: Saptamsa
    "varga.D7": "સપ્તાંશ",
    # EN: Navamsa
    "varga.D9": "નવમાંશ",
    # EN: Dashamsa
    "varga.D10": "દશમાંશ",
    # EN: Dwadashamsa
    "varga.D12": "દ્વાદશાંશ",
    # EN: Not recommended
    "km.band0": "ભલામણ નથી",
    # EN: Acceptable
    "km.band1": "ચાલે તેવું",
    # EN: Good
    "km.band2": "સારું",
    # EN: Excellent
    "km.band3": "ઉત્તમ",
}

# app/seo_text.py FAQ["gu"] — the seven free-kundali FAQ pairs (plain text)  [7]
SEO_FAQ = (
    # EN q: Is the kundali really free?
    # EN a: Yes. Casting the chart, the dashas, the divisional charts and the dosha check cost
    #       nothing, and you do not need to sign in to see them. Only the AI astrologer's answers
    #       beyond your free questions, and in-depth paid reports such as the Life Book, cost money.
    ("શું કુંડળી ખરેખર મફત છે?", "હા. કુંડળી બનાવવી, દશાઓ, વિભાગીય ચાર્ટ અને દોષ તપાસ મફત છે, અને તે જોવા માટે સાઇન-ઇન કરવાની જરૂર નથી. માત્ર તમારા મફત પ્રશ્નો પછીના AI જ્યોતિષીના જવાબો અને લાઇફ બુક જેવા વિગતવાર પેઇડ અહેવાલોના પૈસા લાગે છે."),
    # EN q: What details do I need?
    # EN a: Your date of birth, time of birth and place of birth. The place sets the latitude,
    #       longitude and time zone, which decide the Lagna (ascendant) and the house positions.
    ("મને કઈ વિગતો જોઈશે?", "તમારી જન્મ તારીખ, જન્મનો સમય અને જન્મ સ્થળ. સ્થળ પરથી અક્ષાંશ, રેખાંશ અને સમય ઝોન નક્કી થાય છે, જે લગ્ન (ઉદય રાશિ) અને ભાવોની સ્થિતિ નક્કી કરે છે."),
    # EN q: What if I don't know my exact birth time?
    # EN a: The chart is still cast, at 12:00 noon. The Moon sign and nakshatra are usually still
    #       right (unless the Moon changed sign or nakshatra that day), so Moon-based readings, Sade
    #       Sati and Kundali Milan stay useful — but the Lagna, the houses and Mangal Dosha need a
    #       reliable time. A time from a birth certificate or hospital record is best.
    ("જો મને જન્મનો ચોક્કસ સમય ખબર ન હોય તો?", "તો પણ કુંડળી બપોરે 12:00 વાગ્યાના સમયે બને છે. ચંદ્ર રાશિ અને નક્ષત્ર સામાન્ય રીતે સાચાં જ રહે છે (સિવાય કે તે દિવસે ચંદ્રએ રાશિ કે નક્ષત્ર બદલ્યું હોય), તેથી ચંદ્ર આધારિત ફળાદેશ, સાડાસાતી અને કુંડળી મિલન ઉપયોગી રહે છે — પરંતુ લગ્ન, ભાવો અને મંગળ દોષ માટે ભરોસાપાત્ર સમય જોઈએ. જન્મ પ્રમાણપત્ર કે હોસ્પિટલના રેકોર્ડનો સમય શ્રેષ્ઠ."),
    # EN q: Which system do you use — Lahiri, KP, tropical?
    # EN a: Every chart is sidereal (Nirayana) with the Lahiri (Chitrapaksha) ayanamsa, whole-sign
    #       houses and Vimshottari dasha — the convention of most Indian almanacs and astrologers.
    #       Planet positions come from the Swiss Ephemeris.
    ("તમે કઈ પદ્ધતિ વાપરો છો — લાહિરી, KP, સાયન?", "દરેક કુંડળી લાહિરી (ચિત્રપક્ષ) અયનાંશ સાથે નિરયન છે, સંપૂર્ણ-રાશિ ભાવો અને વિંશોત્તરી દશા સાથે — મોટા ભાગનાં ભારતીય પંચાંગો અને જ્યોતિષીઓની પ્રથા. ગ્રહોની સ્થિતિ સ્વિસ એફેમેરિસ પરથી આવે છે."),
    # EN q: Can I see my kundali in Hindi?
    # EN a: Yes. Switch the app to हिन्दी and the chart, planet and sign names, dashas and readings
    #       all appear in Hindi; the PDF can be downloaded in Hindi too.
    ("શું હું મારી કુંડળી હિન્દીમાં જોઈ શકું?", "હા. એપને હિન્દીમાં બદલો તો કુંડળી, ગ્રહ અને રાશિનાં નામ, દશાઓ અને વાચન બધું હિન્દીમાં દેખાશે; PDF પણ હિન્દીમાં ડાઉનલોડ કરી શકાય છે."),
    # EN q: North Indian or South Indian chart?
    # EN a: Both. The same chart can be shown as the North Indian diamond chart (houses fixed, signs
    #       numbered) or the South Indian square chart (signs fixed), with one tap.
    ("ઉત્તર ભારતીય કે દક્ષિણ ભારતીય કુંડળી?", "બંને. એક જ કુંડળી ઉત્તર ભારતીય હીરાકાર ચાર્ટ (ભાવ નિશ્ચિત, રાશિઓ અંકિત) અથવા દક્ષિણ ભારતીય ચોરસ ચાર્ટ (રાશિઓ નિશ્ચિત) તરીકે એક ટેપથી જોઈ શકાય છે."),
    # EN q: Is this the same as a horoscope?
    # EN a: A janam kundali is the birth chart itself — the fixed map of the sky at your birth. A
    #       daily horoscope or rashifal is a short general forecast for everyone with the same Moon
    #       sign. Your kundali is personal; a rashifal is not.
    ("શું જન્મકુંડળી અને રાશિફળ એક જ છે?", "જન્મકુંડળી એ જન્મકુંડળી જ છે — તમારા જન્મ સમયે આકાશનો નિશ્ચિત નકશો. દૈનિક ભવિષ્ય કે રાશિફળ એ એક જ ચંદ્ર રાશિવાળા બધા માટેનું ટૂંકું સામાન્ય ભવિષ્ય છે. તમારી કુંડળી વ્યક્તિગત છે; રાશિફળ નથી."),
)

# app/i18n.py CHROME["gu"] — chrome shared by every server page: breadcrumb, footer links, disclaimer (HTML: write &amp;)  [10]
CHROME = {
    # EN: Home
    "home": "હોમ",
    # EN: Breadcrumb
    "breadcrumb": "બ્રેડક્રમ્બ",
    # EN: Share on WhatsApp
    "share": "WhatsApp પર શેર કરો",
    # EN: Kathas
    "f_katha": "કથાઓ",
    # EN: Terms &amp; Conditions
    "f_terms": "નિયમો અને શરતો",
    # EN: Privacy Policy
    "f_privacy": "ગોપનીયતા નીતિ",
    # EN: Refund &amp; Cancellation
    "f_refund": "રિફંડ અને રદ કરવાની નીતિ",
    # EN: Contact Us
    "f_contact": "અમારો સંપર્ક કરો",
    # EN: Feedback
    "f_feedback": "પ્રતિભાવ",
    # EN: Astrological readings are provided for guidance and entertainment. They are not medical,
    #     legal or financial advice.
    "disclaimer": "જ્યોતિષીય વાચન માર્ગદર્શન અને મનોરંજન માટે આપવામાં આવે છે. તે તબીબી, કાનૂની કે નાણાકીય સલાહ નથી.",
}

# app/stay_strip.py TEXT["gu"] — the 'Stay in touch' strip at the foot of the pages  [8]
STAY_STRIP = {
    # EN: Stay in touch
    "head": "સંપર્કમાં રહો",
    # EN: Get today's panchang on your phone every morning
    "push": "દરરોજ સવારે આજનું પંચાંગ તમારા ફોન પર મેળવો",
    # EN: Turning on…
    "busy": "ચાલુ કરી રહ્યા છીએ…",
    # EN: Done — you will get it every morning.
    "on": "થઈ ગયું — તમને દરરોજ સવારે મળશે.",
    # EN: Could not turn on alerts. Please try again.
    "err": "ચેતવણીઓ ચાલુ થઈ શકી નથી. કૃપા કરીને ફરી પ્રયત્ન કરો.",
    # EN: Notifications are blocked for this site in your browser settings.
    "denied": "તમારા બ્રાઉઝરના સેટિંગમાં આ સાઇટ માટે સૂચનાઓ બંધ છે.",
    # EN: Join our WhatsApp channel
    "channel": "અમારી WhatsApp ચેનલ સાથે જોડાઓ",
    # EN: Share this page on WhatsApp
    "share": "આ પેજ WhatsApp પર શેર કરો",
}

# app/seo_city_names.py CITIES["gu"] — the 114 cities as that language's newspapers spell them (key = URL slug)  [114]
CITY_NAMES = {
    # EN: New Delhi
    "new-delhi": "નવી દિલ્હી",
    # EN: Mumbai
    "mumbai": "મુંબઈ",
    # EN: Kolkata
    "kolkata": "કોલકાતા",
    # EN: Chennai
    "chennai": "ચેન્નઈ",
    # EN: Bengaluru
    "bengaluru": "બેંગલુરુ",
    # EN: Hyderabad
    "hyderabad": "હૈદરાબાદ",
    # EN: Ahmedabad
    "ahmedabad": "અમદાવાદ",
    # EN: Pune
    "pune": "પુણે",
    # EN: Jaipur
    "jaipur": "જયપુર",
    # EN: Lucknow
    "lucknow": "લખનઉ",
    # EN: Kanpur
    "kanpur": "કાનપુર",
    # EN: Nagpur
    "nagpur": "નાગપુર",
    # EN: Indore
    "indore": "ઇન્દોર",
    # EN: Bhopal
    "bhopal": "ભોપાલ",
    # EN: Patna
    "patna": "પટના",
    # EN: Varanasi
    "varanasi": "વારાણસી",
    # EN: Prayagraj
    "prayagraj": "પ્રયાગરાજ",
    # EN: Surat
    "surat": "સુરત",
    # EN: Vadodara
    "vadodara": "વડોદરા",
    # EN: Chandigarh
    "chandigarh": "ચંડીગઢ",
    # EN: Amritsar
    "amritsar": "અમૃતસર",
    # EN: Dehradun
    "dehradun": "દેહરાદૂન",
    # EN: Haridwar
    "haridwar": "હરિદ્વાર",
    # EN: Noida
    "noida": "નોઇડા",
    # EN: Gurugram
    "gurugram": "ગુરુગ્રામ",
    # EN: Bhubaneswar
    "bhubaneswar": "ભુવનેશ્વર",
    # EN: Guwahati
    "guwahati": "ગુવાહાટી",
    # EN: Ranchi
    "ranchi": "રાંચી",
    # EN: Kochi
    "kochi": "કોચી",
    # EN: Visakhapatnam
    "visakhapatnam": "વિશાખાપટ્ટનમ",
    # EN: Thane
    "thane": "થાણે",
    # EN: Navi Mumbai
    "navi-mumbai": "નવી મુંબઈ",
    # EN: Nashik
    "nashik": "નાશિક",
    # EN: Chhatrapati Sambhajinagar
    "chhatrapati-sambhajinagar": "છત્રપતિ સંભાજીનગર",
    # EN: Solapur
    "solapur": "સોલાપુર",
    # EN: Kolhapur
    "kolhapur": "કોલ્હાપુર",
    # EN: Amravati
    "amravati": "અમરાવતી",
    # EN: Shirdi
    "shirdi": "શિરડી",
    # EN: Rajkot
    "rajkot": "રાજકોટ",
    # EN: Bhavnagar
    "bhavnagar": "ભાવનગર",
    # EN: Jamnagar
    "jamnagar": "જામનગર",
    # EN: Gandhinagar
    "gandhinagar": "ગાંધીનગર",
    # EN: Dwarka
    "dwarka": "દ્વારકા",
    # EN: Somnath
    "somnath": "સોમનાથ",
    # EN: Jodhpur
    "jodhpur": "જોધપુર",
    # EN: Udaipur
    "udaipur": "ઉદયપુર",
    # EN: Kota
    "kota": "કોટા",
    # EN: Ajmer
    "ajmer": "અજમેર",
    # EN: Bikaner
    "bikaner": "બીકાનેર",
    # EN: Agra
    "agra": "આગ્રા",
    # EN: Ghaziabad
    "ghaziabad": "ગાઝિયાબાદ",
    # EN: Meerut
    "meerut": "મેરઠ",
    # EN: Bareilly
    "bareilly": "બરેલી",
    # EN: Aligarh
    "aligarh": "અલીગઢ",
    # EN: Moradabad
    "moradabad": "મુરાદાબાદ",
    # EN: Gorakhpur
    "gorakhpur": "ગોરખપુર",
    # EN: Saharanpur
    "saharanpur": "સહારનપુર",
    # EN: Ayodhya
    "ayodhya": "અયોધ્યા",
    # EN: Mathura
    "mathura": "મથુરા",
    # EN: Vrindavan
    "vrindavan": "વૃંદાવન",
    # EN: Jhansi
    "jhansi": "ઝાંસી",
    # EN: Faridabad
    "faridabad": "ફરીદાબાદ",
    # EN: Kurukshetra
    "kurukshetra": "કુરુક્ષેત્ર",
    # EN: Ludhiana
    "ludhiana": "લુધિયાણા",
    # EN: Jalandhar
    "jalandhar": "જલંધર",
    # EN: Patiala
    "patiala": "પટિયાલા",
    # EN: Rishikesh
    "rishikesh": "ઋષિકેશ",
    # EN: Shimla
    "shimla": "શિમલા",
    # EN: Jammu
    "jammu": "જમ્મુ",
    # EN: Srinagar
    "srinagar": "શ્રીનગર",
    # EN: Katra
    "katra": "કટરા",
    # EN: Gwalior
    "gwalior": "ગ્વાલિયર",
    # EN: Jabalpur
    "jabalpur": "જબલપુર",
    # EN: Ujjain
    "ujjain": "ઉજ્જૈન",
    # EN: Raipur
    "raipur": "રાયપુર",
    # EN: Bhilai
    "bhilai": "ભિલાઈ",
    # EN: Gaya
    "gaya": "ગયા",
    # EN: Bhagalpur
    "bhagalpur": "ભાગલપુર",
    # EN: Muzaffarpur
    "muzaffarpur": "મુઝફ્ફરપુર",
    # EN: Jamshedpur
    "jamshedpur": "જમશેદપુર",
    # EN: Dhanbad
    "dhanbad": "ધનબાદ",
    # EN: Deoghar
    "deoghar": "દેવઘર",
    # EN: Howrah
    "howrah": "હાવડા",
    # EN: Asansol
    "asansol": "આસનસોલ",
    # EN: Siliguri
    "siliguri": "સિલિગુડી",
    # EN: Cuttack
    "cuttack": "કટક",
    # EN: Puri
    "puri": "પુરી",
    # EN: Coimbatore
    "coimbatore": "કોઇમ્બતૂર",
    # EN: Madurai
    "madurai": "મદુરાઈ",
    # EN: Tiruchirappalli
    "tiruchirappalli": "તિરુચિરાપલ્લી",
    # EN: Salem
    "salem": "સેલમ",
    # EN: Rameswaram
    "rameswaram": "રામેશ્વરમ",
    # EN: Thiruvananthapuram
    "thiruvananthapuram": "તિરુવનંતપુરમ",
    # EN: Kozhikode
    "kozhikode": "કોઝિકોડ",
    # EN: Thrissur
    "thrissur": "ત્રિશૂર",
    # EN: Kollam
    "kollam": "કોલ્લમ",
    # EN: Kannur
    "kannur": "કન્નૂર",
    # EN: Malappuram
    "malappuram": "મલપ્પુરમ",
    # EN: Mysuru
    "mysuru": "મૈસૂરુ",
    # EN: Mangaluru
    "mangaluru": "મંગલુરુ",
    # EN: Hubballi
    "hubballi": "હુબલ્લી",
    # EN: Warangal
    "warangal": "વારંગલ",
    # EN: Vijayawada
    "vijayawada": "વિજયવાડા",
    # EN: Tirupati
    "tirupati": "તિરુપતિ",
    # EN: Guntur
    "guntur": "ગુંટૂર",
    # EN: Panaji
    "panaji": "પણજી",
    # EN: Shillong
    "shillong": "શિલોંગ",
    # EN: Imphal
    "imphal": "ઇમ્ફાલ",
    # EN: Agartala
    "agartala": "અગરતલા",
    # EN: Gangtok
    "gangtok": "ગંગટોક",
    # EN: Aizawl
    "aizawl": "આઇઝોલ",
    # EN: Kohima
    "kohima": "કોહિમા",
    # EN: Itanagar
    "itanagar": "ઇટાનગર",
    # EN: Puducherry
    "puducherry": "પુડુચેરી",
}

# app/seo_city_names.py STATES["gu"] — the states and union territories (key = English state name)  [32]
STATE_NAMES = {
    # EN: Andhra Pradesh
    "Andhra Pradesh": "આંધ્ર પ્રદેશ",
    # EN: Arunachal Pradesh
    "Arunachal Pradesh": "અરુણાચલ પ્રદેશ",
    # EN: Assam
    "Assam": "આસામ",
    # EN: Bihar
    "Bihar": "બિહાર",
    # EN: Chandigarh
    "Chandigarh": "ચંડીગઢ",
    # EN: Chhattisgarh
    "Chhattisgarh": "છત્તીસગઢ",
    # EN: Delhi
    "Delhi": "દિલ્હી",
    # EN: Goa
    "Goa": "ગોવા",
    # EN: Gujarat
    "Gujarat": "ગુજરાત",
    # EN: Haryana
    "Haryana": "હરિયાણા",
    # EN: Himachal Pradesh
    "Himachal Pradesh": "હિમાચલ પ્રદેશ",
    # EN: Jammu and Kashmir
    "Jammu and Kashmir": "જમ્મુ અને કાશ્મીર",
    # EN: Jharkhand
    "Jharkhand": "ઝારખંડ",
    # EN: Karnataka
    "Karnataka": "કર્ણાટક",
    # EN: Kerala
    "Kerala": "કેરળ",
    # EN: Madhya Pradesh
    "Madhya Pradesh": "મધ્ય પ્રદેશ",
    # EN: Maharashtra
    "Maharashtra": "મહારાષ્ટ્ર",
    # EN: Manipur
    "Manipur": "મણિપુર",
    # EN: Meghalaya
    "Meghalaya": "મેઘાલય",
    # EN: Mizoram
    "Mizoram": "મિઝોરમ",
    # EN: Nagaland
    "Nagaland": "નાગાલેન્ડ",
    # EN: Odisha
    "Odisha": "ઓડિશા",
    # EN: Puducherry
    "Puducherry": "પુડુચેરી",
    # EN: Punjab
    "Punjab": "પંજાબ",
    # EN: Rajasthan
    "Rajasthan": "રાજસ્થાન",
    # EN: Sikkim
    "Sikkim": "સિક્કિમ",
    # EN: Tamil Nadu
    "Tamil Nadu": "તમિલનાડુ",
    # EN: Telangana
    "Telangana": "તેલંગાણા",
    # EN: Tripura
    "Tripura": "ત્રિપુરા",
    # EN: Uttar Pradesh
    "Uttar Pradesh": "ઉત્તર પ્રદેશ",
    # EN: Uttarakhand
    "Uttarakhand": "ઉત્તરાખંડ",
    # EN: West Bengal
    "West Bengal": "પશ્ચિમ બંગાળ",
}

# app/astro/choghadiya.py CHOGHADIYA_INFO["gu"] — one-line description of each of the seven choghadiya slots  [7]
CHOGHADIYA_DESC = {
    # EN: Best time for all ceremonies, investments, agreements, and starting important endeavors.
    "Amrit": "બધા શુભ કાર્યો, રોકાણ, કરાર અને મહત્વના કામની શરૂઆત માટે સૌથી ઉત્તમ સમય.",
    # EN: Highly auspicious for ceremonies, religious rituals, education, and purchasing property.
    "Shubh": "શુભ પ્રસંગો, ધાર્મિક વિધિ, અભ્યાસ અને મિલકત ખરીદી માટે અત્યંત શુભ.",
    # EN: Favorable for business, trade, financial transactions, launching products, and interviews.
    "Labh": "વેપાર, લેવડદેવડ, નાણાકીય વ્યવહાર, નવી વસ્તુ બજારમાં મૂકવા અને ઇન્ટરવ્યૂ માટે અનુકૂળ.",
    # EN: Neutral. Excellent for journeys, travel, vehicle purchases, and shifting places.
    "Char": "મધ્યમ. મુસાફરી, પ્રવાસ, વાહન ખરીદી અને સ્થળ બદલવા માટે ઉત્તમ.",
    # EN: Inauspicious. Avoid medical procedures or conflict. Only suitable for competitive sports
    #     or defeating rivals.
    "Rog": "અશુભ. તબીબી પ્રક્રિયા કે ઝઘડાથી બચો. ફક્ત સ્પર્ધાત્મક રમતો અથવા હરીફોને હરાવવા માટે યોગ્ય.",
    # EN: Inauspicious. Ruled by Saturn; causes delays and setbacks. Avoid new ventures or signing
    #     documents.
    "Kaal": "અશુભ. શનિનો અધિકાર; વિલંબ અને અડચણો લાવે છે. નવું સાહસ શરૂ કરવાનું કે દસ્તાવેજ પર સહી કરવાનું ટાળો.",
    # EN: Inauspicious. Causes restlessness and anxiety. Favorable only for government filings or
    #     official duties.
    "Udveg": "અશુભ. બેચેની અને ચિંતા વધારે છે. ફક્ત સરકારી ફાઇલિંગ કે અધિકૃત ફરજો માટે અનુકૂળ.",
}

# ----------------------------------------------------------------------------
# rashifal  /rashifal and /rashifal/<sign>
# ----------------------------------------------------------------------------

# app/rashifal_text.py TEXT["gu"] — page text of /rashifal and /rashifal/<sign>  [63]
RASHIFAL_TEXT = {
    # EN: {house} house
    # keep: {house}
    "house_short": "{house} ભાવમાં",
    # EN: (retrograde)
    "rx": " (વક્રી)",
    # EN: Moon
    "planet.Moon": "ચંદ્ર",
    # EN: Saturn
    "planet.Saturn": "શનિ",
    # EN: Jupiter
    "planet.Jupiter": "ગુરુ",
    # EN: Rahu
    "planet.Rahu": "રાહુ",
    # EN: Ketu
    "planet.Ketu": "કેતુ",
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
    "crumb_root": "રાશિફળ",
    # EN: hi
    "sub_lang": 'gu',
    # EN: {name} Rashifal Today, {date_short} — {english} Daily Horoscope | {brand}
    # keep: {brand} {local}
    # may also use: {date_short} {date}
    "s.title": "આજનું {local} રાશિફળ, {date_short} — દૈનિક ભવિષ્ય | {brand}",
    # EN: {name} ({english} Moon sign) rashifal for {weekday}, {date}: the Moon transits your
    #     {house} house — {tone_lower}. Plus Saturn, Jupiter and Rahu–Ketu transits, Sade Sati
    #     status and today's tithi, computed from the sidereal sky.
    # keep: {date} {house} {local} {tone} {weekday}
    "s.desc": "{local} ચંદ્ર રાશિનું {weekday}, {date}નું રાશિફળ: ચંદ્ર તમારા {house} ભાવમાં ગોચર કરે છે — {tone}. સાથે શનિ, ગુરુ અને રાહુ–કેતુનું ગોચર, સાડાસાતીની સ્થિતિ અને આજની તિથિ, નિરયન આકાશ પરથી ગણેલી.",
    # EN: {name} Rashifal Today — {english} Daily Horoscope
    # keep: {local}
    "s.h1": "આજનું {local} રાશિફળ",
    # EN: आज का {name_hi} राशिफल
    # may also use: {local}
    "s.sub": "ચંદ્ર ગોચર પરથી આજનું દૈનિક ભવિષ્ય — {local}",
    # EN: the Moon is in your {house} house from {name}.
    # keep: {house}
    "s.summary": "ચંદ્ર તમારા {house} ભાવમાં છે.",
    # EN: About {name} rashi — traits, nakshatras and name letters
    # keep: {local}
    "s.about_rashi": "{local} રાશિ વિશે — સ્વભાવ, નક્ષત્ર અને નામના અક્ષર",
    # EN: Today's Moon transit (Chandra gochar)
    "moon.head": "આજનું ચંદ્ર ગોચર",
    # EN: The Moon is in {sign} all day — your {house} house.
    # keep: {house} {sign}
    "moon.allday": "ચંદ્ર આખો દિવસ {sign}માં છે — તમારા {house} ભાવમાં.",
    # EN: <strong>Until {time} IST:</strong> the Moon is in {sign} — your {house} house.
    # keep: {house} {sign} {time}
    "moon.until": "<strong>{time} IST સુધી:</strong> ચંદ્ર {sign}માં છે — તમારા {house} ભાવમાં.",
    # EN: <strong>From {time} IST:</strong> the Moon enters {sign} — your {house} house.
    # keep: {house} {sign} {time}
    "moon.from": "<strong>{time} IST થી:</strong> ચંદ્ર {sign}માં પ્રવેશે છે — તમારા {house} ભાવમાં.",
    # EN: <p>The Moon changes sign during the day, so the day reads in two parts.</p>
    "moon.two": "<p>ચંદ્ર દિવસ દરમિયાન રાશિ બદલે છે, તેથી દિવસનું ફળ બે ભાગમાં વંચાય છે.</p>",
    # EN: The longer backdrop: slow transits
    "back.head": "લાંબી પૃષ્ઠભૂમિ: ધીમાં ગોચર",
    # EN: <p>These planets stay in one sign for months or years, so they set the background against
    #     which each day plays out.</p>
    "back.intro": "<p>આ ગ્રહો મહિનાઓ કે વર્ષો સુધી એક જ રાશિમાં રહે છે, તેથી તે પૃષ્ઠભૂમિ બનાવે છે જેના પર દરેક દિવસ ચાલે છે.</p>",
    # EN: {sign}{rx} · {house} house
    # keep: {house} {rx} {sign}
    "back.where": "{sign}{rx} · {house} ભાવમાં",
    # EN: first (rising)
    "phase.1": "પ્રથમ (ઉદય)",
    # EN: second (peak)
    "phase.2": "બીજો (શિખર)",
    # EN: third (setting)
    "phase.3": "ત્રીજો (અસ્ત)",
    # EN: <strong>Sade Sati is running</strong> — the {phase} phase. It is a slow, disciplining
    #     period rather than something to fear; steady routine, service and patience make it
    #     lighter.
    # keep: {phase}
    "sade.running": "<strong>સાડાસાતી ચાલી રહી છે</strong> — {phase} તબક્કો. આ ડરવા જેવો નહીં, પણ ધીમો અને શિસ્ત શીખવતો સમય છે; નિયમિત દિનચર્યા, સેવા અને ધીરજથી તે હળવો બને છે.",
    # EN: <strong>No Sade Sati</strong>, but Saturn's Dhaiya is running (see above).
    "sade.dhaiya": "<strong>સાડાસાતી નથી</strong>, પણ શનિની ઢૈયા ચાલી રહી છે (ઉપર જુઓ).",
    # EN: <strong>No Sade Sati</strong> — Saturn is not in the 12th, 1st or 2nd from your sign.
    "sade.none": "<strong>સાડાસાતી નથી</strong> — શનિ તમારી રાશિથી 12મા, 1લા કે 2જા ભાવમાં નથી.",
    # EN: <h2>Today's Panchang</h2><p>At sunrise in New Delhi it is <strong>{paksha}
    #     {tithi}</strong> tithi with the Moon in <strong>{nakshatra}</strong> nakshatra. Rahu Kaal,
    #     sunrise and the full almanac are on <a href="/panchang">today's Panchang</a>.</p>
    # keep: {nakshatra} {tithi}
    # may also use: {paksha_full} {paksha}
    "panchang": "<h2>આજનું પંચાંગ</h2><p>નવી દિલ્હીમાં સૂર્યોદય સમયે <strong>{paksha} {tithi}</strong> છે અને ચંદ્ર <strong>{nakshatra}</strong> નક્ષત્રમાં છે. રાહુકાળ, સૂર્યોદય અને પૂરું પંચાંગ <a href=\"/panchang\">આજના પંચાંગ</a> પર જુઓ.</p>",
    # EN: <p class="note">This rashifal is read from your Moon sign alone — the same for everyone
    #     born with the Moon in that sign. A personal reading uses your full birth chart: the
    #     ascendant, your running dasha and the ashtakavarga strength of each transit. Not sure of
    #     your Moon sign (rashi)? It is the first thing your free kundali shows — it is usually not
    #     your Western sun sign.</p>
    "personal": "<p class=\"note\">આ રાશિફળ ફક્ત તમારી ચંદ્ર રાશિ પરથી વંચાય છે — તે રાશિમાં ચંદ્ર સાથે જન્મેલા બધા માટે સમાન. અંગત વાચન તમારી પૂરી જન્મકુંડળી વાપરે છે: લગ્ન, તમારી ચાલતી દશા અને દરેક ગોચરનું અષ્ટકવર્ગ બળ. તમારી ચંદ્ર રાશિ ખબર નથી? તે તમારી મફત કુંડળીમાં સૌથી પહેલી દેખાય છે — તે સામાન્ય રીતે તમારી પશ્ચિમી સૂર્ય રાશિ નથી હોતી.</p>",
    # EN: Get your free kundali — then ask a question about your own chart
    "cta": "તમારી મફત કુંડળી મેળવો — પછી તમારી પોતાની કુંડળી વિશે પ્રશ્ન પૂછો",
    # EN: Today's Rashifal for every sign
    "signs.head": "દરેક રાશિનું આજનું રાશિફળ",
    # EN: More free tools
    "more.head": "વધુ મફત સાધનો",
    # EN: <h2>How this is calculated</h2><p>Planet positions are computed for today (IST) with the
    #     Swiss Ephemeris in the sidereal zodiac (Lahiri ayanamsa) — the same positions our kundali
    #     and panchang use. Houses are counted from your Moon sign, as in classical gochar. Which
    #     houses are favourable follows the scheme of Varahamihira's Brihat Samhita (ch. 104) and
    #     Mantreswara's Phaladeepika (ch. 26): the Moon is favourable in the 1st, 3rd, 6th, 7th,
    #     10th and 11th; Saturn, Rahu and Ketu in the 3rd, 6th and 11th; Jupiter in the 2nd, 5th,
    #     7th, 9th and 11th.</p>
    "method": "<h2>આ ગણતરી કેવી રીતે થાય છે</h2><p>ગ્રહોની સ્થિતિ આજ માટે (IST) સ્વિસ એફેમેરિસથી નિરયન રાશિચક્ર (લાહિરી અયનાંશ)માં ગણાય છે — તે જ સ્થિતિ જે અમારી કુંડળી અને પંચાંગ વાપરે છે. શાસ્ત્રીય ગોચરની જેમ ભાવ તમારી ચંદ્ર રાશિથી ગણાય છે. કયા ભાવ અનુકૂળ ગણાય તે વરાહમિહિરની બૃહત્સંહિતા (અ. 104) અને મંત્રેશ્વરના ફલદીપિકા (અ. 26)ની રીત મુજબ છે: ચંદ્ર 1લા, 3જા, 6ઠ્ઠા, 7મા, 10મા અને 11મા ભાવમાં અનુકૂળ; શનિ, રાહુ અને કેતુ 3જા, 6ઠ્ઠા અને 11મા ભાવમાં; ગુરુ 2જા, 5મા, 7મા, 9મા અને 11મા ભાવમાં.</p>",
    # EN: Aaj Ka Rashifal, {date_short} — Today's Horoscope for All 12 Signs | {brand}
    # keep: {brand}
    # may also use: {date_short} {date}
    "i.title": "આજનું રાશિફળ, {date_short} — બધી 12 રાશિનું દૈનિક ભવિષ્ય | {brand}",
    # EN: Today's rashifal for {weekday}, {date}: daily horoscope for all 12 Moon signs from Mesh to
    #     Meen — Moon transit, Saturn, Jupiter and Rahu, and Sade Sati, computed from the sidereal
    #     sky.
    # keep: {date} {weekday}
    "i.desc": "{weekday}, {date}નું રાશિફળ: મેષથી મીન સુધી બધી 12 ચંદ્ર રાશિનું દૈનિક ભવિષ્ય — ચંદ્ર ગોચર, શનિ, ગુરુ અને રાહુ, અને સાડાસાતી, નિરયન આકાશ પરથી ગણેલું.",
    # EN: Today's Rashifal — Daily Horoscope
    "i.h1": "આજનું રાશિફળ — દૈનિક ભવિષ્ય",
    # EN: आज का राशिफल — सभी 12 राशियाँ
    "i.sub": "આજનું રાશિફળ — બધી 12 રાશિ",
    # EN: <p>Rashifal is read from your <strong>Moon sign</strong> (rashi). {moon_text} Saturn is in
    #     {sat_sign}, so Sade Sati is running for {sade_names}.</p>
    # keep: {moon_text} {sade_names} {sat_sign}
    "i.intro": "<p>રાશિફળ તમારી <strong>ચંદ્ર રાશિ</strong> પરથી વંચાય છે. {moon_text} શનિ {sat_sign}માં છે, તેથી {sade_names} માટે સાડાસાતી ચાલી રહી છે.</p>",
    # EN: The Moon is in {now} until {time} IST, then in {next}. The table shows the position for
    #     most of the day.
    # keep: {next} {now} {time}
    "i.moon_two": "ચંદ્ર {time} IST સુધી {now}માં છે, પછી {next}માં. કોષ્ટકમાં દિવસના મોટા ભાગની સ્થિતિ બતાવી છે.",
    # EN: The Moon is in {now} all day.
    # keep: {now}
    "i.moon_one": "ચંદ્ર આખો દિવસ {now}માં છે.",
    # EN: {name} <small>{english}</small>
    # keep: {local}
    "i.name": "{local}",
    # EN: <small>Sade Sati</small>
    "i.sade": "<small>સાડાસાતી</small>",
    # EN: <tr><th>Sign</th><th>Moon in your</th><th>Today</th></tr>
    "i.head_row": "<tr><th>રાશિ</th><th>તમારી રાશિથી ચંદ્ર</th><th>આજે</th></tr>",
    # EN: Sign not found
    "nf.title": "રાશિ મળી નથી",
    # EN: <h1>Sign not found</h1><p>There is no rashi called “{slug}”. Pick your Moon sign
    #     below.</p>
    # keep: {slug}
    "nf.body": "<h1>રાશિ મળી નથી</h1><p>“{slug}” નામની કોઈ રાશિ નથી. નીચેથી તમારી ચંદ્ર રાશિ પસંદ કરો.</p>",
    # EN: 1st
    "house.1": "1લા",
    # EN: 2nd
    "house.2": "2જા",
    # EN: 3rd
    "house.3": "3જા",
    # EN: 4th
    "house.4": "4થા",
    # EN: 5th
    "house.5": "5મા",
    # EN: 6th
    "house.6": "6ઠ્ઠા",
    # EN: 7th
    "house.7": "7મા",
    # EN: 8th
    "house.8": "8મા",
    # EN: 9th
    "house.9": "9મા",
    # EN: 10th
    "house.10": "10મા",
    # EN: 11th
    "house.11": "11મા",
    # EN: 12th
    "house.12": "12મા",
}

# app/rashifal_text.py MORE_LINKS["gu"] — 'More free tools' links: keep every href, translate the text; the first href is '{twin:en}' (this page in English)  [6]
RASHIFAL_MORE_LINKS = (
    # EN href: {twin:en}
    # EN text: Read in English
    ("{twin:en}", "અંગ્રેજીમાં વાંચો"),
    # EN href: /panchang
    # EN text: Today's Panchang
    ("/panchang", "આજનું પંચાંગ"),
    # EN href: /rahu-kaal
    # EN text: Rahu Kaal today
    ("/rahu-kaal", "આજનો રાહુકાળ"),
    # EN href: /choghadiya
    # EN text: Choghadiya today
    ("/choghadiya", "આજનાં ચોઘડિયાં"),
    # EN href: /kundali-milan
    # EN text: Kundali Milan
    ("/kundali-milan", "કુંડળી મિલન"),
    # EN href: /vrat-tyohar
    # EN text: Today's vrat & festivals
    ("/vrat-tyohar", "આજનાં વ્રત અને તહેવાર"),
)

# app/rashifal_text.py TONE_LABEL["gu"] — the three day tones (keys good / mixed / easy)  [3]
RASHIFAL_TONE_LABEL = {
    # EN: Favourable day
    "good": "અનુકૂળ દિવસ",
    # EN: Mixed day
    "mixed": "મિશ્ર દિવસ",
    # EN: Take it easy
    "easy": "આજે શાંતિથી કામ લો",
}

# app/rashifal_text.py MOON_HOUSE["gu"] — Moon transit through houses 1-12 (key = house number)  [12]
RASHIFAL_MOON_HOUSE = {
    # EN: The Moon moves through your own sign today (Janma Chandra). Classical texts read this as a
    #     day of comfort and good spirits — good food, warm company and a clear sense of yourself. A
    #     good day to look after your own needs and begin small, personal things.
    1: "ચંદ્ર આજે તમારી જ રાશિમાં ફરે છે (જન્મ ચંદ્ર). શાસ્ત્રો આને સુખ અને પ્રસન્નતાનો દિવસ ગણે છે — સારું ભોજન, સ્નેહીઓનો સાથ અને પોતાની સ્પષ્ટ સમજ. પોતાની જરૂરિયાતો સંભાળવા અને નાનાં, અંગત કામ શરૂ કરવા માટે સારો દિવસ.",
    # EN: The Moon is in your 2nd house today. Tradition asks for care with money and words —
    #     expenses can creep up and small misunderstandings arise easily. Keep spending planned and
    #     speak gently at home; routine work goes fine.
    2: "ચંદ્ર આજે તમારા 2જા ભાવમાં છે. પરંપરા પૈસા અને વાણીમાં સંભાળ રાખવાનું કહે છે — ખર્ચ ધીરે ધીરે વધી શકે છે અને નાની ગેરસમજ સહેલાઈથી થાય છે. ખર્ચ આયોજનબદ્ધ રાખો અને ઘરમાં મીઠાશથી બોલો; રોજિંદું કામ સારી રીતે ચાલશે.",
    # EN: The Moon in your 3rd house is a favourable transit. Courage and initiative are high,
    #     effort brings results, and contact with siblings, friends and neighbours goes well. A good
    #     day for short trips, calls and pushing a pending task over the line.
    3: "તમારા 3જા ભાવમાં ચંદ્ર અનુકૂળ ગોચર છે. હિંમત અને પહેલ ઊંચી છે, પ્રયત્નનું ફળ મળે છે, અને ભાઈ-બહેન, મિત્રો તથા પડોશીઓ સાથે સંબંધ સારો રહે છે. ટૂંકી મુસાફરી, ફોન કરવા અને બાકી પડેલું કામ પૂરું કરવા માટે સારો દિવસ.",
    # EN: The Moon in your 4th house can leave the mind a little unsettled — home matters or travel
    #     may feel tiring. Keep the day simple, avoid arguments at home and give yourself some quiet
    #     time; the mood lifts as the Moon moves on.
    4: "તમારા 4થા ભાવમાં ચંદ્ર મનને થોડું અશાંત રાખી શકે છે — ઘરની બાબતો કે મુસાફરી થકવનારી લાગી શકે. દિવસ સાદો રાખો, ઘરમાં દલીલ ટાળો અને થોડો શાંત સમય જાતને આપો; ચંદ્ર આગળ વધશે તેમ મન હળવું થશે.",
    # EN: The Moon in your 5th house is a mixed transit. Plans may meet small hurdles and the mind
    #     can swing between ideas. Avoid speculative decisions; study, creative work and time with
    #     children are better uses of the day.
    5: "તમારા 5મા ભાવમાં ચંદ્ર મિશ્ર ગોચર છે. યોજનાઓમાં નાની અડચણો આવી શકે અને મન વિચારો વચ્ચે ડોલતું રહે. સટ્ટાકીય નિર્ણયો ટાળો; અભ્યાસ, સર્જનાત્મક કામ અને બાળકો સાથેનો સમય દિવસનો સારો ઉપયોગ છે.",
    # EN: The Moon in your 6th house is one of its best transits. Classical texts promise success
    #     over rivals and obstacles, and the energy to clear a backlog. A good day for competitive
    #     work, settling pending issues and steady routines.
    6: "તમારા 6ઠ્ઠા ભાવમાં ચંદ્ર તેનાં શ્રેષ્ઠ ગોચરમાંનું એક છે. શાસ્ત્રો હરીફો અને અડચણો પર વિજય તથા બાકી કામ ઉકેલવાની શક્તિ આપે છે. સ્પર્ધાત્મક કામ, બાકી મુદ્દા પતાવવા અને સ્થિર દિનચર્યા માટે સારો દિવસ.",
    # EN: The Moon in your 7th house favours partnership and company. Time with your spouse or
    #     partner, meetings and agreements tend to go smoothly, with comfort and good food. A good
    #     day to reach out and work together.
    7: "તમારા 7મા ભાવમાં ચંદ્ર ભાગીદારી અને સાથને અનુકૂળ છે. જીવનસાથી કે ભાગીદાર સાથેનો સમય, મુલાકાતો અને કરારો સરળતાથી પાર પડે છે, સાથે સુખ અને સારું ભોજન. સંપર્ક કરવા અને સાથે મળીને કામ કરવા માટે સારો દિવસ.",
    # EN: The Moon is in your 8th house — the period known as Chandrashtama. Tradition advises
    #     against starting important new things today; unexpected delays are more likely and the
    #     mind can feel anxious. Keep a margin in your schedule, stick to familiar work and be
    #     gentle with yourself — it passes within two to three days.
    8: "ચંદ્ર તમારા 8મા ભાવમાં છે — જે સમય ચંદ્રાષ્ટમ તરીકે ઓળખાય છે. પરંપરા આજે કોઈ મહત્વનું નવું કામ શરૂ ન કરવાની સલાહ આપે છે; અણધાર્યા વિલંબની શક્યતા વધારે છે અને મન ચિંતિત લાગી શકે. કાર્યક્રમમાં થોડો સમય ખુલ્લો રાખો, જાણીતા કામને વળગી રહો અને પોતાની સાથે નરમ રહો — બે-ત્રણ દિવસમાં તે પસાર થઈ જાય છે.",
    # EN: The Moon in your 9th house is a mixed transit. Plans may need extra effort and you may
    #     feel tired or distracted. Prayer, reading and time with elders or teachers suit the day
    #     better than big new ventures.
    9: "તમારા 9મા ભાવમાં ચંદ્ર મિશ્ર ગોચર છે. યોજનાઓમાં વધારે મહેનત લાગી શકે અને તમે થાકેલા કે વિચલિત અનુભવી શકો. મોટાં નવાં સાહસો કરતાં પ્રાર્થના, વાંચન અને વડીલો કે ગુરુજનો સાથેનો સમય દિવસને વધારે અનુકૂળ છે.",
    # EN: The Moon in your 10th house supports work and reputation. Tasks get done, seniors are
    #     receptive and effort is noticed. A good day to present your work, take a professional step
    #     or finish something visible.
    10: "તમારા 10મા ભાવમાં ચંદ્ર કામ અને પ્રતિષ્ઠાને ટેકો આપે છે. કામ પૂરાં થાય છે, ઉપરી અધિકારીઓ ગ્રહણશીલ હોય છે અને પ્રયત્નની નોંધ લેવાય છે. તમારું કામ રજૂ કરવા, વ્યાવસાયિક પગલું ભરવા કે દેખીતું કામ પૂરું કરવા માટે સારો દિવસ.",
    # EN: The Moon in your 11th house — the house of gains — is a very favourable transit. Expect
    #     support from friends, good news and the fruit of earlier effort. A good day for
    #     networking, making requests and celebrating with others.
    11: "તમારા 11મા ભાવમાં ચંદ્ર — લાભનો ભાવ — ખૂબ અનુકૂળ ગોચર છે. મિત્રોનો સહકાર, સારા સમાચાર અને અગાઉના પ્રયત્નનું ફળ મળવાની આશા રાખો. સંપર્કો વધારવા, વિનંતી કરવા અને બીજાઓ સાથે ઉજવણી કરવા માટે સારો દિવસ.",
    # EN: The Moon in your 12th house can bring extra expenses and a tired, inward mood. Avoid
    #     overspending and late nights; the day suits rest, prayer, charity and finishing old work
    #     rather than starting new.
    12: "તમારા 12મા ભાવમાં ચંદ્ર વધારાનો ખર્ચ અને થાકેલો, અંતર્મુખ મિજાજ લાવી શકે. વધારે ખર્ચ અને મોડી રાત સુધી જાગવાનું ટાળો; આરામ, પ્રાર્થના, દાન અને જૂનું કામ પૂરું કરવા માટે દિવસ યોગ્ય છે, નવું શરૂ કરવા માટે નહીં.",
}

# app/rashifal_text.py SATURN_HOUSE["gu"] — Saturn transit through houses 1-12  [12]
RASHIFAL_SATURN_HOUSE = {
    # EN: Saturn is passing over your Moon sign — the peak phase of Sade Sati. It rewards patience,
    #     routine and honest effort; take on a little less and finish what you start.
    1: "શનિ તમારી ચંદ્ર રાશિ પરથી પસાર થઈ રહ્યો છે — સાડાસાતીનો શિખર તબક્કો. તે ધીરજ, નિયમિતતા અને પ્રામાણિક મહેનતનું ફળ આપે છે; થોડું ઓછું હાથ પર લો અને જે શરૂ કરો તે પૂરું કરો.",
    # EN: Saturn is in your 2nd — the last phase of Sade Sati. Be measured with spending and with
    #     words at home; the pressure is easing.
    2: "શનિ તમારા 2જા ભાવમાં છે — સાડાસાતીનો અંતિમ તબક્કો. ખર્ચમાં અને ઘરમાં બોલવામાં સંયમ રાખો; દબાણ હળવું થઈ રહ્યું છે.",
    # EN: Saturn in your 3rd is one of its best positions — steady effort pays, courage grows and
    #     long-running work gains traction.
    3: "શનિ તમારા 3જા ભાવમાં તેની શ્રેષ્ઠ સ્થિતિઓમાંની એક છે — સતત પ્રયત્ન ફળે છે, હિંમત વધે છે અને લાંબા સમયથી ચાલતા કામને ગતિ મળે છે.",
    # EN: Saturn in your 4th (Dhaiya, Kantaka Shani) can make home life and peace of mind feel
    #     heavier; keep routines simple and handle family matters calmly.
    4: "શનિ તમારા 4થા ભાવમાં (ઢૈયા, કંટક શનિ) ઘરના જીવન અને મનની શાંતિને ભારે બનાવી શકે; દિનચર્યા સાદી રાખો અને કુટુંબની બાબતો શાંતિથી સંભાળો.",
    # EN: Saturn in your 5th asks for patience with plans, studies and children's matters — slow and
    #     careful beats quick.
    5: "શનિ તમારા 5મા ભાવમાં યોજનાઓ, અભ્યાસ અને સંતાનની બાબતોમાં ધીરજ માગે છે — ઉતાવળ કરતાં ધીમે અને સાવચેતીથી ચાલવું સારું.",
    # EN: Saturn in your 6th works in your favour — discipline wins over rivals and backlog, and
    #     hard work gets noticed.
    6: "શનિ તમારા 6ઠ્ઠા ભાવમાં તમારા પક્ષમાં કામ કરે છે — શિસ્ત હરીફો અને બાકી કામ પર વિજય અપાવે છે, અને સખત મહેનતની નોંધ લેવાય છે.",
    # EN: Saturn in your 7th puts partnerships in a slow, serious light — clear agreements and
    #     patience help.
    7: "શનિ તમારા 7મા ભાવમાં ભાગીદારીને ધીમા, ગંભીર પ્રકાશમાં મૂકે છે — સ્પષ્ટ કરારો અને ધીરજ મદદ કરે છે.",
    # EN: Saturn in your 8th (Dhaiya, Ashtama Shani) is a time to avoid shortcuts and keep a margin
    #     for delays.
    8: "શનિ તમારા 8મા ભાવમાં (ઢૈયા, અષ્ટમ શનિ) ટૂંકા રસ્તા ટાળવાનો અને વિલંબ માટે સમય ખુલ્લો રાખવાનો સમય છે.",
    # EN: Saturn in your 9th can slow luck and long journeys; respect for elders and steady duty
    #     keep things on track.
    9: "શનિ તમારા 9મા ભાવમાં ભાગ્ય અને લાંબી મુસાફરીને ધીમી કરી શકે; વડીલોનું સન્માન અને સ્થિર ફરજપાલન બધું પાટા પર રાખે છે.",
    # EN: Saturn in your 10th brings responsibility at work — a heavier load, but sincere effort
    #     builds a lasting reputation.
    10: "શનિ તમારા 10મા ભાવમાં કામ પર જવાબદારી લાવે છે — ભાર વધારે, પણ નિષ્ઠાવાન પ્રયત્ન કાયમી પ્રતિષ્ઠા બનાવે છે.",
    # EN: Saturn in your 11th is favourable — gains come slowly but surely, and long effort starts
    #     to pay off.
    11: "શનિ તમારા 11મા ભાવમાં અનુકૂળ છે — લાભ ધીમે પણ ચોક્કસ આવે છે અને લાંબી મહેનત ફળવા લાગે છે.",
    # EN: Saturn is in your 12th — the opening phase of Sade Sati. Watch expenses and rest well; a
    #     good time for quiet, inward work.
    12: "શનિ તમારા 12મા ભાવમાં છે — સાડાસાતીનો પ્રથમ તબક્કો. ખર્ચ પર ધ્યાન રાખો અને પૂરતો આરામ કરો; શાંત, અંતર્મુખ કામ માટે સારો સમય.",
}

# app/rashifal_text.py JUPITER_HOUSE["gu"] — Jupiter transit through houses 1-12  [12]
RASHIFAL_JUPITER_HOUSE = {
    # EN: Jupiter over your Moon sign is classically a restless position; keep plans grounded and
    #     avoid over-committing.
    1: "તમારી ચંદ્ર રાશિ પર ગુરુ શાસ્ત્ર મુજબ અસ્થિર સ્થિતિ છે; યોજનાઓ વ્યવહારુ રાખો અને વધારે પડતી જવાબદારી ન લો.",
    # EN: Jupiter in your 2nd supports family harmony, savings and kind speech.
    2: "ગુરુ તમારા 2જા ભાવમાં કુટુંબમાં સુમેળ, બચત અને મીઠી વાણીને ટેકો આપે છે.",
    # EN: Jupiter in your 3rd asks a little more effort for the same result — keep at it.
    3: "ગુરુ તમારા 3જા ભાવમાં એ જ પરિણામ માટે થોડી વધારે મહેનત માગે છે — લાગ્યા રહો.",
    # EN: Jupiter in your 4th can unsettle home matters; patience with relatives helps.
    4: "ગુરુ તમારા 4થા ભાવમાં ઘરની બાબતોમાં અશાંતિ લાવી શકે; સગાંઓ સાથે ધીરજ રાખવાથી મદદ મળે છે.",
    # EN: Jupiter in your 5th favours learning, children's matters, creativity and good counsel.
    5: "ગુરુ તમારા 5મા ભાવમાં અભ્યાસ, સંતાનની બાબતો, સર્જનાત્મકતા અને સારી સલાહને અનુકૂળ છે.",
    # EN: Jupiter in your 6th: steer clear of small disputes and overwork.
    6: "ગુરુ તમારા 6ઠ્ઠા ભાવમાં: નાના વિવાદો અને વધુ પડતા કામથી દૂર રહો.",
    # EN: Jupiter in your 7th blesses partnerships, marriage talks and travel.
    7: "ગુરુ તમારા 7મા ભાવમાં ભાગીદારી, લગ્નની વાતચીત અને મુસાફરીને આશીર્વાદ આપે છે.",
    # EN: Jupiter in your 8th suggests care with big decisions — go slow.
    8: "ગુરુ તમારા 8મા ભાવમાં મોટા નિર્ણયોમાં સાવચેતી સૂચવે છે — ધીમે ચાલો.",
    # EN: Jupiter in your 9th is one of its best positions — fortune, dharma and guidance from
    #     teachers.
    9: "ગુરુ તમારા 9મા ભાવમાં તેની શ્રેષ્ઠ સ્થિતિઓમાંની એક છે — ભાગ્ય, ધર્મ અને ગુરુજનોનું માર્ગદર્શન.",
    # EN: Jupiter in your 10th may bring changes at work; stay adaptable.
    10: "ગુરુ તમારા 10મા ભાવમાં કામ પર ફેરફાર લાવી શકે; અનુકૂલનશીલ રહો.",
    # EN: Jupiter in your 11th brings gains, fulfilled wishes and helpful friends.
    11: "ગુરુ તમારા 11મા ભાવમાં લાભ, ઇચ્છાપૂર્તિ અને મદદરૂપ મિત્રો લાવે છે.",
    # EN: Jupiter in your 12th brings expenses, often on good causes; charity and spiritual practice
    #     are well placed.
    12: "ગુરુ તમારા 12મા ભાવમાં ખર્ચ લાવે છે, જે મોટે ભાગે સારા કામ માટે હોય; દાન અને આધ્યાત્મિક સાધના યોગ્ય રહે છે.",
}

# app/rashifal_text.py RAHU_HOUSE["gu"] — Rahu transit through houses 1-12  [12]
RASHIFAL_RAHU_HOUSE = {
    # EN: Rahu over your Moon sign can stir restlessness and unusual wants; stay grounded.
    1: "તમારી ચંદ્ર રાશિ પર રાહુ બેચેની અને અસામાન્ય ઇચ્છાઓ જગાડી શકે; ધરતી પર પગ રાખો.",
    # EN: Rahu in your 2nd: take care with speech and money talk within the family.
    2: "રાહુ તમારા 2જા ભાવમાં: કુટુંબમાં વાણી અને પૈસાની વાતોમાં સંભાળ રાખો.",
    # EN: Rahu in your 3rd is favourable — bold initiatives and communication succeed.
    3: "રાહુ તમારા 3જા ભાવમાં અનુકૂળ છે — હિંમતભરી પહેલ અને સંવાદમાં સફળતા મળે છે.",
    # EN: Rahu in your 4th can unsettle domestic peace; avoid hasty property moves.
    4: "રાહુ તમારા 4થા ભાવમાં ઘરની શાંતિ ડગમગાવી શકે; મિલકત અંગે ઉતાવળિયાં પગલાં ટાળો.",
    # EN: Rahu in your 5th: double-check risky ideas and keep a clear head.
    5: "રાહુ તમારા 5મા ભાવમાં: જોખમી વિચારો બે વાર તપાસો અને મન શાંત રાખો.",
    # EN: Rahu in your 6th helps you get past competition and obstacles.
    6: "રાહુ તમારા 6ઠ્ઠા ભાવમાં સ્પર્ધા અને અડચણો પાર કરવામાં મદદ કરે છે.",
    # EN: Rahu in your 7th: keep partnerships transparent.
    7: "રાહુ તમારા 7મા ભાવમાં: ભાગીદારીમાં પારદર્શિતા રાખો.",
    # EN: Rahu in your 8th: avoid risky shortcuts and stay calm when the unexpected comes.
    8: "રાહુ તમારા 8મા ભાવમાં: જોખમી ટૂંકા રસ્તા ટાળો અને અણધાર્યું આવે ત્યારે શાંત રહો.",
    # EN: Rahu in your 9th can raise doubts about beliefs or mentors; seek advice you trust.
    9: "રાહુ તમારા 9મા ભાવમાં માન્યતાઓ કે માર્ગદર્શકો અંગે શંકા જગાડી શકે; ભરોસાપાત્ર સલાહ લો.",
    # EN: Rahu in your 10th brings ambition and sudden openings at work; move with integrity.
    10: "રાહુ તમારા 10મા ભાવમાં મહત્વાકાંક્ષા અને કામ પર અચાનક તકો લાવે છે; પ્રામાણિકતાથી આગળ વધો.",
    # EN: Rahu in your 11th — gains through networks and new contacts.
    11: "રાહુ તમારા 11મા ભાવમાં — સંપર્કો અને નવા પરિચયો દ્વારા લાભ.",
    # EN: Rahu in your 12th: watch hidden expenses and get proper rest.
    12: "રાહુ તમારા 12મા ભાવમાં: છુપાયેલા ખર્ચ પર ધ્યાન રાખો અને પૂરતો આરામ કરો.",
}

# app/rashifal_text.py KETU_LINE["gu"] — Ketu line, True = favourable house, False = quiet house; {n} is the house  [2]
RASHIFAL_KETU_LINE = {
    # EN: Ketu in your {n} house works quietly in your favour — obstacles clear with less fuss.
    # keep: {n}
    True: "કેતુ તમારા {n} ભાવમાં શાંતિથી તમારા પક્ષમાં કામ કરે છે — અડચણો ઓછી ધમાલે દૂર થાય છે.",
    # EN: Ketu in your {n} house is a quieter, inward influence — good for reflection and spiritual
    #     practice, less so for impulsive moves.
    # keep: {n}
    False: "કેતુ તમારા {n} ભાવમાં શાંત, અંતર્મુખ પ્રભાવ છે — ચિંતન અને આધ્યાત્મિક સાધના માટે સારો, ઉતાવળિયાં પગલાં માટે નહીં.",
}

# app/rashifal_text.py CLOCK_LANG["gu"] — leave '' (the language's own clock words); 'en' prints 6:29 AM as Hindi pages do
# (optional: may stay empty)
RASHIFAL_CLOCK_LANG = ""

# ----------------------------------------------------------------------------
# vrat      /vrat-tyohar /ekadashi-<year> /tyohar/<slug>-<year>
# ----------------------------------------------------------------------------

# app/vrat_text.py TEXT["gu"] — page text of /vrat-tyohar, /ekadashi-<year>, /tyohar/<slug>-<year>  [64]
VRAT_TEXT = {
    # EN: Vrat & festivals
    "crumb": "વ્રત અને તહેવાર",
    # EN: {date}, {weekday}
    # keep: {date} {weekday}
    "day_label": "{date}, {weekday}",
    # EN: {label}: {prefix}{value}
    # keep: {label} {prefix} {value}
    "timing": "{label}: {prefix}{value}",
    # EN: {paksha} {name}: {start} to {end}
    # keep: {end} {name} {paksha} {start}
    "tithi.text": "{paksha} {name}: {start} થી {end} સુધી",
    # EN: {paksha}
    # keep: {paksha}
    "tithi.paksha": "{paksha} પક્ષ",
    # EN: <tr><th>Date</th><th>Vrat / festival</th><th>Timing ({city})</th></tr>
    # keep: {city}
    "table.th": "<tr><th>તારીખ</th><th>વ્રત / તહેવાર</th><th>સમય ({city})</th></tr>",
    # EN: <div class="box"><p><strong>Timings vary by city.</strong> Every time here is for {city}'s
    #     sunrise, sunset and moonrise; in another city they shift by a few minutes and occasionally
    #     the date does too. Dates follow Drik Panchang's Smarta (default) reckoning. Check the
    #     Panchang for your own city.</p></div>
    # keep: {city}
    "city_note": "<div class=\"box\"><p><strong>સમય શહેર પ્રમાણે બદલાય છે.</strong> અહીંના બધા સમય {city}ના સૂર્યોદય, સૂર્યાસ્ત અને ચંદ્રોદય મુજબ છે; બીજા શહેરમાં તે થોડી મિનિટ ખસે છે અને ક્યારેક તારીખ પણ બદલાય છે. તારીખો દ્રિક પંચાંગની સ્માર્ત (મુખ્ય) ગણતરી મુજબ છે. તમારા પોતાના શહેરનું પંચાંગ જુઓ.</p></div>",
    # EN: <p class="note"><small>For most observances the date is the same across India, but puja
    #     muhurat, parana and moonrise times differ from city to city - every time here is for
    #     <strong>{city}</strong>. Regional traditions may vary.</small></p>
    # keep: {city}
    "top_note": "<p class=\"note\"><small>મોટા ભાગનાં વ્રત-તહેવારોની તારીખ આખા ભારતમાં સમાન હોય છે, પણ પૂજા મુહૂર્ત, પારણાં અને ચંદ્રોદયના સમય શહેર પ્રમાણે જુદા હોય છે - અહીંના બધા સમય <strong>{city}</strong> માટે છે. પ્રાદેશિક પરંપરાઓમાં ફેર હોઈ શકે છે.</small></p>",
    # EN: Vrat & festivals in your city
    "cities.heading": "તમારા શહેરમાં વ્રત અને તહેવાર",
    # EN: Today's Panchang in {city}
    # keep: {city}
    "tools.panchang": "{city}માં આજનું પંચાંગ",
    # EN: Rahu Kaal in {city}
    # keep: {city}
    # may also use: {t_rahu_kaal}
    "tools.rahu": "{city}માં રાહુકાળ",
    # EN: More for {city}
    # keep: {city}
    "tools.heading": "{city} માટે વધુ",
    # EN: See the Panchang for your city — free
    "cta": "તમારા શહેરનું પંચાંગ જુઓ — મફત",
    # EN: Today's vrat & festivals
    "more.today": "આજનાં વ્રત અને તહેવાર",
    # EN: Festival calendar {year}
    # keep: {year}
    "more.year": "તહેવાર કેલેન્ડર {year}",
    # EN: Ekadashi {year}
    # keep: {year}
    "more.ekadashi": "એકાદશી {year}",
    # EN: Today's Panchang
    "more.panchang": "આજનું પંચાંગ",
    # EN: Today's Rashifal
    "more.rashifal": "આજનું રાશિફળ",
    # EN: More
    "more.heading": "વધુ",
    # EN: Major festivals {year}
    # keep: {year}
    "majors.heading": "મુખ્ય તહેવારો {year}",
    # EN: Rule
    "today.rule": "નિયમ",
    # EN: No major vrat or festival today.
    "today.none": "આજે કોઈ મોટું વ્રત કે તહેવાર નથી.",
    # EN: Next: <strong>{name}</strong> on {day}.
    # keep: {day} {name}
    "today.next": " હવે પછી: <strong>{name}</strong> — {day}.",
    # EN: Vrat &amp; Festivals today
    "block.heading": "આજનાં વ્રત અને તહેવાર",
    # EN: Page not found
    "nf.h1": "પેજ મળ્યું નથી",
    # EN: Aaj Ke Vrat aur Tyohar: Today's Vrat & Festivals ({date})
    # keep: {date}
    "hub.title_default": "આજનાં વ્રત અને તહેવાર ({date}) — તિથિ, મુહૂર્ત અને પારણાં",
    # EN: Today's Vrat & Festivals in {city} ({date}) - Aaj Ke Vrat
    # keep: {city} {date}
    "hub.title_city": "{city}માં આજનાં વ્રત અને તહેવાર ({date})",
    # EN: Today's vrat & festivals
    "hub.h1_default": "આજનાં વ્રત અને તહેવાર",
    # EN: Today's vrat & festivals in {city}
    # keep: {city}
    "hub.h1_city": "{city}માં આજનાં વ્રત અને તહેવાર",
    # EN: Today, {date}: {names}.
    # keep: {date} {names}
    "hub.desc_today": "આજે, {date}: {names}. ",
    # EN: {date}: no major vrat today.
    # keep: {date}
    "hub.desc_none": "{date}: આજે કોઈ મોટું વ્રત નથી. ",
    # EN: Upcoming fasts and festivals for 30 days with Ekadashi parana, Pradosh and Sankashti
    #     moonrise times - {city}.
    # keep: {city}
    "hub.desc_rest": "આગામી 30 દિવસનાં ઉપવાસ અને તહેવાર, એકાદશીનાં પારણાં, પ્રદોષ અને સંકષ્ટીના ચંદ્રોદયના સમય સાથે - {city}.",
    # EN: <p class="hi" lang="hi">आज के व्रत और त्योहार</p>
    "hub.sub": "<p class=\"hi\">આજનાં વ્રત અને તહેવાર</p>",
    # EN: Next 30 days
    "hub.upcoming": "આગામી 30 દિવસ",
    # EN: Hindu Festival & Vrat Calendar {year} (New Delhi): Dates and Muhurat
    # keep: {year}
    "year.title": "હિન્દુ તહેવાર અને વ્રત કેલેન્ડર {year} (નવી દિલ્હી): તારીખો અને મુહૂર્ત",
    # EN: Vrat & festival calendar {year}
    # keep: {year}
    "year.h1": "વ્રત અને તહેવાર કેલેન્ડર {year}",
    # EN: Every Hindu vrat and festival of {year}, month by month - Ekadashi, Pradosh, Sankashti,
    #     Purnima, Amavasya, Shivratri and festivals like Diwali, Navratri and Raksha Bandhan, with
    #     puja muhurat for New Delhi.
    # keep: {year}
    "year.desc": "{year}નાં બધાં હિન્દુ વ્રત અને તહેવાર, મહિના પ્રમાણે - એકાદશી, પ્રદોષ, સંકષ્ટી, પૂનમ, અમાસ, શિવરાત્રિ અને દિવાળી, નવરાત્રિ, રક્ષાબંધન જેવા તહેવારો, નવી દિલ્હી માટે પૂજા મુહૂર્ત સાથે.",
    # EN: <p><strong>{count}</strong> fasts and festivals in {year} for New Delhi, computed from the
    #     panchang. Tap a major festival for its puja muhurat and what it is about.</p>
    # keep: {count} {year}
    "year.intro": "<p>પંચાંગ પરથી ગણેલાં નવી દિલ્હી માટે {year}નાં <strong>{count}</strong> ઉપવાસ અને તહેવાર. કોઈ મોટા તહેવાર પર ટેપ કરો અને તેનું પૂજા મુહૂર્ત તથા મહત્વ જુઓ.</p>",
    # EN: {month} {year}
    # keep: {month} {year}
    "year.month": "{month} {year}",
    # EN: Major Hindu festivals {year}
    # keep: {year}
    "year.itemlist": "{year}ના મુખ્ય હિન્દુ તહેવારો",
    # EN: Ekadashi {year}: All Ekadashi Vrat Dates and Parana Time (New Delhi)
    # keep: {year}
    "ek.title": "એકાદશી {year}: બધી એકાદશી વ્રતની તારીખો અને પારણાંનો સમય (નવી દિલ્હી)",
    # EN: Ekadashi {year}: dates and parana time
    # keep: {year}
    "ek.h1": "એકાદશી {year}: તારીખો અને પારણાંનો સમય",
    # EN: All {count} Ekadashis of {year} - fasting date, Ekadashi tithi times and the parana (fast-
    #     breaking) window next day, for New Delhi.
    # keep: {count} {year}
    "ek.desc": "{year}ની બધી {count} એકાદશી - ઉપવાસની તારીખ, એકાદશી તિથિના સમય અને બીજા દિવસે પારણાં (વ્રત છોડવા)ની વિન્ડો, નવી દિલ્હી માટે.",
    # EN: <tr><th>Ekadashi</th><th>Fast</th><th>Parana</th></tr>
    "ek.th": "<tr><th>એકાદશી</th><th>ઉપવાસ</th><th>પારણાં</th></tr>",
    # EN: <p><strong>Rule (Smarta):</strong> fast on the day Ekadashi prevails at sunrise; if it
    #     prevails at two sunrises, the second day, and if at none, the day it falls in. Parana is
    #     the next day after sunrise, once Hari Vasara (the first quarter of Dwadashi) is over,
    #     within Pratahkala and before Dwadashi ends; if Hari Vasara runs past Pratahkala, parana
    #     moves to Aparahna (Madhyahna is avoided).</p>
    "ek.rule": "<p><strong>નિયમ (સ્માર્ત):</strong> જે દિવસે સૂર્યોદય વખતે એકાદશી હોય તે દિવસે ઉપવાસ; જો બે સૂર્યોદયે હોય તો બીજા દિવસે, અને કોઈ સૂર્યોદયે ન હોય તો જે દિવસે તે આવે તે દિવસે. પારણાં બીજા દિવસે સૂર્યોદય પછી, હરિવાસર (બારસનો પ્રથમ ચોથો ભાગ) પૂરો થયા પછી, પ્રાતઃકાળમાં અને બારસ પૂરી થાય તે પહેલાં કરાય છે; જો હરિવાસર પ્રાતઃકાળ પછી સુધી ચાલે તો પારણાં અપરાહ્નમાં થાય છે (મધ્યાહ્ન ટાળવામાં આવે છે).</p>",
    # EN: <p class="hi" lang="hi">एकादशी {year}</p>
    # keep: {year}
    "ek.sub": "<p class=\"hi\">એકાદશી {year}</p>",
    # EN: Ekadashi {year}
    # keep: {year}
    "ek.crumb": "એકાદશી {year}",
    # EN: {name} {year}: Date and Puja Muhurat - {short}
    # keep: {name} {short} {year}
    "fest.title": "{name} {year}: તારીખ અને પૂજા મુહૂર્ત - {short}",
    # EN: {name} {year}: date and muhurat
    # keep: {name} {year}
    "fest.h1": "{name} {year}: તારીખ અને મુહૂર્ત",
    # EN: {text}.
    # keep: {text}
    "fest.main": "{text}. ",
    # EN: {name} {year} is on {weekday}, {date}. {main}Puja timings for New Delhi.
    # keep: {date} {main} {name} {weekday} {year}
    "fest.desc": "{name} {year} {weekday}, {date}ના રોજ છે. {main}નવી દિલ્હી માટે પૂજાના સમય.",
    # EN: {name} {year} is on <strong>{when}</strong>.
    # keep: {name} {when} {year}
    "fest.when": "{name} {year} <strong>{when}</strong>ના રોજ છે.",
    # EN: <p class="hi" lang="hi">{name_hi} {year}</p>
    # keep: {year}
    "fest.sub": "<p class=\"hi\">તારીખ અને પૂજા મુહૂર્ત {year}</p>",
    # EN: What it is and how it is observed
    "fest.about_h2": "તે શું છે અને કેવી રીતે ઊજવાય છે",
    # EN: How the date is fixed
    "fest.rule_h2": "તારીખ કેવી રીતે નક્કી થાય છે",
    # EN: Frequently asked questions
    "fest.faq_h2": "વારંવાર પૂછાતા પ્રશ્નો",
    # EN: India
    "event.place": "ભારત",
    # EN: When is {name} {year}?
    # keep: {name} {year}
    "faq.when_q": "{name} {year} ક્યારે છે?",
    # EN: {name} {year} is on {weekday}, {date}.
    # keep: {date} {name} {weekday} {year}
    "faq.when_a": "{name} {year} {weekday}, {date}ના રોજ છે.",
    # EN: What is the {name} {year} puja muhurat?
    # keep: {name} {year}
    "faq.muhurat_q": "{name} {year}નું પૂજા મુહૂર્ત શું છે?",
    # EN: What are the {name} {year} timings?
    # keep: {name} {year}
    "faq.timings_q": "{name} {year}ના સમય શું છે?",
    # EN: For New Delhi - {timings}. Timings vary by city by a few minutes; check the Panchang for
    #     your city.
    # keep: {timings}
    "faq.timings_a": "નવી દિલ્હી માટે - {timings}. સમય શહેર પ્રમાણે થોડી મિનિટ બદલાય છે; તમારા શહેરનું પંચાંગ જુઓ.",
    # EN: Why is {name} {year} observed on {short}?
    # keep: {name} {short} {year}
    "faq.why_q": "{name} {year} {short} ના રોજ કેમ ઊજવાય છે?",
    # EN: The date follows the rule: {rule}. In {year} that is {when} (New Delhi).
    # keep: {rule} {when} {year}
    "faq.why_a": "તારીખ આ નિયમ મુજબ નક્કી થાય છે: {rule}. {year}માં તે {when} (નવી દિલ્હી) છે.",
}

# app/vrat_text.py ABOUT["gu"] — what each of the 47 festivals / vrats is (key = festival slug)  [47]
VRAT_ABOUT = {
    # EN: Makar Sankranti marks the Sun's entry into Makara (Capricorn) and the start of its
    #     northward journey (Uttarayana). It is a harvest festival: people bathe in holy rivers,
    #     give til (sesame), jaggery, khichdi and blankets in charity, and fly kites.
    "makar-sankranti": "મકરસંક્રાંતિ સૂર્યના મકર રાશિમાં પ્રવેશ અને તેની ઉત્તર તરફની યાત્રા (ઉત્તરાયણ)ની શરૂઆત દર્શાવે છે. ગુજરાતમાં તે ઉત્તરાયણ તરીકે ઊજવાય છે. આ પાકનો તહેવાર છે: લોકો પવિત્ર નદીઓમાં સ્નાન કરે છે, તલ, ગોળ, ખીચડી અને ધાબળાનું દાન કરે છે અને પતંગ ચગાવે છે.",
    # EN: Maha Shivratri, the great night of Shiva, falls on the Krishna Chaturdashi of Magha.
    #     Devotees fast, offer water, milk and bel leaves on the Shivling, chant Om Namah Shivaya
    #     and keep vigil through the four prahars of the night; the Nishita kaal puja around
    #     midnight is the most important.
    "maha-shivratri": "મહાશિવરાત્રિ, શિવની મહારાત્રિ, મહા મહિનાની વદ ચૌદશે આવે છે. ભક્તો ઉપવાસ કરે છે, શિવલિંગ પર જળ, દૂધ અને બિલીપત્ર ચઢાવે છે, ‘ઓમ નમઃ શિવાય’નો જાપ કરે છે અને રાત્રિના ચાર પ્રહર જાગરણ કરે છે; મધ્યરાત્રિની આસપાસની નિશીથ કાળની પૂજા સૌથી મહત્વની છે.",
    # EN: Holika Dahan, on the eve of Holi, celebrates Prahlad's devotion and the victory of good
    #     over evil. A bonfire is lit after sunset, avoiding Bhadra, and families circle it offering
    #     grain, coconut and prayers.
    "holika-dahan": "હોળીની આગલી સાંજે થતું હોલિકા દહન પ્રહલાદની ભક્તિ અને અનિષ્ટ પર સારાના વિજયની ઉજવણી છે. સૂર્યાસ્ત પછી, ભદ્રા ટાળીને, હોળી પ્રગટાવાય છે અને પરિવારો તેની પ્રદક્ષિણા કરીને અનાજ, નાળિયેર અને પ્રાર્થના અર્પણ કરે છે.",
    # EN: Holi, the festival of colours, is celebrated the morning after Holika Dahan with colours,
    #     music, sweets like gujiya and visits to family and friends.
    "holi": "ધુળેટી (હોળી), રંગોનો તહેવાર, હોલિકા દહનની બીજી સવારે રંગો, સંગીત, ગુજિયા જેવી મીઠાઈઓ અને સગાં-મિત્રોની મુલાકાતો સાથે ઊજવાય છે.",
    # EN: Ram Navami celebrates the birth of Lord Rama on Chaitra Shukla Navami, at midday. Devotees
    #     fast, read the Ramcharitmanas, and offer puja in the Madhyahna muhurat, the time of his
    #     birth.
    "ram-navami": "રામ નવમી ચૈત્ર સુદ નોમે મધ્યાહ્ને ભગવાન રામના જન્મની ઉજવણી છે. ભક્તો ઉપવાસ કરે છે, રામચરિતમાનસનો પાઠ કરે છે અને તેમના જન્મના સમય, મધ્યાહ્ન મુહૂર્તમાં પૂજા કરે છે.",
    # EN: Hanuman Jayanti (Chaitra Purnima in North India) celebrates the birth of Lord Hanuman.
    #     Devotees visit Hanuman temples, recite the Hanuman Chalisa and Sundarkand, and offer
    #     sindoor and laddoos.
    "hanuman-jayanti": "હનુમાન જયંતી (ઉત્તર ભારતમાં ચૈત્ર પૂનમે) ભગવાન હનુમાનના જન્મની ઉજવણી છે. ભક્તો હનુમાન મંદિરોમાં જાય છે, હનુમાન ચાલીસા અને સુંદરકાંડનો પાઠ કરે છે અને સિંદૂર તથા લાડુ અર્પણ કરે છે.",
    # EN: Akshaya Tritiya, Vaishakha Shukla Tritiya, is held to make every good deed 'akshaya' -
    #     undiminishing. People worship Vishnu and Lakshmi, give in charity, and begin new ventures
    #     or buy gold.
    "akshaya-tritiya": "અક્ષય તૃતીયા, વૈશાખ સુદ ત્રીજ, દરેક સારા કાર્યને ‘અક્ષય’ - ક્યારેય ક્ષીણ ન થનારું - બનાવે છે એમ મનાય છે. લોકો વિષ્ણુ અને લક્ષ્મીની પૂજા કરે છે, દાન કરે છે અને નવાં સાહસો શરૂ કરે છે કે સોનું ખરીદે છે.",
    # EN: Raksha Bandhan, on Shravana Purnima, celebrates the bond between brothers and sisters.
    #     Sisters tie a rakhi on their brother's wrist and pray for his well-being; the rakhi is
    #     tied in a time free of Bhadra.
    "raksha-bandhan": "રક્ષાબંધન, શ્રાવણ પૂનમે, ભાઈ-બહેનના સંબંધની ઉજવણી છે. બહેનો ભાઈના કાંડે રાખડી બાંધે છે અને તેના કલ્યાણની પ્રાર્થના કરે છે; રાખડી ભદ્રા વગરના સમયમાં બંધાય છે. ગુજરાતમાં તે બળેવ તરીકે પણ ઓળખાય છે.",
    # EN: Krishna Janmashtami celebrates the birth of Lord Krishna at midnight on Krishna Ashtami of
    #     Bhadrapada (purnimanta). Devotees fast through the day and break it after the Nishita
    #     (midnight) puja, when the infant Krishna is bathed and placed in a cradle.
    "janmashtami": "કૃષ્ણ જન્માષ્ટમી ભાદરવા વદ આઠમે (પૂર્ણિમાંત; ગુજરાતના અમાંત પંચાંગમાં શ્રાવણ વદ આઠમ) મધ્યરાત્રિએ ભગવાન કૃષ્ણના જન્મની ઉજવણી છે. ભક્તો આખો દિવસ ઉપવાસ કરે છે અને નિશીથ (મધ્યરાત્રિ) પૂજા પછી તે છોડે છે, જ્યારે બાળ કૃષ્ણને સ્નાન કરાવીને પારણામાં પધરાવાય છે.",
    # EN: Ganesh Chaturthi, Bhadrapada Shukla Chaturthi, welcomes Lord Ganesha home. The idol is
    #     installed and worshipped in the Madhyahna (midday) muhurat, the time of his birth, with
    #     modak, durva grass and red flowers; looking at the Moon on this day is avoided.
    "ganesh-chaturthi": "ગણેશ ચતુર્થી, ભાદરવા સુદ ચોથ, ભગવાન ગણેશનું ઘરે સ્વાગત છે. મૂર્તિની સ્થાપના કરીને તેમના જન્મના સમય, મધ્યાહ્ન મુહૂર્તમાં મોદક, દૂર્વા અને લાલ ફૂલોથી પૂજા થાય છે; આ દિવસે ચંદ્રદર્શન ટાળવામાં આવે છે.",
    # EN: Chaitra Navratri, the nine nights of Goddess Durga in spring, begins on Chaitra Shukla
    #     Pratipada - also the Hindu New Year (Vikram Samvat). Ghatasthapana (installing the kalash)
    #     opens the nine days of worship.
    "chaitra-navratri": "ચૈત્ર નવરાત્રિ, વસંતમાં દેવી દુર્ગાની નવ રાત્રિઓ, ચૈત્ર સુદ એકમે શરૂ થાય છે - જે હિન્દુ નવું વર્ષ (વિક્રમ સંવત) પણ છે (ગુજરાતમાં વિક્રમ સંવત દિવાળી પછી કારતક સુદ એકમે બેસે છે). ઘટસ્થાપના (કળશની સ્થાપના) નવ દિવસની પૂજાનો આરંભ કરે છે.",
    # EN: Sharad Navratri, the nine nights of Goddess Durga in autumn, begins on Ashwin Shukla
    #     Pratipada with Ghatasthapana - installing the kalash and sowing barley - in the morning.
    #     Each day honours one of the nine forms of the Goddess.
    "navratri": "શારદીય નવરાત્રિ, શરદ ઋતુમાં દેવી દુર્ગાની નવ રાત્રિઓ, આસો સુદ એકમે સવારે ઘટસ્થાપના - કળશની સ્થાપના અને જવ વાવણી - સાથે શરૂ થાય છે. દરેક દિવસ દેવીના નવ સ્વરૂપોમાંથી એકને સમર્પિત છે.",
    # EN: Dussehra (Vijayadashami) marks Lord Rama's victory over Ravana and Goddess Durga's over
    #     Mahishasura. Shami puja, Aparajita puja and the burning of Ravana effigies are held in the
    #     afternoon; the Vijay muhurat is considered good for starting anything new.
    "dussehra": "દશેરા (વિજયાદશમી) ભગવાન રામના રાવણ પર અને દેવી દુર્ગાના મહિષાસુર પર વિજયનું પ્રતીક છે. શમી પૂજા, અપરાજિતા પૂજા અને રાવણ દહન બપોર પછી થાય છે; વિજય મુહૂર્ત કંઈ પણ નવું શરૂ કરવા માટે શુભ ગણાય છે.",
    # EN: On Karwa Chauth married women keep a fast from sunrise to moonrise for their husbands'
    #     long life. The evening puja of Karwa Mata is followed by offering water (arghya) to the
    #     Moon, after which the fast is broken.
    "karwa-chauth": "કરવા ચોથે પરિણીત સ્ત્રીઓ પતિના દીર્ઘાયુ માટે સૂર્યોદયથી ચંદ્રોદય સુધી ઉપવાસ કરે છે. સાંજે કરવા માતાની પૂજા પછી ચંદ્રને અર્ઘ્ય (જળ) અપાય છે, ત્યાર બાદ ઉપવાસ છોડાય છે.",
    # EN: On Ahoi Ashtami, eight days before Diwali, mothers keep a fast for the well-being of their
    #     children and worship Ahoi Mata in the evening; the fast is traditionally broken after
    #     sighting the stars (or, in some families, the Moon).
    "ahoi-ashtami": "દિવાળીના આઠ દિવસ પહેલાં અહોઈ આઠમે માતાઓ સંતાનોના કલ્યાણ માટે ઉપવાસ કરે છે અને સાંજે અહોઈ માતાની પૂજા કરે છે; પરંપરા મુજબ તારા દેખાયા પછી (કે કેટલાંક કુટુંબોમાં ચંદ્રદર્શન પછી) ઉપવાસ છોડાય છે.",
    # EN: Dhanteras, the first day of Diwali, honours Dhanvantari and Goddess Lakshmi. People buy
    #     new utensils, gold or silver and light the Yama deepak at dusk; the puja is done in
    #     Pradosh kaal, ideally in the fixed (sthir) Vrishabha lagna.
    "dhanteras": "ધનતેરસ, દિવાળીનો પહેલો દિવસ, ધન્વંતરિ અને દેવી લક્ષ્મીનું પૂજન છે. લોકો નવાં વાસણો, સોનું કે ચાંદી ખરીદે છે અને સાંજે યમ દીવો પ્રગટાવે છે; પૂજા પ્રદોષ કાળમાં, આદર્શ રીતે સ્થિર વૃષભ લગ્નમાં કરાય છે.",
    # EN: Diwali, on Kartika Amavasya, is the festival of lights. Lakshmi and Ganesha are worshipped
    #     in the evening - in Pradosh kaal, preferably in the fixed (sthir) Vrishabha lagna so that
    #     prosperity stays - and homes are lit with diyas.
    "diwali": "દિવાળી, આસો વદ અમાસે, પ્રકાશનો તહેવાર છે. સાંજે લક્ષ્મી અને ગણેશની પૂજા થાય છે - પ્રદોષ કાળમાં, સમૃદ્ધિ ટકી રહે તે માટે શક્ય હોય તો સ્થિર વૃષભ લગ્નમાં - અને ઘરોને દીવાઓથી સજાવાય છે.",
    # EN: Govardhan Puja (Annakut), the day after Diwali, remembers Krishna lifting Govardhan hill.
    #     A Govardhan of cow-dung or food is worshipped and an annakut of many dishes is offered,
    #     usually in the morning (Pratahkala).
    "govardhan-puja": "ગોવર્ધન પૂજા (અન્નકૂટ), દિવાળીના બીજા દિવસે, કૃષ્ણે ગોવર્ધન પર્વત ઉપાડ્યો તેનું સ્મરણ છે. ગોબર કે ભોજનનો ગોવર્ધન પૂજાય છે અને અનેક વાનગીઓનો અન્નકૂટ ધરાવાય છે, સામાન્ય રીતે સવારે (પ્રાતઃકાળમાં). ગુજરાતમાં આ દિવસ બેસતું વર્ષ (વિક્રમ સંવતનો પ્રથમ દિવસ) છે.",
    # EN: Bhai Dooj, Kartika Shukla Dwitiya, celebrates brothers and sisters: sisters apply a tilak,
    #     perform aarti and pray for their brother's long life, ideally in the Aparahna (afternoon)
    #     time.
    "bhai-dooj": "ભાઈબીજ, કારતક સુદ બીજ, ભાઈ-બહેનની ઉજવણી છે: બહેનો તિલક કરે છે, આરતી ઉતારે છે અને ભાઈના દીર્ઘાયુની પ્રાર્થના કરે છે, આદર્શ રીતે અપરાહ્ન (બપોર પછી)ના સમયમાં.",
    # EN: Chhath Puja worships the Sun God and Chhathi Maiya over four days. On the main day
    #     (Kartika Shukla Shashthi) devotees stand in water and offer arghya to the setting Sun, and
    #     to the rising Sun the next morning, ending a fast kept without water.
    "chhath-puja": "છઠ પૂજામાં ચાર દિવસ સૂર્ય દેવ અને છઠ્ઠી મૈયાની પૂજા થાય છે. મુખ્ય દિવસે (કારતક સુદ છઠ) ભક્તો પાણીમાં ઊભા રહીને અસ્ત થતા સૂર્યને અને બીજી સવારે ઉદય થતા સૂર્યને અર્ઘ્ય આપે છે, અને પાણી વગરનો ઉપવાસ પૂરો કરે છે.",
    # EN: Vasant Panchami, Magha Shukla Panchami, welcomes spring and honours Goddess Saraswati.
    #     Students and artists worship books and instruments, people wear yellow, and children often
    #     begin learning to write (vidyarambh).
    "vasant-panchami": "વસંત પંચમી, મહા સુદ પાંચમ, વસંતનું સ્વાગત અને દેવી સરસ્વતીનું પૂજન છે. વિદ્યાર્થીઓ અને કલાકારો પુસ્તકો અને વાદ્યોની પૂજા કરે છે, લોકો પીળાં વસ્ત્ર પહેરે છે અને બાળકો ઘણી વાર લખતાં શીખવાની શરૂઆત (વિદ્યારંભ) કરે છે.",
    # EN: Guru Purnima, Ashadha Purnima, honours one's teachers and Maharishi Ved Vyasa, born on
    #     this day. Disciples offer gratitude, flowers and gifts to their guru.
    "guru-purnima": "ગુરુ પૂનમ, અષાઢ પૂનમ, પોતાના ગુરુજનો અને આ દિવસે જન્મેલા મહર્ષિ વેદવ્યાસનું સન્માન કરે છે. શિષ્યો ગુરુ પ્રત્યે કૃતજ્ઞતા, ફૂલ અને ભેટ અર્પણ કરે છે.",
    # EN: Sharad Purnima, Ashwin Purnima, is the night the Moon is held to be brightest and full of
    #     nectar. Kheer is kept in the moonlight overnight and eaten as prasad; Lakshmi is
    #     worshipped (Kojagari).
    "sharad-purnima": "શરદ પૂનમ, આસો પૂનમ, એ રાત છે જ્યારે ચંદ્ર સૌથી તેજસ્વી અને અમૃતથી ભરેલો મનાય છે. ખીર આખી રાત ચાંદનીમાં રાખીને પ્રસાદ તરીકે ખવાય છે; લક્ષ્મીની પૂજા થાય છે (કોજાગરી).",
    # EN: Devuthani (Prabodhini) Ekadashi, Kartika Shukla Ekadashi, is when Lord Vishnu is held to
    #     wake from his four-month sleep, ending Chaturmas. Tulsi vivah begins and the wedding
    #     season opens. Devotees fast and break the fast (parana) the next day.
    "devuthani-ekadashi": "દેવઊઠી (પ્રબોધિની) એકાદશી, કારતક સુદ અગિયારસ, એ દિવસ છે જ્યારે ભગવાન વિષ્ણુ ચાર મહિનાની નિદ્રામાંથી જાગે છે એમ મનાય છે અને ચાતુર્માસ પૂરો થાય છે. તુલસી વિવાહ શરૂ થાય છે અને લગ્નની મોસમ ખૂલે છે. ભક્તો ઉપવાસ કરે છે અને બીજા દિવસે પારણાં કરે છે.",
    # EN: Jivitputrika (Jitiya, Jiutiya) is kept by mothers in Bihar, Jharkhand, eastern Uttar
    #     Pradesh and Nepal for the long life and well-being of their children, on Ashwin Krishna
    #     Ashtami (purnimanta). It begins with nahay-khay the day before; the fast itself is
    #     nirjala, without water, through the day and night, with worship of Jimutavahana and the
    #     Jitiya katha. Parana, breaking the fast, is the next morning.
    "jivitputrika": "જીવિત્પુત્રિકા (જિતિયા, જિઉતિયા) બિહાર, ઝારખંડ, પૂર્વી ઉત્તર પ્રદેશ અને નેપાળમાં માતાઓ સંતાનોના દીર્ઘાયુ અને કલ્યાણ માટે આસો વદ આઠમે (પૂર્ણિમાંત; ગુજરાતના અમાંત પંચાંગમાં ભાદરવા વદ આઠમ) રાખે છે. તેની શરૂઆત આગલા દિવસે નહાય-ખાયથી થાય છે; ઉપવાસ પોતે નિર્જળા - પાણી વગર - આખો દિવસ અને રાત ચાલે છે, જેમાં જીમૂતવાહનની પૂજા અને જિતિયા કથા થાય છે. પારણાં બીજી સવારે.",
    # EN: Lohri, the evening before Makar Sankranti, is the winter harvest festival of Punjab and
    #     North India. A bonfire is lit at dusk and people offer til, gur, rewari, peanuts and
    #     popcorn to it, sing and dance; it is especially celebrated for a new bride or a newborn.
    "lohri": "લોહડી, મકરસંક્રાંતિની આગલી સાંજ, પંજાબ અને ઉત્તર ભારતનો શિયાળુ પાકનો તહેવાર છે. સાંજે અગ્નિ પ્રગટાવાય છે અને લોકો તેમાં તલ, ગોળ, રેવડી, મગફળી અને પોપકોર્ન અર્પણ કરે છે, ગાય છે અને નાચે છે; નવી વહુ કે નવજાત શિશુ માટે તે ખાસ ઊજવાય છે.",
    # EN: Sakat Chauth (Tilkut Chauth), the Sankashti Chaturthi of Magha (purnimanta), is kept by
    #     mothers for their children. Ganesha and Sakat Mata are worshipped with til and jaggery,
    #     and the fast is broken after offering arghya to the rising Moon.
    "sakat-chauth": "સકટ ચોથ (તિલકૂટ ચોથ), મહા મહિનાની (પૂર્ણિમાંત; ગુજરાતના અમાંત પંચાંગમાં પોષ વદ) સંકષ્ટી ચતુર્થી, માતાઓ સંતાનો માટે રાખે છે. ગણેશ અને સકટ માતાની તલ અને ગોળથી પૂજા થાય છે, અને ઉદય પામતા ચંદ્રને અર્ઘ્ય આપ્યા પછી ઉપવાસ છોડાય છે.",
    # EN: Mauni Amavasya, the Amavasya of Magha (purnimanta), is the great bathing day of the Magh
    #     Mela at Prayagraj. Devotees bathe in the Ganga or a holy river, keep silence (mauna) and
    #     give in charity.
    "mauni-amavasya": "મૌની અમાસ, મહા મહિનાની (પૂર્ણિમાંત; ગુજરાતના અમાંત પંચાંગમાં પોષ વદ) અમાસ, પ્રયાગરાજના માઘ મેળાનો મહાન સ્નાન દિવસ છે. ભક્તો ગંગા કે કોઈ પવિત્ર નદીમાં સ્નાન કરે છે, મૌન (મૌના) રાખે છે અને દાન કરે છે.",
    # EN: Sheetala Ashtami (Basoda), Chaitra Krishna Ashtami (purnimanta), honours Sheetala Mata,
    #     the goddess who protects from fevers and pox. Food is cooked the day before and the stale
    #     (basi) food is offered and eaten; no fire is lit for cooking that day.
    "sheetala-ashtami": "શીતળા આઠમ (બસોડા), ચૈત્ર વદ આઠમ (પૂર્ણિમાંત; ગુજરાતના અમાંત પંચાંગમાં ફાગણ વદ આઠમ), તાવ અને શીતળાથી રક્ષણ આપતી દેવી શીતળા માતાનું પૂજન છે. રસોઈ આગલા દિવસે બને છે અને વાસી (બાસી) ભોજન ધરાવીને ખવાય છે; તે દિવસે રસોઈ માટે અગ્નિ પ્રગટાવાતો નથી.",
    # EN: Gudi Padwa (Maharashtra) and Ugadi (Karnataka, Andhra Pradesh, Telangana) mark the lunar
    #     New Year on Chaitra Shukla Pratipada. A gudi - a decorated pole with a cloth and kalash -
    #     is raised at the door, and neem with jaggery is eaten for a year of both sweet and bitter.
    "gudi-padwa": "ગુડી પડવો (મહારાષ્ટ્ર) અને ઉગાદી (કર્ણાટક, આંધ્ર પ્રદેશ, તેલંગાણા) ચૈત્ર સુદ એકમે ચાંદ્ર નવું વર્ષ દર્શાવે છે. દરવાજે કાપડ અને કળશ સાથેનો શણગારેલો દંડ (ગુડી) ઊભો કરાય છે, અને મીઠા-કડવા બંને સ્વાદવાળા વર્ષ માટે લીમડો ગોળ સાથે ખવાય છે.",
    # EN: Gangaur, Chaitra Shukla Tritiya, is Rajasthan's festival of Gauri (Parvati) and Shiva.
    #     Women worship Gauri for marital happiness - married women for their husbands, girls for a
    #     good match - ending eighteen days of puja that begin the day after Holi.
    "gangaur": "ગણગૌર, ચૈત્ર સુદ ત્રીજ, રાજસ્થાનનો ગૌરી (પાર્વતી) અને શિવનો તહેવાર છે. સ્ત્રીઓ અખંડ સૌભાગ્ય માટે ગૌરીની પૂજા કરે છે - પરિણીતાઓ પતિ માટે, કન્યાઓ સારા વર માટે - જે હોળીના બીજા દિવસથી શરૂ થતી અઢાર દિવસની પૂજાનો અંત છે.",
    # EN: Vat Savitri Vrat, on Jyeshtha Amavasya in North India (purnimanta), remembers Savitri, who
    #     won back her husband Satyavan's life from Yama. Married women fast, worship the banyan
    #     (vat) tree, tie raw thread around it while circling it, and hear the Savitri katha.
    "vat-savitri": "વટ સાવિત્રી વ્રત, ઉત્તર ભારતમાં જેઠ અમાસે (પૂર્ણિમાંત; ગુજરાતના અમાંત પંચાંગમાં વૈશાખ અમાસ), સાવિત્રીનું સ્મરણ છે, જેણે યમ પાસેથી પતિ સત્યવાનના પ્રાણ પાછા મેળવ્યા. પરિણીત સ્ત્રીઓ ઉપવાસ કરે છે, વડના વૃક્ષની પૂજા કરે છે, તેની પ્રદક્ષિણા કરતાં કાચો દોરો વીંટે છે અને સાવિત્રી કથા સાંભળે છે.",
    # EN: Vat Purnima is the same Vat Savitri vrat as kept on Jyeshtha Purnima in Maharashtra,
    #     Gujarat and the south (amanta calendar), fifteen days after the North Indian date. Married
    #     women fast and worship the banyan tree for their husbands' long life.
    "vat-purnima": "વટ પૂનમ એ જ વટ સાવિત્રી વ્રત છે જે મહારાષ્ટ્ર, ગુજરાત અને દક્ષિણમાં જેઠ પૂનમે (અમાંત કેલેન્ડર) ઉત્તર ભારતની તારીખથી પંદર દિવસ પછી રખાય છે. પરિણીત સ્ત્રીઓ પતિના દીર્ઘાયુ માટે ઉપવાસ કરે છે અને વડની પૂજા કરે છે.",
    # EN: Ganga Dussehra, Jyeshtha Shukla Dashami, celebrates the descent of the Ganga to earth
    #     through Bhagiratha's penance. Devotees bathe in the Ganga, offer lamps and give in
    #     charity; the bath is held to wash away ten kinds of sin.
    "ganga-dussehra": "ગંગા દશેરા, જેઠ સુદ દશમ, ભગીરથની તપસ્યાથી ગંગાના પૃથ્વી પર અવતરણની ઉજવણી છે. ભક્તો ગંગામાં સ્નાન કરે છે, દીપ અર્પણ કરે છે અને દાન કરે છે; આ સ્નાન દસ પ્રકારનાં પાપ ધોઈ નાખે છે એમ મનાય છે.",
    # EN: Hariyali Teej, Shravana Shukla Tritiya, celebrates the reunion of Shiva and Parvati in the
    #     monsoon. Women wear green, apply mehndi, swing on decorated jhoolas, sing Sawan songs and
    #     many keep a fast for their husbands.
    "hariyali-teej": "હરિયાળી તીજ, શ્રાવણ સુદ ત્રીજ, ચોમાસામાં શિવ અને પાર્વતીના મિલનની ઉજવણી છે. સ્ત્રીઓ લીલાં વસ્ત્ર પહેરે છે, મહેંદી લગાવે છે, શણગારેલા હીંચકે ઝૂલે છે, સાવનનાં ગીતો ગાય છે અને ઘણી પતિ માટે ઉપવાસ રાખે છે.",
    # EN: Nag Panchami, Shravana Shukla Panchami, is the day serpent deities (nagas) are worshipped.
    #     Images of snakes are drawn or installed and offered milk, flowers and sweets, with prayers
    #     for the family's protection. (In Gujarat, Nag Pancham falls later, in Bhadrapada.)
    "nag-panchami": "નાગ પાંચમ, શ્રાવણ સુદ પાંચમ, નાગ દેવતાઓની પૂજાનો દિવસ છે. સાપની આકૃતિ દોરાય છે કે સ્થાપાય છે અને દૂધ, ફૂલ અને મીઠાઈ ધરાવાય છે, કુટુંબના રક્ષણ માટે પ્રાર્થના સાથે. (ગુજરાતમાં નાગ પાંચમ પછી, ભાદરવા મહિનામાં આવે છે.)",
    # EN: Kajari (Kajli, Badi) Teej, Bhadrapada Krishna Tritiya (purnimanta), is kept by married
    #     women of Uttar Pradesh, Bihar, Rajasthan and Madhya Pradesh. They fast, worship the neem
    #     tree (Neemadi Mata) and break the fast after offering arghya to the Moon; kajari folk
    #     songs are sung.
    "kajari-teej": "કજરી (કજલી, બડી) તીજ, ભાદરવા વદ ત્રીજ (પૂર્ણિમાંત; ગુજરાતના અમાંત પંચાંગમાં શ્રાવણ વદ ત્રીજ), ઉત્તર પ્રદેશ, બિહાર, રાજસ્થાન અને મધ્ય પ્રદેશની પરિણીત સ્ત્રીઓ રાખે છે. તેઓ ઉપવાસ કરે છે, લીમડાના વૃક્ષ (નીમડી માતા)ની પૂજા કરે છે અને ચંદ્રને અર્ઘ્ય આપ્યા પછી ઉપવાસ છોડે છે; કજરી લોકગીતો ગવાય છે.",
    # EN: Hal Shashthi (Lalahi Chhath, Har Chhath), Bhadrapada Krishna Shashthi (purnimanta), is
    #     Lord Balarama's birthday, whose weapon is the plough (hal). Mothers fast for their
    #     children and eat nothing grown with a plough - often pasahi rice and buffalo milk.
    "hal-shashthi": "હળ છઠ (લલહી છઠ, હર છઠ), ભાદરવા વદ છઠ (પૂર્ણિમાંત; ગુજરાતના અમાંત પંચાંગમાં શ્રાવણ વદ છઠ), ભગવાન બળરામનો જન્મદિવસ છે, જેમનું શસ્ત્ર હળ છે. માતાઓ સંતાનો માટે ઉપવાસ કરે છે અને હળથી ઉગાડેલું કંઈ ખાતી નથી - ઘણી વાર પસહી ચોખા અને ભેંસનું દૂધ.",
    # EN: Hartalika Teej, Bhadrapada Shukla Tritiya, honours Parvati's penance to win Shiva. Women
    #     keep a nirjala fast, make clay images of Shiva and Parvati, worship them (morning puja in
    #     Pratahkala is preferred), keep vigil at night and break the fast next morning.
    "hartalika-teej": "હરતાલિકા તીજ, ભાદરવા સુદ ત્રીજ, શિવને પામવાની પાર્વતીની તપસ્યાનું સન્માન છે. સ્ત્રીઓ નિર્જળા ઉપવાસ રાખે છે, શિવ-પાર્વતીની માટીની મૂર્તિઓ બનાવીને પૂજે છે (સવારની, પ્રાતઃકાળની પૂજા પસંદ કરાય છે), રાત્રે જાગરણ કરે છે અને બીજી સવારે ઉપવાસ છોડે છે.",
    # EN: Rishi Panchami, Bhadrapada Shukla Panchami, honours the Saptarishis, the seven sages.
    #     Women in particular bathe, fast and worship the sages at midday (Madhyahna), seeking
    #     purification from faults committed unknowingly.
    "rishi-panchami": "ઋષિ પાંચમ, ભાદરવા સુદ પાંચમ, સપ્તર્ષિઓ, સાત ઋષિઓનું સન્માન છે. ખાસ કરીને સ્ત્રીઓ સ્નાન કરે છે, ઉપવાસ કરે છે અને મધ્યાહ્ને ઋષિઓની પૂજા કરે છે, અજાણતાં થયેલી ભૂલોમાંથી શુદ્ધિ માટે.",
    # EN: Anant Chaturdashi, Bhadrapada Shukla Chaturdashi, is the worship of Lord Vishnu as Anant.
    #     A sacred thread with fourteen knots (the anant sutra) is tied on the arm after puja; it is
    #     also the day Ganesh idols are immersed (Ganesh Visarjan).
    "anant-chaturdashi": "અનંત ચૌદશ, ભાદરવા સુદ ચૌદશ, ભગવાન વિષ્ણુની અનંત સ્વરૂપે પૂજા છે. પૂજા પછી ચૌદ ગાંઠવાળો પવિત્ર દોરો (અનંત સૂત્ર) હાથે બંધાય છે; તે ગણેશ મૂર્તિઓના વિસર્જન (ગણેશ વિસર્જન)નો દિવસ પણ છે.",
    # EN: Pitru Paksha, the fortnight of the ancestors, runs from Pratipada to Amavasya of the dark
    #     half of Ashwin (purnimanta). On the tithi of an ancestor's passing, families offer tarpan
    #     and shraddha - pinda, food for Brahmins, cows, crows and dogs - in the Kutup, Rohina or
    #     Aparahna time.
    "pitru-paksha": "પિતૃ પક્ષ, પૂર્વજોનું પખવાડિયું, આસો મહિનાના વદ પક્ષની એકમથી અમાસ સુધી ચાલે છે (પૂર્ણિમાંત; ગુજરાતના અમાંત પંચાંગમાં ભાદરવા વદ). પૂર્વજના અવસાનની તિથિએ કુટુંબો કુતુપ, રોહિણ કે અપરાહ્નના સમયમાં તર્પણ અને શ્રાદ્ધ - પિંડ, બ્રાહ્મણો, ગાય, કાગડા અને કૂતરાં માટે ભોજન - કરે છે.",
    # EN: Sarva Pitru Amavasya (Mahalaya Amavasya) closes Pitru Paksha. Shraddha on this day reaches
    #     all ancestors, including those whose tithi is not known; it is done in the Kutup, Rohina
    #     or Aparahna time.
    "sarva-pitru-amavasya": "સર્વપિતૃ અમાસ (મહાલય અમાસ) પિતૃ પક્ષ પૂરો કરે છે. આ દિવસનું શ્રાદ્ધ બધા પૂર્વજો સુધી પહોંચે છે, જેમની તિથિ ખબર ન હોય તેમના સુધી પણ; તે કુતુપ, રોહિણ કે અપરાહ્નના સમયમાં કરાય છે.",
    # EN: Narak Chaturdashi (Roop Chaudas), Kartika Krishna Chaturdashi (purnimanta), remembers
    #     Krishna's victory over Narakasura. Before sunrise, while the Moon is up, people take an
    #     oil bath with ubtan (Abhyang snan), and a lamp for Yama is lit in the evening.
    "narak-chaturdashi": "નરક ચતુર્દશી (રૂપ ચૌદશ, કાળી ચૌદશ), કારતક વદ ચૌદશ (પૂર્ણિમાંત; ગુજરાતના અમાંત પંચાંગમાં આસો વદ ચૌદશ), નરકાસુર પર કૃષ્ણના વિજયનું સ્મરણ છે. સૂર્યોદય પહેલાં, ચંદ્ર હોય ત્યારે, લોકો ઉબટન સાથે તેલ-સ્નાન (અભ્યંગ સ્નાન) કરે છે, અને સાંજે યમ માટે દીવો પ્રગટાવાય છે.",
    # EN: Tulsi Vivah, on Kartika Shukla Dwadashi, is the ceremonial wedding of the tulsi plant (as
    #     Vrinda) to Lord Vishnu as Shaligram. Families decorate the tulsi like a bride and perform
    #     the rites of a wedding; the Hindu wedding season begins after it.
    "tulsi-vivah": "તુલસી વિવાહ, કારતક સુદ બારસ, તુલસીના છોડ (વૃંદા તરીકે)ના ભગવાન વિષ્ણુ સાથે શાલિગ્રામ સ્વરૂપે વિધિવત્ લગ્ન છે. કુટુંબો તુલસીને નવવધૂની જેમ શણગારે છે અને લગ્નની વિધિઓ કરે છે; તે પછી હિન્દુ લગ્નની મોસમ શરૂ થાય છે.",
    # EN: Kartik Purnima ends the holy month of Kartika. It is a great day for bathing in the Ganga
    #     or a holy river and giving in charity, and also Guru Nanak Jayanti and Tripuri Purnima,
    #     when Shiva destroyed Tripurasura.
    "kartik-purnima": "કારતક પૂનમ પવિત્ર કારતક માસનો અંત કરે છે. તે ગંગા કે કોઈ પવિત્ર નદીમાં સ્નાન અને દાન માટેનો મહાન દિવસ છે, અને ગુરુ નાનક જયંતી તથા ત્રિપુરી પૂનમ પણ છે, જ્યારે શિવે ત્રિપુરાસુરનો નાશ કર્યો હતો.",
    # EN: Dev Deepawali, the 'Diwali of the gods', is celebrated on Kartik Purnima evening, above
    #     all on the ghats of Varanasi, which are lit with lakhs of diyas. It marks Shiva's victory
    #     over Tripurasura; lamps are offered to the Ganga in Pradosh kaal.
    "dev-deepawali": "દેવ દિવાળી, ‘દેવોની દિવાળી’, કારતક પૂનમની સાંજે ઊજવાય છે, ખાસ કરીને વારાણસીના ઘાટો પર, જે લાખો દીવાઓથી ઝળહળે છે. તે શિવના ત્રિપુરાસુર પર વિજયનું પ્રતીક છે; પ્રદોષ કાળમાં ગંગાને દીપ અર્પણ કરાય છે.",
}

# app/vrat_text.py NOTES["gu"] — tradition notes on dates that differ between almanacs (key = festival slug)  [11]
VRAT_NOTES = {
    # EN: Dates follow Drik Panchang. When Bhadra covers the whole Purnima night and Purnima lasts
    #     most of the next day, Drik moves Holika Dahan to the next evening's Pradosh (as in 2026, 3
    #     March); some almanacs instead give a time late on the first night, after Bhadra ends.
    "holika-dahan": "તારીખો દ્રિક પંચાંગ મુજબ છે. જ્યારે ભદ્રા આખી પૂનમની રાત ઢાંકે અને પૂનમ બીજા દિવસના મોટા ભાગ સુધી રહે, ત્યારે દ્રિક હોલિકા દહન બીજી સાંજના પ્રદોષમાં ખસેડે છે (જેમ 2026માં, 3 માર્ચ); કેટલાંક પંચાંગો તેને બદલે ભદ્રા પૂરી થયા પછી પહેલી રાતના મોડા સમયે આપે છે.",
    # EN: Dates follow Drik Panchang's Smarta (default) reckoning, with Rohini nakshatra at midnight
    #     preferred. Vaishnava/ISKCON communities sometimes keep Janmashtami a day later.
    "janmashtami": "તારીખો દ્રિક પંચાંગની સ્માર્ત (મુખ્ય) ગણતરી મુજબ છે, જેમાં મધ્યરાત્રિએ રોહિણી નક્ષત્ર હોય તેને પસંદગી અપાય છે. વૈષ્ણવ/ઇસ્કોન સમુદાયો ક્યારેક જન્માષ્ટમી એક દિવસ પછી ઊજવે છે.",
    # EN: This is the Smarta (householder) date. Where Ekadashi spans two days, Vaishnavas may fast
    #     on the second day.
    "devuthani-ekadashi": "આ સ્માર્ત (ગૃહસ્થ) તારીખ છે. જ્યાં એકાદશી બે દિવસ સુધી ફેલાય ત્યાં વૈષ્ણવો બીજા દિવસે ઉપવાસ કરી શકે છે.",
    # EN: Dates follow Drik Panchang (Dashami in Aparahna, Shravana nakshatra preferred). In Bengal
    #     and some almanacs Vijayadashami can fall a day later.
    "dussehra": "તારીખો દ્રિક પંચાંગ મુજબ છે (અપરાહ્નમાં દશમ, શ્રવણ નક્ષત્રને પસંદગી). બંગાળમાં અને કેટલાંક પંચાંગોમાં વિજયાદશમી એક દિવસ પછી આવી શકે છે.",
    # EN: Dates follow Drik Panchang (Ashtami at midday; when it is at sunrise only briefly, as in
    #     2023, the previous day). Nahay-khay is the day before and parana the next morning;
    #     regional panchangs (e.g. Mithila) can differ by a day.
    "jivitputrika": "તારીખો દ્રિક પંચાંગ મુજબ છે (મધ્યાહ્ને આઠમ; જ્યારે તે સૂર્યોદયે માત્ર થોડી વાર હોય, જેમ 2023માં, ત્યારે આગલો દિવસ). નહાય-ખાય આગલા દિવસે અને પારણાં બીજી સવારે; પ્રાદેશિક પંચાંગો (દા.ત. મિથિલા) એક દિવસ અલગ હોઈ શકે છે.",
    # EN: Two traditions: North India keeps Vat Savitri on Jyeshtha Amavasya (this date);
    #     Maharashtra, Gujarat and the south keep it as Vat Purnima fifteen days later.
    "vat-savitri": "બે પરંપરાઓ: ઉત્તર ભારત વટ સાવિત્રી જેઠ અમાસે રાખે છે (આ તારીખ); મહારાષ્ટ્ર, ગુજરાત અને દક્ષિણ તેને પંદર દિવસ પછી વટ પૂનમ તરીકે રાખે છે.",
    # EN: Two traditions: this is the Purnima (amanta) date of Maharashtra, Gujarat and the south;
    #     North India keeps Vat Savitri on the Amavasya fifteen days earlier.
    "vat-purnima": "બે પરંપરાઓ: આ મહારાષ્ટ્ર, ગુજરાત અને દક્ષિણની પૂનમ (અમાંત) તારીખ છે; ઉત્તર ભારત વટ સાવિત્રી પંદર દિવસ પહેલાં અમાસે રાખે છે.",
    # EN: When Jyeshtha is doubled (an adhika month, as in 2026), Drik Panchang keeps Ganga Dussehra
    #     in the adhika Jyeshtha; some almanacs give the nija Jyeshtha date a month later.
    "ganga-dussehra": "જ્યારે જેઠ બેવડો હોય (અધિક માસ, જેમ 2026માં), ત્યારે દ્રિક પંચાંગ ગંગા દશેરા અધિક જેઠમાં રાખે છે; કેટલાંક પંચાંગો નિજ જેઠની તારીખ એક મહિના પછી આપે છે.",
    # EN: Drik Panchang counts Pitru Paksha from the Pratipada shraddha; Purnima shraddha is on the
    #     day before, and many calendars start the fortnight there.
    "pitru-paksha": "દ્રિક પંચાંગ પિતૃ પક્ષ એકમના શ્રાદ્ધથી ગણે છે; પૂનમનું શ્રાદ્ધ આગલા દિવસે હોય છે, અને ઘણાં કેલેન્ડરો પખવાડિયું ત્યાંથી શરૂ કરે છે.",
    # EN: Drik Panchang publishes Dev Deepawali for Varanasi; the date here uses the same rule
    #     (Purnima in Pradosh), and the Pradosh kaal shown is New Delhi's.
    "dev-deepawali": "દ્રિક પંચાંગ દેવ દિવાળી વારાણસી માટે પ્રગટ કરે છે; અહીંની તારીખ એ જ નિયમ (પ્રદોષમાં પૂનમ) વાપરે છે, અને દર્શાવેલ પ્રદોષ કાળ નવી દિલ્હીનો છે.",
    # EN: This is the snan-daan day (Purnima at sunrise). When Purnima begins the previous
    #     afternoon, the Purnima fast and Dev Deepawali can fall a day earlier.
    "kartik-purnima": "આ સ્નાન-દાનનો દિવસ છે (સૂર્યોદયે પૂનમ). જ્યારે પૂનમ આગલી બપોરથી શરૂ થાય, ત્યારે પૂનમનો ઉપવાસ અને દેવ દિવાળી એક દિવસ વહેલાં આવી શકે છે.",
}

# app/vrat_text.py RULES["gu"] — 'how the date is fixed' sentences: head {month}, tithi {paksha} {tithi}, rule.<kind>, key.<observance>  [16]
VRAT_RULES = {
    # EN: {month} (amanta)
    # keep: {month}
    "head": "{month} (અમાંત) ",
    # EN: {paksha} {tithi}:
    # keep: {paksha} {tithi}
    "tithi": "{paksha} {tithi}: ",
    # EN: tithi prevailing at sunrise
    "rule.udaya": "સૂર્યોદયે રહેલી તિથિ",
    # EN: tithi prevailing in Pratahkala (first fifth of the day)
    "rule.pratah": "પ્રાતઃકાળમાં (દિવસનો પહેલો પાંચમો ભાગ) રહેલી તિથિ",
    # EN: tithi prevailing in the forenoon (purvahna)
    "rule.purvahna": "પૂર્વાહ્ન (સવારના ભાગ)માં રહેલી તિથિ",
    # EN: tithi prevailing at Madhyahna (midday fifth of the day)
    "rule.madhyahna": "મધ્યાહ્ન (દિવસનો મધ્યનો પાંચમો ભાગ)માં રહેલી તિથિ",
    # EN: tithi prevailing at Aparahna (fourth fifth of the day)
    "rule.aparahna": "અપરાહ્ન (દિવસનો ચોથો પાંચમો ભાગ)માં રહેલી તિથિ",
    # EN: first day on which the tithi is present between sunrise and sunset
    "rule.dina": "સૂર્યોદય અને સૂર્યાસ્ત વચ્ચે તિથિ હોય તેવો પહેલો દિવસ",
    # EN: tithi prevailing at sunset
    "rule.sayahna": "સૂર્યાસ્તે રહેલી તિથિ",
    # EN: tithi prevailing in Pradosh kaal (after sunset)
    "rule.pradosh": "પ્રદોષ કાળ (સૂર્યાસ્ત પછી)માં રહેલી તિથિ",
    # EN: tithi prevailing at Nishita kaal (midnight)
    "rule.nishita": "નિશીથ કાળ (મધ્યરાત્રિ)માં રહેલી તિથિ",
    # EN: tithi prevailing at moonrise
    "rule.moonrise": "ચંદ્રોદયે રહેલી તિથિ",
    # EN: Smarta: Ekadashi prevailing at sunrise (second day if at two sunrises); parana next day
    #     after sunrise and after Hari Vasara, within Pratahkala and before Dwadashi ends
    "key.ekadashi": "સ્માર્ત: સૂર્યોદયે એકાદશી (બે સૂર્યોદયે હોય તો બીજો દિવસ); પારણાં બીજા દિવસે સૂર્યોદય પછી અને હરિવાસર પછી, પ્રાતઃકાળમાં અને બારસ પૂરી થાય તે પહેલાં",
    # EN: the Sun's entry into sidereal Makara (Capricorn); punya kaal follows it until sunset
    "key.makar_sankranti": "સૂર્યનો નિરયન મકર રાશિમાં પ્રવેશ; પુણ્ય કાળ તેની પછી સૂર્યાસ્ત સુધી",
    # EN: the day before Makar Sankranti
    "key.lohri": "મકરસંક્રાંતિનો આગલો દિવસ",
    # EN: the day after Holika Dahan
    "key.holi": "હોલિકા દહનનો બીજો દિવસ",
}

# ----------------------------------------------------------------------------
# nakshatra /nakshatra /rashi /naam-se-kundali-milan
# ----------------------------------------------------------------------------

# app/nakshatra_page_text.py TEXT["gu"] — page text of /nakshatra /rashi (nakshatra_pages.py)  [88]
NAKSHATRA_PAGE_TEXT = {
    # EN: Get your free kundali — find your exact birth nakshatra and Moon sign
    "kundali_cta": "તમારી મફત કુંડળી મેળવો — તમારું ચોક્કસ જન્મ નક્ષત્ર અને ચંદ્ર રાશિ જાણો",
    # EN: More free tools
    "more.heading": "વધુ મફત સાધનો",
    # EN: All 27 nakshatras
    "more.naks": "બધાં 27 નક્ષત્ર",
    # EN: All 12 rashis
    "more.rashis": "બધી 12 રાશિ",
    # EN: Naam se Kundali Milan
    "more.milan": "નામ પરથી કુંડળી મિલન",
    # EN: Kundali Milan (36 guna)
    "more.kundali_milan": "કુંડળી મિલન (36 ગુણ)",
    # EN: Today's Rashifal
    "more.rashifal": "આજનું રાશિફળ",
    # EN: Today's Panchang
    "more.panchang": "આજનું પંચાંગ",
    # EN: All 27 nakshatras
    "list.naks": "બધાં 27 નક્ષત્ર",
    # EN: All 12 rashis
    "list.rashis": "બધી 12 રાશિ",
    # EN: {name} ({english})
    # keep: {name}
    "sign": "{name}",
    # EN: {name} · {english}
    # keep: {name}
    "sign.pill": "{name}",
    # EN: <strong>Today the Moon is in {name} (at sunrise in New Delhi).</strong>
    # keep: {name}
    "today.same": "<strong>આજે ચંદ્ર {name}માં છે (નવી દિલ્હીમાં સૂર્યોદય સમયે).</strong>",
    # EN: Today's nakshatra is <a href="{href}"><strong>{name}</strong></a> (at sunrise in New
    #     Delhi).
    # keep: {href} {name}
    "today.other": "આજનું નક્ષત્ર <a href=\"{href}\"><strong>{name}</strong></a> છે (નવી દિલ્હીમાં સૂર્યોદય સમયે).",
    # EN: Its end time, the tithi and Rahu Kaal are on <a href="{pan}">today's Panchang</a>.
    # keep: {pan}
    "today.tail": " તેના અંતનો સમય, તિથિ અને રાહુકાળ <a href=\"{pan}\">આજના પંચાંગ</a> પર છે.",
    # EN: Nakshatras
    "crumb.naks": "નક્ષત્ર",
    # EN: Rashis
    "crumb.rashis": "રાશિ",
    # EN: Nakshatra not found
    "nf.nak": "નક્ષત્ર મળ્યું નથી",
    # EN: Rashi not found
    "nf.rashi": "રાશિ મળી નથી",
    # EN: Nature and traits
    "trait_head": "સ્વભાવ અને લક્ષણો",
    # EN: male
    "gender.male": "પુરુષ",
    # EN: female
    "gender.female": "સ્ત્રી",
    # EN: Fire
    "element.Fire": "અગ્નિ",
    # EN: Earth
    "element.Earth": "પૃથ્વી",
    # EN: Air
    "element.Air": "વાયુ",
    # EN: Water
    "element.Water": "જળ",
    # EN: Movable (Chara)
    "quality.Cardinal": "ચર",
    # EN: Fixed (Sthira)
    "quality.Fixed": "સ્થિર",
    # EN: Dual (Dwiswabhava)
    "quality.Mutable": "દ્વિસ્વભાવ",
    # EN: {name} Nakshatra — Deity, Lord, Gana, Yoni, Nadi & Name Letters ({lat}) | {brand}
    # keep: {brand} {name}
    "nak.title": "{name} નક્ષત્ર — દેવતા, સ્વામી, ગણ, યોનિ, નાડી અને નામના અક્ષર | {brand}",
    # EN: {name} nakshatra ({name_hi}): {span}, ruled by {lord}, deity {deity_short}, {gana} gana,
    #     {nadi} nadi, {yoni} yoni. Name syllables {lat} and traits.
    # keep: {gana} {lord} {nadi} {name} {span} {yoni}
    # may also use: {name_en}
    "nak.desc": "{name} નક્ષત્ર: {span}, સ્વામી {lord}, {gana} ગણ, {nadi} નાડી, {yoni} યોનિ. નામના અક્ષર અને સ્વભાવ.",
    # EN: <h1>{name} Nakshatra</h1>
    # keep: {name}
    "nak.h1": "<h1>{name} નક્ષત્ર</h1>",
    # EN: <p class="hi" lang="hi">{name_hi} नक्षत्र</p>
    # may also use: {name_en} {name}
    "nak.sub": "<p class=\"hi\">નક્ષત્રના નામાક્ષર, ચરણ અને સ્વભાવ</p>",
    # EN: <p class="note">These are traditional tendencies, not verdicts. Your full kundali —
    #     ascendant, planets and dasha — gives the personal picture.</p>
    "nak.trait_note": "<p class=\"note\">આ પરંપરાગત વલણો છે, ચુકાદા નથી. તમારી પૂરી કુંડળી — લગ્ન, ગ્રહો અને દશા — અંગત ચિત્ર આપે છે.</p>",
    # EN: Number
    "f.number": "ક્રમાંક",
    # EN: {n} of 27
    # keep: {n}
    "f.number_v": "27માંથી {n}",
    # EN: Span (sidereal)
    "f.span": "વિસ્તાર (નિરયન)",
    # EN: Rashi
    "f.rashi": "રાશિ",
    # EN: Ruling planet (Vimshottari lord)
    "f.lord": "સ્વામી ગ્રહ (વિંશોત્તરી સ્વામી)",
    # EN: {lord} <small>{years}-year mahadasha</small>
    # keep: {lord} {years}
    "f.lord_v": "{lord} <small>{years} વર્ષની મહાદશા</small>",
    # EN: Deity
    "f.deity": "દેવતા",
    # EN: Symbol
    "f.symbol": "ચિહ્ન",
    # EN: Gana
    "f.gana": "ગણ",
    # EN: {gana} <small lang="hi">{gana_hi}</small>
    # keep: {gana}
    "f.gana_v": "{gana}",
    # EN: Yoni (animal)
    "f.yoni": "યોનિ (પ્રાણી)",
    # EN: Nadi
    "f.nadi": "નાડી",
    # EN: Varna (from its rashi, as used in Guna Milan)
    "f.varna": "વર્ણ (તેની રાશિ પરથી, ગુણ મિલનમાં વપરાય છે તેમ)",
    # EN: Name syllables (namakshar)
    "f.syl": "નામના અક્ષર (નામાક્ષર)",
    # EN: <span class="syl" lang="hi">{syl}</span> <small>{lat}</small>
    # keep: {syl}
    "f.syl_v": "<span class=\"syl\">{syl}</span>",
    # EN: The four padas and their name syllables
    "pada.title": "ચાર ચરણ અને તેમના નામાક્ષર",
    # EN: <tr><th>Pada</th><th>Span</th><th>Rashi</th><th>Name syllable</th></tr>
    "pada.head": "<tr><th>ચરણ</th><th>વિસ્તાર</th><th>રાશિ</th><th>નામાક્ષર</th></tr>",
    # EN: <p class="note">Traditionally a child's name begins with the syllable of the pada the Moon
    #     occupied at birth (namakshar). Syllables follow the 108-pada Swar Siddhanta list (the
    #     Avakahada Chakra) as published by Drik Panchang.</p>
    "pada.note": "<p class=\"note\">પરંપરા મુજબ બાળકનું નામ જન્મ સમયે ચંદ્ર જે ચરણમાં હતો તેના અક્ષરથી શરૂ થાય છે (નામાક્ષર). અક્ષરો દ્રિક પંચાંગે પ્રસિદ્ધ કરેલી 108 ચરણવાળી સ્વર સિદ્ધાંત યાદી (અવકહડા ચક્ર) મુજબ છે.</p>",
    # EN: Related
    "rel.heading": "સંબંધિત",
    # EN: Today's {name} Rashifal
    # keep: {name}
    "rel.rashifal": "આજનું {name} રાશિફળ",
    # EN: The 27 Nakshatras — Lords, Deities, Gana & Name Syllables | {brand}
    # keep: {brand}
    "ni.title": "27 નક્ષત્ર — સ્વામી, દેવતા, ગણ અને નામાક્ષર | {brand}",
    # EN: All 27 nakshatras from Ashwini to Revati: span, rashi, ruling planet, deity, gana, yoni,
    #     nadi and the name syllables of all four padas — consistent with our Kundali Milan tables.
    "ni.desc": "અશ્વિનીથી રેવતી સુધીનાં બધાં 27 નક્ષત્ર: વિસ્તાર, રાશિ, સ્વામી ગ્રહ, દેવતા, ગણ, યોનિ, નાડી અને ચારેય ચરણના નામાક્ષર — અમારા કુંડળી મિલન કોષ્ટકો સાથે સુસંગત.",
    # EN: <h1>The 27 Nakshatras</h1>
    "ni.h1": "<h1>27 નક્ષત્ર</h1>",
    # EN: <p class="hi" lang="hi">27 नक्षत्र</p>
    "ni.sub": "<p class=\"hi\">નક્ષત્રોની યાદી — સ્વામી, દેવતા, ગણ અને નામાક્ષર</p>",
    # EN: <p>Vedic astrology divides the zodiac into 27 nakshatras (lunar mansions) of 13°20′ each,
    #     and each nakshatra into four padas of 3°20′. The 108 padas fall exactly nine to a sign
    #     across the 12 rashis. Your birth nakshatra is the one the Moon occupied when you were
    #     born: it starts your Vimshottari dasha and drives the Tara, Yoni, Gana and Nadi kootas of
    #     Kundali Milan.</p>
    "ni.intro": "<p>વૈદિક જ્યોતિષ રાશિચક્રને 13°20′ના 27 નક્ષત્રોમાં વહેંચે છે, અને દરેક નક્ષત્રને 3°20′ના ચાર ચરણમાં. 108 ચરણ 12 રાશિમાં બરાબર નવ-નવ પ્રમાણે ગોઠવાય છે. તમારું જન્મ નક્ષત્ર એ છે જેમાં તમારા જન્મ સમયે ચંદ્ર હતો: તેનાથી તમારી વિંશોત્તરી દશા શરૂ થાય છે અને કુંડળી મિલનના તારા, યોનિ, ગણ અને નાડી કૂટ નક્કી થાય છે.</p>",
    # EN: <tr><th>#</th><th>Nakshatra</th><th>Rashi</th><th>Lord</th><th>Gana</th><th>Name
    #     syllables</th></tr>
    "ni.head": "<tr><th>#</th><th>નક્ષત્ર</th><th>રાશિ</th><th>સ્વામી</th><th>ગણ</th><th>નામાક્ષર</th></tr>",
    # EN: {name} Rashi ({english}) — Lord, Element, Nakshatras & Name Letters | {brand}
    # keep: {brand} {name}
    # may also use: {english}
    "rs.title": "{name} રાશિ — સ્વામી, તત્ત્વ, નક્ષત્ર અને નામના અક્ષર | {brand}",
    # EN: {name} rashi ({english} Moon sign, {name_hi}): ruled by {lord}, {element_lower} element,
    #     {quality_lower} quality. Its 9 nakshatra padas, name syllables ({lat}) and traits.
    # keep: {lord} {name}
    # may also use: {element_lower} {element} {english} {name_en} {quality_lower} {quality}
    "rs.desc": "{name} રાશિ (ચંદ્ર રાશિ): સ્વામી {lord}. તેના 9 નક્ષત્ર ચરણ, નામાક્ષર અને સ્વભાવ.",
    # EN: <h1>{name} Rashi — {english} Moon Sign</h1>
    # keep: {name}
    # may also use: {english}
    "rs.h1": "<h1>{name} રાશિ — ચંદ્ર રાશિ</h1>",
    # EN: <p class="hi" lang="hi">{name_hi} राशि</p>
    # may also use: {english} {name_en} {name}
    "rs.sub": "<p class=\"hi\">રાશિના ગુણ, નક્ષત્ર ચરણ અને નામાક્ષર</p>",
    # EN: Read today's {name} Rashifal
    # keep: {name}
    "rs.today": "આજનું {name} રાશિફળ વાંચો",
    # EN: <p class="note">In Vedic astrology "rashi" usually means the Moon sign — the sign the Moon
    #     occupied at birth, in the sidereal zodiac. It is often different from a Western sun
    #     sign.</p>
    "rs.note": "<p class=\"note\">વૈદિક જ્યોતિષમાં “રાશિ” સામાન્ય રીતે ચંદ્ર રાશિ એટલે કે નિરયન રાશિચક્રમાં જન્મ સમયે ચંદ્ર જે રાશિમાં હતો તે. તે ઘણી વાર પશ્ચિમી સૂર્ય રાશિથી અલગ હોય છે.</p>",
    # EN: Number
    "r.number": "ક્રમાંક",
    # EN: {n} of 12
    # keep: {n}
    "r.number_v": "12માંથી {n}",
    # EN: Span (sidereal zodiac)
    "r.span": "વિસ્તાર (નિરયન રાશિચક્ર)",
    # EN: Sign lord
    "r.lord": "રાશિ સ્વામી",
    # EN: Element
    "r.element": "તત્ત્વ",
    # EN: Quality
    "r.quality": "ગુણ",
    # EN: Varna (used in Guna Milan)
    "r.varna": "વર્ણ (ગુણ મિલનમાં વપરાય છે)",
    # EN: Nakshatras
    "r.naks": "નક્ષત્ર",
    # EN: Name syllables (namakshar)
    "r.syl": "નામના અક્ષર (નામાક્ષર)",
    # EN: <span class="syl" lang="hi">{syl}</span>
    # keep: {syl}
    "r.syl_v": "<span class=\"syl\">{syl}</span>",
    # EN: The nine nakshatra padas in this sign
    "rp.title": "આ રાશિનાં નવ નક્ષત્ર ચરણ",
    # EN: <tr><th>Nakshatra</th><th>Pada</th><th>Degrees in sign</th><th>Syllable</th></tr>
    "rp.head": "<tr><th>નક્ષત્ર</th><th>ચરણ</th><th>રાશિમાં અંશ</th><th>અક્ષર</th></tr>",
    # EN: The 12 Rashis — Lords, Elements, Nakshatras & Name Letters | {brand}
    # keep: {brand}
    "ri.title": "12 રાશિ — સ્વામી, તત્ત્વ, નક્ષત્ર અને નામના અક્ષર | {brand}",
    # EN: All 12 rashis (Vedic Moon signs) from Mesh to Meen: sign lord, element, quality, the nine
    #     nakshatra padas in each and their name syllables (namakshar).
    "ri.desc": "મેષથી મીન સુધીની બધી 12 રાશિ (વૈદિક ચંદ્ર રાશિ): રાશિ સ્વામી, તત્ત્વ, ગુણ, દરેકમાં નવ નક્ષત્ર ચરણ અને તેમના નામાક્ષર.",
    # EN: <h1>The 12 Rashis (Moon Signs)</h1>
    "ri.h1": "<h1>12 રાશિ (ચંદ્ર રાશિ)</h1>",
    # EN: <p class="hi" lang="hi">12 राशियाँ</p>
    "ri.sub": "<p class=\"hi\">રાશિઓની યાદી — સ્વામી, તત્ત્વ, નક્ષત્ર</p>",
    # EN: <p>Each rashi spans 30° of the sidereal zodiac and holds exactly nine nakshatra padas.
    #     Your rashi is your Moon sign — the sign the Moon occupied at birth — and it is what
    #     rashifal, Sade Sati and Kundali Milan are read from.</p>
    "ri.intro": "<p>દરેક રાશિ નિરયન રાશિચક્રના 30°માં ફેલાયેલી છે અને તેમાં બરાબર નવ નક્ષત્ર ચરણ આવે છે. તમારી રાશિ એટલે તમારી ચંદ્ર રાશિ — જન્મ સમયે ચંદ્ર જે રાશિમાં હતો — અને તેના પરથી રાશિફળ, સાડાસાતી અને કુંડળી મિલન વંચાય છે.</p>",
    # EN: <tr><th>Rashi</th><th>Lord</th><th>Element</th><th>Nakshatras</th><th>Name
    #     syllables</th></tr>
    "ri.head": "<tr><th>રાશિ</th><th>સ્વામી</th><th>તત્ત્વ</th><th>નક્ષત્ર</th><th>નામાક્ષર</th></tr>",
    # EN: {name} <small>{english}</small>
    # keep: {name}
    # may also use: {english}
    "ri.name": "{name}",
    # EN: Vata
    "humour.Vata": "વાત",
    # EN: Pitta
    "humour.Pitta": "પિત્ત",
    # EN: Kapha
    "humour.Kapha": "કફ",
}

# app/nakshatra_text.py NAKSHATRA_TRAITS["gu"] — character paragraph of each of the 27 nakshatras (key = slug)  [27]
NAKSHATRA_TRAITS = {
    # EN: Ashwini is the first nakshatra, ruled by the Ashwini Kumaras, the twin healers of the
    #     gods, and symbolised by a horse's head. People with the Moon here are often quick,
    #     energetic and eager to begin things — the first to help, the first to try something new.
    #     Tradition links Ashwini with healing, speed and fresh starts, so many feel drawn to
    #     medicine, sport, travel or any work that needs swift, practical action. The gift of this
    #     nakshatra is initiative and a youthful optimism; the lesson is patience, finishing what
    #     was started with the same enthusiasm with which it began.
    "ashwini": "અશ્વિની પહેલું નક્ષત્ર છે, જેના સ્વામી દેવોના જોડિયા વૈદ્ય અશ્વિની કુમારો છે અને જેનું પ્રતીક ઘોડાનું માથું છે. ચંદ્ર અહીં હોય તેવા લોકો ઘણી વાર ચપળ, ઉત્સાહી અને કામ શરૂ કરવા આતુર હોય છે — મદદ કરવામાં પહેલા, કંઈક નવું અજમાવવામાં પહેલા. પરંપરા અશ્વિનીને ઉપચાર, ઝડપ અને નવી શરૂઆત સાથે જોડે છે, તેથી ઘણાને તબીબી ક્ષેત્ર, રમતગમત, પ્રવાસ કે ઝડપી, વ્યવહારુ કામ માગતા કોઈ પણ કાર્ય તરફ ખેંચાણ થાય છે. આ નક્ષત્રની ભેટ પહેલ અને યુવાન આશાવાદ છે; શીખવાનું એ છે કે ધીરજ રાખીને, જે ઉત્સાહથી શરૂ કર્યું તે જ ઉત્સાહથી પૂરું કરવું.",
    # EN: Bharani is ruled by Yama, the lord of dharma, and its symbol is the yoni, the womb that
    #     carries and protects new life. People with the Moon here often have strong will, deep
    #     feelings and a serious sense of responsibility. They tend to carry their commitments
    #     through to the end and are not easily swayed. Tradition sees Bharani as the nakshatra of
    #     bearing and nurturing — holding something until it is ready to be born — so creativity,
    #     family, art and work that asks for endurance suit it well. Its strength is steadfastness;
    #     its lesson is balancing desire with restraint and kindness.
    "bharani": "ભરણીના સ્વામી ધર્મરાજ યમ છે અને તેનું પ્રતીક યોનિ છે, જે નવું જીવન ધારણ કરીને તેનું રક્ષણ કરે છે. ચંદ્ર અહીં હોય તેવા લોકોમાં ઘણી વાર મજબૂત ઇચ્છાશક્તિ, ઊંડી લાગણીઓ અને જવાબદારીની ગંભીર સમજ હોય છે. તેઓ પોતાની પ્રતિબદ્ધતા અંત સુધી નિભાવે છે અને સહેલાઈથી ડગતા નથી. પરંપરા ભરણીને ધારણ અને પોષણનું નક્ષત્ર માને છે — કંઈક તૈયાર થઈને જન્મે ત્યાં સુધી તેને સાચવી રાખવું — તેથી સર્જન, કુટુંબ, કલા અને સહનશક્તિ માગતું કામ તેને માફક આવે છે. તેની તાકાત અડગતા છે; શીખવાનું એ છે કે ઇચ્છાને સંયમ અને દયા સાથે સંતુલિત કરવી.",
    # EN: Krittika is ruled by Agni, the sacred fire, and symbolised by a razor or a flame. Fire
    #     purifies and cuts through confusion, and people with the Moon here are often direct,
    #     principled and sharp in judgement. They can be protective of those they love and are
    #     willing to say what needs to be said. Krittika is also the nakshatra of the six mothers
    #     who nursed Kartikeya, so beneath the sharpness there is real warmth and care. Teaching,
    #     cooking, leadership and any work that needs clarity suit it. Its lesson is to let the fire
    #     warm and guide rather than burn.
    "krittika": "કૃત્તિકાના સ્વામી પવિત્ર અગ્નિ, અગ્નિદેવ છે, અને તેનું પ્રતીક અસ્ત્રો કે જ્યોત છે. અગ્નિ શુદ્ધ કરે છે અને મૂંઝવણને કાપી નાખે છે; ચંદ્ર અહીં હોય તેવા લોકો ઘણી વાર સ્પષ્ટવક્તા, સિદ્ધાંતવાદી અને તીક્ષ્ણ નિર્ણયશક્તિવાળા હોય છે. તેઓ પોતાનાં પ્રિયજનોનું રક્ષણ કરે છે અને જે કહેવું જરૂરી હોય તે કહેવા તૈયાર હોય છે. કૃત્તિકા કાર્તિકેયને ધવડાવનાર છ માતાઓનું નક્ષત્ર પણ છે, તેથી તીક્ષ્ણતાની નીચે સાચી હૂંફ અને કાળજી છે. શિક્ષણ, રસોઈ, નેતૃત્વ અને સ્પષ્ટતા માગતું કોઈ પણ કામ તેને માફક આવે છે. શીખવાનું એ છે કે અગ્નિ બાળે નહીં, પણ હૂંફ આપે અને માર્ગ બતાવે.",
    # EN: Rohini is ruled by Brahma, the creator, and symbolised by a chariot or ox-cart. It is said
    #     to be the Moon's favourite nakshatra, and people with the Moon here are often warm,
    #     attractive, artistic and fond of comfort and beauty. They have a gift for making things
    #     grow — gardens, homes, businesses and relationships. Tradition associates Rohini with
    #     fertility, abundance and steady progress, so agriculture, the arts, design, food and
    #     hospitality suit it well. Its nature is gentle and settled; its lesson is to enjoy what is
    #     beautiful without holding on too tightly to it.
    "rohini": "રોહિણીના સ્વામી સર્જક બ્રહ્મા છે અને તેનું પ્રતીક રથ કે બળદગાડું છે. તે ચંદ્રનું સૌથી પ્રિય નક્ષત્ર કહેવાય છે, અને ચંદ્ર અહીં હોય તેવા લોકો ઘણી વાર સ્નેહાળ, આકર્ષક, કલાપ્રેમી અને સુખ-સૌંદર્યના શોખીન હોય છે. વસ્તુઓને ઉછેરવાની — બગીચા, ઘર, વેપાર અને સંબંધો — તેમનામાં કળા હોય છે. પરંપરા રોહિણીને ફળદ્રુપતા, સમૃદ્ધિ અને સ્થિર પ્રગતિ સાથે જોડે છે, તેથી ખેતી, કલા, ડિઝાઇન, ભોજન અને આતિથ્ય તેને માફક આવે છે. તેનો સ્વભાવ નમ્ર અને સ્થિર છે; શીખવાનું એ છે કે જે સુંદર છે તેનો આનંદ લેવો, પણ તેને બહુ ચુસ્તપણે પકડી ન રાખવું.",
    # EN: Mrigashira is ruled by Soma, the Moon, and its symbol is a deer's head — the deer that is
    #     always alert, curious and searching. People with the Moon here are often gentle,
    #     inquisitive and fond of learning, travel and conversation. They enjoy exploring ideas and
    #     places and rarely stop asking questions. Tradition sees Mrigashira as the seeker's
    #     nakshatra, which suits research, writing, teaching, trade and any work that rewards
    #     curiosity. Its charm is a light, friendly mind; its lesson is to settle on what has been
    #     found, so that the search leads somewhere rather than becoming restlessness.
    "mrigashira": "મૃગશીર્ષના સ્વામી સોમ, ચંદ્ર છે અને તેનું પ્રતીક હરણનું માથું છે — હંમેશાં સજાગ, જિજ્ઞાસુ અને શોધતું હરણ. ચંદ્ર અહીં હોય તેવા લોકો ઘણી વાર નમ્ર, જિજ્ઞાસુ અને અભ્યાસ, પ્રવાસ અને વાતચીતના શોખીન હોય છે. તેમને વિચારો અને સ્થળો ખોળવાનું ગમે છે અને પ્રશ્નો પૂછવાનું ભાગ્યે જ બંધ કરે છે. પરંપરા મૃગશીર્ષને શોધકનું નક્ષત્ર માને છે, જે સંશોધન, લેખન, શિક્ષણ, વેપાર અને જિજ્ઞાસાને ઇનામ આપતા કોઈ પણ કામને અનુકૂળ છે. તેનું આકર્ષણ હળવું, મૈત્રીભર્યું મન છે; શીખવાનું એ છે કે જે મળ્યું તેમાં સ્થિર થવું, જેથી શોધ બેચેની બનવાને બદલે ક્યાંક પહોંચે.",
    # EN: Ardra is ruled by Rudra, the storm form of Shiva, and symbolised by a teardrop or a
    #     diamond. As a storm clears the air and brings rain, people with the Moon here often have a
    #     strong, searching intellect and the ability to see through things to the truth. They can
    #     feel deeply and are not afraid of change. Tradition links Ardra with renewal after
    #     difficulty, so research, technology, writing, counselling and problem-solving suit it
    #     well. Its gift is honesty and a sharp mind; its lesson is to let feelings pass like the
    #     rain, leaving the ground greener.
    "ardra": "આર્દ્રાના સ્વામી શિવનું તોફાની સ્વરૂપ રુદ્ર છે, અને તેનું પ્રતીક આંસુનું ટીપું કે હીરો છે. જેમ તોફાન હવા સાફ કરે છે અને વરસાદ લાવે છે, તેમ ચંદ્ર અહીં હોય તેવા લોકો ઘણી વાર મજબૂત, શોધક બુદ્ધિ અને વસ્તુઓની આરપાર સત્ય જોવાની શક્તિ ધરાવે છે. તેઓ ઊંડી લાગણી અનુભવે છે અને પરિવર્તનથી ડરતા નથી. પરંપરા આર્દ્રાને મુશ્કેલી પછીના નવસર્જન સાથે જોડે છે, તેથી સંશોધન, ટેકનોલોજી, લેખન, પરામર્શ અને સમસ્યા ઉકેલવાનું કામ તેને માફક આવે છે. તેની ભેટ પ્રામાણિકતા અને તીક્ષ્ણ મન છે; શીખવાનું એ છે કે લાગણીઓને વરસાદની જેમ પસાર થવા દેવી, જેથી જમીન વધુ લીલી થાય.",
    # EN: Punarvasu is ruled by Aditi, the boundless mother of the gods, and symbolised by a bow and
    #     quiver. Its name means "return of the light", and people with the Moon here are often
    #     optimistic, generous and able to begin again after any setback. They tend to be content
    #     with simple things, good-humoured and caring towards family and guests. Tradition sees
    #     Punarvasu as a nakshatra of renewal and homecoming, suited to teaching, counselling,
    #     writing, travel and caring work. Its blessing is a hopeful, forgiving heart; its lesson is
    #     to aim the arrow — to choose a direction and stay with it.
    "punarvasu": "પુનર્વસુના સ્વામી દેવોની અસીમ માતા અદિતિ છે, અને તેનું પ્રતીક ધનુષ્ય અને ભાથું છે. તેના નામનો અર્થ “પ્રકાશનું પુનરાગમન” છે, અને ચંદ્ર અહીં હોય તેવા લોકો ઘણી વાર આશાવાદી, ઉદાર અને કોઈ પણ આંચકા પછી ફરી શરૂ કરી શકે તેવા હોય છે. તેઓ સાદી વસ્તુઓમાં સંતોષી, હસમુખા અને કુટુંબ તથા મહેમાનો પ્રત્યે કાળજીવાળા હોય છે. પરંપરા પુનર્વસુને નવસર્જન અને ઘરવાપસીનું નક્ષત્ર માને છે, જે શિક્ષણ, પરામર્શ, લેખન, પ્રવાસ અને સેવાનાં કામોને અનુકૂળ છે. તેનો આશીર્વાદ આશાભર્યું, ક્ષમાશીલ હૃદય છે; શીખવાનું એ છે કે તીર સાધવું — દિશા પસંદ કરીને તેમાં ટકી રહેવું.",
    # EN: Pushya is ruled by Brihaspati, the guru of the gods, and symbolised by a cow's udder or a
    #     lotus — images of nourishment. It is counted among the most auspicious nakshatras, and
    #     people with the Moon here are often caring, dependable, devoted and generous with their
    #     time. They like to support others, keep traditions and build something lasting. Tradition
    #     links Pushya with nourishment and wisdom, so teaching, counselling, food, social service,
    #     finance and spiritual work suit it well. Its gift is a steady, protective kindness; its
    #     lesson is to nourish oneself as faithfully as one nourishes others.
    "pushya": "પુષ્યના સ્વામી દેવોના ગુરુ બૃહસ્પતિ છે, અને તેનું પ્રતીક ગાયનું આંચળ કે કમળ છે — પોષણનાં પ્રતીકો. તે સૌથી શુભ નક્ષત્રોમાં ગણાય છે, અને ચંદ્ર અહીં હોય તેવા લોકો ઘણી વાર કાળજીભર્યા, ભરોસાપાત્ર, નિષ્ઠાવાન અને પોતાનો સમય આપવામાં ઉદાર હોય છે. તેમને બીજાને ટેકો આપવો, પરંપરાઓ જાળવવી અને કંઈક કાયમી બનાવવું ગમે છે. પરંપરા પુષ્યને પોષણ અને જ્ઞાન સાથે જોડે છે, તેથી શિક્ષણ, પરામર્શ, ભોજન, સમાજસેવા, નાણાં અને આધ્યાત્મિક કાર્ય તેને માફક આવે છે. તેની ભેટ સ્થિર, રક્ષણાત્મક માયા છે; શીખવાનું એ છે કે બીજાને જેટલી નિષ્ઠાથી પોષીએ તેટલી જ નિષ્ઠાથી જાતને પણ પોષવી.",
    # EN: Ashlesha is ruled by the Nagas, the serpent deities, and symbolised by a coiled serpent —
    #     an image of kundalini, hidden energy and deep wisdom. People with the Moon here are often
    #     perceptive, intelligent and good at understanding what others leave unsaid. They can be
    #     persuasive and strategic, with a strong instinct for self-protection. Tradition links
    #     Ashlesha with insight and with the healing knowledge of herbs, so psychology, research,
    #     medicine, writing and negotiation suit it well. Its gift is penetrating understanding; its
    #     lesson is to use that insight to embrace and heal, the way the serpent's coil protects.
    "ashlesha": "આશ્લેષાના સ્વામી નાગ દેવતાઓ છે, અને તેનું પ્રતીક કુંડળી વાળીને બેઠેલો સર્પ છે — કુંડલિની, છુપાયેલી શક્તિ અને ઊંડા જ્ઞાનની છબિ. ચંદ્ર અહીં હોય તેવા લોકો ઘણી વાર ચતુર, બુદ્ધિશાળી અને બીજાઓ જે કહ્યા વગર છોડે તે સમજવામાં કુશળ હોય છે. તેઓ સમજાવટમાં અને વ્યૂહરચનામાં પાવરધા હોય છે, અને આત્મરક્ષણની પ્રબળ સહજવૃત્તિ ધરાવે છે. પરંપરા આશ્લેષાને આંતરદૃષ્ટિ અને ઔષધિઓના ઉપચાર-જ્ઞાન સાથે જોડે છે, તેથી મનોવિજ્ઞાન, સંશોધન, તબીબી ક્ષેત્ર, લેખન અને વાટાઘાટ તેને માફક આવે છે. તેની ભેટ ઊંડી સમજ છે; શીખવાનું એ છે કે તે સમજનો ઉપયોગ અપનાવવા અને સાજા કરવા માટે કરવો, જેમ સર્પનું ગૂંચળું રક્ષણ કરે છે.",
    # EN: Magha is ruled by the Pitris, the ancestors, and symbolised by a royal throne. People with
    #     the Moon here often carry a natural dignity, a respect for family and tradition, and a
    #     wish to live up to the name they were given. They can be generous leaders who take
    #     responsibility for their people. Tradition links Magha with lineage, honour and authority,
    #     so leadership, administration, history, law and work that preserves heritage suit it well.
    #     Its gift is nobility of heart; its lesson is to wear the crown lightly — to lead through
    #     service and to honour the ancestors through good deeds.
    "magha": "મઘાના સ્વામી પિતૃઓ, પૂર્વજો છે, અને તેનું પ્રતીક રાજ સિંહાસન છે. ચંદ્ર અહીં હોય તેવા લોકોમાં ઘણી વાર સ્વાભાવિક ગરિમા, કુટુંબ અને પરંપરા માટે આદર અને પોતાને મળેલા નામને લાયક બનવાની ઇચ્છા હોય છે. તેઓ ઉદાર નેતા બને છે જે પોતાના લોકોની જવાબદારી ઉપાડે છે. પરંપરા મઘાને વંશ, સન્માન અને અધિકાર સાથે જોડે છે, તેથી નેતૃત્વ, વહીવટ, ઇતિહાસ, કાયદો અને વારસો સાચવતું કામ તેને માફક આવે છે. તેની ભેટ હૃદયની ઉમદાઈ છે; શીખવાનું એ છે કે મુગટ હળવાશથી પહેરવો — સેવા દ્વારા નેતૃત્વ કરવું અને સારાં કર્મો દ્વારા પૂર્વજોનું સન્માન કરવું.",
    # EN: Purva Phalguni is ruled by Bhaga, the god of fortune and marital happiness, and symbolised
    #     by the front legs of a bed — an image of rest and enjoyment. People with the Moon here are
    #     often warm, charming, creative and fond of celebration, music and good company. They bring
    #     people together and know how to relax and enjoy what they have earned. Tradition links
    #     Purva Phalguni with love, the arts and leisure, so entertainment, design, hospitality and
    #     relationship-centred work suit it well. Its gift is joy that is easily shared; its lesson
    #     is balance between pleasure and duty.
    "purva-phalguni": "પૂર્વા ફાલ્ગુનીના સ્વામી ભાગ્ય અને લગ્નસુખના દેવ ભગ છે, અને તેનું પ્રતીક પલંગના આગલા પાયા છે — આરામ અને આનંદની છબિ. ચંદ્ર અહીં હોય તેવા લોકો ઘણી વાર સ્નેહાળ, મોહક, સર્જનશીલ અને ઉત્સવ, સંગીત અને સારા સંગના શોખીન હોય છે. તેઓ લોકોને એકઠા કરે છે અને જે કમાયું તેનો આરામથી આનંદ લેવો જાણે છે. પરંપરા પૂર્વા ફાલ્ગુનીને પ્રેમ, કલા અને નિરાંત સાથે જોડે છે, તેથી મનોરંજન, ડિઝાઇન, આતિથ્ય અને સંબંધ-કેન્દ્રિત કામ તેને માફક આવે છે. તેની ભેટ સહેલાઈથી વહેંચી શકાય તેવો આનંદ છે; શીખવાનું એ છે કે સુખ અને ફરજ વચ્ચે સંતુલન રાખવું.",
    # EN: Uttara Phalguni is ruled by Aryaman, the god of friendship, contracts and marriage vows,
    #     and symbolised by the back legs of a bed. Where its twin Purva Phalguni enjoys, Uttara
    #     Phalguni commits. People with the Moon here are often reliable, helpful, fair-minded and
    #     loyal to friends and partners. They keep their word and like to be of real use to others.
    #     Tradition links this nakshatra with patronage and lasting partnerships, so management,
    #     public service, counselling, law and charitable work suit it well. Its gift is dependable
    #     kindness; its lesson is to accept help as gracefully as it is given.
    "uttara-phalguni": "ઉત્તરા ફાલ્ગુનીના સ્વામી મિત્રતા, કરાર અને લગ્નવચનના દેવ અર્યમા છે, અને તેનું પ્રતીક પલંગના પાછલા પાયા છે. જ્યાં તેની જોડિયા પૂર્વા ફાલ્ગુની આનંદ માણે છે, ત્યાં ઉત્તરા ફાલ્ગુની વચન નિભાવે છે. ચંદ્ર અહીં હોય તેવા લોકો ઘણી વાર ભરોસાપાત્ર, મદદગાર, ન્યાયપ્રિય અને મિત્રો તથા જીવનસાથી પ્રત્યે વફાદાર હોય છે. તેઓ પોતાનો શબ્દ પાળે છે અને બીજાને સાચા અર્થમાં ઉપયોગી થવા માગે છે. પરંપરા આ નક્ષત્રને આશ્રયદાતા ભાવ અને કાયમી ભાગીદારી સાથે જોડે છે, તેથી વ્યવસ્થાપન, જાહેર સેવા, પરામર્શ, કાયદો અને સખાવતી કામ તેને માફક આવે છે. તેની ભેટ ભરોસાપાત્ર માયા છે; શીખવાનું એ છે કે મદદ જેટલી સુંદરતાથી આપીએ તેટલી જ સુંદરતાથી સ્વીકારવી.",
    # EN: Hasta is ruled by Savitr, the radiant Sun, and symbolised by a hand. People with the Moon
    #     here are often skilful, practical, witty and clever with their hands as well as their
    #     minds. They like to get things done and can turn an idea into something real. Tradition
    #     links Hasta with craftsmanship, healing touch and resourcefulness, so crafts, the arts,
    #     surgery, massage, writing, trade and any skilled trade suit it well. Its gift is the
    #     ability to make and to mend; its lesson is to hold things with an open hand, trusting that
    #     effort brings its own rewards.
    "hasta": "હસ્તના સ્વામી તેજસ્વી સૂર્ય સવિતા છે, અને તેનું પ્રતીક હાથ છે. ચંદ્ર અહીં હોય તેવા લોકો ઘણી વાર કુશળ, વ્યવહારુ, હાજરજવાબી અને મનની સાથે હાથના પણ હોંશિયાર હોય છે. તેમને કામ પાર પાડવું ગમે છે અને તેઓ વિચારને વાસ્તવિક રૂપ આપી શકે છે. પરંપરા હસ્તને કારીગરી, ઉપચારના સ્પર્શ અને સૂઝ-સમજ સાથે જોડે છે, તેથી હસ્તકલા, કલા, શસ્ત્રક્રિયા, માલિશ, લેખન, વેપાર અને કોઈ પણ કુશળ ધંધો તેને માફક આવે છે. તેની ભેટ બનાવવાની અને સુધારવાની શક્તિ છે; શીખવાનું એ છે કે વસ્તુઓને ખુલ્લા હાથે પકડવી, એવા ભરોસા સાથે કે પ્રયત્ન પોતાનું ફળ લાવે જ છે.",
    # EN: Chitra is ruled by Tvashtr, also known as Vishwakarma, the divine architect, and
    #     symbolised by a bright jewel. Its name means "brilliant" or "picture", and people with the
    #     Moon here often have a strong sense of beauty, design and form. They enjoy creating things
    #     that are both useful and attractive, and they notice detail. Tradition links Chitra with
    #     architecture, the arts and craftsmanship, so design, engineering, fashion, jewellery,
    #     photography and planning suit it well. Its gift is the eye of an artist and the hand of a
    #     builder; its lesson is to value inner beauty as much as outer polish.
    "chitra": "ચિત્રાના સ્વામી ત્વષ્ટા, એટલે દૈવી શિલ્પી વિશ્વકર્મા છે, અને તેનું પ્રતીક ઝળહળતું રત્ન છે. તેના નામનો અર્થ “તેજસ્વી” કે “ચિત્ર” છે, અને ચંદ્ર અહીં હોય તેવા લોકોમાં ઘણી વાર સૌંદર્ય, ડિઝાઇન અને આકારની પ્રબળ સમજ હોય છે. તેમને ઉપયોગી અને સુંદર બંને હોય તેવી વસ્તુઓ બનાવવી ગમે છે, અને તેઓ ઝીણવટ નોંધે છે. પરંપરા ચિત્રાને સ્થાપત્ય, કલા અને કારીગરી સાથે જોડે છે, તેથી ડિઝાઇન, ઇજનેરી, ફેશન, ઝવેરાત, ફોટોગ્રાફી અને આયોજન તેને માફક આવે છે. તેની ભેટ કલાકારની આંખ અને બાંધકામ કરનારનો હાથ છે; શીખવાનું એ છે કે બહારની ચમક જેટલું જ આંતરિક સૌંદર્યનું મૂલ્ય કરવું.",
    # EN: Swati is ruled by Vayu, the wind, and symbolised by a young shoot swaying in the breeze —
    #     flexible, independent and able to bend without breaking. People with the Moon here often
    #     value freedom, fairness and their own way of doing things. They are usually diplomatic,
    #     courteous and good at business and negotiation. Tradition links Swati with trade, travel
    #     and self-reliance, so commerce, law, diplomacy, communication and independent work suit it
    #     well. Its gift is adaptability and a gentle, balanced manner; its lesson is to put down
    #     roots, so that the young shoot can grow into a strong tree.
    "swati": "સ્વાતિના સ્વામી પવનદેવ વાયુ છે, અને તેનું પ્રતીક પવનમાં ઝૂલતો કૂણો અંકુર છે — લચીલો, સ્વતંત્ર અને તૂટ્યા વગર ઝૂકી શકે તેવો. ચંદ્ર અહીં હોય તેવા લોકો ઘણી વાર સ્વતંત્રતા, ન્યાય અને પોતાની રીતે કામ કરવાને મહત્વ આપે છે. તેઓ સામાન્ય રીતે કુનેહવાળા, વિવેકી અને વેપાર તથા વાટાઘાટમાં કુશળ હોય છે. પરંપરા સ્વાતિને વેપાર, પ્રવાસ અને આત્મનિર્ભરતા સાથે જોડે છે, તેથી વાણિજ્ય, કાયદો, રાજદ્વારી કામ, સંદેશાવ્યવહાર અને સ્વતંત્ર કામ તેને માફક આવે છે. તેની ભેટ અનુકૂલનશીલતા અને નરમ, સંતુલિત વર્તન છે; શીખવાનું એ છે કે મૂળ નાખવા, જેથી કૂણો અંકુર મજબૂત વૃક્ષ બને.",
    # EN: Vishakha is ruled by Indra and Agni together, and symbolised by a triumphal arch decorated
    #     with leaves. People with the Moon here are often purposeful, ambitious and determined to
    #     reach the goal they have set. They have energy, conviction and the patience to keep going
    #     over a long road. Tradition calls Vishakha the nakshatra of purpose, so leadership,
    #     research, politics, sales, teaching and any long-term mission suit it well. Its gift is
    #     focus and the ability to inspire others towards a shared aim; its lesson is to enjoy the
    #     journey, not only the arch at its end.
    "vishakha": "વિશાખાના સ્વામી ઇન્દ્ર અને અગ્નિ બંને સાથે છે, અને તેનું પ્રતીક પાંદડાંથી શણગારેલું વિજય તોરણ છે. ચંદ્ર અહીં હોય તેવા લોકો ઘણી વાર હેતુપૂર્ણ, મહત્વાકાંક્ષી અને પોતે નક્કી કરેલા લક્ષ્ય સુધી પહોંચવા કટિબદ્ધ હોય છે. તેમનામાં શક્તિ, દૃઢ માન્યતા અને લાંબા માર્ગે ચાલતા રહેવાની ધીરજ હોય છે. પરંપરા વિશાખાને હેતુનું નક્ષત્ર કહે છે, તેથી નેતૃત્વ, સંશોધન, રાજકારણ, વેચાણ, શિક્ષણ અને કોઈ પણ લાંબા ગાળાનું ધ્યેય તેને માફક આવે છે. તેની ભેટ એકાગ્રતા અને બીજાને સહિયારા લક્ષ્ય તરફ પ્રેરવાની ક્ષમતા છે; શીખવાનું એ છે કે ફક્ત અંતના તોરણનો નહીં, પણ સફરનો પણ આનંદ લેવો.",
    # EN: Anuradha is ruled by Mitra, the god of friendship and cooperation, and symbolised by a
    #     lotus that blooms out of muddy water. People with the Moon here are often loyal friends,
    #     devoted to their ideals and able to keep going with quiet faith in difficult places. They
    #     are good at bringing people together in groups and organisations. Tradition links Anuradha
    #     with friendship, devotion and success away from home, so teamwork, organisation,
    #     counselling, travel and spiritual practice suit it well. Its gift is the ability to
    #     blossom anywhere; its lesson is to be as gentle with oneself as with friends.
    "anuradha": "અનુરાધાના સ્વામી મૈત્રી અને સહકારના દેવ મિત્ર છે, અને તેનું પ્રતીક કાદવવાળા પાણીમાંથી ખીલતું કમળ છે. ચંદ્ર અહીં હોય તેવા લોકો ઘણી વાર વફાદાર મિત્રો, પોતાના આદર્શોને સમર્પિત અને કઠિન સ્થળોએ પણ શાંત શ્રદ્ધાથી આગળ વધનારા હોય છે. તેઓ જૂથો અને સંસ્થાઓમાં લોકોને એકઠા કરવામાં કુશળ હોય છે. પરંપરા અનુરાધાને મિત્રતા, ભક્તિ અને ઘરથી દૂર સફળતા સાથે જોડે છે, તેથી ટીમવર્ક, સંગઠન, પરામર્શ, પ્રવાસ અને આધ્યાત્મિક સાધના તેને માફક આવે છે. તેની ભેટ ગમે ત્યાં ખીલી શકવાની ક્ષમતા છે; શીખવાનું એ છે કે મિત્રો સાથે જેટલા નરમ છીએ તેટલા જ પોતાની સાથે પણ નરમ રહેવું.",
    # EN: Jyeshtha is ruled by Indra, king of the gods, and symbolised by a circular amulet or
    #     earring. Its name means "the eldest", and people with the Moon here often take on
    #     responsibility early, protect those around them and carry a quiet authority. They are
    #     resourceful, perceptive and capable under pressure. Tradition links Jyeshtha with
    #     seniority and protection, so leadership, management, administration, security and any role
    #     that looks after others suit it well. Its gift is courage and capability; its lesson is to
    #     lead with humility and to let others share the load rather than carrying everything alone.
    "jyeshtha": "જ્યેષ્ઠાના સ્વામી દેવોના રાજા ઇન્દ્ર છે, અને તેનું પ્રતીક ગોળ તાવીજ કે કર્ણફૂલ છે. તેના નામનો અર્થ “સૌથી મોટો” છે, અને ચંદ્ર અહીં હોય તેવા લોકો ઘણી વાર નાની ઉંમરે જવાબદારી ઉપાડે છે, આસપાસનાનું રક્ષણ કરે છે અને શાંત અધિકાર ધરાવે છે. તેઓ સાધનસંપન્ન, નિરીક્ષણશીલ અને દબાણ હેઠળ સક્ષમ હોય છે. પરંપરા જ્યેષ્ઠાને વરિષ્ઠતા અને રક્ષણ સાથે જોડે છે, તેથી નેતૃત્વ, વ્યવસ્થાપન, વહીવટ, સુરક્ષા અને બીજાની સંભાળ રાખતી કોઈ પણ ભૂમિકા તેને માફક આવે છે. તેની ભેટ હિંમત અને ક્ષમતા છે; શીખવાનું એ છે કે નમ્રતાથી નેતૃત્વ કરવું અને બધો ભાર એકલા ઉપાડવાને બદલે બીજાને ભાગ લેવા દેવો.",
    # EN: Mula is ruled by Nirriti and symbolised by a bunch of roots. Its name means "the root",
    #     and people with the Moon here are often drawn to get to the bottom of things — to find the
    #     origin of a question, an idea or a tradition. They can be independent, philosophical and
    #     unafraid to start again from first principles. Tradition links Mula with investigation and
    #     with letting go of what is no longer needed, so research, medicine, philosophy, botany and
    #     spiritual inquiry suit it well. Its gift is depth; its lesson is that clearing old ground
    #     makes room for new growth.
    "mula": "મૂળના સ્વામી નિર્ઋતિ છે, અને તેનું પ્રતીક મૂળિયાંનો ગુચ્છો છે. તેના નામનો અર્થ “મૂળ” છે, અને ચંદ્ર અહીં હોય તેવા લોકો ઘણી વાર વસ્તુઓના મૂળ સુધી પહોંચવા — પ્રશ્ન, વિચાર કે પરંપરાનું મૂળ શોધવા — આકર્ષાય છે. તેઓ સ્વતંત્ર, તત્ત્વચિંતક અને પાયાથી ફરી શરૂ કરવામાં નિર્ભય હોઈ શકે છે. પરંપરા મૂળને તપાસ અને જે હવે જરૂરી નથી તેને છોડી દેવા સાથે જોડે છે, તેથી સંશોધન, તબીબી ક્ષેત્ર, તત્ત્વજ્ઞાન, વનસ્પતિશાસ્ત્ર અને આધ્યાત્મિક શોધ તેને માફક આવે છે. તેની ભેટ ઊંડાણ છે; શીખવાનું એ છે કે જૂની જમીન સાફ કરવાથી નવા વિકાસ માટે જગ્યા થાય છે.",
    # EN: Purva Ashadha is ruled by Apas, the cosmic waters, and symbolised by a winnowing fan or an
    #     elephant tusk. Its name means "the early invincible", and people with the Moon here are
    #     often confident, persuasive and full of conviction. Like water, they can be gentle and yet
    #     wear down any obstacle in time. Tradition links Purva Ashadha with purification and with
    #     victory won through persistence, so teaching, law, debate, the arts, shipping and anything
    #     to do with water suit it well. Its gift is optimism and inner strength; its lesson is to
    #     stay open to other views while holding firm to its own.
    "purva-ashadha": "પૂર્વાષાઢાના સ્વામી કોસ્મિક જળ, અપ્ છે, અને તેનું પ્રતીક સૂપડું કે હાથીદાંત છે. તેના નામનો અર્થ “પહેલો અજેય” છે, અને ચંદ્ર અહીં હોય તેવા લોકો ઘણી વાર આત્મવિશ્વાસુ, સમજાવટમાં કુશળ અને દૃઢ માન્યતાવાળા હોય છે. પાણીની જેમ તેઓ નમ્ર હોવા છતાં સમય જતાં કોઈ પણ અવરોધને ઘસી નાખે છે. પરંપરા પૂર્વાષાઢાને શુદ્ધિ અને દૃઢતાથી મળેલા વિજય સાથે જોડે છે, તેથી શિક્ષણ, કાયદો, વાદ-વિવાદ, કલા, જહાજ-વ્યવસાય અને પાણી સંબંધિત કંઈ પણ તેને માફક આવે છે. તેની ભેટ આશાવાદ અને આંતરિક શક્તિ છે; શીખવાનું એ છે કે પોતાના મત પર અડગ રહેતાં બીજાના મત માટે ખુલ્લા રહેવું.",
    # EN: Uttara Ashadha is ruled by the Vishvedevas, the universal gods, and symbolised by an
    #     elephant tusk. Its name means "the later invincible" — the victory that lasts because it
    #     was earned honestly. People with the Moon here are often principled, patient, responsible
    #     and respected for their integrity. They take the long view and finish what they commit to.
    #     Tradition links Uttara Ashadha with righteous leadership, so government, management, law,
    #     teaching and social causes suit it well. Its gift is steady, ethical strength; its lesson
    #     is to keep a little lightness and warmth alongside the seriousness of duty.
    "uttara-ashadha": "ઉત્તરાષાઢાના સ્વામી વિશ્વેદેવો, સર્વ દેવો છે, અને તેનું પ્રતીક હાથીદાંત છે. તેના નામનો અર્થ “પછીનો અજેય” છે — એવો વિજય જે ટકે છે કારણ કે તે પ્રામાણિકતાથી મેળવ્યો છે. ચંદ્ર અહીં હોય તેવા લોકો ઘણી વાર સિદ્ધાંતવાદી, ધીરજવાળા, જવાબદાર અને પોતાની પ્રામાણિકતા માટે આદર પામેલા હોય છે. તેઓ લાંબું જુએ છે અને જે હાથ પર લે તે પૂરું કરે છે. પરંપરા ઉત્તરાષાઢાને ન્યાયી નેતૃત્વ સાથે જોડે છે, તેથી સરકારી કામ, વ્યવસ્થાપન, કાયદો, શિક્ષણ અને સામાજિક કાર્યો તેને માફક આવે છે. તેની ભેટ સ્થિર, નૈતિક શક્તિ છે; શીખવાનું એ છે કે ફરજની ગંભીરતા સાથે થોડી હળવાશ અને હૂંફ રાખવી.",
    # EN: Shravana is ruled by Vishnu, the preserver, and symbolised by an ear or three footprints.
    #     Its name means "hearing", and people with the Moon here are often good listeners, eager
    #     learners and keepers of knowledge and tradition. They learn by listening and pass on what
    #     they have learned. Tradition links Shravana with wisdom gained through study and with
    #     connecting people, so teaching, counselling, media, languages, music and travel suit it
    #     well. Its gift is attentive understanding and a wish to be useful; its lesson is to listen
    #     to one's own inner voice as carefully as to others.
    "shravana": "શ્રવણના સ્વામી પાલનકર્તા વિષ્ણુ છે, અને તેનું પ્રતીક કાન કે ત્રણ પગલાં છે. તેના નામનો અર્થ “સાંભળવું” છે, અને ચંદ્ર અહીં હોય તેવા લોકો ઘણી વાર સારા શ્રોતા, આતુર વિદ્યાર્થી અને જ્ઞાન તથા પરંપરાના રક્ષક હોય છે. તેઓ સાંભળીને શીખે છે અને જે શીખ્યા તે બીજાને આપે છે. પરંપરા શ્રવણને અભ્યાસથી મળતા જ્ઞાન અને લોકોને જોડવા સાથે સાંકળે છે, તેથી શિક્ષણ, પરામર્શ, માધ્યમો, ભાષાઓ, સંગીત અને પ્રવાસ તેને માફક આવે છે. તેની ભેટ ધ્યાનપૂર્વકની સમજ અને ઉપયોગી થવાની ઇચ્છા છે; શીખવાનું એ છે કે બીજાઓને જેટલા ધ્યાનથી સાંભળીએ તેટલા જ ધ્યાનથી પોતાના અંતરના અવાજને પણ સાંભળવો.",
    # EN: Dhanishta is ruled by the eight Vasus, gods of abundance, and symbolised by a drum. Its
    #     name means "the wealthiest", and people with the Moon here often have rhythm, energy and a
    #     talent for music, dance or teamwork. They are generous, sociable and able to keep a group
    #     moving together. Tradition links Dhanishta with prosperity and with sound, so music,
    #     performance, sport, property, finance and community work suit it well. Its gift is the
    #     ability to set the beat that others follow; its lesson is to listen as well as play,
    #     leaving space for others' rhythms.
    "dhanishta": "ધનિષ્ઠાના સ્વામી સમૃદ્ધિના દેવો, આઠ વસુઓ છે, અને તેનું પ્રતીક ઢોલ (મૃદંગ) છે. તેના નામનો અર્થ “સૌથી ધનવાન” છે, અને ચંદ્ર અહીં હોય તેવા લોકોમાં ઘણી વાર લય, ઊર્જા અને સંગીત, નૃત્ય કે ટીમવર્કની આવડત હોય છે. તેઓ ઉદાર, મિલનસાર અને જૂથને સાથે ચલાવી શકે તેવા હોય છે. પરંપરા ધનિષ્ઠાને સમૃદ્ધિ અને નાદ સાથે જોડે છે, તેથી સંગીત, પ્રદર્શન, રમતગમત, મિલકત, નાણાં અને સમુદાયનું કામ તેને માફક આવે છે. તેની ભેટ એવો તાલ આપવાની ક્ષમતા છે જેને બીજા અનુસરે; શીખવાનું એ છે કે વગાડવાની સાથે સાંભળવું પણ, બીજાના લય માટે જગ્યા રાખવી.",
    # EN: Shatabhisha is ruled by Varuna, lord of the cosmic waters and of truth, and symbolised by
    #     an empty circle. Its name means "a hundred healers", and people with the Moon here are
    #     often independent thinkers, private, truthful and drawn to understanding how things really
    #     work. They can see patterns others miss. Tradition links Shatabhisha with healing and with
    #     the search for hidden truth, so medicine, research, science, technology, astronomy and
    #     alternative healing suit it well. Its gift is clear, original insight; its lesson is to
    #     let others into the circle, sharing what is understood with warmth.
    "shatabhisha": "શતભિષાના સ્વામી કોસ્મિક જળ અને સત્યના સ્વામી વરુણ છે, અને તેનું પ્રતીક ખાલી વર્તુળ છે. તેના નામનો અર્થ “સો વૈદ્યો” છે, અને ચંદ્ર અહીં હોય તેવા લોકો ઘણી વાર સ્વતંત્ર વિચારક, અંતર્મુખ, સત્યવાદી અને વસ્તુઓ ખરેખર કેવી રીતે ચાલે છે તે સમજવા તરફ ખેંચાયેલા હોય છે. તેઓ બીજા ચૂકી જાય તેવી પેટર્ન જોઈ શકે છે. પરંપરા શતભિષાને ઉપચાર અને છુપાયેલા સત્યની શોધ સાથે જોડે છે, તેથી તબીબી ક્ષેત્ર, સંશોધન, વિજ્ઞાન, ટેકનોલોજી, ખગોળશાસ્ત્ર અને વૈકલ્પિક ઉપચાર તેને માફક આવે છે. તેની ભેટ સ્પષ્ટ, મૌલિક આંતરદૃષ્ટિ છે; શીખવાનું એ છે કે બીજાને વર્તુળમાં આવવા દેવા, જે સમજ્યા તે હૂંફથી વહેંચવું.",
    # EN: Purva Bhadrapada is ruled by Aja Ekapada, the one-footed form of Shiva, and symbolised by
    #     swords or the front legs of a cot. People with the Moon here are often idealistic, intense
    #     and willing to give themselves fully to a cause they believe in. They can be eloquent,
    #     generous and deeply spiritual. Tradition links Purva Bhadrapada with transformation and
    #     with the fire of tapas — sincere effort for a higher aim — so social reform, philosophy,
    #     writing, research and spiritual life suit it well. Its gift is passionate commitment; its
    #     lesson is to temper intensity with patience and calm.
    "purva-bhadrapada": "પૂર્વા ભાદ્રપદના સ્વામી શિવનું એકપગવાળું સ્વરૂપ અજ એકપાદ છે, અને તેનું પ્રતીક તલવારો કે ખાટલાના આગલા પાયા છે. ચંદ્ર અહીં હોય તેવા લોકો ઘણી વાર આદર્શવાદી, તીવ્ર અને પોતે જેમાં માને તે કાર્ય માટે સંપૂર્ણ સમર્પણ કરવા તૈયાર હોય છે. તેઓ વાક્પટુ, ઉદાર અને ઊંડા આધ્યાત્મિક હોઈ શકે છે. પરંપરા પૂર્વા ભાદ્રપદને પરિવર્તન અને તપની અગ્નિ — ઊંચા ધ્યેય માટેનો સાચો પ્રયત્ન — સાથે જોડે છે, તેથી સામાજિક સુધારા, તત્ત્વજ્ઞાન, લેખન, સંશોધન અને આધ્યાત્મિક જીવન તેને માફક આવે છે. તેની ભેટ ઉત્કટ પ્રતિબદ્ધતા છે; શીખવાનું એ છે કે તીવ્રતાને ધીરજ અને શાંતિથી સંતુલિત કરવી.",
    # EN: Uttara Bhadrapada is ruled by Ahir Budhnya, the serpent of the deep waters, and symbolised
    #     by the back legs of a cot or twins. Where Purva Bhadrapada burns, Uttara Bhadrapada
    #     settles into calm depth. People with the Moon here are often wise, patient, composed and
    #     compassionate, with self-control and a gift for counsel. They tend to think before they
    #     speak and are steady in difficult times. Tradition links this nakshatra with depth,
    #     renunciation and kindness, so counselling, charity, teaching, research and spiritual
    #     practice suit it well. Its gift is serene wisdom; its lesson is to share it actively, not
    #     only privately.
    "uttara-bhadrapada": "ઉત્તરા ભાદ્રપદના સ્વામી ઊંડા જળના સર્પ અહિર્બુધ્ન્ય છે, અને તેનું પ્રતીક ખાટલાના પાછલા પાયા કે જોડિયાં છે. જ્યાં પૂર્વા ભાદ્રપદ બળે છે, ત્યાં ઉત્તરા ભાદ્રપદ શાંત ઊંડાણમાં ઠરે છે. ચંદ્ર અહીં હોય તેવા લોકો ઘણી વાર જ્ઞાની, ધીરજવાળા, સ્થિર અને કરુણાળુ હોય છે, સંયમ અને સલાહ આપવાની ભેટ સાથે. તેઓ બોલતાં પહેલાં વિચારે છે અને મુશ્કેલ સમયમાં સ્થિર રહે છે. પરંપરા આ નક્ષત્રને ઊંડાણ, ત્યાગ અને માયા સાથે જોડે છે, તેથી પરામર્શ, દાન, શિક્ષણ, સંશોધન અને આધ્યાત્મિક સાધના તેને માફક આવે છે. તેની ભેટ શાંત જ્ઞાન છે; શીખવાનું એ છે કે તેને માત્ર અંગત રીતે નહીં, પણ સક્રિય રીતે વહેંચવું.",
    # EN: Revati, the last nakshatra, is ruled by Pushan, the nourisher who guides travellers and
    #     protects herds on their way, and symbolised by a fish. People with the Moon here are often
    #     gentle, kind, imaginative and protective of the weak, with a love of animals, art and
    #     music. They make good companions on any journey and help others reach their destination
    #     safely. Tradition links Revati with safe journeys, prosperity and completion, so caring
    #     work, the arts, travel, hospitality and spiritual life suit it well. Its gift is
    #     compassion and faith; its lesson is to care for oneself while caring for everyone else.
    "revati": "રેવતી, છેલ્લું નક્ષત્ર, પોષક અને પ્રવાસીઓના માર્ગદર્શક તથા પશુઓના રક્ષક પૂષણના અધિકારમાં છે, અને તેનું પ્રતીક માછલી છે. ચંદ્ર અહીં હોય તેવા લોકો ઘણી વાર નમ્ર, માયાળુ, કલ્પનાશીલ અને નબળાનું રક્ષણ કરનારા હોય છે, તેમને પ્રાણીઓ, કલા અને સંગીત પ્રત્યે પ્રેમ હોય છે. તેઓ કોઈ પણ સફરમાં સારા સાથી બને છે અને બીજાને સુરક્ષિત રીતે મુકામે પહોંચવામાં મદદ કરે છે. પરંપરા રેવતીને સુરક્ષિત પ્રવાસ, સમૃદ્ધિ અને પૂર્ણતા સાથે જોડે છે, તેથી સેવાનાં કામ, કલા, પ્રવાસ, આતિથ્ય અને આધ્યાત્મિક જીવન તેને માફક આવે છે. તેની ભેટ કરુણા અને શ્રદ્ધા છે; શીખવાનું એ છે કે બીજા બધાની કાળજી રાખતાં પોતાની પણ કાળજી રાખવી.",
}

# app/nakshatra_text.py RASHI_TRAITS["gu"] — character paragraph of each of the 12 rashis (key = slug)  [12]
RASHI_TRAITS = {
    # EN: Mesh (Aries) is the first rashi, a movable fire sign ruled by Mars. People with the Moon
    #     in Mesh are often energetic, direct, courageous and quick to act — natural starters who
    #     enjoy a challenge and like to lead from the front. They are honest about their feelings
    #     and recover quickly from setbacks. Their emotional life is warm and spontaneous, and they
    #     bring enthusiasm wherever they go. Work that rewards initiative — sport, the armed forces,
    #     engineering, entrepreneurship, surgery — often suits them. Their growth lies in patience
    #     and in listening before acting, so that their courage is matched by care for others.
    "mesh": "મેષ પહેલી રાશિ છે, મંગળની સ્વામિત્વવાળી ચર અગ્નિ રાશિ. ચંદ્ર મેષમાં હોય તેવા લોકો ઘણી વાર ઊર્જાવાન, સીધા, સાહસિક અને ઝડપથી પગલું ભરનારા હોય છે — સ્વાભાવિક શરૂઆત કરનારા, જેમને પડકાર ગમે છે અને જે આગળ રહીને નેતૃત્વ કરવા માગે છે. તેઓ પોતાની લાગણીઓ વિશે પ્રામાણિક હોય છે અને આંચકામાંથી ઝડપથી બહાર આવે છે. તેમનું ભાવનાત્મક જીવન હૂંફાળું અને સ્વયંસ્ફુરિત છે, અને તેઓ જ્યાં જાય ત્યાં ઉત્સાહ લાવે છે. પહેલને ઇનામ આપતું કામ — રમતગમત, સશસ્ત્ર દળો, ઇજનેરી, ઉદ્યોગસાહસ, શસ્ત્રક્રિયા — ઘણી વાર તેમને માફક આવે છે. તેમની વૃદ્ધિ ધીરજ અને કામ કરતાં પહેલાં સાંભળવામાં છે, જેથી તેમની હિંમત બીજાની કાળજી સાથે જોડાય.",
    # EN: Vrishabh (Taurus) is a fixed earth sign ruled by Venus, and the Moon is exalted here.
    #     People with the Moon in Vrishabh are often calm, patient, loyal and steady, with a love of
    #     comfort, good food, music and beautiful things. They build slowly and surely, and what
    #     they build tends to last. Emotionally they are dependable and affectionate, preferring
    #     security to drama. Finance, agriculture, the arts, food, design and any work that rewards
    #     persistence often suit them. Their growth lies in flexibility — welcoming change when it
    #     comes, and holding possessions and opinions a little more lightly.
    "vrishabh": "વૃષભ સ્થિર પૃથ્વી રાશિ છે, શુક્રની સ્વામિત્વવાળી, અને ચંદ્ર અહીં ઉચ્ચનો છે. ચંદ્ર વૃષભમાં હોય તેવા લોકો ઘણી વાર શાંત, ધીરજવાળા, વફાદાર અને સ્થિર હોય છે, સુખ-સગવડ, સારું ભોજન, સંગીત અને સુંદર વસ્તુઓના શોખીન. તેઓ ધીમે પણ ચોક્કસ બાંધે છે, અને જે બાંધે છે તે ટકે છે. ભાવનાત્મક રીતે તેઓ ભરોસાપાત્ર અને સ્નેહાળ છે, નાટકને બદલે સુરક્ષા પસંદ કરે છે. નાણાં, ખેતી, કલા, ભોજન, ડિઝાઇન અને દૃઢતાને ઇનામ આપતું કોઈ પણ કામ ઘણી વાર તેમને માફક આવે છે. તેમની વૃદ્ધિ લવચીકતામાં છે — પરિવર્તન આવે ત્યારે તેનું સ્વાગત કરવું અને સંપત્તિ તથા મંતવ્યોને થોડા હળવાશથી પકડવા.",
    # EN: Mithun (Gemini) is a dual air sign ruled by Mercury. People with the Moon in Mithun are
    #     often curious, witty, talkative and quick to learn, with many interests and a gift for
    #     connecting ideas and people. They enjoy conversation, reading, travel and anything that
    #     keeps the mind busy. Emotionally they need variety and a partner who is also a friend they
    #     can talk to. Writing, teaching, media, sales, technology and trade often suit them. Their
    #     growth lies in depth and focus — choosing a few things and seeing them through — and in
    #     giving their own feelings the attention they give to ideas.
    "mithun": "મિથુન દ્વિસ્વભાવ વાયુ રાશિ છે, બુધની સ્વામિત્વવાળી. ચંદ્ર મિથુનમાં હોય તેવા લોકો ઘણી વાર જિજ્ઞાસુ, હાજરજવાબી, વાતોડિયા અને ઝડપથી શીખનારા હોય છે, ઘણા રસ અને વિચારો તથા લોકોને જોડવાની આવડત સાથે. તેમને વાતચીત, વાંચન, પ્રવાસ અને મનને વ્યસ્ત રાખતી દરેક વસ્તુ ગમે છે. ભાવનાત્મક રીતે તેમને વિવિધતા અને એવા જીવનસાથીની જરૂર છે જે મિત્ર પણ હોય અને જેની સાથે વાત કરી શકાય. લેખન, શિક્ષણ, માધ્યમો, વેચાણ, ટેકનોલોજી અને વેપાર ઘણી વાર તેમને માફક આવે છે. તેમની વૃદ્ધિ ઊંડાણ અને એકાગ્રતામાં છે — થોડી વસ્તુઓ પસંદ કરીને તેને પૂરી કરવી — અને પોતાની લાગણીઓને એટલું ધ્યાન આપવું જેટલું વિચારોને આપે છે.",
    # EN: Kark (Cancer) is a movable water sign ruled by the Moon itself, so the Moon is at home
    #     here. People with the Moon in Kark are often caring, sensitive, intuitive and devoted to
    #     family and home. They remember kindness, protect those they love and create warmth
    #     wherever they live. Their moods can change like the tides, but their loyalty runs deep.
    #     Nursing, teaching, hospitality, food, real estate, counselling and public service often
    #     suit them. Their growth lies in trusting their own strength, letting go of old hurts and
    #     allowing others to care for them in return.
    "kark": "કર્ક ચર જળ રાશિ છે, જેના સ્વામી ખુદ ચંદ્ર છે, તેથી ચંદ્ર અહીં પોતાના ઘરમાં છે. ચંદ્ર કર્કમાં હોય તેવા લોકો ઘણી વાર કાળજીવાળા, સંવેદનશીલ, સહજબુદ્ધિવાળા અને કુટુંબ તથા ઘરને સમર્પિત હોય છે. તેઓ દયા યાદ રાખે છે, પ્રિયજનોનું રક્ષણ કરે છે અને જ્યાં રહે ત્યાં હૂંફ સર્જે છે. તેમનો મિજાજ ભરતી-ઓટની જેમ બદલાય છે, પણ વફાદારી ઊંડી હોય છે. નર્સિંગ, શિક્ષણ, આતિથ્ય, ભોજન, સ્થાવર મિલકત, પરામર્શ અને જાહેર સેવા ઘણી વાર તેમને માફક આવે છે. તેમની વૃદ્ધિ પોતાની શક્તિ પર ભરોસો કરવામાં, જૂના ઘા ભૂલવામાં અને બદલામાં બીજાને પોતાની કાળજી લેવા દેવામાં છે.",
    # EN: Simha (Leo) is a fixed fire sign ruled by the Sun. People with the Moon in Simha are often
    #     generous, dignified, confident and warm-hearted, with a natural sense of leadership and a
    #     love of recognition. They are loyal to those who trust them and protective of their family
    #     and friends. Emotionally they are proud and open-hearted, and they shine when appreciated.
    #     Leadership, administration, politics, the performing arts, teaching and government service
    #     often suit them. Their growth lies in humility — letting others share the stage, and
    #     finding confidence from within rather than from applause.
    "simha": "સિંહ સ્થિર અગ્નિ રાશિ છે, સૂર્યની સ્વામિત્વવાળી. ચંદ્ર સિંહમાં હોય તેવા લોકો ઘણી વાર ઉદાર, ગરિમાવાળા, આત્મવિશ્વાસુ અને દયાળુ હૃદયવાળા હોય છે, સ્વાભાવિક નેતૃત્વ અને માન્યતાની ઇચ્છા સાથે. જેઓ તેમના પર ભરોસો કરે તેમના પ્રત્યે તેઓ વફાદાર અને કુટુંબ-મિત્રોના રક્ષક હોય છે. ભાવનાત્મક રીતે તેઓ સ્વમાની અને ખુલ્લા દિલના છે, અને પ્રશંસા મળે ત્યારે ચમકે છે. નેતૃત્વ, વહીવટ, રાજકારણ, પ્રદર્શન કલા, શિક્ષણ અને સરકારી સેવા ઘણી વાર તેમને માફક આવે છે. તેમની વૃદ્ધિ નમ્રતામાં છે — બીજાને મંચ વહેંચવા દેવો, અને તાળીઓ નહીં પણ અંદરથી આત્મવિશ્વાસ મેળવવો.",
    # EN: Kanya (Virgo) is a dual earth sign ruled by Mercury. People with the Moon in Kanya are
    #     often practical, analytical, modest and helpful, with an eye for detail and a wish to make
    #     things work properly. They show care through service — fixing, organising and looking
    #     after the small things others overlook. Emotionally they can be reserved, but they are
    #     deeply dependable. Medicine, accounting, research, editing, nutrition, teaching and any
    #     precise craft often suit them. Their growth lies in self-acceptance: being as kind to
    #     their own imperfections as they are patient with other people's needs.
    "kanya": "કન્યા દ્વિસ્વભાવ પૃથ્વી રાશિ છે, બુધની સ્વામિત્વવાળી. ચંદ્ર કન્યામાં હોય તેવા લોકો ઘણી વાર વ્યવહારુ, વિશ્લેષણાત્મક, વિનમ્ર અને મદદગાર હોય છે, ઝીણવટ પર નજર અને વસ્તુઓ બરાબર ચાલે તેવી ઇચ્છા સાથે. તેઓ સેવા દ્વારા કાળજી બતાવે છે — સુધારીને, ગોઠવીને અને બીજા જે નાની વાતો ચૂકી જાય તેની સંભાળ રાખીને. ભાવનાત્મક રીતે તેઓ અંતર્મુખ હોઈ શકે, પણ ઊંડા ભરોસાપાત્ર હોય છે. તબીબી ક્ષેત્ર, હિસાબ, સંશોધન, સંપાદન, પોષણ, શિક્ષણ અને કોઈ પણ ચોકસાઈવાળી કારીગરી ઘણી વાર તેમને માફક આવે છે. તેમની વૃદ્ધિ સ્વ-સ્વીકારમાં છે: બીજાની જરૂરિયાતો માટે જેટલી ધીરજ રાખે છે તેટલી જ દયા પોતાની ખામીઓ પ્રત્યે રાખવી.",
    # EN: Tula (Libra) is a movable air sign ruled by Venus, symbolised by the scales. People with
    #     the Moon in Tula are often gracious, fair-minded, sociable and diplomatic, with a strong
    #     sense of beauty and justice. They value harmony in relationships and are good at seeing
    #     both sides of a question. Emotionally they need partnership and feel most at ease when
    #     things around them are balanced. Law, diplomacy, design, fashion, the arts, counselling
    #     and business partnerships often suit them. Their growth lies in decisiveness — trusting
    #     their own judgement and accepting that a little disagreement can be healthy.
    "tula": "તુલા ચર વાયુ રાશિ છે, શુક્રની સ્વામિત્વવાળી, જેનું પ્રતીક ત્રાજવું છે. ચંદ્ર તુલામાં હોય તેવા લોકો ઘણી વાર સૌજન્યશીલ, ન્યાયપ્રિય, મિલનસાર અને કુનેહવાળા હોય છે, સૌંદર્ય અને ન્યાયની પ્રબળ સમજ સાથે. તેઓ સંબંધોમાં સુમેળને મહત્વ આપે છે અને પ્રશ્નની બંને બાજુ જોવામાં કુશળ હોય છે. ભાવનાત્મક રીતે તેમને સાથની જરૂર છે અને આસપાસ સંતુલન હોય ત્યારે તેઓ સૌથી શાંત અનુભવે છે. કાયદો, રાજદ્વારી કામ, ડિઝાઇન, ફેશન, કલા, પરામર્શ અને વ્યાવસાયિક ભાગીદારી ઘણી વાર તેમને માફક આવે છે. તેમની વૃદ્ધિ નિર્ણાયકતામાં છે — પોતાના નિર્ણય પર ભરોસો કરવો અને સ્વીકારવું કે થોડો મતભેદ સ્વસ્થ હોઈ શકે.",
    # EN: Vrishchik (Scorpio) is a fixed water sign ruled by Mars. People with the Moon in Vrishchik
    #     are often intense, perceptive, determined and deeply loyal, with feelings that run far
    #     below the surface. They are not satisfied with appearances and want to understand what is
    #     really going on. Once they commit — to a person, a cause or a goal — they rarely let go.
    #     Research, investigation, medicine, psychology, finance and crisis work often suit them.
    #     Their growth lies in trust and forgiveness: letting others in, and allowing old feelings
    #     to transform rather than be held.
    "vrishchik": "વૃશ્ચિક સ્થિર જળ રાશિ છે, મંગળની સ્વામિત્વવાળી. ચંદ્ર વૃશ્ચિકમાં હોય તેવા લોકો ઘણી વાર તીવ્ર, સૂક્ષ્મદર્શી, દૃઢ નિશ્ચયી અને ઊંડા વફાદાર હોય છે, સપાટીની ઘણી નીચે વહેતી લાગણીઓ સાથે. તેઓ દેખાવથી સંતોષ પામતા નથી અને ખરેખર શું ચાલી રહ્યું છે તે સમજવા માગે છે. એક વાર તેઓ કોઈ વ્યક્તિ, ધ્યેય કે હેતુ સાથે જોડાય પછી ભાગ્યે જ છોડે છે. સંશોધન, તપાસ, તબીબી ક્ષેત્ર, મનોવિજ્ઞાન, નાણાં અને કટોકટીનું કામ ઘણી વાર તેમને માફક આવે છે. તેમની વૃદ્ધિ વિશ્વાસ અને ક્ષમામાં છે: બીજાને અંદર આવવા દેવા, અને જૂની લાગણીઓને પકડી રાખવાને બદલે રૂપાંતરિત થવા દેવી.",
    # EN: Dhanu (Sagittarius) is a dual fire sign ruled by Jupiter, symbolised by the archer. People
    #     with the Moon in Dhanu are often optimistic, honest, generous and philosophical, with a
    #     love of learning, travel and freedom. They look for meaning in life and enjoy sharing what
    #     they have learned. Emotionally they are open and cheerful, and they need room to grow.
    #     Teaching, law, religion and philosophy, publishing, travel and sport often suit them.
    #     Their growth lies in following through — giving the same attention to the details of daily
    #     life that they give to big ideas and distant horizons.
    "dhanu": "ધનુ દ્વિસ્વભાવ અગ્નિ રાશિ છે, ગુરુની સ્વામિત્વવાળી, જેનું પ્રતીક ધનુર્ધારી છે. ચંદ્ર ધનુમાં હોય તેવા લોકો ઘણી વાર આશાવાદી, પ્રામાણિક, ઉદાર અને તત્ત્વચિંતક હોય છે, અભ્યાસ, પ્રવાસ અને સ્વતંત્રતાના પ્રેમી. તેઓ જીવનનો અર્થ શોધે છે અને જે શીખ્યા તે વહેંચવાનું ગમે છે. ભાવનાત્મક રીતે તેઓ ખુલ્લા અને પ્રફુલ્લિત છે, અને તેમને વિકસવા માટે જગ્યા જોઈએ. શિક્ષણ, કાયદો, ધર્મ અને તત્ત્વજ્ઞાન, પ્રકાશન, પ્રવાસ અને રમતગમત ઘણી વાર તેમને માફક આવે છે. તેમની વૃદ્ધિ પૂરું કરવામાં છે — મોટા વિચારો અને દૂરના ક્ષિતિજોને જેટલું ધ્યાન આપે છે તેટલું જ રોજિંદા જીવનની ઝીણવટને આપવું.",
    # EN: Makar (Capricorn) is a movable earth sign ruled by Saturn. People with the Moon in Makar
    #     are often responsible, disciplined, practical and ambitious in a patient, long-term way.
    #     They take duty seriously, work steadily and earn respect over time. Emotionally they can
    #     seem reserved, but they show love through reliability and quiet support. Administration,
    #     management, engineering, government service, finance and any field that rewards
    #     perseverance often suit them. Their growth lies in warmth and rest — allowing themselves
    #     joy along the way, and remembering that their worth is not measured only by achievement.
    "makar": "મકર ચર પૃથ્વી રાશિ છે, શનિની સ્વામિત્વવાળી. ચંદ્ર મકરમાં હોય તેવા લોકો ઘણી વાર જવાબદાર, શિસ્તબદ્ધ, વ્યવહારુ અને ધીરજવાળી, લાંબા ગાળાની રીતે મહત્વાકાંક્ષી હોય છે. તેઓ ફરજને ગંભીરતાથી લે છે, સ્થિરતાથી કામ કરે છે અને સમય જતાં આદર મેળવે છે. ભાવનાત્મક રીતે તેઓ અંતર્મુખ લાગી શકે, પણ ભરોસાપાત્રતા અને શાંત ટેકા દ્વારા પ્રેમ બતાવે છે. વહીવટ, વ્યવસ્થાપન, ઇજનેરી, સરકારી સેવા, નાણાં અને દૃઢતાને ઇનામ આપતું કોઈ પણ ક્ષેત્ર ઘણી વાર તેમને માફક આવે છે. તેમની વૃદ્ધિ હૂંફ અને આરામમાં છે — રસ્તામાં પોતાને આનંદ માણવા દેવો, અને યાદ રાખવું કે તેમની કિંમત માત્ર સિદ્ધિથી મપાતી નથી.",
    # EN: Kumbh (Aquarius) is a fixed air sign ruled by Saturn, symbolised by the water-bearer who
    #     pours knowledge out for all. People with the Moon in Kumbh are often independent,
    #     humanitarian, inventive and loyal to friends and ideals. They think about the wider
    #     community and enjoy new ideas, science and reform. Emotionally they value friendship and
    #     freedom, and they show care through principle and action. Science, technology, social
    #     work, research, education and community organisations often suit them. Their growth lies
    #     in closeness — letting their warmth show to individuals as well as to humanity as a whole.
    "kumbh": "કુંભ સ્થિર વાયુ રાશિ છે, શનિની સ્વામિત્વવાળી, જેનું પ્રતીક જળવાહક છે જે બધા માટે જ્ઞાન રેડે છે. ચંદ્ર કુંભમાં હોય તેવા લોકો ઘણી વાર સ્વતંત્ર, માનવતાવાદી, સંશોધનશીલ અને મિત્રો તથા આદર્શો પ્રત્યે વફાદાર હોય છે. તેઓ વ્યાપક સમુદાય વિશે વિચારે છે અને નવા વિચારો, વિજ્ઞાન અને સુધારાનો આનંદ લે છે. ભાવનાત્મક રીતે તેઓ મિત્રતા અને સ્વતંત્રતાને મહત્વ આપે છે, અને સિદ્ધાંત તથા કર્મ દ્વારા કાળજી બતાવે છે. વિજ્ઞાન, ટેકનોલોજી, સમાજસેવા, સંશોધન, શિક્ષણ અને સામુદાયિક સંસ્થાઓ ઘણી વાર તેમને માફક આવે છે. તેમની વૃદ્ધિ નિકટતામાં છે — પોતાની હૂંફ સમગ્ર માનવજાતને જ નહીં, પણ વ્યક્તિઓને પણ બતાવવી.",
    # EN: Meen (Pisces) is a dual water sign ruled by Jupiter, the last of the twelve rashis. People
    #     with the Moon in Meen are often compassionate, imaginative, gentle and spiritually
    #     inclined, with a deep sensitivity to the feelings of others. They forgive easily, help
    #     without being asked and are moved by music, art and devotion. Emotionally they are open-
    #     hearted and intuitive. Healing, counselling, the arts, music, charity, teaching and
    #     spiritual work often suit them. Their growth lies in healthy boundaries — caring for
    #     others without losing themselves, and turning their rich imagination into practical
    #     action.
    "meen": "મીન દ્વિસ્વભાવ જળ રાશિ છે, ગુરુની સ્વામિત્વવાળી, બાર રાશિઓમાં છેલ્લી. ચંદ્ર મીનમાં હોય તેવા લોકો ઘણી વાર કરુણાળુ, કલ્પનાશીલ, નમ્ર અને આધ્યાત્મિક ઝુકાવવાળા હોય છે, બીજાની લાગણીઓ પ્રત્યે ઊંડી સંવેદનશીલતા સાથે. તેઓ સહેલાઈથી માફ કરે છે, કહ્યા વગર મદદ કરે છે અને સંગીત, કલા અને ભક્તિથી ભાવવિભોર થાય છે. ભાવનાત્મક રીતે તેઓ ખુલ્લા દિલના અને સહજબુદ્ધિવાળા છે. ઉપચાર, પરામર્શ, કલા, સંગીત, દાન, શિક્ષણ અને આધ્યાત્મિક કાર્ય ઘણી વાર તેમને માફક આવે છે. તેમની વૃદ્ધિ સ્વસ્થ સીમાઓમાં છે — પોતાને ગુમાવ્યા વગર બીજાની કાળજી લેવી, અને સમૃદ્ધ કલ્પનાને વ્યવહારુ કર્મમાં ફેરવવી.",
}

# app/nakshatra_text.py FACTS["gu"] — deity.<slug> and symbol.<slug> of each nakshatra  [54]
NAKSHATRA_FACTS = {
    # EN: The Ashwini Kumaras, the divine physicians
    "deity.ashwini": "અશ્વિની કુમારો, દૈવી વૈદ્યો",
    # EN: A horse's head
    "symbol.ashwini": "ઘોડાનું માથું",
    # EN: Yama, lord of dharma
    "deity.bharani": "યમ, ધર્મના સ્વામી",
    # EN: The yoni (womb)
    "symbol.bharani": "યોનિ (ગર્ભ)",
    # EN: Agni, the fire
    "deity.krittika": "અગ્નિ",
    # EN: A razor or flame
    "symbol.krittika": "અસ્ત્રો કે જ્યોત",
    # EN: Brahma (Prajapati)
    "deity.rohini": "બ્રહ્મા (પ્રજાપતિ)",
    # EN: A chariot or ox-cart
    "symbol.rohini": "રથ કે બળદગાડું",
    # EN: Soma, the Moon
    "deity.mrigashira": "સોમ, ચંદ્ર",
    # EN: A deer's head
    "symbol.mrigashira": "હરણનું માથું",
    # EN: Rudra
    "deity.ardra": "રુદ્ર",
    # EN: A teardrop or diamond
    "symbol.ardra": "આંસુનું ટીપું કે હીરો",
    # EN: Aditi, mother of the gods
    "deity.punarvasu": "અદિતિ, દેવોની માતા",
    # EN: A bow and quiver
    "symbol.punarvasu": "ધનુષ્ય અને ભાથું",
    # EN: Brihaspati, guru of the gods
    "deity.pushya": "બૃહસ્પતિ, દેવોના ગુરુ",
    # EN: A cow's udder or lotus
    "symbol.pushya": "ગાયનું આંચળ કે કમળ",
    # EN: The Nagas (serpent deities)
    "deity.ashlesha": "નાગ (સર્પ દેવતાઓ)",
    # EN: A coiled serpent
    "symbol.ashlesha": "કુંડળી વાળેલો સર્પ",
    # EN: The Pitris (ancestors)
    "deity.magha": "પિતૃઓ (પૂર્વજો)",
    # EN: A royal throne
    "symbol.magha": "રાજ સિંહાસન",
    # EN: Bhaga, giver of fortune
    "deity.purva-phalguni": "ભગ, ભાગ્યદાતા",
    # EN: The front legs of a bed
    "symbol.purva-phalguni": "પલંગના આગલા પાયા",
    # EN: Aryaman, lord of friendship
    "deity.uttara-phalguni": "અર્યમા, મિત્રતાના સ્વામી",
    # EN: The back legs of a bed
    "symbol.uttara-phalguni": "પલંગના પાછલા પાયા",
    # EN: Savitr, the Sun
    "deity.hasta": "સવિતા, સૂર્ય",
    # EN: A hand
    "symbol.hasta": "હાથ",
    # EN: Tvashtr (Vishwakarma), the divine architect
    "deity.chitra": "ત્વષ્ટા (વિશ્વકર્મા), દૈવી શિલ્પી",
    # EN: A bright jewel
    "symbol.chitra": "ઝળહળતું રત્ન",
    # EN: Vayu, the wind
    "deity.swati": "વાયુ, પવન",
    # EN: A young shoot swaying in the wind
    "symbol.swati": "પવનમાં ઝૂલતો કૂણો અંકુર",
    # EN: Indra and Agni (Indragni)
    "deity.vishakha": "ઇન્દ્ર અને અગ્નિ (ઇન્દ્રાગ્ની)",
    # EN: A triumphal arch
    "symbol.vishakha": "વિજય તોરણ",
    # EN: Mitra, lord of friendship
    "deity.anuradha": "મિત્ર, મૈત્રીના સ્વામી",
    # EN: A lotus
    "symbol.anuradha": "કમળ",
    # EN: Indra, king of the gods
    "deity.jyeshtha": "ઇન્દ્ર, દેવોના રાજા",
    # EN: A circular amulet or earring
    "symbol.jyeshtha": "ગોળ તાવીજ કે કર્ણફૂલ",
    # EN: Nirriti
    "deity.mula": "નિર્ઋતિ",
    # EN: A bunch of roots
    "symbol.mula": "મૂળિયાંનો ગુચ્છો",
    # EN: Apas, the waters
    "deity.purva-ashadha": "અપ્, જળ",
    # EN: A winnowing fan or elephant tusk
    "symbol.purva-ashadha": "સૂપડું કે હાથીદાંત",
    # EN: The Vishvedevas (universal gods)
    "deity.uttara-ashadha": "વિશ્વેદેવો (સર્વ દેવો)",
    # EN: An elephant tusk
    "symbol.uttara-ashadha": "હાથીદાંત",
    # EN: Vishnu
    "deity.shravana": "વિષ્ણુ",
    # EN: An ear, or three footprints
    "symbol.shravana": "કાન, અથવા ત્રણ પગલાં",
    # EN: The eight Vasus
    "deity.dhanishta": "આઠ વસુઓ",
    # EN: A drum (mridanga)
    "symbol.dhanishta": "ઢોલ (મૃદંગ)",
    # EN: Varuna, lord of the waters
    "deity.shatabhisha": "વરુણ, જળના સ્વામી",
    # EN: An empty circle
    "symbol.shatabhisha": "ખાલી વર્તુળ",
    # EN: Aja Ekapada
    "deity.purva-bhadrapada": "અજ એકપાદ",
    # EN: Swords, or the front legs of a cot
    "symbol.purva-bhadrapada": "તલવારો, અથવા ખાટલાના આગલા પાયા",
    # EN: Ahir Budhnya, serpent of the deep
    "deity.uttara-bhadrapada": "અહિર્બુધ્ન્ય, ઊંડાણનો સર્પ",
    # EN: The back legs of a cot, or twins
    "symbol.uttara-bhadrapada": "ખાટલાના પાછલા પાયા, અથવા જોડિયાં",
    # EN: Pushan, the nourisher and guide
    "deity.revati": "પૂષણ, પોષક અને માર્ગદર્શક",
    # EN: A fish (or a drum)
    "symbol.revati": "માછલી (અથવા ઢોલ)",
}

# app/naam_milan_text.py TEXT["gu"] — page text of /naam-se-kundali-milan  [34]
NAAM_MILAN_TEXT = {
    # EN: Naam se Kundali Milan — Match 36 Gunas by Name, Free | {brand}
    # keep: {brand}
    "title": "નામ પરથી કુંડળી મિલન — નામથી 36 ગુણ મેળવો, મફત | {brand}",
    # EN: Kundali milan by name: the first syllable of the boy's and girl's names gives each
    #     nakshatra and rashi, then the full 36-guna Ashtakoot match. Type names in Hindi or English
    #     — free, no sign-up.
    "desc": "નામ પરથી કુંડળી મિલન: વર અને કન્યાના નામનો પહેલો અક્ષર દરેકનું નક્ષત્ર અને રાશિ આપે છે, પછી પૂરું 36 ગુણનું અષ્ટકૂટ મિલન. નામ હિન્દી (દેવનાગરી) કે અંગ્રેજીમાં લખો — મફત, સાઇન-અપ વગર.",
    # EN: Naam se Kundali Milan
    "crumb": "નામ પરથી કુંડળી મિલન",
    # EN: <h1>Naam se Kundali Milan — Match by Name</h1>
    "h1": "<h1>નામ પરથી કુંડળી મિલન — નામથી મેળાપક</h1>",
    # EN: <p class="hi" lang="hi">नाम से कुंडली मिलान</p>
    "sub": "<p class=\"hi\">નામના પહેલા અક્ષરથી 36 ગુણ મિલન</p>",
    # EN: <p>When birth times are not known, tradition matches a couple by the <strong>first
    #     syllable of their names</strong>. Type both names in Hindi or English: we show the
    #     syllable used, its nakshatra pada and rashi, and the full 36-guna match.</p>
    "intro": "<p>જન્મનો સમય ખબર ન હોય ત્યારે પરંપરા દંપતીનું મિલન <strong>નામના પહેલા અક્ષર</strong> પરથી કરે છે. બંનેનાં નામ હિન્દી (દેવનાગરી) કે અંગ્રેજીમાં લખો: અમે વપરાયેલો અક્ષર, તેનું નક્ષત્ર ચરણ અને રાશિ, તથા પૂરું 36 ગુણનું મિલન બતાવીએ છીએ.</p>",
    # EN: Open birth-chart Kundali Milan
    "open_milan": "જન્મકુંડળી પરથી કુંડળી મિલન ખોલો",
    # EN: Automatic, from the name
    "auto": "આપોઆપ, નામ પરથી",
    # EN: Other likely syllables for this name
    "alt_head": "આ નામ માટે શક્ય બીજા અક્ષરો",
    # EN: All 108 syllables
    "all_head": "બધા 108 અક્ષર",
    # EN: Boy's name (groom)
    "boy_label": "છોકરાનું નામ (વર)",
    # EN: Girl's name (bride)
    "girl_label": "છોકરીનું નામ (કન્યા)",
    # EN: e.g. Ram or राम
    "boy_ph": "દા.ત. Ram",
    # EN: e.g. Sita or सीता
    "girl_ph": "દા.ત. Sita",
    # EN: Change the first syllable
    "pick": "પહેલો અક્ષર બદલો",
    # EN: Match the gunas
    "button": "ગુણ મેળવો",
    # EN: This syllable belongs to Abhijit, the 28th nakshatra; in the 27-nakshatra wheel it is
    #     counted in Uttara Ashadha pada 4.
    "via.abhijit": "આ અક્ષર 28મા નક્ષત્ર અભિજિતનો છે; 27 નક્ષત્રના ચક્રમાં તેની ગણતરી ઉત્તરાષાઢાના ચોથા ચરણમાં થાય છે.",
    # EN: By the traditional rule, ब is read as व, and श as ष (with the a-vowel) or स.
    "via.alias": "પરંપરાના નિયમ મુજબ બ ને વ, અને શ ને ષ (અ-સ્વર સાથે) અથવા સ ગણવામાં આવે છે.",
    # EN: This exact syllable is not in the 108-syllable list, so the nearest syllable with the same
    #     consonant was used — change it below if you prefer.
    "via.nearest": "આ ચોક્કસ અક્ષર 108 અક્ષરની યાદીમાં નથી, તેથી એ જ વ્યંજનવાળો સૌથી નજીકનો અક્ષર લેવાયો છે — ઇચ્છો તો નીચેથી બદલો.",
    # EN: An English spelling cannot settle this syllable (e.g. T = त or ट), so the most common
    #     reading was used — pick another below if needed.
    "via.latin": "અંગ્રેજી જોડણીથી આ અક્ષર નક્કી થઈ શકતો નથી (દા.ત. T = ત કે ટ), તેથી સૌથી સામાન્ય ઉચ્ચાર લેવાયો છે — જરૂર હોય તો નીચેથી બીજો પસંદ કરો.",
    # EN: You chose this syllable.
    "via.chosen": "તમે આ અક્ષર પસંદ કર્યો છે.",
    # EN: Could not read a first syllable from this name — pick one from the list below.
    "unreadable": "આ નામમાંથી પહેલો અક્ષર વાંચી શકાયો નથી — નીચેની યાદીમાંથી એક પસંદ કરો.",
    # EN: pada
    "pada": "ચરણ",
    # EN: Result
    "result": "પરિણામ",
    # EN: <tr><th></th><th>First syllable</th><th>Nakshatra</th><th>Rashi</th></tr>
    "res.head": "<tr><th></th><th>પહેલો અક્ષર</th><th>નક્ષત્ર</th><th>રાશિ</th></tr>",
    # EN: Boy
    "boy": "વર",
    # EN: Girl
    "girl": "કન્યા",
    # EN: <tr><th>Koota</th><th>Points</th><th>Why</th></tr>
    "res.th": "<tr><th>કૂટ</th><th>ગુણ</th><th>કારણ</th></tr>",
    # EN: Total
    "total": "કુલ",
    # EN: <strong>Mangal dosha: not applicable.</strong> Mangal dosha depends on where Mars stood
    #     from the Lagna, Moon and Venus at birth — a name cannot tell you that. Use birth-chart
    #     matching for it.
    "mangal": "<strong>મંગળ દોષ: લાગુ પડતો નથી.</strong> મંગળ દોષ જન્મ સમયે લગ્ન, ચંદ્ર અને શુક્રથી મંગળ ક્યાં હતો તેના પર આધાર રાખે છે — નામ પરથી તે જાણી શકાતું નથી. તે માટે જન્મકુંડળી પરથી મિલન કરો.",
    # EN: Match by birth details instead — more accurate, free
    "res.cta": "તેને બદલે જન્મની વિગતો પરથી મિલન કરો — વધુ ચોક્કસ, મફત",
    # EN: <div class="box"><p><strong>Please note:</strong> name-based matching is a traditional
    #     shortcut, used when birth details are not known. It assumes each name was chosen from the
    #     syllable of the person's birth nakshatra — which today is often not the case. Matching
    #     from the date, time and place of birth is far more accurate, and is the only way to check
    #     Mangal dosha.</p></div>
    "caveat": "<div class=\"box\"><p><strong>ધ્યાન રાખો:</strong> નામ પરથી મિલન એક પરંપરાગત ટૂંકો રસ્તો છે, જે જન્મની વિગતો ખબર ન હોય ત્યારે વપરાય છે. તે માની લે છે કે દરેક નામ તે વ્યક્તિના જન્મ નક્ષત્રના અક્ષર પરથી પાડ્યું છે — જે આજે ઘણી વાર હોતું નથી. જન્મની તારીખ, સમય અને સ્થળ પરથી મિલન ઘણું વધારે ચોક્કસ છે, અને મંગળ દોષ તપાસવાનો એ જ એકમાત્ર રસ્તો છે.</p></div>",
    # EN: <tr><th>Rashi</th><th>Name syllables</th></tr>
    "syl.head": "<tr><th>રાશિ</th><th>નામના અક્ષર</th></tr>",
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
    "explainer": "\n<h2>નામ પરથી મિલન કેવી રીતે થાય છે</h2> <p>27 નક્ષત્રમાંથી દરેકને ચાર ચરણ છે, અને દરેક ચરણનો એક અક્ષર (નામાક્ષર) છે — કુલ 108. જે ચરણના અક્ષરથી નામ <strong>શરૂ થાય</strong> તે ચરણ તે વ્યક્તિનું નક્ષત્ર ગણાય છે, અને તેની રાશિ તેની ચંદ્ર રાશિ. પછી જન્મકુંડળી સાથે વપરાતું એ જ <strong>અષ્ટકૂટ (36 ગુણ)</strong> મિલન — વર્ણ, વશ્ય, તારા, યોનિ, ગ્રહમૈત્રી, ગણ, ભકૂટ અને નાડી — આ બે નક્ષત્ર પરથી ગણાય છે, અમારા કુંડળી મિલન સાધન પાછળના એ જ એન્જિન વડે.</p> <h3>પહેલો અક્ષર કેવી રીતે વંચાય છે</h3> <ul> <li>પહેલા અક્ષરનો પહેલો વ્યંજન અને તેનો સ્વર: <strong>પ્રિયા → પી</strong>, <strong>ક્ષિતિજ → કી</strong>. હ્રસ્વ અને દીર્ઘ સ્વર સરખા ગણાય છે (ઇ/ઈ, ઉ/ઊ); ઐ ને એ અને ઔ ને ઓ ગણાય છે.</li> <li>બ ને વ, અને શ ને ષ (અ-સ્વર સાથે) અથવા સ વાંચવામાં આવે છે; ઋ ને રી.</li> <li>અભિજિતના અક્ષરો ({abhijit}) ઉત્તરાષાઢાના ચોથા ચરણમાં ગણાય છે.</li> <li>અંગ્રેજીમાં લખેલાં નામોનું લિપ્યંતર થાય છે; T, D, N, Th અને Dh જેવા અક્ષરો બે હિન્દી અક્ષર (ત/ટ, દ/ડ) માટે હોઈ શકે, તેથી પરિણામ બતાવે છે કે કયો અક્ષર વપરાયો અને બીજો પસંદ કરવા દે છે. હિન્દી (દેવનાગરી) લખાણ બરાબર વંચાય છે.</li> </ul> <h3>રાશિ પ્રમાણે નામના અક્ષર</h3> {syllables} <p>દરેક નક્ષત્રના અક્ષર, દેવતા, ગણ અને નાડી માટે <a href=\"{href}\">બધાં 27 નક્ષત્ર</a> જુઓ.</p>",
}

# app/naam_milan_text.py ENGINE["gu"] — score-band notes and the convention note of a naam-milan result  [5]
NAAM_MILAN_ENGINE = {
    # EN: Below the traditional minimum of 18 gunas.
    "band_note0": "18 ગુણના પરંપરાગત લઘુતમથી ઓછા.",
    # EN: In the traditional 18-24 gunas band.
    "band_note1": "18-24 ગુણની પરંપરાગત શ્રેણીમાં.",
    # EN: In the traditional 25-32 gunas band.
    "band_note2": "25-32 ગુણની પરંપરાગત શ્રેણીમાં.",
    # EN: In the traditional 33-36 gunas band.
    "band_note3": "33-36 ગુણની પરંપરાગત શ્રેણીમાં.",
    # EN: The 18/25/33 guna thresholds are a widely used convention, not a measurement. Astrologers
    #     often accept a lower total if the heavily weighted kootas are free of dosha.
    "convention_note": "18/25/33 ગુણની સીમાઓ વ્યાપક રીતે વપરાતી પ્રથા છે, માપ નથી. વધુ વજનવાળા કૂટ દોષ વિનાના હોય તો જ્યોતિષીઓ ઘણી વાર ઓછો કુલ સ્કોર પણ સ્વીકારે છે.",
}

# ----------------------------------------------------------------------------
# muhurat   /muhurat/<kind>-<year>
# ----------------------------------------------------------------------------

# app/muhurat_text.py TEXT["gu"] — page text of /muhurat/<kind>-<year> (the mundan-only keys are MUHURAT_MUNDAN)  [37]
MUHURAT_TEXT = {
    # EN: Vivah Muhurat
    "kind.vivah": "વિવાહ મુહૂર્ત",
    # EN: Griha Pravesh Muhurat
    "kind.griha-pravesh": "ગૃહપ્રવેશ મુહૂર્ત",
    # EN: wedding
    "noun.vivah": "લગ્ન",
    # EN: house-warming
    "noun.griha-pravesh": "ગૃહપ્રવેશ",
    # EN: {name} {year}: Auspicious {noun_title} Dates (New Delhi) | {brand}
    # keep: {brand} {year}
    # may also use: {name} {noun_title} {noun}
    "title": "{name} {year}: શુભ {noun}ની તારીખો (નવી દિલ્હી) | {brand}",
    # EN: {name} {year}: auspicious {noun} dates
    # keep: {year}
    # may also use: {name} {noun}
    "h1": "{name} {year}: શુભ {noun}ની તારીખો",
    # EN: {name} {year} for New Delhi — month-by-month auspicious {noun} dates with tithi and
    #     nakshatra. {count} dates; Chaturmas, Kharmas, Adhik Maas, Pitru Paksha and Guru/Shukra
    #     asta explained.
    # keep: {count} {year}
    # may also use: {name} {noun}
    "desc": "{name} {year} નવી દિલ્હી માટે — તિથિ અને નક્ષત્ર સાથે મહિના પ્રમાણે શુભ {noun}ની તારીખો. {count} તારીખો; ચાતુર્માસ, ખરમાસ, અધિક માસ, પિતૃ પક્ષ અને ગુરુ/શુક્ર અસ્તની સમજૂતી.",
    # EN: <p class="hi" lang="hi">{name_hi} {year}</p>
    # keep: {year}
    # may also use: {name} {noun}
    "sub": "<p class=\"hi\">{name} {year}</p>",
    # EN: {label} · IST
    # keep: {label}
    "place": "{label} · IST",
    # EN: <p>By the panchang there are <strong>{count}</strong> {name_lower} dates in {year} for New
    #     Delhi, in {months}. Each date passes the classical checks on the sunrise tithi, nakshatra,
    #     weekday, yoga and Bhadra, and falls outside Chaturmas, Kharmas, Adhik Maas, Pitru Paksha
    #     and the combustion (asta) of Jupiter and Venus.</p>
    # keep: {count} {months} {year}
    # may also use: {name_lower} {name} {noun}
    "intro": "<p>પંચાંગ મુજબ {year}માં નવી દિલ્હી માટે {months}માં {name}ની <strong>{count}</strong> તારીખો છે. દરેક તારીખ સૂર્યોદયની તિથિ, નક્ષત્ર, વાર, યોગ અને ભદ્રાની શાસ્ત્રીય તપાસમાંથી પસાર થાય છે, અને ચાતુર્માસ, ખરમાસ, અધિક માસ, પિતૃ પક્ષ તથા ગુરુ અને શુક્રના અસ્ત બહાર આવે છે.</p>",
    # EN: <p><strong>Timings vary by city.</strong> These dates are reckoned from New Delhi's
    #     sunrise; elsewhere a tithi or nakshatra can change on a different day. The exact muhurat
    #     (lagna) for a wedding or griha pravesh should be fixed by your family priest. Check your
    #     own city in the Muhurat Finder.</p>
    "note": "<p><strong>સમય શહેર પ્રમાણે બદલાય છે.</strong> આ તારીખો નવી દિલ્હીના સૂર્યોદય પરથી ગણેલી છે; બીજે ક્યાંક તિથિ કે નક્ષત્ર બીજા દિવસે બદલાઈ શકે છે. લગ્ન કે ગૃહપ્રવેશનું ચોક્કસ મુહૂર્ત (લગ્ન) તમારા કુટુંબના પુરોહિતે નક્કી કરવું જોઈએ. મુહૂર્ત શોધકમાં તમારું પોતાનું શહેર તપાસો.</p>",
    # EN: Find muhurat for your city — free
    "cta": "તમારા શહેરનું મુહૂર્ત શોધો — મફત",
    # EN: {name} {year}
    # keep: {name} {year}
    "crumb": "{name} {year}",
    # EN: More muhurat dates
    "more": "વધુ મુહૂર્ત તારીખો",
    # EN: {name} {year}
    # keep: {name} {year}
    "link.kind": "{name} {year}",
    # EN: Today's Panchang
    "link.panchang": "આજનું પંચાંગ",
    # EN: Kundali Milan
    "link.milan": "કુંડળી મિલન",
    # EN: When there is no {name_lower} in {year}
    # keep: {year}
    # may also use: {name_lower} {name} {noun}
    "periods.h2": "{year}માં {noun} ન હોય તેવો સમય",
    # EN: No {name_lower} is given during these periods. The dates are computed from the panchang
    #     (New Delhi, sunrise):
    # may also use: {name_lower} {name} {noun}
    "periods.intro": "આ સમયગાળામાં {noun} અપાતું નથી. તારીખો પંચાંગ (નવી દિલ્હી, સૂર્યોદય) પરથી ગણેલી છે:",
    # EN: <li><strong>{period}</strong>, {range} — {about}.</li>
    # keep: {about} {period} {range}
    "periods.item": "<li><strong>{period}</strong>, {range} — {about}.</li>",
    # EN: No {name_lower} in {month} — {periods}.
    # keep: {month} {periods}
    # may also use: {name_lower} {name} {noun}
    "none.periods": "{month}માં {noun} નથી — {periods}.",
    # EN: No {name_lower} in {month} — no day this month passes the tithi, nakshatra, weekday and
    #     yoga checks.
    # keep: {month}
    # may also use: {name_lower} {name} {noun}
    "none.plain": "{month}માં {noun} નથી — આ મહિનામાં કોઈ દિવસ તિથિ, નક્ષત્ર, વાર અને યોગની તપાસમાં પાસ થતો નથી.",
    # EN: <tr><th>Date</th><th>Day</th><th>Tithi</th><th>Nakshatra</th></tr>
    "th": "<tr><th>તારીખ</th><th>વાર</th><th>તિથિ</th><th>નક્ષત્ર</th></tr>",
    # EN: Muhurat page not found
    "nf.title": "મુહૂર્ત પેજ મળ્યું નથી",
    # EN: Open the Muhurat Finder
    "nf.open": "મુહૂર્ત શોધક ખોલો",
    # EN: Chaturmas
    "period.chaturmas": "ચાતુર્માસ",
    # EN: Devshayani Ekadashi to Devuthani Ekadashi, when Lord Vishnu is in yoga-nidra
    "period_about.chaturmas": "દેવશયની એકાદશીથી દેવઊઠી એકાદશી સુધી, જ્યારે ભગવાન વિષ્ણુ યોગનિદ્રામાં હોય છે",
    # EN: Kharmas
    "period.kharmas": "ખરમાસ (કમૂરતાં)",
    # EN: the Sun in Dhanu (Sagittarius) or Meena (Pisces)
    "period_about.kharmas": "સૂર્ય ધનુ કે મીન રાશિમાં હોય તે સમય",
    # EN: Adhik Maas
    "period.adhik_maas": "અધિક માસ",
    # EN: an intercalary lunar month with no solar ingress
    "period_about.adhik_maas": "સૂર્યની સંક્રાંતિ વિનાનો વધારાનો ચાંદ્ર માસ",
    # EN: Pitru Paksha
    "period.pitru_paksha": "પિતૃ પક્ષ",
    # EN: Bhadrapada Purnima to Sarva Pitru Amavasya, the fortnight of shraddha
    "period_about.pitru_paksha": "ભાદરવા પૂનમથી સર્વપિતૃ અમાસ સુધી, શ્રાદ્ધનું પખવાડિયું",
    # EN: Shukra Asta
    "period.shukra_asta": "શુક્ર અસ્ત",
    # EN: Venus combust (too close to the Sun to be seen), with 3 days either side
    "period_about.shukra_asta": "શુક્ર અસ્ત (સૂર્યની એટલો નજીક કે દેખાતો નથી), બંને બાજુ 3 દિવસ સાથે",
    # EN: Guru Asta
    "period.guru_asta": "ગુરુ અસ્ત",
    # EN: Jupiter combust (too close to the Sun to be seen), with 3 days either side
    "period_about.guru_asta": "ગુરુ અસ્ત (સૂર્યની એટલો નજીક કે દેખાતો નથી), બંને બાજુ 3 દિવસ સાથે",
}

# app/muhurat_text.py MUNDAN["gu"] — the mundan (first haircut) muhurat's own wording  [5]
MUHURAT_MUNDAN = {
    # EN: Mundan Muhurat
    "kind.mundan": "મુંડન મુહૂર્ત",
    # EN: mundan
    "noun.mundan": "મુંડન",
    # EN: <p><strong>Timings vary by city.</strong> These dates are reckoned from New Delhi's
    #     sunrise; elsewhere a tithi or nakshatra can change on a different day. The exact muhurat
    #     for the mundan (chudakarma) should be fixed by your family priest. Check your own city in
    #     the Muhurat Finder.</p>
    "note.mundan": "<p><strong>સમય શહેર પ્રમાણે બદલાય છે.</strong> આ તારીખો નવી દિલ્હીના સૂર્યોદય પરથી ગણેલી છે; બીજે ક્યાંક તિથિ કે નક્ષત્ર બીજા દિવસે બદલાઈ શકે છે. મુંડન (ચૂડાકર્મ)નું ચોક્કસ મુહૂર્ત તમારા કુટુંબના પુરોહિતે નક્કી કરવું જોઈએ. મુહૂર્ત શોધકમાં તમારું પોતાનું શહેર તપાસો.</p>",
    # EN: {name} {year}: the rules these dates follow
    # keep: {name} {year}
    "rules.h2": "{name} {year}: આ તારીખો જે નિયમોને અનુસરે છે",
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
    "rules.body": "<p>મુંડન (ચૂડાકર્મ, પહેલા વાળ ઉતારવા)ની તપાસ લગ્નથી અલગ, પોતાના નિયમોથી થાય છે. નીચેની વર્જિત બાબતોમાંથી કોઈ ન લાગુ પડે અને દિવસ અનુકૂળ નક્ષત્રમાં આવે તો જ તે યાદીમાં આવે છે:</p><ul><li><strong>વર્જિત તિથિઓ:</strong> {tithi_bad}.</li><li><strong>શુભ તિથિઓ</strong> (બંને પક્ષમાં): {tithi_good}; બાકીની મધ્યમ છે.</li><li><strong>અનુકૂળ નક્ષત્રો</strong> (નીચેની દરેક તારીખ તેમાંના એકમાં આવે છે): {nak_good}.</li><li><strong>વર્જિત નક્ષત્રો:</strong> {nak_bad}.</li><li><strong>વર્જિત યોગ અને કરણ:</strong> {yoga_bad}, અને ભદ્રા (વિષ્ટિ).</li><li><strong>વાર:</strong> {vara_good} શુભ ગણાય છે; {vara_bad} દિવસને રદ કર્યા વગર તેની વિરુદ્ધમાં ગણાય છે, તેથી આવી થોડી તારીખો દેખાય છે - તમારું કુટુંબ તે વાર ટાળતું હોય તો તે છોડી દો.</li></ul>",
}

# app/muhurat_text.py MONTHS["gu"] — only if this page must spell the months differently from names_<code>.MONTHS; else leave ()  [12]
# (optional: may stay empty)
MUHURAT_MONTHS = ()   # or 12 month names, January first

# ----------------------------------------------------------------------------
# recurring /purnima-<year> /amavasya-<year> /pradosh-vrat-<year> ... (DIVASTRO-141)
# ----------------------------------------------------------------------------

# app/recurring_text.py TEXT["gu"] — page text of /purnima-<year>, /amavasya-<year>, /pradosh-vrat-<year> ... (the keys it shares with VRAT_TEXT are taken from there)  [60]
RECURRING_TEXT = {
    # EN: Full Moon Dates and Tithi Time
    "what.purnima": "પૂનમની તારીખો અને તિથિનો સમય",
    # EN: New Moon Dates and Tithi Time
    "what.amavasya": "અમાસની તારીખો અને તિથિનો સમય",
    # EN: All Dates and Pradosh Puja Time
    "what.pradosh": "બધી તારીખો અને પ્રદોષ પૂજાનો સમય",
    # EN: All Dates and Moonrise Time
    "what.sankashti": "બધી તારીખો અને ચંદ્રોદયનો સમય",
    # EN: All Dates and Nishita Puja Time
    "what.masik_shivratri": "બધી તારીખો અને નિશીથ પૂજાનો સમય",
    # EN: All Dates and Kala Bhairav Puja
    "what.kalashtami": "બધી તારીખો અને કાલ ભૈરવ પૂજા",
    # EN: {name} {year}: {what} (New Delhi)
    # keep: {name} {what} {year}
    "title": "{name} {year}: {what} (નવી દિલ્હી)",
    # EN: {name} {year}: {what}
    # keep: {name} {what} {year}
    "h1": "{name} {year}: {what}",
    # EN: All {count} {name} dates in {year} with weekday, Hindu month and tithi start and end for
    #     New Delhi. {about}{keytime}{next}
    # keep: {about} {count} {keytime} {name} {next} {year}
    "desc": "{year}ની {name}ની બધી {count} તારીખો, વાર, હિન્દુ માસ અને તિથિની શરૂઆત-અંત સાથે, નવી દિલ્હી માટે. {about}{keytime}{next}",
    # EN: Full-moon vrat days for Satyanarayan puja, bathing and charity.
    "desc.about.purnima": "સત્યનારાયણ પૂજા, સ્નાન અને દાન માટેના પૂનમ વ્રતના દિવસો.",
    # EN: New-moon days for shraddha and tarpan, with Somvati and Shani Amavasya.
    "desc.about.amavasya": "શ્રાદ્ધ અને તર્પણ માટેના અમાસના દિવસો, સોમવતી અને શનિ અમાસ સાથે.",
    # EN: Lord Shiva's twilight fast on Trayodashi, with the puja window.
    "desc.about.pradosh": "તેરસે ભગવાન શિવનું સંધ્યાકાળનું વ્રત, પૂજાના સમય સાથે.",
    # EN: Lord Ganesha's fast on Krishna Chaturthi, broken after moonrise.
    "desc.about.sankashti": "વદ ચોથે ભગવાન ગણેશનું વ્રત, ચંદ્રોદય પછી છોડાય છે.",
    # EN: The monthly night of Shiva on Krishna Chaturdashi, with the midnight puja.
    "desc.about.masik_shivratri": "વદ ચૌદશે શિવની માસિક રાત્રિ, મધ્યરાત્રિની પૂજા સાથે.",
    # EN: Kala Bhairava worship on Krishna Ashtami, every month.
    "desc.about.kalashtami": "દર મહિને વદ આઠમે કાલ ભૈરવની ઉપાસના.",
    # EN: Includes {label}.
    # keep: {label}
    "desc.key": " સાથે {label}.",
    # EN: Next: {date}.
    # keep: {date}
    "desc.next": " હવે પછી: {date}.",
    # EN: The next {name} is on <strong>{when}</strong> ({details}).
    # keep: {details} {name} {when}
    "ans.next": "આગામી {name} <strong>{when}</strong> ({details}) છે.",
    # EN: The first {name} of {year} is on <strong>{when}</strong> ({details}). All {count} dates
    #     for {year} are listed below.
    # keep: {count} {details} {name} {when} {year}
    "ans.first": "{year}ની પહેલી {name} <strong>{when}</strong> ({details}) છે. {year}ની બધી {count} તારીખો નીચે આપી છે.",
    # EN: All {count} {name} dates for {year} are listed below; the last was on
    #     <strong>{when}</strong>.
    # keep: {count} {name} {when} {year}
    "ans.past": "{year}ની {name}ની બધી {count} તારીખો નીચે આપી છે; છેલ્લી <strong>{when}</strong> હતી.",
    # EN: Dates for {year}: {link}.
    # keep: {link} {year}
    "ans.more": " {year}ની તારીખો: {link}.",
    # EN: {name} {year}: all dates
    # keep: {name} {year}
    "table.h2": "{name} {year}: બધી તારીખો",
    # EN: Date
    "th.date": "તારીખ",
    # EN: Hindu month
    "th.month": "હિન્દુ માસ",
    # EN: Tithi
    "th.tithi": "તિથિ",
    # EN: Adhik {month}
    # keep: {month}
    "adhika": "અધિક {month}",
    # EN: Also:
    "also": "આ પણ: ",
    # EN: <p class="note"><small>Months are amanta (a month ends on Amavasya, as in South and West
    #     India). North Indian purnimanta calendars name the dark fortnight one month
    #     later.</small></p>
    "months.note": "<p class=\"note\"><small>માસ અમાંત છે (માસ અમાસે પૂરો થાય છે, જેમ ગુજરાત સહિત દક્ષિણ અને પશ્ચિમ ભારતમાં). ઉત્તર ભારતનાં પૂર્ણિમાંત કેલેન્ડર વદ પક્ષને એક મહિનો પછીનું નામ આપે છે.</small></p>",
    # EN: Som Pradosh
    "variant.pradosh.0": "સોમ પ્રદોષ",
    # EN: Bhauma Pradosh
    "variant.pradosh.1": "ભૌમ પ્રદોષ",
    # EN: Shani Pradosh
    "variant.pradosh.5": "શનિ પ્રદોષ",
    # EN: Angarki Chaturthi
    "variant.sankashti.1": "અંગારકી ચોથ",
    # EN: Somvati Amavasya
    "variant.amavasya.0": "સોમવતી અમાસ",
    # EN: Shani Amavasya
    "variant.amavasya.5": "શનિ અમાસ",
    # EN: What {name} is and how it is observed
    # keep: {name}
    "about.h2": "{name} શું છે અને કેવી રીતે ઊજવાય છે",
    # EN: Panchang for your city
    "city.h2": "તમારા શહેરનું પંચાંગ",
    # EN: Related dates and calendars
    "related.h2": "સંબંધિત તારીખો અને કેલેન્ડર",
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
    "about.purnima": "<p>પૂનમ એ પૂર્ણિમાની તિથિ છે, શુક્લ પક્ષની છેલ્લી (15મી) તિથિ, જ્યારે ચંદ્ર સૂર્યની સામે હોય છે અને પૂરો ચમકે છે. ભક્તો ઉપવાસ રાખે છે, પરોઢિયે સ્નાન કરે છે (નદી કે તીર્થમાં જ્યાં શક્ય હોય), ભગવાન વિષ્ણુની પૂજા કરે છે - સત્યનારાયણ કથા સામાન્ય પૂનમની પૂજા છે - અને સાંજે ચંદ્રને અર્ઘ્ય આપે છે. આ દિવસે અન્ન, વસ્ત્ર કે ધનનું દાન અનેકગણું પુણ્ય આપે છે એમ કહેવાય છે.</p><p>કેટલીક પૂનમ પોતે જ તહેવાર છે: ગુરુ પૂનમ, શરદ પૂનમ, કારતક પૂનમ અને બુદ્ધ પૂનમ, અને હોલિકા દહન ફાગણની પૂનમે થાય છે.</p>",
    # EN: <p>Amavasya is the new-moon tithi, the 30th and last tithi of the dark fortnight (Krishna
    #     paksha), when the Moon is in conjunction with the Sun and cannot be seen. It is the day of
    #     the ancestors (pitru): families offer tarpan and shraddha, feed Brahmins and the poor,
    #     give in charity and bathe in holy water. Many people fast and avoid starting anything
    #     new.</p><p>An Amavasya on a Monday is called Somvati Amavasya and one on a Saturday Shani
    #     Amavasya, both given extra weight. The great Amavasyas are Mauni Amavasya, Sarva Pitru
    #     Amavasya (the end of Pitru Paksha) and the Amavasya of Diwali.</p>
    "about.amavasya": "<p>અમાસ એ અમાવસ્યાની તિથિ છે, વદ પક્ષની 30મી અને છેલ્લી તિથિ, જ્યારે ચંદ્ર સૂર્ય સાથે યુતિમાં હોય છે અને દેખાતો નથી. તે પિતૃઓનો દિવસ છે: કુટુંબો તર્પણ અને શ્રાદ્ધ કરે છે, બ્રાહ્મણો અને ગરીબોને જમાડે છે, દાન કરે છે અને પવિત્ર જળમાં સ્નાન કરે છે. ઘણા લોકો ઉપવાસ કરે છે અને કંઈ નવું શરૂ કરવાનું ટાળે છે.</p><p>સોમવારે આવતી અમાસ સોમવતી અમાસ અને શનિવારે આવતી શનિ અમાસ કહેવાય છે, બંનેને વિશેષ મહત્વ અપાય છે. મોટી અમાસો છે: મૌની અમાસ, સર્વપિતૃ અમાસ (પિતૃ પક્ષનો અંત) અને દિવાળીની અમાસ.</p>",
    # EN: <p>Pradosh Vrat is the fast of Lord Shiva kept on Trayodashi, the 13th tithi, of both
    #     fortnights - so twice a month. Pradosh kaal is the twilight window just after sunset, when
    #     Shiva is believed to be most pleased. Devotees fast through the day, bathe, and do Shiva
    #     puja in the Pradosh window: abhishek with water, milk and bilva (bel) leaves, a lamp and
    #     the Pradosh stotra or Shiva Chalisa. The fast is broken after the puja.</p><p>A Pradosh on
    #     Monday is Som Pradosh, on Tuesday Bhauma Pradosh and on Saturday Shani Pradosh; the
    #     Saturday one is considered especially powerful.</p>
    "about.pradosh": "<p>પ્રદોષ વ્રત એ ભગવાન શિવનું વ્રત છે જે બંને પક્ષની તેરસે, 13મી તિથિએ, રખાય છે - એટલે મહિને બે વાર. પ્રદોષ કાળ સૂર્યાસ્ત પછીનો તરત સંધ્યાનો સમય છે, જ્યારે શિવ સૌથી પ્રસન્ન મનાય છે. ભક્તો આખો દિવસ ઉપવાસ કરે છે, સ્નાન કરે છે અને પ્રદોષ કાળમાં શિવ પૂજા કરે છે: જળ, દૂધ અને બિલીપત્રથી અભિષેક, દીવો અને પ્રદોષ સ્તોત્ર કે શિવ ચાલીસા. પૂજા પછી ઉપવાસ છોડાય છે.</p><p>સોમવારનો પ્રદોષ સોમ પ્રદોષ, મંગળવારનો ભૌમ પ્રદોષ અને શનિવારનો શનિ પ્રદોષ છે; શનિવારનો ખાસ શક્તિશાળી ગણાય છે.</p>",
    # EN: <p>Sankashti Chaturthi (Sankat Hara Chaturthi) is the monthly fast of Lord Ganesha on
    #     Chaturthi, the 4th tithi, of the dark fortnight (Krishna paksha); "sankashti" means
    #     deliverance from trouble. Devotees fast through the day, worship Ganesha in the evening
    #     and break the fast only after seeing the Moon and offering it arghya, which is why
    #     moonrise is the key time on this page.</p><p>A Sankashti on a Tuesday is Angarki Sankashti
    #     Chaturthi, believed to be especially fruitful. The Sankashti of Magha (purnimanta) is kept
    #     in North India as Sakat Chauth.</p>
    "about.sankashti": "<p>સંકષ્ટી ચતુર્થી (સંકટ હર ચતુર્થી) એ ભગવાન ગણેશનું માસિક વ્રત છે જે વદ પક્ષની ચોથ, 4થી તિથિએ, રખાય છે; “સંકષ્ટી” એટલે મુશ્કેલીમાંથી મુક્તિ. ભક્તો આખો દિવસ ઉપવાસ કરે છે, સાંજે ગણેશની પૂજા કરે છે અને ચંદ્રના દર્શન કરીને અર્ઘ્ય આપ્યા પછી જ ઉપવાસ છોડે છે, તેથી આ પેજ પર ચંદ્રોદય મુખ્ય સમય છે.</p><p>મંગળવારની સંકષ્ટી અંગારકી સંકષ્ટી ચતુર્થી છે, જે ખાસ ફળદાયી મનાય છે. મહા (પૂર્ણિમાંત)ની સંકષ્ટી ઉત્તર ભારતમાં સકટ ચોથ તરીકે રખાય છે.</p>",
    # EN: <p>Masik Shivratri (monthly Shivratri) is the night of Lord Shiva kept on Chaturdashi, the
    #     14th tithi, of the dark fortnight (Krishna paksha) every month. Devotees fast and keep
    #     vigil through the night, bathing the Shiva linga with water, milk, honey and bilva leaves
    #     and chanting "Om Namah Shivaya". The best time for the puja is Nishita kaal, the midnight
    #     window.</p><p>Maha Shivratri, which falls on Krishna Chaturdashi of Phalguna (Magha in the
    #     amanta calendar), is the greatest of the twelve.</p>
    "about.masik_shivratri": "<p>માસિક શિવરાત્રિ (દર મહિનાની શિવરાત્રિ) એ ભગવાન શિવની રાત્રિ છે જે દર મહિને વદ પક્ષની ચૌદશે, 14મી તિથિએ, રખાય છે. ભક્તો ઉપવાસ કરે છે અને આખી રાત જાગરણ કરે છે, શિવલિંગને જળ, દૂધ, મધ અને બિલીપત્રથી સ્નાન કરાવે છે અને “ઓમ નમઃ શિવાય”નો જાપ કરે છે. પૂજા માટે સૌથી સારો સમય નિશીથ કાળ, મધ્યરાત્રિનો સમય છે.</p><p>મહાશિવરાત્રિ, જે ફાગણ (અમાંત કેલેન્ડરમાં, જે ગુજરાતમાં વપરાય છે, મહા) વદ ચૌદશે આવે છે, તે બારમાં સૌથી મહાન છે.</p>",
    # EN: <p>Kalashtami (Kala Ashtami) is the monthly day of Lord Kala Bhairava, the fierce form of
    #     Shiva who guards time, kept on Ashtami, the 8th tithi, of the dark fortnight (Krishna
    #     paksha). Devotees fast, worship Bhairava at night with a mustard-oil lamp and offerings
    #     such as black sesame, and feed dogs, which are associated with him.</p><p>The Kalashtami
    #     of Margashirsha in the purnimanta calendar (Kartika in the amanta calendar) is
    #     Kalabhairava Jayanti, his appearance day and the most important of the year.</p>
    "about.kalashtami": "<p>કાલાષ્ટમી (કાલ અષ્ટમી) એ ભગવાન કાલ ભૈરવનો માસિક દિવસ છે, શિવનું ઉગ્ર સ્વરૂપ જે સમયનું રક્ષણ કરે છે, જે વદ પક્ષની આઠમે, 8મી તિથિએ, રખાય છે. ભક્તો ઉપવાસ કરે છે, રાત્રે સરસવના તેલના દીવા અને કાળા તલ જેવી અર્પણો સાથે ભૈરવની પૂજા કરે છે અને કૂતરાંને જમાડે છે, જે તેમની સાથે જોડાયેલાં છે.</p><p>માગશર (પૂર્ણિમાંત કેલેન્ડરમાં; અમાંત કેલેન્ડરમાં કારતક)ની કાલાષ્ટમી કાલભૈરવ જયંતી છે, તેમનો પ્રાગટ્ય દિવસ અને વર્ષનો સૌથી મહત્વનો.</p>",
    # EN: Purnima can begin one evening and end the next afternoon, so the day the tithi starts and
    #     the day of the vrat can differ. The rule settles it: the vrat goes to the day on which the
    #     tithi covers Madhyahna (the middle fifth of the daytime); if it covers Madhyahna on both
    #     days, the earlier day is taken. Some traditions use the sunrise tithi for the holy bath
    #     and charity instead; the table gives the start and end of the tithi so you can check.
    "note.purnima": "પૂનમ એક સાંજે શરૂ થઈને બીજી બપોરે પૂરી થઈ શકે છે, તેથી તિથિ શરૂ થવાનો દિવસ અને વ્રતનો દિવસ અલગ હોઈ શકે. નિયમ તે નક્કી કરે છે: વ્રત તે દિવસે જાય છે જે દિવસે તિથિ મધ્યાહ્ન (દિવસના સમયનો મધ્યનો પાંચમો ભાગ)ને આવરી લે; જો તે બંને દિવસે મધ્યાહ્નને આવરી લે, તો વહેલો દિવસ લેવાય છે. કેટલીક પરંપરાઓ પવિત્ર સ્નાન અને દાન માટે તેને બદલે સૂર્યોદયની તિથિ વાપરે છે; કોષ્ટક તિથિની શરૂઆત અને અંત આપે છે જેથી તમે ચકાસી શકો.",
    # EN: Amavasya is a daytime observance (shraddha and tarpan are done in the day), so the date is
    #     the day on which the Amavasya tithi is running at sunrise. The tithi often starts the
    #     evening before, so the times in the table can begin on the previous date. Festival
    #     Amavasyas follow their own rules - Diwali is fixed by Pradosh, Sarva Pitru Amavasya by
    #     Aparahna - and can fall a day away from the date here.
    "note.amavasya": "અમાસ દિવસનું અનુષ્ઠાન છે (શ્રાદ્ધ અને તર્પણ દિવસે થાય છે), તેથી તારીખ તે દિવસ છે જે દિવસે સૂર્યોદયે અમાસ તિથિ ચાલુ હોય. તિથિ ઘણી વાર આગલી સાંજે શરૂ થાય છે, તેથી કોષ્ટકના સમય આગલી તારીખે શરૂ થઈ શકે છે. તહેવારની અમાસો પોતાના નિયમ અનુસરે છે - દિવાળી પ્રદોષથી, સર્વપિતૃ અમાસ અપરાહ્નથી નક્કી થાય છે - અને અહીંની તારીખથી એક દિવસ દૂર આવી શકે છે.",
    # EN: The date is decided in the evening, not at sunrise: the vrat goes to the day on which
    #     Trayodashi is running in Pradosh kaal after sunset, so a Trayodashi that starts at noon
    #     and ends the next afternoon is kept on the first day. If the tithi touches Pradosh kaal on
    #     two evenings, the earlier evening is taken. The puja window in the table starts at sunset
    #     in New Delhi, so it moves through the year and from city to city.
    "note.pradosh": "તારીખ સાંજે નક્કી થાય છે, સૂર્યોદયે નહીં: વ્રત તે દિવસે જાય છે જે દિવસે સૂર્યાસ્ત પછીના પ્રદોષ કાળમાં તેરસ ચાલુ હોય, તેથી બપોરે શરૂ થઈને બીજી બપોરે પૂરી થતી તેરસ પહેલા દિવસે રખાય છે. જો તિથિ બે સાંજે પ્રદોષ કાળને સ્પર્શે, તો વહેલી સાંજ લેવાય છે. કોષ્ટકમાં પૂજાનો સમય નવી દિલ્હીમાં સૂર્યાસ્તથી શરૂ થાય છે, તેથી તે આખા વર્ષ દરમિયાન અને શહેર પ્રમાણે બદલાય છે.",
    # EN: Sankashti is decided by the Moon, not the Sun: the vrat goes to the evening on which
    #     Chaturthi is running at moonrise, since that is when the fast is broken. The date can
    #     therefore differ from the Chaturthi date of a Panchang that goes by sunrise. Moonrise is
    #     roughly 50 minutes later each day and differs by several minutes between cities, so check
    #     it for your own city.
    "note.sankashti": "સંકષ્ટી ચંદ્ર દ્વારા નક્કી થાય છે, સૂર્ય દ્વારા નહીં: વ્રત તે સાંજે જાય છે જે સાંજે ચંદ્રોદયે ચોથ ચાલુ હોય, કારણ કે ત્યારે ઉપવાસ છોડાય છે. તેથી તારીખ સૂર્યોદય પ્રમાણે ચાલતા પંચાંગની ચોથની તારીખથી અલગ હોઈ શકે. ચંદ્રોદય રોજ લગભગ 50 મિનિટ મોડો થાય છે અને શહેરો વચ્ચે કેટલીક મિનિટ અલગ હોય છે, તેથી તમારા પોતાના શહેર માટે તપાસો.",
    # EN: This is a midnight observance, so the date is the day on which Chaturdashi is running at
    #     Nishita kaal (the 8th of the 15 muhurtas of the night, around midnight). Nishita can fall
    #     just after 12 o'clock, in which case the puja is done in the early hours of the next date
    #     and the time shown carries that date. If the tithi touches Nishita on two nights, the
    #     earlier night is taken.
    "note.masik_shivratri": "આ મધ્યરાત્રિનું અનુષ્ઠાન છે, તેથી તારીખ તે દિવસ છે જે દિવસે નિશીથ કાળ (રાત્રિના 15 મુહૂર્તમાંનું 8મું, મધ્યરાત્રિની આસપાસ)માં ચૌદશ ચાલુ હોય. નિશીથ 12 વાગ્યા પછી થોડી વારે આવી શકે, તો પૂજા આગલી તારીખના વહેલા કલાકોમાં થાય છે અને દર્શાવેલ સમય તે તારીખ સાથે આવે છે. જો તિથિ બે રાત્રે નિશીથને સ્પર્શે, તો વહેલી રાત લેવાય છે.",
    # EN: Kalashtami is a night worship, so the date is the day on which Ashtami is running in
    #     Pradosh kaal (the evening window after sunset); the tithi may begin the previous morning
    #     or end during the night, so check its start and end times in the table. If it touches
    #     Pradosh kaal on two evenings, the earlier evening is taken. Some traditions go by the
    #     midnight tithi instead, which can occasionally differ by a day.
    "note.kalashtami": "કાલાષ્ટમી રાત્રિની ઉપાસના છે, તેથી તારીખ તે દિવસ છે જે દિવસે પ્રદોષ કાળ (સૂર્યાસ્ત પછીનો સાંજનો સમય)માં આઠમ ચાલુ હોય; તિથિ આગલી સવારે શરૂ થઈ શકે અથવા રાત્રિ દરમિયાન પૂરી થઈ શકે, તેથી કોષ્ટકમાં તેનો શરૂઆત અને અંતનો સમય તપાસો. જો તે બે સાંજે પ્રદોષ કાળને સ્પર્શે, તો વહેલી સાંજ લેવાય છે. કેટલીક પરંપરાઓ તેને બદલે મધ્યરાત્રિની તિથિ પ્રમાણે ચાલે છે, જે ક્યારેક એક દિવસ અલગ હોઈ શકે.",
    # EN: What are the {name} dates in {year}?
    # keep: {name} {year}
    "faq.all_q": "{year}માં {name}ની તારીખો કઈ છે?",
    # EN: There are {count} {name} dates in {year} (New Delhi): {dates}.
    # keep: {count} {dates} {name} {year}
    "faq.all_a": "{year}માં {name}ની {count} તારીખો છે (નવી દિલ્હી): {dates}.",
    # EN: When is the next {name}?
    # keep: {name}
    "faq.next_q": "આગામી {name} ક્યારે છે?",
    # EN: When is the first {name} of {year}?
    # keep: {name} {year}
    "faq.first_q": "{year}ની પહેલી {name} ક્યારે છે?",
    # EN: {name} is on {when} ({details}).
    # keep: {details} {name} {when}
    "faq.on_a": "{name} {when} ({details}) છે.",
    # EN: What is the {label} on {name} {short}?
    # keep: {label} {name} {short}
    "faq.key_q": "{short}ની {name}નો {label} શું છે?",
    # EN: At what time does the {name} tithi start and end on {short}?
    # keep: {name} {short}
    "faq.tithi_q": "{short}ના રોજ {name} તિથિ કયા સમયે શરૂ અને પૂરી થાય છે?",
    # EN: How is the {name} date decided?
    # keep: {name}
    "faq.why_q": "{name}ની તારીખ કેવી રીતે નક્કી થાય છે?",
    # EN: The date follows the rule: {rule}. In {year} this gives {count} dates (New Delhi).
    # keep: {count} {rule} {year}
    "faq.why_a": "તારીખ આ નિયમ મુજબ છે: {rule}. {year}માં આનાથી {count} તારીખો મળે છે (નવી દિલ્હી).",
    # EN: Monthly vrat dates
    "hub.h2": "માસિક વ્રતની તારીખો",
}

# ----------------------------------------------------------------------------
# hub       /sitemap
# ----------------------------------------------------------------------------

# app/hub_text.py LABELS["gu"] — section names of the crawlable /sitemap page and the footer link block  [19]
HUB_LABELS = {
    # EN: Site map
    "sitemap": "સાઇટ મેપ",
    # EN: Panchang
    "panchang": "પંચાંગ",
    # EN: Rashifal (daily horoscope)
    "rashifal": "રાશિફળ (દૈનિક ભવિષ્ય)",
    # EN: Vrat &amp; festivals
    "vrat": "વ્રત અને તહેવાર",
    # EN: Shubh muhurat
    "muhurat": "શુભ મુહૂર્ત",
    # EN: Nakshatra
    "nakshatra": "નક્ષત્ર",
    # EN: Rashi (zodiac signs)
    "rashi": "રાશિ (રાશિચક્ર)",
    # EN: Kathas
    "katha": "કથાઓ",
    # EN: Free tools
    "tools": "મફત સાધનો",
    # EN: Kundali Milan
    "milan": "કુંડળી મિલન",
    # EN: Free Kundali
    "kundali": "મફત કુંડળી",
    # EN: Rahu Kaal
    "rahu": "રાહુકાળ",
    # EN: Choghadiya
    "choghadiya": "ચોઘડિયાં",
    # EN: Naam se Kundali Milan
    "naam": "નામ પરથી કુંડળી મિલન",
    # EN: Today's Panchang by city
    "cities": "શહેર પ્રમાણે આજનું પંચાંગ",
    # EN: Rashifal by sign
    "signs": "રાશિ પ્રમાણે રાશિફળ",
    # EN: Vrat and festival calendars
    "years": "વ્રત અને તહેવાર કેલેન્ડર",
    # EN: Ekadashi
    "ekadashi": "એકાદશી",
    # EN: Every section of Divine Astro in one place: daily Panchang for Indian cities, Rashifal,
    #     vrat and festival dates, shubh muhurat, nakshatra and rashi guides, kathas and the free
    #     tools.
    "intro": "Divine Astroનો દરેક વિભાગ એક જગ્યાએ: ભારતીય શહેરો માટે દૈનિક પંચાંગ, રાશિફળ, વ્રત અને તહેવારની તારીખો, શુભ મુહૂર્ત, નક્ષત્ર અને રાશિ માર્ગદર્શિકા, કથાઓ અને મફત સાધનો.",
}

# ----------------------------------------------------------------------------
# app       AI-narration vocabulary here; names_<code>.py and static/i18n/<code>.json beside it
# ----------------------------------------------------------------------------

# app/astro_terms.py TERMS["gu"] — house / dasha / sign vocabulary for the AI narration and the chart labels  [16]
ASTRO_TERMS = {
    # EN: house
    "house": "ભાવ",
    # EN: sign
    "sign": "રાશિ",
    # EN: lord
    "lord": "સ્વામી",
    # EN: dasha
    "dasha": "દશા",
    # EN: mahadasha
    "mahadasha": "મહાદશા",
    # EN: antardasha
    "antardasha": "અંતર્દશા",
    # EN: ascendant
    "ascendant": "લગ્ન",
    # EN: transit
    "transit": "ગોચર",
    # EN: retrograde
    "retrograde": "વક્રી",
    # EN: exalted
    "exalted": "ઉચ્ચ",
    # EN: debilitated
    "debilitated": "નીચ",
    # EN: own sign
    "own sign": "સ્વરાશિ",
    # EN: Sade Sati
    "Sade Sati": "સાડાસાતી",
    # EN: Navamsa
    "Navamsa": "નવમાંશ",
    # EN: yoga
    "yoga": "યોગ",
    # EN: remedy
    "remedy": "ઉપાય",
}

# app/astro_terms.py MONTH_VARIANTS["gu"] — other spellings of a Gregorian month the AI may write (month number -> spellings)
# (optional: may stay empty)
ASTRO_MONTHS = {}   # {month number: (other spellings,)}, e.g. {2: ("...",)}
