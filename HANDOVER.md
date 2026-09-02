# Handover — Divine Astro

Written 20 Aug 2026, updated 2 Sep 2026. Point the next session at this file.

Live at https://divineastro.org · GCP `divineastro`, zone `asia-south1-a`,
project `astro-505710` · static IP `8.234.96.206`.

## Fixed 2 Sep 2026

- **Every live chat answer was missing all Vedic content.** `/api/ask/stream`
  (the only endpoint the frontend actually calls) never set `result["vedic"]`,
  so yogas/dashas/sade-sati/vargottama never reached the narration prompt —
  confirmed the single highest-impact bug found this session. One-line fix in
  `main.py`'s `ask_stream()`, mirroring the unused `/api/ask`'s own line.
- **Kaal Sarp dashboard modal** always showed "No Kaal Sarp" — a key-name
  mismatch (`ks.is_formed` vs the real `ks.forms`, and `ks.type` treated as a
  string when it's an object). Fixed in `app.js`; the API and modal were
  otherwise already correct.
- **Chat response display cleanup**: paragraph fragmentation (every `\n` was
  its own `<p>`), bold-marker flicker while streaming, forced scroll-to-bottom
  on every token, a duplicate error bubble on mid-stream failure, silently
  dropped keystrokes while busy, starter chips that never went away, no
  stop/cancel control, and no truncation signal when a narration hit its token
  cap. See `app.js`'s `markdown()`/`scrollThread()`/the `#ask-form` handler.
- **Topic misclassification**: "will I get promoted" routed to the generic
  `timing` topic, not `career` — `topics.py` had "promotion" but not
  "promoted"/"promote", the same gap class as the dasha-compound fix below.
  Also widened `gather()`'s evidence caps to match the larger `Topic`
  definitions, added a post-generation date-auditor check (the "12/12 across a
  question sweep" claim below had no matching test — there's one now,
  `tests/test_llm_date_audit.py`), and grounded `generate_spiritual_guidance()`
  in the chart's actual computed remedies instead of three bare scalars.
- **UPI payment-claim notification.** `submit_utr()` used to grant nothing and
  notify nobody — an admin had to remember to check `/admin/upi/pending`. Now
  emails `ASTRO_ADMIN_EMAILS` via `app/mail.py` (new `ASTRO_SMTP_*` env vars,
  best-effort — a mail outage never fails the claim). See "No notification…"
  below, now checked off.
- **Muhurat finder** — new tool (`app/astro/muhurat.py`, `GET /api/muhurat`,
  a new tool-card/stage) scanning a date range for the classical red flags
  (rikta tithi, Amavasya, Bhadra) per event. Deliberately scoped to only the
  near-universal exclusions — see the module docstring for what it does not
  claim.
- **Guna Milan is now bilingual.** `matching.py`'s eight koota functions,
  Mangal Dosha, and every verdict/label/disclaimer string now have an
  independently-authored Hindi twin (`lang="hi"`), not a translation layer
  bolted on after. See "Guna Milan results are English-only" below, now
  checked off.
- **Single-question paid reports** — a new `single_question` product kind
  (`sq_career`, `sq_marriage`, `sq_money`, ₹249 each), gated on an actually-
  paid `Order` (new `Order.report_topic` column, migration `d4a2f9c1e7b3`),
  reusing the same `analyse()` + `llm.polish()` pipeline the chat already
  uses rather than new astrology logic. New `single_question_pdf()` in
  `pdf_report.py`, new gated `GET /api/pdf/single-question/{sid}` route, new
  store-modal section in `account.js`. Verified end-to-end against a live
  dev server in `ASTRO_GATEWAY=test` mode — `tests/test_single_question.py`.

All nine items were tracked as Jira issues in a new `DIVASTRO` project
(https://marketpandits-yavi.atlassian.net/browse/DIVASTRO-40 through -48) —
DIVASTRO-40 through 47 are done, DIVASTRO-48 (the credential rotations below)
is still open pending operator action.

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
| `test_money_path`, `test_coupons`, `test_single_question` | `ASTRO_GATEWAY=test` |
| `test_upi` | `ASTRO_GATEWAY=upi_manual`, `ASTRO_UPI_VPA` |
| `test_admin` | `ASTRO_ADMIN_EMAILS=owner@divineastro.org` |

Everything else (`test_delineation`, `test_vargas`, `test_matching`,
`test_panchang`, `test_muhurat`, `test_topic_routing`, `test_llm_date_audit`,
`test_mail`, `test_remedies_doshas`, `test_sweep`) needs no server and no
special env — run directly, e.g. `python -m tests.test_matching`.

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
- [x] No notification when a customer claims a UPI payment — fixed 2 Sep,
      see above. Requires `ASTRO_SMTP_HOST`/`ASTRO_ADMIN_EMAILS` to actually
      be set in production — neither is filled in on the VM yet.

**Security, from earlier in the project**

- [ ] **Rotate the Google OAuth client secret.** It was pasted in plaintext.
      Confirmed 2 Sep: read in exactly one place (`auth.py`), so rotation is
      a pure `.env.production` swap + redeploy, no code change — genuinely
      needs the operator, not something to do from a session.
- [ ] **Delete the old Cloudflare API token.** It carried billing and registrar
      rights. If you still want me to manage DNS, issue one scoped to
      Zone → DNS → Edit on `divineastro.org` only. Confirmed 2 Sep: not
      referenced anywhere in this repo — purely a Cloudflare-dashboard action.

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

**Quality**

- [x] Guna Milan results are English-only — fixed 2 Sep, see above.
- [x] Sade Sati and Kaal Sarp have API endpoints but no UI — turned out to be
      a UI bug, not a missing UI; fixed 2 Sep, see above.
- [ ] Divisional charts never cross-checked against Jagannatha Hora. The
      internal check used `Fraction` to avoid float error at exact 3°20′
      boundaries and found zero mismatches, but that is self-verification.
- [ ] No way to upload or send a finished hand-written kundali scan.
- [ ] The numeric verdict/score (`app/interpret/engine.py`'s `score_of()`) is
      still Western-dignity-only and never incorporates yogas/dashas/sade-sati
      — those live only in the `vedic` text block (now at least reaching the
      narration prompt, per the fix above). Folding them into the actual score
      is a real design question — what weight does a Raja Yoga get against a
      debilitated house lord? — deliberately left for its own pass.

---

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
