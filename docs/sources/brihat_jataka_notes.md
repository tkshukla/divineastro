# Brihat Jataka extraction notes (source: N. Chidambaram Iyer trans., Madras, 1885 — public domain)

Cite as: "Brihat Jataka of Varaha Mihira, tr. N. Chidambaram Iyer (1885), ch. X stanza Y"

## Book structure (from p.40 preface): 28 chapters total
1-2: definitions/elementary principles (zodiacal, planetary)
3: animal/vegetable horoscopy (SKIP — not applicable to human natal consultations)
4: Nisheka (conception)
5(?): Lagna/birthplace determination
6: Balarishta (early death)
7: Ayurdaya (length of life)
8: avocations/wealth
9+: Raja and other Yogas (several chapters)
Pravrajya yoga (renunciation)
Anishtadhyaya (malevolent combinations)
chapter on women (Stri Jataka)
chapter on manner/nature of death
chapter on horoscope when birth-time unknown
(not a complete list per translator)

## Pages read so far: 1-80 (chunks pages_0001-0020 through pages_0061-0080)

### Pages 1-40: front matter + Introduction (philosophical: fatalism vs free will, astrology's validity, ayanamsa/precession discussion, Nadigrandhams). No encodable rules. Confirms translator N. Chidambaram Iyer, Madras 1885 — genuinely PD, no copyright concern.

### Chapter I (Definitions, zodiacal) — pages 42-61 (stanzas 1-20)
ALREADY IN APP (vargas.py) — cross-checked, MATCHES exactly, no changes needed:
- Exaltation signs: Sun-Aries, Moon-Taurus, Mars-Capricorn, Mercury-Virgo, Jupiter-Cancer, Venus-Pisces, Saturn-Libra ✓ matches EXALTATION
- Deep exaltation degrees: Sun 10, Moon 3, Mars 28, Mercury 15, Jupiter 5, Venus 27, Saturn 20 ✓ matches EXALTATION_DEGREE exactly
- Moolatrikona signs: Sun-Leo, Moon-Taurus, Mars-Aries, Mercury-Virgo, Jupiter-Sagittarius, Venus-Libra, Saturn-Aquarius ✓ matches MOOLATRIKONA signs
- House significations, Kendra/Panaphara/Apoklima (angular/succedent/cadent) ✓ conceptually already in app
- Vargottama definition ✓ likely already handled
NOT in app currently (candidates to add, low priority since Ch.1 is mostly foundational, not predictive):
- Melothesia by RASI (body part per sign, Kalapurusha) — app's knowledge.py already has SIGN_BODY (Western melothesia); this Vedic version (Aries=head...Pisces=feet) is actually THE SAME mapping, already effectively covered.
- Planetary aspect STRENGTH by distance (quarter/half/3-quarter/full sight at 3rd/10th, 5th/9th, 4th/8th, 7th houses respectively, with Saturn/Jupiter/Mars getting full sight on their special houses) — app's GRAHA_DRISHTI in vargas.py already encodes special aspects (Mars 4,7,8; Jupiter 5,7,9; Saturn 3,7,10) as binary present/absent. Brihat Jataka actually grades ALL aspects by strength (quarter/half/three-quarter/full), a finer-grained model. Worth flagging as a possible enhancement but changes aspect strength semantics — NOT added without discussion.

### Chapter II (Definitions, planetary) — pages 61-71 (stanzas 1-21)
- Planetary natures/castes/gunas/body parts/colors/directions/gemstones-ish associations (already broadly covered in knowledge.py PLANETS dict + remedies.py gemstones, different framing)
- Natural friendships (stanza 15-18): derivation method via Satyacharya (lords of 2/12/5/9/8/4 houses from Moolatrikona + exaltation lord) cross-checked against worked example for Sun → Mercury neutral, Venus/Saturn enemies, Moon/Mars/Jupiter friends. THIS MATCHES standard BPHS natural friendship table already presumably in chart_service/matching.py. No new info, but good independent confirmation source if a citation is ever wanted for matching.py.
- Planetary strength types (Sthanabala/Dikbala/Cheshtabala/Kalabala/Naisargikabala) — a 5-fold classical strength taxonomy (subset of Shadbala's 6). App does NOT implement Shadbala (noted in vargas.py's NOT_IMPLEMENTED per its docstring — need to verify). POTENTIAL ADDITION but Shadbala is a big undertaking; flag only.

