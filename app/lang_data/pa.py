"""Punjabi (ਪੰਜਾਬੀ, Gurmukhi) — the data a translator fills (DIVASTRO-143).

This file is the ONLY place the pa text of the shared tables is edited; app/lang_data merges it
into them at import time, as if it were written in app/seo_text.py and friends.

  python -m app.lang_data check pa      what is left, per table (exit 0 = complete)
  python -m app.lang_data skeleton pa --force   regenerate (DISCARDS your edits)

Rules: every key below stays; a value "" means "not translated yet" (English shows, the
checker complains). Keep every {placeholder} the comment lists under `keep:`; the word order
is yours. HTML values keep their tags (write &amp; for &). Astrology names (tithi, nakshatra,
rashi, graha ...) are not here: they are in app/astro/names_pa.py. Digits are ASCII, as in
the other languages. Full instructions: docs/lang-agent-brief.md.

Set READY when a whole page module is complete, and only then — an unfinished module in READY
fails `check` and CI. A module that is not READY renders the English body, noindex.
"""

from __future__ import annotations

# Page modules that are complete for this language (the table groups below):
#   "seo" "rashifal" "vrat" "nakshatra" "muhurat" "recurring" "hub" "app"
READY = frozenset({"seo", "app", "rashifal", "hub"})

# Latin-script words the pa text may keep besides the defaults (WhatsApp, UPI, PDF ...).
ALLOW_LATIN = frozenset({"name", "gmail.com"})  # the e-mail placeholder name@gmail.com

# static/i18n/pa.json keys whose value is deliberately the English word (brand names, "OK").
KEEP_ENGLISH = frozenset({"acct.emailPlaceholder"})  # an example e-mail address, not a sentence

# Namakshar syllables are Devanagari in the engine; this maps a letter to this script:
# (Unicode block start, {Devanagari letter: this script's letter where the offset is wrong}).
# Already set — `check` verifies all 108 syllables come out in the pa script.
AKSHAR = (0x0A00, {'ष': 'ਸ਼'})


# ----------------------------------------------------------------------------
# seo       /panchang /rahu-kaal /choghadiya /kundali-milan /free-kundali + shared chrome, cities
# ----------------------------------------------------------------------------

