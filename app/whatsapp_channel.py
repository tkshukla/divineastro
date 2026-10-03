"""Post the daily Panchang to the owner's own WhatsApp Channel (DIVASTRO-116).

    python -m app.whatsapp_channel [--date YYYY-MM-DD] [--force] [--dry-run]
                                   [--no-card]

Meta has no API for posting to a WhatsApp Channel, so this goes through the
`wa` compose service (wa/, Baileys): a linked device on the owner's dedicated
WhatsApp number, reachable only as http://wa:3000 on the compose network. The
owner asked for this and accepts the risk (unofficial; the number could be
restricted). Scope is deliberately tiny: ONE post a day to the owner's own
channel. Nothing here messages people or reads chats.

Run from host cron at 06:02 IST inside the app container (see
deploy/daily_channels.md section 5). The post is the Hindi WhatsApp message
(*bold*) as the caption of the English image card — the same text and card
the 06:01 email pack (app/whatsapp_pack.py) carries; that email keeps running
as the fallback.

Configuration (the app's .env):
  ASTRO_WA_TOKEN         shared secret with the wa service (X-WA-Token header).
                         Secret: never printed.
  ASTRO_WA_CHANNEL_LINK  the channel's invite link, https://whatsapp.com/channel/…
                         Resolved to the channel JID once, then cached in
                         /srv/data/daily_channels/whatsapp_channel.cache.json.
  ASTRO_WA_URL           default http://wa:3000
  ASTRO_WA_WAIT          seconds to wait for a reconnecting connector (default 60)

If the connector is not linked (logged out, never linked, number refused) or
not reachable, the owner gets ONE email that day (ASTRO_DAILY_PACK_TO, else
ASTRO_SUPPORT_EMAIL) with the re-link steps, and the job exits 1.

Once a day: recorded in /srv/data/daily_channels/whatsapp_channel.json
(app/daily_state.py); --force posts again.

Exit codes: 0 posted (or already posted today), 1 not linked / post failed,
2 not configured / bad arguments. --dry-run prints the post and needs nothing.
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import io
import os
import sys
import time

import httpx

from . import daily_state, mail, whatsapp_pack

JOB = "whatsapp_channel"
ALERT_JOB = "whatsapp_channel_alert"
DEFAULT_URL = "http://wa:3000"
TIMEOUT = 150.0              # the connector itself gives up on a send after 120 s
CAPTION_LIMIT = 1024         # stay inside WhatsApp's media-caption limit; longer = text only
TRANSIENT = {"starting", "connecting", "reconnecting"}

# Patched by the tests.
_sleep = time.sleep
_transport: httpx.BaseTransport | None = None


class ConnectorError(RuntimeError):
    def __init__(self, message: str, status: int | None = None):
        super().__init__(message)
        self.status = status


class Unlinked(RuntimeError):
    """The connector is unreachable or not linked to WhatsApp."""


class Client:
    def __init__(self, url: str, token: str):
        self.url = url.rstrip("/")
        self._token = token
        self._http = httpx.Client(base_url=self.url, timeout=TIMEOUT, transport=_transport,
                                  headers={"X-WA-Token": token})

    def _redact(self, text: str) -> str:
        return text.replace(self._token, "<token>") if self._token else text

    def _call(self, method: str, path: str, body: dict | None = None) -> dict:
        try:
            r = self._http.request(method, path, json=body)
        except httpx.HTTPError as exc:
            raise Unlinked(self._redact(f"connector at {self.url} unreachable: "
                                        f"{type(exc).__name__}: {exc}")) from None
        try:
            data = r.json()
        except ValueError:
            data = {}
        if r.status_code == 401:
            raise ConnectorError("the wa service rejected ASTRO_WA_TOKEN — it must be the same "
                                 "value for app and wa (both read .env); recreate both containers",
                                 401)
        if r.status_code != 200:
            raise ConnectorError(self._redact(f"{method} {path}: HTTP {r.status_code}: "
                                              f"{data.get('error', '')}"), r.status_code)
        return data

    def status(self) -> dict:
        return self._call("GET", "/status")

    def resolve(self, invite: str) -> dict:
        return self._call("POST", "/channel/resolve", {"invite": invite})

    def post(self, jid: str, text: str, png: bytes | None, thumb: bytes | None) -> str | None:
        body: dict = {"jid": jid, "text": text}
        if png:
            body["image_base64"] = base64.b64encode(png).decode()
            if thumb:
                body["thumbnail_base64"] = base64.b64encode(thumb).decode()
        return self._call("POST", "/channel/post", body).get("id")


def thumbnail(png: bytes) -> bytes:
    """Small JPEG preview for the channel feed (the connector has no image library)."""
    from PIL import Image
    img = Image.open(io.BytesIO(png)).convert("RGB")
    img.thumbnail((96, 96))
    out = io.BytesIO()
    img.save(out, "JPEG", quality=60)
    return out.getvalue()


def wait_connected(client: Client, wait_s: float) -> dict:
    """Status once connected; raise Unlinked when it is not (after waiting out a
    transient reconnect for up to `wait_s` seconds)."""
    deadline = time.monotonic() + wait_s
    while True:
        st = client.status()
        if st.get("connected"):
            return st
        reason = st.get("reason") or "unknown"
        if reason not in TRANSIENT or time.monotonic() >= deadline:
            raise Unlinked(f"WhatsApp connector is not linked (reason: {reason})")
        _sleep(5)


def channel_jid(client: Client, link: str) -> str:
    """The channel JID for `link`: from the cache, else asked once and cached."""
    cached = daily_state.recall(JOB, "channel")
    if isinstance(cached, dict) and cached.get("link") == link and cached.get("jid"):
        return cached["jid"]
    info = client.resolve(link)
    jid, role = info.get("jid"), (info.get("role") or "").upper()
    if not jid:
        raise ConnectorError(f"no channel found for {link}")
    if role not in ("OWNER", "ADMIN"):
        raise ConnectorError(f"the linked number is not an owner/admin of channel "
                             f"{info.get('name')!r} (role {role or 'none'}); it cannot post there")
    daily_state.remember(JOB, "channel", {"link": link, "jid": jid, "name": info.get("name"),
                                          "role": role})
    print(f"whatsapp_channel: channel {info.get('name')!r} resolved to {jid} (cached)")
    return jid


def alert_body(reason: str, day: dt.date) -> str:
    return "\n".join([
        f"The automatic WhatsApp Channel post for {day.isoformat()} did NOT go out.",
        f"Reason: {reason}",
        "",
        "WhatsApp channel posting is unlinked — re-link with these steps",
        "(details: deploy/daily_channels.md, section 5):",
        "",
        "1. SSH to the server.",
        "2. Restart the connector so it shows a fresh QR code:",
        "     docker compose -f /srv/divineastro/docker-compose.yml restart wa",
        "3. Watch its log (zoom the terminal out if the QR is cut off):",
        "     docker compose -f /srv/divineastro/docker-compose.yml logs -f wa",
        "4. On the phone with the channel number: WhatsApp > Linked devices >",
        "   Link a device, and scan the QR. Ctrl+C the log once it says 'connected'.",
        "   No camera handy? Use a pairing code instead:",
        "     docker compose -f /srv/divineastro/docker-compose.yml exec wa node src/cli.js pair 91XXXXXXXXXX",
        "   and on the phone choose 'Link with phone number instead' and type the code.",
        "5. Post today's message:",
        "     docker compose -f /srv/divineastro/docker-compose.yml exec -T app python -m app.whatsapp_channel",
        "",
        "If the reason is 'forbidden', WhatsApp has restricted the number; re-linking will",
        "not help. Today's post is also in the 'WhatsApp post for ...' email: you can",
        "post it by hand as before.",
        "",
        "You get this email at most once a day.",
    ])


def alert_owner(reason: str, day: dt.date) -> None:
    if daily_state.sent(ALERT_JOB, day):
        print("whatsapp_channel: owner already alerted today", file=sys.stderr)
        return
    to = whatsapp_pack.recipients()
    if not to:
        print("whatsapp_channel: no owner email (ASTRO_DAILY_PACK_TO / ASTRO_SUPPORT_EMAIL) "
              "to alert", file=sys.stderr)
        return
    if mail.send(to, "WhatsApp channel posting is unlinked", alert_body(reason, day)):
        try:
            daily_state.mark(ALERT_JOB, day, "email")
        except OSError as exc:
            print(f"whatsapp_channel: alerted, but could not record it: {exc}", file=sys.stderr)
        print(f"whatsapp_channel: emailed the re-link steps to {', '.join(to)}", file=sys.stderr)
    else:
        print("whatsapp_channel: could not email the owner (mail not configured?)",
              file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m app.whatsapp_channel",
                                 description="Post today's Panchang to the WhatsApp Channel.")
    ap.add_argument("--date", help="YYYY-MM-DD (default: today in IST)")
    ap.add_argument("--force", action="store_true", help="post even if already posted today")
    ap.add_argument("--dry-run", action="store_true", help="print the post, send nothing")
    ap.add_argument("--no-card", action="store_true", help="text only, without the image card")
    args = ap.parse_args(argv)

    try:
        day = dt.date.fromisoformat(args.date) if args.date else daily_state.today_ist()
    except ValueError as exc:
        print(f"whatsapp_channel: {exc}", file=sys.stderr)
        return 2

    text, png = whatsapp_pack.post(day, "hi")
    with_card = not args.no_card and len(text) <= CAPTION_LIMIT
    link = os.environ.get("ASTRO_WA_CHANNEL_LINK", "").strip()

    if args.dry_run:
        print(f"Channel: {link or '(ASTRO_WA_CHANNEL_LINK not set)'}")
        print(f"Image: {'English card, ' + str(len(png)) + ' bytes, text as its caption' if with_card else 'none (text only)'}")
        print(f"----- hi ({len(text)} chars, WhatsApp *bold*) -----")
        print(text)
        return 0

    token = os.environ.get("ASTRO_WA_TOKEN", "").strip()
    url = os.environ.get("ASTRO_WA_URL", "").strip() or DEFAULT_URL
    if not token or not link:
        print("whatsapp_channel: ASTRO_WA_TOKEN and ASTRO_WA_CHANNEL_LINK must both be set "
              "(see deploy/daily_channels.md section 5)", file=sys.stderr)
        return 2
    try:
        wait_s = float(os.environ.get("ASTRO_WA_WAIT") or 60)
    except ValueError:
        wait_s = 60.0

    if not args.force and daily_state.sent(JOB, day):
        print(f"whatsapp_channel: already posted for {day}; nothing to do")
        return 0

    client = Client(url, token)
    try:
        wait_connected(client, wait_s)
        jid = channel_jid(client, link)
        try:
            mid = client.post(jid, text, png if with_card else None,
                              thumbnail(png) if with_card else None)
        except ConnectorError as exc:
            if exc.status == 409:
                raise Unlinked(str(exc)) from None
            if not with_card or exc.status != 502:
                raise
            # The image upload is the fragile part of the unofficial protocol.
            # A failed upload throws before anything is sent, so one text-only
            # try cannot double-post.
            print(f"whatsapp_channel: post with card failed ({exc}); retrying as text only",
                  file=sys.stderr)
            mid = client.post(jid, text, None, None)
        try:
            daily_state.mark(JOB, day, "hi", mid or True)
        except OSError as exc:
            print(f"whatsapp_channel: posted, but could not record it: {exc}", file=sys.stderr)
        print(f"whatsapp_channel: posted hi for {day} (message {mid})")
        return 0
    except Unlinked as exc:
        print(f"whatsapp_channel: NOT POSTED for {day}: {exc}", file=sys.stderr)
        alert_owner(str(exc), day)
        return 1
    except ConnectorError as exc:
        print(f"whatsapp_channel: FAILED for {day}: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:                            # e.g. the state dir is not writable
        print(f"whatsapp_channel: FAILED for {day}: "
              f"{client._redact(f'{type(exc).__name__}: {exc}')}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
