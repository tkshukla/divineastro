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

**Since DIVASTRO-155 the `ollama` service is part of the product** (it writes the
Starter's emailed answers): after a deploy that changes `docker-compose.yml`, run
`docker compose up -d ollama` (it recreates it with the CPU cap and the one-model
settings), check `docker compose exec ollama ollama list` shows `qwen2.5:7b`, and run
the smoke script (see "Starter: emailed answers" below). Mail (`ASTRO_SMTP_*`) must be
configured, or every emailed answer fails and is refunded.

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

## Starter: emailed answers (DIVASTRO-155)

**What the customer gets.** When the free (instant) questions run out, the paywall
store leads with the one-time **Starter: 3 detailed answers by email, ₹21**
(`billing.STARTER_SKU = starter_email3`, kind `email_answers`). The nudge at 1
question left mentions it. After paying ("You have 3 emailed answers. Ask your next
question as usual — the answer arrives by email within 30 minutes."), every question
asked with 0 instant questions and >0 emailed answers is **queued**, not answered in
the chat: the chat shows "Your detailed answer will be emailed to <email> within 30
minutes. You can also find it in My questions." The answer is written in the
background, emailed, and saved in My questions (shown there as on its way / emailed,
with the text). The answers are written by the site's AI; nothing says or implies a
person writes them.

**Rules (server-side).**
* Once per account: a second order is a **409** (`billing.StarterRefused`) when a paid
  Starter or a UPI claim for one exists. An order that was only created (the customer
  left PayU) does not block a retry. `ASTRO_STARTER_ENABLED=0` takes it off sale
  everywhere (catalogue, store, /pricing, checkout: 409); bought credits keep working.
* **Accounts without an email cannot buy it** (phone/SMS and username/password
  accounts have no address; `billing.deliverable_email`): the honest option rather
  than selling an emailed answer we cannot email. `/api/me` → `user.starter =
  {available, reason}` (`disabled | no_email | bought | pending`). No coupons on it.
* **Not on the Diwali offer**: `Product.on_offer=False`, list = offer = 2100 paise, so
  no strike, no Save badge, no offer end and no `priceValidUntil` in the JSON-LD.
* **Separate balance**: `credit_entries.credit_type` is `question` (every existing
  row, all packs, the sign-up gift, admin adjustments) or `email` (the Starter).
  `db.balance()` is the instant balance as before; `db.email_balance()` the emailed
  one. Purchase, the debit at enqueue (`EntryKind.question`) and a refund
  (`EntryKind.refund`) are all `email` rows. Migration `e7a1c3d5f9b2`.

**The queue and the worker** (`app/emailed_answers.py`, table `emailed_answer_jobs`).
One job at a time, started from the app's lifespan, DB-backed (a restart puts a
"running" job back in the queue; after 3 interrupted attempts it fails and is
refunded). Each job stores the chart's birth payload (the in-memory chart session
expires), cleared when the job finishes. Per job:
1. rebuild the chart, `analyse()` + the Vedic context, exactly as an instant answer;
2. **Ollama** (`ASTRO_EMAIL_ANSWER_MODEL`, default `qwen2.5:7b`) writes it in English
   with the chat's narration prompt (`llm.stream_polish`, without the local "keep it
   short" note, up to `ASTRO_EMAIL_ANSWER_NUM_PREDICT`=1000 tokens);
3. a non-English answer is translated by **Claude Haiku** (`llm.translate`,
   `ASTRO_TRANSLATE_MODEL`), a strict prompt with the language's names tables;
4. emailed (HTML + text, the customer's language, question, chart name/date, link,
   disclaimer) and saved to `questions` (`charged=True`; `False` if refunded).

**Fallbacks that keep the 30-minute promise** (`model_used`, `route_reason` and
`translator` record what happened for every job):
* Ollama unreachable / model missing (`/api/tags`) → **Claude** writes it, directly in
  the customer's language (`route_reason=ollama_down`).
* Ollama errors, or runs past its budget (it may run until 25 min after the question,
  `ASTRO_EMAIL_ANSWER_SAFE_MIN`) → Claude (`ollama_error` / `ollama_timeout`).
