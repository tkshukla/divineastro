"""Optional LLM layer.

The astrology is **not** done by the model. The deterministic engine computes the
chart, gathers the evidence and reaches the verdict; the LLM is only allowed to
*re-express* that finished analysis — as fluent prose, and in Hindi when asked.
It is given the evidence and told, in the strongest terms the prompt can manage,
that it may not add, drop or alter a single placement.

That split is the point: turning the narration over to a model while keeping the
judgement deterministic means the answer can read better without becoming less
verifiable. Every claim in the polished text still traces back to an evidence
item you can inspect under "the reasoning".

Two providers, both optional:

  ollama     — fully local (default when the daemon is running). Nothing leaves
               the machine, which preserves the app's original guarantee.
  anthropic  — Claude, when ANTHROPIC_API_KEY (or an `ant auth login` profile)
               is present. Better prose, and markedly better Hindi. Sends the
               chart analysis to Anthropic's API.
"""

from __future__ import annotations

import json
import logging
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass

log = logging.getLogger("astro.llm")

OLLAMA_URL = os.environ.get("ASTRO_OLLAMA_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.environ.get("ASTRO_OLLAMA_MODEL", "llama3:latest")
# Haiku, not Opus. This layer does not do the astrology — the engine has already
# calculated and judged the chart, and every fact is handed to the model in the
# prompt. The remaining job is restructuring supplied facts into plain language,
# which the small model does well. Opus costs roughly an order of magnitude more
# per answer for work that is not reasoning-bound. Set ASTRO_CLAUDE_MODEL to
# claude-sonnet-5 if a quality comparison justifies it.
CLAUDE_MODEL = os.environ.get("ASTRO_CLAUDE_MODEL", "claude-haiku-4-5-20251001")

# The prompt asks for about 150 words. Devanagari costs noticeably more tokens
# per word than Latin script, so Hindi needs the headroom; 8000 was far past any
# answer this app produces and only served to make a runaway response expensive.
CLAUDE_MAX_TOKENS = int(os.environ.get("ASTRO_CLAUDE_MAX_TOKENS", "2000"))

# The report generators ask for roughly 950 words of JSON across three sections.
# That does not fit in 2000 tokens: the response is cut off mid-object, the
# json.loads below raises, and the caller quietly prints the canned fallback
# instead — the failure looks exactly like a working PDF. Devanagari runs about
# two and a half times the tokens of the same text in Latin script, so Hindi
# needs proportionally more. Haiku's ceiling is far above both.
REPORT_MAX_TOKENS_EN = int(os.environ.get("ASTRO_REPORT_MAX_TOKENS_EN", "4000"))
REPORT_MAX_TOKENS_HI = int(os.environ.get("ASTRO_REPORT_MAX_TOKENS_HI", "12000"))


def _report_max_tokens(language: str) -> int:
    return REPORT_MAX_TOKENS_HI if language == "hi" else REPORT_MAX_TOKENS_EN


LANGUAGES = {
    "en": "English",
    "hi": "Hindi (हिन्दी, in Devanagari script)",
}

SYSTEM_PROMPT = """You are the writing layer of an astrology application. You are \
NOT the astrologer — the chart has already been calculated and judged by a \
deterministic engine using the Swiss Ephemeris and traditional rules.

Your job is to ANSWER THE PERSON'S QUESTION in {language}, using the engine's \
analysis as your evidence. You are writing for someone who wants a premium, highly \
detailed, and thorough reading (similar to a professional consultation or reports on \
Astrosage).

The engine's raw analysis reads like a technical reference: dignities, orbs, \
zodiacal releasing, firdaria, profections. That is source material for you, not \
a template to reproduce. Translate this technical data into a cohesive, insightful, \
and comprehensive analysis in plain language.

BE DETAILED, COMPREHENSIVE, AND SPECIFIC. Do not summarize or limit your answer to a \
few sentences. Provide a thorough, multi-paragraph explanation (aim for roughly 300 to \
500 words) that covers:
1. A direct, clear answer to the user's question in the opening paragraph.
2. In-depth analysis of the active birth chart indicators, explaining how the planetary \
dignities, placements, house ruler connections, and aspects shape the situation.
3. Detailed timing predictions. Explain the running Vimshottari mahadasha/antardasha with \
their dates, active transits, annual/monthly profections, and releasing peaks/loosings of \
the bond. Lay out a clear chronological sequence of windows and turning points.
4. Actionable advice and remedies/guidance based on the chart's strengths and challenges.

Maintain a warm, wise, encouraging, and authoritative tone. Use paragraph breaks and \
markdown styling (such as bolding key terms, planets, yogas, or dates) to make the text \
visually clean and easy to scan. Do not use markdown headings (like # or ##) or bulleted/numbered lists.

Absolute rules — breaking any of these makes the output worthless:
1. Never add an astrological fact that is not in the source. No placement, \
   aspect, degree, house, dasha or date that you were not given.
2. Never change a fact. If you cite a placement, sign, degree, house, date or \
   period, it must match the source exactly. You MAY omit detail — leaving out \
   an orb or a minor transit is expected — but you may never alter one.
2a. EVERY YEAR AND MONTH YOU WRITE MUST APPEAR VERBATIM IN THE EVIDENCE. Do no \
   arithmetic on dates: never split a long period into a midpoint, never say \
   "the next few years" as a number, never average two dates, never estimate \
   when something "peaks" inside a range you were given. If the evidence says a \
   period runs Jul 2026 to Jul 2045, the only two years you may print are 2026 \
   and 2045.
3. Never drop the verdict or reverse its polarity. If the source says an area is \
   challenged, your version says so too, in plain words.
4. Never invent certainty. Keep the source's hedging. This is a reading of \
   conditions and tendencies, not a prediction of fact.
5. Never pad with empty generic filler. Always tie statements directly back to the \
   specific placements and timing details in the evidence.

{language_note}

LAST AND MOST IMPORTANT: If a conversational history is provided, pay close attention \
to previous questions and answers. Treat this question as a continuation of the dialogue, \
answering follow-up questions in context while maintaining consistency with previous answers."""

HINDI_NOTE = """Write the entire response in Hindi using Devanagari script. Use \
the standard Sanskrit/Vedic names for planets, signs and houses — सूर्य, चंद्र, \
मंगल, बुध, गुरु, शुक्र, शनि, राहु, केतु; मेष, वृषभ, मिथुन, कर्क, सिंह, कन्या, तुला, \
वृश्चिक, धनु, मकर, कुम्भ, मीन; भाव for house, दशा for dasha. Keep degrees in \
numerals (8°02'). Technical English terms with no natural Hindi equivalent may \
stay in English inside brackets.

The evidence you are given names signs in English. TRANSLATE them using exactly \
this table — never spell an English sign name out in Devanagari letters:

    Aries=मेष  Taurus=वृषभ  Gemini=मिथुन  Cancer=कर्क  Leo=सिंह  Virgo=कन्या
    Libra=तुला  Scorpio=वृश्चिक  Sagittarius=धनु  Capricorn=मकर
    Aquarius=कुम्भ  Pisces=मीन

"कपिकर्न", "एक्वेरियस", "सैजिटेरियस" and the like are wrong and look illiterate \
to an Indian reader. Capricorn is मकर. If you are ever unsure of a term, keep \
the English word in Latin script in brackets rather than inventing a spelling."""

ENGLISH_NOTE = "Write in clear, natural English."


@dataclass
class Provider:
    key: str
    label: str
    detail: str
    local: bool
    available: bool
    hindi_ok: bool = True


def _ollama_models() -> list[str]:
    try:
        with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=2) as resp:
            data = json.loads(resp.read())
        return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []


def _anthropic_ready() -> bool:
    if os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"):
        return True
    # An `ant auth login` profile also authenticates the SDK with no env var.
    profile = os.path.expanduser("~/.config/anthropic/credentials")
    return os.path.isdir(profile) and bool(os.listdir(profile))


