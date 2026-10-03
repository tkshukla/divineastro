"""Branded 1080x1080 social card — CLI wrapper.

The template itself moved to app/social_card.py (DIVASTRO-113) so the app
container, which only ships app/, can render the daily WhatsApp card too.
This wrapper keeps the command the daily marketing task runs unchanged:

    python deploy/marketing/make_card.py "<eyebrow>" "<headline>" "<subline>" out.png

It loads app/social_card.py by file path rather than `import app...`, so the
marketing venv does not need the app's dependencies and app/__init__.py (which
reads .env) never runs.
"""
import importlib.util
import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[2] / "app" / "social_card.py"
_spec = importlib.util.spec_from_file_location("divineastro_social_card", _SRC)
_card = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_card)

make_card = _card.make_card

if __name__ == "__main__":
    make_card(*sys.argv[1:5])
    print("wrote", sys.argv[4])
