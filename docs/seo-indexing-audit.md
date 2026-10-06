# SEO indexing audit (DIVASTRO-133)

Symptom: in 72 h of access logs Googlebot made one request; one Bing referral
and no Google referral in 7 days, although Search Console and AdSense are
verified. This audit read the code and crawled the app in-process (every 5th
URL of the 5,033 in sitemap.xml, plus spot checks). No search engine or
Search Console was contacted.

## What was checked, and what was found

| Area | Result |
|---|---|
| robots.txt (`seo_pages.robots`) | Fine. `Allow: /`, `Disallow: /api/` and `/admin`, `Sitemap:` line. Nothing blocks pages, `/static/` or the sitemap. |
| sitemap.xml (`seo_pages.sitemap`) | One file, 5,033 URLs (limit 50,000 / 50 MB; 0.5 MB), so no sitemap index is needed. Only TRANSLATED languages are listed; untranslated regional copies are not. No duplicates, all canonical. **Problems:** no `<priority>` except on the home and tool pages, no ordering, and `<lastmod>` was claimed only for tool pages (correct) but not for rashifal (which does change daily). |
| hreflang | On-page `<link rel="alternate" hreflang>` is reciprocal and identical on every twin (i18n.alternates, covered by tests/test_seo_regional.py). Not duplicated into the sitemap on purpose: Google accepts either, and a second source that could drift from the page is the usual way hreflang breaks (katha uses its own URL scheme). |
| noindex | None of the 1,000 sampled sitemap URLs is noindex; every one returns 200 with `<link rel=canonical>` equal to its own sitemap URL. Untranslated regional copies are noindex and are not in the sitemap. |
| Duplicates / thin pages | Titles, meta descriptions and h1s are all unique across the sample (city + tool + today's date, in the page's language, e.g. "Today's Panchang in Pune, 7 October 2026"). The 114 cities x 3 tools x 8 languages pages are template-driven but carry computed, city-specific numbers (sunrise, Rahu Kaal, tithi). No change made; see "Remaining risk". |
| Status codes | Unknown city/sign: real 404. `/panchang/pune/` (trailing slash) returns 200 with the canonical pointing at the slash-less URL: acceptable, not changed (a redirect would be a URL change). `/PANCHANG`, `/index.html`: 404. |
| Headers | HTML: `Cache-Control: private, max-age<=1800`, never beyond the next IST midnight. Fine for crawlers (no CDN in front, Caddy does not cache). No stray `X-Robots-Tag` anywhere. `/` is `no-store`. |
| Host duplication | **Problem:** Caddy served the identical site on both `divineastro.org` and `www.divineastro.org` with no redirect. Two hosts, one content: split crawl budget and a canonical conflict for any URL discovered on www. |
| Home page `/` | **Problem:** `app/static/index.html` has no `<link rel="canonical">` and no hreflang, so `/?open=panchang`, `/?lang=hi`, `?utm_...` are distinct URLs to a crawler. index.html is not touched here (see the owner list). |
| Internal links | **Problem (the likely main cause):** the ~110 city pages, muhurat, vrat and nakshatra sections were reachable only from the JS app and from each other. Server-rendered pages had no link to a hub, and the home page is a JS shell. A crawler that lands on one page could not find the rest. |

## What changed

1. **Caddyfile**: `www.divineastro.org` now 301-redirects to `https://divineastro.org{uri}`; `/api/*` and `/admin` get `X-Robots-Tag: noindex, nofollow`. After deploy: restart the caddy container (reload reads the stale bind-mounted file, see MEMORY.md).
2. **Home canonical**: `GET /` now sends `Link: <https://divineastro.org/>; rel="canonical"` (an HTTP-header canonical that Google honours), without editing index.html. Every `/?...` variant canonicalises to `/`.
3. **sitemap.xml**: entries ordered best-first and every entry has a `<priority>` (home 1.0; tool / explainer pages 0.9; section hubs 0.8; sign, year, festival, muhurat, katha pages 0.7; the 20 largest cities 0.6; other cities 0.5; legal 0.3; regional-language copies 0.1 lower). `<lastmod>` stays honest: today's date only on the pages rebuilt daily (tool pages, rashifal), none on static pages. The URL set is unchanged except the 8 new `/sitemap` hub pages.
4. **Crawlable hub `/sitemap`** (also `/hi/sitemap`, `/kn/...`, all 8 languages, `app/site_hub.py`, labels in `app/hub_text.py`): plain HTML links to every section index, the 12 signs, the vrat/ekadashi calendars, the muhurat pages, nakshatra / rashi / naam milan, katha, the tools, and the Panchang page of every city grouped by state. It is in the sitemap.
5. **Footer link block** on every server-rendered page (`seo_pages._footer_sections`, one extra `<nav class="footer-sections">` inside `<footer>`): Site map, Panchang, Rashifal, Vrat, Muhurat, Nakshatra, Katha, in the page's language. Every page now links to the hub.
6. **IndexNow** (`app/indexnow.py`): see "IndexNow" below.

