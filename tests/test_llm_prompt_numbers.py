"""The narration prompt must tell the model never to quote the engine's internal score
(a Hindi answer on 11 Oct 2026 opened with "स्कोर -0.138")."""
import os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("ASTRO_SECRET_KEY", "ci")
from app import llm  # noqa: E402

failures = []
system = llm._system("hi") + llm._system("en")
ok1 = "Never print the engine's internal numbers" in system
print(("PASS" if ok1 else "FAIL"), " system prompt forbids internal numbers"); failures += [] if ok1 else ["rule"]
src = Path(llm.__file__).read_text(encoding="utf-8")
ok2 = "never quote it" in src
print(("PASS" if ok2 else "FAIL"), " the score line in the prompt says never quote it"); failures += [] if ok2 else ["score line"]
raise SystemExit(1 if failures else 0)
