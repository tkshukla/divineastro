"""Punjabi (ਪੰਜਾਬੀ, Gurmukhi) names for the panchang, festivals and matching (DIVASTRO-143).

Same shape as names_kn.py / names_bn.py: one table per name, suffix _PA, keyed by the
ENGLISH name the engines emit; names_i18n.names_for("pa") exposes them. A key left "" (or a
table left out) falls back to the English name, so the site works while this fills up; `python -m
app.lang_data check pa` lists what is left. Use the names Punjabi panchang and jyotish
tradition uses, in this language's script, not a transliteration of the English. Document
choices a native reviewer should confirm in this docstring (see names_bn.py).

Tables: TITHI(16) NAKSHATRAS(27) VARA(7) YOGA(27) KARANA(11) PAKSHA(2) MASA(12 lunar months)
SOLAR_MASA(optional: only if the calendar is solar) RASHI(12) GRAHA(9) CHOGHADIYA(7)
CHOGHADIYA_QUALITY(3) TIMINGS FESTIVAL_TIMINGS FESTIVALS EKADASHI REGIONAL_NOTE(optional)
KOOTA GANA NADI VARNA VASHYA YONI TARA WEEKDAY(7, short) MONTHS(12) CLOCK(4) LIMBS(10) and
the two notes NOTE_POLAR / NOTE_WEDNESDAY.

Regional choices (for a native reviewer):
  * Tithi names follow Punjabi almanac speech: ਏਕਮ, ਦੂਜ, ਤੀਜ, ਚੌਥ, ... ਚੌਦਸ, ਪੂਰਨਮਾਸ਼ੀ, ਮੱਸਿਆ
    (Sanskrit forms from Panchami to Dashami, ਇਕਾਦਸ਼ੀ, ਦੁਆਦਸ਼ੀ, ਤ੍ਰਯੋਦਸ਼ੀ).
  * Hindu lunar months (MASA) use the Punjabi desi names: ਚੇਤ ਵਿਸਾਖ ਜੇਠ ਹਾੜ ਸਾਵਣ ਭਾਦੋਂ ਅੱਸੂ ਕੱਤਕ
    ਮੱਘਰ ਪੋਹ ਮਾਘ ਫੱਗਣ. The Punjabi (Nanakshahi / Bikrami) months are solar and begin on the
    sankranti; the engine's months are lunar, so the same names are used for the lunar month.
    SOLAR_MASA is not filled. Gurpurab / Nanakshahi dates are not in the engine and are not added.
  * Rashi: ਮੇਖ ਬ੍ਰਿਖ ਮਿਥੁਨ ਕਰਕ ਸਿੰਘ ਕੰਨਿਆ ਤੁਲਾ ਬ੍ਰਿਸ਼ਚਕ ਧਨੁ ਮਕਰ ਕੁੰਭ ਮੀਨ. Jupiter is ਬ੍ਰਿਹਸਪਤੀ
    (ਗੁਰੂ is avoided: in Punjabi it means the Sikh Gurus), Saturn ਸ਼ਨੀ, weekday Saturday ਸ਼ਨਿੱਚਰਵਾਰ.
  * ਰਾਹੂ ਕਾਲ, ਯਮਗੰਡ, ਗੁਲਿਕ ਕਾਲ, ਅਭਿਜੀਤ ਮਹੂਰਤ (Punjabi spelling ਮਹੂਰਤ, not ਮੁਹੂਰਤ).
  * Mauni Amavasya ਮੌਨੀ ਮੱਸਿਆ; Karwa Chauth ਕਰਵਾ ਚੌਥ; Diwali ਦੀਵਾਲੀ; Dussehra ਦੁਸਹਿਰਾ;
    Makar Sankranti is written ਮਕਰ ਸੰਕ੍ਰਾਂਤੀ (ਮਾਘੀ) since Maghi falls on the same day in Punjab.
  * Hariyali Teej is ਹਰਿਆਲੀ ਤੀਜ (ਤੀਆਂ), the Punjabi Sawan festival of the same date.
  * Gana in matching: ਦੇਵ / ਮਨੁੱਖ / ਰਾਖਸ਼; Nadi ਆਦਿ / ਮੱਧ / ਅੰਤ; Varna ਖੱਤਰੀ for Kshatriya.
  * The sentence-ending mark is the danda '।'; digits are ASCII.
"""

from __future__ import annotations