# app/seo_text.py TEXT["pa"] — page text of /panchang /rahu-kaal /choghadiya /kundali-milan /free-kundali  [134]
SEO_TEXT = {
    # EN: Panchang
    "tool.panchang": "ਪੰਚਾਂਗ",
    # EN: Rahu Kaal
    "tool.rahu-kaal": "ਰਾਹੂ ਕਾਲ",
    # EN: Choghadiya
    "tool.choghadiya": "ਚੌਘੜੀਆ",
    # EN: {vara}, {date} · {place} · IST
    # keep: {date} {place} {vara}
    "when": "{vara}, {date} · {place} · IST",
    # EN: {name} until {time}
    # keep: {name} {time}
    "limb.until": "{name} {time} ਤੱਕ",
    # EN: then {name}
    # keep: {name}
    "limb.then": "ਫਿਰ {name}",
    # EN: pada
    "limb.pada": "ਚਰਣ",
    # EN: {paksha} paksha
    # keep: {paksha}
    "paksha.full": "{paksha} ਪੱਖ",
    # EN: {tool} in other cities
    # keep: {tool}
    "cities.heading": "ਹੋਰ ਸ਼ਹਿਰਾਂ ਵਿੱਚ {tool}",
    # EN: More free tools
    "links.heading": "ਹੋਰ ਮੁਫ਼ਤ ਟੂਲ",
    # EN: {tool} in {city}
    # keep: {city} {tool}
    "links.tool_in_city": "{city} ਵਿੱਚ {tool}",
    # EN: Kundali Milan (36 guna)
    "links.milan": "ਕੁੰਡਲੀ ਮਿਲਾਨ (36 ਗੁਣ)",
    # EN: Free Janam Kundali
    "links.kundali": "ਮੁਫ਼ਤ ਜਨਮ ਕੁੰਡਲੀ",
    # EN: Muhurat Finder
    "links.muhurat": "ਮਹੂਰਤ ਖੋਜੋ",
    # EN: Today's Rashifal
    "links.rashifal": "ਅੱਜ ਦਾ ਰਾਸ਼ੀਫਲ",
    # EN: Today's Vrat & Festivals in {city}
    # keep: {city}
    "links.vrat": "{city} ਵਿੱਚ ਅੱਜ ਦੇ ਵਰਤ ਅਤੇ ਤਿਉਹਾਰ",
    # EN: City not found — {brand}
    # keep: {brand}
    "nf.title": "ਸ਼ਹਿਰ ਨਹੀਂ ਮਿਲਿਆ — {brand}",
    # EN: {tool} city not found.
    # keep: {tool}
    "nf.desc": "{tool} ਲਈ ਇਹ ਸ਼ਹਿਰ ਨਹੀਂ ਮਿਲਿਆ।",
    # EN: <h1>{tool}: city not found</h1><p>We don't have a page for “{slug}” yet. Pick a city
    #     below, or <a href="{app}">open the {tool} tool</a> to use any place in the world.</p>
    # keep: {app} {slug} {tool}
    "nf.body": "<h1>{tool}: ਸ਼ਹਿਰ ਨਹੀਂ ਮਿਲਿਆ</h1><p>“{slug}” ਲਈ ਸਾਡੇ ਕੋਲ ਹਾਲੇ ਕੋਈ ਪੰਨਾ ਨਹੀਂ ਹੈ। ਹੇਠਾਂ ਤੋਂ ਕੋਈ ਸ਼ਹਿਰ ਚੁਣੋ, ਜਾਂ ਦੁਨੀਆ ਦੀ ਕੋਈ ਵੀ ਥਾਂ ਵਰਤਣ ਲਈ <a href=\"{app}\">{tool} ਟੂਲ ਖੋਲ੍ਹੋ</a>।</p>",
    # EN: Today's Panchang in {city}, {date} — Tithi, Nakshatra, Rahu Kaal | {brand}
    # keep: {brand} {city} {date}
    "p.title": "{city} ਵਿੱਚ ਅੱਜ ਦਾ ਪੰਚਾਂਗ, {date} — ਤਿਥੀ, ਨਕਸ਼ਤਰ, ਰਾਹੂ ਕਾਲ | {brand}",
    # EN: Aaj ka Panchang for {city} on {vara}, {date}: {tithi} tithi ({paksha} paksha), {nakshatra}
    #     nakshatra, sunrise {sunrise}, Rahu Kaal {rahu}. Computed with Swiss Ephemeris.
    # keep: {city} {date} {nakshatra} {rahu} {sunrise} {tithi} {vara}
    # may also use: {paksha_full} {paksha}
    "p.desc": "{city} ਦਾ ਅੱਜ ਦਾ ਪੰਚਾਂਗ, {vara}, {date}: {paksha} ਪੱਖ ਦੀ {tithi} ਤਿਥੀ, {nakshatra} ਨਕਸ਼ਤਰ, ਸੂਰਜ ਚੜ੍ਹਨ ਦਾ ਸਮਾਂ {sunrise}, ਰਾਹੂ ਕਾਲ {rahu}। ਸਵਿਸ ਐਫ਼ੇਮੇਰਿਸ ਨਾਲ ਸਹੀ ਗਣਨਾ।",
    # EN: <h1>Today's Panchang in {city}</h1>
    # keep: {city}
    "p.h1": "<h1>{city} ਵਿੱਚ ਅੱਜ ਦਾ ਪੰਚਾਂਗ</h1>",
    # EN: <p class="hi" lang="hi">आज का पंचांग — {city_hi}</p>
    # keep: {city}
    "p.sub": "<p class=\"hi\">ਤਿਥੀ, ਨਕਸ਼ਤਰ, ਯੋਗ, ਕਰਣ ਅਤੇ ਰਾਹੂ ਕਾਲ — {city}</p>",
    # EN: <div class="box"><p>Today in {city} is <strong>{paksha} {tithi}</strong> with the Moon in
    #     <strong>{nakshatra}</strong> nakshatra. Rahu Kaal runs <strong>{rahu}</strong> — avoid
    #     starting anything new in that window.</p></div>
    # keep: {city} {nakshatra} {rahu} {tithi}
    # may also use: {paksha_full} {paksha}
    "p.box": "<div class=\"box\"><p>ਅੱਜ {city} ਵਿੱਚ <strong>{paksha} {tithi}</strong> ਹੈ ਅਤੇ ਚੰਦਰਮਾ <strong>{nakshatra}</strong> ਨਕਸ਼ਤਰ ਵਿੱਚ ਹੈ। ਰਾਹੂ ਕਾਲ <strong>{rahu}</strong> ਹੈ — ਇਸ ਸਮੇਂ ਕੋਈ ਨਵਾਂ ਕੰਮ ਸ਼ੁਰੂ ਨਾ ਕਰੋ।</p></div>",
    # EN: Vaar (weekday)
    "p.r_vara": "ਵਾਰ (ਦਿਨ)",
    # EN: Tithi
    "p.r_tithi": "ਤਿਥੀ",
    # EN: Paksha
    "p.r_paksha": "ਪੱਖ",
    # EN: Nakshatra
    "p.r_nakshatra": "ਨਕਸ਼ਤਰ",
    # EN: Yoga
    "p.r_yoga": "ਯੋਗ",
    # EN: Karana
    "p.r_karana": "ਕਰਣ",
    # EN: Sunrise
    "p.r_sunrise": "ਸੂਰਜ ਚੜ੍ਹਨ ਦਾ ਸਮਾਂ",
    # EN: Sunset
    "p.r_sunset": "ਸੂਰਜ ਛਿਪਣ ਦਾ ਸਮਾਂ",
    # EN: Moonrise
    "p.r_moonrise": "ਚੰਦਰਮਾ ਚੜ੍ਹਨ ਦਾ ਸਮਾਂ",
    # EN: Moonset
    "p.r_moonset": "ਚੰਦਰਮਾ ਛਿਪਣ ਦਾ ਸਮਾਂ",
    # EN: Moon sign
    "p.r_moon_sign": "ਚੰਦਰ ਰਾਸ਼ੀ",
    # EN: Rahu Kaal
    "p.r_rahu": "ਰਾਹੂ ਕਾਲ",
    # EN: Yamaganda
    "p.r_yama": "ਯਮਗੰਡ",
    # EN: Gulika Kaal
    "p.r_gulika": "ਗੁਲਿਕ ਕਾਲ",
    # EN: Abhijit Muhurat
    "p.r_abhijit": "ਅਭਿਜੀਤ ਮਹੂਰਤ",
    # EN: {vara_en} — {weekday} <span lang="hi">({vara_hi})</span>
    # keep: {vara}
    "p.v_vara": "{vara}",
    # EN: {paksha_en} <span lang="hi">({paksha_hi_full})</span>
    # keep: {paksha_full}
    "p.v_paksha": "{paksha_full}",
    # EN: No moonrise this day
    "p.no_moonrise": "ਇਸ ਦਿਨ ਚੰਦਰਮਾ ਨਹੀਂ ਚੜ੍ਹਦਾ",
    # EN: No moonset this day
    "p.no_moonset": "ਇਸ ਦਿਨ ਚੰਦਰਮਾ ਨਹੀਂ ਛਿਪਦਾ",
    # EN: Not observed on Wednesday (Budhavara)
    "p.no_abhijit": "ਬੁੱਧਵਾਰ ਨੂੰ ਨਹੀਂ ਮੰਨਿਆ ਜਾਂਦਾ",
    # EN: <p>Times are for {place} ({lat}°N, {lon}°E) in Indian Standard Time. The panchang day runs
    #     from sunrise to the next sunrise, so a tithi or nakshatra may end after midnight. Sunrise
    #     is the visible upper limb with refraction, as printed in Indian almanacs; nakshatra and
    #     yoga use the Lahiri ayanamsa.</p>
    # keep: {lat} {lon}
    # may also use: {city} {place}
    "p.note": "<p>ਸਮੇਂ {place} ({lat}° ਉੱਤਰ, {lon}° ਪੂਰਬ) ਲਈ ਭਾਰਤੀ ਮਿਆਰੀ ਸਮੇਂ ਵਿੱਚ ਹਨ। ਪੰਚਾਂਗ ਦਾ ਦਿਨ ਇੱਕ ਸੂਰਜ ਚੜ੍ਹਨ ਤੋਂ ਅਗਲੇ ਸੂਰਜ ਚੜ੍ਹਨ ਤੱਕ ਚੱਲਦਾ ਹੈ, ਇਸ ਲਈ ਕੋਈ ਤਿਥੀ ਜਾਂ ਨਕਸ਼ਤਰ ਅੱਧੀ ਰਾਤ ਤੋਂ ਬਾਅਦ ਵੀ ਖ਼ਤਮ ਹੋ ਸਕਦਾ ਹੈ। ਸੂਰਜ ਚੜ੍ਹਨਾ ਭਾਰਤੀ ਪੰਚਾਂਗਾਂ ਵਾਂਗ ਸੂਰਜ ਦੇ ਉੱਪਰਲੇ ਕਿਨਾਰੇ ਦੇ ਦਿਸਣ (ਵਾਯੂਮੰਡਲੀ ਵਿਵਰਤਨ ਸਮੇਤ) ਦੇ ਪਲ ਨੂੰ ਮੰਨਿਆ ਗਿਆ ਹੈ; ਨਕਸ਼ਤਰ ਅਤੇ ਯੋਗ ਲਾਹਿੜੀ ਅਯਨਾਂਸ਼ ਨਾਲ ਗਿਣੇ ਗਏ ਹਨ।</p>",
    # EN: Open the full Panchang — any city, any date
    "p.cta": "ਪੂਰਾ ਪੰਚਾਂਗ ਖੋਲ੍ਹੋ — ਕੋਈ ਵੀ ਸ਼ਹਿਰ, ਕੋਈ ਵੀ ਤਾਰੀਖ਼",
    # EN: <h2>The five limbs of the Panchang</h2> <p><strong>Tithi</strong> is the lunar day — each
    #     12° the Moon gains on the Sun. <strong>Nakshatra</strong> is the Moon's lunar mansion, one
    #     of 27. <strong>Yoga</strong> comes from the combined longitudes of Sun and Moon, and
    #     <strong>Karana</strong> is half a tithi. <strong>Vaar</strong> is the weekday, reckoned
    #     from sunrise. Together they are the <span lang="hi">पंचांग</span> (“five limbs”) consulted
    #     before any auspicious work.</p>
    "p.limbs": "<h2>ਪੰਚਾਂਗ ਦੇ ਪੰਜ ਅੰਗ</h2><p><strong>ਤਿਥੀ</strong> ਚੰਦਰ ਦਿਨ ਹੈ — ਚੰਦਰਮਾ ਜਦੋਂ ਸੂਰਜ ਤੋਂ 12° ਅੱਗੇ ਵਧ ਜਾਂਦਾ ਹੈ। <strong>ਨਕਸ਼ਤਰ</strong> ਚੰਦਰਮਾ ਦਾ ਟਿਕਾਣਾ ਹੈ, ਕੁੱਲ 27 ਵਿੱਚੋਂ ਇੱਕ। <strong>ਯੋਗ</strong> ਸੂਰਜ ਅਤੇ ਚੰਦਰਮਾ ਦੇ ਮਿਲੇ ਹੋਏ ਅੰਸ਼ਾਂ ਤੋਂ ਬਣਦਾ ਹੈ, ਅਤੇ <strong>ਕਰਣ</strong> ਤਿਥੀ ਦਾ ਅੱਧਾ ਹਿੱਸਾ ਹੁੰਦਾ ਹੈ। <strong>ਵਾਰ</strong> ਹਫ਼ਤੇ ਦਾ ਦਿਨ ਹੈ, ਜੋ ਸੂਰਜ ਚੜ੍ਹਨ ਤੋਂ ਗਿਣਿਆ ਜਾਂਦਾ ਹੈ। ਇਹ ਸਾਰੇ ਮਿਲ ਕੇ ਪੰਚਾਂਗ (“ਪੰਜ ਅੰਗ”) ਬਣਾਉਂਦੇ ਹਨ, ਜੋ ਹਰ ਸ਼ੁਭ ਕੰਮ ਤੋਂ ਪਹਿਲਾਂ ਵੇਖਿਆ ਜਾਂਦਾ ਹੈ।</p>",
    # EN: Rahu Kaal Today in {city} — {rahu}, {date} | {brand}
    # keep: {brand} {city} {rahu}
    # may also use: {date}
    "rk.title": "{city} ਵਿੱਚ ਅੱਜ ਦਾ ਰਾਹੂ ਕਾਲ — {rahu}, {date} | {brand}",
    # EN: Rahu Kaal today in {city} ({vara}, {date}) is {rahu}. Also Yamaganda {yama} and Gulika
    #     {gulika}, with this week's timings and what Rahu Kaal means.
    # keep: {city} {date} {gulika} {rahu} {vara} {yama}
    "rk.desc": "{city} ਵਿੱਚ ਅੱਜ ({vara}, {date}) ਦਾ ਰਾਹੂ ਕਾਲ {rahu} ਹੈ। ਨਾਲ ਯਮਗੰਡ {yama} ਅਤੇ ਗੁਲਿਕ {gulika}, ਇਸ ਹਫ਼ਤੇ ਦੇ ਸਮੇਂ ਅਤੇ ਰਾਹੂ ਕਾਲ ਦਾ ਮਤਲਬ।",
    # EN: <h1>Rahu Kaal Today in {city}</h1>
    # keep: {city}
    "rk.h1": "<h1>{city} ਵਿੱਚ ਅੱਜ ਦਾ ਰਾਹੂ ਕਾਲ</h1>",
    # EN: <p class="hi" lang="hi">आज का राहु काल — {city_hi}</p>
    # keep: {city}
    "rk.sub": "<p class=\"hi\">ਅੱਜ ਰਾਹੂ ਕਾਲ, ਯਮਗੰਡ ਅਤੇ ਗੁਲਿਕ ਕਾਲ ਕਦੋਂ ਹੈ — {city}</p>",
    # EN: Rahu Kaal <span lang="hi">(राहु काल)</span>
    "rk.r_rahu": "ਰਾਹੂ ਕਾਲ",
    # EN: Yamaganda <span lang="hi">(यमगण्ड)</span>
    "rk.r_yama": "ਯਮਗੰਡ",
    # EN: Gulika Kaal <span lang="hi">(गुलिक काल)</span>
    "rk.r_gulika": "ਗੁਲਿਕ ਕਾਲ",
    # EN: Abhijit Muhurat
    "rk.r_abhijit": "ਅਭਿਜੀਤ ਮਹੂਰਤ",
    # EN: Sunrise / Sunset
    "rk.r_sun": "ਸੂਰਜ ਚੜ੍ਹਨਾ / ਛਿਪਣਾ",
    # EN: Not observed on Wednesday
    "rk.no_abhijit": "ਬੁੱਧਵਾਰ ਨੂੰ ਨਹੀਂ ਮੰਨਿਆ ਜਾਂਦਾ",
    # EN: Check Rahu Kaal for any city or date
    "rk.cta": "ਕਿਸੇ ਵੀ ਸ਼ਹਿਰ ਜਾਂ ਤਾਰੀਖ਼ ਦਾ ਰਾਹੂ ਕਾਲ ਵੇਖੋ",
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
    "rk.about": "<h2>ਰਾਹੂ ਕਾਲ ਕੀ ਹੁੰਦਾ ਹੈ?</h2><p>ਰਾਹੂ ਕਾਲ ਹਰ ਰੋਜ਼ ਲਗਭਗ ਡੇਢ ਘੰਟੇ ਦਾ ਉਹ ਸਮਾਂ ਹੁੰਦਾ ਹੈ ਜਿਸ ਨੂੰ ਪਰੰਪਰਾ ਅਨੁਸਾਰ ਉੱਤਰੀ ਚੰਦਰ ਬਿੰਦੂ ਰਾਹੂ ਦੇ ਅਧੀਨ ਮੰਨਿਆ ਜਾਂਦਾ ਹੈ। ਦਿਨ ਦੀ ਰੌਸ਼ਨੀ — ਸੂਰਜ ਚੜ੍ਹਨ ਤੋਂ ਛਿਪਣ ਤੱਕ — ਨੂੰ ਅੱਠ ਬਰਾਬਰ ਹਿੱਸਿਆਂ ਵਿੱਚ ਵੰਡਿਆ ਜਾਂਦਾ ਹੈ ਅਤੇ ਉਨ੍ਹਾਂ ਵਿੱਚੋਂ ਇੱਕ ਹਿੱਸਾ ਰਾਹੂ ਦਾ ਹੁੰਦਾ ਹੈ। ਕਿਹੜਾ ਹਿੱਸਾ, ਇਹ ਵਾਰ ਉੱਤੇ ਨਿਰਭਰ ਹੈ: ਐਤਵਾਰ ਨੂੰ ਅੱਠਵਾਂ, ਸੋਮਵਾਰ ਨੂੰ ਦੂਜਾ, ਮੰਗਲਵਾਰ ਨੂੰ ਸੱਤਵਾਂ, ਬੁੱਧਵਾਰ ਨੂੰ ਪੰਜਵਾਂ, ਵੀਰਵਾਰ ਨੂੰ ਛੇਵਾਂ, ਸ਼ੁੱਕਰਵਾਰ ਨੂੰ ਚੌਥਾ ਅਤੇ ਸ਼ਨਿੱਚਰਵਾਰ ਨੂੰ ਤੀਜਾ।</p><p>ਇਹ ਅਸਲੀ ਸੂਰਜ ਚੜ੍ਹਨ ਤੇ ਛਿਪਣ ਦੇ ਸਮੇਂ ਮੁਤਾਬਕ ਚੱਲਦਾ ਹੈ, ਇਸ ਲਈ ਹਰ ਸ਼ਹਿਰ ਵਿੱਚ ਵੱਖਰਾ ਹੁੰਦਾ ਹੈ ਅਤੇ ਸਾਲ ਭਰ ਖਿਸਕਦਾ ਰਹਿੰਦਾ ਹੈ — ਇਸੇ ਕਰਕੇ “ਸੋਮਵਾਰ 7:30–9:00” ਵਾਲੀ ਪੱਕੀ ਸਾਰਣੀ ਸਿਰਫ਼ ਮੋਟਾ ਅੰਦਾਜ਼ਾ ਹੈ। ਰੀਤ ਅਨੁਸਾਰ ਲੋਕ ਰਾਹੂ ਕਾਲ ਵਿੱਚ ਨਵਾਂ ਕੰਮ ਸ਼ੁਰੂ ਕਰਨ, ਸਮਝੌਤਿਆਂ ’ਤੇ ਦਸਤਖ਼ਤ ਕਰਨ, ਸਫ਼ਰ ’ਤੇ ਨਿਕਲਣ ਜਾਂ ਵੱਡੀ ਖ਼ਰੀਦਦਾਰੀ ਕਰਨ ਤੋਂ ਬਚਦੇ ਹਨ; ਪਹਿਲਾਂ ਤੋਂ ਚੱਲ ਰਿਹਾ ਕੰਮ ਜਾਰੀ ਰੱਖਿਆ ਜਾ ਸਕਦਾ ਹੈ। ਯਮਗੰਡ ਅਤੇ ਗੁਲਿਕ ਕਾਲ ਦਿਨ ਦੇ ਦੋ ਹੋਰ ਅੱਠਵੇਂ ਹਿੱਸੇ ਹਨ, ਜਿਨ੍ਹਾਂ ਬਾਰੇ ਵੀ ਇਸੇ ਤਰ੍ਹਾਂ ਸਾਵਧਾਨੀ ਵਰਤੀ ਜਾਂਦੀ ਹੈ।</p>",
    # EN: <h2>Rahu Kaal in {city} this week</h2>
    # keep: {city}
    "rk.week_h2": "<h2>ਇਸ ਹਫ਼ਤੇ {city} ਵਿੱਚ ਰਾਹੂ ਕਾਲ</h2>",
    # EN: Day
    "rk.th_day": "ਦਿਨ",
    # EN: Rahu Kaal
    "rk.th_rahu": "ਰਾਹੂ ਕਾਲ",
    # EN: Yamaganda
    "rk.th_yama": "ਯਮਗੰਡ",
    # EN: Gulika
    "rk.th_gulika": "ਗੁਲਿਕ",
    # EN: Choghadiya Today in {city}, {date} — Day & Night Timings | {brand}
    # keep: {brand} {city} {date}
    "ch.title": "{city} ਵਿੱਚ ਅੱਜ ਦਾ ਚੌਘੜੀਆ, {date} — ਦਿਨ ਅਤੇ ਰਾਤ ਦੇ ਸਮੇਂ | {brand}",
    # EN: Today's choghadiya for {city} ({vara}, {date}): all 16 day and night muhurtas — Amrit,
    #     Shubh, Labh, Char, Rog, Kaal, Udveg — with exact start and end times from sunrise
    #     {sunrise}.
    # keep: {city} {date} {sunrise} {vara}
    "ch.desc": "{city} ਲਈ ਅੱਜ ਦਾ ਚੌਘੜੀਆ ({vara}, {date}): ਦਿਨ ਅਤੇ ਰਾਤ ਦੇ ਸਾਰੇ 16 ਮਹੂਰਤ — ਅੰਮ੍ਰਿਤ, ਸ਼ੁਭ, ਲਾਭ, ਚਰ, ਰੋਗ, ਕਾਲ, ਉਦਵੇਗ — ਸੂਰਜ ਚੜ੍ਹਨ {sunrise} ਤੋਂ ਸ਼ੁਰੂ ਹੋ ਕੇ ਸਹੀ ਸ਼ੁਰੂ ਤੇ ਅੰਤ ਦੇ ਸਮਿਆਂ ਸਮੇਤ।",
    # EN: <h1>Choghadiya Today in {city}</h1>
    # keep: {city}
    "ch.h1": "<h1>{city} ਵਿੱਚ ਅੱਜ ਦਾ ਚੌਘੜੀਆ</h1>",
    # EN: <p class="hi" lang="hi">आज का चौघड़िया — {city_hi}</p>
    # keep: {city}
    "ch.sub": "<p class=\"hi\">ਅੱਜ ਦੇ ਦਿਨ ਅਤੇ ਰਾਤ ਦੇ ਚੌਘੜੀਆ ਮਹੂਰਤ — {city}</p>",
    # EN: {name} from {time}
    # keep: {name} {time}
    "ch.first_good": "{name} {time} ਤੋਂ",
    # EN: none
    "ch.none": "ਕੋਈ ਨਹੀਂ",
    # EN: <div class="box"><p>Sunrise <strong>{sunrise}</strong>, sunset <strong>{sunset}</strong>.
    #     First auspicious daytime choghadiya: <strong>{first_good}</strong>.</p></div>
    # keep: {first_good} {sunrise} {sunset}
    "ch.box": "<div class=\"box\"><p>ਸੂਰਜ ਚੜ੍ਹਨ ਦਾ ਸਮਾਂ <strong>{sunrise}</strong>, ਸੂਰਜ ਛਿਪਣ ਦਾ ਸਮਾਂ <strong>{sunset}</strong>। ਦਿਨ ਦਾ ਪਹਿਲਾ ਸ਼ੁਭ ਚੌਘੜੀਆ: <strong>{first_good}</strong>।</p></div>",
    # EN: <h2>Day Choghadiya <span lang="hi">(दिन का चौघड़िया)</span></h2>
    "ch.day_h2": "<h2>ਦਿਨ ਦਾ ਚੌਘੜੀਆ</h2>",
    # EN: <h2>Night Choghadiya <span lang="hi">(रात का चौघड़िया)</span></h2>
    "ch.night_h2": "<h2>ਰਾਤ ਦਾ ਚੌਘੜੀਆ</h2>",
    # EN: <tr><th>Time</th><th>Choghadiya</th><th>Nature</th></tr>
    "ch.th": "<tr><th>ਸਮਾਂ</th><th>ਚੌਘੜੀਆ</th><th>ਸੁਭਾਅ</th></tr>",
    # EN: <tr><td>{when}</td><td class="{cls}"><strong>{name}</strong> <span lang="hi">({name_hi})</
    #     span><small>{ruler}</small></td><td>{quality}<small>{desc}</small></td></tr>
    # keep: {cls} {desc} {name} {quality} {ruler} {when}
    "ch.row": "<tr><td>{when}</td><td class=\"{cls}\"><strong>{name}</strong><small>{ruler}</small></td><td>{quality}<small>{desc}</small></td></tr>",
    # EN: Open the live Choghadiya clock
    "ch.cta": "ਲਾਈਵ ਚੌਘੜੀਆ ਘੜੀ ਖੋਲ੍ਹੋ",
    # EN: <h2>How choghadiya works</h2> <p>The day from sunrise to sunset, and the night from sunset
    #     to the next sunrise, are each divided into eight equal parts called choghadiya (<span
    #     lang="hi">चौघड़िया</span>, “four ghadis”). Each is ruled by a planet and named for its
    #     nature: <strong>Amrit</strong>, <strong>Shubh</strong> and <strong>Labh</strong> are
    #     auspicious, <strong>Char</strong> is neutral and good for travel, while
    #     <strong>Rog</strong>, <strong>Kaal</strong> and <strong>Udveg</strong> are avoided for new
    #     beginnings. The order starts from the weekday's ruler, so it changes every day — and the
    #     length of each slot follows the real day length in {city}.</p>
    # keep: {city}
    "ch.about": "<h2>ਚੌਘੜੀਆ ਕਿਵੇਂ ਕੰਮ ਕਰਦਾ ਹੈ</h2><p>ਸੂਰਜ ਚੜ੍ਹਨ ਤੋਂ ਛਿਪਣ ਤੱਕ ਦਾ ਦਿਨ ਅਤੇ ਸੂਰਜ ਛਿਪਣ ਤੋਂ ਅਗਲੇ ਸੂਰਜ ਚੜ੍ਹਨ ਤੱਕ ਦੀ ਰਾਤ, ਦੋਵੇਂ ਅੱਠ-ਅੱਠ ਬਰਾਬਰ ਹਿੱਸਿਆਂ ਵਿੱਚ ਵੰਡੇ ਜਾਂਦੇ ਹਨ, ਜਿਨ੍ਹਾਂ ਨੂੰ ਚੌਘੜੀਆ (“ਚਾਰ ਘੜੀਆਂ”) ਕਿਹਾ ਜਾਂਦਾ ਹੈ। ਹਰ ਇੱਕ ਦਾ ਇੱਕ ਗ੍ਰਹਿ ਸੁਆਮੀ ਹੁੰਦਾ ਹੈ ਅਤੇ ਉਸ ਦਾ ਨਾਂ ਉਸ ਦੇ ਸੁਭਾਅ ਮੁਤਾਬਕ ਹੈ: <strong>ਅੰਮ੍ਰਿਤ</strong>, <strong>ਸ਼ੁਭ</strong> ਅਤੇ <strong>ਲਾਭ</strong> ਸ਼ੁਭ ਹਨ, <strong>ਚਰ</strong> ਮੱਧਮ ਹੈ ਅਤੇ ਸਫ਼ਰ ਲਈ ਚੰਗਾ ਹੈ, ਜਦਕਿ <strong>ਰੋਗ</strong>, <strong>ਕਾਲ</strong> ਅਤੇ <strong>ਉਦਵੇਗ</strong> ਨਵੀਂ ਸ਼ੁਰੂਆਤ ਲਈ ਛੱਡ ਦਿੱਤੇ ਜਾਂਦੇ ਹਨ। ਕ੍ਰਮ ਉਸ ਦਿਨ ਦੇ ਸੁਆਮੀ ਤੋਂ ਸ਼ੁਰੂ ਹੁੰਦਾ ਹੈ, ਇਸ ਲਈ ਹਰ ਰੋਜ਼ ਬਦਲਦਾ ਹੈ — ਅਤੇ ਹਰ ਹਿੱਸੇ ਦੀ ਲੰਬਾਈ {city} ਵਿੱਚ ਦਿਨ ਦੀ ਅਸਲੀ ਲੰਬਾਈ ਮੁਤਾਬਕ ਹੁੰਦੀ ਹੈ।</p>",
    # EN: Kundali Milan — Ashtakoot Guna Milan ({total} Gun) Explained | {brand}
    # keep: {brand} {total}
    "km.title": "ਕੁੰਡਲੀ ਮਿਲਾਨ — ਅਸ਼ਟਕੂਟ ਗੁਣ ਮਿਲਾਨ ({total} ਗੁਣ) ਦੀ ਵਿਆਖਿਆ | {brand}",
    # EN: How Kundali Milan works: the 8 kootas of Ashtakoot Guna Milan, {total} points, what score
    #     is good for marriage, and how Mangal Dosha is checked. Free online matching in English and
    #     Hindi.
    # keep: {total}
    "km.desc": "ਕੁੰਡਲੀ ਮਿਲਾਨ ਕਿਵੇਂ ਹੁੰਦਾ ਹੈ: ਅਸ਼ਟਕੂਟ ਗੁਣ ਮਿਲਾਨ ਦੇ 8 ਕੂਟ, {total} ਅੰਕ, ਵਿਆਹ ਲਈ ਕਿੰਨੇ ਅੰਕ ਚੰਗੇ ਹਨ, ਅਤੇ ਮੰਗਲ ਦੋਸ਼ ਦੀ ਜਾਂਚ ਕਿਵੇਂ ਹੁੰਦੀ ਹੈ। ਅੰਗਰੇਜ਼ੀ ਅਤੇ ਹਿੰਦੀ ਵਿੱਚ ਮੁਫ਼ਤ ਆਨਲਾਈਨ ਮਿਲਾਨ।",
    # EN: Kundali Milan
    "km.crumb": "ਕੁੰਡਲੀ ਮਿਲਾਨ",
    # EN: <h1>Kundali Milan: Ashtakoot Guna Milan explained</h1> <p class="hi" lang="hi">कुंडली
    #     मिलान — अष्टकूट गुण मिलान ({total} गुण)</p> <p>Kundali Milan (<span lang="hi">कुंडली
    #     मिलान</span>) is the traditional Vedic way of checking marriage compatibility. The most
    #     widely used method in North India is <strong>Ashtakoot Guna Milan</strong>: eight factors
    #     (<em>kootas</em>) are compared between the bride's and groom's charts and scored out of
    #     <strong>{total} points (gunas)</strong>. Every one of them is read from the
    #     <strong>Moon</strong> — its sign (rashi) and its nakshatra at birth — which is why the
    #     score needs an accurate birth date and place, but barely depends on the birth time.</p>
    # keep: {total}
    "km.intro": "<h1>ਕੁੰਡਲੀ ਮਿਲਾਨ: ਅਸ਼ਟਕੂਟ ਗੁਣ ਮਿਲਾਨ ਦੀ ਵਿਆਖਿਆ</h1><p class=\"hi\">ਕੁੰਡਲੀ ਮਿਲਾਨ — ਅਸ਼ਟਕੂਟ ਗੁਣ ਮਿਲਾਨ ({total} ਗੁਣ)</p><p>ਕੁੰਡਲੀ ਮਿਲਾਨ ਵਿਆਹ ਦੇ ਮੇਲ ਦੀ ਜਾਂਚ ਕਰਨ ਦਾ ਰਵਾਇਤੀ ਵੈਦਿਕ ਤਰੀਕਾ ਹੈ। ਉੱਤਰੀ ਭਾਰਤ ਵਿੱਚ ਸਭ ਤੋਂ ਵੱਧ ਵਰਤਿਆ ਜਾਂਦਾ ਤਰੀਕਾ <strong>ਅਸ਼ਟਕੂਟ ਗੁਣ ਮਿਲਾਨ</strong> ਹੈ: ਲਾੜੀ ਤੇ ਲਾੜੇ ਦੀਆਂ ਕੁੰਡਲੀਆਂ ਦੇ ਅੱਠ ਪੱਖਾਂ (<em>ਕੂਟ</em>) ਦੀ ਤੁਲਨਾ ਕੀਤੀ ਜਾਂਦੀ ਹੈ ਅਤੇ ਕੁੱਲ <strong>{total} ਅੰਕਾਂ (ਗੁਣਾਂ)</strong> ਵਿੱਚੋਂ ਅੰਕ ਦਿੱਤੇ ਜਾਂਦੇ ਹਨ। ਇਹ ਸਾਰੇ <strong>ਚੰਦਰਮਾ</strong> ਤੋਂ ਪੜ੍ਹੇ ਜਾਂਦੇ ਹਨ — ਜਨਮ ਵੇਲੇ ਉਸ ਦੀ ਰਾਸ਼ੀ ਅਤੇ ਨਕਸ਼ਤਰ ਤੋਂ — ਇਸੇ ਲਈ ਅੰਕਾਂ ਵਾਸਤੇ ਜਨਮ ਦੀ ਸਹੀ ਤਾਰੀਖ਼ ਅਤੇ ਥਾਂ ਚਾਹੀਦੀ ਹੈ, ਪਰ ਜਨਮ ਦੇ ਸਮੇਂ ’ਤੇ ਇਹ ਮੁਸ਼ਕਿਲ ਨਾਲ ਹੀ ਨਿਰਭਰ ਕਰਦੇ ਹਨ।</p>",
    # EN: Match two kundalis now — free
    "km.cta1": "ਹੁਣੇ ਦੋ ਕੁੰਡਲੀਆਂ ਮਿਲਾਓ — ਮੁਫ਼ਤ",
    # EN: <p>Don't know the birth times? Try <a href="{href}">Naam se Kundali Milan</a> — the
    #     traditional match by the first letter of each name.</p>
    # keep: {href}
    "km.naam": "<p>ਜਨਮ ਦਾ ਸਮਾਂ ਨਹੀਂ ਪਤਾ? <a href=\"{href}\">ਨਾਂ ਤੋਂ ਕੁੰਡਲੀ ਮਿਲਾਨ</a> ਅਜ਼ਮਾਓ — ਹਰ ਨਾਂ ਦੇ ਪਹਿਲੇ ਅੱਖਰ ਤੋਂ ਹੋਣ ਵਾਲਾ ਰਵਾਇਤੀ ਮਿਲਾਨ।</p>",
    # EN: <h2>The 8 kootas and their points</h2>
    "km.kootas_h2": "<h2>8 ਕੂਟ ਅਤੇ ਉਨ੍ਹਾਂ ਦੇ ਅੰਕ</h2>",
    # EN: <tr><th>Koota</th><th>Points</th><th>What it measures</th></tr>
    "km.th": "<tr><th>ਕੂਟ</th><th>ਅੰਕ</th><th>ਕੀ ਮਾਪਦਾ ਹੈ</th></tr>",
    # EN: <tr><td><strong>{name}</strong> <span
    #     lang="hi">({name_hi})</span></td><td>{pts}</td><td>{text}</td></tr>
    # keep: {name} {pts} {text}
    "km.row": "<tr><td><strong>{name}</strong></td><td>{pts}</td><td>{text}</td></tr>",
    # EN: Total
    "km.total": "ਕੁੱਲ",
    # EN: <h2>What is a good Guna Milan score?</h2>
    "km.score_h2": "<h2>ਗੁਣ ਮਿਲਾਨ ਦਾ ਚੰਗਾ ਅੰਕ ਕਿੰਨਾ ਹੁੰਦਾ ਹੈ?</h2>",
    # EN: <tr><th>Gunas</th><th>Conventional reading</th></tr>
    "km.score_th": "<tr><th>ਗੁਣ</th><th>ਰਵਾਇਤੀ ਮਤਲਬ</th></tr>",
    # EN: Below {n}
    # keep: {n}
    "km.below": "{n} ਤੋਂ ਘੱਟ",
    # EN: <p>18 is the conventional minimum. The total alone is not the whole story: a high score
    #     with an uncancelled Nadi or Bhakoot dosha is read with caution, and a modest score with
    #     strong Graha Maitri and no doshas is often considered workable. These bands are a
    #     convention with a long history, not a measurement — they are guidance, not a verdict on a
    #     relationship.</p>
    "km.score_p": "<p>ਰਵਾਇਤ ਅਨੁਸਾਰ ਘੱਟੋ-ਘੱਟ 18 ਅੰਕ ਚਾਹੀਦੇ ਹਨ। ਸਿਰਫ਼ ਕੁੱਲ ਅੰਕ ਪੂਰੀ ਗੱਲ ਨਹੀਂ ਦੱਸਦੇ: ਜੇ ਨਾੜੀ ਜਾਂ ਭਕੂਟ ਦੋਸ਼ ਕੱਟਿਆ ਨਾ ਗਿਆ ਹੋਵੇ ਤਾਂ ਉੱਚੇ ਅੰਕ ਵੀ ਸਾਵਧਾਨੀ ਨਾਲ ਪੜ੍ਹੇ ਜਾਂਦੇ ਹਨ, ਅਤੇ ਮਜ਼ਬੂਤ ਗ੍ਰਹਿ ਮੈਤਰੀ ਤੇ ਬਿਨਾਂ ਦੋਸ਼ ਦੇ ਦਰਮਿਆਨੇ ਅੰਕ ਅਕਸਰ ਚੱਲਣਯੋਗ ਮੰਨੇ ਜਾਂਦੇ ਹਨ। ਇਹ ਸ਼੍ਰੇਣੀਆਂ ਲੰਮੇ ਇਤਿਹਾਸ ਵਾਲੀ ਰਵਾਇਤ ਹਨ, ਕੋਈ ਮਾਪ ਨਹੀਂ — ਇਹ ਮਾਰਗ-ਦਰਸ਼ਨ ਹਨ, ਕਿਸੇ ਰਿਸ਼ਤੇ ਬਾਰੇ ਫ਼ੈਸਲਾ ਨਹੀਂ।</p>",
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
    "km.or": "ਜਾਂ",
    # EN: <h2>Mangal Dosha (Manglik)</h2> <p>Mangal Dosha is checked separately from the 36 points.
    #     A chart is Manglik when Mars sits in the {houses} house counted from the
    #     <strong>Lagna</strong> (ascendant), the <strong>Moon</strong> or <strong>Venus</strong>.
    #     Classical texts exempt certain sign placements (for example Mars in its own sign Aries in
    #     the 1st), and Jupiter's aspect on Mars is held to soften it. When <strong>both</strong>
    #     partners are Manglik the dosha is conventionally treated as mutually cancelled — which is
    #     why Manglik matches are made with Manglik partners. Because it depends on the Lagna,
    #     Mangal Dosha does need a reliable birth time.</p>
    # keep: {houses}
    "km.mangal": "<h2>ਮੰਗਲ ਦੋਸ਼ (ਮੰਗਲੀਕ)</h2><p>ਮੰਗਲ ਦੋਸ਼ ਦੀ ਜਾਂਚ 36 ਅੰਕਾਂ ਤੋਂ ਵੱਖਰੀ ਕੀਤੀ ਜਾਂਦੀ ਹੈ। ਕੁੰਡਲੀ ਮੰਗਲੀਕ ਉਦੋਂ ਹੁੰਦੀ ਹੈ ਜਦੋਂ <strong>ਲਗਨ</strong>, <strong>ਚੰਦਰਮਾ</strong> ਜਾਂ <strong>ਸ਼ੁੱਕਰ</strong> ਤੋਂ ਗਿਣਨ ’ਤੇ ਮੰਗਲ ਭਾਵ {houses} ਵਿੱਚ ਬੈਠਾ ਹੋਵੇ। ਸ਼ਾਸਤਰਾਂ ਵਿੱਚ ਕੁਝ ਰਾਸ਼ੀ ਸਥਿਤੀਆਂ ਨੂੰ ਛੋਟ ਦਿੱਤੀ ਗਈ ਹੈ (ਜਿਵੇਂ ਮੰਗਲ ਆਪਣੀ ਰਾਸ਼ੀ ਮੇਖ ਵਿੱਚ ਪਹਿਲੇ ਭਾਵ ਵਿੱਚ), ਅਤੇ ਮੰਗਲ ’ਤੇ ਬ੍ਰਿਹਸਪਤੀ ਦੀ ਦ੍ਰਿਸ਼ਟੀ ਇਸ ਨੂੰ ਨਰਮ ਕਰਨ ਵਾਲੀ ਮੰਨੀ ਜਾਂਦੀ ਹੈ। ਜਦੋਂ <strong>ਦੋਵੇਂ</strong> ਜੀਅ ਮੰਗਲੀਕ ਹੋਣ ਤਾਂ ਰਵਾਇਤ ਅਨੁਸਾਰ ਦੋਸ਼ ਆਪਸ ਵਿੱਚ ਕੱਟਿਆ ਮੰਨਿਆ ਜਾਂਦਾ ਹੈ — ਇਸੇ ਕਰਕੇ ਮੰਗਲੀਕ ਦਾ ਰਿਸ਼ਤਾ ਮੰਗਲੀਕ ਨਾਲ ਹੀ ਕੀਤਾ ਜਾਂਦਾ ਹੈ। ਕਿਉਂਕਿ ਇਹ ਲਗਨ ’ਤੇ ਨਿਰਭਰ ਕਰਦਾ ਹੈ, ਮੰਗਲ ਦੋਸ਼ ਲਈ ਜਨਮ ਦਾ ਭਰੋਸੇਯੋਗ ਸਮਾਂ ਚਾਹੀਦਾ ਹੈ।</p>",
    # EN: <h2>How our matching tool works</h2> <p>Enter both people's date, time and place of birth.
    #     Both charts are cast with the sidereal zodiac (Lahiri ayanamsa) from the Swiss Ephemeris,
    #     and each koota is scored by table lookup from the classical tables, with every
    #     cancellation named. You get the full {total}-point breakdown and both partners' Mangal
    #     Dosha status, in English or <span lang="hi">हिन्दी</span>, free and without signing
    #     up.</p>
    # keep: {total}
    "km.how": "<h2>ਸਾਡਾ ਮਿਲਾਨ ਟੂਲ ਕਿਵੇਂ ਕੰਮ ਕਰਦਾ ਹੈ</h2><p>ਦੋਵਾਂ ਦੀ ਜਨਮ ਤਾਰੀਖ਼, ਸਮਾਂ ਅਤੇ ਥਾਂ ਭਰੋ। ਦੋਵੇਂ ਕੁੰਡਲੀਆਂ ਸਵਿਸ ਐਫ਼ੇਮੇਰਿਸ ਤੋਂ ਨਿਰਯਨ ਰਾਸ਼ੀ ਚੱਕਰ (ਲਾਹਿੜੀ ਅਯਨਾਂਸ਼) ਨਾਲ ਬਣਾਈਆਂ ਜਾਂਦੀਆਂ ਹਨ, ਅਤੇ ਹਰ ਕੂਟ ਦੇ ਅੰਕ ਸ਼ਾਸਤਰੀ ਸਾਰਣੀਆਂ ਵਿੱਚੋਂ ਵੇਖ ਕੇ ਦਿੱਤੇ ਜਾਂਦੇ ਹਨ, ਹਰ ਛੋਟ ਦਾ ਨਾਂ ਲੈ ਕੇ। ਤੁਹਾਨੂੰ {total} ਅੰਕਾਂ ਦਾ ਪੂਰਾ ਵੇਰਵਾ ਅਤੇ ਦੋਵਾਂ ਦੇ ਮੰਗਲ ਦੋਸ਼ ਦੀ ਸਥਿਤੀ ਮਿਲਦੀ ਹੈ, ਅੰਗਰੇਜ਼ੀ ਜਾਂ ਹਿੰਦੀ ਵਿੱਚ, ਮੁਫ਼ਤ ਅਤੇ ਬਿਨਾਂ ਸਾਈਨ ਅੱਪ ਕੀਤੇ।</p>",
    # EN: Open Kundali Milan
    "km.cta2": "ਕੁੰਡਲੀ ਮਿਲਾਨ ਖੋਲ੍ਹੋ",
    # EN: Varna
    "koota.varna": "ਵਰਣ",
    # EN: Vashya
    "koota.vashya": "ਵਸ਼ਯ",
    # EN: Tara
    "koota.tara": "ਤਾਰਾ",
    # EN: Yoni
    "koota.yoni": "ਯੋਨੀ",
    # EN: Graha Maitri
    "koota.graha_maitri": "ਗ੍ਰਹਿ ਮੈਤਰੀ",
    # EN: Gana
    "koota.gana": "ਗਣ",
    # EN: Bhakoot
    "koota.bhakoot": "ਭਕੂਟ",
    # EN: Nadi
    "koota.nadi": "ਨਾੜੀ",
    # EN: Spiritual and working temperament, from the Moon sign's varna. Full point when the groom's
    #     varna is not below the bride's.
    "koota_about.varna": "ਚੰਦਰ ਰਾਸ਼ੀ ਦੇ ਵਰਣ ਤੋਂ ਆਤਮਿਕ ਅਤੇ ਕੰਮਕਾਜੀ ਸੁਭਾਅ। ਪੂਰੇ ਅੰਕ ਉਦੋਂ ਮਿਲਦੇ ਹਨ ਜਦੋਂ ਲਾੜੇ ਦਾ ਵਰਣ ਲਾੜੀ ਦੇ ਵਰਣ ਤੋਂ ਹੇਠਾਂ ਨਾ ਹੋਵੇ।",
    # EN: Mutual attraction and influence — which sign “draws” the other.
    "koota_about.vashya": "ਆਪਸੀ ਖਿੱਚ ਅਤੇ ਪ੍ਰਭਾਵ — ਕਿਹੜੀ ਰਾਸ਼ੀ ਦੂਜੀ ਨੂੰ “ਖਿੱਚਦੀ” ਹੈ।",
    # EN: Health and wellbeing, from the count between the two birth nakshatras; the 3rd, 5th and
    #     7th taras are unfavourable.
    "koota_about.tara": "ਸਿਹਤ ਅਤੇ ਭਲਾਈ, ਦੋਵਾਂ ਜਨਮ ਨਕਸ਼ਤਰਾਂ ਵਿਚਲੀ ਗਿਣਤੀ ਤੋਂ; ਤੀਜਾ, ਪੰਜਵਾਂ ਅਤੇ ਸੱਤਵਾਂ ਤਾਰਾ ਅਸ਼ੁਭ ਹੈ।",
    # EN: Physical and intimate compatibility; each nakshatra has an animal yoni, and sworn-enemy
    #     animals score zero.
    "koota_about.yoni": "ਸਰੀਰਕ ਅਤੇ ਨੇੜਤਾ ਦਾ ਮੇਲ; ਹਰ ਨਕਸ਼ਤਰ ਦੀ ਇੱਕ ਪਸ਼ੂ ਯੋਨੀ ਹੁੰਦੀ ਹੈ, ਅਤੇ ਪੱਕੇ ਵੈਰੀ ਪਸ਼ੂਆਂ ਨੂੰ ਸਿਫ਼ਰ ਅੰਕ ਮਿਲਦੇ ਹਨ।",
    # EN: Friendship between the lords of the two Moon signs — the mental wavelength of the couple.
    "koota_about.graha_maitri": "ਦੋਵਾਂ ਚੰਦਰ ਰਾਸ਼ੀਆਂ ਦੇ ਸੁਆਮੀਆਂ ਵਿਚਲੀ ਦੋਸਤੀ — ਜੋੜੇ ਦੀ ਮਾਨਸਿਕ ਤਾਲ-ਮੇਲ।",
    # EN: Temperament: Deva (divine), Manushya (human) or Rakshasa (fierce).
    "koota_about.gana": "ਸੁਭਾਅ: ਦੇਵ (ਦੈਵੀ), ਮਨੁੱਖ ਜਾਂ ਰਾਖਸ਼ (ਉਗਰ)।",
    # EN: The relative placement of the two Moon signs. The 2/12, 5/9 and 6/8 positions form Bhakoot
    #     dosha, cancelled when the sign lords are the same or friends.
    "koota_about.bhakoot": "ਦੋਵਾਂ ਚੰਦਰ ਰਾਸ਼ੀਆਂ ਦੀ ਆਪਸੀ ਸਥਿਤੀ। 2/12, 5/9 ਅਤੇ 6/8 ਦੀਆਂ ਸਥਿਤੀਆਂ ਭਕੂਟ ਦੋਸ਼ ਬਣਾਉਂਦੀਆਂ ਹਨ, ਜੋ ਰਾਸ਼ੀ ਸੁਆਮੀ ਇੱਕੋ ਹੋਣ ਜਾਂ ਮਿੱਤਰ ਹੋਣ ’ਤੇ ਕੱਟਿਆ ਜਾਂਦਾ ਹੈ।",
    # EN: The highest-weighted koota, tied to health and progeny. The same nadi for both is Nadi
    #     dosha, with classical cancellations for the same sign/different nakshatra or same
    #     nakshatra/different pada.
    "koota_about.nadi": "ਸਭ ਤੋਂ ਵੱਧ ਭਾਰ ਵਾਲਾ ਕੂਟ, ਜੋ ਸਿਹਤ ਅਤੇ ਸੰਤਾਨ ਨਾਲ ਜੁੜਿਆ ਹੈ। ਦੋਵਾਂ ਦੀ ਇੱਕੋ ਨਾੜੀ ਹੋਣਾ ਨਾੜੀ ਦੋਸ਼ ਹੈ, ਜਿਸ ਦੀਆਂ ਸ਼ਾਸਤਰੀ ਛੋਟਾਂ ਹਨ: ਇੱਕੋ ਰਾਸ਼ੀ ਪਰ ਵੱਖਰਾ ਨਕਸ਼ਤਰ, ਜਾਂ ਇੱਕੋ ਨਕਸ਼ਤਰ ਪਰ ਵੱਖਰਾ ਚਰਣ।",
    # EN: Free Kundali Online — Janam Kundali (Birth Chart) in English & Hindi | {brand}
    # keep: {brand}
    "fk.title": "ਮੁਫ਼ਤ ਕੁੰਡਲੀ ਆਨਲਾਈਨ — ਪੰਜਾਬੀ, ਹਿੰਦੀ ਅਤੇ ਅੰਗਰੇਜ਼ੀ ਵਿੱਚ ਜਨਮ ਕੁੰਡਲੀ | {brand}",
    # EN: Make your free janam kundali online: Lagna chart in North or South Indian style, planet
    #     positions, Moon nakshatra, Vimshottari dasha, Navamsa and other divisional charts,
    #     Manglik, Sade Sati and Kaal Sarp check — in English or Hindi, no sign-in needed.
    "fk.desc": "ਆਨਲਾਈਨ ਆਪਣੀ ਮੁਫ਼ਤ ਜਨਮ ਕੁੰਡਲੀ ਬਣਾਓ: ਉੱਤਰੀ ਜਾਂ ਦੱਖਣੀ ਭਾਰਤੀ ਸ਼ੈਲੀ ਵਿੱਚ ਲਗਨ ਕੁੰਡਲੀ, ਗ੍ਰਹਿ ਸਥਿਤੀ, ਚੰਦਰ ਨਕਸ਼ਤਰ, ਵਿਮਸ਼ੋਤਰੀ ਦਸ਼ਾ, ਨਵਾਂਸ਼ ਅਤੇ ਹੋਰ ਵਰਗ ਕੁੰਡਲੀਆਂ, ਮੰਗਲੀਕ, ਸਾੜ੍ਹਸਾਤੀ ਅਤੇ ਕਾਲ ਸਰਪ ਦੀ ਜਾਂਚ — ਸਾਈਨ ਇਨ ਤੋਂ ਬਿਨਾਂ।",
    # EN: Free Kundali
    "fk.crumb": "ਮੁਫ਼ਤ ਕੁੰਡਲੀ",
    # EN: <h1>Free Janam Kundali online</h1> <p class="hi" lang="hi">मुफ़्त जन्म कुंडली — हिंदी और
    #     अंग्रेज़ी में</p> <p>A <strong>janam kundali</strong> (<span lang="hi">जन्म कुंडली</span>,
    #     birth chart) is a map of the sky at the exact moment and place you were born: which of the
    #     twelve signs was rising on the eastern horizon (your <strong>Lagna</strong>), and where
    #     the Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu and Ketu stood among the signs
    #     and the 27 nakshatras. Vedic astrology reads everything else — personality, the twelve
    #     areas of life, and above all <em>timing</em> through the dasha periods — from this one
    #     chart. Ours is computed to the minute and is free.</p>
    "fk.intro": "<h1>ਆਨਲਾਈਨ ਮੁਫ਼ਤ ਜਨਮ ਕੁੰਡਲੀ</h1><p class=\"hi\">ਮੁਫ਼ਤ ਜਨਮ ਕੁੰਡਲੀ — ਲਗਨ, ਗ੍ਰਹਿ, ਦਸ਼ਾ ਅਤੇ ਦੋਸ਼ ਦੀ ਜਾਂਚ</p><p><strong>ਜਨਮ ਕੁੰਡਲੀ</strong> ਤੁਹਾਡੇ ਜਨਮ ਦੇ ਠੀਕ ਪਲ ਅਤੇ ਥਾਂ ਦੇ ਅਸਮਾਨ ਦਾ ਨਕਸ਼ਾ ਹੈ: ਉਸ ਵੇਲੇ ਪੂਰਬੀ ਦਿਸਹੱਦੇ ’ਤੇ ਬਾਰਾਂ ਰਾਸ਼ੀਆਂ ਵਿੱਚੋਂ ਕਿਹੜੀ ਚੜ੍ਹ ਰਹੀ ਸੀ (ਤੁਹਾਡੀ <strong>ਲਗਨ</strong>), ਅਤੇ ਸੂਰਜ, ਚੰਦਰਮਾ, ਮੰਗਲ, ਬੁੱਧ, ਬ੍ਰਿਹਸਪਤੀ, ਸ਼ੁੱਕਰ, ਸ਼ਨੀ, ਰਾਹੂ ਅਤੇ ਕੇਤੂ ਕਿਹੜੀਆਂ ਰਾਸ਼ੀਆਂ ਅਤੇ 27 ਨਕਸ਼ਤਰਾਂ ਵਿੱਚ ਸਨ। ਵੈਦਿਕ ਜੋਤਿਸ਼ ਬਾਕੀ ਸਭ ਕੁਝ — ਸੁਭਾਅ, ਜ਼ਿੰਦਗੀ ਦੇ ਬਾਰਾਂ ਖੇਤਰ, ਅਤੇ ਸਭ ਤੋਂ ਵੱਧ ਦਸ਼ਾਵਾਂ ਰਾਹੀਂ <em>ਸਮਾਂ</em> — ਇਸੇ ਇੱਕ ਕੁੰਡਲੀ ਤੋਂ ਪੜ੍ਹਦਾ ਹੈ। ਸਾਡੀ ਕੁੰਡਲੀ ਮਿੰਟ ਦੀ ਸ਼ੁੱਧਤਾ ਨਾਲ ਗਿਣੀ ਜਾਂਦੀ ਹੈ ਅਤੇ ਮੁਫ਼ਤ ਹੈ।</p>",
    # EN: Make my free kundali now
    "fk.cta1": "ਹੁਣੇ ਮੇਰੀ ਮੁਫ਼ਤ ਕੁੰਡਲੀ ਬਣਾਓ",
    # EN: <p>You need your <strong>date</strong>, <strong>time</strong> and <strong>place</strong>
    #     of birth. No sign-in, no card.</p>
    "fk.need": "<p>ਤੁਹਾਨੂੰ ਜਨਮ ਦੀ <strong>ਤਾਰੀਖ਼</strong>, <strong>ਸਮਾਂ</strong> ਅਤੇ <strong>ਥਾਂ</strong> ਚਾਹੀਦੀ ਹੈ। ਸਾਈਨ ਇਨ ਨਹੀਂ, ਕਾਰਡ ਨਹੀਂ।</p>",
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
    "fk.includes": "<h2>ਤੁਹਾਡੀ ਮੁਫ਼ਤ ਕੁੰਡਲੀ ਵਿੱਚ ਕੀ ਕੁਝ ਹੈ</h2><ul><li><strong>ਲਗਨ ਕੁੰਡਲੀ (D1)</strong> ਉੱਤਰੀ ਜਾਂ ਦੱਖਣੀ ਭਾਰਤੀ ਸ਼ੈਲੀ ਵਿੱਚ — ਇੱਕ ਟੈਪ ਨਾਲ ਬਦਲੋ।</li><li><strong>ਗ੍ਰਹਿ ਸਥਿਤੀ</strong>: ਨੌਂ ਗ੍ਰਹਿਆਂ ਅਤੇ ਲਗਨ ਦੀ ਰਾਸ਼ੀ, ਅੰਸ਼, ਭਾਵ, ਬਲ ਅਤੇ ਵੱਕਰੀ ਹਾਲਤ, ਨਾਲ ਤੁਹਾਡੇ ਚੰਦਰਮਾ ਦਾ ਨਕਸ਼ਤਰ ਤੇ ਚਰਣ।</li><li><strong>ਬਾਰਾਂ ਭਾਵ</strong> ਅਤੇ ਹਰ ਇੱਕ ਵਿੱਚ ਬੈਠੇ ਗ੍ਰਹਿ।</li><li><strong>ਵਿਮਸ਼ੋਤਰੀ ਦਸ਼ਾ</strong>: ਤੁਹਾਡੀ ਮੌਜੂਦਾ ਮਹਾਦਸ਼ਾ ਅਤੇ ਅੰਤਰਦਸ਼ਾ ਮਿਤੀਆਂ ਸਮੇਤ, ਇੱਕ ਚਿੱਤਰ ਸਮਾਂ-ਰੇਖਾ ’ਤੇ।</li><li><strong>ਵਰਗ ਕੁੰਡਲੀਆਂ</strong>: {vargas}।</li><li><strong>ਅਸ਼ਟਕਵਰਗ</strong>: ਸਰਵਾਸ਼ਟਕਵਰਗ ਅਤੇ ਭਿੰਨਾਸ਼ਟਕਵਰਗ ਦੇ ਬਿੰਦੂ, ਭਾਵ ਮੁਤਾਬਕ।</li><li><strong>ਜੈਮਿਨੀ</strong> ਚਰ ਕਾਰਕ (ਆਤਮਕਾਰਕ ਤੋਂ ਦਾਰਾਕਾਰਕ ਤੱਕ) ਅਤੇ ਆਰੂੜ੍ਹ ਪਦ, ਅਤੇ ਲਗਨ, ਚੰਦਰਮਾ ਤੇ ਸੂਰਜ ਤਿੰਨਾਂ ਤੋਂ ਕੁੰਡਲੀ ਦਾ <strong>ਸੁਦਰਸ਼ਨ ਚੱਕਰ</strong> ਵਿਸ਼ਲੇਸ਼ਣ।</li><li><strong>ਦੋਸ਼ ਦੀ ਜਾਂਚ</strong>: ਮੰਗਲ ਦੋਸ਼ (ਮੰਗਲੀਕ), ਸਾੜ੍ਹਸਾਤੀ ਅਤੇ ਕਾਲ ਸਰਪ।</li><li>ਤੁਹਾਡੀ ਕੁੰਡਲੀ ਅਤੇ ਮੌਜੂਦਾ ਦਸ਼ਾ ਲਈ <strong>ਰਤਨ ਅਤੇ ਉਪਾਅ</strong> ਦੇ ਸੁਝਾਅ।</li><li>ਤੁਹਾਡੀ ਕੁੰਡਲੀ ਦੇ ਡੈਸ਼ਬੋਰਡ ’ਤੇ ਤੁਹਾਡਾ <strong>ਰੋਜ਼ਾਨਾ ਫਲਾਦੇਸ਼</strong> ਅਤੇ ਅੱਜ ਦਾ ਪੰਚਾਂਗ।</li></ul><p>ਸਭ ਕੁਝ <strong>ਲਾਹਿੜੀ ਅਯਨਾਂਸ਼ ਵਾਲੇ ਨਿਰਯਨ ਰਾਸ਼ੀ ਚੱਕਰ</strong> ਵਿੱਚ, ਪੂਰੀ ਰਾਸ਼ੀ ਵਾਲੇ ਭਾਵਾਂ ਸਮੇਤ, ਸਵਿਸ ਐਫ਼ੇਮੇਰਿਸ ਤੋਂ ਗਿਣਿਆ ਜਾਂਦਾ ਹੈ। ਮੁਫ਼ਤ ਖਾਤੇ ਨਾਲ ਤੁਸੀਂ ਕੁੰਡਲੀਆਂ ਸੰਭਾਲ ਸਕਦੇ ਹੋ, ਕੁੰਡਲੀ ਨੂੰ ਅੰਗਰੇਜ਼ੀ ਜਾਂ ਹਿੰਦੀ ਵਿੱਚ PDF ਵਜੋਂ ਡਾਊਨਲੋਡ ਕਰ ਸਕਦੇ ਹੋ, ਅਤੇ ਏਆਈ ਜੋਤਸ਼ੀ ਤੋਂ ਆਪਣੇ ਪਹਿਲੇ ਸਵਾਲ ਮੁਫ਼ਤ ਪੁੱਛ ਸਕਦੇ ਹੋ।</p>",
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
    "fk.read": "<h2>ਆਪਣੀ ਕੁੰਡਲੀ ਕਿਵੇਂ ਪੜ੍ਹੀਏ</h2><h3>1. ਲਗਨ ਤੋਂ ਸ਼ੁਰੂ ਕਰੋ</h3><p>ਪਹਿਲਾ ਭਾਵ ਜਨਮ ਵੇਲੇ ਚੜ੍ਹ ਰਹੀ ਰਾਸ਼ੀ ਹੈ। ਉੱਤਰੀ ਭਾਰਤੀ ਕੁੰਡਲੀ ਵਿੱਚ ਇਹ ਉੱਪਰ ਵਿਚਕਾਰਲਾ ਹੀਰਾ ਹੈ, ਅਤੇ ਹਰ ਭਾਵ ਵਿੱਚ ਲਿਖਿਆ ਅੰਕ <em>ਰਾਸ਼ੀ</em> ਦਾ ਹੁੰਦਾ ਹੈ (1 = ਮੇਖ … 12 = ਮੀਨ), ਭਾਵ ਦਾ ਨਹੀਂ। ਦੱਖਣੀ ਭਾਰਤੀ ਕੁੰਡਲੀ ਵਿੱਚ ਰਾਸ਼ੀਆਂ ਪੱਕੇ ਖਾਨਿਆਂ ਵਿੱਚ ਰਹਿੰਦੀਆਂ ਹਨ ਅਤੇ ਲਗਨ ’ਤੇ ਨਿਸ਼ਾਨ ਲੱਗਿਆ ਹੁੰਦਾ ਹੈ। ਲਗਨ ਅਤੇ ਉਸ ਦਾ ਸੁਆਮੀ ਸਰੀਰ, ਸੁਭਾਅ ਅਤੇ ਜ਼ਿੰਦਗੀ ਦੀ ਸਮੁੱਚੀ ਦਿਸ਼ਾ ਦੱਸਦੇ ਹਨ।</p><h3>2. ਆਪਣੀ ਚੰਦਰ ਰਾਸ਼ੀ ਤੇ ਨਕਸ਼ਤਰ ਵੇਖੋ</h3><p>ਭਾਰਤੀ ਵਰਤੋਂ ਵਿੱਚ ਤੁਹਾਡੀ <strong>ਰਾਸ਼ੀ</strong> ਚੰਦਰਮਾ ਦੀ ਰਾਸ਼ੀ ਹੁੰਦੀ ਹੈ, ਸੂਰਜ ਦੀ ਨਹੀਂ। ਰਾਸ਼ੀਫਲ, ਸਾੜ੍ਹਸਾਤੀ ਅਤੇ ਕੁੰਡਲੀ ਮਿਲਾਨ ਇਸੇ ਰਾਸ਼ੀ ਤੋਂ ਵੇਖੇ ਜਾਂਦੇ ਹਨ, ਅਤੇ ਚੰਦਰਮਾ ਦਾ ਨਕਸ਼ਤਰ ਤੈਅ ਕਰਦਾ ਹੈ ਕਿ ਤੁਹਾਡੀ ਵਿਮਸ਼ੋਤਰੀ ਦਸ਼ਾ ਕਿੱਥੋਂ ਸ਼ੁਰੂ ਹੁੰਦੀ ਹੈ।</p><h3>3. ਗ੍ਰਹਿਆਂ ਨੂੰ ਭਾਵ ਮੁਤਾਬਕ ਪੜ੍ਹੋ</h3><p>ਹਰ ਭਾਵ ਜ਼ਿੰਦਗੀ ਦਾ ਇੱਕ ਖੇਤਰ ਹੈ: ਪਹਿਲਾ ਆਪਾ, ਦੂਜਾ ਧਨ ਅਤੇ ਪਰਿਵਾਰ, ਤੀਜਾ ਹਿੰਮਤ ਅਤੇ ਭੈਣ-ਭਰਾ, ਚੌਥਾ ਘਰ ਅਤੇ ਮਾਂ, ਪੰਜਵਾਂ ਸੰਤਾਨ ਅਤੇ ਬੁੱਧੀ, ਛੇਵਾਂ ਸਿਹਤ ਅਤੇ ਵਿਰੋਧੀ, ਸੱਤਵਾਂ ਵਿਆਹ ਅਤੇ ਸਾਂਝੇਦਾਰੀ, ਅੱਠਵਾਂ ਉਮਰ ਅਤੇ ਅਚਾਨਕ ਬਦਲਾਅ, ਨੌਵਾਂ ਕਿਸਮਤ ਅਤੇ ਧਰਮ, ਦਸਵਾਂ ਕਰੀਅਰ, ਗਿਆਰ੍ਹਵਾਂ ਲਾਭ, ਬਾਰ੍ਹਵਾਂ ਖ਼ਰਚ ਅਤੇ ਮੋਕਸ਼। ਗ੍ਰਹਿ ਉਸ ਭਾਵ ਨੂੰ ਰੰਗਦਾ ਹੈ ਜਿਸ ਵਿੱਚ ਉਹ ਬੈਠਾ ਹੈ ਅਤੇ ਉਨ੍ਹਾਂ ਭਾਵਾਂ ਨੂੰ ਵੀ ਜਿਨ੍ਹਾਂ ਦਾ ਉਹ ਸੁਆਮੀ ਹੈ; ਉਸ ਦਾ ਬਲ (ਉੱਚ, ਆਪਣੀ ਰਾਸ਼ੀ, ਨੀਚ) ਦੱਸਦਾ ਹੈ ਕਿ ਉਹ ਕਿੰਨਾ ਫਲ ਦੇ ਸਕਦਾ ਹੈ।</p><h3>4. ਦੇਖੋ ਕਿ ਕਿਹੜੀ ਦਸ਼ਾ ਚੱਲ ਰਹੀ ਹੈ</h3><p>ਦਸ਼ਾ ਦੱਸਦੀ ਹੈ ਕਿ <em>ਕਦੋਂ</em>। ਮਹਾਦਸ਼ਾ ਦਾ ਸੁਆਮੀ, ਅਤੇ ਉਸ ਦੇ ਅੰਦਰ ਅੰਤਰਦਸ਼ਾ ਦਾ ਸੁਆਮੀ, ਉਹ ਗ੍ਰਹਿ ਹਨ ਜਿਨ੍ਹਾਂ ਦੇ ਭਾਵ ਇਸ ਦੌਰ ਵਿੱਚ ਜਾਗ ਪੈਂਦੇ ਹਨ — ਇਸੇ ਲਈ ਇੱਕੋ ਜਿਹੀਆਂ ਕੁੰਡਲੀਆਂ ਵਾਲੇ ਦੋ ਜਣਿਆਂ ਦੇ ਸਾਲ ਬਹੁਤ ਵੱਖਰੇ ਹੋ ਸਕਦੇ ਹਨ।</p><h3>5. ਦੋਸ਼ਾਂ ਨੂੰ ਪ੍ਰਸੰਗ ਵਿੱਚ ਵੇਖੋ</h3><p>ਦੋਸ਼ ਇੱਕ ਪੈਟਰਨ ਹੈ ਜਿਸ ਨੂੰ ਪੜ੍ਹਨਾ ਹੁੰਦਾ ਹੈ, ਕੋਈ ਫ਼ੈਸਲਾ ਨਹੀਂ। ਮੰਗਲ ਦੋਸ਼ ਦੀਆਂ ਸ਼ਾਸਤਰੀ ਛੋਟਾਂ ਹਨ; ਸਾੜ੍ਹਸਾਤੀ ਸਾਢੇ ਸੱਤ ਸਾਲ ਦਾ ਗੋਚਰ ਹੈ ਜੋ ਹਰ ਕਿਸੇ ਦੇ ਜੀਵਨ ਵਿੱਚ ਦੋ-ਤਿੰਨ ਵਾਰ ਆਉਂਦਾ ਹੈ। ਦੋਸ਼ ਰਿਪੋਰਟ ਉਹ ਛੋਟਾਂ ਦੱਸਦੀ ਹੈ ਜੋ ਉਸ ਨੂੰ ਮਿਲੀਆਂ।</p>",
    # EN: Create my janam kundali — free
    "fk.cta2": "ਮੇਰੀ ਜਨਮ ਕੁੰਡਲੀ ਬਣਾਓ — ਮੁਫ਼ਤ",
    # EN: <h2>Frequently asked questions</h2>
    "fk.faq_h2": "<h2>ਅਕਸਰ ਪੁੱਛੇ ਜਾਂਦੇ ਸਵਾਲ</h2>",
    # EN: Rashi
    "varga.D1": "ਰਾਸ਼ੀ",
    # EN: Drekkana
    "varga.D3": "ਦ੍ਰੇਸ਼ਕਾਣ",
    # EN: Saptamsa
    "varga.D7": "ਸਪਤਾਂਸ਼",
    # EN: Navamsa
    "varga.D9": "ਨਵਾਂਸ਼",
    # EN: Dashamsa
    "varga.D10": "ਦਸ਼ਾਂਸ਼",
    # EN: Dwadashamsa
    "varga.D12": "ਦ੍ਵਾਦਸ਼ਾਂਸ਼",
    # EN: Not recommended
    "km.band0": "ਸਿਫ਼ਾਰਸ਼ ਨਹੀਂ",
    # EN: Acceptable
    "km.band1": "ਚੱਲਣਯੋਗ",
    # EN: Good
    "km.band2": "ਚੰਗਾ",
    # EN: Excellent
    "km.band3": "ਉੱਤਮ",
}

