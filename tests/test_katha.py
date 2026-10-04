"""Katha: the story files, the pages, the daily pick and the evening channel post.

    ~/.venvs/divineastro/bin/python -u -m tests.test_katha

Works with any number of real story files in app/katha_stories: the page
checks loop over whatever is there; the pick and CLI checks use fixture
stories written to temp dirs, so they never depend on the real catalogue.
Nothing is ever sent: the connector is httpx.MockTransport.
"""

from __future__ import annotations

import contextlib
import copy
import datetime as dt
import io
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
_tmp = tempfile.mkdtemp(prefix="astro_katha_")
os.environ["ASTRO_DATABASE_URL"] = f"sqlite:///{Path(_tmp).as_posix()}/t.db"
os.environ["ASTRO_DAILY_STATE_DIR"] = _tmp
for _k in ("ASTRO_WA_TOKEN", "ASTRO_WA_CHANNEL_LINK", "ASTRO_WA_URL", "ASTRO_KATHA_DIR"):
    os.environ.pop(_k, None)

import httpx  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import analytics, daily_state, katha, seo_pages, share  # noqa: E402
from app import whatsapp_channel as W  # noqa: E402
from app.main import app  # noqa: E402

client = TestClient(app, raise_server_exceptions=False)
failures: list[str] = []
SITE = seo_pages.SITE_URL
SAVITRI = json.loads((katha.STORY_DIR / "savitri-satyavan.json").read_text(encoding="utf-8"))


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


# --------------------------------------------------------------------------
# Fixture stories
# --------------------------------------------------------------------------

def fixture(slug: str, category: str = "other", tags=(), match_names=None) -> dict:
    doc = copy.deepcopy(SAVITRI)
    doc.update(slug=slug, category=category, tags=list(tags))
    if match_names is None:
        doc.pop("match_names", None)
    else:
        doc["match_names"] = list(match_names)
    doc["hi"]["title"] = f"परीक्षण कथा {slug}"
    doc["en"]["title"] = f"Test story {slug}"
    return doc


def write_dir(docs: list[dict], names: list[str] | None = None) -> Path:
    d = Path(tempfile.mkdtemp(prefix="katha_fx_", dir=_tmp))
    for i, doc in enumerate(docs):
        name = names[i] if names else f"{doc['slug']}.json"
        (d / name).write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    return d


FIXTURES = [
    fixture("a-evergreen", "rishi"),
    fixture("b-evergreen", "shiva", match_names=[]),
    fixture("c-karwa", "vrat-katha", tags=["karwa_chauth"]),
    fixture("d-ekadashi", "vishnu", tags=["ekadashi"]),
    fixture("e-indira", "vrat-katha", match_names=["Indira Ekadashi"]),
]
FIXTURE_DIR = write_dir(FIXTURES)
EVERGREEN = {"a-evergreen", "b-evergreen"}


def fresh_state() -> None:
    os.environ["ASTRO_DAILY_STATE_DIR"] = tempfile.mkdtemp(prefix="state_", dir=_tmp)


