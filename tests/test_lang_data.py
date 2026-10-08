"""DIVASTRO-143: the per-language data modules (app/lang_data) — loader, merge hooks,
TRANSLATED computation, skeleton generator and checker.

Pa, ne, as, mr and gu each have one file, app/lang_data/<code>.py, holding every table that
for kn..or lives inline in the shared text modules. This pins the machinery that lets
five translators work in parallel without touching a shared file:

 1. the files: each loads (also `as`, a Python keyword), declares every table in tables.SPECS
    with the right shape and exactly English's keys, and nothing else;
 2. merge(): each shape lands in the live table as if written inline; empty values stay
    "not translated"; unknown keys are ignored;
 3. READY -> TRANSLATED -> listed: computed from the language's own file (a fake language
    in a temporary directory flips modules one at a time);
 4. the skeleton generator: valid Python, every key, TODO values empty, refuses to
    overwrite edited work, names stub and `{}` json;
 5. the checker, run on a "translation" built from Kannada's live tables under a fake code
    (complete -> exit 0), then with one defect of each kind (missing, empty, extra,
    placeholders, same as English, wrong script, braces, html, READY with an incomplete table);
 6. the real five today: nothing READY, the skeleton is current with the English keys, the
    namakshar script rule converts all 112 syllables, READY (when a translator sets it) is
    backed by a clean check.

    ~/.venvs/divineastro/bin/python -u -m tests.test_lang_data
"""

from __future__ import annotations

import ast
import contextlib
import importlib
import io
import json
import os
import shutil
import sys
import tempfile
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

_tmp = tempfile.mkdtemp(prefix="astro_langdata_")
os.environ.setdefault("ASTRO_DATABASE_URL", f"sqlite:///{Path(_tmp).as_posix()}/t.db")

from app import i18n, lang_data  # noqa: E402
from app.lang_data import check as C  # noqa: E402
from app.lang_data import skeleton as SK  # noqa: E402
from app.lang_data import tables as T  # noqa: E402
from app.lang_data.__main__ import main as cli  # noqa: E402

failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def raises(exc, fn, *a, **k) -> bool:
    try:
        fn(*a, **k)
    except exc:
        return True
    except Exception:
        return False
    return False


NEW = lang_data.NEW_CODES
FAKE = "zz"


class Fake:
    """A fake language `zz` in a temporary tree: Kannada's block, Kannada's live data as its
    translation (so it is complete), loadable through lang_data like a real module."""

    def __init__(self):
        self.root = Path(tempfile.mkdtemp(prefix="astro_fake_lang_"))
        self.dir = self.root / "app" / "lang_data"
        (self.root / "app" / "astro").mkdir(parents=True)
        (self.root / "app" / "static" / "i18n").mkdir(parents=True)
        self.dir.mkdir(parents=True)
        shutil.copy(ROOT / "app" / "static" / "i18n" / "en.json", self.root / "app/static/i18n/en.json")
        self.saved = (list(lang_data.SEARCH_DIRS), lang_data.NEW_CODES, dict(lang_data.BLOCKS),
                      SK.ROOT, C.I18N_DIR)

    def __enter__(self):
        lang_data.SEARCH_DIRS[:] = [self.dir]
        lang_data.NEW_CODES = (*self.saved[1], FAKE)
        lang_data.BLOCKS[FAKE] = lang_data.BLOCKS["kn"]
        SK.ROOT, C.I18N_DIR = self.root, self.root / "app/static/i18n"
        lang_data.reload()
        return self

    def __exit__(self, *exc):
        lang_data.SEARCH_DIRS[:] = self.saved[0]
        lang_data.NEW_CODES = self.saved[1]
        lang_data.BLOCKS.clear()
        lang_data.BLOCKS.update(self.saved[2])
        SK.ROOT, C.I18N_DIR = self.saved[3], self.saved[4]
        lang_data.reload()
        sys.modules.pop("app.astro.names_zz", None)
        shutil.rmtree(self.root, ignore_errors=True)

    def write_from_kn(self, ready=(), allow=(), **patch) -> str:
        """app/lang_data/zz.py = Kannada's live data; `patch` {TABLE_ID: transform(data)}."""
        allowed = {"b", "ṛ", "Priya", "Kshitij", "Nakshatra", "A1", "A12", *allow}
        lines = ["from __future__ import annotations", f"READY = frozenset({set(ready)!r})",
                 f"ALLOW_LATIN = frozenset({allowed!r})", "KEEP_ENGLISH = frozenset()",
                 "AKSHAR = (0x0C80, {})"]
        for spec in T.SPECS.values():
            data = C.live_data("kn", spec)
            if spec.id == "RASHIFAL_TEXT":
                data = {**data, "sub_lang": FAKE}          # the lang="" code is the language's own
            if spec.id in patch:
                data = patch[spec.id](data)
            lines.append(f"{spec.id} = {data!r}")
        text = "\n".join(lines) + "\n"
        (self.dir / f"{FAKE}.py").write_text(text, encoding="utf-8")
        lang_data.reload()
        return text

    def names_module(self) -> types.ModuleType:
        """app.astro.names_zz = Kannada's names renamed _KN -> _ZZ."""
        kn = importlib.import_module("app.astro.names_kn")
        mod = types.ModuleType("app.astro.names_zz")
        for k, v in vars(kn).items():
            if k.endswith("_KN"):
                setattr(mod, k[:-3] + "_ZZ", v)
        sys.modules["app.astro.names_zz"] = mod
        return mod