### Chapter III (Animal/vegetable horoscopy) — pages 72-76: SKIPPED, not applicable to human consultations app.

### Chapter IV (Nisheka/conception) — pages 76-80+ (in progress)
Rules on: conception timing via Moon-Mars relationship, gender-of-child prediction (odd/male vs even/female signs & navamsas for Sun/Jupiter/Moon), which planet represents father/mother by day/night birth, and — NOTE — several stanzas predict maternal/child DEATH or miscarriage from specific malefic placements during pregnancy.
FLAG FOR PRODUCT DECISION: these death/miscarriage-prediction rules are classical and textually real, but encoding automated "the pregnant woman will die" style outputs in a consumer app is an ethically/product-sensitive call — do NOT encode without explicit user sign-off. The gender-prediction and conception-timing rules are lower-stakes and more usable for the app's existing "children" topic (topics.py).

## PRODUCT DECISION (user, 2026-08-26): include Balarishta (infant-death) and Ayurdaya (lifespan) content FULLY, faithfully, no gating requested. Proceed to encode when writing code — cite classically, present factually (not alarmist), but do not omit or hide behind disclaimers per explicit instruction.

### Chapter VI (Balarishta / early death) — pages 101-108
~16 death-yoga combinations (malefics in various houses from Moon/Lagna at birth => infant dies at various intervals) PLUS 16 counteracting/cancellation yogas (powerful Jupiter in Lagna, Moon full & benefic-flanked, etc.) — the cancellation list is the actually useful/positive half and mirrors the app's existing "cancellation" pattern (doshas.py Manglik cancellations). TODO when coding: encode as a scored list like Manglik dosha, weighted toward reporting cancellations prominently.

### Chapter VII (Ayurdaya / longevity) — pages 108-120+ (in progress, several competing methods: Pindayurdaya [planetary exaltation-based years], Satyacharya's method [Navamsa-based], Jeevasarma's method). Multiple non-agreeing classical methods — the module's own "disputed rules, exposed as constants" pattern (vargas.py) fits well here; should implement Pindayurdaya as primary (author's preferred, per commentator) and flag others as alternates.
Exaltation-based max years per planet (Pindayurdaya): Sun 19, Moon 25, Mars 15, Mercury 12, Jupiter 15, Venus 21, Saturn 20. (Lagna gives years = Navamsas-of-rising-sign-risen, per one reading, or signs-from-Aries per another.)
Astangata (combustion) orb table given here (Mars 17°, Mercury 14°/12°retro, Jupiter not given yet, Venus 10°/8°retro, Saturn 15°, Moon 12°) — DIFFERENT from app's COMBUSTION_ARC (Mercury only, 14°/12°) — this text gives combustion arcs for ALL planets, not just Mercury. Worth adding as an extension if Ayurdaya is implemented, but don't retrofit onto existing Budha-Aditya logic without care (different classical purpose).

### Chapter VIII (Dasas/Antardasas) — pages 126-140+
The author's OWN dasa system (positional: Kendra/Panaphara/Apoklima order, strength-based) — per translator's own footnote (p.139-140) this system is "hardly studied by Indian astrologers" in practice; real astrologers use "Udu or Nakshatra dasa" = **exactly Vimshottari** (Sun 6, Moon 10, Mars 7, Rahu 18, Jupiter 16, Saturn 19, Mercury 17, Ketu 7, Venus 20 = 120 yrs, assigned by birth-nakshatra triangular groups) — CONFIRMS app's existing chart_service.vimshottari years/lord order against a 3rd primary source. No change needed, just a nice citation opportunity.