TITHI_PA = {
    "Pratipada": "ਏਕਮ",
    "Dwitiya": "ਦੂਜ",
    "Tritiya": "ਤੀਜ",
    "Chaturthi": "ਚੌਥ",
    "Panchami": "ਪੰਚਮੀ",
    "Shashthi": "ਸ਼ਸ਼ਠੀ",
    "Saptami": "ਸਪਤਮੀ",
    "Ashtami": "ਅਸ਼ਟਮੀ",
    "Navami": "ਨੌਮੀ",
    "Dashami": "ਦਸਮੀ",
    "Ekadashi": "ਇਕਾਦਸ਼ੀ",
    "Dwadashi": "ਦੁਆਦਸ਼ੀ",
    "Trayodashi": "ਤ੍ਰਯੋਦਸ਼ੀ",
    "Chaturdashi": "ਚੌਦਸ",
    "Purnima": "ਪੂਰਨਮਾਸ਼ੀ",
    "Amavasya": "ਮੱਸਿਆ",
}

NAKSHATRAS_PA = {
    "Ashwini": "ਅਸ਼ਵਿਨੀ",
    "Bharani": "ਭਰਨੀ",
    "Krittika": "ਕ੍ਰਿਤਿਕਾ",
    "Rohini": "ਰੋਹਿਣੀ",
    "Mrigashira": "ਮ੍ਰਿਗਸ਼ਿਰਾ",
    "Ardra": "ਆਰਦਰਾ",
    "Punarvasu": "ਪੁਨਰਵਸੂ",
    "Pushya": "ਪੁਸ਼ਯ",
    "Ashlesha": "ਅਸ਼ਲੇਸ਼ਾ",
    "Magha": "ਮਘਾ",
    "Purva Phalguni": "ਪੂਰਵਾ ਫਾਲਗੁਨੀ",
    "Uttara Phalguni": "ਉੱਤਰਾ ਫਾਲਗੁਨੀ",
    "Hasta": "ਹਸਤ",
    "Chitra": "ਚਿੱਤਰਾ",
    "Swati": "ਸਵਾਤੀ",
    "Vishakha": "ਵਿਸ਼ਾਖਾ",
    "Anuradha": "ਅਨੁਰਾਧਾ",
    "Jyeshtha": "ਜੇਸ਼ਠਾ",
    "Mula": "ਮੂਲ",
    "Purva Ashadha": "ਪੂਰਵਾ ਆਸ਼ਾੜ੍ਹਾ",
    "Uttara Ashadha": "ਉੱਤਰਾ ਆਸ਼ਾੜ੍ਹਾ",
    "Shravana": "ਸ਼ਰਵਣ",
    "Dhanishta": "ਧਨਿਸ਼ਠਾ",
    "Shatabhisha": "ਸ਼ਤਭਿਸ਼ਾ",
    "Purva Bhadrapada": "ਪੂਰਵਾ ਭਾਦਰਪਦ",
    "Uttara Bhadrapada": "ਉੱਤਰਾ ਭਾਦਰਪਦ",
    "Revati": "ਰੇਵਤੀ",
}

VARA_PA = {
    "Sunday": "ਐਤਵਾਰ",
    "Monday": "ਸੋਮਵਾਰ",
    "Tuesday": "ਮੰਗਲਵਾਰ",
    "Wednesday": "ਬੁੱਧਵਾਰ",
    "Thursday": "ਵੀਰਵਾਰ",
    "Friday": "ਸ਼ੁੱਕਰਵਾਰ",
    "Saturday": "ਸ਼ਨਿੱਚਰਵਾਰ",
}

YOGA_PA = {
    "Vishkambha": "ਵਿਸ਼ਕੰਭ",
    "Priti": "ਪ੍ਰੀਤੀ",
    "Ayushman": "ਆਯੁਸ਼ਮਾਨ",
    "Saubhagya": "ਸੌਭਾਗਯ",
    "Shobhana": "ਸ਼ੋਭਨ",
    "Atiganda": "ਅਤਿਗੰਡ",
    "Sukarma": "ਸੁਕਰਮਾ",
    "Dhriti": "ਧ੍ਰਿਤੀ",
    "Shula": "ਸ਼ੂਲ",
    "Ganda": "ਗੰਡ",
    "Vriddhi": "ਵ੍ਰਿੱਧੀ",
    "Dhruva": "ਧ੍ਰੁਵ",
    "Vyaghata": "ਵਿਆਘਾਤ",
    "Harshana": "ਹਰਸ਼ਣ",
    "Vajra": "ਵਜ੍ਰ",
    "Siddhi": "ਸਿੱਧੀ",
    "Vyatipata": "ਵਿਅਤੀਪਾਤ",
    "Variyana": "ਵਰੀਯਾਨ",
    "Parigha": "ਪਰਿਘ",
    "Shiva": "ਸ਼ਿਵ",
    "Siddha": "ਸਿੱਧ",
    "Sadhya": "ਸਾਧਯ",
    "Shubha": "ਸ਼ੁਭ",
    "Shukla": "ਸ਼ੁਕਲ",
    "Brahma": "ਬ੍ਰਹਮਾ",
    "Indra": "ਇੰਦਰ",
    "Vaidhriti": "ਵੈਧ੍ਰਿਤੀ",
}