def run(argv: list[str]) -> tuple[int, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = katha.main(argv)
    return code, out.getvalue() + err.getvalue()


# --------------------------------------------------------------------------
# 1. Loader and schema
# --------------------------------------------------------------------------

def test_loader() -> None:
    print("\n1. Loader")
    check("real stories load (at least savitri-satyavan)", "savitri-satyavan" in katha.STORIES)
    check("real stories are in slug order", list(katha.STORIES) == sorted(katha.STORIES))
    s = katha.STORIES["savitri-satyavan"]
    check("savitri-satyavan: vrat-katha, vat_savitri + vat_purnima",
          s.category == "vrat-katha" and set(s.tags) == {"vat_savitri", "vat_purnima"})
    check("savitri-satyavan: English version parallels the Hindi",
          len(s.en.teaser) == len(s.hi.teaser) and len(s.en.rest) == len(s.hi.rest)
          and s.en.title == "Savitri and Satyavan")
    fx = katha.load(FIXTURE_DIR)
    check("fixture dir: good files load, in stable (slug) order",
          list(fx) == [d["slug"] for d in FIXTURES], str(list(fx)))
    check("fixture: tags / match_names / evergreen parsed",
          fx["c-karwa"].tags == ("karwa_chauth",) and fx["e-indira"].match_names
          == ("Indira Ekadashi",) and fx["a-evergreen"].evergreen
          and not fx["c-karwa"].evergreen)
    with patch.dict(os.environ, {"ASTRO_KATHA_DIR": str(FIXTURE_DIR)}):
        check("ASTRO_KATHA_DIR selects the story dir", list(katha.load()) == list(fx))
    check("empty dir: no stories, no error", katha.load(write_dir([])) == {})

    def broken(label: str, mutate, needle: str, name: str | None = None,
               raw: str | None = None) -> None:
        doc = fixture("broken-story")
        mutate(doc)
        d = write_dir([doc], [name] if name else None)
        if raw is not None:
            (d / (name or "broken-story.json")).write_text(raw, encoding="utf-8")
        fname = name or "broken-story.json"
        try:
            katha.load(d)
        except katha.StoryError as exc:
            msg = str(exc)
            check(f"broken file ({label}): StoryError naming the file and the problem",
                  msg.startswith(fname) and needle in msg, msg)
            return
        check(f"broken file ({label}): StoryError raised", False, "loaded without error")

    def drop(*path):
        def f(doc):
            d = doc
            for k in path[:-1]:
                d = d[k]
            del d[path[-1]]
        return f

    def setv(value, *path):
        def f(doc):
            d = doc
            for k in path[:-1]:
                d = d[k]
            d[path[-1]] = value
        return f

    broken("not JSON", lambda d: None, "not valid UTF-8 JSON", raw="{\"slug\": ")
    broken("not an object", lambda d: None, "one JSON object", raw="[]")
    broken("missing category", drop("category"), "missing category")
    broken("missing tags", drop("tags"), "missing tags")
    broken("unknown top-level field", setv("x", "order"), "unknown field(s) order")
    broken("slug differs from file name", lambda d: None, "must match the file name",
           name="other-name.json")
    broken("bad slug", setv("Bad_Slug", "slug"), "lowercase-words-with-hyphens",
           name="Bad_Slug.json")
    broken("unknown category", setv("gods", "category"), "category 'gods'")
    broken("unknown festival tag", setv(["karva_chauth"], "tags"), "karva_chauth")
    broken("tags not a list", setv("diwali", "tags"), "tags must be a list")
    broken("unknown match_name", setv(["Indra Ekadashi"], "match_names"), "Indra Ekadashi")
    broken("missing hi.hook", drop("hi", "hook"), "hi: missing hook")
    broken("extra en field", setv("x", "en", "subtitle"), "en: unknown field(s) subtitle")
    broken("empty teaser", setv([], "en", "teaser"), "en: teaser must be a non-empty list")
    broken("empty paragraph", setv(["ok", " "], "hi", "rest"), "hi: rest[1]")
    broken("empty title", setv("", "en", "title"), "en: title must not be empty")
    broken("note not a string", setv(None, "hi", "note"), "hi: note must be a string")
    broken("** markup", setv(["**bold**"], "hi", "rest"), "'**'")
    broken("unbalanced *", setv(["one *star"], "en", "rest"), "unbalanced")
    broken("HTML in text", setv(["<b>x</b>"], "en", "rest"), "HTML")
    broken("Hindi title not Hindi", setv("Savitri", "hi", "title"), "not in Hindi")
    broken("English title in Devanagari", setv("सावित्री", "en", "title"), "must be English")
    broken("bad link shape", setv([["a", "/hi/x", "b"]], "links"), "links[0]")
    broken("link not a site path", setv([["a", "https://x.com", "b", "/x"]], "links"),
           "site paths")
    broken("teaser too long", setv(["क" * 4100], "hi", "teaser"), "under 4000")


# --------------------------------------------------------------------------
# 2. Pages
# --------------------------------------------------------------------------

def hreflang(html: str) -> dict[str, str]:
    return dict(re.findall(r'<link rel="alternate" hreflang="([\w-]+)" href="([^"]+)"/>', html))


def test_pages() -> None:
    print("\n2. Pages (every real story, both languages)")
    for slug, s in katha.STORIES.items():
        hi_p, en_p = f"/katha/{slug}", f"/en/katha/{slug}"
        want = {"hi": SITE + hi_p, "en": SITE + en_p, "x-default": SITE + hi_p}
        for lang, path, other in (("hi", hi_p, en_p), ("en", en_p, hi_p)):
            t = s.hi if lang == "hi" else s.en
            r = client.get(path)
            body = r.text
            check(f"{path}: 200", r.status_code == 200, str(r.status_code))
            check(f"{path}: whole story (teaser + rest)",
                  all(katha._html(p) in body for p in (*t.teaser, *t.rest)))
            check(f"{path}: title, source, message", t.title.replace("'", "&#x27;") in body
                  and katha._e(t.source) in body and katha._html(t.message) in body)
            check(f"{path}: canonical is itself",
                  f'<link rel="canonical" href="{SITE}{path}"/>' in body)
            check(f"{path}: reciprocal hreflang, x-default Hindi", hreflang(body) == want,
                  str(hreflang(body)))
            check(f"{path}: language switch", f'<a href="{other}" hreflang="{"en" if lang == "hi" else "hi"}"' in body)
            ld = re.search(r'"@type": "Article"[^}]*"inLanguage": "([\w-]+)"', body)
            check(f"{path}: Article JSON-LD in {lang}",
                  ld is not None and ld.group(1) == ("hi-IN" if lang == "hi" else "en-IN"))
            check(f"{path}: html lang", f'<html lang="{"hi" if lang == "hi" else "en-IN"}">'
                  in body)
            check(f"{path}: WhatsApp share button", 'data-share="seo-katha"' in body
                  and (("WhatsApp पर भेजें" if lang == "hi" else "Share on WhatsApp") in body)
                  and "utm_campaign%3Dseo-katha" in body)
            check(f"{path}: counts with the visit beacon", analytics.is_public_page(path))
            check(f"{path}: in the sitemap", path in seo_pages.sitemap_paths())
            links = [(ln[1], ln[0]) if lang == "hi" else (ln[3], ln[2]) for ln in s.links]
            check(f"{path}: closing links in its language",
                  all(f'href="{p}"' in body for p, _ in links))
        tz = katha.teaser(slug)
        check(f"{slug}: teaser stops before the rest", not any(p in tz for p in s.hi.rest))
        check(f"{slug}: teaser links to the Hindi page with UTM",
              f"/katha/{slug}?utm_source=whatsapp&utm_medium=channel&utm_campaign=katha" in tz)
        check(f"{slug}: teaser fits a WhatsApp message", len(tz) < 4000, str(len(tz)))

    for lang, path, other in (("hi", "/katha", "/en/katha"), ("en", "/en/katha", "/katha")):
        r = client.get(path)
        body = r.text
        check(f"{path}: 200", r.status_code == 200, str(r.status_code))
        check(f"{path}: lists every story with summary and source",
              all(f'href="{katha.page_path(slug, lang)}"' in body
                  and katha._e(s.text(lang).summary) in body
                  and katha._e(s.text(lang).source) in body
                  for slug, s in katha.STORIES.items()))
        cats = {s.category for s in katha.STORIES.values()}
        check(f"{path}: grouped by category, headings in its language",
              all(f'<h2 id="{c}">{katha._e(katha.CATEGORIES[c][0 if lang == "hi" else 1])}</h2>'
                  in body for c in cats)
              and not any(f'id="{c}"' in body for c in set(katha.CATEGORIES) - cats))
        check(f"{path}: hreflang (x-default Hindi)", hreflang(body) == {
            "hi": SITE + "/katha", "en": SITE + "/en/katha", "x-default": SITE + "/katha"})
        check(f"{path}: switch + share", f'href="{other}"' in body and "seo-katha" in body)
        check(f"{path}: public + sitemap", analytics.is_public_page(path)
              and path in seo_pages.sitemap_paths())
    for path in ("/katha/no-such-story", "/en/katha/no-such-story"):
        r = client.get(path)
        check(f"{path}: 404, not cacheable, no share",
              r.status_code == 404 and r.headers.get("cache-control") == "no-store"
              and "seo-katha" not in r.text)
        check(f"{path}: not public", not analytics.is_public_page(path))
    check("share text: none for unknown story / lookalike paths",
          share.seo_share_text("/katha/nope") is None and share.seo_share_text("/kathax") is None)
    check("other pages keep x-default English", hreflang(client.get("/hi/panchang").text)
          .get("x-default") == SITE + "/panchang")
    check("Hindi SEO footer links कथाएँ", 'href="/katha">कथाएँ</a>' in client.get("/hi/panchang").text)
    check("English SEO footer links Kathas",
          'href="/en/katha">Kathas</a>' in client.get("/panchang").text)
    index = (ROOT / "app" / "static" / "index.html").read_text(encoding="utf-8")
    app_js = (ROOT / "app" / "static" / "app.js").read_text(encoding="utf-8")
    check("home page has the katha card, app.js localises it",
          'id="open-katha"' in index and '"/katha" : "/en/katha"' in app_js)


# --------------------------------------------------------------------------
# 3. pick()
# --------------------------------------------------------------------------

def test_pick() -> None:
    print("\n3. pick()")
    fx = katha.load(FIXTURE_DIR)
    D = dt.date.fromisoformat
    karwa, indira, quiet = D("2026-10-29"), D("2026-10-06"), D("2026-10-04")
    check("2026-10-29 is Karwa Chauth, 2026-10-06 Indira Ekadashi, 2026-10-04 nothing",
          "karwa_chauth" in {o["key"] for o in katha.festivals.on(karwa)}
          and "Indira Ekadashi" in {o["name_en"] for o in katha.festivals.on(indira)}
          and not katha.festivals.on(quiet))
    check("festival day: the karwa_chauth story", katha.pick(karwa, fx, {}) == "c-karwa")
    check("named Ekadashi: match_names beats the generic ekadashi tag",
          katha.pick(indira, fx, {}) == "e-indira")
    check("named story posted recently: the tagged one instead",
          katha.pick(indira, fx, {"e-indira": D("2026-03-01")}) == "d-ekadashi")
    check("both posted within 300 days: falls back to the rotation",
          katha.pick(indira, fx, {"e-indira": D("2026-03-01"), "d-ekadashi": D("2025-12-15")})
          == "a-evergreen")
    check("festival story posted 384 days ago: picked again",
          katha.pick(karwa, fx, {"c-karwa": D("2025-10-10")}) == "c-karwa")
    check("festival story posted 299 days ago: not repeated",
          katha.pick(karwa, fx, {"c-karwa": karwa - dt.timedelta(days=299)}) == "a-evergreen")
    check("festival story posted exactly 300 days ago: allowed",
          katha.pick(karwa, fx, {"c-karwa": karwa - dt.timedelta(days=300)}) == "c-karwa")
    check("quiet day: first never-posted evergreen", katha.pick(quiet, fx, {}) == "a-evergreen")
    check("quiet day: next in rotation",
          katha.pick(quiet, fx, {"a-evergreen": D("2026-10-03")}) == "b-evergreen")
    check("all evergreen posted (> 60 days): least recently posted",
          katha.pick(quiet, fx, {"a-evergreen": D("2026-06-01"),
                                 "b-evergreen": D("2026-05-01")}) == "b-evergreen")
    check("all evergreen posted within 60 days: a never-posted festival story",
          katha.pick(quiet, fx, {"a-evergreen": D("2026-10-01"),
                                 "b-evergreen": D("2026-09-01")}) == "c-karwa")
    everything = {"a-evergreen": D("2026-10-01"), "b-evergreen": D("2026-09-01"),
                  "c-karwa": D("2025-10-10"), "d-ekadashi": D("2026-08-01"),
                  "e-indira": D("2025-10-17")}
    check("everything posted recently: the least recently posted of all",
          katha.pick(quiet, fx, everything) == "c-karwa")
    only_fest = {k: v for k, v in fx.items() if not v.evergreen}
    check("no evergreen stories at all: still picks something",
          katha.pick(quiet, only_fest, {}) == "c-karwa")
    check("no stories: None", katha.pick(quiet, {}, {}) is None)

    # A season of nightly picks: never a festival story off its day while some
    # evergreen story is older than 60 days (or unposted).
    posted: dict[str, dt.date] = {}
    ok, bad = True, ""
    day = D("2026-09-20")
    seen = []
    while day <= D("2026-11-20"):
        slug = katha.pick(day, fx, posted)
        obs = katha.festivals.on(day)
        s = fx[slug]
        own = any(o["key"] in s.tags or o["name_en"] in s.match_names for o in obs)
        recent = slug in posted and (day - posted[slug]).days < 300
        # Off its day, or a repeat within 300 days, only as the last resort.
        if not s.evergreen and (not own or recent):
            if not all(k in posted and (day - posted[k]).days < 60 for k in EVERGREEN):
                ok, bad = False, f"{slug} on {day}"
        seen.append(slug)
        posted[slug] = day
        day += dt.timedelta(days=1)
    check("two months of nightly picks keep the rules", ok, bad)
    check("the season used the festival stories on their days",
          "c-karwa" in seen and "e-indira" in seen)


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


def test_cli() -> None:
    print("\n4. CLI")
    fx = katha.load(FIXTURE_DIR)
    env = {"ASTRO_WA_TOKEN": "secret-token", "ASTRO_WA_CHANNEL_LINK":
           "https://whatsapp.com/channel/ABC", "ASTRO_WA_URL": "http://wa:3000",
           "ASTRO_WA_WAIT": "0"}
    alerts: list[str] = []
    with patch.object(katha, "STORIES", fx), \
            patch.object(W, "alert_owner", lambda reason, day: alerts.append(reason)):
        fresh_state()
        code, out = run(["--slug", "a-evergreen", "--dry-run"])
        check("--slug --dry-run prints the teaser", code == 0 and "Test story" not in out
              and "परीक्षण कथा a-evergreen" in out, out[:200])
        code, out = run(["--daily", "--date", "2026-10-29", "--dry-run"])
        check("--daily --dry-run shows the festival pick", code == 0
              and "katha c-karwa for 2026-10-29" in out, out[:200])
        check("dry run records nothing", daily_state.sent("katha", dt.date(2026, 10, 29)) == {}
              and daily_state.recall("katha", "c-karwa") is None)
        check("needs --daily or --slug (argparse exit 2)", _exits(lambda: run([])))
        check("bad --date: exit 2", run(["--daily", "--date", "29-10-2026"])[0] == 2)
        code, out = run(["--daily", "--date", "2026-10-29"])
        check("not configured: exit 2", code == 2 and "ASTRO_WA_TOKEN" in out, out)

        stub = Stub()
        with patch.dict(os.environ, env), patch.object(W, "_transport", httpx.MockTransport(stub)):
            code, out = run(["--daily", "--date", "2026-10-29"])
            check("--daily posts today's pick", code == 0 and len(stub.posts) == 1, out)
            p = stub.posts[0] if stub.posts else {}
            check("posted the karwa teaser to the channel", p.get("jid") == "123@newsletter"
                  and p.get("text") == katha.teaser("c-karwa"))
            day_rec = daily_state.sent("katha", dt.date(2026, 10, 29)).get("story")
            hist = daily_state.recall("katha", "c-karwa")
            check("recorded per date and per slug",
                  day_rec == {"slug": "c-karwa", "id": "M1"} and isinstance(hist, dict)
                  and hist.get("id") == "M1" and hist.get("day") == "2026-10-29"
                  and "posted" in hist, f"{day_rec} {hist}")
            check("the history feeds pick()", katha.history(fx) == {"c-karwa":
                                                                      dt.date(2026, 10, 29)})
            code, out = run(["--daily", "--date", "2026-10-29"])
            check("second run the same date: nothing sent, exit 0",
                  code == 0 and len(stub.posts) == 1 and "already posted" in out, out)
            code, out = run(["--daily", "--date", "2026-10-29", "--dry-run"])
            check("dry run after posting shows what went out",
                  code == 0 and "c-karwa" in out and "[already posted]" in out)
            code, out = run(["--daily", "--date", "2026-10-29", "--force"])
            check("--force re-sends the same date's story", code == 0 and len(stub.posts) == 2
                  and stub.posts[1]["text"] == katha.teaser("c-karwa"), out)
            code, out = run(["--daily", "--date", "2026-10-30"])
            check("next day: the rotation, not the festival story again",
                  code == 0 and stub.posts[-1]["text"] == katha.teaser("a-evergreen"), out)
            code, out = run(["--slug", "a-evergreen"])
            check("--slug of an already-posted story: nothing sent",
                  code == 0 and len(stub.posts) == 3 and "already posted" in out, out)
            code, out = run(["--slug", "b-evergreen"])
            check("--slug posts that story", code == 0 and len(stub.posts) == 4
                  and stub.posts[-1]["text"] == katha.teaser("b-evergreen"))
            check("--slug leaves the per-date record alone",
                  set(daily_state.load("katha")) == {"2026-10-29", "2026-10-30"},
                  str(sorted(daily_state.load("katha"))))
            check("token never printed", "secret-token" not in out)

        stub = Stub(post_status=409)
        with patch.dict(os.environ, env), patch.object(W, "_transport", httpx.MockTransport(stub)):
            code, out = run(["--daily", "--date", "2026-10-31"])
            check("connector unlinked mid-send: exit 1, owner alerted",
                  code == 1 and len(alerts) == 1, out)
            check("a failed post is not recorded",
                  daily_state.sent("katha", dt.date(2026, 10, 31)) == {})
        stub = Stub(connected=False)
        with patch.dict(os.environ, env), patch.object(W, "_transport", httpx.MockTransport(stub)):
            code, out = run(["--daily", "--date", "2026-10-31"])
            check("connector not linked: exit 1, owner alerted", code == 1 and len(alerts) == 2
                  and not stub.posts, out)
        stub = Stub(post_status=502)
        with patch.dict(os.environ, env), patch.object(W, "_transport", httpx.MockTransport(stub)):
            code, out = run(["--daily", "--date", "2026-10-31"])
            check("send failure: exit 1, no alert", code == 1 and len(alerts) == 2, out)

    print("\n5. Compatibility")
    fresh_state()
    daily_state.remember("katha", "savitri-satyavan",
                         {"posted": "2026-10-03T19:00:04", "id": "3EB0ABC"})
    check("the entry the first post wrote reads as posted that day",
          katha.history().get("savitri-satyavan") == dt.date(2026, 10, 3))
    code, out = run(["--slug", "savitri-satyavan"])
    check("and --slug still treats it as posted", code == 0 and "already posted" in out, out)


def _exits(fn) -> bool:
    """argparse errors exit 2 via SystemExit; True if `fn` did."""
    try:
        with contextlib.redirect_stderr(io.StringIO()):
            fn()
    except SystemExit as exc:
        return exc.code == 2
    return False


def navratri_checks() -> None:
    """The nine nights get the nine forms of the Devi, in order (real story files)."""
    print("\nNavratri order (Sharad Navratri 11-19 Oct 2026)")
    import datetime as _dt
    got = [katha.pick(_dt.date(2026, 10, 11) + _dt.timedelta(days=i), posted={}) for i in range(9)]
    check("day 1..9 -> Shailputri .. Siddhidatri", tuple(got) == katha.NAVDURGA, str(got))
    check("Dussehra (20 Oct) -> Vijayadashami",
          katha.pick(_dt.date(2026, 10, 20), posted={}) == "vijayadashami")
    check("all nine Navadurga stories exist", all(s in katha.STORIES for s in katha.NAVDURGA))


def main() -> int:
    test_loader()
    test_pages()
    test_pick()
    test_cli()
    navratri_checks()
    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("katha: all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