**HIGH VALUE, NOT YET IN APP: per-planet Mahadasha effects (stanzas 12-18).** Benefic-dasa-effect and malefic-dasa-effect text given for EACH of Sun/Moon/Mars/Mercury/Jupiter/Venus/Saturn (wealth sources, character shifts, ailments, relationships) — e.g. "benefic Mars dasa: fights enemies, wealth through brother/king/lands; malefic Mars dasa: hates sons/friends/wife, disease from blood/fever/bile, becomes vicious." This is DIRECTLY usable for the app's "timing" topic (topics.py) and remedies.py (which already computes active mahadasha lord but has no effect-text for it). STRONG CANDIDATE to encode as MAHADASHA_EFFECTS = {planet: {"benefic": "...", "malefic": "..."}} cited to Brihat Jataka ch.8 stanzas 12-18, gated on whether the dasha lord is itself benefically or malefically disposed in the chart (dasa "Sampoorna/Purna" vs "Rikta/Anishta" quality classification given in stanzas 5-7, based on planet's own dignity — this maps cleanly onto existing planet_strength() scoring in engine.py!).

Antardasha proportion rule (stanza 3-4: 1/2 : 1/3 : 1/7 : 1/4 weighting by house from dasa lord) — a structural rule, not needed since app presumably computes antardasha by standard Vimshottari proportional-year division already; this is the author's alternate system, skip.

### Chapter IX (Ashtakavarga) — pages 141-158
FULL classical Ashtakavarga: benefic-point (bindu) tables for each of 7 grahas counted from each of 8 reference points (7 planets + Lagna) — stanzas 1-7 give the complete raw point-allocation rules per planet (this is exactly the "regular treatises" data). Also gives Trikona and Ekadhipatya reduction rules, Sarvashtakavarga (sum table, total always 337), and prediction-use rules (transits through high/low-bindu signs, timing of death/prosperity per house bindu counts, 10th/11th/12th house bindu comparison for career fortune, etc.).
**vargas.py docstring explicitly states Ashtakavarga is NOT_IMPLEMENTED** ("both need divisions this module does not compute, and a partial version... would be a number that looks authoritative and is not"). This chapter is the actual primary-source data needed to do it properly — a genuinely large feature (8 reference-point tables × 7 planets = the full classical dataset), not a quick addition. FLAG AS FUTURE PROJECT, cite Brihat Jataka ch.9 + note Parasara's Hora Sastra as the fuller source the translator repeatedly defers to.
Also mentions Parasara's Hora Sastra lists 32(!) distinct Ayurdaya (longevity) methods in 7 families — Brihat Jataka's ch.7 only covers the "most important" ones (Pindayurdaya + Satyacharya's + Jeevasarma's). Confirms BPHS as the deeper source for the full longevity system.

### Chapter X (Avocation/wealth-source) — pages 159-160+ (in progress)
Profession/wealth-source by planet (10th-house-from-Lagna-or-Moon occupant, or lord of Navamsa held by 10th lord): Sun→perfumes/gold/medicine/leadership; Moon→agriculture/water-trades/through women; Mars→metals/weapons/fire/boldness; Mercury→writing/accounting/handicraft; Jupiter→teaching/Brahmins/mining/virtue; Venus→gems/silver/cattle/luxury; Saturn→hard labor/menial/low-status work.
GOOD CANDIDATE to enrich app's existing "career"/"money" topics (topics.py) and knowledge.py's PLANETS[...]["careers"] (currently Western-flavored) — could add a parallel classical-Vedic career significator table cited to Brihat Jataka ch.10, without overwriting the existing Western one (app appears to deliberately keep Western delineation vocab separate from Vedic astro/ modules).