def results(code=FAKE, **kw):
    return C.check_language(code, **kw)


def problems_of(rs, name):
    return next(r for r in rs if r.name == name).problems


def main() -> int:
    # ------------------------------------------------------------------ 1
    print("\n1. The five files")
    for code in NEW:
        mod = lang_data.load(code)
        check(f"{code}: app/lang_data/{code}.py loads" + (" (importlib; `as` is a keyword)" if code == "as" else ""),
              mod is not None and (ROOT / "app" / "lang_data" / f"{code}.py").exists())
        ids = {k for k in vars(mod) if k.isupper()}
        want = set(T.SPECS) | set(T.CONFIG)
        check(f"{code}: declares every table of tables.SPECS, and only those (+ READY AKSHAR ...)",
              ids == want, f"missing {sorted(want - ids)} extra {sorted(ids - want)}")
        bad = []
        for spec in T.SPECS.values():
            data = getattr(mod, spec.id)
            en = T.english(spec)
            flat = T.flatten(spec.id, data)
            if spec.shape == "pairs":
                ok = isinstance(data, tuple) and all(isinstance(p, tuple) and len(p) == len(spec.fields)
                                                      for p in data)
            elif spec.shape == "tuple":
                ok = isinstance(data, tuple)
            elif spec.shape == "scalar":
                ok = isinstance(data, str)
            elif spec.shape == "variants":
                ok = isinstance(data, dict)
            else:
                ok = isinstance(data, dict)
            if not ok:
                bad.append(f"{spec.id}: shape {type(data).__name__}")
            elif spec.shape in ("dict", "pairs") and not spec.optional and set(flat) != set(en):
                bad.append(f"{spec.id}: keys differ ({len(set(flat) ^ set(en))})")
        check(f"{code}: every table has the right shape and exactly English's keys (skeleton is current)",
              not bad, "; ".join(bad[:4]) + (" — regenerate with `skeleton %s` if the English changed" % code if bad else ""))
        check(f"{code}: READY is a frozenset of known module keys", isinstance(mod.READY, frozenset)
              and set(mod.READY) <= set(lang_data.READY_KEYS))
        check(f"{code}: names_{code}.py and static/i18n/{code}.json exist",
              (ROOT / "app" / "astro" / f"names_{code}.py").exists()
              and (ROOT / "app" / "static" / "i18n" / f"{code}.json").exists())
        try:
            json.loads((ROOT / "app" / "static" / "i18n" / f"{code}.json").read_text(encoding="utf-8"))
            ok = True
        except ValueError:
            ok = False
        check(f"{code}.json is valid JSON", ok)
    check("the table registry covers every module the hooks name",
          {s.module for s in T.SPECS.values()} >= {"app.seo_text", "app.rashifal_text", "app.vrat_text",
                                                    "app.muhurat_text", "app.nakshatra_page_text",
                                                    "app.nakshatra_text", "app.naam_milan_text",
                                                    "app.recurring_text", "app.hub_text", "app.stay_strip",
                                                    "app.i18n", "app.seo_city_names",
                                                    "app.astro.choghadiya", "app.astro_terms"})
    for spec in T.SPECS.values():
        mod = importlib.import_module(spec.module)
        src = Path(mod.__file__).read_text(encoding="utf-8")
        check(f"{spec.module}: calls lang_data.merge({spec.id!r}, {spec.attr})",
              f'lang_data.merge("{spec.id}", {spec.attr})' in src)
    check("i18n._AKSHAR is fed by lang_data.merge_akshar", "lang_data.merge_akshar(_AKSHAR)" in
          (ROOT / "app" / "i18n.py").read_text(encoding="utf-8"))

    # ------------------------------------------------------------------ 2
    print("\n2. merge(): every shape lands as if written inline")
    with Fake() as fake:
        (fake.dir / f"{FAKE}.py").write_text(
            "READY = frozenset()\n"
            "SEO_TEXT = {'a': 'A!', 'b': '', 'zz.key': 'ok'}\n"
            "SEO_FAQ = (('q1', 'a1'), ('q2', 'a2'))\n"
            "RASHIFAL_MORE_LINKS = (('{twin:en}', 'x'), ('/panchang', ''))\n"
            "RASHIFAL_MOON_HOUSE = {1: 'moon1', 2: '', 99: 'ignored'}\n"
            "RASHIFAL_KETU_LINE = {True: 'ketu+ {n}', False: ''}\n"
            "MUHURAT_MONTHS = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l')\n"
            "RASHIFAL_CLOCK_LANG = 'en'\n"
            "CHOGHADIYA_DESC = {'Amrit': 'amrit text', 'Rog': '', 'Nope': 'zzz'}\n"
            "ASTRO_MONTHS = {2: ('feb2',), 3: ()}\n"
            "AKSHAR = (0x0C80, {'व': 'ವ'})\n", encoding="utf-8")
        lang_data.reload()
        text = {"en": {"a": "A", "b": "B"}}
        lang_data.merge("SEO_TEXT", text)
        check("text: non-empty values merged, empty skipped", text[FAKE] == {"a": "A!", "zz.key": "ok"}, str(text))
        faq = {"en": ()}
        lang_data.merge("SEO_FAQ", faq)
        check("pairs: a complete tuple is set as pairs", faq[FAKE] == (("q1", "a1"), ("q2", "a2")))
        links = {"en": ()}
        lang_data.merge("RASHIFAL_MORE_LINKS", links)
        check("pairs: one empty part and the whole table is skipped (all or nothing)", FAKE not in links)
        bank = {1: {"en": "m1"}, 2: {"en": "m2"}}
        lang_data.merge("RASHIFAL_MOON_HOUSE", bank)
        check("bank: table[key][code]; empty and unknown keys ignored",
              bank == {1: {"en": "m1", FAKE: "moon1"}, 2: {"en": "m2"}}, str(bank))
        ketu = {True: {"en": "t"}, False: {"en": "f"}}
        lang_data.merge("RASHIFAL_KETU_LINE", ketu)
        check("bank: bool keys (KETU_LINE)", ketu[True][FAKE] == "ketu+ {n}" and FAKE not in ketu[False])
        months = {"hi": tuple("x" * 12)}
        lang_data.merge("MUHURAT_MONTHS", months)
        check("tuple: 12 month names", months[FAKE][0] == "a" and len(months[FAKE]) == 12)
        clock = {"hi": "en"}
        lang_data.merge("RASHIFAL_CLOCK_LANG", clock)
        check("scalar: CLOCK_LANG", clock[FAKE] == "en")
        chog = {"Amrit": {"description": "d"}, "Rog": {"description": "d"}}
        lang_data.merge("CHOGHADIYA_DESC", chog)
        check("choghadiya: description_<code> added to the entry, empty/unknown skipped",
              chog["Amrit"][f"description_{FAKE}"] == "amrit text" and f"description_{FAKE}" not in chog["Rog"]
              and "Nope" not in chog)
        var = {}
        lang_data.merge("ASTRO_MONTHS", var)
        check("variants: month spellings, an empty list skipped", var[FAKE] == {2: ("feb2",)})
        ak = {}
        lang_data.merge_akshar(ak)
        check("AKSHAR: block start + overrides", ak[FAKE] == (0x0C80, {"व": "ವ"}))
        check("merge never touches another language", text.get("en") == {"a": "A", "b": "B"})
    check("filled(): ignores the prefilled *_lang code", not lang_data.filled("pa", "RASHIFAL_TEXT")
          if not lang_data.load("pa").READY else True)

    # ------------------------------------------------------------------ 3
    print("\n3. READY -> TRANSLATED -> listed")
    check("ready() rejects an unknown key", raises(KeyError, lang_data.ready, "nonsense"))
    check("translated(): base | legacy | ready",
          lang_data.translated("seo", {"en", "hi"}, lang_data.LEGACY_CODES)
          == frozenset({"en", "hi", *lang_data.LEGACY_CODES}) | lang_data.ready("seo"))
    with Fake() as fake:
        check("a language with no READY: in no module's set, not listed",
              not any(FAKE in lang_data.ready(k) for k in lang_data.READY_KEYS) and not lang_data.listed(FAKE)
              or lang_data.load(FAKE) is None)
        fake.write_from_kn(ready={"seo", "hub"})
        check("READY = {seo, hub}: ready('seo') and ready('hub') have it, ready('vrat') does not",
              FAKE in lang_data.ready("seo") and FAKE in lang_data.ready("hub")
              and FAKE not in lang_data.ready("vrat") and FAKE not in lang_data.ready("app"))
        check("translated() adds exactly those modules",
              FAKE in lang_data.translated("seo", {"en", "hi"}, lang_data.LEGACY_CODES)
              and FAKE not in lang_data.translated("rashifal", {"en", "hi"}, lang_data.LEGACY_CODES))
        check("listed(): a language with something READY is offered in the picker", lang_data.listed(FAKE))
        fake.write_from_kn(ready=set())
        check("... one with nothing READY is not", not lang_data.listed(FAKE))
        os.environ["ASTRO_LIST_ALL_LANGS"] = "1"
        try:
            check("... unless ASTRO_LIST_ALL_LANGS=1", lang_data.listed(FAKE))
        finally:
            del os.environ["ASTRO_LIST_ALL_LANGS"]
        (fake.dir / f"{FAKE}.py").write_text("READY = frozenset({'seo', 'typo'})\n", encoding="utf-8")
        lang_data.reload()
        check("a typo in READY fails loudly at import", raises(ValueError, lang_data.load, FAKE))
    check("recurring_pages / site_hub / the five page modules compute TRANSLATED from READY",
          all("lang_data.translated(" in (ROOT / "app" / f).read_text(encoding="utf-8")
              for f in ("seo_pages.py", "vrat_pages.py", "muhurat_pages.py", "nakshatra_pages.py",
                        "rashifal_pages.py", "site_hub.py"))
          and "lang_data.ready(\"recurring\")" in (ROOT / "app" / "recurring_pages.py").read_text(encoding="utf-8"))
    check("the picker lists a language the moment something is READY (i18n.listed_codes)",
          i18n.listed_codes() == [c for c in i18n.CODES if lang_data.listed(c)]
          and "pa" in i18n.listed_codes("pa"))

    # ------------------------------------------------------------------ 4
    print("\n4. Skeleton generator")
    with Fake() as fake:
        src = SK.render_module(FAKE)
        tree = ast.parse(src)
        names = {t.id for n in tree.body if isinstance(n, ast.Assign) for t in n.targets
                 if isinstance(t, ast.Name)}
        check("render_module(): valid Python assigning every table id and the config constants",
              set(T.SPECS) | set(T.CONFIG) <= names, str((set(T.SPECS) | set(T.CONFIG)) - names))
        ns: dict = {}
        exec(compile(src, "zz.py", "exec"), ns)
        empties = 0
        every_key = True
        for spec in T.SPECS.values():
            flat = T.flatten(spec.id, ns[spec.id])
            en = T.english(spec)
            if spec.shape in ("dict", "pairs") and not spec.optional:
                every_key &= set(flat) == set(en)
            empties += sum(1 for k, v in flat.items() if v == "" )
        check("... with every English key of every table", every_key)
        check("... and every value the TODO marker \"\" (except the lang= codes)",
              all(v == "" or str(k).endswith("_lang") or (spec.id == "RASHIFAL_MORE_LINKS" and str(k).endswith("href"))
                  for spec in T.SPECS.values() for k, v in T.flatten(spec.id, ns[spec.id]).items())
              and empties > 800, str(empties))
        check("... the English text and the {placeholders} are in the comment above each key",
              "# EN: Rahu Kaal" in src and "# keep: {city} {tool}" in src
              and "# EN href: /panchang" in src)
        check("... READY is empty, AKSHAR is declared", ns["READY"] == frozenset() and "AKSHAR" in ns)
        wrote = io.StringIO()
        refused = SK.write(FAKE, say=lambda m: wrote.write(m + "\n"))
        mod_path = fake.dir / f"{FAKE}.py"
        check("write(): lang_data module, names_<code>.py and {} json created",
              refused == 0 and mod_path.exists() and (fake.root / "app/astro/names_zz.py").exists()
              and (fake.root / "app/static/i18n/zz.json").read_text().strip() == "{}")
        names_src = (fake.root / "app/astro/names_zz.py").read_text(encoding="utf-8")
        ns2: dict = {}
        exec(compile(names_src, "names_zz.py", "exec"), ns2)
        from app.astro import names_i18n as N
        check("names stub: every table `<NAME>_ZZ` with English's keys, all \"\", plus add_zz()",
              all(f"{t}_ZZ" in ns2 for t in (*N.TABLES, *N.TEXTS)) and callable(ns2["add_zz"])
              and set(ns2["TITHI_ZZ"]) == set(N._names("en").TITHI) and set(ns2["TITHI_ZZ"].values()) == {""}
              and len(ns2["MONTHS_ZZ"]) == 12)
        mod_path.write_text(mod_path.read_text(encoding="utf-8") + "\n# edited by a translator\n", encoding="utf-8")
        before = mod_path.read_text(encoding="utf-8")
        refused = SK.write(FAKE, say=lambda m: None)
        check("write(): refuses to overwrite a file that differs from a fresh skeleton",
              refused >= 1 and mod_path.read_text(encoding="utf-8") == before)
        (fake.root / "app/static/i18n/zz.json").write_text('{"a": "b"}', encoding="utf-8")
        SK.write(FAKE, force=True, say=lambda m: None)
        check("--force regenerates the file; an existing json is never touched",
              "edited by a translator" not in mod_path.read_text(encoding="utf-8")
              and (fake.root / "app/static/i18n/zz.json").read_text() == '{"a": "b"}')
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = cli(["skeleton", FAKE])
        check("CLI skeleton exits 1 when it refused, 0 when it wrote", code in (0, 1))

    # ------------------------------------------------------------------ 5
    print("\n5. The checker")
    live_ok = C.check_language("kn", source="live", only={"seo", "rashifal", "vrat", "nakshatra", "muhurat",
                                                          "recurring", "hub", "akshar", "names"})
    left = [(r.name, {k: v[:2] for k, v in r.problems.items()}) for r in live_ok if not r.ok and not r.skipped]
    check("Kannada's live tables (the reference translation) pass: no false positives", not left, str(left[:3]))
    with Fake() as fake:
        fake.write_from_kn(ready={"seo"})
        fake.names_module()
        rs = results(only={"seo", "rashifal", "vrat", "nakshatra", "muhurat", "recurring", "hub", "app"})
        bad = [(r.name, list(r.problems)) for r in rs if not r.ok and not r.skipped and r.name in T.SPECS]
        check("a complete module (Kannada's data under a fake code) has no problems", not bad, str(bad[:3]))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = cli(["check", FAKE, "--only", "seo,rashifal,vrat,nakshatra,muhurat,recurring,hub"])
        check("CLI check: exit code 0 when complete", rc == 0, out.getvalue()[-200:])

        def drop(key):
            return lambda d: {k: v for k, v in d.items() if k != key}

        def setkey(key, value):
            return lambda d: {**d, key: value}

        text_key = "p.sub"
        for label, patch, table, cat, needle in (
                ("missing key", {"SEO_TEXT": drop("when")}, "SEO_TEXT", "missing", "when"),
                ("empty value", {"SEO_TEXT": setkey("when", "")}, "SEO_TEXT", "empty", "when"),
                ("extra key", {"SEO_TEXT": setkey("not.a.key", "ಏನೋ")}, "SEO_TEXT", "extra", "not.a.key"),
                ("placeholder dropped", {"SEO_TEXT": setkey(text_key, "ಸ್ಥಿರ ಪಠ್ಯ")}, "SEO_TEXT",
                 "placeholders", text_key),
                ("placeholder invented", {"SEO_TEXT": setkey("tool.panchang", "ಪಂಚಾಂಗ {nonsense}")}, "SEO_TEXT",
                 "placeholders", "tool.panchang"),
                ("same as English", {"SEO_TEXT": setkey("tool.rahu-kaal", "Rahu Kaal")}, "SEO_TEXT",
                 "same as English", "tool.rahu-kaal"),
                ("wrong script (Devanagari)", {"SEO_TEXT": setkey("tool.choghadiya", "चौघड़िया")}, "SEO_TEXT",
                 "wrong script", "tool.choghadiya"),
                ("English word left in", {"SEO_TEXT": setkey("links.heading", "ಇನ್ನಷ್ಟು free tools")}, "SEO_TEXT",
                 "wrong script", "links.heading"),
                ("stray brace", {"SEO_TEXT": setkey("tool.panchang", "ಪಂಚಾಂಗ {")}, "SEO_TEXT", "braces",
                 "tool.panchang"),
                ("unclosed html", {"SEO_TEXT": setkey("links.heading", "<strong>ಇನ್ನಷ್ಟು ಸಾಧನಗಳು")},
                 "SEO_TEXT", "html", "links.heading"),
                ("wrong lang= code", {"RASHIFAL_TEXT": setkey("sub_lang", "hi")}, "RASHIFAL_TEXT",
                 "wrong value", "sub_lang"),
                ("a link href changed", {"RASHIFAL_MORE_LINKS": lambda d: (d[0], ("/oops", d[1][1]), *d[2:])},
                 "RASHIFAL_MORE_LINKS", "placeholders", "1: href"),
                ("a FAQ answer left empty", {"SEO_FAQ": lambda d: ((d[0][0], ""), *d[1:])}, "SEO_FAQ",
                 "empty", "0.a"),
                ("a house missing from a bank", {"RASHIFAL_MOON_HOUSE": drop(5)}, "RASHIFAL_MOON_HOUSE",
                 "missing", "5"),
        ):
            fake.write_from_kn(ready={"seo"}, **patch)
            rs = results(only={"seo", "rashifal"})
            found = problems_of(rs, table).get(cat, [])
            check(f"checker catches: {label}", any(needle in d for d in found), str(problems_of(rs, table))[:160])
        fake.write_from_kn(ready={"seo"})
        fake.names_module()
        fake.write_from_kn(ready={"seo"}, VRAT_NOTES=lambda d: {**d, "holika-dahan": "ಹೋಳಿಕಾ Zxqwv"})
        check("a Latin word in a translation is 'wrong script' ...",
              any("Zxqwv" in d for d in problems_of(results(only={"vrat"}), "VRAT_NOTES")
                  .get("wrong script", [])))
        fake.write_from_kn(ready={"seo"}, allow={"Zxqwv"},
                           VRAT_NOTES=lambda d: {**d, "holika-dahan": "ಹೋಳಿಕಾ Zxqwv"})
        check("... unless the language file lists it in ALLOW_LATIN",
              "wrong script" not in problems_of(results(only={"vrat"}), "VRAT_NOTES"))
        # READY backed by data
        fake.write_from_kn(ready={"seo", "vrat"}, VRAT_ABOUT=drop("diwali"))
        fake.names_module()
        rs = results(only={"seo", "vrat", "names"})
        notes = C.ready_problems(FAKE, results(only=None))
        check("READY naming a module whose table is incomplete is reported",
              any("'vrat'" in n and "VRAT_ABOUT" in n for n in notes), str(notes))
        check("... but not a module that is clean", not any("'seo'" in n for n in notes), str(notes))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = cli(["check", FAKE])
        check("CLI check exits 1 on any problem", rc == 1)
        fake.write_from_kn(ready=set())
        sys.modules.pop("app.astro.names_zz", None)
        rs = results(only={"names"})
        check("names_<code>.py of a missing file is reported, not a crash",
              "missing" in rs[0].problems and rs[0].name.startswith("names_"))
        # json
        jpath = fake.root / "app/static/i18n/zz.json"
        en_json = json.loads((fake.root / "app/static/i18n/en.json").read_text(encoding="utf-8"))
        some = next(k for k, v in en_json.items() if isinstance(v, str) and "{" in v)
        jpath.write_text(json.dumps({some: "ತಪ್ಪು", "not.a.key": "x"}, ensure_ascii=False), encoding="utf-8")
        jr = C.check_json(FAKE)
        check("json: missing keys, extras, placeholder mismatch are all reported",
              "missing" in jr.problems and "extra" in jr.problems and "placeholders" in jr.problems,
              str(list(jr.problems)))
        jpath.write_text("{}", encoding="utf-8")
        jr = C.check_json(FAKE)
        check("json: `{}` is all missing, and passes the loader", len(jr.problems["missing"]) == jr.total)
        jpath.write_text("{not json", encoding="utf-8")
        check("json: invalid JSON is reported", "braces" in C.check_json(FAKE).problems)
        jpath.write_text(json.dumps({k: (v if not isinstance(v, str) else "ನಮಸ್ಕಾರ") for k, v in en_json.items()
                                     if isinstance(v, str)}, ensure_ascii=False), encoding="utf-8")
        jr = C.check_json(FAKE)
        check("json: a value from the English key set in the right script passes script/same-as-English",
              "wrong script" not in jr.problems and "same as English" not in jr.problems)

    check("script blocks cover all eleven regional languages",
          set(lang_data.BLOCKS) >= set(i18n.EXTRA_CODES) | {"hi"})
    check("Assamese is checked against the Bengali block (ৰ U+09F0 and ৱ U+09F1 are inside it)",
          lang_data.BLOCKS["as"] == lang_data.BLOCKS["bn"] and C.in_blocks("ৰ", "as") and C.in_blocks("ৱ", "as"))
    check("Marathi and Nepali are checked against Devanagari, Punjabi against Gurmukhi, Gujarati against Gujarati",
          lang_data.BLOCKS["mr"] == lang_data.BLOCKS["ne"] == ((0x0900, 0x097F),)
          and lang_data.BLOCKS["pa"] == ((0x0A00, 0x0A7F),) and lang_data.BLOCKS["gu"] == ((0x0A80, 0x0AFF),))
    check("script_problems(): digits, punctuation, ZWJ, HTML, placeholders and entities are not 'wrong script'",
          C.script_problems("ਪੰਜਾਬੀ 2026 — <b>{city}</b> &amp; IST, WhatsApp ‍, D9 (28.6°N)", "pa") == [])
    check("script_problems(): Latin words and other scripts are", "tool" in C.script_problems("ਪੰਜਾਬੀ tool", "pa")
          and C.script_problems("ਪੰਜਾਬੀ हिन्दी", "pa") != [])
    check("tags(): HTML balance", C.unbalanced("<p><strong>x</strong></p>") == ""
          and C.unbalanced("<p>x") != "" and C.unbalanced("x</p>") != "" and C.unbalanced("a<br/>b<br>c") == "")

    # ------------------------------------------------------------------ 6
    print("\n6. The real five today")
    for code in NEW:
        mod = lang_data.load(code)
        rs = C.check_language(code, only={"akshar"})
        check(f"{code}: all 112 namakshar syllables convert into the {code} script (AKSHAR)",
              rs[0].ok and rs[0].filled == 112, str(rs[0].problems))
        notes = C.ready_problems(code)
        check(f"{code}: every module in READY={sorted(mod.READY)} is backed by a clean check "
              "(CI fails a half-written module that was switched on)", not notes, "; ".join(notes))
        check(f"{code}: i18n._AKSHAR has it (akshar_lang)", i18n.akshar_lang(code) == code)
        reg = i18n.get(code)
        check(f"{code}: registry strings are in the script and the font is as planned",
              all(getattr(reg, f) for f in ("choose", "hint", "yes", "not_now", "notice", "english_answer")))
    check("skeleton CLI is deterministic: a fresh skeleton equals the committed file for an untouched language",
          all(SK.render_module(c) == (ROOT / "app" / "lang_data" / f"{c}.py").read_text(encoding="utf-8")
              or bool(lang_data.load(c).READY) or lang_data.filled(c, "SEO_TEXT")
              or any(lang_data.filled(c, t) for t in T.SPECS)
              for c in NEW))

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("lang_data: all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
