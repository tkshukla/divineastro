# Handover — Divine Astro

Written 20 Aug 2026, at the end of a long session. Point the next session at
this file.

Live at https://divineastro.org · GCP `divineastro`, zone `asia-south1-a`,
project `astro-505710` · static IP `8.234.96.206`.

---

## Deploying

```powershell
.\deploy\provision.ps1 -Redeploy
```

`.env.production` is uploaded to `/opt/divineastro/.env` on **every** deploy, so
edit the local file — editing the copy on the VM gets silently overwritten next
time. Alembic runs at container startup, so migrations apply themselves.

`provision.ps1` must stay **UTF-8 with BOM**. Without it the em-dashes decode as
CP1252 and a stray byte closes a string early.

---

## Running the tests

All 11 suites pass, but only under the right environment. Three of them
"failing" is almost always the env, not a regression:

| Suite | Needs |
|---|---|
| `test_money_path`, `test_coupons` | `ASTRO_GATEWAY=test` |
| `test_upi` | `ASTRO_GATEWAY=upi_manual`, `ASTRO_UPI_VPA` |
| `test_admin` | `ASTRO_ADMIN_EMAILS=owner@divineastro.org` |

So run them in two passes: everything except `test_upi` on `test`, then
`test_upi` on `upi_manual`.

**Local tests run on SQLite and cannot catch Postgres enum drift.** SQLite
stores enums as plain text and accepts any value. This exact gap took the admin
page down today (see below). Any change to a status or type column must be
checked against Postgres directly.

---

## Fixed today

- **Answers were bookish.** The prompt was sending the engine's own prose, which
  the model paraphrased back. Now facts-only: evidence lines, Vimshottari dasha,
  dated windows. Input dropped ~27%. A date auditor confirms answers only print
  dates present in the prompt (12/12 across a question sweep).
- **Admin page 500.** Production's `orderstatus` enum was missing
  `awaiting_verification` and `rejected`, because the initial migration had been
  edited in place instead of shipping a revision. This broke the **entire UPI
  flow**, not just the page — that enum is on the write path too. Fixed by
  migration `b7e41c9d2a05`.
- **One chart type.** Sidereal / Lahiri / Whole Sign is now forced in
  `main.py` and `api_account.py`, the Advanced settings block is gone from the
  form, and the 5 stored profiles were migrated. A tropical chart silently has
  no Vimshottari dasha, so "when will X happen" had nothing to answer from.
- **Topic classifier missed dasha compounds.** `_hits` anchors on `\b`, so
  `dasha` never matched `mahadasha`. Dasha questions fell through to the default
  topic and got answered as personality questions.
- **Implementation labels removed** from answers: "Rewritten by …", "The
  engine's own wording", and the red narration-failed banner. "The reasoning"
  stays — that one is about the chart, not our plumbing.
- **Udyam number** `UDYAM-UP-28-0235363` live in the footer, Contact page and
  `/api/site`.
- **Email works.** `support@divineastro.org` receives via Cloudflare Email
  Routing → `yaviemail1@gmail.com`, and sends via Brevo SMTP through Gmail's
  send-as. Zero cost. Full configuration and the four failure modes are written
  up at https://claude.ai/code/artifact/07f572ca-5910-4746-831b-c0f9317921fe

---

## Outstanding

**Blocking real revenue**

- [ ] **One real ₹111 UPI payment, end to end**, then approve it in `/admin`.
      Never done with real money. Approving is the only thing that grants
      credits. The admin page works now, but the happy path is unproven.
- [ ] No notification when a customer claims a UPI payment — you have to look.

**Security, from earlier in the project**

- [ ] **Rotate the Google OAuth client secret.** It was pasted in plaintext.
- [ ] **Delete the old Cloudflare API token.** It carried billing and registrar
      rights. If you still want me to manage DNS, issue one scoped to
      Zone → DNS → Edit on `divineastro.org` only.

**Legal**

- [x] **Source published** — https://github.com/tkshukla/divineastro, public,
      AGPL-3.0. `/terms` §10 links it via `ASTRO_SOURCE_URL`, which is what
      actually discharges §13: users must be *offered* the source, not merely
      have it exist somewhere.
- [ ] Udyam registration *date* and Micro/Small/Medium not supplied — the footer
      renders only the number until they are.

> **Before committing anything, re-run the secret scan.** `deploy/env.production.template`
> was misnamed: despite "template" it held a live `ASTRO_SECRET_KEY`,
> `POSTGRES_PASSWORD` and `GOOGLE_CLIENT_SECRET`, and `.gitignore` did not cover
> it. It was caught in the pre-push scan and scrubbed, so nothing leaked — but
> `.gitignore` alone is not a safety net. Grep staged *content* for
> `sk-ant-api03`, `GOCSPX-`, `AIza…`, `xkeysib-`, `BEGIN … PRIVATE KEY`.

