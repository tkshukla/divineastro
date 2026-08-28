# Bhrigu Samhita (Hindi) extraction notes
Source file: bhrigu-samhita-hindi1.pdf, 638 pages, OCR'd with tesseract hin (tessdata_best). OCR quality: workable but noisy on conjuncts/matras — cross-read carefully, don't trust exact spelling of technical terms.
Publisher/edition/author unknown so far (checking front matter) — treat as potentially still-in-copyright modern Hindi commentary/compilation unless front matter says otherwise; extract FACTS/RULES in own words, do not reproduce Hindi prose verbatim.

## Book identity (from front matter, pages 1-9)
Title: "भृगुसंहिता फलित-दर्पण / फलित-प्रकाश" (Bhrigu Samhita Phalit-Darpan / Phalit-Prakash). Nominal ancient author "Bhrigu Rishi" but this is a MODERN compilation — publisher "देहाती पुस्तक भण्डार" (Dehati Pustak Bhandar), Delhi; preface signed "कृष्णपुरी, मथुरा" dated "रामनवमी सं. २०३२ वि." = Vikram Samvat 2032 ≈ **1975 CE**. Author name in preface OCR'd unclearly (something like "Rakesh Baukit/Bawaria" — uncertain).
**COPYRIGHT STATUS: likely still in copyright (1975 publication).** Per policy: do NOT reproduce Hindi prose verbatim anywhere, even in scratch notes — extract only facts/rules, paraphrased, in English, for eventual citation as "traditional Bhrigu-school prediction, as compiled in [this specific published edition]" rather than quoting source text.

## Book structure (from table of contents, pages 6-9):
**Part 1 (खंड 1): Foundations** — tithi, nakshatra (+ pada/chrono-syllable naming), vara (weekday), rashi, graha nature/effects, house significations, trikona/kendra, exaltation/debilitation/moolatrikona, planetary friendship (own/friendly/enemy sign results), 6-fold planetary strength, planetary "pada" (a term to check), lord-of-house-in-various-placements results, daily transit effects, "family combined" reading, chart correction methods.
**Part 2 (खंड 2): "फलादेश" (predictions) — THE BIG SECTION.** For EACH of the 12 Lagnas (Mesha through Meena), gives: (a) general Lagna result, then (b) each of Sun/Moon/Mars/Mercury/Jupiter/Venus/Saturn/Rahu/Ketu's result **placed in each of the 12 houses from that Lagna**. This is a massive combinatorial dataset: 12 lagnas × 9 grahas × 12 houses ≈ 1300 short prediction entries — essentially the classical "planet in Nth house, per ascendant" system, more granular than Brihat Jataka ch.20 (which wasn't lagna-specific). Runs roughly pages 93-565 (per TOC page numbers).
**Part 3 (तृतीय खंड): Conjunctions & misc** — 2/3/4/5/6-planet conjunction ("yuti") results, women's horoscopy ("स्त्री-जातक"), "विशिष्ट योग" (special yogas), "विविध" (miscellaneous). Pages ~565+.

## Cross-check: grah-shanti remedies (page 13, gemstone/donation-per-planet list)
Matches app's remedies.py CHARITIES/GEMSTONES dicts closely (same planet→gem→donation-item associations). Minor extra items noted (red lotus for Sun, conch for Moon) but largely redundant confirmation, not new.

## Pages read: 1-60

### Pages 21-45: rest of Part 1 foundations
All values (exaltation degrees, moolatrikona ranges, natural friendship table, aspect quarter/half/3quarter/full-sight rules incl. Mars→4&8, Jupiter→5&9, Saturn→3&10 special full aspects) **triple-confirm exact match with vargas.py's existing EXALTATION_DEGREE, MOOLATRIKONA, GRAHA_DRISHTI constants** (this is now the 3rd independent classical source agreeing, after BPHS and Brihat Jataka). No new data, good confidence-builder only.

