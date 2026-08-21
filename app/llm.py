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
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass

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
