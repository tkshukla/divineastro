# Work order: translate Divine Astro into ONE language (DIVASTRO-143)

You fill one language: `pa` Punjabi (Gurmukhi), `ne` Nepali (Devanagari), `as` Assamese
(Assamese/Bengali script, with ৰ and ৱ), `mr` Marathi (Devanagari) or `gu` Gujarati
(Gujarati script). Four other agents do the other four at the same time. Read
`docs/i18n.md` ("Adding a language the per-language-module way") once, then follow this.
`<code>` below is your language's code.

## Files you may edit (only these)

1. `app/lang_data/<code>.py` — all the page text (for `as` the file is `app/lang_data/as.py`)
2. `app/astro/names_<code>.py` — astrology names
3. `app/static/i18n/<code>.json` — the app's strings (subset of `app/static/i18n/en.json`)

Never edit a shared file, a test, `app/i18n.py`, another language's file, or any English or
Hindi text. Your commits touch those three files only (plus, at the very end, nothing else).

## The loop

    python -m app.lang_data check <code> --quiet     # what is left (exit 0 = complete)
    python -m app.lang_data check <code> --only names
    python -m app.lang_data check <code> --only seo --all     # every problem of one module

Never run `skeleton --force`: it deletes your work. Every key is already in the file with
the value `""` and the English text and `keep:` placeholders in the comment above it. Fill
the `""`. A value left `""` shows English on the site and the checker lists it.

Work module by module, cheapest first: `names` -> `app` (json + `ASTRO_TERMS`) -> `seo` ->
`hub` -> `vrat` -> `recurring` -> `rashifal` -> `muhurat` -> `nakshatra`. When
`check <code> --only <module>` is clean, add the key to `READY` in your file, e.g.
`READY = frozenset({"seo", "hub"})`. READY switches that module's pages on for real
(indexable, hreflang, sitemap, picker); `check` and CI refuse a READY that is not clean.
Keys: `seo rashifal vrat nakshatra muhurat recurring hub app`. A page module also needs
`names_<code>.py` complete (do names first). `recurring` needs `vrat` complete.
Then run the page tests for your language: `python -u -m tests.test_seo_regional <code>`
and `python -u -m tests.test_lang_data`, `tests.test_i18n`, `tests.test_names_i18n`,
`tests.test_i18n_app` (run tests one at a time, not in parallel). When READY changes the
English/Hindi pages (picker, hreflang, sitemap), `tests.test_seo_snapshots` will fail until
the lead re-records it: report that, do not edit the snapshot.

## Rules for the text

* **Natural everyday wording, not word-for-word.** Write what a native speaker would say
  on a good almanac or news site. If the English sentence is awkward in your language,
  restructure it. Short sentences. Titles and meta descriptions are plain text, so no
  markup, and about as long as the English.
* **Keep every placeholder** the comment under `keep:` lists, spelled exactly (`{city}`,
  `{date}`, `{name}` ...). The word order around them is yours. You may also use anything
  listed under `may also use:`. Never invent a placeholder. Do not translate what is
  inside braces. Don't glue a case ending to a city with a hyphen (`{city}-ਵਿੱਚ`); either
  attach it the way your script does for every name, or say "in the city of {city}".
* **HTML values keep their tags** (`<strong>`, `<ul><li>` ...) in the same order; write
  `&amp;` for `&`. Don't add attributes. A `lang` key (e.g. `sub_lang`) is your own code.
* **Astrology terms in the form your panchang / jyotish tradition really uses**, matching
  `names_<code>.py` (Rahu Kaal, Yamaganda, Gulika, Abhijit Muhurat, tithi, nakshatra,
  rashi names). Use one word for one thing across all three files. Where traditions
  differ (solar vs lunar months; Amanta/Purnimanta; Nanakshahi, Bohag-year,
  Vikram/Shaka calendars, Gujarati New Year after Diwali, Gudi Padwa), follow the
  tradition of your language's readers and note it in the docstring of
  `names_<code>.py`. The vrat dates come from the engine and are the same for everyone.
* **No machine-literal Hindi calques.** Don't translate from the Hindi text and don't
  copy Hindi spellings into your language: translate from the English, check the Hindi
  only for what a term means. Marathi and Nepali share Devanagari with Hindi but are not
  Hindi: use real Marathi / Nepali words and grammar (Marathi: ळ, `मध्ये`, `आहे`, `पाहा`;
  Nepali: `हुन्छ`, `गर्नुहोस्`, honorific `तपाईं`). Assamese is not Bengali: ৰ for র, ৱ
  for ব in Assamese words, `আপুনি`, `কৰক`, `হয়`. Gujarati and Punjabi likewise: no
  Hindi words where your language has its own.
* **Numerals: ASCII digits (0-9)**, as every existing language does. Dates, times, years,
  guna scores stay ASCII. Dates are composed by the site (`day month year`); you only
  supply month names (`MONTHS` in names) and weekday names.
* **Honorifics and tone:** respectful second person, the polite form (Punjabi ਤੁਸੀਂ,
  Nepali तपाईं, Assamese আপুনি, Marathi आपण / तुम्ही, Gujarati તમે). One register
  throughout. No slang, no exclamation marks the English lacks. Medical/legal/financial
  disclaimer text must keep its meaning exactly.
* **Latin letters:** none, except the words the checker allows by default (WhatsApp, UPI,
  PDF, IST, AM/PM, Divine Astro, N/E in coordinates, D1..D60). Anything else (a brand, an
  example name) goes into `ALLOW_LATIN` in your file with a reason in a comment.
  No Devanagari in Gurmukhi/Gujarati/Assamese text; no Bengali-block letters other than
  ৰ ৱ in Assamese. Use your script's own danda/punctuation conventions consistently.
* **City and state names** the way your language's newspapers spell them (`CITY_NAMES`,
  `STATE_NAMES`). Slugs never change.
* **Facts:** do not change numbers, dates or rules; a translation that says something
  different from the English is a bug. If you think the English is wrong, list it in your
  report, do not "fix" it in translation.
* `AKSHAR` (namakshar script mapping) is already set and verified; leave it unless
  `check --only akshar` fails.

## Quality gate before you report

1. `python -m app.lang_data check <code>` exits 0 (or lists only modules you deliberately
   left un-READY, each with the reason).
2. The tests named above are green for your language.
3. Open 3 pages in the test client or a browser (`/<code>/panchang/pune`,
   `/<code>/rashifal/mesh`, `/<code>/vrat-tyohar`) and read them as a native would: grammar,
   spacing around placeholders, no English left, no half-sentences.

## The native-speaker review list (deliver with your work)

End your report with a table a human reviewer can work through without opening code.
One row per judgement call, grouped: (1) names and traditions (month system, nakshatra
spellings, Rahu Kaal wording, festival names that differ by region); (2) words you chose
between alternatives (give both); (3) the 15 sentences you are least sure of (key, your
text, the English, why); (4) anything in the English you believe is wrong or untranslatable.
Also paste the six short registry strings in `app/i18n.py` for your language (`choose`,
`hint`, `yes`, `not_now`, `notice`, `english_answer`) with a confidence note; they were
written once, by hand, for review, and you may propose a better wording (the lead edits
`app/i18n.py`; you do not).
