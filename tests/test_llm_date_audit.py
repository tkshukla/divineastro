"""Date-auditor regression test.

`_allowed_dates_note()` tells the model which "Mon YYYY" dates it may print,
but that instruction was never actually checked against what the model
returned — a prompt-wording regression could silently reintroduce the exact
"the model did its own date arithmetic" bug that note was added to fix, with
nothing catching it. `_audit_dates()` closes that gap with a log-only,
post-generation scan. This is a pure unit test against that function directly
(no network, no chart, no server) — it doesn't need `provider != "off"`.

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.test_llm_date_audit
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import llm

failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def main() -> int:
    print("LLM date auditor")

    prompt = "The Taurus sub-period runs from Jul 2026 to Jul 2045."

    # Only dates present in the prompt: no violation.
    meta: dict = {}
    llm._audit_dates(meta, prompt, "This window closes in Jul 2045, as noted.")
    check("dates drawn from the prompt raise no violation",
          "date_violations" not in meta, f"got {meta}")

    # A date the model invented via arithmetic on the given range: flagged.
    meta = {}
    llm._audit_dates(meta, prompt, "So you should wait until Sep 2026, when this window closes.")
    check("an invented date is flagged",
          meta.get("date_violations") == ["Sep 2026"], f"got {meta}")

    # meta=None (the default for callers that don't care) must be a no-op,
    # not a crash — polish() and any future caller that skips the audit
    # relies on this.
    try:
        llm._audit_dates(None, prompt, "Sep 2026 appears here too.")
        check("meta=None does not raise", True)
    except Exception as exc:
        check("meta=None does not raise", False, f"{type(exc).__name__}: {exc}")

    # A date that legitimately appears nowhere at all (neither prompt nor a
    # real violation scenario) — sanity check the happy path stays silent.
    meta = {}
    llm._audit_dates(meta, prompt, "This is a plain answer with no dates in it.")
    check("no dates in the answer raises no violation",
          "date_violations" not in meta, f"got {meta}")

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("llm date auditor — all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
