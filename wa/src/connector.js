// The WhatsApp side of the connector (DIVASTRO-116): one Baileys linked-device
// session on the owner's dedicated number. It only ever
//   * links (QR in the log / GET /qr.png, or a pairing code),
//   * looks up the owner's channel from its invite link, and
//   * posts one message to that channel when asked.
// It registers no message handlers: it does not read chats, send read
// receipts, sync history or message anyone.
//
// Connection lifecycle:
//   transient close  -> reconnect with backoff (2 s, 4 s, ... max 5 min)
//   restartRequired  -> reconnect at once (normal right after linking)
//   QR not scanned   -> retry 3 rounds of QR codes, then idle ("link_timeout")
//                       until `docker compose restart wa` or POST /pair
//   logged out       -> stop for good, wipe the dead credentials so the next
//                       start shows a fresh QR, report reason "logged_out"
//   forbidden (403)  -> stop, reason "forbidden" (number restricted/banned)

import fs from 'node:fs/promises'
import path from 'node:path'
import QRCode from 'qrcode'
import qrTerminal from 'qrcode-terminal'
import { formatPairingCode, log, maskNumber } from './util.js'

const MAX_BACKOFF_MS = 5 * 60 * 1000
const QR_ROUNDS = 3
const SEND_TIMEOUT_MS = 120 * 1000

const httpError = (status, message) => Object.assign(new Error(message), { status })

function withTimeout (promise, ms, what) {
  let t
  return Promise.race([
    promise.finally(() => clearTimeout(t)),
    new Promise((_, reject) => { t = setTimeout(() => reject(new Error(`${what} timed out`)), ms) })
  ])
}

export class Connector {
  /**
   * @param {object} opts
   * @param {string} opts.authDir  where Baileys keeps the linked-device credentials
   * @param {object} opts.baileys  the @whiskeysockets/baileys module (injected for tests)
   * @param {object} [opts.logger] pino logger handed to Baileys
   */
  constructor ({ authDir, baileys, logger }) {
    this.authDir = authDir
    this.b = baileys
    this.logger = logger
    this.sock = null
    this.connected = false
    this.me = null
    this.linkedAt = null
    this.reason = 'starting'
    this.qr = null
    this.registered = false
    this.attempt = 0
    this.qrRounds = 0
    this.stopped = false
    this.pairing = false
    this.timer = null
    this.qrWaiters = []
  }

  status () {
    const s = { connected: this.connected, me: maskNumber(this.me), linked_at: this.linkedAt }
    if (!this.connected) s.reason = this.reason
    return s
  }

  async start () {
    this.stopped = false
    clearTimeout(this.timer)
    if (this.sock) return
    await this._connect()
  }

  async _connect () {
    const b = this.b
    await fs.mkdir(this.authDir, { recursive: true, mode: 0o700 })
    const { state, saveCreds } = await b.useMultiFileAuthState(this.authDir)
    this.registered = !!state.creds?.registered
    if (this.registered && !this.me) this.me = state.creds.me?.id || null
    this.linkedAt = await this._readLinkedAt()
    if (!this.registered) this.reason = 'awaiting_link'
    else if (this.reason === 'starting') this.reason = 'connecting'
    const makeWASocket = b.makeWASocket || b.default
    const sock = makeWASocket({
      auth: state,
      logger: this.logger,
      browser: b.Browsers.ubuntu('Chrome'),
      printQRInTerminal: false,
      markOnlineOnConnect: false,
      syncFullHistory: false,
      shouldSyncHistoryMessage: () => false,
      generateHighQualityLinkPreview: false,
      getMessage: async () => undefined
    })
    this.sock = sock
    sock.ev.on('creds.update', saveCreds)
    sock.ev.on('connection.update', (u) => { this._onUpdate(u, sock).catch((e) => log('update handler:', e?.message)) })
  }

