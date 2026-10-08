# Assamese (as) review sheet, DIVASTRO-146

Written by a non-native translator (Claude). Please read as a native Assamese reader and mark anything that sounds Bengali, Hindi or stiff. Files: `app/lang_data/as.py`, `app/astro/names_as.py`, `app/static/i18n/as.json`.

## 1. The 40 most visible strings

| # | English | Assamese |
|---|---|---|
| 1 | Panchang | পঞ্জিকা |
| 2 | Today's Panchang in {city} | {city} চহৰৰ আজিৰ পঞ্জিকা |
| 3 | Rahu Kaal | ৰাহুকাল |
| 4 | Yamaganda / Gulika Kaal | যমগণ্ড / গুলিক কাল |
| 5 | Abhijit Muhurat | অভিজিৎ মুহূৰ্ত |
| 6 | Choghadiya | চৌঘড়িয়া |
| 7 | Tithi / Nakshatra / Yoga / Karana | তিথি / নক্ষত্ৰ / যোগ / কৰণ |
| 8 | Sunrise / Sunset | সূৰ্যোদয় / সূৰ্যাস্ত |
| 9 | Moonrise / Moonset | চন্দ্ৰোদয় / চন্দ্ৰাস্ত |
| 10 | Shukla / Krishna paksha | শুক্ল / কৃষ্ণ পক্ষ |
| 11 | Today's Rashifal | আজিৰ ৰাশিফল |
| 12 | Moon sign | চন্দ্ৰ ৰাশি |
| 13 | Favourable day / Mixed day / Take it easy | অনুকূল দিন / মিশ্ৰ দিন / সংযমৰ দিন |
| 14 | Sade Sati | সাড়ে সাতি |
| 15 | Vrat & festivals | ব্ৰত আৰু উৎসৱ |
| 16 | Today's vrat & festivals | আজিৰ ব্ৰত আৰু উৎসৱ |
| 17 | Ekadashi {year}: dates and parana time | একাদশী {year}: তাৰিখ আৰু পাৰণৰ সময় |
| 18 | Parana (breaking the fast) | পাৰণ (উপবাস ভঙা) |
| 19 | Diwali (Lakshmi Puja) | দীপাৱলী (লক্ষ্মী পূজা) |
| 20 | Dussehra (Vijayadashami) | বিজয়া দশমী |
| 21 | Sharad Navratri begins | শাৰদীয় নৱৰাত্ৰি আৰম্ভ |
| 22 | Kundali Milan (36 guna) | কুণ্ডলী মিলন (36 গুণ) |
| 23 | Free Janam Kundali | বিনামূলীয়া জন্মকুণ্ডলী |
| 24 | Naam se Kundali Milan | নামেৰে কুণ্ডলী মিলন |
| 25 | Muhurat Finder | মুহূৰ্ত বিচাৰক |
| 26 | Vivah Muhurat | বিবাহ মুহূৰ্ত |
| 27 | Nakshatra / Rashi | নক্ষত্ৰ / ৰাশি |
| 28 | Mesh, Vrishabh, Mithun ... | মেষ, বৃষ, মিথুন, কৰ্কট, সিংহ, কন্যা, তুলা, বৃশ্চিক, ধনু, মকৰ, কুম্ভ, মীন |
| 29 | Sunday ... Saturday | দেওবাৰ, সোমবাৰ, মঙ্গলবাৰ, বুধবাৰ, বৃহস্পতিবাৰ, শুক্ৰবাৰ, শনিবাৰ |
| 30 | January ... December | জানুৱাৰী ... ডিচেম্বৰ |
| 31 | Chaitra ... Phalguna | চ'ত, বহাগ, জেঠ, আহাৰ, শাওন, ভাদ, আহিন, কাতি, আঘোণ, পুহ, মাঘ, ফাগুন |
| 32 | Open the full Panchang — any city, any date | সম্পূৰ্ণ পঞ্জিকা খোলক — যিকোনো চহৰ, যিকোনো তাৰিখ |
| 33 | Get your free kundali | বিনামূলীয়া কুণ্ডলী বনাওক |
| 34 | Share on WhatsApp | হোৱাটছএপত শ্বেয়াৰ কৰক |
| 35 | Stay in touch | আমাৰ লগত যোগাযোগত থাকক |
| 36 | Terms & Conditions | নিয়ম আৰু চৰ্তাৱলী |
| 37 | Privacy Policy | গোপনীয়তা নীতি |
| 38 | Contact Us | আমাৰ লগত যোগাযোগ কৰক |
| 39 | Sign in | ছাইন-ইন কৰক |
| 40 | Astrological readings are ... not medical, legal or financial advice. | জ্যোতিষ শাস্ত্ৰৰ ভৱিষ্যদ্বাণী কেৱল পথ-প্ৰদৰ্শন আৰু মনোৰঞ্জনৰ বাবে দিয়া হৈছে। ই চিকিৎসা, আইনী বা বিত্তীয় পৰামৰ্শ নহয়। |