# app/seo_text.py FAQ["pa"] — the seven free-kundali FAQ pairs (plain text)  [7]
SEO_FAQ = (
    # EN q: Is the kundali really free?
    # EN a: Yes. Casting the chart, the dashas, the divisional charts and the dosha check cost
    #       nothing, and you do not need to sign in to see them. Only the AI astrologer's answers
    #       beyond your free questions, and in-depth paid reports such as the Life Book, cost money.
    ("ਕੀ ਕੁੰਡਲੀ ਸੱਚਮੁੱਚ ਮੁਫ਼ਤ ਹੈ?", "ਹਾਂ। ਕੁੰਡਲੀ ਬਣਾਉਣ, ਦਸ਼ਾਵਾਂ, ਵਰਗ ਕੁੰਡਲੀਆਂ ਅਤੇ ਦੋਸ਼ ਦੀ ਜਾਂਚ ਵਿੱਚ ਕੋਈ ਖ਼ਰਚ ਨਹੀਂ ਆਉਂਦਾ, ਅਤੇ ਇਨ੍ਹਾਂ ਨੂੰ ਵੇਖਣ ਲਈ ਸਾਈਨ ਇਨ ਕਰਨ ਦੀ ਲੋੜ ਨਹੀਂ। ਸਿਰਫ਼ ਮੁਫ਼ਤ ਸਵਾਲਾਂ ਤੋਂ ਬਾਅਦ ਏਆਈ ਜੋਤਸ਼ੀ ਦੇ ਜਵਾਬਾਂ ਅਤੇ ਲਾਈਫ਼ ਬੁੱਕ ਵਰਗੀਆਂ ਵਿਸਥਾਰ ਵਾਲੀਆਂ ਭੁਗਤਾਨ ਵਾਲੀਆਂ ਰਿਪੋਰਟਾਂ ਲਈ ਪੈਸੇ ਲੱਗਦੇ ਹਨ।"),
    # EN q: What details do I need?
    # EN a: Your date of birth, time of birth and place of birth. The place sets the latitude,
    #       longitude and time zone, which decide the Lagna (ascendant) and the house positions.
    ("ਮੈਨੂੰ ਕਿਹੜਾ ਵੇਰਵਾ ਚਾਹੀਦਾ ਹੈ?", "ਤੁਹਾਡੀ ਜਨਮ ਤਾਰੀਖ਼, ਜਨਮ ਦਾ ਸਮਾਂ ਅਤੇ ਜਨਮ ਸਥਾਨ। ਥਾਂ ਤੋਂ ਅਕਸ਼ਾਂਸ਼, ਰੇਖਾਂਸ਼ ਅਤੇ ਸਮਾਂ ਖੇਤਰ ਤੈਅ ਹੁੰਦੇ ਹਨ, ਜਿਨ੍ਹਾਂ ਨਾਲ ਲਗਨ ਅਤੇ ਭਾਵਾਂ ਦੀ ਸਥਿਤੀ ਨਿਕਲਦੀ ਹੈ।"),
    # EN q: What if I don't know my exact birth time?
    # EN a: The chart is still cast, at 12:00 noon. The Moon sign and nakshatra are usually still
    #       right (unless the Moon changed sign or nakshatra that day), so Moon-based readings, Sade
    #       Sati and Kundali Milan stay useful — but the Lagna, the houses and Mangal Dosha need a
    #       reliable time. A time from a birth certificate or hospital record is best.
    ("ਜੇ ਮੈਨੂੰ ਜਨਮ ਦਾ ਸਹੀ ਸਮਾਂ ਨਾ ਪਤਾ ਹੋਵੇ ਤਾਂ?", "ਕੁੰਡਲੀ ਫਿਰ ਵੀ ਬਣ ਜਾਂਦੀ ਹੈ, ਦੁਪਹਿਰ 12:00 ਵਜੇ ਦੇ ਸਮੇਂ ਨਾਲ। ਚੰਦਰ ਰਾਸ਼ੀ ਅਤੇ ਨਕਸ਼ਤਰ ਆਮ ਤੌਰ ’ਤੇ ਫਿਰ ਵੀ ਸਹੀ ਰਹਿੰਦੇ ਹਨ (ਜਦੋਂ ਤੱਕ ਉਸ ਦਿਨ ਚੰਦਰਮਾ ਨੇ ਰਾਸ਼ੀ ਜਾਂ ਨਕਸ਼ਤਰ ਨਾ ਬਦਲਿਆ ਹੋਵੇ), ਇਸ ਲਈ ਚੰਦਰਮਾ ਆਧਾਰਿਤ ਫਲ, ਸਾੜ੍ਹਸਾਤੀ ਅਤੇ ਕੁੰਡਲੀ ਮਿਲਾਨ ਕੰਮ ਦੇ ਰਹਿੰਦੇ ਹਨ — ਪਰ ਲਗਨ, ਭਾਵਾਂ ਅਤੇ ਮੰਗਲ ਦੋਸ਼ ਲਈ ਭਰੋਸੇਯੋਗ ਸਮਾਂ ਚਾਹੀਦਾ ਹੈ। ਜਨਮ ਸਰਟੀਫ਼ਿਕੇਟ ਜਾਂ ਹਸਪਤਾਲ ਦੇ ਰਿਕਾਰਡ ਵਾਲਾ ਸਮਾਂ ਸਭ ਤੋਂ ਵਧੀਆ ਹੈ।"),
    # EN q: Which system do you use — Lahiri, KP, tropical?
    # EN a: Every chart is sidereal (Nirayana) with the Lahiri (Chitrapaksha) ayanamsa, whole-sign
    #       houses and Vimshottari dasha — the convention of most Indian almanacs and astrologers.
    #       Planet positions come from the Swiss Ephemeris.
    ("ਤੁਸੀਂ ਕਿਹੜੀ ਪ੍ਰਣਾਲੀ ਵਰਤਦੇ ਹੋ — ਲਾਹਿੜੀ, ਕੇਪੀ, ਸਾਇਨ?", "ਹਰ ਕੁੰਡਲੀ ਨਿਰਯਨ ਹੈ, ਲਾਹਿੜੀ (ਚਿਤ੍ਰਪੱਖ) ਅਯਨਾਂਸ਼, ਪੂਰੀ ਰਾਸ਼ੀ ਵਾਲੇ ਭਾਵਾਂ ਅਤੇ ਵਿਮਸ਼ੋਤਰੀ ਦਸ਼ਾ ਨਾਲ — ਜੋ ਜ਼ਿਆਦਾਤਰ ਭਾਰਤੀ ਪੰਚਾਂਗਾਂ ਅਤੇ ਜੋਤਸ਼ੀਆਂ ਦੀ ਰਵਾਇਤ ਹੈ। ਗ੍ਰਹਿਆਂ ਦੀਆਂ ਸਥਿਤੀਆਂ ਸਵਿਸ ਐਫ਼ੇਮੇਰਿਸ ਤੋਂ ਆਉਂਦੀਆਂ ਹਨ।"),
    # EN q: Can I see my kundali in Hindi?
    # EN a: Yes. Switch the app to हिन्दी and the chart, planet and sign names, dashas and readings
    #       all appear in Hindi; the PDF can be downloaded in Hindi too.
    ("ਕੀ ਮੈਂ ਆਪਣੀ ਕੁੰਡਲੀ ਹਿੰਦੀ ਵਿੱਚ ਵੇਖ ਸਕਦਾ ਹਾਂ?", "ਹਾਂ। ਐਪ ਨੂੰ ਹਿੰਦੀ ਵਿੱਚ ਬਦਲੋ ਅਤੇ ਕੁੰਡਲੀ, ਗ੍ਰਹਿਆਂ ਅਤੇ ਰਾਸ਼ੀਆਂ ਦੇ ਨਾਂ, ਦਸ਼ਾਵਾਂ ਅਤੇ ਫਲ ਸਭ ਹਿੰਦੀ ਵਿੱਚ ਦਿਸਣਗੇ; PDF ਵੀ ਹਿੰਦੀ ਵਿੱਚ ਡਾਊਨਲੋਡ ਹੋ ਸਕਦੀ ਹੈ।"),
    # EN q: North Indian or South Indian chart?
    # EN a: Both. The same chart can be shown as the North Indian diamond chart (houses fixed, signs
    #       numbered) or the South Indian square chart (signs fixed), with one tap.
    ("ਉੱਤਰੀ ਭਾਰਤੀ ਜਾਂ ਦੱਖਣੀ ਭਾਰਤੀ ਕੁੰਡਲੀ?", "ਦੋਵੇਂ। ਇੱਕੋ ਕੁੰਡਲੀ ਨੂੰ ਇੱਕ ਟੈਪ ਨਾਲ ਉੱਤਰੀ ਭਾਰਤੀ ਹੀਰੇ ਵਾਲੀ ਕੁੰਡਲੀ (ਭਾਵ ਪੱਕੇ, ਰਾਸ਼ੀਆਂ ਦੇ ਅੰਕ) ਜਾਂ ਦੱਖਣੀ ਭਾਰਤੀ ਚੌਰਸ ਕੁੰਡਲੀ (ਰਾਸ਼ੀਆਂ ਪੱਕੀਆਂ) ਵਜੋਂ ਵੇਖਿਆ ਜਾ ਸਕਦਾ ਹੈ।"),
    # EN q: Is this the same as a horoscope?
    # EN a: A janam kundali is the birth chart itself — the fixed map of the sky at your birth. A
    #       daily horoscope or rashifal is a short general forecast for everyone with the same Moon
    #       sign. Your kundali is personal; a rashifal is not.
    ("ਕੀ ਇਹ ਰਾਸ਼ੀਫਲ ਵਾਂਗ ਹੀ ਹੈ?", "ਜਨਮ ਕੁੰਡਲੀ ਖ਼ੁਦ ਜਨਮ ਦਾ ਨਕਸ਼ਾ ਹੈ — ਤੁਹਾਡੇ ਜਨਮ ਵੇਲੇ ਅਸਮਾਨ ਦਾ ਪੱਕਾ ਨਕਸ਼ਾ। ਰੋਜ਼ਾਨਾ ਰਾਸ਼ੀਫਲ ਇੱਕੋ ਚੰਦਰ ਰਾਸ਼ੀ ਵਾਲੇ ਸਭ ਲੋਕਾਂ ਲਈ ਇੱਕ ਛੋਟਾ ਆਮ ਪੂਰਵ-ਅਨੁਮਾਨ ਹੁੰਦਾ ਹੈ। ਤੁਹਾਡੀ ਕੁੰਡਲੀ ਨਿੱਜੀ ਹੈ; ਰਾਸ਼ੀਫਲ ਨਹੀਂ।"),
)

# app/i18n.py CHROME["pa"] — chrome shared by every server page: breadcrumb, footer links, disclaimer (HTML: write &amp;)  [10]
CHROME = {
    # EN: Home
    "home": "ਮੁੱਖ ਪੰਨਾ",
    # EN: Breadcrumb
    "breadcrumb": "ਬ੍ਰੈੱਡਕ੍ਰੰਬ",
    # EN: Share on WhatsApp
    "share": "WhatsApp ’ਤੇ ਸਾਂਝਾ ਕਰੋ",
    # EN: Kathas
    "f_katha": "ਕਥਾਵਾਂ",
    # EN: Terms &amp; Conditions
    "f_terms": "ਸ਼ਰਤਾਂ ਅਤੇ ਨਿਯਮ",
    # EN: Privacy Policy
    "f_privacy": "ਗੋਪਨੀਯਤਾ ਨੀਤੀ",
    # EN: Refund &amp; Cancellation
    "f_refund": "ਰਿਫ਼ੰਡ ਅਤੇ ਰੱਦ ਕਰਨਾ",
    # EN: Contact Us
    "f_contact": "ਸਾਡੇ ਨਾਲ ਸੰਪਰਕ ਕਰੋ",
    # EN: Feedback
    "f_feedback": "ਸੁਝਾਅ",
    # EN: Astrological readings are provided for guidance and entertainment. They are not medical,
    #     legal or financial advice.
    "disclaimer": "ਜੋਤਿਸ਼ੀ ਫਲ ਮਾਰਗ-ਦਰਸ਼ਨ ਅਤੇ ਮਨੋਰੰਜਨ ਲਈ ਦਿੱਤੇ ਜਾਂਦੇ ਹਨ। ਇਹ ਡਾਕਟਰੀ, ਕਾਨੂੰਨੀ ਜਾਂ ਵਿੱਤੀ ਸਲਾਹ ਨਹੀਂ ਹਨ।",
}

# app/stay_strip.py TEXT["pa"] — the 'Stay in touch' strip at the foot of the pages  [8]
STAY_STRIP = {
    # EN: Stay in touch
    "head": "ਸਾਡੇ ਨਾਲ ਜੁੜੇ ਰਹੋ",
    # EN: Get today's panchang on your phone every morning
    "push": "ਹਰ ਸਵੇਰ ਆਪਣੇ ਫ਼ੋਨ ’ਤੇ ਅੱਜ ਦਾ ਪੰਚਾਂਗ ਪਾਓ",
    # EN: Turning on…
    "busy": "ਚਾਲੂ ਹੋ ਰਿਹਾ ਹੈ…",
    # EN: Done — you will get it every morning.
    "on": "ਹੋ ਗਿਆ — ਤੁਹਾਨੂੰ ਹਰ ਸਵੇਰ ਮਿਲੇਗਾ।",
    # EN: Could not turn on alerts. Please try again.
    "err": "ਅਲਰਟ ਚਾਲੂ ਨਹੀਂ ਹੋ ਸਕੇ। ਕਿਰਪਾ ਕਰਕੇ ਦੁਬਾਰਾ ਕੋਸ਼ਿਸ਼ ਕਰੋ।",
    # EN: Notifications are blocked for this site in your browser settings.
    "denied": "ਤੁਹਾਡੇ ਬ੍ਰਾਊਜ਼ਰ ਦੀਆਂ ਸੈਟਿੰਗਾਂ ਵਿੱਚ ਇਸ ਸਾਈਟ ਲਈ ਨੋਟੀਫ਼ਿਕੇਸ਼ਨ ਬੰਦ ਹਨ।",
    # EN: Join our WhatsApp channel
    "channel": "ਸਾਡੇ WhatsApp ਚੈਨਲ ਨਾਲ ਜੁੜੋ",
    # EN: Share this page on WhatsApp
    "share": "ਇਸ ਪੰਨੇ ਨੂੰ WhatsApp ’ਤੇ ਸਾਂਝਾ ਕਰੋ",
}

# app/seo_city_names.py CITIES["pa"] — the 114 cities as that language's newspapers spell them (key = URL slug)  [114]
CITY_NAMES = {
    # EN: New Delhi
    "new-delhi": "ਨਵੀਂ ਦਿੱਲੀ",
    # EN: Mumbai
    "mumbai": "ਮੁੰਬਈ",
    # EN: Kolkata
    "kolkata": "ਕੋਲਕਾਤਾ",
    # EN: Chennai
    "chennai": "ਚੇਨਈ",
    # EN: Bengaluru
    "bengaluru": "ਬੰਗਲੁਰੂ",
    # EN: Hyderabad
    "hyderabad": "ਹੈਦਰਾਬਾਦ",
    # EN: Ahmedabad
    "ahmedabad": "ਅਹਿਮਦਾਬਾਦ",
    # EN: Pune
    "pune": "ਪੁਣੇ",
    # EN: Jaipur
    "jaipur": "ਜੈਪੁਰ",
    # EN: Lucknow
    "lucknow": "ਲਖਨਊ",
    # EN: Kanpur
    "kanpur": "ਕਾਨਪੁਰ",
    # EN: Nagpur
    "nagpur": "ਨਾਗਪੁਰ",
    # EN: Indore
    "indore": "ਇੰਦੌਰ",
    # EN: Bhopal
    "bhopal": "ਭੋਪਾਲ",
    # EN: Patna
    "patna": "ਪਟਨਾ",
    # EN: Varanasi
    "varanasi": "ਵਾਰਾਣਸੀ",
    # EN: Prayagraj
    "prayagraj": "ਪ੍ਰਯਾਗਰਾਜ",
    # EN: Surat
    "surat": "ਸੂਰਤ",
    # EN: Vadodara
    "vadodara": "ਵਡੋਦਰਾ",
    # EN: Chandigarh
    "chandigarh": "ਚੰਡੀਗੜ੍ਹ",
    # EN: Amritsar
    "amritsar": "ਅੰਮ੍ਰਿਤਸਰ",
    # EN: Dehradun
    "dehradun": "ਦੇਹਰਾਦੂਨ",
    # EN: Haridwar
    "haridwar": "ਹਰਿਦੁਆਰ",
    # EN: Noida
    "noida": "ਨੋਇਡਾ",
    # EN: Gurugram
    "gurugram": "ਗੁਰੂਗ੍ਰਾਮ",
    # EN: Bhubaneswar
    "bhubaneswar": "ਭੁਵਨੇਸ਼ਵਰ",
    # EN: Guwahati
    "guwahati": "ਗੁਹਾਟੀ",
    # EN: Ranchi
    "ranchi": "ਰਾਂਚੀ",
    # EN: Kochi
    "kochi": "ਕੋਚੀ",
    # EN: Visakhapatnam
    "visakhapatnam": "ਵਿਸ਼ਾਖਾਪਟਨਮ",
    # EN: Thane
    "thane": "ਠਾਣੇ",
    # EN: Navi Mumbai
    "navi-mumbai": "ਨਵੀਂ ਮੁੰਬਈ",
    # EN: Nashik
    "nashik": "ਨਾਸ਼ਿਕ",
    # EN: Chhatrapati Sambhajinagar
    "chhatrapati-sambhajinagar": "ਛਤਰਪਤੀ ਸੰਭਾਜੀਨਗਰ",
    # EN: Solapur
    "solapur": "ਸ਼ੋਲਾਪੁਰ",
    # EN: Kolhapur
    "kolhapur": "ਕੋਲਹਾਪੁਰ",
    # EN: Amravati
    "amravati": "ਅਮਰਾਵਤੀ",
    # EN: Shirdi
    "shirdi": "ਸ਼ਿਰਡੀ",
    # EN: Rajkot
    "rajkot": "ਰਾਜਕੋਟ",
    # EN: Bhavnagar
    "bhavnagar": "ਭਾਵਨਗਰ",
    # EN: Jamnagar
    "jamnagar": "ਜਾਮਨਗਰ",
    # EN: Gandhinagar
    "gandhinagar": "ਗਾਂਧੀਨਗਰ",
    # EN: Dwarka
    "dwarka": "ਦਵਾਰਕਾ",
    # EN: Somnath
    "somnath": "ਸੋਮਨਾਥ",
    # EN: Jodhpur
    "jodhpur": "ਜੋਧਪੁਰ",
    # EN: Udaipur
    "udaipur": "ਉਦੈਪੁਰ",
    # EN: Kota
    "kota": "ਕੋਟਾ",
    # EN: Ajmer
    "ajmer": "ਅਜਮੇਰ",
    # EN: Bikaner
    "bikaner": "ਬੀਕਾਨੇਰ",
    # EN: Agra
    "agra": "ਆਗਰਾ",
    # EN: Ghaziabad
    "ghaziabad": "ਗਾਜ਼ੀਆਬਾਦ",
    # EN: Meerut
    "meerut": "ਮੇਰਠ",
    # EN: Bareilly
    "bareilly": "ਬਰੇਲੀ",
    # EN: Aligarh
    "aligarh": "ਅਲੀਗੜ੍ਹ",
    # EN: Moradabad
    "moradabad": "ਮੁਰਾਦਾਬਾਦ",
    # EN: Gorakhpur
    "gorakhpur": "ਗੋਰਖਪੁਰ",
    # EN: Saharanpur
    "saharanpur": "ਸਹਾਰਨਪੁਰ",
    # EN: Ayodhya
    "ayodhya": "ਅਯੁੱਧਿਆ",
    # EN: Mathura
    "mathura": "ਮਥੁਰਾ",
    # EN: Vrindavan
    "vrindavan": "ਵ੍ਰਿੰਦਾਵਨ",
    # EN: Jhansi
    "jhansi": "ਝਾਂਸੀ",
    # EN: Faridabad
    "faridabad": "ਫ਼ਰੀਦਾਬਾਦ",
    # EN: Kurukshetra
    "kurukshetra": "ਕੁਰੂਕਸ਼ੇਤਰ",
    # EN: Ludhiana
    "ludhiana": "ਲੁਧਿਆਣਾ",
    # EN: Jalandhar
    "jalandhar": "ਜਲੰਧਰ",
    # EN: Patiala
    "patiala": "ਪਟਿਆਲਾ",
    # EN: Rishikesh
    "rishikesh": "ਰਿਸ਼ੀਕੇਸ਼",
    # EN: Shimla
    "shimla": "ਸ਼ਿਮਲਾ",
    # EN: Jammu
    "jammu": "ਜੰਮੂ",
    # EN: Srinagar
    "srinagar": "ਸ੍ਰੀਨਗਰ",
    # EN: Katra
    "katra": "ਕਟੜਾ",
    # EN: Gwalior
    "gwalior": "ਗਵਾਲੀਅਰ",
    # EN: Jabalpur
    "jabalpur": "ਜਬਲਪੁਰ",
    # EN: Ujjain
    "ujjain": "ਉੱਜੈਨ",
    # EN: Raipur
    "raipur": "ਰਾਇਪੁਰ",
    # EN: Bhilai
    "bhilai": "ਭਿਲਾਈ",
    # EN: Gaya
    "gaya": "ਗਯਾ",
    # EN: Bhagalpur
    "bhagalpur": "ਭਾਗਲਪੁਰ",
    # EN: Muzaffarpur
    "muzaffarpur": "ਮੁਜ਼ੱਫ਼ਰਪੁਰ",
    # EN: Jamshedpur
    "jamshedpur": "ਜਮਸ਼ੇਦਪੁਰ",
    # EN: Dhanbad
    "dhanbad": "ਧਨਬਾਦ",
    # EN: Deoghar
    "deoghar": "ਦੇਵਘਰ",
    # EN: Howrah
    "howrah": "ਹਾਵੜਾ",
    # EN: Asansol
    "asansol": "ਆਸਨਸੋਲ",
    # EN: Siliguri
    "siliguri": "ਸਿਲੀਗੁੜੀ",
    # EN: Cuttack
    "cuttack": "ਕਟਕ",
    # EN: Puri
    "puri": "ਪੁਰੀ",
    # EN: Coimbatore
    "coimbatore": "ਕੋਇੰਬਟੂਰ",
    # EN: Madurai
    "madurai": "ਮਦੁਰਈ",
    # EN: Tiruchirappalli
    "tiruchirappalli": "ਤਿਰੂਚਿਰਾਪੱਲੀ",
    # EN: Salem
    "salem": "ਸਲੇਮ",
    # EN: Rameswaram
    "rameswaram": "ਰਾਮੇਸ਼ਵਰਮ",
    # EN: Thiruvananthapuram
    "thiruvananthapuram": "ਤਿਰੂਵਨੰਤਪੁਰਮ",
    # EN: Kozhikode
    "kozhikode": "ਕੋਜ਼ੀਕੋਡ",
    # EN: Thrissur
    "thrissur": "ਤ੍ਰਿਸ਼ੂਰ",
    # EN: Kollam
    "kollam": "ਕੋਲਮ",
    # EN: Kannur
    "kannur": "ਕੰਨੂਰ",
    # EN: Malappuram
    "malappuram": "ਮਲੱਪੁਰਮ",
    # EN: Mysuru
    "mysuru": "ਮੈਸੂਰ",
    # EN: Mangaluru
    "mangaluru": "ਮੰਗਲੁਰੂ",
    # EN: Hubballi
    "hubballi": "ਹੁਬਲੀ",
    # EN: Warangal
    "warangal": "ਵਾਰੰਗਲ",
    # EN: Vijayawada
    "vijayawada": "ਵਿਜੈਵਾੜਾ",
    # EN: Tirupati
    "tirupati": "ਤਿਰੂਪਤੀ",
    # EN: Guntur
    "guntur": "ਗੁੰਟੂਰ",
    # EN: Panaji
    "panaji": "ਪਣਜੀ",
    # EN: Shillong
    "shillong": "ਸ਼ਿਲਾਂਗ",
    # EN: Imphal
    "imphal": "ਇੰਫ਼ਾਲ",
    # EN: Agartala
    "agartala": "ਅਗਰਤਲਾ",
    # EN: Gangtok
    "gangtok": "ਗੰਗਟੋਕ",
    # EN: Aizawl
    "aizawl": "ਆਈਜ਼ੋਲ",
    # EN: Kohima
    "kohima": "ਕੋਹਿਮਾ",
    # EN: Itanagar
    "itanagar": "ਈਟਾਨਗਰ",
    # EN: Puducherry
    "puducherry": "ਪੁਡੂਚੇਰੀ",
}

