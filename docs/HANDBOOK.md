# Divine Astro — engineer's handbook

Live: **https://divineastro.org** · Repo: `github.com/tkshukla/divineastro` (branch `main`)
Server: Oracle Cloud VM (ARM64, Ubuntu 24.04), code at `/srv/divineastro`
Tracker: Jira project **DIVASTRO** · Last updated: 2 Nov 2026

> `HANDOVER.md` in this repo was written when the app lived on GCP. Its deploy
> section (`provision.ps1`, `/opt/divineastro`) is **out of date**; use this file.

---

## 1. What the product is

A Vedic astrology web app for Indian users, mainly on phones, in 13 languages
(en, hi, kn, te, ta, ml, bn, or, pa, ne, as, mr, gu).

- **Free:** a kundali (birth chart), first questions answered in chat, a daily Panchang,
  and about 1,000 SEO pages (panchang, rahu kaal, choghadiya, rashifal, vrat/tyohar,
  muhurat, nakshatra, learn, katha, city pages).
- **Paid:**
  - Starter, ₹21: 3 detailed answers by email.
  - Topic reports (career, marriage, wealth).
  - Kundali Milan report.
  - Comprehensive Life Book PDF.
  - Prices are in `app/billing.py`. A festive offer runs until 15 Nov 2026.
- **Revenue:** payments go through PayU. Google AdSense runs on content pages.

### The one design rule to keep

**The astrology is never done by a language model.**

- The chart comes from the Swiss Ephemeris (via the `stellium` library).
- A deterministic rule engine (`app/interpret/`) picks the evidence and reaches the verdict.
- Claude (Anthropic API) only rewrites that verdict into plain, friendly language and
  translates it. The prompt forbids it to add or change any placement or date.
- If the API key is missing, the engine answers in its own words.

`README.md` §"What computes what" and §"How an answer is produced" explain this in depth.
Read them.

---

## 2. Architecture

```
 Browser (SPA + SEO pages)
      │ HTTPS
 ┌────▼─────┐   Docker Compose project "divineastro"  (/srv/divineastro/docker-compose.yml)
 │  caddy   │  :80/:443, Let's Encrypt TLS, security headers/CSP, /marketing static files
 └────┬─────┘
      │ http://app:8000
 ┌────▼─────┐      ┌──────────┐
 │   app    │──────│    db    │  Postgres 16 (volume pgdata, no host port)
 │ FastAPI  │      └──────────┘
 │ uvicorn  │──────┐
 └──────────┘      │ http://wa:3000 (shared token)
               ┌───▼───┐            ┌──────────┐
               │  wa   │ WhatsApp   │ ollama   │ local LLM fallback, currently STOPPED
               │ node  │ linked dev.│ (opt.)   │ (too slow on 2 cores)
               └───────┘            └──────────┘
 External: Anthropic API (answers), PayU (payments), Google OAuth, SMTP (mail),
           Telegram Bot API, Web Push (VAPID), IndexNow, AdSense, GitHub Actions (CI)
```

Ports 80/443 on this VM belong to this project's Caddy. The other apps on the VM are
reached through a Cloudflare Tunnel. Every external service, IP, DNS record and
firewall rule is in `INFRA.md` and `00-VM-OVERVIEW.md`. Both are confidential: the owner
keeps them, and on the VM they are in `~/handbook/`. They are **not** in this public repo.

### Stack

| Layer | Tech |
|---|---|
| Backend | Python 3.12, FastAPI, SQLAlchemy, Alembic, Authlib |
| Astronomy | `stellium` 0.22 (Swiss Ephemeris), a bundled GeoNames city index |
| Front end | Vanilla JS single-page app in `app/static/` with no build step. SEO pages are rendered on the server in Python. |
| PDFs | Typst, with script fonts installed in the image for the Indic languages |
| DB | Postgres 16 in production; SQLite for local tests |
| Proxy | Caddy 2 |

---

## 3. Code map