KARANA_PA = {
    "Bava": "ਬਵ",
    "Balava": "ਬਾਲਵ",
    "Kaulava": "ਕੌਲਵ",
    "Taitila": "ਤੈਤਿਲ",
    "Gara": "ਗਰ",
    "Vanija": "ਵਣਿਜ",
    "Vishti": "ਵਿਸ਼ਟੀ (ਭਦਰਾ)",
    "Shakuni": "ਸ਼ਕੁਨੀ",
    "Chatushpada": "ਚਤੁਸ਼ਪਦ",
    "Naga": "ਨਾਗ",
    "Kimstughna": "ਕਿੰਸਤੁਘਨ",
}

PAKSHA_PA = {
    "Shukla": "ਸ਼ੁਕਲ",
    "Krishna": "ਕ੍ਰਿਸ਼ਨ",
}

MASA_PA = {
    "Chaitra": "ਚੇਤ",
    "Vaishakha": "ਵਿਸਾਖ",
    "Jyeshtha": "ਜੇਠ",
    "Ashadha": "ਹਾੜ",
    "Shravana": "ਸਾਵਣ",
    "Bhadrapada": "ਭਾਦੋਂ",
    "Ashwin": "ਅੱਸੂ",
    "Kartika": "ਕੱਤਕ",
    "Margashirsha": "ਮੱਘਰ",
    "Pausha": "ਪੋਹ",
    "Magha": "ਮਾਘ",
    "Phalguna": "ਫੱਗਣ",
}

# lunar months are MASA; fill this only if the calendar is solar (keys "Aries".."Pisces")
SOLAR_MASA_PA = {}

RASHI_PA = {
    "Aries": "ਮੇਖ",
    "Taurus": "ਬ੍ਰਿਖ",
    "Gemini": "ਮਿਥੁਨ",
    "Cancer": "ਕਰਕ",
    "Leo": "ਸਿੰਘ",
    "Virgo": "ਕੰਨਿਆ",
    "Libra": "ਤੁਲਾ",
    "Scorpio": "ਬ੍ਰਿਸ਼ਚਕ",
    "Sagittarius": "ਧਨੁ",
    "Capricorn": "ਮਕਰ",
    "Aquarius": "ਕੁੰਭ",
    "Pisces": "ਮੀਨ",
}

GRAHA_PA = {
    "Sun": "ਸੂਰਜ",
    "Moon": "ਚੰਦਰਮਾ",
    "Mars": "ਮੰਗਲ",
    "Mercury": "ਬੁੱਧ",
    "Jupiter": "ਬ੍ਰਿਹਸਪਤੀ",
    "Venus": "ਸ਼ੁੱਕਰ",
    "Saturn": "ਸ਼ਨੀ",
    "Rahu": "ਰਾਹੂ",
    "Ketu": "ਕੇਤੂ",
}

CHOGHADIYA_PA = {
    "Amrit": "ਅੰਮ੍ਰਿਤ",
    "Shubh": "ਸ਼ੁਭ",
    "Labh": "ਲਾਭ",
    "Char": "ਚਰ",
    "Rog": "ਰੋਗ",
    "Kaal": "ਕਾਲ",
    "Udveg": "ਉਦਵੇਗ",
}

CHOGHADIYA_QUALITY_PA = {
    "auspicious": "ਸ਼ੁਭ",   # Auspicious
    "neutral": "ਮੱਧਮ",   # Neutral
    "inauspicious": "ਅਸ਼ੁਭ",   # Inauspicious
}

TIMINGS_PA = {
    "rahu_kaal": "ਰਾਹੂ ਕਾਲ",   # Rahu Kaal
    "yamaganda": "ਯਮਗੰਡ",   # Yamaganda
    "gulika": "ਗੁਲਿਕ ਕਾਲ",   # Gulika Kaal
    "abhijit": "ਅਭਿਜੀਤ ਮਹੂਰਤ",   # Abhijit Muhurta
    "brahma_muhurta": "ਬ੍ਰਹਮ ਮਹੂਰਤ",   # Brahma Muhurta
    "pradosh": "ਪ੍ਰਦੋਸ਼ ਕਾਲ",   # Pradosh Kaal
    "nishita": "ਨਿਸ਼ੀਥ ਕਾਲ",   # Nishita Kaal
    "sunrise": "ਸੂਰਜ ਚੜ੍ਹਨ ਦਾ ਸਮਾਂ",   # Sunrise
    "sunset": "ਸੂਰਜ ਛਿਪਣ ਦਾ ਸਮਾਂ",   # Sunset
    "moonrise": "ਚੰਦਰਮਾ ਚੜ੍ਹਨ ਦਾ ਸਮਾਂ",   # Moonrise
    "moonset": "ਚੰਦਰਮਾ ਛਿਪਣ ਦਾ ਸਮਾਂ",   # Moonset
    "parana": "ਪਾਰਣਾ ਦਾ ਸਮਾਂ",   # Parana time
    "durmuhurtam": "ਦੁਰਮਹੂਰਤ",   # Durmuhurtam
    "varjyam": "ਵਰਜਯਮ",   # Varjyam
    "good_time": "ਸ਼ੁਭ ਸਮਾਂ",   # Good time
}