# app/seo_city_names.py STATES["pa"] — the states and union territories (key = English state name)  [32]
STATE_NAMES = {
    # EN: Andhra Pradesh
    "Andhra Pradesh": "ਆਂਧਰਾ ਪ੍ਰਦੇਸ਼",
    # EN: Arunachal Pradesh
    "Arunachal Pradesh": "ਅਰੁਣਾਚਲ ਪ੍ਰਦੇਸ਼",
    # EN: Assam
    "Assam": "ਅਸਾਮ",
    # EN: Bihar
    "Bihar": "ਬਿਹਾਰ",
    # EN: Chandigarh
    "Chandigarh": "ਚੰਡੀਗੜ੍ਹ",
    # EN: Chhattisgarh
    "Chhattisgarh": "ਛੱਤੀਸਗੜ੍ਹ",
    # EN: Delhi
    "Delhi": "ਦਿੱਲੀ",
    # EN: Goa
    "Goa": "ਗੋਆ",
    # EN: Gujarat
    "Gujarat": "ਗੁਜਰਾਤ",
    # EN: Haryana
    "Haryana": "ਹਰਿਆਣਾ",
    # EN: Himachal Pradesh
    "Himachal Pradesh": "ਹਿਮਾਚਲ ਪ੍ਰਦੇਸ਼",
    # EN: Jammu and Kashmir
    "Jammu and Kashmir": "ਜੰਮੂ ਅਤੇ ਕਸ਼ਮੀਰ",
    # EN: Jharkhand
    "Jharkhand": "ਝਾਰਖੰਡ",
    # EN: Karnataka
    "Karnataka": "ਕਰਨਾਟਕ",
    # EN: Kerala
    "Kerala": "ਕੇਰਲ",
    # EN: Madhya Pradesh
    "Madhya Pradesh": "ਮੱਧ ਪ੍ਰਦੇਸ਼",
    # EN: Maharashtra
    "Maharashtra": "ਮਹਾਰਾਸ਼ਟਰ",
    # EN: Manipur
    "Manipur": "ਮਨੀਪੁਰ",
    # EN: Meghalaya
    "Meghalaya": "ਮੇਘਾਲਿਆ",
    # EN: Mizoram
    "Mizoram": "ਮਿਜ਼ੋਰਮ",
    # EN: Nagaland
    "Nagaland": "ਨਾਗਾਲੈਂਡ",
    # EN: Odisha
    "Odisha": "ਓਡੀਸ਼ਾ",
    # EN: Puducherry
    "Puducherry": "ਪੁਡੂਚੇਰੀ",
    # EN: Punjab
    "Punjab": "ਪੰਜਾਬ",
    # EN: Rajasthan
    "Rajasthan": "ਰਾਜਸਥਾਨ",
    # EN: Sikkim
    "Sikkim": "ਸਿੱਕਮ",
    # EN: Tamil Nadu
    "Tamil Nadu": "ਤਾਮਿਲ ਨਾਡੂ",
    # EN: Telangana
    "Telangana": "ਤੇਲੰਗਾਨਾ",
    # EN: Tripura
    "Tripura": "ਤ੍ਰਿਪੁਰਾ",
    # EN: Uttar Pradesh
    "Uttar Pradesh": "ਉੱਤਰ ਪ੍ਰਦੇਸ਼",
    # EN: Uttarakhand
    "Uttarakhand": "ਉੱਤਰਾਖੰਡ",
    # EN: West Bengal
    "West Bengal": "ਪੱਛਮੀ ਬੰਗਾਲ",
}

# app/astro/choghadiya.py CHOGHADIYA_INFO["pa"] — one-line description of each of the seven choghadiya slots  [7]
CHOGHADIYA_DESC = {
    # EN: Best time for all ceremonies, investments, agreements, and starting important endeavors.
    "Amrit": "ਸਾਰੇ ਸੰਸਕਾਰਾਂ, ਨਿਵੇਸ਼ਾਂ, ਸਮਝੌਤਿਆਂ ਅਤੇ ਅਹਿਮ ਕੰਮ ਸ਼ੁਰੂ ਕਰਨ ਲਈ ਸਭ ਤੋਂ ਵਧੀਆ ਸਮਾਂ।",
    # EN: Highly auspicious for ceremonies, religious rituals, education, and purchasing property.
    "Shubh": "ਸੰਸਕਾਰਾਂ, ਧਾਰਮਿਕ ਕਰਮਾਂ, ਪੜ੍ਹਾਈ ਅਤੇ ਜਾਇਦਾਦ ਖ਼ਰੀਦਣ ਲਈ ਬਹੁਤ ਸ਼ੁਭ।",
    # EN: Favorable for business, trade, financial transactions, launching products, and interviews.
    "Labh": "ਕਾਰੋਬਾਰ, ਵਪਾਰ, ਲੈਣ-ਦੇਣ, ਨਵੀਂ ਚੀਜ਼ ਸ਼ੁਰੂ ਕਰਨ ਅਤੇ ਇੰਟਰਵਿਊ ਲਈ ਅਨੁਕੂਲ।",
    # EN: Neutral. Excellent for journeys, travel, vehicle purchases, and shifting places.
    "Char": "ਮੱਧਮ। ਯਾਤਰਾ, ਸਫ਼ਰ, ਗੱਡੀ ਖ਼ਰੀਦਣ ਅਤੇ ਟਿਕਾਣਾ ਬਦਲਣ ਲਈ ਬਹੁਤ ਵਧੀਆ।",
    # EN: Inauspicious. Avoid medical procedures or conflict. Only suitable for competitive sports
    #     or defeating rivals.
    "Rog": "ਅਸ਼ੁਭ। ਡਾਕਟਰੀ ਇਲਾਜ ਜਾਂ ਝਗੜੇ ਤੋਂ ਬਚੋ। ਸਿਰਫ਼ ਮੁਕਾਬਲੇ ਵਾਲੀਆਂ ਖੇਡਾਂ ਜਾਂ ਵਿਰੋਧੀਆਂ ਨੂੰ ਹਰਾਉਣ ਲਈ ਠੀਕ।",
    # EN: Inauspicious. Ruled by Saturn; causes delays and setbacks. Avoid new ventures or signing
    #     documents.
    "Kaal": "ਅਸ਼ੁਭ। ਸ਼ਨੀ ਦੇ ਅਧੀਨ; ਦੇਰੀ ਅਤੇ ਰੁਕਾਵਟਾਂ ਪਾਉਂਦਾ ਹੈ। ਨਵੇਂ ਕੰਮ ਜਾਂ ਦਸਤਾਵੇਜ਼ਾਂ ’ਤੇ ਦਸਤਖ਼ਤ ਤੋਂ ਬਚੋ।",
    # EN: Inauspicious. Causes restlessness and anxiety. Favorable only for government filings or
    #     official duties.
    "Udveg": "ਅਸ਼ੁਭ। ਬੇਚੈਨੀ ਅਤੇ ਚਿੰਤਾ ਪੈਦਾ ਕਰਦਾ ਹੈ। ਸਿਰਫ਼ ਸਰਕਾਰੀ ਕਾਗਜ਼ਾਂ ਜਾਂ ਦਫ਼ਤਰੀ ਡਿਊਟੀਆਂ ਲਈ ਅਨੁਕੂਲ।",
}

# ----------------------------------------------------------------------------
# rashifal  /rashifal and /rashifal/<sign>
# ----------------------------------------------------------------------------

# app/rashifal_text.py TEXT["pa"] — page text of /rashifal and /rashifal/<sign>  [63]
RASHIFAL_TEXT = {
    # EN: {house} house
    # keep: {house}
    "house_short": "{house} ਭਾਵ",
    # EN: (retrograde)
    "rx": "(ਵੱਕਰੀ)",
    # EN: Moon
    "planet.Moon": "ਚੰਦਰਮਾ",
    # EN: Saturn
    "planet.Saturn": "ਸ਼ਨੀ",
    # EN: Jupiter
    "planet.Jupiter": "ਬ੍ਰਿਹਸਪਤੀ",
    # EN: Rahu
    "planet.Rahu": "ਰਾਹੂ",
    # EN: Ketu
    "planet.Ketu": "ਕੇਤੂ",
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
    "crumb_root": "ਰਾਸ਼ੀਫਲ",
    # EN: hi
    "sub_lang": 'pa',
    # EN: {name} Rashifal Today, {date_short} — {english} Daily Horoscope | {brand}
    # keep: {brand} {local}
    # may also use: {date_short} {date}
    "s.title": "{local} ਰਾਸ਼ੀਫਲ ਅੱਜ, {date_short} — ਅੱਜ ਦਾ ਰੋਜ਼ਾਨਾ ਫਲਾਦੇਸ਼ | {brand}",
    # EN: {name} ({english} Moon sign) rashifal for {weekday}, {date}: the Moon transits your
    #     {house} house — {tone_lower}. Plus Saturn, Jupiter and Rahu–Ketu transits, Sade Sati
    #     status and today's tithi, computed from the sidereal sky.
    # keep: {date} {house} {local} {tone} {weekday}
    "s.desc": "{local} ਰਾਸ਼ੀ ਦਾ {weekday}, {date} ਦਾ ਰਾਸ਼ੀਫਲ: ਚੰਦਰਮਾ ਤੁਹਾਡੀ ਰਾਸ਼ੀ ਤੋਂ {house} ਭਾਵ ਵਿੱਚ ਹੈ — {tone}। ਨਾਲ ਸ਼ਨੀ, ਬ੍ਰਿਹਸਪਤੀ ਅਤੇ ਰਾਹੂ-ਕੇਤੂ ਦਾ ਗੋਚਰ, ਸਾੜ੍ਹਸਾਤੀ ਦੀ ਸਥਿਤੀ ਅਤੇ ਅੱਜ ਦੀ ਤਿਥੀ, ਨਿਰਯਨ ਗਣਨਾ ਨਾਲ।",
    # EN: {name} Rashifal Today — {english} Daily Horoscope
    # keep: {local}
    "s.h1": "{local} ਰਾਸ਼ੀ ਦਾ ਅੱਜ ਦਾ ਰਾਸ਼ੀਫਲ",
    # EN: आज का {name_hi} राशिफल
    # may also use: {local}
    "s.sub": "{local} ਰਾਸ਼ੀ · ਰੋਜ਼ਾਨਾ ਰਾਸ਼ੀਫਲ",
    # EN: the Moon is in your {house} house from {name}.
    # keep: {house}
    "s.summary": "ਚੰਦਰਮਾ ਤੁਹਾਡੀ ਰਾਸ਼ੀ ਤੋਂ {house} ਭਾਵ ਵਿੱਚ ਹੈ।",
    # EN: About {name} rashi — traits, nakshatras and name letters
    # keep: {local}
    "s.about_rashi": "{local} ਰਾਸ਼ੀ ਬਾਰੇ — ਸੁਭਾਅ, ਨਕਸ਼ਤਰ ਅਤੇ ਨਾਂ ਦੇ ਅੱਖਰ",
    # EN: Today's Moon transit (Chandra gochar)
    "moon.head": "ਅੱਜ ਦਾ ਚੰਦਰਮਾ ਗੋਚਰ (ਚੰਦਰ ਗੋਚਰ)",
    # EN: The Moon is in {sign} all day — your {house} house.
    # keep: {house} {sign}
    "moon.allday": "ਚੰਦਰਮਾ ਸਾਰਾ ਦਿਨ {sign} ਵਿੱਚ ਹੈ — ਤੁਹਾਡਾ {house} ਭਾਵ।",
    # EN: <strong>Until {time} IST:</strong> the Moon is in {sign} — your {house} house.
    # keep: {house} {sign} {time}
    "moon.until": "<strong>{time} IST ਤੱਕ:</strong> ਚੰਦਰਮਾ {sign} ਵਿੱਚ ਹੈ — ਤੁਹਾਡਾ {house} ਭਾਵ।",
    # EN: <strong>From {time} IST:</strong> the Moon enters {sign} — your {house} house.
    # keep: {house} {sign} {time}
    "moon.from": "<strong>{time} IST ਤੋਂ:</strong> ਚੰਦਰਮਾ {sign} ਵਿੱਚ ਆਉਂਦਾ ਹੈ — ਤੁਹਾਡਾ {house} ਭਾਵ।",
    # EN: <p>The Moon changes sign during the day, so the day reads in two parts.</p>
    "moon.two": "<p>ਚੰਦਰਮਾ ਦਿਨ ਵਿੱਚ ਰਾਸ਼ੀ ਬਦਲਦਾ ਹੈ, ਇਸ ਲਈ ਦਿਨ ਦੋ ਹਿੱਸਿਆਂ ਵਿੱਚ ਪੜ੍ਹਿਆ ਜਾਂਦਾ ਹੈ।</p>",
    # EN: The longer backdrop: slow transits
    "back.head": "ਲੰਮੀ ਪਿੱਠਭੂਮੀ: ਹੌਲੀ ਚੱਲਣ ਵਾਲੇ ਗੋਚਰ",
    # EN: <p>These planets stay in one sign for months or years, so they set the background against
    #     which each day plays out.</p>
    "back.intro": "<p>ਇਹ ਗ੍ਰਹਿ ਮਹੀਨਿਆਂ ਜਾਂ ਸਾਲਾਂ ਤੱਕ ਇੱਕੋ ਰਾਸ਼ੀ ਵਿੱਚ ਰਹਿੰਦੇ ਹਨ, ਇਸ ਲਈ ਇਹ ਉਹ ਪਿੱਠਭੂਮੀ ਤੈਅ ਕਰਦੇ ਹਨ ਜਿਸ ਵਿੱਚ ਹਰ ਦਿਨ ਬੀਤਦਾ ਹੈ।</p>",
    # EN: {sign}{rx} · {house} house
    # keep: {house} {rx} {sign}
    "back.where": "{sign}{rx} · {house} ਭਾਵ",
    # EN: first (rising)
    "phase.1": "ਪਹਿਲਾ (ਚੜ੍ਹਦਾ)",
    # EN: second (peak)
    "phase.2": "ਦੂਜਾ (ਸਿਖ਼ਰ)",
    # EN: third (setting)
    "phase.3": "ਤੀਜਾ (ਢਲਦਾ)",
    # EN: <strong>Sade Sati is running</strong> — the {phase} phase. It is a slow, disciplining
    #     period rather than something to fear; steady routine, service and patience make it
    #     lighter.
    # keep: {phase}
    "sade.running": "<strong>ਸਾੜ੍ਹਸਾਤੀ ਚੱਲ ਰਹੀ ਹੈ</strong> — {phase} ਪੜਾਅ। ਇਹ ਡਰਨ ਵਾਲੀ ਗੱਲ ਨਹੀਂ, ਸਗੋਂ ਹੌਲੀ ਅਤੇ ਅਨੁਸ਼ਾਸਨ ਸਿਖਾਉਣ ਵਾਲਾ ਸਮਾਂ ਹੈ; ਪੱਕਾ ਰੋਜ਼ਮਰ੍ਹਾ, ਸੇਵਾ ਅਤੇ ਸਬਰ ਇਸ ਨੂੰ ਹਲਕਾ ਕਰ ਦਿੰਦੇ ਹਨ।",
    # EN: <strong>No Sade Sati</strong>, but Saturn's Dhaiya is running (see above).
    "sade.dhaiya": "<strong>ਸਾੜ੍ਹਸਾਤੀ ਨਹੀਂ ਹੈ</strong>, ਪਰ ਸ਼ਨੀ ਦੀ ਢੱਈਆ ਚੱਲ ਰਹੀ ਹੈ (ਉੱਪਰ ਵੇਖੋ)।",
    # EN: <strong>No Sade Sati</strong> — Saturn is not in the 12th, 1st or 2nd from your sign.
    "sade.none": "<strong>ਸਾੜ੍ਹਸਾਤੀ ਨਹੀਂ ਹੈ</strong> — ਸ਼ਨੀ ਤੁਹਾਡੀ ਰਾਸ਼ੀ ਤੋਂ ਬਾਰ੍ਹਵੇਂ, ਪਹਿਲੇ ਜਾਂ ਦੂਜੇ ਭਾਵ ਵਿੱਚ ਨਹੀਂ ਹੈ।",
    # EN: <h2>Today's Panchang</h2><p>At sunrise in New Delhi it is <strong>{paksha}
    #     {tithi}</strong> tithi with the Moon in <strong>{nakshatra}</strong> nakshatra. Rahu Kaal,
    #     sunrise and the full almanac are on <a href="/panchang">today's Panchang</a>.</p>
    # keep: {nakshatra} {tithi}
    # may also use: {paksha_full} {paksha}
    "panchang": "<h2>ਅੱਜ ਦਾ ਪੰਚਾਂਗ</h2><p>ਨਵੀਂ ਦਿੱਲੀ ਵਿੱਚ ਸੂਰਜ ਚੜ੍ਹਨ ਵੇਲੇ <strong>{paksha} {tithi}</strong> ਤਿਥੀ ਹੈ ਅਤੇ ਚੰਦਰਮਾ <strong>{nakshatra}</strong> ਨਕਸ਼ਤਰ ਵਿੱਚ ਹੈ। ਰਾਹੂ ਕਾਲ, ਸੂਰਜ ਚੜ੍ਹਨ ਦਾ ਸਮਾਂ ਅਤੇ ਪੂਰਾ ਪੰਚਾਂਗ <a href=\"/panchang\">ਅੱਜ ਦੇ ਪੰਚਾਂਗ</a> ’ਤੇ ਹੈ।</p>",
    # EN: <p class="note">This rashifal is read from your Moon sign alone — the same for everyone
    #     born with the Moon in that sign. A personal reading uses your full birth chart: the
    #     ascendant, your running dasha and the ashtakavarga strength of each transit. Not sure of
    #     your Moon sign (rashi)? It is the first thing your free kundali shows — it is usually not
    #     your Western sun sign.</p>
    "personal": "<p class=\"note\">ਇਹ ਰਾਸ਼ੀਫਲ ਸਿਰਫ਼ ਤੁਹਾਡੀ ਚੰਦਰ ਰਾਸ਼ੀ ਤੋਂ ਪੜ੍ਹਿਆ ਗਿਆ ਹੈ — ਉਸ ਰਾਸ਼ੀ ਵਿੱਚ ਚੰਦਰਮਾ ਨਾਲ ਜਨਮੇ ਹਰ ਕਿਸੇ ਲਈ ਇੱਕੋ ਜਿਹਾ। ਨਿੱਜੀ ਫਲਾਦੇਸ਼ ਤੁਹਾਡੀ ਪੂਰੀ ਜਨਮ ਕੁੰਡਲੀ ਵਰਤਦਾ ਹੈ: ਲਗਨ, ਤੁਹਾਡੀ ਚੱਲ ਰਹੀ ਦਸ਼ਾ ਅਤੇ ਹਰ ਗੋਚਰ ਦਾ ਅਸ਼ਟਕਵਰਗ ਬਲ। ਆਪਣੀ ਚੰਦਰ ਰਾਸ਼ੀ ਦਾ ਪੱਕਾ ਨਹੀਂ ਪਤਾ? ਇਹ ਤੁਹਾਡੀ ਮੁਫ਼ਤ ਕੁੰਡਲੀ ਦੀ ਪਹਿਲੀ ਚੀਜ਼ ਹੈ — ਇਹ ਆਮ ਤੌਰ ’ਤੇ ਤੁਹਾਡੀ ਪੱਛਮੀ ਸੂਰਜ ਰਾਸ਼ੀ ਨਹੀਂ ਹੁੰਦੀ।</p>",
    # EN: Get your free kundali — then ask a question about your own chart
    "cta": "ਆਪਣੀ ਮੁਫ਼ਤ ਕੁੰਡਲੀ ਲਵੋ — ਫਿਰ ਆਪਣੀ ਕੁੰਡਲੀ ਬਾਰੇ ਸਵਾਲ ਪੁੱਛੋ",
    # EN: Today's Rashifal for every sign
    "signs.head": "ਹਰ ਰਾਸ਼ੀ ਲਈ ਅੱਜ ਦਾ ਰਾਸ਼ੀਫਲ",
    # EN: More free tools
    "more.head": "ਹੋਰ ਮੁਫ਼ਤ ਟੂਲ",
    # EN: <h2>How this is calculated</h2><p>Planet positions are computed for today (IST) with the
    #     Swiss Ephemeris in the sidereal zodiac (Lahiri ayanamsa) — the same positions our kundali
    #     and panchang use. Houses are counted from your Moon sign, as in classical gochar. Which
    #     houses are favourable follows the scheme of Varahamihira's Brihat Samhita (ch. 104) and
    #     Mantreswara's Phaladeepika (ch. 26): the Moon is favourable in the 1st, 3rd, 6th, 7th,
    #     10th and 11th; Saturn, Rahu and Ketu in the 3rd, 6th and 11th; Jupiter in the 2nd, 5th,
    #     7th, 9th and 11th.</p>
    "method": "<h2>ਇਹ ਕਿਵੇਂ ਗਿਣਿਆ ਜਾਂਦਾ ਹੈ</h2><p>ਗ੍ਰਹਿਆਂ ਦੀਆਂ ਸਥਿਤੀਆਂ ਅੱਜ (IST) ਲਈ ਸਵਿਸ ਐਫ਼ੇਮੇਰਿਸ ਨਾਲ ਨਿਰਯਨ ਰਾਸ਼ੀ ਚੱਕਰ (ਲਾਹਿੜੀ ਅਯਨਾਂਸ਼) ਵਿੱਚ ਗਿਣੀਆਂ ਜਾਂਦੀਆਂ ਹਨ — ਉਹੀ ਸਥਿਤੀਆਂ ਜੋ ਸਾਡੀ ਕੁੰਡਲੀ ਅਤੇ ਪੰਚਾਂਗ ਵਰਤਦੇ ਹਨ। ਭਾਵ ਸ਼ਾਸਤਰੀ ਗੋਚਰ ਵਾਂਗ ਤੁਹਾਡੀ ਚੰਦਰ ਰਾਸ਼ੀ ਤੋਂ ਗਿਣੇ ਜਾਂਦੇ ਹਨ। ਕਿਹੜੇ ਭਾਵ ਸ਼ੁਭ ਹਨ, ਇਹ ਵਰਾਹਮਿਹਿਰ ਦੀ ਬ੍ਰਿਹਤ ਸੰਹਿਤਾ (ਅਧਿਆਇ 104) ਅਤੇ ਮੰਤ੍ਰੇਸ਼ਵਰ ਦੀ ਫਲਦੀਪਿਕਾ (ਅਧਿਆਇ 26) ਦੀ ਵਿਧੀ ਮੁਤਾਬਕ ਹੈ: ਚੰਦਰਮਾ ਪਹਿਲੇ, ਤੀਜੇ, ਛੇਵੇਂ, ਸੱਤਵੇਂ, ਦਸਵੇਂ ਅਤੇ ਗਿਆਰ੍ਹਵੇਂ ਵਿੱਚ ਸ਼ੁਭ ਹੈ; ਸ਼ਨੀ, ਰਾਹੂ ਅਤੇ ਕੇਤੂ ਤੀਜੇ, ਛੇਵੇਂ ਅਤੇ ਗਿਆਰ੍ਹਵੇਂ ਵਿੱਚ; ਬ੍ਰਿਹਸਪਤੀ ਦੂਜੇ, ਪੰਜਵੇਂ, ਸੱਤਵੇਂ, ਨੌਵੇਂ ਅਤੇ ਗਿਆਰ੍ਹਵੇਂ ਵਿੱਚ।</p>",
    # EN: Aaj Ka Rashifal, {date_short} — Today's Horoscope for All 12 Signs | {brand}
    # keep: {brand}
    # may also use: {date_short} {date}
    "i.title": "ਅੱਜ ਦਾ ਰਾਸ਼ੀਫਲ, {date_short} — ਸਾਰੀਆਂ 12 ਰਾਸ਼ੀਆਂ ਦਾ ਅੱਜ ਦਾ ਫਲਾਦੇਸ਼ | {brand}",
    # EN: Today's rashifal for {weekday}, {date}: daily horoscope for all 12 Moon signs from Mesh to
    #     Meen — Moon transit, Saturn, Jupiter and Rahu, and Sade Sati, computed from the sidereal
    #     sky.
    # keep: {date} {weekday}
    "i.desc": "{weekday}, {date} ਦਾ ਰਾਸ਼ੀਫਲ: ਮੇਖ ਤੋਂ ਮੀਨ ਤੱਕ ਸਾਰੀਆਂ 12 ਚੰਦਰ ਰਾਸ਼ੀਆਂ ਦਾ ਰੋਜ਼ਾਨਾ ਫਲਾਦੇਸ਼ — ਚੰਦਰਮਾ ਗੋਚਰ, ਸ਼ਨੀ, ਬ੍ਰਿਹਸਪਤੀ ਅਤੇ ਰਾਹੂ, ਅਤੇ ਸਾੜ੍ਹਸਾਤੀ, ਨਿਰਯਨ ਗਣਨਾ ਨਾਲ।",
    # EN: Today's Rashifal — Daily Horoscope
    "i.h1": "ਅੱਜ ਦਾ ਰਾਸ਼ੀਫਲ — ਰੋਜ਼ਾਨਾ ਫਲਾਦੇਸ਼",
    # EN: आज का राशिफल — सभी 12 राशियाँ
    "i.sub": "ਅੱਜ ਦਾ ਰਾਸ਼ੀਫਲ — ਸਾਰੀਆਂ 12 ਰਾਸ਼ੀਆਂ",
    # EN: <p>Rashifal is read from your <strong>Moon sign</strong> (rashi). {moon_text} Saturn is in
    #     {sat_sign}, so Sade Sati is running for {sade_names}.</p>
    # keep: {moon_text} {sade_names} {sat_sign}
    "i.intro": "<p>ਰਾਸ਼ੀਫਲ ਤੁਹਾਡੀ <strong>ਚੰਦਰ ਰਾਸ਼ੀ</strong> ਤੋਂ ਪੜ੍ਹਿਆ ਜਾਂਦਾ ਹੈ। {moon_text} ਸ਼ਨੀ {sat_sign} ਵਿੱਚ ਹੈ, ਇਸ ਲਈ {sade_names} ਲਈ ਸਾੜ੍ਹਸਾਤੀ ਚੱਲ ਰਹੀ ਹੈ।</p>",
    # EN: The Moon is in {now} until {time} IST, then in {next}. The table shows the position for
    #     most of the day.
    # keep: {next} {now} {time}
    "i.moon_two": "ਚੰਦਰਮਾ {time} IST ਤੱਕ {now} ਵਿੱਚ ਹੈ, ਫਿਰ {next} ਵਿੱਚ। ਸਾਰਣੀ ਵਿੱਚ ਦਿਨ ਦੇ ਜ਼ਿਆਦਾਤਰ ਹਿੱਸੇ ਦੀ ਸਥਿਤੀ ਦਿੱਤੀ ਗਈ ਹੈ।",
    # EN: The Moon is in {now} all day.
    # keep: {now}
    "i.moon_one": "ਚੰਦਰਮਾ ਸਾਰਾ ਦਿਨ {now} ਵਿੱਚ ਹੈ।",
    # EN: {name} <small>{english}</small>
    # keep: {local}
    "i.name": "{local}",
    # EN: <small>Sade Sati</small>
    "i.sade": "<small>ਸਾੜ੍ਹਸਾਤੀ</small>",
    # EN: <tr><th>Sign</th><th>Moon in your</th><th>Today</th></tr>
    "i.head_row": "<tr><th>ਰਾਸ਼ੀ</th><th>ਤੁਹਾਡੀ ਰਾਸ਼ੀ ਤੋਂ ਚੰਦਰਮਾ</th><th>ਅੱਜ</th></tr>",
    # EN: Sign not found
    "nf.title": "ਰਾਸ਼ੀ ਨਹੀਂ ਮਿਲੀ",
    # EN: <h1>Sign not found</h1><p>There is no rashi called “{slug}”. Pick your Moon sign
    #     below.</p>
    # keep: {slug}
    "nf.body": "<h1>ਰਾਸ਼ੀ ਨਹੀਂ ਮਿਲੀ</h1><p>“{slug}” ਨਾਂ ਦੀ ਕੋਈ ਰਾਸ਼ੀ ਨਹੀਂ ਹੈ। ਹੇਠਾਂ ਤੋਂ ਆਪਣੀ ਚੰਦਰ ਰਾਸ਼ੀ ਚੁਣੋ।</p>",
    # EN: 1st
    "house.1": "ਪਹਿਲੇ",
    # EN: 2nd
    "house.2": "ਦੂਜੇ",
    # EN: 3rd
    "house.3": "ਤੀਜੇ",
    # EN: 4th
    "house.4": "ਚੌਥੇ",
    # EN: 5th
    "house.5": "ਪੰਜਵੇਂ",
    # EN: 6th
    "house.6": "ਛੇਵੇਂ",
    # EN: 7th
    "house.7": "ਸੱਤਵੇਂ",
    # EN: 8th
    "house.8": "ਅੱਠਵੇਂ",
    # EN: 9th
    "house.9": "ਨੌਵੇਂ",
    # EN: 10th
    "house.10": "ਦਸਵੇਂ",
    # EN: 11th
    "house.11": "ਗਿਆਰ੍ਹਵੇਂ",
    # EN: 12th
    "house.12": "ਬਾਰ੍ਹਵੇਂ",
}

# app/rashifal_text.py MORE_LINKS["pa"] — 'More free tools' links: keep every href, translate the text; the first href is '{twin:en}' (this page in English)  [6]
RASHIFAL_MORE_LINKS = (
    # EN href: {twin:en}
    # EN text: Read in English
    ("{twin:en}", "ਅੰਗਰੇਜ਼ੀ ਵਿੱਚ ਪੜ੍ਹੋ"),
    # EN href: /panchang
    # EN text: Today's Panchang
    ("/panchang", "ਅੱਜ ਦਾ ਪੰਚਾਂਗ"),
    # EN href: /rahu-kaal
    # EN text: Rahu Kaal today
    ("/rahu-kaal", "ਅੱਜ ਦਾ ਰਾਹੂ ਕਾਲ"),
    # EN href: /choghadiya
    # EN text: Choghadiya today
    ("/choghadiya", "ਅੱਜ ਦਾ ਚੌਘੜੀਆ"),
    # EN href: /kundali-milan
    # EN text: Kundali Milan
    ("/kundali-milan", "ਕੁੰਡਲੀ ਮਿਲਾਨ"),
    # EN href: /vrat-tyohar
    # EN text: Today's vrat & festivals
    ("/vrat-tyohar", "ਅੱਜ ਦੇ ਵਰਤ ਅਤੇ ਤਿਉਹਾਰ"),
)

# app/rashifal_text.py TONE_LABEL["pa"] — the three day tones (keys good / mixed / easy)  [3]
RASHIFAL_TONE_LABEL = {
    # EN: Favourable day
    "good": "ਸ਼ੁਭ ਦਿਨ",
    # EN: Mixed day
    "mixed": "ਮਿਲਿਆ-ਜੁਲਿਆ ਦਿਨ",
    # EN: Take it easy
    "easy": "ਸਹਿਜ ਨਾਲ ਚੱਲੋ",
}