# Small local models vary enormously at Devanagari. Llama-family 8B models
# transliterate rather than translate and leak CJK tokens mid-sentence; the
# Qwen and Gemma families are markedly better. Flagging this in the picker is
# more useful than silently producing garbled Hindi.
GOOD_AT_HINDI = ("qwen", "gemma", "aya", "mistral-nemo", "command-r")
CODE_MODEL = ("coder", "codellama", "deepseek-coder", "starcoder", "codegemma")


def _model_note(name: str) -> tuple[str, bool]:
    """Return (caveat, good_at_hindi) for an installed Ollama model."""
    lower = name.lower()
    if any(tag in lower for tag in CODE_MODEL):
        return "Tuned for code — prose will be weak.", False
    if any(tag in lower for tag in GOOD_AT_HINDI):
        return "Good multilingual support; the better choice for Hindi.", True
    return "Weak at Devanagari — expect garbled Hindi. Fine for English.", False


def default_provider() -> str:
    """What a visitor who has never touched the narration picker should get.

    Claude when it is configured, the rule engine otherwise. Local models are
    never chosen automatically: they take minutes per answer on CPU, so opting
    into that has to be a deliberate act rather than a surprise.
    """
    return "anthropic" if _anthropic_ready() else "off"


def providers() -> list[Provider]:
    out = [Provider(
        key="off", label="Off (deterministic)", local=True, available=True,
        detail="Rule-engine wording only. Instant, fully offline, most literal.",
    )]

    # Embedding models are installed alongside chat models but cannot generate.
    models = [m for m in _ollama_models() if "embed" not in m.lower()]
    if not models:
        out.append(Provider(
            key="ollama", label="Local (Ollama)", local=True, available=False,
            detail="Ollama is not running. Start it, then `ollama pull qwen2.5:7b`.",
        ))
    for name in models:
        note, hindi_ok = _model_note(name)
        out.append(Provider(
            key=f"ollama:{name}", label=f"Local — {name}", local=True, available=True,
            hindi_ok=hindi_ok,
            detail=f"Runs on this machine, nothing leaves it. {note} "
                   f"Expect minutes per answer on CPU.",
        ))

    out.append(Provider(
        key="anthropic", label="Claude (Anthropic)", local=False,
        available=_anthropic_ready(),
        detail=("Fast, and by far the best Hindi. Sends the chart analysis to "
                "Anthropic's API — the only option here that leaves your machine."
                if _anthropic_ready() else
                "Set ANTHROPIC_API_KEY (or run `ant auth login`) to enable."),
    ))
    return out


def _split(provider: str) -> tuple[str, str]:
    """'ollama:qwen2.5:7b' -> ('ollama', 'qwen2.5:7b')."""
    if provider.startswith("ollama:"):
        return "ollama", provider.split(":", 1)[1]
    return provider, OLLAMA_MODEL


_DIV_SIGNIFIES = {
    "D3": "siblings, initiative and courage",
    "D7": "children and progeny",
    "D9": "marriage, relationships and core planetary strength",
    "D10": "career, standing, reputation and public role",
    "D12": "parents and ancestry"
}


def _vedic_block(vedic: dict) -> str:
    """The classical apparatus, when the engine could compute it.

    Readers of an Indian astrology product expect the Navamsa and the named
    yogas — an answer that never mentions them reads as a Western horoscope
    with Sanskrit words sprinkled on. Only what actually formed is listed, so
    the model has nothing to invent from.
    """
    if not vedic:
        return ""

    lines = []
    
    divs = vedic.get("divisional_charts") or {}
    for dk in ["D9", "D10", "D3", "D7", "D12"]:
        d_info = divs.get(dk)
        if d_info:
            pls_str = ", ".join(f"{p}: {val}" for p, val in d_info.get("placements", {}).items())
            sig = _DIV_SIGNIFIES.get(dk, "")
            lines.append(
                f"- Divisional {d_info['name']} ({dk}) [signifies {sig}]: "
                f"Lagna in {d_info['lagna']}. Placements: {pls_str}"
            )

    for y in vedic.get("yogas") or []:
        lines.append(f"- Yoga formed — {y['name']}: {y.get('note', '')}")
    if vedic.get("vargottama"):
        lines.append(f"- Vargottama planets: {', '.join(vedic['vargottama'])}")
    ss = vedic.get("sade_sati")
    if ss:
        lines.append(f"- Sade Sati: {ss.get('phase', 'running')} "
                     f"({ss.get('starts', '')[:10]} to {ss.get('ends', '')[:10]})")

    dignities = vedic.get("dignities") or {}
    for name, d in dignities.items():
        lines.append(
            f"- {name} — dignity: {d['state'].replace('_', ' ')} ({d['note']}); "
            f"in the {_ord(d['house'])} house: {d['house_note']}"
        )
    for c in vedic.get("career_significators") or []:
        lines.append(
            f"- Career/wealth signal (10th from the {c['from']}, {c['planet']} "
            f"as {c['role']}): {c['theme']}"
        )
    for c in vedic.get("conjunctions") or []:
        lines.append(
            f"- {' + '.join(c['planets'])} conjunct in {c['sign']}: {c['note']}")

    if not lines:
        return ""
    return ("\nClassical Vedic factors (cite these when they bear on the "
            "question; do NOT mention ones that are absent):\n" + "\n".join(lines) + "\n")


def _ord(n) -> str:
    """1 -> 1st, 3 -> 3rd, 11 -> 11th. House numbers read as "the 3th" otherwise."""
    try:
        n = int(n)
    except (TypeError, ValueError):
        return str(n)
    if 10 <= n % 100 <= 20:
        return f"{n}th"
    return f"{n}{ {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th') }"


# The engine names aspects as nouns. Handed "Jupiter conjunction Mercury", the
# model copied the noun straight into a verb slot — "Jupiter is conjunction your
# Mercury". Giving it the adjective costs nothing and reads properly.
_ASPECT_ADJ = {
    "conjunction": "conjunct",
    "opposition": "opposite",
    "square": "square",
    "trine": "trine",
    "sextile": "sextile",
    "quincunx": "quincunx",
}


# "list my mahadashas", "dasha kab hai", "antardasha timing" - all asking for
# the whole ladder. Matched on the question because the engine's topic
# classifier has no dasha topic and files these under personality.
_DASHA_WORDS = ("dasha", "dasa", "mahadasha", "mahadasa", "antardasha",
                "antardasa", "bhukti", "vimshottari", "दशा")


def _wants_dasha_list(question: str) -> bool:
    q = (question or "").lower()
    return any(w in q for w in _DASHA_WORDS)