FESTIVAL_TIMINGS_PA = {
    "parana": "ਪਾਰਣਾ (ਵਰਤ ਖੋਲ੍ਹਣਾ)",   # Parana (breaking the fast)
    "pradosh": "ਪ੍ਰਦੋਸ਼ ਪੂਜਾ",   # Pradosh puja
    "pradosh_kaal": "ਪ੍ਰਦੋਸ਼ ਕਾਲ",   # Pradosh kaal
    "moonrise": "ਚੰਦਰਮਾ ਚੜ੍ਹਨ ਦਾ ਸਮਾਂ",   # Moonrise
    "madhyahna": "ਮੱਧਾਹਨ ਪੂਜਾ ਮਹੂਰਤ",   # Madhyahna puja muhurat
    "nishita": "ਨਿਸ਼ੀਥ ਕਾਲ ਪੂਜਾ",   # Nishita kaal puja
    "aparahna": "ਅਪਰਾਹਨ ਪੂਜਾ",   # Aparahna puja
    "vijay": "ਵਿਜੈ ਮਹੂਰਤ",   # Vijay muhurat
    "ghatasthapana": "ਘਟ ਸਥਾਪਨਾ ਮਹੂਰਤ",   # Ghatasthapana muhurat
    "ghatasthapana_abhijit": "ਘਟ ਸਥਾਪਨਾ (ਅਭਿਜੀਤ)",   # Ghatasthapana (Abhijit)
    "lakshmi_puja": "ਲਕਸ਼ਮੀ ਪੂਜਾ ਮਹੂਰਤ",   # Lakshmi puja muhurat
    "dhanteras_puja": "ਧਨਤੇਰਸ ਪੂਜਾ ਮਹੂਰਤ",   # Dhanteras puja muhurat
    "vrishabha": "ਬ੍ਰਿਖ ਕਾਲ (ਸਥਿਰ ਲਗਨ)",   # Vrishabha kaal (sthir lagna)
    "punya_kaal": "ਪੁੰਨ ਕਾਲ",   # Punya kaal
    "maha_punya_kaal": "ਮਹਾਂ ਪੁੰਨ ਕਾਲ",   # Maha punya kaal
    "sankranti": "ਸੰਕ੍ਰਾਂਤੀ ਦਾ ਪਲ",   # Sankranti moment
    "holika_dahan": "ਹੋਲਿਕਾ ਦਹਨ ਮਹੂਰਤ",   # Holika Dahan muhurat
    "holika_after_bhadra": "ਭਦਰਾ ਖ਼ਤਮ ਹੋਣ ਮਗਰੋਂ ਹੋਲਿਕਾ ਦਹਨ",   # Holika Dahan after Bhadra ends
    "rakhi": "ਰੱਖੜੀ ਬੰਨ੍ਹਣ ਦਾ ਮਹੂਰਤ",   # Rakhi muhurat
    "karwa_puja": "ਪੂਜਾ ਮਹੂਰਤ",   # Puja muhurat
    "puja": "ਪੂਜਾ ਮਹੂਰਤ",   # Puja muhurat
    "sandhya_arghya": "ਸੰਧਿਆ ਅਰਘ (ਸੂਰਜ ਛਿਪਣ ਵੇਲੇ)",   # Sandhya arghya (sunset)
    "usha_arghya": "ਊਸ਼ਾ ਅਰਘ (ਅਗਲੇ ਦਿਨ ਸੂਰਜ ਚੜ੍ਹਨ ਵੇਲੇ)",   # Usha arghya (sunrise, next day)
    "pratah": "ਸਵੇਰ ਦਾ ਮਹੂਰਤ",   # Pratahkala muhurat
    "sayahna": "ਸ਼ਾਮ ਦਾ ਮਹੂਰਤ",   # Sayahnakala muhurat
    "tithi": "ਤਿਥੀ",   # Tithi
    "dwadashi_end": "ਦੁਆਦਸ਼ੀ ਦਾ ਅੰਤ",   # Dwadashi ends
    "hari_vasara_end": "ਹਰਿ ਵਾਸਰ ਦਾ ਅੰਤ",   # Hari Vasara ends
    "kutup": "ਕੁਤੁਪ ਮਹੂਰਤ",   # Kutup muhurat
    "rohina": "ਰੋਹਿਣ ਮਹੂਰਤ",   # Rohina muhurat
    "aparahna_kaal": "ਅਪਰਾਹਨ ਕਾਲ",   # Aparahna kaal
    "abhyang": "ਅਭਯੰਗ ਇਸ਼ਨਾਨ (ਚੰਦਰਮਾ ਚੜ੍ਹਨ ਤੋਂ ਸੂਰਜ ਚੜ੍ਹਨ ਤੱਕ)",   # Abhyang snan (moonrise to sunrise)
}

