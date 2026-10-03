// node --test test/   (DIVASTRO-116) — HTTP validation and the token check,
// with the WhatsApp side faked. No network, no Baileys.

import { test, before, after } from 'node:test'
import assert from 'node:assert/strict'
import { createServer, MAX_TEXT } from '../src/server.js'
import { maskNumber, normalizePhone, parseInvite, tokenOk, isNewsletterJid } from '../src/util.js'

const TOKEN = 'test-token-0123456789abcdef'
const JID = '120363012345678901@newsletter'
const PNG = Buffer.from('89504e470d0a1a0a0000', 'hex')

const calls = []
const fake = {
  connected: true,
  status () { return { connected: this.connected, me: '+91••••••••10', linked_at: '2026-10-03T00:00:00Z' } },
  async qrPng () { return this.connected ? null : PNG },
  async pair (phone) { calls.push(['pair', phone]); return 'ABCD-EFGH' },
  async resolve (code) {
    calls.push(['resolve', code])
    return { jid: JID, name: 'Divine Astro', role: 'OWNER' }
  },
  async post (p) {
    calls.push(['post', p])
    if (!this.connected) throw Object.assign(new Error('not connected (logged_out)'), { status: 409 })
    if (p.text === 'boom') throw new Error('upload failed')
    return '3EB0ABC'
  }
}

let server, base
before(async () => {
  server = createServer({ token: TOKEN, wa: fake })
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve))
  base = `http://127.0.0.1:${server.address().port}`
})
after(() => server.close())

async function req (method, path, body, token = TOKEN) {
  const headers = { 'Content-Type': 'application/json' }
  if (token !== null) headers['X-WA-Token'] = token
  const r = await fetch(base + path, { method, headers, body: body === undefined ? undefined : (typeof body === 'string' ? body : JSON.stringify(body)) })
  const type = r.headers.get('content-type') || ''
  return [r.status, type.includes('json') ? await r.json() : Buffer.from(await r.arrayBuffer())]
}

test('every endpoint needs the token', async () => {
  for (const [m, p] of [['GET', '/status'], ['GET', '/qr.png'], ['POST', '/pair'],
    ['POST', '/channel/resolve'], ['POST', '/channel/post'], ['GET', '/nope']]) {
    const [s1] = await req(m, p, m === 'POST' ? {} : undefined, null)
    assert.equal(s1, 401, `${m} ${p} without token`)
    const [s2] = await req(m, p, m === 'POST' ? {} : undefined, 'wrong')
    assert.equal(s2, 401, `${m} ${p} wrong token`)
  }
  const [s3] = await req('GET', '/nope')
  assert.equal(s3, 404)
})

test('status', async () => {
  const [s, b] = await req('GET', '/status')
  assert.equal(s, 200)
  assert.deepEqual(b, { connected: true, me: '+91••••••••10', linked_at: '2026-10-03T00:00:00Z' })
})

test('qr.png: 404 when linked, PNG when awaiting a link', async () => {
  assert.equal((await req('GET', '/qr.png'))[0], 404)
  fake.connected = false
  const [s, b] = await req('GET', '/qr.png')
  fake.connected = true
  assert.equal(s, 200)
  assert.ok(b.equals(PNG))
})

test('pair validates the phone number', async () => {
  for (const phone of [undefined, '', '12345', '+0919876543210', 'abc', '9198765432101234']) {
    const [s] = await req('POST', '/pair', { phone })
    assert.equal(s, 400, `phone ${phone}`)
  }
  const [s, b] = await req('POST', '/pair', { phone: '+91 98765-43210' })
  assert.equal(s, 200)
  assert.equal(b.code, 'ABCD-EFGH')
  assert.deepEqual(calls.at(-1), ['pair', '919876543210'])
})

test('channel/resolve takes a link or a bare code', async () => {
  assert.equal((await req('POST', '/channel/resolve', { invite: 'https://example.com/x' }))[0], 400)
  assert.equal((await req('POST', '/channel/resolve', {}))[0], 400)
  const [s, b] = await req('POST', '/channel/resolve', { invite: 'https://whatsapp.com/channel/0029VaAbCdEfGh12?x=1' })
  assert.equal(s, 200)
  assert.equal(b.jid, JID)
  assert.equal(b.role, 'OWNER')
  assert.deepEqual(calls.at(-1), ['resolve', '0029VaAbCdEfGh12'])
})

test('channel/post validation', async () => {
  const cases = [
    [{ text: 'x' }, 'no jid'],
    [{ jid: '919876543210@s.whatsapp.net', text: 'x' }, 'a person, not a channel'],
    [{ jid: '1234@g.us', text: 'x' }, 'a group'],
    [{ jid: JID }, 'no text'],
    [{ jid: JID, text: '   ' }, 'blank text'],
    [{ jid: JID, text: 'x'.repeat(MAX_TEXT + 1) }, 'too long'],
    [{ jid: JID, text: 'x', image_base64: '%%%' }, 'bad base64'],
    [{ jid: JID, text: 'x', image_base64: PNG.toString('base64'), thumbnail_base64: '!!' }, 'bad thumbnail']
  ]
  for (const [body, label] of cases) {
    const before = calls.length
    const [s] = await req('POST', '/channel/post', body)
    assert.equal(s, 400, label)
    assert.equal(calls.length, before, `${label}: WhatsApp not called`)
  }
  assert.equal((await req('POST', '/channel/post', '{not json'))[0], 400)
})

test('channel/post sends text, or image with caption', async () => {
  let [s, b] = await req('POST', '/channel/post', { jid: JID, text: 'नमस्ते *bold*' })
  assert.equal(s, 200)
  assert.equal(b.id, '3EB0ABC')
  assert.equal(calls.at(-1)[1].image, null)
  ;[s, b] = await req('POST', '/channel/post', { jid: JID, text: 'cap', image_base64: PNG.toString('base64') })
  assert.equal(s, 200)
  assert.ok(calls.at(-1)[1].image.equals(PNG))
  assert.equal(calls.at(-1)[1].text, 'cap')
})

test('channel/post: 409 when not connected, 502 on a WhatsApp failure', async () => {
  fake.connected = false
  let [s, b] = await req('POST', '/channel/post', { jid: JID, text: 'x' })
  fake.connected = true
  assert.equal(s, 409)
  assert.match(b.error, /logged_out/)
  ;[s, b] = await req('POST', '/channel/post', { jid: JID, text: 'boom' })
  assert.equal(s, 502)
  assert.match(b.error, /upload failed/)
})

test('helpers', () => {
  assert.equal(maskNumber('919876543210:12@s.whatsapp.net'), '+91••••••••10')
  assert.equal(maskNumber(null), null)
  assert.equal(normalizePhone('919876543210'), '919876543210')
  assert.equal(normalizePhone('0919876543210'), null)
  assert.equal(parseInvite('whatsapp.com/channel/0029VaXYZ123'), '0029VaXYZ123')
  assert.equal(parseInvite('https://whatsapp.com/channel/0029VaXYZ123/'), '0029VaXYZ123')
  assert.equal(parseInvite('https://evil.com/whatsapp.com/channel/abc'), null)
  assert.ok(tokenOk('a'.repeat(20), 'a'.repeat(20)))
  assert.ok(!tokenOk('a'.repeat(20), 'b'.repeat(20)))
  assert.ok(!tokenOk(undefined, 'x'))
  assert.ok(!tokenOk('', ''))
  assert.ok(isNewsletterJid(JID))
  assert.ok(!isNewsletterJid('120363@newsletter.evil'))
})
