"""Topic-classification regression test: verb-form phrasings.

`classify()`'s keyword matcher only strips one trailing e/y (`_stem()`), so a
keyword list that names a noun ("promotion") does not automatically cover its
verb forms ("promoted", "promote") — the exact gap that once sent "list of
mahadasha and its time" to the wrong topic before the dasha vocabulary was
spelled out explicitly (see topics.py). This file enumerates the same class
of phrasing per topic so a future keyword-list edit that reintroduces the gap
fails a test instead of silently misrouting real questions.

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.test_topic_routing
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.interpret.topics import classify

failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


# (question, expected topic key) — each pair exercises a verb/inflected form
# of a keyword the topic's strong_keywords list names only as a noun.
CASES = [
    ("will I get promoted", "career"),
    ("when will I get promoted", "career"),
    ("will I be promoted this year", "career"),
    ("when will I get a promotion", "career"),
    ("will I get married", "love"),
    ("when will I marry", "love"),
    ("am I going to marry soon", "love"),
    ("will we divorce", "love"),
    ("when did I get divorced", "love"),
]


def main() -> int:
    print("Topic routing — verb-form regression")
    for question, expected in CASES:
        r = classify(question)
        check(f"{question!r} -> {expected}", r.topic.key == expected,
              f"got {r.topic.key!r} (matched={r.matched})")

    # The false-positive this session also found: a bare "art" keyword
    # matching "article" via the \w{0,4} inflection tail on _hits' regex.
    r = classify("I read an interesting article about vedic astrology")
    check("'article' does not false-positive into children/creativity",
          r.topic.key != "children", f"got {r.topic.key!r} (matched={r.matched})")

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("topic routing — all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