No page became noindex, no URL changed.

## IndexNow

Off unless `ASTRO_INDEXNOW_KEY` is set (8-128 chars, letters, digits, `-`). When set, `/<key>.txt` serves the key. Commands:

    python -m app.indexnow --daily    # ~600-700 URLs: default city + 20 biggest cities x 3 tools,
                                      # rashifal, vrat hub, katha index, tonight's story and any
                                      # story not submitted before; all 8 languages; once per date
    python -m app.indexnow --all      # whole sitemap (~5,040 URLs), once; --force repeats
    add --dry-run to print, --date YYYY-MM-DD, --force to resend

State is in `daily_state` (job `indexnow`), so cron retries are harmless. Run `--all` once after the key is live, then `--daily` from cron after the 06:00 IST jobs. IndexNow reaches Bing, Yandex, Naver and Seznam; **Google does not use IndexNow**.

## Remaining risk (not changed)

* Googlebot's one-request-in-72 h is typical for a new, small domain with no inbound links; the technical blockers above were the fixable part. The rest is authority: external links, time, and Search Console requests.
* Near-duplicate risk across 114 cities: pages differ by computed values and names but share most template text. If Search Console reports "Crawled - currently not indexed" or "Duplicate, Google chose different canonical" for city pages, the safe next step is to keep only the top ~30 cities in the sitemap and let the hub/footer links carry the rest.
* Regional-language pages (kn, te, ta, ml, bn, or) were added recently and are in the sitemap; if they dilute crawl, drop them from `sitemap_paths()` first.
* `index.html` still lacks an on-page canonical, hreflang and any crawlable link list (see below).

## Owner actions in Search Console

1. Deploy, then restart the caddy container so the www redirect and headers load.
2. Add the property for `https://divineastro.org/` (URL-prefix) if not yet present; add `www` only to check it now redirects.
3. Sitemaps: submit `https://divineastro.org/sitemap.xml` (and note the discovered-URL count vs 5,041).
4. URL Inspection, then "Request indexing" for: `/`, `/sitemap`, `/hi/sitemap`, `/panchang`, `/hi/panchang`, `/rashifal`, `/hi/rashifal`, `/vrat-tyohar`, `/muhurat/vivah-2026`, `/nakshatra`, `/katha`, `/panchang/mumbai`, `/panchang/bengaluru`. For `/` also confirm "User-declared canonical" shows `https://divineastro.org/`.
5. Pages > Indexing: after a week, read the reasons for non-indexed pages (Discovered / Crawled - not indexed, Duplicate...) per section and report back.
6. Settings > Crawl stats: confirm requests rise after the sitemap and hub are live.
7. Bing Webmaster Tools: import the site from Search Console and submit the sitemap; the IndexNow key file at `/<key>.txt` can be verified there.
8. Build a few real inbound links (Instagram / WhatsApp channel bio, Telegram channel, Play Store listing, any directory) pointing at `https://divineastro.org/` and `/panchang`: a link from an indexed site is what makes Googlebot return.
9. For the home page (index.html, owned elsewhere): add `<link rel="canonical" href="https://divineastro.org/">`, hreflang alternates, and a visible link block (or footer) to `/sitemap`, `/panchang`, `/rashifal`, `/vrat-tyohar`, `/katha` in plain `<a href>` so the JS shell is crawlable.
