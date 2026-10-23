"""DIVASTRO-161/163: the chat answer must be plain and about this person.

Customer feedback: "the answers are too generic" (161) and "should be simple in
language without jargons" (163). The narration prompt used to ask for a
"premium, highly detailed" 300-500 word reading covering dignities,
profections and releasing peaks by name. This pins the replacement:
  - the plain-language and specificity rules are in the system prompt, for
    English, Hindi and a regional language;
  - the prompt names the banned technical words only to forbid them (it never
    asks for one);
  - the built prompt carries "they are N years old" and the running
    mahadasha/antardasha when a birth date is known, and nothing when not;
  - the age never becomes a printable date, and the date list is unchanged.
"""
import datetime as dt
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("ASTRO_SECRET_KEY", "ci")
from app import llm  # noqa: E402

failures: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(("PASS" if ok else "FAIL"), "", name, ("" if ok else f"-- {detail}"))
    if not ok:
        failures.append(name)


# --- the system prompt's rules ------------------------------------------------
for code in ("en", "hi", "kn"):
    system = llm._system(code)
    check(f"{code}: family-astrologer, everyday-words style",
          "family astrologer" in system and "Everyday words" in system
          and "short sentences" in system)
    check(f"{code}: at most two or three terms, each explained",
          "at most two or three astrology terms" in system
          and "explain each" in system)
    check(f"{code}: the banned list is spelled out",
          all(f'"{w}"' in system for w in llm.BANNED_JARGON))
    check(f"{code}: open with a direct answer to their exact question",
          "Open with a direct answer to their exact question" in system)
    check(f"{code}: delete any sentence that could be said to anyone",
          "delete every sentence that could be said to anyone" in system)
    check(f"{code}: their own dates, their age and running period",
          "their own dates" in system and "their age" in system
          and "the period they are running now" in system)
    check(f"{code}: two or three practical, question-specific steps",
          "two or three practical steps" in system and "stay positive" in system)
    check(f"{code}: 180 to 320 words, no headings or lists",
          "About 180 to 320 words" in system and "no headings" in system)
    check(f"{code}: no degrees unless asked", "No degrees" in system)
    # The absolute rules stay.
    for rule in ("Never add an astrological fact", "Never change a fact",
                 "EVERY YEAR AND MONTH YOU WRITE MUST APPEAR VERBATIM",
                 "Never drop the verdict", "Never invent certainty",
                 "Never print the engine's internal numbers"):
        check(f"{code}: keeps rule '{rule[:30]}'", rule in system)

check("hi: simple spoken Hindi, not Sanskritised",
      "simple spoken Hindi" in llm._system("hi") and "Sanskritised" in llm._system("hi"))
check("hi: the sign table stays", "Capricorn=मकर" in llm._system("hi"))
check("kn: simple spoken register", "simple spoken" in llm._system("kn"))
check("the old 'premium, highly detailed' 300-500 brief is gone",
      "premium" not in llm.SYSTEM_PROMPT and "300 to 500" not in llm.SYSTEM_PROMPT)

# The prompt may name a banned word only inside the sentence that forbids it.
system = llm._system("en")
ban_start = system.index("These words must never appear")
ban_end = system.index("Translate the meaning instead")
outside = (system[:ban_start] + system[ban_end:]).lower()
asked = [w for w in llm.BANNED_JARGON
         if re.search(r"(?<![a-z])" + re.escape(w.lower()) + r"(?![a-z])", outside)]
check("the system prompt never asks for a banned term", not asked, str(asked))
for phrase in ("dignities", "profections", "releasing peaks", "house ruler connections"):
    check(f"the system prompt no longer requests '{phrase}'", phrase not in outside)

# Translation (regional emailed answers) keeps the plain register.
check("translation keeps the plain register",
      "simple spoken" in llm.TRANSLATE_SYSTEM and "Sanskritised" in llm.TRANSLATE_SYSTEM)
check("remedy guidance asks for plain words", "plain, everyday words" in llm._REMEDY_GROUNDING)
check("report prose asks for plain language", "plain, everyday language" in llm.REPORT_SYSTEM)

# --- the person line in the built prompt ----------------------------------------
ANALYSIS = {
    "topic_label": "Marriage", "verdict": "favourable", "score": 0.4,
    "evidence": [{"factor": "7th ruler", "detail": "Venus Libra 12°00′ H7", "score": 1.0}],
    "timing": {"snapshot": {"vimshottari": {
        "mahadasha": {"lord": "Mars", "start": "Dec 2025", "end": "Dec 2032"},
        "antardasha": {"lord": "Rahu", "start": "May 2026", "end": "May 2027"}}}},
}
with_birth = dict(ANALYSIS, birth_date="1996-03-14", as_of="2026-10-23")
prompt = llm._build_prompt(with_birth, "en", "When will I get married?")
check("the built prompt says the age", "they are 30 years old" in prompt, prompt[:400])
check("the built prompt names the running mahadasha and antardasha",
      "Mars mahadasha (Dec 2025 to Dec 2032)" in prompt
      and "Rahu antardasha (May 2026 to May 2027)" in prompt)
check("the person line comes right after the question",
      prompt.index("THE QUESTION") < prompt.index("About the person asking")
      < prompt.index("Topic:"))
check("no birth year reaches the prompt", "1996" not in prompt)
allowed = llm._allowed_dates_note(prompt)
check("the allowed dates are only the evidence's",
      allowed.startswith("The ONLY dates you may print are: May 2026, May 2027, Dec 2025, Dec 2032")
      or set(re.findall(r"[A-Z][a-z]{2} \d{4}", allowed.split(".")[0]))
      == {"Dec 2025", "Dec 2032", "May 2026", "May 2027"}, allowed[:200])
check("the user turn asks for 180-320 words, not 300-500",
      "180 to 320 words" in prompt and "300 to 500" not in prompt)

# Birthday not yet reached this year; the as_of date wins over today.
check("age before the birthday", llm._age_on("1996-11-01", dt.date(2026, 10, 23)) == 29)
check("age on the birthday", llm._age_on("1996-10-23", dt.date(2026, 10, 23)) == 30)
check("an unreadable birth date gives no age", llm._age_on("not a date", dt.date(2026, 1, 1)) is None)

no_birth = llm._build_prompt(dict(ANALYSIS), "en", "When will I get married?")
check("without a birth date there is no age, but the period still shows",
      "years old" not in no_birth and "About the person asking: the life phase" in no_birth)
bare = llm._build_prompt({"topic_label": "Career", "verdict": "mixed", "score": 0.0,
                          "evidence": []}, "en", "Career?")
check("with neither, no person line at all", "About the person asking" not in bare)

# Ollama keeps its own shorter note.
check("the local model's brevity note still applies",
      "150-220 words" in llm._brevity_note("ollama") and llm._brevity_note("anthropic") == "")

raise SystemExit(1 if failures else 0)
