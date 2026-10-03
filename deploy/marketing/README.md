# Marketing image host

Static files bind-mounted into the Caddy container and served at
`https://divineastro.org/marketing/<file>` — see the `@marketing` block in
`../../Caddyfile`. Deliberately decoupled from the app's build/deploy: dropping
a file here needs no rebuild, no app restart, no `git push`.

On the server this directory is `/srv/divineastro/marketing`. Files here are
**not** committed to git (see `.gitignore`) — they are uploaded directly via
`scp`/`rsync` to that path. Name every file with a content hash or a
date+slug (e.g. `2026-10-01-free-questions-a1b2c3.png`) and never reuse a
filename for different bytes: the Cache-Control on this path is
`max-age=31536000, immutable`.

The daily Telegram post and the WhatsApp Channel email pack (DIVASTRO-113) are
set up separately; see `../daily_channels.md`.