def _timing_block(timing: dict, question: str = "") -> str:
    """The timing evidence as dated facts, not as the engine's prose.

    Everything here is something the reader can act on: which dasha and which
    year they are actually in, the windows that open and close on real dates,
    and the transits in orb right now. The engine's own long-form timing
    narration is deliberately not passed on - see the note in _build_prompt.

    Note on keys: windows carry from/to/text/quality and zr_events carry
    kind/sign/from/to. Reading label/detail/when off those yields None, which
    is how "Window: None" reached the prompt and how the model came to invent
    timing out of nulls.
    """
    if not timing:
        return ""

    lines = []
    snap = timing.get("snapshot") or {}

    vim = snap.get("vimshottari") or {}
    if vim:
        maha = vim.get("mahadasha") or {}
        antar = vim.get("antardasha") or {}
        if maha:
            lines.append(
                f"- Vimshottari mahadasha: {maha.get('lord')} "
                f"({maha.get('start')} to {maha.get('end')})"
            )
        if antar:
            lines.append(
                f"- Current antardasha: {antar.get('lord')} "
                f"({antar.get('start')} to {antar.get('end')})"
            )
        if vim.get("nakshatra"):
            lines.append(
                f"- Birth nakshatra: {vim['nakshatra']} pada {vim.get('pada')}"
            )
        # A question that names the dasha system is asking for the ladder, not
        # for one period. Sending all of it always would add eight lines to
        # every unrelated question, so it is spent only where it is the answer.
        upcoming = vim.get("upcoming") or []
        for n in (upcoming if _wants_dasha_list(question) else upcoming[:1]):
            lines.append(
                f"- Then {n.get('lord')} mahadasha: {n.get('start')} to {n.get('end')}"
            )

    prof = snap.get("profection") or {}
    if prof:
        line = (
            f"- Year lord: {prof.get('lord_of_year')} "
            f"(annual profection to the {_ord(prof.get('house'))}, {prof.get('sign')})"
        )
        if prof.get("lord_position"):
            line += (
                f"; that lord sits in {prof['lord_position']}, "
                f"house {prof.get('lord_house')}"
            )
        lines.append(line)
        if prof.get("monthly_lord"):
            lines.append(
                f"- This month: profected to the {_ord(prof.get('monthly_house'))} "
                f"({prof.get('monthly_sign')}), month lord {prof['monthly_lord']}"
            )

    zr = snap.get("zodiacal_releasing") or {}
    if zr:
        l1, l2 = zr.get("l1") or {}, zr.get("l2") or {}
        # The peak / loosing-of-the-bond flags belong to the SUB-period, not to
        # the long chapter. Emitting them as free-standing lines let the model
        # attach "a peak period" to the L1 end date and promise years of it, so
        # each flag is now written inside the line it qualifies.
        marks = []
        if zr.get("is_peak"):
            marks.append("a PEAK - a high point for visible results")
        if zr.get("is_loosing_bond"):
            marks.append("a LOOSING OF THE BOND - an abrupt change of chapter")
        mark = (" - this sub-period is " + " and ".join(marks)) if marks else ""
        if l1:
            lines.append(
                f"- Zodiacal releasing from {zr.get('lot')}: the long chapter is "
                f"{l1.get('sign')} ({l1.get('start')} to {l1.get('end')}); this is "
                f"background, not a window"
            )
        if l2:
            lines.append(
                f"- The sub-period running now is {l2.get('sign')}, and it ends "
                f"{l2.get('end')}{mark}"
            )
        elif marks:
            lines.append("- The sub-period running now is " + " and ".join(marks))

    fir = snap.get("firdaria") or {}
    if fir:
        # Named as a secondary system on purpose. Left unqualified, the model
        # picked the Firdaria end date as "the window to move" ahead of the
        # dasha and the actual dated windows, which is not how it ranks.
        lines.append(
            f"- Firdaria (a secondary system - mention only if nothing better "
            f"fits): {fir.get('major')} major / {fir.get('sub')} sub, the major "
            f"period ending {fir.get('major_until')}"
        )

    for w in (timing.get("windows") or [])[:4]:
        lines.append(
            f"- Window {w.get('from')} to {w.get('to')}: {w.get('text')} "
            f"[{w.get('quality')}]"
        )
    for e in (timing.get("zr_events") or [])[:3]:
        lines.append(
            f"- Turning point {e.get('from')}: {e.get('kind')} in {e.get('sign')}"
        )
    for t in (timing.get("active_transits") or [])[:4]:
        lines.append(
            f"- In orb now: transiting {t.get('transit')} "
            f"{_ASPECT_ADJ.get((t.get('aspect') or '').lower(), (t.get('aspect') or '').lower())} "
            f"natal {t.get('natal')} (orb {t.get('orb')}\u00b0)"
        )

    if not lines:
        return ""
    header = "\nTiming evidence (use these real dates; do not invent others):\n"
    return header + "\n".join(lines) + "\n"


# Month abbreviations only. A bare [A-Z][a-z]{2} also matches ordinary words —
# "The 2026" would have been offered to the model as a permitted date.
_DATE_RE = re.compile(
    r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+"
    r"((?:19|20)\d{2})\b"
)


def _allowed_dates_note(body: str) -> str:
    """Enumerate the dates the answer is permitted to print.

    A general "do not invent dates" rule was not enough on its own: told the
    Taurus sub-period *ends Aug 2026*, the model advised waiting until "Sep
    2026, when this window closes" — arithmetic on a supplied date rather than
    an invention out of nothing, and the kind of slip a reader would plan
    around. Listing the permitted strings explicitly turns an instruction the
    model has to reason about into one it can check itself against, for about
    thirty tokens.
    """
    seen = sorted({f"{m} {y}" for m, y in _DATE_RE.findall(body)},
                  key=lambda s: (s[-4:], s[:3]))
    if not seen:
        return ""
    return (
        "The ONLY dates you may print are: " + ", ".join(seen) + ". Any other "
        "month or year — including the month after one of these, or a point "
        "part-way through a period — is forbidden. If you need to refer to a "
        "time that is not on this list, describe it in words instead.\n\n"
    )


def _build_prompt(analysis: dict, language: str, question: str, history: list[dict] | None = None) -> str:
    """Facts only — deliberately NOT the engine's own prose.

    The engine writes its own long-form answer, and passing it through was
    half the prompt by weight. Worse, the model paraphrased it: readings came
    back full of the engine's stock phrases ("routes this through home and
    roots", "plays the long game", "works indirectly"), which is exactly the
    bookish register a customer does not want. It cannot echo wording it was
    never shown.

    Dropping the prose took the user turn from ~1160 to ~570 tokens; spending
    some of that back on structured timing detail — the dasha, the dated
    windows — leaves it around 850, so roughly a quarter cheaper per question
    and materially more specific. Prompt caching is not an option here: Haiku
    will not cache a prefix below 4096 tokens, and this whole request is a
    fifth of that.
    """
    evidence = "\n".join(
        f"- [{e['factor']}] {e['detail']} (weight {e['score']:+.2f})"
        for e in analysis.get("evidence", [])[:10]
    )
    hist_text = ""
    if history:
        hist_text = "PREVIOUS CONVERSATION HISTORY:\n"
        for h in history:
            hist_text += f"User: {h.get('question')}\nAssistant: {h.get('answer')}\n\n"
        hist_text += "--- END OF HISTORY ---\n\n"

    body = (
        hist_text +
        f"THE QUESTION TO ANSWER: “{question}”\n\n"
        f"Topic: {analysis.get('topic_label')}. "
        f"The engine's verdict: {analysis.get('verdict')} "
        f"(score {analysis.get('score')} on -1 to +1).\n\n"
        f"Chart evidence behind that verdict:\n{evidence}\n"
        f"{_timing_block(analysis.get('timing') or {}, question)}"
        f"{_vedic_block(analysis.get('vedic') or {})}\n"
    )
    return (
        body
        + _allowed_dates_note(body)
        + f"Write the answer in {LANGUAGES.get(language, 'English')}. These are your "
        f"facts; the words are yours. Do not describe what a planet 'is' or what it "
        f"'governs' in the abstract — say what it means for this person's life, in "
        f"the concrete terms they would recognise.\n\n"
        f"Remember, length must be detailed: Aim for 300 to 500 words, structured into clear, "
        f"informative paragraphs. Plain prose only — no headings, no bullets, no bold or italics inside paragraph text unless emphasizing critical placements or dates."
    )


def _system(language: str) -> str:
    return SYSTEM_PROMPT.format(
        language=LANGUAGES.get(language, "English"),
        language_note=HINDI_NOTE if language == "hi" else ENGLISH_NOTE,
    )


def _brevity_note(provider: str) -> str:
    """Local CPU inference runs at a few tokens/sec — keep its output short.

    A full-length rewrite at 3-4 tok/s takes minutes. Asking a local model for
    a tighter piece is the difference between usable and unusable, and it is an
    honest trade rather than a hidden truncation.
    """
    if provider != "ollama":
        return ""
    return (
        "\n\nIMPORTANT: keep this rewrite tight — aim for roughly 250-300 words. "
        "Cover the verdict, the key chart factors, and timing details. Drop the "
        "unnecessary details rather than compressing everything."
    )


