"""Dignity-faithfulness regression test (DIVASTRO-94/96).

`_audit_dignity()` checks that a polished answer doesn't reverse a planet's
dignity (call its own exaltation sign "debilitated"/"enemy", or its own
debilitation sign "exalted"/"friendly"). The prompt never spells dignity
words out (see `_build_prompt`'s docstring - evidence gives bare positions
like "Mars Capricorn 28°39'"), so this checks the model's claim against the
canonical EXALTATION/DEBILITATION tables, not against the prompt's wording.

The first two cases below are the REAL text a local model produced during
the DIVASTRO-96 comparison (2026-09-28) — not invented examples — for the
same chart used throughout that session's testing (Mars exalted in
Capricorn, 1990-03-12 09:30 Delhi). Pure unit test: no network, no chart, no
server.

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.test_llm_dignity_audit
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import llm  # noqa: E402

failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


# The real chart used throughout DIVASTRO-95/96 testing: Mars exalted in
# Capricorn (10th), Venus also in Capricorn (conjunct Mars, not exalted or
# debilitated there - Venus exalts in Pisces, debilitates in Virgo), Saturn
# in Aquarius (its own sign, not tested here since own-sign is out of scope).
ANALYSIS = {
    "evidence": [
        {"factor": "10th ruler", "detail": "Mars Capricorn 28°39' H10"},
        {"factor": "Venus in 10th", "detail": "Venus Capricorn 12°37' H10"},
        {"factor": "Sun in 11th", "detail": "Sun Aquarius 5°10' H11"},
    ]
}

# Verbatim excerpt from the real qwen2.5:3b career/en answer, 2026-09-28.
REAL_HALLUCINATION_1 = (
    "Mars, the planet of action and physical courage, is dignified in the 10th house, "
    "which is the house of career and public life. Mars is also in an enemy sign "
    "(Aquarius) in the 10th house, which brings a challenging but also potentially "
    "rewarding environment."
)

# Verbatim excerpt from the real qwen2.5:3b love/en answer, 2026-09-28 - the
# internally self-contradictory one (calls Venus friendly, then enemy, in the
# same paragraph).
REAL_HALLUCINATION_2 = (
    "Venus, the planet of love and harmony, is in a friendly sign (Pisces) in the "
    "10th house, which is the house of career. Venus is in an enemy sign (Capricorn) "
    "in the 10th house, which brings a strong pull between desire and discipline."
)

# The real Sonnet answer for the same question - clean, no violation expected.
REAL_CLEAN_SONNET = (
    "The strongest point in your favor is Mars. It sits exalted in Capricorn in your "
    "10th house of career, and it rules your 1st house (identity) as well — this is "
    "the classical placement of drive, competence, and capability."
)


def main() -> int:
    print("Dignity-faithfulness auditor\n")

    meta: dict = {}
    llm._audit_dignity(meta, ANALYSIS, REAL_HALLUCINATION_1)
    check("flags Mars-in-Capricorn called 'enemy sign' (it's exalted) - the real bug found",
          any("Mars" in v and "enemy" in v for v in meta.get("dignity_violations", [])),
          str(meta))

    # A known, accepted limitation: Venus in Capricorn is neither exalted nor
    # debilitated there (Venus exalts in Pisces, debilitates in Virgo), so
    # the narrow exalt/debilitate-reversal rule has no ground truth to check
    # "friendly"/"enemy" against here and correctly stays silent - even
    # though the SAME sentence contradicts itself (friendly, then enemy, for
    # the same placement). Catching an internal self-contradiction regardless
    # of ground truth is a real, different capability this auditor does not
    # attempt; noting it here rather than silently dropping the case.
    meta = {}
    llm._audit_dignity(meta, ANALYSIS, REAL_HALLUCINATION_2)
    check("Venus/Capricorn is outside the narrow exalt/debilitate rule, so no violation "
          "is raised here (a real gap - self-contradiction isn't checked - not a bug)",
          "dignity_violations" not in meta, str(meta))

    meta = {}
    llm._audit_dignity(meta, ANALYSIS, REAL_CLEAN_SONNET)
    check("the real clean Sonnet answer raises no violation",
          "dignity_violations" not in meta, str(meta))

    meta = {}
    llm._audit_dignity(meta, ANALYSIS, "Mars sits exalted in Capricorn in your 10th house.")
    check("correctly calling an exalted planet 'exalted' raises no violation",
          "dignity_violations" not in meta, str(meta))

    meta = {}
    llm._audit_dignity(meta, ANALYSIS,
                       "Sun is in Aquarius, its enemy sign, which weakens its results here.")
    check("a claim about a planet not in the evidence list at all (no ground truth) "
          "is silently skipped, not guessed at", "dignity_violations" not in meta, str(meta))

    meta = {}
    llm._audit_dignity(None, ANALYSIS, REAL_HALLUCINATION_1)
    check("meta=None is a no-op, not a crash (mirrors _audit_dates)", True)

    meta = {}
    llm._audit_dignity(meta, {"evidence": []}, REAL_HALLUCINATION_1)
    check("empty evidence list -> nothing to check against, no violation guessed",
          "dignity_violations" not in meta, str(meta))

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("dignity audit: all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