# app/rashifal_text.py MOON_HOUSE["pa"] — Moon transit through houses 1-12 (key = house number)  [12]
RASHIFAL_MOON_HOUSE = {
    # EN: The Moon moves through your own sign today (Janma Chandra). Classical texts read this as a
    #     day of comfort and good spirits — good food, warm company and a clear sense of yourself. A
    #     good day to look after your own needs and begin small, personal things.
    1: "ਚੰਦਰਮਾ ਅੱਜ ਤੁਹਾਡੀ ਆਪਣੀ ਰਾਸ਼ੀ ਵਿੱਚੋਂ ਲੰਘ ਰਿਹਾ ਹੈ (ਜਨਮ ਚੰਦਰ)। ਸ਼ਾਸਤਰ ਇਸ ਨੂੰ ਸੁੱਖ-ਆਰਾਮ ਅਤੇ ਚੰਗੇ ਮੂਡ ਦਾ ਦਿਨ ਮੰਨਦੇ ਹਨ — ਚੰਗਾ ਖਾਣਾ, ਮਿੱਠਾ ਸਾਥ ਅਤੇ ਆਪਣੇ ਆਪ ਬਾਰੇ ਸਾਫ਼ ਸਮਝ। ਆਪਣੀਆਂ ਲੋੜਾਂ ਦਾ ਖ਼ਿਆਲ ਰੱਖਣ ਅਤੇ ਛੋਟੇ ਨਿੱਜੀ ਕੰਮ ਸ਼ੁਰੂ ਕਰਨ ਲਈ ਚੰਗਾ ਦਿਨ ਹੈ।",
    # EN: The Moon is in your 2nd house today. Tradition asks for care with money and words —
    #     expenses can creep up and small misunderstandings arise easily. Keep spending planned and
    #     speak gently at home; routine work goes fine.
    2: "ਚੰਦਰਮਾ ਅੱਜ ਤੁਹਾਡੇ ਦੂਜੇ ਭਾਵ ਵਿੱਚ ਹੈ। ਪਰੰਪਰਾ ਪੈਸੇ ਅਤੇ ਬੋਲ-ਚਾਲ ਵਿੱਚ ਸਾਵਧਾਨੀ ਮੰਗਦੀ ਹੈ — ਖ਼ਰਚ ਚੁੱਪਚਾਪ ਵਧ ਸਕਦੇ ਹਨ ਅਤੇ ਛੋਟੀਆਂ ਗ਼ਲਤਫ਼ਹਿਮੀਆਂ ਛੇਤੀ ਪੈਦਾ ਹੋ ਜਾਂਦੀਆਂ ਹਨ। ਖ਼ਰਚ ਯੋਜਨਾ ਨਾਲ ਕਰੋ ਅਤੇ ਘਰ ਵਿੱਚ ਨਰਮੀ ਨਾਲ ਬੋਲੋ; ਰੋਜ਼ ਦੇ ਕੰਮ ਠੀਕ ਚੱਲਣਗੇ।",
    # EN: The Moon in your 3rd house is a favourable transit. Courage and initiative are high,
    #     effort brings results, and contact with siblings, friends and neighbours goes well. A good
    #     day for short trips, calls and pushing a pending task over the line.
    3: "ਚੰਦਰਮਾ ਦਾ ਤੀਜੇ ਭਾਵ ਵਿੱਚ ਹੋਣਾ ਸ਼ੁਭ ਗੋਚਰ ਹੈ। ਹਿੰਮਤ ਅਤੇ ਪਹਿਲ-ਕਦਮੀ ਉੱਚੀ ਹੈ, ਮਿਹਨਤ ਦਾ ਫਲ ਮਿਲਦਾ ਹੈ, ਅਤੇ ਭੈਣ-ਭਰਾਵਾਂ, ਦੋਸਤਾਂ ਤੇ ਗੁਆਂਢੀਆਂ ਨਾਲ ਮੇਲ-ਜੋਲ ਚੰਗਾ ਰਹਿੰਦਾ ਹੈ। ਛੋਟੇ ਸਫ਼ਰਾਂ, ਫ਼ੋਨ ਕਾਲਾਂ ਅਤੇ ਕਿਸੇ ਲਟਕੇ ਹੋਏ ਕੰਮ ਨੂੰ ਨਿਬੇੜਨ ਲਈ ਚੰਗਾ ਦਿਨ ਹੈ।",
    # EN: The Moon in your 4th house can leave the mind a little unsettled — home matters or travel
    #     may feel tiring. Keep the day simple, avoid arguments at home and give yourself some quiet
    #     time; the mood lifts as the Moon moves on.
    4: "ਚੰਦਰਮਾ ਦਾ ਚੌਥੇ ਭਾਵ ਵਿੱਚ ਹੋਣਾ ਮਨ ਨੂੰ ਥੋੜ੍ਹਾ ਬੇਚੈਨ ਰੱਖ ਸਕਦਾ ਹੈ — ਘਰ ਦੇ ਮਾਮਲੇ ਜਾਂ ਸਫ਼ਰ ਥਕਾਊ ਲੱਗ ਸਕਦੇ ਹਨ। ਦਿਨ ਨੂੰ ਸਾਦਾ ਰੱਖੋ, ਘਰ ਵਿੱਚ ਬਹਿਸ ਤੋਂ ਬਚੋ ਅਤੇ ਆਪਣੇ ਲਈ ਥੋੜ੍ਹਾ ਸ਼ਾਂਤ ਸਮਾਂ ਕੱਢੋ; ਚੰਦਰਮਾ ਦੇ ਅੱਗੇ ਵਧਣ ਨਾਲ ਮੂਡ ਸੁਧਰ ਜਾਵੇਗਾ।",
    # EN: The Moon in your 5th house is a mixed transit. Plans may meet small hurdles and the mind
    #     can swing between ideas. Avoid speculative decisions; study, creative work and time with
    #     children are better uses of the day.
    5: "ਚੰਦਰਮਾ ਦਾ ਪੰਜਵੇਂ ਭਾਵ ਵਿੱਚ ਹੋਣਾ ਮਿਲਿਆ-ਜੁਲਿਆ ਗੋਚਰ ਹੈ। ਯੋਜਨਾਵਾਂ ਵਿੱਚ ਛੋਟੀਆਂ ਰੁਕਾਵਟਾਂ ਆ ਸਕਦੀਆਂ ਹਨ ਅਤੇ ਮਨ ਵਿਚਾਰਾਂ ਵਿੱਚ ਡੋਲ ਸਕਦਾ ਹੈ। ਜੋਖਮ ਵਾਲੇ ਫ਼ੈਸਲਿਆਂ ਤੋਂ ਬਚੋ; ਪੜ੍ਹਾਈ, ਰਚਨਾਤਮਕ ਕੰਮ ਅਤੇ ਬੱਚਿਆਂ ਨਾਲ ਸਮਾਂ ਦਿਨ ਦੀ ਚੰਗੀ ਵਰਤੋਂ ਹੈ।",
    # EN: The Moon in your 6th house is one of its best transits. Classical texts promise success
    #     over rivals and obstacles, and the energy to clear a backlog. A good day for competitive
    #     work, settling pending issues and steady routines.
    6: "ਚੰਦਰਮਾ ਦਾ ਛੇਵੇਂ ਭਾਵ ਵਿੱਚ ਹੋਣਾ ਉਸ ਦੇ ਸਭ ਤੋਂ ਵਧੀਆ ਗੋਚਰਾਂ ਵਿੱਚੋਂ ਇੱਕ ਹੈ। ਸ਼ਾਸਤਰ ਵਿਰੋਧੀਆਂ ਅਤੇ ਰੁਕਾਵਟਾਂ ਉੱਤੇ ਜਿੱਤ ਅਤੇ ਜਮ੍ਹਾ ਹੋਏ ਕੰਮ ਨਿਬੇੜਨ ਦੀ ਤਾਕਤ ਦਾ ਵਾਅਦਾ ਕਰਦੇ ਹਨ। ਮੁਕਾਬਲੇ ਵਾਲੇ ਕੰਮ, ਲਟਕੇ ਮਸਲੇ ਸੁਲਝਾਉਣ ਅਤੇ ਪੱਕੇ ਰੁਟੀਨ ਲਈ ਚੰਗਾ ਦਿਨ ਹੈ।",
    # EN: The Moon in your 7th house favours partnership and company. Time with your spouse or
    #     partner, meetings and agreements tend to go smoothly, with comfort and good food. A good
    #     day to reach out and work together.
    7: "ਚੰਦਰਮਾ ਦਾ ਸੱਤਵੇਂ ਭਾਵ ਵਿੱਚ ਹੋਣਾ ਸਾਂਝੇਦਾਰੀ ਅਤੇ ਸਾਥ ਦੇ ਪੱਖ ਵਿੱਚ ਹੈ। ਜੀਵਨ ਸਾਥੀ ਜਾਂ ਸਾਂਝੇਦਾਰ ਨਾਲ ਸਮਾਂ, ਮੀਟਿੰਗਾਂ ਅਤੇ ਸਮਝੌਤੇ ਆਮ ਤੌਰ ’ਤੇ ਸੁਚਾਰੂ ਰਹਿੰਦੇ ਹਨ, ਸੁੱਖ-ਆਰਾਮ ਅਤੇ ਚੰਗੇ ਖਾਣੇ ਸਮੇਤ। ਹੱਥ ਵਧਾਉਣ ਅਤੇ ਮਿਲ ਕੇ ਕੰਮ ਕਰਨ ਲਈ ਚੰਗਾ ਦਿਨ ਹੈ।",
    # EN: The Moon is in your 8th house — the period known as Chandrashtama. Tradition advises
    #     against starting important new things today; unexpected delays are more likely and the
    #     mind can feel anxious. Keep a margin in your schedule, stick to familiar work and be
    #     gentle with yourself — it passes within two to three days.
    8: "ਚੰਦਰਮਾ ਤੁਹਾਡੇ ਅੱਠਵੇਂ ਭਾਵ ਵਿੱਚ ਹੈ — ਜਿਸ ਸਮੇਂ ਨੂੰ ਚੰਦਰਾਸ਼ਟਮ ਕਿਹਾ ਜਾਂਦਾ ਹੈ। ਪਰੰਪਰਾ ਅੱਜ ਕੋਈ ਅਹਿਮ ਨਵੀਂ ਸ਼ੁਰੂਆਤ ਨਾ ਕਰਨ ਦੀ ਸਲਾਹ ਦਿੰਦੀ ਹੈ; ਅਚਾਨਕ ਦੇਰੀਆਂ ਦੀ ਸੰਭਾਵਨਾ ਵੱਧ ਹੈ ਅਤੇ ਮਨ ਚਿੰਤਤ ਹੋ ਸਕਦਾ ਹੈ। ਆਪਣੇ ਪ੍ਰੋਗਰਾਮ ਵਿੱਚ ਗੁੰਜਾਇਸ਼ ਰੱਖੋ, ਜਾਣੇ-ਪਛਾਣੇ ਕੰਮ ਕਰੋ ਅਤੇ ਆਪਣੇ ਨਾਲ ਨਰਮੀ ਨਾਲ ਪੇਸ਼ ਆਓ — ਇਹ ਦੋ-ਤਿੰਨ ਦਿਨਾਂ ਵਿੱਚ ਲੰਘ ਜਾਂਦਾ ਹੈ।",
    # EN: The Moon in your 9th house is a mixed transit. Plans may need extra effort and you may
    #     feel tired or distracted. Prayer, reading and time with elders or teachers suit the day
    #     better than big new ventures.
    9: "ਚੰਦਰਮਾ ਦਾ ਨੌਵੇਂ ਭਾਵ ਵਿੱਚ ਹੋਣਾ ਮਿਲਿਆ-ਜੁਲਿਆ ਗੋਚਰ ਹੈ। ਯੋਜਨਾਵਾਂ ਲਈ ਵਾਧੂ ਮਿਹਨਤ ਕਰਨੀ ਪੈ ਸਕਦੀ ਹੈ ਅਤੇ ਥਕਾਵਟ ਜਾਂ ਧਿਆਨ ਭਟਕਣ ਦਾ ਅਹਿਸਾਸ ਹੋ ਸਕਦਾ ਹੈ। ਵੱਡੇ ਨਵੇਂ ਕੰਮਾਂ ਨਾਲੋਂ ਪੂਜਾ-ਪਾਠ, ਪੜ੍ਹਨਾ ਅਤੇ ਬਜ਼ੁਰਗਾਂ ਜਾਂ ਗੁਰੂਆਂ ਨਾਲ ਸਮਾਂ ਦਿਨ ਨੂੰ ਜ਼ਿਆਦਾ ਰਾਸ ਆਉਂਦਾ ਹੈ।",
    # EN: The Moon in your 10th house supports work and reputation. Tasks get done, seniors are
    #     receptive and effort is noticed. A good day to present your work, take a professional step
    #     or finish something visible.
    10: "ਚੰਦਰਮਾ ਦਾ ਦਸਵੇਂ ਭਾਵ ਵਿੱਚ ਹੋਣਾ ਕੰਮ ਅਤੇ ਸਾਖ ਦਾ ਸਾਥ ਦਿੰਦਾ ਹੈ। ਕੰਮ ਨਿਬੜਦੇ ਹਨ, ਵੱਡੇ ਅਫ਼ਸਰ ਗੱਲ ਸੁਣਦੇ ਹਨ ਅਤੇ ਮਿਹਨਤ ਨੂੰ ਨੋਟਿਸ ਕੀਤਾ ਜਾਂਦਾ ਹੈ। ਆਪਣਾ ਕੰਮ ਪੇਸ਼ ਕਰਨ, ਪੇਸ਼ੇਵਰ ਕਦਮ ਚੁੱਕਣ ਜਾਂ ਕੋਈ ਨਜ਼ਰ ਆਉਣ ਵਾਲਾ ਕੰਮ ਪੂਰਾ ਕਰਨ ਲਈ ਚੰਗਾ ਦਿਨ ਹੈ।",
    # EN: The Moon in your 11th house — the house of gains — is a very favourable transit. Expect
    #     support from friends, good news and the fruit of earlier effort. A good day for
    #     networking, making requests and celebrating with others.
    11: "ਚੰਦਰਮਾ ਦਾ ਗਿਆਰ੍ਹਵੇਂ ਭਾਵ — ਲਾਭ ਦੇ ਭਾਵ — ਵਿੱਚ ਹੋਣਾ ਬਹੁਤ ਸ਼ੁਭ ਗੋਚਰ ਹੈ। ਦੋਸਤਾਂ ਦਾ ਸਾਥ, ਚੰਗੀ ਖ਼ਬਰ ਅਤੇ ਪਹਿਲਾਂ ਕੀਤੀ ਮਿਹਨਤ ਦਾ ਫਲ ਮਿਲਣ ਦੀ ਆਸ ਰੱਖੋ। ਜਾਣ-ਪਛਾਣ ਵਧਾਉਣ, ਬੇਨਤੀਆਂ ਕਰਨ ਅਤੇ ਦੂਜਿਆਂ ਨਾਲ ਖ਼ੁਸ਼ੀ ਮਨਾਉਣ ਲਈ ਚੰਗਾ ਦਿਨ ਹੈ।",
    # EN: The Moon in your 12th house can bring extra expenses and a tired, inward mood. Avoid
    #     overspending and late nights; the day suits rest, prayer, charity and finishing old work
    #     rather than starting new.
    12: "ਚੰਦਰਮਾ ਦਾ ਬਾਰ੍ਹਵੇਂ ਭਾਵ ਵਿੱਚ ਹੋਣਾ ਵਾਧੂ ਖ਼ਰਚ ਅਤੇ ਥਕਾਵਟ ਭਰਿਆ, ਅੰਦਰ ਵੱਲ ਮੁੜਿਆ ਮੂਡ ਲਿਆ ਸਕਦਾ ਹੈ। ਫ਼ਜ਼ੂਲਖ਼ਰਚੀ ਅਤੇ ਦੇਰ ਰਾਤ ਜਾਗਣ ਤੋਂ ਬਚੋ; ਦਿਨ ਆਰਾਮ, ਪੂਜਾ-ਪਾਠ, ਦਾਨ ਅਤੇ ਪੁਰਾਣੇ ਕੰਮ ਨਿਬੇੜਨ ਲਈ ਠੀਕ ਹੈ, ਨਵਾਂ ਸ਼ੁਰੂ ਕਰਨ ਲਈ ਨਹੀਂ।",
}

# app/rashifal_text.py SATURN_HOUSE["pa"] — Saturn transit through houses 1-12  [12]
RASHIFAL_SATURN_HOUSE = {
    # EN: Saturn is passing over your Moon sign — the peak phase of Sade Sati. It rewards patience,
    #     routine and honest effort; take on a little less and finish what you start.
    1: "ਸ਼ਨੀ ਤੁਹਾਡੀ ਚੰਦਰ ਰਾਸ਼ੀ ਉੱਤੋਂ ਲੰਘ ਰਿਹਾ ਹੈ — ਸਾੜ੍ਹਸਾਤੀ ਦਾ ਸਿਖ਼ਰ ਪੜਾਅ। ਇਹ ਸਬਰ, ਰੁਟੀਨ ਅਤੇ ਇਮਾਨਦਾਰ ਮਿਹਨਤ ਦਾ ਫਲ ਦਿੰਦਾ ਹੈ; ਥੋੜ੍ਹਾ ਘੱਟ ਕੰਮ ਲਵੋ ਅਤੇ ਜੋ ਸ਼ੁਰੂ ਕਰੋ ਉਹ ਪੂਰਾ ਕਰੋ।",
    # EN: Saturn is in your 2nd — the last phase of Sade Sati. Be measured with spending and with
    #     words at home; the pressure is easing.
    2: "ਸ਼ਨੀ ਤੁਹਾਡੇ ਦੂਜੇ ਭਾਵ ਵਿੱਚ ਹੈ — ਸਾੜ੍ਹਸਾਤੀ ਦਾ ਆਖ਼ਰੀ ਪੜਾਅ। ਖ਼ਰਚ ਅਤੇ ਘਰ ਦੀ ਬੋਲ-ਚਾਲ ਵਿੱਚ ਸੰਜਮ ਰੱਖੋ; ਦਬਾਅ ਘਟ ਰਿਹਾ ਹੈ।",
    # EN: Saturn in your 3rd is one of its best positions — steady effort pays, courage grows and
    #     long-running work gains traction.
    3: "ਸ਼ਨੀ ਦਾ ਤੀਜੇ ਭਾਵ ਵਿੱਚ ਹੋਣਾ ਉਸ ਦੀਆਂ ਸਭ ਤੋਂ ਵਧੀਆ ਸਥਿਤੀਆਂ ਵਿੱਚੋਂ ਇੱਕ ਹੈ — ਲਗਾਤਾਰ ਮਿਹਨਤ ਫਲ ਦਿੰਦੀ ਹੈ, ਹਿੰਮਤ ਵਧਦੀ ਹੈ ਅਤੇ ਲੰਮੇ ਸਮੇਂ ਤੋਂ ਚੱਲ ਰਹੇ ਕੰਮ ਰਫ਼ਤਾਰ ਫੜਦੇ ਹਨ।",
    # EN: Saturn in your 4th (Dhaiya, Kantaka Shani) can make home life and peace of mind feel
    #     heavier; keep routines simple and handle family matters calmly.
    4: "ਸ਼ਨੀ ਦਾ ਚੌਥੇ ਭਾਵ ਵਿੱਚ ਹੋਣਾ (ਢੱਈਆ, ਕੰਟਕ ਸ਼ਨੀ) ਘਰੇਲੂ ਜੀਵਨ ਅਤੇ ਮਨ ਦੀ ਸ਼ਾਂਤੀ ਨੂੰ ਭਾਰੀ ਬਣਾ ਸਕਦਾ ਹੈ; ਰੁਟੀਨ ਸਾਦਾ ਰੱਖੋ ਅਤੇ ਪਰਿਵਾਰਕ ਮਾਮਲੇ ਸ਼ਾਂਤੀ ਨਾਲ ਨਿਬੇੜੋ।",
    # EN: Saturn in your 5th asks for patience with plans, studies and children's matters — slow and
    #     careful beats quick.
    5: "ਸ਼ਨੀ ਦਾ ਪੰਜਵੇਂ ਭਾਵ ਵਿੱਚ ਹੋਣਾ ਯੋਜਨਾਵਾਂ, ਪੜ੍ਹਾਈ ਅਤੇ ਬੱਚਿਆਂ ਦੇ ਮਾਮਲਿਆਂ ਵਿੱਚ ਸਬਰ ਮੰਗਦਾ ਹੈ — ਜਲਦਬਾਜ਼ੀ ਨਾਲੋਂ ਹੌਲੀ ਅਤੇ ਸੋਚ-ਸਮਝ ਕੇ ਚੱਲਣਾ ਚੰਗਾ ਹੈ।",
    # EN: Saturn in your 6th works in your favour — discipline wins over rivals and backlog, and
    #     hard work gets noticed.
    6: "ਸ਼ਨੀ ਦਾ ਛੇਵੇਂ ਭਾਵ ਵਿੱਚ ਹੋਣਾ ਤੁਹਾਡੇ ਹੱਕ ਵਿੱਚ ਕੰਮ ਕਰਦਾ ਹੈ — ਅਨੁਸ਼ਾਸਨ ਵਿਰੋਧੀਆਂ ਅਤੇ ਜਮ੍ਹਾ ਕੰਮ ਉੱਤੇ ਜਿੱਤ ਦਿਵਾਉਂਦਾ ਹੈ, ਅਤੇ ਸਖ਼ਤ ਮਿਹਨਤ ਨੂੰ ਪਛਾਣ ਮਿਲਦੀ ਹੈ।",
    # EN: Saturn in your 7th puts partnerships in a slow, serious light — clear agreements and
    #     patience help.
    7: "ਸ਼ਨੀ ਦਾ ਸੱਤਵੇਂ ਭਾਵ ਵਿੱਚ ਹੋਣਾ ਸਾਂਝੇਦਾਰੀਆਂ ਨੂੰ ਹੌਲੀ ਅਤੇ ਗੰਭੀਰ ਰੰਗ ਵਿੱਚ ਦਿਖਾਉਂਦਾ ਹੈ — ਸਾਫ਼ ਸਮਝੌਤੇ ਅਤੇ ਸਬਰ ਮਦਦ ਕਰਦੇ ਹਨ।",
    # EN: Saturn in your 8th (Dhaiya, Ashtama Shani) is a time to avoid shortcuts and keep a margin
    #     for delays.
    8: "ਸ਼ਨੀ ਦਾ ਅੱਠਵੇਂ ਭਾਵ ਵਿੱਚ ਹੋਣਾ (ਢੱਈਆ, ਅਸ਼ਟਮ ਸ਼ਨੀ) ਸ਼ਾਰਟਕੱਟਾਂ ਤੋਂ ਬਚਣ ਅਤੇ ਦੇਰੀ ਲਈ ਗੁੰਜਾਇਸ਼ ਰੱਖਣ ਦਾ ਸਮਾਂ ਹੈ।",
    # EN: Saturn in your 9th can slow luck and long journeys; respect for elders and steady duty
    #     keep things on track.
    9: "ਸ਼ਨੀ ਦਾ ਨੌਵੇਂ ਭਾਵ ਵਿੱਚ ਹੋਣਾ ਕਿਸਮਤ ਅਤੇ ਲੰਮੇ ਸਫ਼ਰਾਂ ਨੂੰ ਹੌਲੀ ਕਰ ਸਕਦਾ ਹੈ; ਬਜ਼ੁਰਗਾਂ ਦਾ ਆਦਰ ਅਤੇ ਪੱਕੀ ਜ਼ਿੰਮੇਵਾਰੀ ਗੱਲ ਨੂੰ ਲੀਹ ’ਤੇ ਰੱਖਦੇ ਹਨ।",
    # EN: Saturn in your 10th brings responsibility at work — a heavier load, but sincere effort
    #     builds a lasting reputation.
    10: "ਸ਼ਨੀ ਦਾ ਦਸਵੇਂ ਭਾਵ ਵਿੱਚ ਹੋਣਾ ਕੰਮ ’ਤੇ ਜ਼ਿੰਮੇਵਾਰੀ ਲਿਆਉਂਦਾ ਹੈ — ਬੋਝ ਭਾਰੀ ਹੈ, ਪਰ ਸੱਚੀ ਮਿਹਨਤ ਪੱਕੀ ਸਾਖ ਬਣਾਉਂਦੀ ਹੈ।",
    # EN: Saturn in your 11th is favourable — gains come slowly but surely, and long effort starts
    #     to pay off.
    11: "ਸ਼ਨੀ ਦਾ ਗਿਆਰ੍ਹਵੇਂ ਭਾਵ ਵਿੱਚ ਹੋਣਾ ਸ਼ੁਭ ਹੈ — ਲਾਭ ਹੌਲੀ ਪਰ ਪੱਕੇ ਤੌਰ ’ਤੇ ਆਉਂਦਾ ਹੈ, ਅਤੇ ਲੰਮੀ ਮਿਹਨਤ ਦਾ ਫਲ ਮਿਲਣ ਲੱਗਦਾ ਹੈ।",
    # EN: Saturn is in your 12th — the opening phase of Sade Sati. Watch expenses and rest well; a
    #     good time for quiet, inward work.
    12: "ਸ਼ਨੀ ਤੁਹਾਡੇ ਬਾਰ੍ਹਵੇਂ ਭਾਵ ਵਿੱਚ ਹੈ — ਸਾੜ੍ਹਸਾਤੀ ਦਾ ਸ਼ੁਰੂਆਤੀ ਪੜਾਅ। ਖ਼ਰਚਿਆਂ ਦਾ ਧਿਆਨ ਰੱਖੋ ਅਤੇ ਚੰਗਾ ਆਰਾਮ ਕਰੋ; ਸ਼ਾਂਤ, ਅੰਦਰੂਨੀ ਕੰਮ ਲਈ ਚੰਗਾ ਸਮਾਂ ਹੈ।",
}

# app/rashifal_text.py JUPITER_HOUSE["pa"] — Jupiter transit through houses 1-12  [12]
RASHIFAL_JUPITER_HOUSE = {
    # EN: Jupiter over your Moon sign is classically a restless position; keep plans grounded and
    #     avoid over-committing.
    1: "ਬ੍ਰਿਹਸਪਤੀ ਦਾ ਚੰਦਰ ਰਾਸ਼ੀ ਉੱਤੇ ਹੋਣਾ ਸ਼ਾਸਤਰਾਂ ਅਨੁਸਾਰ ਬੇਚੈਨ ਸਥਿਤੀ ਹੈ; ਯੋਜਨਾਵਾਂ ਜ਼ਮੀਨ ’ਤੇ ਰੱਖੋ ਅਤੇ ਲੋੜ ਤੋਂ ਵੱਧ ਵਾਅਦੇ ਨਾ ਕਰੋ।",
    # EN: Jupiter in your 2nd supports family harmony, savings and kind speech.
    2: "ਬ੍ਰਿਹਸਪਤੀ ਦਾ ਦੂਜੇ ਭਾਵ ਵਿੱਚ ਹੋਣਾ ਪਰਿਵਾਰਕ ਮੇਲ-ਜੋਲ, ਬੱਚਤ ਅਤੇ ਮਿੱਠੀ ਬੋਲੀ ਦਾ ਸਾਥ ਦਿੰਦਾ ਹੈ।",
    # EN: Jupiter in your 3rd asks a little more effort for the same result — keep at it.
    3: "ਬ੍ਰਿਹਸਪਤੀ ਦਾ ਤੀਜੇ ਭਾਵ ਵਿੱਚ ਹੋਣਾ ਉਸੇ ਨਤੀਜੇ ਲਈ ਥੋੜ੍ਹੀ ਵੱਧ ਮਿਹਨਤ ਮੰਗਦਾ ਹੈ — ਲੱਗੇ ਰਹੋ।",
    # EN: Jupiter in your 4th can unsettle home matters; patience with relatives helps.
    4: "ਬ੍ਰਿਹਸਪਤੀ ਦਾ ਚੌਥੇ ਭਾਵ ਵਿੱਚ ਹੋਣਾ ਘਰ ਦੇ ਮਾਮਲਿਆਂ ਨੂੰ ਡਾਵਾਂਡੋਲ ਕਰ ਸਕਦਾ ਹੈ; ਰਿਸ਼ਤੇਦਾਰਾਂ ਨਾਲ ਸਬਰ ਮਦਦ ਕਰਦਾ ਹੈ।",
    # EN: Jupiter in your 5th favours learning, children's matters, creativity and good counsel.
    5: "ਬ੍ਰਿਹਸਪਤੀ ਦਾ ਪੰਜਵੇਂ ਭਾਵ ਵਿੱਚ ਹੋਣਾ ਪੜ੍ਹਾਈ, ਬੱਚਿਆਂ ਦੇ ਮਾਮਲਿਆਂ, ਰਚਨਾਤਮਕਤਾ ਅਤੇ ਚੰਗੀ ਸਲਾਹ ਦੇ ਪੱਖ ਵਿੱਚ ਹੈ।",
    # EN: Jupiter in your 6th: steer clear of small disputes and overwork.
    6: "ਬ੍ਰਿਹਸਪਤੀ ਦਾ ਛੇਵੇਂ ਭਾਵ ਵਿੱਚ ਹੋਣਾ: ਛੋਟੇ ਝਗੜਿਆਂ ਅਤੇ ਹੱਦੋਂ ਵੱਧ ਕੰਮ ਤੋਂ ਬਚੋ।",
    # EN: Jupiter in your 7th blesses partnerships, marriage talks and travel.
    7: "ਬ੍ਰਿਹਸਪਤੀ ਦਾ ਸੱਤਵੇਂ ਭਾਵ ਵਿੱਚ ਹੋਣਾ ਸਾਂਝੇਦਾਰੀਆਂ, ਵਿਆਹ ਦੀਆਂ ਗੱਲਾਂ ਅਤੇ ਸਫ਼ਰ ਲਈ ਸ਼ੁਭ ਹੈ।",
    # EN: Jupiter in your 8th suggests care with big decisions — go slow.
    8: "ਬ੍ਰਿਹਸਪਤੀ ਦਾ ਅੱਠਵੇਂ ਭਾਵ ਵਿੱਚ ਹੋਣਾ ਵੱਡੇ ਫ਼ੈਸਲਿਆਂ ਵਿੱਚ ਸਾਵਧਾਨੀ ਦਾ ਸੰਕੇਤ ਦਿੰਦਾ ਹੈ — ਹੌਲੀ ਚੱਲੋ।",
    # EN: Jupiter in your 9th is one of its best positions — fortune, dharma and guidance from
    #     teachers.
    9: "ਬ੍ਰਿਹਸਪਤੀ ਦਾ ਨੌਵੇਂ ਭਾਵ ਵਿੱਚ ਹੋਣਾ ਉਸ ਦੀਆਂ ਸਭ ਤੋਂ ਵਧੀਆ ਸਥਿਤੀਆਂ ਵਿੱਚੋਂ ਇੱਕ ਹੈ — ਕਿਸਮਤ, ਧਰਮ ਅਤੇ ਗੁਰੂਆਂ ਤੋਂ ਸੇਧ।",
    # EN: Jupiter in your 10th may bring changes at work; stay adaptable.
    10: "ਬ੍ਰਿਹਸਪਤੀ ਦਾ ਦਸਵੇਂ ਭਾਵ ਵਿੱਚ ਹੋਣਾ ਕੰਮ ’ਤੇ ਬਦਲਾਅ ਲਿਆ ਸਕਦਾ ਹੈ; ਲਚਕੀਲੇ ਰਹੋ।",
    # EN: Jupiter in your 11th brings gains, fulfilled wishes and helpful friends.
    11: "ਬ੍ਰਿਹਸਪਤੀ ਦਾ ਗਿਆਰ੍ਹਵੇਂ ਭਾਵ ਵਿੱਚ ਹੋਣਾ ਲਾਭ, ਮਨ ਦੀਆਂ ਮੁਰਾਦਾਂ ਦੀ ਪੂਰਤੀ ਅਤੇ ਮਦਦਗਾਰ ਦੋਸਤ ਲਿਆਉਂਦਾ ਹੈ।",
    # EN: Jupiter in your 12th brings expenses, often on good causes; charity and spiritual practice
    #     are well placed.
    12: "ਬ੍ਰਿਹਸਪਤੀ ਦਾ ਬਾਰ੍ਹਵੇਂ ਭਾਵ ਵਿੱਚ ਹੋਣਾ ਖ਼ਰਚ ਲਿਆਉਂਦਾ ਹੈ, ਅਕਸਰ ਚੰਗੇ ਕੰਮਾਂ ’ਤੇ; ਦਾਨ ਅਤੇ ਅਧਿਆਤਮਿਕ ਸਾਧਨਾ ਲਈ ਇਹ ਸਮਾਂ ਠੀਕ ਹੈ।",
}