  async _onUpdate ({ connection, lastDisconnect, qr }, sock) {
    if (sock !== this.sock) return // an old socket's late event
    if (qr) {
      this.qr = qr
      this.reason = 'awaiting_link'
      for (const w of this.qrWaiters.splice(0)) w()
      if (!this.pairing) {
        log('Not linked yet. On the phone with the channel: WhatsApp > Settings > Linked devices > Link a device, and scan this QR (it changes every ~20 s; zoom the terminal out if it is cut off):')
        qrTerminal.generate(qr, { small: true }, (ascii) => console.log(ascii))
      }
    }
    if (connection === 'open') {
      this.connected = true
      this.qr = null
      this.pairing = false
      this.attempt = 0
      this.qrRounds = 0
      this.registered = true
      this.reason = null
      this.me = sock.user?.id || null
      if (!this.linkedAt) {
        this.linkedAt = new Date().toISOString()
        await fs.writeFile(path.join(this.authDir, 'linked_at'), this.linkedAt).catch(() => {})
      }
      log(`connected as ${maskNumber(this.me)}`)
    } else if (connection === 'close') {
      this.connected = false
      this.sock = null
      this.qr = null
      const code = lastDisconnect?.error?.output?.statusCode
      const DR = this.b.DisconnectReason
      if (code === DR.loggedOut) {
        this.pairing = false
        await this._stop('logged_out')
        await this._wipeCreds()
        log('LOGGED OUT: the phone removed this linked device (or WhatsApp did). Credentials wiped. Re-link: `docker compose restart wa`, then scan the new QR (deploy/daily_channels.md).')
      } else if (code === DR.forbidden) {
        await this._stop('forbidden')
        log('FORBIDDEN (403): WhatsApp refused this number. It may be restricted or banned. Not retrying.')
      } else if (code === DR.restartRequired) {
        log('restart required (normal right after linking); reconnecting')
        this._schedule(0)
      } else if (!this.registered && code === DR.timedOut) {
        this.qrRounds += 1
        this.pairing = false
        if (this.qrRounds >= QR_ROUNDS) {
          await this._stop('link_timeout')
          log('Nobody linked a phone in time; idle. `docker compose restart wa` shows new QR codes, or use the pairing code (node src/cli.js pair <number>).')
        } else {
          this._schedule(1000)
        }
      } else {
        this.reason = this.registered ? 'reconnecting' : 'awaiting_link'
        const ms = Math.min(MAX_BACKOFF_MS, 2000 * 2 ** this.attempt)
        this.attempt += 1
        log(`disconnected (code ${code ?? 'none'}); retrying in ${Math.round(ms / 1000)} s`)
        this._schedule(ms)
      }
    }
  }

  _schedule (ms) {
    clearTimeout(this.timer)
    if (this.stopped) return
    this.timer = setTimeout(() => {
      this._connect().catch((e) => {
        log('connect failed:', e?.message)
        this._schedule(Math.min(MAX_BACKOFF_MS, 2000 * 2 ** this.attempt++))
      })
    }, ms)
  }

  async _stop (reason) {
    this.stopped = true
    this.reason = reason
    clearTimeout(this.timer)
  }

  async _readLinkedAt () {
    try {
      return (await fs.readFile(path.join(this.authDir, 'linked_at'), 'utf8')).trim() || null
    } catch {
      return null
    }
  }

  async _wipeCreds () {
    const entries = await fs.readdir(this.authDir).catch(() => [])
    await Promise.all(entries.map((e) => fs.rm(path.join(this.authDir, e), { recursive: true, force: true })))
    this.registered = false
    this.linkedAt = null
    this.me = null
  }

  async qrPng () {
    return this.qr ? QRCode.toBuffer(this.qr, { type: 'png', margin: 2, scale: 8 }) : null
  }

  async pair (phone) {
    if (this.connected || this.registered) {
      throw httpError(409, 'already linked; to link again, log this device out on the phone first')
    }
    this.qrRounds = 0
    if (!this.sock) await this.start()
    if (!this.qr) {
      await withTimeout(new Promise((resolve) => this.qrWaiters.push(resolve)), 30000, 'waiting for WhatsApp')
    }
    this.pairing = true
    const code = await this.sock.requestPairingCode(phone)
    log('pairing code issued; enter it on the phone within about a minute')
    return formatPairingCode(code)
  }

  _requireConnected () {
    if (!this.connected || !this.sock) {
      throw httpError(409, `not connected (${this.reason || 'unknown'})`)
    }
  }

  async resolve (code) {
    this._requireConnected()
    const meta = await withTimeout(this.sock.newsletterMetadata('invite', code), 30000, 'channel lookup')
    if (!meta?.id) throw httpError(404, 'no channel for that link')
    let viewer = meta.viewer_metadata ?? meta.viewerMetadata ?? null
    // The invite lookup can come back without the viewer's role even for the
    // channel's owner; the same query keyed by the channel id usually has it.
    if (!viewer?.role) {
      try {
        const byJid = await withTimeout(this.sock.newsletterMetadata('jid', meta.id), 30000, 'channel lookup')
        viewer = byJid?.viewer_metadata ?? byJid?.viewerMetadata ?? viewer
      } catch { /* keep what the invite lookup gave */ }
    }
    return {
      jid: meta.id,
      name: meta.thread_metadata?.name?.text ?? meta.name ?? null,
      role: viewer?.role ?? null,
      // Field names only (no values), to diagnose a missing role without logging anything personal.
      viewer_fields: viewer ? Object.keys(viewer) : []
    }
  }

  async post ({ jid, text, image, thumbnail }) {
    this._requireConnected()
    const content = image
      ? { image, caption: text, mimetype: 'image/png', ...(thumbnail ? { jpegThumbnail: thumbnail } : {}) }
      : { text, linkPreview: null }
    const msg = await withTimeout(this.sock.sendMessage(jid, content), SEND_TIMEOUT_MS, 'sending')
    return msg?.key?.id ?? null
  }
}