### Pages 46-60: Dignity-state delineations — GOOD CANDIDATE
Short (3-5 sentence) personality/life delineation for EACH of 9 grahas (7 classical + Rahu/Ketu) × EACH of 6 dignity states (exalted / moolatrikona / own-sign / friendly-sign / enemy-sign / debilitated) = ~54 entries. E.g. exalted Sun: "fair-complexioned, fortunate, brave, wealthy, prosperous, famous, happy, learned, a magistrate/commander"; debilitated Saturn (in Aries): "independent thinker, has relatives, willful, strong-bodied, high official, village head, happy, handsome but fickle." This is a richer, more specific version of what vargas.py's DIGNITY_TEXT currently provides as generic short phrases ("exalted — honoured, given more than it strictly earned"). GOOD CANDIDATE to enrich engine.py's planet_strength() notes with per-planet-specific dignity text instead of the current one-size-fits-all phrasing — but must be written in own English words (copyright caution), cited generically as "traditional Bhrigu-school delineation."
Note: general framing rule stated (p.56): 3+ planets in enemy signs → generally unhappy but happiness may come late in life; 3+ in debilitation → foolish. A soft severity-counting principle, could pair with existing scoring.

## Pages 61-71: rest of Part 1
Generic house-lordship strength rules (exalted/own-sign lord → good result for that house; benefic occupant → good; malefic occupant → reduces good; kendra=full strength; trikona→wealth; 2nd/11th→income; 3rd→valor; 6/8/12→difficulty) — all standard, matches engine.py's existing scoring philosophy conceptually, nothing new to add verbatim. A combustion-by-degree rule given but numbers look OCR-garbled/self-contradictory — not reliable enough to use.

## Part 2 structure CONFIRMED (pages 72+): the big combinatorial dataset
For each of 12 Lagnas, the book gives ~108 numbered "example horoscopes" (9 grahas × 12 houses-from-that-Lagna), each a short (2-4 sentence) prediction. Confirmed exact count for Mesha (Aries) Lagna: entries #116-223 = 108 entries (Sun 116-127, Moon 128-139, Mars 140-151, Mercury 152-163, Jupiter 164-175, Venus 176-187, Saturn 188-199, Rahu 200-211, Ketu 212-223). Same pattern repeats for all 12 lagnas per TOC (entry ranges up to #1322 for Meena/Pisces lagna) = **~1300 total short predictive entries** — the complete classical "planet in Nth house from Lagna X" system, exhaustively tabulated.
Also: each entry serves DOUBLE DUTY per the book's own instructions (pages 73-74) — used both for natal (sthayi/permanent) placement AND for transit (gochar/temporary) reading of the same planet-in-sign-relative-to-that-lagna. Clever reuse, not two datasets.
**SCALE REALITY CHECK: transcribing and verifying ~1300 individual short Hindi predictions from noisy OCR accurately is its own large sub-project — not something to rush through in this pass.** Given full-coverage instruction, I will keep reading/skimming every chunk to fulfill that, but will characterize content by sampling rather than exhaustively cataloging every entry in these notes (the pattern is now fully understood; only flag if something structurally breaks the pattern, e.g. a special yoga aside, a materially different phrasing style, or the Part 3 sections at the end).

## Pages 81-100: confirmed actual entry content/style (Mesha Lagna, Sun/Moon/Mars/Mercury/Jupiter through house 7)
Each entry = (1) which sign the planet occupies relative to Lagna + dignity note (own/friend/enemy sign), (2) 2-4 sentence effect for that house, (3) explicit walk-through of EVERY aspect (drishti) the planet throws from that position and the effect on each aspected house, (4) closing one-line character summary. E.g. "Mars in 1st (own sign, Aries): sound body, self-reliant, brave... but as 8th-lord causes occasional illness though long life; 7th aspect (on Venus's sign) causes some loss re: wife/business." This is a fully pre-composed version of exactly what engine.py's evidence/scoring architecture computes programmatically (house placement + dignity + aspects + lordship) — written out by hand for every combination.

**PRACTICALITY DECISION:** ~1300 such entries exist across 12 lagnas. Faithfully transcribing/translating all of them from noisy Hindi OCR (already showing conjunct/matra errors, garbled words) is its own large project, not achievable to full fidelity in this pass. Will continue opening and skimming every remaining chunk (per "full coverage"), but will log only pattern-confirmations and any structural anomalies from here, not re-transcribe repetitive entries. When it's time to write code, will use a representative, spot-verified sample rather than claiming full-corpus coverage, and say so plainly.