```
app/
  main.py            FastAPI app, lifespan (starts the push sender and the emailed-answer worker),
                     chart/ask/PDF routes
  chart_service.py   builds the chart (stellium), transits, dasha, solar return, wheel SVG
  interpret/         THE ENGINE: topics.py (question → topic/intent), engine.py (evidence,
                     scoring), periods.py / window.py (timing), knowledge.py
  astro/             Vedic modules: panchang, choghadiya, muhurat, doshas, matching (Milan),
                     vargas, ashtakavarga, jaimini, remedies, festivals, names_*.py
                     (localised names)
  llm.py             prompt + Anthropic call that turns engine evidence into plain language;
                     Ollama fallback
  emailed_answers*.py  Starter product: DB-backed queue + worker that writes and emails answers
  billing.py         products, prices, credits ledger, orders
  gateways.py        payment gateways (payu live; cashfree, instamojo, upi_manual, test)
  upi.py, coupons.py, guest_checkout.py   UPI claims, coupon codes, buying without an account
  auth.py, email_auth.py, phone_auth.py, otp.py
                     sign-in: Google OAuth, email OTP, phone OTP, username+password.
                     One identity scheme: (provider, provider_sub)
  api_account.py     /api account endpoints: me, births, history, history threads, orders,
                     ledger
  threads.py         rebuilds a past conversation for "My questions"
  db.py              SQLAlchemy models + session
  analytics.py, api_traffic.py   first-party event and visit tracking, /admin traffic report
  pdf_report.py, pdf_i18n.py, milan_report.py, report_text.py   PDF generation (Typst)
  person_name.py     anonymity helpers (no "Native" or real name printed when a name is blank)
  seo_*.py, *_pages.py, *_text.py   server-rendered SEO pages and their copy
  i18n.py, lang_data/   language registry; per-language tables (READY flags show what is done)
  telegram_daily.py, whatsapp_channel.py, whatsapp_pack.py, katha.py, reflections.py,
  daily_message.py   daily channel posts (cron-driven, see §7)
  push.py            daily web-push sender (in-process loop; assumes ONE uvicorn worker)
  indexnow.py        pings search engines with changed URLs
  static/            SPA: index.html, app.js (chat/chart), account.js (sign-in, store,
                     history), i18n/*.json (UI strings), sw.js (service worker), admin.*
migrations/versions/   Alembic; runs automatically when the container starts
tests/               ~100 suites (unit + integration over HTTP) + tests/e2e (Playwright, ~36)
wa/                  Node WhatsApp connector (Baileys-style linked device), src/cli.js
deploy/              healthcheck.sh (watchdog), daily_channels.md (channel runbook),
                     env template
marketing/           social assets, served at /marketing/* by Caddy
docs/                i18n.md (how translation works), manual-uat-checklist.md (payments),
                     SEO audits
```

### How a question is answered

1. The browser POSTs to `/api/ask/stream`, an SSE stream. Caddy disables buffering for this path.
2. `interpret.topics` routes the question to a topic and an intent. `topics.is_follow_up`
   decides whether earlier Q&A is relevant (DIVASTRO-169).
3. `interpret.engine` gathers scored evidence from the chart, plus timing windows.
4. `llm.py` sends that evidence to Claude (`ASTRO_CLAUDE_MODEL`) with SYSTEM_PROMPT.
   - Rules: plain language, "their life first, the sky second", a banned-jargon list,
     one question at a time.
   - It streams the text back.
5. The answer is logged in `QuestionLog` and credits are debited from the ledger.

---

## 4. Data

- **Postgres DB:** `astro`, user `astro`, password from `POSTGRES_PASSWORD` in `.env`.
- **Main tables:**
  - users, birth profiles
  - QuestionLog (questions and answers)
  - ledger: credits and email credits
  - orders: with order_data, guest_* fields and UTR for UPI
  - coupons
  - emailed_answer_jobs
  - push_subscriptions
  - events and visits (analytics)
  - feedback
- **Schema changes:** add an Alembic migration in `migrations/versions/`. It applies on
  container start.
- **Postgres enum warning:** local tests run on SQLite, which does **not** enforce
  enums. Check any new status or type value against Postgres. This has broken
  `/admin` before.
- Volumes: `pgdata` (DB), `appdata` (chart scratch space, geo index), `wadata`
  (WhatsApp login; treat it like a password), `caddydata` (certificates).

### Backups

