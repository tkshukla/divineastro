# Classical source notes

Working notes from a full read-through of three classical Jyotish sources,
kept here so the citations in `app/astro/` (and future work on the same
sources) have a paper trail back to where a rule came from.

- **`brihat_jataka_notes.md`** — Varaha Mihira's *Brihat Jataka*, translated by
  N. Chidambaram Iyer (Madras, 1885). Public domain (Harvard Widener Library /
  Google Books scan). Chapter-by-chapter notes with page references; candidate
  rules are ranked by how directly they fit the app's existing engineering
  style (cited, mechanical, generalizable).
- **`bhrigu_samhita_notes.md`** — a modern (1975) Hindi compilation, *Bhrigu
  Samhita Phalit-Prakash* (Dehati Pustak Bhandar, Delhi), presented under Sage
  Bhrigu's name but authored by a 20th-century compiler. **Likely still under
  copyright** — nothing from this source is or should be reproduced verbatim
  anywhere in the codebase; only independently-phrased facts/rules, cited
  generically as "a traditional Bhrigu-school compilation," never quoting or
  translating its Hindi prose directly, and never naming this specific edition
  in a way that implies it's been redistributed. Its ~1300-entry per-Lagna
  planet-in-house corpus (`app/astro/delineation.py`'s `BHRIGU_LAGNA_HOUSE_TEXT`)
  is now **complete for all twelve Lagnas** — Aries (Mesha) through Pisces
  (Meena) — 1,293 of 1,296 possible entries, with three genuine documented
  scan-page gaps (Aries/Jupiter 8th-10th houses, Taurus/Jupiter 3rd house,
  Pisces/Ketu 2nd-4th houses) and one documented internal source
  contradiction left unresolved rather than guessed (Taurus's Jupiter 3rd
  house). See the notes file for the full per-Lagna breakdown, including
  the recurring cross-Lagna patterns (a habit of calling Mercury "friend"
  to planets the standard table calls neutral or enemy; occasional
  Guru/Budh body-text mixups resolved via section headers or fixed
  rulership facts) and every confirmed exaltation/debilitation placement.

- **`ravana_samhita_notes.md`** — a modern compilation presented as "Ravana
  Samhita" (5 volumes; likely still under copyright, same handling as the
  Bhrigu source). Mostly tantra/curse ritual, Ayurveda, and Shiva-puja
  content, out of scope or firmly excluded (see the notes for the full
  breakdown); Volume 4 was read in full for "anything genuinely new" and
  contributed Baladi Avastha and Vimshottari Antardasha result texts to
  `app/astro/delineation.py`, plus a full second dasha system — Yogini
  Dasha — in `app/chart_service.py` (the arithmetic) and
  `app/astro/delineation.py` (the result texts).

Both Brihat Jataka and Bhrigu Samhita notes flag two categories that were deliberately left out of the app:
women's-horoscopy chastity/widowhood/adultery judgments (regressive by modern
standards, a different kind of risk than plain delineation), and ultra-specific
named Raja Yoga combinations (too narrow to generalize — the app's existing
kendra/trikona-lord-based Raja Yoga logic in `app/astro/vargas.py` is the
better model). Balarishta (infant-death yogas) and Ayurdaya (lifespan
calculation) content is in scope per an explicit product decision to include
it faithfully and factually, without alarmist framing.

See `app/astro/vargas.py` (Nabhasa yogas and the rest of the classical yoga
families) and `app/astro/delineation.py` (dignity/house/career/conjunction/
dasha/avastha text) for what has actually been encoded from these notes so
far, and each module's own docstring/citations for the specific chapter/
stanza a rule traces to.
