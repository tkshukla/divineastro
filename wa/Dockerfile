# Divine Astro — WhatsApp Channel connector (DIVASTRO-116).
#
# Node 20 + @whiskeysockets/baileys (unofficial WhatsApp Web linked-device
# protocol). Pure JS/WASM dependencies only: the optional native image
# libraries (sharp, jimp) are NOT installed (.npmrc legacy-peer-deps) — channel
# media is uploaded raw and the Python sender supplies the JPEG thumbnail.
#
#   docker build -t divineastro-wa wa/                # also runs the unit tests
#   docker build --target test wa/                    # tests only

FROM node:20-slim AS deps
WORKDIR /app
COPY package.json package-lock.json .npmrc ./
RUN npm ci --omit=dev --ignore-scripts \
    && node -e "import('@whiskeysockets/baileys').then(m => { if (!m.makeWASocket || !m.useMultiFileAuthState) process.exit(1); console.log('baileys ok') })"

# ---------------------------------------------------------------- tests
FROM deps AS test
COPY src ./src
COPY test ./test
RUN node --test test/ && touch /app/.tested

# ---------------------------------------------------------------- runtime
FROM node:20-slim
ENV NODE_ENV=production WA_PORT=3000
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY package.json ./
COPY src ./src
# Make the runtime stage depend on the test stage, so a failing test fails the build.
COPY --from=test /app/.tested /app/.tested
# The wadata volume is mounted here; a named volume inherits this ownership.
RUN mkdir -p /data/auth && chown -R node:node /data && chmod 700 /data/auth
USER node
EXPOSE 3000
HEALTHCHECK --interval=60s --timeout=5s --start-period=30s --retries=3 \
    CMD node -e "if((process.env.ASTRO_WA_TOKEN||'').trim().length<16)process.exit(0);fetch('http://127.0.0.1:'+(process.env.WA_PORT||3000)+'/status',{headers:{'X-WA-Token':process.env.ASTRO_WA_TOKEN||''}}).then(r=>process.exit(r.ok?0:1),()=>process.exit(1))"
CMD ["node", "src/index.js"]
