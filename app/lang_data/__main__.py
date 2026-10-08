"""python -m app.lang_data skeleton <code> [--force] | check <code> [--live] [--only ...] [--all]"""

from __future__ import annotations

import argparse
import sys

from . import NEW_CODES, READY_KEYS


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m app.lang_data", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sk = sub.add_parser("skeleton", help="write app/lang_data/<code>.py, app/astro/names_<code>.py, static/i18n/<code>.json")
    sk.add_argument("code")
    sk.add_argument("--force", action="store_true", help="overwrite files that differ from a fresh skeleton")
    ck = sub.add_parser("check", help="completeness / placeholders / script report (exit 0 = complete)")
    ck.add_argument("code")
    ck.add_argument("--only", help="comma list of: " + ", ".join(READY_KEYS) + ", akshar, names, json")
    ck.add_argument("--live", action="store_true",
                    help="read the live shared tables instead of app/lang_data/<code>.py "
                         "(validates an older language such as kn)")
    ck.add_argument("--all", action="store_true", help="list every problem, not the first 8 per table")
    ck.add_argument("--quiet", action="store_true", help="only the tables with problems")
    args = ap.parse_args(argv)

    if args.cmd == "skeleton":
        from . import skeleton
        print(f"skeleton {args.code}")
        return 1 if skeleton.write(args.code, force=args.force) else 0

    from . import check
    only = [x.strip() for x in args.only.split(",")] if args.only else None
    results = check.check_language(args.code, source="live" if args.live else "module", only=only)
    print(f"check {args.code}" + (" (live tables)" if args.live else ""))
    problems = check.report(args.code, results, limit=10 ** 6 if args.all else 8, quiet=args.quiet)
    notes = [] if args.live or only else check.ready_problems(args.code, results)
    for line in notes:
        print(f"  FAIL  {line}")
    done = sum(1 for r in results if r.ok and not r.skipped)
    print(f"{done}/{len(results)} tables complete; {problems} problem(s)" + (f"; {len(notes)} READY inconsistency" if notes else ""))
    if args.code in NEW_CODES and not problems and not notes:
        from . import load
        mod = load(args.code)
        print("READY =", sorted(getattr(mod, "READY", ()) if mod else ()))
    return 1 if (problems or notes) else 0


if __name__ == "__main__":
    sys.exit(main())
