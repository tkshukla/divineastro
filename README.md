# Astro

A fully local astrological analysis workbench. Enter a birth date, time and
place; get a computed chart and a chat interface that answers questions about it
using the actual chart rather than generic sun-sign text.

**The astrology is never done by a language model.** The chart is computed from
the Swiss Ephemeris, and a deterministic rule engine gathers the evidence and
reaches the verdict. Ephemeris data ships with the library and the city database
is a bundled GeoNames dump, so all of that runs locally with no API key.

A model is used for one thing only: re-expressing the finished analysis as
readable prose, and translating it. It is given the evidence and forbidden from
adding, dropping or altering a single placement or date — every claim in the
polished text traces back to an evidence item you can inspect under "the
reasoning". Set `ANTHROPIC_API_KEY` to enable it; leave it unset and the engine
answers in its own words, offline.

---

## Running it

```bash
cd C:\Astro; .\run.ps1
```

That starts the server on <http://127.0.0.1:8600> and opens a browser. First run
takes ~2 seconds longer while the city index is built and cached.

To set it up on a fresh machine:

```bash
python -m venv .venv; .\.venv\Scripts\python.exe -m pip install -r requirements.txt; .\.venv\Scripts\python.exe tools\fetch_data.py
```

Run the test sweep:

```bash
.\.venv\Scripts\python.exe -m tests.test_sweep
```

---

## What computes what