**Quality & Features**

- [x] **Guna Milan bilingual localization** — Complete English & Devanagari Hindi translations for all 8 kootas, score bands, and Mangal Dosha.
- [x] **Sade Sati and Kaal Sarp UI** — Dashboard doshas modal renders Manglik, Sade Sati phase breakdown, and Kaal Sarp types.
- [x] **Muhurat Finder** — Deterministic classical electional engine and stage for Marriage, Griha Pravesh, Mundan, Namkaran, and General events.
- [x] **Single-Question Paid Reports** — Paid targeted PDF consultations (Career, Marriage Timing, Wealth & Business) with payment gating (`report_topic`).
- [x] **Ashtakavarga Matrix & Heatmap Engine** — Classical Parashari Sarvashtakavarga (337 bindus) and Bhinnashtakavarga tables with house strength ratings and bilingual financial interpretations.
- [x] **Real-Time Choghadiya Clock & Timeline** — 16-slot Day/Night Choghadiya engine with weekday ruler calculation, active slot highlight, and countdown.
- [x] **Shodashvarga Divisional Charts (D1-D60)** — Complete classical Parashari varga calculations and UI switcher for D1, D3, D7, D9, D10, D12.
- [x] **Comprehensive Vedic Life Book** — horoscope book PDF (`life_book`, about 8 pages measured, DIVASTRO-150) with D1/D9 charts, varga table, 120-year Dasha ladder, 12-house and planet readings and the next 12 months of sub-periods.
- [x] **Admin Panel Overhaul & Existing Coupons Suite** — Complete existing coupons list with live/paused status, filter/copy codes, usage/discount tracking, KPI Revenue Overview, Customer Account Manager with credit adjustments, Live AI Questions Stream, and Platform System Diagnostics.
- [x] **Jaimini Chara Karakas & Arudha Padas (A1-A12)** — Classical Jaimini soul purpose analysis (7 Karakas: AK, AmK, BK, MK, PK, GK, DK), Karakamsha Lagna, and 12 Arudha Padas (AL, UL) with bilingual Hindi/English interpretations.
- [x] **Sudarshana Chakra (Triple-Lagna) Synthesis** — 3-tier simultaneous chart analysis from Janma Lagna, Chandra Lagna, and Surya Lagna with tri-lagna convergence ratings across all 12 houses.
- [ ] No way to upload or send a finished hand-written kundali scan.

---

## Diwali offer pricing (DIVASTRO-152)

Every product has two prices in `app/billing.py`: the **offer price**
(`Product.offer_paise`, the first money argument of each `Product(...)`) and the
**list price** (`LIST_PRICES_PAISE`, what the site charges once the offer is
over). The price in force is *computed from the clock*, never stored:
`billing.effective_price_paise(sku, now=None)`; `billing.offer_status(now=None)`
-> `{active, name, ends_at_iso, ends_at_label}`. `Product.amount_paise` is now a
property returning the effective price, so every old reader keeps working.

* **End date**: 15 Nov 2026 23:59:59 IST (`OFFER_END_DEFAULT`). The offer is live
  strictly *before* that instant; at it and after, list prices apply by
  themselves (no deploy, no manual step, strike and offer label vanish).
  Move it without a deploy with `ASTRO_OFFER_ENDS` (ISO 8601 with offset, e.g.
  `2026-11-20T23:59:59+05:30`; no offset = IST). An unparseable value is logged
  and treated as "offer over" (list prices), the safe failure.
* **Kill switch**: `ASTRO_OFFER_OFF=1` ends the offer immediately (list prices).
  It can only ever end the offer, never start or extend one.
* **Change prices**: edit `offer_paise` in the `Product(...)` or the
  `LIST_PRICES_PAISE` table. An assert refuses list < offer.
* **API**: `/api/products` keeps `amount_paise`/`rupees`/`per_question` (now the
  effective price) and adds `list_amount_paise` (null unless the offer is
  active), `list_per_question`, and `offer {active, name, ends_at}`.
  `/pricing` JSON-LD carries `priceValidUntil` only while the offer is active.
* **Orders**: `Order.amount_paise` is frozen at creation (coupon applied to the
  effective price of that instant, `original_amount_paise` = that price). Paying
  later never reprices: gateways and verification use the stored amount, and the
  PayU return now also refuses a signed return whose amount differs from it. A
  pending order is neither repriced nor expired at the end instant; it stays
  payable at the price the customer was quoted (the gateway session already
  carries it).
* **Honesty rules (India consumer law: no fake "was" price, no fake urgency)**:
  charged == shown, always; the struck-through price is shown only while the offer
  is active and is exactly what is charged afterwards; no per-visitor countdown or
  stock-style urgency, the only urgency is the real end date; never show a list
  price the site does not charge. Tests: `tests/test_offer_pricing.py`. CI sets
  `ASTRO_OFFER_ENDS=2099-...` so the other suites (which assert offer prices) do
  not go red after the offer; locally they will after 15 Nov unless you set it.