def stream_polish(analysis: dict, language: str, provider: str, question: str, history: list[dict] | None = None):
    """Yield the rewritten answer in chunks. Raises on failure — caller decides."""
    kind, model = _split(provider)
    system = _system(language)
    prompt = _build_prompt(analysis, language, question, history) + _brevity_note(kind)

    if kind == "ollama":
        payload = json.dumps({
            "model": model,
            "stream": True,
            "options": {"temperature": 0.4, "num_predict": 900},
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
        }).encode()
        request = urllib.request.Request(
            f"{OLLAMA_URL}/api/chat", data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=900) as resp:
            for raw in resp:
                if not raw.strip():
                    continue
                event = json.loads(raw)
                chunk = (event.get("message") or {}).get("content", "")
                if chunk:
                    yield chunk
                if event.get("done"):
                     return

    elif kind == "anthropic":
        import anthropic

        client = anthropic.Anthropic()
        # `output_config.effort` and `fallbacks` are accepted only by the
        # reasoning-tier models; Haiku rejects the whole request with a 400 if
        # either is present. The engine has already done the judgement, so the
        # small model is the default here — these go only to models that take
        # them. Note the failure mode this caused: polish() catches everything
        # and quietly returns the engine's own text, so a rejected request looks
        # exactly like a working one until you read `llm_error`.
        extra: dict = {}
        if "opus" in CLAUDE_MODEL or "sonnet" in CLAUDE_MODEL:
            extra["output_config"] = {"effort": "low"}
            extra["betas"] = ["server-side-fallback-2026-07-01"]
            extra["fallbacks"] = "default"

        with client.beta.messages.stream(
            model=CLAUDE_MODEL,
            max_tokens=CLAUDE_MAX_TOKENS,
            system=system,
            messages=[{"role": "user", "content": prompt}],
            **extra,
        ) as stream:
            for text in stream.text_stream:
                yield text
            if stream.get_final_message().stop_reason == "refusal":
                raise RuntimeError("Claude declined to rewrite this reading.")
    else:
        raise ValueError(f"Unknown provider '{provider}'")


def polish(analysis: dict, language: str = "en", provider: str = "off",
           question: str = "", history: list[dict] | None = None) -> tuple[str, str | None]:
    """Blocking version of `stream_polish`, for the non-streaming endpoint.

    Returns (text, error). On any failure the engine's own wording is returned,
    so a missing or broken model degrades the prose but never the reading.
    """
    if provider in ("off", "", None):
        return analysis.get("answer", ""), None

    try:
        text = "".join(stream_polish(analysis, language, provider, question, history)).strip()
    except urllib.error.URLError as exc:
        return analysis.get("answer", ""), f"Could not reach the local model ({exc.reason})."
    except Exception as exc:
        return analysis.get("answer", ""), f"{type(exc).__name__}: {exc}"

    # A model that returns almost nothing has failed, whatever it says.
    if len(text) < 120:
        return analysis.get("answer", ""), "The model returned too little text to trust."
    return text, None


