"""Tonight's Reflection: the library, the nightly pick, the post and the CLI.

    ~/.venvs/divineastro/bin/python -u -m tests.test_reflections

The library checks run on the real app/reflections.json; the pick checks use
both the real library (a simulated run of nights) and small fixtures. Nothing
is ever sent: the connector is httpx.MockTransport.
"""

from __future__ import annotations

import contextlib
import datetime as dt
import io
import json
import os
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
_tmp = tempfile.mkdtemp(prefix="astro_reflection_")
os.environ["ASTRO_DAILY_STATE_DIR"] = _tmp
for _k in ("ASTRO_WA_TOKEN", "ASTRO_WA_CHANNEL_LINK", "ASTRO_WA_URL", "ASTRO_REFLECTIONS_FILE"):
    os.environ.pop(_k, None)

import httpx  # noqa: E402

from app import daily_state, reflections as R  # noqa: E402
from app import whatsapp_channel as W  # noqa: E402

failures: list[str] = []
MIN_LIBRARY = 300


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def fresh_state() -> None:
    os.environ["ASTRO_DAILY_STATE_DIR"] = tempfile.mkdtemp(prefix="state_", dir=_tmp)


def run(argv: list[str]) -> tuple[int, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = R.main(argv)
    return code, out.getvalue() + err.getvalue()


def write_lib(items: list[dict]) -> Path:
    p = Path(tempfile.mkdtemp(prefix="lib_", dir=_tmp)) / "reflections.json"
    p.write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")
    return p


# --------------------------------------------------------------------------
# 1. The library
# --------------------------------------------------------------------------

def test_library() -> None:
    print("\n1. Library")
    lib = R.LIBRARY
    raw = json.loads(R.LIBRARY_FILE.read_text(encoding="utf-8"))
    check(f"at least {MIN_LIBRARY} reflections", len(lib) >= MIN_LIBRARY, str(len(lib)))
    ids = [x["id"] for x in raw]
    check("ids unique", len(ids) == len(set(ids)))
    themes = Counter(r.theme for r in lib.values())
    check("every theme used, several times each",
          set(themes) == set(R.THEMES) and min(themes.values()) >= 5, str(themes))
    keys = R.festival_keys()
    dev = re.compile(r"[ऀ-ॿ]")
    latin = re.compile(r"[A-Za-z0-9]")
    bad_en, bad_hi, bad_tags, bad_src = [], [], [], []
    for r in lib.values():
        en, hi = r.en.split("\n"), r.hi.split("\n")
        if not (2 <= len(en) <= 3 and len(r.en) <= 300 and not dev.search(r.en)):
            bad_en.append(r.id)
        if not (2 <= len(hi) <= 3 and dev.search(r.hi) and not latin.search(r.hi)):
            bad_hi.append(r.id)
        if not set(r.tags) <= keys:
            bad_tags.append(r.id)
    for x in raw:
        if "source" in x and not (isinstance(x["source"], str) and x["source"].strip()):
            bad_src.append(x["id"])
    check("en: 2-3 lines, <= 300 chars, no Devanagari", not bad_en, str(bad_en[:5]))
    check("hi: 2-3 lines, Devanagari only", not bad_hi, str(bad_hi[:5]))
    check("tags are festival keys", not bad_tags, str(bad_tags[:5]))
    check("sources non-empty when present", not bad_src, str(bad_src[:5]))
    sourced = sum(1 for r in lib.values() if r.source)
    check("roughly a quarter to a third are quotations/paraphrases",
          0.15 <= sourced / len(lib) <= 0.4, f"{sourced}/{len(lib)}")
    check("no links or WhatsApp markup in any text",
          not any(re.search(r"https?://|[*_~`]", r.en + r.hi) for r in lib.values()))
    for day, rid in R.PINNED.items():
        r = lib.get(rid)
        check(f"pinned {day} -> {rid} exists, from the Gita or an Upanishad",
              r is not None and re.match(r"^(Bhagavad Gita|\w+ Upanishad)", r.source or ""))

    def broken(label: str, item: dict, needle: str) -> None:
        base = {"id": "x-one", "theme": "mind", "en": "One line.\nTwo lines.",
                "hi": "एक पंक्ति।\nदूसरी पंक्ति।"}
        base.update(item)
        base = {k: v for k, v in base.items() if v is not None}
        try:
            R.load(write_lib([base]))
        except R.ReflectionError as exc:
            check(f"rejects {label}", needle in str(exc), str(exc))
        else:
            check(f"rejects {label}", False, "loaded")

    broken("one-line en", {"en": "Only one."}, "2-3")
    broken("four-line hi", {"hi": "क\nख\nग\nघ"}, "2-3")
    broken("Latin in hi", {"hi": "एक line।\nदो।"}, "Devanagari only")
    broken("Devanagari in en", {"en": "One नमस्ते.\nTwo."}, "Devanagari")
    broken("unknown theme", {"theme": "astrology"}, "theme")
    broken("unknown tag", {"tags": ["christmas"]}, "festival keys")
    broken("empty source", {"source": " "}, "source")
    broken("a link", {"en": "See https://x.org\nnow."}, "link")
    broken("bold markup", {"en": "*Bold*\nline."}, "markup")
    broken("too long", {"en": "x" * 200 + "\n" + "y" * 120}, "chars")
    broken("unknown field", {"title": "t"}, "unknown")
    try:
        R.load(write_lib([{"id": "a", "theme": "mind", "en": "a\nb", "hi": "क\nख"}] * 2))
        check("rejects duplicate ids", False)
    except R.ReflectionError as exc:
        check("rejects duplicate ids", "duplicate" in str(exc))


# --------------------------------------------------------------------------
# 2. The pick
# --------------------------------------------------------------------------

def simulate(start: dt.date, nights: int, lib=None) -> list[tuple[dt.date, str]]:
    lib = R.LIBRARY if lib is None else lib
    posted: dict[str, dt.date] = {}
    out = []
    for i in range(nights):
        day = start + dt.timedelta(days=i)
        rid = R.pick(day, lib, posted)
        out.append((day, rid))
        posted[rid] = day
    return out


def test_pick() -> None:
    print("\n2. Pick")
    lib = R.LIBRARY
    check("2026-10-04 is pinned to the Gita", R.pick(dt.date(2026, 10, 4), posted={})
          == R.PINNED["2026-10-04"])
    check("a pin wins even when already posted",
          R.pick(dt.date(2026, 10, 4), posted={R.PINNED["2026-10-04"]: dt.date(2026, 10, 4)})
          == R.PINNED["2026-10-04"])

    # Karwa Chauth 2026-10-29, Dussehra 2026-10-20, Diwali 2026-11-08 (New Delhi).
    for day, key in ((dt.date(2026, 10, 29), "karwa_chauth"), (dt.date(2026, 10, 20), "dussehra"),
                     (dt.date(2026, 11, 8), "diwali")):
        rid = R.pick(day, posted={})
        check(f"{day}: a {key} reflection", key in lib[rid].tags, rid)
        tagged = [r.id for r in lib.values() if key in r.tags]
        recent = {t: day - dt.timedelta(days=10) for t in tagged}
        rid2 = R.pick(day, posted=recent)
        check(f"{day}: not repeated within 300 days", key not in lib[rid2].tags, rid2)
        old = {t: day - dt.timedelta(days=R.FESTIVAL_GAP_DAYS + 1) for t in tagged}
        others = {r.id: day - dt.timedelta(days=5) for r in lib.values()
                  if r.tags and r.id not in tagged}
        check(f"{day}: allowed again after 300 days",
              key in lib[R.pick(day, posted={**others, **old})].tags)

    plain = dt.date(2026, 10, 5)
    check("an ordinary night gets an evergreen reflection", not lib[R.pick(plain, posted={})].tags)
    check("rotation starts near the head of the shuffled order",
          R.pick(plain, posted={}) in R.rotation(lib)[:3])
    check("the rotation is deterministic", R.rotation(lib) == R.rotation(dict(lib)))
    check("the rotation is shuffled (not file order)",
          R.rotation(lib)[:10] != [r.id for r in lib.values() if not r.tags][:10])

    run_ = simulate(dt.date(2026, 10, 5), 120)
    themes = [lib[rid].theme for _d, rid in run_]
    same = [(run_[i][0], themes[i]) for i in range(1, len(themes)) if themes[i] == themes[i - 1]]
    check("120 nights: never the same theme two nights running", not same, str(same[:3]))
    ids = [rid for _d, rid in run_]
    check("120 nights: no reflection repeated", len(ids) == len(set(ids)))
    check("120 nights: festival reflections land on their days",
          all(set(lib[rid].tags) & {o["key"] for o in R._observances(d)}
              for d, rid in run_ if lib[rid].tags))
    check("120 nights: at least 15 themes", len(set(themes)) >= 15, str(len(set(themes))))

    evergreen = [r.id for r in lib.values() if not r.tags]
    long_run = simulate(dt.date(2027, 1, 1), len(evergreen) + 120)
    seq = [rid for _d, rid in long_run if not lib[rid].tags]
    first_cycle = seq[:len(evergreen)]
    check("no evergreen repeats until all have been posted",
          len(set(first_cycle)) == len(first_cycle) == len(evergreen),
          f"{len(set(first_cycle))}/{len(evergreen)}")
    after = seq[len(evergreen):]
    check("then the least recently posted come back first",
          len(after) >= 5 and all(x in first_cycle[:10] for x in after[:5]), str(after[:5]))

    # Fixtures: theme rule and festival fallbacks in isolation.
    def item(i: str, theme: str, tags=()) -> dict:
        d = {"id": i, "theme": theme, "en": "One.\nTwo.", "hi": "एक।\nदो।"}
        if tags:
            d["tags"] = list(tags)
        return d
    fx = R.load(write_lib([item("a1", "mind"), item("a2", "mind"), item("b1", "fear"),
                           item("k1", "mind", ["karwa_chauth"]),
                           item("k2", "fear", ["karwa_chauth"])]))
    day = dt.date(2026, 10, 29)
    check("festival: the one whose theme differs from last night's",
          R.pick(day, fx, {"a1": day - dt.timedelta(days=1)}) == "k2")
    check("festival: file order otherwise", R.pick(day, fx, {}) == "k1")
    check("tagged reflections stay out of the ordinary rotation",
          set(R.rotation(fx)) == {"a1", "a2", "b1"})
    d2 = dt.date(2026, 10, 5)
    got = R.pick(d2, fx, {"b1": d2 - dt.timedelta(days=1), "a1": d2 - dt.timedelta(days=2)})
    check("evergreen: never-posted first, even against the recent-theme preference",
          got == "a2", got)
    got = R.pick(d2, fx, {"a2": d2 - dt.timedelta(days=1), "a1": d2 - dt.timedelta(days=30),
                         "b1": d2 - dt.timedelta(days=20)})
    check("exhausted: least recently posted with a different theme", got == "b1", got)
    check("empty library: None", R.pick(d2, {}, {}) is None)


# --------------------------------------------------------------------------
# 3. The post
# --------------------------------------------------------------------------

def test_post() -> None:
    print("\n3. Post")
    r = R.LIBRARY["gita-2-47"]
    text = R.post_text(r)
    expect = "\n\n".join(["*🌙 आज रात का विचार · Tonight's Reflection*", r.en, r.hi,
                          "_— Bhagavad Gita 2.47_", "🙏 शुभ रात्रि · Good night"])
    check("format: header, en, hi, source, good night", text == expect, text)
    plain = next(x for x in R.LIBRARY.values() if not x.source)
    t2 = R.post_text(plain)
    check("no source line without a source", "_—" not in t2 and t2.endswith("Good night"))
    check("no links in any post",
          not any("http" in R.post_text(x) for x in R.LIBRARY.values()))
    check("every post well inside WhatsApp's limit",
          max(len(R.post_text(x)) for x in R.LIBRARY.values()) < 1000)


# --------------------------------------------------------------------------
# 4. The CLI
# --------------------------------------------------------------------------

class Stub:
    """The wa connector: connected, one channel, records posts."""

    def __init__(self, post_status: int = 200, connected: bool = True):
        self.posts: list[dict] = []
        self.post_status, self.connected = post_status, connected

    def __call__(self, req: httpx.Request) -> httpx.Response:
        if req.url.path == "/status":
            return httpx.Response(200, json={"connected": self.connected,
                                             "reason": None if self.connected else "logged_out"})
        if req.url.path == "/channel/resolve":
            return httpx.Response(200, json={"jid": "123@newsletter", "name": "Divine Astro",
                                             "role": "OWNER"})
        if req.url.path == "/channel/post":
            if self.post_status != 200:
                return httpx.Response(self.post_status, json={"error": "nope"})
            self.posts.append(json.loads(req.content))
            return httpx.Response(200, json={"id": f"M{len(self.posts)}"})
        return httpx.Response(404, json={})


def _exits(fn) -> bool:
    try:
        with contextlib.redirect_stderr(io.StringIO()):
            fn()
    except SystemExit as exc:
        return exc.code == 2
    return False


def test_cli() -> None:
    print("\n4. CLI")
    env = {"ASTRO_WA_TOKEN": "secret-token", "ASTRO_WA_CHANNEL_LINK":
           "https://whatsapp.com/channel/ABC", "ASTRO_WA_URL": "http://wa:3000",
           "ASTRO_WA_WAIT": "0"}
    alerts: list[str] = []
    gita = R.LIBRARY["gita-2-47"]
    karwa = R.pick(dt.date(2026, 10, 29), posted={})
    with patch.object(W, "alert_owner", lambda reason, day: alerts.append(reason)):
        fresh_state()
        code, out = run(["--daily", "--date", "2026-10-04", "--dry-run"])
        check("--daily --dry-run on 4 Oct shows the pinned Gita post",
              code == 0 and "reflection gita-2-47" in out and R.post_text(gita) in out, out[:300])
        check("dry run records nothing", daily_state.sent("reflection", dt.date(2026, 10, 4)) == {})
        code, out = run(["--id", "dhammapada-5", "--dry-run"])
        check("--id --dry-run prints that one", code == 0 and "Dhammapada 5" in out)
        check("--id unknown: exit 2", run(["--id", "nope"])[0] == 2)
        check("needs --daily or --id (argparse exit 2)", _exits(lambda: run([])))
        check("bad --date: exit 2", run(["--daily", "--date", "04-10-2026"])[0] == 2)
        code, out = run(["--daily", "--date", "2026-10-04"])
        check("not configured: exit 2", code == 2 and "ASTRO_WA_TOKEN" in out, out)

        stub = Stub()
        with patch.dict(os.environ, env), patch.object(W, "_transport", httpx.MockTransport(stub)):
            code, out = run(["--daily", "--date", "2026-10-04"])
            check("--daily posts the pick", code == 0 and len(stub.posts) == 1, out)
            p = stub.posts[0] if stub.posts else {}
            check("posted the Gita reflection to the channel, text only",
                  p.get("jid") == "123@newsletter" and p.get("text") == R.post_text(gita)
                  and "image_base64" not in p)
            rec = daily_state.sent("reflection", dt.date(2026, 10, 4)).get("post")
            hist = daily_state.recall("reflection", "gita-2-47")
            check("recorded per date and per id",
                  rec == {"reflection": "gita-2-47", "id": "M1"} and isinstance(hist, dict)
                  and hist.get("day") == "2026-10-04", f"{rec} {hist}")
            check("the history feeds pick()",
                  R.history() == {"gita-2-47": dt.date(2026, 10, 4)})
            code, out = run(["--daily", "--date", "2026-10-04"])
            check("second run the same date: nothing sent, exit 0",
                  code == 0 and len(stub.posts) == 1 and "already posted" in out, out)
            code, out = run(["--daily", "--date", "2026-10-04", "--dry-run"])
            check("dry run after posting shows what went out",
                  code == 0 and "gita-2-47" in out and "[already posted]" in out)
            code, out = run(["--daily", "--date", "2026-10-04", "--force"])
            check("--force re-sends the same date's post",
                  code == 0 and len(stub.posts) == 2 and stub.posts[1]["text"] == p.get("text"))
            code, out = run(["--daily", "--date", "2026-10-29"])
            check("a festival night posts its reflection",
                  code == 0 and stub.posts[-1]["text"] == R.post_text(R.LIBRARY[karwa]), out)
            code, out = run(["--daily", "--date", "2026-10-05"])
            nxt = daily_state.sent("reflection", dt.date(2026, 10, 5)).get("post", {})
            check("next night: a different reflection",
                  code == 0 and nxt.get("reflection") not in ("gita-2-47", karwa), str(nxt))
            code, out = run(["--id", "gita-2-47"])
            check("--id of an already-posted one: nothing sent",
                  code == 0 and len(stub.posts) == 4 and "already posted" in out, out)
            code, out = run(["--id", "dhammapada-5"])
            check("--id posts that one", code == 0 and len(stub.posts) == 5
                  and "Dhammapada 5" in stub.posts[-1]["text"])
            check("--id leaves the per-date record alone",
                  set(daily_state.load("reflection")) == {"2026-10-04", "2026-10-05",
                                                          "2026-10-29"})
            check("token never printed", "secret-token" not in out)

        stub = Stub(post_status=409)
        with patch.dict(os.environ, env), patch.object(W, "_transport", httpx.MockTransport(stub)):
            code, out = run(["--daily", "--date", "2026-10-31"])
            check("connector unlinked mid-send: exit 1, owner alerted",
                  code == 1 and len(alerts) == 1, out)
            check("a failed post is not recorded",
                  daily_state.sent("reflection", dt.date(2026, 10, 31)) == {})
        stub = Stub(connected=False)
        with patch.dict(os.environ, env), patch.object(W, "_transport", httpx.MockTransport(stub)):
            code, out = run(["--daily", "--date", "2026-10-31"])
            check("connector not linked: exit 1, owner alerted",
                  code == 1 and len(alerts) == 2 and not stub.posts, out)
        stub = Stub(post_status=502)
        with patch.dict(os.environ, env), patch.object(W, "_transport", httpx.MockTransport(stub)):
            code, out = run(["--daily", "--date", "2026-10-31"])
            check("send failure: exit 1, no alert", code == 1 and len(alerts) == 2, out)

    # The real alert_owner shares whatsapp_channel's once-a-day record.
    fresh_state()
    sent: list[tuple] = []
    with patch.dict(os.environ, env), \
            patch.object(W, "_transport", httpx.MockTransport(Stub(connected=False))), \
            patch.object(W.whatsapp_pack, "recipients", lambda: ["owner@example.com"]), \
            patch.object(W.mail, "send", lambda to, subj, body: sent.append((to, subj)) or True):
        daily_state.mark(W.ALERT_JOB, dt.date(2026, 10, 31), "email")
        code, out = run(["--daily", "--date", "2026-10-31"])
        check("no second alert on a day the morning post already alerted",
              code == 1 and not sent and "already alerted" in out, out)


def main() -> int:
    test_library()
    test_pick()
    test_post()
    test_cli()
    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("reflections: all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
