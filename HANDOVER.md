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

- [ ] **Publish the source.** `stellium` is AGPL-3.0 and §13 obliges offering
      source to users of a network service. Currently unmet.
- [ ] Udyam registration *date* and Micro/Small/Medium not supplied — the footer
      renders only the number until they are.

**Quality**

- [ ] Guna Milan results are English-only; the koota notes are untranslated.
- [ ] Sade Sati and Kaal Sarp have API endpoints but no UI.
- [ ] Divisional charts never cross-checked against Jagannatha Hora. The
      internal check used `Fraction` to avoid float error at exact 3°20′
      boundaries and found zero mismatches, but that is self-verification.
- [ ] No way to upload or send a finished hand-written kundali scan.

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