- **Nightly:** `/home/ubuntu/backup_apps.sh`, written 2 Nov 2026, runs at 02:40 once the
  owner has enabled it.
  - It writes `/srv/backups/apps/divineastro-*.sql.gz` and keeps 14 days.
  - It sanity-checks each dump before keeping it.
- **Before risky migrations**, take a manual dump as well:

```bash
cd /srv/divineastro
docker compose exec -T db pg_dump -U astro -d astro --clean --if-exists | gzip -9 > /srv/backups/divineastro-$(date +%Y%m%d-%H%M).sql.gz
```

- **Restore:** `zcat <dump> | docker exec -i divineastro-db-1 psql -U astro -d astro`.
- **Still to do:** an off-VM copy. Every backup is on the VM's own disk.

---

## 5. Configuration (`/srv/divineastro/.env`)

Never commit `.env`. Back it up before you edit it. Variable names, grouped (values are
secrets):

| Group | Variables |
|---|---|
| Core | `ASTRO_BRAND`, `ASTRO_SITE_URL`, `ASTRO_SECRET_KEY`, `ASTRO_COOKIE_SECURE`, `ASTRO_DEV_LOGIN` (must be 0 in production), `POSTGRES_PASSWORD`, `ASTRO_ADMIN_EMAILS` |
| Answers | `ANTHROPIC_API_KEY`, `ASTRO_CLAUDE_MODEL`, `ASTRO_CLAUDE_MAX_TOKENS`, `ASTRO_FREE_QUESTIONS`, `ASTRO_EMAIL_ANSWER_WRITER` (claude default) |
| Sign-in | `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` |
| Payments | `ASTRO_GATEWAY` (= `payu` live), `PAYU_*`, `CASHFREE_*`, `INSTAMOJO_*`, `ASTRO_UPI_VPA`, `ASTRO_UPI_PAYEE` |
| Mail | `ASTRO_SMTP_HOST/PORT/USER/PASS`, `ASTRO_MAIL_FROM`. If mail fails, every emailed answer fails and is refunded. |
| Push / channels | `ASTRO_VAPID_*`, `ASTRO_TELEGRAM_BOT_TOKEN/CHAT_ID/LANGS`, `ASTRO_WA_TOKEN`, `ASTRO_WA_CHANNEL_LINK`, `ASTRO_INDEXNOW_KEY` |
| Legal footer | `ASTRO_LEGAL_NAME`, `ASTRO_ADDRESS`, `ASTRO_SUPPORT_*`, `ASTRO_GSTIN`, `ASTRO_PAN`, `ASTRO_UDYAM_*` |

---

## 6. Day-to-day operations

### Deploy (after a PR is merged to `main`)

```bash
git -C /srv/divineastro pull --ff-only origin main
docker compose -f /srv/divineastro/docker-compose.yml up -d --build app
docker compose -f /srv/divineastro/docker-compose.yml ps app      # wait for "(healthy)"
curl -s https://divineastro.org/api/health
```

- Migrations run on start. Take a DB dump first if the release has a migration.
- After a **Caddyfile** change, run `docker compose restart caddy`. A plain reload reads
  a stale copy of the bind-mounted file.
- After a `docker-compose.yml` change, run `docker compose up -d` for the affected
  service.

### Logs and status

```bash
cd /srv/divineastro
docker compose ps
docker compose logs app --since 30m
docker compose exec caddy tail -f /data/access.log         # JSON access log
```

### Admin

- `https://divineastro.org/admin` is open only to the emails in `ASTRO_ADMIN_EMAILS`.
- It has: metrics, a traffic report (per day and funnel), users (block, grant credits),
  orders, UPI verification, manual orders, coupons, feedback, questions, kundali
  fulfilment, and system health.

### Watchdog

- Cron runs `deploy/healthcheck.sh` every minute.
- It checks `/api/health`, restarts the app container after repeated failures, and alerts
  through ntfy.sh.
- Settings are in `~/.divineastro-watchdog.env`.

### WhatsApp connector

The connector is a linked device on the dedicated number (ask the owner). It unlinks itself sometimes.

```bash
docker compose exec -T wa node src/cli.js status
docker compose exec -T wa node src/cli.js pair <number>       # prints a pairing code; enter it on the phone:
                                                              # WhatsApp > Linked devices > Link with phone number
```