# app/rashifal_text.py RAHU_HOUSE["pa"] — Rahu transit through houses 1-12  [12]
RASHIFAL_RAHU_HOUSE = {
    # EN: Rahu over your Moon sign can stir restlessness and unusual wants; stay grounded.
    1: "ਰਾਹੂ ਦਾ ਚੰਦਰ ਰਾਸ਼ੀ ਉੱਤੇ ਹੋਣਾ ਬੇਚੈਨੀ ਅਤੇ ਅਜੀਬ ਇੱਛਾਵਾਂ ਜਗਾ ਸਕਦਾ ਹੈ; ਜ਼ਮੀਨ ਨਾਲ ਜੁੜੇ ਰਹੋ।",
    # EN: Rahu in your 2nd: take care with speech and money talk within the family.
    2: "ਰਾਹੂ ਦੂਜੇ ਭਾਵ ਵਿੱਚ: ਪਰਿਵਾਰ ਵਿੱਚ ਬੋਲਣ ਅਤੇ ਪੈਸੇ ਦੀ ਗੱਲ-ਬਾਤ ਵਿੱਚ ਖ਼ਿਆਲ ਰੱਖੋ।",
    # EN: Rahu in your 3rd is favourable — bold initiatives and communication succeed.
    3: "ਰਾਹੂ ਦਾ ਤੀਜੇ ਭਾਵ ਵਿੱਚ ਹੋਣਾ ਸ਼ੁਭ ਹੈ — ਦਲੇਰ ਪਹਿਲਕਦਮੀਆਂ ਅਤੇ ਗੱਲ-ਬਾਤ ਵਿੱਚ ਸਫਲਤਾ ਮਿਲਦੀ ਹੈ।",
    # EN: Rahu in your 4th can unsettle domestic peace; avoid hasty property moves.
    4: "ਰਾਹੂ ਦਾ ਚੌਥੇ ਭਾਵ ਵਿੱਚ ਹੋਣਾ ਘਰ ਦੀ ਸ਼ਾਂਤੀ ਨੂੰ ਡਾਵਾਂਡੋਲ ਕਰ ਸਕਦਾ ਹੈ; ਜਾਇਦਾਦ ਦੇ ਮਾਮਲਿਆਂ ਵਿੱਚ ਕਾਹਲੀ ਨਾ ਕਰੋ।",
    # EN: Rahu in your 5th: double-check risky ideas and keep a clear head.
    5: "ਰਾਹੂ ਪੰਜਵੇਂ ਭਾਵ ਵਿੱਚ: ਜੋਖਮ ਭਰੇ ਵਿਚਾਰਾਂ ਨੂੰ ਦੋ ਵਾਰ ਪਰਖੋ ਅਤੇ ਦਿਮਾਗ਼ ਠੰਢਾ ਰੱਖੋ।",
    # EN: Rahu in your 6th helps you get past competition and obstacles.
    6: "ਰਾਹੂ ਦਾ ਛੇਵੇਂ ਭਾਵ ਵਿੱਚ ਹੋਣਾ ਮੁਕਾਬਲੇ ਅਤੇ ਰੁਕਾਵਟਾਂ ਨੂੰ ਪਾਰ ਕਰਨ ਵਿੱਚ ਮਦਦ ਕਰਦਾ ਹੈ।",
    # EN: Rahu in your 7th: keep partnerships transparent.
    7: "ਰਾਹੂ ਸੱਤਵੇਂ ਭਾਵ ਵਿੱਚ: ਸਾਂਝੇਦਾਰੀਆਂ ਵਿੱਚ ਪਾਰਦਰਸ਼ਤਾ ਰੱਖੋ।",
    # EN: Rahu in your 8th: avoid risky shortcuts and stay calm when the unexpected comes.
    8: "ਰਾਹੂ ਅੱਠਵੇਂ ਭਾਵ ਵਿੱਚ: ਜੋਖਮ ਭਰੇ ਸ਼ਾਰਟਕੱਟਾਂ ਤੋਂ ਬਚੋ ਅਤੇ ਅਚਾਨਕ ਕੁਝ ਹੋ ਜਾਣ ’ਤੇ ਸ਼ਾਂਤ ਰਹੋ।",
    # EN: Rahu in your 9th can raise doubts about beliefs or mentors; seek advice you trust.
    9: "ਰਾਹੂ ਦਾ ਨੌਵੇਂ ਭਾਵ ਵਿੱਚ ਹੋਣਾ ਵਿਸ਼ਵਾਸਾਂ ਜਾਂ ਮਾਰਗ-ਦਰਸ਼ਕਾਂ ਬਾਰੇ ਸ਼ੰਕੇ ਪੈਦਾ ਕਰ ਸਕਦਾ ਹੈ; ਭਰੋਸੇਯੋਗ ਸਲਾਹ ਲਵੋ।",
    # EN: Rahu in your 10th brings ambition and sudden openings at work; move with integrity.
    10: "ਰਾਹੂ ਦਾ ਦਸਵੇਂ ਭਾਵ ਵਿੱਚ ਹੋਣਾ ਲਾਲਸਾ ਅਤੇ ਕੰਮ ’ਤੇ ਅਚਾਨਕ ਮੌਕੇ ਲਿਆਉਂਦਾ ਹੈ; ਇਮਾਨਦਾਰੀ ਨਾਲ ਅੱਗੇ ਵਧੋ।",
    # EN: Rahu in your 11th — gains through networks and new contacts.
    11: "ਰਾਹੂ ਗਿਆਰ੍ਹਵੇਂ ਭਾਵ ਵਿੱਚ — ਜਾਣ-ਪਛਾਣ ਅਤੇ ਨਵੇਂ ਸੰਪਰਕਾਂ ਰਾਹੀਂ ਲਾਭ।",
    # EN: Rahu in your 12th: watch hidden expenses and get proper rest.
    12: "ਰਾਹੂ ਬਾਰ੍ਹਵੇਂ ਭਾਵ ਵਿੱਚ: ਲੁਕਵੇਂ ਖ਼ਰਚਿਆਂ ਦਾ ਧਿਆਨ ਰੱਖੋ ਅਤੇ ਪੂਰਾ ਆਰਾਮ ਕਰੋ।",
}

# app/rashifal_text.py KETU_LINE["pa"] — Ketu line, True = favourable house, False = quiet house; {n} is the house  [2]
RASHIFAL_KETU_LINE = {
    # EN: Ketu in your {n} house works quietly in your favour — obstacles clear with less fuss.
    # keep: {n}
    True: "ਤੁਹਾਡੇ {n} ਭਾਵ ਵਿੱਚ ਕੇਤੂ ਚੁੱਪਚਾਪ ਤੁਹਾਡੇ ਹੱਕ ਵਿੱਚ ਕੰਮ ਕਰਦਾ ਹੈ — ਰੁਕਾਵਟਾਂ ਬਿਨਾਂ ਸ਼ੋਰ-ਸ਼ਰਾਬੇ ਦੇ ਦੂਰ ਹੋ ਜਾਂਦੀਆਂ ਹਨ।",
    # EN: Ketu in your {n} house is a quieter, inward influence — good for reflection and spiritual
    #     practice, less so for impulsive moves.
    # keep: {n}
    False: "ਤੁਹਾਡੇ {n} ਭਾਵ ਵਿੱਚ ਕੇਤੂ ਇੱਕ ਸ਼ਾਂਤ, ਅੰਦਰ ਵੱਲ ਮੋੜਨ ਵਾਲਾ ਪ੍ਰਭਾਵ ਹੈ — ਸੋਚ-ਵਿਚਾਰ ਅਤੇ ਅਧਿਆਤਮਿਕ ਸਾਧਨਾ ਲਈ ਚੰਗਾ, ਕਾਹਲੀ ਵਿੱਚ ਚੁੱਕੇ ਕਦਮਾਂ ਲਈ ਘੱਟ।",
}

# app/rashifal_text.py CLOCK_LANG["pa"] — leave '' (the language's own clock words); 'en' prints 6:29 AM as Hindi pages do
# (optional: may stay empty)
RASHIFAL_CLOCK_LANG = ""

# ----------------------------------------------------------------------------
# vrat      /vrat-tyohar /ekadashi-<year> /tyohar/<slug>-<year>
# ----------------------------------------------------------------------------

# app/vrat_text.py TEXT["pa"] — page text of /vrat-tyohar, /ekadashi-<year>, /tyohar/<slug>-<year>  [64]
VRAT_TEXT = {
    # EN: Vrat & festivals
    "crumb": "",
    # EN: {date}, {weekday}
    # keep: {date} {weekday}
    "day_label": "",
    # EN: {label}: {prefix}{value}
    # keep: {label} {prefix} {value}
    "timing": "",
    # EN: {paksha} {name}: {start} to {end}
    # keep: {end} {name} {paksha} {start}
    "tithi.text": "",
    # EN: {paksha}
    # keep: {paksha}
    "tithi.paksha": "",
    # EN: <tr><th>Date</th><th>Vrat / festival</th><th>Timing ({city})</th></tr>
    # keep: {city}
    "table.th": "",
    # EN: <div class="box"><p><strong>Timings vary by city.</strong> Every time here is for {city}'s
    #     sunrise, sunset and moonrise; in another city they shift by a few minutes and occasionally
    #     the date does too. Dates follow Drik Panchang's Smarta (default) reckoning. Check the
    #     Panchang for your own city.</p></div>
    # keep: {city}
    "city_note": "",
    # EN: <p class="note"><small>For most observances the date is the same across India, but puja
    #     muhurat, parana and moonrise times differ from city to city - every time here is for
    #     <strong>{city}</strong>. Regional traditions may vary.</small></p>
    # keep: {city}
    "top_note": "",
    # EN: Vrat & festivals in your city
    "cities.heading": "",
    # EN: Today's Panchang in {city}
    # keep: {city}
    "tools.panchang": "",
    # EN: Rahu Kaal in {city}
    # keep: {city}
    # may also use: {t_rahu_kaal}
    "tools.rahu": "",
    # EN: More for {city}
    # keep: {city}
    "tools.heading": "",
    # EN: See the Panchang for your city — free
    "cta": "",
    # EN: Today's vrat & festivals
    "more.today": "",
    # EN: Festival calendar {year}
    # keep: {year}
    "more.year": "",
    # EN: Ekadashi {year}
    # keep: {year}
    "more.ekadashi": "",
    # EN: Today's Panchang
    "more.panchang": "",
    # EN: Today's Rashifal
    "more.rashifal": "",
    # EN: More
    "more.heading": "",
    # EN: Major festivals {year}
    # keep: {year}
    "majors.heading": "",
    # EN: Rule
    "today.rule": "",
    # EN: No major vrat or festival today.
    "today.none": "",
    # EN: Next: <strong>{name}</strong> on {day}.
    # keep: {day} {name}
    "today.next": "",
    # EN: Vrat &amp; Festivals today
    "block.heading": "",
    # EN: Page not found
    "nf.h1": "",
    # EN: Aaj Ke Vrat aur Tyohar: Today's Vrat & Festivals ({date})
    # keep: {date}
    "hub.title_default": "",
    # EN: Today's Vrat & Festivals in {city} ({date}) - Aaj Ke Vrat
    # keep: {city} {date}
    "hub.title_city": "",
    # EN: Today's vrat & festivals
    "hub.h1_default": "",
    # EN: Today's vrat & festivals in {city}
    # keep: {city}
    "hub.h1_city": "",
    # EN: Today, {date}: {names}.
    # keep: {date} {names}
    "hub.desc_today": "",
    # EN: {date}: no major vrat today.
    # keep: {date}
    "hub.desc_none": "",
    # EN: Upcoming fasts and festivals for 30 days with Ekadashi parana, Pradosh and Sankashti
    #     moonrise times - {city}.
    # keep: {city}
    "hub.desc_rest": "",
    # EN: <p class="hi" lang="hi">आज के व्रत और त्योहार</p>
    "hub.sub": "",
    # EN: Next 30 days
    "hub.upcoming": "",
    # EN: Hindu Festival & Vrat Calendar {year} (New Delhi): Dates and Muhurat
    # keep: {year}
    "year.title": "",
    # EN: Vrat & festival calendar {year}
    # keep: {year}
    "year.h1": "",
    # EN: Every Hindu vrat and festival of {year}, month by month - Ekadashi, Pradosh, Sankashti,
    #     Purnima, Amavasya, Shivratri and festivals like Diwali, Navratri and Raksha Bandhan, with
    #     puja muhurat for New Delhi.
    # keep: {year}
    "year.desc": "",
    # EN: <p><strong>{count}</strong> fasts and festivals in {year} for New Delhi, computed from the
    #     panchang. Tap a major festival for its puja muhurat and what it is about.</p>
    # keep: {count} {year}
    "year.intro": "",
    # EN: {month} {year}
    # keep: {month} {year}
    "year.month": "",
    # EN: Major Hindu festivals {year}
    # keep: {year}
    "year.itemlist": "",
    # EN: Ekadashi {year}: All Ekadashi Vrat Dates and Parana Time (New Delhi)
    # keep: {year}
    "ek.title": "",
    # EN: Ekadashi {year}: dates and parana time
    # keep: {year}
    "ek.h1": "",
    # EN: All {count} Ekadashis of {year} - fasting date, Ekadashi tithi times and the parana (fast-
    #     breaking) window next day, for New Delhi.
    # keep: {count} {year}
    "ek.desc": "",
    # EN: <tr><th>Ekadashi</th><th>Fast</th><th>Parana</th></tr>
    "ek.th": "",
    # EN: <p><strong>Rule (Smarta):</strong> fast on the day Ekadashi prevails at sunrise; if it
    #     prevails at two sunrises, the second day, and if at none, the day it falls in. Parana is
    #     the next day after sunrise, once Hari Vasara (the first quarter of Dwadashi) is over,
    #     within Pratahkala and before Dwadashi ends; if Hari Vasara runs past Pratahkala, parana
    #     moves to Aparahna (Madhyahna is avoided).</p>
    "ek.rule": "",
    # EN: <p class="hi" lang="hi">एकादशी {year}</p>
    # keep: {year}
    "ek.sub": "",
    # EN: Ekadashi {year}
    # keep: {year}
    "ek.crumb": "",
    # EN: {name} {year}: Date and Puja Muhurat - {short}
    # keep: {name} {short} {year}
    "fest.title": "",
    # EN: {name} {year}: date and muhurat
    # keep: {name} {year}
    "fest.h1": "",
    # EN: {text}.
    # keep: {text}
    "fest.main": "",
    # EN: {name} {year} is on {weekday}, {date}. {main}Puja timings for New Delhi.
    # keep: {date} {main} {name} {weekday} {year}
    "fest.desc": "",
    # EN: {name} {year} is on <strong>{when}</strong>.
    # keep: {name} {when} {year}
    "fest.when": "",
    # EN: <p class="hi" lang="hi">{name_hi} {year}</p>
    # keep: {year}
    "fest.sub": "",
    # EN: What it is and how it is observed
    "fest.about_h2": "",
    # EN: How the date is fixed
    "fest.rule_h2": "",
    # EN: Frequently asked questions
    "fest.faq_h2": "",
    # EN: India
    "event.place": "",
    # EN: When is {name} {year}?
    # keep: {name} {year}
    "faq.when_q": "",
    # EN: {name} {year} is on {weekday}, {date}.
    # keep: {date} {name} {weekday} {year}
    "faq.when_a": "",
    # EN: What is the {name} {year} puja muhurat?
    # keep: {name} {year}
    "faq.muhurat_q": "",
    # EN: What are the {name} {year} timings?
    # keep: {name} {year}
    "faq.timings_q": "",
    # EN: For New Delhi - {timings}. Timings vary by city by a few minutes; check the Panchang for
    #     your city.
    # keep: {timings}
    "faq.timings_a": "",
    # EN: Why is {name} {year} observed on {short}?
    # keep: {name} {short} {year}
    "faq.why_q": "",
    # EN: The date follows the rule: {rule}. In {year} that is {when} (New Delhi).
    # keep: {rule} {when} {year}
    "faq.why_a": "",
}

# app/vrat_text.py ABOUT["pa"] — what each of the 47 festivals / vrats is (key = festival slug)  [47]
VRAT_ABOUT = {
    # EN: Makar Sankranti marks the Sun's entry into Makara (Capricorn) and the start of its
    #     northward journey (Uttarayana). It is a harvest festival: people bathe in holy rivers,
    #     give til (sesame), jaggery, khichdi and blankets in charity, and fly kites.
    "makar-sankranti": "",
    # EN: Maha Shivratri, the great night of Shiva, falls on the Krishna Chaturdashi of Magha.
    #     Devotees fast, offer water, milk and bel leaves on the Shivling, chant Om Namah Shivaya
    #     and keep vigil through the four prahars of the night; the Nishita kaal puja around
    #     midnight is the most important.
    "maha-shivratri": "",
    # EN: Holika Dahan, on the eve of Holi, celebrates Prahlad's devotion and the victory of good
    #     over evil. A bonfire is lit after sunset, avoiding Bhadra, and families circle it offering
    #     grain, coconut and prayers.
    "holika-dahan": "",
    # EN: Holi, the festival of colours, is celebrated the morning after Holika Dahan with colours,
    #     music, sweets like gujiya and visits to family and friends.
    "holi": "",
    # EN: Ram Navami celebrates the birth of Lord Rama on Chaitra Shukla Navami, at midday. Devotees
    #     fast, read the Ramcharitmanas, and offer puja in the Madhyahna muhurat, the time of his
    #     birth.
    "ram-navami": "",
    # EN: Hanuman Jayanti (Chaitra Purnima in North India) celebrates the birth of Lord Hanuman.
    #     Devotees visit Hanuman temples, recite the Hanuman Chalisa and Sundarkand, and offer
    #     sindoor and laddoos.
    "hanuman-jayanti": "",
    # EN: Akshaya Tritiya, Vaishakha Shukla Tritiya, is held to make every good deed 'akshaya' -
    #     undiminishing. People worship Vishnu and Lakshmi, give in charity, and begin new ventures
    #     or buy gold.
    "akshaya-tritiya": "",
    # EN: Raksha Bandhan, on Shravana Purnima, celebrates the bond between brothers and sisters.
    #     Sisters tie a rakhi on their brother's wrist and pray for his well-being; the rakhi is
    #     tied in a time free of Bhadra.
    "raksha-bandhan": "",
    # EN: Krishna Janmashtami celebrates the birth of Lord Krishna at midnight on Krishna Ashtami of
    #     Bhadrapada (purnimanta). Devotees fast through the day and break it after the Nishita
    #     (midnight) puja, when the infant Krishna is bathed and placed in a cradle.
    "janmashtami": "",
    # EN: Ganesh Chaturthi, Bhadrapada Shukla Chaturthi, welcomes Lord Ganesha home. The idol is
    #     installed and worshipped in the Madhyahna (midday) muhurat, the time of his birth, with
    #     modak, durva grass and red flowers; looking at the Moon on this day is avoided.
    "ganesh-chaturthi": "",
    # EN: Chaitra Navratri, the nine nights of Goddess Durga in spring, begins on Chaitra Shukla
    #     Pratipada - also the Hindu New Year (Vikram Samvat). Ghatasthapana (installing the kalash)
    #     opens the nine days of worship.
    "chaitra-navratri": "",
    # EN: Sharad Navratri, the nine nights of Goddess Durga in autumn, begins on Ashwin Shukla
    #     Pratipada with Ghatasthapana - installing the kalash and sowing barley - in the morning.
    #     Each day honours one of the nine forms of the Goddess.
    "navratri": "",
    # EN: Dussehra (Vijayadashami) marks Lord Rama's victory over Ravana and Goddess Durga's over
    #     Mahishasura. Shami puja, Aparajita puja and the burning of Ravana effigies are held in the
    #     afternoon; the Vijay muhurat is considered good for starting anything new.
    "dussehra": "",
    # EN: On Karwa Chauth married women keep a fast from sunrise to moonrise for their husbands'
    #     long life. The evening puja of Karwa Mata is followed by offering water (arghya) to the
    #     Moon, after which the fast is broken.
    "karwa-chauth": "",
    # EN: On Ahoi Ashtami, eight days before Diwali, mothers keep a fast for the well-being of their
    #     children and worship Ahoi Mata in the evening; the fast is traditionally broken after
    #     sighting the stars (or, in some families, the Moon).
    "ahoi-ashtami": "",
    # EN: Dhanteras, the first day of Diwali, honours Dhanvantari and Goddess Lakshmi. People buy
    #     new utensils, gold or silver and light the Yama deepak at dusk; the puja is done in
    #     Pradosh kaal, ideally in the fixed (sthir) Vrishabha lagna.
    "dhanteras": "",
    # EN: Diwali, on Kartika Amavasya, is the festival of lights. Lakshmi and Ganesha are worshipped
    #     in the evening - in Pradosh kaal, preferably in the fixed (sthir) Vrishabha lagna so that
    #     prosperity stays - and homes are lit with diyas.
    "diwali": "",
    # EN: Govardhan Puja (Annakut), the day after Diwali, remembers Krishna lifting Govardhan hill.
    #     A Govardhan of cow-dung or food is worshipped and an annakut of many dishes is offered,
    #     usually in the morning (Pratahkala).
    "govardhan-puja": "",
    # EN: Bhai Dooj, Kartika Shukla Dwitiya, celebrates brothers and sisters: sisters apply a tilak,
    #     perform aarti and pray for their brother's long life, ideally in the Aparahna (afternoon)
    #     time.
    "bhai-dooj": "",
    # EN: Chhath Puja worships the Sun God and Chhathi Maiya over four days. On the main day
    #     (Kartika Shukla Shashthi) devotees stand in water and offer arghya to the setting Sun, and
    #     to the rising Sun the next morning, ending a fast kept without water.
    "chhath-puja": "",
    # EN: Vasant Panchami, Magha Shukla Panchami, welcomes spring and honours Goddess Saraswati.
    #     Students and artists worship books and instruments, people wear yellow, and children often
    #     begin learning to write (vidyarambh).
    "vasant-panchami": "",
    # EN: Guru Purnima, Ashadha Purnima, honours one's teachers and Maharishi Ved Vyasa, born on
    #     this day. Disciples offer gratitude, flowers and gifts to their guru.
    "guru-purnima": "",
    # EN: Sharad Purnima, Ashwin Purnima, is the night the Moon is held to be brightest and full of
    #     nectar. Kheer is kept in the moonlight overnight and eaten as prasad; Lakshmi is
    #     worshipped (Kojagari).
    "sharad-purnima": "",
    # EN: Devuthani (Prabodhini) Ekadashi, Kartika Shukla Ekadashi, is when Lord Vishnu is held to
    #     wake from his four-month sleep, ending Chaturmas. Tulsi vivah begins and the wedding
    #     season opens. Devotees fast and break the fast (parana) the next day.
    "devuthani-ekadashi": "",
    # EN: Jivitputrika (Jitiya, Jiutiya) is kept by mothers in Bihar, Jharkhand, eastern Uttar
    #     Pradesh and Nepal for the long life and well-being of their children, on Ashwin Krishna
    #     Ashtami (purnimanta). It begins with nahay-khay the day before; the fast itself is
    #     nirjala, without water, through the day and night, with worship of Jimutavahana and the
    #     Jitiya katha. Parana, breaking the fast, is the next morning.
    "jivitputrika": "",
    # EN: Lohri, the evening before Makar Sankranti, is the winter harvest festival of Punjab and
    #     North India. A bonfire is lit at dusk and people offer til, gur, rewari, peanuts and
    #     popcorn to it, sing and dance; it is especially celebrated for a new bride or a newborn.
    "lohri": "",
    # EN: Sakat Chauth (Tilkut Chauth), the Sankashti Chaturthi of Magha (purnimanta), is kept by
    #     mothers for their children. Ganesha and Sakat Mata are worshipped with til and jaggery,
    #     and the fast is broken after offering arghya to the rising Moon.
    "sakat-chauth": "",
    # EN: Mauni Amavasya, the Amavasya of Magha (purnimanta), is the great bathing day of the Magh
    #     Mela at Prayagraj. Devotees bathe in the Ganga or a holy river, keep silence (mauna) and
    #     give in charity.
    "mauni-amavasya": "",
    # EN: Sheetala Ashtami (Basoda), Chaitra Krishna Ashtami (purnimanta), honours Sheetala Mata,
    #     the goddess who protects from fevers and pox. Food is cooked the day before and the stale
    #     (basi) food is offered and eaten; no fire is lit for cooking that day.
    "sheetala-ashtami": "",
    # EN: Gudi Padwa (Maharashtra) and Ugadi (Karnataka, Andhra Pradesh, Telangana) mark the lunar
    #     New Year on Chaitra Shukla Pratipada. A gudi - a decorated pole with a cloth and kalash -
    #     is raised at the door, and neem with jaggery is eaten for a year of both sweet and bitter.
    "gudi-padwa": "",
    # EN: Gangaur, Chaitra Shukla Tritiya, is Rajasthan's festival of Gauri (Parvati) and Shiva.
    #     Women worship Gauri for marital happiness - married women for their husbands, girls for a
    #     good match - ending eighteen days of puja that begin the day after Holi.
    "gangaur": "",
    # EN: Vat Savitri Vrat, on Jyeshtha Amavasya in North India (purnimanta), remembers Savitri, who
    #     won back her husband Satyavan's life from Yama. Married women fast, worship the banyan
    #     (vat) tree, tie raw thread around it while circling it, and hear the Savitri katha.
    "vat-savitri": "",
    # EN: Vat Purnima is the same Vat Savitri vrat as kept on Jyeshtha Purnima in Maharashtra,
    #     Gujarat and the south (amanta calendar), fifteen days after the North Indian date. Married
    #     women fast and worship the banyan tree for their husbands' long life.
    "vat-purnima": "",
    # EN: Ganga Dussehra, Jyeshtha Shukla Dashami, celebrates the descent of the Ganga to earth
    #     through Bhagiratha's penance. Devotees bathe in the Ganga, offer lamps and give in
    #     charity; the bath is held to wash away ten kinds of sin.
    "ganga-dussehra": "",
    # EN: Hariyali Teej, Shravana Shukla Tritiya, celebrates the reunion of Shiva and Parvati in the
    #     monsoon. Women wear green, apply mehndi, swing on decorated jhoolas, sing Sawan songs and
    #     many keep a fast for their husbands.
    "hariyali-teej": "",
    # EN: Nag Panchami, Shravana Shukla Panchami, is the day serpent deities (nagas) are worshipped.
    #     Images of snakes are drawn or installed and offered milk, flowers and sweets, with prayers
    #     for the family's protection. (In Gujarat, Nag Pancham falls later, in Bhadrapada.)
    "nag-panchami": "",
    # EN: Kajari (Kajli, Badi) Teej, Bhadrapada Krishna Tritiya (purnimanta), is kept by married
    #     women of Uttar Pradesh, Bihar, Rajasthan and Madhya Pradesh. They fast, worship the neem
    #     tree (Neemadi Mata) and break the fast after offering arghya to the Moon; kajari folk
    #     songs are sung.
    "kajari-teej": "",
    # EN: Hal Shashthi (Lalahi Chhath, Har Chhath), Bhadrapada Krishna Shashthi (purnimanta), is
    #     Lord Balarama's birthday, whose weapon is the plough (hal). Mothers fast for their
    #     children and eat nothing grown with a plough - often pasahi rice and buffalo milk.
    "hal-shashthi": "",
    # EN: Hartalika Teej, Bhadrapada Shukla Tritiya, honours Parvati's penance to win Shiva. Women
    #     keep a nirjala fast, make clay images of Shiva and Parvati, worship them (morning puja in
    #     Pratahkala is preferred), keep vigil at night and break the fast next morning.
    "hartalika-teej": "",
    # EN: Rishi Panchami, Bhadrapada Shukla Panchami, honours the Saptarishis, the seven sages.
    #     Women in particular bathe, fast and worship the sages at midday (Madhyahna), seeking
    #     purification from faults committed unknowingly.
    "rishi-panchami": "",
    # EN: Anant Chaturdashi, Bhadrapada Shukla Chaturdashi, is the worship of Lord Vishnu as Anant.
    #     A sacred thread with fourteen knots (the anant sutra) is tied on the arm after puja; it is
    #     also the day Ganesh idols are immersed (Ganesh Visarjan).
    "anant-chaturdashi": "",
    # EN: Pitru Paksha, the fortnight of the ancestors, runs from Pratipada to Amavasya of the dark
    #     half of Ashwin (purnimanta). On the tithi of an ancestor's passing, families offer tarpan
    #     and shraddha - pinda, food for Brahmins, cows, crows and dogs - in the Kutup, Rohina or
    #     Aparahna time.
    "pitru-paksha": "",
    # EN: Sarva Pitru Amavasya (Mahalaya Amavasya) closes Pitru Paksha. Shraddha on this day reaches
    #     all ancestors, including those whose tithi is not known; it is done in the Kutup, Rohina
    #     or Aparahna time.
    "sarva-pitru-amavasya": "",
    # EN: Narak Chaturdashi (Roop Chaudas), Kartika Krishna Chaturdashi (purnimanta), remembers
    #     Krishna's victory over Narakasura. Before sunrise, while the Moon is up, people take an
    #     oil bath with ubtan (Abhyang snan), and a lamp for Yama is lit in the evening.
    "narak-chaturdashi": "",
    # EN: Tulsi Vivah, on Kartika Shukla Dwadashi, is the ceremonial wedding of the tulsi plant (as
    #     Vrinda) to Lord Vishnu as Shaligram. Families decorate the tulsi like a bride and perform
    #     the rites of a wedding; the Hindu wedding season begins after it.
    "tulsi-vivah": "",
    # EN: Kartik Purnima ends the holy month of Kartika. It is a great day for bathing in the Ganga
    #     or a holy river and giving in charity, and also Guru Nanak Jayanti and Tripuri Purnima,
    #     when Shiva destroyed Tripurasura.
    "kartik-purnima": "",
    # EN: Dev Deepawali, the 'Diwali of the gods', is celebrated on Kartik Purnima evening, above
    #     all on the ghats of Varanasi, which are lit with lakhs of diyas. It marks Shiva's victory
    #     over Tripurasura; lamps are offered to the Ganga in Pradosh kaal.
    "dev-deepawali": "",
}

# app/vrat_text.py NOTES["pa"] — tradition notes on dates that differ between almanacs (key = festival slug)  [11]
VRAT_NOTES = {
    # EN: Dates follow Drik Panchang. When Bhadra covers the whole Purnima night and Purnima lasts
    #     most of the next day, Drik moves Holika Dahan to the next evening's Pradosh (as in 2026, 3
    #     March); some almanacs instead give a time late on the first night, after Bhadra ends.
    "holika-dahan": "",
    # EN: Dates follow Drik Panchang's Smarta (default) reckoning, with Rohini nakshatra at midnight
    #     preferred. Vaishnava/ISKCON communities sometimes keep Janmashtami a day later.
    "janmashtami": "",
    # EN: This is the Smarta (householder) date. Where Ekadashi spans two days, Vaishnavas may fast
    #     on the second day.
    "devuthani-ekadashi": "",
    # EN: Dates follow Drik Panchang (Dashami in Aparahna, Shravana nakshatra preferred). In Bengal
    #     and some almanacs Vijayadashami can fall a day later.
    "dussehra": "",
    # EN: Dates follow Drik Panchang (Ashtami at midday; when it is at sunrise only briefly, as in
    #     2023, the previous day). Nahay-khay is the day before and parana the next morning;
    #     regional panchangs (e.g. Mithila) can differ by a day.
    "jivitputrika": "",
    # EN: Two traditions: North India keeps Vat Savitri on Jyeshtha Amavasya (this date);
    #     Maharashtra, Gujarat and the south keep it as Vat Purnima fifteen days later.
    "vat-savitri": "",
    # EN: Two traditions: this is the Purnima (amanta) date of Maharashtra, Gujarat and the south;
    #     North India keeps Vat Savitri on the Amavasya fifteen days earlier.
    "vat-purnima": "",
    # EN: When Jyeshtha is doubled (an adhika month, as in 2026), Drik Panchang keeps Ganga Dussehra
    #     in the adhika Jyeshtha; some almanacs give the nija Jyeshtha date a month later.
    "ganga-dussehra": "",
    # EN: Drik Panchang counts Pitru Paksha from the Pratipada shraddha; Purnima shraddha is on the
    #     day before, and many calendars start the fortnight there.
    "pitru-paksha": "",
    # EN: Drik Panchang publishes Dev Deepawali for Varanasi; the date here uses the same rule
    #     (Purnima in Pradosh), and the Pradosh kaal shown is New Delhi's.
    "dev-deepawali": "",
    # EN: This is the snan-daan day (Purnima at sunrise). When Purnima begins the previous
    #     afternoon, the Purnima fast and Dev Deepawali can fall a day earlier.
    "kartik-purnima": "",
}