## 2. Astrology-term decisions

| Term | Chosen | Rejected | Why |
|---|---|---|---|
| Panchang | পঞ্জিকা (pages); পঞ্চাঙ্গ only when explaining the "five limbs" | পাঁজি | পঞ্জিকা read as the standard almanac word; please confirm |
| Lunar months | চ'ত বহাগ জেঠ আহাৰ শাওন ভাদ আহিন কাতি আঘোণ পুহ মাঘ ফাগুন | Sanskrit forms (চৈত্ৰ, বৈশাখ ...) | Assamese usage. The engine's months are lunar (amanta), so SOLAR_MASA is empty although the Bhaskarabda calendar is solar |
| Weekdays | -বাৰ forms; Sunday = দেওবাৰ | ৰবিবাৰ | দেওবাৰ is the everyday word |
| Gregorian months | as in item 30 | -ৰি endings, চেপ্টেম্বৰ | As the brief and media write them |
| v-sound | ৱ inside a word (দেৱ, অমাৱস্যা, নৱমী, দীপাৱলী); ব at word start (বিজয়া, বসন্ত, বিশাখা) | ৱ everywhere | My understanding of Assamese practice; the namakshar mapping (ব→ৱ) comes from the plumbing |
| Rahu Kaal | ৰাহুকাল | ৰাহু কাল | One word, as bn does |
| Yamaganda | যমগণ্ড | যমঘণ্ট | Sanskrit form |
| Gulika Kaal | গুলিক কাল | গুলিকা | As in the Bengali tradition |
| Varjyam | বৰ্জ্যম | বৰ্জ্য ("waste") | Same caution as bn |
| Nakshatras | ৰোহিণী, পূৰ্ব ফল্গুনী, পূৰ্বাষাঢ়া, পূৰ্ব ভাদ্ৰপদ ... | Bengali spellings | Space after পূৰ্ব/উত্তৰ for the Phalguni and Bhadrapada pairs, none for Ashadha |
| Gana | দেৱ / মানৱ / ৰাক্ষস | নৰ for Manushya | Matches the engine's "Manushya" |
| Koota names | বৰ্ণ বশ্য তাৰা যোনি গ্ৰহ মৈত্ৰী গণ ভকূট নাড়ী | ৰাশিকূট for Bhakoot | Matches the English key |
| Kundali Milan | কুণ্ডলী মিলন | যোটক বিচাৰ (Bengali), কোষ্ঠী বিচাৰ | Neutral |
| Janam kundali | জন্মকুণ্ডলী | জন্মপত্ৰিকা, কোষ্ঠী | |
| Sade Sati | সাড়ে সাতি | সাড়েসাতি | |
| Dussehra | বিজয়া দশমী | দশেৰা | Brief's choice; দশেৰা appears once in brackets in the about text |
| Sharad Navratri | শাৰদীয় নৱৰাত্ৰি আৰম্ভ + REGIONAL_NOTE "দুৰ্গা পূজা" | | The only regional note; no Bihu observances (not in the engine) |
| Bhai Dooj | ভাতৃ দ্বিতীয়া | ভাইফোঁটা (Bengali) | |
| Vasant Panchami | বসন্ত পঞ্চমী (সৰস্বতী পূজা) | | Saraswati Puja is the Assamese name |
| Makar Sankranti | মকৰ সংক্ৰান্তি | with মাঘ বিহু | Not an engine observance |
| Houses | ভাৱ | ভাব | ৱ rule |
| House ordinals | প্ৰথম, দ্বিতীয় ... দ্বাদশ | 1ম, 2য় | Plain words |
| Choghadiya quality | শুভ / মধ্যম / অশুভ | | |
| Drik Panchang | দৃক পঞ্জিকা | | |