* Projected late: queue position × the measured average local duration (last 5
  local jobs; `ASTRO_EMAIL_ANSWER_AVG_MIN`=4 until measured) would end more than 25
  min after the question → that job goes to Claude, ahead of the local queue
  (`projected_late`).
* Claude fails too (no key, credit balance too low, API down) → the **rule engine's**
  own reading with a one-line note in the customer's language
  (`model_used=engine`); still emailed and saved within the deadline.
* Translation fails → the English answer with a one-line note (`translator=failed`).
* The chart cannot be rebuilt, or the email cannot be sent → job `failed`, the
  emailed answer is **refunded**, the customer is told (if the email works).

**Alerts.** A job delivered after 30 min, more than `ASTRO_EMAIL_ANSWER_FALLBACK_ALERT`
(3) local-model fallbacks in an hour, any Claude failure, a failed job: logged at
ERROR (`astro.emailed_answers ALERT`) and emailed to `ASTRO_ADMIN_EMAILS`, at most one
email an hour (lines in between ride along with the next one).

**Env** (all optional; see `deploy/env.production.template`): `ASTRO_STARTER_ENABLED`
(1), `ASTRO_EMAIL_ANSWER_DEADLINE_MIN` (30), `ASTRO_EMAIL_ANSWER_MODEL` (qwen2.5:7b),
`ASTRO_EMAIL_ANSWER_OLLAMA_URL` (default `ASTRO_OLLAMA_URL`),
`ASTRO_EMAIL_ANSWER_SAFE_MIN` (25), `ASTRO_EMAIL_ANSWER_AVG_MIN` (4),
`ASTRO_EMAIL_ANSWER_NUM_PREDICT` (1000), `ASTRO_EMAIL_ANSWER_OLLAMA_MAX_S` (1200),
`ASTRO_EMAIL_ANSWER_FALLBACK_ALERT` (3), `ASTRO_TRANSLATE_MODEL` (Haiku),
`ASTRO_EMAIL_ANSWER_WORKER` (1; 0 = the queue only fills), `ASTRO_EMAIL_ANSWER_POLL_S` (5).
Mail must be configured (`ASTRO_SMTP_*`, Brevo) or every job fails and is refunded.

**Compose.** The `ollama` service must be running (`restart: unless-stopped`):
`cpus: "1.0"` (the website keeps a core), `mem_limit: 7g`, `OLLAMA_MAX_LOADED_MODELS=1`
(the earlier OOM was the 3b and 7b models loaded together), `OLLAMA_NUM_PARALLEL=1`,
`OLLAMA_KEEP_ALIVE=15m`, `OLLAMA_CONTEXT_LENGTH=4096`; port still loopback-only. With
one core expect roughly half of the 3.1 tok/s measured uncapped: ~8-15 min a job, so
at most one or two queued jobs are written locally and the rest by Claude. **Measure
before trusting it:** `docker compose up -d ollama`, then
`docker compose exec app python tools/emailed_answer_smoke.py --ollama-url http://ollama:11434`
(add `--lang hi`; `--no-claude` to see the local path alone). It runs one job on a
scratch database and prints the duration, `model_used` and the email, sending nothing.
Set `ASTRO_EMAIL_ANSWER_AVG_MIN` to what it measures.

**Watching the queue.** Admin → Traffic: "Emailed answers today" (count, median
minutes, late, failed, waiting now, model mix). Logs: `docker compose logs app | grep
emailed`. SQL: `select id, status, model_used, route_reason, translator, created_at,
finished_at, error from emailed_answer_jobs order by id desc limit 20;`.

**When Ollama is down.** Nothing to do for the customers: Claude writes every job
(the alert email says "fallbacks"). Check `docker compose ps ollama`, `docker compose
logs ollama`, `docker compose exec ollama ollama list` (is `qwen2.5:7b` pulled?), then
`docker compose up -d ollama`. If Claude is also failing (alert `claude_failed`, e.g.
the Anthropic credit balance), customers get the engine's reading with a note: top up
Anthropic. To stop selling while fixing: `ASTRO_STARTER_ENABLED=0` and redeploy.

Tests: `tests/test_emailed_answers.py` (fake Ollama `tests/fake_ollama.py` + fake
`anthropic`), `tests/e2e/test_starter_email.py`.

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