# app/vrat_text.py RULES["pa"] — 'how the date is fixed' sentences: head {month}, tithi {paksha} {tithi}, rule.<kind>, key.<observance>  [16]
VRAT_RULES = {
    # EN: {month} (amanta)
    # keep: {month}
    "head": "",
    # EN: {paksha} {tithi}:
    # keep: {paksha} {tithi}
    "tithi": "",
    # EN: tithi prevailing at sunrise
    "rule.udaya": "",
    # EN: tithi prevailing in Pratahkala (first fifth of the day)
    "rule.pratah": "",
    # EN: tithi prevailing in the forenoon (purvahna)
    "rule.purvahna": "",
    # EN: tithi prevailing at Madhyahna (midday fifth of the day)
    "rule.madhyahna": "",
    # EN: tithi prevailing at Aparahna (fourth fifth of the day)
    "rule.aparahna": "",
    # EN: first day on which the tithi is present between sunrise and sunset
    "rule.dina": "",
    # EN: tithi prevailing at sunset
    "rule.sayahna": "",
    # EN: tithi prevailing in Pradosh kaal (after sunset)
    "rule.pradosh": "",
    # EN: tithi prevailing at Nishita kaal (midnight)
    "rule.nishita": "",
    # EN: tithi prevailing at moonrise
    "rule.moonrise": "",
    # EN: Smarta: Ekadashi prevailing at sunrise (second day if at two sunrises); parana next day
    #     after sunrise and after Hari Vasara, within Pratahkala and before Dwadashi ends
    "key.ekadashi": "",
    # EN: the Sun's entry into sidereal Makara (Capricorn); punya kaal follows it until sunset
    "key.makar_sankranti": "",
    # EN: the day before Makar Sankranti
    "key.lohri": "",
    # EN: the day after Holika Dahan
    "key.holi": "",
}

# ----------------------------------------------------------------------------
# nakshatra /nakshatra /rashi /naam-se-kundali-milan
# ----------------------------------------------------------------------------

# app/nakshatra_page_text.py TEXT["pa"] — page text of /nakshatra /rashi (nakshatra_pages.py)  [88]
NAKSHATRA_PAGE_TEXT = {
    # EN: Get your free kundali — find your exact birth nakshatra and Moon sign
    "kundali_cta": "",
    # EN: More free tools
    "more.heading": "",
    # EN: All 27 nakshatras
    "more.naks": "",
    # EN: All 12 rashis
    "more.rashis": "",
    # EN: Naam se Kundali Milan
    "more.milan": "",
    # EN: Kundali Milan (36 guna)
    "more.kundali_milan": "",
    # EN: Today's Rashifal
    "more.rashifal": "",
    # EN: Today's Panchang
    "more.panchang": "",
    # EN: All 27 nakshatras
    "list.naks": "",
    # EN: All 12 rashis
    "list.rashis": "",
    # EN: {name} ({english})
    # keep: {name}
    "sign": "",
    # EN: {name} · {english}
    # keep: {name}
    "sign.pill": "",
    # EN: <strong>Today the Moon is in {name} (at sunrise in New Delhi).</strong>
    # keep: {name}
    "today.same": "",
    # EN: Today's nakshatra is <a href="{href}"><strong>{name}</strong></a> (at sunrise in New
    #     Delhi).
    # keep: {href} {name}
    "today.other": "",
    # EN: Its end time, the tithi and Rahu Kaal are on <a href="{pan}">today's Panchang</a>.
    # keep: {pan}
    "today.tail": "",
    # EN: Nakshatras
    "crumb.naks": "",
    # EN: Rashis
    "crumb.rashis": "",
    # EN: Nakshatra not found
    "nf.nak": "",
    # EN: Rashi not found
    "nf.rashi": "",
    # EN: Nature and traits
    "trait_head": "",
    # EN: male
    "gender.male": "",
    # EN: female
    "gender.female": "",
    # EN: Fire
    "element.Fire": "",
    # EN: Earth
    "element.Earth": "",
    # EN: Air
    "element.Air": "",
    # EN: Water
    "element.Water": "",
    # EN: Movable (Chara)
    "quality.Cardinal": "",
    # EN: Fixed (Sthira)
    "quality.Fixed": "",
    # EN: Dual (Dwiswabhava)
    "quality.Mutable": "",
    # EN: {name} Nakshatra — Deity, Lord, Gana, Yoni, Nadi & Name Letters ({lat}) | {brand}
    # keep: {brand} {name}
    "nak.title": "",
    # EN: {name} nakshatra ({name_hi}): {span}, ruled by {lord}, deity {deity_short}, {gana} gana,
    #     {nadi} nadi, {yoni} yoni. Name syllables {lat} and traits.
    # keep: {gana} {lord} {nadi} {name} {span} {yoni}
    # may also use: {name_en}
    "nak.desc": "",
    # EN: <h1>{name} Nakshatra</h1>
    # keep: {name}
    "nak.h1": "",
    # EN: <p class="hi" lang="hi">{name_hi} नक्षत्र</p>
    # may also use: {name_en} {name}
    "nak.sub": "",
    # EN: <p class="note">These are traditional tendencies, not verdicts. Your full kundali —
    #     ascendant, planets and dasha — gives the personal picture.</p>
    "nak.trait_note": "",
    # EN: Number
    "f.number": "",
    # EN: {n} of 27
    # keep: {n}
    "f.number_v": "",
    # EN: Span (sidereal)
    "f.span": "",
    # EN: Rashi
    "f.rashi": "",
    # EN: Ruling planet (Vimshottari lord)
    "f.lord": "",
    # EN: {lord} <small>{years}-year mahadasha</small>
    # keep: {lord} {years}
    "f.lord_v": "",
    # EN: Deity
    "f.deity": "",
    # EN: Symbol
    "f.symbol": "",
    # EN: Gana
    "f.gana": "",
    # EN: {gana} <small lang="hi">{gana_hi}</small>
    # keep: {gana}
    "f.gana_v": "",
    # EN: Yoni (animal)
    "f.yoni": "",
    # EN: Nadi
    "f.nadi": "",
    # EN: Varna (from its rashi, as used in Guna Milan)
    "f.varna": "",
    # EN: Name syllables (namakshar)
    "f.syl": "",
    # EN: <span class="syl" lang="hi">{syl}</span> <small>{lat}</small>
    # keep: {syl}
    "f.syl_v": "",
    # EN: The four padas and their name syllables
    "pada.title": "",
    # EN: <tr><th>Pada</th><th>Span</th><th>Rashi</th><th>Name syllable</th></tr>
    "pada.head": "",
    # EN: <p class="note">Traditionally a child's name begins with the syllable of the pada the Moon
    #     occupied at birth (namakshar). Syllables follow the 108-pada Swar Siddhanta list (the
    #     Avakahada Chakra) as published by Drik Panchang.</p>
    "pada.note": "",
    # EN: Related
    "rel.heading": "",
    # EN: Today's {name} Rashifal
    # keep: {name}
    "rel.rashifal": "",
    # EN: The 27 Nakshatras — Lords, Deities, Gana & Name Syllables | {brand}
    # keep: {brand}
    "ni.title": "",
    # EN: All 27 nakshatras from Ashwini to Revati: span, rashi, ruling planet, deity, gana, yoni,
    #     nadi and the name syllables of all four padas — consistent with our Kundali Milan tables.
    "ni.desc": "",
    # EN: <h1>The 27 Nakshatras</h1>
    "ni.h1": "",
    # EN: <p class="hi" lang="hi">27 नक्षत्र</p>
    "ni.sub": "",
    # EN: <p>Vedic astrology divides the zodiac into 27 nakshatras (lunar mansions) of 13°20′ each,
    #     and each nakshatra into four padas of 3°20′. The 108 padas fall exactly nine to a sign
    #     across the 12 rashis. Your birth nakshatra is the one the Moon occupied when you were
    #     born: it starts your Vimshottari dasha and drives the Tara, Yoni, Gana and Nadi kootas of
    #     Kundali Milan.</p>
    "ni.intro": "",
    # EN: <tr><th>#</th><th>Nakshatra</th><th>Rashi</th><th>Lord</th><th>Gana</th><th>Name
    #     syllables</th></tr>
    "ni.head": "",
    # EN: {name} Rashi ({english}) — Lord, Element, Nakshatras & Name Letters | {brand}
    # keep: {brand} {name}
    # may also use: {english}
    "rs.title": "",
    # EN: {name} rashi ({english} Moon sign, {name_hi}): ruled by {lord}, {element_lower} element,
    #     {quality_lower} quality. Its 9 nakshatra padas, name syllables ({lat}) and traits.
    # keep: {lord} {name}
    # may also use: {element_lower} {element} {english} {name_en} {quality_lower} {quality}
    "rs.desc": "",
    # EN: <h1>{name} Rashi — {english} Moon Sign</h1>
    # keep: {name}
    # may also use: {english}
    "rs.h1": "",
    # EN: <p class="hi" lang="hi">{name_hi} राशि</p>
    # may also use: {english} {name_en} {name}
    "rs.sub": "",
    # EN: Read today's {name} Rashifal
    # keep: {name}
    "rs.today": "",
    # EN: <p class="note">In Vedic astrology "rashi" usually means the Moon sign — the sign the Moon
    #     occupied at birth, in the sidereal zodiac. It is often different from a Western sun
    #     sign.</p>
    "rs.note": "",
    # EN: Number
    "r.number": "",
    # EN: {n} of 12
    # keep: {n}
    "r.number_v": "",
    # EN: Span (sidereal zodiac)
    "r.span": "",
    # EN: Sign lord
    "r.lord": "",
    # EN: Element
    "r.element": "",
    # EN: Quality
    "r.quality": "",
    # EN: Varna (used in Guna Milan)
    "r.varna": "",
    # EN: Nakshatras
    "r.naks": "",
    # EN: Name syllables (namakshar)
    "r.syl": "",
    # EN: <span class="syl" lang="hi">{syl}</span>
    # keep: {syl}
    "r.syl_v": "",
    # EN: The nine nakshatra padas in this sign
    "rp.title": "",
    # EN: <tr><th>Nakshatra</th><th>Pada</th><th>Degrees in sign</th><th>Syllable</th></tr>
    "rp.head": "",
    # EN: The 12 Rashis — Lords, Elements, Nakshatras & Name Letters | {brand}
    # keep: {brand}
    "ri.title": "",
    # EN: All 12 rashis (Vedic Moon signs) from Mesh to Meen: sign lord, element, quality, the nine
    #     nakshatra padas in each and their name syllables (namakshar).
    "ri.desc": "",
    # EN: <h1>The 12 Rashis (Moon Signs)</h1>
    "ri.h1": "",
    # EN: <p class="hi" lang="hi">12 राशियाँ</p>
    "ri.sub": "",
    # EN: <p>Each rashi spans 30° of the sidereal zodiac and holds exactly nine nakshatra padas.
    #     Your rashi is your Moon sign — the sign the Moon occupied at birth — and it is what
    #     rashifal, Sade Sati and Kundali Milan are read from.</p>
    "ri.intro": "",
    # EN: <tr><th>Rashi</th><th>Lord</th><th>Element</th><th>Nakshatras</th><th>Name
    #     syllables</th></tr>
    "ri.head": "",
    # EN: {name} <small>{english}</small>
    # keep: {name}
    # may also use: {english}
    "ri.name": "",
    # EN: Vata
    "humour.Vata": "",
    # EN: Pitta
    "humour.Pitta": "",
    # EN: Kapha
    "humour.Kapha": "",
}

# app/nakshatra_text.py NAKSHATRA_TRAITS["pa"] — character paragraph of each of the 27 nakshatras (key = slug)  [27]
NAKSHATRA_TRAITS = {
    # EN: Ashwini is the first nakshatra, ruled by the Ashwini Kumaras, the twin healers of the
    #     gods, and symbolised by a horse's head. People with the Moon here are often quick,
    #     energetic and eager to begin things — the first to help, the first to try something new.
    #     Tradition links Ashwini with healing, speed and fresh starts, so many feel drawn to
    #     medicine, sport, travel or any work that needs swift, practical action. The gift of this
    #     nakshatra is initiative and a youthful optimism; the lesson is patience, finishing what
    #     was started with the same enthusiasm with which it began.
    "ashwini": "",
    # EN: Bharani is ruled by Yama, the lord of dharma, and its symbol is the yoni, the womb that
    #     carries and protects new life. People with the Moon here often have strong will, deep
    #     feelings and a serious sense of responsibility. They tend to carry their commitments
    #     through to the end and are not easily swayed. Tradition sees Bharani as the nakshatra of
    #     bearing and nurturing — holding something until it is ready to be born — so creativity,
    #     family, art and work that asks for endurance suit it well. Its strength is steadfastness;
    #     its lesson is balancing desire with restraint and kindness.
    "bharani": "",
    # EN: Krittika is ruled by Agni, the sacred fire, and symbolised by a razor or a flame. Fire
    #     purifies and cuts through confusion, and people with the Moon here are often direct,
    #     principled and sharp in judgement. They can be protective of those they love and are
    #     willing to say what needs to be said. Krittika is also the nakshatra of the six mothers
    #     who nursed Kartikeya, so beneath the sharpness there is real warmth and care. Teaching,
    #     cooking, leadership and any work that needs clarity suit it. Its lesson is to let the fire
    #     warm and guide rather than burn.
    "krittika": "",
    # EN: Rohini is ruled by Brahma, the creator, and symbolised by a chariot or ox-cart. It is said
    #     to be the Moon's favourite nakshatra, and people with the Moon here are often warm,
    #     attractive, artistic and fond of comfort and beauty. They have a gift for making things
    #     grow — gardens, homes, businesses and relationships. Tradition associates Rohini with
    #     fertility, abundance and steady progress, so agriculture, the arts, design, food and
    #     hospitality suit it well. Its nature is gentle and settled; its lesson is to enjoy what is
    #     beautiful without holding on too tightly to it.
    "rohini": "",
    # EN: Mrigashira is ruled by Soma, the Moon, and its symbol is a deer's head — the deer that is
    #     always alert, curious and searching. People with the Moon here are often gentle,
    #     inquisitive and fond of learning, travel and conversation. They enjoy exploring ideas and
    #     places and rarely stop asking questions. Tradition sees Mrigashira as the seeker's
    #     nakshatra, which suits research, writing, teaching, trade and any work that rewards
    #     curiosity. Its charm is a light, friendly mind; its lesson is to settle on what has been
    #     found, so that the search leads somewhere rather than becoming restlessness.
    "mrigashira": "",
    # EN: Ardra is ruled by Rudra, the storm form of Shiva, and symbolised by a teardrop or a
    #     diamond. As a storm clears the air and brings rain, people with the Moon here often have a
    #     strong, searching intellect and the ability to see through things to the truth. They can
    #     feel deeply and are not afraid of change. Tradition links Ardra with renewal after
    #     difficulty, so research, technology, writing, counselling and problem-solving suit it
    #     well. Its gift is honesty and a sharp mind; its lesson is to let feelings pass like the
    #     rain, leaving the ground greener.
    "ardra": "",
    # EN: Punarvasu is ruled by Aditi, the boundless mother of the gods, and symbolised by a bow and
    #     quiver. Its name means "return of the light", and people with the Moon here are often
    #     optimistic, generous and able to begin again after any setback. They tend to be content
    #     with simple things, good-humoured and caring towards family and guests. Tradition sees
    #     Punarvasu as a nakshatra of renewal and homecoming, suited to teaching, counselling,
    #     writing, travel and caring work. Its blessing is a hopeful, forgiving heart; its lesson is
    #     to aim the arrow — to choose a direction and stay with it.
    "punarvasu": "",
    # EN: Pushya is ruled by Brihaspati, the guru of the gods, and symbolised by a cow's udder or a
    #     lotus — images of nourishment. It is counted among the most auspicious nakshatras, and
    #     people with the Moon here are often caring, dependable, devoted and generous with their
    #     time. They like to support others, keep traditions and build something lasting. Tradition
    #     links Pushya with nourishment and wisdom, so teaching, counselling, food, social service,
    #     finance and spiritual work suit it well. Its gift is a steady, protective kindness; its
    #     lesson is to nourish oneself as faithfully as one nourishes others.
    "pushya": "",
    # EN: Ashlesha is ruled by the Nagas, the serpent deities, and symbolised by a coiled serpent —
    #     an image of kundalini, hidden energy and deep wisdom. People with the Moon here are often
    #     perceptive, intelligent and good at understanding what others leave unsaid. They can be
    #     persuasive and strategic, with a strong instinct for self-protection. Tradition links
    #     Ashlesha with insight and with the healing knowledge of herbs, so psychology, research,
    #     medicine, writing and negotiation suit it well. Its gift is penetrating understanding; its
    #     lesson is to use that insight to embrace and heal, the way the serpent's coil protects.
    "ashlesha": "",
    # EN: Magha is ruled by the Pitris, the ancestors, and symbolised by a royal throne. People with
    #     the Moon here often carry a natural dignity, a respect for family and tradition, and a
    #     wish to live up to the name they were given. They can be generous leaders who take
    #     responsibility for their people. Tradition links Magha with lineage, honour and authority,
    #     so leadership, administration, history, law and work that preserves heritage suit it well.
    #     Its gift is nobility of heart; its lesson is to wear the crown lightly — to lead through
    #     service and to honour the ancestors through good deeds.
    "magha": "",
    # EN: Purva Phalguni is ruled by Bhaga, the god of fortune and marital happiness, and symbolised
    #     by the front legs of a bed — an image of rest and enjoyment. People with the Moon here are
    #     often warm, charming, creative and fond of celebration, music and good company. They bring
    #     people together and know how to relax and enjoy what they have earned. Tradition links
    #     Purva Phalguni with love, the arts and leisure, so entertainment, design, hospitality and
    #     relationship-centred work suit it well. Its gift is joy that is easily shared; its lesson
    #     is balance between pleasure and duty.
    "purva-phalguni": "",
    # EN: Uttara Phalguni is ruled by Aryaman, the god of friendship, contracts and marriage vows,
    #     and symbolised by the back legs of a bed. Where its twin Purva Phalguni enjoys, Uttara
    #     Phalguni commits. People with the Moon here are often reliable, helpful, fair-minded and
    #     loyal to friends and partners. They keep their word and like to be of real use to others.
    #     Tradition links this nakshatra with patronage and lasting partnerships, so management,
    #     public service, counselling, law and charitable work suit it well. Its gift is dependable
    #     kindness; its lesson is to accept help as gracefully as it is given.
    "uttara-phalguni": "",
    # EN: Hasta is ruled by Savitr, the radiant Sun, and symbolised by a hand. People with the Moon
    #     here are often skilful, practical, witty and clever with their hands as well as their
    #     minds. They like to get things done and can turn an idea into something real. Tradition
    #     links Hasta with craftsmanship, healing touch and resourcefulness, so crafts, the arts,
    #     surgery, massage, writing, trade and any skilled trade suit it well. Its gift is the
    #     ability to make and to mend; its lesson is to hold things with an open hand, trusting that
    #     effort brings its own rewards.
    "hasta": "",
    # EN: Chitra is ruled by Tvashtr, also known as Vishwakarma, the divine architect, and
    #     symbolised by a bright jewel. Its name means "brilliant" or "picture", and people with the
    #     Moon here often have a strong sense of beauty, design and form. They enjoy creating things
    #     that are both useful and attractive, and they notice detail. Tradition links Chitra with
    #     architecture, the arts and craftsmanship, so design, engineering, fashion, jewellery,
    #     photography and planning suit it well. Its gift is the eye of an artist and the hand of a
    #     builder; its lesson is to value inner beauty as much as outer polish.
    "chitra": "",
    # EN: Swati is ruled by Vayu, the wind, and symbolised by a young shoot swaying in the breeze —
    #     flexible, independent and able to bend without breaking. People with the Moon here often
    #     value freedom, fairness and their own way of doing things. They are usually diplomatic,
    #     courteous and good at business and negotiation. Tradition links Swati with trade, travel
    #     and self-reliance, so commerce, law, diplomacy, communication and independent work suit it
    #     well. Its gift is adaptability and a gentle, balanced manner; its lesson is to put down
    #     roots, so that the young shoot can grow into a strong tree.
    "swati": "",
    # EN: Vishakha is ruled by Indra and Agni together, and symbolised by a triumphal arch decorated
    #     with leaves. People with the Moon here are often purposeful, ambitious and determined to
    #     reach the goal they have set. They have energy, conviction and the patience to keep going
    #     over a long road. Tradition calls Vishakha the nakshatra of purpose, so leadership,
    #     research, politics, sales, teaching and any long-term mission suit it well. Its gift is
    #     focus and the ability to inspire others towards a shared aim; its lesson is to enjoy the
    #     journey, not only the arch at its end.
    "vishakha": "",
    # EN: Anuradha is ruled by Mitra, the god of friendship and cooperation, and symbolised by a
    #     lotus that blooms out of muddy water. People with the Moon here are often loyal friends,
    #     devoted to their ideals and able to keep going with quiet faith in difficult places. They
    #     are good at bringing people together in groups and organisations. Tradition links Anuradha
    #     with friendship, devotion and success away from home, so teamwork, organisation,
    #     counselling, travel and spiritual practice suit it well. Its gift is the ability to
    #     blossom anywhere; its lesson is to be as gentle with oneself as with friends.
    "anuradha": "",
    # EN: Jyeshtha is ruled by Indra, king of the gods, and symbolised by a circular amulet or
    #     earring. Its name means "the eldest", and people with the Moon here often take on
    #     responsibility early, protect those around them and carry a quiet authority. They are
    #     resourceful, perceptive and capable under pressure. Tradition links Jyeshtha with
    #     seniority and protection, so leadership, management, administration, security and any role
    #     that looks after others suit it well. Its gift is courage and capability; its lesson is to
    #     lead with humility and to let others share the load rather than carrying everything alone.
    "jyeshtha": "",
    # EN: Mula is ruled by Nirriti and symbolised by a bunch of roots. Its name means "the root",
    #     and people with the Moon here are often drawn to get to the bottom of things — to find the
    #     origin of a question, an idea or a tradition. They can be independent, philosophical and
    #     unafraid to start again from first principles. Tradition links Mula with investigation and
    #     with letting go of what is no longer needed, so research, medicine, philosophy, botany and
    #     spiritual inquiry suit it well. Its gift is depth; its lesson is that clearing old ground
    #     makes room for new growth.
    "mula": "",
    # EN: Purva Ashadha is ruled by Apas, the cosmic waters, and symbolised by a winnowing fan or an
    #     elephant tusk. Its name means "the early invincible", and people with the Moon here are
    #     often confident, persuasive and full of conviction. Like water, they can be gentle and yet
    #     wear down any obstacle in time. Tradition links Purva Ashadha with purification and with
    #     victory won through persistence, so teaching, law, debate, the arts, shipping and anything
    #     to do with water suit it well. Its gift is optimism and inner strength; its lesson is to
    #     stay open to other views while holding firm to its own.
    "purva-ashadha": "",
    # EN: Uttara Ashadha is ruled by the Vishvedevas, the universal gods, and symbolised by an
    #     elephant tusk. Its name means "the later invincible" — the victory that lasts because it
    #     was earned honestly. People with the Moon here are often principled, patient, responsible
    #     and respected for their integrity. They take the long view and finish what they commit to.
    #     Tradition links Uttara Ashadha with righteous leadership, so government, management, law,
    #     teaching and social causes suit it well. Its gift is steady, ethical strength; its lesson
    #     is to keep a little lightness and warmth alongside the seriousness of duty.
    "uttara-ashadha": "",
    # EN: Shravana is ruled by Vishnu, the preserver, and symbolised by an ear or three footprints.
    #     Its name means "hearing", and people with the Moon here are often good listeners, eager
    #     learners and keepers of knowledge and tradition. They learn by listening and pass on what
    #     they have learned. Tradition links Shravana with wisdom gained through study and with
    #     connecting people, so teaching, counselling, media, languages, music and travel suit it
    #     well. Its gift is attentive understanding and a wish to be useful; its lesson is to listen
    #     to one's own inner voice as carefully as to others.
    "shravana": "",
    # EN: Dhanishta is ruled by the eight Vasus, gods of abundance, and symbolised by a drum. Its
    #     name means "the wealthiest", and people with the Moon here often have rhythm, energy and a
    #     talent for music, dance or teamwork. They are generous, sociable and able to keep a group
    #     moving together. Tradition links Dhanishta with prosperity and with sound, so music,
    #     performance, sport, property, finance and community work suit it well. Its gift is the
    #     ability to set the beat that others follow; its lesson is to listen as well as play,
    #     leaving space for others' rhythms.
    "dhanishta": "",
    # EN: Shatabhisha is ruled by Varuna, lord of the cosmic waters and of truth, and symbolised by
    #     an empty circle. Its name means "a hundred healers", and people with the Moon here are
    #     often independent thinkers, private, truthful and drawn to understanding how things really
    #     work. They can see patterns others miss. Tradition links Shatabhisha with healing and with
    #     the search for hidden truth, so medicine, research, science, technology, astronomy and
    #     alternative healing suit it well. Its gift is clear, original insight; its lesson is to
    #     let others into the circle, sharing what is understood with warmth.
    "shatabhisha": "",
    # EN: Purva Bhadrapada is ruled by Aja Ekapada, the one-footed form of Shiva, and symbolised by
    #     swords or the front legs of a cot. People with the Moon here are often idealistic, intense
    #     and willing to give themselves fully to a cause they believe in. They can be eloquent,
    #     generous and deeply spiritual. Tradition links Purva Bhadrapada with transformation and
    #     with the fire of tapas — sincere effort for a higher aim — so social reform, philosophy,
    #     writing, research and spiritual life suit it well. Its gift is passionate commitment; its
    #     lesson is to temper intensity with patience and calm.
    "purva-bhadrapada": "",
    # EN: Uttara Bhadrapada is ruled by Ahir Budhnya, the serpent of the deep waters, and symbolised
    #     by the back legs of a cot or twins. Where Purva Bhadrapada burns, Uttara Bhadrapada
    #     settles into calm depth. People with the Moon here are often wise, patient, composed and
    #     compassionate, with self-control and a gift for counsel. They tend to think before they
    #     speak and are steady in difficult times. Tradition links this nakshatra with depth,
    #     renunciation and kindness, so counselling, charity, teaching, research and spiritual
    #     practice suit it well. Its gift is serene wisdom; its lesson is to share it actively, not
    #     only privately.
    "uttara-bhadrapada": "",
    # EN: Revati, the last nakshatra, is ruled by Pushan, the nourisher who guides travellers and
    #     protects herds on their way, and symbolised by a fish. People with the Moon here are often
    #     gentle, kind, imaginative and protective of the weak, with a love of animals, art and
    #     music. They make good companions on any journey and help others reach their destination
    #     safely. Tradition links Revati with safe journeys, prosperity and completion, so caring
    #     work, the arts, travel, hospitality and spiritual life suit it well. Its gift is
    #     compassion and faith; its lesson is to care for oneself while caring for everyone else.
    "revati": "",
}

# app/nakshatra_text.py RASHI_TRAITS["pa"] — character paragraph of each of the 12 rashis (key = slug)  [12]
RASHI_TRAITS = {
    # EN: Mesh (Aries) is the first rashi, a movable fire sign ruled by Mars. People with the Moon
    #     in Mesh are often energetic, direct, courageous and quick to act — natural starters who
    #     enjoy a challenge and like to lead from the front. They are honest about their feelings
    #     and recover quickly from setbacks. Their emotional life is warm and spontaneous, and they
    #     bring enthusiasm wherever they go. Work that rewards initiative — sport, the armed forces,
    #     engineering, entrepreneurship, surgery — often suits them. Their growth lies in patience
    #     and in listening before acting, so that their courage is matched by care for others.
    "mesh": "",
    # EN: Vrishabh (Taurus) is a fixed earth sign ruled by Venus, and the Moon is exalted here.
    #     People with the Moon in Vrishabh are often calm, patient, loyal and steady, with a love of
    #     comfort, good food, music and beautiful things. They build slowly and surely, and what
    #     they build tends to last. Emotionally they are dependable and affectionate, preferring
    #     security to drama. Finance, agriculture, the arts, food, design and any work that rewards
    #     persistence often suit them. Their growth lies in flexibility — welcoming change when it
    #     comes, and holding possessions and opinions a little more lightly.
    "vrishabh": "",
    # EN: Mithun (Gemini) is a dual air sign ruled by Mercury. People with the Moon in Mithun are
    #     often curious, witty, talkative and quick to learn, with many interests and a gift for
    #     connecting ideas and people. They enjoy conversation, reading, travel and anything that
    #     keeps the mind busy. Emotionally they need variety and a partner who is also a friend they
    #     can talk to. Writing, teaching, media, sales, technology and trade often suit them. Their
    #     growth lies in depth and focus — choosing a few things and seeing them through — and in
    #     giving their own feelings the attention they give to ideas.
    "mithun": "",
    # EN: Kark (Cancer) is a movable water sign ruled by the Moon itself, so the Moon is at home
    #     here. People with the Moon in Kark are often caring, sensitive, intuitive and devoted to
    #     family and home. They remember kindness, protect those they love and create warmth
    #     wherever they live. Their moods can change like the tides, but their loyalty runs deep.
    #     Nursing, teaching, hospitality, food, real estate, counselling and public service often
    #     suit them. Their growth lies in trusting their own strength, letting go of old hurts and
    #     allowing others to care for them in return.
    "kark": "",
    # EN: Simha (Leo) is a fixed fire sign ruled by the Sun. People with the Moon in Simha are often
    #     generous, dignified, confident and warm-hearted, with a natural sense of leadership and a
    #     love of recognition. They are loyal to those who trust them and protective of their family
    #     and friends. Emotionally they are proud and open-hearted, and they shine when appreciated.
    #     Leadership, administration, politics, the performing arts, teaching and government service
    #     often suit them. Their growth lies in humility — letting others share the stage, and
    #     finding confidence from within rather than from applause.
    "simha": "",
    # EN: Kanya (Virgo) is a dual earth sign ruled by Mercury. People with the Moon in Kanya are
    #     often practical, analytical, modest and helpful, with an eye for detail and a wish to make
    #     things work properly. They show care through service — fixing, organising and looking
    #     after the small things others overlook. Emotionally they can be reserved, but they are
    #     deeply dependable. Medicine, accounting, research, editing, nutrition, teaching and any
    #     precise craft often suit them. Their growth lies in self-acceptance: being as kind to
    #     their own imperfections as they are patient with other people's needs.
    "kanya": "",
    # EN: Tula (Libra) is a movable air sign ruled by Venus, symbolised by the scales. People with
    #     the Moon in Tula are often gracious, fair-minded, sociable and diplomatic, with a strong
    #     sense of beauty and justice. They value harmony in relationships and are good at seeing
    #     both sides of a question. Emotionally they need partnership and feel most at ease when
    #     things around them are balanced. Law, diplomacy, design, fashion, the arts, counselling
    #     and business partnerships often suit them. Their growth lies in decisiveness — trusting
    #     their own judgement and accepting that a little disagreement can be healthy.
    "tula": "",
    # EN: Vrishchik (Scorpio) is a fixed water sign ruled by Mars. People with the Moon in Vrishchik
    #     are often intense, perceptive, determined and deeply loyal, with feelings that run far
    #     below the surface. They are not satisfied with appearances and want to understand what is
    #     really going on. Once they commit — to a person, a cause or a goal — they rarely let go.
    #     Research, investigation, medicine, psychology, finance and crisis work often suit them.
    #     Their growth lies in trust and forgiveness: letting others in, and allowing old feelings
    #     to transform rather than be held.
    "vrishchik": "",
    # EN: Dhanu (Sagittarius) is a dual fire sign ruled by Jupiter, symbolised by the archer. People
    #     with the Moon in Dhanu are often optimistic, honest, generous and philosophical, with a
    #     love of learning, travel and freedom. They look for meaning in life and enjoy sharing what
    #     they have learned. Emotionally they are open and cheerful, and they need room to grow.
    #     Teaching, law, religion and philosophy, publishing, travel and sport often suit them.
    #     Their growth lies in following through — giving the same attention to the details of daily
    #     life that they give to big ideas and distant horizons.
    "dhanu": "",
    # EN: Makar (Capricorn) is a movable earth sign ruled by Saturn. People with the Moon in Makar
    #     are often responsible, disciplined, practical and ambitious in a patient, long-term way.
    #     They take duty seriously, work steadily and earn respect over time. Emotionally they can
    #     seem reserved, but they show love through reliability and quiet support. Administration,
    #     management, engineering, government service, finance and any field that rewards
    #     perseverance often suit them. Their growth lies in warmth and rest — allowing themselves
    #     joy along the way, and remembering that their worth is not measured only by achievement.
    "makar": "",
    # EN: Kumbh (Aquarius) is a fixed air sign ruled by Saturn, symbolised by the water-bearer who
    #     pours knowledge out for all. People with the Moon in Kumbh are often independent,
    #     humanitarian, inventive and loyal to friends and ideals. They think about the wider
    #     community and enjoy new ideas, science and reform. Emotionally they value friendship and
    #     freedom, and they show care through principle and action. Science, technology, social
    #     work, research, education and community organisations often suit them. Their growth lies
    #     in closeness — letting their warmth show to individuals as well as to humanity as a whole.
    "kumbh": "",
    # EN: Meen (Pisces) is a dual water sign ruled by Jupiter, the last of the twelve rashis. People
    #     with the Moon in Meen are often compassionate, imaginative, gentle and spiritually
    #     inclined, with a deep sensitivity to the feelings of others. They forgive easily, help
    #     without being asked and are moved by music, art and devotion. Emotionally they are open-
    #     hearted and intuitive. Healing, counselling, the arts, music, charity, teaching and
    #     spiritual work often suit them. Their growth lies in healthy boundaries — caring for
    #     others without losing themselves, and turning their rich imagination into practical
    #     action.
    "meen": "",
}

