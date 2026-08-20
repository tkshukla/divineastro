# Divine Astro — production image
#
# Two things here are not boilerplate and matter:
#   * Devanagari fonts. Without them, Hindi PDFs print as empty boxes. Verified
#     at runtime by GET /api/pdf/fonts.
#   * A build toolchain, because pyswisseph and timezonefinder compile C
#     extensions. They are installed in a builder stage and left behind, so the
#     runtime image stays small and carries no compiler.

# ---------------------------------------------------------------- builder
FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build
COPY requirements.txt .
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir --upgrade pip \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# ---------------------------------------------------------------- runtime
FROM python:3.12-slim

# fonts-noto-core   -> Latin/symbol faces the PDF template expects, and Noto
#                      Sans Devanagari, so Hindi answers render as script.
# fonts-deva        -> Debian's Devanagari meta-package, as a belt-and-braces
#                      fallback; `fonts-noto-devanagari` does NOT exist on
#                      Debian 12 (verified with apt-cache, not assumed).
# tzdata            -> historical timezone rules for birth-time localisation
# fontconfig is needed for fc-cache/fc-list and is NOT pulled in under
# --no-install-recommends, so it is named explicitly.
RUN apt-get update && apt-get install -y --no-install-recommends \
        fontconfig fonts-noto-core fonts-deva tzdata curl \
    && rm -rf /var/lib/apt/lists/* \
    && fc-cache -f \
    # Fail the build here rather than ship an image that silently prints
    # Hindi as empty boxes.
    && fc-list :lang=hi family | head -5 \
    && test -n "$(fc-list :lang=hi family)"

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /srv
COPY alembic.ini ./
COPY migrations ./migrations
COPY app ./app
COPY tools ./tools
COPY data/cities5000.txt data/admin1CodesASCII.txt data/countryInfo.txt ./data/

# Build the city index at image-build time so the first request is not slow.
RUN python -c "import sys; sys.path.insert(0,'.'); from app import geo; print('indexed', len(geo.get_index()), 'places')"

# Run as a non-root user: nothing here needs root, and a container escape
# should not land on one.
RUN useradd --system --uid 10001 --home /srv astro \
    && mkdir -p /srv/data && chown -R astro:astro /srv
USER astro

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD curl -fsS http://127.0.0.1:8000/api/health || exit 1

# One worker: chart sessions live in process memory, so a second worker would
# serve requests that cannot see them. Scale by adding a shared session store
# first, not by raising this number.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--proxy-headers", "--forwarded-allow-ips", "*"]
