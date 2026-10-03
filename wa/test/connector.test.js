// node --test test/   (DIVASTRO-116) — connection lifecycle with Baileys faked:
// linking, reconnect, logged-out handling, and what goes to sendMessage.

import { test, beforeEach, afterEach } from 'node:test'
import assert from 'node:assert/strict'
import { EventEmitter } from 'node:events'
import fs from 'node:fs/promises'
import os from 'node:os'
import path from 'node:path'
import { Connector } from '../src/connector.js'

const DR = { loggedOut: 401, forbidden: 403, restartRequired: 515, timedOut: 408, connectionLost: 408 }
const closeWith = (statusCode) => ({ connection: 'close', lastDisconnect: { error: { output: { statusCode } } } })

function fakeBaileys ({ registered = false } = {}) {
  const sockets = []
  return {
    sockets,
    DisconnectReason: DR,
    Browsers: { ubuntu: (b) => ['Ubuntu', b, '22.04'] },
    async useMultiFileAuthState () {
      return { state: { creds: { registered, me: registered ? { id: '919876543210:3@s.whatsapp.net' } : undefined } }, saveCreds: async () => {} }
    },
    makeWASocket (config) {
      const ev = new EventEmitter()
      const sock = {
        config,
        ev,
        user: { id: '919876543210:3@s.whatsapp.net' },
        sent: [],
        async requestPairingCode (phone) { sock.pairedWith = phone; return 'ABCDEFGH' },
        async newsletterMetadata (type, key) {
          // Like the live service: the invite lookup omits the viewer's role, the jid lookup has it.
          const viewer = type === 'jid' ? { role: 'OWNER', mute: 'off' } : { mute: 'off' }
          return { id: '120363012345678901@newsletter', thread_metadata: { name: { text: 'Divine Astro' } }, viewer_metadata: viewer, type, key }
        },
        async sendMessage (jid, content) { sock.sent.push([jid, content]); return { key: { id: 'MSG1' } } }
      }
      sockets.push(sock)
      return sock
    }
  }
}

let dir, logs
const origLog = console.log
beforeEach(async () => {
  dir = await fs.mkdtemp(path.join(os.tmpdir(), 'wa-test-'))
  logs = []
  console.log = (...a) => logs.push(a.join(' '))
})
afterEach(async () => {
  console.log = origLog
  await fs.rm(dir, { recursive: true, force: true })
})

const emit = async (c, sock, u) => { sock.ev.emit('connection.update', u); await new Promise((r) => setTimeout(r, 20)) }

test('first start: QR goes to the log, then open -> connected', async () => {
  const b = fakeBaileys()
  const c = new Connector({ authDir: dir, baileys: b })
  await c.start()
  assert.deepEqual(c.status(), { connected: false, me: null, linked_at: null, reason: 'awaiting_link' })
  assert.equal(b.sockets[0].config.syncFullHistory, false)
  assert.equal(b.sockets[0].config.markOnlineOnConnect, false)
  await emit(c, b.sockets[0], { qr: '2@abc,def' })
  assert.ok(await c.qrPng(), 'QR PNG available while awaiting a link')
  assert.ok(logs.some((l) => l.includes('Linked devices')))
  await emit(c, b.sockets[0], { connection: 'open' })
  const s = c.status()
  assert.equal(s.connected, true)
  assert.equal(s.me, '+91••••••••10')
  assert.ok(s.linked_at)
  assert.equal(await c.qrPng(), null)
  assert.ok(!logs.join('\n').includes('919876543210'), 'full number never logged')
})

test('post: image with caption, or text only; resolve returns the role', async () => {
  const b = fakeBaileys({ registered: true })
  const c = new Connector({ authDir: dir, baileys: b })
  await c.start()
  await assert.rejects(c.post({ jid: 'x@newsletter', text: 'hi' }), (e) => e.status === 409)
  await emit(c, b.sockets[0], { connection: 'open' })
  const img = Buffer.from('png')
  assert.equal(await c.post({ jid: 'x@newsletter', text: 'cap', image: img, thumbnail: Buffer.from('jpg') }), 'MSG1')
  const [jid, content] = b.sockets[0].sent[0]
  assert.equal(jid, 'x@newsletter')
  assert.equal(content.caption, 'cap')
  assert.equal(content.mimetype, 'image/png')
  assert.ok(content.jpegThumbnail)
  await c.post({ jid: 'x@newsletter', text: 'only text' })
  assert.deepEqual(b.sockets[0].sent[1][1], { text: 'only text', linkPreview: null })
  const r = await c.resolve('0029Va')
  assert.deepEqual(r, { jid: '120363012345678901@newsletter', name: 'Divine Astro', role: 'OWNER', viewer_fields: ['role', 'mute'] })
})

test('transient close reconnects; restartRequired reconnects at once', async () => {
  const b = fakeBaileys({ registered: true })
  const c = new Connector({ authDir: dir, baileys: b })
  await c.start()
  await emit(c, b.sockets[0], { connection: 'open' })
  await emit(c, b.sockets[0], closeWith(515))
  await new Promise((r) => setTimeout(r, 50))
  assert.equal(b.sockets.length, 2, 'new socket after restartRequired')
  await emit(c, b.sockets[1], closeWith(428))
  assert.equal(c.status().reason, 'reconnecting')
  assert.ok(c.timer, 'a reconnect is scheduled with backoff')
  clearTimeout(c.timer)
})

test('logged out: stop retrying, wipe credentials, report logged_out', async () => {
  const b = fakeBaileys({ registered: true })
  const c = new Connector({ authDir: dir, baileys: b })
  await c.start()
  await fs.writeFile(path.join(dir, 'creds.json'), '{}')
  await emit(c, b.sockets[0], { connection: 'open' })
  await emit(c, b.sockets[0], closeWith(401))
  const s = c.status()
  assert.equal(s.connected, false)
  assert.equal(s.reason, 'logged_out')
  assert.deepEqual(await fs.readdir(dir), [], 'dead credentials removed')
  await new Promise((r) => setTimeout(r, 50))
  assert.equal(b.sockets.length, 1, 'no reconnect after logout')
  await assert.rejects(c.post({ jid: 'x@newsletter', text: 'hi' }), (e) => e.status === 409 && /logged_out/.test(e.message))
})

test('pairing code: waits for the socket, returns ABCD-EFGH, refuses when linked', async () => {
  const b = fakeBaileys()
  const c = new Connector({ authDir: dir, baileys: b })
  await c.start()
  const p = c.pair('919876543210')
  await emit(c, b.sockets[0], { qr: '2@abc' })
  assert.equal(await p, 'ABCD-EFGH')
  assert.equal(b.sockets[0].pairedWith, '919876543210')
  await emit(c, b.sockets[0], { connection: 'open' })
  await assert.rejects(c.pair('919876543210'), (e) => e.status === 409)
})

test('unscanned QR: gives up after 3 rounds with link_timeout', async () => {
  const b = fakeBaileys()
  const c = new Connector({ authDir: dir, baileys: b })
  await c.start()
  for (let i = 0; i < 3; i++) {
    await emit(c, b.sockets.at(-1), closeWith(408))
    await new Promise((r) => setTimeout(r, 1100))
  }
  assert.equal(c.status().reason, 'link_timeout')
  assert.equal(b.sockets.length, 3)
})