FESTIVALS_PA = {
    "pradosh": "ਪ੍ਰਦੋਸ਼ ਵਰਤ",   # Pradosh Vrat
    "sankashti": "ਸੰਕਸ਼ਟੀ ਚੌਥ",   # Sankashti Chaturthi
    "vinayaka": "ਵਿਨਾਇਕ ਚੌਥ",   # Vinayaka Chaturthi
    "purnima": "ਪੂਰਨਮਾਸ਼ੀ ਦਾ ਵਰਤ",   # Purnima Vrat
    "amavasya": "ਮੱਸਿਆ",   # Amavasya
    "masik_shivratri": "ਮਾਸਿਕ ਸ਼ਿਵਰਾਤਰੀ",   # Masik Shivratri
    "durgashtami": "ਮਾਸਿਕ ਦੁਰਗਾ ਅਸ਼ਟਮੀ",   # Masik Durgashtami
    "kalashtami": "ਕਾਲ ਅਸ਼ਟਮੀ",   # Kalashtami
    "skanda_shashthi": "ਸਕੰਦ ਸ਼ਸ਼ਠੀ",   # Skanda Shashthi
    "maha_shivratri": "ਮਹਾਂ ਸ਼ਿਵਰਾਤਰੀ",   # Maha Shivratri
    "holika_dahan": "ਹੋਲਿਕਾ ਦਹਨ",   # Holika Dahan
    "ram_navami": "ਰਾਮ ਨੌਮੀ",   # Ram Navami
    "hanuman_jayanti": "ਹਨੂੰਮਾਨ ਜਯੰਤੀ",   # Hanuman Jayanti
    "akshaya_tritiya": "ਅਕਸ਼ੈ ਤ੍ਰਿਤੀਆ",   # Akshaya Tritiya
    "raksha_bandhan": "ਰੱਖੜੀ (ਰਕਸ਼ਾ ਬੰਧਨ)",   # Raksha Bandhan
    "janmashtami": "ਕ੍ਰਿਸ਼ਨ ਜਨਮ ਅਸ਼ਟਮੀ",   # Krishna Janmashtami
    "ganesh_chaturthi": "ਗਣੇਸ਼ ਚਤੁਰਥੀ",   # Ganesh Chaturthi
    "chaitra_navratri": "ਚੇਤ ਦੇ ਨਰਾਤੇ ਸ਼ੁਰੂ",   # Chaitra Navratri begins
    "navratri": "ਸ਼ਾਰਦੀਆ ਨਰਾਤੇ ਸ਼ੁਰੂ",   # Sharad Navratri begins
    "dussehra": "ਦੁਸਹਿਰਾ (ਵਿਜੈ ਦਸ਼ਮੀ)",   # Dussehra (Vijayadashami)
    "karwa_chauth": "ਕਰਵਾ ਚੌਥ",   # Karwa Chauth
    "ahoi_ashtami": "ਅਹੋਈ ਅਸ਼ਟਮੀ",   # Ahoi Ashtami
    "dhanteras": "ਧਨਤੇਰਸ",   # Dhanteras
    "diwali": "ਦੀਵਾਲੀ (ਲਕਸ਼ਮੀ ਪੂਜਾ)",   # Diwali (Lakshmi Puja)
    "govardhan": "ਗੋਵਰਧਨ ਪੂਜਾ",   # Govardhan Puja
    "bhai_dooj": "ਭਾਈ ਦੂਜ",   # Bhai Dooj
    "chhath": "ਛਠ ਪੂਜਾ",   # Chhath Puja
    "vasant_panchami": "ਬਸੰਤ ਪੰਚਮੀ",   # Vasant Panchami
    "guru_purnima": "ਗੁਰੂ ਪੂਰਨਿਮਾ",   # Guru Purnima
    "sharad_purnima": "ਸ਼ਰਦ ਪੂਰਨਿਮਾ",   # Sharad Purnima
    "sakat_chauth": "ਸਕਟ ਚੌਥ",   # Sakat Chauth
    "mauni_amavasya": "ਮੌਨੀ ਮੱਸਿਆ",   # Mauni Amavasya
    "sheetala_ashtami": "ਸ਼ੀਤਲਾ ਅਸ਼ਟਮੀ (ਬਸੋੜਾ)",   # Sheetala Ashtami (Basoda)
    "gudi_padwa": "ਗੁੜੀ ਪੜਵਾ / ਉਗਾਦੀ",   # Gudi Padwa / Ugadi
    "gangaur": "ਗਣਗੌਰ",   # Gangaur
    "vat_savitri": "ਵਟ ਸਾਵਿਤਰੀ ਵਰਤ",   # Vat Savitri Vrat
    "ganga_dussehra": "ਗੰਗਾ ਦੁਸਹਿਰਾ",   # Ganga Dussehra
    "vat_purnima": "ਵਟ ਪੂਰਨਿਮਾ ਵਰਤ",   # Vat Purnima Vrat
    "hariyali_teej": "ਹਰਿਆਲੀ ਤੀਜ (ਤੀਆਂ)",   # Hariyali Teej
    "nag_panchami": "ਨਾਗ ਪੰਚਮੀ",   # Nag Panchami
    "kajari_teej": "ਕਜਰੀ ਤੀਜ",   # Kajari Teej
    "hal_shashthi": "ਹਲ ਸ਼ਸ਼ਠੀ (ਲਲਹੀ ਛਠ)",   # Hal Shashthi (Lalahi Chhath)
    "hartalika_teej": "ਹਰਤਾਲਿਕਾ ਤੀਜ",   # Hartalika Teej
    "rishi_panchami": "ਰਿਸ਼ੀ ਪੰਚਮੀ",   # Rishi Panchami
    "anant_chaturdashi": "ਅਨੰਤ ਚੌਦਸ",   # Anant Chaturdashi
    "pitru_paksha": "ਪਿਤਰ ਪੱਖ ਸ਼ੁਰੂ (ਪ੍ਰਤਿਪਦਾ ਸ਼ਰਾਧ)",   # Pitru Paksha begins (Pratipada Shraddha)
    "jivitputrika": "ਜੀਵਿਤਪੁੱਤ੍ਰਿਕਾ ਵਰਤ (ਜਿਤੀਆ)",   # Jivitputrika Vrat (Jitiya)
    "sarva_pitru_amavasya": "ਸਰਵ ਪਿਤਰ ਮੱਸਿਆ (ਮਹਾਲਿਆ)",   # Sarva Pitru Amavasya (Mahalaya)
    "narak_chaturdashi": "ਨਰਕ ਚੌਦਸ (ਰੂਪ ਚੌਦਸ)",   # Narak Chaturdashi (Roop Chaudas)
    "tulsi_vivah": "ਤੁਲਸੀ ਵਿਆਹ",   # Tulsi Vivah
    "kartik_purnima": "ਕੱਤਕ ਦੀ ਪੂਰਨਮਾਸ਼ੀ",   # Kartik Purnima
    "dev_deepawali": "ਦੇਵ ਦੀਵਾਲੀ",   # Dev Deepawali
    "makar_sankranti": "ਮਕਰ ਸੰਕ੍ਰਾਂਤੀ (ਮਾਘੀ)",   # Makar Sankranti
    "lohri": "ਲੋਹੜੀ",   # Lohri
    "holi": "ਹੋਲੀ",   # Holi
    "ekadashi": "ਇਕਾਦਸ਼ੀ",   # Ekadashi
    "santan_saptami": "ਸੰਤਾਨ ਸਪਤਮੀ",   # Santan Saptami
}

