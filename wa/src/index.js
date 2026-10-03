// Entry point of the `wa` compose service (DIVASTRO-116). See src/connector.js
// and deploy/daily_channels.md section 5.
//
// Env:
//   ASTRO_WA_TOKEN  shared secret for the X-WA-Token header (required; at
//                   least 16 characters). Without it the service idles: it
//                   does not touch WhatsApp at all.
//   WA_AUTH_DIR     linked-device credentials (default /data/auth, the
//                   `wadata` volume)
//   WA_PORT         default 3000
//   WA_LOG_LEVEL    Baileys' own log level (default "error")

import pino from 'pino'
import * as baileys from '@whiskeysockets/baileys'
import { Connector } from './connector.js'
import { createServer } from './server.js'
import { log } from './util.js'

const token = (process.env.ASTRO_WA_TOKEN || '').trim()
const port = Number(process.env.WA_PORT || 3000)
const authDir = process.env.WA_AUTH_DIR || '/data/auth'

if (token.length < 16) {
  log('ASTRO_WA_TOKEN is not set (or shorter than 16 characters): idle, not connecting to WhatsApp. ' +
      'Set it in .env (openssl rand -hex 24) and run `docker compose up -d wa`.')
  setInterval(() => {}, 1 << 30)
} else {
  const wa = new Connector({
    authDir,
    baileys,
    logger: pino({ level: process.env.WA_LOG_LEVEL || 'error' })
  })
  createServer({ token, wa }).listen(port, '0.0.0.0', () => log(`listening on :${port}`))
  wa.start().catch((e) => log('start failed:', e?.message))
  for (const sig of ['SIGTERM', 'SIGINT']) {
    process.on(sig, () => {
      log(`${sig}: bye`)
      try { wa.sock?.end(undefined) } catch {}
      process.exit(0)
    })
  }
}
