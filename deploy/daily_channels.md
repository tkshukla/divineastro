# Daily Panchang on Telegram and WhatsApp (DIVASTRO-113, DIVASTRO-116)

Every morning from 06:00 IST three jobs run inside the app container:

| Time | Job | What it does | Automatic? |
|---|---|---|---|
| 06:00 | `python -m app.telegram_daily` | Posts today's Panchang (Hindi; optionally English too) to the Telegram channel through the Bot API | Fully |
| 06:01 | `python -m app.whatsapp_pack` | Emails the owner a **"WhatsApp post for <date>"** message: the Hindi and English text, ready to paste, plus the image card as a PNG attachment | Owner pastes it. Kept as the fallback |
| 06:02 | `python -m app.whatsapp_channel` | Posts the Hindi message, as the caption of the image card, to the owner's own WhatsApp Channel through the `wa` connector (a linked device on a dedicated number) | Fully, once linked. **Unofficial**, see section 5 |

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
docker compose -f /srv/divineastro/docker-compose.yml exec -T app python -m app.whatsapp_channel --dry-run
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

## 2. WhatsApp Channel by hand (the fallback email)

Once the automatic post (section 5) is linked you can ignore this email on
days the post went out. It is still sent every day so the post is ready to
paste if the link ever breaks.

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
2 6 * * * docker compose -f /srv/divineastro/docker-compose.yml exec -T app python -m app.whatsapp_channel >> /srv/divineastro/deploy/daily_channels.log 2>&1 # divineastro-whatsapp-channel
```

Add the third line only after the WhatsApp connector is linked and tested
(section 5).

The evening katha (section 6) goes to the same WhatsApp Channel at 19:00:

```cron
0 19 * * * docker compose -f /srv/divineastro/docker-compose.yml exec -T app python -m app.katha --daily >> /srv/divineastro/deploy/daily_channels.log 2>&1 # divineastro-katha-daily
```

And the nightly reflection (section 7) at 22:00:

```cron
0 22 * * * docker compose -f /srv/divineastro/docker-compose.yml exec -T app python -m app.reflections --daily >> /srv/divineastro/deploy/daily_channels.log 2>&1 # divineastro-reflection-daily
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
| `ASTRO_DAILY_PACK_TO` | whatsapp_pack, whatsapp_channel | Recipient(s) of the pack and of the "unlinked" alert; blank uses `ASTRO_SUPPORT_EMAIL` |
| `ASTRO_SMTP_*`, `ASTRO_MAIL_FROM` | whatsapp_pack, whatsapp_channel | The existing Brevo settings |
| `ASTRO_WA_TOKEN` | whatsapp_channel, `wa` service | Secret shared by app and wa. Never printed |
| `ASTRO_WA_CHANNEL_LINK` | whatsapp_channel | `https://whatsapp.com/channel/…` |
| `ASTRO_WA_URL` | whatsapp_channel | Default `http://wa:3000` |
| `ASTRO_WA_WAIT` | whatsapp_channel | Seconds to wait for a reconnecting connector; default 60 |
| `ASTRO_DAILY_STATE_DIR` | all three | Default `/srv/data/daily_channels` |