### Chapter XI (Raja Yoga) — pages 161-170
Mostly ultra-specific named-configuration yogas ("when Saturn occupies Aquarius AND Sun occupies Aries AND Moon occupies Taurus AND... rising sign is Aquarius, person becomes king") — essentially worked examples, not generalizable rules. LOW VALUE for encoding (too narrow/specific, app's existing generalized Raja Yoga logic in vargas.py, built from kendra/trikona lord association, is the better generalizable model already implemented). Skip most of this chapter's specific combos; general principle worth keeping: "3+ planets powerful in own/exaltation/moolatrikona houses => raja yoga (king if royal-born, rich if not); 5+ => raja yoga even from a low-born family" (stanza 13) — a graded-strength idea not currently in app, minor candidate.

### Chapter XII (Nabhasa Yogas) — pages 170-180+ (in progress)
**STRONG CANDIDATE, structural/positional yoga system, purely mechanical (no subjective "powerful" judgment calls needed for formation), with per-yoga effect text given.** 32 yogas in 4 families:
- Asraya yogas (3): Rajju (all planets in movable signs), Musala (all in fixed), Nala (all in common signs) — effects given (stanza 11): Rajju=jealous/wanders foreign lands; Musala=respectable & rich; Nala=defective organs but rich & skilled.
- Dala yogas (2): Srik (benefics in kendras), Sarpa (malefics in kendras) — Srik=comfort/luxury, Sarpa=miserable.
- Akriti yogas (20): shape patterns by which houses hold all 7 grahas — e.g. Gada (2 adjacent kendras), Sakata (1st+7th only), Vihaga (4th+10th only), Sringataka (1,5,9), Hala (2,6,10 or 3,7,11 or 4,8,12), Vajra (benefics in 1&7, malefics in 4&10), Yava (reverse), Kamala (all 4 kendras), Vapi (all 4 panaphara or all 4 apoklima), Yupa/Ishu/Sakti/Danda (planets confined to a specific consecutive 4-house span), Nau/Kuta/Chhatra/Chapa (confined to a 7-house span), Ardha-Chandra (7-house span starting from a panaphara/apoklima), Samudra (alternate houses 2,4,6,8,10,12), Chakra (alternate houses 1,3,5,7,9,11) — each has a short effect blurb (stanzas 13-15+, e.g. Vajra=lifelong happiness+bold fighter, Yava=powerful+happy in middle life, Kamala=renowned+accomplished, Vapi=miserly/hoards).
- Sankhya yogas (7): named purely by COUNT of signs occupied by all 7 planets (Vallaki=7 signs, Damini=6, Pasa=5, Kedara=4, Sula=3, Yuga=2, Gola=all in 1) — priority rule: if a configuration matches both a Sankhya yoga and an Akriti/Asraya/Dala yoga, the more specific one wins (stanza 10 note).
This is genuinely well-suited to vargas.py's existing engineering style (mechanical sign/house pattern-matching, like the Pancha Mahapurusha / Nabhasa-adjacent yogas already there) — cite as Brihat Jataka ch.12, cross-check against BPHS's own (largely identical) Nabhasa yoga chapter if implementing, since BPHS is app's primary citation source elsewhere. FLAG AS GOOD NEW-FEATURE CANDIDATE once reading is further along.

### Chapter XIII (Chandra/Lunar yogas) — pages 184-191
Adhi Yoga (benefics in 6/7/8th from Moon → minister/king), Sunapha/Anapha/Durudhura (planets 2nd/12th/both from Moon → self-made wealth/authority/pleasure), Kemadruma (none in 2nd/12th nor conjunct Moon → poverty despite birth) — **these yoga NAMES already appear in vargas.py (KEMADRUMA_* constants)**, likely already implemented; this chapter is a confirmation/citation source (Brihat Jataka ch.13), not new. Worth a citation add only, not new logic — should verify Sunapha/Anapha/Durudhura/Adhi Yoga are actually implemented too (not just Kemadruma) when I get to code.

### Chapter XIV (Double/multiple planetary conjunction yogas) — pages 191-200+ (in progress)
Sourced by the translator from **Jataka Parijata** (a different classical text). Exhaustive combinatorial list: every 2-planet conjunction (21 pairs), then 3-planet (35), 4-planet, etc., each with a short personality/outcome blurb, e.g. "Sun+Saturn: dull understanding, subject to enemies"; "Moon+Jupiter: protects pious men, very intelligent"; "Mercury+Venus: ruler over countries and men."
GOOD CANDIDATE for the 21 pairwise conjunctions specifically (a clean, bounded, encodable set) — would enrich app's generic ASPECTS["conjunction"] text in knowledge.py with per-pair classical flavor, cited Brihat Jataka ch.14 / Jataka Parijata. The 3+/4+/5+/6+-planet combinations are far less practically useful (rare in real charts, huge combinatorial list) — skip encoding those, note their existence only.

### Chapter XV (Pravrajya / ascetic yogas) — pages 204-206: 4+ planets conjunct in one sign → renunciation, ascetic-type keyed to strongest planet (Mars=Buddhist monk, Mercury=Jain, Jupiter=Brahmin ascetic, Moon=Kapalika/Shaiva, Venus=discus-bearer, Saturn=naked ascetic, Sun=forest hermit). Niche/rare configuration, low practical value for a consumer app (renunciation yoga is an edge case) — low priority, skip unless time allows.

### Chapter XVI (Moon by Nakshatra) — pages 206-210
**HIGH VALUE, DIRECTLY USABLE.** Personality delineation for birth-Moon in EACH of the 27 nakshatras (Aswini→fond of ornaments, popular; Bharani→truthful, able; Krittika→glutton, bright, famous; ... Revati→perfect limbs, deeply learned, rich). Clean, bounded (27 entries), classic "janma nakshatra" personality content — directly fills a gap, since knowledge.py has no nakshatra-level delineation at all currently (app's panchang.py likely computes nakshatra but doesn't interpret it). STRONG CANDIDATE.

### Chapter XVII (Moon by Rashi) — pages 210-213
**HIGH VALUE.** Personality/appearance delineation for Moon in each of 12 signs (Vedic/sidereal framing) — parallel to knowledge.py's existing (Western/tropical) MOON_SIGN dict. Should be added as a SEPARATE Vedic-specific table (e.g. in a new vedic_knowledge module or astro/knowledge.py), not merged into the Western one, since app deliberately keeps sidereal Jyotish (astro/) and tropical Western (interpret/knowledge.py) layers apart. STRONG CANDIDATE, cite Brihat Jataka ch.17.

### Chapter XVIII (Sun/Mars/Mercury/Jupiter/Venus/Saturn by Rashi, + Lagna by Rashi) — pages 213-220+ (in progress)
**HIGH VALUE, the big one.** Full classical planet-in-sign delineations for all 7 grahas × 12 signs (grouped by exaltation-sign pairs, e.g. "Mars in Aries or Scorpio..."), PLUS a separate detailed Lagna-by-rashi section (from Satyacharya's work) covering appearance, temperament, family relations, marriage type, and — again — manner of death (per Aries-lagna example: "death by weapons/poison/bile/fire/prison/fall"). This is the single richest, most generically-reusable delineation dataset in the book so far — directly parallels/extends knowledge.py's PLANETS+SIGNS dicts but in authentic Vedic/classical form. STRONG CANDIDATE — this alone justifies a new vedic-specific delineation module citing Brihat Jataka ch.18 (+ Satyacharya via ch.18 notes for Lagna specifically). Manner-of-death clauses embedded here again — per user's "include fully" decision, keep them, but they're a minor clause within an otherwise rich, generically useful personality/marriage/career description, not the focus like Ch.6-7 were.

### Chapter XVIII cont'd (Lagna by Rashi, Satyacharya's list) — pages 221-224: all 12 rising-sign delineations completed (appearance/temperament/family/career/manner-of-death per Lagna sign) — part of the same STRONG CANDIDATE dataset noted above.

### Chapter XIX (Moon/Lagna-by-sign × aspecting-planet) — pages 224-229
Combinatorial: for Moon (or Lagna) in each of 12 signs, aspected by each of 6 other planets → specific outcome (e.g. Moon in Leo aspected by Sun or Mars = king; aspected by Saturn = barber). ~70+ combos, plus parallel rules for Navamsa placements. Interesting but narrow/combinatorial and lower generalizability than Ch16-18's cleaner per-sign tables. MEDIUM priority, skip detailed encoding unless time allows — the underlying pattern (aspect modifies the base sign placement) is more a delineation-composition principle than new data.

### Chapter XX (Planets in the Bhavas/Houses) — pages 230-235
**VERY HIGH VALUE — possibly the single most directly usable chapter in the book.** Full classical delineation of each of 7 grahas placed in each of the 12 houses from Lagna (Sun in 1st/2nd/.../12th, Moon in 1st-12th, etc.), plus a general strength-grading rule (stanza 11): effects come to pass in full/3-quarters/half/quarter/less/fail proportion to whether the placed planet is exalted/moolatrikona/own-sign/friendly-sign/enemy-sign/debilitated — a clean, directly-codable weighting scheme that maps perfectly onto engine.py's existing DIGNITY_POINTS scoring pattern. STRONGEST CANDIDATE FOR ENCODING — directly extends engine.py's evidence-generation with per-house PLANET_IN_HOUSE text, Brihat Jataka ch.20, exactly the "specific, cited chart factor" style the engine's own docstring calls for.

### Chapter XXI (Planets in Vargas: Drekkana/Navamsa/Trimsamsa) — pages 235-240
Trimsamsa (D30, own-sign placement per planet) delineations, Drekkana-type effects (Sarpa/Ayudha/Chatushpad/Pakshi Drekkanas → wicked/torture/adultery/wandering), rising-Navamsa-by-sign personality (thief/king/hermaphrodite/slave etc. per Navamsa sign). MEDIUM value — Trimsamsa isn't in vargas.py's implemented list (D1,D3,D7,D9,D10,D12) nor its NOT_IMPLEMENTED note (worth checking); could be a modest future varga addition, but is its own small feature, not just a knowledge-text add. Note only, lower priority than Ch.20.

### Chapter XXII (Misc Yogas: Karaka-planet definitions) — pages 240+ (starting): mutually-exalted-and-in-kendra planets become "Karaka" (helper) to each other — a technical relationship concept, narrow use. LOW priority, skip.

### Chapter XXII cont'd (Karaka planets) — pages 241-243: mutual-exaltation/kendra "helper planet" relationships, dasa-timing-within-period rules by rising type (Sirodaya/Prishtodaya). Narrow/technical, low priority, noted only.

### Chapter XXIII (Malefic Yogas) — pages 243-249
Marriage/children denial, wife's death by fire/fall/rope, blindness/deafness/leprosy/idiocy/insanity/imprisonment predictions from specific combos. Same sensitive-content category as Balarishta (disability/affliction prediction, not just death) — user's "include fully" decision was framed around infant-death/lifespan specifically; disability-prediction is adjacent but distinct. Treating as covered by the same general decision (classical predictive astrology, faithfully sourced) unless told otherwise — noting it clearly here for visibility.

### Chapter XXIV (Horoscopy of Women / Stri Jataka) — pages 249-256
Chastity/fidelity judgments (Trimsamsa-lord based: "will become unchaste," "will commit adultery"), husband's traits from 7th house, widowhood timing. **DECISION (mine, not asked): declining to encode the chastity/moral-character-judgment rules** — these read as regressive/offensive by modern standards and are a distinct reputational risk from pure death/lifespan content (gendered morality judgments vs. astrological trait description). Will mention this choice to the user rather than ask, similar to skipping ch.3 animal horoscopy. The non-judgmental parts (husband's general temperament from 7th house lord, physique indicators) are lower-risk and could optionally be kept, but low priority anyway.

### Chapter XXV (Manner & Place of Death) — pages 256-260+ (in progress)
Extremely specific: exact cause of death (weapons/fire/drowning/prison/stones/spear/club/machine-caught/excrement/birds/lightning/falling-wall) keyed to precise multi-planet house combos; plus place-of-death-by-sign and pre-death-unconsciousness-duration formulas. This is the "manner of death" chapter the preface promised. Per user's broad "include fully" stance on death/longevity content, treating as in-scope, cited faithfully and factually (not sensationalized) if/when encoded — but this is a LARGE, highly combinatorial chapter; likely to summarize the general method (8th-house-lord/aspecting-planet → cause-of-death-by-planet-and-humor, per stanza 1's clean table) rather than enumerate every named multi-planet special case.