* **UI half**: while `offer.active` is true the app shows the real regular price
  (`list_amount_paise`) struck through beside the current one (`<s class="was">` with
  sr-only "Regular price ..., now ..."), a "Save N%" badge (arithmetic on the two API
  numbers), a banner at the top of the home Plans section, the store and `/pricing`
  ("Diwali offer prices are valid until {date}, 11:59 PM IST. Regular prices apply after
  that."), and on `/pricing` an explanation section (en + hi, `pricing_text.py`). Nothing
  is hard-coded: `account.js` (`offerOn`, `offerBanner`, `priceHtml`, `saveBadge`) and
  `pricing_pages.py` (`_offer_of`, `_table`) render it only from the catalogue, so after the
  end instant (or `ASTRO_OFFER_OFF=1`) every screen is the plain regular-price screen with no
  code change. The store re-reads `/api/products` when it opens. The Orders screen shows the
  charged amount only. Strings: `acct.offerPill/offerBanner/wasPrice/nowPrice/savePct` in all
  13 i18n files. Tests: `tests/test_offer_screens.py`, `tests/e2e/test_offer.py`.
* **Caching**: `/pricing` is `private, max-age=min(300, seconds until ends_at)` while the
  offer is live (so a browser copy can never show the offer after the end instant), the shell's
  usual header (up to 30 min) once it is over; there is no in-process page cache and Caddy does
  no response caching. `/api/products` is `no-store`. The seo snapshot test pins
  `ASTRO_OFFER_ENDS` to 2099 so its recording does not depend on the calendar.

## Free questions and the guest answer (DIVASTRO-154)

* **New accounts get 3 free questions** (`billing.FREE_QUESTIONS`, env
  `ASTRO_FREE_QUESTIONS`, default 3; was 10). Every sign-up grant reads it at the
  moment the account is created; existing balances (credit_entries) are never
  touched. **The production `.env` still says `ASTRO_FREE_QUESTIONS=10`: change it
  to 3 (or delete the line) when deploying, or nothing changes.**
* Every place that states the allowance reads that value: `/api/me` and
  `/api/products` (`free_questions`, which the app's `{n}` strings use), `/pricing`
  + its FAQ JSON-LD (`pricing_text`, `{free}`), the daily WhatsApp/Telegram promo
  (`daily_message._promos`), the katha call to action, index.html's og:description
  (`__FREE_QUESTIONS__`, filled by `main._page`). The share card image
  `app/static/og-card.jpg` (from `assets/og/card.html`, `python assets/og/shot.py`)
  is the one place the number is baked in: regenerate it if the number changes.
* **One answer without signing in** (`app/guest.py`): a signed-out visitor with a
  chart gets one real answer from `/api/ask/stream` (same engine and narration,
  nothing charged), then 401 and the sign-in sheet ("Sign in to keep asking — 3 more
  questions free"). Limits: signed HttpOnly cookie `astro_guest` + a `guest_answers`
  row per answer keyed by the day-scoped visitor hash (no IP stored) + an in-memory
  per-address ceiling (`ASTRO_GUEST_ANSWERS_PER_ADDRESS`, 20/day) + global caps
  (`ASTRO_GUEST_ANSWERS_PER_HOUR` 60, `ASTRO_GUEST_ANSWERS_PER_DAY` 400); none for
  bots, prefetches, cloud addresses. DNT/GPC visitors get their answer but only
  time + hash are stored. `ASTRO_GUEST_ANSWER=0` switches it off (pages and promos
  then stop offering it). Rows are purged after 400 days with the statistics and
  show in the admin's signed-out questions as "answered free (guest)".
  Known limit: the hash rotates at IST midnight, so a visitor who clears cookies
  can get one more answer the next day; the global caps bound the cost.
  Tests: `tests/test_guest_answer.py`, `tests/e2e/test_guest_answer.py`.

## Working notes

Google sign-in **does** work — `/api/me` returns `provider: "google"` for
`tkshukla2504@gmail.com` with `is_admin: true`.

Narration is Claude Haiku 4.5. Reasoning-tier params (`output_config.effort`,
`fallbacks`, `betas`) return 400 on Haiku and must stay gated to opus/sonnet.
Haiku's minimum cacheable prefix is 4096 tokens, so prompt caching does nothing
at our prompt size — the efficiency win has to come from sending less.

Static assets are cache-busted with `?v=<max static mtime>`, and HTML is served
`no-store`. A normal reload is enough to pick up a deploy.

**Verify against what the user actually sees.** Repeatedly this session, a fix
looked correct in a dashboard or in my own cache-busted probe and was still
broken for the user. External DNS resolution beat the Cloudflare record list;
the Brevo delivery log beat guessing; `classify()` run inside the container beat
assuming the deploy shipped.