EKADASHI_PA = {
    "Kamada Ekadashi": "ਕਾਮਦਾ ਇਕਾਦਸ਼ੀ",
    "Varuthini Ekadashi": "ਵਰੂਥਿਨੀ ਇਕਾਦਸ਼ੀ",
    "Mohini Ekadashi": "ਮੋਹਿਨੀ ਇਕਾਦਸ਼ੀ",
    "Apara Ekadashi": "ਅਪਰਾ ਇਕਾਦਸ਼ੀ",
    "Nirjala Ekadashi": "ਨਿਰਜਲਾ ਇਕਾਦਸ਼ੀ",
    "Yogini Ekadashi": "ਯੋਗਿਨੀ ਇਕਾਦਸ਼ੀ",
    "Devshayani Ekadashi": "ਦੇਵਸ਼ਯਨੀ ਇਕਾਦਸ਼ੀ",
    "Kamika Ekadashi": "ਕਾਮਿਕਾ ਇਕਾਦਸ਼ੀ",
    "Shravana Putrada Ekadashi": "ਸਾਵਣ ਪੁੱਤਰਦਾ ਇਕਾਦਸ਼ੀ",
    "Aja Ekadashi": "ਅਜਾ ਇਕਾਦਸ਼ੀ",
    "Parsva Ekadashi": "ਪਾਰਸ਼ਵ ਇਕਾਦਸ਼ੀ",
    "Indira Ekadashi": "ਇੰਦਰਾ ਇਕਾਦਸ਼ੀ",
    "Papankusha Ekadashi": "ਪਾਪਾਂਕੁਸ਼ਾ ਇਕਾਦਸ਼ੀ",
    "Rama Ekadashi": "ਰਮਾ ਇਕਾਦਸ਼ੀ",
    "Devutthana Ekadashi": "ਦੇਵਉਠਨੀ ਇਕਾਦਸ਼ੀ",
    "Utpanna Ekadashi": "ਉਤਪੰਨਾ ਇਕਾਦਸ਼ੀ",
    "Mokshada Ekadashi": "ਮੋਕਸ਼ਦਾ ਇਕਾਦਸ਼ੀ",
    "Saphala Ekadashi": "ਸਫਲਾ ਇਕਾਦਸ਼ੀ",
    "Pausha Putrada Ekadashi": "ਪੋਹ ਪੁੱਤਰਦਾ ਇਕਾਦਸ਼ੀ",
    "Shattila Ekadashi": "ਸ਼ਟਤਿਲਾ ਇਕਾਦਸ਼ੀ",
    "Jaya Ekadashi": "ਜਯਾ ਇਕਾਦਸ਼ੀ",
    "Vijaya Ekadashi": "ਵਿਜਯਾ ਇਕਾਦਸ਼ੀ",
    "Amalaki Ekadashi": "ਆਮਲਕੀ ਇਕਾਦਸ਼ੀ",
    "Papmochani Ekadashi": "ਪਾਪਮੋਚਨੀ ਇਕਾਦਸ਼ੀ",
    "Padmini Ekadashi": "ਪਦਮਿਨੀ ਇਕਾਦਸ਼ੀ",
    "Parama Ekadashi": "ਪਰਮਾ ਇਕਾਦਸ਼ੀ",
}