### Chapter XXV cont'd + Chapter XXVI (Lost/unknown-birth-time horoscope reconstruction via Prashna) — pages 261-274: Purely divinatory/computational methods for reconstructing an unknown birth time from a query moment (horary Lagna math, shadow-length calculations, name-syllable counting). Not applicable to the app (which has known accurate birth data) — SKIP, no encodable delineation content, just astronomical technique.

### Chapter XXVII (The 36 Drekkanas / Decans, D3) — pages 274-280+ (in progress)
Vivid mythic-figure imagery for each of the 36 decans (e.g. "1st Drekkana of Aries: a dark man with an axe, fearful appearance" ruled by Mars; "1st Drekkana of Virgo: a virgin girl carrying a flower-pot" ruled by Mercury) — the classical Decan-deity system (parallel to Western/Egyptian decan imagery). vargas.py already computes D3 (Drekkana) placements but likely only for yoga-lordship logic, not this descriptive imagery. MEDIUM-value flavor-text candidate — could enrich D3 output with per-decan character imagery, cited Brihat Jataka ch.27, but lower priority than the Ch16/17/18/20 core delineation tables.

### Chapter XXVII cont'd + Chapter XXVIII (Conclusion) — pages 281-286: remaining decans, then the author's own chapter-by-chapter summary (confirms 27 chapters, matches what we read) plus a listing of his companion work "Yoga Yatra" (muhurta/electional astrology — not covered in this book, different text, not available to us). Then Appendix (worked example of Lagna-longitude calculation, oblique-ascension tables, equation-of-time tables, culmination tables for building a sundial/star-clock) — pure 1885-era astronomical-observation methodology, superseded entirely by the app's existing Swiss-Ephemeris-based chart_service. No delineation content. Back matter (pages 296-305): Harvard Widener Library stamps, BookLab preservation note (1994), Google digitization stamps — confirms public-domain status conclusively.

