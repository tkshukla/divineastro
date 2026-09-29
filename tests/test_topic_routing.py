"""Topic-routing regression sweep (DIVASTRO-94).

`classify()` in app/interpret/topics.py has already been bitten twice by the
same bug class: a keyword covers one verb form but not another a real user
types ("promotion" but not "promoted"; "dasha" but not "mahadasha", because
\\b sits inside the compound). Both were fixed by spelling out the missing
form explicitly - `_stem()`'s one-suffix strip and `_hits()`'s `\\w{0,4}` tail
cover a lot of inflections for free, but not everything, and nothing swept
the other 12 topics for the same gap before this file existed.

This asks, per topic, several realistically-phrased questions using different
verb forms/tenses for the same subject, and asserts they all land on the
expected topic. A phrasing that routes to the wrong topic gets none of that
topic's houses/significators to answer from - the exact failure mode DIVASTRO-43
found and fixed once already.

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.test_topic_routing
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.interpret.topics import classify  # noqa: E402

failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def expect(topic_key: str, *questions: str) -> None:
    for q in questions:
        got = classify(q).topic.key
        check(f"[{topic_key}] {q!r}", got == topic_key, f"routed to {got!r}")


def main() -> int:
    print("Topic routing: verb-form / tense sweep across all 13 topics\n")

    expect("career",
           "Will I get promoted this year?",
           "When will I be promoted?",
           "Am I getting a promotion soon?",
           "Should I quit my job?",
           "I'm thinking of resigning from work",
           "Will my startup succeed?",
           "Should I become an entrepreneur?",
           "Is my boss going to fire me?")

    expect("money",
           "Will I become rich?",
           "Am I going to be wealthy?",
           "Can I afford a new car?",
           "Will I ever get out of debt?",
           "Am I going bankrupt?",
           "Will my investments pay off?")

    expect("love",
           "Will I get married?",
           "When am I getting married?",
           "Am I going to find a life partner?",
           "Will my marriage survive?",
           "Is my relationship going to work out?",
           "Will we get engaged?")

    expect("family",
           "Will I buy a house?",
           "Did I buy my own house?",
           "Am I going to own a home?",
           "Thinking of buying a house next year",
           "Will I relocate to be near my parents?",
           "How is my relationship with my mother?")

    expect("children",
           "Will I have children?",
           "Am I going to have a baby?",
           "When will I conceive?",
           "Are we going to get pregnant?")

    expect("health",
           "Will I get sick this year?",
           "Am I falling ill often?",
           "Will I recover from my illness?",
           "Am I going to need surgery?")

    expect("education",
           "Will I get admission to a good college?",
           "Did I pass my exams?",
           "Am I studying for the right degree?",
           "Will I get my PhD?")

    expect("travel",
           "Will I move abroad?",
           "Am I migrating this year?",
           "Thinking of relocating overseas",
           "Will I get my visa approved?")

    expect("spirituality",
           "Am I a spiritual person?",
           "Will I find my life's purpose?",
           "Should I start meditating?")

    expect("friends",
           "Will I make new friends?",
           "Who are my true friends?",
           "Will I find a good mentor?")

    expect("obstacles",
           "Why do I keep struggling?",
           "Am I stuck in life?",
           "Will I win my court case?",
           "Are my enemies plotting against me?")

    expect("self",
           "What am I like as a person?",
           "Describe my personality",
           "What are my strengths and weaknesses?")

    expect("timing",
           "What's happening in my life right now?",
           "Which mahadasha am I in?",
           "When does my antardasha change?",
           "Is this a good time for anything important?")

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("topic routing: all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
