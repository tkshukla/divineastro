# Ravana Samhita (5-volume compilation) — survey notes

A modern Hindi compilation in five volumes, presented under the name "Ravana
Samhita" but — like the Bhrigu Samhita source above — authored/compiled in the
20th/21st century (the closing colophon of the tantra-mantra chapter names a
contemporary editor, "Maithili Acharya Shivakant Jha"). **Likely still under
copyright.** As with the Bhrigu Samhita source, nothing from this set is or
should be quoted/translated verbatim; only independently-phrased facts are
extracted, cited generically as "a traditional compilation," never naming the
specific edition.

## What's actually in the five volumes

A contents-page survey of all five volumes, followed by a full read of Volume
4, found this is **not** primarily a jyotish (birth-chart astrology) text:

| Volume | Content | Decision |
|---|---|---|
| 1–2 | Tantra-mantra sadhana: predominantly *vashikaran* (subjugation), *maran/uchchatan/vidveshan* (curse/eviction/enmity-creation) rituals targeting named third parties, plus folk business/wealth charms and a Navagraha yantra-mantra section | **Excluded** except the Navagraha section (see below) |
| 3 | Ayurvedic/herbal medicine, unrelated to astrology | Excluded (out of scope) |
| 4 | Arishta (affliction) timing and multi-planet yoga combinations | Read in full — see below |
| 5 | Shiva-puja ritual worship, unrelated to astrology or its prediction engine | Excluded (out of scope) |

### Firm exclusion: shatkarma tantra

Volumes 1–2's *vashikaran/maran/uchchatan/vidveshan/stambhan/mohan* material
(the six classical tantric acts aimed at subjugating, cursing, evicting, or
manipulating a named real person, or at binding/harming a named rival's
business) is excluded categorically, independent of any user preference — this
is coercive-control and harm-intent content, the same class of thing as
stalking/manipulation instructions from any other source. It was skipped
entirely rather than paraphrased.

### Extracted: Navagraha yantra-mantra section (Vol. 2, printed pp. 162–178)

This section is ordinary classical graha-shanti (planetary pacification)
material — for each of the 9 grahas: a Puranic pranam verse, a Vedic mantra, a
tantric bija mantra, a Graha Gayatri, a prescribed japa (recitation) count for
a full siddhi (with a larger count "classically observed in Kali Yuga"), and a
herb-root substitute for when the prescribed gemstone can't be worn. This
overlaps with (and extends) what `app/astro/remedies.py` already encoded from
general classical practice — the bija mantras there already match this
source's tantric mantras almost verbatim, confirming they're standard,
attributable-to-tradition text rather than anything original to this
compilation.

**Encoded:** the japa counts, the Graha Gayatri mantras (8 of 9 — Saturn's page
was not legibly recoverable via OCR and was left out rather than guessed), and
the herb-root gemstone substitutes. See `JAPA_COUNT`, `GRAHA_GAYATRI`, and
`GRAHA_HERB` in `app/astro/remedies.py`.

**Not encoded:** the section's yantra-construction instructions (numerological
square diagrams — not text-representable in this app), and the granular
per-planet charity-item lists (already adequately covered by the existing
`CHARITIES` dict; the marginal gain from re-deriving it via OCR wasn't worth
the transcription-error risk).

**Also skipped from the same page range:** several business-charm mantras
printed immediately before the Navagraha section (pp. 108–112 of the scanned
PDF) — most are harmless folk prosperity charms, but at least one is an
explicit *vidveshan* (enmity-creation between two named people) mantra, so the
whole preceding block was left out rather than partially picked through.

## Volume 4 (Arishta timing / multi-planet yogas) — full read

Read in full per an explicit decision to check it for anything genuinely new
beyond what the Brihat Jataka and Bhrigu Samhita sources already provided.
Most of it substantially overlaps with material already covered or already
excluded on the same grounds as the first two sources:

| Section | Verdict |
|---|---|
| Kalapurusha/rashi basics, graha dignities, friendships, exaltation degrees | Already covered by `app/astro/vargas.py` / `app/astro/matching.py` |
| Planet-in-house results (7 planets × 12 houses) | Already covered by `PLANET_HOUSE_TEXT` in `delineation.py` (from Brihat Jataka) |
| Two-planet conjunction results | Already covered by `CONJUNCTION_DELINEATION` in `delineation.py` |
| 2-to-7-planet combinatorial "sitting together" yogas | Excluded — an extremely large, mechanical combinatorial table, not the kind of generalizable rule this engine encodes elsewhere |
| ~80 named Raja Yoga combinations, and a matching list of named affliction/misfortune yogas (some framed around caste/social status) | Excluded, same reasoning as both earlier sources: too narrow to generalize, and the caste-framed ones carry the same kind of risk as the chastity/widowhood material already excluded |
| Balarishta/Arishta timing at various ages | Already covered by the Brihat Jataka's own Balarishta/Ayurdaya material |
| Pancha Mahapurusha yoga definitions | Already implemented in `vargas.py` |

Two sections had something genuinely new and in scope:

- **Baladi Avastha** — a planet's five-fold "life stage" (Bala/infant,
  Kumara/growing, Yuva/mature, Vriddha/aged, Mrita/dead) within its own
  sign's 30°, read in one direction for odd signs and the reverse for even
  signs. A standard, unambiguous classical rule, not particular to this
  compilation. **Encoded** as `baladi_avastha()` in `app/astro/delineation.py`
  and folded into `delineate()`'s per-planet output.
- **Vimshottari Antardasha (sub-period) result texts**, one fixed reading per
  graha (distinct from the benefic/malefic-conditioned Mahadasha texts
  already encoded from the Brihat Jataka) covering all nine grahas including
  Rahu/Ketu. **Encoded** as `ANTARDASHA_EFFECTS` / `antardasha_reading()` in
  `app/astro/delineation.py`, surfaced in chat via `_vedic_context()` and in
  the Kundali PDF alongside the existing Mahadasha reading.

One more thing was found and, after a follow-up request, built as its own
dedicated task:

- **Yogini Dasha** — a complete alternate 8-fold dasha system (nakshatra-based
  starting lord, 1–8 year periods per lord totalling a 36-year cycle, its own
  antardasha subdivision, and per-dasha result texts). **Encoded** as
  `chart_service.yogini_dasha()` (the date arithmetic — mirrors
  `vimshottari()`'s shape) and `delineation.YOGINI_EFFECTS` /
  `yogini_dasha_reading()` (the eight result texts). Surfaced alongside
  Vimshottari, not in place of it, in chat (`_vedic_context()`), the Kundali
  PDF's dasha summary, and the PDF's narrative facts. The starting-Yogini
  rule ((birth nakshatra number + 3) mod 8) is this source's own stated
  method — other traditions state it differently, and this is not asserted
  as the one universal rule. Sankata, the 8-year eighth dasha, is Rahu's for
  its first half and Ketu's for its second, per the source's own note; that
  split is applied only at the mahadasha timescale; a Sankata antardasha
  (much shorter) is reported under the combined label "Rahu/Ketu" rather
  than guessing a finer split the source doesn't describe. See
  `tests/test_yogini_dasha.py` for the full test coverage, including exact
  date arithmetic checked against stubbed sessions.

One more thing was found and deliberately **not** encoded:

- **Sattva/Rajas/Tamas (guna) temperament** — the source ties a native's basic
  temperament to whichever of the three gunas was "dominant" among the grahas
  at birth, but does not spell out a precise, computable rule for what makes
  one graha's guna dominant over another's at a given moment. Rather than
  guess at a computation the source itself doesn't pin down, this was left
  unimplemented.
