// Small pure helpers for the WhatsApp Channel connector (DIVASTRO-116).
// No Baileys import here, so the tests can load this file on any machine.

import { createHash, timingSafeEqual } from 'node:crypto'

/** Constant-time compare of the X-WA-Token header against the configured token. */
export function tokenOk (given, expected) {
  if (typeof given !== 'string' || typeof expected !== 'string' || !expected) return false
  const a = createHash('sha256').update(given).digest()
  const b = createHash('sha256').update(expected).digest()
  return timingSafeEqual(a, b)
}

/** "919876543210:12@s.whatsapp.net" -> "+91••••••••10". Never the whole number. */
export function maskNumber (jid) {
  if (!jid || typeof jid !== 'string') return null
  const digits = jid.split('@')[0].split(':')[0].replace(/\D/g, '')
  if (digits.length < 5) return '•••'
  return '+' + digits.slice(0, 2) + '•'.repeat(digits.length - 4) + digits.slice(-2)
}

/** Phone number for pairing: digits only, with country code, no leading 0 or +. */
export function normalizePhone (raw) {
  if (typeof raw !== 'string' && typeof raw !== 'number') return null
  const digits = String(raw).replace(/[\s+\-().]/g, '')
  return /^[1-9]\d{7,14}$/.test(digits) ? digits : null
}

/** The invite code from "https://whatsapp.com/channel/<code>" (or a bare code). */
export function parseInvite (raw) {
  if (typeof raw !== 'string') return null
  const s = raw.trim()
  const m = s.match(/^(?:https?:\/\/)?(?:www\.)?whatsapp\.com\/channel\/([A-Za-z0-9_-]{6,64})\/?(?:[?#].*)?$/)
  if (m) return m[1]
  return /^[A-Za-z0-9_-]{6,64}$/.test(s) ? s : null
}

/** A channel ("newsletter") JID such as "120363012345678901@newsletter". */
export function isNewsletterJid (jid) {
  return typeof jid === 'string' && /^\d{5,40}@newsletter$/.test(jid)
}

/** "ABCDEFGH" -> "ABCD-EFGH", the way WhatsApp shows it. */
export function formatPairingCode (code) {
  const c = String(code || '').toUpperCase()
  return c.length === 8 ? `${c.slice(0, 4)}-${c.slice(4)}` : c
}

/** Base64 -> Buffer, or null when it is not valid base64. */
export function decodeBase64 (s) {
  if (typeof s !== 'string' || !s.length) return null
  const clean = s.replace(/\s+/g, '')
  if (!/^[A-Za-z0-9+/]+={0,2}$/.test(clean)) return null
  const buf = Buffer.from(clean, 'base64')
  return buf.length ? buf : null
}

/** One log line, timestamped. Callers pass lengths and states, never bodies or secrets. */
export function log (...args) {
  console.log(new Date().toISOString(), '[wa]', ...args)
}