# optional strong regional framing per festival key
REGIONAL_NOTE_PA = {}

KOOTA_PA = {
    "varna": "ਵਰਣ",   # Varna
    "vashya": "ਵਸ਼ਯ",   # Vashya
    "tara": "ਤਾਰਾ (ਦਿਨ)",   # Tara (Dina)
    "yoni": "ਯੋਨੀ",   # Yoni
    "graha_maitri": "ਗ੍ਰਹਿ ਮੈਤਰੀ",   # Graha Maitri
    "gana": "ਗਣ",   # Gana
    "bhakoot": "ਭਕੂਟ",   # Bhakoot
    "nadi": "ਨਾੜੀ",   # Nadi
}

GANA_PA = {
    "Deva": "ਦੇਵ",
    "Manushya": "ਮਨੁੱਖ",
    "Rakshasa": "ਰਾਖਸ਼",
}

NADI_PA = {
    "Adi": "ਆਦਿ",
    "Madhya": "ਮੱਧ",
    "Antya": "ਅੰਤ",
}

VARNA_PA = {
    "Brahmin": "ਬ੍ਰਾਹਮਣ",
    "Kshatriya": "ਖੱਤਰੀ",
    "Vaishya": "ਵੈਸ਼",
    "Shudra": "ਸ਼ੂਦਰ",
}

VASHYA_PA = {
    "Chatushpada": "ਚੌਪਾਇਆ",
    "Manava": "ਮਨੁੱਖ",
    "Jalachara": "ਜਲਚਰ",
    "Vanachara": "ਵਨਚਰ",
    "Keeta": "ਕੀਟ",
}

YONI_PA = {
    "Horse": "ਘੋੜਾ",
    "Elephant": "ਹਾਥੀ",
    "Sheep": "ਭੇਡ",
    "Serpent": "ਸੱਪ",
    "Dog": "ਕੁੱਤਾ",
    "Cat": "ਬਿੱਲੀ",
    "Rat": "ਚੂਹਾ",
    "Cow": "ਗਾਂ",
    "Buffalo": "ਮੱਝ",
    "Tiger": "ਬਾਘ",
    "Deer": "ਹਿਰਨ",
    "Monkey": "ਬਾਂਦਰ",
    "Mongoose": "ਨਿਓਲਾ",
    "Lion": "ਸ਼ੇਰ",
}