Everything astronomical comes from **[`stellium`](https://pypi.org/project/stellium/)**
(v0.22), which wraps the Swiss Ephemeris. This project does not reimplement any
of it. Specifically, `stellium` supplies:

| Layer | Source |
|---|---|
| Planetary positions, speeds, declinations, phases | Swiss Ephemeris via `stellium` |
| House cusps (Placidus, Whole Sign, Porphyry) | `stellium.engines.houses` |
| Aspects with orb and applying/separating | `stellium` aspect + orb engines |
| Essential & accidental dignity, mutual reception | `stellium.components.DignityComponent` |
| Sect, aspect patterns, Arabic Parts | `stellium` analysers and components |
| Annual profections, zodiacal releasing, firdaria | `stellium.engines` time-lord engines |
| Solar returns | `stellium.ReturnBuilder` |
| Chart wheel SVG | `stellium` visualisation (`midnight` theme) |

Three things are layered on top, in `app/chart_service.py`:

- **Transit-to-natal contacts** are computed here rather than reused from the
  natal aspect engine, so the orbs are transit-appropriate (1.5° for personal
  planets, 2° for slow ones, 3° for the Moon) and applying/separating is judged
  from the transiting body's own motion against a fixed natal point.
- **Vimshottari dasha** (sidereal charts only) — the 120-year period arithmetic,
  driven by the sidereal Moon longitude that `stellium` provides.
- **Polar-latitude handling** — above 66° latitude Placidus cusps are
  mathematically undefined, so the app falls back to Whole Sign + Porphyry and
  says so in the reading.

---

## How an answer is produced

`app/interpret/` is a deterministic pipeline, not a language model.

1. **Route** (`topics.py`) — the question is matched to one of 13 topics
   (career, money, love, family, children, health, education, travel,
   spirituality, friends, obstacles, self, timing) and one of four intents
   (`describe`, `forecast`, `timing`, `advice`). Each topic declares its
   primary houses, supporting houses and natural significators.

2. **Gather evidence** (`engine.py`) — for those houses the engine reads the
   sign on the cusp, the condition of its ruler, its occupants, the natural
   significators, and the strongest aspects touching any of them. Each becomes
   an `Evidence` item carrying a sentence, a signed score and the exact
   placement it came from.

3. **Score** — planetary condition is scored traditionally: essential dignity,
   angularity, solar phase (combustion / cazimi / under the beams), retrograde
   motion, sect status, and aspects from benefics and malefics. Evidence is
   combined as a weighted mean and normalised to −1 … +1.

4. **Time it** — for timing and forecast questions the engine adds annual
   profections, zodiacal releasing, firdaria, Vimshottari (sidereal), transits
   in force now, and a monthly walk of the next four years to find windows when
   a slow planet contacts the topic's ruler, cusp or significator. It also
   flags **Zodiacal Releasing peaks and loosings of the bond**, and the
   **monthly profections** that land on the topic's houses — the annual
   profection sets a year's theme, but the monthly is what dates an event
   inside it.

   Questions can name their own moment — *"in 2012"*, *"March 2015"*, *"when I
   was 25"*, *"three years ago"*. The engine then re-centres the whole timing
   search on that date and reads **backwards**, which is how you check the
   technique against events you already lived through.

5. **Compose** — the answer is assembled from the evidence. Every claim is
   backed by an evidence item, and the full weighted factor list is visible
   under *the reasoning* in each reply.

The delineation vocabulary lives in `interpret/knowledge.py` as reusable
ingredients (a planet's verb, a sign's style, a house's field) which are
composed into sentences — so the wording follows the actual placement rather
than being pre-written per combination.

---

## Language

A toggle at the top right switches between **English** and **हिन्दी**. The UI
chrome, chart panels, planet/sign/house names (सूर्य, चंद्र, मंगल… / मेष, वृषभ…)
and the suggested questions are translated offline, with no model involved.

The *analysis narrative* is a different matter: it is composed from an English
delineation vocabulary, so translating it needs the narration layer below. With
narration off, the panels and chrome are Hindi and the reading itself stays
English.

## Narration (optional LLM)

The astrology is never done by a model. The engine computes the chart, gathers
the evidence and reaches the verdict; the LLM is only allowed to **re-express
that finished analysis** — as better prose, and in Hindi. It is handed the
evidence list and instructed that it may not add, drop, or alter any placement,
degree, date or verdict. Every answer keeps the engine's original wording in a
collapsible *"The engine's own wording"* block, so you can diff the two.

If the model fails, times out, or returns too little text, the engine's reading
is shown instead — narration can degrade the prose, never the analysis.

| Provider | Where it runs | Notes |
|---|---|---|
| **Off** (default) | — | Rule-engine wording. Instant, fully offline, most literal. |
| **Local — `<model>`** | Ollama on this machine | Every installed chat model is listed. Nothing leaves the computer. |
| **Claude** | Anthropic's API | Best prose, by far the best Hindi. **This is the only option that sends your chart off the machine.** Needs `ANTHROPIC_API_KEY` or `ant auth login`. |

Answers stream token by token — the engine's verdict lands immediately and the
rewrite arrives over the top of it, which matters because local CPU inference is
slow. Measured on this machine (llama3 8B, `size_vram: 0` — no GPU offload,
~3.6 tokens/sec, under some CPU contention):

| Provider | First token | Full answer |
|---|---|---|
| Off (engine) | — | instant |
| Local llama3 8B, English | ~200s | ~300s |
| Local llama3 8B, Hindi | ~70s | ~300s |

Local output is capped at roughly 250 words for that reason; a full-length
rewrite would take far longer. On a GPU box these numbers collapse.

**Measured caveat on local models:** small Llama-family models transliterate
rather than translate Devanagari and leak CJK tokens mid-sentence — `llama3:8b`
produced *"लिब्रह"* for Libra and *"सामाजिक 流नसके"*. The provider picker flags
which installed models are weak at Hindi. For usable local Hindi, pull a
multilingual model (`ollama pull qwen2.5:7b` or `gemma2:9b`); for good Hindi,
use Claude.

Environment overrides: `ASTRO_OLLAMA_URL`, `ASTRO_OLLAMA_MODEL`, `ASTRO_CLAUDE_MODEL`.

## Layout

```
app/
  main.py             FastAPI app + JSON API
  chart_service.py    stellium wrappers, normalisation, transits, dashas
  geo.py              offline city search + timezone resolution
  interpret/
    topics.py         question -> topic + intent routing
    knowledge.py      delineation vocabulary
    engine.py         evidence gathering, scoring, composition
  static/             the UI (no frameworks, no CDN)
data/                 GeoNames dumps + cached index
tools/fetch_data.py   one-time geodata download
tests/test_sweep.py   880-check robustness sweep
```

### API

| Endpoint | Purpose |
|---|---|
| `GET /api/places?q=` | offline city autocomplete |
| `POST /api/chart` | build a chart, returns bundle + wheel SVG + current time-lords |
| `POST /api/ask` | ask a question against a chart session |
| `POST /api/ask/stream` | same, as SSE — engine verdict first, then streamed narration |
| `GET /api/llm` | which narration providers are installed and usable |
| `GET /api/transits/{sid}` | current transits and time-lord snapshot |
| `GET /api/solar-return/{sid}?year=` | solar return summary |
| `GET /api/report/{sid}` | the chart as `stellium`'s own prompt text |
| `DELETE /api/session/{sid}` | forget a chart |

Birth data is held in process memory only and is never written to disk.

---

## Accuracy notes

- Birth times are localised with the IANA zone for the birthplace, so historical
  DST and offset changes are applied correctly (verified against London 1955
  BST, Kathmandu +5:45, and pre-war Berlin in the test sweep).
- Sidereal mode supports Lahiri, Raman, Krishnamurti and Fagan–Bradley ayanamsas.
- Where the time of birth is unknown, houses and angles are unreliable; the app
  uses noon and flags it. Sign-level and aspect judgements remain valid.
- Health output is symbolic pattern-reading and is labelled as such. It is not
  diagnosis.

## Licence

This project is licensed under the **GNU Affero General Public License v3.0** —
see [LICENSE](LICENSE).

AGPL is not a choice made for its own sake. The chart engine uses `stellium`,
which is AGPLv3+, so the combined work inherits it. Section 13 is the clause
that matters here: running the software as a network service counts as
conveying it, which means anyone who uses the hosted site is entitled to its
source. That is what this repository is for, and it is linked from the Terms
page via `ASTRO_SOURCE_URL`.

`stellium` bundles Swiss Ephemeris, itself dual-licensed (AGPL or commercial).
GeoNames data is CC BY 4.0.
