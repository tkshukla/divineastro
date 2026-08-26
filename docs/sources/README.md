# Classical source notes

Working notes from a full read-through of two classical Jyotish texts, kept
here so the citations in `app/astro/` (and future work on the same sources)
have a paper trail back to where a rule came from.

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
  in a way that implies it's been redistributed.

Both notes flag two categories that were deliberately left out of the app:
women's-horoscopy chastity/widowhood/adultery judgments (regressive by modern
standards, a different kind of risk than plain delineation), and ultra-specific
named Raja Yoga combinations (too narrow to generalize — the app's existing
kendra/trikona-lord-based Raja Yoga logic in `app/astro/vargas.py` is the
better model). Balarishta (infant-death yogas) and Ayurdaya (lifespan
calculation) content is in scope per an explicit product decision to include
it faithfully and factually, without alarmist framing.

See `app/astro/nabhasa.py` and `app/astro/delineation.py` for what has actually
been encoded from these notes so far, and each module's own docstring/citations
for the specific chapter/stanza a rule traces to.