**Once-a-day state:** `/srv/data/daily_channels/telegram.json`,
`whatsapp_pack.json` and `whatsapp_channel.json` (plus
`whatsapp_channel_alert.json`, the once-a-day "unlinked" email, and
`whatsapp_channel.cache.json`, the channel's resolved id), in the app's
`appdata` volume, so they survive rebuilds.
Each records what was sent per date (entries older than 60 days are pruned).
To resend, use `--force`, or delete the date from the file.

**Exit codes:** `0` sent (or already sent today), `1` a send failed (the reason
is in the log, never the token), `2` not configured or bad arguments.

**Flags:** `--date YYYY-MM-DD`, `--dry-run`, `--force`; Telegram also takes
`--langs hi,en` and `--with-card`; the pack also takes `--to` and, with
`--dry-run`, `--card-out file.png`; the channel poster also takes `--no-card`
(text only).

**The image card** is English only: Pillow on this server can't shape
Devanagari, and `app/social_card.py` refuses it. The template moved there from
`deploy/marketing/make_card.py`, which is now a wrapper with the same
command line.

---

## 5. WhatsApp Channel, automatic (DIVASTRO-116)

### What this is, and the risk you are accepting

Meta has **no official API** for posting to a WhatsApp Channel. This uses the
same route as WhatsApp Web: a small service (`wa`, built from `wa/` with the
open-source Baileys library) is linked as a **linked device** of a WhatsApp
number, exactly like a browser tab of web.whatsapp.com, and posts as that
number.

- It is **unofficial**. WhatsApp's terms do not allow unofficial clients, and
  WhatsApp can restrict or **ban the number** at any time. Use a **dedicated
  number** (a cheap second SIM), never your personal one.
- It does **one thing**: one post a day to your own channel. It does not
  message anybody, read chats, sync history or look at contacts.
- If WhatsApp changes its protocol, posting can stop until the `wa` service is
  updated to a newer Baileys version. You get the "unlinked" email, and the
  06:01 email pack still has the post to paste by hand.
- WhatsApp logs out linked devices when the **phone** with the number has not
  been used for about 14 days. Open WhatsApp on that phone at least once a
  week.
- To stop it at any time: on that phone, **WhatsApp → Linked devices → tap the
  "Chrome (Ubuntu)" device → Log out**. That alone cuts it off.

### a) The number and the channel

1. Put the dedicated SIM in a phone (an old Android phone is fine) and set up
   WhatsApp on that number.
2. The dedicated number must be the channel's **owner or an admin**. Either
   create the channel on that number (WhatsApp → **Updates** → **+** →
   **Create channel**), or, if your channel already exists on your own
   number, open it → tap its name → **Invite admins** → pick the dedicated
   number, and accept the invite on the dedicated phone.
3. Copy the channel link: open the channel → tap its name at the top →
   **Share** / **Copy link**. It looks like
   `https://whatsapp.com/channel/0029VaXXXXXXXXXXXXXXXX`.

### b) Configure the server (one time)

SSH to the VM, then:

1. Make a random secret for the app and the connector to share:

   ```bash
   openssl rand -hex 24
   ```

2. Edit `/srv/divineastro/.env` and add (see `deploy/env.production.template`):

   ```
   ASTRO_WA_TOKEN=<the hex string from step 1>
   ASTRO_WA_CHANNEL_LINK=https://whatsapp.com/channel/0029Va...
   ```

3. Build and start the connector, and recreate the app so it sees the new
   values (a plain `exec` does not re-read `.env`):

   ```bash
   docker compose -f /srv/divineastro/docker-compose.yml up -d --build wa
   docker compose -f /srv/divineastro/docker-compose.yml up -d app
   ```

   The `wa` service has **no public port**. Only the app can reach it
   (`http://wa:3000`, with the token). Its link to WhatsApp is kept in the
   `wadata` Docker volume, so rebuilds and restarts stay linked. Without
   `ASTRO_WA_TOKEN` it just idles and never contacts WhatsApp.

### c) Link the dedicated phone, option 1: QR code

1. Watch the connector's log:

   ```bash
   docker compose -f /srv/divineastro/docker-compose.yml logs -f wa
   ```

   It prints a QR code made of block characters. Windows PowerShell / Windows
   Terminal over SSH shows it fine; if it is cut off or wraps, **zoom the
   terminal out** (Ctrl and minus, or Ctrl + mouse wheel) or enlarge the
   window until the whole square shows. A new QR is printed every ~20
   seconds; always scan the newest one.
2. On the dedicated phone: WhatsApp → **⋮ (top right) → Linked devices** on
   Android, or **Settings → Linked devices** on iPhone → **Link a device**,
   and point the camera at the QR.
3. The log says `connected as +91••••••••NN`. Press **Ctrl+C** to stop
   watching the log (the service keeps running).

If nobody scans for a few minutes, the connector stops showing codes (status
`link_timeout`). Run `docker compose -f /srv/divineastro/docker-compose.yml restart wa`
for fresh ones.

QR won't show properly? Save it as an image and copy it to your laptop
(quickly: each QR expires after ~20 seconds):

```bash
docker compose -f /srv/divineastro/docker-compose.yml exec -T wa node src/cli.js qr > ~/wa-qr.png
# then on the laptop (PowerShell):  scp ubuntu@<server>:wa-qr.png .   and open it
```

### c') Link the dedicated phone, option 2: pairing code (no camera needed)

1. On the server, give the dedicated number in full with the country code,
   digits only (India: `91` + the 10-digit number):

   ```bash
   docker compose -f /srv/divineastro/docker-compose.yml exec wa node src/cli.js pair 91XXXXXXXXXX
   ```

   It prints `Pairing code: ABCD-EFGH`.
2. On the dedicated phone: **Linked devices → Link a device → Link with phone
   number instead**, and type the 8 characters. Do it within about a minute;
   if it expires, run the `pair` command again.

### d) Check the link

```bash
docker compose -f /srv/divineastro/docker-compose.yml exec wa node src/cli.js status
```

should print `{"connected":true,"me":"+91••••••••NN","linked_at":"…"}`.
Optional: `docker compose -f /srv/divineastro/docker-compose.yml exec wa node src/cli.js resolve https://whatsapp.com/channel/0029Va...`
prints the channel's id and the number's role there (`OWNER` or `ADMIN` is
needed to post).

### e) Test, then a real post

1. Preview (sends nothing):

   ```bash
   docker compose -f /srv/divineastro/docker-compose.yml exec -T app python -m app.whatsapp_channel --dry-run
   ```

2. Post for real (this **really posts** today's message to the channel):

   ```bash
   docker compose -f /srv/divineastro/docker-compose.yml exec -T app python -m app.whatsapp_channel
   ```

   It prints `posted hi for <date>`. Running it again prints `already posted`
   and posts nothing. Check the channel on your phone.
3. Then add the 06:02 cron line from section 3.

### If it stops posting

The job emails you **"WhatsApp channel posting is unlinked"** (at most once a
day, to `ASTRO_DAILY_PACK_TO`, else `ASTRO_SUPPORT_EMAIL`) with these steps,
and exits 1. The reason it gives:

| Reason | Meaning | Fix |
|---|---|---|
| `logged_out` | The device was logged out: on the phone, by WhatsApp, or because the phone was unused ~14 days | `docker compose ... restart wa`, then link again (c or c') |
| `awaiting_link` / `link_timeout` | Never linked, or the QR codes expired | Link (c or c') |
| `forbidden` | WhatsApp refused the number (restricted or banned) | Re-linking won't help. Post by hand from the 06:01 email |
| `unreachable` | The `wa` container is not running | `docker compose ... up -d wa`, then `docker compose ... logs wa` |

After fixing it, post today's message by running step e2 again.

If the job says the token was rejected, `ASTRO_WA_TOKEN` differs between the
two containers: run both `up -d` commands from step b3 again.

### Unlink / remove completely

1. On the dedicated phone: **Linked devices → the device → Log out**.
2. Remove the 06:02 cron line, then on the server:
   `docker compose -f /srv/divineastro/docker-compose.yml stop wa`, and
   optionally `docker compose -f /srv/divineastro/docker-compose.yml rm -f wa`
   and `docker volume rm divineastro_wadata` (deletes the stored link; check
   the exact name with `docker volume ls`).

---

## 6. Evening katha on the WhatsApp Channel (DIVASTRO-120)

At 19:00 `python -m app.katha --daily` posts one story teaser to the same
channel, through the same `wa` connector and the same `ASTRO_WA_*` settings
as section 5. The teaser stops at the story's turning point and links to the
whole story on the site (`/katha/<slug>`, Hindi; the English copy is at
`/en/katha/<slug>`), tagged `utm_campaign=katha`.

**Which story** (`app/katha.py`, `pick()`):

1. If today (New Delhi) has an observance that a story belongs to (its
   `match_names` hold the observance's exact name, e.g. "Indira Ekadashi",
   or its `tags` hold the observance key, e.g. `karwa_chauth`), that story,
   unless it was posted in the last 300 days. A name match beats a tag, a
   major festival beats a minor one.
2. Otherwise the next evergreen story (no tags, no match_names) that has never
   been posted, in file-name order; once all have gone out, the one posted
   longest ago.
3. Festival stories are never used on other days, unless every evergreen
   story was posted within the last 60 days.

Preview, post, re-post:

```bash
docker compose -f /srv/divineastro/docker-compose.yml exec -T app python -m app.katha --daily --dry-run
docker compose -f /srv/divineastro/docker-compose.yml exec -T app python -m app.katha --daily --dry-run --date 2026-10-29
docker compose -f /srv/divineastro/docker-compose.yml exec -T app python -m app.katha --slug savitri-satyavan --dry-run
```

`--daily` posts once per date (a retry or a second run does nothing; `--force`
re-sends that date's story). `--slug <slug>` posts one particular story once
(`--force` to repeat). Exit codes as in section 4. If the connector is
unlinked, the owner gets the same once-a-day "unlinked" email as the morning
post.

**State:** `/srv/data/daily_channels/katha.json` (what went out per date) and
`katha.cache.json` (`{slug: {"posted": ..., "id": ..., "day": ...}}`, the
history the picker reads; never pruned). Deleting a slug from the cache file
makes that story count as never posted.

### Adding a story

One story is one file, `app/katha_stories/<slug>.json`; nothing else to edit.
The index, the two pages, the sitemap, the share button and the rotation pick
it up after a deploy.

```json
{
  "slug": "savitri-satyavan",
  "category": "vrat-katha",
  "tags": ["vat_savitri", "vat_purnima"],
  "match_names": [],
  "hi": {"title": "...", "source": "...", "summary": "...", "teaser": ["para", "..."],
         "hook": "...", "rest": ["para", "..."], "message": "...", "note": ""},
  "en": {"title": "...", "source": "...", "summary": "...", "teaser": ["..."],
         "hook": "...", "rest": ["..."], "message": "...", "note": ""},
  "links": [["हिंदी लेबल", "/hi/path", "English label", "/path"]]
}
```

- `slug`: lowercase words joined by hyphens, the same as the file name.
- `category`: one of `vrat-katha devi shiva vishnu krishna ram ganesh
  mahabharata rishi other` (the index groups by it).
- `tags`: observance keys from `app/astro/festivals.py` (`karwa_chauth`,
  `ekadashi`, `diwali`, ...); `[]` for an evergreen story.
- `match_names` (optional): exact observance names from the same file, for a
  story that belongs to one particular day, e.g. `["Indira Ekadashi"]`.
- `hi` / `en`: every field present; all but `note` non-empty; `teaser` and
  `rest` non-empty lists of paragraphs; the Hindi title in Devanagari, the
  English one not. Markup is `*bold*` only (no `**`, HTML or Markdown
  links). The teaser post must stay under 4000 characters.
- `links` (optional): closing links, `[hindi label, hindi path, english label,
  english path]`.

Check before committing: `python -m tests.test_katha`. The app refuses to start
on a bad file, and the error names the file and the field.


---

## 7. Tonight's Reflection on the WhatsApp Channel (DIVASTRO-127)

At 22:00 `python -m app.reflections --daily` posts a short reflection to the
same channel (same `wa` connector, same `ASTRO_WA_*` settings as section 5):
English on top, Hindi below, the source when it is a quotation, and good
night. No links and no image.

```
*🌙 आज रात का विचार · Tonight's Reflection*

<English, 2-3 lines>

<Hindi, 2-3 lines>

_— <source>_            (only for a quotation or paraphrase)

🙏 शुभ रात्रि · Good night
```

**Which reflection** (`app/reflections.py`, `pick()`):

0. A date listed in `PINNED` (in the code) gets that reflection, whatever
   else is true (2026-10-04, the first post: Bhagavad Gita 2.47).
1. If today (New Delhi) has an observance named in a reflection's `tags`
   (`ekadashi`, `diwali`, `purnima`, ...), that reflection, unless it was posted
   in the last 300 days or its theme was last night's. Tagged reflections are
   used only on their days.
2. Otherwise the next never-posted untagged reflection in a fixed shuffled
   order that spreads the themes out; once all have gone out, the one posted
   longest ago.
3. Never the same theme two nights running; where possible not one of the
   last three nights' themes, and not the theme tomorrow's festival reflection
   needs.

Preview, post, re-post:

```bash
docker compose -f /srv/divineastro/docker-compose.yml exec -T app python -m app.reflections --daily --dry-run
docker compose -f /srv/divineastro/docker-compose.yml exec -T app python -m app.reflections --daily --dry-run --date 2026-11-08
docker compose -f /srv/divineastro/docker-compose.yml exec -T app python -m app.reflections --id gita-2-47 --dry-run
```

`--daily` posts once per date (`--force` re-sends that date's reflection);
`--id <id>` posts one reflection once (`--force` to repeat). Exit codes as in
section 4: 0 posted or already posted, 1 send failure, 2 not configured. If
the connector is unlinked the owner gets the same once-a-day "unlinked" email
as the morning post (one email per day across all three posts).

**State:** `/srv/data/daily_channels/reflection.json` (what went out per date)
and `reflection.cache.json` (`{id: {"posted", "id", "day"}}`, the history the
picker reads; never pruned).

### Adding a reflection

Append to `app/reflections.json`:

```json
{"id": "gita-2-48", "theme": "karma", "en": "line one\nline two", "hi": "पहली पंक्ति\nदूसरी पंक्ति",
 "source": "Bhagavad Gita 2.48", "tags": []}
```

- `id`: unique, lowercase-words-with-hyphens.
- `theme`: one of `mind attachment ego fear anger desire acceptance gratitude
  stillness karma impermanence compassion self-knowledge relationships
  discipline faith time silence forgiveness contentment`.
- `en` / `hi`: 2-3 lines joined by `\n`; English at most 300 characters;
  Hindi in Devanagari only (no Latin letters or digits); no `*` `_` `~` or links.
- `source` (optional): only for a genuine quotation with exact attribution,
  or a faithful paraphrase marked `(paraphrased)`. Never a quote you cannot
  verify.
- `tags` (optional): observance keys from `app/astro/festivals.py`; a tagged
  reflection is posted only on those days.

Check before committing: `python -m tests.test_reflections`.
