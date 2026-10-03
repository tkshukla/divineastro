# Daily Panchang on Telegram and WhatsApp (DIVASTRO-113)

Every morning at 06:00 IST two jobs run inside the app container:

| Job | What it does | Automatic? |
|---|---|---|
| `python -m app.telegram_daily` | Posts today's Panchang (Hindi; optionally English too) to the Telegram channel through the Bot API | Fully |
| `python -m app.whatsapp_pack` | Emails the owner a **"WhatsApp post for <date>"** message: the Hindi and English text, ready to paste, plus the image card as a PNG attachment | Owner pastes it. Meta doesn't allow automated posts to a WhatsApp Channel |

The message (`app/daily_message.py`) covers New Delhi: date and vaar, tithi
(with its end time), nakshatra, sunrise and sunset, Rahu Kaal, Abhijit, the
day's vrat and festivals with their first validated puja timing (the same data
as `/vrat-tyohar`), where the Moon is today (with a link to `/rashifal`), and
links to `/panchang` and `/vrat-tyohar`. The Hindi post links to the `/hi/`
pages. Every link is tagged
`utm_source=telegram|whatsapp&utm_medium=channel&utm_campaign=daily-<date>`,
so visits from the posts show up in the `/admin` Traffic panel.

Preview any day without sending anything:

```bash
docker compose -f /srv/divineastro/docker-compose.yml exec -T app python -m app.telegram_daily --dry-run --langs hi,en
docker compose -f /srv/divineastro/docker-compose.yml exec -T app python -m app.whatsapp_pack --dry-run --date 2026-11-08
```

---

## 1. Telegram setup, step by step (one time, about 10 minutes)

You need the Telegram app on your phone (or Telegram Desktop) and a Telegram
account.

### a) Create the bot

1. In Telegram, tap the search bar and search for **@BotFather**. Open the
   one with the blue verified tick.
2. Tap **Start** (or send `/start`).
3. Send `/newbot`.
4. BotFather asks for a **name**. This is what people see, for example
   `Divine Astro Panchang`.
5. It then asks for a **username**. It must end in `bot` and nobody else can
   already have it, for example `divineastro_panchang_bot`.
6. BotFather replies with a long **token** like `1234567890:AAH...`.
   **Treat it like a password.** Anyone who has it can post as your bot.
   Don't paste it in chats or screenshots. If it ever leaks, send `/revoke` to
   BotFather and use the new token it gives you.

### b) Create the channel

1. In Telegram: the pencil / "new message" button → **New Channel**.
2. Name: `Divine Astro – दैनिक पंचांग` (or whatever you like). Add a
   description and photo if you want, then tap **Next**.
3. Choose **Public** and pick a link, for example `t.me/divineastro_panchang`.
   The part after `t.me/` is the channel's username. Public is recommended:
   anyone can find and join it, and its chat id is simply `@` + that username.
   (A private channel works too. See step d.)
4. Skip adding subscribers for now.

### c) Make the bot an admin of the channel

1. Open the channel → tap its name at the top → **Administrators** (or
   **Manage channel → Administrators**) → **Add Admin**.
2. Search for your bot's username (`divineastro_panchang_bot`), select it.
3. Make sure **Post Messages** is switched on. Everything else can be off.
4. Tap **Done** / **Save**.

### d) Find the chat id

- **Public channel:** the chat id is `@` followed by the channel username,
  for example `@divineastro_panchang`. That's all.
- **Private channel:** post any message in the channel. Then, on a computer,
  open `https://api.telegram.org/bot<TOKEN>/getUpdates` in a browser
  (replace `<TOKEN>` with your token, keeping the word `bot` in front of it).
  Find `"chat":{"id":-100…` in the text. That number, including the minus
  sign, is the chat id. (If the page shows `"result":[]`, post another message
  in the channel and reload.) Clear the browser history afterwards because the
  URL contains the token.

### e) Put the values on the server

