"""The uptime watchdog (deploy/healthcheck.sh, DIVASTRO-89).

The script runs unattended every minute on a SHARED server, so what it refuses to
do matters as much as what it does. These tests run the real script under bash with
fake `curl` and `docker` commands that record every call:

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.test_watchdog
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "deploy" / "healthcheck.sh"
failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def find_bash() -> str | None:
    for cand in (r"C:\Program Files\Git\bin\bash.exe", r"C:\Program Files\Git\usr\bin\bash.exe"):
        if os.path.exists(cand):
            return cand
    found = shutil.which("bash")
    if found and "system32" not in found.lower():          # not the WSL launcher
        return found
    return None


FAKE_CURL = r'''#!/usr/bin/env bash
# Fake curl: the alert endpoint is recorded, the health URL answers from a state file.
D="$FAKE_DIR"
args="$*"
case "$args" in
  *ntfy.example*) echo "$args" >> "$D/ntfy.log"; exit 0 ;;
esac
if [ "$(cat "$D/public" 2>/dev/null)" = "ok" ]; then echo '{"ok":true,"cities":1}'; exit 0; fi
exit 22
'''

FAKE_DOCKER = r'''#!/usr/bin/env bash
# Fake docker: records every call; answers from state files.
D="$FAKE_DIR"
echo "$*" >> "$D/docker.log"
case "$1" in
  exec)     [ "$(cat "$D/app" 2>/dev/null)" = "ok" ] && exit 0 || exit 1 ;;
  inspect)  cat "$D/running" 2>/dev/null || echo missing; exit 0 ;;
  start|restart)
     if [ "$(cat "$D/heal_works" 2>/dev/null)" = "yes" ]; then echo ok > "$D/app"; echo ok > "$D/public"; fi
     exit 0 ;;
esac
exit 0
'''


class Rig:
    def __init__(self, bash: str):
        self.bash = bash
        self.dir = Path(tempfile.mkdtemp(prefix="wd_"))
        self.fake = self.dir / "fakebin"
        self.fake.mkdir()
        self.state = self.dir / "state"
        for name, body in (("curl", FAKE_CURL), ("docker", FAKE_DOCKER)):
            f = self.fake / name
            f.write_text(body, encoding="utf-8", newline="\n")
            # The executable bit is ignored by Windows/MSYS bash but strictly
            # enforced by real Linux — without it, every "$CURL"/"$DOCKER" call
            # in the script under test silently fails with "Permission denied"
            # (invisible here since Rig.run() discards stderr), so every check
            # looks like a failure and no fake ever gets invoked. Found via the
            # GitHub Actions run of DIVASTRO-72's CI workflow — this test had
            # never actually run on real Linux before, which is where the real
            # watchdog script runs in production.
            f.chmod(0o755)
        self.set(public="ok", app="ok", running="true", heal_works="no")

    def set(self, **kw) -> None:
        for k, v in kw.items():
            (self.dir / k).write_text(v, encoding="utf-8")

    def run(self, topic: bool = True, extra_env: dict | None = None) -> None:
        env = dict(os.environ)
        env.update({
            "FAKE_DIR": self.dir.as_posix(),
            "PATH": str(self.fake) + os.pathsep + env.get("PATH", ""),        # native form: MSYS bash converts it correctly
            "WATCHDOG_STATE_DIR": self.state.as_posix(),
            "WATCHDOG_ENV_FILE": (self.dir / "none.env").as_posix(),
            "WATCHDOG_NTFY_BASE": "https://ntfy.example",
            "WATCHDOG_NTFY_TOPIC": "test-topic" if topic else "",
            "WATCHDOG_FAIL_THRESHOLD": "2",
            "WATCHDOG_CURL": (self.fake / "curl").as_posix(),
            "WATCHDOG_DOCKER": (self.fake / "docker").as_posix(),
        })
        env.update(extra_env or {})
        subprocess.run([self.bash, SCRIPT.as_posix()], env=env, timeout=60,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def read(self, name: str) -> str:
        p = self.dir / name
        return p.read_text(encoding="utf-8") if p.exists() else ""

    def state_read(self, name: str) -> str:
        p = self.state / name
        return p.read_text(encoding="utf-8") if p.exists() else ""

    def alerts(self) -> list[str]:
        return [l for l in self.read("ntfy.log").splitlines() if l.strip()]

    def docker_calls(self) -> list[str]:
        return [l for l in self.read("docker.log").splitlines() if l.strip()]

    def restarts(self) -> list[str]:
        return [c for c in self.docker_calls() if c.split()[0] in ("start", "restart")]


def main() -> int:
    bash = find_bash()
    if not bash:
        print("bash not found: skipping the watchdog tests")
        return 0

    print("\n0. The script is valid shell")
    r = subprocess.run([bash, "-n", SCRIPT.as_posix()], capture_output=True, text=True)
    check("bash -n accepts it", r.returncode == 0, r.stderr.strip()[:120])

    print("\n1. Healthy: silent and does nothing")
    rig = Rig(bash)
    for _ in range(3):
        rig.run()
    check("no alert", rig.alerts() == [])
    check("docker is never touched", rig.docker_calls() == [], str(rig.docker_calls()))
    check("failure counter stays at 0", rig.state_read("fails").strip() == "0")

    print("\n2. App container stopped (the 2026-09-25 outage): it comes back and you are told")
    rig = Rig(bash)
    rig.set(public="bad", app="bad", running="false", heal_works="yes")
    rig.run()
    check("ONE failed check is not enough to act (no flapping)", rig.restarts() == [] and rig.alerts() == [])
    rig.run()
    check("the 2nd failed check starts the app container", rig.restarts() == ["start divineastro-app-1"], str(rig.restarts()))
    check("and sends exactly one DOWN alert", len(rig.alerts()) == 1 and "DOWN" in rig.alerts()[0], str(rig.alerts()))
    check("the alert says what was done", "started divineastro-app-1" in rig.alerts()[0])
    rig.run()
    check("once it is healthy again, the next run says so", len(rig.alerts()) == 2 and "back" in rig.alerts()[1], str(rig.alerts()[-1:]))
    rig.run()
    rig.run()
    check("then it is quiet again", len(rig.alerts()) == 2)
    check("and the down marker is cleared", not (rig.state / "down_since").exists())

    print("\n3. App running but hung: restart, do not start")
    rig = Rig(bash)
    rig.set(public="bad", app="bad", running="true", heal_works="yes")
    rig.run(); rig.run()
    check("a running-but-unhealthy app is restarted", rig.restarts() == ["restart divineastro-app-1"], str(rig.restarts()))

    print("\n4. App cannot be healed: no alert storm")
    rig = Rig(bash)
    rig.set(public="bad", app="bad", running="false", heal_works="no")
    for _ in range(14):
        rig.run()
    kinds = [("STILL" if "STILL" in a else "DOWN") for a in rig.alerts()]
    check("one DOWN alert, then one 'STILL down' ten checks later, nothing in between", kinds == ["DOWN", "STILL"], str(kinds))
    check("it tried to start the app once, not every minute", len(rig.restarts()) == 1, str(rig.restarts()))

    print("\n5. The public path is broken but the app is fine (Caddy, DNS, certificate)")
    rig = Rig(bash)
    rig.set(public="bad", app="ok", running="true", heal_works="yes")
    rig.run(); rig.run(); rig.run()
    check("it alerts", len(rig.alerts()) == 1 and "public address" in rig.alerts()[0], str(rig.alerts()))
    check("and does NOT restart anything (a restart could not fix it and would loop forever)",
          rig.restarts() == [], str(rig.restarts()))

    print("\n6. Safety on a shared server")
    rig = Rig(bash)
    rig.set(public="bad", app="bad", running="false", heal_works="no")
    for _ in range(4):
        rig.run()
    calls = rig.docker_calls()
    bad = [c for c in calls if any(w in c for w in ("prune", "system", "compose", "kill", "rm ", "stop", "reboot", "daemon"))]
    others = [c for c in calls if c.split()[0] in ("start", "restart") and c.split()[-1] != "divineastro-app-1"]
    check("it never prunes, kills, removes, stops or uses compose", bad == [], str(bad))
    check("the only container it may start or restart is divineastro-app-1", others == [], str(others))

    print("\n7. Deploys: a maintenance marker pauses it")
    rig = Rig(bash)
    rig.set(public="bad", app="bad", running="false", heal_works="yes")
    rig.state.mkdir(parents=True, exist_ok=True)
    (rig.state / "maintenance").write_text("deploying")
    rig.run(); rig.run(); rig.run()
    check("while the marker is fresh it does nothing at all", rig.docker_calls() == [] and rig.alerts() == [])
    old = time.time() - 3 * 3600
    os.utime(rig.state / "maintenance", (old, old))
    rig.run()
    check("a forgotten marker (older than 30 min) is ignored and removed", not (rig.state / "maintenance").exists())

    print("\n8. Without an alert topic it still heals and logs")
    rig = Rig(bash)
    rig.set(public="bad", app="bad", running="false", heal_works="yes")
    rig.run(topic=False); rig.run(topic=False)
    check("no alert is sent", rig.alerts() == [])
    check("the app is still started", rig.restarts() == ["start divineastro-app-1"])
    check("and the log records the ALERT line", "ALERT: Divine Astro is DOWN" in rig.state_read("watchdog.log"))

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("watchdog: all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