TARA_PA = {
    "Janma": "ਜਨਮ",
    "Sampat": "ਸੰਪਤ",
    "Vipat": "ਵਿਪਤ",
    "Kshema": "ਖੇਮ",
    "Pratyak": "ਪ੍ਰਤਿਅਰ",
    "Sadhaka": "ਸਾਧਕ",
    "Vadha": "ਵਧ",
    "Mitra": "ਮਿੱਤਰ",
    "Ati-Mitra": "ਅਤਿ ਮਿੱਤਰ",
}

WEEKDAY_PA = {
    "Sunday": "ਐਤ",   # Sun
    "Monday": "ਸੋਮ",   # Mon
    "Tuesday": "ਮੰਗਲ",   # Tue
    "Wednesday": "ਬੁੱਧ",   # Wed
    "Thursday": "ਵੀਰ",   # Thu
    "Friday": "ਸ਼ੁੱਕਰ",   # Fri
    "Saturday": "ਸ਼ਨੀ",   # Sat
}

MONTHS_PA = [
    "ਜਨਵਰੀ",   # January
    "ਫ਼ਰਵਰੀ",   # February
    "ਮਾਰਚ",   # March
    "ਅਪ੍ਰੈਲ",   # April
    "ਮਈ",   # May
    "ਜੂਨ",   # June
    "ਜੁਲਾਈ",   # July
    "ਅਗਸਤ",   # August
    "ਸਤੰਬਰ",   # September
    "ਅਕਤੂਬਰ",   # October
    "ਨਵੰਬਰ",   # November
    "ਦਸੰਬਰ",   # December
]

CLOCK_PA = {
    "morning": "ਸਵੇਰ",
    "afternoon": "ਦੁਪਹਿਰ",
    "evening": "ਸ਼ਾਮ",
    "night": "ਰਾਤ",
}

LIMBS_PA = {
    "tithi": "ਤਿਥੀ",   # Tithi
    "nakshatra": "ਨਕਸ਼ਤਰ",   # Nakshatra
    "yoga": "ਯੋਗ",   # Yoga
    "karana": "ਕਰਣ",   # Karana
    "vara": "ਵਾਰ",   # Vara
    "paksha": "ਪੱਖ",   # Paksha
    "masa": "ਮਹੀਨਾ",   # Month
    "moon_sign": "ਚੰਦਰ ਰਾਸ਼ੀ",   # Moon sign
    "sun_sign": "ਸੂਰਜ ਰਾਸ਼ੀ",   # Sun sign
    "panchang": "ਪੰਚਾਂਗ",   # Panchang
}

# EN: The Sun does not both rise and set on this date at this latitude, so the vedic day cannot be
#     bounded by sunrise. The limbs below are reckoned from local midnight instead, and the sunrise-
#     based muhurtas are not defined.
NOTE_POLAR_PA = "ਇਸ ਤਾਰੀਖ਼ ਨੂੰ ਇਸ ਅਕਸ਼ਾਂਸ਼ ’ਤੇ ਸੂਰਜ ਨਾ ਚੜ੍ਹਦਾ ਹੈ ਤੇ ਨਾ ਛਿਪਦਾ ਹੈ, ਇਸ ਲਈ ਵੈਦਿਕ ਦਿਨ ਨੂੰ ਸੂਰਜ ਚੜ੍ਹਨ ਤੋਂ ਨਹੀਂ ਗਿਣਿਆ ਜਾ ਸਕਦਾ। ਹੇਠਾਂ ਦਿੱਤੇ ਅੰਗ ਸਥਾਨਕ ਅੱਧੀ ਰਾਤ ਤੋਂ ਗਿਣੇ ਗਏ ਹਨ ਅਤੇ ਸੂਰਜ ਚੜ੍ਹਨ ’ਤੇ ਆਧਾਰਿਤ ਮਹੂਰਤ ਲਾਗੂ ਨਹੀਂ ਹੁੰਦੇ।"

# EN: Abhijit muhurta is omitted on Wednesday, whose lord Mercury is held to spoil it.
NOTE_WEDNESDAY_PA = "ਬੁੱਧਵਾਰ ਨੂੰ ਅਭਿਜੀਤ ਮਹੂਰਤ ਨਹੀਂ ਮੰਨਿਆ ਜਾਂਦਾ, ਕਿਉਂਕਿ ਇਸ ਦਿਨ ਦਾ ਸੁਆਮੀ ਬੁੱਧ ਇਸ ਨੂੰ ਵਿਗਾੜਨ ਵਾਲਾ ਮੰਨਿਆ ਗਿਆ ਹੈ।"


def add_pa(p: dict) -> dict:
    """add_hindi's twin for Punjabi: name_pa / paksha_pa / label_pa / notes_pa."""
    from .names_i18n import add_names
    return add_names(p, "pa")