# app/nakshatra_text.py FACTS["pa"] — deity.<slug> and symbol.<slug> of each nakshatra  [54]
NAKSHATRA_FACTS = {
    # EN: The Ashwini Kumaras, the divine physicians
    "deity.ashwini": "",
    # EN: A horse's head
    "symbol.ashwini": "",
    # EN: Yama, lord of dharma
    "deity.bharani": "",
    # EN: The yoni (womb)
    "symbol.bharani": "",
    # EN: Agni, the fire
    "deity.krittika": "",
    # EN: A razor or flame
    "symbol.krittika": "",
    # EN: Brahma (Prajapati)
    "deity.rohini": "",
    # EN: A chariot or ox-cart
    "symbol.rohini": "",
    # EN: Soma, the Moon
    "deity.mrigashira": "",
    # EN: A deer's head
    "symbol.mrigashira": "",
    # EN: Rudra
    "deity.ardra": "",
    # EN: A teardrop or diamond
    "symbol.ardra": "",
    # EN: Aditi, mother of the gods
    "deity.punarvasu": "",
    # EN: A bow and quiver
    "symbol.punarvasu": "",
    # EN: Brihaspati, guru of the gods
    "deity.pushya": "",
    # EN: A cow's udder or lotus
    "symbol.pushya": "",
    # EN: The Nagas (serpent deities)
    "deity.ashlesha": "",
    # EN: A coiled serpent
    "symbol.ashlesha": "",
    # EN: The Pitris (ancestors)
    "deity.magha": "",
    # EN: A royal throne
    "symbol.magha": "",
    # EN: Bhaga, giver of fortune
    "deity.purva-phalguni": "",
    # EN: The front legs of a bed
    "symbol.purva-phalguni": "",
    # EN: Aryaman, lord of friendship
    "deity.uttara-phalguni": "",
    # EN: The back legs of a bed
    "symbol.uttara-phalguni": "",
    # EN: Savitr, the Sun
    "deity.hasta": "",
    # EN: A hand
    "symbol.hasta": "",
    # EN: Tvashtr (Vishwakarma), the divine architect
    "deity.chitra": "",
    # EN: A bright jewel
    "symbol.chitra": "",
    # EN: Vayu, the wind
    "deity.swati": "",
    # EN: A young shoot swaying in the wind
    "symbol.swati": "",
    # EN: Indra and Agni (Indragni)
    "deity.vishakha": "",
    # EN: A triumphal arch
    "symbol.vishakha": "",
    # EN: Mitra, lord of friendship
    "deity.anuradha": "",
    # EN: A lotus
    "symbol.anuradha": "",
    # EN: Indra, king of the gods
    "deity.jyeshtha": "",
    # EN: A circular amulet or earring
    "symbol.jyeshtha": "",
    # EN: Nirriti
    "deity.mula": "",
    # EN: A bunch of roots
    "symbol.mula": "",
    # EN: Apas, the waters
    "deity.purva-ashadha": "",
    # EN: A winnowing fan or elephant tusk
    "symbol.purva-ashadha": "",
    # EN: The Vishvedevas (universal gods)
    "deity.uttara-ashadha": "",
    # EN: An elephant tusk
    "symbol.uttara-ashadha": "",
    # EN: Vishnu
    "deity.shravana": "",
    # EN: An ear, or three footprints
    "symbol.shravana": "",
    # EN: The eight Vasus
    "deity.dhanishta": "",
    # EN: A drum (mridanga)
    "symbol.dhanishta": "",
    # EN: Varuna, lord of the waters
    "deity.shatabhisha": "",
    # EN: An empty circle
    "symbol.shatabhisha": "",
    # EN: Aja Ekapada
    "deity.purva-bhadrapada": "",
    # EN: Swords, or the front legs of a cot
    "symbol.purva-bhadrapada": "",
    # EN: Ahir Budhnya, serpent of the deep
    "deity.uttara-bhadrapada": "",
    # EN: The back legs of a cot, or twins
    "symbol.uttara-bhadrapada": "",
    # EN: Pushan, the nourisher and guide
    "deity.revati": "",
    # EN: A fish (or a drum)
    "symbol.revati": "",
}

# app/naam_milan_text.py TEXT["pa"] — page text of /naam-se-kundali-milan  [34]
NAAM_MILAN_TEXT = {
    # EN: Naam se Kundali Milan — Match 36 Gunas by Name, Free | {brand}
    # keep: {brand}
    "title": "",
    # EN: Kundali milan by name: the first syllable of the boy's and girl's names gives each
    #     nakshatra and rashi, then the full 36-guna Ashtakoot match. Type names in Hindi or English
    #     — free, no sign-up.
    "desc": "",
    # EN: Naam se Kundali Milan
    "crumb": "",
    # EN: <h1>Naam se Kundali Milan — Match by Name</h1>
    "h1": "",
    # EN: <p class="hi" lang="hi">नाम से कुंडली मिलान</p>
    "sub": "",
    # EN: <p>When birth times are not known, tradition matches a couple by the <strong>first
    #     syllable of their names</strong>. Type both names in Hindi or English: we show the
    #     syllable used, its nakshatra pada and rashi, and the full 36-guna match.</p>
    "intro": "",
    # EN: Open birth-chart Kundali Milan
    "open_milan": "",
    # EN: Automatic, from the name
    "auto": "",
    # EN: Other likely syllables for this name
    "alt_head": "",
    # EN: All 108 syllables
    "all_head": "",
    # EN: Boy's name (groom)
    "boy_label": "",
    # EN: Girl's name (bride)
    "girl_label": "",
    # EN: e.g. Ram or राम
    "boy_ph": "",
    # EN: e.g. Sita or सीता
    "girl_ph": "",
    # EN: Change the first syllable
    "pick": "",
    # EN: Match the gunas
    "button": "",
    # EN: This syllable belongs to Abhijit, the 28th nakshatra; in the 27-nakshatra wheel it is
    #     counted in Uttara Ashadha pada 4.
    "via.abhijit": "",
    # EN: By the traditional rule, ब is read as व, and श as ष (with the a-vowel) or स.
    "via.alias": "",
    # EN: This exact syllable is not in the 108-syllable list, so the nearest syllable with the same
    #     consonant was used — change it below if you prefer.
    "via.nearest": "",
    # EN: An English spelling cannot settle this syllable (e.g. T = त or ट), so the most common
    #     reading was used — pick another below if needed.
    "via.latin": "",
    # EN: You chose this syllable.
    "via.chosen": "",
    # EN: Could not read a first syllable from this name — pick one from the list below.
    "unreadable": "",
    # EN: pada
    "pada": "",
    # EN: Result
    "result": "",
    # EN: <tr><th></th><th>First syllable</th><th>Nakshatra</th><th>Rashi</th></tr>
    "res.head": "",
    # EN: Boy
    "boy": "",
    # EN: Girl
    "girl": "",
    # EN: <tr><th>Koota</th><th>Points</th><th>Why</th></tr>
    "res.th": "",
    # EN: Total
    "total": "",
    # EN: <strong>Mangal dosha: not applicable.</strong> Mangal dosha depends on where Mars stood
    #     from the Lagna, Moon and Venus at birth — a name cannot tell you that. Use birth-chart
    #     matching for it.
    "mangal": "",
    # EN: Match by birth details instead — more accurate, free
    "res.cta": "",
    # EN: <div class="box"><p><strong>Please note:</strong> name-based matching is a traditional
    #     shortcut, used when birth details are not known. It assumes each name was chosen from the
    #     syllable of the person's birth nakshatra — which today is often not the case. Matching
    #     from the date, time and place of birth is far more accurate, and is the only way to check
    #     Mangal dosha.</p></div>
    "caveat": "",
    # EN: <tr><th>Rashi</th><th>Name syllables</th></tr>
    "syl.head": "",
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
    "explainer": "",
}

# app/naam_milan_text.py ENGINE["pa"] — score-band notes and the convention note of a naam-milan result  [5]
NAAM_MILAN_ENGINE = {
    # EN: Below the traditional minimum of 18 gunas.
    "band_note0": "",
    # EN: In the traditional 18-24 gunas band.
    "band_note1": "",
    # EN: In the traditional 25-32 gunas band.
    "band_note2": "",
    # EN: In the traditional 33-36 gunas band.
    "band_note3": "",
    # EN: The 18/25/33 guna thresholds are a widely used convention, not a measurement. Astrologers
    #     often accept a lower total if the heavily weighted kootas are free of dosha.
    "convention_note": "",
}

# ----------------------------------------------------------------------------
# muhurat   /muhurat/<kind>-<year>
# ----------------------------------------------------------------------------

# app/muhurat_text.py TEXT["pa"] — page text of /muhurat/<kind>-<year> (the mundan-only keys are MUHURAT_MUNDAN)  [37]
MUHURAT_TEXT = {
    # EN: Vivah Muhurat
    "kind.vivah": "",
    # EN: Griha Pravesh Muhurat
    "kind.griha-pravesh": "",
    # EN: wedding
    "noun.vivah": "",
    # EN: house-warming
    "noun.griha-pravesh": "",
    # EN: {name} {year}: Auspicious {noun_title} Dates (New Delhi) | {brand}
    # keep: {brand} {year}
    # may also use: {name} {noun_title} {noun}
    "title": "",
    # EN: {name} {year}: auspicious {noun} dates
    # keep: {year}
    # may also use: {name} {noun}
    "h1": "",
    # EN: {name} {year} for New Delhi — month-by-month auspicious {noun} dates with tithi and
    #     nakshatra. {count} dates; Chaturmas, Kharmas, Adhik Maas, Pitru Paksha and Guru/Shukra
    #     asta explained.
    # keep: {count} {year}
    # may also use: {name} {noun}
    "desc": "",
    # EN: <p class="hi" lang="hi">{name_hi} {year}</p>
    # keep: {year}
    # may also use: {name} {noun}
    "sub": "",
    # EN: {label} · IST
    # keep: {label}
    "place": "",
    # EN: <p>By the panchang there are <strong>{count}</strong> {name_lower} dates in {year} for New
    #     Delhi, in {months}. Each date passes the classical checks on the sunrise tithi, nakshatra,
    #     weekday, yoga and Bhadra, and falls outside Chaturmas, Kharmas, Adhik Maas, Pitru Paksha
    #     and the combustion (asta) of Jupiter and Venus.</p>
    # keep: {count} {months} {year}
    # may also use: {name_lower} {name} {noun}
    "intro": "",
    # EN: <p><strong>Timings vary by city.</strong> These dates are reckoned from New Delhi's
    #     sunrise; elsewhere a tithi or nakshatra can change on a different day. The exact muhurat
    #     (lagna) for a wedding or griha pravesh should be fixed by your family priest. Check your
    #     own city in the Muhurat Finder.</p>
    "note": "",
    # EN: Find muhurat for your city — free
    "cta": "",
    # EN: {name} {year}
    # keep: {name} {year}
    "crumb": "",
    # EN: More muhurat dates
    "more": "",
    # EN: {name} {year}
    # keep: {name} {year}
    "link.kind": "",
    # EN: Today's Panchang
    "link.panchang": "",
    # EN: Kundali Milan
    "link.milan": "",
    # EN: When there is no {name_lower} in {year}
    # keep: {year}
    # may also use: {name_lower} {name} {noun}
    "periods.h2": "",
    # EN: No {name_lower} is given during these periods. The dates are computed from the panchang
    #     (New Delhi, sunrise):
    # may also use: {name_lower} {name} {noun}
    "periods.intro": "",
    # EN: <li><strong>{period}</strong>, {range} — {about}.</li>
    # keep: {about} {period} {range}
    "periods.item": "",
    # EN: No {name_lower} in {month} — {periods}.
    # keep: {month} {periods}
    # may also use: {name_lower} {name} {noun}
    "none.periods": "",
    # EN: No {name_lower} in {month} — no day this month passes the tithi, nakshatra, weekday and
    #     yoga checks.
    # keep: {month}
    # may also use: {name_lower} {name} {noun}
    "none.plain": "",
    # EN: <tr><th>Date</th><th>Day</th><th>Tithi</th><th>Nakshatra</th></tr>
    "th": "",
    # EN: Muhurat page not found
    "nf.title": "",
    # EN: Open the Muhurat Finder
    "nf.open": "",
    # EN: Chaturmas
    "period.chaturmas": "",
    # EN: Devshayani Ekadashi to Devuthani Ekadashi, when Lord Vishnu is in yoga-nidra
    "period_about.chaturmas": "",
    # EN: Kharmas
    "period.kharmas": "",
    # EN: the Sun in Dhanu (Sagittarius) or Meena (Pisces)
    "period_about.kharmas": "",
    # EN: Adhik Maas
    "period.adhik_maas": "",
    # EN: an intercalary lunar month with no solar ingress
    "period_about.adhik_maas": "",
    # EN: Pitru Paksha
    "period.pitru_paksha": "",
    # EN: Bhadrapada Purnima to Sarva Pitru Amavasya, the fortnight of shraddha
    "period_about.pitru_paksha": "",
    # EN: Shukra Asta
    "period.shukra_asta": "",
    # EN: Venus combust (too close to the Sun to be seen), with 3 days either side
    "period_about.shukra_asta": "",
    # EN: Guru Asta
    "period.guru_asta": "",
    # EN: Jupiter combust (too close to the Sun to be seen), with 3 days either side
    "period_about.guru_asta": "",
}

# app/muhurat_text.py MUNDAN["pa"] — the mundan (first haircut) muhurat's own wording  [5]
MUHURAT_MUNDAN = {
    # EN: Mundan Muhurat
    "kind.mundan": "",
    # EN: mundan
    "noun.mundan": "",
    # EN: <p><strong>Timings vary by city.</strong> These dates are reckoned from New Delhi's
    #     sunrise; elsewhere a tithi or nakshatra can change on a different day. The exact muhurat
    #     for the mundan (chudakarma) should be fixed by your family priest. Check your own city in
    #     the Muhurat Finder.</p>
    "note.mundan": "",
    # EN: {name} {year}: the rules these dates follow
    # keep: {name} {year}
    "rules.h2": "",
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
    "rules.body": "",
}

# app/muhurat_text.py MONTHS["pa"] — only if this page must spell the months differently from names_<code>.MONTHS; else leave ()  [12]
# (optional: may stay empty)
MUHURAT_MONTHS = ()   # or 12 month names, January first

# ----------------------------------------------------------------------------
# recurring /purnima-<year> /amavasya-<year> /pradosh-vrat-<year> ... (DIVASTRO-141)
# ----------------------------------------------------------------------------

# app/recurring_text.py TEXT["pa"] — page text of /purnima-<year>, /amavasya-<year>, /pradosh-vrat-<year> ... (the keys it shares with VRAT_TEXT are taken from there)  [60]
RECURRING_TEXT = {
    # EN: Full Moon Dates and Tithi Time
    "what.purnima": "",
    # EN: New Moon Dates and Tithi Time
    "what.amavasya": "",
    # EN: All Dates and Pradosh Puja Time
    "what.pradosh": "",
    # EN: All Dates and Moonrise Time
    "what.sankashti": "",
    # EN: All Dates and Nishita Puja Time
    "what.masik_shivratri": "",
    # EN: All Dates and Kala Bhairav Puja
    "what.kalashtami": "",
    # EN: {name} {year}: {what} (New Delhi)
    # keep: {name} {what} {year}
    "title": "",
    # EN: {name} {year}: {what}
    # keep: {name} {what} {year}
    "h1": "",
    # EN: All {count} {name} dates in {year} with weekday, Hindu month and tithi start and end for
    #     New Delhi. {about}{keytime}{next}
    # keep: {about} {count} {keytime} {name} {next} {year}
    "desc": "",
    # EN: Full-moon vrat days for Satyanarayan puja, bathing and charity.
    "desc.about.purnima": "",
    # EN: New-moon days for shraddha and tarpan, with Somvati and Shani Amavasya.
    "desc.about.amavasya": "",
    # EN: Lord Shiva's twilight fast on Trayodashi, with the puja window.
    "desc.about.pradosh": "",
    # EN: Lord Ganesha's fast on Krishna Chaturthi, broken after moonrise.
    "desc.about.sankashti": "",
    # EN: The monthly night of Shiva on Krishna Chaturdashi, with the midnight puja.
    "desc.about.masik_shivratri": "",
    # EN: Kala Bhairava worship on Krishna Ashtami, every month.
    "desc.about.kalashtami": "",
    # EN: Includes {label}.
    # keep: {label}
    "desc.key": "",
    # EN: Next: {date}.
    # keep: {date}
    "desc.next": "",
    # EN: The next {name} is on <strong>{when}</strong> ({details}).
    # keep: {details} {name} {when}
    "ans.next": "",
    # EN: The first {name} of {year} is on <strong>{when}</strong> ({details}). All {count} dates
    #     for {year} are listed below.
    # keep: {count} {details} {name} {when} {year}
    "ans.first": "",
    # EN: All {count} {name} dates for {year} are listed below; the last was on
    #     <strong>{when}</strong>.
    # keep: {count} {name} {when} {year}
    "ans.past": "",
    # EN: Dates for {year}: {link}.
    # keep: {link} {year}
    "ans.more": "",
    # EN: {name} {year}: all dates
    # keep: {name} {year}
    "table.h2": "",
    # EN: Date
    "th.date": "",
    # EN: Hindu month
    "th.month": "",
    # EN: Tithi
    "th.tithi": "",
    # EN: Adhik {month}
    # keep: {month}
    "adhika": "",
    # EN: Also:
    "also": "",
    # EN: <p class="note"><small>Months are amanta (a month ends on Amavasya, as in South and West
    #     India). North Indian purnimanta calendars name the dark fortnight one month
    #     later.</small></p>
    "months.note": "",
    # EN: Som Pradosh
    "variant.pradosh.0": "",
    # EN: Bhauma Pradosh
    "variant.pradosh.1": "",
    # EN: Shani Pradosh
    "variant.pradosh.5": "",
    # EN: Angarki Chaturthi
    "variant.sankashti.1": "",
    # EN: Somvati Amavasya
    "variant.amavasya.0": "",
    # EN: Shani Amavasya
    "variant.amavasya.5": "",
    # EN: What {name} is and how it is observed
    # keep: {name}
    "about.h2": "",
    # EN: Panchang for your city
    "city.h2": "",
    # EN: Related dates and calendars
    "related.h2": "",
    # EN: {name} {year}
    # keep: {name} {year}
    "crumb.page": "",
    # EN: <p>Purnima is the full-moon tithi, the last (15th) tithi of the bright fortnight (Shukla
    #     paksha), when the Moon stands opposite the Sun and shines full. Devotees keep a fast,
    #     bathe at dawn (in a river or tirtha where they can), worship Lord Vishnu - Satyanarayan
    #     Katha is the usual Purnima puja - and offer arghya to the Moon in the evening. Charity
    #     (daan) of food, clothes or money on this day is said to bring multiplied merit.</p><p>Some
    #     Purnimas are festivals in their own right: Guru Purnima, Sharad Purnima, Kartik Purnima
    #     and Buddha Purnima, and Holika Dahan is kept on the Purnima of Phalguna.</p>
    "about.purnima": "",
    # EN: <p>Amavasya is the new-moon tithi, the 30th and last tithi of the dark fortnight (Krishna
    #     paksha), when the Moon is in conjunction with the Sun and cannot be seen. It is the day of
    #     the ancestors (pitru): families offer tarpan and shraddha, feed Brahmins and the poor,
    #     give in charity and bathe in holy water. Many people fast and avoid starting anything
    #     new.</p><p>An Amavasya on a Monday is called Somvati Amavasya and one on a Saturday Shani
    #     Amavasya, both given extra weight. The great Amavasyas are Mauni Amavasya, Sarva Pitru
    #     Amavasya (the end of Pitru Paksha) and the Amavasya of Diwali.</p>
    "about.amavasya": "",
    # EN: <p>Pradosh Vrat is the fast of Lord Shiva kept on Trayodashi, the 13th tithi, of both
    #     fortnights - so twice a month. Pradosh kaal is the twilight window just after sunset, when
    #     Shiva is believed to be most pleased. Devotees fast through the day, bathe, and do Shiva
    #     puja in the Pradosh window: abhishek with water, milk and bilva (bel) leaves, a lamp and
    #     the Pradosh stotra or Shiva Chalisa. The fast is broken after the puja.</p><p>A Pradosh on
    #     Monday is Som Pradosh, on Tuesday Bhauma Pradosh and on Saturday Shani Pradosh; the
    #     Saturday one is considered especially powerful.</p>
    "about.pradosh": "",
    # EN: <p>Sankashti Chaturthi (Sankat Hara Chaturthi) is the monthly fast of Lord Ganesha on
    #     Chaturthi, the 4th tithi, of the dark fortnight (Krishna paksha); "sankashti" means
    #     deliverance from trouble. Devotees fast through the day, worship Ganesha in the evening
    #     and break the fast only after seeing the Moon and offering it arghya, which is why
    #     moonrise is the key time on this page.</p><p>A Sankashti on a Tuesday is Angarki Sankashti
    #     Chaturthi, believed to be especially fruitful. The Sankashti of Magha (purnimanta) is kept
    #     in North India as Sakat Chauth.</p>
    "about.sankashti": "",
    # EN: <p>Masik Shivratri (monthly Shivratri) is the night of Lord Shiva kept on Chaturdashi, the
    #     14th tithi, of the dark fortnight (Krishna paksha) every month. Devotees fast and keep
    #     vigil through the night, bathing the Shiva linga with water, milk, honey and bilva leaves
    #     and chanting "Om Namah Shivaya". The best time for the puja is Nishita kaal, the midnight
    #     window.</p><p>Maha Shivratri, which falls on Krishna Chaturdashi of Phalguna (Magha in the
    #     amanta calendar), is the greatest of the twelve.</p>
    "about.masik_shivratri": "",
    # EN: <p>Kalashtami (Kala Ashtami) is the monthly day of Lord Kala Bhairava, the fierce form of
    #     Shiva who guards time, kept on Ashtami, the 8th tithi, of the dark fortnight (Krishna
    #     paksha). Devotees fast, worship Bhairava at night with a mustard-oil lamp and offerings
    #     such as black sesame, and feed dogs, which are associated with him.</p><p>The Kalashtami
    #     of Margashirsha in the purnimanta calendar (Kartika in the amanta calendar) is
    #     Kalabhairava Jayanti, his appearance day and the most important of the year.</p>
    "about.kalashtami": "",
    # EN: Purnima can begin one evening and end the next afternoon, so the day the tithi starts and
    #     the day of the vrat can differ. The rule settles it: the vrat goes to the day on which the
    #     tithi covers Madhyahna (the middle fifth of the daytime); if it covers Madhyahna on both
    #     days, the earlier day is taken. Some traditions use the sunrise tithi for the holy bath
    #     and charity instead; the table gives the start and end of the tithi so you can check.
    "note.purnima": "",
    # EN: Amavasya is a daytime observance (shraddha and tarpan are done in the day), so the date is
    #     the day on which the Amavasya tithi is running at sunrise. The tithi often starts the
    #     evening before, so the times in the table can begin on the previous date. Festival
    #     Amavasyas follow their own rules - Diwali is fixed by Pradosh, Sarva Pitru Amavasya by
    #     Aparahna - and can fall a day away from the date here.
    "note.amavasya": "",
    # EN: The date is decided in the evening, not at sunrise: the vrat goes to the day on which
    #     Trayodashi is running in Pradosh kaal after sunset, so a Trayodashi that starts at noon
    #     and ends the next afternoon is kept on the first day. If the tithi touches Pradosh kaal on
    #     two evenings, the earlier evening is taken. The puja window in the table starts at sunset
    #     in New Delhi, so it moves through the year and from city to city.
    "note.pradosh": "",
    # EN: Sankashti is decided by the Moon, not the Sun: the vrat goes to the evening on which
    #     Chaturthi is running at moonrise, since that is when the fast is broken. The date can
    #     therefore differ from the Chaturthi date of a Panchang that goes by sunrise. Moonrise is
    #     roughly 50 minutes later each day and differs by several minutes between cities, so check
    #     it for your own city.
    "note.sankashti": "",
    # EN: This is a midnight observance, so the date is the day on which Chaturdashi is running at
    #     Nishita kaal (the 8th of the 15 muhurtas of the night, around midnight). Nishita can fall
    #     just after 12 o'clock, in which case the puja is done in the early hours of the next date
    #     and the time shown carries that date. If the tithi touches Nishita on two nights, the
    #     earlier night is taken.
    "note.masik_shivratri": "",
    # EN: Kalashtami is a night worship, so the date is the day on which Ashtami is running in
    #     Pradosh kaal (the evening window after sunset); the tithi may begin the previous morning
    #     or end during the night, so check its start and end times in the table. If it touches
    #     Pradosh kaal on two evenings, the earlier evening is taken. Some traditions go by the
    #     midnight tithi instead, which can occasionally differ by a day.
    "note.kalashtami": "",
    # EN: What are the {name} dates in {year}?
    # keep: {name} {year}
    "faq.all_q": "",
    # EN: There are {count} {name} dates in {year} (New Delhi): {dates}.
    # keep: {count} {dates} {name} {year}
    "faq.all_a": "",
    # EN: When is the next {name}?
    # keep: {name}
    "faq.next_q": "",
    # EN: When is the first {name} of {year}?
    # keep: {name} {year}
    "faq.first_q": "",
    # EN: {name} is on {when} ({details}).
    # keep: {details} {name} {when}
    "faq.on_a": "",
    # EN: What is the {label} on {name} {short}?
    # keep: {label} {name} {short}
    "faq.key_q": "",
    # EN: At what time does the {name} tithi start and end on {short}?
    # keep: {name} {short}
    "faq.tithi_q": "",
    # EN: How is the {name} date decided?
    # keep: {name}
    "faq.why_q": "",
    # EN: The date follows the rule: {rule}. In {year} this gives {count} dates (New Delhi).
    # keep: {count} {rule} {year}
    "faq.why_a": "",
    # EN: Monthly vrat dates
    "hub.h2": "",
}

# ----------------------------------------------------------------------------
# hub       /sitemap
# ----------------------------------------------------------------------------

# app/hub_text.py LABELS["pa"] — section names of the crawlable /sitemap page and the footer link block  [19]
HUB_LABELS = {
    # EN: Site map
    "sitemap": "ਸਾਈਟ ਮੈਪ",
    # EN: Panchang
    "panchang": "ਪੰਚਾਂਗ",
    # EN: Rashifal (daily horoscope)
    "rashifal": "ਰਾਸ਼ੀਫਲ (ਰੋਜ਼ਾਨਾ ਫਲਾਦੇਸ਼)",
    # EN: Vrat &amp; festivals
    "vrat": "ਵਰਤ ਅਤੇ ਤਿਉਹਾਰ",
    # EN: Shubh muhurat
    "muhurat": "ਸ਼ੁਭ ਮਹੂਰਤ",
    # EN: Nakshatra
    "nakshatra": "ਨਕਸ਼ਤਰ",
    # EN: Rashi (zodiac signs)
    "rashi": "ਰਾਸ਼ੀ (ਰਾਸ਼ੀ ਚਿੰਨ੍ਹ)",
    # EN: Kathas
    "katha": "ਕਥਾਵਾਂ",
    # EN: Free tools
    "tools": "ਮੁਫ਼ਤ ਟੂਲ",
    # EN: Kundali Milan
    "milan": "ਕੁੰਡਲੀ ਮਿਲਾਨ",
    # EN: Free Kundali
    "kundali": "ਮੁਫ਼ਤ ਕੁੰਡਲੀ",
    # EN: Rahu Kaal
    "rahu": "ਰਾਹੂ ਕਾਲ",
    # EN: Choghadiya
    "choghadiya": "ਚੌਘੜੀਆ",
    # EN: Naam se Kundali Milan
    "naam": "ਨਾਂ ਤੋਂ ਕੁੰਡਲੀ ਮਿਲਾਨ",
    # EN: Today's Panchang by city
    "cities": "ਸ਼ਹਿਰ ਮੁਤਾਬਕ ਅੱਜ ਦਾ ਪੰਚਾਂਗ",
    # EN: Rashifal by sign
    "signs": "ਰਾਸ਼ੀ ਮੁਤਾਬਕ ਰਾਸ਼ੀਫਲ",
    # EN: Vrat and festival calendars
    "years": "ਵਰਤ ਅਤੇ ਤਿਉਹਾਰਾਂ ਦੇ ਕੈਲੰਡਰ",
    # EN: Ekadashi
    "ekadashi": "ਇਕਾਦਸ਼ੀ",
    # EN: Every section of Divine Astro in one place: daily Panchang for Indian cities, Rashifal,
    #     vrat and festival dates, shubh muhurat, nakshatra and rashi guides, kathas and the free
    #     tools.
    "intro": "Divine Astro ਦਾ ਹਰ ਹਿੱਸਾ ਇੱਕੋ ਥਾਂ: ਭਾਰਤੀ ਸ਼ਹਿਰਾਂ ਦਾ ਰੋਜ਼ਾਨਾ ਪੰਚਾਂਗ, ਰਾਸ਼ੀਫਲ, ਵਰਤ ਅਤੇ ਤਿਉਹਾਰਾਂ ਦੀਆਂ ਤਾਰੀਖ਼ਾਂ, ਸ਼ੁਭ ਮਹੂਰਤ, ਨਕਸ਼ਤਰ ਅਤੇ ਰਾਸ਼ੀ ਗਾਈਡਾਂ, ਕਥਾਵਾਂ ਅਤੇ ਮੁਫ਼ਤ ਟੂਲ।",
}

# ----------------------------------------------------------------------------
# app       AI-narration vocabulary here; names_<code>.py and static/i18n/<code>.json beside it
# ----------------------------------------------------------------------------

# app/astro_terms.py TERMS["pa"] — house / dasha / sign vocabulary for the AI narration and the chart labels  [16]
ASTRO_TERMS = {
    # EN: house
    "house": "ਭਾਵ",
    # EN: sign
    "sign": "ਰਾਸ਼ੀ",
    # EN: lord
    "lord": "ਸੁਆਮੀ",
    # EN: dasha
    "dasha": "ਦਸ਼ਾ",
    # EN: mahadasha
    "mahadasha": "ਮਹਾਦਸ਼ਾ",
    # EN: antardasha
    "antardasha": "ਅੰਤਰਦਸ਼ਾ",
    # EN: ascendant
    "ascendant": "ਲਗਨ",
    # EN: transit
    "transit": "ਗੋਚਰ",
    # EN: retrograde
    "retrograde": "ਵੱਕਰੀ",
    # EN: exalted
    "exalted": "ਉੱਚ ਦਾ",
    # EN: debilitated
    "debilitated": "ਨੀਚ ਦਾ",
    # EN: own sign
    "own sign": "ਆਪਣੀ ਰਾਸ਼ੀ",
    # EN: Sade Sati
    "Sade Sati": "ਸਾੜ੍ਹਸਾਤੀ",
    # EN: Navamsa
    "Navamsa": "ਨਵਾਂਸ਼",
    # EN: yoga
    "yoga": "ਯੋਗ",
    # EN: remedy
    "remedy": "ਉਪਾਅ",
}

# app/astro_terms.py MONTH_VARIANTS["pa"] — other spellings of a Gregorian month the AI may write (month number -> spellings)
# (optional: may stay empty)
ASTRO_MONTHS = {}   # {month number: (other spellings,)}, e.g. {2: ("...",)}