---

## 7. Scheduled jobs (crontab of user `ubuntu`)

All times are IST and run inside the app container, logging to
`deploy/daily_channels.log`.

| Time | Job |
|---|---|
| every min | `deploy/healthcheck.sh` (watchdog) |
| 06:00 | `app.telegram_daily --with-card`: Panchang to the Telegram channel |
| 06:01 | `app.whatsapp_pack`: emails the owner a ready-to-paste WhatsApp post |
| 06:02 | `app.whatsapp_channel`: posts the Panchang to the WhatsApp Channel through `wa` |
| 06:20 | `app.indexnow --daily` |
| 19:00 | `app.katha --daily` |
| 22:00 | `app.reflections --daily` |
| 08:02 alternate days | Claude Code headless run that drafts social posts (`deploy/marketing/DAILY_TASK_VM.md`) |

These also run inside the app process:
- the web-push sender (`push.py`);
- the emailed-answer worker (`emailed_answers.py`, one job at a time). Set
  `ASTRO_EMAIL_ANSWER_WORKER=0` to turn it off.

The full channel runbook is `deploy/daily_channels.md`.

---

## 8. Development workflow

1. Branch off `main` and write code plus tests.
2. Open a PR. GitHub Actions (`.github/workflows/ci.yml`) runs:
   - unit suites, with no server;
   - integration suites against a live server with `ASTRO_GATEWAY=test`;
   - `test_upi` with `ASTRO_GATEWAY=upi_manual`;
   - the Playwright e2e suites.
3. The owner approves, the PR is merged, then deploy (§6), check the live site, and close
   the Jira ticket.
4. A release that touches payments also needs the manual check in
   `docs/manual-uat-checklist.md`. A real PayU payment can't be automated.

### Running tests locally

```bash
# unit suite (any single file under tests/)
ASTRO_SECRET_KEY=ci ASTRO_DATABASE_URL=sqlite:////tmp/x.db python -m tests.test_follow_up
# SEO snapshots after changing page output or i18n JSON:
python -m tests.test_seo_snapshots --update
# e2e (needs playwright + chromium); each test starts its own server
python -m tests.e2e.test_history
```

Gotchas:
- Some suites need specific env vars: `ASTRO_GATEWAY`, `ASTRO_ADMIN_EMAILS`, `ASTRO_UPI_VPA`.
  CI's yml shows exactly which.
- e2e tests are occasionally flaky in CI (timeouts or an external 502). Rerun once before
  you debug.
- `tests/test_sweep.py` is a 1,200-check sweep that takes about 90 CPU-minutes. It runs
  only on demand.

### Translation

- UI strings are in `app/static/i18n/<lang>.json`.
- Page and PDF copy is in `*_text.py`, `lang_data/`, and `pdf_i18n.py`.
- `docs/i18n.md` explains the process.
- A language shows up only where its `READY` set includes that surface.

---

## 9. Known issues and open items

- **Backups are on the VM only:** there is no off-VM copy yet (§4).
- **Ollama is stopped:** at about 25 minutes per answer on 2 cores it is too slow. The
  Claude API writes every answer, so an Anthropic outage means the engine's own,
  plainer text.
- **WhatsApp connector:** it is unofficial and can get unlinked. Re-pair it (§6).
- **AdSense:** a "dishonest declarations" notice is pending. The fix is in the
  AdSense payments profile (payee name, account type, address), not in the code.
- **Open tickets:**
  - DIVASTRO-158: guest checkout for the Milan report (the Starter already supports it).
  - DIVASTRO-166: the festive social campaign.
- **Only one uvicorn worker:** the push sender and the email worker are in-process. Don't
  scale to several workers without moving them out first.

## 10. Accounts and services the owner controls

GitHub repo, Jira, Google Cloud console (OAuth client), Google Search Console,
Google Business Profile, AdSense, PayU merchant dashboard, Anthropic console,
SMTP mailbox, Telegram bot, the WhatsApp number/channel, Metricool (Facebook
scheduling), Oracle Cloud, and Cloudflare/DNS registrar. Ask the owner for access.
Nobody keeps credentials in the repo.
