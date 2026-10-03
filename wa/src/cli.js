// Owner helper, run inside the wa container so the token never has to be typed
// (DIVASTRO-116, deploy/daily_channels.md section 5):
//
//   docker compose exec wa node src/cli.js status
//   docker compose exec wa node src/cli.js pair 919876543210
//   docker compose exec wa node src/cli.js resolve https://whatsapp.com/channel/0029Va...
//   docker compose exec -T wa node src/cli.js qr > wa-qr.png
//
// It only talks to the local HTTP endpoints; the token comes from the
// container's environment and is never printed.

const [cmd, arg] = process.argv.slice(2)
const base = `http://127.0.0.1:${process.env.WA_PORT || 3000}`
const headers = { 'X-WA-Token': process.env.ASTRO_WA_TOKEN || '', 'Content-Type': 'application/json' }

async function call (method, path, body) {
  const r = await fetch(base + path, { method, headers, body: body ? JSON.stringify(body) : undefined })
  return [r.status, r]
}

async function main () {
  let status, r
  if (cmd === 'status') {
    [status, r] = await call('GET', '/status')
  } else if (cmd === 'pair' && arg) {
    [status, r] = await call('POST', '/pair', { phone: arg })
    if (status === 200) {
      const { code } = await r.json()
      console.log(`Pairing code: ${code}`)
      console.log('On the phone: WhatsApp > Settings > Linked devices > Link a device >')
      console.log('"Link with phone number instead", then type this code. It expires in about a minute.')
      return 0
    }
  } else if (cmd === 'resolve' && arg) {
    [status, r] = await call('POST', '/channel/resolve', { invite: arg })
  } else if (cmd === 'qr') {
    [status, r] = await call('GET', '/qr.png')
    if (status === 200) {
      process.stdout.write(Buffer.from(await r.arrayBuffer()))
      return 0
    }
  } else {
    console.error('usage: node src/cli.js status | pair <number with country code> | resolve <channel link> | qr > file.png')
    return 2
  }
  const text = await r.text()
  ;(status === 200 ? console.log : console.error)(text)
  return status === 200 ? 0 : 1
}

main().then((c) => process.exit(c), (e) => {
  console.error(`wa cli: ${e?.message || e}`)
  process.exit(1)
})
