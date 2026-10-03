// HTTP front of the WhatsApp Channel connector (DIVASTRO-116).
//
// Reachable only on the compose network as http://wa:3000 (no published
// port). Every endpoint needs the shared secret in the X-WA-Token header
// (env ASTRO_WA_TOKEN). The WhatsApp side is the `wa` object passed in
// (src/connector.js in production, a fake in the tests):
//
//   wa.status()                       -> {connected, me, linked_at, reason?}
//   wa.qrPng()                        -> Buffer | null
//   wa.pair(phone)                    -> "ABCD-EFGH"
//   wa.resolve(inviteCode)            -> {jid, name, role}
//   wa.post({jid, text, image, thumbnail}) -> message id
//
// A method may throw an Error with .status (409 not connected, 404 ...) and a
// short, secret-free .message; anything else becomes a 502.

import http from 'node:http'
import {
  decodeBase64, isNewsletterJid, log, normalizePhone, parseInvite, tokenOk
} from './util.js'

export const MAX_BODY = 8 * 1024 * 1024 // JSON body: a ~1 MB PNG as base64 fits easily
export const MAX_TEXT = 4096
export const MAX_IMAGE = 5 * 1024 * 1024

function send (res, status, body, type = 'application/json') {
  const data = type === 'application/json' ? JSON.stringify(body) : body
  res.writeHead(status, { 'Content-Type': type, 'Cache-Control': 'no-store' })
  res.end(data)
}

function readJson (req) {
  return new Promise((resolve, reject) => {
    let size = 0
    const chunks = []
    req.on('data', (c) => {
      size += c.length
      if (size > MAX_BODY) {
        reject(Object.assign(new Error('body too large'), { status: 413 }))
        req.destroy()
        return
      }
      chunks.push(c)
    })
    req.on('end', () => {
      if (!chunks.length) return resolve({})
      try {
        const v = JSON.parse(Buffer.concat(chunks).toString('utf8'))
        resolve(v && typeof v === 'object' && !Array.isArray(v) ? v : {})
      } catch {
        reject(Object.assign(new Error('body is not JSON'), { status: 400 }))
      }
    })
    req.on('error', reject)
  })
}

const bad = (message) => Object.assign(new Error(message), { status: 400 })

export function createServer ({ token, wa }) {
  const routes = {
    'GET /status': async () => [200, wa.status()],

    'GET /qr.png': async (req, res) => {
      const png = await wa.qrPng()
      if (!png) return [404, { error: 'no QR right now (already linked, or not started)' }]
      send(res, 200, png, 'image/png')
      return null
    },

    'POST /pair': async (req) => {
      const body = await readJson(req)
      const phone = normalizePhone(body.phone)
      if (!phone) throw bad('phone: full number with country code, digits only, e.g. 919876543210')
      return [200, { code: await wa.pair(phone) }]
    },

    'POST /channel/resolve': async (req) => {
      const body = await readJson(req)
      const code = parseInvite(body.invite)
      if (!code) throw bad('invite: a channel link like https://whatsapp.com/channel/0029Va...')
      return [200, await wa.resolve(code)]
    },

    'POST /channel/post': async (req) => {
      const body = await readJson(req)
      if (!isNewsletterJid(body.jid)) throw bad('jid: a channel JID ending in @newsletter')
      if (typeof body.text !== 'string' || !body.text.trim()) throw bad('text: required')
      if (body.text.length > MAX_TEXT) throw bad(`text: over ${MAX_TEXT} characters`)
      let image = null
      let thumbnail = null
      if (body.image_base64 != null) {
        image = decodeBase64(body.image_base64)
        if (!image) throw bad('image_base64: not valid base64')
        if (image.length > MAX_IMAGE) throw bad('image_base64: image over 5 MB')
        if (body.thumbnail_base64 != null) {
          thumbnail = decodeBase64(body.thumbnail_base64)
          if (!thumbnail || thumbnail.length > 64 * 1024) throw bad('thumbnail_base64: invalid or over 64 KB')
        }
      }
      const id = await wa.post({ jid: body.jid, text: body.text, image, thumbnail })
      log(`posted to channel: text ${body.text.length} chars${image ? `, image ${image.length} bytes` : ''}, id ${id}`)
      return [200, { id }]
    }
  }

  return http.createServer(async (req, res) => {
    const path = (req.url || '/').split('?')[0]
    const handler = routes[`${req.method} ${path}`]
    try {
      if (!tokenOk(req.headers['x-wa-token'], token)) {
        // Same answer for "wrong token" and "no such route": say nothing to strangers.
        return send(res, 401, { error: 'unauthorized' })
      }
      if (!handler) return send(res, 404, { error: 'not found' })
      const out = await handler(req, res)
      if (out) send(res, out[0], out[1])
    } catch (err) {
      const status = Number.isInteger(err?.status) ? err.status : 502
      const message = status === 502 ? `whatsapp: ${err?.message || 'failed'}` : err.message
      if (status >= 500) log(`${req.method} ${path} failed: ${String(message).slice(0, 200)}`)
      if (!res.headersSent) send(res, status, { error: message })
      else res.end()
    }
  })
}