def generate_spiritual_guidance(analysis: dict, language: str = "en") -> str:
    """Generate a custom paragraph of spiritual/remedy guidance from Claude or Ollama."""
    provider = os.environ.get("ASTRO_PROVIDER", "anthropic")
    if not provider or provider == "off":
        if os.environ.get("ANTHROPIC_API_KEY"):
            provider = "anthropic"
        else:
            provider = "off"
            
    if provider == "off":
        return (
            "Continue with your daily meditation, focus on balancing your mind, and wear "
            "your prescribed gemstones with care. Maintain clarity, integrity, and follow "
            "the dasha specific mantras to navigate the current transit windows smoothly."
        )

    # Let's build a prompt
    meta = analysis.get("meta", {})
    lagna = analysis.get("lagna", "") or "Ascendant"
    moon_sign = analysis.get("moon_sign", "") or "Moon Sign"
    dasha_lord = analysis.get("dasha", {}).get("mahadasha", {}).get("lord", "")
    
    prompt = (
        f"You are Pandit Shukla, an elite Vedic astrologer with decades of experience. "
        f"Generate a personalized, warm, and highly authoritative spiritual guidance and remedy guidance "
        f"report for a native with Lagna in {lagna} and Moon in {moon_sign}. "
        f"They are currently running their {dasha_lord} Mahadasha. "
        f"Write 2 to 3 paragraphs of deep, practical, and highly premium spiritual counseling, "
        f"mindset shifts, and direct advice to make the most of this period. "
        f"Write {'in Hindi (Devanagari script)' if language == 'hi' else 'in English'}. "
        f"Do not output markdown headings or titles. Go straight into the text."
    )
    
    system = "You are a warm, wise, and highly experienced Vedic astrologer providing guidance."
    
    try:
        kind, model = _split(provider)
        if kind == "anthropic":
            import anthropic
            client = anthropic.Anthropic()
            msg = client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=600,
                system=system,
                messages=[{"role": "user", "content": prompt}]
            )
            return msg.content[0].text
        elif kind == "ollama":
            payload = json.dumps({
                "model": model,
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
                "stream": False
            }).encode("utf-8")
            request = urllib.request.Request(
                f"{OLLAMA_URL}/api/chat", data=payload,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(request, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["message"]["content"]
    except Exception:
        pass
    return "Continue with your daily prayers and wear the recommended gemstones to support your astrological alignment."


def _parse_json_object(raw: str) -> dict:
    """The first JSON object in a model response.

    `json.loads` on the whole string is brittle in both directions: a ```json
    fence or a "Here is your analysis:" preamble puts characters before the
    object, and a response that keeps going after it raises "Extra data". Find
    the first `{` and let the decoder consume exactly one value from there.
    """
    start = raw.find("{")
    if start < 0:
        raise ValueError("no JSON object in the response")
    obj, _end = json.JSONDecoder().raw_decode(raw[start:])
    if not isinstance(obj, dict):
        raise ValueError(f"expected a JSON object, got {type(obj).__name__}")
    return obj


def _chart_facts(analysis: dict) -> str:
    """The computed chart, rendered for a prompt.

    The PDF generators used to send the Lagna, the Moon sign and the running
    dasha lord, and then ask for a house-by-house and planet-by-planet reading.
    Nothing in that request could be answered from what was sent, so the model
    filled in placements — and the invented ones were printed a page away from
    the engine's own tables, which is the worst place to be wrong. Everything
    here is already computed by `chart_service` and `vargas`; the model's job
    is to read it, not to reconstruct it.
    """
    parts: list[str] = []

    header = []
    if analysis.get("lagna"):
        header.append(f"Lagna (Ascendant): {analysis['lagna']}")
    if analysis.get("moon_sign"):
        header.append(f"Moon sign (Rashi): {analysis['moon_sign']}")
    maha = analysis.get("dasha", {}).get("mahadasha", {}) or {}
    if maha.get("lord"):
        if maha.get("start") and maha.get("end"):
            header.append(
                f"Running Mahadasha: {maha['lord']}, "
                f"{maha['start']} to {maha['end']} ({maha.get('years', '')} years)")
        else:
            header.append(f"Running Mahadasha lord: {maha['lord']}")
    if header:
        parts.append("\n".join(header))

    # The chart bundle calls the lunar nodes "True Node" and "South Node". Asked
    # for a reading of the nine grahas against a table naming them that way, the
    # model simply left Rahu and Ketu out — it had no row it recognised as
    # either. The varga grid already uses the Vedic names; match it.
    def _vedic(text: str) -> str:
        for western, vedic in (("True Node", "Rahu"), ("Mean Node", "Rahu"),
                               ("North Node", "Rahu"), ("South Node", "Ketu")):
            text = text.replace(western, vedic)
        return text

    def _table(rows: list) -> str:
        return "\n".join(_vedic(" | ".join(str(c) for c in r)) for r in rows)

    rows = analysis.get("placements") or []
    if rows:
        parts.append(
            "PLANETARY POSITIONS (body | sign | degree | house | placement | dignity)\n"
            + _table(rows))

    rows = analysis.get("houses") or []
    if rows:
        parts.append(
            "HOUSES (house | sign on cusp | cusp degree | ruler | occupants)\n"
            + _table(rows))

    vargas = analysis.get("vargas") or {}
    if vargas.get("rows"):
        parts.append(
            "DIVISIONAL CHARTS (" + " | ".join(vargas.get("headers", [])) + ")\n"
            + "\n".join(" | ".join(str(c) for c in r) for r in vargas["rows"]))

    rows = analysis.get("yogas") or []
    if rows:
        parts.append(
            "YOGAS FOUND BY THE ENGINE "
            "(name | category | planets | why it forms | classical note)\n"
            + _table(rows))

    rows = analysis.get("antardasha") or []
    if rows:
        parts.append(
            "ANTARDASHAS OF THE RUNNING MAHADASHA (lord | from | to | status)\n"
            + "\n".join(" | ".join(str(c) for c in r) for r in rows))

    # Remedies are computed, not a matter of opinion: the stones follow from the
    # 1st, 5th and 9th lords and the mantra from the running dasha lord. Left to
    # itself the model wrote a different Shani mantra than the engine's, so the
    # chart PDF and the remedies PDF disagreed for the same person.
    rem = analysis.get("remedies") or {}
    if rem:
        lines = []
        for stone in (rem.get("gemstones") or {}).values():
            lines.append(
                f"{stone.get('role', 'Stone')}: {stone.get('name')} "
                f"(for {stone.get('planet')}) — {stone.get('finger')}, "
                f"set in {stone.get('metal')}")
        dr = rem.get("dasha_remedies") or {}
        if dr.get("mantra"):
            lines.append(f"Mantra for the running {dr.get('mahadasha_lord')} "
                         f"mahadasha: {dr['mantra']}")
        if dr.get("charity"):
            lines.append(f"Charity: {dr['charity']}")
        if lines:
            parts.append(
                "PRESCRIBED REMEDIES — use these exactly. Do not substitute a "
                "different mantra, stone, finger or metal.\n" + "\n".join(lines))

    reading = (analysis.get("dasha") or {}).get("mahadasha", {}).get("classical_reading")
    if reading:
        parts.append(
            "CLASSICAL READING OF THE RUNNING MAHADASHA (Brihat Jataka ch. 8): "
            + reading)

    rows = analysis.get("dignities") or []
    if rows:
        parts.append(
            "CLASSICAL DIGNITY OF EACH PLANET (planet | state | what it means "
            "here)\n" + _table(rows))

    rows = analysis.get("house_placements") or []
    if rows:
        parts.append(
            "CLASSICAL READING OF EACH PLANET'S HOUSE (planet | house | what "
            "it brings, Brihat Jataka ch. 20)\n" + _table(rows))

    rows = analysis.get("career_significators") or []
    if rows:
        parts.append(
            "CAREER / WEALTH-SOURCE SIGNIFICATORS (planet | read from Lagna or "
            "Moon | as occupant or lord of the 10th | classical theme, Brihat "
            "Jataka ch. 10)\n" + _table(rows))

    rows = analysis.get("conjunctions") or []
    if rows:
        parts.append(
            "PLANETARY CONJUNCTIONS AND THEIR CLASSICAL MEANING (planets | "
            "sign | note)\n" + _table(rows))

    if not parts:
        return ""
    return (
        "COMPUTED CHART — this is the native's actual chart, calculated with the "
        "Swiss Ephemeris (sidereal, Lahiri ayanamsa, whole-sign houses). Every "
        "claim you make about a placement must come from the data below. Do not "
        "state a position, house, dignity or yoga that does not appear here.\n\n"
        + "\n\n".join(parts))


# These report generators do not use SYSTEM_PROMPT, so none of its guardrails
# reach them. Without this rule the model did arithmetic on the dasha dates and
# printed a mahadasha ending in 2039 that the engine ends in 2037 — a wrong year
# in a paid report, sitting a page away from the correct dasha table.
REPORT_DATE_RULE = (
    "EVERY YEAR AND DATE YOU WRITE MUST APPEAR VERBATIM IN THE CHART DATA ABOVE. "
    "Do no arithmetic on dates: do not add a period's length to its start, do not "
    "estimate a midpoint, do not say when something 'peaks' inside a range. If a "
    "date you want is not printed above, describe the period without naming a year."
)

# The chart data is handed over in the engine's English vocabulary, so a Hindi
# report transliterates it — "कादिर भाव" for Cadent, "यूरेनस" for Uranus — while
# the tables on the facing page use आपोक्लिम and अरुण. Same document, two
# vocabularies. HINDI_NOTE does this job for the chat path; these generators
# need the terms the PDF tables actually print.
REPORT_HINDI_GLOSSARY = """Use exactly these Hindi terms so the prose matches the \
tables printed beside it. Never transliterate an English term into Devanagari \
letters when it appears here:

    Angular=केंद्र  Succedent=पणफर  Cadent=आपोक्लिम
    Uranus=अरुण  Neptune=वरुण  Pluto=यम  Rahu=राहु  Ketu=केतु
    ruler=स्वराशि  exalted=उच्च  fall=नीच  detriment=शत्रुक्षेत्र
    peregrine=बलहीन  term=सीमा बल  triplicity=त्रिकोण बल
    house=भाव  sign=राशि  lord=स्वामी  dasha=दशा  antardasha=अंतर्दशा

Signs: Aries=मेष Taurus=वृषभ Gemini=मिथुन Cancer=कर्क Leo=सिंह Virgo=कन्या \
Libra=तुला Scorpio=वृश्चिक Sagittarius=धनु Capricorn=मकर Aquarius=कुंभ Pisces=मीन

Planets: Sun=सूर्य Moon=चंद्रमा Mars=मंगल Mercury=बुध Jupiter=बृहस्पति \
Venus=शुक्र Saturn=शनि"""


REPORT_SYSTEM = (
    "You are a warm, wise, and highly experienced Vedic astrologer providing "
    "guidance in JSON format. The chart has already been calculated by a "
    "deterministic engine; you interpret what you are given and never restate a "
    "placement or a date differently from how it appears in the data."
)


def generate_kundali_narratives(analysis: dict, language: str = "en") -> dict:
    """Generate Yearly Varshphal (month-by-month), Upcoming Key Periods, and House-wise summaries."""
    provider = default_provider()
    _who = "generate_kundali_narratives"

    meta = analysis.get("meta", {})
    lagna = analysis.get("lagna", "") or "Ascendant"
    moon_sign = analysis.get("moon_sign", "") or "Moon Sign"
    dasha_lord = analysis.get("dasha", {}).get("mahadasha", {}).get("lord", "")

    # Calculate 12 monthly intervals starting from the solar return of current year
    import datetime as dt
    birth_date_str = meta.get("local_time", "").split()[0] if meta.get("local_time") else "1999-08-14"
    try:
        b_dt = dt.datetime.strptime(birth_date_str, "%Y-%m-%d")
    except Exception:
        b_dt = dt.datetime(1999, 8, 14)
        
    now = dt.datetime.now()
    varsh_year = now.year if (now.month > b_dt.month or (now.month == b_dt.month and now.day >= b_dt.day)) else now.year - 1
    
    start_date = dt.datetime(varsh_year, b_dt.month, b_dt.day)
    
    monthly_intervals = []
    month_names_en = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    month_names_hi = ["जनवरी", "फरवरी", "मार्च", "अप्रैल", "मई", "जून", "जुलाई", "अगस्त", "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर"]
    
    for i in range(12):
        m_start = start_date
        try:
            if m_start.month == 12:
                m_end = dt.datetime(m_start.year + 1, 1, m_start.day)
            else:
                m_end = dt.datetime(m_start.year, m_start.month + 1, m_start.day)
        except ValueError:
            m_end = m_start + dt.timedelta(days=30)
            
        if language == "hi":
            lbl = f"{m_start.day} {month_names_hi[m_start.month - 1]} से {m_end.day} {month_names_hi[m_end.month - 1]}"
        else:
            lbl = f"{m_start.day} {month_names_en[m_start.month - 1]} to {m_end.day} {month_names_en[m_end.month - 1]}"
            
        monthly_intervals.append(lbl)
        start_date = m_end

    # Pre-translated fallbacks
    fallbacks = {
        "en": {
            "varshphal": [
                [monthly_intervals[0], "Transit of Ascendant lord brings new opportunities and fresh energy. Focus on self-development."],
                [monthly_intervals[1], "Financial planning is highlighted. Good time to invest in long-term stable assets."],
                [monthly_intervals[2], "Short travels and intellectual pursuits are favored. Communication with siblings is productive."],
                [monthly_intervals[3], "Domestic happiness increases. Focus on home decoration and spending quality time with family."],
                [monthly_intervals[4], "Creativity and learning are at their peak. Academic and speculative interests bring joy."],
                [monthly_intervals[5], "Pay attention to health and routine. Avoid disputes and manage your work-life balance carefully."],
                [monthly_intervals[6], "Partnerships and relationships are favored. Good period for collaborative projects."],
                [monthly_intervals[7], "Sudden transformations or interest in research and occult sciences may arise. Stay patient."],
                [monthly_intervals[8], "Fortunate period. Spiritual inclination rises and long-distance travel is indicated."],
                [monthly_intervals[9], "Career advancement and professional consolidation. Recognition from authority figures."],
                [monthly_intervals[10], "Social networking brings financial gains. Fulfillment of desires and happiness through friends."],
                [monthly_intervals[11], "Spiritual reflection and higher expenditures. Good time for introspection and charity."]
            ],
            "key_periods": "Key opportunities arise in the second half of the year when planetary transits align with your natal solar placements. Avoid starting major ventures during Rahu Kalam hours, and utilize the auspicious Abhijit Muhurtha for important initiations.",
            "house_summary": "Your ascendant lord indicates a focus on self-expression and personal development. The planetary placements in the second and eleventh houses indicate steady source of income and support from social networks, while the tenth house energy drives ambition and leadership."
        },
        "hi": {
            "varshphal": [
                [monthly_intervals[0], "लग्न स्वामी का गोचर आपके स्वास्थ्य में सुधार और नई ऊर्जा लाएगा। व्यक्तिगत विकास पर ध्यान दें।"],
                [monthly_intervals[1], "आर्थिक योजना के लिए समय अनुकूल है। दीर्घावधि के निवेश से लाभ होने की संभावना है।"],
                [monthly_intervals[2], "लघु यात्राएं और बौद्धिक कार्य सफल रहेंगे। भाई-बहनों के साथ संवाद सुखद रहेगा।"],
                [monthly_intervals[3], "पारिवारिक सुख-शांति में वृद्धि होगी। घर की सजावट और माता के स्वास्थ्य पर ध्यान दें।"],
                [monthly_intervals[4], "रचनात्मकता और विद्या के क्षेत्र में उन्नति होगी। शिक्षा और नवीन कार्यों में रुचि बढ़ेगी।"],
                [monthly_intervals[5], "स्वास्थ्य और दैनिक दिनचर्या के प्रति सतर्क रहें। व्यर्थ के विवादों से दूर रहना ही श्रेयस्कर है।"],
                [monthly_intervals[6], "साझेदारी और दांपत्य जीवन के लिए समय अनुकूल है। आपसी तालमेल से काम बनेंगे।"],
                [monthly_intervals[7], "जीवन में अचानक कुछ बड़े बदलाव या शोध कार्यों में रुचि जागृत हो सकती है। धैर्य रखें।"],
                [monthly_intervals[8], "भाग्य का पूर्ण सहयोग मिलेगा। धार्मिक यात्राओं और आध्यात्मिक कार्यों में मन लगेगा।"],
                [monthly_intervals[9], "करियर में उन्नति और मान-सम्मान की प्राप्ति होगी। अधिकारियों से सहयोग मिलेगा।"],
                [monthly_intervals[10], "सामाजिक संपर्कों से लाभ होगा। मित्रों के सहयोग से अधूरी इच्छाएं पूरी होंगी।"],
                [monthly_intervals[11], "खर्चों में वृद्धि होगी और आध्यात्मिक चिंतन बढ़ेगा। दान-पुण्य के कार्यों में रुचि लें।"]
            ],
            "key_periods": "वर्ष के दूसरे भाग में महत्वपूर्ण अवसर आने की संभावना है जब प्रमुख ग्रहों का गोचर आपकी कुंडली के अनुकूल रहेगा। राहूकाल के दौरान महत्वपूर्ण कार्यों को टालें और अभिजीत मुहूर्त का उपयोग करें।",
            "house_summary": "आपका लग्न स्वामी आपके व्यक्तित्व और आत्म-विकास के लिए उत्तम है। द्वितीय और एकादश भाव में ग्रहों की स्थिति आय के नए स्रोतों और सामाजिक संबंधों से लाभ की ओर संकेत करती है। दशम भाव की ऊर्जा आपके कार्यक्षेत्र में उन्नति प्रदान करेगी।"
        }
    }

    lang_key = "hi" if language == "hi" else "en"
    default_res = fallbacks[lang_key]

    if provider == "off":
        return default_res

    prompt = (
        f"You are Pandit Shukla, an elite Vedic astrologer with decades of experience.\n"
        f"Generate a personalized, premium month-by-month Varshphal analysis for a native named {meta.get('name', 'Native')} "
        f"born on {meta.get('local_time', '')} at {meta.get('place', '')}.\n\n"
        f"{_chart_facts(analysis)}\n\n"
        f"Ground every month's forecast in the placements above — name the planet, "
        f"its house and the dasha or antardasha you are reading from.\n\n"
        f"Please provide three distinct sections:\n"
        f"1. A month-by-month forecast (varshphal) for the next 12 months. You must use these exact month labels:\n"
        f"   {', '.join(monthly_intervals)}\n"
        f"2. Upcoming key periods, indicating when major developments in career, finance, or relationships are likely to occur (around 120 words).\n"
        f"3. A house-wise summary explaining the planetary influences active across the primary houses of their chart (around 150 words).\n\n"
        f"You MUST format the output as a valid JSON object with the following three keys:\n"
        f"- 'varshphal': a JSON array of 12 objects, each having:\n"
        f"  - 'month': the exact month label string from the list above\n"
        f"  - 'prediction': a monthly forecast written in {'Hindi (Devanagari script)' if language == 'hi' else 'English'} (around 30-40 words)\n"
        f"- 'key_periods': write in {'Hindi (Devanagari script)' if language == 'hi' else 'English'}\n"
        f"- 'house_summary': write in {'Hindi (Devanagari script)' if language == 'hi' else 'English'}\n\n"
        f"{REPORT_DATE_RULE}\n\n"
        f"Respond ONLY with the raw JSON block. Do not include any markdown fences, introduction, or notes."
        + (f"\n\n{REPORT_HINDI_GLOSSARY}" if language == "hi" else "")
    )

    system = REPORT_SYSTEM

    try:
        kind, model = _split(provider)
        if kind == "anthropic":
            import anthropic
            client = anthropic.Anthropic()
            msg = client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=_report_max_tokens(language),
                system=system,
                messages=[{"role": "user", "content": prompt}]
            )
            if msg.stop_reason == "max_tokens":
                # Truncated JSON parses as an error further down and the
                # report silently falls back to canned text. Say so.
                log.warning(
                    "%s: response hit the %s-token ceiling and was cut off; "
                    "using the fallback text. Raise ASTRO_REPORT_MAX_TOKENS_%s.",
                    _who, _report_max_tokens(language), "HI" if language == "hi" else "EN")
            raw = msg.content[0].text.strip()
        elif kind == "ollama":
            payload = json.dumps({
                "model": model,
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
                "stream": False,
                "format": "json"
            }).encode("utf-8")
            request = urllib.request.Request(
                f"{OLLAMA_URL}/api/chat", data=payload,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(request, timeout=40) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                raw = data["message"]["content"].strip()
        else:
            return default_res

        parsed = _parse_json_object(raw)
        
        # Format monthly predictions list
        parsed_varshphal = parsed.get("varshphal", [])
        formatted_varsh = []
        for i, lbl in enumerate(monthly_intervals):
            # Try to match by index or label
            pred = "Transit influence brings standard opportunities. Focus on routine prayers."
            if i < len(parsed_varshphal):
                item = parsed_varshphal[i]
                if isinstance(item, dict):
                    pred = item.get("prediction", pred)
                elif isinstance(item, list) and len(item) > 1:
                    pred = item[1]
            formatted_varsh.append([lbl, pred])

        return {
            "varshphal": formatted_varsh,
            "key_periods": parsed.get("key_periods", default_res["key_periods"]),
            "house_summary": parsed.get("house_summary", default_res["house_summary"]),
        }
    except Exception as exc:
        # Never let a narration failure break the PDF, but never let it
        # pass unrecorded either: the fallback is indistinguishable from
        # a real reading on the page.
        log.warning("%s failed (%s: %s); using the fallback text.",
                    _who, type(exc).__name__, exc)
    return default_res


def generate_kundali_interpretations(analysis: dict, language: str = "en") -> dict:
    """Detailed 12-house, 9-graha, and yoga/remedies interpretations of a chart.

    The chart itself is rendered into the prompt by `_chart_facts`; without it
    these three sections have nothing to interpret.
    """
    provider = default_provider()
    _who = "generate_kundali_interpretations"
    
    fallbacks = {
        "en": {
            "houses_detailed": (
                "* **First House (Lagna / Ascendant)**: Represents physical body, appearance, and life path. Your Lagna lord is well-placed, giving strong resilience, physical strength, and determination.\n"
                "* **Second House (Dhana Bhava)**: Governs wealth, speech, and family. The placement of planets here suggests steady accumulation of assets, refined speech, and strong family ties.\n"
                "* **Third House (Sahaja Bhava)**: Represents siblings, courage, and short travels. A strong third house indicates courage, sibling support, and success in communication-related ventures.\n"
                "* **Fourth House (Sukha Bhava)**: Represents mother, home, and happiness. Influences on this house point to a comfortable home environment and a strong emotional bond with the mother.\n"
                "* **Fifth House (Putra Bhava)**: Governs intellect, education, and children. You possess a sharp, analytical mind with a penchant for learning and creative pursuits.\n"
                "* **Sixth House (Shatru Bhava)**: Represents enemies, debts, and health. A well-aspected sixth house helps you overcome obstacles, defeat adversaries, and maintain robust health.\n"
                "* **Seventh House (Yuvati Bhava)**: Represents spouse, partnerships, and business. Signifies harmonious relationships and successful business partnerships built on trust.\n"
                "* **Eighth House (Randhra Bhava)**: Represents longevity, mysteries, and transformation. Suggests an interest in occult sciences, research, and deep life transformations.\n"
                "* **Ninth House (Dharma Bhava)**: Governs religion, fortune, and father. Indicates strong moral values, support from father figures, and fortunate long journeys.\n"
                "* **Tenth House (Karma Bhava)**: Represents career, status, and actions. Suggests a position of authority, professional growth, and high ambition.\n"
                "* **Eleventh House (Labha Bhava)**: Represents gains, desires, and friends. Points to multiple streams of income and fulfillment of desires through a supportive social network.\n"
                "* **Twelfth House (Vyaya Bhava)**: Governs expenses, isolation, and spiritual liberation. Indicates spiritual inclination and foreign travels or associations."
            ),
            "planets_detailed": (
                "* **Sun (Surya)**: The king of planets represents soul, authority, and father. Its placement drives your sense of self and ambition to lead.\n"
                "* **Moon (Chandra)**: Controls mind, emotions, and mother. The placement of the Moon determines your emotional response patterns and mental peace.\n"
                "* **Mars (Mangal)**: Governs energy, courage, and action. Its position dictates how you channel passion, resolve conflicts, and drive initiatives.\n"
                "* **Mercury (Budha)**: The planet of communication, intellect, and trade. Indicates logical thinking, business acumen, and learning capacity.\n"
                "* **Jupiter (Guru)**: Symbolizes wisdom, spirituality, expansion, and luck. Its influence brings spiritual inclination, growth, and benevolence.\n"
                "* **Venus (Shukra)**: Represents love, luxury, relationships, and arts. Governs your approach to aesthetics, partner harmony, and comfort.\n"
                "* **Saturn (Shani)**: The taskmaster represents discipline, hard work, and delay. Its placement highlights areas where focus and persistence are demanded.\n"
                "* **Rahu**: The north node represents worldly desire, ambition and sudden change. Its house shows where you reach hardest and where illusion must be watched for.\n"
                "* **Ketu**: The south node represents detachment, past merit and liberation. Its house shows what comes to you easily and what you are asked to let go of."
            ),
            "yogas_remedies_detailed": (
                "Your chart displays powerful planetary configurations (yogas) that shape your destiny. The active Vimshottari Mahadasha indicates that this is a period of transition and manifestation.\n\n"
                "**Recommended Remedies:**\n"
                "1. Recite the mantras for your active dasha lord daily to harmonize planetary energies.\n"
                "2. Practice charity on Saturdays (helping the needy) and fast on Thursdays to invoke auspicious results.\n"
                "3. Consider wearing the recommended gemstones (e.g., life stone) mounted in the appropriate metal."
            )
        },
        "hi": {
            "houses_detailed": (
                "* **प्रथम भाव (लग्न - शरीर और व्यक्तित्व)**: यह आपके शरीर, स्वास्थ्य और व्यक्तित्व को दर्शाता है। आपका लग्न स्वामी मजबूत स्थिति में है, जो आपको उत्तम स्वास्थ्य, तेजस्विता और स्वतंत्र विचार प्रदान करता है।\n"
                "* **द्वितीय भाव (धन और वाणी)**: यह संचित धन, कुटुंब और वाणी का प्रतिनिधित्व करता है। इस भाव पर ग्रहों की शुभ दृष्टि धन संचय और मधुर वाणी की ओर संकेत करती है।\n"
                "* **तृतीय भाव (पराक्रम और सहोदर)**: यह पराक्रम, भाई-बहन और लघु यात्राओं को दर्शाता है। यह स्थिति आपको साहसी बनाती है और भाई-बहनों से सहयोग दिलाती है।\n"
                "* **चतुर्थ भाव (सुख और माता)**: यह गृह सुख, वाहन, माता और मानसिक शांति का भाव है। चतुर्थ भाव में शुभता जीवन में सुख-सुविधाओं और माता से घनिष्ठ संबंध दर्शाती है।\n"
                "* **पंचम भाव (बुद्धि, संतान और विद्या)**: यह उच्च शिक्षा, रचनात्मकता और संतान सुख का भाव है। आपकी बुद्धि कुशाग्र है और रचनात्मक कार्यों में आपकी गहरी रुचि है।\n"
                "* **षष्ठ भाव (रोग, ऋण और शत्रु)**: यह भाव स्वास्थ्य संबंधी समस्याओं, कर्ज और शत्रुओं को दर्शाता है। ग्रहों की स्थिति आपको शत्रुओं पर विजय और बाधाओं को पार करने की शक्ति देती है।\n"
                "* **सप्तम भाव (दांपत्य जीवन और साझेदारी)**: यह जीवनसाथी और व्यापार में साझेदारी का भाव है। यह एक सामंजस्यपूर्ण वैवाहिक जीवन और सफल व्यावसायिक संबंधों की ओर संकेत करता है।\n"
                "* **अष्टम भाव (आयु और गुप्त ज्ञान)**: यह आयु, रहस्यमयी विद्याओं और जीवन में आने वाले बड़े बदलावों का भाव है। यह शोध कार्यों और गुप्त विज्ञान में रुचि को दर्शाता है।\n"
                "* **नवम भाव (भाग्य और धर्म)**: यह भाग्य, पिता और आध्यात्मिक उन्नति का भाव है। आपकी रुचि धार्मिक कार्यों में होगी और आपको पिता का पूर्ण सहयोग प्राप्त होगा।\n"
                "* **दशम भाव (कर्म और व्यवसाय)**: यह आपके करियर, सामाजिक प्रतिष्ठा और कार्यों का भाव है। यह करियर में निरंतर उन्नति, नेतृत्व क्षमता और उच्च पद की प्राप्ति दर्शाता है।\n"
                "* **एकादश भाव (आय और लाभ)**: यह आय के साधन, इच्छाओं की पूर्ति और बड़े भाई-बहनों का भाव है। यह आय के स्थिर स्रोत और मित्रों के सहयोग को दर्शाता है।\n"
                "* **द्वादश भाव (व्यय और मोक्ष)**: यह व्यय, विदेश यात्रा और आध्यात्मिक मोक्ष का प्रतिनिधित्व करता है। आपकी रुचि ध्यान और एकांत साधना में हो सकती है।"
            ),
            "planets_detailed": (
                "* **सूर्य (Surya)**: सूर्य आत्मा, शक्ति, मान-सम्मान और पिता का कारक है। इसकी स्थिति आपके नेतृत्व गुणों और महत्वाकांक्षा को निर्धारित करती है।\n"
                "* **चंद्रमा (Chandra)**: चंद्रमा मन, भावनाओं और माता का कारक है। यह आपकी मानसिक शांति, संवेदनशीलता और विचारों को प्रभावित करता है।\n"
                "* **मंगल (Mangal)**: मंगल ऊर्जा, साहस और पराक्रम का कारक है। इसकी स्थिति आपके साहसिक कार्यों और निर्णय लेने की क्षमता को दर्शाती है।\n"
                "* **बुध (Budha)**: बुध बुद्धि, वाणी और व्यापार का कारक है। यह आपके तार्किक विश्लेषण, लेखन और व्यापारिक सूझबूझ को प्रकट करता है।\n"
                "* **बृहस्पति (Guru)**: बृहस्पति ज्ञान, धर्म, भाग्य और संतान का कारक है। इसकी शुभ स्थिति आपके जीवन में सुख, भाग्य और उच्च सोच को विकसित करती है।\n"
                "* **शुक्र (Shukra)**: शुक्र प्रेम, कला, विलासिता और दांपत्य का कारक है। यह आपकी रचनात्मकता और भौतिक सुखों के प्रति आकर्षण को दर्शाता है।\n"
                "* **शनि (Shani)**: शनि कर्म, अनुशासन और न्याय का कारक है। इसकी स्थिति बताती है कि जीवन के किस क्षेत्र में आपको अत्यधिक परिश्रम और धैर्य की आवश्यकता है।\n"
                "* **राहु (Rahu)**: राहु सांसारिक इच्छा, महत्वाकांक्षा और आकस्मिक परिवर्तन का कारक है। यह बताता है कि जीवन के किस क्षेत्र में आप सर्वाधिक प्रयासरत रहेंगे।\n"
                "* **केतु (Ketu)**: केतु वैराग्य, पूर्वजन्म के संचित कर्म और मोक्ष का कारक है। यह दर्शाता है कि कौन सी उपलब्धि सहज मिलेगी और किससे विरक्ति आवश्यक है।"
            ),
            "yogas_remedies_detailed": (
                "आपकी कुंडली में विभिन्न ग्रहों के योग बन रहे हैं जो आपके जीवन की दिशा तय करते हैं। वर्तमान महादशा की अवधि में इन योगों का प्रभाव विशेष रूप से परिलक्षित होगा।\n\n"
                "**अनुशंसित ज्योतिषीय उपाय:**\n"
                "1. नकारात्मक प्रभावों को शांत करने के लिए अपने सक्रिय दशा स्वामी के मंत्र का प्रतिदिन १०८ बार जाप करें।\n"
                "2. प्रत्येक शनिवार को जरूरतमंदों को तिल या तेल का दान करें और गुरुवार को नमक रहित व्रत रखें।\n"
                "3. अपने जीवन चक्र को संतुलित करने के लिए शुभ मुहूर्त में अनुशंसित रत्न धारण करें।"
            )
        }
    }

    lang_key = "hi" if language == "hi" else "en"
    default_res = fallbacks[lang_key]

    if provider == "off":
        return default_res

    meta = analysis.get("meta", {})
    lagna = analysis.get("lagna", "")
    moon_sign = analysis.get("moon_sign", "")
    dasha_lord = analysis.get("dasha", {}).get("mahadasha", {}).get("lord", "")

    # We will query Claude/Ollama to generate the three detailed sections
    prompt = (
        f"You are Pandit Shukla, a premium Vedic astrologer with decades of experience.\n"
        f"Generate a detailed, comprehensive Kundali Vishleshan analysis for a native named {meta.get('name', 'Native')} "
        f"born on {meta.get('local_time', '')} at {meta.get('place', '')}.\n\n"
        f"{_chart_facts(analysis)}\n\n"
        f"This report is printed alongside the tables above, so a placement you "
        f"state incorrectly will sit next to the correct one. Read what is given; "
        f"do not supply anything that is missing.\n\n"
        f"Please provide three distinct sections:\n"
        f"1. A house-by-house analysis (houses_detailed) covering all 12 houses. For each house give the sign on it, "
        f"its lord and where that lord sits, and any occupying planets — taken from the tables above (around 400 words).\n"
        f"2. A planet-by-planet interpretation (planets_detailed) covering all nine grahas, Rahu and Ketu included. "
        f"For each, name its actual sign, house and dignity from the table above before interpreting it (around 350 words).\n"
        f"3. An analysis of the yogas listed above — only those, and give the reason each one forms "
        f"as the data states it (which houses the planets rule, not merely where they sit) — followed "
        f"by the prescribed remedies above, reproducing the mantra, stones, fingers and metals exactly "
        f"as given (yogas_remedies_detailed, around 250 words).\n\n"
        f"You MUST format the output as a valid JSON object with the following three keys:\n"
        f"- 'houses_detailed': write in {'Hindi (Devanagari script)' if language == 'hi' else 'English'}\n"
        f"- 'planets_detailed': write in {'Hindi (Devanagari script)' if language == 'hi' else 'English'}\n"
        f"- 'yogas_remedies_detailed': write in {'Hindi (Devanagari script)' if language == 'hi' else 'English'}\n\n"
        f"{REPORT_DATE_RULE}\n\n"
        f"Respond ONLY with the raw JSON block. Do not include markdown fences, preambles, or notes."
        + (f"\n\n{REPORT_HINDI_GLOSSARY}" if language == "hi" else "")
    )

    system = REPORT_SYSTEM

    try:
        kind, model = _split(provider)
        if kind == "anthropic":
            import anthropic
            client = anthropic.Anthropic()
            msg = client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=_report_max_tokens(language),
                system=system,
                messages=[{"role": "user", "content": prompt}]
            )
            if msg.stop_reason == "max_tokens":
                # Truncated JSON parses as an error further down and the
                # report silently falls back to canned text. Say so.
                log.warning(
                    "%s: response hit the %s-token ceiling and was cut off; "
                    "using the fallback text. Raise ASTRO_REPORT_MAX_TOKENS_%s.",
                    _who, _report_max_tokens(language), "HI" if language == "hi" else "EN")
            raw = msg.content[0].text.strip()
        elif kind == "ollama":
            payload = json.dumps({
                "model": model,
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
                "stream": False,
                "format": "json"
            }).encode("utf-8")
            request = urllib.request.Request(
                f"{OLLAMA_URL}/api/chat", data=payload,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(request, timeout=40) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                raw = data["message"]["content"].strip()
        else:
            return default_res

        parsed = _parse_json_object(raw)
        return {
            "houses_detailed": parsed.get("houses_detailed", default_res["houses_detailed"]),
            "planets_detailed": parsed.get("planets_detailed", default_res["planets_detailed"]),
            "yogas_remedies_detailed": parsed.get("yogas_remedies_detailed", default_res["yogas_remedies_detailed"]),
        }
    except Exception as exc:
        # Never let a narration failure break the PDF, but never let it
        # pass unrecorded either: the fallback is indistinguishable from
        # a real reading on the page.
        log.warning("%s failed (%s: %s); using the fallback text.",
                    _who, type(exc).__name__, exc)
    return default_res