1. On the VM, edit `/srv/divineastro/.env` and add (see
   `deploy/env.production.template`):

   ```
   ASTRO_TELEGRAM_BOT_TOKEN=1234567890:AAH...your token...
   ASTRO_TELEGRAM_CHAT_ID=@divineastro_panchang
   ASTRO_TELEGRAM_LANGS=hi            # or hi,en to also post English
   ASTRO_DAILY_PACK_TO=you@example.com   # blank = ASTRO_SUPPORT_EMAIL
   ```

2. Recreate the app container so it picks up the new `.env`. A plain
   `exec` does **not** re-read it:
   `docker compose -f /srv/divineastro/docker-compose.yml up -d app`
3. Test it once. This **really posts** to the channel:
   `docker compose -f /srv/divineastro/docker-compose.yml exec -T app python -m app.telegram_daily`
   It should print `posted hi for <date>`. Running it again prints
   `already posted` and posts nothing.

---

## 2. WhatsApp Channel: what to do each morning

You'll get an email titled **WhatsApp post for 3 October 2026** at about 06:00.
On your phone:

1. Open the email and save the attached image (`divineastro-panchang-<date>.png`).
2. Open WhatsApp → **Updates** → your Divine Astro channel.
3. Attach the image and paste the Hindi text (between the `==== हिंदी ====`
   lines) as its caption, or send it as a second message. Send.
4. Optionally do the same with the English text.

`*stars*` are WhatsApp's bold, so paste them as they are.

---

## 3. Cron lines (owner installs them with `crontab -e`; not installed by the code)

The host clock is IST (`date` prints `IST`), so `0 6` means 06:00 IST, the
same convention as the existing 08:02 marketing job. Check with `date`
before installing.

```cron
0 6 * * * docker compose -f /srv/divineastro/docker-compose.yml exec -T app python -m app.telegram_daily >> /srv/divineastro/deploy/daily_channels.log 2>&1 # divineastro-telegram-daily
1 6 * * * docker compose -f /srv/divineastro/docker-compose.yml exec -T app python -m app.whatsapp_pack >> /srv/divineastro/deploy/daily_channels.log 2>&1 # divineastro-whatsapp-pack
```

Add `--with-card` to the Telegram line to post the image card above the text.
A retry line such as `30 6 * * *` with the same command is safe: each job
records what it already sent and posts only what is missing.

---

## 4. Reference

**Environment** (`/srv/divineastro/.env`, documented in `deploy/env.production.template`):

| Variable | Used by | Notes |
|---|---|---|
| `ASTRO_TELEGRAM_BOT_TOKEN` | telegram_daily | Secret. Never printed: error messages have it replaced by `<token>` |
| `ASTRO_TELEGRAM_CHAT_ID` | telegram_daily | `@channelusername` or `-100…` |
| `ASTRO_TELEGRAM_LANGS` | telegram_daily | `hi` (default) or `hi,en` |
| `ASTRO_DAILY_PACK_TO` | whatsapp_pack | Recipient(s); blank uses `ASTRO_SUPPORT_EMAIL` |
| `ASTRO_SMTP_*`, `ASTRO_MAIL_FROM` | whatsapp_pack | The existing Brevo settings |
| `ASTRO_DAILY_STATE_DIR` | both | Default `/srv/data/daily_channels` |

**Once-a-day state:** `/srv/data/daily_channels/telegram.json` and
`whatsapp_pack.json`, in the app's `appdata` volume, so they survive rebuilds.
Each records what was sent per date (entries older than 60 days are pruned).
To resend, use `--force`, or delete the date from the file.

**Exit codes:** `0` sent (or already sent today), `1` a send failed (the reason
is in the log, never the token), `2` not configured or bad arguments.

**Flags:** `--date YYYY-MM-DD`, `--dry-run`, `--force`; Telegram also takes
`--langs hi,en` and `--with-card`; the pack also takes `--to` and, with
`--dry-run`, `--card-out file.png`.

**The image card** is English only: Pillow on this server can't shape
Devanagari, and `app/social_card.py` refuses it. The template moved there from
`deploy/marketing/make_card.py`, which is now a wrapper with the same
command line.
