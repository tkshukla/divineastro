"""Assamese (অসমীয়া, Assamese/Bengali script) — the data a translator fills (DIVASTRO-143).

This file is the ONLY place the as text of the shared tables is edited; app/lang_data merges it
into them at import time, as if it were written in app/seo_text.py and friends.

  python -m app.lang_data check as      what is left, per table (exit 0 = complete)
  python -m app.lang_data skeleton as --force   regenerate (DISCARDS your edits)

Rules: every key below stays; a value "" means "not translated yet" (English shows, the
checker complains). Keep every {placeholder} the comment lists under `keep:`; the word order
is yours. HTML values keep their tags (write &amp; for &). Astrology names (tithi, nakshatra,
rashi, graha ...) are not here: they are in app/astro/names_as.py. Digits are ASCII, as in
the other languages. Full instructions: docs/lang-agent-brief.md.

Set READY when a whole page module is complete, and only then — an unfinished module in READY
fails `check` and CI. A module that is not READY renders the English body, noindex.
"""

from __future__ import annotations

# Page modules that are complete for this language (the table groups below):
#   "seo" "rashifal" "vrat" "nakshatra" "muhurat" "recurring" "hub" "app"
READY = frozenset({"seo", "rashifal", "vrat", "nakshatra", "muhurat", "recurring", "hub", "app"})

# Latin-script words the as text may keep besides the defaults (WhatsApp, UPI, PDF ...).
# "Priya", "Kshitij": Latin-spelled example names in the naam-milan explainer (users type names in English);
# "name", "gmail.com": the e-mail input placeholder.
ALLOW_LATIN = frozenset({"Priya", "Kshitij", "name", "gmail.com"})

# static/i18n/as.json keys whose value is deliberately the English word (brand names, "OK").
# the e-mail placeholder is an address, not prose
KEEP_ENGLISH = frozenset({"acct.emailPlaceholder"})

# Namakshar syllables are Devanagari in the engine; this maps a letter to this script:
# (Unicode block start, {Devanagari letter: this script's letter where the offset is wrong}).
# Already set — `check` verifies all 108 syllables come out in the as script.
AKSHAR = (0x0980, {'र': 'ৰ', 'व': 'ৱ'})


# ----------------------------------------------------------------------------
# seo       /panchang /rahu-kaal /choghadiya /kundali-milan /free-kundali + shared chrome, cities
# ----------------------------------------------------------------------------

# app/seo_text.py TEXT["as"] — page text of /panchang /rahu-kaal /choghadiya /kundali-milan /free-kundali  [134]
SEO_TEXT = {
    # EN: Panchang
    "tool.panchang": "পঞ্জিকা",
    # EN: Rahu Kaal
    "tool.rahu-kaal": "ৰাহুকাল",
    # EN: Choghadiya
    "tool.choghadiya": "চৌঘড়িয়া",
    # EN: {vara}, {date} · {place} · IST
    # keep: {date} {place} {vara}
    "when": "{vara}, {date} · {place} · ভাৰতীয় সময়",
    # EN: {name} until {time}
    # keep: {name} {time}
    "limb.until": "{name} {time} লৈকে",
    # EN: then {name}
    # keep: {name}
    "limb.then": "তাৰ পিছত {name}",
    # EN: pada
    "limb.pada": "পাদ",
    # EN: {paksha} paksha
    # keep: {paksha}
    "paksha.full": "{paksha} পক্ষ",
    # EN: {tool} in other cities
    # keep: {tool}
    "cities.heading": "অন্য চহৰৰ {tool}",
    # EN: More free tools
    "links.heading": "আৰু বিনামূলীয়া সেৱা",
    # EN: {tool} in {city}
    # keep: {city} {tool}
    "links.tool_in_city": "{city} চহৰৰ {tool}",
    # EN: Kundali Milan (36 guna)
    "links.milan": "কুণ্ডলী মিলন (36 গুণ)",
    # EN: Free Janam Kundali
    "links.kundali": "বিনামূলীয়া জন্মকুণ্ডলী",
    # EN: Muhurat Finder
    "links.muhurat": "শুভ মুহূৰ্ত বিচাৰক",
    # EN: Today's Rashifal
    "links.rashifal": "আজিৰ ৰাশিফল",
    # EN: Today's Vrat & Festivals in {city}
    # keep: {city}
    "links.vrat": "{city} চহৰত আজিৰ ব্ৰত আৰু উৎসৱ",
    # EN: City not found — {brand}
    # keep: {brand}
    "nf.title": "চহৰটো পোৱা নগ'ল — {brand}",
    # EN: {tool} city not found.
    # keep: {tool}
    "nf.desc": "{tool}: এই চহৰটো আমাৰ তালিকাত নাই।",
    # EN: <h1>{tool}: city not found</h1><p>We don't have a page for “{slug}” yet. Pick a city
    #     below, or <a href="{app}">open the {tool} tool</a> to use any place in the world.</p>
    # keep: {app} {slug} {tool}
    "nf.body": "<h1>{tool}: চহৰটো পোৱা নগ'ল</h1><p>“{slug}”ৰ বাবে আমাৰ এতিয়াও কোনো পৃষ্ঠা নাই। তলৰ পৰা এটা চহৰ বাছি লওক, অথবা <a href=\"{app}\">{tool} খোলক</a> — তাত পৃথিৱীৰ যিকোনো ঠাই বাছি ল'ব পাৰিব।</p>",
    # EN: Today's Panchang in {city}, {date} — Tithi, Nakshatra, Rahu Kaal | {brand}
    # keep: {brand} {city} {date}
    "p.title": "আজিৰ পঞ্জিকা {city}, {date} — তিথি, নক্ষত্ৰ, ৰাহুকাল | {brand}",
    # EN: Aaj ka Panchang for {city} on {vara}, {date}: {tithi} tithi ({paksha} paksha), {nakshatra}
    #     nakshatra, sunrise {sunrise}, Rahu Kaal {rahu}. Computed with Swiss Ephemeris.
    # keep: {city} {date} {nakshatra} {rahu} {sunrise} {tithi} {vara}
    # may also use: {paksha_full} {paksha}
    "p.desc": "{city} চহৰৰ {vara}, {date} তাৰিখৰ পঞ্জিকা: {paksha} পক্ষৰ {tithi} তিথি, {nakshatra} নক্ষত্ৰ, সূৰ্যোদয় {sunrise}, ৰাহুকাল {rahu}। সুইচ এফেমেৰিছেৰে নিৰ্ভুল গণনা।",
    # EN: <h1>Today's Panchang in {city}</h1>
    # keep: {city}
    "p.h1": "<h1>{city} চহৰৰ আজিৰ পঞ্জিকা</h1>",
    # EN: <p class="hi" lang="hi">आज का पंचांग — {city_hi}</p>
    # keep: {city}
    "p.sub": "<p class=\"hi\">তিথি, নক্ষত্ৰ, যোগ, কৰণ আৰু ৰাহুকাল — {city}</p>",
    # EN: <div class="box"><p>Today in {city} is <strong>{paksha} {tithi}</strong> with the Moon in
    #     <strong>{nakshatra}</strong> nakshatra. Rahu Kaal runs <strong>{rahu}</strong> — avoid
    #     starting anything new in that window.</p></div>
    # keep: {city} {nakshatra} {rahu} {tithi}
    # may also use: {paksha_full} {paksha}
    "p.box": "<div class=\"box\"><p>আজি {city} চহৰত <strong>{paksha} {tithi}</strong>, চন্দ্ৰ আছে <strong>{nakshatra}</strong> নক্ষত্ৰত। ৰাহুকাল <strong>{rahu}</strong> — এই সময়ছোৱাত নতুন কোনো কাম আৰম্ভ নকৰিব।</p></div>",
    # EN: Vaar (weekday)
    "p.r_vara": "বাৰ",
    # EN: Tithi
    "p.r_tithi": "তিথি",
    # EN: Paksha
    "p.r_paksha": "পক্ষ",
    # EN: Nakshatra
    "p.r_nakshatra": "নক্ষত্ৰ",
    # EN: Yoga
    "p.r_yoga": "যোগ",
    # EN: Karana
    "p.r_karana": "কৰণ",
    # EN: Sunrise
    "p.r_sunrise": "সূৰ্যোদয়",
    # EN: Sunset
    "p.r_sunset": "সূৰ্যাস্ত",
    # EN: Moonrise
    "p.r_moonrise": "চন্দ্ৰোদয়",
    # EN: Moonset
    "p.r_moonset": "চন্দ্ৰাস্ত",
    # EN: Moon sign
    "p.r_moon_sign": "চন্দ্ৰ ৰাশি",
    # EN: Rahu Kaal
    "p.r_rahu": "ৰাহুকাল",
    # EN: Yamaganda
    "p.r_yama": "যমগণ্ড",
    # EN: Gulika Kaal
    "p.r_gulika": "গুলিক কাল",
    # EN: Abhijit Muhurat
    "p.r_abhijit": "অভিজিৎ মুহূৰ্ত",
    # EN: {vara_en} — {weekday} <span lang="hi">({vara_hi})</span>
    # keep: {vara}
    "p.v_vara": "{vara}",
    # EN: {paksha_en} <span lang="hi">({paksha_hi_full})</span>
    # keep: {paksha_full}
    "p.v_paksha": "{paksha_full}",
    # EN: No moonrise this day
    "p.no_moonrise": "এই দিনা চন্দ্ৰোদয় নাই",
    # EN: No moonset this day
    "p.no_moonset": "এই দিনা চন্দ্ৰাস্ত নাই",
    # EN: Not observed on Wednesday (Budhavara)
    "p.no_abhijit": "বুধবাৰে অভিজিৎ মুহূৰ্ত ধৰা নহয়",
    # EN: <p>Times are for {place} ({lat}°N, {lon}°E) in Indian Standard Time. The panchang day runs
    #     from sunrise to the next sunrise, so a tithi or nakshatra may end after midnight. Sunrise
    #     is the visible upper limb with refraction, as printed in Indian almanacs; nakshatra and
    #     yoga use the Lahiri ayanamsa.</p>
    # keep: {lat} {lon}
    # may also use: {city} {place}
    "p.note": "<p>সকলো সময় {place} ({lat}° উত্তৰ, {lon}° পূব)ৰ বাবে, ভাৰতীয় মান সময়ত দিয়া হৈছে। পঞ্জিকাৰ দিন এটা সূৰ্যোদয়ৰ পৰা পিছৰ সূৰ্যোদয়লৈ চলে, গতিকে কোনো তিথি বা নক্ষত্ৰ মাজৰাতিৰ পিছতো শেষ হ'ব পাৰে। সূৰ্যোদয় ভাৰতীয় পঞ্জিকাত ছপা হোৱাৰ দৰে, বায়ুমণ্ডলৰ প্ৰতিসৰণসহ সূৰ্যৰ ওপৰৰ কিনাৰা দেখা দিয়া মুহূৰ্তত ধৰা হৈছে; নক্ষত্ৰ আৰু যোগ লাহিড়ী অয়নাংশত গণনা কৰা।</p>",
    # EN: Open the full Panchang — any city, any date
    "p.cta": "সম্পূৰ্ণ পঞ্জিকা খোলক — যিকোনো চহৰ, যিকোনো তাৰিখ",
    # EN: <h2>The five limbs of the Panchang</h2> <p><strong>Tithi</strong> is the lunar day — each
    #     12° the Moon gains on the Sun. <strong>Nakshatra</strong> is the Moon's lunar mansion, one
    #     of 27. <strong>Yoga</strong> comes from the combined longitudes of Sun and Moon, and
    #     <strong>Karana</strong> is half a tithi. <strong>Vaar</strong> is the weekday, reckoned
    #     from sunrise. Together they are the <span lang="hi">पंचांग</span> (“five limbs”) consulted
    #     before any auspicious work.</p>
    "p.limbs": "<h2>পঞ্জিকাৰ পাঁচটা অঙ্গ</h2> <p><strong>তিথি</strong> হ'ল চান্দ্ৰ দিন — চন্দ্ৰই সূৰ্যতকৈ প্ৰতি 12° আগবাঢ়িলে এটা তিথি হয়। <strong>নক্ষত্ৰ</strong> হ'ল 27 টাৰ ভিতৰত চন্দ্ৰ থকা নক্ষত্ৰ। <strong>যোগ</strong> সূৰ্য আৰু চন্দ্ৰৰ ভোগাংশৰ যোগফলৰ পৰা পোৱা যায়, আৰু <strong>কৰণ</strong> হ'ল আধা তিথি। <strong>বাৰ</strong> হ'ল সপ্তাহৰ দিন, যিটো সূৰ্যোদয়ৰ পৰা গণনা কৰা হয়। এই পাঁচটা লগ লাগিয়েই পঞ্চাঙ্গ (“পাঁচ অঙ্গ”) হয়, যিটো যিকোনো শুভ কামৰ আগতে চোৱা হয়।</p>",
    # EN: Rahu Kaal Today in {city} — {rahu}, {date} | {brand}
    # keep: {brand} {city} {rahu}
    # may also use: {date}
    "rk.title": "আজিৰ ৰাহুকাল {city} — {rahu}, {date} | {brand}",
    # EN: Rahu Kaal today in {city} ({vara}, {date}) is {rahu}. Also Yamaganda {yama} and Gulika
    #     {gulika}, with this week's timings and what Rahu Kaal means.
    # keep: {city} {date} {gulika} {rahu} {vara} {yama}
    "rk.desc": "আজি {vara}, {date} তাৰিখে {city} চহৰত ৰাহুকাল {rahu}। লগতে যমগণ্ড {yama} আৰু গুলিক কাল {gulika}, এই সপ্তাহৰ সময়সূচী আৰু ৰাহুকালৰ অৰ্থ।",
    # EN: <h1>Rahu Kaal Today in {city}</h1>
    # keep: {city}
    "rk.h1": "<h1>{city} চহৰৰ আজিৰ ৰাহুকাল</h1>",
    # EN: <p class="hi" lang="hi">आज का राहु काल — {city_hi}</p>
    # keep: {city}
    "rk.sub": "<p class=\"hi\">আজি ৰাহুকাল, যমগণ্ড আৰু গুলিক কাল কেতিয়া — {city}</p>",
    # EN: Rahu Kaal <span lang="hi">(राहु काल)</span>
    "rk.r_rahu": "ৰাহুকাল",
    # EN: Yamaganda <span lang="hi">(यमगण्ड)</span>
    "rk.r_yama": "যমগণ্ড",
    # EN: Gulika Kaal <span lang="hi">(गुलिक काल)</span>
    "rk.r_gulika": "গুলিক কাল",
    # EN: Abhijit Muhurat
    "rk.r_abhijit": "অভিজিৎ মুহূৰ্ত",
    # EN: Sunrise / Sunset
    "rk.r_sun": "সূৰ্যোদয় / সূৰ্যাস্ত",
    # EN: Not observed on Wednesday
    "rk.no_abhijit": "বুধবাৰে ধৰা নহয়",
    # EN: Check Rahu Kaal for any city or date
    "rk.cta": "যিকোনো চহৰ বা তাৰিখৰ ৰাহুকাল চাওক",
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
    "rk.about": "<h2>ৰাহুকাল কি?</h2> <p>ৰাহুকাল হ'ল প্ৰতিদিনৰ প্ৰায় দেৰ ঘণ্টাৰ এটা সময়, যিটো পৰম্পৰা অনুসৰি ৰাহুৰ (চন্দ্ৰৰ উত্তৰ পাত) অধীন বুলি ধৰা হয়। সূৰ্যোদয়ৰ পৰা সূৰ্যাস্তলৈকে দিনটোক আঠটা সমান ভাগত ভাগ কৰা হয়, তাৰে এটা ভাগ ৰাহুৰ। কোনটো ভাগ সেয়া বাৰৰ ওপৰত নিৰ্ভৰ কৰে: দেওবাৰে অষ্টম, সোমবাৰে দ্বিতীয়, মঙ্গলবাৰে সপ্তম, বুধবাৰে পঞ্চম, বৃহস্পতিবাৰে ষষ্ঠ, শুক্ৰবাৰে চতুৰ্থ আৰু শনিবাৰে তৃতীয়।</p> <p>এইটো প্ৰকৃত সূৰ্যোদয় আৰু সূৰ্যাস্ত অনুসৰি চলে, সেয়ে ৰাহুকাল প্ৰতিটো চহৰতে বেলেগ আৰু বছৰটোত সলনি হৈ থাকে — সেইবাবে “সোমবাৰ 7:30–9:00”ৰ দৰে নিৰ্দিষ্ট তালিকা কেৱল আনুমানিক। পৰম্পৰা অনুসৰি ৰাহুকালত নতুন উদ্যোগ আৰম্ভ, চুক্তিত চহী, যাত্ৰা আৰম্ভ বা ডাঙৰ কিনাকটা কৰা নহয়; আগৰে পৰা চলি থকা কাম চলাই যাব পাৰি। যমগণ্ড আৰু গুলিক কাল দিনটোৰ আৰু দুটা অষ্টমাংশ, যিবোৰতো একে ধৰণৰ সাৱধানতা মানা হয়।</p>",
    # EN: <h2>Rahu Kaal in {city} this week</h2>
    # keep: {city}
    "rk.week_h2": "<h2>এই সপ্তাহত {city} চহৰৰ ৰাহুকাল</h2>",
    # EN: Day
    "rk.th_day": "দিন",
    # EN: Rahu Kaal
    "rk.th_rahu": "ৰাহুকাল",
    # EN: Yamaganda
    "rk.th_yama": "যমগণ্ড",
    # EN: Gulika
    "rk.th_gulika": "গুলিক",
    # EN: Choghadiya Today in {city}, {date} — Day & Night Timings | {brand}
    # keep: {brand} {city} {date}
    "ch.title": "আজিৰ চৌঘড়িয়া {city}, {date} — দিন আৰু ৰাতিৰ শুভ সময় | {brand}",
    # EN: Today's choghadiya for {city} ({vara}, {date}): all 16 day and night muhurtas — Amrit,
    #     Shubh, Labh, Char, Rog, Kaal, Udveg — with exact start and end times from sunrise
    #     {sunrise}.
    # keep: {city} {date} {sunrise} {vara}
    "ch.desc": "{city} চহৰৰ আজিৰ চৌঘড়িয়া ({vara}, {date}): দিন আৰু ৰাতিৰ সকলো 16 টা মুহূৰ্ত — অমৃত, শুভ, লাভ, চৰ, ৰোগ, কাল, উদ্বেগ — সূৰ্যোদয় {sunrise}ৰ পৰা আৰম্ভ হোৱা আৰু শেষ হোৱাৰ নিৰ্ভুল সময়সহ।",
    # EN: <h1>Choghadiya Today in {city}</h1>
    # keep: {city}
    "ch.h1": "<h1>{city} চহৰৰ আজিৰ চৌঘড়িয়া</h1>",
    # EN: <p class="hi" lang="hi">आज का चौघड़िया — {city_hi}</p>
    # keep: {city}
    "ch.sub": "<p class=\"hi\">দিন আৰু ৰাতিৰ শুভ-অশুভ সময় — {city}</p>",
    # EN: {name} from {time}
    # keep: {name} {time}
    "ch.first_good": "{name} — {time}ৰ পৰা",
    # EN: none
    "ch.none": "নাই",
    # EN: <div class="box"><p>Sunrise <strong>{sunrise}</strong>, sunset <strong>{sunset}</strong>.
    #     First auspicious daytime choghadiya: <strong>{first_good}</strong>.</p></div>
    # keep: {first_good} {sunrise} {sunset}
    "ch.box": "<div class=\"box\"><p>সূৰ্যোদয় <strong>{sunrise}</strong>, সূৰ্যাস্ত <strong>{sunset}</strong>। দিনৰ প্ৰথম শুভ চৌঘড়িয়া: <strong>{first_good}</strong>।</p></div>",
    # EN: <h2>Day Choghadiya <span lang="hi">(दिन का चौघड़िया)</span></h2>
    "ch.day_h2": "<h2>দিনৰ চৌঘড়িয়া</h2>",
    # EN: <h2>Night Choghadiya <span lang="hi">(रात का चौघड़िया)</span></h2>
    "ch.night_h2": "<h2>ৰাতিৰ চৌঘড়িয়া</h2>",
    # EN: <tr><th>Time</th><th>Choghadiya</th><th>Nature</th></tr>
    "ch.th": "<tr><th>সময়</th><th>চৌঘড়িয়া</th><th>প্ৰকৃতি</th></tr>",
    # EN: <tr><td>{when}</td><td class="{cls}"><strong>{name}</strong> <span lang="hi">({name_hi})</
    #     span><small>{ruler}</small></td><td>{quality}<small>{desc}</small></td></tr>
    # keep: {cls} {desc} {name} {quality} {ruler} {when}
    "ch.row": "<tr><td>{when}</td><td class=\"{cls}\"><strong>{name}</strong><small>অধিপতি: {ruler}</small></td><td>{quality}<small>{desc}</small></td></tr>",
    # EN: Open the live Choghadiya clock
    "ch.cta": "লাইভ চৌঘড়িয়া ঘড়ী খোলক",
    # EN: <h2>How choghadiya works</h2> <p>The day from sunrise to sunset, and the night from sunset
    #     to the next sunrise, are each divided into eight equal parts called choghadiya (<span
    #     lang="hi">चौघड़िया</span>, “four ghadis”). Each is ruled by a planet and named for its
    #     nature: <strong>Amrit</strong>, <strong>Shubh</strong> and <strong>Labh</strong> are
    #     auspicious, <strong>Char</strong> is neutral and good for travel, while
    #     <strong>Rog</strong>, <strong>Kaal</strong> and <strong>Udveg</strong> are avoided for new
    #     beginnings. The order starts from the weekday's ruler, so it changes every day — and the
    #     length of each slot follows the real day length in {city}.</p>
    # keep: {city}
    "ch.about": "<h2>চৌঘড়িয়া কেনেকৈ গণনা কৰা হয়</h2> <p>সূৰ্যোদয়ৰ পৰা সূৰ্যাস্তলৈকে দিন, আৰু সূৰ্যাস্তৰ পৰা পিছৰ সূৰ্যোদয়লৈকে ৰাতি — দুয়োটাকে আঠটাকৈ সমান ভাগত ভাগ কৰা হয়, যাক চৌঘড়িয়া (“চাৰি ঘড়ী”) বোলা হয়। প্ৰতিটো ভাগৰ এজন অধিপতি গ্ৰহ আছে, আৰু নামটো তাৰ প্ৰকৃতি অনুসৰি: <strong>অমৃত</strong>, <strong>শুভ</strong> আৰু <strong>লাভ</strong> শুভ, <strong>চৰ</strong> মধ্যম আৰু যাত্ৰাৰ বাবে ভাল, আনহাতে <strong>ৰোগ</strong>, <strong>কাল</strong> আৰু <strong>উদ্বেগ</strong>ত নতুন কাম আৰম্ভ কৰা নহয়। ক্ৰম বাৰৰ অধিপতিৰ পৰা আৰম্ভ হয়, সেয়ে প্ৰতিদিনে সলনি হয় — আৰু প্ৰতিটো ভাগৰ দৈৰ্ঘ্য {city} চহৰৰ প্ৰকৃত দিনৰ দৈৰ্ঘ্য অনুসৰি হয়।</p>",
    # EN: Kundali Milan — Ashtakoot Guna Milan ({total} Gun) Explained | {brand}
    # keep: {brand} {total}
    "km.title": "কুণ্ডলী মিলন — অষ্টকূট গুণ মিলন ({total} গুণ) বিতংভাৱে | {brand}",
    # EN: How Kundali Milan works: the 8 kootas of Ashtakoot Guna Milan, {total} points, what score
    #     is good for marriage, and how Mangal Dosha is checked. Free online matching in English and
    #     Hindi.
    # keep: {total}
    "km.desc": "কুণ্ডলী মিলন কেনেকৈ হয়: অষ্টকূট গুণ মিলনৰ 8 টা কূট, মুঠ {total} গুণ, বিয়াৰ বাবে কিমান গুণ ভাল, আৰু মঙ্গল দোষ কেনেকৈ চোৱা হয়। বিনামূলীয়া অনলাইন কুণ্ডলী মিলন।",
    # EN: Kundali Milan
    "km.crumb": "কুণ্ডলী মিলন",
    # EN: <h1>Kundali Milan: Ashtakoot Guna Milan explained</h1> <p class="hi" lang="hi">कुंडली
    #     मिलान — अष्टकूट गुण मिलान ({total} गुण)</p> <p>Kundali Milan (<span lang="hi">कुंडली
    #     मिलान</span>) is the traditional Vedic way of checking marriage compatibility. The most
    #     widely used method in North India is <strong>Ashtakoot Guna Milan</strong>: eight factors
    #     (<em>kootas</em>) are compared between the bride's and groom's charts and scored out of
    #     <strong>{total} points (gunas)</strong>. Every one of them is read from the
    #     <strong>Moon</strong> — its sign (rashi) and its nakshatra at birth — which is why the
    #     score needs an accurate birth date and place, but barely depends on the birth time.</p>
    # keep: {total}
    "km.intro": "<h1>কুণ্ডলী মিলন: অষ্টকূট গুণ মিলনৰ সম্পূৰ্ণ ব্যাখ্যা</h1> <p class=\"hi\">কুণ্ডলী মিলন — অষ্টকূট গুণ মিলন ({total} গুণ)</p> <p>কুণ্ডলী মিলন হ'ল বিয়াৰ আগতে বৰ-কইনাৰ মিল চোৱাৰ পৰম্পৰাগত বৈদিক পদ্ধতি। উত্তৰ ভাৰতত সবাতোকৈ বেছি ব্যৱহৃত পদ্ধতিটো হ'ল <strong>অষ্টকূট গুণ মিলন</strong>: বৰ আৰু কইনাৰ কুণ্ডলীৰ আঠটা বিষয় (<em>কূট</em>) তুলনা কৰি <strong>{total} গুণ</strong>ৰ ভিতৰত নম্বৰ দিয়া হয়। সকলোবোৰ <strong>চন্দ্ৰ</strong>ৰ পৰা চোৱা হয় — জন্মৰ সময়ৰ চন্দ্ৰ ৰাশি আৰু নক্ষত্ৰ — সেইবাবে নম্বৰৰ বাবে জন্মৰ তাৰিখ আৰু স্থান সঠিক লাগে, কিন্তু জন্মৰ সময়ৰ ওপৰত প্ৰায় নিৰ্ভৰ নকৰে।</p>",
    # EN: Match two kundalis now — free
    "km.cta1": "এতিয়াই দুটা কুণ্ডলী মিলাওক — বিনামূলীয়া",
    # EN: <p>Don't know the birth times? Try <a href="{href}">Naam se Kundali Milan</a> — the
    #     traditional match by the first letter of each name.</p>
    # keep: {href}
    "km.naam": "<p>জন্মৰ সময় নাজানেনে? <a href=\"{href}\">নামৰ আখৰেৰে কুণ্ডলী মিলন</a> চেষ্টা কৰক — দুয়োৰে নামৰ প্ৰথম আখৰৰ পৰম্পৰাগত মিলন।</p>",
    # EN: <h2>The 8 kootas and their points</h2>
    "km.kootas_h2": "<h2>8 টা কূট আৰু সিহঁতৰ গুণ</h2>",
    # EN: <tr><th>Koota</th><th>Points</th><th>What it measures</th></tr>
    "km.th": "<tr><th>কূট</th><th>গুণ</th><th>কি জোখে</th></tr>",
    # EN: <tr><td><strong>{name}</strong> <span
    #     lang="hi">({name_hi})</span></td><td>{pts}</td><td>{text}</td></tr>
    # keep: {name} {pts} {text}
    "km.row": "<tr><td><strong>{name}</strong></td><td>{pts}</td><td>{text}</td></tr>",
    # EN: Total
    "km.total": "মুঠ",
    # EN: <h2>What is a good Guna Milan score?</h2>
    "km.score_h2": "<h2>গুণ মিলনৰ ভাল নম্বৰ কিমান?</h2>",
    # EN: <tr><th>Gunas</th><th>Conventional reading</th></tr>
    "km.score_th": "<tr><th>গুণ</th><th>প্ৰচলিত অৰ্থ</th></tr>",
    # EN: Below {n}
    # keep: {n}
    "km.below": "{n}তকৈ কম",
    # EN: <p>18 is the conventional minimum. The total alone is not the whole story: a high score
    #     with an uncancelled Nadi or Bhakoot dosha is read with caution, and a modest score with
    #     strong Graha Maitri and no doshas is often considered workable. These bands are a
    #     convention with a long history, not a measurement — they are guidance, not a verdict on a
    #     relationship.</p>
    "km.score_p": "<p>18 হ'ল প্ৰচলিত সৰ্বনিম্ন নম্বৰ। কেৱল মুঠ নম্বৰেই সকলো নহয়: নাড়ী বা ভকূট দোষ নকটা হৈ থাকিলে বেছি নম্বৰকো সাৱধানে চোৱা হয়, আৰু গ্ৰহ মৈত্ৰী ভাল আৰু কোনো দোষ নথকা অৱস্থাত মাজাৰি নম্বৰকো প্ৰায়ে চলিব পৰা বুলি ধৰা হয়। এই সীমাবোৰ দীঘলীয়া পৰম্পৰাৰ এক নিয়ম, জোখ-মাপ নহয় — এয়া পথ-প্ৰদৰ্শন, সম্পৰ্কৰ ওপৰত ৰায় নহয়।</p>",
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
    "km.or": " বা ",
    # EN: <h2>Mangal Dosha (Manglik)</h2> <p>Mangal Dosha is checked separately from the 36 points.
    #     A chart is Manglik when Mars sits in the {houses} house counted from the
    #     <strong>Lagna</strong> (ascendant), the <strong>Moon</strong> or <strong>Venus</strong>.
    #     Classical texts exempt certain sign placements (for example Mars in its own sign Aries in
    #     the 1st), and Jupiter's aspect on Mars is held to soften it. When <strong>both</strong>
    #     partners are Manglik the dosha is conventionally treated as mutually cancelled — which is
    #     why Manglik matches are made with Manglik partners. Because it depends on the Lagna,
    #     Mangal Dosha does need a reliable birth time.</p>
    # keep: {houses}
    "km.mangal": "<h2>মঙ্গল দোষ (মাংগলিক)</h2> <p>মঙ্গল দোষ 36 গুণৰ পৰা বেলেগকৈ চোৱা হয়। <strong>লগ্ন</strong>, <strong>চন্দ্ৰ</strong> বা <strong>শুক্ৰ</strong>ৰ পৰা গণনা কৰি মঙ্গল গ্ৰহ {houses} ঘৰত থাকিলে কুণ্ডলীটো মাংগলিক বুলি ধৰা হয়। শাস্ত্ৰ অনুসৰি কিছুমান ৰাশিত থকা অৱস্থাত ইয়াৰ ব্যতিক্ৰম আছে (যেনে মঙ্গল নিজৰ ঘৰ মেষত প্ৰথম ঘৰত থাকিলে), আৰু মঙ্গলৰ ওপৰত বৃহস্পতিৰ দৃষ্টি পৰিলে দোষ কমে বুলি ধৰা হয়। <strong>দুয়ো</strong>জন মাংগলিক হ'লে দোষ পৰস্পৰে কাটি যায় বুলি প্ৰথাগতভাৱে ধৰা হয় — সেইবাবে মাংগলিকৰ বিয়া মাংগলিকৰ লগতে দিয়া হয়। লগ্নৰ ওপৰত নিৰ্ভৰ কৰে বাবে মঙ্গল দোষ চাবলৈ জন্মৰ সঠিক সময় লাগে।</p>",
    # EN: <h2>How our matching tool works</h2> <p>Enter both people's date, time and place of birth.
    #     Both charts are cast with the sidereal zodiac (Lahiri ayanamsa) from the Swiss Ephemeris,
    #     and each koota is scored by table lookup from the classical tables, with every
    #     cancellation named. You get the full {total}-point breakdown and both partners' Mangal
    #     Dosha status, in English or <span lang="hi">हिन्दी</span>, free and without signing
    #     up.</p>
    # keep: {total}
    "km.how": "<h2>আমাৰ মিলন সঁজুলিয়ে কেনেকৈ কাম কৰে</h2> <p>দুয়োজনৰে জন্মৰ তাৰিখ, সময় আৰু স্থান লিখক। দুয়োখন কুণ্ডলী সুইচ এফেমেৰিছৰ পৰা লাহিড়ী অয়নাংশৰ সৈতে নিৰয়ন ৰাশিচক্ৰত তৈয়াৰ কৰা হয়, আৰু প্ৰতিটো কূট শাস্ত্ৰীয় তালিকা চাই নম্বৰ দিয়া হয়, প্ৰতিটো দোষ-খণ্ডন নামসহ উল্লেখ কৰি। আপুনি {total} গুণৰ সম্পূৰ্ণ বিৱৰণ আৰু দুয়োজনৰে মঙ্গল দোষৰ অৱস্থা পাব — বিনামূলীয়াকৈ, ছাইন-আপ নকৰাকৈ।</p>",
    # EN: Open Kundali Milan
    "km.cta2": "কুণ্ডলী মিলন খোলক",
    # EN: Varna
    "koota.varna": "বৰ্ণ",
    # EN: Vashya
    "koota.vashya": "বশ্য",
    # EN: Tara
    "koota.tara": "তাৰা",
    # EN: Yoni
    "koota.yoni": "যোনি",
    # EN: Graha Maitri
    "koota.graha_maitri": "গ্ৰহ মৈত্ৰী",
    # EN: Gana
    "koota.gana": "গণ",
    # EN: Bhakoot
    "koota.bhakoot": "ভকূট",
    # EN: Nadi
    "koota.nadi": "নাড়ী",
    # EN: Spiritual and working temperament, from the Moon sign's varna. Full point when the groom's
    #     varna is not below the bride's.
    "koota_about.varna": "চন্দ্ৰ ৰাশিৰ বৰ্ণৰ পৰা চোৱা আধ্যাত্মিক আৰু কৰ্মগত স্বভাৱ। বৰৰ বৰ্ণ কইনাৰ বৰ্ণতকৈ তলত নহ'লে সম্পূৰ্ণ গুণ।",
    # EN: Mutual attraction and influence — which sign “draws” the other.
    "koota_about.vashya": "পৰস্পৰৰ আকৰ্ষণ আৰু প্ৰভাৱ — কোনটো ৰাশিয়ে আনটোক “টানে”।",
    # EN: Health and wellbeing, from the count between the two birth nakshatras; the 3rd, 5th and
    #     7th taras are unfavourable.
    "koota_about.tara": "দুয়োৰে জন্ম নক্ষত্ৰৰ মাজৰ গণনাৰ পৰা চোৱা স্বাস্থ্য আৰু কল্যাণ; 3য়, 5ম আৰু 7ম তাৰা অশুভ।",
    # EN: Physical and intimate compatibility; each nakshatra has an animal yoni, and sworn-enemy
    #     animals score zero.
    "koota_about.yoni": "শাৰীৰিক আৰু ঘনিষ্ঠ মিল; প্ৰতিটো নক্ষত্ৰৰ এটা পশুযোনি আছে, আৰু শত্ৰু পশুৰ যোনিয়ে শূন্য গুণ পায়।",
    # EN: Friendship between the lords of the two Moon signs — the mental wavelength of the couple.
    "koota_about.graha_maitri": "দুয়োটা চন্দ্ৰ ৰাশিৰ অধিপতিৰ মাজৰ বন্ধুত্ব — দম্পতীৰ মানসিক তৰংগৰ মিল।",
    # EN: Temperament: Deva (divine), Manushya (human) or Rakshasa (fierce).
    "koota_about.gana": "স্বভাৱ: দেৱ (দিব্য), মানৱ বা ৰাক্ষস (উগ্ৰ)।",
    # EN: The relative placement of the two Moon signs. The 2/12, 5/9 and 6/8 positions form Bhakoot
    #     dosha, cancelled when the sign lords are the same or friends.
    "koota_about.bhakoot": "দুয়োটা চন্দ্ৰ ৰাশিৰ আপেক্ষিক স্থান। 2/12, 5/9 আৰু 6/8 স্থানে ভকূট দোষ হয়, ৰাশি অধিপতি একে বা বন্ধু হ'লে দোষ কাটি যায়।",
    # EN: The highest-weighted koota, tied to health and progeny. The same nadi for both is Nadi
    #     dosha, with classical cancellations for the same sign/different nakshatra or same
    #     nakshatra/different pada.
    "koota_about.nadi": "সবাতোকৈ বেছি গুণৰ কূট, স্বাস্থ্য আৰু সন্তানৰ লগত জড়িত। দুয়োৰে একে নাড়ী হ'লে নাড়ী দোষ হয়, একে ৰাশি/বেলেগ নক্ষত্ৰ বা একে নক্ষত্ৰ/বেলেগ পাদ হ'লে শাস্ত্ৰীয় দোষ-খণ্ডন আছে।",
    # EN: Free Kundali Online — Janam Kundali (Birth Chart) in English & Hindi | {brand}
    # keep: {brand}
    "fk.title": "বিনামূলীয়া কুণ্ডলী অনলাইন — জন্মকুণ্ডলী (জন্ম-পত্ৰিকা) | {brand}",
    # EN: Make your free janam kundali online: Lagna chart in North or South Indian style, planet
    #     positions, Moon nakshatra, Vimshottari dasha, Navamsa and other divisional charts,
    #     Manglik, Sade Sati and Kaal Sarp check — in English or Hindi, no sign-in needed.
    "fk.desc": "অনলাইনত বিনামূলীয়া জন্মকুণ্ডলী বনাওক: উত্তৰ বা দক্ষিণ ভাৰতীয় ধৰণৰ লগ্ন কুণ্ডলী, গ্ৰহৰ স্থিতি, চন্দ্ৰ নক্ষত্ৰ, বিংশোত্তৰী দশা, নৱাংশ আৰু অন্য বিভাগীয় কুণ্ডলী, মাংগলিক, সাড়ে সাতি আৰু কালসৰ্প যোগ — ছাইন-ইন নালাগে।",
    # EN: Free Kundali
    "fk.crumb": "বিনামূলীয়া কুণ্ডলী",
    # EN: <h1>Free Janam Kundali online</h1> <p class="hi" lang="hi">मुफ़्त जन्म कुंडली — हिंदी और
    #     अंग्रेज़ी में</p> <p>A <strong>janam kundali</strong> (<span lang="hi">जन्म कुंडली</span>,
    #     birth chart) is a map of the sky at the exact moment and place you were born: which of the
    #     twelve signs was rising on the eastern horizon (your <strong>Lagna</strong>), and where
    #     the Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu and Ketu stood among the signs
    #     and the 27 nakshatras. Vedic astrology reads everything else — personality, the twelve
    #     areas of life, and above all <em>timing</em> through the dasha periods — from this one
    #     chart. Ours is computed to the minute and is free.</p>
    "fk.intro": "<h1>অনলাইন বিনামূলীয়া জন্মকুণ্ডলী</h1> <p class=\"hi\">বিনামূলীয়া জন্মকুণ্ডলী — অসমীয়াত</p> <p><strong>জন্মকুণ্ডলী</strong> (জন্ম-পত্ৰিকা) হ'ল আপুনি জন্ম হোৱা সঠিক মুহূৰ্ত আৰু স্থানৰ আকাশৰ নক্সা: পূব দিগন্তত বাৰটা ৰাশিৰ কোনটো উদিত হৈছিল (আপোনাৰ <strong>লগ্ন</strong>), আৰু সূৰ্য, চন্দ্ৰ, মঙ্গল, বুধ, বৃহস্পতি, শুক্ৰ, শনি, ৰাহু আৰু কেতু ৰাশি আৰু 27 টা নক্ষত্ৰৰ ভিতৰত ক'ত আছিল। বৈদিক জ্যোতিষে বাকী সকলো — ব্যক্তিত্ব, জীৱনৰ বাৰটা ক্ষেত্ৰ, আৰু বিশেষকৈ দশা-কালৰ দ্বাৰা <em>সময়</em> — এই এখন কুণ্ডলীৰ পৰাই পঢ়ে। আমাৰটো মিনিট পৰ্যন্ত নিৰ্ভুলকৈ গণনা কৰা, আৰু বিনামূলীয়া।</p>",
    # EN: Make my free kundali now
    "fk.cta1": "মোৰ বিনামূলীয়া কুণ্ডলী এতিয়াই বনাওক",
    # EN: <p>You need your <strong>date</strong>, <strong>time</strong> and <strong>place</strong>
    #     of birth. No sign-in, no card.</p>
    "fk.need": "<p>আপোনাৰ জন্মৰ <strong>তাৰিখ</strong>, <strong>সময়</strong> আৰু <strong>স্থান</strong> লাগিব। ছাইন-ইন নালাগে, কাৰ্ডো নালাগে।</p>",
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
    "fk.includes": "<h2>আপোনাৰ বিনামূলীয়া কুণ্ডলীত কি কি থাকে</h2> <ul> <li><strong>লগ্ন কুণ্ডলী (D1)</strong> উত্তৰ ভাৰতীয় বা দক্ষিণ ভাৰতীয় ধৰণৰ — এটা টিপতে সলনি কৰক।</li> <li><strong>গ্ৰহৰ স্থিতি</strong>: নটা গ্ৰহ আৰু লগ্নৰ ৰাশি, অংশ, ভাৱ, বল আৰু বক্ৰী অৱস্থা, লগতে আপোনাৰ চন্দ্ৰৰ নক্ষত্ৰ আৰু পাদ।</li> <li><strong>বাৰটা ভাৱ</strong> আৰু প্ৰতিটোত থকা গ্ৰহ।</li> <li><strong>বিংশোত্তৰী দশা</strong>: আপোনাৰ বৰ্তমানৰ মহাদশা আৰু অন্তৰ্দশা তাৰিখসহ, চিত্ৰসহ সময়ৰেখাত।</li> <li><strong>বিভাগীয় কুণ্ডলী (বৰ্গ)</strong>: {vargas}।</li> <li><strong>অষ্টকবৰ্গ</strong>: ভাৱ অনুসৰি সৰ্বাষ্টকবৰ্গ আৰু ভিন্নাষ্টকবৰ্গৰ বিন্দু।</li> <li><strong>জৈমিনি</strong> চৰকাৰক (আত্মকাৰকৰ পৰা দাৰকাৰকলৈ) আৰু আৰুঢ় পদ, আৰু লগ্ন, চন্দ্ৰ আৰু সূৰ্য একেলগে লৈ কুণ্ডলীৰ <strong>সুদৰ্শন চক্ৰ</strong> বিশ্লেষণ।</li> <li><strong>দোষ পৰীক্ষা</strong>: মঙ্গল দোষ (মাংগলিক), সাড়ে সাতি আৰু কালসৰ্প।</li> <li>আপোনাৰ কুণ্ডলী আৰু বৰ্তমানৰ দশাৰ বাবে <strong>ৰত্ন আৰু প্ৰতিকাৰ</strong>ৰ পৰামৰ্শ।</li> <li>আপোনাৰ কুণ্ডলীৰ ডেছব'ৰ্ডত আপোনাৰ <strong>দৈনিক ভৱিষ্যদ্বাণী</strong> আৰু আজিৰ পঞ্জিকা।</li> </ul> <p>সকলো <strong>নিৰয়ন ৰাশিচক্ৰত লাহিড়ী অয়নাংশৰ সৈতে</strong>, সম্পূৰ্ণ-ৰাশি ভাৱ পদ্ধতিৰে, সুইচ এফেমেৰিছৰ পৰা গণনা কৰা। বিনামূলীয়া একাউণ্টেৰে আপুনি কুণ্ডলী সংৰক্ষণ কৰিব, কুণ্ডলীটো PDF হিচাপে ডাউনল'ড কৰিব আৰু এআই জ্যোতিষীক প্ৰথম কেইটা প্ৰশ্ন বিনামূলীয়াকৈ সোধিব পাৰিব।</p>",
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
    "fk.read": "<h2>আপোনাৰ কুণ্ডলী কেনেকৈ পঢ়িব</h2> <h3>1. লগ্নৰ পৰা আৰম্ভ কৰক</h3> <p>প্ৰথম ভাৱ হ'ল জন্মৰ সময়ত উদিত ৰাশি। উত্তৰ ভাৰতীয় কুণ্ডলীত ই ওপৰৰ মাজৰ হীৰাৰ আকৃতিৰ ঘৰ, আৰু প্ৰতিটো ঘৰত লিখা সংখ্যাটো ভাৱ নহয়, <em>ৰাশি</em> (1 = মেষ … 12 = মীন)। দক্ষিণ ভাৰতীয় কুণ্ডলীত ৰাশিবোৰ নিৰ্দিষ্ট ঘৰতে থাকে আৰু লগ্ন চিহ্নিত কৰা থাকে। লগ্ন আৰু ইয়াৰ অধিপতিয়ে শৰীৰ, স্বভাৱ আৰু জীৱনৰ সামগ্ৰিক দিশ বুজায়।</p> <h3>2. আপোনাৰ চন্দ্ৰ ৰাশি আৰু নক্ষত্ৰ চাওক</h3> <p>ভাৰতীয় ব্যৱহাৰত আপোনাৰ <strong>ৰাশি</strong> মানে চন্দ্ৰৰ ৰাশি, সূৰ্যৰ নহয়। ৰাশিফল, সাড়ে সাতি আৰু কুণ্ডলী মিলনত এই ৰাশিয়েই ব্যৱহাৰ হয়, আৰু চন্দ্ৰৰ নক্ষত্ৰই ঠিক কৰে আপোনাৰ বিংশোত্তৰী দশা ক'ৰ পৰা আৰম্ভ হ'ব।</p> <h3>3. ভাৱ অনুসৰি গ্ৰহবোৰ পঢ়ক</h3> <p>প্ৰতিটো ভাৱ জীৱনৰ এটা ক্ষেত্ৰ: 1ম নিজে, 2য় ধন আৰু পৰিয়াল, 3য় সাহস আৰু ভাই-ভনী, 4ৰ্থ ঘৰ আৰু মাতৃ, 5ম সন্তান আৰু বুদ্ধি, 6ষ্ঠ স্বাস্থ্য আৰু শত্ৰু, 7ম বিবাহ আৰু অংশীদাৰী, 8ম আয়ুস আৰু হঠাৎ পৰিৱৰ্তন, 9ম ভাগ্য আৰু ধৰ্ম, 10ম কৰ্ম, 11শ লাভ, 12শ খৰচ আৰু মোক্ষ। গ্ৰহে নিজে থকা ভাৱ আৰু অধিপতি হোৱা ভাৱবোৰক ৰং দিয়ে; তাৰ বল (উচ্চ, স্বক্ষেত্ৰ, নীচ) চালে সি কিমান ভাল ফল দিব পাৰে সেয়া বুজা যায়।</p> <h3>4. চলি থকা দশাটো চাওক</h3> <p>দশাই কয় <em>কেতিয়া</em>। মহাদশাৰ অধিপতি আৰু তাৰ ভিতৰত অন্তৰ্দশাৰ অধিপতি—এই গ্ৰহবোৰৰ ভাৱ এই সময়ছোৱাত সক্ৰিয় হয় — সেইবাবে একে ধৰণৰ কুণ্ডলী থকা দুজন মানুহৰ বছৰ বেলেগ হ'ব পাৰে।</p> <h3>5. দোষবোৰ প্ৰসংগ চাই বুজক</h3> <p>দোষ এটা পঢ়িবলগীয়া ধৰণ, ৰায় নহয়। মঙ্গল দোষৰ শাস্ত্ৰীয় খণ্ডন আছে; সাড়ে সাতি হ'ল সাড়ে সাত বছৰীয়া গোচৰ, যিটো সকলোৱে দুই-তিনিবাৰ পায়। দোষৰ প্ৰতিবেদনে পোৱা খণ্ডনবোৰৰ নাম দিয়ে।</p>",
    # EN: Create my janam kundali — free
    "fk.cta2": "মোৰ জন্মকুণ্ডলী বনাওক — বিনামূলীয়া",
    # EN: <h2>Frequently asked questions</h2>
    "fk.faq_h2": "<h2>সঘনাই সোধা প্ৰশ্ন</h2>",
    # EN: Rashi
    "varga.D1": "ৰাশি",
    # EN: Drekkana
    "varga.D3": "দ্ৰেক্কাণ",
    # EN: Saptamsa
    "varga.D7": "সপ্তাংশ",
    # EN: Navamsa
    "varga.D9": "নৱাংশ",
    # EN: Dashamsa
    "varga.D10": "দশাংশ",
    # EN: Dwadashamsa
    "varga.D12": "দ্বাদশাংশ",
    # EN: Not recommended
    "km.band0": "পৰামৰ্শযোগ্য নহয়",
    # EN: Acceptable
    "km.band1": "চলিব পৰা",
    # EN: Good
    "km.band2": "ভাল",
    # EN: Excellent
    "km.band3": "অতি উত্তম",
}

# app/seo_text.py FAQ["as"] — the seven free-kundali FAQ pairs (plain text)  [7]
SEO_FAQ = (
    # EN q: Is the kundali really free?
    # EN a: Yes. Casting the chart, the dashas, the divisional charts and the dosha check cost
    #       nothing, and you do not need to sign in to see them. Only the AI astrologer's answers
    #       beyond your free questions, and in-depth paid reports such as the Life Book, cost money.
    ("কুণ্ডলী সঁচাকৈয়ে বিনামূলীয়া নেকি?", "হয়। কুণ্ডলী বনোৱা, দশা, বিভাগীয় কুণ্ডলী আৰু দোষ পৰীক্ষা সকলোতে এপইচাও নালাগে, আৰু চাবলৈ ছাইন-ইন কৰাও লাগিব নোৱাৰে। কেৱল এআই জ্যোতিষীৰ বিনামূলীয়া প্ৰশ্নৰ বাহিৰৰ উত্তৰ আৰু জীৱন-পুথিৰ দৰে বিতং পেইড প্ৰতিবেদনত পইচা লাগে।"),
    # EN q: What details do I need?
    # EN a: Your date of birth, time of birth and place of birth. The place sets the latitude,
    #       longitude and time zone, which decide the Lagna (ascendant) and the house positions.
    ("মোক কি কি তথ্য লাগিব?", "আপোনাৰ জন্মৰ তাৰিখ, জন্মৰ সময় আৰু জন্মস্থান। স্থানে অক্ষাংশ, দ্ৰাঘিমাংশ আৰু সময় অঞ্চল ঠিক কৰে, যিয়ে লগ্ন আৰু ভাৱৰ স্থিতি নিৰ্ধাৰণ কৰে।"),
    # EN q: What if I don't know my exact birth time?
    # EN a: The chart is still cast, at 12:00 noon. The Moon sign and nakshatra are usually still
    #       right (unless the Moon changed sign or nakshatra that day), so Moon-based readings, Sade
    #       Sati and Kundali Milan stay useful — but the Lagna, the houses and Mangal Dosha need a
    #       reliable time. A time from a birth certificate or hospital record is best.
    ("জন্মৰ ঠিক সময় নাজানিলে কি হ'ব?", "তথাপি কুণ্ডলী বনোৱা হয়, দুপৰীয়া 12:00 বজাৰ সময়ত। চন্দ্ৰ ৰাশি আৰু নক্ষত্ৰ সাধাৰণতে শুদ্ধ হৈ থাকে (সেইদিনা চন্দ্ৰই ৰাশি বা নক্ষত্ৰ সলনি কৰা হ'লে বাদে), সেয়ে চন্দ্ৰভিত্তিক ফল, সাড়ে সাতি আৰু কুণ্ডলী মিলন কামত আহে — কিন্তু লগ্ন, ভাৱ আৰু মঙ্গল দোষৰ বাবে ভৰসাযোগ্য সময় লাগে। জন্ম প্ৰমাণপত্ৰ বা হাস্পতালৰ ৰেকৰ্ডৰ সময় সবাতোকৈ ভাল।"),
    # EN q: Which system do you use — Lahiri, KP, tropical?
    # EN a: Every chart is sidereal (Nirayana) with the Lahiri (Chitrapaksha) ayanamsa, whole-sign
    #       houses and Vimshottari dasha — the convention of most Indian almanacs and astrologers.
    #       Planet positions come from the Swiss Ephemeris.
    ("আপুনি কোনটো পদ্ধতি ব্যৱহাৰ কৰে — লাহিড়ী, কেপি নে সায়ন?", "প্ৰতিখন কুণ্ডলী নিৰয়ন, লাহিড়ী (চিত্ৰপক্ষ) অয়নাংশ, সম্পূৰ্ণ-ৰাশি ভাৱ আৰু বিংশোত্তৰী দশাৰে বনোৱা — বেছিভাগ ভাৰতীয় পঞ্জিকা আৰু জ্যোতিষীয়ে মানি চলা পদ্ধতি। গ্ৰহৰ স্থিতি সুইচ এফেমেৰিছৰ পৰা অহা।"),
    # EN q: Can I see my kundali in Hindi?
    # EN a: Yes. Switch the app to हिन्दी and the chart, planet and sign names, dashas and readings
    #       all appear in Hindi; the PDF can be downloaded in Hindi too.
    ("মই মোৰ কুণ্ডলী অসমীয়াত চাব পাৰিম নে?", "হয়। এপটো অসমীয়ালৈ সলনি কৰিলে কুণ্ডলী, গ্ৰহ আৰু ৰাশিৰ নাম, দশা আৰু ফল সকলো অসমীয়াত দেখা যাব; PDF ও অসমীয়াত ডাউনল'ড কৰিব পাৰি।"),
    # EN q: North Indian or South Indian chart?
    # EN a: Both. The same chart can be shown as the North Indian diamond chart (houses fixed, signs
    #       numbered) or the South Indian square chart (signs fixed), with one tap.
    ("উত্তৰ ভাৰতীয় নে দক্ষিণ ভাৰতীয় কুণ্ডলী?", "দুয়োটা। একেখন কুণ্ডলী এটা টিপতে উত্তৰ ভাৰতীয় হীৰাৰ আকৃতিৰ কুণ্ডলী (ভাৱ নিৰ্দিষ্ট, ৰাশি সংখ্যাৰে) বা দক্ষিণ ভাৰতীয় বৰ্গাকাৰ কুণ্ডলী (ৰাশি নিৰ্দিষ্ট) হিচাপে দেখুৱাব পাৰি।"),
    # EN q: Is this the same as a horoscope?
    # EN a: A janam kundali is the birth chart itself — the fixed map of the sky at your birth. A
    #       daily horoscope or rashifal is a short general forecast for everyone with the same Moon
    #       sign. Your kundali is personal; a rashifal is not.
    ("ই ৰাশিফলৰ দৰেই নেকি?", "জন্মকুণ্ডলী হ'ল জন্মৰ সময়ৰ আকাশৰ নিৰ্দিষ্ট নক্সা, অৰ্থাৎ জন্মপত্ৰিকা নিজেই। দৈনিক ৰাশিফল হ'ল একে চন্দ্ৰ ৰাশিৰ সকলোৰে বাবে এটা চমু সাধাৰণ ভৱিষ্যদ্বাণী। আপোনাৰ কুণ্ডলী ব্যক্তিগত; ৰাশিফল সেইদৰে নহয়।"),
)

# app/i18n.py CHROME["as"] — chrome shared by every server page: breadcrumb, footer links, disclaimer (HTML: write &amp;)  [10]
CHROME = {
    # EN: Home
    "home": "মুখ্য পৃষ্ঠা",
    # EN: Breadcrumb
    "breadcrumb": "পৃষ্ঠাৰ পথ",
    # EN: Share on WhatsApp
    "share": "হোৱাটছএপত শ্বেয়াৰ কৰক",
    # EN: Kathas
    "f_katha": "কথা",
    # EN: Terms &amp; Conditions
    "f_terms": "নিয়ম আৰু চৰ্তাৱলী",
    # EN: Privacy Policy
    "f_privacy": "গোপনীয়তা নীতি",
    # EN: Refund &amp; Cancellation
    "f_refund": "ধন-ঘূৰাই আৰু বাতিল",
    # EN: Contact Us
    "f_contact": "আমাৰ লগত যোগাযোগ কৰক",
    # EN: Feedback
    "f_feedback": "মতামত",
    # EN: Astrological readings are provided for guidance and entertainment. They are not medical,
    #     legal or financial advice.
    "disclaimer": "জ্যোতিষ শাস্ত্ৰৰ ভৱিষ্যদ্বাণী কেৱল পথ-প্ৰদৰ্শন আৰু মনোৰঞ্জনৰ বাবে দিয়া হৈছে। ই চিকিৎসা, আইনী বা বিত্তীয় পৰামৰ্শ নহয়।",
}

# app/stay_strip.py TEXT["as"] — the 'Stay in touch' strip at the foot of the pages  [8]
STAY_STRIP = {
    # EN: Stay in touch
    "head": "আমাৰ লগত যোগাযোগত থাকক",
    # EN: Get today's panchang on your phone every morning
    "push": "প্ৰতিদিনে ৰাতিপুৱা আপোনাৰ ফোনত আজিৰ পঞ্জিকা পাওক",
    # EN: Turning on…
    "busy": "চালু কৰি আছে…",
    # EN: Done — you will get it every morning.
    "on": "হৈ গ'ল — প্ৰতিদিনে ৰাতিপুৱা পাব।",
    # EN: Could not turn on alerts. Please try again.
    "err": "সতৰ্কবাৰ্তা চালু কৰিব নোৱাৰিলোঁ। অনুগ্ৰহ কৰি পুনৰ চেষ্টা কৰক।",
    # EN: Notifications are blocked for this site in your browser settings.
    "denied": "আপোনাৰ ব্ৰাউজাৰৰ ছেটিঙত এই চাইটৰ বাবে জাননী বন্ধ কৰি থোৱা আছে।",
    # EN: Join our WhatsApp channel
    "channel": "আমাৰ হোৱাটছএপ চেনেলত যোগ দিয়ক",
    # EN: Share this page on WhatsApp
    "share": "এই পৃষ্ঠাটো হোৱাটছএপত শ্বেয়াৰ কৰক",
}

# app/seo_city_names.py CITIES["as"] — the 114 cities as that language's newspapers spell them (key = URL slug)  [114]
CITY_NAMES = {
    # EN: New Delhi
    "new-delhi": "নতুন দিল্লী",
    # EN: Mumbai
    "mumbai": "মুম্বাই",
    # EN: Kolkata
    "kolkata": "কলকাতা",
    # EN: Chennai
    "chennai": "চেন্নাই",
    # EN: Bengaluru
    "bengaluru": "বেংগালুৰু",
    # EN: Hyderabad
    "hyderabad": "হায়দৰাবাদ",
    # EN: Ahmedabad
    "ahmedabad": "আহমেদাবাদ",
    # EN: Pune
    "pune": "পুনে",
    # EN: Jaipur
    "jaipur": "জয়পুৰ",
    # EN: Lucknow
    "lucknow": "লখনউ",
    # EN: Kanpur
    "kanpur": "কানপুৰ",
    # EN: Nagpur
    "nagpur": "নাগপুৰ",
    # EN: Indore
    "indore": "ইন্দোৰ",
    # EN: Bhopal
    "bhopal": "ভোপাল",
    # EN: Patna
    "patna": "পাটনা",
    # EN: Varanasi
    "varanasi": "বাৰাণসী",
    # EN: Prayagraj
    "prayagraj": "প্ৰয়াগৰাজ",
    # EN: Surat
    "surat": "সুৰাট",
    # EN: Vadodara
    "vadodara": "বদোদৰা",
    # EN: Chandigarh
    "chandigarh": "চণ্ডীগড়",
    # EN: Amritsar
    "amritsar": "অমৃতসৰ",
    # EN: Dehradun
    "dehradun": "দেৰাদুন",
    # EN: Haridwar
    "haridwar": "হৰিদ্বাৰ",
    # EN: Noida
    "noida": "নয়ডা",
    # EN: Gurugram
    "gurugram": "গুৰুগ্ৰাম",
    # EN: Bhubaneswar
    "bhubaneswar": "ভুবনেশ্বৰ",
    # EN: Guwahati
    "guwahati": "গুৱাহাটী",
    # EN: Ranchi
    "ranchi": "ৰাঁচী",
    # EN: Kochi
    "kochi": "কোচি",
    # EN: Visakhapatnam
    "visakhapatnam": "বিশাখাপত্তনম",
    # EN: Thane
    "thane": "থানে",
    # EN: Navi Mumbai
    "navi-mumbai": "নৱী মুম্বাই",
    # EN: Nashik
    "nashik": "নাসিক",
    # EN: Chhatrapati Sambhajinagar
    "chhatrapati-sambhajinagar": "ছত্ৰপতি সম্ভাজীনগৰ",
    # EN: Solapur
    "solapur": "শোলাপুৰ",
    # EN: Kolhapur
    "kolhapur": "কোলহাপুৰ",
    # EN: Amravati
    "amravati": "অমৰাৱতী",
    # EN: Shirdi
    "shirdi": "শিৰ্ডি",
    # EN: Rajkot
    "rajkot": "ৰাজকোট",
    # EN: Bhavnagar
    "bhavnagar": "ভাৱনগৰ",
    # EN: Jamnagar
    "jamnagar": "জামনগৰ",
    # EN: Gandhinagar
    "gandhinagar": "গান্ধীনগৰ",
    # EN: Dwarka
    "dwarka": "দ্বাৰকা",
    # EN: Somnath
    "somnath": "সোমনাথ",
    # EN: Jodhpur
    "jodhpur": "যোধপুৰ",
    # EN: Udaipur
    "udaipur": "উদয়পুৰ",
    # EN: Kota
    "kota": "কোটা",
    # EN: Ajmer
    "ajmer": "আজমীৰ",
    # EN: Bikaner
    "bikaner": "বিকানেৰ",
    # EN: Agra
    "agra": "আগ্ৰা",
    # EN: Ghaziabad
    "ghaziabad": "গাজিয়াবাদ",
    # EN: Meerut
    "meerut": "মীৰাট",
    # EN: Bareilly
    "bareilly": "বৰেলী",
    # EN: Aligarh
    "aligarh": "আলীগড়",
    # EN: Moradabad
    "moradabad": "মুৰাদাবাদ",
    # EN: Gorakhpur
    "gorakhpur": "গোৰক্ষপুৰ",
    # EN: Saharanpur
    "saharanpur": "সাহাৰণপুৰ",
    # EN: Ayodhya
    "ayodhya": "অযোধ্যা",
    # EN: Mathura
    "mathura": "মথুৰা",
    # EN: Vrindavan
    "vrindavan": "বৃন্দাবন",
    # EN: Jhansi
    "jhansi": "ঝাঁসি",
    # EN: Faridabad
    "faridabad": "ফৰিদাবাদ",
    # EN: Kurukshetra
    "kurukshetra": "কুৰুক্ষেত্ৰ",
    # EN: Ludhiana
    "ludhiana": "লুধিয়ানা",
    # EN: Jalandhar
    "jalandhar": "জালন্ধৰ",
    # EN: Patiala
    "patiala": "পাতিয়ালা",
    # EN: Rishikesh
    "rishikesh": "ঋষিকেশ",
    # EN: Shimla
    "shimla": "শিমলা",
    # EN: Jammu
    "jammu": "জম্মু",
    # EN: Srinagar
    "srinagar": "শ্ৰীনগৰ",
    # EN: Katra
    "katra": "কাটৰা",
    # EN: Gwalior
    "gwalior": "গোৱালিয়ৰ",
    # EN: Jabalpur
    "jabalpur": "জবলপুৰ",
    # EN: Ujjain
    "ujjain": "উজ্জয়িনী",
    # EN: Raipur
    "raipur": "ৰায়পুৰ",
    # EN: Bhilai
    "bhilai": "ভিলাই",
    # EN: Gaya
    "gaya": "গয়া",
    # EN: Bhagalpur
    "bhagalpur": "ভাগলপুৰ",
    # EN: Muzaffarpur
    "muzaffarpur": "মুজফ্ফৰপুৰ",
    # EN: Jamshedpur
    "jamshedpur": "জামশেদপুৰ",
    # EN: Dhanbad
    "dhanbad": "ধানবাদ",
    # EN: Deoghar
    "deoghar": "দেওঘৰ",
    # EN: Howrah
    "howrah": "হাওড়া",
    # EN: Asansol
    "asansol": "আসানসোল",
    # EN: Siliguri
    "siliguri": "শিলিগুড়ি",
    # EN: Cuttack
    "cuttack": "কটক",
    # EN: Puri
    "puri": "পুৰী",
    # EN: Coimbatore
    "coimbatore": "কোয়েম্বাটুৰ",
    # EN: Madurai
    "madurai": "মাদুৰাই",
    # EN: Tiruchirappalli
    "tiruchirappalli": "তিৰুচিৰাপল্লী",
    # EN: Salem
    "salem": "ছেলেম",
    # EN: Rameswaram
    "rameswaram": "ৰামেশ্বৰম",
    # EN: Thiruvananthapuram
    "thiruvananthapuram": "তিৰুৱনন্তপুৰম",
    # EN: Kozhikode
    "kozhikode": "কোজিকোড",
    # EN: Thrissur
    "thrissur": "ত্ৰিশূৰ",
    # EN: Kollam
    "kollam": "কোল্লাম",
    # EN: Kannur
    "kannur": "কান্নুৰ",
    # EN: Malappuram
    "malappuram": "মালাপ্পুৰম",
    # EN: Mysuru
    "mysuru": "মহীশূৰ",
    # EN: Mangaluru
    "mangaluru": "মেংগালুৰু",
    # EN: Hubballi
    "hubballi": "হুব্বালি",
    # EN: Warangal
    "warangal": "ৱাৰংগল",
    # EN: Vijayawada
    "vijayawada": "বিজয়ৱাডা",
    # EN: Tirupati
    "tirupati": "তিৰুপতি",
    # EN: Guntur
    "guntur": "গুণ্টুৰ",
    # EN: Panaji
    "panaji": "পানাজী",
    # EN: Shillong
    "shillong": "শ্বিলং",
    # EN: Imphal
    "imphal": "ইম্ফল",
    # EN: Agartala
    "agartala": "আগৰতলা",
    # EN: Gangtok
    "gangtok": "গ্যাংটক",
    # EN: Aizawl
    "aizawl": "আইজল",
    # EN: Kohima
    "kohima": "কোহিমা",
    # EN: Itanagar
    "itanagar": "ইটানগৰ",
    # EN: Puducherry
    "puducherry": "পুদুচেৰী",
}

# app/seo_city_names.py STATES["as"] — the states and union territories (key = English state name)  [32]
STATE_NAMES = {
    # EN: Andhra Pradesh
    "Andhra Pradesh": "অন্ধ্ৰ প্ৰদেশ",
    # EN: Arunachal Pradesh
    "Arunachal Pradesh": "অৰুণাচল প্ৰদেশ",
    # EN: Assam
    "Assam": "অসম",
    # EN: Bihar
    "Bihar": "বিহাৰ",
    # EN: Chandigarh
    "Chandigarh": "চণ্ডীগড়",
    # EN: Chhattisgarh
    "Chhattisgarh": "ছত্তিশগড়",
    # EN: Delhi
    "Delhi": "দিল্লী",
    # EN: Goa
    "Goa": "গোৱা",
    # EN: Gujarat
    "Gujarat": "গুজৰাট",
    # EN: Haryana
    "Haryana": "হৰিয়ানা",
    # EN: Himachal Pradesh
    "Himachal Pradesh": "হিমাচল প্ৰদেশ",
    # EN: Jammu and Kashmir
    "Jammu and Kashmir": "জম্মু আৰু কাশ্মীৰ",
    # EN: Jharkhand
    "Jharkhand": "ঝাৰখণ্ড",
    # EN: Karnataka
    "Karnataka": "কৰ্ণাটক",
    # EN: Kerala
    "Kerala": "কেৰালা",
    # EN: Madhya Pradesh
    "Madhya Pradesh": "মধ্য প্ৰদেশ",
    # EN: Maharashtra
    "Maharashtra": "মহাৰাষ্ট্ৰ",
    # EN: Manipur
    "Manipur": "মণিপুৰ",
    # EN: Meghalaya
    "Meghalaya": "মেঘালয়",
    # EN: Mizoram
    "Mizoram": "মিজোৰাম",
    # EN: Nagaland
    "Nagaland": "নাগালেণ্ড",
    # EN: Odisha
    "Odisha": "ওড়িশা",
    # EN: Puducherry
    "Puducherry": "পুদুচেৰী",
    # EN: Punjab
    "Punjab": "পঞ্জাব",
    # EN: Rajasthan
    "Rajasthan": "ৰাজস্থান",
    # EN: Sikkim
    "Sikkim": "চিকিম",
    # EN: Tamil Nadu
    "Tamil Nadu": "তামিলনাডু",
    # EN: Telangana
    "Telangana": "তেলেংগানা",
    # EN: Tripura
    "Tripura": "ত্ৰিপুৰা",
    # EN: Uttar Pradesh
    "Uttar Pradesh": "উত্তৰ প্ৰদেশ",
    # EN: Uttarakhand
    "Uttarakhand": "উত্তৰাখণ্ড",
    # EN: West Bengal
    "West Bengal": "পশ্চিমবংগ",
}

# app/astro/choghadiya.py CHOGHADIYA_INFO["as"] — one-line description of each of the seven choghadiya slots  [7]
CHOGHADIYA_DESC = {
    # EN: Best time for all ceremonies, investments, agreements, and starting important endeavors.
    "Amrit": "সকলো অনুষ্ঠান, বিনিয়োগ, চুক্তি আৰু গুৰুত্বপূৰ্ণ কাম আৰম্ভ কৰিবলৈ আটাইতকৈ ভাল সময়।",
    # EN: Highly auspicious for ceremonies, religious rituals, education, and purchasing property.
    "Shubh": "অনুষ্ঠান, ধৰ্মীয় কৰ্ম, শিক্ষা আৰু সম্পত্তি কিনিবলৈ অতি শুভ।",
    # EN: Favorable for business, trade, financial transactions, launching products, and interviews.
    "Labh": "ব্যৱসায়, বাণিজ্য, আৰ্থিক লেনদেন, নতুন সামগ্ৰী উন্মোচন আৰু সাক্ষাৎকাৰৰ বাবে অনুকূল।",
    # EN: Neutral. Excellent for journeys, travel, vehicle purchases, and shifting places.
    "Char": "মধ্যম। যাত্ৰা, ভ্ৰমণ, বাহন কিনা আৰু স্থান সলনি কৰিবলৈ উত্তম।",
    # EN: Inauspicious. Avoid medical procedures or conflict. Only suitable for competitive sports
    #     or defeating rivals.
    "Rog": "অশুভ। চিকিৎসা প্ৰক্ৰিয়া বা বিবাদ এৰাই চলক। প্ৰতিযোগিতামূলক খেল বা প্ৰতিদ্বন্দ্বীক পৰাস্ত কৰাৰ বাবেহে উপযুক্ত।",
    # EN: Inauspicious. Ruled by Saturn; causes delays and setbacks. Avoid new ventures or signing
    #     documents.
    "Kaal": "অশুভ। শনিৰ অধীন; পলম আৰু বাধা-বিঘিনি ঘটায়। নতুন উদ্যোগ বা নথিপত্ৰত চহী কৰা এৰাই চলক।",
    # EN: Inauspicious. Causes restlessness and anxiety. Favorable only for government filings or
    #     official duties.
    "Udveg": "অশুভ। অস্থিৰতা আৰু উদ্বেগ ঘটায়। চৰকাৰী দাখিলা বা চাকৰিৰ কামৰ বাবেহে অনুকূল।",
}

# ----------------------------------------------------------------------------
# rashifal  /rashifal and /rashifal/<sign>
# ----------------------------------------------------------------------------

# app/rashifal_text.py TEXT["as"] — page text of /rashifal and /rashifal/<sign>  [63]
RASHIFAL_TEXT = {
    # EN: {house} house
    # keep: {house}
    "house_short": "{house} ভাৱ",
    # EN: (retrograde)
    "rx": " (বক্ৰী)",
    # EN: Moon
    "planet.Moon": "চন্দ্ৰ",
    # EN: Saturn
    "planet.Saturn": "শনি",
    # EN: Jupiter
    "planet.Jupiter": "বৃহস্পতি",
    # EN: Rahu
    "planet.Rahu": "ৰাহু",
    # EN: Ketu
    "planet.Ketu": "কেতু",
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
    "crumb_root": "ৰাশিফল",
    # EN: hi
    "sub_lang": 'as',
    # EN: {name} Rashifal Today, {date_short} — {english} Daily Horoscope | {brand}
    # keep: {brand} {local}
    # may also use: {date_short} {date}
    "s.title": "{local} ৰাশিফল আজি, {date_short} — আজিৰ দৈনিক ৰাশিফল | {brand}",
    # EN: {name} ({english} Moon sign) rashifal for {weekday}, {date}: the Moon transits your
    #     {house} house — {tone_lower}. Plus Saturn, Jupiter and Rahu–Ketu transits, Sade Sati
    #     status and today's tithi, computed from the sidereal sky.
    # keep: {date} {house} {local} {tone} {weekday}
    "s.desc": "{local} ৰাশিৰ {weekday}, {date} তাৰিখৰ ৰাশিফল: চন্দ্ৰ আপোনাৰ ৰাশিৰ পৰা {house} ভাৱত — {tone}। লগতে শনি, বৃহস্পতি আৰু ৰাহু-কেতুৰ গোচৰ, সাড়ে সাতিৰ অৱস্থা আৰু আজিৰ তিথি, নিৰয়ন গণনাৰে।",
    # EN: {name} Rashifal Today — {english} Daily Horoscope
    # keep: {local}
    "s.h1": "{local} ৰাশিৰ আজিৰ ৰাশিফল",
    # EN: आज का {name_hi} राशिफल
    # may also use: {local}
    "s.sub": "{local} ৰাশি · দৈনিক ৰাশিফল",
    # EN: the Moon is in your {house} house from {name}.
    # keep: {house}
    "s.summary": "চন্দ্ৰ আপোনাৰ ৰাশিৰ পৰা {house} ভাৱত আছে।",
    # EN: About {name} rashi — traits, nakshatras and name letters
    # keep: {local}
    "s.about_rashi": "{local} ৰাশি — স্বভাৱ, নক্ষত্ৰ আৰু নামৰ আদ্যক্ষৰ",
    # EN: Today's Moon transit (Chandra gochar)
    "moon.head": "আজিৰ চন্দ্ৰ গোচৰ",
    # EN: The Moon is in {sign} all day — your {house} house.
    # keep: {house} {sign}
    "moon.allday": "আজি দিনটোত চন্দ্ৰ {sign} ৰাশিত — আপোনাৰ {house} ভাৱত।",
    # EN: <strong>Until {time} IST:</strong> the Moon is in {sign} — your {house} house.
    # keep: {house} {sign} {time}
    "moon.until": "<strong>{time}লৈকে:</strong> চন্দ্ৰ {sign} ৰাশিত — আপোনাৰ {house} ভাৱত।",
    # EN: <strong>From {time} IST:</strong> the Moon enters {sign} — your {house} house.
    # keep: {house} {sign} {time}
    "moon.from": "<strong>{time}ৰ পৰা:</strong> চন্দ্ৰই {sign} ৰাশিত প্ৰৱেশ কৰে — আপোনাৰ {house} ভাৱত।",
    # EN: <p>The Moon changes sign during the day, so the day reads in two parts.</p>
    "moon.two": "<p>আজি দিনটোৰ ভিতৰতে চন্দ্ৰই ৰাশি সলনি কৰে, গতিকে দিনটো দুটা ভাগত পঢ়ক।</p>",
    # EN: The longer backdrop: slow transits
    "back.head": "দীঘলীয়া পটভূমি: লেহেমীয়া গ্ৰহৰ গোচৰ",
    # EN: <p>These planets stay in one sign for months or years, so they set the background against
    #     which each day plays out.</p>
    "back.intro": "<p>এই গ্ৰহবোৰ মাহৰ পিছত মাহ বা বছৰৰ পিছত বছৰ একেটা ৰাশিতে থাকে, সেয়ে প্ৰতিদিনৰ ঘটনাৰ পটভূমি এইবোৰেই গঢ়ি তোলে।</p>",
    # EN: {sign}{rx} · {house} house
    # keep: {house} {rx} {sign}
    "back.where": "{sign}{rx} · {house} ভাৱ",
    # EN: first (rising)
    "phase.1": "প্ৰথম (আৰম্ভণি)",
    # EN: second (peak)
    "phase.2": "দ্বিতীয় (চূড়ান্ত)",
    # EN: third (setting)
    "phase.3": "তৃতীয় (শেষৰ)",
    # EN: <strong>Sade Sati is running</strong> — the {phase} phase. It is a slow, disciplining
    #     period rather than something to fear; steady routine, service and patience make it
    #     lighter.
    # keep: {phase}
    "sade.running": "<strong>সাড়ে সাতি চলি আছে</strong> — {phase} পৰ্যায়। ই ভয় কৰিবলগীয়া একো নহয়, বৰং লাহে লাহে শৃংখলা শিকোৱা সময়; নিয়মীয়া দিনচৰ্যা, সেৱা আৰু ধৈৰ্যই ইয়াক পাতল কৰে।",
    # EN: <strong>No Sade Sati</strong>, but Saturn's Dhaiya is running (see above).
    "sade.dhaiya": "<strong>সাড়ে সাতি নাই</strong>, কিন্তু শনিৰ আড়াই বছৰীয়া প্ৰভাৱ (ঢৈয়া) চলি আছে (ওপৰত চাওক)।",
    # EN: <strong>No Sade Sati</strong> — Saturn is not in the 12th, 1st or 2nd from your sign.
    "sade.none": "<strong>সাড়ে সাতি নাই</strong> — শনি আপোনাৰ ৰাশিৰ পৰা দ্বাদশ, প্ৰথম বা দ্বিতীয় ভাৱত নাই।",
    # EN: <h2>Today's Panchang</h2><p>At sunrise in New Delhi it is <strong>{paksha}
    #     {tithi}</strong> tithi with the Moon in <strong>{nakshatra}</strong> nakshatra. Rahu Kaal,
    #     sunrise and the full almanac are on <a href="/panchang">today's Panchang</a>.</p>
    # keep: {nakshatra} {tithi}
    # may also use: {paksha_full} {paksha}
    "panchang": "<h2>আজিৰ পঞ্জিকা</h2><p>নতুন দিল্লীত সূৰ্যোদয়ৰ সময়ত <strong>{paksha} {tithi}</strong> তিথি, চন্দ্ৰ <strong>{nakshatra}</strong> নক্ষত্ৰত। ৰাহুকাল, সূৰ্যোদয় আৰু সম্পূৰ্ণ পঞ্জিকা <a href=\"/panchang\">আজিৰ পঞ্জিকাত</a> চাওক।</p>",
    # EN: <p class="note">This rashifal is read from your Moon sign alone — the same for everyone
    #     born with the Moon in that sign. A personal reading uses your full birth chart: the
    #     ascendant, your running dasha and the ashtakavarga strength of each transit. Not sure of
    #     your Moon sign (rashi)? It is the first thing your free kundali shows — it is usually not
    #     your Western sun sign.</p>
    "personal": "<p class=\"note\">এই ৰাশিফল কেৱল আপোনাৰ চন্দ্ৰ ৰাশিৰ পৰা পঢ়া — সেই ৰাশিত চন্দ্ৰ লৈ জন্ম হোৱা সকলোৰে বাবে একে। ব্যক্তিগত ফল চোৱা হয় আপোনাৰ সম্পূৰ্ণ জন্মকুণ্ডলীৰ পৰা: লগ্ন, চলি থকা দশা আৰু প্ৰতিটো গোচৰৰ অষ্টকবৰ্গৰ বল। নিজৰ চন্দ্ৰ ৰাশি নাজানেনে? বিনামূলীয়া কুণ্ডলীত আটাইতকৈ আগতে সেইটোৱেই দেখা যায় — সাধাৰণতে এইটো পাশ্চাত্য মতৰ সূৰ্য ৰাশি নহয়।</p>",
    # EN: Get your free kundali — then ask a question about your own chart
    "cta": "বিনামূলীয়া কুণ্ডলী বনাওক — তাৰ পিছত নিজৰ কুণ্ডলীৰ বিষয়ে প্ৰশ্ন সোধক",
    # EN: Today's Rashifal for every sign
    "signs.head": "সকলো ৰাশিৰ আজিৰ ৰাশিফল",
    # EN: More free tools
    "more.head": "আৰু বিনামূলীয়া সেৱা",
    # EN: <h2>How this is calculated</h2><p>Planet positions are computed for today (IST) with the
    #     Swiss Ephemeris in the sidereal zodiac (Lahiri ayanamsa) — the same positions our kundali
    #     and panchang use. Houses are counted from your Moon sign, as in classical gochar. Which
    #     houses are favourable follows the scheme of Varahamihira's Brihat Samhita (ch. 104) and
    #     Mantreswara's Phaladeepika (ch. 26): the Moon is favourable in the 1st, 3rd, 6th, 7th,
    #     10th and 11th; Saturn, Rahu and Ketu in the 3rd, 6th and 11th; Jupiter in the 2nd, 5th,
    #     7th, 9th and 11th.</p>
    "method": "<h2>কেনেকৈ গণনা কৰা হয়</h2><p>আজিৰ (ভাৰতীয় সময়) গ্ৰহৰ স্থিতি সুইচ এফেমেৰিছেৰে নিৰয়ন ৰাশিচক্ৰত (লাহিড়ী অয়নাংশ) গণনা কৰা হৈছে — আমাৰ কুণ্ডলী আৰু পঞ্জিকাতো একেটা স্থিতিয়েই ব্যৱহাৰ হয়। শাস্ত্ৰীয় গোচৰৰ নিয়মত ভাৱ গণনা কৰা হয় আপোনাৰ চন্দ্ৰ ৰাশিৰ পৰা। কোনটো ভাৱ শুভ, সেয়া বৰাহমিহিৰৰ বৃহৎসংহিতা (অধ্যায় 104) আৰু মন্ত্ৰেশ্বৰৰ ফলদীপিকা (অধ্যায় 26) অনুসৰি: চন্দ্ৰ 1, 3, 6, 7, 10 আৰু 11 নং ভাৱত শুভ; শনি, ৰাহু আৰু কেতু 3, 6 আৰু 11 নং ভাৱত; বৃহস্পতি 2, 5, 7, 9 আৰু 11 নং ভাৱত।</p>",
    # EN: Aaj Ka Rashifal, {date_short} — Today's Horoscope for All 12 Signs | {brand}
    # keep: {brand}
    # may also use: {date_short} {date}
    "i.title": "আজিৰ ৰাশিফল, {date_short} — 12 টা ৰাশিৰ দৈনিক ৰাশিফল | {brand}",
    # EN: Today's rashifal for {weekday}, {date}: daily horoscope for all 12 Moon signs from Mesh to
    #     Meen — Moon transit, Saturn, Jupiter and Rahu, and Sade Sati, computed from the sidereal
    #     sky.
    # keep: {date} {weekday}
    "i.desc": "{weekday}, {date} তাৰিখৰ ৰাশিফল: মেষৰ পৰা মীনলৈ — 12 টা চন্দ্ৰ ৰাশিৰ দৈনিক ৰাশিফল, চন্দ্ৰ গোচৰ, শনি, বৃহস্পতি আৰু ৰাহুৰ প্ৰভাৱ আৰু সাড়ে সাতি, নিৰয়ন গণনাৰে।",
    # EN: Today's Rashifal — Daily Horoscope
    "i.h1": "আজিৰ ৰাশিফল",
    # EN: आज का राशिफल — सभी 12 राशियाँ
    "i.sub": "সকলো 12 টা ৰাশিৰ দৈনিক ৰাশিফল",
    # EN: <p>Rashifal is read from your <strong>Moon sign</strong> (rashi). {moon_text} Saturn is in
    #     {sat_sign}, so Sade Sati is running for {sade_names}.</p>
    # keep: {moon_text} {sade_names} {sat_sign}
    "i.intro": "<p>ৰাশিফল পঢ়া হয় আপোনাৰ <strong>চন্দ্ৰ ৰাশি</strong>ৰ পৰা। {moon_text} শনি এতিয়া {sat_sign} ৰাশিত, সেয়ে {sade_names} ৰাশিৰ সাড়ে সাতি চলি আছে।</p>",
    # EN: The Moon is in {now} until {time} IST, then in {next}. The table shows the position for
    #     most of the day.
    # keep: {next} {now} {time}
    "i.moon_two": "{time}লৈকে চন্দ্ৰ {now} ৰাশিত, তাৰ পিছত {next} ৰাশিত। তালিকাত দিনটোৰ বেছিভাগ সময়ৰ স্থিতি দেখুওৱা হৈছে।",
    # EN: The Moon is in {now} all day.
    # keep: {now}
    "i.moon_one": "আজি দিনটোত চন্দ্ৰ {now} ৰাশিত।",
    # EN: {name} <small>{english}</small>
    # keep: {local}
    "i.name": "{local}",
    # EN: <small>Sade Sati</small>
    "i.sade": "<small>সাড়ে সাতি</small>",
    # EN: <tr><th>Sign</th><th>Moon in your</th><th>Today</th></tr>
    "i.head_row": "<tr><th>ৰাশি</th><th>চন্দ্ৰ আপোনাৰ</th><th>আজি</th></tr>",
    # EN: Sign not found
    "nf.title": "ৰাশি পোৱা নগ'ল",
    # EN: <h1>Sign not found</h1><p>There is no rashi called “{slug}”. Pick your Moon sign
    #     below.</p>
    # keep: {slug}
    "nf.body": "<h1>ৰাশি পোৱা নগ'ল</h1><p>“{slug}” নামৰ কোনো ৰাশি নাই। তলত আপোনাৰ চন্দ্ৰ ৰাশি বাছি লওক।</p>",
    # EN: 1st
    "house.1": "প্ৰথম",
    # EN: 2nd
    "house.2": "দ্বিতীয়",
    # EN: 3rd
    "house.3": "তৃতীয়",
    # EN: 4th
    "house.4": "চতুৰ্থ",
    # EN: 5th
    "house.5": "পঞ্চম",
    # EN: 6th
    "house.6": "ষষ্ঠ",
    # EN: 7th
    "house.7": "সপ্তম",
    # EN: 8th
    "house.8": "অষ্টম",
    # EN: 9th
    "house.9": "নৱম",
    # EN: 10th
    "house.10": "দশম",
    # EN: 11th
    "house.11": "একাদশ",
    # EN: 12th
    "house.12": "দ্বাদশ",
}

# app/rashifal_text.py MORE_LINKS["as"] — 'More free tools' links: keep every href, translate the text; the first href is '{twin:en}' (this page in English)  [6]
RASHIFAL_MORE_LINKS = (
    # EN href: {twin:en}
    # EN text: Read in English
    ("{twin:en}", "ইংৰাজীত পঢ়ক"),
    # EN href: /panchang
    # EN text: Today's Panchang
    ("/panchang", "আজিৰ পঞ্জিকা"),
    # EN href: /rahu-kaal
    # EN text: Rahu Kaal today
    ("/rahu-kaal", "আজিৰ ৰাহুকাল"),
    # EN href: /choghadiya
    # EN text: Choghadiya today
    ("/choghadiya", "আজিৰ চৌঘড়িয়া"),
    # EN href: /kundali-milan
    # EN text: Kundali Milan
    ("/kundali-milan", "কুণ্ডলী মিলন"),
    # EN href: /vrat-tyohar
    # EN text: Today's vrat & festivals
    ("/vrat-tyohar", "আজিৰ ব্ৰত আৰু উৎসৱ"),
)

# app/rashifal_text.py TONE_LABEL["as"] — the three day tones (keys good / mixed / easy)  [3]
RASHIFAL_TONE_LABEL = {
    # EN: Favourable day
    "good": "অনুকূল দিন",
    # EN: Mixed day
    "mixed": "মিশ্ৰ দিন",
    # EN: Take it easy
    "easy": "সংযমৰ দিন",
}

# app/rashifal_text.py MOON_HOUSE["as"] — Moon transit through houses 1-12 (key = house number)  [12]
RASHIFAL_MOON_HOUSE = {
    # EN: The Moon moves through your own sign today (Janma Chandra). Classical texts read this as a
    #     day of comfort and good spirits — good food, warm company and a clear sense of yourself. A
    #     good day to look after your own needs and begin small, personal things.
    1: "আজি চন্দ্ৰ আপোনাৰ নিজৰ ৰাশিত আছে (জন্ম চন্দ্ৰ)। শাস্ত্ৰ অনুসৰি এইটো আৰাম আৰু ভাল মনৰ দিন — ভাল খাদ্য, আপোনজনৰ সঙ্গ আৰু নিজৰ বিষয়ে স্পষ্ট ধাৰণা। নিজৰ প্ৰয়োজনৰ যত্ন লোৱা আৰু সৰু ব্যক্তিগত কাম আৰম্ভ কৰাৰ বাবে ভাল দিন।",
    # EN: The Moon is in your 2nd house today. Tradition asks for care with money and words —
    #     expenses can creep up and small misunderstandings arise easily. Keep spending planned and
    #     speak gently at home; routine work goes fine.
    2: "আজি চন্দ্ৰ আপোনাৰ দ্বিতীয় ভাৱত আছে। পৰম্পৰাই ধন আৰু কথাত সাৱধান হ'বলৈ কয় — খৰচ লাহে লাহে বাঢ়িব পাৰে আৰু সৰু ভুল বুজাবুজি সহজে হ'ব পাৰে। খৰচ পৰিকল্পিত ৰাখক আৰু ঘৰত নম্ৰভাৱে কথা পাতক; নিয়মীয়া কাম ভালদৰেই চলিব।",
    # EN: The Moon in your 3rd house is a favourable transit. Courage and initiative are high,
    #     effort brings results, and contact with siblings, friends and neighbours goes well. A good
    #     day for short trips, calls and pushing a pending task over the line.
    3: "আপোনাৰ তৃতীয় ভাৱত চন্দ্ৰ থকাটো অনুকূল গোচৰ। সাহস আৰু উদ্যম বেছি, চেষ্টাই ফল দিয়ে, আৰু ভাই-ভনী, বন্ধু আৰু ওচৰ-চুবুৰীয়াৰ লগত সম্পৰ্ক ভাল হয়। চুটি যাত্ৰা, ফোন কৰা আৰু বাকী থকা কাম শেষ কৰিবলৈ ভাল দিন।",
    # EN: The Moon in your 4th house can leave the mind a little unsettled — home matters or travel
    #     may feel tiring. Keep the day simple, avoid arguments at home and give yourself some quiet
    #     time; the mood lifts as the Moon moves on.
    4: "আপোনাৰ চতুৰ্থ ভাৱত চন্দ্ৰ থাকিলে মনটো অলপ অস্থিৰ হ'ব পাৰে — ঘৰৰ কথা বা যাত্ৰাই ক্লান্ত কৰিব পাৰে। দিনটো সৰল ৰাখক, ঘৰত তৰ্ক-বিতৰ্ক এৰাই চলক আৰু নিজকে অলপ নিৰিবিলিকৈ সময় দিয়ক; চন্দ্ৰ আগবঢ়িলে মনটো পাতল হৈ যাব।",
    # EN: The Moon in your 5th house is a mixed transit. Plans may meet small hurdles and the mind
    #     can swing between ideas. Avoid speculative decisions; study, creative work and time with
    #     children are better uses of the day.
    5: "আপোনাৰ পঞ্চম ভাৱত চন্দ্ৰ থকাটো মিশ্ৰ গোচৰ। পৰিকল্পনাত সৰু বাধা আহিব পাৰে আৰু মন নানা চিন্তাত দুলিব পাৰে। অনুমানভিত্তিক সিদ্ধান্ত এৰাই চলক; অধ্যয়ন, সৃজনশীল কাম আৰু সন্তানৰ লগত সময় কটোৱাটো দিনটোৰ বাবে ভাল।",
    # EN: The Moon in your 6th house is one of its best transits. Classical texts promise success
    #     over rivals and obstacles, and the energy to clear a backlog. A good day for competitive
    #     work, settling pending issues and steady routines.
    6: "আপোনাৰ ষষ্ঠ ভাৱত চন্দ্ৰ থকাটো তাৰ আটাইতকৈ ভাল গোচৰবোৰৰ এটা। শাস্ত্ৰই শত্ৰু আৰু বাধাৰ ওপৰত জয় আৰু জমা কাম শেষ কৰাৰ শক্তিৰ প্ৰতিশ্ৰুতি দিয়ে। প্ৰতিযোগিতামূলক কাম, বাকী থকা সমস্যা সমাধান আৰু নিয়মীয়া কামৰ বাবে ভাল দিন।",
    # EN: The Moon in your 7th house favours partnership and company. Time with your spouse or
    #     partner, meetings and agreements tend to go smoothly, with comfort and good food. A good
    #     day to reach out and work together.
    7: "আপোনাৰ সপ্তম ভাৱত চন্দ্ৰ থকাই অংশীদাৰী আৰু সঙ্গৰ বাবে অনুকূল। স্বামী-স্ত্ৰী বা সঙ্গীৰ লগত সময়, সভা আৰু চুক্তি সহজে আগবাঢ়ে, আৰাম আৰু ভাল খাদ্যৰ সৈতে। যোগাযোগ কৰি লগ লাগি কাম কৰাৰ বাবে ভাল দিন।",
    # EN: The Moon is in your 8th house — the period known as Chandrashtama. Tradition advises
    #     against starting important new things today; unexpected delays are more likely and the
    #     mind can feel anxious. Keep a margin in your schedule, stick to familiar work and be
    #     gentle with yourself — it passes within two to three days.
    8: "আজি চন্দ্ৰ আপোনাৰ অষ্টম ভাৱত আছে — যাক চন্দ্ৰাষ্টম বোলা হয়। পৰম্পৰাই আজি গুৰুত্বপূৰ্ণ নতুন কাম আৰম্ভ নকৰিবলৈ পৰামৰ্শ দিয়ে; অপ্ৰত্যাশিত পলম হোৱাৰ সম্ভাৱনা বেছি আৰু মন উদ্বিগ্ন হ'ব পাৰে। সময়সূচীত অলপ ঠাই ৰাখক, চিনাকি কামতে লাগি থাকক আৰু নিজৰ প্ৰতি নম্ৰ হওক — দুই-তিনি দিনৰ ভিতৰতে এইটো পাৰ হৈ যায়।",
    # EN: The Moon in your 9th house is a mixed transit. Plans may need extra effort and you may
    #     feel tired or distracted. Prayer, reading and time with elders or teachers suit the day
    #     better than big new ventures.
    9: "আপোনাৰ নৱম ভাৱত চন্দ্ৰ থকাটো মিশ্ৰ গোচৰ। পৰিকল্পনাত অতিৰিক্ত চেষ্টা লাগিব পাৰে আৰু আপুনি ক্লান্ত বা অন্যমনস্ক অনুভৱ কৰিব পাৰে। প্ৰাৰ্থনা, পঢ়া আৰু বয়োজ্যেষ্ঠ বা শিক্ষকৰ সৈতে সময় কটোৱাটো ডাঙৰ নতুন উদ্যোগতকৈ দিনটোৰ বাবে বেছি উপযুক্ত।",
    # EN: The Moon in your 10th house supports work and reputation. Tasks get done, seniors are
    #     receptive and effort is noticed. A good day to present your work, take a professional step
    #     or finish something visible.
    10: "আপোনাৰ দশম ভাৱত চন্দ্ৰ থকাই কাম আৰু সুনামৰ সহায়ক। কাম সম্পন্ন হয়, ওপৰৱালাই কথা শুনে আৰু চেষ্টাক চিনি পায়। নিজৰ কাম দাঙি ধৰিবলৈ, বৃত্তিগত পদক্ষেপ ল'বলৈ বা দৃশ্যমান কিবা শেষ কৰিবলৈ ভাল দিন।",
    # EN: The Moon in your 11th house — the house of gains — is a very favourable transit. Expect
    #     support from friends, good news and the fruit of earlier effort. A good day for
    #     networking, making requests and celebrating with others.
    11: "আপোনাৰ একাদশ ভাৱত — লাভৰ ভাৱত — চন্দ্ৰ থকাটো অতি অনুকূল গোচৰ। বন্ধুৰ সহায়, শুভ খবৰ আৰু আগৰ চেষ্টাৰ ফল পোৱাৰ আশা কৰক। যোগাযোগ বঢ়াবলৈ, অনুৰোধ জনাবলৈ আৰু আনৰ লগত আনন্দ কৰিবলৈ ভাল দিন।",
    # EN: The Moon in your 12th house can bring extra expenses and a tired, inward mood. Avoid
    #     overspending and late nights; the day suits rest, prayer, charity and finishing old work
    #     rather than starting new.
    12: "আপোনাৰ দ্বাদশ ভাৱত চন্দ্ৰ থাকিলে অতিৰিক্ত খৰচ আৰু ক্লান্ত, অন্তৰ্মুখী মন আহিব পাৰে। অত্যধিক খৰচ আৰু দেৰিলৈকে জগাই থকাটো এৰাই চলক; দিনটো নতুন কাম আৰম্ভ কৰাতকৈ জিৰণি, প্ৰাৰ্থনা, দান আৰু পুৰণি কাম শেষ কৰিবলৈ উপযুক্ত।",
}

# app/rashifal_text.py SATURN_HOUSE["as"] — Saturn transit through houses 1-12  [12]
RASHIFAL_SATURN_HOUSE = {
    # EN: Saturn is passing over your Moon sign — the peak phase of Sade Sati. It rewards patience,
    #     routine and honest effort; take on a little less and finish what you start.
    1: "শনি আপোনাৰ চন্দ্ৰ ৰাশিৰ ওপৰেদি পাৰ হৈছে — সাড়ে সাতিৰ চূড়ান্ত পৰ্যায়। ই ধৈৰ্য, নিয়ম আৰু সৎ চেষ্টাক পুৰস্কৃত কৰে; অলপ কম কাম হাতত লওক আৰু আৰম্ভ কৰা কাম শেষ কৰক।",
    # EN: Saturn is in your 2nd — the last phase of Sade Sati. Be measured with spending and with
    #     words at home; the pressure is easing.
    2: "শনি আপোনাৰ দ্বিতীয় ভাৱত — সাড়ে সাতিৰ শেষৰ পৰ্যায়। খৰচ আৰু ঘৰৰ কথাত সংযত হওক; চাপ কমি আহিছে।",
    # EN: Saturn in your 3rd is one of its best positions — steady effort pays, courage grows and
    #     long-running work gains traction.
    3: "তৃতীয় ভাৱত শনি থকাটো তাৰ আটাইতকৈ ভাল স্থিতিবোৰৰ এটা — স্থিৰ চেষ্টাই ফল দিয়ে, সাহস বাঢ়ে আৰু দীঘলীয়া কামে গতি পায়।",
    # EN: Saturn in your 4th (Dhaiya, Kantaka Shani) can make home life and peace of mind feel
    #     heavier; keep routines simple and handle family matters calmly.
    4: "চতুৰ্থ ভাৱত শনি (ঢৈয়া, কণ্টক শনি) থাকিলে ঘৰুৱা জীৱন আৰু মনৰ শান্তি অলপ ভাৰী অনুভৱ হ'ব পাৰে; নিয়ম সৰল ৰাখক আৰু পৰিয়ালৰ কথা শান্তভাৱে সামৰক।",
    # EN: Saturn in your 5th asks for patience with plans, studies and children's matters — slow and
    #     careful beats quick.
    5: "পঞ্চম ভাৱত শনিয়ে পৰিকল্পনা, অধ্যয়ন আৰু সন্তানৰ কথাত ধৈৰ্য বিচাৰে — লাহে লাহে আৰু সাৱধানে কৰাটো খৰখেদাতকৈ ভাল।",
    # EN: Saturn in your 6th works in your favour — discipline wins over rivals and backlog, and
    #     hard work gets noticed.
    6: "ষষ্ঠ ভাৱত শনি আপোনাৰ পক্ষে কাম কৰে — শৃংখলাই শত্ৰু আৰু জমা কামৰ ওপৰত জয় লাভ কৰে, আৰু কঠোৰ পৰিশ্ৰম চকুত পৰে।",
    # EN: Saturn in your 7th puts partnerships in a slow, serious light — clear agreements and
    #     patience help.
    7: "সপ্তম ভাৱত শনিয়ে অংশীদাৰীক লেহেমীয়া আৰু গভীৰ ৰূপত দেখুৱায় — স্পষ্ট চুক্তি আৰু ধৈৰ্যই সহায় কৰে।",
    # EN: Saturn in your 8th (Dhaiya, Ashtama Shani) is a time to avoid shortcuts and keep a margin
    #     for delays.
    8: "অষ্টম ভাৱত শনি (ঢৈয়া, অষ্টম শনি) থাকিলে চুটি পথ এৰাই চলিব লাগে আৰু পলম হ'ব পাৰে বুলি অলপ সময় ৰাখিব লাগে।",
    # EN: Saturn in your 9th can slow luck and long journeys; respect for elders and steady duty
    #     keep things on track.
    9: "নৱম ভাৱত শনিয়ে ভাগ্য আৰু দীঘলীয়া যাত্ৰা লেহেমীয়া কৰিব পাৰে; বয়োজ্যেষ্ঠৰ প্ৰতি সন্মান আৰু স্থিৰ কৰ্তব্যই কামবোৰ ঠিকে ৰাখে।",
    # EN: Saturn in your 10th brings responsibility at work — a heavier load, but sincere effort
    #     builds a lasting reputation.
    10: "দশম ভাৱত শনিয়ে কামত দায়িত্ব আনে — বোজা অলপ বেছি, কিন্তু আন্তৰিক চেষ্টাই স্থায়ী সুনাম গঢ়ি তোলে।",
    # EN: Saturn in your 11th is favourable — gains come slowly but surely, and long effort starts
    #     to pay off.
    11: "একাদশ ভাৱত শনি অনুকূল — লাভ লাহে লাহে কিন্তু নিশ্চিতভাৱে আহে, আৰু দীঘলীয়া চেষ্টাই ফল দিবলৈ আৰম্ভ কৰে।",
    # EN: Saturn is in your 12th — the opening phase of Sade Sati. Watch expenses and rest well; a
    #     good time for quiet, inward work.
    12: "শনি আপোনাৰ দ্বাদশ ভাৱত — সাড়ে সাতিৰ আৰম্ভণিৰ পৰ্যায়। খৰচৰ প্ৰতি লক্ষ্য ৰাখক আৰু ভালকৈ জিৰণি লওক; নিৰিবিলি, অন্তৰ্মুখী কামৰ বাবে ভাল সময়।",
}

# app/rashifal_text.py JUPITER_HOUSE["as"] — Jupiter transit through houses 1-12  [12]
RASHIFAL_JUPITER_HOUSE = {
    # EN: Jupiter over your Moon sign is classically a restless position; keep plans grounded and
    #     avoid over-committing.
    1: "আপোনাৰ চন্দ্ৰ ৰাশিত বৃহস্পতি থকাটো শাস্ত্ৰমতে অস্থিৰ স্থিতি; পৰিকল্পনা বাস্তৱসন্মত ৰাখক আৰু অত্যধিক প্ৰতিশ্ৰুতি দিয়াৰ পৰা বিৰত থাকক।",
    # EN: Jupiter in your 2nd supports family harmony, savings and kind speech.
    2: "দ্বিতীয় ভাৱত বৃহস্পতিয়ে পৰিয়ালৰ সম্প্ৰীতি, সঞ্চয় আৰু মিঠা কথাক সমৰ্থন কৰে।",
    # EN: Jupiter in your 3rd asks a little more effort for the same result — keep at it.
    3: "তৃতীয় ভাৱত বৃহস্পতিয়ে একে ফলৰ বাবে অলপ বেছি চেষ্টা বিচাৰে — লাগি থাকক।",
    # EN: Jupiter in your 4th can unsettle home matters; patience with relatives helps.
    4: "চতুৰ্থ ভাৱত বৃহস্পতিয়ে ঘৰৰ কথাত অস্থিৰতা আনিব পাৰে; আত্মীয়ৰ প্ৰতি ধৈৰ্যই সহায় কৰে।",
    # EN: Jupiter in your 5th favours learning, children's matters, creativity and good counsel.
    5: "পঞ্চম ভাৱত বৃহস্পতিয়ে শিক্ষা, সন্তানৰ কথা, সৃজনশীলতা আৰু ভাল পৰামৰ্শৰ অনুকূল।",
    # EN: Jupiter in your 6th: steer clear of small disputes and overwork.
    6: "ষষ্ঠ ভাৱত বৃহস্পতি: সৰু সৰু বিবাদ আৰু অত্যধিক পৰিশ্ৰমৰ পৰা আঁতৰি থাকক।",
    # EN: Jupiter in your 7th blesses partnerships, marriage talks and travel.
    7: "সপ্তম ভাৱত বৃহস্পতিয়ে অংশীদাৰী, বিয়াৰ কথা আৰু যাত্ৰাক আশীৰ্বাদ দিয়ে।",
    # EN: Jupiter in your 8th suggests care with big decisions — go slow.
    8: "অষ্টম ভাৱত বৃহস্পতিয়ে ডাঙৰ সিদ্ধান্তত সাৱধানতা বিচাৰে — লাহে লাহে আগবাঢ়ক।",
    # EN: Jupiter in your 9th is one of its best positions — fortune, dharma and guidance from
    #     teachers.
    9: "নৱম ভাৱত বৃহস্পতি তাৰ আটাইতকৈ ভাল স্থিতিবোৰৰ এটা — ভাগ্য, ধৰ্ম আৰু শিক্ষকৰ পথ-প্ৰদৰ্শন।",
    # EN: Jupiter in your 10th may bring changes at work; stay adaptable.
    10: "দশম ভাৱত বৃহস্পতিয়ে কামত পৰিৱৰ্তন আনিব পাৰে; নমনীয় হৈ থাকক।",
    # EN: Jupiter in your 11th brings gains, fulfilled wishes and helpful friends.
    11: "একাদশ ভাৱত বৃহস্পতিয়ে লাভ, পূৰ্ণ হোৱা ইচ্ছা আৰু সহায়ক বন্ধু আনে।",
    # EN: Jupiter in your 12th brings expenses, often on good causes; charity and spiritual practice
    #     are well placed.
    12: "দ্বাদশ ভাৱত বৃহস্পতিয়ে খৰচ আনে, প্ৰায়ে ভাল কামতে; দান আৰু আধ্যাত্মিক সাধনা ভালদৰে খাপ খায়।",
}

# app/rashifal_text.py RAHU_HOUSE["as"] — Rahu transit through houses 1-12  [12]
RASHIFAL_RAHU_HOUSE = {
    # EN: Rahu over your Moon sign can stir restlessness and unusual wants; stay grounded.
    1: "আপোনাৰ চন্দ্ৰ ৰাশিত ৰাহু থাকিলে অস্থিৰতা আৰু অস্বাভাৱিক ইচ্ছা জাগিব পাৰে; মাটিত ভৰি ৰাখক।",
    # EN: Rahu in your 2nd: take care with speech and money talk within the family.
    2: "দ্বিতীয় ভাৱত ৰাহু: পৰিয়ালত কথা আৰু ধনৰ আলোচনাত সাৱধান হওক।",
    # EN: Rahu in your 3rd is favourable — bold initiatives and communication succeed.
    3: "তৃতীয় ভাৱত ৰাহু অনুকূল — সাহসী উদ্যোগ আৰু যোগাযোগ সফল হয়।",
    # EN: Rahu in your 4th can unsettle domestic peace; avoid hasty property moves.
    4: "চতুৰ্থ ভাৱত ৰাহুয়ে ঘৰৰ শান্তি বিঘ্নিত কৰিব পাৰে; সম্পত্তিৰ ক্ষেত্ৰত খৰখেদা নকৰিব।",
    # EN: Rahu in your 5th: double-check risky ideas and keep a clear head.
    5: "পঞ্চম ভাৱত ৰাহু: বিপজ্জনক ধাৰণাবোৰ দুবাৰ ভালকৈ চাওক আৰু মূৰ ঠাণ্ডা ৰাখক।",
    # EN: Rahu in your 6th helps you get past competition and obstacles.
    6: "ষষ্ঠ ভাৱত ৰাহুয়ে প্ৰতিযোগিতা আৰু বাধা পাৰ হোৱাত সহায় কৰে।",
    # EN: Rahu in your 7th: keep partnerships transparent.
    7: "সপ্তম ভাৱত ৰাহু: অংশীদাৰী স্বচ্ছ ৰাখক।",
    # EN: Rahu in your 8th: avoid risky shortcuts and stay calm when the unexpected comes.
    8: "অষ্টম ভাৱত ৰাহু: বিপজ্জনক চুটি পথ এৰাই চলক আৰু অপ্ৰত্যাশিত ঘটনা আহিলে শান্ত থাকক।",
    # EN: Rahu in your 9th can raise doubts about beliefs or mentors; seek advice you trust.
    9: "নৱম ভাৱত ৰাহুয়ে বিশ্বাস বা গুৰুৰ প্ৰতি সন্দেহ জগাব পাৰে; ভৰসাযোগ্য পৰামৰ্শ লওক।",
    # EN: Rahu in your 10th brings ambition and sudden openings at work; move with integrity.
    10: "দশম ভাৱত ৰাহুয়ে উচ্চাকাংক্ষা আৰু কামত হঠাৎ সুযোগ আনে; সততাৰে আগবাঢ়ক।",
    # EN: Rahu in your 11th — gains through networks and new contacts.
    11: "একাদশ ভাৱত ৰাহু — যোগাযোগ আৰু নতুন পৰিচয়ৰ দ্বাৰা লাভ।",
    # EN: Rahu in your 12th: watch hidden expenses and get proper rest.
    12: "দ্বাদশ ভাৱত ৰাহু: লুকাই থকা খৰচৰ প্ৰতি সাৱধান হওক আৰু ভালকৈ জিৰণি লওক।",
}

# app/rashifal_text.py KETU_LINE["as"] — Ketu line, True = favourable house, False = quiet house; {n} is the house  [2]
RASHIFAL_KETU_LINE = {
    # EN: Ketu in your {n} house works quietly in your favour — obstacles clear with less fuss.
    # keep: {n}
    True: "আপোনাৰ {n} ভাৱত কেতুয়ে নীৰৱে আপোনাৰ পক্ষে কাম কৰে — বাধা-বিঘিনি অলপ হই-চৈ নোহোৱাকৈয়ে আঁতৰি যায়।",
    # EN: Ketu in your {n} house is a quieter, inward influence — good for reflection and spiritual
    #     practice, less so for impulsive moves.
    # keep: {n}
    False: "আপোনাৰ {n} ভাৱত কেতু এক শান্ত, অন্তৰ্মুখী প্ৰভাৱ — চিন্তন আৰু আধ্যাত্মিক সাধনাৰ বাবে ভাল, হঠাৎ পদক্ষেপৰ বাবে কম।",
}

# app/rashifal_text.py CLOCK_LANG["as"] — leave '' (the language's own clock words); 'en' prints 6:29 AM as Hindi pages do
# (optional: may stay empty)
RASHIFAL_CLOCK_LANG = ""

# ----------------------------------------------------------------------------
# vrat      /vrat-tyohar /ekadashi-<year> /tyohar/<slug>-<year>
# ----------------------------------------------------------------------------

# app/vrat_text.py TEXT["as"] — page text of /vrat-tyohar, /ekadashi-<year>, /tyohar/<slug>-<year>  [64]
VRAT_TEXT = {
    # EN: Vrat & festivals
    "crumb": "ব্ৰত আৰু উৎসৱ",
    # EN: {date}, {weekday}
    # keep: {date} {weekday}
    "day_label": "{date}, {weekday}",
    # EN: {label}: {prefix}{value}
    # keep: {label} {prefix} {value}
    "timing": "{label}: {prefix}{value}",
    # EN: {paksha} {name}: {start} to {end}
    # keep: {end} {name} {paksha} {start}
    "tithi.text": "{paksha} {name}: {start}ৰ পৰা {end}লৈ",
    # EN: {paksha}
    # keep: {paksha}
    "tithi.paksha": "{paksha} পক্ষ",
    # EN: <tr><th>Date</th><th>Vrat / festival</th><th>Timing ({city})</th></tr>
    # keep: {city}
    "table.th": "<tr><th>তাৰিখ</th><th>ব্ৰত / উৎসৱ</th><th>সময় ({city})</th></tr>",
    # EN: <div class="box"><p><strong>Timings vary by city.</strong> Every time here is for {city}'s
    #     sunrise, sunset and moonrise; in another city they shift by a few minutes and occasionally
    #     the date does too. Dates follow Drik Panchang's Smarta (default) reckoning. Check the
    #     Panchang for your own city.</p></div>
    # keep: {city}
    "city_note": "<div class=\"box\"><p><strong>সময় চহৰ অনুসৰি সলনি হয়।</strong> ইয়াত দিয়া প্ৰতিটো সময় {city} চহৰৰ সূৰ্যোদয়, সূৰ্যাস্ত আৰু চন্দ্ৰোদয় অনুসৰি; আন চহৰত সেয়া কেইমিনিটমান আগপিছ হয়, কেতিয়াবা তাৰিখো সলনি হয়। তাৰিখবোৰ দৃক পঞ্জিকাৰ স্মাৰ্ত (সাধাৰণ) গণনা অনুসৰি দিয়া। নিজৰ চহৰৰ পঞ্জিকা চাই লওক।</p></div>",
    # EN: <p class="note"><small>For most observances the date is the same across India, but puja
    #     muhurat, parana and moonrise times differ from city to city - every time here is for
    #     <strong>{city}</strong>. Regional traditions may vary.</small></p>
    # keep: {city}
    "top_note": "<p class=\"note\"><small>বেছিভাগ ব্ৰত-উৎসৱৰ তাৰিখ সমগ্ৰ ভাৰতত একে, কিন্তু পূজাৰ মুহূৰ্ত, পাৰণ আৰু চন্দ্ৰোদয়ৰ সময় চহৰ অনুসৰি বেলেগ - ইয়াত প্ৰতিটো সময় <strong>{city}</strong>ৰ। আঞ্চলিক প্ৰথা বেলেগ হ'ব পাৰে।</small></p>",
    # EN: Vrat & festivals in your city
    "cities.heading": "আপোনাৰ চহৰৰ ব্ৰত আৰু উৎসৱ",
    # EN: Today's Panchang in {city}
    # keep: {city}
    "tools.panchang": "{city} চহৰৰ আজিৰ পঞ্জিকা",
    # EN: Rahu Kaal in {city}
    # keep: {city}
    # may also use: {t_rahu_kaal}
    "tools.rahu": "{city} চহৰৰ ৰাহুকাল",
    # EN: More for {city}
    # keep: {city}
    "tools.heading": "{city} চহৰৰ বাবে আৰু",
    # EN: See the Panchang for your city — free
    "cta": "আপোনাৰ চহৰৰ পঞ্জিকা চাওক — বিনামূলীয়া",
    # EN: Today's vrat & festivals
    "more.today": "আজিৰ ব্ৰত আৰু উৎসৱ",
    # EN: Festival calendar {year}
    # keep: {year}
    "more.year": "ব্ৰত-উৎসৱৰ পঞ্জী {year}",
    # EN: Ekadashi {year}
    # keep: {year}
    "more.ekadashi": "একাদশী {year}",
    # EN: Today's Panchang
    "more.panchang": "আজিৰ পঞ্জিকা",
    # EN: Today's Rashifal
    "more.rashifal": "আজিৰ ৰাশিফল",
    # EN: More
    "more.heading": "আৰু চাওক",
    # EN: Major festivals {year}
    # keep: {year}
    "majors.heading": "{year} চনৰ প্ৰধান উৎসৱ",
    # EN: Rule
    "today.rule": "নিয়ম",
    # EN: No major vrat or festival today.
    "today.none": "আজি কোনো প্ৰধান ব্ৰত বা উৎসৱ নাই।",
    # EN: Next: <strong>{name}</strong> on {day}.
    # keep: {day} {name}
    "today.next": " পৰৱৰ্তী: <strong>{name}</strong>, {day}।",
    # EN: Vrat &amp; Festivals today
    "block.heading": "আজিৰ ব্ৰত আৰু উৎসৱ",
    # EN: Page not found
    "nf.h1": "পৃষ্ঠাটো পোৱা নগ'ল",
    # EN: Aaj Ke Vrat aur Tyohar: Today's Vrat & Festivals ({date})
    # keep: {date}
    "hub.title_default": "আজিৰ ব্ৰত আৰু উৎসৱ ({date}) - পূজাৰ শুভ মুহূৰ্তসহ",
    # EN: Today's Vrat & Festivals in {city} ({date}) - Aaj Ke Vrat
    # keep: {city} {date}
    "hub.title_city": "{city} চহৰৰ আজিৰ ব্ৰত আৰু উৎসৱ ({date}) - শুভ মুহূৰ্ত",
    # EN: Today's vrat & festivals
    "hub.h1_default": "আজিৰ ব্ৰত আৰু উৎসৱ",
    # EN: Today's vrat & festivals in {city}
    # keep: {city}
    "hub.h1_city": "{city} চহৰৰ আজিৰ ব্ৰত আৰু উৎসৱ",
    # EN: Today, {date}: {names}.
    # keep: {date} {names}
    "hub.desc_today": "আজি {date}: {names}। ",
    # EN: {date}: no major vrat today.
    # keep: {date}
    "hub.desc_none": "{date}: আজি কোনো প্ৰধান ব্ৰত নাই। ",
    # EN: Upcoming fasts and festivals for 30 days with Ekadashi parana, Pradosh and Sankashti
    #     moonrise times - {city}.
    # keep: {city}
    "hub.desc_rest": "আগন্তুক 30 দিনৰ ব্ৰত আৰু উৎসৱ, একাদশীৰ পাৰণ, প্ৰদোষ আৰু সংকষ্টী চতুৰ্থীৰ চন্দ্ৰোদয়ৰ সময় - {city}।",
    # EN: <p class="hi" lang="hi">आज के व्रत और त्योहार</p>
    "hub.sub": "<p class=\"hi\">আজি কোনটো ব্ৰত, কোনটো উৎসৱ</p>",
    # EN: Next 30 days
    "hub.upcoming": "আগন্তুক 30 দিন",
    # EN: Hindu Festival & Vrat Calendar {year} (New Delhi): Dates and Muhurat
    # keep: {year}
    "year.title": "ব্ৰত আৰু উৎসৱ {year}: উৎসৱৰ তালিকা, তাৰিখ আৰু শুভ মুহূৰ্ত",
    # EN: Vrat & festival calendar {year}
    # keep: {year}
    "year.h1": "ব্ৰত আৰু উৎসৱৰ পঞ্জী {year}",
    # EN: Every Hindu vrat and festival of {year}, month by month - Ekadashi, Pradosh, Sankashti,
    #     Purnima, Amavasya, Shivratri and festivals like Diwali, Navratri and Raksha Bandhan, with
    #     puja muhurat for New Delhi.
    # keep: {year}
    "year.desc": "{year} চনৰ সকলো হিন্দু ব্ৰত আৰু উৎসৱ, মাহ অনুসৰি - একাদশী, প্ৰদোষ, সংকষ্টী, পূৰ্ণিমা, অমাৱস্যা, শিৱৰাত্ৰি আৰু দীপাৱলী, নৱৰাত্ৰি, ৰাখী বন্ধনৰ দৰে উৎসৱ, নতুন দিল্লীৰ পূজাৰ মুহূৰ্তসহ।",
    # EN: <p><strong>{count}</strong> fasts and festivals in {year} for New Delhi, computed from the
    #     panchang. Tap a major festival for its puja muhurat and what it is about.</p>
    # keep: {count} {year}
    "year.intro": "<p>{year} চনত নতুন দিল্লীৰ বাবে <strong>{count}</strong> টা ব্ৰত আৰু উৎসৱ, পঞ্জিকাৰ পৰা গণনা কৰা। যিকোনো প্ৰধান উৎসৱত টিপিলে তাৰ পূজাৰ মুহূৰ্ত আৰু বিৱৰণ চাব পাৰিব।</p>",
    # EN: {month} {year}
    # keep: {month} {year}
    "year.month": "{month} {year}",
    # EN: Major Hindu festivals {year}
    # keep: {year}
    "year.itemlist": "{year} চনৰ প্ৰধান হিন্দু উৎসৱ",
    # EN: Ekadashi {year}: All Ekadashi Vrat Dates and Parana Time (New Delhi)
    # keep: {year}
    "ek.title": "একাদশী {year} তালিকা: সকলো একাদশী ব্ৰতৰ তাৰিখ আৰু পাৰণৰ সময়",
    # EN: Ekadashi {year}: dates and parana time
    # keep: {year}
    "ek.h1": "একাদশী {year}: তাৰিখ আৰু পাৰণৰ সময়",
    # EN: All {count} Ekadashis of {year} - fasting date, Ekadashi tithi times and the parana (fast-
    #     breaking) window next day, for New Delhi.
    # keep: {count} {year}
    "ek.desc": "{year} চনৰ সকলো {count} টা একাদশী - উপবাসৰ তাৰিখ, একাদশী তিথিৰ সময় আৰু পিছদিনা পাৰণৰ (উপবাস ভঙা) সময়, নতুন দিল্লীৰ বাবে।",
    # EN: <tr><th>Ekadashi</th><th>Fast</th><th>Parana</th></tr>
    "ek.th": "<tr><th>একাদশী</th><th>উপবাস</th><th>পাৰণ</th></tr>",
    # EN: <p><strong>Rule (Smarta):</strong> fast on the day Ekadashi prevails at sunrise; if it
    #     prevails at two sunrises, the second day, and if at none, the day it falls in. Parana is
    #     the next day after sunrise, once Hari Vasara (the first quarter of Dwadashi) is over,
    #     within Pratahkala and before Dwadashi ends; if Hari Vasara runs past Pratahkala, parana
    #     moves to Aparahna (Madhyahna is avoided).</p>
    "ek.rule": "<p><strong>নিয়ম (স্মাৰ্ত):</strong> যিদিনা সূৰ্যোদয়ত একাদশী থাকে সেইদিনা উপবাস; দুটা সূৰ্যোদয়তে থাকিলে দ্বিতীয় দিনা, আৰু কোনো সূৰ্যোদয়তে নাথাকিলে যিদিনা একাদশী পৰে সেইদিনা। পাৰণ পিছদিনা সূৰ্যোদয়ৰ পিছত, হৰিবাসৰ (দ্বাদশীৰ প্ৰথম চতুৰ্থাংশ) শেষ হ'লে, প্ৰাতঃকালৰ ভিতৰত আৰু দ্বাদশী শেষ হোৱাৰ আগতে; হৰিবাসৰ প্ৰাতঃকাল পাৰ হৈ গ'লে মধ্যাহ্ন এৰি অপৰাহ্ণত পাৰণ কৰা হয়।</p>",
    # EN: <p class="hi" lang="hi">एकादशी {year}</p>
    # keep: {year}
    "ek.sub": "<p class=\"hi\">একাদশী ব্ৰত {year}</p>",
    # EN: Ekadashi {year}
    # keep: {year}
    "ek.crumb": "একাদশী {year}",
    # EN: {name} {year}: Date and Puja Muhurat - {short}
    # keep: {name} {short} {year}
    "fest.title": "{name} {year}: তাৰিখ আৰু শুভ মুহূৰ্ত - {short}",
    # EN: {name} {year}: date and muhurat
    # keep: {name} {year}
    "fest.h1": "{name} {year}: তাৰিখ আৰু মুহূৰ্ত",
    # EN: {text}.
    # keep: {text}
    "fest.main": "{text}। ",
    # EN: {name} {year} is on {weekday}, {date}. {main}Puja timings for New Delhi.
    # keep: {date} {main} {name} {weekday} {year}
    "fest.desc": "{name} {year} {weekday}, {date} তাৰিখে পৰিছে। {main}নতুন দিল্লীৰ পূজাৰ সময়।",
    # EN: {name} {year} is on <strong>{when}</strong>.
    # keep: {name} {when} {year}
    "fest.when": "{name} {year} <strong>{when}</strong> তাৰিখে পৰিছে।",
    # EN: <p class="hi" lang="hi">{name_hi} {year}</p>
    # keep: {year}
    "fest.sub": "<p class=\"hi\">তিথি, শুভ মুহূৰ্ত আৰু পূজাৰ সময় · {year}</p>",
    # EN: What it is and how it is observed
    "fest.about_h2": "ই কি আৰু কেনেকৈ পালন কৰা হয়",
    # EN: How the date is fixed
    "fest.rule_h2": "তাৰিখ কেনেকৈ নিৰ্ধাৰণ হয়",
    # EN: Frequently asked questions
    "fest.faq_h2": "সঘনাই সোধা প্ৰশ্ন",
    # EN: India
    "event.place": "ভাৰত",
    # EN: When is {name} {year}?
    # keep: {name} {year}
    "faq.when_q": "{name} {year} কেতিয়া?",
    # EN: {name} {year} is on {weekday}, {date}.
    # keep: {date} {name} {weekday} {year}
    "faq.when_a": "{name} {year} {weekday}, {date} তাৰিখে পৰিছে।",
    # EN: What is the {name} {year} puja muhurat?
    # keep: {name} {year}
    "faq.muhurat_q": "{name} {year} ৰ পূজাৰ শুভ মুহূৰ্ত কেতিয়া?",
    # EN: What are the {name} {year} timings?
    # keep: {name} {year}
    "faq.timings_q": "{name} {year} ৰ সময় কি?",
    # EN: For New Delhi - {timings}. Timings vary by city by a few minutes; check the Panchang for
    #     your city.
    # keep: {timings}
    "faq.timings_a": "নতুন দিল্লীৰ বাবে - {timings}। চহৰ অনুসৰি সময় কেইমিনিটমান সলনি হয়; নিজৰ চহৰৰ পঞ্জিকা চাওক।",
    # EN: Why is {name} {year} observed on {short}?
    # keep: {name} {short} {year}
    "faq.why_q": "{name} {year} কিয় {short} তাৰিখে পালন কৰা হয়?",
    # EN: The date follows the rule: {rule}. In {year} that is {when} (New Delhi).
    # keep: {rule} {when} {year}
    "faq.why_a": "তাৰিখৰ নিয়ম: {rule}। {year} চনত সেয়া পৰিছে {when} (নতুন দিল্লী)।",
}

# app/vrat_text.py ABOUT["as"] — what each of the 47 festivals / vrats is (key = festival slug)  [47]
VRAT_ABOUT = {
    # EN: Makar Sankranti marks the Sun's entry into Makara (Capricorn) and the start of its
    #     northward journey (Uttarayana). It is a harvest festival: people bathe in holy rivers,
    #     give til (sesame), jaggery, khichdi and blankets in charity, and fly kites.
    "makar-sankranti": "মকৰ সংক্ৰান্তিয়ে সূৰ্যই মকৰ ৰাশিত প্ৰৱেশ কৰা আৰু উত্তৰমুখী যাত্ৰা (উত্তৰায়ণ) আৰম্ভ হোৱা বুজায়। এয়া এক শস্য উৎসৱ: মানুহে পবিত্ৰ নদীত স্নান কৰে, তিল, গুড়, খিচুৰী আৰু কম্বল দান কৰে, আৰু ঘুড়ী উৰুৱায়।",
    # EN: Maha Shivratri, the great night of Shiva, falls on the Krishna Chaturdashi of Magha.
    #     Devotees fast, offer water, milk and bel leaves on the Shivling, chant Om Namah Shivaya
    #     and keep vigil through the four prahars of the night; the Nishita kaal puja around
    #     midnight is the most important.
    "maha-shivratri": "মহাশিৱৰাত্ৰি, শিৱৰ মহান ৰাতি, মাঘ মাহৰ কৃষ্ণ চতুৰ্দশীত পৰে। ভক্তসকলে উপবাস কৰে, শিৱলিংগত পানী, গাখীৰ আৰু বেলপাত অৰ্পণ কৰে, ওঁ নমঃ শিৱায় জপ কৰে আৰু ৰাতিৰ চাৰিটা প্ৰহৰ জাগ্ৰত থাকে; মাজৰাতিৰ ওচৰৰ নিশীথ কালৰ পূজা সবাতোকৈ গুৰুত্বপূৰ্ণ।",
    # EN: Holika Dahan, on the eve of Holi, celebrates Prahlad's devotion and the victory of good
    #     over evil. A bonfire is lit after sunset, avoiding Bhadra, and families circle it offering
    #     grain, coconut and prayers.
    "holika-dahan": "হোলিৰ আগদিনা হোলিকা দহনে প্ৰহ্লাদৰ ভক্তি আৰু বেয়াৰ ওপৰত ভালৰ জয় উদযাপন কৰে। সূৰ্যাস্তৰ পিছত ভদ্ৰা এৰাই জুই জ্বলোৱা হয়, আৰু পৰিয়ালবৰ্গই ইয়াক প্ৰদক্ষিণ কৰি শস্য, নাৰিকল আৰু প্ৰাৰ্থনা অৰ্পণ কৰে।",
    # EN: Holi, the festival of colours, is celebrated the morning after Holika Dahan with colours,
    #     music, sweets like gujiya and visits to family and friends.
    "holi": "ৰঙৰ উৎসৱ হোলি হোলিকা দহনৰ পিছদিনা ৰাতিপুৱা ৰং, সংগীত, গুজিয়াৰ দৰে মিঠাই আৰু পৰিয়াল-বন্ধুৰ ঘৰলৈ যোৱাৰ মাজেৰে পালন কৰা হয়।",
    # EN: Ram Navami celebrates the birth of Lord Rama on Chaitra Shukla Navami, at midday. Devotees
    #     fast, read the Ramcharitmanas, and offer puja in the Madhyahna muhurat, the time of his
    #     birth.
    "ram-navami": "ৰাম নৱমীয়ে চ'ত মাহৰ শুক্ল নৱমীত দুপৰীয়া ভগৱান ৰামৰ জন্ম উদযাপন কৰে। ভক্তসকলে উপবাস কৰে, ৰামচৰিতমানস পাঠ কৰে আৰু তেওঁৰ জন্মৰ সময় মধ্যাহ্ন মুহূৰ্তত পূজা কৰে।",
    # EN: Hanuman Jayanti (Chaitra Purnima in North India) celebrates the birth of Lord Hanuman.
    #     Devotees visit Hanuman temples, recite the Hanuman Chalisa and Sundarkand, and offer
    #     sindoor and laddoos.
    "hanuman-jayanti": "হনুমান জয়ন্তী (উত্তৰ ভাৰতত চ'ত পূৰ্ণিমা)ই ভগৱান হনুমানৰ জন্ম উদযাপন কৰে। ভক্তসকলে হনুমান মন্দিৰলৈ যায়, হনুমান চালীসা আৰু সুন্দৰকাণ্ড পাঠ কৰে, আৰু সেন্দূৰ আৰু লাডু অৰ্পণ কৰে।",
    # EN: Akshaya Tritiya, Vaishakha Shukla Tritiya, is held to make every good deed 'akshaya' -
    #     undiminishing. People worship Vishnu and Lakshmi, give in charity, and begin new ventures
    #     or buy gold.
    "akshaya-tritiya": "অক্ষয় তৃতীয়া, বহাগ মাহৰ শুক্ল তৃতীয়াত, প্ৰতিটো ভাল কামক ‘অক্ষয়’ - কেতিয়াও নোহোৱা হোৱা - কৰে বুলি মানা হয়। মানুহে বিষ্ণু আৰু লক্ষ্মীৰ পূজা কৰে, দান কৰে, আৰু নতুন কাম আৰম্ভ কৰে বা সোণ কিনে।",
    # EN: Raksha Bandhan, on Shravana Purnima, celebrates the bond between brothers and sisters.
    #     Sisters tie a rakhi on their brother's wrist and pray for his well-being; the rakhi is
    #     tied in a time free of Bhadra.
    "raksha-bandhan": "শাওন পূৰ্ণিমাত পৰা ৰাখী বন্ধনে ভাই-ভনীৰ বান্ধোন উদযাপন কৰে। ভনীয়েকে ভায়েকৰ হাতত ৰাখী বান্ধি তেওঁৰ কল্যাণৰ প্ৰাৰ্থনা কৰে; ৰাখী ভদ্ৰা নথকা সময়ত বন্ধা হয়।",
    # EN: Krishna Janmashtami celebrates the birth of Lord Krishna at midnight on Krishna Ashtami of
    #     Bhadrapada (purnimanta). Devotees fast through the day and break it after the Nishita
    #     (midnight) puja, when the infant Krishna is bathed and placed in a cradle.
    "janmashtami": "কৃষ্ণ জন্মাষ্টমীয়ে ভাদ মাহৰ কৃষ্ণ অষ্টমীত (পূৰ্ণিমান্ত) মাজৰাতি ভগৱান কৃষ্ণৰ জন্ম উদযাপন কৰে। ভক্তসকলে গোটেই দিনটো উপবাস থাকে আৰু নিশীথ (মাজৰাতি) পূজাৰ পিছত উপবাস ভাঙে, যেতিয়া শিশু কৃষ্ণক স্নান কৰাই দোলাত ৰখা হয়।",
    # EN: Ganesh Chaturthi, Bhadrapada Shukla Chaturthi, welcomes Lord Ganesha home. The idol is
    #     installed and worshipped in the Madhyahna (midday) muhurat, the time of his birth, with
    #     modak, durva grass and red flowers; looking at the Moon on this day is avoided.
    "ganesh-chaturthi": "গণেশ চতুৰ্থী, ভাদ মাহৰ শুক্ল চতুৰ্থী, ভগৱান গণেশক ঘৰলৈ আদৰি আনে। মূৰ্তি স্থাপন কৰি মধ্যাহ্নৰ মুহূৰ্তত, তেওঁৰ জন্মৰ সময়ত, মোদক, দূৰ্বা ঘাঁহ আৰু ৰঙা ফুলেৰে পূজা কৰা হয়; এই দিনা চন্দ্ৰ চোৱা নিষিদ্ধ।",
    # EN: Chaitra Navratri, the nine nights of Goddess Durga in spring, begins on Chaitra Shukla
    #     Pratipada - also the Hindu New Year (Vikram Samvat). Ghatasthapana (installing the kalash)
    #     opens the nine days of worship.
    "chaitra-navratri": "চৈত্ৰ নৱৰাত্ৰি, বসন্তকালৰ দেৱী দুৰ্গাৰ নটা ৰাতি, চ'ত মাহৰ শুক্ল প্ৰতিপদত আৰম্ভ হয় - একেদিনাই হিন্দু নৱবৰ্ষ (বিক্ৰম সংবৎ)ও। ঘটস্থাপনা (কলস স্থাপন)ৰ লগেলগে নটা দিনৰ পূজা আৰম্ভ হয়।",
    # EN: Sharad Navratri, the nine nights of Goddess Durga in autumn, begins on Ashwin Shukla
    #     Pratipada with Ghatasthapana - installing the kalash and sowing barley - in the morning.
    #     Each day honours one of the nine forms of the Goddess.
    "navratri": "শাৰদীয় নৱৰাত্ৰি, শৰৎকালৰ দেৱী দুৰ্গাৰ নটা ৰাতি, আহিন মাহৰ শুক্ল প্ৰতিপদত ৰাতিপুৱা ঘটস্থাপনাৰে - কলস স্থাপন আৰু যৱ সিঁচাৰে - আৰম্ভ হয়। প্ৰতিটো দিনে দেৱীৰ নটা ৰূপৰ এটাক সন্মান জনায়।",
    # EN: Dussehra (Vijayadashami) marks Lord Rama's victory over Ravana and Goddess Durga's over
    #     Mahishasura. Shami puja, Aparajita puja and the burning of Ravana effigies are held in the
    #     afternoon; the Vijay muhurat is considered good for starting anything new.
    "dussehra": "বিজয়া দশমীয়ে (দশেৰা) ভগৱান ৰামে ৰাৱণৰ ওপৰত আৰু দেৱী দুৰ্গাই মহিষাসুৰৰ ওপৰত লাভ কৰা বিজয় সূচায়। অপৰাহ্ণত শমী পূজা, অপৰাজিতা পূজা আৰু ৰাৱণৰ প্ৰতিমূৰ্তি দহন কৰা হয়; বিজয় মুহূৰ্ত যিকোনো নতুন কাম আৰম্ভ কৰিবলৈ ভাল বুলি ধৰা হয়।",
    # EN: On Karwa Chauth married women keep a fast from sunrise to moonrise for their husbands'
    #     long life. The evening puja of Karwa Mata is followed by offering water (arghya) to the
    #     Moon, after which the fast is broken.
    "karwa-chauth": "কৰৱা চৌথত বিবাহিত মহিলাই স্বামীৰ দীৰ্ঘায়ুৰ বাবে সূৰ্যোদয়ৰ পৰা চন্দ্ৰোদয়লৈ উপবাস কৰে। সন্ধিয়া কৰৱা মাতাৰ পূজাৰ পিছত চন্দ্ৰলৈ অৰ্ঘ্য (পানী) দিয়া হয়, তাৰ পিছতহে উপবাস ভঙা হয়।",
    # EN: On Ahoi Ashtami, eight days before Diwali, mothers keep a fast for the well-being of their
    #     children and worship Ahoi Mata in the evening; the fast is traditionally broken after
    #     sighting the stars (or, in some families, the Moon).
    "ahoi-ashtami": "দীপাৱলীৰ আঠ দিন আগৰ অহোই অষ্টমীত মাকসকলে সন্তানৰ কল্যাণৰ বাবে উপবাস কৰে আৰু সন্ধিয়া অহোই মাতাৰ পূজা কৰে; পৰম্পৰা অনুসৰি তৰা দেখাৰ পিছত (বা কিছুমান পৰিয়ালত চন্দ্ৰ দেখাৰ পিছত) উপবাস ভঙা হয়।",
    # EN: Dhanteras, the first day of Diwali, honours Dhanvantari and Goddess Lakshmi. People buy
    #     new utensils, gold or silver and light the Yama deepak at dusk; the puja is done in
    #     Pradosh kaal, ideally in the fixed (sthir) Vrishabha lagna.
    "dhanteras": "ধনতেৰস, দীপাৱলীৰ প্ৰথম দিন, ধন্বন্তৰি আৰু দেৱী লক্ষ্মীক সন্মান জনায়। মানুহে নতুন বাচন-বৰ্তন, সোণ বা ৰূপ কিনে আৰু গধূলি যম দীপ জ্বলায়; প্ৰদোষ কালত, আদৰ্শভাৱে স্থিৰ বৃষ লগ্নত, পূজা কৰা হয়।",
    # EN: Diwali, on Kartika Amavasya, is the festival of lights. Lakshmi and Ganesha are worshipped
    #     in the evening - in Pradosh kaal, preferably in the fixed (sthir) Vrishabha lagna so that
    #     prosperity stays - and homes are lit with diyas.
    "diwali": "দীপাৱলী, কাতি মাহৰ অমাৱস্যাত, জ্যোতিৰ উৎসৱ। সন্ধিয়া লক্ষ্মী আৰু গণেশৰ পূজা কৰা হয় - প্ৰদোষ কালত, সমৃদ্ধি থাকি যাবলৈ স্থিৰ বৃষ লগ্নত হ'লে ভাল - আৰু ঘৰবোৰ প্ৰদীপেৰে জ্বলমলাই তোলা হয়।",
    # EN: Govardhan Puja (Annakut), the day after Diwali, remembers Krishna lifting Govardhan hill.
    #     A Govardhan of cow-dung or food is worshipped and an annakut of many dishes is offered,
    #     usually in the morning (Pratahkala).
    "govardhan-puja": "দীপাৱলীৰ পিছদিনা গোৱৰ্ধন পূজা (অন্নকূট)ই কৃষ্ণই গোৱৰ্ধন পৰ্বত দাঙি ধৰা কথা সোঁৱৰায়। গোবৰ বা খাদ্যেৰে গঢ়া গোৱৰ্ধনৰ পূজা কৰা হয় আৰু নানা ব্যঞ্জনৰ অন্নকূট অৰ্পণ কৰা হয়, সাধাৰণতে ৰাতিপুৱা (প্ৰাতঃকাল)।",
    # EN: Bhai Dooj, Kartika Shukla Dwitiya, celebrates brothers and sisters: sisters apply a tilak,
    #     perform aarti and pray for their brother's long life, ideally in the Aparahna (afternoon)
    #     time.
    "bhai-dooj": "ভাতৃ দ্বিতীয়া, কাতি মাহৰ শুক্ল দ্বিতীয়া, ভাই-ভনীৰ উৎসৱ: ভনীয়েকে ভায়েকক তিলক লগায়, আৰতি কৰে আৰু তেওঁৰ দীৰ্ঘায়ুৰ প্ৰাৰ্থনা কৰে, আদৰ্শভাৱে অপৰাহ্ণ সময়ত।",
    # EN: Chhath Puja worships the Sun God and Chhathi Maiya over four days. On the main day
    #     (Kartika Shukla Shashthi) devotees stand in water and offer arghya to the setting Sun, and
    #     to the rising Sun the next morning, ending a fast kept without water.
    "chhath-puja": "ছঠ পূজাত চাৰি দিন ধৰি সূৰ্য দেৱতা আৰু ছঠী মাইৰ পূজা কৰা হয়। মুখ্য দিনা (কাতি মাহৰ শুক্ল ষষ্ঠী) ভক্তসকলে পানীত থিয় হৈ অস্তগামী সূৰ্যলৈ আৰু পিছদিনা ৰাতিপুৱা উদীয়মান সূৰ্যলৈ অৰ্ঘ্য দিয়ে, আৰু পানীবিহীন উপবাস সামৰে।",
    # EN: Vasant Panchami, Magha Shukla Panchami, welcomes spring and honours Goddess Saraswati.
    #     Students and artists worship books and instruments, people wear yellow, and children often
    #     begin learning to write (vidyarambh).
    "vasant-panchami": "বসন্ত পঞ্চমী, মাঘ মাহৰ শুক্ল পঞ্চমী, বসন্তক আদৰি লয় আৰু দেৱী সৰস্বতীক সন্মান জনায়। ছাত্ৰ-ছাত্ৰী আৰু শিল্পীসকলে কিতাপ আৰু বাদ্যযন্ত্ৰৰ পূজা কৰে, মানুহে হালধীয়া কাপোৰ পিন্ধে, আৰু শিশুৱে প্ৰায়ে লিখিবলৈ শিকা আৰম্ভ কৰে (বিদ্যাৰম্ভ)।",
    # EN: Guru Purnima, Ashadha Purnima, honours one's teachers and Maharishi Ved Vyasa, born on
    #     this day. Disciples offer gratitude, flowers and gifts to their guru.
    "guru-purnima": "গুৰু পূৰ্ণিমা, আহাৰ মাহৰ পূৰ্ণিমা, শিক্ষকসকল আৰু এই দিনা জন্ম হোৱা মহৰ্ষি বেদব্যাসক সন্মান জনায়। শিষ্যসকলে গুৰুলৈ কৃতজ্ঞতা, ফুল আৰু উপহাৰ অৰ্পণ কৰে।",
    # EN: Sharad Purnima, Ashwin Purnima, is the night the Moon is held to be brightest and full of
    #     nectar. Kheer is kept in the moonlight overnight and eaten as prasad; Lakshmi is
    #     worshipped (Kojagari).
    "sharad-purnima": "শৰৎ পূৰ্ণিমা, আহিন মাহৰ পূৰ্ণিমা, এই ৰাতি চন্দ্ৰ আটাইতকৈ উজ্জ্বল আৰু অমৃতেৰে পূৰ্ণ বুলি মানা হয়। ক্ষীৰ ৰাতিটো জোনাকত ৰাখি প্ৰসাদ হিচাপে খোৱা হয়; লক্ষ্মীৰ পূজা কৰা হয় (কোজাগৰী)।",
    # EN: Devuthani (Prabodhini) Ekadashi, Kartika Shukla Ekadashi, is when Lord Vishnu is held to
    #     wake from his four-month sleep, ending Chaturmas. Tulsi vivah begins and the wedding
    #     season opens. Devotees fast and break the fast (parana) the next day.
    "devuthani-ekadashi": "দেৱোত্থান (প্ৰবোধিনী) একাদশী, কাতি মাহৰ শুক্ল একাদশী, এইদিনা ভগৱান বিষ্ণু চাৰি মাহৰ নিদ্ৰাৰ পৰা সাৰ পায় বুলি মানা হয়, আৰু চাতুৰ্মাস্য শেষ হয়। তুলসী বিবাহ আৰম্ভ হয় আৰু বিবাহৰ ঋতু খোল খায়। ভক্তসকলে উপবাস কৰে আৰু পিছদিনা পাৰণ কৰে।",
    # EN: Jivitputrika (Jitiya, Jiutiya) is kept by mothers in Bihar, Jharkhand, eastern Uttar
    #     Pradesh and Nepal for the long life and well-being of their children, on Ashwin Krishna
    #     Ashtami (purnimanta). It begins with nahay-khay the day before; the fast itself is
    #     nirjala, without water, through the day and night, with worship of Jimutavahana and the
    #     Jitiya katha. Parana, breaking the fast, is the next morning.
    "jivitputrika": "জীৱিতপুত্ৰিকা (জিতিয়া, জিউতিয়া) বিহাৰ, ঝাৰখণ্ড, পূব উত্তৰ প্ৰদেশ আৰু নেপালৰ মাকসকলে সন্তানৰ দীৰ্ঘায়ু আৰু কল্যাণৰ বাবে আহিন মাহৰ কৃষ্ণ অষ্টমীত (পূৰ্ণিমান্ত) পালন কৰে। আগদিনা ‘নহায়-খায়’ৰে আৰম্ভ হয়; উপবাস নিজেই নিৰ্জলা, পানীবিহীন, দিনে-ৰাতিয়ে, জীমূতবাহনৰ পূজা আৰু জিতিয়া কথাৰ সৈতে। পিছদিনা ৰাতিপুৱা পাৰণ কৰি উপবাস ভঙা হয়।",
    # EN: Lohri, the evening before Makar Sankranti, is the winter harvest festival of Punjab and
    #     North India. A bonfire is lit at dusk and people offer til, gur, rewari, peanuts and
    #     popcorn to it, sing and dance; it is especially celebrated for a new bride or a newborn.
    "lohri": "মকৰ সংক্ৰান্তিৰ আগৰ সন্ধিয়াৰ লোহৰী পঞ্জাব আৰু উত্তৰ ভাৰতৰ শীতকালীন শস্য উৎসৱ। গধূলি জুই জ্বলোৱা হয় আৰু মানুহে তাত তিল, গুড়, ৰেৱৰী, বাদাম আৰু পপকৰ্ণ অৰ্পণ কৰে, গীত গায় আৰু নাচে; নতুন কইনা বা নৱজাতকৰ বাবে বিশেষকৈ উদযাপন কৰা হয়।",
    # EN: Sakat Chauth (Tilkut Chauth), the Sankashti Chaturthi of Magha (purnimanta), is kept by
    #     mothers for their children. Ganesha and Sakat Mata are worshipped with til and jaggery,
    #     and the fast is broken after offering arghya to the rising Moon.
    "sakat-chauth": "সকট চৌথ (তিলকূট চৌথ), মাঘ মাহৰ (পূৰ্ণিমান্ত) সংকষ্টী চতুৰ্থী, মাকসকলে সন্তানৰ বাবে পালন কৰে। তিল আৰু গুড়েৰে গণেশ আৰু সকট মাতাৰ পূজা কৰা হয়, আৰু উদীয়মান চন্দ্ৰলৈ অৰ্ঘ্য দিয়াৰ পিছত উপবাস ভঙা হয়।",
    # EN: Mauni Amavasya, the Amavasya of Magha (purnimanta), is the great bathing day of the Magh
    #     Mela at Prayagraj. Devotees bathe in the Ganga or a holy river, keep silence (mauna) and
    #     give in charity.
    "mauni-amavasya": "মৌনী অমাৱস্যা, মাঘ মাহৰ (পূৰ্ণিমান্ত) অমাৱস্যা, প্ৰয়াগৰাজৰ মাঘ মেলাৰ প্ৰধান স্নানৰ দিন। ভক্তসকলে গঙ্গা বা পবিত্ৰ নদীত স্নান কৰে, মৌন (মৌনব্ৰত) থাকে আৰু দান কৰে।",
    # EN: Sheetala Ashtami (Basoda), Chaitra Krishna Ashtami (purnimanta), honours Sheetala Mata,
    #     the goddess who protects from fevers and pox. Food is cooked the day before and the stale
    #     (basi) food is offered and eaten; no fire is lit for cooking that day.
    "sheetala-ashtami": "শীতলা অষ্টমী (বাসোড়া), চ'ত মাহৰ (পূৰ্ণিমান্ত) কৃষ্ণ অষ্টমী, জ্বৰ আৰু বসন্তৰ পৰা ৰক্ষা কৰা শীতলা মাতাক সন্মান জনায়। আগদিনা ৰান্ধি থোৱা বাহী খাদ্য অৰ্পণ কৰি খোৱা হয়; সেইদিনা ৰন্ধনৰ বাবে জুই জ্বলোৱা নহয়।",
    # EN: Gudi Padwa (Maharashtra) and Ugadi (Karnataka, Andhra Pradesh, Telangana) mark the lunar
    #     New Year on Chaitra Shukla Pratipada. A gudi - a decorated pole with a cloth and kalash -
    #     is raised at the door, and neem with jaggery is eaten for a year of both sweet and bitter.
    "gudi-padwa": "গুড়ি পাডৱা (মহাৰাষ্ট্ৰ) আৰু উগাদি (কৰ্ণাটক, অন্ধ্ৰ প্ৰদেশ, তেলেংগানা)য়ে চ'ত মাহৰ শুক্ল প্ৰতিপদত চান্দ্ৰ নৱবৰ্ষ সূচায়। দুৱাৰমুখত কাপোৰ আৰু কলস লগোৱা সজ্জিত খুঁটা - এটা গুড়ি - তোলা হয়, আৰু মিঠা-তিতা দুয়োটাকে সামৰি বছৰটোৰ বাবে নিমপাত আৰু গুড় খোৱা হয়।",
    # EN: Gangaur, Chaitra Shukla Tritiya, is Rajasthan's festival of Gauri (Parvati) and Shiva.
    #     Women worship Gauri for marital happiness - married women for their husbands, girls for a
    #     good match - ending eighteen days of puja that begin the day after Holi.
    "gangaur": "গণগৌৰ, চ'ত মাহৰ শুক্ল তৃতীয়া, ৰাজস্থানৰ গৌৰী (পাৰ্বতী) আৰু শিৱৰ উৎসৱ। মহিলাসকলে বৈবাহিক সুখৰ বাবে গৌৰীৰ পূজা কৰে - বিবাহিতাই স্বামীৰ বাবে, কুমাৰীয়ে ভাল বৰৰ বাবে - হোলীৰ পিছদিনাৰ পৰা আৰম্ভ হোৱা ওঠৰ দিনৰ পূজা সামৰি।",
    # EN: Vat Savitri Vrat, on Jyeshtha Amavasya in North India (purnimanta), remembers Savitri, who
    #     won back her husband Satyavan's life from Yama. Married women fast, worship the banyan
    #     (vat) tree, tie raw thread around it while circling it, and hear the Savitri katha.
    "vat-savitri": "বট সাৱিত্ৰী ব্ৰত, উত্তৰ ভাৰতত জেঠ মাহৰ অমাৱস্যাত (পূৰ্ণিমান্ত), সাৱিত্ৰীক সোঁৱৰে, যিয়ে যমৰ পৰা স্বামী সত্যৱানৰ প্ৰাণ ঘূৰাই আনিছিল। বিবাহিতা মহিলাই উপবাস কৰে, বট গছৰ পূজা কৰে, প্ৰদক্ষিণ কৰি কেঁচা সূতা বান্ধে আৰু সাৱিত্ৰী কথা শুনে।",
    # EN: Vat Purnima is the same Vat Savitri vrat as kept on Jyeshtha Purnima in Maharashtra,
    #     Gujarat and the south (amanta calendar), fifteen days after the North Indian date. Married
    #     women fast and worship the banyan tree for their husbands' long life.
    "vat-purnima": "বট পূৰ্ণিমা সেই একেটা বট সাৱিত্ৰী ব্ৰত যিটো মহাৰাষ্ট্ৰ, গুজৰাট আৰু দক্ষিণত জেঠ পূৰ্ণিমাত (অমান্ত পঞ্জিকা) পালন কৰা হয়, উত্তৰ ভাৰতৰ তাৰিখৰ পোন্ধৰ দিন পিছত। বিবাহিতা মহিলাই স্বামীৰ দীৰ্ঘায়ুৰ বাবে উপবাস কৰে আৰু বট গছৰ পূজা কৰে।",
    # EN: Ganga Dussehra, Jyeshtha Shukla Dashami, celebrates the descent of the Ganga to earth
    #     through Bhagiratha's penance. Devotees bathe in the Ganga, offer lamps and give in
    #     charity; the bath is held to wash away ten kinds of sin.
    "ganga-dussehra": "গঙ্গা দশহৰা, জেঠ মাহৰ শুক্ল দশমী, ভগীৰথৰ তপস্যাৰ ফলত গঙ্গা পৃথিৱীলৈ নামি অহাৰ উৎসৱ। ভক্তসকলে গঙ্গাত স্নান কৰে, প্ৰদীপ অৰ্পণ কৰে আৰু দান কৰে; এই স্নানে দহ প্ৰকাৰৰ পাপ ধুই পেলায় বুলি মানা হয়।",
    # EN: Hariyali Teej, Shravana Shukla Tritiya, celebrates the reunion of Shiva and Parvati in the
    #     monsoon. Women wear green, apply mehndi, swing on decorated jhoolas, sing Sawan songs and
    #     many keep a fast for their husbands.
    "hariyali-teej": "হৰিয়ালী তীজ, শাওন মাহৰ শুক্ল তৃতীয়া, বৰষুণৰ দিনত শিৱ আৰু পাৰ্বতীৰ পুনৰ মিলনৰ উৎসৱ। মহিলাসকলে সেউজীয়া কাপোৰ পিন্ধে, মেহেন্দী লগায়, সজ্জিত দোলাত দুলে, শাওনৰ গীত গায় আৰু বহুতে স্বামীৰ বাবে উপবাস থাকে।",
    # EN: Nag Panchami, Shravana Shukla Panchami, is the day serpent deities (nagas) are worshipped.
    #     Images of snakes are drawn or installed and offered milk, flowers and sweets, with prayers
    #     for the family's protection. (In Gujarat, Nag Pancham falls later, in Bhadrapada.)
    "nag-panchami": "নাগ পঞ্চমী, শাওন মাহৰ শুক্ল পঞ্চমী, নাগ দেৱতাৰ পূজাৰ দিন। সাপৰ ছবি আঁকি বা স্থাপন কৰি গাখীৰ, ফুল আৰু মিঠাই অৰ্পণ কৰা হয়, পৰিয়ালৰ সুৰক্ষাৰ প্ৰাৰ্থনাৰে। (গুজৰাটত নাগ পঞ্চম পিছত, ভাদ মাহত পৰে।)",
    # EN: Kajari (Kajli, Badi) Teej, Bhadrapada Krishna Tritiya (purnimanta), is kept by married
    #     women of Uttar Pradesh, Bihar, Rajasthan and Madhya Pradesh. They fast, worship the neem
    #     tree (Neemadi Mata) and break the fast after offering arghya to the Moon; kajari folk
    #     songs are sung.
    "kajari-teej": "কাজৰী (কাজলী, বাড়ী) তীজ, ভাদ মাহৰ কৃষ্ণ তৃতীয়া (পূৰ্ণিমান্ত), উত্তৰ প্ৰদেশ, বিহাৰ, ৰাজস্থান আৰু মধ্য প্ৰদেশৰ বিবাহিতা মহিলাই পালন কৰে। তেওঁলোকে উপবাস কৰে, নিম গছৰ (নিমাড়ী মাতা) পূজা কৰে আৰু চন্দ্ৰলৈ অৰ্ঘ্য দিয়াৰ পিছত উপবাস ভাঙে; কাজৰী লোকগীত গোৱা হয়।",
    # EN: Hal Shashthi (Lalahi Chhath, Har Chhath), Bhadrapada Krishna Shashthi (purnimanta), is
    #     Lord Balarama's birthday, whose weapon is the plough (hal). Mothers fast for their
    #     children and eat nothing grown with a plough - often pasahi rice and buffalo milk.
    "hal-shashthi": "হল ষষ্ঠী (ললহী ছঠ, হৰ ছঠ), ভাদ মাহৰ কৃষ্ণ ষষ্ঠী (পূৰ্ণিমান্ত), ভগৱান বলৰামৰ জন্মদিন, যাৰ অস্ত্ৰ হল (লাঙল)। মাকসকলে সন্তানৰ বাবে উপবাস কৰে আৰু লাঙলে বোৱা একো নাখায় - প্ৰায়ে পসাহী চাউল আৰু ম'হৰ গাখীৰ।",
    # EN: Hartalika Teej, Bhadrapada Shukla Tritiya, honours Parvati's penance to win Shiva. Women
    #     keep a nirjala fast, make clay images of Shiva and Parvati, worship them (morning puja in
    #     Pratahkala is preferred), keep vigil at night and break the fast next morning.
    "hartalika-teej": "হৰতালিকা তীজ, ভাদ মাহৰ শুক্ল তৃতীয়া, শিৱক পাবলৈ পাৰ্বতীয়ে কৰা তপস্যাক সন্মান জনায়। মহিলাসকলে নিৰ্জলা উপবাস কৰে, শিৱ-পাৰ্বতীৰ মাটিৰ মূৰ্তি গঢ়ি পূজা কৰে (প্ৰাতঃকালৰ পূজা বেছি ভাল), ৰাতি জাগি থাকে আৰু পিছদিনা ৰাতিপুৱা উপবাস ভাঙে।",
    # EN: Rishi Panchami, Bhadrapada Shukla Panchami, honours the Saptarishis, the seven sages.
    #     Women in particular bathe, fast and worship the sages at midday (Madhyahna), seeking
    #     purification from faults committed unknowingly.
    "rishi-panchami": "ঋষি পঞ্চমী, ভাদ মাহৰ শুক্ল পঞ্চমী, সপ্তৰ্ষি, সাত ঋষিক সন্মান জনায়। বিশেষকৈ মহিলাসকলে স্নান কৰে, উপবাস কৰে আৰু অজানিতে হোৱা ভুলৰ শুদ্ধিৰ বাবে মধ্যাহ্নত ঋষিসকলৰ পূজা কৰে।",
    # EN: Anant Chaturdashi, Bhadrapada Shukla Chaturdashi, is the worship of Lord Vishnu as Anant.
    #     A sacred thread with fourteen knots (the anant sutra) is tied on the arm after puja; it is
    #     also the day Ganesh idols are immersed (Ganesh Visarjan).
    "anant-chaturdashi": "অনন্ত চতুৰ্দশী, ভাদ মাহৰ শুক্ল চতুৰ্দশী, ভগৱান বিষ্ণুৰ অনন্ত ৰূপৰ পূজা। পূজাৰ পিছত বাহুত চৈধ্যটা গাঁঠিৰ পবিত্ৰ সূতা (অনন্ত সূত্ৰ) বান্ধা হয়; এইদিনাই গণেশৰ মূৰ্তি বিসৰ্জনো (গণেশ বিসৰ্জন) কৰা হয়।",
    # EN: Pitru Paksha, the fortnight of the ancestors, runs from Pratipada to Amavasya of the dark
    #     half of Ashwin (purnimanta). On the tithi of an ancestor's passing, families offer tarpan
    #     and shraddha - pinda, food for Brahmins, cows, crows and dogs - in the Kutup, Rohina or
    #     Aparahna time.
    "pitru-paksha": "পিতৃ পক্ষ, পূৰ্বপুৰুষৰ পক্ষ, আহিন মাহৰ (পূৰ্ণিমান্ত) কৃষ্ণ পক্ষৰ প্ৰতিপদৰ পৰা অমাৱস্যালৈ চলে। পূৰ্বপুৰুষৰ মৃত্যুৰ তিথিত পৰিয়ালবোৰে তৰ্পণ আৰু শ্ৰাদ্ধ - পিণ্ড, ব্ৰাহ্মণ, গৰু, কাউৰী আৰু কুকুৰৰ বাবে খাদ্য - কুতুপ, ৰৌহিণ বা অপৰাহ্ণ সময়ত অৰ্পণ কৰে।",
    # EN: Sarva Pitru Amavasya (Mahalaya Amavasya) closes Pitru Paksha. Shraddha on this day reaches
    #     all ancestors, including those whose tithi is not known; it is done in the Kutup, Rohina
    #     or Aparahna time.
    "sarva-pitru-amavasya": "সৰ্বপিতৃ অমাৱস্যা (মহালয়া অমাৱস্যা)য়ে পিতৃ পক্ষ সামৰণি মাৰে। এইদিনা কৰা শ্ৰাদ্ধই তিথি নজনা পূৰ্বপুৰুষকে ধৰি সকলো পূৰ্বপুৰুষৰ ওচৰত পায়; ইয়াক কুতুপ, ৰৌহিণ বা অপৰাহ্ণ সময়ত কৰা হয়।",
    # EN: Narak Chaturdashi (Roop Chaudas), Kartika Krishna Chaturdashi (purnimanta), remembers
    #     Krishna's victory over Narakasura. Before sunrise, while the Moon is up, people take an
    #     oil bath with ubtan (Abhyang snan), and a lamp for Yama is lit in the evening.
    "narak-chaturdashi": "নৰক চতুৰ্দশী (ৰূপ চৌদশ), কাতি মাহৰ কৃষ্ণ চতুৰ্দশী (পূৰ্ণিমান্ত), কৃষ্ণই নৰকাসুৰক জয় কৰা কথা সোঁৱৰে। সূৰ্যোদয়ৰ আগতে, চন্দ্ৰ থাকোঁতে, মানুহে তেল আৰু উবটন লগাই স্নান (অভ্যঙ্গ স্নান) কৰে, আৰু সন্ধিয়া যমৰ বাবে প্ৰদীপ জ্বলোৱা হয়।",
    # EN: Tulsi Vivah, on Kartika Shukla Dwadashi, is the ceremonial wedding of the tulsi plant (as
    #     Vrinda) to Lord Vishnu as Shaligram. Families decorate the tulsi like a bride and perform
    #     the rites of a wedding; the Hindu wedding season begins after it.
    "tulsi-vivah": "তুলসী বিবাহ, কাতি মাহৰ শুক্ল দ্বাদশীত, তুলসী গছৰ (বৃন্দাৰূপে) ভগৱান বিষ্ণুৰ (শালগ্ৰামৰূপে) লগত আনুষ্ঠানিক বিয়া। পৰিয়ালবোৰে তুলসীক কইনাৰ দৰে সজায় আৰু বিয়াৰ ৰীতি পালন কৰে; ইয়াৰ পিছতেই হিন্দু বিয়াৰ ঋতু আৰম্ভ হয়।",
    # EN: Kartik Purnima ends the holy month of Kartika. It is a great day for bathing in the Ganga
    #     or a holy river and giving in charity, and also Guru Nanak Jayanti and Tripuri Purnima,
    #     when Shiva destroyed Tripurasura.
    "kartik-purnima": "কাৰ্তিক পূৰ্ণিমাই পবিত্ৰ কাতি মাহৰ সামৰণি মাৰে। এয়া গঙ্গা বা পবিত্ৰ নদীত স্নান আৰু দানৰ মহান দিন, আৰু গুৰু নানক জয়ন্তী আৰু ত্ৰিপুৰী পূৰ্ণিমাও, যেতিয়া শিৱে ত্ৰিপুৰাসুৰক বধ কৰিছিল।",
    # EN: Dev Deepawali, the 'Diwali of the gods', is celebrated on Kartik Purnima evening, above
    #     all on the ghats of Varanasi, which are lit with lakhs of diyas. It marks Shiva's victory
    #     over Tripurasura; lamps are offered to the Ganga in Pradosh kaal.
    "dev-deepawali": "দেৱ দীপাৱলী, ‘দেৱতাসকলৰ দীপাৱলী’, কাৰ্তিক পূৰ্ণিমাৰ সন্ধিয়া, বিশেষকৈ বাৰাণসীৰ ঘাটত, লাখ লাখ প্ৰদীপেৰে আলোকিত কৰি পালন কৰা হয়। ই ত্ৰিপুৰাসুৰৰ ওপৰত শিৱৰ বিজয় সূচায়; প্ৰদোষ কালত গঙ্গালৈ প্ৰদীপ অৰ্পণ কৰা হয়।",
}

# app/vrat_text.py NOTES["as"] — tradition notes on dates that differ between almanacs (key = festival slug)  [11]
VRAT_NOTES = {
    # EN: Dates follow Drik Panchang. When Bhadra covers the whole Purnima night and Purnima lasts
    #     most of the next day, Drik moves Holika Dahan to the next evening's Pradosh (as in 2026, 3
    #     March); some almanacs instead give a time late on the first night, after Bhadra ends.
    "holika-dahan": "তাৰিখবোৰ দৃক পঞ্জিকা অনুসৰি। যেতিয়া ভদ্ৰাই গোটেই পূৰ্ণিমাৰ ৰাতি ঢাকি ৰাখে আৰু পূৰ্ণিমা পিছদিনাৰ বেছিভাগ সময় থাকে, তেতিয়া দৃকে হোলিকা দহন পিছদিনাৰ সন্ধিয়াৰ প্ৰদোষলৈ নিয়ে (যেনে 2026 ত, 3 মাৰ্চ); কিছুমান পঞ্জিকাই ভদ্ৰা শেষ হোৱাৰ পিছত প্ৰথম ৰাতিৰ শেষৰ ফালৰ এটা সময় দিয়ে।",
    # EN: Dates follow Drik Panchang's Smarta (default) reckoning, with Rohini nakshatra at midnight
    #     preferred. Vaishnava/ISKCON communities sometimes keep Janmashtami a day later.
    "janmashtami": "তাৰিখবোৰ দৃক পঞ্জিকাৰ স্মাৰ্ত (সাধাৰণ) গণনা অনুসৰি, মাজৰাতি ৰোহিণী নক্ষত্ৰ থকাটোক অগ্ৰাধিকাৰ দি। বৈষ্ণৱ/ইস্কনৰ সম্প্ৰদায়বোৰে কেতিয়াবা জন্মাষ্টমী এদিন পিছত পালন কৰে।",
    # EN: This is the Smarta (householder) date. Where Ekadashi spans two days, Vaishnavas may fast
    #     on the second day.
    "devuthani-ekadashi": "এয়া স্মাৰ্ত (গৃহস্থ)ৰ তাৰিখ। একাদশী দুদিনত বিয়পি থাকিলে বৈষ্ণৱসকলে দ্বিতীয় দিনা উপবাস কৰিব পাৰে।",
    # EN: Dates follow Drik Panchang (Dashami in Aparahna, Shravana nakshatra preferred). In Bengal
    #     and some almanacs Vijayadashami can fall a day later.
    "dussehra": "তাৰিখবোৰ দৃক পঞ্জিকা অনুসৰি (অপৰাহ্ণত দশমী, শ্ৰৱণ নক্ষত্ৰক অগ্ৰাধিকাৰ দি)। বংগ আৰু কিছুমান পঞ্জিকাত বিজয়া দশমী এদিন পিছত পৰিব পাৰে।",
    # EN: Dates follow Drik Panchang (Ashtami at midday; when it is at sunrise only briefly, as in
    #     2023, the previous day). Nahay-khay is the day before and parana the next morning;
    #     regional panchangs (e.g. Mithila) can differ by a day.
    "jivitputrika": "তাৰিখবোৰ দৃক পঞ্জিকা অনুসৰি (মধ্যাহ্নত অষ্টমী; সূৰ্যোদয়ত অষ্টমী অলপ সময়হে থাকিলে, যেনে 2023 ত, আগদিনা)। নহায়-খায় আগদিনা আৰু পাৰণ পিছদিনা ৰাতিপুৱা; আঞ্চলিক পঞ্জিকা (যেনে মিথিলা)ত এদিনৰ পাৰ্থক্য হ'ব পাৰে।",
    # EN: Two traditions: North India keeps Vat Savitri on Jyeshtha Amavasya (this date);
    #     Maharashtra, Gujarat and the south keep it as Vat Purnima fifteen days later.
    "vat-savitri": "দুটা পৰম্পৰা: উত্তৰ ভাৰতে বট সাৱিত্ৰী জেঠ মাহৰ অমাৱস্যাত (এই তাৰিখ) পালন কৰে; মহাৰাষ্ট্ৰ, গুজৰাট আৰু দক্ষিণে ইয়াক পোন্ধৰ দিন পিছত বট পূৰ্ণিমা হিচাপে পালন কৰে।",
    # EN: Two traditions: this is the Purnima (amanta) date of Maharashtra, Gujarat and the south;
    #     North India keeps Vat Savitri on the Amavasya fifteen days earlier.
    "vat-purnima": "দুটা পৰম্পৰা: এয়া মহাৰাষ্ট্ৰ, গুজৰাট আৰু দক্ষিণৰ পূৰ্ণিমা (অমান্ত) তাৰিখ; উত্তৰ ভাৰতে বট সাৱিত্ৰী পোন্ধৰ দিন আগৰ অমাৱস্যাত পালন কৰে।",
    # EN: When Jyeshtha is doubled (an adhika month, as in 2026), Drik Panchang keeps Ganga Dussehra
    #     in the adhika Jyeshtha; some almanacs give the nija Jyeshtha date a month later.
    "ganga-dussehra": "জেঠ মাহ দুবাৰ পৰিলে (অধিক মাহ, যেনে 2026 ত), দৃক পঞ্জিকাই গঙ্গা দশহৰা অধিক জেঠতে ৰাখে; কিছুমান পঞ্জিকাই নিজ জেঠৰ তাৰিখ এমাহ পিছত দিয়ে।",
    # EN: Drik Panchang counts Pitru Paksha from the Pratipada shraddha; Purnima shraddha is on the
    #     day before, and many calendars start the fortnight there.
    "pitru-paksha": "দৃক পঞ্জিকাই পিতৃ পক্ষ প্ৰতিপদ শ্ৰাদ্ধৰ পৰা গণনা কৰে; পূৰ্ণিমা শ্ৰাদ্ধ আগদিনা, আৰু বহুতো পঞ্জিকাই পক্ষটো তাৰ পৰাই আৰম্ভ কৰে।",
    # EN: Drik Panchang publishes Dev Deepawali for Varanasi; the date here uses the same rule
    #     (Purnima in Pradosh), and the Pradosh kaal shown is New Delhi's.
    "dev-deepawali": "দৃক পঞ্জিকাই দেৱ দীপাৱলী বাৰাণসীৰ বাবে প্ৰকাশ কৰে; ইয়াত দিয়া তাৰিখে একেটা নিয়মেই (প্ৰদোষত পূৰ্ণিমা) মানে, আৰু দেখুওৱা প্ৰদোষ কাল নতুন দিল্লীৰ।",
    # EN: This is the snan-daan day (Purnima at sunrise). When Purnima begins the previous
    #     afternoon, the Purnima fast and Dev Deepawali can fall a day earlier.
    "kartik-purnima": "এয়া স্নান-দানৰ দিন (সূৰ্যোদয়ত পূৰ্ণিমা)। পূৰ্ণিমা আগদিনা অপৰাহ্ণত আৰম্ভ হ'লে, পূৰ্ণিমাৰ উপবাস আৰু দেৱ দীপাৱলী এদিন আগতে পৰিব পাৰে।",
}

# app/vrat_text.py RULES["as"] — 'how the date is fixed' sentences: head {month}, tithi {paksha} {tithi}, rule.<kind>, key.<observance>  [16]
VRAT_RULES = {
    # EN: {month} (amanta)
    # keep: {month}
    "head": "{month} (অমান্ত) ",
    # EN: {paksha} {tithi}:
    # keep: {paksha} {tithi}
    "tithi": "{paksha} {tithi}: ",
    # EN: tithi prevailing at sunrise
    "rule.udaya": "সূৰ্যোদয়ত থকা তিথি",
    # EN: tithi prevailing in Pratahkala (first fifth of the day)
    "rule.pratah": "প্ৰাতঃকালত (দিনৰ প্ৰথম পঞ্চমাংশ) থকা তিথি",
    # EN: tithi prevailing in the forenoon (purvahna)
    "rule.purvahna": "পূৰ্বাহ্নত (দিনৰ আগভাগ) থকা তিথি",
    # EN: tithi prevailing at Madhyahna (midday fifth of the day)
    "rule.madhyahna": "মধ্যাহ্নত (দিনৰ মাজৰ পঞ্চমাংশ) থকা তিথি",
    # EN: tithi prevailing at Aparahna (fourth fifth of the day)
    "rule.aparahna": "অপৰাহ্ণত (দিনৰ চতুৰ্থ পঞ্চমাংশ) থকা তিথি",
    # EN: first day on which the tithi is present between sunrise and sunset
    "rule.dina": "যিদিনা সূৰ্যোদয় আৰু সূৰ্যাস্তৰ মাজত প্ৰথমবাৰৰ বাবে তিথি থাকে সেইদিনা",
    # EN: tithi prevailing at sunset
    "rule.sayahna": "সূৰ্যাস্তত থকা তিথি",
    # EN: tithi prevailing in Pradosh kaal (after sunset)
    "rule.pradosh": "প্ৰদোষ কালত (সূৰ্যাস্তৰ পিছত) থকা তিথি",
    # EN: tithi prevailing at Nishita kaal (midnight)
    "rule.nishita": "নিশীথ কালত (মাজৰাতি) থকা তিথি",
    # EN: tithi prevailing at moonrise
    "rule.moonrise": "চন্দ্ৰোদয়ত থকা তিথি",
    # EN: Smarta: Ekadashi prevailing at sunrise (second day if at two sunrises); parana next day
    #     after sunrise and after Hari Vasara, within Pratahkala and before Dwadashi ends
    "key.ekadashi": "স্মাৰ্ত: সূৰ্যোদয়ত একাদশী থাকিলে (দুটা সূৰ্যোদয়ত থাকিলে দ্বিতীয় দিনা); পাৰণ পিছদিনা সূৰ্যোদয়ৰ পিছত আৰু হৰিবাসৰ শেষ হোৱাৰ পিছত, প্ৰাতঃকালৰ ভিতৰত আৰু দ্বাদশী শেষ হোৱাৰ আগতে",
    # EN: the Sun's entry into sidereal Makara (Capricorn); punya kaal follows it until sunset
    "key.makar_sankranti": "সূৰ্যই নিৰয়ন মকৰ ৰাশিত প্ৰৱেশ কৰা; ইয়াৰ পিছত সূৰ্যাস্তলৈকে পুণ্যকাল",
    # EN: the day before Makar Sankranti
    "key.lohri": "মকৰ সংক্ৰান্তিৰ আগদিনা",
    # EN: the day after Holika Dahan
    "key.holi": "হোলিকা দহনৰ পিছদিনা",
}

# ----------------------------------------------------------------------------
# nakshatra /nakshatra /rashi /naam-se-kundali-milan
# ----------------------------------------------------------------------------

# app/nakshatra_page_text.py TEXT["as"] — page text of /nakshatra /rashi (nakshatra_pages.py)  [88]
NAKSHATRA_PAGE_TEXT = {
    # EN: Get your free kundali — find your exact birth nakshatra and Moon sign
    "kundali_cta": "বিনামূলীয়া কুণ্ডলী বনাওক — আপোনাৰ ঠিক জন্ম নক্ষত্ৰ আৰু চন্দ্ৰ ৰাশি জানি লওক",
    # EN: More free tools
    "more.heading": "আৰু বিনামূলীয়া সেৱা",
    # EN: All 27 nakshatras
    "more.naks": "সকলো 27 টা নক্ষত্ৰ",
    # EN: All 12 rashis
    "more.rashis": "সকলো 12 টা ৰাশি",
    # EN: Naam se Kundali Milan
    "more.milan": "নামৰ আখৰেৰে কুণ্ডলী মিলন",
    # EN: Kundali Milan (36 guna)
    "more.kundali_milan": "কুণ্ডলী মিলন (36 গুণ)",
    # EN: Today's Rashifal
    "more.rashifal": "আজিৰ ৰাশিফল",
    # EN: Today's Panchang
    "more.panchang": "আজিৰ পঞ্জিকা",
    # EN: All 27 nakshatras
    "list.naks": "সকলো 27 টা নক্ষত্ৰ",
    # EN: All 12 rashis
    "list.rashis": "সকলো 12 টা ৰাশি",
    # EN: {name} ({english})
    # keep: {name}
    "sign": "{name}",
    # EN: {name} · {english}
    # keep: {name}
    "sign.pill": "{name}",
    # EN: <strong>Today the Moon is in {name} (at sunrise in New Delhi).</strong>
    # keep: {name}
    "today.same": "<strong>আজি (নতুন দিল্লীত সূৰ্যোদয়ৰ সময়ত) চন্দ্ৰ {name} নক্ষত্ৰত আছে।</strong>",
    # EN: Today's nakshatra is <a href="{href}"><strong>{name}</strong></a> (at sunrise in New
    #     Delhi).
    # keep: {href} {name}
    "today.other": "আজিৰ নক্ষত্ৰ (নতুন দিল্লীত সূৰ্যোদয়ৰ সময়ত) <a href=\"{href}\"><strong>{name}</strong></a>।",
    # EN: Its end time, the tithi and Rahu Kaal are on <a href="{pan}">today's Panchang</a>.
    # keep: {pan}
    "today.tail": " ইয়াৰ শেষ হোৱাৰ সময়, তিথি আৰু ৰাহুকাল <a href=\"{pan}\">আজিৰ পঞ্জিকাত</a> চাওক।",
    # EN: Nakshatras
    "crumb.naks": "নক্ষত্ৰ",
    # EN: Rashis
    "crumb.rashis": "ৰাশি",
    # EN: Nakshatra not found
    "nf.nak": "নক্ষত্ৰ পোৱা নগ'ল",
    # EN: Rashi not found
    "nf.rashi": "ৰাশি পোৱা নগ'ল",
    # EN: Nature and traits
    "trait_head": "স্বভাৱ আৰু বৈশিষ্ট্য",
    # EN: male
    "gender.male": "পুৰুষ",
    # EN: female
    "gender.female": "মহিলা",
    # EN: Fire
    "element.Fire": "অগ্নি",
    # EN: Earth
    "element.Earth": "পৃথিৱী",
    # EN: Air
    "element.Air": "বায়ু",
    # EN: Water
    "element.Water": "জল",
    # EN: Movable (Chara)
    "quality.Cardinal": "চৰ",
    # EN: Fixed (Sthira)
    "quality.Fixed": "স্থিৰ",
    # EN: Dual (Dwiswabhava)
    "quality.Mutable": "দ্বিস্বভাৱ",
    # EN: {name} Nakshatra — Deity, Lord, Gana, Yoni, Nadi & Name Letters | {brand}
    # keep: {brand} {name}
    "nak.title": "{name} নক্ষত্ৰ — দেৱতা, অধিপতি, গণ, যোনি, নাড়ী আৰু নামাক্ষৰ | {brand}",
    # EN: {name} nakshatra ({name_hi}): {span}, ruled by {lord}, deity {deity_short}, {gana} gana,
    #     {nadi} nadi, {yoni} yoni. Name syllables {lat} and traits.
    # keep: {gana} {lord} {nadi} {name} {span} {yoni}
    # may also use: {name_en}
    "nak.desc": "{name} নক্ষত্ৰ: {span}, অধিপতি গ্ৰহ {lord}, {gana} গণ, {nadi} নাড়ী, {yoni} যোনি। চাৰি পাদৰ নামাক্ষৰ আৰু স্বভাৱ।",
    # EN: <h1>{name} Nakshatra</h1>
    # keep: {name}
    "nak.h1": "<h1>{name} নক্ষত্ৰ</h1>",
    # EN: <p class="hi" lang="hi">{name_hi} नक्षत्र</p>
    # may also use: {name_en} {name}
    "nak.sub": "<p class=\"hi\">{name} নক্ষত্ৰ</p>",
    # EN: <p class="note">These are traditional tendencies, not verdicts. Your full kundali —
    #     ascendant, planets and dasha — gives the personal picture.</p>
    "nak.trait_note": "<p class=\"note\">এইবোৰ পৰম্পৰাগত প্ৰৱণতা, চূড়ান্ত ৰায় নহয়। আপোনাৰ সম্পূৰ্ণ কুণ্ডলী — লগ্ন, গ্ৰহ আৰু দশা — য়ে ব্যক্তিগত ছবি দিয়ে।</p>",
    # EN: Number
    "f.number": "ক্ৰম",
    # EN: {n} of 27
    # keep: {n}
    "f.number_v": "27 টাৰ ভিতৰত {n} নম্বৰ",
    # EN: Span (sidereal)
    "f.span": "বিস্তাৰ (নিৰয়ন)",
    # EN: Rashi
    "f.rashi": "ৰাশি",
    # EN: Ruling planet (Vimshottari lord)
    "f.lord": "অধিপতি গ্ৰহ (বিংশোত্তৰী)",
    # EN: {lord} <small>{years}-year mahadasha</small>
    # keep: {lord} {years}
    "f.lord_v": "{lord} <small>মহাদশা {years} বছৰ</small>",
    # EN: Deity
    "f.deity": "দেৱতা",
    # EN: Symbol
    "f.symbol": "প্ৰতীক",
    # EN: Gana
    "f.gana": "গণ",
    # EN: {gana} <small lang="hi">{gana_hi}</small>
    # keep: {gana}
    "f.gana_v": "{gana}",
    # EN: Yoni (animal)
    "f.yoni": "যোনি (প্ৰাণী)",
    # EN: Nadi
    "f.nadi": "নাড়ী",
    # EN: Varna (from its rashi, as used in Guna Milan)
    "f.varna": "বৰ্ণ (ৰাশি অনুসৰি, গুণ মিলনত ব্যৱহৃত)",
    # EN: Name syllables (namakshar)
    "f.syl": "নামৰ আদ্যক্ষৰ (নামাক্ষৰ)",
    # EN: <span class="syl" lang="hi">{syl}</span> <small>{lat}</small>
    # keep: {syl}
    "f.syl_v": "<span class=\"syl\">{syl}</span>",
    # EN: The four padas and their name syllables
    "pada.title": "চাৰিটা পাদ আৰু সিহঁতৰ নামাক্ষৰ",
    # EN: <tr><th>Pada</th><th>Span</th><th>Rashi</th><th>Name syllable</th></tr>
    "pada.head": "<tr><th>পাদ</th><th>বিস্তাৰ</th><th>ৰাশি</th><th>নামাক্ষৰ</th></tr>",
    # EN: <p class="note">Traditionally a child's name begins with the syllable of the pada the Moon
    #     occupied at birth (namakshar). Syllables follow the 108-pada Swar Siddhanta list (the
    #     Avakahada Chakra) as published by Drik Panchang.</p>
    "pada.note": "<p class=\"note\">পৰম্পৰা অনুসৰি শিশুৰ নাম জন্মৰ সময়ত চন্দ্ৰ থকা পাদৰ আখৰেৰে আৰম্ভ হয় (নামাক্ষৰ)। আখৰবোৰ দৃক পঞ্জিকাত প্ৰকাশিত স্বৰ-সিদ্ধান্তৰ 108 পাদৰ তালিকা (অৱকহড়া চক্ৰ) অনুসৰি দিয়া।</p>",
    # EN: Related
    "rel.heading": "সম্পৰ্কিত",
    # EN: Today's {name} Rashifal
    # keep: {name}
    "rel.rashifal": "আজিৰ {name} ৰাশিফল",
    # EN: The 27 Nakshatras — Lords, Deities, Gana & Name Syllables | {brand}
    # keep: {brand}
    "ni.title": "27 টা নক্ষত্ৰ — অধিপতি, দেৱতা, গণ আৰু নামাক্ষৰৰ তালিকা | {brand}",
    # EN: All 27 nakshatras from Ashwini to Revati: span, rashi, ruling planet, deity, gana, yoni,
    #     nadi and the name syllables of all four padas — consistent with our Kundali Milan tables.
    "ni.desc": "অশ্বিনীৰ পৰা ৰেৱতীলৈ সকলো 27 টা নক্ষত্ৰ: বিস্তাৰ, ৰাশি, অধিপতি গ্ৰহ, দেৱতা, গণ, যোনি, নাড়ী আৰু চাৰিওটা পাদৰ নামাক্ষৰ — আমাৰ কুণ্ডলী মিলনৰ তালিকাৰ লগত মিলাই।",
    # EN: <h1>The 27 Nakshatras</h1>
    "ni.h1": "<h1>27 টা নক্ষত্ৰ</h1>",
    # EN: <p class="hi" lang="hi">27 नक्षत्र</p>
    "ni.sub": "<p class=\"hi\">অশ্বিনীৰ পৰা ৰেৱতীলৈ</p>",
    # EN: <p>Vedic astrology divides the zodiac into 27 nakshatras (lunar mansions) of 13°20′ each,
    #     and each nakshatra into four padas of 3°20′. The 108 padas fall exactly nine to a sign
    #     across the 12 rashis. Your birth nakshatra is the one the Moon occupied when you were
    #     born: it starts your Vimshottari dasha and drives the Tara, Yoni, Gana and Nadi kootas of
    #     Kundali Milan.</p>
    "ni.intro": "<p>বৈদিক জ্যোতিষে ৰাশিচক্ৰক 13°20′ কৈ 27 টা নক্ষত্ৰত ভাগ কৰে, আৰু প্ৰতিটো নক্ষত্ৰক 3°20′ ৰ চাৰিটা পাদত। মুঠ 108 টা পাদ 12 টা ৰাশিত ঠিক নটাকৈ পৰে। আপোনাৰ জন্ম নক্ষত্ৰ হ'ল জন্মৰ সময়ত চন্দ্ৰ থকা নক্ষত্ৰ: তাৰ পৰাই বিংশোত্তৰী দশা আৰম্ভ হয়, আৰু কুণ্ডলী মিলনৰ তাৰা, যোনি, গণ আৰু নাড়ী কূট ইয়াৰ ওপৰতে নিৰ্ভৰ কৰে।</p>",
    # EN: <tr><th>#</th><th>Nakshatra</th><th>Rashi</th><th>Lord</th><th>Gana</th><th>Name
    #     syllables</th></tr>
    "ni.head": "<tr><th>#</th><th>নক্ষত্ৰ</th><th>ৰাশি</th><th>অধিপতি</th><th>গণ</th><th>নামাক্ষৰ</th></tr>",
    # EN: {name} Rashi ({english}) — Lord, Element, Nakshatras & Name Letters | {brand}
    # keep: {brand} {name}
    # may also use: {english}
    "rs.title": "{name} ৰাশি ({english}) — অধিপতি, তত্ত্ব, নক্ষত্ৰ আৰু নামাক্ষৰ | {brand}",
    # EN: {name} rashi ({english} Moon sign, {name_hi}): ruled by {lord}, {element_lower} element,
    #     {quality_lower} quality. Its 9 nakshatra padas, name syllables ({lat}) and traits.
    # keep: {lord} {name}
    # may also use: {element_lower} {element} {english} {name_en} {quality_lower} {quality}
    "rs.desc": "{name} ৰাশি ({english} চন্দ্ৰ ৰাশি): অধিপতি {lord}, {element_lower} তত্ত্ব, {quality_lower} স্বভাৱ। ইয়াৰ 9 টা নক্ষত্ৰ-পাদ, নামাক্ষৰ আৰু স্বভাৱ।",
    # EN: <h1>{name} Rashi — {english} Moon Sign</h1>
    # keep: {name}
    # may also use: {english}
    "rs.h1": "<h1>{name} ৰাশি — {english} চন্দ্ৰ ৰাশি</h1>",
    # EN: <p class="hi" lang="hi">{name_hi} राशि</p>
    # may also use: {english} {name_en} {name}
    "rs.sub": "<p class=\"hi\">{name} ৰাশি · {english}</p>",
    # EN: Read today's {name} Rashifal
    # keep: {name}
    "rs.today": "আজিৰ {name} ৰাশিফল পঢ়ক",
    # EN: <p class="note">In Vedic astrology "rashi" usually means the Moon sign — the sign the Moon
    #     occupied at birth, in the sidereal zodiac. It is often different from a Western sun
    #     sign.</p>
    "rs.note": "<p class=\"note\">বৈদিক জ্যোতিষত “ৰাশি” বুলিলে সাধাৰণতে চন্দ্ৰ ৰাশি বুজায় — জন্মৰ সময়ত নিৰয়ন ৰাশিচক্ৰত চন্দ্ৰ থকা ৰাশি। ই প্ৰায়ে পাশ্চাত্য সূৰ্য ৰাশিতকৈ বেলেগ হয়।</p>",
    # EN: Number
    "r.number": "ক্ৰম",
    # EN: {n} of 12
    # keep: {n}
    "r.number_v": "12 টাৰ ভিতৰত {n} নম্বৰ",
    # EN: Span (sidereal zodiac)
    "r.span": "বিস্তাৰ (নিৰয়ন ৰাশিচক্ৰ)",
    # EN: Sign lord
    "r.lord": "ৰাশিৰ অধিপতি",
    # EN: Element
    "r.element": "তত্ত্ব",
    # EN: Quality
    "r.quality": "স্বভাৱ (চৰ / স্থিৰ / দ্বিস্বভাৱ)",
    # EN: Varna (used in Guna Milan)
    "r.varna": "বৰ্ণ (গুণ মিলনত ব্যৱহৃত)",
    # EN: Nakshatras
    "r.naks": "নক্ষত্ৰ",
    # EN: Name syllables (namakshar)
    "r.syl": "নামৰ আদ্যক্ষৰ (নামাক্ষৰ)",
    # EN: <span class="syl" lang="hi">{syl}</span>
    # keep: {syl}
    "r.syl_v": "<span class=\"syl\">{syl}</span>",
    # EN: The nine nakshatra padas in this sign
    "rp.title": "এই ৰাশিৰ নটা নক্ষত্ৰ-পাদ",
    # EN: <tr><th>Nakshatra</th><th>Pada</th><th>Degrees in sign</th><th>Syllable</th></tr>
    "rp.head": "<tr><th>নক্ষত্ৰ</th><th>পাদ</th><th>ৰাশিত অংশ</th><th>আখৰ</th></tr>",
    # EN: The 12 Rashis — Lords, Elements, Nakshatras & Name Letters | {brand}
    # keep: {brand}
    "ri.title": "12 টা ৰাশি — অধিপতি, তত্ত্ব, নক্ষত্ৰ আৰু নামাক্ষৰৰ তালিকা | {brand}",
    # EN: All 12 rashis (Vedic Moon signs) from Mesh to Meen: sign lord, element, quality, the nine
    #     nakshatra padas in each and their name syllables (namakshar).
    "ri.desc": "মেষৰ পৰা মীনলৈ সকলো 12 টা ৰাশি (বৈদিক চন্দ্ৰ ৰাশি): ৰাশিৰ অধিপতি, তত্ত্ব, স্বভাৱ, প্ৰতিটোৰ নটা নক্ষত্ৰ-পাদ আৰু নামৰ আদ্যক্ষৰ (নামাক্ষৰ)।",
    # EN: <h1>The 12 Rashis (Moon Signs)</h1>
    "ri.h1": "<h1>12 টা ৰাশি (চন্দ্ৰ ৰাশি)</h1>",
    # EN: <p class="hi" lang="hi">12 राशियाँ</p>
    "ri.sub": "<p class=\"hi\">মেষৰ পৰা মীনলৈ</p>",
    # EN: <p>Each rashi spans 30° of the sidereal zodiac and holds exactly nine nakshatra padas.
    #     Your rashi is your Moon sign — the sign the Moon occupied at birth — and it is what
    #     rashifal, Sade Sati and Kundali Milan are read from.</p>
    "ri.intro": "<p>প্ৰতিটো ৰাশিয়ে নিৰয়ন ৰাশিচক্ৰৰ 30° ঠাই লয় আৰু তাত ঠিক নটা নক্ষত্ৰ-পাদ থাকে। আপোনাৰ ৰাশি হ'ল আপোনাৰ চন্দ্ৰ ৰাশি — জন্মৰ সময়ত চন্দ্ৰ থকা ৰাশি — আৰু ৰাশিফল, সাড়ে সাতি আৰু কুণ্ডলী মিলন ইয়াৰ পৰাই চোৱা হয়।</p>",
    # EN: <tr><th>Rashi</th><th>Lord</th><th>Element</th><th>Nakshatras</th><th>Name
    #     syllables</th></tr>
    "ri.head": "<tr><th>ৰাশি</th><th>অধিপতি</th><th>তত্ত্ব</th><th>নক্ষত্ৰ</th><th>নামাক্ষৰ</th></tr>",
    # EN: {name} <small>{english}</small>
    # keep: {name}
    # may also use: {english}
    "ri.name": "{name} <small>{english}</small>",
    # EN: Vata
    "humour.Vata": "বাত",
    # EN: Pitta
    "humour.Pitta": "পিত্ত",
    # EN: Kapha
    "humour.Kapha": "কফ",
}

# app/nakshatra_text.py NAKSHATRA_TRAITS["as"] — character paragraph of each of the 27 nakshatras (key = slug)  [27]
NAKSHATRA_TRAITS = {
    # EN: Ashwini is the first nakshatra, ruled by the Ashwini Kumaras, the twin healers of the
    #     gods, and symbolised by a horse's head. People with the Moon here are often quick,
    #     energetic and eager to begin things — the first to help, the first to try something new.
    #     Tradition links Ashwini with healing, speed and fresh starts, so many feel drawn to
    #     medicine, sport, travel or any work that needs swift, practical action. The gift of this
    #     nakshatra is initiative and a youthful optimism; the lesson is patience, finishing what
    #     was started with the same enthusiasm with which it began.
    "ashwini": "অশ্বিনী প্ৰথম নক্ষত্ৰ; ইয়াৰ অধিপতি অশ্বিনী কুমাৰ, দেৱতাসকলৰ যমজ চিকিৎসক, আৰু প্ৰতীক ঘোঁৰাৰ মূৰ। এই নক্ষত্ৰত চন্দ্ৰ থকা মানুহ প্ৰায়ে চঞ্চল, উদ্যমী আৰু কাম আৰম্ভ কৰিবলৈ আগ্ৰহী হয় — সহায় কৰিবলৈ প্ৰথমজন, নতুন কিবা চেষ্টা কৰিবলৈ প্ৰথমজন। পৰম্পৰাই অশ্বিনীক আৰোগ্য, গতি আৰু নতুন আৰম্ভণিৰ লগত সাঙুৰে, গতিকে বহুতে চিকিৎসা, খেল-ধেমালি, ভ্ৰমণ বা খৰ আৰু ব্যৱহাৰিক পদক্ষেপ লাগিবলগীয়া কামলৈ আকৰ্ষিত হয়। এই নক্ষত্ৰৰ দান হ'ল উদ্যম আৰু যুৱসুলভ আশাবাদ; ইয়াৰ শিক্ষা হ'ল ধৈৰ্য — যি উৎসাহেৰে কাম আৰম্ভ কৰা হৈছিল, সেই একে উৎসাহেৰে শেষ কৰা।",
    # EN: Bharani is ruled by Yama, the lord of dharma, and its symbol is the yoni, the womb that
    #     carries and protects new life. People with the Moon here often have strong will, deep
    #     feelings and a serious sense of responsibility. They tend to carry their commitments
    #     through to the end and are not easily swayed. Tradition sees Bharani as the nakshatra of
    #     bearing and nurturing — holding something until it is ready to be born — so creativity,
    #     family, art and work that asks for endurance suit it well. Its strength is steadfastness;
    #     its lesson is balancing desire with restraint and kindness.
    "bharani": "ভৰণীৰ অধিপতি যম, ধৰ্মৰ অধিপতি, আৰু ইয়াৰ প্ৰতীক যোনি — নতুন জীৱনক বহন আৰু ৰক্ষা কৰা গৰ্ভ। এই নক্ষত্ৰত চন্দ্ৰ থকা মানুহৰ প্ৰায়ে দৃঢ় ইচ্ছাশক্তি, গভীৰ অনুভূতি আৰু দায়িত্ববোধৰ গম্ভীৰ ভাৱ থাকে। তেওঁলোকে নিজৰ প্ৰতিশ্ৰুতি শেষলৈকে পালন কৰে আৰু সহজে বিচলিত নহয়। পৰম্পৰাই ভৰণীক বহন আৰু লালন-পালনৰ নক্ষত্ৰ বুলি গণ্য কৰে — কিবা এটা জন্ম লোৱাৰ সময় নোহোৱালৈকে ধৰি ৰখা — সেয়ে সৃজনশীলতা, পৰিয়াল, কলা আৰু সহনশীলতা লাগিবলগীয়া কাম ইয়াৰ বাবে উপযুক্ত। ইয়াৰ শক্তি হ'ল অটলতা; ইয়াৰ শিক্ষা হ'ল ইচ্ছাক সংযম আৰু দয়াৰ লগত সমতা ৰখা।",
    # EN: Krittika is ruled by Agni, the sacred fire, and symbolised by a razor or a flame. Fire
    #     purifies and cuts through confusion, and people with the Moon here are often direct,
    #     principled and sharp in judgement. They can be protective of those they love and are
    #     willing to say what needs to be said. Krittika is also the nakshatra of the six mothers
    #     who nursed Kartikeya, so beneath the sharpness there is real warmth and care. Teaching,
    #     cooking, leadership and any work that needs clarity suit it. Its lesson is to let the fire
    #     warm and guide rather than burn.
    "krittika": "কৃত্তিকাৰ অধিপতি অগ্নি, পবিত্ৰ জুই, আৰু প্ৰতীক খুৰ বা জুইৰ শিখা। জুইয়ে শুদ্ধ কৰে আৰু দ্বিধা কাটি পেলায়, আৰু এই নক্ষত্ৰত চন্দ্ৰ থকা মানুহ প্ৰায়ে পোনপটীয়া, নীতিবান আৰু তীক্ষ্ণ বিচাৰৰ হয়। তেওঁলোকে প্ৰিয়জনক ৰক্ষা কৰিবলৈ আগ্ৰহী আৰু কোৱা প্ৰয়োজনীয় কথা কবলৈ সাহসী। কৃত্তিকা কাৰ্তিকেয়ক পালন কৰা ছজনী মাতৃৰো নক্ষত্ৰ, সেয়ে তীক্ষ্ণতাৰ তলত প্ৰকৃত উষ্ণতা আৰু যত্ন থাকে। শিক্ষকতা, ৰন্ধন, নেতৃত্ব আৰু স্পষ্টতা লাগিবলগীয়া যিকোনো কাম ইয়াৰ বাবে উপযুক্ত। ইয়াৰ শিক্ষা হ'ল জুইয়ে পুৰি নেপেলাই উষ্ণতা আৰু পথ দেখুৱাওক।",
    # EN: Rohini is ruled by Brahma, the creator, and symbolised by a chariot or ox-cart. It is said
    #     to be the Moon's favourite nakshatra, and people with the Moon here are often warm,
    #     attractive, artistic and fond of comfort and beauty. They have a gift for making things
    #     grow — gardens, homes, businesses and relationships. Tradition associates Rohini with
    #     fertility, abundance and steady progress, so agriculture, the arts, design, food and
    #     hospitality suit it well. Its nature is gentle and settled; its lesson is to enjoy what is
    #     beautiful without holding on too tightly to it.
    "rohini": "ৰোহিণীৰ অধিপতি ব্ৰহ্মা, সৃষ্টিকৰ্তা, আৰু প্ৰতীক ৰথ বা গৰু-গাড়ী। কোৱা হয় এইটো চন্দ্ৰৰ প্ৰিয় নক্ষত্ৰ, আৰু এই নক্ষত্ৰত চন্দ্ৰ থকা মানুহ প্ৰায়ে উষ্ণ, আকৰ্ষণীয়, শিল্পমনা আৰু আৰাম আৰু সৌন্দৰ্যপ্ৰিয় হয়। বস্তু বৃদ্ধি কৰাত তেওঁলোকৰ বিশেষ দক্ষতা — বাগিচা, ঘৰ, ব্যৱসায় আৰু সম্পৰ্ক। পৰম্পৰাই ৰোহিণীক উৰ্বৰতা, প্ৰাচুৰ্য আৰু স্থিৰ উন্নতিৰ লগত জড়ায়, সেয়ে কৃষি, কলা, ডিজাইন, খাদ্য আৰু আতিথ্য ইয়াৰ বাবে উপযুক্ত। ইয়াৰ স্বভাৱ কোমল আৰু স্থিৰ; ইয়াৰ শিক্ষা হ'ল সুন্দৰ বস্তুক অত বেছি নিচেপাকৈ ধৰি নাৰাখি উপভোগ কৰা।",
    # EN: Mrigashira is ruled by Soma, the Moon, and its symbol is a deer's head — the deer that is
    #     always alert, curious and searching. People with the Moon here are often gentle,
    #     inquisitive and fond of learning, travel and conversation. They enjoy exploring ideas and
    #     places and rarely stop asking questions. Tradition sees Mrigashira as the seeker's
    #     nakshatra, which suits research, writing, teaching, trade and any work that rewards
    #     curiosity. Its charm is a light, friendly mind; its lesson is to settle on what has been
    #     found, so that the search leads somewhere rather than becoming restlessness.
    "mrigashira": "মৃগশিৰাৰ অধিপতি সোম, চন্দ্ৰ, আৰু ইয়াৰ প্ৰতীক হৰিণৰ মূৰ — সদায় সজাগ, কৌতূহলী আৰু সন্ধানকাৰী হৰিণ। এই নক্ষত্ৰত চন্দ্ৰ থকা মানুহ প্ৰায়ে কোমল, জিজ্ঞাসু আৰু শিক্ষা, ভ্ৰমণ আৰু কথোপকথনপ্ৰিয় হয়। তেওঁলোকে নতুন ধাৰণা আৰু ঠাই অন্বেষণ কৰি ভাল পায় আৰু প্ৰশ্ন সোধা কমকৈয়ে বন্ধ কৰে। পৰম্পৰাই মৃগশিৰাক সন্ধানকাৰীৰ নক্ষত্ৰ বুলি গণ্য কৰে, যাৰ বাবে গৱেষণা, লেখা, শিক্ষকতা, বাণিজ্য আৰু কৌতূহলক পুৰস্কৃত কৰা যিকোনো কাম উপযুক্ত। ইয়াৰ আকৰ্ষণ হ'ল পাতল, বন্ধুসুলভ মন; ইয়াৰ শিক্ষা হ'ল যি পোৱা গৈছে তাতে থিতাপি লোৱা, যাতে সন্ধান কৰা অস্থিৰতা নহৈ কোনোবা ঠাইত গৈ উপনীত হয়।",
    # EN: Ardra is ruled by Rudra, the storm form of Shiva, and symbolised by a teardrop or a
    #     diamond. As a storm clears the air and brings rain, people with the Moon here often have a
    #     strong, searching intellect and the ability to see through things to the truth. They can
    #     feel deeply and are not afraid of change. Tradition links Ardra with renewal after
    #     difficulty, so research, technology, writing, counselling and problem-solving suit it
    #     well. Its gift is honesty and a sharp mind; its lesson is to let feelings pass like the
    #     rain, leaving the ground greener.
    "ardra": "আৰ্দ্ৰাৰ অধিপতি ৰুদ্ৰ, শিৱৰ ঝড়ৰ ৰূপ, আৰু প্ৰতীক চকুলো বা হীৰা। ঝড়ে যেনেকৈ বতাহ পৰিষ্কাৰ কৰে আৰু বৰষুণ আনে, তেনেকৈ এই নক্ষত্ৰত চন্দ্ৰ থকা মানুহৰ প্ৰায়ে প্ৰখৰ, অনুসন্ধানী বুদ্ধি আৰু বস্তুৰ ভিতৰলৈ চাই সত্য বুজাৰ ক্ষমতা থাকে। তেওঁলোকে গভীৰভাৱে অনুভৱ কৰে আৰু পৰিৱৰ্তনক ভয় নকৰে। পৰম্পৰাই আৰ্দ্ৰাক কঠিন সময়ৰ পিছৰ নৱীকৰণৰ লগত জড়ায়, সেয়ে গৱেষণা, প্ৰযুক্তি, লেখা, পৰামৰ্শ আৰু সমস্যা সমাধান ইয়াৰ বাবে উপযুক্ত। ইয়াৰ দান হ'ল সততা আৰু তীক্ষ্ণ মন; ইয়াৰ শিক্ষা হ'ল অনুভূতিক বৰষুণৰ দৰে পাৰ হৈ যাবলৈ দিয়া, মাটি অধিক সেউজীয়া কৰি।",
    # EN: Punarvasu is ruled by Aditi, the boundless mother of the gods, and symbolised by a bow and
    #     quiver. Its name means "return of the light", and people with the Moon here are often
    #     optimistic, generous and able to begin again after any setback. They tend to be content
    #     with simple things, good-humoured and caring towards family and guests. Tradition sees
    #     Punarvasu as a nakshatra of renewal and homecoming, suited to teaching, counselling,
    #     writing, travel and caring work. Its blessing is a hopeful, forgiving heart; its lesson is
    #     to aim the arrow — to choose a direction and stay with it.
    "punarvasu": "পুনৰ্বসুৰ অধিপতি অদিতি, দেৱতাসকলৰ অসীম মাতৃ, আৰু প্ৰতীক ধনু আৰু তীৰৰ কোঁহ। ইয়াৰ নামৰ অৰ্থ “পোহৰৰ প্ৰত্যাৱৰ্তন”, আৰু এই নক্ষত্ৰত চন্দ্ৰ থকা মানুহ প্ৰায়ে আশাবাদী, উদাৰ আৰু যিকোনো বাধাৰ পিছত নতুনকৈ আৰম্ভ কৰিব পৰা হয়। তেওঁলোক সৰল বস্তুতে সন্তুষ্ট, হাঁহিমুখীয়া আৰু পৰিয়াল আৰু অতিথিৰ প্ৰতি যত্নশীল। পৰম্পৰাই পুনৰ্বসুক নৱীকৰণ আৰু ঘৰলৈ উভতি অহাৰ নক্ষত্ৰ বুলি গণ্য কৰে, যিটো শিক্ষকতা, পৰামৰ্শ, লেখা, ভ্ৰমণ আৰু যত্নৰ কামৰ বাবে উপযুক্ত। ইয়াৰ আশীৰ্বাদ হ'ল আশাবাদী, ক্ষমাশীল হৃদয়; ইয়াৰ শিক্ষা হ'ল তীৰ লক্ষ্যত মৰা — এটা দিশ বাছি লৈ তাতে লাগি থকা।",
    # EN: Pushya is ruled by Brihaspati, the guru of the gods, and symbolised by a cow's udder or a
    #     lotus — images of nourishment. It is counted among the most auspicious nakshatras, and
    #     people with the Moon here are often caring, dependable, devoted and generous with their
    #     time. They like to support others, keep traditions and build something lasting. Tradition
    #     links Pushya with nourishment and wisdom, so teaching, counselling, food, social service,
    #     finance and spiritual work suit it well. Its gift is a steady, protective kindness; its
    #     lesson is to nourish oneself as faithfully as one nourishes others.
    "pushya": "পুষ্যাৰ অধিপতি বৃহস্পতি, দেৱতাসকলৰ গুৰু, আৰু প্ৰতীক গাইৰ ওঁঠ বা পদুম — পোষণৰ প্ৰতীক। ইয়াক আটাইতকৈ শুভ নক্ষত্ৰৰ ভিতৰত গণ্য কৰা হয়, আৰু এই নক্ষত্ৰত চন্দ্ৰ থকা মানুহ প্ৰায়ে যত্নশীল, নিৰ্ভৰযোগ্য, নিষ্ঠাবান আৰু নিজৰ সময় দিয়াত উদাৰ হয়। তেওঁলোকে আনক সহায় কৰি, পৰম্পৰা ৰক্ষা কৰি আৰু স্থায়ী কিবা গঢ়ি ভাল পায়। পৰম্পৰাই পুষ্যাক পোষণ আৰু প্ৰজ্ঞাৰ লগত জড়ায়, সেয়ে শিক্ষকতা, পৰামৰ্শ, খাদ্য, সমাজসেৱা, বিত্ত আৰু আধ্যাত্মিক কাম ইয়াৰ বাবে উপযুক্ত। ইয়াৰ দান হ'ল স্থিৰ, ৰক্ষাকাৰী দয়া; ইয়াৰ শিক্ষা হ'ল আনক যিমান নিষ্ঠাৰে পোষণ কৰে নিজকো সিমানে পোষণ কৰা।",
    # EN: Ashlesha is ruled by the Nagas, the serpent deities, and symbolised by a coiled serpent —
    #     an image of kundalini, hidden energy and deep wisdom. People with the Moon here are often
    #     perceptive, intelligent and good at understanding what others leave unsaid. They can be
    #     persuasive and strategic, with a strong instinct for self-protection. Tradition links
    #     Ashlesha with insight and with the healing knowledge of herbs, so psychology, research,
    #     medicine, writing and negotiation suit it well. Its gift is penetrating understanding; its
    #     lesson is to use that insight to embrace and heal, the way the serpent's coil protects.
    "ashlesha": "অশ্লেষাৰ অধিপতি নাগ, সৰ্প দেৱতা, আৰু প্ৰতীক কুণ্ডলী পকোৱা সাপ — কুণ্ডলিনী, লুকাই থকা শক্তি আৰু গভীৰ প্ৰজ্ঞাৰ প্ৰতিচ্ছবি। এই নক্ষত্ৰত চন্দ্ৰ থকা মানুহ প্ৰায়ে সূক্ষ্মদৰ্শী, বুদ্ধিমান আৰু আনে নোকোৱা কথা বুজি পোৱাত দক্ষ হয়। তেওঁলোক প্ৰভাৱশালী আৰু কৌশলী হ'ব পাৰে, আত্মৰক্ষাৰ প্ৰবল সহজাত প্ৰবৃত্তিৰে। পৰম্পৰাই অশ্লেষাক অন্তৰ্দৃষ্টি আৰু ঔষধি গছ-গছনিৰ আৰোগ্যজ্ঞানৰ লগত জড়ায়, সেয়ে মনোবিজ্ঞান, গৱেষণা, চিকিৎসা, লেখা আৰু আলোচনা ইয়াৰ বাবে উপযুক্ত। ইয়াৰ দান হ'ল ভেদক বুজাশক্তি; ইয়াৰ শিক্ষা হ'ল সেই অন্তৰ্দৃষ্টিক সাবটি লোৱা আৰু সুস্থ কৰাত ব্যৱহাৰ কৰা, যেনেকৈ সাপৰ কুণ্ডলীয়ে ৰক্ষা কৰে।",
    # EN: Magha is ruled by the Pitris, the ancestors, and symbolised by a royal throne. People with
    #     the Moon here often carry a natural dignity, a respect for family and tradition, and a
    #     wish to live up to the name they were given. They can be generous leaders who take
    #     responsibility for their people. Tradition links Magha with lineage, honour and authority,
    #     so leadership, administration, history, law and work that preserves heritage suit it well.
    #     Its gift is nobility of heart; its lesson is to wear the crown lightly — to lead through
    #     service and to honour the ancestors through good deeds.
    "magha": "মঘাৰ অধিপতি পিতৃ, পূৰ্বপুৰুষ, আৰু প্ৰতীক ৰাজসিংহাসন। এই নক্ষত্ৰত চন্দ্ৰ থকা মানুহৰ প্ৰায়ে স্বাভাৱিক মৰ্যাদা, পৰিয়াল আৰু পৰম্পৰাৰ প্ৰতি শ্ৰদ্ধা, আৰু পোৱা নামৰ যোগ্য হৈ জীয়াই থকাৰ ইচ্ছা থাকে। তেওঁলোক নিজৰ মানুহৰ দায়িত্ব লোৱা উদাৰ নেতা হ'ব পাৰে। পৰম্পৰাই মঘাক বংশ, সন্মান আৰু কৰ্তৃত্বৰ লগত জড়ায়, সেয়ে নেতৃত্ব, প্ৰশাসন, ইতিহাস, আইন আৰু ঐতিহ্য ৰক্ষা কৰা কাম ইয়াৰ বাবে উপযুক্ত। ইয়াৰ দান হ'ল হৃদয়ৰ মহানুভৱতা; ইয়াৰ শিক্ষা হ'ল মুকুট পাতলকৈ পিন্ধা — সেৱাৰ দ্বাৰা নেতৃত্ব দিয়া আৰু ভাল কামেৰে পূৰ্বপুৰুষক সন্মান জনোৱা।",
    # EN: Purva Phalguni is ruled by Bhaga, the god of fortune and marital happiness, and symbolised
    #     by the front legs of a bed — an image of rest and enjoyment. People with the Moon here are
    #     often warm, charming, creative and fond of celebration, music and good company. They bring
    #     people together and know how to relax and enjoy what they have earned. Tradition links
    #     Purva Phalguni with love, the arts and leisure, so entertainment, design, hospitality and
    #     relationship-centred work suit it well. Its gift is joy that is easily shared; its lesson
    #     is balance between pleasure and duty.
    "purva-phalguni": "পূৰ্ব ফল্গুনীৰ অধিপতি ভগ, ভাগ্য আৰু বৈবাহিক সুখৰ দেৱতা, আৰু প্ৰতীক খাটৰ আগফালৰ ভৰি — বিশ্ৰাম আৰু উপভোগৰ প্ৰতিচ্ছবি। এই নক্ষত্ৰত চন্দ্ৰ থকা মানুহ প্ৰায়ে উষ্ণ, আকৰ্ষণীয়, সৃজনশীল আৰু উৎসৱ, সংগীত আৰু ভাল সঙ্গপ্ৰিয় হয়। তেওঁলোকে মানুহক একেলগ কৰে আৰু নিজে উপাৰ্জন কৰাখিনি কেনেকৈ জিৰণি লৈ উপভোগ কৰিব লাগে জানে। পৰম্পৰাই পূৰ্ব ফল্গুনীক প্ৰেম, কলা আৰু অৱসৰৰ লগত জড়ায়, সেয়ে বিনোদন, ডিজাইন, আতিথ্য আৰু সম্পৰ্ককেন্দ্ৰিক কাম ইয়াৰ বাবে উপযুক্ত। ইয়াৰ দান হ'ল সহজে ভগাব পৰা আনন্দ; ইয়াৰ শিক্ষা হ'ল আমোদ আৰু কৰ্তব্যৰ মাজত সমতা।",
    # EN: Uttara Phalguni is ruled by Aryaman, the god of friendship, contracts and marriage vows,
    #     and symbolised by the back legs of a bed. Where its twin Purva Phalguni enjoys, Uttara
    #     Phalguni commits. People with the Moon here are often reliable, helpful, fair-minded and
    #     loyal to friends and partners. They keep their word and like to be of real use to others.
    #     Tradition links this nakshatra with patronage and lasting partnerships, so management,
    #     public service, counselling, law and charitable work suit it well. Its gift is dependable
    #     kindness; its lesson is to accept help as gracefully as it is given.
    "uttara-phalguni": "উত্তৰ ফল্গুনীৰ অধিপতি অৰ্যমা, বন্ধুত্ব, চুক্তি আৰু বিবাহৰ শপতৰ দেৱতা, আৰু প্ৰতীক খাটৰ পিছফালৰ ভৰি। ইয়াৰ যমজ পূৰ্ব ফল্গুনীয়ে যিমান উপভোগ কৰে, উত্তৰ ফল্গুনীয়ে সিমান প্ৰতিশ্ৰুতি ৰক্ষা কৰে। এই নক্ষত্ৰত চন্দ্ৰ থকা মানুহ প্ৰায়ে নিৰ্ভৰযোগ্য, সহায়ক, ন্যায়পৰায়ণ আৰু বন্ধু আৰু সঙ্গীৰ প্ৰতি বিশ্বস্ত হয়। তেওঁলোকে কথা ৰাখে আৰু আনৰ প্ৰকৃত কামত অহা ভাল পায়। পৰম্পৰাই এই নক্ষত্ৰক পৃষ্ঠপোষকতা আৰু স্থায়ী অংশীদাৰীৰ লগত জড়ায়, সেয়ে পৰিচালনা, জনসেৱা, পৰামৰ্শ, আইন আৰু দাতব্য কাম ইয়াৰ বাবে উপযুক্ত। ইয়াৰ দান হ'ল ভৰসাযোগ্য দয়া; ইয়াৰ শিক্ষা হ'ল সহায় দিয়াৰ দৰে সহায় গ্ৰহণো সুন্দৰভাৱে কৰা।",
    # EN: Hasta is ruled by Savitr, the radiant Sun, and symbolised by a hand. People with the Moon
    #     here are often skilful, practical, witty and clever with their hands as well as their
    #     minds. They like to get things done and can turn an idea into something real. Tradition
    #     links Hasta with craftsmanship, healing touch and resourcefulness, so crafts, the arts,
    #     surgery, massage, writing, trade and any skilled trade suit it well. Its gift is the
    #     ability to make and to mend; its lesson is to hold things with an open hand, trusting that
    #     effort brings its own rewards.
    "hasta": "হস্তাৰ অধিপতি সবিতৃ, দীপ্তিমান সূৰ্য, আৰু প্ৰতীক হাত। এই নক্ষত্ৰত চন্দ্ৰ থকা মানুহ প্ৰায়ে দক্ষ, ব্যৱহাৰিক, ৰসিক আৰু মনৰ লগতে হাতৰ কামতো চতুৰ হয়। তেওঁলোকে কাম সম্পন্ন কৰি ভাল পায় আৰু ধাৰণাক বাস্তৱ ৰূপ দিব পাৰে। পৰম্পৰাই হস্তাক হস্তশিল্প, আৰোগ্যকাৰী স্পৰ্শ আৰু উপায়কুশলতাৰ লগত জড়ায়, সেয়ে হস্তশিল্প, কলা, শল্যচিকিৎসা, মালিছ, লেখা, বাণিজ্য আৰু যিকোনো দক্ষতাৰ কাম ইয়াৰ বাবে উপযুক্ত। ইয়াৰ দান হ'ল গঢ়িব আৰু মেৰামতি কৰিব পৰা ক্ষমতা; ইয়াৰ শিক্ষা হ'ল বস্তুক মুকলি হাতেৰে ধৰা, বিশ্বাস ৰখা যে চেষ্টাই নিজৰ পুৰস্কাৰ আনে।",
    # EN: Chitra is ruled by Tvashtr, also known as Vishwakarma, the divine architect, and
    #     symbolised by a bright jewel. Its name means "brilliant" or "picture", and people with the
    #     Moon here often have a strong sense of beauty, design and form. They enjoy creating things
    #     that are both useful and attractive, and they notice detail. Tradition links Chitra with
    #     architecture, the arts and craftsmanship, so design, engineering, fashion, jewellery,
    #     photography and planning suit it well. Its gift is the eye of an artist and the hand of a
    #     builder; its lesson is to value inner beauty as much as outer polish.
    "chitra": "চিত্ৰাৰ অধিপতি ত্বষ্টা, বিশ্বকৰ্মা নামেও পৰিচিত, দিব্য স্থপতি, আৰু প্ৰতীক উজ্জ্বল ৰত্ন। ইয়াৰ নামৰ অৰ্থ “দীপ্তিমান” বা “ছবি”, আৰু এই নক্ষত্ৰত চন্দ্ৰ থকা মানুহৰ প্ৰায়ে সৌন্দৰ্য, নক্সা আৰু আকৃতিৰ প্ৰবল বোধ থাকে। তেওঁলোকে একে সময়তে উপযোগী আৰু আকৰ্ষণীয় বস্তু সৃষ্টি কৰি ভাল পায়, আৰু বিতং কথা লক্ষ্য কৰে। পৰম্পৰাই চিত্ৰাক স্থাপত্য, কলা আৰু হস্তশিল্পৰ লগত জড়ায়, সেয়ে ডিজাইন, ইঞ্জিনিয়াৰিং, ফেশ্বন, অলংকাৰ, ফটোগ্ৰাফী আৰু পৰিকল্পনা ইয়াৰ বাবে উপযুক্ত। ইয়াৰ দান হ'ল শিল্পীৰ চকু আৰু নিৰ্মাতাৰ হাত; ইয়াৰ শিক্ষা হ'ল বাহ্যিক চমকৰ দৰে অন্তৰৰ সৌন্দৰ্যকো মূল্য দিয়া।",
    # EN: Swati is ruled by Vayu, the wind, and symbolised by a young shoot swaying in the breeze —
    #     flexible, independent and able to bend without breaking. People with the Moon here often
    #     value freedom, fairness and their own way of doing things. They are usually diplomatic,
    #     courteous and good at business and negotiation. Tradition links Swati with trade, travel
    #     and self-reliance, so commerce, law, diplomacy, communication and independent work suit it
    #     well. Its gift is adaptability and a gentle, balanced manner; its lesson is to put down
    #     roots, so that the young shoot can grow into a strong tree.
    "swati": "স্বাতীৰ অধিপতি বায়ু, বতাহ, আৰু প্ৰতীক বতাহত দুলি থকা কুঁহিপাত — নমনীয়, স্বাধীন আৰু নভঙাকৈ নুঁৱাব পৰা। এই নক্ষত্ৰত চন্দ্ৰ থকা মানুহে প্ৰায়ে স্বাধীনতা, ন্যায় আৰু নিজৰ ধৰণে কাম কৰা মূল্য দিয়ে। তেওঁলোক সাধাৰণতে কূটনৈতিক, ভদ্ৰ আৰু ব্যৱসায় আৰু আলোচনাত দক্ষ। পৰম্পৰাই স্বাতীক বাণিজ্য, ভ্ৰমণ আৰু আত্মনিৰ্ভৰতাৰ লগত জড়ায়, সেয়ে বাণিজ্য, আইন, কূটনীতি, যোগাযোগ আৰু স্বাধীন কাম ইয়াৰ বাবে উপযুক্ত। ইয়াৰ দান হ'ল খাপ খুৱাব পৰা ক্ষমতা আৰু কোমল, সুষম আচৰণ; ইয়াৰ শিক্ষা হ'ল শিপা পুতা, যাতে কুঁহিপাতটো শক্তিশালী গছ হ'ব পাৰে।",
    # EN: Vishakha is ruled by Indra and Agni together, and symbolised by a triumphal arch decorated
    #     with leaves. People with the Moon here are often purposeful, ambitious and determined to
    #     reach the goal they have set. They have energy, conviction and the patience to keep going
    #     over a long road. Tradition calls Vishakha the nakshatra of purpose, so leadership,
    #     research, politics, sales, teaching and any long-term mission suit it well. Its gift is
    #     focus and the ability to inspire others towards a shared aim; its lesson is to enjoy the
    #     journey, not only the arch at its end.
    "vishakha": "বিশাখাৰ অধিপতি ইন্দ্ৰ আৰু অগ্নি একেলগে, আৰু প্ৰতীক পাতেৰে সজোৱা বিজয় তোৰণ। এই নক্ষত্ৰত চন্দ্ৰ থকা মানুহ প্ৰায়ে লক্ষ্যনিষ্ঠ, উচ্চাকাংক্ষী আৰু নিৰ্ধাৰিত লক্ষ্যত পাবলৈ দৃঢ়সংকল্প হয়। তেওঁলোকৰ শক্তি, প্ৰত্যয় আৰু দীঘলীয়া বাটত আগবাঢ়ি যাবলৈ ধৈৰ্য থাকে। পৰম্পৰাই বিশাখাক উদ্দেশ্যৰ নক্ষত্ৰ বোলে, সেয়ে নেতৃত্ব, গৱেষণা, ৰাজনীতি, বিক্ৰী, শিক্ষকতা আৰু যিকোনো দীঘলীয়া অভিযান ইয়াৰ বাবে উপযুক্ত। ইয়াৰ দান হ'ল মনোযোগ আৰু আনক সাধাৰণ লক্ষ্যৰ ফালে অনুপ্ৰাণিত কৰিব পৰা ক্ষমতা; ইয়াৰ শিক্ষা হ'ল যাত্ৰাটো উপভোগ কৰা, কেৱল শেষৰ তোৰণটো নহয়।",
    # EN: Anuradha is ruled by Mitra, the god of friendship and cooperation, and symbolised by a
    #     lotus that blooms out of muddy water. People with the Moon here are often loyal friends,
    #     devoted to their ideals and able to keep going with quiet faith in difficult places. They
    #     are good at bringing people together in groups and organisations. Tradition links Anuradha
    #     with friendship, devotion and success away from home, so teamwork, organisation,
    #     counselling, travel and spiritual practice suit it well. Its gift is the ability to
    #     blossom anywhere; its lesson is to be as gentle with oneself as with friends.
    "anuradha": "অনুৰাধাৰ অধিপতি মিত্ৰ, বন্ধুত্ব আৰু সহযোগিতাৰ দেৱতা, আৰু প্ৰতীক ঘোলা পানীত ফুলা পদুম। এই নক্ষত্ৰত চন্দ্ৰ থকা মানুহ প্ৰায়ে বিশ্বস্ত বন্ধু, নিজৰ আদৰ্শৰ প্ৰতি নিষ্ঠাবান আৰু কঠিন ঠাইতো নীৰৱ বিশ্বাসেৰে আগবাঢ়ি যাব পৰা হয়। তেওঁলোক গোট আৰু সংগঠনত মানুহক লগ লগাত দক্ষ। পৰম্পৰাই অনুৰাধাক বন্ধুত্ব, ভক্তি আৰু ঘৰৰ বাহিৰত সফলতাৰ লগত জড়ায়, সেয়ে দলীয় কাম, সংগঠন, পৰামৰ্শ, ভ্ৰমণ আৰু আধ্যাত্মিক সাধনা ইয়াৰ বাবে উপযুক্ত। ইয়াৰ দান হ'ল য'তে নহওক ফুলি উঠিব পৰা ক্ষমতা; ইয়াৰ শিক্ষা হ'ল বন্ধুৰ প্ৰতি যিমান কোমল, নিজৰ প্ৰতিও সিমানেই কোমল হোৱা।",
    # EN: Jyeshtha is ruled by Indra, king of the gods, and symbolised by a circular amulet or
    #     earring. Its name means "the eldest", and people with the Moon here often take on
    #     responsibility early, protect those around them and carry a quiet authority. They are
    #     resourceful, perceptive and capable under pressure. Tradition links Jyeshtha with
    #     seniority and protection, so leadership, management, administration, security and any role
    #     that looks after others suit it well. Its gift is courage and capability; its lesson is to
    #     lead with humility and to let others share the load rather than carrying everything alone.
    "jyeshtha": "জ্যেষ্ঠাৰ অধিপতি ইন্দ্ৰ, দেৱতাসকলৰ ৰজা, আৰু প্ৰতীক গোলাকাৰ তাবিজ বা কাণফুলি। ইয়াৰ নামৰ অৰ্থ “সবাতোকৈ বয়োজ্যেষ্ঠ”, আৰু এই নক্ষত্ৰত চন্দ্ৰ থকা মানুহ প্ৰায়ে সৰুতে দায়িত্ব লয়, চাৰিওফালৰ মানুহক ৰক্ষা কৰে আৰু নীৰৱ কৰ্তৃত্ব বহন কৰে। তেওঁলোক উপায়কুশল, সূক্ষ্মদৰ্শী আৰু চাপৰ মাজতো সক্ষম। পৰম্পৰাই জ্যেষ্ঠাক জ্যেষ্ঠতা আৰু সুৰক্ষাৰ লগত জড়ায়, সেয়ে নেতৃত্ব, পৰিচালনা, প্ৰশাসন, নিৰাপত্তা আৰু আনৰ যত্ন লোৱা যিকোনো ভূমিকা ইয়াৰ বাবে উপযুক্ত। ইয়াৰ দান হ'ল সাহস আৰু সক্ষমতা; ইয়াৰ শিক্ষা হ'ল বিনয়ৰে নেতৃত্ব দিয়া আৰু সকলো একেলগে নবহি আনকো বোজা ভগাই দিয়া।",
    # EN: Mula is ruled by Nirriti and symbolised by a bunch of roots. Its name means "the root",
    #     and people with the Moon here are often drawn to get to the bottom of things — to find the
    #     origin of a question, an idea or a tradition. They can be independent, philosophical and
    #     unafraid to start again from first principles. Tradition links Mula with investigation and
    #     with letting go of what is no longer needed, so research, medicine, philosophy, botany and
    #     spiritual inquiry suit it well. Its gift is depth; its lesson is that clearing old ground
    #     makes room for new growth.
    "mula": "মূলাৰ অধিপতি নিঋতি আৰু প্ৰতীক শিপাৰ থোপা। ইয়াৰ নামৰ অৰ্থ “শিপা”, আৰু এই নক্ষত্ৰত চন্দ্ৰ থকা মানুহ প্ৰায়ে বস্তুৰ গভীৰলৈ যাবলৈ আকৰ্ষিত হয় — কোনো প্ৰশ্ন, ধাৰণা বা পৰম্পৰাৰ উৎস বিচাৰি উলিয়াবলৈ। তেওঁলোক স্বাধীন, দাৰ্শনিক আৰু মূল নীতিৰ পৰা নতুনকৈ আৰম্ভ কৰিবলৈ নিৰ্ভয় হ'ব পাৰে। পৰম্পৰাই মূলাক অনুসন্ধান আৰু যিটো আৰু লাগিবলগীয়া নহয় তাক এৰি দিয়াৰ লগত জড়ায়, সেয়ে গৱেষণা, চিকিৎসা, দৰ্শন, উদ্ভিদবিজ্ঞান আৰু আধ্যাত্মিক অনুসন্ধান ইয়াৰ বাবে উপযুক্ত। ইয়াৰ দান হ'ল গভীৰতা; ইয়াৰ শিক্ষা হ'ল পুৰণি মাটি সাৰি দিলে নতুন বৃদ্ধিৰ ঠাই হয়।",
    # EN: Purva Ashadha is ruled by Apas, the cosmic waters, and symbolised by a winnowing fan or an
    #     elephant tusk. Its name means "the early invincible", and people with the Moon here are
    #     often confident, persuasive and full of conviction. Like water, they can be gentle and yet
    #     wear down any obstacle in time. Tradition links Purva Ashadha with purification and with
    #     victory won through persistence, so teaching, law, debate, the arts, shipping and anything
    #     to do with water suit it well. Its gift is optimism and inner strength; its lesson is to
    #     stay open to other views while holding firm to its own.
    "purva-ashadha": "পূৰ্বাষাঢ়াৰ অধিপতি অপ, মহাজাগতিক জল, আৰু প্ৰতীক কুলা বা হাতীদাঁত। ইয়াৰ নামৰ অৰ্থ “আগৰ অপৰাজিত”, আৰু এই নক্ষত্ৰত চন্দ্ৰ থকা মানুহ প্ৰায়ে আত্মবিশ্বাসী, প্ৰভাৱশালী আৰু প্ৰত্যয়েৰে ভৰা হয়। পানীৰ দৰে তেওঁলোক কোমল হ'লেও সময়ত যিকোনো বাধা ক্ষয় কৰিব পাৰে। পৰম্পৰাই পূৰ্বাষাঢ়াক শুদ্ধি আৰু অধ্যৱসায়েৰে লাভ কৰা বিজয়ৰ লগত জড়ায়, সেয়ে শিক্ষকতা, আইন, বিতৰ্ক, কলা, জাহাজ আৰু পানীৰ লগত জড়িত যিকোনো কাম ইয়াৰ বাবে উপযুক্ত। ইয়াৰ দান হ'ল আশাবাদ আৰু অন্তৰৰ শক্তি; ইয়াৰ শিক্ষা হ'ল নিজৰ মতত অটল থাকিও আনৰ মতৰ প্ৰতি মুকলি হৈ থকা।",
    # EN: Uttara Ashadha is ruled by the Vishvedevas, the universal gods, and symbolised by an
    #     elephant tusk. Its name means "the later invincible" — the victory that lasts because it
    #     was earned honestly. People with the Moon here are often principled, patient, responsible
    #     and respected for their integrity. They take the long view and finish what they commit to.
    #     Tradition links Uttara Ashadha with righteous leadership, so government, management, law,
    #     teaching and social causes suit it well. Its gift is steady, ethical strength; its lesson
    #     is to keep a little lightness and warmth alongside the seriousness of duty.
    "uttara-ashadha": "উত্তৰাষাঢ়াৰ অধিপতি বিশ্বদেৱ, সাৰ্বজনীন দেৱতা, আৰু প্ৰতীক হাতীদাঁত। ইয়াৰ নামৰ অৰ্থ “পিছৰ অপৰাজিত” — সততাৰে অৰ্জিত বাবে স্থায়ী হোৱা বিজয়। এই নক্ষত্ৰত চন্দ্ৰ থকা মানুহ প্ৰায়ে নীতিবান, ধৈৰ্যশীল, দায়িত্বশীল আৰু সততাৰ বাবে সন্মানিত হয়। তেওঁলোকে দীঘলীয়া দৃষ্টিৰে চায় আৰু প্ৰতিশ্ৰুতি দিয়া কাম শেষ কৰে। পৰম্পৰাই উত্তৰাষাঢ়াক ধাৰ্মিক নেতৃত্বৰ লগত জড়ায়, সেয়ে চৰকাৰ, পৰিচালনা, আইন, শিক্ষকতা আৰু সামাজিক কাম ইয়াৰ বাবে উপযুক্ত। ইয়াৰ দান হ'ল স্থিৰ, নৈতিক শক্তি; ইয়াৰ শিক্ষা হ'ল কৰ্তব্যৰ গাম্ভীৰ্যৰ লগতে অলপ পাতলতা আৰু উষ্ণতা ৰখা।",
    # EN: Shravana is ruled by Vishnu, the preserver, and symbolised by an ear or three footprints.
    #     Its name means "hearing", and people with the Moon here are often good listeners, eager
    #     learners and keepers of knowledge and tradition. They learn by listening and pass on what
    #     they have learned. Tradition links Shravana with wisdom gained through study and with
    #     connecting people, so teaching, counselling, media, languages, music and travel suit it
    #     well. Its gift is attentive understanding and a wish to be useful; its lesson is to listen
    #     to one's own inner voice as carefully as to others.
    "shravana": "শ্ৰৱণাৰ অধিপতি বিষ্ণু, পালনকৰ্তা, আৰু প্ৰতীক কাণ বা তিনিটা ভৰিৰ চিন। ইয়াৰ নামৰ অৰ্থ “শুনা”, আৰু এই নক্ষত্ৰত চন্দ্ৰ থকা মানুহ প্ৰায়ে ভাল শ্ৰোতা, আগ্ৰহী শিকাৰু আৰু জ্ঞান আৰু পৰম্পৰাৰ ৰক্ষক হয়। তেওঁলোকে শুনি শিকে আৰু শিকাখিনি আনক দিয়ে। পৰম্পৰাই শ্ৰৱণাক অধ্যয়নেৰে লাভ কৰা প্ৰজ্ঞা আৰু মানুহক সংযোগ কৰাৰ লগত জড়ায়, সেয়ে শিক্ষকতা, পৰামৰ্শ, সংবাদমাধ্যম, ভাষা, সংগীত আৰু ভ্ৰমণ ইয়াৰ বাবে উপযুক্ত। ইয়াৰ দান হ'ল মনোযোগী বুজাশক্তি আৰু উপযোগী হোৱাৰ ইচ্ছা; ইয়াৰ শিক্ষা হ'ল আনৰ কথাৰ দৰে নিজৰ অন্তৰৰ মাতো মন দি শুনা।",
    # EN: Dhanishta is ruled by the eight Vasus, gods of abundance, and symbolised by a drum. Its
    #     name means "the wealthiest", and people with the Moon here often have rhythm, energy and a
    #     talent for music, dance or teamwork. They are generous, sociable and able to keep a group
    #     moving together. Tradition links Dhanishta with prosperity and with sound, so music,
    #     performance, sport, property, finance and community work suit it well. Its gift is the
    #     ability to set the beat that others follow; its lesson is to listen as well as play,
    #     leaving space for others' rhythms.
    "dhanishta": "ধনিষ্ঠাৰ অধিপতি আঠজন বসু, প্ৰাচুৰ্যৰ দেৱতা, আৰু প্ৰতীক ঢোল। ইয়াৰ নামৰ অৰ্থ “সবাতোকৈ ধনী”, আৰু এই নক্ষত্ৰত চন্দ্ৰ থকা মানুহৰ প্ৰায়ে তাল, শক্তি আৰু সংগীত, নৃত্য বা দলীয় কামৰ প্ৰতিভা থাকে। তেওঁলোক উদাৰ, মিলনসাৰ আৰু গোটক একেলগে আগবঢ়াই নিব পৰা। পৰম্পৰাই ধনিষ্ঠাক সমৃদ্ধি আৰু ধ্বনিৰ লগত জড়ায়, সেয়ে সংগীত, প্ৰদৰ্শন, খেল, সম্পত্তি, বিত্ত আৰু সামাজিক কাম ইয়াৰ বাবে উপযুক্ত। ইয়াৰ দান হ'ল আনে অনুসৰণ কৰা তাল ধৰিব পৰা ক্ষমতা; ইয়াৰ শিক্ষা হ'ল বজোৱাৰ লগতে শুনা, আনৰ তালৰ বাবে ঠাই এৰি দিয়া।",
    # EN: Shatabhisha is ruled by Varuna, lord of the cosmic waters and of truth, and symbolised by
    #     an empty circle. Its name means "a hundred healers", and people with the Moon here are
    #     often independent thinkers, private, truthful and drawn to understanding how things really
    #     work. They can see patterns others miss. Tradition links Shatabhisha with healing and with
    #     the search for hidden truth, so medicine, research, science, technology, astronomy and
    #     alternative healing suit it well. Its gift is clear, original insight; its lesson is to
    #     let others into the circle, sharing what is understood with warmth.
    "shatabhisha": "শতভিষাৰ অধিপতি বৰুণ, মহাজাগতিক জল আৰু সত্যৰ অধিপতি, আৰু প্ৰতীক খালী বৃত্ত। ইয়াৰ নামৰ অৰ্থ “এশ চিকিৎসক”, আৰু এই নক্ষত্ৰত চন্দ্ৰ থকা মানুহ প্ৰায়ে স্বাধীন চিন্তাবিদ, একান্তপ্ৰিয়, সত্যবাদী আৰু বস্তুবোৰ প্ৰকৃততে কেনেকৈ চলে বুজিবলৈ আকৰ্ষিত হয়। আনে এৰি যোৱা ধৰণ তেওঁলোকে দেখা পায়। পৰম্পৰাই শতভিষাক আৰোগ্য আৰু লুকাই থকা সত্যৰ সন্ধানৰ লগত জড়ায়, সেয়ে চিকিৎসা, গৱেষণা, বিজ্ঞান, প্ৰযুক্তি, জ্যোতিৰ্বিজ্ঞান আৰু বিকল্প চিকিৎসা ইয়াৰ বাবে উপযুক্ত। ইয়াৰ দান হ'ল স্পষ্ট, মৌলিক অন্তৰ্দৃষ্টি; ইয়াৰ শিক্ষা হ'ল আনক বৃত্তৰ ভিতৰলৈ আদৰি যি বুজা হৈছে তাক উষ্ণতাৰে ভগাই লোৱা।",
    # EN: Purva Bhadrapada is ruled by Aja Ekapada, the one-footed form of Shiva, and symbolised by
    #     swords or the front legs of a cot. People with the Moon here are often idealistic, intense
    #     and willing to give themselves fully to a cause they believe in. They can be eloquent,
    #     generous and deeply spiritual. Tradition links Purva Bhadrapada with transformation and
    #     with the fire of tapas — sincere effort for a higher aim — so social reform, philosophy,
    #     writing, research and spiritual life suit it well. Its gift is passionate commitment; its
    #     lesson is to temper intensity with patience and calm.
    "purva-bhadrapada": "পূৰ্ব ভাদ্ৰপদৰ অধিপতি অজ একপাদ, শিৱৰ এক ভৰিৰ ৰূপ, আৰু প্ৰতীক তৰোৱাল বা খাটিয়াৰ আগফালৰ ভৰি। এই নক্ষত্ৰত চন্দ্ৰ থকা মানুহ প্ৰায়ে আদৰ্শবাদী, তীব্ৰ আৰু বিশ্বাস কৰা কোনো লক্ষ্যৰ বাবে নিজকে সম্পূৰ্ণ সমৰ্পণ কৰিবলৈ ইচ্ছুক হয়। তেওঁলোক বাকপটু, উদাৰ আৰু গভীৰভাৱে আধ্যাত্মিক হ'ব পাৰে। পৰম্পৰাই পূৰ্ব ভাদ্ৰপদক ৰূপান্তৰ আৰু তপস্যাৰ জুইৰ — উচ্চ লক্ষ্যৰ বাবে আন্তৰিক চেষ্টাৰ — লগত জড়ায়, সেয়ে সমাজ সংস্কাৰ, দৰ্শন, লেখা, গৱেষণা আৰু আধ্যাত্মিক জীৱন ইয়াৰ বাবে উপযুক্ত। ইয়াৰ দান হ'ল আৱেগময় প্ৰতিশ্ৰুতি; ইয়াৰ শিক্ষা হ'ল তীব্ৰতাক ধৈৰ্য আৰু শান্তিৰে সংযত কৰা।",
    # EN: Uttara Bhadrapada is ruled by Ahir Budhnya, the serpent of the deep waters, and symbolised
    #     by the back legs of a cot or twins. Where Purva Bhadrapada burns, Uttara Bhadrapada
    #     settles into calm depth. People with the Moon here are often wise, patient, composed and
    #     compassionate, with self-control and a gift for counsel. They tend to think before they
    #     speak and are steady in difficult times. Tradition links this nakshatra with depth,
    #     renunciation and kindness, so counselling, charity, teaching, research and spiritual
    #     practice suit it well. Its gift is serene wisdom; its lesson is to share it actively, not
    #     only privately.
    "uttara-bhadrapada": "উত্তৰ ভাদ্ৰপদৰ অধিপতি অহিৰ্বুধ্ন্য, গভীৰ জলৰ সাপ, আৰু প্ৰতীক খাটিয়াৰ পিছফালৰ ভৰি বা যমজ। পূৰ্ব ভাদ্ৰপদে যিদৰে জ্বলে, উত্তৰ ভাদ্ৰপদে শান্ত গভীৰতাত থিতাপি লয়। এই নক্ষত্ৰত চন্দ্ৰ থকা মানুহ প্ৰায়ে জ্ঞানী, ধৈৰ্যশীল, সংযত আৰু কৰুণাময় হয়, আত্মসংযম আৰু পৰামৰ্শ দিয়াৰ প্ৰতিভাৰে। তেওঁলোকে কোৱাৰ আগতে ভাবে আৰু কঠিন সময়ত স্থিৰ থাকে। পৰম্পৰাই এই নক্ষত্ৰক গভীৰতা, ত্যাগ আৰু দয়াৰ লগত জড়ায়, সেয়ে পৰামৰ্শ, দান, শিক্ষকতা, গৱেষণা আৰু আধ্যাত্মিক সাধনা ইয়াৰ বাবে উপযুক্ত। ইয়াৰ দান হ'ল প্ৰশান্ত প্ৰজ্ঞা; ইয়াৰ শিক্ষা হ'ল ইয়াক কেৱল নিজৰ ভিতৰতে নৰখি সক্ৰিয়ভাৱে ভগাই দিয়া।",
    # EN: Revati, the last nakshatra, is ruled by Pushan, the nourisher who guides travellers and
    #     protects herds on their way, and symbolised by a fish. People with the Moon here are often
    #     gentle, kind, imaginative and protective of the weak, with a love of animals, art and
    #     music. They make good companions on any journey and help others reach their destination
    #     safely. Tradition links Revati with safe journeys, prosperity and completion, so caring
    #     work, the arts, travel, hospitality and spiritual life suit it well. Its gift is
    #     compassion and faith; its lesson is to care for oneself while caring for everyone else.
    "revati": "ৰেৱতী, শেষৰ নক্ষত্ৰ, ইয়াৰ অধিপতি পূষণ — পথিকক পথ দেখুওৱা আৰু পথত গৰু-ম'হ ৰক্ষা কৰা পালনকৰ্তা — আৰু প্ৰতীক মাছ। এই নক্ষত্ৰত চন্দ্ৰ থকা মানুহ প্ৰায়ে কোমল, দয়ালু, কল্পনাশীল আৰু দুৰ্বলক ৰক্ষা কৰা হয়, জীৱ-জন্তু, কলা আৰু সংগীতৰ প্ৰতি ভালপোৱাৰে। তেওঁলোক যিকোনো যাত্ৰাত ভাল সংগী আৰু আনক নিৰাপদে গন্তব্যস্থানত পোৱাত সহায় কৰে। পৰম্পৰাই ৰেৱতীক নিৰাপদ যাত্ৰা, সমৃদ্ধি আৰু পূৰ্ণতাৰ লগত জড়ায়, সেয়ে যত্নৰ কাম, কলা, ভ্ৰমণ, আতিথ্য আৰু আধ্যাত্মিক জীৱন ইয়াৰ বাবে উপযুক্ত। ইয়াৰ দান হ'ল কৰুণা আৰু বিশ্বাস; ইয়াৰ শিক্ষা হ'ল আনৰ যত্ন লওঁতে নিজৰো যত্ন লোৱা।",
}

# app/nakshatra_text.py RASHI_TRAITS["as"] — character paragraph of each of the 12 rashis (key = slug)  [12]
RASHI_TRAITS = {
    # EN: Mesh (Aries) is the first rashi, a movable fire sign ruled by Mars. People with the Moon
    #     in Mesh are often energetic, direct, courageous and quick to act — natural starters who
    #     enjoy a challenge and like to lead from the front. They are honest about their feelings
    #     and recover quickly from setbacks. Their emotional life is warm and spontaneous, and they
    #     bring enthusiasm wherever they go. Work that rewards initiative — sport, the armed forces,
    #     engineering, entrepreneurship, surgery — often suits them. Their growth lies in patience
    #     and in listening before acting, so that their courage is matched by care for others.
    "mesh": "মেষ প্ৰথম ৰাশি, মঙ্গলৰ অধীন এক চৰ অগ্নি ৰাশি। মেষত চন্দ্ৰ থকা মানুহ প্ৰায়ে উদ্যমী, পোনপটীয়া, সাহসী আৰু খৰকৈ কাম কৰা হয় — স্বাভাৱিক আৰম্ভকাৰী যিয়ে প্ৰত্যাহ্বান উপভোগ কৰে আৰু আগভাগৰ পৰা নেতৃত্ব দিয়া ভাল পায়। তেওঁলোক নিজৰ অনুভূতিৰ বিষয়ে সৎ আৰু বাধাৰ পৰা দ্ৰুতকৈ উভতি আহে। তেওঁলোকৰ আৱেগিক জীৱন উষ্ণ আৰু স্বতঃস্ফূৰ্ত, আৰু য'তে যায় উৎসাহ লৈ যায়। উদ্যমক পুৰস্কৃত কৰা কাম — খেল, সেনা, ইঞ্জিনিয়াৰিং, উদ্যোগ, শল্যচিকিৎসা — প্ৰায়ে তেওঁলোকৰ বাবে উপযুক্ত। তেওঁলোকৰ বিকাশ ধৈৰ্য আৰু কাম কৰাৰ আগতে শুনাত নিহিত, যাতে সাহসৰ লগত আনৰ প্ৰতি যত্নও থাকে।",
    # EN: Vrishabh (Taurus) is a fixed earth sign ruled by Venus, and the Moon is exalted here.
    #     People with the Moon in Vrishabh are often calm, patient, loyal and steady, with a love of
    #     comfort, good food, music and beautiful things. They build slowly and surely, and what
    #     they build tends to last. Emotionally they are dependable and affectionate, preferring
    #     security to drama. Finance, agriculture, the arts, food, design and any work that rewards
    #     persistence often suit them. Their growth lies in flexibility — welcoming change when it
    #     comes, and holding possessions and opinions a little more lightly.
    "vrishabh": "বৃষ এক স্থিৰ পৃথিৱী ৰাশি, শুক্ৰৰ অধীন, আৰু ইয়াত চন্দ্ৰ উচ্চ। বৃষত চন্দ্ৰ থকা মানুহ প্ৰায়ে শান্ত, ধৈৰ্যশীল, বিশ্বস্ত আৰু স্থিৰ হয়, আৰাম, ভাল খাদ্য, সংগীত আৰু সুন্দৰ বস্তুৰ প্ৰতি ভালপোৱাৰে। তেওঁলোকে লাহে লাহে কিন্তু নিশ্চিতভাৱে গঢ়ে, আৰু গঢ়াবোৰ স্থায়ী হয়। আৱেগিকভাৱে তেওঁলোক ভৰসাযোগ্য আৰু স্নেহশীল, নাটকতকৈ নিৰাপত্তা বেছি ভাল পায়। বিত্ত, কৃষি, কলা, খাদ্য, ডিজাইন আৰু অধ্যৱসায়ক পুৰস্কৃত কৰা যিকোনো কাম প্ৰায়ে তেওঁলোকৰ বাবে উপযুক্ত। তেওঁলোকৰ বিকাশ নমনীয়তাত নিহিত — পৰিৱৰ্তন আহিলে আদৰি লোৱা, আৰু সম্পত্তি আৰু মতামতক অলপ পাতলকৈ ধৰা।",
    # EN: Mithun (Gemini) is a dual air sign ruled by Mercury. People with the Moon in Mithun are
    #     often curious, witty, talkative and quick to learn, with many interests and a gift for
    #     connecting ideas and people. They enjoy conversation, reading, travel and anything that
    #     keeps the mind busy. Emotionally they need variety and a partner who is also a friend they
    #     can talk to. Writing, teaching, media, sales, technology and trade often suit them. Their
    #     growth lies in depth and focus — choosing a few things and seeing them through — and in
    #     giving their own feelings the attention they give to ideas.
    "mithun": "মিথুন এক দ্বিস্বভাৱ বায়ু ৰাশি, বুধৰ অধীন। মিথুনত চন্দ্ৰ থকা মানুহ প্ৰায়ে কৌতূহলী, ৰসিক, কথা-বতৰাপ্ৰিয় আৰু খৰকৈ শিকা হয়, বহু আগ্ৰহ আৰু ধাৰণা আৰু মানুহক সংযোগ কৰাৰ প্ৰতিভাৰে। তেওঁলোকে কথোপকথন, পঢ়া, ভ্ৰমণ আৰু মনক ব্যস্ত ৰখা যিকোনো কাম উপভোগ কৰে। আৱেগিকভাৱে তেওঁলোকৰ বৈচিত্ৰ্য লাগে আৰু এজন এনে সঙ্গী লাগে যি এজন বন্ধুও, যাৰ লগত কথা পাতিব পাৰি। লেখা, শিক্ষকতা, সংবাদমাধ্যম, বিক্ৰী, প্ৰযুক্তি আৰু বাণিজ্য প্ৰায়ে তেওঁলোকৰ বাবে উপযুক্ত। তেওঁলোকৰ বিকাশ গভীৰতা আৰু মনোযোগত নিহিত — অলপ বস্তু বাছি শেষলৈকে লৈ যোৱা — আৰু ধাৰণাক যিমান মনোযোগ দিয়ে নিজৰ অনুভূতিকো সিমান দিয়া।",
    # EN: Kark (Cancer) is a movable water sign ruled by the Moon itself, so the Moon is at home
    #     here. People with the Moon in Kark are often caring, sensitive, intuitive and devoted to
    #     family and home. They remember kindness, protect those they love and create warmth
    #     wherever they live. Their moods can change like the tides, but their loyalty runs deep.
    #     Nursing, teaching, hospitality, food, real estate, counselling and public service often
    #     suit them. Their growth lies in trusting their own strength, letting go of old hurts and
    #     allowing others to care for them in return.
    "kark": "কৰ্কট এক চৰ জল ৰাশি, চন্দ্ৰৰ নিজৰ অধীন, সেয়ে ইয়াত চন্দ্ৰ নিজৰ ঘৰত। কৰ্কটত চন্দ্ৰ থকা মানুহ প্ৰায়ে যত্নশীল, সংবেদনশীল, সহজাত বুদ্ধিসম্পন্ন আৰু পৰিয়াল আৰু ঘৰৰ প্ৰতি নিষ্ঠাবান হয়। তেওঁলোকে দয়াক মনত ৰাখে, প্ৰিয়জনক ৰক্ষা কৰে আৰু য'তে থাকে তাত উষ্ণতা সৃষ্টি কৰে। তেওঁলোকৰ মনৰ ভাৱ জোৱাৰ-ভাটাৰ দৰে সলনি হ'ব পাৰে, কিন্তু বিশ্বস্ততা গভীৰ। সেৱিকাৰ কাম, শিক্ষকতা, আতিথ্য, খাদ্য, ৰিয়েল এষ্টেট, পৰামৰ্শ আৰু জনসেৱা প্ৰায়ে তেওঁলোকৰ বাবে উপযুক্ত। তেওঁলোকৰ বিকাশ নিজৰ শক্তিত বিশ্বাস কৰা, পুৰণি আঘাত এৰি দিয়া আৰু আনক সলনি তেওঁলোকৰ যত্ন ল'বলৈ দিয়াত নিহিত।",
    # EN: Simha (Leo) is a fixed fire sign ruled by the Sun. People with the Moon in Simha are often
    #     generous, dignified, confident and warm-hearted, with a natural sense of leadership and a
    #     love of recognition. They are loyal to those who trust them and protective of their family
    #     and friends. Emotionally they are proud and open-hearted, and they shine when appreciated.
    #     Leadership, administration, politics, the performing arts, teaching and government service
    #     often suit them. Their growth lies in humility — letting others share the stage, and
    #     finding confidence from within rather than from applause.
    "simha": "সিংহ এক স্থিৰ অগ্নি ৰাশি, সূৰ্যৰ অধীন। সিংহত চন্দ্ৰ থকা মানুহ প্ৰায়ে উদাৰ, মৰ্যাদাশীল, আত্মবিশ্বাসী আৰু উষ্ণহৃদয় হয়, নেতৃত্বৰ স্বাভাৱিক বোধ আৰু স্বীকৃতিৰ প্ৰতি ভালপোৱাৰে। তেওঁলোকে বিশ্বাস কৰা লোকৰ প্ৰতি বিশ্বস্ত আৰু পৰিয়াল-বন্ধুৰ প্ৰতি ৰক্ষাকাৰী। আৱেগিকভাৱে তেওঁলোক গৰ্বিত আৰু মুকলিমনা, আৰু প্ৰশংসা পালে উজ্জ্বল হয়। নেতৃত্ব, প্ৰশাসন, ৰাজনীতি, মঞ্চকলা, শিক্ষকতা আৰু চৰকাৰী সেৱা প্ৰায়ে তেওঁলোকৰ বাবে উপযুক্ত। তেওঁলোকৰ বিকাশ বিনয়ত নিহিত — আনকো মঞ্চ ভগাই দিয়া, আৰু হাত-চাপৰিৰ পৰা নহয়, ভিতৰৰ পৰা আত্মবিশ্বাস বিচৰা।",
    # EN: Kanya (Virgo) is a dual earth sign ruled by Mercury. People with the Moon in Kanya are
    #     often practical, analytical, modest and helpful, with an eye for detail and a wish to make
    #     things work properly. They show care through service — fixing, organising and looking
    #     after the small things others overlook. Emotionally they can be reserved, but they are
    #     deeply dependable. Medicine, accounting, research, editing, nutrition, teaching and any
    #     precise craft often suit them. Their growth lies in self-acceptance: being as kind to
    #     their own imperfections as they are patient with other people's needs.
    "kanya": "কন্যা এক দ্বিস্বভাৱ পৃথিৱী ৰাশি, বুধৰ অধীন। কন্যাত চন্দ্ৰ থকা মানুহ প্ৰায়ে ব্যৱহাৰিক, বিশ্লেষণধৰ্মী, বিনয়ী আৰু সহায়ক হয়, বিতং কথাত চকু আৰু বস্তু ঠিকমতে চলোৱাৰ ইচ্ছাৰে। তেওঁলোকে সেৱাৰ মাজেৰে যত্ন দেখুৱায় — মেৰামতি, সজোৱা আৰু আনে উপেক্ষা কৰা সৰু কথাবোৰৰ যত্ন লোৱা। আৱেগিকভাৱে তেওঁলোক সংযত হ'ব পাৰে, কিন্তু গভীৰভাৱে ভৰসাযোগ্য। চিকিৎসা, হিচাপ, গৱেষণা, সম্পাদনা, পুষ্টিবিজ্ঞান, শিক্ষকতা আৰু যিকোনো নিখুঁত শিল্প প্ৰায়ে তেওঁলোকৰ বাবে উপযুক্ত। তেওঁলোকৰ বিকাশ আত্মস্বীকৃতিত নিহিত: আনৰ প্ৰয়োজনৰ প্ৰতি যিমান ধৈৰ্যশীল, নিজৰ অপূৰ্ণতাৰ প্ৰতিও সিমান দয়ালু হোৱা।",
    # EN: Tula (Libra) is a movable air sign ruled by Venus, symbolised by the scales. People with
    #     the Moon in Tula are often gracious, fair-minded, sociable and diplomatic, with a strong
    #     sense of beauty and justice. They value harmony in relationships and are good at seeing
    #     both sides of a question. Emotionally they need partnership and feel most at ease when
    #     things around them are balanced. Law, diplomacy, design, fashion, the arts, counselling
    #     and business partnerships often suit them. Their growth lies in decisiveness — trusting
    #     their own judgement and accepting that a little disagreement can be healthy.
    "tula": "তুলা এক চৰ বায়ু ৰাশি, শুক্ৰৰ অধীন, তৰ্জুৰ প্ৰতীকেৰে। তুলাত চন্দ্ৰ থকা মানুহ প্ৰায়ে ভদ্ৰ, ন্যায়পৰায়ণ, মিলনসাৰ আৰু কূটনৈতিক হয়, সৌন্দৰ্য আৰু ন্যায়ৰ প্ৰবল বোধৰে। তেওঁলোকে সম্পৰ্কত সম্প্ৰীতিক মূল্য দিয়ে আৰু প্ৰশ্নৰ দুয়ো দিশ চাবলৈ দক্ষ। আৱেগিকভাৱে তেওঁলোকৰ সঙ্গী লাগে আৰু চাৰিওফালে সমতা থাকিলে আটাইতকৈ স্বচ্ছন্দ অনুভৱ কৰে। আইন, কূটনীতি, ডিজাইন, ফেশ্বন, কলা, পৰামৰ্শ আৰু ব্যৱসায়িক অংশীদাৰী প্ৰায়ে তেওঁলোকৰ বাবে উপযুক্ত। তেওঁলোকৰ বিকাশ সিদ্ধান্ত লোৱাত নিহিত — নিজৰ বিচাৰক বিশ্বাস কৰা আৰু অলপ মতভেদ স্বাস্থ্যকৰ হ'ব পাৰে বুলি মানি লোৱা।",
    # EN: Vrishchik (Scorpio) is a fixed water sign ruled by Mars. People with the Moon in Vrishchik
    #     are often intense, perceptive, determined and deeply loyal, with feelings that run far
    #     below the surface. They are not satisfied with appearances and want to understand what is
    #     really going on. Once they commit — to a person, a cause or a goal — they rarely let go.
    #     Research, investigation, medicine, psychology, finance and crisis work often suit them.
    #     Their growth lies in trust and forgiveness: letting others in, and allowing old feelings
    #     to transform rather than be held.
    "vrishchik": "বৃশ্চিক এক স্থিৰ জল ৰাশি, মঙ্গলৰ অধীন। বৃশ্চিকত চন্দ্ৰ থকা মানুহ প্ৰায়ে তীব্ৰ, সূক্ষ্মদৰ্শী, দৃঢ়সংকল্প আৰু গভীৰভাৱে বিশ্বস্ত হয়, পৃষ্ঠৰ বহু তলত চলি থকা অনুভূতিৰে। তেওঁলোক বাহ্যিক ৰূপত সন্তুষ্ট নহয় আৰু প্ৰকৃততে কি চলি আছে বুজিব বিচাৰে। এবাৰ প্ৰতিশ্ৰুতিবদ্ধ হ'লে — কোনো মানুহ, উদ্দেশ্য বা লক্ষ্যৰ প্ৰতি — তেওঁলোকে কমকৈয়ে এৰে। গৱেষণা, তদন্ত, চিকিৎসা, মনোবিজ্ঞান, বিত্ত আৰু সংকটকালীন কাম প্ৰায়ে তেওঁলোকৰ বাবে উপযুক্ত। তেওঁলোকৰ বিকাশ বিশ্বাস আৰু ক্ষমাত নিহিত: আনক ভিতৰলৈ আহিবলৈ দিয়া, আৰু পুৰণি অনুভূতিক ধৰি নাৰাখি ৰূপান্তৰ হ'বলৈ দিয়া।",
    # EN: Dhanu (Sagittarius) is a dual fire sign ruled by Jupiter, symbolised by the archer. People
    #     with the Moon in Dhanu are often optimistic, honest, generous and philosophical, with a
    #     love of learning, travel and freedom. They look for meaning in life and enjoy sharing what
    #     they have learned. Emotionally they are open and cheerful, and they need room to grow.
    #     Teaching, law, religion and philosophy, publishing, travel and sport often suit them.
    #     Their growth lies in following through — giving the same attention to the details of daily
    #     life that they give to big ideas and distant horizons.
    "dhanu": "ধনু এক দ্বিস্বভাৱ অগ্নি ৰাশি, বৃহস্পতিৰ অধীন, ধনুৰ্ধৰৰ প্ৰতীকেৰে। ধনুত চন্দ্ৰ থকা মানুহ প্ৰায়ে আশাবাদী, সৎ, উদাৰ আৰু দাৰ্শনিক হয়, শিক্ষা, ভ্ৰমণ আৰু স্বাধীনতাৰ প্ৰতি ভালপোৱাৰে। তেওঁলোকে জীৱনৰ অৰ্থ বিচাৰে আৰু শিকাখিনি ভগাই ভাল পায়। আৱেগিকভাৱে তেওঁলোক মুকলি আৰু প্ৰফুল্ল, আৰু বিকাশৰ বাবে ঠাই লাগে। শিক্ষকতা, আইন, ধৰ্ম আৰু দৰ্শন, প্ৰকাশন, ভ্ৰমণ আৰু খেল প্ৰায়ে তেওঁলোকৰ বাবে উপযুক্ত। তেওঁলোকৰ বিকাশ শেষলৈকে কৰি যোৱাত নিহিত — ডাঙৰ ধাৰণা আৰু দূৰ দিগন্তক যিমান মনোযোগ দিয়ে দৈনন্দিন জীৱনৰ বিতং কথাতো সিমান দিয়া।",
    # EN: Makar (Capricorn) is a movable earth sign ruled by Saturn. People with the Moon in Makar
    #     are often responsible, disciplined, practical and ambitious in a patient, long-term way.
    #     They take duty seriously, work steadily and earn respect over time. Emotionally they can
    #     seem reserved, but they show love through reliability and quiet support. Administration,
    #     management, engineering, government service, finance and any field that rewards
    #     perseverance often suit them. Their growth lies in warmth and rest — allowing themselves
    #     joy along the way, and remembering that their worth is not measured only by achievement.
    "makar": "মকৰ এক চৰ পৃথিৱী ৰাশি, শনিৰ অধীন। মকৰত চন্দ্ৰ থকা মানুহ প্ৰায়ে দায়িত্বশীল, শৃংখলাবদ্ধ, ব্যৱহাৰিক আৰু ধৈৰ্যশীল, দীঘলীয়া সময়ৰ উচ্চাকাংক্ষী হয়। তেওঁলোকে কৰ্তব্যক গুৰুত্ব দিয়ে, স্থিৰভাৱে কাম কৰে আৰু সময়ৰ লগে লগে সন্মান অৰ্জন কৰে। আৱেগিকভাৱে তেওঁলোক সংযত যেন লাগিব পাৰে, কিন্তু নিৰ্ভৰযোগ্যতা আৰু নীৰৱ সমৰ্থনেৰে প্ৰেম দেখুৱায়। প্ৰশাসন, পৰিচালনা, ইঞ্জিনিয়াৰিং, চৰকাৰী সেৱা, বিত্ত আৰু অধ্যৱসায়ক পুৰস্কৃত কৰা যিকোনো ক্ষেত্ৰ প্ৰায়ে তেওঁলোকৰ বাবে উপযুক্ত। তেওঁলোকৰ বিকাশ উষ্ণতা আৰু জিৰণিত নিহিত — বাটত নিজকে আনন্দ কৰিবলৈ দিয়া, আৰু মনত ৰখা যে তেওঁলোকৰ মূল্য কেৱল সফলতাৰে জোখা নহয়।",
    # EN: Kumbh (Aquarius) is a fixed air sign ruled by Saturn, symbolised by the water-bearer who
    #     pours knowledge out for all. People with the Moon in Kumbh are often independent,
    #     humanitarian, inventive and loyal to friends and ideals. They think about the wider
    #     community and enjoy new ideas, science and reform. Emotionally they value friendship and
    #     freedom, and they show care through principle and action. Science, technology, social
    #     work, research, education and community organisations often suit them. Their growth lies
    #     in closeness — letting their warmth show to individuals as well as to humanity as a whole.
    "kumbh": "কুম্ভ এক স্থিৰ বায়ু ৰাশি, শনিৰ অধীন, সকলোৰে বাবে জ্ঞান ঢালি দিয়া জলবাহকৰ প্ৰতীকেৰে। কুম্ভত চন্দ্ৰ থকা মানুহ প্ৰায়ে স্বাধীন, মানৱহিতৈষী, উদ্ভাৱনী আৰু বন্ধু আৰু আদৰ্শৰ প্ৰতি বিশ্বস্ত হয়। তেওঁলোকে বৃহৎ সমাজৰ কথা ভাবে আৰু নতুন ধাৰণা, বিজ্ঞান আৰু সংস্কাৰ উপভোগ কৰে। আৱেগিকভাৱে তেওঁলোকে বন্ধুত্ব আৰু স্বাধীনতাক মূল্য দিয়ে, আৰু নীতি আৰু কৰ্মৰ দ্বাৰা যত্ন দেখুৱায়। বিজ্ঞান, প্ৰযুক্তি, সমাজকৰ্ম, গৱেষণা, শিক্ষা আৰু সামাজিক সংগঠন প্ৰায়ে তেওঁলোকৰ বাবে উপযুক্ত। তেওঁলোকৰ বিকাশ ঘনিষ্ঠতাত নিহিত — সমগ্ৰ মানৱজাতিৰ লগতে ব্যক্তিগত মানুহৰ প্ৰতিও নিজৰ উষ্ণতা দেখুওৱা।",
    # EN: Meen (Pisces) is a dual water sign ruled by Jupiter, the last of the twelve rashis. People
    #     with the Moon in Meen are often compassionate, imaginative, gentle and spiritually
    #     inclined, with a deep sensitivity to the feelings of others. They forgive easily, help
    #     without being asked and are moved by music, art and devotion. Emotionally they are open-
    #     hearted and intuitive. Healing, counselling, the arts, music, charity, teaching and
    #     spiritual work often suit them. Their growth lies in healthy boundaries — caring for
    #     others without losing themselves, and turning their rich imagination into practical
    #     action.
    "meen": "মীন এক দ্বিস্বভাৱ জল ৰাশি, বৃহস্পতিৰ অধীন, বাৰটা ৰাশিৰ শেষটো। মীনত চন্দ্ৰ থকা মানুহ প্ৰায়ে কৰুণাময়, কল্পনাশীল, কোমল আৰু আধ্যাত্মিক ঝোঁকৰ হয়, আনৰ অনুভূতিৰ প্ৰতি গভীৰ সংবেদনশীলতাৰে। তেওঁলোকে সহজে ক্ষমা কৰে, নোসোধাকৈ সহায় কৰে আৰু সংগীত, কলা আৰু ভক্তিয়ে তেওঁলোকক ছুই যায়। আৱেগিকভাৱে তেওঁলোক মুকলিমনা আৰু সহজাত বুদ্ধিসম্পন্ন। আৰোগ্যদান, পৰামৰ্শ, কলা, সংগীত, দান, শিক্ষকতা আৰু আধ্যাত্মিক কাম প্ৰায়ে তেওঁলোকৰ বাবে উপযুক্ত। তেওঁলোকৰ বিকাশ স্বাস্থ্যকৰ সীমাত নিহিত — নিজকে হেৰুৱাই নপেলাই আনৰ যত্ন লোৱা, আৰু নিজৰ সমৃদ্ধ কল্পনাক ব্যৱহাৰিক কৰ্মলৈ ৰূপান্তৰ কৰা।",
}

# app/nakshatra_text.py FACTS["as"] — deity.<slug> and symbol.<slug> of each nakshatra  [54]
NAKSHATRA_FACTS = {
    # EN: The Ashwini Kumaras, the divine physicians
    "deity.ashwini": "অশ্বিনী কুমাৰ, দেৱতাৰ চিকিৎসক",
    # EN: A horse's head
    "symbol.ashwini": "ঘোঁৰাৰ মূৰ",
    # EN: Yama, lord of dharma
    "deity.bharani": "যম, ধৰ্মৰ অধিপতি",
    # EN: The yoni (womb)
    "symbol.bharani": "যোনি (গৰ্ভ)",
    # EN: Agni, the fire
    "deity.krittika": "অগ্নি",
    # EN: A razor or flame
    "symbol.krittika": "খুৰ বা জুইৰ শিখা",
    # EN: Brahma (Prajapati)
    "deity.rohini": "ব্ৰহ্মা (প্ৰজাপতি)",
    # EN: A chariot or ox-cart
    "symbol.rohini": "ৰথ বা গৰু-গাড়ী",
    # EN: Soma, the Moon
    "deity.mrigashira": "সোম, চন্দ্ৰ",
    # EN: A deer's head
    "symbol.mrigashira": "হৰিণৰ মূৰ",
    # EN: Rudra
    "deity.ardra": "ৰুদ্ৰ",
    # EN: A teardrop or diamond
    "symbol.ardra": "চকুলো বা হীৰা",
    # EN: Aditi, mother of the gods
    "deity.punarvasu": "অদিতি, দেৱতাৰ মাতৃ",
    # EN: A bow and quiver
    "symbol.punarvasu": "ধনু আৰু তীৰৰ কোঁহ",
    # EN: Brihaspati, guru of the gods
    "deity.pushya": "বৃহস্পতি, দেৱতাৰ গুৰু",
    # EN: A cow's udder or lotus
    "symbol.pushya": "গাইৰ ওঁঠ বা পদুম",
    # EN: The Nagas (serpent deities)
    "deity.ashlesha": "নাগ (সৰ্প দেৱতা)",
    # EN: A coiled serpent
    "symbol.ashlesha": "কুণ্ডলী পকোৱা সাপ",
    # EN: The Pitris (ancestors)
    "deity.magha": "পিতৃ (পূৰ্বপুৰুষ)",
    # EN: A royal throne
    "symbol.magha": "ৰাজসিংহাসন",
    # EN: Bhaga, giver of fortune
    "deity.purva-phalguni": "ভগ, ভাগ্যদাতা",
    # EN: The front legs of a bed
    "symbol.purva-phalguni": "খাটৰ আগফালৰ ভৰি",
    # EN: Aryaman, lord of friendship
    "deity.uttara-phalguni": "অৰ্যমা, বন্ধুত্বৰ অধিপতি",
    # EN: The back legs of a bed
    "symbol.uttara-phalguni": "খাটৰ পিছফালৰ ভৰি",
    # EN: Savitr, the Sun
    "deity.hasta": "সবিতৃ, সূৰ্য",
    # EN: A hand
    "symbol.hasta": "হাত",
    # EN: Tvashtr (Vishwakarma), the divine architect
    "deity.chitra": "ত্বষ্টা (বিশ্বকৰ্মা), দিব্য স্থপতি",
    # EN: A bright jewel
    "symbol.chitra": "উজ্জ্বল ৰত্ন",
    # EN: Vayu, the wind
    "deity.swati": "বায়ু, বতাহ",
    # EN: A young shoot swaying in the wind
    "symbol.swati": "বতাহত দুলি থকা কুঁহিপাত",
    # EN: Indra and Agni (Indragni)
    "deity.vishakha": "ইন্দ্ৰ আৰু অগ্নি (ইন্দ্ৰাগ্নি)",
    # EN: A triumphal arch
    "symbol.vishakha": "বিজয় তোৰণ",
    # EN: Mitra, lord of friendship
    "deity.anuradha": "মিত্ৰ, বন্ধুত্বৰ অধিপতি",
    # EN: A lotus
    "symbol.anuradha": "পদুম",
    # EN: Indra, king of the gods
    "deity.jyeshtha": "ইন্দ্ৰ, দেৱতাসকলৰ ৰজা",
    # EN: A circular amulet or earring
    "symbol.jyeshtha": "গোলাকাৰ তাবিজ বা কাণফুলি",
    # EN: Nirriti
    "deity.mula": "নিঋতি",
    # EN: A bunch of roots
    "symbol.mula": "শিপাৰ থোপা",
    # EN: Apas, the waters
    "deity.purva-ashadha": "অপ, জল",
    # EN: A winnowing fan or elephant tusk
    "symbol.purva-ashadha": "কুলা বা হাতীদাঁত",
    # EN: The Vishvedevas (universal gods)
    "deity.uttara-ashadha": "বিশ্বদেৱ (সাৰ্বজনীন দেৱতা)",
    # EN: An elephant tusk
    "symbol.uttara-ashadha": "হাতীদাঁত",
    # EN: Vishnu
    "deity.shravana": "বিষ্ণু",
    # EN: An ear, or three footprints
    "symbol.shravana": "কাণ, বা তিনিটা ভৰিৰ চিন",
    # EN: The eight Vasus
    "deity.dhanishta": "আঠজন বসু",
    # EN: A drum (mridanga)
    "symbol.dhanishta": "ঢোল (মৃদঙ্গ)",
    # EN: Varuna, lord of the waters
    "deity.shatabhisha": "বৰুণ, জলৰ অধিপতি",
    # EN: An empty circle
    "symbol.shatabhisha": "খালী বৃত্ত",
    # EN: Aja Ekapada
    "deity.purva-bhadrapada": "অজ একপাদ",
    # EN: Swords, or the front legs of a cot
    "symbol.purva-bhadrapada": "তৰোৱাল, বা খাটিয়াৰ আগফালৰ ভৰি",
    # EN: Ahir Budhnya, serpent of the deep
    "deity.uttara-bhadrapada": "অহিৰ্বুধ্ন্য, গভীৰ জলৰ সাপ",
    # EN: The back legs of a cot, or twins
    "symbol.uttara-bhadrapada": "খাটিয়াৰ পিছফালৰ ভৰি, বা যমজ",
    # EN: Pushan, the nourisher and guide
    "deity.revati": "পূষণ, পালনকৰ্তা আৰু পথপ্ৰদৰ্শক",
    # EN: A fish (or a drum)
    "symbol.revati": "মাছ (বা ঢোল)",
}

# app/naam_milan_text.py TEXT["as"] — page text of /naam-se-kundali-milan  [34]
NAAM_MILAN_TEXT = {
    # EN: Naam se Kundali Milan — Match 36 Gunas by Name, Free | {brand}
    # keep: {brand}
    "title": "নামেৰে কুণ্ডলী মিলন — নামৰ আদ্যক্ষৰেৰে 36 গুণ মিলন, বিনামূলীয়া | {brand}",
    # EN: Kundali milan by name: the first syllable of the boy's and girl's names gives each
    #     nakshatra and rashi, then the full 36-guna Ashtakoot match. Type names in Hindi or English
    #     — free, no sign-up.
    "desc": "নামেৰে কুণ্ডলী মিলন: বৰ আৰু কইনাৰ নামৰ প্ৰথম আখৰৰ পৰা নক্ষত্ৰ আৰু ৰাশি উলিয়াই সম্পূৰ্ণ অষ্টকূট 36 গুণ মিলন। নাম ইংৰাজী বা হিন্দীত লিখক — বিনামূলীয়া, ছাইন-আপ নোহোৱাকৈ।",
    # EN: Naam se Kundali Milan
    "crumb": "নামেৰে কুণ্ডলী মিলন",
    # EN: <h1>Naam se Kundali Milan — Match by Name</h1>
    "h1": "<h1>নামেৰে কুণ্ডলী মিলন — নামৰ আখৰেৰে গুণ মিলন</h1>",
    # EN: <p class="hi" lang="hi">नाम से कुंडली मिलान</p>
    "sub": "<p class=\"hi\">নামৰ প্ৰথম আখৰৰ পৰা নক্ষত্ৰ, ৰাশি আৰু 36 গুণ</p>",
    # EN: <p>When birth times are not known, tradition matches a couple by the <strong>first
    #     syllable of their names</strong>. Type both names in Hindi or English: we show the
    #     syllable used, its nakshatra pada and rashi, and the full 36-guna match.</p>
    "intro": "<p>জন্মৰ সময় নাজানিলে পৰম্পৰা অনুসৰি দুয়োজনৰ <strong>নামৰ প্ৰথম আখৰ</strong> ব্যৱহাৰ কৰি মিলন কৰা হয়। দুয়োজনৰে নাম ইংৰাজী বা হিন্দী (দেৱনাগৰী) আখৰেৰে লিখক: আমি দেখুৱাম কোনটো আখৰ ধৰা হ'ল, তাৰ নক্ষত্ৰ-পাদ আৰু ৰাশি, আৰু সম্পূৰ্ণ 36 গুণৰ মিলন।</p>",
    # EN: Open birth-chart Kundali Milan
    "open_milan": "জন্মকুণ্ডলীৰে কুণ্ডলী মিলন খোলক",
    # EN: Automatic, from the name
    "auto": "নামৰ পৰা নিজে নিজে",
    # EN: Other likely syllables for this name
    "alt_head": "এই নামৰ সম্ভাব্য অন্য আখৰ",
    # EN: All 108 syllables
    "all_head": "সকলো 108 টা নামাক্ষৰ",
    # EN: Boy's name (groom)
    "boy_label": "বৰৰ (ল'ৰাৰ) নাম",
    # EN: Girl's name (bride)
    "girl_label": "কইনাৰ (ছোৱালীৰ) নাম",
    # EN: e.g. Ram or राम
    "boy_ph": "যেনে Ram",
    # EN: e.g. Sita or सीता
    "girl_ph": "যেনে Sita",
    # EN: Change the first syllable
    "pick": "প্ৰথম আখৰ সলনি কৰক",
    # EN: Match the gunas
    "button": "গুণ মিলাই চাওক",
    # EN: This syllable belongs to Abhijit, the 28th nakshatra; in the 27-nakshatra wheel it is
    #     counted in Uttara Ashadha pada 4.
    "via.abhijit": "এই আখৰটো অভিজিৎ, অৰ্থাৎ 28 নং নক্ষত্ৰৰ; 27 নক্ষত্ৰৰ চক্ৰত ইয়াক উত্তৰাষাঢ়াৰ চতুৰ্থ পাদত গণনা কৰা হয়।",
    # EN: By the traditional rule, ब is read as व, and श as ष (with the a-vowel) or स.
    "via.alias": "পৰম্পৰাগত নিয়ম অনুসৰি ‘ব’ক ‘ৱ’ হিচাপে, আৰু ‘শ’ক ‘ষ’ (অ-কাৰসহ) বা ‘স’ হিচাপে পঢ়া হৈছে।",
    # EN: This exact syllable is not in the 108-syllable list, so the nearest syllable with the same
    #     consonant was used — change it below if you prefer.
    "via.nearest": "এই আখৰটো হুবহু 108 টাৰ তালিকাত নাই, গতিকে একেটা ব্যঞ্জনৰ আটাইতকৈ ওচৰৰ আখৰটো লোৱা হ'ল — ইচ্ছা হ'লে তলত সলনি কৰক।",
    # EN: An English spelling cannot settle this syllable (e.g. T = त or ट), so the most common
    #     reading was used — pick another below if needed.
    "via.latin": "ইংৰাজী বানানৰ পৰা এই আখৰটো নিশ্চিত কৰিব নোৱাৰি (যেনে T = ত নে ট), সেয়ে আটাইতকৈ প্ৰচলিত উচ্চাৰণ ধৰা হ'ল — প্ৰয়োজন হ'লে তলত আন এটা বাছক।",
    # EN: You chose this syllable.
    "via.chosen": "এই আখৰটো আপুনি নিজে বাছি লৈছে।",
    # EN: Could not read a first syllable from this name — pick one from the list below.
    "unreadable": "এই নামৰ পৰা প্ৰথম আখৰ পঢ়িব নোৱাৰিলোঁ — তলৰ তালিকাৰ পৰা এটা বাছক।",
    # EN: pada
    "pada": "পাদ",
    # EN: Result
    "result": "ফলাফল",
    # EN: <tr><th></th><th>First syllable</th><th>Nakshatra</th><th>Rashi</th></tr>
    "res.head": "<tr><th></th><th>প্ৰথম আখৰ</th><th>নক্ষত্ৰ</th><th>ৰাশি</th></tr>",
    # EN: Boy
    "boy": "বৰ",
    # EN: Girl
    "girl": "কইনা",
    # EN: <tr><th>Koota</th><th>Points</th><th>Why</th></tr>
    "res.th": "<tr><th>কূট</th><th>গুণ</th><th>কাৰণ</th></tr>",
    # EN: Total
    "total": "মুঠ",
    # EN: <strong>Mangal dosha: not applicable.</strong> Mangal dosha depends on where Mars stood
    #     from the Lagna, Moon and Venus at birth — a name cannot tell you that. Use birth-chart
    #     matching for it.
    "mangal": "<strong>মাংগলিক দোষ: প্ৰযোজ্য নহয়।</strong> মাংগলিক দোষ নিৰ্ভৰ কৰে জন্মৰ সময়ত লগ্ন, চন্দ্ৰ আৰু শুক্ৰৰ পৰা মঙ্গল ক'ত আছিল তাৰ ওপৰত — নামৰ পৰা সেয়া জনা নাযায়। তাৰ বাবে জন্মকুণ্ডলীৰে মিলন কৰক।",
    # EN: Match by birth details instead — more accurate, free
    "res.cta": "বৰং জন্মৰ বিৱৰণৰে মিলাওক — অধিক নিৰ্ভুল, বিনামূলীয়া",
    # EN: <div class="box"><p><strong>Please note:</strong> name-based matching is a traditional
    #     shortcut, used when birth details are not known. It assumes each name was chosen from the
    #     syllable of the person's birth nakshatra — which today is often not the case. Matching
    #     from the date, time and place of birth is far more accurate, and is the only way to check
    #     Mangal dosha.</p></div>
    "caveat": "<div class=\"box\"><p><strong>অনুগ্ৰহ কৰি মনত ৰাখিব:</strong> নামেৰে মিলন এক পৰম্পৰাগত চমু পদ্ধতি, যিটো জন্মৰ বিৱৰণ নাজানিলে ব্যৱহাৰ কৰা হয়। ই ধৰি লয় যে নামটো জন্ম নক্ষত্ৰৰ আখৰৰ পৰা ৰখা হৈছিল — আজিকালি প্ৰায়ে তেনে নহয়। জন্মৰ তাৰিখ, সময় আৰু স্থানেৰে কৰা কুণ্ডলী মিলন বহু বেছি নিৰ্ভুল, আৰু মাংগলিক দোষ কেৱল তেনেকৈয়ে চাব পাৰি।</p></div>",
    # EN: <tr><th>Rashi</th><th>Name syllables</th></tr>
    "syl.head": "<tr><th>ৰাশি</th><th>নামাক্ষৰ</th></tr>",
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
    "explainer": " <h2>নামেৰে মিলন কেনেকৈ হয়</h2> <p>27 টা নক্ষত্ৰৰ প্ৰতিটোৰ চাৰিটা পাদ, আৰু প্ৰতিটো পাদৰ এটা আখৰ (নামাক্ষৰ) — মুঠ 108 টা। নামটো যি পাদৰ আখৰেৰে <strong>আৰম্ভ হয়</strong>, সেইটোৱেই সেই ব্যক্তিৰ নক্ষত্ৰ, আৰু ইয়াৰ ৰাশিয়েই চন্দ্ৰ ৰাশি বুলি ধৰা হয়। তাৰ পিছত এই দুটা নক্ষত্ৰৰ পৰা সেই একেটা <strong>অষ্টকূট (36 গুণ)</strong> মিলন কৰা হয়, যিটো জন্মকুণ্ডলীৰে কৰা হয় — বৰ্ণ, বশ্য, তাৰা, যোনি, গ্ৰহ মৈত্ৰী, গণ, ভকূট আৰু নাড়ী — আমাৰ কুণ্ডলী মিলন সঁজুলিৰ সেই একে গণনা-পদ্ধতিৰে।</p> <h3>প্ৰথম আখৰ কেনেকৈ পঢ়া হয়</h3> <ul> <li>প্ৰথম আখৰৰ প্ৰথম ব্যঞ্জন আৰু তাৰ স্বৰচিহ্ন লোৱা হয়: <strong>Priya → পী</strong>, <strong>Kshitij → কী</strong>। হ্ৰস্ব আৰু দীঘল স্বৰ একে ধৰা হয় (ই/ঈ, উ/ঊ); ঐক এ আৰু ঔক ও ধৰা হয়।</li> <li>‘ব’ক ‘ৱ’ হিচাপে, আৰু ‘শ’ক ‘ষ’ (অ-কাৰসহ) বা ‘স’ হিচাপে পঢ়া হয়; ঋক ৰী।</li> <li>অভিজিৎ নক্ষত্ৰৰ আখৰ ({abhijit}) উত্তৰাষাঢ়াৰ চতুৰ্থ পাদত গণনা কৰা হয়।</li> <li>ইংৰাজীত লিখা নাম লিপ্যন্তৰ কৰি পঢ়া হয়; T, D, N, Th, Dh ৰ দৰে আখৰে দুটা বেলেগ আখৰ বুজাব পাৰে (ত/ট, দ/ড), সেয়ে ফলাফলত দেখুওৱা হয় কোনটো আখৰ ধৰা হ'ল, আৰু আপুনি আন এটা বাছিব পাৰে। হিন্দী (দেৱনাগৰী) আখৰেৰে লিখা নাম হুবহু পঢ়া হয়।</li> </ul> <h3>ৰাশি অনুসৰি নামাক্ষৰ</h3> {syllables} <p>প্ৰতিটো নক্ষত্ৰৰ আখৰ, দেৱতা, গণ আৰু নাড়ী জানিবলৈ চাওক <a href=\"{href}\">27 টা নক্ষত্ৰৰ তালিকা</a>।</p>",
}

# app/naam_milan_text.py ENGINE["as"] — score-band notes and the convention note of a naam-milan result  [5]
NAAM_MILAN_ENGINE = {
    # EN: Below the traditional minimum of 18 gunas.
    "band_note0": "পৰম্পৰাগত সৰ্বনিম্ন 18 গুণতকৈ কম।",
    # EN: In the traditional 18-24 gunas band.
    "band_note1": "পৰম্পৰাগত 18-24 গুণৰ সীমাত।",
    # EN: In the traditional 25-32 gunas band.
    "band_note2": "পৰম্পৰাগত 25-32 গুণৰ সীমাত।",
    # EN: In the traditional 33-36 gunas band.
    "band_note3": "পৰম্পৰাগত 33-36 গুণৰ সীমাত।",
    # EN: The 18/25/33 guna thresholds are a widely used convention, not a measurement. Astrologers
    #     often accept a lower total if the heavily weighted kootas are free of dosha.
    "convention_note": "18/25/33 গুণৰ সীমাবোৰ বহুলভাৱে প্ৰচলিত নিয়ম, জোখ-মাপ নহয়। অধিক গুণৰ কূটবোৰ দোষমুক্ত হ'লে জ্যোতিষীসকলে প্ৰায়ে কম মুঠ নম্বৰকো গ্ৰহণ কৰে।",
}

# ----------------------------------------------------------------------------
# muhurat   /muhurat/<kind>-<year>
# ----------------------------------------------------------------------------

# app/muhurat_text.py TEXT["as"] — page text of /muhurat/<kind>-<year> (the mundan-only keys are MUHURAT_MUNDAN)  [37]
MUHURAT_TEXT = {
    # EN: Vivah Muhurat
    "kind.vivah": "বিবাহ মুহূৰ্ত",
    # EN: Griha Pravesh Muhurat
    "kind.griha-pravesh": "গৃহ প্ৰৱেশ মুহূৰ্ত",
    # EN: wedding
    "noun.vivah": "বিবাহ",
    # EN: house-warming
    "noun.griha-pravesh": "গৃহ প্ৰৱেশ",
    # EN: {name} {year}: Auspicious {noun_title} Dates (New Delhi) | {brand}
    # keep: {brand} {year}
    # may also use: {name} {noun_title} {noun}
    "title": "{name} {year}: শুভ {noun_title} তাৰিখ (নতুন দিল্লী) | {brand}",
    # EN: {name} {year}: auspicious {noun} dates
    # keep: {year}
    # may also use: {name} {noun}
    "h1": "{name} {year}: শুভ {noun} তাৰিখ",
    # EN: {name} {year} for New Delhi — month-by-month auspicious {noun} dates with tithi and
    #     nakshatra. {count} dates; Chaturmas, Kharmas, Adhik Maas, Pitru Paksha and Guru/Shukra
    #     asta explained.
    # keep: {count} {year}
    # may also use: {name} {noun}
    "desc": "নতুন দিল্লীৰ বাবে {name} {year} — তিথি আৰু নক্ষত্ৰৰ সৈতে মাহ অনুসৰি শুভ {noun} তাৰিখ। {count} টা তাৰিখ; চাতুৰ্মাস্য, খৰমাস, অধিমাস, পিতৃ পক্ষ আৰু গুৰু/শুক্ৰ অস্তৰ ব্যাখ্যাসহ।",
    # EN: <p class="hi" lang="hi">{name_hi} {year}</p>
    # keep: {year}
    # may also use: {name} {noun}
    "sub": "<p class=\"hi\">{name} {year}</p>",
    # EN: {label} · IST
    # keep: {label}
    "place": "{label} · ভাৰতীয় সময়",
    # EN: <p>By the panchang there are <strong>{count}</strong> {name_lower} dates in {year} for New
    #     Delhi, in {months}. Each date passes the classical checks on the sunrise tithi, nakshatra,
    #     weekday, yoga and Bhadra, and falls outside Chaturmas, Kharmas, Adhik Maas, Pitru Paksha
    #     and the combustion (asta) of Jupiter and Venus.</p>
    # keep: {count} {months} {year}
    # may also use: {name_lower} {name} {noun}
    "intro": "<p>পঞ্জিকা অনুসৰি নতুন দিল্লীৰ বাবে {year} চনত {months}ত {name_lower}ৰ <strong>{count}</strong> টা তাৰিখ আছে। প্ৰতিটো তাৰিখে সূৰ্যোদয়ৰ তিথি, নক্ষত্ৰ, বাৰ, যোগ আৰু ভদ্ৰাৰ শাস্ত্ৰীয় পৰীক্ষা পাৰ হয়, আৰু চাতুৰ্মাস্য, খৰমাস, অধিমাস, পিতৃ পক্ষ আৰু বৃহস্পতি-শুক্ৰৰ অস্তৰ বাহিৰত পৰে।</p>",
    # EN: <p><strong>Timings vary by city.</strong> These dates are reckoned from New Delhi's
    #     sunrise; elsewhere a tithi or nakshatra can change on a different day. The exact muhurat
    #     (lagna) for a wedding or griha pravesh should be fixed by your family priest. Check your
    #     own city in the Muhurat Finder.</p>
    "note": "<p><strong>সময় চহৰ অনুসৰি সলনি হয়।</strong> এই তাৰিখবোৰ নতুন দিল্লীৰ সূৰ্যোদয় অনুসৰি গণনা কৰা; আন ঠাইত তিথি বা নক্ষত্ৰ বেলেগ দিনা সলনি হ'ব পাৰে। বিবাহ বা গৃহ প্ৰৱেশৰ ঠিক মুহূৰ্ত (লগ্ন) আপোনাৰ পৰিয়ালৰ পুৰোহিতে ঠিক কৰিব লাগে। নিজৰ চহৰ মুহূৰ্ত বিচাৰকত চাওক।</p>",
    # EN: Find muhurat for your city — free
    "cta": "আপোনাৰ চহৰৰ মুহূৰ্ত বিচাৰক — বিনামূলীয়া",
    # EN: {name} {year}
    # keep: {name} {year}
    "crumb": "{name} {year}",
    # EN: More muhurat dates
    "more": "আৰু মুহূৰ্তৰ তাৰিখ",
    # EN: {name} {year}
    # keep: {name} {year}
    "link.kind": "{name} {year}",
    # EN: Today's Panchang
    "link.panchang": "আজিৰ পঞ্জিকা",
    # EN: Kundali Milan
    "link.milan": "কুণ্ডলী মিলন",
    # EN: When there is no {name_lower} in {year}
    # keep: {year}
    # may also use: {name_lower} {name} {noun}
    "periods.h2": "{year} চনত কেতিয়া {name_lower} নাথাকে",
    # EN: No {name_lower} is given during these periods. The dates are computed from the panchang
    #     (New Delhi, sunrise):
    # may also use: {name_lower} {name} {noun}
    "periods.intro": "এই সময়ছোৱাবোৰত {name_lower} দিয়া নহয়। তাৰিখবোৰ পঞ্জিকাৰ পৰা গণনা কৰা (নতুন দিল্লী, সূৰ্যোদয়):",
    # EN: <li><strong>{period}</strong>, {range} — {about}.</li>
    # keep: {about} {period} {range}
    "periods.item": "<li><strong>{period}</strong>, {range} — {about}।</li>",
    # EN: No {name_lower} in {month} — {periods}.
    # keep: {month} {periods}
    # may also use: {name_lower} {name} {noun}
    "none.periods": "{month}ত {name_lower} নাই — {periods}।",
    # EN: No {name_lower} in {month} — no day this month passes the tithi, nakshatra, weekday and
    #     yoga checks.
    # keep: {month}
    # may also use: {name_lower} {name} {noun}
    "none.plain": "{month}ত {name_lower} নাই — এই মাহৰ কোনো দিনেই তিথি, নক্ষত্ৰ, বাৰ আৰু যোগৰ পৰীক্ষা পাৰ নহয়।",
    # EN: <tr><th>Date</th><th>Day</th><th>Tithi</th><th>Nakshatra</th></tr>
    "th": "<tr><th>তাৰিখ</th><th>বাৰ</th><th>তিথি</th><th>নক্ষত্ৰ</th></tr>",
    # EN: Muhurat page not found
    "nf.title": "মুহূৰ্তৰ পৃষ্ঠা পোৱা নগ'ল",
    # EN: Open the Muhurat Finder
    "nf.open": "মুহূৰ্ত বিচাৰক খোলক",
    # EN: Chaturmas
    "period.chaturmas": "চাতুৰ্মাস্য",
    # EN: Devshayani Ekadashi to Devuthani Ekadashi, when Lord Vishnu is in yoga-nidra
    "period_about.chaturmas": "দেৱশয়নী একাদশীৰ পৰা দেৱোত্থান একাদশীলৈ, যেতিয়া ভগৱান বিষ্ণু যোগনিদ্ৰাত থাকে",
    # EN: Kharmas
    "period.kharmas": "খৰমাস",
    # EN: the Sun in Dhanu (Sagittarius) or Meena (Pisces)
    "period_about.kharmas": "সূৰ্য ধনু বা মীন ৰাশিত থকা সময়",
    # EN: Adhik Maas
    "period.adhik_maas": "অধিমাস",
    # EN: an intercalary lunar month with no solar ingress
    "period_about.adhik_maas": "সূৰ্যৰ ৰাশি পৰিৱৰ্তন নথকা এক অতিৰিক্ত চান্দ্ৰ মাহ",
    # EN: Pitru Paksha
    "period.pitru_paksha": "পিতৃ পক্ষ",
    # EN: Bhadrapada Purnima to Sarva Pitru Amavasya, the fortnight of shraddha
    "period_about.pitru_paksha": "ভাদ পূৰ্ণিমাৰ পৰা সৰ্বপিতৃ অমাৱস্যালৈ, শ্ৰাদ্ধৰ পক্ষ",
    # EN: Shukra Asta
    "period.shukra_asta": "শুক্ৰ অস্ত",
    # EN: Venus combust (too close to the Sun to be seen), with 3 days either side
    "period_about.shukra_asta": "শুক্ৰ অস্তমিত (সূৰ্যৰ অতি ওচৰত থকা বাবে দেখা নাযায়), দুয়োফালে 3 দিনসহ",
    # EN: Guru Asta
    "period.guru_asta": "গুৰু অস্ত",
    # EN: Jupiter combust (too close to the Sun to be seen), with 3 days either side
    "period_about.guru_asta": "বৃহস্পতি অস্তমিত (সূৰ্যৰ অতি ওচৰত থকা বাবে দেখা নাযায়), দুয়োফালে 3 দিনসহ",
}

# app/muhurat_text.py MUNDAN["as"] — the mundan (first haircut) muhurat's own wording  [5]
MUHURAT_MUNDAN = {
    # EN: Mundan Muhurat
    "kind.mundan": "মুণ্ডন মুহূৰ্ত",
    # EN: mundan
    "noun.mundan": "মুণ্ডন",
    # EN: <p><strong>Timings vary by city.</strong> These dates are reckoned from New Delhi's
    #     sunrise; elsewhere a tithi or nakshatra can change on a different day. The exact muhurat
    #     for the mundan (chudakarma) should be fixed by your family priest. Check your own city in
    #     the Muhurat Finder.</p>
    "note.mundan": "<p><strong>সময় চহৰ অনুসৰি সলনি হয়।</strong> এই তাৰিখবোৰ নতুন দিল্লীৰ সূৰ্যোদয় অনুসৰি গণনা কৰা; আন ঠাইত তিথি বা নক্ষত্ৰ বেলেগ দিনা সলনি হ'ব পাৰে। মুণ্ডনৰ (চূড়াকৰ্ম) ঠিক মুহূৰ্ত আপোনাৰ পৰিয়ালৰ পুৰোহিতে ঠিক কৰিব লাগে। নিজৰ চহৰ মুহূৰ্ত বিচাৰকত চাওক।</p>",
    # EN: {name} {year}: the rules these dates follow
    # keep: {name} {year}
    "rules.h2": "{name} {year}: এই তাৰিখবোৰে অনুসৰণ কৰা নিয়ম",
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
    "rules.body": "<p>মুণ্ডন (চূড়াকৰ্ম, প্ৰথম চুলি কটা)ক বিবাহৰ নহয়, নিজৰ নিয়মেৰে বিচাৰ কৰা হয়। তলৰ নিষিদ্ধ বিষয়ৰ কোনোটো প্ৰযোজ্য নহ'লে আৰু দিনটো শুভ নক্ষত্ৰত পৰিলেহে তালিকাত দিয়া হয়:</p><ul><li><strong>নিষিদ্ধ তিথি:</strong> {tithi_bad}।</li><li><strong>শুভ তিথি</strong> (যিকোনো পক্ষত): {tithi_good}; বাকীবোৰ মধ্যম।</li><li><strong>শুভ নক্ষত্ৰ</strong> (তলৰ প্ৰতিটো তাৰিখ এটাত পৰে): {nak_good}।</li><li><strong>নিষিদ্ধ নক্ষত্ৰ:</strong> {nak_bad}।</li><li><strong>নিষিদ্ধ যোগ আৰু কৰণ:</strong> {yoga_bad}, আৰু ভদ্ৰা (বিষ্টি)।</li><li><strong>বাৰ:</strong> {vara_good} শুভ; {vara_bad} দিনটোক বাদ নিদিয়াকৈ বিপক্ষে গণ্য কৰা হয়, সেয়ে এনে কিছুমান তাৰিখ দেখা যায় - আপোনাৰ পৰিয়ালে সেই দিনবোৰ এৰাই চলিলে এৰি দিয়ক।</li></ul>",
}

# app/muhurat_text.py MONTHS["as"] — only if this page must spell the months differently from names_<code>.MONTHS; else leave ()  [12]
# (optional: may stay empty)
MUHURAT_MONTHS = ()   # or 12 month names, January first

# ----------------------------------------------------------------------------
# recurring /purnima-<year> /amavasya-<year> /pradosh-vrat-<year> ... (DIVASTRO-141)
# ----------------------------------------------------------------------------

# app/recurring_text.py TEXT["as"] — page text of /purnima-<year>, /amavasya-<year>, /pradosh-vrat-<year> ... (the keys it shares with VRAT_TEXT are taken from there)  [60]
RECURRING_TEXT = {
    # EN: Full Moon Dates and Tithi Time
    "what.purnima": "পূৰ্ণিমাৰ তাৰিখ আৰু তিথিৰ সময়",
    # EN: New Moon Dates and Tithi Time
    "what.amavasya": "অমাৱস্যাৰ তাৰিখ আৰু তিথিৰ সময়",
    # EN: All Dates and Pradosh Puja Time
    "what.pradosh": "সকলো তাৰিখ আৰু প্ৰদোষ পূজাৰ সময়",
    # EN: All Dates and Moonrise Time
    "what.sankashti": "সকলো তাৰিখ আৰু চন্দ্ৰোদয়ৰ সময়",
    # EN: All Dates and Nishita Puja Time
    "what.masik_shivratri": "সকলো তাৰিখ আৰু নিশীথ পূজাৰ সময়",
    # EN: All Dates and Kala Bhairav Puja
    "what.kalashtami": "সকলো তাৰিখ আৰু কালভৈৰৱ পূজা",
    # EN: {name} {year}: {what} (New Delhi)
    # keep: {name} {what} {year}
    "title": "{name} {year}: {what} (নতুন দিল্লী)",
    # EN: {name} {year}: {what}
    # keep: {name} {what} {year}
    "h1": "{name} {year}: {what}",
    # EN: All {count} {name} dates in {year} with weekday, Hindu month and tithi start and end for
    #     New Delhi. {about}{keytime}{next}
    # keep: {about} {count} {keytime} {name} {next} {year}
    "desc": "{year} চনৰ সকলো {count} টা {name}ৰ তাৰিখ, বাৰ, হিন্দু মাহ আৰু তিথি আৰম্ভ-শেষৰ সময়সহ, নতুন দিল্লীৰ বাবে। {about}{keytime}{next}",
    # EN: Full-moon vrat days for Satyanarayan puja, bathing and charity.
    "desc.about.purnima": "সত্যনাৰায়ণ পূজা, স্নান আৰু দানৰ বাবে পূৰ্ণিমাৰ ব্ৰতৰ দিন।",
    # EN: New-moon days for shraddha and tarpan, with Somvati and Shani Amavasya.
    "desc.about.amavasya": "শ্ৰাদ্ধ আৰু তৰ্পণৰ বাবে অমাৱস্যাৰ দিন, সোমৱতী আৰু শনি অমাৱস্যাসহ।",
    # EN: Lord Shiva's twilight fast on Trayodashi, with the puja window.
    "desc.about.pradosh": "ত্ৰয়োদশীত ভগৱান শিৱৰ গধূলিৰ উপবাস, পূজাৰ সময়সহ।",
    # EN: Lord Ganesha's fast on Krishna Chaturthi, broken after moonrise.
    "desc.about.sankashti": "কৃষ্ণ চতুৰ্থীত ভগৱান গণেশৰ উপবাস, চন্দ্ৰোদয়ৰ পিছত ভঙা।",
    # EN: The monthly night of Shiva on Krishna Chaturdashi, with the midnight puja.
    "desc.about.masik_shivratri": "কৃষ্ণ চতুৰ্দশীত শিৱৰ মাহেকীয়া ৰাতি, মাজৰাতিৰ পূজাসহ।",
    # EN: Kala Bhairava worship on Krishna Ashtami, every month.
    "desc.about.kalashtami": "প্ৰতি মাহে কৃষ্ণ অষ্টমীত কালভৈৰৱৰ পূজা।",
    # EN: Includes {label}.
    # keep: {label}
    "desc.key": " ইয়াত {label} আছে।",
    # EN: Next: {date}.
    # keep: {date}
    "desc.next": " পৰৱৰ্তী: {date}।",
    # EN: The next {name} is on <strong>{when}</strong> ({details}).
    # keep: {details} {name} {when}
    "ans.next": "পৰৱৰ্তী {name} <strong>{when}</strong> তাৰিখে ({details})।",
    # EN: The first {name} of {year} is on <strong>{when}</strong> ({details}). All {count} dates
    #     for {year} are listed below.
    # keep: {count} {details} {name} {when} {year}
    "ans.first": "{year} চনৰ প্ৰথম {name} <strong>{when}</strong> তাৰিখে ({details})। {year} চনৰ সকলো {count} টা তাৰিখ তলত তালিকাভুক্ত কৰা হ'ল।",
    # EN: All {count} {name} dates for {year} are listed below; the last was on
    #     <strong>{when}</strong>.
    # keep: {count} {name} {when} {year}
    "ans.past": "{year} চনৰ সকলো {count} টা {name}ৰ তাৰিখ তলত তালিকাভুক্ত কৰা হ'ল; শেষটো আছিল <strong>{when}</strong> তাৰিখে।",
    # EN: Dates for {year}: {link}.
    # keep: {link} {year}
    "ans.more": " {year} চনৰ তাৰিখ: {link}।",
    # EN: {name} {year}: all dates
    # keep: {name} {year}
    "table.h2": "{name} {year}: সকলো তাৰিখ",
    # EN: Date
    "th.date": "তাৰিখ",
    # EN: Hindu month
    "th.month": "হিন্দু মাহ",
    # EN: Tithi
    "th.tithi": "তিথি",
    # EN: Adhik {month}
    # keep: {month}
    "adhika": "অধিক {month}",
    # EN: Also:
    "also": "লগতে: ",
    # EN: <p class="note"><small>Months are amanta (a month ends on Amavasya, as in South and West
    #     India). North Indian purnimanta calendars name the dark fortnight one month
    #     later.</small></p>
    "months.note": "<p class=\"note\"><small>মাহবোৰ অমান্ত (অমাৱস্যাত মাহ শেষ হয়, দক্ষিণ আৰু পশ্চিম ভাৰতৰ দৰে)। উত্তৰ ভাৰতৰ পূৰ্ণিমান্ত পঞ্জিকাই কৃষ্ণ পক্ষৰ নাম এমাহ পিছৰ দিয়ে।</small></p>",
    # EN: Som Pradosh
    "variant.pradosh.0": "সোম প্ৰদোষ",
    # EN: Bhauma Pradosh
    "variant.pradosh.1": "ভৌম প্ৰদোষ",
    # EN: Shani Pradosh
    "variant.pradosh.5": "শনি প্ৰদোষ",
    # EN: Angarki Chaturthi
    "variant.sankashti.1": "অঙ্গাৰকী চতুৰ্থী",
    # EN: Somvati Amavasya
    "variant.amavasya.0": "সোমৱতী অমাৱস্যা",
    # EN: Shani Amavasya
    "variant.amavasya.5": "শনি অমাৱস্যা",
    # EN: What {name} is and how it is observed
    # keep: {name}
    "about.h2": "{name} কি আৰু কেনেকৈ পালন কৰা হয়",
    # EN: Panchang for your city
    "city.h2": "আপোনাৰ চহৰৰ পঞ্জিকা",
    # EN: Related dates and calendars
    "related.h2": "সম্পৰ্কিত তাৰিখ আৰু পঞ্জী",
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
    "about.purnima": "<p>পূৰ্ণিমা হ'ল চন্দ্ৰ পূৰ্ণ হোৱা তিথি, শুক্ল পক্ষৰ শেষ (15 নং) তিথি, যেতিয়া চন্দ্ৰ সূৰ্যৰ বিপৰীত দিশত থাকি পূৰ্ণকৈ জিলিকে। ভক্তসকলে উপবাস কৰে, ভোৰে স্নান কৰে (সম্ভৱ হ'লে নদী বা তীৰ্থত), ভগৱান বিষ্ণুৰ পূজা কৰে - সত্যনাৰায়ণ কথা পূৰ্ণিমাৰ সাধাৰণ পূজা - আৰু সন্ধিয়া চন্দ্ৰলৈ অৰ্ঘ্য দিয়ে। এইদিনা খাদ্য, কাপোৰ বা ধনৰ দান কৰিলে পুণ্য বহুগুণ হয় বুলি কোৱা হয়।</p><p>কিছুমান পূৰ্ণিমা নিজেই উৎসৱ: গুৰু পূৰ্ণিমা, শৰৎ পূৰ্ণিমা, কাৰ্তিক পূৰ্ণিমা আৰু বুদ্ধ পূৰ্ণিমা, আৰু হোলিকা দহন ফাগুনৰ পূৰ্ণিমাত পালন কৰা হয়।</p>",
    # EN: <p>Amavasya is the new-moon tithi, the 30th and last tithi of the dark fortnight (Krishna
    #     paksha), when the Moon is in conjunction with the Sun and cannot be seen. It is the day of
    #     the ancestors (pitru): families offer tarpan and shraddha, feed Brahmins and the poor,
    #     give in charity and bathe in holy water. Many people fast and avoid starting anything
    #     new.</p><p>An Amavasya on a Monday is called Somvati Amavasya and one on a Saturday Shani
    #     Amavasya, both given extra weight. The great Amavasyas are Mauni Amavasya, Sarva Pitru
    #     Amavasya (the end of Pitru Paksha) and the Amavasya of Diwali.</p>
    "about.amavasya": "<p>অমাৱস্যা হ'ল অমাৱস্যা তিথি, কৃষ্ণ পক্ষৰ 30 নং আৰু শেষ তিথি, যেতিয়া চন্দ্ৰ সূৰ্যৰ লগত যুতি হয় আৰু দেখা নাযায়। এয়া পিতৃসকলৰ দিন: পৰিয়ালবোৰে তৰ্পণ আৰু শ্ৰাদ্ধ কৰে, ব্ৰাহ্মণ আৰু দৰিদ্ৰক খুৱায়, দান কৰে আৰু পবিত্ৰ পানীত স্নান কৰে। বহুতে উপবাস কৰে আৰু নতুন একো আৰম্ভ নকৰে।</p><p>সোমবাৰে পৰা অমাৱস্যাক সোমৱতী অমাৱস্যা আৰু শনিবাৰে পৰাটোক শনি অমাৱস্যা বোলে, দুয়োটাকে অতিৰিক্ত গুৰুত্ব দিয়া হয়। মহান অমাৱস্যাবোৰ হ'ল মৌনী অমাৱস্যা, সৰ্বপিতৃ অমাৱস্যা (পিতৃ পক্ষৰ শেষ) আৰু দীপাৱলীৰ অমাৱস্যা।</p>",
    # EN: <p>Pradosh Vrat is the fast of Lord Shiva kept on Trayodashi, the 13th tithi, of both
    #     fortnights - so twice a month. Pradosh kaal is the twilight window just after sunset, when
    #     Shiva is believed to be most pleased. Devotees fast through the day, bathe, and do Shiva
    #     puja in the Pradosh window: abhishek with water, milk and bilva (bel) leaves, a lamp and
    #     the Pradosh stotra or Shiva Chalisa. The fast is broken after the puja.</p><p>A Pradosh on
    #     Monday is Som Pradosh, on Tuesday Bhauma Pradosh and on Saturday Shani Pradosh; the
    #     Saturday one is considered especially powerful.</p>
    "about.pradosh": "<p>প্ৰদোষ ব্ৰত হ'ল দুয়োটা পক্ষৰ ত্ৰয়োদশী, 13 নং তিথিত পালন কৰা ভগৱান শিৱৰ উপবাস - গতিকে মাহত দুবাৰ। প্ৰদোষ কাল হ'ল সূৰ্যাস্তৰ ঠিক পিছৰ গধূলিৰ সময়, যেতিয়া শিৱ আটাইতকৈ সন্তুষ্ট হয় বুলি বিশ্বাস কৰা হয়। ভক্তসকলে গোটেই দিনটো উপবাস কৰে, স্নান কৰে, আৰু প্ৰদোষ কালত শিৱ পূজা কৰে: পানী, গাখীৰ আৰু বেলপাতেৰে অভিষেক, প্ৰদীপ আৰু প্ৰদোষ স্তোত্ৰ বা শিৱ চালীসা। পূজাৰ পিছত উপবাস ভঙা হয়।</p><p>সোমবাৰৰ প্ৰদোষ সোম প্ৰদোষ, মঙ্গলবাৰৰ ভৌম প্ৰদোষ আৰু শনিবাৰৰ শনি প্ৰদোষ; শনিবাৰৰটো বিশেষভাৱে শক্তিশালী বুলি গণ্য কৰা হয়।</p>",
    # EN: <p>Sankashti Chaturthi (Sankat Hara Chaturthi) is the monthly fast of Lord Ganesha on
    #     Chaturthi, the 4th tithi, of the dark fortnight (Krishna paksha); "sankashti" means
    #     deliverance from trouble. Devotees fast through the day, worship Ganesha in the evening
    #     and break the fast only after seeing the Moon and offering it arghya, which is why
    #     moonrise is the key time on this page.</p><p>A Sankashti on a Tuesday is Angarki Sankashti
    #     Chaturthi, believed to be especially fruitful. The Sankashti of Magha (purnimanta) is kept
    #     in North India as Sakat Chauth.</p>
    "about.sankashti": "<p>সংকষ্টী চতুৰ্থী (সংকট হৰা চতুৰ্থী) হ'ল কৃষ্ণ পক্ষৰ চতুৰ্থী, 4 নং তিথিত ভগৱান গণেশৰ মাহেকীয়া উপবাস; “সংকষ্টী”ৰ অৰ্থ বিপদৰ পৰা মুক্তি। ভক্তসকলে গোটেই দিনটো উপবাস কৰে, সন্ধিয়া গণেশৰ পূজা কৰে আৰু চন্দ্ৰ দেখি তালৈ অৰ্ঘ্য দিয়াৰ পিছতহে উপবাস ভাঙে, সেয়ে এই পৃষ্ঠাত চন্দ্ৰোদয়েই মূল সময়।</p><p>মঙ্গলবাৰৰ সংকষ্টী অঙ্গাৰকী সংকষ্টী চতুৰ্থী, বিশেষভাৱে ফলদায়ক বুলি বিশ্বাস কৰা হয়। মাঘ (পূৰ্ণিমান্ত)ৰ সংকষ্টী উত্তৰ ভাৰতত সকট চৌথ হিচাপে পালন কৰা হয়।</p>",
    # EN: <p>Masik Shivratri (monthly Shivratri) is the night of Lord Shiva kept on Chaturdashi, the
    #     14th tithi, of the dark fortnight (Krishna paksha) every month. Devotees fast and keep
    #     vigil through the night, bathing the Shiva linga with water, milk, honey and bilva leaves
    #     and chanting "Om Namah Shivaya". The best time for the puja is Nishita kaal, the midnight
    #     window.</p><p>Maha Shivratri, which falls on Krishna Chaturdashi of Phalguna (Magha in the
    #     amanta calendar), is the greatest of the twelve.</p>
    "about.masik_shivratri": "<p>মাহেকীয়া শিৱৰাত্ৰি হ'ল প্ৰতি মাহৰ কৃষ্ণ পক্ষৰ চতুৰ্দশী, 14 নং তিথিত পালন কৰা ভগৱান শিৱৰ ৰাতি। ভক্তসকলে উপবাস কৰে আৰু ৰাতিটো জাগি থাকে, শিৱলিংগক পানী, গাখীৰ, মৌ আৰু বেলপাতেৰে স্নান কৰায় আৰু “ওঁ নমঃ শিৱায়” জপ কৰে। পূজাৰ আটাইতকৈ ভাল সময় নিশীথ কাল, মাজৰাতিৰ সময়।</p><p>মহাশিৱৰাত্ৰি, যিটো ফাগুনৰ কৃষ্ণ চতুৰ্দশীত (অমান্ত পঞ্জিকাত মাঘ) পৰে, বাৰটাৰ ভিতৰত আটাইতকৈ মহান।</p>",
    # EN: <p>Kalashtami (Kala Ashtami) is the monthly day of Lord Kala Bhairava, the fierce form of
    #     Shiva who guards time, kept on Ashtami, the 8th tithi, of the dark fortnight (Krishna
    #     paksha). Devotees fast, worship Bhairava at night with a mustard-oil lamp and offerings
    #     such as black sesame, and feed dogs, which are associated with him.</p><p>The Kalashtami
    #     of Margashirsha in the purnimanta calendar (Kartika in the amanta calendar) is
    #     Kalabhairava Jayanti, his appearance day and the most important of the year.</p>
    "about.kalashtami": "<p>কালাষ্টমী হ'ল সময়ৰ ৰক্ষক শিৱৰ উগ্ৰ ৰূপ ভগৱান কালভৈৰৱৰ মাহেকীয়া দিন, কৃষ্ণ পক্ষৰ অষ্টমী, 8 নং তিথিত পালন কৰা। ভক্তসকলে উপবাস কৰে, ৰাতি সৰিয়হৰ তেলৰ প্ৰদীপ আৰু ক'লা তিলৰ দৰে অৰ্পণেৰে ভৈৰৱৰ পূজা কৰে, আৰু তেওঁৰ লগত জড়িত কুকুৰক খুৱায়।</p><p>পূৰ্ণিমান্ত পঞ্জিকাৰ আঘোণৰ (অমান্ত পঞ্জিকাত কাতি) কালাষ্টমী হ'ল কালভৈৰৱ জয়ন্তী, তেওঁৰ আবিৰ্ভাৱৰ দিন আৰু বছৰৰ আটাইতকৈ গুৰুত্বপূৰ্ণ।</p>",
    # EN: Purnima can begin one evening and end the next afternoon, so the day the tithi starts and
    #     the day of the vrat can differ. The rule settles it: the vrat goes to the day on which the
    #     tithi covers Madhyahna (the middle fifth of the daytime); if it covers Madhyahna on both
    #     days, the earlier day is taken. Some traditions use the sunrise tithi for the holy bath
    #     and charity instead; the table gives the start and end of the tithi so you can check.
    "note.purnima": "পূৰ্ণিমা এটা সন্ধিয়া আৰম্ভ হৈ পিছদিনা দুপৰীয়া শেষ হ'ব পাৰে, গতিকে তিথি আৰম্ভ হোৱা দিন আৰু ব্ৰতৰ দিন বেলেগ হ'ব পাৰে। নিয়মে ইয়াক ঠিক কৰে: ব্ৰত সেই দিনলৈ যায় যিদিনা তিথিয়ে মধ্যাহ্ন (দিনৰ মাজৰ পঞ্চমাংশ) ঢাকি ৰাখে; দুয়োদিনাই মধ্যাহ্ন ঢাকিলে আগৰ দিনটো লোৱা হয়। কিছুমান পৰম্পৰাই পবিত্ৰ স্নান আৰু দানৰ বাবে সূৰ্যোদয়ৰ তিথি ব্যৱহাৰ কৰে; তালিকাত তিথিৰ আৰম্ভ আৰু শেষ দিয়া আছে যাতে আপুনি মিলাই চাব পাৰে।",
    # EN: Amavasya is a daytime observance (shraddha and tarpan are done in the day), so the date is
    #     the day on which the Amavasya tithi is running at sunrise. The tithi often starts the
    #     evening before, so the times in the table can begin on the previous date. Festival
    #     Amavasyas follow their own rules - Diwali is fixed by Pradosh, Sarva Pitru Amavasya by
    #     Aparahna - and can fall a day away from the date here.
    "note.amavasya": "অমাৱস্যা দিনৰ পালন (শ্ৰাদ্ধ আৰু তৰ্পণ দিনত কৰা হয়), গতিকে তাৰিখ হ'ল সেইদিনা যিদিনা সূৰ্যোদয়ত অমাৱস্যা তিথি চলি থাকে। তিথি প্ৰায়ে আগৰ সন্ধিয়াই আৰম্ভ হয়, সেয়ে তালিকাৰ সময় আগৰ তাৰিখত আৰম্ভ হ'ব পাৰে। উৎসৱৰ অমাৱস্যাই নিজৰ নিয়ম মানে - দীপাৱলী প্ৰদোষেৰে, সৰ্বপিতৃ অমাৱস্যা অপৰাহ্ণেৰে ঠিক হয় - আৰু ইয়াত দিয়া তাৰিখৰ পৰা এদিন আঁতৰত পৰিব পাৰে।",
    # EN: The date is decided in the evening, not at sunrise: the vrat goes to the day on which
    #     Trayodashi is running in Pradosh kaal after sunset, so a Trayodashi that starts at noon
    #     and ends the next afternoon is kept on the first day. If the tithi touches Pradosh kaal on
    #     two evenings, the earlier evening is taken. The puja window in the table starts at sunset
    #     in New Delhi, so it moves through the year and from city to city.
    "note.pradosh": "তাৰিখ সন্ধিয়া ঠিক হয়, সূৰ্যোদয়ত নহয়: ব্ৰত সেইদিনালৈ যায় যিদিনা সূৰ্যাস্তৰ পিছৰ প্ৰদোষ কালত ত্ৰয়োদশী চলি থাকে, গতিকে দুপৰীয়া আৰম্ভ হৈ পিছদিনা দুপৰীয়া শেষ হোৱা ত্ৰয়োদশী প্ৰথম দিনা পালন কৰা হয়। তিথিয়ে দুটা সন্ধিয়া প্ৰদোষ কাল চুলে আগৰ সন্ধিয়াটো লোৱা হয়। তালিকাৰ পূজাৰ সময় নতুন দিল্লীৰ সূৰ্যাস্তৰ পৰা আৰম্ভ হয়, সেয়ে বছৰটোত আৰু চহৰ অনুসৰি সলনি হয়।",
    # EN: Sankashti is decided by the Moon, not the Sun: the vrat goes to the evening on which
    #     Chaturthi is running at moonrise, since that is when the fast is broken. The date can
    #     therefore differ from the Chaturthi date of a Panchang that goes by sunrise. Moonrise is
    #     roughly 50 minutes later each day and differs by several minutes between cities, so check
    #     it for your own city.
    "note.sankashti": "সংকষ্টী সূৰ্যই নহয়, চন্দ্ৰই ঠিক কৰে: ব্ৰত সেই সন্ধিয়ালৈ যায় যিটো সন্ধিয়া চন্দ্ৰোদয়ত চতুৰ্থী চলি থাকে, কাৰণ তেতিয়াই উপবাস ভঙা হয়। গতিকে তাৰিখ সূৰ্যোদয় অনুসৰি চলা পঞ্জিকাৰ চতুৰ্থীৰ তাৰিখৰ পৰা বেলেগ হ'ব পাৰে। চন্দ্ৰোদয় প্ৰতিদিনে প্ৰায় 50 মিনিট পলমকৈ হয় আৰু চহৰ অনুসৰি কেইমিনিটমান বেলেগ, সেয়ে নিজৰ চহৰৰ বাবে চাই লওক।",
    # EN: This is a midnight observance, so the date is the day on which Chaturdashi is running at
    #     Nishita kaal (the 8th of the 15 muhurtas of the night, around midnight). Nishita can fall
    #     just after 12 o'clock, in which case the puja is done in the early hours of the next date
    #     and the time shown carries that date. If the tithi touches Nishita on two nights, the
    #     earlier night is taken.
    "note.masik_shivratri": "এয়া মাজৰাতিৰ পালন, সেয়ে তাৰিখ হ'ল সেইদিনা যিদিনা নিশীথ কালত (ৰাতিৰ 15 টা মুহূৰ্তৰ 8 নং, মাজৰাতিৰ কাষত) চতুৰ্দশী চলি থাকে। নিশীথ 12 বজাৰ ঠিক পিছতো পৰিব পাৰে, তেনে ক্ষেত্ৰত পূজা পিছৰ তাৰিখৰ ভোৰবেলা কৰা হয় আৰু দেখুওৱা সময়ত সেই তাৰিখ থাকে। তিথিয়ে দুটা ৰাতি নিশীথ চুলে আগৰ ৰাতিটো লোৱা হয়।",
    # EN: Kalashtami is a night worship, so the date is the day on which Ashtami is running in
    #     Pradosh kaal (the evening window after sunset); the tithi may begin the previous morning
    #     or end during the night, so check its start and end times in the table. If it touches
    #     Pradosh kaal on two evenings, the earlier evening is taken. Some traditions go by the
    #     midnight tithi instead, which can occasionally differ by a day.
    "note.kalashtami": "কালাষ্টমী ৰাতিৰ পূজা, সেয়ে তাৰিখ হ'ল সেইদিনা যিদিনা প্ৰদোষ কালত (সূৰ্যাস্তৰ পিছৰ সন্ধিয়াৰ সময়) অষ্টমী চলি থাকে; তিথি আগদিনা ৰাতিপুৱা আৰম্ভ হ'ব পাৰে বা ৰাতিৰ ভিতৰত শেষ হ'ব পাৰে, সেয়ে তালিকাত ইয়াৰ আৰম্ভ আৰু শেষৰ সময় চাওক। দুটা সন্ধিয়া প্ৰদোষ কাল চুলে আগৰ সন্ধিয়াটো লোৱা হয়। কিছুমান পৰম্পৰাই মাজৰাতিৰ তিথি অনুসৰি চলে, যিটো কেতিয়াবা এদিনৰ পাৰ্থক্য হ'ব পাৰে।",
    # EN: What are the {name} dates in {year}?
    # keep: {name} {year}
    "faq.all_q": "{year} চনত {name}ৰ তাৰিখবোৰ কি কি?",
    # EN: There are {count} {name} dates in {year} (New Delhi): {dates}.
    # keep: {count} {dates} {name} {year}
    "faq.all_a": "{year} চনত {name}ৰ {count} টা তাৰিখ আছে (নতুন দিল্লী): {dates}।",
    # EN: When is the next {name}?
    # keep: {name}
    "faq.next_q": "পৰৱৰ্তী {name} কেতিয়া?",
    # EN: When is the first {name} of {year}?
    # keep: {name} {year}
    "faq.first_q": "{year} চনৰ প্ৰথম {name} কেতিয়া?",
    # EN: {name} is on {when} ({details}).
    # keep: {details} {name} {when}
    "faq.on_a": "{name} {when} তাৰিখে ({details})।",
    # EN: What is the {label} on {name} {short}?
    # keep: {label} {name} {short}
    "faq.key_q": "{short} তাৰিখৰ {name}ৰ {label} কি?",
    # EN: At what time does the {name} tithi start and end on {short}?
    # keep: {name} {short}
    "faq.tithi_q": "{short} তাৰিখে {name} তিথি কেতিয়া আৰম্ভ আৰু কেতিয়া শেষ হয়?",
    # EN: How is the {name} date decided?
    # keep: {name}
    "faq.why_q": "{name}ৰ তাৰিখ কেনেকৈ ঠিক কৰা হয়?",
    # EN: The date follows the rule: {rule}. In {year} this gives {count} dates (New Delhi).
    # keep: {count} {rule} {year}
    "faq.why_a": "তাৰিখ নিয়ম অনুসৰি: {rule}। {year} চনত ই {count} টা তাৰিখ দিয়ে (নতুন দিল্লী)।",
    # EN: Monthly vrat dates
    "hub.h2": "মাহেকীয়া ব্ৰতৰ তাৰিখ",
}

# ----------------------------------------------------------------------------
# hub       /sitemap
# ----------------------------------------------------------------------------

# app/hub_text.py LABELS["as"] — section names of the crawlable /sitemap page and the footer link block  [19]
HUB_LABELS = {
    # EN: Site map
    "sitemap": "চাইট মেপ",
    # EN: Panchang
    "panchang": "পঞ্জিকা",
    # EN: Rashifal (daily horoscope)
    "rashifal": "ৰাশিফল (দৈনিক ভৱিষ্যদ্বাণী)",
    # EN: Vrat &amp; festivals
    "vrat": "ব্ৰত &amp; উৎসৱ",
    # EN: Shubh muhurat
    "muhurat": "শুভ মুহূৰ্ত",
    # EN: Nakshatra
    "nakshatra": "নক্ষত্ৰ",
    # EN: Rashi (zodiac signs)
    "rashi": "ৰাশি (ৰাশিচক্ৰ)",
    # EN: Kathas
    "katha": "কথা",
    # EN: Free tools
    "tools": "বিনামূলীয়া সঁজুলি",
    # EN: Kundali Milan
    "milan": "কুণ্ডলী মিলন",
    # EN: Free Kundali
    "kundali": "বিনামূলীয়া কুণ্ডলী",
    # EN: Rahu Kaal
    "rahu": "ৰাহুকাল",
    # EN: Choghadiya
    "choghadiya": "চৌঘড়িয়া",
    # EN: Naam se Kundali Milan
    "naam": "নামেৰে কুণ্ডলী মিলন",
    # EN: Today's Panchang by city
    "cities": "চহৰ অনুসৰি আজিৰ পঞ্জিকা",
    # EN: Rashifal by sign
    "signs": "ৰাশি অনুসৰি ৰাশিফল",
    # EN: Vrat and festival calendars
    "years": "ব্ৰত আৰু উৎসৱৰ পঞ্জী",
    # EN: Ekadashi
    "ekadashi": "একাদশী",
    # EN: Every section of Divine Astro in one place: daily Panchang for Indian cities, Rashifal,
    #     vrat and festival dates, shubh muhurat, nakshatra and rashi guides, kathas and the free
    #     tools.
    "intro": "Divine Astro ৰ সকলো বিভাগ এঠাইত: ভাৰতীয় চহৰৰ দৈনিক পঞ্জিকা, ৰাশিফল, ব্ৰত আৰু উৎসৱৰ তাৰিখ, শুভ মুহূৰ্ত, নক্ষত্ৰ আৰু ৰাশিৰ গাইড, কথা আৰু বিনামূলীয়া সঁজুলি।",
}

# ----------------------------------------------------------------------------
# app       AI-narration vocabulary here; names_<code>.py and static/i18n/<code>.json beside it
# ----------------------------------------------------------------------------

# app/astro_terms.py TERMS["as"] — house / dasha / sign vocabulary for the AI narration and the chart labels  [16]
ASTRO_TERMS = {
    # EN: house
    "house": "ভাৱ",
    # EN: sign
    "sign": "ৰাশি",
    # EN: lord
    "lord": "অধিপতি",
    # EN: dasha
    "dasha": "দশা",
    # EN: mahadasha
    "mahadasha": "মহাদশা",
    # EN: antardasha
    "antardasha": "অন্তৰ্দশা",
    # EN: ascendant
    "ascendant": "লগ্ন",
    # EN: transit
    "transit": "গোচৰ",
    # EN: retrograde
    "retrograde": "বক্ৰী",
    # EN: exalted
    "exalted": "উচ্চ",
    # EN: debilitated
    "debilitated": "নীচ",
    # EN: own sign
    "own sign": "স্বক্ষেত্ৰ",
    # EN: Sade Sati
    "Sade Sati": "সাড়ে সাতি",
    # EN: Navamsa
    "Navamsa": "নৱাংশ",
    # EN: yoga
    "yoga": "যোগ",
    # EN: remedy
    "remedy": "প্ৰতিকাৰ",
}

# app/astro_terms.py MONTH_VARIANTS["as"] — other spellings of a Gregorian month the AI may write (month number -> spellings)
# (optional: may stay empty)
ASTRO_MONTHS = {}   # {month number: (other spellings,)}, e.g. {2: ("...",)}