## === BRIHAT JATAKA: COMPLETE (all 305 pages read) ===

### TOP CANDIDATES for encoding, ranked:
1. **Ch.20 (Planets in the 12 Houses)** — 7 grahas × 12 houses delineation + clean dignity-based strength-grading rule (full/3-4/half/quarter/less/fail by exaltation→moolatrikona→own→friendly→enemy→debilitated). Best fit with engine.py's existing evidence/scoring architecture.
2. **Ch.16-18 (Moon-by-Nakshatra, Moon-by-Rashi, 7-grahas-by-Rashi, Lagna-by-Rashi)** — the big generically-reusable Vedic delineation dataset, parallel to knowledge.py's Western tables but sidereal/classical. Largest single content block.
3. **Ch.12 (Nabhasa Yogas)** — 32 structurally-defined, mechanically-computable yogas with effect text. Good engineering fit (positional pattern-matching, like existing Pancha Mahapurusha logic).
4. **Ch.10 (Avocation)** — classical career/wealth-source-by-planet table, enriches career/money topics.
5. **Ch.8 stanzas 12-18 (Mahadasha effects per planet)** — benefic/malefic dasha-period text per graha, fills a real gap (remedies.py computes active mahadasha lord but has no effect-text).
6. **Ch.14 (21 two-planet conjunction yogas)** — bounded, enriches generic ASPECTS["conjunction"] with per-pair classical color.
7. **Ch.9 (Ashtakavarga)** — the full classical benefic-point tables; large future-feature scope (app currently deliberately NOT_IMPLEMENTED), not a quick add.
8. **Ch.27 (36 Drekkana/decan images)** — descriptive flavor text for D3, medium priority.
9. **Ch.6 Balarishta + Ch.7 Ayurdaya + Ch.25 manner/place of death** — per user's explicit "include fully" decision; faithful, factually-framed encoding when reached.

### Content deliberately excluded (my judgment, flagging for user):
- Ch.3 (animal/vegetable horoscopy) — not applicable to human consultations.
- Ch.24 (Stri Jataka) chastity/fidelity/adultery judgments — declined as regressive gendered content, distinct from the death/longevity content the user already approved. Will mention this choice explicitly when reporting back.
- Ch.26 (lost-horoscope reconstruction via Prashna) — pure horary-astrology technique, not applicable (app has exact birth data).

## NEXT: Bhrigu Samhita (Hindi), 638 pages, 32 chunks in C:\ocrtools\ocr_text\bhrigu_samhita\ — not yet started.