## Skimming forward through remaining Lagnas (pages 101+)
Sampled Vrishabha (Taurus, p.115+) and Kanya (Virgo, p.301+) lagnas directly — pattern held 100% identical to Mesha. Confidence is high the same holds for the other 9 lagnas (Mithuna, Karka, Simha, Tula, Vrishchika, Dhanu, Makara, Kumbha, Meena) not individually re-verified line-by-line, all opened/skimmed through to Meena lagna ending at page 580.

## Part 3 (pages 581-638): conjunctions, women's chapter, special yogas
- **Planetary conjunctions (yuti), 2 through 7 planets together in one house** (pages 582-613): full combinatorial catalog — 21 pairs, 35 triples, ~35 quads, ~21 quints, ~7 sextets, 1 septet — each with a short (1-2 sentence) personality/outcome description. Parallels Brihat Jataka ch.14's pairwise conjunctions but is this book's own (differently-worded) tradition. GOOD CANDIDATE for the pair-level (21) and maybe triple-level (35) entries specifically — bounded, classic, reusable — but this text is likely still in copyright (1975 pub.) so must be paraphrased in original English wording, cited generically ("traditional Bhrigu-school conjunction delineation"), never quoted.
- **स्त्री-जातक (Women's horoscopy)** (pages 613-620): same category as Brihat Jataka ch.24 — physical/temperament indicators (lower-risk, could keep) mixed with husband-abandonment/widowhood/infidelity/chastity judgments (same regressive-content concern) — **applying the same exclusion decision as Brihat Jataka ch.24**, noting only the neutral physical/temperament rules as usable if ever wanted.
- **विशिष्ट योग (Special Yogas)** (pages 621-636): ~50 highly specific named-configuration Rajayogas (narrow multi-planet exact placements → "becomes a king/emperor") of low generalizability (same issue as Brihat Jataka ch.11) — but also a clean catalog of ~15 named STRUCTURAL yogas with simple mechanical rules, good candidates: **Chatuhsara Yoga** (all planets in the 4 kendras, or all in Aries/Cancer/Libra/Capricorn = "very wealthy king"), **Danda Yoga** (all planets in Gemini/Virgo/Sagittarius/Pisces), **Amar Yoga** (all malefics in kendras OR all benefics in kendras), **Ekavali Yoga** (7 planets occupy 7 consecutive houses starting anywhere), **Vani Yoga** (all planets in any houses except 1st/2nd/12th), **Hans Yoga** (all planets in 1st/5th/7th/9th), **Dhwaja Yoga** (malefic in 8th + benefics in Lagna), **Simhasan Yoga** (all planets in 2nd/3rd/6th/8th/12th), **Karma Yoga** (all 7 in 10th+11th, or 9th+7th), **2nd Hans Yoga** (all planets in Aries/Kumbha/Dhanu/Tula/Makara/Vrishchika). These mirror Brihat Jataka's Nabhasa-yoga engineering style (mechanical whole-chart sign/house pattern-matching) — GOOD CANDIDATE, cite as Bhrigu-school special yogas, cross-check against Nabhasa yogas for overlap before adding (some may be functionally identical, e.g. Chatuhsara ≈ Kamala from Brihat Jataka ch.12).

## === BHRIGU SAMHITA: COMPLETE (all 638 pages read) === Book's own colophon confirms "1635 example horoscopes total."

### TOP CANDIDATES from this book, ranked:
1. **Dignity-state delineations** (54 entries: 9 grahas × 6 states) — richer per-planet dignity text than vargas.py's current generic DIGNITY_TEXT.
2. **Named structural "special yogas"** (~15 from Part 3) — mechanical, Nabhasa-yoga-like, good engineering fit.
3. **Pairwise conjunction meanings** (21, Part 3) — bounded, enriches ASPECTS["conjunction"] alongside Brihat Jataka's own 21.
4. **The ~1300-entry planet-in-house-per-Lagna corpus (Part 2)** — hugely valuable in principle (it's literally a hand-composed version of what engine.py computes), but impractical to transcribe in full from noisy OCR in this pass; treat as a known future asset, sample-verify a small subset if ever encoding real text from it, don't claim full coverage.
5. Triple-confirmed (3rd source) that all of vargas.py's EXALTATION_DEGREE/MOOLATRIKONA/GRAHA_DRISHTI/friendship-table constants are correct per classical consensus — good confidence, not new content.

### Excluded by my own judgment (flagging for user, same as Brihat Jataka):
- Women's-horoscopy chastity/widowhood/adultery judgments (both books) — declining to encode.
- Ultra-specific named Rajayoga combos (both books, ~30+50 entries) — too narrow/low-generalizability to encode as generic rules; app's existing kendra/trikona-lord-based Raja Yoga logic is the better generalizable model.
- Lost-horoscope/Prashna reconstruction techniques (Brihat Jataka ch.26) — not applicable, app has exact birth data.

## Copyright note reminder: Bhrigu Samhita (this specific 1975 Hindi compilation) is likely still under copyright. Everything above must be encoded as independently-phrased facts/rules in English, never as translated/quoted Hindi prose, and cited as "a traditional Bhrigu-school compilation" rather than naming this specific edition/publisher.

## Update: the ~1300-entry per-Lagna corpus is being encoded incrementally

Following a decision to actually build this (previously logged above only as
"known future asset"), work has started on `app/astro/delineation.py`'s
`BHRIGU_LAGNA_HOUSE_TEXT`, one Lagna at a time.

**Structural correction to the note above:** the earlier claim that
"[Vrishabha and Kanya] pattern held 100% identical to Mesha" was checked
again while doing the real extraction and is *mostly* right but was
imprecise in one way worth recording. Vrishabha's own printed pages open
with a numbered cross-reference table (pages ~115-120) explaining how the
book's numbered "example horoscope" system is reused for *gochar* (transit)
lookups by current sign — before the actual full-prose entries for
Vrishabha resume at page 121 in the same style as Mesha. So the corpus
really is present in full prose for every Lagna checked so far; a reader
extracting a later Lagna should expect this kind of instructional preamble
to appear at the *start* of a Lagna's section and not mistake it for the
Lagna having no prose.

**A real scan gap, found and confirmed:** printed page 107 is missing
outright from the PDF scan. Confirmed by rendering the surrounding pages at
400dpi and reading them directly — page 98 → printed "105", page 99 →
printed "106", page 100 → printed "108", with every planet's section on
that spread (this lands inside Jupiter's Aries-Lagna entries) jumping
straight from house 7 to house 11, no OCR segmentation issue. This costs
Jupiter's 8th/9th/10th-house entries for Aries Lagna specifically; left
absent in the code rather than guessed at. An automated pass trying to
detect *other* such gaps by cross-checking every page's printed page-number
against PDF page order was tried and abandoned — OCR misreads isolated
Devanagari numerals too often (single digits merge, split, or misread) to
trust as a systematic check; the one gap above was found by direct visual
inspection, which doesn't scale to all 638 pages. Future Lagnas should
expect the occasional undetected gap of this kind, treated the same way:
left absent, never guessed at, and flagged if actually noticed.

### Lagnas encoded so far

- **Aries (Mesha)** — complete except the 3-entry Jupiter gap above.
  105 of 108 entries (9 grahas × 12 houses, including Rahu/Ketu — this
  table is the only place in the app that has planet-in-house text for the
  nodes at all). Read from PDF pages 81-114 (chunks `pages_0081-0100.txt`
  and `pages_0101-0120.txt`).
- **Remaining 11 Lagnas (Taurus through Pisces)** — not yet done. Each is a
  similar-sized read (~30-35 PDF pages, ~2000 OCR lines) and paraphrase
  pass; `planet_house_text()` falls back cleanly to the Lagna-independent
  Brihat Jataka table for any Lagna not yet in `BHRIGU_LAGNA_HOUSE_TEXT`, so
  partial coverage never breaks anything — it just means those natives get
  the same generic text every Lagna got before this work started.
