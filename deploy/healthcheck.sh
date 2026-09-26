#!/usr/bin/env bash
# Divine Astro watchdog (DIVASTRO-89). Run every minute from the `ubuntu` user's
# crontab on the Oracle host:
#
#   * * * * * /srv/divineastro/deploy/healthcheck.sh >/dev/null 2>&1
#
# What it does, and deliberately does NOT do:
#   - checks the PUBLIC health URL (what a customer sees), then the app container
#     from the inside, so it can tell "app is down" from "the path to it is broken";
#   - app down for WATCHDOG_FAIL_THRESHOLD checks in a row -> starts (or restarts)
#     ONLY the divineastro-app-1 container, then alerts;
#   - public path failing while the app is fine (Caddy / DNS / certificate) -> alerts
#     only. It never restarts Caddy by itself: a check that fails for a reason a
#     restart cannot fix would otherwise restart it every minute, forever;
#   - never touches any other project on this shared box, never prunes, never
#     reboots, never restarts the docker daemon;
#   - alerts (ntfy push) on: down, still down, recovered. It stays quiet otherwise.
# It cannot report that the whole machine is down; that needs an outside monitor.
#
# Settings live in ~/.divineastro-watchdog.env (never in the repo):
#   WATCHDOG_NTFY_TOPIC=<long random private topic>   # phone push via the ntfy app
# Everything below can be overridden by environment variables (the tests do).
#
# During a deploy: `touch "$STATE_DIR/maintenance"` pauses it (auto-expires after 30 min).

set -u

[ -f "${WATCHDOG_ENV_FILE:-$HOME/.divineastro-watchdog.env}" ] && . "${WATCHDOG_ENV_FILE:-$HOME/.divineastro-watchdog.env}"

STATE_DIR="${WATCHDOG_STATE_DIR:-/var/tmp/divineastro-watchdog}"
PUBLIC_URL="${WATCHDOG_URL:-https://divineastro.org/api/health}"
APP="${WATCHDOG_APP_CONTAINER:-divineastro-app-1}"
THRESHOLD="${WATCHDOG_FAIL_THRESHOLD:-2}"
NTFY_BASE="${WATCHDOG_NTFY_BASE:-https://ntfy.sh}"
TOPIC="${WATCHDOG_NTFY_TOPIC:-}"
MAINT_MAX_AGE_MIN="${WATCHDOG_MAINT_MAX_AGE_MIN:-30}"
CURL="${WATCHDOG_CURL:-curl}"        # overridable so the tests can substitute fakes
DOCKER="${WATCHDOG_DOCKER:-docker}"

mkdir -p "$STATE_DIR" 2>/dev/null || exit 0
LOG="$STATE_DIR/watchdog.log"
FAILS_FILE="$STATE_DIR/fails"
SINCE_FILE="$STATE_DIR/down_since"

log() { printf '%s %s\n' "$(date -u +%FT%TZ)" "$*" >> "$LOG"; }

alert() {   # alert <title> <message> [priority]
  log "ALERT: $1 - $2"
  [ -n "$TOPIC" ] || return 0
  "$CURL" -fsS -m 10 -H "Title: $1" -H "Priority: ${3:-default}" -H "Tags: ${4:-warning}" \
       -d "$2" "$NTFY_BASE/$TOPIC" >/dev/null 2>&1 || log "could not send the alert"
}

# One run at a time (a slow check must not stack up behind itself).
exec 9>"$STATE_DIR/lock"
if command -v flock >/dev/null 2>&1; then flock -n 9 || exit 0; fi

# Deploy pause: a marker file, ignored once it is older than MAINT_MAX_AGE_MIN.
if [ -f "$STATE_DIR/maintenance" ]; then
  if [ -z "$(find "$STATE_DIR/maintenance" -mmin +"$MAINT_MAX_AGE_MIN" 2>/dev/null)" ]; then exit 0; fi
  rm -f "$STATE_DIR/maintenance"; log "stale maintenance marker removed"
fi

public_ok() { "$CURL" -fsS -m 10 "$PUBLIC_URL" 2>/dev/null | grep -q '"ok" *: *true'; }

app_ok() {
  "$DOCKER" exec "$APP" python -c \
    "import urllib.request,sys; sys.exit(0 if b'true' in urllib.request.urlopen('http://127.0.0.1:8000/api/health',timeout=5).read() else 1)" \
    >/dev/null 2>&1
}

fails=0; [ -f "$FAILS_FILE" ] && fails=$(cat "$FAILS_FILE" 2>/dev/null || echo 0)
case "$fails" in ''|*[!0-9]*) fails=0 ;; esac

if public_ok; then
  if [ -f "$SINCE_FILE" ]; then
    since=$(cat "$SINCE_FILE"); mins=$(( ( $(date +%s) - since ) / 60 ))
    alert "Divine Astro is back" "The site is answering again after about ${mins} minute(s)." default white_check_mark
    rm -f "$SINCE_FILE"
  fi
  echo 0 > "$FAILS_FILE"
  exit 0
fi

# Not healthy from outside. Work out why.
fails=$(( fails + 1 )); echo "$fails" > "$FAILS_FILE"
[ -f "$SINCE_FILE" ] || date +%s > "$SINCE_FILE"

if app_ok; then
  reason="the app is healthy but the public address is not answering (Caddy, DNS or certificate)"
  heal="none: this needs a person"
else
  reason="the app container is not healthy"
  heal="none yet"
fi
log "check failed ($fails in a row): $reason"

if [ "$fails" -eq "$THRESHOLD" ]; then
  if ! app_ok; then
    state=$("$DOCKER" inspect -f '{{.State.Running}}' "$APP" 2>/dev/null || echo missing)
    if [ "$state" = "true" ]; then
      "$DOCKER" restart "$APP" >/dev/null 2>&1 && heal="restarted $APP" || heal="restart of $APP failed"
    else
      "$DOCKER" start "$APP" >/dev/null 2>&1 && heal="started $APP" || heal="start of $APP failed"
    fi
    log "self-heal: $heal"
  fi
  alert "Divine Astro is DOWN" "The site failed $fails checks in a row: $reason. Action taken: $heal." high rotating_light
elif [ "$fails" -eq $(( THRESHOLD + 10 )) ] || { [ "$fails" -gt $(( THRESHOLD + 10 )) ] && [ $(( (fails - THRESHOLD) % 60 )) -eq 0 ]; }; then
  alert "Divine Astro is STILL down" "Still failing after $fails checks: $reason." urgent sos
fi
exit 0