## 3. Where I am unsure

1. **ৰ/ৱ by rule, not dictionary.** Words most likely wrong: নৱমী/নৱৰাত্ৰি/নৱাংশ (maybe নবমী...), অমাৱস্যা, জীৱিতপুত্ৰিকা, গোৱৰ্ধন, the karanas বৱ/বালৱ/কৌলৱ, ধ্ৰুৱ, শিৱ.
2. **Apostrophe** in চ'ত, মে', ল'ৰা, নগ'ল, ডাউনল'ড: ASCII ' is used for the Assamese mark. Confirm the form.
3. **Imperatives**: কৰক, চাওক, সোধক, বাছক, খোলক, বনাওক, লিখক, পাওক. Check পাওক, and whether "বিচাৰক" (Finder, in মুহূৰ্ত বিচাৰক) reads as a noun rather than "please search".
4. **Negation**: নাই / নহয় / নাথাকে / নকৰিব / নোৱাৰি / নাযায়.
5. **"{date} তাৰিখে পৰিছে"** for "falls on" on festival pages; a native may prefer "{date}ত পৰিছে".
6. **{time}লৈকে / {time}ৰ পৰা** suffixes attached directly to the placeholder with no hyphen.
7. **Festival rule line** displays "আহিন (অমান্ত)কৃষ্ণ অমাৱস্যা:প্ৰদোষ কাল ..." with no space after "(অমান্ত)" or ":". This comes from how the engine joins VRAT_RULES `head`, `tithi` and `rule.*` for every language; not changed here.
8. **Loan words in the app**: ছাইন-ইন, ইউজাৰনেম, পাছৱৰ্ড, একাউণ্ট, চাৰ্ভাৰ, ছেটিং, এছএমএছ, কুপন. A native UI might prefer native words.
9. **Western-astrology terms** (annual profection, zodiacal releasing, firdaria, sect, angular/succedent/cadent): বাৰ্ষিক প্ৰফেক্সন, ৰাশিচক্ৰীয় ৰিলিজিং, ফাৰ্দাৰিয়া, ছেক্ট, কেন্দ্ৰ/পণফৰ/আপোক্লিম. Low confidence.
10. **"এআই জ্যোতিষী", "এআই গুৰু"**: AI transliterated (Latin AI would also pass the checker).
11. **Hindi-belt festival names** (গুড়ি পাডৱা, কৰৱা চৌথ, সকট চৌথ, ছঠ পূজা, জিতিয়া, ললহী ছঠ): transliterated; Assamese readers may know them differently.
12. **Naam-milan input**: the engine reads English or Hindi names, not Assamese script; examples are therefore Latin (Ram, Sita) and the explainer shows Priya → পী, Kshitij → কী.
13. **Rashifal sentences** (RASHIFAL_MOON_HOUSE etc.) were written freely; please read two or three for naturalness.
14. **Long traits** (NAKSHATRA_TRAITS, RASHI_TRAITS) are faithful but may read as translationese in places.
15. **Yoni animals**: মেকুৰী (cat), ইন্দুৰ (rat), ঘোঁৰা, হাতী, নেউল, বান্দৰ, ম'হ — check spellings.

## 4. Conventions chosen

- Polite আপুনি register; "আমি" for the site; no exclamation marks beyond the English.
- ASCII digits everywhere; danda । ends sentences.
- Hindi (Devanagari) glosses that the English pages show beside names were dropped; the pages show only Assamese.
- "Kathas" = কথা; "free" = বিনামূলীয়া.
- Latin kept only for Divine Astro, UPI/UTR/PDF, payment-app names, OAuth, YYYY-MM-DD, the e-mail placeholder and the Latin example names in the naam-milan explainer (ALLOW_LATIN / KEEP_ENGLISH in as.py).
- The six registry strings in `app/i18n.py` were not reviewed here (the lead owns them); a native reader should check them against this sheet's spellings.
